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

"""HANDSHAKE-ROUND-DIGEST, per PROTOCOL.md v3 §5a.

The checksum that lets two projects prove they hold the same record. It exists
because both gates reported healthy through thirteen laps that one side never
received: a gate reading only its own directory cannot tell "they agreed" from
"they never got it", and reports green for both.

The construction is fixed by the spec so two independent implementations agree:

  1. sha256 of each lap file's EXACT bytes
  2. one line per lap: "<lap>\\t<HANDSHAKE-FROM>\\t<sha256 hex>"
  3. sort those lines byte-wise ascending
  4. join with "\\n", append a trailing "\\n", encode UTF-8
  5. digest = first 16 hex chars of sha256 of that, plus the lap count

Deliberately keyed on the lap number and HANDSHAKE-FROM rather than the
filename: filenames are local layout, the two projects already differ, and a
digest depending on them would disagree by construction. Deliberately over exact
bytes: a lap reflowed or re-encoded in transit must not pass as the original.

Usage:
    tools/round-digest.py 8            # our laps plus docs/handshake/inbound/
    tools/round-digest.py 8 --verbose  # show every line that went in
"""

import argparse
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HS = ROOT / "docs" / "handshake"

LAP_RE = re.compile(r"^HANDSHAKE-LAP:[ \t]*(\d+)[ \t]*$", re.M)
ROUND_RE = re.compile(r"^HANDSHAKE-ROUND:[ \t]*(\d+)[ \t]*$", re.M)
FROM_RE = re.compile(r"^HANDSHAKE-FROM:[ \t]*(\S+)[ \t]*$", re.M)


def lap_lines(round_no):
    """One "<lap>\\t<from>\\t<sha>" line per lap file of this round we hold.

    Both directories: ours and inbound/. The digest covers the record, and the
    record is everything the writer holds -- its own laps and the other side's
    alike. A digest over only our own outbox would agree with itself forever,
    which is the defect this replaces.
    """
    out = []
    for path in sorted(list(HS.glob("round-*.md")) +
                       list((HS / "inbound").glob("round-*.md"))):
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        rm = ROUND_RE.search(text)
        if not rm or int(rm.group(1)) != round_no:
            continue
        lm = LAP_RE.search(text)
        fm = FROM_RE.search(text)
        if not lm or not fm:
            # A file with no lap or no author cannot be placed in the record,
            # and guessing at either is how a digest stops meaning anything.
            print(f"warning: {path.name} declares no "
                  f"{'HANDSHAKE-LAP' if not lm else 'HANDSHAKE-FROM'} "
                  "-- excluded from the digest", file=sys.stderr)
            continue
        out.append(f"{lm.group(1)}\t{fm.group(1)}\t"
                   f"{hashlib.sha256(raw).hexdigest()}")
    return sorted(out)


def digest(round_no):
    lines = lap_lines(round_no)
    blob = ("\n".join(lines) + "\n").encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16], len(lines), lines


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("round", type=int)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    d, n, lines = digest(args.round)
    if args.verbose:
        for line in lines:
            print(line, file=sys.stderr)
    print(f"HANDSHAKE-ROUND-DIGEST: sha256/16 = {d} over {n} lap(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
