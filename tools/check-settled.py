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

import os
import pathlib
import re
import shlex
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SETTLED = ROOT / "docs" / "SETTLED.md"

# ROWS WHOSE CHECK IS ITSELF A MESON TEST, delegated when this runs INSIDE
# meson. Measured 2026-09-26: 64 of this test's 78 s were two rows re-running
# tests/release_gate.py and probe-argv-surface.py --gate, which the same
# `meson test` also runs as "Release gate" and "Argv surface probe". The fact
# is still checked in that run, by that test, and the output names it.
#
# Standalone -- no MESON_TEST_ITERATION, which meson sets for every test --
# every row runs as before. And a row is delegated only while its target is
# still registered in tests/meson.build with the same script and arguments,
# so renaming or removing that test makes the row run here again rather than
# vanish.
DELEGATED = {
    "python3 tests/release_gate.py":
        ("Release gate", "files('release_gate.py')"),
    "python3 tools/probe-argv-surface.py --gate":
        ("Argv surface probe", "files('../tools/probe-argv-surface.py'), '--gate'"),
}


def delegated_to(command):
    """The meson test that checks this row in the same run, or None."""
    if "MESON_TEST_ITERATION" not in os.environ:
        return None
    hit = DELEGATED.get(command.strip())
    if not hit:
        return None
    name, args = hit
    build = (ROOT / "tests" / "meson.build").read_text(encoding="utf-8")
    pat = rf"test\('{re.escape(name)}', python,\s*args: \[ {re.escape(args)}"
    return name if re.search(pat, build) else None

# A row is `| fact | check |`, and the check is either a `backticked command`
# or an em dash. Anything else is a malformed row and is reported as one rather
# than passed over -- a row nobody can run is indistinguishable from a row that
# passes, which is the failure this whole file is about.
ROW = re.compile(r"^\|(?P<fact>.+?)\|(?P<check>.+?)\|\s*$")
# A DOUBLE-BACKTICK SPAN IS TRIED FIRST, so a check command may itself contain
# a backtick. With only the single-backtick form, such a command was TRUNCATED
# AT THE FIRST INNER BACKTICK and the fragment was handed to the shell -- which
# then failed on an unterminated quote and was reported STALE, i.e. as a fact
# that had stopped being true rather than as a row that could not be read.
# Silent truncation into a shell command is the worse of the two failures: it
# looks exactly like a finding.
CMD_FENCED = re.compile(r"``(.+?)``")
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

#: `cells()` saw a table row it could not split into exactly two cells.
MALFORMED = object()


# A line that OPENS and CLOSES with a pipe is a table row, whatever it splits
# into. Anything else is prose.
LOOKS_LIKE_A_ROW = re.compile(r"^\s*\|.*\|\s*$")


def cells(line):
    """The row's two cells, or None for prose, or MALFORMED for a broken row.

    THE THREE-WAY RETURN IS THE POINT. This used to return None both for prose
    and for a row that split into the wrong number of cells, and the caller
    `continue`d on None -- so a row with an UNESCAPED pipe in its command
    vanished from the run entirely. Not reported, not counted, not run.

    Found 2026-09-15 by tripping it: a new row whose check contained
    `grep -E 'A|B'` split into five cells and was silently skipped, while the
    summary line went on reporting "0 stale". **A row nobody can run is
    indistinguishable from a row that passes** -- this file's own docstring
    says so, and this function was the place it was true.
    """
    parts = UNESCAPED_PIPE.split(line.rstrip())
    # `| fact | check |` -> ['', ' fact ', ' check ', '']
    if len(parts) == 4 and not parts[0].strip() and not parts[3].strip():
        return parts[1].strip(), parts[2].strip()
    if not LOOKS_LIKE_A_ROW.match(line):
        return None
    return MALFORMED


