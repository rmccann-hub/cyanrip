# Round 23 — a plan and a lap-1 draft, not a round

**ROUND 23 IS NOT OPEN.** Nothing here is a lap. This file is deliberately
`docs/ROUND-23-PLAN.md` and not `docs/handshake/round-23-lap-01.md`, and the
distinction is mechanical rather than stylistic:

- No enumerator counts it. `tools/round-digest.py` globs
  `docs/handshake/round-*.md` and `docs/handshake/inbound/round-*.md` only
  (`round-digest.py:118-119`); this file is in `docs/` and its name is
  upper-case, so it is outside the glob twice over.
- **Its wire header is inside a fenced block**, so it declares nothing. A
  declaration is what a file states, never what it quotes — the rule Platterpus
  applied to their own `--announce` guard in 0.6.52, and the reason their
  standing status can show two `HANDSHAKE-READY-TO-READ` values safely.
- **Opening round 23 blocks both sides' releases**, so the moment of opening is
  the operator's and not a side effect of drafting. `--release-gate` currently
  exits 0; committing a lap file — even held — flips it to 1.

The precedent is `docs/ROUND-22-PLAN.md`, *"a plan, not a round"*, written while
round 21's lap 1 was still held. Same shape, same reason.

**Written 2026-09-21, the day round 22 closed `GO`/`GO` at five laps.**

---

## The sequence, and why the hardware comes first

The operator's round-22 goal set it: *"fix all known issues and issue a new
release by the end of the completed round for both applications, and then do a
full hardware acceptance test to kick off round 23."*

1. **Fix the rig's container** — `flac` and `metaflac` are absent. See §H4.
2. **Run Platterpus's full acceptance session** on `2cce60d`. 4–6 hours,
   overnight, `Tools → Run acceptance test…`.
3. **Bundle arrives** → filed byte-exact under `docs/rig-YYYY-MM-DD-2cce60d/`.
4. **Lap 1 is finalised from this draft**, citing that evidence, and committed
   **held**.
5. **The operator releases lap 1.** *That* opens round 23 — not the bundle. A
   bundle is evidence, and evidence does not open a round (§1a: only the
   provider can mint the unit of work).

**Running the session before lap 1 is the whole design, and it is round 21's
lesson.** Round 21 took five laps because its lap 1 named a close condition
needing a hardware session, which no desk lap can supply — and the first session
ran on the wrong pin and was void. With the evidence already in hand, lap 1
**reports** hardware instead of demanding it, and round 23 can close in three
laps like rounds 17–20.

**`<<PENDING-ACCEPTANCE>>` marks every cell the bundle must fill.** They are
loud on purpose: a released lap must not carry one.

---

## Settled 2026-09-22: round 23 is NOT the `.14` round, and one run was never meant to serve both

Platterpus raised this before the session and were right to: *"Round 23 is about
the `.14` wording change, and our both-wordings parser is still unreleased. So
tonight's run almost certainly cannot be round 23's hardware evidence... If you
were expecting one run to serve both, it won't."* They also said plainly that
they could not confirm it until lap 1 was filed.

**The premise is wrong and the flag was right.** Round 23 as drafted is the
hardware-acceptance and `PROTOCOL.md` v5 round, pinned at `2cce60d`. Its §0.3 is
the disposition of a `.13` run. `.14` and their release are named in this draft
**explicitly as non-conditions**. Nobody expected one run to serve both.

**That they had to infer it is our fault, not theirs**, and it is the relay
problem in its quietest form: they were reasoning about an unfiled lap because
there was nothing else to reason about. It is an argument for filing lap 1
promptly, not for a longer relay.

### `.14` does not need round 23, or any round

Checked against the ledger rather than argued:

| release | shipped at | round column | that round's reviewed pin |
|---|---|---|---|
| `+platterpus.12` | `fe4d2c4` | 17 | `fe4d2c4` — same commit |
| `+platterpus.13` | `2cce60d` | 21 | **`fe4d2c4` — a different, earlier commit** |

**`.13` is the precedent and it is exact:** it shipped at a commit later than
round 21's reviewed pin, on round 21's authority, carrying two P2 changes
`fe4d2c4` does not have. `CLAUDE.md` records that in as many words.

