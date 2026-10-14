# Rig session 2026-10-04 — build `174a134`, Platterpus 0.6.65, three Full runs, **none complete**

**Read the build, not the date.** All three runs are `174a134`, `+platterpus.19`,
through Platterpus **0.6.65** (`0981c69`), the pair round 30 tested on
2026-09-30 (`docs/rig-2026-09-30b-174a134/`). `tools/ingest-bundle.py --peer`
reads it as the newest pair on both sides when each run began. **No new pair
existed**, so these runs are not a round's real test. They are further evidence
on the same pair, on three discs that are not the reference disc.

**No run's own verdict is a pass**, and the bundles say so: two stopped at
section E, `pass 107, fail 2, blocked 214`; the third was stopped from the
console in section N, `pass 252, fail 10, blocked 61`
(`session-*/script-report.json`, `session/script-report.json`).

## Provenance

| | |
|---|---|
| bundles | three, handed over by the operator: `platterpusbundle20261004t152045z.tar.gz` (sha256 `034682685559cfede1b68cd89fd32bd460f86340f587fd93f4b3a5eaa25f559d`, 3,139,178 bytes, 25 files), `platterpusbundle20261004t160027z.tar.gz` (`aeb66f4ed52c9d5bbc4fa22cb06c5bbaff50c935d0b4b4f6acb21ac4d6809bc9`, 3,119,311 bytes, 25 files) and `platterpusbundle20261004t160255z.tar.gz` (`d7881c27575d42b835f27a0796f4713e9d0e42ddd05f4ea9a79ea14c2fded888`, 6,397,797 bytes, 66 files). Each was uploaded more than once, and every copy hashed the same |
| sessions | `20261004T152045Z` → `session-152045z/`; `20261004T160027Z` → `session-160027z/`; `20261004T160255Z` → `session/` and `rips/`. Run size full in all three. Host time is UTC−4 |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| discs | **three, none the reference disc.** 152045z: DiscID `PKt4tUZ9zkm_5aEh6ButPQLlNs0-`, 16 tracks. 160027z: `83jwDRaSUuT.GTqbBXMLHeQRAKw-`, 11 tracks. 160255z: `zxtbw2JgJ.kZBiyIcKOQvn2ZTUM-`, 18 tracks, *Roots Music: An American Journey* (Rounder 11661-0501-2), medium 1 of 4, MusicBrainz release `53d0f596-95a3-4e60-b4aa-09f5f7532b1e` |
| ripper | `cyanrip 0.9.4-rc2+platterpus.19 (platterpus-fork-g174a134)`, in every log's banner and in each transcript's section A |
| consumer | `platterpus/0.6.65`, build `0981c69` (`session/COMPONENTS.json`) |

**Every file here but this README is byte-identical to a member of one of the
three tarballs**, hashed against its original when copied, with one exception
that is still checkable: `full-acceptance-angle-bracket.ripper-stdout.txt` is
Platterpus's capture of cyanrip's stdout for section F, taken from the
`artifacts.ripper_stdout.text` field of their `.platterpus.json` and written as
UTF-8. Its sha256 is the one that report records for it, so the bytes are the
ones their tool hashed. It is filed because it is the only record of the second
pass described below: that pass ran in a temporary directory and its own log is
not in the bundle.

