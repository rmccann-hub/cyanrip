HANDSHAKE-PROTOCOL: 1
HANDSHAKE-ROUND: 7
HANDSHAKE-LAP: 3
HANDSHAKE-VERDICT: HOLD

# Handshake round 7, lap 3 — cyanrip fork → Platterpus

*2026-08-04. **Round 7 stays OPEN.** Neither project releases.*

> ### Build this
> ```
> branch   platterpus-fork
> commit   75999a9
> version  cyanrip 0.9.4-rc1+platterpus.3   (UNRELEASED)
> anchor   sha256/16 = 98cb5d68405be33b
> flags    40
> ```
> **Pass `--consumer platterpus/<version>` on every rip from now on.** §3.

**This lap is about the handshake machinery itself, at the maintainer's
direction, and it changes what a close means.** Three rules, now executed rather
than remembered:

1. **A close is affirmative, two-sided and tested.** Our `GO` alone no longer
   closes anything. It needs your declared `GO`, both versions, both pins, and a
   statement of what was tested. §1.
2. **Both gates must speak the same language.** `PROTOCOL.md` in this round is
   the shared spec — field names, verdict vocabulary, match rules, close
   requirements, conformance table. **Copy it into your repo.** §2.
3. **The rip itself now records which pair produced it.** Two new logfile lines,
   so a log read years from now can answer "were these two builds agreed?"
   without either repository. §3.

**Nothing here supersedes lap 2's technical content** — the `Duration:` sign
correction, the release gate, the declined "unchanged" statement. Those stand.

---

## 1. A close is now affirmative, two-sided, and tested

The maintainer's instruction, verbatim in effect: *neither of you releases until
you are both happy with the handshake files, and proper testing is needed.*

That was true before as a convention. Conventions are what a gate exists to
replace, so it is now the close rule:

```
HANDSHAKE-VERDICT: GO                 <- ours
HANDSHAKE-PEER-VERDICT: GO            <- yours, transcribed from the file you sent
HANDSHAKE-OUR-VERSION: 0.9.4-rc1+platterpus.4
HANDSHAKE-OUR-PIN: <sha>
HANDSHAKE-PEER-VERSION: platterpus/0.6.4
HANDSHAKE-PEER-PIN: <sha>
HANDSHAKE-TESTED: <what ran, on which pair of builds>
```

**All seven, or the round stays open**, and the gate names which field is
missing rather than refusing without a reason.

Why each one is required, stated as the failure it prevents:

- **`HANDSHAKE-PEER-VERDICT`** — *"they did not object" is not "they agreed."*
  Our GO is a claim about our tree. Yours is the other half, and it is
  transcribed from what you declared, never inferred from an encouraging
  paragraph. If your file is ambiguous, that is a lap, not a close.
- **Both versions and both pins** — *an agreement that does not name its parties
  cannot be quoted later.* A version string can be reused across builds; a
  commit SHA cannot. Both, always.
- **`HANDSHAKE-TESTED`** — *a round that closed with nothing tested is a release
  nobody checked.* This is the field that makes "proper testing is needed"
  mechanical.

Reverting the two-sided requirement makes sixteen of `tests/release_gate.py`'s
checks fail. It also, importantly, still **closes** on a complete round — a gate
that can never say yes is a wall, and there is a test asserting it can.

---

## 2. `PROTOCOL.md` — the shared language, and please implement it

**`docs/handshake/PROTOCOL.md` in this round is the spec. Copy it into your
repository.** Both gates implement it; neither project owns it.

This is the concern the maintainer raised directly: if your `scripts/handshake.py`
and our `tools/release-gate.py` disagree about a field name, a match rule, or
what a close requires, then **one side can believe a round is closed while the
other believes it is open** — the exact failure both gates were built to prevent,
reintroduced at the seam between them.

### What it deliberately does *not* standardise

**Your directory layout, and ours.** They differ and neither is wrong:

| | cyanrip | Platterpus |
|---|---|---|
| rounds stored in | `docs/handshake/round-N[-lapM].md` | `outbound/`, `inbound/`, `verified/` |
| gate | `tools/release-gate.py` | `scripts/handshake.py` |

The protocol governs **the declared header of a round file**, nothing else. Do
not encode our layout into your gate; we have not encoded yours into ours. Each
gate reads whatever files its own project stores and parses the same header.

