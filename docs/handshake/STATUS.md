# cyanrip standing status — what the consumer can assume between rounds

STATUS-NEWEST-LAP: round-36-lap-01.md
STATUS-NEWEST-LAP-STATE: held

STATUS-ROUND: 36, OPEN, opened by our lap 1, published held for our operator's release word, on +platterpus.25 at 5f1d036 with your 0.7.110, the newest released pair; it reviews +platterpus.26, which carries upstream's 7dbe56a, Accurate stream:, Recordable: and a pregap the TOC does not signal searched twice (lap 1 S3 to S6), and closes on the Full run on +platterpus.26 through your first release that reads the three new lines, with a timed rip of +platterpus.25 against +platterpus.26 in it (lap 1 S15); round 35 closed, 2026-10-20, on our lap 17 and your lap 18, both GO, approving +platterpus.25 at 5f1d036 with your 0.7.110, on the Full run of that pair on 2026-10-20, filed in both trees from one bundle, ours at de128212 and yours at 37482669, and read GO by both; your FORK_PIN rolls to 5f1d036 on this close (your lap 18 S15)
STATUS-LAPS: newest sent none (ours), none (theirs); next 1 (ours) carrying round 36's opening, sent when our operator releases it; held 1 carrying +platterpus.26's three wordings for your reader (S4 to S6), the timed rip of +platterpus.25 against +platterpus.26 (S12) and the close (S15); your lap 2 follows it, and only you write it
STATUS-RELEASED: +platterpus.25 at 5f1d036, 2026-10-19
STATUS-RELEASE-NEXT: +platterpus.26, once your reader takes its three new lines, which round 36's first lap proposes, carrying upstream's 7dbe56a, Accurate stream:, Recordable: and a pregap the TOC does not signal searched twice; +platterpus.25 is on the beta channel, approved by round 35 with your 0.7.110, and the stable channel stays +platterpus.23 at 891c79e until a release of ours moves it; pins 5f1d036, reviews +platterpus.26
STATUS-RUN-NEXT: +platterpus.26 with your-next-release; waiting on both releases, which round 36 names, with a timed rip of +platterpus.25 against +platterpus.26 in the run, on the owner's word of 2026-10-20; round 35's Full run, +platterpus.25 with your 0.7.110 on 2026-10-20, is filed on our evidence branch at de128212 (docs/rig-2026-10-20-5f1d036/), and our reading is that folder's README
STATUS-OPEN: repeat-limit-last-read us fixing at 200530e, priority 1: landed at ab0f49b with the wording your lap 2 S14 accepted, released in +platterpus.22, and open until a drive prints it: round 32's Full run on 2026-10-13 and round 34's on 2026-10-16 each hit the repeat limit three times, all on track 3, in the secure re-read and in both securing passes, each with five checksums in five reads, so the newest read was kept, which is the last, and the clause rightly did not print; when the read kept at the repeat limit is not the last, the Done; line names the last read's checksum; round 35's Full run, +platterpus.25 with your 0.7.110 on 2026-10-20 (docs/rig-2026-10-20-5f1d036/), hit the limit nowhere, so the clause had no cause to print
STATUS-OPEN: gaps-undetermined-pregap us fixing at 200530e, priority 1: landed at 4a0fc55 with the wording your lap 2 S15 accepted, released in +platterpus.22, and open until a drive prints it: no pregap search failed in round 32's Full run on 2026-10-13 or in round 34's on 2026-10-16, so the line had no cause to print; a pregap whose search failed is a pregap of track N unknown (reason) line in the Gaps: list, and None signalled prints only when no line did; round 35's Full run, +platterpus.25 with your 0.7.110 on 2026-10-20 (docs/rig-2026-10-20-5f1d036/), failed no pregap search either
STATUS-OPEN: j-record-fields us fixing at 51445c1, priority 2: -j fields for pre-emphasis, the disc's own ISRC beside the one written, CD-TEXT and the -f result, asked by your round 31 lap 3 S5, S8, S9 and S12, proposed in our round 32 lap 1 S10, and accepted in your lap 2 S7 with S8's amendment, cdtext's keys listed in P8b with their types; landed at 51445c1, released in +platterpus.23 at 891c79e, on both channels from 2026-10-16, and run on a drive in round 34's run on 2026-10-16, where all thirteen records carry them: deemphasis_applied true under -E and false under -W, isrc_disc null with libcdio returned none for each track read and not read for each other, cdtext none reported by libcdio; offset_search did not run, since the run's -f step asks for no record
STATUS-OPEN: disc-isrc-line us fixing at dd60143, priority 2: the ISRC read from the disc on a line of its own in each audio track block, Disc ISRC:, and --prefer-disc-isrc to make it win over -t track by track, your TASKS R20, which our operator chose on 2026-10-16; landed at dd60143, released in +platterpus.24 at 93afa15 on beta from 2026-10-16, and in +platterpus.25 with the ISO 3901 check, and proposed in our round 35 lap 1 S4 and S5, the wording open until you answer S13; a drive's read is the MMC path, which only a run shows: round 35's Full run, +platterpus.25 with your 0.7.110 on 2026-10-20 (docs/rig-2026-10-20-5f1d036/), read it, and every track of the reference disc printed Disc ISRC: none (libcdio returned none), each record's isrc_disc null with that reason; a disc whose sub-channel carries ISRCs has not run
STATUS-OPEN: track1-pregap-base us fixing at a64d58d, priority 3: track 1's Pregap length: prints 150 frames for an ordinary disc's lead-in and for two seconds before track 1 alike, told apart only by Pregap source:; counting from LBA 0, proposed in our round 32 lap 1 S13, accepted in your lap 2 S10 with no release of yours first (S11); landed at a64d58d, released in +platterpus.23 at 891c79e, on both channels from 2026-10-16; round 34's run reads 150 from the lead-in, and the reference disc's track 1 starts at LSN 0, so it cannot tell the two counts apart
STATUS-OPEN: disc-isrc-check us fixing at 72a7a8b, priority 2: a disc ISRC that is not an ISO 3901 code is not used, and its Disc ISRC: line says so, asked in your lap 2 S7 for the release after +platterpus.24; our lap 4 proposed your report's own pattern as the rule (S4) and the wording, in both modes (S5); landed at 72a7a8b as proposed, on our operator's word of 2026-10-16, before your answer (our lap 5 S2), released in +platterpus.25 at 5f1d036 on beta from 2026-10-19, after your 0.7.109 at fe557e80, which parses the new shape (our lap 5 S6); open until a drive shows it; round 35's Full run, +platterpus.25 with your 0.7.110 on 2026-10-20 (docs/rig-2026-10-20-5f1d036/), had no disc that carries ISRCs, so it has not
STATUS-OPEN: overread-bounded us fixing at bfe71ec, priority 1: under -O a frame outside the disc was read through paranoia and retried to the retry limit with no timeout of ours, and on a disc image at -P 0 the first frame past the disc was never returned; now read once, a refused one written as silence, and a track that read any says Beyond disc: N of M frames refused (written as silence); landed at bfe71ec, released in +platterpus.24 at 93afa15 on beta from 2026-10-16, and open until a drive shows what it does with a read past its lead-out, which round 35's run on +platterpus.25 is to show; it did not run there: your script sets force_overread off and passes no -O, so no log printed Beyond disc:
STATUS-OPEN: accurate-stream-declared us fixing at a52ea2b, priority 5: a header line saying what the drive's capabilities page declares about accurate stream, proposed in our round 32 lap 1 S19; landed at a52ea2b for +platterpus.26 in that wording, and proposed again in round 36's first lap for your reader; readable only on a drive
STATUS-OPEN: subchannel-pregap-varies us fixing at 81805de, priority 5: track 9's sub-channel pregap reads 94 or 95 frames between rips in twelve filed sessions and the log states one value, and track 4's 158-frame pregap reads 0 in 6 filed logs of the reference disc, once on .22 on 2026-10-13 and twice on .23 on 2026-10-16, where each search returned zero rather than failing; a line giving both counts when two searches disagree proposed in our round 32 lap 1 S19, and which frame is right still needs the drive; in round 35's Full run, +platterpus.25 with your 0.7.110 on 2026-10-20 (docs/rig-2026-10-20-5f1d036/), track 9 read 95 in 2 of its 12 logs and 94 in 10, and track 4 read 158 in all 12; landed at 81805de for +platterpus.26: each such pregap is searched twice, and when the two disagree Pregap source: gives both counts, the wording proposed in round 36's first lap
STATUS-OPEN: error-positions us fixing at 58f7779, priority 8: each track's positions of read errors and skips in the --diagnostics record, your F5's second addition, as our round 35 lap 7 S18 shaped it and your lap 8 S8 accepted it with the first 500 and the last 500 kept; landed at 58f7779, released in +platterpus.25 at 5f1d036 on beta from 2026-10-19, error_positions with error_positions_dropped, one entry per report of paranoia's callback over every read of the track (our lap 9 S7); a -Z re-read mismatch has no position, since -Z compares whole-track checksums; on a drive in round 35's Full run, +platterpus.25 with your 0.7.110 on 2026-10-20 (docs/rig-2026-10-20-5f1d036/), every record carries it, empty, since paranoia reported no read error or skip even on reads AccurateRip shows wrong
STATUS-OPEN: exit-classes us fixing at 292858d, priority 8: 64 for an argument refused or a flag this build lacks, 74 for the disc or drive, 128 + N for a run signal N stopped after its footer said so, and 1 for every other failure, your F8, named by your lap 8 S9; landed at 292858d, released in +platterpus.25 at 5f1d036 on beta from 2026-10-19, a P4 change, with --verify-log's 0 to 5 unmoved and no sixth (our lap 9 S10); the four choices of class our lap 9 S12 asked about, your lap 11 S7 accepted as built; on a drive in round 35's Full run, +platterpus.25 with your 0.7.110 on 2026-10-20 (docs/rig-2026-10-20-5f1d036/), the cancel step's record has exit_code 143 and the C1 refusal exited 64, which your script still expects as 1 (platterpus@e4b0115:src/platterpus/rig_scripts/fullacceptance.txt:1408), the run's one failed step
STATUS-OPEN: unsent-flag-rows them fixing at round 36, priority 8: docs/seam-commands.md §1b, landed here in round 35, rows each flag of ours your rip path does not send; your lap 8 S4's cells landed as given at 061e718, eighteen NO: <reason>, and -X, -C and -B left ? as your S5 says are yours; and --encoder-option's row, added at ac04e1d, has your lap 11 S5's cell, landed as given
STATUS-OPEN: recordable-medium-line us fixing at 0a72e18, priority 9: a tri-state line saying whether the drive reports the disc as recordable, from your F9; landed at 0a72e18 for +platterpus.26 as Recordable:, from the drive's current profile, its wording proposed in round 36's first lap; readable only on a drive
STATUS-OPEN: all-pass-paranoia-counters us fixing at 58f7779, priority 9: a track's paranoia counters summed over every read, beside the last read's, which the Scope: line qualifies, from your F9, the record only, accepted by your lap 8 S10; landed at 58f7779, released in +platterpus.25 at 5f1d036 on beta from 2026-10-19, as paranoia_all_reads, every one of the log's sixteen counter names a key (our lap 9 S8); on a drive in round 35's Full run, +platterpus.25 with your 0.7.110 on 2026-10-20 (docs/rig-2026-10-20-5f1d036/), at least the log's last-read counters for every track the secure re-read read more than once, and equal to them on the rip that read each track once
STATUS-OPEN: encoder-options-flag us fixing at ac04e1d, priority 9: --encoder-option key=value, long-only, repeatable, to every output's encoder, refused in the encoder's own words, from your F9, accepted by your lap 8 S11; landed at ac04e1d, released in +platterpus.25 at 5f1d036 on beta from 2026-10-19, each key tried before anything opens (our lap 9 S9)
STATUS-OPEN: hardware-unverified us cannot, because each needs a disc or a drive this environment lacks: C2, which the rig's drive reports unsupported; CD-TEXT from a physical disc; -W on a pre-emphasised disc; a paranoia skip on a drive; -f on a second drive, and a -f search that finds nothing on a drive; and -P 0's sector-by-sector salvage on a drive; asked of your rig in our round 32 lap 1 S21
STATUS-OPEN: superseded-read-marker us fixing at round 36, priority 7: a superseded track's read marked as such, with the time of that read (round 24's item, with round 8 J14's read time); your round 32 lap 2 S21 kept it and set the order: we propose the wording, your reader takes it, then we print it; this status said we were still asking whether to keep it until our round 35 lap 10, and the proposal is ours and not yet made
STATUS-OPEN: files-listed-from-request us fixing at round 36, priority 7: File(s): computed from the request rather than from what was found; your round 32 lap 2 S21 kept it, in the same order as the superseded-read marker, with your reader taking both forms before ours changes, since it moves a P2 block you parse; this status said we were still asking whether to keep it until our round 35 lap 10, and the proposal is ours and not yet made
STATUS-OPEN: upstream-reports-filed us cannot, because what follows is upstream's maintainer's: our operator filed reports 1 to 23 on 2026-10-16 as one issue, https://github.com/cyanreg/cyanrip/issues/167, in the order of importance docs/upstream/issues-to-file.md suggests, and reports 24 and 25, drafted on 2026-10-19 and rendered there, go to that issue as a comment of our operator's, their word of 2026-10-19; a reply asking for a pull request or for an item as an issue of its own goes to our operator, who files it
STATUS-OPEN: suite-timeouts-at-default us cannot, because neither settling run reproduces a timeout (the suite serially, and each test under the two heaviest), so no mechanism is known to fix; each occurrence is recorded

