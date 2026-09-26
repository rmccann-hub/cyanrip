#!/usr/bin/env python3
"""tools/lap-statements.py must refuse every malformed statement it claims to.

The checker is the whole of LSL's value: a statement language nothing enforces
is prose with a stricter look. So each refusal in the spec's list gets a lap
built to trigger exactly it, and each assertion names the MESSAGE as well as
the exit code -- a lap refused for some other reason would otherwise pass a
test written for this one. The well-formed lap is checked too, and so is every
committed lap that declares `LSL: 1`, so a lap of ours cannot be sent
malformed.

References resolve against this repository's real history (`ee0221c`, and the
laps we hold), because a checker tested only against fixtures it invented can
agree with itself. Temporary files are removed when the test ends.
"""

import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "lap-statements.py"

failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


HEAD = """HANDSHAKE-PROTOCOL: 5
HANDSHAKE-ROUND: 27
HANDSHAKE-LAP: 9
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-VERDICT: {verdict}

# a title

LSL: 1

"""

# Every kind, well formed, with references that resolve in our tree.
GOOD = """S1 FACT read: The banner is written as soon as the log opens.
  evidence: cyanrip@ee0221c:src/cyanrip_log.c:1-20
S2 FACT measured: The pooled sweep reports no violations.
  evidence: run: python3 tools/blackbox.py --gate => no invariant violations
S3 FACT reproduced: Their lap 2 section B answers our lap 1.
  re: platterpus:R27.L2.§B
  evidence: cyanrip@ee0221c:docs/handshake/inbound/round-27-lap-02.md:111
S4 NONE: No round-27 lap of theirs is newer than lap 3 in our tree.
  scope: docs/handshake/inbound/round-27-lap-*.md at ee0221c
  evidence: run: git ls-tree ee0221c docs/handshake/inbound/ => laps 2 and 3
S5 UNKNOWN: Whether the drive caches reads beyond 140 sectors.
  reason: our probe's figure is known to be wrong
S6 DID: The early-log banner fix.
  commit: ee0221c
S7 WILL: Cut the next release.
  owner: us
  when: once this round is closed on both gates
S8 ACCEPT: Their wording for the summary line.
  re: platterpus:R27.L2.§D
S9 AMEND: The per-track line.
  re: cyanrip:R27.L9.S8
  to: a shorter tail
S10 ASK: Does your gate read round 27 closed?
  target: NEXT-ROUND
S11 NOTE: Anything a human needs that is not a claim.
S12 VERDICT: {verdict}
  basis: S1, S2, S6
"""


