#!/usr/bin/env python3
"""A rip under Valgrind's memcheck: no memory error, nothing lost outright.

Review C item 3.7. ASan and UBSan instrument this program's own code, in two
of CI's rows, and TSan its threads in a third; none of them sees inside the
libraries it calls as built, FFmpeg, libcdio and libmusicbrainz among them.
Memcheck does, with no rebuild. This rips the basic image, -N -A -U, to FLAC
with a log and a CUE sheet, under

    valgrind --error-exitcode=99 --leak-check=full
             --errors-for-leak-kinds=definite --track-origins=yes

and fails on any error memcheck counts, a block definitely lost included, or
on a rip that did not happen: both tracks' files, the sheet, and the log's
Log FUN512 line must be there, so a run that exits 0 having done nothing
cannot pass.

    valgrind_rip.py CYANRIP FIXTURES SANITIZE

SANITIZE is meson's b_sanitize. Memcheck and a sanitizer's runtime cannot
share a process, so a sanitized build exits 77, skipped, as does a machine
without valgrind, unless CYANRIP_VALGRIND_REQUIRED=1: CI's linux (default)
row installs valgrind and sets it, so there this cannot pass by skipping.
"""

import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

cyanrip, fixtures, sanitize = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
required = os.environ.get("CYANRIP_VALGRIND_REQUIRED") == "1"

if sanitize != "none":
    print(f"SKIP: a {sanitize} build; memcheck cannot run beside its runtime")
    sys.exit(1 if required else 77)
if not shutil.which("valgrind"):
    if required:
        print("FAIL: CYANRIP_VALGRIND_REQUIRED=1 and valgrind is not installed")
        sys.exit(1)
    print("SKIP: valgrind is not installed")
    sys.exit(77)

failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


with tempfile.TemporaryDirectory(prefix="cyanrip-memcheck-") as d:
    work = pathlib.Path(d)
    # libcdio pairs a sheet with its .bin by basename, as rip_images.py stages
    shutil.copy(fixtures / "basic.cue", work)
    shutil.copy(fixtures / "cdda.bin", work / "basic.bin")
    out = work / "out"
    r = subprocess.run(["valgrind", "--error-exitcode=99", "--leak-check=full",
                        "--errors-for-leak-kinds=definite",
                        "--track-origins=yes", cyanrip,
                        "-d", str(work / "basic.cue"), "-N", "-A", "-U",
                        "-s", "0", "-P", "0", "-o", "flac", "-D", str(out),
                        "-F", "{track}", "-L", "log", "-M", "sheet"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=1200)
    summary = re.search(r"ERROR SUMMARY: (\d+) errors", r.stderr)
    if r.returncode != 0:
        fail(f"exit {r.returncode} under memcheck (99 is memcheck's own)")
    if not summary:
        fail("memcheck printed no ERROR SUMMARY, so it did not run the rip")
    elif summary.group(1) != "0":
        fail(f"memcheck counted {summary.group(1)} error(s)")
    lost = re.search(r"definitely lost: ([\d,]+) bytes", r.stderr)
    if lost and lost.group(1) != "0":
        fail(f"{lost.group(1)} bytes definitely lost")

    made = sorted(p.name for p in out.glob("*")) if out.exists() else []
    if made != ["1.flac", "2.flac", "log.log", "sheet.cue"]:
        fail(f"the rip left {made}, expected both tracks, the log and the sheet")
    log = (out / "log.log").read_text(encoding="utf-8", errors="replace") \
        if (out / "log.log").exists() else ""
    if not re.search(r"^Log FUN512: \S+$", log, re.M):
        fail("the log has no Log FUN512 line, so the rip did not finish")

    if failures:
        print("--- memcheck's report ---")
        print("\n".join(r.stderr.splitlines()[-60:]))

if failures:
    print(f"{failures} failure(s)")
    sys.exit(1)
print(f"memcheck: a rip of two tracks, {summary.group(0)}, "
      f"{lost.group(0) if lost else 'no leak summary'}")
