#!/usr/bin/env python3
# Rips the disc image fixtures and verifies the finished files.
# Usage: rip_images.py <cyanrip-binary> <fixtures-dir> <scenario>

import hashlib
import importlib.util
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CRIP = str(Path(sys.argv[1]).resolve())
FIX = Path(sys.argv[2])
SCENARIO = sys.argv[3]
# The repo root, for tools/ -- the handshake scenario asks the release gate
# what it says rather than hardcoding an expectation that would go stale.
ROOT = Path(__file__).resolve().parent.parent

FFPROBE = shutil.which("ffprobe")

fails = 0


def fail(msg):
    global fails
    print("FAIL:", msg)
    fails += 1


def skip(msg):
    """Exit 77, which meson reports as skipped and counts separately.

    For a check that CANNOT RUN here, never for one that ran and found
    nothing -- those are different claims and collapsing them is the thing
    this suite exists to stop. A skip stays visible in meson's summary, so
    coverage cannot vanish quietly; it just does not read as a defect in the
    thing under test when the limitation is the environment.
    """
    print("SKIP:", msg)
    sys.exit(77)


def crip(*args, cwd=None, env=None):
    r = subprocess.run([CRIP, *map(str, args)], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=60, cwd=cwd, env=env)
    return r.returncode, r.stdout.decode(errors="replace")


def rip(name, img, *extra, cwd=None):
    # libcdio's cdrdao driver opens a .toc's FILE with the raw relative path
    # instead of the absolute one it just computed (lib/driver/image/cdrdao.c,
    # cdio_stdio_new(psz_field) rather than psz_filename -- bincue.c gets this
    # right), so a .toc only loads when the process runs in its directory.
    # cwd= lets a scenario satisfy that; everything else keeps absolute paths.
    ec, log = crip("-d", img if cwd else WORK / img,
                   "-N", "-A", "-U", "-s", "0", "-P", "0",
                   "-o", "flac", "-D", WORK / f"out_{name}", "-F", "{track}",
                   "-L", "log", "-M", "sheet", *extra, cwd=cwd)
    (WORK / f"{name}.log").write_text(log)
    if ec != 0:
        fail(f"{name}: cyanrip exited with {ec} (log follows)")
        print(log)


def probe(path, *entries):
    r = subprocess.run([FFPROBE, "-v", "error", *entries, "-of",
                        "default=nw=1:nk=1", str(path)],
                       stdout=subprocess.PIPE, timeout=60)
    return r.stdout.decode().strip()


def pcm_md5(name, track):
    data = (WORK / f"out_{name}" / f"{track}.pcm").read_bytes()
    return hashlib.md5(data).hexdigest()


def expect(name, *specs):
    out = WORK / f"out_{name}"
    want = sorted(s.split(":")[0] for s in specs)
    have = sorted(p.name for p in out.iterdir()) if out.is_dir() else []
    if have != want:
        fail(f"{name}: outputs {have} != expected {want}")
        return

    for spec in specs:
        f, _, dur = spec.partition(":")
        path = out / f

        if f.endswith(".flac") and path.read_bytes()[:4] != b"fLaC":
            fail(f"{name}: {f} is not FLAC")

        if dur and FFPROBE:
            d = probe(path, "-show_entries", "format=duration")
            if abs(float(d) - float(dur)) > 0.1:
                fail(f"{name}: {f} duration {d} != {dur}")


def sc_info():
    # Info-only mode on every image type
    for img in ("basic.cue", "pregap.cue", "mixed.cue", "preemph.cue",
                "cdda.nrg"):
        ec, _ = crip("-d", WORK / img, "-I", "-N", "-A", "-U", "-P", "0")
        if ec != 0:
            fail(f"info {img}: cyanrip exited with {ec}")


def sc_cli():
    # Version probing. cyanrip 0.9.3 and earlier spelled this -V; genopt moved
    # it to -v, which broke callers probing with -V -- they get exit 1 and a
    # parse error, which reads as "not installed" rather than "flag renamed".
    # All three spellings must work, and the banner must carry the fork id so a
    # consumer can tell a fork build from stock upstream.
    for flag in ("-V", "-v", "--version"):
        ec, out = crip(flag)
        if ec != 0:
            fail(f"cli: {flag} exited {ec}, wanted 0")
        if "platterpus-fork" not in out:
            fail(f"cli: {flag} banner missing fork id: {out.strip()!r}")

    # All three must agree, or a consumer's answer depends on which it asked.
    banners = {crip(f)[1].strip() for f in ("-V", "-v", "--version")}
    if len(banners) != 1:
        fail(f"cli: version spellings disagree: {banners}")

    # The version number must stay inside a namespace upstream cannot mint.
    # Releases r1/r2 shipped bare "0.9.4-rc1", indistinguishable from each other
    # and from upstream; the first fix attempt advanced our own rc number to
    # "0.9.4-rc3", which upstream can also tag. Both were reverted in favour of
    # SemVer build metadata. This is the check that fails if it ever drifts back:
    # a bare upstream-shaped number with nothing after it.
    banner = banners.pop()
    ver = re.search(r"^cyanrip (\S+)", banner)
    if not ver:
        fail(f"cli: banner has no version field: {banner!r}")
    elif "+platterpus." not in ver.group(1):
        fail(f"cli: version {ver.group(1)!r} is in upstream's namespace -- a "
             "fork build must carry a +platterpus.N suffix upstream cannot mint")

    # The build tag must identify a build. Packaging beta.7 as a source tarball
    # produced "platterpus-fork-g-dirty": with no .git, `git rev-parse` printed
    # nothing and `git diff --quiet` failed, so the sh -c still exited 0 and
    # meson's fallback never fired. That string names no build AND asserts a
    # modification that did not happen -- permanently, in every logfile, which
    # for this program is an archival record. Fixed with git-archive
    # export-subst; this pins the shape from either source.
    tag = re.search(r"\(platterpus-fork-g([^)]*)\)", banner)
    if not tag:
        fail(f"cli: banner has no build tag: {banner!r}")
    elif not re.fullmatch(r"[0-9a-f]{7,}(-dirty)?|unknown", tag.group(1)):
        fail(f"cli: build tag {tag.group(1)!r} names no build -- wanted a "
             "commit, optionally -dirty, or the explicit string 'unknown'")

    # -h must still work and must not be confused with the above
    if crip("-h")[0] != 0:
        fail("cli: -h exited non-zero")

    # -k (read-liveness threshold) must be accepted across its range, including
    # 0, which disables the reporting entirely.
    for k in ("0", "1", "45"):
        if crip("-d", WORK / "basic.cue", "-I", "-N", "-A", "-U", "-P", "0", "-k", k)[0] != 0:
            fail(f"cli: -k {k} was rejected")

    # -x (drive cache probe) must be accepted, must refuse to guess on an
    # image rather than print a meaningless number, and must not appear at all
    # unless asked for. The measurement itself needs a real drive.
    ec, out = crip("-d", WORK / "basic.cue", "-I", "-N", "-A", "-U", "-P", "0", "-x")
    if ec != 0:
        fail(f"cli: -x was rejected (exit {ec})")
    if "Cache probe:    not run (disc image has no drive cache)" not in out:
        fail("cli: -x on an image did not refuse to measure")
    if "Cache probe:" in crip("-d", WORK / "basic.cue", "-I", "-N", "-A",
                             "-U", "-P", "0")[1]:
        fail("cli: Cache probe line appeared without -x")

    # -s is bounded, and the bound is a fix rather than tidiness. It took the
    # full int32 range, and UBSAN reaches three separate undefined behaviours on
    # INT32_MIN: the negation in cyanrip_run(), the abs() in the Offset: log
    # line -- which printed "--2147483648", a doubled sign in a contract line --
    # and `offset*4` in setup_track_lsn(), which is signed overflow in
    # arithmetic a real rip performs. Found by tools/probe-argv-surface.py and
    # reported to Platterpus in round 7 lap 30 (seam-rules S-11: a defect found
    # at the seam gets its regression test in the same change, naming the
    # round).
    #
    # Boundary and one past each, which is what S-9 asks for.
    for v, want in ((-1048576, 0), (1048576, 0), (-1048577, 1), (1048577, 1),
                    (-2147483648, 1)):
        ec, out = crip("-d", WORK / "basic.cue", "-I", "-N", "-A", "-U",
                       "-P", "0", "-s", str(v))
        if ec != want:
            fail(f"cli: -s {v} exited {ec}, wanted {want}")
        if want and "range" not in out:
            fail(f"cli: -s {v} was refused without naming the range: {out.strip()[:90]!r}")

    # The magnitude is printed unsigned, so no accepted value can double the
    # sign. Asserted on the widest accepted value, which is where it broke.
    _, out = crip("-d", WORK / "basic.cue", "-I", "-N", "-A", "-U", "-P", "0",
                  "-s", "-1048576")
    if "--" in out.split("Offset:")[1].split("\n")[0]:
        fail("cli: the Offset: line doubled its sign")

    # -t requires its "<track>=" prefix, and the check is a memory-safety fix
    # rather than input tidiness. cyanrip did strtol() and then stepped one past
    # the terminator without checking a "=" was ever there, so "-t 1" walked off
    # the end of the argv string and append_missing_keys() copied whatever
    # followed it in memory into that track's metadata dictionary -- reaching
    # the FLAC tags, the log and the cue at exit 0, with nothing printed. An
    # environment variable landed in a rip's archival record that way.
    # Reported by Platterpus in round 7 lap 31 (seam-rules S-11: a defect found
    # at the seam gets its regression test in the same change, naming the
    # round).
    #
    # Note ASAN and UBSAN are both silent on this: argv and environ strings
    # share the initial stack block, so the overread crosses no boundary either
    # sanitizer redzones. A behavioural assertion is the only thing that catches
    # it, which is why this asserts on output rather than on a clean run.
    #
    # This pair is the discriminator -- reverting the fix makes "-t 1" exit 0.
    ec, out = crip("-d", WORK / "basic.cue", "-I", "-N", "-A", "-U", "-P", "0",
                   "-t", "1")
    if ec != 1:
        fail(f"cli: bare -t 1 exited {ec}, wanted 1")
    if "Missing \"=\" in track metadata" not in out:
        fail(f"cli: bare -t 1 gave no diagnosable message: {out.strip()[:90]!r}")

    # And the leak itself, named. This cannot fire unless adjacent memory is
    # genuinely being published, but which bytes follow the argv string is a
    # layout detail, so it is a safety net rather than the discriminator above.
    # The canary is placed first in a minimal environment because envp[0]
    # directly follows the last argv string, which is where it was observed.
    canary = "MUST-NOT-REACH-METADATA"
    ec, out = crip("-d", WORK / "basic.cue", "-I", "-N", "-A", "-U", "-P", "0",
                   "-t", "1",
                   env={"CYANRIP_LEAK_CANARY": canary,
                        "PATH": os.environ.get("PATH", "")})
    if canary in out:
        fail("cli: bare -t 1 published adjacent process memory into metadata")

    # The well-formed spelling is untouched, including the backslash escape
    # Platterpus relies on for a colon inside a value.
    ec, out = crip("-d", WORK / "basic.cue", "-I", "-N", "-A", "-U", "-P", "0",
                   "-t", r"1=title=A\: B")
    if ec != 0:
        fail(f"cli: well-formed -t exited {ec}, wanted 0")
    if "A: B" not in out:
        fail("cli: -t lost the escaped colon in a track title")

    # An argument that is nothing but its own separator tokenises to no token
    # at all, and both -c and -p then handed NULL to strtol(). Four segfaults:
    # -c / -c // -p = -p ==, each exiting 139 with not one line of output --
    # the undiagnosable non-zero exit the seam rules single out as the one
    # failure a consumer cannot explain. Found by adding a malformed-shape axis
    # to tools/probe-argv-surface.py after Platterpus's lap 31 J3 report showed
    # the grid had never varied argument shape.
    #
    # The second av_strtok() in both functions was always NULL-checked; the
    # first never was, because a non-empty string was assumed to yield a token.
    for flag, val in (("-c", "/"), ("-c", "//"), ("-p", "="), ("-p", "==")):
        ec, out = crip("-d", WORK / "basic.cue", "-I", "-N", "-A", "-U",
                       "-P", "0", flag, val)
        if ec < 0 or ec == 139:
            fail(f"cli: {flag} {val!r} died by signal (exit {ec})")
        if ec != 1:
            fail(f"cli: {flag} {val!r} exited {ec}, wanted 1")
        if "Missing" not in out:
            fail(f"cli: {flag} {val!r} exited non-zero with no diagnosis: "
                 f"{out.strip()[:90]!r}")

    # ...and the well-formed spellings still work, or the guards are too wide.
    for flag, val in (("-c", "1/2"), ("-p", "1=drop")):
        if crip("-d", WORK / "basic.cue", "-I", "-N", "-A", "-U", "-P", "0",
                flag, val)[0] != 0:
            fail(f"cli: {flag} {val!r} was rejected")

    # A genuinely unknown flag must still fail, diagnosably, on stdout
    ec, out = crip("--no-such-flag")
    if ec != 1:
        fail(f"cli: unknown flag exited {ec}, wanted 1")
    if "Unable to parse" not in out:
        fail(f"cli: unknown flag gave no diagnosable message: {out.strip()!r}")


def sc_basic():
    rip("basic", "basic.cue")
    expect("basic", "1.flac:4", "2.flac:4", "log.log", "sheet.cue")


def sc_pregap():
    # Track 1 HTOA stays unmerged by default, track 2 pregap merges into track 1
    rip("def", "pregap.cue")
    expect("def", "1.flac:3", "2.flac:2", "3.flac:1", "log.log", "sheet.cue")

    # HTOA becomes track 0, track 2 pregap becomes a track of its own
    rip("track", "pregap.cue", "-p", "1=track", "-p", "2=track")
    expect("track", "0.flac:2", "1.flac:2", "2.flac:1", "3.flac:2",
           "4.flac:1", "log.log", "sheet.cue")

    rip("drop", "pregap.cue", "-p", "2=drop")
    expect("drop", "1.flac:2", "2.flac:2", "3.flac:1", "log.log", "sheet.cue")

    # An INDEX 00 is an offset into the FILE it is nested under, so a partial
    # rip that excludes the track holding the gap must not emit one. Round 8,
    # Platterpus's 2026-08-14 hand-off §8: on `-l 1,3,5,6,7` track 5's marker
    # was computed against excluded track 4 and printed inside track 3's FILE,
    # 682 frames past its end. Upstream-origin, so stock cyanrip has it too.
    #
    # Track 2 carries the signalled pre-gap here, so -l 2,3 is the shape: its
    # predecessor is not in the rip set and its FILE is never written.
    rip("lgap", "pregap.cue", "-l", "2,3")
    cue = (WORK / "out_lgap" / "sheet.cue").read_text()
    if "INDEX 00" in cue:
        fail("lgap: INDEX 00 written against a FILE the rip never produced:\n"
             + cue)

    # Not vacuous: the same disc ripped whole DOES emit one, so the assertion
    # above is about the selection and not about the fixture having no gaps.
    full = (WORK / "out_def" / "sheet.cue").read_text()
    if "INDEX 00" not in full:
        fail("lgap: the full rip emits no INDEX 00, so the -l check proves "
             "nothing about the fix")

    # One log must not disagree with itself about the same gap.
    #
    # Four places state track N's pregap length, and they were not all saying
    # the same thing: the per-track block added the 2-second lead-in to track 1
    # unconditionally, so on a disc whose TOC already signals an HTOA the same
    # 150 sectors were counted twice -- `300 frames` and `00:04.00` against a
    # `Gaps:` block, an LSN subtraction and a cue sheet that all said 150.
    #
    # Track 2 is the control: its four agreed all along, which is what made
    # track 1 a finding rather than a doubt about the arithmetic. Both are
    # checked, so a "fix" that made every source equally wrong would fail here.
    log = (WORK / "out_def" / "log.log").read_text()
    gaps = dict((int(n), int(f)) for f, n in
                re.findall(r"^ +(\d+) frame pregap in track (\d+),", log, re.M))
    # Track 1's Gaps: row is absent when its gap is the bare lead-in, so the
    # expectation comes from the fixture's own INDEX 00/01 pair: 2 s and 1 s.
    for num, want in ((1, 150), (2, 75)):
        blk = re.search(rf"^Track {num} ripped.*?(?=^Track |\Z)", log,
                        re.M | re.S)
        if not blk:
            fail(f"pregap: no track {num} block")
            continue
        b = blk.group(0)
        m_len = re.search(r"^ +Pregap length: (\d+) frames", b, re.M)
        m_lsn = re.search(r"^ +Pregap LSN:  (\d+) \(duration: (\S+)\)", b, re.M)
        m_start = re.search(r"^ +Start LSN:   (\d+)", b, re.M)
        if not (m_len and m_lsn and m_start):
            fail(f"pregap: track {num} is missing a pregap/LSN row")
            continue

        if int(m_len.group(1)) != want:
            fail(f"pregap: track {num} 'Pregap length' is "
                 f"{m_len.group(1)}, not {want}")

        # The duration must be the same quantity in MM:SS.FF, not a second
        # opinion -- both are printed from one variable and must stay that way.
        mm, ss_ff = m_lsn.group(2).split(":")
        ss, ff = ss_ff.split(".")
        as_frames = (int(mm) * 60 + int(ss)) * 75 + int(ff)
        if as_frames != want:
            fail(f"pregap: track {num} duration {m_lsn.group(2)} is "
                 f"{as_frames} frames, not {want}")

        # And the LSN arithmetic, which is the independent artifact: it comes
        # from the TOC rather than from the line above it.
        span = int(m_start.group(1)) - int(m_lsn.group(1))
        if num in gaps and gaps[num] != want:
            fail(f"pregap: track {num} Gaps: row says {gaps[num]}, not {want}")
        if span and span != want:
            fail(f"pregap: track {num} Start LSN - Pregap LSN = {span}, "
                 f"but the block says {want}")


