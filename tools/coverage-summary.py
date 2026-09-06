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

SOURCE_RE = re.compile(r"^\s*-:\s*0:Source:(?P<path>.+)$")
LINE_RE = re.compile(r"^\s*(?P<count>[#=]{5}|-|\d+\*?):\s*(?P<no>\d+):")
BRANCH_RE = re.compile(r"^branch\s+(?P<idx>\d+)\s+(?:taken\s+(?P<taken>\d+)|never executed)")


class Merge:
    """Union of per-line and per-branch execution across every object file.

    WHY A UNION AND NOT A PERCENTAGE. gcov's text summary gives one percentage
    per (source, object) pair, and a header compiled into several objects gets
    several. src/utils.h is reported by TEN of them here. Percentages cannot be
    merged -- a line executed by one object and not another is covered, and
    picking one reading discards the rest. The first version of this tool kept
    the reading with the most branches and understated every shared header.

    So this keys on (file, line) and (file, line, branch index) and asks whether
    ANY object executed it, which is what "covered" means.
    """

    def __init__(self):
        self.executable = collections.defaultdict(set)   # file -> {line}
        self.covered = collections.defaultdict(set)      # file -> {line}
        self.branches = collections.defaultdict(set)     # file -> {(line, idx)}
        self.taken = collections.defaultdict(set)        # file -> {(line, idx)}

    def feed(self, path, text):
        line_no = None
        for raw in text.splitlines():
            m = LINE_RE.match(raw)
            if m:
                line_no = int(m.group("no"))
                c = m.group("count")
                if c == "-":
                    line_no = None      # not executable; branches cannot attach
                    continue
                self.executable[path].add(line_no)
                if c[0] not in "#=":
                    self.covered[path].add(line_no)
                continue
            m = BRANCH_RE.match(raw)
            if m and line_no is not None:
                key = (line_no, int(m.group("idx")))
                self.branches[path].add(key)
                # -c prints exact counts, so a branch taken once in ten thousand
                # is 1 and not a rounded 0%. That distinction is the whole
                # reason for -c.
                if m.group("taken") and int(m.group("taken")) > 0:
                    self.taken[path].add(key)

    def files(self):
        return sorted(self.executable)


def run_gcov(build, gcno):
    """Emit .gcov files for one object and return {source path: text}.

    gcov resolves sources against the COMPILATION directory recorded in the
    .gcno -- the build root, not the object directory. Running anywhere else
    yields a .gcov containing only a four-line header, which parses to zero
    coverage and reads exactly like an untested file.
    """
    for stale in build.glob("*.gcov"):
        stale.unlink()
    subprocess.run(["gcov", "-b", "-c", "-o", str(gcno.parent), str(gcno)],
                   cwd=str(build), stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=300)
    out = {}
    for f in build.glob("*.gcov"):
        text = f.read_text(encoding="utf-8", errors="replace")
        m = SOURCE_RE.match(text.splitlines()[0]) if text else None
        if m:
            out[m.group("path")] = text
        f.unlink()
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

    merge = Merge()
    for g in gcno:
        if not g.with_suffix(".gcda").exists():
            continue
        for path, text in run_gcov(build, g).items():
            try:
                rel = (build / pathlib.Path(path)).resolve().relative_to(ROOT)
            except (ValueError, OSError):
                continue
            # Only OUR sources. gcov also reports system and FFmpeg headers,
            # and counting those moves the total by an amount that has nothing
            # to do with this project's tests.
            if rel.parts[0] != "src":
                continue
            merge.feed(rel, text)

    if not merge.files():
        sys.exit("gcov produced no data for src/ -- refusing to print 0%, "
                 "which would be a claim about the tests when it is a fact "
                 "about this tool having failed")

    print(f"branch coverage from {build.name}, via gcov -b -c, "
          f"unioned across objects\n")
    print(f"  {'file':<34} {'lines':>8}  {'branch':>8}  {'branches':>9}")
    print(f"  {'-' * 34} {'-' * 8}  {'-' * 8}  {'-' * 9}")

    rows, tot_cl = [], 0
    tot_el = tot_tb = tot_ab = 0
    for rel in merge.files():
        el, cl = len(merge.executable[rel]), len(merge.covered[rel])
        ab, tb = len(merge.branches[rel]), len(merge.taken[rel])
        rows.append((rel, 100.0 * cl / el if el else 0.0,
                     100.0 * tb / ab if ab else 0.0, ab))
        tot_el += el
        tot_cl += cl
        tot_ab += ab
        tot_tb += tb

    for rel, lp, bp, ab in sorted(rows, key=lambda r: r[2]):
        print(f"  {str(rel):<34} {lp:7.2f}% {bp:8.2f}% {ab:9d}")

    line_pct = 100.0 * tot_cl / tot_el if tot_el else 0.0
    branch_pct = 100.0 * tot_tb / tot_ab if tot_ab else 0.0
    print(f"\n  TOTAL over {len(rows)} file(s): {line_pct:.2f}% line "
          f"({tot_cl}/{tot_el}), {branch_pct:.2f}% branch "
          f"({tot_tb}/{tot_ab})")

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
