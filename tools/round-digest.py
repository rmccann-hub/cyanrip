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
FENCE_RE = re.compile(r"^```.*?^```", re.M | re.S)


def is_a_lap(text):
    """PROTOCOL.md v4 §5a: one lap iff ROUND, LAP and FROM each appear exactly
    once after fenced blocks are stripped.

    Returns (round, lap, from) or None.

    Derived from §2 rule 3 -- a field declared twice is ambiguous and ambiguity
    is never resolved by taking the first or the last -- so a file with two
    HANDSHAKE-LAP lines is not a lap, it is a file CONTAINING laps.

    Platterpus found this on their implementation's first run: a transport
    envelope carrying three laps verbatim declared three wire headers in its
    body, their enumerator took the first, and the envelope counted as a fourth
    lap 2. The digest was stable, reproducible, and described a record neither
    side held -- which under §4a puts the round into RECONCILE, a state
    exchanging files cannot exit because nothing is missing.

    Deliberately NOT a filename or container-format exclusion. A list only ever
    excludes the container someone has already met; this excludes the next one.
    """
    stripped = FENCE_RE.sub("", text)
    got = []
    for rx in (ROUND_RE, LAP_RE, FROM_RE):
        m = rx.findall(stripped)
        if len(m) != 1:
            return None
        got.append(m[0])
    return got[0], got[1], got[2]


def lap_lines(round_no, exclude=()):
    """One "<lap>\\t<from>\\t<sha>" line per lap file of this round we hold.

    Both directories: ours and inbound/. The digest covers the record, and the
    record is everything the writer holds -- its own laps and the other side's
    alike. A digest over only our own outbox would agree with itself forever,
    which is the defect this replaces.
    """
    out = []
    excluded = set()
    for path in sorted(list(HS.glob("round-*.md")) +
                       list((HS / "inbound").glob("round-*.md"))):
        if path.name in exclude:
            excluded.add(path.name)
            continue
        raw = path.read_bytes()
        parts = is_a_lap(raw.decode("utf-8", errors="replace"))
        if parts is None:
            continue
        rnd, lap, frm = parts
        if int(rnd) != round_no:
            continue
        out.append(f"{lap}\t{frm}\t{hashlib.sha256(raw).hexdigest()}")

    # An exclusion that matched nothing is a MANUFACTURED MISMATCH, and it is
    # indistinguishable from a real one -- inside the tool implementing the one
    # §5a rule neither side may override.
    #
    # Ours matched on basename and silently dropped nothing when the name did
    # not match, so `--exclude docs/handshake/inbound/round-09-lap-04.md`
    # printed a confident digest over the full set including the lap it had been
    # told to remove. Platterpus found it in their implementation (round 9 lap 6
    # §F3) by attacking their own diagnosis before publishing it; we had the
    # identical defect and had not asked the question. It is this project's own
    # "can this check be satisfied by finding nothing?" -- unasked, in the check
    # that matters most.
    missed = set(exclude) - excluded
    if missed:
        raise SystemExit(
            "refusing to print a digest: --exclude matched nothing for "
            + ", ".join(sorted(missed))
            + "\nPass the FILENAME as it appears in the record, not a path. A "
              "silently ignored exclusion produces a digest over the wrong set "
              "and is indistinguishable from a genuine mismatch.")
    return sorted(out)


def digest_of_lines(lines):
    """The construction itself, separated so it can be tested on synthetic
    records rather than only on this repository's own history -- a digest that
    can only be exercised against one real record cannot be shown to be
    sensitive to anything."""
    blob = ("\n".join(sorted(lines)) + "\n").encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def digest(round_no, exclude=()):
    lines = lap_lines(round_no, exclude)
    return digest_of_lines(lines), len(lines), lines


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("round", type=int)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--exclude", metavar="FILENAME", action="append", default=[],
                    help="the lap being written, or -- when VERIFYING a peer's "
                         "declared digest -- the lap THEY wrote. v4 §5a: the "
                         "writer excludes itself and the reader excludes that "
                         "same file, never its own newest lap. Getting this "
                         "backwards makes the two sides disagree forever. "
                         "Repeatable: reproducing an older declaration means "
                         "dropping every lap filed since, which one value "
                         "cannot express. Refuses if a name matches nothing.")
    args = ap.parse_args()

    d, n, lines = digest(args.round, args.exclude)
    if args.verbose:
        for line in lines:
            print(line, file=sys.stderr)
    print(f"HANDSHAKE-ROUND-DIGEST: sha256/16 = {d} over {n} lap(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