def sc_mixed():
    # Data track must be skipped, and produce no stray file
    rip("mixed", "mixed.cue")
    expect("mixed", "2.flac:2", "3.flac:2", "log.log", "sheet.cue")

    # Data track selected via rip indices
    rip("idx", "mixed.cue", "-l", "1,2")
    expect("idx", "2.flac:2", "log.log", "sheet.cue")


def sc_nrg():
    # NRG with a DAOX pregap on track 2
    rip("nrg", "cdda.nrg")
    expect("nrg", "1.flac:3", "2.flac:3", "log.log", "sheet.cue")


def sc_contract_covers_log():
    # Every label a real rip prints must be known to the contract.
    #
    # This is the floor the contract could previously decay past, and
    # Platterpus proposed it in their 2026-08-14 hand-off §6: "run a real rip,
    # extract every label from the resulting log, and fail the generator if any
    # is absent from P2". We built only the first half of that fix -- the
    # generator changes -- and this is the second, which is what found the
    # defect the first half did not:
    #
    #   `Log FUN512: ` is written with a bare fprintf() to the logfile, never
    #   through cyanrip_log(), because it is the checksum OVER the log and must
    #   be appended after the log is otherwise finished. The scanner knew
    #   cyanrip_log(), genopt and fprintf(stderr) and had no pattern for it, so
    #   a stable line present in EVERY logfile -- the one `-Y/--verify-log`
    #   round-trips -- was absent from every provider contract ever published.
    #
    # A positive check ("the labels I expected are there") could never have
    # found that, because nobody expected it. This asks the log what it says.
    rip("cov", "pregap.cue", "-Z", "2", "-G", "-Q")
    log = (WORK / "out_cov" / "log.log").read_text()
    contract = (ROOT / "PROVIDER-CONTRACT.md").read_text()

    # Column-0 labels only: an indented row is a per-track field, and the
    # label must be followed by whitespace so `Ripping finished at 2026-08-15T20:`
    # is not read as a label ending in the timestamp's own colon.
    labels = sorted(set(re.findall(r"^([A-Z][A-Za-z0-9 /()-]*:)(?=\s)", log, re.M)))
    if len(labels) < 15:
        fail(f"contract_covers_log: only {len(labels)} labels found -- the "
             "extraction is broken, not the contract")
        return

    # Two labels are libavfilter's, not ours, and the contract says so in P3
    # rather than publishing them as API. `Album Loudness Summary:` is the
    # split case: `Album Loudness` is ours, ` Summary:` is the filter's.
    NOT_OURS = {"Summary:", "Album Loudness Summary:"}

    missing = [l for l in labels
               if l not in NOT_OURS and l.rstrip(":") not in
               {n.rstrip(":") for n in NOT_OURS}
               and l not in contract]
    if missing:
        fail("contract_covers_log: the log prints labels the contract has "
             "never heard of, so they sit outside our own breaking-change "
             f"rule: {missing}")


def sc_album_loudness():
    # Album-level loudness must be readable from lines we own.
    #
    # Only the two words `Album Loudness` were ours -- the ` Summary:` tail and
    # every value under it are libavfilter's ebur128 output, wording our own
    # contract marks as moving when FFmpeg does. So one FFmpeg release could
    # empty a consumer's whole album_loudness field silently, with no version
    # signal to branch on and nothing else in the log to fall back to. Round 8,
    # Platterpus's 2026-08-14 hand-off §1.
    #
    # Asserted against libavfilter's OWN block in the same log, not against
    # constants: a test comparing our line to a string we wrote proves only
    # that a constant can be printed, and both halves come from the same filter
    # so they must agree exactly.
    rip("albloud", "pregap.cue", "-G")
    whole = (WORK / "out_albloud" / "log.log").read_text()

    # Bounded to the album block. Every ripped track prints an ebur128
    # `Summary:` of its own, so an unbounded search finds track 1's numbers and
    # compares them against the album's -- which is what the first version of
    # this test did, reporting a mismatch that was entirely its own.
    start = whole.find("Album Loudness Summary:")
    if start < 0:
        fail("album_loudness: no album block at all")
        return
    log = whole[start:]

    def one(pat, what):
        m = re.search(pat, log, re.M)
        if not m:
            fail(f"album_loudness: no {what} line")
        return m.group(1) if m else None

    theirs = {
        "I": one(r"^\s+I:\s+(-?\d+\.\d)\s+LUFS", "libav integrated"),
        "LRA": one(r"^\s+LRA:\s+(-?\d+\.\d)\s+LU", "libav LRA"),
        "low": one(r"^\s+LRA low:\s+(-?\d+\.\d)\s+LUFS", "libav LRA low"),
        "high": one(r"^\s+LRA high:\s+(-?\d+\.\d)\s+LUFS", "libav LRA high"),
    }
    ours = {
        "I": one(r"^Album integrated loudness \(R128\): (-?\d+\.\d) LUFS", "owned integrated"),
        "LRA": one(r"^Album loudness range \(R128\):\s+(-?\d+\.\d) LU", "owned LRA"),
        "low": one(r"^Album loudness range \(R128\):.*\((-?\d+\.\d) to", "owned LRA low"),
        "high": one(r"^Album loudness range \(R128\):.*to (-?\d+\.\d) LUFS", "owned LRA high"),
    }
    for k in theirs:
        if theirs[k] is not None and ours[k] != theirs[k]:
            fail(f"album_loudness: our {k} is {ours[k]} but libavfilter's own "
                 f"block says {theirs[k]} in the same log")

    # Peaks likewise, and both `Peak:` rows are ambiguous alone -- the sample
    # one comes first under `Sample peak:`, the true one under `True peak:`.
    peaks = re.findall(r"^\s+(?:Sample|True) peak:\n\s+Peak:\s+(-?\d+\.\d) dBFS",
                       log, re.M)
    if len(peaks) != 2:
        fail(f"album_loudness: expected 2 libav peak rows, found {len(peaks)}")
    else:
        for label, want in (("sample", peaks[0]), ("true", peaks[1])):
            got = one(rf"^Album {label} peak level:\s+(-?\d+\.\d) dBFS",
                      f"owned {label} peak")
            if got != want:
                fail(f"album_loudness: our {label} peak is {got} but "
                     f"libavfilter's own block says {want}")

    # The qualifier is load-bearing: unqualified, it collides with
    # libavfilter's own heading in the same log.
    if re.search(r"^Album integrated loudness:", log, re.M):
        fail("album_loudness: the (R128) qualifier is gone, so the label "
             "collides with libavfilter's own unqualified heading")


def sc_filters():
    # The HDCD and deemphasis filter graphs, verified on raw PCM output
    rip("plain", "basic.cue", "-o", "pcm")
    expect("plain", "1.pcm", "2.pcm", "log.log", "sheet.cue")
    plain_size = (WORK / "out_plain" / "1.pcm").stat().st_size
    if plain_size != 4 * 44100 * 2 * 2:
        fail(f"plain: 1.pcm is {plain_size} bytes")

    # HDCD decodes to 24-bit, so raw output must be s32
    rip("hdcd", "basic.cue", "-o", "pcm", "-H")
    hdcd_size = (WORK / "out_hdcd" / "1.pcm").stat().st_size
    if hdcd_size != 2 * plain_size:
        fail(f"hdcd: 1.pcm is {hdcd_size} bytes, wanted {2 * plain_size}")

    # Forced deemphasis must actually alter the audio
    rip("forced", "basic.cue", "-o", "pcm", "-E")
    if pcm_md5("forced", 1) == pcm_md5("plain", 1):
        fail("-E did not change the audio")

    # TOC preemphasis flags trigger automatic deemphasis, matching -E;
    # -W disables it, matching an unfiltered rip
    rip("auto", "preemph.cue", "-o", "pcm")
    if pcm_md5("auto", 1) != pcm_md5("forced", 1):
        fail("automatic deemphasis output doesn't match -E")

    rip("off", "preemph.cue", "-o", "pcm", "-W")
    if pcm_md5("off", 1) != pcm_md5("plain", 1):
        fail("-W did not disable deemphasis")


def sc_art():
    # Album cover art: written out per format and embedded in every track
    rip("art", "basic.cue", "-C", f"Front={FIX / 'art.png'}")
    expect("art", "1.flac:4", "2.flac:4", "Front.png", "log.log", "sheet.cue")
    if FFPROBE:
        for f in (1, 2):
            pics = probe(WORK / "out_art" / f"{f}.flac", "-select_streams",
                         "v", "-show_entries", "stream=codec_name")
            if len(pics.splitlines()) != 1:
                fail(f"art: {f}.flac embedded pictures: {pics!r}, wanted 1")

            # Typed as a front cover, or file managers won't thumbnail it
            ptype = probe(WORK / "out_art" / f"{f}.flac", "-select_streams",
                          "v", "-show_entries", "stream_tags=comment")
            if ptype != "Cover (front)":
                fail(f"art: {f}.flac picture type {ptype!r}")


def sc_cue_only():
    # -J generates and prints the CUE sheet without ripping anything
    rip("cue", "pregap.cue", "-J")
    have = sorted(p.name for p in (WORK / "out_cue").iterdir())
    if have != ["sheet.cue"]:
        fail(f"cue_only: outputs {have}, wanted only the CUE sheet")

    cue = (WORK / "out_cue" / "sheet.cue").read_text()
    if 'FILE "1.flac" WAVE' not in cue:
        fail("cue_only: file references are not relative to the sheet")
    if "TRACK 03 AUDIO" not in cue:
        fail("cue_only: cue sheet incomplete")

    if "TRACK 01 AUDIO" not in (WORK / "cue.log").read_text():
        fail("cue_only: cue sheet not printed to the terminal")

    if crip("-d", WORK / "basic.cue", "-J", "-I")[0] != 1:
        fail("cue_only: -J with -I did not error out")


def sc_errors():
    # Schemes sending multiple tracks to one file must be warned about
    rip("collide", "basic.cue", "-F", "{album}")
    if "resolve to the same file" not in (WORK / "collide.log").read_text():
        fail("collide: expected a filename collision warning")

    # Encoder init failure (file name too long) must fail cleanly, not
    # crash in cleanup on the uninitialized encoder mutex/thread
    ec, _ = crip("-d", WORK / "basic.cue", "-N", "-A", "-U", "-s", "0",
                 "-P", "0", "-K", "-o", "flac", "-D", WORK / "out_longname",
                 "-F", "x" * 300, "-L", "log", "-M", "sheet")
    if ec != 1:
        fail(f"longname: expected clean failure (1), got exit {ec}")

    # -p with a track the disc does not have. Round 8, from Platterpus's
    # 2026-08-14 hand-off §9: -p was bounded at a fixed 197 because it parses
    # before the TOC is read, so `-p 99=drop` on a short disc was accepted,
    # exited 0, and went into a slot no track reads -- while -t rejected the
    # same mistake outright. Accepted-and-ignored is the outcome the seam rules
    # call worse than a refusal, because a refusal gets investigated.
    #
    # Both ends are asserted. Checking only the refusal would pass just as well
    # if the bound rejected everything.
    for bad in ("99=drop", "4=drop"):
        ec, out = crip("-I", "-N", "-d", WORK / "pregap.cue", "-p", bad)
        if ec == 0:
            fail(f"-p {bad}: accepted a track the 3-track disc does not have")
        if "Invalid track number" not in out:
            fail(f"-p {bad}: refused with no diagnosable line: {out[-200:]!r}")

    ec, out = crip("-I", "-N", "-d", WORK / "pregap.cue", "-p", "3=drop")
    if ec != 0:
        fail(f"-p 3=drop: refused a track the disc has (exit {ec}): {out[-200:]!r}")


def sc_cdtext():
    # A cdrdao .toc image is the only disc image format libcdio parses CD-TEXT
    # from, so it stands in for a CD-TEXT disc that no drive is needed to read.
    rip("cdtext", "cdtext.toc", cwd=WORK)
    log = (WORK / "out_cdtext" / "log.log").read_text()

    if "CD-TEXT:        present (English, 5 disc fields, 2 of 2 tracks tagged)" not in log:
        fail("cdtext: disc-level CD-TEXT summary line missing or wrong")

    # Disc-level fields, verbatim
    for field, value in (("title", "Probe Disc Title"),
                         ("performer", "Probe Disc Performer"),
                         ("message", "Probe disc message"),
                         ("upc_ean", "0123456789012"),
                         ("discid", "PROBE-DISCID")):
        if f"{field}:" not in log or value not in log:
            fail(f"cdtext: disc field {field}={value!r} missing")

    # Per-track fields, including the two that deliberately reach no tag
    for value in ("Probe Track One", "Probe Artist One", "Probe Writer One",
                  "Probe Composer One", "Probe Arranger One",
                  "Probe Track Two", "Probe Artist Two"):
        if value not in log:
            fail(f"cdtext: track field {value!r} missing")

    # CD-TEXT fills empty tags, so the disc is named rather than "Unknown disc"
    if "Album:          Probe Disc Title" not in log:
        fail("cdtext: album not filled from CD-TEXT")
    if "Unknown disc" in log:
        fail("cdtext: placeholder album survived a named CD-TEXT disc")

    # ...but never overrides what the user asked for
    rip("cdtext_user", "cdtext.toc", "-a", "album=User Album", cwd=WORK)
    ulog = (WORK / "out_cdtext_user" / "log.log").read_text()
    if "Album:          User Album" not in ulog:
        fail("cdtext_user: -a did not win over CD-TEXT")
    if "title:     Probe Disc Title" not in ulog:
        fail("cdtext_user: CD-TEXT block lost when a tag overrode it")

    # A disc with no CD-TEXT must say so, and say it was libcdio that reported
    # nothing -- not that the disc is definitely bare
    rip("cdtext_none", "basic.cue")
    nlog = (WORK / "out_cdtext_none" / "log.log").read_text()
    if "CD-TEXT:        none reported by libcdio" not in nlog:
        fail("cdtext_none: absent CD-TEXT not reported")


