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
import json
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
        "HANDSHAKE-PIN: bbb2222\n"
        # v4 §3a, required from round 9. Carried by every fixture rather than
        # only the v4 ones: they are ignored before round 9, so a fixture that
        # has them tests the rule it means to test instead of tripping over an
        # unrelated one.
        "HANDSHAKE-FROM-REPO: https://github.com/rmccann-hub/cyanrip\n"
        "HANDSHAKE-FROM-COMMIT: bbb2222\n"
        "HANDSHAKE-TO-REPO: https://github.com/rmccann-hub/Platterpus\n"
        "HANDSHAKE-TO-VERSION: platterpus 0.6.4\n"
        "HANDSHAKE-INBOUND-HELD: none\n")

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


def test_protocol_version_matches_the_shared_spec():
    """The gate implements exactly the version PROTOCOL.md declares.

    Was a hardcoded `== 2`, which made bumping the gate a two-place edit where
    one place could be forgotten -- and the forgettable one is the document
    both projects compare hashes of. Derived instead: the spec's own title is
    the single source, so a gate ahead of or behind the shared file fails here
    rather than at a close.

    Bumping is still a deliberate, visible act -- it now requires editing the
    shared spec, which is a version bump both projects ship.
    """
    title = (HERE.parent / "docs" / "handshake" / "PROTOCOL.md").read_text(
        encoding="utf-8").splitlines()[0]
    m = re.search(r"v(\d+)\s*$", title)
    check(m is not None, f"PROTOCOL.md's title declares no version: {title!r}")
    if m:
        check(rg.PROTOCOL_VERSION == int(m.group(1)),
              f"gate implements {rg.PROTOCOL_VERSION}, PROTOCOL.md declares "
              f"v{m.group(1)} -- both repos must ship the same version")




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


def test_a_declared_none_test_pin_is_not_rendered_as_a_build():
    """Found in round 14 lap 11, in this gate's own output.

    `HANDSHAKE-TEST-PIN: none.` printed as `test pin none. -- for the rig to
    gather evidence`, which names a build called "none." -- a label asserting
    what its value disclaims. Both sides declare the field this way and both
    are right to: "we considered a test pin and there is not one" is a
    different claim from a missing field.

    No conformance row: PROTOCOL.md §8 says nothing about what a gate prints,
    and adding a row is a shared-spec bump neither project may make alone.

    Three cases, because the whole point is that they are three: a real pin
    still renders as a pin, a declared absence renders as an absence, and a
    missing field renders as nothing at all."""
    def render(extra):
        d = pathlib.Path(tempfile.mkdtemp())
        (d / "round-9.md").write_text(
            GO.replace("HANDSHAKE-PIN: bbb2222",
                       "HANDSHAKE-PIN: bbb2222" + extra), encoding="utf-8")
        lap_obj = rg.load_rounds(d)[0]
        return lap_obj

    real = render("\nHANDSHAKE-TEST-PIN: ccc3333")
    check(not real.test_pin_is_declared_none(),
          "a real test pin must not be read as a declared absence")

    for spelling in ("none", "none.", "None", "NONE", "none..."):
        declared = render(f"\nHANDSHAKE-TEST-PIN: {spelling}")
        check(declared.test_pin == spelling,
              f"the raw declaration must survive parsing: {declared.test_pin!r}")
        check(declared.test_pin_is_declared_none(),
              f"{spelling!r} is an answer, not a build")

    absent = render("")
    check(absent.test_pin is None, "no field means no declaration")
    check(not absent.test_pin_is_declared_none(),
          "a missing field is not a declared absence -- that is the whole "
          "distinction this test exists for")

    # And the value nobody should guess at: an unrecognised string stays a pin.
    weird = render("\nHANDSHAKE-TEST-PIN: nonesuch1")
    check(not weird.test_pin_is_declared_none(),
          "only an exact `none` is an absence; anything else is a build")




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


def test_manifest_build_command_is_derived_per_commit():
    """schema 2. `install` hands over a source tarball and said nothing about
    how to build it, so the consumer built the default and `+platterpus.6`
    shipped with round 10's whole deliverable switched off.

    The trap is the fix, not the defect. `-Ddeclare_released=true` does not
    exist before +platterpus.6, and meson fails the entire configure on an
    unknown -D:

        meson.build:1:0: ERROR: Unknown options: "declare_released"

    So one global build string breaks the DOWNGRADE path -- the single thing
    retaining a previous stable exists to guarantee, and ddf7ac3 is the pin the
    consumer is running right now. The command has to be derived from each
    released commit's own tree.
    """
    m = _manifest_mod()

    # A commit that predates the option must NOT be told to pass it.
    old = m.build_command("ddf7ac3")
    check("declare_released" not in old,
          f"ddf7ac3 predates the option but its build command passes it: "
          f"{old!r} -- meson would fail the configure and the downgrade path "
          f"would be dead")
    check("meson setup" in old and "ninja" in old,
          f"the fallback build command is not a build command: {old!r}")

    # ...and a commit that has it must be. Without this the test passes on a
    # derivation that always returns the fallback.
    new = m.build_command("c4d1a00")
    check("-Ddeclare_released=true" in new,
          f"c4d1a00 declares the option but its build command omits it: {new!r}")

    # And the shipped manifest carries one per channel.
    man = m.build()
    for name, ch in man["channels"].items():
        check("build" in ch, f"{name}: manifest has no build command")
        check("meson setup" in ch["build"],
              f"{name}: build command is not a build: {ch['build']!r}")


def test_manifest_schema_is_declared_and_current():
    """A consumer pins a schema. Adding `build` without moving the number
    leaves them unable to tell a manifest that has it from one that does not,
    which is the whole reason the field exists."""
    m = _manifest_mod()
    man = m.build()
    check(man["schema"] == 2,
          f"manifest schema is {man['schema']!r}; `build` arrived at 2")
    committed = json.loads((HERE.parent / "release-manifest.json").read_text())
    check(committed["schema"] == man["schema"],
          f"committed manifest declares schema {committed['schema']!r} but the "
          f"generator emits {man['schema']!r}")


# The auto-runner lives at the END of the file, not the middle.
#
# It reads globals(), so every test defined BELOW it was silently never run --
# and the conformance meta-check, which also reads globals(), reported sixteen
# rows as uncovered while their tests sat forty lines further down. Two
# different symptoms, one cause: a sweep placed where the thing it sweeps is
# not all there yet. Same shape as the contract generator's scan landing
# partway through the banner block.

# A CLOSED ROUND IS NOT A RELEASED BUILD.
#
# HANDSHAKE_RELEASED renders "-- NOT a released build" in every logfile. It was
# derived from "is the record closed?" alone, which is a question about
# HANDSHAKE-OUR-PIN, while the claim it renders is about THIS BINARY. The moment
# round 8 closed on ddf7ac3 the tree was 33 commits past it, carrying ten
# unreviewed fixes and one breaking schema change -- and every log it wrote would
# have dropped the disclaimer and read as jointly verified.
# The comment above is kept because the defect it describes is real and the
# disclaimer still exists to prevent it. What is gone is the REMEDY it used to
# test: `_head_is(latest_lap.our_pin)`, requiring the build to be the approved
# pin.
#
# That remedy was correct about the defect and unsatisfiable as a fix. `our_pin`
# is read from a lap file inside the tree being built, so setting the flag
# needed that file to contain the abbreviated SHA of the commit containing it --
# the same fixpoint that stops a generated artifact naming the build that
# produced it. Round 10 lap 1 measured it across all 15 commits in the release
# ledger and the tip: 16 for 16, always 0. Platterpus then produced the other
# half from their rig artifacts: ddf7ac3, seq 11, DID render clean, because
# `_head_is` post-dates it -- so the disclaimer was invariant only from a083279
# onward, not from the beginning.
#
# `_head_is` is deleted rather than repaired. It also compared prefixes in
# whichever direction was shorter with no minimum length, so `_head_is('b')` was
# True for roughly one commit in sixteen (round 10 lap 1 §J3). Platterpus's lap
# 2 §F asked for that fixed BEFORE the flag became reachable, on the grounds
# that a latent permissive comparison behind a constant False goes live the
# moment the constant is fixed. They were right, and removing the function is
# the stronger answer than bounding it.
#
# The replacement is test_released_is_declared_and_defaults_to_off below, which
# pins every direction the claim can be withdrawn in.


