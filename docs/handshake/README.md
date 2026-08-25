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
commit          237a4ff                          <- build this
--version       cyanrip 0.9.4-rc2+platterpus.7 (platterpus-fork-g237a4ff)
release_seq     17                               <- the ONLY orderable identifier
channel         stable
build           meson setup build -Ddeclare_released=true && ninja -C build
git tag         none published
```

### `beta` — opt-in, **not yet verified by anyone but us**

```
repo            rmccann-hub/cyanrip
branch          platterpus-fork
commit          d9c058c
--version       cyanrip 0.9.4-rc2+platterpus.10 (platterpus-fork-gd9c058c)
release_seq     20                               <- newest of any channel
channel         beta
build           meson setup build -Ddeclare_released=true && ninja -C build
git tag         none published
```

**Two things this beta claims that the previous one did not, both weaker.** It
has **no disc behind it** — 52/52 in four build configurations, and not one
sector read from a drive — *and* it carries **no joint verification**: it was cut
while handshake round 14 was open, on the maintainer's explicit instruction, and
`tools/release-gate.py --release-gate` exits 1 on this tree naming that round.

**`stable` did not move and the assertion protecting it is untouched.**
`gen-release-manifest.py` independently refuses a `stable` row pointing at an
unclosed round; `stable` is `237a4ff`, round 12, closed. The manifest reports
`"round_closed": false` for this beta row, truthfully. Opting in is reversible by
design, and that is the whole reason `stable` is retained.

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

**Every round is closed and a release is permitted.** Round 13 approved
`9f8592e`; `+platterpus.8` was cut at `796df32`, which is the first commit where
the version and every derived artifact agree.

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

| | |
|---|---|
| Every flag, log line, exit code and error string | `PROVIDER-CONTRACT.md` (generated) |
| A worked example of the log | `docs/golden-reference.log` |
| What changed per fork release | `Changelog.md` |
| Behaviour that differs from upstream | `README.md`, *Fork differences* |
| Why the pregap carry looks the way it does | `docs/pregap-carry.md` |

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
