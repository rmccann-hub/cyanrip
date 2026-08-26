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

"""Check a handshake lap and report findings in Platterpus's rig-check format.

WHY THIS EXISTS. Round 14 took sixteen laps, and a large share of them were one
side telling the other, in prose, what was wrong with a file. Every such finding
in that round was mechanical: a missing wire field, a digest that would not
re-derive, a pin naming the wrong repository, two files claiming one lap number.
**None of them needed an essay. They needed a checker and a line of output.**

THE FORMAT IS NOT OURS. It is Platterpus's `rig-check` manifest format, adopted
verbatim rather than invented:

    LEVEL  category/check  message  [artifact]

with levels OK / INFO / WARN / FAIL / SKIP. They built it, it is good, and a
second format would be a fourth shared document nobody asked for. Ours emits the
same shape so a finding can travel as a record instead of as a lap.

WHAT IT CHECKS AND WHAT IT REFUSES TO. It reads a lap file -- an artifact that
was *sent to us* -- and judges it against the shared protocol. It says nothing
about the sender's code, their environment, or their intentions, because we can
read none of those: round 12's blocker was a confident claim about a constant in
their source we had never seen. **A checker that stays on the artifact cannot
make that mistake.**

EVERY FAIL CARRIES A FIX. A finding that says what is wrong and not what to do
about it is the thing that generates a reply lap, which is the cost this file
exists to remove.

    tools/seam-check.py docs/handshake/inbound/round-14-lap-12.md
    tools/seam-check.py --all            # every lap in the record, ours included
"""

import argparse
import hashlib
import importlib.util
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HS = ROOT / "docs" / "handshake"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rg = _load("rg", ROOT / "tools" / "release-gate.py")
rdg = _load("rdg", ROOT / "tools" / "round-digest.py")

# Deliberately not a subclass of anything and not sortable by level: findings
# print in the order they were made, because the order a checker looks in is
# itself information for whoever reads the output.
FINDINGS = []


def note(level, cat, msg, fix=None, artifact=None):
    FINDINGS.append((level, cat, msg, fix, artifact))