# ---------------------------------------------------------------------------
# Round 10: the released claim is DECLARED, and every way it can be withdrawn.
#
# _head_is was correct about the defect and unsatisfiable as a remedy -- it
# required a lap file inside the tree to name the commit containing it, which
# lap 1 measured at 0 for 16 across the whole release ledger. §J1(b) replaced
# the derivation with a build-time declaration in the `Consumer:` idiom.
#
# A declaration is only as good as its fail-closed directions, so those are
# what this pins. Platterpus's one condition on accepting (b) was that a
# mis-set flag must produce a release that UNDER-claims, never a working tree
# that OVER-claims.
# ---------------------------------------------------------------------------
def _ghs():
    spec = importlib.util.spec_from_file_location(
        "ghs2", HERE.parent / "tools" / "gen-handshake-state.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_released_is_declared_and_defaults_to_off():
    """Covers: round 10 §J1(b), §B's fail-closed condition.

    Runs the generator as a subprocess against a REAL tree rather than poking
    module state, because the thing under test is the composition -- flag AND
    closed record AND not-visibly-dirty -- and a monkeypatched precondition
    proves nothing about how the three combine.
    """
    import subprocess, shutil

    root = HERE.parent

    def build_tree(with_git):
        """A copy of the WORKING tree's tools plus a fixed, closed record.

        Two things this deliberately does not do, each learned by doing it:

        `git archive HEAD` / `git clone` -- the first version used both, and
        both test the last commit rather than the code under test. They failed
        against this very fix while it was uncommitted, which is exactly
        backwards: a test that passes only after you commit cannot tell you
        whether to commit.

        Inheriting the repo's live docs/handshake -- the second version did,
        and round 10 being open made "declared release claims released"
        unprovable, because `ok` was False for reasons that had nothing to do
        with the flag. The record here is ONE closed round, fixed, so every
        answer below is attributable to the term the step moves.
        """
        work = pathlib.Path(tempfile.mkdtemp()) / "tree"
        (work / "docs" / "handshake").mkdir(parents=True)
        shutil.copytree(root / "tools", work / "tools")
        shutil.copy(root / "docs" / "handshake" / "round-08-lap-17.md",
                    work / "docs" / "handshake")
        if with_git:
            for cmd in (["git", "init", "-q"], ["git", "add", "-A"],
                        ["git", "-c", "user.email=t@t", "-c", "user.name=t",
                         "commit", "-qm", "fixture"]):
                subprocess.run(cmd, cwd=work, capture_output=True, check=True)
        return work

    def released_in(tree, *args):
        out = subprocess.run(
            [sys.executable, str(tree / "tools" / "gen-handshake-state.py"), *args],
            capture_output=True, text=True, check=True).stdout
        m = re.search(r"^#define HANDSHAKE_RELEASED\s+(\d)$", out, re.M)
        check(m is not None, "the generator emitted no HANDSHAKE_RELEASED")
        return m.group(1) if m else None

    # --- no git at all: the unpacked-tarball install path -------------------
    work = build_tree(with_git=False)
    hs = work / "docs" / "handshake"

    # 1. The default. Only the flag differs between this and step 2.
    check(released_in(work) == "0",
          "a build with no declaration claimed to be a released build")

    # 2. Declared, record closed, dirt unaskable -> the claim stands. Without
    #    this the rest is satisfiable by a generator that always says 0, which
    #    is precisely the shape _head_is failed in for sixteen builds while
    #    every test on it passed.
    check(released_in(work, "--declare-released") == "1",
          "a declared release could not claim to be one -- the flag is "
          "unreachable again, which is the defect round 10 exists to fix")

    # 3. An open round withdraws it. Same tree, same flag, no git: `ok` is the
    #    only term that moved.
    open_lap = hs / "round-99-lap-01.md"
    open_lap.write_text(
        "HANDSHAKE-PROTOCOL: 4\nHANDSHAKE-ROUND: 99\nHANDSHAKE-LAP: 1\n"
        "HANDSHAKE-FROM: cyanrip-fork\nHANDSHAKE-VERDICT: OPEN\n",
        encoding="utf-8")
    check(released_in(work, "--declare-released") == "0",
          "a build from a tree with an OPEN round declared itself released")
    open_lap.unlink()
    check(released_in(work, "--declare-released") == "1",
          "removing the open lap did not restore the claim -- then step 3 "
          "proved nothing about the round state")

    # --- a real repo: the visibly-dirty withdrawal --------------------------
    repo = build_tree(with_git=True)
    check(released_in(repo, "--declare-released") == "1",
          "a clean declared tree did not claim release -- the dirty step "
          "below would then prove nothing")
    (repo / "tools" / "scratch.txt").write_text("dirty\n", encoding="utf-8")
    check(released_in(repo, "--declare-released") == "0",
          "a visibly dirty tree declared itself a released build")
    (repo / "tools" / "scratch.txt").unlink()
    check(released_in(repo, "--declare-released") == "1",
          "removing the dirt did not restore the claim -- then the dirty "
          "check was not what moved it")

    shutil.rmtree(work.parent, ignore_errors=True)
    shutil.rmtree(repo.parent, ignore_errors=True)


def test_the_tarball_install_path_can_still_declare():
    """Covers: round 10 §J1(b), the trap inside the fix.

    Platterpus installs from `.../archive/<sha>.tar.gz` -- the only path the
    manifest offers. An unpacked tarball has no .git, so a released check that
    DEMANDS a clean git tree refuses the exact artifact users install, and the
    flag is unreachable again through the distribution channel rather than
    through the condition.

    That is not hypothetical: the check this replaced returned False on any
    tree where git could not answer, and called it failing safe. It was failing
    safe into unreachable.
    """
    import json
    manifest = json.loads((HERE.parent / "release-manifest.json").read_text())
    installs = [c["install"] for c in manifest["channels"].values()]
    check(all(".tar.gz" in u for u in installs),
          f"the manifest no longer installs from tarballs: {installs} -- "
          f"if the install path changed, this test's premise needs rechecking")

    ghs = _ghs()
    # The behaviour that makes it work, asserted directly: unknown dirt is not
    # dirt. `_known_dirty` answers about ROOT, which is a git tree here, so the
    # tarball case is asserted by the subprocess test above; this pins the
    # three-state intent against a future two-state rewrite.
    check(ghs._known_dirty() in (True, False),
          "_known_dirty must answer a bool, never raise, on any tree")



# ---------------------------------------------------------------------------
# v4 conformance, C21-C36. One test per row in PROTOCOL.md §8's v3/v4 table.
#
# Written when the gate moved to 4. The rows were deferred behind a heading so
# that bumping PROTOCOL_VERSION turned them on with no second edit -- and it
# did, which is the only reason this block exists rather than being forgotten.
# ---------------------------------------------------------------------------

import importlib.util as _ilu
_ds = _ilu.spec_from_file_location("rdg", HERE.parent / "tools" / "round-digest.py")
rdg = _ilu.module_from_spec(_ds); _ds.loader.exec_module(rdg)


def test_digest_mismatch_and_reconcile():
    """Covers: C21, C22

    Two sides holding different records must not close. There is nothing to
    assert about equality here that is not tautological, so this asserts the
    thing that can actually go wrong: that the construction is sensitive to
    the record at all. A digest that ignored a lap would compare equal forever
    and refuse nothing.
    """
    a = rdg.digest_of_lines(["1\tcyanrip-fork\t" + "a" * 64])
    b = rdg.digest_of_lines(["1\tcyanrip-fork\t" + "b" * 64])
    check(a != b, "the digest is insensitive to a lap's content")
    c = rdg.digest_of_lines(["1\tcyanrip-fork\t" + "a" * 64,
                             "2\tplatterpus\t" + "a" * 64])
    check(a != c, "the digest is insensitive to a lap being present or absent")
    check(rdg.digest_of_lines([]) != a, "an empty record digests like a full one")


def test_inbound_held_is_required_and_none_is_legal():
    """Covers: C23, C24

    Both directions. `none` must be ACCEPTED -- it is a claim, and the whole
    point of the field is that "we hold none of yours" and "we forgot to say"
    are different. A gate that treated `none` as absent would punish the honest
    answer.
    """
    missing = GO.replace("HANDSHAKE-INBOUND-HELD: none\n", "")
    ok, probs = gate({"round-9.md": missing})
    check(not ok, "a round-9 lap with no HANDSHAKE-INBOUND-HELD closed")
    check(any("INBOUND-HELD" in p for p in probs),
          f"refused, but not for the missing field: {probs}")

    ok, probs = gate({"round-9.md": GO})
    check(ok, f"`none` should be a legal value, not a missing one: {probs}")


def test_addressing_fields_required_from_round_nine():
    """Covers: C25

    And NOT before: round 8's record must keep closing. A requirement that
    reached backwards would reopen a round both projects have closed.
    """
    for field in ("HANDSHAKE-FROM-REPO", "HANDSHAKE-FROM-COMMIT",
                  "HANDSHAKE-TO-REPO", "HANDSHAKE-TO-VERSION"):
        body = "\n".join(l for l in GO.splitlines() if not l.startswith(field))
        ok, probs = gate({"round-9.md": body + "\n"})
        check(not ok, f"a round-9 lap without {field} closed")
        check(any(field in p for p in probs),
              f"refused without naming {field}: {probs}")

    r8 = GO.replace("HANDSHAKE-ROUND: 9", "HANDSHAKE-ROUND: 8")
    r8 = "\n".join(l for l in r8.splitlines()
                    if not l.startswith("HANDSHAKE-FROM-REPO"))
    ok, probs = gate({"round-8.md": r8 + "\n"})
    check(ok, f"round 8 must not be held to a v4 field: {probs}")


def test_a_file_not_addressed_to_us_is_not_acted_on():
    """Covers: C26

    Asserted at the level a gate can actually enforce: the field is parsed and
    carried, so a caller can compare it. A gate cannot know its own repository
    URL without being told, and inventing that would be a guess.
    """
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "round-9.md").write_text(GO, encoding="utf-8")
    lp = rg.load_rounds(d)[0]
    check(lp.to_repo == "https://github.com/rmccann-hub/Platterpus",
          f"TO-REPO not carried: {lp.to_repo!r}")


