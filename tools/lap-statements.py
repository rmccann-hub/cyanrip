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

`LSL: 2` IS LSL 1 PLUS THE AMENDMENTS BOTH SIDES ACCEPTED, A1-A8 from
Platterpus's LSL amendments 1, A3 as cyanrip amended it in round 28 lap 1 S21.
Every refusal a rule of LSL 2 adds names the amendment that added it, `A1` to
`A8`, the ids Platterpus's checker reports, so the two checkers can say which
amendment they disagree about. `LSL: 3` IS LSL 2 PLUS B1-B3, accepted in
round 28 (Platterpus's lap 2 S17 and lap 4 S22-S24): a GO needs a close
condition to wait for (B2), `answers:` counts only on a claim (B3), and with
--rerun a `run:` is re-run at the commit it names, when its command is one
that can only depend on that commit (B1). `LSL: 4` IS LSL 3 PLUS ONE LITERAL on
A2, from round 30 (our lap 3 S10 as Platterpus's lap 4 S36 amends it): a WILL
carrying verdict: says exactly `when: our next lap`. A lap declaring `LSL: 1` is checked exactly as
before: the new kinds and fields are still refused in it.

Three amendments read other laps of the round: A1 (a GO waits for every close
condition), A2 (a pre-commit binds the author's next lap) and A7 (a GO waits for
the other side's blocking questions). They read the laps this tree holds, ours
in docs/handshake/ and theirs in docs/handshake/inbound/, or --laps DIR.

    tools/lap-statements.py docs/handshake/round-28-lap-01.md
    tools/lap-statements.py LAP --peer ../platterpus
    tools/lap-statements.py LAP --ref cyanrip=HEAD     # judge ours against HEAD

Exit 0: every statement is well formed (warnings may be printed). Exit 1: at
least one refusal. Exit 2: the file could not be checked -- unreadable, or not
an LSL lap. Two codes, because "refused" and "could not check" are different
claims.
"""

import argparse
import codecs
import os
import pathlib
import re
import shlex
import shutil
import signal
import subprocess
import sys
import importlib.util
import tempfile

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
    # LSL 2's amendments, each under the id Platterpus's checker reports.
    "A1": "refused",            # TERM: close conditions, and a GO that waits for them
    "A2": "refused",            # WILL verdict:/unless:, and the next lap's triggers:
    "A3": "refused",            # FINDING, and whose it is
    "A4": "refused",            # a FACT names what it holds for (holds:)
    "A5": "refused",            # a measurement names its population (examined:)
    "A6": "refused",            # only a checkable claim in basis: or because:
    "A7": "refused",            # answers:, and a GO that waits for blocking ASKs
    "A8": "refused",            # a CORRECT carries evidence
    # LSL 3's, accepted in round 28 under the ids cyanrip proposed them by.
    "B1": "refused",            # a run: names its commit, and re-runs to its result
    "B2": "refused",            # a GO needs at least one close condition
    "B3": "refused",            # answers: only on a statement that carries weight
    # HR-2's (PROTOCOL.md v9 §17), for every LSL version from a side's move.
    "HR-2.6a": "refused",       # an evidence citation's SHA-256 and branch
    "HR-2.6b": "refused",       # its manifest row, its bytes, or no fetch in CI
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

# LSL 2: what each amendment adds. A kind, grade or field in these is refused
# in an LSL 1 lap exactly as before, by LSL.1 and LSL.field.
KINDS2 = {"TERM": {"set", "met", "unmet", "waived", "pending"},    # A1
          "FINDING": {"ours", "yours", "upstream", "unknown"}}     # A3
# (kind, grade) -> [(field, the amendment that requires it)]
REQUIRED2 = {
    ("FACT", "measured"): [("holds", "A4"), ("examined", "A5")],
    ("FACT", "read"): [("holds", "A4")],
    ("FACT", "reproduced"): [("holds", "A4")],
    ("NONE", None): [("examined", "A5")],
    ("CORRECT", None): [("evidence", "A8")],
    ("TERM", "set"): [("requires", "A1")],
    ("TERM", "met"): [("term", "A1"), ("evidence", "A1")],
    ("TERM", "unmet"): [("term", "A1"), ("reason", "A1")],
    ("TERM", "waived"): [("term", "A1"), ("override", "A1")],
    ("TERM", "pending"): [("term", "A1"), ("on", "A1"), ("remains", "A1")],
}
for _g in KINDS2["FINDING"]:
    REQUIRED2[("FINDING", _g)] = [("in", "A3"), ("shape", "A3"),
                                  ("target", "A3"), ("evidence", "A3")]
FIELDS2 = {"requires": "A1", "restates": "A1", "regression": "A1",
           "term": "A1", "override": "A1", "on": "A1", "remains": "A1",
           "verdict": "A2", "unless": "A2", "triggers": "A2",
           "in": "A3", "shape": "A3", "landed": "A3", "portable": "A3",
           "holds": "A4", "examined": "A5", "missing": "A5",
           "answers": "A7"}
# A6: what cannot carry a verdict or a refusal, because nothing checks it.
UNWEIGHTED = {("NOTE", None), ("ASK", None), ("VERDICT", None),
              ("WILL", None), ("UNKNOWN", None), ("FACT", "relayed")}

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
# The versions this checker implements, in one place. LSL_RE listed 1-3 after
# LSL 4 landed (049886f) while parse() accepted 4, so a held LSL 4 lap parsed
# and a statement in it could not be cited: "a prose lap". Round 30 lap 7.
LSL_VERSIONS = (1, 2, 3, 4)
LSL_RE = re.compile(r"^LSL: (" + "|".join(map(str, LSL_VERSIONS)) + r")\s*$", re.M)


def _versions_said():
    """LSL_VERSIONS as a sentence says it: "1, 2, 3 and 4"."""
    v = [str(n) for n in LSL_VERSIONS]
    return v[0] if len(v) == 1 else ", ".join(v[:-1]) + " and " + v[-1]
# A4: holds: must name a commit or a version.
HOLDS_RE = re.compile(r"\b[0-9a-f]{7,40}\b|\b\d+\.\d+(?:\.\d+)?\b")
# A5: examined: <n> <unit>, closed|open
EXAMINED_RE = re.compile(r"^(\d+) (\S.*), (closed|open)$")

# LSL 3, B1: which `run:` commands a checker re-runs. Only what can depend on
# nothing but the commit it names: a read-only git query, a checksum or count
# over paths in the tree, or one of the author's committed tools that declares
# as much in its own first lines. Everything else is reported unchecked, never
# guessed at, and nothing is ever passed to a shell.
FIELDS3 = {"at": "B1"}
RERUN_MARK = "LSL-RERUN: commit-only"
GIT_READ = {"log", "show", "diff", "rev-parse", "merge-base", "ls-tree",
            "cat-file", "rev-list"}
PLAIN = {"sha256sum", "wc"}
# `python` is not `python3`: the text names python3, and which interpreter
# `python` is depends on the machine (round 29 lap 1 S29).
INTERPRETERS = {"python3"}
NOT_SIMPLE = set("|;&<>`$()*?[]{}\\\n") | {"…"}
# The marker counts as a LINE that begins with it once the file's comment
# marker and the spaces after it are off, not as a substring anywhere, so a
# string in the tool's code that happens to spell it does not mark it.
MARK_LINE_RE = re.compile(r"^\s*(?:#+|//+|/\*+|\*+|--|;+)?\s*"
                          + re.escape(RERUN_MARK))
# `exit N` as a result states it (their round 29 lap 2 S15): lower case, one
# space, `exit` a word of its own and N digits that are not the start of a
# longer word, read outside the quotes with each quote a gap between words.
EXIT_RE = re.compile(r"(?<![\w-])exit ([0-9]{1,9})(?!\w)")
# What makes a read-only git query depend on more than its commit: a moving
# ref, the clock, or where the checkout is (round 29 lap 1 S29).
PSEUDO_REFS = {"FETCH_HEAD", "ORIG_HEAD", "MERGE_HEAD", "CHERRY_PICK_HEAD",
               "REVERT_HEAD", "REBASE_HEAD", "BISECT_HEAD", "AUTO_MERGE"}
REF_OPTIONS = {"--all", "--branches", "--tags", "--remotes", "--glob",
               "--exclude", "--reflog"}
CLOCK_OPTION_RE = re.compile(
    r"^--(?:since|until|after|before|max-age|min-age)(?:=|$)"
    r"|^--relative-date$|^--date=(?:relative|human)$")
CLOCK_FORMAT_RE = re.compile(r"%[ac][rh]")
LOCATION_OPTIONS = {"--show-toplevel", "--show-prefix", "--show-cdup",
                    "--git-dir", "--absolute-git-dir", "--git-common-dir",
                    "--show-superproject-working-tree", "--git-path",
                    "--resolve-git-dir"}
QUOTED_RE = re.compile(r'"([^"]+)"')
AT_RE = re.compile(r"^(?:(cyanrip|platterpus)@)?([0-9a-f]{7,40})$")

# Where held laps are read from; --laps moves it (tests use it).
LAPS = ROOT / "docs" / "handshake"


class Lap:
    def __init__(self, path, text):
        self.path = path
        self.text = text
        self.refusals = []
        self.warnings = []
        self.headers = {}
        self.statements = []
        self.version = None
        self.notes = []     # what a check was run over, printed with the result

    def refuse(self, line, rule, msg):
        assert RULES[rule] in ("refused", "could not check"), rule
        self.refusals.append((line, rule, msg))

    def warn(self, line, rule, msg):
        assert RULES[rule] == "warning", rule
        self.warnings.append((line, rule, msg))


def _fenced_lines(text):
    """v8 §2 rule 2's fence (E10), from the one function every reader of a lap
    in this tree shares, beside the digest."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "round_digest_fences", pathlib.Path(__file__).resolve().parent / "round-digest.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.fenced_lines(text)


def parse(lap):
    """Split the file into wire headers and statements; return False if not LSL.

    A header line or an `LSL:` line inside a fenced block is a quotation, not a
    declaration, so the header pass skips fenced lines (E10). Until v8 this
    checker read every line before the marker, fenced or not. The statements
    after the marker are read as they stand: a fence there is not LSL, and is
    refused as any other prose line is."""
    lines = lap.text.splitlines()
    fenced = _fenced_lines("\n".join(lines))
    start = None
    for i, line in enumerate(lines):
        if start is None and i in fenced:
            continue
        m = WIRE_RE.match(line)
        if m and start is None:
            lap.headers.setdefault(m.group(1), []).append(m.group(2))
        if line.rstrip().startswith("LSL:") and start is None:
            if not LSL_RE.fullmatch(line.rstrip()):
                lap.refuse(i + 1, "LSL.version",
                           f"declares {line.strip()!r}; this checker "
                           f"implements LSL {_versions_said()} only")
                return False
            lap.version = int(line.rstrip()[-1])
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


def _decoded(data):
    """git's output as text, whatever encoding a cited file is in.

    `text=True` decoded every `git show` as strict UTF-8, so citing a UTF-16
    file, which is how EAC writes its logs, raised and stopped the whole
    check. Platterpus's checker had the same defect and found it first
    (their round 30 lap 16 S15). A byte-order mark names the codec;
    anything else is UTF-8 with undecodable bytes replaced, so a line is
    counted as an editor shows it. Newlines are normalised as `text=True`
    did, so nothing that decoded before reads differently now.
    """
    if data.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        text = data.decode("utf-16", "replace")
    elif data.startswith(codecs.BOM_UTF8):
        text = data.decode("utf-8-sig", "replace")
    else:
        text = data.decode("utf-8", "replace")
    return text.replace("\r\n", "\n").replace("\r", "\n")


# HR-1.6: one reading of Platterpus's commit maps, shared with seam-sync-check.
_spec = importlib.util.spec_from_file_location(
    "commit_map", pathlib.Path(__file__).resolve().parent / "commit-map.py")
COMMIT_MAP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(COMMIT_MAP)
# HR-2 (PROTOCOL.md v9 §17): where run evidence is, and how it is fetched.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import evidence as EVIDENCE  # noqa: E402
SHA256_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    return subprocess.CompletedProcess(r.args, r.returncode,
                                       _decoded(r.stdout), _decoded(r.stderr))


class Resolver:
    """Resolves commits and artifacts in each side's tree, if given one."""

    def __init__(self, ours, peer, refs):
        self.repo = {"cyanrip": ours, "platterpus": peer}
        self.maps = {}
        self.refs = dict(RECORD)
        self.refs.update(refs)
        self.located = {}
        self.record_ref = {}
        self.ev_stores = {}
        # HR-2 6d: the bytes of each evidence citation judged, so B1 can
        # place them at their own paths before it re-runs a command.
        self.ev_files = {}

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

    def mapped(self, side, sha):
        """`sha` through HR-1.6, as (sha, problem).

        Platterpus rewrote its history once and old IDs stay as sent, so a
        Platterpus value is looked up in the commit maps in Platterpus's own
        tree BEFORE it is resolved in the clone: a clone made before the
        rewrite still holds the old objects, which are not on the new history
        (HR-1.6 (d)). problem is None, or (verdict, detail) to report instead
        of resolving. A cyanrip ID is never looked up in a map."""
        if side != "platterpus" or self.repo.get(side) is None:
            return sha, None
        if side not in self.maps:
            rec = self._record(side)
            try:
                self.maps[side] = COMMIT_MAP.parse(COMMIT_MAP.read_maps_from(
                    self.repo[side], rec))
            except COMMIT_MAP.MapError as e:
                self.maps[side] = e
        maps = self.maps[side]
        if isinstance(maps, COMMIT_MAP.MapError):
            return sha, ("unchecked", f"{side}'s commit map does not read "
                                      f"cleanly, so {sha} is not resolved "
                                      f"through it: {maps} (HR-1.6 (f))")
        verdict, new, note = COMMIT_MAP.resolve(maps, sha)
        if verdict == "ambiguous":
            return sha, ("missing", note)
        return (new if verdict == "mapped" else sha), None

    def locate(self, side, sha):
        """Where `sha` is in `side`'s tree, as (verdict, detail).

        verdict is one of: ok, offrecord, unchecked, missing."""
        key = (side, sha)
        if key in self.located:
            return self.located[key]
        sha, problem = self.mapped(side, sha)
        repo = self.repo[side]
        if problem:
            got = problem
        elif repo is None:
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

    def _ev_store(self, side):
        """A store over side's clone: its evidence tips and its cache."""
        if side not in self.ev_stores:
            repo = self.repo.get(side)
            self.ev_stores[side] = EVIDENCE.Store(
                repo, manifest=EVIDENCE.HEADER + "\n") if repo else None
        return self.ev_stores[side]

    def evidence_row(self, lap, side, sha, path):
        """(row, problem, decided): the manifest row naming side@sha:path.
        decided is False when the manifest could not be read at all, which
        is a reason to report the citation unchecked, never to refuse it.

        For the author's own evidence, the manifest at the lap's
        HANDSHAKE-FROM-COMMIT (HR-2 6b); for the other side's, at that
        side's ref of record, since the author's manifest lists only its own
        branch (a copy the author holds is on its own branch, 6c)."""
        repo = self.repo[side]
        author = FROM_SIDE.get((lap.headers.get("FROM") or [""])[0].strip())
        if side == author:
            froms = [v.split()[0] for v in lap.headers.get("FROM-COMMIT", [])
                     if v.split()]
            if len(froms) != 1:
                return (None, "the lap declares no single "
                              "HANDSHAKE-FROM-COMMIT", True)
            rev = self.mapped(side, froms[0])[0]
            where = f"the lap's HANDSHAKE-FROM-COMMIT, {froms[0]}"
        else:
            rec = self._record(side)
            if not rec:
                return (None, f"{side}'s ref of record is not in the clone "
                              f"given", False)
            rev, where = rec[0], f"{side}'s {self.refs[side]}"
        if git(repo, "rev-parse", "--verify", "--quiet",
               f"{rev}^{{commit}}").returncode != 0:
            return None, f"{where} is not in {side}'s clone", False
        try:
            rows = EVIDENCE.manifest_at(repo, rev)
        except EVIDENCE.ManifestError as e:
            return (None, f"{side}'s manifest at {where} does not read: "
                          f"{e}", True)
        hits = [r for r in rows if r.path == path and r.commit.startswith(sha)]
        if len(hits) != 1:
            return None, (f"no row in {EVIDENCE.MANIFEST} at {where} names "
                          f"{path} at {sha}"), True
        return hits[0], None, True

    def evidence_citation(self, lap, line, side, sha, path, a, b, rest):
        """HR-2 6a and 6b. True when side@sha:path is an evidence citation and
        has been judged; False to judge it as any other artifact.

        It is one when the manifest names it, or when the commit is on the
        side's evidence branch: the evidence branch is a second ref of record
        for these citations, and only for these."""
        repo = self.repo.get(side)
        store = self._ev_store(side)
        if repo is None or store is None:
            return False
        row, problem, decided = self.evidence_row(lap, side, sha, path)
        present = git(repo, "rev-parse", "--verify", "--quiet",
                      f"{sha}^{{commit}}").returncode == 0
        on = EVIDENCE.on_evidence(store, sha) if present else None
        if row is None:
            if on is not True:
                return False
            if not decided:
                lap.warn(line, "LSL.unchecked",
                         f"UNCHECKED {side}@{sha}:{path}: on {side}'s evidence "
                         f"branch, and {problem}, so its manifest row cannot "
                         f"be looked for")
                return True
            lap.refuse(line, "HR-2.6b",
                       f"{side}@{sha}:{path} is on {side}'s evidence branch, "
                       f"and {problem}: a lap is written from a commit that "
                       f"already has the rows (HR-2 10)")
            return True
        quoted = SHA256_RE.findall(rest)
        if not quoted:
            lap.refuse(line, "HR-2.6a",
                       f"{side}@{sha}:{path} cites evidence without its "
                       f"SHA-256; the manifest row gives {row.sha256}")
        elif quoted[0] != row.sha256:
            lap.refuse(line, "HR-2.6a",
                       f"{side}@{sha}:{path} quotes SHA-256 {quoted[0][:16]}..."
                       f", and its manifest row says {row.sha256[:16]}...")
        full, why = row.commit, ""
        data = store._blob(repo, full, path) or store._blob(store.cache, full,
                                                              path)
        reach = EVIDENCE.on_evidence(store, full)
        if data is None or reach is None:
            # A missing commit is fetched by its hash into a separate
            # repository, never into the clone given (HR-2 6b, 7).
            try:
                EVIDENCE.fetch(store, [full], EVIDENCE.remote_url(repo),
                               branch=True)
            except (RuntimeError, OSError) as e:
                why = str(e).splitlines()[0][:160]
            data = data or store._blob(store.cache, full, path)
            reach = EVIDENCE.on_evidence(store, full)
        if data is None or reach is None:
            msg = (f"UNCHECKED {side}@{sha}:{path}: an evidence citation "
                   f"whose commit could not be fetched"
                   + (f" ({why})" if why else ""))
            if EVIDENCE.required():
                lap.refuse(line, "HR-2.6b", msg + f"; refused, as "
                           f"{EVIDENCE.REQUIRED_ENV}=1 says this is CI's "
                           f"evidence job")
            else:
                lap.warn(line, "LSL.unchecked", msg)
            return True
        if reach is False:
            lap.refuse(line, "HR-2.6a",
                       f"{full[:12]} is not reachable from {side}'s "
                       f"refs/heads/{EVIDENCE.BRANCH}")
            return True
        if len(data) != row.size or EVIDENCE.sha256(data) != row.sha256:
            lap.refuse(line, "HR-2.6b",
                       f"{side}@{sha}:{path} is {len(data)} bytes, sha256 "
                       f"{EVIDENCE.sha256(data)[:16]}..., and its manifest row "
                       f"says {row.size} bytes, {row.sha256[:16]}...")
            return True
        self.ev_files[(side, sha, path)] = data
        self._lines(lap, line, side, full, path, data.decode(
            "utf-8", "replace"), a, b)
        return True

    def _lines(self, lap, line, side, sha, path, text, a, b):
        # A final line counts whether or not it ends in a newline (our
        # round 30 lap 1 S20, accepting Platterpus's round 29 lap 4 S33).
        # Counting newline characters alone made the last line of such a
        # file uncitable.
        got = text.count("\n") + (1 if text and not text.endswith("\n")
                                  else 0)
        lo, hi = a, (b if b is not None else a)
        if lo is not None:
            if lo < 1 or hi < lo:
                lap.refuse(line, "LSL.4", f"line range {a}-{b} is not a range")
            elif hi > got:
                lap.refuse(line, "LSL.4",
                           f"{side}@{sha}:{path} has {got} lines; "
                           f"line {hi} does not exist")

    def artifact(self, lap, line, side, sha, path, a, b, rest=""):
        if self.locate(side, sha)[0] != "ok" and self.evidence_citation(
                lap, line, side, sha, path, a, b, rest):
            return
        if not self._report(lap, line, side, sha):
            return
        # A path or line claim is checked at the mapped commit (HR-1.6 (e)).
        sha = self.mapped(side, sha)[0]
        r = git(self.repo[side], "show", f"{sha}:{path}")
        if r.returncode != 0:
            lap.refuse(line, "LSL.4", f"{path} does not exist at {side}@{sha}")
            return
        self._lines(lap, line, side, sha, path, r.stdout, a, b)

    def commit(self, lap, line, side, sha):
        self._report(lap, line, side, sha)


def lap_file(side, rnd, lp):
    name = f"round-{int(rnd):02d}-lap-{int(lp):02d}.md"
    if side == "cyanrip":
        return LAPS / name
    return LAPS / "inbound" / name


def statement_ids(text):
    """The S-numbers of an LSL lap, or None for a prose lap."""
    if not LSL_RE.search(text):
        return None
    return {int(m.group(1)) for m in
            re.finditer(r"^S(\d+) [A-Z]+", text, re.M)}


_HELD = {}


def held(side, rnd, lp):
    """A held lap, parsed but not checked, or None if not held or not LSL."""
    key = (side, int(rnd), int(lp))
    if key not in _HELD:
        f = lap_file(*key)
        lap = None
        if f.exists():
            lap = Lap(f, f.read_text(encoding="utf-8", errors="replace"))
            if not parse(lap):
                lap = None
        _HELD[key] = lap
    return _HELD[key]


def round_laps(me, this):
    """Every LSL lap of this round we hold, both sides, up to and including
    this one, as {(side, lap): Lap}. The lap under check stands in for any
    held copy of itself, which may be an older draft."""
    side, rnd, lp = me
    out = {}
    for s in SIDES:
        d = LAPS if s == "cyanrip" else LAPS / "inbound"
        for f in d.glob(f"round-{rnd:02d}-lap-*.md"):
            m = re.fullmatch(rf"round-{rnd:02d}-lap-(\d+)\.md", f.name)
            if not m or int(m.group(1)) > lp or (s, int(m.group(1))) == (side, lp):
                continue
            h = held(s, rnd, int(m.group(1)))
            if h is not None:
                out[(s, int(m.group(1)))] = h
    out[(side, lp)] = this
    return out


def field(s, name):
    return [v for f, v, _ in s["fields"] if f == name]


def resolve_stmt(token, me, this):
    """The statement a reference names, as (side, lap, statement), or None."""
    m = STMT_RE.match(token)
    if not m or m.group(4).startswith("§"):
        return None
    side, rnd, lp, target = m.groups()
    n = int(target[1:])
    if side is None or (side, int(rnd), int(lp)) == me:
        lap, side, lp = this, me[0], me[2]
    else:
        lap, lp = held(side, rnd, lp), int(lp)
    if lap is None:
        return None
    for s in lap.statements:
        if s["n"] == n:
            return side, lp, s
    return None


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


def other(side):
    return "platterpus" if side == "cyanrip" else "cyanrip"


def weight_key(s):
    return (s["kind"], s["grade"] if s["kind"] == "FACT" else None)


def unweighted(lap, line, tag, name, token, me):
    """A6: a basis: or because: must name a claim somebody can check."""
    got = resolve_stmt(token, me, lap)
    if got and weight_key(got[2]) in UNWEIGHTED:
        k = " ".join(x for x in weight_key(got[2]) if x)
        lap.refuse(line, "A6", f"{tag}: {name}: {token} is a {k}, which "
                               f"nothing can check, so it carries no weight")


def check_v2(lap, s, tag, have, me, by_n, resolver):
    """LSL 2's field shapes and per-statement rules, one amendment at a time."""
    kind, grade, n = s["kind"], s["grade"], s["line"]
    me_side = me[0]

    # A1: TERM
    for value, fl in have.get("on", []):
        if value not in ("us", "them"):
            lap.refuse(fl, "A1", f"{tag}: on: is us or them, not {value!r}")
    for value, fl in have.get("term", []):
        for token in re.split(r"[,\s]+", value.strip()):
            got = resolve_stmt(token, me, lap) if token else None
            if not token:
                continue
            if got is None or (got[2]["kind"], got[2]["grade"]) != ("TERM", "set"):
                lap.refuse(fl, "A1", f"{tag}: term: {token} does not name a "
                                     f"TERM set this tree holds")
    for value, fl in have.get("restates", []):
        first = value.split()[0]
        if check_stmt_ref(lap, fl, first, me, set(by_n)):
            continue
        ref = art_ref(first)
        if ref:
            resolver.artifact(lap, fl, *ref, rest=value[len(first):])
        else:
            lap.refuse(fl, "A1", f"{tag}: restates: {first!r} is neither a "
                                 f"statement, a section nor an artifact")
    if (kind, grade) == ("TERM", "set") and me[2] and me[2] > 1 \
            and "restates" not in have and "regression" not in have:
        lap.refuse(n, "A1", f"{tag}: close conditions are fixed in lap 1 "
                            f"(S-13), so after it a TERM set restates one "
                            f"(restates:) or names a regression (regression:)")

    # A2: a pre-commit
    if "verdict" in have and kind != "WILL":
        lap.refuse(have["verdict"][0][1], "A2",
                   f"{tag}: only a WILL carries a pre-committed verdict:")
    for value, fl in have.get("verdict", []):
        if value not in ("GO", "HOLD"):
            lap.refuse(fl, "A2", f"{tag}: verdict: is GO or HOLD")
        if kind == "WILL" and [v for v, _ in have.get("owner", [])] != ["us"]:
            lap.refuse(fl, "A2", f"{tag}: a pre-committed verdict: is the "
                                 f"author's, so owner: is us")
    if "unless" in have and "verdict" not in have:
        lap.refuse(have["unless"][0][1], "A2",
                   f"{tag}: unless: qualifies a verdict:, and there is none")
    # LSL 4: a pre-commit's when: is the literal the binding reads (our round
    # 30 lap 3 S10, amended by Platterpus's lap 4 S36). A2 binds the author's
    # next LSL lap, so a verdict: promised for any other moment is one the
    # checker would enforce at the wrong lap; and no checker can decide what
    # "before our closing lap" means.
    if lap.version is not None and lap.version >= 4 and kind == "WILL" \
            and "verdict" in have:
        whens = [v for v, _ in have.get("when", [])]
        if whens != ["our next lap"]:
            lap.refuse(have["verdict"][0][1], "A2",
                       f"{tag}: in LSL 4 a WILL carrying verdict: says exactly "
                       f"'when: our next lap', the lap A2 binds; it says "
                       f"{whens or 'no when:'}")
    for value, fl in have.get("triggers", []):
        for token in re.split(r"[,\s]+", value.strip()):
            if not token:
                continue
            got = resolve_stmt(token, me, lap)
            if (got is None or got[0] != me_side or got[1] >= me[2]
                    or got[2]["kind"] != "WILL" or not field(got[2], "verdict")):
                lap.refuse(fl, "A2", f"{tag}: triggers: {token} does not name "
                                     f"a pre-committed WILL in an earlier lap "
                                     f"of the author's")

    # A3: FINDING
    if kind == "FINDING":
        targets = [v for v, _ in have.get("target", [])]
        for value, fl in have.get("target", []):
            if value not in ("NEXT-ROUND", "BLOCKING", "FIXED"):
                lap.refuse(fl, "A3", f"{tag}: a FINDING's target: is "
                                     f"NEXT-ROUND, BLOCKING or FIXED")
        if "BLOCKING" in targets and "breaks" not in have:
            lap.refuse(n, "A3", f"{tag}: a BLOCKING finding names what it "
                                f"breaks in the pin (breaks:)")
        if "FIXED" in targets and "landed" not in have:
            lap.refuse(n, "A3", f"{tag}: a FIXED finding names where the fix "
                                f"landed (landed:)")
        if grade == "ours" and "portable" not in have:
            lap.refuse(n, "A3", f"{tag}: a finding of ours says whether its "
                                f"shape could hold in the other side's code "
                                f"(portable:)")
        for value, fl in have.get("portable", []):
            if value not in ("yes", "no"):
                lap.refuse(fl, "A3", f"{tag}: portable: is yes or no")
        # cyanrip's amendment, round 28 lap 1 S21: R9 puts a finding the
        # other side need not act on in a commit, not a lap.
        if (grade == "ours" and [v for v, _ in have.get("portable", [])] == ["no"]
                and targets and "BLOCKING" not in targets):
            lap.refuse(n, "A3", f"{tag}: a finding of ours that cannot hold in "
                                f"the other side's code and blocks nothing is "
                                f"for a commit, not a lap")
        for name in ("in", "landed"):
            for value, fl in have.get(name, []):
                ref = art_ref(value.split()[0])
                if ref is None:
                    lap.refuse(fl, "A3", f"{tag}: {name}: is an artifact "
                                         f"reference, side@commit:path")
                    continue
                if grade == "ours" and ref[0] != me_side:
                    lap.refuse(fl, "A3", f"{tag}: a finding of ours is in "
                                         f"{me_side}'s tree, not {ref[0]}'s")
                elif grade == "yours" and name == "in" and ref[0] == me_side:
                    lap.refuse(fl, "A3", f"{tag}: a finding of yours cannot be "
                                         f"in the author's own tree")
                resolver.artifact(lap, fl, *ref,
                                  rest=value[len(value.split()[0]):])

    # A4, A5
    for value, fl in have.get("holds", []):
        if not HOLDS_RE.search(value):
            lap.refuse(fl, "A4", f"{tag}: holds: names a commit or a version "
                                 f"the fact covers")
    for value, fl in have.get("examined", []):
        m = EXAMINED_RE.match(value)
        if not m:
            lap.refuse(fl, "A5", f"{tag}: examined: is '<n> <unit>, closed' "
                                 f"or '<n> <unit>, open'")
        elif int(m.group(1)) < 1:
            lap.refuse(fl, "A5", f"{tag}: examined: 0 -- a measurement over "
                                 f"nothing is satisfied by finding nothing")
        elif m.group(3) == "open" and "missing" not in have:
            lap.refuse(fl, "A5", f"{tag}: an open population names what is "
                                 f"missing from it (missing:)")

    # A7, and B3 in an LSL 3 lap: answers: only on a statement that carries
    # weight, because a NOTE that answers a blocking question says nothing a
    # reader could check (our round 28 lap 3 S20).
    if lap.version is not None and lap.version >= 3 and have.get("answers") \
            and weight_key(s) in UNWEIGHTED:
        k = " ".join(x for x in weight_key(s) if x)
        lap.refuse(have["answers"][0][1], "B3",
                   f"{tag}: answers: on a {k}, which carries no claim, so it "
                   f"answers nothing")
    for value, fl in have.get("answers", []):
        for token in re.split(r"[,\s]+", value.strip()):
            if not token:
                continue
            got = resolve_stmt(token, me, lap)
            if got is None or got[0] == me_side or got[2]["kind"] != "ASK":
                lap.refuse(fl, "A7", f"{tag}: answers: {token} does not name "
                                     f"an ASK of the other side's we hold")


def waits(lap, line, tag, me, resolver):
    """A1 and A7: a GO waits for every close condition, and for the other
    side's blocking questions. Read over every lap of the round we hold."""
    me_side, rnd, lp = me
    if None in me:
        return
    laps = round_laps(me, lap)

    # A1
    sets, status = {}, {}
    for (side, lpn), L in sorted(laps.items(), key=lambda kv: kv[0][1]):
        if L.version is None or L.version < 2:
            continue
        for s in L.statements:
            if s["kind"] != "TERM":
                continue
            if s["grade"] == "set":
                sets[(side, lpn, s["n"])] = s
                continue
            for value in field(s, "term"):
                for token in re.split(r"[,\s]+", value.strip()):
                    got = token and resolve_stmt(token, (side, rnd, lpn), L)
                    if not got:
                        continue
                    on = [v for v in field(s, "on")]
                    on_side = (side if on == ["us"] else
                               other(side) if on == ["them"] else None)
                    status.setdefault((got[0], got[1], got[2]["n"]), []).append(
                        (lpn, s["n"], s["grade"], on_side, side))
    for key, s in sorted(sets.items()):
        name = f"{key[0]}:R{rnd}.L{key[1]}.S{key[2]}"
        got = sorted(status.get(key, []))
        if not got:
            lap.refuse(line, "A1", f"{tag}: close condition {name} has no "
                                   f"status in any lap of round {rnd} we hold")
            continue
        _, sn, grade, on_side, by = got[-1]
        if grade == "unmet":
            lap.refuse(line, "A1", f"{tag}: close condition {name} is unmet")
        elif grade == "pending" and on_side == me_side:
            lap.refuse(line, "A1", f"{tag}: close condition {name} is pending "
                                   f"on the author's own side; a side may say "
                                   f"GO over the other side's pending half, "
                                   f"never over its own")
    v3 = lap.version is not None and lap.version >= 3
    if v3 and not sets:
        # B2: A1 over no close condition passes by finding nothing, so an
        # LSL 3 GO needs at least one to have waited for (round 28 lap 3 S19).
        lap.refuse(line, "B2", f"{tag}: a GO in LSL 3 waits for at least one "
                               f"close condition, and no lap of round {rnd} "
                               f"this tree holds writes one as TERM set")
    lap.notes.append(f"A1: this GO was checked against {len(sets)} close "
                     f"condition(s) written as TERM set in the laps of round "
                     f"{rnd} this tree holds"
                     + ("; none is, so A1 had nothing to wait for" if not sets
                        else ""))

    # A7
    asks = {(side, lpn, s["n"]) for (side, lpn), L in laps.items()
            if side != me_side and lpn < lp for s in L.statements
            if s["kind"] == "ASK" and "BLOCKING" in field(s, "target")}
    answered = set()
    for (side, lpn), L in laps.items():
        if side != me_side:
            continue
        for s in L.statements:
            if v3 and weight_key(s) in UNWEIGHTED:
                continue    # B3: an answer that carries no claim is none
            for value in field(s, "answers"):
                for token in re.split(r"[,\s]+", value.strip()):
                    got = token and resolve_stmt(token, (side, rnd, lpn), L)
                    if got:
                        answered.add((got[0], got[1], got[2]["n"]))
    for key in sorted(asks - answered):
        lap.refuse(line, "A7", f"{tag}: {key[0]}:R{rnd}.L{key[1]}.S{key[2]} is "
                               f"a BLOCKING question with no answers: from "
                               f"the author")
    lap.notes.append(f"A7: {len(asks)} blocking question(s) of "
                     f"{other(me_side)}'s in the laps held, "
                     f"{len(asks & answered)} answered")


def pre_committed(lap, s, line, tag, me):
    """A2: the author's previous LSL lap's pre-commit binds this one."""
    me_side, rnd, lp = me
    if None in me:
        return
    said = s["sentence"].split()[0].rstrip(".")
    prev = [(lpn, L) for (side, lpn), L in round_laps(me, lap).items()
            if side == me_side and lpn < lp]
    if not prev:
        return
    lpn, L = max(prev, key=lambda x: x[0])
    triggered = set()
    for t in lap.statements:
        for value in field(t, "triggers"):
            for token in re.split(r"[,\s]+", value.strip()):
                got = token and resolve_stmt(token, me, lap)
                if got:
                    triggered.add((got[0], got[1], got[2]["n"]))
    for w in L.statements:
        promised = field(w, "verdict") if w["kind"] == "WILL" else []
        if promised and promised[0] != said and \
                (me_side, lpn, w["n"]) not in triggered:
            lap.refuse(line, "A2",
                       f"{tag}: says {said}, and {me_side}:R{rnd}.L{lpn}."
                       f"S{w['n']} pre-committed {promised[0]}; a statement "
                       f"with triggers: naming it must say which unless: "
                       f"came true")


def b1_at(lap, tag, have, me_side, resolver):
    """B1: `at:` on ANY statement names one commit of the author's tree.

    Returns None when the statement has no at:, False when it has one that is
    refused, else the commit. Round 28 lap 6 S26 found three places the first
    version was laxer than the text: it read only the first at:, checked a
    commit's shape and side but not that it is in the author's tree, and read
    at: only on a statement whose evidence had a run:. All three are here."""
    ats = have.get("at", [])
    if not ats:
        return None
    if len(ats) > 1:
        lap.refuse(ats[1][1], "B1", f"{tag}: at: names the one commit a run: "
                                    f"ran at, and this statement has "
                                    f"{len(ats)}")
        return False
    value, fl = ats[0]
    m = AT_RE.match(value.strip())
    if not m or (m.group(1) and m.group(1) != me_side):
        lap.refuse(fl, "B1", f"{tag}: at: names a commit of the author's "
                             f"tree, as <sha> or {me_side}@<sha>")
        return False
    sha = m.group(2)
    if me_side is not None and resolver.repo.get(me_side) is not None:
        verdict, detail = resolver.locate(me_side, sha)
        if verdict == "missing":
            lap.refuse(fl, "B1", f"{tag}: at: names a commit of the author's "
                                 f"tree, and {detail}")
            return False
        if verdict == "unchecked":
            lap.warn(fl, "LSL.unchecked", f"UNCHECKED at: {detail}")
    return sha


def b1_run(lap, line, tag, value, have, at_sha, me_side, resolver, counts):
    """B1: a run: in LSL 3 names the commit it ran at, and with --rerun is
    re-run there when its command can depend on nothing but that commit."""
    cmd, _, result = value[len("run: "):].partition(" => ")
    counts["seen"] += 1
    if at_sha is False:
        return
    if at_sha:
        sha = at_sha
    else:
        froms = [v.split()[0] for v in lap.headers.get("FROM-COMMIT", [])
                 if v.split()]
        if len(froms) != 1 or not re.fullmatch(r"[0-9a-f]{7,40}", froms[0]):
            lap.refuse(line, "B1", f"{tag}: a run: in LSL 3 names the commit "
                                   f"it ran at: an at: field on the statement, "
                                   f"or the lap's HANDSHAKE-FROM-COMMIT")
            return
        sha = froms[0]
    if not getattr(resolver, "rerun", False) or me_side is None:
        return
    # HR-2 6d: the evidence this statement cites, at its own paths, in the
    # tree the command is re-run in. After a move the run's files are on the
    # evidence branch and not in that tree.
    cited = {}
    for v, _ in have.get("evidence", []):
        ref = art_ref(v.split()[0])
        if ref and ref[0] == me_side and \
                (me_side, ref[1], ref[2]) in resolver.ev_files:
            cited[ref[2]] = resolver.ev_files[(me_side, ref[1], ref[2])]
    verdict, detail = rerun(resolver, me_side, sha, cmd, result, cited)
    counts[verdict] += 1
    if verdict == "mismatch":
        lap.refuse(line, "B1", f"{tag}: re-run at {me_side}@{sha}, and "
                               f"{detail}")
    elif verdict == "unchecked":
        lap.warn(line, "LSL.unchecked", f"UNCHECKED run: {detail}")


def git_moves(repo, args):
    """Why a read-only git query depends on more than its commit, or None.

    A ref other than HEAD moves (in the scratch worktree HEAD is the commit),
    so does anything reading the clone's refs or the clock, and a path to the
    checkout names the scratch worktree, not what the commit holds. Each turns
    a re-run into UNCHECKED and never into a refusal (round 29 lap 1 S29)."""
    listed = git(repo, "for-each-ref", "--format=%(refname)%09%(refname:short)")
    refs = {p for ln in listed.stdout.splitlines() for p in ln.split("\t") if p}
    for arg in args:
        if arg == "--":
            return None  # the rest are paths
        if arg.startswith("-"):
            opt = arg.split("=", 1)[0]
            if CLOCK_OPTION_RE.match(arg) or (
                    opt in ("--format", "--pretty") and CLOCK_FORMAT_RE.search(arg)):
                return f"{arg} reads the clock, so its answer is not the commit's alone"
            if opt in REF_OPTIONS:
                return f"{arg} reads the clone's refs, which move"
            if opt in LOCATION_OPTIONS:
                return f"{arg} prints where the checkout is, not what the commit holds"
            continue
        if "@{" in arg:
            return f"{arg} reads a reflog, which moves"
        for side in re.split(r"\.\.\.?", arg.split(":", 1)[0].lstrip("^")):
            base = re.split(r"[~^@]", side, maxsplit=1)[0]
            if base and base != "HEAD" and (base in refs or base in PSEUDO_REFS):
                return (f"{arg} names the ref {base}, which can move; only a "
                        f"SHA or HEAD names what the command ran at")
    return None


def rerun(resolver, side, sha, cmd, result, evidence_files=None):
    """Re-run one command at one commit of the author's tree, as (verdict,
    detail), verdict one of ok, mismatch, unchecked. evidence_files, path to
    bytes, are placed at their paths in that tree first (HR-2 6d)."""
    repo = resolver.repo.get(side)
    if repo is None:
        return "unchecked", f"no clone of {side}'s tree was given"
    sha, problem = resolver.mapped(side, sha)
    if problem:
        return "unchecked", problem[1]
    quoted = QUOTED_RE.findall(result)
    if not quoted:
        return "unchecked", "its result quotes no output to compare"
    # A quote that is only an elision compares nothing, so it cannot match
    # (round 28 lap 6 S27, first of four).
    quoted = [q for q in quoted if any(f.strip() for f in q.split("…"))]
    if not quoted:
        return "unchecked", ("its result quotes only an elision, so there is "
                             "nothing to compare")
    # The exit codes the result states outside its quotes, each quote read as
    # a gap between words so the words either side cannot join into one.
    stated = []
    for m in EXIT_RE.finditer(QUOTED_RE.sub(" ", result)):
        if int(m.group(1)) not in stated:
            stated.append(int(m.group(1)))
    if any(ch in cmd for ch in NOT_SIMPLE):
        return "unchecked", ("not a simple command: it needs a shell, a glob "
                             "or an elision to mean what it says")
    try:
        argv = shlex.split(cmd)
    except ValueError as e:
        return "unchecked", f"does not split into words: {e}"
    if not argv:
        return "unchecked", "an empty command"
    for a in argv:
        if a.startswith("#"):
            return "unchecked", (f"a shell would read {a!r} as the start of "
                                 f"a comment")
    if any(a.startswith("/") or any(v.startswith("/") for v in a.split("=")[1:])
           or ".." in re.split(r"[/=:]", a) or a.startswith("--output")
           for a in argv[1:]):
        return "unchecked", ("names a path outside the tree, or asks to "
                             "write a file")
    if git(repo, "rev-parse", "--verify", "--quiet",
           f"{sha}^{{commit}}").returncode != 0:
        return "unchecked", f"commit {sha} is not in {side}'s clone"
    if argv[0] == "git":
        if len(argv) < 2 or argv[1] not in GIT_READ:
            return "unchecked", (f"git {argv[1] if len(argv) > 1 else ''} is "
                                 f"not one of the read-only queries "
                                 f"{sorted(GIT_READ)}")
        why = git_moves(repo, argv[2:])
        if why:
            return "unchecked", why
    elif argv[0] not in PLAIN:
        prog = argv[1] if argv[0] in INTERPRETERS and len(argv) > 1 else argv[0]
        shown = git(repo, "show", f"{sha}:{prog}")
        if shown.returncode != 0:
            return "unchecked", (f"{prog} is not a file of {side}'s tree at "
                                 f"{sha}, so it is not one of the author's "
                                 f"committed tools")
        if not any(MARK_LINE_RE.match(ln)
                   for ln in shown.stdout.splitlines()[:40]):
            return "unchecked", (f"{prog} does not declare '{RERUN_MARK}' in "
                                 f"its first 40 lines, so its output may "
                                 f"depend on more than the commit")
    if len(stated) > 1:
        return "mismatch", (f"its result states {len(stated)} different exit "
                            f"codes, {', '.join(map(str, stated))}, and no "
                            f"run can satisfy them all")
    work = pathlib.Path(tempfile.mkdtemp(prefix="lsl-rerun-"))
    try:
        if git(repo, "worktree", "add", "--detach", "--quiet", str(work),
               sha).returncode != 0:
            return "unchecked", f"could not check {sha} out"
        for path, data in (evidence_files or {}).items():
            target = work / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        # No standard input, so a command that reads it cannot wait on ours;
        # its own session, so a timeout kills everything it started and no
        # child is left holding its pipes; bytes decoded with replacement, so
        # output that is not UTF-8 is compared rather than raised out of the
        # checker as a refusal (round 28 lap 6 S27, S28).
        # git's abbreviation pinned to seven characters (Platterpus round 29
        # lap 4 S9): git otherwise sizes it by the clone's object count, so a
        # larger clone prints a longer hash and a correct quote of a hash
        # followed by text is not found. Appended after any GIT_CONFIG_*
        # entries already set, so it is the value git reads; git still
        # lengthens a prefix that would be ambiguous.
        env = dict(os.environ)
        n = int(env.get("GIT_CONFIG_COUNT", "0") or "0")
        env[f"GIT_CONFIG_KEY_{n}"] = "core.abbrev"
        env[f"GIT_CONFIG_VALUE_{n}"] = "7"
        env["GIT_CONFIG_COUNT"] = str(n + 1)
        try:
            proc = subprocess.Popen(argv, cwd=work, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    start_new_session=True, env=env)
        except OSError as e:
            return "unchecked", f"did not start: {e}"
        try:
            so, se = proc.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
            proc.communicate()
            return "unchecked", "did not finish within 120 s, and was killed"
        out = (so + se).decode("utf-8", errors="replace")
        status = proc.returncode
    finally:
        git(repo, "worktree", "remove", "--force", str(work))
        shutil.rmtree(work, ignore_errors=True)
        git(repo, "worktree", "prune")
    # The exit status is read (S27, second of four): a result that states
    # `exit N` is held to it, and one that states none is not matched by a
    # command that failed, whatever its error text happens to contain.
    if stated and status != stated[0]:
        return "mismatch", (f"it exited {status}, and its result says "
                            f"exit {stated[0]}")
    if not stated and status != 0:
        return "unchecked", (f"it exited {status}, and its result does not "
                             f"say it expected a non-zero exit")
    for q in quoted:
        pos = 0
        parts = q.split("…")
        for i, frag in enumerate(parts):
            # Only the spaces beside an elision come off: a quote with none is
            # compared with its spaces (round 29 lap 1 S29).
            if i > 0:
                frag = frag.lstrip()
            if i < len(parts) - 1:
                frag = frag.rstrip()
            if not frag:
                continue
            at = out.find(frag, pos)
            if at < 0:
                return "mismatch", (f"its output does not contain the quoted "
                                    f"result \"{q}\"")
            pos = at + len(frag)
    return "ok", ""


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

    v2 = lap.version is not None and lap.version >= 2
    v3 = lap.version is not None and lap.version >= 3
    kinds = dict(KINDS, **KINDS2) if v2 else KINDS
    fields = FIELDS | set(FIELDS2) if v2 else FIELDS
    if v3:
        fields = fields | set(FIELDS3)
    rerun_counts = {"seen": 0, "ok": 0, "mismatch": 0, "unchecked": 0}
    for s in stmts:
        n, kind, grade = s["line"], s["kind"], s["grade"]
        tag = f"S{s['n']} {kind}" + (f" {grade}" if grade else "")
        if kind not in kinds:
            lap.refuse(n, "LSL.1", f"{tag}: {kind} is not a kind")
            continue
        if kinds[kind] and grade not in kinds[kind]:
            lap.refuse(n, "LSL.1", f"{tag}: a {kind} takes one grade of "
                                   f"{sorted(kinds[kind])}")
            continue
        if not kinds[kind] and grade:
            lap.refuse(n, "LSL.1", f"{tag}: a {kind} takes no grade")
            continue
        have = {}
        for name, value, fl in s["fields"]:
            if name not in fields:
                lap.refuse(fl, "LSL.field", f"{tag}: {name}: is not a field")
                continue
            have.setdefault(name, []).append((value, fl))
        for req in REQUIRED.get((kind, grade), []):
            if req not in have:
                lap.refuse(n, "LSL.2", f"{tag}: needs a {req}: field")
        if v2:
            for req, rule in REQUIRED2.get((kind, grade), []):
                if req not in have:
                    lap.refuse(n, rule, f"{tag}: needs a {req}: field")
            check_v2(lap, s, tag, have, me, by_n, resolver)

        at_sha = b1_at(lap, tag, have, me_side, resolver) if v3 else None

        # Every field value has a shape; check each one that has one. Artifact
        # citations first, so a run: re-run below can place the evidence
        # files this statement cites at their own paths (HR-2 6d).
        evs = have.get("evidence", [])
        evs = ([e for e in evs if not e[0].startswith("run: ")]
               + [e for e in evs if e[0].startswith("run: ")])
        for value, fl in evs:
            first = value.split()[0]
            if value.startswith("run: "):
                if " => " not in value:
                    lap.refuse(fl, "LSL.value",
                               f"{tag}: a run: names its command AND its "
                               f"result, as 'run: CMD => RESULT'")
                elif v3:
                    b1_run(lap, fl, tag, value, have, at_sha, me_side,
                           resolver, rerun_counts)
                continue
            ref = art_ref(first)
            if ref is None:
                lap.refuse(fl, "LSL.value",
                           f"{tag}: evidence {first!r} is neither "
                           f"'run: CMD => RESULT' nor side@commit:path"
                           f"[:line[-line]]")
                continue
            resolver.artifact(lap, fl, *ref, rest=value[len(first):])
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
                resolver.artifact(lap, fl, *ref, rest=value[len(first):])
            else:
                lap.refuse(fl, "LSL.4", f"{tag}: re: {first!r} is neither a "
                                        f"statement nor an artifact reference")
        for value, fl in have.get("because", []):
            for token in re.split(r"[,\s]+", value.strip()):
                if token and not check_stmt_ref(lap, fl, token, me, local_ids):
                    lap.refuse(fl, "LSL.4", f"{tag}: because: {token!r} is not "
                                            f"a statement reference")
                elif token and v2:
                    unweighted(lap, fl, tag, "because", token, me)
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
            if kind == "FINDING":
                continue    # A3's targets, checked in check_v2()
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
                    elif v2:
                        unweighted(lap, fl, tag, "basis", token, me)
            if v2 and said == "GO":
                waits(lap, n, tag, me, resolver)
        if v2 and kind == "VERDICT":
            pre_committed(lap, s, n, tag, me)

    if v3:
        c = rerun_counts
        total = c["seen"]
        if getattr(resolver, "rerun", False):
            lap.notes.append(f"B1: {total} run: result(s) in this lap; "
                             f"{c['ok']} re-run and matched, {c['mismatch']} "
                             f"re-run and not matched, {c['unchecked']} not "
                             f"re-runnable (each named above)")
        else:
            lap.notes.append(f"B1: {total} run: result(s) in this lap, none "
                             f"re-run: --rerun was not given")


def main():
    global LAPS
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
    ap.add_argument("--laps", type=pathlib.Path, default=LAPS,
                    help="where held laps are read from: ours in DIR, theirs "
                         "in DIR/inbound (default: docs/handshake)")
    ap.add_argument("--rerun", action="store_true",
                    help="LSL 3, B1: re-run each run: whose command can "
                         "depend only on the commit it names, at that "
                         "commit, and refuse the lap when a quoted result is "
                         "not in its output. It EXECUTES the author's "
                         "committed tools: run it where that is acceptable")
    args = ap.parse_args()
    LAPS = args.laps

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
                  f"-- no 'LSL: N' line for N in {', '.join(map(str, LSL_VERSIONS))}")
        return 2
    resolver = Resolver(args.ours, args.peer, refs)
    resolver.rerun = args.rerun
    check(lap, resolver)

    for line, rule, msg in sorted(lap.refusals):
        print(f"REFUSED  {args.lap.name}:{line}  [{rule}] {msg}")
    for line, rule, msg in sorted(lap.warnings):
        print(f"WARN     {args.lap.name}:{line}  [{rule}] {msg}")
    kinds = {}
    for s in lap.statements:
        kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
    census = ", ".join(f"{v} {k}" for k, v in sorted(kinds.items()))
    print(f"\n{len(lap.statements)} statement(s), LSL {lap.version}: "
          f"{census or 'none'}")
    for note in lap.notes:
        print(note)
    if lap.refusals:
        print(f"{len(lap.refusals)} refusal(s) -- not a well-formed LSL lap")
        return 1
    print(f"well formed, {len(lap.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
