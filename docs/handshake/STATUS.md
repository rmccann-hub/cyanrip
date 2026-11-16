# cyanrip standing status — what the consumer can assume between rounds

STATUS-NEWEST-LAP: round-41-lap-01.md
STATUS-NEWEST-LAP-STATE: sent

STATUS-ROUND: 41, OPEN, on our lap 1 and your lap 2, both OPEN; it reviews +platterpus.33 at 13bec0a with your 0.7.126, and your next release names it under review (your lap 2 S18); it closes on our lap 1 S28, which your lap 2 S17 accepts as given; protocol v10 is accepted (your S15), its texts ours to write
STATUS-LAPS: newest sent round-41-lap-01.md (ours), round-41-lap-02.md (theirs); next 3 (ours) carrying our reading of your lap 2 and the texts of protocol v10 your S15 accepts; held none
STATUS-RELEASED: +platterpus.34 at fb28088, 2026-11-16
STATUS-RELEASE-NEXT: +platterpus.35, not built: Disc MCN: printed always and the Ripping errors: parts named, in our first build after your release that reads both (your round 41 lap 2 S9 and S10), and what round 41's questions decide; +platterpus.34 is on the beta channel from 2026-11-16, which our round 41 lap 3 asks to make the round's pin in place of +platterpus.33, and +platterpus.32 on stable; pins edb73dd, reviews +platterpus.34
STATUS-RUN-NEXT: +platterpus.34 with your-first-release-naming-it; waiting on your lap 4's answer to our round 41 lap 3 S9, which keeps +platterpus.33 as your lap 2 S17 restates if you decline, and your release naming the pin, then our owner's rip of round 41 on the reference disc, with -O in one rip and second 245 in the C2 probe (your lap 2 S11, S12); round 40's rip is filed on our evidence branch at 589db53 (docs/rig-2026-11-14-edb73dd/)
STATUS-OPEN: track1-pregap-base us fixing at a64d58d, priority 3: track 1's Pregap length: counted from LBA 0, proposed in our round 32 lap 1 S13 and accepted in your lap 2 S10, released in +platterpus.23 at 891c79e; the reference disc's track 1 starts at LSN 0, so no run of it can tell the two counts apart, and a disc with a pregap before track 1 is what settles it (docs/OPEN-ITEMS.md HW-11)
STATUS-OPEN: overread-bounded us fixing at bfe71ec, priority 1: under -O a frame outside the disc is read once, a refused one written as silence, and a track that read any says Beyond disc: N of M frames refused (written as silence); released in +platterpus.24 at 93afa15, and open until a drive shows what it does with a read past its lead-out: no run through round 40 sent -O, and no log has printed Beyond disc: (docs/OPEN-ITEMS.md R41-9 and HW-10)
STATUS-OPEN: subchannel-pregap-varies us fixing at 8726bd3, priority 5: a pregap the TOC does not signal read differently between rips of one disc while the log stated one value; fixed by placing each Q frame at the sector its own address names (316682e), with every search's counts in Pregap searches: (8726bd3, +platterpus.27 and .28), and since +platterpus.29 the one sector the reads leave undecided prints as such: track 9 is 94 or 95 frames (undecided) in 18 of the 19 .29 logs of 2026-11-04 and 26 of round 40's 29 rip logs, 95 in the rest, and 94 in no log since .29; this drive's raw Q of LSN 145567 fails its CRC, so a raw read on a second drive settles it (our round 39 lap 1 S11; docs/OPEN-ITEMS.md HW-6; the record is docs/KNOWN-ISSUES.md)
STATUS-OPEN: unsent-flag-rows them fixing at round 41, priority 8: docs/seam-commands.md §1b rows each flag of ours your rip path does not send, and every cell has landed except the PP cells for -X, -C and -B, still ?, which are yours; --prefer-accuraterip-match and --reread-until-accuraterip, which your rip path sends, move to §1 in the shared-documents version proposed for round 41 (docs/OPEN-ITEMS.md R41-5 and PP-12)
STATUS-OPEN: hardware-unverified us cannot, because each needs a disc or a drive this environment lacks: the list is docs/OPEN-ITEMS.md, Needs a drive, HW-1 to HW-17, which on 2026-11-16 replaced this line's own list, CLAUDE.md's table and KNOWN-ISSUES.md's, which disagreed; among them C2 read by cyanrip itself, the C2 probe at track 3's second 245, track 9's LSN 145567 on a second drive, -O past the lead-out, CD-TEXT from a disc, a recordable disc, -W on a pre-emphasised disc, -P 0's salvage, Speed: with -S, and .32's footer third form and Still waiting: names; asked of your rig in our round 32 lap 1 S21
STATUS-OPEN: upstream-reports-filed us cannot, because what follows is upstream's maintainer's: our operator filed reports 1 to 23 on 2026-10-16 as upstream issue 167, in the order of importance docs/upstream/issues-to-file.md suggests, and reports 24 to 32, drafted from 2026-10-19 to 2026-11-16, go to that issue as one comment of our operator's; two more defects fixed here are read in upstream's code and not yet run there; a reply asking for a pull request or an issue of its own goes to our operator, who files it (docs/OPEN-ITEMS.md OW-8, UP-1, UP-3 and UP-4)
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

