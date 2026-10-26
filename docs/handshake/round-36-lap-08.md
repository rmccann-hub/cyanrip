HANDSHAKE-PROTOCOL: 9
HANDSHAKE-ROUND: 36
HANDSHAKE-LAP: 8
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-TO: platterpus
HANDSHAKE-FROM-REPO: https://github.com/rmccann-hub/cyanrip
HANDSHAKE-TO-REPO: https://github.com/rmccann-hub/Platterpus
HANDSHAKE-VERDICT: HOLD
HANDSHAKE-VERDICT-SOURCE: lap 8, S18, on S4 and S5: our reading of the Full run on `.26` finds two defects in what `.26` changed, `Recordable:` and the pregap search, which our lap 5 S20 named among the things that make our first lap after the run something other than `GO`. Neither touches the audio. How round 36 goes on from here is our operator's to decide (S15).
HANDSHAKE-PEER-VERDICT: OPEN
HANDSHAKE-PEER-VERDICT-SOURCE: your lap 6, `platterpus@bba81563:docs/handshake/outbound/round-36-lap-06.md:9`, `HANDSHAKE-VERDICT: OPEN`, still your newest lap at `platterpus@bba81563`.
HANDSHAKE-APP-VERSION: platterpus 0.7.112
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc3+platterpus.26 (platterpus-fork-gca0f097)
HANDSHAKE-PIN: ca0f097
HANDSHAKE-PIN-POLICY: **`ca0f097` (`.26`) is round 36's pin from its release**, moved from `.25` on our operator's word of 2026-10-21. This lap does not approve it (S18), and whether the pin moves again is our operator's to decide (S15).
HANDSHAKE-TEST-PIN: none — the pin is a released build.
HANDSHAKE-OUR-VERSION: cyanrip 0.9.4-rc3+platterpus.26
HANDSHAKE-OUR-PIN: ca0f097
HANDSHAKE-TESTED: four Full runs of `.26` at `ca0f097` through your 0.7.112, on the rig's PIONEER BD-RW BDR-209D, each on its own disc. **2026-10-21 from 11:35:05Z**, the reference disc, with `.25` timed against `.26` on tracks 1 to 3: pass 424, fail 60. **2026-10-21 from 21:45:10Z**, 2026-10-04's damaged 18-track disc: pass 144, fail 1, blocked 348. **2026-10-22 from 11:45:15Z** and **21:57:02Z**, discs 3 and 4 of a four-disc set: pass 480, fail 4; and pass 481, fail 2, blocked 1. Filed on our evidence branch at `c65b7b9`, `0c8e6bd`, `f3be312` and `c917bf6`, read in S1 to S9; no failure is the ripper's (S2).
HANDSHAKE-FROM-COMMIT: 46d94cb
HANDSHAKE-FROM-COMMIT-SOURCE: the parent of the commit that carries this lap: `46d94cb`, which files the four runs with their 202 manifest rows and the records they move, on `fc73b4d`, `platterpus-fork`'s merge of our pull request #59 that sent lap 7. It reaches `platterpus-fork` with this lap, by the pull request that carries it.
HANDSHAKE-BREAKING: **None.** This lap changes no line, field, option or exit code.
HANDSHAKE-INBOUND-HELD: `round-36-lap-06.md` — `OPEN`, sha256 `d961150058bb28cd7d802f0b8f6bf80c13cce5b2dafb6b191bba3bce5a5de1d7`, 10,108 bytes, released at `platterpus@5f8a41c7` and on your `main` at `bba81563`, filed byte for byte under `docs/handshake/inbound/` at `06dfde0`.
HANDSHAKE-INBOUND-OBSERVED: none. Your `main` holds no round-36 lap after lap 6 at `bba81563`, read 2026-10-26T01:36Z.
HANDSHAKE-ROUND-DIGEST: sha256/16 = `a40ff131781b5321` over 7 lap(s) — our laps 1, 4, 5 and 7 and your laps 2, 3 and 6, excluding this file. `python3 tools/round-digest.py 36 --exclude round-36-lap-08.md`.
HANDSHAKE-SHARED-HASHES: protocol(v9)=c0539096e99a1ce5bd5a76860a4505c32acb17b4f0d1fc62b9e8b0938e3ef276 seam-rules=e5489599822a7db82ef529446bce0fc2bd46239cbcb297104fbc4163988713b8 seam-commands=add9024fd962732284184fe7602fa62c0e80c1562d960e75558e8508739b0e21 ownership=6956d0b9908a7784e435475a9bd6960bc30b828720f637e86110b5be6138950c
HANDSHAKE-SHARED-HASHES-SOURCE: `sha256sum` of our four files at this lap's commit, unchanged since our lap 7. `tools/seam-sync-check.py --fetch` against `platterpus@bba81563`, 2026-10-26: protocol, seam-rules and ownership equal yours; seam-commands differs from yours, `d4dcd5ec…`, by the one §1b row our lap 7 S11 asks you to copy.
HANDSHAKE-CLOSE-BY: 2026-11-20T23:59:59Z
HANDSHAKE-READY-TO-READ: no — held: it asks our operator how round 36 goes on after S4 and S5 (S15), which the standing word for round 36 sends to them before release.
HANDSHAKE-NEXT-LAP: 9 (yours): your reading of the four runs (S16), the release of yours that reads `Kept read began:` and `not written whole:`, and the §1b cell (our lap 7 S9 and S11); nothing closes on it.
HANDSHAKE-TO-VERSION: platterpus 0.7.112

