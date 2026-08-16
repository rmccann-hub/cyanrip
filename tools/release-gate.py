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

"""Decide whether this tree may be released, and say why not when it may not.

The rule has existed in prose since r1 -- "no release and no pin switch while a
handshake round is open" -- and until now nothing executed it. Prose that
nothing executes is a rule only for as long as somebody remembers it.

Platterpus found the specific way a gate like this goes wrong (their round-7
verification, section 11): theirs derived "round closed" from three *files
existing*, so a file whose first paragraph said "HOLD, do not release" counted
as a close exactly like a GO would have. Every property below exists because
that failure, or one this repo has already made, would otherwise be reachable:

  * The verdict is read from a declared field, never inferred from a file being
    present. A round file exists from the moment it is started.

  * The field is matched line-anchored at column 0, and **fenced code blocks are
    stripped before matching**. Prose *about* a verdict is not a verdict, and
    neither is an example of one: a round file that says "this is not a closing
    GO" must not close a round, and a file that documents the format by showing
    `HANDSHAKE-PEER-VERSION: platterpus/0.6.4` inside a ``` block must not be
    read as declaring it. Found the hard way -- the lap that introduced the
    shared spec had its own examples parsed as declarations.

  * A round with no verdict field fails closed. The tempting shortcut -- treat a
    missing verdict as GO so historical rounds still pass -- puts the entire
    defect back through the fallback. Rounds predating the convention are
    grandfathered *by number*, in a set spelled out below, so that adding a
    round to it is a visible act rather than a side effect.

  * OPEN and HOLD are both "not closed". A deliberate mid-round lap is the
    normal case, not an edge case.

  * A close is *affirmative and two-sided*. Our own GO is a statement about our
    tree, not agreement: it also needs the peer's declared GO, both sides'
    versions and pins, and a declaration of what was tested. Any one missing and
    the round stays open. "They did not object" is not "they agreed", and a
    round that closed without testing would be a release nobody checked.

  * A round can take several laps, and its state is the *latest* lap's verdict.
    The alternative -- every lap must say GO -- would force us to go back and
    edit a file we had already sent, which is the one thing a record of an
    exchange must never do. A later lap may therefore also *reopen* a round, and
    a test asserts it can.

Run with no arguments for a human summary; --release-gate exits non-zero when a
release is not permitted, which is the form a script should use.
"""

import argparse
import pathlib
import re
import sys

HANDSHAKE_DIR = pathlib.Path(__file__).resolve().parent.parent / "docs" / "handshake"

# Rounds 5 and 6 were recorded before the verdict field existed. They are
# grandfathered by number rather than by "has no field", because the latter is
# the fallback that reintroduces the whole defect -- under it, any new round
# would close simply by omitting the field. Pinned, and asserted by a test.
GRANDFATHERED = {5, 6}

# The v2 wire header (FROM / APP-VERSION / RIPPER-VERSION / PIN) is required
# from this round on. Rounds up to and including 7 are exempt because neither
# project could comply with a spec that was written during round 7 -- stated in
# round-07-lap-04.md and agreed with Platterpus. Pinned, and asserted by a test, so
# widening the exemption is a visible edit rather than a side effect.
WIRE_HEADER_REQUIRED_FROM = 8

# Column 0 only. A quoted or indented copy inside prose is not a declaration.
VERDICT_RE = re.compile(r"^HANDSHAKE-VERDICT:[ \t]*([A-Z][A-Z-]*)[ \t]*$", re.M)
ROUND_RE = re.compile(r"^HANDSHAKE-ROUND:[ \t]*(\d+)[ \t]*$", re.M)
LAP_RE = re.compile(r"^HANDSHAKE-LAP:[ \t]*(\d+)[ \t]*$", re.M)

# A close needs BOTH sides to have said yes and testing to have happened. Our
# own GO is a statement about our tree; it is not agreement. These carry the
# other half, recorded from the file they actually sent.
# The shared spec both projects implement. A file declaring a version this gate
# does not implement is refused rather than guessed at -- see docs/handshake/
# PROTOCOL.md, which is copied into both repositories.
PROTOCOL_VERSION = 4
PROTOCOL_RE = re.compile(r"^HANDSHAKE-PROTOCOL:[ \t]*(\d+)[ \t]*$", re.M)

