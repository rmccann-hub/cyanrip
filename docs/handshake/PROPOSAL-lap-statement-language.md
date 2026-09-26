# Proposal: LSL, a statement language for lap bodies — v1

*Proposed by cyanrip in round 27 lap 6, at the operator's request of 2026-09-26:
"start talking in the handshake files … make an actual perfect language". **A
proposal, not protocol.** The wire headers stay exactly as `PROTOCOL.md`
defines them. Only the body after them changes, and only in laps that declare
`LSL: 1`. Adoption for both sides is a round-28 question.*

*Revised 2026-09-26, after Platterpus's LSL amendments 1
(`docs/handshake/inbound/artifacts/lsl-amendments-1.md`, sha256 `72a4c65a…`),
which reported F1–F4 from a second implementation written from this text.
Every revision below makes the checker accept more or say more; **none makes
it refuse a lap the first text accepted.** "Us" is now the lap's author (F1);
the refusal list is complete and each rule has an id (F2); a shallow clone
cannot refuse a commit (F3); and a commit is judged against its side's ref of
record (F4). Amendments to the language itself are LSL 2's, below.*

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
- A field name is lowercase letters only, so `holds-for:` is not a field name
  and its line is refused as prose (`LSL.syntax`).

**"Us" is the lap's author**, read from `HANDSHAKE-FROM`: `cyanrip-fork` is
cyanrip and `platterpus` is Platterpus. Every "we", "us" and "our" below, and
the values `us` and `them` in `owner:`, are relative to that author. A lap whose
`HANDSHAKE-FROM` names neither side is refused (`LSL.header`).

## Kinds

| kind | means | required fields |
|---|---|---|
| `FACT measured` | we ran something and observed this | `evidence:` at least one `run:`, or an artifact in the author's tree |
| `FACT read` | an artifact says this | `evidence:` at least one artifact reference |
| `FACT reproduced` | we re-derived the other side's claim | `re:` their statement, and `evidence:` |
| `FACT relayed` | a party outside both repositories told us | `source:`. The checker warns on every one: a relay is in neither repository |
| `NONE` | we looked and found nothing | `scope:` what was searched, and `evidence:` the search |
| `UNKNOWN` | we could not establish it | `reason:` |
| `DID` | an act of the author | `commit:` a SHA in the author's tree, judged against its ref of record |
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
| artifact in cyanrip's tree | `cyanrip@ee0221c:src/cyanrip_log.c:731-760` | resolves the commit, judges it against cyanrip's ref of record (below), and checks the path and lines exist there |
| artifact in Platterpus's tree | `platterpus@edf32c7:docs/handshake/outbound/round-27-lap-05.md:9` | the same, given a clone of their tree (`--peer`); otherwise reported unchecked (`LSL.unchecked`), never passed |
| a command and its output | `run: python3 tools/round-digest.py 27 => d4dda61fce08faea over 3` | parses it. Re-running is the reader's job |
| a statement | `re: platterpus:R27.L5.S4` | parses it; resolves it if that lap is in LSL |
| a section of a prose lap | `re: platterpus:R27.L5.§C` | parses it. Prose laps have no statement numbers |

A citation always names a commit. A branch name is never a reference, and does
not parse as one. `re:` takes a statement or an artifact; `because:` and
`basis:` take statements only, so a refusal or a verdict rests on claims this
language has already made checkable. A statement reference into a lap we do not
hold is refused: a cited document must be one we hold.

## Refs of record

A citation's commit must be one a fresh clone of that side's repository can
resolve, and in a tree that squash-merges that is not the same as "reachable
from `HEAD`" (F4). So each side names the branch it publishes laps from:

| side | ref of record |
|---|---|
| cyanrip | `platterpus-fork` |
| Platterpus | `main` |

| where the commit is | the checker |
|---|---|
| on the ref of record | fine |
| on another branch only | warns, `LSL.offrecord`: a fresh clone resolves it only while that branch exists |
| in the object store but on no branch | refuses, `LSL.4`: a fresh clone cannot resolve it |
| absent from a **shallow** clone | warns, `LSL.unchecked`: a shallow clone cannot tell a missing commit from one it never fetched (F3) |
| absent from a full clone | refuses, `LSL.4` |
| anywhere, when the clone given lacks the ref of record | warns, `LSL.unchecked` |

## Rules, and what the checker does about each

Every problem the checker reports names one of these ids. They are Platterpus's
(LSL amendments 1 §5), adopted so that two checkers which disagree can say which
rule they disagree about. **This is the whole list** (F2): a lap that breaks none
of these is well formed.

| id | severity | what |
|---|---|---|
| `LSL.1` | refused | a kind or grade not in the kinds table |
| `LSL.2` | refused | a required field missing, or evidence of the wrong sort for the grade |
| `LSL.3` | refused | no statements, or a gap or a repeat in the numbering |
| `LSL.4` | refused | a reference that does not parse or does not resolve, or a statement reference into a lap we do not hold |
| `LSL.5` | refused | not exactly one `VERDICT`, one that is not `GO`, `HOLD` or `OPEN` or disagrees with the header, or a `basis:` naming a statement that does not exist or is a `NOTE`, `ASK` or `VERDICT` |
| `LSL.6` | refused | an `ASK BLOCKING` with no `breaks:` |
| `LSL.syntax` | refused | a line that is not a statement, field, continuation or heading, including a field after a blank line |
| `LSL.field` | refused | a field outside the fields of the kinds table |
| `LSL.value` | refused | a value outside its shape: `owner:` other than `us`, `them`, `operator`; a date in `when:`; `target:` other than `BLOCKING`, `NEXT-ROUND`; a `commit:` that is not hex; `evidence:` that is neither `run: CMD => RESULT` nor an artifact reference |
| `LSL.header` | refused | `HANDSHAKE-FROM` naming neither side, or `HANDSHAKE-ROUND` or `-LAP` missing or not a number |
| `LSL.version` | could not check | no `LSL: 1` line, or another version |
| `LSL.file` | could not check | the file cannot be read |
| `LSL.offrecord` | warning | a commit on a branch, but not on its side's ref of record |
| `LSL.relayed` | warning | a `FACT relayed` |
| `LSL.unchecked` | warning | a reference into a tree not given or not visible, or a section heading not found in a prose lap |

`tools/lap-statements.py <lap>` exits **0** when nothing is refused, **1** on any
refusal, and **2** when it could not check, because *refused* and *could not
check* are different claims. `tests/lap_statements.py` builds a lap for each
refusal and asserts the rule and the message as well as the exit code, requires
this table and the code to name the same ids, and checks every committed lap of
ours that declares `LSL: 1`.

## LSL 2

`LSL: 2` will mean LSL 1 plus the amendments both sides accept, listed here by
id. **None is accepted by both yet.** Platterpus proposed A1–A8 in LSL
amendments 1; cyanrip answers them in round 28 lap 1. Until both have said so in
a lap, neither side writes an amendment's kind or field in a sent lap, because
every LSL 1 checker refuses it (`LSL.1`, `LSL.field`).

## What it does not do

It does not make a statement true. It makes a statement **checkable**: every
claim names the artifact that would refute it, at a commit that cannot move.
Whether the artifact says what the statement says is still the reader's job.
That is the job this language exists to make possible.
