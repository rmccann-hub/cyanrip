# Rig session 2026-09-28 — build `e0471f4`, Platterpus 0.6.61, **Full**

**Read the build, not the date.** This is `e0471f4`, `+platterpus.17`: the
release, and round 28's reviewed pin. All eight rips, the direct invocations
that print a banner and `session/rig-check-ripper-version.txt` say
`platterpus-fork-ge0471f4`, 54 times in the transcript. The seven `g221a1df`
there are Platterpus's own notes that `.17` is not the build 0.6.61 was
approved against (`session/transcript.txt:400`), which is true until round 28
closes: their `FORK_PIN` is still round 27's.

**This is the Full run that closes round 28, by the operator's decision of
2026-09-28.** It is the pair round 28 lap 1 S6 names: `.17` installed through
Platterpus 0.6.61 with `PIN_UNDER_REVIEW` `e0471f4`. Platterpus's round 28
lap 6 S36, written after this run ended and without its bundle, records an
override moving the Full run to their 0.6.62, released at 08:23Z, after this
run's last rip. Asked which run closes the round, the operator chose this one,
so that override falls away and S6 stands as written.

## Provenance

| | |
|---|---|
| bundle | `platterpusbundle20260928t014808z.tar.gz`, handed over by the operator |
| sha256 | `9182201706006872c79663d14a2396a46fd0793914da359a9b15fc8f33fee2c9` |
| size | 4,929,294 bytes, 72 files, 25 of them screenshots |
| session stamp | `20260928T014808Z`, `started_at` 01:48:08Z; the last rip finished at 03:08:11 host time, 07:08:11Z (`session/transcript.txt:1642`, host time UTC−4) |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667 (`rips/full-acceptance-angle-bracket.log:7`, `:10`) |
| disc | DiscID `pNtImOkdBm9RMBIalzx0w9cfsYY-`, 14 tracks, the disc of every earlier filed session |
| ripper | `cyanrip 0.9.4-rc2+platterpus.17 (platterpus-fork-ge0471f4)` |
| consumer | `platterpus/0.6.61`, build `59f4c00`, their `v0.6.61` tag (`session/COMPONENTS.json`) |
| script | the full acceptance script, run size **full** |
| outcome | **pass 320, fail 0, error 0, skipped 0, blocked 0, unreachable 0, info 1**, `ok: true`, `counts_as_evidence: true` (`session/script-report.json`). The one `info` is their ripper-wrapper probe: `cyanrip --version` exited in 0.29 s with stdin open and closed. That is the script's own verdict; Platterpus's reading of their reports is theirs to give |

**Every file here but this README is byte-identical to a member of that
tarball**, checked by hashing each copy against the tarball's members, 36 of 36.
The rip files are renamed as in `docs/rig-2026-09-26-221a1df/`; `-2` is
section H's overwrite re-rip (`-l 1,2`), and the name without it is section F's
whole-disc rip. This bundle carries no Platterpus addendum, so there are two
files fewer than that one.

**Not filed**, with sha256/16 so each stays verifiable: the 25 screenshots; the
two app logs, `session/artifacts/02platterpus/log.txt` (7,430,283 bytes,
`480509485c4c1c66`) and `session/zz-applog-rotations/03platterpus/log.txt.1`
(8,388,570 bytes, `9c7ea4e71f0edd37`); `session/transcript.txt`, which is
byte-identical to the `session/run/transcript.txt` filed here; and the eight
`.platterpus.json` reports, Platterpus's artifact: `e20a930638619286`
full-acceptance-angle-bracket, `60193b367dee88c0`
full-acceptance-angle-bracket-2, `82daae2c16c5e069` secure-reread,
`5cc4b1dd6353437e` derived-mp3, `02d70bc97139a508` derived-wav,
`621ab6ff373b5837` derived-wavpack, `bcbfc0b8dc0dbe63` after-cancel,
`8b9be599b6c29e61` cancel-me. No claim below depends on any of them.

## When it ran, against the laps

**Our round 28 lap 5 was committed at 01:38:31Z, nine and a half minutes
before this run started**, and pushed at 05:03Z while it was running. Its
*"Nothing has run on a drive for this round"* was true when it was written.
**Platterpus's laps 6 and 7 were written after the run ended** and say no Full
run has happened; their S39 is scoped to their tree, which held no bundle, and
is true of it. Neither lap is wrong, and neither saw this run.

## Our reading: every cyanrip log in the bundle

