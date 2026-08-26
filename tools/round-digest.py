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
    tools/round-digest.py 8 --list     # every candidate FILE, in or out, and why
    tools/round-digest.py 8 --check    # re-derive every declaration in the round
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


def candidates():
    """Every file the enumerator looks at, ours and inbound/, in one order.

    Separated from the filtering so `--list` reports on the same set the digest
    walks rather than on a second, hand-kept idea of what the record contains.
    """
    return sorted(list(HS.glob("round-*.md")) +
                  list((HS / "inbound").glob("round-*.md")))


def matches_exclude(path, exclude):
    """Whether one --exclude token names this file.

    A bare basename matches, and so does any repo-relative path whose tail this
    file's path ends with -- which is what makes an AMBIGUOUS basename
    disambiguable at all. See lap_lines(): a token matching two files is a
    refusal, not a double exclusion.
    """
    rel = str(path)
    for tok in exclude:
        tok = tok.strip()
        if not tok:
            continue
        if path.name == tok or rel.endswith("/" + tok.lstrip("./")) or rel == tok:
            return True
    return False


def survey(round_no, exclude=()):
    """Per-FILE verdicts: (path, line-or-None, reason).

    `line` is the "<lap>\\t<from>\\t<sha>" string when the file is enumerated,
    None otherwise, and `reason` says which it was and why. This exists because
    a digest is a single opaque number: when two sides disagree, the count is
    the only clue, and "over 4" against "over 6" does not say WHICH two. Round 9
    lap 8 asked for exactly this output and had to reconstruct our record by
    exhaustive search over subsets to ask the question at all.
    """
    out = []
    for path in candidates():
        if matches_exclude(path, exclude):
            out.append((path, None, "excluded by --exclude"))
            continue
        raw = path.read_bytes()
        parts = is_a_lap(raw.decode("utf-8", errors="replace"))
        if parts is None:
            out.append((path, None, "not a lap: " + why_not_a_lap(raw)))
            continue
        rnd, lap, frm = parts
        if int(rnd) != round_no:
            out.append((path, None, f"round {rnd}, not {round_no}"))
            continue
        out.append((path, f"{lap}\t{frm}\t{hashlib.sha256(raw).hexdigest()}",
                    "enumerated"))
    return out


def why_not_a_lap(raw):
    """The counts that made is_a_lap() refuse, so `--list` names the field.

    Reports what was counted rather than a category, because "malformed" is the
    answer that sends someone to read the whole file. A transport envelope and a
    truncated lap are both "not a lap" and the remedies are opposite.
    """
    stripped = FENCE_RE.sub("", raw.decode("utf-8", errors="replace"))
    bits = []
    for name, rx in (("ROUND", ROUND_RE), ("LAP", LAP_RE), ("FROM", FROM_RE)):
        n = len(rx.findall(stripped))
        if n != 1:
            bits.append(f"{name}x{n}")
    return ", ".join(bits) if bits else "unknown"


def lap_lines(round_no, exclude=()):
    """One "<lap>\\t<from>\\t<sha>" line per lap file of this round we hold.

    Both directories: ours and inbound/. The digest covers the record, and the
    record is everything the writer holds -- its own laps and the other side's
    alike. A digest over only our own outbox would agree with itself forever,
    which is the defect this replaces.
    """
    rows = survey(round_no, exclude)
    out = [line for _, line, _ in rows if line is not None]
    excluded = {p.name for p, line, r in rows if r == "excluded by --exclude"}

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
    missed = [t for t in exclude
              if not any(matches_exclude(p, [t]) for p, _, _ in rows)]
    if missed:
        raise SystemExit(
            "refusing to print a digest: --exclude matched nothing for "
            + ", ".join(sorted(missed))
            + "\nPass the FILENAME as it appears in the record, or a "
              "repo-relative path. A silently ignored exclusion produces a "
              "digest over the wrong set and is indistinguishable from a "
              "genuine mismatch.")

    # AND THE MIRROR, which is the same defect pointing the other way and which
    # both projects missed. The refusal above catches a token matching NOTHING.
    # A token matching MORE THAN ONE file was excluding all of them, silently,
    # and that becomes reachable the moment two laps cross at one number --
    # which round 14 did at lap 18, ours and theirs. `--exclude
    # round-14-lap-18.md` then dropped THEIRS as well as ours, and the digest
    # came out over 20 rows either way: same count, different set, different
    # hash. Our own seam-check read that as "a sent lap's bytes changed", which
    # is the wrong diagnosis for a right finding.
    #
    # Refusing rather than guessing: the writer's rule is "exclude yourself",
    # and only the caller knows which of two same-numbered files is theirs.
    for tok in exclude:
        hits = [p for p, _, _ in rows if matches_exclude(p, [tok])]
        if len(hits) > 1:
            raise SystemExit(
                f"refusing to print a digest: --exclude {tok} matches "
                f"{len(hits)} files:\n  "
                + "\n  ".join(sorted(str(h) for h in hits))
                + "\nTwo laps crossed at one number, so the basename no longer "
                  "identifies one file. Pass the repo-relative path of the lap "
                  "carrying this digest -- excluding both silently produces a "
                  "digest over the wrong set, which is what this refusal is "
                  "for.")
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


