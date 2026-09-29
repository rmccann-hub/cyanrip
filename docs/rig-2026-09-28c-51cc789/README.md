# Rig session 2026-09-28c — build `51cc789`, Platterpus 0.6.63, **Full**

**Read the build, not the date.** This is `51cc789`, `+platterpus.18`, through
Platterpus **0.6.63** (`d226c03`). It is the third filed session dated
2026-09-28; the other two, `docs/rig-2026-09-28-e0471f4/` and
`docs/rig-2026-09-28b-e0471f4/`, are `.17`. All ten cyanrip logs open with
`cyanrip 0.9.4-rc2+platterpus.18 (platterpus-fork-g51cc789)`, and the
transcript names that build 54 times. The seven `ge0471f4` in it are
Platterpus's notes that `.18` is not the build 0.6.63 was verified against
(`session/transcript.txt:432`, the first): their `FORK_PIN` is still round
28's.

**This is round 29's real test, the run its lap 1 S6 names**: the operator's
Full acceptance on the rig with `.18` installed through Platterpus's app, from
0.6.63, the release whose `PIN_UNDER_REVIEW` is `51cc789`
(`platterpus@d226c03:src/platterpus/deps/fork_source.py:662`; `FORK_PIN` is
`e0471f4` at line 219). S6 also asks for
the bundle to be committed to both repositories, and this directory is ours.

**The script's own verdict is not a pass**: pass 320, **fail 3**, error 0,
skipped 0, blocked 0, unreachable 0, info 1, `ok: false`, with
`counts_as_evidence: true`, run size full, and no `ended_reason`
(`session/script-report.json`). All three failures are `screenshot` steps:
L676 `afteroverwrite`, L724 `aftercancel` and L850 `afterwav`. Each reports
*"examined 12 window(s) and none was on screen, so there was nothing to
photograph"*: of the twelve it lists, nine read `exposed=False` and three
`exposed=n/a`, never shown (`session/transcript.txt:473`, `:531`, `:765`). The other eight screenshot
steps passed. None of the three is a cyanrip step; what they mean for the run
is Platterpus's to say.

## Provenance

