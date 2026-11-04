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

"""The build tag names its commit in seven characters, however big the clone.

`git rev-parse --short` takes its length from the repository's object count,
and this repository passed git's eight-character line with .29: a full clone
built `platterpus-fork-g8d2ca726` where the release manifest, the ledger, our
laps and Platterpus's pin say `8d2ca72`, and their installer refused the
owner's install of .29 (platterpus@7fdc33a1). The build now asks for seven,
and an archive carries the full hash, cut to seven.

The tag script is taken from src/meson.build and run here, in a repository
told to abbreviate at twelve and in a directory with no git at all, so the
check does not depend on how big the clone running it is. The binary's own
banner is then held to the same rule.
"""

import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CRIP = str(pathlib.Path(sys.argv[1]).resolve()) if len(sys.argv) > 1 else None
fails = 0

# No automatic gc in the repositories built here, as tests/lap_and_run_tools.py
# explains; and no enclosing repository found from a directory meant to have
# none.
ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
       "GIT_CONFIG_COUNT": "2",
       "GIT_CONFIG_KEY_0": "gc.auto", "GIT_CONFIG_VALUE_0": "0",
       "GIT_CONFIG_KEY_1": "maintenance.auto", "GIT_CONFIG_VALUE_1": "false"}


def check(ok, msg):
    global fails
    print(f"{'ok  ' if ok else 'FAIL:'} {msg}")
    fails += not ok


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t",
                           "-c", "user.email=t@t", *args], check=True,
                          capture_output=True, text=True, encoding="utf-8",
                          env=ENV).stdout.strip()


def tag_script():
    """The shell the build runs for its tag, as src/meson.build gives it."""
    text = (ROOT / "src" / "meson.build").read_text(encoding="utf-8")
    m = re.search(r"'cd ' \+ meson\.project_source_root\(\) \+\s*'''(.*?)'''",
                  text, re.S)
    return m.group(1) if m else None


def run_tag(script, where, ceiling):
    env = dict(ENV, GIT_CEILING_DIRECTORIES=str(ceiling))
    r = subprocess.run(["sh", "-c", f"cd {where}" + script], capture_output=True,
                       text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout.strip()


def main():
    script = tag_script()
    check(script is not None, "src/meson.build's vcs_tag script is found")
    if script is None:
        return 1
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        d = pathlib.Path(d).resolve()

        # A working tree whose git abbreviates at twelve: the stand-in for a
        # clone big enough to lengthen a short hash.
        repo = d / "repo"
        repo.mkdir()
        git(repo, "init", "-q")
        (repo / "f").write_text("x\n", encoding="utf-8")
        git(repo, "add", "f")
        git(repo, "commit", "-q", "-m", "c")
        git(repo, "config", "core.abbrev", "12")
        full = git(repo, "rev-parse", "HEAD")
        check(len(git(repo, "rev-parse", "--short", "HEAD")) == 12,
              "the scratch repository abbreviates at twelve")
        ec, out = run_tag(script, repo, d)
        check(ec == 0 and out == full[:7],
              f"a clone abbreviating at twelve tags its commit in seven: "
              f"{out!r}, want {full[:7]!r}")
        (repo / "f").write_text("y\n", encoding="utf-8")
        ec, out = run_tag(script, repo, d)
        check(ec == 0 and out == full[:7] + "-dirty",
              f"a modified tree still says -dirty after seven: {out!r}")

        # A source archive: no git, and the file export-subst fills in. The
        # full hash and an eight-character one both give the first seven.
        arch = d / "arch"
        (arch / "src").mkdir(parents=True)
        for given in (full, full[:8]):
            (arch / "src" / "archive-version.txt").write_text(given + "\n",
                                                              encoding="utf-8")
            ec, out = run_tag(script, arch, d)
            check(ec == 0 and out == full[:7],
                  f"an archive naming {len(given)} characters tags seven: "
                  f"{out!r}, want {full[:7]!r}")
        (arch / "src" / "archive-version.txt").write_text("$Format:%H$\n",
                                                          encoding="utf-8")
        ec, out = run_tag(script, arch, d)
        check(ec == 0 and out == "unknown",
              f"an unsubstituted placeholder tags unknown: {out!r}")

    # What git archive writes into the file, from this checkout, when it is one.
    placeholder = (ROOT / "src" / "archive-version.txt").read_text(encoding="utf-8")
    check(placeholder.strip() == "$Format:%H$",
          f"src/archive-version.txt asks for the full hash: {placeholder.strip()!r}")
    try:
        head = git(ROOT, "rev-parse", "HEAD")
        got = subprocess.run(
            ["sh", "-c", "git archive HEAD src/archive-version.txt | tar -xO"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            env=ENV).stdout.strip()
        check(got == head, f"git archive fills in the full hash: {got!r}")
    except subprocess.CalledProcessError:
        print("UNPROBED: the source tree is not a git checkout, so git archive "
              "was not run")

    # The binary this build made, held to the same rule.
    if CRIP:
        banner = subprocess.run([CRIP, "-V"], capture_output=True, text=True,
                                encoding="utf-8").stdout.strip()
        m = re.search(r"\(platterpus-fork-g([^)]*)\)", banner)
        tag = m.group(1) if m else ""
        try:
            # git lengthens a prefix only where seven would be ambiguous
            want = git(ROOT, "rev-parse", "--short=7", "HEAD")
            check(re.fullmatch(re.escape(want) + r"(-dirty)?", tag) is not None,
                  f"this build's banner tags its commit as --short=7 does: "
                  f"{banner!r}, want {want!r}")
        except subprocess.CalledProcessError:
            check(re.fullmatch(r"[0-9a-f]{7}(-dirty)?|unknown", tag) is not None,
                  f"this build's banner tags its commit in seven: {banner!r}")
    else:
        print("UNPROBED: no cyanrip binary given, so its banner was not read")
    if fails:
        print(f"{fails} check(s) failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
