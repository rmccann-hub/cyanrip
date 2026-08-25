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

## Rewritten 2026-08-24. **Round 13 is CLOSED. Two releases exist.**

The previous rewrite of this file, earlier the same day, said round 13 was open,
that we did not hold their lap 1, and that **no release was to be cut from this
side.** All three have changed. Round 13 closed `GO`/`GO` on `9f8592e` in eight
laps, and `0.9.4-rc2+platterpus.8` is published on the **`beta`** channel.

### The release table — now two channels, and the rows are named for it

**`commit` was an unambiguous row label until this morning.** It stopped being one
the instant a second channel was published, which is the same defect as
`Peak level:` becoming ambiguous when `True peak level:` was printed below it. The
rows are channel-qualified now, and `sc_status_is_current()` was changed to key on
the qualified names *and* to check the beta row, which it never did before —
nothing verified the beta channel of this table until there was a beta in it.

| | |
|---|---|
| **stable version** | `0.9.4-rc2+platterpus.7` |
| **stable commit** | **`237a4ff`** |
| stable build tag | `platterpus-fork-g237a4ff` |
| stable install | `https://github.com/rmccann-hub/cyanrip/archive/237a4ff.tar.gz` |
| stable `release_seq` | 17 |
| stable authorised by | handshake round 12, closed `GO`/`GO` on `64ae7bc` |

| | |
|---|---|
| **beta version** | `0.9.4-rc2+platterpus.9` |
| **beta commit** | **`f2c0506`** |
| beta build tag | `platterpus-fork-gf2c0506` |
| beta install | `https://github.com/rmccann-hub/cyanrip/archive/f2c0506.tar.gz` |
| beta `release_seq` | 19 |
| beta authorised by | **nothing yet — handshake round 14 is OPEN** |

**`+platterpus.8` (`796df32`, seq 18) is superseded and should not be installed.**
It is still in the ledger, because the ledger is append-only and a published
build is a fact, but no channel resolves to it any more.

Build command for either: `meson setup build -Ddeclare_released=true && ninja -C build`.

`release-manifest.json` is the only mechanism to install from and it is what
resolves these; this table is a human-readable copy of it and the test exists
because a copy rots.

### Why beta, and why a SECOND beta — read this before pinning anything

**`+platterpus.9` has not been verified by anyone but us, and it was cut while
round 14 was open.** Both facts are stated here because neither is visible from
the version number.

**Two betas in two days is not churn, it is the CC-2 repair applied again.**
Round 13's original close condition measured a *test pin* while the release would
necessarily be a later commit — so satisfying it would still have left the
released pair with no hardware evidence. It was moved to round 14 by bilateral
agreement (our lap 6 §N1, their lap 7 §W1) precisely so the pass would test **the
build that ships**. Then four fixes landed after `796df32` was cut, and testing
`796df32` would have meant testing something nobody would install — the same gap,
one release later. So the release moved to match the fixes, rather than the test
being pointed at a stale build.

**Round 14's pin therefore moves to `f2c0506`.** That is a departure from S-15,
which freezes a pin for the duration of a round, and it is declared as one rather
than smuggled. The maintainer instructed it, both projects are cutting fresh
releases, and the alternative was a hardware pass on a build no consumer would
ever install.

**What the gate says, recorded rather than worked around:**
`tools/release-gate.py --release-gate` **exits 1** on this tree and names round
14 as open. The rule it enforces — no release while a round is open — was
overridden deliberately.

**What was NOT overridden, and this is the part that matters to a user.** The
gate protects `stable`, and `stable` did not move: it is still `237a4ff`, seq 17,
round 12, closed. `gen-release-manifest.py` independently refuses a `stable` row
pointing at an unclosed round, and that assertion is untouched and still passing.
The manifest reports `"round_closed": false` for the beta row, truthfully. A
`beta` pointing at an open round is exactly what the beta channel is for.

