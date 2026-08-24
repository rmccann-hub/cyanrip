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
import json
import os
import re
import subprocess
import sys
import tempfile

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

# Lines written STRAIGHT to the logfile, never through cyanrip_log().
#
# `Log FUN512: ` is the one that exposed this: it is the checksum OVER the log,
# so it has to be appended after the log is otherwise finished and cannot go
# through the capture path. The scanner knew cyanrip_log(), genopt and
# fprintf(stderr) and had no pattern for this -- so a stable line present in
# every logfile, which `-Y/--verify-log` round-trips, has been absent from
# every provider contract ever published. Found 2026-08-15 by building the
# self-check Platterpus asked for in their §6 (extract every label from a real
# rip log, fail if any is missing from the contract) rather than by reading the
# generator again.
#
# Routing is the mirror of the `not directly` class: these reach the LOGFILE and
# not stdout, where a cyanrip_log(NULL, ...) reaches stdout and not the logfile.
LOGFILECALL = re.compile(
    r'fprintf\s*\(\s*ctx->logfile\s*\[[^\]]*\]\s*,\s*'
    r'(?P<macro>[A-Z][A-Z0-9_]*\s+)?'
    r'(?P<lit>"(?:[^"\\]|\\.)*"(?:\s*"(?:[^"\\]|\\.)*")*)', re.S)

# Object-like macros holding a bare string, so a format spliced together as
# `MARKER "%s\n"` resolves instead of publishing half of itself.
OBJ_MACRO = re.compile(
    r'^#define\s+(?P<name>[A-Z][A-Z0-9_]*)\s+"(?P<val>(?:[^"\\]|\\.)*)"\s*$', re.M)

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
    r'snprintf\s*\(\s*{buf}\b(?P<off>[^;,]*),[^;]*?,\s*'
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
    """snprintf formats writing into `buf` within [lo, hi), in source order.

    Returns [(piece, writes_whole_buffer)].

    The second field is what says whether the segments COMBINE or ALTERNATE,
    and it is derived rather than assumed. `snprintf(buf, ...)` writes from the
    start and NUL-terminates, so it replaces whatever was there; only a write
    at an offset -- `snprintf(buf + n, ...)` -- can append. That is a fact
    about the call, readable from the call.

    It exists because this file used to print, under every composed row and
    without deriving anything, *"Segment 0 is always present; the rest are
    appended conditionally."* For `cache_probe.c` that is flatly false: the
    nine segments are arms of a `switch`, each ending in `return`, so exactly
    one is ever emitted. A consumer building a matcher from that sentence would
    have written a concatenation pattern for a line that alternates -- and it
    is `Cache probe:`, the one line in round 14 whose real shape has never been
    seen on hardware. A hardcoded prose claim inside a generated document is a
    guess wearing a derivation's clothes, which is the exact failure this
    generator exists to prevent."""
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
            parts.append((piece, not sm.group("off").strip()))
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


def object_macros():
    """Every `#define NAME "literal"` in the tree, by name.

    Tree-wide rather than per-file on purpose: CRIP_LOG_FUN512_MARKER is
    defined in fun512.h and used in cyanrip_log.c, and a per-file table would
    have resolved neither."""
    out = {}
    for name in sorted(os.listdir(SRC)):
        if name.endswith((".c", ".h")):
            text = open(os.path.join(SRC, name), encoding="utf-8").read()
            for m in OBJ_MACRO.finditer(text):
                out[m.group("name")] = m.group("val")
    return out


def collect():
    """Walk every log call site. Returns (stable, unstable, fatal)."""
    stable, unstable, fatal = [], [], []
    macros = object_macros()
    for name in sorted(os.listdir(SRC)):
        if not name.endswith((".c", ".h")):
            continue
        path = os.path.join(SRC, name)
        text = open(path, encoding="utf-8").read()

        # Written straight to the logfile: reaches the logfile and NOT stdout.
        for m in LOGFILECALL.finditer(text):
            raw = splice_inttypes(text, m.end("lit"), joined(m.group("lit")))
            if m.group("macro"):
                key = m.group("macro").strip()
                if key not in macros:
                    # Publishing the tail alone would be a format missing its
                    # own label -- worse than omitting the row, because it
                    # looks complete.
                    continue
                raw = macros[key] + raw
            line = text[:m.start()].count("\n") + 1
            s = raw.replace("\\n", "").replace("\\t", " ").strip()
            if not s:
                continue
            rec = (name, line, s, True)
            if any(u in s for u in UNSTABLE_SUBSTRINGS):
                unstable.append(rec)
            else:
                stable.append(rec)

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


def blank_noncode(text):
    """Comments and string literals replaced by spaces, newlines preserved.

    A grep hit is not a fact, and this file has already shipped two findings
    that were prose: a function name matched inside a TODO, and a search for
    cache handling matched a comment written an hour earlier. Scanning for
    `return` or `exit(` in a file whose comments DISCUSS returns and exits will
    find them there -- the first run of exit_surface() reported three phantom
    paths, every one of them a sentence explaining the real code beside it.

    Line numbers must survive, because every citation in this document is a
    file:line. So content is replaced rather than removed.
    """
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join(ch if ch == "\n" else " " for ch in text[i:j]))
            i = j
        elif c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif c in "\"'":
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == "\\" else 1
            j = min(j + 1, n)
            out.append("".join(ch if ch == "\n" else " " for ch in text[i:j]))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def enum_values():
    """Every enumerator in src/*.h that has an explicit integer initialiser,
    with the trailing comment on its line.

    Only explicit initialisers, on purpose. Implicit successors would have to be
    counted through the enum, and a miscount there produces a *plausible* wrong
    number in a document whose whole job is not doing that. Every exit code this
    program returns is explicitly valued (see CRIPLogVerifyExit in fun512.h), so
    the restriction costs nothing and an enumerator that stops being explicit
    shows up as unresolved rather than as a guess.

    The comment is captured because for the exit codes it IS the meaning, in the
    source, next to the value -- which is the only place a meaning can be
    derived from rather than editorialised into this file.
    """
    out = {}
    for name in sorted(os.listdir(SRC)):
        if not name.endswith(".h"):
            continue
        path = os.path.join(SRC, name)
        for i, line in enumerate(open(path, encoding="utf-8"), 1):
            m = re.match(r"\s*([A-Z][A-Z0-9_]*)\s*=\s*(-?\d+)\s*,?"
                         r"\s*(?:/\*\s*(.*?)\s*\*/)?\s*$", line)
            if m:
                out[m.group(1)] = (int(m.group(2)), m.group(3) or "",
                                   f"{name}:{i}")
    return out


