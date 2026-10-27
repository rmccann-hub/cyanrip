#!/usr/bin/env python3
"""Black-box probe of cyanrip's own argument surface.

Seam-rules S-9: each side establishes its limits by **running its own binary**,
not by reading the other's documentation, and not by reading its own source. A
range transcribed from a `GEN_OPT_*` line is a claim about behaviour nobody ran;
this file runs it.

What it establishes per argument, which is what S-9 asks for:

    valid range     the real accepted min and max
    boundary        at min, at max, and one past each
    on a bad value  exit code, the distinguishing message, and -- the part that
                    matters most -- whether the operation DIES or the flag is
                    SILENTLY IGNORED
    interactions    mutual exclusions, probed as real invocations
    zero/empty      because 0 so often means "auto"

Outcomes are classified from what the binary did, never from what it should
have done:

    refused     non-zero exit; the run died. The message is recorded verbatim
    crashed     killed by a signal -- NOT a refusal, however much the exit code
                looks like one. This class was added in round 7 lap 32 after
                the script graded four segfaults (-c /, -c //, -p =, -p ==) as
                clean refusals and printed "0 silently ignored" in the same run
    accepted    exit 0 AND the value is visible in the header, so it took effect
    unobservable  exit 0, and no header line exposes this flag's value, so
                whether it took effect was NOT observed. It was graded
                `accepted` until 2026-09-27, and three quarters of the accepted
                rows were this: the summary then said every value "took
                effect" over rows nobody saw take effect
                (docs/history/KNOWN-ISSUES-2026-10-21.md, seam-commands row 1). It is not a finding, and the gate does not
                fire on it; it is a gap in what this probe can see.
    ignored     exit 0 and the value is NOT visible -- a silently dropped
                argument, which is the outcome S-9 most wants written down
    n/a         the probe could not be run here; the row says why

**A blank reads as "tested and fine", so there are none.** Where a limit needs a
drive this prints `not-probed: <reason>` rather than nothing.

Usage:
    tools/probe-argv-surface.py --binary build/src/cyanrip [--markdown]
    tools/probe-argv-surface.py --gate      # non-zero if anything is silently ignored

The gate is the point, not the table. A CI failure when a non-default value
vanishes without a refusal is what keeps this honest between rounds; the
markdown is a rendering of the same run.
"""

import argparse
import os
import pathlib
import re
import shutil
import concurrent.futures
import json
import subprocess
import sys
import tempfile

# -I so no rip happens: this probes argument handling, not the drive. -N -A -U
# keep it off the network, which S-9 would otherwise make non-reproducible.
BASE = ["-I", "-N", "-A", "-U", "-P", "0"]

# Header lines that prove a value took effect. Without one of these a probe
# cannot tell "accepted" from "silently ignored", and guessing between them is
# exactly the thing this file exists to stop.
EFFECT = {
    "-s": (r"^Offset:\s+([+-]?\d+) samples", lambda v: int(v)),
    "-r": (r"^Retry limit:\s+(\d+)", lambda v: int(v)),
    # The header prints 0 as "none" and the top level, 3, as "max".
    "-P": (r"^Paranoia level:\s+(\S+)",
           lambda v: {0: "none", 3: "max"}.get(int(v), int(v))),
    # The disc number, the part before "/". A value strtol() wrapped past
    # INT_MAX reads here as what it wrapped to, so it grades ignored.
    "-c": (r"^Disc number:\s+(\S+)",
           lambda v: int(str(v).split("/")[0])),
    "-O": (r"^Overread:\s+([+-]?\d+) frames", None),
    "--consumer": (r"^Consumer:\s+(\S+)", None),
}


