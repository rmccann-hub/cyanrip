# Rig session 2026-09-17 — build `fe4d2c4`, Platterpus 0.6.50

**Read the build, not the date.** Two sessions ran on 2026-08-04 and calling both
"the 2026-08-04 session" is how a claim about one came to be checked against the
other's log. This one is `fe4d2c4`, and **that is the finding rather than a
label** — see below.

## Provenance

| | |
|---|---|
| bundle | `platterpusbundle20260917t024405z.tar.gz`, handed over by the operator |
| sha256 | `d8037c57291f93f322b178c84d2208f883ff6aef2de3542479fb234574dfa4db` |
| size | 11,284,966 bytes, 277 entries |
| session stamp | `20260917T024405Z` |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), `/dev/sr0` |
| disc | The Police, 14 tracks, MusicBrainz `65282302-368b-4ba2-953a-483bcdef2410` |
| ripper | `cyanrip 0.9.4-rc2+platterpus.12 (platterpus-fork-gfe4d2c4)` |
| consumer | `platterpus/0.6.50` |

**Everything filed here is byte-identical to a file in that tarball**, checked by
hashing all 78 distinct bundle objects and requiring each filed file to match
one. Not filed: 229 screenshots, and the eight `.platterpus.json` records, which
are 12 MB and are Platterpus's own artifact rather than ours. The tarball's
sha256 is recorded above so the unfiled remainder stays verifiable.

## The finding: this session ran on the RELEASE pin, not the TEST pin

Round 21 §0.1 asks for **one hardware acceptance session on `3952c03`**. Every
one of the eight rips here reports:

```
cyanrip 0.9.4-rc2+platterpus.12 (platterpus-fork-gfe4d2c4)
Handshake:      round 16 lap 17 closed, verdict GO -- released build
Frame retries:  3
```

`fe4d2c4` is `HANDSHAKE-PIN`, the **release** pin. `3952c03` is
`HANDSHAKE-TEST-PIN`. Zero logs contain `Retry limit:`; all eight carry the old
`Frame retries:`.

**The `Handshake:` line is what makes this checkable, and it did the job it was
built for.** It names *round 16 lap 17*, and a build from a tree with an open
round says `NOT a released build` instead. Nobody had to remember which build the
rig held — every rip on disk says so permanently.

### Against §0.1's three things

| | established | evidence |
|---|---|---|
| 1. the `fast_verified` whole-disc path runs on hardware | **yes** | `rips/full-acceptance-angle-bracket-2.log`, `rip_goal: fast_verified`, `Rip completed:  yes (14 of 14 tracks)`. **The `-2` is the whole-disc run** — the bundle gave two scenarios the same name and the suffix here was assigned by directory order, not by which ran first, so the name carries no meaning and the mapping below was re-derived by content hash. |
| 2. their parser reads `Retry limit:` on real logs | **no** | the label does not exist in this build |
| 3. `Ripping errors:` on a real session is the moved field | **no** | `fe4d2c4` prints the footer above the encoder-status loop |

**One of three.** Items 2 and 3 are precisely the two changes that exist only in
`3952c03`, so no re-reading of these logs can reach them. Item 1 is about
Platterpus's own section-F fix and does not depend on our build, which is why it
survives the pin mismatch.

### Where the datum was, and what nobody joined it to

**Their derivation is not missing — it is correct, and it was not consulted.**
Read at `platterpus@5aeffe9:src/platterpus/deps/fork_source.py` (this section
first cited `deps/fork_source.py`, which is the wrong path and the weaker claim):

```python
508:  PIN_UNDER_REVIEW: Final[str] = "fe4d2c4"
697:  FORK_TEST_PIN:    Final[str] = "3952c03"
1178: def pin_the_rig_should_install() -> str:
1193:     return FORK_TEST_PIN if rig_installs_the_test_pin() else PIN_UNDER_REVIEW
1224:     return a_round_is_reviewing_a_build() and not same_commit(
1225:         FORK_TEST_PIN, PIN_UNDER_REVIEW)
```

Round 21 is open and the two pins differ, so `pin_the_rig_should_install()`
returns **`3952c03`**. The rig ran `fe4d2c4`, and this session's own
`session/rig-check-ripper-version.txt` recorded that. **Both values were present
in one session and nothing compared them** — the shape Platterpus named in their
round-21 lap 2 §C, one level up from a log line.

Their own docstring names the failure class, and is more precise about it than we
would have been: round 16's two candidates were behaviourally identical
(*"`git diff a9aedf0..ddc1e8c -- src/ meson.build` is empty"*), so a mix-up then
would have cost *"the artifact's provenance … the mis-pairing class this module
exists to prevent rather than a wasted night."* **This time it is both**, because
`fe4d2c4` and `3952c03` differ by exactly the two changes the round is
reviewing.

## What it established that nothing asked for

**A SIGTERM that reached the process mid-rip**, on the `fast_verified` goal:

```
rips/cancel-me.log
  Ripping errors: 1
  Rip completed:  no (interrupted by SIGTERM, 0 of 14 tracks)
```

