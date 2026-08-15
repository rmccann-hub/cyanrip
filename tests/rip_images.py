#!/usr/bin/env python3
# Rips the disc image fixtures and verifies the finished files.
# Usage: rip_images.py <cyanrip-binary> <fixtures-dir> <scenario>

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
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
        if not open_round and "NOT a released build" in state:
            fail(f"handshake: round is closed but the log claims otherwise: {state!r}")

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

    if d.get("schema") != "cyanrip-diagnostics/1":
        fail(f"diagnostics: schema is {d.get('schema')!r}")
    if d.get("exit_code") != 0:
        fail(f"diagnostics: exit_code {d.get('exit_code')!r} for a clean rip")
    if d.get("rip", {}).get("tracks_completed") != 2:
        fail(f"diagnostics: tracks_completed {d.get('rip', {}).get('tracks_completed')!r}")

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
        laps = ROOT / "docs" / "handshake"
        named = any(sha in p.read_text() for p in laps.glob("round-*.md"))
        if not named:
            fail(f"no handshake lap names {sha}, the build that produced the "
                 "golden reference -- name both it and the commit the "
                 "reference is committed at")

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
    # CLI wiring only, the checksum logic itself is unit-tested
    rip("basic", "basic.cue")
    log = WORK / "out_basic" / "log.log"
    if crip("--verify-log", log)[0] != 0:
        fail("valid log did not verify")

    tampered = WORK / "tampered.log"
    tampered.write_text(log.read_text().replace("Ripping errors: 0",
                                                "Ripping errors: 1"))
    if crip("--verify-log", tampered)[0] == 0:
        fail("tampered log verified")

    # Trailing content must not verify either. Platterpus asked whether it
    # could append an addendum after the checksum line; it cannot, and this
    # locks that answer so it cannot silently become "yes".
    appended = WORK / "appended.log"
    appended.write_text(log.read_text() + "\n[addendum]\ntrailing content\n")
    if crip("--verify-log", appended)[0] == 0:
        fail("log with trailing content verified")

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


with tempfile.TemporaryDirectory() as tmpdir:
    WORK = Path(tmpdir)

    # libcdio pairs .cue and .bin files by basename, so stage a copy per sheet
    for f in FIX.glob("*.cue"):
        shutil.copy(f, WORK)
    shutil.copy(FIX / "cdda.nrg", WORK)
    shutil.copy(FIX / "cdtext.toc", WORK)
    shutil.copy(FIX / "cdda.bin", WORK / "cdtext.bin")
    for name in ("basic", "pregap", "preemph"):
        shutil.copy(FIX / "cdda.bin", WORK / f"{name}.bin")
    shutil.copy(FIX / "mixed.bin", WORK / "mixed.bin")

    globals()[f"sc_{SCENARIO}"]()

if fails:
    print(f"{fails} check(s) failed")
    sys.exit(1)
print(SCENARIO, "passed")
