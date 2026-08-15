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
    P6  Version flags across the stock line (stated, not derived)
"""

import argparse
import hashlib
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
#
# Platterpus caught this list being incomplete in round 5 -- it missed
# "err = 1" feeding a later "total_error_count += err", a bare negative
# "return -1", and every "goto end_meta". The deeper problem was that replacing
# a hand-written list of *words* with a hand-written list of *control-flow
# idioms* is the same defect one level up: still a guess, still silently
# incomplete, still presented as derived.
#
# So gotos are no longer enumerated here at all. Every "goto <label>" is
# discovered from the source and reported under its own label name (see
# GOTO_ANY), which cannot miss a label nobody thought of.
FAIL_PATH = re.compile(
    r"\breturn\s+1\s*;"
    r"|\breturn\s+-\d+\s*;"
    r"|\bexit\s*\(\s*[1-9]"
    r"|\breturn\s+AVERROR"
    r"|total_error_count\s*(\+\+|\+=)"
    r"|\berr\s*=\s*[1-9]"
    r"|\bret\s*=\s*[1-9]\s*;")

# Any goto, with its label captured. A label is *named* rather than judged:
# "goto fail" is unambiguous, "goto end" is both the success cleanup and the
# abort route, and "goto end_meta" is somewhere in between. Naming them lets a
# consumer decide, and means a label added later cannot silently vanish.
GOTO_ANY = re.compile(r"\bgoto\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;")

# Labels whose block is known, by reading them, to leave on a failure path.
# Kept deliberately small and stated, rather than inferred.
GOTO_FATAL = ("fail",)

# Where to stop looking. A failure exit only counts as belonging to this call if
# nothing has opened a new branch in between -- otherwise an informational line
# inherits the error handling of whatever happens to follow it. Without this cut
# "Opening drive..." reads as fatal because the *next* statement's if-block
# returns AVERROR.
#
# Deliberately does NOT cut at the next log call. Two arms of one if/else that
# both log and then converge on a single exit must carry the same class -- the
# first arm's exit lies past the second arm's log call, so cutting there gave
# accurip.c:137 and :140 different verdicts for one shared "goto end".
# Platterpus caught that.
NEXT_BRANCH = re.compile(r"\b(if|for|while|switch)\s*\(")

# Hard cap, in case no branch follows at all.
FAIL_PATH_WINDOW = 320

LOGCALL = re.compile(
    r'(?P<fn>cyanrip_log)\s*\(\s*(?P<target>[A-Za-z_][A-Za-z0-9_>\-\.]*)\s*,\s*\d+\s*,\s*'
    r'(?P<lit>"(?:[^"\\]|\\.)*"(?:\s*"(?:[^"\\]|\\.)*")*)', re.S)
# Function-like macros that wrap cyanrip_log() and take the format as their
# first argument. Found by structure -- a #define whose body calls
# cyanrip_log(...) with the macro's own first parameter as the format -- rather
# than by a hardcoded list of names, because a hardcoded list is a guess wearing
# a derivation's clothes and this generator has shipped that defect twice.
#
# cyanrip_log.c's CLOG is one, and it emits seven banner labels every rip
# prints: Disc number:, Total discs:, DiscID:, Release ID:, CDDB ID:, Album:,
# Album artist:. None of them was in ANY published contract -- five of them, so
# all five published contracts -- because the scanner had no pattern for the
# macro. Platterpus depends on six (2026-08-14 hand-off §6), so the two halves
# of the seam disagreed about what was covered, and the side that would break
# on a reword was the side with no say in it.
# The body runs to the last backslash-continued line, so a multi-line macro is
# read whole. Getting this wrong is silent: an alternation that stopped at the
# first newline matched CLOG's signature, found no cyanrip_log in the one line
# it had, and reported "not a wrapper" -- which looks exactly like "there are
# no wrappers".
WRAPPER_DEF = re.compile(
    r'^#define\s+(?P<name>[A-Z][A-Z0-9_]*)\s*\(\s*(?P<fmt>[A-Za-z_][A-Za-z0-9_]*)\s*,'
    r'(?P<rest>(?:.*\\\n)*.*)', re.M)

STDERRCALL = re.compile(
    r'fprintf\s*\(\s*stderr\s*,\s*(?P<lit>"(?:[^"\\]|\\.)*"(?:\s*"(?:[^"\\]|\\.)*")*)', re.S)

# genopt's own diagnostics, which reach the terminal and the logfile through
# GEN_OPT_LOG -> crip_genopt_log -> cyanrip_vlog, and which were invisible to
# this generator until 2026-08-10. The contract's anchor has always claimed to
# cover `src/*.h`, and genopt.h has always been in `src/`; the scan simply had
# no pattern for the macro. So an entire family of fatal messages was missing
# from a document that presents itself as the complete inventory -- including
#
#     Unable to parse command line argument: %s
#
# the message that once read to a consumer as "cyanrip is not installed", and
# the reason this fork restored -V. Found by running the binary with a bad
# argument and looking for its message in the contract.
# Whitespace INCLUDING line continuations. Every one of these call sites that
# matters lives inside a #define, so the tokens are separated by "\\\n" rather
# than by whitespace alone. A \s*-only pattern silently matched the four sites
# outside macro bodies and missed the four inside them -- among them the exact
# message a malformed -l produced during seam testing, which is what sent us
# looking here. A pattern that returns a plausible number is worse than one
# that returns nothing.
_WS = r'[\s\\]*'
GENOPTCALL = re.compile(
    r'GEN_OPT_LOG' + _WS + r'\(' + _WS + r'[A-Za-z_][A-Za-z0-9_]*' + _WS + r',' + _WS +
    r'(?P<level>GEN_OPT_LOG_[A-Z]+)' + _WS + r',' + _WS +
    r'(?P<lit>"(?:[^"\\]|\\.)*"(?:' + _WS + r'"(?:[^"\\]|\\.)*")*)', re.S)

# A macro body stringifies its parameter into the message: `"as a " #type " for"`.
# The rendered text depends on the instantiation -- int32_t, double, and so on --
# so there is no single literal to publish. Report the placeholder rather than
# either guessing one instantiation or truncating the format at the break, which
# is what joining only the string tokens would do.
STRINGIFY_RUN = re.compile(
    r'[\s\\]*#([A-Za-z_][A-Za-z0-9_]*)[\s\\]*'
    r'((?:"(?:[^"\\]|\\.)*"[\s\\]*)+)')


# Some lines are composed into a char buffer by a run of snprintf() calls and
# then emitted with cyanrip_log(..., "%s", buf). The emitter's literal is a bare
# "%s", so scanning call sites alone shows a consumer nothing about what the
# line actually says -- Platterpus depends on the composed progress text for its
# progress bar and ETA, and asked (round 5 A1) for it to be declared rather than
# hidden behind "%s". Derive the pieces from the snprintf formats that build the
# buffer, in source order, so the shape stays generated rather than described.
COMPOSED_EMIT = re.compile(
    r'cyanrip_log\s*\(\s*(?P<target>[A-Za-z_][A-Za-z0-9_>\-\.]*)\s*,\s*\d+\s*,\s*'
    r'(?P<lit>"(?:[^"\\]|\\.)*")\s*,\s*(?P<buf>[a-z_][a-z0-9_]*)\s*\)')

# The literal must be a fixed prefix (possibly empty) followed by one %s and
# nothing else -- `"%s"` or `"Cache probe:    %s\n"`. Anything with a second
# conversion is not one buffer being echoed and must not be reconstructed as
# though it were.
COMPOSED_LIT = re.compile(r'^"((?:[^"\\%]|\\.)*)%s(?:\\n)?"$')

# A buffer filled by a named helper rather than in the emitting function:
#   char line[224];
#   crip_cache_probe_line(line, sizeof(line), ...);
#   cyanrip_log(ctx, 0, "Cache probe:    %s\n", line);
# One hop, and only when the buffer is the helper's FIRST argument, so the
# formats attributed to it are the ones writing into that buffer and not into
# something else the helper also touches.
FILLED_BY = r'\b(?P<fn>[a-z_][a-z0-9_]*)\s*\(\s*{buf}\s*,\s*sizeof\s*\(\s*{buf}\s*\)'

# Its definition, so the scan can be bounded to that function's body and the
# parameter name it writes through recovered. Nothing is assumed about the
# parameter being called the same thing as the caller's buffer -- it is not.
FN_DEF = (r'^[A-Za-z_][A-Za-z0-9_ \*]*\b{fn}\s*\(\s*char\s*\*\s*'
          r'(?P<param>[a-z_][a-z0-9_]*)\b')
SNPRINTF_INTO = (
    r'snprintf\s*\(\s*{buf}\b[^;]*?,\s*'
    r'(?P<lit>"(?:[^"\\]|\\.)*"(?:\s*"(?:[^"\\]|\\.)*")*)')


# <inttypes.h> length macros, which sit *outside* the string literals and so
# would otherwise truncate a format mid-conversion (", ETA - %" PRId64 "s").
INTTYPES = {
    "PRId64": "lld", "PRIu64": "llu", "PRIx64": "llx", "PRIi64": "lli",
    "PRId32": "d",   "PRIu32": "u",   "PRIx32": "x",   "PRIi32": "i",
    "PRId16": "hd",  "PRIu16": "hu",  "PRIx16": "hx",  "PRIi16": "hi",
    "PRId8":  "hhd", "PRIu8":  "hhu", "PRIx8":  "hhx", "PRIi8":  "hhi",
}

INTTYPE_RUN = re.compile(
    r'[\s\\]*(PRI[diux](?:8|16|32|64))[\s\\]*'
    r'((?:"(?:[^"\\]|\\.)*"[\s\\]*)+)')


def splice_inttypes(text, end, base):
    """Continue a joined literal through <inttypes.h> length macros.

    "Read stalls: ... exceeded %" PRId64 "s\\n" is three tokens with the macro
    between them, so joining only the string literals stops at the '%' and
    publishes a format truncated mid-conversion. That is not hypothetical: two
    stable contract lines shipped ending in a bare '%', and P2 is the set of
    lines we undertake not to reword -- a truncated one cannot be checked
    against anything. Loops, because a format may carry several."""
    out = base
    pos = end
    while True:
        m = STRINGIFY_RUN.match(text, pos)
        if m:
            out += "<" + m.group(1) + ">" + joined(m.group(2))
            pos = m.end()
            continue
        m = INTTYPE_RUN.match(text, pos)
        if not m:
            break
        # Never "?": a generated document that quietly prints %? for a macro
        # it does not know has published a format string that is wrong, while
        # looking derived. PRIi64 was missing and shipped four rows reading
        # `(default: %?)` and `not in [%?:%?] range!` before this refused.
        if m.group(1) not in INTTYPES:
            sys.exit("gen-provider-contract: unknown length macro %s at "
                     "offset %i -- add it to INTTYPES rather than publishing "
                     "a guessed conversion" % (m.group(1), m.start()))
        conv = INTTYPES[m.group(1)]
        # The '%' lives at the end of the preceding literal by convention;
        # only supply one when it does not.
        out += conv if out.endswith("%") else "%" + conv
        out += joined(m.group(2))
        pos = m.end()
    return out


def reaches_cell(to_log):
    """How a call site's target maps to "does this reach the logfile?".

    It used to be a straight yes/no on `ctx != NULL`, and that stopped being
    true when pre-log output began being replayed: a cyanrip_log(NULL, ...)
    made before cyanrip_log_init() is buffered and written into the logfile
    when it opens, while the same call made after it is not. Which of those a
    given site is depends on when it runs, which is not a property of the call
    site -- so this reports the evidence and leaves the timing open rather than
    picking one and being wrong for half the rows."""
    return "yes" if to_log else "**not directly** - see legend"


def func_start(text, pos):
    """Offset of the enclosing function's opening brace, approximated by the
    last column-0 '}' before pos. Reliable for this tree's K&R layout, and the
    point is only to stop a buffer in one function from being attributed the
    snprintf calls of a same-named buffer in another -- which it did: the cue
    sheet echoed at cyanrip_main.c:1910 uses a char line[4096] filled by
    fgets(), and picked up the progress line's formats without this bound."""
    m = None
    for m2 in re.finditer(r"^\}", text[:pos], re.M):
        m = m2
    return m.end() if m else 0