`beta` resolves to the newest row of **any** channel, so opting in reaches
`+platterpus.9` and can never move a user backwards.

**Their `FORK_PIN` stays at `ddf7ac3` and we are not asking them to move it.**
Their lap 7 §W2 is right that a pin they have not run on hardware is a pin they
do not claim, and their bar and ours agree here.

**A consequence they found and own:** a user who opts into `beta` gets
`unapproved` in their archival record, and their §W3 identifies that as
overstating — the true statement is *"jointly verified, no hardware evidence
yet"*, which is the same missing state their §J1 hit in the verdict vocabulary a
week earlier. Two vocabularies, one absent value, discovered independently. That
is theirs to fix and they have not asked us for anything.

### What `+platterpus.9` adds on top of `+platterpus.8`

**Nothing in `src/`.** The source anchor is unchanged, so the binary behaves
identically. Said explicitly because "a new release" normally implies changed
behaviour and here it does not.

1. **A false structural claim removed from `PROVIDER-CONTRACT.md`, and the
   generator taught to derive what it used to assert.** P2 printed one hardcoded
   sentence under *every* buffer-composed row — *"Segment 0 is always present;
   the rest are appended conditionally"*. It is right for the progress line and
   **flatly wrong for `Cache probe:`**, whose nine segments are `switch` arms
   that each write the whole buffer and `return`, so exactly one is emitted. A
   matcher built from it is a concatenation pattern that can never match a real
   probe result — and that is the line round 14's T3 exists to put on a drive.
   Now derived: a whole-buffer `snprintf` replaces, only an offset write appends.

2. **`contract_composed`**, which asserts against the **binary** rather than the
   document — it runs `-x -I` and checks the emitted line carries exactly one
   segment head. 52 tests, up from 51. Revert-proved on both assertions.

3. **`docs/round-14-acceptance-spec.md`** — what we expect the acceptance pass to
   *observe*, per test, measured by running the binary. It states no acceptance
   criteria: we report measurements, Platterpus judges.

### What `+platterpus.8` contained, and `.9` inherits

Round 13's work, all of it already reviewed by them:

1. **`[ASK A]` answered — the `-T` substitution table is published as `P7`**,
   derived in five parts: the default and four spellings, the substitution table
   with codepoints, the effective result per mode per compile-time branch, the two
   behaviours a table cannot express (`/` is decided by the call site rather than
   the mode, and the two quote glyphs alternate on a parity), and the availability
   macros with `file:line`. The `sanitize` scenario parses P7c out of the committed
   contract and rips with each mode, so the document is checked against the binary.

2. **Their `os_unicode` derivation was inverted, and we measured it rather than
   argued it.** The name their rig produced is the `unicode` **default**; `<` being
   legal on ext4 is why `os_unicode` leaves it *alone*. Their newly-pinned
   `-T os_unicode` would have changed every folder name they write.

3. **A CD-Extra defect that published a garbage DiscID at exit 0.** An unguarded
   session-gap subtraction ran the LSN negative, `discid.c` left-shifted a negative
   int (undefined behaviour), and the run emitted `CDDB ID: FFFF6E02` with **no
   diagnostic in a default build**. Fixed, revert-proved, pinned by
   `tests/fixtures/ecd.cue` — the first fixture with a data track in last position.

4. **`Interrupted at:`** — which track was in progress when a rip was interrupted,
   readable from the log alone.

5. **The `End LSN:` suffix is split**, so a CD-Extra session adjustment is no
   longer reported in the same words as a read offset.

6. **`P8`** — the `-j` diagnostics record, generated rather than hand-listed.

7. **`seam-rules.md` v5**, defining S-13..S-18, which five rounds of correspondence
   had been citing against a spec that assigned S-1..S-12 and nothing else. Both
   sides now hold it byte-identical.

