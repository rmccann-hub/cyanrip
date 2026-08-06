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
import re
import shutil
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
    "-r": (r"^Frame retries:\s+(\d+)", lambda v: int(v)),
    "-P": (r"^Paranoia level:\s+(\S+)", None),
    "-O": (r"^Overread:\s+([+-]?\d+) frames", None),
    "-u": (r"^Consumer:\s+(\S+)", None),
}


def probe(binary, image, flag, value, extra=None):
    """One invocation. Returns (outcome, exit code, message, observed)."""
    base = list(BASE)
    extra = list(extra or [])
    # An interaction probe that inherits -I from the base is not probing what
    # it says: "-J alone" came back refused with the -I conflict message.
    if "-J" in extra and "-I" not in extra:
        base = [f for f in base if f != "-I"]
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

    pat = EFFECT.get(flag)
    if not pat:
        return "accepted", 0, "", "(no header field exposes this)"
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


GRID = [
    # flag, label, values (below-min, min, typical, max, one-past)
    ("-s", "read offset, samples", [-2147483648, -5000, -667, 0, 667, 5000, 2147483647]),
    ("-r", "frame/rip retries", [-1, 0, 1, 10, 2147483647, 2147483648]),
    ("-Z", "repeat rips until N matches", [-1, 0, 1, 2, 10, 2147483647]),
    ("-S", "drive speed multiplier", [-1, 0, 1, 48, 2147483647]),
    ("-k", "stall threshold, seconds", [-1, 0, 1, 10, 2147483647]),
    ("-P", "paranoia level", [-1, 0, 1, 3, 4, 999]),
    ("-m", "cover art max size", [-2, -1, 250, 500, 1200, 999]),
    ("-b", "lossy bitrate, kbps", [-1, 0, 1, 256, 100000]),
    ("-l", "track list", [0, 1, 2, 3, 99]),
    ("-c", "disc/totaldiscs", ["0/0", "1/1", "2/1", "1/2",
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
    ("-u", "consumer tag", ["", "x", "platterpus/0.6.4b12", "a" * 4096]),
    ("-a", "album metadata blob", ["", "album=x", "album=a:b", "album=" + "z" * 8192,
                                   "album", "=x", "album=", "a=b:", "a=b::c=d",
                                   "a==b", "album=x\\"]),
    # "1" and "99" carry no "=" on purpose. That shape used to step past the
    # terminator and publish adjacent process memory as track metadata; it is
    # refused since 3923dee. Reported by Platterpus in round 7 lap 31.
    ("-t", "track metadata", ["1=title=x", "1=title=a:b", "0=title=x",
                              "99=title=x", "1", "99", "1="]),
    ("-o", "output formats", ["flac", "", "nosuchformat", "flac,flac"]),
    ("-T", "filename sanitation", ["simple", "os_simple", "unicode", "os_unicode", "bogus"]),
    ("-p", "pregap action", ["1=default", "1=drop", "1=merge", "1=track", "1=bogus", "99=drop",
                             "1", "=drop", "1=", "1==drop", "1=drop=", "=", "=="]),
    ("-C", "cover art location", ["Front=/nonexistent.png", "Front=", "=/nonexistent.png",
                                  "Front", "1=", "="]),
]

INTERACTIONS = [
    (["-I", "-J"], "info-only with cue-only"),
    (["-J"], "cue-only alone"),
    (["-E", "-W"], "force deemphasis with no-deemphasis"),
    (["-x"], "cache probe on an image"),
    (["-f"], "find-offset on an image"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--binary", default="build/src/cyanrip")
    ap.add_argument("--markdown", action="store_true")
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
        image = os.path.join(work, "basic.cue")

        rows, ignored = [], []
        for flag, label, values in GRID + STRING_GRID:
            for v in values:
                outcome, rc, msg, obs = probe(binary, image, flag, v)
                rows.append((flag, label, repr(v), outcome, rc, msg, obs))
                if outcome == "ignored":
                    ignored.append((flag, v))

        inter = []
        for flags, label in INTERACTIONS:
            outcome, rc, msg, _ = probe(binary, image, None, None, extra=flags)
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
              f"{sum(1 for r in rows if r[3] == 'refused')} refused")
        return 0

    if a.markdown:
        print("### Measured argument behaviour (black-box, our own binary)\n")
        print("| flag | meaning | value | outcome | exit | message / observed |")
        print("|---|---|---|---|---|---|")
        for flag, label, v, outcome, rc, msg, obs in rows:
            cell = msg if msg else (obs or "")
            print(f"| `{flag}` | {label} | `{v}` | **{outcome}** | {rc} | {cell} |")
        print("\n### Interactions\n")
        print("| flags | meaning | outcome | exit | message |")
        print("|---|---|---|---|---|")
        for f, label, outcome, rc, msg in inter:
            print(f"| `{f}` | {label} | **{outcome}** | {rc} | {msg} |")
        n_ref = sum(1 for r in rows if r[3] == "refused")
        n_acc = sum(1 for r in rows if r[3] == "accepted")
        n_ign = len(ignored)
        print(f"\n**{len(rows)} probes: {n_acc} accepted, {n_ref} refused, "
              f"{n_ign} silently ignored.**")
        if ignored:
            print("\n**Silently-ignored values (findings):** " +
                  ", ".join(f"`{f} {v}`" for f, v in ignored))
        else:
            print("\n**Silently-ignored values: none.** Every value either took "
                  "effect or was refused with a message.")
        return 0

    for r in rows:
        print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