def test_withdrawn_is_terminal_but_never_permits_a_release():
    """Covers: C27, C28

    The reason WITHDRAWN did not exist before v4: a terminal state with no
    guard is a way to get past "no release while a round is open" by ending the
    round instead of closing it.
    """
    w = GO.replace("HANDSHAKE-VERDICT: GO", "HANDSHAKE-VERDICT: WITHDRAWN")
    w = w.replace("HANDSHAKE-PEER-VERDICT: GO\n", "")
    ok, probs = gate({"round-9.md": w})
    check(not ok, "a WITHDRAWN round permitted a release")
    check(any("WITHDRAWN" in p and "no\nrelease" not in p for p in probs),
          f"refused, but not as a withdrawal: {probs}")

    no_reason = w
    ok, probs = gate({"round-9.md": no_reason})
    check(not ok, "WITHDRAWN with no reason was accepted")

    with_reason = w.replace("HANDSHAKE-VERDICT: WITHDRAWN",
                            "HANDSHAKE-VERDICT: WITHDRAWN\n"
                            "HANDSHAKE-WITHDRAWN-REASON: the rig disc was destroyed")
    ok, probs = gate({"round-9.md": with_reason})
    check(not ok, "a withdrawn round still must not permit a release")
    check(any("destroyed" in p for p in probs),
          f"the reason must be reported, not swallowed: {probs}")


def test_protocol_must_not_go_backwards():
    """Covers: C29

    Under-declaring is silently valid to a version check -- a gate accepts
    anything at or below what it implements -- so it asks the peer to grade the
    file by rules the sender is not following. Ours did it for eight laps.
    """
    files = {"round-9-lap1.md": lap(1, 9, "HOLD").replace("HANDSHAKE-PROTOCOL: 1",
                                                          "HANDSHAKE-PROTOCOL: 4"),
             "round-9-lap2.md": lap(2, 9, "HOLD")}
    laps = rg.load_rounds_all(pathlib.Path(_write(files))) if hasattr(rg, "load_rounds_all") else None
    d = pathlib.Path(_write(files))
    every = rg.load_rounds(d, every_lap=True)
    by_lap = {l.lap: l for l in every}
    check(int(by_lap[1].protocol) == 4 and int(by_lap[2].protocol) == 1,
          "the fixture did not produce a backwards step")
    # The rule is enforced in tests/handshake_wire.py against the real record;
    # here we assert the data a gate needs to see it is actually carried.


def _write(files):
    d = pathlib.Path(tempfile.mkdtemp())
    for name, body in files.items():
        (d / name).write_text(body, encoding="utf-8")
    return d


def test_lap_ceiling_and_its_override():
    """Covers: C30

    And that it is NOT retroactive: round 7 ran to lap 39 and is closed. A
    ceiling reaching backwards would reopen the round that motivated it, which
    is the one outcome that teaches nothing.
    """
    over = GO.replace("HANDSHAKE-LAP: 1", "HANDSHAKE-LAP: 22")
    ok, probs = gate({"round-9.md": over})
    check(not ok, "lap 22 closed a round with no override")

    allowed = over.replace("HANDSHAKE-VERDICT: GO",
                           "HANDSHAKE-OVERRIDE: R7 — lap ceiling\n"
                           "HANDSHAKE-OVERRIDE-BY: operator (test), 2026-08-16\n"
                           "HANDSHAKE-OVERRIDE-WHY: the record is long because the "
                           "channel was broken, not because the round grew\n"
                           "HANDSHAKE-VERDICT: GO")
    ok, probs = gate({"round-9.md": allowed})
    check(ok, f"a fully recorded override should be honoured: {probs}")

    old = GO.replace("HANDSHAKE-ROUND: 9", "HANDSHAKE-ROUND: 7").replace(
        "HANDSHAKE-LAP: 1", "HANDSHAKE-LAP: 39")
    ok, probs = gate({"round-7.md": old})
    check(ok, f"the ceiling must not reach back to round 7: {probs}")


def test_override_must_be_fully_recorded_and_is_printed():
    """Covers: C31, C32

    An override without a weighable reason is not recorded, and an unrecorded
    override did not happen. And one that becomes invisible after the session
    that made it is indistinguishable from the rule never existing -- so it is
    reported every time the state is, not once.
    """
    part = GO.replace("HANDSHAKE-VERDICT: GO",
                      "HANDSHAKE-OVERRIDE: R4 — pin moved\nHANDSHAKE-VERDICT: GO")
    ok, probs = gate({"round-9.md": part})
    check(not ok, "an override with no -BY and no -WHY was honoured")

    full = GO.replace("HANDSHAKE-VERDICT: GO",
                      "HANDSHAKE-OVERRIDE: R4 — pin moved\n"
                      "HANDSHAKE-OVERRIDE-BY: operator (test), 2026-08-16\n"
                      "HANDSHAKE-OVERRIDE-WHY: the rig session cannot be rescheduled\n"
                      "HANDSHAKE-VERDICT: GO")
    ok, probs = gate({"round-9.md": full})
    check(ok, f"a fully recorded override should be honoured: {probs}")

    # Printed where the state is printed -- not returned as a refusal, which
    # would make honouring it indistinguishable from rejecting it.
    _, out = _gate_main({"round-9.md": full}, [])
    check("OVERRIDE" in out and "rescheduled" in out,
          f"an honoured override was not printed with its reason:\n{out}")


def test_the_digest_rule_cannot_be_overridden():
    """Covers: C33

    The one rule no reason waives. Two parties exchanging GO over divergent
    records are agreeing about different things, and no justification makes
    that mean something.
    """
    bad = GO.replace("HANDSHAKE-VERDICT: GO",
                     "HANDSHAKE-OVERRIDE: §5a — digest mismatch, ship anyway\n"
                     "HANDSHAKE-OVERRIDE-BY: operator (test), 2026-08-16\n"
                     "HANDSHAKE-OVERRIDE-WHY: we are confident the records agree\n"
                     "HANDSHAKE-VERDICT: GO")
    ok, probs = gate({"round-9.md": bad})
    check(not ok, "the digest rule was overridden")
    check(any("not overridable" in p for p in probs),
          f"refused, but not as an unoverridable rule: {probs}")


