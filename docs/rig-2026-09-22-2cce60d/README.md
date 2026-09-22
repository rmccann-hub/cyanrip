# Rig session 2026-09-22 — build `2cce60d`, Platterpus 0.6.52

**Read the build, not the date.** This is `2cce60d` — `+platterpus.13`, the
**release** pin and round 22's reviewed pin, which for this session are the same
commit. The 2026-09-17 session ran on `fe4d2c4` when `3952c03` was asked for, so
the label is checked here rather than assumed: every one of the eight rips, the
three direct invocations, and `rig-check-ripper-version.txt` all say
`platterpus-fork-g2cce60d`.

## Provenance

| | |
|---|---|
| bundle | `platterpusbundle20260922t022152z.tar.gz`, handed over by the operator |
| sha256 | `be82f5020f0459808fcba9fb00f72fa2e1ce256ca41c582f1a523c424abbf9f6` |
| size | 10,300,319 bytes, 340 entries, 295 of them screenshots |
| session stamp | `20260922T022152Z` |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), `/dev/sr0` |
| disc | The Police, *Every Breath You Take: The Classics*, 14 tracks, MusicBrainz `65282302-368b-4ba2-953a-483bcdef2410` |
| ripper | `cyanrip 0.9.4-rc2+platterpus.13 (platterpus-fork-g2cce60d)` |
| consumer | `platterpus/0.6.52` (build `a0aed36`) |
| script | `fullacceptance.txt`, 247 steps |
| outcome | **pass 247, fail 0, error 0, skipped 0, blocked 0, unreachable 0, info 1** |
| wall clock | 02:21:52Z to ~06:36Z; the `-Z 2` whole-disc rip alone took 2h 52m 35s |

**Everything filed here is byte-identical to a file in that tarball**, checked by
hashing each source and each destination and requiring equality per file, 35 for
35. Not filed: 295 screenshots, and the eight `.platterpus.json` records, which
come to 12,692,271 bytes and are Platterpus's artifact rather than ours. The tarball's
sha256 is recorded above so the unfiled remainder stays verifiable.

**The `-2` suffix was re-derived from content, not read off the folder name.**
The 2026-09-17 README records that the bundle gives two scenarios the same name
and the suffix is assigned by directory order, so it carries no meaning. Here it
was taken from each rip's own `Invoked as:` line:
`full-acceptance-angle-bracket` has no `-l` and rips `all` (14 of 14), and
`full-acceptance-angle-bracket-2` carries `-l 1,2` and `-D "{album_artist}/{album} (2)"`,
so it is the section-H overwrite re-rip. This time the suffix happens to agree
with the content; that is a fact about this bundle and not a rule.

## What this session establishes

### Round 21 §0.1's two unreachable items are now reached

Both failed on 2026-09-17 for one reason — that session ran on `fe4d2c4`, which
predates the changes — and both are what `2cce60d` exists to carry.

| | established | evidence |
|---|---|---|
| their parser reads `Retry limit:` on real logs | **yes** | all 8 rips carry `Retry limit:    3 (per frame, and per whole-track re-read)`; zero carry `Frame retries:`. `rig-check-manifest.txt` reports `parser/log  parsed 14 track(s)` and `log_parse` clean |
| `Ripping errors:` on a real session is the moved field | **yes** | `rips/cancel-me.log`: `Ripping errors: 1`, `Rip completed:  no (interrupted by SIGTERM, 0 of 14 tracks)`, `Interrupted at: track 1, mid-read` |

### The corrected paranoia claim, re-measured

`rips/secure-reread.log`, 14 tracks at `-Z 2 -r 3`:

```
Scope:         the last of 3 reads; the disc totals below sum all of them
```

present on **14 of 14** tracks. Per-track counters sum to **26,656** against a
disc total of **76,378** — a ratio of 2.87, so a consumer summing the per-track
blocks under round 5's retired invariant would under-report by two thirds.
Platterpus's own `rig-check` computes the same two numbers independently and
prints them side by side, which is the second implementation agreeing.

The single-pass rips are the control: `full-acceptance-angle-bracket.log` sums to
**23,841** against a disc total of **23,841**, exactly equal, with the `Scope:`
line absent on all 14 tracks. Same log format, same parser, two different and
correct answers.

### `-x` on hardware, for the tenth time, and the number is wrong for the tenth time

`session/script-report.json` step 207, `cyanrip -N -x -I`, exit 0:

```
Cache model:    1200 sectors (drive cache probed separately, see "Cache probe:")
Cache probe:    at least 2048 sectors, upper bound unknown (4704.0 KiB or more,
                search ceiling reached, uncached read 251.4 ms, cached read 42.1 ms)
```

`cd-paranoia -A` on this same drive reports **137 sectors, then 140**. This is
the tenth filed session to produce the line and the tenth to say *at least 2048*.
The mechanism is in `docs/KNOWN-ISSUES.md` and is not the ceiling. **Do not cite
our cache figure.**

The two `Cache model:` qualifiers are worth keeping as a positive result: the
eight Platterpus rips say `(drive cache size not probed)` and the `-x` run says
`(drive cache probed separately, see "Cache probe:")`. One number, two different
statements about how it is known, neither of them a verdict.

### The abort footer, and a refusal that does not hang the drive

`session/script-report.json` step 212, `cyanrip -N -l 1` with no `-s`, exit 1:

```
Offset is unset! To continue with an offset of 0, run with -s 0!
Ripping errors: 0
Read stalls:    none (no read exceeded 10s)
Rip completed:  no (aborted, 0 of 14 tracks)
```

A diagnosable line, a non-zero exit, a complete footer, and `Ripping errors: 0`
because nothing was read rather than because nothing went wrong — the abort arm,
distinct from the interrupt arm that `cancel-me.log` exercises in the same
session. The drive was usable immediately afterwards: the CTDB lookup and the
`-x -I` probe both ran in the following seconds.

## Two findings

### 1. ~~Tracks 3 and 5 again, and this time nothing records the read that was kept~~ — WRONG, CORRECTED 2026-09-22

**THE HEADING ABOVE WAS FALSE AND IS KEPT SO THE CORRECTION HAS A SUBJECT.**
Platterpus refuted it in round 23 lap 2 §A, and the refutation was verified here
against their code and against a file that was in the bundle the whole time:

```json
"retried_tracks": [
  {"track": 3, "reripped_z": 2, "converged": false, "replaced": false},
  {"track": 5, "reripped_z": 2, "converged": false, "replaced": false}
]
```

`replaced: false` on both. A track is swapped only by a **converged** re-read —
`platterpus@a0aed36:src/platterpus/workers/rip_worker.py:2705-2708`, where
`converged = getattr(track, "secure_rerip_converged", None) is True` guards
`replaced = self._swap_in_reripped_track(...)`, read at that SHA rather than
taken on their word. Neither track converged, **so nothing was swapped, the
first pass's bytes are the bytes on disk, and the album log describing them is
the correct log.**

**And the absent addendum was a correct negative, not a missing record.** Their
`SupersededTrack` addendum (`:2673`) and `_swapped_track_records` (`:1003`,
populated at `:2723`) exist and are written **on a swap**. No swap happened, so
no addendum was due. Reading its absence as a lost record is the
did-not-happen versus happened-and-found-nothing rule, failed in the direction
this file warns about in the other.

**Root cause, and it is the filing decision above.** The eight
`.platterpus.json` records were left out as *"Platterpus's artifact rather than
ours"*, and then a claim was made about a question one field in them answers.
**`/read_speed/retried_tracks` was in the tarball from the first minute.** Worse,
the same file had already caught us out three days earlier: on the 2026-09-19
bundle the `.log` carried no `-l` while the `.platterpus.json` carried `-l 3,5`.
Same file, same blind spot, twice.

**So `rips/secure-reread.platterpus.json` is now filed**, sha256
`1d9c64d2b72243d8b446b9e081c5ed7d00ee355b8d8d2c8e257b22d88eb82773` — the one
report a disputed claim turned on. The other seven stay unfiled and their
sha256/16 are recorded here so they stay verifiable: `eaf4a0ca94cf0b2a`
after-cancel, `856e6822b8f4df52` cancel-me, `344c15c18cfaca8e` derived-mp3,
`be7d50df94dc7385` derived-wav, `f059a84efccaf06c` derived-wavpack,
`a95c72be9b019b72` full-acceptance, `acda897a7fbc4119` full-acceptance-2.

### What actually survives, which is narrower and mostly theirs

`rips/secure-reread.log` reports, for tracks 3 and 5:

```
Secure re-read:  did NOT converge after 3 reads (repeat limit hit)
```

Platterpus then re-ripped exactly those two tracks in a **second cyanrip
invocation** — `session/platterpus-app-log.txt:49024`, `-Z 2 -l 3,5`, with
`cwd=/tmp/platterpus-refix-_sf3v80t` — and that run did not converge either. Its
disposition is in their log at `02:35:35,414`:

> ⚠ Read stability: tracks 3, 5 still didn't read identically even after an
> automatic re-rip — **kept the best read, which may not be bit-perfect.**

**So the audio on disk for tracks 3 and 5 came from an invocation whose log is
not in this bundle**, and the log that *is* in the album folder — the one filed
here, the one a consumer archives — is the first invocation's. Its blocks for
tracks 3 and 5 carry that invocation's `EAC CRC32`, `Accurip`, `creation_time`
and paranoia counts, describing reads that were superseded.

**Theirs, and they are fixing it.** The re-rip of tracks 3 and 5 ran 23 minutes
in a `tempfile` root that a `finally` removes, taking cyanrip's log for that read
with it. So the read that was **discarded** — the one worth diagnosing, because
it is the one that failed — survives only in their debug lines.
`session/SOURCES.txt` asks for six paths and that directory is not among them.

**Theirs, and conceded by them.** *"kept the best read, which may not be
bit-perfect"* is their user-facing sentence, and when nothing converges no
selection between copies happens, so the sentence describes something that did
not occur. It is what this reading was built on.

**Ours, and still real — but this run is not evidence for it.** *We give a
consumer no way to say a file was superseded.* There is no field a second
invocation can write into the first log and no way to amend one, because it is
immutable and `Log FUN512:` covers it. That gap stands on its own merits and
belongs in round 24; **it needs a case where a swap actually happened, and this
is not one.** Their §E Q1 asks exactly that and they are right to.

**What cyanrip did here was correct throughout.** It wrote a complete and true
record of what that invocation did, including the non-convergence, with a
`Scope:` line on all fourteen tracks.

### 2. Every number the log reports about the audio is measured before the filter graph

Section P3 of the script runs `-H -E` and `-H -W` on track 1 back to back
(`script-report.json` steps 217 and 221). The two logs report:

| | `-H -E` | `-H -W` |
|---|---|---|
| `EAC CRC32` | `B0D122E7` | `B0D122E7` |
| `Accurip v1` / `v2` | `5D3C90CB` / `22B9924D` | `5D3C90CB` / `22B9924D` |
| `Sample peak level` | `94.3% (-0.5 dBFS)` | `94.3% (-0.5 dBFS)` |
| `True peak level` | `0.3 dBFS` | `0.3 dBFS` |
| `Integrated loudness (R128)` | `-13.9 LUFS` | `-13.9 LUFS` |
| `REPLAYGAIN_TRACK_PEAK` | `1.029445` | `1.029445` |
| `Preemphasis` | `none detected (deemphasis forced)` | `none detected` |

Identical to the digit on everything except the one field that reads a setting.

**That reads like the round-15 ternary-cascade defect and is not.** That fix is
in and it works — verified here on images rather than inferred, six invocations
producing four distinct PCM streams, in `docs/KNOWN-ISSUES.md`. What this
comparison actually shows is that **the log cannot witness the difference**,
because the checksums are taken on the raw bytes off the disc and the ebur128
graph is fed the pre-filter frame. Full mechanism, citations and the measurement
in `docs/KNOWN-ISSUES.md`.

It has **no Platterpus exposure today**, and that is checkable rather than
assumed: no rip argv in this session carries `-H`, `-E`, `-W` or `-x` — read off
the eight `Invoked as:` lines, not off their rig-check summary.

## What this session does NOT establish

Said out loud, because a 247-of-247 pass invites the opposite reading.

| | why |
|---|---|
| **C2** | `UNREACHABLE` on this drive — it reports C2 unsupported, and the logs say `C2 errors:      unsupported by drive`. No procedure reaches it |
| **`-f`** | **not run.** No invocation in this session carries `-f`. Platterpus's UI reports `read offset: +667 — confirmed — two independent sources agree` after the full rip, but that is *their* AccurateRip inference, not our autodetection, and the two are different code |
| **damaged media** | needs a damaged disc; this one read clean apart from tracks 3 and 5 |
| **CD-TEXT from a physical disc** | `CD-TEXT:        none reported by libcdio` on every rip — the observation, not the stronger claim |
| **the both-wordings pairing** | `2cce60d` is `+platterpus.13`. No log here carries `Track %i read successfully!`; **seven of the eight** carry `Track %i ripped and encoded successfully!` — the eighth is `cancel-me.log`, which was killed inside track 1 and completed no track, so it correctly has neither. That pairing needs a later session on `.14` plus Platterpus's parser release |