def probe(binary, image, flag, value, extra=None):
    """One invocation. Returns (outcome, exit code, message, observed)."""
    base = list(BASE)
    extra = list(extra or [])
    # An interaction probe that inherits -I from the base is not probing what
    # it says: "-J alone" came back refused with the -I conflict message.
    if "-J" in extra and "-I" not in extra:
        base = [f for f in base if f != "-I"]
    if flag == "-d":
        # -d IS the image, so its probe replaces it rather than adding a
        # second -d. Values are relative to the image's own directory.
        args = [binary, "-d", str(value)] + base + extra
    else:
        args = [binary, "-d", image] + base + extra
        if flag:
            args += [flag] + ([str(value)] if value is not None else [])
    r = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=120, cwd=os.path.dirname(image) or ".")
    out = r.stdout.decode(errors="replace")

    if r.returncode != 0:
        # The distinguishing line, which S-12 grades. Take the last non-noise
        # line: cyanrip prints its diagnosis immediately before exiting.
        noise = re.compile(r"^(Checking|Opening|MusicBrainz|https|Log\(s\)|CUE files|\s|$)")
        msg = [l for l in out.splitlines() if l.strip() and not noise.match(l)]
        # A death by signal is NOT a refusal, and grading it as one is how this
        # probe reported "0 silently ignored" while -c / segfaulted in the same
        # run. subprocess reports signal death as a negative returncode.
        if r.returncode < 0:
            return ("crashed", r.returncode,
                    f"**killed by signal {-r.returncode}**", None)
        return "refused", r.returncode, (msg[-1] if msg else "(no message)"), None

    if flag == "--diagnostics":
        return record_outcome(out, os.path.dirname(image) or ".", value)

    pat = EFFECT.get(flag)
    if not pat:
        return "unobservable", 0, "", "(no header field exposes this)"
    m = re.search(pat[0], out, re.M)
    if not m:
        return "ignored", 0, "", "(field absent from header)"
    observed = m.group(1)
    if value is not None and pat[1]:
        # Compare numerically. The header prints a sign ("+0 samples") and a
        # string compare against "0" reported five false "ignored" rows -- the
        # check was wrong, not the binary, which is the same false alarm
        # Platterpus hit resolving INDEX 00 against absolute LSNs.
        try:
            same = pat[1](value) == int(observed)
        except ValueError:
            same = str(pat[1](value)) == observed
        return ("accepted" if same else "ignored"), 0, "", observed
    return "accepted", 0, "", observed


# --diagnostics takes effect as a FILE, written at exit, so no header line
# can show it: the probe looks for the record where the value says. Asked for
# by Platterpus's round 35 lap 8 S7, at an unwritable path and with an empty
# value, both of which exit 0 with no record. Each says why on stderr, which
# this probe captures, so the row carries that line; a run that exits 0 with
# no record AND no line is graded ignored, which --gate refuses.
RECORD_REFUSED = re.compile(r'^Couldn\'t open diagnostics path ".*" for writing!$',
                            re.M)


def record_outcome(out, cwd, value):
    path = os.path.join(cwd, str(value)) if value else None
    if path and os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as f:
                json.load(f)
        except (OSError, ValueError):
            return "ignored", 0, "", "(a file was written that is not JSON)"
        return "accepted", 0, "", "record written"
    m = RECORD_REFUSED.search(out)
    if not m:
        return "ignored", 0, "", "(no record and no line saying why)"
    return "no record", 0, m.group(0), None


GRID = [
    # flag, label, values (below-min, min, typical, max, one-past)
    ("-s", "read offset, samples", [-2147483648, -5000, -667, 0, 667, 5000, 2147483647]),
    ("-r", "frame/rip retries", [-1, 0, 1, 10, 2147483647, 2147483648]),
    ("-Z", "repeat rips until N matches", [-1, 0, 1, 2, 10, 2147483647]),
    ("-S", "drive speed multiplier", [-1, 0, 1, 48, 2147483647]),
    ("--stall-secs", "stall threshold, seconds", [-1, 0, 1, 10, 2147483647]),
    ("-P", "paranoia level", [-1, 0, 1, 3, 4, 999, 4294967296, 4294967297]),
    ("-m", "cover art max size", [-2, -1, 250, 500, 1200, 999]),
    ("-b", "lossy bitrate, kbps", [-1, 0, 1, 256, 100000]),
    ("-l", "track list", [0, 1, 2, 3, 99]),
    ("-c", "disc/totaldiscs", ["0/0", "1/1", "2/1", "1/2",
                               "2147483647/2147483647",
                               "2147483648/2147483648", "1/2147483648",
                               "4294967297/4294967297", "1/4294967298",
                               # malformed shapes: separator missing, doubled,
                               # empty either side. See MALFORMED_SHAPES below.
                               "1", "1/", "/2", "1//2", "/", "//"]),
]

