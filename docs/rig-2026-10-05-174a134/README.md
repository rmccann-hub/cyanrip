# Rig session 2026-10-05 — build `174a134`, Platterpus 0.6.65, **Full**

**Read the build, not the date.** This is `174a134`, `+platterpus.19`, through
Platterpus **0.6.65** (`0981c69`): the pair of `docs/rig-2026-09-30b-174a134/`
and `docs/rig-2026-10-04-174a134/`. The operator announced it on 2026-10-04 as
*"1 final acceptance run file in the morning, same version"*, and that is what
it is: a second Full run of the pair round 30 opened on, on the reference disc.
**It tests nothing landed for `.20`**: every log here opens with `cyanrip
0.9.4-rc2+platterpus.19 (platterpus-fork-g174a134)`, and `.20` is not cut.
`tools/ingest-bundle.py --peer` reads the pair as the newest on both sides when
the run began.

**The script's own verdict is not a pass**: pass 316, **fail 7**, error 0,
skipped 0, blocked 0, unreachable 0, info 1, `ok: false`, with
`counts_as_evidence: true`, run size full, and no `ended_reason`
(`session/script-report.json`). **All seven failures are `screenshot` steps**,
the same seven as on 2026-09-30b: L585, L676, L724, L749, L815, L850 and L988,
each reporting *"examined 8 window(s) and none was on screen, so there was
nothing to photograph"*, with the main window `visible=True` and
`exposed=False` (`session/transcript.txt:387-390`, the first). None is a cyanrip
step; what they mean is Platterpus's to say.

## Provenance

| | |
|---|---|
| bundle | `platterpusbundle20261005t010835z.tar.gz`, handed over by the operator on 2026-10-05 |
| sha256 | `d4a35338c6d9466b835f0e7bc33a1ef551a7964b0d91815f6de863ab274ef189` |
| size | 5,210,218 bytes, 67 files, 12 of them screenshots |
| session stamp | `20261005T010835Z`, `started_at` 01:08:35Z (`session/script-report.json`). The last rip, section P3's `-H -W`, finished at 02:17:53 host time, 06:17:53Z (`rips/r16deemphoff.log`, host time UTC−4) |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| disc | DiscID `pNtImOkdBm9RMBIalzx0w9cfsYY-`, 14 tracks, the reference disc |
| ripper | `cyanrip 0.9.4-rc2+platterpus.19 (platterpus-fork-g174a134)`, in every log's banner and in `session/rig-check-ripper-version.txt` |
| consumer | `platterpus/0.6.65`, build `0981c69` (`session/COMPONENTS.json`) |
| script | the full acceptance script, run size **full** |

**Every file here but this README is byte-identical to a member of that
tarball**, 40 of 40, each hashed against its original when it was copied, with
one exception that is still checkable:
`full-acceptance-angle-bracket.ripper-stdout.txt` is Platterpus's capture of
cyanrip's stdout for section F, taken from the `artifacts.ripper_stdout.text`
field of their `.platterpus.json` and written as UTF-8. Its sha256,
`3675ac714b925af4…`, is the one that report records for it, so the bytes are the
ones their tool hashed. It is filed because it is the only record of section F's
second pass: that pass ran in a temporary directory and its own log is not in
the bundle. As in earlier filings, `-2` is section H's overwrite re-rip, the name
without it is section F's whole-disc rip, and the two `-H` rips of section P3 are
delivered as `Unknown disc (PNTI).log`, so their names say which: `r16deemphon`
for `-H -E` and `r16deemphoff` for `-H -W`.

