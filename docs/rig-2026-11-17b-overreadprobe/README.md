# Rig session 2026-11-17b: the overread probe, Platterpus's runner, the reference disc

**What this is.** Platterpus's UI script `overreadprobe` (`probe/overreadprobe.txt`, as delivered),
run by the owner from Platterpus 0.7.127 on the BDR-209D (revision 1.51) from 22:57:58Z. It
installed `.34`, `cyanrip 0.9.4-rc3+platterpus.34 (platterpus-fork-gfb28088)`, and ran two
bounded `-O` reads:

- **Lead-out:** the last track, 14, at the drive's offset of +667:
  `cyanrip -N -s 667 -l 14 -O -D overreadleadout`. That reaches two frames past the disc's end.
- **Lead-in:** track 1 at a deliberately wrong -667: `cyanrip -N -s -667 -l 1 -O -D
  overreadleadin`. That reaches two frames before LSN 0.

Each ran with `--consumer platterpus/0.7.127` and `--diagnostics`, under the runner's fixed
300-second limit. This is round 41's missing `-O` read (`docs/OPEN-ITEMS.md` R41-9), run after
the round's rip of the same day (`docs/rig-2026-11-17-fb28088/`).

**What was delivered and filed.** Three files, under `probe/`: the runner's `transcript.txt`, which
holds each step's argv, exit code and complete standard output; its `report.json`; and the script.
The owner sent the transcript and the report twice, byte for byte the same. Home-folder paths were
replaced by `tools/redact.py`, 7 in each of the two, and `SHA256SUMS` gives each file's delivered
and filed hash. No hostname was in them.

## What it establishes

1. **The bound holds at both edges on this drive, and nothing hung.**
   - **Lead-out:** exit 0 in 73.4 s, `Elapsed: 62.75 s`.
   - **Lead-in:** exit 0 in 87.4 s, `Elapsed: 75.58 s`.
   - **Neither came near the limit.** Both printed `Read stalls: none (no read exceeded 10s)` and
     `Ripping errors: 0`.
2. **The BDR-209D refused every frame asked outside the disc.**
   - **Lead-out:** `Overread: +2 frames`, then `Beyond disc: 2 of 2 frames refused (written as
     silence)`. `End LSN: 268706 (with offset: 268708)` puts both past the disc's last sector.
   - **Lead-in:** `Underread: -2 frames`, then `Beyond disc: 2 of 2 frames refused (written as
     silence)`. `Start LSN: 0 (with offset: -2)` puts both before LSN 0.
   - **The line has now printed on a drive.** It had not until this run.
3. **On this drive `-O` gave track 14 nothing a default rip lacks.**
   - **The comparison:** its EAC CRC32 is `787BA2D6`. All seven `.34` logs of round 41's rip that
     carry track 14 give the same: the full-acceptance rip, the five repeat rips and the secure
     re-read. All seven ran without `-O` (`Overread mode: fill with silence in lead-in/lead-out`).
   - **What it shows:** refused and written as silence, the frames past the lead-out give the
     bytes the default fill gives.
4. **Track 14's AccurateRip match does not speak to those samples.**
   - **The match:** `Accurip v1: 3B2FCF8E (accurately ripped, confidence 117)` and `v2: A5AB0AE9`
     (confidence 200).
   - **Why it cannot:** the AccurateRip sums of a disc's last audio track leave out its last five
     frames, 2,940 samples (`cyanrip@fb28088:src/checksums.h:83-84`). The 667 samples the refused
     frames would have supplied are among them.
5. **Track 1 at -667 matches nothing, as a wrong offset should.** `Accurip v1: AB78CDFB` and `v2:
   B75F1E79` are each `not found`, and `Tracks ripped accurately: 0/1`.

## Questions, gaps and next time

- **Questioned:**
  - **`force_overread` was on after the run.** The script's last step, `expect force_overread
    off` ("nothing here turned overread on for your rips"), failed: `expected force_overread ==
    False, got True` (`transcript.txt`, line 421). It is Platterpus's setting, and the delivery
    does not say whether the run turned it on or it was on before. Theirs to answer, and the owner's
    to check before the next rip from Platterpus (`docs/OPEN-ITEMS.md` PP-16).
  - **Track 9's pregap read two ways.** The lead-out step printed `pregap of track 9: 94 or 95
    frames (undecided)`, and the lead-in step, started 74 seconds later by its diagnostics file's name,
    `95 frame pregap in track 9`. That is one more pair for `STATUS-OPEN subchannel-pregap-varies`, the same LSN 145567.
- **Possibly missing:** the two logs, in `overreadleadout/` and `overreadleadin/`, and the two
  diagnostics records the argv names. The script says the bundle the run ends with carries both
  logs, and only the transcript, the report and the script were delivered. So the log files
  themselves are not read here, only what the transcript holds of standard output, which carries
  every log line.
- **To add next time:**
  - **A drive that answers past its lead-out.** This run took only the refusal arm of the bound;
    the arm that reads a frame once and keeps it has not run on a drive (`docs/OPEN-ITEMS.md`
    HW-10).
  - **The C2 probe at the seconds round 41 named** has still not run (HW-1).
- **More than we asked:**
  - **`Invoked as:` names `/usr/local/bin/cyanrip`, where the runner's argv names
    `~/.local/bin/cyanrip`.** The C2 probe of 2026-11-11 showed the same two paths.
  - **`Handshake: round 41 lap 1 OPEN`** is `.34`'s, built before our lap 3 was committed, as a
    build always predates the laps that name it.
