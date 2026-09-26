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

"""Check a lap body written in LSL, the lap statement language.

The spec is docs/handshake/PROPOSAL-lap-statement-language.md. This is its
checker, and the spec's "What the checker refuses" is the list this enforces.

WHY IT EXISTS. Every defect either project has found in the other's laps was
in the prose, never in a wire header: a claim with no artifact behind it, a
citation with no commit, "none" where "we could not tell" was true, a relay
treated as a lap. The headers are fields a gate reads; the body was sentences.
LSL makes the body fields too, and this makes each of those a refusal.

WHAT IT DOES NOT DO. It never decides whether a statement is TRUE. It decides
whether it is CHECKABLE: whether it names, at a commit that cannot move, the
artifact that would refute it. Reading that artifact is still the reader's job.

A reference into the other project's tree is resolved only against a clone
given with --peer. Without one it is reported UNCHECKED, never passed.

    tools/lap-statements.py docs/handshake/round-27-lap-06.md
    tools/lap-statements.py LAP --peer ../platterpus

Exit 0: every statement is well formed (warnings may be printed). Exit 1: at
least one refusal. Exit 2: the file could not be checked -- unreadable, or not
an LSL lap. Two codes, because "refused" and "could not check" are different
claims.
"""

import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# kind -> the grades it takes (empty: it takes none)
KINDS = {
    "FACT": {"measured", "read", "reproduced", "relayed"},
    "NONE": set(), "UNKNOWN": set(), "DID": set(), "WILL": set(),
    "ACCEPT": set(), "AMEND": set(), "REFUSE": set(), "CORRECT": set(),
    "ASK": set(), "VERDICT": set(), "NOTE": set(),
}

REQUIRED = {
    ("FACT", "measured"): ["evidence"],
    ("FACT", "read"): ["evidence"],
    ("FACT", "reproduced"): ["re", "evidence"],
    ("FACT", "relayed"): ["source"],
    ("NONE", None): ["scope", "evidence"],
    ("UNKNOWN", None): ["reason"],
    ("DID", None): ["commit"],
    ("WILL", None): ["owner", "when"],
    ("ACCEPT", None): ["re"],
    ("AMEND", None): ["re", "to"],
    ("REFUSE", None): ["re", "because"],
    ("CORRECT", None): ["re", "was", "now"],
    ("ASK", None): ["target"],
    ("VERDICT", None): ["basis"],
    ("NOTE", None): [],
}

FIELDS = {"evidence", "re", "source", "scope", "reason", "commit", "owner",
          "when", "to", "because", "was", "now", "target", "breaks", "basis"}

SIDES = {"cyanrip", "platterpus"}
# What each side writes in HANDSHAKE-FROM.
FROM_SIDE = {"cyanrip-fork": "cyanrip", "cyanrip": "cyanrip",
             "platterpus": "platterpus"}

HEAD_RE = re.compile(r"^S(\d+) ([A-Z]+)(?: ([a-z]+))?: (\S.*)$")
FIELD_RE = re.compile(r"^  ([a-z]+): (\S.*)$")
CONT_RE = re.compile(r"^    (\S.*)$")
WIRE_RE = re.compile(r"^HANDSHAKE-([A-Z0-9-]+): ?(.*)$")
# A commit is hex. A branch name never parses, which is the point.
ART_RE = re.compile(r"^(cyanrip|platterpus)@([0-9a-f]{7,40}):([^\s:]+)"
                    r"(?::(\d+)(?:-(\d+))?)?$")
STMT_RE = re.compile(r"^(?:(cyanrip|platterpus):R(\d+)\.L(\d+)\.)?"
                     r"(S\d+|§[A-Za-z0-9.]+)$")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


class Lap:
    def __init__(self, path, text):
        self.path = path
        self.text = text
        self.refusals = []
        self.warnings = []
        self.headers = {}
        self.statements = []

    def refuse(self, line, msg):
        self.refusals.append((line, msg))

    def warn(self, line, msg):
        self.warnings.append((line, msg))


