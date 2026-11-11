# Rig session 2026-11-10 — build `5cc1c6b` (`.30`), Platterpus 0.7.121, **Full**, the reference disc

**Read the build, not the date.** `.30` at `5cc1c6b`, through Platterpus
**0.7.121**, the newest app tag when the run began, 22:55:24Z. Eighteen logs
open with `platterpus-fork-g5cc1c6b`; six are `.28` at `3f288fb`, installed
only for the timed rips `timing A1` and `A2` and the paired rips `accuracy A1`
to `A4`. It is phase 4 of round 38's drive test, its last.

**The script's verdict is not a pass**: pass 592, fail 2, error 0, unreachable
1, info 22 (`session/run/report.json`), the shape of the `.29` Full run of
2026-11-04. Both failures are `expect-ctdb whole` (L783 and L1383), on the two
whole-disc rips, grading track 5's read. The unreachable step is the offset
refusal this drive cannot reach.

**Every member matches the sender's own hash**: 183 of 183. Every one of the 24
cyanrip logs ends with its signed completion footer, and every one says `Read
stalls: none`.

## What it establishes

1. **Track 5 read `E0036697` in both whole-disc rips**, and the secure re-read
   converged on it after 3 reads; AccurateRip does not verify it, as in every
   session of this disc on this drive.
2. **Platterpus's automatic CTDB repair committed on both** (their 0.7.121,
   first on hardware): *"CTDB repair repaired: track(s) 5 rewritten toward
   entry 32115 (1,425 submissions)"*, then *"CTDB after it: match"*
   (`session/transcript.txt`). The repair is theirs to read; ours is that the
   read it repaired is the one `.30` always makes.
3. **Track 3 verified in 5 of 14 rips** (`59D352DD`), counted from the
   EAC-compatible logs: the whole-disc rip, the secure re-read and three of
   four timed rips verify; none of the eight paired `accuracy` rips does
   (`3D8FCF0C` six times, `0EE1440E`, `2363932F`). By build: `.28` 2 of 6,
   `.30` 3 of 8. Nothing in the build decides it.
4. **13 of 14 tracks verify** in the secure re-read, every track converging
   after 3 reads; track 5 is the one.

## What it does not establish

- Whether AccurateRip agrees with the repaired track 5: the repair record is
  Platterpus's, and its after-repair AccurateRip values are theirs to read.
- Why track 3 reads as it does: no step here varies anything that changes it.

## Questions, gaps and next time

**Questioned:** none of `.30`'s lines.

**Possibly missing:** the C2 probe at the wrong samples, which neither runner
ran on this disc.

**To add next time:** the C2 probe and the two-read check of
`tools/rig-drivetest.sh`, in Platterpus's runner (round 38 lap 16).

**More than we asked:** the first hardware run of Platterpus's automatic CTDB
repair.
