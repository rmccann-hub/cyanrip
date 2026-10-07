# cyanrip standing status — what the consumer can assume between rounds

STATUS-NEWEST-LAP: round-31-lap-01.md
STATUS-NEWEST-LAP-STATE: held

STATUS-ROUND: 31, OPEN, opened by our lap 1 on +platterpus.21 at ca3f3ea, held until the operator releases it; it proposes that either side releases when its own suite is green and a round reviews the released pair (E1 to E9), and closes on that settled with its text in both trees, the Full run on .21 with your 0.6.66, and our two findings from round 30's run fixed
STATUS-LAPS: newest sent none (ours), none (theirs); next 1 (ours) carrying round 31's opening lap, once the operator releases it; held 1 carrying round 31's opening lap
STATUS-RELEASED: +platterpus.21 at ca3f3ea, 2026-10-07
STATUS-RELEASE-NEXT: +platterpus.22, carrying round 31's fixes: the repeat limit's last read, the Gaps: list's undetermined pregap and the one-frame tally's label; pins ca3f3ea, reviews +platterpus.22
STATUS-RUN-NEXT: +platterpus.21 with 0.6.66; waiting on your 0.6.66
STATUS-OPEN: album-graph-first-encoded-pass us fixing at round 30: landed at d7ee6c4 released in +platterpus.20 on beta at 5704062; the -Z spool encodes only the kept read, so the album graph is fed that read alone
STATUS-OPEN: suite-timeouts-at-default us cannot, because neither settling run reproduces a timeout (the suite serially, and each test under the two heaviest), so no mechanism is known to fix; each occurrence is recorded
STATUS-OPEN: repeat-limit-kept-read us fixing at round 30: landed at d7ee6c4 released in +platterpus.20 on beta at 5704062; at the repeat limit the read the most reads agreed on is kept, the newest of them on a tie
STATUS-OPEN: files-listed-from-request us cannot, because moving File(s): changes a P2 block you parse, and no design exists yet
STATUS-OPEN: partially-accurate-tally-label us fixing at round 31: renamed Tracks matched on one frame only: in src/cyanrip_log.c, not yet released, after your 0.6.66b1 reads both wordings (platterpus@fd439881 is its ancestor), as round 20's order asks; it ships in +platterpus.22
STATUS-OPEN: superseded-read-marker both cannot, because the format needs a design both sides agree (round 24's item)
STATUS-OPEN: cache-probe-calibration us fixing at round 30: landed at 394ab17 released in +platterpus.20 on beta at 5704062, and measured once on 2026-10-06: 128 to 255 sectors beside your section P's cd-paranoia -A at 137 (docs/rig-2026-10-06-5704062/); a re-read is a hit under cd-paranoia's 6 ms, and .19's 128 to 255 on 2026-10-05 was the old defect landing on the other side of its threshold, not a measurement
STATUS-OPEN: p0-unreadable-sector-hang us fixing at round 30: landed at c57b596 released in +platterpus.20 on beta at 5704062; at -P 0 a short read is retried sector by sector and a sector that will not read is zero-filled, and its speed on a drive is not measured
STATUS-OPEN: gate-c13a us fixing at round 31: v6 amended the row (PROTOCOL.md C13a), so no amendment is needed, where this line said one was; our gate still reads a later lap of a different verdict as the round's new state, and will refuse it (our round 31 lap 1 S25)
STATUS-OPEN: upstream-reports-unfiled us cannot, because filing on upstream's tracker is the maintainer's act, which the operator said on 2026-10-05 they will do
STATUS-OPEN: read-successfully-over-skips us fixing at round 30: landed at e5a0897 (a paranoia skip) and 4529810 (a -Z read that never agreed) released in +platterpus.20 on beta at 5704062; Ripping errors: counts the skips too, with a suffix saying how many, by the operator's word of 2026-10-05, landed at 0c692ed; a rip whose only errors are skips still exits 0, as our lap 9 S13 asked and your lap 10 S11 accepted
STATUS-OPEN: extraction-speed-below-1x us fixing at round 30: landed at a72b162 released in +platterpus.20 on beta at 5704062; two significant figures below 1x, three decimals at most because your _TRACK_SPEED reads no more
STATUS-OPEN: f-and-j-runs us fixing at round 30: landed at aa1f067 released in +platterpus.20 on beta at 5704062; a -J or -f run's footer says what it was where it said aborted, and a stop ends a -f search; a -f search that finds no offset exits 1 by the operator's word of 2026-10-05 (0645ddb), landed with the seam-commands.md text our lap 9 S16 proposed and their lap 10 S10 accepted; their tree carries the same bytes from platterpus@0769c61e (their lap 12 S6)
STATUS-OPEN: one-frame-under-threshold us fixing at round 30: landed at b1857d6 released in +platterpus.20 on beta at 5704062; a one-frame AccurateRip entry found under the threshold says so where it said (not found), one P2 arm, which your lap 12 S8 accepted
STATUS-OPEN: repeat-limit-last-read us fixing at round 31: found 2026-10-06 reading the closing run, not landed, and left for round 31 by the operator's word of 2026-10-06, round 30 closing on that run; at the repeat limit the loop prints no checksum for its last read, and since the -Z spool (d7ee6c4) keeps the most-agreed read, a kept read that is not the last leaves the last one in no line of the log; the proposed fix names it in the Done; (repeat limit …) line after `agreed`, which both your patterns still match (platterpus@9ecd1147:src/platterpus/parsers/cyanrip_log.py:341-352)
STATUS-OPEN: gaps-undetermined-pregap us fixing at round 31: found 2026-10-06 reading the closing run, not landed, older than .20, and left for round 31 by the operator's word of 2026-10-06, round 30 closing on that run; the Gaps: list skips a pregap whose sub-channel search failed with no line, so a rip of selected tracks reads it as no pregap, and with every search failed the list says None signalled; the proposed fix gives each a line, which changes the first line you render as EAC's Gap handling row (platterpus@9ecd1147:src/platterpus/parsers/cyanrip_log.py:199-204)

**The block above is the proposal's D6, and it is checked, not trusted**
(`sc_status_block_is_current()`): the round and its state against the release
gate's own loader; the newest laps of each side, the next lap and our held lap
against the same loader; the next release against `release-manifest.json`, one
past its newest release, with the pin it would stand beside being the
manifest's stable commit; the run's provider build against the next release;
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
close conditions at lap 1, and an open round blocks both sides' releases. Between
rounds each side still needs somewhere to say where it is.

**Rewritten in place, never appended to.** A stale standing status is worse than
none. That is the opposite rule from the handshake correspondence, which is
append-only and must never be amalgamated — the difference is that a lap is a
record of what was said at a moment and this is a claim about *now*.

---

## Now — rewritten 2026-10-05, after the operator's final Full run of `.19`

**This section is the whole of what this file claims.** Everything below it is
either guidance on reading the manifest or the rig procedure the suite
checks, and neither is a dated state.

### Runs, and what is next

**Which build is released, on which channel, is in `release-manifest.json` and
nowhere else**, and what each release changed is in `Changelog.md`. This file
kept hand-written copies of both, and a test that existed only because copies
rot; both were removed on the operator's word of 2026-10-07.

| | |
|---|---|
| `.18` on a drive | **round 29's Full acceptance on `.18` with Platterpus 0.6.63 ran from 2026-09-28T22:33:56Z to 2026-09-29T03:55Z** (`docs/rig-2026-09-28c-51cc789/`). **Its script's verdict is not a pass**: 320 pass, 3 fail, `counts_as_evidence: true`, no section skipped or blocked, and all three failures are `screenshot` steps that found no window on screen. All ten cyanrip logs verify with `-Y`; nine completed with `Ripping errors: 0`, and the interrupted one printed `.18`'s stop marker and its `Encoder errors:` and `Partial files:` lines. The secure re-read converged on all fourteen tracks. Nothing in it is a defect in `.18`. The disc-level `AccurateRip:` line's `mismatch` and `not found` arms and upstream's MusicBrainz retry are not exercised |
| `.17` on a drive | **the Full acceptance on `.17` with Platterpus 0.6.61 ran on 2026-09-28 from 01:48:08Z to 07:08Z**: its script reported 320 of 320, 0 skipped, `counts_as_evidence: true` (`docs/rig-2026-09-28-e0471f4/`). All eight cyanrip logs verify with `-Y`; seven completed with `Ripping errors: 0` and the interrupted one stopped as section I intends. `.17`'s `Accurip 450` wording printed on the drive for the first time. One wrong read, track 3 in section F with no `-Z`, a checksum never filed before; the secure re-read got track 3 right. **The operator chose on 2026-09-28 that this run closes round 28**, as lap 1 S6 names it, so Platterpus's lap 6 S36 override moving the run to their 0.6.62 falls away. **A second Full run of `.17`, through their 0.6.62, ran the same day from 14:42:38Z to 19:27Z** and is filed as `docs/rig-2026-09-28b-e0471f4/`: 320 of 320, all eight logs verify with `-Y`, and the secure re-read converged on all fourteen tracks. It is a close condition of neither round 28 nor round 29 |
| `.20` on a drive, 2026-10-06 | **the closing run of `.20` with Platterpus 0.6.66b1, Full, on the reference disc** (`docs/rig-2026-10-06-5704062/`): 418 pass, 7 fail, 1 unreachable. All seven failures are their album audit warning that `.20` logs `NOT a released build`, which a beta cut inside the round does by design. All eleven cyanrip logs and both securing-pass logs verify with `-Y`. **First on a drive**: `-f` found `+667` at confidence 14; the cache probe said `128 to 255 sectors` beside `cd-paranoia -A`'s 137; a `-Z` read that never agreed read `with errors.`; `-H -E` and `-H -W` measured different loudness, on the delivered audio. **Two findings of ours**, both open above: the last read at the repeat limit can be in no line, and the `Gaps:` list leaves out a pregap it could not determine |
| `.19` on a drive, 2026-10-05 | **the operator's final Full run of the pair, on the reference disc** (`docs/rig-2026-10-05-174a134/`): 316 pass, 7 fail, all seven `screenshot` steps, as on 2026-09-30b. All ten cyanrip logs verify with `-Y`. AccurateRip 12 of 14 again, tracks 3 and 5; track 3 read eleven times with eleven checksums. Three `-Z` reads hit the repeat limit, and the one in a log prints `read successfully!`, the case `.20` changes. The cache probe said `128 to 255 sectors`, the first bracket in seventeen sessions, because a 304.2 ms calibration put `.19`'s threshold under the ~82 ms backseeks: the defect, not a fix. The cancel showed the rescue's SIGTERM is the first cyanrip receives, which withdraws a finding we had drafted. **No defect in `.19` not already recorded** |
| `.19` on a drive, 2026-10-04 | **three Full runs, none complete** (`docs/rig-2026-10-04-174a134/`). Two stopped at section E on discs MusicBrainz does not know (both disc IDs 404). The third ripped *Roots Music* disc 1 of 4, which the drive reads differently each time from track 11 on: track 18 took **8,161 s**, with **2,586** paranoia skips and reads of up to **54 s**, and a `-Z 2` pass hit the repeat limit on five tracks, five checksums each. That is the first filed rip with a skip, and `.19`'s reworded limit line printing on a drive. Five of six logs verify. The sixth was copied while cyanrip was still writing it. **No defect in `.19`**; two inherited behaviours of ours go to round 31, below |
| next | **Round 30 is closed** on our lap 17 (2026-10-07), `GO` with the ledger our lap 15 left out, beside their lap 16's `GO`; both gates read it closed on lap 17. **`.21` is on stable** at `ca3f3ea`, and **round 31 is opened by our lap 1, held** until the operator releases it. **Next**: their 0.6.66, which installs `.19` and reviews `.21` (`FORK_PIN` `174a134`, round 30's declared pin, and `PIN_UNDER_REVIEW` `ca3f3ea`, read at `platterpus@a0330d09:src/platterpus/deps/fork_source.py:242,757`), and our round 31 lap 1 on `.21` |

