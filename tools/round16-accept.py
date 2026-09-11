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

"""Grade a round-16 rig run against the close condition. WRITTEN BEFORE THE RUN.

WHY IT EXISTS, AND WHY THE TIMING IS THE POINT. `tools/rig-round16.sh` MEASURES;
it prints numbers for a person to read. Nothing turned those numbers into a
verdict, so the closing lap's §F would have been written by someone looking at
printed text and deciding, afterwards, what counted as a pass.

S-13 fixes a round's close conditions at lap 1 and says they cannot grow. **A
checker written after the results are in is how a close condition quietly
moves** -- not by anyone bending it, but because a criterion is easier to state
once you have seen which way the data went. So this exists before any data does,
and its own git history is the evidence of that.

THE CONDITION, quoted verbatim from round 16 lap 1 §0 and not paraphrased:

    A hardware acceptance run on this pin establishing three things: that the
    AccurateRip path still succeeds with the rewritten response parser; that
    -H together with de-emphasis produces correct de-emphasised audio; and that
    no line you parse has moved except the ones §D names.

THREE RULES IT IS BUILT ON, each one this repository has paid for:

  * A CHECK THAT CANNOT FIRE IS WORSE THAN A MISSING ONE. Every clause reports
    UNPROBED when its evidence is absent, and UNPROBED is never a pass. A rip
    that did not happen must not read like a rip that succeeded.
  * "DID NOT HAPPEN" AND "HAPPENED AND FOUND NOTHING" ARE DIFFERENT CLAIMS.
    AccurateRip reporting `not found` for a track is a real measurement of a
    real query; a missing logfile is not. They get different levels.
  * CHECK THE DATA IS NON-TRIVIAL. Silence compares equal to silence and an
    empty file compares equal to an empty file, and both have read as success
    here before. Clause 2 asserts the two PCM files are non-empty and carry
    non-zero samples BEFORE believing that they differ.

Output is Platterpus's `rig-check` manifest format, adopted verbatim rather than
invented, so a finding can travel as a record instead of as prose:

    LEVEL  category/check  message  [artifact]

    tools/round16-accept.py --out round16-20260907T120000Z
"""

import argparse
import hashlib
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REFERENCE = ROOT / "docs" / "rig-2026-08-05" / "cyanrip.log"

# The two builds whose evidence can close round 16. Both, because
# `git diff a9aedf0..ddc1e8c -- src/ meson.build` is empty: one program, two
# commits. Kept in step with tools/rig-round16.sh's preflight by hand, and the
# test asserts the two agree rather than trusting that.
ROUND16_BUILDS = ("platterpus-fork-gddc1e8c", "platterpus-fork-ga9aedf0")

FINDINGS = []


def note(level, cat, msg, artifact=None):
    FINDINGS.append((level, cat, msg, artifact))


def accurip_lines(text):
    """Every per-track AccurateRip checksum, in order, as (kind, sum, conf).

    `Accurip`, not `AccurateRip` -- the per-track lines are spelled without the
    "ate", and a pattern matching both once returned four lines here when the
    real inventory was twelve, three of which were not checksums at all. The
    disc-level `AccurateRip:` status line is deliberately NOT matched by this.
    """
    out = []
    for m in re.finditer(r"^\s+Accurip (v1|v2|450):\s+([0-9A-F]{8}) \((.*)\)\s*$",
                         text, re.M):
        conf = re.search(r"confidence (\d+)", m.group(3))
        out.append((m.group(1), m.group(2), int(conf.group(1)) if conf else None))
    return out


def read(p):
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def nonzero_fraction(data):
    """What share of 16-bit samples are not zero. Silence must not pass as audio."""
    if not data:
        return 0.0
    n = len(data) // 2
    if not n:
        return 0.0
    nz = sum(1 for i in range(0, n * 2, 2) if data[i] or data[i + 1])
    return nz / n


