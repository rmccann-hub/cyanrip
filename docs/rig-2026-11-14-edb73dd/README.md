# Rig session 2026-11-14 — build `edb73dd` (`.32`), Platterpus 0.7.125, **Full**, round 40's rip

**Read the build, not the date.** `.32` at `edb73dd` and Platterpus **0.7.125**
(build `553a2d8`, tag `v0.7.125`, the newest when the run began at
02:12:01Z). The paired rips `accuracy A1` to `A4` and `timing A1` and `A2` ran
`.31` at `e531a33`; every other cyanrip log opens with
`platterpus-fork-gedb73dd`. It is round 40's rip, the run our round 40 lap 1
S10 closes on: one default whole-disc rip of `.32` through Platterpus's first
release naming it under review. Their runner ran five, in folders it still
names `round 39 repeat rip 1` to `5`, beside the full acceptance rip and the
whole-disc secure re-read.

**The script's verdict is not a pass**: pass 650, fail 2, error 0, unreachable
1, info 22 (`session/run/report.json`). Both failures are `expect-ctdb whole`
(`session/run/transcript.txt`, L786 and L1389), on the full acceptance rip and
the whole-disc secure re-read, grading track 5's read, as on 2026-11-10 and
2026-11-11. The unreachable step is `expect-offset-refusal` (L625), which this
drive cannot reach.

**Every member matches the sender's own hash**: 268 of 268. All 36 signed
cyanrip logs verify with `-Y`: 6 on `.31`, and 30 on `.32`, 23 rips and 7
securing passes. Every one of the 29 rip logs ends with its signed completion
footer. The bundle carries 76 `--diagnostics` records, and each of the 36 logs
names one that is in it.

## What it establishes