def _fn_body(text, signature_re):
    """The text of the first function whose signature matches, brace-balanced.

    Brace counting rather than a regex to the next "^}": cyanrip_run() contains
    nested blocks at column 0 in no case today, but a function that gained one
    would silently truncate the body and drop every return past it -- which is
    the failure mode that makes a derivation quietly incomplete.
    """
    m = signature_re.search(text)
    if not m:
        return None, 0
    start = text.index("{", m.start())
    depth, i = 0, start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1], text[:start].count("\n") + 1
        i += 1
    return text[start:], text[:start].count("\n") + 1


def exit_surface():
    """Every distinct process exit value, and every path we could NOT resolve.

    WHY THIS IS NOT A LIST OF DIGITS ANY MORE. The previous version scanned for
    `exit\((\d+)\)` across src/*.c and for `^\s*return (\d+);` inside main().
    Both halves were wrong in the same direction:

      * main() does not return a literal. It returns `rc`, which is
        cyanrip_run()'s value, so every real exit code was out of scope.
      * the codes are not literals. --verify-log returns CRIP_LOG_EXIT_VALID and
        a variable `ec` assigned from four more enumerators.

    So it reported `1` while the binary returned 0, 1, 2, 3, 4 and 5 -- and the
    P4 table above it was hardcoded prose saying "1, Every failure, without
    exception", which is a hand-written claim inside a generated document, the
    exact defect this file exists to prevent. Platterpus found it in round 12
    lap 2 §E1 by reading the delivered contract against our own lap.

    HOW IT DERIVES NOW. Start at main()/wmain(); follow `return <var>;` one hop
    to the function that assigned it; enumerate every `return <expr>;` in the
    functions so reached, plus every exit()/_exit() call anywhere in src/. An
    expression that is a literal or a known enumerator resolves to a value; an
    expression that is a variable resolves to every value assigned to that
    variable inside the same function. Anything left over is REPORTED, with
    file:line, rather than dropped -- an exit path we cannot read is a fact a
    consumer needs, and silently omitting it is how a contract comes to describe
    a program that does not exist.

    Returns (resolved, unresolved, chain):
      resolved   {int: [evidence strings]}
      unresolved [(where, expression)]
      chain      the functions followed, in order, so a reader can check the
                 hop rather than trust it.
    """
    enums = enum_values()
    resolved, unresolved, chain = {}, [], []

    def note(value, where):
        resolved.setdefault(value, []).append(where)

    def resolve(expr, where, body):
        """expr -> value(s), or record it as unresolved."""
        expr = " ".join(expr.split())
        if re.fullmatch(r"-?\d+", expr):
            note(int(expr), where)
            return
        # `cond ? A : B` where both arms are constants. Resolved rather than
        # reported, because this IS the normal rip's exit -- `(err_cnt ||
        # fatal_abort) ? 1 : 0` -- and a contract that files the program's main
        # exit path under "could not resolve" is describing a different program.
        # Only when BOTH arms resolve: one unreadable arm makes the whole
        # expression unreadable, and half an answer here is worse than none.
        tern = re.fullmatch(r".+\?\s*([^:?]+?)\s*:\s*([^:?]+?)\s*", expr)
        if tern:
            arms = [a.strip() for a in tern.groups()]
            vals = [int(a) if re.fullmatch(r"-?\d+", a)
                    else (enums[a][0] if a in enums else None) for a in arms]
            if all(v is not None for v in vals):
                for v in vals:
                    note(v, f"{where} (ternary)")
                return
        if expr in enums:
            note(enums[expr][0], f"{where} (`{expr}`)")
            return
        # A bare identifier: every value assigned to it in this function. Bounded
        # to the function on purpose -- following it further would be a dataflow
        # analysis, and a wrong one would be indistinguishable from a right one
        # in the output.
        if re.fullmatch(r"[a-z_][a-z0-9_]*", expr) and body is not None:
            hits = re.findall(rf"\b{re.escape(expr)}\s*=\s*([^;]+);", body)
            if hits:
                for h in hits:
                    h = h.strip()
                    if re.fullmatch(r"-?\d+", h):
                        note(int(h), f"{where} (via `{expr}`)")
                    elif h in enums:
                        note(enums[h][0], f"{where} (via `{expr}` = `{h}`)")
                    else:
                        unresolved.append((where, f"{expr} = {h}"))
                return
        unresolved.append((where, expr))

    main_src = blank_noncode(
        open(os.path.join(SRC, "cyanrip_main.c"), encoding="utf-8").read())

    # The entry points, and one hop from each. wmain() is the Windows entry
    # point and is compiled instead of main() there, so both are followed.
    frontier = [(re.compile(r"^int\s+(?:w)?main\s*\(", re.M), "main()")]
    seen = set()
    for _ in range(4):                       # depth cap, stated rather than felt
        if not frontier:
            break
        sig, fname = frontier.pop(0)
        body, first_line = _fn_body(main_src, sig)
        if body is None:
            continue
        if fname in seen:
            continue
        seen.add(fname)
        chain.append(fname)

        for m in re.finditer(r"\breturn\s+([^;]+);", body):
            expr = m.group(1).strip()
            line = first_line + body[:m.start()].count("\n")
            where = f"cyanrip_main.c:{line}"
            # `return <var>;` where <var> was assigned from a call: follow the
            # call rather than the variable, one hop.
            call = re.search(rf"\b{re.escape(expr)}\s*=\s*([a-z_][a-z0-9_]*)\s*\(",
                             body) if re.fullmatch(r"[a-z_][a-z0-9_]*", expr) else None
            if call:
                frontier.append(
                    (re.compile(rf"^(?:static\s+)?int\s+{call.group(1)}\s*\(",
                                re.M), f"{call.group(1)}()"))
                continue
            resolve(expr, where, body)

    # exit()/_exit() anywhere. Headers included: genopt.h is a header and carries
    # argument-parsing failures, and scanning only .c is how the old version
    # would have missed them had they been there.
    for name in sorted(os.listdir(SRC)):
        if not name.endswith((".c", ".h")):
            continue
        path = os.path.join(SRC, name)
        text = blank_noncode(open(path, encoding="utf-8").read())
        for i, line in enumerate(text.splitlines(), 1):
            for m in re.finditer(r"\b_?exit\s*\(\s*([^)]+?)\s*\)", line):
                resolve(m.group(1), f"{name}:{i}", None)

    return resolved, unresolved, chain


# The build tag inside the banner. Normalised in --check ONLY, never in the
# written file, and the split is the whole point of E3's fix.
BUILD_TAG = re.compile(r"-g[0-9a-f]{7,40}\)")


def md_cell(s):
    """A string safe to drop into a GFM table cell.

    `|` is one of the ten characters the substitution table names, and an
    unescaped one splits the row -- P7b rendered its `|` row with two extra
    columns, silently, because a pipe inside a code span is still a pipe to
    the table parser. Backslash-escaping is the only thing GFM honours here.
    """
    return s.replace("|", "\\|")


