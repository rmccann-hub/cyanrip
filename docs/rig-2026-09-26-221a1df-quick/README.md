# Rig session 2026-09-26 — build `221a1df`, Platterpus 0.6.60, a QUICK run

**Read the build, not the date.** This is `221a1df`, `+platterpus.16`: the
release, and round 27's reviewed pin. The one rip, the argv probe and
`session/rig-check-ripper-version.txt` all say `platterpus-fork-g221a1df`.

**A quick run, not the Full acceptance, and its own report says it is not
evidence** (`session/report.json`: `run_size: quick`, `counts_as_evidence:
false`). Round 27 lap 1 §0.1 asked for the Full run. The operator chose, on
2026-09-26, to close round 27 without a Full or Standard run and to test both
projects' next releases together in round 28. So this is the only drive
evidence round 27 has. Our lap 4 records that as an override of R1.

## Provenance

| | |
|---|---|
| bundle | `platterpusbundle20260926t000413z.tar.gz`, handed over by the operator |
| sha256 | `827d43da95f4dfe150e70900b56d5e96163cff41f7a6e117819760970e9cc4e0` |
| size | 1,656,589 bytes, 29 files, 13 of them screenshots |
| session stamp | `20260926T000413Z` |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), `/dev/sr0` |
| disc | The Police, *Every Breath You Take: The Classics*, 14 tracks, MusicBrainz `65282302-368b-4ba2-953a-483bcdef2410` |
| ripper | `cyanrip 0.9.4-rc2+platterpus.16 (platterpus-fork-g221a1df)` |
| consumer | `platterpus/0.6.60` (build `88c09dd`, their `v0.6.60` tag) |
| script | `fullacceptance.txt` at size `quick`, 320 steps |
| outcome | **pass 206, fail 0, error 0, skipped 114, blocked 0, unreachable 0, info 1**. All 114 skips are `declined_by_size: true` |

**Every file here is byte-identical to a file in that tarball**, checked by
hashing each source and each copy, 15 of 15. The tarball holds
`session/transcript.txt` and `session/run/transcript.txt`, which are identical,
so it is filed once. Not filed: the 13 screenshots. Their sha256/16, in the
tarball's `session/run/` order: `75ff5d221debb054` `c0639b3d7d5fc6fa`
`0b619346c5b76842` `0dbe9e6b5f80de86` `c4ae54954e728917` `57d2888ad9158bfe`
`0dbe9e6b5f80de86` `94766adac4a3aeac` `9d2caee8373c0168` `0dbe9e6b5f80de86`
`52d64e07a78b15e3` `e840cc6ac355e3ee` `0dbe9e6b5f80de86`.

| filed as | in the tarball |
|---|---|
| `rips/derived-mp3.{log,cue,platterpus.json}` | `album/derived mp3 20260926t000413 platterpus-fork-g221a1df.*` |
| `session/{MANIFEST.txt,DIAGNOSTICS.txt,SETTINGS.json,SOURCES.txt,COMPONENTS.json}` | the same names at its root |
| `session/config.toml` | `session/artifacts/03platterpus/config.toml` |
| `session/transcript.txt`, `session/report.json` | `session/run/` |
| `session/rig-check-*` | `session/run/rig-check/*` |

## What it establishes

- **0.6.60's section A accepted `.16`.** `session/transcript.txt:110`, `L274
  expect-ripper-under-review`: *"installed build is platterpus-fork-g221a1df —
  the build under review"*. 0.6.59's first Full attempt stopped at this step
  with `.15` installed.
- **One two-track rip on `.16`, section K1** (`-l 1,2`, no `-H`, no `-Z`):
  `EAC CRC32` `B0D122E7` and `985AAE32`, both exact AccurateRip v1 and v2
  matches; `Ripping errors: 0`; `Rip completed:  yes (2 of 14 tracks)`;
  `Handshake: round 26 lap 6 closed, verdict GO -- released build`, correct for
  the tree `221a1df` was built from; `cyanrip -Y` says the log checksum is
  valid.
- **It agrees with every good filed read of the same tracks.**
  `tools/cross-rip.py` over this folder and `docs/rig-2026-09-24-df91ae7/rips`
  puts track 1 with the five other `B0D122E7` reads; the only disagreement is
  that session's known wrong read, `after-cancel.log`.

## What it does not establish

- **Neither of `.16`'s two changes ran.** Section I, the cancel that reaches
  the interrupted-track tally fix, is a standard-size section, and P3, the `-H`
  rips that reach the `media` tag fix, is full-size. Both were declined.
- **No whole-disc rip** (section F, standard) and **no secure re-read** (N,
  full). Section F's whole-disc rip has now not completed in two sessions.
- **A sector that will not read** is still untested on a drive.

## One defect in the bundle, which is Platterpus's

`session/MANIFEST.txt` says *"run ended  reached the last step"* and then
*"run outcome  ⚠ The run DID NOT COMPLETE — it stopped before the last step.
206 of 320 step(s) passed, 0 failed, 114 never ran."* The second is wrong:
`session/report.json` has all 114 skips `declined_by_size: true` and the last
step, L1290, passed, and the transcript ends *"every step this quick run ran
passed"*. The outcome sentence reads a quick run's declined sections as a stop.
