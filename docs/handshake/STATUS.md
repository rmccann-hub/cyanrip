# cyanrip standing status — what the consumer can assume between rounds

STATUS-NEWEST-LAP: round-42-lap-01.md
STATUS-NEWEST-LAP-STATE: sent

STATUS-ROUND: 42, OPEN, on our lap 1, OPEN, and your lap 2, OPEN; it reviews +platterpus.35 at 1280aa4 with your 0.7.129, which names it under review, and closes on our lap 1 S32, which your lap 2 S21 accepts as given: one default whole-disc rip of it and your C2 probe, filed, and each side's gate on protocol v10, which both lap 1 S9 and your lap 2 S5 now say
STATUS-LAPS: newest sent round-42-lap-01.md (ours), round-42-lap-02.md (theirs); next 3 (ours) carrying our reading of your lap 2, declaring protocol 10; we write it, and only we do; held none
STATUS-RELEASED: +platterpus.35 at 1280aa4, 2026-11-17
STATUS-RELEASE-NEXT: +platterpus.36, not built: what round 42 agrees, among them the Ripping errors: parts as a complete list (our round 41 lap 5 S8) and the two AccurateRip fixes (docs/OPEN-ITEMS.md US-32); +platterpus.35 is on the beta channel from 2026-11-17 for round 42 to review, and +platterpus.34, the pin round 41 approved, is on stable from 2026-11-23; pins fb28088, reviews +platterpus.35
STATUS-RUN-NEXT: +platterpus.35 with 0.7.129; waiting on the bundle of our owner's Full run of round 42, which ran through 0.7.129 on 2026-11-23 and 24 and has not reached us, and on your C2 probe at seconds 240, 244, 245, 251 and 252 of track 3, 144 of track 5 and 162 of track 1, which stopped before any read on 2026-11-24 because Platterpus was still open; your overreadprobe ran 2026-11-17 on +platterpus.34 and is filed on our evidence branch at 1a16efe (docs/rig-2026-11-17b-overreadprobe/)
STATUS-OPEN: track1-pregap-base us fixing at a64d58d, priority 3: track 1's Pregap length: counted from LBA 0, proposed in our round 32 lap 1 S13 and accepted in your lap 2 S10, released in +platterpus.23 at 891c79e; the reference disc's track 1 starts at LSN 0, so no run of it can tell the two counts apart, and a disc with a pregap before track 1 is what settles it (docs/OPEN-ITEMS.md HW-11)
STATUS-OPEN: overread-bounded us fixing at bfe71ec, priority 1: under -O a frame outside the disc is read once, a refused one written as silence, and a track that read any says Beyond disc: N of M frames refused (written as silence); released in +platterpus.24 at 93afa15; on 2026-11-17 your overreadprobe ran it under +platterpus.34 on the BDR-209D, which refused 2 of 2 frames past the lead-out and 2 of 2 before LSN 0, each read once and written as silence in about a minute (docs/rig-2026-11-17b-overreadprobe/), so it stays open only for a drive that answers past its lead-out (docs/OPEN-ITEMS.md HW-10)
STATUS-OPEN: subchannel-pregap-varies us fixing at 8726bd3, priority 5: a pregap the TOC does not signal read differently between rips of one disc while the log stated one value; fixed by placing each Q frame at the sector its own address names (316682e), with every search's counts in Pregap searches: (8726bd3, +platterpus.27 and .28), and since +platterpus.29 the one sector the reads leave undecided prints as such: track 9 is 94 or 95 frames (undecided) in 18 of the 19 .29 logs of 2026-11-04 and 26 of round 40's 29 rip logs, 95 in the rest, and 94 in no log since .29; this drive's raw Q of LSN 145567 fails its CRC, so a raw read on a second drive settles it (our round 39 lap 1 S11; docs/OPEN-ITEMS.md HW-6; the record is docs/KNOWN-ISSUES.md)
STATUS-OPEN: unsent-flag-rows both fixing at round 42, priority 8: docs/seam-commands.md §1b rows each flag of ours your rip path does not send; its last PP cells, for -X, -C and -B, and the move of --prefer-accuraterip-match and --reread-until-accuraterip to §1 are in protocol v10's texts, byte-identical in both trees since your round 41 lap 6 S7; what is left is §2a's ? cells, ours at :260 and :261 and yours at :261 (docs/OPEN-ITEMS.md US-11 and PP-12)
STATUS-OPEN: hardware-unverified us cannot, because each needs a disc or a drive this environment lacks: the list is docs/OPEN-ITEMS.md, Needs a drive, HW-1 to HW-17, which on 2026-11-16 replaced this line's own list, CLAUDE.md's table and KNOWN-ISSUES.md's, which disagreed; among them C2 read by cyanrip itself, the C2 probe at track 3's seconds 240 and 245 and track 1's second 162, track 9's LSN 145567 on a second drive, -O past the lead-out, CD-TEXT from a disc, a recordable disc, -W on a pre-emphasised disc, -P 0's salvage, Speed: with -S, and .32's footer third form and Still waiting: names; asked of your rig in our round 32 lap 1 S21
STATUS-OPEN: upstream-reports-filed us cannot, because what follows is upstream's maintainer's: our operator filed reports 1 to 23 on 2026-10-16 as upstream issue 167, in the order of importance docs/upstream/issues-to-file.md suggests, and reports 24 to 33, drafted from 2026-10-19 to 2026-11-17, go to that issue as one comment of our operator's; two more defects fixed here are read in upstream's code and not yet run there; a reply asking for a pull request or an issue of its own goes to our operator, who files it (docs/OPEN-ITEMS.md OW-8, UP-1, UP-3 and UP-4)
STATUS-OPEN: suite-timeouts-at-default us cannot, because neither settling run reproduces a timeout (the suite serially, and each test under the two heaviest), so no mechanism is known to fix; each occurrence is recorded, and none has been since 2026-09-30 (docs/OPEN-ITEMS.md US-4)

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

