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

"""Black-box conformance sweep: hostile INPUTS, not hostile flags.

WHAT IS ALREADY COVERED, so this does not repeat it. `probe-argv-surface.py`
establishes each argument's accepted range, its boundaries and whether a bad
value is refused or silently ignored -- the S-9 obligation, and it is already a
gate. `sanitize-run.py` rips every fixture under ASan/UBSan. Between them the
FLAG surface and the HAPPY PATH are probed.

WHAT WAS NOT, AND WHY IT MATTERS MORE. cyanrip's inputs are not just its flags.
They are a disc image, a naming scheme, and -- the part that decides this
tool's shape -- METADATA THAT THE OPERATOR DID NOT WRITE. Platterpus looks a
disc up in MusicBrainz and feeds what comes back into `-a`/`-t`, and
MusicBrainz is a wiki: any human on the internet can edit a release title.
Those strings are then expanded into DIRECTORY AND FILE NAMES on the operator's
machine.

So the interesting question is not "does -s reject 'abc'". It is: given a
string an untrusted third party chose, can this program be made to crash, to
hang, to die without saying why, or to write outside the directory it was told
to write in. This sweep asks that.

THE INVARIANTS, CHECKED ON EVERY SINGLE INVOCATION -- not per probe family.
Each is a property this repository already commits to in prose; a sweep is
worth building only because prose does not execute.

    I1  never killed by a signal. A crash is not a refusal, however much the
        shell's exit code resembles one. probe-argv-surface graded four
        segfaults as clean refusals in round 7 and printed "0 silently ignored"
        in the same run.
    I2  always terminates. A hang is the failure a timeout hides: the run is
        recorded as slow rather than as wrong.
    I3  a non-zero exit ALWAYS prints at least one non-empty line. CLAUDE.md:
        "a non-zero exit with no output is the one failure they cannot explain
        to a user."
    I4  no sanitizer diagnostic. Only meaningful against an instrumented
        binary, so this states UNPROBED when the binary carries no sanitizer
        symbols rather than passing quietly -- the exact defect that left three
        `if "runtime error" in out` checks unable to fire for months.
    I5  stdin is never read. Every run gets a CLOSED stdin; a program that
        blocks on it violates I2 and is reported there. "Never prompt or block
        on stdin. There is no controlling terminal."
    I6  CONTAINMENT: no file is created outside the directory the run was told
        to write in. This is the one that is about the threat model above
        rather than about tidiness.
    I7  any logfile written begins with this fork's banner.

WHAT A FINDING IS, AND WHAT IT IS NOT. This tool reports what the binary did.
It does not decide whether a refusal is correct, whether a message is well
worded, or whether a value should have been accepted -- those are judgements,
and judgements are the consumer's. A probe that violates no invariant is
reported as OBSERVED with its exit code, never as "passed", because "passed"
would be a claim about intent that running a binary cannot support.

Usage:
    tools/blackbox.py                          # against build/src/cyanrip
    tools/blackbox.py --binary build-asan/src/cyanrip
    tools/blackbox.py --gate                   # non-zero if any invariant broke
    tools/blackbox.py --family metadata        # one family
    tools/blackbox.py --list                   # what would run
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "tests" / "fixtures"

# Long enough that a genuine hang is unambiguous, short enough that a sweep of
# a few hundred runs finishes. A run that needs longer than this is itself the
# finding.
TIMEOUT = 45

# A known defect is still a finding; it is just one that already has a home.
# Naming it here keeps the report honest in both directions -- it is not
# silently dropped, and it does not read as new.
# Reasons a probe declined to run, stated out loud. A blank reads as "tested
# and fine", so there are none.
UNPROBED_STATIC = set()

KNOWN = {
    "apostrophe-swallows-later-fields":
        "docs/SETTLED.md, and pinned by tests/rip_images.py sc_consumer_argv",
}


class Run:
    """One invocation and everything observable about it."""

    def __init__(self, label, argv, exit_code, signal, out, timed_out,
                 escaped, logs):
        self.label = label
        self.argv = argv
        self.exit_code = exit_code
        self.signal = signal
        self.out = out
        self.timed_out = timed_out
        self.escaped = escaped        # files created outside the output root
        self.logs = logs              # (path, first_line) for each *.log written


def instrumented(binary):
    """Ask the BINARY whether it carries sanitizer symbols, not the environment.

    Meson exports ASAN_OPTIONS and UBSAN_OPTIONS for every test whatever the
    build options are, so the environment looks instrumented while the binary
    is not. `nm` is the artifact.
    """
    try:
        nm = subprocess.run(["nm", str(binary)], stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    text = nm.stdout.decode("utf-8", "replace").lower()
    return ("asan" in text) or ("ubsan" in text)


def snapshot(root):
    return {p for p in root.rglob("*") if p.is_file()}


# THE SANDBOX IS NOT THE WORLD, and assuming it was is why this tool missed the
# finding it exists to find. snapshot() walks `work`, so a write ABOVE `work`
# is not "escaped" -- it is INVISIBLE. On 2026-09-05 cyanrip wrote a whole rip
# to `/Some Album` and a 758-probe sweep reported nothing, because nothing it
# looked at had changed. The escape was found by hand, by listing `/`.
#
# One listdir per root per run is cheap and catches exactly that class.
OUTSIDE_ROOTS = [Path("/"), Path("/tmp"), Path.home()]


def outside_snapshot():
    seen = {}
    for r in OUTSIDE_ROOTS:
        try:
            seen[r] = set(os.listdir(r))
        except OSError:
            seen[r] = set()
    return seen


def invoke(binary, label, argv, work, out_root, env_overlay=None):
    """Run once, with stdin CLOSED, and record everything observable.

    `env_overlay` maps a variable to a value, or to None to UNSET it -- unset
    and empty are different inputs and a probe that cannot express the
    difference cannot test it, the same distinction this project draws between
    `none` and `unknown (reason)`.
    """
    before = snapshot(work)
    outside_before = outside_snapshot()
    timed_out = False
    env = dict(os.environ)
    for k, v in (env_overlay or {}).items():
        if v is None:
            env.pop(k, None)
        else:
            env[k] = v
    try:
        r = subprocess.run([str(binary)] + [str(a) for a in argv],
                           stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           cwd=str(work), timeout=TIMEOUT, env=env)
        code, out = r.returncode, r.stdout
    except subprocess.TimeoutExpired as e:
        timed_out = True
        code, out = None, (e.output or b"")

    text = out.decode("utf-8", "replace")
    sig = -code if (code is not None and code < 0) else None

    after = snapshot(work)
    new = after - before

    # WHERE WAS THIS RUN TOLD TO WRITE? Derive it from the argv rather than
    # assuming `out/`: several probes deliberately pass a different -D, and a
    # hardcoded root reported four correct writes as containment breaches on
    # the sweep's first run. The invariant is "outside what it was TOLD", and
    # a check whose expectation is a constant is not testing that.
    allowed = set()
    for flag in ("-D", "-j"):
        if flag in argv:
            v = str(argv[argv.index(flag) + 1])
            try:
                allowed.add((work / v).resolve())
            except (OSError, RuntimeError):   # RuntimeError: symlink loop
                pass
    allowed.add(out_root.resolve())

    def contained(f):
        try:
            r = f.resolve()
        except (OSError, RuntimeError):
            return False
        return any(a == r or a in r.parents for a in allowed)

    escaped = sorted(str(p.relative_to(work)) for p in new
                     if not contained(p) and p.parent != work)

    # Anything that appeared in a root this run had no business touching.
    outside_after = outside_snapshot()
    for r, names in outside_after.items():
        for n in sorted(names - outside_before.get(r, set())):
            escaped.append(f"{r / n}   (OUTSIDE the sandbox entirely)")
    logs = []
    for p in sorted(new):
        if p.suffix == ".log":
            try:
                first = p.read_text(encoding="utf-8",
                                    errors="replace").splitlines()
            except OSError:
                first = []
            logs.append((str(p.relative_to(work)), first[0] if first else ""))
    return Run(label, argv, code, sig, text, timed_out, escaped, logs)


def check(run, banner_re, can_sanitize, findings, unprobed):
    """Apply every invariant to one run. One run may break several."""
    def note(inv, what):
        findings.append((inv, run.label, what, run.argv))

    if run.timed_out:
        note("I2", f"did not terminate within {TIMEOUT}s")
        return                       # nothing else is meaningful about a hang

    if run.signal is not None:
        note("I1", f"killed by signal {run.signal}")

    if run.exit_code not in (0, None) and not run.out.strip():
        note("I3", f"exit {run.exit_code} with no output at all")

    if can_sanitize:
        for pat in ("runtime error", "AddressSanitizer", "LeakSanitizer",
                    "UndefinedBehaviorSanitizer"):
            if pat in run.out:
                line = next((l for l in run.out.splitlines() if pat in l), pat)
                note("I4", f"sanitizer: {line.strip()[:160]}")
                break
    elif can_sanitize is None:
        unprobed.add("I4: could not run nm on the binary")
    else:
        unprobed.add("I4: binary carries no sanitizer symbols -- "
                     "re-run against build-asan/src/cyanrip")

    for p in run.escaped:
        note("I6", f"wrote outside the output directory: {p}")

    for path, first in run.logs:
        if not banner_re.search(first):
            note("I7", f"{path} first line is not this fork's banner: "
                       f"{first[:100]!r}")


# ---------------------------------------------------------------- probes ----
#
# Each family returns a list of (label, argv). They are DATA, so `--list` can
# print exactly what will run without running it.

# Every probe rips or inspects this, because it is the smallest fixture and the
# subject under test is the STRING, not the disc.
def base(work, extra):
    return ["-d", "basic.cue", "-N", "-A", "-U", "-s", "0", "-P", "0",
            "-o", "flac", "-D", "out", "-L", "log", "-M", "sheet"] + extra


# Strings an untrusted third party could put in a MusicBrainz release title.
# Each is a value, not a whole argument, so the probe can place it in either
# the metadata or the naming scheme and compare.
HOSTILE = [
    ("apostrophe",        "Don't Stop"),
    ("double-quote",      'She said "no"'),
    ("backslash",         "AC\\DC"),
    ("backslash-quote",   "AC\\'DC"),
    ("colon",             "Album: The Sequel"),
    ("equals",            "E=mc2"),
    ("percent-s",         "%s%s%s"),
    ("percent-n",         "%n"),
    ("brace-token",       "{album}"),
    ("brace-unbalanced",  "{album"),
    ("brace-if",          "{if #a# > #b#|x|}"),
    ("dotdot",            "../escaped"),
    ("dotdot-deep",       "../../../escaped"),
    ("absolute",          "/tmp/escaped"),
    ("slash",             "a/b/c"),
    ("newline",           "line1\nline2"),
    ("tab",               "a\tb"),
    ("cr",                "a\rb"),
    ("nul-ish",           "a\\0b"),
    ("ansi-escape",       "\x1b[31mRED\x1b[0m"),
    ("bell",              "ding\x07"),
    ("utf8-invalid",      "caf\udcff"),
    ("utf8-combining",    "é" * 40),
    ("rtl-override",      "abc‮def"),
    ("zero-width",        "a​b"),
    ("emoji",             "\U0001f4bf\U0001f4c0"),
    ("empty",             ""),
    ("space-only",        "   "),
    ("dot",               "."),
    ("dotdot-bare",       ".."),
    ("long-255",          "L" * 255),
    ("long-4096",         "L" * 4096),
    ("long-65535",        "L" * 65535),
    ("leading-dash",      "-oops"),
    ("tilde",             "~/escaped"),
    ("dollar",            "$HOME"),
    ("backtick",          "`id`"),
    ("semicolon",         "a; id"),
    ("pipe",              "a | id"),
    ("glob",              "a*b?c[d]"),
]


def fam_metadata(work):
    """A hostile string as a metadata VALUE -- the MusicBrainz threat model."""
    out = []
    for name, value in HOSTILE:
        out.append((f"meta/album/{name}",
                    base(work, ["-a", f"album={value}"])))
        out.append((f"meta/title/{name}",
                    base(work, ["-t", f"1=title={value}"])))
    return out


def fam_containment(work):
    """THE THREAT MODEL, ASKED DIRECTLY: can untrusted metadata escape -D?

    Platterpus looks a disc up in MusicBrainz and feeds what comes back into
    `-a`/`-t`. MusicBrainz is a wiki. Those strings are expanded into directory
    and file names by the default schemes, so a release title is untrusted
    input that decides a path on the operator's machine.

    `fam_metadata` CANNOT ask this and it took a run to notice: its base() pins
    `-D out`, a literal, so `{album}` never reaches a path at all. A probe
    family whose fixture defeats the property it was written for is the
    "fixture whose numbers agree by construction" defect one level up.

    Here the scheme is `{album}` / `{title}`, so the hostile string IS the
    path, and I6 does the judging.
    """
    out = []

    # MULTI-COMPONENT SCHEMES FIRST, because a single-component one cannot
    # reach the defect. It takes an EMPTY leading component to make the whole
    # path ABSOLUTE, and `-D out/{album}` can never produce one -- the literal
    # `out/` is always in front. The consumer passes `{album_artist}/{album}`,
    # with metadata in the FIRST position, and that is the shape that escapes.
    for sanitize in ("simple", "unicode"):
        for name, value in HOSTILE:
            out.append((f"contain/leading/{sanitize}/{name}",
                        ["-d", "basic.cue", "-N", "-A", "-U", "-s", "0",
                         "-P", "0", "-o", "flac", "-T", sanitize,
                         "-D", "{album_artist}/{album}",
                         "-a", f"album_artist={value}:album=BlackboxProbe"]))

    for sanitize in ("simple", "os_simple", "unicode", "os_unicode"):
        for name, value in HOSTILE:
            out.append((f"contain/folder/{sanitize}/{name}",
                        ["-d", "basic.cue", "-N", "-A", "-U", "-s", "0",
                         "-P", "0", "-o", "flac", "-T", sanitize,
                         "-D", "out/{album}", "-L", "log", "-M", "sheet",
                         "-a", f"album={value}"]))
            out.append((f"contain/track/{sanitize}/{name}",
                        ["-d", "basic.cue", "-N", "-A", "-U", "-s", "0",
                         "-P", "0", "-o", "flac", "-T", sanitize,
                         "-D", "out", "-F", "{title}", "-L", "log",
                         "-M", "sheet", "-t", f"1=title={value}"]))
    return out


def fam_scheme(work):
    """A hostile string as a NAMING SCHEME -- the operator's own input."""
    out = []
    for name, value in HOSTILE:
        out.append((f"scheme/track/{name}", base(work, ["-F", value])))
        out.append((f"scheme/folder/{name}",
                    ["-d", "basic.cue", "-N", "-A", "-U", "-s", "0",
                     "-P", "0", "-o", "flac", "-D", f"out/{value}",
                     "-L", "log", "-M", "sheet"]))
        out.append((f"scheme/log/{name}", base(work, ["-L", value])))
        out.append((f"scheme/cue/{name}", base(work, ["-M", value])))
    return out