def test_a_container_is_not_a_lap():
    """Covers: C34

    Platterpus's envelope carried three laps' wire headers in its body and
    their enumerator counted it as a fourth lap. Derived from §2 rule 3 rather
    than from a list of container formats, so it excludes the next one too.
    """
    one = ("HANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: 3\nHANDSHAKE-FROM: cyanrip-fork\n")
    check(rdg.is_a_lap(one) == ("9", "3", "cyanrip-fork"),
          "a plain lap was not recognised")
    check(rdg.is_a_lap(one + one) is None,
          "a file declaring the fields twice was counted as a lap")
    fenced = "```\n" + one + "```\n" + one
    check(rdg.is_a_lap(fenced) == ("9", "3", "cyanrip-fork"),
          "a quoted example inside a fence was counted as a declaration")
    check(rdg.is_a_lap("HANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: 3\n") is None,
          "a file with no HANDSHAKE-FROM was counted as a lap")


def test_an_envelope_carrying_one_lap_can_be_built():
    """Covers: round 11 lap 2 §J3 -- the exchange the transport rule requires
    and the tool refused to produce.

    Two rules were in direct conflict. "One file per exchange, the lap travels
    inside the envelope with everything it references" is the transport
    convention. §5a says a file is a lap when ROUND, LAP and FROM each appear
    exactly once. An envelope carrying ONE lap declares each exactly once, so
    make-envelope.py refused to emit it -- and one lap plus its artifacts is by
    far the commonest exchange there is. Round 10 lap 5 travelled bare because
    of this, and round 11 lap 3 has to carry PROVIDER-CONTRACT.md.

    Fixed inside the spec rather than by relaxing it: the envelope re-declares
    the triple its operative lap declares, so the count is two and §5a excludes
    it by construction. No protocol change, no version bump, and the envelope's
    own prose -- which already claimed it "declares the wire headers of every
    lap it carries" -- becomes true for the single-lap case instead of being
    quietly false.
    """
    import subprocess

    root = HERE.parent
    d = pathlib.Path(tempfile.mkdtemp())
    lap = d / "round-42-lap-07.md"
    lap.write_text(
        "HANDSHAKE-PROTOCOL: 4\nHANDSHAKE-ROUND: 42\nHANDSHAKE-LAP: 7\n"
        "HANDSHAKE-FROM: cyanrip-fork\nHANDSHAKE-VERDICT: GO\n\nbody\n",
        encoding="utf-8")
    art = d / "artifact.md"
    art.write_text("some artifact the lap references\n", encoding="utf-8")

    def run(*args):
        return subprocess.run(
            [sys.executable, str(root / "tools" / "make-envelope.py"), *args],
            capture_output=True, text=True)

    # 1. One lap plus one artifact. This is the case that used to be refused.
    r = run(str(d / "out.md"), "--lap", str(lap), str(art))
    check(r.returncode == 0,
          f"an envelope carrying one lap was refused: {r.stderr.strip()!r}")
    env = d / "round-42-lap-07-envelope.md"
    check(env.exists(), f"envelope not written where expected: {list(d.iterdir())}")

    # 2. It must still not READ as a lap, which is the property the refusal was
    #    protecting. Asserted with the real enumerator, not by eye.
    if env.exists():
        check(rdg.is_a_lap(env.read_text(encoding="utf-8")) is None,
              "the envelope parses as a lap -- §5a's exactly-once test now "
              "counts it, which is the defect the guard existed to prevent")

        # 3. And the parts must come back byte-identical, or the fix traded one
        #    failure for a worse one.
        import hashlib, re as _re
        PART = _re.compile(
            r"^<{10} BEGIN (?P<name>\S+) sha256=(?P<sha>[0-9a-f]{64}) >{10}$\n"
            r"(?P<body>.*?)\n^<{10} END (?P=name) >{10}$",
            _re.MULTILINE | _re.DOTALL)
        got = {}
        for m in PART.finditer(env.read_text(encoding="utf-8")):
            data = (m["body"] + "\n").encode("utf-8")
            check(hashlib.sha256(data).hexdigest() == m["sha"],
                  f"{m['name']}: declared sha256 does not match its own body")
            got[m["name"]] = data
        check(got.get(lap.name) == lap.read_bytes(),
              "the lap did not survive the envelope byte-identically")
        check(got.get(art.name) == art.read_bytes(),
              "the artifact did not survive the envelope byte-identically")

    # 4. The artifacts-only envelope must NOT regress. With no lap the parts
    #    declare nothing, so adding envelope-level declarations would make each
    #    field appear exactly once -- refusing the very case that worked before.
    art2 = d / "artifact2.md"
    art2.write_text("second artifact\n", encoding="utf-8")
    r2 = run(str(d / "plain.md"), str(art), str(art2))
    check(r2.returncode == 0,
          f"an envelope with no lap was refused: {r2.stderr.strip()!r}")


def test_the_digest_excludes_the_lap_that_carries_it():
    """Covers: C35, C36

    Both halves, and the second is the one that is easy to get backwards: the
    writer excludes ITSELF, the reader excludes THE FILE IT JUST RECEIVED.
    Excluding your own newest lap makes the two sides disagree forever.
    """
    lines = ["1\tcyanrip-fork\t" + "a" * 64, "2\tplatterpus\t" + "b" * 64]
    whole = rdg.digest_of_lines(lines)
    without_1 = rdg.digest_of_lines(lines[1:])
    without_2 = rdg.digest_of_lines(lines[:1])
    check(len({whole, without_1, without_2}) == 3,
          "excluding a lap did not change the digest, so exclusion is a no-op")
    # The asymmetry, stated as the property it guarantees: a writer's declared
    # value is reproducible by a reader that excludes the SAME lap, and not by
    # one that excludes its own.
    check(rdg.digest_of_lines(lines[:1]) == without_2,
          "excluding the same lap did not reproduce the writer's value")


# The lap from which a declared HANDSHAKE-ROUND-DIGEST must re-derive.
#
# Round 9 laps 5 and 7 do not, and cannot be made to: they are SENT, and a sent
# lap is immutable -- the one rule this session already broke once and rebuilt
# tests/sent_laps.py to stop. Both carry the same defect, conceded in lap 7 §D
# and re-declared in lap 9: a VERIFIER's computation under the WRITER's field.
# Round 8 and earlier predate the field entirely.
#
# Scoped forward rather than retroactively, for the reason the v4 lap ceiling
# had to be: a requirement that reaches backwards reopens a round both projects
# have closed. Widening this constant is a visible act.
WRITER_DIGEST_CHECKED_FROM = (9, 9)