| filed here | as delivered in their bundle | sha256/16 |
|---|---|---|
| `after-cancel.cue` | `album/after cancel 20261005t010835 platterpus-fork-g174a134/after cancel 20261005t010835 platterpus-fork-g174a134.cue` | `3dbcd8b707548047…` |
| `after-cancel.eac.log` | `album/after cancel 20261005t010835 platterpus-fork-g174a134/after cancel 20261005t010835 platterpus-fork-g174a134 (EAC-compatible).log` | `46450cbafcef4710…` |
| `after-cancel.log` | `album/after cancel 20261005t010835 platterpus-fork-g174a134/after cancel 20261005t010835 platterpus-fork-g174a134.log` | `f01b337b074d7ce8…` |
| `cancel-me.cue` | `album/cancel me 20261005t010835 platterpus-fork-g174a134/cancel me 20261005t010835 platterpus-fork-g174a134.cue` | `78adc14cf99511a9…` |
| `cancel-me.eac.log` | `album/cancel me 20261005t010835 platterpus-fork-g174a134/cancel me 20261005t010835 platterpus-fork-g174a134 (EAC-compatible).log` | `ec9ef63c45255469…` |
| `cancel-me.log` | `album/cancel me 20261005t010835 platterpus-fork-g174a134/cancel me 20261005t010835 platterpus-fork-g174a134.log` | `0fa6fd204bf7edbe…` |
| `derived-mp3.cue` | `album/derived mp3 20261005t010835 platterpus-fork-g174a134/derived mp3 20261005t010835 platterpus-fork-g174a134.cue` | `43792632b49225d1…` |
| `derived-mp3.eac.log` | `album/derived mp3 20261005t010835 platterpus-fork-g174a134/derived mp3 20261005t010835 platterpus-fork-g174a134 (EAC-compatible).log` | `fa23634e75db1218…` |
| `derived-mp3.log` | `album/derived mp3 20261005t010835 platterpus-fork-g174a134/derived mp3 20261005t010835 platterpus-fork-g174a134.log` | `9aa9101648ebf810…` |
| `derived-wav.cue` | `album/derived wav 20261005t010835 platterpus-fork-g174a134/derived wav 20261005t010835 platterpus-fork-g174a134.cue` | `2bb628ba150fa9f5…` |
| `derived-wav.eac.log` | `album/derived wav 20261005t010835 platterpus-fork-g174a134/derived wav 20261005t010835 platterpus-fork-g174a134 (EAC-compatible).log` | `0dece4b95146391b…` |
| `derived-wav.log` | `album/derived wav 20261005t010835 platterpus-fork-g174a134/derived wav 20261005t010835 platterpus-fork-g174a134.log` | `5684beb45a0acf0b…` |
| `derived-wavpack.cue` | `album/derived wavpack 20261005t010835 platterpus-fork-g174a134/derived wavpack 20261005t010835 platterpus-fork-g174a134.cue` | `8f760467b909daef…` |
| `derived-wavpack.eac.log` | `album/derived wavpack 20261005t010835 platterpus-fork-g174a134/derived wavpack 20261005t010835 platterpus-fork-g174a134 (EAC-compatible).log` | `0b9f78c63f910484…` |
| `derived-wavpack.log` | `album/derived wavpack 20261005t010835 platterpus-fork-g174a134/derived wavpack 20261005t010835 platterpus-fork-g174a134.log` | `90609ca107d58e1e…` |
| `full-acceptance-angle-bracket-2.cue` | `album/full acceptance_ angle_bracket 20261005t01__us-fork-g174a134 _2_/full acceptance∶ angle‹bracket 20261005t010835 platterpus-fork-g174a134.cue` | `93e11d866953acf4…` |
| `full-acceptance-angle-bracket-2.eac.log` | `album/full acceptance_ angle_bracket 20261005t01__us-fork-g174a134 _2_/full acceptance∶ angle‹bracket 20261005t010835 platterpus-fork-g174a134 (EAC-compatible).log` | `980b8d671a5890b4…` |
| `full-acceptance-angle-bracket-2.log` | `album/full acceptance_ angle_bracket 20261005t01__us-fork-g174a134 _2_/full acceptance∶ angle‹bracket 20261005t010835 platterpus-fork-g174a134.log` | `09bdba09ba14e64b…` |
| `full-acceptance-angle-bracket.cue` | `album/full acceptance_ angle_bracket 20261005t01__terpus-fork-g174a134/full acceptance∶ angle‹bracket 20261005t010835 platterpus-fork-g174a134.cue` | `f54d4c6b46c9579a…` |
| `full-acceptance-angle-bracket.eac.log` | `album/full acceptance_ angle_bracket 20261005t01__terpus-fork-g174a134/full acceptance∶ angle‹bracket 20261005t010835 platterpus-fork-g174a134 (EAC-compatible).log` | `dd4a624f3c941781…` |
| `full-acceptance-angle-bracket.log` | `album/full acceptance_ angle_bracket 20261005t01__terpus-fork-g174a134/full acceptance∶ angle‹bracket 20261005t010835 platterpus-fork-g174a134.log` | `1e7c988457877cc5…` |
| `r16deemphoff.cue` | `album/r16deemphoff/Unknown disc (PNTI).cue` | `f3c0672791431738…` |
| `r16deemphoff.log` | `album/r16deemphoff/Unknown disc (PNTI).log` | `cba81f4af7e15066…` |
| `r16deemphon.cue` | `album/r16deemphon/Unknown disc (PNTI).cue` | `f3c0672791431738…` |
| `r16deemphon.log` | `album/r16deemphon/Unknown disc (PNTI).log` | `b3ef5844d3e4724e…` |
| `secure-reread.cue` | `album/secure reread 20261005t010835 platterpus-fork-g174a134/secure reread 20261005t010835 platterpus-fork-g174a134.cue` | `8a2c42b850435fea…` |
| `secure-reread.eac.log` | `album/secure reread 20261005t010835 platterpus-fork-g174a134/secure reread 20261005t010835 platterpus-fork-g174a134 (EAC-compatible).log` | `78fd6f3eb013e042…` |
| `secure-reread.log` | `album/secure reread 20261005t010835 platterpus-fork-g174a134/secure reread 20261005t010835 platterpus-fork-g174a134.log` | `b8647b8df82f631c…` |
| `session/COMPONENTS.json` | `COMPONENTS.json` | `3be5759169a4a284…` |
| `session/DIAGNOSTICS.txt` | `DIAGNOSTICS.txt` | `3e7a1579d5bdafb2…` |
| `session/MANIFEST.txt` | `MANIFEST.txt` | `60e623e9dcadf5a3…` |
| `session/SETTINGS.json` | `SETTINGS.json` | `9cd5a169eb2e0c5a…` |
| `session/SOURCES.txt` | `SOURCES.txt` | `0fb21815079f0e01…` |
| `session/config.toml` | `session/artifacts/10platterpus/config.toml` | `8d816eea558fa8c8…` |
| `session/rig-check-argv-probe-output.txt` | `session/run/rig-check/argv-probe-output.txt` | `321c0320930cf65e…` |
| `session/rig-check-argv-probe.json` | `session/run/rig-check/argv-probe.json` | `368309967ce1e3b2…` |
| `session/rig-check-manifest.txt` | `session/run/rig-check/MANIFEST.txt` | `f499717f24473d92…` |
| `session/rig-check-ripper-version.txt` | `session/run/rig-check/ripper-version.txt` | `3dd6fb1ac56dbfad…` |
| `session/script-report.json` | `session/run/report.json` | `abdab97ab170dac0…` |
| `session/transcript.txt` | `session/transcript.txt` | `482e96b048cd62b7…` |

