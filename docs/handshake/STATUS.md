# cyanrip standing status — what the consumer can assume between rounds

STATUS-NEWEST-LAP: round-32-lap-07.md
STATUS-NEWEST-LAP-STATE: sent

STATUS-ROUND: 32, OPEN, opened by our lap 1 on +platterpus.22 at 200530e; HR-1.7 (4) and (5) hold on both sides, our check passes your lap 6, and our lap 7, sent on 2026-10-13, waits on yours, which completes HR-1.7 (6), after which your 0.7.104 follows; round 31 closed on 2026-10-11, approving +platterpus.21 at ca3f3ea with your 0.6.66
STATUS-LAPS: newest sent round-32-lap-07.md (ours), round-32-lap-06.md (theirs); next 8 (theirs) carrying your reading of the Full run on .22 with 0.7.104, made on 2026-10-13 and filed here; held none
STATUS-RELEASED: +platterpus.22 at 200530e, 2026-10-12
STATUS-RELEASE-NEXT: +platterpus.23, no longer held by HR-1.3, since HR-1.7's check passed on 2026-10-13, or by the Full run on .22 with your 0.7.104, filed here on 2026-10-13 (our lap 3 S16, docs/rig-2026-10-13-200530e/), carrying the -j record's /8 fields and track 1's pregap count from the start of the disc, both landed for round 32, and upstream's 0.9.4-rc3, merged at 79da685, with -j at /9 and two new disc lines and data-track rows your parser must accept first (docs/upstream/sync-2026-10-12-rc3.md section 4), and with the short options -j, -k, -u and -x retired for their long names, so your argv must send --diagnostics rather than -j before it can run this build (Changelog.md), which your 0.7.104 does (your lap 6 S14); pins ca3f3ea, reviews +platterpus.22
STATUS-RUN-NEXT: +platterpus.23 with 0.7.105; waiting on both releases: +platterpus.23, once your parser accepts upstream 0.9.4-rc3's new lines (STATUS-RELEASE-NEXT), and your 0.7.105, your next release by your status at platterpus@39b6c366, or the first later one whose section A accepts +platterpus.23; round 32's run, +platterpus.22 with 0.7.104, was made on 2026-10-13 and is filed in docs/rig-2026-10-13-200530e/
STATUS-OPEN: repeat-limit-last-read us fixing at 200530e, priority 1: landed at ab0f49b with the wording your lap 2 S14 accepted, released in +platterpus.22, and open until a drive prints it: round 32's Full run on 2026-10-13 hit the repeat limit twice, on track 3 in the secure re-read and in the securing pass, each with five checksums in five reads, so the newest read was kept, which is the last, and the clause rightly did not print; when the read kept at the repeat limit is not the last, the Done; line names the last read's checksum
STATUS-OPEN: gaps-undetermined-pregap us fixing at 200530e, priority 1: landed at 4a0fc55 with the wording your lap 2 S15 accepted, released in +platterpus.22, and open until a drive prints it: no pregap search failed in round 32's Full run on 2026-10-13, so the line had no cause to print; a pregap whose search failed is a pregap of track N unknown (reason) line in the Gaps: list, and None signalled prints only when no line did
STATUS-OPEN: partially-accurate-tally-label us fixing at 200530e, priority 1: landed at 113c05f, released in +platterpus.22, and read on a drive by round 32's Full run on 2026-10-13, where both whole-disc rips print Tracks matched on one frame only: 2/14, so it leaves this list when round 32 closes; the one-frame tally reads Tracks matched on one frame only:, which your 0.6.66b1 and every release since reads
STATUS-OPEN: j-record-fields us fixing at 51445c1, priority 2: -j fields for pre-emphasis, the disc's own ISRC beside the one written, CD-TEXT and the -f result, asked by your round 31 lap 3 S5, S8, S9 and S12, proposed in our round 32 lap 1 S10, and accepted in your lap 2 S7 with S8's amendment, cdtext's keys listed in P8b with their types; landed at 51445c1, ships in +platterpus.23, and the disc ISRC read has run on no drive
STATUS-OPEN: track1-pregap-base us fixing at a64d58d, priority 3: track 1's Pregap length: prints 150 frames for an ordinary disc's lead-in and for two seconds before track 1 alike, told apart only by Pregap source:; counting from LBA 0, proposed in our round 32 lap 1 S13, accepted in your lap 2 S10 with no release of yours first (S11); landed at a64d58d, ships in +platterpus.23
STATUS-OPEN: version-field-meaning both fixing at round 32, priority 4: round 31's closing files name different Platterpus builds as the party, 0.6.66 in ours and 0.7.102 in yours, as round 28's did; our lap 1 S16's reading, the build the round reviewed, accepted in your lap 2 S12, and both closing laps of round 32 use it
STATUS-OPEN: overread-bounded us fixing at round 32, priority 5: under -O a frame past the disc's last sector is retried up to the retry limit with no timeout of ours; a bounded read proposed in our round 32 lap 1 S18, verifiable only on a drive
STATUS-OPEN: accurate-stream-declared us fixing at round 32, priority 5: a header line saying what the drive's capabilities page declares about accurate stream, proposed in our round 32 lap 1 S19, readable only on a drive
STATUS-OPEN: subchannel-pregap-varies us fixing at round 32, priority 5: track 9's sub-channel pregap reads 94 or 95 frames between rips in eleven filed sessions and the log states one value; a line giving both counts when two searches disagree proposed in our round 32 lap 1 S19, and which frame is right still needs the drive
STATUS-OPEN: error-positions us fixing at round 33, priority 8: each track's positions of read errors and skips in the -j record, your F5's second addition, from the position paranoia passes our status callback, which we discard today; re-read mismatch positions are not computed at all, since -Z compares whole-track checksums
STATUS-OPEN: exit-classes us fixing at round 33, priority 8: round 8's three exit classes, a flag this build lacks, a disc or drive failure apart from a refused argument, and cancelled or signalled, and a sixth -Y code, from your F8; 1 is the generic code at 30 sites today and 2 to 5 are -Y's, so it is a P4 change proposed in a lap before it lands
STATUS-OPEN: unsent-flag-rows us fixing at round 33, priority 8: docs/seam-commands.md has rows for the flags you send, and every other flag of ours needs one reading NO: <reason> or ?, from your F8
STATUS-OPEN: flag-limits us fixing at round 33, priority 9: a boundary row in docs/seam-commands.md for each flag you send, min, max and one past each, from tools/probe-argv-surface.py's runs, -d, -c, -l and -t first, from your F9
STATUS-OPEN: recordable-medium-line us fixing at round 33, priority 9: a tri-state line saying whether the drive reports the disc as recordable, from your F9, readable only on a drive
STATUS-OPEN: all-pass-paranoia-counters us fixing at round 33, priority 9: a -Z track's paranoia counters summed over every read, beside the last read's, which the Scope: line qualifies, from your F9
STATUS-OPEN: encoder-options-flag us fixing at round 33, priority 9: a repeatable key=value flag passing options to the encoder, not -O, from your F9
STATUS-OPEN: hardware-unverified us cannot, because each needs a disc or a drive this environment lacks: C2, which the rig's drive reports unsupported; CD-TEXT from a physical disc; -W on a pre-emphasised disc; a paranoia skip on a drive; -f on a second drive, and a -f search that finds nothing on a drive; and -P 0's sector-by-sector salvage on a drive; asked of your rig in our round 32 lap 1 S21
STATUS-OPEN: superseded-read-marker both cannot, because the format needs a design both sides agree (round 24's item, with round 8 J14's read time); asked in our round 32 lap 1 S22 whether to keep it
STATUS-OPEN: files-listed-from-request us cannot, because moving File(s): changes a P2 block you parse and no design exists; asked in our round 32 lap 1 S22 whether to keep it
STATUS-OPEN: upstream-reports-unfiled us cannot, because filing on upstream's tracker is the maintainer's act, which the operator said on 2026-10-05 they will do; all twenty-three are drafted in docs/upstream/issues-to-file.md
STATUS-OPEN: suite-timeouts-at-default us cannot, because neither settling run reproduces a timeout (the suite serially, and each test under the two heaviest), so no mechanism is known to fix; each occurrence is recorded
STATUS-OPEN: windows-ci-unpinned us cannot, because the operator decided on 2026-10-05 to leave the Windows build as upstream ships it, and no consumer uses its artifact
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