def check_build(out):
    """Refuse to grade a run from a build that cannot close this round."""
    banner = read(out / "banner.txt")
    if banner is None:
        note("FAIL", "build/banner",
             "no banner.txt -- the run did not record which binary produced it, "
             "so nothing here can be attributed to a build. This is not a "
             "clause failure; it is evidence with no provenance",
             "banner.txt")
        return False
    banner = banner.strip()
    for b in ROUND16_BUILDS:
        if b in banner:
            note("OK", "build/pin", f"{banner}  -- a round-16 build")
            return True
    note("FAIL", "build/pin",
         f"{banner} is neither {ROUND16_BUILDS[0]} nor {ROUND16_BUILDS[1]}. "
         f"The measurements below may be perfectly good and they are NOT "
         f"evidence for round 16", "banner.txt")
    return False


def clause1(out):
    """The AccurateRip path still succeeds with the rewritten response parser."""
    log = out / "accurip" / "accurip.log"
    text = read(log)
    if text is None:
        note("UNPROBED", "clause1/log",
             "no accurip/accurip.log -- the clause-1 rip wrote no logfile. Read "
             f"{out}/accurip.stdout for why. NOT a pass and NOT a failure",
             "accurip.stdout")
        return
    status = re.search(r"^AccurateRip:\s+(\S.*?)\s*$", text, re.M)
    if not status:
        note("FAIL", "clause1/status",
             "the logfile has no `AccurateRip:` line at all, so the query path "
             "did not reach the point of reporting", str(log))
        return
    verdict = status.group(1)
    got = accurip_lines(text)
    if verdict != "found":
        # FIVE VALUES, NOT TWO, and the first version of this lumped four of
        # them into one sentence that said "the parser RAN". It does not run at
        # all for `disabled`, so that sentence was false for the value a
        # misconfigured harness actually produces. Found by running this
        # against a real rip rather than against the fixtures it was written
        # with -- the fixtures only ever produced `found`.
        #
        # cyanrip_log.c:786 is the whole set: error, not found, found,
        # mismatch, disabled.
        if verdict == "disabled":
            # ROUND 16 LAP 12 §C2, AND THE HALF OF IT THEY DID NOT TAKE FAR
            # ENOUGH. `disabled` is the bare `else` of a ternary cascade over
            # `ar_db_status`, whose zero value IS `CYANRIP_ACCUDB_DISABLED`
            # (cyanrip_main.h:67, cyanrip_log.c:786-790 at a9aedf0). So EVERY
            # path that leaves the field unwritten prints it, and there are at
            # least three:
            #
            #   -A                     crip_fill_accurip() returns at once
            #   missing CDDB ID        accurip.c:134, `goto end`, no query made
            #   CONTENT_TYPE getinfo   accurip.c:211, AFTER curl_easy_perform
            #                          returned CURLE_OK -- the query DID run
            #
            # The message that used to be here asserted the FIRST of those as
            # the cause. That is a mechanism the printed value cannot establish
            # -- the same defect one level down from the one their §C2 found,
            # and the first rule in this tree forbids it.
            #
            # It IS distinguishable, but from the argv rather than from the
            # status line, so that is what we read. Absent that, say which two
            # remain and that this cannot choose between them.
            inv = re.search(r"^Invoked as:\s+(.*?)\s*$", text, re.M)
            argv = inv.group(1).split() if inv else None
            if argv is None:
                note("WARN", "clause1/disabled",
                     "`AccurateRip: disabled` and the logfile carries no "
                     "`Invoked as:` line, so this cannot say whether -A was "
                     "passed or whether the query ran and left the status "
                     "unwritten. The clause is UNSETTLED either way", str(log))
            elif "-A" in argv:
                # An exact token after splitting, never a substring: `-A` occurs
                # inside ordinary paths and metadata values, and a pattern that
                # nearly matches is worse than one that does not.
                note("FAIL", "clause1/disabled",
                     "`AccurateRip: disabled` and `-A` IS in `Invoked as:` -- "
                     "read from the logfile, not inferred from the status. The "
                     "query never ran and nothing about the rewritten parser "
                     "was exercised. A harness error, not a result: drop -A "
                     "from the clause-1 rip and run it again", str(log))
            else:
                note("WARN", "clause1/disabled",
                     "`AccurateRip: disabled` with NO -A in `Invoked as:`. The "
                     "status field was left at its zero value by some path "
                     "inside crip_fill_accurip() -- accurip.c:134 (missing "
                     "CDDB ID, no query) and :211 (CONTENT_TYPE getinfo failed "
                     "AFTER a successful transfer, so the query DID run) are "
                     "two of them, and THIS LINE CANNOT TELL THEM APART. Read "
                     "the stdout for the `Unable to get AccuRIP DB data:` "
                     "message, which names the path", str(log))
        elif verdict == "not found":
            note("WARN", "clause1/status",
                 "`AccurateRip: not found`. The parser RAN and the disc is not "
                 "in the database -- a real measurement, and not a failure of "
                 "ours. With no match there is nothing to compare, so the "
                 "clause is UNSETTLED rather than failed. Try a disc that is "
                 "in the database", str(log))
        elif verdict == "mismatch":
            note("WARN", "clause1/status",
                 "`AccurateRip: mismatch` -- the parser RAN and worked; the "
                 "disc was found and our checksums disagree with the "
                 "database. That is a claim about THIS RIP or this pressing, "
                 "not about the parser, and the clause is unsettled either "
                 "way. Read the per-track lines before concluding anything",
                 str(log))
        else:
            note("WARN", "clause1/status",
                 f"`AccurateRip: {verdict}` -- the query failed. Whether the "
                 f"rewritten parser ran at all is NOT established by this: an "
                 f"error can be raised before any response is parsed", str(log))
        note("UNPROBED", "clause1/checksums",
             f"{len(got)} per-track checksum line(s) produced, nothing to "
             f"compare them to")
        return
    note("OK", "clause1/status", "`AccurateRip: found` -- a real response was "
         "parsed by the rewritten parser", str(log))

    ref = read(REFERENCE)
    if ref is None:
        note("UNPROBED", "clause1/compare",
             f"the on-record reference {REFERENCE} is missing, so the checksums "
             f"cannot be compared. The run is fine; this checkout is not")
        return
    want = accurip_lines(ref)
    if not got:
        note("FAIL", "clause1/checksums",
             "`AccurateRip: found` but not one `Accurip v1:/v2:/450:` line was "
             "produced. A status without checksums is the shape a broken "
             "parser makes", str(log))
        return

    # The rig rips fewer tracks than the reference holds, so compare the
    # overlap and SAY how many -- a comparison whose scope is unstated is the
    # defect that shipped "all four lines identical" over an inventory of 12.
    n = min(len(got), len(want))
    bad, rose, fell = [], 0, 0
    for i in range(n):
        gk, gs, gc = got[i]
        wk, ws, wc = want[i]
        if gk != wk or gs != ws:
            bad.append(f"#{i+1} {gk} {gs} != reference {wk} {ws}")
        elif gc is not None and wc is not None:
            if gc > wc:
                rose += 1
            elif gc < wc:
                fell += 1
                bad.append(f"#{i+1} {gk} confidence FELL {wc} -> {gc}")
    if bad:
        note("FAIL", "clause1/checksums",
             f"{len(bad)} of {n} compared line(s) disagree with the reference: "
             + "; ".join(bad[:4]), str(log))
    else:
        note("OK", "clause1/checksums",
             f"all {n} compared checksum(s) identical to "
             f"docs/rig-2026-08-05/cyanrip.log ({len(got)} produced, "
             f"{len(want)} on record, {n} overlap). {rose} confidence(s) rose, "
             f"0 fell -- a rise is the database moving and is expected")


