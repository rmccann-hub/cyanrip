# cyanrip standing status — what the consumer can assume between rounds

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

## Rewritten 2026-09-07. **ROUND 16 IS OPEN on `a9aedf0`. The TEST PIN `ddc1e8c` IS AGREED by both sides, and the rig can run.**

**A release is blocked and should be.** `tools/release-gate.py --release-gate`
exits **1** on this tree and names round 16 as open. That is not being
overridden, and no ledger row or manifest change has been made: both channels
still resolve to `978f9b0`.

**What unblocks a hardware session instead is a TEST PIN**, which
`PROTOCOL.md` §6a defines precisely so a round is not deadlocked between
"a close needs hardware evidence" and "the pin may not move while the round is
open". Our lap 2 declared **`HANDSHAKE-TEST-PIN: ddc1e8c`**; **their lap 3 agreed it
verbatim** and carries an S-18 pre-commit — *their next lap is `GO` on
`a9aedf0` + `platterpus 0.6.41` unless the hardware run finds the reviewed pin
unsafe.* So the round now needs a RUN, not another lap, and both sides have
said so.

**Run A is ours and is the one that closes the round.** It drives
`tools/rig-round16.sh` directly against the installed test pin and needs no
Platterpus process at all. **The script at the branch tip is NOT the one they
reviewed**: they hashed `ddc1e8c`'s copy at sha256/16 `615243361882b881`, and
the tip is `178bd4df5dc28d53` — three defects they found in §H1 are fixed in
it (a build check that fired on a correct install, a preflight that said
"Stop." and did not, and `-u` reaching one rip of five). Run A fetches the tip
by design; that is the split their §0 proposes, newest harness against the
pinned binary.

Our lap 2 asks Platterpus
to declare the same one, or name another.

**The test pin is the same program as the production pin**, and that is
checkable rather than asserted: `git diff a9aedf0..ddc1e8c -- src/ meson.build`
is empty, and `git rev-parse a9aedf0:src` and `git rev-parse ddc1e8c:src` are
the same tree object, `bc446254fce57c98…`. A third reading, if you want one
that is not git's: `source_hash()` in `tools/gen-provider-contract.py` gives
`c0f550c75450f031` at both pins.

**Correction, and it is ours.** Round 16 lap 2 §A2, and this file until now,
quoted that hash as `8c2817219f6aa087` and invited the other side to check it.
**It cannot be re-derived.** Platterpus tried six constructions and got six
other values; we then tried six hundred — four file sets, four name schemes,
five digests, three separators, both truncations — and none produces it. The
invariant it was offered as evidence for is TRUE and is confirmed three ways
above; the number was not. A hash published with "check it yourself" and no
method is uncheckable, and this one turned out to be unreproducible as well.
Lap 2 is sent and stays as sent; the correction lives here and in the next
lap.
Everything between the two is `tools/`, `docs/` and regenerated artifacts. It
is preferred only because its logs say `Handshake: round 16 lap 1 OPEN` rather
than naming the previous closed round, and because it carries
`tools/rig-round16.sh`.

**Lap 2 pre-commits under S-18**: our next lap agrees whatever test pin their
reply names. No answer costs another lap of negotiation.

Closed by our lap 14 and their lap 15, both declaring `GO`.
`tools/release-gate.py` reports every round closed.

**Their lap 16 arrived 2026-09-06, out of order and out of turn, and owes no
reply.** `HANDSHAKE-NEXT-LAP: none owed, and none requested`; §F says absorbing
it by reference in our opener is a complete answer. `seam-check` passes 14 of 14
on it: the digest `696b8ada8b203d21 over 15` re-derives here, and so does every
inbound digest since lap 2 — **nine consecutive**, counted by running
`seam-check` over each inbound lap rather than recalled. Lap 2 is the one
`FAIL`, allowlisted because its cause is the old construction and not the
population. All four shared-artifact hashes match this tree.

Its purpose is that their lap 15 had aged: it *promised* a fix for our §5 item 7
and the fix now exists, along with three more. Sending an opener's worth of stale
promises would have cost us a lap collecting corrections.

**A release is NOT cut, and one is now possible for the first time this round.**
The round closing and a release are different acts: no version bump, no
`release-ledger.tsv` row, no manifest regeneration. The build still says
`NOT a released build`, correctly.

### All seven held items have landed. That is what changed since the last rewrite.

Our lap 14 §5 announced seven changes held for round 16 because each moves
something the consumer parses or relies on. **Every one is now in the tree**, each
revert-proved with the build confirmed green during the revert:

| item | what it was | landed |
|---|---|---|
| 1 | the `log_init`/`cue_init` failure paths emitted no completion footer | `a79ac9e` — `fatal_abort = 1`, so `end:` reports the abort rather than a success |
| 2 | **`-H` silently discarded de-emphasis** while the log printed `(deemphasis applied)` and the cue dropped `FLAGS PRE` | `b866900` |
| 3 | an ASCII apostrophe in `-a`/`-t` destroyed every later field | `c59dea3` |
| 4 | invalid UTF-8 truncated a name; an empty leading component made `-D` resolve **absolute** | `c3482b0` |
| 5 | a logfile's first line was not always the fork banner | `c3482b0`, same fix |
| 6 | **no timeout of any kind on any curl handle** | `e7835c3` |
| 7 | timestamps carried no UTC offset | `8d465f1` |

**Their lap 16 §D closes four of the seven on their side** — items 1, 4, 5 and 7
reach them and all four are now handled there too. Item 2 does not reach them at
all (*"we never pass `-H`. Measured across the codebase."*), item 3 is covered by
their escaping, and item 6 they decline to argue us out of.

**Item 2 is the one worth reading.** The filter description was a ternary cascade,
so `hdcd` matched first and `aemphasis` was never reached; audio, log and cue were
**self-consistently wrong**, and a reader checking one against another found
agreement. The composed chain needs two explicit `aresample` bridges, because
libavfilter's `hdcd` filter calls `avfilter_graph_set_auto_convert(NONE)` in its
own init and that setting is **graph-wide** — the plain chain does not mis-render,
it fails to configure. `aformat` cannot substitute: it constrains a link and
relies on the converter that is switched off. Both were tried against libavfilter
directly before either was written.

### Four things found here since the close, none of them lap material

Under the 2026-08-26 reform findings go in commit messages and `Changelog.md`,
which they can read from git and which need no reply.

- **The provider contract published lines the binary never printed.** The
  generator deleted every `\n` in a format string, including **interior** ones,
  fusing two printed lines into one string. It reached **P2** — the surface we
  undertake not to reword without a round — where `cyanrip_log.c:635` published
  `Embedded cover art:    %s: %ix%i %s` while a real rip prints the label and the
  value on separate lines. P5 was worse: `...for writing: %s!Invalid folder name?
  Try -D <folder>.` ran two sentences together with no separator at all. **Nine
  rows** across P2, P3 and P5. Fixed at `1c96c8d`; the corrected contract is the
  commit after. **This is a change to what the contract publishes and is round-16
  material**, even though the binary did not move.
- **`tools/message-witness.py`** answers a question P5 could not: which of its
  messages does anything here actually assert? The 2026-09-05 audit put it at
  "~20 of ~128" as a lead. **Measured: 7 witnessed, 107 with no witness, 6
  unprobable** — a literal prefix too short for a probe to discriminate, counted
  in neither column. It found the fused-line defect on its first run. It gates
  drift and a floor, never full coverage: most of P5 needs a drive, a network or
  an allocation failure, and a permanently red gate is one nobody reads.
- **`check-settled.py` truncated any check command containing a backtick** and
  handed the fragment to the shell, which then failed on an unterminated quote —
  reported as a **stale fact** rather than an unreadable row. Fixed at `c399f44`,
  and the first diagnosis was wrong: the note blamed the `\|` escape, which
  survives fine.
- **`README.md` displayed upstream's green CI badge** at the head of a section in
  this fork's README, for a repository whose own CI has never executed a run.
  Now says whose it is (`6e74343`).

### The shared file has a SECOND wrong row, and they found it

`docs/seam-commands.md` line 504 publishes `-p '99=drop'` as accepted / exit 0;
the binary refuses it. **Line 97 publishes `-D` as `directory` / `str, path` /
`writable` / "output directory".** It is `folder_scheme`, *"Directory naming
scheme"* (`cyanrip_main.c:1603` at the pin) — a **relative scheme**, with `-F` its
per-track sibling. Their lap 16 §B3, read from our source at `978f9b0` and
re-checked here.

**Two is a pattern where one was a coincidence**, and the `-D` row is not
incidental: its real semantics are exactly why held item 4 mattered, since an
empty leading component made a multi-component scheme resolve **absolute**. A
reader who believed line 97 would not have looked.

