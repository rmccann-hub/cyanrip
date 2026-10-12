#!/usr/bin/env python3
"""tools/warn-gate.py gates the diagnostics located in this tree, and only
those.

CI's first macOS run showed clang reporting `-Wundef`, one of our flags, inside
Homebrew's libcdio-paranoia `cdda.h`, because pkg-config hands that header over
by -I rather than as a system header. Counted, that would make `Compiler
diagnostics` move whenever a dependency moves. Dropped silently, it would hide
a real diagnostic of ours that happened to be reported against an absolute
path. Each case below is one way partition() could get that wrong, on synthetic
compiler lines, so it needs no compiler of the kind that produced them.
"""

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "warn_gate", ROOT / "tools" / "warn-gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

ENTRY = {"directory": str(ROOT / "build")}
CASES = [
    # (line, gated?)
    ("../src/pregap.c:184:15: warning: unused variable 'ioctl_errno' "
     "[-Wunused-variable]", True),
    (f"{ROOT / 'src' / 'cyanrip_main.h'}:12:1: warning: an in-tree header "
     f"reported by absolute path [-Wundef]", True),
    ("/opt/homebrew/Cellar/libcdio-paranoia/10.2-2.0.2_1/include/cdio/paranoia/"
     "cdda.h:180:5: warning: 'TESTING_IS_FINISHED' is not defined, evaluates "
     "to 0 [-Wundef]", False),
    # A directory whose name starts with ours is not ours: the comparison is
    # by path component, not by string prefix.
    (f"{ROOT.parent / (ROOT.name + '-other') / 'x.h'}:1:1: warning: a "
     f"neighbour's header [-Wundef]", False),
    # A relative path that climbs out of the tree is not ours either.
    ("../../elsewhere/y.h:3:4: warning: outside, by a relative path "
     "[-Wundef]", False),
]

failures = 0
matches = []
for line, _ in CASES:
    m = gate.DIAG.match(line)
    if not m:
        print(f"FAIL: DIAG does not match {line[:70]!r}, so this case tests "
              f"nothing")
        failures += 1
    matches.append(m)

if not failures:
    ours, theirs = gate.partition(ENTRY, matches)
    if len(ours) + len(theirs) != len(CASES):
        print(f"FAIL: partition returned {len(ours)} + {len(theirs)} of "
              f"{len(CASES)} diagnostics; one was lost or doubled")
        failures += 1
    for (line, gated), m in zip(CASES, matches):
        got = any(m is o for o in ours)
        if got != gated:
            print(f"FAIL: {'gated' if got else 'not gated'} but should be "
                  f"{'gated' if gated else 'not gated'}: {line[:90]}")
            failures += 1

if failures:
    print(f"{failures} check(s) failed")
    sys.exit(1)
print(f"ok: {len(CASES)} diagnostics, {sum(g for _, g in CASES)} gated")
