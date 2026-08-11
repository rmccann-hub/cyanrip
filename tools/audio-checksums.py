#!/usr/bin/env python3
"""Recompute cyanrip's per-track checksums over an audio file, and localise a
difference between two files.

Why this exists
---------------
Every claim of the form "the rip matches EAC" in this project's history has
rested on somebody else's comparison, reported in prose. `docs/AUDIT-2026-08-05.md`
§2 lists "14/14 bit-perfect vs EAC" as closed, and the artifact behind it is a
report, not a file anyone here can open. That is an assertion, not a
verification, by this project's own rule.

This makes it checkable. The algorithms are mirrored from `src/checksums.h` --
the same file the ripper uses -- so the numbers this prints are comparable to
the ones a cyanrip log states, and to the ones the AccurateRip database holds.

Mirrored, not shared: this is Python and that is C, and **the two can drift**.
`--self-test` is what catches that -- it recomputes against a known
(file, expected) pair, so a change to `src/checksums.h` that this file does not
follow shows up as a failure rather than as a quietly wrong number. There is no
way to make one implementation serve both without linking libavutil here.

What it does NOT do
-------------------
It cannot tell you a rip is *correct*. It tells you whether two sets of samples
agree, and what the ripper would have logged for them. Which read is the good
one is a judgement, and judgements belong downstream.

Usage
-----
    tools/audio-checksums.py sum FILE [--first] [--last]
    tools/audio-checksums.py check FILE --log cyanrip.log --track N
    tools/audio-checksums.py diff FILE_A FILE_B

`--first`/`--last` mirror `acurip_track_is_first`/`_is_last`: AccurateRip skips
the leading 5 sectors of track 1 and the trailing 5 of the last track, so the
v1/v2 sums are wrong for those tracks without the flag. `check` reads them from
the log's track count so you cannot forget.

Requires `ffmpeg` on PATH to decode; any format it can read works.

`check` exit codes, which callers are expected to distinguish:

    0   every field the log states matches the file
    1   they describe DIFFERENT audio -- normal when a consumer superseded the
        file after the log was written
    2   no comparison was possible at all: undecodable or truncated file, or a
        log with no such track

1 and 2 were both 1 until 2026-08-11, which let `rig-check.py` report a broken
file as an expected supersede. A caller that treats non-zero as one thing is
making the same mistake this project keeps finding in absence values: two
different facts collapsed into one symbol.
"""

import argparse
import re
import struct
import subprocess
import sys
import zlib

M32 = 0xFFFFFFFF
SECTOR_SAMPLES = 2352 >> 2          # 588 stereo frames per CD sector
AR_SKIP_SAMPLES = (2352 * 5) >> 2   # AccurateRip's 5-sector lead/tail skip

# `check` exits 1 when the audio and the log describe DIFFERENT audio, and 2
# when it could not compare them at all -- an undecodable file, a truncated
# file, a log with no such track. Those were both exit 1 until 2026-08-11,
# so a caller could not tell "this track was superseded by a re-rip", which is
# expected and fine, from "this file is broken", which is not. `rig-check.py`
# graded a truncated FLAC as the former and said so reassuringly in its report.
EXIT_DIFFER = 1
EXIT_UNUSABLE = 2


def unusable(msg):
    """Exit for 'no comparison was possible', distinct from 'they differ'."""
    print(msg, file=sys.stderr)
    sys.exit(EXIT_UNUSABLE)


def decode(path):
    """Decode to interleaved signed 16-bit little-endian stereo, as ripped."""
    p = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path,
         "-f", "s16le", "-acodec", "pcm_s16le", "-ac", "2", "-ar", "44100", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        unusable(f"{path}: ffmpeg failed: {p.stderr.decode(errors='replace').strip()}")
    if not p.stdout:
        unusable(f"{path}: decoded to zero bytes -- nothing to checksum")
    if len(p.stdout) % 4:
        unusable(f"{path}: decoded length {len(p.stdout)} is not a whole number "
                 "of stereo frames")
    return p.stdout


