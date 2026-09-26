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
checker, and every problem it reports names one of the spec's rule ids, so two
checkers that disagree can say which rule they disagree about.

WHY IT EXISTS. Every defect either project has found in the other's laps was
in the prose, never in a wire header: a claim with no artifact behind it, a
citation with no commit, "none" where "we could not tell" was true, a relay
treated as a lap. The headers are fields a gate reads; the body was sentences.
LSL makes the body fields too, and this makes each of those a refusal.

WHAT IT DOES NOT DO. It never decides whether a statement is TRUE. It decides
whether it is CHECKABLE: whether it names, at a commit that cannot move, the
artifact that would refute it. Reading that artifact is still the reader's job.

"US" IS WHOEVER WROTE THE LAP, read from HANDSHAKE-FROM. The first version
read it as cyanrip whatever the header said, so a correct Platterpus lap was
refused for citing its own commits (Platterpus, LSL amendments 1, F1).

A COMMIT IS JUDGED AGAINST ITS SIDE'S REF OF RECORD, the branch that side
publishes laps from: platterpus-fork for us, main for them. On that ref it is
fine. On another branch only it is a warning, LSL.offrecord: a fresh clone
resolves it only while that branch exists, which in a tree that squash-merges
is every lap's own commits (F4). On no branch at all it is refused. And a
commit a SHALLOW clone cannot see is LSL.unchecked, never refused, because a
shallow clone cannot tell a missing commit from one it never fetched (F3).

    tools/lap-statements.py docs/handshake/round-28-lap-01.md
    tools/lap-statements.py LAP --peer ../platterpus
    tools/lap-statements.py LAP --ref cyanrip=HEAD     # judge ours against HEAD

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

# The rule ids, shared with Platterpus's checker (their LSL amendments 1 §5).
# The spec's table must name exactly these; tests/lap_statements.py checks it.
RULES = {
    "LSL.1": "refused",         # a kind or grade not in the table
    "LSL.2": "refused",         # a required field missing, or the wrong sort of evidence
    "LSL.3": "refused",         # a gap or a repeat in the numbering, or no statements
    "LSL.4": "refused",         # a reference that does not parse or does not resolve
    "LSL.5": "refused",         # the VERDICT: count, agreement with the header, basis
    "LSL.6": "refused",         # an ASK BLOCKING with no breaks:
    "LSL.syntax": "refused",    # a line that is not a statement, field, continuation or heading
    "LSL.field": "refused",     # a field outside the fields table
    "LSL.value": "refused",     # a value outside its shape
    "LSL.header": "refused",    # HANDSHAKE-FROM, -ROUND or -LAP missing or unreadable
    "LSL.version": "could not check",
    "LSL.file": "could not check",
    "LSL.offrecord": "warning",
    "LSL.relayed": "warning",
    "LSL.unchecked": "warning",
}

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

SIDES = ("cyanrip", "platterpus")
# What each side writes in HANDSHAKE-FROM.
FROM_SIDE = {"cyanrip-fork": "cyanrip", "cyanrip": "cyanrip",
             "platterpus": "platterpus"}
# The branch each side publishes its laps from.
RECORD = {"cyanrip": "platterpus-fork", "platterpus": "main"}

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

    def refuse(self, line, rule, msg):
        assert RULES[rule] in ("refused", "could not check"), rule
        self.refusals.append((line, rule, msg))

    def warn(self, line, rule, msg):
        assert RULES[rule] == "warning", rule
        self.warnings.append((line, rule, msg))


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
                lap.refuse(i + 1, "LSL.version",
                           f"declares {line.strip()!r}; this checker "
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
        lap.refuse(n, "LSL.syntax",
                   "not a statement, a field, a continuation or a "
                   "heading -- prose goes in a NOTE: "
                   f"{line.strip()[:60]!r}")
    return True


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)


