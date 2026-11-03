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

"""Generate docs/upstream/issues-to-file.md: the twenty-eight upstream bug
reports, rendered as issues ready to paste into cyanreg/cyanrip's tracker.

The reports themselves are written in two files, and this renders them:

  * `docs/upstream/defect-reports.md`, reports 1-7 and 9-28;
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

Which commits are upstream's depends on how far our mirror of upstream's
`master` reaches, and that differs between clones: on 2026-11-02 this clone's
`master` branch sat at `7dbe56a` while CI fetched `648b1dd`, so a file that
passed here failed there. So the file names the upstream commit its links
were resolved against, and `--check` renders against that commit, not against
whatever the clone's refs hold: every clone holding it gives one answer. A
render takes upstream's tip from `origin/master`, which any fetch of it
moves, before the `master` branch, which only a deliberate update moves.
"""

import argparse
import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORK = "https://github.com/rmccann-hub/cyanrip"
UPSTREAM = "https://github.com/cyanreg/cyanrip"
DEFECTS = "docs/upstream/defect-reports.md"
CACHEMODEL = "docs/upstream-cachemodel-report.md"
COUNT = 28
# Where the operator filed the first FILED_COUNT, as one issue, on 2026-10-16.
# The rest are drafted and not filed, and the header says so.
FILED_COUNT = 23
FILED = f"{UPSTREAM}/issues/167"


# The commit a report was checked at. Reports 1-18 were checked at the commit
# the defect file's header names; a later report names its own on its first
# **Where:** line ("... at `b40c1f0`"), and the footer says that one. Read
# from the reports, so the footer cannot claim a check nobody made.
HEADER_AT = re.compile(r"\*\*Checked against upstream `master` at `([0-9a-f]{7})`")
WHERE_AT = re.compile(r"\A\*\*Where:\*\*[^\n]* at `([0-9a-f]{7})`")
# The upstream commit a rendered file's links were resolved against.
PINNED_AT = re.compile(
    r"^\*\*Links were resolved against upstream's `master` at "
    r"`([0-9a-f]{7,40})`\*\*", re.M)


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, encoding="utf-8")


def is_commit(sha, ref):
    """A commit this checkout's history or our mirror of upstream reaches.
    Not any object the clone holds: a clone that had fetched upstream's
    648b1dd to read it linked that commit as the fork's, a link to nothing,
    and rendered a file CI's clone, without the object, called stale."""
    r = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e",
                        sha + "^{commit}"], capture_output=True)
    if r.returncode != 0:
        return False
    return any(subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", sha, tip],
        capture_output=True).returncode == 0 for tip in ("HEAD", ref) if tip)


def upstream_tip():
    """Our mirror of upstream's `master`, as a full commit ID: its
    remote-tracking copy, which any fetch of it moves, before the local
    branch, which only a deliberate update moves and which was two syncs
    stale here on 2026-11-02. None when the clone has neither."""
    for ref in ("origin/master", "master"):
        r = git("rev-parse", "-q", "--verify", ref + "^{commit}")
        if r.returncode == 0:
            return r.stdout.strip()
    return None


def is_upstream(sha, ref):
    """A commit upstream made, which the fork merged and did not write. Its
    link goes to upstream: report 8 linked `c431d58` and `f8ebf48`, both
    upstream's, as commits of the fork (the operator, 2026-10-15)."""
    return ref is not None and subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", sha, ref],
        capture_output=True).returncode == 0


def link_commits(text, ref):
    def link(m):
        sha = m.group(1)
        if not is_commit(sha, ref):
            return m.group(0)
        return f"[`{sha}`]({UPSTREAM if is_upstream(sha, ref) else FORK}/commit/{sha})"
    return re.sub(r"`([0-9a-f]{7})`", link, text)