def snprintf_parts(text, buf, lo, hi):
    """snprintf formats writing into `buf` within [lo, hi), in source order."""
    pat = re.compile(SNPRINTF_INTO.format(buf=re.escape(buf)), re.S)
    parts = []
    for sm in pat.finditer(text):
        if sm.start() >= hi or sm.start() < lo:
            continue
        # Splice in any inttypes macros sitting between adjacent literals --
        # the same handling as the call-site scanners, so the two cannot drift
        # apart in what they can read.
        piece = splice_inttypes(text, sm.end("lit"), joined(sm.group("lit")))
        piece = piece.replace("\\n", "").replace("\\t", " ")
        if piece:
            parts.append(piece)
    return parts


def composed(text):
    """Reconstruct buffer-composed log lines.

    Returns [(emit_line, reaches_logfile, prefix, [parts], derived_ok)].
    derived_ok is False when the buffer's content cannot be derived -- the line
    still emits arbitrary text, and saying so is better than inventing a shape
    for it.

    Two shapes are read. The buffer is filled by snprintf in the emitting
    function; or it is filled by a named helper the emitting function calls as
    `helper(buf, sizeof(buf), ...)`, in which case the formats come from that
    helper's body, keyed on ITS parameter name.

    The second hop exists because `Cache probe:` was published as
    `Cache probe:    %s` and nothing else -- nine wordings a consumer could not
    see, in the document whose purpose is that the contract cannot describe
    behaviour we do not have. Platterpus found it from the other end (2026-08-14
    hand-off §5) and asked for a regeneration; a regeneration alone would have
    published the same `%s`, because the composer had never been able to reach
    through a helper.

    Bounded deliberately at ONE hop and at the first parameter. A composer that
    chases arbitrary call graphs would eventually attribute some other
    function's formats to this line, which is the defect this function already
    carries a scar from -- a same-named buffer in another function."""
    out = []
    for m in COMPOSED_EMIT.finditer(text):
        lit_m = COMPOSED_LIT.match(m.group("lit"))
        if not lit_m:
            continue
        prefix = lit_m.group(1).replace("\\n", "").replace("\\t", " ")
        buf = m.group("buf")
        emit_line = text[:m.start()].count("\n") + 1
        lo = func_start(text, m.start())

        # It must actually BE a buffer. Widening the emit regex to allow a
        # prefix also swept up every ordinary `"...%s\n", some_char_ptr` call
        # -- `cdio error: %s` with libcdio's message, `Invalid pregap action
        # %s` with the argv token. Those are complete literals already
        # published in P2, and filing them here as "not derivable" would have
        # added ten rows of noise saying nothing was hidden. A composed line's
        # buffer is a char array declared in the emitting function; that is
        # the discriminator, and it is read from the source rather than
        # guessed from the name.
        if not re.search(r'\bchar\s+' + re.escape(buf) + r'\s*\[',
                         text[lo:m.start()]):
            continue

        parts = snprintf_parts(text, buf, lo, m.start())

        if not parts:
            fm = re.search(FILLED_BY.format(buf=re.escape(buf)),
                           text[lo:m.start()])
            if fm:
                fn = fm.group("fn")
                dm = re.search(FN_DEF.format(fn=re.escape(fn)), text, re.M)
                if dm:
                    body_lo = dm.end()
                    body_hi = next_func_start(text, body_lo)
                    parts = snprintf_parts(text, dm.group("param"),
                                           body_lo, body_hi)

        out.append((emit_line, m.group("target") != "NULL", prefix, parts,
                    bool(parts)))
    return out


