# Rig session 2026-10-16 — build `891c79e`, Platterpus 0.7.106, **Full**

**Read the build, not the date.** This is `891c79e`, `+platterpus.23`, the
release round 34 reviews, through Platterpus **0.7.106** (`v0.7.106`,
`dd200af7`), whose `PIN_UNDER_REVIEW` is `891c79e`. Every log opens with
`cyanrip 0.9.4-rc3+platterpus.23 (platterpus-fork-g891c79e)` and reads
`Handshake: round 33 lap 7 closed, verdict GO -- released build`: `.23` was
built after round 33 closed and before round 34 opened.

**It is round 34's test**: the Full run of our lap 1's S14, on `.23` with
0.7.106. `tools/ingest-bundle.py --peer` reads both as the newest when the
run began, 00:20:45Z: `.23` is `release_seq` 33, the newest ledger row, and
`v0.7.106` is the newest tag, created 2026-10-15T23:51:56Z.

**The script's verdict is a pass**: pass 426, fail 0, error 0, skipped 0,
blocked 0, unreachable 1, info 6, `ok: true`, `counts_as_evidence: true`, run
size full (`session/run/report.json`). The unreachable step is section E2
(L566), as on every run on this drive: the disc is in AccurateRip's list, so
the offset refusal E2 tests cannot be reached on it. Five `info` steps are
2026-10-13's five; the sixth is new, L1554 `expect-pregaps-agree`, below.

**Every member matches the sender's own hash**: `tools/ingest-bundle.py`
checked each of the 107 members the bundle's `MANIFEST.txt` hashes against
it, and all 107 match byte for byte. It is the first filing to run that
check, which our round 34 lap 2 S10 undertook and `418fdd2` landed.

**Filed under the names it was delivered with.** `tools/ingest-bundle.py
--into` copied 52 members, each matching the archive (`sha256sum -c
SHA256SUMS`, 52 OK). The audio, the screenshots, the thirteen
`--diagnostics` records, the `.platterpus.json` files and the app-log
rotations are not filed, and `SHA256SUMS` names each. **Nothing needed
replacing**: no filed file carried a home path, which Platterpus's export
now replaces itself (their X9). The owner's name was not checked, because no
local list of names exists here, and not checked is not the same as not
present.

| | |
|---|---|
| bundle | `platterpusbundle20261016t002045z.tar.gz`, handed over by the operator on 2026-10-16 |
| sha256 | `cfb2fab2eb68ef12aeee90dcfdbeb28c837b09ce0bcba11e677565fb1f815016` |
| size | 6,720,084 bytes, 108 members, 107 of them hashed in its `MANIFEST.txt` |
| session | `20261016T002045Z`, `started_at` 00:20:45Z, ended 05:30Z at the earliest |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| disc | the reference disc, 14 tracks |

## What it shows

- **All thirteen cyanrip logs verify with `-Y`** and end in a signed footer:
  the eleven `.log` files and the logs of the two securing passes. `cancel
  me` is the one incomplete rip, `interrupted by SIGTERM, 0 of 14 tracks`, as
  the section intends, and the one with `Ripping errors: 1`; every other
  reads 0. No read stalled past 10 s in any rip.
