# The Platterpus handshake

This fork feeds **Platterpus** (`rmccann-hub/Platterpus`), which parses this
program's log as an archival record. That makes the log an interface and the two
projects each other's dependency, so changes to what a consumer can observe go
through a **round**: we send a file, they verify it against their real parser,
they send a verification file back. A round stays **OPEN** until that arrives,
and neither side releases while one is open.

The protocol itself — what a round must contain, and the rules both sides hold
to — lives in `CLAUDE.md` under *The Platterpus seam*. This directory is the
record of the rounds themselves.

---

## Current pin

**Two channels resolve to two different builds.** `stable` is what you get
without opting in; `beta` is newer and has never been run on a drive. Pick by
risk tolerance, not by recency — and never by comparing the version strings,
which cannot be ordered at all.

### `stable` — the default

```
repo            rmccann-hub/cyanrip
branch          platterpus-fork                  <- the only branch to build from
commit          3e01bb3                          <- build this
--version       cyanrip 0.9.4-rc2+platterpus.14 (platterpus-fork-g3e01bb3)
release_seq     24                               <- the ONLY orderable identifier
channel         stable
build           meson setup build -Ddeclare_released=true && ninja -C build
git tag         none published
```

### `beta` — currently the SAME BUILD as stable

```
repo            rmccann-hub/cyanrip
branch          platterpus-fork
commit          3e01bb3
--version       cyanrip 0.9.4-rc2+platterpus.14 (platterpus-fork-g3e01bb3)
release_seq     24                               <- newest of any channel
channel         beta
build           meson setup build -Ddeclare_released=true && ninja -C build
git tag         none published
```

**`beta` resolves to the newest row of ANY channel**, so opting into
pre-releases can never move a user backwards. `+platterpus.12` is the newest row
overall, so both channels resolve to it and there is no separate beta to take.
That property was not decorative: the first generated manifest had `beta` on seq
10 while `stable` was seq 11, so opting in would have been a downgrade.

**`0.9.4-rc2+platterpus.12` IS A STABLE RELEASE despite the `-rc2`.** That
string is upstream's, copied verbatim because we may not mint in
`cyanreg/cyanrip`'s namespace; the part that advances is SemVer build metadata,
which the spec says MUST be ignored for precedence. **A check that reads the
shape of the version will call this a pre-release and will be wrong.** Order by
`release_seq`; read the `channel` column.

**Authorised by handshake round 14, closed `GO`/`GO`** on `d9c058c` /
Platterpus `b524936`, with its single close condition met by two independent
hardware runs on that build — including T1, the whole-disc secure re-read, which
had never run anywhere before 2026-08-26.

**`+platterpus.8` (`796df32`, seq 18) is superseded** — still in the ledger,
because a published build is a fact and the ledger is append-only, but no channel
resolves to it.

`release-manifest.json` is the machine-readable form and is authoritative;
this block is a convenience copy, and `sc_status_is_current()` compares the two
on every test run. That check exists because **this block had gone five releases
stale** — it named `d5d12ec` / `+platterpus.3` long after the manifest resolved
to `+platterpus.7`, so anyone following the directory's own index would have
built a binary from July. A document that claims something about *now* and is
checked by nobody is the shape this directory keeps finding wrong.

**Pin the commit, not the tag, and not the branch tip.** The git proxy in this
environment refuses tag pushes (`HTTP 403` — re-probed each round rather than
assumed); `git ls-remote --tags origin` returns nothing, and no tag from this
fork has ever reached the remote. The commit SHA is the only release identifier a
consumer can resolve.

`237a4ff` is **the released commit, not the last commit that changes the
binary** — the two are different questions and this file used to answer the
second. A release is the first commit at which the version and every derived
artifact agree AND the round that reviewed it has closed; commits after the
version bump that only regenerate artifacts are part of the release, not noise
before it. Verified at `237a4ff` itself, from a fresh clone rather than a working
tree: the whole suite as it stood at that commit — 47 tests — passed in four
build configurations including ASAN and UBSAN. The suite has grown since; that
number describes the release's verification, not the tree today.

