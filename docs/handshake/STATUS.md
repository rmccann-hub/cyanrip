# cyanrip standing status — what the consumer can assume between rounds

STATUS-NEWEST-LAP: round-25-lap-03.md
STATUS-NEWEST-LAP-STATE: held

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

## Now — rewritten 2026-09-23, after our round 25 lap 3

**This section is the whole of what this file claims.** Everything below it is
either the release table a consumer reads or the rig procedure the suite
checks, and neither is a dated state.

### The release

| | |
|---|---|
| **released** | **`0.9.4-rc2+platterpus.14` at `3e01bb3`**, `release_seq` 24, stable, cut 2026-09-22 on round 22's authority |
| build it | `meson setup build -Ddeclare_released=true && ninja -C build` from `https://github.com/rmccann-hub/cyanrip/archive/3e01bb3.tar.gz` — verified from exactly that tarball before publication, reporting `released build` |
| previous | `.13` at `2cce60d`, seq 23, 2026-09-18, round 21 |
| what `.14` changed | `Track %i read successfully!` / `read with errors.` replace the `ripped and encoded` pair, and a three-state `Encoder errors:` line is new. All P2, all agreed in round 22 |
| gate | `--release-gate` exits **1** and names round 25, which is open. That is correct and is not being overridden |
| the tip | **the `.15` candidate, and not a release.** `src/` changed at `2af669e` (the per-frame retry limit, round 25 lap 2 §B1), and `tools/gen-handshake-state.py` at `20a5aca` (the draft qualifier). A build of the tip reports round 25 open and `NOT a released build`. Build from the release, not the tip |
| next | **`+platterpus.15`, candidate `61711f1`**, cut when round 25 closes and not before. It is the first release under the operator's rule that a round ends on releases of both applications: ours first, then Platterpus's. Theirs pins `3e01bb3`, because their `FORK_PIN` must be a closed round's pin, so their users are offered `.15` marked `unapproved` until round 26 reviews it (lap 3 §C). It carries the draft qualifier and the retry-limit fix |

**Stable by the operator's instruction, and round 24 has now reviewed it.**
`.14` went to stable before any round reviewed it, over the beta that
`docs/RELEASE-PLAN-platterpus.14.md` §3 recommended, so Platterpus's app offered
it stamped `unapproved`. Round 24 closed in a day, and their `FORK_PIN` rolled to
`3e01bb3` on their `main` at `platterpus@86f0547`. **Their users get the roll in
0.6.54**, which is not tagged yet; until it ships, 0.6.53 as installed still
approves `2cce60d`. **Round 25 being open now holds 0.6.54 too**, under the
strict-gate policy the operator chose for their `v0.*` line, unless it goes out
under a written override. Our round 25 lap 1 §D says so to them. Their round 25
lap 2 §C says their operator chose to wait.

### The rounds

