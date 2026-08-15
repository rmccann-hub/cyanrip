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
import re
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
    return rg.check(resolve(files))


def resolve(files):
    """The rounds as the gate resolves them, before check() judges them.

    Separate from gate() because "the gate refused" and "the gate picked the
    right lap" are different claims, and a test that only asserts refusal can
    be satisfied by an unrelated guard. One was: the ordering test below
    passed with the ordering rule reverted, because a second guard caught the
    same fixture for a different reason.
    """
    d = pathlib.Path(tempfile.mkdtemp())
    for name, body in files.items():
        (d / name).write_text(body, encoding="utf-8")
    return rg.load_rounds(d)


# A complete, closing round: both verdicts GO, both identities, and testing
# declared. Anything less must not close -- see the tests below, one per field.
# The v2 wire header, required from round 8 on. Every fixture below uses round
# 9, so it carries these; the round-7 exemption is tested separately.
WIRE = ("HANDSHAKE-FROM: cyanrip-fork\n"
        "HANDSHAKE-APP-VERSION: platterpus 0.6.4\n"
        "HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc1+platterpus.5 (platterpus-fork-gbbb2222)\n"
        "HANDSHAKE-PIN: bbb2222\n")

GO = ("HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: 1\n" + WIRE +
      "HANDSHAKE-VERDICT: GO\n"
      "HANDSHAKE-PEER-VERDICT: GO\n"
      "HANDSHAKE-PEER-VERSION: platterpus/0.6.4\n"
      "HANDSHAKE-PEER-PIN: abc1234\n"
      "HANDSHAKE-OUR-VERSION: 0.9.4-rc1+platterpus.4\n"
      "HANDSHAKE-OUR-PIN: def5678\n"
      "HANDSHAKE-TESTED: T1-T14 on both builds, rig session 2026-08-04\n"
      "\n# round 9\n")


def test_our_go_alone_does_not_close():
    """Covers: C1"""
    # The core of an affirmative handshake: our GO is a statement about our
    # tree, not agreement. Silence from the other side is not consent.
    body = "\n".join(l for l in GO.splitlines()
                     if not l.startswith("HANDSHAKE-PEER-VERDICT"))
    ok, probs = gate({"round-9.md": body})
    check(not ok, "our GO alone must not close a round")
    check(any("no peer verdict" in p for p in probs),
          f"should say the peer verdict is missing: {probs}")


def test_peer_hold_blocks_our_go():
    """Covers: C2"""
    ok, probs = gate({"round-9.md": GO.replace("HANDSHAKE-PEER-VERDICT: GO",
                                               "HANDSHAKE-PEER-VERDICT: HOLD")})
    check(not ok, "a peer HOLD must block even when we say GO")
    check(any("peer verdict HOLD" in p for p in probs), f"should name it: {probs}")


def test_close_requires_every_identity_and_testing_field():
    """Covers: C3, C4"""
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
    """Covers: C4"""
    # Stated separately from the loop because it is the rule the maintainer
    # asked for by name: no release without proper testing, ever.
    body = "\n".join(l for l in GO.splitlines()
                     if not l.startswith("HANDSHAKE-TESTED:"))
    ok, _ = gate({"round-9.md": body})
    check(not ok, "a round with no declared testing must never close")


def test_complete_two_sided_round_does_close():
    """Covers: C16"""
    # The gate must still be satisfiable, or it is not a gate, it is a wall.
    ok, probs = gate({"round-9.md": GO})
    check(ok, f"a complete two-sided tested round should close: {probs}")


def lap(n, round_no, verdict, complete=False):
    """A lap file. complete=True adds the peer/identity/testing fields a close
    requires, so a test can distinguish "this lap says GO" from "this lap is a
    valid close" -- they are different things now."""
    head = (f"HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: {round_no}\nHANDSHAKE-LAP: {n}\n"
            + WIRE + f"HANDSHAKE-VERDICT: {verdict}\n")
    if complete:
        head += ("HANDSHAKE-PEER-VERDICT: GO\n"
                 "HANDSHAKE-PEER-VERSION: platterpus/0.6.4\n"
                 "HANDSHAKE-PEER-PIN: abc1234\n"
                 "HANDSHAKE-OUR-VERSION: 0.9.4-rc1+platterpus.4\n"
                 "HANDSHAKE-OUR-PIN: def5678\n"
                 "HANDSHAKE-TESTED: T1-T14 both builds\n")
    return head + f"\n# round {round_no} lap {n}\n"