**The block above is the proposal's D6, and it is checked, not trusted**
(`sc_status_block_is_current()`): the round and its state against the release
gate's own loader; the newest laps of each side, the next lap and our held lap
against the same loader; the next release against `release-manifest.json`, one
past its newest release, with the pin it would stand beside being one a closed
round agreed, since v8 E8 makes it the consumer's approved pin and not our
stable commit, and the release it reviews being published or the next; the
run's provider build against a published release or the next one;
and every `STATUS-OPEN` against the shape D6 gives it, each id once. It is
rewritten in the same commit as any change to what it states. Platterpus keeps
the same block in their standing status, checked by their own code, so the
convention has two implementations.

**Those two lines are declarations, not wire headers.** They carry a `STATUS-`
prefix precisely so that no conforming enumerator counts this file as a lap —
the rule in the paragraph below is unchanged. They exist because on 2026-09-16
this document said round 20 lap 1 was *"published, NOT yet released"* and
*"waiting on the operator's word"* for part of a day **after** the operator had
released it at `6c86689`, and every check over this file passed, because none of
them looked at a lap. `sc_status_is_current()` now resolves the newest lap with
the release gate's own loader and its own `held` property, and compares these
two cells against it.

**Not a round, not a lap, and it must not be counted as one.** It carries no
`HANDSHAKE-*` wire headers for that reason, and `tests/handshake_wire.py` never
sees it because it is not named `round-NN-lap-LL.md`.

