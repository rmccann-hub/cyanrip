#!/usr/bin/env python3
"""A BURN WRITES A DISC: no living text of ours calls a read one.

The owner, 2026-11-11, as Platterpus's round 39 lap 4 S10 quotes it: "a rip
is a read from the drive, a burn is write to a cd to the drive. i do not plan
to do burns right now." and "both sides shouldnt use burn unless they mean it
as i said". Both sides had called round 39's five back-to-back rips a "test
burn", which says the drive wrote in a run where it only read. In a program
whose whole job is reading discs, that is a wrong claim about what the drive
did, and CLAUDE.md's first rule is to say exactly what is true.

What it reads: every text file git tracks or would, except the records, which keep what
was written when it was written:
- our laps up to round 39 lap 3, the last one sent before the rule, and every
  lap of Platterpus's filed under docs/handshake/inbound/;
- the evidence manifest, whose paths carry the folder names Platterpus's
  runner gave the five rips;
- docs/history/, the Changelog's released sections and tests/fixtures/.

A line passes when it is about writing a disc, or states the rule that
retires the word for a read.

Usage: burn_means_writing.py [root]   (default: the tree this file is in)
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent
THIS = "tests/burn_means_writing.py"

# Every form of the word: burn, burns, burned, burnt, burning, burner.
BURN = re.compile(r"\bburn", re.IGNORECASE)

# The one meaning allowed: writing a disc, or the rule that says so, this
# check's own name included.
WRITING = re.compile(r"CD-RW?\b|burner|burned (?:disc|CD)|burn_means_writing"
                     r"|writ(?:e|es|ing) (?:to )?a (?:disc|cd)", re.IGNORECASE)

# Our laps are named round-R-lap-L.md; those sent before the rule are records.
LAP = re.compile(r"^docs/handshake/round-(\d+)-lap-(\d+)\.md$")
LAST_LAP_BEFORE_RULE = (39, 3)

# A released section of the Changelog opens with its version's header line.
RELEASED = re.compile(r"^\S.*\+platterpus\.\d+ — \d{4}-\d{2}-\d{2}")


def is_record(path):
    """A file that keeps what was written when it was written."""
    m = LAP.match(path)
    if m:
        return (int(m.group(1)), int(m.group(2))) <= LAST_LAP_BEFORE_RULE
    return path == "docs/evidence-manifest.tsv" or \
        path.startswith(("docs/handshake/inbound/", "docs/history/",
                         "tests/fixtures/"))


def released_from(path):
    """The first line number of the Changelog's released sections, else 0."""
    if path != "Changelog.md":
        return 0
    lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
    for n, line in enumerate(lines, 1):
        if RELEASED.match(line):
            return n
    return 0


# --untracked: a file not yet added is still text someone is about to commit,
# and a run that skipped it would pass on what it never read. A fixed string,
# because git grep's -E is the platform's regex library, and macOS's has no
# \b: there the word-boundary pattern matched nothing at all, and only the
# guard below said so. BURN finds the word on the lines it returns.
out = subprocess.run(["git", "grep", "--untracked", "-I", "-n", "-i", "-F",
                      "burn"], cwd=ROOT, capture_output=True,
                     encoding="utf-8")
if out.returncode not in (0, 1):
    print(f"FAIL: git grep exited {out.returncode}: {out.stderr.strip()}")
    sys.exit(1)

failures, records, allowed = [], 0, 0
cut = {}
for hit in out.stdout.splitlines():
    path, num, text = hit.split(":", 2)
    if path == THIS or not BURN.search(text):
        continue
    if is_record(path):
        records += 1
        continue
    if path not in cut:
        cut[path] = released_from(path)
    if cut[path] and int(num) >= cut[path]:
        records += 1
        continue
    if WRITING.search(text):
        allowed += 1
        continue
    failures.append(f"{path}:{num}: {text.strip()[:120]}")

# The check must be able to fire: the records hold the word, so a grep that
# found nothing would mean the grep, not the tree, is broken.
if records == 0:
    failures.append("no record line holds the word, so the grep cannot be "
                    "trusted to have read the tree")

for f in failures:
    print(f"FAIL: {f}")
print(f"burn_means_writing: {len(failures)} line(s) call a read a burn; "
      f"{records} record line(s) kept as written, {allowed} about writing")
sys.exit(1 if failures else 0)
