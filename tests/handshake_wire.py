#!/usr/bin/env python3
"""Every handshake lap is well-formed enough for the other side's gate.

Not whether a round is closed -- an open round is the normal state and must
never fail a build. Only whether the files we SEND carry the fields the shared
protocol requires, because that is the failure that already happened: round-8
laps 1 and 3 went to Platterpus missing three required headers, and this
repository's whole suite was green at the time.

The requirement is PROTOCOL.md C9: a round >= 8 file missing any of FROM /
APP-VERSION / RIPPER-VERSION / PIN must be refused by the receiving gate,
naming the field. So a file like that is not a lap; it is a bounced message we
have not noticed bouncing.

It imports release-gate.py's own loader rather than re-parsing the headers.
Two readers of one record that can disagree is the defect both gates exist to
prevent, and a second copy of the parsing rules is how they come to disagree.
"""

import importlib.util
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

spec = importlib.util.spec_from_file_location("relgate", root / "tools" / "release-gate.py")
relgate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(relgate)

# Files that went out malformed and CANNOT be corrected, because the
# correspondence is append-only and editing a sent lap falsifies the record.
# They are named individually rather than waved through by round number, so
# adding to this set is a visible act -- and every addition is an admission
# that another malformed file reached the other side.
#
# Both of these are round-8 laps sent on 2026-08-10 missing three required v2
# headers. `round-08-lap-05.md` withdraws that round and says so on the record.
SENT_MALFORMED = {
    "round-08-lap-01.md",
    "round-08-lap-03.md",
}

fails = 0
laps = relgate.load_rounds(root / "docs" / "handshake", every_lap=True)

# The declared protocol version must never go BACKWARDS.
#
# Round 8 lap 1 declared `HANDSHAKE-PROTOCOL: 1` when every round-7 lap had
# declared 2, and it propagated through eight laps before anyone noticed --
# found 2026-08-15 while reading Platterpus's own laps, all of which declare 2.
# Nothing caught it: the gate accepts anything <= the version it implements, so
# under-declaring is silently valid, and PROTOCOL.md's own example says 2.
#
# It matters because the version selects which rules the RECEIVING gate
# applies. Declaring an older protocol than the spec both sides implement asks
# the peer to grade our file by rules we are not following, and the failure is
# invisible from the sending side by construction -- exactly what the
# HANDSHAKE-INBOUND-HELD: proposal exists to surface.
# All eight round-8 laps carry the regression and all eight were SENT, so they
# cannot be corrected -- editing a sent lap falsifies the record. Named
# individually rather than waved through by round number, so adding to this set
# stays a visible act and each entry is an admission that another under-declared
# file reached the other side. Lap 17 declares 2 and is deliberately absent.
SENT_UNDER_DECLARED = {
    "round-08-lap-01.md", "round-08-lap-03.md", "round-08-lap-05.md",
    "round-08-lap-07.md", "round-08-lap-09.md", "round-08-lap-11.md",
    "round-08-lap-13.md", "round-08-lap-15.md",
}

prev_max = 0
for lap in sorted(laps, key=lambda l: (l.number or 0, l.lap or 0)):
    if lap.protocol is None:
        continue
    if int(lap.protocol) < prev_max:
        if lap.path.name in SENT_UNDER_DECLARED:
            print(f"known-bad (sent, cannot be edited): {lap.path.name} -- "
                  f"declares HANDSHAKE-PROTOCOL: {lap.protocol}, "
                  f"{prev_max} was already declared")
        else:
            print(f"FAIL: {lap.path.name} declares HANDSHAKE-PROTOCOL: "
                  f"{lap.protocol} after an earlier lap declared {prev_max} -- "
                  "the declared protocol must never go backwards")
            fails += 1
    prev_max = max(prev_max, int(lap.protocol))
if not laps:
    print("FAIL: no handshake laps found at all -- an empty record is not a pass")
    sys.exit(1)

