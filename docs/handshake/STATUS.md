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

## Rewritten 2026-08-25. **Round 13 CLOSED. Round 14 OPEN. `+platterpus.10` is the build to test.**

Round 13 closed `GO`/`GO` on `9f8592e` in eight laps. Round 14 is open with one
close condition — a hardware acceptance pass — and
**`0.9.4-rc2+platterpus.10` at `d9c058c` is the build it is about.**

**Three betas in two days, and the last of them.** `+platterpus.8`, `.9` and
`.10` were cut in quick succession as the acceptance plan came together, and each
one invalidated a build-tag assertion in the script Platterpus had already
written. **That churn is ours and it stops here:**

> **Pre-commit, and it binds: no further release until round 14 closes or the
> acceptance pass reports.** `d9c058c` is what the pass runs against.

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
| **beta version** | `0.9.4-rc2+platterpus.10` |
| **beta commit** | **`d9c058c`** |
| beta build tag | `platterpus-fork-gd9c058c` |
| beta install | `https://github.com/rmccann-hub/cyanrip/archive/d9c058c.tar.gz` |
| beta `release_seq` | 20 |
| beta authorised by | **nothing yet — handshake round 14 is OPEN** |

**`+platterpus.8` (`796df32`, seq 18) is superseded and should not be installed.**
It is still in the ledger, because the ledger is append-only and a published
build is a fact, but no channel resolves to it any more.

Build command for either: `meson setup build -Ddeclare_released=true && ninja -C build`.

`release-manifest.json` is the only mechanism to install from and it is what
resolves these; this table is a human-readable copy of it and the test exists
because a copy rots.

### Why beta — read this before pinning anything

**`+platterpus.10` has not been verified by anyone but us, and it was cut while
round 14 was open.** Both facts are stated here because neither is visible from
the version number.

**The first two of the three were the CC-2 repair applied again; the third was
not, and the difference is worth keeping.**
Round 13's original close condition measured a *test pin* while the release would
necessarily be a later commit — so satisfying it would still have left the
released pair with no hardware evidence. It was moved to round 14 by bilateral
agreement (our lap 6 §N1, their lap 7 §W1) precisely so the pass would test **the
build that ships**. Then four fixes landed after `796df32` was cut, and testing
`796df32` would have meant testing something nobody would install — the same gap,
one release later. So the release moved to match the fixes, rather than the test
being pointed at a stale build.

**`+platterpus.10` had a different reason**, and a weaker one: no fix landed
after `f2c0506` — only correspondence. What moved was the compiled-in handshake
state, which is a real part of an archival record but is not a defect being
fixed. Distinguishing the two is why the pre-commit above exists: the first two
releases had to happen, the third was a judgement call, and a fourth would be
churn.

**Round 14's pin therefore moved, twice, and now rests at `d9c058c`.** That is a
departure from S-15, which freezes a pin for the duration of a round, and it is
declared as one rather than smuggled — our round-14 lap 2 and lap 3 both say so
at column 0. The maintainer instructed it, both projects are cutting fresh
releases, and the alternative was a hardware pass on a build no consumer would
ever install. **It does not move again.**

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
`+platterpus.10` and can never move a user backwards.

**Their `FORK_PIN` stays at `ddf7ac3` and we are not asking them to move it.**
Their lap 7 §W2 is right that a pin they have not run on hardware is a pin they
do not claim, and their bar and ours agree here.

**A consequence they found and own:** a user who opts into `beta` gets
`unapproved` in their archival record, and their §W3 identifies that as
overstating — the true statement is *"jointly verified, no hardware evidence
yet"*, which is the same missing state their §J1 hit in the verdict vocabulary a
week earlier. Two vocabularies, one absent value, discovered independently. That
is theirs to fix and they have not asked us for anything.

### What `+platterpus.10` adds on top of `+platterpus.9`

**Nothing in `src/`, and nothing a rip can observe.** The one substantive change
is the **compiled-in handshake state**: `+platterpus.9` stamps `round 14 lap 1
OPEN, verdict OPEN` into every logfile, which was two laps stale by the time the
acceptance plan was reviewed. This build stamps `round 14 lap 3 OPEN, verdict
HOLD`.

That is worth a release because the pass's logs are **archival records of a
measurement nobody repeats**, and the round they name is part of the record.

It also carries round 14 laps 2 and 3 — the pin reconciliation, the review of
Platterpus's acceptance plan against the seven questions we published in advance,
and the identification that **round 13's lap 8 had never been delivered**, which
is why their gate was correctly holding round 13 open.

### What `+platterpus.9` added on top of `+platterpus.8`

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

## Round 14: eleven laps in, one close condition, waiting on a disc

**We opened it**, per the settled rule that cyanrip goes first — only the
provider can mint the unit of work, because a round is a decision about a pin and
you cannot open one against a commit that does not exist.