| | |
|---|---|
| bundle | `platterpusbundle20260928t223356z.tar.gz`, handed over by the operator |
| sha256 | `43a837415e51157b4a8464d2601c6b38453a52eddf818684c275acb21a4237a6` |
| size | 4,293,783 bytes, 72 files, 20 of them screenshots |
| session stamp | `20260928T223356Z`, `started_at` 22:33:56Z (`session/script-report.json`). The last rip, the `-H -W` rip of section P3, finished at 23:55:23 host time, 03:55:23Z on 2026-09-29 (`rips/r16deemphoff.log`, host time UTC−4) |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667 |
| disc | DiscID `pNtImOkdBm9RMBIalzx0w9cfsYY-`, 14 tracks, the disc of every filed session (`tools/cross-rip.py docs/rig-*` finds this one disc across 125 logs, this session's included) |
| ripper | `cyanrip 0.9.4-rc2+platterpus.18 (platterpus-fork-g51cc789)` |
| consumer | `platterpus/0.6.63`, build `d226c03` (`session/COMPONENTS.json`), which is where `git ls-remote --tags` puts their `v0.6.63` |
| script | the full acceptance script, run size **full** |

**Every file here but this README is byte-identical to a member of that
tarball**, 41 of 41, each hashed against its original when it was copied. The
table below maps each one back to its delivered name. This is the first
bundle to carry the two `-H` rips of section P3 as logs; both are delivered as
`Unknown disc (PNTI).log`, so their directories name them here, `r16deemphon`
for `-H -E` and `r16deemphoff` for `-H -W`. As in earlier filings, `-2` is
section H's overwrite re-rip (`-l 1,2`), and the name without it is section F's
whole-disc rip.

| filed here | as delivered in their bundle | sha256/16 |
|---|---|---|
| `after-cancel.cue` | `album/after cancel 20260928t223356 platterpus-fork-g51cc789/after cancel 20260928t223356 platterpus-fork-g51cc789.cue` | `5ddf7bd0cc86f311…` |
| `after-cancel.eac.log` | `album/after cancel 20260928t223356 platterpus-fork-g51cc789/after cancel 20260928t223356 platterpus-fork-g51cc789 (EAC-compatible).log` | `78c50cb9a0833540…` |
| `after-cancel.log` | `album/after cancel 20260928t223356 platterpus-fork-g51cc789/after cancel 20260928t223356 platterpus-fork-g51cc789.log` | `1b3880c82b6d63aa…` |
| `cancel-me.cue` | `album/cancel me 20260928t223356 platterpus-fork-g51cc789/cancel me 20260928t223356 platterpus-fork-g51cc789.cue` | `07127be3448bde57…` |
| `cancel-me.eac.log` | `album/cancel me 20260928t223356 platterpus-fork-g51cc789/cancel me 20260928t223356 platterpus-fork-g51cc789 (EAC-compatible).log` | `6c3c03f4f65222de…` |
| `cancel-me.log` | `album/cancel me 20260928t223356 platterpus-fork-g51cc789/cancel me 20260928t223356 platterpus-fork-g51cc789.log` | `f195866993ad102b…` |
| `derived-mp3.cue` | `album/derived mp3 20260928t223356 platterpus-fork-g51cc789/derived mp3 20260928t223356 platterpus-fork-g51cc789.cue` | `2e8cdf7958eff76e…` |
| `derived-mp3.eac.log` | `album/derived mp3 20260928t223356 platterpus-fork-g51cc789/derived mp3 20260928t223356 platterpus-fork-g51cc789 (EAC-compatible).log` | `f9bb204a79ed34f0…` |
| `derived-mp3.log` | `album/derived mp3 20260928t223356 platterpus-fork-g51cc789/derived mp3 20260928t223356 platterpus-fork-g51cc789.log` | `5b2c7c2ce371c883…` |
| `derived-wav.cue` | `album/derived wav 20260928t223356 platterpus-fork-g51cc789/derived wav 20260928t223356 platterpus-fork-g51cc789.cue` | `0bdb1fe1441604bb…` |
| `derived-wav.eac.log` | `album/derived wav 20260928t223356 platterpus-fork-g51cc789/derived wav 20260928t223356 platterpus-fork-g51cc789 (EAC-compatible).log` | `2de2279d3f0ea142…` |
| `derived-wav.log` | `album/derived wav 20260928t223356 platterpus-fork-g51cc789/derived wav 20260928t223356 platterpus-fork-g51cc789.log` | `7f855583dee17743…` |
| `derived-wavpack.cue` | `album/derived wavpack 20260928t223356 platterpus-fork-g51cc789/derived wavpack 20260928t223356 platterpus-fork-g51cc789.cue` | `a45f1fe88f3d42f3…` |
| `derived-wavpack.eac.log` | `album/derived wavpack 20260928t223356 platterpus-fork-g51cc789/derived wavpack 20260928t223356 platterpus-fork-g51cc789 (EAC-compatible).log` | `6a4e35cf4894bae1…` |
| `derived-wavpack.log` | `album/derived wavpack 20260928t223356 platterpus-fork-g51cc789/derived wavpack 20260928t223356 platterpus-fork-g51cc789.log` | `9b0d5c75acd05129…` |
| `full-acceptance-angle-bracket-2.cue` | `album/full acceptance_ angle_bracket 20260928t22__us-fork-g51cc789 _2_/full acceptance∶ angle‹bracket 20260928t223356 platterpus-fork-g51cc789.cue` | `77060e6606bf4089…` |
| `full-acceptance-angle-bracket-2.eac.log` | `album/full acceptance_ angle_bracket 20260928t22__us-fork-g51cc789 _2_/full acceptance∶ angle‹bracket 20260928t223356 platterpus-fork-g51cc789 (EAC-compatible).log` | `fd1e6a3848d60547…` |
| `full-acceptance-angle-bracket-2.log` | `album/full acceptance_ angle_bracket 20260928t22__us-fork-g51cc789 _2_/full acceptance∶ angle‹bracket 20260928t223356 platterpus-fork-g51cc789.log` | `636bbb9c8d85147c…` |
| `full-acceptance-angle-bracket.cue` | `album/full acceptance_ angle_bracket 20260928t22__terpus-fork-g51cc789/full acceptance∶ angle‹bracket 20260928t223356 platterpus-fork-g51cc789.cue` | `b099a1324650b5a6…` |
| `full-acceptance-angle-bracket.eac.log` | `album/full acceptance_ angle_bracket 20260928t22__terpus-fork-g51cc789/full acceptance∶ angle‹bracket 20260928t223356 platterpus-fork-g51cc789 (EAC-compatible).log` | `9c6cdb880be74f09…` |
| `full-acceptance-angle-bracket.log` | `album/full acceptance_ angle_bracket 20260928t22__terpus-fork-g51cc789/full acceptance∶ angle‹bracket 20260928t223356 platterpus-fork-g51cc789.log` | `e4467f07f63d1637…` |
| `full-acceptance-angle-bracket.platterpus-addendum.txt` | `album/full acceptance_ angle_bracket 20260928t22__terpus-fork-g51cc789/full acceptance∶ angle‹bracket 20260928t223356 platterpus-fork-g51cc789.platterpus-addendum.txt` | `180cb9327b9e32f9…` |
| `r16deemphoff.cue` | `album/r16deemphoff/Unknown disc (PNTI).cue` | `62f5d1f150e71e71…` |
| `r16deemphoff.log` | `album/r16deemphoff/Unknown disc (PNTI).log` | `7c9141a215dcbe4b…` |
| `r16deemphon.cue` | `album/r16deemphon/Unknown disc (PNTI).cue` | `62f5d1f150e71e71…` |
| `r16deemphon.log` | `album/r16deemphon/Unknown disc (PNTI).log` | `66a42a7d296e48b8…` |
| `secure-reread.cue` | `album/secure reread 20260928t223356 platterpus-fork-g51cc789/secure reread 20260928t223356 platterpus-fork-g51cc789.cue` | `a0c77b89dcb14f00…` |
| `secure-reread.eac.log` | `album/secure reread 20260928t223356 platterpus-fork-g51cc789/secure reread 20260928t223356 platterpus-fork-g51cc789 (EAC-compatible).log` | `b9d39a92481a8858…` |
| `secure-reread.log` | `album/secure reread 20260928t223356 platterpus-fork-g51cc789/secure reread 20260928t223356 platterpus-fork-g51cc789.log` | `76dea5f4254d414c…` |
| `session/COMPONENTS.json` | `COMPONENTS.json` | `d030b8229f3b6c61…` |
| `session/DIAGNOSTICS.txt` | `DIAGNOSTICS.txt` | `da890d5a426a1fc9…` |
| `session/MANIFEST.txt` | `MANIFEST.txt` | `af09b1d9fd99c69e…` |
| `session/SETTINGS.json` | `SETTINGS.json` | `551e8b2b536c471f…` |
| `session/SOURCES.txt` | `SOURCES.txt` | `344a914b728b0fc3…` |
| `session/config.toml` | `session/artifacts/04platterpus/config.toml` | `8d816eea558fa8c8…` |
| `session/rig-check-argv-probe-output.txt` | `session/run/rig-check/argv-probe-output.txt` | `9666539892406fec…` |
| `session/rig-check-argv-probe.json` | `session/run/rig-check/argv-probe.json` | `71f16bc3ac4ff7e4…` |
| `session/rig-check-manifest.txt` | `session/run/rig-check/MANIFEST.txt` | `c653ae2f3b0236f8…` |
| `session/rig-check-ripper-version.txt` | `session/run/rig-check/ripper-version.txt` | `c0c6fd32cd89dda3…` |
| `session/script-report.json` | `session/run/report.json` | `45b89f288a8900d3…` |
| `session/transcript.txt` | `session/transcript.txt` | `d312cc7d3a0daeb9…` |

**Not filed**, with sha256/16 so each stays verifiable: the 20 screenshots; the
two app logs, `session/artifacts/02platterpus/log.txt` (7,525,050 bytes,
`034c6afa30b9dc48`) and `session/zz-applog-rotations/03platterpus/log.txt.1`
(8,388,586 bytes, `a3c66d5014a89d1e`); `session/run/transcript.txt`, which is
byte-identical to the `session/transcript.txt` filed here; and the eight
`.platterpus.json` reports, Platterpus's artifact: `debe6cf4f7c510ad`
full-acceptance-angle-bracket, `efb56b5f30ee1d69`
full-acceptance-angle-bracket-2, `6e91c1c170227025` secure-reread,
`efb055478d7de343` derived-mp3, `627fa78d42c0bf36` derived-wav,
`49183500e79127ea` derived-wavpack, `c9142377644b1470` after-cancel,
`783c5b1e4e612134` cancel-me. No claim below depends on any of them.

## Our reading: every cyanrip log in the bundle

**All ten verify against their own checksum** with `cyanrip -Y`, and each
footer is consistent with its `Invoked as:` line: nine completed with
`Ripping errors: 0` and `Read stalls:    none (no read exceeded 10s)`, and
`cancel-me` was interrupted mid-read by SIGTERM, as section I intends
(`Interrupted at: track 1, mid-read`). Every log's `Handshake:` line reads
`round 28 lap 8 closed, verdict GO -- released build`, the record `.18` was
built from.

**Nothing here shows a defect in `.18`.**

### `.18`'s changes, on a drive for the first time

- **`rips/cancel-me.log:56` prints `Stopping, ripping incomplete!`** on the
  signal stop of a read (`9d52271`).
- **The same log's footer carries both of `f150c0c`'s lines**:
  `Encoder errors: not applicable; no whole track was encoded`, and
  `Partial files:  1 track (1), read not completed; encoder failures: none`.
  The aborted arm printed too, in section P2's deliberate no-offset refusal:
  `cyanrip -N -l 1` exited 1 with `Offset is unset! To continue with an offset
  of 0, run with -s 0!` and `Encoder errors: not applicable; no track was
  encoded` (`session/DIAGNOSTICS.txt`, the second warning). No log of that
  invocation is in the bundle.
- **The disc-level `AccurateRip:` line reads `found` in all ten.** That is the
  only arm a disc in the database reaches; `mismatch` and `not found`
  (`64642db`) are not exercised here.
- **Upstream's MusicBrainz retry (`f8ebf48`) is not exercised**: every
  invocation passes `-N`.

### What else the logs show

- **Section N's secure re-read converged on all fourteen tracks**: eleven
  after 3 reads, and tracks 1, 3 and 4 after 4 (`rips/secure-reread.log`).
- **Tracks ripped accurately: 12/14 in section F, partially accurately 2/14**,
  tracks 3 and 5, each matching on frame 450 only; **13/14 and 1/14 in section
  N**, track 5.
- **Track 3 in section F read `3D8FCF0C`**, its second commonest read: 11 of
  the 40 filed, by `tools/cross-rip.py docs/rig-*`. Platterpus's addendum says
  its re-read reproduced it byte for byte and converged after 3 reads, and
  section N converged on `59D352DD` after 4, which AccurateRip v1 and v2
  match. So the drive converges on either reading of track 3, as it does of
  track 5 (`E0036697` in section F and the addendum, `6902BCF0` in section N).
- **Track 1 in the `-H -W` rip read `64CA69D1`**, with `Ripping errors: 0`,
  matching on frame 450 only. No filed read of track 1 has had it before: it is
  1 of 125, beside 121 of `B0D122E7` and 3 of `0E91CD1A`. The other eight
  track-1 reads this session are `B0D122E7`, the `-H -E` rip's included. The
  checksums are taken over the samples as read, before any filter, so `-W`
  and `-E` are not what separates the two.
- **The `-H` pair prints `HDCD detected: no` and `media: CD`** in both logs,
  `.16`'s fix, and `Preemphasis:   none detected (deemphasis forced)` only
  under `-E`.
- **The repeat loop prints its checksum unfinalised.** Track 1's
  `Done; (2 out of 2 matches for current checksum 4F2EDD18)`
  (`rips/secure-reread.log:62`) stands beside `EAC CRC32:     B0D122E7`, and
  `0xB0D122E7 ^ 0xFFFFFFFF = 0x4F2EDD18`. That is what `9669d84` fixes, after
  `.18`; `.18` does not carry it.
- **Tag keys are lowercase, with `totaldiscs` and no `DISCTOTAL`**, as in
  `.17`: `bf50705`, which writes them in capitals, is also after `.18`.
- **Platterpus now passes `-r 5`** on every app rip, where the 0.6.62 and
  0.6.61 runs passed `-r 3`, so `Retry limit:    5 (per frame, and per
  whole-track re-read)` carries no rounding note. The two `-H` rips pass no
  `-r` and read `10`, the default.

### The cache probe, a fifteenth time

Section P's `cyanrip -N -x -I` again printed `at least 2048 sectors … search
ceiling reached` (`session/transcript.txt:995`), uncached 362.0 ms and cached
81.6 ms, with `Cache model:    1200 sectors (drive cache probed separately,
see "Cache probe:")` above it (`:983`). `cd-paranoia -A` on this drive says
137–140. That is the fifteenth filed session to show it, now in
`docs/KNOWN-ISSUES.md`'s table. **Do not cite our cache figure.**

## What this run does not test

The disc-level `AccurateRip:` line's `mismatch` and `not found` arms;
upstream's MusicBrainz retry; `bf50705` and `9669d84`, which postdate `.18`; a
sector that will not read; C2, which this drive reports unsupported; `-f`; and
CD-TEXT from a physical disc.