def c_char(lit):
    """The character a C single-quoted literal denotes.

    The table's `from` column contains `'\\\\'` and its `to` column `'\\''`, and
    printing those verbatim into the contract would publish the C escape rather
    than the character -- a consumer matching on it would look for a backslash
    followed by a quote. Unknown escapes are returned unchanged rather than
    guessed at, so a new one shows up as itself instead of as a wrong glyph.
    """
    return {"\\\\": "\\", "\\'": "'", "\\\"": "\"",
            "\\n": "\n", "\\t": "\t", "\\r": "\r",
            "\\0": "\0"}.get(lit, lit)


def sanitize_table():
    """Rows of `crip_char_replacement[]` in src/naming.c, in table order.

    Derived from the initialiser rather than transcribed. This table IS the
    answer to "what does -T do to a filename", and a hand-copied second copy of
    it inside a generated document is the exact defect this generator exists to
    prevent -- it would look authoritative and rot the first time a row moved.

    Returns (rows, unresolved). A row is (index, from_char, to_char, to_utf8,
    availability_macro). Anything in the initialiser that does not parse is
    REPORTED rather than dropped: a substitution we cannot read is a fact the
    consumer needs.
    """
    text = open(os.path.join(SRC, "naming.c"), encoding="utf-8").read()
    m = re.search(r"crip_char_replacement\[\]\s*=\s*\{(.*?)\n\};", text, re.S)
    if not m:
        return [], ["crip_char_replacement[] initialiser not found in naming.c"]
    base = text[:m.start(1)].count("\n") + 1
    rows, unresolved = [], []
    idx = 0
    for off, raw in enumerate(m.group(1).splitlines()):
        s = raw.strip()
        if not s or s.startswith("/*") or s.startswith("*"):
            continue
        if re.match(r"\{\s*0\s*\}\s*,?$", s):          # the terminator
            continue
        r = re.match(r"\{\s*'(\\?.)'\s*,\s*'(\\?.)'\s*,\s*\"(.*?)\"\s*,"
                     r"\s*(\w+)\s*\}\s*,?$", s)
        if r:
            rows.append((idx, r.group(1), r.group(2), r.group(3), r.group(4)))
            idx += 1
        else:
            unresolved.append(f"naming.c:{base + off}: {s}")
    return rows, unresolved


def sanitize_modes():
    """The four -T spellings, the enum constant each selects, the default, and
    which constants take the OS-availability path and which glyph field.

    Every part of this is read from control flow rather than from the help
    text: the help string lists the spellings but says nothing about what any
    of them does, and it is the *behaviour* Platterpus has to reproduce.
    """
    naming = blank_noncode(
        open(os.path.join(SRC, "naming.c"), encoding="utf-8").read())
    # The spellings ARE string literals, so this one derivation has to read the
    # raw text -- blank_noncode() would erase the very thing being extracted.
    # It is anchored on `strcmp(sanitize, ...)` followed by the assignment, so
    # a mention of "unicode" in a comment cannot contribute a spelling: a
    # comment does not contain that call shape.
    raw_main = open(os.path.join(SRC, "cyanrip_main.c"), encoding="utf-8").read()

    unresolved = []

    # -T "<spelling>" -> enum constant, from the strcmp chain.
    spellings = re.findall(
        r'strcmp\(\s*sanitize\s*,\s*"([^"]+)"\s*\)\s*\)\s*'
        r'settings\.sanitize_method\s*=\s*(\w+)\s*;', raw_main)
    if not spellings:
        unresolved.append("cyanrip_main.c: -T strcmp chain not found")

    # The default: the one assignment that is not part of the strcmp chain.
    default, default_at = None, None
    for i, line in enumerate(raw_main.splitlines(), 1):
        m = re.match(r"\s*settings\.sanitize_method\s*=\s*(\w+)\s*;\s*$", line)
        if m:
            if default is not None:
                unresolved.append(
                    f"cyanrip_main.c:{i}: a second unconditional default "
                    f"({m.group(1)}) -- two declarations are ambiguous, not "
                    f"'the first one'")
            default, default_at = m.group(1), i

    # Which constants take the availability path.
    m = re.search(r"int\s+os_sanitize\s*=\s*(.*?);", naming, re.S)
    os_modes = set(re.findall(r"==\s*(\w+)", m.group(1))) if m else set()
    if not m:
        unresolved.append("naming.c: os_sanitize expression not found")

    # Which constants emit rep->to, and which emit rep->to_u. Derived from the
    # branch that actually writes, not from the constant's name -- CRIP_
    # SANITIZE_OS_SIMPLE reads like "simple" but nothing guarantees the source
    # agrees, and a contract that assumes it is guessing.
    glyph = {}
    for cond, body in re.findall(
            r"if\s*\((ctx->settings\.sanitize_method[^{]*?)\)\s*\{(.*?)\n\s*\}",
            naming, re.S):
        field = None
        if re.search(r"rep->to_u", body):
            field = "to_u"
        elif re.search(r"rep->to\b", body):
            field = "to"
        if field:
            for c in re.findall(r"==\s*(\w+)", cond):
                glyph[c] = field

    modes = []
    for spelling, const in spellings:
        if const not in glyph:
            unresolved.append(
                f"naming.c: no branch in crip_bprint_sanitize() writes a glyph "
                f"for {const}")
        modes.append((spelling, const, const in os_modes, glyph.get(const)))
    return modes, default, default_at, unresolved


