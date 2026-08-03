#!/usr/bin/env python3
"""Generate the provider half of the cyanrip/Platterpus dependency contract.

The consumer (Platterpus) generates its half from its parser tables. This is the
mirror: every input this build accepts, every line it emits, every fatal string,
and every exit code -- derived from the source tree and the built binary, never
hand-written, so it cannot describe behaviour we do not have.

Usage:
    tools/gen-provider-contract.py [--binary build/src/cyanrip] > PROVIDER-CONTRACT.md
    tools/gen-provider-contract.py --check PROVIDER-CONTRACT.md   # non-zero on drift

Sections emitted:
    P1  Every command line flag, from the binary's own --help
    P2  Stable log lines -- the API, grouped by where they appear
    P3  Unstable lines -- reserved for reword without a handshake
    P4  Exit codes, and whether any non-zero exit can be silent
    P5  Fatal/error message inventory, with file:line
"""

import argparse
import os
import re
import subprocess
import sys

SRC = "src"

# Lines whose wording we explicitly reserve the right to change. Everything else
# emitted by cyanrip_log() is treated as stable API. Keeping this list short and
# explicit is the point: an unlisted line is a promise.
UNSTABLE_SUBSTRINGS = (
    "progress - ",            # \r-redrawn progress, stdout only
    "Flushing encoders",      # stdout only
    "Trying to quit",         # stdout only
    "Force quitting",         # stdout only
    "folder: [",              # -o help listing, stdout only
)

# Emitted by libavfilter, not by us -- wording belongs to FFmpeg and moves with it.
FFMPEG_OWNED = (
    "Integrated loudness", "Loudness range", "Sample peak:", "True peak:",
    "LRA", "Threshold", "Summary:",
)

# Wordings that read as a diagnostic. This list used to be the *only* test for
# whether a message was fatal, which was a guess dressed as a derivation: a
# hand-maintained allowlist cannot know about a message somebody words
# differently. Platterpus caught exactly that in round 5 -- two argument-
# validation fatals ("discnumber ... is larger than totaldiscs ...", "Cover art
# already specified ...") that begin with no listed prefix and so never reached
# the inventory, even though the parser saw them and printed them in P2.
#
# It is now one of two independent kinds of evidence, not the test. See
# FAIL_PATH below and P5's evidence column.
DIAGNOSTIC_PREFIXES = (
    "Invalid", "Unable", "Missing", "No device", "No cover art", "Error",
    "Errors", "Failed", "Couldn't", "Could not", "Cannot", "Unsupported",
    "Unknown", "Unrecognized", "Stopping", "Aborting", "Drive media",
    "Insufficient", "Out of memory", "Fatal", "-J ",
)

# The second kind of evidence, and the one that does not depend on wording: the
# call is followed by something that leaves on a failure path.
FAIL_PATH = re.compile(
    r"\breturn\s+1\s*;"
    r"|\bexit\s*\(\s*[1-9]"
    r"|\breturn\s+AVERROR"
    r"|total_error_count\s*\+\+"
    r"|\bgoto\s+fail\b")

# "goto end" gets its own class rather than being folded into either bucket.
# cyanrip_main.c uses it for the ordinary success cleanup *and* for several
# genuine aborts ("Offset is unset!" leaves that way), so calling it fatal would
# file success lines as failures and calling it non-fatal would drop real
# aborts. Neither is honest; naming it is.
GOTO_END = re.compile(r"\bgoto\s+end\b")

# Where to stop looking. A failure exit only counts as belonging to this call if
# nothing has opened a new branch in between -- otherwise an informational line
# inherits the error handling of whatever happens to follow it. Without this cut
# "Opening drive..." reads as fatal because the *next* statement's if-block
# returns AVERROR.
NEXT_BRANCH = re.compile(r"\b(if|for|while|switch)\s*\(|cyanrip_log\s*\(|fprintf\s*\(")

# Hard cap, in case no branch follows at all.
FAIL_PATH_WINDOW = 320

