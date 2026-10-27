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

"""Resolve a Platterpus commit ID through Platterpus's commit maps (HR-1.6).

HR-1 (`docs/handshake/HR-1.md`, adopted word for word by both sides) records
that Platterpus rewrote its history once, so every Platterpus commit has a new
ID, and that old IDs stay as sent in every lap and record. An old ID resolves
through `docs/handshake/commit-map-<YYYY-MM-DD>.txt` in Platterpus's tree. This
is the one reading of those maps in this repository: `tools/lap-statements.py`
resolves every Platterpus value through `resolve()`, and
`tools/seam-sync-check.py` reports a map that does not read cleanly.

The rule, step by step as HR-1.6 states it:

  (a) every commit-map-*.txt in docs/handshake, oldest date first;
  (b) exactly one old ID beginning with <x>: <x> names its new ID, and a new ID
      that is an old ID in a later map is followed, at most 16 times;
  (c) no old ID beginning with <x>: resolve <x> in the clone as before; two or
      more: <x> names no commit;
  (d) (b) before (c), because a clone made before the rewrite still holds the
      old objects;
  (f) a map that does not read cleanly is reported, never guessed at.

The maps are read from the clone's ref of record when one is given, so a
working tree checked out somewhere else does not decide what the record says,
and from the working tree otherwise. It applies to Platterpus's tree only: a
cyanrip ID is never looked up in it.

    commit-map.py --check CLONE [--ref REF]   exit 0 clean or no map, 1 not clean
    commit-map.py CLONE X [--ref REF]         print what X names
"""

import argparse
import re
import subprocess
import sys

MAP_DIR = "docs/handshake"
MAP_NAME = re.compile(r"^commit-map-(\d{4}-\d{2}-\d{2})\.txt$")
HEADER = re.compile(r"^old +new$")
LINE = re.compile(r"^([0-9a-f]{40}) ([0-9a-f]{40})$")
VALUE = re.compile(r"^[0-9a-f]{7,40}$")
MAX_FOLLOW = 16


class MapError(Exception):
    """A map that does not read cleanly (HR-1.6 (f))."""


def _git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       text=True, encoding="utf-8")
    return r.returncode, r.stdout


def read_maps(repo, ref=None):
    """[(name, text)] of every map, oldest date first. From `ref`'s tree when
    `ref` resolves, else from the working tree."""
    found = []
    if ref is not None and _git(repo, "rev-parse", "--verify", "--quiet",
                                f"{ref}^{{commit}}")[0] == 0:
        rc, out = _git(repo, "ls-tree", "--name-only", f"{ref}:{MAP_DIR}")
        if rc == 0:
            for name in out.splitlines():
                if MAP_NAME.match(name):
                    rc2, text = _git(repo, "show", f"{ref}:{MAP_DIR}/{name}")
                    if rc2 != 0:
                        raise MapError(f"{name} is listed at {ref} and cannot "
                                       f"be read")
                    found.append((name, text))
        return sorted(found, key=lambda m: (MAP_NAME.match(m[0]).group(1),
                                            m[0]))
    import pathlib
    d = pathlib.Path(repo) / MAP_DIR
    if d.is_dir():
        for p in d.iterdir():
            if MAP_NAME.match(p.name):
                found.append((p.name, p.read_bytes().decode("utf-8", "replace")))
    return sorted(found, key=lambda m: (MAP_NAME.match(m[0]).group(1), m[0]))


def read_maps_from(repo, refs):
    """read_maps() over every ref in `refs`, merged by file name.

    A clone's refs of record can disagree about the maps: a local `main` from
    before the rewrite carries none while `origin/main` carries them. Reading
    the first ref alone missed them, and an old ID then resolved in the clone
    against HR-1.6 (d), refused as on no branch in one clone and accepted in
    another (Platterpus round 32 lap 4 S9). A map is append-only, so every ref
    of record is read and the union kept. The same file reading differently on
    two refs is not guessed at: it is a map that does not read cleanly
    (HR-1.6 (f)). With no refs, the working tree is read."""
    if not refs:
        return read_maps(repo)
    merged, where = {}, {}
    for ref in refs:
        for name, text in read_maps(repo, ref):
            if name in merged and merged[name] != text:
                raise MapError(f"{name} reads differently at {where[name]} "
                               f"and at {ref}")
            merged.setdefault(name, text)
            where.setdefault(name, ref)
    return sorted(merged.items(), key=lambda m: (MAP_NAME.match(m[0]).group(1),
                                                 m[0]))


