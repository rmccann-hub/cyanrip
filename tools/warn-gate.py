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

-WEXTRA IS SHIPPED AND GATED SINCE 2026-11-03, less two of its checks, which
are a real bound on this tool. Under the full set the src/ units gave 35
diagnostics at 16 sites of -Wunused-parameter and 13 of -Wsign-compare, and
nothing else, so the rest of -Wextra (missing initialisers, type limits, empty
bodies, implicit fall-through) came in at zero. The two left off were read site
by site, and src/meson.build says what they are; none is a defect. A new site
of either kind fails nothing: `--extra` turns the two back on and lists them,
and never gates. Recorded rather than silently dropped, because a gate that
quietly covers less than a reader assumes is worse than none.

A CORRECTION, 2026-11-03. This docstring said, from 2026-09-06, that one of
those warnings was a known defect: "unused parameter 'deemphasis'" in
src/cyanrip_encode.c, the de-emphasis that `-H` threw away, and that "the
compiler has been pointing at it the whole time". It never was. At 9995a10,
where that was written, the unused parameter is `setup_out_avctx()`'s, which
sets the encoder up and has no use for it; the defect was in
`init_filtering()`, where `deemphasis` IS used, in the branch of a ternary
cascade that `hdcd` never let it reach. No unused-parameter warning can see
that. The defect was found by a test and fixed in b866900 (SETTLED.md, the
`-H` row); the warning still stands at the same harmless parameter.

(Counts are over src/ only. compile_commands.json also carries test units,
which is why an earlier hand count said 29 and 26. A header included by
several units is reported once per unit, so 35 diagnostics are 29 sites.)

ONLY DIAGNOSTICS LOCATED IN THIS TREE ARE GATED, and the rest are printed.
CI's first macOS run showed why: clang reports `-Wundef`, one of our flags,
inside Homebrew's libcdio-paranoia `cdda.h` (`TESTING_IS_FINISHED`), because
pkg-config hands that header over by -I and not as a system header, where the
same flag says nothing on Linux. A count that moves when a dependency moves is
the thing this gate exists not to be, so a diagnostic whose file is outside
this repository is listed as NOT GATED, with its count, and never hidden.

THE TRAP, and it made an earlier attempt report a false zero. Every compile line
carries `-fdiagnostics-color=always`, so a checker that greps for `: warning:`
matches nothing when the text is wrapped in ANSI escapes. Colour is disabled
explicitly below rather than stripped afterwards.

Usage:
    tools/warn-gate.py                    # non-zero if any diagnostic appears
    tools/warn-gate.py --extra            # list the two -Wextra checks left off; never gates
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
        # The two checks src/meson.build leaves off, named outright. Appending
        # -Wextra instead would list nothing under GCC, where an explicit
        # -Wno- wins wherever it stands; clang lets the last flag win.
        cmd += " -Wunused-parameter -Wsign-compare"
    r = subprocess.run(cmd, shell=True, cwd=entry["directory"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, timeout=300, encoding="utf-8")
    return [m for m in (DIAG.match(l) for l in r.stdout.splitlines()) if m]


def partition(entry, found):
    """(ours, theirs): the diagnostics located in this tree, which gate, and
    those located anywhere else, such as a dependency's header, which do not.
    A relative path is relative to the compile's directory."""
    ours, theirs = [], []
    for m in found:
        p = pathlib.Path(m.group("file"))
        if not p.is_absolute():
            p = pathlib.Path(entry["directory"]) / p
        (ours if p.resolve().is_relative_to(ROOT) else theirs).append(m)
    return ours, theirs


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--build", default="build",
                    help="the build directory, relative to the repository or "
                         "absolute; meson test passes its own")
    ap.add_argument("--extra", action="store_true",
                    help="list the two -Wextra checks the build leaves off; "
                         "informational, never gates")
    args = ap.parse_args()

    cc = ROOT / args.build / "compile_commands.json"
    if not cc.exists():
        print(f"FAIL: no {cc} -- meson has not configured {args.build}")
        return 1
    entries = json.loads(cc.read_text(encoding="utf-8"))
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

    found, outside = [], []
    for e in ours:
        mine, other = partition(e, diagnostics(e, args.extra))
        found += mine
        outside += other

    by_kind = collections.Counter(m.group("kind") for m in found)
    by_flag = collections.Counter(
        (re.search(r"\[-W([a-z0-9-]+)\]", m.group("msg")) or [None, "no-flag"])[1]
        for m in found)

    label = ("the shipped flags plus -Wunused-parameter -Wsign-compare"
             if args.extra else "the shipped flags")
    print(f"{len(ours)} translation unit(s) re-run under {label}: "
          f"{len(found)} diagnostic(s)")
    for flag, n in by_flag.most_common():
        print(f"    {n:4d}  -W{flag}")
    for m in found[:25]:
        print(f"  {m.group('file')}: {m.group('kind')}: {m.group('msg')[:110]}")
    if outside:
        seen = collections.Counter((m.group("file"), m.group("kind"),
                                    m.group("msg")[:110]) for m in outside)
        print(f"NOT GATED: {len(outside)} diagnostic(s) located outside this "
              f"tree, in {len({f for f, _, _ in seen})} file(s)")
        for (f, kind, msg), n in seen.most_common(10):
            print(f"  {n:4d}x {f}: {kind}: {msg}")

    if args.extra:
        print("\n--extra is informational and never gates. src/meson.build "
              "says why these two checks are off.")
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