# Every argument above with internal structure gets its separator abused the
# same four ways: missing, doubled, empty-left, empty-right, trailing. The -t
# defect Platterpus found in round 7 lap 31 lived in exactly this axis and the
# grid had no such axis -- every -t value was well-formed, so the probe varied
# the track number and the value and never the shape. Adding the axis once,
# for every structured argument, is the generalisation of that one fix.

STRING_GRID = [
    # -d, F9's first flag. Only values whose last line is cyanrip's own
    # "Unable to open device:" are tabled, because §7 is compared byte for
    # byte on every CI host: a missing .cue and a directory end on libcdio's
    # own error, whose wording is its version's; and an empty -d makes
    # libcdio look for a default drive, which opens a real one on a host
    # that has a drive. All three were run on 2026-10-19 and each exited 1
    # with a message; they are in our round 35 lap 7, not in this table.
    ("-d", "disc image or drive", ["basic.cue", "basic.bin", "/nonexistent",
                                   "/nonexistent.toc", "/nonexistent.nrg"]),
    ("--consumer", "consumer tag", ["", "x", "platterpus/0.6.4b12", "a" * 4096]),
    ("-a", "album metadata blob", ["", "album=x", "album=a:b", "album=" + "z" * 8192,
                                   "album", "=x", "album=", "a=b:", "a=b::c=d",
                                   "a==b", "album=x\\"]),
    # "1" and "99" carry no "=" on purpose. That shape used to step past the
    # terminator and publish adjacent process memory as track metadata; it is
    # refused since 3923dee. Reported by Platterpus in round 7 lap 31.
    ("-t", "track metadata", ["1=title=x", "1=title=a:b", "0=title=x",
                              "2=title=x", "3=title=x", "99=title=x",
                              "4294967297=title=x", "1", "99", "1="]),
    ("-o", "output formats", ["flac", "", "nosuchformat", "flac,flac"]),
    ("-T", "filename sanitation", ["simple", "os_simple", "unicode", "os_unicode", "bogus"]),
    ("-p", "pregap action", ["1=default", "1=drop", "1=merge", "1=track", "1=bogus", "99=drop",
                             "197=drop", "198=drop", "4294967297=drop",
                             "1", "=drop", "1=", "1==drop", "1=drop=", "=", "=="]),
    ("-C", "cover art location", ["Front=/nonexistent.png", "Front=", "=/nonexistent.png",
                                  "Front", "1=", "="]),
    # Relative to the probe's own directory, so the row reads the same on
    # every host; "." is a directory, which open() refuses for writing.
    ("--diagnostics", "diagnostics record path", ["rec.json", "/nonexistent/rec.json",
                                                  "", "."]),
]

INTERACTIONS = [
    (["-I", "-J"], "info-only with cue-only"),
    (["-J"], "cue-only alone"),
    (["-E", "-W"], "force deemphasis with no-deemphasis"),
    (["--cache-probe"], "cache probe on an image"),
    (["-f"], "find-offset on an image"),
]


BEGIN_MARK = "<!-- BEGIN GENERATED probe-argv-surface -->"
END_MARK = "<!-- END GENERATED probe-argv-surface -->"


def banner_of(binary):
    """The version line of the binary these rows were measured from.

    PLATTERPUS'S RIDER, round 15 lap 15 §E: "the regenerated table is a claim
    about *a* binary, so it needs to say which -- or the check tells a future
    reader that a flag behaves a way it stopped behaving two pins ago." That is
    the seam's own "a shared hash cannot prove the bytes describe the binary",
    turned on the thing replacing it. So the block carries its build tag.
    """
    r = subprocess.run([binary, "--version"], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=60)
    return r.stdout.decode("utf-8", "replace").strip().splitlines()[0]


