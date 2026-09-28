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

"""Generate docs/upstream/issues-to-file.md: the thirteen upstream bug
reports, rendered as issues ready to paste into cyanreg/cyanrip's tracker.

The reports themselves are written in two files, and this renders them:

  * `docs/upstream/defect-reports.md`, reports 1-7 and 9-13;
  * `docs/upstream-cachemodel-report.md`, report 8.

It exists because filing is the maintainer's act, done in a browser, and a
report written for this repository is not quite a report written for
upstream's tracker: each needs a title line, a body with nothing about the
fork's own files, and every fork commit it names as a link a reader outside
this repository can follow. Rendering it by hand from two files is how a
copy drifts from its source, so it is derived instead, and `--check` fails
when either source has moved since the rendered copy was made.

It judges nothing and checks nothing about upstream. Whether each report is
still true of upstream's `master` is `tools/check-settled.py`'s job, through
the report's row in `docs/SETTLED.md`.

    tools/gen-upstream-issues.py > docs/upstream/issues-to-file.md
    tools/gen-upstream-issues.py --check docs/upstream/issues-to-file.md

It needs a git checkout, because it links a hex string only when it names a
commit this repository holds.
"""

import argparse
import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORK = "https://github.com/rmccann-hub/cyanrip"
DEFECTS = "docs/upstream/defect-reports.md"
CACHEMODEL = "docs/upstream-cachemodel-report.md"
COUNT = 13


def is_commit(sha):
    r = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e",
                        sha + "^{commit}"], capture_output=True)
    return r.returncode == 0


def link_commits(text):
    return re.sub(r"`([0-9a-f]{7})`",
                  lambda m: f"[`{m.group(1)}`]({FORK}/commit/{m.group(1)})"
                  if is_commit(m.group(1)) else m.group(0), text)


def render():
    if subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--git-dir"],
                      capture_output=True).returncode != 0:
        sys.exit("gen-upstream-issues: not a git checkout; commit links "
                 "cannot be told from other hex strings without one")
    dr = (ROOT / DEFECTS).read_text()
    cm = (ROOT / CACHEMODEL).read_text()

    issues = {}
    parts = re.split(r"(?m)^## (\d+)\. (.+)$", dr)
    for i in range(1, len(parts), 3):
        n, title, body = int(parts[i]), parts[i + 1].strip(), parts[i + 2]
        body = re.sub(r"\n---\s*$", "", body.strip())
        body = body.replace(
            "(Report 8 is `docs/upstream-cachemodel-report.md`.)\n\n", "")
        body = body.replace("report 4",
                            "the filter-graph issue (item 4 of this set)")
        if n in issues:
            sys.exit(f"gen-upstream-issues: report {n} appears twice in "
                     f"{DEFECTS}")
        issues[n] = (title, body)
    m = re.search(r"(?ms)^## Title\s*\n+(.+?)\n\s*\n## Body", cm)
    if not m or 8 in issues:
        sys.exit(f"gen-upstream-issues: report 8 is {CACHEMODEL}'s, and "
                 f"that file must carry a '## Title' then a '## Body'")
    issues[8] = (m.group(1).strip(), cm.split("\n## Body", 1)[1].strip())
    if sorted(issues) != list(range(1, COUNT + 1)):
        sys.exit(f"gen-upstream-issues: expected reports 1-{COUNT}, found "
                 f"{sorted(issues)}")

    digest = hashlib.sha256((dr + "\0" + cm).encode()).hexdigest()[:16]
    out = [
        f"# {COUNT} upstream issues for cyanreg/cyanrip, ready to paste", "",
        "**Generated, never edited.** `tools/gen-upstream-issues.py` renders "
        f"it from `{DEFECTS}` and `{CACHEMODEL}`, whose combined sha256/16 is "
        f"`{digest}`; `--check` fails when either has moved. Every `file:line` "
        "below is upstream's, at the commit its source file names, and each "
        "report's row in `docs/SETTLED.md` re-checks it against `master`. "
        "Every fork commit linked below is on `platterpus-fork`, which is "
        "public.", "",
        "**How to file.** For each item: open "
        "<https://github.com/cyanreg/cyanrip/issues/new>, paste the "
        "**Title** line into the title box and everything between the two "
        "`BODY` markers into the body. File them in order: item 5 refers to "
        "item 4, so once item 4 is filed you can replace *\"item 4 of this "
        "set\"* in item 5 with its issue link. Before filing, a quick search "
        "of upstream's open issues for each title's key words avoids a "
        "duplicate; this list was not checked against their tracker.", "",
        "**Suggested order of importance**, if you file only some: 6 "
        "(apostrophes corrupt metadata on real rips), 8 (disc images rip "
        "corrupted audio with `Ripping errors: 0`), 1 and 2 (a hung or cut-off "
        "process with the drive held), 4 and 5 (`-H` silently drops "
        "de-emphasis and the log claims it), then the rest.", ""]
    footer = ("\n\n---\n*Found in the fork `rmccann-hub/cyanrip` (branch "
              "`platterpus-fork`), which feeds the Platterpus ripper. Checked "
              "against `master` at `f8ebf48`. The fix is linked above; happy "
              "to open a PR if it helps.*")
    for n in range(1, COUNT + 1):
        title, body = issues[n]
        out += [f"## Item {n} of {COUNT}", "",
                f"**Title:** {title.replace('**', '')}", "",
                "<!-- BODY START -->", "", link_commits(body) + footer, "",
                "<!-- BODY END -->", ""]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", metavar="FILE",
                    help="exit 1 if FILE is not what this would generate")
    a = ap.parse_args()
    text = render()
    if a.check:
        have = pathlib.Path(a.check).read_text()
        if have != text:
            print(f"{a.check}: stale; regenerate with "
                  f"tools/gen-upstream-issues.py > {a.check}", file=sys.stderr)
            return 1
        print(f"{a.check}: current ({COUNT} issues)")
        return 0
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
