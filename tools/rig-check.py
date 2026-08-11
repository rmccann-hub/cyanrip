#!/usr/bin/env python3
"""Everything the rig can check WITHOUT re-ripping a disc, in one run.

A full rip costs the better part of an hour and wears the media; almost nothing
either project needs to know actually requires one. This collects the checks
that do not -- argument integrity, the installed build's identity, the audio on
disk against the log that claims it, the two drive probes that read but never
rip -- writes every raw output into one directory, and prints a summary the
operator can paste back.

What it deliberately does NOT do:

  * rip anything, or write into the music library. Every file it creates lands
    under --out. The one cyanrip invocation that would otherwise litter the
    working directory (`-I` announces "Log(s) will be written to:" and means
    it) is given its own -D inside --out.
  * decide whether the rip was good. It reports measurements; the judgement is
    Platterpus's, per the ownership rule.
  * reach the network, except for the one optional manifest check, which is
    skipped rather than failed when it cannot.

Exit status is 0 when nothing FAILED. A skip is not a failure -- "did not run"
and "ran and found nothing" are different claims and the summary keeps them
apart.

Usage:

    tools/rig-check.py --album-dir ~/Music/rips/Artist/Album      # no disc
    tools/rig-check.py --album-dir ... --device /dev/sr0          # + drive
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

OK, FAIL, SKIP, INFO = "OK", "FAIL", "SKIP", "INFO"
results = []


def record(name, status, detail, artifact=None):
    results.append((name, status, detail, artifact))
    mark = {OK: "  ok  ", FAIL: " FAIL ", SKIP: " skip ", INFO: " info "}[status]
    print(f"[{mark}] {name}: {detail}")
    return status


def run(argv, timeout=300, cwd=None):
    """Never raises. A tool that is missing is a skip, not a crash."""
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=timeout, cwd=cwd)
        return p.returncode, p.stdout.decode(errors="replace")
    except FileNotFoundError:
        return None, f"{argv[0]}: not found"
    except subprocess.TimeoutExpired:
        return None, f"{argv[0]}: timed out after {timeout}s"


def save(out, name, text):
    p = out / name
    p.write_text(text, encoding="utf-8")
    return p.name


# ---------------------------------------------------------------- no disc ---

def check_build(out, crip):
    ec, txt = run([crip, "--version"], timeout=180)
    save(out, "version.txt", txt)
    if ec != 0:
        return record("build", FAIL, f"`{crip} --version` exited {ec}: {txt.strip()[:120]}",
                      "version.txt")
    m = re.search(r"^cyanrip (\S+) \(([^)]+)\)", txt, re.M)
    if not m:
        return record("build", FAIL, f"unrecognised banner: {txt.strip()[:120]}", "version.txt")
    ver, tag = m.group(1), m.group(2)
    if "-dirty" in tag:
        return record("build", FAIL, f"{ver} ({tag}) -- built from a tree with "
                      "uncommitted changes, so the SHA does not describe it", "version.txt")
    return record("build", INFO, f"{ver} ({tag})", "version.txt")


def check_manifest(out, crip):
    """Which published channel, if any, is installed. Optional and networked."""
    url = ("https://raw.githubusercontent.com/rmccann-hub/cyanrip/"
           "platterpus-fork/release-manifest.json")
    ec, txt = run(["curl", "-sSL", "--max-time", "20", url], timeout=40)
    if ec != 0:
        return record("manifest", SKIP, "could not fetch (offline is fine)")
    try:
        d = json.loads(txt)
    except Exception as e:
        return record("manifest", SKIP, f"not JSON: {e}")
    save(out, "release-manifest.json", txt)
    chans = d.get("channels", d)
    ec, vtxt = run([crip, "--version"], timeout=180)
    installed = re.search(r"^cyanrip (\S+) ", vtxt or "", re.M)
    installed = installed.group(1) if installed else "?"
    where = [c for c, v in chans.items()
             if isinstance(v, dict) and v.get("version") == installed]
    detail = ", ".join(f"{c}={chans[c]['version']}@{chans[c]['commit']}"
                       for c in chans if isinstance(chans[c], dict))
    if where:
        return record("manifest", OK, f"installed {installed} is channel "
                      f"{'/'.join(where)} | {detail}", "release-manifest.json")
    return record("manifest", INFO, f"installed {installed} matches no published "
                  f"channel | {detail}", "release-manifest.json")


def check_argv(out, crip, container):
    """Does anything between the caller and the binary alter the command line?

    Platterpus's self_check caught `-Z -l` being sent and not received, and
    neither side could tell where they went. -j writes its record from atexit,
    so this needs no disc and no successful run: point it at a device that
    cannot open and read back what argv actually arrived.
    """
    probes = [("shim", [crip])]
    if container and shutil.which("distrobox"):
        probes.append(("direct", ["distrobox", "enter", container, "--",
                                  "/usr/local/bin/cyanrip"]))

    seen = {}
    for label, prefix in probes:
        j = out / f"argv-{label}.json"
        ec, txt = run(prefix + ["-j", str(j), "-Z", "3", "-l", "1,2", "-N",
                                "-d", "/nonexistent.cue"], timeout=240)
        save(out, f"argv-{label}.txt", txt if isinstance(txt, str) else "")
        if not j.exists():
            record(f"argv/{label}", FAIL,
                   "-j wrote no record at all, which is the one job it has "
                   "on a run that fails early")
            continue
        try:
            inv = json.loads(j.read_text()).get("invocation", "")
        except Exception as e:
            record(f"argv/{label}", FAIL, f"diagnostics record unreadable: {e}")
            continue
        seen[label] = inv
        missing = [f for f in ("-Z 3", "-l 1,2") if f not in inv]
        if missing:
            record(f"argv/{label}", FAIL,
                   f"dropped {missing} -- cyanrip received: {inv}",
                   f"argv-{label}.json")
        else:
            record(f"argv/{label}", OK, "-Z and -l both arrived intact",
                   f"argv-{label}.json")

    if len(seen) == 2:
        a, b = seen["shim"], seen["direct"]
        # Compare only the flags, not argv[0] or the -j path, which differ by
        # construction between the two invocations.
        norm = lambda s: re.sub(r"\S*cyanrip\s+-j\s+\S+", "", s).strip()
        if norm(a) == norm(b):
            record("argv/shim-vs-direct", OK, "identical once argv[0] and the "
                   "-j path are normalised out")
        else:
            record("argv/shim-vs-direct", FAIL,
                   f"the shim alters the command line\n    shim  : {a}\n    direct: {b}")
    elif probes and len(seen) < 2:
        record("argv/shim-vs-direct", SKIP,
               "no container given (--container) or distrobox absent, so the "
               "shim could not be compared against the binary")


def find_log(album):
    """The newest rip log at or beside `album`, or a REASON it found none.

    Returns (path, None) or (None, reason). One message for "that directory is
    not there" and "that directory has no log in it" was the same defect this
    script exists to report in other people's output: an absence that can mean
    two things and does not say which. It cost a live rig run, where the
    directory was known to hold a log and the script said only "no rip log
    found under <path>".

    Every path is printed in quotes, because the difference between a real
    failure and a shell that fed us a trailing space is invisible without
    them -- and that is a real possibility, not a hypothetical: a line
    continuation followed by spaces stops continuing the line."""
    if not album.exists():
        # A dead end is not an answer. Album directories here carry characters
        # a path cannot survive being retyped through -- this album's title
        # holds U+2236 RATIO standing in for a colon -- so "does not exist" is
        # far more often a transcription failure than a missing rip, and the
        # operator has no way to tell which from that sentence alone. Name what
        # IS beside it and the next command writes itself.
        near = album.parent
        if near.is_dir():
            sibs = sorted(d.name for d in near.iterdir() if d.is_dir())
            if sibs:
                shown = ", ".join(repr(x) for x in sibs[:6])
                more = f" (+{len(sibs) - 6} more)" if len(sibs) > 6 else ""
                return None, (f"{str(album)!r} does not exist. {str(near)!r} "
                              f"holds: {shown}{more} -- if one of those is the "
                              "album, the name differs by characters a copy-paste "
                              "cannot carry; select it with find rather than "
                              "retyping it")
            return None, (f"{str(album)!r} does not exist, and {str(near)!r} "
                          "holds no directories at all")
        return None, (f"{str(album)!r} does not exist, and neither does its "
                      f"parent {str(near)!r}")
    if not album.is_dir():
        return None, f"{str(album)!r} is not a directory"

    for where, d in (("in", album), ("beside", album.parent)):
        logs = sorted(d.glob("*.log"))
        cands = [p for p in logs if "EACcompatible" not in p.name]
        if cands:
            # The parent fallback exists because -D {album_artist}/{album} can
            # put the log one level up. It is also how an EMPTY album directory
            # silently bound to an unrelated log during this script's own
            # testing, and reported it as the album's. Which directory the log
            # came from is therefore part of the answer, not a detail.
            return (max(cands, key=lambda p: p.stat().st_mtime), where), None
        if logs:
            return None, (f"{len(logs)} .log file(s) {where} {str(d)!r}, but "
                          "every one is an EAC-compatible export, not a rip log")
    n = len(list(album.iterdir()))
    return None, (f"{str(album)!r} exists and holds {n} entr{'y' if n == 1 else 'ies'}, "
                  "but no .log in it or beside it")


def check_verify_log(out, crip, log):
    ec, txt = run([crip, "--verify-log", str(log)], timeout=180)
    save(out, "verify-log.txt", txt)
    if ec == 0:
        return record("verify-log", OK, "the log verifies its own FUN512", "verify-log.txt")
    return record("verify-log", FAIL, f"exit {ec}: {txt.strip()[:160]}", "verify-log.txt")


def check_checksum_inventory(out, log):
    """Count the checksum lines, then check the count against the rule.

    Not against the track count: `Accurip 450:` is printed ONLY where v1 and v2
    both missed (cyanrip_log.c), so a disc with an offset-variant pressing has
    more lines than 3x tracks. We told Platterpus to assert 3x and that was
    wrong -- the near-miss-grep defect, committed inside the warning about it.
    """
    text = log.read_text(encoding="utf-8", errors="replace")
    counts = {k: len(re.findall(rf"^\s+{k}:", text, re.M))
              for k in ("EAC CRC32", "Accurip v1", "Accurip v2", "Accurip 450")}
    tracks = len(re.findall(r"^Track \d+ ripped", text, re.M))
    both_missed = 0
    for blk in re.split(r"^Track \d+ ripped", text, flags=re.M)[1:]:
        v1 = re.search(r"^\s+Accurip v1:.*$", blk, re.M)
        v2 = re.search(r"^\s+Accurip v2:.*$", blk, re.M)
        if v1 and v2 and "accurately ripped" not in v1.group(0) \
                and "accurately ripped" not in v2.group(0):
            both_missed += 1
    want = 3 * tracks + both_missed
    got = sum(counts.values())
    detail = (f"{got} lines ({counts['EAC CRC32']}/{counts['Accurip v1']}/"
              f"{counts['Accurip v2']}/{counts['Accurip 450']}), "
              f"rule says 3x{tracks} + {both_missed} = {want}")
    return record("checksum-inventory", OK if got == want else FAIL, detail)


def check_audio(out, log, album):
    tool = HERE / "audio-checksums.py"
    if not tool.exists():
        return record("audio-vs-log", SKIP,
                      f"{tool} not next to this script -- download it from the "
                      "same commit and re-run")
    ec, st = run([sys.executable, str(tool), "self-test"], timeout=120)
    if ec != 0:
        return record("audio-vs-log", SKIP,
                      "the checksum tool fails its own self-test, so nothing "
                      "it says about the files would mean anything")
    if not shutil.which("ffmpeg"):
        return record("audio-vs-log", SKIP, "ffmpeg not installed")

    flacs = sorted(album.glob("*.flac"))
    if not flacs:
        return record("audio-vs-log", SKIP, f"no .flac files in {album}")

    lines, differ, checked = [], [], 0
    for f in flacs:
        m = re.match(r"^(\d+)", f.name)
        if not m:
            continue
        n = int(m.group(1))
        ec, txt = run([sys.executable, str(tool), "check", "--log", str(log),
                       "--track", str(n), str(f)], timeout=300)
        lines.append(f"=== track {n}: {f.name} ===\n{txt}")
        checked += 1
        if ec != 0:
            differ.append(n)
    save(out, "audio-vs-log.txt", "\n".join(lines))

    # A track whose file was replaced after the log was written MUST differ --
    # the log describes the read that was thrown away. So a mismatch is not by
    # itself a defect, and this reports rather than judges.
    #
    # Which is exactly why a difference is INFO and not OK. The script cannot
    # tell a superseded track from a corrupted one; only the consumer that did
    # the superseding knows which tracks it replaced. Grading it OK would put
    # a reassuring word on a line whose detail says two files do not match
    # their log, and a reader who greps the status is entitled to believe the
    # status.
    if differ:
        return record("audio-vs-log", INFO,
                      f"{checked} track(s) checked; differ: "
                      f"{', '.join(map(str, differ))} -- expected for any track "
                      "a re-rip superseded, a finding for any track it did not",
                      "audio-vs-log.txt")
    return record("audio-vs-log", OK,
                  f"{checked} track(s) checked; every one matches its log",
                  "audio-vs-log.txt")


# -------------------------------------------------------------- with disc ---

def check_cache_probe(out, crip, device):
    """-x, and -j for a complete record. Read-only: rips nothing, writes no
    audio. -D keeps the logfile -I announces inside --out instead of cwd."""
    j = out / "cache-probe.diagnostics.json"
    ec, txt = run([crip, "-x", "-j", str(j), "-I", "-N", "-d", device,
                   "-D", str(out / "probe-out")], timeout=600)
    save(out, "cache-probe.txt", txt if isinstance(txt, str) else "")
    m = re.search(r"^Cache probe:\s+(.*)$", txt or "", re.M)
    if not m:
        return record("cache-probe", FAIL,
                      f"no `Cache probe:` line (exit {ec})", "cache-probe.txt")
    return record("cache-probe", INFO, m.group(1), "cache-probe.txt")


def check_offset(out, crip, device):
    ec, txt = run([crip, "-f", "-d", device], timeout=900)
    save(out, "offset-autodetect.txt", txt if isinstance(txt, str) else "")
    m = re.search(r"^Drive offset of ([+-]\d+) found \(confidence: (\d+)\)", txt or "", re.M)
    if not m:
        return record("offset", INFO,
                      "no offset reported -- 'searched and did not find' is a "
                      "result, not a failure", "offset-autodetect.txt")
    return record("offset", INFO, f"{m.group(1)} at confidence {m.group(2)}",
                  "offset-autodetect.txt")


def check_cdparanoia_cache(out, device):
    """The only independent cross-check our -x number has ever had.

    cyanrip's probe has produced exactly one measurement in its existence and
    nothing corroborates it. cd-paranoia -A does its own cache analysis by a
    related method, so a wild disagreement is a finding about our probe.
    """
    exe = shutil.which("cd-paranoia") or shutil.which("cdparanoia")
    if not exe:
        return record("cdparanoia-cache", SKIP, "cd-paranoia not installed")
    ec, txt = run([exe, "-A", "-d", device], timeout=900)
    save(out, "cdparanoia-A.txt", txt if isinstance(txt, str) else "")
    m = re.search(r"cache.*?(\d+)\s*sector", txt or "", re.I | re.S)
    return record("cdparanoia-cache", INFO,
                  f"{m.group(1)} sectors reported" if m else
                  "ran; no sector figure matched -- read the file",
                  "cdparanoia-A.txt")


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--album-dir", type=Path,
                    help="a finished rip: its .log and .flac files")
    ap.add_argument("--device", help="e.g. /dev/sr0. Omit to skip every drive check.")
    ap.add_argument("--binary", default=os.path.expanduser("~/.local/bin/cyanrip"),
                    help="the cyanrip a caller would actually invoke (default: the shim)")
    ap.add_argument("--container", default="ripping",
                    help="distrobox container holding the real binary, for the "
                         "shim-vs-direct argv comparison")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    crip = args.binary if (os.path.sep in args.binary) else (shutil.which(args.binary) or args.binary)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out = args.out or Path.home() / f"seam-check-{stamp}"
    out.mkdir(parents=True, exist_ok=True)
    print(f"cyanrip rig check -- output in {out}\n")

    check_build(out, crip)
    check_manifest(out, crip)
    check_argv(out, crip, args.container)

    if args.album_dir:
        album = args.album_dir.expanduser()
        found, why = find_log(album)
        if not found:
            record("album", SKIP, why)
        else:
            log, where = found
            record("album", INFO, f"log: {str(log)!r}" + (
                "" if where == "in" else
                "  <- NOT in the album directory, found BESIDE it; check this "
                "is the right album's log"))
            check_verify_log(out, crip, log)
            check_checksum_inventory(out, log)
            check_audio(out, log, album)
    else:
        record("album", SKIP, "no --album-dir given")

    if args.device:
        check_cache_probe(out, crip, args.device)
        check_offset(out, crip, args.device)
        check_cdparanoia_cache(out, args.device)
    else:
        for n in ("cache-probe", "offset", "cdparanoia-cache"):
            record(n, SKIP, "no --device given, so no drive check ran")

    manifest = [f"cyanrip rig check {stamp}",
                f"binary: {crip}",
                f"album:  {args.album_dir}",
                f"device: {args.device}", ""]
    for name, status, detail, artifact in results:
        manifest.append(f"{status:5}  {name:22}  {detail}"
                        + (f"   [{artifact}]" if artifact else ""))
    (out / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    n_fail = sum(1 for r in results if r[1] == FAIL)
    n_skip = sum(1 for r in results if r[1] == SKIP)
    print(f"\n{len(results)} check(s): {n_fail} failed, {n_skip} skipped.")
    print(f"Upload the whole directory: {out}")
    print(f"  tar czf {out.name}.tar.gz -C {out.parent} {out.name}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
