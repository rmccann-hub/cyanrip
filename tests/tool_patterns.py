#!/usr/bin/env python3
"""No pattern in our tools or tests takes time quadratic in a run of blanks.

ROUND 30, PLATTERPUS'S LAP 14 S20. They sent two regex shapes they had fixed in
themselves, under the could-in-any-possible-way bar and with no claim that we
had them: a lazy capture before trailing blanks, and adjacent repeats over the
same characters. We had the first in five places, in four tools that read our
own logs and our source. On a line carrying a 20,000-blank run each took 1.5 s
in Python's backtracking engine, four times as long for each doubling, and an
`Invoked as:` line carries whatever a caller passes in `-a`.

Each was rewritten to capture from the first non-blank to the last, which
matched what the old pattern captured on every filed log (558 matches over 562
files) and takes 0.03 ms on that line. This sweep refuses the shape coming back:
a lazy `*?` or `+?`, then any closing groups, then optional blanks, then the
end of the line, optionally inside an optional group. It reads source text, so
it is exact about the spelling and blind to an equivalent written another way;
the timing check below covers the five rewritten patterns themselves.

AND IT WAS BLIND TO NINETEEN MORE, found the next day. Its first version
matched the blanks only as `\s*`, and seventeen wire-header patterns in
`tools/release-gate.py`, one in `tools/seam-sync-check.py` and one in this
suite spell them `[ \t]*`: the same shape, quadratic the same way (1.9 s on a
20,000-blank `HANDSHAKE-AGREED-CHANGES:` line), in the gate that reads every
lap of either side. Our round 30 lap 15 told Platterpus there were five. The
sweep below matches every spelling of the blank class we use, and the gate's
rewrite captures what the old patterns captured: 4,882 matches over the 529
lap files of both trees and a set of edge lines (an empty value, an all-blank
value, a trailing `\r`), with the gate's whole report byte-identical.
"""

import pathlib
import re
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
SELF = pathlib.Path(__file__).resolve()

# The shape, as it is spelled in a Python source file.
SHAPE = re.compile(r"[*+]\?\)*(?:\\s|\[ ?\\t\]|\[\\t ?\]|\[ \]| )[*+](?:\)\?)?\$")

failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


files = sorted(p for d in ("tools", "tests") for p in (ROOT / d).glob("*.py")
               if p.resolve() != SELF)
if len(files) < 20:
    fail(f"only {len(files)} files found, so the glob moved and this checks "
         f"almost nothing")
hits = 0
for p in files:
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if SHAPE.search(line):
            hits += 1
            fail(f"{p.relative_to(ROOT)}:{n}: a lazy capture before trailing "
                 f"blanks is quadratic in a run of blanks: {line.strip()}")

# The rewritten patterns, timed on the line that took 1.5 s each before.
LINEAR = [
    r"^AccurateRip:\s+(\S(?:.*\S)?)\s*$",
    r"^Offset:\s+(\S(?:.*\S)?)\s*$",
    r"^Invoked as:\s+((?:\S(?:.*\S)?)?)\s*$",
]
for pat in LINEAR:
    found = sum(pat in p.read_text(encoding="utf-8") for p in files)
    if not found:
        fail(f"{pat!r} is in no tool, so this times a pattern nothing uses")
    label = pat.split(":")[0].lstrip("^")
    line = f"{label}: x" + " " * 20000 + "y\n"
    t0 = time.perf_counter()
    m = re.search(pat, line, re.M)
    dt = time.perf_counter() - t0
    if not m or m.group(1) != "x" + " " * 20000 + "y":
        fail(f"{pat!r} does not capture the value from its first non-blank "
             f"to its last")
    if dt > 0.1:
        fail(f"{pat!r} took {dt * 1000:.0f} ms on a 20,000-blank run")

if failures:
    print(f"{failures} check(s) failed", file=sys.stderr)
    sys.exit(1)
print(f"tool patterns: {len(files)} files swept, none quadratic in a blank run")
