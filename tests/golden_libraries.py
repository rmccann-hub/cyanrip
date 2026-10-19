#!/usr/bin/env python3
"""The golden checks compare only on the library set the reference was made
with, and nowhere else do they pass as checked.

docs/golden-reference.log is a byte record of a rip made with Ubuntu 24.04's
libcdio 2.1 and FFmpeg 6.1. CI's macOS job, on Homebrew's libcdio 2.4 and
FFmpeg 9.0.1, produced the same rip with every checksum and every other line
identical, and differed in text those libraries write and in paranoia's READ
counter. On 2026-10-12 the owner chose that the two golden checks compare only
on the reference's own library set and say SKIP, naming both, elsewhere.
tools/gen-golden-reference.py's library_mismatch() decides that for both, and
tools/check-settled.py reports the SETTLED row that re-runs one of them as
UNPROBED when it exits 77. Each case below is one way either could go wrong:

  * the real reference's own lines must read as libcdio 2.1, libavcodec 60;
  * the two lines macOS printed must read as a different set, and the reason
    must name both;
  * the same set, and a patch-level bump, must still be compared, because a
    bump on the reference's platform is what asks for a regeneration;
  * a log that names a library ambiguously or not at all must be compared,
    because a rip that failed before writing those lines must fail;
  * check-settled must count a 77 as unprobed, print its reason, and still
    report any other non-zero exit as stale;
  * and it must say where its time went, and, killed mid-row as meson kills
    a test that overruns, name the row it was running and exit 143;
  * and read that back out of meson's testlog.json for a run that passed.
"""

import contextlib
import importlib.util
import io
import json
import os
import pathlib
import signal
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gen = load("gen_golden", ROOT / "tools" / "gen-golden-reference.py")
settled = load("check_settled", ROOT / "tools" / "check-settled.py")

failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


ref = (ROOT / "docs" / "golden-reference.log").read_text()
drive = next(l for l in ref.splitlines() if l.startswith("Drive used:"))
encoder = next(l for l in ref.splitlines() if l.startswith("Encoder:"))
acoustid = next(l for l in ref.splitlines() if l.startswith("AcoustID:"))

# 1. The reference itself, from its own lines.
if gen.library_set(ref) != ("2.1", "60", "absent"):
    fail(f"the reference reads as {gen.library_set(ref)!r}, from {drive!r}, "
         f"{encoder!r} and {acoustid!r}")

# 2. The lines CI's macOS job printed for the same rip (run 38292984001).
mac = (ref.replace(drive, "Drive used:     libcdio CDRWIN (revision 2.4.)")
          .replace(encoder, "Encoder:        libavformat 63.1.101, "
                            "libavcodec 63.1.101 (9.0.1)"))
why = gen.library_mismatch(ref, mac)
if not why:
    fail("macOS's libcdio 2.4 and libavcodec 63 were compared with the "
         "reference's 2.1 and 60")
elif not all(v in why for v in ("2.1", "60", "2.4", "63", "absent")):
    fail(f"the reason does not name both sets: {why!r}")

# Each library alone is enough.
for label, fresh in (
        ("libcdio alone", ref.replace(drive, drive.replace("2.1.", "2.4."))),
        ("libavcodec alone", ref.replace(encoder, encoder.replace(
            "libavcodec 60.", "libavcodec 61."))),
        # A build with libchromaprint prints another AcoustID: value
        # (cyanrip_log.c), and nothing else about the library.
        ("libchromaprint alone", ref.replace(
            acoustid, "AcoustID:       fingerprinting, no user API key to "
                      "submit with"))):
    if fresh == ref:
        fail(f"{label}: the substitution did not land, so this case tests "
             f"nothing")
    elif not gen.library_mismatch(ref, fresh):
        fail(f"{label}: a different library set was compared")

# 3. Still compared: the same set, and a patch-level bump.
if gen.library_mismatch(ref, ref) is not None:
    fail("the reference against itself was not compared")
bumped = ref.replace(encoder, encoder.replace("(6.1.1-3ubuntu5)",
                                              "(6.1.1-3ubuntu5.1)")
                                     .replace("60.31.102", "60.31.103"))
if bumped == ref:
    fail("the patch-level substitution did not land")
elif gen.library_mismatch(ref, bumped) is not None:
    fail("a patch-level FFmpeg bump was skipped; it must fail and ask for a "
         "regeneration")

# 4. Fail closed: a library named ambiguously or not at all is compared.
for label, fresh in (
        ("no Drive used line", ref.replace(drive + "\n", "")),
        ("no Encoder line", ref.replace(encoder + "\n", "")),
        ("two Drive used lines", ref.replace(
            drive, drive + "\nDrive used:     libcdio CDRWIN (revision 2.4.)")),
        ("no AcoustID line", ref.replace(acoustid + "\n", "")),
        ("two AcoustID lines", ref.replace(
            acoustid, acoustid + "\nAcoustID:       disabled"))):
    if fresh == ref:
        fail(f"{label}: the substitution did not land")
    elif gen.library_mismatch(ref, fresh) is not None:
        fail(f"{label}: skipped without evidence that the libraries differ")


