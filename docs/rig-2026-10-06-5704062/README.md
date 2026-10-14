# Rig session 2026-10-06 — build `5704062`, Platterpus 0.6.66b1, **Full**

**Read the build, not the date.** This is `5704062`, `+platterpus.20`, the beta
cut inside round 30, through Platterpus **0.6.66b1** (`db5fd0e1`), their beta
naming it as their build under review. This is the pair the operator's round 30
close conditions of 2026-10-05 name: *"betas of both applications, and an
acceptance run of both on that pair"*. `tools/ingest-bundle.py --peer` reads
both as the newest when the run began: `.20` at `release_seq` 30, its ledger
row added by `b62650d` at 01:08:12Z, and tag `v0.6.66b1` of 01:39:31Z, both
commit or tag dates rather than pushes. Every log opens with `cyanrip
0.9.4-rc2+platterpus.20 (platterpus-fork-g5704062)` and reads `Handshake:
round 30 lap 11 OPEN, verdict OPEN -- NOT a released build`, as a beta cut with
the round open does.

**The script's own verdict is not a pass**: pass 418, **fail 7**, error 0,
skipped 0, blocked 0, **unreachable 1**, info 5, `ok: false`, with
`counts_as_evidence: true`, run size full, and no `ended_reason`
(`session/script-report.json`). **All seven failures are one check on one
property**: `expect-album-audit` at L717, L794, L897, L1041, L1068, L1095 and
L1260, each reporting *"handshake_note warned: the ripper says it was built from
an OPEN round: 'round 30 lap 11 OPEN, verdict OPEN -- NOT a released build'"*
(`session/transcript.txt:441-442`, the first). That sentence is true of this
build and was chosen knowingly: `docs/RELEASE-PLAN-platterpus.20.md` says a beta
cut inside the round logs it permanently, and `.21`, cut from the closed tree, is
the stable release. The audit's grading of it is Platterpus's to weigh. The
unreachable step is section E2 (L567): the drive is in AccurateRip's drive list,
so the offset refusal it tests cannot be reached on it. The seven screenshot
failures of 2026-09-30b and 2026-10-05 did not recur: every screenshot step
found the window on screen.

## Provenance

| | |
|---|---|
| bundle | `platterpusbundle20261006t015821z.tar.gz`, handed over by the operator on 2026-10-06 |
| sha256 | `bf0aa42428ee5c4b82af332714a36495f134f82dc9af0073866654e9b1ae4879` |
| size | 6,836,717 bytes, 105 files, 26 of them screenshots |
| session stamp | `20261006T015821Z`, `started_at` 01:58:21Z (`session/script-report.json`). The last rip, section P3's `-H -W`, finished at 03:31:40 host time, 07:31:40Z (`rips/r16deemphoff.log`, host time UTC−4) |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| disc | DiscID `pNtImOkdBm9RMBIalzx0w9cfsYY-`, 14 tracks, the reference disc |
| ripper | `cyanrip 0.9.4-rc2+platterpus.20 (platterpus-fork-g5704062)`, in every log's banner and in `session/rig-check-ripper-version.txt` |
| consumer | `platterpus/0.6.66b1`, build `db5fd0e` (`session/COMPONENTS.json`) |
| script | the full acceptance script, run size **full** |

**Every file here but this README is byte-identical to a member of that
tarball**, 57 of 57, each hashed against its original when it was copied. Three
kinds are filed for the first time:

- **The two securing passes' own logs**, `*.securing-pass.txt`. Platterpus
  re-ripped tracks 3 and 5 after sections F and N (`-Z 2 -l 3,5`), and from
  0.6.66b1 it bundles that pass's logfile, not only its stdout. Both are signed
  and verify with `cyanrip -Y`. On 2026-10-05 the only record of a second pass
  was a stdout capture.
- **Nine `-j` records**, `session/diagnostics/`, `cyanrip-diagnostics/7`, one
  for each Platterpus rip but the two securing passes, which ran in a temporary
  directory: their `Invoked as:` lines name records (the N pass's is
  `cyanrip-diagnostics-20261006T064841Z.json`) that are not in the bundle.
  Platterpus's manifest says *"ripper -j records: 9 found in the rips folders"*.
