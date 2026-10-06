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

# --- the repeat loop's own reads, and a single read ---------------------------
# 2026-10-04: track 12 of that day's disc read six different ways -- once in the
# first pass, five times in a `-Z` pass at the repeat limit -- and this tool said
# `1 read(s), 1 distinct EAC CRC32  agree`. From `.19` each `Repeating ripping`
# line names the EAC CRC32 of a whole-track read, so it is a read; before `.19`
# it named the value before the final XOR and is not comparable; and one read
# agrees with nothing.
R0930 = ROOT / "docs" / "rig-2026-09-30b-174a134" / "rips"
loop = (R0930 / "secure-reread.log").read_text(encoding="utf-8")
first = "Repeating ripping (0 out of 2 matches for current checksum B0D122E7)"
check(loop.count(first) == 1 and loop.startswith(
      "cyanrip 0.9.4-rc2+platterpus.19 (platterpus-fork-g174a134)"),
      "fixture drift: secure-reread.log of 2026-09-30b changed")
with tempfile.TemporaryDirectory() as t:
    d = pathlib.Path(t)
    (d / "n.log").write_text(loop, encoding="utf-8")
    ec, out = run(d)
    check(re.search(r"^  track 1: 3 read\(s\), 1 distinct EAC CRC32  agree$", out, re.M),
          f"a converged loop of 3 passes is 3 agreeing reads:\n{out}")
    (d / "n.log").write_text(loop.replace(first, first.replace("B0D122E7", "0E91CD1A")),
                             encoding="utf-8")
    ec, out = run(d)
    check(ec == 1 and re.search(r"^  track 1: 3 read\(s\), 2 distinct EAC CRC32  DISAGREE$",
                                out, re.M),
          f"a loop pass that read differently is a disagreement: exit {ec}\n{out}")
    old = loop.replace(first, first.replace("B0D122E7", "0E91CD1A")).replace(
        "+platterpus.19 (", "+platterpus.18 (", 1)
    (d / "n.log").write_text(old, encoding="utf-8")
    ec, out = run(d)
    check(ec == 0 and "track 1: 1 read, nothing to compare it with" in out,
          f"before .19 the loop's checksum is not a read's EAC CRC32: exit {ec}\n{out}")
    check("were read once, which nothing here can compare" in out,
          f"the summary must count the tracks read once: {out[-300:]}")

# --- from .20 the kept read at the repeat limit is not always the last -------
# The -Z spool (d7ee6c4) keeps the read the most reads agreed on, newest on a
# tie, and the loop prints no line for its last read. On the 2026-10-06 run,
# section N's track 5 read E0036697, C96464AB, C96464AB, BBB13C9B and a fifth
# read, and kept E0036697: a two-two tie the fifth read must have made, so it
# was E0036697 and the log carries all five. Changing the fourth pass to
# E0036697 makes the case where it does not: E and C tie on the printed passes,
# E is the newer, so E is kept, and the fifth read was neither. Counting the
# kept block as that read would report E three times and lose the fifth.
R1006 = ROOT / "docs" / "rig-2026-10-06-5704062" / "rips"
spool = (R1006 / "secure-reread.log").read_text(encoding="utf-8")
fourth = "Repeating ripping (0 out of 2 matches for current checksum BBB13C9B)"
check(spool.count(fourth) == 1 and spool.startswith(
      "cyanrip 0.9.4-rc2+platterpus.20 (platterpus-fork-g5704062)"),
      "fixture drift: secure-reread.log of 2026-10-06 changed")
with tempfile.TemporaryDirectory() as t:
    d = pathlib.Path(t)
    (d / "s.log").write_text(spool, encoding="utf-8")
    ec, out = run(d)
    check(re.search(r"^  track 5: 5 read\(s\), 3 distinct EAC CRC32  DISAGREE$", out, re.M)
          and crc_line(out, "E0036697")[0] == 2,
          f"a tie the last read made: all five reads are in the log:\n{out}")
    (d / "s.log").write_text(spool.replace(fourth, "Repeating ripping (1 out of 2 "
                             "matches for current checksum E0036697)"), encoding="utf-8")
    ec, out = run(d)
    check(re.search(r"^  track 5: 5 read\(s\), 2 distinct EAC CRC32 in the log and 1 "
                    r"read\(s\) whose checksum it does not carry  DISAGREE$", out, re.M),
          f"a kept read that is not the last: the last read is not in the log:\n{out}")
    check(crc_line(out, "E0036697")[0] == 2,
          f"the kept read was counted as the last read too:\n{out}")

# --- a positive line that contains a negative phrase -------------------------
# Platterpus's round 27 lap 5 §C: a classifier that decides NEGATIVE on a phrase
# misreads a positive line containing it, and `.17`'s 450 match ends
# "whole-track checksums not found". Ours matches the parenthetical's START and
# tries the positive forms first; this pins that, on both wordings.
import importlib.util
_spec = importlib.util.spec_from_file_location("cross_rip_tool", TOOL)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
for line, want in [
    ("    Accurip 450: 57722DDE (matches Accurip DB, confidence 200, one frame "
     "only; whole-track checksums not found)\n", "450 match, confidence 200"),
    ("    Accurip 450: 57722DDE (matches Accurip DB, confidence 200, partially "
     "accurately ripped)\n", "450 match, confidence 200"),
    ("    Accurip v1:  1B28C061 (not found, either a new pressing, or bad rip)\n",
     "v1 not found"),
]:
    got = _mod.ar_summary(line)
    check(got == want, f"{line.strip()!r} read as {got!r}, want {want!r}")

if failures:
    print(f"{failures} check(s) failed", file=sys.stderr)
    sys.exit(1)
print("cross-rip reader: all checks passed")
