# Rig session 2026-09-30b — build `174a134`, Platterpus 0.6.65, **Full**

**Read the build, not the date.** This is `174a134`, `+platterpus.19`, through
Platterpus **0.6.65** (`0981c69`). The other filing dated 2026-09-30,
`docs/rig-2026-09-30-174a134/`, is the Full run that 0.6.64 stopped at section A
and a `.18` rip stopped by closing the console; neither ripped `.19`. All ten
cyanrip logs here open with `cyanrip 0.9.4-rc2+platterpus.19
(platterpus-fork-g174a134)`.

**This is round 30's real test, the run its lap 1 S10 names**: the operator's
Full acceptance with `.19` installed through Platterpus's app, from 0.6.65, the
release whose `PIN_UNDER_REVIEW` is `174a134`
(`platterpus@0981c69:src/platterpus/deps/fork_source.py:695`). S10 asks for the
bundle to be committed to both repositories, and this directory is ours.

**The script's own verdict is not a pass**: pass 316, **fail 7**, error 0,
skipped 0, blocked 0, unreachable 0, info 1, `ok: false`, with
`counts_as_evidence: true`, run size full, and no `ended_reason`
(`session/script-report.json`). **All seven failures are `screenshot` steps**,
L585, L676, L724, L749, L815, L850 and L988, each reporting *"examined 9
window(s) and none was on screen, so there was nothing to photograph"*
(`session/transcript.txt:391`, the first). Round 29's run had three of the same;
0.6.65 held the screen awake for this one (their round 30 lap 2 S15), so a
blanked screen was not the cause. None of the seven is a cyanrip step; what they
mean is Platterpus's to say.

## Provenance

| | |
|---|---|
| bundle | `platterpusbundle20260930t030705z.tar.gz`, handed over by the operator |
| sha256 | `fa1a533363b330711c14129de58b49b042b655f4ca93d085a810d1d316a047ac` |
| size | 4,302,318 bytes, 66 files, 12 of them screenshots |
| session stamp | `20260930T030705Z`, `started_at` 03:07:05Z (`session/script-report.json`). The last rip, the `-H -W` rip of section P3, finished at 04:27:43 host time, 08:27:43Z (`rips/r16deemphoff.log`, host time UTC−4) |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667 |
| disc | DiscID `pNtImOkdBm9RMBIalzx0w9cfsYY-`, 14 tracks, the disc of every filed session |
| ripper | `cyanrip 0.9.4-rc2+platterpus.19 (platterpus-fork-g174a134)` |
| consumer | `platterpus/0.6.65`, build `0981c69` (`session/COMPONENTS.json`), which is where `git ls-remote --tags` puts their `v0.6.65` |
| script | the full acceptance script, run size **full** |

**Every file here but this README is byte-identical to a member of that
tarball**, 41 of 41, each hashed against its original when it
was copied. As in earlier filings, `-2` is section H's overwrite re-rip, the
name without it is section F's whole-disc rip, and the two `-H` rips of section
P3 are delivered as `Unknown disc (PNTI).log`, so their directories name them:
`r16deemphon` for `-H -E` and `r16deemphoff` for `-H -W`.