- **`session/cd-paranoia-A.txt`**, Platterpus's capture of section P's
  `cd-paranoia -A`. It is **exactly 2,000 bytes** and ends inside the timing
  table, before the cache result: the figure *"cache 137 sectors"* is in the
  step's own summary (`session/transcript.txt:1461`) and in no line of
  cd-paranoia's that the bundle carries.

Names as on 2026-10-05: `-2` is section H's overwrite re-rip, the name without
it is section F's whole-disc rip, and the two `-H` rips of section P3 are
delivered as `Unknown disc (PNTI).log`, so their names say which: `r16deemphon`
for `-H -E` and `r16deemphoff` for `-H -W`. `permutations` is section J2, a
one-track rip with no `-r` and no `-Z`, filed into a library folder.

| filed here | as delivered in their bundle | sha256/16 |
|---|---|---|
| `after-cancel.cue` | `album/after cancel 20261006t015821 platterpus-fork-g5704062/after cancel 20261006t015821 platterpus-fork-g5704062.cue` | `fe5e8021492f80d0…` |
| `after-cancel.eac.log` | `album/after cancel 20261006t015821 platterpus-fork-g5704062/after cancel 20261006t015821 platterpus-fork-g5704062 (EAC-compatible).log` | `f3a4f0159da80f71…` |
| `after-cancel.log` | `album/after cancel 20261006t015821 platterpus-fork-g5704062/after cancel 20261006t015821 platterpus-fork-g5704062.log` | `e12708d39610d868…` |
| `cancel-me.cue` | `album/cancel me 20261006t015821 platterpus-fork-g5704062/cancel me 20261006t015821 platterpus-fork-g5704062.cue` | `99a19ae8af37408e…` |
| `cancel-me.eac.log` | `album/cancel me 20261006t015821 platterpus-fork-g5704062/cancel me 20261006t015821 platterpus-fork-g5704062 (EAC-compatible).log` | `96aff69e1fdd4ace…` |
| `cancel-me.log` | `album/cancel me 20261006t015821 platterpus-fork-g5704062/cancel me 20261006t015821 platterpus-fork-g5704062.log` | `4e45b19f90bfeb86…` |
| `derived-mp3.cue` | `album/derived mp3 20261006t015821 platterpus-fork-g5704062/derived mp3 20261006t015821 platterpus-fork-g5704062.cue` | `1b0f28dd34086edd…` |
| `derived-mp3.eac.log` | `album/derived mp3 20261006t015821 platterpus-fork-g5704062/derived mp3 20261006t015821 platterpus-fork-g5704062 (EAC-compatible).log` | `a159cf46c97b3139…` |
| `derived-mp3.log` | `album/derived mp3 20261006t015821 platterpus-fork-g5704062/derived mp3 20261006t015821 platterpus-fork-g5704062.log` | `629a0b8ceded46f7…` |
| `derived-wav.cue` | `album/derived wav 20261006t015821 platterpus-fork-g5704062/derived wav 20261006t015821 platterpus-fork-g5704062.cue` | `8dab2ea567c2d11f…` |
| `derived-wav.eac.log` | `album/derived wav 20261006t015821 platterpus-fork-g5704062/derived wav 20261006t015821 platterpus-fork-g5704062 (EAC-compatible).log` | `d5fe35e570ac2dc7…` |
| `derived-wav.log` | `album/derived wav 20261006t015821 platterpus-fork-g5704062/derived wav 20261006t015821 platterpus-fork-g5704062.log` | `ae8a7bc08073f9ad…` |
| `derived-wavpack.cue` | `album/derived wavpack 20261006t015821 platterpus-fork-g5704062/derived wavpack 20261006t015821 platterpus-fork-g5704062.cue` | `aba766a258ed2ebe…` |
| `derived-wavpack.eac.log` | `album/derived wavpack 20261006t015821 platterpus-fork-g5704062/derived wavpack 20261006t015821 platterpus-fork-g5704062 (EAC-compatible).log` | `e31ae84960d28767…` |
| `derived-wavpack.log` | `album/derived wavpack 20261006t015821 platterpus-fork-g5704062/derived wavpack 20261006t015821 platterpus-fork-g5704062.log` | `93ae806eb567d3a0…` |
| `full-acceptance-angle-bracket-2.cue` | `album/full acceptance_ angle_bracket 20261006t01__us-fork-g5704062 _2_/full acceptance∶ angle‹bracket 20261006t015821 platterpus-fork-g5704062.cue` | `c2723104b7d2ee6b…` |
| `full-acceptance-angle-bracket-2.eac.log` | `album/full acceptance_ angle_bracket 20261006t01__us-fork-g5704062 _2_/full acceptance∶ angle‹bracket 20261006t015821 platterpus-fork-g5704062 (EAC-compatible).log` | `c90bac32115d0279…` |
| `full-acceptance-angle-bracket-2.log` | `album/full acceptance_ angle_bracket 20261006t01__us-fork-g5704062 _2_/full acceptance∶ angle‹bracket 20261006t015821 platterpus-fork-g5704062.log` | `819ac7fef67aa828…` |
| `full-acceptance-angle-bracket.cue` | `album/full acceptance_ angle_bracket 20261006t01__terpus-fork-g5704062/full acceptance∶ angle‹bracket 20261006t015821 platterpus-fork-g5704062.cue` | `6ce522b261e613bb…` |
| `full-acceptance-angle-bracket.eac.log` | `album/full acceptance_ angle_bracket 20261006t01__terpus-fork-g5704062/full acceptance∶ angle‹bracket 20261006t015821 platterpus-fork-g5704062 (EAC-compatible).log` | `e8254482922bc8e0…` |
| `full-acceptance-angle-bracket.log` | `album/full acceptance_ angle_bracket 20261006t01__terpus-fork-g5704062/full acceptance∶ angle‹bracket 20261006t015821 platterpus-fork-g5704062.log` | `4b183838983e02d3…` |
| `full-acceptance-angle-bracket.platterpus-addendum.txt` | `album/full acceptance_ angle_bracket 20261006t01__terpus-fork-g5704062/full acceptance∶ angle‹bracket 20261006t015821 platterpus-fork-g5704062.platterpus-addendum.txt` | `0ad4bcfa7934522d…` |
| `full-acceptance-angle-bracket.securing-pass.txt` | `album/full acceptance_ angle_bracket 20261006t01__terpus-fork-g5704062/full acceptance∶ angle‹bracket 20261006t015821 platterpus-fork-g5704062.platterpus-securing-pass.txt` | `f454365628076320…` |
| `permutations.cue` | `album/permutations 20261006t015821 platterpus-fork-g5704062/permutations 20261006t015821 platterpus-fork-g5704062.cue` | `b3323e375ca4a24b…` |
| `permutations.eac.log` | `album/permutations 20261006t015821 platterpus-fork-g5704062/permutations 20261006t015821 platterpus-fork-g5704062 (EAC-compatible).log` | `6add6091cce281f4…` |
| `permutations.log` | `album/permutations 20261006t015821 platterpus-fork-g5704062/permutations 20261006t015821 platterpus-fork-g5704062.log` | `4eada00546804c2d…` |
| `r16deemphoff.cue` | `album/r16deemphoff/Unknown disc (PNTI).cue` | `801640a40fd2ba0a…` |
| `r16deemphoff.log` | `album/r16deemphoff/Unknown disc (PNTI).log` | `d3473afd286c6bf1…` |
| `r16deemphon.cue` | `album/r16deemphon/Unknown disc (PNTI).cue` | `801640a40fd2ba0a…` |
| `r16deemphon.log` | `album/r16deemphon/Unknown disc (PNTI).log` | `fea0dbef017ff680…` |
| `secure-reread.cue` | `album/secure reread 20261006t015821 platterpus-fork-g5704062/secure reread 20261006t015821 platterpus-fork-g5704062.cue` | `4725bf2c776a40fd…` |
| `secure-reread.eac.log` | `album/secure reread 20261006t015821 platterpus-fork-g5704062/secure reread 20261006t015821 platterpus-fork-g5704062 (EAC-compatible).log` | `70a8299b24fee00e…` |
| `secure-reread.log` | `album/secure reread 20261006t015821 platterpus-fork-g5704062/secure reread 20261006t015821 platterpus-fork-g5704062.log` | `edc3cc68afc60388…` |
| `secure-reread.platterpus-addendum.txt` | `album/secure reread 20261006t015821 platterpus-fork-g5704062/secure reread 20261006t015821 platterpus-fork-g5704062.platterpus-addendum.txt` | `4a991283b101496a…` |
| `secure-reread.securing-pass.txt` | `album/secure reread 20261006t015821 platterpus-fork-g5704062/secure reread 20261006t015821 platterpus-fork-g5704062.platterpus-securing-pass.txt` | `ab710c853d33bcea…` |
| `session/COMPONENTS.json` | `COMPONENTS.json` | `3a9da3bc6df12fad…` |
| `session/DIAGNOSTICS.txt` | `DIAGNOSTICS.txt` | `89ae9d1f00f3b393…` |
| `session/MANIFEST.txt` | `MANIFEST.txt` | `f021d2e7b2fba87b…` |
| `session/SETTINGS.json` | `SETTINGS.json` | `b144137c552c9db1…` |
| `session/SOURCES.txt` | `SOURCES.txt` | `ace041634a5952a2…` |
| `session/config.toml` | `session/artifacts/12platterpus/config.toml` | `b8ae1bfdc7ac4030…` |
| `session/cd-paranoia-A.txt` | `session/run/cacheprobe1348.txt` | `95e61b0f2170be3f…` |
| `session/rig-check-argv-probe-output.txt` | `session/run/rig-check/argv-probe-output.txt` | `f8874e9eb888ae4e…` |
| `session/rig-check-argv-probe.json` | `session/run/rig-check/argv-probe.json` | `ffef720d652932b2…` |
| `session/rig-check-manifest.txt` | `session/run/rig-check/MANIFEST.txt` | `6c223988db21e658…` |
| `session/rig-check-ripper-version.txt` | `session/run/rig-check/ripper-version.txt` | `d7efcb717187db0a…` |
| `session/script-report.json` | `session/run/report.json` | `6f245fb7444ff7e4…` |
| `session/transcript.txt` | `session/transcript.txt` | `9efc65c17a20de11…` |
| `session/diagnostics/cyanrip-diagnostics-20261006T015852Z.json` | `ripperdiagnostics/cyanrip-diagnostics-20261006T015852Z.json` | `29710741e72e4d22…` |
| `session/diagnostics/cyanrip-diagnostics-20261006T032722Z.json` | `ripperdiagnostics/cyanrip-diagnostics-20261006T032722Z.json` | `7f745f4cdc813b37…` |
| `session/diagnostics/cyanrip-diagnostics-20261006T033311Z.json` | `ripperdiagnostics/cyanrip-diagnostics-20261006T033311Z.json` | `4834026966a7ed7d…` |
| `session/diagnostics/cyanrip-diagnostics-20261006T033707Z.json` | `ripperdiagnostics/cyanrip-diagnostics-20261006T033707Z.json` | `6318cc4b63385a66…` |
| `session/diagnostics/cyanrip-diagnostics-20261006T034259Z.json` | `ripperdiagnostics/cyanrip-diagnostics-20261006T034259Z.json` | `5ce49f1dd66fc741…` |
| `session/diagnostics/cyanrip-diagnostics-20261006T034604Z.json` | `ripperdiagnostics/cyanrip-diagnostics-20261006T034604Z.json` | `2beafb93a4d8f410…` |
| `session/diagnostics/cyanrip-diagnostics-20261006T035150Z.json` | `ripperdiagnostics/cyanrip-diagnostics-20261006T035150Z.json` | `fd4ff4c8a7246f75…` |
| `session/diagnostics/cyanrip-diagnostics-20261006T035731Z.json` | `ripperdiagnostics/cyanrip-diagnostics-20261006T035731Z.json` | `e08c044992ac97c5…` |
| `session/diagnostics/cyanrip-diagnostics-20261006T040325Z.json` | `ripperdiagnostics/cyanrip-diagnostics-20261006T040325Z.json` | `9da01ffd8bebe52c…` |

