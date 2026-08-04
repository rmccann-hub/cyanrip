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


# A complete, closing round: both verdicts GO, both identities, and testing
# declared. Anything less must not close -- see the tests below, one per field.
GO = ("HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: 1\nHANDSHAKE-VERDICT: GO\n"
      "HANDSHAKE-PEER-VERDICT: GO\n"
      "HANDSHAKE-PEER-VERSION: platterpus/0.6.4\n"
      "HANDSHAKE-PEER-PIN: abc1234\n"
      "HANDSHAKE-OUR-VERSION: 0.9.4-rc1+platterpus.4\n"
      "HANDSHAKE-OUR-PIN: def5678\n"
      "HANDSHAKE-TESTED: T1-T14 on both builds, rig session 2026-08-04\n"
      "\n# round 9\n")


def test_our_go_alone_does_not_close():
    # The core of an affirmative handshake: our GO is a statement about our
    # tree, not agreement. Silence from the other side is not consent.
    body = "\n".join(l for l in GO.splitlines()
                     if not l.startswith("HANDSHAKE-PEER-VERDICT"))
    ok, probs = gate({"round-9.md": body})
    check(not ok, "our GO alone must not close a round")
    check(any("no peer verdict" in p for p in probs),
          f"should say the peer verdict is missing: {probs}")


def test_peer_hold_blocks_our_go():
    ok, probs = gate({"round-9.md": GO.replace("HANDSHAKE-PEER-VERDICT: GO",
                                               "HANDSHAKE-PEER-VERDICT: HOLD")})
    check(not ok, "a peer HOLD must block even when we say GO")
    check(any("peer verdict HOLD" in p for p in probs), f"should name it: {probs}")


def test_close_requires_every_identity_and_testing_field():
    # One test per field, generated, so adding a required field cannot be
    # forgotten here -- and so the gate must name which one is absent.
    for field in ("HANDSHAKE-PEER-VERSION", "HANDSHAKE-PEER-PIN",
                  "HANDSHAKE-OUR-VERSION", "HANDSHAKE-OUR-PIN",
                  "HANDSHAKE-TESTED"):
        body = "\n".join(l for l in GO.splitlines()
                         if not l.startswith(field + ":"))
        ok, probs = gate({"round-9.md": body})
        check(not ok, f"a close without {field} must be refused")
        check(any(field in p for p in probs),
              f"the refusal should name {field}: {probs}")


def test_untested_round_cannot_close():
    # Stated separately from the loop because it is the rule the maintainer
    # asked for by name: no release without proper testing, ever.
    body = "\n".join(l for l in GO.splitlines()
                     if not l.startswith("HANDSHAKE-TESTED:"))
    ok, _ = gate({"round-9.md": body})
    check(not ok, "a round with no declared testing must never close")


def test_complete_two_sided_round_does_close():
    # The gate must still be satisfiable, or it is not a gate, it is a wall.
    ok, probs = gate({"round-9.md": GO})
    check(ok, f"a complete two-sided tested round should close: {probs}")


def lap(n, round_no, verdict, complete=False):
    """A lap file. complete=True adds the peer/identity/testing fields a close
    requires, so a test can distinguish "this lap says GO" from "this lap is a
    valid close" -- they are different things now."""
    head = (f"HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: {round_no}\nHANDSHAKE-LAP: {n}\n"
            f"HANDSHAKE-VERDICT: {verdict}\n")
    if complete:
        head += ("HANDSHAKE-PEER-VERDICT: GO\n"
                 "HANDSHAKE-PEER-VERSION: platterpus/0.6.4\n"
                 "HANDSHAKE-PEER-PIN: abc1234\n"
                 "HANDSHAKE-OUR-VERSION: 0.9.4-rc1+platterpus.4\n"
                 "HANDSHAKE-OUR-PIN: def5678\n"
                 "HANDSHAKE-TESTED: T1-T14 both builds\n")
    return head + f"\n# round {round_no} lap {n}\n"


def test_latest_lap_decides_and_can_close():
    # Lap 1 opened; lap 2 closes. The round must close WITHOUT going back and
    # editing lap 1 -- a file already sent must never be retroactively rewritten.
    ok, probs = gate({"round-9.md": lap(1, 9, "OPEN"),
                      "round-9-lap2.md": lap(2, 9, "GO", complete=True)})
    check(ok, f"a later complete GO lap must close the round: {probs}")


def test_a_later_go_lap_that_is_incomplete_does_not_close():
    # Guards against the fix above being read as "a later GO always wins".
    ok, _ = gate({"round-9.md": lap(1, 9, "OPEN"),
                  "round-9-lap2.md": lap(2, 9, "GO")})
    check(not ok, "a later GO lap missing the peer fields must not close")


def test_latest_lap_can_reopen():
    # The converse, and it must work or a round could never be reopened by new
    # evidence: lap 1 said GO, lap 2 found something.
    ok, _ = gate({"round-9.md": lap(1, 9, "GO", complete=True),
                  "round-9-lap2.md": lap(2, 9, "HOLD")})
    check(not ok, "a later lap declaring HOLD must reopen the round")