| filed here | as delivered in their bundle | sha256/16 |
|---|---|---|
| `after-cancel.eac.log` | `160255z: album/after cancel 20261004t160255 platterpus-fork-g174a134/after cancel 20261004t160255 platterpus-fork-g174a134 CD1 (EAC-compatible).log` | `3e8ebcad6219dd8c…` |
| `after-cancel.cue` | `160255z: album/after cancel 20261004t160255 platterpus-fork-g174a134/after cancel 20261004t160255 platterpus-fork-g174a134 CD1.cue` | `9be78ad6111471e4…` |
| `after-cancel.log` | `160255z: album/after cancel 20261004t160255 platterpus-fork-g174a134/after cancel 20261004t160255 platterpus-fork-g174a134 CD1.log` | `70d4bd39259ac0a4…` |
| `derived-mp3.eac.log` | `160255z: album/derived mp3 20261004t160255 platterpus-fork-g174a134/derived mp3 20261004t160255 platterpus-fork-g174a134 CD1 (EAC-compatible).log` | `790a75eb66024d8c…` |
| `derived-mp3.cue` | `160255z: album/derived mp3 20261004t160255 platterpus-fork-g174a134/derived mp3 20261004t160255 platterpus-fork-g174a134 CD1.cue` | `6b9bc9abd3b6130b…` |
| `derived-mp3.log` | `160255z: album/derived mp3 20261004t160255 platterpus-fork-g174a134/derived mp3 20261004t160255 platterpus-fork-g174a134 CD1.log` | `71fcc15f87260416…` |
| `derived-wav.eac.log` | `160255z: album/derived wav 20261004t160255 platterpus-fork-g174a134/derived wav 20261004t160255 platterpus-fork-g174a134 CD1 (EAC-compatible).log` | `7549e1bdff008799…` |
| `derived-wav.cue` | `160255z: album/derived wav 20261004t160255 platterpus-fork-g174a134/derived wav 20261004t160255 platterpus-fork-g174a134 CD1.cue` | `46d4640d6876193f…` |
| `derived-wav.log` | `160255z: album/derived wav 20261004t160255 platterpus-fork-g174a134/derived wav 20261004t160255 platterpus-fork-g174a134 CD1.log` | `56f113e0569c763c…` |
| `derived-wavpack.eac.log` | `160255z: album/derived wavpack 20261004t160255 platterpus-fork-g174a134/derived wavpack 20261004t160255 platterpus-fork-g174a134 CD1 (EAC-compatible).log` | `bf27a3ca0229fbd7…` |
| `derived-wavpack.cue` | `160255z: album/derived wavpack 20261004t160255 platterpus-fork-g174a134/derived wavpack 20261004t160255 platterpus-fork-g174a134 CD1.cue` | `c04ae2052f37b719…` |
| `derived-wavpack.log` | `160255z: album/derived wavpack 20261004t160255 platterpus-fork-g174a134/derived wavpack 20261004t160255 platterpus-fork-g174a134 CD1.log` | `e558d7634a56b42b…` |
| `full-acceptance-angle-bracket.eac.log` | `160255z: album/full acceptance_ angle_bracket 20261004t16__terpus-fork-g174a134/full acceptance∶ angle‹bracket 20261004t160255 platterpus-fork-g174a134 CD1 (EAC-compatible).log` | `f5b9acc4506e01b5…` |
| `full-acceptance-angle-bracket.cue` | `160255z: album/full acceptance_ angle_bracket 20261004t16__terpus-fork-g174a134/full acceptance∶ angle‹bracket 20261004t160255 platterpus-fork-g174a134 CD1.cue` | `b3d9c864e7c59141…` |
| `full-acceptance-angle-bracket.log` | `160255z: album/full acceptance_ angle_bracket 20261004t16__terpus-fork-g174a134/full acceptance∶ angle‹bracket 20261004t160255 platterpus-fork-g174a134 CD1.log` | `15372c9cc33f6fec…` |
| `secure-reread.cue` | `160255z: album/secure reread 20261004t160255 platterpus-fork-g174a134/secure reread 20261004t160255 platterpus-fork-g174a134 CD1.cue` | `248d442185350150…` |
| `secure-reread.log` | `160255z: album/secure reread 20261004t160255 platterpus-fork-g174a134/secure reread 20261004t160255 platterpus-fork-g174a134 CD1.log` | `848fb243d2d5b285…` |
| `full-acceptance-angle-bracket.ripper-stdout.txt` | `160255z: album/full acceptance_ angle_bracket 20261004t16__terpus-fork-g174a134/full acceptance∶ angle‹bracket 20261004t160255 platterpus-fork-g174a134 CD1.platterpus.json, field artifacts.ripper_stdout.text` | `0f1a033bf2103141…` |
| `session/transcript.txt` | `160255z: session/transcript.txt` | `005c73757af6a6c6…` |
| `session/script-report.json` | `160255z: session/run/report.json` | `7c8b727a72a17ea9…` |
| `session/MANIFEST.txt` | `160255z: MANIFEST.txt` | `f848aee6ee765796…` |
| `session/COMPONENTS.json` | `160255z: COMPONENTS.json` | `36750ddc3ef0a759…` |
| `session/DIAGNOSTICS.txt` | `160255z: DIAGNOSTICS.txt` | `223b6d3ae4d67c0c…` |
| `session/SETTINGS.json` | `160255z: SETTINGS.json` | `6d5726cad6e6cab6…` |
| `session/SOURCES.txt` | `160255z: SOURCES.txt` | `1fbad15fdbe1b141…` |
| `session/config.toml` | `160255z: session/artifacts/08platterpus/config.toml` | `8d816eea558fa8c8…` |
| `session/rig-check-manifest.txt` | `160255z: session/run/rig-check/MANIFEST.txt` | `d5c892d3a3581b4c…` |
| `session/rig-check-argv-probe-output.txt` | `160255z: session/run/rig-check/argv-probe-output.txt` | `03f6b131d7d2b2b9…` |
| `session/rig-check-argv-probe.json` | `160255z: session/run/rig-check/argv-probe.json` | `eefbfbe4c46b1327…` |
| `session/rig-check-ripper-version.txt` | `160255z: session/run/rig-check/ripper-version.txt` | `3dd6fb1ac56dbfad…` |
| `session-152045z/transcript.txt` | `152045z: session/transcript.txt` | `b3b7406de057c059…` |
| `session-152045z/script-report.json` | `152045z: session/run/report.json` | `b7d613c094f313d2…` |
| `session-152045z/MANIFEST.txt` | `152045z: MANIFEST.txt` | `c0b77ae660271e3e…` |
| `session-152045z/COMPONENTS.json` | `152045z: COMPONENTS.json` | `9d8847c64622e8c3…` |
| `session-152045z/DIAGNOSTICS.txt` | `152045z: DIAGNOSTICS.txt` | `da63e2260f7706a0…` |
| `session-152045z/SETTINGS.json` | `152045z: SETTINGS.json` | `d476f416b418aec7…` |
| `session-152045z/SOURCES.txt` | `152045z: SOURCES.txt` | `84b41ce8be1f6ec8…` |
| `session-152045z/config.toml` | `152045z: session/artifacts/06platterpus/config.toml` | `8d816eea558fa8c8…` |
| `session-160027z/transcript.txt` | `160027z: session/transcript.txt` | `ac6e3e7e56529f68…` |
| `session-160027z/script-report.json` | `160027z: session/run/report.json` | `eb3e1af32d362cce…` |
| `session-160027z/MANIFEST.txt` | `160027z: MANIFEST.txt` | `746bd199285fccca…` |
| `session-160027z/COMPONENTS.json` | `160027z: COMPONENTS.json` | `5253f42f1f54edee…` |
| `session-160027z/DIAGNOSTICS.txt` | `160027z: DIAGNOSTICS.txt` | `7d24232578103ba4…` |
| `session-160027z/SETTINGS.json` | `160027z: SETTINGS.json` | `72437ea3761f3ed8…` |
| `session-160027z/SOURCES.txt` | `160027z: SOURCES.txt` | `c6944ee78a6227c5…` |
| `session-160027z/config.toml` | `160027z: session/artifacts/06platterpus/config.toml` | `8d816eea558fa8c8…` |