def markdown_block(rows, inter, ignored, banner):
    """The generated §7 body, delimited so --check can find it exactly.

    The delimiters are not decoration. docs/seam-commands.md is JOINTLY OWNED,
    and a regenerate-and-diff over the whole file would claim prose the other
    side wrote. Bounding the generated region is what makes the check safe to
    run on a shared document -- agreed in round 15 lap 14 §4 and assented in
    their lap 15 §E.
    """
    out = [BEGIN_MARK, "",
           f"*Generated by `tools/probe-argv-surface.py --markdown` from "
           f"`{banner}`. Do not hand-edit; `--check` verifies it.*", "",
           "### Measured argument behaviour (black-box, our own binary)", "",
           "| flag | meaning | value | outcome | exit | message / observed |",
           "|---|---|---|---|---|---|"]
    for flag, label, v, outcome, rc, msg, obs in rows:
        cell = msg if msg else (obs or "")
        out.append(f"| `{flag}` | {label} | `{v}` | **{outcome}** | {rc} | {cell} |")
    out += ["", "### Interactions", "",
            "| flags | meaning | outcome | exit | message |", "|---|---|---|---|---|"]
    for f, label, outcome, rc, msg in inter:
        out.append(f"| `{f}` | {label} | **{outcome}** | {rc} | {msg} |")
    n_ref = sum(1 for r in rows if r[3] == "refused")
    n_acc = sum(1 for r in rows if r[3] == "accepted")
    n_uno = sum(1 for r in rows if r[3] == "unobservable")
    n_nor = sum(1 for r in rows if r[3] == "no record")
    out += ["", f"**{len(rows)} probes: {n_acc} accepted, {n_uno} unobservable, "
                f"{n_ref} refused, {n_nor} exited 0 with no record and a line "
                f"saying why, {len(ignored)} silently ignored.**", "",
            END_MARK]
    return "\n".join(out)


# THE BANNER NAMES THE BUILD THAT GENERATED THE BLOCK, which is never the
# commit that contains it: the block is committed after the build, so every
# commit after it moves the tag and nothing else. Compared byte for byte, the
# check failed on the first commit after a regeneration, with no row changed
# (found 2026-09-29, the first time §7 carried the delimiters). A clean tag is
# compared only in shape, as gen-provider-contract.py --check does for its own
# Build: line. The two sides differ on purpose. The COMMITTED banner must name a
# clean build, so a `-dirty` one there is not matched and still differs: a dirty
# build's commit does not describe it. The LIVE binary may be dirty, as it is
# whenever the suite runs over uncommitted edits, and every mutant of
# tools/mutate.py is; refusing that would make this a test that detects the
# edit rather than the defect.
#
# THE VERSION IS NORMALISED TOO, for the same reason one release later: every
# release moves it and nothing else, and the file is jointly owned, so without
# this each release would force a change to a shared document for a banner. The
# `.19` candidate's own suite failed on exactly that (2026-09-30). The banner
# stays true -- it names the build the tables were generated from -- and what is
# compared is what matters: every measured row against the live binary.
BUILD_TAG_RE = re.compile(r"(platterpus-fork-g)[0-9a-f]{7,40}(?=\)`)")
LIVE_TAG_RE = re.compile(r"(platterpus-fork-g)[0-9a-f]{7,40}(?:-dirty)?(?=\)`)")
VERSION_RE = re.compile(r"(`cyanrip )[^ `]+(?= \(platterpus-fork-g)")


def _normalise_build(text, live=False):
    text = VERSION_RE.sub(r"\1<version>", text)
    return (LIVE_TAG_RE if live else BUILD_TAG_RE).sub(r"\1<build>", text)