class Resolver:
    """Resolves commits and artifacts in each side's tree, if given one."""

    def __init__(self, ours, peer, refs):
        self.repo = {"cyanrip": ours, "platterpus": peer}
        self.refs = dict(RECORD)
        self.refs.update(refs)
        self.located = {}
        self.record_ref = {}

    def _record(self, side):
        """Every ref in this clone that stands for the ref of record.

        The local branch AND each remote-tracking copy of it, because either
        can be the newer one: `git fetch` moves `origin/main` and not a stale
        local `main`, and our own unpushed commits are on the local branch
        only. A commit reachable from any of them is on the record. The first
        version took the local branch alone and called every commit of a
        fetched peer tree off the record."""
        if side not in self.record_ref:
            name, repo = self.refs[side], self.repo[side]
            found = []
            listed = git(repo, "for-each-ref", "--format=%(refname)",
                         f"refs/heads/{name}", "refs/remotes").stdout.split()
            for ref in listed:
                if ref == f"refs/heads/{name}" or (
                        ref.startswith("refs/remotes/")
                        and ref.split("/", 3)[-1] == name):
                    found.append(ref)
            if not found and git(repo, "rev-parse", "--verify", "--quiet",
                                 f"{name}^{{commit}}").returncode == 0:
                found.append(name)
            self.record_ref[side] = found
        return self.record_ref[side]

    def locate(self, side, sha):
        """Where `sha` is in `side`'s tree, as (verdict, detail).

        verdict is one of: ok, offrecord, unchecked, missing."""
        key = (side, sha)
        if key in self.located:
            return self.located[key]
        repo = self.repo[side]
        if repo is None:
            got = ("unchecked", f"no clone of {side}'s tree was given (--peer)")
        elif git(repo, "rev-parse", "--verify", "--quiet",
                 f"{sha}^{{commit}}").returncode != 0:
            shallow = git(repo, "rev-parse",
                          "--is-shallow-repository").stdout.strip() == "true"
            if shallow:
                got = ("unchecked", f"commit {sha} is not in {side}'s clone, "
                                    f"which is shallow, so it cannot tell a "
                                    f"missing commit from one it never fetched")
            else:
                got = ("missing", f"commit {sha} does not resolve in "
                                  f"{side}'s tree")
        else:
            rec = self._record(side)
            if not rec:
                got = ("unchecked", f"{side}'s ref of record, "
                                    f"{self.refs[side]}, is not in the clone "
                                    f"given, so reachability cannot be judged")
            elif any(git(repo, "merge-base", "--is-ancestor", sha,
                         ref).returncode == 0 for ref in rec):
                got = ("ok", "")
            else:
                # Symbolic refs such as origin/HEAD are aliases, not branches.
                on = [r for r in git(repo, "for-each-ref", "--contains", sha,
                                     "--format=%(refname:short) %(symref)",
                                     "refs/heads", "refs/remotes"
                                     ).stdout.splitlines()
                      if r.split() and len(r.split()) == 1]
                on = [r.split()[0] for r in on]
                if on:
                    got = ("offrecord",
                           f"commit {sha} is not on {side}'s ref of record, "
                           f"{self.refs[side]}, only on "
                           f"{', '.join(sorted(on)[:3])}"
                           f"{' and others' if len(on) > 3 else ''}: a fresh "
                           f"clone resolves it only while that branch exists")
                else:
                    got = ("missing", f"commit {sha} is in {side}'s object "
                                      f"store but on no branch, so a fresh "
                                      f"clone cannot resolve it")
        self.located[key] = got
        return got

    def _report(self, lap, line, side, sha):
        """Report where a commit is; return True if its content can be read."""
        verdict, detail = self.locate(side, sha)
        if verdict == "missing":
            lap.refuse(line, "LSL.4", detail)
            return False
        if verdict == "unchecked":
            lap.warn(line, "LSL.unchecked", f"UNCHECKED {side}@{sha}: {detail}")
            return False
        if verdict == "offrecord":
            lap.warn(line, "LSL.offrecord", detail)
        return True

    def artifact(self, lap, line, side, sha, path, a, b):
        if not self._report(lap, line, side, sha):
            return
        r = git(self.repo[side], "show", f"{sha}:{path}")
        if r.returncode != 0:
            lap.refuse(line, "LSL.4", f"{path} does not exist at {side}@{sha}")
            return
        got = r.stdout.count("\n")
        lo, hi = a, (b if b is not None else a)
        if lo is not None:
            if lo < 1 or hi < lo:
                lap.refuse(line, "LSL.4", f"line range {a}-{b} is not a range")
            elif hi > got:
                lap.refuse(line, "LSL.4",
                           f"{side}@{sha}:{path} has {got} lines; "
                           f"line {hi} does not exist")

    def commit(self, lap, line, side, sha):
        self._report(lap, line, side, sha)


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
            lap.refuse(line, "LSL.4", f"{token}: this lap is LSL; cite a "
                                      f"statement, not a section")
        elif int(target[1:]) not in local_ids:
            lap.refuse(line, "LSL.4", f"{token}: no such statement in this lap")
        return True
    f = lap_file(side, rnd, lp)
    if not f.exists():
        lap.refuse(line, "LSL.4",
                   f"{token}: we do not hold {side}'s round {rnd} lap "
                   f"{lp} (looked for {f.relative_to(ROOT)}); a cited "
                   f"document must be one we hold")
        return True
    text = f.read_text(encoding="utf-8", errors="replace")
    ids = statement_ids(text)
    if target.startswith("S"):
        if ids is None:
            lap.refuse(line, "LSL.4",
                       f"{token}: {f.name} is a prose lap and has no "
                       f"statement numbers; cite a section (§X)")
        elif int(target[1:]) not in ids:
            lap.refuse(line, "LSL.4", f"{token}: {f.name} has no statement "
                                      f"{target}")
    else:
        sec = re.escape(target[1:])
        if not (re.search(rf"^#+\s*(?:§\s*)?{sec}[.\s:—-]", text, re.M)
                or f"§{target[1:]}" in text
                or re.search(rf"^\*\*{sec}[.\s:]", text, re.M)):
            lap.warn(line, "LSL.unchecked",
                     f"{token}: no heading for section {target[1:]} "
                     f"found in {f.name}")
    return True


