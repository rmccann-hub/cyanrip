#!/usr/bin/env python3
"""Compare every read of each track across all the cyanrip logs in a bundle.

WHY THIS EXISTS. Round 26's reading checked AccurateRip on the whole-disc rip
and not across the two-track rips, and missed a wrong read that only shows up
across them: `rips/after-cancel.log` reads track 1 as `EAC CRC32: 0E91CD1A`,
while the five other rips of track 1 in the same session read `B0D122E7`, each
an exact AccurateRip match. Platterpus found it (their round 26 lap 5 §B3). The
same wrong bytes were already filed thirteen days earlier, in
`docs/rig-2026-09-11-ddc1e8c/rips/derived-wavpack.log`, and nobody had noticed.
A log read on its own cannot show either: each one is internally consistent.
Only putting the reads of one track side by side does.

WHAT IT COMPARES. Reads are grouped by disc (`DiscID:`) and read offset
(`Offset:`), because a different offset gives different bytes by design, and a
comparison across offsets would report a disagreement nobody caused. Within a
group, each track's `EAC CRC32` is compared across every log that read it. A
track read with more than one checksum is reported as a DISAGREEMENT, with each
checksum's logs and what AccurateRip said about that read.

WHAT IT DOES NOT DO. It does not say which read is right. That is a judgement
and it belongs downstream; the AccurateRip status beside each checksum is the
evidence, printed as the log states it. It reads cyanrip's logs only, found by
content (rig-check.py's `is_cyanrip_log`, imported rather than copied), so a
consumer's EAC-format export or addendum is not read and cannot supersede
anything here. A track the log has no block for (a killed or interrupted read)
is not a read and is not counted.

Exit status: 0 every track agrees; 1 at least one disagreement; 2 nothing to
compare (no cyanrip log, or no track block in any). 1 and 2 are different
claims and stay apart.

Usage:
    python3 tools/cross-rip.py docs/rig-2026-09-24-df91ae7/rips
"""

import argparse
import collections
import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("rigcheck", ROOT / "tools" / "rig-check.py")
_rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rc)
is_cyanrip_log = _rc.is_cyanrip_log

# Both wordings: round 22 renamed `Track N ripped and encoded successfully!` to
# `Track N read successfully!` / `read with errors.`, and filed logs carry the
# old one. A block DELIMITER over a format with a history, as in rig-check.py.
TRACK_BLOCK = re.compile(r"^Track (\d+) (?:ripped|read)\b.*$", re.M)
DISC_ID = re.compile(r"^DiscID:\s+(\S+)", re.M)
OFFSET = re.compile(r"^Offset:\s+(.+?)\s*$", re.M)
EAC_CRC = re.compile(r"^\s+EAC CRC32:\s+([0-9A-F]{8})\b(.*)$", re.M)
AR_LINE = re.compile(r"^\s+Accurip (v1|v2|450):\s+[0-9A-F]{8}(?: \((.*)\))?\s*$", re.M)


def ar_summary(block):
    """What the log says AccurateRip found for this read, in its own words."""
    parts = []
    for name, paren in AR_LINE.findall(block):
        if not paren:
            continue
        m = re.search(r"confidence (\d+)", paren)
        if paren.startswith("accurately ripped") and m:
            parts.append(f"{name} match, confidence {m.group(1)}")
        elif paren.startswith("matches Accurip DB") and m:
            parts.append(f"{name} match, confidence {m.group(1)}")
        elif paren.startswith("not found"):
            parts.append(f"{name} not found")
        else:
            parts.append(f"{name}: {paren}")
    return "; ".join(parts) if parts else "no AccurateRip result in the log"


def reads_in(path):
    """[(disc, offset, track, crc, suffix, ar)] for one log."""
    text = path.read_text(encoding="utf-8", errors="replace")
    disc = DISC_ID.search(text)
    off = OFFSET.search(text)
    disc = disc.group(1) if disc else "unknown disc"
    off = off.group(1) if off else "unknown offset"
    heads = list(TRACK_BLOCK.finditer(text))
    out = []
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        block = text[h.end():end]
        crc = EAC_CRC.search(block)
        if not crc:
            continue
        out.append((disc, off, int(h.group(1)), crc.group(1),
                    crc.group(2).strip(), ar_summary(block)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", type=pathlib.Path,
                    help="directories to search, or log files")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        cands = sorted(p.rglob("*")) if p.is_dir() else [p]
        files += [c for c in cands if c.is_file() and is_cyanrip_log(c)]
    groups = collections.defaultdict(lambda: collections.defaultdict(list))
    logs_per_group = collections.defaultdict(set)
    for f in files:
        for disc, off, tr, crc, suffix, ar in reads_in(f):
            groups[(disc, off)][tr].append((crc, suffix, ar, f))
            logs_per_group[(disc, off)].add(f)

    if not groups:
        print(f"nothing to compare: {len(files)} cyanrip log(s) found, "
              "and none has a track block with an EAC CRC32")
        return 2

    disagree = 0
    for (disc, off), tracks in sorted(groups.items()):
        print(f"disc {disc} at offset {off}: {len(logs_per_group[(disc, off)])} "
              f"log(s), {len(tracks)} track(s) read at least once")
        for tr in sorted(tracks):
            reads = tracks[tr]
            by_crc = collections.defaultdict(list)
            for crc, suffix, ar, f in reads:
                by_crc[crc].append((f, suffix, ar))
            state = "agree" if len(by_crc) == 1 else "DISAGREE"
            disagree += state == "DISAGREE"
            print(f"  track {tr}: {len(reads)} read(s), {len(by_crc)} distinct "
                  f"EAC CRC32  {state}")
            if state == "agree":
                continue
            for crc, rs in sorted(by_crc.items(), key=lambda kv: -len(kv[1])):
                ars = sorted({ar for _, _, ar in rs})
                names = ", ".join(sorted(f"{f.name}{' ' + s if s else ''}"
                                         for f, s, _ in rs))
                print(f"      {crc}  x{len(rs)}  [{' | '.join(ars)}]  {names}")
    if disagree:
        print(f"\n{disagree} track(s) read with more than one checksum. Which read "
              "is right is not decided here; the AccurateRip result beside each "
              "is the log's own.")
        return 1
    print("\nevery track that was read more than once was read the same way")
    return 0


if __name__ == "__main__":
    sys.exit(main())