# The two known-failing laps, pinned by the value each declares. Naming them by
# their WRONG value rather than by filename is deliberate: if either file is
# ever edited, the declaration moves, this stops matching, and the test fails
# rather than silently excusing a file that has changed under it.
KNOWN_UNREPRODUCIBLE = {
    "round-09-lap-05.md": "ed2cf5c3c4443733",
    "round-09-lap-07.md": "53f0b465833ac845",
    # Round 13 lap 7, theirs. Declares `039cfa03a335266e over 6`; we re-derive
    # `051bfc6d98ed1eb9` over the SAME COUNT. Same six laps, different bytes for
    # at least one of them -- which is exactly what this field exists to detect,
    # and the first time it has detected it rather than catching a typed value.
    #
    # CAUSE NOW DETERMINED, round 14 lap 2 §E2, and VERIFIED HERE rather than
    # accepted: their six rows, transcribed from their lap and re-hashed by
    # this side, reproduce 039cfa03a335266e exactly, while ours reproduce
    # 051bfc6d98ed1eb9. Exactly ONE row of six differs:
    #
    #     ours   1  platterpus  f4bece7f...   <- as they sent it
    #     theirs 3  platterpus  4c5dd696...   <- after renumbering it
    #
    # Same file at two moments. It is their verification of our lap 1, sent
    # declaring LAP 1, then renamed and its header renumbered to lap 3 on their
    # disk. Renumbering edits the header, so the file's sha moves with the lap
    # field. `docs/handshake/inbound/round-13-lap-01-verification.md` in this
    # tree hashes to f4bece7f..., which is the row they say they held before the
    # rename -- so the half of their account that touches OUR artifact is
    # confirmed against it. The half in their git history is read from their lap
    # and is not independently checkable here.
    #
    # SO NEITHER IMPLEMENTATION IS WRONG. The digest is over the RECORD, the two
    # records genuinely differ by one file's bytes, and the field reported that
    # on its first real use. That is the mechanism working, not failing.
    #
    # Our first hypothesis below was right about the MECHANISM and its test was
    # necessarily incomplete: we varied the lap number with the sha held fixed,
    # because we do not hold their renumbered file and cannot know its hash. A
    # hypothesis that cannot be fully tested from one side is not a refuted one,
    # and recording it as "REJECTED" flattened that. Kept, corrected, because
    # the three rejections are still the useful part of this entry:
    #
    #   * renumbered LAP 1 -> LAP 3, sha held fixed -> 468ad5d6fd563dcf. Right
    #     mechanism, wrong because the sha moves too. NOT refuted; untestable.
    #   * they hold the pre-edit lap 6 (ARTIFACT-BUILD g2865436) while we hold
    #     the corrected one (ge9b9d4c) -> re-derives c311b5e06ff3c975. Refuted.
    #   * a different population -> ruled out by the count, which agrees at 6.
    #
    # RETAINED, not retired, and they invited us to retire it. The entry's job
    # is to stop a declared digest we cannot re-derive from silently passing;
    # that is still true of this file, because we still cannot re-derive it from
    # laps we hold -- only from rows they typed. Deleting it would make the gate
    # green for a reason no reader could reconstruct.
    #
    # Allowlisted rather than left red because the disagreement is about the
    # RECORD and not about the verdicts: both sides' GO is declared in a file
    # the other holds and quotes by line. Named individually and pinned by the
    # wrong value, like the two above, so that if their file is ever edited this
    # stops matching and the test fails rather than excusing a moved target.
    "round-13-lap-07.md": "039cfa03a335266e",
    # Round 14 lap 6, theirs. Declares `801c634a4ff9113e over 5`; we re-derive
    # six over the same retroactive population.
    #
    # CAUSE KNOWN AT THE MOMENT OF FILING, which is the difference from the
    # entry above: **they do not hold our round-14 lap 2.** Their lap 6's
    # HANDSHAKE-INBOUND-HELD lists "your laps 3 and 4"; lap 2 is absent. It is
    # the lap that moved the pin to f2c0506, superseded by our lap 4, and it
    # evidently never reached them.
    #
    # So the extra lap in our count is `round-14-lap-02.md` (ours, outbound),
    # which sits beside `inbound/round-14-lap-02.md` (theirs) -- round 14
    # carries TWO lap 2s and TWO lap 5s, both sides having numbered from their
    # own directory listing. That is the collision `HANDSHAKE-NEXT-LAP` is
    # being added to the protocol to remove, and their lap 6 §Z9 names the
    # shape: the number is chosen when a lap is WRITTEN and the divergence
    # appears when it is not immediately sent.
    #
    # Both declarations are therefore correct about their own record and the
    # records genuinely differ, exactly as in round 13. Allowlisted rather than
    # left red because the disagreement is about which files each side holds,
    # not about any verdict; our lap 7 reports it and ships lap 2 with it.
    # Pinned by their declared value so an edit to their file fails here.
    "round-14-lap-06.md": "801c634a4ff9113e",
    # Round 14 lap 8, theirs. Declares `adf7122c1c236276 over 7`; we re-derive
    # eight. SAME CAUSE as the entry above and they PRE-DECLARED IT: their own
    # field reads "every round-14 lap either side holds *that we hold*,
    # excluding this one. Your §F is right that the true population is 8; the
    # eighth is your lap 2".
    #
    # So this is not a divergence either side has to discover -- it is an
    # agreed, named difference in holdings, declared in the same field that
    # carries the number. That is the field working as well as it can: the
    # value disagrees, the prose says exactly why, and neither side had to
    # spend a round finding out. Our lap 9 ships lap 2 as its own file, which
    # is what closes it.
    #
    # Kept rather than suppressed until they confirm receipt: an allowlist
    # entry that outlives its cause is how a gate stops gating, so this comes
    # out when a later lap of theirs enumerates eight.
    "round-14-lap-08.md": "adf7122c1c236276",
    # Round 14 lap 13, theirs. Declares `84744e825d0b3d42 over 12`; we re-derive
    # `fceaf38eff740b03 over 13`.
    #
    # CAUSE DETERMINED HERE, and it is a DIFFERENT one from the three above:
    # not a difference in holdings. Their own field says so -- "unchanged from
    # our lap 12, which this file does not count and which named the same
    # population". They deliberately RE-DECLARED lap 12's value because nothing
    # new had arrived.
    #
    # But something had: their own lap 12. A lap's digest covers the round's
    # laps excluding the lap in flight, and by lap 13 their lap 12 is a held lap
    # of the round. Re-declaring lap 12's number omits it.
    #
    # DERIVED, not argued. Over the 13 laps they held when writing it --
    # everything in round 14 numbered below 13 -- the digest is
    # `fceaf38eff740b03`, which is exactly what OUR lap 13 declares, written
    # independently and covering the same population. So the two loaders agree
    # and the declaration is the slip: this is a third consecutive agreement
    # once the value is corrected, not a fourth divergence.
    #
    # WHY THE NAME COLLISION HERE DOES NOT SUPPRESS OUR OWN LAP 13. Round 14
    # has two files called `round-14-lap-13.md` -- ours and theirs -- and the
    # pin is keyed on the basename, so it matches both. It does not excuse ours
    # because an entry only applies when the DECLARED VALUE also matches, and
    # ours declares `fceaf38eff740b03`. Value-pinning was added so an edit to
    # their file would fail here; it now carries a second load it was not
    # designed for, so there is a test asserting our lap 13 is still judged.
    #
    # Comes out when a later lap of theirs declares over its full holdings.
    "round-14-lap-13.md": "84744e825d0b3d42",
    # Round 14 lap 16, theirs. Declares `7b5737acf715a7f5 over 15`; we re-derive
    # `6ebd98bf1a8e04d4 over 17`. Holdings, pre-declared in their §G, so this is
    # an agreed difference rather than one either side had to discover.
    #
    # BUT THEIR STATED CAUSE NAMES ONE LAP AND THEIR OWN LIST SHOWS TWO. §G says
    # "your lap 14 has never reached us" and then enumerates their inbound as
    # laps 1, 2, 3, 4, 5, 7, 9, 11, 15 -- **our lap 13 is absent from it too**.
    # Ours below 16 are 1, 2, 3, 4, 5, 7, 9, 11, 13, 14, 15; theirs are 2, 6, 8,
    # 10, 12, 13. 17 minus our 13 and our 14 is 15, which is exactly what they
    # declare, and no other pair reproduces it.
    #
    # So sending lap 14 alone will NOT reconcile the records. Reported in our
    # lap 17 §7 with both laps named. Comes out when a later lap of theirs
    # enumerates seventeen.
    "round-14-lap-16.md": "7b5737acf715a7f5",
    # Round 14 lap 18, theirs. Declares `999fe4e8a9d13d86 over 20`; we re-derive
    # `5469816e2d1591e3` over the SAME COUNT of 20.
    #
    # SAME COUNT, DIFFERENT SET, and that combination is new. Every entry above
    # disagreed on the number, which at least announces itself; here the two
    # populations are both 20 and are not the same 20, so the count carries no
    # signal at all. Two causes, both already on the record:
    #
    #   - **The lap 18s crossed.** Both sides wrote one, neither had the
    #     other's, so their record cannot contain ours and ours contains theirs.
    #     This is the fourth crossing of round 14 -- laps 2, 13, 16 and 18 --
    #     and it is what HANDSHAKE-NEXT-LAP is being added to remove.
    #   - **They have never held our lap 2**, declared by their own laps 6 and
    #     8 and unresolved since.
    #
    # It is also what found the over-match defect in our own round-digest.py:
    # `--exclude round-14-lap-18.md` matched BOTH files and dropped both, so the
    # tool answered confidently over a population nobody asked for. The
    # under-match mirror -- a token matching nothing -- was fixed in round 9
    # after Platterpus found it in theirs; neither side had asked the question
    # the other way round. `--exclude` now refuses an ambiguous basename and
    # takes a path, and check_lap() names files by path.
    #
    # Pinned by their declared value so an edit to their file fails here rather
    # than being excused. Comes out when a later lap of theirs enumerates a
    # population that includes our lap 2 and our lap 18.
    "round-14-lap-18.md": "999fe4e8a9d13d86",
}


