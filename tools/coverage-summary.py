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

"""Per-file BRANCH coverage over src/, summarised from gcov.

WHY THIS AND NOT gcovr. Neither gcovr nor lcov is installed here; gcov is.

WHICH NUMBER, AND WHY NOT THE OBVIOUS ONE. gcov prints three:

    Lines executed:      94.35% of 478
    Branches executed:   91.69% of 385     <- the branch was REACHED
    Taken at least once: 75.32% of 385     <- both arms were TAKEN

"Branches executed" counts a branch as covered when control merely reached it,
even if one arm never ran. **"Taken at least once" is branch coverage** as every
standard means it, and it is the smaller number -- reporting the other would
overstate this codebase by roughly sixteen points. The strongest verb the
evidence supports, not one notch stronger.

WHAT COVERAGE IS AND IS NOT WORTH HERE, because this project has a considered
position and it is not "coverage is good". tools/mutate.py measures whether the
tests ASSERT, not merely whether they EXECUTE, and CLAUDE.md's standing example
is that coverage would report the FIFO path green while mutation shows it
untested. So the two are complements:

  * coverage answers "what did no test even REACH?" -- which mutation cannot,
    since an unreached line yields no surviving mutant to notice;
  * mutation answers "what did no test CHECK?" -- which coverage cannot.

A file at 100% line coverage with a 40% mutation score is exactly the shape the
two numbers exist to tell apart, and this repository has measured it.

Usage:
    tools/coverage-summary.py                     # against build-cov
    tools/coverage-summary.py --build build-cov
    tools/coverage-summary.py --min-branch 60     # non-zero below the floor
"""

import argparse
import collections
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

FILE_RE = re.compile(r"^File '(?P<path>[^']+)'$")
LINES_RE = re.compile(r"^Lines executed:(?P<pct>[\d.]+)% of (?P<n>\d+)$")
TAKEN_RE = re.compile(r"^Taken at least once:(?P<pct>[\d.]+)% of (?P<n>\d+)$")

Cov = collections.namedtuple("Cov", "lines_pct lines_n branch_pct branch_n")


def gcov_for(gcno):
    """Run gcov -b -n on one .gcno and return {reported path: fields}."""
    r = subprocess.run(["gcov", "-b", "-n", gcno.name],
                       cwd=str(gcno.parent), stdout=subprocess.PIPE,
                       stderr=subprocess.DEVNULL, text=True, timeout=180)
    out, cur, found = {}, None, {}
    for line in r.stdout.splitlines():
        m = FILE_RE.match(line)
        if m:
            if cur and "lines" in found:
                out[cur] = found
            cur, found = m.group("path"), {}
            continue
        m = LINES_RE.match(line)
        if m and cur:
            found["lines"] = (float(m.group("pct")), int(m.group("n")))
            continue
        m = TAKEN_RE.match(line)
        if m and cur:
            found["taken"] = (float(m.group("pct")), int(m.group("n")))
    if cur and "lines" in found:
        out[cur] = found
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--build", default="build-cov")
    ap.add_argument("--min-branch", type=float, default=None)
    args = ap.parse_args()

    build = (ROOT / args.build).resolve()
    if not build.is_dir():
        sys.exit(f"no such build directory: {build}\n"
                 f"create it with: meson setup {args.build} -Db_coverage=true")

    gcno = sorted(build.rglob("*.gcno"))
    if not gcno:
        sys.exit(f"no .gcno under {build} -- configured with "
                 f"-Db_coverage=true and built?")

    # A .gcno with no .gcda never executed at all. Reported, never skipped: an
    # omitted unexecuted TU reads as full coverage of a smaller program.
    never_ran = [g for g in gcno if not g.with_suffix(".gcda").exists()]

    per_file = {}
    for g in gcno:
        if not g.with_suffix(".gcda").exists():
            continue
        for path, d in gcov_for(g).items():
            # gcov reports source paths relative to the COMPILATION
            # directory recorded in the .gcno -- which is the build root, not
            # the .gcno's own directory. Resolving against g.parent yields
            # build-cov/src/src/... and matches nothing, which this tool's
            # own guard caught by refusing to report 0%.
            try:
                rel = (build / pathlib.Path(path)).resolve().relative_to(ROOT)
            except (ValueError, OSError):
                continue
            # Only OUR sources. gcov also reports system and FFmpeg headers,
            # and counting those moves the total by an amount that has nothing
            # to do with this project's tests.
            if rel.parts[0] != "src":
                continue
            lp, ln = d.get("lines", (0.0, 0))
            bp, bn = d.get("taken", (0.0, 0))
            prev = per_file.get(rel)
            # A header included by several TUs is reported more than once; keep
            # the reading with the most branches, the fullest compilation.
            if prev is None or bn > prev.branch_n:
                per_file[rel] = Cov(lp, ln, bp, bn)

    if not per_file:
        sys.exit("gcov produced no data for src/ -- refusing to print 0%, "
                 "which would be a claim about the tests when it is a fact "
                 "about this tool having failed")

    print(f"branch coverage from {build.name}, via gcov "
          f'("Taken at least once", not "Branches executed")\n')
    print(f"  {'file':<34} {'lines':>8}  {'branch':>8}  {'branches':>9}")
    print(f"  {'-' * 34} {'-' * 8}  {'-' * 8}  {'-' * 9}")
    tot_l = tot_ln = tot_b = tot_bn = 0
    for rel in sorted(per_file, key=lambda r: per_file[r].branch_pct):
        c = per_file[rel]
        print(f"  {str(rel):<34} {c.lines_pct:7.2f}% {c.branch_pct:8.2f}% "
              f"{c.branch_n:9d}")
        tot_l += c.lines_pct * c.lines_n / 100.0
        tot_ln += c.lines_n
        tot_b += c.branch_pct * c.branch_n / 100.0
        tot_bn += c.branch_n

    line_pct = 100.0 * tot_l / tot_ln if tot_ln else 0.0
    branch_pct = 100.0 * tot_b / tot_bn if tot_bn else 0.0
    print(f"\n  TOTAL over {len(per_file)} file(s): {line_pct:.2f}% line, "
          f"{branch_pct:.2f}% branch ({tot_bn} branches)")

    if never_ran:
        print(f"\n  {len(never_ran)} translation unit(s) produced no .gcda -- "
              f"never executed:")
        for g in never_ran:
            print(f"    {g.name[:-5]}")
        print("  (fmtprobe_* are sc_format_guard's control snippets and "
              "version.c is generated; expected)")

    print("\n  NOT a substitute for tools/mutate.py. Coverage says what no test "
          "REACHED;\n  mutation says what no test CHECKED.")

    if args.min_branch is not None and branch_pct < args.min_branch:
        print(f"\nFAIL: branch coverage {branch_pct:.2f}% is below the "
              f"{args.min_branch:.2f}% floor")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
