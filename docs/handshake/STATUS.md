# cyanrip standing status — what the consumer can assume between rounds

STATUS-NEWEST-LAP: round-43-lap-03.md
STATUS-NEWEST-LAP-STATE: sent

STATUS-ROUND: 43, OPEN, on our lap 3 and your lap 2, both OPEN; it reviews +platterpus.35 at 1280aa4 with your 0.7.130, which names it under review, our owner's two Full runs on that pair of 2026-11-25 and 26 being its run; your lap 2 accepts every +platterpus.36 wording and our lap 1 S62 as given, and reads G1, G2 and G5 as met; G3 waits on your 0.7.131 and G4 on S18's shared version landing in both trees with +platterpus.36's build, which we publish after your 0.7.131, for round 44 to review; round 42 closed GO/GO on 2026-11-25
STATUS-LAPS: newest sent round-43-lap-03.md (ours), round-43-lap-02.md (theirs); next 4 (theirs) carrying your reading of our lap 3 S5's version against its hashes, and your 0.7.131 once published; you write it, and only you do; held none
STATUS-RELEASED: +platterpus.35 at 1280aa4, 2026-11-17
STATUS-RELEASE-NEXT: +platterpus.36, not built: everything our round 43 lap 1 S5 to S18 names, in one build, published only after your release that reads its new wordings in both forms; +platterpus.35, the pin round 42 approved, is on beta from 2026-11-17 and on stable from 2026-11-25; pins 1280aa4, reviews +platterpus.35
STATUS-RUN-NEXT: +platterpus.36 with your-next-release; waiting on .36's build and your release that reads its new wordings (round 43's G3); round 43's two Full runs of +platterpus.35 are filed at 6451c5c and ebedeac, and our owner's checks of 2026-11-26 at 1d7f47e (docs/rig-2026-11-26b-drivecheck/): -I -N alone took 18.7 s, and the door lock setting reads 1
STATUS-OPEN: track1-pregap-base us fixing at a64d58d, priority 3: track 1's Pregap length: counted from LBA 0, proposed in our round 32 lap 1 S13 and accepted in your lap 2 S10, released in +platterpus.23 at 891c79e; the reference disc's track 1 starts at LSN 0, so no run of it can tell the two counts apart, and a disc with a pregap before track 1 is what settles it (docs/OPEN-ITEMS.md HW-11)
STATUS-OPEN: overread-bounded us fixing at bfe71ec, priority 1: under -O a frame outside the disc is read once, a refused one written as silence, and a track that read any says Beyond disc: N of M frames refused (written as silence); released in +platterpus.24 at 93afa15; on 2026-11-17 your overreadprobe ran it under +platterpus.34 on the BDR-209D, which refused 2 of 2 frames past the lead-out and 2 of 2 before LSN 0, each read once and written as silence in about a minute (docs/rig-2026-11-17b-overreadprobe/), so it stays open only for a drive that answers past its lead-out (docs/OPEN-ITEMS.md HW-10)
STATUS-OPEN: subchannel-pregap-varies us fixing at 8726bd3, priority 5: a pregap the TOC does not signal read differently between rips of one disc while the log stated one value; fixed by placing each Q frame at the sector its own address names (316682e), with every search's counts in Pregap searches: (8726bd3, +platterpus.27 and .28), and since +platterpus.29 the one sector the reads leave undecided prints as such: track 9 is 94 or 95 frames (undecided) in 18 of the 19 .29 logs of 2026-11-04 and 26 of round 40's 29 rip logs, 95 in the rest, and 94 in no log since .29; this drive's raw Q of LSN 145567 fails its CRC, so a raw read on a second drive settles it (our round 39 lap 1 S11; docs/OPEN-ITEMS.md HW-6; the record is docs/KNOWN-ISSUES.md)
STATUS-OPEN: unsent-flag-rows both fixing at round 42, priority 8: docs/seam-commands.md §1b rows each flag of ours your rip path does not send; its last PP cells, for -X, -C and -B, and the move of --prefer-accuraterip-match and --reread-until-accuraterip to §1 are in protocol v10's texts, byte-identical in both trees since your round 41 lap 6 S7; what is left is §2a's ? cells, ours at :260 and :261 and yours at :261 (docs/OPEN-ITEMS.md US-11 and PP-12)
STATUS-OPEN: hardware-unverified us cannot, because each needs a disc or a drive this environment lacks: the list is docs/OPEN-ITEMS.md, Needs a drive, HW-1 to HW-21, which on 2026-11-16 replaced this line's own list, CLAUDE.md's table and KNOWN-ISSUES.md's, which disagreed; among them C2 read by cyanrip itself, track 9's LSN 145567 on a second drive, -O past the lead-out, CD-TEXT from a disc, a recordable disc, -W on a pre-emphasised disc, -P 0's salvage, Speed: with -S, and .32's and .34's Still waiting: names; asked of your rig in our round 32 lap 1 S21
STATUS-OPEN: upstream-reports-filed us cannot, because what follows is upstream's maintainer's: our operator filed reports 1 to 23 on 2026-10-16 as upstream issue 167, in the order of importance docs/upstream/issues-to-file.md suggests, and reports 24 to 35, drafted from 2026-10-19 to 2026-11-26, go to that issue as one comment of our operator's; three more defects found here and in upstream's code are not yet drafted; a reply asking for a pull request or an issue of its own goes to our operator, who files it (docs/OPEN-ITEMS.md OW-8, UP-5, UP-6 and UP-7)
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