**All eight verify against their own checksum** with `cyanrip -Y` (build
`faec4a8`), and each footer is consistent with its `Invoked as:` line: seven
completed with `Ripping errors: 0` and `Read stalls: none`, and `cancel-me` was
interrupted mid-read by SIGTERM, as section I intends. Every log's
`Handshake:` line reads `round 27 lap 6 closed, verdict GO -- released build`,
which is what `.17` was released on.

### `.17`'s changes, on the drive

- **The `Accurip 450` match says it covers one frame** (`ec0fe47`), for the
  first time on hardware: `(matches Accurip DB, confidence 200, one frame only;
  whole-track checksums not found)` at `rips/full-acceptance-angle-bracket.log:245`
  and `:395`, and `rips/secure-reread.log:428`.
- **The 450 lookup compares only 450 checksums** (`10f36fe`). It ran on every
  track here, but the defect it fixes had one chance in 2^32 per entry, so no
  run could show a before and after.
- **An early failure's log opens with the banner** (`ee0221c`): not exercised.
  The one early failure here, the rig check's `-d
  /nonexistent-platterpus-rig-check.cue`, opens no logfile. Its `-j` record is
  complete: `exit_code: 1`, the libcdio message in `messages`, and the build
  `e0471f4` with `released_build_declared: true`
  (`session/rig-check-argv-probe.json`).

### `.16`'s two changes, still holding

- **The interrupted track is left out of the AccurateRip tally**:
  `rips/cancel-me.log:79` prints `Tracks ripped accurately: 0/14` at
  `READ: 578`, and no `partially accurately` line.
- **`media` is tagged `CD` under `-H`**: section P3's two `-H` rips print
  `HDCD detected: no` and `media: CD` (`session/transcript.txt:1334`, `:1364`,
  `:1560`, `:1590`).

### One wrong read, logged with `Ripping errors: 0`

`tools/cross-rip.py` over this bundle and every filed one:

| track | this read | in | its good read | times this exact read is filed |
|---|---|---|---|---|
| 3 | `15D16895` | `full-acceptance-angle-bracket.log` (section F, no `-Z`) | `59D352DD`, `secure-reread.log` | **1**: new |

Track 3 has now been read 36 times across the filed sessions with **18
different checksums**, and only `59D352DD` (9 times) matches AccurateRip v1 and
v2. The log says `not found` for both and matches only on frame 450,
`rips/full-acceptance-angle-bracket.log:243-245`, **which `.17` now words as
one frame only**. The disc-level tally prints `Tracks ripped partially
accurately: 2/14` over it and track 5: that label is unchanged in `.17`,
because renaming it needs Platterpus's both-wordings release first
(`docs/KNOWN-ISSUES.md`). `Ripping errors:` counts
operational failures, not read quality, so `0` is the line doing what it
documents. Track 1, wrong once in each of the last two Full runs, agrees on all
seven reads here.

### The secure re-read

`secure-reread.log` (`-Z 2`) converged after 3 reads on 13 tracks, track 3
included, whose kept read `59D352DD` matches v1 and v2 (`:260-264`). **Track 5
did not converge** (`:424`, *"did NOT converge after 3 reads (repeat limit
hit)"*). In round 27's Full run it was track 3 that did not. Track 5's kept
read, `6902BCF0`, is the one section F read too, and matches only on frame 450,
as it has on all 31 of its filed reads, in three checksums. It is the case our
record already carries, not a new one.

### The cache probe, a thirteenth time

Section P's `cyanrip -N -x -I` again printed `at least 2048 sectors … search
ceiling reached` (`session/transcript.txt:935`), uncached 362.7 ms and cached
81.3 ms. `cd-paranoia -A` on this drive says 137–140. That is the thirteenth
filed session to show it, now in `docs/KNOWN-ISSUES.md`'s table. **Do not cite
our cache figure.**

### Nothing found that breaks the pin

`rips/cancel-me.log:87` reads `Encoder errors: none; 1 track encoded` over a
rip with `0 of 14 tracks` completed, as `.16`'s and `.15`'s did. That is the
line `.18` changes (`f150c0c`), announced in round 28 lap 3 and accepted in
Platterpus's lap 4. Nothing else here is new.

## What this run does not test

`.18`, which is not released; a sector that will not read; C2, which this drive
reports unsupported; `-f`; CD-TEXT from a physical disc; and `ee0221c`'s
banner on an early failure's log.