**Not filed**, with sha256/16 so each stays checkable against its tarball: the
48 screenshots (12 in each stopped run, 24 in the third); the six
`.platterpus.json` reports, Platterpus's artifact (`785dbd300db548dc` after
cancel, `5e350794ce9cbb72` derived mp3, `319d2843f6cb3f28` derived wav,
`82749de2935e453e` derived wavpack, `d658601b45b329e8` full acceptance, 7,308,860
bytes, and `8f3c4dc29e96de07` secure reread); each run's duplicate
`session/run/transcript.txt`, byte-identical to its `session/transcript.txt`;
and the app logs, of which the readings below cite these:
160255z `session/artifacts/02platterpus/log.txt` (4,857,449 bytes,
`732f9e86403b7db6`), 160255z `session/zz-applog-rotations/03platterpus/log.txt.1`
(8,388,572 bytes, `102ca6638f2dccda`), 160255z
`session/zz-applog-rotations/04platterpus/log.txt.2` (8,388,557 bytes,
`d81ebcfa49ecd224`), and the newest logs of the stopped runs,
152045z (6,821,238 bytes, `96cecf8ac1283bb6`) and 160027z (6,837,699 bytes,
`bd6ef7a75e5b2663`). The other rotations are older and hold no 2026-10-04 line
the readings use. Line numbers below are in those files as delivered.

## Our reading

### The two runs that stopped at section E: discs MusicBrainz does not have

Both identified the drive, passed sections A to D, then read a disc MusicBrainz
returned no release for. Platterpus showed *Rip as unknown album*, and its own
guard stopped the run (`session-152045z/transcript.txt:326-343`; the same lines
of 160027z run four later). cyanrip's part was `cyanrip -I -N -d /dev/sr0`,
which read 16 tracks and the disc ID `PKt4tUZ9zkm_5aEh6ButPQLlNs0-` in the first
(152045z app log `:60185`), and 11 tracks and `83jwDRaSUuT.GTqbBXMLHeQRAKw-` in
the second (160027z app log `:60317`).