| | |
|---|---|
| **round 25** | **OPEN** since 2026-09-23. Our laps 1 and 2 are released. **Their lap 2 is released too, `GO`, and crossed ours**: it answers our lap 1 and holds no lap 2 of ours. Our lap 3 answers it. Close conditions: the three texts byte-identical in both trees (lap 1), and **both releases ready and agreed** (lap 2 §0.3, by the operator's override of R1). Pin `3e01bb3`, unchanged; `.15` candidate `61711f1`. Next: their lap 4 |
| round 24 | **CLOSED `GO`/`GO`** 2026-09-23, **three laps**, 13 days before the close-by. One close condition, Platterpus's verdict on `3e01bb3`, met by their lap 2 (`GO`, their 0.6.53 parser reading our golden reference). It closed on their gate at their lap 2 and on ours at our lap 3: the two gates close on different laps, their round-25 item N1. Three laps is the lap-1 `GO`, not v5 |
| round 25, their lap 2 | released, `GO` on the three texts, sha256 `3ae11ad1…`, 15,042 bytes, filed byte-exact as `docs/handshake/inbound/round-25-lap-02.md`, read at `platterpus@5374729`. It lands our lap **1** v6 with one amendment, so it has no R8 or R9 |
| round 23 | CLOSED `GO`/`GO` 2026-09-22 — five laps by the highest `HANDSHAKE-LAP` either side declared, four by Platterpus's own count. Pin `2cce60d`, reviewed for its behaviour on a drive |
| lap counts | rounds 21, 22 and 23 all took five. In 22 and 23 the fifth lap existed only to carry a transcription, which v5 §5b was adopted to remove — and as written cannot, because step 3 needs a peer lap the closing file could not have declared. `CLAUDE.md` has the measure, why rounds 22–24 could not score v5, and round 25's prediction of four laps. **It cannot be met now**: the crossing added a lap, so the fewest is five (our 3, their 4, our 5) |

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

**Their lap 2 crossed ours.** It lands our lap 1 v6 with one amendment, which
says what both gates already do. It has no R8 or R9, and it did not run their
parser over our golden reference or name their release candidate. Lap 3
proposes the one v6 both trees can hold, and asks for those two items.

| text | sha256 | where |
|---|---|---|
| `docs/handshake/proposed/PROTOCOL-v6.md` | **`05abdfde706316f8…`** (lap 3: lap 2's `c47ce7a4…` plus their amendment, and R8 point 1 corrected) | becomes `docs/handshake/PROTOCOL.md` |
| their `docs/handshake-protocol.md` | `522a18ebcb2b9c9a…` (our lap 1 draft plus their amendment) | on their `main` at `5374729` |
| `docs/OWNERSHIP.md` | `6956d0b9908a7784…` | **landed** here at `c07bf68`, identical to theirs |
| `docs/seam-rules.md` | `a0d2139338c6e2b7…` | **landed** here at `c07bf68`, identical to theirs |

**Pre-committed (lap 3 §D, superseding lap 2's):** our lap 5 lands the protocol
as their `main` then carries it, sets our gate to 6, carries the ledger, and
declares `GO`. The exceptions are that their lap 4 changes a conformance row's
expected outcome, refuses a clause, or reports that their parser cannot read
our golden reference. Then we release `.15` at once. **Landing v6 here
means implementing it in our gate in the same change**, as `f748d15` did for v5:
`test_protocol_version_matches_the_shared_spec()` requires it. Our gate fixes
for their D1 and D2 landed first, at `cc235a1` and `12a85fd`. **N4 is decided**:
the operator chose a strict gate for their `v0.*` releases, recorded in our
round 24 lap 3 §F.

### The protocol

| | |
|---|---|
| `PROTOCOL.md` | **v5** here, `d698d58a8130ab52`. **Their `main` holds a v6**, `522a18eb…`, since `5374729`, so `seam-sync-check --fetch` exits **1** on the protocol alone: the other three documents are byte-identical. The v6 both trees can hold is proposed above |
| what v5 added | §5b, the close rule; §5c, Platterpus's readability condition; `HANDSHAKE-PEER-VERDICT-SOURCE`, their field; rows C37–C42 |
| v5's reach | **Both gates implement 5**: ours since round 23, theirs from `platterpus@c2f43d28` (21:30Z 2026-09-22 by commit date; at `52b44282` it was 4). **The two gates read §5b's *"enumerated"* differently**, and under ours step 3 cannot fire on a real record. Measured, and in `docs/KNOWN-ISSUES.md`. The proposed v6 adopts theirs |
| **what v5 is missing** | **K1, K2 and K3**, agreed in rounds 21 and 22 and never written into the spec — found by the pre-round-24 audit. `docs/KNOWN-ISSUES.md` → *Three agreed protocol changes never reached the spec*. All three are in the proposed v6 |

### Platterpus's side, and how we know each part

| | how we know |
|---|---|
| released **0.6.53**, 2026-09-22, at `52b44282`, tag `v0.6.53`, pre-release as every `v0.*` tag is | `git ls-remote --tags` and `--symref` on their repository |
| 0.6.53 is **the both-wordings release** — `_TRACK_START` matches both pairs, and no earlier tag does | read at `52b44282:src/platterpus/parsers/cyanrip_log.py:237-244`; counted across four tags |
| on their `main`, **`FORK_PIN = "3e01bb3"`** and `PIN_UNDER_REVIEW = "3e01bb3"` — the roll, not yet released | read at `86f0547:src/platterpus/deps/fork_source.py:196` and `:568` |
| `APPROVED_BY_ROUND = 24`, `APPROVED_FOR_PLATTERPUS_VERSION = "0.6.53"` | read at `86f0547:src/platterpus/handshake_approval.py:229` and `:141` |
| their `main` is **`5374729`**, untagged; **no `v0.6.54` tag exists**. Their gate implements protocol 5 from `c2f43d28`, and refuses a round in which any file declares more (`scripts/handshake.py:1920`) | `git ls-remote` on their repository, and a fetch |
| their app **offers, never installs**, a newer build from our manifest on the user's channel, and says it will report `unapproved` until a round verifies it | read at `52b44282:src/platterpus/deps/ripper_manifest.py:1-16`, `:66-68`, and `5374729:src/platterpus/config.py:383-393` |
| their `FORK_PIN` must equal the pin of their newest closed round, so it cannot name a release cut after the close | read at `5374729:tests/test_fork_source.py:132-190` |
| their standing status, as of 0.6.53 | filed byte-exact twice, because it was rewritten the same day under the same as-of: `docs/handshake/inbound/status-2026-09-22-v0.6.53.md` (read at `52b44282`, sha256 `2ac99eb5…09ab9`, 39,016 bytes) and `…-2026-09-22-v0.6.53-c2f43d28.md` (read at `c2f43d28`, sha256 `ddfcbbe6…62ac0`, 43,166 bytes) |
| their branch-delete cause was a repository setting, now off | **relayed**, and corroborated rather than proven: the cited commits are reachable again as ancestors of `claude/session-omka9f` at `9cc23eab` |

### What is still open

The list is `docs/KNOWN-ISSUES.md` and it is not repeated here. The headline
items:

- **K1–K3 are missing from the spec** (proposed in v6).
- `File(s):` is still built from the request.
- The loudness block is measured upstream of the filter graph.
- The cache figure is wrong on all ten filed sessions.
- There is no way in our format to mark a superseded or abandoned read.
- **At `-P 0`, one unreadable sector still hangs the rip**, at any `-r`.
  Platterpus never passes `-P`.

Round 23's `Handshake:` qualifier is now built (`20a5aca`), and the `-r` hang
at the default level is fixed (`2af669e`). Both ship in `.15`.
**The four shared documents carry thirteen known defects**, tabled in one place
under *"The four shared documents: every known defect"*. None can be fixed
from one side. Round 25 lap 1 proposes the fixes for three of the four
documents as one bump; `seam-commands.md` waits for round 26, because its fix
needs `tools/probe-argv-surface.py` to measure what it asserts.

### Where their statuses are filed

Eight, each dated by the date **it declares**, not the day we received it:
`docs/handshake/inbound/status-2026-08-21-v0.6.21.md`, `…-2026-08-21-v0.6.23.md`,
`…-2026-08-24-v0.6.23.md`, `…-2026-09-21-v0.6.52.md`, `…-2026-09-22-v0.6.53.md`,
`…-2026-09-22-v0.6.53-c2f43d28.md`, `…-2026-09-23-v0.6.53.md` and
`…-2026-09-23-v0.6.53-53747294.md`. Each later file of a pair that declares the
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
| **stable version** | `0.9.4-rc2+platterpus.14` |
| **stable commit** | **`3e01bb3`** |
| stable build tag | `platterpus-fork-g3e01bb3` |
| stable install | `https://github.com/rmccann-hub/cyanrip/archive/3e01bb3.tar.gz` |
| stable `release_seq` | 24 |
| stable authorised by | handshake round 22, closed `GO`/`GO` on `2cce60d` / `417d61b` (Platterpus 0.6.51), five laps — the pins round 22 lap 5 declares |
| | |
| **beta version** | `0.9.4-rc2+platterpus.14` |
| **beta commit** | **`3e01bb3`** |
| beta build tag | `platterpus-fork-g3e01bb3` |
| beta install | `https://github.com/rmccann-hub/cyanrip/archive/3e01bb3.tar.gz` |
| beta `release_seq` | 24 |
| beta authorised by | handshake round 22, closed `GO`/`GO` — same build as stable |

`beta` resolves to the newest row of *any* channel, so opting into pre-releases
can never move a user backwards. Both channels resolve to `3e01bb3`; there is no
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
