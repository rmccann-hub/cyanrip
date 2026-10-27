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

"""Check the subject of each commit a change adds (review C item 5.2).

CLAUDE.md asks for subjects that are plain and imperative, and nothing
checked them: the review counted 43 of the last 200 over 72 characters. A
subject is the line `git log --oneline`, a pull request's commit list and
every merge's summary show, and git's own convention cuts it at 72. Each
non-merge commit in BASE..HEAD that upstream does not also hold must have a
subject that:

  * is at most 72 characters;
  * begins with a capital letter, as an imperative sentence does;
  * does not end with a full stop, since a subject is a title.

Imperative mood itself is not checked: telling "Embed" from "Fixed" takes a
list of words, and a list is what a check should not be built on.

    check-commit-subjects.py BASE HEAD [--upstream REF] [--repo DIR]

--upstream (default origin/master, upstream's mirror) excludes commits a
sync brings in, which are upstream's to word. Exit 0 when every subject
passes, 1 naming each that fails, 2 when git cannot list the range.
"""

import argparse
import subprocess
import sys

LIMIT = 72


def problems(subject):
    out = []
    if len(subject) > LIMIT:
        out.append(f"{len(subject)} characters, over {LIMIT}")
    if not subject[:1].isupper():
        out.append("does not begin with a capital letter")
    if subject.endswith("."):
        out.append("ends with a full stop")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("base")
    ap.add_argument("head")
    ap.add_argument("--upstream", default="origin/master")
    ap.add_argument("--repo", default=".")
    a = ap.parse_args(argv)

    cmd = ["git", "-C", a.repo, "log", "--no-merges", "--format=%h %s",
           f"{a.base}..{a.head}"]
    if a.upstream:
        cmd += ["--not", a.upstream]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       timeout=120)
    if r.returncode != 0:
        print(f"cannot list {a.base}..{a.head}: {r.stderr.strip()}",
              file=sys.stderr)
        return 2

    rows = [ln.split(" ", 1) for ln in r.stdout.splitlines() if ln]
    bad = 0
    for sha, subject in ((row[0], row[1] if len(row) > 1 else "") for row in rows):
        for p in problems(subject):
            bad += 1
            print(f"{sha} {subject!r}: {p}")
    if bad:
        print(f"{bad} problem(s) in {len(rows)} commit subject(s)")
        return 1
    print(f"{len(rows)} commit subject(s) checked, each at most {LIMIT} "
          "characters, capitalised, with no full stop")
    return 0


if __name__ == "__main__":
    sys.exit(main())