# 5. check-settled: 77 is unprobed and printed, anything else non-zero is
# stale. A table of its own, shaped to pass the checker's floors.
def run_settled(rows):
    table = ["| fact | check |", "|---|---|"]
    table += [f"| fact {i} | `true` |" for i in range(8)]
    table += rows
    table += ["| a structural fact | — structural: none |",
              "| a fact of theirs | — theirs: none |"]
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "SETTLED.md"
        p.write_text("\n".join(table) + "\n")
        saved, settled.SETTLED = settled.SETTLED, p
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                rc = settled.main()
        finally:
            settled.SETTLED = saved
    return rc, out.getvalue()


rc, out = run_settled(["| cannot be checked here | "
                       "`echo the libraries differ; exit 77` |"])
if rc != 0:
    fail(f"check-settled failed a row that exited 77 (rc {rc}):\n{out}")
if "UNPROBED" not in out or "the libraries differ" not in out:
    fail(f"check-settled did not print the unprobed row and its reason:\n{out}")
if "1 unprobed here" not in out:
    fail(f"check-settled did not count the unprobed row:\n{out}")

rc, out = run_settled(["| a real failure | `exit 3` |"])
if rc == 0 or "STALE" not in out:
    fail(f"check-settled did not report exit 3 as stale (rc {rc}):\n{out}")
if "TIMING:" not in out or "  exit 3" not in out:
    fail(f"check-settled did not say where its time went:\n{out}")

# 6. Killed mid-row, as meson kills a test that overruns its timeout, it
# names the row that was running (CI's macOS timeouts printed nothing at all,
# so no run could say where 120 s went: STATUS.md's settled-facts-macos).
with tempfile.TemporaryDirectory() as d:
    table = ["| fact | check |", "|---|---|"]
    table += [f"| fact {i} | `true` |" for i in range(8)]
    table += ["| a slow fact | `sleep 30` |",
              "| a structural fact | — structural: none |",
              "| a fact of theirs | — theirs: none |"]
    (pathlib.Path(d) / "SETTLED.md").write_text("\n".join(table) + "\n")
    code = ("import importlib.util, pathlib, sys\n"
            "spec = importlib.util.spec_from_file_location('cs', sys.argv[1])\n"
            "cs = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(cs)\n"
            "cs.SETTLED = pathlib.Path(sys.argv[2])\n"
            "sys.exit(cs.main())\n")
    proc = subprocess.Popen(
        [sys.executable, "-c", code, str(ROOT / "tools" / "check-settled.py"),
         str(pathlib.Path(d) / "SETTLED.md")],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        start_new_session=True)
    time.sleep(3)
    os.killpg(proc.pid, signal.SIGTERM)
    out = proc.communicate(timeout=20)[0]
    if proc.returncode != 143:
        fail(f"check-settled killed mid-row exited {proc.returncode}, not 143:"
             f"\n{out}")
    if "KILLED by signal 15" not in out or "running for" not in out \
            or "sleep 30" not in out or "with 8 row(s) run" not in out:
        fail(f"check-settled killed mid-row did not name the row it was "
             f"running:\n{out}")

# 7. --timing-from reads that block back out of meson's testlog.json, which
# keeps a passing test's stdout that meson itself never prints: CI runs it
# after every suite, so a pass near the limit names its slow rows too.
with tempfile.TemporaryDirectory() as d:
    log = pathlib.Path(d) / "testlog.json"
    # And the rows it could not check, with the count: an unprobed row takes
    # no time, so the slowest list cannot show it.
    stdout = ("STALE: nothing\n"
              "UNPROBED (exit 77, cannot be checked here): a row\n"
              "       reads run evidence this clone has not fetched: x\n"
              "TIMING: 106.5 s, 99 row(s) run here; the "
              "slowest:\n    40.00 s  sleep 40\n     1.00 s  true\n"
              "99 runnable check(s), 0 stale, 1 unprobed here; 3 row(s) "
              "carry no command (3 past)\n")
    log.write_text(json.dumps({"name": "cyanrip / Release gate",
                               "stdout": "TIMING: not this one\n"}) + "\n" +
                   json.dumps({"name": "cyanrip / Settled facts",
                               "result": "OK", "duration": 106.55,
                               "stdout": stdout}) + "\n")
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "check-settled.py"),
                        "--timing-from", str(log)], capture_output=True,
                       text=True)
    want = ["Settled facts: OK in 106.5 s",
            "UNPROBED (exit 77, cannot be checked here): a row",
            "       reads run evidence this clone has not fetched: x",
            "TIMING: 106.5 s, 99 row(s) run here; the slowest:",
            "    40.00 s  sleep 40", "     1.00 s  true",
            "99 runnable check(s), 0 stale, 1 unprobed here; 3 row(s) "
            "carry no command (3 past)"]
    if r.returncode != 0 or r.stdout.splitlines() != want:
        fail(f"--timing-from printed {r.stdout.splitlines()!r} (exit "
             f"{r.returncode}), not {want!r}")
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "check-settled.py"),
                        "--timing-from", str(pathlib.Path(d) / "absent.json")],
                       capture_output=True, text=True)
    if r.returncode != 0 or "no testlog" not in r.stdout:
        fail(f"--timing-from on a missing log: exit {r.returncode}, "
             f"{r.stdout!r}")

if failures:
    print(f"{failures} check(s) failed")
    sys.exit(1)
print("ok: the golden checks compare on the reference's library set only, "
      "and check-settled counts what it could not check")
