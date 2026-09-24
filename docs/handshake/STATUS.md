# cyanrip standing status — what the consumer can assume between rounds

STATUS-NEWEST-LAP: round-26-lap-06.md
STATUS-NEWEST-LAP-STATE: sent

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

## Now — rewritten 2026-09-24, after `+platterpus.16`

**This section is the whole of what this file claims.** Everything below it is
either the release table a consumer reads or the rig procedure the suite
checks, and neither is a dated state.

### The release

| | |
|---|---|
| **released** | **`0.9.4-rc2+platterpus.16` at `221a1df`**, `release_seq` 26, stable, cut 2026-09-24 on round 26's authority |
| build it | `meson setup build -Ddeclare_released=true && ninja -C build` from `https://github.com/rmccann-hub/cyanrip/archive/221a1df.tar.gz` — verified from a `git archive` of exactly that commit before publication, reporting `released build` |
| previous | `.15` at `df91ae7`, seq 25, 2026-09-23, round 25; `.14` at `3e01bb3`, seq 24 |
| what `.16` changed | two fixes from round 26's real test: an interrupted track is left out of the AccurateRip tally, so an interrupted rip no longer prints `Tracks ripped partially accurately: 1/14` above `0 of 14 tracks`; and `media` is tagged `CD` whatever `-H` says. No line's text changes. `docs/RELEASE-PLAN-platterpus.16.md` |
| gate | `--release-gate` exits **0**: every round is closed, round 26 at our lap 6 on 2026-09-24 |
| the tip | **the release's publish commit and after.** Build from the release commit, not the tip |
| next | **round 27**, opened on `.16` before its real test, as round 26 was, because Platterpus's acceptance run expects the newest pin we send. Then **Platterpus 0.6.56**, pinning `df91ae7`, and the real test on `.16` with 0.6.56 |

**`.16` is stable because round 26 authorised it, and the build itself is
round 27's to review.** Platterpus's `FORK_PIN` is `df91ae7` in their 0.6.56, so
their app offers `.16` marked `unapproved` until round 27 closes on it. That is
v6 R8 point 2's mark: their offer states it, and a person decides.

### The rounds

| | |
|---|---|
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
| `PROTOCOL.md` | **v6**, `05abdfde706316f8`, byte-identical in both trees. `seam-sync-check --fetch` exits **0**, read at `platterpus@53b3c04` |
| what v5 added | §5b, the close rule; §5c, Platterpus's readability condition; `HANDSHAKE-PEER-VERDICT-SOURCE`, their field; rows C37–C42 |
| the gates | **ours implements 6** from `643631b`, **theirs 5**, with 6 next (their lap 4). For a file declaring 5, ours still reads §5b's *"enumerated"* literally and theirs at decision time; v6 adopts theirs, and applies to files declaring 6. `docs/KNOWN-ISSUES.md` keeps it open until a round closes under step 3 |
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
**upstream has not moved since**: `git ls-remote` on 2026-09-22 returned
`f8ebf48` for both `cyanreg/cyanrip` and our `origin`. Its analysis is
`docs/upstream/sync-2026-08-24-mb-retry.md`. That is a reading of one moment;
`tools/upstream-delta.py` is how to check again. **Nine defects of ours
exist upstream and none is filed there** — each re-checked by
`tools/check-settled.py` against `master`, listed in `CLAUDE.md`.

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

### The hardware procedure, pinned, and contained to one directory

**Round 18 decides what the release test IS.** This is the procedure that exists
today — round 16's Run A, which settled that round's three clauses — kept here
because it is the only pinned rig block either project has and round 18 will
start from it rather than from nothing.

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

| field | value |
|---|---|
| **stable version** | `0.9.4-rc2+platterpus.16` |
| **stable commit** | **`221a1df`** |
| stable build tag | `platterpus-fork-g221a1df` |
| stable install | `https://github.com/rmccann-hub/cyanrip/archive/221a1df.tar.gz` |
| stable `release_seq` | 26 |
| stable authorised by | handshake round 26, closed `GO`/`GO` on `df91ae7` / `629ffa2` (Platterpus 0.6.55), six laps — the pins round 26 lap 6 declares |
| | |
| **beta version** | `0.9.4-rc2+platterpus.16` |
| **beta commit** | **`221a1df`** |
| beta build tag | `platterpus-fork-g221a1df` |
| beta install | `https://github.com/rmccann-hub/cyanrip/archive/221a1df.tar.gz` |
| beta `release_seq` | 26 |
| beta authorised by | handshake round 26, closed `GO`/`GO` — same build as stable |

`beta` resolves to the newest row of *any* channel, so opting into pre-releases
can never move a user backwards. Both channels resolve to `221a1df`; there is no
separate beta to take.

**`+platterpus.8` (`796df32`, seq 18) is superseded and should not be installed.**
It is still in the ledger, because the ledger is append-only and a published build
is a fact, but no channel resolves to it any more.

Build command: `meson setup build -Ddeclare_released=true && ninja -C build`.

`release-manifest.json` is the only mechanism to install from and it is what
resolves these; this table is a human-readable copy of it and the test exists
because a copy rots.

**No release while any round is open.** `tools/release-gate.py --release-gate`
names the open round; the *Now* section above says which it is. The previous
text of this paragraph named round 16 for five weeks after that round closed,
which is why it no longer names one.
