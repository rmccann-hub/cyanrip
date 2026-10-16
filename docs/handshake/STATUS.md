# cyanrip standing status — what the consumer can assume between rounds

STATUS-NEWEST-LAP: round-34-lap-02.md
STATUS-NEWEST-LAP-STATE: held

STATUS-ROUND: 34, OPEN, opened by our lap 1, sent 2026-10-15, on +platterpus.23 at 891c79e, and it closes on the Full run on it through your first release naming 891c79e as its build under review, read by both sides (lap 1 S14); lap 1 carries what is known now and leaves the rest to the run, by our operator's rule of 2026-10-15; round 33 closed on 2026-10-15, approving +platterpus.22 at 200530e with your 0.7.105
STATUS-LAPS: newest sent round-34-lap-01.md (ours), none (theirs); next 2 (theirs) carrying whatever you have to say of our lap 1, and your reading of the Full run once it is filed; held 2 carrying our answers to your TASKS R12 and X9's narrowing, two stale lines of yours, and what we landed of lap 1's known items, renumbered under K1 if your lap 2 is released first
STATUS-RELEASED: +platterpus.23 at 891c79e, 2026-10-15
STATUS-RELEASE-NEXT: +platterpus.24, whenever it is ready (v8 §6b), carrying what round 34 accepts; +platterpus.23 is on the beta channel and the stable channel stays +platterpus.22 at 200530e, which round 33 approved with your 0.7.105; pins 200530e, reviews +platterpus.23
STATUS-RUN-NEXT: +platterpus.23 with 0.7.106; waiting on your 0.7.106's release, whose commit 47159768, on your main at dd200af7, already names 891c79e as its build under review for round 34 and carries a message inventory equal to .23's P5 (our lap 1 S7); that run is round 34's test; round 33's run, +platterpus.22 with 0.7.105 on 2026-10-14, is filed on your evidence branch at f57cdc2b
STATUS-OPEN: repeat-limit-last-read us fixing at 200530e, priority 1: landed at ab0f49b with the wording your lap 2 S14 accepted, released in +platterpus.22, and open until a drive prints it: round 32's Full run on 2026-10-13 hit the repeat limit three times, all on track 3, in the secure re-read and in both securing passes, each with five checksums in five reads, so the newest read was kept, which is the last, and the clause rightly did not print; when the read kept at the repeat limit is not the last, the Done; line names the last read's checksum
STATUS-OPEN: gaps-undetermined-pregap us fixing at 200530e, priority 1: landed at 4a0fc55 with the wording your lap 2 S15 accepted, released in +platterpus.22, and open until a drive prints it: no pregap search failed in round 32's Full run on 2026-10-13, so the line had no cause to print; a pregap whose search failed is a pregap of track N unknown (reason) line in the Gaps: list, and None signalled prints only when no line did
STATUS-OPEN: j-record-fields us fixing at 51445c1, priority 2: -j fields for pre-emphasis, the disc's own ISRC beside the one written, CD-TEXT and the -f result, asked by your round 31 lap 3 S5, S8, S9 and S12, proposed in our round 32 lap 1 S10, and accepted in your lap 2 S7 with S8's amendment, cdtext's keys listed in P8b with their types; landed at 51445c1, released in +platterpus.23 at 891c79e on the beta channel, and the disc ISRC read has run on no drive
STATUS-OPEN: track1-pregap-base us fixing at a64d58d, priority 3: track 1's Pregap length: prints 150 frames for an ordinary disc's lead-in and for two seconds before track 1 alike, told apart only by Pregap source:; counting from LBA 0, proposed in our round 32 lap 1 S13, accepted in your lap 2 S10 with no release of yours first (S11); landed at a64d58d, released in +platterpus.23 at 891c79e on the beta channel
STATUS-OPEN: overread-bounded us fixing at round 34, priority 5: under -O a frame past the disc's last sector is retried up to the retry limit with no timeout of ours; a bounded read proposed in our round 32 lap 1 S18, verifiable only on a drive; first in your order of our round 32 lap 1 S18 and S19 (your round 32 lap 2 S19)
STATUS-OPEN: accurate-stream-declared us fixing at round 34, priority 5: a header line saying what the drive's capabilities page declares about accurate stream, proposed in our round 32 lap 1 S19, readable only on a drive
STATUS-OPEN: subchannel-pregap-varies us fixing at round 34, priority 5: track 9's sub-channel pregap reads 94 or 95 frames between rips in eleven filed sessions and the log states one value, and track 4's 158-frame pregap reads 0 in 4 of the 211 filed logs of the reference disc, once on .22 on 2026-10-13, where the search returned zero rather than failing and that rip's cue sheet gives track 4 no INDEX 00; a line giving both counts when two searches disagree proposed in our round 32 lap 1 S19, and which frame is right still needs the drive
STATUS-OPEN: error-positions us fixing at round 34, priority 8: each track's positions of read errors and skips in the -j record, your F5's second addition, from the position paranoia passes our status callback, which we discard today; re-read mismatch positions are not computed at all, since -Z compares whole-track checksums
STATUS-OPEN: exit-classes us fixing at round 34, priority 8: round 8's three exit classes, a flag this build lacks, a disc or drive failure apart from a refused argument, and cancelled or signalled, and a sixth -Y code, from your F8; 1 is the generic code at 30 sites today and 2 to 5 are -Y's, so it is a P4 change proposed in a lap before it lands
STATUS-OPEN: unsent-flag-rows us fixing at round 34, priority 8: docs/seam-commands.md has rows for the flags you send, and every other flag of ours needs one reading NO: <reason> or ?, from your F8
STATUS-OPEN: flag-limits us fixing at round 34, priority 9: a boundary row in docs/seam-commands.md for each flag you send, min, max and one past each, from tools/probe-argv-surface.py's runs, -d, -c, -l and -t first, from your F9
STATUS-OPEN: recordable-medium-line us fixing at round 34, priority 9: a tri-state line saying whether the drive reports the disc as recordable, from your F9, readable only on a drive
STATUS-OPEN: all-pass-paranoia-counters us fixing at round 34, priority 9: a -Z track's paranoia counters summed over every read, beside the last read's, which the Scope: line qualifies, from your F9
STATUS-OPEN: encoder-options-flag us fixing at round 34, priority 9: a repeatable key=value flag passing options to the encoder, not -O, from your F9
STATUS-OPEN: settled-facts-macos us fixing at round 34, priority 4: Settled facts timed out on CI's macOS runner on the push of b06d20e at 120.03 s, after 93.08 s on the same tree at da0db2c and 30.73 s at 21382e4 the same day, and once before at 3e467b3 at 120.05 s; no cause is established (our lap 1 S8, docs/KNOWN-ISSUES.md)
STATUS-OPEN: hardware-unverified us cannot, because each needs a disc or a drive this environment lacks: C2, which the rig's drive reports unsupported; CD-TEXT from a physical disc; -W on a pre-emphasised disc; a paranoia skip on a drive; -f on a second drive, and a -f search that finds nothing on a drive; and -P 0's sector-by-sector salvage on a drive; asked of your rig in our round 32 lap 1 S21
STATUS-OPEN: superseded-read-marker both cannot, because the format needs a design both sides agree (round 24's item, with round 8 J14's read time); asked in our round 32 lap 1 S22 whether to keep it
STATUS-OPEN: files-listed-from-request us cannot, because moving File(s): changes a P2 block you parse and no design exists; asked in our round 32 lap 1 S22 whether to keep it
STATUS-OPEN: upstream-reports-unfiled us cannot, because filing on upstream's tracker is the maintainer's act, which the operator said on 2026-10-05 they will do; all twenty-three are drafted in docs/upstream/issues-to-file.md
STATUS-OPEN: suite-timeouts-at-default us cannot, because neither settling run reproduces a timeout (the suite serially, and each test under the two heaviest), so no mechanism is known to fix; each occurrence is recorded
STATUS-OPEN: release-markers us cannot, because building or retiring the release/* markers of docs/UPGRADE-CHANNELS-PLAN.md §6a is the operator's decision, now that v8 decouples releases from rounds; put to the operator on 2026-10-12

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
close conditions at lap 1, and an open round blocks both sides' releases. Between
rounds each side still needs somewhere to say where it is.

**Rewritten in place, never appended to.** A stale standing status is worse than
none. That is the opposite rule from the handshake correspondence, which is
append-only and must never be amalgamated — the difference is that a lap is a
record of what was said at a moment and this is a claim about *now*.

---

## Now — rewritten 2026-10-16: round 34's lap 1 sent and lap 2 held, the run ready on `.23` with 0.7.106

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
- **`.23` is released, on the beta channel**, at `891c79e`, 2026-10-15, on
  the operator's word. The stable channel stays `.22`.
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
- **Round 34's lap 2 is ours, held** (`round-34-lap-02.md`). It answers what
  Platterpus's status and TASKS ask of us: R12's two questions (the flag table
  for `-X` and `-B` is P1 of `.23`'s contract, and whether a build fingerprints
  shows in its `AcoustID:` line), X9 as they narrowed it, accepted, and two
  stale lines of theirs. It reports three commits: the lap checker printing
  hashes whole, X6 to X10 recorded as landed, and three open items moved off
  round 32. Their 0.7.106 was tagged at `dd200af7` on 2026-10-16, so the run
  can run.
- **What we would ask of Platterpus next**, to make a run easier to read, is in
  the handshake README's data register, X6 to X10: each securing pass's
  record, a hash per bundle member, `--consumer` and `--diagnostics` on the
  pre-emphasis rips, home paths replaced at export, and the bundle's hash in
  their reading lap. Their lap 8 meets X10 and takes X6 as their own fix for
  round 33; our lap 9 asks X7 to X9 for round 33.
- The table of every round is the handshake README's, and the gate is the
  authority over both.

### Runs

| | |
|---|---|
| newest | **`.22` with Platterpus 0.7.105, Full, on the reference disc, 2026-10-14** from 11:07:56Z: 425 pass, 0 fail, 1 blocked (the Cover Art Archive answered HTTP 500), the one unreachable step E2; round 33's test, filed on Platterpus's evidence branch at `f57cdc2b` and read in our round 33 lap 7 (S2, S3) |
| next | **`.23` with their 0.7.106**, round 34's test, once 0.7.106 is released; `.23` is published, on the beta channel, at `891c79e` |

Every earlier run is a `docs/rig-*` folder with its own README.

### The protocol

`PROTOCOL.md` v9, which is v8 plus HR-2 and HR-2.1 (§17), is byte-identical
in both trees from `platterpus@37826a5f` (`tools/seam-sync-check.py --fetch`,
2026-10-14), and governed round 33. **Both gates implement 9**: ours from
`aae9164`, theirs as their round 33 lap 2 says, and every lap of round 33
from our lap 3 on declares 9.

### Platterpus's side, read and not run

Their newest release is 0.7.105, tag `v0.7.105` at `b33b90d4`, read with
`git ls-remote` on 2026-10-15. Their standing status is
`docs/handshake/outbound/platterpusstatus.md` in their tree, read at
`049111ed`: it reads round 33 closed on both gates, and its `STATUS-RUN-NEXT`
expects round 34's run on `.23` with 0.7.106, as ours does.
Seventeen of their earlier statuses are filed under
`docs/handshake/inbound/status-*.md`, each dated by the date it declares; theirs
are evidence and are never consolidated, and ours is a claim about now and is
rewritten.

### Open items

**The block's `STATUS-OPEN` lines are the list, in priority order**, each saying
whether it is being fixed or stays open and why; `docs/KNOWN-ISSUES.md` has the
detail. Priority 1 is released in `.22` and stays listed until round 32's
Full run reads it on a drive. Priorities 2 to 4 are what round 32 asks
of Platterpus to close, and priority 5 needs a drive. Round 32's lap 1 gives
priorities 6 and 7 to runs only a drive can give and to four parked joint
items. Priorities 8 and 9 are what Platterpus's standing status ranked for us
on 2026-10-12, F5's second addition and F8 and F9, for round 33. The rest stay
open, each with its reason.

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
again. **Twenty-three defects this fork found in upstream's code are not filed
there**: all are drafted, ready to paste, in `docs/upstream/issues-to-file.md`,
each re-checked against `master` by `tools/check-settled.py`. Filing them is
the maintainer's act.

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

**A release does not wait for a round** (`PROTOCOL.md` v8 §6b). `tools/release-gate.py
--release-gate` names every open round and permits; the suite on the release
commit from a clean checkout is what refuses one, and a round reviews the
released pair afterwards. Until v8 this paragraph said *"No release while any
round is open"*, and it outlived that rule by a release.