def sanitize_availability():
    """HAS_* macro values by platform, from src/os_compat.h's own #if structure.

    Reported as a structure rather than as "this build's values" on purpose:
    this generator runs on one platform and the contract describes the program,
    so collapsing the conditional into whatever the build machine happens to be
    would state a per-OS fact at the scope of a single OS. Both branches are
    emitted and the reader picks their own.

    Returns (overrides, defaults, unread):
      overrides  {condition: {macro: (value, line)}}
      defaults   {macro: (value, comment, line)}
      unread     macros defined here that no file reads
    """
    path = os.path.join(SRC, "os_compat.h")
    lines = open(path, encoding="utf-8").read().splitlines()
    overrides, defaults = {}, {}
    guard, pend = [], None
    for i, raw in enumerate(lines, 1):
        s = raw.strip()
        m = re.match(r"#\s*if\s+defined\s*\(\s*(\w+)\s*\)\s*$", s)
        if m:
            guard.append(m.group(1)); pend = None; continue
        m = re.match(r"#\s*ifndef\s+(\w+)\s*$", s)
        if m:
            guard.append("!" + m.group(1)); pend = m.group(1); continue
        if re.match(r"#\s*if(def)?\b", s):
            guard.append(None); pend = None; continue
        if re.match(r"#\s*endif\b", s):
            if guard:
                guard.pop()
            pend = None; continue
        if re.match(r"#\s*el(se|if)\b", s):
            pend = None; continue
        m = re.match(r"#\s*define\s+(HAS_[A-Z0-9_]*)\s+(-?\d+)\s*"
                     r"(?://\s*(.*?)\s*)?$", s)
        if m:
            name, val, cmt = m.group(1), int(m.group(2)), m.group(3) or ""
            if pend == name:
                defaults[name] = (val, cmt, i)
            else:
                cond = guard[-1] if guard and guard[-1] else "?"
                overrides.setdefault(cond, {})[name] = (val, i)

    named = set(defaults)
    for d in overrides.values():
        named |= set(d)

    # "Defined and never read" is derivable, so it is derived. A prose note
    # saying so would go stale the moment somebody wired the macro up; this
    # line disappears by itself when they do.
    unread = []
    for macro in sorted(named):
        read = False
        for name in sorted(os.listdir(SRC)):
            if not name.endswith((".c", ".h")):
                continue
            text = blank_noncode(
                open(os.path.join(SRC, name), encoding="utf-8").read())
            for line in text.splitlines():
                if re.match(r"\s*#\s*(define|ifndef|undef)\s+" + macro + r"\b",
                            line):
                    continue
                if re.search(r"\b" + macro + r"\b", line):
                    read = True
                    break
            if read:
                break
        if not read:
            where = defaults.get(macro)
            if where is None:
                for cond, d in overrides.items():
                    if macro in d:
                        where = (d[macro][0], cond, d[macro][1])
            unread.append((macro, where))
    return overrides, defaults, unread


def sanitize_writes():
    """Every output-buffer write inside crip_bprint_sanitize(), in order.

    This is what backs P7b's passthrough claim. "The table is the only
    transformation" is an absence, and an absence asserted in prose goes
    quietly wrong the first time somebody adds a fifth branch -- the same shape
    as "there is no -V", which was true when written and one upstream commit
    from being the misleading kind of true. Enumerating the writes means a new
    one appears in the document as an unclassified row instead of not appearing
    at all.
    """
    text = open(os.path.join(SRC, "naming.c"), encoding="utf-8").read()
    body, start = _fn_body(blank_noncode(text),
                           re.compile(r"crip_bprint_sanitize\s*\([^;{}]*?\)\s*\n?\s*\{"))
    if body is None:
        return []
    out = []
    for m in re.finditer(r"(av_bprint_\w+)\s*\(([^;{}]*?)\)\s*;", body, re.S):
        args = [a.strip() for a in m.group(2).split(",")]
        line = start + body[:m.start()].count("\n")
        out.append((line, m.group(1), args[1] if len(args) > 1 else "?"))
    return out


def sanitize_callsites():
    """Every crip_bprint_sanitize() call and the sanitize_fwdslash argument it
    passes, because that argument decides whether '/' is a separator or a
    character -- and it is the one part of the substitution table that is not a
    property of the mode at all."""
    text = open(os.path.join(SRC, "naming.c"), encoding="utf-8").read()
    blanked = blank_noncode(text)
    out = []
    for m in re.finditer(r"crip_bprint_sanitize\s*\(([^;{}]*?)\)\s*;", blanked, re.S):
        args = [a.strip() for a in m.group(1).split(",")]
        line = blanked[:m.start()].count("\n") + 1
        out.append((line, args[-1] if args else "?"))
    return out

def diag_schema_literal():
    """The `schema` string diagnostics.c emits, and its file:line.

    Read from the source rather than from a record, because it is the one field
    a consumer is expected to gate on and the contract must say what THIS tree
    emits even if no record were available to read.
    """
    path = os.path.join(SRC, "diagnostics.c")
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        m = re.search(r'\\"schema\\":\s*\\"([^\\]+)\\"', line)
        if m:
            return m.group(1), f"diagnostics.c:{i}"
    return None, None


def diag_source_keys():
    """Every JSON key literal in diagnostics.c's emitter, in emission order.

    The record is built by a run of av_bprintf() calls with the key names
    spelled into the format strings, so the keys ARE derivable from source.
    This half exists to catch the opposite error from reading records: a key
    the code can emit under a condition no sample reaches would be invisible to
    a record-only derivation, and a contract that lists only what happened to
    be exercised is a coverage report wearing a schema's clothes.
    """
    path = os.path.join(SRC, "diagnostics.c")
    text = open(path, encoding="utf-8").read()
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r'\\"([A-Za-z_][A-Za-z0-9_]*)\\":', line):
            out.append((m.group(1), i))
    return out


def diag_walk(node, path, acc):
    """Collect {json path: (types seen, nullable)} from one record."""
    if isinstance(node, dict):
        # The object itself is a TYPE, not just a parent. Without this a field
        # that is an object in one record and null in another accumulated no
        # type at all and rendered as "null in every record here" -- which is
        # exactly what `rip` did, and it is false: `rip` is the record's
        # largest object on any run that opened a disc.
        if path:
            ts, _nul = acc.setdefault(path, (set(), False))
            ts.add("object")
        for k, v in node.items():
            p = f"{path}.{k}" if path else k
            diag_walk(v, p, acc)
            t, nullable = acc.setdefault(p, (set(), False))
            if v is None:
                acc[p] = (t, True)
    elif isinstance(node, list):
        t, nullable = acc.setdefault(path, (set(), False))
        t.add("array")
        for v in node:
            diag_walk(v, path + "[]", acc)
    else:
        t, nullable = acc.setdefault(path, (set(), False))
        if node is None:
            acc[path] = (t, True)
        elif isinstance(node, bool):
            t.add("bool")
        elif isinstance(node, int):
            t.add("int")
        elif isinstance(node, float):
            t.add("float")
        else:
            t.add("string")


