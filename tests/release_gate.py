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

"""Tests for tools/release-gate.py.

Every case here is a way the gate could wrongly permit a release. Platterpus's
round-7 verification section 11 supplied four of them from their own gate's
failure; the rest are the shapes this repo has already got wrong elsewhere.

The one that matters most is test_prose_about_a_verdict_is_not_a_verdict: a
mid-round file whose text says "this is not a closing GO" must not close the
round because a matcher found GO somewhere in it. Their gate closed a round off
a file that said HOLD in its first paragraph.
"""

import importlib.util
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "release_gate", HERE.parent / "tools" / "release-gate.py")
rg = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rg)

failures = 0


def check(cond, msg):
    global failures
    if not cond:
        failures += 1
        print(f"FAIL: {msg}", file=sys.stderr)


def gate(files):
    """Build a throwaway handshake dir and return (ok, problems)."""
    d = pathlib.Path(tempfile.mkdtemp())
    for name, body in files.items():
        (d / name).write_text(body, encoding="utf-8")
    return rg.check(rg.load_rounds(d))


GO = "HANDSHAKE-ROUND: 9\nHANDSHAKE-VERDICT: GO\n\n# round 9\n"


def test_go_closes():
    ok, _ = gate({"round-9.md": GO})
    check(ok, "a declared GO should close a round")


def test_open_does_not_close():
    ok, probs = gate({"round-9.md": GO.replace("GO", "OPEN")})
    check(not ok, "OPEN must not close a round")
    check(any("not closed" in p for p in probs), "OPEN should say why")


def test_hold_does_not_close():
    # A deliberate mid-round lap. This is the normal case, not an edge case.
    ok, _ = gate({"round-9.md": GO.replace("GO", "HOLD")})
    check(not ok, "HOLD must not close a round")


def test_unknown_verdict_does_not_close():
    # An unrecognised verdict is not evidence of agreement.
    ok, _ = gate({"round-9.md": GO.replace("GO", "PROBABLY-FINE")})
    check(not ok, "an unrecognised verdict must not close a round")


def test_missing_verdict_fails_closed():
    # The tempting shortcut is to treat a missing field as GO so old rounds
    # still pass. That puts the whole defect back through the fallback.
    ok, probs = gate({"round-9.md": "# round 9\n\nno field here at all\n"})
    check(not ok, "a round with no verdict field must fail closed")
    check(any("NO VERDICT" in p for p in probs),
          "a missing verdict should say so explicitly")


def test_prose_about_a_verdict_is_not_a_verdict():
    # The exact failure Platterpus reported: a file that says it is NOT a GO,
    # closing the round because a matcher found the word GO in the prose.
    body = ("HANDSHAKE-ROUND: 9\nHANDSHAKE-VERDICT: HOLD\n\n"
            "# round 9\n\n"
            "This is deliberately **not a closing GO**. The verdict is HOLD.\n"
            "Do not read `HANDSHAKE-VERDICT: GO` from this sentence.\n"
            "GO\nGONE\nHANDSHAKE-VERDICT: GO but indented below\n"
            "  HANDSHAKE-VERDICT: GO\n")
    ok, _ = gate({"round-9.md": body})
    check(not ok, "prose mentioning GO must not close a HOLD round")


def test_indented_declaration_is_not_a_declaration():
    body = "HANDSHAKE-ROUND: 9\n  HANDSHAKE-VERDICT: GO\n\n# round 9\n"
    ok, _ = gate({"round-9.md": body})
    check(not ok, "an indented verdict is quoted prose, not a declaration")


def test_two_verdicts_are_ambiguous_not_closed():
    body = ("HANDSHAKE-ROUND: 9\nHANDSHAKE-VERDICT: GO\n"
            "HANDSHAKE-VERDICT: HOLD\n\n# round 9\n")
    ok, _ = gate({"round-9.md": body})
    check(not ok, "two verdicts must be ambiguous, not closed on the first")


def test_grandfathered_set_is_pinned():
    # Grandfathering is by number and must stay a deliberate, visible act. If
    # this set grows, someone changed the gate rather than closing a round.
    check(rg.GRANDFATHERED == {5, 6},
          f"grandfathered set changed: {rg.GRANDFATHERED}")


def test_grandfathering_does_not_leak_to_new_rounds():
    ok, _ = gate({"round-99.md": "# round 99\n\nno verdict\n"})
    check(not ok, "a new round must not inherit the grandfathered exemption")


def test_mismatched_round_number_is_a_problem():
    body = "HANDSHAKE-ROUND: 8\nHANDSHAKE-VERDICT: GO\n\n# round 9\n"
    ok, probs = gate({"round-9.md": body})
    check(not ok, "a file declaring a different round number must not pass")
    check(any("declares" in p for p in probs), "should name the mismatch")


def test_one_open_round_blocks_even_when_others_closed():
    ok, _ = gate({"round-8.md": GO.replace("9", "8"),
                  "round-9.md": GO.replace("GO", "OPEN")})
    check(not ok, "one open round must block a release")


def test_empty_record_is_not_agreement():
    # Guarded in main() rather than check(); assert the loader reports nothing
    # so an empty directory can never look like "every round closed".
    d = pathlib.Path(tempfile.mkdtemp())
    check(rg.load_rounds(d) == [], "an empty directory must yield no rounds")


def test_the_real_tree_is_consistent():
    # The gate must be able to read this repo's actual round files. A gate that
    # only works on synthetic input is not guarding anything.
    rounds = rg.load_rounds()
    check(len(rounds) >= 3, f"expected the real round files, got {len(rounds)}")
    seven = [r for r in rounds if r.number == 7]
    check(len(seven) == 1, "round 7 should be present exactly once")
    if seven:
        check(seven[0].verdict is not None,
              "round 7 must declare a verdict now that the field exists")


for name, fn in sorted(globals().items()):
    if name.startswith("test_") and callable(fn):
        fn()

if failures:
    print(f"{failures} check(s) failed", file=sys.stderr)
    sys.exit(1)
print("all release gate checks passed")