| filed here | as delivered in their bundle | sha256/16 |
|---|---|---|
| `after-cancel.eac.log` | `album/after cancel 20260930t030705 platterpus-fork-g174a134/after cancel 20260930t030705 platterpus-fork-g174a134 (EAC-compatible).log` | `0abd06154235680f…` |
| `after-cancel.cue` | `album/after cancel 20260930t030705 platterpus-fork-g174a134/after cancel 20260930t030705 platterpus-fork-g174a134.cue` | `48bebc394f88ac40…` |
| `after-cancel.log` | `album/after cancel 20260930t030705 platterpus-fork-g174a134/after cancel 20260930t030705 platterpus-fork-g174a134.log` | `bf47c758395d1982…` |
| `cancel-me.eac.log` | `album/cancel me 20260930t030705 platterpus-fork-g174a134/cancel me 20260930t030705 platterpus-fork-g174a134 (EAC-compatible).log` | `52b58ca739a18556…` |
| `cancel-me.cue` | `album/cancel me 20260930t030705 platterpus-fork-g174a134/cancel me 20260930t030705 platterpus-fork-g174a134.cue` | `65958adc48a97be3…` |
| `cancel-me.log` | `album/cancel me 20260930t030705 platterpus-fork-g174a134/cancel me 20260930t030705 platterpus-fork-g174a134.log` | `4beb47c1344592f7…` |
| `derived-mp3.eac.log` | `album/derived mp3 20260930t030705 platterpus-fork-g174a134/derived mp3 20260930t030705 platterpus-fork-g174a134 (EAC-compatible).log` | `13814d0b9ea30511…` |
| `derived-mp3.cue` | `album/derived mp3 20260930t030705 platterpus-fork-g174a134/derived mp3 20260930t030705 platterpus-fork-g174a134.cue` | `843489068553dbab…` |
| `derived-mp3.log` | `album/derived mp3 20260930t030705 platterpus-fork-g174a134/derived mp3 20260930t030705 platterpus-fork-g174a134.log` | `231452c304f1ea63…` |
| `derived-wav.eac.log` | `album/derived wav 20260930t030705 platterpus-fork-g174a134/derived wav 20260930t030705 platterpus-fork-g174a134 (EAC-compatible).log` | `d781a0714022f3be…` |
| `derived-wav.cue` | `album/derived wav 20260930t030705 platterpus-fork-g174a134/derived wav 20260930t030705 platterpus-fork-g174a134.cue` | `998f40eb1559309a…` |
| `derived-wav.log` | `album/derived wav 20260930t030705 platterpus-fork-g174a134/derived wav 20260930t030705 platterpus-fork-g174a134.log` | `b44182ea65e27226…` |
| `derived-wavpack.eac.log` | `album/derived wavpack 20260930t030705 platterpus-fork-g174a134/derived wavpack 20260930t030705 platterpus-fork-g174a134 (EAC-compatible).log` | `8c5115a128c3dfc5…` |
| `derived-wavpack.cue` | `album/derived wavpack 20260930t030705 platterpus-fork-g174a134/derived wavpack 20260930t030705 platterpus-fork-g174a134.cue` | `a1f6b4180466c5e7…` |
| `derived-wavpack.log` | `album/derived wavpack 20260930t030705 platterpus-fork-g174a134/derived wavpack 20260930t030705 platterpus-fork-g174a134.log` | `e19498d3032c3c99…` |
| `full-acceptance-angle-bracket.eac.log` | `album/full acceptance_ angle_bracket 20260930t03__terpus-fork-g174a134/full acceptance∶ angle‹bracket 20260930t030705 platterpus-fork-g174a134 (EAC-compatible).log` | `7f80367cb7304dea…` |
| `full-acceptance-angle-bracket.cue` | `album/full acceptance_ angle_bracket 20260930t03__terpus-fork-g174a134/full acceptance∶ angle‹bracket 20260930t030705 platterpus-fork-g174a134.cue` | `c096619612930afb…` |
| `full-acceptance-angle-bracket.log` | `album/full acceptance_ angle_bracket 20260930t03__terpus-fork-g174a134/full acceptance∶ angle‹bracket 20260930t030705 platterpus-fork-g174a134.log` | `2fe217bc7acfc85b…` |
| `full-acceptance-angle-bracket.platterpus-addendum.txt` | `album/full acceptance_ angle_bracket 20260930t03__terpus-fork-g174a134/full acceptance∶ angle‹bracket 20260930t030705 platterpus-fork-g174a134.platterpus-addendum.txt` | `495e7458c52ce40a…` |
| `full-acceptance-angle-bracket-2.eac.log` | `album/full acceptance_ angle_bracket 20260930t03__us-fork-g174a134 _2_/full acceptance∶ angle‹bracket 20260930t030705 platterpus-fork-g174a134 (EAC-compatible).log` | `6f722fb63b53d96c…` |
| `full-acceptance-angle-bracket-2.cue` | `album/full acceptance_ angle_bracket 20260930t03__us-fork-g174a134 _2_/full acceptance∶ angle‹bracket 20260930t030705 platterpus-fork-g174a134.cue` | `00da832a96fa65e8…` |
| `full-acceptance-angle-bracket-2.log` | `album/full acceptance_ angle_bracket 20260930t03__us-fork-g174a134 _2_/full acceptance∶ angle‹bracket 20260930t030705 platterpus-fork-g174a134.log` | `8d84bb1cd1055a00…` |
| `r16deemphoff.cue` | `album/r16deemphoff/Unknown disc (PNTI).cue` | `f3c0672791431738…` |
| `r16deemphoff.log` | `album/r16deemphoff/Unknown disc (PNTI).log` | `157bd97b3789050f…` |
| `r16deemphon.cue` | `album/r16deemphon/Unknown disc (PNTI).cue` | `f3c0672791431738…` |
| `r16deemphon.log` | `album/r16deemphon/Unknown disc (PNTI).log` | `c7f58e5db94f4f8b…` |
| `secure-reread.eac.log` | `album/secure reread 20260930t030705 platterpus-fork-g174a134/secure reread 20260930t030705 platterpus-fork-g174a134 (EAC-compatible).log` | `bcfa2ec233c5193a…` |
| `secure-reread.cue` | `album/secure reread 20260930t030705 platterpus-fork-g174a134/secure reread 20260930t030705 platterpus-fork-g174a134.cue` | `01549da5c14f9cba…` |
| `secure-reread.log` | `album/secure reread 20260930t030705 platterpus-fork-g174a134/secure reread 20260930t030705 platterpus-fork-g174a134.log` | `522d65d31624ea35…` |
| `session/COMPONENTS.json` | `COMPONENTS.json` | `2fce7043d44c4395…` |
| `session/DIAGNOSTICS.txt` | `DIAGNOSTICS.txt` | `4e9e065e7273ca37…` |
| `session/MANIFEST.txt` | `MANIFEST.txt` | `e6ee70ed7e12f9f8…` |
| `session/SETTINGS.json` | `SETTINGS.json` | `905abbf1ff697864…` |
| `session/SOURCES.txt` | `SOURCES.txt` | `048a92b6c26bd668…` |
| `session/config.toml` | `session/artifacts/06platterpus/config.toml` | `8d816eea558fa8c8…` |
| `session/script-report.json` | `session/run/report.json` | `976ef07181451632…` |
| `session/transcript.txt` | `session/transcript.txt` | `2d71dc74f4992008…` |
| `session/rig-check-manifest.txt` | `session/run/rig-check/MANIFEST.txt` | `e7a665a89427b8d6…` |
| `session/rig-check-argv-probe-output.txt` | `session/run/rig-check/argv-probe-output.txt` | `053dae5fd738e837…` |
| `session/rig-check-argv-probe.json` | `session/run/rig-check/argv-probe.json` | `0465a0f4c3252507…` |
| `session/rig-check-ripper-version.txt` | `session/run/rig-check/ripper-version.txt` | `3dd6fb1ac56dbfad…` |

