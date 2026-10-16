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

"""Print what a filed rig session shows, so a reading starts from the record.

WHY. Every filed run was read the same way, by hand: a grep per question,
rebuilt each time from the last README. The 2026-10-13 reading took some forty
commands to answer questions every reading asks -- did each log sign, who
called it, what the tallies say, which tracks hit the repeat limit and whether
the read kept was the last, whether any pregap search failed, whether each
log's `--diagnostics` record reached the bundle, what `-f` and the cache probe
printed, and whether the script's non-pass steps changed since the last run.

THIS JUDGES NOTHING. It prints what the files say, each line beside the file
it came from, and leaves the reading -- what is a defect, and whose -- to
whoever writes the README. A summary that drew conclusions would be a second
author of the reading, and one nobody reviews.

Usage:
    tools/read-run.py docs/rig-2026-10-13-200530e
    tools/read-run.py docs/rig-2026-10-13-200530e --cyanrip build/src/cyanrip
"""

import argparse
import collections
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import evidence  # noqa: E402

BANNER = re.compile(r"^cyanrip \S+ \(")
NOT_PASS = ("fail", "error", "skipped", "blocked", "unreachable", "info")
# The strings the program prints, from its source: a Done; line at the repeat
# limit (src/cyanrip_main.c, "repeat limit of %i read%s reached"), the clause
# naming a last read that was not kept ("last read %08X, not kept"), and a
# pregap whose search failed ("pregap of track %i unknown (%s)").
DONE_RE = re.compile(r"^Done; \((.*)\)$")
REPEAT_RE = re.compile(r"^Repeating ripping \((\d+) out of (\d+) matches for "
                       r"current checksum ([0-9A-F]{8})\)$")
TRACK_RE = re.compile(r"^Track (\d+) (read successfully!|read with errors\.|.*)$")
GAP_RE = re.compile(r"^\s+(\d+) frame pregap in track (\d+)")
UNKNOWN_GAP_RE = re.compile(r"^\s+pregap of track (\d+) unknown \((.*)\)$")
DIAG_RE = re.compile(r"(?:^|\s)(?:--diagnostics|-j) (\S+)")
TALLY_RE = re.compile(r"^(Tracks ripped accurately|Tracks matched on one frame "
                      r"only|Tracks ripped partially accurately): (.*)$")
FOOTER = ("Ripping errors:", "Read stalls:", "Rip completed:", "Consumer:",
          "Handshake:", "Tracks to rip:")
TRANSCRIPT_RE = re.compile(r"^\s*(?:Drive offset of|Cache probe:|cd-paranoia -A:)")


LOG_DIRS = ("album", "rips")


def logs_in(run):
    """Every cyanrip log filed under album/ (or rips/, the layout before
    2026-09-27): a file whose first line is the banner. A securing pass's log
    is kept under another suffix and is a log all the same; an
    EAC-compatible rendering is not ours."""
    out = []
    for p in sorted(q for d in LOG_DIRS for q in (run / d).rglob("*")):
        if not p.is_file() or "(EAC-compatible)" in p.name:
            continue
        try:
            with p.open(encoding="utf-8") as fh:
                first = fh.readline()
        except (UnicodeDecodeError, OSError):
            continue
        if BANNER.match(first):
            out.append(p)
    return out


def short(run, p):
    rel = p.relative_to(run)
    name = rel.parts[1] if len(rel.parts) > 2 else p.stem
    kind = "securing pass" if "securing-pass" in p.name else "log"
    return f"{name[:44]} [{kind}]"


def report(run):
    p = run / "session" / "run" / "report.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def non_pass(rep):
    return sorted((int(s.get("line_no") or 0), s.get("source", ""),
                   s.get("outcome", ""))
                  for s in rep.get("steps", [])
                  if s.get("outcome") in NOT_PASS)


def previous_run(run):
    runs = sorted(d for d in run.parent.glob("rig-*")
                  if d.is_dir() and (d / "session" / "run" / "report.json").exists())
    earlier = [d for d in runs if d.name < run.name]
    return earlier[-1] if earlier else None


