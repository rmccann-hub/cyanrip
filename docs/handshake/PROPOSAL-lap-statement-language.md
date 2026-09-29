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

*Revised 2026-09-27: **LSL 2 is defined and implemented**, below. Both sides
accepted A1–A8 in round 28, A3 as cyanrip amended it (cyanrip's lap 1 S19–S27,
Platterpus's lap 2 S10–S12). A lap declaring `LSL: 1` is checked exactly as
before.*

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

A line reading exactly `LSL: 1`, `LSL: 2` or `LSL: 3`, at column 0, starts the body
and says which version it is written in. Everything
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
| `LSL.version` | could not check | no `LSL: 1`, `LSL: 2` or `LSL: 3` line, or another version |
| `LSL.file` | could not check | the file cannot be read |
| `LSL.offrecord` | warning | a commit on a branch, but not on its side's ref of record |
| `LSL.relayed` | warning | a `FACT relayed` |
| `LSL.unchecked` | warning | a reference into a tree not given or not visible, or a section heading not found in a prose lap |
| `A1` | refused | LSL 2 only: a `TERM` statement malformed, or a `GO` over a close condition with no status, an unmet one, or one pending on the author's side |
| `A2` | refused | LSL 2 only: a pre-committed `verdict:` malformed, or broken by the author's next LSL lap without `triggers:` |
| `A3` | refused | LSL 2 only: a `FINDING` malformed, in the wrong tree, or ours, not portable and blocking nothing |
| `A4` | refused | LSL 2 only: a `FACT measured`, `read` or `reproduced` with no `holds:`, or one naming no commit or version |
| `A5` | refused | LSL 2 only: a `FACT measured` or `NONE` with no `examined:`, one over nothing, or an open one with no `missing:` |
| `A6` | refused | LSL 2 only: a `basis:` or `because:` naming a `WILL`, `UNKNOWN` or `FACT relayed` (and, in `because:`, a `NOTE`, `ASK` or `VERDICT`) |
| `A7` | refused | LSL 2 only: an `answers:` naming anything but the other side's `ASK`, or a `GO` over a `BLOCKING` one of theirs with no answer |
| `A8` | refused | LSL 2 only: a `CORRECT` with no `evidence:` |

`tools/lap-statements.py <lap>` exits **0** when nothing is refused, **1** on any
refusal, and **2** when it could not check, because *refused* and *could not
check* are different claims. `tests/lap_statements.py` builds a lap for each
refusal and asserts the rule and the message as well as the exit code, requires
this table and the code to name the same ids, and checks every committed lap of
ours that declares `LSL: 1`, `LSL: 2` or `LSL: 3`. It also reads Platterpus's worked
example of the amendments, filed at `inbound/artifacts/lap_language_round27_lap05.md`,
and asserts what their LSL amendments 1 §6 says each version must report.

## LSL 2

`LSL: 2` is LSL 1 plus the amendments both sides accepted, by id. **A1–A8
are accepted by both**, from Platterpus's LSL amendments 1 §2
(`inbound/artifacts/lsl-amendments-1.md`, sha256 `72a4c65a…`), with A3 as
cyanrip amended it. Nothing else is in LSL 2. Every refusal an amendment adds
names that amendment's id, which is the id Platterpus's checker reports, so two
checkers that disagree can say which amendment they disagree about.

| id | adds | refused when |
|---|---|---|
| `A1` | kind `TERM`, grades `set` (`requires:`), `met` (`term:`, `evidence:`), `unmet` (`term:`, `reason:`), `waived` (`term:`, `override:`), `pending` (`term:`, `on:` `us` or `them`, `remains:`); fields `restates:`, `regression:` | a required field is missing; `term:` names no `TERM set` we hold; after lap 1 a `set` has neither `restates:` nor `regression:` (S-13); or a `VERDICT GO` stands while a `TERM set` of the round has no status, its latest status is `unmet`, or it is `pending` on the author's own side. A side may say `GO` over the other side's pending half, never over its own |
| `A2` | on a `WILL` with `owner: us`: `verdict:` `GO` or `HOLD`, and `unless:` (repeatable); on any statement, `triggers:` | `verdict:` on anything but a `WILL`, or with an owner other than `us`; `unless:` with no `verdict:`; `triggers:` naming anything but a pre-committed `WILL` in an earlier lap of the author's; or the author's next LSL lap in the round declares another verdict and no statement's `triggers:` names the `WILL` |
| `A3` | kind `FINDING`, grade its origin: `ours`, `yours`, `upstream`, `unknown`. Always `in:` (an artifact), `shape:`, `target:` (`NEXT-ROUND`, `BLOCKING`, `FIXED`), `evidence:`; `BLOCKING` needs `breaks:`, `FIXED` needs `landed:`, `ours` needs `portable:` (`yes` or `no`) | a required field is missing or out of shape; a finding of ours is not in the author's tree, or one of yours is; or, **cyanrip's amendment**, a finding of ours with `portable: no` and a target other than `BLOCKING`, which R9 puts in a commit, not a lap |
| `A4` | `holds:` on `FACT measured`, `read` and `reproduced` | it is missing, or names no commit and no version |
| `A5` | `examined: <n> <unit>, closed` or `…, open` on `FACT measured` and `NONE`; `missing:` | it is missing or out of shape, `n` is 0, or it is `open` with no `missing:` |
| `A6` | nothing | a `basis:` or `because:` names a `WILL`, `UNKNOWN` or `FACT relayed`, or a `because:` names a `NOTE`, `ASK` or `VERDICT`. In a `basis:` those three stay `LSL.5`, as in LSL 1 |
| `A7` | `answers:` on any statement | it names anything but an `ASK` of the other side's we hold; or a `VERDICT GO` stands while an `ASK` with `target: BLOCKING` from the other side, earlier in the round, has no `answers:` from the author |
| `A8` | `evidence:` on `CORRECT` | it is missing |

**A1, A2 and A7 read the round**, not only the lap: every lap of it this tree
holds, ours in `docs/handshake/` and theirs in `docs/handshake/inbound/`, up to
the lap under check, which stands in for any held copy of itself. `on: us` is
the side that wrote the status. **The checker prints what those rules were
checked over**, the number of close conditions and blocking questions it found,
because a `GO` over a round with none satisfies A1 and A7 by finding nothing.

## LSL 3

`LSL: 3` is LSL 2 plus **B1, B2 and B3**, accepted by both sides in round 28:
B1 proposed in cyanrip's lap 1 (S30) and amended by Platterpus's lap 2 (S17),
B2 and B3 proposed in cyanrip's lap 3 (S22, S23), and all three accepted as LSL
3 in Platterpus's lap 4 (S22–S24), so that LSL 2 stays exactly A1–A8. Nothing
else is in LSL 3. Every refusal it adds names its id, which is the id both
checkers report.

| id | adds | refused when |
|---|---|---|
| `B1` | on any statement, `at:` — the commit of the author's tree a `run:` ran at, as `<sha>` or `<side>@<sha>`. With `--rerun`, the checker re-runs a `run:` whose command can depend on nothing but that commit | a `run:` has neither an `at:` on its statement nor a `HANDSHAKE-FROM-COMMIT` on its lap; `at:` names anything but a commit of the author's tree; or, with `--rerun`, the command was re-run and one of its result's quoted strings is not in its output |
| `B2` | nothing | a `VERDICT GO` stands and no lap of the round this tree holds writes a `TERM set`. A1 over no close condition passes by finding nothing, which a `GO` must not be able to do |
| `B3` | nothing | `answers:` stands on a `NOTE`, `ASK`, `VERDICT`, `WILL`, `UNKNOWN` or `FACT relayed`, the statements A6 lets carry no weight. Such an `answers:`, in any lap of the round, also answers nothing for A7 |

**What B1 re-runs**, and only this, because a checker that guessed which
commands are safe to repeat would be a guess wearing a derivation's clothes:

1. **The commit** is the statement's `at:`, else the lap's
   `HANDSHAKE-FROM-COMMIT`. It is the commit the command ran at, checked out
   detached in a scratch worktree of the author's clone and removed afterwards.
   When a `run:` needs it, `HANDSHAKE-FROM-COMMIT` must name exactly one
   commit, and an `at:` is a commit and nothing else, `<sha>` or
   `<side>@<sha>` with no prose beside it; either one otherwise is refused.
2. **The command is a simple one**: it splits into words with no shell, and has
   none of `| ; & < > $ ( ) * ? [ ] { } \`, a backtick, a newline or an `…`. A
   command that needs a shell, a glob or an elision to mean what it says is not
   the command that ran. Quotes are allowed, and it is split as a shell would
   split it, with no shell running. No argument is an absolute path, climbs
   out with `..` (as a part between `/`, `=` or `:`, so `HEAD:../x` climbs
   out), asks git to write a file (`--output`), or begins with `#`, which a
   shell would read as a comment.
3. **Its program is one of three kinds**: `git` with a read-only query as its
   first word (`log`, `show`, `diff`, `rev-parse`, `merge-base`, `ls-tree`,
   `cat-file`, `rev-list`); `sha256sum` or `wc`; or a file of the author's tree
   at that commit, run directly or as `python3 PATH` (`python` is not
   `python3`), **whose own first 40 lines include a line that begins with
   `LSL-RERUN: commit-only`** once the file's comment marker (`#`, `//`, `/*`,
   `*`, `--` or `;`) and the spaces after it are taken off. That line is the
   tool's author saying its output depends only on the commit it runs in. A
   tool that reads the network, a drive, the clock or a moving ref must not
   carry it. Each side marks its own tools; neither marks the other's. **A git
   query can still depend on more than its commit**, and is not re-run when
   an argument before `--` names a ref other than `HEAD` (a branch, a tag, a
   remote-tracking ref or a pseudo-ref such as `FETCH_HEAD`, alone, in a range,
   or with `~`, `^` or `@`), uses `@{`, reads the clone's refs (`--all`,
   `--branches`, `--tags`, `--remotes`, `--glob`, `--exclude`, `--reflog`),
   reads the clock (`--since`, `--until`, `--after`, `--before`, `--max-age`,
   `--min-age`, `--relative-date`, `--date=relative`, `--date=human`, or `%ar`,
   `%cr`, `%ah` or `%ch` in a `--format` or `--pretty`), or prints where the
   checkout is (`--show-toplevel`, `--show-prefix`, `--show-cdup`,
   `--git-dir`, `--absolute-git-dir`, `--git-common-dir`,
   `--show-superproject-working-tree`, `--git-path`, `--resolve-git-dir`).
