# Rig session 2026-10-26 — build `ca0f097`, Platterpus 0.7.113, **Full**, the reference disc

**Read the build, not the date.** This is `ca0f097`, `+platterpus.26`,
through Platterpus **0.7.113** (`v0.7.113`). Nineteen logs open with `cyanrip
0.9.4-rc3+platterpus.26 (platterpus-fork-gca0f097)`. Six are `.25` at
`5f1d036`, installed for two steps only: the timed rip's `timing A1` and
`timing A2`, and the paired rips' `accuracy A1` to `A4`.
`tools/ingest-bundle.py --peer` reads 0.7.113 as the newest tag when the run
began, 12:12:21Z, and the ripper as two builds, as these two steps run.

**It is not round 36's closing run.** The round closes on the Full run of the
reference disc on `.27` (our lap 10 S13). `.27` was published when pull request
#61 merged, at 12:58Z, 46 minutes after this run began. What this run does
carry is section P6, the paired rips of track 3 that our operator's word of
2026-10-26 added, and P5, the timed rip, both `.25` against `.26`.

**The script's verdict is a pass**: pass 553, fail 0, error 0, skipped 0,
blocked 0, unreachable 1, info 22, `ok: true`, `counts_as_evidence: true`, run
size full (`session/run/report.json`). The unreachable step is L573,
`expect-offset-refusal`, which this drive cannot reach because it is in
AccurateRip's drive list, as on every run on it.

**Every member matches the sender's own hash**: all 181 members the bundle's
`MANIFEST.txt` hashes match it byte for byte.

**Filed under the names it was delivered with.** `tools/ingest-bundle.py
--into` filed 101 members and named 81 it did not file, each in `SHA256SUMS`.
**Nothing needed replacing.** The owner's name was not checked, because no
local list of names exists here, and not checked is not the same as not
present.

| | |
|---|---|
| bundle | `platterpusbundle20261026t121221z.tar.gz`, handed over by the operator on 2026-10-26 |
| sha256 | `2f3bd79db49e6ec981e48f1bdca8461caa1e2c4ca4ab30d381bc8b8a0f2b4fc4` |
| size | 8,014,936 bytes, 182 members, 181 of them hashed in its `MANIFEST.txt` |
| session | `20261026T121221Z`, `started_at` 12:12:21Z, ended 14:15Z at the earliest |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| disc | the reference disc, 14 tracks, `AccurateRip ID: 001d420f-013bb370-e20dfe0e` |

## What it shows

- **P6: in eight rips, track 3's accuracy does not follow the build.**
  - The section rips track 3 alone, eight times in ABBA order, with `-Z` off
    and read speed 0 (L1723).
  - `.25` was verified by AccurateRip in 1 of 4 rips (`accuracy A4`,
    `59D352DD`), and matched on frame 450 only in the other 3. `.26` was
    verified in 0 of 4, frame 450 only in all 4
    (`session/transcript.txt:2525-2530`).
  - Seven distinct CRC32s in eight rips: only `2AC1F945` was read twice, once
    under each build.
  - One verified rip in eight cannot tell the builds apart. What the section
    does show is that the drive reads track 3 differently nearly every time,
    under either build.
- **P5: `.26` read tracks 1 to 3 in under a fifth of `.25`'s time.**
  - Platterpus's L1658 gives `B1/A1 = 0.189` (109.34 s against 577.86 s) and
    `B2/A2 = 0.191` (110.53 s against 577.53 s), agreeing within 0.002
    (`session/transcript.txt:2194-2197`).
  - All four rips verify tracks 1 and 2 whole and match track 3 on frame 450
    only.
- **The repeat limit's `last read` clause printed on a drive for the first
  time.**
  - In the whole-disc rip's securing pass, track 3 reads `Done; (repeat limit
    of 5 reads reached; at most 2 reads agreed; last read 3B2FA27B, not
    kept)`. The kept read is `2AC1F945`, read twice in the four before.
  - The other three repeat-limit cases kept the last read, so the clause
    rightly did not print.
- **Track 5: `-Z 2` agreed on a read AccurateRip does not match; the repeat
  limit kept one it does.**
  - The `-Z 2` whole-disc rip converged on `E0036697` after 5 reads, which
    AccurateRip matches on frame 450 only.
  - The plain whole-disc rip's securing pass read `E0036697`, `E0036697`,
    `C96464AB` and `4065BECC`, then a fifth read whose checksum the log does
    not print. It kept `C96464AB`, which is accurately ripped (v1 confidence
    129, v2 confidence 200), and printed no `last read` clause. Under the
    spool's rule, the read most reads agreed on and the newest on a tie, that
    means the fifth read was `C96464AB` too, tying `E0036697` at two.
  - These are the two checksums of 2026-10-06, which `--prefer-accuraterip-match`
    in `.27` was built for. That option acts only at the repeat limit, so it
    would not have changed the converged `-Z 2` result.
- **The whole disc.**
  - The plain rip reads `Tracks ripped accurately: 12/14`, with tracks 3 and
    5 matched on frame 450 only, and `Ripping errors: 0`.
  - The `-Z 2` rip: 11 tracks converged after 3 reads, 2 after 5, and track 3
    did not converge, with 4 distinct checksums in the 4 reads before the last.
- **The disc ISRC read on `.26` again.** All 53 `.26` track blocks read a
  code, the same code for each track in every log that rips it, track 1
  `GBAAM7800003`. All 10 `.25` track blocks read `none`.
- **The three lines.**
  - `Accurate stream: declared supported by drive (capabilities page, not
    measured)` in every `.26` log.
  - `Recordable: unknown (profile 0xffff is not a CD profile)` in all 19 `.26`
    logs: the defect `.27` fixes, not in this build.
  - No two-search clause printed.
- **Track 9's pregap is never 94 on `.26`, as on 2026-10-21.**
  - 14 `.26` logs list 95. The other 5 list no pregap for track 9 and name
    `sub-channel CRC mismatches`: `accuracy B1`, `B2`, `timing B1`, `B2`, and
    the second whole-disc folder.
  - The `.25` logs list 94 in 5 and 95 in 1 (`accuracy A2`). EAC's log of
    this disc has 94 (our lap 8 S5).
- **The cancel step exits 143**: `cancel me` reads `Rip completed:  no
  (interrupted by SIGTERM, 2 of 14 tracks)` and `Ripping errors: 1`, and its
  record has `exit_code` 143.
- **All 25 cyanrip logs verify with `-Y`** and end in a signed footer: the 23
  logs and the 2 securing passes. All 25 ask for a `--diagnostics` record, the
  bundle has each, and every one is `cyanrip-diagnostics/10` with empty
  `error_positions`.
- **`-f` found `+667` at confidence 14** (`session/transcript.txt:1196`).
- **The cache probe said `128 to 255 sectors`** (uncached read 237.3 ms,
  cached 2.0 ms, `session/transcript.txt:1266`), beside `cd-paranoia -A`'s
  137 (`session/transcript.txt:1484`).

**It answers P6's question for eight rips, and no more:** under either build,
track 3 reads differently nearly every time. It shows `.26`'s speed again, and
for the first time on a drive the repeat limit naming a last read it did not
keep. On track 5, two agreeing reads were the wrong ones.

**Every fact above can be re-derived** with `tools/read-run.py
docs/rig-2026-10-26-ca0f097 --cyanrip build/src/cyanrip`, beside
`tools/ingest-bundle.py`'s verdict on the bundle itself. The `--diagnostics`
records are in the bundle, whose `SHA256SUMS` names each.
