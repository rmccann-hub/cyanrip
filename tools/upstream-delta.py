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

"""What an upstream sync would bring us, across the surfaces a consumer sees.

WHY THIS EXISTS. We inherit upstream's changes, and twice they have broken our
consumer without touching a line of our code: `-V` became `-v` when getopt was
replaced with genopt, and `Total time:` changed from HH:MM:SS.mmm to MM:SS.FF
under PR #130. Neither was a bug in cyanrip and neither was visible in a
"does it still build?" check. CLAUDE.md's rule is therefore to **diff the CLI
surface and the log text, not just the code** -- and this is that diff, run
rather than remembered.

WHAT IT COMPARES, and how each is established:

  * versions        -- read from each ref's meson.build
  * commits/files   -- git, between the two refs
  * CLI flags       -- MEASURED, by running each binary's --help. Not read from
                       the option table: seam-rules S-9 says limits are
                       established by running the binary, and a flag list
                       transcribed from source is a claim about behaviour
                       nobody ran. If a binary is not supplied the section says
                       so rather than falling back to source and pretending.
  * log lines       -- read from cyanrip_log() format strings in each tree.
                       Source-derived on purpose: a rip only exercises the
                       paths a fixture reaches, so a log diff taken from two
                       runs UNDERSTATES the delta. Run-based comparison is
                       still worth doing, and the report says to do it.
  * dependencies    -- read from dependency() calls in both meson.build files

WHAT IT DOES NOT DO: judge. It reports what differs; whether a difference is a
collision, a gap or a non-event is a human call, and that judgement belongs in
the per-sync document under docs/upstream/ rather than in here. Same
division the log itself keeps -- we report measurements with provenance, the
consumer makes the verdict.

ONE TRAP, PAID FOR ON 2026-08-18. Compare the MERGED TREES, never individual
commits in the series. Upstream's b227408 added a track line spelled
`Peak: %.6f`; two later "Address PR comments" commits renamed it to
`Sample peak: %.6f`. Reading the introducing commit gave a label that never
shipped, and it was reported as a finding before anyone opened the merged file.
`git show <ref>:<path>` is what this tool uses, and it is the reason.

Usage:
    tools/upstream-delta.py [--fork REF] [--upstream REF]
                            [--fork-binary PATH] [--upstream-binary PATH]
"""