def fam_image(work):
    """A malformed or hostile disc image.

    libcdio terminates the process from inside a library call -- its default
    log handler exit()s on CDIO_LOG_ERROR and abort()s on CDIO_LOG_ASSERT --
    so this family is where I1 and I3 earn their keep.
    """
    cases = {
        "empty":            b"",
        "nul":              b"\x00" * 512,
        "text":             b"this is not a cue sheet\n",
        "truncated-cue":    (FIX / "basic.cue").read_bytes()[:20],
        "cue-no-file":      b'FILE "nope.bin" BINARY\n  TRACK 01 AUDIO\n',
        "cue-bad-index":    b'FILE "basic.bin" BINARY\n  TRACK 01 AUDIO\n'
                            b'    INDEX 01 99:99:99\n',
        "cue-track-zero":   b'FILE "basic.bin" BINARY\n  TRACK 00 AUDIO\n'
                            b'    INDEX 01 00:00:00\n',
        "cue-track-huge":   b'FILE "basic.bin" BINARY\n  TRACK 99999 AUDIO\n'
                            b'    INDEX 01 00:00:00\n',
        "cue-huge-line":    b'FILE "' + b"A" * 100000 + b'" BINARY\n',
        "cue-many-tracks":  b'FILE "basic.bin" BINARY\n' + b"".join(
                                b'  TRACK %02d AUDIO\n    INDEX 01 00:00:00\n'
                                % (i % 100) for i in range(1, 500)),
        "cue-self-ref":     b'FILE "loop.cue" BINARY\n  TRACK 01 AUDIO\n'
                            b'    INDEX 01 00:00:00\n',
        "toc-truncated":    (FIX / "cdtext.toc").read_bytes()[:40],
        "toc-garbage":      b"CD_DA\nTRACK AUDIO\nFILE \x00\x01\x02\n",
        "nrg-truncated":    (FIX / "cdda.nrg").read_bytes()[:64],
        "nrg-header-only":  (FIX / "cdda.nrg").read_bytes()[-12:],
    }
    out = []
    for name, blob in cases.items():
        suffix = ".toc" if name.startswith("toc") else (
                 ".nrg" if name.startswith("nrg") else ".cue")
        p = work / f"bad_{name}{suffix}"
        p.write_bytes(blob)
        if name == "cue-self-ref":
            (work / "loop.cue").write_bytes(blob)
        out.append((f"image/{name}",
                    ["-d", p.name, "-N", "-A", "-U", "-s", "0", "-P", "0",
                     "-o", "flac", "-D", "out", "-L", "log", "-M", "sheet"]))
        out.append((f"image/{name}/info",
                    ["-d", p.name, "-N", "-A", "-U", "-I"]))
    # A path that is not a file at all.
    for name, dev in (("directory", "."), ("missing", "no_such_file"),
                      ("devnull", "/dev/null"), ("devzero", "/dev/zero"),
                      ("proc", "/proc/self/mem")):
        out.append((f"image/path/{name}",
                    ["-d", dev, "-N", "-A", "-U", "-I"]))
    return out


