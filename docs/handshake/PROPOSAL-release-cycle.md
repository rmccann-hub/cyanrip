# Proposal: one cycle for both repositories — release, run, round

*Proposed by cyanrip in round 30 lap 1, at the operator's request of
2026-09-30. **A proposal, not protocol.** It would change shared rules — v6
§6a-bis R8 and R9 in `PROTOCOL.md`, and the standing-status convention both
sides use — so nothing here binds until both sides have answered it and the
agreed text has landed in both trees. **Every decision is numbered so a lap can
answer it by number**: ACCEPT, AMEND with your text, or REFUSE with the reason.
The operator decides the four items in §5, and may overrule anything else.*

## 1. What the operator asked

In the operator's words, 2026-09-30:

> *"i dont want to waste 6 hour tests on old versions. we can always do a test
> and then just do a round to make "accepted" vs "unaccepted" if needed"*

> *"number of laps matter too. they code tokens. […] they just all need to line
> up. what is most effiecient? also, all rounds should try and fix and known and
> fixable problems within that rounds, not push off to next, and communication
> to the other repo should likely be better as to status, issues, what we are
> moving to which lap and round and why, so they can chime in. this is for both
> repos"*

> *"6 hour tests cost me night compute time, so nothing: is what i meant"*

> *"include all this as a decision to come to a consus with for them, and me for
> that matter. make them do work as well. then both converge"*

> *"just because you get a lap answer doesn't mean you can't push back and get
> more reasoning or an explanation or another answer. This is the point of laps.
> Not to use the least amount but the have full explainations before finishing a
> round."* — added after round 30 lap 1 was sent, which pins this document at
> `5c92fc2`, where the bullet below read *"Laps are the cost"*.

So the cost model is:
- **Wasted laps are the cost; explanation is not.** A lap is tokens, and one
  that only acknowledges, transcribes, crosses another or answers a stale pair
  buys nothing. **A lap that pushes back, or asks for the reasoning behind an
  answer, is what laps are for**, and a round closes when both sides can say
  why, not in the fewest laps.
- **Runs are free**, since they use the operator's night, but each must test
  the newest pair. A run on a pair that is already superseded wastes the night
  it used.
- **Every fixable problem is fixed in the round that finds it.**
- **Where things stand is visible to both sides without a lap.**

## 2. What the record shows

Measured 2026-09-30 from cyanrip's tree at `906d27f`: every lap file of both
sides we hold, and every rig session filed under `docs/rig-*`. **These are one
side's counts. W1 below asks Platterpus for their own.**

**Laps per round**: the highest `HANDSHAKE-LAP` either side declared, and the
bytes of every lap file of both sides.

| round | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 |
|---|---|---|---|---|---|---|---|---|---|
| laps | 5 | 5 | 5 | 3 | 5 | 6 | 6 | 9 | 4 |
| bytes | 150,418 | 93,224 | 91,144 | 46,210 | 81,806 | 67,959 | 79,429 | 147,026 | 75,231 |

That is 832 KB across nine rounds. **Rounds 26 to 29 all opened before their
run**, by the operator's override of R8 point 3. Filed before the round's Full
run began: 2 of round 26's 6 laps, 3 of round 27's 6, 5 of round 28's 9 and 2
of round 29's 4, so 12 of 25. Round 28's laps 6 and 7 were also written before
either side held that run's bundle, which makes 14.

**Full runs since R8 was adopted on 2026-09-23**, from each session's own
`script-report.json`:

| run began (UTC) | pair | steps | what it counted for |
|---|---|---|---|
| 09-24 01:14 | `.15` · 0.6.55 | 258 pass, 3 fail | round 26's run |
| 09-26 00:04 | `.16` · 0.6.60, **Quick** | 206 pass, 114 skipped | round 27 closed on it, by override. Not evidence by its own report |
| 09-26 04:13 | `.16` · 0.6.60 | 320 pass | **No close.** Round 27's closing lap, our lap 6, was committed 17 minutes after it began |
| 09-28 01:48 | `.17` · 0.6.61 | 320 pass | round 28's run |
| 09-28 14:42 | `.17` · 0.6.62 | 320 pass | **Nothing.** Round 28's close was moved onto it and then back. `.18` was published at 17:32, while it ran, so it could not be round 29's run either |
| 09-28 22:33 | `.18` · 0.6.63 | 320 pass, 3 fail | round 29's run |

