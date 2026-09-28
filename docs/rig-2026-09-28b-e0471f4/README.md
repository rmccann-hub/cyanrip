# Rig session 2026-09-28b — build `e0471f4`, Platterpus 0.6.62, **Full**

**Read the build, not the date.** This is `e0471f4`, `+platterpus.17`, the
same build as `docs/rig-2026-09-28-e0471f4/`, on the same day, through a
different Platterpus: **0.6.62** (`9e96fa0`), not 0.6.61. All eight rips, the
direct invocations that print a banner and
`session/rig-check-ripper-version.txt` say `platterpus-fork-ge0471f4`, 54 times
in the transcript. The seven `g221a1df` there are Platterpus's own notes that
`.17` is not the build 0.6.62 was verified against
(`session/transcript.txt:410`, the first): their `FORK_PIN` was still
`221a1df`, round 27's.

**It is not round 29's Full run, and it does not meet round 29 lap 1 S6.** S6
needs `.18` (`51cc789`) installed through a Platterpus release whose
`PIN_UNDER_REVIEW` is `51cc789`. The first such release is 0.6.63, whose
release commit `platterpus@d226c03` is dated 19:53:39Z, 26 minutes after this
run's last rip. **Nor is it the run that closed round 28.** It is the run
Platterpus's round 28 lap 6 S36 moved that round's Full run to, from 0.6.62, and
our lap 8 S13 records that the operator chose the 0.6.61 run to close round 28
instead. So it is a close condition of neither round. It is filed as what it is:
a second Full run of `.17` on the same drive and disc, which no later run can
replace.

## Provenance

| | |
|---|---|
| bundle | `platterpusbundle20260928t144238z.tar.gz`, handed over by the operator |
| sha256 | `6e3f9e6c70d6f3b00731019080fd349b15c6cb8ba5e23ee34d6e1ec195bb652b` |
| size | 6,200,020 bytes, 76 files, 26 of them screenshots |
| session stamp | `20260928T144238Z`, `started_at` 14:42:38Z (`session/script-report.json`); the last rip, the secure re-read, finished at 15:27:10 host time, 19:27:10Z (`rips/secure-reread.log`, host time UTC−4) |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667 |
| disc | DiscID `pNtImOkdBm9RMBIalzx0w9cfsYY-`, 14 tracks, the disc of every filed session (`tools/cross-rip.py docs/rig-*` finds this one disc across 116 logs) |
| ripper | `cyanrip 0.9.4-rc2+platterpus.17 (platterpus-fork-ge0471f4)` |
| consumer | `platterpus/0.6.62`, build `9e96fa0` (`session/COMPONENTS.json`), which is where `git ls-remote --tags` puts their `v0.6.62` |
| script | the full acceptance script, run size **full** |
| outcome | **pass 320, fail 0, error 0, skipped 0, blocked 0, unreachable 0, info 1**, `ok: true`, `counts_as_evidence: true` (`session/script-report.json`). That is the script's own verdict; Platterpus's reading of their reports is theirs to give |

**Every file here but this README is byte-identical to a member of that
tarball**, checked by hashing each copy against the tarball's members, 37 of 37.
The rip files are renamed as in `docs/rig-2026-09-28-e0471f4/`; `-2` is
section H's overwrite re-rip (`-l 1,2`), and the name without it is section F's
whole-disc rip. This bundle carries one Platterpus addendum, for section F's
rip, filed as `rips/full-acceptance-angle-bracket.platterpus-addendum.txt`.