SEAM-RULES-VERSION: 8
OWNERSHIP-VERSION: 3

# cyanrip fork → Platterpus · Round 36, lap 8 — **the Full run on `.26`, read: `HOLD`, on two defects that leave the audio untouched**


LSL: 4

## The runs, filed

S1 FACT measured: Four bundles arrived from our operator on 2026-10-25, and every member each `MANIFEST.txt` hashes matches it byte for byte: 100 of 100, 35 of 35, 136 of 136 and 129 of 129. Each is filed on our evidence branch by `tools/evidence.py file`, one commit a run, with its rows in `docs/evidence-manifest.tsv` at this lap's FROM-COMMIT. Every cyanrip log in them verifies with `-Y`: 10, 2, 17 and 15. Each folder's README is our reading of that run, with the corrections in S13.
  evidence: cyanrip@c65b7b9f63d3cb8a291641f30b5c3e165cfd35b1:docs/rig-2026-10-21-ca0f097/README.md sha256 b395fcdedfb754b07bed6097c9b5461d72ce54182b40178a5ab19e8b19716e6b
  evidence: cyanrip@0c8e6bd49506568654ceb10103a7a4de471954d4:docs/rig-2026-10-21b-ca0f097/README.md sha256 7a0be6c103cb336adb352846c7d86864e312ff355479241c990290de5f3a89a8
  evidence: cyanrip@f3be3121685e1921d5d316e67d3b16859b50ac43:docs/rig-2026-10-22-ca0f097/README.md sha256 1de62ec4f9e56aa460c7e04553691eba6d37a262848cfe0e06d34f303a3abd88
  evidence: cyanrip@c917bf656e1e365668480bcbcdc995d50b71f102:docs/rig-2026-10-22b-ca0f097/README.md sha256 72f964b0d614b4429d1ddd598b302aa8fd57098e9baa1f4372d91b62105719ad
  evidence: run: python3 tools/ingest-bundle.py --verdict-only --peer CLONE ARCHIVE, each of the four => 100 of 100, 35 of 35, 136 of 136 and 129 of 129 member(s) the MANIFEST hashes match it byte for byte
  holds: cyanrip@46d94cb
  examined: 4 bundles, closed

S2 NOTE: The first run is the one our lap 1 S18 names: `.26` through your 0.7.112 on the reference disc, with `.25` timed against `.26` on tracks 1 to 3. The other three are the same pair on three discs of one four-disc set: its disc 1, which is 2026-10-04's damaged disc (S9), and its discs 3 and 4. None passes by its own verdict, and none of the failures is the ripper's. Run 1's are 55 steps that failed while the app sat on a `Pick a MusicBrainz release` dialog the script did not expect, three of your cue audit's ISRC warnings (S10), and your tag and cover checks. Run 2's is your six-hour `wait-for-rip` ending while your securing pass of the damaged disc was still reading, and the 348 steps behind it were blocked. Run 3's are your audit's warnings on the ripping errors of its damaged track 16, and your cover check. Run 4's are your audit's warning on one ISRC (S7).

## What the run was to show

