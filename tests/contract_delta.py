#!/usr/bin/env python3
"""The contract delta must name the section from the document, not from a guess.

ROUND 16 LAP 7 §H1. Our lap 6 told the consumer the contract's one added row
was in P5. It is in P3. The generator was right and the diff was right; the
LABEL was written by inferring "a message inventory row is a P5 row" from a
diff hunk, and nothing checked it against the document.

P3 and P5 are not neighbours, they are opposites: a P5 row is a fatal string a
consumer must surface, and a P3 row is unstable wording whose absence from a
logfile proves nothing about whether it fired. So the mislabel is not cosmetic
and the test asserts the specific one, not merely that the tool runs.
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "contract-delta.py"
OLD, NEW = "a9aedf0", "0cd611a"

failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


def have(ref):
    return subprocess.run(["git", "cat-file", "-e", f"{ref}:PROVIDER-CONTRACT.md"],
                          cwd=ROOT, capture_output=True).returncode == 0


def run(*args):
    r = subprocess.run([sys.executable, str(TOOL), *args], cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=120)
    return r.returncode, r.stdout.decode(errors="replace")


def main():
    # A CHECK THAT CANNOT RUN SAYS SO. A shallow clone has no history to
    # compare, and silently passing there would make this decoration.
    if not (have(OLD) and have(NEW)):
        print(f"UNPROBED: {OLD} or {NEW} is not in this clone -- the delta "
              f"cannot be computed and nothing here is asserted")
        return 0

    rc, out = run(OLD, NEW, "--rows")
    if rc != 0:
        fail(f"exit {rc}\n{out}")
        return 1

    # 1. Exactly one section changed, and it is P3.
    if "1 section(s) changed: ## P3" not in out:
        fail(f"expected exactly one changed section, P3\n{out}")

    # 2. THE REGRESSION ITSELF: P5 must be reported identical for this pair.
    #    This is the sentence our lap 6 got wrong, asserted directly.
    if "identical  ## P5 - Fatal and error message inventory" not in out:
        fail(f"P5 is not reported identical -- lap 6's mislabel would still "
             f"be reachable\n{out}")

    # 3. The added row must be attributed to P3, not merely listed.
    if "+ ## P3" not in out or "-j given %i times" not in out:
        fail(f"the added row is not attributed to a section\n{out}")

    # 4. Section names come from the document. A hardcoded list would go stale
    #    the moment a section is added, which is the failure one level up from
    #    the one this file exists for.
    tool = TOOL.read_text()
    for hardcoded in ('"P1"', "'P1'", '"P5"', "'P5'"):
        if hardcoded in tool:
            fail(f"{hardcoded} appears literally in the tool -- section names "
                 f"must be read from the document's own headings")

    # 5. Comparing a ref to itself must report nothing changed, or every
    #    result above is satisfiable by a tool that always says "DIFFERS".
    rc2, out2 = run(NEW, NEW)
    if "No section changed" not in out2:
        fail(f"comparing {NEW} to itself did not report an empty delta\n{out2}")

    print(f"{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