def test_lap_order_is_by_declaration_not_filename():
    # Constructed so filename order and declared order DISAGREE, or the test
    # cannot discriminate between the two implementations.
    #   by name:        round-9-lap2.md < round-9.md  ('-' sorts before '.')
    #                   -> last-by-name is round-9.md, verdict GO   -> allowed
    #   by declaration: lap 3 > lap 2
    #                   -> latest is round-9-lap2.md, verdict HOLD  -> blocked
    ok, _ = gate({"round-9.md": lap(2, 9, "GO", complete=True),
                  "round-9-lap2.md": lap(3, 9, "HOLD")})
    check(not ok, "latest lap must come from the declared number, not the name")


def test_ambiguous_lap_is_not_shadowed_by_a_good_one():
    body = ("HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: 1\nHANDSHAKE-LAP: 2\n"
            "HANDSHAKE-VERDICT: GO\n\n# round 9\n")
    ok, probs = gate({"round-9.md": body,
                      "round-9-lap2.md": lap(2, 9, "GO", complete=True)})
    check(not ok, "an ambiguous lap declaration must not be hidden behind a good one")
    check(any("ambiguous" in p for p in probs), "should name the ambiguity")


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
    body = "HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\n\n# round 9\n"
    ok, probs = gate({"round-9.md": body})
    check(not ok, "a round with no verdict field must fail closed")
    check(any("NO VERDICT" in p for p in probs),
          f"a missing verdict should say so explicitly: {probs}")


def test_prose_about_a_verdict_is_not_a_verdict():
    # The exact failure Platterpus reported: a file that says it is NOT a GO,
    # closing the round because a matcher found the word GO in the prose.
    body = ("HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\nHANDSHAKE-VERDICT: HOLD\n\n"
            "# round 9\n\n"
            "This is deliberately **not a closing GO**. The verdict is HOLD.\n"
            "Do not read `HANDSHAKE-VERDICT: GO` from this sentence.\n"
            "GO\nGONE\nHANDSHAKE-VERDICT: GO but indented below\n"
            "  HANDSHAKE-VERDICT: GO\n")
    ok, _ = gate({"round-9.md": body})
    check(not ok, "prose mentioning GO must not close a HOLD round")


def test_indented_declaration_is_not_a_declaration():
    body = "HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\n  HANDSHAKE-VERDICT: GO\n\n# round 9\n"
    ok, _ = gate({"round-9.md": body})
    check(not ok, "an indented verdict is quoted prose, not a declaration")


def test_two_verdicts_are_ambiguous_not_closed():
    body = ("HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\nHANDSHAKE-VERDICT: GO\n"
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
    body = "HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 8\nHANDSHAKE-VERDICT: GO\n\n# round 9\n"
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




def test_future_protocol_version_is_refused_not_guessed():
    # A gate reading a spec it does not implement must refuse. Guessing is how
    # the two sides drift into disagreeing about what a close means.
    ok, probs = gate({"round-9.md": GO.replace("HANDSHAKE-PROTOCOL: 1",
                                               "HANDSHAKE-PROTOCOL: 99")})
    check(not ok, "a future protocol version must be refused")
    check(any("refusing rather than guessing" in p for p in probs),
          f"should say why it refused: {probs}")


def test_missing_protocol_field_fails_closed():
    body = "\n".join(l for l in GO.splitlines()
                     if not l.startswith("HANDSHAKE-PROTOCOL:"))
    ok, _ = gate({"round-9.md": body})
    check(not ok, "a round with no protocol declaration must fail closed")


def test_fenced_examples_are_not_declarations():
    # Found by running it: the lap that introduced the shared spec documented
    # the format with field lines inside ``` blocks, at column 0, and the gate
    # read them as declarations -- so a peer version the file was merely
    # *illustrating* was compiled into the binary as a fact. A declaration is a
    # statement the file makes, not one it quotes.
    body = ("HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: 1\n"
            "HANDSHAKE-VERDICT: HOLD\n\n"
            "# round 9\n\n"
            "A close needs all of these:\n\n"
            "```\n"
            "HANDSHAKE-VERDICT: GO\n"
            "HANDSHAKE-PEER-VERDICT: GO\n"
            "HANDSHAKE-PEER-VERSION: platterpus/9.9.9\n"
            "HANDSHAKE-PEER-PIN: deadbee\n"
            "HANDSHAKE-OUR-VERSION: 1.2.3\n"
            "HANDSHAKE-OUR-PIN: cafe123\n"
            "HANDSHAKE-TESTED: everything\n"
            "```\n")
    ok, _ = gate({"round-9.md": body})
    check(not ok, "a file illustrating a close in a code block must not close")

    # And the illustrated values must not be picked up as this file's own.
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "round-9.md").write_text(body, encoding="utf-8")
    lap_obj = rg.load_rounds(d)[0]
    check(lap_obj.verdict == "HOLD",
          f"verdict should be the declared HOLD, got {lap_obj.verdict!r}")
    check(lap_obj.peer_version is None,
          f"peer version was quoted, not declared: {lap_obj.peer_version!r}")
    check(lap_obj.tested is None,
          f"tested was quoted, not declared: {lap_obj.tested!r}")


def test_protocol_version_is_pinned():
    # Bumping this is a protocol change and must be a deliberate, visible edit
    # shipped to both projects before the next close.
    check(rg.PROTOCOL_VERSION == 2,
          f"protocol version changed to {rg.PROTOCOL_VERSION} -- "
          "both repos must ship the new spec before the next close")


for name, fn in sorted(globals().items()):
    if name.startswith("test_") and callable(fn):
        fn()

if failures:
    print(f"{failures} check(s) failed", file=sys.stderr)
    sys.exit(1)
print("all release gate checks passed")