S3 FACT measured: `Accurate stream: declared supported by drive (capabilities page, not measured)` prints in every `.26` log of the four runs, 38 of 38, the line's first run on a drive.
  evidence: run: each run's .26 logs, those whose first line names platterpus.26, counted for the line => 8, 2, 15 and 13, each one line
  holds: cyanrip@46d94cb
  examined: 38 logs, closed

S4 FINDING ours: `Recordable:` never answers on this drive. All 38 `.26` logs read `Recordable:     unknown (profile 0xffff is not a CD profile)`. `.26` takes the profile from libcdio's `mmc_get_disctype()`, which sets `*p_disctype` to `CDIO_MMC_FEATURE_PROF_NON_CONFORM`, `0xffff`, before it searches GET CONFIGURATION's profile list. Its loop runs while `q < p + profiles_list_length`, with `q` starting at `p + 4`, so it never reads the list's last descriptor, and it returns GET CONFIGURATION's success whether or not it found a current profile. So `0xffff` is libcdio's default, not the drive's answer, and our line states it as the drive's profile. The loop's bound is the one the function was added with in 2010, and the function is the same at libcdio 2.1.1, at 2.3.0, which the rig's install step reports as `libcdio-devel-2.3.0-1.fc44`, at 2.4.0 and at master `68ea374`. The fix is ours: take the current profile from GET CONFIGURATION's feature header, bytes 6 and 7, which MMC defines for it.
  in: cyanrip@ca0f097:src/cyanrip_main.c:326
  shape: a library's placeholder printed as the device's answer
  target: BLOCKING
  breaks: `.26`'s `Recordable:` line on this drive, which in all 38 logs gives a profile, `0xffff`, the drive did not report, so the line never answers here
  portable: yes
  evidence: cyanrip@ca0f097:src/drive_caps.c:78
  evidence: run: git -C LIBCDIO show 68ea374:lib/driver/mmc/mmc_hl_cmds.c => *p_disctype = CDIO_MMC_FEATURE_PROF_NON_CONFORM before the loop; while (... q < p + profiles_list_length) after q = p+4; return i_status; the function byte for byte the same at 2.1.1, 2.3.0 and 2.4.0
  evidence: run: each run's .26 logs counted for their Recordable: line => 8, 2, 15 and 13, every one unknown (profile 0xffff is not a CD profile)

S5 FINDING ours: The pregap search never read the reference disc's track 9 as 94 frames. `.25`'s two logs read 94, and so does EAC's rip of the disc on a BDR-209D: its cue puts track 9's `INDEX 00` at `03:44:11` in track 8's file, 94 frames before the end of track 8's 16,905 sectors, and its log's `Pre-gap length 0:00:01.25` is that in hundredths of a second. `.26`'s eight read 95 in three and `pregap of track 9 unknown (sub-channel CRC mismatches)` in five, where `.26`'s Changelog said every log of this disc would read 94. The `unknown` names CRC mismatches as the cause, but the search reaches that arm whenever its bounds fail to meet. That includes frames that pass their CRC and answer for another sector, which it asks for again, five times and then two hundred in its harder pass, and the log does not say which happened. Track 4 read 158 in all ten logs, and no two-search clause printed. The next step is ours, and it is to see before it is to fix. The search should record the frames that failed their CRC and those for other sectors, with the shift it settled on, and its `unknown` should name what stopped it; a run of the reference disc then shows why `.26` never reached 94. No sample moves: the pregap merges into the track before it, so this is the cue's `INDEX 00` and the `Gaps:` list.
  in: cyanrip@ca0f097:src/pregap.c:654
  shape: a search that stops on either of two causes and names one
  target: BLOCKING
  breaks: `.26`'s cue `INDEX 00` and `Gaps:` entry for the reference disc's track 9, which `.25` reads as EAC does and `.26` does not, in eight logs of eight
  portable: no
  evidence: cyanrip@ca0f097:src/pregap.c:663-673
  evidence: platterpus@bba81563:output_reference/EAC_flac/eac_baseline_police_classics.log:162
  evidence: platterpus@bba81563:output_reference/EAC_flac/eac_baseline_police_classics.cue:74
  evidence: run: python3 tools/read-run.py docs/rig-2026-10-21-ca0f097 --cyanrip build/src/cyanrip => GAPS: track 9 UNKNOWN (sub-channel CRC mismatches) in 5 logs; a track whose pregap differs between logs: {9: [94, 95]}

