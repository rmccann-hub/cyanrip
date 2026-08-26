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

"""Break the program on purpose and find out which breakages nothing notices.

WHY THIS AND NOT MORE TESTS. Every test in this suite is an EXAMPLE: run this
input, assert that output. Examples find the bugs somebody thought of. **A
surviving mutant is a bug nobody thought of** -- a change to the program that
every test agrees is fine. That is the only technique here that finds a gap
BEFORE a defect walks through it, which is the difference between "we test a
lot" and "we would have caught it".

It also answers the other half: **a test that never kills any mutant is doing
nothing**, and this is how you find that out without arguing about it.

HOW A MUTANT IS JUDGED, and the asymmetry matters:

  KILLED     some test failed. The suite covers this line's behaviour.
  SURVIVED   the whole suite passed with the program changed. **A GAP.**
  STILLBORN  it did not compile, so it was never a valid mutant. Not evidence.
  TIMEOUT    the change hung something. Reported separately -- a hang is not a
             pass and must never be counted as one.

STAGED, because most mutants die cheaply and the stages differ by fifty-fold:

  1. the sub-second C unit tests            ~0.5s
  2. the disc-image rip suite               ~13s   only if 1 passed
  3. every remaining test                   ~26s   only if 2 passed

Stage 3 exists so that "SURVIVED" means *every test we have*, not "every test I
thought to run". Excluding a slow test from the sweep would silently promote the
mutants only that test kills into the survivor list, and a false gap costs more
to chase than the 26 seconds costs to rule out.

ONE TEST IS EXCLUDED, AND THE REASON GENERALISES. `contract_build` compares
PROVIDER-CONTRACT.md's source anchor -- a sha256 over `src/*.c` and `src/*.h` --
against the live tree, so it fails on ANY byte changed in src/, behaviour or
not. **A test that hashes the source detects the edit, not the defect**, and
leaving it in makes the whole measurement vacuous: the first sweep run here
scored 100% over 100 mutants and the number meant nothing, because every mutant
that got past stage 1 was killed by that one hash. It was found by making a
behaviourally inert edit (a comment appended at EOF, moving no line number) and
asking which tests failed. Exactly one did.

That check is EXCLUDED_TESTS below, derived-and-named rather than filtered by a
pattern, and the exclusion is printed on every run. If another source-hashing
check is ever added, this sweep silently returns to reporting 100% -- so the
probe above is worth repeating rather than trusting this comment.

SAFETY. `src/` is restored from git after every mutant and verified clean at the
end. If this is interrupted, run `git status` before trusting the tree -- and
the final line says whether it verified.

    tools/mutate.py                     # every target file
    tools/mutate.py src/fun512.c        # one
    tools/mutate.py --limit 20          # bounded
"""

import argparse
import pathlib
import random
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Stage 1, named individually. `--no-suite images` would be shorter and would
# also pull in `Argv surface probe`, which is 25 of the 26 seconds the whole
# suite costs -- putting the most expensive test in the cheapest stage. These
# are the tests that link the C directly and finish in hundredths of a second.
FAST_TESTS = [
    "FUN512 checksum", "Naming schemes", "Q sub-channel decoding",
    "Cue pre-gap decision", "Peak cross-check", "Diagnostics retention",
    "Cache probe wording", "Audio checksum mirror", "Log rendering",
]

# See the header. Each entry needs a reason, and the reason must be that the
# check fires on the EDIT rather than on the BEHAVIOUR -- never that it is slow,
# flaky or inconvenient.
EXCLUDED_TESTS = {
    "contract_build": "hashes src/ into the contract's source anchor, so it "
                      "fails on any byte changed in src/ whether or not the "
                      "program behaves differently",
}