def test_latest_lap_decides_and_can_close():
    """Covers: C16"""
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
    """Covers: C13"""
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


def test_two_files_declaring_one_lap_are_ambiguous_not_a_close():
    """Round 7 lap 34, from the blind-exchange design.

    Two files declaring the SAME lap have no order between them. The resolver
    kept whichever `sorted()` yielded first -- i.e. by FILENAME -- which is the
    defect Platterpus found in their own gate in lap 17. We believed we did not
    share it because we compare declared numbers rather than stems. True, and
    useless when the declared numbers are equal.

    Measured before it was fixed: a lap 34 HOLD and a lap 34 GO in one
    directory reported the GO and ALLOWED a release, decided purely by name.
    """
    ok, probs = gate({"round-9.md": lap(1, 9, "OPEN"),
                      "round-9-lapA.md": lap(2, 9, "GO", complete=True),
                      "round-9-lapB.md": lap(2, 9, "HOLD")})
    check(not ok, f"two files declaring one lap must not close: {probs}")
    check(any("no order between them" in p for p in probs),
          f"the refusal must name the collision, not just say 'not closed': {probs}")


def test_a_lap_collision_blocks_even_when_both_halves_agree():
    """Guards the fix above against being narrowed to 'only when they differ'.

    Two concurrent GOs are still two documents with no order between them, and
    neither has seen the other. Ambiguity is not a close even when the two
    happen to agree -- otherwise the check passes exactly when it is not needed.
    """
    ok, _ = gate({"round-9.md": lap(1, 9, "OPEN"),
                  "round-9-lapA.md": lap(2, 9, "GO", complete=True),
                  "round-9-lapB.md": lap(2, 9, "GO", complete=True)})
    check(not ok, "two concurrent GO laps must still not close the round")


def test_a_collision_below_the_latest_lap_is_harmless():
    """The converse, or the fix would freeze the record permanently.

    Once a genuinely later lap exists -- the rejoin, written by someone who has
    seen both halves -- it supersedes the concurrent pair legitimately and the
    round can close again. Without this, one blind exchange would make a round
    unclosable forever.
    """
    ok, probs = gate({"round-9-lapA.md": lap(2, 9, "HOLD"),
                      "round-9-lapB.md": lap(2, 9, "HOLD"),
                      "round-9-lapC.md": lap(3, 9, "GO", complete=True)})
    check(ok, f"a later rejoin lap must supersede a concurrent pair: {probs}")


def test_a_first_go_is_expressible():
    """A GO whose peer has not GO'd yet must be *sayable*, not malformed.

    Platterpus's round 7 lap 23 §H reports a deadlock: their conformance
    checker refuses a file declaring GO while HANDSHAKE-PEER-VERDICT is HOLD,
    on the reading that "a GO that cannot close is worth saying at check time".
    Both sides need a closable GO; a GO is closable only once the peer has
    GO'd; so neither can go first and a round that reaches agreement can never
    record it.

    Ours does not have that hole, and this pins the difference rather than
    leaving it to be rediscovered. Two separate properties, and conflating them
    is what produced the deadlock:

      * the file is ACCEPTED -- it is a well-formed declaration;
      * the round does NOT close -- a close still needs both verdicts.

    Asserting only the second would pass against an implementation that
    rejected the file outright, which is exactly their failure.
    """
    files = {"round-09-lap-01.md":
             ("HANDSHAKE-PROTOCOL: 2\nHANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: 1\n"
              + WIRE
              + "HANDSHAKE-VERDICT: GO\n"
                "HANDSHAKE-PEER-VERDICT: HOLD\n"
                "HANDSHAKE-PEER-VERSION: platterpus/0.6.4b4\n"
                "HANDSHAKE-PEER-PIN: c7aa67c\n"
                "HANDSHAKE-OUR-VERSION: 0.9.4-rc1+platterpus.5\n"
                "HANDSHAKE-OUR-PIN: aaa1111\n"
                "HANDSHAKE-TESTED: rig session, 14/14 vs EAC\n\n# first GO\n")}

    rounds = resolve(files)
    check(len(rounds) == 1 and rounds[0].verdict == "GO",
          "a first GO must parse as a well-formed GO, not be refused")
    check(rounds[0].peer_verdict == "HOLD",
          "the peer's HOLD must be read verbatim, not normalised away")

    ok, probs = gate(files)
    check(not ok, "one GO must not close the round")
    check(any("peer verdict HOLD" in p for p in probs),
          f"the gate should name the peer's HOLD as the reason: {probs}")