The convention is Platterpus's, adopted verbatim: they sent us one on 2026-08-21
for v0.6.21, explicitly outside the round mechanism, and it was the right shape.
Rounds are the *formal* channel and they cost something — S-13 fixes a round's
close conditions at lap 1, and an open round holds the consumer's approved pin
(from v8 it no longer blocks a release). Between
rounds each side still needs somewhere to say where it is.

**Rewritten in place, never appended to.** A stale standing status is worse than
none. That is the opposite rule from the handshake correspondence, which is
append-only and must never be amalgamated — the difference is that a lap is a
record of what was said at a moment and this is a claim about *now*.

---

## Now — rewritten 2026-10-16: round 34 closed, `.23` on stable; round 35's lap 1 held for `.24`

**This section is the whole of what this file claims.** Everything below it is
either guidance on reading the manifest or the rig procedure the suite
checks, and neither is a dated state. **Which build is released, on which
channel, is in `release-manifest.json` and nowhere else**, and what each release
changed is in `Changelog.md`.

### Rounds

- **Round 31 is closed**, 2026-10-11, five laps, on our lap 4 and Platterpus's
  lap 5, both `GO`, by v6 §5b step 3 on both gates. It approves `.21` at
  `ca3f3ea` with their 0.6.66, and their `FORK_PIN` is `ca3f3ea`
  (`platterpus@2f7855be:src/platterpus/deps/fork_source.py:252`).
