#!/usr/bin/env python3
"""Every way tools/round16-accept.py could wrongly say a round-16 run passed.

THE CHECKER IS THE THING UNDER TEST, not the rig. It grades a close condition,
so a bug in it either closes a round on evidence that does not support the claim
or refuses one that does -- and both are worse than having no checker, because
a verdict carries authority a printed number does not.

There is no drive here and there never will be, so every fixture is BUILT: a
synthetic $OUT that passes, and then one mutation at a time. That is the only
way to know a check can fire. Three of this repository's sharpest defects were
checks that could not -- three `if "runtime error" in out` assertions against a
binary with no sanitizer symbols, a substring search satisfied by the document
being wrong, and a `sectors?` pattern that matched both arms of the branch it
was written for.

UNPROBED IS ASSERTED AS CAREFULLY AS FAIL. "The evidence is absent" and "the
evidence says no" are different claims about a round, and a checker that
collapses them lets a rip that never happened read like one that succeeded.
"""

import pathlib
import re
import subprocess
import struct
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "round16-accept.py"
REFERENCE = ROOT / "docs" / "rig-2026-08-05" / "cyanrip.log"

failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


def run(out):
    r = subprocess.run([sys.executable, str(TOOL), "--out", str(out)],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=120)
    return r.returncode, r.stdout.decode(errors="replace")


