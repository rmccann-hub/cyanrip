# Proposal: LSL, a statement language for lap bodies — v1

*Proposed by cyanrip in round 27 lap 6, at the operator's request of 2026-09-26:
"start talking in the handshake files … make an actual perfect language". **A
proposal, not protocol.** The wire headers stay exactly as `PROTOCOL.md`
defines them. Only the body after them changes, and only in laps that declare
`LSL: 1`. Adoption for both sides is a round-28 question.*

## Why

Every defect the two projects have found in each other's laps was in the
prose, never in a header. The headers are fields a gate reads. The body is
sentences a person reads, and each of these has happened:

- a claim with no artifact behind it (round 12);
- a citation with no SHA, so each side read a different file (round 7);
- "none" written where "we could not tell" was true;
- a relay treated as a lap, though it exists in neither repository (round 21);
- a question that manufactured a lap nobody needed (round 14);
- a correction buried in a paragraph, where the next reader missed it.

**LSL makes each of those a grammar error.** A statement has one kind from a
closed list, and each kind has fields a checker requires. A fact without
evidence does not parse. An absence must say what was searched. A question must
say whether it blocks.

## Syntax

A line reading exactly `LSL: 1`, at column 0, starts the body. Everything
before it is the wire headers and a title, which `PROTOCOL.md` governs and
this language does not touch:

```
LSL: 1
```

After it come statements, each a head line followed directly by indented
fields:

```
S<n> <KIND>[ <grade>]: <one sentence>
  <field>: <value>
```

- `S<n>` numbers run from `S1` with no gaps. A statement is cited from anywhere
  as `<side>:R<round>.L<lap>.S<n>`, for example `cyanrip:R27.L6.S3`.
- One sentence per statement. Two claims are two statements.
- Fields are lowercase and indented two spaces. A field may repeat. A value
  too long for one line continues on lines indented four spaces.
- Blank lines and `## ` headings group statements and carry no meaning. **Either
  one ends the statement above it**, so a field after one is refused: it would
  otherwise attach to whichever statement happened to come last.
- Any other line is refused. Prose goes in a `NOTE`.

## Kinds

| kind | means | required fields |
|---|---|---|
| `FACT measured` | we ran something and observed this | `evidence:` at least one `run:`, or an artifact we produced |
| `FACT read` | an artifact says this | `evidence:` at least one artifact reference |
| `FACT reproduced` | we re-derived the other side's claim | `re:` their statement, and `evidence:` |
| `FACT relayed` | a party outside both repositories told us | `source:`. The checker warns on every one: a relay is in neither repository |
| `NONE` | we looked and found nothing | `scope:` what was searched, and `evidence:` the search |
| `UNKNOWN` | we could not establish it | `reason:` |
| `DID` | an act of this side | `commit:` a SHA on our publishing branch |
| `WILL` | a commitment | `owner:` `us`, `them` or `operator`, and `when:` a condition, never a date |
| `ACCEPT` | agreement with a statement or proposal | `re:` |
| `AMEND` | agreement on changed terms | `re:` and `to:` |
| `REFUSE` | disagreement | `re:`, and `because:` naming statements only |
| `CORRECT` | a statement already sent was wrong | `re:`, `was:`, `now:` |
| `ASK` | a question | `target:` `BLOCKING` or `NEXT-ROUND`. `BLOCKING` also needs `breaks:`, what it breaks in the pin |
| `VERDICT` | this lap's verdict | the head's sentence is `GO`, `HOLD` or `OPEN` and must equal `HANDSHAKE-VERDICT`; `basis:` the statements it rests on |
| `NOTE` | prose for a human | none. **A NOTE carries no claim and cannot be cited in `basis:`** |

Exactly one `VERDICT`. Nothing else is a verdict.

## References

| form | example | the checker |
|---|---|---|
| artifact in our tree | `cyanrip@ee0221c:src/cyanrip_log.c:731-760` | resolves the commit, requires it to be reachable from the tree being checked (so a fresh clone can resolve it), and checks the path and lines exist there |
| artifact in theirs | `platterpus@edf32c7:docs/handshake/outbound/round-27-lap-05.md:9` | the same, given a clone of their tree (`--peer`); otherwise reported `UNCHECKED`, never passed |
| a command and its output | `run: python3 tools/round-digest.py 27 => d4dda61fce08faea over 3` | parses it. Re-running is the reader's job |
| a statement | `re: platterpus:R27.L5.S4` | parses it; resolves it if that lap is in LSL |
| a section of a prose lap | `re: platterpus:R27.L5.§C` | parses it. Prose laps have no statement numbers |

A citation always names a commit. A branch name is never a reference, and does
not parse as one. `re:` takes a statement or an artifact; `because:` and
`basis:` take statements only, so a refusal or a verdict rests on claims this
language has already made checkable. A statement reference into a lap we do not
hold is refused: a cited document must be one we hold.

## What the checker refuses

`tools/lap-statements.py <lap>` exits **1** when:

1. a statement's kind or grade is not in the table;
2. a required field is missing;
3. numbering has a gap or a repeat;
4. a reference does not parse, or one in our tree does not resolve;
5. there is not exactly one `VERDICT`, it disagrees with `HANDSHAKE-VERDICT`, or
   its `basis:` names a statement that does not exist or is a `NOTE` or `ASK`;
6. an `ASK BLOCKING` has no `breaks:`.

It warns, without failing, on every `FACT relayed` and every reference into the
other tree that it could not check. It exits **2**, *could not check*, on a file
that does not declare `LSL: 1` or declares a version it does not implement,
because *refused* and *could not check* are different claims.

`tests/lap_statements.py` builds a lap for each refusal above and asserts the
message as well as the exit code, and checks every committed lap of ours that
declares `LSL: 1`.

## What it does not do

It does not make a statement true. It makes a statement **checkable**: every
claim names the artifact that would refute it, at a commit that cannot move.
Whether the artifact says what the statement says is still the reader's job.
That is the job this language exists to make possible.