**Not filed**, with sha256/16 so each stays checkable against the tarball: the
26 screenshots; `session/run/transcript.txt`, byte-identical to the
`session/transcript.txt` filed here; the 9 `.platterpus.json` reports,
Platterpus's artifact (`e9a6d0309a83108c` after cancel, `bc5733c7d95fb913`
cancel me, `bcca9be4c4559ff5` derived mp3, `b622df51e8a63269` derived wav,
`170403936a5d3bdf` derived wavpack, `6eb384764abf91eb` full acceptance,
6,184,183 bytes, `77f038790396866e` full acceptance (2), `349aec1c896b9636`
permutations, and `96e7a9a99f0ef769` secure reread); the seven `tags*.txt`,
Platterpus's dumps of one FLAC's tags per rip (`81f135e841afe237`,
`37f9e4be04c51320`, `49516fccca5693ec`, `02a8d6463f9c6e4e`, `45a55032b0b0a712`,
`e07f87c868186775`, `835a61ea0ec2e977`); and the five app logs:
`session/artifacts/02platterpus/log.txt` (8,196,312 bytes, `7a1ea340c179f5f4`),
`session/zz-applog-rotations/03platterpus/log.txt.1` (8,388,506 bytes,
`48cc38e400ca22ed`), which holds this run's sections F to N and the cancel,
`04platterpus/log.txt.2` (`43897f0e5d176c4b`), which holds its start, and two
older rotations: `05platterpus/log.txt.3` (`024b3b262fb0c515`), byte-identical
to the 2026-10-05 bundle's `log.txt.1`, and `06platterpus/log.txt.4`
(`a8cd0f5cb3e042d2`). Five older rotations were left out by their bundler's
64 MiB budget, and its manifest names each. Line numbers below are in the files
as delivered.

