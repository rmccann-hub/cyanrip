# Rig session 2026-11-24b: round 42's C2 probe, run twice to the end

**What this is.** Round 42's G2 probe: Platterpus's `docs/rig-scripts/drivetest.sh`, its `probe`
entry, on the BDR-209D and the reference disc. The owner ran it to the end twice on
2026-11-24, from 16:04:26Z and from 23:38:36Z. A start at 23:32:04Z logged its first step and
nothing more, and nothing says how it ended. Each run did three things:

- **One `cyanrip -I -N` read alone,** with a 300 s limit.
- **Two such reads 2.4 s apart,** then the pair again under `strace`.
- **The C2 probe:** READ CD with byte 9 = `12h` (C2 error pointers, 2,646 bytes a frame), three
  times at each of 22 windows of 26 frames, each after a cache flush. The windows cover a
  control at LBA 5000 and the seconds G2 names: 162 of track 1, 240, 244, 245, 251 and 252 of
  track 3, and 144 of track 5. One more read at LBA 83416 used byte 9 = `14h`, which adds the
  block error byte.

The probe kept the C2 bytes of each read and dropped its audio (`probe/*.noaudio`, 294 bytes a
frame, or 296 for the `14h` read; `probe/audio-dropped.txt`).

The owner uploaded it as `platterpusdrivetest42probe.tar.gz` (sha256
`a9b9d57619dd8f982ab6fb3d533cd0effe3ae73ebabf4e503f5ca3d34147ffe3`, 985,786 bytes).

- **Integrity.** All 150 members it lists match the sender's `MANIFEST.txt`.
- **Personal details.** `tools/redact.py` replaced 2,343 home paths in 71 files: the app logs,
  `drivetest.log`, the probe's text files and `records/RECORDS.txt`. It found no hostname, and
  the owner's name was not checked, for want of a local list.
- **Hashes.** `SHA256SUMS` gives each file's filed hash, and the delivered hash of each file
  that changed. `MANIFEST.txt` is filed as delivered.

**What comes from which run.** `drivetest.log` keeps every run of the day, from the stop at
06:17:00Z (`docs/rig-2026-11-24-c2probe-stopped/`) on. The `probe/` folder holds only the last
run's files: each run overwrites the one before. So the 16:04Z run is filed as its summary lines
in `drivetest.log` (`:557` to `:586`), and the 23:38Z run as those lines (`:681` to `:710`) and
its files.

**Read the build, not the date.**

- **The C2 reads** are `sg_raw`, not cyanrip.
- **The solo and pair reads** ran `~/.local/bin/cyanrip`. Pair A's tags name it
  `cyanrip 0.9.4-rc3+platterpus.35` (`probe/pairA.txt`).
- **The script.** `drivetest.log` names no revision of it. Bash names line 696 for the killed
  read in the 16:04Z run and line 720 in the 23:38Z run, so the two runs ran different revisions.
- **The app.** `applog/` is Platterpus's own log, 0.7.128 and 0.7.129, from 2026-11-18 to
  2026-11-24 16:04:16Z. It keeps local time, five hours behind UTC.

## What it establishes

1. **C2 at G2's seconds.** Both runs agree on where the drive sets C2 bits and where it sets
   none. Inside the flagged windows, which reads flag and how many bits vary.

   | Window (the script's label) | LBAs | 16:04Z run | 23:38Z run |
   |---|---|---|---|
   | control | 5000 to 5025 | none in 3 reads | none in 3 reads |
   | track 1 second 162, three windows | 12150 to 12227 | none in 9 reads | none in 9 reads |
   | track 3 second 240, three windows | 46067 to 46144 | none in 9 reads | none in 9 reads |
   | track 3 second 244, three windows | 46367 to 46444 | none in 9 reads | none in 9 reads |
   | track 3 second 245, three windows | 46442 to 46519 | none in 9 reads | none in 9 reads |
   | track 3 second 251 | 46892 to 46917 | read 1: 46902 (11 bits), 46913 (11); read 2: none; read 3: 46902 (14) | read 1: none; read 2: 46913 (3); read 3: 46902 (11), 46913 (3) |
   | track 3 second 251 | 46918 to 46943 | read 2: 46925 (3); reads 1 and 3: none | none in 3 reads |
   | track 3 second 251 | 46944 to 46969 | none in 3 reads | none in 3 reads |
   | track 3 second 252 | 46967 to 46992 | none in 3 reads | none in 3 reads |
   | track 3 second 252 | 46993 to 47018 | read 2: 47006 (2), 47007 (1); reads 1 and 3: none | read 2: 46995 (6); reads 1 and 3: none |
   | track 3 second 252 | 47019 to 47044 | none in 3 reads | none in 3 reads |
   | track 5 second 144 | 83370 to 83421 | none in 6 reads | none in 6 reads |
   | track 5 second 144 | 83422 to 83447 | 83430 (3 bits) in all 3 | read 1: 83443 (3); reads 2 and 3: 83430 (3) |

   - **Checked independently.** The 23:38Z column is our decoding of the kept bytes, counting
     set bits in each frame's 294. It matches the script's own summary read for read. The 16:04Z
     column is the script's summary alone, because its bytes were overwritten.
   - **The `14h` read** at 83416 sets 3 C2 bits at LBA 83430 and the block error byte `38h`. That
     matches the first probe of 2026-11-11 (`docs/rig-2026-11-11b-c2probe/`).
2. **Track 5's flag is where it was.** LBA 83430 is the frame round 39's probe flagged, the
   sample range CTDB's majority entry disagrees with (track 5's "3 samples @02:24:59"), and it
   is flagged in 5 of 6 reads here.
