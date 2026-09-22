# cyanrip standing status — what the consumer can assume between rounds

STATUS-NEWEST-LAP: round-23-lap-05.md
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

## Now — rewritten 2026-09-22, after `+platterpus.14` shipped and before round 24 opens

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
| gate | `--release-gate` exits **0** — no round is open |
| the tip | ahead of `3e01bb3` by commits that change nothing the build compiles in — the ledger, the manifest, documentation and a tool. `git log 3e01bb3..platterpus-fork -- src/ meson.build 'docs/handshake/round-*.md'` is empty, and the round files are in that list because the `Handshake:` line is compiled from them. The tip's banner still names a different commit, so build from the release, not the tip |
| next | `+platterpus.15`, not planned. It should carry round 23's agreed `Handshake:` qualifier, which was never built |

**Stable by the operator's instruction, and the cost is on Platterpus's side.**
Their app reads our manifest from this branch's tip and offers `.14` on its
default channel stamped `unapproved`, because their `FORK_PIN` still names
`2cce60d` and moves only once a round reviews `.14`. That was weighed against a
beta in `docs/RELEASE-PLAN-platterpus.14.md` §3 and chosen knowingly, on the
judgement that round 24 will be short. **Round 24's opening lap says so.**

### The rounds

| | |
|---|---|
| round 23 | **CLOSED `GO`/`GO`** 2026-09-22 — five laps by the highest `HANDSHAKE-LAP` either side declared, four by Platterpus's own count. Pin `2cce60d`, reviewed for its behaviour on a drive |
| round 22 | CLOSED `GO`/`GO` 2026-09-21, five laps. Authorised `.14` |
| round 24 | **not open**, and ours to open — the provider opens (§1a). Its lap 1 must say `.14` went stable by the operator's instruction |
| lap counts | rounds 21, 22 and 23 all took five. In 22 and 23 the fifth lap existed only to carry a transcription, which is what v5 §5b removes. **Round 24 is v5's first possible test**, and only if their gate implements 5 by then; `CLAUDE.md` sets the prediction, the measure and that condition |

### The protocol

| | |
|---|---|
| `PROTOCOL.md` | **v5**, byte-identical in both trees, `d698d58a8130ab52`; `seam-sync-check --fetch` exits 0 at `platterpus@52b4428` |
| what v5 added | §5b, the close rule; §5c, Platterpus's readability condition; `HANDSHAKE-PEER-VERDICT-SOURCE`, their field; rows C37–C42 |
| v5's reach | **none yet.** Our gate implements it, keyed on the FILE's declared version, and no lap has declared 5. Theirs implements 4 (`platterpus@52b44282:scripts/handshake.py:1093`); their round-23 lap 4 §C says *"implementation follows"*, and a bootstrap reason their suite requires keeps the lag visible (`tests/test_handshake_tooling.py:1415`). **A v4 gate refuses a file declaring 5**, so round 24 can test v5 only once their gate reaches 5, and its lap 1 declares whatever both gates accept |
| **what v5 is missing** | **K1, K2 and K3**, agreed in round 22 and never written into the spec — found by the pre-round-24 audit. `docs/KNOWN-ISSUES.md` → *Three agreed protocol changes never reached the spec* |

### Platterpus's side, and how we know each part

| | how we know |
|---|---|
| released **0.6.53**, 2026-09-22, at `52b44282`, tag `v0.6.53`, pre-release as every `v0.*` tag is | `git ls-remote --tags` and `--symref` on their repository |
| 0.6.53 is **the both-wordings release** — `_TRACK_START` matches both pairs, and no earlier tag does | read at `52b44282:src/platterpus/parsers/cyanrip_log.py:237-244`; counted across four tags |
| `FORK_PIN = "2cce60d"`, `PIN_UNDER_REVIEW = "2cce60d"` | read at `52b44282:src/platterpus/deps/fork_source.py:183` and `:538` |
| `APPROVED_BY_ROUND = 23`, `APPROVED_FOR_PLATTERPUS_VERSION = "0.6.52"` | read at `52b44282:src/platterpus/handshake_approval.py:216` and `:132` |
| their app **offers, never installs**, a newer build from our manifest on the user's channel | read at `52b44282:src/platterpus/deps/ripper_manifest.py:1-16`, `:66-68` |
| their standing status, as of 0.6.53 | filed byte-exact at `docs/handshake/inbound/status-2026-09-22-v0.6.53.md`, sha256 `2ac99eb5…09ab9`, 39,016 bytes |
| their branch-delete cause was a repository setting, now off | **relayed**, and corroborated rather than proven: the cited commits are reachable again as ancestors of `claude/session-omka9f` at `9cc23eab` |

### What is still open

The list is `docs/KNOWN-ISSUES.md` and it is not repeated here. The headline
items: **K1–K3 missing from the spec**; round 23's `Handshake:` qualifier
**agreed and not built**; `File(s):` still built from the request; the loudness
block measured upstream of the filter graph; the cache figure wrong on all ten
filed sessions; and no way in our format to mark a superseded or abandoned read.
**The four shared documents carry twelve known defects**, tabled in one place
under *"The four shared documents: every known defect"*. None can be fixed
from one side, so round 24 proposes them as one bump.

### Where their statuses are filed

Five, each dated by the date **it declares**, not the day we received it:
`docs/handshake/inbound/status-2026-08-21-v0.6.21.md`, `…-2026-08-21-v0.6.23.md`,
`…-2026-08-24-v0.6.23.md`, `…-2026-09-21-v0.6.52.md` and
`…-2026-09-22-v0.6.53.md`. **Theirs are evidence and are never consolidated;
ours is a claim about now and is rewritten** — the two rules are opposite and
both are right. None declares a live wire header; the `HANDSHAKE-*` lines in the
newest are inside a fenced example, and `test_a_standing_status_is_never_counted_as_a_lap()`
executes that rather than trusting it.

### Upstream

Our `master` mirrors `cyanreg/cyanrip` at `f8ebf48` (2026-08-21), and
**upstream has not moved since**: `git ls-remote` on 2026-09-22 returned
`f8ebf48` for both `cyanreg/cyanrip` and our `origin`. Its analysis is
`docs/upstream/sync-2026-08-24-mb-retry.md`. That is a reading of one moment;
`tools/upstream-delta.py` is how to check again. **Eight defects of ours
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
can never move a user backwards. Both channels resolve to `978f9b0`; there is no
separate beta to take.

**`+platterpus.8` (`796df32`, seq 18) is superseded and should not be installed.**
It is still in the ledger, because the ledger is append-only and a published build
is a fact, but no channel resolves to it any more.

Build command: `meson setup build -Ddeclare_released=true && ninja -C build`.

`release-manifest.json` is the only mechanism to install from and it is what
resolves these; this table is a human-readable copy of it and the test exists
because a copy rots.

**No release is coming while round 16 is open.**
`tools/release-gate.py --release-gate` exits 1 on this tree and names round 16,
which is correct and is not being overridden. Work has landed on
`platterpus-fork` since the pin — all of it documentation, tests and tooling,
none of it in `src/`.
