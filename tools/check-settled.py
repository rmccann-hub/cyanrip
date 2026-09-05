#!/usr/bin/env python3
#
# This file is part of cyanrip.
#
# cyanrip is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# cyanrip is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with cyanrip; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""Run every `check` in docs/SETTLED.md and report which ones no longer pass.

SETTLED.md exists so a fact established once is looked up rather than derived
again -- the maintainer's finding, 2026-08-26: "you are constantly backtracking,
and figuring out stuff you've already said or fixed."

A lookup table is only worth reading if it is current, and a document that can
go stale silently is the thing this repository keeps warning about. So every row
carries the command that re-checks it, and this runs them.

WHAT IT ASSERTS, AND WHAT IT DELIBERATELY DOES NOT. It asserts that each check
command still succeeds. It does NOT assert that the sentence beside it is a
correct reading of that command's output -- nothing can, short of re-deriving
the fact, which is the cost this file exists to avoid. What it buys is that a
row whose underlying artifact has moved stops being quietly authoritative.

ROWS MARKED `check: —` ARE COUNTED AND NAMED, not skipped in silence. They are
facts about somebody else's machine or about a past event, so no command here
can re-run them; they are the rows to distrust first and the count is printed so
their number is visible rather than implied.
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SETTLED = ROOT / "docs" / "SETTLED.md"

# A row is `| fact | check |`, and the check is either a `backticked command`
# or an em dash. Anything else is a malformed row and is reported as one rather
# than passed over -- a row nobody can run is indistinguishable from a row that
# passes, which is the failure this whole file is about.
ROW = re.compile(r"^\|(?P<fact>.+?)\|(?P<check>.+?)\|\s*$")
CMD = re.compile(r"`([^`]+)`")

# A markdown cell escapes a pipe as `\|`, and ROW's lazy `.+?` pair cannot see
# that escape -- so a row whose FACT cell contains one split in the wrong place
# and this checker ran the wrong text as that row's command. Measured
# 2026-09-05: a row reading "`&&` from `\|\|`" reported
# `exit 2: Syntax error: end of file unexpected`, having executed a fragment of
# its own prose.
#
# The pipe-COUNT check below already honoured the escape. Two readers of one
# convention disagreed -- the seam failure this project names in as many words,
# here inside a single file. Splitting on unescaped pipes makes them one reader.
UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")


def cells(line):
    """The row's two cells, split on UNESCAPED pipes, or None if not a row."""
    parts = UNESCAPED_PIPE.split(line.rstrip())
    # `| fact | check |` -> ['', ' fact ', ' check ', '']
    if len(parts) != 4 or parts[0].strip() or parts[3].strip():
        return None
    return parts[1].strip(), parts[2].strip()


def main():
    text = SETTLED.read_text(encoding="utf-8")
    runnable, unrunnable, failures, malformed = 0, 0, [], []
    kinds, untagged = {}, []

    for line in text.splitlines():
        split = cells(line)
        if split is None:
            continue
        # Exactly two columns. The `— past: / theirs: / structural:` legend in
        # this file's own header is a THREE-column table, and the non-greedy
        # middle group happily swallowed its middle column and reported the
        # legend as four malformed facts. A parser that reads a document's
        # explanation of itself as data is the shape this whole file exists to
        # stop.
        # UNESCAPED pipes only: a command containing `\|` is one cell, not
        # three. Counting raw pipes dropped every upstream row whose check
        # pipes into grep -- 15 runnable checks became 11, silently, and the
        # only reason it was caught is that the number was read after the edit
        # rather than assumed.
        fact, check = split
        # The header row and its underline.
        if fact in ("fact",) or set(fact) <= set("-: "):
            continue

        if check.startswith("—") or check.startswith("--"):
            # A row with no command must say WHY it has none. Three very
            # different confidences were looking identical behind a bare em
            # dash: a past measurement, a fact about someone else's machine,
            # and a truth about our own code that no fixture can observe.
            # Untagged is a defect, not a default -- the same `none` versus
            # `unknown (reason)` rule this project applies to every log line.
            for t in ("past:", "theirs:", "structural:"):
                if t in check[:24]:
                    kinds[t] = kinds.get(t, 0) + 1
                    break
            else:
                untagged.append(fact[:70])
            unrunnable += 1
            continue

        cmd = CMD.search(check)
        if not cmd:
            malformed.append(fact[:70])
            continue

        runnable += 1
        # A markdown table cell must escape a pipe as `\|`, so a command
        # containing one arrives here escaped and the shell sees a literal
        # backslash. Unescape before running -- otherwise every piped check is
        # reported STALE for a reason that has nothing to do with the fact.
        command = cmd.group(1).replace("\\|", "|")
        r = subprocess.run(command, shell=True, cwd=ROOT,
                           capture_output=True, text=True)
        if r.returncode != 0:
            failures.append((fact[:70], command, r.returncode,
                             (r.stderr or r.stdout).strip()[:200]))

    for fact, cmd, rc, err in failures:
        print(f"STALE: {fact}")
        print(f"       {cmd}")
        print(f"       exit {rc}: {err}")
    for fact in malformed:
        print(f"MALFORMED (no command and no em dash): {fact}")

    for fact in untagged:
        print(f"UNTAGGED (no command and no reason for having none): {fact}")

    breakdown = ", ".join(f"{n} {t.rstrip(':')}" for t, n in sorted(kinds.items()))
    print(f"{runnable} runnable check(s), {len(failures)} stale; "
          f"{unrunnable} row(s) carry no command ({breakdown})")

    if runnable < 8:
        print("REFUSING: too few runnable checks to be worth running -- "
              "SETTLED.md has probably been reformatted out from under this")
        return 1

    # A floor on each class, not just on the total. Every row losing its tag at
    # once, or the runnable set collapsing, both read as "0 stale" -- which is
    # how a checker comes to pass by checking nothing. The runnable floor
    # already caught one: an edit that counted escaped pipes as columns dropped
    # 15 runnable checks to 11 in silence.
    if not kinds.get("structural:") or not kinds.get("theirs:"):
        print("REFUSING: a whole class of unrunnable row has vanished -- "
              "SETTLED.md has probably been reformatted out from under this")
        return 1

    return 1 if failures or malformed or untagged else 0


if __name__ == "__main__":
    sys.exit(main())
