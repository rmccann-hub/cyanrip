# Rig session 2026-09-12 — **the published pair works. First clean session in the sequence.**

Platterpus acceptance session `20260912T204421Z` on the **published** pair:
`platterpus 0.6.47` (`abd2eb8`) driving
`cyanrip 0.9.4-rc2+platterpus.12 (platterpus-fork-gfe4d2c4)`, PIONEER BD-RW
BDR-209D.

## What it establishes

**The pair works end to end.** Eight rips: two whole-disc (`14 of 14`), five
partial (`2 of 14`), one deliberately interrupted. Seven `Ripping errors: 0`,
`Read stalls: none` on all eight, `AccurateRip: found` on all eight.

**All eight logs verify against our own tool**, run here rather than reported:
`cyanrip -Y <each>` → exit **0**, eight for eight.

**`errors: 0` in their diagnostics — the first time in this sequence**, and it
is a specific fix landing rather than luck:

| session | `ripper.log_verify_failed` |
|---|---|
| 2026-09-10 (`ddc1e8c`) | 2 |
| 2026-09-11 (`ddc1e8c`) | 2 |
| **2026-09-12 (`fe4d2c4`)** | **0** |

That is Platterpus's round-16 §C1 race — reading the rip log 6.1 s and 7 s
before cyanrip finished writing it, then reporting a complete signed log as
carrying no checksum. The fix sat unmerged through two rounds; `0.6.47` carries
it and it works on hardware.

**A third cancel reached cyanrip mid-read**, and the record of the incomplete
rip is itself complete and attested: `Ripping errors: 1`,
`Rip completed:  no (interrupted by SIGTERM, 0 of 14 tracks)`,
`Interrupted at: track 1, mid-read`, a valid `Log FUN512:`, and `-Y` exit 0.

**The approval string reads exactly as designed**, and it is not a mis-pairing:

```
ripper build platterpus-fork-gfe4d2c4 is the one handshake round 17 approved,
verified by both projects, for Platterpus 0.6.46
```

`0.6.46` is the pairing round 17 approved; `0.6.47` is what ran. Their constant
names the approved pairing rather than the running app, deliberately.

**`grep unapproved` hits once and it is not a verdict.** The match is inside
their test script's own embedded comment text, describing a hypothetical. A grep
hit is not a fact.

## What it does NOT establish, and one of these looks like it does

**It is evidence about `fe4d2c4` under `0.6.47`. It is NOT evidence about the
approved pair `(fe4d2c4, 0.6.46)`**, which no run has exercised and which is not
what anyone is running.

**Clause 2 was invoked and NOT settled here.** The transcript shows
`cyanrip -N -s 667 -l 1 -H -E -D r16deemphon` and the `-H -W` control, both on
`fe4d2c4` — but they wrote `.flac`, not `-o pcm`, and **none of their output
travelled** (0 files matching `*deemph*` in this bundle). Container FLACs differ
in `creation_time` whatever the audio does, so a difference there is necessary
and not sufficient. What this shows is that the invocation runs and prints
`Preemphasis: none detected (deemphasis forced)` — **the setup, not the clause**.

**Clause 2's result does carry across from `ddc1e8c`, by derivation rather than
assumption.** `fe4d2c4` differs from Run A's program by exactly one commit,
`12f2081`, which is a single hunk in `main()` at `cyanrip_main.c:2734` and
touches no file under `src/` other than `cyanrip_main.c` — nothing in the encode
path, the filter graph, the checksums, naming or the cue writer. The filter graph
is byte-identical, so Run A's decoded-sample comparison stands for this build.

**`12f2081` itself still has not run on hardware.** All eight rips pass `-j`
exactly once (`cyanrip_backend.py:390`), and the line it adds cannot fire for a
caller that does.

**The `-x` upper bound is still ours.** The probe ran on `fe4d2c4` and reported
`at least 2048 sectors, upper bound unknown (… search ceiling reached)`. Three
successful probes now, across two builds, and **not one of them has bounded the
drive** — `search ceiling reached` is our own `PROBE_MAX_SECTORS`.

**Still untouched by any run:** C2 (the drive reports it unsupported — not
pending, unreachable on this hardware), `-f`, damaged media, and CD-TEXT from a
disc that has some.

**Our `-j` records still do not travel.** Every one of the eight rips passes
`-j <path>`; the bundle contains **zero** of them, as every previous bundle has.

## The rips were renamed when filed, and here is the mapping

Same reason as the two bundles before it, and the reason is theirs: their
round-16 lap 14 §C found that `*.eac.log` is a third spelling of their EAC
export, and a name-keyed exclusion that worked over their bundle failed over our
filed copy. **Renaming is a change to an artifact even when every byte
survives.** Each row was produced by hashing the filed file.

