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

"""An argument Clang ignores in LDFLAGS no longer drops the hardening flags.

src/meson.build checks each hardening flag by linking a probe with
-Werror=unused-command-line-argument, which Clang accepts in a compile-only
check. With LDFLAGS=-mmacosx-version-min=10.9 on Linux every link check then
failed, before any flag was added, and `meson setup` succeeded with all four
flags left out: no -fstack-protector-strong anywhere in build.ninja. This
sets up a scratch build that way and asks for the warning and the flags.

It needs Clang, and a target where Clang ignores that argument at a link, so
it skips (77) on macOS, where the argument is used, and where Clang is
missing, as on CI's suite rows: a green suite there does not cover it.
"""

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
IGNORED = "-mmacosx-version-min=10.9"
WARNING = "The hardening probe does not link with"

clang = shutil.which("clang")
meson = shutil.which("meson")
if sys.platform == "darwin" or not clang or not meson:
    print("SKIP: needs clang and meson on a target that is not macOS")
    sys.exit(77)

with tempfile.TemporaryDirectory() as d:
    d = pathlib.Path(d)
    probe = d / "p.c"
    probe.write_text("int main(void) { return 0; }\n", encoding="utf-8")
    r = subprocess.run([clang, "-Werror=unused-command-line-argument", IGNORED,
                        str(probe), "-o", str(d / "p")],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode == 0:
        print(f"UNPROBED: this clang uses {IGNORED} at a link, so the state "
              f"cannot be built here")
        sys.exit(77)

    env = dict(os.environ, CC=clang, LDFLAGS=IGNORED)
    for k in ("CFLAGS", "CPPFLAGS", "CC_LD"):
        env.pop(k, None)
    r = subprocess.run([meson, "setup", str(d / "b"), str(ROOT)], env=env,
                       capture_output=True, text=True, encoding="utf-8")
    out = r.stdout + r.stderr
    fails = []
    if r.returncode != 0:
        fails.append(f"meson setup exited {r.returncode}:\n{out[-3000:]}")
    else:
        if WARNING not in out:
            fails.append("setup did not warn that the probe fails without "
                         "a flag")
        ninja = (d / "b" / "build.ninja").read_text(encoding="utf-8")
        for flag in ("-fstack-protector-strong", "-fcf-protection=full"):
            if flag not in ninja:
                fails.append(f"{flag} is not in build.ninja")

if fails:
    for f in fails:
        print("FAIL:", f)
    sys.exit(1)
print(f"hardening probe: with LDFLAGS={IGNORED} under clang the setup warns "
      f"and keeps the flags")