def parse(maps):
    """[(name, {old: new})] in the order given, or MapError naming the first
    defect HR-1.6 (f) lists."""
    parsed, seen_old = [], {}
    for name, text in maps:
        lines = text.split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        if not lines or not HEADER.match(lines[0]):
            raise MapError(f"{name}: the first line is "
                           f"{(lines[0] if lines else '')!r}, not 'old new'")
        table, news = {}, set()
        for n, line in enumerate(lines[1:], 2):
            m = LINE.match(line)
            if not m:
                raise MapError(f"{name}:{n}: {line[:60]!r} is not an old ID, one "
                               f"space and a new ID, each 40 lowercase hex")
            old, new = m.groups()
            if old == new:
                raise MapError(f"{name}:{n}: {old} is mapped to itself")
            if old in table:
                raise MapError(f"{name}:{n}: old ID {old} is listed twice")
            if old in seen_old:
                raise MapError(f"{name}:{n}: old ID {old} is listed twice, "
                               f"also in {seen_old[old]}")
            table[old] = new
            news.add(new)
        both = sorted(set(table) & news)
        if both:
            raise MapError(f"{name}: {both[0]} is both an old ID and a new ID")
        for old in table:
            seen_old[old] = name
        parsed.append((name, table))
    return parsed


def resolve(parsed, x):
    """What `x` names through the maps: ("mapped", new_id, note),
    ("none", None, note) when no old ID begins with it, so it resolves in the
    clone as before, or ("ambiguous", None, note) when it names no commit."""
    if not VALUE.match(x):
        return "none", None, f"{x!r} is not 7 to 40 lowercase hex"
    hits = [(i, old) for i, (_, table) in enumerate(parsed)
            for old in table if old.startswith(x)]
    if not hits:
        return "none", None, "no old ID in the maps begins with it"
    if len(hits) > 1:
        names = ", ".join(f"{old[:12]} ({parsed[i][0]})" for i, old in hits[:3])
        return "ambiguous", None, (f"{len(hits)} old IDs in the maps begin with "
                                   f"{x} ({names}), so it names no commit "
                                   f"(HR-1.6 (c))")
    i, old = hits[0]
    new = parsed[i][1][old]
    via = [parsed[i][0]]
    for _ in range(MAX_FOLLOW):
        later = [(j, t[new]) for j, (_, t) in enumerate(parsed)
                 if j > i and new in t]
        if not later:
            break
        i, new = later[0]
        via.append(parsed[i][0])
    else:
        if any(j > i and new in t for j, (_, t) in enumerate(parsed)):
            return "ambiguous", None, (f"{x} is still an old ID after "
                                       f"{MAX_FOLLOW} maps were followed "
                                       f"(HR-1.6 (b))")
    return "mapped", new, f"{x} is old ID {old}, new ID {new} by {', '.join(via)}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("clone")
    ap.add_argument("x", nargs="?")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--ref")
    a = ap.parse_args()
    try:
        parsed = parse(read_maps(a.clone, a.ref))
    except MapError as e:
        print(f"commit-map: NOT CLEAN: {e} (HR-1.6 (f))", file=sys.stderr)
        return 1
    if a.check or a.x is None:
        total = sum(len(t) for _, t in parsed)
        print(f"commit-map: {len(parsed)} map(s), {total} old ID(s), clean"
              + ("".join(f"\n  {n}: {len(t)}" for n, t in parsed)))
        return 0
    verdict, new, note = resolve(parsed, a.x)
    print(f"{verdict}: {new or '-'} ({note})")
    return 1 if verdict == "ambiguous" else 0


if __name__ == "__main__":
    sys.exit(main())
