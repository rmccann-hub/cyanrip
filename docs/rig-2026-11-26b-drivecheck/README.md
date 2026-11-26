# Rig session 2026-11-26: `.35`'s `-I -N` alone on the reference disc, and the drive's door setting

**What this is.** The two checks round 43's runs left (our round 43 lap 1, S67), run by the
owner on 2026-11-26 from a terminal, with Platterpus closed and nothing else holding the drive:
- **The timed read.** `time ~/.local/bin/cyanrip -I -N -d /dev/sr0` on the reference disc
  (US-44, HW-20).
- **The door setting.** `cat /proc/sys/dev/cdrom/lock` and `/proc/sys/dev/cdrom/info`
  (R43-4).
- **Not run.** The optional `strace` step: the ripping container has no `strace`.

**Where it comes from.** One archive the owner made with the commands we gave,
`drivecheck-20261126T131329Z.tar.gz`, sha256
`33225a340094c8c7b580185bcbcf24cba447606111dba749698ff57afc009f84`, 3,401 bytes, seven
files, all filed under `drivecheck/`. **No sender's hash**: the archive is the delivery, and
`SHA256SUMS` gives its hash and each file's. `tools/redact.py` replaced nothing; the owner's
name was not checked, for want of a local list.

**Read the build, not the date.** `version.txt` and the log header both read
`cyanrip 0.9.4-rc3+platterpus.35 (platterpus-fork-g1280aa4)`. The disc is the reference disc:
MusicBrainz disc ID `pNtImOkdBm9RMBIalzx0w9cfsYY-` in the read's own output.

## What it establishes

1. **`-I -N` took 18.7 s with the drive to itself, and named no wait.**
   - **The times.** It ran from `2026-11-26T13:07:47Z` (`start.txt`) to `13:08:06Z`
     (`end.txt`); `time` reads `real 0m18.663s`, `user 0m0.084s`, `sys 0m0.117s`
     (`info-run.txt:549-551`).
   - **No wait named.** The output holds no `Still waiting:` line, so none of the waits `.35`
     names after `Opening drive...` lasted 10 s, track 9's search with its 200-retry pass
     included.
   - **The same searches as before.** It found the nine pregaps every rip of this disc finds,
     track 9's decided at 95 frames, from the same searches: track 2's asked 144 sectors and
     track 9's 150, `92 frames were another sector's; …; 200-retry pass ran`
     (`info-run.txt:46-70`).
   - **So the minutes of 2026-11-25 were the shared drive.** There the same build's `-I -N`
     named waits of 12 to 41 s per search and was killed at 300 s while `cd-paranoia -A`
     timed the drive (`docs/rig-2026-11-25-drivesetup/`). Alone, the whole read takes 18.7 s.
     **US-44 is not a defect of ours.**
2. **HW-20's silence did not recur.** The solo reads of 2026-11-11 and 2026-11-24 printed
   `Opening drive...` and nothing more in 300 s. This one printed its whole output. What held
   those reads is still not known, and nothing here traces one.
3. **The kernel's door setting is on.**
   - **The setting.** `/proc/sys/dev/cdrom/lock` reads `1`.
   - **The drive.** `cdrom-info.txt` lists `Can lock tray: 1` for `sr0`.
   - **Not checked here:** whether cyanrip's open of `/dev/sr0`, through libcdio, is one the
     kernel locks the door for. R43-4 keeps that question.

## What it does not establish

- **Why the solo reads of 2026-11-11 and 2026-11-24 were silent.** No trace was taken, then or
  now.
- **Anything about a drive with no cache, a damaged disc, or another drive.**

## Questions, gaps and next time

**Questioned:** none.

**Possibly missing:**
- **A trace.** `strace` is not installed in the ripping container
  (`strace-run.txt`: *"executable file `strace` not found in $PATH"*).

**To add next time:**
- **If a solo read is ever silent again:** `strace` installed in the container, and the same
  read under it. Ours to ask.
- **For R43-4:** during a rip, press the drive's eject button and note whether the tray opens.
  The owner's.

**More than we asked:** the drive's whole `cdrom-info.txt` capability list.
