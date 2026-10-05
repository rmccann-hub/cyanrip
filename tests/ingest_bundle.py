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
import os
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


def test_a_clean_transcript_names_what_it_read():
    """Round 28 lap 2 S19-S20 (Platterpus): a clean result printed over nothing.

    An empty transcript printed `no [ FAIL ] lines`, word for word what a
    whole clean run prints, and with no report.json nothing else was said.
    """
    rc, out = run(make({"session/transcript.txt": b""}), "--verdict-only")
    check("no [ FAIL ] lines" not in out,
          f"an empty transcript must not read as a clean one: {out[:300]}")
    check("EMPTY, 0 byte(s)" in out, f"it must say it is empty: {out[:300]}")
    check("is NOT 'the run passed'" in out,
          f"with no `ok` anywhere it must say nothing asserts a pass: {out[:300]}")
    rc, out = run(make({"session/transcript.txt": b"a\nb\nc\n"}), "--verdict-only")
    check("no [ FAIL ] lines in 3 line(s)" in out,
          f"a clean transcript must name how many lines it read: {out[:300]}")


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


ROOT = HERE.parent
BANNER19 = b"cyanrip 0.9.4-rc2+platterpus.19 (platterpus-fork-g174a134)\n"
BANNER18 = b"cyanrip 0.9.4-rc2+platterpus.18 (platterpus-fork-g51cc789)\n"


def pair_bundle(started, banner, app="0.6.65", steps=None):
    report = {"ok": True, "app_version": app}
    if started:
        report["started_at"] = started
    if steps is not None:
        report["steps"] = [{"elapsed_s": s} for s in steps]
    return make({
        "session/script-report.json": json.dumps(report).encode(),
        "session/rig-check-ripper-version.txt": banner,
        "rips/a.log": banner + b"Rip completed:  yes (14 of 14 tracks)\n",
    })


def pair_lines(out):
    return [l for l in out.splitlines() if l.startswith("  cyanrip:")
            or l.startswith("  app:") or l.startswith("  run ")]