def fam_selection(work):
    """Track selections, disc tags, pregaps, covers -- structured arguments."""
    out = []
    for v in ("0", "-1", "99", "1-99", "1,,2", ",", "1,", "a", "1.5", "1-",
              "-1", "0-0", "2-1", "1" * 200, "", " ", "1,1,1,1"):
        out.append((f"select/tracks/{v!r}", base(work, ["-l", v])))
    for v in ("0/0", "1/0", "0/1", "-1/-1", "1/", "/1", "//", "a/b", "1/2/3",
              "999999/999999", "", "1"):
        out.append((f"select/disc/{v!r}", base(work, ["-c", v])))
    for v in ("1=drop", "1=merge", "1=track", "0=drop", "99=drop", "=drop",
              "1=", "1=bogus", "", "1=drop:2=merge", "a=drop"):
        out.append((f"select/pregap/{v!r}", base(work, ["-p", v])))
    for v in ("nope.png", "title=nope.png", "1=nope.png", "=", "1=",
              "title=/dev/null", "0=nope.png", ""):
        out.append((f"select/cover/{v!r}", base(work, ["-C", v])))
    for v in ("flac", "flac,flac", "bogus", "", ",", "flac,", ",flac",
              "FLAC", "flac,bogus", "help"):
        out.append((f"select/outputs/{v!r}",
                   ["-d", "basic.cue", "-N", "-A", "-U", "-s", "0", "-P", "0",
                    "-o", v, "-D", "out", "-L", "log", "-M", "sheet"]))
    for v in ("simple", "os_simple", "unicode", "os_unicode", "bogus", "",
              "SIMPLE"):
        out.append((f"select/sanitize/{v!r}", base(work, ["-T", v])))
    return out


