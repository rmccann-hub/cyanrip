#!/usr/bin/env python3
"""§C's commit count must name a range, and the range must be re-derivable.

ROUND 16 LAP 10 §D. Our lap 9 §C said "three commits since lap 8" and listed
them in prose. Platterpus derived it from our repository and got FIVE from the
send pin, NINE from lap 8's HANDSHAKE-FROM-COMMIT. Two commits were missing,
and one of them -- 7ace6e5 -- corrected the Run A block: the procedure for the
single artifact the round is waiting on. A reader of lap 9 alone would not have
known it moved.

THE DEFECT IS THE MISSING RANGE. "Three commits since lap 8" is unfalsifiable
in the same way "EAC reports N" is; there is nothing to check it against, which
is why they had to guess two baselines and report both.

The sharpest assertion available is the cross-check: this tool must reproduce
BOTH numbers a SECOND, INDEPENDENT implementation derived from our own history
and published in their lap 10 §D. Not a comparison with ourselves.
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "lap-commits.py"

# Round 16 lap 10 §D, verbatim: "`343ebd1..59cb5a9` is **nine** commits and
# `8880d8f..59cb5a9` -- measuring from *"Pin lap 8 as sent"* -- is **five**".
PEER = [("343ebd1", 9), ("8880d8f", 5)]

failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


def have(ref):
    return subprocess.run(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
                          cwd=ROOT, capture_output=True).returncode == 0


def run(*args):
    r = subprocess.run([sys.executable, str(TOOL), *args], cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=180)
    return r.returncode, r.stdout.decode(errors="replace")


def count(out):
    m = re.search(r"\*\*(\d+) commit\(s\)\*\*", out)
    return int(m[1]) if m else None


def main():
    # A CHECK THAT CANNOT RUN SAYS SO, rather than passing on an absence.
    if not all(have(r) for r, _ in PEER) or not have("59cb5a9"):
        print("UNPROBED: this history is not present (shallow clone). The "
              "cross-check against\nPlatterpus's derivation needs the commits "
              "their lap 10 §D named.")
        return 0

    # 1. THE CROSS-CHECK. Both numbers a second implementation derived.
    for base, want in PEER:
        rc, out = run("--since", base, "--head", "59cb5a9")
        got = count(out)
        if rc or got != want:
            fail(f"{base}..59cb5a9 derived {got}, their lap 10 §D derived "
                 f"{want} from our own history\n{out}")

    # 2. Every count names the range it counted over. Without this the tool
    #    reproduces lap 9's defect with better arithmetic.
    rc, out = run("--since", "8880d8f", "--head", "59cb5a9")
    for token in ("`8880d8f`", "`59cb5a9`", "§C baseline"):
        if token not in out:
            fail(f"the summary line omits {token} -- a count with no range is "
                 f"the defect\n{out}")

    # 3. The baseline is DERIVED from the previous lap's wire field, not from
    #    a filename and not from the send pin. Lap 9's baseline must be lap 8's
    #    HANDSHAKE-FROM-COMMIT, 343ebd1, and the send pin must be labelled as
    #    something the other side cannot resolve.
    rc, out = run("16", "9", "--head", "59cb5a9")
    if "343ebd1" not in out or "HANDSHAKE-FROM-COMMIT" not in out:
        fail(f"lap 9's baseline is not lap 8's HANDSHAKE-FROM-COMMIT\n{out}")
    if count(out) != 9:
        fail(f"derived baseline gave {count(out)}, not 9\n{out}")
    if "8880d8f" not in out or "cannot resolve" not in out:
        fail(f"the send pin is absent or not marked unresolvable by them\n{out}")

    # 4. --check REFUSES A LAP THAT PASTES NO RANGE, and lap 9 is the case.
    #    A tool whose check mode passes anything would have caught nothing.
    lap9 = ROOT / "docs" / "handshake" / "round-16-lap-09.md"
    if lap9.exists():
        rc, out = run("16", "9", "--head", "59cb5a9", "--check", str(lap9))
        if rc == 0:
            fail("--check PASSED lap 9, the lap this test exists for")
        if "cannot be re-derived" not in out:
            fail(f"--check's refusal does not say why\n{out}")

    # 5. --check ACCEPTS a file carrying the line, or (4) is satisfied by a
    #    check mode that always fails.
    rc, out = run("--since", "8880d8f", "--head", "59cb5a9")
    line = [l for l in out.splitlines() if l.startswith("§C baseline")][0]
    tmp = ROOT / "tests" / ".lap_commits_probe.md"
    try:
        tmp.write_text(f"## C\n\n{line}\n")
        rc, out = run("--since", "8880d8f", "--head", "59cb5a9",
                      "--check", str(tmp))
        if rc != 0:
            fail(f"--check rejected a file that pastes the derived line\n{out}")
    finally:
        tmp.unlink(missing_ok=True)

    # 6. docs/handshake/round-*.md counts as touching the binary. Since r3 the
    #    handshake state is COMPILED IN, so a lap file moves the `Handshake:`
    #    line. A pin chosen with `git log -- src/ meson.build` is wrong, and
    #    one was. Lap 8's own file commit is the case.
    rc, out = run("--since", "343ebd1", "--head", "59cb5a9")
    lap8 = [l for l in out.splitlines() if "Round 16 lap 8" in l]
    if not lap8:
        fail(f"lap 8's own commit is absent from its successor's range\n{out}")
    elif "[binary]" not in lap8[0]:
        fail(f"a lap file is not marked as touching the binary: {lap8[0]}\n"
             f"docs/handshake/round-*.md is compiled in by "
             f"gen-handshake-state.py")

    # 7. It reports the log-site evidence and does NOT grade it. §D is where
    #    "did the text move" is answered; a tool that answered it would be
    #    making the judgement the lap owes.
    tool = TOOL.read_text()
    if "cyanrip_log(" not in tool:
        fail("the tool does not look for log call sites at all")
    if "YOURS TO" not in tool.upper():
        fail("the tool does not say that reading the log sites is the lap's "
             "job -- reporting evidence and issuing a verdict are different "
             "claims")

    print(f"{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