def art_ref(first):
    m = ART_RE.match(first)
    if not m:
        return None
    return (m.group(1), m.group(2), m.group(3),
            int(m.group(4)) if m.group(4) else None,
            int(m.group(5)) if m.group(5) else None)


def check(lap, resolver):
    declared_from = (lap.headers.get("FROM") or [""])[0].strip()
    me_side = FROM_SIDE.get(declared_from)
    if me_side is None:
        lap.refuse(1, "LSL.header",
                   f"HANDSHAKE-FROM is {declared_from or 'missing'!r}, which "
                   f"names neither side, so 'us' in this lap is unknown")
    try:
        me = (me_side, int(lap.headers["ROUND"][0]),
              int(lap.headers["LAP"][0]))
    except (KeyError, ValueError, IndexError):
        me = (me_side, None, None)
        lap.refuse(1, "LSL.header", "HANDSHAKE-ROUND and HANDSHAKE-LAP must "
                                    "each be declared once, as numbers")

    stmts = lap.statements
    if not stmts:
        lap.refuse(1, "LSL.3", "an LSL lap with no statements")
    by_n = {}
    gap_reported = False
    for i, s in enumerate(stmts, 1):
        if s["n"] in by_n:
            lap.refuse(s["line"], "LSL.3", f"S{s['n']} is numbered twice")
        elif s["n"] != i and not gap_reported:
            lap.refuse(s["line"], "LSL.3",
                       f"S{s['n']} where S{i} was expected; "
                       f"numbers run from S1 with no gaps")
            gap_reported = True
        by_n.setdefault(s["n"], s)
    local_ids = set(by_n)

    verdicts = [s for s in stmts if s["kind"] == "VERDICT"]
    if len(verdicts) != 1:
        lap.refuse(1, "LSL.5", f"{len(verdicts)} VERDICT statements; exactly "
                               f"one is required")

    for s in stmts:
        n, kind, grade = s["line"], s["kind"], s["grade"]
        tag = f"S{s['n']} {kind}" + (f" {grade}" if grade else "")
        if kind not in KINDS:
            lap.refuse(n, "LSL.1", f"{tag}: {kind} is not a kind")
            continue
        if KINDS[kind] and grade not in KINDS[kind]:
            lap.refuse(n, "LSL.1", f"{tag}: a {kind} takes one grade of "
                                   f"{sorted(KINDS[kind])}")
            continue
        if not KINDS[kind] and grade:
            lap.refuse(n, "LSL.1", f"{tag}: a {kind} takes no grade")
            continue
        have = {}
        for name, value, fl in s["fields"]:
            if name not in FIELDS:
                lap.refuse(fl, "LSL.field", f"{tag}: {name}: is not a field")
                continue
            have.setdefault(name, []).append((value, fl))
        for req in REQUIRED[(kind, grade)]:
            if req not in have:
                lap.refuse(n, "LSL.2", f"{tag}: needs a {req}: field")

        # Every field value has a shape; check each one that has one.
        for value, fl in have.get("evidence", []):
            first = value.split()[0]
            if value.startswith("run: "):
                if " => " not in value:
                    lap.refuse(fl, "LSL.value",
                               f"{tag}: a run: names its command AND its "
                               f"result, as 'run: CMD => RESULT'")
                continue
            ref = art_ref(first)
            if ref is None:
                lap.refuse(fl, "LSL.value",
                           f"{tag}: evidence {first!r} is neither "
                           f"'run: CMD => RESULT' nor side@commit:path"
                           f"[:line[-line]]")
                continue
            resolver.artifact(lap, fl, *ref)
        if kind == "FACT" and grade == "measured" and have.get("evidence"):
            if not any(v.startswith("run: ") or v.startswith(f"{me_side}@")
                       for v, _ in have["evidence"]):
                lap.refuse(n, "LSL.2",
                           f"{tag}: measured by the lap's author "
                           f"({me_side}) needs a run: or an artifact in "
                           f"{me_side}'s tree")
        if kind == "FACT" and grade == "read" and have.get("evidence"):
            if not any(art_ref(v.split()[0]) for v, _ in have["evidence"]):
                lap.refuse(n, "LSL.2", f"{tag}: read needs an artifact "
                                       f"reference")
        if kind == "FACT" and grade == "relayed":
            lap.warn(n, "LSL.relayed",
                     f"{tag}: a relay is in neither repository; nothing "
                     f"here can be checked by the other side")

        for value, fl in have.get("re", []):
            first = value.split()[0]
            if check_stmt_ref(lap, fl, first, me, local_ids):
                continue
            ref = art_ref(first)
            if ref:
                resolver.artifact(lap, fl, *ref)
            else:
                lap.refuse(fl, "LSL.4", f"{tag}: re: {first!r} is neither a "
                                        f"statement nor an artifact reference")
        for value, fl in have.get("because", []):
            for token in re.split(r"[,\s]+", value.strip()):
                if token and not check_stmt_ref(lap, fl, token, me, local_ids):
                    lap.refuse(fl, "LSL.4", f"{tag}: because: {token!r} is not "
                                            f"a statement reference")
        for value, fl in have.get("commit", []):
            sha = value.split()[0]
            if not re.fullmatch(r"[0-9a-f]{7,40}", sha):
                lap.refuse(fl, "LSL.value",
                           f"{tag}: commit: {sha!r} is not a commit SHA")
            elif me_side is not None:
                # A DID is an act of the lap's author, so its commit is in
                # the author's tree (F1).
                resolver.commit(lap, fl, me_side, sha)
        for value, fl in have.get("owner", []):
            if value not in ("us", "them", "operator"):
                lap.refuse(fl, "LSL.value", f"{tag}: owner: is us, them or "
                                            f"operator, not {value!r}")
        for value, fl in have.get("when", []):
            if DATE_RE.search(value):
                lap.refuse(fl, "LSL.value",
                           f"{tag}: when: is a condition, never a date")
        for value, fl in have.get("target", []):
            if value not in ("BLOCKING", "NEXT-ROUND"):
                lap.refuse(fl, "LSL.value",
                           f"{tag}: target: is BLOCKING or NEXT-ROUND")
            elif value == "BLOCKING" and "breaks" not in have:
                lap.refuse(fl, "LSL.6",
                           f"{tag}: a BLOCKING question names what it "
                           f"breaks in the pin (breaks:)")

        if kind == "VERDICT":
            said = s["sentence"].split()[0].rstrip(".")
            declared = [v.split()[0] for v in lap.headers.get("VERDICT", [])
                        if v.split()]
            if said not in ("GO", "HOLD", "OPEN"):
                lap.refuse(n, "LSL.5", f"{tag}: the verdict is GO, HOLD or OPEN")
            elif len(declared) != 1 or declared[0] != said:
                lap.refuse(n, "LSL.5", f"{tag}: says {said} and "
                                       f"HANDSHAKE-VERDICT says "
                                       f"{declared or 'nothing'}")
            for value, fl in have.get("basis", []):
                for token in re.split(r"[,\s]+", value.strip()):
                    if not token:
                        continue
                    if not re.fullmatch(r"S\d+", token):
                        lap.refuse(fl, "LSL.5", f"{tag}: basis: {token!r} is "
                                                f"not a statement of this lap")
                    elif int(token[1:]) not in by_n:
                        lap.refuse(fl, "LSL.5",
                                   f"{tag}: basis: {token} does not exist")
                    elif by_n[int(token[1:])]["kind"] in ("NOTE", "ASK",
                                                          "VERDICT"):
                        lap.refuse(fl, "LSL.5",
                                   f"{tag}: basis: {token} is a "
                                   f"{by_n[int(token[1:])]['kind']}, "
                                   f"which carries no claim")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lap", type=pathlib.Path)
    ap.add_argument("--peer", type=pathlib.Path,
                    help="a clone of Platterpus's tree, to resolve "
                         "references into it")
    ap.add_argument("--ours", type=pathlib.Path, default=ROOT,
                    help="the clone of cyanrip's tree to resolve our "
                         "references in (default: this one)")
    ap.add_argument("--ref", action="append", default=[],
                    metavar="SIDE=REF",
                    help="judge SIDE's commits against REF rather than its "
                         f"ref of record ({RECORD})")
    args = ap.parse_args()

    refs = {}
    for item in args.ref:
        side, _, ref = item.partition("=")
        if side not in SIDES or not ref:
            ap.error(f"--ref takes SIDE=REF with SIDE one of {SIDES}")
        refs[side] = ref

    try:
        text = args.lap.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"CANNOT CHECK  {args.lap}  [LSL.file] {e}")
        return 2
    lap = Lap(args.lap, text)
    if not parse(lap):
        for line, rule, msg in lap.refusals:
            print(f"CANNOT CHECK  {args.lap}:{line}  [{rule}] {msg}")
        if not lap.refusals:
            print(f"CANNOT CHECK  {args.lap}  [LSL.version] not an LSL lap "
                  f"-- no 'LSL: 1' line")
        return 2
    check(lap, Resolver(args.ours, args.peer, refs))

    for line, rule, msg in sorted(lap.refusals):
        print(f"REFUSED  {args.lap.name}:{line}  [{rule}] {msg}")
    for line, rule, msg in sorted(lap.warnings):
        print(f"WARN     {args.lap.name}:{line}  [{rule}] {msg}")
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
