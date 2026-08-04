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

  * The field is matched line-anchored at column 0. Prose *about* a verdict is
    not a verdict: a round file that says "this is not a closing GO" must not
    close a round because the word GO appears in it.

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
PROTOCOL_VERSION = 1
PROTOCOL_RE = re.compile(r"^HANDSHAKE-PROTOCOL:[ \t]*(\d+)[ \t]*$", re.M)

PEER_VERDICT_RE = re.compile(r"^HANDSHAKE-PEER-VERDICT:[ \t]*([A-Z][A-Z-]*)[ \t]*$", re.M)
PEER_VERSION_RE = re.compile(r"^HANDSHAKE-PEER-VERSION:[ \t]*(\S.*?)[ \t]*$", re.M)
PEER_PIN_RE = re.compile(r"^HANDSHAKE-PEER-PIN:[ \t]*(\S+)[ \t]*$", re.M)
OUR_VERSION_RE = re.compile(r"^HANDSHAKE-OUR-VERSION:[ \t]*(\S.*?)[ \t]*$", re.M)
OUR_PIN_RE = re.compile(r"^HANDSHAKE-OUR-PIN:[ \t]*(\S+)[ \t]*$", re.M)
TESTED_RE = re.compile(r"^HANDSHAKE-TESTED:[ \t]*(\S.*?)[ \t]*$", re.M)

# Only GO closes a round. Anything else -- including a verdict this script has
# never heard of -- leaves it open, because an unrecognised verdict is not
# evidence of agreement.
CLOSING = {"GO"}


class Lap:
    def __init__(self, number, lap, path, verdict, declared_number,
                 peer_verdict=None, peer_version=None, peer_pin=None,
                 our_version=None, our_pin=None, tested=None, protocol=None):
        self.number = number
        self.lap = lap
        self.path = path
        self.verdict = verdict
        self.declared_number = declared_number
        self.peer_verdict = peer_verdict
        self.peer_version = peer_version
        self.peer_pin = peer_pin
        self.our_version = our_version
        self.our_pin = our_pin
        self.tested = tested
        self.protocol = protocol

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

    @property
    def closed(self):
        if self.grandfathered:
            return True
        if not self.protocol_ok:
            return False
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


def load_rounds(directory=HANDSHAKE_DIR):
    all_laps = []
    for path in sorted(directory.glob("round-*.md")):
        m = re.match(r"round-(\d+)", path.name)
        if not m:
            continue
        text = path.read_text(encoding="utf-8")
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
        ))

    # A round's state is its latest lap. An unparseable lap number sorts to the
    # end so it cannot be shadowed by a well-formed earlier one.
    latest = {}
    for lp in all_laps:
        cur = latest.get(lp.number)
        if cur is None or lp.lap is None or (cur.lap is not None and lp.lap > cur.lap):
            latest[lp.number] = lp
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
        if not r.closed:
            problems.append(f"round {r.number} is not closed ({r.why}): {r.path.name}")
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
    return 1 if args.release_gate else 0


if __name__ == "__main__":
    sys.exit(main())