def clause2(out):
    """-H together with de-emphasis produces correct de-emphasised audio."""
    pcm = {}
    for name in ("hdcd-deemph", "hdcd-nodeemph"):
        found = sorted((out / name).glob("*.pcm")) if (out / name).is_dir() else []
        pcm[name] = found[0] if found else None
    if not all(pcm.values()):
        missing = [k for k, v in pcm.items() if not v]
        note("UNPROBED", "clause2/audio",
             f"no .pcm from {', '.join(missing)} -- the pair cannot be compared. "
             f"Read the matching .stdout. NOT a pass")
        return

    data = {k: v.read_bytes() for k, v in pcm.items()}
    # BEFORE believing they differ, believe they are audio. An empty file
    # compares equal to an empty file and silence to silence, and both have
    # read as success in this repository before.
    for k, d in data.items():
        if len(d) < 4096:
            note("FAIL", "clause2/trivial",
                 f"{pcm[k].name} from {k} is {len(d)} bytes -- too small to be "
                 f"a track. A comparison over near-empty files proves nothing",
                 str(pcm[k]))
            return
    fr = {k: nonzero_fraction(d[:400000]) for k, d in data.items()}
    # `min`, NOT `max`. ROUND 16 LAP 12 §C1. With `max` this fires only when
    # NEITHER arm carries audio, so one silent arm beside one real arm sails
    # straight through -- and then PASSES the hash comparison below, because the
    # two hashes differ PRECISELY BECAUSE one of them is silence. A broken
    # `-H -E` that decoded to nothing would have been graded as proof that
    # de-emphasis reached the audio: the exact mirror of `b866900`, which this
    # clause exists to retire, and the one the fixtures could not see.
    quiet = sorted(k for k, v in fr.items() if v < 0.01)
    if quiet:
        # Derived from the count, never a bare `file(s)`. A message that fits
        # both arities describes neither, and this branch's whole job is to say
        # WHICH arm is empty -- the old one could only ever say "both".
        note("FAIL", "clause2/trivial",
             f"{' and '.join(quiet)} "
             f"{'is' if len(quiet) == 1 else 'are'} >=99% silence in the first "
             f"200k samples (-H -E {fr['hdcd-deemph']:.3%}, -H -W "
             f"{fr['hdcd-nodeemph']:.3%}). Silence compares equal to silence, "
             f"and a hash that differs because one side is EMPTY settles "
             f"nothing about de-emphasis")
        return

    # THE SAME CLASS AS §C1, AND THE INSTANCE THEY DID NOT NAME: a hash that
    # differs for a reason that is not de-emphasis. Silence was one; unequal
    # LENGTH is another, and it is not caught above -- a half-truncated arm is
    # neither near-empty nor silent, and its hash differs from the other arm's
    # for a reason this clause is not about.
    #
    # Equal length is a real invariant here, not a hope. Both arms pass `-H`,
    # so both decode to the same width, and `aemphasis` is a biquad -- a
    # filter, sample-count preserving. Two `-o pcm` rips of one track list off
    # one disc differ in length only if something OTHER than the filter graph
    # did it, which is exactly when the comparison stops measuring de-emphasis.
    #
    # What the passing fixtures shared was "same length and both audio". Asking
    # what a set of passing cases has in common is the move that would have
    # found §C1 here rather than in their lap.
    if len(data["hdcd-deemph"]) != len(data["hdcd-nodeemph"]):
        note("FAIL", "clause2/trivial",
             f"the two arms are different LENGTHS: -H -E "
             f"{len(data['hdcd-deemph'])} bytes, -H -W "
             f"{len(data['hdcd-nodeemph'])}. De-emphasis is a filter and "
             f"preserves sample count, so this difference was produced by "
             f"something else and the hashes below cannot be about "
             f"de-emphasis. Read both .stdout files", str(pcm["hdcd-deemph"]))
        return

    h = {k: hashlib.md5(d).hexdigest() for k, d in data.items()}
    if h["hdcd-deemph"] == h["hdcd-nodeemph"]:
        note("FAIL", "clause2/differ",
             f"-H -E and -H -W produced BYTE-IDENTICAL decoded samples "
             f"({h['hdcd-deemph']}). De-emphasis did not reach the audio -- "
             f"this is exactly the defect the filter-composition fix was for",
             str(pcm["hdcd-deemph"]))
        return
    note("OK", "clause2/differ",
         f"decoded samples differ: -H -E {h['hdcd-deemph']}, -H -W "
         f"{h['hdcd-nodeemph']}. These are raw interleaved samples, not "
         f"containers, so there is no creation_time to explain it away and no "
         f"decoder in the path")
    note("INFO", "clause2/content",
         f"non-zero samples: -H -E {fr['hdcd-deemph']:.1%}, "
         f"-H -W {fr['hdcd-nodeemph']:.1%} -- both carry audio")