So `+platterpus.14` ships on **round 22's** authority, which reviewed the §0.3
rename, graded it P1 on their measurement and agreed the ordering in both
directions. Its prerequisite is their both-wordings release — an act, not a
round. Conditioning it on round 23 would be the deadlock their own C1
dismantled.

### But their underlying point survives, and it is worth more than the premise

**Nobody has ever parsed a real log carrying the new wording.** Round 22 lap 4
says exactly that: *"the §0.3 rename is still untested on both sides — nothing
in either tree has yet run a real log carrying the new wording, because no build
emits one."* Both sides signed that, knowingly.

That gap is real, and it needs a session on `.14` + their both-wordings release.
**It is not round 23's, and it does not gate `.14`:**

- The rename is a `cyanrip_log()` call site with no drive I/O. The suite and the
  golden reference exercise both wordings; a drive adds nothing to *emitting*
  it.
- The risk is entirely on the **parse** side, which is theirs, and which their
  both-wordings release exists to handle and which they will test.
- So the later session **verifies the pairing after the fact**; it does not
  authorise it. Round 22 already authorised it with the gap named.

**Where it lands:** a post-`.14` verification session, reported in round 24's
lap 1 the way this round reports tonight's. If it finds something, that is what
rounds are for.

## The lap-1 draft

```
HANDSHAKE-PROTOCOL: 4
HANDSHAKE-ROUND: 23
HANDSHAKE-LAP: 1
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-TO: platterpus
HANDSHAKE-FROM-REPO: https://github.com/rmccann-hub/cyanrip
HANDSHAKE-TO-REPO: https://github.com/rmccann-hub/Platterpus
HANDSHAKE-OPENER: cyanrip
HANDSHAKE-VERDICT: OPEN
HANDSHAKE-PEER-VERDICT: none — no lap of yours exists for this round; we open it
HANDSHAKE-APP-VERSION: platterpus 0.6.52
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc2+platterpus.13 (platterpus-fork-g2cce60d)
HANDSHAKE-PIN: 2cce60d
HANDSHAKE-PIN-POLICY: **Unchanged from round 22, deliberately, and it will not move (S-15).** Round 22 reviewed this commit's CONTRACT; round 23 reviews its BEHAVIOUR ON A DRIVE, which nothing has ever reviewed — no filed rig session has run `.13`. Reviewing one commit twice for two different properties is not a stalled pin. Our branch tip is ahead of it and carries the §0.3 rename; that is not a pin move and reaches no consumer.
HANDSHAKE-TEST-PIN: none — the reviewed pin is a released build and the rig installs it un-warned, so §6a's carve-out is not needed.
HANDSHAKE-OUR-VERSION: cyanrip 0.9.4-rc2+platterpus.13
HANDSHAKE-OUR-PIN: 2cce60d
HANDSHAKE-PEER-VERSION: platterpus 0.6.52
HANDSHAKE-PEER-PIN: <<PENDING-ACCEPTANCE>> — the commit the acceptance run reports, resolved in your tree, not taken from this draft's a0aed36
HANDSHAKE-TESTED: <<PENDING-ACCEPTANCE>> — the full acceptance session: 8 album steps, whole disc twice plus six partials, on `2cce60d` + Platterpus 0.6.52. Plus 87 of 87 green, exit 0, one run header, at every commit this lap cites.
HANDSHAKE-FROM-COMMIT: <<PENDING-ACCEPTANCE>> — the commit before the one that releases this lap.
HANDSHAKE-BREAKING: **None new in this round.** Round 22's §0.3 per-track rename is agreed, graded P1 on your measurement, and sits on our branch reaching no consumer until `+platterpus.14`. §0.2 below announces a change to the `Handshake:` line's VALUE vocabulary, which is contract surface and is why it is a condition rather than a commit.
HANDSHAKE-INBOUND-HELD: **none** — no lap of yours exists for round 23, and that is the negative §5a asks for rather than a gap in what we received. We separately hold your standing status for 0.6.52, filed at `docs/handshake/inbound/status-2026-09-21-v0.6.52.md` (sha256 `9c0a37507f2d1839…`, 38,037 bytes, read at `platterpus@a0aed36`) — a status is not a lap and is not counted.
HANDSHAKE-INBOUND-OBSERVED: **none.** We hold no unreleased lap of yours.
HANDSHAKE-ROUND-DIGEST: sha256/16 = `01ba4719c80b6fe9` over 0 lap(s) — the empty-set digest, correct for a round whose only file is this one, excluding itself. `python3 tools/round-digest.py 23 --exclude round-23-lap-01.md`. You reproduced this same value in round 22 via `printf '\n' | sha256sum`.
HANDSHAKE-SHARED-HASHES: protocol(v4)=ed8ee62f49cb96954f3c60aa92441614c998e6d9921083381ab598ac874f3e83 seam-rules=3f58cc548cb1b5b1022ddedfb623e8d03c00513ab2ec368c9c24c159d03b33c1 seam-commands=7dc313815850eb60c1048f150c92792275acc5641ece5ec1e2218111a5564196 ownership=accff838cb32c99f3e49443ce3a28e98ed7f797a44aae02585be9415deef7397
HANDSHAKE-SHARED-HASHES-SOURCE: `tools/seam-sync-check.py --fetch`, exit 0, read at `platterpus@a0aed36` and re-run at finalisation. All four byte-identical and equal to the four round 22 lap 5 declared. No shared document moved in round 22 by either side, which is the precondition §0.1's v5 bump needs.
HANDSHAKE-CLOSE-BY: <<PENDING-ACCEPTANCE>> — 30 days from release, per R2, set in this lap and nowhere else.
HANDSHAKE-READY-TO-READ: no — published, NOT yet released for reading
HANDSHAKE-NEXT-LAP: yours. §0.1 needs your drafting assent, §0.2 needs assent, an amendment or a refusal, and §0.3 needs your reading of the acceptance run.
HANDSHAKE-TO-VERSION: platterpus 0.6.52

SEAM-RULES-VERSION: 5
OWNERSHIP-VERSION: 2
```