def next_func_start(text, pos):
    """Offset of the next column-0 '}' after pos -- the end of the function
    whose body starts at pos. The mirror of func_start(), and the bound that
    stops a helper's formats bleeding into whatever is defined below it."""
    m = re.search(r"^\}", text[pos:], re.M)
    return pos + m.end() if m else len(text)


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

    g = GOTO_ANY.search(window)
    label = g.group(1) if g else None
    if label in GOTO_FATAL:
        by_flow, label = True, None

    if by_flow and by_word:
        return "both"
    if by_flow:
        return "control flow"
    if label and by_word:
        return f"wording + goto {label}"
    if label:
        return f"goto {label}"
    if by_word:
        return "wording"
    return None


TERNARY_LABEL = re.compile(
    r'\s*,\s*[^,()]*?\?\s*(?P<a>"(?:[^"\\]|\\.)*")\s*:\s*(?P<b>"(?:[^"\\]|\\.)*")')


def label_variants(text, end, fmt):
    """Expand a leading `%s` fed by a ternary of two string literals.

    `cyanrip_log(ctx, 0, "%s%c%i %s\\n", cond ? "Underread:      " :
    "Overread:       ", ...)` publishes as `%s%c%i %s`, which pins no text at
    all -- and `Overread:` is a line Platterpus keys on. The label is a
    compile-time literal in the source; enumerating both arms states what the
    line can say instead of leaving a row whose label is a conversion.

    Returns [] when the shape does not apply, so nothing is invented for a `%s`
    fed by a variable."""
    if not fmt.startswith("%s"):
        return []
    m = TERNARY_LABEL.match(text, end)
    if not m:
        return []
    tail = fmt[2:]
    return [joined(m.group("a")) + tail, joined(m.group("b")) + tail]