4. **Its result quotes what it printed**: each `"double-quoted"` string in the
   result after `=>` must appear in the output, stdout and stderr together,
   and an `…` inside a quoted string splits it into parts that must appear in
   that order. Only the spaces beside an `…` are taken off a part; a quoted
   string with no `…` is compared with its spaces. A result with no quoted
   string is prose, and prose is not compared.
5. **Its exit status is held to what the result states.** A result states an
   exit code as `exit N`: literally, lower case, one space between, `exit` a
   word of its own (not `pre-exit`, not `exited`) and `N` digits not followed
   by a word character, outside every quoted string, a quoted string being read
   as a gap between words and never as nothing. A result that states one code
   is held to it, and may state a non-zero one (`=> exit 1, "refused"`); one
   that states two different codes is refused when re-run, since no run can
   satisfy both; and one that states none is `UNCHECKED` when the command
   exits non-zero. Proposed in cyanrip's round 29 lap 1 (S28), with the shape
   of `exit N` from Platterpus's round 29 lap 2 (S15), and accepted by both
   (their lap 2 S12, our lap 3 S27).

**Anything else is reported, not refused**: `UNCHECKED run:` with the reason,
as `LSL.unchecked`. A network, drive or clock command is never re-run, as
Platterpus's amendment says. Without `--rerun` nothing is executed and the
checker says so. **`--rerun` executes the author's committed code**, the other
side's when checking their lap, so it is run where that is acceptable.

The checker prints what B1 covered: how many `run:` results the lap has, how
many were re-run and matched, how many were not matched, and how many could not
be re-run.

## What it does not do

It does not make a statement true. It makes a statement **checkable**: every
claim names the artifact that would refute it, at a commit that cannot move.
Whether the artifact says what the statement says is still the reader's job.
That is the job this language exists to make possible.