def sc_exit_codes():
    # A diagnosed abort must exit non-zero. The exit code used to track
    # total_error_count, which counts *read* errors -- so a refusal to start or
    # a rip that failed outright printed its reason and then exited 0, and a
    # consumer checking the exit code saw success on a run that produced no
    # audio.
    #
    # Our own generated contract flagged `goto end` as the one class it could
    # not classify from control flow and said it needed a run to settle.
    #
    # WHAT THIS DOES NOT COVER, stated so the scenario cannot imply otherwise:
    # every case below already exited 1 before the fix. Reverting the fix leaves
    # this scenario passing. The paths the fix actually changes are not
    # reachable from a disc image --
    #
    #   * "Offset is unset!" is gated on the drive reporting
    #     CDIO_DRIVE_CAP_READ_ISRC, which no image driver does, so it can only
    #     fire on real hardware.
    #   * the two cyanrip_rip_track failure paths need a rip that genuinely
    #     fails, which a synthetic image does not do.
    #
    # So the fix is UNVERIFIED by any test here, and that is an H12 item for the
    # rig session rather than something a fixture can retire. What this scenario
    # does pin is that the already-correct cases stay correct, and that a
    # non-zero exit is never silent.
    cases = [
        # (argv, expected exit, a string the output must contain)
        (("-d", str(WORK / "nonexistent.cue"), "-I", "-N", "-A", "-U"), 1, None),
        (("--no-such-flag",), 1, "Unable to parse command line argument"),
        (("-d", WORK / "basic.cue", "-N", "-A", "-U", "-s", "0", "-P", "0",
          "-o", "flac", "-D", WORK / "out_ec", "-F", "{track}", "-t", "99"),
         1, "Invalid track number 99"),
        (("-d", WORK / "basic.cue", "-I", "-N", "-A", "-U", "-S", "8"),
         1, "Device does not support changing speeds"),
    ]
    for argv, want_ec, want_text in cases:
        ec, out = crip(*argv)
        if ec != want_ec:
            fail(f"exit_codes: {argv[0]} {argv[1] if len(argv) > 1 else ''} "
                 f"exited {ec}, wanted {want_ec}")
        # Never a non-zero exit with nothing to explain it: that is the one
        # failure a user cannot be told anything about.
        if ec != 0 and not out.strip():
            fail(f"exit_codes: exit {ec} with no output at all for {argv}")
        if want_text and want_text not in out:
            fail(f"exit_codes: expected {want_text!r} in the output for {argv}")

    # And the converse, or the check above is satisfied by a binary that always
    # fails: a good run exits 0.
    ec, _ = crip("-d", WORK / "basic.cue", "-I", "-N", "-A", "-U", "-P", "0")
    if ec != 0:
        fail(f"exit_codes: a valid -I run exited {ec}, wanted 0")


def sc_handshake():
    # Every rip must record which pair of builds produced it. A log read months
    # later cannot otherwise tell a mutually-verified release from a mid-round
    # working tree, and those are different provenance.
    rip("hs", "basic.cue")
    log = (WORK / "out_hs" / "log.log").read_text()

    m = re.search(r"^Handshake:      (.+)$", log, re.M)
    if not m:
        fail("handshake: no Handshake: line in the log")
    else:
        state = m.group(1)
        # It must say round and verdict, not merely "ok".
        if not re.match(r"round \d+( lap \d+)? (OPEN|closed), verdict \S+", state) \
           and "unknown" not in state:
            fail(f"handshake: state not in the derived form: {state!r}")
        # An unreleased build must say so where a reader will see it, not
        # leave "closed" to be inferred from the absence of a warning.
        gate = subprocess.run([sys.executable, str(ROOT / "tools" / "release-gate.py"),
                               "--release-gate"], capture_output=True)
        open_round = gate.returncode != 0
        if open_round and "NOT a released build" not in state:
            fail(f"handshake: round is open but the log does not say so: {state!r}")

        # A CLOSED ROUND IS NOT A RELEASED BUILD. That is still the rule; what
        # changed in round 10 is how the second half is established.
        #
        # This block used to compute `is_the_pin` -- HEAD equals the newest
        # lap's HANDSHAKE-OUR-PIN on a clean tree -- and assert the disclaimer
        # against it. That was the `_head_is` design, and it is deleted: a lap
        # is read from a file inside the tree it names, so the pin can only ever
        # be an ancestor and `is_the_pin` was unreachable. It survived here as
        # dead code whose SECOND branch then did the work for the wrong reason:
        # with is_the_pin always false, it demanded the disclaimer on every closed
        # round -- including on a legitimately declared release, which correctly
        # omits it. Measured: the shipping configuration failed 2 of 41.
        #
        # The rule now is the declaration, so the test needs to know what the
        # binary was built with. meson passes it; without the variable we assume
        # the default, which is what a bare `python3 tests/rip_images.py` gets.
        declared = os.environ.get("CYANRIP_DECLARED_RELEASED") == "1"
        qualifier = "(declared at build time, not verified by cyanrip)"

        # The declaration is not the whole condition: a VISIBLY dirty tree
        # withdraws it. So a test that expects the released rendering from the
        # option alone fails for every developer with uncommitted work -- which
        # is how this test first failed, on the very change that added it.
        #
        # Asked of the generator rather than reimplemented with a second
        # `git status`. Two readers of one tree that can disagree is the failure
        # the release manifest already imports the gate's loader to avoid, and
        # a test disagreeing with the binary about the same tree would be
        # indistinguishable from the rendering being broken.
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            "ghs_probe", ROOT / "tools" / "gen-handshake-state.py")
        _ghs = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_ghs)
        expect_released = declared and not _ghs._known_dirty()

        if not open_round and not expect_released and "NOT a released build" not in state:
            fail(f"handshake: the round is closed and this build makes no "
                 f"effective release declaration, so the log must still "
                 f"disclaim: {state!r}")

        # The declared rendering, which nothing tested until now -- it was
        # verified only by hand-run transcripts pasted into handshake laps.
        if not open_round and expect_released:
            if "-- released build" not in state or "NOT a released build" in state:
                fail(f"handshake: built with -Ddeclare_released=true on a closed "
                     f"round, but the log does not say so: {state!r}")
            # ...and it must NOT go silent. Before round 10 a released build
            # printed no suffix at all, which made the strongest claim in the
            # line by omission. The qualifier is the whole fix: it says who
            # declared it and that cyanrip did not check.
            if qualifier not in log:
                fail("handshake: the released rendering dropped its qualifier "
                     f"{qualifier!r} -- a declaration rendering as a bare claim "
                     "is the defect round 10 existed to remove")
            # Adjacency, not mere presence. The qualifier belongs to the
            # Handshake: line; Consumer: has its own, two lines later, and a
            # reader folding by proximity must not graft one onto the other.
            for i, ln in enumerate(log.splitlines()):
                if ln.startswith("Handshake:"):
                    nxt = log.splitlines()[i + 1] if i + 1 < len(log.splitlines()) else ""
                    if qualifier not in nxt:
                        fail("handshake: the qualifier is not on the line "
                             f"immediately after Handshake:, it is {nxt!r}")
                    break

    # Without --consumer the log must say the caller did not identify itself,
    # rather than leaving the field absent -- a missing field prompts a
    # question, a field saying "not identified" answers it.
    if "Consumer:       not identified" not in log:
        fail("handshake: no Consumer: line when --consumer was not given")

    # With it, the value is recorded verbatim AND disclaimed. cyanrip cannot
    # check what the caller calls itself, and must not imply that it did.
    ec, _ = crip("-d", WORK / "basic.cue", "-N", "-A", "-U", "-s", "0", "-P", "0",
                 "-o", "flac", "-D", WORK / "out_hs2", "-F", "{track}",
                 "-L", "log", "-u", "platterpus/9.9.9-test")
    if ec != 0:
        fail(f"handshake: --consumer was rejected (exit {ec})")
    log2 = (WORK / "out_hs2" / "log.log").read_text()
    if "Consumer:       platterpus/9.9.9-test" not in log2:
        fail("handshake: --consumer value not recorded verbatim")
    if "not verified by cyanrip" not in log2:
        fail("handshake: --consumer value recorded without its disclaimer")


