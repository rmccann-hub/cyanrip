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

"""Decide whether a release may be tagged, and what the tag says.

`.github/workflows/tag-release.yml` runs this and then creates the tag. Every
decision is made here rather than in the workflow's shell, so the suite can test
it (`tests/tag_release.py`) on a repository it builds; a workflow can only be
tested by running it, and creating a tag is not something to try out.

    tag-release-check.py RELEASE COMMIT [--ref origin/platterpus-fork]
                         [--repo DIR] [--message-file PATH]

RELEASE is the version exactly as `release-manifest.json` names it, such as
`0.9.4-rc2+platterpus.22`, and COMMIT is a full 40-character SHA. The release
may be tagged only when all of these hold:

  * COMMIT is a commit in the repository and an ancestor of REF, the
    integration branch; a commit only a topic branch holds is not a release;
  * the manifest **at REF** names RELEASE, in at least one channel;
  * every channel naming RELEASE names COMMIT, resolved to its full SHA (the
    manifest abbreviates, and an abbreviation git cannot resolve to exactly one
    commit is a refusal, not a prefix match);
  * those channels agree on `release_seq`.

**The manifest names only the current channel heads**, so only a release that
is still published on some channel can be tagged by this. Older releases are
in `docs/release-ledger.tsv` alone.

**Ordering is `release_seq`, never the version.** The part of ours that
advances, `+platterpus.N`, is SemVer build metadata, which precedence ignores,
so the annotated message records `release_seq` for anyone ordering tags. The
tag NAME is `platterpus-fork-rN`, with N read from that build metadata: a name,
which decides nothing.

Prints `tag=<name>` on stdout. Exit codes:

  0  create the tag
  1  refused, with the reason on stderr
  2  usage
  3  the tag already exists at this commit; nothing to do

A tag that exists at a different commit is a refusal: a tag is never moved.
"""

import argparse
import json
import re
import subprocess
import sys

TAG_PREFIX = "platterpus-fork-r"
BUILD = re.compile(r"\+platterpus\.([1-9][0-9]*)$")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True,
                       text=True, encoding="utf-8")
    return p.returncode, p.stdout.strip()


def refuse(msg):
    print(f"tag-release-check: REFUSED: {msg}", file=sys.stderr)
    sys.exit(1)


def resolve(repo, rev):
    """A full commit SHA for REV, or None when git cannot name exactly one."""
    rc, out = git(repo, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
    return out if rc == 0 and FULL_SHA.match(out) else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("release")
    ap.add_argument("commit")
    ap.add_argument("--ref", default="origin/platterpus-fork")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--message-file")
    a = ap.parse_args()

    m = BUILD.search(a.release)
    if not m or not re.match(r"^[0-9A-Za-z.+-]+$", a.release):
        refuse(f"{a.release!r} is not a release of this fork: a version ends "
               "in +platterpus.N, as release-manifest.json writes it")
    if not FULL_SHA.match(a.commit):
        refuse(f"{a.commit!r} is not a full 40-character lowercase commit SHA")
    if resolve(a.repo, a.commit) != a.commit:
        refuse(f"commit {a.commit} is not in this repository")
    tip = resolve(a.repo, a.ref)
    if tip is None:
        refuse(f"{a.ref} does not resolve; nothing to check the commit against")
    rc, _ = git(a.repo, "merge-base", "--is-ancestor", a.commit, tip)
    if rc != 0:
        refuse(f"commit {a.commit} is not on {a.ref} (at {tip})")

    rc, text = git(a.repo, "show", f"{tip}:release-manifest.json")
    if rc != 0:
        refuse(f"{a.ref} (at {tip}) has no release-manifest.json")
    try:
        channels = json.loads(text)["channels"]
    except (ValueError, KeyError, TypeError) as e:
        refuse(f"release-manifest.json at {tip} does not parse: {e}")
    named = {c: v for c, v in sorted(channels.items())
             if isinstance(v, dict) and v.get("version") == a.release}
    if not named:
        refuse(f"release-manifest.json at {tip} does not name {a.release}; "
               "it names " + ", ".join(f"{c} {v.get('version')}" for c, v in
                                       sorted(channels.items())))
    for c, v in named.items():
        full = resolve(a.repo, str(v.get("commit", "")))
        if full != a.commit:
            refuse(f"the manifest's {c} channel names {a.release} at "
                   f"{v.get('commit')!r}, which is "
                   + (f"{full}" if full else "not exactly one commit here")
                   + f", not {a.commit}")
    seqs = {v.get("release_seq") for v in named.values()}
    if len(seqs) != 1 or not isinstance(next(iter(seqs)), int):
        refuse(f"the channels naming {a.release} disagree on release_seq: "
               f"{sorted(map(str, seqs))}")
    seq = seqs.pop()
    rounds = sorted({str(v.get("handshake_round")) for v in named.values()})

    tag = TAG_PREFIX + m.group(1)
    existing = resolve(a.repo, f"refs/tags/{tag}")
    if existing == a.commit:
        print(f"tag={tag}")
        print(f"tag-release-check: {tag} already exists at {a.commit}; "
              "nothing to do", file=sys.stderr)
        sys.exit(3)
    if existing is not None:
        refuse(f"{tag} already exists at {existing}; a tag is never moved")

    message = (
        f"cyanrip-fork {a.release}\n"
        f"\n"
        f"commit: {a.commit}\n"
        f"release_seq: {seq}\n"
        f"channels: {', '.join(named)}\n"
        f"handshake_round: {', '.join(rounds)}\n"
        f"manifest: release-manifest.json at {tip}\n"
        f"\n"
        f"Order releases by release_seq, never by this version: the part that\n"
        f"advances, +platterpus.N, is SemVer build metadata, which precedence\n"
        f"ignores.\n")
    if a.message_file:
        with open(a.message_file, "w", encoding="utf-8") as f:
            f.write(message)
    print(f"tag={tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