- **`.23`'s two new header lines printed on a drive.** `AccurateRip ID:
  001d420f-013bb370-e20dfe0e`, whose third field is the `CDDB:` value every
  track's metadata gives, `E20DFE0E`, and whose lookup found the disc: both
  whole-disc rips read `Tracks ripped accurately: 12/14` and `Tracks matched
  on one frame only: 2/14`, tracks 3 and 5, as on every run of this disc. And
  `AcoustID: unsupported (built without libchromaprint)`, which answers
  Platterpus's TASKS R12 for the rig: its build does not fingerprint, so no
  `acoustid_fingerprint` tag is written there, with or without `-B`.
- **The `/9` record's fields ran on a drive**, in all thirteen records,
  schema `cyanrip-diagnostics/9`. Pre-emphasis: the two R16 rips' records
  read `preemphasis: none` with `deemphasis_applied: true` under `-E` and
  `false` under `-W`, which their logs' `Preemphasis:` lines say too (`none
  detected (deemphasis forced)`, `none detected`). The disc's own ISRC: in
  every record, each track the rip read has `isrc_disc` null with the reason
  `libcdio returned none`, 14 of 14 in the two whole-disc rips, and each
  track it did not read gives `not read`, so the two reasons stay apart on a
  drive; whether the disc carries ISRCs this run cannot say. `isrc_written` is the ISRC the
  caller passed (`GBAAM0201086` for track 1) and null in the R16 rips, which
  pass none. CD-TEXT: `none reported by libcdio`, as every log's `CD-TEXT:`
  line says. **The `-f` result did not run**: the run's `-f` step (L1286)
  asks for no record, so every record's `offset_search` is null for the
  reason that no rip searched.
- **Track 1's pregap reads 150 frames from the lead-in** (`Pregap source:
  lead-in`). `.23` counts it from the start of the disc (`a64d58d`); track 1
  of this disc starts at LSN 0, so the old count and the new are both 150,
  and this disc cannot tell them apart.
- **The repeat limit's clause had no cause to print, again.** Track 3 hit
  the limit three times, in the same three places as on 2026-10-13: the
  secure re-read (`-Z 2`), its securing pass (`-Z 2 -l 3`) and the first
  rip's securing pass (`-Z 2 -l 3,5`). Each time its five reads gave five
  different checksums, so the newest read was kept, which is the last, and
  the clause rightly stayed silent. In the secure re-read's securing pass the
  fourth read was `59D352DD`, the one checksum of track 3 AccurateRip
  matches, and it was not kept, since no two reads agreed. **The arm that
  prints has not run on a drive.**
- **No pregap search failed**, so no `Gaps:` list printed `pregap of track N
  unknown (reason)`. **That arm has not run on a drive either.**
- **But two searches returned zero for track 4's pregap again.** Eleven
  `Gaps:` lists give `158 frame pregap in track 4` and two leave it out: the
  `derived mp3` rip (tracks 1 and 2) and the secure re-read's securing pass
  (track 3). Neither ripped track 4, so neither has its block, but neither
  list says the search failed, so on `.23` both were returned zeros. It is
  the old defect `STATUS.md`'s `subchannel-pregap-varies` records, which counted
  4 of the 211 filed logs of the reference disc before this run, so these two
  make six; it is not in what `.23` changed. Under
  the default action the pregap merges into track 3, whose end the TOC
  gives, so no audio byte moves; the cue sheet's record of track 4 does.
- **Platterpus found the same two disagreements by itself.** Its new step
  L1554 `expect-pregaps-agree` compared the 13 logs and reported tracks 4 and
  9 differing, graded `info`, *"gathered, not graded"*, naming the fork's
  `subchannel-pregap-varies` (`session/transcript.txt:1954-1960`). **Track
  9's pregap is 95 frames in the `derived mp3` rip and 94 in the twelve
  others.**
- **Every `--diagnostics` record is in the bundle, the securing passes'
  included** (their X6). The two passes asked for
  `cyanrip-diagnostics-20261016T011132Z.json` and `…050149Z.json`, and
  Platterpus keeps each as that name with `-securingpass` before the suffix
  (`platterpus@dd200af7:src/platterpus/record_fate.py:49`, `:102`), so the
  bundle carries `…011132Z-securingpass.json` and `…050149Z-securingpass.json`.
  Our `tools/read-run.py` reported both missing until it learned that name,
  found writing this reading.
- **One of the two pre-emphasis rips names no caller, and the cause is in
  Platterpus's runner.** Their X8 sends `(consumer) (diagnostics)` on both
  R16 rips, and both wrote their records; but `r16deemphon`'s argv has no
  `--consumer`, so its log reads `Consumer: not identified (no --consumer
  given)`, while `r16deemphoff`'s carries `Consumer: platterpus/0.7.106`. The
  runner's note says why (`session/transcript.txt:1506`): *"(consumer) sent
  nothing: the ripper build no read exceeded 10s is not one known to accept
  --consumer"*. The step before it, L1394, is the C1 refusal, `cyanrip -N -l
  1` with no offset, whose output carries no banner, and their
  `identify_from_banner` takes the text inside the output's first
  parentheses as the build tag
  (`platterpus@dd200af7:src/platterpus/ripper_identity.py:239-240`), which in
  that output is `Read stalls:    none (no read exceeded 10s)`. The latch
  that calls it says output with no recognisable banner leaves the captured
  tag alone (`platterpus@dd200af7:src/platterpus/uiscript/runner.py:1939-1945`);
  this output replaced it. The `-E` rip's own banner set it right again, so
  the `-W` rip sent `--consumer`. It is theirs, and no line of ours changed.
- **The secure re-read** (`-Z 2`): thirteen tracks converged after 3 reads,
  and track 3 hit the repeat limit as above. Track 5 converged on `E0036697`,
  which AccurateRip does not hold whole.
- **The first rip's securing pass** (`-Z 2 -l 3,5`): track 5 first read
  `C96464AB`, the one checksum of track 5 AccurateRip matches whole, then
  `E0036697` three times, and kept `E0036697`, the third run in a row to do
  so (2026-10-12, 2026-10-13). The log cannot show that `C96464AB` matches,
  since only the kept read is looked up.
- **`-f` found `+667` at confidence 14** (`session/transcript.txt:1164`), the
  fifth run to do so and the first on `.23`.
- **The cache probe said `128 to 255 sectors`** (uncached read 244.5 ms,
  cached 1.7 ms, three re-reads after a 256-sector run at 31.9 ms or more,
  `session/transcript.txt:1232`), beside `cd-paranoia -A`'s **137 sectors**
  (`session/run/cacheprobe1347.txt`). The fifth run in agreement.
- **The cancel** (L863, `info`): podman does not forward the wrapper's
  SIGTERM, so the ripper still held the drive when Platterpus's rescue fired
  5 s after Cancel, and it signed its log after the rescue's SIGTERM, as on
  2026-10-13.

**It shows no defect in what `.23` changed.** The one defect of ours it
shows, track 4's pregap read as zero, is old and recorded, moves no audio
byte, and was in the build round 33 approved. Our round 34 lap 1 S16 said
our first lap after this run is `GO` unless the run shows a defect in `.23`
that makes the pin unsafe; this reading finds none. The one finding for
Platterpus is the build tag their runner took from a refused rip. This is our
reading of round 34's run; round 34's S14 needs Platterpus's too, in a lap
of theirs.

**Every fact above can be re-derived** with `tools/read-run.py
docs/rig-2026-10-16-891c79e --cyanrip build/src/cyanrip`, beside
`tools/ingest-bundle.py`'s verdict on the bundle itself.