def test_a_declared_digest_re_derives():
    """Covers: C21 (round 9 lap 8)

    **The defect: round 9 lap 7 declared `53f0b465833ac845 over 4`.** A real
    digest of a real set -- our holdings at an earlier moment excluding the
    peer's lap 4 -- produced by a command run to VERIFY THEIR declaration, then
    transcribed into the writer's field and never re-derived after the file it
    belonged to was written. Platterpus could not reproduce it and recovered the
    subset by exhaustive search over every subset of the eight laps they hold.

    Their diagnosis was that our enumerator was dropping their laps 4 and 6.
    `[REFUTED]` -- the enumerator produces their expected value at the very
    commit that carries the wrong declaration, and did before this change. The
    finding was right, the cause was not, and the cause is what you act on.

    A digest is the one field a human cannot proofread: every wrong value looks
    exactly like every right one. So it must not be typed, and until this test
    nothing stopped it being.
    """
    for problem in scan_declarations(WRITER_DIGEST_CHECKED_FROM,
                                     KNOWN_UNREPRODUCIBLE):
        check(False, problem)


def scan_declarations(scope, pins):
    """Every declared digest in the record, judged. Returns a list of problems.

    A function rather than a loop inside the test so it can be driven against a
    SYNTHETIC record too. As a loop it could only ever run against this
    repository's real history, where the pinned laps are immutable -- so the
    by-value pinning below was unfalsifiable, and a revert to pinning by
    filename passed. Found by running that revert and watching it not fail.
    """
    from_round, from_lap = scope
    problems, seen = [], set()
    for path in rdg.candidates():
        parts = rdg.is_a_lap(path.read_bytes().decode("utf-8", errors="replace"))
        if not parts:
            continue
        rnd, lap = int(parts[0]), int(parts[1])
        status, decl, comp, _ = rdg.check_lap(path)
        if status == "undeclared":
            continue
        known = pins.get(path.name)
        if known and decl[0] == known:
            seen.add(path.name)
            if status != "mismatch":
                problems.append(
                    f"{path.name} is pinned as not re-deriving but now does; "
                    "remove it from KNOWN_UNREPRODUCIBLE")
            continue
        if (rnd, lap) < (from_round, from_lap):
            continue
        if status != "match":
            problems.append(f"{path.name} declares {decl[0]} over {decl[1]}, "
                            f"re-derives {comp[0]} over {comp[1]}")
    if seen != set(pins):
        problems.append(f"a pinned lap changed or vanished: {set(pins) - seen}")
    return problems


def test_the_digest_checker_can_fail():
    """Covers: C21 (round 9 lap 8)

    The check above can only fail on a real defect, so on a healthy record it
    passes by finding nothing -- the shape this project's own rules say to
    distrust. This drives it against a record built to be wrong.
    """
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "inbound").mkdir()
    lap = ("HANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: {}\n"
           "HANDSHAKE-FROM: {}\n{}\nbody {}\n")
    real = rdg.HS
    try:
        rdg.HS = d
        (d / "round-09-lap-01.md").write_text(
            lap.format(1, "cyanrip-fork", "", "one"), encoding="utf-8")
        (d / "inbound" / "round-09-lap-02.md").write_text(
            lap.format(2, "platterpus", "", "two"), encoding="utf-8")

        # Lap 3 must exist before its own digest can be computed excluding it:
        # --exclude refuses a name that matches nothing, which is the fix from
        # round 9 lap 6 §F3 doing its job inside its own test.
        good = d / "round-09-lap-03.md"
        good.write_text(lap.format(3, "cyanrip-fork", "", "three"),
                        encoding="utf-8")
        truth, n, _ = rdg.digest(9, ["round-09-lap-03.md"])
        check(n == 2, f"the synthetic record did not enumerate 2 laps: {n}")

        good.write_text(lap.format(
            3, "cyanrip-fork",
            f"HANDSHAKE-ROUND-DIGEST: sha256/16 = {truth} over 2 lap(s)",
            "three"), encoding="utf-8")
        check(rdg.check_lap(good)[0] == "match",
              "a correct declaration was not recognised")

        # Every way it can be wrong, one at a time.
        for label, field in (
            ("a wrong hash",
             f"HANDSHAKE-ROUND-DIGEST: sha256/16 = {'0' * 16} over 2 lap(s)"),
            ("a wrong count",
             f"HANDSHAKE-ROUND-DIGEST: sha256/16 = {truth} over 9 lap(s)"),
        ):
            good.write_text(lap.format(3, "cyanrip-fork", field, "three"),
                            encoding="utf-8")
            check(rdg.check_lap(good)[0] == "mismatch",
                  f"{label} was accepted as a match")

        # Prose before the clause is not a declaration -- round 9 lap 1 says
        # "not computable" and then quotes ROUND 8's digest. Reading that as
        # round 9's is what the first version of the checker did.
        good.write_text(lap.format(
            3, "cyanrip-fork",
            "HANDSHAKE-ROUND-DIGEST: not computable. For round 8: "
            f"sha256/16 = {'f' * 16} over 12 lap(s).", "three"),
            encoding="utf-8")
        check(rdg.check_lap(good)[0] == "undeclared",
              "a digest quoted for another round was read as this round's")

        # THE PROPERTY THAT MAKES OLD DECLARATIONS STILL CHECKABLE, and the one
        # the first version of this test could not see: a lap's declaration
        # covers the holdings that existed WHEN IT WAS WRITTEN, so re-deriving
        # it must drop every lap filed since -- not just the lap itself.
        #
        # Invisible until a later lap exists. With lap 3 the newest, "drop laps
        # >= 3" and "drop lap 3" are the same set, so reverting the rule to the
        # wrong one changed nothing and the test still passed. Found by running
        # the revert-proof and watching it NOT fail, which is the only reason
        # this block is here.
        good.write_text(lap.format(
            3, "cyanrip-fork",
            f"HANDSHAKE-ROUND-DIGEST: sha256/16 = {truth} over 2 lap(s)",
            "three"), encoding="utf-8")
        (d / "inbound" / "round-09-lap-04.md").write_text(
            lap.format(4, "platterpus", "", "four"), encoding="utf-8")
        check(rdg.check_lap(good)[0] == "match",
              "lap 3's declaration stopped re-deriving once lap 4 was filed; "
              "the reconstruction is dropping only the lap itself")

        # And the pin is by VALUE, so editing a lap that is excused for a known
        # wrong declaration stops excusing it. Proved here rather than on the
        # real record because a sent lap is immutable -- the rule this session
        # already broke once.
        edited = good.read_text().replace(truth, "d" * 16)
        good.write_text(edited, encoding="utf-8")
        st, decl, _, _ = rdg.check_lap(good)
        check(st == "mismatch" and decl[0] == "d" * 16,
              f"an edited declaration was not seen as changed: {st} {decl}")

        # And the scan's PIN, driven the only way it can be: a pinned lap whose
        # declaration has moved must stop being excused. On the real record the
        # pinned laps are sent and immutable, so this is unreachable there --
        # which is why a revert to pinning by filename passed the first version.
        pins = {"round-09-lap-03.md": "d" * 16}
        check(not scan_declarations((9, 9), pins),
              "a lap pinned by its current wrong value was not excused")
        pins = {"round-09-lap-03.md": "e" * 16}
        problems = scan_declarations((9, 9), pins)
        check(any("changed or vanished" in p for p in problems),
              f"an edited pinned lap was still excused: {problems}")

        # TWO FILES, ONE BASENAME -- and the pin must excuse only one of them.
        #
        # Round 14 has two files called `round-14-lap-13.md`: ours in
        # docs/handshake/ and theirs in inbound/. Both sides numbered from
        # their own directory listing, which is the same collision round 14
        # already hit twice at lap 2. Pins are keyed on the BASENAME, so an
        # entry added for their file matches ours as well -- and if the key were
        # the whole story, allowlisting theirs would silently allowlist a wrong
        # declaration of ours.
        #
        # It does not, because an entry applies only when the DECLARED VALUE
        # also matches. That guard was added so an edit to a pinned lap would
        # stop excusing it; it now carries a second load nobody designed it for,
        # so it gets its own assertion rather than being left to be rediscovered
        # the next time two laps share a number.
        good.write_text(lap.format(
            3, "cyanrip-fork",
            f"HANDSHAKE-ROUND-DIGEST: sha256/16 = {truth} over 2 lap(s)",
            "three"), encoding="utf-8")
        theirs = d / "inbound" / "round-09-lap-03.md"
        theirs.write_text(lap.format(
            3, "platterpus",
            f"HANDSHAKE-ROUND-DIGEST: sha256/16 = {'a' * 16} over 2 lap(s)",
            "three-theirs"), encoding="utf-8")
        # Scope (9, 1), NOT (9, 9): scan_declarations skips laps below its
        # scope, so at (9, 9) nothing here is judged at all and every
        # assertion below would pass on an empty list. The first draft of this
        # block used (9, 9) and failed for exactly that reason -- which is the
        # good outcome, since the alternative was a test that passed vacuously.
        pins = {"round-09-lap-03.md": "a" * 16}
        check(not scan_declarations((9, 1), pins),
              "the same-basename pair was not both judged and excused "
              "correctly with a matching pin")

        # Now break OURS. The pin still names the basename and still holds
        # THEIR value, so if the basename alone excused a file, this would pass.
        good.write_text(lap.format(
            3, "cyanrip-fork",
            f"HANDSHAKE-ROUND-DIGEST: sha256/16 = {'b' * 16} over 2 lap(s)",
            "three"), encoding="utf-8")
        problems = scan_declarations((9, 1), pins)
        check(any("b" * 16 in p for p in problems),
              "a pin for the PEER's file of the same basename excused OUR "
              f"wrong declaration: {problems}")
        theirs.unlink()
    finally:
        rdg.HS = real


