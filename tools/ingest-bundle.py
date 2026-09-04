#!/usr/bin/env python3
"""Read a delivered acceptance bundle -- VERDICT FIRST, omissions DERIVED.

WHY THIS EXISTS, and it is not hypothetical.

The 2026-09-03 bundle contained `session/transcript.txt` and `report.json`.
They said:

    transcript.txt:293   [ FAIL ] L366  wait-for-rip 10800   (10800.1s)
    report.json          "ok": false,  counts {pass: 217, fail: 5}

Neither was filed. Neither was read. cyanrip then published `CC-1 IS MET` into
three documents, and Platterpus corrected it three laps later from a file that
had been sitting in our own scratch directory the whole time.

TWO FAILURES, AND THE SECOND IS WHAT MADE THE FIRST INVISIBLE.

  1. The run's own verdict was never consulted. We read the rips inside the run
     and concluded about the run -- "I verified the list you sent" is not "I
     verified your inventory".

  2. The filing note was written from MEMORY of what was dropped. It said "what
     is NOT here, and it is a choice rather than an omission", named the JSONs
     and the screenshots, and did not name these two. An absence nobody can see
     reads as a complete bundle -- which is, word for word, what Platterpus's
     own SOURCES.txt says it exists to prevent, in a file we DID read.

So this tool does two things a human reading a tarball reliably does not:

  * It prints the RUN-LEVEL VERDICT before anything else, and exits non-zero if
    the bundle says the run failed. Not a summary of the rips -- the run's own
    `ok` flag and its own FAIL lines.

  * It DERIVES the not-filed list, as the set difference between what the
    archive holds and what was written. A hand-written omission list is the
    defect, not the remedy.

It deliberately does NOT judge rip quality. That is Platterpus's under
OWNERSHIP.md §3. It reports what the bundle asserts about itself.
"""

import argparse
import hashlib
import json
import os
import pathlib
import re
import sys
import tarfile

# Files whose CONTENT states the outcome of the run, as opposed to the outcome
# of a rip inside it. Ordered by how directly they answer "did the run pass".
VERDICT_FILES = ("report.json", "transcript.txt")

# Extensions filed in full. Everything else is recorded by hash and named.
TEXT_SUFFIXES = (".log", ".cue", ".txt", ".toc", ".md")

FAIL_LINE = re.compile(r"^\s*\[\s*FAIL\s*\]", re.M)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_verdict(members):
    """What the bundle says about ITS OWN run. Returns (ok, lines)."""
    out, ok = [], None
    for name, data in members.items():
        base = os.path.basename(name)
        if base == "report.json":
            try:
                d = json.loads(data)
            except Exception as e:
                out.append(f"  {name}: UNPARSEABLE ({e})")
                continue
            if "ok" in d:
                ok = bool(d["ok"]) if ok is None else (ok and bool(d["ok"]))
                out.append(f"  {name}: ok = {d['ok']!r}")
            if "counts" in d:
                out.append(f"  {name}: counts = {d['counts']}")
        elif base == "transcript.txt":
            text = data.decode("utf-8", errors="replace")
            fails = FAIL_LINE.findall(text)
            if fails:
                ok = False
                out.append(f"  {name}: {len(fails)} [ FAIL ] line(s)")
                for m in FAIL_LINE.finditer(text):
                    line_no = text.count("\n", 0, m.start()) + 1
                    line = text[m.start():text.find("\n", m.start())]
                    out.append(f"      :{line_no}  {line.strip()[:96]}")
            else:
                out.append(f"  {name}: no [ FAIL ] lines")
    return ok, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archive")
    ap.add_argument("--into", help="directory to file into (docs/rig-...)")
    ap.add_argument("--verdict-only", action="store_true",
                    help="read and report the run's verdict; write nothing")
    args = ap.parse_args()

    blob = pathlib.Path(args.archive).read_bytes()
    print(f"archive: {args.archive}")
    print(f"sha256 : {sha256(blob)}\n")

    members = {}
    with tarfile.open(args.archive, "r:*") as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            f = tf.extractfile(m)
            members[m.name] = f.read() if f else b""

    # ---- 1. THE RUN'S OWN VERDICT, BEFORE ANYTHING ELSE -------------------
    print("=" * 68)
    print("RUN VERDICT -- what the bundle says about itself")
    print("=" * 68)
    ok, lines = read_verdict(members)
    if not lines:
        print("  NO VERDICT FILE FOUND. Looked for: " + ", ".join(VERDICT_FILES))
        print("  This is NOT 'the run passed'. It is 'the bundle does not say'.")
    else:
        print("\n".join(lines))
    print()
    if ok is False:
        print("  ***  THE BUNDLE SAYS THE RUN DID NOT PASS.  ***")
        print("  Do not describe this session as a pass. Rips inside a failed")
        print("  run are still evidence about the ripper; the run is not.")
    elif ok is True:
        print("  The bundle asserts the run passed. Check the sections you")
        print("  care about anyway -- `ok` is their aggregate, not ours.")
    print()

    if args.verdict_only:
        return 0 if ok is not False else 1

    if not args.into:
        print("no --into given; nothing filed")
        return 0 if ok is not False else 1

    # ---- 2. FILE, AND DERIVE WHAT WAS NOT FILED ---------------------------
    dest = pathlib.Path(args.into)
    filed, dropped = [], []
    for name, data in sorted(members.items()):
        # A VERDICT FILE IS ALWAYS FILED, whatever its extension. The first
        # draft of this tool keyed only on TEXT_SUFFIXES, so `report.json` --
        # the file that carries `ok` -- was named as not-filed and dropped.
        # That is the same defect the tool exists to prevent, reproduced in the
        # act of writing it, and tests/ingest_bundle.py is what found it.
        is_verdict = os.path.basename(name) in VERDICT_FILES
        if is_verdict or pathlib.PurePosixPath(name).suffix.lower() in TEXT_SUFFIXES:
            out = dest / name
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            filed.append(name)
        else:
            dropped.append(name)

    print("=" * 68)
    print(f"FILED {len(filed)} / NOT FILED {len(dropped)}   (derived, not recalled)")
    print("=" * 68)
    sums = dest / "SHA256SUMS"
    with sums.open("w") as fh:
        fh.write("# Filed here, byte-exact from the bundle.\n")
        for n in filed:
            fh.write(f"{sha256(members[n])}  {n}\n")
        fh.write("\n# NOT filed. This list is the SET DIFFERENCE between the\n"
                 "# archive's contents and what was written -- never a\n"
                 "# hand-written note, which is how two files carrying the\n"
                 "# run's own verdict were dropped from a filing whose own\n"
                 "# paragraph called the omissions 'a choice'.\n")
        for n in dropped:
            fh.write(f"{sha256(members[n])}  (not filed) {n}\n")
        fh.write(f"\n# The archive as delivered.\n{sha256(blob)}  (not filed) "
                 f"{os.path.basename(args.archive)}\n")
    print(f"  SHA256SUMS written: {len(filed)} filed + {len(dropped)} named-not-filed")

    missing = [v for v in VERDICT_FILES
               if not any(os.path.basename(n) == v for n in filed)]
    if missing:
        print(f"\n  WARNING: verdict file(s) not filed: {', '.join(missing)}")
        print("  They carry the run's outcome. File them.")
    return 0 if ok is not False else 1


if __name__ == "__main__":
    sys.exit(main())