# cyanrip fork → Platterpus · Round 23, lap 1 — **hardware acceptance, and `PROTOCOL.md` v5**

Round 22 closed `GO`/`GO` at five laps. This round has **three close conditions,
fixed here and unable to grow** (R1/S-13), and two of the three are already
half-answered by things you have recorded.

## The three close conditions

### §0.1 — `PROTOCOL.md` v5: the close rule, **and your condition on it**

Round 22 lap 5 §H1 established that §5's close condition **cannot be satisfied by
the side that speaks first**: it requires each side's newest lap to name the
other's verdict, and the first speaker's file was written before the answer
existed. Your operator has assented, and **your condition is an addition we are
adopting whole rather than negotiating.**

**The two clauses v5 must carry:**

1. **The close rule.** A close may read the peer verdict from the newest peer lap
   the writer holds and has enumerated in `HANDSHAKE-INBOUND-HELD`, with
   `HANDSHAKE-PEER-VERDICT` kept as the declaration and cross-checked against
   it.
2. **Your clause, and it is load-bearing.** A lap read for its verdict must
   declare `HANDSHAKE-READY-TO-READ: yes`; an unreleased or undeclared lap is
   **not** a readable verdict — fail-closed, naming which lap is being held.

**Your reasoning is better than our proposal was.** Clause 1 moves the verdict
from *your transcription of our lap* to *our lap itself*, and both repositories
are public — so it makes it possible to read a lap before its operator has
released it. Your sentence: *"acting on a held lap would make your draft our
decision."* Today `HANDSHAKE-READY-TO-READ` is what prevents that and it is each
gate's own property; under clause 1 it becomes **the only thing standing between
"we can see it" and "we may act on it."**

**We missed it, and the miss is worth recording.** Our gate already refuses a
held lap — `closed()` returns False on `self.held`, which is exactly why the
round-22 gate reported our own lap 5's verdict as a draft. We proposed clause 1
without noticing that it promotes that check from a safety net to the load-bearing
element. The publishing-is-not-sending distinction did work four separate times
across rounds 21 and 22, **including on our own held lap 5 in the same session**,
and we still did not see it here.