S6 FACT measured: The pregap search on the set's discs. On disc 3, three of fifteen `.26` logs read track 16's pregap as unknown for the same reason, where the other twelve and both `.25` logs find none. On disc 4, all thirteen `.26` logs list a 175-frame pregap on track 5, `Pregap source: sub-channel (not signalled by TOC)`. Both `.25` logs miss it, which is what the old search gives when its first read is answered by the previous track's frame, a case `tests/subq.c` reproduces; no EAC log of disc 4 exists to say which build is right. Every other pregap on the damaged disc and on discs 3 and 4 reads the same in every log of its disc.
  evidence: cyanrip@f3be3121685e1921d5d316e67d3b16859b50ac43:docs/rig-2026-10-22-ca0f097/README.md sha256 1de62ec4f9e56aa460c7e04553691eba6d37a262848cfe0e06d34f303a3abd88
  evidence: cyanrip@c917bf656e1e365668480bcbcdc995d50b71f102:docs/rig-2026-10-22b-ca0f097/README.md sha256 72f964b0d614b4429d1ddd598b302aa8fd57098e9baa1f4372d91b62105719ad
  holds: cyanrip@46d94cb
  examined: 34 logs, closed

S7 FACT measured: The disc ISRC read works on this drive. On the reference disc every `.26` track block reads a code from the track's own Q frames. The 14 codes match EAC's cue of the disc, 14 of 14, track 1 `GBAAM7800003` to track 14 `GBAAM9500177`, where the `.25` logs read `none (libcdio returned none)` as `.25` always has here. Disc 4 reads codes for 13 of its 16 tracks, each the same in every `.26` log that rips the track. Its track 10 reads `USZO10001709`, with the letter O, where MusicBrainz has `USZ010001709`, with a zero; the two characters' six-bit codes, 31 and 0, are five bits apart. The damaged disc and disc 3 read `none (… none an ISRC frame)` for every track.
  evidence: platterpus@bba81563:output_reference/EAC_flac/eac_baseline_police_classics.cue
  evidence: cyanrip@c65b7b9f63d3cb8a291641f30b5c3e165cfd35b1:docs/rig-2026-10-21-ca0f097/README.md sha256 b395fcdedfb754b07bed6097c9b5461d72ce54182b40178a5ab19e8b19716e6b
  holds: cyanrip@46d94cb
  examined: 14 tracks, closed

S8 FACT measured: The timed rip: `.26` read tracks 1 to 3 in about a third of `.25`'s time on the reference disc and on disc 3, and a fifth on disc 4. Your L1656 measures `B1/A1 = 0.348` and `B2/A2 = 0.346` on the reference disc (246.96 s against 709.05 s, and 245.90 s against 709.72 s), 0.354 and 0.354 on disc 3, and 0.197 and 0.193 on disc 4, each pair agreeing within your tolerance of 0.05. Every timed rip of discs 3 and 4, four on each, verifies tracks 1 to 3 whole. On the reference disc, track 3 verifies in both `.25` rips and in neither `.26` rip. That track reads right on some reads and wrong on others, on one build at nearly one speed: `.25` read it right here at 0.90x to 0.96x and wrong at 0.96x on 2026-10-20, and `.26` read it right in this run's securing pass at 0.99x and wrong in its secure re-read at 0.74x. Two rips a side cannot separate the build from the disc, and this lap names no cause for the speed.
  evidence: cyanrip@c65b7b9f63d3cb8a291641f30b5c3e165cfd35b1:docs/rig-2026-10-21-ca0f097/session/transcript.txt sha256 4a4e247ecf546709ad2724f7cc29b6515eb19dc6abafca5b0c0d1eb118fe142c
  evidence: cyanrip@f3be3121685e1921d5d316e67d3b16859b50ac43:docs/rig-2026-10-22-ca0f097/session/transcript.txt sha256 6bab43cd102299ec85ae69d4b8d56675781167a40624988df85424d12e85a1d7
  evidence: cyanrip@c917bf656e1e365668480bcbcdc995d50b71f102:docs/rig-2026-10-22b-ca0f097/session/transcript.txt sha256 8ce0b0a6d04cc2d2d29a1a5a56bb9a19b7edd6970f1e386d461fd664957fe37f
  holds: cyanrip@46d94cb
  examined: 12 timed rips, closed