**Do not use `0.9.4-rc3`.** That string was committed locally, never released,
and withdrawn: it mints an identifier in upstream's namespace, which upstream can
also mint. See `round-07-lap-01.md` §2.

**Superseded, do not build:** `2f950c8` (r2 — carries the read-liveness heartbeat
that never fired, `round-07-lap-01.md` §0), `ad65a244` and `e1d800e` (both carry the
disc-image silence defect fixed in r2).

### Branches on the remote

As reported by `git ls-remote --heads origin`, which asks the remote — not by
`git branch -r`, which prints a cache and once made this file list two branches
that did not exist.

| ref | what it is |
|---|---|
| `platterpus-fork` | integration branch — **build from this** |
| `master` | clean mirror of upstream `cyanreg/cyanrip`, never committed to |

**Two, and only two.** This table used to list a third,
`claude/pending-task-vg2afd`, and it is gone from the remote. It is worth saying
why rather than quietly dropping the row: a session branch pushed once is
**permanent from inside a session** — branch delete is `HTTP 403` from this git
proxy, measured by trying it — so it can only be removed by the repository
owner, and one was. The standing rule is therefore not to create the problem:
develop on a session branch locally, land on `platterpus-fork`, push only that.

`platterpus-fork` is no longer strictly fast-forward: `1ee56fc` is a merge
commit, the upstream `0.9.4-rc2` sync. That carve-out is deliberate and is
recorded in `CLAUDE.md` — the straight-line rule exists so a consumer can
bisect our own topic work, and an upstream sync is not that.

## Round status

**Do not read this table as authoritative — run the gate.**
`python3 tools/release-gate.py` prints the live state from the declared verdicts
in `docs/handshake/`, and it is what blocks a release. This table went stale
once already, stopping at *"round 7 is open"* through five closed rounds.

| Round | State | Pin it settled on | Record |
|---|---|---|---|
| 5 | closed, GO | `e1d800e` *(superseded)* | `round-5.md` |
| 6 | closed from our side by round 7; verification file never received | `2f950c8` *(superseded)* | `round-6.md` |
| 7 | closed, GO/GO — 39 laps | `5bc654d` *(superseded)* | `round-07-lap-39.md` |
| 8 | closed, GO/GO | `ddf7ac3` — **the build Platterpus installs** | `round-08-lap-17.md` |
| 9 | closed, GO/GO | *(no pin move)* | `round-09-lap-11.md` |
| 10 | closed, GO/GO | `56413d2` *(superseded)* | `round-10-lap-05.md` |
| 11 | closed, GO/GO | `beb9fba` *(superseded)* | `round-11-lap-03.md` |
| 12 | closed, GO/GO — 4 laps | `64ae7bc`, released as `237a4ff` | `round-12-lap-03.md` |
| 13 | closed, GO/GO — 8 laps | `9f8592e`, released as `796df32` (`beta`) | `round-13-lap-08.md` |