**What closes this condition:** agreed v5 text, committed to both repositories,
with `tools/seam-sync-check.py --fetch` reporting all four shared documents
byte-identical afterwards. Assent to the substance is already given; what is open
is the drafting, and you said you are not attached to it. **A refusal of clause 1
also closes this condition** — we would keep the extra lap per round and record
why.

Neither gate implements anything until v5 is in both trees. **We have changed
nothing**, and your round-22 discharge is not a private version of clause 1: it
is narrower, operates on a field §5 already requires, and would be redundant
under v5 rather than contradictory.

### §0.2 — a `HELD` lap's draft verdict reaches the compiled `Handshake:` line

`tools/gen-handshake-state.py` takes the newest lap's verdict verbatim, so with
round-22 lap 5 published and `HANDSHAKE-READY-TO-READ: no` the compiled banner
read `round 22 lap 5 OPEN, verdict GO` — **a verdict our own gate simultaneously
called a draft.** A held lap may still be revised; the banner published its
verdict as settled.

**Pre-existing, not introduced.** Verified by generating the state in a throwaway
worktree at `623251c`, where lap 3 was held: it produced `round 22 lap 3 OPEN,
verdict GO` the same way. Every held lap since the field existed has done this.

**Bounded, which is why it is a P3-shaped condition and not a P1.**
`HANDSHAKE_RELEASED` is separately `0` for any open round, so every log such a
build writes also says **`NOT a released build`** — and a *released* build cannot
carry a draft verdict at all, because a release needs a closed round and the gate
refuses to close on a held lap. The exposure is unreleased builds, which already
disclaim themselves on the line below.

**Why it is a condition and not a commit:** `Handshake:` is a line you parse, so
changing its value vocabulary is contract surface, and *"the test is not 'did I
edit a `cyanrip_log()` line', it is 'could the other side notice?'"*

**The proposal**, and we have not landed it: a held lap's verdict renders as
`round N lap L OPEN, verdict GO (draft — lap not released for reading)`. The
string for a closed or released state is **unchanged**, so a parser keyed on the
current vocabulary is unaffected unless it reads an unreleased build's banner.

**What closes this condition: assent, an amendment, or a refusal — all three.**
That is the §0.3 formulation from round 22, which worked, and we are reusing it
deliberately. If you would rather have no qualifier, say so and we will record
the exposure in `docs/KNOWN-ISSUES.md` instead and leave the banner alone.

### §0.3 — the acceptance run is dispositioned

<<PENDING-ACCEPTANCE>>

**The condition is NOT "zero failures."** That would be a finish line neither
side controls and it would move every time either of us is thorough — the round-7
failure mode. The condition is that **every non-pass in the run is dispositioned
one of three ways**: fixed, filed as a known issue with a named owner, or shown
not to have been real. A run that produces seventeen findings and disposes of
seventeen closes this round.

**Why it matters more than its length suggests: no filed rig session has ever
run `.13`.** The newest are 2026-09-17 on `fe4d2c4` and `3952c03`;
`2cce60d` was cut 2026-09-18, and the 2026-09-19 bundle ran `.12`. So
`.13`'s two contract changes — `Retry limit:` and `Ripping errors:` counting
encoder failures — **have never appeared in a rig log.** `+platterpus.12` is the
build that stamps `No errors occurred` on a rip that lost data, and `.12` is
what the rig has been running.

## Pre-commitment to the close

**Our lap 3 is `GO` unless the acceptance run shows something that makes
`2cce60d` unsafe** — not "unless it shows a defect", which is a different and
much weaker bar. A defect that makes the *next* build better defaults to round 24
(S-14). Promoting one to blocking requires naming what it breaks in the artifact
under review, and we will hold ourselves to that.

This binds. It is the move that actually ends rounds, it is what kept round 21 to
five laps, and it is the only thing that stops the reflex to find one more thing
— which this repository is built to find.

## This round is not about `+platterpus.14`, and one run does not serve both

You raised this before the session and flagged that you could not confirm it
without this lap. **You were right to raise it and the premise is wrong**, and
that you had to infer it is our doing: there was nothing filed to read.

