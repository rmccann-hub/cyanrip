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

"""Which CONTRACT SECTIONS changed between two commits. Derived, never read off.

ROUND 16 LAP 7 §H1 IS WHY THIS EXISTS. Our lap 6 told Platterpus the one row
the contract gained was in **P5**. It is in **P3**. Nobody had lied and no
generator was wrong: the regeneration diff showed a single added table row that
looked like a message inventory entry, and "message inventory" is P5, so the
label was written from that inference and never checked against the document.
A claim about a generated artifact, made by reading a diff hunk instead of the
artifact.

**P3 AND P5 MEAN OPPOSITE THINGS TO A CONSUMER**, which is what makes it worth
a tool rather than a note. A P5 row is a fatal string a consumer must surface.
A P3 row is unstable wording, and the legend says of exactly this one that it
never reaches a logfile directly -- so **its absence from a log is not evidence
it never fired**. Telling a consumer a P3 row was P5 invites them to treat
unstable wording as a fatal contract string.

So: never describe this delta again. Run it and paste it.

    tools/contract-delta.py a9aedf0 0cd611a
"""

import argparse
import hashlib
import re
import subprocess
import sys

# A section heading in PROVIDER-CONTRACT.md. Captured rather than assumed: the
# document's own headings are the only authority on which sections exist, and a
# hardcoded list would go stale exactly when a section is added.
HEADING = re.compile(r"(?m)^(## P[0-9]+[a-z]?\b.*)$")


def contract_at(ref):
    r = subprocess.run(["git", "show", f"{ref}:PROVIDER-CONTRACT.md"],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"cannot read PROVIDER-CONTRACT.md at {ref}: "
                 f"{r.stderr.strip()}")
    return r.stdout


def sections(text):
    """{heading: body}, in document order, from the document's own headings."""
    parts = HEADING.split(text)
    out, i = {}, 1
    while i < len(parts) - 1:
        out[parts[i].strip()] = parts[i + 1]
        i += 2
    return out


def rows(body):
    return [l for l in body.splitlines() if l.startswith("| `")]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--rows", action="store_true",
                    help="also print the added and removed table rows")
    args = ap.parse_args()

    a, b = sections(contract_at(args.old)), sections(contract_at(args.new))
    names = list(a) + [n for n in b if n not in a]

    h = lambda s: hashlib.sha256(s.encode()).hexdigest()[:12]
    changed = []
    print(f"PROVIDER-CONTRACT.md   {args.old} -> {args.new}\n")
    for n in names:
        if n not in a:
            print(f"  ADDED      {n}"); changed.append(n); continue
        if n not in b:
            print(f"  REMOVED    {n}"); changed.append(n); continue
        same = a[n] == b[n]
        if not same:
            changed.append(n)
        print(f"  {'identical ' if same else '*** DIFFERS'} {n}"
              f"{'' if same else f'   {h(a[n])} -> {h(b[n])}'}")

    print()
    if not changed:
        print("No section changed. If the file differs at all it is in the "
              "preamble\n-- the banner and the source anchor live above the "
              "first heading.")
    else:
        print(f"{len(changed)} section(s) changed: {', '.join(changed)}")
        print("\nNAME THE SECTION FROM THIS OUTPUT, NEVER FROM READING A DIFF "
              "HUNK.\nP3 and P5 mean opposite things to a consumer: P5 is a "
              "fatal string they must\nsurface, P3 is unstable wording whose "
              "absence from a log proves nothing.")

    if args.rows:
        for n in changed:
            ra, rb = set(rows(a.get(n, ""))), set(rows(b.get(n, "")))
            for r in sorted(rb - ra):
                print(f"\n  + {n}\n    {r}")
            for r in sorted(ra - rb):
                print(f"\n  - {n}\n    {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