def check_against(path, block):
    """Non-zero when the committed block has drifted from the live binary.

    WHY THIS EXISTS. `seam-commands.md` §7 is the ONLY place the accepted
    argument ranges are published -- `--help` prints defaults, not ranges -- and
    it had no check. Line 504 published `-p '99=drop'` as accepted/exit 0 while
    the binary refused it with exit 1, and had done since the bound moved on
    2026-08-15. Both projects then hash-attested the stale bytes in two
    consecutive laps, and every gate reported OK, because a shared hash proves
    both sides hold the same bytes and can never prove the bytes describe the
    binary. This is the check that closes that gap.
    """
    text = pathlib.Path(path).read_text(encoding="utf-8")
    if BEGIN_MARK not in text or END_MARK not in text:
        print(f"FAIL: {path} carries no generated-block delimiters.")
        print(f"      Insert {BEGIN_MARK} and {END_MARK} around \u00a77's tables.")
        print("      Bounded on purpose: the file is jointly owned and the "
              "check must not claim prose the other side wrote.")
        return 1
    start = text.index(BEGIN_MARK)
    end = text.index(END_MARK) + len(END_MARK)
    have = _normalise_build(text[start:end].strip())
    want = _normalise_build(block.strip(), live=True)
    if have == want:
        print(f"{path}: \u00a77 matches the live binary")
        return 0
    import difflib
    print(f"FAIL: {path} \u00a77 has drifted from the live binary.")
    for line in list(difflib.unified_diff(have.splitlines(), want.splitlines(),
                                          "committed", "regenerated",
                                          lineterm=""))[:40]:
        print("   ", line)
    print("    Regenerate with: tools/probe-argv-surface.py --markdown")
    print("    NOTE: seam-commands.md is JOINTLY OWNED -- correcting it takes a "
          "version bump both sides ship, not a unilateral edit.")
    return 1


HELP_FLAG = re.compile(r"^\s+(--[a-z0-9-]+)(?: \((-[A-Za-z])\))?:", re.M)
ROW_FLAGS = re.compile(r"`(--?[A-Za-z][a-z0-9-]*)`")