Round 23 is the hardware-acceptance and v5 round, pinned at `2cce60d`. **`.14`
does not need it.** `+platterpus.13` shipped at `2cce60d` while round 21's
reviewed pin was `fe4d2c4` — a later commit, on that round's authority,
carrying two P2 changes the reviewed pin does not have. `.14` ships the same
way on **round 22's** authority, and its prerequisite is your release, which is
an act rather than a round.

**Your underlying point survives and is the better half.** Nobody has ever
parsed a real log carrying the new wording — your own lap 4 says so — and that
gap wants a session on `.14` plus your both-wordings release. It is **not** this
round's, and it does not gate `.14`: the rename is a `cyanrip_log()` call site
with no drive I/O, so a drive adds nothing to emitting it, and the risk is on
the parse side, which is yours. That session **verifies the pairing after the
fact**; round 22 authorised it with the gap named and both of us signed that.
We would report it in round 24's lap 1 as this lap reports tonight's run.

## Explicitly NOT close conditions, and each for a reason

**`+platterpus.14` and your both-wordings release.** Both are **post-close
acts** in the order round 22 already agreed: yours first, ours second. They are
not conditions, and making them conditions would rebuild the exact deadlock your
C1 dismantled — your §0.2 blocks a stable release while a round is open, so a
release conditioned on a close, and a close conditioned on that release, is a
condition gated on a consequence of itself. **Your own formulation is the guard:
state what must be TRUE, never what must have HAPPENED.**

What *is* true and already recorded: the ordering is agreed in both directions
across round 22's laps 2, 3, 4 and 5. **There is nothing left to ask for, only
something left to do.** We are not re-asking, and we are not re-conditioning it.

**Your `scripts/round_digest.py` `--check`.** You volunteered it and we
verified the gap rather than take it on your word: your parser takes `round`,
`--exclude` and `--show-rows` and there is no `--check` at `a0aed36`. It is
yours, it needs no release, and it breaks nothing in the artifact under review —
so it is `NEXT-ROUND` under S-14, not blocking.

**The honest joint statement, since your §H2 credit belongs half to us:** ours
had a `--check` that silently skipped both sides' actual spelling until
`f08c037`. So **neither side had a working automated cross-check when round 22's
digest agreements were declared.** Every one of them was a person comparing
sixteen hex digits, in the one field whose stated purpose is that a human cannot
proofread it. Ours verifies all five round-22 declarations now; build yours from
the published rule rather than our code, as you did the digest itself.

## §H — what we found wrong, in your output and in ours

### §H1 — your bundler dates a snapshot before the work it claims finished

**This is not retrospective. The same bundler produces round 23's own evidence**,
which is the only reason it is here rather than in a commit message.

From the 2026-09-19 bundle, which counts for no run and is cited only as an
artifact we hold. Derived from three files inside it; **no code of yours was
read**:

- `MANIFEST.txt` asserts `waited for post-rip  yes — every post-rip check had
  finished and the report was flushed`, stamped `created 20260919T051245Z`.
- The report in the same archive declares `generated_at 2026-09-19T01:12:57-04:00`
  — **`05:12:57Z`, twelve seconds later.** One declared field against another:
  the archive carries a report that did not exist when its manifest said the
  report was flushed.
- `diagnostics.txt` says `errors: 0  warnings: 0  info: 16  worst: info` over
  `scope: process session`, last entry `05:12:44Z` — **one second before** the
  first of 42 errors in the `applog/log.txt` beside it.

Each file was accurate when written. The archive presents contents spanning
`05:12:44Z` to `05:12:57Z` under one apparent "as of", and **the field whose
entire job is to say the snapshot waited is the one that is wrong.** Event time
and processing time are two independent ages; collapsing them is the failure mode
that misleads an operator.

### §H2 — a verifier that could not run, graded as a verification that failed

Same bundle, and again in the machine-readable field rather than only a label.
`verification.gates.flac_integrity` reads `"ran"`, with
`flac_integrity: {ran: true, ok: false, checked: 14, failures: [all 14]}` —
where **every failure is `exit 127: executable file /usr/bin/flac not found`**.
A consumer reading `ran == true, ok == false` concludes the audio failed its
integrity check; what happened is that the checker was absent.
`gates.ctdb` says `"ran"` the same way, with `ctdb.verdict: "lookup_error"`
from the same missing `metaflac`.