def main():
    text = SETTLED.read_text(encoding="utf-8")
    runnable, unrunnable, failures, malformed = 0, 0, [], []
    delegated = []
    kinds, untagged = {}, []

    # THE LEGEND ABOVE THE MAIN TABLE IS A THREE-COLUMN TABLE, so a wrong cell
    # count is only a defect once the main table has started. Keyed to the main
    # table's own `| fact | check |` header rather than to a line number or a
    # list of exempt lines -- the document's structure, read from the document.
    in_main_table = False
    for line in text.splitlines():
        split = cells(line)
        if split is None:
            continue
        if split is not MALFORMED and split[0] == "fact":
            in_main_table = True
        if split is MALFORMED and not in_main_table:
            continue
        if split is MALFORMED:
            # Named and counted, never skipped. The commonest cause is an
            # unescaped `|` inside the check command -- a markdown cell needs
            # `\\|`, and a regex alternation or a shell pipe written raw
            # splits the row into five cells.
            malformed.append(("cells", line.strip()[:70]))
            continue
        # Exactly two columns. The `— past: / theirs: / peer-source: /
        # structural:` legend in
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
            # A row with no command must say WHY it has none. FOUR very
            # different confidences were looking identical behind a bare em
            # dash: a past measurement, a fact about someone else's machine,
            # a fact READ FROM THEIR SOURCE at a pinned commit, and a truth
            # about our own code that no fixture can observe. `peer-source:`
            # was added 2026-09-18: it is stronger than `theirs:`, which means
            # "only as good as the lap that told us", and it earns no command
            # because a check that reaches the network is not evidence about
            # this program -- one such row already times this suite out.
            # Untagged is a defect, not a default -- the same `none` versus
            # `unknown (reason)` rule this project applies to every log line.
            for t in ("past:", "theirs:", "peer-source:", "structural:"):
                if t in check[:24]:
                    kinds[t] = kinds.get(t, 0) + 1
                    break
            else:
                untagged.append(fact[:70])
            unrunnable += 1
            continue

        cmd = CMD_FENCED.search(check) or CMD.search(check)
        if not cmd:
            malformed.append(("nocmd", fact[:70]))
            continue

        # THIS SCRIPT IS ITSELF A REGISTERED MESON TEST ('Settled facts'), so a
        # cell that runs `meson test -C build ...` re-enters meson on the SAME
        # build directory. Meson's log base is <builddir>/meson-logs/testlog
        # with no uniquifier, so the inner run TRUNCATES the file the outer run
        # is still appending to. Measured 2026-09-05 after two such cells were
        # added: testlog.json came out 26.7% NUL bytes with 47 of 61 records
        # surviving and the inner run's single result first, while the JUnit
        # copy stayed intact because it is rewritten whole at finish().
        #
        # The suite really had passed. Its machine-readable record of having
        # passed was corrupt -- which is the confident-wrong-artifact this
        # project rates worse than a missing one, and it is exactly the file a
        # CI job archives as proof the commit was green.
        #
        # Invoke the scenario directly instead; that is how meson runs it.
        if re.search(r"\bmeson\s+test\b", cmd.group(1)) and "--logbase" not in cmd.group(1):
            malformed.append(fact[:70] + "  [re-enters meson test without "
                             "--logbase; run the scenario directly]")
            continue

        runnable += 1
        # A markdown table cell must escape a pipe as `\|`, so a command
        # containing one arrives here escaped and the shell sees a literal
        # backslash. Unescape before running -- otherwise every piped check is
        # reported STALE for a reason that has nothing to do with the fact.
        command = cmd.group(1).replace("\\|", "|")

        # LEXICALLY WELL-FORMED, checked before running. An unbalanced quote
        # cannot occur in a command somebody wrote and can only arrive here by
        # truncation, so this turns "reported STALE for a reason that has
        # nothing to do with the fact" into a row that names its own defect.
        try:
            shlex.split(command)
        except ValueError as e:
            malformed.append(fact[:70] + f"  [command is not lexically valid "
                             f"({e}); if it contains a backtick, wrap the whole "
                             f"command in a ``double-backtick`` span]")
            runnable -= 1
            continue

        target = delegated_to(command)
        if target:
            delegated.append((fact[:70], target))
            continue

        r = subprocess.run(command, shell=True, cwd=ROOT,
                           capture_output=True, text=True)
        if r.returncode != 0:
            failures.append((fact[:70], command, r.returncode,
                             (r.stderr or r.stdout).strip()[:200]))

    for fact, cmd, rc, err in failures:
        print(f"STALE: {fact}")
        print(f"       {cmd}")
        print(f"       exit {rc}: {err}")
    # TWO DIFFERENT DEFECTS, NAMED SEPARATELY. "the row has no command" and
    # "the row could not be split into cells" need different fixes, and the
    # second one used to be invisible -- so collapsing them into one message
    # would be the `none` versus `unknown (reason)` rule failing in the tool
    # that indexes the rule.
    for kind, fact in malformed:
        if kind == "cells":
            print(f"MALFORMED (not two cells -- an unescaped `|` in the check "
                  f"splits the row; markdown needs `\\|`): {fact}")
        else:
            print(f"MALFORMED (no command and no em dash): {fact}")

    for fact in untagged:
        print(f"UNTAGGED (no command and no reason for having none): {fact}")

    for fact, target in delegated:
        print(f"DELEGATED to meson test '{target}', which checks it in this "
              f"run: {fact}")

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
    # `past:` and `peer-source:` are deliberately NOT floored, and the
    # omission was previously unexplained: both are finite sets that can
    # legitimately empty as a measurement is superseded or a peer fact is
    # promoted to something runnable, so a floor there would refuse on a
    # correct edit. `structural:` and `theirs:` cannot empty while this
    # project has a consumer and a source tree.
    if not kinds.get("structural:") or not kinds.get("theirs:"):
        print("REFUSING: a whole class of unrunnable row has vanished -- "
              "SETTLED.md has probably been reformatted out from under this")
        return 1

    return 1 if failures or malformed or untagged else 0


if __name__ == "__main__":
    sys.exit(main())