def checksums(pcm, is_first=False, is_last=False):
    """Mirror of crip_process_checksums()/crip_finalize_checksums()."""
    n = len(pcm) // 4

    # av_crc(AV_CRC_32_IEEE_LE) seeded UINT32_MAX and finalised ^UINT32_MAX is
    # bit-for-bit zlib's crc32.
    eac = zlib.crc32(pcm) & M32

    start = AR_SKIP_SAMPLES if is_first else 0
    end = n - AR_SKIP_SAMPLES if is_last else n

    v1 = v2 = v1_450 = 0
    lo_450 = 450 * SECTOR_SAMPLES
    hi_450 = 451 * SECTOR_SAMPLES
    mult = 1
    for (val,) in struct.iter_unpack("<I", pcm):
        if start <= mult <= end:
            v1 = (v1 + mult * val) & M32
            tmp = mult * val
            v2 = (v2 + (tmp >> 32) + (tmp & M32)) & M32
        if lo_450 <= mult - 1 < hi_450:
            v1_450 = (v1_450 + val * (mult - lo_450)) & M32
        mult += 1

    return {"samples": n, "eac_crc": eac, "v1": v1, "v2": v2, "v1_450": v1_450}


def parse_log(path):
    """Per-track checksums out of a cyanrip log, keyed by track number.

    Keyed off the `track:` line in each Metadata block rather than off block
    order, because a rip with -c or a mixed-mode disc does not number its
    blocks 1..N.
    """
    tracks, cur = {}, {}
    pats = (
        (re.compile(r"^\s+Samples:\s+(\d+)\s*$"), "samples", int),
        (re.compile(r"^\s+EAC CRC32:\s+([0-9A-F]{8})"), "eac_crc", lambda s: int(s, 16)),
        (re.compile(r"^\s+Accurip v1:\s+([0-9A-F]{8})"), "v1", lambda s: int(s, 16)),
        (re.compile(r"^\s+Accurip v2:\s+([0-9A-F]{8})"), "v2", lambda s: int(s, 16)),
        (re.compile(r"^\s+Accurip 450:\s+([0-9A-F]{8})"), "v1_450", lambda s: int(s, 16)),
    )
    track_line = re.compile(r"^\s+track:\s+(\d+)\s*$")
    total_line = re.compile(r"^\s+tracktotal:\s+(\d+)\s*$")
    total = None

    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            for pat, key, conv in pats:
                m = pat.match(line)
                if m:
                    cur[key] = conv(m.group(1))
            m = total_line.match(line)
            if m:
                total = int(m.group(1))
            m = track_line.match(line)
            if m and cur:
                tracks[int(m.group(1))] = cur
                cur = {}
    return tracks, total


def cmd_sum(args):
    c = checksums(decode(args.file), args.first, args.last)
    print(f"file:        {args.file}")
    print(f"samples:     {c['samples']}")
    print(f"EAC CRC32:   {c['eac_crc']:08X}")
    print(f"Accurip v1:  {c['v1']:08X}"
          f"{'   (first-track skip applied)' if args.first else ''}")
    print(f"Accurip v2:  {c['v2']:08X}"
          f"{'   (last-track skip applied)' if args.last else ''}")
    print(f"Accurip 450: {c['v1_450']:08X}")
    return 0


def cmd_check(args):
    tracks, total = parse_log(args.log)
    if args.track not in tracks:
        unusable(f"{args.log}: no track {args.track} (found: "
                 f"{sorted(tracks) or 'none'})")
    want = tracks[args.track]
    got = checksums(decode(args.file),
                    is_first=(args.track == 1),
                    is_last=(total is not None and args.track == total))

    if total is None:
        print("note: no `tracktotal:` in the log, so the last-track AccurateRip "
              "skip could not be applied -- v1/v2 will differ if this IS the "
              "last track", file=sys.stderr)

    print(f"file:  {args.file}")
    print(f"log:   {args.log}  track {args.track}"
          f"{f' of {total}' if total else ''}")
    print()
    bad = 0
    for key, label in (("samples", "samples   "), ("eac_crc", "EAC CRC32 "),
                       ("v1", "Accurip v1"), ("v2", "Accurip v2"),
                       ("v1_450", "Accurip 450")):
        if key not in want:
            print(f"  {label}  computed "
                  f"{got[key] if key == 'samples' else format(got[key], '08X')}"
                  f"   log: absent")
            continue
        fmt = (lambda v: str(v)) if key == "samples" else (lambda v: format(v, "08X"))
        same = got[key] == want[key]
        bad += not same
        print(f"  {label}  computed {fmt(got[key]):<10} "
              f"log {fmt(want[key]):<10} {'match' if same else 'DIFFER'}")

    if bad:
        print("\nThe file and the log describe different audio. That is not by "
              "itself a defect:\na consumer that re-rips a track and supersedes "
              "the file leaves the ripper's log\ndescribing the read that was "
              "thrown away -- by design, so the log stays verifiable.")
    return EXIT_DIFFER if bad else 0