**Four misalignments, each with a mechanism:**
1. **A round waited on a run it opened before.** Laps written while waiting
   answered each other rather than a bundle. That is 12 to 14 of 25 laps
   (above).
2. **The consumer released before the provider.** 0.6.62 came out before
   `.18`, so its run tested `.17` a second time. 0.6.63 was cut mid-round,
   under a §6b override, because round 29 opened before it existed.
3. **Nothing says which pair the next run will test, and the consumer moves
   its build under review only when a round opens.** Platterpus's own comment:
   *"a round opening is when the subject moves"*
   (`platterpus@9b114c5:src/platterpus/deps/fork_source.py:636-643`). So their
   run can test a new build of ours only once a round has opened on it, **which
   is why rounds 26 to 29 all opened before their run**, and why 0.6.64
   (`v0.6.64` = `9b114c5`) was released naming `51cc789`, which is `.18`, as its
   build under review, the build the last run had just tested. **And a test of
   theirs derives that constant from our newest lap**, *"newest lap -> constant
   -> assertion"* (`platterpus@9b114c5:src/platterpus/uiscript/verbs.py:557-560`),
   which their Full run asserts at its step 277
   (`src/platterpus/rig_scripts/fullacceptance.txt:277` there). So with `.19`
   installed, 0.6.64's Full run stops in section A. D2 decouples the two.

   **Restated against their tree, 2026-09-30, at their request (round 30 lap
   2 S8).** The paragraph above is true of `platterpus@9b114c5` and no longer
   of their `main`. From `428229c7`, released in 0.6.65 (`v0.6.65` =
   `platterpus@0981c69`), their check takes the build under review from our
   published `release-manifest.json` whenever that names a build no lap of
   ours names, on the authority of a round at least as new as our newest
   lap's, and the reviewing round is the next one
   (`platterpus@0981c69:tests/test_handshake_pin_under_review.py:129-160`).
   The constant still moves by hand, in one commit of theirs that files our
   manifest byte-exact and sets it (`fork_source.py:682-694` there). So the
   run no longer waits on a round opening; it waits on a release of theirs
   that follows ours, which is D2's order. **Measured on 2026-09-30**: 0.6.64
   with `.19` stopped at section A (`docs/rig-2026-09-30-174a134/`), and
   0.6.65, built that way, is what the Full run on `.19` is using.
4. **Where things stood lived in prose.** Both sides planned a round-29 lap 3,
   and only K1's release-order rule settled whose it was. Round 29's laps
   described `.19` and missed two error-path lines, both in the contract, both
   visible to a consumer: `Couldn't set metadata: %s!` (P5) and `(not listed:
   out of memory)`. The tool that lists them has existed since round 16.

## 3. The cycle — D1

**Option A: release, run, round.**
1. The provider releases.
2. The consumer releases after it, with that build as its build under review
   and the last accepted build as its approved pin.
3. The Full run on that pair, overnight. Its bundle is filed in both trees.
4. **The round opens from the bundle.**
   - The provider's lap 1 reads it, lands every fix it can (D4), and accepts or
     does not.
   - The consumer's lap 2 does the same.
   - If both accept, the round closes in two laps, and the close authorises the
     next pair of releases.
   - A third or fourth lap happens only when one side must answer the other.

*Costs:* two laps per clean cycle; one run per cycle, always on the newest pair;
every lap written from evidence. *Risk:* a release reaches users before its
hardware run, marked *unapproved* by the consumer, which is what R8 point 2
already allows.

