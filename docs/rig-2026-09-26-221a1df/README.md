# Rig session 2026-09-26 — build `221a1df`, Platterpus 0.6.60, **Full**

**Read the build, not the date.** This is `221a1df`, `+platterpus.16`: the
release, and round 27's reviewed pin. All eight rips, the four direct
invocations that print a banner (`-x -I`, `-N -l 1`, `-H -E`, `-H -W`) and
`session/rig-check-ripper-version.txt` say
`platterpus-fork-g221a1df`. The one `gdf91ae7` in the transcript is
Platterpus's own note that `.16` is not the build their 0.6.60 was approved
against, which was true until their round 27 lap 5.

**It is not the same session as `docs/rig-2026-09-26-221a1df-quick/`.** That
one ran from 00:04:13Z at size *quick*, and round 27 closed on it under the
operator's override of R1. This one ran from **04:13:08Z at size *full***, with
`counts_as_evidence: true`, and it is the run round 27 lap 1 §0.1 asked for.

## Provenance

| | |
|---|---|
| bundle | `platterpusbundle20260926t041308z.tar.gz`, handed over by the operator |
| sha256 | `7b6b45d38f1e723551fcbb1fe41262faa968abdddc4d475d903b39a1bada7ae8` |
| size | 4,826,147 bytes, 74 files, 25 of them screenshots |
| session stamp | `20260926T041308Z`; the last rip finished at 09:47:01Z (`session/transcript.txt:1663`, host time UTC−4) |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667 |
| disc | DiscID `pNtImOkdBm9RMBIalzx0w9cfsYY-`, 14 tracks: the disc of all 99 filed cyanrip logs that print a `DiscID:`, these eight included |
| ripper | `cyanrip 0.9.4-rc2+platterpus.16 (platterpus-fork-g221a1df)` |
| consumer | `platterpus/0.6.60`, build `88c09dd`, their `v0.6.60` tag (`session/COMPONENTS.json`) |
| script | `fullacceptance.txt`, run size **full** |
| outcome | **pass 320, fail 0, error 0, skipped 0, blocked 0, unreachable 0, info 1**, `ok: true`, `counts_as_evidence: true` (`session/script-report.json`) |

**Every file here but this README is byte-identical to a member of that
tarball**, checked by hashing each copy against the tarball's members, 38 of 38. The rip files are
renamed as in `docs/rig-2026-09-24-df91ae7/`; `-2` is section H's overwrite
re-rip (`-l 1,2`), and the name without it is section F's whole-disc rip.

**Not filed**, with sha256/16 so each stays verifiable: the 25 screenshots; the
two app logs, `session/artifacts/02platterpus/log.txt` (8,050,002 bytes,
`2aabc38707c9028f`) and `session/zz-applog-rotations/03platterpus/log.txt.1`
(8,388,569 bytes, `9acf533d184c6871`); `session/transcript.txt`, which is
byte-identical to the `session/run/transcript.txt` filed here; and the eight
`.platterpus.json` reports, Platterpus's artifact: `ed747d731ac06a57`
full-acceptance-angle-bracket, `326ed50c4c5b55c1`
full-acceptance-angle-bracket-2, `67af4d42584c0c36` secure-reread,
`706107f582aaa04a` derived-mp3, `75e62c94d39c8ea6` derived-wav,
`8b45e667d7f41cc3` derived-wavpack, `ad4989c0a59bbd9b` after-cancel,
`3432d387e8a2a431` cancel-me. No claim below depends on any of them.

## What this corrects, and where

**Our round 27 lap 6 was committed at 04:30:48Z, seventeen minutes into this
run**, which we did not know was running. Its `HANDSHAKE-TESTED` says *"the
quick run … not the Full run lap 1 §0.1 asked for"* and lists as *"not tested,
by this or any run"* `.16`'s two changes, a whole-disc rip and a secure
re-read. All four ran here. Lap 6 is sent and stays as it is, so the correction
lives in `docs/handshake/STATUS.md` now and in round 28 lap 1. A sector that
will not read, and anything in `.17`, are still untested.

## Our reading: every cyanrip log in the bundle

**All eight verify against their own checksum** with `cyanrip -Y` (build
`58b4aa8`), and each footer is consistent with its `Invoked as:` line: seven
completed with `Ripping errors: 0` and `Read stalls: none`, and `cancel-me` was
interrupted as section I intends.