- **Round 32's lap 1 is ours, sent** on 2026-10-12 on the operator's word,
  *"Release with all open tasks as well"* (`round-32-lap-01.md`). It names
  `.22` at `200530e` with their 0.7.103 at `2f7855be`, presents our open list
  in priority and, in S9 to S22, what needs them, and answers their F1 to F9
  in S23 to S31.
- **Their lap 2 is sent** (`inbound/round-32-lap-02.md`, released at
  `platterpus@c4b624cf`). It moves the run to their 0.7.104, since 0.7.103's
  acceptance script accepts `.21` alone (S2, S3), accepts our `-j` fields with
  `cdtext`'s keys to be listed in P8b (S7, S8), accepts track 1's pregap from
  LBA 0 with no release of theirs first (S10, S11), and takes our reading of the
  version fields (S12).
- **Our lap 3 is sent** on 2026-10-12 on the operator's word
  (`round-32-lap-03.md`). It takes S3 and S8, reports the commits that land
  S10 and S13, asks whether an EAC log shows the additive half of track 1's
  convention, holds `.23` until the run on `.22` with 0.7.104 is filed (S16),
  and pre-commits our closing lap to `GO` unless that run shows a defect of
  ours.
- **Their lap 4 is sent**, released on 2026-10-12 at `platterpus@09b1cd97`
  and on their `main` at `e27cee5b` (`inbound/round-32-lap-04.md`). It is
  their HR-1 lap: the rewrite done, the commit map committed, our side of HR-1
  verified, and 0.7.104 to follow our HR-1 lap. Our lap checker reads it well
  formed through their map; our gate refuses it as a file under C29, because
  it declares protocol 7 after our lap 3 declared 8.