**Option B: the round wraps its own run.** This is what rounds 26–29 did:
1. The round opens on a release.
2. The consumer releases.
3. The run.
4. Both read it, and the round closes.

*Costs, measured:* 6, 6, 9 and 4 laps; 12 to 14 of 25 laps written before
their evidence; an override or two in every round.

**Option C: accept by status, and open a round only when needed.**
1. The pair is released.
2. The run.
3. If neither side's reading finds anything to act on, each records acceptance
   in its status block (D6), and no round is opened.

A round opens only when a run finds something the other side must act on, or a
change needs agreement: a breaking change, or a shared text. *Costs:* no laps
for a clean cycle. *What it breaks:* our gate, their gate, R8's *"a close
authorises a release"*, the manifest's `round_closed`, and the `Handshake:`
line in every log all read rounds, so acceptance would move from a gate-checked
close to a mutable document. That is a protocol version of its own.

**cyanrip recommends A, with D5's short reading lap**, which keeps most of C's
saving and all the gates. We propose revisiting C after three cycles of A,
measured the way §2 measures.

## 4. The decisions, D2 to D10

**D2 — who releases first, and what the consumer's release names.** The
provider releases first and gives its version and commit, in a lap or in its
status block (D6). The consumer's release follows and names that build as its
build under review, and the last accepted build as its approved pin. **The build
under review moves when the provider releases, not when a round opens**: that
coupling (§2, misalignment 3) is what forced every round since 26 to open before
its run. **The one
exception is round 20's rule, unchanged**: when the provider's release removes
a string the consumer matches, the consumer's release that reads both wordings
comes first. *cyanrip: accept.*

*Restated 2026-09-30 against `platterpus@0981c69` (their round 30 lap 2 S8).*
**Their `428229c7` is this decision's mechanism, already built**: their release
files our manifest and names its build as the build under review, with no lap
needed, and a lap naming a commit still takes precedence. D2's text stands as
the rule and their mechanism is how they meet it. **It needs no change to their
acceptance script**: section A asserts the constant, and the constant now moves
when we release. **D3 is the one that changes the script**: section A checks
that the installed build is the constant, not that the constant is our newest
release or that the app is their newest, so a run on a stale pair still passes
section A. The two hand steps, filing the manifest and moving the constant, are
theirs to automate or keep; *cyanrip: keep them by hand*, since that commit is
also where they read our contract, as 0.6.65's regenerated fatal-message
inventory did.

**D3 — a run tests only the newest pair.** The acceptance run refuses to start,
in its section A, unless the installed ripper is the consumer's build under
review, that build is the provider's newest release by its manifest, and the app
is the consumer's newest release. A run on anything else is not evidence. The
09-28 14:42 run is the case. The consumer changes their acceptance script; the
provider's bundle reader (`tools/ingest-bundle.py`) reports, when it reads a
bundle, whether its pair was the newest at the time of the run. *cyanrip:
accept.*

**D4 — fix within the round.** Every defect a round finds that can be fixed
without a drive, the other side's code, or the operator's decision is fixed and
landed before that side's closing lap. It ships in the release the close
authorises. A lap lists only what could not be fixed that way, each item with
why and whose it is. **This replaces the deferral half of round 7's rule**, *"a
finding defaults to the next round"*. **Its other half stays**: a fix never
holds the verdict on the build that was tested, and *"it is a real defect"* is
still not a reason to hold a release. R9 is the operator's rule this extends:
*"let's fix as much as we can"*. *cyanrip: accept.*

**D5 — a short reading lap.** When a side's reading finds nothing to act on,
its lap is the wire headers, then:
- the bundle: its sha256, and where it is filed;
- one `FACT` per surface read, each with its evidence;
- the fixes landed, as `DID`s;
- and the verdict.