def diag_records(binary):
    """Three real records, covering the three shapes the emitter has.

    Named rather than globbed, so a shape that stops being covered is a visible
    act. The third is PRODUCED here rather than committed, because the refusal
    path leaves no logfile and therefore has no golden artifact -- and it is
    reached from the argument table (`-J` with `-I`), which involves no disc and
    no network. A check that reaches the network is not evidence about this
    program; an earlier version of a related test drove the refusal through a
    MusicBrainz lookup and its result depended on whether that lookup failed by
    not-found or by timeout.

    Returns (records, missing) -- a record that cannot be read is REPORTED, not
    skipped, or this section silently narrows to whatever happens to be on disk.
    """
    want = [
        ("a completed rip", os.path.join("docs", "golden-reference.diagnostics.json")),
        ("a rip stopped by a signal", os.path.join("docs", "sample-interrupted.diagnostics.json")),
    ]
    records, missing = [], []
    for what, rel in want:
        if os.path.exists(rel):
            try:
                records.append((what, rel, json.load(open(rel, encoding="utf-8"))))
            except ValueError as e:
                missing.append(f"{rel}: not valid JSON ({e})")
        else:
            missing.append(f"{rel}: not found")

    # Two more, produced here. The refusal path leaves no logfile and so has
    # no golden artifact; `-k 0` reaches a read_stalls shape the other three
    # cannot, which the source/record reconciliation below found by flagging
    # `reason` as emitted-but-never-observed. Adding the run that observes it
    # is the fix; leaving the row in the disagreement list would have been a
    # documented hole where a covered field was one flag away.
    produced = [
        ("a run refused during argument validation", ["-J", "-I"]),
        ("a run with stall reporting off (-k 0)", ["-J", "-I", "-k", "0"]),
    ]
    with tempfile.TemporaryDirectory() as td:
        for what, extra in produced:
            out = os.path.join(td, re.sub(r"\W+", "_", what) + ".json")
            argv = [binary] + extra + ["-j", out]
            subprocess.run(argv, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=60)
            shown = "produced by " + " ".join(extra + ["-j"])
            if os.path.exists(out):
                try:
                    records.append((what, shown,
                                    json.load(open(out, encoding="utf-8"))))
                except ValueError as e:
                    missing.append(f"{shown}: not valid JSON ({e})")
            else:
                missing.append(f"{shown}: wrote no record")

    return records, missing

