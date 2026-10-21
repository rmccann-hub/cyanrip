#!/usr/bin/env python3
"""CLAUDE.md stays within its cap: 300 lines and 32 KiB.

A session loads CLAUDE.md whole before it reads anything else. By
2026-10-19 this one was 2,720 lines and 174,166 bytes, every round added to
it, and a rule written once was lost among hundreds: the operator's review
of that day, item 3, found stale rules in it had already cost round trips.
The standard both repositories were set up against caps the file at 300
lines and 32 KiB, so it holds only the rules a session needs on every task;
history and reasons go to docs/history/, procedures to the documents they
describe. This is the test that keeps it there, as the review asked.

A rule that does not fit is a sign something else should move out, not that
the cap should move.

Usage: claude_md_cap.py [path]   (default: CLAUDE.md at the tree's root)
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_LINES = 300
MAX_BYTES = 32 * 1024

path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "CLAUDE.md"
data = path.read_bytes()
lines = data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)
failures = []
if lines > MAX_LINES:
    failures.append(f"{lines} lines, over the cap of {MAX_LINES}")
if len(data) > MAX_BYTES:
    failures.append(f"{len(data)} bytes, over the cap of {MAX_BYTES}")
if failures:
    for f in failures:
        print(f"FAIL: {path.name}: {f}. Move history and reasons to "
              f"docs/history/ and procedures to the documents they describe.")
    sys.exit(1)
print(f"{path.name}: {lines} of {MAX_LINES} lines, {len(data)} of "
      f"{MAX_BYTES} bytes")
