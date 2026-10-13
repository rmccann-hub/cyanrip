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

"""Take in one of Platterpus's laps: read it from their tree, file it, check it.

WHY. Taking in a lap is the same nine steps every time, and they lived in no
file. Each was rebuilt from the last session's history: fetch their `main`,
find the lap, compare it with the operator's announcement, refuse it while it is
held, file it byte for byte, re-derive its digest and every hash it quotes,
run the lap checker with their tree as its peer, diff the shared documents, and
compare every lap of the round across both trees. In round 32 lap 6 the digest
and the quoted hashes were re-derived by hand while `tools/seam-check.py`, which
does exactly that, went unused, because nothing pointed at it.

So this runs the tools that already exist, in order, and prints each one's
command and verdict. It re-implements none of their rules: a second copy of a
rule is how two readers of one record come to disagree.

IT FAILS CLOSED. A held lap is refused and not filed (§5c). A mismatch with
the announcement is refused. An existing inbound file with different bytes is
refused, because a sent lap is immutable on both sides. A check that cannot run
is a failure, not a skip.

Usage:
    tools/take-in-lap.py ROUND LAP                       # read and check only
    tools/take-in-lap.py ROUND LAP --file                # and file it
    tools/take-in-lap.py ROUND LAP --sha256 HEX --bytes N --file
"""

import argparse
import hashlib
import importlib.util
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HS = ROOT / "docs" / "handshake"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SYNC = _load("seam_sync_check", "seam-sync-check.py")
GATE = _load("release_gate", "release-gate.py")

PEER_OUTBOUND = "docs/handshake/outbound"
PEER_INBOUND = "docs/handshake/inbound"
# The value without its surrounding blanks, in a form linear in a run of
# them (tests/tool_patterns.py); the gate's NEXT_LAP_DECL_RE has the same.
FIELD_RE = re.compile(r"^HANDSHAKE-([A-Z-]+):[ \t]*"
                      r"((?:[^ \t\n](?:[^\n]*[^ \t\n])?)?)[ \t]*$", re.M)
SHOWN = ("PROTOCOL", "ROUND", "LAP", "FROM", "VERDICT", "READY-TO-READ",
         "NEXT-LAP")


def git(repo, *args, binary=False):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    out = r.stdout if binary else r.stdout.decode("utf-8", errors="replace")
    return r.returncode, out


def name_of(rnd, lap):
    return f"round-{rnd:02d}-lap-{lap:02d}.md"


def fields(text):
    """Each HANDSHAKE- field declared at column 0, outside a fence, as a list
    of values: two values is ambiguous and is shown as such, never picked."""
    out = {}
    for k, v in FIELD_RE.findall(GATE.strip_fences(text)):
        out.setdefault(k, []).append(v)
    return out


def ready(fl):
    """True only for exactly one declaration whose value opens with `yes`."""
    vals = fl.get("READY-TO-READ", [])
    return len(vals) == 1 and re.match(r"yes\b", vals[0]) is not None


