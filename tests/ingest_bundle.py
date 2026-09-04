#!/usr/bin/env python3
"""The bundle ingester must refuse a bundle that says its run failed.

THE DEFECT THIS PINS. The 2026-09-03 acceptance bundle carried
`session/transcript.txt:293` reading `[ FAIL ] ... still not finished after
10800s` and `report.json` with `"ok": false`. Both were in our hands. Neither
was read, and `CC-1 IS MET` went into three documents.

Two properties, and the second is the one that made the first invisible:

  * the run's own verdict is read BEFORE anything else and a failing run exits
    non-zero -- rips inside a failed run are evidence about the ripper, the run
    is not;
  * the not-filed list is the SET DIFFERENCE between the archive and what was
    written, never a sentence somebody typed.

Fixtures are BUILT here rather than taken from a delivered archive. A test that
needs an upload cannot run in a clone, and the states that matter -- a bundle
with no verdict file at all, a passing one, a failing one -- are states no
single real bundle can supply.
"""

import io
import json
import pathlib
import subprocess
import sys
import tarfile
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE.parent / "tools" / "ingest-bundle.py"
failures = 0


def check(cond, msg):
    global failures
    if not cond:
        failures += 1
        print(f"FAIL: {msg}", file=sys.stderr)


def make(files):
    """Build a .tar.gz containing {name: bytes}. Returns its path."""
    d = pathlib.Path(tempfile.mkdtemp())
    p = d / "bundle.tar.gz"
    with tarfile.open(p, "w:gz") as tf:
        for name, data in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return p


def run(archive, *extra):
    r = subprocess.run([sys.executable, str(TOOL), str(archive), *extra],
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


RIP = b"cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-g978f9b0)\nRip completed:  yes (14 of 14 tracks)\n"


def test_a_failing_run_is_refused():
    """report.json ok:false must exit non-zero and say so at the top."""
    a = make({
        "album/x/x.log": RIP,
        "extra/report.json": json.dumps({"ok": False, "counts": {"pass": 217, "fail": 5}}).encode(),
    })
    rc, out = run(a, "--verdict-only")
    check(rc != 0, "a bundle declaring ok:false must exit non-zero")
    check("DID NOT PASS" in out, f"it must say so plainly: {out[:200]}")
    check("ok = False" in out, "it must quote the field it read")


def test_a_failing_transcript_is_refused_even_with_no_report():
    """[ FAIL ] lines alone are enough. The line number must be reported."""
    t = (b"log --- F ---\n" * 40) + b"[ FAIL ] L366  wait-for-rip 10800   (10800.1s)\n"
    a = make({"album/x/x.log": RIP, "session/transcript.txt": t})
    rc, out = run(a, "--verdict-only")
    check(rc != 0, "a transcript with [ FAIL ] must exit non-zero")
    check(":41" in out, f"the failing line's number must be reported: {out[:300]}")
    check("wait-for-rip 10800" in out, "the failing line itself must be quoted")


def test_a_passing_run_is_accepted_so_it_is_not_always_refusing():
    a = make({
        "album/x/x.log": RIP,
        "extra/report.json": json.dumps({"ok": True, "counts": {"pass": 218, "fail": 0}}).encode(),
        "session/transcript.txt": b"log --- all good ---\n",
    })
    rc, out = run(a, "--verdict-only")
    check(rc == 0, f"a passing bundle must be accepted: {out[:200]}")
    check("DID NOT PASS" not in out, "and must not be described as failing")


def test_no_verdict_file_is_NOT_read_as_a_pass():
    """The absence of a verdict is not a verdict. `none` vs `unknown (reason)`."""
    a = make({"album/x/x.log": RIP})
    rc, out = run(a, "--verdict-only")
    check("NO VERDICT FILE FOUND" in out, f"silence must be named: {out[:200]}")
    check("is NOT 'the run passed'" in out,
          "and must be distinguished from a pass in words")


def test_the_not_filed_list_is_derived_not_written():
    """Every archive member is either filed or named in SHA256SUMS. No third state."""
    files = {
        "album/x/x.log": RIP,
        "album/x/x.cue": b"REM nothing\n",
        "session/transcript.txt": b"clean\n",
        "extra/report.json": json.dumps({"ok": True}).encode(),
        "extra/shot.png": b"\x89PNG\r\n\x1a\n" + b"\0" * 40,
        "extra/blob.bin": b"\0" * 32,
    }
    a = make(files)
    d = pathlib.Path(tempfile.mkdtemp()) / "rig"
    rc, out = run(a, "--into", str(d))
    check(rc == 0, f"a passing bundle must file: {out[:200]}")
    sums = (d / "SHA256SUMS").read_text()
    for name in files:
        check(name in sums,
              f"{name} appears in neither the filed nor the not-filed list -- "
              "a member in no list is exactly the omission nobody can see")
    # the two that carry the verdict must be FILED, not merely named
    for v in ("session/transcript.txt", "extra/report.json"):
        onto = d / v
        check(onto.exists(), f"{v} carries the run's verdict and must be filed")
        check(onto.read_bytes() == files[v], f"{v} must be filed byte-exact")
    # and the binaries must be named as not filed rather than vanish
    for b in ("extra/shot.png", "extra/blob.bin"):
        check(f"(not filed) {b}" in sums, f"{b} must be NAMED as not filed")


for name, fn in sorted(globals().items()):
    if name.startswith("test_") and callable(fn):
        fn()

if failures:
    print(f"{failures} check(s) failed", file=sys.stderr)
    sys.exit(1)
print("all ingest-bundle checks passed")
