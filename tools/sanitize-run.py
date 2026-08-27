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

"""Rip every disc-image fixture under AddressSanitizer and UBSan.

WHY, and it is a measurement rather than a worry. `tests/rip_images.py` carries
three assertions of the form `if "runtime error" in out: fail(...)`, written
while chasing the CD-Extra session-gap underflow. The committed build is
`b_sanitize=none` -- `nm build/src/cyanrip | grep -ci ubsan` returns **0** -- so
UBSan can never print that string and **those three checks cannot fail.** They
have been decoration since the day the investigation ended.

Meson sets ASAN_OPTIONS and UBSAN_OPTIONS for every test it runs, which is what
made this hard to see: the environment looks instrumented in the test log while
the binary is not.

The fix is not to delete the checks. It is to run the suite against a build
where they can fire. Signed-overflow, shift-out-of-range, a bad array index and
a NULL deref are exactly the defects that turn an archival record into a
confident wrong number, and this program does lsn arithmetic on every track.

MEASURED COST, so the trade is explicit rather than assumed: a cold configure
and build of the instrumented tree is ~7 s, the 37 image scenarios take ~16 s
under it. About 23 s to make a whole class of defect un-omittable.

IT VERIFIES THAT THE BINARY IS INSTRUMENTED BEFORE BELIEVING A CLEAN RUN. A
sanitizer sweep over a build with no sanitizer in it reports zero findings and
means nothing -- the same shape as a mutation sweep whose every mutant is killed
by a check that hashes the source. `nm` is asked, not the build options.

    tools/sanitize-run.py            # configure if needed, build, run
    tools/sanitize-run.py --quick    # a representative subset, for iteration
"""

import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = ROOT / "build-asan"

# The scenarios that do the most integer and pointer arithmetic on values a
# disc supplies: LSNs, session gaps, offsets, track counts, and the argument
# parser's own bounds. --quick runs these; the default runs everything.
QUICK = ["enhanced_cd", "pregap", "duration", "cli", "sanitize", "basic"]

# `contract_build` is excluded, for a reason that is not about sanitizers at
# all and that this tool got wrong on its first day.
#
# It compares PROVIDER-CONTRACT.md's source anchor -- a sha256 over src/ --
# against the live tree, so it fails on ANY byte changed in src/, behaviour or
# not. tools/mutate.py already excludes it for that reason. This tool did not,
# and because it runs the whole images suite in the instrumented tree, it
# INHERITED the check transitively: a mutation sweep whose third stage runs
# `--no-suite images` picks up "Sanitizer sweep", which runs contract_build,
# which kills every mutant on the edit.
#
# That is exactly how the FIRST sweep in this repository came to report 100%
# over 100 mutants and mean nothing, reintroduced by the commit that added this
# file -- and CLAUDE.md had predicted it in those words: "a second one added
# later would silently restore the 100%." The first cyanrip_encode.c sweep
# scored 100.0% because of it.
#
# Found the way that rule says to: append a comment to a source file, moving no
# line number and changing no behaviour, and ask which tests fail. Two did.
EXCLUDED = {"contract_build"}


def scenarios():
    """Every image scenario except the ones that detect an edit, from
    tests/meson.build so the list cannot go stale as scenarios are added."""
    text = (ROOT / "tests" / "meson.build").read_text(encoding="utf-8")
    block = re.search(r"rip_scenarios = \[(.*?)\]", text, re.S)
    if not block:
        print("FAIL: no rip_scenarios list in tests/meson.build")
        sys.exit(1)
    names = [n for n in re.findall(r"'([a-z0-9_]+)'", block.group(1))
             if n not in EXCLUDED]
    if not names:
        print("FAIL: every scenario was excluded")
        sys.exit(1)
    return names


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)


def skip(msg):
    """Exit 77 -- meson counts it as skipped and keeps it visible.

    For a check that CANNOT run here, never for one that ran and found nothing.
    Those are different claims and this suite exists to keep them apart.
    """
    print("SKIP:", msg)
    sys.exit(77)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="a representative subset rather than all 37")
    args = ap.parse_args()

    if not shutil.which("meson") or not shutil.which("ninja"):
        skip("meson or ninja is not on PATH")

    if not (BUILD / "build.ninja").exists():
        r = run(["meson", "setup", str(BUILD),
                 "-Db_sanitize=address,undefined", "-Db_lundef=false"])
        if r.returncode != 0:
            # A toolchain without a sanitizer runtime is an environment
            # limitation, not a defect in this program. Say which.
            tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
            skip("could not configure an instrumented build; this compiler or "
                 "libc may have no sanitizer runtime: " + " / ".join(tail))

    r = run(["ninja", "-C", str(BUILD)])
    if r.returncode != 0:
        print("FAIL: the instrumented build did not compile")
        print((r.stdout + r.stderr)[-2000:])
        return 1

    # THE CHECK THAT STOPS THIS BEING DECORATION IN ITS TURN. Asked of the
    # binary, not of the build options: a stale build directory configured
    # without sanitizers would otherwise report a clean sweep forever.
    binary = BUILD / "src" / "cyanrip"
    nm = run(["nm", str(binary)])
    symbols = sum(1 for line in nm.stdout.splitlines()
                  if "ubsan" in line.lower() or "asan" in line.lower())
    if nm.returncode != 0:
        blob = binary.read_bytes()
        symbols = (b"__ubsan_handle" in blob) + (b"__asan_report" in blob)
    if not symbols:
        print(f"FAIL: {binary} carries no sanitizer symbols, so a clean run "
              f"would prove nothing. Wipe {BUILD.name} and re-run.")
        return 1

    cmd = ["meson", "test", "-C", str(BUILD), "--suite", "images"]
    if args.quick:
        cmd += QUICK
    else:
        cmd += scenarios()
    r = run(cmd, timeout=1800)
    out = r.stdout + r.stderr

    # THE TEST LOG, NOT MESON'S SUMMARY. meson prints a failing test's command
    # and a few lines, and truncates the stdout that carries UBSan's own
    # message -- so classifying from `out` alone reported "failed without a
    # sanitizer finding" for a deliberately injected shift-out-of-range. Right
    # finding, wrong diagnosis, inside the tool whose job is to tell the two
    # apart. Proved by injecting `_ub << 40` into crip_fill_discid().
    log = BUILD / "meson-logs" / "testlog.txt"
    haystack = out
    if log.exists():
        haystack += "\n" + log.read_text(encoding="utf-8", errors="replace")

    # "the rip broke" and "the rip was fine and UBSan objected" are different
    # findings that want different fixes, so say which.
    findings = [l for l in haystack.splitlines()
                if "runtime error" in l or "AddressSanitizer" in l
                or "LeakSanitizer" in l]
    if findings:
        print(f"FAIL: {len(findings)} sanitizer finding(s):")
        for l in findings[:40]:
            print("   ", l.strip()[:160])
    elif r.returncode != 0:
        print("FAIL: the instrumented suite failed without a sanitizer "
              "finding, so the defect is in the rip and not in undefined "
              "behaviour:")
        print(out[-2000:])

    n_ran = len(QUICK) if args.quick else len(scenarios())
    scope = (f"{n_ran} scenario(s), --quick" if args.quick
             else f"{n_ran} scenario(s), excluding {sorted(EXCLUDED)}")
    if r.returncode == 0 and not findings:
        print(f"clean under address,undefined over {scope} "
              f"({symbols} sanitizer symbols in the binary)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