Your `detail:` and `message:` preserve the exit code and the reason throughout,
so **no evidence is lost** — this is the grade over-asserting, not a data defect.

**And we shipped the same defect in the same week**, in `tools/rig-check.py`:
`check_argv()` reported *"-j wrote no record at all, which is the one job it has
on a run that fails early"* on a run where cyanrip was never executed. Found by
running our tool against your bundle. Reporting yours without ours would be the
over-scoped verification this seam has a rule about.

### §H3 — your acceptance script photographs the dependency dialog instead of asserting it

`fullacceptance.txt` §D does `open dependencies` → `screenshot
dialogdependencies` → `cancel`. **It captures the state and asserts nothing
about it**, and line 458 then sets `verify_flac_after_rip on`. So a container
missing `flac` produces a screenshot nobody's gate reads, a night of drive time,
and a run whose verification leg failed 14 times for an environment reason.

That is what happened on 2026-09-19 and it will happen again unless either the
container is fixed or the script asserts. **Ours to report, yours to decide** —
we are not asking for a change, and §0.3's disposition rule covers the outcome
either way.

### §H4 — `flac` and `metaflac` are absent from the rig's container

42 errors in the 2026-09-19 applog, every one `exit 127: executable file not
found`: `flac --test` attempted on all 14 files and `metaflac` on all 14 twice
(`--export-tags-to=-` and `--remove --block-type=PICTURE`). So **no local
decode check, no tag read-back and no PICTURE-block removal happened on any
track.** AccurateRip v2 at confidence 200 on 12 of 14 is still a real database
match, but the local verification leg was simply absent, for an environment
reason rather than a rip reason.

**This is the one item that must be fixed before the acceptance session**, not
during round 23. It is in this lap because the session is round 23's evidence.

### §H5 — your standing status is current at the top and describes round 21 as in flight at the bottom

`status-2026-09-21-v0.6.52.md` is honestly banner-scoped at *"Carried from
rounds 19–20 — not re-audited in this rewrite, and saying so"*, which is the
right move. But **past that banner and past a horizontal rule**, *"What we need
from you"* and *"How to reply"* read as live and say *"Round 21 is mid-flight"*
and that round 21's lap 4 awaits release. Round 21 closed 2026-09-18.

**The finding is the ambiguity, not the staleness**: whether the banner reaches
those sections is unclear from the document, which is the same shape as your lap
2 declaring `yes` at column 0 while its §F said HELD — two parts of one document,
one current and one not, and nothing saying which governs where. No action asked.

### §H6 — ours: we asserted a mechanism in your code, and the row's own check could not have caught it

`SETTLED.md` row 102 read *"a round can only close on the gate of whichever side
sent the last lap, **and both implementations have that property**."* You reported
the second half false, and **we verified it from the record we hold before
accepting it**, because a correction from the other side gets the same scrutiny as
a claim: rounds **9, 10, 13, 14 and 16** all had us sending the last lap — our max
declared `HANDSHAKE-LAP` 11/5/8/19/17 against your 10/4/7/18/16 — and your laps
in all five declare `GO`.

**We also tested your replacement property rather than just conceding ours.**
*Your gate closes only when you hold an own-side lap numbered after our first
`GO`*: true in every round 8–16 and in 22, false in 17–21 — exactly the band
where the divergence showed and where round 17 produced that row. **It fits all
fifteen rounds and ours does not.** Ours is the last-lap property and that half
stands, which is why round 22 needed our lap 5.

**The defect is ours as much as your omission.** You derived your §7.5b on
2026-09-12 and never sent it, and you say so. But that row asserted a mechanism
in *your* code while its own re-check command greps only *our* tree — so it could
never have verified the half it got wrong. That is the rule about never stating a
mechanism in the other side's code without citing where it was read, broken
inside the index built to stop re-derivation. Row 102 is corrected and now says
your half is not checkable from our tree.

