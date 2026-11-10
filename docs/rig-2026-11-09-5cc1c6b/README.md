# Rig session 2026-11-09 — build `5cc1c6b` (`.30`), Platterpus 0.7.121, round 38's drive test, phases 1 to 3

**Read the build, not the date.** Every one of the 41 rip logs here opens with
`cyanrip 0.9.4-rc3+platterpus.30 (platterpus-fork-g5cc1c6b)`; the app is
0.7.121 (`2ca5196`); the drive the BDR-209D, firmware 1.51; the disc the
reference disc. The runner was Platterpus's `docs/rig-scripts/drivetest.sh`
from their branch `claude/session-omka9f`, whose rig scripts were 9800 and
10694 bytes (`session/drivetest.log:6`), not the 8598 and 9492 of the printed
sheet: their release pick by MBID. Phase 4, the Full run, was still running
when this was filed.

**What is here.** `runA/`, `runB/` and `runC/` are the three bundles the app
wrote, filed by `tools/ingest-bundle.py`: 12, 12 and 17 cyanrip logs, each
ending with its signed completion footer. `session/` is the runner's own
output, the track 9 reads and the phase 3 screenshot, with `SHA256SUMS` giving
the delivered and filed hash of each. Personal details were replaced by
`tools/redact.py`.

## What it establishes

Counted from the 41 rip logs themselves, each log's track CRC and its
`Accurip v1` line, which agree with the runner's summary line for line:

| | Rips | AccurateRip-verified | The other values |
|---|---|---|---|
| Track 5, Runs A, B and C | 19 | 0 | `E0036697` 18 times; `6902BCF0` once, Run C's `dsfivespeedfour1` |
| Track 3, Run A (disc left in) | 6 | 2 | `3D8FCF0C` twice, `DBA21A84`, `E45FCE56` |
| Track 3, Run B (after the wipe) | 6 | 2 | `3D8FCF0C` twice, `0EE1440E`, `CEC480C2` |
| Track 3, Run C, speed not set | 4 | 2 | `3D8FCF0C` twice |
| Track 3, Run C, `-S 4` | 3 | 1 | `3D8FCF0C` twice |
| Track 3, Run C, `-S 24` | 3 | 0 | `3D8FCF0C` twice, `52DFDF7D` |

1. **Track 5 reads one wrong value**, `E0036697`, in 18 of 19 rips, AccurateRip
   matching it at frame 450 only, as every earlier session of this disc on
   this drive has.
2. **Track 3 verifies 7 times in 22** (`59D352DD`). Ten of the 15 wrong reads
   are one value, `3D8FCF0C`. Wiping the disc between Run A and Run B changed
   nothing measurable: 2 of 6 before, 2 of 6 after. The session clustering of
   2026-11-03 (8 of 8) and 2026-11-04 (0 of 8) did not recur: verified and
   wrong reads alternate within each run.
3. **The speed asked for did not change the speed read.** Run C's logs print
   `Speed: 4x` or `Speed: 24x`, so the drive took the command without an
   error, yet every one of the 41 rips read at 2.9x to 3.5x by its own
   `Extraction speed:` line. The drive's settings block reports Quiet mode on
   (bytes 2 and 3 are `02`, by pioneer-optical's reading); whether that is the
   cap is not established.
4. **Phase 2 completed**: three raw and three formatted Q reads of track 9's
   pregap and cdrdao's TOC (`session/track9/`).
5. **Phase 3: Pioneer's utility does not reach this drive.** Windows lists
   `PIONEER BD-RW BDR-209D`, working properly (the owner's Explorer
   screenshot, not filed); `PioneerBDR-209-211_DriveUtility_v1.2.0.3.exe`, run
   as administrator, says *"The drive is not connected"*
   (`session/phase3-pioneer-utility.png`). With the settings block's byte 9 =
   0, no PureRead setting is reachable on this drive, so Run D could not run.
6. **No disc read timed out on 2026-11-09.** The app log carries one start-up
   double probe, at 22:42Z, before the runner began.

## What it does not establish

- Why track 3 and track 5 read wrong: the drive's error handling is the
  hypothesis the PureRead runs were to test, and they cannot run here.
- Whether Quiet mode caps the speed: turning it off needs a write to the
  drive, which no side has agreed, and Pioneer's utility cannot reach it.
- Anything of phase 4.

## Questions, gaps and next time

**Questioned:**
- `dsfivespeedfour1`: one track 5 read of `6902BCF0`, the only other value
  track 5 has given in this session. One read; nothing settles it but more.

**Possibly missing:**
- The C2 probe and the two-read check of `tools/rig-drivetest.sh`, which
  Platterpus's runner does not carry: whether the drive flags the wrong
  samples with C2 pointers is still unmeasured.

**To add next time:**
- READ CD with C2 pointers at track 3's and track 5's wrong samples, as
  `tools/rig-drivetest.sh`'s C2 probe does.
- Our `.31` liveness line for the stretch after the drive open (round 38 lap
  14 S8), so a stall like 2026-11-06's names what it waits on.

**More than we asked:** every rip carries the cache probe's measurement, 128
to 255 sectors (`session/drivetest.log`).