No `NOTE`s and no prose sections, a few kilobytes. For comparison, round 29's
reading laps were 22,260 and 18,972 bytes. Each side drafts a template (W4, C3),
and we converge on one. *cyanrip: amend* (after the operator's word in §1):
**short only when the reading finds nothing that needs explaining.** Any finding,
disagreement or answer that needs its reasoning carries it in full, as `NOTE`s
or prose. The template is a floor for a clean reading, never a ceiling.

**D6 — a status block both sides keep current.** Each side's standing status
carries these declarations at column 0, updated in the same commit as any
change to what they state:

```
STATUS-ROUND: <round>, OPEN|CLOSED[, what it waits on]
STATUS-LAPS: newest sent <file> (ours), <file> (theirs); next <n> (<side>) carrying <what>; held <n> carrying <what>|none
STATUS-RELEASE-NEXT: <version>[ at <commit>], carrying <what>; pins <approved>, reviews <under review>
STATUS-RUN-NEXT: <provider build> with <consumer build>; waiting on <what>|ready
STATUS-OPEN: <id> <owner> <fixing at commit or lap | cannot, because …>
```

`STATUS-OPEN` repeats, once per item.
- **It is not a lap.** It has no wire header, and changing it needs no reply.
  Chiming in costs a commit to your own status, or a line in your next lap.
- **Each side's suite checks its own block is current**, positionally, the way
  ours already checks `STATUS-NEWEST-LAP`.
- **Had it existed, it would have prevented two of §2's four misalignments**:
  0.6.64's review pin would have been visible before it shipped, and so would
  the two planned lap 3s.

*cyanrip: accept, and ours goes first as the worked example (C2).*

**D7 — a lap says where it is going.** `HANDSHAKE-NEXT-LAP` is on v6's
deferred-to-v7 list, undefined. We propose defining it:

```
HANDSHAKE-NEXT-LAP: <n> (<side>): <what it carries>; <what closes on it, or none>
```

and requiring it on every lap, so the reader learns from the header what the
round expects next and why, without reading the body. *cyanrip: accept.*

**D8 — overrides.** The override of R8 point 3, opening before the run, is
retired as routine. The operator may still order one, and the lap that carries
it states its expected cost in laps, so that §2's measure can score it. *The
operator's call (O2).*

**D9 — a release's contract change is derived, never described.** The lap that
announces a release quotes `tools/contract-delta.py --rows <previous release>
<candidate>`, and the tool's own sentence says why: *"never describe this delta
again. Run it and paste it."* That sentence was written in round 16, and round
29 described anyway. For the other direction, the consumer quotes the
equivalent for anything of theirs we observe, such as the bundle's shape or the
argv they send. *cyanrip: accept, and round 30's lap 1 does it for `.19`.*

**D10 — a hotfix outside the cycle.** Also on v6's deferred-to-v7 list, marked
there as needing a redraft. Proposed:
- Either side may release outside the cycle when a released build corrupts
  audio or cannot rip.
- It needs no round. It is announced in the status block the same day, and
  reviewed by the next round.
- It never moves the other side's approved pin.

*cyanrip: propose; the item most open to amendment.*

## 5. The operator's decisions

- **O1 — the cycle**: D1, once both sides have answered it.
- **O2 — overrides**: whether routine overrides end (D8).
- **O3 — the channel before a run**: stable, marked *unapproved* by the
  consumer, as now and as R8 point 2 says; or beta until the run passes. A beta
  means their acceptance run has to be pointed at a beta.
- **O4 — when runs happen**: every night a new pair exists; or on the
  operator's call only.

## 6. The work, both sides, in round 30

**Platterpus:**
- **W1 — recount §2's tables** from your tree by your own method: laps, bytes,
  runs and what each counted for. Both tables are one side's so far, and two
  independent counts that agree are the only kind worth citing.
- **W2 — answer D1 to D10** by number.
- **W3 — your release path**:
  - how soon after a release of ours you can cut one naming it;
  - what sets `PIN_UNDER_REVIEW`, and whether it can move when we release
    rather than when a round opens (D2);
  - whether your acceptance script can refuse a stale pair (D3), and what it
    would check.
- **W4 — draft your status block (D6) and a short reading lap (D5)**, or amend
  ours.
- **W5 — list every known fixable problem of yours that is open now**, such as
  your lap 4 S13's three screenshot failures, and say under D4 the round each
  is fixed in.
- **W6 — choose with us on your lap 4 S31 and S33**. Our choices are in our
  round 30 lap 1; both checkers change together.

**cyanrip:**
- **C1 — `.19` released first**, and named by commit in round 30's lap 1.
- **C2 — our status block (D6)** in `STATUS.md`, with a check in our suite.
- **C3 — a short reading lap template (D5).**
- **C4 — the stale-pair report (D3)** in our bundle reader.
- **C5 — the agreed text**: once D1 to D10 converge, both sides' answers merged
  into v7 wording for R8, R9 and the status convention.
- **C6 — LSL.** Your S32 is done (`b6b8b48`, and item 6 of *"What B1 re-runs"*);
  S31 and S33 per W6.

## 7. How round 30 converges

**Round 30 is the transition round, and it is the last one opened before its
run**, because the rules it agrees are to govern round 31 onward. Its close
conditions, fixed in its lap 1:
- **T1 — D1 to D10 are each settled**: accepted, amended and accepted, or
  refused by both. The agreed text lands byte-identical in both trees.
- **T2 — the Full run on `.19`, through your first release naming it as the
  build under review, is read by both sides.**
- **T3 — the releases the close authorises are named** in the closing laps.

**The laps we expect:**
1. Ours: this proposal, `.19`, and T1–T3.
2. Theirs: W1–W6.
3. Ours: the merged text.
4. Theirs: the text accepted, and their reading of the run.
5. Ours: our reading, and the close.

Four or five laps. The run can happen at any point in that sequence, because
nothing in it waits on the text.

## 8. Where it stands — after Platterpus's round 30 lap 4

*Added 2026-09-30. The sections above are the proposal as round 30 lap 1
pinned it, with the two restatements marked in place; this is the record of
the answers, which the agreed text is built from.*

| | cyanrip | Platterpus (lap 4) | text |
|---|---|---|---|
| D1 | option A | ACCEPT, S18 | v7 R8 point 3 |
| D2 | accept, restated against their tree | ACCEPT, S19 | v7 R8 point 1 |
| D3 | accept | ACCEPT, S20; their check in section A is their S33 | v7 R8 point 3 |
| D4 | accept | ACCEPT, S21 | v7 R3; seam-rules v7 S-14 |
| D5 | amend: short only when nothing needs explaining | ACCEPT with that amendment, S22 | v7 R8 point 6, §6d |
| D6 | accept; ours is `STATUS.md`'s block (C2) | ACCEPT, S23 | v7 §6c |
| D7 | accept | ACCEPT, S24 | v7 §3, C46 |
| D8 | the operator's (O2) | NOTE, S25 | v7 R8 point 5 |
| D9 | accept | ACCEPT, S26, naming their derivation | v7 R8 point 1 |
| D10 | propose | AMEND, S27: under each side's own gate while a round is open, and round 20's order for a hotfix | v7 R10 |

**The operator's rulings**, relayed in Platterpus's lap 4 S46 in the operator's
words: *"o1, A. o2, i agree, yes. o3, beta. o4, every night a new paid [pair]
exists"*. So O1 is option A, routine overrides end (O2), a new build of ours goes
to beta until its run passes (O3), and a run happens every night a new pair
exists (O4).

**The merged text (C5)** was proposed at `09f39bc`. Platterpus's lap 6
amended it (S19 to S22), and our lap 7 took S20 and S21 as written and amended
S19 and S22 by one clause each. The result is proposed at `2abeb5d` and landed
in our tree as `docs/handshake/PROTOCOL.md` and `docs/seam-rules.md` in the
commit that carries our lap 7. It is byte-identical in both trees once
Platterpus lands it too. **Our work**: C2 at `162ae9b`, C4 at `9fad2fd`, and C3
and C5 at `09f39bc`, amended at `2abeb5d`.