def sc_duration():
    # Duration: must agree with Samples:, which is an independently sourced
    # field in the same block -- not with the value it was computed from.
    #
    # setup_track_lsn() widens t->frames by one frame at whichever end the read
    # offset shifts into, so with a nonzero -s an interior track's t->frames is
    # one greater than the track is. Sourcing Duration: from it printed a frame
    # (13.3 ms) long, and the same block simultaneously reported
    # "Samples: 176400" (exactly 00:04.00) next to "Duration: 00:04.01".
    # Found on bovinemagnet/cyanrip 3eb6e22 and reproduced before fixing.
    #
    # -s 0 cannot catch it. Every offset below is exercised, and the run asserts
    # the offset actually reached the rip rather than trusting that it did.
    def dur(frames):
        return "%02i:%02i.%02i" % (frames // (75 * 60), (frames // 75) % 60,
                                   frames % 75)

    checked = 0
    for img in ("basic.cue", "pregap.cue"):
        # 667 is the rig drive's real offset and is large enough that the
        # shifted range reaches the disc boundary, which is where the error
        # inverts: the last track at +667 and the first at -667 are -1, not +1.
        # A repair that "adds a frame back" would pass every other case here.
        for off in ("0", "6", "588", "667", "-6", "-588", "-667"):
            name = f"dur_{img.split('.')[0]}_{off}"
            ec, log = crip("-d", WORK / img, "-N", "-A", "-U", "-s", off,
                           "-P", "0", "-o", "flac", "-D", WORK / f"out_{name}",
                           "-F", "{track}", "-L", "log")
            if ec != 0:
                fail(f"duration: {img} at -s {off} exited {ec}")
                continue

            text = (WORK / f"out_{name}" / "log.log").read_text()

            # The offset must have reached the rip, or every case below is the
            # -s 0 case wearing a different name and the check is vacuous.
            if f"Offset:         {'+' if not off.startswith('-') else ''}{off} samples" not in text:
                fail(f"duration: -s {off} not reflected in the log's Offset: line")

            pairs = re.findall(r"^    Duration:\s+(\S+)\n    Samples:\s+(\d+)$",
                               text, re.M)
            if len(pairs) < 2:
                fail(f"duration: {img} at -s {off} gave {len(pairs)} audio "
                     "tracks, need >= 2 for an interior boundary to exist")
            for got, samples in pairs:
                want = dur(int(samples) // 588)
                if got != want:
                    fail(f"duration: {img} at -s {off}: Duration {got} but "
                         f"Samples {samples} is {want}")
                checked += 1

    if checked < 28:
        fail(f"duration: only {checked} track blocks checked, expected >= 28")


def sc_reporting():
    # Per-track paranoia counters must account for the disc total exactly.
    # They are a delta of a process-global array, so an off-by-one in the
    # snapshot would show up here and nowhere else.
    rip("rep", "basic.cue")
    log = (WORK / "out_rep" / "log.log").read_text()

    disc, per_track, cur = {}, [], None
    for ln in log.splitlines():
        if ln == "Paranoia status counts:":
            cur = disc
            continue
        if ln == "  Paranoia status counts:":
            cur = {}
            per_track.append(cur)
            continue
        m = re.match(r"\s+([A-Z_]+):\s+(\d+)$", ln)
        if m and cur is not None:
            cur[m.group(1)] = int(m.group(2))
        elif not ln.strip():
            cur = None

    if not per_track:
        fail("reporting: no per-track paranoia block found")
    if not disc:
        fail("reporting: no disc-level paranoia block found")

    for key, total in disc.items():
        summed = sum(t.get(key, 0) for t in per_track)
        if summed != total:
            fail(f"reporting: {key} per-track sum {summed} != disc total {total}")

    # The Encoder: line must name the library that actually wrote the audio.
    # Assert against the FLAC vendor string rather than against itself, or the
    # check proves only that we can print a constant.
    # A label must not assert more than its value establishes. "Cache defeat"
    # named an action we explicitly do not perform -- we report a model and say
    # the drive was never probed -- so the field is "Cache model".
    if "Cache defeat" in log:
        fail("reporting: 'Cache defeat' label claims an outcome never established")
    if not re.search(r"^Cache model:\s+\S", log, re.M):
        fail("reporting: no Cache model: line")

    # "Peak level" did not say which peak, with a true peak reported below it.
    if re.search(r"^\s+Peak level:", log, re.M):
        fail("reporting: ambiguous 'Peak level' label (which peak?)")
    if not re.search(r"^\s+Sample peak level:\s+[\d.]+% \(-?[\d.]+ dBFS\)", log, re.M):
        fail("reporting: no Sample peak level: line")
    if not re.search(r"^\s+True peak level:\s+-?[\d.]+ dBFS", log, re.M):
        fail("reporting: no True peak level: line")

    # R128 loudness must be ours and must not collide with libavfilter's own
    # "Integrated loudness:" / "Loudness range:" headings.
    for pat, what in ((r"^\s+Integrated loudness \(R128\):\s+-?[\d.]+ LUFS", "integrated"),
                      (r"^\s+Loudness range \(R128\):\s+[\d.]+ LU \(-?[\d.]+ to -?[\d.]+ LUFS\)", "range")):
        if not re.search(pat, log, re.M):
            fail(f"reporting: no fork-owned R128 {what} line")
    if re.search(r"^\s{4}Integrated loudness:", log, re.M):
        fail("reporting: unqualified 'Integrated loudness:' collides with libavfilter's")

    m = re.search(r"^Encoder:\s+libavformat (\d+)\.(\d+)\.(\d+)", log, re.M)
    if not m:
        fail("reporting: no Encoder: line")
    elif FFPROBE:
        vendor = probe(WORK / "out_rep" / "1.flac", "-show_entries",
                       "format_tags=encoder")
        want = "Lavf" + ".".join(m.groups())
        if vendor != want:
            fail(f"reporting: Encoder: says {want!r}, FLAC vendor string says {vendor!r}")


def sc_paranoia():
    # Every other scenario passes -P 0 through rip(), so until this existed the
    # suite had never once run an image at the DEFAULT paranoia level -- and at
    # that level upstream's cachemodel override returned one correct sector
    # followed by silence, with "Ripping errors: 0". 99.7% of samples zeroed,
    # and nothing in the suite, the logs or the checksums said so.
    #
    # Asserts against the source image rather than against another rip: two
    # builds with the same defect agree with each other perfectly.
    for img, name in (("basic.cue", "basic"), ("cdda.nrg", "nrg")):
        ec, _ = crip("-d", WORK / img, "-N", "-A", "-U", "-s", "0", "-P", "0",
                     "-o", "pcm", "-D", WORK / f"par_{name}_off", "-F", "{track}")
        if ec != 0:
            fail(f"paranoia: {img} -P 0 exited {ec}")
            continue
        ec, _ = crip("-d", WORK / img, "-N", "-A", "-U", "-s", "0",
                     "-o", "pcm", "-D", WORK / f"par_{name}_on", "-F", "{track}")
        if ec != 0:
            fail(f"paranoia: {img} default exited {ec}")
            continue

        off = (WORK / f"par_{name}_off" / "1.pcm").read_bytes()
        on = (WORK / f"par_{name}_on" / "1.pcm").read_bytes()

        # Paranoia must not alter a deterministic image at all.
        if on != off:
            nz_on = sum(1 for b in on if b)
            fail(f"paranoia: {img} default-level audio differs from -P 0 "
                 f"({100.0 * nz_on / max(len(on), 1):.1f}% of bytes non-zero) -- "
                 "cachemodel too small for paranoia's overlap logic")

        # And the result must not be mostly silence, which is how the defect
        # presented. A check that only compared two rips would pass on two
        # equally-silent ones.
        if len(on) and (sum(1 for b in on if b) / len(on)) < 0.5:
            fail(f"paranoia: {img} default-level output is mostly silence")


def sc_early_log():
    # Everything cyanrip says before the logfile exists is replayed into it.
    # Without that, a diagnostic's fate depended on *when* it fired: the drive
    # open, the MusicBrainz lookup and the AccurateRip lookup all report before
    # cyanrip_log_init(), so a consumer that archives the log and not the
    # terminal lost them, and an aborted rip could read as a quiet success.
    rip("early", "basic.cue")
    log = (WORK / "out_early" / "log.log").read_text()
    lines = log.splitlines()

    # The banner is contractually the first line -- the only reliable answer to
    # "is this the fork?". The first version of the replay flushed at log-open
    # and pushed the banner to line 8. This is that regression, pinned.
    if not re.match(r"^cyanrip \S+ \(platterpus-fork-g", lines[0]):
        fail(f"early_log: first log line is not the version banner: {lines[0]!r}")

    for marker in ("--- output before this log was opened ---",
                   "--- end of pre-log output ---"):
        if marker not in log:
            fail(f"early_log: {marker!r} missing from the log")

    # Assert against an independent artifact: lines the binary prints before
    # the log opens, which are therefore in the log only via the replay. Each
    # is checked to have been printed at all first, so a probe that stops
    # firing fails loudly instead of passing by absence.
    stdout = (WORK / "early.log").read_text()
    for probe_line in ("Checking", "Opening drive..."):
        if probe_line not in stdout:
            fail(f"early_log: {probe_line!r} not printed at all -- probe is stale")
        elif probe_line not in log:
            fail(f"early_log: {probe_line!r} reached stdout but not the log")

    # A real diagnostic, not just progress chatter. Cover-art lookup reports
    # its own refusal before the log opens; -N makes it deterministic and
    # offline (no release ID to search with), so this exercises the case the
    # buffer exists for without depending on a network round trip.
    # (rip() always passes -U, so this one is spelled out without it.)
    _, out = crip("-d", WORK / "basic.cue", "-N", "-A", "-s", "0", "-P", "0",
                  "-o", "flac", "-D", WORK / "out_earlydiag", "-F", "{track}",
                  "-L", "log")
    diag = "No MusicBrainz release ID at cover art lookup, cannot search Cover Art DB!"
    if diag not in out:
        fail(f"early_log: {diag!r} not printed at all -- probe is stale")
    elif diag not in (WORK / "out_earlydiag" / "log.log").read_text():
        fail(f"early_log: {diag!r} reached stdout but not the log")

    # The block must sit inside the log, not be appended after the checksum --
    # --verify-log rejects trailing content, so a replay written at the end
    # would make every log from this build fail its own verification.
    if crip("--verify-log", WORK / "out_early" / "log.log")[0] != 0:
        fail("early_log: a log containing the replay block fails --verify-log")


def sc_cue_isrc():
    # Every ISRC handed in must come back out in the cue, on a disc WITH
    # pre-gaps. Both halves of that sentence are the test.
    #
    # Platterpus, round 7 lap 29: a rip on pin 9048082 carried 5 of its 14
    # ISRCs, and the missing nine were exactly the nine tracks that got an
    # INDEX 00. cyanrip_cue_track() has two shapes -- with an appended pre-gap
    # and without -- and only the second emitted ISRC. The first forked from
    # the second and did not inherit it.
    #
    # **The branch is upstream's**, verbatim in master since a0de6a0
    # ("Prevent writing duplicate cue file commands when pregap exists"). What
    # the fork changed is reachability: our sub-channel search finds pre-gaps
    # stock leaves as CDIO_INVALID_LSN, so stock never takes the branch on a
    # disc like this one and never loses an ISRC.
    #
    # WHY THIS FIXTURE: pregap.cue's track 2 takes the appended-pre-gap branch.
    # The same assertion on basic.cue passes with the defect present, which is
    # how it survived -- so this scenario is worthless on a gapless disc and
    # the fixture choice is the substance, not an implementation detail.
    codes = {1: "AAAAA0000001", 2: "BBBBB0000002", 3: "CCCCC0000003"}
    rip("isrc", "pregap.cue",
        *[a for n, c in codes.items() for a in ("-t", f"{n}=isrc={c}")])
    cue = (WORK / "out_isrc" / "sheet.cue").read_text()

    # The branch must actually be taken, or this proves nothing. A fixture that
    # stopped producing an appended pre-gap would make every check below pass
    # by never entering the code they are about.
    if "INDEX 00" not in cue:
        fail("cue_isrc: no INDEX 00 in the sheet -- the appended-pregap branch "
             "was not taken, so this scenario cannot discriminate")

    for n, code in codes.items():
        if f"ISRC {code}" not in cue:
            fail(f"cue_isrc: track {n}'s ISRC {code} is missing from the cue")

    # Position, not just presence: the CUE grammar puts ISRC in the TRACK block
    # before any INDEX line. An ISRC emitted after INDEX 00 would satisfy the
    # count above and still be malformed.
    for block in re.split(r"^  TRACK ", cue, flags=re.M)[1:]:
        i_isrc = block.find("ISRC ")
        i_index = block.find("INDEX ")
        if i_isrc >= 0 and i_index >= 0 and i_isrc > i_index:
            fail("cue_isrc: ISRC appears after an INDEX line in a TRACK block")


def sc_status_is_current():
    """Every doc in docs/handshake/ that names the current pin must name it.

    Two files claim it: STATUS.md's release table and README.md's pin block.
    They are checked together because it is ONE property -- a document that says
    what to build has to say what to build -- and splitting it would let one
    drift while the other passed.

    It is the one document here that claims things about *now* rather than about
    a moment, and it says so itself: rewritten in place, never appended to,
    because a stale standing status is worse than none. That property is a rule
    and a rule nothing executes is not a rule -- the whole reason it exists is
    that Platterpus reads it between rounds, when no lap is coming to correct it.

    Checked against `release-manifest.json` rather than against the ledger,
    because the manifest is what the consumer actually resolves. Three fields,
    all of which a reader would act on: the commit they clone, the version they
    expect the binary to print, and the build tag their capability table keys on.

    Deliberately NOT a check that the prose is up to date -- nothing can check
    that. It catches the one way this file rots that is mechanical, which is a
    release being cut and this file still naming the previous one.
    """
    status = ROOT / "docs" / "handshake" / "STATUS.md"
    manifest = ROOT / "release-manifest.json"
    if not status.exists():
        fail("status_is_current: docs/handshake/STATUS.md is missing")
        return
    if not manifest.exists():
        fail("status_is_current: release-manifest.json is missing")
        return

    text = status.read_text()
    stable = json.loads(manifest.read_text())["channels"]["stable"]

    # POSITIONAL, not a substring sweep of the file. The first version of this
    # check asked whether the SHA appeared ANYWHERE in the document, and its
    # revert-proof did not fail: the release commit is also in the install URL,
    # the build tag and a paragraph of prose, so corrupting the table cell left
    # the string present three times over. A check satisfied by the string
    # being somewhere is satisfied by the document being wrong.
    rows = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 4:
            key = cells[1].strip("* `")
            rows.setdefault(key, cells[2])

    for key, want in (
        ("commit", stable["commit"]),
        ("version", stable["version"]),
        ("build tag", f"platterpus-fork-g{stable['commit']}"),
        ("install", f"archive/{stable['commit']}.tar.gz"),
    ):
        cell = rows.get(key)
        if cell is None:
            fail(f"status_is_current: the release table has no {key!r} row. It "
                 f"is the table a consumer reads to find what to clone.")
        elif want not in cell:
            fail(f"status_is_current: the release table's {key!r} row says "
                 f"{cell!r}, but the manifest's stable channel says {want!r}. A "
                 f"release was cut and the standing status still describes "
                 f"another one.")

    # README.md's pin block. Found five releases stale -- it named d5d12ec and
    # +platterpus.3 while the manifest resolved to +platterpus.7, and its round
    # table still said "round 7 is open" through five closed rounds. A consumer
    # landing on the directory's index would have built a binary from July.
    #
    # A fenced block rather than a table, so this reads the lines inside the
    # fence positionally: `commit  <sha>`. Same rule as above -- the whole file
    # contains the right SHA in several places, and asking whether it is
    # "somewhere" is a check the wrong document passes.
    readme = ROOT / "docs" / "handshake" / "README.md"
    if not readme.exists():
        fail("status_is_current: docs/handshake/README.md is missing")
        return

    rtext = readme.read_text()
    block = re.search(r"^```\n(repo\s+.*?)^```", rtext, re.M | re.S)
    if not block:
        fail("status_is_current: README.md has no `repo ...` pin block. It is "
             "the first thing a consumer reads to find what to build.")
    else:
        fields = {}
        for line in block.group(1).splitlines():
            parts = line.split(None, 1)
            if len(parts) == 2:
                fields[parts[0]] = parts[1].split("<-")[0].strip()
        for key, want in (("commit", stable["commit"]),
                          ("--version", stable["version"]),
                          ("release_seq", str(stable["release_seq"]))):
            got = fields.get(key)
            if got is None:
                fail(f"status_is_current: README.md's pin block has no {key!r}")
            elif want not in got:
                fail(f"status_is_current: README.md's pin block says "
                     f"{key} = {got!r}, but the manifest's stable channel says "
                     f"{want!r}. The index a consumer lands on names a build "
                     f"that is not the release.")

    # And the round table must not advertise an open round while the gate says
    # every round is closed. That exact disagreement is what let "round 7 is
    # open" survive five closures.
    gate = subprocess.run([sys.executable, str(ROOT / "tools" / "release-gate.py")],
                          cwd=ROOT, stdout=subprocess.PIPE, timeout=60)
    gate_out = gate.stdout.decode(errors="replace")
    if "Release allowed" in gate_out and re.search(r"^\|.*\*\*open\*\*", rtext, re.M):
        fail("status_is_current: README.md's round table marks a round **open** "
             "while tools/release-gate.py reports every round closed. The gate "
             "is authoritative; the table is a copy that rotted.")


def sc_contract_exit_codes():
    """Every exit code the binary actually produces must be in P4.

    THE DEFECT THIS EXISTS FOR. P4's table was literal strings inside the
    generator -- one row read *"1, Every failure, without exception"* -- while
    the binary had just gained five distinct `--verify-log` codes, declared at
    column 0 as HANDSHAKE-BREAKING in the same round. The `Distinct exit values`
    line below the table WAS derived and found only `1`, so a generated document
    contradicted itself in one section and neither half matched the program.
    Platterpus found it by reading the delivered contract against our own lap
    (round 12 lap 2 §E1); nothing here noticed, because nothing here had ever
    compared the contract to a running binary.

    So this does the comparison the generator cannot: seam-rules S-9, limits are
    established by RUNNING the binary. The generator reads source and can only
    be as right as its parsing; this runs the real thing and asserts P4 is a
    superset of what came back.

    Superset, not equality, and the asymmetry is deliberate. A code P4 declares
    but no scenario here reaches is not a defect -- most failure paths need a
    drive. A code the binary returns and P4 omits is a consumer told the wrong
    thing, which is the only direction that hurts.
    """
    contract = ROOT / "PROVIDER-CONTRACT.md"
    if not contract.exists():
        fail("contract_exit_codes: PROVIDER-CONTRACT.md is missing")
        return

    text = contract.read_text()
    section = re.search(r"^## P4 .*?(?=^## P5 )", text, re.M | re.S)
    if not section:
        fail("contract_exit_codes: no P4 section")
        return
    declared = {int(m) for m in re.findall(r"^\| `(\d+)` \|", section.group(0),
                                           re.M)}
    if not declared:
        fail("contract_exit_codes: P4 declares no codes at all -- a check that "
             "can be satisfied by finding nothing is the failure it guards")
        return

    rip("basic", "basic.cue")
    log = WORK / "out_basic" / "log.log"
    body = log.read_text()

    tampered = WORK / "ec_tampered.log"
    tampered.write_text(body.replace("Ripping errors: 0", "Ripping errors: 1"))
    truncated = WORK / "ec_truncated.log"
    truncated.write_text(body[:body.index("Log FUN512:")])
    appended = WORK / "ec_appended.log"
    appended.write_text(body + "\n[addendum]\n")

    # One invocation per class we can reach without a drive. Named rather than
    # globbed, so adding a class is a visible act.
    probes = [
        ("valid log",       ["--verify-log", log]),
        ("mismatched log",  ["--verify-log", tampered]),
        ("footerless log",  ["--verify-log", truncated]),
        ("appended log",    ["--verify-log", appended]),
        ("unreadable log",  ["--verify-log", WORK / "ec_absent.log"]),
        ("refused argv",    ["--verify-log"]),
        ("version",         ["--version"]),
        ("help",            ["--help"]),
        ("-I and -J",       ["-d", WORK / "basic.cue", "-I", "-J", "-N", "-A",
                             "-U", "-s", "0"]),
    ]

    observed = {}
    for what, argv in probes:
        observed.setdefault(crip(*argv)[0], []).append(what)

    missing = sorted(set(observed) - declared)
    if missing:
        fail(f"contract_exit_codes: the binary returns "
             f"{ {c: observed[c] for c in missing} } and P4 does not declare "
             f"{missing}. P4 declares {sorted(declared)}. A generated contract "
             f"that omits a code the program returns tells a consumer the wrong "
             f"thing about a failure it will actually see.")

    # And the check must not be passable by a P4 that declares nothing useful:
    # if the probes above only ever produced one code, this scenario proves
    # nothing about discrimination and should say so rather than pass quietly.
    if len(observed) < 2:
        fail(f"contract_exit_codes: every probe returned {sorted(observed)} -- "
             f"this cannot discriminate, so its result means nothing")


def sc_contract_build():
    # The contract must describe THIS tree's version, not the previous one.
    #
    # This is the check for a defect that shipped in six of this fork's seven
    # version bumps -- 5bc654d is the only exception, because its contract had been
    # regenerated one commit earlier from a tree already carrying the new
    # string, so this check passes there.
    # `tools/gen-provider-contract.py` reads the *built binary*
    # and refuses on a dirty tree, so the contract can never be regenerated in
    # the same commit as a version bump -- the bump has to be committed before
    # a clean build exists to derive from. The consequence went unnoticed:
    #
    #     c5fb909  meson.build beta.2   contract says beta.1
    #     e61e75a  meson.build beta.3   contract says beta.2
    #     f5e11ba  meson.build beta.4   contract says beta.3
    #
    # Every beta note then published "PROVIDER-CONTRACT.md @ <release commit>",
    # so a consumer following those instructions checked out a tree whose
    # contract described the build before the one they had just compiled --
    # wrong anchor, wrong coverart string, six wrong `cyanrip_log.c` line
    # numbers. Found by an adversarial re-read, not by any check.
    #
    # The fix is procedural (pin the artifacts commit, not the release commit)
    # and procedure rots, so this is the thing that fails when it does. It is
    # pure text on purpose: no build, no network, no git, so it runs in a
    # tarball and on a dirty tree, which is exactly where --check cannot.
    version = re.search(r"^\s*version:\s*'([^']+)'", (ROOT / "meson.build").read_text(),
                        re.M)
    if not version:
        fail("contract_build: no version in meson.build")
        return

    contract = (ROOT / "PROVIDER-CONTRACT.md").read_text()
    build = re.search(r"^Build: `cyanrip (\S+)", contract, re.M)
    if not build:
        fail("contract_build: PROVIDER-CONTRACT.md has no `Build:` line -- "
             "the generator's output shape changed and this check is stale")
    elif build.group(1) != version.group(1):
        fail(f"contract_build: PROVIDER-CONTRACT.md describes "
             f"{build.group(1)!r} but this tree is {version.group(1)!r}. "
             "Rebuild from a clean tree and regenerate; do not publish this "
             "commit as a pin.")

    # And the CONTENT half, which the version check cannot reach: a contract
    # generated from a different tree describes different line numbers and can
    # be missing whole log lines while its version string is right.
    #
    # Round 8, Platterpus's 2026-08-14 hand-off §4/§5: the contract shipped with
    # round-8 lap 1 was the regeneration from one commit BEFORE the log change
    # the same lap announced, so it published a retired wording and omitted the
    # live one -- and its version string gave nothing away.
    #
    # Their diagnosis was that `--check` does not compare the Build banner.
    # Measured here rather than accepted: `--check` regenerates and diffs the
    # WHOLE file, banner included, and a doctored banner fails it. So the check
    # was not blind; it simply was not run again after the later commits, and
    # nothing tied the lap's claim about which build generated the file to the
    # file. This is that tie, and it is deliberately the pure-text kind: no
    # build, no network, so it runs in a tarball and on a dirty tree, which is
    # exactly where `--check` refuses to.
    #
    # Imports the generator's own hash rather than reimplementing it. Two
    # readers of one record that can disagree is the defect both gates exist to
    # prevent.
    spec = importlib.util.spec_from_file_location(
        "gpc", ROOT / "tools" / "gen-provider-contract.py")
    gpc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gpc)
    # Its SRC is relative and it documents "run from the repository root".
    # meson runs this from build/, where `src/` is the GENERATED header
    # directory -- a real directory with real files, so the hash came out
    # different rather than erroring, and the check failed for a reason that
    # had nothing to do with the contract. Point it at the tree explicitly.
    gpc.SRC = str(ROOT / "src")

    anchor = re.search(r"^\*\*Source anchor:\*\* `sha256/16 = ([0-9a-f]+)`",
                       contract, re.M)
    if not anchor:
        fail("contract_build: PROVIDER-CONTRACT.md has no source anchor -- "
             "every file:line in it is unverifiable")
    elif anchor.group(1) != gpc.source_hash():
        fail(f"contract_build: PROVIDER-CONTRACT.md's source anchor is "
             f"{anchor.group(1)} but src/ hashes to {gpc.source_hash()}. It "
             "was generated from a different tree, so its line numbers cite "
             "source that is not this source. Regenerate.")