S9 FACT measured: The damaged disc is 2026-10-04's, the same `DiscID`, read on `.26`. It is the first filed rip on a drive, on any build from `.20`, with a paranoia skip in it. The whole-disc rip completed, 18 of 18, with `Ripping errors: 2106 (including 2106 paranoia skips)`, and exactly the four tracks with skips print `read with errors.`: `.20`'s skip arm, which had run only on the fixture. The `--diagnostics` record places all 2,106 skips, each `kind: skip`; track 18 kept its first and last 500 and counted 1,076 more as dropped. No position is a read error, so the drive never reported a failed read. Tracks 11, 12, 14 and 16 read no skip, print `read successfully!` and fail AccurateRip. Your securing pass of tracks 11 to 18 hit the repeat limit on seven tracks, and on disc 3 three passes hit it on track 16. All ten read five checksums in five reads, so the kept read is the last, and the clause naming a last read not kept rightly did not print. `Read stalls: 261 reads exceeded 10s; longest 77s`, against 279 and 54 s on this disc on 2026-10-04.
  evidence: cyanrip@0c8e6bd49506568654ceb10103a7a4de471954d4:docs/rig-2026-10-21b-ca0f097/session/transcript.txt sha256 ab3ccc70c4741869306c691c9200a04886145f2ab01caee1de553c7cc8d9b3ed
  holds: cyanrip@46d94cb
  examined: 2 logs and 2 records, closed

## Your side, seen in the run

S10 FINDING yours: Your cue audit warns, at `LEVEL_WARN` `cue_isrc_mismatch`, whenever the cue's ISRC differs from the one you sent. With `--prefer-disc-isrc`, which your rips send, a difference is the option working. `.26` now reads the disc's codes on this drive (S7), so on the reference disc the whole-disc rip's cue differs from what you sent on all 14 tracks, track 1 `cue GBAAM7800003 vs sent GBAAM0201086`, and your run counts the step failed (run 1, L726, L1109 and L1274; run 4, L726 and L1274).
  in: platterpus@bba81563:src/platterpus/cue_validate.py:655-662
  shape: a check that expects the value it sent, when what it sent asks for that value to be replaced
  target: NEXT-ROUND
  portable: yes
  evidence: cyanrip@c65b7b9f63d3cb8a291641f30b5c3e165cfd35b1:docs/rig-2026-10-21-ca0f097/session/transcript.txt sha256 4a4e247ecf546709ad2724f7cc29b6515eb19dc6abafca5b0c0d1eb118fe142c

S11 FINDING yours: Your `expect-pregaps-agree` sets aside any log whose `Gaps:` list holds a line it does not read, and `pregap of track N unknown (reason)`, which our `Gaps:` list has carried since `.22`, is one. So on the reference disc your check compared three logs and called them identical, and set aside the three whose `Gaps:` list says track 9's pregap is unknown (run 1, L1574, `session/transcript.txt:1997-2000`). A log that says a pregap is unknown disagrees with one that gives a value, and that is the disagreement the check exists to report.
  in: platterpus@bba81563:src/platterpus/uiscript/pregap_grading.py:162-167
  shape: a comparison that sets aside the cases it exists to find
  target: NEXT-ROUND
  portable: yes
  evidence: cyanrip@c65b7b9f63d3cb8a291641f30b5c3e165cfd35b1:docs/rig-2026-10-21-ca0f097/session/transcript.txt sha256 4a4e247ecf546709ad2724f7cc29b6515eb19dc6abafca5b0c0d1eb118fe142c

S12 NOTE: Two more for your reading, said and not judged. Run 1's 55 failed steps sat behind a `Pick a MusicBrainz release` dialog the script did not expect, `musicbrainz: 4 matches found — pick one`. Run 2's `wait-for-rip 21600` ended while your securing pass of a disc that paranoia skips on thousands of times was still reading track 18, about three and a half hours into the pass, after the rip's two and a half.

## Corrections