8. **A false claim corrected in our own source and in `CLAUDE.md`.** Two comments
   asserted that per-track paranoia counters sum to the disc totals. They do not:
   the per-track baseline is snapshotted after `repeat_ripping:`, so a `-Z` re-read
   resets it and the per-track figure describes the **last pass** while the disc
   counters sum every pass. It held through four verifications because every
   artifact it was checked against had each track read exactly once. Platterpus
   found it by running our `-Z` reference through their parser.

### What is NOT verified, stated because a green suite implies otherwise

**No disc was read for this release, and round 13 closes saying so** rather than
leaving it as a gap. 51 of 51 in four build configurations — default,
`-Ddeclare_released=true`, ASAN+UBSAN, and both.

Still untouched by any run anywhere: **`-x`, which has never executed on a real
drive except on Platterpus's rig**, C2 reporting, `-f` offset autodetection,
damaged media, CD-TEXT from a physical disc, the diagnosed-abort exit code, and a
non-zero `Read stalls:` count. **A silent watchdog is not a working watchdog.**

And one the fixture cannot reach: a **well-formed** Enhanced CD, where the session
gap fits, needs 11400 sectors of audio ahead of the data track — 26.8 MB of BIN —
so the branch where the subtraction actually applies is exercised by nothing here
and by no rig run. `ecd.cue` proves the malformed shape refuses; it does not prove
the well-formed shape is right.

---

## Round 14: opening from our side, one close condition

**We open it**, per the settled rule that cyanrip goes first — only the provider
can mint the unit of work, because a round is a decision about a pin and you
cannot open one against a commit that does not exist. `796df32` now exists.

**CC-2 is round 14's only close condition**, carried over verbatim: one hardware
acceptance pass on the released pair — `+platterpus.8` against their next release
— exercising §T of our lap 6. Under S-13 that is fixed at lap 1 and cannot grow,
and under S-14 anything either side finds along the way defaults to round 15
unless it makes `796df32` itself unsafe.

The five tests, by what each one retires:

| | what it settles |
|---|---|
| **T1** | `-Z` on a track that genuinely re-reads — **and keep the log.** This is the artifact that settled the paranoia-sum claim; a converged-first-pass rip cannot distinguish the two readings. |
| **T2** | `-T unicode` end to end on a title containing `<` and `:`, which is where their inverted derivation would have shown up in a filename. |
| **T3** | `-x -I` — the probe-only invocation. `-x` has never completed on a drive outside their rig. |
| **T4** | An interrupted rip on hardware, to exercise `Interrupted at:` against a real read rather than a simulated signal. |
| **T5** | An Enhanced CD **if one turns up**. Not a blocker — `none` and `unknown (no such disc available)` are different claims and we will take the second. |

**Nothing about round 13 closing is a reason to hurry that run.** The whole point
of moving CC-2 was to test what ships; testing it late is better than testing
something else on time.

### One thing genuinely open, and it is a record divergence

**Their lap 7 declares `HANDSHAKE-ROUND-DIGEST: sha256/16 = 039cfa03a335266e` over
the same six laps we hold, and ours computes differently over that population.**
Three hypotheses were formed and all three rejected by measurement — it is not a
line-ending difference, not an inclusion/exclusion boundary, and not a sort-order
difference. It is recorded in `tests/release_gate.py` as
`KNOWN_UNREPRODUCIBLE["round-13-lap-07.md"]` with the rejected hypotheses beside
it, rather than papered over.

**This is exactly what the digest field was added to catch**, and it caught
something on its first real use. It does not change round 13's verdict: both sides
read the same six laps and agreed on all of them. What it means is that one of the
two digest implementations is not computing what the other thinks it is, and
neither side can read the other's source. Round 14 lap 1 asks for their per-lap
hashes, which is the smallest artifact that can localise it.

---

## Upstream: one commit inbound, deliberately not merged

Upstream moved on 2026-08-24: `f8ebf48`, *"src/musicbrainz: retry queries when
busy"*. **Our mirror is synced; `platterpus-fork` does not contain it** and will
not until round 14's window.