def sc_format_guard():
    # Every cyanrip_log() format string is compiler-checked, and stays that way.
    #
    # It was not until now. -Wformat only inspects functions the compiler knows
    # are printf-like, and cyanrip_log() carried no such annotation, so not one
    # of this program's format strings had ever been checked -- in a program
    # whose output is an archival record. Adding av_printf_format() to the
    # declaration surfaced six live mismatches in the tree, none of which
    # changed a byte of output on x86-64 (measured: the golden reference is
    # unchanged), and all of which were the same shape as defects that had
    # already reached a logfile: a -t argument that printed adjacent process
    # memory into FLAC tags, the log and the cue, at exit 0.
    #
    # Two things have to hold, and they fail independently, so both are checked
    # here:
    #
    #   1. the annotation is present, so the compiler looks at all, and
    #   2. -Werror=format is set, so what it sees stops a build rather than
    #      scrolling past in a wall of ninja output.
    #
    # Removing either one puts the program back to unchecked while every test
    # in this suite still passes -- which is precisely why this is a test and
    # not a comment. The control compile is not decoration: without it, a probe
    # that fails because the include paths are wrong reads exactly like a probe
    # that fails because the guard worked.
    import shlex

    build_dir = Path(CRIP).resolve().parent.parent
    compdb = build_dir / "compile_commands.json"
    if not compdb.exists():
        skip(f"no {compdb} -- the guard is a property of the compile, and "
             "there is nothing here to reproduce the compile from")

    entry = next((e for e in json.loads(compdb.read_text())
                  if e.get("file", "").endswith("src/cyanrip_log.c")), None)
    if entry is None:
        skip("compile_commands.json has no entry for src/cyanrip_log.c")

    argv, drop_next = [], False
    for a in shlex.split(entry["command"])[1:]:
        if drop_next:
            drop_next = False
            continue
        if a in ("-o", "-MQ", "-MF"):
            drop_next = True
            continue
        if a in ("-MD", "-MMD") or a == entry["file"] or a.endswith(".c"):
            continue
        argv.append(a)
    cc = shlex.split(entry["command"])[0]

    def compiles(body, name):
        src = WORK / f"fmtprobe_{name}.c"
        src.write_text('#include "cyanrip_log.h"\n'
                       "void crip_format_probe(void);\n"
                       "void crip_format_probe(void)\n{\n"
                       f"    {body}\n}}\n")
        r = subprocess.run([cc, *argv, "-fsyntax-only", str(src)],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           cwd=entry["directory"], timeout=60)
        return r.returncode, r.stdout.decode(errors="replace")

    ec, out = compiles('cyanrip_log(NULL, 0, "%s\\n", "ok");', "control")
    if ec != 0:
        fail("format_guard: a CORRECT cyanrip_log() call does not compile with "
             f"the project's own flags, so this scenario cannot discriminate: {out.strip()!r}")
        return

    # Too few arguments: the class that reads whatever is next on the stack and
    # prints it into a file nobody can re-measure.
    ec, out = compiles('cyanrip_log(NULL, 0, "%s\\n");', "missing_arg")
    if ec == 0:
        fail("format_guard: a cyanrip_log() format string with more conversions "
             "than arguments compiled cleanly. Either av_printf_format() is "
             "missing from the declaration in src/cyanrip_log.h or "
             "-Werror=format is missing from src/meson.build; the program's "
             "format strings are unchecked again.")
    elif "format" not in out:
        fail(f"format_guard: the bad call failed to compile, but not for a "
             f"format reason -- the proof is not clean: {out.strip()!r}")

    # Wrong type: the class that prints a wrong number into the record.
    ec, out = compiles('cyanrip_log(NULL, 0, "%d\\n", "not an int");', "wrong_type")
    if ec == 0:
        fail("format_guard: a cyanrip_log() call passing char* to %d compiled "
             "cleanly -- type mismatches are unchecked.")


def sc_version_matrix():
    # P6 of the provider contract is the one section that is STATED, not
    # derived: it describes upstream builds, which the generator cannot
    # introspect. The sentence it replaced -- "prefer --version, it has never
    # changed and never will" -- was false, lived in a generated document, and
    # was quoted into a handshake lap as a recommendation before a build
    # disproved it.
    #
    # So the two upstream claims are re-checked here from git. This cannot
    # rebuild 0.9.3 on every run, but it can fail when the commits P6 cites
    # stop saying what P6 says they say, which is the drift that would make the
    # section quietly wrong again.
    contract = (ROOT / "PROVIDER-CONTRACT.md").read_text()
    if "## P6 - Version flags across the stock line" not in contract:
        fail("version_matrix: P6 is missing from the contract")
        return

    def git(*args):
        r = subprocess.run(["git", "-C", str(ROOT), *args],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           timeout=60)
        return r.returncode, r.stdout.decode(errors="replace")

    if git("rev-parse", "--git-dir")[0] != 0:
        # A source tarball has no history, so P6's upstream citations cannot be
        # resolved here at all. That is "the check could not run", not "the
        # check failed", and reporting it as a failure made a correct beta.8
        # tarball show a red suite on extraction -- a false alarm in exactly
        # the delivery path git-archive support was added to enable.
        # Still not silent: meson counts it under Skipped.
        skip("version_matrix: not a git checkout (source tarball?), so P6's "
             "upstream citations cannot be resolved. P6 is UNVERIFIED here -- "
             "run this from a clone to check it")

    # Claim 1: pre-genopt parses with getopt and has no long options at all.
    ec, pre = git("show", "442de2a^:src/cyanrip_main.c")
    if ec != 0:
        fail("version_matrix: 442de2a^ is unreachable; P6 cites it")
    else:
        if "getopt_long" in pre:
            fail("version_matrix: 442de2a^ uses getopt_long -- P6 says it has "
                 "no long options, so --version might be accepted after all")
        m = re.search(r'getopt\(argc, argv, "([^"]+)"', pre)
        if not m:
            fail("version_matrix: no getopt() optstring at 442de2a^ -- "
                 "P6's account of how it parses is stale")
        elif "V" not in m.group(1):
            fail(f"version_matrix: 442de2a^ optstring {m.group(1)!r} has no "
                 "'V' -- P6 says -V is its version flag")

    # Claim 2: genopt onward has no -V in the option table. Checked against
    # upstream master rather than our tree, because ours restores it.
    #
    # `master` is a local branch here and a remote-tracking ref in a fresh
    # clone: `git clone` creates a local branch only for the remote's HEAD,
    # which is platterpus-fork. So this failed for every consumer who cloned
    # the repository and passed for us, and both betas shipped a note claiming
    # 28/28 from a clean checkout on the strength of a tree that happened to
    # have the branch. Try each spelling and fail only when none resolves --
    # an absent ref is still a refusal, never a silent skip.
    for ref in ("master", "origin/master", "refs/remotes/origin/master"):
        ec, post = git("show", f"{ref}:src/cyanrip_main.c")
        if ec == 0:
            break
    if ec != 0:
        fail("version_matrix: upstream master is unreachable under any of "
             "master, origin/master, refs/remotes/origin/master; P6 cites it")
    elif re.search(r'GEN_OPT_\w+\([^)]*"V"', post):
        fail("version_matrix: upstream master has a -V option now -- P6 says "
             "genopt dropped it, and our -V alias is described as fork-only")

    # Claim 3, the fork's own row, which IS derivable: all three spellings work
    # here. sc_cli already asserts they agree; this asserts P6's row matches.
    for flag in ("--version", "-V", "-v"):
        if crip(flag)[0] != 0:
            fail(f"version_matrix: P6 says this fork accepts {flag}, and it "
                 "exits non-zero")


def sc_diagnostics():
    # The machine-readable record. What it is *for* is the runs that produce no
    # logfile at all -- a refusal writes nothing to disk, so a consumer that
    # archives artifacts rather than terminals cannot say why a rip did not
    # happen. Every check below is about that, not about the happy path.
    diag = WORK / "diag.json"

    # 1. Off by default. An unconditional extra file would break a consumer
    #    asserting the exact set of files a rip produces -- sc_cue_only is one.
    rip("nodiag", "basic.cue")
    stray = [p.name for p in (WORK / "out_nodiag").iterdir()
             if p.suffix == ".json"]
    if stray:
        fail(f"diagnostics: wrote {stray} without being asked")

    # 2. A normal rip: valid JSON, and the structured facts are the *measured*
    #    ones. Parsed with json.load, so a malformed file fails here rather
    #    than in the consumer.
    rip("diag", "basic.cue", "-j", diag)
    try:
        d = json.loads(diag.read_text())
    except Exception as e:
        fail(f"diagnostics: file is not valid JSON: {e}")
        return

    if d.get("schema") != "cyanrip-diagnostics/3":
        fail(f"diagnostics: schema is {d.get('schema')!r}")
    if d.get("exit_code") != 0:
        fail(f"diagnostics: exit_code {d.get('exit_code')!r} for a clean rip")
    if d.get("rip", {}).get("tracks_completed") != 2:
        fail(f"diagnostics: tracks_completed {d.get('rip', {}).get('tracks_completed')!r}")

    # A rip that finished says so twice, and the two are separate facts: the
    # bool says no signal arrived, and interrupted_by is null rather than
    # absent. `is not None` and `not in d` would read the same for a consumer
    # using .get(), which is how an absence of an interruption becomes
    # indistinguishable from a field nobody wrote.
    if d.get("rip", {}).get("interrupted") is not False:
        fail("diagnostics: interrupted must be false for a completed rip")
    if "interrupted_by" not in d.get("rip", {}):
        fail("diagnostics: interrupted_by must be present, null, not absent")
    elif d["rip"]["interrupted_by"] is not None:
        fail(f"diagnostics: interrupted_by is "
             f"{d['rip']['interrupted_by']!r} for a completed rip")

    # The other side of the audio_ripped discriminator, checked here so it
    # cannot be satisfied by a build that reports false for everything. A rip
    # that finished must report every track ripped, WITH its checksum.
    states = d.get("rip", {}).get("track_state") or []
    if len(states) != 2:
        fail(f"diagnostics: {len(states)} track_state entries for a 2-track disc")
    for st in states:
        if not st or st.get("audio_ripped") is not True:
            fail(f"diagnostics: {st!r} did not report audio_ripped on a rip "
                 f"that completed")
        elif st.get("eac_crc") is None:
            fail(f"diagnostics: track {st.get('number')!r} finished but "
                 f"publishes no checksum")

    # No severity is claimed anywhere, and the file says so rather than leaving
    # a consumer to read the absence of the field as "nothing here was
    # serious". Classifying by wording is the defect the provider contract's
    # fatal inventory already shipped once.
    if d.get("messages_are_classified") is not False:
        fail("diagnostics: messages_are_classified must be present and false")

    # Progress is collapsed by modelling the terminal, not by matching text.
    # Without that, one rip is thousands of near-identical lines; the check is
    # that a bounded rip stays bounded and the *last* state of the line lives.
    msgs = d.get("messages", [])
    if len(msgs) > 400:
        fail(f"diagnostics: {len(msgs)} messages for a 2-track rip -- "
             "progress rewrites are not being collapsed")
    if not any("Rip completed:  yes" in m for m in msgs):
        fail("diagnostics: the rip's own completion line is missing")
    if any(m.startswith("\r") or "\r" in m for m in msgs):
        fail("diagnostics: a message still contains a carriage return")

    # 3. The point of the feature. A refusal that opens no logfile must still
    #    leave a record, with the reason in it.
    #
    #    -J with -I is used because it is decided from the argument table
    #    alone: no disc, no network. The first version of this check used the
    #    no-metadata refusal, which reaches that state via a MusicBrainz
    #    lookup -- so what it asserted depended on whether the lookup failed by
    #    not-found or by timeout, and it failed once in a way that did not
    #    reproduce. A check whose result depends on the network is not
    #    evidence about this program.
    refusal = WORK / "refusal.json"
    ec, out = crip("-J", "-I", "-D", WORK / "out_refusal", "-j", refusal)
    if ec == 0:
        fail("diagnostics: -J with -I stopped refusing -- probe is stale")
    if (WORK / "out_refusal").exists():
        logs = list((WORK / "out_refusal").glob("*.log"))
        if logs:
            fail(f"diagnostics: refusal wrote a logfile {logs} -- probe is stale, "
                 "this case is meant to have no log at all")
    if not refusal.exists():
        fail("diagnostics: no record written for a run that wrote no log")
    else:
        r = json.loads(refusal.read_text())
        if r.get("exit_code") != 1:
            fail(f"diagnostics: refusal recorded exit_code {r.get('exit_code')!r}")
        if not any("cannot be used with -I" in m for m in r.get("messages", [])):
            fail(f"diagnostics: the refusal's reason is not in the record: "
                 f"{r.get('messages')}")

    # 4. An error raised *inside libcdio* must reach the record. Left alone,
    #    libcdio prints to stderr and exits the process itself, so cyanrip
    #    never sees the only message explaining the failure.
    cdio = WORK / "cdio.json"
    ec, out = crip("-d", WORK / "no-such-image.cue", "-N", "-o", "flac",
                   "-j", cdio)
    if ec == 0:
        fail("diagnostics: opening a nonexistent CUE succeeded -- probe is stale")
    if not cdio.exists():
        fail("diagnostics: no record written for a libcdio-terminated run")
    else:
        c = json.loads(cdio.read_text())
        if not any("libcdio" in m for m in c.get("messages", [])):
            fail(f"diagnostics: libcdio's own message is not in the record: "
                 f"{c.get('messages')}")
        # rip is null, not absent: "no disc was ever opened" and "a disc with
        # no tracks" are different claims.
        if "rip" not in c or c["rip"] is not None:
            fail(f"diagnostics: rip should be null when no disc was opened, "
                 f"got {c.get('rip')!r}")

    # 5. An argument-parsing failure happens before the option table is read,
    #    so -j has to be found by a pre-pass or these runs stay unrecorded.
    #    This is the exact shape of the -V incident: a parse error that read to
    #    a consumer as "cyanrip is not installed".
    argf = WORK / "argfail.json"
    ec, out = crip("--not-a-real-flag", "-j", argf)
    if ec == 0:
        fail("diagnostics: an unknown flag was accepted -- probe is stale")
    if not argf.exists():
        fail("diagnostics: no record written for an argument-parsing failure")
    else:
        a = json.loads(argf.read_text())
        if a.get("exit_code") != 1:
            fail(f"diagnostics: argfail recorded exit_code {a.get('exit_code')!r}")
        if not any("Unable to parse command line argument" in m
                   for m in a.get("messages", [])):
            fail(f"diagnostics: genopt's own error is not in the record: "
                 f"{a.get('messages')}")