## Now — rewritten 2026-11-24: round 42 open on `.35`, your lap 2 filed, our lap 3 next; round 41 closed on `.34`, on stable since

**This section is the whole of what this file claims.** Everything below it is
either guidance on reading the manifest or the rig procedure the suite
checks, and neither is a dated state. **Which build is released, on which
channel, is in `release-manifest.json` and nowhere else**, and what each release
changed is in `Changelog.md`. `tests/rip_images.py`'s `status_now_is_current`
fails when this heading's date is older than the newest ledger row or lap file
of the current round, by committer date in UTC.

### Rounds

- **Round 41 is closed**, 2026-11-18, six laps, on our lap 5 and Platterpus's
  lap 6, both `GO`, approving `.34` at `fb28088` with their 0.7.127. Their lap
  6, released by their operator and filed byte for byte from their `main` at
  `0cb08891`, reads round 41's rip as meeting G1 to G3 by its own reading and
  lands protocol v10 in their tree (G4). Their `FORK_PIN` moved to `fb28088`
  in the commit that released it, `13bf57bc`.
- **`.34` went to stable on 2026-11-23**, as our owner decided on 2026-11-17,
  by the way our owner chose that day: ledger row 48 puts it on stable and row
  49 lists `.35` on beta again, since beta resolves to the newest row of any
  channel and a stable row alone would have moved beta back to `.34`. Nothing
  was rebuilt.
- **Round 42 is open**, on our lap 1 (`docs/handshake/round-42-lap-01.md`),
  sent when its pull request merged, on our owner's words of 2026-11-17 and
  2026-11-23. It reviews `.35` at `1280aa4`, says our gate implements protocol
  v10, and proposes what `.36` would change; it closes on its S32, one default
  whole-disc rip of `.35` through Platterpus's first release naming it, their
  C2 probe, and each side's gate on v10.
- **Their lap 2 accepts all of it**, filed 2026-11-24 from their `main` at `9d9177a2`:
  `.35` under review in their 0.7.129, their gate on protocol 10, every `.36`
  proposal, the close as given, and their readers for `.36`'s new forms in the
  release after 0.7.129 (their S19). Our lap 3, reading it, is next.
- **Round 42's Full run ran** through 0.7.129 on 2026-11-23 and 24, by
  Platterpus's app log; its bundle has not reached us. The C2 probe after it
  stopped before any read, Platterpus being still open, and is still to run.