**Not filed**, with sha256/16 so each stays checkable against the tarball: the
12 screenshots; `session/run/transcript.txt`, byte-identical to the
`session/transcript.txt` filed here; the 8 `.platterpus.json` reports,
Platterpus's artifact (`29f1140eef7716f8` after cancel, `97b64c4dfc83c5fd`
cancel me, `53655418c98f5d17` derived mp3, `dc930e314fdc00bd` derived wav,
`f3c47394a3eb095f` derived wavpack, `2d07ac7a32683484` full acceptance,
6,256,172 bytes, `02faa20cecf46b6e` full acceptance (2), and `8af212575fc1acdb`
secure reread); and the six app logs, of which the readings below cite these:
`session/artifacts/02platterpus/log.txt` (6,239,918 bytes, `37df2bf17bed8495`),
`session/zz-applog-rotations/03platterpus/log.txt.1` (8,388,508 bytes,
`024b3b262fb0c515`), which holds this run's sections F to N, and
`session/zz-applog-rotations/05platterpus/log.txt.3` (8,388,572 bytes,
`102ca6638f2dccda`), which is **byte-identical** to the 2026-10-04 160255z
bundle's `log.txt.1` that `docs/rig-2026-10-04-174a134/README.md` cites, so its
line numbers are that README's. The other three rotations
(`a8cd0f5cb3e042d2`, `d81ebcfa49ecd224`, `42b8aa3d6907ffd5`) are older; the last
two are byte-identical to app logs of the 2026-10-04 and 2026-09-30b bundles.
Line numbers below are in the files as delivered.

## Our reading: every cyanrip log in the bundle