def run(body, *extra, verdict="GO", head=None):
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "lap.md"
        p.write_text((head or HEAD).format(verdict=verdict)
                     + body.replace("{verdict}", verdict))
        r = subprocess.run([sys.executable, str(TOOL), str(p), *extra],
                           capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout + r.stderr


def expect(name, body, code, needle, **kw):
    got, out = run(body, **kw)
    if got != code:
        fail(f"{name}: exit {got}, expected {code}\n{out}")
    elif needle and needle not in out:
        fail(f"{name}: exit {code} as expected, but not for the reason "
             f"tested -- {needle!r} is not in:\n{out}")
    else:
        print(f"ok   {name}")


def swap(old, new):
    assert GOOD.count(old) == 1, old
    return GOOD.replace(old, new)


# 0. The well-formed lap, and it is well formed for a reason: it carries a
#    peer reference, so without --peer it must warn rather than pass silently.
got, out = run(GOOD)
if got != 0 or "well formed" not in out:
    fail(f"the well-formed lap: exit {got}\n{out}")
else:
    print("ok   the well-formed lap")

# 1. kind and grade
expect("unknown kind", swap("S11 NOTE:", "S11 MAYBE:"), 1, "MAYBE is not a kind")
expect("FACT with no grade", swap("S1 FACT read:", "S1 FACT:"), 1,
       "a FACT takes one grade")
expect("FACT with a made-up grade", swap("S1 FACT read:", "S1 FACT likely:"),
       1, "a FACT takes one grade")
expect("a grade on a kind that takes none", swap("S6 DID:", "S6 DID read:"), 1,
       "a DID takes no grade")

# 2. required fields
expect("FACT read with no evidence",
       swap("  evidence: cyanrip@ee0221c:src/cyanrip_log.c:1-20\n", ""), 1,
       "S1 FACT read: needs a evidence: field")
expect("NONE with no scope",
       swap("  scope: docs/handshake/inbound/round-27-lap-*.md at ee0221c\n",
            ""), 1, "S4 NONE: needs a scope: field")
expect("UNKNOWN with no reason",
       swap("  reason: our probe's figure is known to be wrong\n", ""), 1,
       "S5 UNKNOWN: needs a reason: field")
expect("an unknown field", swap("  to: a shorter tail", "  gist: a shorter tail"),
       1, "gist: is not a field")

# 3. numbering
expect("a gap", swap("S5 UNKNOWN:", "S15 UNKNOWN:"), 1,
       "S15 where S5 was expected")
expect("a repeat", swap("S5 UNKNOWN:", "S4 UNKNOWN:"), 1, "S4 is numbered twice")

# 4. references
expect("a branch name is not a reference",
       swap("cyanrip@ee0221c:src/cyanrip_log.c:1-20",
            "cyanrip@platterpus-fork:src/cyanrip_log.c"), 1,
       "is neither 'run: CMD => RESULT' nor side@commit:path")
expect("a commit that does not exist",
       swap("cyanrip@ee0221c:src/cyanrip_log.c:1-20",
            "cyanrip@0000000:src/cyanrip_log.c"), 1,
       "commit 0000000 does not resolve")
expect("a path that does not exist at the commit",
       swap("cyanrip@ee0221c:src/cyanrip_log.c:1-20",
            "cyanrip@ee0221c:src/no_such_file.c"), 1,
       "src/no_such_file.c does not exist at cyanrip@ee0221c")
expect("a line past the end of the file",
       swap("cyanrip@ee0221c:src/cyanrip_log.c:1-20",
            "cyanrip@ee0221c:src/cyanrip_log.c:99999"), 1,
       "line 99999 does not exist")
expect("a run: with no result",
       swap(" => no invariant violations", ""), 1,
       "names its command AND its result")
expect("a lap we do not hold",
       swap("re: platterpus:R27.L2.§D", "re: platterpus:R27.L7.§D"), 1,
       "we do not hold platterpus's round 27 lap 7")
expect("a statement number in a prose lap",
       swap("re: platterpus:R27.L2.§D", "re: platterpus:R27.L2.S4"), 1,
       "is a prose lap and has no statement numbers")
expect("a statement of this lap that does not exist",
       swap("re: cyanrip:R27.L9.S8", "re: cyanrip:R27.L9.S80"), 1,
       "no such statement in this lap")
expect("a DID naming a commit that does not exist",
       swap("  commit: ee0221c", "  commit: 1234567"), 1,
       "commit 1234567 does not resolve in our tree")
got, out = run(GOOD)
if "UNCHECKED" in out or "platterpus@" in GOOD:
    fail("fixture drift: GOOD should carry no platterpus@ artifact")
got, out = run(swap("  evidence: cyanrip@ee0221c:docs/handshake/inbound/round-27-lap-02.md:111",
                    "  evidence: platterpus@183073b:docs/handshake/outbound/round-27-lap-02.md:1"))
if got != 0 or "UNCHECKED platterpus@183073b" not in out:
    fail(f"a peer artifact with no --peer must be UNCHECKED, not passed "
         f"or refused: exit {got}\n{out}")
else:
    print("ok   a peer artifact with no --peer is UNCHECKED")

# 5. the verdict
expect("no VERDICT", swap("S12 VERDICT: {verdict}\n  basis: S1, S2, S6\n", ""),
       1, "0 VERDICT statements")
expect("two VERDICTs", GOOD + "S13 VERDICT: GO\n  basis: S1\n", 1,
       "2 VERDICT statements")
got, out = run(GOOD.replace("S12 VERDICT: {verdict}", "S12 VERDICT: HOLD"))
if got != 1 or "says HOLD and HANDSHAKE-VERDICT says ['GO']" not in out:
    fail(f"a VERDICT disagreeing with the header: exit {got}\n{out}")
else:
    print("ok   a VERDICT disagreeing with the header")
expect("a verdict that is not a verdict",
       GOOD.replace("S12 VERDICT: {verdict}", "S12 VERDICT: YES"), 1,
       "the verdict is GO, HOLD or OPEN")
expect("basis naming a NOTE", swap("  basis: S1, S2, S6", "  basis: S1, S11"),
       1, "basis: S11 is a NOTE")
expect("basis naming an ASK", swap("  basis: S1, S2, S6", "  basis: S10"),
       1, "basis: S10 is a ASK")
expect("basis naming nothing", swap("  basis: S1, S2, S6", "  basis: S1, S40"),
       1, "basis: S40 does not exist")

# 6. questions and commitments
expect("a BLOCKING question with no breaks",
       swap("  target: NEXT-ROUND", "  target: BLOCKING"), 1,
       "names what it breaks in the pin")
expect("a target that is neither", swap("  target: NEXT-ROUND", "  target: SOON"),
       1, "target: is BLOCKING or NEXT-ROUND")
expect("a WILL with a date",
       swap("  when: once this round is closed on both gates",
            "  when: by 2026-10-01"), 1, "when: is a condition, never a date")
expect("a WILL with an unknown owner", swap("  owner: us", "  owner: someone"),
       1, "owner: is us, them or operator")

# 7. relays warn, prose is refused, and a prose lap cannot be checked at all
got, out = run(GOOD + "S13 FACT relayed: The operator said it is released.\n"
                      "  source: a chat message\n")
if got != 0 or "a relay is in neither repository" not in out:
    fail(f"a relay must warn and not refuse: exit {got}\n{out}")
else:
    print("ok   a relay warns")
expect("a line of prose between statements",
       swap("S11 NOTE:", "Some prose that is not a statement.\n\nS11 NOTE:"), 1,
       "not a statement, a field, a continuation or a heading")
expect("a field after a blank line",
       swap("  owner: us\n", "\n  owner: us\n"), 1,
       "not a statement, a field, a continuation or a heading")
got, out = run("", head=HEAD.replace("LSL: 1\n", ""))
if got != 2 or "not an LSL lap" not in out:
    fail(f"a prose lap must be CANNOT CHECK, exit 2: exit {got}\n{out}")
else:
    print("ok   a prose lap cannot be checked")
got, out = run(GOOD, head=HEAD.replace("LSL: 1", "LSL: 2"))
if got != 2 or "implements LSL 1 only" not in out:
    fail(f"an unimplemented LSL version must exit 2: exit {got}\n{out}")
else:
    print("ok   an unimplemented LSL version cannot be checked")

# 8. every committed LSL lap of ours is well formed
laps = [p for p in sorted((ROOT / "docs" / "handshake").glob("round-*.md"))
        if re.search(r"^LSL: 1\s*$", p.read_text(encoding="utf-8"), re.M)]
for p in laps:
    r = subprocess.run([sys.executable, str(TOOL), str(p)],
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        fail(f"{p.name} is not a well-formed LSL lap:\n{r.stdout}")
    else:
        print(f"ok   {p.name} is well formed")
print(f"({len(laps)} committed LSL lap(s))")

if failures:
    print(f"\n{failures} failure(s)")
    sys.exit(1)
print("\nall checks passed")