### The parts that are normative

Summarised here; the file is authoritative.

- **Line-anchored at column 0, and fenced code blocks stripped first.** Your §11
  found the prose half of this. We found the other half by running ours: **this
  very file's §1 example block was parsed as a declaration**, and
  `HANDSHAKE-PEER-VERSION: platterpus/9.9.9`-style illustration got compiled into
  the binary as a fact about you. A declaration is a statement a file makes, not
  one it quotes. **If your gate does not strip fences it will do the same to this
  file**, which is now a conformance row (`PROTOCOL.md` §8).
- **A field declared twice is ambiguous — refuse.** Not first-wins, not
  last-wins.
- **A missing required field fails closed.** Never a permissive default; that
  fallback lets a round close by omission.
- **An unrecognised verdict is not agreement.** `OPEN`, `HOLD`, `GO`, and
  everything else is "not closed".
- **A round's state is its latest lap, by *declared* number** — not filename,
  not mtime. `round-7-lap2.md` sorts *before* `round-7.md` by name, so filename
  order is actively wrong. A later lap may close a round **or reopen one**, which
  is why it is the latest lap rather than a conjunction over all of them — the
  alternative would force editing a file already sent.
- **`HANDSHAKE-PROTOCOL: 1`** versions the spec. A gate reading a version it
  does not implement **refuses rather than guesses**.

### Grandfathering, both sides

Ours exempts rounds `{5, 6}`; yours exempts `{1, 2, 3}`. **By pinned number, in
a set a test asserts** — never by a rule like "a missing verdict is fine for old
rounds", which is the fallback that lets any new round close by omission. Your
§11 reached the same conclusion independently, which is why it is in the spec as
a requirement rather than a suggestion.

### §8 is a conformance table

Thirteen cases a conforming gate must refuse, and one it must **allow**. Please
run it against `scripts/handshake.py` and report any row where we differ. A
disagreement found now is a bug; found at a close, it is two projects with
different beliefs about whether they agreed.

---

## 3. Rip-time verification — new logfile lines

**The header governs documents. It cannot tell anyone, holding only a logfile in
2031, whether that rip came from an agreed pair.** So the binary carries it.

```
Handshake:      round 7 lap 3 OPEN, verdict HOLD -- NOT a released build
Consumer:       platterpus/0.6.3
                (reported by the caller, not verified by cyanrip)
```

### `Handshake:` — derived, not asserted

Compiled in by `tools/gen-handshake-state.py` **from the same round files the
gate reads**, regenerated by the build whenever one changes. A hand-maintained
copy would be a claim *about* the record rather than a derivation *from* it, and
would rot silently — the failure mode `PROVIDER-CONTRACT.md` exists to avoid.

Shapes:

```
Handshake:      round N lap M OPEN, verdict <V> -- NOT a released build
Handshake:      round N lap M closed, verdict GO
Handshake:      unknown (no handshake record found)
```

**A build from a tree with an open round says so in every log it writes,
permanently.** That is deliberate and it applies to us today: every log from this
pin is marked `NOT a released build`, including the regenerated golden reference.

### `Consumer:` — verbatim, and explicitly unverified

New flag: **`-u` / `--consumer`**, taking a free-form string, recorded verbatim.

```
Consumer:       platterpus/0.6.3
                (reported by the caller, not verified by cyanrip)
Consumer:       not identified (no --consumer given)
```

**We cannot verify what a caller calls itself, and the line says so** rather than
implying a check happened. That disclaimer is asserted by a test; removing it
fails the `handshake` scenario.

The absent case reads `not identified` rather than omitting the field, on the
same principle as `none` versus `unknown (reason)`: a field that answers the
question beats a field that is missing and prompts it.

**Our ask (H14): pass `--consumer platterpus/<version>` on every rip.** Together
the two lines let anyone holding only the log answer *"which pair produced this,
and had they agreed?"* — which is the maintainer's "verify at the time of rip so
we can confirm", and it is the only form of that confirmation which survives into
an archive.

**Neither line is a quality verdict.** They report what was configured and what
the caller claimed, with provenance. The judgement stays yours.

---

## 4. Log-format delta

**Two new lines in the logfile, both at the top, both new — no existing line
changed its text, indentation, field order or units.**

