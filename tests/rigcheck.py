#!/usr/bin/env python3
"""Regression tests for the two rig tools, `tools/rig-check.py` and
`tools/audio-checksums.py`.

Both are things we hand to the operator and ask them to run on hardware we
cannot reach, and both have now reported a reassuring status over a check that
had not actually happened. That failure mode is invisible on a green suite --
the check passes, because passing is what it does when it finds nothing -- so
these assertions exist to make each one fail out loud instead.

Every case here is a defect that occurred, named by the round that found it.

Round 9, 2026-08-11, from re-reading the rig transcript against the source:

  * `cdparanoia-cache` reported *"it did not fail, it declined to answer"* on a
    run where cd-paranoia had printed `Approximate random access cache size:
    137 sector(s)`. `re.M` anchors `^` after `\\n` and not after `\\r`, and
    cd-paranoia separates progress output with `\\r`.
  * `audio-vs-log` graded a file it could not decode as *"differ -- expected
    for any track a re-rip superseded"*, because `audio-checksums.py check`
    exited 1 both for "different audio" and for "no comparison was possible".
  * `audio-vs-log` could return OK saying *"0 track(s) checked; every one
    matches its log"* when no filename carried a leading track number.

Run standalone or under meson; it needs ffmpeg only for the exit-code cases and
skips them, loudly, if it is absent.
"""

import importlib.util
import os
import shutil
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(os.path.dirname(HERE), "tools")

failures = []