def fam_verify(work):
    """-Y reads a file the operator did not write. Same threat model."""
    cases = {
        "empty": b"",
        "nul": b"\x00" * 4096,
        "text": b"not a cyanrip log\n",
        "truncated": b"cyanrip 0.9.4\nLog FUN512: ",
        "bad-checksum": b"cyanrip 0.9.4\nLog FUN512: " + b"0" * 128 + b"\n",
        "huge-line": b"Log FUN512: " + b"a" * 1000000 + b"\n",
        "many-lines": b"Log FUN512: x\n" * 100000,
        "binary": bytes(range(256)) * 64,
    }
    out = []
    for name, blob in cases.items():
        p = work / f"verify_{name}.log"
        p.write_bytes(blob)
        out.append((f"verify/{name}", ["-Y", p.name]))
    out.append(("verify/directory", ["-Y", "."]))
    out.append(("verify/missing", ["-Y", "no_such.log"]))
    out.append(("verify/devnull", ["-Y", "/dev/null"]))
    return out


def fam_combo(work):
    """Flag combinations, including ones the help text says are exclusive."""
    pairs = [
        ["-I", "-J"], ["-I", "-Y", "log"], ["-J", "-Y", "log"],
        ["-H", "-E"], ["-H", "-W"], ["-E", "-W"], ["-H", "-E", "-W"],
        ["-x", "-I"], ["-x", "-J"], ["-f", "-I"], ["-Q", "-I"],
        ["-Z", "0", "-r", "0"], ["-Z", "1", "-r", "1"],
        ["-k", "0"], ["-k", "1"], ["-O"], ["-K"], ["-G"], ["-N", "-R", "1"],
        ["-A", "-f"], ["-m", "0"], ["-m", "1"], ["-m", "-2"],
        ["-b", "0"], ["-b", "-1"], ["-b", "999999"],
        ["-P", "none"], ["-P", "max"], ["-P", "-1"], ["-P", "99999"],
        ["-j", "diag.json"], ["-j", "/dev/full"], ["-j", "."],
        ["-u", ""], ["-u", "x" * 65535], ["-u", "a\nb"],
    ]
    out = []
    for p in pairs:
        out.append((f"combo/{' '.join(p)}", base(work, p)))
    # Arguments with no fixture at all -- the table alone.
    for p in (["-h"], ["--help"], ["-v"], ["-V"], ["--version"],
              ["--bogus"], ["-Z"], ["-"], ["--"], ["-zzz"], []):
        out.append((f"combo/bare/{' '.join(p) or '<none>'}", p))
    return out