def clause3(out):
    """No line a consumer parses has moved, except the ones lap 1 §D names."""
    rec = out / "plain.json"
    raw = read(rec)
    if raw is None:
        note("UNPROBED", "clause3/record",
             "no plain.json -- the -j record was not written. If the plain-j "
             "rip timed out, that IS the C1 reproduction and is a finding",
             "plain-j.stdout")
    else:
        try:
            d = json.loads(raw)
        except ValueError as e:
            note("FAIL", "clause3/record", f"plain.json is not JSON: {e}", str(rec))
            d = None
        if d is not None:
            schema = d.get("schema")
            if schema != "cyanrip-diagnostics/4":
                note("FAIL", "clause3/schema",
                     f"schema is {schema!r}, expected 'cyanrip-diagnostics/4' -- "
                     f"lap 1 §D announced this move and a consumer allowlists it",
                     str(rec))
            else:
                note("OK", "clause3/schema", "cyanrip-diagnostics/4")
            for f in ("started_at", "finished_at"):
                if not d.get(f):
                    note("FAIL", "clause3/instants",
                         f"{f} absent or empty. Two instants are carried because "
                         f"event time and processing time are different ages",
                         str(rec))
                else:
                    note("OK", f"clause3/{f}", str(d[f]))

    logs = sorted(p for p in out.rglob("*.log"))
    if not logs:
        note("UNPROBED", "clause3/logs", "no logfiles anywhere under the run")
        return
    banner_bad, zre, ure = [], 0, 0
    for p in logs:
        t = read(p) or ""
        first = t.splitlines()[0] if t.splitlines() else ""
        if "platterpus-fork" not in first:
            banner_bad.append(p.name)
        if re.search(r"^\s+Secure re-read:", t, re.M):
            zre += 1
        if re.search(r"^Consumer:", t, re.M):
            ure += 1
    if banner_bad:
        note("FAIL", "clause3/banner",
             f"{len(banner_bad)} logfile(s) do not open with the fork banner: "
             f"{', '.join(banner_bad[:3])}. PROJECT_FORK_ID in the first line is "
             f"the only reliable answer to 'is this the fork?'")
    else:
        note("OK", "clause3/banner",
             f"all {len(logs)} logfile(s) open with the fork banner")
    note("OK" if zre else "FAIL", "clause3/secure-reread",
         f"`Secure re-read:` present in {zre} of {len(logs)} logfile(s)"
         + ("" if zre else " -- without -Z the converged/not-converged arm is "
                           "never emitted and the clause cannot show it unmoved"))
    note("OK" if ure else "FAIL", "clause3/consumer",
         f"`Consumer:` present in {ure} of {len(logs)} logfile(s)"
         + ("" if ure else " -- without -u the log is one header line shorter "
                           "than the reference it is compared against"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, help="the rig run's $OUT directory")
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    if not out.is_dir():
        sys.exit(f"{out} is not a directory")

    graded = check_build(out)
    clause1(out)
    clause2(out)
    clause3(out)

    fails = unprobed = 0
    for level, cat, msg, artifact in FINDINGS:
        line = f"{level:<9} {cat:<22} {msg}"
        if artifact:
            line += f"  [{artifact}]"
        print(line)
        fails += level == "FAIL"
        unprobed += level == "UNPROBED"

    print()
    if not graded:
        print("THIS RUN CANNOT CLOSE ROUND 16 -- see build/ above. Whatever the "
              "clauses say,\nthe evidence is not attributable to a round-16 build.")
    print(f"{fails} FAIL, {unprobed} UNPROBED.")
    if unprobed:
        print("UNPROBED IS NOT A PASS. A clause whose evidence is absent is "
              "unsettled, and\nsaying so is the difference between 'did not "
              "happen' and 'happened and found\nnothing'.")
    if not fails and not unprobed and graded:
        print("All three clauses settled by this run.")

    # THREE EXIT CODES, BECAUSE THERE ARE THREE OUTCOMES. The first version
    # returned 0 here whenever nothing FAILED -- so a run with an unsettled
    # clause exited 0 and read as a pass to any caller checking the code, while
    # the text above it said in capitals that UNPROBED is not a pass. The prose
    # disclaimed and the exit code asserted, and the exit code is what a script
    # reads. Caught by tests/round16_accept.py, which is what it is for.
    #
    # Seam rule S-12 says an error code that distinguishes nothing is a defect
    # row rather than a datum. "A clause said no" and "a clause could not be
    # asked" are different answers to a round and get different codes.
    if not graded or fails:
        return 1                      # failed, or not attributable to the pin
    if unprobed:
        return 2                      # nothing failed; the round is UNSETTLED
    return 0                          # all three clauses settled and passed


if __name__ == "__main__":
    sys.exit(main())
