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

"""HR-2 point 2, as a check: no new reader of run evidence, and every fixture
copied from it still its source's bytes.

HR-2 (PROTOCOL.md v9 §17) moves run evidence to the `evidence` branch. Before
the move, every file a test, tool or check opened there was copied to
tests/fixtures/evidence/ or put behind tools/evidence.py; measured on
2026-10-14 in a clone with the move simulated, where `meson setup` failed on
one file named as a build input, ten tests failed, and thirty SETTLED rows went
stale. From then on, HR-2 says, a check refuses any new test, tool or check
that opens an evidence path. This is that check.

IT COUNTS EVERY MENTION, NOT EVERY OPEN. Telling a read from a docstring is a
guess, and a guess that errs towards "only prose" lets the next reader in. So
each file's mentions are counted and compared with an allowance that says why
each is there; one more fails, and so does one fewer, so the allowance never
drifts loose. A real new reader goes through tools/evidence.py or reads a
fixture copy, and its allowance says so.

AND EACH FIXTURE COPY IS CHECKED AGAINST ITS SOURCE: by the checkout's file
while the source is still here, and by its manifest row's SHA-256 after the
move, which needs nothing fetched. A copy that drifted from the run it came
from would make the tests reading it about a run nobody made.
"""

import hashlib
import pathlib
import re
import subprocess
import sys
import importlib.util

ROOT = pathlib.Path(__file__).resolve().parent.parent
THIS = "tests/evidence_readers.py"
sys.path.insert(0, str(ROOT / "tools"))
import evidence  # noqa: E402

PAT = re.compile(r"""docs/rig-|["']docs["']\s*/\s*["']rig-|glob\(\s*["']rig-"""
                 r"""|round-14-(?:rig|acceptance)-2026"""
                 r"""|inbound/artifacts/round-1[45]-lap""")
SCOPE = ["tools", "tests", ".github", "meson.build", "src/meson.build",
         ".claude"]

# Every file that names a run-evidence path, how many times, and why.
ALLOWED = {
    "tests/cuegap.c": (1, "a comment naming the log its numbers came from"),
    "tests/evidence_tool.py": (5, "run folders built in a temporary repository"),
    "tests/ingest_bundle.py": (5, "run folders built in a temporary directory"),
    "tests/lap_and_run_tools.py": (1, "a run folder built in a temporary "
                                      "directory"),
    "tests/lap_statements.py": (8, "lap texts citing a README at a commit, "
                                   "which stays, and a run folder built in a "
                                   "temporary repository for HR-2's cases"),
    "tests/personal_details.py": (1, "its docstring, naming its scope"),
    "tests/spool.c": (1, "a comment naming the run its case came from"),
    "tests/rip_images.py": (5, "two prefix tests on folders listed by "
                               "tools/evidence.py, and three docstrings"),
    "tools/cross-rip.py": (3, "its docstring's examples"),
    "tools/evidence.py": (5, "the one tool every evidence reader goes through"),
    "tools/ingest-bundle.py": (3, "help text and the refusal naming where a "
                                  "run is filed after the move"),
    "tools/read-run.py": (4, "examples, and the earlier runs it compares, "
                             "read through an overlay of tools/evidence.py"),
    "tools/rig-round16.sh": (1, "a message naming the reference on record"),
    "tools/round16-accept.py": (1, "a comment naming what its pinned copy "
                                   "reads"),
}
# SETTLED rows that re-check a fact against run evidence. tools/check-settled.py
# runs each through tools/evidence.py, so a moved file is read from the
# evidence branch or the row is unprobed; a new one is a new reader.
SETTLED_ROWS = 32

fails = 0


def check(ok, msg):
    global fails
    if ok:
        print(f"ok   {msg}")
    else:
        print(f"FAIL: {msg}")
        fails += 1