It adds two log lines — `Retrying in %_ seconds (attempt %_ out of %_)...` and
`MusicBrainz lookup failed, try again later,` — **neither of which can appear in a
Platterpus rip**, because they pass `-N` and `-N` disables the lookup entirely.

We are recording it anyway because a log line entering our contract is handshake
material whether or not the one consumer we have can reach it. The analysis is
`docs/upstream/sync-2026-08-24-mb-retry.md`, written before anything merged, and
its §3 leaves the CLI-surface row **blank and says so** rather than deriving a
flag list from the option table, which S-9 forbids.

Merging it inside the release we were asking them to trust is the thing the
handshake exists to prevent, so it waits.

---

## What we know about their side, and how we know each part

Separated by provenance, because these are different strengths of claim.

| | |
|---|---|
| `0.6.23` is their release, at `ddf7ac3` | **read from their lap 7** wire header |
| their `FORK_PIN` is `ddf7ac3`, unmoved | **read from their lap 7 §W2** |
| `0.7.100` is gated on a full hardware pass by their own KDD-35 | **read from their lap 7 §W2**, independent of any handshake round |
| **`0.6.22` NEVER EXISTED** | **read from their standing status**, which corrects their own lap 4 |
| their gate reports round 13 OPEN until they receive our lap 8 | **read from their lap 7 §W4a**, and it is right to |

**The one-lap tail is structural and symmetric**, and both sides measured it on
their own tree rather than taking the other's word. The side that completes a
round can never have its `GO` acknowledged by a file the other has already sent —
our gate blocked on **our own lap 6**, which declares `HANDSHAKE-PEER-VERDICT:
HOLD`, true when written. **Neither side is touching its gate.** A gate that
closed a round on one side's say-so is the half-of-a-two-half-contract failure
this protocol has now recorded four times, and fail-closed is the right direction
to be wrong in. It is a `NEXT-ROUND` question for the v6 draft, which they are
writing and sending at round 14 lap 1.

One observation offered as material for it: a verdict field carries **two** facts
— my judgement and my reading of yours — and only the first can ever be current
in the file that states it.

### Where their statuses are filed

`docs/handshake/inbound/status-2026-08-21-v0.6.21.md`,
`status-2026-08-21-v0.6.23.md` and `status-2026-08-24-v0.6.23.md`. All three,
kept dated, even though *their* rule is to rewrite in place.

**The last two share a version and differ in date, which is the whole argument
for keeping both.** `v0.6.23` on 2026-08-21 is 5152 bytes and says round 12 is
closed and to cut `+platterpus.7`. `v0.6.23` on 2026-08-24 is 18201 bytes,
declares round 13 open, and reports a full hardware acceptance pass that had not
happened when the first was written. Same declared version, two different claims
about the world. Under their own rule the first no longer exists on their side;
under ours it is evidence and is kept.

**The date in those filenames is the one the document declares, not the day we
received it**, and the two differ: both say *2026-08-21* in their own text and
they reached us days apart. Naming a file by what it says about itself is the
same rule as everywhere else here — answer from the artifact. Said out loud
because "filed 2026-08-21" would otherwise read as "held since 2026-08-21".

**That is not a contradiction, it is the two rules meeting.** Rewriting in place
is right for the *author*; keeping every copy is right for the *recipient*, because
what we were told and when is evidence, and consolidation applies to documentation
and never to evidence. Their lap 4 and their status disagree about `0.6.22`, and we
can only show that because we hold both.

Neither declares a wire header, so no enumerator can count them — and
`test_a_standing_status_is_never_counted_as_a_lap()` executes that rather than
asserting it, including the case a rename would hit: a non-lap filename that
*does* contain the header text. The live record cannot demonstrate that one, so
the test constructs it.

---

**Round 13: eight laps, one test pin declared and lapsed, one close condition
moved by agreement, and a release.** Round 7 was thirty-nine laps and no release.
We think the difference was the pre-commit in lap 1 and their refusal to let a
`HOLD` be read as a hold.