**Neither cell is corrected.** The file is jointly owned; a correction is a
version bump both sides ship. **They assent to the `--check` remedy** (lap 16 §D)
with two riders we accept: the delimiters must not claim prose either side wrote,
and **the regenerated table must name the build it was measured from** — a shared
hash cannot prove the bytes describe the binary, and neither can its replacement
unless it says which binary.

### Their §G asks one question, and our answer is no

They ask whether our side has a mechanism making a lap's **sent/unsent** state
visible in the tree. **We do not, and we have the same failure at least three
times**: `56e7d71` withdrew a committed lap 5 that was never sent, `d360c38`
edited lap 14 after committing it, `6239860` replaced a lap 13 we had already
answered. Each was stopped by the operator, not by a check.

The reason is structural rather than an oversight: **"sent" is an event outside
both repositories**, so neither tree can observe it. The only in-tree evidence is
the peer quoting the hash back — the check they built, and which they correctly
say is not sufficient. Whether *committed* can stand in for *sent* is a real
trade with a real cost: it is strictly stronger and checkable, and it would have
forbidden our own `56e7d71` withdrawal. That belongs in the round-16 opener.

### What is still not verified, and no green suite implies it

Unchanged by any of the above. **No hardware has run since the run that closed
this round.** Untouched by any run to date: C2 (the rig's drive reports it
unsupported), `-f`, damaged media, CD-TEXT from a disc that has some, the
diagnosed-abort exit code, and `-x` alone returning a drive (`-x -I` has; they are
different claims about the same flag).

**Nothing in this section's landed work has been on a drive.** In particular
item 2 changes **audio** for `-H` on a pre-emphasised disc, and item 6 changes
what happens when a network endpoint stalls — neither of which any fixture here
can exercise.

## Releases — read the channel, never the version string

**`0.9.4-rc2+platterpus.11` is a STABLE release.** The `-rc2` is upstream's own
string, copied verbatim because we may not mint in `cyanreg/cyanrip`'s namespace;
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
| **stable version** | `0.9.4-rc2+platterpus.11` |
| **stable commit** | **`978f9b0`** |
| stable build tag | `platterpus-fork-g978f9b0` |
| stable install | `https://github.com/rmccann-hub/cyanrip/archive/978f9b0.tar.gz` |
| stable `release_seq` | 21 |
| stable authorised by | handshake round 14, closed `GO`/`GO` on `d9c058c` / `b524936` |
| | |
| **beta version** | `0.9.4-rc2+platterpus.11` |
| **beta commit** | **`978f9b0`** |
| beta build tag | `platterpus-fork-g978f9b0` |
| beta install | `https://github.com/rmccann-hub/cyanrip/archive/978f9b0.tar.gz` |
| beta `release_seq` | 21 |
| beta authorised by | handshake round 14, closed `GO`/`GO` — same build as stable |

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

**No release is coming while round 15 is open.**
`tools/release-gate.py --release-gate` exits 1 on this tree and names round 15,
which is correct and is not being overridden. Work has landed on
`platterpus-fork` since the pin — all of it documentation, tests and tooling,
none of it in `src/`.

## Round 15 — closed at 16 laps

| | |
|---|---|
| **opened** | our lap 1, on the released pair rather than a test pin |
| **close condition** | **one, fixed at lap 1 under S-13: CC-1**, a hardware acceptance pass on the released pair. **Met** |
| **pin** | `978f9b0`, unmoved all round on both sides. No test pin was ever declared |
| **closed by** | our lap 14 (`GO`) and their lap 15 (`GO`), each transcribing the other |
| **their lap 16** | out of order, `GO`/`GO`, **no reply owed**. Four fixes on their side, an assent, and one question (§G, answered above) |
| **next** | **round 16, ours to open.** Not yet open |

**The reform's measure is lap count, and round 15 ran to 16.** Round 14 ran to
nineteen; the reform's own test was *"round 15 closes in three laps or the reform
failed"*. It did not. Sixteen is better than nineteen and it is not three, and
saying so is cheaper than explaining it away.

### The digest methods no longer differ — seven consecutive agreeing values

Lap 2 declared `a1ff77af1fd6e3cb over 1` where we derived `c8fa5d93d9af5a20`:
same population, different construction. Lap 3 §3 shipped our full spec and
asked them to adopt one or tell us to adopt theirs.

**They adopted ours and built it independently** (`scripts/round_digest.py`),
having first reproduced both of lap 2's numbers. Every value since re-derives
here exactly, in both directions:

| lap | declared | |
|---|---|---|
| theirs 4 | `1ad28e7744de3d6b over 3` | reproduces |
| theirs 5 | `ddc0d8a741f76b60 over 4` | reproduces |
| theirs 6 | `09268d7203773872 over 5` | reproduces |
| theirs 7 | `60a7c64dc252b1fa over 6` | reproduces |
| **ours 8** | `44e14b452950ebb0 over 7` | **they reproduce it** — their lap 9 §B2 |
| theirs 9 | `35b861f25abfa69c over 8` | reproduces |

**Two implementations of one written spec, agreeing on six consecutive values,
neither having read the other's code.** Their §B2 makes the point that matters:
two implementations agreeing is weak evidence when they share an ancestor and
strong evidence when they do not. These do not.

The allowlist entry in `tests/release_gate.py` stays pinned to lap 2's declared
value, because lap 2 is immutable and was computed by the old method.

### The process reform — 2026-08-26, on the maintainer's instruction

Round 14 ran to nineteen laps with every rule followed, which is round 7's failure
repeated. **Cut: §J as a requirement, acknowledgement laps, "send a file even when
nothing changed", and findings written up in laps.** Kept: every rule about
evidence. **One file per exchange and it is the lap** — the repository is the
transport, and a test does not travel, its specification does.

**The measure is lap count and round 15 is at 3.** `docs/SETTLED.md` is the index
that stops facts being re-derived, and `tools/check-settled.py` runs every row's
check.

---

## What we know about their side, and how we know each part

Separated by provenance, because these are different strengths of claim.

| | |
|---|---|
| `0.6.34` is what ran on 2026-09-03 | **measured**, from `Consumer:` in every log we hold |
| `0.6.33` at `0a69732` is their round-15 release | **read from their lap 2 §B** |
| `0.6.34`'s commit | **unknown.** Nothing we hold names it; the `Consumer:` string carries no SHA |
| their `0.6.33` banner reads `platterpus 0.6.33 (0a69732)` | **UNVERIFIED.** Lap 3 said the next bundle would answer it. It does not — the bundle is `0.6.34` |
| `0.6.34` treats `978f9b0` as `unapproved` | **measured**, from their JSON: *"NOT the build this Platterpus was verified against (platterpus-fork-gd9c058c)"* — which is round 14's pin, so the field is right and round 15 is what changes it |
| their `FORK_PIN` is `ddf7ac3`, unmoved | **read from their round-14 lap 7 §W2** |
| **`0.6.22` NEVER EXISTED** | **read from their standing status**, which corrects their own lap 4 |

**`session/DIAGNOSTICS.txt`'s banner names `+platterpus.10` / `d9c058c` while
every rip in that bundle was made by `+platterpus.11` / `978f9b0`.** Not a defect:
the banner names the **approved** pair, not the running one. Checked before it was
written down, because the shorter reading was "their diagnostics are stale".

### Where their statuses are filed

`docs/handshake/inbound/status-2026-08-21-v0.6.21.md`,
`status-2026-08-21-v0.6.23.md` and `status-2026-08-24-v0.6.23.md`. All three, kept
dated, even though *their* rule is to rewrite in place.

**The last two share a version and differ in date, which is the whole argument for
keeping both.** Same declared version, two different claims about the world. Under
their own rule the first no longer exists on their side; under ours it is evidence
and is kept. **The date in those filenames is the one the document declares, not
the day we received it**, and the two differ.

Neither declares a wire header, so no enumerator can count them — and
`test_a_standing_status_is_never_counted_as_a_lap()` executes that rather than
asserting it, including the case a rename would hit.

## Upstream: one commit inbound, deliberately not merged

Upstream moved on 2026-08-24: `f8ebf48`, *"src/musicbrainz: retry queries when
busy"*. **Our mirror is synced; `platterpus-fork` does not contain it.**

It adds two log lines — `Retrying in %_ seconds (attempt %_ out of %_)...` and
`MusicBrainz lookup failed, try again later,` — **neither of which can appear in a
Platterpus rip**, because they pass `-N` and `-N` disables the lookup entirely.
Recorded anyway, because a log line entering our contract is handshake material
whether or not the one consumer we have can reach it. The analysis is
`docs/upstream/sync-2026-08-24-mb-retry.md`.

**Three defects of ours are verified as present upstream and not yet contributed
back**: the signal-handler deadlock, SIGTERM unhandled, and the completion-footer
skip. Each has its re-check in `docs/SETTLED.md`.
