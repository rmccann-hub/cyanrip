# Rig session 2026-10-28 — build `5aeefc4`, Platterpus 0.7.114, **Full**, the reference disc

**Read the build, not the date.** This is `5aeefc4`, `+platterpus.27`,
through Platterpus **0.7.114** (`v0.7.114`, at `platterpus@95691b5b`).
Seventeen `.log` files open with `cyanrip 0.9.4-rc3+platterpus.27
(platterpus-fork-g5aeefc4)`, and so do the securing pass's record and the five
logs of Platterpus's verified-read chase. Six `.log` files are `.25` at
`5f1d036`, installed for two steps only: the timed rip's `timing A1` and
`timing A2`, and the paired rips' `accuracy A1` to `A4`.
`tools/ingest-bundle.py --peer` reads 0.7.114 as the newest tag when the run
began, 03:07:46Z (the tag's date is 03:00:00Z), and the ripper as two builds,
as these two steps run.

**It is round 36's closing run**: the Full run of the reference disc on `.27`
through Platterpus's first release naming it, with the paired rips of track 3,
`.25` against `.27` (our lap 14 S14, their lap 15 S13).

**The script's verdict is a pass**: pass 553, fail 0, error 0, skipped 0,
blocked 0, unreachable 1, info 22, `ok: true`, `counts_as_evidence: true`, run
size full (`session/run/report.json`). The unreachable step is L573,
`expect-offset-refusal`, which this drive cannot reach because it is in
AccurateRip's drive list, as on every run on it.

**Every member matches the sender's own hash**: all 178 members the bundle's
`MANIFEST.txt` hashes match it byte for byte.

**Filed under the names it was delivered with.** `tools/ingest-bundle.py
--into` filed 99 members and named 80 it did not file, each in `SHA256SUMS`.
**Nothing needed replacing.** The owner's name was not checked, because no
local list of names exists here, and not checked is not the same as not
present.

| | |
|---|---|
| bundle | `platterpusbundle20261028t030745z.tar.gz`, handed over by the operator on 2026-10-28 |
| sha256 | `e056a8f52ef1d6b4cf122fe9c9e84ec6e021a60951d03f8065925664f732fa4e` |
| size | 8,697,962 bytes, 179 members, 178 of them hashed in its `MANIFEST.txt` |
| session | `20261028T030745Z`, `started_at` 03:07:46Z, ended 06:01Z at the earliest |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| disc | the reference disc, 14 tracks, `AccurateRip ID: 001d420f-013bb370-e20dfe0e` |

## What it shows

- **`Recordable:` answers for a pressed disc.** All 23 `.27` logs read
  `Recordable:     no, CD-ROM (drive's current profile)`: the 17 `.log`
  files, the securing pass and the five chase logs. `.26` read `unknown
  (profile 0xffff is not a CD profile)` in every log of its four runs and of
  2026-10-26's. `.25` predates the line.
- **Track 9's pregap is never 94 on `.27`, and where track 9 is ripped the
  log says why.**
  - The 23 `.27` logs list `pregap of track 9 unknown (sub-channel CRC
    mismatches)` in 21 and `95 frame pregap in track 9` in 2, `derived mp3`
    and `permutations`. The six `.25` logs list 94, as EAC's log of this disc
    does (our round 36 lap 8 S5).
  - Track 9's `Pregap search:` line is in the two `.27` logs that rip track
    9, the whole-disc rip and the `-Z 2` secure re-read: `267 sectors asked;
    131 reads failed the CRC; 0 sectors gave no frame passing it; 210 frames
    were another sector's; 0 had no address; frames answer +0 sectors off;
    200-retry pass ran; LSN 145567 to 145567 undecided` (the re-read's says
    130 reads failed the CRC). Track 9 starts at LSN 145662.
  - So the search placed sector 145566 in track 8 and sector 145568 in track
    9's pregap, and left one sector undecided. That is the sector between
    EAC's 94 and 95. Every sector it asked for gave a frame that passed its
    CRC, and 210 frames answered for another sector than the one asked.
  - The `unknown`'s own words, `sub-channel CRC mismatches`, name a cause
    the record beside them contradicts: no sector failed to give a frame
    passing its CRC. Our `KNOWN-ISSUES.md` said the arm is reached whenever
    the bounds fail to meet, and `tests/subq.c` reproduces it with no CRC
    failure at all.
  - None of the 21 other `.27` logs, the 2 at 95 among them, rips track 9,
    and the line is printed only in a ripped track's block, so none of them
    says why its track 9 answer is what it is.
- **P6: track 3's accuracy does not follow the build.**
  - The section rips track 3 alone, eight times in ABBA order, with `-Z` off
    and read speed 0 (L1723).
  - `.25` was verified by AccurateRip in 2 of 4 (`accuracy A1` and `A3`,
    `59D352DD`), and matched on frame 450 only in 2 (`4C88B732`,
    `3D8FCF0C`). `.27` was verified in 0 of 4, frame 450 only in all 4
    (`E45FCE56` twice, `3D8FCF0C`, `FAB39275`)
    (`session/transcript.txt:2518-2523`).
  - P5's four timed rips cover track 3 too, and go the other way: `.25`
    read `3D8FCF0C` and `E45FCE56`, `.27` read `59D352DD` twice. Over all
    twelve rips, each build was right in 2 of 6, and `59D352DD`, `3D8FCF0C`
    and `E45FCE56` were each read under both builds.
  - `.25` read track 3 at 0.96x and `.27` at 2.9x to 3.0x, and each build
    read `59D352DD` at its own speed.
- **P5: `.27` read tracks 1 to 3 in about a third of `.25`'s time.**
  - Platterpus's L1658 gives `B1/A1 = 0.341` (242.06 s against 709.27 s) and
    `B2/A2 = 0.341` (241.65 s against 709.26 s)
    (`session/transcript.txt:2187-2189`).
  - Both builds read slower than on 2026-10-26: `timing B1`'s three tracks at
    2.6x, 2.7x and 2.9x against `.26`'s 6.3x, 5.8x and 6.1x, and `timing A1`'s
    at 0.90x, 0.94x and 0.96x against 1.1x, 1.2x and 1.2x
    (`docs/rig-2026-10-26-ca0f097/`). The diff from `ca0f097` to `5aeefc4`
    touches no sector read, speed or media-change call, and this run does
    not show why the drive read slower.
- **The whole disc.**
  - The plain rip reads `Tracks ripped accurately: 12/14`, with tracks 3
    (`6D3F43B0`) and 5 (`0B2B0A62`) matched on frame 450 only, and `Ripping
    errors: 0`. Its securing pass (`-Z 2 -l 3,5`) converged on each after 3
    reads: track 3 on `59D352DD`, accurately ripped, and track 5 on
    `E0036697`, frame 450 only.
  - Platterpus's verified-read chase then ripped track 5 five times, and read
    `E0036697` all five times.
  - The `-Z 2` rip: 13 tracks converged after 3 reads and track 5 after 4,
    on `E0036697`; `Tracks ripped accurately: 13/14`. All 14 checksums are
    the ones Platterpus's sheet gives from the baseline that matched EAC
    (`platterpus@95691b5b:docs/hardware-test-checklist.md:92-100`).
  - No read reached the repeat limit, so `--prefer-accuraterip-match`, which
    acts only there, had nothing to act on.
- **The disc ISRC read.** All 59 `.27` track blocks read a code, the same
  code for each track in every log that rips it, track 1 `GBAAM7800003`. All
  10 `.25` track blocks read `none (libcdio returned none)`.
- **`Accurate stream: declared supported by drive (capabilities page, not
  measured)`** in every `.27` log. No two-search clause printed.
- **The cancel step exits 143**: `cancel me` reads `Rip completed:  no
  (interrupted by SIGTERM, 1 of 14 tracks)` and `Ripping errors: 1`, and its
  record has `exit_code` 143.
- **All 24 signed logs verify with `-Y`** and end in a signed footer: the 23
  `.log` files and the securing pass. All 24 ask for a `--diagnostics`
  record, the bundle has each, and every one is `cyanrip-diagnostics/10` with
  empty `error_positions`.
- **`-f` found `+667` at confidence 14** (`session/transcript.txt:1206`).
- **The cache probe said `128 to 255 sectors`** (uncached read 362.8 ms,
  cached 1.3 ms, `session/transcript.txt:1276`), beside `cd-paranoia -A`'s
  140 (`session/transcript.txt:1467`).

**It shows `Recordable:` fixed, and why track 9 is not 94 where track 9 is
ripped: one sector, 145567, whose own frame the drive never returned.** It
does not show that for the 21 logs that list track 9 without ripping it, nor
where the two 95s came from. Track 3's twelve rips do not tell the builds
apart.

**Every fact above can be re-derived** with `tools/read-run.py
docs/rig-2026-10-28-5aeefc4 --cyanrip build/src/cyanrip`, beside
`tools/ingest-bundle.py`'s verdict on the bundle itself. The `--diagnostics`
records are in the bundle, whose `SHA256SUMS` names each.