def wrapper_macros(text):
    """Names of function-like macros in `text` that wrap cyanrip_log() with
    their own first parameter as the format."""
    out = []
    for m in WRAPPER_DEF.finditer(text):
        body = m.group("rest")
        if re.search(r'cyanrip_log\s*\([^;]*?\b' + re.escape(m.group("fmt")) +
                     r'\b', body, re.S):
            out.append(m.group("name"))
    return out


def collect():
    """Walk every log call site. Returns (stable, unstable, fatal)."""
    stable, unstable, fatal = [], [], []
    for name in sorted(os.listdir(SRC)):
        if not name.endswith((".c", ".h")):
            continue
        path = os.path.join(SRC, name)
        text = open(path, encoding="utf-8").read()

        for m in LOGCALL.finditer(text):
            raw = splice_inttypes(text, m.end("lit"), joined(m.group("lit")))
            line = text[:m.start()].count("\n") + 1
            to_log = m.group("target") != "NULL"
            s = raw.replace("\\n", "").replace("\\t", " ").strip()
            if not s:
                continue
            # A leading `%s` fed by a ternary of two literals publishes as a
            # conversion and pins nothing; enumerate the arms instead.
            variants = label_variants(text, m.end("lit"), s) or [s]
            for v in variants:
                rec = (name, line, v, to_log)
                if any(u in v for u in UNSTABLE_SUBSTRINGS) or not to_log:
                    unstable.append(rec)
                else:
                    stable.append(rec)
            ev = evidence(text, m.end(), s)
            if ev:
                fatal.append((name, line, s, to_log, ev))

        # Sites that reach cyanrip_log() through a wrapper macro. The target is
        # the macro's, not the call site's, so `to_log` is read from the macro
        # body once rather than guessed per site.
        for wname in wrapper_macros(text):
            wdef = re.search(r'^#define\s+' + wname + r'\b((?:.*\\\n)*.*)',
                             text, re.M)
            wraps_ctx = bool(wdef and re.search(
                r'cyanrip_log\s*\(\s*(?!NULL)[A-Za-z_]', wdef.group(1)))
            wcall = re.compile(r'\b' + wname +
                               r'\s*\(\s*(?P<lit>"(?:[^"\\]|\\.)*"'
                               r'(?:\s*"(?:[^"\\]|\\.)*")*)', re.S)
            for m in wcall.finditer(text):
                if wdef and wdef.start() <= m.start() <= wdef.end():
                    continue
                raw = splice_inttypes(text, m.end("lit"),
                                      joined(m.group("lit")))
                line = text[:m.start()].count("\n") + 1
                s = raw.replace("\\n", "").replace("\\t", " ").strip()
                if not s:
                    continue
                rec = (name, line, s, wraps_ctx)
                if any(u in s for u in UNSTABLE_SUBSTRINGS) or not wraps_ctx:
                    unstable.append(rec)
                else:
                    stable.append(rec)

        for m in GENOPTCALL.finditer(text):
            raw = splice_inttypes(text, m.end("lit"), joined(m.group("lit")))
            line = text[:m.start()].count("\n") + 1
            s = raw.replace("\\n", "").replace("\\t", " ").strip()
            if not s:
                continue
            # Routed through cyanrip_vlog() by crip_genopt_log(), so it reaches
            # the logfile exactly as any other message does. Every one of them
            # is an argument-parsing failure and genopt returns non-zero, so
            # they are fatal by construction rather than by classification --
            # which is why they carry their own evidence value rather than
            # going through evidence(), whose heuristics are written for
            # cyanrip's own control flow and do not describe a macro body.
            # INFO-level genopt output is --help, which P1 already derives by
            # running the binary. Publishing its fragments in P2 as well would
            # commit us to not rewording text we do not own and did not write,
            # and P2 is exactly the set of lines we undertake not to reword.
            if m.group("level") == "GEN_OPT_LOG_ERROR":
                stable.append((name, line, s, True))
            else:
                unstable.append((name, line, s, True))
            # Only the ERROR level is a failure. GEN_OPT_LOG also prints --help,
            # and filing help text as a fatal message is the same defect as the
            # classifier that once filed "Opening drive..." as one: a line
            # inheriting a neighbour's meaning because the test was too coarse.
            if m.group("level") == "GEN_OPT_LOG_ERROR":
                fatal.append((name, line, s, True, "genopt"))

        for m in STDERRCALL.finditer(text):
            raw = splice_inttypes(text, m.end("lit"), joined(m.group("lit")))
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

    # A -dirty banner means the binary was built from a tree with uncommitted
    # changes, so its SHA does not describe it. Refuse rather than normalise:
    # a contract generated from such a build documents something that is not in
    # any commit, and normalising the marker away would hide exactly what A9
    # added it to expose. This surfaced immediately -- --check reported "stale,
    # regenerate" for a build/ that was merely out of date, which blames the
    # committed file for the state of the build directory.
    if "-dirty" in raw:
        sys.exit(f"refusing to derive the contract from a dirty build: {raw}\n"
                 "The binary was built from a tree with uncommitted changes, so "
                 "its commit does not describe it.\n"
                 "Commit or stash, rebuild, and re-run.")

    return re.sub(r"-g[0-9a-f]{7,40}\)", "-g<commit>)", raw)