# Adopted from Platterpus round 7 lap 3 §1: the wire header both sides emit.
# FROM makes a crossed pair unambiguous without filename conventions;
# APP-VERSION and RIPPER-VERSION say which *pair* produced a file's results, so
# a result carries its provenance rather than needing it reconstructed.
FROM_RE = re.compile(r"^HANDSHAKE-FROM:[ \t]*(\S+)[ \t]*$", re.M)
APP_VERSION_RE = re.compile(r"^HANDSHAKE-APP-VERSION:[ \t]*(\S.*?)[ \t]*$", re.M)
RIPPER_VERSION_RE = re.compile(r"^HANDSHAKE-RIPPER-VERSION:[ \t]*(\S.*?)[ \t]*$", re.M)
PIN_RE = re.compile(r"^HANDSHAKE-PIN:[ \t]*(\S+)[ \t]*$", re.M)

# A build designated to gather the hardware evidence a close requires. It is
# NOT a release and must never close a round -- see PROTOCOL.md 6a for the
# deadlock it breaks. Parsed so the gate can report which build the rig should
# be running, and asserted never to affect closure.
TEST_PIN_RE = re.compile(r"^HANDSHAKE-TEST-PIN:[ \t]*(\S+)[ \t]*$", re.M)

PEER_VERDICT_RE = re.compile(r"^HANDSHAKE-PEER-VERDICT:[ \t]*([A-Z][A-Z-]*)[ \t]*$", re.M)
PEER_VERSION_RE = re.compile(r"^HANDSHAKE-PEER-VERSION:[ \t]*(\S.*?)[ \t]*$", re.M)
PEER_PIN_RE = re.compile(r"^HANDSHAKE-PEER-PIN:[ \t]*(\S+)[ \t]*$", re.M)
OUR_VERSION_RE = re.compile(r"^HANDSHAKE-OUR-VERSION:[ \t]*(\S.*?)[ \t]*$", re.M)
OUR_PIN_RE = re.compile(r"^HANDSHAKE-OUR-PIN:[ \t]*(\S+)[ \t]*$", re.M)

# v4 fields. Captured to end-of-line rather than \S+ because every one of them
# carries prose: an INBOUND-HELD that says "none" and a digest that explains why
# it could not be computed are both legal and both meaningful.
INBOUND_RE = re.compile(r"^HANDSHAKE-INBOUND-HELD:[ \t]*(.+?)[ \t]*$", re.M)
DIGEST_RE = re.compile(r"^HANDSHAKE-ROUND-DIGEST:[ \t]*(.+?)[ \t]*$", re.M)
TO_REPO_RE = re.compile(r"^HANDSHAKE-TO-REPO:[ \t]*(.+?)[ \t]*$", re.M)
FROM_REPO_RE = re.compile(r"^HANDSHAKE-FROM-REPO:[ \t]*(\S+)[ \t]*$", re.M)
FROM_COMMIT_RE = re.compile(r"^HANDSHAKE-FROM-COMMIT:[ \t]*(.+?)[ \t]*$", re.M)
TO_VERSION_RE = re.compile(r"^HANDSHAKE-TO-VERSION:[ \t]*(.+?)[ \t]*$", re.M)
WITHDRAWN_REASON_RE = re.compile(r"^HANDSHAKE-WITHDRAWN-REASON:[ \t]*(.+?)[ \t]*$", re.M)
OVERRIDE_RE = re.compile(r"^HANDSHAKE-OVERRIDE:[ \t]*(.+?)[ \t]*$", re.M)
OVERRIDE_BY_RE = re.compile(r"^HANDSHAKE-OVERRIDE-BY:[ \t]*(.+?)[ \t]*$", re.M)
OVERRIDE_WHY_RE = re.compile(r"^HANDSHAKE-OVERRIDE-WHY:[ \t]*(.+?)[ \t]*$", re.M)

# v4 6a-bis R7. A lap past this needs a recorded override.
LAP_CEILING = 21

# v4 3a: required from round 9, the way v2's four are required from round 8.
ADDRESSING_FROM_ROUND = 9
TESTED_RE = re.compile(r"^HANDSHAKE-TESTED:[ \t]*(\S.*?)[ \t]*$", re.M)