**The pin moved once, at lap 2, and has not moved since.** `796df32` →
`f2c0506` → **`d9c058c`**, each declared as an S-15 departure rather than
smuggled, and frozen from lap 5 on. **`0.9.4-rc2+platterpus.10` at `d9c058c` is
what the pass runs against**, alongside **platterpus 0.6.26** — their lap 10 §D
declines to ship a new app build for the same S-15 reason, so the rerun measures
the pair both sides agreed on rather than a fresher one.

**CC-2 is round 14's only close condition**, carried over verbatim: one hardware
acceptance pass on the released pair, exercising §T of our lap 6. Under S-13 that
is fixed at lap 1 and cannot grow, and under S-14 anything either side finds
along the way defaults to round 15 unless it makes `d9c058c` itself unsafe.

**Both sides have pre-committed to the close.** Ours: the next lap is `GO` unless
the rerun fails on a cause that is ours. Theirs: the same. **The only thing
between this round and a close is running the disc.**

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

**Where the five stand:** T1 is the queued rerun and is the one the close waits
on. T3 is owed the acceptance bundle by their own operator, not by us. T2, T4 and
T5 are unreported.

### What the eleven laps produced, since a round this long invites the question

**Four defects found and fixed**, three of them theirs; **two claims withdrawn**,
one from each side; and **one defect still open** — C1, below, which is ours.

 - **C2 — a cancelled rip's log never got its completion footer.** Ours.
   `cyanrip_log_finish_report()` sat above the `end:` label and **24 `goto end`
   sites skipped it**, so `Interrupted at:` — the feature `+platterpus.8` shipped
   for their round-12 ask — was unreachable in practice. Fixed at lap 7, with a
   third state for `Rip completed:` so an abort is distinguishable from a
   completed rip and from a signalled one. **Not in `d9c058c`**; it ships after
   the round closes.
 - **Two SIGTERMs, 0.445 ms apart.** Theirs, confirmed by measurement in their
   lap 10 after our lap 9 §D named `_exit(1)` as the only path in our code
   fitting all four rig observations. Their reap sent a redundant second signal;
   their comment reasoned about idempotence at the wrong layer.
 - **A read loop that dropped the first line after a cancel.** Theirs. It is why
   `Trying to quit` never appeared in the capture — **and it is what makes our
   lap 9 §B wrong**: we concluded our handler had not run, from an absence in a
   capture whose retention we had never established.
 - **A support-set lookup miss that went quiet on the pin under review.** Theirs.
   Their `--verify-log` tri-state read `not_determined` on `d9c058c` whatever the
   log contained, which degraded the rerun's own evidence.

**Two withdrawn claims, one each.** Ours is lap 9 §B, above. Theirs is the lap 5
diagnosis that our §B2 footer defect explained the rig's cancelled rip — our own
revert-proof showed that defect leaves the FUN512 *present* and the rig's rip had
none, so different symptom, different cause.

### One thing still open: **C1, the 30-minute hang. Cause NOT determined**

A run with no `-s` hits our offset refusal. On the rig it wrote its `-j` record
**fourteen seconds in, from `atexit`** — so the process decided to fail, ran its
exit path to completion, and **then stayed alive for roughly thirty more
minutes** with the drive held, needing SIGKILL.

Two of the three observations are now explained and neither is the defect:

 - *"SIGTERM did not land"* is **our documented behaviour**. `signal()` appears at
   exactly one site in all of `src/`, installing our handler for `SIGINT` and
   `SIGTERM`, and nothing restores either disposition. **A single SIGTERM has not
   been able to terminate cyanrip since `+platterpus.7`** — an unstated cost of
   the fix we shipped for their ask 1, because once the rip loop is behind us
   nothing reads the quit flag again.
 - *The 0-byte stdout capture* is a measurement of the capture, not of cyanrip.
   `crip_diag_record()` has one call site, at the top of `cyanrip_vlog()`, which
   ends `vprintf` + `fflush(stdout)` unconditionally — so the four messages in
   the `-j` record **are** proof that 174 bytes reached fd 1 and were flushed.
   The tarball's own mtimes show the capture file stamped at the second the step
   began and never written to again.

**What remains unexplained is the thirty minutes**, and it is ours. It is
unreachable from every fixture either project has — the refusal is gated on a
**drive capability** image drivers do not report — so it cannot be bisected
without hardware. Lap 11 asks for a bounded 90-second rerun of that step plus
`/proc/<pid>/wchan` while it hangs, which is one word and would end it.

**It does not block the rerun**: `securereread.txt` passes `-s 667`, so it cannot
reach the offset refusal at all.


### The digest divergence — **round 14's now agrees; round 13's is still unreproduced**

**Round 14 lap 10 declares `dde21d98d1159ec6 over 10 lap(s)` and ours computes
byte-identically over that population.** Two independent implementations of one
convention agreeing on a value neither side computed for the other, which is the
only evidence there is that the loaders have not drifted. It took until lap 10
because the population had to converge first — each side was missing one of the
other's laps, and both `HANDSHAKE-INBOUND-HELD` fields said so.

**Round 13's remains open and is recorded rather than papered over.**

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