LOGCALL = re.compile(
    r'(?P<fn>cyanrip_log)\s*\(\s*(?P<target>[A-Za-z_][A-Za-z0-9_>\-\.]*)\s*,\s*\d+\s*,\s*'
    r'(?P<lit>"(?:[^"\\]|\\.)*"(?:\s*"(?:[^"\\]|\\.)*")*)', re.S)
STDERRCALL = re.compile(
    r'fprintf\s*\(\s*stderr\s*,\s*(?P<lit>"(?:[^"\\]|\\.)*"(?:\s*"(?:[^"\\]|\\.)*")*)', re.S)


def joined(lit):
    return "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', lit))


def evidence(text, end, msg):
    """Why this message is believed to be reachable on a failure path.

    Returns "both", "control flow", "wording", or None. Two independent tests,
    reported separately rather than OR-ed into a bare verdict, so a consumer can
    see which ones rest on the weaker of the two.
    """
    window = text[end:end + FAIL_PATH_WINDOW]

    # Trim at the next branch or log call, so this call is only credited with an
    # exit that is actually its own.
    cut = NEXT_BRANCH.search(window)
    if cut:
        window = window[:cut.start()]

    by_flow = bool(FAIL_PATH.search(window))
    by_word = any(msg.startswith(p) for p in DIAGNOSTIC_PREFIXES)
    by_end = bool(GOTO_END.search(window))

    if by_flow and by_word:
        return "both"
    if by_flow:
        return "control flow"
    if by_end and by_word:
        return "wording + goto end"
    if by_end:
        return "goto end"
    if by_word:
        return "wording"
    return None


def collect():
    """Walk every log call site. Returns (stable, unstable, fatal)."""
    stable, unstable, fatal = [], [], []
    for name in sorted(os.listdir(SRC)):
        if not name.endswith((".c", ".h")):
            continue
        path = os.path.join(SRC, name)
        text = open(path, encoding="utf-8").read()

        for m in LOGCALL.finditer(text):
            raw = joined(m.group("lit"))
            line = text[:m.start()].count("\n") + 1
            to_log = m.group("target") != "NULL"
            s = raw.replace("\\n", "").replace("\\t", " ").strip()
            if not s:
                continue
            rec = (name, line, s, to_log)
            if any(u in s for u in UNSTABLE_SUBSTRINGS) or not to_log:
                unstable.append(rec)
            else:
                stable.append(rec)
            ev = evidence(text, m.end(), s)
            if ev:
                fatal.append((name, line, s, to_log, ev))

        for m in STDERRCALL.finditer(text):
            raw = joined(m.group("lit"))
            line = text[:m.start()].count("\n") + 1
            s = raw.replace("\\n", "").strip()
            if not s:
                continue
            ev = evidence(text, m.end(), s)
            if ev:
                fatal.append((name, line, s, False, ev))

    return stable, unstable, fatal


def flags(binary):
    """Every flag, from the binary's own --help so it cannot drift from reality."""
    out = subprocess.run([binary, "--help"], capture_output=True, text=True).stdout
    rows, section = [], "General"
    for ln in out.splitlines():
        if ln.endswith(":") and not ln.startswith(" "):
            section = ln.rstrip(":")
            continue
        m = re.match(r"\s+--(?P<long>[a-z0-9-]+)\s+\((?P<short>-[A-Za-z])\):\s+(?P<desc>.+)", ln)
        if m:
            rows.append((section, m.group("short"), "--" + m.group("long"),
                         m.group("desc").strip()))
    return rows


def exit_codes():
    """Every distinct process exit value reachable from main()."""
    codes = set()
    for name in os.listdir(SRC):
        if not name.endswith(".c"):
            continue
        t = open(os.path.join(SRC, name), encoding="utf-8").read()
        codes.update(re.findall(r"exit\((\d+)\)", t))
    main = open(os.path.join(SRC, "cyanrip_main.c"), encoding="utf-8").read()
    start = main.index("int main(")
    codes.update(re.findall(r"^\s*return (\d+);", main[start:], re.M))
    return sorted(codes, key=int)