def audio(seed, n=200000):
    """Non-silent 16-bit stereo. Silence compares equal to silence."""
    return b"".join(struct.pack("<hh", (i * 37 + seed) % 20000 - 10000,
                                (i * 53 + seed) % 20000 - 10000)
                    for i in range(n // 4))


def logfile(name, extra=""):
    return (f"cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-gddc1e8c)\n"
            f"Invoked as:     /usr/local/bin/cyanrip -d /dev/sr0\n"
            f"Consumer:       cyanrip-rig/round-16\n"
            f"Track 1:\n"
            f"    Secure re-read:  converged after 3 reads\n"
            f"{extra}"
            f"Rip completed:  yes (1 of 14 tracks)\n"
            f"Log FUN512: {name}\n")


def build(root):
    """A synthetic $OUT that must pass every clause."""
    out = pathlib.Path(root)
    (out / "banner.txt").write_text(
        "cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-gddc1e8c)\n")

    # clause 1: the first three reference checksum lines, reproduced exactly.
    ref = REFERENCE.read_text(errors="replace")
    lines = re.findall(r"^\s+Accurip (?:v1|v2|450):.*$", ref, re.M)[:3]
    (out / "accurip").mkdir()
    (out / "accurip" / "accurip.log").write_text(
        logfile("accurip", "AccurateRip:    found\n" + "\n".join(lines) + "\n"))

    # clause 2: two files that differ and are both audio.
    for name, seed in (("hdcd-deemph", 1), ("hdcd-nodeemph", 2)):
        (out / name).mkdir()
        (out / name / "1.pcm").write_bytes(audio(seed))
        (out / name / f"{name}.log").write_text(logfile(name))

    # clause 3.
    (out / "plain.json").write_text(
        '{"schema": "cyanrip-diagnostics/4",'
        ' "started_at": "2026-09-07T12:00:00+00:00",'
        ' "finished_at": "2026-09-07T12:01:00+00:00", "exit_code": 0}')
    (out / "plain").mkdir()
    (out / "plain" / "plain.log").write_text(logfile("plain"))
    return out


def expect(label, mutate, want_rc, want_re, want_absent=None):
    """Mutate a passing fixture one way and assert the checker notices.

    want_rc is 1 for "a clause said no" and 2 for "a clause could not be
    asked". They are different answers to a round and the checker must not
    collapse them -- its first version exited 0 on every UNPROBED, so an
    unsettled clause read as a pass to anything reading the code while the
    text above said the opposite.
    """
    with tempfile.TemporaryDirectory() as td:
        out = build(td)
        mutate(out)
        rc, txt = run(out)
        if want_rc is not None and rc != want_rc:
            fail(f"{label}: exit {rc}, expected {want_rc}\n{txt}")
            return
        if want_re and not re.search(want_re, txt):
            fail(f"{label}: nothing matched /{want_re}/\n{txt}")
            return
        if want_absent and re.search(want_absent, txt):
            fail(f"{label}: /{want_absent}/ appeared and must not\n{txt}")


def main():
    # 0. The baseline must PASS. Without this every mutation below is
    #    meaningless -- a checker that always fails also "detects" everything.
    with tempfile.TemporaryDirectory() as td:
        out = build(td)
        rc, txt = run(out)
        if rc != 0:
            fail(f"the passing fixture does not pass (exit {rc})\n{txt}")
        elif "All three clauses settled by this run." not in txt:
            fail(f"the passing fixture passed without saying so\n{txt}")

    # 1. Provenance. A run from another build must not be graded as round-16
    #    evidence however good its numbers are.
    expect("wrong build",
           lambda o: (o / "banner.txt").write_text(
               "cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-g978f9b0)\n"),
           1, r"CANNOT CLOSE ROUND 16")
    expect("no banner", lambda o: (o / "banner.txt").unlink(),
           1, r"FAIL.*build/banner")

    # 2. Clause 1. Absence is UNPROBED and must never read as a pass.
    expect("clause 1 log missing",
           lambda o: (o / "accurip" / "accurip.log").unlink(),
           2, r"UNPROBED.*clause1/log", r"All three clauses settled")
    expect("clause 1 checksum differs",
           lambda o: (o / "accurip" / "accurip.log").write_text(
               (o / "accurip" / "accurip.log").read_text()
               .replace("5D3C90CB", "DEADBEEF")),
           1, r"FAIL.*clause1/checksums")
    expect("clause 1 confidence FELL",
           lambda o: (o / "accurip" / "accurip.log").write_text(
               (o / "accurip" / "accurip.log").read_text()
               .replace("confidence 129", "confidence 3")),
           1, r"confidence FELL")
    # THE FIVE VALUES cyanrip_log.c:786 CAN PRINT, each asserted separately.
    # The checker's first version collapsed four of them into one sentence
    # claiming "the parser RAN", which is FALSE for `disabled` -- the value a
    # misconfigured harness actually produces. It was found by running the
    # checker against a real rip, because every fixture here produced `found`.
    # An example suite only finds the cases someone thought of.
    def verdict(v):
        return lambda o: (o / "accurip" / "accurip.log").write_text(
            (o / "accurip" / "accurip.log").read_text()
            .replace("AccurateRip:    found", f"AccurateRip:    {v}"))

    # `not found`: the parser RAN and the disc is not in the database. A real
    # measurement, not our failure, and still cannot settle the clause.
    expect("clause 1 not found is unsettled, not failed", verdict("not found"),
           2, r"parser RAN and the disc is not in the database")
    # `disabled`: THIS CASE USED TO ASSERT THE DEFECT. It read "the query never
    # ran at all. -A reached the one rip that must not have it, which is a
    # harness error" and demanded exit 1 -- pinning, as a requirement, the
    # claim round 16 lap 12 §C2 disproved. A test written from the same wrong
    # premise as the code cannot catch the code; it makes the defect harder to
    # remove. The base fixture's argv carries no `-A`, so the honest grade is
    # UNSETTLED, and the four cases below assert the distinction properly.
    expect("clause 1 disabled on the base fixture is UNSETTLED, not a harness error",
           verdict("disabled"), 2, r"WARN.*clause1/disabled",
           r"because -A was passed")
    # `mismatch`: the parser worked; the disc was found and the checksums
    # disagree. A claim about the rip, not about the parser.
    expect("clause 1 mismatch is about the rip, not the parser",
           verdict("mismatch"), 2, r"parser RAN and worked")
    # `error`: whether the parser ran at all is NOT established.
    expect("clause 1 error establishes nothing about the parser",
           verdict("error"), 2, r"NOT established")
    # And none of the four may be mistaken for the passing case.
    for v in ("not found", "disabled", "mismatch", "error"):
        expect(f"clause 1 {v} is never a pass", verdict(v),
               None, None, r"All three clauses settled")

    # RUN A, 2026-09-11. The 2026-08-05 reference's track 3 reads "not found,
    # either a new pressing, or bad rip" -- no confidence. That night's rip of
    # the same track came back accurately ripped at confidence 128. The checker
    # called that a disagreement and FAILED: it graded the BETTER rip as a
    # regression against a line the database never recognised, and would have
    # held the round closed on it.
    #
    # The fixture reproduces the shape exactly -- six of our lines against the
    # reference's first six, where the reference's 5th and 6th are the NOT
    # FOUND ones and ours carry confidences.
    ref_lines = re.findall(r"^\s+Accurip (?:v1|v2|450):.*$",
                           REFERENCE.read_text(errors="replace"), re.M)[:6]
    unrecognised = [l for l in ref_lines if "confidence" not in l]
    if len(unrecognised) != 2:
        fail(f"the reference no longer has exactly 2 unrecognised lines in its "
             f"first six ({len(unrecognised)}); this case needs rewriting "
             f"against whatever it has now")
    else:
        ours = [re.sub(r"\(not found[^)]*\)",
                       "(accurately ripped, confidence 128)", l).replace(
                    "DCA378E8", "3C8BDDD2").replace("36F6EA91", "96DF8C22")
                for l in ref_lines]

        def six(o):
            log = o / "accurip" / "accurip.log"
            body = log.read_text()
            head = body.split("AccurateRip:    found")[0]
            log.write_text(head + "AccurateRip:    found\n"
                           + "\n".join(ours) + "\n"
                           + "Rip completed:  yes (3 of 14 tracks)\n"
                           + "Log FUN512: x\n")

        with tempfile.TemporaryDirectory() as td:
            out = build(td)
            six(out)
            rc, txt = run(out)
            if re.search(r"FAIL.*clause1/checksums", txt):
                fail("our recognised checksum disagreeing with an UNRECOGNISED "
                     f"reference line was graded a failure\n{txt}")
            if not re.search(r"INFO.*clause1/reference", txt):
                fail(f"the unusable reference lines were not reported at all -- "
                     f"silence is not the fix either\n{txt}")
            if "NOT FOUND by the database" not in txt:
                fail(f"the row does not say WHY the reference is unusable\n{txt}")

    # 3. Clause 2, including the two ways a comparison lies.
    expect("clause 2 identical audio",
           lambda o: (o / "hdcd-nodeemph" / "1.pcm").write_bytes(
               (o / "hdcd-deemph" / "1.pcm").read_bytes()),
           1, r"FAIL.*clause2/differ")
    expect("clause 2 silence",
           lambda o: [(o / n / "1.pcm").write_bytes(b"\0" * 200000)
                      for n in ("hdcd-deemph", "hdcd-nodeemph")],
           1, r"FAIL.*clause2/trivial.*hdcd-deemph and hdcd-nodeemph are")

    # ROUND 16 LAP 12 §C1, AND THE CASE THAT MADE THE DEFECT INVISIBLE. The
    # gate was `max(fr.values()) < 0.01`, which fires only when NEITHER arm has
    # audio -- and "neither" is the one case the fixture above builds. One
    # silent arm beside one real arm sailed through, and then PASSED, because
    # the two hashes differ PRECISELY BECAUSE one of them is silence. A broken
    # `-H -E` decoding to nothing would have been graded as proof that
    # de-emphasis reached the audio.
    #
    # Both arms get their own case. A gate written to look at one key passes
    # whichever one the single fixture happens to use, and which arm goes
    # silent is not something a rig run gets to choose.
    for silent, other in (("hdcd-deemph", "hdcd-nodeemph"),
                          ("hdcd-nodeemph", "hdcd-deemph")):
        expect(f"clause 2 ONLY {silent} is silent",
               lambda o, s=silent: (o / s / "1.pcm").write_bytes(b"\0" * 200000),
               1, rf"FAIL.*clause2/trivial.*\b{silent} is\b",
               # THE HARM, asserted directly: without this the checker reports
               # the two arms differing as a clause-2 PASS.
               r"OK.*clause2/differ")

    # The message must say WHICH arm, and a message that fits both arities
    # describes neither -- `sectors?` matching `sector` and `sectors` alike is
    # the precedent, and it killed none of the three mutants it was for. So the
    # single-arm case must NOT name the arm that still has audio.
    expect("clause 2 one-arm message does not name the loud arm",
           lambda o: (o / "hdcd-deemph" / "1.pcm").write_bytes(b"\0" * 200000),
           1, r"clause2/trivial.*hdcd-deemph is\b",
           r"clause2/trivial.*hdcd-deemph and hdcd-nodeemph")
    expect("clause 2 near-empty",
           lambda o: (o / "hdcd-deemph" / "1.pcm").write_bytes(b"\1\2" * 8),
           1, r"FAIL.*clause2/trivial")
    expect("clause 2 no pcm at all",
           lambda o: (o / "hdcd-deemph" / "1.pcm").unlink(),
           2, r"UNPROBED.*clause2/audio", r"All three clauses settled")

    # ROUND 16 LAP 12 §C2. `disabled` is the ZERO-VALUE FALLTHROUGH of the
    # ternary at cyanrip_log.c:786, over a field whose zero is
    # CYANRIP_ACCUDB_DISABLED -- so every path leaving it unwritten prints it,
    # including accurip.c:211, reached AFTER curl_easy_perform returned
    # CURLE_OK. The message here used to assert `-A` as the cause, which the
    # status line cannot establish. It IS readable, from the argv.
    def disable(o, invoked=None):
        log = o / "accurip" / "accurip.log"
        txt = log.read_text().replace("AccurateRip:    found",
                                      "AccurateRip:    disabled")
        if invoked is None:
            txt = "\n".join(l for l in txt.splitlines()
                             if not l.startswith("Invoked as:")) + "\n"
        else:
            txt = re.sub(r"(?m)^Invoked as:.*$", f"Invoked as:     {invoked}", txt)
        log.write_text(txt)

    expect("clause 1 disabled WITH -A in the argv",
           lambda o: disable(o, "/usr/local/bin/cyanrip -d /dev/sr0 -N -A -U"),
           1, r"FAIL.*clause1/disabled.*`-A` IS in `Invoked as:`")

    # The one that matters: -A absent. The old message would have reported a
    # harness error that did not happen, and named a cause it cannot know.
    expect("clause 1 disabled with NO -A",
           lambda o: disable(o, "/usr/local/bin/cyanrip -d /dev/sr0 -N -U"),
           2, r"WARN.*clause1/disabled.*NO -A in `Invoked as:`",
           r"because -A was passed")

    # -A must be matched as a TOKEN. It occurs inside ordinary paths, and a
    # pattern that nearly matches is worse than one that does not.
    expect("clause 1 disabled where -A is only a substring",
           lambda o: disable(o, "/usr/local/bin/cyanrip -d /dev/sr0 -N -U "
                                "-D /home/rig/OUT-Archive -a album=SIDE-Α"),
           2, r"WARN.*clause1/disabled.*NO -A in `Invoked as:`",
           r"`-A` IS in")

    expect("clause 1 disabled with no Invoked as: line at all",
           lambda o: disable(o, None),
           2, r"WARN.*clause1/disabled.*no `Invoked as:` line",
           r"because -A was passed")

    # The mirror of §C1 that their lap did not name: a hash differing for a
    # reason that is not de-emphasis. A truncated arm is neither near-empty nor
    # silent, so neither guard above sees it -- and the hashes differ.
    expect("clause 2 one arm TRUNCATED",
           lambda o: (o / "hdcd-nodeemph" / "1.pcm").write_bytes(audio(2)[:100000]),
           1, r"FAIL.*clause2/trivial.*different LENGTHS",
           r"OK.*clause2/differ")

    # 4. Clause 3.
    expect("clause 3 old schema",
           lambda o: (o / "plain.json").write_text(
               (o / "plain.json").read_text().replace("/4", "/3")),
           1, r"FAIL.*clause3/schema")
    expect("clause 3 no started_at",
           lambda o: (o / "plain.json").write_text(
               (o / "plain.json").read_text().replace(
                   '"started_at": "2026-09-07T12:00:00+00:00",', "")),
           1, r"FAIL.*clause3/instants")
    expect("clause 3 no record",
           lambda o: (o / "plain.json").unlink(),
           2, r"UNPROBED.*clause3/record", r"All three clauses settled")
    expect("clause 3 no Secure re-read",
           lambda o: [p.write_text(p.read_text().replace(
               "    Secure re-read:  converged after 3 reads\n", ""))
               for p in o.rglob("*.log")],
           1, r"FAIL.*clause3/secure-reread")
    expect("clause 3 no Consumer",
           lambda o: [p.write_text(p.read_text().replace(
               "Consumer:       cyanrip-rig/round-16\n", ""))
               for p in o.rglob("*.log")],
           1, r"FAIL.*clause3/consumer")
    expect("clause 3 foreign banner",
           lambda o: (o / "plain" / "plain.log").write_text("cyanrip 0.9.3\n"),
           1, r"FAIL.*clause3/banner")

    # 5. TWO DESCRIPTIONS OF ONE FACT, so they must be checked against each
    #    other. The accepted builds live in the checker AND in the rig script's
    #    preflight, and a run graded by one and gated by the other is exactly
    #    the two-implementations-drift this seam already suffered.
    tool = TOOL.read_text()
    script = (ROOT / "tools" / "rig-round16.sh").read_text()
    # COUNT WHAT THE PATTERN RETURNED. The first version spelled this
    # `[0-9a-f]+`, so drifting a build id to `gCAFEBAB` matched NOTHING, the
    # loop ran zero times, and the check passed while the two files disagreed
    # -- a pattern that nearly matches, in the test written to catch exactly
    # that class of defect. Asserting the count is what makes it fire.
    ids = re.findall(r'"(platterpus-fork-g[0-9A-Za-z]+)"', tool)
    if len(ids) != 2:
        fail(f"expected 2 accepted build ids in the checker, found {len(ids)}: "
             f"{ids}. A cross-check over an empty list passes vacuously")
    for build_id in ids:
        if build_id.replace("platterpus-fork-", "") not in script:
            fail(f"{build_id} is accepted by the checker and is not in "
                 f"rig-round16.sh's preflight -- one of them is wrong")

    print(f"{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