**Not filed**, with sha256/16 so each stays verifiable: the 12
screenshots; the 4 app logs (`session/artifacts/02platterpus/log.txt` (6,775,132 bytes, `b02ef5d72fe2246e`), `session/zz-applog-rotations/05platterpus/log.txt.3` (8,388,586 bytes, `a3c66d5014a89d1e`), `session/zz-applog-rotations/03platterpus/log.txt.1` (8,388,508 bytes, `42b8aa3d6907ffd5`), `session/zz-applog-rotations/04platterpus/log.txt.2` (8,388,516 bytes, `93995681743b4f4c`));
`session/run/transcript.txt`, byte-identical to the `session/transcript.txt`
filed here; and the 8 `.platterpus.json` reports, Platterpus's
artifact: `1d958896ce31d330` secure reread, `dccb3dcffe693716` full acceptance anglebracket, `7ef630e4ab558491` full acceptance anglebracket, `a01c527ea2e3fc6c` after cancel, `b03b6adf3d2d8410` derived wav, `61ccc1c00d83ff0f` derived mp3, `cbbd08dfc4b403e6` derived wavpack, `f09037303ba5aa2d` cancel me. No
claim below depends on any of them.

## Our reading: every cyanrip log in the bundle

**All ten verify against their own checksum** with `cyanrip -Y`, and each footer
is consistent with its `Invoked as:` line: nine completed with `Ripping errors:
0` and `Read stalls:    none (no read exceeded 10s)`, and `cancel-me` was
interrupted mid-read by SIGTERM, as section I intends (`Rip completed:  no
(interrupted by SIGTERM, 0 of 14 tracks)`, `Interrupted at: track 1, mid-read`,
`Partial files:  1 track (1)`). Every log's `Handshake:` line reads `round 29
lap 3 closed, verdict GO -- released build`, the record `.19` was built from.

**Nothing here shows a defect in `.19`.**

### `.19`'s changes, on a drive for the first time

- **The repeat loop's checksum is the track's EAC CRC32, on all fourteen
  tracks of section N.** In `rips/secure-reread.log`, every track's `Done; (2
  out of 2 matches for current checksum X)` names the same eight digits as its
  `EAC CRC32:` line. On `.18`, all fourteen differed, each being the value
  before its final XOR (`docs/rig-2026-09-28c-51cc789/rips/secure-reread.log:62`
  against `:100`).
- **Every tag key is in capitals**, in every `Metadata:` block of the nine logs
  that have one (`cancel-me` stopped before any track finished, so it has none),
  and the seven of those Platterpus made, each passing `-c 1/1`, carry
  `DISCTOTAL` beside `TOTALDISCS`. The two section P3 rips pass no `-c` and
  carry neither, as they should.
- **Not exercised, as round 30 lap 3 S17 said**: the reworded repeat-limit line
  prints only when a track reaches the limit, and none did (13 converged after
  3 reads and track 5 after 5); and the `-Z`/`-r` refusal, which Platterpus's
  validator refuses before cyanrip starts.

### What else the logs show

- **AccurateRip**: the two whole-disc rips have `Tracks ripped accurately:
  12/14`, and the two not found are **tracks 3 and 5**, as on every run of this
  disc. Their checksums differ between the two rips: EAC CRC32 track 3
  `FB789B52` in F and `3D8FCF0C` in N, track 5 `E0036697` and `6902BCF0`; and
  AccurateRip v1 track 3 `3D9B0781` and `1B28C061`, track 5 `F5426D5F` and
  `7CE3F6E7`. **Corrected 2026-10-05**: this quoted only the v1 values, as
  *"checksums"*, beside a count of EAC CRC32s. And across every filed rip
  `tools/cross-rip.py docs/rig-*` counts **19 distinct EAC CRC32s for track 3 in
  42 reads** and 3 for track 5 in 37: the disc does not read the same twice
  there. Platterpus's addendum re-read both in section F: track 3 replaced to
  `59D352DD`, AccurateRip-accurate at confidence 128, the value `.18`'s section
  N converged on; track 5 replaced to `6902BCF0`, matching only the one-frame 450
  checksum. Every two-track rip is 2 of 2.
- **Section P, the cache probe**: `-x -I` exited 0 in 16.4 s with `at least 2048
  sectors, upper bound unknown (4704.0 KiB or more, search ceiling reached,
  uncached read 363.0 ms, cached read 82.0 ms)` (`session/transcript.txt:958`),
  the sixteenth session to say so, against `cd-paranoia -A`'s 137 to 140. The
  row is in `docs/KNOWN-ISSUES.md`'s table. **Do not cite the figure.**
- **Section P2**: `cyanrip -N -l 1` refused for want of an offset, exit 1 in
  4.9 s, `Offset is unset! To continue with an offset of 0, run with -s 0!`
  (`session/transcript.txt:1207`). No hang.
- **Section P3**: the `-H -E` and `-H -W` rips each ran 221.2 s and exited 0.
  They settle nothing about de-emphasis, since every figure the log reports is
  taken before the filter graph (`docs/KNOWN-ISSUES.md`).