1. **The `C2 errors:` line, round 40's G1.**
   - **On `.32`.** All 23 rip logs, all 7 securing passes and all 39 logs in
     Platterpus's chase files print `C2 errors:      not declared by drive
     (capabilities page, not measured)` (rip 1's log, line 14).
   - **On `.31`.** The 6 paired-rip logs print `unsupported by drive`.
   - **In Platterpus's records.** Every rip's `.platterpus.json`, all 27,
     keeps `rip.c2_declared` as `not_declared`. Its reason is `capabilities
     page, not measured` on `.32`, and null on `.31`. Each record also carries
     `disc.drive_declared.cd_read_feature.c2_flags: true`. Our own 76
     `--diagnostics` records carry that feature as `001E0904 03…`, byte 4
     `03h`, C2 Flags set. Page 2Ah's "no" and that feature's "yes" are the
     drive's two disagreeing C2 answers that our round 38 lap 14 S7 read. The
     records are named with their hashes in `SHA256SUMS`, not filed;
     `tools/ingest-bundle.py` files only cyanrip's own JSON. They were read
     from the archive.
2. **The five rips, round 40's G2.** Each is a default whole-disc rip of `.32`
   through 0.7.125 (`-s 667 -o flac -r 5 --prefer-disc-isrc
   --prefer-accuraterip-match`). Platterpus's securing pass of tracks 3 and 5
   follows it, `-Z 2 -r 5 -l 3,5 --reread-until-accuraterip 2
   --reread-time-limit 1457` (each folder's `.platterpus-securing-pass.txt`).
   - **Tracks 1, 2, 4 and 6 to 14.** AccurateRip verified each on the
     whole-disc read, in all five rips.
   - **Track 3, the whole-disc reads.** All five were wrong: `2E36401F` in
     rip 1, `0D427962` in rip 2, `3D8FCF0C` in rips 3 and 4, and `80035387`
     in rip 5. AccurateRip matches each at frame 450 only.
   - **Track 3, the securing passes.** The passes of rips 1, 3, 4 and 5
     delivered `59D352DD`, which AccurateRip matches (v1 `3C8BDDD2` at
     confidence 128, v2 `96DF8C22` at 200). Rip 2's pass overruled its
     agreement and ended at the limit, keeping `3D8FCF0C`: `Done; (repeat
     limit of 5 reads reached; at most 3 reads agreed; agreement on 3D8FCF0C
     overruled by AccurateRip; last read 2363932F, not kept)` (rip 2's
     securing pass, line 83).
   - **Track 3, rip 2's chase.** Platterpus's chase then read it in single
     rips of `-l 3`: `3D8FCF0C` six times, `2363932F` twice, and `59D352DD`
     on the ninth (the folder's `.platterpus-verified-read.txt`, line 1543 on).
     So track 3 is `59D352DD` from a drive read, with no repair, in all five.
   - **Track 5, the reads.** Every securing pass kept `E0036697`, and rip 3's
     also read `6902BCF0` twice. The whole-disc reads of rips 2 to 5 were
     `E0036697`; rip 1's was `6902BCF0`. AccurateRip matches `E0036697` at frame 450 only. The chases
     of rips 1 and 3, fifteen reads each, read `E0036697` 29 times and
     `6902BCF0` once.
   - **Track 5, the repair.** Platterpus's record repairs it from CTDB entry
     32115 to `C96464AB` in all five, the repaired audio "verified by
     AccurateRip v2 BCF4E815 (confidence 200)" (transcript L1909, L1919,
     L1929, L1939, L1949). The repair and that reading are theirs.
3. **What `.32` changed, on a drive.**
   - **The footer's third form.** It did not print in any log, and could not
     have: track 5 converged in no `-Z` pass. Every pass's footer names it,
     `Secure re-reads: 1 track did not converge (track 5)` five times, and
     `2 tracks did not converge (tracks 3, 5)` three times.
   - **`Still waiting:`.** No log prints it, and all 75 logs, chases
     included, say `Read stalls:    none (no read exceeded 10s)`.
   - **What that leaves.** Of `.32`'s three changes, only the C2 line was
     exercised on this drive.
4. **Every read of tracks 3 and 5, by second, from the 70 `.32` records.**
   Every value's per-second CRCs are the same in every record holding it. Each
   wrong value differs from the right one in one or two seconds:

   | Track | Value | Differs from | In seconds | Records |
   |---|---|---|---|---|
   | 3 | `2AC1F945`, `ABD0A042`, `2E36401F`, `0D427962`, `B4B3EE53` | `59D352DD` | 244 (04:04) | 1, 2, 1, 1, 1 |
   | 3 | `12D83BD0`, `F2B0AB0B` | `59D352DD` | 245 (04:05) | 1, 1 |
   | 3 | `EAC1AA44` | `59D352DD` | 244 and 245 | 1 |
   | 3 | `3D8FCF0C`, `2363932F`, `80035387` | `59D352DD` | 251 (04:11) | 12, 3, 1 |
   | 3 | `4C88B732`, `58322CE3` | `59D352DD` | 251 and 252 | 1, 1 |
   | 3 | `C553E601` | `59D352DD` | 252 (04:12) | 1 |
   | 5 | `6902BCF0` | `E0036697` | 144 (02:24) | 3 |

   - **What is new.** Second 245 is new. Round 39's run placed track 3's
     misreads in 244, 251 and 252 only.
   - **Values new to our record.** Eight values are new: `ABD0A042`,
     `58322CE3`, `2E36401F`, `0D427962`, `12D83BD0`, `B4B3EE53`, `F2B0AB0B`
     and `EAC1AA44`. Each was searched case-blind, and none is found on the
     evidence branch at `74b6f0a` or in `platterpus-fork` at `97bfd984`.
   - **Where `59D352DD` and `E0036697` appear.** `59D352DD` is in 13 records,
     and `E0036697` in 42.
5. **The paired rips.**
   - **Accuracy.** Track 3 was right in 4 of 4 rips on each build (L1850).
   - **Timing.** The timing ratios agree: B1/A1 1.003, and B2/A2 0.998
     (L1719). `timing A2`, on `.31`, read track 3 as `3D8FCF0C`.
6. **The cache, the thirty-fourth row.** Our `--cache-probe` gave `128 to 255
   sectors`, with an uncached read of 362.9 ms and a cached read of 1.3 ms
   (`session/transcript.txt`, line 1360, step L1483). `cd-paranoia -A`, the
   next step, L1484, measured 140 (line 1513).
7. **Platterpus's whole-disc secure re-read now sends
   `--reread-until-accuraterip 2`.** Our round 39 reading questioned that it
   did not. Its track 3 read `4C88B732` twice, `3D8FCF0C`, `58322CE3` and
   `3D8FCF0C`.
   - **No agreement formed.** Under `-Z 2` an agreement is three identical
     reads, so none formed and none was overruled. `Done; (repeat limit of 5
     reads reached; at most 2 reads agreed)` is exact.
   - **The read kept.** It kept `3D8FCF0C`, the newest of the two reads given
     twice, by the rule at `src/spool.h:49`.

## What it does not establish

- **`.32`'s footer third form and its `Still waiting:` names on a drive.**
  Neither printed.
- **Whether the drive flags second 245.** No C2 probe ran in this session.
- **Why the reads land where they do.** Nothing here varies anything that
  changes it.
- **What the run says against round 40's S10.** That is each side's lap.

## Questions, gaps and next time

**Questioned:**
- **Platterpus's records give `kept_read_began` as the whole-disc read's time
  for tracks 3 and 5 in all seven whole-disc rips**, 14 of 14, including track
  3, whose files carry a later read.
  - **Rip 1, track 3.** The record keeps `59D352DD`, which the securing pass
    read (its line 112, `Kept read began: 2026-11-14T05:21:02Z`). Its
    `kept_read_began` is `2026-11-14T05:02:54Z`, the whole-disc read's
    (rip 1's log, line 260), and that read was `2E36401F`.
  - **Rip 2, track 3.** The record keeps chase attempt 9's `59D352DD`, begun
    `2026-11-14T06:36:53Z` (the chase file, line 1650), and gives the
    whole-disc read's `05:53:04Z`.
  - **Who settles it.** Platterpus's, to say which read the field describes.
- **Rip 1's track 5 record.** It reads "repaired from CTDB entry 32115
  (confidence 1,429) after the read (re-read, at most 5 agreeing): Copy CRC
  6902BCF0 before, C96464AB after, 6 samples corrected".
  - **What the logs show.** `6902BCF0` is the whole-disc read, a single read
    (rip 1's log, line 418). The securing pass's five reads agreed on
    `E0036697` (its line 169).
  - **What the record mixes.** Its parenthetical describes the pass, and its
    CRC and sample count describe the whole-disc read.
  - **Rip 3's record.** It says "at most 3 agreeing", its pass's count, over
    the whole-disc read's `kept_read_began`.
  - **Who settles it.** Platterpus's: which read the repair started from, and
    which read the parenthetical names.

**Possibly missing:**
- **A C2 probe at second 245 of track 3.** It is the first wrong second there
  that no probe has asked about.

**To add next time:**
- **The C2 probe at seconds 144, 244, 245, 251 and 252.** These are every
  second the records name, and round 39's reading asked for four of them.

**More than we asked:**
- **Five whole-disc rips where round 40 asked for one**, each with its
  securing pass, plus the full acceptance rip and the whole-disc secure
  re-read: seven whole-disc reads of `.32`.
- **Every rip's `--diagnostics` record, 76 of them**, 39 of them Platterpus's
  single-track chase reads, so each chased read is placed by second too.
