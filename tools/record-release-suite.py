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

"""Run the suite at one commit, in a fresh worktree, and write down the result.

PLATTERPUS'S ROUND 30 LAP 2 S5 IS WHY THIS EXISTS. Every release plan says the
candidate was "proved green on its own: 97 of 97 in a fresh worktree from a
removed log", and the log that count came from lived in a scratch worktree
that was deleted once the proof was done. So neither side's checker could read
the lines behind the number, and what survived for `.19` was the run's stdout,
which names no commit. A count whose evidence is gone is a claim about a run,
not a record of one.

This writes the record in the form a reader can check:

  * the FULL SHA the worktree was checked out at, read back from the worktree
    rather than taken from the argument;
  * the run header count from meson's own testlog -- it must be 1, or the log
    is a composite of two runs and nothing in it is evidence;
  * every test's result line and the summary, from that single run;
  * the command, the meson version and the UTC start and end.

It exits non-zero, and writes nothing, if the build fails or the testlog does
not hold exactly one run. A red suite is still recorded, since a failure is a
result: the record then says so, and the exit status is the suite's.

    tools/record-release-suite.py 174a134 > docs/release-evidence/174a134-suite.txt
"""

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULT = re.compile(r"^\s*\d+/\d+ .*\s(OK|FAIL|SKIP|EXPECTEDFAIL|UNEXPECTEDPASS|"
                    r"TIMEOUT|ERROR)\s+[\d.]+s")
SUMMARY = re.compile(r"^(Ok|Expected Fail|Fail|Unexpected Pass|Skipped|Timeout):\s+\d+")


def run(argv, cwd, **kw):
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True, **kw)


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("commit")
    args = ap.parse_args()

    base = Path(tempfile.mkdtemp(prefix="release-suite-"))
    work = base / "tree"
    try:
        r = run(["git", "worktree", "add", "--detach", "--quiet", str(work),
                 args.commit], ROOT)
        if r.returncode:
            sys.exit(f"cannot check out {args.commit}: {r.stderr.strip()}")
        sha = run(["git", "rev-parse", "HEAD"], work).stdout.strip()
        dirty = run(["git", "status", "--porcelain"], work).stdout.strip()
        if dirty:
            sys.exit(f"the worktree at {sha} is not clean:\n{dirty}")

        build = work / "build"
        for step in (["meson", "setup", str(build)], ["ninja", "-C", str(build)]):
            r = run(step, work)
            if r.returncode:
                sys.exit(f"{' '.join(step[:2])} failed at {sha}:\n"
                         f"{(r.stdout + r.stderr)[-2000:]}")

        started = now()
        cmd = ["meson", "test", "-C", str(build), "--print-errorlogs"]
        env = dict(os.environ, TMPDIR=str(base))
        suite = run(cmd, work, env=env)
        ended = now()

        log = build / "meson-logs" / "testlog.txt"
        text = log.read_text(errors="replace") if log.exists() else ""
        headers = len(re.findall(r"(?m)^Log of Meson test suite run", text))
        if headers != 1:
            sys.exit(f"the testlog holds {headers} run header(s), not 1, so it "
                     f"is not one run's record")

        lines = suite.stdout.splitlines()
        results = [l.rstrip() for l in lines if RESULT.match(l)]
        summary = [l.rstrip() for l in lines if SUMMARY.match(l)]
        logged = len(re.findall(r"(?m)^\s*result:", text))
        meson = run(["meson", "--version"], work).stdout.strip()

        print(f"commit:       {sha}")
        print(f"command:      meson setup build && ninja -C build && "
              f"meson test -C build --print-errorlogs")
        print(f"meson:        {meson}")
        print(f"started:      {started}")
        print(f"ended:        {ended}")
        print(f"exit:         {suite.returncode}")
        print(f"run headers:  {headers} in meson-logs/testlog.txt")
        print(f"result lines: {len(results)} in the run's stdout, "
              f"{logged} in its testlog")
        print()
        for l in summary:
            print(l)
        print()
        for l in results:
            print(l)
        return suite.returncode
    finally:
        run(["git", "worktree", "remove", "--force", str(work)], ROOT)
        run(["git", "worktree", "prune"], ROOT)
        shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
