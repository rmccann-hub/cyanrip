#!/usr/bin/env python3
"""Are both projects holding the SAME rules? Answer before reading their lap.

The four seam documents -- the protocol, the two seam sheets and the ownership
split -- live at a path in EACH repository and neither project owns any of them.
A change is a version bump both sides ship. Restating one faithfully is still a
second spec that can drift, and it already has: round 7 lap 30 found their
protocol copy missing a paragraph ours carried, by diffing rather than assuming.

Until 2026-09-13 the only way to check was to exchange hashes in a lap and hope
both sides computed them over the same thing. That was never the only way -- it
was believed to be, because `CLAUDE.md` asserted "we cannot read their source"
and nobody ran the check. Their repository is public. This tool diffs the real
files.

RUN IT BEFORE READING A LAP OF THEIRS, every time. Two projects agreeing on a
verdict while holding different rulebooks are not agreeing about anything, and
that failure is silent by construction: every test on both sides passes.

WHY THIS IS NOT A MESON TEST, deliberately. It reaches the network, and a check
that reaches the network is not evidence about this program -- it would fail
offline for reasons unrelated to anything either project did. This repository
already has that defect once (docs/SETTLED.md row 84 re-checks a fact about our
own parser by calling accuraterip.com, which is 59% of check-settled's runtime
and times the suite out). Adding a second would be repeating a mistake recorded
in the same week it was found. It is a tool you run, and it names the commit it
read, so its output can be quoted in a lap like any other measurement.

FAILS CLOSED. No peer checkout, a missing file, an unresolvable ref: all exit
non-zero. "Could not check" and "checked and agreed" are different claims, and
collapsing them is the defect this whole seam is built to avoid.
"""

import argparse
import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# The shared documents, and where each side keeps its copy. The paths differ --
# that is layout, not drift -- so the mapping is explicit rather than searched.
# A search would find SOME file and compare it confidently; a missing path
# should be loud, because a moved shared document is itself worth a lap.
SHARED = [
    # (key as spelled in HANDSHAKE-SHARED-HASHES, our path, their path)
    ("protocol",      "docs/handshake/PROTOCOL.md", "docs/handshake-protocol.md"),
    ("seam-rules",    "docs/seam-rules.md",         "docs/seam-rules.md"),
    ("seam-commands", "docs/seam-commands.md",      "docs/seam-commands.md"),
    ("ownership",     "docs/OWNERSHIP.md",          "docs/OWNERSHIP.md"),
]

DEFAULT_PEER = "/home/user/rmccann-hub/platterpus"
PEER_URL = "https://github.com/rmccann-hub/platterpus"

SHARED_HASHES_RE = re.compile(r"(?m)^HANDSHAKE-SHARED-HASHES:[ \t]*(.+?)[ \t]*$")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def newest_lap_hashes():
    """What our most recent lap DECLARED, so a third reading can disagree.

    Two trees agreeing tells you nothing about whether the lap we sent quoted
    those same values -- and a lap is what the other side actually holds.
    """
    laps = sorted(ROOT.glob("docs/handshake/round-*-lap-*.md"))
    for lap in reversed(laps):
        m = SHARED_HASHES_RE.search(lap.read_text(errors="replace"))
        if m:
            out = {}
            for tok in m.group(1).split():
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    out[re.sub(r"\(.*\)$", "", k)] = v
            return lap.name, out
    return None, {}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--peer", default=DEFAULT_PEER,
                    help=f"peer checkout (default {DEFAULT_PEER})")
    ap.add_argument("--fetch", action="store_true",
                    help="git fetch the peer's default branch first")
    args = ap.parse_args()

    peer = pathlib.Path(args.peer)
    if not (peer / ".git").exists():
        print(f"CANNOT CHECK: no peer checkout at {peer}", file=sys.stderr)
        print(f"  GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 {PEER_URL} {peer}",
              file=sys.stderr)
        print("  (public repository; this environment's git proxy serves "
              "anonymous reads)", file=sys.stderr)
        return 2

    rc, origin, _ = git(peer, "remote", "get-url", "origin")
    if rc != 0 or "rmccann-hub/platterpus" not in origin.lower():
        print(f"CANNOT CHECK: {peer} is not the peer repository "
              f"(origin={origin or 'unknown'})", file=sys.stderr)
        print("  A directory is not the right repo because of its NAME.",
              file=sys.stderr)
        return 2

    if args.fetch:
        rc, _, err = git(peer, "fetch", "--depth", "1", "origin", "HEAD")
        if rc != 0:
            print(f"CANNOT CHECK: fetch failed: {err}", file=sys.stderr)
            return 2
        git(peer, "checkout", "-q", "FETCH_HEAD")

    rc, peer_sha, _ = git(peer, "rev-parse", "HEAD")
    if rc != 0:
        print(f"CANNOT CHECK: cannot resolve HEAD in {peer}", file=sys.stderr)
        return 2
    rc, dirty, _ = git(peer, "status", "--porcelain")
    rc, ours_sha, _ = git(ROOT, "rev-parse", "HEAD")

    lap_name, declared = newest_lap_hashes()

    print(f"ours   {ours_sha[:7]}  {ROOT}")
    print(f"theirs {peer_sha[:7]}  {peer}"
          + ("  [WORKING TREE IS DIRTY]" if dirty else ""))
    if lap_name:
        print(f"lap    {lap_name} declares HANDSHAKE-SHARED-HASHES")
    else:
        print("lap    no lap declares HANDSHAKE-SHARED-HASHES")
    print()

    bad = 0
    for key, our_rel, their_rel in SHARED:
        our_p, their_p = ROOT / our_rel, peer / their_rel
        if not our_p.exists():
            print(f"MISSING  {key}: ours    {our_rel}"); bad += 1; continue
        if not their_p.exists():
            print(f"MISSING  {key}: theirs  {their_rel}"); bad += 1; continue

        a, b = sha256(our_p), sha256(their_p)
        d = declared.get(key)
        if a != b:
            print(f"DRIFT    {key}")
            print(f"         ours   {a[:16]}  {our_rel}")
            print(f"         theirs {b[:16]}  {their_rel}")
            bad += 1
        elif d is not None and d != a:
            # Both trees agree and the lap we SENT quoted something else. The
            # other side holds that lap, so this is a live disagreement even
            # though the files match.
            print(f"LAP DISAGREES  {key}: trees {a[:16]}, "
                  f"{lap_name} declared {d[:16]}")
            bad += 1
        else:
            tag = "matches lap" if d is not None else "no lap value"
            print(f"OK       {key:14s} {a[:16]}  ({tag})")

    print()
    if bad:
        print(f"NOT IN SYNC: {bad} of {len(SHARED)} shared document(s) disagree.")
        print("Do not act on their lap until this is resolved -- two projects "
              "agreeing while holding different rulebooks agree about nothing.")
        return 1
    print(f"IN SYNC: all {len(SHARED)} shared documents byte-identical, "
          f"read at platterpus@{peer_sha[:7]}.")
    print("Quote that SHA in any lap that relies on this check: a shallow "
          "clone of a moving branch is a claim about whenever it was fetched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