def parse(lap):
    """Split the file into wire headers and statements; return False if not LSL."""
    lines = lap.text.splitlines()
    start = None
    for i, line in enumerate(lines):
        m = WIRE_RE.match(line)
        if m and start is None:
            lap.headers.setdefault(m.group(1), []).append(m.group(2))
        if line.rstrip().startswith("LSL:") and start is None:
            if line.rstrip() != "LSL: 1":
                lap.refuse(i + 1, f"declares {line.strip()!r}; this checker "
                                  f"implements LSL 1 only")
                return False
            start = i + 1
    if start is None:
        return False

    cur = None
    field = None
    for i in range(start, len(lines)):
        n, line = i + 1, lines[i]
        if not line.strip() or line.startswith("## "):
            # A blank line or a heading ends the statement: a field after
            # one would attach to whichever statement happened to be last.
            cur = field = None
            continue
        m = HEAD_RE.match(line)
        if m:
            cur = {"n": int(m.group(1)), "kind": m.group(2),
                   "grade": m.group(3), "sentence": m.group(4).strip(),
                   "line": n, "fields": []}
            lap.statements.append(cur)
            field = None
            continue
        m = FIELD_RE.match(line)
        if m and cur is not None:
            field = [m.group(1), m.group(2).strip(), n]
            cur["fields"].append(field)
            continue
        m = CONT_RE.match(line)
        if m and field is not None:
            field[1] += " " + m.group(1).strip()
            continue
        lap.refuse(n, "not a statement, a field, a continuation or a "
                      "heading -- prose goes in a NOTE: "
                      f"{line.strip()[:60]!r}")
    return True


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)


class Resolver:
    """Resolves artifact references against our tree and, if given, theirs."""

    def __init__(self, ours, peer, at):
        self.repo = {"cyanrip": ours, "platterpus": peer}
        self.at = at
        self.cache = {}

    def artifact(self, lap, line, side, sha, path, a, b):
        repo = self.repo[side]
        if repo is None:
            lap.warn(line, f"UNCHECKED {side}@{sha}:{path} -- no clone of "
                           f"that tree was given (--peer)")
            return
        key = (side, sha, path)
        if key not in self.cache:
            r = git(repo, "rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}")
            if r.returncode != 0:
                self.cache[key] = f"commit {sha} does not resolve in {side}'s tree"
            elif side == "cyanrip" and git(
                    repo, "merge-base", "--is-ancestor", sha,
                    self.at).returncode != 0:
                self.cache[key] = (f"commit {sha} is not reachable from "
                                   f"{self.at}, so a fresh clone cannot "
                                   f"resolve it")
            else:
                r = git(repo, "show", f"{sha}:{path}")
                self.cache[key] = (r.stdout.count("\n") if r.returncode == 0
                                   else f"{path} does not exist at {side}@{sha}")
        got = self.cache[key]
        if isinstance(got, str):
            lap.refuse(line, got)
            return
        lo, hi = a, (b if b is not None else a)
        if lo is not None:
            if lo < 1 or hi < lo:
                lap.refuse(line, f"line range {a}-{b} is not a range")
            elif hi > got:
                lap.refuse(line, f"{side}@{sha}:{path} has {got} lines; "
                                 f"line {hi} does not exist")

    def commit(self, lap, line, sha):
        r = git(self.repo["cyanrip"], "rev-parse", "--verify", "--quiet",
                f"{sha}^{{commit}}")
        if r.returncode != 0:
            lap.refuse(line, f"commit {sha} does not resolve in our tree")
        elif git(self.repo["cyanrip"], "merge-base", "--is-ancestor", sha,
                 self.at).returncode != 0:
            lap.refuse(line, f"commit {sha} is not reachable from {self.at}")


def lap_file(side, rnd, lp):
    name = f"round-{int(rnd):02d}-lap-{int(lp):02d}.md"
    if side == "cyanrip":
        return ROOT / "docs" / "handshake" / name
    return ROOT / "docs" / "handshake" / "inbound" / name


def statement_ids(text):
    """The S-numbers of an LSL lap, or None for a prose lap."""
    if not re.search(r"^LSL: 1\s*$", text, re.M):
        return None
    return {int(m.group(1)) for m in
            re.finditer(r"^S(\d+) [A-Z]+", text, re.M)}


def check_stmt_ref(lap, line, token, me, local_ids):
    m = STMT_RE.match(token)
    if not m:
        return False
    side, rnd, lp, target = m.groups()
    if side is None or (side, int(rnd), int(lp)) == me:
        if target.startswith("§"):
            lap.refuse(line, f"{token}: this lap is LSL; cite a statement, "
                             f"not a section")
        elif int(target[1:]) not in local_ids:
            lap.refuse(line, f"{token}: no such statement in this lap")
        return True
    f = lap_file(side, rnd, lp)
    if not f.exists():
        lap.refuse(line, f"{token}: we do not hold {side}'s round {rnd} lap "
                         f"{lp} (looked for {f.relative_to(ROOT)}); a cited "
                         f"document must be one we hold")
        return True
    text = f.read_text(encoding="utf-8", errors="replace")
    ids = statement_ids(text)
    if target.startswith("S"):
        if ids is None:
            lap.refuse(line, f"{token}: {f.name} is a prose lap and has no "
                             f"statement numbers; cite a section (§X)")
        elif int(target[1:]) not in ids:
            lap.refuse(line, f"{token}: {f.name} has no statement {target}")
    else:
        sec = re.escape(target[1:])
        if not (re.search(rf"^#+\s*(?:§\s*)?{sec}[.\s:—-]", text, re.M)
                or f"§{target[1:]}" in text
                or re.search(rf"^\*\*{sec}[.\s:]", text, re.M)):
            lap.warn(line, f"{token}: no heading for section {target[1:]} "
                           f"found in {f.name}")
    return True


