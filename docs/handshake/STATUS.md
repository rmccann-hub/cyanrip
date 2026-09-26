# cyanrip standing status — what the consumer can assume between rounds

STATUS-NEWEST-LAP: round-28-lap-01.md
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

## Now — rewritten 2026-09-26, after round 27 closed

**This section is the whole of what this file claims.** Everything below it is
either the release table a consumer reads or the rig procedure the suite
checks, and neither is a dated state.

### The release

| | |
|---|---|
| **released** | **`0.9.4-rc2+platterpus.17` at `e0471f4`**, `release_seq` 27, stable, cut 2026-09-26 on round 27's authority |
| build it | `meson setup build -Ddeclare_released=true && ninja -C build` from `https://github.com/rmccann-hub/cyanrip/archive/e0471f4.tar.gz` — verified from a `git archive` of exactly that commit before publication, reporting `released build` |
| previous | `.16` at `221a1df`, seq 26, 2026-09-24, round 26; `.15` at `df91ae7`, seq 25 |
| what `.17` changed | three `src/` commits against `.16`: a 450 lookup compares only 450 checksums (`10f36fe`); the `Accurip 450` match reads `(matches Accurip DB, confidence N, one frame only; whole-track checksums not found)` (`ec0fe47`, a P2 line announced in round 27 lap 4); and a log opened by a run that then fails early starts with the banner and the identity lines (`ee0221c`). `docs/RELEASE-PLAN-platterpus.17.md` |
| `.17` on a drive | **nothing yet.** Round 28's Full run on `.17` with Platterpus 0.6.61 is the first |
| `.16` on a drive | **the Full acceptance on `.16` with Platterpus 0.6.60 ran on 2026-09-26 from 04:13:08Z**: its script reported 320 of 320, 0 skipped, `counts_as_evidence: true` (`docs/rig-2026-09-26-221a1df/`), and Platterpus's ledger grades it `partial` by the operator's ruling, because the records carried errors no step could fail over, two of them lines of our log (`platterpus@d582d6a:docs/handshake/outbound/platterpusstatus.md:314`). Both `.16` changes ran on the drive, each with a before and after on the same disc. **This corrects our round 27 lap 6**, committed at 04:30:48Z during that run: its `HANDSHAKE-TESTED` says the quick run and not the Full run, and lists `.16`'s two changes, a whole-disc rip and a secure re-read as untested by any run. Lap 6 is sent and stays as it is; round 28 lap 1 carries the correction. Still untested: a sector that will not read, and `.17` |
| gate | `--release-gate` exits **1** and names round 28, which is open. That is correct: `.17` is released on round 27's authority, and round 28 reviews it |
| the tip | **the release's publish commit and after.** Build from the release commit, not the tip |
| next | **Platterpus's round 28 lap 2 and their 0.6.61**, which moves `PIN_UNDER_REVIEW` to `e0471f4` and carries `FORK_PIN` `221a1df` (their round 27 lap 5 §D). Then the operator runs one Full acceptance on that pair, which is round 28's close condition 1 |

**`.17` is stable because round 27 authorised it, and the build itself is
round 28's to review.** Platterpus's 0.6.61 carries `FORK_PIN` `221a1df`, so
their app offers `.17` marked `unapproved` until round 28 closes on it. That is
v6 R8 point 2's mark: their offer states it, and a person decides.

### The rounds

| | |
|---|---|
| **round 28** | **OPEN** since 2026-09-26, opened by our lap 1 on **`e0471f4`** (`.17`) before the real test, by the operator's override of R8 point 3, as rounds 26 and 27 were. Close conditions: the Full acceptance on `.17` installed through their app, from their 0.6.61 with `PIN_UNDER_REVIEW` `e0471f4`; both sides' reading of the bundle; R8's two releases (their `FORK_PIN` roll to `e0471f4`, our `.18`). Close-by 2026-10-24. **Our lap 1** is the first opening lap in LSL. It corrects round 27 lap 6's account of that round's testing, asks which `Encoder errors:` form they would read for `.18`, and answers their LSL amendments 1: F1–F4 fixed or written into the spec (`eea9e50`), A1, A2 and A4–A8 accepted, A3 amended, H1–H3 accepted for protocol v7, and a proposal B1 of ours. Next: their lap 2 and their 0.6.61 |
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

| field | value |
|---|---|
| **stable version** | `0.9.4-rc2+platterpus.17` |
| **stable commit** | **`e0471f4`** |
| stable build tag | `platterpus-fork-ge0471f4` |
| stable install | `https://github.com/rmccann-hub/cyanrip/archive/e0471f4.tar.gz` |
| stable `release_seq` | 27 |
| stable authorised by | handshake round 27, closed `GO`/`GO` on `221a1df` / `88c09dd` (Platterpus 0.6.60), six laps — the pins round 27 lap 6 declares |
| | |
| **beta version** | `0.9.4-rc2+platterpus.17` |
| **beta commit** | **`e0471f4`** |
| beta build tag | `platterpus-fork-ge0471f4` |
| beta install | `https://github.com/rmccann-hub/cyanrip/archive/e0471f4.tar.gz` |
| beta `release_seq` | 27 |
| beta authorised by | handshake round 27, closed `GO`/`GO` — same build as stable |

`beta` resolves to the newest row of *any* channel, so opting into pre-releases
can never move a user backwards. Both channels resolve to `e0471f4`; there is no
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