**All ten verify against their own checksum** with `cyanrip -Y`, run with the
build of `ac54207`, and each footer is consistent with its `Invoked as:` line:
nine completed with `Ripping errors: 0` and `Read stalls:    none (no read
exceeded 10s)`, and `cancel-me` was interrupted mid-read by SIGTERM, as section
I intends (`Rip completed:  no (interrupted by SIGTERM, 0 of 14 tracks)`,
`Interrupted at: track 1, mid-read`, `Partial files:  1 track (1), read not
completed`). Every log's `Handshake:` line reads `round 29 lap 3 closed, verdict
GO -- released build`.

**Nothing here is a defect in `.19` that was not already recorded.** One known
defect shows again, already fixed for `.20`; the cache probe does something it
has not done before, and the reason is the known defect, not a fix.

### The repeat limit on `.19`, three times, and the line `.20` changes

- **Section N, track 3**: five reads, five checksums, `Done; (repeat limit of 5
  reads reached; at most 1 read agreed)`, `Secure re-read:  did NOT converge
  after 5 reads (repeat limit hit)` and, above them, `Track 3 read
  successfully!` (`rips/secure-reread.log:220-267`). That outcome line is the
  one `.20` changes to `read with errors.` (`4529810`). The other thirteen
  converged, twelve after 3 reads and track 5 after 4.
- **Section F's second pass**, `-Z 2 -l 3,5`, which Platterpus ran after the
  whole-disc pass because tracks 3 and 5 matched AccurateRip on one frame only:
  both hit the limit. Track 3 read `981BA62F`, `A25C69A3`, `2AC1F945`, `418F6CF8`,
  then `80035387`, five checksums; track 5 read `4065BECC` twice, `C96464AB`,
  then `6902BCF0` twice, and `.19` kept the fifth read
  (`rips/full-acceptance-angle-bracket.ripper-stdout.txt:1196-1335`). **Their
  outcome lines are not in the capture**, nor is any track's in either pass: see
  the last section.
- **What `.20`'s spool would have kept**, from these reads: the most-agreed read,
  the newest on a tie. Track 5's two pairs tie, so the newest, `6902BCF0`, the
  read `.19` kept; track 3's reads all differ, so the fifth, again the read `.19`
  kept. On this run the spool changes no delivered byte. It changes the outcome
  line, which says `with errors` on all three.

### What else the logs show

- **AccurateRip**: both whole-disc rips have `Tracks ripped accurately: 12/14`,
  and the two not found are **tracks 3 and 5**, as on every run of this disc;
  each matched only the one-frame 450 checksum. Every two-track rip is 2 of 2. In
  this session **track 3 was read 11 times with 11 different EAC CRC32s**: six in
  the logs, from `tools/cross-rip.py docs/rig-2026-10-05-174a134/rips`, and the
  second pass's five, counted by hand, since the capture carries the first pass
  too and the tool would count that twice. None is `59D352DD`, the
  AccurateRip-accurate value earlier sessions reached. **Track 5 was read 10
  times with four values**: `6902BCF0` four times, `E0036697` three, `4065BECC`
  twice and `C96464AB` once. Across every filed log `tools/cross-rip.py
  docs/rig-*` now counts 24 values for track 3 in 50 reads and 3 for track 5 in
  46, before this session's second pass.
- **Platterpus replaced nothing.** Their section F report says *"read
  instability remained after the automatic re-rip (track(s) 3, 5)"*, its verdict
  is `warn`, and its `addendum` artifact is `missing`, where 2026-09-30b's
  addendum replaced both tracks.
- **Section P, the cache probe: `128 to 255 sectors`**, for the first time in
  seventeen filed sessions, and the reason is the known defect, not a fix. `-N
  -x -I` exited 0 in 8.6 s with `Cache probe:    128 to 255 sectors (294.0 to
  585.7 KiB, uncached read 304.2 ms, cached read 1.5 ms)`
  (`session/transcript.txt:947`). The bracket holds `cd-paranoia -A`'s 137 to
  140. Two things are new. **The calibration read was 304.2 ms**, which puts
  `.19`'s threshold, a quarter of it, at 76.05 ms, under the 81.3 to 82.2 ms
  classified reads that six of the sixteen earlier rows printed. The search
  stopped at 256 only because the re-read there took at least 76.05 ms. The line
  does not print that read, and no `-j` record of it exists, since the probe runs
  without `-j`. And **`cached read 1.5 ms` is the first classified read in any
  filed transcript under `cd-paranoia -A`'s 6 ms**: a re-read of the seed after
  128 sectors, inside the cache `cd-paranoia` measures, took 1.5 ms. That is one
  sample supporting the premise of `.20`'s fix (`394ab17`): on this drive a real
  hit is far under 6 ms. It is not a test of that fix, which needs a `-x` run on
  `.20`. The row is in `docs/KNOWN-ISSUES.md`'s table. **Do not cite `.19`'s
  figure**: on a calibration read near 363 ms, as in twelve earlier rows, the
  same reads would have run to the ceiling.
- **Section P2**: `cyanrip -N -l 1` refused for want of an offset, exit 1 in
  5.6 s, `Offset is unset! To continue with an offset of 0, run with -s 0!`
  (`session/transcript.txt:1199`). No hang.
- **Section P3**: the `-H -E` and `-H -W` rips ran 186.2 s and 177.2 s and exited
  0. Their loudness, peak and checksum lines are identical to each other and to
  2026-09-30b's, since on `.19` every figure the log reports is taken before the
  filter graph (`docs/KNOWN-ISSUES.md`). `.20` measures the loudness figures on
  the delivered audio (`cc79c5b`), so `.20`'s run of P3 is that change's test.
- **Section A**: `cyanrip --version` exited 0 in 0.4 s, and Platterpus's wrapper
  probe found all four paths exit within 0.3 s.

### The cancel: the rescue's signal was the first one cyanrip received

Section I cancelled at 22:44:57.041 host time, 90 s into track 1. Platterpus's
app log (`03platterpus/log.txt.1:22161-22170`) then shows:

| host time | |
|---|---|
| 22:44:57.041 | SIGTERM sent, *"user cancel"* |
| ≈22:44:57.0 | the host wrapper exits: the settle line below puts the footer *"5.3s after the wrapper exited"* |
| 22:45:01.791 | the post-cancel rescue: *"device-scoped SIGTERM to whatever holds /dev/sr0"* |
| 22:45:01.978 | `fuser -k TERM /dev/sr0 rc=0`: a process still held the drive, and was signalled |
| 22:45:02 | cyanrip's footer, `Ripping finished at 2026-10-04T22:45:02-04:00` (`rips/cancel-me.log`) |
| 22:45:02.300 | *"gained its completion footer 5.3s after the wrapper exited"* |

**On `.19` a second signal `_exit()`s with no footer**
(`cyanrip@174a134:src/cyanrip_main.c:1216-1221`), and this log has its footer,
signed. So cyanrip received exactly one signal before writing it. That signal
arrived after 22:45:01.978, when the drive was still held, and the footer
followed within about 0.3 s. **The cancel's own SIGTERM stopped at the host
wrapper and never reached cyanrip; the rescue's was the first and only signal
cyanrip received, and it is what ended the rip.** That is what
`platterpus@0981c69:src/platterpus/drive_control.py:58-68` already says, *"the
in-container reader typically writes its completion footer because this rescue
fires (measured 2026-09-09: rescue at +4.9 s, footer at +6.6 s)"*, and it makes
our reading of 2026-10-04 wrong: that README called the rescue *"a second TERM"*
and our held lap 9 drafted a finding on it. Both are corrected.

The one alternative this does not rule out is a second process holding
`/dev/sr0` at 22:45:01.978 and taking the rescue's signal, while cyanrip, given
the cancel's, took about 5 s to stop. Nothing in the bundle shows such a
process, and track 1 was reading at about 1.2x, a read every few milliseconds.

### Found on Platterpus's side, for them to weigh

- **Their stdout capture drops every track's outcome line.** The capture carries
  each track's block, from `Summary:` on, and never its `Track N read
  successfully!`; the app log has the same gap. In their worker a finished-track
  line is classified as a progress redraw
  (`platterpus@0981c69:src/platterpus/workers/rip_worker.py:3348-3352`), a redraw
  is not retained (`:2236-2243`), and it reaches the app log only when 0.1 s has
  passed since the last redraw, which is how one line of six app logs carries
  it (`05platterpus/log.txt.3:879`). Their report describes the capture as
  *"complete even when the ripper was killed"*. **It is the only record of a
  second pass, and from `.20` the outcome line is the one that says `read with
  errors.`** Unchanged at `platterpus@5ec71f4e`.
- **No `-j` record in the bundle**, again. Every Platterpus rip passed `-j`
  (`rips/full-acceptance-angle-bracket.log:2`, `-j
  cyanrip-diagnostics-20261005T010902Z.json`), so each record was written; none
  was collected. On 2026-10-04 we reported the same gap from three bundles.
- **A second pass's own log is not bundled**, only the stdout capture, so the
  record of the reads a dynamic re-rip would swap in cannot be checked with
  `cyanrip -Y`.

### Not established

- What the re-read at 256 sectors cost in section P, beyond at least 76.05 ms.
- Whether `.20`'s probe would have stopped at 256: it retries a slow re-read
  twice more, and this run made no such retries.
- Whether section F's second pass wrote a signed footer: its log is not in the
  bundle, and the capture ends `Ripping finished at 2026-10-04T22:37:07-04:00`
  without a `Log FUN512:` line, which goes to the logfile alone.