def read_log(p):
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    info = {"invoked": "", "footer": {}, "tallies": {}, "gaps": [],
            "unknown": [], "none_signalled": False, "limits": [],
            "secure": collections.Counter()}
    reps, in_gaps = [], False
    for ln in lines:
        if ln.startswith("Invoked as:"):
            info["invoked"] = ln
        for f in FOOTER:
            if ln.startswith(f):
                info["footer"].setdefault(f, ln[len(f):].strip())
        m = TALLY_RE.match(ln)
        if m:
            info["tallies"][m.group(1)] = m.group(2)
        if ln.startswith("Gaps:"):
            in_gaps = True
            continue
        if in_gaps:
            m, u = GAP_RE.match(ln), UNKNOWN_GAP_RE.match(ln)
            if m:
                info["gaps"].append((int(m.group(2)), int(m.group(1))))
            elif u:
                info["unknown"].append((int(u.group(1)), u.group(2)))
            elif ln.strip() == "None signalled":
                info["none_signalled"] = True
            elif not ln.strip() or not ln.startswith(" "):
                in_gaps = False
        m = REPEAT_RE.match(ln)
        if m:
            reps.append(m.group(3))
        m = DONE_RE.match(ln)
        if m:
            done, reps_here, reps = m.group(1), reps, []
            if "repeat limit" in done:
                info["limits"].append({"done": done, "reads": reps_here,
                                       "track": None})
        m = TRACK_RE.match(ln)
        if m and info["limits"] and info["limits"][-1]["track"] is None:
            info["limits"][-1]["track"] = int(m.group(1))
            info["limits"][-1]["outcome"] = m.group(2)
        s = re.match(r"^\s+Secure re-read:\s+(.*)$", ln)
        if s:
            info["secure"][s.group(1)] += 1
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run", help="a filed session, docs/rig-...")
    ap.add_argument("--cyanrip", help="a cyanrip binary, to check every log "
                                      "with -Y")
    args = ap.parse_args()
    run = pathlib.Path(args.run)
    # A FILED SESSION MAY BE ON THE EVIDENCE BRANCH (HR-2), with only its
    # README in this checkout. It is then read from an overlay where the
    # session, and every earlier session's report.json the comparison below
    # reads, are at their own paths, read through tools/evidence.py.
    overlay_dir = None
    try:
        rel = run.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        rel = None
    if rel and evidence.run_folder(rel + "/x") == rel:
        store = evidence.Store(ROOT)
        need = [p for p in store.files(rel) if not store.in_tree(p)]
        need += [f"{f}/session/run/report.json" for f in store.folders()
                 if f"{f}/session/run/report.json" in store.rows
                 and not store.in_tree(f"{f}/session/run/report.json")]
        if need:
            import tempfile
            overlay_dir = tempfile.TemporaryDirectory(prefix="read-run-")
            try:
                evidence.overlay(store, set(need), overlay_dir.name)
            except evidence.NotFetched as e:
                print(f"{rel} is on the evidence branch and not fetched here: "
                      f"{e}", file=sys.stderr)
                return evidence.UNPROBED
            run = pathlib.Path(overlay_dir.name) / rel
    if not any((run / d).is_dir() for d in LOG_DIRS):
        print(f"{run} has neither album/ nor rips/: not a filed session",
              file=sys.stderr)
        return 2

    def head(t):
        print(f"\n{'=' * 68}\n{t}\n{'=' * 68}")

    # ---- the script's verdict, and what changed since the last run -------
    head("VERDICT -- session/run/report.json")
    rep = report(run)
    if rep is None:
        print("  no readable report.json: the script's verdict is unknown")
    else:
        for k in ("started_at", "run_size", "ok", "counts_as_evidence", "counts"):
            print(f"  {k}: {rep.get(k)}")
        steps = non_pass(rep)
        for s in steps:
            print(f"  L{s[0]:<5} {s[2]:12} {s[1]}")
        prev = previous_run(run)
        if prev is not None:
            before = non_pass(report(prev) or {})
            if before == steps:
                print(f"  the same {len(steps)} non-pass step(s) as {prev.name}")
            else:
                print(f"  DIFFERS from {prev.name}: "
                      f"new {sorted(set(steps) - set(before))}, "
                      f"gone {sorted(set(before) - set(steps))}")

    # ---- every log ------------------------------------------------------
    logs = logs_in(run)
    infos = {p: read_log(p) for p in logs}
    head(f"LOGS -- {len(logs)} cyanrip log(s) under album/ or rips/")
    banners = collections.Counter(p.read_text(encoding="utf-8").splitlines()[0]
                                  for p in logs)
    for b, n in banners.items():
        print(f"  {n} x {b}")
    for p in logs:
        i = infos[p]
        print(f"\n  {short(run, p)}")
        flags = " ".join(m.group(0).strip() for m in re.finditer(
            r" -(?:Z|l|r|f|s|P) \S+| -[HWE](?= )|--cache-probe|-x(?= )",
            i["invoked"]))
        print(f"    flags:      {flags or '(none of -Z -l -r -f -s -P -H -W -E)'}")
        for f in FOOTER:
            if f in i["footer"]:
                print(f"    {f:15} {i['footer'][f][:110]}")
        for k, v in i["tallies"].items():
            print(f"    {k}: {v}")
        if i["secure"]:
            print("    secure re-read: " + "; ".join(
                f"{n} x {s}" for s, n in sorted(i["secure"].items())))
        if args.cyanrip:
            try:
                r = subprocess.run([args.cyanrip, "-Y", str(p)],
                                   capture_output=True, text=True)
                said = ("verifies" if r.returncode == 0
                        else f"DOES NOT VERIFY (exit {r.returncode})")
            except OSError as e:
                # Not run is not the same claim as not verified.
                said = f"not run ({e.strerror}: {args.cyanrip})"
            print(f"    -Y:         {said}")

    # ---- the repeat limit -----------------------------------------------
    head("REPEAT LIMIT -- every Done; line that names it")
    any_limit = False
    for p in logs:
        for lim in infos[p]["limits"]:
            any_limit = True
            reads = lim["reads"]
            print(f"  {short(run, p)}, track {lim['track']}: "
                  f"{lim.get('outcome', '?')}")
            print(f"    Done; ({lim['done']})")
            print(f"    checksums before the last read: {' '.join(reads) or 'none'}"
                  f" ({len(set(reads))} distinct of {len(reads)})")
            print(f"    clause naming a last read not kept: "
                  f"{'PRINTED' if 'last read' in lim['done'] else 'not printed'}")
    if not any_limit:
        print("  no read hit the repeat limit")

    # ---- gaps -------------------------------------------------------------
    head("GAPS -- each log's Gaps: list")
    per_track = collections.defaultdict(set)
    listed_in = collections.defaultdict(list)
    for p in logs:
        i = infos[p]
        for t, n in i["gaps"]:
            per_track[t].add(n)
            listed_in[t].append(p)
        flags = []
        if i["unknown"]:
            flags.append(f"UNKNOWN: {i['unknown']}")
        if i["none_signalled"]:
            flags.append("None signalled")
        print(f"  {short(run, p)}: {len(i['gaps'])} pregap(s)"
              + (f"; {', '.join(flags)}" if flags else ""))
    varied = {t: sorted(v) for t, v in sorted(per_track.items()) if len(v) > 1}
    print(f"  a track whose pregap differs between logs: {varied or 'none'}")
    # A pregap one list gives and another leaves out is the larger form of
    # the same disagreement: the search returned zero, or failed with no
    # line (before .22). The track's own block, if the log ripped it, says
    # which. Found reading 2026-10-13: track 4 absent from one of 13 lists.
    for t in sorted(listed_in):
        # A list that says the search failed (`unknown`) accounts for the
        # track; only a list silent about it leaves it out.
        absent = [p for p in logs if p not in listed_in[t]
                  and not infos[p]["none_signalled"]
                  and t not in {u for u, _ in infos[p]["unknown"]}]
        if absent:
            print(f"  track {t}'s pregap is in {len(listed_in[t])} list(s) "
                  f"and absent from {len(absent)}:")
            for p in absent:
                print(f"    {short(run, p)}")

    # ---- --diagnostics records ------------------------------------------
    head("RECORDS -- each log's --diagnostics name against the bundle")
    sums = run / "SHA256SUMS"
    listed = set()
    if sums.exists():
        listed = {pathlib.PurePosixPath(m.group(1)).name for m in re.finditer(
            r"\s((?:\(not filed\) )?\S*ripperdiagnostics\S*/\S+\.json)$",
            sums.read_text(encoding="utf-8"), re.M)}
        listed = {n.replace("(not filed) ", "") for n in listed}
    asked = 0
    for p in logs:
        m = DIAG_RE.search(infos[p]["invoked"])
        if not m:
            print(f"  {short(run, p)}: asks for no record")
            continue
        asked += 1
        name = pathlib.PurePosixPath(m.group(1)).name
        if name in listed:
            print(f"  {short(run, p)}: {name} in the bundle")
            continue
        # Platterpus keeps a securing pass's record under the name the log
        # gives plus `-securingpass` before the suffix, numbered if that is
        # taken (their X6, platterpus@dd200af7:src/platterpus/record_fate.py:
        # 49, 102). Only a securing pass's: an album pass's record is kept
        # under its own name, so a renamed copy of one is not looked for.
        # Found reading 2026-10-16, which reported both of the first two kept
        # records missing.
        stem, dot, ext = name.rpartition(".")
        kept = re.compile(re.escape(stem) + r"-securingpass\d*"
                          + re.escape(dot + ext) + "$")
        copies = sorted(n for n in listed if kept.match(n))
        if "securing-pass" in p.name and copies:
            print(f"  {short(run, p)}: {name} in the bundle as "
                  f"{', '.join(copies)}")
        else:
            print(f"  {short(run, p)}: {name} NOT IN THE BUNDLE")
    print(f"  {asked} log(s) ask for a record; the bundle lists {len(listed)}")

    # ---- the transcript ---------------------------------------------------
    head("TRANSCRIPT -- -f, the cache probe and cd-paranoia -A")
    t = run / "session" / "transcript.txt"
    if t.exists():
        for n, ln in enumerate(t.read_text(encoding="utf-8",
                                           errors="replace").splitlines(), 1):
            if TRANSCRIPT_RE.search(ln):
                print(f"  session/transcript.txt:{n}: {ln.strip()[:150]}")
    else:
        print("  no session/transcript.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