def cmd_diff(args):
    a, b = decode(args.file_a), decode(args.file_b)
    if len(a) != len(b):
        print(f"lengths differ: {len(a)//4} vs {len(b)//4} stereo frames")
        print("Different track boundaries, not a read difference -- compare the "
              "TOC, not the audio.")
        return 1

    first = last = None
    ndiff = 0
    for i in range(0, len(a), 4):
        if a[i:i+4] != b[i:i+4]:
            ndiff += 1
            if first is None:
                first = i // 4
            last = i // 4

    if not ndiff:
        print(f"identical: {len(a)//4} stereo frames, sample for sample")
        return 0

    print(f"{ndiff} of {len(a)//4} stereo frames differ "
          f"({100.0*ndiff/(len(a)//4):.4f}%)")
    print(f"first differing sample: {first}  (CD sector {first//SECTOR_SAMPLES} "
          f"of this track, offset {first % SECTOR_SAMPLES})")
    print(f"last  differing sample: {last}   (CD sector {last//SECTOR_SAMPLES})")
    span = last // SECTOR_SAMPLES - first // SECTOR_SAMPLES + 1
    print(f"spanning {span} CD sector(s)")
    if span <= 8:
        print("\nA short span is the shape of a localised read problem. "
              "Which side is correct\nis not something this tool can tell you "
              "-- check both against AccurateRip.")
    return 1


def cmd_self_test(_args):
    """Guard the mirror. See the module docstring: this file and
    src/checksums.h are two implementations of one algorithm, and nothing else
    notices when they part company.

    The vector is synthetic and constructed here rather than read from a fixture,
    so the test travels with the file. It is NOT a check that the C is right --
    it is a check that this Python still computes what it computed on the day it
    was verified against three real EAC-ripped tracks, whose values are recorded
    in docs/handshake/round-07-lap-25.md.
    """
    pcm = bytes(((i * 2654435761) >> 8) & 0xFF for i in range(4 * SECTOR_SAMPLES * 460))
    c = checksums(pcm)
    expect = {"samples": SECTOR_SAMPLES * 460,
              "eac_crc": 0x34A93862, "v1": 0xE6955D38,
              "v2": 0x28C032D7, "v1_450": 0xD5CCCF1E}
    bad = 0
    for k, v in expect.items():
        got = c[k]
        ok = got == v
        bad += not ok
        shown = got if k == "samples" else f"{got:08X}"
        wanted = v if k == "samples" else f"{v:08X}"
        print(f"  {k:<10} {shown:<12} expected {wanted:<12} "
              f"{'ok' if ok else 'DRIFTED'}")
    if bad:
        print("\nThis file no longer computes what it did when it was verified "
              "against real\nEAC audio. Either it changed, or it was changed to "
              "follow src/checksums.h --\nin which case re-verify against real "
              "tracks and update these vectors, do not\njust paste the new "
              "numbers in.")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("sum", help="print cyanrip's checksums for a file")
    p.add_argument("file")
    p.add_argument("--first", action="store_true",
                   help="this is track 1 (apply AccurateRip's 5-sector lead skip)")
    p.add_argument("--last", action="store_true",
                   help="this is the last track (apply the 5-sector tail skip)")
    p.set_defaults(func=cmd_sum)

    p = sub.add_parser("check", help="compare a file against a cyanrip log")
    p.add_argument("file")
    p.add_argument("--log", required=True)
    p.add_argument("--track", type=int, required=True)
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("diff", help="localise where two files' samples differ")
    p.add_argument("file_a")
    p.add_argument("file_b")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("self-test", help="check this file has not drifted")
    p.set_defaults(func=cmd_self_test)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
