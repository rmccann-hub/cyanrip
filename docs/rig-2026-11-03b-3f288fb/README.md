# Rig session 2026-11-03 (second) — build `3f288fb`, Platterpus 0.7.119, **Full**, the reference disc

**Read the build, not the date.** This is `3f288fb`, `+platterpus.28`, through
Platterpus **0.7.119**, which names `.28` as both its fork pin and its build
under review. `tools/ingest-bundle.py --peer` reads both as the newest when
the run began at 23:05:46Z. It is the second Full run of `.28` that day, so its
folder takes the `b` suffix. It is not a round's run: round 37 closed before it
began. The claude-code-skills note of 2026-11-03 asks each side to read it.

**The run did not pass.** The script's own verdict is pass 462, fail 16, error 0,
blocked 1, unreachable 128, info 9, and `ok: false` (`session/run/report.json`).
**Every failure follows one event: the drive failing mid-rip.** None of them
points at `.28`.

**Every member matches the sender's own hash**: all 110 members that the
bundle's `MANIFEST.txt` hashes match it byte for byte. `tools/ingest-bundle.py`
filed 53 members and named 58 it did not file, each in `SHA256SUMS`. All 12
signed logs verify with `-Y`. Nothing needed replacing. The owner's name was not
checked, because no local list of names exists here, and not checked is not the
same as not present.

## What happened

- **The secure re-read** (`-Z 2 -r 5`) began at 00:00:24Z, according to its
  record's name. Tracks 1 to 9 read with no error reported. During track 10,
  the drive answered `007: Unknown, unrecoverable error reading data` 6,720
  times (`READERR: 6720`), and `Unable to access sector 170017`. One read
  stalled for 17 s at LSN 170803. Then `Drive media change query failed
  (libcdio error -1), stopping!`.
- **The log closed as it should**: a signed footer, `Rip completed:  no
  (aborted, 9 of 14 tracks)`, `Partial files:  1 track (10), read not
  completed`, and exit 74.
- **After that, every cyanrip call exited 74** with `Unable to open device:
  /dev/sr0`: `-f`, `--cache-probe -I`, the offset refusal `-l 1`, and both
  de-emphasis rips. Each printed the reason at column 0.
- **The 16 failures**:
  - the secure re-read's completion, and its seven checks that need a whole
    rip (verification, album audit, AccurateRip, CTDB, read offset, tags, cover
    art);
  - two each for `-f`, the cache probe, the offset refusal, and the two
    de-emphasis rips.
- **The 128 unreachable steps** are the script's later sections, which never ran
  with no drive. One step is `blocked`.

## What `.28` showed, on a drive for the first time

- **A drive that reports failed reads.** This is `CLAUDE.md`'s *damaged media*
  row's missing arm, and part of `hardware-unverified`. Here the disc was not
  damaged; the drive failed.
- **`error_positions` filled from a real drive.** Track 10's entry in the
  `--diagnostics` record holds 1,000 positions: 995 `read_error` and 5 `skip`,
  from LSN 170832 to 171270. It counts 5,748 more in `error_positions_dropped`.
  `audio_ripped` is false.
- **The read-stall watchdog on a real stall**: `Read stalls:    1 read exceeded
  10s; longest 17s (track 10, LSN 170803)`. The record's `read_stalls` field
  agrees.
- **The not-written-whole footer** names track 10.

## The reads before the drive failed

`tools/cross-rip.py` over the run's logs:

| track | reads | distinct checksums | what AccurateRip says |
|---|---|---|---|
| 1 | 15 | 2 | `B0D122E7` 14 times, matched; `0E91CD1A` once (`derived wavpack`), frame 450 only |
| 3 | 7 | 1 | `3D8FCF0C` every time, not found |
| 5 | 7 | 1 | `E0036697` every time, not found |
| 2, 4, 6 to 9 | 4 to 9 | 1 | matched |
| 10 to 14 | 1 each | — | the full rip only |

- **Track 3 read wrong in every read of this run.** On the earlier run of the
  same day it read right in 14 of 21 reads. `3D8FCF0C` is the wrong value
  already seen there and on 2026-10-28.
- **Track 5 read `E0036697` again**, as it has since 2026-10-06.
- **Track 1 read wrong once.** It has never read wrong in an earlier run.
- Track 9's pregap was decided in one log, `derived mp3`, as 95 frames. The
  other 11 logs say `unknown (sub-channel search bounds did not meet)`.

Wrong reads spreading to a track that never read wrong before, and then a drive
that stopped answering, point at the drive or its connection getting worse
during the session. Nothing in the bundle rules out the disc. Nothing points at
the build: `.28` read these same tracks right earlier that day.

## Questions, gaps and next time

**Questioned**

1. Is the BDR-209D, its cable or its USB port failing? The kernel log from the
   rig around 00:31Z would say whether the device dropped off the bus. Settled
   by: the rig's `dmesg`. Owner: the operator.
2. The footer says `Ripping errors: 57 (including 28 paranoia skips)`, while
   paranoia counted `READERR: 6720`. Neither line says what one counted that
   the other did not. Settled by: reading the read loop's counting against this
   log, and a wording in round 38, beside A5's, if the two differ by design.
   Owner: us.

**Possibly missing**

1. The kernel's view of the drive's failure. Not in the bundle, as above.
2. Track 3's FLACs from this run and the earlier one would say where `3D8FCF0C`
   differs from the matched read. Owner: the operator.

**To add next time**

1. Repeat the Full run once the drive is checked. This run says nothing about
   steps after the secure re-read. Owner: the operator.
2. `error_positions` keeps 1,000 positions per track and counts the rest. A
   drive that fails for good can fill that in one track. Whether 1,000 is the
   right cap is for round 38. Owner: us, with Platterpus.

**More than we asked**

1. The failed-read arm of `hardware-unverified` is now shown on a drive.

**Every fact above can be re-derived** with `tools/read-run.py
docs/rig-2026-11-03b-3f288fb --cyanrip build/src/cyanrip` and
`tools/cross-rip.py docs/rig-2026-11-03b-3f288fb`, through `tools/evidence.py
run`.