def fam_environment(work):
    """The environment is an input too, and locale decides FILENAMES.

    `-T unicode` promises a sanitation policy. Whether that policy survives
    LC_ALL=C is a question about the archival record -- a rip whose filenames
    depend on the shell that launched it is not reproducible -- and no fixture
    in the suite varies it.
    """
    out = []
    envs = {
        "LC_ALL=C":            {"LC_ALL": "C", "LANG": "C"},
        "LC_ALL=POSIX":        {"LC_ALL": "POSIX", "LANG": "POSIX"},
        "LC_ALL=C.UTF-8":      {"LC_ALL": "C.UTF-8", "LANG": "C.UTF-8"},
        "LC_ALL=invalid":      {"LC_ALL": "xx_YY.NOPE", "LANG": "xx_YY.NOPE"},
        "LANG-unset":          {"LANG": None, "LC_ALL": None},
        "HOME-unset":          {"HOME": None},
        "HOME-empty":          {"HOME": ""},
        "TMPDIR-missing":      {"TMPDIR": "/no/such/tmpdir"},
        "PATH-empty":          {"PATH": ""},
        "TERM-unset":          {"TERM": None},
        "COLUMNS-0":           {"COLUMNS": "0"},
    }
    for name, env in envs.items():
        for sanitize in ("unicode", "os_unicode", "simple"):
            out.append((f"env/{name}/-T {sanitize}",
                        base(work, ["-T", sanitize,
                                    "-a", "album=Caf\u00e9 \u2019 \U0001f4bf"]),
                        env))
    return out