def check_lap(path):
    """Every mechanical thing round 14 spent a lap saying in prose."""
    text = path.read_text(encoding="utf-8", errors="replace")
    name = path.name

    # --- protocol version -------------------------------------------------
    proto = rg.PROTOCOL_RE.findall(text)
    if not proto:
        note("FAIL", "wire/protocol", f"{name} declares no HANDSHAKE-PROTOCOL",
             fix="add `HANDSHAKE-PROTOCOL: 4` at column 0. A reader that has to "
                 "guess the version grades the file by rules the sender is not "
                 "following.")
    elif len(set(proto)) > 1:
        note("FAIL", "wire/protocol",
             f"{name} declares HANDSHAKE-PROTOCOL more than once: {set(proto)}",
             fix="declare it once. Two declarations are ambiguous, and under "
                 "§5a a file declaring a wire field twice is not a lap at all.")
    elif int(proto[0]) > rg.PROTOCOL_VERSION:
        note("WARN", "wire/protocol",
             f"{name} declares protocol {proto[0]}; this checker implements "
             f"{rg.PROTOCOL_VERSION}",
             fix="ship the new spec to both sides before the next close. A gate "
                 "reading a version it does not implement refuses rather than "
                 "guesses.")
    else:
        note("OK", "wire/protocol", f"protocol {proto[0]}")

    # --- is it a lap at all ----------------------------------------------
    parts = rdg.is_a_lap(text)
    if not parts:
        note("INFO", "wire/identity",
             f"{name} is not a lap under §5a -- ROUND, LAP or FROM is declared "
             f"zero times or more than once. Envelopes and standing statuses "
             f"are legitimately in this class.")
        return
    rnd, lap, frm = int(parts[0]), int(parts[1]), parts[2]
    note("OK", "wire/identity", f"round {rnd} lap {lap} from {frm}")

    # --- required v4 fields ----------------------------------------------
    laps = rg.load_rounds(path.parent, every_lap=True)
    this = next((l for l in laps if l.path == path), None)
    missing = this.missing_wire_header() if this else None
    if missing:
        note("FAIL", "wire/required",
             f"{name} is missing required fields: {', '.join(missing)}",
             fix="add them. Shortening a lap means cutting prose, never cutting "
                 "what a machine reads -- the header is the cheap half and the "
                 "only half either gate can check.")
    else:
        note("OK", "wire/required", "every required field for this round is present")

    # --- verdict ----------------------------------------------------------
    verdicts = rg.VERDICT_RE.findall(text)
    if len(verdicts) != 1:
        note("FAIL", "wire/verdict",
             f"{name} declares HANDSHAKE-VERDICT {len(verdicts)} time(s)",
             fix="declare exactly one at column 0. No verdict fails closed and "
                 "two are ambiguous; neither is agreement.")
    elif verdicts[0] not in ("GO", "HOLD", "OPEN", "WITHDRAWN"):
        note("WARN", "wire/verdict", f"{name} declares an unrecognised verdict "
             f"{verdicts[0]!r}",
             fix="use GO / HOLD / OPEN / WITHDRAWN. An unrecognised verdict is "
                 "not agreement and leaves the round open.")
    else:
        note("OK", "wire/verdict", verdicts[0])

    # --- the digest, which is the one field a human cannot proofread ------
    status, decl, comp, _ = rdg.check_lap(path)
    if status == "undeclared":
        note("INFO", "wire/digest", f"{name} declares no round digest")
    elif status == "match":
        note("OK", "wire/digest", f"{decl[0]} over {decl[1]} re-derives here")
    elif decl[1] != comp[1]:
        # A RECORDS DIFFERENCE, not a failure of either side. OWNERSHIP.md §6:
        # a gate that reports this as a bare rejection is a defective gate --
        # both sides computed correctly from what each holds. So say WHAT WE
        # HOLD, so the other side can compute the difference and send what is
        # missing. A hash says *that* two records differ; only the enumeration
        # says *how*, and without it a mismatch costs a lap to diagnose.
        mine = []
        for other in rdg.candidates():
            q = rdg.is_a_lap(other.read_bytes().decode("utf-8", errors="replace"))
            if q and int(q[0]) == rnd and int(q[1]) < lap:
                mine.append(f"{q[1]}:{q[2]}")
        mine.sort(key=lambda r: (int(r.split(":")[0]), r))
        note("WARN", "wire/digest",
             f"RECORDS DIFFER, not a fault: {name} declares {decl[0]} over "
             f"{decl[1]}; we re-derive {comp[0]} over {comp[1]}",
             fix="RECONCILE, do not re-do work -- neither side is wrong. We hold "
                 f"these {len(mine)} lap(s) below {lap}, as lap:sender pairs: "
                 + ", ".join(mine) +
                 ". Enumerate yours the same way; the set difference names "
                 "exactly what each side must send, and nothing else needs "
                 "deciding. Then declare the enumeration in every lap, per "
                 "OWNERSHIP.md §6's baseline, so the next mismatch costs a diff "
                 "and not a lap.")
    else:
        note("FAIL", "wire/digest",
             f"SAME COUNT, DIFFERENT HASH: {name} declares {decl[0]} over "
             f"{decl[1]}; we re-derive {comp[0]} over the same count",
             fix="this one is NOT a holdings difference -- both sides hold the "
                 "same number of laps and at least one file's bytes differ "
                 "between the records. Compare per-lap hashes to find which. "
                 "The usual cause is a file edited or renumbered after it was "
                 "sent, which moves its hash; a sent lap is immutable on both "
                 "sides precisely so this cannot happen quietly.")

    # --- pins name the right repository, round 14 lap 14 §C ---------------
    for field, regex, should_resolve in (
            ("HANDSHAKE-OUR-PIN", rg.OUR_PIN_RE, frm == "cyanrip-fork"),
            ("HANDSHAKE-PEER-PIN", rg.PEER_PIN_RE, frm != "cyanrip-fork")):
        m = regex.search(text)
        if not m or m.group(1).startswith("<"):
            continue
        sha = m.group(1)
        r = subprocess.run(["git", "-C", str(ROOT), "log", "--format=%s", "-1",
                            sha + "^{commit}"], capture_output=True, text=True)
        resolves = r.returncode == 0
        if resolves and not should_resolve:
            note("FAIL", "wire/pin",
                 f"{name}'s {field} is {sha}, which is a commit in the CYANRIP "
                 f"repository: {r.stdout.strip()!r}",
                 fix="that field names the OTHER project's build. We shipped "
                     "this defect first and you transcribed it back, correctly, "
                     "because the protocol says to transcribe what the peer "
                     "declared -- so the fix is at the source: check that your "
                     "own pin resolves in your repository and the peer's does "
                     "not, before sending.")
        elif not resolves and should_resolve:
            note("WARN", "wire/pin",
                 f"{name}'s {field} is {sha}, which this clone does not have",
                 fix="either it is a commit we have not fetched, or the field "
                     "names the wrong repository. An absent object is weaker "
                     "evidence than a present one -- it only means this clone "
                     "lacks it.")
        else:
            note("OK", "wire/pin", f"{field} {sha} resolves as expected")

    # --- lap number collisions, which round 14 hit three times -------------
    # resolve() on both sides: candidates() yields paths built from its own
    # root, so a `==` against the path the caller typed matched nothing and
    # every file collided with itself. Caught by running it, not by reading it.
    same, me = [], path.resolve()
    for other in rdg.candidates():
        if other.resolve() == me:
            continue
        p = rdg.is_a_lap(other.read_bytes().decode("utf-8", errors="replace"))
        if p and int(p[0]) == rnd and int(p[1]) == lap:
            same.append((other.name, p[2]))
    if same:
        others = ", ".join(f"{n} (from {f})" for n, f in same)
        note("WARN", "wire/lap-number",
             f"round {rnd} lap {lap} is also claimed by {others}",
             fix="both files are sent and neither can be renumbered. §5a's "
                 "digest keys rows on (lap, FROM) and handles this; §2's state "
                 "rule keys on the number alone and has no tiebreak, so a GO "
                 "against a HOLD at one number would be unresolvable. Number "
                 "the next lap past the collision and say so.")
    else:
        note("OK", "wire/lap-number", f"lap {lap} is claimed once")

    # --- THE SHARED FILES BOTH SIDES MUST HOLD IDENTICALLY -----------------
    #
    # `HANDSHAKE-SHARED-HASHES` has been declared in every lap since round 7 and
    # **verified by nothing on either side** until 2026-08-26. Both projects
    # published hashes of the shared spec at each other for eight rounds and
    # neither gate ever compared them with its own copies.
    #
    # It is the enforcement slot for OWNERSHIP.md's §6: if a lap's declared hash
    # differs from the file in this tree, the two sides are working from
    # different rules and NOTHING ELSE IN THE LAP HAS BEEN GRADED -- it was
    # graded against a spec the sender is not following. So this FAILs, and a
    # round cannot close over a failing lap.
    for label, rel in (("protocol(v4)", "docs/handshake/PROTOCOL.md"),
                       ("seam-rules", "docs/seam-rules.md"),
                       ("seam-commands", "docs/seam-commands.md"),
                       ("ownership", "docs/OWNERSHIP.md")):
        declared = re.search(rf"{re.escape(label)}=([0-9a-f]{{64}})", text)
        local = ROOT / rel
        if not local.exists():
            note("WARN", "shared/" + label,
                 f"{rel} is not in this tree, so nothing can be compared",
                 fix=f"add {rel}. A shared file only one side holds is not "
                     f"shared, and its hash cannot be checked by anybody.")
            continue
        ours = hashlib.sha256(local.read_bytes()).hexdigest()
        if not declared:
            note("WARN", "shared/" + label,
                 f"{name} declares no hash for {rel}",
                 fix=f"add `{label}={ours}` to HANDSHAKE-SHARED-HASHES. An "
                     f"undeclared shared file is one nobody can prove you hold "
                     f"the same copy of.")
        elif declared.group(1) != ours:
            note("FAIL", "shared/" + label,
                 f"{name} declares {rel} as {declared.group(1)[:16]}…; this tree "
                 f"holds {ours[:16]}…",
                 fix="RECONCILE THE FILE BEFORE ANYTHING ELSE IN THIS LAP IS "
                     "JUDGED. The two sides are working from different rules, so "
                     "every other finding here was graded against a spec you are "
                     "not following. Diff the two copies, agree one, bump its "
                     "version, ship it both sides, re-send the lap.")
        else:
            note("OK", "shared/" + label, f"{ours[:16]}… matches this tree")

    # --- a declared-none test pin is an answer, not a build ---------------
    if this and this.test_pin_is_declared_none():
        note("OK", "wire/test-pin", "declared `none` -- an answer, not a build")
    elif this and this.test_pin:
        note("INFO", "wire/test-pin",
             f"test pin {this.test_pin} -- not a release and cannot close a round")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lap", nargs="*", help="lap file(s) to check")
    ap.add_argument("--all", action="store_true",
                    help="every lap in the record, ours and theirs")
    args = ap.parse_args()

    paths = [pathlib.Path(p) for p in args.lap]
    if args.all:
        paths = sorted(rdg.candidates())
    if not paths:
        ap.error("give a lap file, or --all")

    for p in paths:
        if not p.exists():
            note("FAIL", "input/missing", f"{p} does not exist")
            continue
        FINDINGS.append(("----", "", f"=== {p} ===", None, None))
        check_lap(p)

    fails = 0
    for level, cat, msg, fix, artifact in FINDINGS:
        if level == "----":
            print(f"\n{msg}")
            continue
        line = f"{level:<5} {cat:<20} {msg}"
        if artifact:
            line += f"  [{artifact}]"
        print(line)
        if fix:
            print(f"{'':<5} {'':<20} FIX: {fix}")
        if level == "FAIL":
            fails += 1

    print(f"\n{len(paths)} lap(s) checked, {fails} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
