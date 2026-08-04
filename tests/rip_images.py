#!/usr/bin/env python3
# Rips the disc image fixtures and verifies the finished files.
# Usage: rip_images.py <cyanrip-binary> <fixtures-dir> <scenario>

import hashlib
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


def crip(*args, cwd=None):
    r = subprocess.run([CRIP, *map(str, args)], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=60, cwd=cwd)
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


def sc_reference():
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
