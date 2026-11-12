# Rig session 2026-11-11 — build `e531a33` (`.31`), Platterpus 0.7.122, **Full**, round 39's five-rip run

**Reworded 2026-11-12**, on the owner's word that a burn writes a disc (Platterpus's
round 39 lap 4 S10): round 39's five back-to-back rips are the five-rip run here. The
evidence's folder names keep the word their runner gave them.

**Read the build, not the date.** `.31` at `e531a33` and Platterpus **0.7.122**
(tag `v0.7.122`, the newest when the run began at 12:34:47Z). The paired rips
`accuracy A1` to `A4` and `timing A1` and `A2` ran `.30` at `5cc1c6b`; every
other cyanrip log opens with `platterpus-fork-ge531a33`. It is round 39's
five-rip run, the run our round 39 lap 1 S16 closes on.

**The script's verdict is not a pass**: pass 651, fail 1, error 0, unreachable
1, info 22 (`session/run/report.json`). The one failure is `expect-ctdb whole`
(`session/run/transcript.txt`, L1389), on the whole-disc secure re-read,
grading track 5's read, as on 2026-11-10. The unreachable step is
`expect-offset-refusal` (L625), which this drive cannot reach.

**Every member matches the sender's own hash**: 275 of 275. All 35 signed
cyanrip logs, the securing passes included, verify with `-Y`, and every one of
the 29 rip logs ends with its signed completion footer. This is the first
filing that carries cyanrip's `--diagnostics` records: 83 of them, under
`ripperdiagnostics/`, which `tools/ingest-bundle.py` dropped until this filing.

## What it establishes

1. **The five rips.** Each is a default whole-disc rip of `.31` through
   0.7.122, followed by Platterpus's securing pass of tracks 3 and 5,
   `-Z 2 -r 5 -l 3,5 --reread-until-accuraterip 2 --reread-time-limit 1457`
   (each folder's `.platterpus-securing-pass.txt`).
   - **Track 3.** The whole-disc rip read it wrong in all five: `2AC1F945` in
     rip 1 and `3D8FCF0C` in rips 2 to 5, which AccurateRip does not find. The
     securing pass delivered `59D352DD` in all five, which AccurateRip matches
     (v1 `3C8BDDD2` at confidence 128, v2 `96DF8C22` at 200).
   - **Track 5.** It read `E0036697` in every whole-disc rip and every
     securing pass, which AccurateRip matches at frame 450 only.
   - **Platterpus's transcript, for each rip,** reads AccurateRip verifying
     tracks 1 to 4 and 6 to 14, and track 5 "repaired from CTDB", its repaired
     audio "verified by AccurateRip v2 BCF4E815 (confidence 200)" (L1909,
     L1919, L1929, L1939, L1949). The repair and that reading are theirs.
2. **`--reread-until-accuraterip` ran on a drive for the first time**, and
   printed what our round 39 lap 1 S4 announced.
   - **Rip 3's securing pass, track 3.** The reads agreed on `3D8FCF0C`
     three times. Read 4 was `59D352DD`, and the track ended there:
     `Done; (read 4 matches AccurateRip at confidence 200; agreement on
     3D8FCF0C overruled by AccurateRip; kept 59D352DD, read 1 time)`, then
     `Secure re-read:  matched AccurateRip after 4 reads (agreement on
     3D8FCF0C overruled)`.
   - **Track 3 in the other four passes.** `-Z` agreed on `59D352DD` itself:
     after 3 reads in rips 1, 2 and 5, and after 5 reads in rip 4, which also
     read `2AC1F945` and `5D24EB87`.
   - **Track 5, in all five passes.** The agreement on `E0036697` was
     overruled, no read matched AccurateRip, and the pass ended at `-r`'s 5
     reads, keeping `E0036697` with the clause on the `Done;` line.
   - **The footer** reads `Secure re-reads: 1 track did not converge (track
     5)` in every pass.
3. **G4's comparison, from the records.** Every wrong read of track 3 differs
   from `59D352DD` in exactly one second of the track, and track 5's only other
   value differs from `E0036697` in one second:

   | Track | Value | Differs from | In second | Records holding it |
   |---|---|---|---|---|
   | 3 | `2AC1F945`, `3F5462BB`, `5D24EB87` | `59D352DD` | 244 (04:04) | 2, 1, 1 |
   | 3 | `3D8FCF0C`, `15D16895`, `E45FCE56` | `59D352DD` | 251 (04:11) | 9, 1, 1 |
   | 3 | `E5BEB068` | `59D352DD` | 252 (04:12) | 1 |
   | 5 | `6902BCF0` | `E0036697` | 144 (02:24) | 6 |

   - **How it was read.** Each value's per-second CRCs are the same in every
     record holding it; `59D352DD` is in 15 records and `E0036697` in 55.
   - **Track 5 against CTDB.** Platterpus's report puts `E0036697`'s
     difference from CTDB's 1,425-submission entry at "3 samples @02:24:59",
     inside second 144.
   - **What it shows.** On this drive, track 3's misreads fall in three
     seconds near its end, and track 5's in one.
4. **Track 3, by kind of rip, across every record of the run.**
   - **Right (`59D352DD`):** all 8 paired `accuracy` rips, 4 on `.30` and 4 on
     `.31`; the first whole-disc rip of the run; all 5 securing passes.
   - **Wrong:** all 4 `timing` rips (`3D8FCF0C` three times, `E5BEB068`); all
     5 rips' whole-disc reads; the whole-disc secure re-read.
   - **The secure re-read.** It ran `-Z 2` without
     `--reread-until-accuraterip`, so its agreement on `3D8FCF0C` (reads 1
     and 4) ended the track. Platterpus's chase then read `3F5462BB` and
     `59D352DD`.
   - **The comparison with 2026-11-10.** The paired `accuracy` rips read track
     3 right in 0 of 8 on 2026-11-10 and in 8 of 8 here. Nothing in the build
     decides it.
5. **Track 5 never read `C96464AB` from this drive.** Its 58 records keep
   `E0036697` 55 times and `6902BCF0` 3 times, 45 of them from Platterpus's
   chase of track 5.

## What it does not establish

- **G4's other half.** No C2 probe ran in this session, so whether the drive
  flags the samples in seconds 144, 244, 251 and 252 is still unmeasured.
- **G5.** The owner's EAC re-rip is not in this bundle.
- **Why the reads land where they do.** Nothing here varies anything that
  changes it.
- **What the run says against S16.** That is each side's lap.

## Questions, gaps and next time

**Questioned:**
- **Platterpus's whole-disc secure re-read sends `-Z 2` without
  `--reread-until-accuraterip`**, so it kept the wrong `3D8FCF0C` by agreement
  before their chase replaced it. Theirs to say whether that step should send
  the option (round 39 lap 3).
- **Track 3's per-second differences sit in three seconds, 244, 251 and 252.**
  Whether CTDB places this disc's wrong track 3 in the same seconds is
  Platterpus's to derive.

**Possibly missing:**
- **The C2 probe's output**, which G4 needs.
- **The EAC re-rip**, which G5 needs.

**To add next time:**
- **The C2 probe at seconds 144, 244, 251 and 252**, not only at round 38's
  five LBAs. These are the samples the records name.

**More than we asked:**
- **Every rip's `--diagnostics` record** (our round 39 lap 1 S10), and with
  them the per-second CRCs of every distinct read of tracks 3 and 5: eight
  values of track 3 and two of track 5.