for lap in sorted(laps, key=lambda l: (l.number or 0, l.lap or 0)):
    missing = lap.missing_wire_header()
    if not missing:
        continue
    if lap.path.name in SENT_MALFORMED:
        print(f"known-bad (sent, cannot be edited): {lap.path.name} "
              f"-- missing {', '.join(missing)}")
        continue
    print(f"FAIL: {lap.path.name} is missing {', '.join(missing)} -- "
          "PROTOCOL.md C9 tells the receiving gate to refuse this file")
    fails += 1

# --- the envelope's artifact-provenance refusal ---------------------------
#
# make-envelope.py had no test at all until round 13, and it shipped the defect
# that proves it needed one: lap 1 went out with five artifacts whose banners
# said `platterpus-fork-g673a57b` inside a lap that named `g9f8592e` and
# `g6fbc41d` and never mentioned 673a57b. Platterpus found it by checking
# provenance where it is derivable -- the artifact's own content -- rather than
# from the covering message.
#
# Driven as a subprocess against files built here, so it exercises the real
# tool and not a reimplementation of its rule. Both refusals must fire and the
# clean case must still be accepted; a check that only proves the refusals
# would pass with the tool refusing everything.
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "make-envelope.py"

LAP_STUB = """HANDSHAKE-PROTOCOL: 4
HANDSHAKE-ROUND: 99
HANDSHAKE-LAP: 1
HANDSHAKE-FROM: cyanrip-fork

Body naming build platterpus-fork-g%s and nothing else.
"""


def _envelope(tmp, lap_sha, artifact_shas):
    lap = tmp / "round-99-lap-01.md"
    lap.write_text(LAP_STUB % lap_sha, encoding="utf-8")
    parts = []
    for i, sha in enumerate(artifact_shas):
        a = tmp / f"artifact{i}.log"
        a.write_text(f"cyanrip 0.0.0 (platterpus-fork-g{sha})\nbody\n",
                     encoding="utf-8")
        parts.append(str(a))
    r = subprocess.run(
        [sys.executable, str(TOOL), str(tmp / "out.md"), "--lap", str(lap)]
        + parts, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)


with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)

    # 1. The exact round-13 mistake: artifacts agree with each other and the
    #    lap names a different build.
    rc, out = _envelope(tmp, "9f8592e", ["673a57b", "673a57b"])
    if rc == 0:
        print("FAIL: make-envelope.py accepted a bundle whose artifacts all "
              "assert a build the lap never names -- this is round 13 lap 1's "
              "own defect and it must not be emittable")
        fails += 1
    elif "never names it" not in out:
        print(f"FAIL: make-envelope.py refused for the wrong reason: {out!r}")
        fails += 1

    # 2. A mixed bundle -- one artifact regenerated, one not.
    rc, out = _envelope(tmp, "673a57b", ["673a57b", "24de9b4"])
    if rc == 0:
        print("FAIL: make-envelope.py accepted a bundle whose artifacts "
              "assert two different builds")
        fails += 1
    elif "different builds" not in out:
        print(f"FAIL: mixed bundle refused for the wrong reason: {out!r}")
        fails += 1

    # 3. And it must still emit the correct case, or the two above prove only
    #    that the tool refuses everything.
    rc, out = _envelope(tmp, "673a57b", ["673a57b", "673a57b"])
    if rc != 0:
        print(f"FAIL: make-envelope.py refused a correct bundle: {out!r}")
        fails += 1

