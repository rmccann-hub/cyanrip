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

"""Fail when a compiler diagnostic appears, using the flags the build ships.

WHY A TEST AND NOT -Werror. Setting -Werror would also fail on a NEW compiler
version's new warnings, turning an unrelated toolchain bump into a red build.
This pins the diagnostic COUNT under the flags actually used, which moves only
when our own code moves.

WHY NOW. Measured 2026-09-06 across the **19** src/ translation units: **0
diagnostics under the shipped flags.** The gate is therefore free today, and it
stops being free the moment one lands -- after that, someone has to triage a
backlog to get the gate they could have had for nothing.

WHAT IS NOT GATED, and it is a real bound on this tool. Under `-Wextra` the same
19 units produce **22** diagnostics: 13 -Wunused-parameter and 9 -Wsign-compare.
Gating on -Wextra means fixing those first, which is a separate change with its
own argument. Recorded rather than silently dropped, because a gate that quietly
covers less than a reader assumes is worse than none.

AND ONE OF THE 22 IS A KNOWN DEFECT, which is the argument for eventually
gating on -Wextra rather than a reason to dismiss it:

    src/cyanrip_encode.c: warning: unused parameter 'deemphasis'

`deemphasis` is unused because `init_filtering()`'s filter string is a ternary
cascade in which `hdcd` wins outright, so de-emphasis never enters the graph --
the defect held for round 16, where the log prints `(deemphasis applied)` from
the settings anyway. The compiler has been pointing at it the whole time.

(Counts are over src/ only. compile_commands.json also carries test units,
which is why an earlier hand count said 29 and 26.)

THE TRAP, and it made an earlier attempt report a false zero. Every compile line
carries `-fdiagnostics-color=always`, so a checker that greps for `: warning:`
matches nothing when the text is wrapped in ANSI escapes. Colour is disabled
explicitly below rather than stripped afterwards.

Usage:
    tools/warn-gate.py                    # non-zero if any diagnostic appears
    tools/warn-gate.py --extra            # report the -Wextra set, never gates
    tools/warn-gate.py --build build
"""

import argparse
import collections
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIAG = re.compile(r"^(?P<file>[^:]+):\d+:\d+:\s+(?P<kind>warning|error):\s+(?P<msg>.*)$")


def diagnostics(entry, extra):
    """Re-run one compile line for diagnostics only, colour off."""
    cmd = entry["command"]
    cmd = cmd.replace("-fdiagnostics-color=always", "-fno-diagnostics-color")
    # A REAL COMPILE, not -fsyntax-only. Measured: -fsyntax-only stops before
    # the dataflow analysis, so it misses -Wunused-function, -Wuninitialized
    # and their neighbours entirely. An appended
    #     static int probe(void) { int u; return u; }
    # produced ZERO diagnostics under -fsyntax-only and one under a real
    # compile. The first version of this gate used -fsyntax-only and its own
    # revert-proof caught it: a gate that cannot fire is worse than none.
    cmd = re.sub(r"-o\s+\S+", "-o /dev/null", cmd)
    if extra:
        cmd += " -Wextra"
    r = subprocess.run(cmd, shell=True, cwd=entry["directory"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, timeout=300)
    return [m for m in (DIAG.match(l) for l in r.stdout.splitlines()) if m]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--build", default="build")
    ap.add_argument("--extra", action="store_true",
                    help="report the -Wextra set; informational, never gates")
    args = ap.parse_args()

    cc = ROOT / args.build / "compile_commands.json"
    if not cc.exists():
        print(f"FAIL: no {cc} -- meson has not configured {args.build}")
        return 1
    entries = json.loads(cc.read_text())
    if not entries:
        print(f"FAIL: {cc} is empty; refusing to report 0 diagnostics over "
              f"0 translation units, which would pass by measuring nothing")
        return 1

    # Only our own sources. compile_commands can carry generated units, and a
    # diagnostic in one of those is not something this tree can fix.
    ours = [e for e in entries
            if (pathlib.Path(e["directory"]) / e["file"]).resolve().is_relative_to(ROOT / "src")]
    if not ours:
        print("FAIL: no src/ translation unit in compile_commands.json")
        return 1

    found = []
    for e in ours:
        found += diagnostics(e, args.extra)

    by_kind = collections.Counter(m.group("kind") for m in found)
    by_flag = collections.Counter(
        (re.search(r"\[-W([a-z0-9-]+)\]", m.group("msg")) or [None, "no-flag"])[1]
        for m in found)

    label = "-Wextra" if args.extra else "the shipped flags"
    print(f"{len(ours)} translation unit(s) re-run under {label}: "
          f"{len(found)} diagnostic(s)")
    for flag, n in by_flag.most_common():
        print(f"    {n:4d}  -W{flag}")
    for m in found[:25]:
        print(f"  {m.group('file')}: {m.group('kind')}: {m.group('msg')[:110]}")

    if args.extra:
        print("\n--extra is informational and never gates. Gating on it means "
              "fixing these first.")
        return 0

    if found:
        print(f"\nFAIL: {by_kind['warning']} warning(s) and {by_kind['error']} "
              f"error(s) under the flags this build ships. The gate was free "
              f"when it was installed because the count was 0.")
        return 1

    print("\nclean under the shipped flags")
    return 0


if __name__ == "__main__":
    sys.exit(main())