def listed():
    r = subprocess.run(["git", "ls-files", "-z", "--cached", "--others",
                        "--exclude-standard", "--", *SCOPE], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return None
    return sorted({p for p in r.stdout.split("\0") if p})


files = listed()
if files is None:
    print("SKIP: not a git checkout, so the files in scope cannot be listed")
    sys.exit(77)

counts = {}
for f in files:
    if f == THIS or f.startswith("tests/fixtures/"):
        continue
    try:
        text = (ROOT / f).read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    n = len(PAT.findall(text))
    if n:
        counts[f] = n
for f in sorted(set(counts) | set(ALLOWED)):
    have, (want, why) = counts.get(f, 0), ALLOWED.get(f, (0, ""))
    if have > want:
        check(False, f"{f} names a run-evidence path {have} time(s), allowed "
                     f"{want}. HR-2 point 2: a test, tool or check does not "
                     f"open run evidence. Read a copy under "
                     f"tests/fixtures/evidence/, or go through "
                     f"tools/evidence.py and raise this allowance saying why")
    elif have < want:
        check(False, f"{f} names a run-evidence path {have} time(s), allowed "
                     f"{want} ({why}). Lower the allowance, so the next new "
                     f"one is caught")
    else:
        check(True, f"{f}: {have}, {why}" if have else f"{f}: none")

spec = importlib.util.spec_from_file_location("check_settled",
                                              ROOT / "tools" / "check-settled.py")
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)
rows, in_main = 0, False
for line in (ROOT / "docs" / "SETTLED.md").read_text(encoding="utf-8").splitlines():
    cells = cs.cells(line)
    if cells is None or cells is cs.MALFORMED:
        continue
    fact, cmd = cells
    if fact == "fact":
        in_main = True
        continue
    if in_main and not cmd.startswith(("—", "--")) and PAT.search(cmd):
        rows += 1
check(rows == SETTLED_ROWS,
      f"{rows} runnable SETTLED row(s) re-check run evidence, allowed "
      f"{SETTLED_ROWS}" + ("" if rows == SETTLED_ROWS else
                           ". A new one is a new reader (HR-2 point 2); one "
                           "fewer lowers the allowance"))

# --- each fixture copy is still its source's bytes ------------------------
store = evidence.Store(ROOT)
src = ROOT / "tests" / "fixtures" / "evidence" / "SOURCES.tsv"
lines = src.read_text(encoding="utf-8").splitlines()
check(lines[:1] == ["fixture\tsource\tsha256"], "SOURCES.tsv has its header")
named = set()
tracked = set(files) | set(subprocess.run(
    ["git", "ls-files", "-z", "--", "tests/fixtures/evidence"], cwd=ROOT,
    capture_output=True, text=True, encoding="utf-8").stdout.split("\0"))
for ln in lines[1:]:
    fixture, source, digest = ln.split("\t")
    named.add(fixture)
    f = ROOT / fixture
    if not f.is_file():
        check(False, f"{fixture} is listed and missing")
        continue
    if fixture not in tracked:
        check(False, f"{fixture} is not tracked by git, so a clone lacks it")
    got = hashlib.sha256(f.read_bytes()).hexdigest()
    if got != digest:
        check(False, f"{fixture} hashes {got[:16]}..., SOURCES.tsv says "
                     f"{digest[:16]}...: a fixture copy was edited")
        continue
    if store.in_tree(source):
        theirs = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
        how = "the checkout's file"
    elif source in store.rows:
        theirs, how = store.rows[source].sha256, "its manifest row"
    else:
        check(False, f"{source}, the source of {fixture}, is neither in this "
                     f"checkout nor in {evidence.MANIFEST}")
        continue
    if theirs != digest:
        check(False, f"{fixture} is not {source}'s bytes ({how})")
copies = {p.relative_to(ROOT).as_posix()
          for p in (ROOT / "tests" / "fixtures" / "evidence").rglob("*")
          if p.is_file() and p.name != "SOURCES.tsv"}
check(copies == named, f"every file under tests/fixtures/evidence/ is listed "
                       f"in SOURCES.tsv, and only those: "
                       f"{sorted(copies ^ named)[:3]}")
check(len(named) >= 50, f"{len(named)} fixture copies checked against their "
                        f"sources")

print(f"\n{'all ok' if not fails else f'{fails} failure(s)'}")
sys.exit(1 if fails else 0)