def test_legacy_named_no_lap_file_cannot_shadow_a_canonical_lap():
    """The bug Platterpus's gate had, run against ours (round 7 lap 17 D).

    Their `_round_files` picked the newest file in a round by sorting stems.
    Adopting `round-NN-lap-LL.md` put canonically-named files BEFORE the
    legacy `round-N.md` lexically -- '0' < '7' at the seventh character -- so
    the oldest file in the round sorted last, was read as the newest, and its
    GO closed a round whose latest lap says HOLD. Their release gate reported
    `they-verified=yes (GO)` against our HOLD.

    We adopt the same filenames this lap, so the same collision exists here.
    It does not bite, for a reason worth pinning rather than assuming: a file
    with no HANDSHAKE-LAP is treated as lap 1, not as unknown, so it loses to
    every later lap on the declared number.
    """
    files = {
        # Legacy name, no lap field, and a GO complete enough to close.
        "round-9.md": ("HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\n" + WIRE
                       + "HANDSHAKE-VERDICT: GO\n"
                       "HANDSHAKE-PEER-VERDICT: GO\n"
                       "HANDSHAKE-PEER-VERSION: platterpus/0.6.4\n"
                       "HANDSHAKE-PEER-PIN: abc1234\n"
                       "HANDSHAKE-OUR-VERSION: 0.9.4-rc1+platterpus.4\n"
                       "HANDSHAKE-OUR-PIN: def5678\n"
                       "HANDSHAKE-TESTED: T1-T14 both builds\n\n# round 9\n"),
        # Canonical name, later lap, HOLD.
        "round-09-lap-16.md": lap(16, 9, "HOLD"),
    }

    # Floor: the test is only meaningful if the naive sort really does misorder
    # these two. If a future rename made them agree, this would pass by the bug
    # being unreachable rather than by the gate being right.
    names = sorted(files)
    check(names[-1] == "round-9.md",
          "floor: the legacy name must sort LAST for this to reproduce the bug; "
          f"got {names}")

    # Assert WHICH lap won, not merely that the gate refused. Refusal alone is
    # satisfied by an unrelated guard -- and was: with the no-lap-is-lap-1 rule
    # reverted, this fixture still failed to close, because an unknown lap is
    # separately treated as ambiguous. That is a second safety net, not this
    # rule, and a test that cannot tell them apart pins neither.
    rounds = resolve(files)
    check(len(rounds) == 1, f"expected one round, got {len(rounds)}")
    won = rounds[0]
    check(won.lap == 16 and won.path.name == "round-09-lap-16.md",
          "the later canonical lap must win the round; got "
          f"lap={won.lap} from {won.path.name}")

    ok, probs = gate(files)
    check(not ok,
          "a legacy-named no-lap GO must not shadow a later canonical HOLD -- "
          f"this is the filename-ordering bug: {probs}")


def test_ambiguous_lap_is_not_shadowed_by_a_good_one():
    body = ("HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: 1\nHANDSHAKE-LAP: 2\n"
            + WIRE + "HANDSHAKE-VERDICT: GO\n\n# round 9\n")
    ok, probs = gate({"round-9.md": body,
                      "round-9-lap2.md": lap(2, 9, "GO", complete=True)})
    check(not ok, "an ambiguous lap declaration must not be hidden behind a good one")
    check(any("ambiguous" in p for p in probs), "should name the ambiguity")


def test_go_closes():
    """Covers: C16"""
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
    """Covers: C11"""
    # An unrecognised verdict is not evidence of agreement.
    ok, _ = gate({"round-9.md": GO.replace("GO", "PROBABLY-FINE")})
    check(not ok, "an unrecognised verdict must not close a round")


def test_missing_verdict_fails_closed():
    """Covers: C5"""
    # The tempting shortcut is to treat a missing field as GO so old rounds
    # still pass. That puts the whole defect back through the fallback.
    body = "HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\n" + WIRE + "\n# round 9\n"
    ok, probs = gate({"round-9.md": body})
    check(not ok, "a round with no verdict field must fail closed")
    check(any("NO VERDICT" in p for p in probs),
          f"a missing verdict should say so explicitly: {probs}")