def version(binary):
    """The banner, with the commit suffix normalised.

    The real suffix is this build's short SHA. Embedding it verbatim would mean
    committing this file changes the SHA, which makes the file it just produced
    stale -- a generated artifact cannot contain a value that generating it
    alters. The shape is the contract; the digits are not.
    """
    raw = subprocess.run([binary, "--version"], capture_output=True,
                         text=True).stdout.strip()
    return re.sub(r"-g[0-9a-f]{7,40}\)", "-g<commit>)", raw)


def emit(binary):
    stable, unstable, fatal = collect()
    o = []
    w = o.append

    w("# cyanrip provider contract")
    w("")
    w("**Generated** by `tools/gen-provider-contract.py` from the source tree and the")
    w("built binary. Do not edit by hand -- regenerate. A hand-written contract goes")
    w("stale silently, which is the failure this file exists to prevent.")
    w("")
    w(f"Build: `{version(binary)}`")
    w("")
    w("This is the provider half of the seam. Platterpus generates the consumer half")
    w("(`docs/cyanrip-consumer-contract.md`) from its parser tables. Neither side")
    w("describes behaviour it does not have.")
    w("")

    w("## P1 - Inputs: every command line flag")
    w("")
    w("From the binary's own `--help`, so it cannot drift from what the build accepts.")
    w("")
    rows = flags(binary)
    cur = None
    for section, short, long, desc in rows:
        if section != cur:
            cur = section
            w("")
            w(f"### {section}")
            w("")
            w("| Short | Long | Meaning |")
            w("|---|---|---|")
        w(f"| `{short}` | `{long}` | {desc} |")
    w("")
    w(f"**{len(rows)} flags total.** Notes that are not derivable from `--help`:")
    w("")
    w("- `-O` is **overread**, not an options passthrough. Never repurpose it.")
    w("- `-v` is version; there is no `-V`.")
    w("- `-J` and `-I` are mutually exclusive; combining them exits 1.")
    w("- `-d` accepts a device path **or** a TOC/CUE/NRG image file.")
    w("- `-a`/`-t` values are `:`-separated; a literal colon must be escaped `\\:`.")
    w("- `-t N=` and `-l N` are 1-based and validated against the disc's real track")
    w("  count; out of range exits 1 with a message naming both numbers.")
    w("- Multiple `-o` formats produce **one logfile and one cue per format**.")
    w("")

    w("## P2 - Outputs: stable log lines (the API)")
    w("")
    w("Every line below reaches **both stdout and the logfile**. Changing the text,")
    w("indentation, field order or units of any of them is a breaking change and")
    w("requires a handshake round.")
    w("")
    w("| File:line | Line |")
    w("|---|---|")
    seen = set()
    for name, line, s, _ in stable:
        if s in seen:
            continue
        seen.add(s)
        disp = s.replace("|", "\\|")
        w(f"| `{name}:{line}` | `{disp}` |")
    w("")
    w(f"**{len(seen)} distinct stable lines.**")
    w("")
    w("Field order within a block is fixed and is part of the contract. The golden")
    w("reference log in the handshake package is the authoritative example.")
    w("")

    w("## P3 - Unstable lines: reworded without a handshake")
    w("")
    w("Do not parse these. Most are stdout-only and never reach the logfile at all.")
    w("")
    w("| File:line | Line | Reaches logfile? |")
    w("|---|---|---|")
    seen = set()
    for name, line, s, to_log in unstable:
        if s in seen:
            continue
        seen.add(s)
        disp = (s.replace("|", "\\|") or "(empty / formatting only)")
        w(f"| `{name}:{line}` | `{disp}` | {'yes' if to_log else '**no, stdout only**'} |")
    w("")
    w("Also unstable, and **not ours**: the loudness block FFmpeg's `ebur128` filter")
    w("prints (" + ", ".join(f"`{x}`" for x in FFMPEG_OWNED[:4]) + ", ...). That wording")
    w("belongs to libavfilter and moves when FFmpeg does. Prefer the `Peak level:`")
    w("line in P2, which is ours and is gated on a completed rip.")
    w("")

    w("## P4 - Exit codes")
    w("")
    w("| Code | Meaning |")
    w("|---|---|")
    w("| `0` | Success: completed rip, `-I`, `-J`, `-h`, `-v`, or a `-Y` that validated |")
    w("| `1` | Every failure, without exception |")
    w("")
    w(f"Distinct exit values found in the tree: {', '.join('`'+c+'`' for c in exit_codes())}.")
    w("")
    w("**There is no per-failure-class code.** Classification must come from the text,")
    w("which is why P5 exists. No non-zero exit is silent: argument parse failures")
    w("print before returning, and every other `return 1` in `main()` is preceded by a")
    w("`cyanrip_log()` call.")
    w("")
    w("Argument validation runs **before the logfile is opened**, so that whole class of")
    w("diagnosis is **stdout only**. A consumer that reads only the logfile cannot see it.")
    w("")

    w("## P5 - Fatal and error message inventory")
    w("")
    w("Every string reachable on a failure path. Use this to derive error matching")
    w("rather than guessing prefixes.")
    w("")
    w("**Evidence** says why each string is here, and is reported rather than folded")
    w("into a bare verdict so you can see which entries rest on the weaker test:")
    w("")
    w("- `control flow` - the call is followed by `return 1`, a non-zero `exit()`,")
    w("  `return AVERROR(...)`, `total_error_count++`, or `goto fail`. Does not")
    w("  depend on how the message is worded.")
    w("- `wording` - the message begins like a diagnostic, but no failure exit was")
    w("  found near it. Either the exit is further away than the search window, or")
    w("  the message is a warning that does not end the run. **Treat these as")
    w("  possibly non-fatal.**")
    w("- `both` - the two agree.")
    w("- `goto end` / `wording + goto end` - the call is followed by `goto end`,")
    w("  which in `cyanrip_main.c` is *both* the ordinary success cleanup and the")
    w("  route several genuine aborts take (`Offset is unset!` leaves that way).")
    w("  It is reported as its own class because calling it fatal would file")
    w("  success lines as failures, and calling it non-fatal would drop real")
    w("  aborts. **Neither of us can settle these from the source alone; they need")
    w("  a run to classify.**")
    w("")
    w("The search stops at the next `if`/`for`/`while`/`switch` or the next log")
    w("call, so a message is only credited with an exit that is its own. Without")
    w("that cut, `Opening drive...` reads as fatal because the *next* statement's")
    w("if-block returns `AVERROR`.")
    w("")
    w("| File:line | Message | Evidence | Reaches logfile? |")
    w("|---|---|---|---|")
    seen = {}
    for name, line, s, to_log, ev in fatal:
        if s in seen:
            continue
        seen[s] = ev
        disp = s.replace("|", "\\|")
        w(f"| `{name}:{line}` | `{disp}` | {ev} | {'yes' if to_log else '**no, stdout only**'} |")
    w("")
    tally = {}
    for ev in seen.values():
        tally[ev] = tally.get(ev, 0) + 1
    w(f"**{len(seen)} distinct strings.** By evidence: " +
      ", ".join(f"{tally.get(k, 0)} {k}"
                for k in ("both", "control flow", "wording",
                          "goto end", "wording + goto end")) + ".")
    w("")
    w("The `control flow` and `both` rows total "
      f"{tally.get('both', 0) + tally.get('control flow', 0)} strings proven reachable on a")
    w("failure path without reference to their wording. That subset is the one to")
    w("build a hard failure classifier on.")
    w("")
    return "\n".join(o) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--binary", default="build/src/cyanrip")
    ap.add_argument("--check", metavar="FILE",
                    help="compare against FILE and exit non-zero on drift")
    args = ap.parse_args()

    if not os.path.isdir(SRC):
        sys.exit("run from the repository root")
    if not os.path.exists(args.binary):
        sys.exit(f"binary not found: {args.binary} (build first)")

    text = emit(args.binary)

    if args.check:
        have = open(args.check, encoding="utf-8").read()
        if have != text:
            sys.stderr.write(
                f"{args.check} is stale -- regenerate with "
                f"tools/gen-provider-contract.py\n")
            return 1
        print(f"{args.check} is up to date")
        return 0

    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