**What the 2026-10-04 and 2026-10-05 runs showed on your side, and where each
stands** at `platterpus@bd508bf1`, read and not run:

- **Answered by your commits**: `pick-release` on placeholder rows, and a
  cancelled re-read reported as clean (`12903dc0`); the shutdown grace's floor,
  now 108 s (`12903dc0`); a bundle written around a running ripper
  (`d62f1ca4`); no `-j` record in any bundle (`a7a631b9`); the re-read path's
  docstring (`d6669722`); and a swapped-in re-read's signed log deleted
  (`32985e07`, kept byte for byte).
- ~~**The cancel's rescue sends a second TERM 4.9 s after the first.**~~
  **Withdrawn 2026-10-05**: behind your wrapper the rescue's is the first
  signal cyanrip receives, as the 2026-10-05 run shows and your S31 says. **One
  case remains**, our lap 9 S28: a native install, with no wrapper, where the
  cancel's TERM reaches cyanrip directly.
- **Still open**: your stdout capture drops every track's outcome line (our lap
  9 S29); your ladder cannot step down on a read the drive failed, because
  cyanrip exits 1 then (S27); and your lap 8 S42 drops its README's qualifier on
  which tracks match EAC (S30).

### The rounds

| | |
|---|---|
| **round 31** | **OPEN**, our lap 1 held, on `ca3f3ea` (`.21`). It proposes that either side releases when its own suite is green and a round reviews the released pair (E1 to E9), and closes on that settled with its text in both trees, the Full run on `.21` with their 0.6.66, and our two findings from round 30's run fixed. Close-by 2026-11-04 |
| **round 30** | **CLOSED `GO`/`GO`** 2026-10-07, seventeen laps, on our lap 17 beside their lap 16, on the closing run of `.20` at `5704062` with their 0.6.66b1, and authorising `.21`; their `FORK_PIN` is `174a134`, round 30's declared pin. Opened 2026-09-30 by our lap 1 on **`174a134`** (`.19`), before its run, by the operator's override of R8 point 3, as rounds 26 to 29 were. **Our lap 1 is sent** (sha256 `6db0ed0d…`, 15,546 bytes): it names `.19` for their next release (S6), records why 0.6.64's section A stopped (S22–S24), reports a `.18` log left footerless by closing their script console (S25), and carries `docs/handshake/PROPOSAL-release-cycle.md` (D1–D10). **Their lap 2 is released**, `OPEN`, read at `platterpus@0981c69` and filed byte-exact as `inbound/round-30-lap-02.md` (sha256 `85fdb608…`, 16,439 bytes). It names `174a134` in 0.6.65 (S13), released under their §6b override, and corrects our S23: their `428229c7` already let a release name `174a134` from our manifest (S7). It asks S8, `BLOCKING`, and S5, S20 and S22, and answers D1–D10 after the run (S18). Its digest `8e1dfcd54e77a28c` reproduces, and our checker reads it as well formed with 0 warnings. **The Full run on `.19` ran** 2026-09-30 through 0.6.65 (`docs/rig-2026-09-30b-174a134/`): 316 steps passed and 7 failed, all `screenshot`; all ten cyanrip logs verify, section N's fourteen repeat-loop checksums each equal the track's EAC CRC32, and every tag key is in capitals. **Our lap 3 is sent**, released on the operator's word 2026-09-30, at protocol 6 in LSL 3: it reads the run (S17–S23), restates misalignment 3 and D2 against `0981c69` (S3–S5), files `.19`'s suite record re-run at `174a134` (S7), withdraws our S19 (S10), and gives the signal table with SIGHUP handled for `.20` (S12–S15). Its digest is `7d236872d2bc95d7` over two laps. **Their lap 4 is sent**, filed byte-exact as `inbound/round-30-lap-04.md` (sha256 `5db48a29…`, 25,476 bytes, released at `platterpus@6d286acf`, merged into their `main` at `a1805da8`); its digest `b22d3ddab53b3cbb` over three laps reproduces, and our checker reads it as well formed with 2 warnings. It meets our lap 1 S10 on their side (their S17) and leaves S9 and S11. **Our lap 5 is sent**, released on the operator's word 2026-09-30 (sha256 `8f11cdc3…`, 22,514 bytes): it delivers C2 to C5 as `DID`s (their `BLOCKING` S41), proposes PROTOCOL v7 and seam-rules v7 (`09f39bc`), accepts their D10 amendment, amends their LSL amendment to a declared LSL 4, measures `-U` safe (S42), reports their shutdown fix's 8 s grace shorter than reads of 11 s filed on the rig's drive (S17), names `+platterpus.20` on beta as our closing release, and declares `GO` on the texts as proposed; its digest is `a6d4999d87b6f2e2` over four laps. **Their lap 6 is sent**, `OPEN`, filed byte-exact as `inbound/round-30-lap-06.md` (sha256 `c5669248…`, 18,177 bytes, merged into their `main` at `5ec71f4e`): it amends the proposed v7 texts four times (S19 to S22), one blocking because §6d's template carries no `TERM`; fixes their shutdown grace at 40 s (S7); sends `-U` (S5); and asks whether the `-f` summary line is stable (S14). Its digest `c6ea0cbb40287811` over five laps reproduces. Our checker refuses its S15 under A3 and theirs does not. **Our lap 7 is sent**, released on the operator's word 2026-09-30 (sha256 `108fcb1a…`, 17,371 bytes): it takes S20 and S21, amends S19 and S22, proposes the texts at `2abeb5d`, lands them in its own commit, answers S14 and declares `GO`. **Their lap 8 is sent**, `OPEN`, filed byte-exact as `inbound/round-30-lap-08.md` (sha256 `ef9b1dbb…`, 35,138 bytes, released at `platterpus@61b505e1`, merged into their `main` at `bd508bf1`): it reads the 2026-10-05 run, fixes eight things of theirs, asks how their EAC-layout log should word a track the reads could not verify (S20), and asks both sides for a data register (S36, S37). Its digest `747c80610cb90180` over seven laps reproduces, and our checker reads it as well formed with 2 warnings, both on relayed quotations. **The operator then kept the round open, 2026-10-05**: it ends only when every finding is fixed or explained, both applications ship betas, and an acceptance run of both passes. **The operator's final Full run of `.19` with 0.6.65 ran that night** (`docs/rig-2026-10-05-174a134/`). **Their lap 10 is sent**, `OPEN`, filed byte-exact as `inbound/round-30-lap-10.md` (sha256 `20e17e55…`, 27,675 bytes, released at `platterpus@e43d05d1`, merged into their `main` at `9425a524`): it accepts our lap 9 S13, S16, S39 and S3, withdraws their lap 8 S28 and corrects its S42, fixes our S27 to S29 for 0.6.66, implements protocol 7 in their gate, asks S30 and S32, and finds our lap 9 carries no R6 pre-commit (S14). Its digest `d72da50b46f7ea72` over nine laps reproduces, and our checker reads it as well formed with 0 warnings. **Our lap 9 is sent**, released on the operator's word 2026-10-05: it records the operator's close conditions as an override of R1 and their answers to nine questions, releases our lap 7 S20's pre-committed `GO`, lists ten fixes for `.20` and proposes an eleventh with the shared `seam-commands.md`, answers their lap 8, refutes one premise of its S28, gives our half of the register, and reads the 2026-10-05 run. Its digest is `525abc43c7d759b7` over eight laps. **Close conditions** (our lap 1 S9–S11, accepted in their S17): D1–D10 settled with the text landed in both trees; the Full run on `.19` through 0.6.65, read by both; and the closing releases named. Close-by 2026-10-28 |
| **round 29** | **CLOSED `GO`/`GO`** 2026-09-29, **four laps**, 27 days before the close-by, on Platterpus's lap 4 by v6 §5b step 3, with no lap 5 of ours. Opened 2026-09-28 by our lap 1 on **`51cc789`** (`.18`) before the real test, by the operator's override of R8 point 3, as rounds 26 to 28 were. Close conditions: the Full acceptance on `.18` through their 0.6.63, with the bundle in both trees (ours `docs/rig-2026-09-28c-51cc789/`, theirs `platterpus@6873d45b`); both readings (our lap 3, their lap 4); the tag change (`bf50705`); and R8's releases, named in the closing laps: our `.19` and their 0.6.64 with `FORK_PIN` `51cc789`. **Their lap 4** (`GO`, sha256 `67c4167d…`, 18,972 bytes, released at `platterpus@58ad83db`, filed byte-exact) corrects their lap 2 S4, accepts our S24 and S35, adopts the shared `seam-commands.md` with their argv check (`68abbd95`), and reads the run. Both checkers read it as well formed with 2 warnings, each re-running three results and matching. Digest `4b2cbed42b7971f1` over three laps, as our lap 3 predicted. Three NEXT-ROUND notes for the shared LSL spec (S31–S33) go to round 30, and one finding is portable to our checker (S9: git's abbreviation length in a re-run) |
| **round 28** | **CLOSED `GO`/`GO`** 2026-09-28, **nine laps**, 26 days before the close-by, on Platterpus's lap 9 by v6 §5b step 3, with no lap 10 of ours. Opened 2026-09-26 by our lap 1 on **`e0471f4`** (`.17`) before the real test, by the operator's override of R8 point 3, as rounds 26 and 27 were. Close conditions: the Full acceptance on `.17` installed through their app, from their 0.6.61 with `PIN_UNDER_REVIEW` `e0471f4`; both sides' reading of the bundle; R8's two releases (their `FORK_PIN` roll to `e0471f4`, our `.18`). Close-by 2026-10-24. **Our lap 1** is the first opening lap in LSL. It corrects round 27 lap 6's account of that round's testing, asks which `Encoder errors:` form they would read for `.18`, and answers their LSL amendments 1: F1–F4 fixed or written into the spec (`eea9e50`), A1, A2 and A4–A8 accepted, A3 amended, H1–H3 accepted for protocol v7, and a proposal B1 of ours. **Their lap 2 is released**, `OPEN`, read at `platterpus@a881716` on their `main`: sha256 `c1b8d15d…`, 11,541 bytes, filed byte-exact as `inbound/round-28-lap-02.md`. It accepts our close conditions S6–S8 (S10) and our A3 amendment (S11), so A1–A8 go into `LSL: 2`; it accepts our `.18` `Encoder errors:` change (S16) and amends our B1 to deterministic commands only (S17); and it records a §6b override for 0.6.61, correcting their round 27 lap 5, which said none was needed (S1). Their digest `682f442fb68813c3` over our lap 1 reproduces, and our checker reads the lap as well formed with 0 warnings. Its three portable shapes were checked against our tree and each had an instance, fixed at `f309743`, `126c433` and `f5ba200`. **Our lap 3 is released**, `OPEN`, before the Full run, by the operator's word of 2026-09-27: sha256 `0a8f3e0f…`, 12,784 bytes, in LSL 1, which both checkers read as well formed with 0 warnings (ours at the lap's commit, theirs at `platterpus@404fe8e`). It gives `.17`'s contract (sha256 `c6bc6c89…`), announces `.18`'s `Encoder errors:` count and new `Partial files:` line, reports LSL 2 implemented and their worked example read as their §6 says, notes their checker reads only `LSL: 1`, accepts their B1 amendment, asks B2 and B3 about two holes in A1 and A7, and pre-commits our lap 4 to `GO` unless the run shows a defect in `.17` that breaks the pin. **Their lap 4 is released**, `OPEN`, read at `platterpus@785925a` on their `main` (released at `a84a1c1f`): sha256 `9719aabb…`, 13,449 bytes, filed byte-exact as `inbound/round-28-lap-04.md`. It asks nothing of us (S29). It confirms lap 3's claims against both trees, files `.17`'s contract (S11), claims `Partial files:` as a line their parser knowingly ignores (S15), and accepts B2, B3 and B1 as amended as LSL 3, to implement once the text is in the shared proposal (S22–S25). It notes `.18`'s contract changes three stable rows, not two (S6, S7), and pre-commits their lap after ours to `GO` unless the bundle shows a defect in 0.6.61 or `.17` that breaks the pin (S33). Both its digests reproduce, `ea02f995b25796e3` over three laps and `fedab85f0b1fe638` over two, and our checker reads it as well formed with 0 warnings. **Our lap 5 is released**, `OPEN`, before the Full run, by the operator's word of 2026-09-28, *"release the lap when ready"*: sha256 `2afde847…`, 26,682 bytes, protocol 6, in LSL 1, which both checkers read as well formed with 0 warnings (ours at the lap's commit, theirs at `platterpus@785925a`). It declares protocol 6 for the rest of the round (S5–S7), with our gate rehearsed closing on their reading lap at 6 and refusing it at 5; corrects lap 3's next-lap number (S1); announces the rest of `.18` with its contract delta measured against `.17`'s: 308 stable rows against 306, P5 120 against 120, and P5a unchanged, because writing the lap found that splitting out the AccurateRip parser had dropped a row from P5a that their error matcher and a test of theirs name, fixed at `a646d54` before the lap was sent (S9–S21, S17); answers from our source the question beside their parser's `AccurateRip:` pattern, whether per-track rows print for a disc not in the database: they do (S13); finds none of their S27–S28 shape in our tests (S22); reports LSL 3 landed, which is their S25's condition (S23); lists each file it cites with its sha256 (S26–S33); and answers the operator's proposal, its facts, FK1–FK7 and our half of J1–J5 (S34–S61). Its digest is `7d71c2d922ae79ea` over four laps. **Their laps 6 and 7 are released**, both `OPEN` at protocol 6, read at `platterpus@079f592` and filed byte-exact: lap 6 (sha256 `8bb70679…`, 20,793 bytes) checks our lap 5 in both their checkers, carries 0.6.62, and records an override moving the Full run to 0.6.62 (S36) with a `BLOCKING` question on it (S37); lap 7 (sha256 `bb35415b…`, 21,267 bytes) answers the operator's proposal for round 29. Their digests reproduce on our tool, `81c1c08a13921558` over five laps and `df4ed98900ae6379` over six. **The Full run had already happened, on 0.6.61**, from 01:48:08Z to 07:08Z, before 0.6.62 existed and before either lap was written; neither side held its bundle then. The operator chose that it closes the round (`docs/rig-2026-09-28-e0471f4/`). **Our lap 8 is released**, `GO`, by the operator's word of 2026-09-28, *"release lap 8, they will do lap 9 after"*: sha256 `547872a5…`, 12,348 bytes, at protocol 6, in LSL 1, which both checkers read as well formed with 0 warnings (ours at the lap's commit, theirs at `platterpus@079f592`): it reads the run (S1–S11), answers their `BLOCKING` S37 with the operator's decision (S12–S14), keeps lap 3 S29 (S16–S17), and names `.18` and their `FORK_PIN` roll as R8's releases (S18). Its digest is `1e8882f019bdef1f` over seven laps, and our gate is rehearsed closing on a released `GO` lap 9 of theirs at protocol 6. **Their lap 9 is released**, `GO` at protocol 6, read at `platterpus@41f92220` on their `main` and filed byte-exact: sha256 `2c16d819…`, 14,882 bytes. It reads its half of the bundle (S8–S15): two archival defects of theirs, both fixed, and none in `.17`. It finds our lap 1's close conditions met (S20), rolls their `FORK_PIN` to `e0471f4`, and names their 0.6.63 and our `.18` as R8's releases (S22, S23). Three behaviours of our repeat loop go to round 29 (S16, S17, S19). Its digest, `27a1515bdec5949c` over eight laps, reproduces on our tool, and both checkers read it as well formed with 0 warnings. Our gate reads the round **closed** on it: *"peer GO resolved per v6 §5b from round-28-lap-09.md, which supersedes our transcription of peer lap 7 (OPEN)"*. That is what lap 5 S6 said it would do. Their lap names its own version as 0.6.62 at `9e96fa0` and ours names the tested 0.6.61, so the two closing files name different parties (`docs/KNOWN-ISSUES.md`, shared-documents row 14, for round 29) |
| **round 27** | **CLOSED `GO`/`GO`** 2026-09-26; opened 2026-09-24 by our lap 1 on **`221a1df`** (`.16`) before the real test, by the operator's override of R8 point 3 again. Close conditions: the Full acceptance on `.16` installed through their app from a release whose `PIN_UNDER_REVIEW` is `221a1df`; both sides' reading of the bundle; R8's two releases (their `FORK_PIN` roll to `221a1df`, our `.17`). Carried, not conditions: the `Accurip 450` wording, album loudness, their three bug patterns, and proposed wording for R8 point 3. Close-by 2026-10-22. **Our lap 1** was marked released at `87facd5`, returned to held under the operator's override and revised to name their **0.6.59**, and released again once `v0.6.59` (`183073b`) showed `PIN_UNDER_REVIEW` `221a1df` (sha256 `c3a7a2a4…`). **Their lap 2** (`OPEN`, sha256 `8ed9d7c2…`, at `platterpus@183073b`) moved `PIN_UNDER_REVIEW` and named 0.6.59, under a §6b override. It answers our lap 1's first version, so its digest (`3d3696c4…`) reproduces only over that version, and `tests/release_gate.py` pins it. Filed at `f1f4784`. **For our lap 3:** both its corrections are applied (the section F container was an earlier Platterpus window's; a stable `Accurip 450` checksum does not show a pressing variant); its B1a, `crip_find_ar()` falling through on a 450 miss, is fixed for `.17`; its B1 and B2 answers are in `docs/KNOWN-ISSUES.md`; its §D amendment waives the §6b override when the consumer's naming lap is released first; and its one question, `NEXT-ROUND`, is answered from the source: `Trying to quit` is printed for SIGINT and SIGTERM only. **Their lap 3** (`OPEN`, sha256 `f4af4c8c…`, at `platterpus@88c09dd`) says the first Full attempt, on 0.6.59, stopped at section A with `.15` installed, because 0.6.59's update offer and setup wizard could each put `FORK_PIN` back over the build under review. **0.6.60** (`88c09dd`) fixes both and is the release the real test runs on, under a second §6b override. It holds our lap 1 as released again. **The operator asked for three items inside round 27, none a close condition, for our lap 4:** (1) **our tests, read by name**: done over all 31 non-image tests. Two were wrong and are fixed: the `Audio checksum mirror`'s docs claimed it catches drift in the C, which it cannot (measured), and `Seam record audit` could never fail and is renamed `Seam gap report`; (2) **nothing of ours installs or restores a build**; (3) **their `Accurip 450` wording, amended**: *"rest of track unverified"* becomes *"whole-track checksums not found"*, because the line prints only after both were compared and missed (`src/cyanrip_log.c:594`), and the confidence moves beside the frame match. Their summary line is accepted as written. **`.17` so far, not released:** the `crip_find_ar()` fix (`10f36fe`) and our own 450 match reworded to `(matches Accurip DB, confidence N, one frame only; whole-track checksums not found)` (`ec0fe47`), a P2 change lap 4 announces. `tools/cross-rip.py` now compares every read of each track across a bundle, for lap 4's reading. **The operator then chose, on 2026-09-26, to close the round without a Full or Standard run**, and to test both projects' next releases together in round 28. **The quick run of that day** (`docs/rig-2026-09-26-221a1df-quick/`) stands in for §0.1: 0.6.60's section A accepted `.16`, and its one rip is clean. **Our lap 4** (`GO`, sha256 `90b7f401…`) records the override of R1, reads that run, names `.17` and announces its 450 rewording. **Their lap 5** (`GO`, sha256 `33ab7dac…`, at `platterpus@edf32c7`) accepts the override and both rewordings, closes the round on their gate and rolls their `FORK_PIN` to `221a1df`. **Our lap 6** (`GO`) transcribes it and closes the round on ours, **CLOSED 2026-09-26, six laps**. It corrects lap 4's candidate to three `src/` commits, adding `ee0221c` (an early failure's log now opens with the banner), and it is the first lap whose body is in LSL, proposed for round 28 |
| **round 26** | **CLOSED `GO`/`GO`** 2026-09-24, **six laps**, 27 days before the close-by. Opened 2026-09-23, opened by our lap 1 on **`df91ae7`** (`.15`) **before** the real test, by the operator's override of R8 point 3. Close conditions: the real test on `.15` installed through their app, both sides' reading of the bundle, and R8's two releases (their `FORK_PIN` roll to `df91ae7`, our `.16`). Close-by 2026-10-21. Their lap 2 (`OPEN`, `8485afc7…`) moved `PIN_UNDER_REVIEW` and named 0.6.54. **Their lap 3** (`OPEN`, sha256 `ba57e7bd…`, read at `platterpus@629ffa2`) says 0.6.54's section A refused `.15`, and names **0.6.55** as the fix, cut under a second §6b override. The test then ran on 0.6.55. **Our lap 4** (`GO`, sha256 `7a56b1d2…`) reads it and names `.16`; released by the operator 2026-09-24. **Their lap 5** (`GO`, sha256 `8c7df540…`, on their `main` at `platterpus@6c1890b`) closes it on their gate, rolls their `FORK_PIN` to `df91ae7`, names 0.6.56 as their release after `.16`, and found a wrong track-1 read our lap 4 missed (`docs/KNOWN-ISSUES.md`). **Our lap 6** (`GO`, sha256 `a5338b20…`) records their verdict and closes it on ours; released by the operator 2026-09-24 |
| round 25 | **CLOSED `GO`/`GO`** 2026-09-23, **five laps**, 14 days before the close-by. Close conditions: the three texts byte-identical in both trees (lap 1 §0.1, §0.2), and both releases ready and agreed (lap 2 §0.3, by the operator's override of R1). Their lap 2 crossed ours, which cost one lap; their lap 4 (`GO`, sha256 `f6d18230…`) landed the merged v6, parsed our golden reference and named 0.6.54; our lap 5 (`GO`) closed it. Pin `3e01bb3`, never moved. Next, under R8: `.15`, then their 0.6.54, then the real test, which opens round 26 |
| round 24 | **CLOSED `GO`/`GO`** 2026-09-23, **three laps**, 13 days before the close-by. One close condition, Platterpus's verdict on `3e01bb3`, met by their lap 2 (`GO`, their 0.6.53 parser reading our golden reference). It closed on their gate at their lap 2 and on ours at our lap 3: the two gates close on different laps, their round-25 item N1. Three laps is the lap-1 `GO`, not v5 |
| round 25, their laps | lap 2: `GO` on the texts, sha256 `3ae11ad1…`, read at `platterpus@5374729`, answering our lap 1 only. Lap 4: `GO`, sha256 `f6d18230…`, 11,717 bytes, read at `platterpus@53b3c04`. Both filed byte-exact under `docs/handshake/inbound/` |
| round 23 | CLOSED `GO`/`GO` 2026-09-22 — five laps by the highest `HANDSHAKE-LAP` either side declared, four by Platterpus's own count. Pin `2cce60d`, reviewed for its behaviour on a drive |
| lap counts | rounds 21, 22 and 23 all took five. In 22 and 23 the fifth lap existed only to carry a transcription, which v5 §5b was adopted to remove — and as written cannot, because step 3 needs a peer lap the closing file could not have declared. `CLAUDE.md` has the measure, why rounds 22–24 could not score v5, and round 25's prediction of four laps, **which failed: round 25 took five**, and the extra lap was the crossing, not the mechanism |

### Round 25

**Opened by our lap 1. Lap 2 carries the operator's instructions of the same
day**, given after lap 1 was released, so it could not travel in it:

- as few rounds as needed, and fix as much as we can;
- physical CD rips, not arguing over bugs and language;
- **every round ends on usable releases of both applications**, and the real
  test on the released pair opens the next round, with its bundle in both
  repositories.

Lap 2 adds that as close condition §0.3 by recorded override of R1, and
proposes it for every round as v6 R8 and R9. Platterpus compiled every known
seam issue into one agenda, `platterpus@86f0547:TASKS.md:57`, and lap 1 §E
places every item on it.

**Their lap 2 crossed ours** and answered our lap 1 only. Our lap 3 proposed
the one v6 both trees could hold, and their lap 4 landed it and supplied the two
§0.3 items. Our lap 5 discharged lap 3's pre-commitment as `GO`.

| text | sha256 | landed |
|---|---|---|
| `docs/handshake/PROTOCOL.md` v6 | `05abdfde706316f8…` | `643631b` here, `platterpus@53b3c04` there |
| `docs/OWNERSHIP.md` v3 | `6956d0b9908a7784…` | `c07bf68` here, `platterpus@5374729` there |
| `docs/seam-rules.md` v6 | `a0d2139338c6e2b7…` | `c07bf68` here, `platterpus@5374729` there |

**Our gate implements 6 from `643631b`**, where landing v6 set the constant, as
`f748d15` did for v5. Every lap still declares 5: v6 §14 waits until both
gates have said in a lap that they implement 6, and ours has said so in lap 5.

### The protocol

| | |
|---|---|
| `PROTOCOL.md` | **v7**, `b9611d3b1b18fff4`, byte-identical in both trees, landed by our lap 7's commit and their `41d34ab2`. `seam-sync-check --fetch` exits **0**, read at `platterpus@bd508bf` |
| what v5 added | §5b, the close rule; §5c, Platterpus's readability condition; `HANDSHAKE-PEER-VERDICT-SOURCE`, their field; rows C37–C42 |
| the gates | **ours implements 7** from the commit that files their round 30 lap 8, **theirs 6**, moving to 7 before their round 31 lap 1 (their lap 8 S41); round 30's laps declare 6. Before that: ours implemented 6 from `643631b`, theirs 5, with 6 next (their lap 4). For a file declaring 5, ours still reads §5b's *"enumerated"* literally and theirs at decision time; v6 adopts theirs, and applies to files declaring 6. `docs/KNOWN-ISSUES.md` keeps it open until a round closes under step 3 |
| **what v6 added** | **K1, K2 and K3**, agreed in rounds 21 and 22 and missing from v5; §5e, the agreed-change ledger; the decision-time §5b; C43–C45; and the operator's **R8** and **R9** |

### Platterpus's side, and how we know each part

| | how we know |
|---|---|
| released **0.6.53**, 2026-09-22, at `52b44282`, tag `v0.6.53`, pre-release as every `v0.*` tag is | `git ls-remote --tags` and `--symref` on their repository |
| 0.6.53 is **the both-wordings release** — `_TRACK_START` matches both pairs, and no earlier tag does | read at `52b44282:src/platterpus/parsers/cyanrip_log.py:237-244`; counted across four tags |
| on their `main`, **`FORK_PIN = "3e01bb3"`** and `PIN_UNDER_REVIEW = "3e01bb3"` — the roll, not yet released | read at `86f0547:src/platterpus/deps/fork_source.py:196` and `:568` |
| `APPROVED_BY_ROUND = 24`, `APPROVED_FOR_PLATTERPUS_VERSION = "0.6.53"` | read at `86f0547:src/platterpus/handshake_approval.py:229` and `:141` |
| **Platterpus 0.6.54 is released**, tag `v0.6.54` at `b381c31`, their `main`. In it `PIN_UNDER_REVIEW` is `df91ae7` (round 26) and `FORK_PIN` is still `3e01bb3`, which rolls to `df91ae7` when round 26 closes. Their gate implements protocol 5 and refuses a round in which any file declares more (`scripts/handshake.py:1920`) | `git ls-remote --tags` and a fetch; read at `b381c31:src/platterpus/deps/fork_source.py:196`, `:582`, `:596`, and `src/platterpus/__init__.py:13`. **Whether its GitHub release page and build are up was not checked**: this environment reads their git, not their API |
| their app **offers, never installs**, a newer build from our manifest on the user's channel, and says it will report `unapproved` until a round verifies it | read at `52b44282:src/platterpus/deps/ripper_manifest.py:1-16`, `:66-68`, and `5374729:src/platterpus/config.py:383-393` |
| their `FORK_PIN` must equal the pin of their newest closed round, so it cannot name a release cut after the close | read at `5374729:tests/test_fork_source.py:132-190` |
| their standing status, as of 0.6.53 | filed byte-exact twice, because it was rewritten the same day under the same as-of: `docs/handshake/inbound/status-2026-09-22-v0.6.53.md` (read at `52b44282`, sha256 `2ac99eb5…09ab9`, 39,016 bytes) and `…-2026-09-22-v0.6.53-c2f43d28.md` (read at `c2f43d28`, sha256 `ddfcbbe6…62ac0`, 43,166 bytes) |
| their branch-delete cause was a repository setting, now off | **relayed**, and corroborated rather than proven: the cited commits are reachable again as ancestors of `claude/session-omka9f` at `9cc23eab` |

### What is still open

The list is `docs/KNOWN-ISSUES.md` and it is not repeated here. The headline
items:

- `File(s):` is still built from the request.
- The loudness block is measured upstream of the filter graph.
- The cache figure is wrong on all ten filed sessions.
- There is no way in our format to mark a superseded or abandoned read.
- **At `-P 0`, one unreadable sector still hangs the rip**, at any `-r`.
  Platterpus never passes `-P`.

Round 23's `Handshake:` qualifier is now built (`20a5aca`), and the `-r` hang
at the default level is fixed (`2af669e`). Both ship in `.15`.
**The four shared documents carried thirteen known defects**, tabled in one
place under *"The four shared documents: every known defect"*. Round 25 fixed
the eight in three of the documents as one bump. The five in `seam-commands.md`
wait for round 26, because their fix needs `tools/probe-argv-surface.py` to
measure what it asserts.

### Where their statuses are filed

Ten, each dated by the date **it declares**, not the day we received it:
`docs/handshake/inbound/status-2026-08-21-v0.6.21.md`, `…-2026-08-21-v0.6.23.md`,
`…-2026-08-24-v0.6.23.md`, `…-2026-09-21-v0.6.52.md`, `…-2026-09-22-v0.6.53.md`,
`…-2026-09-22-v0.6.53-c2f43d28.md`, `…-2026-09-23-v0.6.53.md`,
`…-2026-09-23-v0.6.53-53747294.md`, `…-2026-09-23-v0.6.53-53b3c046.md` and
`…-2026-09-23-v0.6.54.md`. Each later file of a pair that declares the
same as-of carries the commit it was read at — the one identifier that tells
them apart. **Theirs are evidence and are never consolidated;
ours is a claim about now and is rewritten** — the two rules are opposite and
both are right. None declares a live wire header; the `HANDSHAKE-*` lines in the
newest are inside a fenced example, and `test_a_standing_status_is_never_counted_as_a_lap()`
executes that rather than trusting it.

### Upstream

Our `master` mirrors `cyanreg/cyanrip` at `f8ebf48` (2026-08-21), and
**upstream has not moved since**: `git ls-remote` on 2026-09-28T00:15Z returned
`f8ebf48` for `cyanreg/cyanrip`. **`f8ebf48` is merged into `platterpus-fork` at
`1fb6f07`**, on the operator's decision of 2026-09-28, for `.18`; its analysis,
measured CLI surface included, is `docs/upstream/sync-2026-08-24-mb-retry.md`.
That is a reading of one moment; `tools/upstream-delta.py` is how to check again.
**Thirteen defects of ours exist upstream and none is filed there**: twelve
drafted in `docs/upstream/defect-reports.md` and the cache model in
`docs/upstream-cachemodel-report.md`, each re-checked by `tools/check-settled.py`
against `master`.

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

**Every `0.9.4-rc2+platterpus.N` the manifest calls stable IS stable.** The
`-rc2` is upstream's own string, copied verbatim because we may not mint in `cyanreg/cyanrip`'s namespace;
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

**No release while any round is open.** `tools/release-gate.py --release-gate`
names the open round; the *Now* section above says which it is. The previous
text of this paragraph named round 16 for five weeks after that round closed,
which is why it no longer names one.