## Now — rewritten 2026-11-16: round 41 open on `.33`; `.32` on stable

**This section is the whole of what this file claims.** Everything below it is
either guidance on reading the manifest or the rig procedure the suite
checks, and neither is a dated state. **Which build is released, on which
channel, is in `release-manifest.json` and nowhere else**, and what each release
changed is in `Changelog.md`.

### Rounds

- **Round 40 is closed**, 2026-11-16, four laps, on our lap 3 and Platterpus's
  lap 4, both `GO`, approving `.32` at `edb73dd` with their 0.7.125. Their
  `FORK_PIN` moved to `edb73dd` on the close (`platterpus@90b822fa`), and
  their 0.7.126 of 2026-11-16 installs it by default (`platterpus@3e2f194a`).
- **`.33` is on the beta channel** at `13bec0a`, from 2026-11-16, ledger row
  45. **`.32` is on stable** at `edb73dd`, from 2026-11-16, on our owner's
  word that day to take every recommendation put to them; ledger rows 43 and
  44 name the same commit, so nothing was rebuilt. Stable had been `.23` since
  2026-10-16.
- **Round 41 is open**, on our lap 1 of 2026-11-16, reviewing `.33` at
  `13bec0a` with their 0.7.126 and proposing protocol v10. It closes on its
  S28: a rip of `.33` reading the drive's declared read performance, all 14
  tracks verified, the bundle filed, and v10 landed in both trees.
- **Every earlier round** is a row of the handshake README's round table, and
  the gate is the authority over both.

### Runs

| | |
|---|---|
| newest | **`.32` with Platterpus 0.7.125, Full, the reference disc, 2026-11-14**, from 02:12:01Z, round 40's rip, five default whole-disc rips with their securing passes, and the paired rips of track 3, `.31` against `.32`: pass 650, fail 2, unreachable 1; both failures are Platterpus's `expect-ctdb whole` on track 5's read, as in the two runs before it; filed on our evidence branch at `589db53` (`docs/rig-2026-11-14-edb73dd/`), whose README is our reading: every `.32` log prints the new `C2 errors:` line, and all 14 tracks are verified in all five rips |
| before | **`.31` with Platterpus 0.7.122, Full, the reference disc, 2026-11-11**, from 12:34:47Z, round 39's five-rip run: pass 651, fail 1, unreachable 1; filed on our evidence branch at `f6b9188` (`docs/rig-2026-11-11-e531a33/`), and its C2 probe at `74b6f0a` (`docs/rig-2026-11-11b-c2probe/`) |
| next | **what round 41 agrees**; the reading of 2026-11-14 asks for the C2 probe at every second the records name in tracks 3 and 5, 144, 244, 245, 251 and 252 |

Every earlier run is a `docs/rig-*` folder with its own README.

### The protocol

`PROTOCOL.md` v9, which is v8 plus HR-2 and HR-2.1 (§17), governs. **Both
gates implement 9.** The four shared documents are byte-identical in both trees
at `platterpus@34d2033`, read with `tools/seam-sync-check.py --fetch` on
2026-11-16. What both sides accepted and neither has shipped in them, and the
stale text found since, is one proposed version: `docs/OPEN-ITEMS.md` R41-5.

### Platterpus's side, read and not run

Their newest release is 0.7.125, tag `v0.7.125` at `553a2d8c`, published
2026-11-14. Their newest lap is round 40's lap 4, at `platterpus@34d20333`, and
their standing status is `docs/handshake/outbound/platterpusstatus.md` in their
tree. Seventeen of their earlier statuses are filed under
`docs/handshake/inbound/status-*.md`, each dated by the date it declares; theirs
are evidence and are never consolidated, and ours is a claim about now and is
rewritten.

### Open items

**Every open item is a row of `docs/OPEN-ITEMS.md`**, the one list, reviewed
before each round's opening lap. The block's `STATUS-OPEN` lines are the
summary Platterpus reads, in the shape their gate checks, and each names its
rows there. `docs/KNOWN-ISSUES.md` keeps the evidence behind our open defects.

### Upstream

Our `master` mirrors upstream at `648b1dd`, 0.9.4-rc3, merged into
`platterpus-fork` at `56da02eb` on 2026-11-03
(`docs/upstream/sync-2026-11-03-ci.md`); `git ls-remote` returned the same
commit on 2026-11-16, and `tools/upstream-delta.py` is how to check again.
**Thirty-two defects this fork found in upstream's code are drafted; the
first twenty-three are filed there, as upstream issue 167**, by our operator
on 2026-10-16, and 24 to 32 wait for our operator to add them as one comment
(`docs/OPEN-ITEMS.md` OW-8). Two more fixed here are read in upstream's code
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
