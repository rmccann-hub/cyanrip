# Rig session 2026-11-04 — build `8d2ca72`, Platterpus 0.7.120, **Full**, the reference disc

**Read the build, not the date.** This is `8d2ca72`, `+platterpus.29`, through
Platterpus **0.7.120** (`v0.7.120`, tagged 2026-11-04T10:20:43Z). Nineteen
logs open with `cyanrip 0.9.4-rc3+platterpus.29 (platterpus-fork-g8d2ca72)`,
the securing pass among them. Six are `.28` at `3f288fb`, installed for two
steps only: the timed rips `timing A1` and `A2`, and the paired rips
`accuracy A1` to `A4`. `tools/ingest-bundle.py --peer` reads 0.7.120 as the
newest tag when the run began, 12:53:46Z, and the ripper as two builds, as
those two steps run.

**It is round 38's closing run**: the Full run of the reference disc on `.29`
through Platterpus's first release naming it as their build under review (our
lap 1 S14; their lap 6 S3 and S4). **No reading plan was written for it before
it arrived**, as round 37's was (`docs/ROUND-37-READING-PLAN.md`). Dumbass us:
the procedure says a run expected in advance gets one. This reading is held to
`.29`'s changes as our lap 3 gave them as built, each checked below.

**The script's verdict is not a pass**: pass 591, fail 2, error 0, skipped 0,
blocked 0, unreachable 1, info 22, `ok: false`, `counts_as_evidence: true`,
run size full (`session/run/report.json`). Both failures are the same step,
`expect-ctdb whole` (L779 and L1379), on the two whole-disc rips, and both
grade track 5's read, which the earlier readings of this disc report the
same way (below). The unreachable step is L618, `expect-offset-refusal`, which this
drive cannot reach because it is in AccurateRip's drive list, as on every run
on it.

**Every member matches the sender's own hash**: all 184 members the bundle's
`MANIFEST.txt` hashes match it byte for byte. `tools/ingest-bundle.py --into`
filed 104 members and named 81 it did not file, each in `SHA256SUMS`. The 26
`--diagnostics` records are among those named, and were read from the bundle.
**Nothing needed replacing.** The owner's name was not checked, because no
local list of names exists here, and not checked is not the same as not
present. **All 25 signed logs verify with `-Y`**, the securing pass among them.

## What it shows

### Round 38's close condition

- **The run is the one our lap 1 S14 names**: `.29` through 0.7.120, which
  names `.29` as its build under review. It is filed here with its manifest
  rows. Platterpus's reading is theirs to file.
- **No defect in `.29` makes the pin unsafe to approve.** Every log reaches
  its signed footer. Every rip but the one the script cancels read every
  track it was asked for, with `Ripping errors: 0` in all 25. The wrong reads
  below happen on both builds, and in earlier filed runs of this disc, and
  each log says so rather than calling the track verified.

### What `.29` changed, on a drive for the first time

Each is round 38's, as Platterpus's lap 2 accepted it and our lap 3 gave it as
built.

- **`Secure re-reads:` (A5)**: `Secure re-reads: every track converged` in
  the secure re-read rip (line 1300) and in the full rip's securing pass (line
  275). Both rips converged on every track: 13 after 3 reads, and track 3
  after 5.
- **The tallies (B5)**: they divide by the tracks asked. The four `.29` single-
  track rips of track 3 read `Tracks ripped accurately: 0/1` and `Tracks
  matched on one frame only: 1/1`, where the four `.28` rips of the same track
  read `0/14` and `1/14`. **`-f` prints neither**: the offset search, on
  `.29`, goes from `Read stalls:` to `Rip completed:  no (offset search only, 0
  of 14 tracks)` (`session/transcript.txt`, lines 1307 and 1308). **A cancel is not a ripping
  error**: `cancel me`, stopped by SIGTERM in track 2, reads `Ripping errors:
  0` and `Rip completed:  no (interrupted by SIGTERM, 1 of 14 tracks)`.
- **`Filtered:` (A6)**: `Filtered:      hdcd, de-emphasis; the checksums and
  AccurateRip verdicts above are of the read, before the filter` with `-H -E`
  (`r16deemphon`), and `Filtered:      hdcd; ...` with `-H` alone
  (`r16deemphoff`). Track 1, which both rip, is neither HDCD nor pre-emphasised
  (`HDCD detected: no`, `Preemphasis:   none detected`), so each filter ran
  because it was asked for, which is what the line says.
- **The undecided pregap (A7)**: track 9's search narrowed to one sector and
  left it, so `Gaps:` reads `pregap of track 9: 94 or 95 frames (undecided)` in
  18 of the 19 `.29` logs. Where track 9 was ripped, its block reads `Pregap
  LSN:  145567 or 145568 (undecided)` and `Pregap length: 94 or 95 frames
  (undecided)` (the full rip, line 733; the secure re-read, line 797), and each
  cue puts its `INDEX 00` at `03:44:10` of track 8's file. Track 8 starts at
  LSN 128757, so that is LSN 145567, the earlier bound, as built. Five of the
  six `.28` logs read `unknown (sub-channel search bounds did not meet)` for
  the same search, as `.28` does. The nineteenth `.29` log and the sixth `.28`
  one decided it (below).
- **`block_crcs` (S10)**: all 20 `.29` records are `cyanrip-diagnostics/12`,
  and the six `.28` records are `/11`. Every one of the 56 tracks with
  `block_crcs` gives its `eac_crc` back when its blocks are combined with
  zlib's `crc32_combine` at 176,400 bytes a block. 52 of them end on a block
  shorter than 75 frames, which the golden record cannot exercise. Tracks a
  rip did not read carry `null`, as built.