# Only GO closes a round. Anything else -- including a verdict this script has
# never heard of -- leaves it open, because an unrecognised verdict is not
# evidence of agreement.
CLOSING = {"GO"}


class Lap:
    def __init__(self, number, lap, path, verdict, declared_number,
                 peer_verdict=None, peer_version=None, peer_pin=None,
                 our_version=None, our_pin=None, tested=None, protocol=None,
                 sender=None, app_version=None, ripper_version=None, pin=None,
                 test_pin=None):
        self.number = number
        self.lap = lap
        self.path = path
        self.verdict = verdict
        self.declared_number = declared_number
        self.tied_with = None
        self.peer_verdict = peer_verdict
        self.peer_version = peer_version
        self.peer_pin = peer_pin
        self.our_version = our_version
        self.our_pin = our_pin
        # v4. Defaulted to None so a v2/v3 file keeps working unchanged --
        # unknown-fields-are-ignored cuts both ways, and a gate that broke on
        # an older file would make the version bump a flag day.
        self.inbound_held = None
        self.digest = None
        self.to_repo = None
        self.from_repo = None
        self.from_commit = None
        self.to_version = None
        self.withdrawn_reason = None
        self.override = None
        self.override_by = None
        self.override_why = None
        self.tested = tested
        self.protocol = protocol
        self.sender = sender
        self.app_version = app_version
        self.ripper_version = ripper_version
        self.pin = pin
        self.test_pin = test_pin

    def missing_wire_header(self):
        """v2 fields every file must declare, from WIRE_HEADER_REQUIRED_FROM on.

        Separate from missing_for_close(): these are required on *every* file,
        including a mid-round HOLD, because a lap reporting a measurement must
        say which pair produced it. The close-only fields say who agreed."""
        if self.number < WIRE_HEADER_REQUIRED_FROM:
            return []
        need = {
            "HANDSHAKE-FROM": self.sender,
            "HANDSHAKE-APP-VERSION": self.app_version,
            "HANDSHAKE-RIPPER-VERSION": self.ripper_version,
            "HANDSHAKE-PIN": self.pin,
        }
        return [k for k, v in need.items() if not v]

    def missing_for_close(self):
        """Fields a close requires. Named individually so the gate can say
        which one is absent rather than refusing without a reason."""
        need = {
            "HANDSHAKE-PEER-VERDICT": self.peer_verdict,
            "HANDSHAKE-PEER-VERSION": self.peer_version,
            "HANDSHAKE-PEER-PIN": self.peer_pin,
            "HANDSHAKE-OUR-VERSION": self.our_version,
            "HANDSHAKE-OUR-PIN": self.our_pin,
            "HANDSHAKE-TESTED": self.tested,
        }
        return [k for k, v in need.items() if not v]

    @property
    def grandfathered(self):
        return self.verdict is None and self.number in GRANDFATHERED

    @property
    def protocol_ok(self):
        if self.protocol is None:
            return self.grandfathered
        return int(self.protocol) <= PROTOCOL_VERSION

    def missing_v4(self):
        """v4 fields this lap should carry and does not. Empty for older rounds.

        Scoped by ROUND rather than by declared protocol on purpose: a lap can
        under-declare its protocol -- ours did, for eight laps -- so keying the
        requirement on the declaration would let a file exempt itself from the
        checks by claiming to be older than it is."""
        if self.number is None or self.number < ADDRESSING_FROM_ROUND:
            return []
        want = {"HANDSHAKE-FROM-REPO": self.from_repo,
                "HANDSHAKE-FROM-COMMIT": self.from_commit,
                "HANDSHAKE-TO-REPO": self.to_repo,
                "HANDSHAKE-TO-VERSION": self.to_version,
                "HANDSHAKE-INBOUND-HELD": self.inbound_held}
        return [k for k, v in want.items() if not v]

    def bad_override(self):
        """An override that is not fully recorded, or that names the one rule
        no reason can waive."""
        if not self.override:
            return None
        if not self.override_by or not self.override_why:
            return ("HANDSHAKE-OVERRIDE without -BY and -WHY is not recorded, "
                    "and an unrecorded override did not happen")
        if re.search(r"\b5a\b|digest", self.override, re.I):
            return ("§5a's digest rule is not overridable -- two parties "
                    "exchanging GO over divergent records are agreeing about "
                    "different things")
        return None

    @property
    def over_ceiling(self):
        """v4 §6a-bis R7, and NOT retroactive.

        Round 7 ran to lap 39. Applying the ceiling backwards would reopen a
        round both projects closed, on a rule that did not exist while it ran
        -- and round 7 is the history that MOTIVATED the ceiling, so punishing
        it is the one outcome that teaches nothing. Scoped from the round v4
        was adopted in, exactly like the addressing fields, and for the same
        reason: a rule arrives at a round boundary or it rewrites the past."""
        if self.number is None or self.number < ADDRESSING_FROM_ROUND:
            return False
        return (self.lap is not None and self.lap > LAP_CEILING
                and not self.override)

    @property
    def withdrawn(self):
        """v4 §4b. Terminal, and requires only a reason -- there is no
        agreement to record. A gate must additionally refuse any release that
        names it, which check() does."""
        return self.verdict == "WITHDRAWN"

    @property
    def closed(self):
        if self.grandfathered:
            return True
        if not self.protocol_ok:
            return False
        if self.missing_wire_header():
            return False
        if self.missing_v4():
            return False
        if self.bad_override() or self.over_ceiling:
            return False
        # WITHDRAWN is terminal but is NOT a close that permits a release --
        # check() refuses one that names it. Reported separately so a withdrawn
        # round does not sit forever in the "not closed" list.
        if self.withdrawn:
            return bool(self.withdrawn_reason)
        if self.verdict not in CLOSING:
            return False
        # Our GO alone is not agreement.
        if self.peer_verdict not in CLOSING:
            return False
        return not self.missing_for_close()

    @property
    def why(self):
        if self.grandfathered:
            return "no verdict field, grandfathered by number"
        if self.protocol is not None and int(self.protocol) > PROTOCOL_VERSION:
            return (f"declares HANDSHAKE-PROTOCOL: {self.protocol}, this gate "
                    f"implements {PROTOCOL_VERSION} -- refusing rather than guessing")
        if self.protocol is None:
            return "NO HANDSHAKE-PROTOCOL FIELD -- fails closed"
        wire = self.missing_wire_header()
        if wire:
            return "missing required v2 wire header: " + ", ".join(wire)
        if self.tied_with:
            return ("two files declare lap "
                    f"{self.lap}, so there is no order between them: "
                    + ", ".join(self.tied_with)
                    + " -- ambiguity is not a close")
        if self.verdict is None:
            return "NO VERDICT FIELD -- fails closed"
        if self.verdict not in CLOSING:
            return f"verdict {self.verdict}"
        if self.peer_verdict is None:
            return "our verdict GO, but no peer verdict declared"
        if self.peer_verdict not in CLOSING:
            return f"our verdict GO, peer verdict {self.peer_verdict}"
        missing = self.missing_for_close()
        if missing:
            return "both verdicts GO, but missing " + ", ".join(missing)
        return "verdict GO, peer GO, versions/pins/testing declared"