def rows_cover_help(text, binary):
    """Every flag in the live --help has a row in §1, §1b or §2.

    Platterpus's F8, landed in round 35: §1 tabled the flags they send and nothing
    said which of ours they do not, so a flag added here could go unseen
    there. §1b now rows each one they do not send, and this fails when a
    flag in --help has no row anywhere, so a new flag cannot land without
    one. Reads the flag cell of each table row only, never the prose, which
    is jointly owned. Returns the number of flags --help listed and those
    without a row; none listed is a refusal, not a pass."""
    helptext = subprocess.run([binary, "--help"], capture_output=True,
                              text=True).stdout
    flags = HELP_FLAG.findall(helptext)
    tabled = set()
    for head in (r"## 1\. ", r"## 1b\. ", r"## 2\. "):
        m = re.search(head + r".*?(?=^## )", text, re.M | re.S)
        for line in (m.group(0).splitlines() if m else ()):
            if line.startswith("| `"):
                tabled |= set(ROW_FLAGS.findall(line.split("|")[1]))
    return len(flags), [long_ if not short else f"{short}, {long_}"
                        for long_, short in flags
                        if long_ not in tabled and short not in tabled]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--binary", default="build/src/cyanrip")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--check", metavar="FILE",
                    help="exit non-zero if FILE's generated block has "
                         "drifted from the live binary")
    ap.add_argument("--gate", action="store_true")
    a = ap.parse_args()

    binary = os.path.abspath(a.binary)
    if not os.path.exists(binary):
        sys.exit(f"{a.binary}: not built")

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with tempfile.TemporaryDirectory() as work:
        shutil.copy(os.path.join(root, "tests/fixtures/basic.cue"), work)
        shutil.copy(os.path.join(root, "tests/fixtures/cdda.bin"),
                    os.path.join(work, "basic.bin"))
        # ONE DIRECTORY PER INVOCATION, and a worker pool over them. The 116
        # invocations are independent, and one at a time they were 27 s of
        # the suite (2026-09-26). But they ran in ONE directory, and -I writes
        # its logs into the working directory, so running them together there
        # could let one see another's files. Each gets its own directory with
        # links to the one image, so none can see another's output, and
        # results come back in submission order. Measured byte-identical to
        # the sequential run's --markdown output before this landed.
        def fresh(n):
            d = os.path.join(work, f"p{n:03d}")
            os.mkdir(d)
            for f in ("basic.cue", "basic.bin"):
                os.symlink(os.path.join(work, f), os.path.join(d, f))
            return os.path.join(d, "basic.cue")

        jobs = [(flag, label, v, None)
                for flag, label, values in GRID + STRING_GRID for v in values]
        jobs += [(None, label, None, flags) for flags, label in INTERACTIONS]
        images = [fresh(n) for n in range(len(jobs))]
        workers = max(1, min(8, os.cpu_count() or 1))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            results = list(ex.map(
                lambda ji: probe(binary, ji[1], ji[0][0], ji[0][2],
                                 extra=ji[0][3]),
                zip(jobs, images)))

        rows, ignored, inter = [], [], []
        for (flag, label, v, flags), (outcome, rc, msg, obs) in zip(jobs, results):
            if flags is None:
                rows.append((flag, label, repr(v), outcome, rc, msg, obs))
                if outcome == "ignored":
                    ignored.append((flag, v))
            else:
                inter.append((" ".join(flags), label, outcome, rc, msg))

    if a.gate:
        # A crash outranks every other finding: it is an undiagnosable failure
        # and, for -c / and -p =, it was graded "refused" by this very script
        # until round 7 lap 32. Checked first so it can never be masked.
        crashed = [(r[0], r[2]) for r in rows if r[3] == "crashed"]
        crashed += [(f, "(interaction)") for f, _, o, _, _ in inter
                    if o == "crashed"]
        if crashed:
            print("CRASHED -- killed by a signal, no diagnosable exit:")
            for f, v in crashed:
                print(f"  {f} {v}")
            return 1
        # Every fatal path owes the caller a line. A non-zero exit with nothing
        # printed is the one failure a consumer cannot explain to a user.
        silent = [(r[0], r[2]) for r in rows
                  if r[3] == "refused" and r[5] == "(no message)"]
        if silent:
            print("REFUSED WITH NO MESSAGE (undiagnosable to a consumer):")
            for f, v in silent:
                print(f"  {f} {v}")
            return 1
        if ignored:
            print("SILENTLY IGNORED VALUES (S-9 findings):")
            for f, v in ignored:
                print(f"  {f} {v!r}")
            return 1
        if not any(r[3] == "refused" for r in rows):
            print("nothing was refused by any probe -- the range guards are gone")
            return 1
        print(f"{len(rows)} probes, 0 crashed, 0 refused-without-a-message, "
              f"0 silently ignored, "
              f"{sum(1 for r in rows if r[3] == 'refused')} refused, "
              f"{sum(1 for r in rows if r[3] == 'accepted')} seen to take "
              f"effect, {sum(1 for r in rows if r[3] == 'unobservable')} "
              f"unobservable, "
              f"{sum(1 for r in rows if r[3] == 'no record')} with no "
              f"record and a line saying why")
        return 0

    if a.check:
        rc = check_against(a.check,
                           markdown_block(rows, inter, ignored,
                                          banner_of(a.binary)))
        listed, missing = rows_cover_help(
            pathlib.Path(a.check).read_text(encoding="utf-8"), binary)
        if not listed:
            print(f"FAIL: {binary} --help listed no flags, so whether "
                  f"{a.check} rows them all was not checked")
            return 1
        for flag in missing:
            print(f"FAIL: {a.check} has no row for {flag}, which --help "
                  f"lists: add it to \u00a71 if the consumer sends it, else "
                  f"\u00a71b")
        if not missing:
            print(f"{a.check}: each of the {listed} flags --help lists has a "
                  f"row in \u00a71, \u00a71b or \u00a72")
        return rc or (1 if missing else 0)

    if a.markdown:
        print(markdown_block(rows, inter, ignored, banner_of(a.binary)))
        if ignored:
            print("\n**Silently-ignored values (findings):** " +
                  ", ".join(f"`{f} {v}`" for f, v in ignored))
        else:
            n_uno = sum(1 for r in rows if r[3] == "unobservable")
            print("\n**Silently-ignored values: none.** Every value was seen to "
                  "take effect, was refused with a message, exited 0 with no "
                  "record and a line saying why, or could not be "
                  f"observed ({n_uno} unobservable, which is not the same as "
                  "taking effect).")
        return 0

    for r in rows:
        print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
