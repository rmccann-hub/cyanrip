# Rig session 2026-11-24: round 42's C2 probe, stopped before any read

**What this is.** Platterpus's `docs/rig-scripts/drivetest.sh`, its `probe` entry, run by the
owner at 06:16:47Z, a few seconds after round 42's Full run quit. That run's bundle,
`platterpusbundle20261123t2349480000.tar.gz`, never reached us: Platterpus deleted it (*Possibly
missing*, below). The probe installed its tools and stopped at 06:17:00Z, before any read.

The owner uploaded it as `platterpusdrivetest42probestopped.tar.gz` (sha256
`79123e2624e56ff10446e5d7cdc394f56590de225f379adb559a2afcf5a9b5d5`, 485,120 bytes).

- **Integrity.** All five members it lists match the sender's `MANIFEST.txt`. Two folders,
  `bundles/` and `scriptruns/`, arrived empty.
- **Personal details.** `tools/redact.py` replaced 1,158 home paths in `applog/log.txt` and 2 in
  `records/RECORDS.txt`. It found no hostname, and the owner's name was not checked, for want of
  a local list.
- **Hashes.** `SHA256SUMS` gives each file's filed hash, and the delivered hash of each file
  that changed. `MANIFEST.txt` is filed as delivered, so its hashes are of the delivered bytes.

**Read the build, not the date.** No cyanrip ran.

- **The app.** Platterpus 0.7.129 (build `a964e3b`) ran the Full run (`applog/log.txt:818`).
- **The script.** `drivetest.log` does not name the script's revision. Its stop is the same line
  at `platterpus@a964e3bd:docs/rig-scripts/drivetest.sh:698` and `@9d9177a2:…:700`.
- **The clock.** The app log keeps local time, five hours behind the drive test's UTC: its quit
  at 01:16:46 is 06:16:46Z. Times below are UTC.

## What it establishes

1. **The probe read nothing from the disc.**
   - `drivetest.log:2` starts the tool install at 06:16:47Z: `cdrdao`, `sg3_utils`, `strace` and
     their dependencies, 139 packages, 55 MiB.
   - `drivetest.log:496` stops at 06:17:00Z with `Platterpus is open. Close it, then run this
     again: the probe needs the drive to itself.`, as does `errors.txt`.
   - `kernel.txt` holds no line about the drive.
   - `records/RECORDS.txt` reads `ripper records: 0 of 0 found`.
2. **The stop is a name match.** Their `probe()` runs
   `pgrep -f "platterpus-x86_64.AppImage"` after installing its tools and before waiting for the
   disc. Any match stops it (`platterpus@9d9177a2:docs/rig-scripts/drivetest.sh:700`).
   - `-f` matches any process whose whole command line holds that name.
   - The stop prints neither the process nor its command line.
3. **The app log holds six launches, and one never says it ended.**

   | Launch | Line | How it ended | Line |
   |---|---|---|---|
   | 2026-11-18 22:32:06Z, 0.7.128, desktop | 2 | exit check, 22:35:06Z | 301 |
   | 2026-11-18 22:35:08Z, 0.7.128, desktop | 303 | exit check, 22:48:00Z | 462 |
   | 2026-11-18 22:50:33Z, 0.7.128, desktop | 464 | exit check, 22:51:35Z | 673 |
   | 2026-11-23 23:04:33Z, 0.7.128, desktop | 675 | relaunch into the update, 23:04:47Z | 703 |
   | **2026-11-23 23:04:47Z, 0.7.129, desktop** | 705 | **no line**; its last, 23:11:56Z, opens the Run tests dialog | 816 |
   | 2026-11-23 23:49:47Z, 0.7.129, `--run-script fullacceptance` | 818 | exit check, 2026-11-24 06:16:47Z | 34824 |

   The Full run's launch waited for its bundle to be written (`:34815`) and quit at 06:16:46Z
   (`:34820`). Its exit check at 06:16:47Z reads `nothing holds /dev/sr0; no ripper process is
   running, as the host sees them` (`:34824`).

4. **The 23:04:47Z launch was still open when the probe looked.** This bundle cannot show it;
   the next one can. The probe's completed run of the same day
   (`docs/rig-2026-11-24b-c2probe/`) carries the app log onward. In its `applog/log.txt.1`, the
   only Run tests dialog of the day closes at 2026-11-24 09:38:02Z (`:34825`). A window is closed
   "from outside the app" at 09:38:04Z (`:34826`) and gives its exit check (`:34827`). The next
   launch starts at 09:38:24Z (`:34829`). No launch starts between 23:49:47Z and 09:38:24Z, and
   the Full run's launch had already given its exit check at 06:16:47Z. So the window closed at
   09:38:04Z is the 23:04:47Z launch, open from 23:04:47Z to 09:38:04Z. **The probe's stop at
   06:17:00Z was right.**

## What it does not establish

- **Which process the check matched.** The stop names none. The 23:04:47Z launch was running, so
  the check had a true match; whether it matched anything else as well is not recorded.
- **Anything about the drive or the disc.** Nothing read them.

## Questions, gaps and next time

**Questioned:**
- **Their account of this stop.** Platterpus's `drivetest.sh` since `2de917f7` (2026-11-24
  12:48Z) waits up to 120 s for the app to close. Its stop now names each process still running
  (`platterpus@e279ded9:docs/rig-scripts/drivetest.sh:213` to `:232`, `:724`). Its comment says
  this probe "stopped on "Platterpus is open" when nobody had a window open" (`:222`).
  Their own app log contradicts that (point 4): a window opened at 23:04:47Z stayed open until
  09:38:04Z. The wait does no harm, and naming the process settles the next stop. The comment's
  claim is theirs to correct, and our next lap says so.

**Possibly missing:**
- **The Full run's bundle.** Platterpus deleted it. The app log (`docs/rig-2026-11-24b-c2probe/`,
  `applog/log.txt.1`) has it written at 06:16:46Z (`:34817`), with `SEND THIS ONE FILE` naming it
  (`:34819`). It was pruned at 12:24:01Z, `keeping 20` (`:49396`), after 20 more bundles from a
  second Full run started at 09:38:24Z. The prune protects only the bundle it has just written
  (`platterpus@a964e3bd:src/platterpus/evidence_bundle.py:1118`, `:1135`). Theirs; our next lap
  reports it.
- **The round 42 probe in their rig sheet.** `docs/rig-session.md`'s *What the next session is
  for* still described round 41's run at `platterpus@9d9177a2:docs/rig-session.md:22`. The
  probe's command is in `platterpus@9d9177a2:docs/rig-scripts/README.md:204`, and 0.7.129's Run
  tests dialog points to it (`platterpus@a964e3bd:src/platterpus/ui/dialogs/run_tests_dialog.py:79`).
  Theirs.
- **The script's revision** in `drivetest.log`. Theirs.

**To add next time:**
- **Before the probe,** `pgrep -af platterpus-x86_64.AppImage` should print nothing. The owner
  runs it, closing any window it names.

**More than we asked:** the app log gives the Full run's app-side timeline: started at
23:49:47Z (`:818`), batch finished at 06:16:44Z (`:34815`), quit at 06:16:46Z (`:34820`).