def sc_golden_reference_is_from_a_clean_build():
    # The shipped reference must name a build someone else can reproduce. A
    # -dirty banner means it was generated from a tree with uncommitted
    # changes, so its SHA does not describe the binary that wrote it -- which
    # is exactly what A9's marker was added to expose, and it caught a
    # reference committed that way rather than a hypothetical one.
    ref = ROOT / "docs" / "golden-reference.log"
    if not ref.exists():
        fail("golden reference is missing")
        return
    first = ref.read_text().splitlines()[0]
    if "-dirty" in first:
        fail(f"golden reference was generated from a dirty tree: {first!r}")
    if not re.match(r"^cyanrip \S+ \(platterpus-fork-g[0-9a-f]{7,}\)$", first):
        fail(f"golden reference banner is not the expected shape: {first!r}")

    # ...and it must describe THIS tree's version, exactly as contract_build
    # requires of PROVIDER-CONTRACT.md. That check existed for the contract and
    # not for the reference, so beta.8 shipped a reference generated at beta.7
    # and nothing complained -- the same "generated artifact lags its
    # generator" shape Platterpus filed against us in round 7 lap 31 §H, which
    # we fixed for the contract and left open here. A consumer diffing against
    # this file cannot see our test output; the banner is all they have.
    ref_ver = re.match(r"^cyanrip (\S+) ", first)
    tree_ver = re.search(r"^\s*version:\s*'([^']+)'",
                         (ROOT / "meson.build").read_text(), re.M)
    if not tree_ver:
        fail("golden reference: no version in meson.build")
    elif ref_ver and ref_ver.group(1) != tree_ver.group(1):
        fail(f"golden reference describes {ref_ver.group(1)!r} but this tree "
             f"is {tree_ver.group(1)!r}. Regenerate it from a clean build and "
             "name that build in a lap; do not publish this commit as a pin.")

    # The companion diagnostics record ships beside it and must describe the
    # SAME run. Two reference artifacts that drifted apart would be worse than
    # one: a consumer would reconcile them and one of the two would be wrong,
    # with nothing saying which.
    dj = ROOT / "docs" / "golden-reference.diagnostics.json"
    if not dj.exists():
        fail("golden diagnostics record is missing")
        return
    try:
        d = json.loads(dj.read_text())
    except Exception as e:
        fail(f"golden diagnostics record is not valid JSON: {e}")
        return

    # The build that PRODUCED the reference must be named somewhere a reader
    # can find it, not only the commit it was committed at.
    #
    # Those are always different commits and always will be: the fix builds the
    # binary, a later commit checks in the regenerated artifact, and a file can
    # never name a build that contains itself. Laps 12 and 14 each named the
    # reference by its commit-at -- 70dcf19, f00cb2b -- while the banners said
    # ceca8bc and 486dce3, and lap 14 stated outright that the number it gave
    # was "the build of the artifact this lap is about". It was not. Platterpus
    # caught it as the third instance of one shape: a build tag names a commit,
    # it does not name what was built.
    #
    # No git here: asserting the pairing is recorded is what makes it
    # checkable in a tarball too, and it is the practice, not the ancestry,
    # that went wrong.
    banner_sha = re.search(r"platterpus-fork-g([0-9a-f]{7,})", first)
    if not banner_sha:
        fail(f"golden reference banner has no build tag: {first!r}")
    else:
        sha = banner_sha.group(1)
        # Laps OR the changelog. The rule is that the pairing is written down
        # somewhere a reader can find it; the original check hardcoded laps as
        # the only such place, which quietly assumed every regeneration happens
        # inside a round.
        #
        # A RELEASE regeneration does not. The reference is regenerated at the
        # version bump, which by CLAUDE.md's own ordering happens AFTER the
        # round that authorised the release has closed -- and the closing lap
        # is pinned as sent, so it cannot be edited to name a build that did
        # not exist when it was written. Found by hitting it: the
        # +platterpus.6 release regenerated at bde52d2 and no lap could ever
        # name it.
        #
        # Changelog.md is the right second home rather than a loophole -- it is
        # where a release's provenance belongs, it is durable, and it is what a
        # consumer reads. The property is unchanged: the generating build must
        # be named, and "generated by X, committed at Y" must both appear.
        homes = list((ROOT / "docs" / "handshake").glob("round-*.md"))
        homes.append(ROOT / "Changelog.md")
        named = any(p.exists() and sha in p.read_text() for p in homes)
        if not named:
            fail(f"nothing names {sha}, the build that produced the golden "
                 "reference -- name both it and the commit the reference is "
                 "committed at, in a handshake lap or in Changelog.md")

    want_vcs = re.search(r"platterpus-fork-g(\S+)\)$", first)
    if want_vcs and d.get("cyanrip", {}).get("vcs") != want_vcs.group(1):
        fail(f"golden pair disagree on the build: log says "
             f"{want_vcs.group(1)!r}, diagnostics says "
             f"{d.get('cyanrip', {}).get('vcs')!r}")

    # The fields a consumer will key on. Listed by name so that removing one
    # fails here rather than in Platterpus.
    for key in ("schema", "cyanrip", "invocation", "exit_code", "read_stalls",
                "rip", "messages", "messages_are_classified",
                "messages_dropped"):
        if key not in d:
            fail(f"golden diagnostics record has no {key!r} field")
    if d.get("messages_dropped"):
        fail(f"golden diagnostics record dropped {d['messages_dropped']} "
             "message(s) -- it is not a complete reference")


def sc_reference():
    sc_golden_reference_is_from_a_clean_build()
    # The golden reference sent to a consumer guards only the paths it
    # exercises, and coverage is lost by dropping a *flag*, not by changing a
    # fixture. Round 5's reference silently lost the secure-re-read surface and
    # every over-full-scale peak because -Z and -G were omitted -- the fixture
    # audio had a true peak above 0 dBFS the whole time.
    rip("ref", "pregap.cue", "-Z", "2", "-G")
    log = (WORK / "out_ref" / "log.log").read_text()

    for pat, what in ((r"^Repeating ripping \(\d+ out of \d+", "-Z repeat line"),
                      (r"^Done; \(\d+ out of \d+", "-Z convergence line"),
                      (r"EAC CRC32:\s+[0-9A-F]{8} \(after \d+ rips\)", "rip-count suffix"),
                      (r"^\s+Secure re-read:\s+converged after \d+ reads", "secure verdict")):
        if not re.search(pat, log, re.M):
            fail(f"reference: {what} missing -- -Z coverage lost")

    # An intersample peak above full scale must survive into the tags, or the
    # consumer's >1.0 reconciliation path is never exercised.
    peaks = [float(m) for m in
             re.findall(r"REPLAYGAIN_TRACK_PEAK:\s+([\d.]+)", log)]
    if not peaks:
        fail("reference: no REPLAYGAIN_TRACK_PEAK -- -G coverage lost")
    elif max(peaks) <= 1.0:
        fail(f"reference: no over-full-scale peak (max {max(peaks)}) -- "
             "true peak above 0 dBFS is not exercised")


def sc_verify_log():
    # CLI wiring only, the checksum logic itself is unit-tested.
    #
    # Every case below asserts the EXACT exit code, not `!= 0`. Platterpus
    # ask 2 (standing status 2026-08-21): "the ripper was killed mid-write" and
    # "this file was modified" are different findings and only the second is a
    # tamper claim, and until this change both exited 1. A test written as
    # `!= 0` passes just as well with all five collapsed back onto one code,
    # which is exactly the state being fixed -- so the numbers are named here
    # and this is where they become contract.
    rip("basic", "basic.cue")
    log = WORK / "out_basic" / "log.log"
    body = log.read_text()

    tampered = WORK / "tampered.log"
    tampered.write_text(body.replace("Ripping errors: 0", "Ripping errors: 1"))

    # Trailing content must not verify either. Platterpus asked whether it
    # could append an addendum after the checksum line; it cannot, and this
    # locks that answer so it cannot silently become "yes".
    appended = WORK / "appended.log"
    appended.write_text(body + "\n[addendum]\ntrailing content\n")

    # The case ask 2 is actually about, and the one this program manufactures:
    # a log with NO footer, which is what a rip killed mid-write leaves. Built
    # by truncating a real log at its checksum line rather than by writing a
    # fake one, so what is checked is a genuine cyanrip log missing exactly the
    # footer -- a hand-written file could differ in some other way and pass for
    # the wrong reason.
    truncated = WORK / "truncated.log"
    truncated.write_text(body[:body.index("Log FUN512:")])

    cases = [
        ("valid",         log,                        0),
        ("mismatch",      tampered,                   2),
        ("no checksum",   truncated,                  3),
        ("trailing data", appended,                   4),
        ("I/O error",     WORK / "no_such_file.log",  5),
    ]

    observed = {}
    for what, path, want in cases:
        ec, out = crip("--verify-log", path)
        observed[what] = ec
        if ec != want:
            fail(f"verify_log: {what} exited {ec}, expected {want} "
                 f"({out.strip()!r})")

    # The point of the change is that the verdicts DIFFER, and this is asserted
    # over what the binary actually returned rather than over the list of
    # numbers written above -- a set built from the expectations can only ever
    # agree with itself, which is a check satisfied by the thing it is checking.
    if len(set(observed.values())) != len(observed):
        fail(f"verify_log: verdicts share an exit code: {observed}")

    # And 1 stays reserved for "no verdict was reached": it is what cyanrip
    # exits with for a rejected command line, so a verdict taking it would make
    # a modified log indistinguishable from an argv cyanrip refused. Checked
    # against a real refusal, so it is a statement about this binary.
    if crip("--verify-log")[0] != 1:
        fail("verify_log: a --verify-log with no argument no longer exits 1, "
             "so the reserved 'no verdict' code has moved")
    if 1 in observed.values():
        fail(f"verify_log: a verdict took exit code 1: {observed}")

    # docs/sample-interrupted.log carries a header explaining what it is, and
    # that header makes two checkable claims about --verify-log: that the file
    # as shipped does NOT verify, and that stripping the header makes the same
    # bytes verify. Both are asserted here, because a claim written into an
    # archival artifact and checked by nobody is the shape this project keeps
    # finding wrong. Same pattern as the rig-log addendum check below: reject
    # the shipped file, and prove the header is the reason.
    sample = ROOT / "docs" / "sample-interrupted.log"
    end = "=== END OF HEADER -- THE LOG ITSELF STARTS ON THE NEXT LINE ===\n"
    if not sample.exists():
        fail("verify_log: the interrupted sample is missing")
    else:
        text = sample.read_text()
        if crip("--verify-log", sample)[0] == 0:
            fail("verify_log: the interrupted sample verified WITH its header "
                 "attached, which its own header says it does not")
        if end not in text:
            fail("verify_log: the interrupted sample has no header marker, so "
                 "the instruction it ships for recovering the log is wrong")
        else:
            stripped = WORK / "sample_stripped.log"
            stripped.write_text(text.split(end, 1)[1])
            ec, out = crip("--verify-log", stripped)
            if ec != 0:
                fail(f"verify_log: the interrupted sample does not verify even "
                     f"with its header removed ({out.strip()!r}) -- the header "
                     f"is then not the reason, and its instructions are wrong")

    # The same rule, against a real artifact rather than one we constructed.
    #
    # The 2026-08-04 rig log came back with a consumer's auto-fix addendum
    # appended after the checksum line, so it no longer verifies -- and the
    # consumer's own integrity check reported the rip fine, because it verified
    # a different file's checksum. Both halves are pinned here: that the shipped
    # file is rejected, and that removing exactly the appended block makes the
    # same bytes verify. The second half is what makes this a finding about the
    # addendum rather than about the log.
    rig = ROOT / "docs" / "rig-2026-08-04" / "cyanrip.log"
    if not rig.exists():
        fail("rig log evidence is missing")
    else:
        text = rig.read_text()
        if crip("--verify-log", rig)[0] == 0:
            fail("rig log verified -- it carries an addendum after the "
                 "checksum and must not, or finding H1 has silently reverted")

        head, sep, _ = text.partition("\n=====")
        if not sep:
            fail("rig log no longer contains the appended block -- the "
                 "archived evidence was modified")
        else:
            clean = WORK / "rig_stripped.log"
            clean.write_text(head + "\n")
            ec, out = crip("--verify-log", clean)
            if ec != 0:
                fail(f"rig log does not verify even with the addendum removed: "
                     f"{out.strip()!r} -- the addendum is then not the cause, "
                     "and this test's premise is wrong")


def sc_interrupt():
    """A rip stopped by a signal still leaves a complete, checksummed record.

    Platterpus standing status 2026-08-21, ask 1, and it was a real defect
    found by them running a flag for the first time. Before this only SIGINT
    was handled, so a supervising process's kill took the default disposition
    and cyanrip died where it stood: the logfile was cut off mid-sentence with
    no `Log FUN512:` footer, and the -j record -- which is written from atexit
    and therefore never ran -- was not written at all. -j exists for runs that
    open no logfile, so that lost it exactly where it was most needed, and the
    footerless log is the case Platterpus then has to tell apart from a
    tampered one.

    THREE things are asserted per signal and they fail independently:

      * the exit is graceful and the log carries a VALID checksum footer,
        checked by running --verify-log over it rather than by grepping for
        the marker. A footer that is present and wrong would pass a grep.
      * the log NAMES THE SIGNAL. This is what makes the test discriminate:
        handling only SIGINT (the state before the fix) leaves the SIGTERM
        case failing, and printing a fixed string for both -- the old
        "interrupted by user" -- fails on whichever signal is not that one.
      * the diagnostics record agrees with the log, independently. Two
        surfaces reporting one fact must not be able to drift.

    The rip is made long with -Z rather than with a big fixture, so the
    scenario costs nothing when the signal lands and cannot silently become a
    full rip if the signal is lost: it is killed and reported instead.
    """
    for signo, name in ((signal.SIGINT, "SIGINT"),
                        (signal.SIGTERM, "SIGTERM")):
        out = WORK / f"out_int_{name}"
        diag = WORK / f"int_{name}.json"
        stdout = WORK / f"int_{name}.out"

        with stdout.open("wb") as fh:
            p = subprocess.Popen(
                [CRIP, "-d", WORK / "basic.cue", "-N", "-A", "-U", "-s", "0",
                 "-P", "0", "-o", "flac", "-D", out, "-F", "{track}",
                 "-L", "log", "-M", "sheet", "-Z", "200", "-r", "200",
                 "-j", diag],
                stdout=fh, stderr=subprocess.STDOUT)

        # Signal only once the rip is demonstrably under way. Signalling on a
        # fixed sleep races the handler's installation, and a signal that
        # arrives before the handler is a DEFAULT-DISPOSITION kill that would
        # then be reported as this fix failing.
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if b"Ripping track" in stdout.read_bytes():
                break
            if p.poll() is not None:
                break
            time.sleep(0.05)
        else:
            p.kill(), p.wait()
            fail(f"interrupt/{name}: rip never started")
            continue

        p.send_signal(signo)
        try:
            ec = p.wait(timeout=60)
        except subprocess.TimeoutExpired:
            p.kill(), p.wait()
            fail(f"interrupt/{name}: still running 60s after the signal")
            continue

        if ec != 1:
            fail(f"interrupt/{name}: exited {ec}, expected 1")

        log = out / "log.log"
        if not log.exists():
            fail(f"interrupt/{name}: no logfile was written")
            continue

        vec, vout = crip("--verify-log", log)
        if vec != 0:
            fail(f"interrupt/{name}: the log it left does not verify "
                 f"({vout.strip()!r}) -- an interrupted rip must still close "
                 f"its record")

        want = f"Rip completed:  no (interrupted by {name},"
        if want not in log.read_text():
            got = [ln for ln in log.read_text().splitlines()
                   if ln.startswith("Rip completed:")]
            fail(f"interrupt/{name}: log says {got!r}, expected {want!r}")

        # WHICH track, from the log alone. Platterpus carried this across two
        # rounds: the -j record has always answered it and the log has not, so
        # a consumer holding only the log knew a rip stopped after N tracks and
        # not which track the drive was on.
        #
        # This signals once `Ripping track` has appeared, so the read is always
        # in flight and the mid-read arm is the one produced. The other arm --
        # `between tracks, no read in progress` -- needs the signal to land in
        # the writeout window, which nothing here can schedule. It is in the
        # contract, it is UNEXERCISED, and that is said out loud rather than
        # left for a green suite to imply.
        #
        # The track number is cross-checked against the -j record below rather
        # than hardcoded: two surfaces reporting one fact must not be able to
        # drift, and pinning "track 1" here would pass even if the two
        # disagreed.
        at = re.search(r"^Interrupted at: track (\d+), mid-read$",
                       log.read_text(), re.M)
        if not at:
            got = [ln for ln in log.read_text().splitlines()
                   if ln.startswith("Interrupted at:")]
            fail(f"interrupt/{name}: no mid-read `Interrupted at:` line "
                 f"(found {got!r}). The log names how many tracks finished "
                 f"and must also name the one that did not")

        if not diag.exists():
            fail(f"interrupt/{name}: no diagnostics record -- it is written "
                 f"from atexit, so this means the process did not unwind")
            continue

        d = json.loads(diag.read_text())
        rip_d = d.get("rip") or {}
        if rip_d.get("interrupted") is not True:
            fail(f"interrupt/{name}: diagnostics interrupted is "
                 f"{rip_d.get('interrupted')!r}")
        if rip_d.get("interrupted_by") != name:
            fail(f"interrupt/{name}: diagnostics interrupted_by is "
                 f"{rip_d.get('interrupted_by')!r}")

        # NO CHECKSUM MAY BE PUBLISHED FOR A TRACK THAT DID NOT FINISH.
        #
        # The track that was in progress has had crip_finalize_checksums() run
        # over its partial read, so eac_crc holds a real number describing
        # audio that is not on disk. Emitting it is a confident wrong field in
        # an archival record, which is worse than a missing one -- and null,
        # not 00000000, because a zero checksum is a value somebody compares
        # against.
        states = rip_d.get("track_state") or []
        if not states:
            fail(f"interrupt/{name}: no per-track state in the record")

        # The log's `Interrupted at:` and the record's per-track state are two
        # surfaces describing one fact. The track the log names must be the
        # first one the record says did not finish.
        if at and states:
            unfinished = [st.get("number") for st in states
                          if st and st.get("audio_ripped") is False]
            if unfinished and int(at.group(1)) != unfinished[0]:
                fail(f"interrupt/{name}: the log says the rip stopped in "
                     f"track {at.group(1)} and the -j record's first "
                     f"unfinished track is {unfinished[0]}. Two surfaces, one "
                     f"fact, and they disagree")
        for st in states:
            if st is None:
                continue
            if st.get("audio_ripped") is not False:
                continue_ = st.get("audio_ripped")
                fail(f"interrupt/{name}: track {st.get('number')!r} reports "
                     f"audio_ripped={continue_!r}, but no track can have "
                     f"finished -- the rip was stopped during the first one")
            if st.get("eac_crc") is not None:
                fail(f"interrupt/{name}: track {st.get('number')!r} publishes "
                     f"eac_crc {st['eac_crc']!r} for audio that was never "
                     f"written")
            if st.get("crcs_computed") is not False:
                fail(f"interrupt/{name}: track {st.get('number')!r} claims "
                     f"crcs_computed for an unfinished track")

        # The per-track flags and the disc counter must agree. They are set
        # together today; this is what notices if they ever stop being.
        ripped = sum(1 for st in states if st and st.get("audio_ripped"))
        if ripped != rip_d.get("tracks_completed"):
            fail(f"interrupt/{name}: {ripped} tracks report audio_ripped but "
                 f"the disc says tracks_completed="
                 f"{rip_d.get('tracks_completed')!r}")