## Now — rewritten 2026-11-26: round 42 closed `GO`/`GO` on `.35`, on stable since; round 43 on our lap 3, sent

**This section is the whole of what this file claims.** Everything below it is
either guidance on reading the manifest or the rig procedure the suite
checks, and neither is a dated state. **Which build is released, on which
channel, is in `release-manifest.json` and nowhere else**, and what each release
changed is in `Changelog.md`. `tests/rip_images.py`'s `status_now_is_current`
fails when this heading's date is older than the newest ledger row or lap file
of the current round, by committer date in UTC.

### Rounds

- **Round 42 is closed**, 2026-11-25, six laps, on our lap 5 and Platterpus's
  lap 6, both `GO`, approving `.35` at `1280aa4` with their 0.7.129. Their lap
  6, released by their operator and filed byte for byte from their `main` at
  `b628344e`, reads our G3 filing on our evidence branch (`c55c217`), finds G1
  to G4 met and no defect in `.35` that makes the pin unsafe. Their `FORK_PIN`
  moved to `1280aa4` in the commit that released it, `79ad1496`, and their
  0.7.130, tagged 2026-11-25, installs `.35` by default.
- **What round 42 found.** Each Full run's section F rip verifies 13 tracks
  from the read and track 5 by their labeled CTDB repair, as round 41's did,
  and the second run's repeat rip 4 verifies all 14 from `.35`'s own reads.
  `Disc MCN:` reads `none (libcdio returned none)` in all 56 `.35` logs. Their
  C2 probe finds C2 bits at track 5's LBA 83430 in 5 of 6 reads, which `C2
  errors:` does not measure (HW-1). Two defects are theirs, accepted for their
  next release: their app pruned the bundle a run told our owner to send
  (R42-1, their R200), and their in-app bundle carries no album folder (R42-2,
  their R197).
- **`.35` went to stable on 2026-11-25**, on our owner's word that day, *"yes
  move stable to .35"*. Ledger row 50 puts it on stable under round 42, and beta
  resolves to the same row, so beta stays on `.35`. Nothing was rebuilt.
  Stable had been `.34` since 2026-11-23.
- **Round 43's opening lap is sent**
  (`docs/handshake/round-43-lap-01.md`), released by our owner's word of
  2026-11-26, *"Do all recommended. Fold all into this round and release when
  ready"*, once our owner's drive checks of that day were read into it. It reviews `.35` with their 0.7.130,
  our owner's Full run on that pair being its run, and agrees everything `.36`
  will carry. We build `.36` during the round and publish it only after their
  release that reads its new wordings, so round 44 reviews it: our owner's
  schedule of 2026-11-25. The lap answers each of their audit's seventeen asks,
  sweeps our list from 82 rows to 72, and asks them to sweep theirs.
- **Their lap 2 accepts it all, and our lap 3 answers.** Their lap 2
  (`docs/handshake/inbound/round-43-lap-02.md`) accepts every `.36` wording,
  S4's order and S62 as given, and reads G1, G2 and G5 as met. Our lap 3
  (`docs/handshake/round-43-lap-03.md`) confirms the wordings, adds US-54 and
  US-55 for `.36`, and sends S18's version: `PROTOCOL.md` v11 and
  `seam-rules.md` v10 final by hash, and `seam-commands.md`, whose hash
  follows `.36`'s build. G3 waits on their 0.7.131, and G4 on that version
  landing in both trees.
- **Round 43's runs are filed and read in that lap**, before it was sent:
  our owner's two Full runs of `.35` through 0.7.130, on 2026-11-25 and 26
  (`docs/rig-2026-11-25-1280aa4/`, `docs/rig-2026-11-26-1280aa4/`, evidence
  `6451c5c` and `ebedeac`). Neither passed: in each, all eight failures are
  Platterpus's album audit failing a `.35` binary their production target built
  without our release declaration (R43-13). Nothing in either is a defect in
  `.35`.
- **Round 41 is closed**, 2026-11-18, approving `.34` at `fb28088`, and it and
  every earlier round is a row of the handshake README's round table; the gate
  is the authority over all of them.

### Runs

| | |
|---|---|
| newest | **`.35` with Platterpus 0.7.130, Full, the reference disc, a second time, 2026-11-26 from 00:58:46Z**, 17 rips: the first run's verdict step for step, pass 531, fail 8, unreachable 128, every failure your `expect-album-audit` on `-- NOT a released build` (R43-13). All 17 logs verify and end `Ripping errors: 0`. Track 3 differs: no read of 158, 112 of them your re-reads of it alone, is matched by AccurateRip v1 or v2, so your CTDB repair rewrote it in all seven whole-disc rips; `--reread-until-accuraterip` kept track 5's `C96464AB` in all 7 of its loops. Filed at `ebedeac` (`docs/rig-2026-11-26-1280aa4/`) |
| first of round 43 | **`.35` with Platterpus 0.7.130, Full, the reference disc, 2026-11-25 from 20:24:17Z**, round 43's run, 17 rips: pass 531, fail 8, unreachable 128, so it did not pass. Every failure is your `expect-album-audit` on `-- NOT a released build`: the binary on the rig was built without `-Ddeclare_released=true`, which your production target withholds (R43-13), where round 42's 42 `.35` logs say `released build`. 127 of the 128 unreachable steps are the A/B sections, skipped because your pin and build under review are both `1280aa4`, and the 128th is the offset refusal this drive cannot reach. All 17 logs verify and end `Ripping errors: 0` and `Read stalls:    none`; section F verifies 13 tracks from reads and track 3 by your labeled CTDB repair; repeat rips 2 and 3 verify all 14 from the drive's reads; `--reread-until-accuraterip` kept `C96464AB` for track 5 in 5 of 8 repeat loops; track 9's pregap is undecided in 4 of 24 `Gaps:` lists. Filed on our evidence branch at `6451c5c` (`docs/rig-2026-11-25-1280aa4/`) |
| before | **`.35` with Platterpus 0.7.129, Full, the reference disc, twice: 2026-11-23 from 23:49:48Z and 2026-11-24 from 09:38:25Z**, round 42's runs, each with 29 rips; the first pass 647, fail 2, unreachable 1, and the second pass 650, fail 1, unreachable 1, every failure your `expect-ctdb whole` on track 5's minority CTDB match. All 68 logs verify and end `Ripping errors: 0`; all 56 `.35` logs print `Disc MCN:       none (libcdio returned none)`. Each run's section F rip verifies 13 tracks from the read and track 5 by your labeled CTDB repair, as round 41's did, and the second run's repeat rip 4 verifies all 14 from the drive's reads, its securing pass keeping `C96464AB` for track 5 over three reads of `E0036697`. Filed on our evidence branch at `fa045e5` (`docs/rig-2026-11-23-1280aa4/`, from the session and rip folders, the bundle being pruned) and `c55c217` (`docs/rig-2026-11-24-1280aa4/`, from the bundle and rip folders) |
| next | **`.36`'s acceptance run, for round 44**; round 43's G1 is answered by these runs, and our owner's checks of 2026-11-26 are filed at `1d7f47e` (`docs/rig-2026-11-26b-drivecheck/`) |

Every earlier run is a `docs/rig-*` folder with its own README.

### The protocol

**Round 42 ran under v10**, both gates implementing it (our lap 3 S3, their
lap 4 S3). The four shared documents are byte-identical in both trees at
`platterpus@b628344`, read with `tools/seam-sync-check.py --fetch` on
2026-11-25 at 15:38Z. Our gate implements 10 (`PROTOCOL_VERSION` in
`tools/release-gate.py`, US-40) and still reads earlier rounds' laps, which
declare 9 or less.

### Platterpus's side, read and not run

Their newest release is 0.7.130, tag `v0.7.130` at `d15c0fff`, tagged
2026-11-25 at 16:42Z. It installs `.35` by default, its `FORK_PIN` being
`1280aa4` since round 42's close (`79ad1496`), and still names `.35` as the
build under review, round 43 not being open. Their 0.7.129 installs `.34`.
Their newest lap is round 42's lap 6, released 2026-11-25 and on their
`main` from `b628344e`, filed here in the commit that closes round 42. Their standing status is
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
**Thirty-five defects this fork found in upstream's code are drafted; the
first twenty-three are filed there, as upstream issue 167**, by our operator
on 2026-10-16, and 24 to 35 wait for our operator to add them as one comment
(`docs/OPEN-ITEMS.md` OW-8). The fork has report 33's defect too, unfixed
until a round agrees the change (US-32), and part of report 34's (US-54).
Three more found here and in upstream's code are not yet drafted (UP-5 to
UP-7).
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