def image_scenarios():
    """The images suite, read from tests/meson.build so it cannot go stale."""
    text = (ROOT / "tests" / "meson.build").read_text(encoding="utf-8")
    block = re.search(r"rip_scenarios = \[(.*?)\]", text, re.S)
    if not block:
        raise SystemExit("mutate: no rip_scenarios list in tests/meson.build")
    names = re.findall(r"'([a-z0-9_]+)'", block.group(1))
    return [n for n in names if n not in EXCLUDED_TESTS]

# The files whose correctness the ARCHIVAL RECORD depends on. Not every file:
# a mutant in an unreachable branch teaches nothing, and this list is where a
# wrong answer becomes a wrong claim about a disc that may never be read again.
TARGETS = [
    "src/fun512.c",         # the log's own checksum footer
    "src/accurip.c",        # the checksums a consumer trusts
    "src/discid.c",         # the identity of the disc
    "src/pregap.c",         # sub-channel pregap search
    "src/cue_writer.c",     # INDEX 00 / PREGAP emission
    "src/cyanrip_log.c",    # the record itself
    "src/cache_probe.c",    # the -x measurement
    "src/cyanrip_main.c",   # the rip loop and -Z convergence
    "src/cyanrip_encode.c", # decode -> filter -> encode
]

# Operators chosen to COMPILE reliably. A stillborn mutant costs a build and
# teaches nothing, so swapping a relation or a boolean connective beats deleting
# a statement, which usually fails to compile or changes types.
MUTATIONS = [
    (r"(?<![<>=!])<=(?!=)", "<",  "<= to <"),
    (r"(?<![<>=!])>=(?!=)", ">",  ">= to >"),
    (r"(?<![<>=!+\-*/])<(?![=<])", "<=", "< to <="),
    (r"(?<![<>=!+\-*/])>(?![=>])", ">=", "> to >="),
    (r"(?<![<>=!])==(?!=)", "!=", "== to !="),
    (r"(?<![<>=!])!=(?!=)", "==", "!= to =="),
    (r"&&", "||", "&& to ||"),
    (r"\|\|", "&&", "|| to &&"),
]

# Lines a mutation must not touch: a preprocessor line can break the build in
# ways that are about the mutation tool and not about the tests, and a comment
# or a string literal is not program behaviour at all.
SKIP_LINE = re.compile(r"^\s*#|^\s*\*|^\s*/\*|^\s*//")