3. **The solo read and pair B printed `Opening drive...` and nothing more in 300 s,** in both runs.
   - **Exit codes.** Each exited 137, killed after the 300 s limit and its 5 s grace
     (`probe/summary.txt`; `drivetest.log:513`, `:526`, `:632` and `:645`).
   - **Pair A got further.** In the 23:38Z run it printed track 1's block and
     `Still waiting: the ISRC search of the Q frames for track 2 has not returned after 10s`,
     and was stopped at 300 s, exit 124 (`probe/pairA.txt`, `probe/pairA.rc`).
   - **Under `strace`,** pair A reached the second pregap searches (`probe/pairA-strace.txt`).
     The traces hold 906 and 697 `CDROM_SEND_PACKET` calls (`probe/pairA.strace`,
     `probe/pairB.strace`).

## What it does not establish

- **Whether a flagged frame read wrong.** The audio was dropped before upload, so no read here can
  be compared with the disc.
- **Whether the flags at track 3's seconds 251 and 252 line up with the rips' disagreeing
  seconds.** That needs the round's rip records, which are not in this delivery (*Possibly
  missing*).
- **Where the solo read sat.**
  - `.35` names the drive open as a wait, with a 10 s threshold by default
    (`src/cyanrip_main.c:496`, `:497`, `:3450`).
  - `cyanrip_log()` flushes stdout after every message (`src/cyanrip_log.c:1689`).
  - So a block in the drive open, or in any wait `.35` names, would have printed
    `Still waiting:`. None printed.
  - Either the read sat in a call no wait names, or the watchdog did not print. Without a trace
    of the solo read, which one is not known.

## Questions, gaps and next time

**Questioned:**
- **The solo read's silence on `.35`** (`probe/solo.txt`). It is round 39's lone read again
  (`docs/rig-2026-11-11b-c2probe/`), now on a build that names every wait after the open. Ours:
  HW-13. Settled by a trace of the solo read.
- **The varying flags at track 3's seconds 251 and 252** (the table). The drive flags different
  frames, and different bit counts, on reads minutes apart. Settled by the rips' per-second CRCs
  for those seconds, once the rip records are filed. Ours.

**Possibly missing:**
- **The 16:04Z run's own files.** The script overwrites `probe/` on each run, so only its summary
  survives. Theirs.
- **How the 23:32:04Z start ended** (`drivetest.log:626`). Theirs.
- **The script's revision** in `drivetest.log`. Theirs.
- **The round's rip records,** for G2's other half: what the `C2 errors:` lines and records say.
  The Full run's bundle was deleted by Platterpus's prune before it reached us
  (`applog/log.txt.1:34817`, `:34819`, `:49396`). Its session folder and rip folders are being
  collected separately.

**To add next time:**
- **Each run's `probe/` folder under its own stamp,** so a second run does not erase the first.
  Theirs.
- **An `strace` of the solo read,** not only of the pair. Theirs, with ours to read it.

**More than we asked:**
- **The app log** runs from 2026-11-18 to 2026-11-24 16:04:16Z, with both Full runs of round 42
  in it: 23:49:47Z to 06:16:47Z (`applog/log.txt.1:818` to `:34824`), and 09:38:24Z to 16:04:16Z
  (`:34829` on).
- **The window behind the first probe's stop.** It is the desktop launch of 23:04:47Z, closed at
  09:38:04Z (`applog/log.txt.1:34825` to `:34827`). The stopped probe's README reads it.