- **Round 40 is closed**, 2026-11-16, and every earlier round is a row of the
  handshake README's round table; the gate is the authority over both.

### Runs

| | |
|---|---|
| newest | **Your `overreadprobe` with `.34`, Platterpus 0.7.127, the reference disc, 2026-11-17**, from 22:57:58Z: track 14 at +667 and track 1 at -667, each with `-O`, each exit 0 in under 90 s, each `Beyond disc: 2 of 2 frames refused (written as silence)`; pass 23, fail 1, the failure your `expect force_overread off`; filed on our evidence branch at `1a16efe` (`docs/rig-2026-11-17b-overreadprobe/`) |
| before | **`.34` with Platterpus 0.7.127, Full, the reference disc, 2026-11-17**, from 01:14:14Z, round 41's rip, five default whole-disc rips with their securing passes, and the paired rips of track 3, `.32` against `.34`: pass 649, fail 3, unreachable 1; two failures are Platterpus's `expect-ctdb whole` on track 5's read, as in the three runs before it, and the third is the de-emphasis pair, whose `-E` arm misread track 1 in second 162, the same bytes as a 2026-09-28 read; filed on our evidence branch at `e1e6a68` (`docs/rig-2026-11-17-fb28088/`), whose README is our reading: all 37 `.34` records hold the drive's declared read performance, and all 14 tracks are verified in all five rips, track 5 by the labeled repair |
| next | **your C2 probe**, which no run has carried; the reading of 2026-11-17 asks for it at every second the records name: 240, 244, 245, 251 and 252 of track 3, 144 of track 5 and 162 of track 1 |

Every earlier run is a `docs/rig-*` folder with its own README.

### The protocol

**Round 41 closed under v9, and v10 governs from round 42** (`PROTOCOL.md`
§18). The four shared documents, v10's text among them, are byte-identical in
both trees at `platterpus@0cb0889`, read with `tools/seam-sync-check.py
--fetch` on 2026-11-18 at 00:50Z. Our gate implements 10 (`PROTOCOL_VERSION`
in `tools/release-gate.py`, US-40), and still reads round 41's laps, which
declare 9. Theirs implements 9 by their round 41 lap 6 S7 and D7, which says it
implements 10 before their first lap of round 42. Under §18 neither side
declares 10 until both have said in a lap that their gate implements it: round
42's opening lap says it of ours.

### Platterpus's side, read and not run

Their newest release is 0.7.128, tag `v0.7.128` at `0ec72e6b`, tagged
2026-11-18 at 02:35Z. It installs `.34` by default, its `FORK_PIN` being
`fb28088` as their lap 6 S18 said, and still names `.34` as the build under
review, round 42 not being open. Their
newest lap is round 41's lap 6, released 2026-11-18 at `0cb08891` and filed
here in the commit that closes round 41. Their standing status is
`docs/handshake/outbound/platterpusstatus.md` in their tree. Seventeen of their
earlier statuses are filed under `docs/handshake/inbound/status-*.md`, each
dated by the date it declares; theirs are evidence and are never consolidated,
and ours is a claim about now and is rewritten.

### Open items

**Every open item is a row of `docs/OPEN-ITEMS.md`**, the one list, reviewed
before each round's opening lap. The block's `STATUS-OPEN` lines are the
summary Platterpus reads, in the shape their gate checks, and each names its
rows there. `docs/KNOWN-ISSUES.md` keeps the evidence behind our open defects.

### Upstream

Our `master` mirrors upstream at `648b1dd`, 0.9.4-rc3, merged into
`platterpus-fork` at `56da02eb` on 2026-11-03
(`docs/upstream/sync-2026-11-03-ci.md`); `git ls-remote` returned the same
commit on 2026-11-17, and `tools/upstream-delta.py` is how to check again.
**Thirty-three defects this fork found in upstream's code are drafted; the
first twenty-three are filed there, as upstream issue 167**, by our operator
on 2026-10-16, and 24 to 33 wait for our operator to add them as one comment
(`docs/OPEN-ITEMS.md` OW-8). The fork has report 33's defect too, unfixed
until a round agrees the change (US-32). Two more fixed here are read in upstream's code
and not yet run there (UP-3, UP-4).
The issue's existence is our operator's word: this session cannot open
upstream's tracker.

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