## Our reading: every cyanrip log in the bundle

**All thirteen verify against their own checksum** with `cyanrip -Y`, run with
the build of `8d68806`: the eleven rips and the two securing passes. Each footer
is consistent with its `Invoked as:` line: twelve completed with `Ripping errors: 0`
and `Read stalls:    none (no read exceeded 10s)`, and `cancel-me` was
interrupted mid-read by SIGTERM, as section I intends (`Rip completed:  no
(interrupted by SIGTERM, 0 of 14 tracks)`, `Interrupted at: track 1, mid-read`,
`Partial files:  1 track (1), read not completed; encoder failures: none`),
with exit 1 in its `-j` record. `tools/ingest-bundle.py` finds every log ending
in a signed completion footer.

### What `.20` changed, seen on a drive for the first time

- **`read with errors.` for a `-Z` read that never agreed** (`4529810`). Section
  N, `-Z 2 -r 5`, read tracks 3 and 5 five times each without three agreeing,
  and both blocks open `Track 3 read with errors.` and `Track 5 read with
  errors.` (`rips/secure-reread.log:227`, `:397`), under `Done; (repeat limit of
  5 reads reached; at most 1 read agreed)` and `at most 2 reads agreed`. On `.19`
  the same outcome printed `read successfully!`
  (`docs/rig-2026-10-05-174a134/rips/secure-reread.log`). Section F's securing
  pass reads track 3 the same way
  (`rips/full-acceptance-angle-bracket.securing-pass.txt:63`).
  `Ripping errors: 0` stands beside them, as designed: since `0c692ed` it counts
  operational failures and paranoia's skips, and this run had no skip
  (`paranoia_skips: 0` in every `-j` record). **The skip arm of `e5a0897` has
  still not run on a drive.**