# ---------------------------------------------------------------------------
# A pin field must name the repository it claims to.
#
# THE DEFECT, and we shipped it first. `HANDSHAKE-OUR-PIN` and
# `HANDSHAKE-PEER-PIN` exist so a closed round records WHICH TWO PROGRAMS
# agreed (PROTOCOL.md line 361). Ours declared `HANDSHAKE-PEER-PIN: ddf7ac3` --
# a CYANRIP commit, our own `0.9.4-rc1+platterpus.5` -- as Platterpus's pin, in
# round-11 lap 3, round-12 lap 3 and round-13 laps 3, 6 and 8. Two of those are
# the laps that CLOSED rounds 11 and 13. The same shape appears in round 7 with
# `9048082` and `104f6d4`.
#
# It then propagated: Platterpus transcribed it back as their own
# `HANDSHAKE-OUR-PIN`, correctly following the protocol's instruction to
# transcribe what the peer declared, and it has stood in nine of their laps
# from round-13 lap 2 to round-14 lap 13 while their APP-VERSION prose named a
# real Platterpus SHA (`0.6.23 (722e24f)`) a few lines above it.
#
# NEITHER GATE COULD CATCH IT, because neither side can resolve the other's
# SHAs -- which is exactly why the check has to be local and about our own
# half: each side can verify that its OWN pin resolves here and that the PEER's
# does not. Cheap, offline, and it would have fired on the first occurrence.
#
# WHAT THIS CANNOT DO, said rather than implied: a 7-hex prefix could collide
# across two repositories, so a "resolves here" is evidence and not proof. The
# subject line is printed so a human can tell a collision from a mistake. And
# an absent object is not proof either -- it only means this clone does not
# have it.


def _resolves_here(sha):
    """The commit subject if this repository has it, else None."""
    r = subprocess.run(["git", "-C", str(root), "log", "--format=%s", "-1",
                        sha + "^{commit}"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


# Sent and therefore uncorrectable, exactly like SENT_MALFORMED above. Named
# individually so that adding one is a visible act, and each is an admission
# that a lap went out naming the wrong repository's commit.
SENT_WRONG_PEER_PIN = {
    "round-07-lap-30.md", "round-07-lap-32.md", "round-07-lap-33.md",
    "round-07-lap-36.md", "round-07-lap-38.md", "round-07-lap-39.md",
    "round-11-lap-03.md", "round-12-lap-03.md", "round-13-lap-03.md",
    "round-13-lap-06.md", "round-13-lap-08.md",
}

_git_ok = subprocess.run(["git", "-C", str(root), "rev-parse", "--git-dir"],
                         capture_output=True, text=True).returncode == 0
if not _git_ok:
    print("pin-repository check SKIPPED: not a git checkout "
          "(this is a gap, not a pass)")
else:
    # The checker must be able to tell the two cases apart, or every assertion
    # below passes for the wrong reason. `ddf7ac3` is ours; `722e24f` is the
    # Platterpus SHA their own round-13 laps print in APP-VERSION.
    if _resolves_here("ddf7ac3") is None:
        print("FAIL: the pin resolver cannot find a commit known to be ours "
              "-- every check below would pass vacuously")
        fails += 1
    if _resolves_here("722e24f") is not None:
        print("FAIL: the pin resolver claims a Platterpus SHA is ours")
        fails += 1

    for lap in laps:
        text = lap.path.read_text(encoding="utf-8")
        ours = relgate.OUR_PIN_RE.search(text)
        theirs = relgate.PEER_PIN_RE.search(text)

        if ours and not ours.group(1).startswith("<"):
            if _resolves_here(ours.group(1)) is None:
                print(f"FAIL: {lap.path.name} declares HANDSHAKE-OUR-PIN "
                      f"{ours.group(1)}, which is not a commit in this "
                      f"repository")
                fails += 1

        if theirs and not theirs.group(1).startswith("<"):
            subject = _resolves_here(theirs.group(1))
            if subject is not None:
                msg = (f"{lap.path.name} declares HANDSHAKE-PEER-PIN "
                       f"{theirs.group(1)}, which is a commit in THIS "
                       f"repository: {subject!r}")
                if lap.path.name in SENT_WRONG_PEER_PIN:
                    print(f"known-bad (sent, cannot be edited): {msg}")
                else:
                    print(f"FAIL: {msg}")
                    fails += 1

print(f"{len(laps)} lap(s) checked, {fails} malformed")
sys.exit(1 if fails else 0)
