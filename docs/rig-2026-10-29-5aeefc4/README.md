# Rig session 2026-10-29 — build `5aeefc4`, Platterpus 0.7.115, **Full**, the reference disc

**Read the build, not the date.** This is `5aeefc4`, `+platterpus.27`,
through Platterpus **0.7.115** (`v0.7.115`, at `platterpus@de2420d6`). All
eleven `.log` files open with `cyanrip 0.9.4-rc3+platterpus.27
(platterpus-fork-g5aeefc4)`, and so does the securing pass's record. No other
build was installed. `tools/ingest-bundle.py --peer` reads both as the newest
release of each side when the run began, 04:17:08Z: `.27` by our release
ledger, and 0.7.115 by its tag, dated 01:17:45Z.

**It is a Full run on the pair our round 37 lap 1 names**, `.27` with
0.7.115. It is not round 37's closing run, which our lap 1 S10 sets on
`.28`. It is also not round 36's: that round closed on 2026-10-28 on the run
in `docs/rig-2026-10-28-5aeefc4/`.

**The script's verdict is a pass**: pass 440, fail 0, error 0, skipped 0,
blocked 0, unreachable 128, info 8, `ok: true`, `counts_as_evidence: true`, run
size full (`session/run/report.json`). Of the 128 unreachable steps:
- One is L573, `expect-offset-refusal`. This drive cannot reach it because
  it is in AccurateRip's drive list, as on every run on it.
- 127 are sections P5 and P6, the timed rip and the paired rips of track 3.
  They compare the approved build with the one under review. 0.7.115 names
  `5aeefc4` as both, so each section stops at its `skip-if-same-build` step
  (`session/transcript.txt:1977` and `:2085`). This run has no timing and no
  paired accuracy.

**Every member matches the sender's own hash**: all 108 members the bundle's
`MANIFEST.txt` hashes match it byte for byte.

**Filed under the names it was delivered with.** `tools/ingest-bundle.py
--into` filed 51 members and named 58 it did not file, each in `SHA256SUMS`.
**Nothing needed replacing.** The owner's name was not checked, because no
local list of names exists here, and not checked is not the same as not
present.

| | |
|---|---|
| bundle | `platterpusbundle20261029t041708z.tar.gz`, handed over by the operator on 2026-10-29 |
| sha256 | `b75221ff5d040258bead788aec2737572da71587da66ebff5fced3a2f4127875` |
| size | 7,911,451 bytes, 109 members, 108 of them hashed in its `MANIFEST.txt` |
| session | `20261029T041708Z`, `started_at` 04:17:08Z, ended 05:54Z at the earliest |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| disc | the reference disc, 14 tracks, `AccurateRip ID: 001d420f-013bb370-e20dfe0e` |

## What it shows

- **Track 9's pregap is never 94 on `.27`, again.**
  - The eleven `.log` files and the securing pass list `pregap of track 9
    unknown (sub-channel CRC mismatches)` in 11 and `95 frame pregap in
    track 9` in 1, `r16deemphoff`, which rips track 1 alone. `.25` and EAC
    read 94 (`docs/rig-2026-10-28-5aeefc4/`).
  - Track 9's `Pregap search:` line is in the two logs that rip track 9,
    the whole-disc rip and the `-Z 2` secure re-read. Both say the same: `114
    sectors asked; 201 reads failed the CRC; 1 sectors gave no frame passing
    it; 56 frames were another sector's; 0 had no address; frames answer +0
    sectors off; 200-retry pass ran; LSN 145567 to 145567 undecided`.
  - **The undecided sector is the same as on 2026-10-28: LSN 145567,** the
    sector between EAC's 94 and 95. This time one sector gave no frame
    passing its CRC; on 2026-10-28 none did, and 210 frames answered for
    another sector. So on this run the `unknown`'s words do not contradict
    its record. The search ended the same way, though, on the same sector,
    with a different count of each cause.
  - The other ten logs, the 95 among them, do not rip track 9 and carry no
    record for it. That is our round 36 lap 16 S10, which `14f9298` fixes
    for `.28` with a `Pregap searches:` block (our round 37 lap 1 S5).
- **The whole disc.**
  - The plain rip reads `Tracks ripped accurately: 13/14`, with track 5
    (`E0036697`) matched on frame 450 only, and `Ripping errors: 0`. Track 3
    read `59D352DD`, accurately ripped. Its securing pass, `-Z 2 -l 5`,
    converged after 3 reads on `E0036697`, frame 450 only.
  - The `-Z 2` rip: all 14 tracks converged after 3 reads, and `Tracks
    ripped accurately: 12/14`. Track 3 read `3D8FCF0C` and track 5
    `E0036697`, both matched on frame 450 only.
  - Track 3 read `59D352DD` in one whole-disc rip and `3D8FCF0C` in the
    other, both values it read on 2026-10-28 under both builds. Track 5 read
    `E0036697` in all three rips that read it.
  - No read reached the repeat limit, so `--prefer-accuraterip-match` had
    nothing to act on.
- **`Recordable:     no, CD-ROM (drive's current profile)`** in all eleven
  `.log` files, and **`Accurate stream: declared supported by drive
  (capabilities page, not measured)`** in all eleven. No two-search clause
  printed.
- **The disc ISRC read.** All 43 track blocks read a code, the same code for
  each track in every log that rips it, track 1 `GBAAM7800003`.
- **The cancel step exits 143**: `cancel me` reads `Rip completed:  no
  (interrupted by SIGTERM, 1 of 14 tracks)` and `Ripping errors: 1`, and its
  record has `exit_code` 143.
- **All 12 signed logs verify with `-Y`** and end in a signed footer: the 11
  `.log` files and the securing pass. All 12 ask for a `--diagnostics`
  record, the bundle has each, and every one is `cyanrip-diagnostics/10` with
  empty `error_positions`.
- **Each log's `Handshake:` line reads `round 36 lap 8 OPEN, verdict HOLD --
  released build`**, the state compiled into `.27` when it was built, and
  `Consumer: platterpus/0.7.115`.
- **`-f` found `+667` at confidence 14** (`session/transcript.txt:1196`).
- **The cache probe said `128 to 255 sectors`** (uncached read 362.7 ms,
  cached 1.2 ms, `session/transcript.txt:1266`), beside `cd-paranoia -A`'s
  140 (`session/transcript.txt:1457`).

**It shows `.27` on 0.7.115 as it was on 0.7.114**, with one new datum:
track 9's undecided sector is the same sector on two runs, whatever stopped
the search there. It shows no timing and no paired accuracy, because
0.7.115 approves and reviews the same build.

**Every fact above can be re-derived** with `tools/read-run.py
docs/rig-2026-10-29-5aeefc4 --cyanrip build/src/cyanrip`, beside
`tools/ingest-bundle.py`'s verdict on the bundle itself. The `--diagnostics`
records are in the bundle, whose `SHA256SUMS` names each.