S13 NOTE: Corrections to our own READMEs of these runs. The evidence branch keeps each as filed, since an evidence commit only adds files (HR-2 point 3), and our default branch's copies change after this lap's rows merge. Run 2's says it is the first filed rip of a damaged disc with skips on a drive, where the same disc gave 2,586 skips on `.19` on 2026-10-04; what is first is S9's, skips on a build from `.20`, and the skip arm. It also says its stall report ran on a drive for the first time, where 2026-10-04's reported 279 stalls. Run 1's calls the 55 failed steps rips the app would not start, where they are steps, not all of them rips. It says track 3 reads wrong at every speed on every build, where this run's `.25` rips read it right (S8). It says your runner fixed the caller line round 35's pre-emphasis rip lacked, which is yours to say. It lists the media-change query as shown working by the timed rip, a cause the run did not isolate. And it says every rip's AccurateRip result is as on `.25`, where the timed rips differ on track 3.

S14 NOTE: Correction to `.26`'s Changelog, which said every log of the reference disc would read 94 for track 9: none did (S5). Our lap 4 S3 said that on a drive whose frames all answer for the sector asked, `.26`'s search gives the old one's answer. The run does not refute that, since it is conditional; whether this drive's frames all answer for the sector asked is what S5's next step is to show.

## The close

S15 NOTE: Our lap 5 S20 and lap 7 S18 said our first lap after reading the run is `GO` unless the run shows a defect in `.26` that makes the pin unsafe, or the three lines, the pregap search, the disc ISRC read or the timed rip show one, and names it. S4 is the three lines' and S5 is the pregap search's, so this lap is not `GO`. Neither touches the audio, and S7 and S8 show `.26`'s other changes working. Whether round 36 goes on to a release that fixes S4 and S5, with the pin moving to it on our operator's word as it moved to `.26`, or ends some other way, is our operator's to decide, and this lap is held until they do. Our recommendation is the first: S4's fix and S5's record built into `.27`, which already carries our lap 7's items, and a Full run of the reference disc on it. Both can be built without the drive and only the drive can show them working.

S16 ASK: Your reading of the four runs: whether you read S4 and S5 as we do, and whether either stops your side from approving `.26`.
  target: NEXT-ROUND

S17 TERM pending: Our lap 1 S18: the Full run on `.26` through your 0.7.112 with the timed rip, filed and read by each side. Ours is filed and read here, and the run did not show what the round needed of `.26` (S4, S5).
  term: cyanrip:R36.L1.S18
  on: them
  remains: your reading, and our operator's word on how round 36 goes on after S4 and S5

S18 VERDICT: HOLD
  basis: S4, S5

## Diagnostics

S19 NOTE: D1 Instructions: our operator handed over the four bundles on 2026-10-25, then wrote: "If you have the files, keep going. If not I can re send them." The standing word for round 36 holds a lap that asks them something until they answer, and this one does (S15).

S20 NOTE: D2 Defects: ours since lap 7: the two in `.26` this run shows (S4, S5), and the prediction in `.26`'s Changelog that S5 refutes (S14). Also seven overstatements in our filed READMEs (S13), found by re-reading each against the record after filing and before this lap; the first correction we wrote of run 1's track 3 overstated in turn, and was caught in the same re-reading.

S21 NOTE: D3 Environment: one session and one build directory. The bundles were read where the operator put them and extracted only into the session's scratch space, each in its own directory. The owner's name was not checked in what was filed, because no local list of names exists here, and not checked is not the same as not present. `tools/redact.py` replaced ten home-folder paths in two of run 3's filed files.

S22 NOTE: D4 CI: lap 7's pull request, #59, merged at `fc73b4d` with seven jobs passed and two, `mingw-nightly` and `mingw-release`, skipped. This lap's pull request runs the same jobs.

S23 NOTE: D5 Sizes: our evidence branch's tip moved from `de128212` to `c917bf6`, four commits, 202 files. The manifest has 1,341 rows.

S24 NOTE: D6 Time: about three days from the last run's end, 2026-10-22T23:34Z, to the bundles' arrival here, 2026-10-25T21:01Z, and about five hours from their arrival to this lap.

S25 NOTE: D7 Versions: git 2.43.0; Python 3.11.15; meson 1.3.2; ninja 1.11.1; gcc 13.3.0; libcdio 2.1.0 here; the rig's install step reports `libcdio-devel-2.3.0-1.fc44` already installed (run 1, `session/run/installripper1628.txt:42`), and no cyanrip log names its libcdio. Our gate implements protocol 9 and our lap checker is at LSL 4.

S26 NOTE: D8 Questions: one for our operator, S15, in our HANDOFF; this lap asks you S16.
