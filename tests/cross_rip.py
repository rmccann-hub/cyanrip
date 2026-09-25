#!/usr/bin/env python3
"""tools/cross-rip.py must find the wrong reads our own record already holds.

ROUND 26 LAP 5 §B3 IS WHY. Platterpus found `after-cancel.log` reading track 1
as `0E91CD1A` while five other rips of it read `B0D122E7`, and our reading had
missed it. We then found the same wrong read in a bundle filed thirteen days
earlier. Both are filed and immutable, so they are the ground truth: a reader
that does not name exactly those two logs has not done its one job.

The synthetic cases pin the other directions, which no real bundle supplies on
demand: two identical reads must agree, a different read offset must not be
compared at all, and a consumer's EAC-format export must not be read as a log.
Temporary files are removed when the test ends.
"""

import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "cross-rip.py"
R0924 = ROOT / "docs" / "rig-2026-09-24-df91ae7" / "rips"
R0911 = ROOT / "docs" / "rig-2026-09-11-ddc1e8c" / "rips"
failures = 0


def check(cond, msg):
    global failures
    if not cond:
        failures += 1
        print(f"FAIL: {msg}")


def run(*paths):
    r = subprocess.run([sys.executable, str(TOOL), *map(str, paths)],
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


def crc_line(out, crc):
    m = re.search(rf"^\s+{crc}\s+x(\d+)\s+\[.*?\]\s+(.*)$", out, re.M)
    return (int(m.group(1)), m.group(2)) if m else (None, "")


# --- the two wrong reads already in our record --------------------------------
ec, out = run(R0924)
check(ec == 1, f"2026-09-24 bundle: exit {ec}, want 1 (a disagreement)")
check(re.search(r"^  track 1: 6 read\(s\), 2 distinct EAC CRC32  DISAGREE$", out, re.M),
      "2026-09-24 bundle: track 1 is not reported as 6 reads in disagreement")
n, names = crc_line(out, "0E91CD1A")
check(n == 1 and names == "after-cancel.log",
      f"2026-09-24 bundle: the wrong read is not attributed to after-cancel.log "
      f"alone (got x{n} {names!r})")
n, _ = crc_line(out, "B0D122E7")
check(n == 5, f"2026-09-24 bundle: {n} reads of B0D122E7, want 5")
check(len(re.findall(r"DISAGREE$", out, re.M)) == 1,
      "2026-09-24 bundle: more than track 1 disagrees")

ec, out = run(R0911)
check(ec == 1, f"2026-09-11 bundle: exit {ec}, want 1")
n, names = crc_line(out, "0E91CD1A")
check(n == 1 and names == "derived-wavpack.log",
      f"2026-09-11 bundle: the wrong read is not attributed to "
      f"derived-wavpack.log alone (got x{n} {names!r})")

# --- the directions no real bundle supplies on demand -------------------------
src = (R0924 / "derived-wav.log").read_text(encoding="utf-8")
check("EAC CRC32:     B0D122E7" in src, "fixture drift: derived-wav.log changed")

with tempfile.TemporaryDirectory() as t:
    d = pathlib.Path(t)
    (d / "a.log").write_text(src, encoding="utf-8")
    (d / "b.log").write_text(src, encoding="utf-8")
    ec, out = run(d)
    check(ec == 0, f"two identical reads: exit {ec}, want 0\n{out}")

    (d / "b.log").write_text(src.replace("B0D122E7", "0E91CD1A"), encoding="utf-8")
    ec, out = run(d)
    check(ec == 1, f"one changed checksum: exit {ec}, want 1 -- the tool cannot fail")

    shifted = src.replace("B0D122E7", "0E91CD1A").replace(
        "Offset:         +667 samples", "Offset:         +6 samples")
    check(shifted != src.replace("B0D122E7", "0E91CD1A"),
          "fixture drift: the Offset: line was not found to change")
    (d / "b.log").write_text(shifted, encoding="utf-8")
    ec, out = run(d)
    check(ec == 0, f"a different offset was compared as the same read: exit {ec}\n{out}")
    check(out.count("disc ") == 2, "a different offset did not form its own group")

with tempfile.TemporaryDirectory() as t:
    d = pathlib.Path(t)
    (d / "x.eac.log").write_bytes((R0924 / "after-cancel.eac.log").read_bytes())
    ec, out = run(d)
    check(ec == 2, f"an EAC-format export alone: exit {ec}, want 2 (nothing read)")
    # The exit code alone cannot tell the detector from a name filter: an
    # export has no cyanrip track block, so it yields no reads either way. The
    # count of logs FOUND is what differs, and it must be zero.
    check("0 cyanrip log(s) found" in out,
          f"an EAC-format export was taken for a cyanrip log: {out.strip()!r}")
    ec, out = run(d / "nothing-here")
    check(ec == 2, f"no files at all: exit {ec}, want 2")

if failures:
    print(f"{failures} check(s) failed", file=sys.stderr)
    sys.exit(1)
print("cross-rip reader: all checks passed")
