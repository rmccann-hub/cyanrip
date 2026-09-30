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

AND IT SAYS WHETHER THE PAIR WAS THE NEWEST WHEN THE RUN BEGAN (round 30's
release-cycle proposal, D3, C4): *"a run tests only the newest pair ... A run
on anything else is not evidence"*. The 2026-09-28 14:42 run tested `.17` a
second time while `.18` was published mid-run. The report compares the build
the bundle ran with the newest release of ours at the run's start, by the
commit that added its row to `docs/release-ledger.tsv`, and the app with the
newest tag of theirs at that time when `--peer` names their tree. A commit
date is when the row was written, not when it was pushed, and the report says
so. A pair it cannot establish is `unknown`, never newest.
"""

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tarfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = "docs/release-ledger.tsv"
BANNER = re.compile(r"cyanrip (\S+) \(platterpus-fork-g([0-9a-f]{7,40})\)")

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
            elif not text.strip():
                # A clean result must name its population, or it prints the
                # same over nothing as over a whole run. Platterpus's round 28
                # lap 2 S19-S20: a secret scan that read 0 commits and said
                # "no leaks found". An empty transcript is not a clean one.
                out.append(f"  {name}: EMPTY, {len(data)} byte(s) -- it records "
                           f"nothing, which is not 'no failures'")
            else:
                n = len(text.splitlines())
                out.append(f"  {name}: no [ FAIL ] lines in {n} line(s)")
    return ok, out


def when(text):
    """An ISO 8601 time as an aware datetime, or None."""
    try:
        t = datetime.datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
    return t if t.tzinfo else t.replace(tzinfo=datetime.timezone.utc)


def read_pair(members):
    """What the bundle says it ran: (start, end, ripper builds, app, start's file)."""
    started, ended, app, builds, start_from = None, None, None, {}, None
    for name, data in sorted(members.items()):
        base = os.path.basename(name)
        if base in ("script-report.json", "report.json"):
            try:
                d = json.loads(data)
            except Exception:
                continue
            if started is None and when(str(d.get("started_at", ""))):
                started = when(d["started_at"])
                start_from = name
                # No end field exists. The start plus the sum of the steps'
                # own times is when the last step finished, not counting any
                # gap between steps, so it is the earliest the run can have
                # ended.
                steps = d.get("steps") or []
                total = sum(float(s.get("elapsed_s") or 0) for s in steps
                            if isinstance(s, dict))
                if steps:
                    ended = started + datetime.timedelta(seconds=total)
            if app is None and d.get("app_version"):
                app = str(d["app_version"])
        elif base == "COMPONENTS.json" and app is None:
            try:
                app = str(json.loads(data).get("app") or "") or None
            except Exception:
                pass
        # The ripper is read from what the ripper printed: the version probe
        # and each log's banner. Every build named is kept, so a bundle that
        # ran two builds says two and is not reduced to the first.
        if base == "rig-check-ripper-version.txt" or name.endswith(".log"):
            first = data[:400].decode("utf-8", errors="replace")
            m = BANNER.search(first.splitlines()[0] if first else "")
            if m:
                builds.setdefault(m.group(2)[:7], (m.group(1), []))[1].append(name)
    return started, ended, builds, app, start_from


def publications(root=ROOT):
    """Each release row of the ledger with the commit that added it.

    Returns [(seq, version, commit, published_at, by)], or None outside a git
    checkout. published_at is that commit's committer date: when the row was
    written, which is not when it was pushed.
    """
    try:
        r = subprocess.run(
            ["git", "-C", str(root), "log", "--reverse", "-p", "--no-color",
             "--format=@@commit %h %cI", "--", LEDGER],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    out, seen, commit, date = [], set(), None, None
    for line in r.stdout.splitlines():
        if line.startswith("@@commit "):
            _, commit, stamp = line.split(" ", 2)
            date = when(stamp)
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        cols = line[1:].split("\t")
        if len(cols) < 4 or not cols[0].strip().isdigit():
            continue
        seq = int(cols[0])
        if seq in seen:
            continue
        seen.add(seq)
        out.append((seq, cols[2].strip(), cols[3].strip(), date, commit))
    return out


def peer_releases(peer):
    """Their tags v*, each with its creator date: [(tag, date)], or None."""
    try:
        r = subprocess.run(
            ["git", "-C", str(peer), "for-each-ref", "refs/tags/v*",
             "--format=%(refname:short)\t%(creatordate:iso-strict)"],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    tags = []
    for line in r.stdout.splitlines():
        tag, _, stamp = line.partition("\t")
        if when(stamp):
            tags.append((tag, when(stamp)))
    return tags


def report_pair(members, peer=None, root=ROOT):
    """D3: was the bundle's pair the newest when its run began? Lines to print."""
    started, ended, builds, app, start_from = read_pair(members)
    out = []
    if started is None:
        out.append("  run start: unknown (no started_at in a script-report.json "
                   "or report.json), so neither side can be judged newest")
    else:
        out.append(f"  run start: {started.isoformat()} (started_at in "
                   f"{start_from})")
        if ended is not None:
            out.append(f"  run end:   {ended.isoformat()} at the earliest (the "
                       f"start plus the sum of the report's step times)")

    # ---- ours ----
    if not builds:
        out.append("  cyanrip: unknown (no banner in the version probe or any "
                   "log), which is NOT newest")
    elif len(builds) > 1:
        names = ", ".join(f"{v} {sha}" for sha, (v, _) in sorted(builds.items()))
        out.append(f"  cyanrip: the bundle ran {len(builds)} builds ({names}); a "
                   f"run on more than one ripper is not one pair")
    elif started is not None:
        sha, (version, seen_in) = next(iter(builds.items()))
        pubs = publications(root)
        if pubs is None:
            out.append(f"  cyanrip: ran {version} at {sha}; unknown whether "
                       f"newest (no git history of {LEDGER} to read)")
        else:
            before = [p for p in pubs if p[3] is not None and p[3] <= started]
            mine = [p for p in pubs if p[2][:7] == sha]
            newest = max(before, key=lambda p: p[0]) if before else None
            if newest and newest[2][:7] == sha:
                out.append(f"  cyanrip: NEWEST -- ran {version} at {sha}, "
                           f"release_seq {newest[0]}, the newest in {LEDGER} at "
                           f"the run's start (its row added by {newest[4]} at "
                           f"{newest[3].isoformat()}, a commit date, not a push)")
            elif mine and mine[0][3] is not None and mine[0][3] > started:
                out.append(f"  cyanrip: NOT YET PUBLISHED -- ran {version} at "
                           f"{sha}, whose ledger row was added by {mine[0][4]} "
                           f"at {mine[0][3].isoformat()}, after the run began")
            elif mine:
                out.append(f"  cyanrip: STALE -- ran {version} at {sha}, "
                           f"release_seq {mine[0][0]}; {newest[1]} at "
                           f"{newest[2]}, release_seq {newest[0]}, was published "
                           f"by {newest[4]} at {newest[3].isoformat()}, before "
                           f"the run began. Not evidence under D3")
            else:
                out.append(f"  cyanrip: NOT A RELEASE -- ran {version} at {sha}, "
                           f"which no row of {LEDGER} names (a test pin, or an "
                           f"unreleased build)")
            # D3's own case: 2026-09-28 14:42 ran .17, newest at its start,
            # and .18 was published at 17:32 while it ran.
            base_seq = mine[0][0] if mine else None
            during = [p for p in pubs if p[3] is not None and ended is not None
                      and started < p[3] <= ended
                      and (base_seq is None or p[0] > base_seq)]
            for p in during:
                out.append(f"  cyanrip: SUPERSEDED DURING THE RUN -- {p[1]} at "
                           f"{p[2]}, release_seq {p[0]}, was published by {p[4]} "
                           f"at {p[3].isoformat()}, before the run ended")

    # ---- theirs ----
    if app is None:
        out.append("  app: unknown (no app_version in the report and no app in "
                   "COMPONENTS.json), which is NOT newest")
    elif peer is None:
        out.append(f"  app: ran {app}; unknown whether newest (no --peer tree "
                   f"given, and their releases are their tags)")
    elif started is not None:
        tags = peer_releases(peer)
        if tags is None:
            out.append(f"  app: ran {app}; unknown whether newest (no tags "
                       f"readable in {peer})")
        else:
            before = [t for t in tags if t[1] <= started]
            newest = max(before, key=lambda t: t[1]) if before else None
            mine = [t for t in tags if t[0] == f"v{app}"]
            if newest and newest[0] == f"v{app}":
                out.append(f"  app: NEWEST -- ran {app}, tag {newest[0]} of "
                           f"{newest[1].isoformat()}, the newest tag at the "
                           f"run's start (a tag's creator date, not a push)")
            elif mine and mine[0][1] > started:
                out.append(f"  app: NOT YET TAGGED -- ran {app}, whose tag "
                           f"{mine[0][0]} is dated {mine[0][1].isoformat()}, "
                           f"after the run began")
            elif mine:
                out.append(f"  app: STALE -- ran {app}; {newest[0]} is dated "
                           f"{newest[1].isoformat()}, before the run began. Not "
                           f"evidence under D3")
            else:
                out.append(f"  app: NOT A RELEASE -- ran {app}, and {peer} has "
                           f"no tag v{app}")
            base = mine[0][1] if mine else None
            for tag, stamp in sorted((t for t in tags if ended is not None
                                      and started < t[1] <= ended
                                      and (base is None or t[1] > base)),
                                     key=lambda t: t[1]):
                out.append(f"  app: SUPERSEDED DURING THE RUN -- {tag} is "
                           f"dated {stamp.isoformat()}, before the run ended")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archive")
    ap.add_argument("--into", help="directory to file into (docs/rig-...)")
    ap.add_argument("--verdict-only", action="store_true",
                    help="read and report the run's verdict; write nothing")
    ap.add_argument("--peer", help="a clone of Platterpus's repository, whose "
                    "tags say which app release was newest when the run began")
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
    elif lines:
        print("  Nothing here asserts that the run passed or failed: no")
        print("  report.json declares `ok`. This is NOT 'the run passed'.")
    print()

    # ---- 1b. THE PAIR: WAS IT THE NEWEST WHEN THE RUN BEGAN (D3) ---------
    print("=" * 68)
    print("PAIR -- was it the newest pair when the run began (D3)")
    print("=" * 68)
    print("\n".join(report_pair(members, args.peer)))
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