- **Our lap 5 is sent**, released on the operator's word of 2026-10-13
  (`round-32-lap-05.md`): HR-1.7 (4) from our side, HR-1 in our ledger, their
  S9 fixed at `f5ffbb4`, a blocking ask to declare 8, and the retired letters
  and the upstream sync announced for our next release.
- **Their lap 6 is sent**, released on 2026-10-13 at `platterpus@5fc122e8`
  and on their `main` at `93cc0ab4` (`inbound/round-32-lap-06.md`). It
  declares 8, sends `--diagnostics` in place of `-j`, lands our
  `seam-commands.md`, and finds two things in ours: our lap 5's
  `HANDSHAKE-NEXT-LAP` trips C46, and our gate attached a C29 refusal to every
  lap of its round, so round 32 could never close here. Our checker reads it
  well formed.
- **Our lap 7 is sent**, released on the operator's word of 2026-10-13
  (`round-32-lap-07.md`): HR-1.7 (6) from our side, C29 and C46 refusing the
  file and not the round at `9fca98a`, as their S8 asks, and a suite check
  that would have stopped our lap 5.
- **HR-1.7 (6) holds**: Platterpus filed our lap 7 byte for byte, and their
  `--check` and lap checker pass it (`platterpus@7d6b412f`, a commit message,
  not a lap). They released 0.7.104 at `platterpus@3577be65`.
- **Round 32's Full run is made and filed**, `.22` with 0.7.104, 2026-10-13
  (`docs/rig-2026-10-13-200530e/`): 424 pass, 0 fail, the one unreachable
  step E2. Our reading, in that folder's README, finds one defect of ours,
  old and recorded: the sub-channel search read track 4's 158-frame pregap as
  none in the secure re-read (`subchannel-pregap-varies`). Our lap 7 S14 said
  our next lap is `GO` unless the run shows a defect of ours, so that lap says
  whether this one holds it.
- **Their lap 8 is sent**, released on 2026-10-13 at `platterpus@ecdbceab`
  and on their `main` at `be180d4c` (`inbound/round-32-lap-08.md`): their
  reading of the run, filed in their tree from the same bundle, and `GO`.
- **Our lap 9 is sent**, released on the operator's word of 2026-10-13
  (`round-32-lap-09.md`): our reading and `GO`. It says the track-4 defect
  does not hold the round, because it is older than `.22`, was already
  recorded, needs a drive to diagnose, and moves no audio byte.
- **Round 32 is closed**, 2026-10-14, on our lap 9 and their lap 8, both
  `GO`: ours with their lap 8's verdict, theirs by v6 §5b step 3 on our lap 9
  (their lap 8 S17). It approves `.22` at `200530e` with their 0.7.104. Their
  lap 8 S17 moves their `FORK_PIN` from `ca3f3ea` to `200530e`. Two items
  leave the open list with it: the one-frame tally's label, which printed on a
  drive in the run, and the version fields, which both closing laps fill with
  the builds the round reviewed.