| 14 | closed, GO/GO — 16 laps | `d9c058c`, released as `+platterpus.11` | `round-14-lap-*.md` |
| 15 | closed, GO/GO | *(see the gate)* | `round-15-lap-*.md` |
| 16 | closed, GO/GO — 17 laps | `fe4d2c4` line; closed on Run A hardware | `round-16-lap-17.md` |
| 17 | closed, GO/GO — 3 laps | **`fe4d2c4`, released as `+platterpus.12`** | `round-17-lap-03.md` |
| 18 | closed, GO/GO — 3 laps | *(no pin move — a procedure round)* | `round-18-lap-03.md` |
| 19 | closed, GO/GO — 3 laps | *(no pin move — a procedure round)* | `round-19-lap-03.md` |
| 20 | closed, GO/GO — 3 laps | *(no pin move — a procedure round; `fe4d2c4`, under `0.6.48` then `0.6.49`)* | `round-20-lap-03.md` |
| 21 | **CLOSED `GO`/`GO`**, 2026-09-18, five laps, **32 days before the declared close-by**. §0.2 closed by their refusal; §0.1's three conditions answered from one whole-disc `fast_verified` rip on the test pin (`docs/rig-2026-09-17-3952c03/`) — **and item 2 was never satisfiable as worded, which is our defect** and is explained in lap 5 §2 rather than ticked. Two P2 changes shipped: `Frame retries:` → `Retry limit:`, and `Ripping errors:` now counting encoder failures. Their `verified/round-21-lap-06.md` is a verification record, **not a lap** — not sent, not filed here, not in any digest | *(pin `fe4d2c4` and test pin `3952c03` both unmoved all round; the test pin **does not become a release**, §6a)* | `round-21-lap-05.md` |
| 22 | **CLOSED `GO`/`GO`**, 2026-09-21, five laps, 27 days before the declared close-by. Opened 2026-09-18 on the new pin. Carries the **operator's goal for the round** — fix all known issues, release both applications by the close, then a full hardware acceptance test to **open round 23**. Two close conditions and **neither needs a drive**: §0.1 the two shared-protocol changes (their K1, our K3), §0.2 whether a Platterpus release can be cut inside this round. Declares `HANDSHAKE-PROTOCOL: 4` and proposes 5, because both sides must ship a version before either declares it. **A third condition, §0.3, was added while lap 1 was still HELD** — the per-track split, announced as two P2 lines and corrected by their lap 2 to a **P1**: the renamed line is their `_TRACK_START` block delimiter, so on the real `3952c03` log the rename takes 14 parsed tracks to **0** while the disc-level fields still read 14 of 14 and `No errors occurred`. **Not a veto** — their ask is the round-20 ordering, their both-wordings release before our `+platterpus.14`, agreed at `1dfd9fc`. Lap 2 closes §0.1 and §0.2; lap 3 is `GO` from our side and names a circularity in their own `GO` condition. **Their lap 4 resolves it by route (i)** — the one lap 3 recommended — conceding that the second clause of their own condition conflated a decision with an act, and declares `GO`/`GO` on `2cce60d` with no question and nothing that could reopen it. **Lap 5 is ours and is the close**, and it is a fifth lap for a reason worth the row: `PROTOCOL.md` §5 needs `HANDSHAKE-PEER-VERDICT: GO` **in a file of ours**, and lap 3 declared `OPEN` because that was the only honest value when it was written — so their lap 4 closed the round on their gate and could not on ours. That is `SETTLED.md` row 102, from round 17 with the roles reversed, and lap 5 §H1 proposes the v5 fix rather than making it | *(pin **`2cce60d`** = `+platterpus.13`, released on round 21's authority; **no test pin**, declared `none` as an answer)* | `round-22-lap-05.md` |
| 23 | **CLOSED `GO`/`GO`**, 2026-09-22, five laps by the measure `CLAUDE.md` states — the highest `HANDSHAKE-LAP` either side declared; four by Platterpus's own count — 30 days before the declared close-by. Opened the same day, the day after round 22 closed. **It reports hardware rather than demanding it** — the full acceptance session ran first, on 2026-09-22, 247 of 247 steps on `2cce60d` + Platterpus 0.6.52, filed at `docs/rig-2026-09-22-2cce60d/`; that is round 21's lesson applied, whose five laps came of naming a condition no desk lap could supply. Three close conditions, fixed at lap 1 and unable to grow (R1/S-13): **§0.1** `PROTOCOL.md` v5 — the close rule plus Platterpus's condition on it, that a lap count only once it declares `HANDSHAKE-READY-TO-READ: yes`; **§0.2** that a HELD lap's draft verdict reaches the compiled `Handshake:` line, which is a change to that line's value vocabulary and so a condition rather than a commit; **§0.3** that every non-pass in the acceptance run is dispositioned — fixed, filed with a named owner, or shown not to have been real — which is deliberately not *"zero failures"*, a finish line neither side controls. **We pre-commit to `GO`.** The run reached the two round-21 items `fe4d2c4` could not: `Retry limit:` on real logs, and `Ripping errors:` as the moved field on a real interrupted session. Two findings, neither a condition — tracks 3 and 5 were superseded by an automatic re-rip with no addendum written (**wrong, and retracted in lap 3; see below**), and every audio figure our log reports is measured upstream of the filter graph. `+platterpus.14` is **explicitly a non-condition**: it ships on round 22's authority, after Platterpus's both-wordings release. **Lap 2 is theirs and answers all three**: §0.2 assented after running four banner shapes through their real parser, §0.3 agreed on four of five rows, §0.1 assented in substance with the drafting left to us — plus a `partial` grade on their own script, because three of eight rips had post-rip checks dropped unfinished and no step could see it. **Their §A refutes our §0.3 row 2 and they are right**: `retried_tracks` records `replaced: false` on tracks 3 and 5, a swap happens only on a converged re-read, so nothing was superseded and the absent addendum was a correct negative. Retracted in lap 3 §A; the cause was filing the session without the `.platterpus.json` records and then reasoning about a question one field in them answers. **Lap 3 is ours and is `GO`**, discharging lap 1's pre-commitment, and it lands `PROTOCOL.md` **v5** — §5b the close rule, §5c their condition on it, `HANDSHAKE-PEER-VERDICT-SOURCE` their field, rows C37–C42. Implemented but inert: every path is gated on the FILE's declared version and nothing declares 5, so **round 23 still costs the extra lap v5 exists to remove, and round 24 is v5's first *possible* test** — only once their gate, which implements 4, reaches 5, since a v4 gate refuses a file declaring 5 (`STATUS.md`). **Lap 4 is theirs**: v5 committed byte-identical, `GO`/`GO`, and their gate closes it — but ours could not, because §0.1's condition names `seam-sync-check --fetch` and it still exited **1**: v5 was on their working branch and not on `main`, the default branch the tool reads and the one their own `FROM-COMMIT-SOURCE` calls *"the ref you can fetch"*. Held open one exchange rather than closed on a check that said no. **Lap 5 is ours and is the close**, once `main` carried v5 at `platterpus@48776b0` and the tool exited 0 on all four. **And §D2 happened**: the PR squash-merged and the branch was deleted four minutes later, orphaning both commits this round's citations name — one of them in a lap already sent. Recovered from a session clone before GitHub ran `gc`, which is luck and is filed as an event rather than a success. Lap 5 adopts their round-24 proposal early: **the sha256 is the anchor, the commit is a fetch hint** | *(pin **`2cce60d`**, unchanged from round 22 and it never moved (S-15) — that round reviewed this commit's contract, this one reviews its behaviour on a drive; **no test pin**, declared `none`)* | `round-23-lap-05.md` |

**THIS TABLE WENT STALE AGAIN, EXACTLY AS ITS OWN WARNING DESCRIBES.** It
stopped at round 13 through **five** closed rounds (14–18) while claiming
*"every round is closed"* and naming `+platterpus.8` at `796df32` as the
release — which had been superseded twice. Found 2026-09-13 by auditing this
directory against `tools/release-gate.py`. **The warning above the table did not
stop it happening a second time, so read the gate and treat the table as a
convenience.**

**Every round is closed and a release is permitted.** The live release is
**`0.9.4-rc2+platterpus.14` at `3e01bb3`**, `release_seq` 24, authorised by
round 22 — the first release of this fork with a **consumer-side
prerequisite**, met by Platterpus 0.6.53, because both renamed lines are their
`_TRACK_START` block delimiter. `Track %i read successfully!` / `read with
errors.` and the new `Encoder errors:` line are P2. **Their `FORK_PIN` still
names `2cce60d`**, and they have said it moves only once a round reviews `.14`,
so their app offers `.14` stamped `unapproved` until then — accepted on the
operator's instruction, and round 24's opening lap says so. Round 18 agreed a tiered acceptance *procedure* and deliberately moved
no pin.

**Round 13 carried one close condition out with it, and that is a first.** CC-2
required a hardware acceptance pass, and it was mis-specified: it named a *test
pin* that could not be the released commit, so satisfying it would still have
left the released pair with no hardware evidence. It was **moved** to round 14 by
explicit bilateral agreement — never deleted, and never by one side alone. Those
three properties are what stop the mechanism emptying every future round, and
they are `seam-rules.md` v5's newest row rather than an improvisation.

Round 14 opens from our side with CC-2 as its only close condition.

Per the protocol a "no changes" round is still a round; silence is not.

## Between rounds

`STATUS.md` here is the standing status — **not a lap**, declares no
`HANDSHAKE-*` wire headers, and no conforming enumerator can count it.
Platterpus's received statuses are filed dated under
`inbound/status-YYYY-MM-DD-vN.md`.

Ours is rewritten in place; theirs are kept as they arrive. Both rules are right
and they are opposite: ours claims something about now, theirs are evidence of
what we were told and when. See `CLAUDE.md`.

## What a consumer needs, and where it lives

**Under pull transport (2026-09-13) this table is how the consumer finds a lap,
so it has to name the laps — it did not, because laps used to be mailed.**

| | |
|---|---|
| **Our laps — the handshake itself** | **`docs/handshake/round-NN-lap-LL.md`**, both fields zero-padded |
| **Our standing status, between rounds** | **`docs/handshake/STATUS.md`** — rewritten in place, claims about *now*, carries no `HANDSHAKE-*` wire headers so no enumerator counts it |
| **Laps we have received** | `docs/handshake/inbound/` — filed byte-exact; a transport envelope is kept as `envelope-round-NN-lap-LL.md`, a name no `round-*-lap-*` glob can match |
| **The live round state** | `python3 tools/release-gate.py` — the gate, not the table above |
| The shared seam documents | `docs/handshake/PROTOCOL.md`, `docs/seam-rules.md`, `docs/seam-commands.md`, `docs/OWNERSHIP.md` — **neither project owns any of them** |
| Every flag, log line, exit code and error string | `PROVIDER-CONTRACT.md` (generated) |
| A worked example of the log | `docs/golden-reference.log` |
| What changed per fork release, **and every finding** | `Changelog.md` — the no-reply channel; findings go here, not in laps |
| Facts already settled, with the command that re-checks each | `docs/SETTLED.md` |
| Known defects we have not fixed, and why | `docs/KNOWN-ISSUES.md` |
| What a user installs, and from which commit | `release-manifest.json` |
| Behaviour that differs from upstream | `README.md`, *Fork differences* |
| Why the pregap carry looks the way it does | `docs/pregap-carry.md` |

## Where WE read from, in THEIR repository

**The other half of the same map, and it did not exist until 2026-09-13.** It
lived only in one session's scrollback, which is the failure `SETTLED.md` was
created to stop. Derived by reading `rmccann-hub/Platterpus` at `abd2eb8`, not
from memory:

| | |
|---|---|
| Their laps, as sent | `docs/handshake/outbound/` — **naming is theirs, not the agreed one**: `round17lap02FROMplatterpusTOcyanrip.md`, unpadded, no separators |
| Their canonical/filed copies | `docs/handshake/verified/` |
| Laps of ours they hold | `docs/handshake/inbound/` |
| Their standing status | `docs/handshake/outbound/platterpusstatus.md` — **not** named `STATUS.md`; a `STATUS*.md` search finds nothing in their tree |
| Their copy of the protocol | `docs/handshake-protocol.md` — **a different path from ours** (`docs/handshake/PROTOCOL.md`); the other three shared files share our path |
| Their gate | `scripts/handshake.py` |
| Their state vocabulary | `src/platterpus/uiscript/report.py` — six outcomes; **their `SKIPPED`/`BLOCKED` are swapped against ours** |
| Their version | `src/platterpus/__init__.py`, `__version__` |
| Their changelog | `CHANGELOG.md` (upper case; ours is `Changelog.md`) |

**Clone it read-only; we cannot push to it:**

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone \
    https://github.com/rmccann-hub/platterpus /home/user/rmccann-hub/platterpus
git -C /home/user/rmccann-hub/platterpus fetch origin HEAD           # to update
git -C /home/user/rmccann-hub/platterpus fetch origin <branch>       # a lap on a branch
```

**NO `--depth`, and these commands used to carry it.** `fetch --depth 1` turns a
full clone shallow — measured 2026-09-15, a 5-commit clone reduced to 1 — which
is why `tools/seam-sync-check.py` stopped using it. A shallow clone cannot answer
`git merge-base --is-ancestor`, and that is the check that decides whether a
commit a sent lap cites is still reachable. **It decided exactly that on
2026-09-22**, when their branch was deleted by a repository setting and
restored: both cited commits were confirmed reachable as ancestors of the
restored branch — and a first pass that scanned stale `refs/remotes/` without
fetching the branch said they were not.

**Pull transport is live in both directions now.** Platterpus publishes laps to
`docs/handshake/outbound/` in their repository, on `main` once merged and on a
working branch before that — so a lap can be readable before it reaches their
default branch, and must be cited by content hash first with the commit as a
fetch hint. On 2026-09-13 their newest published lap was round 17 lap 2 and
laps reached us through the operator; that is no longer true. **"§5b.7" here once
named this, in `PROTOCOL-v5-PROPOSAL-evidence-transport.md`'s numbering — which is
not the v5 that shipped**; shipped v5's §5b is the round-23 close rule. Pull
transport is operative by operator rule and practice, not by the spec.

`PROVIDER-CONTRACT.md` is generated by `tools/gen-provider-contract.py` from the
source tree and the built binary. Regenerate it rather than editing it;
`--check` exits non-zero when the committed copy is stale.

## Regenerating the golden reference

```sh
mkdir /tmp/g && cp tests/fixtures/pregap.cue /tmp/g/ && cp tests/fixtures/cdda.bin /tmp/g/pregap.bin
cd /tmp/g && cyanrip -d pregap.cue -N -A -Q -s 0 -o flac -Z 2 -G \
                     -D o -F "{track}" -L reference -M sheet -P 0
```

**Every flag there is load-bearing**, and a reference generated without them
silently guards less than it appears to:

- `-P 0` — without it the audio is silence on any build before r2, and the
  reference describes a rip that never happened properly
- `-Z 2` — without it the secure-re-read surface is not exercised at all
- `-G` — keeps the ReplayGain tags, including the over-full-scale peaks that
  exercise a consumer's `> 1.0` reconciliation

Varying per run: `Invoked as:`, `creation_time`, `Extraction speed:`,
`Elapsed:`, the paranoia counters, `Encoder:`, and the `Log FUN512:` covering
them. Everything else is reproducible.

## Open hardware gates

Three, all needing a disc in a real drive. None blocks a release; all three are
about paths that have never executed rather than paths that might regress.

1. **`Pregap source: sub-channel` succeeding on real media.** *(See the note
   below — this may now be closed.)*
2. **A cancelled rip on the rig**, proving the `setvbuf` fix under podman, which
   does not forward signals into the container.
3. **The read-liveness heartbeat firing on a real stall.** `-k` now lets the
   threshold match a consumer's own stall detector.

> **Gate 1 appears closed.** A rig rip on 2026-08-03 with fork build
> `g2f950c8` reports `Pregap source: sub-channel (not signalled by TOC)` on
> thirteen of fourteen tracks, with plausible lengths (85–160 frames) that the
> TOC did not declare. That is the first sub-channel success observed anywhere,
> on either side. It needs confirming against a second disc before the gate is
> struck, and belongs in the next round.
