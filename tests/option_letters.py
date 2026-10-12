#!/usr/bin/env python3
"""An option this fork adds is long-only, and no short letter collides with
upstream's without a recorded decision.

Upstream allocates short letters and a fork cannot reserve one. `-k` was
--stall-secs here when upstream's b40c1f0 gave it to --acoustid-key, so the
two projects now spell different options `-k`, and the sync had to make
upstream's long-only here. A long name can still collide, but only on the
same word, which a sync's diff of --help shows. So from 2026-10-12 a new fork
option has no short letter (CLAUDE.md, "Watching upstream").

What this checks, against the binary's own --help:

  * the option table read from src/cyanrip_main.c is exactly what the binary
    prints, so the same reader can be trusted on upstream's source;
  * every option upstream does not have is long-only, unless it is one of
    the letters the fork already shipped, which stay: renaming one breaks
    every caller;
  * every upstream option keeps upstream's letter, unless it is recorded as
    long-only here with the reason;
  * no letter is given twice, and upstream's table never takes a letter the
    fork uses outside the table (-V, in src/genopt.h).

UPSTREAM'S TABLE is read at `git merge-base HEAD master` (or origin/master):
the last upstream commit merged, not master's tip, so syncing master ahead
of a merge can never fail this branch. Without that commit, a tarball or a
shallow clone, the upstream half cannot run; the rest still does, and the
test then skips (77) and says what it did not check.
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = "src/cyanrip_main.c"

# The fork's shipped letters. They stay; nothing new joins this list.
FORK_LETTERS = {
    "stall-secs": "k",
    "cache-probe": "x",
    "consumer": "u",
    "diagnostics": "j",
}
# Accepted outside the option table, so the table reader cannot see it.
OUTSIDE_TABLE = {"V": "--version's alias in src/genopt.h, upstream's own "
                      "spelling up to 0.9.3"}
# Upstream options that are long-only here, and why.
LONG_ONLY_HERE = {
    "acoustid-key": "upstream's -k, which was --stall-secs here first",
}
# genopt prints these itself; they are not in the table.
BUILTIN = {"help": "h", "version": "v"}

TABLE = re.compile(r'GEN_OPT_(?!INIT|SEC)[A-Z_]+\(opts_list,\s*[^,]+,\s*'
                   r'(\w+),\s*"(\w?)"')
HELP = re.compile(r"^\s+--([a-z0-9-]+)(?: \(-(.)\))?:", re.M)

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL: " + msg)


def table(src):
    found = {}
    for m in TABLE.finditer(src):
        found[m.group(1).replace("_", "-")] = m.group(2)
    return dict(found, **BUILTIN)


def git(*args):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                       text=True)
    return r.stdout if r.returncode == 0 else None


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: option_letters.py <cyanrip binary>")
    r = subprocess.run([sys.argv[1], "--help"], capture_output=True,
                       text=True)
    shown = {m.group(1): m.group(2) or "" for m in HELP.finditer(r.stdout)}
    if len(shown) < 10:
        fail(f"--help listed {len(shown)} options; the reader is broken or "
             f"the binary printed something else (exit {r.returncode})")
        return 1

    ours = table((ROOT / SRC).read_text())
    if ours != shown:
        diff = {k: (ours.get(k), shown.get(k))
                for k in set(ours) | set(shown) if ours.get(k) != shown.get(k)}
        fail(f"the table read from {SRC} is not what --help prints, so it "
             f"cannot be trusted on upstream's source either: {diff}")

    letters = {}
    for name, letter in shown.items():
        if letter:
            letters.setdefault(letter, []).append(name)
    for letter, names in letters.items():
        if len(names) > 1:
            fail(f"-{letter} is given to {', '.join('--' + n for n in names)}")
        if letter in OUTSIDE_TABLE:
            fail(f"-{letter} is given to --{names[0]}, and is already "
                 f"{OUTSIDE_TABLE[letter]}")

    for name, letter in FORK_LETTERS.items():
        if shown.get(name) != letter:
            fail(f"--{name} was -{letter} and is now {shown.get(name)!r}: a "
                 "shipped letter is never renamed, since every caller using "
                 "it breaks")

    base = None
    for ref in ("master", "origin/master"):
        out = git("merge-base", "HEAD", ref)
        if out:
            base = out.strip()
            break
    upstream = None
    if base:
        src = git("show", f"{base}:{SRC}")
        if src is not None:
            upstream = table(src)
    if upstream is None or len(upstream) < 10:
        print("SKIP (partial): no merged upstream commit to read, so whether "
              "a new option takes a letter, and whether upstream's letters "
              "are kept, was NOT checked; the reader and the fork's shipped "
              "letters were")
        return 1 if failures else 77

    for name, letter in shown.items():
        if name in upstream:
            continue
        if letter and FORK_LETTERS.get(name) != letter:
            fail(f"--{name} takes -{letter}. An option this fork adds is "
                 "long-only (CLAUDE.md, 'Watching upstream'): upstream "
                 "allocates short letters and can take this one in any sync")

    for name, letter in upstream.items():
        here = shown.get(name)
        if name in LONG_ONLY_HERE:
            if not letter:
                fail(f"LONG_ONLY_HERE names --{name}, which upstream no "
                     "longer gives a letter; remove the entry")
            if here != "":
                fail(f"--{name} is recorded long-only here ("
                     f"{LONG_ONLY_HERE[name]}) and has {here!r}")
            continue
        if here is None:
            fail(f"upstream's --{name} is missing here")
        elif here != letter:
            fail(f"upstream gives --{name} "
                 f"{('-' + letter) if letter else 'no letter'}, "
                 f"and here it has {('-' + here) if here else 'none'}; "
                 "decide at the sync and record it in LONG_ONLY_HERE")
        if letter in OUTSIDE_TABLE:
            fail(f"upstream gives -{letter} to --{name}, and here it is "
                 f"{OUTSIDE_TABLE[letter]}")

    added = sorted(n for n in shown if n not in upstream)
    print(f"{len(shown)} options; {len(upstream)} upstream's at "
          f"{base[:7]}; added here: "
          + ", ".join(f"--{n}" + (f" (-{shown[n]})" if shown[n] else "")
                      for n in added)
          + "; long-only here: "
          + ", ".join("--" + n for n in sorted(LONG_ONLY_HERE)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
