# Rig session 2026-11-17 — build `fb28088` (`.34`), Platterpus 0.7.127, **Full**, round 41's rip

**Read the build, not the date.** `.34` at `fb28088` and Platterpus **0.7.127**
(build `69483cf`, tag `v0.7.127` of 00:20:40Z, the newest when the run began at
01:14:14Z). The paired rips `accuracy A1` to `A4` and `timing A1` and `A2` ran
`.32` at `edb73dd`; every other cyanrip log opens with
`platterpus-fork-gfb28088`. It is round 41's rip, the run our round 41 lap 3
S10 closes on, which Platterpus's lap 4 S5 accepted: one default whole-disc
rip of `.34` through their first release naming it under review. Their runner
ran five, `repeat rip 1` to `5`, beside the full acceptance rip and the
whole-disc secure re-read.

**The script's verdict is not a pass**: pass 649, fail 3, error 0, unreachable
1, info 22 (`session/run/report.json`). Two failures are `expect-ctdb whole`
(`session/transcript.txt`, L786 and L1389), on the full acceptance rip and the
whole-disc secure re-read, grading track 5's read, as on 2026-11-10, 2026-11-11
and 2026-11-14. The third is new: `expect-deemphasis-pair r16deemphon
r16deemphoff` (L1637), because the drive misread track 1 in one arm (item 6).
The unreachable step is `expect-offset-refusal` (L625), which this drive cannot
reach.

**Every member matches the sender's own hash**: 230 of 230. All 36 signed
cyanrip logs verify with `-Y`: 6 on `.32`, and 30 on `.34`, 23 rips and 7
securing passes. Every one of the 29 rip logs ends with its signed completion
footer. The bundle carries 43 `--diagnostics` records, and each of the 36 logs
names one that is in it. The other 7 are Platterpus's six chase reads of
track 3 in `repeat rip 5` and the first `overwrite answers` rip, whose log the
second one replaced.

## What it establishes

1. **The drive's declared read performance, round 41's G1.**
   - **In our record.** All 37 `.34` records, `cyanrip-diagnostics/14`, hold
     `drive_declared.read_performance` with `answered: true`, 24 bytes,
     `000000140000000000000000000003F4000419A2000009A5`, and one descriptor:
     `start_lba` 0 at `start_kb_per_s` 1012, `end_lba` 268706 at
     `end_kb_per_s` 2469. The four fields were decoded again from the bytes
     here and agree. 268706 is one sector short of `Total time: 59:42.57`,
     268,707 sectors.
   - **What it says.** The drive declares one ramp, rising from 1012 to 2469
     kilobytes of 1000 bytes a second across the disc: 5.7 and 14.0 times
     176.4. It is what the drive declared when asked, not a measured speed;
     no `-S` was sent, and every log prints `Speed:          default (drive
     not asked whether it can change speed)`.
   - **On `.32`.** The 6 paired-rip records are `/13` and have no such key.
   - **In Platterpus's records.** Their 27 `.platterpus.json` records keep
     `disc.drive_declared` without `read_performance`; their lap 2 S4 said no
     reader of theirs reads it yet. G1 asks for it in the rip's record, which
     is ours. The records are named with their hashes in `SHA256SUMS`, not
     filed; `tools/ingest-bundle.py` files only cyanrip's own JSON. They were
     read from the archive.
