#!/usr/bin/env python3
"""The Python tools and tests pass ruff's Pyflakes rules (review C item 4.3).

ruff.toml chooses the rules: an undefined name, an unused import or variable,
a redefinition, an f-string with no field, a syntax error. Where ruff is not
installed this exits 77, skipped, unless CYANRIP_LINT_REQUIRED=1, which CI's
`linux (released)` row sets after installing a pinned ruff, so the gate runs
there and cannot pass by skipping.
"""

import os
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

if not shutil.which("ruff"):
    if os.environ.get("CYANRIP_LINT_REQUIRED") == "1":
        print("FAIL: CYANRIP_LINT_REQUIRED=1 and ruff is not installed")
        sys.exit(1)
    print("SKIP: ruff is not installed")
    sys.exit(77)

files = sorted(p for d in ("tools", "tests") for p in (ROOT / d).glob("*.py"))
if len(files) < 50:
    print(f"FAIL: {len(files)} Python files found in tools/ and tests/, "
          "expected over 50; the glob has stopped matching")
    sys.exit(1)
r = subprocess.run(["ruff", "check", "--no-cache", "--config",
                    str(ROOT / "ruff.toml"), *map(str, files)],
                   cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                   timeout=300)
sys.stdout.write(r.stdout)
sys.stderr.write(r.stderr)
if r.returncode != 0:
    sys.exit(1)
print(f"ruff: {len(files)} files pass the Pyflakes rules")