**Not filed**, with sha256/16 so each stays verifiable: the 26 screenshots; the
four app logs, `session/artifacts/02platterpus/log.txt` (5,200,943 bytes,
`e3a70bee039571f6`) and `session/zz-applog-rotations/03platterpus/log.txt.1`,
`04platterpus/log.txt.2` and `05platterpus/log.txt.3` (`0f682cd5c4186277`,
`a2458ca9b7147c26`, `9c7ea4e71f0edd37`); `session/run/transcript.txt`, which is
byte-identical to the `session/transcript.txt` filed here; and the eight
`.platterpus.json` reports, Platterpus's artifact: `ff8d5e3ef38766b1`
full-acceptance-angle-bracket, `58ffd9acfafb8207`
full-acceptance-angle-bracket-2, `66f724559ba7af67` secure-reread,
`4576f1065821cf6f` derived-mp3, `c35c85c4f8b62304` derived-wav,
`865ff3659ed682b9` derived-wavpack, `ef619747a54aaef7` after-cancel,
`82c89e58615febb5` cancel-me. No claim below depends on any of them.

## Our reading: every cyanrip log in the bundle

**All eight verify against their own checksum** with `cyanrip -Y`, and each
footer is consistent with its `Invoked as:` line: seven completed with
`Ripping errors: 0` and `Read stalls:    none (no read exceeded 10s)`, and
`cancel-me` was interrupted
mid-read by SIGTERM, as section I intends (`Interrupted at: track 1, mid-read`).
Every log's `Handshake:` line reads `round 27 lap 6 closed, verdict GO --
released build`, which is what `.17` was released on.

**Nothing here shows a defect in `.17`.**

- **Section N's secure re-read converged on all fourteen tracks**, *"converged
  after 3 reads"* on every one (`rips/secure-reread.log`). The 0.6.61 run
  earlier the same day left track 5 unconverged
  (`docs/rig-2026-09-28-e0471f4/rips/secure-reread.log:424`).
- **Tracks ripped accurately: 13/14** in both fourteen-track rips, sections F
  and N, and **partially accurately: 1/14**, track 5, matching on frame 450 only, with
  `.17`'s wording, *"one frame only; whole-track checksums not found"*.
- **Track 3's read in section F is `59D352DD`**, which AccurateRip v1 and v2
  match. The 0.6.61 run's section F read it as `15D16895`, which matched on
  frame 450 only.
- **`.16`'s two changes hold**: `rips/cancel-me.log:79` prints `Tracks ripped
  accurately: 0/14` over the interrupted rip with no `partially accurately`
  line, and the two `-H` rips of section P3 print `HDCD detected: no` and
  `media: CD` (`session/transcript.txt:1357`, `:1387`, `:1581`, `:1611`).
- **`rips/cancel-me.log:87` reads `Encoder errors: none; 1 track encoded`**
  over `0 of 14 tracks`. That is the line `.18` changes (`f150c0c`), to count
  only tracks whose read completed.

### Track 5, read two ways again

`tools/cross-rip.py` over this session finds one track read two ways: track 5,
`E0036697` in section F's rip and `6902BCF0` in the secure re-read. Both match
AccurateRip on frame 450 only. Over every filed session including this one,
`tools/cross-rip.py docs/rig-*` counts 33 reads of track 5: `E0036697` 18
times, `6902BCF0` 14 and `4065BECC` once. **Each of this session's two reproduced itself**:
Platterpus's addendum says its re-read of section F's track 5 reproduced
`E0036697` byte for byte and converged after 3 reads, and our `-Z 2` pass
converged on `6902BCF0`. So the same drive, on the same day, converges on either
reading of this track. Neither matches the database's whole-track checksums.

### The cache probe, a fourteenth time

Section P's `cyanrip -N -x -I` again printed `at least 2048 sectors … search
ceiling reached` (`session/transcript.txt:957`), uncached 362.6 ms and cached
62.4 ms. `cd-paranoia -A` on this drive says 137–140. That is the fourteenth
filed session to show it, now in `docs/KNOWN-ISSUES.md`'s table. **Do not cite
our cache figure.**

## What this run does not test

`.18`, which is round 29's pin; a sector that will not read; C2, which this
drive reports unsupported; `-f`; CD-TEXT from a physical disc; and `ee0221c`'s
banner on an early failure's log.