class Report:
    def __init__(self):
        self.failed = 0

    def line(self, ok, what, detail=""):
        tag = "OK  " if ok else "FAIL"
        if not ok:
            self.failed += 1
        print(f"  {tag}  {what}" + (f": {detail}" if detail else ""))

    def run(self, what, cmd, ok_codes=(0,), cwd=ROOT):
        print(f"\n  $ {' '.join(str(c) for c in cmd)}")
        r = subprocess.run([str(c) for c in cmd], capture_output=True,
                           text=True, cwd=cwd)
        tail = (r.stdout + r.stderr).strip().splitlines()[-4:]
        for t in tail:
            print(f"      {t[:160]}")
        self.line(r.returncode in ok_codes, what, f"exit {r.returncode}")
        return r


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("round", type=int)
    ap.add_argument("lap", type=int)
    ap.add_argument("--peer", default=SYNC.DEFAULT_PEER,
                    help=f"a clone of Platterpus (default {SYNC.DEFAULT_PEER})")
    ap.add_argument("--no-fetch", action="store_true",
                    help="read the clone's origin/main as it is, without "
                         "fetching first; the report then says so")
    ap.add_argument("--sha256", help="the hash the announcement gives")
    ap.add_argument("--bytes", type=int, help="the size the announcement gives")
    ap.add_argument("--file", action="store_true",
                    help="write it to docs/handshake/inbound/ byte for byte")
    ap.add_argument("--laps", default=str(HS),
                    help="our record: ours in DIR, theirs in DIR/inbound "
                         "(default docs/handshake); a test points it at a "
                         "scratch copy so nothing real is written")
    args = ap.parse_args()
    hs = pathlib.Path(args.laps)

    peer = pathlib.Path(args.peer)
    name = name_of(args.round, args.lap)
    rep = Report()
    print(f"TAKING IN {name} from {peer}")

    if not (peer / ".git").exists():
        print(f"  CANNOT: no clone at {peer}. "
              f"git clone {SYNC.PEER_URL} {peer}", file=sys.stderr)
        return 2
    if not args.no_fetch:
        rc, _ = git(peer, "fetch", "-q", "origin", SYNC.PEER_REF)
        if rc != 0:
            print("  CANNOT: fetch failed; nothing read", file=sys.stderr)
            return 2
    ref = f"origin/{SYNC.PEER_REF}"
    _, tip = git(peer, "log", "-1", "--format=%h %cI", ref)
    print(f"  their {ref} is {tip.strip()}"
          + (" (NOT fetched: a cached ref, not the remote)" if args.no_fetch
             else ", fetched just now"))

    # ---- 1. THE LAP, AS THEIR TREE HOLDS IT ------------------------------
    rc, data = git(peer, "show", f"{ref}:{PEER_OUTBOUND}/{name}", binary=True)
    if rc != 0:
        print(f"  {name} is not in their {PEER_OUTBOUND} at {ref}; nothing "
              f"to take in")
        return 1
    _, added = git(peer, "log", "-1", "--format=%h %cI", ref, "--",
                   f"{PEER_OUTBOUND}/{name}")
    digest = hashlib.sha256(data).hexdigest()
    text = data.decode("utf-8", errors="replace")
    fl = fields(text)
    print(f"  last changed at {added.strip()}")
    print(f"  {len(data):,} bytes, sha256 {digest}")
    for k in SHOWN:
        v = fl.get(k)
        shown = "ABSENT" if not v else (v[0] if len(v) == 1
                                       else f"AMBIGUOUS {v}")
        print(f"  {k:14} {shown[:150]}")

    print()
    rep.line(fl.get("ROUND") == [str(args.round)]
             and fl.get("LAP") == [str(args.lap)],
             "it declares the round and lap its name says")
    rep.line(fl.get("FROM") == ["platterpus"], "it says it is from platterpus")
    if args.sha256:
        rep.line(args.sha256.lower() == digest, "sha256 matches the "
                 "announcement", args.sha256 if args.sha256.lower() != digest
                 else "")
    if args.bytes is not None:
        rep.line(args.bytes == len(data), "size matches the announcement",
                 f"{args.bytes:,} announced" if args.bytes != len(data) else "")
    if not ready(fl):
        rep.line(False, "released for reading (§5c)",
                 "held, or undeclared: not filed, not checked, not acted on")
        return 1
    rep.line(True, "released for reading (§5c)")
    if rep.failed:
        print("\nREFUSED before filing: fix the mismatch above first")
        return 1

    # ---- 2. FILE IT ------------------------------------------------------
    dest = hs / "inbound" / name
    if dest.exists():
        same = dest.read_bytes() == data
        rep.line(same, f"already filed at {dest}",
                 "" if same else "WITH DIFFERENT BYTES: a sent lap is "
                 "immutable, so this is refused and nothing is overwritten")
        if not same:
            return 1
    elif args.file:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        rep.line(dest.read_bytes() == data, f"filed byte for byte at {dest}")
    else:
        print(f"\n  not filed (no --file); the checks below read a scratch "
              f"copy and say nothing about our record")
    checked = dest if dest.exists() else None
    if checked is None:
        import tempfile
        tmp = pathlib.Path(tempfile.mkdtemp()) / name
        tmp.write_bytes(data)
        checked = tmp

    # ---- 3. THE CHECKS THAT ALREADY EXIST --------------------------------
    py = sys.executable
    rep.run("seam-check: wire fields, digest, pins, shared hashes, and every "
            "hash it quotes back at us",
            [py, "tools/seam-check.py", "--held", checked])
    rep.run("lap checker, their tree as its peer",
            [py, "tools/lap-statements.py", checked, "--peer", peer])
    rep.run("shared documents byte-identical in both trees",
            [py, "tools/seam-sync-check.py", "--peer", peer]
            + ([] if args.no_fetch else ["--fetch"]))

    # Every lap of the round, in both trees. Ours live in their inbound/,
    # theirs in their outbound/; a lap either side changed after sending
    # shows here and nowhere else.
    print()
    pairs = 0
    for ours in sorted(hs.glob(f"round-{args.round:02d}-lap-*.md")):
        rc, theirs = git(peer, "show", f"{ref}:{PEER_INBOUND}/{ours.name}",
                         binary=True)
        if rc != 0:
            print(f"        ours {ours.name}: not in their {PEER_INBOUND} "
                  f"(not sent yet, or not filed by them yet)")
            continue
        pairs += 1
        rep.line(theirs == ours.read_bytes(),
                 f"ours {ours.name} is byte-identical in their tree")
    for held in sorted((hs / "inbound").glob(f"round-{args.round:02d}-lap-*.md")):
        rc, theirs = git(peer, "show", f"{ref}:{PEER_OUTBOUND}/{held.name}",
                         binary=True)
        pairs += 1
        rep.line(rc == 0 and theirs == held.read_bytes(),
                 f"theirs {held.name} is byte-identical to their outbound")
    print(f"        {pairs} pair(s) compared")

    # The gate's line for the round, verbatim: the authority on its state.
    r = subprocess.run([py, "tools/release-gate.py"], capture_output=True,
                       text=True, cwd=ROOT)
    print()
    inside = False
    for ln in r.stdout.splitlines():
        if re.match(r"\s+round \d+ \(", ln):
            inside = re.match(rf"\s+round {args.round} \(", ln) is not None
        elif not ln.strip():
            inside = False
        if inside and not ln.strip().startswith("close-by:"):
            print(f"  gate  {ln.strip()[:200]}")

    print(f"\n{'ALL CHECKS PASS' if not rep.failed else f'{rep.failed} CHECK(S) FAILED'}"
          f" for {name} at their {tip.split()[0] if tip else ref}")
    return 0 if not rep.failed else 1


if __name__ == "__main__":
    sys.exit(main())
