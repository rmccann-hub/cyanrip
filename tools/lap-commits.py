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

"""§C's commit list, derived from git. Never written from memory again.

ROUND 16 LAP 10 §D IS WHY THIS EXISTS. Our lap 9 §C said "three commits since
lap 8" and named them in prose. Platterpus derived it from our own repository:
**five**, measuring from the send pin, or **nine** from lap 8's
`HANDSHAKE-FROM-COMMIT`. Two were missing, and one of them was `7ace6e5` -- the
commit that corrected the Run A block, the procedure for the single artifact
the round is waiting on. A reader of lap 9 alone would not have known the block
had moved.

**THE DEFECT IS THE MISSING BASELINE, NOT THE MISSING TWO.** "Three commits
since lap 8" names no range, so it is unfalsifiable in the same way "EAC
reports N" is: there is nothing to re-derive it against. Platterpus could only
check it by GUESSING two baselines and reporting both. So every line this tool
prints names the range it counted over, and `--check` refuses a lap that does
not paste one.

Baseline is the previous lap's `HANDSHAKE-FROM-COMMIT`, because that is a wire
field BOTH SIDES HOLD and can resolve independently. "Pin lap N as sent" is a
local commit-message convention the other side cannot check, so it is printed
as a secondary, labelled, never as the number.

It judges nothing. §C asks for "commits, flagging log-text changes", and
whether a log line's TEXT moved is a reading of the diff -- so the tool reports
which commits touch a `cyanrip_log()` call site and says out loud that reading
them is yours. Same division as contract-delta.py: structure here, judgement in
the lap.

    tools/lap-commits.py 16 11              # what lap 11 of round 16 should say
    tools/lap-commits.py --since 8880d8f    # an explicit baseline
    tools/lap-commits.py 16 11 --check docs/handshake/round-16-lap-11.md
"""

import argparse
import glob
import os
import re
import subprocess
import sys

# Paths whose change moves the BINARY. docs/handshake/round-*.md is in the list
# and is not an oversight: since r3 the handshake state is compiled in by
# tools/gen-handshake-state.py, so adding a lap file changes the `Handshake:`
# line. A pin chosen with `git log -- src/ meson.build` is therefore wrong, and
# one was.
BINARY = ("src/", "meson.build", "meson_options.txt", "docs/handshake/round-")

LAP_FILE = "docs/handshake/round-{:02d}-lap-{:02d}.md"
FROM_COMMIT = re.compile(r"(?m)^HANDSHAKE-FROM-COMMIT:\s*(\S+)")


def git(*a):
    r = subprocess.run(["git", *a], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"git {' '.join(a)}: {r.stderr.strip()}")
    return r.stdout


def previous_lap(rnd, lap):
    """The newest lap of OURS below `lap`, by declared number, not filename.

    Laps are ours only if they are in docs/handshake/ -- inbound/ is theirs and
    their FROM-COMMIT names THEIR tree, which no ref here can resolve.
    """
    found = []
    for p in glob.glob("docs/handshake/round-*-lap-*.md"):
        t = os.path.basename(p)
        m = re.fullmatch(r"round-(\d+)-lap-(\d+)\.md", t)
        if m and int(m[1]) == rnd and int(m[2]) < lap:
            found.append((int(m[2]), p))
    if not found:
        return None, None
    n, p = max(found)
    m = FROM_COMMIT.search(open(p, encoding="utf-8").read())
    if not m:
        sys.exit(f"{p} declares no HANDSHAKE-FROM-COMMIT -- cannot baseline "
                 f"against it. Pass --since explicitly and say so in the lap.")
    return n, m[1]


def send_pin(lap):
    """The "Pin lap N as sent" commit, if the convention was followed."""
    out = git("log", "--format=%H %s", "--grep", f"^Pin lap {lap} as sent")
    return out.split()[0][:7] if out.strip() else None


def classify(sha):
    paths = git("show", "--name-only", "--format=", sha).split()
    binary = [p for p in paths if p.startswith(BINARY)]
    diff = git("show", "--format=", "--unified=0", "--", "src/", sha)
    logsite = any(re.match(r"[+-][^+-]", l) and "cyanrip_log(" in l
                  for l in diff.splitlines())
    return paths, binary, logsite


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("round", type=int, nargs="?")
    ap.add_argument("lap", type=int, nargs="?")
    ap.add_argument("--since", help="baseline ref, overriding the derivation")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--check", metavar="LAPFILE",
                    help="fail unless LAPFILE pastes the summary line")
    args = ap.parse_args()

    if args.since:
        base, why, prev = args.since, "given on the command line", None
    else:
        if args.round is None or args.lap is None:
            ap.error("give ROUND and LAP, or --since")
        prev, base = previous_lap(args.round, args.lap)
        if base is None:
            sys.exit(f"no lap of ours below round {args.round} lap {args.lap} "
                     f"-- pass --since")
        why = f"lap {prev}'s own HANDSHAKE-FROM-COMMIT"

    shas = git("log", "--format=%h", f"{base}..{args.head}").split()
    shas.reverse()

    summary = (f"§C baseline `{base}` ({why}) .. `{git('rev-parse', '--short', args.head).strip()}`: "
               f"**{len(shas)} commit(s)**, "
               f"{sum(1 for s in shas if classify(s)[1])} touching the binary.")

    if args.check:
        text = open(args.check, encoding="utf-8").read()
        if summary in text:
            print(f"OK    {args.check} pastes the derived line")
            return 0
        print(f"FAIL  {args.check} does not paste the derived §C line.\n"
              f"      expected, verbatim:\n        {summary}\n"
              f"      A §C with no range in it cannot be re-derived by the "
              f"other side,\n      which is the whole of lap 10 §D.",
              file=sys.stderr)
        return 1

    print(f"§C -- commits since {why}\n")
    print(f"  baseline  {base}   ({why})")
    if prev is not None:
        sp = send_pin(prev)
        print(f"  secondary {sp or '(none found)':<9}"
              f"   \"Pin lap {prev} as sent\" -- LOCAL CONVENTION, they cannot "
              f"resolve it.\n{'':13}Never quote this as the number; it "
              f"undercounts by the lap's own file.")
    print()

    logsites = []
    for s in shas:
        paths, binary, logsite = classify(s)
        subj = git("log", "--format=%s", "-1", s).strip()
        if logsite:
            logsites.append(s)
        print(f"  {s}  {'[binary]' if binary else '[docs]  '}"
              f"{' [log-site]' if logsite else ''}  {subj}")

    print(f"\n{summary}\n")
    if logsites:
        print(f"{len(logsites)} commit(s) change a `cyanrip_log()` call site: "
              f"{', '.join(logsites)}.\nWHETHER THE TEXT MOVED IS YOURS TO "
              f"READ -- this tool found the call sites,\nit did not compare "
              f"the strings. §D is the section that answers it.")
    else:
        print("No commit changes a `cyanrip_log()` call site in `src/`. That "
              "is evidence for\n§D's \"no changes\", not a substitute for it: "
              "the cue writer and the compiled-in\n`Handshake:` line move "
              "log text without touching one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