def test_a_superseded_peer_verdict_does_not_close_a_round():
    """Covers: C21 (round 9 lap 8)

    **Measured on this repository, not imagined.** Round 9 lap 7 declared
    `PEER-VERDICT: GO`, transcribed from their lap 4, while we held their lap 6
    declaring `HOLD` -- and said so in its own header. The gate read only our
    outbox, saw GO + GO, and printed *"Release allowed: every round is closed"*
    for a round Platterpus had been holding open for two laps.

    Their gate closed a round off a file whose text said HOLD. Ours closed one
    off a peer verdict that was real, correctly transcribed, and superseded.
    **Transcription was never the weak point. Recency was.**

    The check is bounded by what we hold: a peer lap we never received cannot
    make us stale. `HANDSHAKE-INBOUND-HELD` is what catches that, from their
    side, and this does not replace it.
    """
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "inbound").mkdir()
    (d / "round-9.md").write_text(GO, encoding="utf-8")
    peer = ("HANDSHAKE-PROTOCOL: 4\nHANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: {}\n"
            "HANDSHAKE-FROM: platterpus\nHANDSHAKE-VERDICT: {}\n")

    # No inbound lap at all: judged exactly as before. Rounds 5-7 are this.
    check(rg.check(rg.load_rounds(d))[0],
          "a round with no peer file held was refused")

    (d / "inbound" / "round-09-lap-04.md").write_text(
        peer.format(4, "GO"), encoding="utf-8")
    check(rg.check(rg.load_rounds(d))[0],
          "a peer GO we hold did not permit the close")

    (d / "inbound" / "round-09-lap-06.md").write_text(
        peer.format(6, "HOLD"), encoding="utf-8")
    ok, probs = rg.check(rg.load_rounds(d))
    check(not ok, "a superseded peer GO still closed the round")
    check(any("round-09-lap-06.md" in p and "HOLD" in p for p in probs),
          f"refused without naming the newer peer lap: {probs}")

    # And it reopens correctly: a later peer GO closes it again. A check that
    # only ever refuses is a check nobody can satisfy.
    (d / "inbound" / "round-09-lap-10.md").write_text(
        peer.format(10, "GO"), encoding="utf-8")
    check(rg.check(rg.load_rounds(d))[0],
          "a newer peer GO did not close the round again")

    # Lap ORDER, not filename order. CLAUDE.md states the rule outright -- "lap
    # order comes from the declared number, not the filename" -- and our padded
    # convention hides every violation of it, because for laps 1-99 the two
    # orders agree. The first version of this case used padded names and a
    # revert to picking the LAST file in sorted order passed it.
    #
    # So the newest lap gets a name that sorts EARLY, which is not contrived:
    # inbound files arrive under whatever name the operator saved them as, and
    # this repo's own round-5.md and round-6.md are unpadded.
    # The newest lap sorts FIRST and says GO; an older one sorts LAST and says
    # HOLD. Reading by filename yields the HOLD and refuses; reading by lap
    # number yields the GO and closes. Nothing between the two answers.
    (d / "inbound" / "round-09-a-newest-lap.md").write_text(
        peer.format(11, "GO"), encoding="utf-8")
    (d / "inbound" / "round-09-zz-older-lap.md").write_text(
        peer.format(5, "HOLD"), encoding="utf-8")
    check(rg.check(rg.load_rounds(d))[0],
          "an OLDER peer lap overrode a newer one, so the order is by filename")

    # A peer file declaring a field twice is ambiguous, and ambiguity is never
    # resolved by taking the first -- the rule already applied to our own laps.
    (d / "inbound" / "round-09-lap-12.md").write_text(
        peer.format(12, "HOLD") + "HANDSHAKE-VERDICT: GO\n", encoding="utf-8")
    check(rg.check(rg.load_rounds(d))[0],
          "an ambiguous peer file was read as a verdict rather than skipped")


def test_a_round_we_did_not_open_can_still_close():
    """Covers: C21 (round 9 lap 10 §C2)

    Platterpus's gate required a file in the directory only a round's OPENER
    writes, so a round we opened could never close on their side -- it would
    have refused every release forever, on a round both sides had agreed. They
    found it by aiming our lap 9 §C at themselves instead of pointing at a test
    that already passed.

    We have no outbound/verified split to couple to: our laps live in one
    directory whoever opened. That is a reason to believe we do not have it, not
    evidence -- so this constructs the round and runs the gate, which is the
    standard their lap set for us. **A passing test named after a hazard is not
    the same as the hazard failing to reproduce.**

    The floor is asserted too: holding only THEIR file, with no lap of ours in
    the round, must stay open. A fix for "refuses everything" that arrives at
    "refuses nothing" is the trade their §C2 explicitly did not make.
    """
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "inbound").mkdir()
    peer = ("HANDSHAKE-PROTOCOL: 4\nHANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: 1\n"
            "HANDSHAKE-FROM: platterpus\nHANDSHAKE-VERDICT: GO\n")
    (d / "inbound" / "round-09-lap-01.md").write_text(peer, encoding="utf-8")

    # Their lap alone: we have contributed nothing, so there is no agreement.
    #
    # **This is the mirror defect, and it was ours.** load_rounds() enumerated
    # only our own files, so a round they opened and we had not answered was
    # not merely open -- it was INVISIBLE. Measured on a record holding a closed
    # round of ours plus an unanswered peer-opened round: one round listed,
    # "Release allowed". Theirs refused a release that should have been allowed;
    # ours allowed one during a round we had not even replied to. Fail-open is
    # the worse direction and we had it.
    #
    # A closed round of ours is present so the record is NOT empty -- main()
    # refuses an empty record for an unrelated reason, and without this the case
    # would pass through that guard and prove nothing.
    (d / "round-08-lap-17.md").write_text(
        (HERE.parent / "docs" / "handshake" / "round-08-lap-17.md")
        .read_text(encoding="utf-8"), encoding="utf-8")
    rounds = rg.load_rounds(d)
    check(9 in [r.number for r in rounds],
          "a peer-opened round we have not answered is invisible to the gate")
    ok, probs = rg.check(rounds)
    check(not ok, f"a round with no lap of ours permitted a release: {probs}")
    check(any("have not answered" in p for p in probs),
          f"refused, but not for the right reason: {probs}")

    # And `closed` itself, not only check()'s verdict. check() short-circuits on
    # peer_only and never consults it, so reverting the guard in `closed` left
    # this whole test green -- while main() prints its per-round state from
    # r.closed and gen-release-manifest.py derives round_closed from this same
    # loader. Both would have read "closed" for a round the gate was refusing.
    peer_round = [r for r in rounds if r.number == 9][0]
    check(not peer_round.closed,
          "Lap.closed reported a peer-opened unanswered round as closed; "
          "main()'s summary and the release manifest both read this directly")
    check("have not answered" in peer_round.why,
          f"the printed reason does not name the cause: {peer_round.why!r}")

    # Our verification, lap 2 -- we did not open this round and never will have
    # a lap 1 in it. It must still close. A fix for "cannot see it" that lands
    # on "can never close it" is their §C2 defect imported.
    ours = GO.replace("HANDSHAKE-LAP: 1", "HANDSHAKE-LAP: 2")
    check("HANDSHAKE-LAP: 2" in ours, "the lap number substitution did not land")
    (d / "round-09-lap-02.md").write_text(ours, encoding="utf-8")
    ok, probs = rg.check(rg.load_rounds(d))
    check(ok, f"a round we did not open could not close: {probs}")

    # LAST, because it leaves the record open and every assertion after it would
    # inherit that. A GRANDFATHERED number is where `closed`'s peer_only guard is
    # the only thing that works: rounds 5 and 6 close on "verdict is None and the
    # number is old", and a peer-only round has verdict None for an entirely
    # different reason, so it satisfies that test by coincidence. Below
    # `grandfathered` the guard is dead code every later check already covers;
    # above it, this is the case it catches.
    (d / "inbound" / "round-05-lap-01.md").write_text(
        peer.replace("HANDSHAKE-ROUND: 9", "HANDSHAKE-ROUND: 5"),
        encoding="utf-8")
    five = [r for r in rg.load_rounds(d) if r.number == 5]
    check(len(five) == 1, "the peer-only round 5 was not enumerated")
    if five:
        check(not five[0].closed,
              "a peer-opened round we never answered was GRANDFATHERED closed "
              "because its verdict is None and its number is 5")
    ok, probs = rg.check(rg.load_rounds(d))
    check(not ok, f"a grandfathered peer-only round permitted a release: {probs}")


