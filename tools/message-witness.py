#!/usr/bin/env python3
"""Which of P5's failure messages does anything here actually assert?

WHY THIS EXISTS. `PROVIDER-CONTRACT.md` P5 is the inventory of every string
this program can print on a failure path -- the surface a consumer writes its
error matching against, and the one we undertake not to reword without a
handshake round. It is derived from the source, so it cannot describe a binary
we do not have. It says nothing at all about whether any of those messages has
ever been *seen*.

The 2026-09-05 audit put the number at "~20 of ~128 have a test witness". That
was a lead, not a measurement: nobody had counted. This counts, and publishes
the count, so a claim about our own coverage of the seam's error surface stops
being a recollection.

WHAT IT IS NOT. It is NOT a gate on full coverage, and it must never become
one. Most of P5 needs a real drive, a live network, an allocation failure or a
libcdio internal to reach; a check that failed until every row had a witness
would be red forever, and a permanently red gate is one nobody reads. What it
gates is the two things that are actually defects:

  1. A witness citing a message P5 does not publish. That means the message was
     reworded or removed and the assertion still names the old text -- so it is
     either about to fail, or, if it asserts an ABSENCE, already passing
     vacuously. This is the direction that catches drift.
  2. The witnessed count falling below the recorded floor. Coverage that was
     paid for once should not be given back silently.

DERIVED, NOT DECLARED. A hand-kept list of "messages we cover" is the same
defect as a hand-written contract: it looks authoritative and it rots. The
witness set is derived by searching the test corpus for each message's literal
prefix, exactly as a consumer would have to.

THE THIRD ANSWER IS THE HONEST ONE. A message whose literal prefix is too
short to identify it -- `Error` , `%s!` -- is reported as UNPROBABLE and
counted in neither column. Calling it uncovered would overstate the gap;
calling it covered because `Error` appears in some test file would be a match
that means nothing. This is `none` versus `unknown (reason)` on a census.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Where an assertion about a message can live. Tests, and the tools that run
# the binary and read its output -- a witness is a witness wherever it sits.
CORPUS = [
    ROOT / "tests",
    ROOT / "tools",
]
CORPUS_SUFFIXES = {".py", ".c", ".h"}

# This file is the census, not a witness: every message appears in its own
# output, so counting itself would make the number meaningless.
EXCLUDED = {"message-witness.py"}

# The shortest literal prefix that identifies a message rather than matching
# any diagnostic. Below this a probe cannot discriminate, so the row is
# UNPROBABLE and counted in neither column.
MIN_PROBE = 12

# The count of witnessed rows at the last deliberate measurement. Raising it is
# a normal part of adding a test; LOWERING it is an act, and has to be one.
WITNESS_FLOOR = 7


def looks_like_a_regex(s):
    r"""Is this string a regex fragment rather than a message?

    The citation scan reads string literals out of the corpus, and a corpus of
    TESTS is full of patterns. `rig-check.py` builds one across two source
    lines -- `r"^.*(Could not stat|...|Unable to open).*$"` -- and the half on
    the second line, `"Unable to open).*$"`, matched the scan's own prefix
    filter and was reported as a message the binary cannot print. It is not a
    message at all.

    Two signals, both structural rather than a list of words: an unbalanced
    bracket cannot occur in a message somebody wrote and can occur in half of a
    pattern, and a regex quantifier or anchor is not diagnostic prose.
    """
    for opener, closer in (("(", ")"), ("[", "]"), ("{", "}")):
        if s.count(opener) != s.count(closer):
            return True
    return any(tok in s for tok in (".*", ".+", "\\\\s", "\\\\d", "\\\\w", "$", "^", "|"))


def p5_rows(contract):
    """Every (file:line, message) in P5, read from the table, not from src/.

    Bounded to P5: P5a is the list of strings this document explicitly does
    NOT classify as failures, so folding it in would count rows the contract
    declines to claim.
    """
    text = contract.read_text(encoding="utf-8")
    start = text.find("## P5 - Fatal and error message inventory")
    if start < 0:
        raise SystemExit("P5 heading not found -- has the contract moved?")
    end = text.find("## P5a", start)
    body = text[start:end if end > 0 else len(text)]
    rows = []
    for m in re.finditer(r"^\| `([^`]+:\d+)` \| `(.+?)` \| ", body, re.M):
        rows.append((m.group(1), m.group(2)))
    return rows


def probe_for(message):
    r"""The longest leading run of literal text, or None if too short.

    Stops at the first conversion specifier, because everything after one is
    runtime data a test cannot match on. The contract escapes an embedded
    double quote as \", which is markdown's escaping and not the C source's,
    so it is undone before probing.
    """
    literal = message.replace('\\"', '"')
    cut = literal.find("%")
    probe = literal if cut < 0 else literal[:cut]
    probe = probe.strip()
    return probe if len(probe) >= MIN_PROBE else None


def corpus_files():
    for base in CORPUS:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if (path.is_file() and path.suffix in CORPUS_SUFFIXES
                    and path.name not in EXCLUDED):
                yield path


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--contract", default=str(ROOT / "PROVIDER-CONTRACT.md"))
    ap.add_argument("--gate", action="store_true",
                    help="exit non-zero on a stale citation or a drop below "
                         "the floor; the uncovered rows alone never fail")
    ap.add_argument("--list-uncovered", action="store_true")
    args = ap.parse_args()

    rows = p5_rows(Path(args.contract))
    if len(rows) < 50:
        print(f"FAIL: P5 yielded {len(rows)} rows -- the table's shape has "
              f"changed and this census is reading the wrong thing")
        return 1

    corpus = {p: p.read_text(encoding="utf-8", errors="replace")
              for p in corpus_files()}
    if not corpus:
        print("FAIL: the test corpus is empty -- every row would read as "
              "uncovered, which is a broken scan and not a finding")
        return 1

    witnessed, uncovered, unprobable = [], [], []
    for site, message in rows:
        probe = probe_for(message)
        if probe is None:
            unprobable.append((site, message))
            continue
        where = [p.name for p, text in corpus.items() if probe in text]
        (witnessed if where else uncovered).append((site, message, where))

    total = len(rows)
    print(f"P5 failure messages: {total}")
    print(f"  witnessed by the corpus: {len(witnessed)}")
    print(f"  no witness:              {len(uncovered)}")
    print(f"  unprobable (literal prefix under {MIN_PROBE} chars, so a probe "
          f"would match anything): {len(unprobable)}")
    print(f"  corpus: {len(corpus)} file(s) under "
          f"{', '.join(str(c.relative_to(ROOT)) for c in CORPUS)}")

    if args.list_uncovered:
        for site, message, _ in uncovered:
            print(f"    UNCOVERED {site}: {message}")
        for site, message in unprobable:
            print(f"    UNPROBABLE {site}: {message}")

    problems = []

    # Direction 2 of the traceability: a citation naming a message P5 does not
    # publish. Only strings that LOOK like one of ours are considered, or every
    # ordinary sentence in a test would be a candidate.
    # EVERY PRINTED LINE, not just the first. A message with an interior
    # newline is two lines on screen and both are separately matchable, so a
    # test asserting the SECOND one is citing real text. Before this split,
    # `Invalid folder name? Try -D <folder>.` -- the second line of
    # cue_writer.c:39 -- was reported as text the binary cannot print, which is
    # the opposite of true. The contract only started rendering that newline in
    # 1c96c8d; before it, the segment could not have been found at all.
    published = set()
    for _, message in rows:
        for seg in message.split("\\n"):
            published.add(probe_for(seg))
    published.discard(None)
    for path, text in corpus.items():
        for cited in re.findall(r'"((?:Unable to|Couldn\'t|Error |Invalid )'
                                r'[^"\\\n]{8,})"', text):
            head = cited.split("%")[0].strip()
            if len(head) < MIN_PROBE:
                continue
            if looks_like_a_regex(head):
                continue
            if not any(head.startswith(p) or p.startswith(head)
                       for p in published):
                problems.append(
                    f"{path.name} asserts \"{cited}\", which P5 does not "
                    f"publish -- the message was reworded or removed and this "
                    f"citation now names text the binary cannot print")

    if len(witnessed) < WITNESS_FLOOR:
        problems.append(
            f"witnessed rows fell to {len(witnessed)}, below the recorded "
            f"floor of {WITNESS_FLOOR} -- coverage was given back")

    for p in problems:
        print(f"FAIL: {p}")

    if args.gate:
        return 1 if problems else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