def render(ref, short):
    """The file, its links resolved against upstream's `master` at REF, a
    full commit ID, which the header names as SHORT."""
    dr = (ROOT / DEFECTS).read_text(encoding="utf-8")
    cm = (ROOT / CACHEMODEL).read_text(encoding="utf-8")

    issues = {}
    m = HEADER_AT.search(dr)
    if not m:
        sys.exit(f"gen-upstream-issues: {DEFECTS} no longer names the commit "
                 "its reports were checked at")
    checked_at = m.group(1)
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
        w = WHERE_AT.search(body)
        issues[n] = (title, body, w.group(1) if w else checked_at)
    m = re.search(r"(?ms)^## Title\s*\n+(.+?)\n\s*\n## Body", cm)
    if not m or 8 in issues:
        sys.exit(f"gen-upstream-issues: report 8 is {CACHEMODEL}'s, and "
                 f"that file must carry a '## Title' then a '## Body'")
    issues[8] = (m.group(1).strip(), cm.split("\n## Body", 1)[1].strip(),
                 checked_at)
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
        "public, and every upstream commit links to upstream.", "",
        f"**Links were resolved against upstream's `master` at `{short}`**, "
        "our mirror's tip when this was rendered: a commit it reaches links "
        "to upstream, and any other commit our history reaches links to the "
        "fork. `--check` renders against that commit, not against what a "
        "clone's `master` holds, so every clone holding it gives the same "
        "answer; `git fetch origin master` brings it.", "",
        f"**Items 1 to {FILED_COUNT} were filed on 2026-10-16**, by the "
        "operator, as one issue combining them in the order of importance "
        f"below: <{FILED}>. That link is the operator's word; this file's "
        "generator does not read upstream's tracker. An item asked for as an "
        "issue of its own is pasted from here. "
        f"**Items {FILED_COUNT + 1} to {COUNT} are not filed yet**: they go "
        "to the same issue as a comment, or each as an issue of its own, "
        "as the operator decides.", "",
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
        "corrupted audio with `Ripping errors: 0`), 19 (with libcdio 2.3.0 or "
        "later, every image rip without `-s` stops at `Offset is unset!`), "
        "1 and 2 (a hung or cut-off "
        "process with the drive held), 4 and 5 (`-H` silently drops "
        "de-emphasis and the log claims it), then the rest.", ""]
    for n in range(1, COUNT + 1):
        title, body, at = issues[n]
        footer = ("\n\n---\n*Found in the fork `rmccann-hub/cyanrip` (branch "
                  "`platterpus-fork`), which feeds the Platterpus ripper. "
                  f"Checked against `master` at `{at}`. The fix is linked "
                  "above; happy to open a PR if it helps.*")
        out += [f"## Item {n} of {COUNT}", "",
                f"**Title:** {title.replace('**', '')}", "",
                "<!-- BODY START -->", "", link_commits(body, ref) + footer, "",
                "<!-- BODY END -->", ""]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", metavar="FILE",
                    help="exit 1 if FILE is not what this would generate")
    a = ap.parse_args()
    if git("rev-parse", "--git-dir").returncode != 0:
        sys.exit("gen-upstream-issues: not a git checkout; commit links "
                 "cannot be told from other hex strings without one")
    if a.check:
        have = pathlib.Path(a.check).read_text(encoding="utf-8")
        m = PINNED_AT.search(have)
        if not m:
            print(f"{a.check}: stale; it names no upstream commit its links "
                  "were resolved against. Regenerate with "
                  f"tools/gen-upstream-issues.py > {a.check}", file=sys.stderr)
            return 1
        r = git("rev-parse", "-q", "--verify", m.group(1) + "^{commit}")
        if r.returncode != 0:
            print(f"{a.check}: its links were resolved against upstream's "
                  f"`master` at {m.group(1)}, which this clone does not hold; "
                  "`git fetch origin master` brings it", file=sys.stderr)
            return 1
        text = render(r.stdout.strip(), m.group(1))
        if have != text:
            print(f"{a.check}: stale; regenerate with "
                  f"tools/gen-upstream-issues.py > {a.check}", file=sys.stderr)
            return 1
        print(f"{a.check}: current ({COUNT} issues, links resolved against "
              f"upstream's master at {m.group(1)})")
        return 0
    tip = upstream_tip()
    if tip is None:
        sys.exit("gen-upstream-issues: this clone has no mirror of upstream's "
                 "master, origin/master or master, to tell upstream's commits "
                 "from the fork's; `git fetch origin master` brings it")
    short = git("rev-parse", "--short=7", tip).stdout.strip()
    sys.stdout.write(render(tip, short))
    return 0


if __name__ == "__main__":
    sys.exit(main())