def sc_artifacts_are_tracked():
    """Every artifact this suite reads must be IN the repository.

    Third time is a rule. `.gitignore` starts with `*.log`, and docs/ is full of
    files that are artifacts rather than build output, so three of them have now
    been silently excluded: the golden reference, the rig-session logs, and the
    interrupted sample. Each was fixed by adding a negation, which only ever
    helps the file somebody remembered.

    The failure mode is what makes this worth a test rather than a comment. An
    ignored file is still THERE in the working tree, so every check that reads
    it passes locally and forever -- the rig-log case shipped exactly that way,
    with a green suite over a file no clone contained. Nothing fails until
    somebody clones, at which point the tests that read it fail for a reason
    that looks nothing like "the file was never committed".

    So the assertion is against git's index, not the filesystem: presence on
    disk is precisely the evidence that misleads. Untracked and ignored are
    both failures and are reported separately, because "we forgot to add it"
    and ".gitignore ate it" need different fixes.
    """
    if not (ROOT / ".git").exists():
        skip("artifacts_are_tracked: not a git checkout (source tarball)")

    # Named, not globbed. A glob over docs/ would pass by finding nothing if the
    # directory moved, and this is a check that must not be satisfiable by
    # finding nothing.
    artifacts = [
        "docs/golden-reference.log",
        "docs/golden-reference.diagnostics.json",
        "docs/sample-interrupted.log",
        "docs/sample-interrupted.diagnostics.json",
        "PROVIDER-CONTRACT.md",
        "release-manifest.json",
        "docs/release-ledger.tsv",
    ]

    tracked = subprocess.run(["git", "ls-files", "-z", "--", *artifacts],
                             cwd=ROOT, stdout=subprocess.PIPE, timeout=60)
    have = set(tracked.stdout.decode().split("\0")) - {""}

    for a in artifacts:
        if a in have:
            continue
        if not (ROOT / a).exists():
            fail(f"artifacts_are_tracked: {a} is neither tracked nor present")
            continue
        ign = subprocess.run(["git", "check-ignore", "-q", "--", a],
                             cwd=ROOT, timeout=60)
        if ign.returncode == 0:
            fail(f"artifacts_are_tracked: {a} exists but .gitignore excludes "
                 f"it, so a clone will not have it and every check that reads "
                 f"it passes here for a reason no clone shares")
        else:
            fail(f"artifacts_are_tracked: {a} exists but was never git-added")


def sc_interrupt_deadlock():
    """A signal arriving while the log lock is held must not wedge the process.

    THE DEFECT THIS PINS. on_quit_signal() called cyanrip_log(), which takes
    log_lock and uses stdio -- neither of which a signal handler may do. When
    the signal landed while the main thread was inside cyanrip_vlog() holding
    that same non-recursive mutex, the handler blocked on it forever, on the
    thread that would have released it. The process then sat there with the
    drive held and only SIGKILL left, which produces exactly the truncated
    footerless log the rest of this round exists to stop producing. Found by
    running sc_interrupt() in a loop until it hung and reading the backtrace;
    it is almost certainly what Platterpus saw on 2026-08-19 as "the child
    could not be reaped (exit: null), so the drive stayed held".

    WHY THIS IS A SEPARATE SCENARIO FROM sc_interrupt(). sc_interrupt() hits
    the window by luck -- the race is one frame wide, and it reproduced roughly
    once in forty runs on an idle machine. A test that catches a defect one
    time in forty is not a regression test. This one CONSTRUCTS the state:
    cyanrip's stdout is a pipe nobody drains, so the main thread parks inside
    write(2) with log_lock held and stays there. The signal then always lands
    in the window.

    AND WHY THE PIPE IS DRAINED AFTERWARDS. Blocking in write(2) is not the
    defect -- the reader can always release it -- so the drain separates the
    two: with the fix the process wakes and shuts down, and with the defect it
    is still stuck on the mutex, which draining cannot touch. Without the drain
    both versions would hang and the test would prove nothing.

    Linux-only, and skipped rather than silently weakened elsewhere: the
    premise assertion needs F_GETPIPE_SZ and FIONREAD to establish that the
    pipe really is full before the signal is sent. A version of this that just
    slept would pass on a build where the writer was never blocked at all.
    """
    if not sys.platform.startswith("linux"):
        skip("interrupt_deadlock: needs Linux pipe introspection to assert "
             "the writer is actually blocked before signalling")

    import fcntl
    import struct
    import termios
    import threading

    F_GETPIPE_SZ = 1032

    rfd, wfd = os.pipe()
    out = WORK / "out_deadlock"
    p = subprocess.Popen(
        [CRIP, "-d", str(WORK / "basic.cue"), "-N", "-A", "-U", "-s", "0",
         "-P", "0", "-o", "flac", "-D", str(out), "-F", "{track}",
         "-L", "log", "-M", "sheet", "-Z", "200", "-r", "200"],
        stdout=wfd, stderr=subprocess.STDOUT)
    os.close(wfd)

    try:
        capacity = fcntl.fcntl(rfd, F_GETPIPE_SZ)

        def buffered():
            return struct.unpack(
                "i", fcntl.ioctl(rfd, termios.FIONREAD, b"\0\0\0\0"))[0]

        # The premise is "the writer is parked in write(2)", and the signal it
        # gives is that the buffered count STOPS GROWING while the process is
        # still alive. Waiting for buffered == capacity does not work and the
        # difference is the point: a blocked writer is one whose next chunk did
        # not fit, so the pipe stops a chunk short of full and stays there.
        # Measured at 65386 of 65536 the first time this was written.
        #
        # Both halves are required. Near-full alone could be a writer that is
        # merely slow; steady alone could be a writer that has not started.
        deadline = time.monotonic() + 30
        last, steady_since, level = -1, None, 0
        while time.monotonic() < deadline:
            level = buffered()
            if level != last:
                last, steady_since = level, time.monotonic()
            elif (level > capacity - 8192 and
                  time.monotonic() - steady_since > 1.0):
                break
            if p.poll() is not None:
                break
            time.sleep(0.02)

        if p.poll() is not None or level <= capacity - 8192:
            p.kill(), p.wait()
            fail(f"interrupt_deadlock: the writer never blocked on the pipe "
                 f"({level} of {capacity} bytes buffered, exit {p.poll()}) -- "
                 f"this check cannot discriminate and its result means nothing "
                 f"either way")
            return

        p.send_signal(signal.SIGINT)

        # Only now let it write again. A fixed binary unblocks and shuts down;
        # one deadlocked on the mutex does not, because nothing is holding the
        # pipe against it any more.
        drained = bytearray()

        def drain():
            while True:
                chunk = os.read(rfd, 65536)
                if not chunk:
                    break
                drained.extend(chunk)

        t = threading.Thread(target=drain, daemon=True)
        t.start()

        try:
            ec = p.wait(timeout=30)
        except subprocess.TimeoutExpired:
            p.kill(), p.wait()
            fail("interrupt_deadlock: still running 30s after the signal with "
                 "its output being drained -- the quit handler is blocked on "
                 "something the reader cannot release, which is the log-lock "
                 "self-deadlock")
            return
        finally:
            t.join(timeout=5)

        if ec != 1:
            fail(f"interrupt_deadlock: exited {ec}, expected 1")

        log = out / "log.log"
        if not log.exists():
            fail("interrupt_deadlock: no logfile -- it did not unwind")
        elif crip("--verify-log", log)[0] != 0:
            fail("interrupt_deadlock: the log it left does not verify")
    finally:
        os.close(rfd)


def sc_cache_probe_only():
    """-x is a modifier; -x -I is the probe-only invocation, and both are pinned.

    Platterpus standing status 2026-08-21, ask 1: they read `--cache-probe` as
    a command, ran it on the rig, and got a full rip with a 1h03m ETA. The flag
    was behaving as documented -- "measure the drive's readback cache BEFORE
    ripping" -- so the defect was that nothing told a caller how to measure
    WITHOUT ripping, which -I already does and which is the same idiom -I and
    -J use elsewhere.

    Three assertions, and the first two are the ones that would catch a future
    change to -x's meaning before a consumer does:

      * -x -I writes no audio. This is the probe-only guarantee.
      * -x alone DOES rip. If someone later makes -x exit after measuring --
        which is what was asked for, and which we declined with reasons -- this
        fails and forces the question back through a round instead of letting a
        documented flag change meaning quietly.
      * --help says how. A remedy that is only in a commit message is not a
        remedy; this makes the sentence a thing that runs.

    WHAT THIS DOES NOT COVER, said plainly: the probe itself never executes
    here. cache_probe.c refuses on image drivers, which have no cache to
    measure, so what is exercised is the DISPATCH around it -- whether -x
    proceeds into a rip -- and not a single cdio_read_audio_sectors() call.
    -x has still never run to completion on real hardware anywhere.
    """
    out = WORK / "out_xprobe"
    ec, log = crip("-d", WORK / "basic.cue", "-N", "-A", "-U", "-s", "0",
                   "-P", "0", "-o", "flac", "-D", out, "-F", "{track}",
                   "-L", "log", "-M", "sheet", "-x", "-I")
    if ec != 0:
        fail(f"cache_probe_only: -x -I exited {ec}")
    if out.exists() and any(p.suffix == ".flac" for p in out.iterdir()):
        fail("cache_probe_only: -x -I ripped audio -- the probe-only "
             "invocation is gone, and a caller measuring a drive now waits "
             "for a whole disc")
    if "Cache probe:" not in log:
        fail("cache_probe_only: -x -I reported no cache probe result at all")

    # The modifier half. Separate output directory so a leftover from the
    # check above cannot satisfy this one.
    out2 = WORK / "out_xrip"
    ec, _ = crip("-d", WORK / "basic.cue", "-N", "-A", "-U", "-s", "0",
                 "-P", "0", "-o", "flac", "-D", out2, "-F", "{track}",
                 "-L", "log", "-M", "sheet", "-x")
    if ec != 0:
        fail(f"cache_probe_only: -x exited {ec}")
    if not (out2.exists() and any(p.suffix == ".flac" for p in out2.iterdir())):
        fail("cache_probe_only: -x alone did not rip. That may be an "
             "improvement, but it is a change to a documented flag and it "
             "belongs in a handshake round, not in a passing test")

    # Measured from the binary, not read from the option table (seam-rules
    # S-9). The substring is deliberately just the actionable half: pinning
    # the whole sentence would make every rewording a test failure.
    helptext = crip("--help")[1]
    if "measure without ripping" not in helptext:
        fail("cache_probe_only: --help no longer says how to measure without "
             "ripping, so the only fix for ask 1 has been undone")