def check(lap, resolver):
    me_side = FROM_SIDE.get((lap.headers.get("FROM") or [""])[0].strip())
    try:
        me = (me_side, int(lap.headers["ROUND"][0]),
              int(lap.headers["LAP"][0]))
    except (KeyError, ValueError, IndexError):
        me = (me_side, None, None)
        lap.refuse(1, "HANDSHAKE-ROUND and HANDSHAKE-LAP must each be "
                      "declared once, as numbers")

    stmts = lap.statements
    if not stmts:
        lap.refuse(1, "an LSL lap with no statements")
    by_n = {}
    gap_reported = False
    for i, s in enumerate(stmts, 1):
        if s["n"] in by_n:
            lap.refuse(s["line"], f"S{s['n']} is numbered twice")
        elif s["n"] != i and not gap_reported:
            lap.refuse(s["line"], f"S{s['n']} where S{i} was expected; "
                                  f"numbers run from S1 with no gaps")
            gap_reported = True
        by_n.setdefault(s["n"], s)
    local_ids = set(by_n)

    verdicts = [s for s in stmts if s["kind"] == "VERDICT"]
    if len(verdicts) != 1:
        lap.refuse(1, f"{len(verdicts)} VERDICT statements; exactly one is "
                      f"required")

    for s in stmts:
        n, kind, grade = s["line"], s["kind"], s["grade"]
        tag = f"S{s['n']} {kind}" + (f" {grade}" if grade else "")
        if kind not in KINDS:
            lap.refuse(n, f"{tag}: {kind} is not a kind")
            continue
        if KINDS[kind] and grade not in KINDS[kind]:
            lap.refuse(n, f"{tag}: a {kind} takes one grade of "
                          f"{sorted(KINDS[kind])}")
            continue
        if not KINDS[kind] and grade:
            lap.refuse(n, f"{tag}: a {kind} takes no grade")
            continue
        have = {}
        for name, value, fl in s["fields"]:
            if name not in FIELDS:
                lap.refuse(fl, f"{tag}: {name}: is not a field")
                continue
            have.setdefault(name, []).append((value, fl))
        for req in REQUIRED[(kind, grade)]:
            if req not in have:
                lap.refuse(n, f"{tag}: needs a {req}: field")

        # Every field value has a shape; check each one that has one.
        for value, fl in have.get("evidence", []):
            first = value.split()[0]
            if value.startswith("run: "):
                if " => " not in value:
                    lap.refuse(fl, f"{tag}: a run: names its command AND its "
                                   f"result, as 'run: CMD => RESULT'")
                continue
            m = ART_RE.match(first)
            if not m:
                lap.refuse(fl, f"{tag}: evidence {first!r} is neither "
                               f"'run: CMD => RESULT' nor side@commit:path"
                               f"[:line[-line]]")
                continue
            resolver.artifact(lap, fl, m.group(1), m.group(2), m.group(3),
                              int(m.group(4)) if m.group(4) else None,
                              int(m.group(5)) if m.group(5) else None)
        if kind == "FACT" and grade == "measured" and have.get("evidence"):
            if not any(v.startswith("run: ") or v.startswith("cyanrip@")
                       for v, _ in have["evidence"]):
                lap.refuse(n, f"{tag}: measured by us needs a run: or an "
                              f"artifact in our tree")
        if kind == "FACT" and grade == "read" and have.get("evidence"):
            if not any(ART_RE.match(v.split()[0]) for v, _ in have["evidence"]):
                lap.refuse(n, f"{tag}: read needs an artifact reference")
        if kind == "FACT" and grade == "relayed":
            lap.warn(n, f"{tag}: a relay is in neither repository; nothing "
                        f"here can be checked by the other side")

        for fname in ("re",):
            for value, fl in have.get(fname, []):
                first = value.split()[0]
                if check_stmt_ref(lap, fl, first, me, local_ids):
                    continue
                m = ART_RE.match(first)
                if m:
                    resolver.artifact(lap, fl, m.group(1), m.group(2),
                                      m.group(3),
                                      int(m.group(4)) if m.group(4) else None,
                                      int(m.group(5)) if m.group(5) else None)
                else:
                    lap.refuse(fl, f"{tag}: re: {first!r} is neither a "
                                   f"statement nor an artifact reference")
        for value, fl in have.get("because", []):
            for token in re.split(r"[,\s]+", value.strip()):
                if token and not check_stmt_ref(lap, fl, token, me, local_ids):
                    lap.refuse(fl, f"{tag}: because: {token!r} is not a "
                                   f"statement reference")
        for value, fl in have.get("commit", []):
            sha = value.split()[0]
            if not re.fullmatch(r"[0-9a-f]{7,40}", sha):
                lap.refuse(fl, f"{tag}: commit: {sha!r} is not a commit SHA")
            else:
                resolver.commit(lap, fl, sha)
        for value, fl in have.get("owner", []):
            if value not in ("us", "them", "operator"):
                lap.refuse(fl, f"{tag}: owner: is us, them or operator, not "
                               f"{value!r}")
        for value, fl in have.get("when", []):
            if DATE_RE.search(value):
                lap.refuse(fl, f"{tag}: when: is a condition, never a date")
        for value, fl in have.get("target", []):
            if value not in ("BLOCKING", "NEXT-ROUND"):
                lap.refuse(fl, f"{tag}: target: is BLOCKING or NEXT-ROUND")
            elif value == "BLOCKING" and "breaks" not in have:
                lap.refuse(fl, f"{tag}: a BLOCKING question names what it "
                               f"breaks in the pin (breaks:)")

        if kind == "VERDICT":
            said = s["sentence"].split()[0].rstrip(".")
            declared = [v.split()[0] for v in lap.headers.get("VERDICT", [])
                        if v.split()]
            if said not in ("GO", "HOLD", "OPEN"):
                lap.refuse(n, f"{tag}: the verdict is GO, HOLD or OPEN")
            elif len(declared) != 1 or declared[0] != said:
                lap.refuse(n, f"{tag}: says {said} and HANDSHAKE-VERDICT "
                              f"says {declared or 'nothing'}")
            for value, fl in have.get("basis", []):
                for token in re.split(r"[,\s]+", value.strip()):
                    if not token:
                        continue
                    if not re.fullmatch(r"S\d+", token):
                        lap.refuse(fl, f"{tag}: basis: {token!r} is not a "
                                       f"statement of this lap")
                    elif int(token[1:]) not in by_n:
                        lap.refuse(fl, f"{tag}: basis: {token} does not exist")
                    elif by_n[int(token[1:])]["kind"] in ("NOTE", "ASK",
                                                          "VERDICT"):
                        lap.refuse(fl, f"{tag}: basis: {token} is a "
                                       f"{by_n[int(token[1:])]['kind']}, "
                                       f"which carries no claim")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lap", type=pathlib.Path)
    ap.add_argument("--peer", type=pathlib.Path,
                    help="a clone of the other project's tree, to resolve "
                         "references into it")
    ap.add_argument("--at", default="HEAD",
                    help="our commits must be reachable from this ref "
                         "(default HEAD)")
    args = ap.parse_args()

    try:
        text = args.lap.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"CANNOT CHECK  {args.lap}: {e}")
        return 2
    lap = Lap(args.lap, text)
    if not parse(lap):
        for line, msg in lap.refusals:
            print(f"CANNOT CHECK  {args.lap}:{line}: {msg}")
        if not lap.refusals:
            print(f"CANNOT CHECK  {args.lap}: not an LSL lap -- no 'LSL: 1' "
                  f"line")
        return 2
    check(lap, Resolver(ROOT, args.peer, args.at))

    for line, msg in sorted(lap.refusals):
        print(f"REFUSED  {args.lap.name}:{line}  {msg}")
    for line, msg in sorted(lap.warnings):
        print(f"WARN     {args.lap.name}:{line}  {msg}")
    kinds = {}
    for s in lap.statements:
        kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
    census = ", ".join(f"{v} {k}" for k, v in sorted(kinds.items()))
    print(f"\n{len(lap.statements)} statement(s): {census or 'none'}")
    if lap.refusals:
        print(f"{len(lap.refusals)} refusal(s) -- not a well-formed LSL lap")
        return 1
    print(f"well formed, {len(lap.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