def peer_repo():
    """A stand-in for their tree: two tags, dated as their real ones are."""
    d = pathlib.Path(tempfile.mkdtemp()) / "peer"
    d.mkdir()
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(["git", "init", "-q", str(d)], check=True, env=env)
    for tag, stamp in (("v0.6.64", "2026-09-29T20:00:00+00:00"),
                       ("v0.6.65", "2026-09-30T02:51:29+00:00")):
        e = dict(env, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
        subprocess.run(["git", "-C", str(d), "commit", "-q", "--allow-empty",
                        "-m", tag], check=True, env=e)
        subprocess.run(["git", "-C", str(d), "tag", tag], check=True, env=e)
    return d


def test_the_pair_is_judged_against_the_ledgers_own_history():
    """Round 30 D3, C4: the report says whether the pair was the newest.

    Our side is read from the commits that added each ledger row, so these
    expectations are facts of this repository's history: `.19`'s row was
    added by 7677b3f at 2026-09-30T00:52:10Z, and `.18`'s on 2026-09-28.
    """
    if not (ROOT / ".git").exists():
        print("UNPROBED: not a git checkout, so the ledger has no history")
        return
    rc, out = run(pair_bundle("2026-09-30T03:07:05+00:00", BANNER19),
                  "--verdict-only")
    lines = "\n".join(pair_lines(out))
    check("cyanrip: NEWEST -- ran 0.9.4-rc2+platterpus.19 at 174a134" in lines,
          f".19 at the Full run's start is the newest release: {lines}")
    check("7677b3f" in lines, f"it must name the commit that published it: {lines}")

    rc, out = run(pair_bundle("2026-09-30T03:07:05+00:00", BANNER18),
                  "--verdict-only")
    lines = "\n".join(pair_lines(out))
    check("cyanrip: STALE" in lines and "0.9.4-rc2+platterpus.19 at 174a134" in lines,
          f".18 after .19 was published is stale, naming the newer: {lines}")

    rc, out = run(pair_bundle("2026-09-29T12:00:00+00:00", BANNER18),
                  "--verdict-only")
    lines = "\n".join(pair_lines(out))
    check("cyanrip: NEWEST -- ran 0.9.4-rc2+platterpus.18" in lines,
          f".18 before .19 existed is the newest: {lines}")
    check("SUPERSEDED" not in lines, f"with no step times there is no end: {lines}")

    # D3's own case, in shape: newest at the start, overtaken before the end.
    rc, out = run(pair_bundle("2026-09-29T20:00:00+00:00", BANNER18,
                              steps=[3600.0] * 6), "--verdict-only")
    lines = "\n".join(pair_lines(out))
    check("cyanrip: NEWEST -- ran 0.9.4-rc2+platterpus.18" in lines
          and "cyanrip: SUPERSEDED DURING THE RUN -- 0.9.4-rc2+platterpus.19" in lines,
          f"a release published mid-run must be named: {lines}")

    rc, out = run(pair_bundle("2026-09-30T03:07:05+00:00",
                              b"cyanrip 0.9.4-rc2+platterpus.19 (platterpus-fork-g1234567)\n"),
                  "--verdict-only")
    check("cyanrip: NOT A RELEASE" in out, f"an unreleased build is named as one: {out[-600:]}")


def test_an_unestablished_pair_is_never_newest():
    """`unknown (reason)`, never newest: no start, no banner, no peer."""
    rc, out = run(pair_bundle(None, BANNER19), "--verdict-only")
    check("run start: unknown" in out, f"no started_at must be named: {out[-600:]}")
    check("NEWEST" not in out, f"nothing is newest without a start: {out[-600:]}")
    a = make({"session/script-report.json": json.dumps(
        {"ok": True, "started_at": "2026-09-30T03:07:05+00:00"}).encode()})
    rc, out = run(a, "--verdict-only")
    check("cyanrip: unknown" in out and "app: unknown" in out,
          f"no banner and no app version must each be unknown: {out[-600:]}")
    rc, out = run(pair_bundle("2026-09-30T03:07:05+00:00", BANNER19),
                  "--verdict-only")
    check("app: ran 0.6.65; unknown whether newest (no --peer" in out,
          f"without their tree the app cannot be judged: {out[-600:]}")
    two = make({
        "session/script-report.json": json.dumps(
            {"ok": True, "started_at": "2026-09-30T03:07:05+00:00"}).encode(),
        "rips/a.log": BANNER19, "rips/b.log": BANNER18})
    rc, out = run(two, "--verdict-only")
    check("the bundle ran 2 builds" in out, f"two rippers are not one pair: {out[-600:]}")


def test_the_app_is_judged_against_their_tags():
    peer = peer_repo()
    rc, out = run(pair_bundle("2026-09-30T03:07:05+00:00", BANNER19, "0.6.65"),
                  "--verdict-only", "--peer", str(peer))
    check("app: NEWEST -- ran 0.6.65, tag v0.6.65" in out,
          f"0.6.65 after its tag is the newest: {out[-600:]}")
    rc, out = run(pair_bundle("2026-09-30T03:07:05+00:00", BANNER19, "0.6.64"),
                  "--verdict-only", "--peer", str(peer))
    check("app: STALE -- ran 0.6.64; v0.6.65" in out,
          f"0.6.64 after 0.6.65 was tagged is stale: {out[-600:]}")
    rc, out = run(pair_bundle("2026-09-30T01:00:00+00:00", BANNER19, "0.6.64",
                              steps=[3600.0] * 4),
                  "--verdict-only", "--peer", str(peer))
    check("app: NEWEST -- ran 0.6.64" in out
          and "app: SUPERSEDED DURING THE RUN -- v0.6.65" in out,
          f"a tag dated mid-run must be named: {out[-600:]}")
    rc, out = run(pair_bundle("2026-09-30T03:07:05+00:00", BANNER19, "0.6.99"),
                  "--verdict-only", "--peer", str(peer))
    check("app: NOT A RELEASE" in out, f"an untagged app is named as one: {out[-600:]}")


def test_the_banner_is_read_where_a_raw_bundle_keeps_it():
    """The 2026-10-04 runs: a banner the reader could not find, read as absent.

    Two runs stopped at section E before any rip, so they hold no log and no
    rig-check, and the reader printed `cyanrip: unknown (...), which is NOT
    newest` -- while section A's `cyanrip --version` step had relayed the banner
    into the transcript. A third probe path was missed too: the version probe
    is `rig-check-ripper-version.txt` once we file it and
    `session/run/rig-check/ripper-version.txt` in their tarball.

    So: the raw probe is read; a transcript line that IS the banner is read,
    with or without `output: `; a line that only NAMES a build in prose is
    not, since the transcript and DIAGNOSTICS both mention the approved pair;
    and unknown says it cannot be shown newest, which is not a claim that it
    is not.
    """
    start = {"ok": False, "started_at": "2026-10-04T15:20:45+00:00"}
    raw = make({
        "session/run/report.json": json.dumps(start).encode(),
        "session/run/rig-check/ripper-version.txt": BANNER19,
    })
    rc, out = run(raw, "--verdict-only")
    check("ran 0.9.4-rc2+platterpus.19 at 174a134" in out,
          f"the raw tarball's version probe must be read: {out[-600:]}")
    transcript = (
        b"[  ok  ] L274  cyanrip --version   (0.4s)\n"
        b"           exit: 0\n"
        b"           " + BANNER19 +
        b"             [in-container binary] exits\n"
        b"               output: " + BANNER19 +
        b"           INFO  ripper/version  cyanrip 0.9.4-rc2+platterpus.18 "
        b"(platterpus-fork-g51cc789)  [ripper-version.txt]\n"
        b"Approved pair: Platterpus 0.6.63 + cyanrip 0.9.4-rc2+platterpus.18 "
        b"(platterpus-fork-g51cc789) -- verified by handshake round 29.\n"
    )
    only = make({
        "session/run/report.json": json.dumps(start).encode(),
        "session/transcript.txt": transcript,
    })
    rc, out = run(only, "--verdict-only")
    check("ran 0.9.4-rc2+platterpus.19 at 174a134" in out,
          f"a transcript's relayed banner must be read: {out[-600:]}")
    check("2 builds" not in out and "51cc789" not in out,
          f"a build named in prose is not a build that ran: {out[-600:]}")
    none = make({"session/run/report.json": json.dumps(start).encode(),
                 "session/transcript.txt": b"[  ok  ] L1  log hello\n"})
    rc, out = run(none, "--verdict-only")
    check("cyanrip: unknown" in out and "cannot be shown newest" in out
          and "NOT newest" not in out,
          f"no banner anywhere is unknown, not a negative: {out[-600:]}")


for name, fn in sorted(globals().items()):
    if name.startswith("test_") and callable(fn):
        fn()

if failures:
    print(f"{failures} check(s) failed", file=sys.stderr)
    sys.exit(1)
print("all ingest-bundle checks passed")