This is the interrupt footer, not the abort footer — a different path. Three
earlier folders named for a cancel never exercised it: two finished normally and
one ran 15m33s past the signal because it went to a distrobox wrapper. **A folder
name is not evidence**; this one is, because the footer says what happened.

## The eight rips

| file | goal | completed | errors |
|---|---|---|---|
| `secure-reread` | `archival` | yes (14 of 14) | 0 |
| `full-acceptance-angle-bracket-2` | `fast_verified` | **yes (14 of 14)** | 0 |
| `full-acceptance-angle-bracket` | `fast_verified` | yes (2 of 14) | 0 |
| `cancel-me` | `fast_verified` | **no (interrupted by SIGTERM, 0 of 14)** | **1** |
| `after-cancel` | `fast_verified` | yes (2 of 14) | 0 |
| `derived-wav` | `custom` | yes (2 of 14) | 0 |
| `derived-wavpack` | `custom` | yes (2 of 14) | 0 |
| `derived-mp3` | `portable` | yes (2 of 14) | 0 |

`Read stalls:    none (no read exceeded 10s)` on all eight — expected on healthy
media, and **not evidence either way** about the watchdog.

## `-x` ran, on a rip that is not in the eight

**This README first said `-x` was not run.** That was derived from the eight
album rips' `Invoked as:` lines, and the probe ran on a rip they do not contain —
a different disc, CDDB `E20DFE0E`, `Total time: 59:42.57`, recorded in
`session/transcript.txt`. Caught by `sc_cache_table_matches_the_transcripts()`,
which counted nine sessions with a probe line against eight table rows. **A
filtered view of an artifact is not the artifact**, and here the filter was our
own choice of which files to read.

```
Cache probe:    at least 2048 sectors, upper bound unknown (4704.0 KiB or more,
                search ceiling reached, uncached read 362.8 ms, cached read 62.2 ms)
```

**The ninth session to report `at least 2048 sectors`**, and the ninth to report
a figure `cd-paranoia -A` puts at 137–140 on the same drive. Filed as a row in
`docs/KNOWN-ISSUES.md`: 362.8 ms uncached, 62.2 ms cached, 90.7 ms threshold,
69% margin.

**§4b's ask is still unmet, and the build is why.** What it wanted was the
*series* — the calibration reads, the median that became the threshold, and one
entry per run with what the rule scored it. That block lives in `-j` at
`cyanrip-diagnostics/6`, which exists only in `3952c03`. All eight album rips
passed `-j` and got the older schema. So the probe ran, the series was not
recorded, and the wrong build cost this as well as §0.1's items 2 and 3.
`docs/ROUND-22-PLAN.md` §2 stays gated.

## Rename mapping

**Backfilled 2026-09-29**, derived by hashing each file filed here against
the members of `platterpusbundle20260917t024405z.tar.gz`; round 16 lap 14 §C's rule, which this filing
had not followed until then. The first column is how the file is filed
here, the second how it was delivered.