def sc_sanitize():
    """P7's substitution tables, asserted against the running binary.

    WHY THIS SHAPE. The generator reads source and can only be as right as its
    parsing; nothing in it runs cyanrip. So this does the comparison the
    generator cannot -- it parses the committed contract's P7c table and rips
    with each -T mode, asserting the document predicts the filename that
    actually appears on disk. Seam rule S-9: limits are established by running
    the binary. It is also the only kind of check that can catch the generator
    misreading the table, because a wrong derivation and a wrong hand-written
    claim look identical in the document.

    WHAT IT COST TO NOT HAVE THIS. Platterpus's overwrite guard predicted a rip
    directory by rendering our naming template through their own two-entry copy
    of our substitution table. It got one character wrong, probed a directory
    that did not exist, found no audio, asked nothing, and a completed 14-track
    archival rip was overwritten by a 2-track one (round 13 [ASK A]). Neither
    contract described the substitutions; P1 documented only that the flag
    existed.

    WHICH COLUMN. P7c reports both compile-time branches, because availability
    is a property of the build and this suite runs on one platform. The column
    is chosen from os.name and stated out loud rather than inferred from the
    behaviour under test -- picking the column by measuring the thing the column
    is supposed to predict would make the assertion circular.

    QUOTES ARE HELD BACK from the per-character pass on purpose. They have two
    table rows and a parity rule, so folding them in would test the parity and
    the table at once and tell you nothing about which failed. They get their
    own block below.
    """
    contract = ROOT / "PROVIDER-CONTRACT.md"
    if not contract.exists():
        fail("sanitize: PROVIDER-CONTRACT.md is missing")
        return
    text = contract.read_text()

    section = re.search(r"^### P7c .*?(?=^### P7d )", text, re.M | re.S)
    if not section:
        fail("sanitize: no P7c section in the contract -- round 13's blocking "
             "ask was to publish this table, and it is not there")
        return

    def unwrap(cell):
        cell = cell.strip().rstrip("†").strip()
        if cell == "unchanged":
            return None
        m = re.fullmatch(r"`(.*)`", cell)
        if not m:
            return "UNPARSED:" + cell
        # GFM tables escape a literal pipe as \| even inside a code span; it is
        # the one escape the table parser honours, so it is the one to undo.
        return m.group(1).replace("\\|", "|")

    rows = {}
    for line in section.group(0).splitlines():
        if not line.startswith("| `"):
            continue
        # Split on unescaped pipes only. `\|` is a cell's content, not a
        # boundary -- splitting on it drops the `|` row entirely, and a row
        # missing from a completeness check is the failure this test is for.
        cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))
        if len(cells) != 7:
            fail(f"sanitize: P7c row has {len(cells)} cells, expected 7: "
                 f"{line}")
            continue
        ch = unwrap(cells[0])
        rows.setdefault(ch, []).append([unwrap(c) for c in cells[1:]])
    if not rows:
        fail("sanitize: P7c declares no rows at all -- a check satisfiable by "
             "finding nothing is the failure it guards")
        return

    win = os.name == "nt"
    col = {"simple": 0, "unicode": 1,
           "os_simple": 4 if win else 2, "os_unicode": 5 if win else 3}
    print(f"sanitize: asserting the "
          f"{'HAVE_WMAIN' if win else 'non-HAVE_WMAIN'} columns of P7c "
          f"(os.name={os.name!r})")

    # `/` is excluded: P7c footnotes it because its result depends on the call
    # site rather than the mode, and it is asserted separately below.
    # `"` is excluded: two rows, parity rule, own block below.
    chars = [c for c in rows if c not in ('/', '"') and len(rows[c]) == 1]
    if len(chars) < 4:
        fail(f"sanitize: only {len(chars)} single-row characters to test "
             f"({chars}) -- too few to discriminate")
        return

    subject = "A".join([""] + chars + [""])          # A<A>A:A|A?A*A\A
    # -a parses key=value:key=value and treats \ as an escape, so a literal
    # colon and a literal backslash have to be escaped to reach the tag at all.
    encoded = subject.replace("\\", "\\\\").replace(":", "\\:")

    for mode in ("simple", "unicode", "os_simple", "os_unicode"):
        want = "".join((rows[c][0][col[mode]] or c) if c in rows else c
                       for c in subject)
        if "UNPARSED:" in want:
            fail(f"sanitize: P7c has a cell this test cannot read for {mode}: "
                 f"{want}")
            continue
        out = WORK / f"out_san_{mode}"
        ec, _ = crip("-d", WORK / "basic.cue", "-N", "-A", "-U", "-s", "0",
                     "-P", "0", "-l", "1", "-o", "flac", "-D", out,
                     "-F", "{album}", "-L", "log", "-M", "sheet",
                     "-T", mode, "-a", f"album={encoded}")
        if ec != 0:
            fail(f"sanitize: -T {mode} exited {ec}")
            continue
        have = [p.name for p in out.iterdir() if p.suffix == ".flac"]
        if have != [want + ".flac"]:
            fail(f"sanitize: -T {mode} on {subject!r} produced {have}, and "
                 f"P7c predicts {[want + '.flac']}. The contract and the "
                 f"binary disagree about a filename, which is the exact "
                 f"failure round 13 [ASK A] was raised for")

    # The default. Parsed from P7a's own marker rather than hardcoded here:
    # two places naming the default is two places that can disagree.
    m = re.search(r"^\| `(\w+)` \*\(default\)\*", text, re.M)
    if not m:
        fail("sanitize: P7a marks no mode as the default")
    else:
        declared = m.group(1)
        out = WORK / "out_san_default"
        ec, _ = crip("-d", WORK / "basic.cue", "-N", "-A", "-U", "-s", "0",
                     "-P", "0", "-l", "1", "-o", "flac", "-D", out,
                     "-F", "{album}", "-L", "log", "-M", "sheet",
                     "-a", f"album={encoded}")
        if ec != 0:
            fail(f"sanitize: the default-mode rip exited {ec}")
        else:
            have = [p.name for p in out.iterdir() if p.suffix == ".flac"]
            same = [p.name for p in (WORK / f"out_san_{declared}").iterdir()
                    if p.suffix == ".flac"]
            if have != same:
                fail(f"sanitize: with no -T the binary produced {have}, but "
                     f"P7a declares the default is `{declared}`, which "
                     f"produced {same}")

    # --- quotes: two rows, and a parity that other characters advance -------
    #
    # Measured, then written down -- not the reverse. Each case pins one thing:
    #   1. plain alternation, nothing in between
    #   2. ONE other substituted character in between flips the closing glyph,
    #      because the parity advances on every table match and not on quotes
    #   3. TWO put it back
    #   4. a {tag} boundary resets it, so identical rendered text gives two
    #      different filenames depending on where the scheme's braces fall
    #
    # 4 is the one a consumer cannot possibly guess, and the one that makes
    # "reconstruct the path from the metadata" wrong rather than merely fragile.
    qrows = rows.get('"')
    if not qrows or len(qrows) != 2:
        fail(f"sanitize: P7c has {len(qrows or [])} rows for `\"`, expected 2 "
             f"-- the parity below is meaningless without both glyphs")
        return
    open_q = qrows[0][col["unicode"]]
    close_q = qrows[1][col["unicode"]]
    lt = rows['<'][0][col["unicode"]] if '<' in rows else None
    star = rows['*'][0][col["unicode"]] if '*' in rows else None
    if not (open_q and close_q and lt and star):
        fail("sanitize: P7c's unicode column is missing a glyph the parity "
             "cases need")
        return

    for what, scheme, meta, want in (
            ("plain alternation", 'q"a"z', None,
             f"q{open_q}a{close_q}z"),
            ("one intervening substitution", 'q"a<b"z', None,
             f"q{open_q}a{lt}b{open_q}z"),
            ("two intervening substitutions", 'q"a<b*c"z', None,
             f"q{open_q}a{lt}b{star}c{close_q}z"),
            ("a {tag} boundary resets the parity", 'x"a{album}"z', "MID",
             f"x{open_q}aMID{open_q}z"),
            ("the same text with no boundary", 'x"aMID"z', None,
             f"x{open_q}aMID{close_q}z")):
        out = WORK / ("out_q" + str(abs(hash(what)) % 10**8))
        extra = ["-a", f"album={meta}"] if meta else []
        ec, _ = crip("-d", WORK / "basic.cue", "-N", "-A", "-U", "-s", "0",
                     "-P", "0", "-l", "1", "-o", "flac", "-D", out,
                     "-F", scheme, "-L", "log", "-M", "sheet",
                     "-T", "unicode", *extra)
        if ec != 0:
            fail(f"sanitize/quotes ({what}): exited {ec}")
            continue
        have = [p.name for p in out.iterdir() if p.suffix == ".flac"]
        if have != [want + ".flac"]:
            fail(f"sanitize/quotes ({what}): scheme {scheme!r} produced "
                 f"{have}, expected {[want + '.flac']}")

    # And the two cases must actually differ, or the pair proves nothing.
    if f"x{open_q}aMID{open_q}z" == f"x{open_q}aMID{close_q}z":
        fail("sanitize/quotes: the two boundary cases predict the same name, "
             "so they cannot discriminate")

    # --- `/`: a separator or a character, decided by the call site ----------
    slash = rows.get('/')
    if not slash:
        fail("sanitize: P7c has no `/` row")
        return
    # In a tag value it is substituted, in all four modes.
    for mode in ("simple", "unicode", "os_simple", "os_unicode"):
        want = slash[0][col[mode]]
        if want is None:
            fail(f"sanitize: P7c says `/` is unchanged under {mode}; the "
                 f"footnote says it is the one row that is never unchanged")
            continue
        out = WORK / f"out_slash_{mode}"
        ec, _ = crip("-d", WORK / "basic.cue", "-N", "-A", "-U", "-s", "0",
                     "-P", "0", "-l", "1", "-o", "flac", "-D", out,
                     "-F", "{album}", "-L", "log", "-M", "sheet",
                     "-T", mode, "-a", "album=a/b")
        if ec != 0:
            fail(f"sanitize/slash: -T {mode} exited {ec}")
            continue
        have = [p.name for p in out.iterdir() if p.suffix == ".flac"]
        if have != [f"a{want}b.flac"]:
            fail(f"sanitize/slash: -T {mode} on a tag value 'a/b' produced "
                 f"{have}, and P7c predicts {[f'a{want}b.flac']}")

    # In the scheme itself it is a directory separator, in every mode.
    for mode in ("simple", "unicode", "os_simple", "os_unicode"):
        out = WORK / f"out_sep_{mode}"
        ec, _ = crip("-d", WORK / "basic.cue", "-N", "-A", "-U", "-s", "0",
                     "-P", "0", "-l", "1", "-o", "flac", "-D", out,
                     "-F", "sub/trk", "-L", "log", "-M", "sheet", "-T", mode)
        if ec != 0:
            fail(f"sanitize/separator: -T {mode} exited {ec}")
            continue
        if not (out / "sub" / "trk.flac").exists():
            fail(f"sanitize/separator: -T {mode} did not treat `/` in the "
                 f"naming scheme as a directory separator; P7d says it is one "
                 f"in all four modes. Found "
                 f"{sorted(str(p.relative_to(out)) for p in out.rglob('*'))}")

def sc_enhanced_cd():
    """A trailing data track must not be able to publish a garbage disc ID.

    THE DEFECT. cyanrip treats a data track in LAST position as a CD-Extra
    second session and takes CDEXTRA_SESSION_GAP frames off the preceding audio
    track, because libcdio reports the inter-session link area as part of it.
    The subtraction was unguarded. On a TOC where the gap does not fit, the LSN
    went negative, discid.c left-shifted a negative int -- undefined behaviour,
    and UBSan says so at discid.c:87 -- and the run published

        toc=1+2+4294956496+150+375        CDDB ID: FFFF6E02

    at exit 0, with no diagnostic whatsoever in a default build. Nothing else
    in the output looked wrong: 3 tracks, the right total time. That is a
    confident wrong field in an archival record, which is the single outcome
    this program exists not to produce.

    Found while answering a NEXT-ROUND question from Platterpus about
    two-session (Enhanced CD) TOCs -- they asked because a mishandled session
    gap shifts every sector number and silently breaks the disc ID, and
    therefore AccurateRip and CTDB, across a whole class of discs. They were
    right that it was worth asking; the answer turned out to be worse than
    "we handle it".

    BOTH SHAPES ARE COVERED, and the second one only because the first write-up
    of this was wrong. ecd.cue is the disc whose gap does NOT fit, committed,
    and it pins the refusal. The well-formed disc needs 11400 sectors of audio
    ahead of the data track -- 29.6 MB -- which this file twice called
    impossible, and gen_fixtures.py called impossible before that. Both were
    reasoning about what can be COMMITTED. A fixture does not have to be: the
    big one is built in the temp workdir at test time and costs the repository
    nothing, which is a `for` loop rather than a hardware session.

    WHAT NEITHER SHAPE SETTLES: whether 11400 is the RIGHT number to remove
    from a physical Enhanced CD. These are images, and on an image the data
    track starts immediately after the audio, so the gap is carved out of real
    audio bytes. What libcdio reports for track 2's last LSN on a pressed
    CD-Extra disc is not knowable from here, and the constant is inherited from
    upstream unverified. That question needs a disc and is round 13 §J.

    The strongest assertion below is not "the numbers look sane", which garbage
    can satisfy. It is that the leadout in the MusicBrainz TOC equals the last
    audio track's own End LSN plus 151, both read out of the same run -- an
    invariant between two fields of one artifact, which is what a negative LSN
    breaks and what a plausible-looking wrong number cannot satisfy.
    """
    rip("ecd", "ecd.cue")
    out = (WORK / "ecd.log").read_text()
    log = (WORK / "out_ecd" / "log.log").read_text()

    if "runtime error" in out:
        fail(f"enhanced_cd: the sanitizer fired: "
             f"{[l for l in out.splitlines() if 'runtime error' in l]}")

    if "CD-Extra session gap does not fit" not in out:
        fail("enhanced_cd: no diagnostic about the session gap. Either the "
             "guard is gone -- in which case the numbers below are garbage -- "
             "or it was reworded, which is contract surface and belongs in a "
             "round")

    # Every End LSN in the log, in track order.
    ends = [int(m) for m in re.findall(r"^    End LSN:     (-?\d+)", log, re.M)]
    if len(ends) != 3:
        fail(f"enhanced_cd: found {len(ends)} End LSN lines, expected 3")
        return
    if any(e < 0 for e in ends):
        fail(f"enhanced_cd: a negative End LSN reached the log: {ends}. "
             f"The session-gap guard is not holding")

    starts = [int(m) for m in re.findall(r"^    Start LSN:   (-?\d+)", log, re.M)]
    if len(starts) != 3:
        fail(f"enhanced_cd: found {len(starts)} Start LSN lines, expected 3")
        return

    # The last AUDIO track is track 2 here; track 3 is the data track and is
    # excluded from the disc ID by design. Read that from the log rather than
    # assuming it, so the assertion still means something if the fixture grows.
    if "Track 3 is data:" not in log:
        fail("enhanced_cd: track 3 was not identified as data")
    last_audio_end = ends[1]

    # The TOC string is printed by the lookup path, not by a rip, so it takes
    # its own -I run. Same fixture, same numbers; asserting it separately is
    # what pins the leadout itself rather than only the length field derived
    # from it.
    _, info = crip("-d", WORK / "ecd.cue", "-I", "-N", "-A", "-U", "-P", "0")
    if "runtime error" in info:
        fail(f"enhanced_cd: the sanitizer fired during -I: "
             f"{[l for l in info.splitlines() if 'runtime error' in l]}")
    m = re.search(r"toc=(\d+)\+(\d+)\+(\d+)((?:\+\d+)*)", info)
    if not m:
        fail("enhanced_cd: no MusicBrainz TOC string in the -I output")
        return
    leadout = int(m.group(3))
    if leadout != last_audio_end + 151:
        fail(f"enhanced_cd: the TOC leadout is {leadout} but the last audio "
             f"track's End LSN is {last_audio_end}, so it should be "
             f"{last_audio_end + 151}. These are two fields of one artifact "
             f"and they disagree")
    if int(m.group(2)) != 2:
        fail(f"enhanced_cd: the TOC's last track is {m.group(2)}, expected 2 "
             f"-- the data track must not appear in the disc ID")

    # And the CDDB ID's middle 16 bits are the disc length in seconds, which is
    # the field that read 0xFF6E when the LSN went negative.
    c = re.search(r"^CDDB ID:\s+([0-9A-F]{8})$", log, re.M)
    if not c:
        fail("enhanced_cd: no CDDB ID line in the log")
        return
    want = leadout // 75 - (starts[0] + 150) // 75
    have = (int(c.group(1), 16) >> 8) & 0xFFFF
    if have != want:
        fail(f"enhanced_cd: CDDB ID {c.group(1)} carries a length field of "
             f"{have}, and the TOC says {want}")

    expect("ecd", "1.flac", "2.flac", "log.log", "sheet.cue")

    # --- and the case where the gap DOES fit -------------------------------
    #
    # This was written off twice as needing hardware: gen_fixtures.py's header
    # said a trailing data track "cannot fit in a bundled-size fixture", and
    # ecd.cue's own header said the well-formed path "needs a real disc". Both
    # were reasoning about what can be COMMITTED, and the fixture does not have
    # to be committed -- 29.6 MB of BIN is unreasonable in a repository and
    # entirely reasonable in a temp directory that exists for the length of one
    # test. CLAUDE.md's rule is to check whether a different image can reach it
    # before accepting that nothing can; the answer here was a `for` loop.
    #
    # Track 2 spans 150..11999, which is 11850 frames, so CDEXTRA_SESSION_GAP
    # fits with room: 11999 - 11400 = 599, still past the track's own start.
    # The read is therefore 150..599 -- 450 frames -- so the fixture is large
    # and the rip is not.
    big = WORK / "ecdbig.bin"
    with big.open("wb") as fh:
        chunk = (FIX / "cdda.bin").read_bytes()
        for _ in range(21):                 # 21 * 600 = 12600 sectors
            fh.write(chunk)
    (WORK / "ecdbig.cue").write_text(
        'FILE "ecdbig.bin" BINARY\n'
        "  TRACK 01 AUDIO\n"
        "    INDEX 01 00:00:00\n"
        "  TRACK 02 AUDIO\n"
        "    INDEX 01 00:02:00\n"
        "  TRACK 03 MODE1/2352\n"
        "    INDEX 01 02:40:00\n")

    rip("ecdbig", "ecdbig.cue")
    bigout = (WORK / "ecdbig.log").read_text()
    biglog = (WORK / "out_ecdbig" / "log.log").read_text()

    if "runtime error" in bigout:
        fail(f"enhanced_cd/wellformed: the sanitizer fired: "
             f"{[l for l in bigout.splitlines() if 'runtime error' in l]}")
    if "CD-Extra session gap does not fit" in bigout:
        fail("enhanced_cd/wellformed: the guard refused a gap that fits. "
             "Track 2 is 11850 frames against an 11400 frame gap, so this is "
             "the guard being wrong, not the disc")

    # THE POINT OF THIS HALF. The old wording called an 11400-frame session
    # adjustment a read offset -- a field that is normally worth one frame --
    # so a consumer reading `End LSN: 11999 (with offset: 599)` would attribute
    # 11400 frames to `-s`. Both clauses of the replacement are asserted.
    m = re.search(r"^    End LSN:     (\d+) "
                  r"\(less (\d+) frame CD-Extra session gap, read to: (-?\d+)\)$",
                  biglog, re.M)
    if not m:
        ends = re.findall(r"^    End LSN:.*$", biglog, re.M)
        fail(f"enhanced_cd/wellformed: no session-gap End LSN line. Found "
             f"{ends}. If one of those says `(with offset:` then the two "
             f"causes have been collapsed back into one label")
    else:
        sig, gap, read_to = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if sig - gap != read_to:
            fail(f"enhanced_cd/wellformed: the line says {sig} less {gap} "
                 f"frames reads to {read_to}, and {sig} - {gap} is "
                 f"{sig - gap}. The three numbers on one line disagree")
        # No -s is passed by rip(), so the gap is the whole delta here. Stated
        # as an assertion rather than assumed: if rip() ever grows an offset,
        # this fires instead of silently checking something weaker.
        if gap != 11400:
            fail(f"enhanced_cd/wellformed: the gap is reported as {gap} frames "
                 f"and CDEXTRA_SESSION_GAP is 11400")

    # An offset-only line must still read exactly as it always has, on a disc
    # with no trailing data track. This is the half that must NOT have moved.
    rip("ecdoff", "basic.cue", "-s", "10")
    offlog = (WORK / "out_ecdoff" / "log.log").read_text()
    if not re.search(r"^    End LSN:     \d+ \(with offset: -?\d+\)$", offlog,
                     re.M):
        fail("enhanced_cd/wellformed: the offset-only End LSN wording changed. "
             "It was left byte-identical on purpose -- Platterpus parses it, "
             "and this change was supposed to ADD a shape, not reword one")
    if "CD-Extra session gap" in offlog:
        fail("enhanced_cd/wellformed: a disc with no data track reported a "
             "CD-Extra session gap")

with tempfile.TemporaryDirectory() as tmpdir:
    WORK = Path(tmpdir)

    # libcdio pairs .cue and .bin files by basename, so stage a copy per sheet
    for f in FIX.glob("*.cue"):
        shutil.copy(f, WORK)
    shutil.copy(FIX / "cdda.nrg", WORK)
    shutil.copy(FIX / "cdtext.toc", WORK)
    shutil.copy(FIX / "cdda.bin", WORK / "cdtext.bin")
    for name in ("basic", "pregap", "preemph", "ecd"):
        shutil.copy(FIX / "cdda.bin", WORK / f"{name}.bin")
    shutil.copy(FIX / "mixed.bin", WORK / "mixed.bin")

    globals()[f"sc_{SCENARIO}"]()

if fails:
    print(f"{fails} check(s) failed")
    sys.exit(1)
print(SCENARIO, "passed")