import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def git(*args, check=True):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and p.returncode != 0:
        sys.exit(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout


def show(ref, path):
    """A file as of `ref`, or None when that ref has no such file.

    Absence is a real answer -- meson_options.txt does not exist before
    +platterpus.6 -- so it is returned rather than raised."""
    p = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT,
                       capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def version_of(ref):
    src = show(ref, "meson.build") or ""
    m = re.search(r"^\s*version:\s*'([^']+)'", src, re.M)
    return m.group(1) if m else "unknown"


def cli_flags(binary):
    """MEASURED. Returns None when no binary was given, which is not the same
    as an empty set and must not be rendered as one."""
    if not binary:
        return None
    p = subprocess.run([str(binary), "--help"], capture_output=True, text=True)
    text = p.stdout + p.stderr
    return set(re.findall(r"^\s+(--[a-z0-9-]+)", text, re.M))


def log_lines(ref):
    """Format strings passed to cyanrip_log(), from every source file in `ref`.

    Numeric/string conversions are collapsed so that a line whose VALUE differs
    between the two trees does not read as a line whose TEXT differs. What we
    undertake not to reword is the text.
    """
    out = set()
    files = [f for f in git("ls-tree", "--name-only", "-r", ref, "src/").split()
             if f.endswith(".c")]
    for f in files:
        src = show(ref, f) or ""
        for m in re.finditer(r'cyanrip_log\s*\([^,]*,[^,]*,\s*("(?:[^"\\]|\\.)*")',
                             src):
            lit = m.group(1)[1:-1]
            lit = re.sub(r"%[-+ #0-9.*]*[a-zA-Z]", "%_", lit)
            lit = lit.replace("\\n", "").strip()
            if lit:
                out.add(lit)
    return out


def deps(ref):
    out = set()
    for path in ("meson.build", "src/meson.build"):
        src = show(ref, path) or ""
        out |= set(re.findall(r"dependency\(\s*'([^']+)'", src))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fork", default="platterpus-fork")
    ap.add_argument("--upstream", default="master",
                    help="our clean mirror of upstream, not a remote")
    ap.add_argument("--fork-binary")
    ap.add_argument("--upstream-binary")
    args = ap.parse_args()

    fork, up = args.fork, args.upstream
    base = git("merge-base", fork, up).strip()
    inbound = git("rev-list", "--count", f"{fork}..{up}").strip()
    ours = git("rev-list", "--count", f"{up}..{fork}").strip()

    o = []
    o.append(f"## Delta: `{up}` -> `{fork}`\n")
    o.append(f"| | |\n| --- | --- |")
    o.append(f"| fork `{fork}` | `{git('rev-parse', '--short', fork).strip()}`"
             f" — {version_of(fork)} |")
    o.append(f"| upstream `{up}` | `{git('rev-parse', '--short', up).strip()}`"
             f" — {version_of(up)} |")
    o.append(f"| merge-base | `{base[:7]}` |")
    o.append(f"| commits inbound (upstream has, fork lacks) | **{inbound}** |")
    o.append(f"| commits ours (fork has, upstream lacks) | {ours} |\n")

    o.append("### Inbound commits\n")
    log = git("log", "--oneline", "--reverse", f"{fork}..{up}").strip()
    o.append("```\n" + (log or "(none)") + "\n```\n")

    o.append("### Files an inbound sync would touch\n")
    stat = git("diff", "--stat", f"{fork}...{up}", check=False).strip()
    o.append("```\n" + (stat or "(none)") + "\n```\n")

    o.append("### CLI surface\n")
    f_cli, u_cli = cli_flags(args.fork_binary), cli_flags(args.upstream_binary)
    if f_cli is None or u_cli is None:
        o.append("**NOT MEASURED** — one or both binaries were not supplied. "
                 "This section is deliberately blank rather than derived from "
                 "the option table: a flag list read from source is a claim "
                 "about behaviour nobody ran (seam-rules S-9). Build both and "
                 "pass `--fork-binary` / `--upstream-binary`.\n")
    else:
        gained = sorted(u_cli - f_cli)
        oursonly = sorted(f_cli - u_cli)
        o.append(f"`[MEASURED]` from `--help` of both binaries.\n")
        o.append("- **inbound (upstream has, we lack):** "
                 + (", ".join(f"`{x}`" for x in gained) if gained else "**none**"))
        o.append(f"- ours only (our divergence): "
                 f"{', '.join(f'`{x}`' for x in oursonly) if oursonly else 'none'}\n")

    o.append("### Log text\n")
    f_log, u_log = log_lines(fork), log_lines(up)
    gained = sorted(u_log - f_log)
    lost = sorted(f_log - u_log)
    o.append("Format strings from `cyanrip_log()` in each tree, conversions "
             "collapsed to `%_` so a differing VALUE does not read as "
             "differing TEXT.\n")
    o.append(f"**Inbound lines we do not have ({len(gained)}):**\n")
    o.append("```\n" + ("\n".join(gained) if gained else "(none)") + "\n```\n")
    o.append(f"**Lines we have that upstream does not ({len(lost)}) — our "
             f"divergence, listed because a sync must not silently drop "
             f"them:**\n")
    o.append("```\n" + ("\n".join(lost) if lost else "(none)") + "\n```\n")

    o.append("### Dependencies\n")
    f_d, u_d = deps(fork), deps(up)
    o.append(f"- inbound: "
             f"{', '.join(f'`{x}`' for x in sorted(u_d - f_d)) or 'none'}")
    o.append(f"- ours only: "
             f"{', '.join(f'`{x}`' for x in sorted(f_d - u_d)) or 'none'}\n")

    o.append("---\n")
    o.append("*Generated by `tools/upstream-delta.py`. It reports differences "
             "and judges none of them: whether a difference is a collision, a "
             "gap or a non-event is a human call, and it belongs in the "
             "per-sync document rather than here.*")

    print("\n".join(o))
    return 0


if __name__ == "__main__":
    sys.exit(main())