- **Round 33 is closed**, 2026-10-15, seven laps, on our lap 7 and their lap
  6, both `GO`, 27 days before the close-by. It approves `.22` at `200530e`
  with their 0.7.105, the pair R8 point 3 gave it, on HR-2 point 12's proof:
  both moves verified by the other side's checker, ours `0f9375ad` and theirs
  `c737fb6b`, and each side's evidence citation passed by the other's. HR-2's
  open item leaves the list with it. Round 34 opens on our lap 1, with `.23`
  and their 0.7.106.
- **`.23` is released on both channels**, at `891c79e`: on beta on
  2026-10-15 and on stable on 2026-10-16, each on the operator's word, the
  second once round 34 approved it. Ledger rows 33 and 34 name the same
  commit, so nothing was rebuilt.
- **Round 34's lap 1 is ours, sent** on 2026-10-15 on the operator's word,
  *"If you are ready release it"* (`round-34-lap-01.md`). On the operator's
  rule of 2026-10-15, *"Give what you know, wait for the test"*, it opens the
  round before Platterpus's next release instead of waiting for it. It carries
  what is known now: their message inventory against `.23`'s P5 (S5), and the
  build under review their section A needs before any Full run can pass it (S3,
  S4); and ours, `Settled facts` timing out on CI's macOS runner (S8) and the
  checker's cut hashes (S9). It names the run by condition, their first release
  naming `891c79e` as its build under review (S14). Read again at release, their
  `main` at `dd200af7` already carries both of theirs in 0.7.106's release
  commit, not yet tagged (S7).
- **Round 34's Full run is filed and read**, `.23` with their 0.7.106 on
  2026-10-16: 426 pass, 0 fail, the one unreachable step E2, every bundle
  member matching their MANIFEST's hash, filed on our evidence branch at
  `79b36c97` (`docs/rig-2026-10-16-891c79e/`, whose README is our reading).
  No defect in what `.23` changed. One old defect of ours shows again, track
  4's pregap read as zero twice (`subchannel-pregap-varies`), and one finding
  is theirs: their runner took `no read exceeded 10s` as the ripper's build
  tag from a refused rip, so one pre-emphasis rip sent no `--consumer`.
- **Their lap 2 is sent**, released on 2026-10-16 at `platterpus@b5d6b06a`
  (`inbound/round-34-lap-02.md`): their reading of the run, filed on their
  evidence branch at `fe13de0c` from the same bundle, finds no defect in `.23`,
  and `GO`. Our checker reads it well formed, after two fixes to our checker
  it found: one for the K1 collision with our held lap 2, one for reading their
  evidence rows on a stale local branch.
- **Round 34's lap 3 is ours, sent** on 2026-10-16 on the operator's word,
  *"release your lap"* (`round-34-lap-03.md`), our held lap 2 renumbered under
  K1. It is our reading of the run and `GO`, as lap 1 S16 pre-committed; it
  answers Platterpus's TASKS R12, accepts X9 as they narrowed it, reports what
  landed (I16 among it), corrects two counts in their lap 2, and carries our
  round summary.
- **Round 34 is closed**, 2026-10-16, three laps, on our lap 3 and their lap
  2, both `GO`, 28 days before the close-by. It approves `.23` at `891c79e`
  with their 0.7.106, on the Full run of that pair, filed in both trees from
  one bundle and read `GO` by both. Their lap 2 S15 moves their approved pin to
  `891c79e` on this close, and their 0.7.107 is the first release of theirs
  to install it by default. `.23` moved to our stable channel the same day.
- **Round 35's lap 1 is ours, sent 2026-10-16** (`round-35-lap-01.md`),
  naming `.24` at `93afa15`. It carries Platterpus's TASKS R20, the route the
  operator chose: each audio track block prints the ISRC read from the disc,
  `Disc ISRC:`, and `--prefer-disc-isrc` makes it win over `-t`, both landed at
  `dd60143` for `.24`. It asks Platterpus to accept or amend the wording (S13),
  and closes on the Full run on `.24` through their first release that parses
  the line and sends the option (S19).