| filed here | as delivered in their bundle | sha256/16 |
|---|---|---|
| `after-cancel.cue` | `album/after cancel 20260917t024405 platterpus-fork-gfe4d2c4/after cancel 20260917t024405 platterpus-fork-gfe4d2c4.cue` | `79dcf34f55d9b9af…` |
| `after-cancel.eac.log` | `album/after cancel 20260917t024405 platterpus-fork-gfe4d2c4/after cancel 20260917t024405 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `ad12781954cf1817…` |
| `after-cancel.log` | `album/after cancel 20260917t024405 platterpus-fork-gfe4d2c4/after cancel 20260917t024405 platterpus-fork-gfe4d2c4.log` | `8648baaf49d96c84…` |
| `cancel-me.cue` | `album/cancel me 20260917t024405 platterpus-fork-gfe4d2c4/cancel me 20260917t024405 platterpus-fork-gfe4d2c4.cue` | `6ef66a1ec4fb691c…` |
| `cancel-me.eac.log` | `album/cancel me 20260917t024405 platterpus-fork-gfe4d2c4/cancel me 20260917t024405 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `d6aa2df654615b4b…` |
| `cancel-me.log` | `album/cancel me 20260917t024405 platterpus-fork-gfe4d2c4/cancel me 20260917t024405 platterpus-fork-gfe4d2c4.log` | `cc313b326ada4e1d…` |
| `derived-mp3.cue` | `album/derived mp3 20260917t024405 platterpus-fork-gfe4d2c4/derived mp3 20260917t024405 platterpus-fork-gfe4d2c4.cue` | `d9ec0750b316c337…` |
| `derived-mp3.eac.log` | `album/derived mp3 20260917t024405 platterpus-fork-gfe4d2c4/derived mp3 20260917t024405 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `035bf92e09b3106c…` |
| `derived-mp3.log` | `album/derived mp3 20260917t024405 platterpus-fork-gfe4d2c4/derived mp3 20260917t024405 platterpus-fork-gfe4d2c4.log` | `14dbc068a3598098…` |
| `derived-wav.cue` | `album/derived wav 20260917t024405 platterpus-fork-gfe4d2c4/derived wav 20260917t024405 platterpus-fork-gfe4d2c4.cue` | `45e11d3837db790b…` |
| `derived-wav.eac.log` | `album/derived wav 20260917t024405 platterpus-fork-gfe4d2c4/derived wav 20260917t024405 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `f6fd811d0f5dc7b0…` |
| `derived-wav.log` | `album/derived wav 20260917t024405 platterpus-fork-gfe4d2c4/derived wav 20260917t024405 platterpus-fork-gfe4d2c4.log` | `e0ee720dd053912b…` |
| `derived-wavpack.cue` | `album/derived wavpack 20260917t024405 platterpus-fork-gfe4d2c4/derived wavpack 20260917t024405 platterpus-fork-gfe4d2c4.cue` | `b6565672adacb2ce…` |
| `derived-wavpack.eac.log` | `album/derived wavpack 20260917t024405 platterpus-fork-gfe4d2c4/derived wavpack 20260917t024405 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `160758f8879b4112…` |
| `derived-wavpack.log` | `album/derived wavpack 20260917t024405 platterpus-fork-gfe4d2c4/derived wavpack 20260917t024405 platterpus-fork-gfe4d2c4.log` | `f13f94e1591c4a01…` |
| `full-acceptance-angle-bracket-2.cue` | `album/full acceptance_ angle_bracket 20260917t02__terpus-fork-gfe4d2c4/full acceptance∶ angle‹bracket 20260917t024405 platterpus-fork-gfe4d2c4.cue` | `02591046b899fb9d…` |
| `full-acceptance-angle-bracket-2.eac.log` | `album/full acceptance_ angle_bracket 20260917t02__terpus-fork-gfe4d2c4/full acceptance∶ angle‹bracket 20260917t024405 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `8eb93743facbf63f…` |
| `full-acceptance-angle-bracket-2.log` | `album/full acceptance_ angle_bracket 20260917t02__terpus-fork-gfe4d2c4/full acceptance∶ angle‹bracket 20260917t024405 platterpus-fork-gfe4d2c4.log` | `d41efe6ab74b6268…` |
| `full-acceptance-angle-bracket.cue` | `album/full acceptance_ angle_bracket 20260917t02__us-fork-gfe4d2c4 _2_/full acceptance∶ angle‹bracket 20260917t024405 platterpus-fork-gfe4d2c4.cue` | `9dec8c55904fbc2c…` |
| `full-acceptance-angle-bracket.eac.log` | `album/full acceptance_ angle_bracket 20260917t02__us-fork-gfe4d2c4 _2_/full acceptance∶ angle‹bracket 20260917t024405 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `6a836a567cf01842…` |
| `full-acceptance-angle-bracket.log` | `album/full acceptance_ angle_bracket 20260917t02__us-fork-gfe4d2c4 _2_/full acceptance∶ angle‹bracket 20260917t024405 platterpus-fork-gfe4d2c4.log` | `3f2993060073d11e…` |
| `secure-reread.cue` | `album/secure reread 20260917t024405 platterpus-fork-gfe4d2c4/secure reread 20260917t024405 platterpus-fork-gfe4d2c4.cue` | `1671c7b9a0888b93…` |
| `secure-reread.eac.log` | `album/secure reread 20260917t024405 platterpus-fork-gfe4d2c4/secure reread 20260917t024405 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `d6c94bbf0c46437a…` |
| `secure-reread.log` | `album/secure reread 20260917t024405 platterpus-fork-gfe4d2c4/secure reread 20260917t024405 platterpus-fork-gfe4d2c4.log` | `b70c68fee7452358…` |
| `session/DIAGNOSTICS.txt` | `DIAGNOSTICS.txt` | `8b7efe994e6ca6ad…` |
| `session/MANIFEST.txt` | `MANIFEST.txt` | `923406f912afe493…` |
| `session/SOURCES.txt` | `SOURCES.txt` | `9e165df90771dfe4…` |
| `session/config.toml` | `session/artifacts/09platterpus/config.toml` | `1eea184c717254a3…` |
| `session/rig-check-argv-probe-output.txt` | `extra1020260917T024405_0000/rig-check/argv-probe-output.txt` | `b899e8dc08b2862d…` |
| `session/rig-check-argv-probe.json` | `extra1020260917T024405_0000/rig-check/argv-probe.json` | `a998a8fc6312e39f…` |
| `session/rig-check-manifest.txt` | `extra1020260917T024405_0000/rig-check/MANIFEST.txt` | `d6bd88e21653c6c3…` |
| `session/rig-check-ripper-version.txt` | `extra1020260917T024405_0000/rig-check/ripper-version.txt` | `d85fa20181278240…` |
| `session/script-report.json` | `extra1020260917T024405_0000/report.json` | `2e0c9c8d389b4f90…` |
| `session/transcript.txt` | `session/transcript.txt` | `5c2c5cd63f5fd134…` |

`session/transcript.txt` is also byte-identical to the bundle's `extra1020260917T024405_0000/transcript.txt`.