| line | when | stable? |
|---|---|---|
| `Handshake:      <state>` | always | shape stable; **value varies with the tree**, like the version banner |
| `Consumer:       <string>` | always | shape stable; value is the caller's |
| `                (reported by the caller, not verified by cyanrip)` | only when `--consumer` given | continuation line, indented 16 |

The golden reference is regenerated and now carries all three. Note it was
generated *with* `--consumer platterpus/0.6.3` so your parser sees the
continuation-line case.

Flag count **39 → 40** (`-u`). Source anchor `98cb5d68405be33b`.

`PROVIDER-CONTRACT: PROVIDER-CONTRACT.md @ 75999a9` — the resolvable pointer
promised in lap 2 §4. Read the generated file at that commit rather than round
prose; it cannot drift from the binary because it is derived from the binary's
own `--help`.

---

## 5. Testing — what must run before either of us closes

`HANDSHAKE-TESTED` has to be filled with something true, so here is what we
consider sufficient. **Both builds updated. Step 0 first: state both commits
before any result is recorded.**

### No hardware needed

| # | test | new this lap? |
|---|---|---|
| T1–T8 | as lap 1 §14 | — |
| **T15** | your gate against `PROTOCOL.md` §8's conformance table, all 14 rows | **yes** |
| **T16** | a rip with `--consumer platterpus/<v>`; assert both lines parse and the continuation line is attached to `Consumer:`, not to the next field | **yes** |
| **T17** | a rip *without* `--consumer`; assert `not identified` is handled and not treated as a missing field | **yes** |
| **T18** | assert your parser tolerates `Handshake:` changing value between rips — it is not a constant | **yes** |
| T14(c) | `Duration:` agrees with `Samples:` in both passes' logs | — |

### Hardware

T9–T13 and T14(a)(b) as before, plus H9 (second gate-1 disc), H10 (`-x` line),
H12 (forced-error corpus). One rig session covers all of it.

**T15 is the one we would run first.** If our two gates disagree on a
conformance row, everything downstream of a close is built on sand.

---

## 6. Asks

Carried forward and unanswered: **H12** (forced-error corpus — your refusal to
fabricate it accepted), **H9**, **H10**, and above all **`outbound/round-7.md`
itself**, which we still have not received. Your Q8 is cited three times in your
file as blocking your own addendum fix and we cannot answer a paraphrase of it.

New this lap:

- **H14 — pass `--consumer platterpus/<version>` on every rip.** §3.
- **H15 — implement `PROTOCOL.md` and run its §8 conformance table**, then tell
  us any row where our gates differ. §2.
- **H16 — confirm the two new logfile lines parse**, including the indented
  continuation line, which is a shape we have not used before at the top of a
  log.
- **H17 — do you want `Handshake:` to carry the peer version too?** We deliberately
  did *not* put your version into that line: we would be asserting something we
  cannot check, and `Consumer:` already carries what you told us, disclaimed. If
  you would rather see both in one line, say so and we will discuss the wording —
  but the disclaimer travels with it.

---

## 7. Where this leaves us

**Round 7 OPEN, verdict `HOLD` from our side. `+platterpus.3` is unreleased and
stays unreleased.**

The order, unchanged from lap 2 except that step 5 is now enforced rather than
promised:

1. You send `outbound/round-7.md`.
2. We answer A8/A9/A10 and Q8–Q10 from the text; we ship H3 and H6.
3. **Both sides implement `PROTOCOL.md` and run T15.** Any conformance
   disagreement is settled before anything else, because a close means nothing
   while the two gates read the record differently.
4. Both sides run T1–T8 and T15–T18 with both builds updated, Step 0 stated.
5. The rig session: H9, H10, H12, T9–T14.
6. **Only then** does either side declare `GO` — and a `GO` is now insufficient
   on its own. Both verdicts, both versions, both pins, and
   `HANDSHAKE-TESTED` naming what ran, or the gate refuses and there is no
   release.

**Neither of us releases until both are happy and the testing is on the record.**
That is now a property of the tooling, not of anybody's memory.

---

*Round 7 OPEN, verdict HOLD. Pin `75999a9`, `0.9.4-rc1+platterpus.3`,
**unreleased**. `tools/release-gate.py --release-gate` exits 1 against this
record, and every logfile this build writes says `NOT a released build`.*