def run(cmd, timeout=300):
    try:
        return subprocess.run(cmd, cwd=ROOT, capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def candidates(relpath):
    """Every (line index, column, replacement, label) this file admits."""
    text = (ROOT / relpath).read_text(encoding="utf-8", errors="replace")
    out = []
    in_block_comment = False
    for i, line in enumerate(text.splitlines()):
        stripped = line.strip()
        if "/*" in line and "*/" not in line:
            in_block_comment = True
        if in_block_comment:
            if "*/" in line:
                in_block_comment = False
            continue
        if SKIP_LINE.match(line) or not stripped:
            continue
        # Strip string literals so a `>` inside a format string is not a
        # candidate: mutating one changes output text, the suite screams, and
        # the "kill" says nothing about whether the LOGIC is covered.
        masked = re.sub(r'"(?:[^"\\]|\\.)*"', lambda m: " " * len(m.group(0)), line)
        if "//" in masked:
            masked = masked[:masked.index("//")] + " " * (len(masked) - masked.index("//"))
        for pat, repl, label in MUTATIONS:
            for m in re.finditer(pat, masked):
                out.append((i, m.start(), m.end(), repl, label))
    return out


def apply_mutation(relpath, mut):
    i, a, b, repl, _ = mut
    p = ROOT / relpath
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    line = lines[i]
    lines[i] = line[:a] + repl + line[b:]
    p.write_text("".join(lines), encoding="utf-8")


def restore(relpath):
    run(["git", "checkout", "--", relpath])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", default=None)
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after this many valid mutants")
    ap.add_argument("--seed", type=int, default=20260826)
    ap.add_argument("--count", action="store_true",
                    help="report the pool size per file and exit, so a sweep "
                         "is costed before it is started")
    args = ap.parse_args()

    if args.count:
        total = 0
        for t in (args.files or TARGETS):
            n = len(candidates(t))
            total += n
            print(f"{n:5d}  {t}")
        print(f"{total:5d}  TOTAL  (~14s each staged, ~{total*14/60:.0f} min "
              f"if none survives to stage 3)")
        return 0

    dirty = run(["git", "status", "--porcelain", "src/"]).stdout.strip()
    if dirty:
        print("REFUSING: src/ has uncommitted changes. This tool restores from "
              "git after every mutant and would destroy them.")
        return 2

    targets = args.files or TARGETS
    pool = []
    for t in targets:
        for mut in candidates(t):
            pool.append((t, mut))
    random.Random(args.seed).shuffle(pool)
    if args.limit:
        pool = pool[:args.limit]

    images = image_scenarios()
    print(f"{len(pool)} mutant(s) across {len(targets)} file(s)")
    for name, why in sorted(EXCLUDED_TESTS.items()):
        print(f"EXCLUDED: {name} -- {why}")
    print(f"stage 2 runs {len(images)} image scenario(s)\n")

    killed = stillborn = survived = timeout = 0
    survivors = []
    t0 = time.time()

    try:
        for n, (relpath, mut) in enumerate(pool, 1):
            i, a, _, repl, label = mut
            src_line = (ROOT / relpath).read_text().splitlines()[i].strip()[:72]
            apply_mutation(relpath, mut)

            b = run(["ninja", "-C", "build"], timeout=180)
            if b is None:
                timeout += 1
                restore(relpath)
                continue
            if b.returncode != 0:
                stillborn += 1
                restore(relpath)
                continue

            stages = [
                (["meson", "test", "-C", "build", "--maxfail", "1"]
                 + FAST_TESTS, 120),
                (["meson", "test", "-C", "build", "--suite", "images",
                  "--maxfail", "1"] + images, 600),
                (["meson", "test", "-C", "build", "--no-suite", "images",
                  "--maxfail", "1"], 900),
            ]
            verdict = "survived"
            for cmd, tmo in stages:
                r = run(cmd, timeout=tmo)
                if r is None:
                    verdict = "timeout"
                    break
                if r.returncode != 0:
                    verdict = "killed"
                    break

            if verdict == "killed":
                killed += 1
            elif verdict == "timeout":
                timeout += 1
                print(f"  TIMEOUT  {relpath}:{i+1}  {label}")
            else:
                survived += 1
                survivors.append((relpath, i + 1, label, src_line))
                print(f"  SURVIVED {relpath}:{i+1}  {label}\n"
                      f"           {src_line}")
            restore(relpath)

            if n % 10 == 0:
                print(f"  … {n}/{len(pool)}  killed {killed}  survived "
                      f"{survived}  stillborn {stillborn}  "
                      f"{time.time()-t0:.0f}s")
    finally:
        for t in targets:
            restore(t)

    clean = not run(["git", "status", "--porcelain", "src/"]).stdout.strip()

    print(f"\n{'='*70}")
    valid = killed + survived
    print(f"{valid} valid mutant(s): {killed} killed, {survived} SURVIVED"
          f"   ({stillborn} stillborn, {timeout} timed out)")
    if valid:
        print(f"mutation score: {100.0*killed/valid:.1f}%")
    if survivors:
        print("\nSURVIVORS -- each is a change to the program that every test "
              "agrees is fine:\n")
        for relpath, ln, label, src in survivors:
            print(f"  {relpath}:{ln}  [{label}]\n      {src}")
        print("\nA survivor is one of three things, and they need different "
              "answers: a REAL GAP in the tests, a line whose two behaviours "
              "are genuinely equivalent, or code no fixture can reach. Read "
              "each one; do not assume the first.")
    print(f"\nsrc/ restored and verified clean: {clean}")
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
