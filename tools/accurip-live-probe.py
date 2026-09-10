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

"""Drive the AccurateRip response parser against the LIVE database, no drive.

WHAT THIS OVERTURNS. `CLAUDE.md` said, and round-16 lap 1 §0 told Platterpus,
that close-condition clause 1 *"is the one we cannot reach at all here -- every
scenario passes `-A`, and there is no network in this environment, so
`crip_fill_accurip()` returns before any of the rewritten code executes."*

**Both halves stopped being true.** This sandbox reaches `accuraterip.com`, and
the query is driven by the TOC alone -- so an image whose track offsets match a
disc that IS in the database produces the same request a real rip would, gets a
real 200 back, and runs the rewritten parser over it. Measured 2026-09-10: the
reference disc's TOC gave `AccurateRip: found` and `max confidence: 200`, and
200 is the maximum confidence in that disc's own rig log.

WHY IT IS A TOOL AND NOT A TEST. It reaches the network, and a check that
reaches the network is not evidence about this program -- it would fail offline
for reasons unrelated to anything. Homes considered: `tools/rig-check.py` is
the no-rip checks and this rips; `tools/rig-round16.sh` needs a drive;
`tests/rip_images.py` may not reach the network. None fit.

WHAT IT DOES AND DOES NOT SETTLE. The audio is silence, so every per-track
checksum is `00000000` and correctly matches nothing. It exercises the QUERY
and the RESPONSE PARSE; it does not exercise the per-track MATCH path, which
needs the real audio and therefore the drive. Clause 1 is de-risked, not
settled, and this prints that rather than leaving it to be assumed.

    tools/accurip-live-probe.py --crip build/src/cyanrip
"""

import argparse
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
# The reference disc, read from the log of the rig session that ripped it
# rather than typed. A TOC transcribed by hand is a second description of a
# fact, and this one has fourteen chances to be wrong.
REF_LOG = ROOT / "docs" / "rig-2026-09-10-ddc1e8c" / "rips" / "secure-reread.log"
SECTOR = 2352


def toc_from(log):
    text = log.read_text(encoding="utf-8", errors="replace")
    lsns = [int(m) for m in
            re.findall(r"^\s+Start LSN:\s+(\d+)", text, re.M)]
    tt = re.search(r"^Total time:\s+(\d+):(\d+)\.(\d+)", text, re.M)
    if not lsns or not tt:
        sys.exit(f"{log}: no Start LSN lines or no Total time -- cannot build "
                 f"a TOC from it")
    mm, ss, ff = (int(g) for g in tt.groups())
    return lsns, mm * 60 * 75 + ss * 75 + ff


def msf(lsn):
    return f"{lsn // (75 * 60):02d}:{(lsn // 75) % 60:02d}:{lsn % 75:02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--crip", default="build/src/cyanrip")
    ap.add_argument("--tracks", default="1,2,3",
                    help="which tracks to rip; the query covers the whole TOC "
                         "either way, so three is enough and is faster")
    args = ap.parse_args()

    lsns, leadout = toc_from(REF_LOG)
    print(f"TOC from {REF_LOG.relative_to(ROOT)}: {len(lsns)} tracks, "
          f"leadout {leadout}")

    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        cue = ['FILE "disc.bin" BINARY']
        for i, l in enumerate(lsns, 1):
            cue += [f"  TRACK {i:02d} AUDIO", f"    INDEX 01 {msf(l)}"]
        (d / "disc.cue").write_text("\n".join(cue) + "\n")
        # Sparse: the bytes are never written, the filesystem serves zeros, and
        # a 603 MB image costs nothing on disk.
        with open(d / "disc.bin", "wb") as f:
            f.truncate(leadout * SECTOR)

        crip = str(pathlib.Path(args.crip).resolve())
        r = subprocess.run(
            [crip, "-d", "disc.cue", "-s", "0", "-P", "0", "-l", args.tracks,
             "-N", "-U", "-o", "flac", "-D", "out", "-F", "{track}",
             "-L", "ar", "-M", "ar"],
            cwd=d, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=600)
        out = r.stdout.decode(errors="replace")
        log = (d / "out" / "ar.log")
        logtext = log.read_text(errors="replace") if log.exists() else ""

    status = re.search(r"^AccurateRip:\s+(\S.*?)\s*$", logtext, re.M)
    conf = re.search(r"max confidence:\s*(\d+)", out)
    print(f"  exit {r.returncode}")
    print(f"  AccurateRip: {status.group(1) if status else '<no line>'}")
    print(f"  max confidence parsed: {conf.group(1) if conf else '<none>'}")

    if not status:
        print("\nNO `AccurateRip:` LINE. The rip did not reach the point of "
              "reporting;\nread the output above.")
        return 1
    if status.group(1) != "found":
        print(f"\n`AccurateRip: {status.group(1)}` -- the parser RAN and this "
              f"is a real\nmeasurement, but the disc was not matched, so the "
              f"response parse is\nNOT exercised. Is the reference TOC still "
              f"in the database?")
        return 2
    if not conf:
        print("\nFOUND but no confidence parsed -- a status without a "
              "confidence is the\nshape a broken response parse makes.")
        return 1

    print(f"\nThe rewritten response parser ran over a real 200 and read a "
          f"confidence\nout of it, with no drive.\n"
          f"NOT SETTLED BY THIS: the per-track MATCH path. The audio is "
          f"silence, so every\nchecksum is 00000000 and correctly matches "
          f"nothing. Clause 1 is de-risked,\nnot closed -- that needs the "
          f"disc.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