### `.16`'s two changes, on the drive, with a before and after

- **An interrupted track is left out of the AccurateRip tally.** `cancel-me.log`
  was interrupted mid-read on track 1 with `READ: 578`, and prints `Tracks
  ripped accurately: 0/14` and no `partially accurately` line. Every earlier
  build interrupted the same way printed `Tracks ripped partially accurately:
  1/14`: `.11` at `docs/rig-2026-09-10-ddc1e8c/rips/cancel-me.log:79`, `.12`,
  `.13`, and `.15` at `docs/rig-2026-09-24-df91ae7/rips/cancel-me.log:80`, each
  at `READ: 578` or `674`.
- **`media` is tagged `CD` under `-H`.** Section P3's `-H -E` and `-H -W` rips
  print `HDCD decoding: enabled`, `HDCD detected: no` and `media: CD`
  (`session/transcript.txt:1387`, `:1611`). `.15`'s Full run printed
  `media: HDCD` at the same step
  (`docs/rig-2026-09-24-df91ae7/session/transcript.txt:1396`), and `.13`'s did
  too (`docs/rig-2026-09-22-2cce60d/session/transcript.txt:1445`).

### Two wrong reads, each logged with `Ripping errors: 0`

`tools/cross-rip.py` over this bundle and every filed one:

| track | this read | in | its good read | times this exact read is filed |
|---|---|---|---|---|
| 1 | `0E91CD1A` | `derived-mp3.log` | `B0D122E7`, the other six reads here | **3**: here, `docs/rig-2026-09-24-df91ae7/rips/after-cancel.log` (round 26) and `docs/rig-2026-09-11-ddc1e8c/rips/derived-wavpack.log` |
| 3 | `3D8FCF0C` | `full-acceptance-angle-bracket.log` (section F, no `-Z`) | `59D352DD`, `secure-reread.log` | **10** |

Both logs say `not found` for v1 and v2 and match only on frame 450, which
`.16` words as `track is partially accurately ripped`
(`full-acceptance-angle-bracket.log:245`). **That is the wording `.17`'s
`ec0fe47` replaces**, and this run is a further instance of the case that
motivated it: a one-frame match printed beside a whole track that was read
wrong.

Platterpus re-read both tracks, and its addenda say each re-read replaced the
first pass (`rips/derived-mp3.platterpus-addendum.txt`,
`rips/full-acceptance-angle-bracket.platterpus-addendum.txt`). **The AccurateRip
values they give for the replacement reads match our own logs of those reads
exactly**: track 1 v1 `5D3C90CB` and v2 `22B9924D` as in `derived-wav.log`, and
track 3 v1 `3C8BDDD2` and v2 `96DF8C22` as in `secure-reread.log`. Our logs
describe the first pass, which is what they say they describe.

### The secure re-read

`secure-reread.log` (`-Z 2`) converged after 3 reads on 13 tracks. **Track 3
did not converge** (`secure-reread.log:261`, *"did NOT converge after 3 reads
(repeat limit hit)"*), and the read it kept, `59D352DD`, matches v1 and v2.
`docs/SETTLED.md` already records that convergence and the reported checksum
are independent, on this same track.

**Track 5 matched only on frame 450 in both whole-disc rips**, `E0036697` both
times with `Accurip 450: 4CCBCF89`. Over every filed session it has been read 29
times and has never matched a whole-track checksum. It is the case our record
already carries, not a new one.

### The cache probe, a twelfth time

Section P's `cyanrip -N -x -I` again printed `at least 2048 sectors … search
ceiling reached` (`session/transcript.txt:957`), uncached 362.8 ms and cached
62.2 ms. `cd-paranoia -A` on this drive says 137–140. That is the twelfth filed
session to show it, now in `docs/KNOWN-ISSUES.md`'s table. **Do not cite our
cache figure.**

### Found, for the next round

`cancel-me.log:87` reads `Encoder errors: none; 1 track encoded` over a rip with
`0 of 14 tracks` completed. The count is right about encoders and wide about
tracks. `.15`'s log said the same. Recorded in `docs/KNOWN-ISSUES.md`; it is a P2
line, so any change goes through a round. `cancel-me.log`'s album loudness block
over a partial track is already recorded there, with the same −14.4 LUFS.

## What this run does not test

`.17`, which is not released; a sector that will not read; C2, which this drive
reports unsupported; and `-f`.