- **The `-Z` spool at the repeat limit** (`d7ee6c4`) kept, for every limit-hit
  track, the read `.19` would also have kept, so it changed no delivered byte
  on this run. Track 3 of section N read five different checksums, so the
  newest, `2AC1F945`, was kept. Track 5 read `E0036697`, `C96464AB`, `C96464AB`
  and `BBB13C9B` (`:388-396`), and kept `E0036697` with `at most 2 reads
  agreed`. **The fifth read is printed nowhere**, and it is known only because
  the rule allows nothing else: `E0036697` could be kept only by tying
  `C96464AB` at two reads and being newer, so the fifth read was `E0036697`.
  The securing passes then **converged on both kept values**: section N's on
  `2AC1F945` for track 3 (three of five reads) and on `E0036697` for track 5
  (three of four), and section F's on `E0036697` for track 5, its first pass's
  read. Section F's securing pass did not converge on track 3, and its addendum
  names track 5 only, so track 3's file is the first pass's read, `329DC760`.
  That the fifth read is not printed is a defect, found reading this run and
  recorded below.
- **The cache probe, on `cd-paranoia -A`'s criterion** (`394ab17`, `6dd608c`):
  `-N -x -I` exited 0 in 7.9 s with `Cache probe:    128 to 255 sectors (294.0
  to 585.7 KiB, uncached read 251.0 ms, cached read 1.7 ms, 3 re-reads after a
  256-sector run took 32.6 ms or more)` (`session/transcript.txt:1230`).
  `cd-paranoia -A`, run on the same drive straight after it for 75 s, reported
  137 sectors by Platterpus's summary of it (above). **137 falls inside the
  bracket, which is the agreement `docs/KNOWN-ISSUES.md` set as this measurement's test**, and it
  is the first run of the fix on a drive. The re-read after a 128-sector run took
  1.7 ms, under the 6 ms threshold, and all three re-reads after the 256-sector
  run took at least 32.6 ms, over five times it, so the search stopped for the
  reason the criterion gives. One run; the doubling search can say no more than
  a power of two. On 2026-10-05 `.19` printed the same bracket for a reason the
  fix removed: its threshold was a quarter of a 304.2 ms calibration read.