def fam_filesystem(work):
    """Hostile filesystem conditions at the output path."""
    out = []

    # AS ROOT, PERMISSION BITS DO NOT BIND. Measured here rather than assumed:
    # `touch` into a 0555 directory succeeds at euid 0. These three probes are
    # therefore unable to fail in this container, and a check that cannot fire
    # is worse than a missing one -- it reads as coverage. They are skipped
    # with a stated reason instead of quietly passing.
    if os.geteuid() == 0:
        UNPROBED_STATIC.add(
            "fs/readonly-*: running as root (euid 0), where permission bits do "
            "not bind -- verified by writing into a 0555 directory. Re-run "
            "unprivileged to probe these three")
    else:
        ro = work / "readonly"
        ro.mkdir(exist_ok=True)
        os.chmod(ro, 0o555)
        out.append(("fs/readonly-outdir",
                ["-d", "basic.cue", "-N", "-A", "-U", "-s", "0", "-P", "0",
                     "-o", "flac", "-D", "readonly/out", "-L", "log",
                     "-M", "sheet"]))
        out.append(("fs/diagnostics-to-readonly",
                    base(work, ["-j", "readonly/d.json"])))
        out.append(("fs/diagnostics-to-dir", base(work, ["-j", "readonly"])))

    afile = work / "afile"
    afile.write_text("not a directory\n")
    out.append(("fs/outdir-is-a-file",
                ["-d", "basic.cue", "-N", "-A", "-U", "-s", "0", "-P", "0",
                 "-o", "flac", "-D", "afile/out", "-L", "log", "-M", "sheet"]))

    deep = "/".join(["d"] * 60)
    out.append(("fs/very-deep-outdir",
                ["-d", "basic.cue", "-N", "-A", "-U", "-s", "0", "-P", "0",
                 "-o", "flac", "-D", f"out/{deep}", "-L", "log",
                 "-M", "sheet"]))

    try:
        (work / "loop").symlink_to("loop")
    except OSError:
        pass
    out.append(("fs/symlink-loop-outdir",
                ["-d", "basic.cue", "-N", "-A", "-U", "-s", "0", "-P", "0",
                 "-o", "flac", "-D", "loop/out", "-L", "log", "-M", "sheet"]))

    # /dev/full accepts writes and fails them. A writer that never checks is
    # how a truncated archival record gets written and reported as complete.
    out.append(("fs/diagnostics-to-dev-full", base(work, ["-j", "/dev/full"])))
    return out