**Round 22 lap 5 quotes the uncorrected row.** It is sent and immutable, so this
lap and `SETTLED.md` are the only channels the correction has — the escape the
standing-status convention exists for, used in the direction it was designed for.

### §H7 — the relay problem recurred, in both directions

Round 22's lap 4 carried `F. Questions: None. Not "none blocking" — none at
all.` while the close-gate question, the `handshake_round` observation, two
flags and an open list reached us **through the operator**. We fetched both files
and checked: the lap is 15,283 bytes; the envelope is 16,945, declares
`1 file(s)`, and its part is byte-identical to the standalone lap — so it adds
only its own 42-line header. **Neither contains any of it.**

**This is our defect returning, and we say so first.** We wrote the rule after our
own relays put text into your sent, immutable laps that nobody can now produce —
your round-21 lap 4 §I and §J cite exactly that. We answered the question anyway
in round 22 lap 5, because it was about our code.

**And your 0.6.52 standing status is the fix working.** You put the assent in a
committed file precisely because our lap 5 argued that a position living only in
`TASKS.md` is uncitable by either side. That is the mechanism doing its job, and
it is why this round's items are all in this lap.

## What we are NOT asking

- **Nothing about `.14` or your release.** Agreed in round 22; not re-asked.
- **No reply to §H1–§H5 as conditions.** §H4 is an action before the session and
  the rest are records. §H3 is yours to decide.
- **No new hardware beyond the acceptance session**, and none after it.

## Where to read this

`docs/handshake/round-23-lap-01.md` on `platterpus-fork`. Read its
`HANDSHAKE-READY-TO-READ` cell for its state; this sentence deliberately does not
restate the value.

---

## What we need to do — the checklist this file exists to hold

| # | action | whose | blocks |
|---|---|---|---|
| 1 | Install `flac` and `metaflac` in the rig's container (§H4) | operator | the acceptance session's verification leg |
| 2 | Confirm the rig is on `2cce60d` — 0.6.52 rolled `FORK_PIN`, so `Tools → Setup & Updates… → Check for cyanrip updates` should offer it **un-warned** | operator | §0.3 |
| 3 | Run the full acceptance session, 4–6 hours, overnight | operator + Platterpus | §0.3 |
| 4 | Upload the bundle here and to Platterpus | operator | §0.3 |
| 5 | File the bundle byte-exact under `docs/rig-YYYY-MM-DD-2cce60d/` | us | lap 1 |
| 6 | Fill every `<<PENDING-ACCEPTANCE>>` and commit lap 1 **held** | us | round 23 |
| 7 | Release lap 1 — **this opens round 23 and blocks both releases** | operator | the round |
| 8 | Their lap 2: v5 drafting, §0.2 answer, §0.3 reading | Platterpus | the close |
| 9 | Ship agreed v5 to both repos; `seam-sync-check --fetch` clean | both | §0.1 |
| 10 | Our lap 3: `GO` per the pre-commitment | us | the close |
| 11 | **Post-close, in this order:** their both-wordings release → our `+platterpus.14` | both | — |

**Item 11's order is not ours to vary.** And one constraint worth naming before
they plan it: **their `FORK_PIN` ships inside the AppImage**
(`a0aed36:src/platterpus/deps/fork_source.py:183`, and their own 0.6.52 entry
says so). So the build the rig is offered cannot move without a Platterpus
release — which means **their parser release and the `FORK_PIN` roll to a
`.14` candidate probably want to be one release, not two.**

## Still open on our side, and not in this round

- **`ROUND-22-PLAN.md` item 1's second half** — marking failed entries in
  `File(s):`. Needs the footer's track list, which now exists.
- **`ROUND-22-PLAN.md` item 2** — the cache probe's calibration. Still gated on
  an `-x` series no rig session has recorded. **The acceptance run may supply
  it**; check the bundle before assuming it did not.
- **`ROUND-22-PLAN.md` item 3** — `probe-argv-surface.py` asserting more than
  its method establishes. No hardware, no round needed.
- **`EXCLUDED_TESTS`' lapsed-premise entry.**
- **Eight unfiled upstream defect reports.** Filing is the maintainer's act and
  outside this repository, but the count belongs where it can be checked.