- **Round 35's Full run is filed and read**, `.25` with their 0.7.110 on
  2026-10-20: 434 pass, 1 fail, the one unreachable step E2, every bundle
  member matching their MANIFEST's hash, filed on our evidence branch at
  `de128212` (`docs/rig-2026-10-20-5f1d036/`, whose README is our reading).
  No defect in what `.25` changed. The failed step is theirs: C1's `cyanrip
  -N -l 1` exits 64, the class our lap 9 S12 proposed and their lap 11 S7
  accepted, and their script still expects 1. The bounded `-O` did not run.
- **What we would ask of Platterpus next**, to make a run easier to read, is in
  the handshake README's data register. X6 to X9 landed in theirs on
  2026-10-14 and X10 is met (round 32 lap 8); the asks still open are X1, X2
  and X5, each `proposed`.
- The table of every round is the handshake README's, and the gate is the
  authority over both.

### Runs

| | |
|---|---|
| newest | **`.25` with Platterpus 0.7.110, Full, on the reference disc, 2026-10-20** from 11:36:56Z: 434 pass, 1 fail, the one unreachable step E2; round 35's test, filed on our evidence branch at `de128212` (`docs/rig-2026-10-20-5f1d036/`), whose README is our reading: no defect in what `.25` changed; the one failed step is their script expecting exit 1 from the C1 refusal, which `.25` exits 64 as agreed, and their runner again took a refused rip's `(no read exceeded 10s)` as the build tag |
| next | **`.26` with Platterpus's next release**, whatever the round after 35 asks for |

Every earlier run is a `docs/rig-*` folder with its own README.

### The protocol

`PROTOCOL.md` v9, which is v8 plus HR-2 and HR-2.1 (§17), is byte-identical
in both trees from `platterpus@37826a5f` (`tools/seam-sync-check.py --fetch`,
2026-10-14), and governed round 33. **Both gates implement 9**: ours from
`aae9164`, theirs as their round 33 lap 2 says, and every lap of round 33
from our lap 3 on declares 9.

### Platterpus's side, read and not run

Their newest release is 0.7.110, tag `v0.7.110` at `e4b0115d`, read with
`git ls-remote` on 2026-10-20. Their newest lap is round 35's lap 16, read at
`e4b0115d`, and their standing status is
`docs/handshake/outbound/platterpusstatus.md` in their tree.
Seventeen of their earlier statuses are filed under
`docs/handshake/inbound/status-*.md`, each dated by the date it declares; theirs
are evidence and are never consolidated, and ours is a claim about now and is
rewritten.

### Open items

**The block's `STATUS-OPEN` lines are the list**, each with its priority and
whether it is being fixed or stays open and why; `docs/KNOWN-ISSUES.md` has the
detail. Priorities 8 and 9 are what Platterpus's standing status ranked for us
on 2026-10-12, F5's second addition and F8 and F9.

**Removed on 2026-10-12, because they are done**: the eight fixed in `.20`,
and so in the `.21` round 31 approved, which the block still listed as open:
the album graph fed the kept read alone, the kept read at the repeat limit, the
cache probe's calibration (measured twice since, in agreement with
`cd-paranoia -A` to a power of two), `-P 0`'s sector-by-sector salvage, a track
read with errors over a paranoia skip, extraction speed below 1x, the `-f` and
`-J` footers, and the one-frame entry under the threshold. What each still
lacks on hardware is the `hardware-unverified` line.

### Upstream

Our `master` mirrors `cyanreg/cyanrip` at `b40c1f0`, 0.9.4-rc3, merged into
`platterpus-fork` at `79da685`. That is a reading of 2026-10-12T22:46Z, when
`git ls-remote` last returned it; `tools/upstream-delta.py` is how to check
again. **Twenty-five defects this fork found in upstream's code are
reported; the first twenty-three are filed there, as one issue, [cyanreg/cyanrip#167](https://github.com/cyanreg/cyanrip/issues/167)**, by our operator on 2026-10-16, in the
order of importance `docs/upstream/issues-to-file.md` suggests, each
re-checked against `master` by `tools/check-settled.py`. The link is our
operator's word: this session cannot open upstream's tracker.

## Earlier states of this file are in git history, not here

**This file held about twenty stacked "Rewritten…" sections** — from 2026-09-11
to 2026-09-22, each describing a moment as *now*: round 20 *"IS OPEN"*, round 21
*"IS OPEN"*, laps *"HELD"*, two of them annotated *"(wrong — see above)"*. Its own
rule is *"rewritten in place and never appended to"*, and for eleven days every
rewrite was a prepend. **A reader got twenty contradictory nows**, and on
2026-09-22 two of them still asserted that `.14` had not been cut after it had.

They were removed by the pre-round-24 audit, not lost: `git log -p --
docs/handshake/STATUS.md` has every version, and **the laps are the record** —
this file never was. Consolidation applies to documentation and never to
evidence.

### Round 16's hardware procedure, kept as a record, not today's test

**This is round 16's Run A, which settled that round's three clauses. It is not
the real test any more.** That is Platterpus's Full acceptance run, which
installs the build under review through their app. Run A's preflight accepts
only round 16's two builds (`tools/rig-round16.sh:103-126`) and exits 1 on any
other, so on `.16` it stops before the drive unless `ALLOW_ANY_BUILD=1`. **It
installs nothing and restores nothing**, and neither does any other tool here:
`tools/rig-check.py` only reads the installed build and names the channel it
matches, and `release-manifest.json` names one build per channel with no
rollback field. That is our answer to round 27 lap 3's question.

**Everything it creates lives under `~/cyanrip-rig`, so cleanup is one
`rm -rf`.** Operator's instruction, 2026-09-11, after a session left five
directories and a tarball loose in `$HOME`.

```sh
RIG=~/cyanrip-rig
rm -rf "$RIG/work" && mkdir -p "$RIG"
git clone -q https://github.com/rmccann-hub/cyanrip "$RIG/work" && cd "$RIG/work"
git checkout 5bbb5ae -- tools/rig-round16.sh tools/audio-checksums.py \
                       tools/round16-accept.py docs/rig-2026-08-05/cyanrip.log
