#!/usr/bin/env python3
"""An option this fork adds is long-only, and no short letter collides with
upstream's without a recorded decision.

Upstream allocates short letters and a fork cannot reserve one. `-k` was
--stall-secs here when upstream's b40c1f0 gave it to --acoustid-key, so the
two projects now spell different options `-k`, and the sync had to make
upstream's long-only here. A long name can still collide, but only on the
same word, which a sync's diff of --help shows. So from 2026-10-12 a fork
option has no short letter (CLAUDE.md, "Watching upstream"), and the four the
fork had shipped, -j, -k, -u and -x, were retired the same day on the owner's
word, while nobody but the owner used either project.

What this checks, against the binary's own --help:

  * the option table read from src/cyanrip_main.c is exactly what the binary
    prints, so the same reader can be trusted on upstream's source;
  * every option upstream does not have is long-only;
  * the retired letters are given to nothing, and the binary refuses each:
    a letter that meant one thing here must not quietly mean another;
  * every upstream option keeps upstream's letter, unless it is recorded as
    long-only here with the reason;
  * no letter is given twice, and upstream's table never takes a letter the
    fork uses outside the table (-V, in src/genopt.h);
  * the contract's P1, which calls itself every flag, lists every option
    --help prints. Its reader required a "(-x)" and dropped every long-only
    option, --acoustid-key from the upstream merge and the four retired here
    with it, though the consumer reads P1 for --consumer by name.

UPSTREAM'S TABLE is read at `git merge-base HEAD master` (or origin/master):
the last upstream commit merged, not master's tip, so syncing master ahead
of a merge can never fail this branch. Without that commit, a tarball or a
shallow clone, the upstream half cannot run; the rest still does, and the
test then skips (77) and says what it did not check.
"""

import importlib.util
import pathlib
import re
import subprocess
import sys

sys.dont_write_bytecode = True

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = "src/cyanrip_main.c"

# Letters the fork once gave its own options, retired 2026-10-12. Each stays
# unassigned until a decision removes it from here: -k in particular is
# upstream's --acoustid-key, and taking it before old `-k 10` invocations are
# gone would read a stall threshold as an AcoustID key.
RETIRED = {
    "j": "--diagnostics",
    "k": "--stall-secs",
    "u": "--consumer",
    "x": "--cache-probe",
}
# Accepted outside the option table, so the table reader cannot see it.
OUTSIDE_TABLE = {"V": "--version's alias in src/genopt.h, upstream's own "
                      "spelling up to 0.9.3"}
# Upstream options that are long-only here, and why.
LONG_ONLY_HERE = {
    "acoustid-key": "upstream's -k, which was --stall-secs here until "
                    "2026-10-12 and is retired for now (RETIRED)",
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
                       text=True, encoding="utf-8")
    return r.stdout if r.returncode == 0 else None


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: option_letters.py <cyanrip binary>")
    r = subprocess.run([sys.argv[1], "--help"], capture_output=True,
                       text=True, encoding="utf-8")
    shown = {m.group(1): m.group(2) or "" for m in HELP.finditer(r.stdout)}
    if len(shown) < 10:
        fail(f"--help listed {len(shown)} options; the reader is broken or "
             f"the binary printed something else (exit {r.returncode})")
        return 1

    ours = table((ROOT / SRC).read_text(encoding="utf-8"))
    if ours != shown:
        diff = {k: (ours.get(k), shown.get(k))
                for k in set(ours) | set(shown) if ours.get(k) != shown.get(k)}
        fail(f"the table read from {SRC} is not what --help prints, so it "
             f"cannot be trusted on upstream's source either: {diff}")

    spec = importlib.util.spec_from_file_location(
        "gen_provider_contract", ROOT / "tools" / "gen-provider-contract.py")
    gpc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gpc)
    p1 = {row[2][2:]: (row[1] or "")[1:] for row in gpc.flags(sys.argv[1])}
    if p1 != shown:
        diff = {k: (shown.get(k), p1.get(k))
                for k in set(p1) | set(shown) if p1.get(k) != shown.get(k)}
        fail(f"the contract's P1 does not list what --help prints "
             f"(--help, P1): {diff}")

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

    for letter, was in RETIRED.items():
        if letter in letters:
            fail(f"-{letter} is given to --{letters[letter][0]}; it was {was} "
                 "here until 2026-10-12 and is retired (RETIRED)")
        if shown.get(was.lstrip("-")) is None:
            fail(f"{was} is gone; it was renamed from -{letter}, not removed")
        r = subprocess.run([sys.argv[1], f"-{letter}", "1", "-I"],
                           capture_output=True, text=True, encoding="utf-8")
        said = r.stdout + r.stderr
        if r.returncode == 0 or f"-{letter}" not in said:
            fail(f"the binary did not refuse -{letter}, naming it: exit "
                 f"{r.returncode}, {said.strip()[:120]!r}")

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
        if letter:
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