def test_prose_about_a_verdict_is_not_a_verdict():
    """Covers: C7"""
    # The exact failure Platterpus reported: a file that says it is NOT a GO,
    # closing the round because a matcher found the word GO in the prose.
    body = ("HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\n" + WIRE + "HANDSHAKE-VERDICT: HOLD\n\n"
            "# round 9\n\n"
            "This is deliberately **not a closing GO**. The verdict is HOLD.\n"
            "Do not read `HANDSHAKE-VERDICT: GO` from this sentence.\n"
            "GO\nGONE\nHANDSHAKE-VERDICT: GO but indented below\n"
            "  HANDSHAKE-VERDICT: GO\n")
    ok, _ = gate({"round-9.md": body})
    check(not ok, "prose mentioning GO must not close a HOLD round")


def test_indented_declaration_is_not_a_declaration():
    """Covers: C7"""
    body = "HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\n" + WIRE + "  HANDSHAKE-VERDICT: GO\n\n# round 9\n"
    ok, _ = gate({"round-9.md": body})
    check(not ok, "an indented verdict is quoted prose, not a declaration")


def test_two_verdicts_are_ambiguous_not_closed():
    """Covers: C6"""
    body = ("HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\n" + WIRE + "HANDSHAKE-VERDICT: GO\n"
            "HANDSHAKE-VERDICT: HOLD\n\n# round 9\n")
    ok, _ = gate({"round-9.md": body})
    check(not ok, "two verdicts must be ambiguous, not closed on the first")


def test_grandfathered_set_is_pinned():
    # Grandfathering is by number and must stay a deliberate, visible act. If
    # this set grows, someone changed the gate rather than closing a round.
    check(rg.GRANDFATHERED == {5, 6},
          f"grandfathered set changed: {rg.GRANDFATHERED}")


def test_grandfathering_does_not_leak_to_new_rounds():
    ok, _ = gate({"round-99.md": "HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 99\n"
                                 + WIRE + "\n# round 99\n"})
    check(not ok, "a new round must not inherit the grandfathered exemption")


def test_mismatched_round_number_is_a_problem():
    """Covers: C12"""
    body = "HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 8\n" + WIRE + "HANDSHAKE-VERDICT: GO\n\n# round 9\n"
    ok, probs = gate({"round-9.md": body})
    check(not ok, "a file declaring a different round number must not pass")
    check(any("declares" in p for p in probs), "should name the mismatch")


def test_one_open_round_blocks_even_when_others_closed():
    ok, _ = gate({"round-8.md": GO.replace("9", "8"),
                  "round-9.md": GO.replace("GO", "OPEN")})
    check(not ok, "one open round must block a release")