**Both disc IDs are absent from MusicBrainz**, checked by us on 2026-10-05 with
one request each to `musicbrainz.org/ws/2/discid/<id>`: `404 Not Found` for
both, while the reference disc's `pNtImOkdBm9RMBIalzx0w9cfsYY-`, asked the same
way as a control, returned its release. So *"not in MusicBrainz"* reports
MusicBrainz's answer correctly. **What the bundles cannot settle** is whether
MusicBrainz holds either disc under a different ID, which would mean ours was
computed wrongly. That needs the disc's TOC, and neither bundle carries the
`-I` output.

**A fourth attempt is in the app log and not in any bundle**: session
`20261004T151939Z`, a minute before 152045z, on the 16-track disc, stopped the
same way and wrote `platterpusbundle20261004t151939z.tar.gz`, which was not
handed over (152045z app log `:59929`, `:60039`, `:60046`).

Neither run's step L463 is right about itself: it passed with *"the disc
identified unambiguously, so there was nothing to pick"* over a disc that was not
identified at all, and L464 and L473 then failed. The cause, read in their code
at the build that ran: with no picker on screen, the step passes as soon as any
track rows are loaded (`platterpus@0981c69:src/platterpus/uiscript/runner.py:3327-3335`),
and an unknown disc loads placeholder rows too. It checks no MusicBrainz release
ID, which `expect-identified` does. That is Platterpus's step to fix.

**At app start their version probe timed out after 60 s** (152045z app log
`:59918`), *"keeping the 99 character(s) it had already written"*, and it parsed
version 0.9.4 from them, so our banner had arrived. `cyanrip --version` on
`174a134`, measured here, prints 59 bytes and exits 0 in about 0.05 s with stdin
open or closed. It returns inside option parsing
(`cyanrip@174a134:src/cyanrip_main.c:1716`), before libcdio or the drive are
touched (`:2112`). So the other 40 bytes, and the wait, came from between their
probe and our process, most likely the container wrapper on its first start of
the session, which a `cyanrip -I` launched in the same second was also starting
(`:59910`). Later probes returned in under a second.

In 160027z the snapshots read `read offset: —` and `cache defeat: —`, where the
runs either side of it read `+667 — confirmed` on the same drive. That run's
disc was unknown. Why their display changed is theirs to say; nothing in our
logs bears on it.

### The third run: what happened, in UTC

| when | what | where |
|---|---|---|
| 16:03:36 | section F starts a whole-disc rip, no `-Z`, `-r 5` (`fast_verified`, dynamic re-read) | 160255z `04…log.txt.2:60476`; `rips/full-acceptance-angle-bracket.log:2` |
| 16:03 → 16:50 | tracks 1 to 17 read, 98 to 325 s each, 1.0x to 1.2x | the log's `Elapsed:` lines |
| 16:50 → 19:06:22 | **track 18 alone takes 8,161 s** | `rips/full-acceptance-angle-bracket.log:1414` |
| 19:06:23 | Platterpus starts a second cyanrip, `-Z 2 -l 12,13,14,15,17,18`: the six tracks that matched AccurateRip only on frame 450 | 160255z `03platterpus/log.txt.1:15867`; `rips/…ripper-stdout.txt:2983` |
| 19:14 → 20:33 | tracks 12, 13, 14, 15 and 17 each end `did NOT converge after 5 reads (repeat limit hit)` | `rips/…ripper-stdout.txt:3081`, `:3171`, `:3261`, `:3351`, `:3481` |
| 22:03:36 | section F's 6-hour wait expires, the second pass still on track 18; sections G and H run against a rip still in progress | `session/transcript.txt:385`; `03…log.txt.1:57829` |
| 23:07:10 | section I's cancel sends SIGTERM; 0.6 s later Platterpus logs `rip finished: success=True` for the album, noting the reaped process was the host wrapper | `03…log.txt.1:59790`, `:59794`, `:59795` |
| 23:07:15 | Platterpus's *post-cancel rescue* sends `fuser -k TERM /dev/sr0` to whatever holds the drive, 4.9 s after the cancel; `rc=0`, so a process still held it. **Corrected 2026-10-05**: this row said *"a second TERM"*. On this rig the cancel's TERM stops at the host wrapper, so the rescue's is most likely the first cyanrip received (`docs/rig-2026-10-05-174a134/README.md`) | `03…log.txt.1:59806-59807` |
| 23:07:57 | section J's two-track rip starts and opens the drive | `03…log.txt.1:59836` |
| 23:33:35 → 01:01:00 | section N reads the whole disc at `-Z 2`: tracks 1 to 10 each `converged after 3 reads`; track 11's four passes give four checksums | `03…log.txt.1:71329`; `rips/secure-reread.log` |
| 01:01:01 | the script is stopped from the console, and the bundle is written in the same second | 160255z `02platterpus/log.txt:43366` |