| filed here | as delivered in their bundle | sha256/16 |
|---|---|---|
| `after-cancel.cue` | `after cancel 20260912t204421 platterpus-fork-gfe4d2c4.cue` | `f7498702c9ad457a…` |
| `after-cancel.eac.log` | `after cancel 20260912t204421 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `b81bf922169edd7e…` |
| `after-cancel.log` | `after cancel 20260912t204421 platterpus-fork-gfe4d2c4.log` | `8c09d129e18f3ad8…` |
| `cancel-me.cue` | `cancel me 20260912t204421 platterpus-fork-gfe4d2c4.cue` | `e0e8d3b2d8d52771…` |
| `cancel-me.eac.log` | `cancel me 20260912t204421 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `e17c18a0753d1d17…` |
| `cancel-me.log` | `cancel me 20260912t204421 platterpus-fork-gfe4d2c4.log` | `3b710ec1a6a1b91e…` |
| `derived-mp3.cue` | `derived mp3 20260912t204421 platterpus-fork-gfe4d2c4.cue` | `c5d2b6458c9715c7…` |
| `derived-mp3.eac.log` | `derived mp3 20260912t204421 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `c3e4c8e0296ecfe9…` |
| `derived-mp3.log` | `derived mp3 20260912t204421 platterpus-fork-gfe4d2c4.log` | `7f7c8fb3823b0481…` |
| `derived-wav.cue` | `derived wav 20260912t204421 platterpus-fork-gfe4d2c4.cue` | `c98c7e3142633eb2…` |
| `derived-wav.eac.log` | `derived wav 20260912t204421 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `3b7c574a25c47b80…` |
| `derived-wav.log` | `derived wav 20260912t204421 platterpus-fork-gfe4d2c4.log` | `b617d8c501748d56…` |
| `derived-wavpack.cue` | `derived wavpack 20260912t204421 platterpus-fork-gfe4d2c4.cue` | `65966ef8f9d55f8b…` |
| `derived-wavpack.eac.log` | `derived wavpack 20260912t204421 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `185c6a46abff1bd7…` |
| `derived-wavpack.log` | `derived wavpack 20260912t204421 platterpus-fork-gfe4d2c4.log` | `d934413fc1f94f03…` |
| `full-acceptance-angle-bracket-2.cue` | `full acceptance∶ angle‹bracket 20260912t204421 platterpus-fork-gfe4d2c4.cue` | `f8de12b77a2b28e7…` |
| `full-acceptance-angle-bracket-2.eac.log` | `full acceptance∶ angle‹bracket 20260912t204421 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `c65585bcc64661c1…` |
| `full-acceptance-angle-bracket-2.log` | `full acceptance∶ angle‹bracket 20260912t204421 platterpus-fork-gfe4d2c4.log` | `247c2a21c3d445d8…` |
| `full-acceptance-angle-bracket.cue` | `full acceptance∶ angle‹bracket 20260912t204421 platterpus-fork-gfe4d2c4.cue` | `9629b10609c4fc7f…` |
| `full-acceptance-angle-bracket.eac.log` | `full acceptance∶ angle‹bracket 20260912t204421 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `58213a1ff6df5338…` |
| `full-acceptance-angle-bracket.log` | `full acceptance∶ angle‹bracket 20260912t204421 platterpus-fork-gfe4d2c4.log` | `7d99395ef5fb6927…` |
| `secure-reread.cue` | `secure reread 20260912t204421 platterpus-fork-gfe4d2c4.cue` | `6291f7d61f9fec44…` |
| `secure-reread.eac.log` | `secure reread 20260912t204421 platterpus-fork-gfe4d2c4 (EAC-compatible).log` | `36cdb9bbc5685ed8…` |
| `secure-reread.log` | `secure reread 20260912t204421 platterpus-fork-gfe4d2c4.log` | `5a588a01baa4edf3…` |

**Two rips share a delivered name**: their bundle carries two
`full acceptance∶ angle‹bracket …` runs in directories distinguished only by the
directory, so the second takes a `-2` suffix here.

## What is not filed

The delivered tarball is 60 MB; this is 7.8 MB. Filed: the eight rip logs, their
EAC companions, the eight cues, and the session's transcript, manifest, sources
and diagnostics, plus the current application log. Not filed: the UI screenshots,
the rotated application logs, and the per-rip `.platterpus.json` reports — those
are evidence about Platterpus's internals rather than about cyanrip's output, and
`session/SOURCES.txt` is filed whole so the full inventory is recoverable here.