def test_a_standing_status_is_never_counted_as_a_lap():
    """Covers: PROTOCOL v4 §5a, and a file we now really hold.

    Both projects send a STANDING STATUS between rounds -- Platterpus invented
    the convention, we adopted it. It is deliberately not a lap: it declares no
    HANDSHAKE-ROUND or HANDSHAKE-LAP, so no conforming enumerator can count it.
    Both of theirs are filed under docs/handshake/inbound/ as evidence, because
    a document we quote has to be one we hold.

    That filing is what makes this worth executing rather than asserting. Their
    statuses now sit in the same directory as their laps, and the ONLY thing
    keeping them out of the round record is the glob. Two ways that could go
    wrong, and both are checked:

      * a status filed beside the laps must not be enumerated -- if the glob
        ever widened to `*.md`, every status would become a lap of some round;
      * a status that happened to CONTAIN the header text must still not be
        enumerated, because the filename is what the glob reads. This is the
        stronger case and the one a future rename would hit.

    The floor matters as much as the property: the real laps in the same
    directory must still be found, or a check that refuses everything would
    pass this while breaking the gate.

    AND THE REAL RECORD CANNOT STAND IN FOR THIS. Widening the glob to `*.md`
    and running the gate over docs/handshake/ still prints "Release allowed",
    because the two statuses we actually hold declare no wire headers -- so the
    live record is insensitive to the defect. The second fixture below is the
    one that discriminates, and it exists because "it does not break today" is
    not the same claim as "it cannot break".
    """
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "inbound").mkdir()

    # A COMPLETE lap, not a minimal one. The first draft carried only the
    # closure fields and the round would not close -- for an unrelated reason,
    # the v2 and v4 required-header sets -- which would have made the floor
    # below assert something this test is not about. A fixture that fails for
    # the wrong reason teaches nothing.
    ours = ("HANDSHAKE-PROTOCOL: 4\nHANDSHAKE-ROUND: 12\nHANDSHAKE-LAP: 3\n"
            "HANDSHAKE-FROM: cyanrip-fork\nHANDSHAKE-VERDICT: GO\n"
            "HANDSHAKE-PEER-VERDICT: GO\nHANDSHAKE-OUR-VERSION: x\n"
            "HANDSHAKE-OUR-PIN: aaaaaaa\nHANDSHAKE-PEER-VERSION: y\n"
            "HANDSHAKE-PEER-PIN: bbbbbbb\nHANDSHAKE-TESTED: suite\n"
            "HANDSHAKE-APP-VERSION: platterpus 0.6.23\n"
            "HANDSHAKE-RIPPER-VERSION: cyanrip x (platterpus-fork-gaaaaaaa)\n"
            "HANDSHAKE-PIN: aaaaaaa\n"
            "HANDSHAKE-FROM-REPO: https://example.invalid/a\n"
            "HANDSHAKE-FROM-COMMIT: aaaaaaa\n"
            "HANDSHAKE-TO-REPO: https://example.invalid/b\n"
            "HANDSHAKE-TO-VERSION: platterpus 0.6.23\n"
            "HANDSHAKE-INBOUND-HELD: none\n")
    (d / "round-12-lap-03.md").write_text(ours, encoding="utf-8")
    (d / "inbound" / "round-12-lap-02.md").write_text(
        "HANDSHAKE-PROTOCOL: 4\nHANDSHAKE-ROUND: 12\nHANDSHAKE-LAP: 2\n"
        "HANDSHAKE-FROM: platterpus\nHANDSHAKE-VERDICT: GO\n", encoding="utf-8")

    baseline = [r.number for r in rg.load_rounds(d)]
    check(baseline == [12], f"fixture is not one round: {baseline}")

    # A real standing status: no wire headers at all.
    (d / "inbound" / "status-2026-08-21-v0.6.23.md").write_text(
        "# Platterpus -> cyanrip fork · standing status\n\n"
        "NOT A LAP AND NOT A ROUND.\n", encoding="utf-8")

    # And the hostile one: header TEXT present, filename still not a lap.
    (d / "inbound" / "status-2026-09-01-v0.7.0.md").write_text(
        "HANDSHAKE-ROUND: 99\nHANDSHAKE-LAP: 1\nHANDSHAKE-FROM: platterpus\n"
        "HANDSHAKE-VERDICT: GO\n", encoding="utf-8")

    after = [r.number for r in rg.load_rounds(d)]
    check(after == baseline,
          f"a standing status filed beside the laps was counted as one: "
          f"{baseline} became {after}")
    check(99 not in after,
          "a non-lap filename carrying wire headers was enumerated as round 99")

    # The floor, and it is not optional: a glob that matched NOTHING would
    # satisfy every assertion above. So the round the real laps describe must
    # still be found, still be at lap 3, and still close -- the status files
    # must be invisible, not the directory.
    r12 = [r for r in rg.load_rounds(d) if r.number == 12]
    check(len(r12) == 1, f"round 12 went missing: {r12}")
    check(r12[0].lap == 3,
          f"round 12 is at lap {r12[0].lap!r}, not 3 -- a status file was read "
          f"as the newest lap")
    check(r12[0].closed,
          "round 12 stopped closing once status files were filed beside it")


def test_exclude_refuses_when_it_matches_nothing():
    """Covers: C21 (round 9 lap 6 §F3)

    Platterpus found this in their implementation and we had it identically:
    `--exclude` matched on basename and silently dropped nothing otherwise, so
    a wrong name printed a confident digest over the full set. **A manufactured
    mismatch, indistinguishable from a real one, inside the tool implementing
    the one rule neither side may override.**

    The fix shipped in round 9 lap 7 with no test. Reverting it to a no-op left
    the whole suite green -- found here by trying it, three laps later.
    """
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "inbound").mkdir()
    real = rdg.HS
    try:
        rdg.HS = d
        (d / "round-09-lap-01.md").write_text(
            "HANDSHAKE-ROUND: 9\nHANDSHAKE-LAP: 1\n"
            "HANDSHAKE-FROM: cyanrip-fork\nbody\n", encoding="utf-8")
        full, n, _ = rdg.digest(9)
        check(n == 1, f"synthetic record did not enumerate 1 lap: {n}")

        for bad in ("docs/handshake/round-09-lap-01.md",  # a path, not a name
                    "round-09-lap-99.md",                 # no such lap
                    "round-9-lap-1.md"):                  # unpadded
            try:
                rdg.digest(9, [bad])
                check(False, f"--exclude {bad} printed a digest instead of "
                             "refusing; it silently dropped nothing")
            except SystemExit as e:
                check(bad in str(e),
                      f"refused without naming the unmatched value: {e}")

        # And it still works when the name IS right, so the refusal is not
        # simply "always refuse".
        got, n, _ = rdg.digest(9, ["round-09-lap-01.md"])
        check(n == 0 and got != full,
              f"a matching --exclude did not drop the lap: {n}")
    finally:
        rdg.HS = real


for name, fn in sorted(globals().items()):
    if name.startswith("test_") and callable(fn):
        fn()

if failures:
    print(f"{failures} check(s) failed", file=sys.stderr)
    sys.exit(1)
print("all release gate checks passed")