# Anchored to the START of the field, not searched within it. Every lap of
# round 9 carries prose in this field, and three of them quote a SECOND digest
# in it -- round 8's, or the peer's declaration being verified. A search finds
# whichever comes first in the sentence and reports it as the declaration:
# round 9 lap 1 says "not computable ... For round 8: sha256/16 = 81415fe9..."
# and the first version of this checker read round 8's number as round 9's,
# then reported the lap as a mismatch. It was the checker that was wrong.
#
# The rule is derived rather than chosen: the field's machine-readable part is
# exactly what round-digest.py PRINTS, and it prints the clause immediately
# after the colon. Anything further along is commentary. A field not beginning
# with the clause declares nothing machine-readable, which is the honest
# reading of lap 1 -- it says "not computable" and means it.
#
# This is the verdict-field prose question of round 9 §I arriving in a second
# field, and it wants the same v5 answer: the value is the leading token
# sequence, prose follows and is ignored.
DECL_RE = re.compile(
    r"^HANDSHAKE-ROUND-DIGEST:[ \t]*sha256/16 = ([0-9a-f]{16}) over (\d+) lap",
    re.M)


def check_lap(path):
    """Re-derive the HANDSHAKE-ROUND-DIGEST a lap file declares.

    Returns (status, declared, computed, excluded) where status is one of
    "match", "mismatch", "undeclared", "not-a-lap".

    **The one defect this exists for, named because S-11 requires it: round 9
    lap 7.** It declared `53f0b465833ac845 over 4`, which is a real digest of a
    real set -- our holdings at an earlier moment, excluding the peer's lap 4,
    computed by a command run to VERIFY THEIR declaration and then transcribed
    into the writer's field. Platterpus could not reproduce it and recovered the
    subset by exhaustive search over every subset of the eight laps they hold.
    The same lap's section D is the section conceding that the previous lap had
    put the verifier's computation under the writer's field. It announced the
    correction and committed it again, in its own header, two screens apart.

    A digest is the one field a human cannot proofread: every wrong value looks
    exactly like every right one. So it must not be typed, and until now nothing
    stopped it being.

    The reconstruction: a lap's declaration covers the holdings that existed
    when it was written, which is every lap of the round numbered BELOW it --
    so excluding every lap numbered at or above L reproduces it. That is the
    writer's rule (exclude yourself, hold 1..L-1) and the reader's retroactive
    rule (exclude that lap and everything filed since) arriving at one set,
    which is why this works on the peer's laps as well as ours.

    It is a reconstruction and not a recording, and it can be wrong in exactly
    one way: a lap written while a lower-numbered lap was not yet held. That is
    not a false positive to be tolerated -- under §5a such a lap CANNOT declare
    a digest its reader reproduces, because the reader holds the lap the writer
    was missing. The check failing is the correct outcome, and lap 7 is the case
    in point: it was written holding lap 6 and declared a value computed before
    lap 6 arrived.
    """
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    parts = is_a_lap(text)
    if parts is None:
        return "not-a-lap", None, None, []
    rnd, lap, _frm = parts
    m = DECL_RE.search(FENCE_RE.sub("", text))
    if not m:
        return "undeclared", None, None, []
    declared = (m.group(1), int(m.group(2)))

    # By PATH, not by basename. The set this drops is "this lap and everything
    # filed since", by lap NUMBER and across both directories -- so when two
    # laps cross at one number it genuinely wants both, and naming them by
    # basename asked for one token to match two files. That reads as the
    # ambiguity --exclude now refuses, in the one caller where dropping both is
    # the correct answer. A path names exactly one file, so the same set is
    # dropped and nothing is ambiguous. Round 14 crossed at laps 2, 13, 16
    # and 18.
    drop = []
    for p in candidates():
        got = is_a_lap(p.read_bytes().decode("utf-8", errors="replace"))
        if got and int(got[0]) == int(rnd) and int(got[1]) >= int(lap):
            drop.append(str(p))
    d, n, _ = digest(int(rnd), drop)
    return ("match" if (d, n) == declared else "mismatch",
            declared, (d, n), sorted(drop))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("round", type=int)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--list", action="store_true", dest="list_",
                    help="every candidate file and whether it was enumerated, "
                         "with the reason when it was not. A count alone cannot "
                         "say WHICH laps two sides differ over.")
    ap.add_argument("--check", action="store_true",
                    help="re-derive the digest every lap of this round "
                         "declares. Non-zero on any mismatch.")
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

    if args.list_:
        for path, line, reason in survey(args.round, args.exclude):
            mark = "IN " if line else "out"
            rel = path.relative_to(HS)
            print(f"{mark} {rel}  ({reason})")
            if line and args.verbose:
                print(f"      {line}")

    if args.check:
        bad = 0
        for path in candidates():
            got = is_a_lap(path.read_bytes().decode("utf-8", errors="replace"))
            if not got or int(got[0]) != args.round:
                continue
            status, decl, comp, drop = check_lap(path)
            rel = path.relative_to(HS)
            if status == "undeclared":
                print(f"  -- {rel}: declares no digest")
                continue
            ds = f"{decl[0]} over {decl[1]}"
            if status == "match":
                print(f"  ok {rel}: {ds}")
            else:
                bad += 1
                print(f"FAIL {rel}: declares {ds}, "
                      f"re-derives {comp[0]} over {comp[1]}")
                print(f"       (excluding {', '.join(drop)})")
        if bad:
            print(f"\n{bad} declaration(s) do not re-derive.", file=sys.stderr)
            return 1
        return 0

    d, n, lines = digest(args.round, args.exclude)
    if args.verbose and not args.list_:
        for line in lines:
            print(line, file=sys.stderr)
    print(f"HANDSHAKE-ROUND-DIGEST: sha256/16 = {d} over {n} lap(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