- **The handshake line**: every `.29` log reads `Handshake:      round 38 lap 3
  OPEN, verdict OPEN -- released build`, the newest lap `8d2ca72` carries.
- **Not reached**: B6's cover lines, since no log prints `Embedded cover
  art:`. 23 of the 25 logs pass `-G`, and the two de-emphasis rips, which run
  cyanrip directly, pass neither `-G` nor `-C`. And `Error ripping:
  Input/output error`, since no drive was lost.

### The two failed steps: CTDB outvotes track 5's read

- Both whole-disc rips end with track 5 at `E0036697`: the full rip's
  securing pass after 3 reads, replacing its first pass's `6902BCF0`, and the
  secure re-read after 3. Each matches AccurateRip on frame 450 only (`Accurip
  450: 4CCBCF89`, confidence 200), as the readings of earlier runs of this
  disc report track 5, from 2026-09-26 (`docs/rig-2026-09-26-221a1df/`) to
  2026-11-03 (`docs/rig-2026-11-03-3f288fb/`).
- `expect-ctdb whole` says CTDB matched the rip to 1 of 1,525 submissions,
  that 1,423 of them agree on another entry, and that track 5 differs from it
  in 3 samples at 02:24:59. Platterpus changed the step after 2026-11-03's run
  to fail a match its own database outvotes (`platterpus@eb550dd6`, their
  review item A3). That run passed it on the same figures: one submission
  matched, against 1,524 that disagree. So
  the failures are a stricter grade of the same read, not a new one, and
  AccurateRip, which Platterpus's step calls the authority, says frame 450
  only either way.
- Whether `E0036697` is this pressing's track 5 or a misread every run shares
  is not something this run can settle. The 3-sample difference is CTDB's
  report, and nothing here measured it.

### Track 3, and the two builds side by side

- In the four single-track rips per build (`-l 3`, no `-Z`), track 3 matched
  AccurateRip on frame 450 only every time. `.29` read `3D8FCF0C` all 4 times,
  and `.28` read 3 checksums in 4 rips (`3D8FCF0C` twice, `7684A601`,
  `E45FCE56`), Platterpus's `compare-accuracy` (L1836) says.
- Where re-reads ran, track 3 came out right: the securing pass and the secure
  re-read both converged on `59D352DD`, which AccurateRip verifies at
  confidence 128. The full rip's first pass had read `3D8FCF0C`.
- Timing, tracks 1 to 3 (`compare-timings`, L1705): `.29` over `.28` is 1.011
  and 1.008 in the two pairs, 244.38 s against 241.67 s and 244.48 s against
  242.58 s, which Platterpus's step calls in agreement within 0.05.

### Track 9's pregap

- Decided in 2 of 25 logs, at 95 frames, one per build (`derived wavpack` on
  `.29`, `timing A2` on `.28`), and undecided or unknown in the other 23. This
  is `subchannel-pregap-varies`, as filed before. `tools/read-run.py` reads
  `.29`'s undecided row only since `1245b218` (our round 38 lap 5 S4); before
  it, it would have called track 9 absent from 18 lists.

### Carried over

- **Cache**: `Cache probe:    128 to 255 sectors (294.0 to 585.7 KiB, uncached
  read 362.9 ms, cached read 1.2 ms, 3 re-reads after a 256-sector run took
  59.0 ms or more)`, on `.29`, beside `cd-paranoia -A: cache 140 sectors,
  defeated`. `docs/KNOWN-ISSUES.md`'s cache table has its row.
- **`-f`**: `Drive offset of +667 found (confidence: 14)!`, on `.29`, as on
  every run of this drive.
- **The build tag**: every `.29` log says `g8d2ca72`, seven characters,
  because Platterpus's installer now pins git's abbreviation at seven in its
  clone (`platterpus@7fdc33a1`). A full clone of ours builds `g8d2ca726`, which
  their installer refused at the owner's first install of 0.7.120. The fix
  that makes our build name seven characters itself is on our branch, not in
  `.29`.

## Questions, gaps and next time

**Questioned:**

- **Track 5's `E0036697` against CTDB's majority** (both whole-disc logs, track
  5 block). AccurateRip matches it on frame 450 only, and CTDB's majority
  differs in 3 samples. Settled only by another pressing of this disc, or a
  second drive. Owner: the operator.
- **Track 3's `3D8FCF0C`** (`accuracy B1` to `B4`, track 3 block), read 4 of 4
  times by `.29` and 2 of 4 by `.28` without `-Z`, and never by a rip whose
  re-reads ran. Whether a single read of track 3 on this drive lands on it
  because of the drive or the disc is not settled. Owner: ours, with the
  operator's drive.

**Possibly missing:**

- **No reading plan before the run** (`docs/ROUND-37-READING-PLAN.md` was
  round 37's). Owner: ours; the next run expected in advance gets one.
- **`Error ripping: Input/output error` after a lost drive**, and **B6's
  cover lines**, did not print, as nothing in the run could reach them.
  Owner: ours, `tests/rip_images.py` holds both on images.

**To add next time:**

- A rip with `-C` and no `-G` on a FLAC output, to show B6's lines on a drive.
  Owner: the operator's script, by Platterpus's word.

**More than we asked:**

- Platterpus's `expect-pregaps-agree` (L1875) reads `.29`'s undecided row as
  unknown, "the search narrowed it to two lengths", which is their lap 4 S4's
  fix working on a drive's logs.