FENCE_RE = re.compile(r"^```.*?^```", re.M | re.S)


def strip_fences(text):
    """Remove fenced code blocks, preserving line structure elsewhere.

    A declaration is a statement the file makes, not one it quotes. Examples,
    templates and conformance tables all legitimately contain field lines at
    column 0, and none of them is a declaration."""
    return FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def load_rounds(directory=None, every_lap=False):
    """Latest lap per round, or every lap when every_lap is set.

    Closure is a property of a round, so the default collapses each round to
    its latest lap. Well-formedness is a property of a FILE -- PROTOCOL.md C9
    refuses an individual file missing a required header -- and applying a
    per-file rule per-round-latest lets a malformed earlier lap through. That
    is not hypothetical: round-8 laps 1 and 3 went out missing three required
    fields and would still not have been caught by a check built on the
    default, because lap 5 superseded them.
    """
    # Resolved at call time, not bound at definition time. A default of
    # `directory=HANDSHAKE_DIR` captures the module-level value when the
    # function is defined, so any caller that points the gate at a different
    # record -- a test, a check of another checkout -- silently gets the real
    # one instead and its result is about the wrong files.
    if directory is None:
        directory = HANDSHAKE_DIR
    all_laps = []
    for path in sorted(directory.glob("round-*.md")):
        m = re.match(r"round-(\d+)", path.name)
        if not m:
            continue
        text = strip_fences(path.read_text(encoding="utf-8"))
        verdicts = VERDICT_RE.findall(text)
        declared = ROUND_RE.findall(text)

        # More than one declaration is ambiguous, and picking either one would
        # be a guess. Ambiguity is not a close.
        verdict = verdicts[0] if len(verdicts) == 1 else None
        if len(verdicts) > 1:
            verdict = "AMBIGUOUS"

        declared_number = int(declared[0]) if len(declared) == 1 else None

        # A file with no lap field is lap 1. Two lap declarations are ambiguous
        # and sort last, so ambiguity cannot be hidden behind a later lap.
        laps = LAP_RE.findall(text)
        lap = int(laps[0]) if len(laps) == 1 else (1 if not laps else None)

        def one(rx):
            hits = rx.findall(text)
            return hits[0] if len(hits) == 1 else None

        all_laps.append(Lap(
            int(m.group(1)), lap, path, verdict, declared_number,
            peer_verdict=one(PEER_VERDICT_RE),
            peer_version=one(PEER_VERSION_RE),
            peer_pin=one(PEER_PIN_RE),
            our_version=one(OUR_VERSION_RE),
            our_pin=one(OUR_PIN_RE),
            tested=one(TESTED_RE),
            protocol=one(PROTOCOL_RE),
            sender=one(FROM_RE),
            app_version=one(APP_VERSION_RE),
            ripper_version=one(RIPPER_VERSION_RE),
            pin=one(PIN_RE),
            test_pin=one(TEST_PIN_RE),
        ))
        # v4 fields, set after construction so the constructor signature stays
        # the v2 one -- Platterpus's gate is a separate implementation and a
        # widened positional signature is the kind of change that only breaks
        # for whoever tries to share code later.
        lp = all_laps[-1]
        lp.inbound_held = one(INBOUND_RE)
        lp.digest = one(DIGEST_RE)
        lp.to_repo = one(TO_REPO_RE)
        lp.from_repo = one(FROM_REPO_RE)
        lp.from_commit = one(FROM_COMMIT_RE)
        lp.to_version = one(TO_VERSION_RE)
        lp.withdrawn_reason = one(WITHDRAWN_REASON_RE)
        lp.override = one(OVERRIDE_RE)
        lp.override_by = one(OVERRIDE_BY_RE)
        lp.override_why = one(OVERRIDE_WHY_RE)

    # A round's state is its latest lap. An unparseable lap number sorts to the
    # end so it cannot be shadowed by a well-formed earlier one.
    latest = {}
    for lp in all_laps:
        cur = latest.get(lp.number)
        if cur is None or lp.lap is None or (cur.lap is not None and lp.lap > cur.lap):
            latest[lp.number] = lp

    # Two files declaring the SAME lap have no order between them, and the loop
    # above resolved that by keeping whichever `sorted()` yielded first -- i.e.
    # by FILENAME. Measured, not feared: with a lap 34 declaring HOLD and
    # another lap 34 declaring GO, the gate reported the GO and allowed a
    # release, purely because that file's name sorted earlier. It is the exact
    # defect Platterpus found in their own gate in round 7 lap 17, which we
    # believed we did not share because our comparison is on the declared
    # number rather than the stem -- true, and it does not help when the
    # declared numbers are equal.
    #
    # Equal lap numbers are ambiguous, and ambiguity is not a close. This
    # matters now because blind concurrent laps -- both sides reading one rig
    # artifact without seeing each other -- produce exactly this shape.
    for number, win in latest.items():
        if win.lap is None:
            continue
        tied = [lp for lp in all_laps if lp.number == number and lp.lap == win.lap]
        if len(tied) > 1:
            win.verdict = "AMBIGUOUS-LAP"
            win.tied_with = sorted(lp.path.name for lp in tied)
    if every_lap:
        return sorted(all_laps, key=lambda lp: (lp.number or 0, lp.lap or 0,
                                                lp.path.name))
    return [latest[k] for k in sorted(latest)]