def source_hash():
    """A content hash over the sources every file:line in this document refers
    to. The build banner cannot serve as that anchor -- its SHA is normalised
    away, because a generated file cannot contain the hash of the commit that
    adds it. Without an anchor, both sides cited line numbers at each other from
    different trees and each was right about a different one. This hash is
    stable across committing the document, and anyone can recompute it."""
    h = hashlib.sha256()
    for name in sorted(os.listdir(SRC)):
        if name.endswith((".c", ".h")):
            h.update(name.encode())
            h.update(open(os.path.join(SRC, name), "rb").read())
    return h.hexdigest()[:16]


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
    w(f"**Source anchor:** `sha256/16 = {source_hash()}` over `src/*.c` and")
    w("`src/*.h`. **Every `file:line` below refers to exactly that source.** Line")
    w("numbers move between commits, so a citation without an anchor is not")
    w("checkable -- recompute this hash before quoting one back.")
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
    w("- `-v`, `-V` and `--version` all print the version banner and exit 0 **on")
    w("  this fork**. Across the stock line they are not interchangeable and there")
    w("  is no single spelling that works everywhere -- see P6.")
    w("- `-J` and `-I` are mutually exclusive; combining them exits 1.")
    w("- `-d` accepts a device path **or** a TOC/CUE/NRG image file.")
    w("- `-a`/`-t` values are `:`-separated; a literal colon must be escaped `\\:`.")
    w("- `-t N=` and `-l N` are 1-based and validated against the disc's real track")
    w("  count; out of range exits 1 with a message naming both numbers.")
    w("- Multiple `-o` formats produce **one logfile and one cue per format**.")
    w("")
    w("**Units that are not obvious from the line itself:**")
    w("")
    w("- `Total time:` and every `duration:` is **`MM:SS.FF`, where FF is CD frames")
    w("  (1/75 s, range 0-74)** - not centiseconds and not milliseconds. There is")
    w("  **no hours field** and minutes are **not** modulo 60: a 125-minute disc")
    w("  prints `125:00.00`. Real seconds are `mm*60 + ss + ff/75`. Reading `.26` as")
    w("  hundredths is wrong by up to 0.98 s. Upstream changed this shape from")
    w("  `HH:MM:SS.mmm` between 0.9.3 and 0.9.4-rc1 (upstream PR #130), so a")
    w("  consumer that has seen both must discriminate on the colon count: three")
    w("  fields is the legacy form, two is frames.")
    w("- `Pregap length:` is in **frames**, stated in the line.")
    w("- `Sample peak level:` is a percentage of full scale **and** dBFS;")
    w("  `True peak level:` is dBFS only.")
    w("- Paranoia counters are **raw callback counts**, not rates or scores, and are")
    w("  only comparable between tracks of the same disc on the same drive.")
    w("- **Paranoia counter scope (A8).** A per-track `Paranoia status counts:`")
    w("  block covers **the final `-Z` pass for that track only**; the disc-level")
    w("  block is **cumulative across every pass the invocation performed**. They")
    w("  are therefore equal only at `-Z 0`, where there is exactly one pass -")
    w("  confirmed on real hardware by Platterpus (round 7: 22055/1600/54/468,")
    w("  summing exactly across 14 tracks). Under `-Z N` the per-track figures sum")
    w("  to **less** than the disc block by the reads the earlier passes did. A")
    w("  consumer cross-checking the two blocks must condition on `-Z`.")
    w("- **Paranoia counter denominator under `-l` (Q10).** The disc-level block")
    w("  counts only what **this invocation** read, not the whole disc. Under")
    w("  `-l 3,5` it covers tracks 3 and 5 and nothing else, and `Rip completed:`")
    w("  says `yes (2 of 14 tracks)`. The denominator is the invocation, never the")
    w("  TOC.")
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
    w("### P2a - Composed lines")
    w("")
    w("Lines assembled into a buffer and emitted through a trailing `%s`. The")
    w("emitting call site shows a consumer nothing, so the pieces are reconstructed")
    w("here from the `snprintf` formats that build the buffer, in source order.")
    w("Segments after the first are conditional.")
    w("")
    w("The buffer is either filled in the emitting function, or filled by a helper")
    w("the emitting function calls as `helper(buf, sizeof(buf), ...)` -- one hop, and")
    w("only through the helper's first parameter. `Cache probe:` is the second shape,")
    w("and until this generator could follow that hop the contract published it as a")
    w("bare `%s` with none of its wordings, in the document whose whole purpose is")
    w("that the contract cannot describe behaviour we do not have.")
    w("")
    for src_name in ("cyanrip_main.c", "cache_probe.c"):
        src_text = open(os.path.join(SRC, src_name), encoding="utf-8").read()
        for emit_line, to_log, prefix, parts, ok in composed(src_text):
            w(f"**`{src_name}:{emit_line}`** - reaches logfile: "
              f"{reaches_cell(to_log)}")
            w("")
            if prefix:
                w(f"Fixed prefix: `{prefix}`")
                w("")
            if not ok:
                w("Not derivable: the buffer is built neither by `snprintf` in this")
                w("function nor by a `helper(buf, sizeof(buf), ...)` call in it. It")
                w("emits arbitrary text - here, the generated CUE sheet echoed back to")
                w("the terminal a line at a time. **Do not pattern-match this row**; a")
                w("pattern built from its `\"%s\"` would match every line in the log.")
                w("")
                continue
            w("| # | Segment |")
            w("|---|---|")
            for i, part in enumerate(parts):
                w(f"| {i} | `{part}` |")
            w("")
            w("Segment 0 is always present; the rest are appended conditionally.")
            w("")

    w("## P3 - Unstable wording, and stdout-only routing")
    w("")
    w("**This section answers two independent questions, and a row can be here for")
    w("either.** Conflating them is what put `cyanrip_encode.c` and two other rows in")
    w("both P3 and P5 and made the membership look contradictory (Platterpus, round 5")
    w("A2):")
    w("")
    w("- **Unstable wording** - the text may be reworded without a handshake round.")
    w("  Do not depend on the exact string.")
    w("- **not directly** - the call passes no context, so it never writes to a")
    w("  logfile itself. It is still buffered: anything said *before* the logfile is")
    w("  opened is replayed into it, delimited by")
    w("  `--- output before this log was opened ---` and `--- end of pre-log output ---`,")
    w("  after the header block. Anything said *after* it is opened reaches stdout")
    w("  only. Which of the two a given row is depends on when it runs, and that is")
    w("  not derivable from the call site - **it needs a run to settle**.")
    w("")
    w("**Appearing here does not mean a line is harmless.** A line can be")
    w("stdout-only *and* a failure diagnostic; those rows are also in P5, and P5 is")
    w("the authority on whether something is reachable on a failure path. Match")
    w("P5 rows for error detection even when they appear here.")
    w("")
    w("| File:line | Line | Reaches logfile? |")
    w("|---|---|---|")
    seen = set()
    for name, line, s, to_log in unstable:
        if s in seen:
            continue
        seen.add(s)
        disp = (s.replace("|", "\\|") or "(empty / formatting only)")
        w(f"| `{name}:{line}` | `{disp}` | {reaches_cell(to_log)} |")
    w("")
    w("Also unstable, and **not ours**: the loudness block FFmpeg's `ebur128` filter")
    w("prints (" + ", ".join(f"`{x}`" for x in FFMPEG_OWNED[:4]) + ", ...). That wording")
    w("belongs to libavfilter and moves when FFmpeg does. Prefer the")
    w("`Sample peak level:` and `True peak level:` lines in P2, which are ours,")
    w("are gated on a completed rip, and each say which peak they report.")
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
    w("Argument validation runs **before the logfile is opened**. Those diagnostics are")
    w("buffered and replayed into the logfile if one is later opened, so a consumer")
    w("reading the log does see them. **But a run that refuses during argument")
    w("validation opens no logfile at all**, and for that class the only artifact is")
    w("the `-j` diagnostics record, which is written for those runs and is off unless")
    w("asked for. Without `-j`, a refused run leaves its reason on stdout and nowhere")
    w("else.")
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
    w("The search stops at the next `if`/`for`/`while`/`switch`, so a message is")
    w("only credited with an exit that is its own -- without that cut,")
    w("`Opening drive...` reads as fatal because the *next* statement's if-block")
    w("returns `AVERROR`. It deliberately does *not* stop at the next log call:")
    w("two arms of one if/else that both log and then converge on a single exit")
    w("must carry the same class.")
    w("")
    w("| File:line | Message | Evidence | Reaches logfile? |")
    w("|---|---|---|---|")
    seen = {}
    for name, line, s, to_log, ev in fatal:
        if s in seen:
            continue
        seen[s] = ev
        disp = s.replace("|", "\\|")
        w(f"| `{name}:{line}` | `{disp}` | {ev} | {reaches_cell(to_log)} |")
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

    w("## P6 - Version flags across the stock line")
    w("")
    w("**STATED, NOT DERIVED.** Every other section here comes from this build or")
    w("this source tree. This one is about *upstream* builds, which this generator")
    w("cannot introspect, so it is measured by hand and cited to commits. It is")
    w("here because a consumer probing for cyanrip's version needs it and nowhere")
    w("else carries it -- and because the sentence it replaces was wrong.")
    w("")
    w("P1 used to say **\"prefer `--version`, it has never changed and never")
    w("will\"**. That is false: `--version` did not exist before genopt. The claim")
    w("was prose, it was cited in a handshake lap as a recommendation, and a")
    w("five-minute build disproved it. The `cli` scenario pins all three spellings")
    w("**for this fork**, which is a real test whose scope is narrower than the")
    w("claim it was cited for.")
    w("")
    w("Measured 2026-08-04 by building each tree and running the binary:")
    w("")
    w("| build | `--version` | `-V` | `-v` |")
    w("|---|---|---|---|")
    w("| stock, pre-genopt (`442de2a^`, `meson.build` says `0.9.3`) | **exit 1** | exit 0 | **exit 1** |")
    w("| stock, genopt onward (`master` = `958e1ad`, 0.9.4-rc1) | exit 0 | **exit 1** | exit 0 |")
    w("| **this fork** (`e1d800e` onward) | exit 0 | exit 0 | exit 0 |")
    w("")
    w("- Pre-genopt uses plain `getopt()` -- `#include <getopt.h>`, a short-only")
    w("  optstring containing `V`, **no long options at all** -- so `--version` is")
    w("  rejected by getopt before cyanrip sees it, on stderr, prefixed with the")
    w("  binary's own path.")
    w("- `442de2a` *\"Replace getopt option parsing with genopt\"* moved the flag to")
    w("  `-v`/`--version` and dropped `-V`.")
    w("- `e1d800e` restores `-V` as an alias **on this fork only**; it is not")
    w("  upstream.")
    w("")
    w("**`-V` and `--version` are exactly complementary across the stock line.**")
    w("No single spelling answers every stock build, so a probe over stock needs at")
    w("least two attempts by construction -- no ordering reduces it to one. Only")
    w("this fork accepts all three, and that is a property of ours, not something")
    w("to rely on for stock.")
    w("")
    w("The `version_matrix` test scenario re-checks the two upstream claims from")
    w("git -- that `442de2a^` parses with `getopt` and no long options, and that")
    w("`442de2a` onward has no `-V` in its option table -- so this section fails")
    w("when the commits it cites stop saying what it says they say.")
    w("")
    w("### P6a - What a rejection actually prints")
    w("")
    w("**Appendix, deliberately not table cells.** Platterpus asked for the exact")
    w("text so nobody has to guess it, and asked for it kept out of the table so")
    w("it does not read like something to match on (round 7 lap 19 §C). Both")
    w("halves of that are right: **key on the exit code, not on these strings.**")
    w("They are upstream's wording, not ours, and one of them is not even")
    w("constant.")
    w("")
    w("Measured 2026-08-04 by running each build:")
    w("")
    w("| build, flag | stream | text |")
    w("|---|---|---|")
    w("| stock pre-genopt, `--version` | **stderr** | `<argv[0]>: invalid option -- '-'` |")
    w("| stock pre-genopt, `-v` | **stderr** | `<argv[0]>: invalid option -- 'v'` |")
    w("| stock genopt onward, `-V` | **stdout** | `Unable to parse command line argument: -V` |")
    w("")
    w("Three things a consumer would otherwise have to discover the hard way:")
    w("")
    w("- **The two stock builds disagree about which stream carries the**")
    w("  **diagnosis.** Pre-genopt writes to stderr, because the message is")
    w("  getopt's own; genopt writes to stdout. A probe capturing only one stream")
    w("  sees nothing at all from one of the two.")
    w("- **The pre-genopt text is not constant.** getopt prefixes `argv[0]`")
    w("  verbatim, so the line contains the path the binary was invoked by. Only")
    w("  the `: invalid option -- 'X'` suffix is stable.")
    w("- **One line each**, no usage block follows.")
    w("")
    w("On **this fork** the genopt message is routed through `cyanrip_log()`, so")
    w("it reaches stdout, the logfile if one is open, and the `-j` record. That")
    w("is a fork property; stock does neither.")
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