- **`-f` on a drive** (`aa1f067`, `0645ddb`), section O, the first in any filed
  session: `cyanrip -N -f` exited 0 in 34.1 s with `Drive offset of +667 found
  (confidence: 14)!`, every one of the 14 tracks confirming it
  (`session/transcript.txt:1113-1165`). +667 is the offset the rig is set to and
  AccurateRip's drive list carries. Its footer reads `Rip completed:  no (offset
  search only, 0 of 14 tracks)` and `Encoder errors: not applicable; no track was
  encoded`; `Tracks ripped accurately: 0/14` above them counts finished tracks,
  as it does on the cancelled rip.
- **Loudness measured on the delivered audio** (`cc79c5b`), section P3. On `.19`
  the `-H -E` and `-H -W` rips of track 1 printed identical loudness and peak
  figures, the read buffer's. On `.20` they differ: `-H -W` reads `-19.9 LUFS`,
  sample peak `-6.5 dBFS`, true peak `-5.8 dBFS`, and `-H -E` reads `-20.7
  LUFS`, `-6.3 dBFS`, `-6.3 dBFS` (`rips/r16deemphoff.log`, `rips/r16deemphon.log`).
  `-H -W` is 6.0 below `.19`'s `-13.9 LUFS` and `-0.5 dBFS`, the 6.02 dB a `-H`
  rip of a non-HDCD disc delivers, measured on a fixture when the fix landed.
  `EAC CRC32` and the AccurateRip checksums are unchanged, from each other and
  from `.19`'s, since they stay on the bytes read.
- **The interrupt, again in the one-signal world.** Section I cancelled at
  23:34:41.648 host time, with one SIGTERM to the process Platterpus started,
  the host wrapper; the post-cancel rescue signalled whatever held `/dev/sr0`
  at 23:34:46.548, `fuser rc=0` at .661; the log gained its footer by 23:34:46.906
  (`03platterpus/log.txt.1:32551-32558`), and it reads `Ripping finished at
  2026-10-05T23:34:46-04:00`. Their script's `sigterm-world` step says the same
  (`session/transcript.txt:564`). As on 2026-10-05, the rescue's signal was
  cyanrip's first.
- **Section P2**: `cyanrip -N -l 1` refused for want of an offset, exit 1 in
  5.1 s (`session/transcript.txt:1484`). No hang.

### What else the logs show

- **AccurateRip**: both whole-disc rips print `Tracks ripped accurately: 12/14`
  and `Tracks ripped partially accurately: 2/14`, over **tracks 3 and 5**, as on
  every run of this disc; each matched only the one-frame 450 checksum. Every
  shorter rip is all of its tracks. CTDB, Platterpus's: `no_match` for section F
  and `match, confidence 1` for section N (L719, L1262).
- **Tracks 3 and 5 across this session**, by `tools/cross-rip.py
  docs/rig-2026-10-06-5704062/rips`: **track 3 was read 16 times with 12
  checksums**, `2AC1F945` four times and `329DC760` twice; **track 5 was read 15
  times with 5**, `E0036697` nine times. None is AccurateRip-accurate. Neither
  `59D352DD`, the accurate track 3 earlier sessions reached, nor any accurate
  track 5 appears; over every filed session `E0036697` and `6902BCF0`, both
  one-frame matches only, are the values track 5 repeats.
- **Every other track agreed with itself**: tracks 1 and 2 across twelve and
  nine reads, the rest across four.

### Found in our code, reading this run

Both are recorded in `docs/KNOWN-ISSUES.md` under *Open, ours, and solvable*.

- **At the repeat limit `.20` does not print the last read's checksum, and when
  the spool keeps an earlier read it is in no line of the log.** The loop prints
  `Repeating ripping (... current checksum X)` after every read but the last,
  and the block's `EAC CRC32` is the kept read's. On `.19` the kept read was the
  last one, so the log carried all five; on `.20` it is the most-agreed read, so
  a track read A, A, B, B, C keeps B and carries no trace of C. On this run it
  did not happen, as above. It happens on demand with `tests/badsector.c`'s flip
  schedule, `CYCLE 3 RUN 2 -r 5`: the log prints `B664A115` twice and
  `2FFECF45` twice and keeps `2FFECF45`, and the fifth read, `EE58174A`, is
  nowhere. The block's paranoia counters are the last read's too (`Scope:
  the last of 5 reads`), so in that case they describe a read the block does not
  otherwise describe. **`tools/cross-rip.py` counted the kept block as the last
  read, which was false in exactly this case: it reported `2FFECF45` three
  times and lost the fifth read.** Fixed in the commit after this filing, with
  its test.
- **The `Gaps:` list leaves out a pregap it could not determine, so it reads as
  no pregap.** Section P3's `-H -W` log lists eight pregaps and the
  `-H -E` log nine: `158 frame pregap in track 4` is missing from the first.
  Both rip track 1 only, so track 4's block, which says `Pregap LSN:  unknown
  (...)` when its search fails, is not printed, and nothing in the log says why
  the line is gone. `setup_track_offsets_and_report()` skips an invalid pregap
  silently (`src/cyanrip_main.c:1535-1536`). It is the second time in 153 filed
  logs of this disc that carry the list; the first is
  `docs/rig-2026-09-22-2cce60d/rips/derived-wavpack.log`. A disc image shows it
  without a drive: `-l 1` of `tests/fixtures/basic.cue` prints `Gaps:` `None
  signalled` while track 2's pregap is `unknown (sub-channel unreadable)`. No
  audio byte changes: the default action merges a pregap into the track before
  it, whose end the TOC already gives.

### Found on Platterpus's side, for them to weigh

- **Their album audit fails a property the beta declares on purpose**, seven
  times (above). The sentence it warns on is the one `.20` must print.
- **Two `-j` records were not collected**: the securing passes', written in
  their temporary directory.
- **The `cd-paranoia -A` capture is cut at 2,000 bytes**, before the line the
  step's summary reads its figure from.
- **Their securing-pass logs and addenda agree with the logs**: each addendum's
  CRC, AccurateRip values and `Secure re-read:` line are the ones the
  corresponding securing-pass log prints. The 2026-10-05 gap, a second pass with
  no log, is closed.

### Not established

- The fifth read of section N's track 3: all five differ, so the kept read was
  the newest by the rule, and the log prints the kept read; that it was the
  fifth follows from the rule, not from a line.
- Whether `.20`'s cache bracket holds over more than one run.
- What the `-H -W` rip's track 4 search returned: a failure, or a pregap of
  zero, which the list also leaves out.