def version(binary):
    """The banner, verbatim, INCLUDING the build's short SHA.

    It used to be written as `-g<commit>)`, a literal placeholder, and the
    reasoning was sound as far as it went: committing this file changes HEAD, so
    a file containing HEAD's SHA is stale the instant it lands. Same fixpoint as
    every other generated artifact here.

    But the conclusion was wrong, and Platterpus was right to flag it (round 12
    lap 2 §E3): a generated contract with an unfilled placeholder cannot be
    checked against a binary at all. Their proposed one-line fix -- just fill it
    in -- recreates the fixpoint. The actual fix is the one gen-golden-reference.py
    has used all along: WRITE the real value and NORMALISE IT IN --check. The
    reference's banner carries `platterpus-fork-gdef36a6` and its --check ignores
    that field, so the artifact names its build and the gate still passes.

    So this file now says which build produced it, and that build is always the
    commit BEFORE the one containing this file -- "generated by X, committed at
    Y", the same labelling every other artifact here uses.

    The SHA is the weaker of the two provenance handles and is not the one to
    check against. A build tag names a COMMIT, not what was built -- round 6 cost
    both projects two golden references to that. The source anchor below it is
    content-derived, survives committing this file, and is what a consumer should
    recompute.
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

    return raw


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
    w("That is the build that GENERATED this file, which is always the commit")
    w("*before* the one containing it -- a generated artifact cannot carry the hash")
    w("of a commit that adds it. `--check` normalises this field for exactly that")
    w("reason; everything else in the file is compared byte for byte. **It is the")
    w("weaker provenance handle**: a build tag names a commit, not what was built.")
    w("The source anchor below is content-derived, survives committing this file,")
    w("and is the one to recompute.")
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
    w("- **`Elapsed:` and `Extraction speed:` - what the interval covers.** Both")
    w("  are fork-only lines, so there is no upstream documentation to fall back")
    w("  on, and the interval is not derivable from the number. Read from the")
    w("  source rather than described: the clock starts at `cyanrip_main.c`'s")
    w("  `track_start_time`, **before** the `repeat_ripping:` label, and is read")
    w("  at the `end:` label. Therefore it **includes** the paranoia seek and any")
    w("  drive spin-up it triggers, the read, the filter graph, and sending PCM to")
    w("  the encoders including the flush signal; it **includes every `-Z` pass**,")
    w("  not only the final one; it **excludes** `cyanrip_finalize_encoding()`,")
    w("  which joins and muxes after the clock is read; and it **excludes any")
    w("  AccurateRip network request** - the only AccurateRip call inside the")
    w("  bracket is `crip_find_ar()`, a lookup in an already-populated table.")
    w("  `Extraction speed:` is the track's audio duration divided by that same")
    w("  `Elapsed:`, so it is **not** a drive-speed multiple and is not directly")
    w("  comparable to EAC's row of the same name, which brackets a different")
    w("  interval. Asked by Platterpus in round 8; the four sub-questions they")
    w("  posed are each answered above.")
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
            for i, (part, _whole) in enumerate(parts):
                w(f"| {i} | `{part}` |")
            w("")
            # DERIVED, not asserted. See snprintf_parts' docstring for the
            # sentence this replaced and what it got wrong.
            whole = [p for p, is_whole in parts if is_whole]
            appended = [p for p, is_whole in parts if not is_whole]
            if not appended:
                w("**These segments ALTERNATE - exactly one is emitted.** Every")
                w("write above targets the whole buffer (`snprintf(buf, ...)`),")
                w("which writes from the start and NUL-terminates, so each")
                w("replaces the last rather than extending it. **Match them as")
                w("alternatives, never as a concatenation.**")
            elif not whole:
                w(f"**These {len(appended)} segments are written at an offset**")
                w("(`snprintf(buf + n, ...)`), so they extend the buffer rather")
                w("than replacing it, and more than one can appear in a single")
                w("line.")
            else:
                repl = [str(i) for i, (_p, is_whole) in enumerate(parts)
                        if is_whole]
                ext = [str(i) for i, (_p, is_whole) in enumerate(parts)
                       if not is_whole]
                w(f"**Mixed: segment(s) {', '.join(repl)} replace the buffer, "
                  f"{', '.join(ext)} extend it.**")
                w("A whole-buffer `snprintf(buf, ...)` writes from the start, so")
                w("it resets the line; a `snprintf(buf + n, ...)` appends to")
                w("whatever is already there. So a rendered line is one of the")
                w("replacing segments followed by zero or more of the extending")
                w("ones, in source order.")
                w("")
                w("**Which of them actually appear needs a run to settle** - that")
                w("is control flow, and this generator reports the writes it can")
                w("see rather than guessing at the branches around them. In")
                w("particular it does NOT claim any segment is unconditional.")
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
    w("**Derived, including the table.** Until round 12 the rows here were literal")
    w("strings in the generator -- one of them read *\"1, Every failure, without")
    w("exception\"* -- while the line beneath them counted the tree and found")
    w("something else. A hand-written claim inside a generated document is the exact")
    w("defect this file exists to prevent, and it shipped a contract saying the")
    w("opposite of the binary's `--verify-log` codes. Platterpus found it.")
    w("")
    resolved, unresolved, chain = exit_surface()
    enums = enum_values()
    w("| Code | Return/exit sites | Meaning, where the source states one |")
    w("|---|---|---|")
    for code in sorted(resolved):
        named = []
        for ev in resolved[code]:
            for m in re.finditer(r"`([A-Z][A-Z0-9_]*)`", ev):
                if m.group(1) in enums and enums[m.group(1)][1]:
                    named.append(f"`{m.group(1)}` -- {enums[m.group(1)][1]}")
        meaning = "; ".join(dict.fromkeys(named)) or "*(the source annotates none)*"
        w(f"| `{code}` | {len(resolved[code])} | {meaning} |")
    w("")
    w(f"**Values resolved: "
      f"{', '.join('`'+str(c)+'`' for c in sorted(resolved))}.** "
      f"Exit paths that could not be resolved: "
      + (f"**{len(unresolved)}** -- "
         + "; ".join(f"`{w_}` (`{e}`)" for w_, e in unresolved)
         if unresolved else "**none**.") )
    w("")
    w("Followed from the entry point, one hop at a time, so the scope is checkable")
    w("rather than asserted: " + " -> ".join("`" + c + "`" for c in chain) + ".")
    w("Comments and string literals are blanked before scanning, because this file's")
    w("own comments discuss returns and exits and the first version of this")
    w("derivation reported three of them as real paths.")
    w("")
    w("**`1` is the generic failure and carries no class.** For everything except")
    w("`--verify-log`, classification must come from the text, which is why P5")
    w("exists. `--verify-log` is the one surface that discriminates, and its five")
    w("values are wire format: the enum's ORDER is an implementation detail, the")
    w("numbers are not, and they are mapped explicitly for that reason.")
    w("")
    w("No non-zero exit is silent: argument parse failures print before returning,")
    w("and every other `return 1` reachable from the entry point is preceded by a")
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
    w("| stock, genopt onward (`958e1ad`, 0.9.4-rc1) | exit 0 | **exit 1** | exit 0 |")
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
    w("**The middle row names a COMMIT, not a branch, and that is a repair.** It")
    w("used to read `master` = `958e1ad`, which was an equality rather than an")
    w("identification -- true on 2026-08-04 and false the moment our mirror of")
    w("upstream moved on. Found by asking what would break if `master` were")
    w("synced: nothing else does, and this row already had. A measurement is")
    w("about the build it ran on, and a branch tip is not a build.")
    w("")
    w("The `version_matrix` scenario checks its claim against whatever `master`")
    w("points at **now**, not against `958e1ad`, so it stays meaningful across a")
    w("sync and will fail if upstream ever restores `-V`.")
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
    w("## P8 - The `-j` diagnostics record")
    w("")
    w("**DERIVED, from two sources that must agree.** The key names come from")
    w("`diagnostics.c`'s emitter, where they are spelled into the format")
    w("strings; the types and nullability come from real records. Neither half")
    w("is sufficient alone, and the failure mode each one covers is the other's")
    w("blind spot: a record-only derivation lists whatever the samples happened")
    w("to exercise and calls it a schema, and a source-only derivation cannot")
    w("say which fields are ever null. Anything the two disagree about is")
    w("reported below rather than reconciled.")
    w("")
    w("Platterpus asked for this in round 12 §F1 and carried it into round 13.")
    w("")

    schema, schema_at = diag_schema_literal()
    records, missing = diag_records(binary)
    source_keys = diag_source_keys()

    w("### P8a - The schema string, and what a consumer should do with it")
    w("")
    if schema:
        w(f"This build emits `\"schema\": \"{schema}\"` (`{schema_at}`).")
    else:
        w("**The schema literal could not be found in `diagnostics.c`.** Treat")
        w("every claim in this section as unverified until that is fixed.")
    w("")
    w("The number after the slash is not a version to compare, it is an")
    w("identity to recognise. A field ADDED to this record is harmless to a")
    w("reader that ignores unknown keys, and every change so far has been an")
    w("addition -- so a consumer that rejects an unrecognised schema string")
    w("rejects records it could have read. Gate on the prefix, and widen the")
    w("accepted set rather than pinning one value.")
    w("")

    w("### P8b - Every field")
    w("")
    if missing:
        w("**Records this section could not read, reported rather than dropped:**")
        w("")
        for m in missing:
            w(f"- `{m}`")
        w("")
        w("Every column below is narrower than it should be by whatever those")
        w("would have contributed.")
        w("")
    w(f"Derived from {len(records)} records, named rather than globbed so that")
    w("a shape which stops being covered is a visible act:")
    w("")
    for what, where, _ in records:
        shown = where if where.startswith("produced by") else f"`{where}`"
        w(f"- **{what}** -- {shown}")
    w("")

    acc = {}
    per_record = []
    for what, _where, rec in records:
        one = {}
        diag_walk(rec, "", one)
        per_record.append((what, set(one)))
        for k, (types, nullable) in one.items():
            t, n = acc.setdefault(k, (set(), False))
            t |= types
            acc[k] = (t, n or nullable)

    w("`null` in the table means **observed null in at least one record**, which")
    w("is a stronger claim than \"the type allows it\" and a weaker one than")
    w("\"it is the only way it can be null\". A field marked `--` was never")
    w("observed null by any record here; that is not a guarantee it cannot be.")
    w("")
    w("| field | type | observed null | in every record |")
    w("|---|---|---|---|")
    for key in sorted(acc):
        types, nullable = acc[key]
        everywhere = all(key in ks for _w, ks in per_record)
        if types:
            tdesc = "/".join(sorted(types))
        elif nullable:
            # Never observed carrying a value. NOT the same as "container",
            # which is what this said first and which would have described
            # read_stalls.longest_lsn -- a plain integer -- as a nested object.
            tdesc = "*(null in every record here)*"
        else:
            tdesc = "*(container)*"
        w(f"| `{key}` | {tdesc} | {'**yes**' if nullable else '--'} | "
          f"{'yes' if everywhere else '**no**'} |")
    w("")

    # Source-vs-record reconciliation. Reported, never silently merged.
    src_names = {k for k, _ln in source_keys}
    rec_leaves = {k.split(".")[-1].replace("[]", "") for k in acc}
    only_src = sorted(src_names - rec_leaves)
    only_rec = sorted(rec_leaves - src_names)
    if only_src or only_rec:
        w("**Where the two derivations disagree.** Reported rather than")
        w("reconciled: a difference here is either a field no record reaches or")
        w("a field this generator cannot read out of the source, and those need")
        w("different fixes.")
        w("")
        if only_src:
            w("Emitted by `diagnostics.c` and absent from every record read here"
              " -- so reachable only under conditions none of them met:")
            w("")
            for k in only_src:
                lines = sorted(ln for name, ln in source_keys if name == k)
                w(f"- `{k}` (`diagnostics.c:{lines[0]}`)")
            w("")
        if only_rec:
            w("Present in a record and not found in the source scan -- this")
            w("generator's key extraction is incomplete for these:")
            w("")
            for k in only_rec:
                w(f"- `{k}`")
            w("")
    else:
        w("The two derivations agree: every key in the source scan appears in a")
        w("record, and every key in a record appears in the source scan.")
        w("")

    w("### P8c - Two absences that are deliberate")
    w("")
    w("Both would be easy to add and both would be wrong, so they are stated")
    w("here rather than left to look like oversights.")
    w("")
    w("- **No severity on any message.** `cyanrip_log()` carries none, so")
    w("  attaching one here would be this program guessing at its own output.")
    w("  The record says so in its own `messages_note` field rather than only")
    w("  in this document.")
    w("- **No `success` flag.** A record is written for runs that produce no")
    w("  logfile at all, which is the reason `-j` exists; a boolean verdict")
    w("  would be cyanrip making a judgement, and judgements are the")
    w("  consumer's. `exit_code`, `ripping_errors`, `interrupted` and the")
    w("  per-track `audio_ripped` are the measurements a verdict would be")
    w("  built from, and they are all present.")
    w("")
    w("`exit_code` is **tri-state and `null` is not `0`.** A record written from")
    w("`atexit` before the exit status is known reports `null`, and a consumer")
    w("that coerces that to zero reports a crashed run as a clean one.")
    w("")

    w("On **this fork** the genopt message is routed through `cyanrip_log()`, so")
    w("it reaches stdout, the logfile if one is open, and the `-j` record. That")
    w("is a fork property; stock does neither.")
    w("")
    w("## P7 - Filename sanitisation (`-T`)")
    w("")
    w("**DERIVED.** From `src/naming.c`'s substitution table and the branch that")
    w("writes each glyph, `src/cyanrip_main.c`'s option handling, and")
    w("`src/os_compat.h`'s per-OS availability macros. Nothing here is")
    w("transcribed; a hand-copied second copy of the table inside a generated")
    w("document is the failure this generator exists to prevent.")
    w("")
    w("**Why it is here.** Platterpus asked for it in round 13 (`[ASK A]`,")
    w("BLOCKING). P1 documented the flag and its four spellings and documented")
    w("**none of their substitutions**, so the path a rip lands on -- a value")
    w("that crosses the seam -- was described by neither contract. The concrete")
    w("cost was a completed 14-track rip silently overwritten by a 2-track one,")
    w("because a downstream guard predicted the directory name from a two-entry")
    w("copy of this table and probed a directory that did not exist.")
    w("")
    w("This section is not advice about which mode to use. It is what the")
    w("program does.")
    w("")

    rows, row_unresolved = sanitize_table()
    modes, default_const, default_line, mode_unresolved = sanitize_modes()
    overrides, defaults, unread = sanitize_availability()
    callsites = sanitize_callsites()

    w("### P7a - The default, and the four spellings")
    w("")
    if default_const:
        dname = next((s for s, c, _o, _g in modes if c == default_const), None)
        w(f"**The default is `{dname or default_const}`.** "
          f"`cyanrip_main.c:{default_line}` assigns `{default_const}`, and it")
        w("is the only assignment to `settings.sanitize_method` that is not")
        w("guarded by a `-T` value -- which is how this generator identifies it,")
        w("and why a second unguarded one would be reported here as ambiguous")
        w("rather than resolved to the first.")
    else:
        w("**The default could not be resolved from the source.** Treat every")
        w("mode below as possible until this is fixed.")
    w("")
    w("| `-T` value | enum constant | glyph field | limited to characters unavailable on the build's OS |")
    w("|---|---|---|---|")
    for spelling, const, is_os, field in modes:
        dflt = " *(default)*" if const == default_const else ""
        w(f"| `{spelling}`{dflt} | `{const}` | `{field or '**unresolved**'}` | "
          f"{'**yes**' if is_os else 'no' } |")
    w("")
    w("`-T` takes a value; there is no bare form. An unrecognised value is")
    w("refused before any disc is touched -- P5 carries the string and the")
    w("`return 1` that follows it.")
    w("")

    w("### P7b - The substitution table")
    w("")
    w("`crip_char_replacement[]`, in source order. The order matters for one")
    w("thing only, and P7d is about that thing.")
    w("")
    w("| # | character | codepoint | `simple` writes | `unicode` writes | codepoint | availability macro |")
    w("|---|---|---|---|---|---|---|")
    for idx, frm, to, to_u, macro in rows:
        f_ch, t_ch = c_char(frm), c_char(to)
        w(f"| {idx} | `{md_cell(f_ch)}` | `U+{ord(f_ch):04X}` | "
          f"`{md_cell(t_ch)}` | `{md_cell(to_u)}` | "
          f"`{' '.join('U+%04X' % ord(ch) for ch in to_u)}` | `{macro}` |")
    w("")
    if row_unresolved:
        w("**Rows this generator could not parse, reported rather than dropped:**")
        w("")
        for u in row_unresolved:
            w(f"- `{u}`")
        w("")
    w("**Anything not in the `character` column is passed through unchanged**")
    w("-- no length limit, no case folding, no whitespace collapsing, no")
    w("trailing-dot handling. That is an absence, so here is what it rests on")
    w("rather than an assurance: these are every call in")
    w("`crip_bprint_sanitize()` that writes to the output buffer, enumerated")
    w("from the function body. A transformation this table does not describe")
    w("would have to appear as a call here.")
    w("")
    w("| line | call | writes |")
    w("|---|---|---|")
    for line, call, arg in sanitize_writes():
        if "pos" in arg:
            what = "the input, verbatim"
        elif "to_u" in arg:
            what = "the `unicode` glyph, from the table"
        elif "rep->to" in arg:
            what = "the `simple` glyph, from the table"
        else:
            what = f"**unclassified** -- `{md_cell(arg)}`"
        w(f"| `naming.c:{line}` | `{call}` | {what} |")
    w("")

    w("### P7c - What each mode does to each character")
    w("")
    w("The two `os_` modes substitute a character **only when it is unavailable")
    w("on the build's OS**. Note which way that runs: a character being *legal*")
    w("on the target filesystem is why an `os_` mode leaves it **alone**. On any")
    w("given build an `os_` mode is therefore the **least** substituting of the")
    w("four, never the most, and `-T os_unicode` is not a way to ask for the")
    w("unicode glyphs -- it is a way to ask for fewer of them.")
    w("")
    w("Availability is a **compile-time** property (P7e). Two columns cover it,")
    w("because `os_compat.h` has exactly two states for these macros: the")
    w("`HAVE_WMAIN` build and everything else. `HAVE_WMAIN` is set by")
    w("`src/meson.build:150` when the compiler links `wmain` with `-municode`,")
    w("so in practice it means a Windows/MinGW build. The build that generated")
    w("this document is named in the banner at the top; which branch **your**")
    w("build took is a property of your build, not of this file.")
    w("")

    def avail(macro, win):
        if win and macro in overrides.get("HAVE_WMAIN", {}):
            return overrides["HAVE_WMAIN"][macro][0]
        if macro in defaults:
            return defaults[macro][0]
        return None

    def cell(macro, glyph, win):
        a = avail(macro, win)
        if a is None:
            return "**unresolved**"
        return "unchanged" if a else f"`{md_cell(glyph)}`"

    w("| character | `simple` | `unicode` | `os_simple` non-`HAVE_WMAIN` | `os_unicode` non-`HAVE_WMAIN` | `os_simple` `HAVE_WMAIN` | `os_unicode` `HAVE_WMAIN` |")
    w("|---|---|---|---|---|---|---|")
    for idx, frm, to, to_u, macro in rows:
        f_ch, t_ch = c_char(frm), c_char(to)
        note = " †" if f_ch == "/" else ""
        w(f"| `{md_cell(f_ch)}`{note} | `{md_cell(t_ch)}` | `{md_cell(to_u)}` | "
          f"{cell(macro, t_ch, False)} | {cell(macro, to_u, False)} | "
          f"{cell(macro, t_ch, True)} | {cell(macro, to_u, True)} |")
    w("")
    same = list(dict.fromkeys(c_char(f) for _i, f, _t, _u, m in rows
                              if avail(m, False)))
    diff = list(dict.fromkeys(c_char(f) for _i, f, _t, _u, m in rows
                              if not avail(m, False)))
    if same:
        w("Read the two `non-HAVE_WMAIN` columns before treating an `os_` mode as")
        w("a safe substitute for a plain one. On such a build "
          f"**{len(same)} of the {len(set(c_char(r[1]) for r in rows))} distinct")
        w("characters** are left unchanged by both `os_` modes: "
          + ", ".join(f"`{md_cell(c)}`" for c in same) + ".")
        w("")
        if diff:
            w("Which leaves `os_simple` and `os_unicode` differing, on such a")
            w("build, on " + ", ".join(f"`{md_cell(c)}`" for c in diff) +
              " and nothing else.")
            w("")
    w("**† `/` is the exception, and it is not a property of the mode.** See")
    w("P7d.")
    w("")

    w("### P7d - Two behaviours the table cannot express")
    w("")
    w("Both are read from the control flow of `crip_bprint_sanitize()`, not from")
    w("the table, and both change the resulting filename. A consumer predicting")
    w("a path from metadata gets the wrong answer without them.")
    w("")
    w("**1. `/` depends on where the text came from, not on the mode.**")
    w("`crip_bprint_sanitize()` takes a `sanitize_fwdslash` argument; when it is")
    w("0, a `/` is emitted verbatim -- which is how a naming scheme spells a")
    w("subdirectory. Every call site, and what each one passes:")
    w("")
    w("| call site | `sanitize_fwdslash` | meaning |")
    w("|---|---|---|")
    for line, arg in callsites:
        if arg == "0":
            meaning = ("literal text, never a tag value -- `/` is a directory "
                       "separator here")
        else:
            meaning = (f"`{arg}`: 1 when the token resolved to a metadata tag, "
                       f"0 when it fell back to literal scheme text")
        w(f"| `naming.c:{line}` | `{arg}` | {meaning} |")
    w("")
    w("So a `/` **inside a metadata value** is substituted, and a `/` **in the")
    w("scheme itself** creates a directory. The pass-through is checked after")
    w("the OS-availability test, so it applies in all four modes.")
    w("")
    w("**2. The two quote glyphs alternate on a counter that every substituted")
    w("character advances -- not only quotes.** The table holds two rows for")
    w("`\"`; which one is used is chosen by a parity flag, and that flag is")
    w("toggled by **every** character the table matches, including characters")
    w("that are then left unchanged by an `os_` mode or by the `/` pass-through.")
    w("The flag is a local, so it resets at every call -- and `process_cond()`")
    w("calls once per literal run and once per `{tag}`, which means a `{tag}`")
    w("boundary between two quotes resets the parity.")
    w("")
    w("Two consequences, both observable in a filename:")
    w("")
    w("- an odd number of other substitutable characters between two quotes")
    w("  flips which glyph the closing quote gets;")
    w("- the same rendered text produces different filenames depending on where")
    w("  the scheme's `{}` boundaries fall.")
    w("")
    w("The `sanitize_quotes` scenario in `tests/rip_images.py` rips with each")
    w("mode and asserts the resulting names, so this section fails when the")
    w("behaviour moves.")
    w("")

    w("### P7e - Availability macros, and where they come from")
    w("")
    w("| macro | default | set under | value there |")
    w("|---|---|---|---|")
    for macro in dict.fromkeys(r[4] for r in rows):
        d = defaults.get(macro)
        dtxt = (f"`{d[0]}` (`os_compat.h:{d[2]}`"
                + (f", *{d[1]}*" if d[1] else "") + ")") if d else "**none**"
        ovs = [f"`{cond}` -> `{v[0]}` (`os_compat.h:{v[1]}`)"
               for cond, m in sorted(overrides.items()) if macro in m
               for v in [m[macro]]]
        w(f"| `{macro}` | {dtxt} | "
          f"{'; '.join(c.split(' -> ')[0] for c in ovs) if ovs else '--'} | "
          f"{'; '.join(c.split(' -> ')[1] for c in ovs) if ovs else '--'} |")
    w("")
    w("A macro appears once per row of P7b, so `HAS_CH_QUOTES` governs both")
    w("quote rows together.")
    w("")
    if unread:
        w("**Defined here and read by nothing.** Derived, not noted: this")
        w("paragraph disappears by itself when the macro is wired up, which a")
        w("prose remark could not do.")
        w("")
        for macro, where in unread:
            if where and len(where) == 3 and isinstance(where[1], str) and where[1]:
                w(f"- **`{macro}`** -- `os_compat.h:{where[2]}` defines it as")
                w(f"  `{where[0]}` under `{where[1]}`. No file in `src/` reads")
                w(f"  that name.")
            else:
                w(f"- **`{macro}`** -- defined in `os_compat.h`, read nowhere.")
        w("")
        w("Stated as an observation and not as an intent: this generator can see")
        w("that the name is never read, and cannot see what was meant. The")
        w("consequence a consumer can act on is in the table above -- the macro")
        w("the substitution table actually reads has no override under that")
        w("condition, so those builds follow the default column.")
        w("")
    if mode_unresolved:
        w("**Unresolved while deriving this section:**")
        w("")
        for u in mode_unresolved:
            w(f"- `{u}`")
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
        # The build tag is normalised on BOTH sides and nothing else is. Written
        # verbatim so the artifact names its build (E3); ignored here so
        # committing the file does not make it stale. Same split, and for the
        # same reason, as gen-golden-reference.py's VOLATILE table.
        if BUILD_TAG.sub("-g<tag>)", have) != BUILD_TAG.sub("-g<tag>)", text):
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