def test_empty_record_is_not_agreement():
    """Covers: C14"""
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
    """Covers: C15"""
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
    """Covers: C8"""
    # Found by running it: the lap that introduced the shared spec documented
    # the format with field lines inside ``` blocks, at column 0, and the gate
    # read them as declarations -- so a peer version the file was merely
    # *illustrating* was compiled into the binary as a fact. A declaration is a
    # statement the file makes, not one it quotes.
    body = ("HANDSHAKE-PROTOCOL: 1\nHANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: 1\n"
            + WIRE + "HANDSHAKE-VERDICT: HOLD\n\n"
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




def test_v2_wire_header_required_from_round_8():
    """Covers: C9, C16"""
    # The spec called four fields "required" while the gate enforced none of
    # them -- shipped in the very lap that introduced the spec. If Platterpus
    # implements the spec faithfully and we do not, the two gates disagree,
    # which is the failure the protocol exists to prevent.
    body = ("HANDSHAKE-PROTOCOL: 2\nHANDSHAKE-ROUND: 8\nHANDSHAKE-LAP: 1\n"
            "HANDSHAKE-VERDICT: GO\nHANDSHAKE-PEER-VERDICT: GO\n"
            "HANDSHAKE-PEER-VERSION: platterpus/0.6.4\nHANDSHAKE-PEER-PIN: aaa1111\n"
            "HANDSHAKE-OUR-VERSION: 0.9.4-rc1+platterpus.5\nHANDSHAKE-OUR-PIN: bbb2222\n"
            "HANDSHAKE-TESTED: T1-T18 on both builds\n\n# round 8\n")
    ok, probs = gate({"round-8.md": body})
    check(not ok, "a round-8 close without the v2 wire header must be refused")
    for f in ("HANDSHAKE-FROM", "HANDSHAKE-APP-VERSION",
              "HANDSHAKE-RIPPER-VERSION", "HANDSHAKE-PIN"):
        check(any(f in p for p in probs), f"refusal should name {f}: {probs}")

    # With them, the same round closes -- the gate must remain satisfiable.
    full = body.replace("HANDSHAKE-VERDICT: GO",
                        "HANDSHAKE-FROM: cyanrip-fork\n"
                        "HANDSHAKE-APP-VERSION: platterpus 0.6.4\n"
                        "HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc1+platterpus.5 (platterpus-fork-gbbb2222)\n"
                        "HANDSHAKE-PIN: bbb2222\n"
                        "HANDSHAKE-VERDICT: GO")
    ok2, probs2 = gate({"round-8.md": full})
    check(ok2, f"a complete round-8 file should close: {probs2}")


def test_wire_header_required_on_a_mid_round_lap_too():
    """Covers: C9"""
    # Required on EVERY file, not only a closing one: a lap reporting a
    # measurement must say which pair produced it.
    body = ("HANDSHAKE-PROTOCOL: 2\nHANDSHAKE-ROUND: 8\nHANDSHAKE-LAP: 2\n"
            "HANDSHAKE-VERDICT: HOLD\n\n# round 8 lap 2\n")
    ok, probs = gate({"round-8-lap2.md": body})
    check(not ok, "a HOLD lap without the wire header must be flagged")
    check(any("wire header" in p for p in probs),
          f"should name the wire header, not only the verdict: {probs}")


def test_round_7_is_exempt_from_the_wire_header():
    """Covers: C10"""
    # Neither project could comply with a spec written during round 7.
    body = ("HANDSHAKE-PROTOCOL: 2\nHANDSHAKE-ROUND: 7\nHANDSHAKE-LAP: 1\n"
            "HANDSHAKE-VERDICT: HOLD\n\n# round 7\n")
    _, probs = gate({"round-7.md": body})
    check(not any("wire header" in p for p in probs),
          f"round 7 must not be asked for the v2 header: {probs}")


def test_wire_header_exemption_boundary_is_pinned():
    check(rg.WIRE_HEADER_REQUIRED_FROM == 8,
          f"exemption boundary moved to {rg.WIRE_HEADER_REQUIRED_FROM} -- "
          "widening it is a protocol change, not a fix")




def test_every_conformance_row_has_a_test():
    """Covers: none -- this is the meta-check.

    The mapping between PROTOCOL.md's conformance table and this file must be
    derived from the table, not maintained beside it. A hand-kept list of "rows
    we cover" is the same defect as a hand-written contract: it looks
    authoritative and it rots the moment a row is added.

    Reading the table for IDs and the test docstrings for claims makes both
    directions checkable -- an uncovered row fails, and so does a test claiming
    a row that does not exist.
    """
    proto = (HERE.parent / "docs" / "handshake" / "PROTOCOL.md").read_text(encoding="utf-8")
    # Rows below the "added in v3" heading are not in force until this gate
    # implements 3. Scoped by HEADING, not by a hardcoded list: bumping
    # PROTOCOL_VERSION turns them on with no second edit, and a deferral that
    # needs a human to remember it is a deferral that rots.
    split = proto.find("### Rows added in v3")
    in_force = proto if split < 0 else proto[:split]
    deferred_text = "" if split < 0 else proto[split:]
    rows = set(re.findall(r"^\| (C\d+) \|", in_force, re.M))
    deferred = set(re.findall(r"^\| (C\d+) \|", deferred_text, re.M))
    check(len(rows) >= 16, f"expected the conformance table, found {len(rows)} rows")

    import importlib.util as _ilu
    _s = _ilu.spec_from_file_location("rg2", HERE.parent / "tools" / "release-gate.py")
    _rg = _ilu.module_from_spec(_s); _s.loader.exec_module(_rg)
    if _rg.PROTOCOL_VERSION >= 3:
        rows |= deferred
        deferred = set()
    if deferred:
        print(f"  (deferred to protocol 3, not yet in force: "
              f"{len(deferred)} row(s))")

    claimed = set()
    for name, fn in globals().items():
        if not (name.startswith("test_") and callable(fn) and fn.__doc__):
            continue
        m = re.search(r"Covers:\s*([^\n]+)", fn.__doc__)
        if not m:
            continue
        claimed.update(re.findall(r"C\d+", m.group(1)))

    uncovered = sorted(rows - claimed, key=lambda c: int(c[1:]))
    check(not uncovered,
          f"conformance rows with no test: {uncovered}")

    invented = sorted(claimed - rows, key=lambda c: int(c[1:]))
    check(not invented,
          f"tests claim conformance rows that do not exist: {invented}")




def test_a_test_pin_does_not_close_a_round():
    """Covers: C17

    The whole reason the field exists is to let the rig run a build the round
    has not agreed to. If declaring one closed the round, it would be a release
    by another name -- which is the rule it was invented to work around, not to
    defeat.
    """
    body = ("HANDSHAKE-PROTOCOL: 2\nHANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: 1\n" + WIRE +
            "HANDSHAKE-VERDICT: HOLD\n"
            "HANDSHAKE-TEST-PIN: ccc3333\n"
            "HANDSHAKE-PEER-VERDICT: GO\n"
            "HANDSHAKE-PEER-VERSION: platterpus/0.6.4\nHANDSHAKE-PEER-PIN: aaa1111\n"
            "HANDSHAKE-OUR-VERSION: 0.9.4-rc1+platterpus.5\nHANDSHAKE-OUR-PIN: bbb2222\n"
            "HANDSHAKE-TESTED: rig session\n\n# round 9\n")
    ok, _ = gate({"round-9.md": body})
    check(not ok, "a test pin must not close a round on its own")


def test_a_test_pin_is_not_the_production_pin():
    """Covers: C18

    They are different builds by definition -- the test pin is what the rig
    runs to produce the evidence, the production pin is what the round agrees
    to. Reading one as the other would install an unreviewed build everywhere.
    """
    body = GO.replace("HANDSHAKE-PIN: bbb2222",
                      "HANDSHAKE-PIN: bbb2222\nHANDSHAKE-TEST-PIN: ccc3333")
    ok, probs = gate({"round-9.md": body})
    check(ok, f"a complete close alongside a test pin should still close: {probs}")

    d = pathlib.Path(tempfile.mkdtemp())
    (d / "round-9.md").write_text(body, encoding="utf-8")
    lap_obj = rg.load_rounds(d)[0]
    check(lap_obj.pin == "bbb2222", f"production pin misread: {lap_obj.pin!r}")
    check(lap_obj.test_pin == "ccc3333", f"test pin misread: {lap_obj.test_pin!r}")




def _gate_main(files, argv):
    """Run the gate's main() against a throwaway record, capturing exit + out."""
    import contextlib, io, sys as _sys
    d = pathlib.Path(tempfile.mkdtemp())
    for name, body in files.items():
        (d / name).write_text(body, encoding="utf-8")
    saved_dir, saved_argv = rg.HANDSHAKE_DIR, _sys.argv
    rg.HANDSHAKE_DIR, _sys.argv = d, ["release-gate.py"] + argv
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            code = rg.main()
    finally:
        rg.HANDSHAKE_DIR, _sys.argv = saved_dir, saved_argv
    return code, buf.getvalue()


def test_stable_release_refused_with_a_round_open():
    """Covers: C19"""
    body = lap(1, 9, "HOLD")
    code, _ = _gate_main({"round-9.md": body}, ["--release-gate"])
    check(code != 0, "a stable release must be refused with a round open")


def test_prerelease_permitted_but_never_quietly():
    """Covers: C20

    A beta claims no joint verification, so refusing it would only guarantee
    the round can never close -- the evidence a close needs comes from running
    the thing. But it must never be quiet: the open rounds are printed first.
    """
    body = lap(1, 9, "HOLD")
    code, out = _gate_main({"round-9.md": body},
                           ["--release-gate", "--prerelease"])
    check(code == 0, "a pre-release must be permitted with a round open")
    check("round 9" in out,
          f"the open round must be printed before permitting: {out!r}")
    check("PRE-RELEASE permitted" in out,
          "permitting a pre-release must say so explicitly")
    check("STABLE release is still refused" in out,
          "must state that a stable release is still refused")


def test_prerelease_does_not_close_the_round():
    """Covers: C20

    Permitting a beta must not make the record read as closed -- otherwise the
    flag would be a release by another name, which is what it exists to avoid.
    """
    body = lap(1, 9, "HOLD")
    ok, _ = gate({"round-9.md": body})
    check(not ok, "the round must still be open after a pre-release is allowed")


def test_real_handshake_files_follow_the_naming_convention():
    """The convention agreed with Platterpus in round 7 lap 17 §C.

        round-NN-lap-LL.md   both zero-padded to two digits

    Checked against the real record rather than a fixture, because the point is
    that OUR files obey it -- a fixture would prove the checker works on files
    nobody sends.

    Their §C2 reasoning is why each clause is here: the filename becomes a
    second description of a fact the header already carries, and two
    descriptions drift unless something compares them. Zero-padding is so a
    lexical sort is chronological -- `lap-9` sorts after `lap-10` otherwise,
    and at seventeen laps that is not hypothetical.

    Files predating the lap header keep their old names, and the exemption is
    derived rather than listed: a file with no declared lap has nothing to name
    itself with. The converse is enforced too -- a canonical name on a file
    declaring no lap is a false label, which is worse than a legacy name
    because it looks checkable and is not.
    """
    canonical = re.compile(r"^round-(\d{2})-lap-(\d{2})\.md$")
    seen = {}
    for path in sorted(rg.HANDSHAKE_DIR.glob("round-*.md")):
        text = path.read_text(encoding="utf-8")
        rounds = rg.ROUND_RE.findall(text)
        laps = rg.LAP_RE.findall(text)
        m = canonical.match(path.name)

        if len(laps) == 1 and len(rounds) == 1:
            want = f"round-{int(rounds[0]):02d}-lap-{int(laps[0]):02d}.md"
            check(path.name == want,
                  f"{path.name} declares round {rounds[0]} lap {laps[0]}; "
                  f"the convention names it {want}")
            key = (int(rounds[0]), int(laps[0]))
            check(key not in seen,
                  f"{path.name} and {seen.get(key)} both claim round "
                  f"{key[0]} lap {key[1]}")
            seen[key] = path.name
        elif m:
            check(False, f"{path.name} wears a canonical name but declares "
                         "no single round/lap -- a false label is worse than "
                         "a legacy name, because it looks checkable")

        # Direction comes from the directory, never the name (their §C2).
        froms = re.findall(r"^HANDSHAKE-FROM:[ \t]*(\S+)", text, re.M)
        if froms:
            check(all(f == "cyanrip-fork" for f in froms),
                  f"{path.name} declares HANDSHAKE-FROM {froms}; this "
                  "directory holds our outbound files")

    # Floor: a checker that found no canonically-named files would pass every
    # assertion above by having nothing to check.
    check(len(seen) >= 2,
          f"floor: expected several lap-declaring files, found {len(seen)}")

    # And the padding must actually deliver a chronological lexical sort, which
    # is the property the padding is FOR. Asserting the rule without asserting
    # its purpose is how a convention survives while its reason quietly stops
    # holding.
    names = sorted(n for n in seen.values())
    by_lap = [n for _, n in sorted(seen.items())]
    check(names == by_lap,
          f"lexical order is not chronological: {names} vs {by_lap}")


# ---------------------------------------------------------------------------
# release-manifest.json -- the file a consumer polls to decide whether to
# offer an upgrade. Every check below blocks a way a USER gets hurt, not a way
# the format looks wrong.
# ---------------------------------------------------------------------------

def _manifest_mod():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "genman", HERE.parent / "tools" / "gen-release-manifest.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _ledger(rows):
    """A ledger file from (seq, channel, version, commit, round) tuples."""
    body = "# seq\tchannel\tversion\tcommit\tround\n"
    return body + "".join("\t".join(str(c) for c in r) + "\n" for r in rows)


def test_manifest_committed_copy_is_current():
    """A stale manifest is worse than none: a consumer polls it and is told the
    newest build is one that has been superseded."""
    m = _manifest_mod()
    want = m.render(m.build())
    have = (HERE.parent / "release-manifest.json").read_text(encoding="utf-8")
    check(want == have,
          "release-manifest.json is stale -- regenerate with "
          "tools/gen-release-manifest.py")


def test_manifest_stable_never_points_at_an_open_round():
    """A stable release claims joint verification. An open round means it does
    not have it, so the generator must refuse rather than publish."""
    m = _manifest_mod()
    import tempfile, pathlib as _p
    with tempfile.TemporaryDirectory() as d:
        f = _p.Path(d) / "l.tsv"
        f.write_text(_ledger([(1, "stable", "v1", "aaaaaaa", 999)]))
        orig = m.LEDGER
        try:
            m.LEDGER = f
            try:
                m.build()
                check(False, "stable on an unclosed round 999 was published")
            except m.LedgerError as e:
                check("NOT closed" in str(e),
                      f"refused, but not for the round reason: {e}")
        finally:
            m.LEDGER = orig


def test_manifest_beta_channel_never_offers_a_downgrade():
    """Opting into pre-releases must never move a user backwards. The first
    generated manifest had exactly this bug: beta resolved to beta.8 (seq 10)
    while stable was seq 11."""
    m = _manifest_mod()
    man = m.build()
    ch = man["channels"]
    if "beta" in ch and "stable" in ch:
        check(ch["beta"]["release_seq"] >= ch["stable"]["release_seq"],
              f"beta seq {ch['beta']['release_seq']} is behind stable "
              f"{ch['stable']['release_seq']} -- that is a downgrade")


def test_manifest_default_channel_is_stable():
    """A user who never opts in must be unable to reach a beta, even
    transiently, even if this file is generated wrong."""
    m = _manifest_mod()
    check(m.build()["default_channel"] == "stable",
          "default_channel must be stable")


def test_ledger_sequence_is_monotonic_and_unique():
    """The sequence is the ONLY orderable thing we publish -- our version
    string is not orderable at all. Reuse or a gap destroys it."""
    m = _manifest_mod()
    import tempfile, pathlib as _p
    cases = [
        ([(1, "stable", "v1", "aaaaaaa", 5), (1, "beta", "v2", "bbbbbbb", 5)],
         "reused", "reused"),
        ([(1, "stable", "v1", "aaaaaaa", 5), (3, "beta", "v2", "bbbbbbb", 5)],
         "gap", "does not follow"),
        ([(1, "stable", "v1", "aaaaaaa", 5), (2, "nightly", "v2", "bbbbbbb", 5)],
         "unknown channel", "not one of"),
    ]
    with tempfile.TemporaryDirectory() as d:
        f = _p.Path(d) / "l.tsv"
        orig = m.LEDGER
        try:
            m.LEDGER = f
            for rows, label, want in cases:
                f.write_text(_ledger(rows))
                try:
                    m.load_ledger(f)
                    check(False, f"ledger with a {label} seq was accepted")
                except m.LedgerError as e:
                    check(want in str(e),
                          f"{label}: refused for the wrong reason: {e}")
        finally:
            m.LEDGER = orig


def test_manifest_round_closed_agrees_with_the_gate():
    """Derived, never stated. A manifest claiming a round closed while the gate
    says otherwise is the two-gates-disagree failure in a new place -- so the
    manifest imports the gate's loader rather than reimplementing it."""
    m = _manifest_mod()
    man = m.build()
    truth = {r.number: bool(r.closed) for r in rg.load_rounds()}
    for name, ch in man["channels"].items():
        rnd = ch["handshake_round"]
        check(ch["round_closed"] == truth.get(rnd, False),
              f"{name}: round_closed={ch['round_closed']} but the gate says "
              f"{truth.get(rnd)} for round {rnd}")


for name, fn in sorted(globals().items()):
    if name.startswith("test_") and callable(fn):
        fn()

# A CLOSED ROUND IS NOT A RELEASED BUILD.
#
# HANDSHAKE_RELEASED renders "-- NOT a released build" in every logfile. It was
# derived from "is the record closed?" alone, which is a question about
# HANDSHAKE-OUR-PIN, while the claim it renders is about THIS BINARY. The moment
# round 8 closed on ddf7ac3 the tree was 33 commits past it, carrying ten
# unreviewed fixes and one breaking schema change -- and every log it wrote would
# have dropped the disclaimer and read as jointly verified.
def test_released_requires_the_build_to_be_the_pin():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ghs", HERE.parent / "tools" / "gen-handshake-state.py")
    ghs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ghs)

    check(not ghs._head_is(None), "a missing pin counted as released")
    check(not ghs._head_is(""), "an empty pin counted as released")
    check(not ghs._head_is("0000000"), "a pin that is not HEAD counted as released")

    # And the positive direction, so the guard cannot pass by always saying no.
    import subprocess
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE.parent,
                          capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=HERE.parent,
                           capture_output=True, text=True).stdout.strip()
    if head and not dirty:
        check(ghs._head_is(head[:7]),
              "HEAD's own abbreviated SHA was not recognised as the build")
    # A dirty tree is never a released build, whatever it is checked out at.
    if dirty:
        check(not ghs._head_is(head[:7]),
              "a dirty tree counted as a released build")


test_released_requires_the_build_to_be_the_pin()

if failures:
    print(f"{failures} check(s) failed", file=sys.stderr)
    sys.exit(1)
print("all release gate checks passed")