def check(name, cond, detail=""):
    print(f"  {'ok  ' if cond else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))
    if not cond:
        failures.append(name)


def load(path, name):
    """Import a hyphenated script as a module."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rig = load(os.path.join(TOOLS, "rig-check.py"), "rig_check")

# --------------------------------------------------------------------------
# cd-paranoia's cache figure, and the carriage return that hid it
# --------------------------------------------------------------------------
print("cdparanoia_cache_size")

# Verbatim shape of what the rig produced: cd-paranoia writes its progress with
# `\r` so the analysis block does not start after a `\n`. This exact string is
# what made the tool say it had searched and found nothing.
RIG = ("cdparanoia III release 10.2 libcdio 2.1.0\r"
       "Checking drive cache/timing behavior...\r"
       "Analyzing cache behavior...\r"
       "        Approximate random access cache size: 137 sector(s)\r\n"
       "        Drive cache tests as contiguous\r\n"
       "        Drive readahead past read cursor: 119 sector(s)\r\n")
check("finds the figure when the heading follows a carriage return",
      rig.cdparanoia_cache_size(RIG) == "137",
      f"got {rig.cdparanoia_cache_size(RIG)!r}")

check("finds it in ordinary newline-separated output",
      rig.cdparanoia_cache_size(
          "Analyzing cache behavior...\n"
          "        Approximate random access cache size: 140 sector(s)\n") == "140")

check("returns None when no cache size was reported",
      rig.cdparanoia_cache_size(
          "Analyzing cache behavior...\r"
          "Unable to open disc.\n") is None)

check("returns None on empty and on None input",
      rig.cdparanoia_cache_size("") is None and rig.cdparanoia_cache_size(None) is None)

# The loose pattern this one replaced would return 2352 here. The point of
# anchoring on the heading is that a number elsewhere in the output is not an
# answer, and an answer from the wrong line is worse than no answer.
check("does not take a number from some other line",
      rig.cdparanoia_cache_size(
          "Drive cache tests as contiguous\n"
          "reading 2352 bytes per sector\n"
          "no cache analysis was performed\n") is None)

# --------------------------------------------------------------------------
# `check`'s exit codes: 0 match, 1 different audio, 2 no comparison possible
# --------------------------------------------------------------------------
print("audio-checksums.py check exit codes")

TOOL = os.path.join(TOOLS, "audio-checksums.py")


def wav(path, pcm):
    """Minimal 44-byte canonical WAV, 44100/16/2, so ffmpeg decodes it."""
    with open(path, "wb") as fh:
        fh.write(b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVEfmt "
                 + struct.pack("<IHHIIHH", 16, 1, 2, 44100, 44100 * 4, 4, 16)
                 + b"data" + struct.pack("<I", len(pcm)) + pcm)


def log_for(path, track, vals, tracktotal=1):
    """The fragment of a cyanrip log that parse_log() reads."""
    with open(path, "w") as fh:
        fh.write(f"Track {track} ripped and encoded successfully!\n"
                 f"  Properties:\n"
                 f"    Samples:     {vals['samples']}\n"
                 f"\n  EAC CRC32:     {vals['eac_crc']:08X}\n"
                 f"    Accurip v1:  {vals['v1']:08X}\n"
                 f"    Accurip v2:  {vals['v2']:08X}\n"
                 f"    Accurip 450: {vals['v1_450']:08X}\n"
                 f"\n  Metadata:\n"
                 f"    track:                         {track}\n"
                 f"    tracktotal:                    {tracktotal}\n")


def run_check(audio, logpath, track):
    p = subprocess.run([sys.executable, TOOL, "check", "--log", logpath,
                        "--track", str(track), audio],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode


if not shutil.which("ffmpeg"):
    print("  SKIP  ffmpeg is not installed, so the exit-code cases cannot run.")
    print("        That is a gap in this run, not a pass -- say so if it matters.")
else:
    acs = load(TOOL, "audio_checksums")
    with tempfile.TemporaryDirectory() as td:
        # Two seconds of a deterministic non-silent signal. Silence would
        # compare equal to silence and prove nothing.
        pcm = bytes(((i * 2654435761) >> 8) & 0xFF for i in range(4 * 588 * 150))
        good = os.path.join(td, "01 - good.wav")
        wav(good, pcm)

        vals = acs.checksums(pcm, is_first=True, is_last=True)
        lg = os.path.join(td, "match.log")
        log_for(lg, 1, vals)
        check("exits 0 when the file matches the log", run_check(good, lg, 1) == 0)

        wrong = dict(vals, eac_crc=vals["eac_crc"] ^ 0xFFFFFFFF)
        lw = os.path.join(td, "differ.log")
        log_for(lw, 1, wrong)
        check("exits 1 when the file and the log describe different audio",
              run_check(good, lw, 1) == 1)

        # The case that was graded as an expected supersede: a file that is not
        # audio at all. It must not land in the same bucket as a re-rip.
        broken = os.path.join(td, "01 - broken.wav")
        with open(broken, "wb") as fh:
            fh.write(b"RIFF" + b"\x00" * 60)
        check("exits 2 when the file cannot be decoded at all",
              run_check(broken, lg, 1) == 2)

        check("exits 2 when the log has no such track",
              run_check(good, lg, 7) == 2)

        # Empty file: a zero-byte decode once read as "no peaks at all" here.
        empty = os.path.join(td, "01 - empty.wav")
        open(empty, "wb").close()
        check("exits 2 on a zero-byte file", run_check(empty, lg, 1) == 2)

    # ----------------------------------------------------------------------
    # `digest`: the whole-directory block, for when the audio cannot travel
    # ----------------------------------------------------------------------
    print("audio-checksums.py digest")

    def digest(args):
        p = subprocess.run([sys.executable, TOOL, "digest"] + args,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.returncode, p.stdout.decode()

    with tempfile.TemporaryDirectory() as td:
        pcm = bytes(((i * 2654435761) >> 8) & 0xFF for i in range(4 * 588 * 460))
        for name in ("01 - a.wav", "05 - b.wav", "10 - c.wav"):
            wav(os.path.join(td, name), pcm)
        # A file with no leading number must be skipped silently, not counted.
        wav(os.path.join(td, "cover-note.wav"), pcm)

        ec, out = digest([td, "--tracktotal", "14"])
        rows = [l for l in out.splitlines() if l and not l.startswith("#")]
        check("digest exits 0 and emits one row per numbered file",
              ec == 0 and len(rows) == 3, f"exit={ec} rows={len(rows)}")
        check("digest ignores files with no leading track number",
              "cover-note" not in out)
        check("digest names the assumed last track",
              "track 14 treated as the last on the disc" in out)

        # The trap the flag exists for: with no --tracktotal the highest number
        # present is assumed last, which applies AccurateRip's tail skip to a
        # track that is not the last one. The values MUST differ, and the
        # header must say which assumption produced them.
        _, out10 = digest([td])
        row10_a = [l for l in out.splitlines() if l.strip().startswith("10")][0]
        row10_b = [l for l in out10.splitlines() if l.strip().startswith("10")][0]
        check("assuming the wrong last track changes track 10's v1/v2",
              row10_a != row10_b)
        check("and the header discloses the assumption",
              "highest number present" in out10 and
              "highest number present" not in out)

        # Track 1 always gets the lead skip, so it must NOT depend on the
        # tracktotal assumption at all.
        r1a = [l for l in out.splitlines() if l.strip().startswith("1 ")][0]
        r1b = [l for l in out10.splitlines() if l.strip().startswith("1 ")][0]
        check("track 1 is unaffected by the tracktotal assumption", r1a == r1b)

    with tempfile.TemporaryDirectory() as td:
        wav(os.path.join(td, "no-number.wav"), pcm)
        ec, _ = digest([td])
        check("digest exits 2 when nothing in the directory is numbered", ec == 2)

    # ----------------------------------------------------------------------
    # rig-check's own grading of those exit codes
    # ----------------------------------------------------------------------
    print("rig-check.py check_audio grading")

    from pathlib import Path

    def grade(files, logvals=None, track=1):
        """Run check_audio over a synthetic album and return its status."""
        td = tempfile.mkdtemp()
        album, out = Path(td) / "album", Path(td) / "out"
        album.mkdir(); out.mkdir()
        for name, body in files.items():
            if body is None:
                wav(str(album / name), pcm)
            else:
                (album / name).write_bytes(body)
        lg = Path(td) / "rip.log"
        log_for(str(lg), track, logvals or acs.checksums(pcm, is_first=True,
                                                         is_last=True))
        return rig.check_audio(out, lg, album)

    pcm = bytes(((i * 2654435761) >> 8) & 0xFF for i in range(4 * 588 * 150))

    # The vacuous OK: files present, none nameable, so nothing was compared.
    # This returned OK "0 track(s) checked; every one matches its log".
    check("no filename carries a track number -> SKIP, not OK",
          grade({"untitled.flac": None, "bonus.flac": None}) == rig.SKIP)

    # The misgrade: a file that is not audio must not be filed under the
    # reassuring "expected for any track a re-rip superseded".
    check("an undecodable file -> FAIL, not INFO",
          grade({"01 - good.flac": None,
                 "02 - broken.flac": b"RIFF" + b"\x00" * 60}) == rig.FAIL)

    # And the case that IS an expected supersede still reads as INFO.
    wrongvals = dict(acs.checksums(pcm, is_first=True, is_last=True),
                     eac_crc=0x00000000)
    check("a genuine checksum difference -> INFO, unchanged",
          grade({"01 - superseded.flac": None}, logvals=wrongvals) == rig.INFO)

    check("everything matches -> OK, unchanged",
          grade({"01 - good.flac": None}) == rig.OK)

print()
if failures:
    print(f"FAILED: {len(failures)} check(s): {', '.join(failures)}")
    sys.exit(1)
print("all checks passed")