def fam_rerun(work):
    """Ripping twice into an occupied directory.

    An operator re-runs a rip. Whether the second run overwrites, refuses, or
    half-writes decides whether a partially-overwritten archive can be told
    from a complete one. Two invocations, identical -- the finding, if there is
    one, is in the second.
    """
    return [("rerun/first", base(work, ["-D", "rerun"])),
            ("rerun/second", base(work, ["-D", "rerun"])),
            ("rerun/third-different-meta",
             base(work, ["-D", "rerun", "-a", "album=Different"]))]


FAMILIES = {
    "metadata": fam_metadata,
    "containment": fam_containment,
    "environment": fam_environment,
    "filesystem": fam_filesystem,
    "rerun": fam_rerun,
    "scheme": fam_scheme,
    "image": fam_image,
    "selection": fam_selection,
    "verify": fam_verify,
    "combo": fam_combo,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--binary", default=str(ROOT / "build" / "src" / "cyanrip"))
    ap.add_argument("--family", action="append", choices=sorted(FAMILIES))
    ap.add_argument("--gate", action="store_true",
                    help="exit non-zero if any invariant was broken")
    ap.add_argument("--list", action="store_true",
                    help="print the probes and exit without running them")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    binary = Path(args.binary).resolve()
    if not binary.exists():
        sys.exit(f"no such binary: {binary}")

    banner = subprocess.run([str(binary), "--version"], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=60
                            ).stdout.decode("utf-8", "replace").strip()
    m = re.match(r"^(cyanrip \S+)", banner)
    banner_re = re.compile(re.escape(m.group(1)) if m else r"^cyanrip ")
    can_sanitize = instrumented(binary)

    families = args.family or sorted(FAMILIES)
    findings, unprobed, runs = [], set(), []

    print(f"binary   {binary}")
    print(f"banner   {banner}")
    print(f"sanitize {'yes' if can_sanitize else ('unknown' if can_sanitize is None else 'NO -- I4 cannot fire')}")
    print(f"families {', '.join(families)}\n")

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for f in FIX.glob("*.cue"):
            shutil.copy(f, work)
        shutil.copy(FIX / "cdda.nrg", work)
        shutil.copy(FIX / "cdtext.toc", work)
        shutil.copy(FIX / "cdda.bin", work / "cdtext.bin")
        for n in ("basic", "pregap", "preemph", "ecd"):
            shutil.copy(FIX / "cdda.bin", work / f"{n}.bin")
        shutil.copy(FIX / "mixed.bin", work / "mixed.bin")
        out_root = work / "out"
        out_root.mkdir(exist_ok=True)

        probes = []
        for name in families:
            probes.extend(FAMILIES[name](work))

        # A family may return (label, argv) or (label, argv, env_overlay).
        probes = [p if len(p) == 3 else (p[0], p[1], None) for p in probes]

        if args.list:
            for label, argv, env in probes:
                print(f"{label}\n    {argv}" + (f"\n    env {env}" if env else ""))
            print(f"\n{len(probes)} probe(s)")
            return 0

        for i, (label, argv, env) in enumerate(probes, 1):
            run = invoke(binary, label, argv, work, out_root, env)
            runs.append(run)
            check(run, banner_re, can_sanitize, findings, unprobed)
            if args.verbose:
                print(f"  [{i}/{len(probes)}] {label} -> "
                      f"{'TIMEOUT' if run.timed_out else run.exit_code}")
            elif i % 25 == 0:
                print(f"  ... {i}/{len(probes)}", flush=True)

        # fam_filesystem chmods a directory to 0o555, and a file inside a
        # read-only directory cannot be unlinked -- so TemporaryDirectory's own
        # cleanup would fail and the sweep would end in a traceback AFTER doing
        # all its work. Restore every directory before leaving the block.
        for d in work.rglob("*"):
            if d.is_dir():
                try:
                    os.chmod(d, 0o755)
                except OSError:
                    pass

    print(f"\n{len(runs)} invocation(s)\n")

    by_inv = {}
    for inv, label, what, argv in findings:
        by_inv.setdefault(inv, []).append((label, what, argv))

    NAMES = {"I1": "killed by a signal", "I2": "did not terminate",
             "I3": "silent non-zero exit", "I4": "sanitizer diagnostic",
             "I6": "wrote outside the output directory",
             "I7": "logfile does not carry this fork's banner"}
    for inv in sorted(by_inv):
        rows = by_inv[inv]
        print(f"=== {inv}  {NAMES.get(inv, '')} -- {len(rows)} ===")
        for label, what, argv in rows:
            print(f"  {label}")
            print(f"      {what}")
            print(f"      argv: {argv}")
        print()

    for u in sorted(unprobed | UNPROBED_STATIC):
        print(f"UNPROBED  {u}")

    # An exit-code census, because "no invariant broke" is not "nothing
    # happened", and a reader is entitled to see the shape of what did.
    census = {}
    for r in runs:
        k = "timeout" if r.timed_out else (
            f"signal {r.signal}" if r.signal is not None else f"exit {r.exit_code}")
        census[k] = census.get(k, 0) + 1
    print("\nexit-code census (an observation, not a verdict):")
    for k in sorted(census, key=lambda k: (-census[k], k)):
        print(f"  {census[k]:5d}  {k}")

    if findings:
        print(f"\n{len(findings)} invariant violation(s) across "
              f"{len({f[1] for f in findings})} invocation(s)")
    else:
        print("\nno invariant violations")

    return 1 if (args.gate and findings) else 0


if __name__ == "__main__":
    sys.exit(main())