## Now — rewritten 2026-10-12: `.22` released, round 32 being opened

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
  step E2, and our reading in that folder's README finds no defect of ours.
  Their lap 8, with their reading, is next.
- The table of every round is the handshake README's, and the gate is the
  authority over both.

### Runs

| | |
|---|---|
| newest | **`.22` with Platterpus 0.7.104, Full, on the reference disc, 2026-10-13** (`docs/rig-2026-10-13-200530e/`): 424 pass, 0 fail, the one unreachable step E2; round 32's test, read by us in that folder's README; Platterpus's reading is their lap 8, not yet published |
| next | the first run of `.23`, once it is released; none scheduled |

Every earlier run is a `docs/rig-*` folder with its own README.

### The protocol

`PROTOCOL.md` v8 and `seam-rules.md` v8 are byte-identical in both trees
(`tools/seam-sync-check.py --fetch` at `platterpus@2d8644a`, exit 0) and govern
from round 32. **Both gates implement 8**: ours from `2e800f4`, theirs from
`platterpus@01fd8eac`. Our round 32 lap 1, which declares 7, says so, and our
laps declare 8 from our next one.

### Platterpus's side, read and not run

Their newest release is 0.7.103, tag `v0.7.103` at `2f7855be`, read with
`git ls-remote` on 2026-10-12. Their
standing status is `docs/handshake/outbound/platterpusstatus.md` in their tree,
read at `808f8fb1`: its block names nine open items of theirs, it ranks F1 to
F9 for us, which our round 32 lap 1 answers, and its `STATUS-RUN-NEXT` expects
round 32 on `.22` with 0.7.103, as ours does.
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