def check(rounds):
    """Returns (ok, problems). Problems are reasons a release is not allowed."""
    problems = []
    for r in rounds:
        if r.lap is None:
            problems.append(
                f"round {r.number} has an ambiguous HANDSHAKE-LAP declaration: "
                f"{r.path.name}"
            )
        wire = r.missing_wire_header()
        if wire:
            problems.append(
                f"round {r.number} ({r.path.name}) is missing required v2 wire "
                f"header fields: {', '.join(wire)}"
            )
        if not r.closed:
            problems.append(f"round {r.number} is not closed ({r.why}): {r.path.name}")
        elif r.withdrawn:
            # v4 §4b, C27. WITHDRAWN is terminal -- the round is over and no
            # further lap can reopen it -- but it records NO agreement, so a
            # release must never name it. Without this, WITHDRAWN is a way to
            # get past "no release while a round is open" by ending the round
            # instead of closing it, which is worse than not having the state.
            problems.append(
                f"round {r.number} is WITHDRAWN, not closed by agreement, so no "
                f"release may name it: {r.path.name}"
                + (f" -- {r.withdrawn_reason}" if r.withdrawn_reason else ""))
        bad = r.bad_override()
        if bad:
            problems.append(f"round {r.number} ({r.path.name}): {bad}")
        miss4 = r.missing_v4()
        if miss4:
            problems.append(
                f"round {r.number} ({r.path.name}) is missing required v4 "
                f"fields: {', '.join(miss4)}")
        # A file that declares a different round number than its name is a
        # bookkeeping error that would make any per-round claim unresolvable.
        if r.declared_number is not None and r.declared_number != r.number:
            problems.append(
                f"round {r.number} declares HANDSHAKE-ROUND: {r.declared_number} "
                f"but is named {r.path.name}"
            )
        elif r.verdict is not None and r.declared_number is None:
            problems.append(
                f"round {r.number} has a verdict but no unambiguous "
                f"HANDSHAKE-ROUND declaration: {r.path.name}"
            )
    return (not problems), problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--release-gate", action="store_true",
                    help="exit non-zero if a release is not permitted")
    ap.add_argument("--prerelease", action="store_true",
                    help="permit a BETA/pre-release while a round is open, "
                         "after printing every open round")
    args = ap.parse_args()

    rounds = load_rounds()
    if not rounds:
        print("release-gate: no round files found -- refusing rather than "
              "reporting an empty record as agreement", file=sys.stderr)
        return 1

    ok, problems = check(rounds)

    print("Handshake rounds:")
    for r in rounds:
        state = "closed" if r.closed else "OPEN"
        lap = f"lap {r.lap}" if r.lap is not None else "lap ?"
        print(f"  round {r.number} ({lap}, {r.path.name}): {state:6}  ({r.why})")
        if r.override and not r.bad_override():
            # C32: every time the state is printed, not once. An override
            # that becomes invisible after the session that made it is
            # indistinguishable from the rule never having existed.
            print(f"      OVERRIDE {r.override} — by {r.override_by} "
                  f"— {r.override_why}")
        if r.test_pin:
            print(f"      test pin {r.test_pin} -- for the rig to gather "
                  f"evidence; NOT a release and does not close this round")
    print()

    if ok:
        print("Release allowed: every round is closed.")
        return 0

    print("Release NOT allowed:")
    for p in problems:
        print(f"  - {p}")
    print()
    print("A round closes when the other side's verification file agrees and "
          "this tree's round file declares HANDSHAKE-VERDICT: GO.")

    # A pre-release is permitted with a round open; a stable one is not.
    #
    # Adopted from Platterpus round 7 lap 7, and it is the same argument as
    # HANDSHAKE-TEST-PIN one level up: what the gate protects is the claim a
    # STABLE release makes -- that the pair was jointly verified. A beta makes
    # no such claim. It ships saying so, and every rip it produces carries
    # "NOT a released build" in its own log. Refusing it would not protect
    # anyone; it would guarantee the round can never close, because the
    # evidence a close requires can only come from running the thing.
    #
    # The open rounds are printed FIRST and unconditionally, so permitting a
    # beta is never quiet.
    if args.prerelease:
        print()
        print("PRE-RELEASE permitted: the rounds above are open, and a beta "
              "claims no joint verification. A STABLE release is still "
              "refused.")
        return 0

    return 1 if args.release_gate else 0


if __name__ == "__main__":
    sys.exit(main())
