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

"""tools/gen-upstream-issues.py gives one answer whatever a clone's mirror of
upstream's `master` holds.

On 2026-11-02 docs/upstream/issues-to-file.md passed `--check` here and failed
it in CI, twice: this clone's `master` branch was at `7dbe56a` while CI fetched
`648b1dd`, and which commits link to upstream follows that ref. The file now
names the upstream commit its links were resolved against, and `--check`
renders against that commit. Each probe runs the generator on a view of this
repository with refs of its own, a git directory sharing this one's objects,
so the real refs are never touched:

  * stale: `master` and `origin/master` both at the fork point, the state that
    failed. A render there must differ from the committed file, or the probe
    cannot tell anything and says UNPROBED; `--check` of the committed file
    must pass all the same;
  * ahead: `origin/master` at the pinned commit, `master` at the fork point.
    A render takes `origin/master`, which any fetch moves, and must equal the
    committed file;
  * a file naming a commit the clone lacks fails `--check` with how to get it,
    and a file naming none fails it as stale.
"""

import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "gen-upstream-issues.py"
FILE = ROOT / "docs" / "upstream" / "issues-to-file.md"
PINNED = re.compile(r"^\*\*Links were resolved against upstream's `master` at "
                    r"`([0-9a-f]{7,40})`\*\*", re.M)

failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


def git(*args, env=None):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                          text=True, env=env, encoding="utf-8")


def gen(*args, env=None):
    return subprocess.run([sys.executable, str(TOOL), *args],
                          capture_output=True, text=True, env=env,
                          encoding="utf-8")


have = FILE.read_text(encoding="utf-8")
m = PINNED.search(have)
if not m:
    print(f"FAIL: {FILE.name} names no upstream commit its links were "
          "resolved against")
    sys.exit(1)
pin = git("rev-parse", "-q", "--verify", m.group(1) + "^{commit}").stdout.strip()
head = git("rev-parse", "--verify", "HEAD").stdout.strip()
if not pin or not head:
    print(f"FAIL: this clone lacks upstream's {m.group(1)}, which the file "
          "names; CI fetches master, and `git fetch origin master` brings it")
    sys.exit(1)
fork = git("merge-base", head, pin).stdout.strip()

common = pathlib.Path(git("rev-parse", "--git-common-dir").stdout.strip())
if not common.is_absolute():
    common = ROOT / common

with tempfile.TemporaryDirectory(prefix="upstream-issues-") as tmp:
    view = pathlib.Path(tmp) / "view.git"
    subprocess.run(["git", "init", "-q", "--bare", str(view)], check=True)
    (view / "objects" / "info" / "alternates").write_text(
        str(common / "objects") + "\n", encoding="utf-8")
    if (common / "shallow").exists():
        (view / "shallow").write_bytes((common / "shallow").read_bytes())
    env = {**os.environ, "GIT_DIR": str(view)}
    env.pop("GIT_WORK_TREE", None)

    def refs(master, origin):
        git("update-ref", "--no-deref", "HEAD", head, env=env)
        git("update-ref", "refs/heads/master", master, env=env)
        git("update-ref", "refs/remotes/origin/master", origin, env=env)
        got = [git("rev-parse", r, env=env).stdout.strip()
               for r in ("HEAD", "master", "origin/master")]
        if got != [head, master, origin]:
            fail(f"the view's refs are {got}, not {[head, master, origin]}")

    # stale: both mirrors at the fork point
    refs(fork, fork)
    r = gen(env=env)
    if r.returncode != 0:
        fail(f"a render with a stale mirror exited {r.returncode}: {r.stderr}")
    elif r.stdout == have:
        print(f"UNPROBED: a mirror at the fork point {fork[:7]} renders the "
              f"same file as {pin[:7]}, so no ref here could change --check's "
              "answer")
    else:
        print(f"ok   a mirror at {fork[:7]} renders a different file from the "
              f"one pinned to {m.group(1)}")
    r = gen("--check", str(FILE), env=env)
    if r.returncode != 0:
        fail(f"--check followed the stale mirror at {fork[:7]}, not the "
             f"pinned {m.group(1)}: exit {r.returncode}\n{r.stderr}")
    else:
        print(f"ok   --check passes with both mirrors at {fork[:7]}")

    # ahead: a fetch moved origin/master, the branch stayed behind
    refs(fork, pin)
    r = gen(env=env)
    if r.stdout != have:
        fail(f"a render with origin/master at {pin[:7]} and master at "
             f"{fork[:7]} is not the committed file: it took the branch")
    else:
        print(f"ok   a render takes origin/master at {pin[:7]} over master "
              f"at {fork[:7]}")

    # a pin this clone lacks, and no pin
    for name, text, code, needle in (
            ("a pin the clone lacks",
             have.replace(f"at `{m.group(1)}`**", "at `0000000`**", 1), 1,
             "`git fetch origin master` brings it"),
            ("no pin",
             PINNED.sub("", have, count=1), 1,
             "names no upstream commit")):
        p = pathlib.Path(tmp) / "issues.md"
        p.write_text(text, encoding="utf-8")
        r = gen("--check", str(p))
        if r.returncode != code or needle not in r.stderr:
            fail(f"{name}: exit {r.returncode}, want {code} saying "
                 f"{needle!r}:\n{r.stderr}")
        else:
            print(f"ok   {name} fails --check, saying so")

if failures:
    print(f"{failures} failure(s)")
    sys.exit(1)
print("all checks passed")