2. **The five rips, round 41's G2.** Each is a default whole-disc rip of `.34`
   through 0.7.127 (`-s 667 -o flac -r 5 --prefer-disc-isrc
   --prefer-accuraterip-match`). Platterpus's securing pass of tracks 3 and 5
   follows it, `-Z 2 -r 5 -l 3,5 --reread-time-limit 1457
   --reread-until-accuraterip 2` (each folder's
   `.platterpus-securing-pass.txt`).
   - **Tracks 1, 2, 4 and 6 to 14.** AccurateRip verified each on the
     whole-disc read, in all five rips.
   - **Track 3, the whole-disc reads.** Rips 2, 3 and 4 read `59D352DD`,
     which AccurateRip matches (v1 `3C8BDDD2` at confidence 128, v2
     `96DF8C22` at 200). Rips 1 and 5 read `3D8FCF0C`, which it matches at
     frame 450 only.
   - **Track 3, the securing passes.** Rip 1's pass kept `59D352DD` at the
     limit: `Done; (repeat limit of 5 reads reached; at most 2 reads agreed;
     kept 59D352DD, read 2 times, which AccurateRip matches at confidence 200;
     last read E9248186, not kept)` (its line 83). Rip 5's pass read
     `3D8FCF0C` four times and `73C78A94` once, and overruled the agreement:
     `agreement on 3D8FCF0C overruled by AccurateRip` (its line 83).
   - **Track 3, rip 5's chase.** Platterpus's chase then read it in single
     rips of `-l 3`: `E45FCE56`, `3D8FCF0C` four times, and `59D352DD` on the
     sixth (the folder's `.platterpus-verified-read.txt`, line 1077), which
     the record keeps. So track 3 is `59D352DD` from a drive read, with no
     repair, in all five.
   - **Track 5, the reads.** Every read of track 5 in the session is
     `E0036697`: every whole-disc read and every pass read, all five agreeing
     in each of the seven passes and in the secure re-read. `6902BCF0`, read four times on 2026-11-14,
     did not appear. AccurateRip matches `E0036697` at frame 450 only.
   - **Track 5, the repair.** Platterpus's record repairs it from CTDB entry
     32115 (confidence 1,431) to `C96464AB` in all five, "3 samples
     corrected", the repaired audio matched by AccurateRip v1 `134C0B9D`
     (confidence 129) and v2 `BCF4E815` (confidence 200). The repair and that
     reading are theirs. On 2026-11-14 rip 1's repair started from
     `6902BCF0` and corrected 6.
   - **So G2 holds in each of the five** as round 40's did, track 5 by the
     labeled repair (our round 40 lap 3 S4). The full acceptance rip and the
     whole-disc secure re-read hold it the same way.
3. **What `.34` changed, on a drive.**
   - **`-f`.** Its search ran (L1423): `Offset of +667 confirmed (confidence:
     N) in track N` for each of the 14 tracks, then `Drive offset of +667
     found (confidence: 14)!` (`session/transcript.txt`, line 1304). Each line
     names its track by its own number. Neither half of `8610f3c1` is
     distinguished here: this disc numbers its tracks from 1, so a track's
     number and its position plus one agree, and the drive's offset is not 0.
   - **The rest.** No log prints `Still waiting:`, and all 29 rip logs and
     the 13 pass and chase outputs say `Read stalls:    none (no read exceeded
     10s)`. The disc has no data track and no CD-TEXT, and its cover is a
     JPEG, so the data-track cancel, the ISRC check and the cover formats did
     not run on it.
   - **What that leaves.** Of `.34`'s changes, only `-f` ran on this drive,
     and the disc could not tell its fix from the old code.
4. **Every read of tracks 1, 3 and 5, by second, from all 43 records.** Every
   value's per-second CRCs are the same in every record holding it. Each wrong
   value differs from the right one in one or two seconds:

   | Track | Value | Differs from | In seconds | Records |
   |---|---|---|---|---|
   | 1 | `64CA69D1` | `B0D122E7` | 162 (02:42) | 1 |
   | 3 | `061D2412` | `59D352DD` | 240 (04:00) | 1 |
   | 3 | `253ACDBF`, `52DFDF7D` | `59D352DD` | 244 (04:04) | 1, 1 |
   | 3 | `5D061F9B` | `59D352DD` | 244 and 245 | 1 |
   | 3 | `E9248186` | `59D352DD` | 244 and 251 | 1 |
   | 3 | `3D8FCF0C`, `80035387`, `E45FCE56` | `59D352DD` | 251 (04:11) | 14, 2, 2 |
   | 3 | `73C78A94` | `59D352DD` | 251 and 252 | 1 |
   | 3 | `E5BEB068` | `59D352DD` | 252 (04:12) | 1 |

   - **What is new.** Second 240 of track 3 is new: no earlier run placed a
     misread there. Track 1's misread is placed by second for the first
     time: its one earlier read of `64CA69D1`, on 2026-09-28, came before
     `.29` put per-second CRCs in the record.
   - **Values new to our record.** Five are new: `061D2412`, `253ACDBF`,
     `5D061F9B`, `73C78A94` and `E9248186`. Each was searched case-blind, and
     none is found on the evidence branch at `589db536` or in
     `platterpus-fork` at `fd20a0ad`.
   - **Where the right reads appear.** `B0D122E7` is in 21 records,
     `59D352DD` in 8, and `E0036697` in 14.
5. **The paired rips.**
   - **Accuracy.** Track 3 was right in 0 of 4 rips on `.32` and 1 of 4 on
     `.34` (L1850). On 2026-11-14 it was right in 4 of 4 on each build.
   - **Timing.** The timing ratios agree: B1/A1 1.001, and B2/A2 0.995
     (L1719). All four timed rips read track 3 wrong, at frame 450 only.
6. **The de-emphasis pair, the run's new failure.** Both arms rip track 1 with
   `-s 667 -l 1 -H`, one with `-E` and one with `-W`. The `-W` arm read
   `B0D122E7`, which AccurateRip matches. The `-E` arm read `64CA69D1`, which
   it matches at frame 450 only, with `FIXUP_ATOM: 12`. The `-W` arm has
   none. A fix-up does not by itself mean a misread: the first `overwrite answers` rip,
   whose log was replaced, has `FIXUP_ATOM` 16 in its record and read
   `B0D122E7`.
   - **It is the read, not the filter.** Our checksums are taken on the read
     buffer, before any filter (`src/cyanrip_encode.c:816`). The AccurateRip
     database is the independent witness: its frame 450 matches the `-E`
     arm's read at confidence 200, which a de-emphasised signal could not do.
     The two reads differ in second 162 alone (item 4).
   - **The same misread happened before.** `64CA69D1` is filed once already,
     in the `-H -W` arm of 2026-09-28c (`docs/rig-2026-09-28c-51cc789/`): the
     same bytes, seven weeks apart, once in each arm. Of the 40 de-emphasis
     rips of this disc, 38 filed and these two, all on this drive, 38 read
     `B0D122E7` and 2 read `64CA69D1`.
   - **What their check said.** Their check reports it as it is: `the two
     arms READ different audio (track(s) 1), so a loudness difference cannot
     be put down to de-emphasis`. No `.34` defect follows from it.
7. **The cache, the thirty-fifth row.** Our `--cache-probe` gave `128 to 255
   sectors`, with an uncached read of 362.8 ms and a cached read of 1.3 ms,
   and three re-reads after 256 sectors of 59.1 ms or more
   (`session/transcript.txt`, line 1372). `cd-paranoia -A`, step L1484,
   measured 140 (line 1525).
8. **Track 9's pregap.** It is `94 or 95 frames (undecided)` in 32 of the 36
   logs and 95 in 4: `derived wav` and three securing passes. No log says 94.
9. **The secure re-read.** Its track 3 read `3D8FCF0C` five times in five
   reads, and the rule overruled that agreement: `Done; (repeat limit of 5
   reads reached; at most 5 reads agreed; agreement on 3D8FCF0C overruled by
   AccurateRip)` (its log, line 251). Its securing pass read `061D2412`, then
   `59D352DD` three times, and converged (that file, line 81). The footer of
   the re-read is `Secure re-reads: 2 tracks did not converge (tracks 3, 5)`;
   no log printed the third form.

## What it does not establish

- **`.34`'s fixes on a drive.** `-f` ran on a disc that cannot show either
  half; the rest did not run.
- **`.32`'s footer third form and the `Still waiting:` names, `.34`'s two
  included.** Neither printed.
- **Whether the drive flags seconds 162, 240, 244, 245, 251 or 252.** No C2
  probe ran in this session.
- **Why the reads land where they do.** Nothing here varies anything that
  changes it.
- **What the run says against round 41's S10.** That is each side's lap.

## Questions, gaps and next time

**Questioned:**
- **Platterpus's secure re-read record names a build the log is not from.**
  For 13 of its 14 tracks it says "whether the fork's .31 AccurateRip-guided
  -Z rule chose this read is not determined (this release does not read that
  build's log)".
  - **What the log shows.** The log is `.34`'s. Each of those tracks' kept
    read ends in the agreement form, as track 1's does: `Done; (2 out of 2
    matches for current checksum B0D122E7)` (line 78), with `Secure re-read:
    converged after 3 reads` (line 119). Track 3's kept read is its securing
    pass's, which ends the same way (that file, line 81). On `.34` the rule
    prints its own clause whenever it overrules an agreement, as it did for
    tracks 3 and 5 (lines 251 and 427).
  - **Who settles it.** Platterpus's: which build "that build" names, and
    whether the agreement form settles what chose the read.
- **Their de-emphasis check still asks a question we answered.** Its output
  ends "the fork is asked to confirm where it measures loudness (our round 37
  lap 6, S12 (d))". Our round 37 lap 7 S4 (d) answered it: loudness is
  measured on what the encoders receive, after the filter, since `.20`, and
  the checksums stay on the read buffer. Platterpus's to retire.

**Possibly missing:**
- **A C2 probe at second 240 of track 3, and at second 162 of track 1.** No
  probe has asked about either.

**To add next time:**
- **The C2 probe at seconds 144 of track 5, 240, 244, 245, 251 and 252 of
  track 3, and 162 of track 1.** These are every second the records name.
- **The de-emphasis pair read twice, or with `-r 5`,** so a single misread
  arm does not end the comparison. That is Platterpus's script to change.
- **`-f` on a disc numbered from other than 1, or a drive whose offset is
  0.** Only that can show `8610f3c1` on a drive.

**More than we asked:**
- **Five whole-disc rips where round 41 asked for one**, each with its
  securing pass, plus the full acceptance rip and the whole-disc secure
  re-read: seven whole-disc reads of `.34`.
- **Every rip's `--diagnostics` record, 43 of them**, six of them
  Platterpus's single-track chase reads, so each chased read is placed by
  second too.
