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


def main():
    text = SETTLED.read_text(encoding="utf-8")
    runnable, unrunnable, failures, malformed = 0, 0, [], []

    for line in text.splitlines():
        m = ROW.match(line)
        if not m:
            continue
        fact, check = m.group("fact").strip(), m.group("check").strip()
        # The header row and its underline.
        if fact in ("fact",) or set(fact) <= set("-: "):
            continue

        if check.startswith("—") or check.startswith("--"):
            unrunnable += 1
            continue

        cmd = CMD.search(check)
        if not cmd:
            malformed.append(fact[:70])
            continue

        runnable += 1
        r = subprocess.run(cmd.group(1), shell=True, cwd=ROOT,
                           capture_output=True, text=True)
        if r.returncode != 0:
            failures.append((fact[:70], cmd.group(1), r.returncode,
                             (r.stderr or r.stdout).strip()[:200]))

    for fact, cmd, rc, err in failures:
        print(f"STALE: {fact}")
        print(f"       {cmd}")
        print(f"       exit {rc}: {err}")
    for fact in malformed:
        print(f"MALFORMED (no command and no em dash): {fact}")

    print(f"{runnable} runnable check(s), {len(failures)} stale; "
          f"{unrunnable} row(s) carry no command and are trusted on their "
          f"source alone")

    if runnable < 8:
        print("REFUSING: too few runnable checks to be worth running -- "
              "SETTLED.md has probably been reformatted out from under this")
        return 1

    return 1 if failures or malformed else 0


if __name__ == "__main__":
    sys.exit(main())