### Every cyanrip log

**Five of six verify** against their own checksum with `cyanrip -Y` built from
`174a134` (exit 0): the whole-disc rip, `after-cancel` and the three derived
rips. Each ends `Ripping errors: 0` and `Rip completed:  yes`, and each two-track
rip's tracks 1 and 2 read `A0E382F5` and `ABC106DC`, the whole-disc rip's
checksums, AccurateRip-accurate at confidence 29.

**`secure-reread.log` has no footer** (`-Y` exit 3, *"No FUN512 checksum
found"*): 909 lines, ending in track 11's fourth repeat pass. **It was copied
while cyanrip was still writing it.** Its last line is the app log's line at
01:01:00.985 (`02platterpus/log.txt:43365`); the script ended 0.8 s later
(`:43366`); the bundle was written then; and no line in between signals or
reaps the ripper. The operator closed both programs before sending the bundle,
but the bundle already held the copy. Whether that rip went on to write its
footer is on the rig's disk, in the same log, and not in the bundle.
`tools/ingest-bundle.py` now names every log that did not reach a signed footer,
with this distinction (`acfd48b`).

**The second pass's own log is not in the bundle.** Platterpus runs a re-read in
a throwaway directory (`platterpus@0981c69:src/platterpus/workers/rip_worker.py:2790-2791`),
so what our process wrote after the SIGTERM at 23:07:10 is not here. The
captured stdout stops at *"Still reading track 18 - the read for LSN 247049 has
not returned after 20s"* (`rips/…ripper-stdout.txt:5064`): the capture ends
there because the host wrapper exited at the cancel. Our handler `_exit(1)`s on a
second signal (`cyanrip@174a134:src/cyanrip_main.c:1219-1220`), and this said the
rescue's TERM, 4.9 s later, was that second signal. **Corrected 2026-10-05**: the
next run's cancel shows the cancel's TERM stopping at the host wrapper and the
rescue's being the first signal cyanrip receives
(`docs/rig-2026-10-05-174a134/README.md`), which is what
`platterpus@0981c69:src/platterpus/drive_control.py:58-68` says. Here the rescue
found the drive still held, mid-way through a read that had not returned after
20 s, and cyanrip stops only once its read returns. So whether that log was
signed, and when that process ended, **still cannot be established from this
bundle.**

### The disc did not read the same twice from track 11 on

The reference disc does not read the same twice on two tracks (3 and 5); this
disc does not on seven. **It is the first filed rip in which paranoia skipped
anything**: no earlier filed log records a `SKIP` above 0, and the most atom
fixups any records is 126 (`docs/rig-2026-09-03-978f9b0/rips/secure-reread.log`),
against 73,012,166 here. So it shows how this drive behaves on media it cannot
read reliably:

| track | first pass, s | AccurateRip, whole track | FIXUP_ATOM | SKIP | `-Z 2` pass |
|---|---|---|---|---|---|
| 1–10 | 115–208 | match, confidence 29 (track 9: 28) | 0 | 0 | section N: converged after 3 reads |
| 11 | 158.50 | match, 29 | 28 | 0 | section N: 4 passes, 4 checksums when the bundle was written |
| 12 | 98.39 | **no**; frame 450 matches at 28 | 52,936 | 0 | 5 reads, 5 checksums, limit hit |
| 13 | 157.86 | **no**; 450 at 29 | 18,891 | 0 | 5 reads, 5 checksums, limit hit |
| 14 | 324.52 | **no**; 450 at 29 | 8,275 | 0 | 5 reads, 5 checksums, limit hit |
| 15 | 215.00 | **no**; 450 at 29 | 85,969 | 0 | 5 reads, 5 checksums, limit hit |
| 16 | 137.94 | match, 29 | 204 | 0 | not re-read |
| 17 | 167.65 | **no**; 450 at 29 | 5,577 | 0 | 5 reads, 5 checksums, limit hit |
| 18 | **8,161.25** | **no**; 450 at 28 | **72,840,286** | **2,586** | interrupted by section I's cancel |

- **The drive never reported an error.** No `cdio error` or `Frame read failed`
  line appears in any filed log or in the captured output, and every log with a
  footer says `Ripping errors: 0`. C2 is unsupported, so the
  drive said nothing about these sectors either way.
- **It was slow instead.** `Read stalls:    279 reads exceeded 10s; longest 54s
  (track 18, LSN 257082)` (`rips/full-acceptance-angle-bracket.log:1501`). The
  longest read in any log filed in this repository until now was 21 s, on the
  same drive.
- **A frame-450 match beside a whole-track miss, at the same confidence as the
  tracks that match, is not a different pressing here**: each of tracks 12 to 15
  and 17 was read five times in the second pass with five distinct checksums
  (`rips/…ripper-stdout.txt:3041` to `:3481`), so the bytes are what changes.

**And every one of those tracks printed `Track N read successfully!`**, track 18
included, over 2,586 SKIPs. That line tells the reader the drive returned no
error and nothing was counted in `Ripping errors:`. It does not say paranoia
verified the data, and here it plainly had not. The condition is upstream's
(`ctx->total_error_count - start_err`, `cyanrip@174a134:src/cyanrip_main.c:1128`,
and `:911` at upstream's `f8ebf48`), and the line's meaning is a contract question, so it is
recorded in `docs/KNOWN-ISSUES.md` for round 31 rather than changed now. The
footer's `Tracks ripped partially accurately: 6/18` (`:1489`) is the
`partially-accurate-tally-label` item in `STATUS.md` meeting its first real disc.

### `.19`'s changes, on a drive

- **The reworded repeat-limit line, printed for the first time**: `Done;
  (repeat limit of 5 reads reached; at most 1 read agreed)`, five times
  (`rips/…ripper-stdout.txt:3041` the first), each followed by `EAC CRC32: …
  (after 5 rips)` and `Secure re-read:  did NOT converge after 5 reads (repeat
  limit hit)`. Earlier builds hit the limit in fourteen filed logs, worded
  `Done; (no matches found, but hit repeat limit of 3)`; no `.19` run had
  reached it.
- **The loop's checksum is the track's EAC CRC32** in section N, tracks 1 to 10:
  each `Done; (2 out of 2 matches for current checksum X)` names its block's
  value.
- **Tag keys in capitals** with `DISCTOTAL` beside `TOTALDISCS`, in every
  `Metadata:` block, each run passing `-c 1/4`.

### Found in Platterpus's side, for them to weigh

- **A cancelled re-read reported as a clean rip.** After section I's cancel the
  status line read *"Done — all 18 tracks ripped cleanly, no read errors"*, from
  the first pass's log. Their report says `status: "cancelled"` beside
  `health_status: "No errors occurred"`, and their own L711 failed on it.
- ~~**The cancel's rescue sends a second TERM 4.9 s after the first**, while
  this disc's reads took up to 54 s, and a second signal ends cyanrip without
  its footer.~~ **Withdrawn 2026-10-05.** The cancel's TERM stops at the host
  wrapper, so the rescue's is the first signal cyanrip receives; the 2026-10-05
  run shows it (`docs/rig-2026-10-05-174a134/README.md`), and their own comment
  at `platterpus@0981c69:src/platterpus/drive_control.py:58-68` said so before
  we wrote this. Our held round 30 lap 9 drafted a finding on it, removed before
  release.
- **That grace's floor test reads their tree's filed logs**: twice this run's 54 s
  is 108 s, against the 40 s it sets.
- **The re-read path's docstring still says `HARDWARE-GATED … not been exercised
  on a real drive yet`** (`rip_worker.py:2795` at `0981c69`): this run exercised
  it, and no track converged.
- **A bundle written while the ripper was still running** says only *"stopped
  from the console"*. Their bundle could say the ripper was still running, or
  wait for it to finish.
- **No `-j` record is in any of the three bundles**, for any rip, and none is
  named as missing. Their bundler collects a record only when its caller names
  it (`platterpus@0981c69:src/platterpus/evidence_bundle.py:534-546`), and the
  acceptance session names none. cyanrip writes that record through `atexit`,
  with its exit code and whether and how the rip was interrupted, so it is the
  record of how each ripper ended. Its absence beside a footerless log would
  have said the process had not exited.

### Not established

- Whether either unknown disc is in MusicBrainz under another ID: the TOCs are
  not in the bundles.
- Whether section N's rip and the cancelled second pass wrote their footers.
- Anything about the cache probe, sections O to P3: the run was stopped in N.