OUT="$RIG/runA" DEV=/dev/sr0 OFFSET=667 CRIP="$HOME/.local/bin/cyanrip" \
    sh tools/rig-round16.sh
python3 tools/round16-accept.py --out "$RIG/runA"
```

**Three things in it are there because a previous version was broken**, each
found by running it rather than reading it: it **clones** (the block once began
at `git checkout` and produced `fatal: not a git repository` from a home
directory); it checks out **`docs/rig-2026-08-05/cyanrip.log`** (a fresh clone
lands on `master`, a clean upstream mirror with no `tools/` and no reference
log, and without it the grader exits 2 after all the drive time); and `OUT` is
named up front so no timestamp is transcribed off the screen at the end of a
long night. `sc_runa_block_is_complete` derives the required file list from the
tools' own source, so a new dependency fails the suite until the block names it.

**`CRIP` here is the host wrapper, and that is the one thing to change for a
release test.** `timeout -k` around `~/.local/bin/cyanrip` kills the **distrobox
wrapper** and leaves the containerized cyanrip running — measured on 2026-09-11
from the run's own mtimes, 23m20s between the script giving up and the log being
written, with `plain.json` recording `exit_code: 0`. Every rip completed; the
script was wrong about all five. Drive the real binary directly
(`distrobox enter ripping -- /usr/local/bin/cyanrip`) or accept that every step
will hit its ceiling.

## Releases — read the channel, never the version string

**Every `0.9.4-rcN+platterpus.N` the manifest calls stable IS stable.** The
`-rcN`, `-rc3` now, is upstream's own string, copied verbatim because we may not mint in `cyanreg/cyanrip`'s namespace;
the part that advances is `+platterpus.N`, which SemVer says MUST be ignored for
precedence. **A check that reads the shape of the version will call this a
pre-release, and it will be wrong.** Order by `release_seq`, read the `channel`
column of `release-manifest.json`.

**There is no tag.** Tag pushes are `HTTP 403` from the environment this is built
in, and `git ls-remote --tags origin` returns nothing. No release of this fork has
ever been reachable by tag. The commit SHA and the manifest row are the whole
identifier.

`beta` resolves to the newest row of *any* channel, so opting into pre-releases
can never move a user backwards.

**`+platterpus.8` (`796df32`, seq 18) is superseded and should not be installed.**
It is still in the ledger, because the ledger is append-only and a published build
is a fact, but no channel resolves to it any more.

Build command: `meson setup build -Ddeclare_released=true && ninja -C build`.

`release-manifest.json` is the only mechanism to install from, and the only
place a release is named.

**A release does not wait for a round** (`PROTOCOL.md` v8 §6b). `tools/release-gate.py
--release-gate` names every open round and permits; the suite on the release
commit from a clean checkout is what refuses one, and a round reviews the
released pair afterwards. Until v8 this paragraph said *"No release while any
round is open"*, and it outlived that rule by a release.
