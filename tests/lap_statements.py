#!/usr/bin/env python3
"""tools/lap-statements.py must refuse every malformed statement it claims to.

The checker is the whole of LSL's value: a statement language nothing enforces
is prose with a stricter look. So each refusal in the spec's list gets a lap
built to trigger exactly it, and each assertion names the MESSAGE as well as
the exit code -- a lap refused for some other reason would otherwise pass a
test written for this one. The well-formed lap is checked too, and so is every
committed lap that declares `LSL: 1`, so a lap of ours cannot be sent
malformed.

References resolve against this repository's real history (`ee0221c`, and the
laps we hold), because a checker tested only against fixtures it invented can
agree with itself. Temporary files are removed when the test ends.
"""

import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "lap-statements.py"

failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


HEAD = """HANDSHAKE-PROTOCOL: 5
HANDSHAKE-ROUND: 27
HANDSHAKE-LAP: 9
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-VERDICT: {verdict}

# a title

LSL: 1

"""

# Every kind, well formed, with references that resolve in our tree.
GOOD = """S1 FACT read: The banner is written as soon as the log opens.
  evidence: cyanrip@ee0221c:src/cyanrip_log.c:1-20
S2 FACT measured: The pooled sweep reports no violations.
  evidence: run: python3 tools/blackbox.py --gate => no invariant violations
S3 FACT reproduced: Their lap 2 section B answers our lap 1.
  re: platterpus:R27.L2.§B
  evidence: cyanrip@ee0221c:docs/handshake/inbound/round-27-lap-02.md:111
S4 NONE: No round-27 lap of theirs is newer than lap 3 in our tree.
  scope: docs/handshake/inbound/round-27-lap-*.md at ee0221c
  evidence: run: git ls-tree ee0221c docs/handshake/inbound/ => laps 2 and 3
S5 UNKNOWN: Whether the drive caches reads beyond 140 sectors.
  reason: our probe's figure is known to be wrong
S6 DID: The early-log banner fix.
  commit: ee0221c
S7 WILL: Cut the next release.
  owner: us
  when: once this round is closed on both gates
S8 ACCEPT: Their wording for the summary line.
  re: platterpus:R27.L2.§D
S9 AMEND: The per-track line.
  re: cyanrip:R27.L9.S8
  to: a shorter tail
S10 ASK: Does your gate read round 27 closed?
  target: NEXT-ROUND
S11 NOTE: Anything a human needs that is not a claim.
S12 VERDICT: {verdict}
  basis: S1, S2, S6
"""


def run(body, *extra, verdict="GO", head=None):
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "lap.md"
        p.write_text((head or HEAD).format(verdict=verdict)
                     + body.replace("{verdict}", verdict))
        r = subprocess.run([sys.executable, str(TOOL), str(p), *extra],
                           capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout + r.stderr


def expect(name, body, code, needle, **kw):
    got, out = run(body, **kw)
    if got != code:
        fail(f"{name}: exit {got}, expected {code}\n{out}")
    elif needle and needle not in out:
        fail(f"{name}: exit {code} as expected, but not for the reason "
             f"tested -- {needle!r} is not in:\n{out}")
    else:
        print(f"ok   {name}")


def swap(old, new):
    assert GOOD.count(old) == 1, old
    return GOOD.replace(old, new)


# 0. The well-formed lap, and it is well formed for a reason: it carries a
#    peer reference, so without --peer it must warn rather than pass silently.
got, out = run(GOOD)
if got != 0 or "well formed" not in out:
    fail(f"the well-formed lap: exit {got}\n{out}")
else:
    print("ok   the well-formed lap")

# 1. kind and grade
expect("unknown kind", swap("S11 NOTE:", "S11 MAYBE:"), 1, "MAYBE is not a kind")
expect("FACT with no grade", swap("S1 FACT read:", "S1 FACT:"), 1,
       "a FACT takes one grade")
expect("FACT with a made-up grade", swap("S1 FACT read:", "S1 FACT likely:"),
       1, "a FACT takes one grade")
expect("a grade on a kind that takes none", swap("S6 DID:", "S6 DID read:"), 1,
       "a DID takes no grade")

# 2. required fields
expect("FACT read with no evidence",
       swap("  evidence: cyanrip@ee0221c:src/cyanrip_log.c:1-20\n", ""), 1,
       "S1 FACT read: needs a evidence: field")
expect("NONE with no scope",
       swap("  scope: docs/handshake/inbound/round-27-lap-*.md at ee0221c\n",
            ""), 1, "S4 NONE: needs a scope: field")
expect("UNKNOWN with no reason",
       swap("  reason: our probe's figure is known to be wrong\n", ""), 1,
       "S5 UNKNOWN: needs a reason: field")
expect("an unknown field", swap("  to: a shorter tail", "  gist: a shorter tail"),
       1, "gist: is not a field")

# 3. numbering
expect("a gap", swap("S5 UNKNOWN:", "S15 UNKNOWN:"), 1,
       "S15 where S5 was expected")
expect("a repeat", swap("S5 UNKNOWN:", "S4 UNKNOWN:"), 1, "S4 is numbered twice")

# 4. references
expect("a branch name is not a reference",
       swap("cyanrip@ee0221c:src/cyanrip_log.c:1-20",
            "cyanrip@platterpus-fork:src/cyanrip_log.c"), 1,
       "is neither 'run: CMD => RESULT' nor side@commit:path")
# A commit absent from THIS clone is refused only if the clone is complete.
# Cloud sessions hold a shallow clone, where the honest answer is "could not
# tell" (F3); the refusal arm is pinned on a full clone in section 8.
SHALLOW = subprocess.run(["git", "-C", str(ROOT), "rev-parse",
                          "--is-shallow-repository"], capture_output=True,
                         text=True).stdout.strip() == "true"
ABSENT = ((0, "[LSL.unchecked]") if SHALLOW else (1, "[LSL.4]"))
expect("a commit that does not exist" + (" (shallow clone)" if SHALLOW else ""),
       swap("cyanrip@ee0221c:src/cyanrip_log.c:1-20",
            "cyanrip@0000000:src/cyanrip_log.c"), ABSENT[0],
       ABSENT[1] + (" UNCHECKED cyanrip@0000000" if SHALLOW
                    else " commit 0000000 does not resolve"))
expect("a path that does not exist at the commit",
       swap("cyanrip@ee0221c:src/cyanrip_log.c:1-20",
            "cyanrip@ee0221c:src/no_such_file.c"), 1,
       "src/no_such_file.c does not exist at cyanrip@ee0221c")
expect("a line past the end of the file",
       swap("cyanrip@ee0221c:src/cyanrip_log.c:1-20",
            "cyanrip@ee0221c:src/cyanrip_log.c:99999"), 1,
       "line 99999 does not exist")
expect("a run: with no result",
       swap(" => no invariant violations", ""), 1,
       "names its command AND its result")
expect("a lap we do not hold",
       swap("re: platterpus:R27.L2.§D", "re: platterpus:R27.L7.§D"), 1,
       "we do not hold platterpus's round 27 lap 7")
expect("a statement number in a prose lap",
       swap("re: platterpus:R27.L2.§D", "re: platterpus:R27.L2.S4"), 1,
       "is a prose lap and has no statement numbers")
expect("a statement of this lap that does not exist",
       swap("re: cyanrip:R27.L9.S8", "re: cyanrip:R27.L9.S80"), 1,
       "no such statement in this lap")
expect("a DID naming a commit that does not exist"
       + (" (shallow clone)" if SHALLOW else ""),
       swap("  commit: ee0221c", "  commit: 1234567"), ABSENT[0],
       ABSENT[1] + (" UNCHECKED cyanrip@1234567" if SHALLOW
                    else " commit 1234567 does not resolve in cyanrip's tree"))
got, out = run(GOOD)
if "UNCHECKED" in out or "platterpus@" in GOOD:
    fail("fixture drift: GOOD should carry no platterpus@ artifact")
got, out = run(swap("  evidence: cyanrip@ee0221c:docs/handshake/inbound/round-27-lap-02.md:111",
                    "  evidence: platterpus@183073b:docs/handshake/outbound/round-27-lap-02.md:1"))
if got != 0 or "UNCHECKED platterpus@183073b" not in out:
    fail(f"a peer artifact with no --peer must be UNCHECKED, not passed "
         f"or refused: exit {got}\n{out}")
else:
    print("ok   a peer artifact with no --peer is UNCHECKED")

# 5. the verdict
expect("no VERDICT", swap("S12 VERDICT: {verdict}\n  basis: S1, S2, S6\n", ""),
       1, "0 VERDICT statements")
expect("two VERDICTs", GOOD + "S13 VERDICT: GO\n  basis: S1\n", 1,
       "2 VERDICT statements")
got, out = run(GOOD.replace("S12 VERDICT: {verdict}", "S12 VERDICT: HOLD"))
if got != 1 or "says HOLD and HANDSHAKE-VERDICT says ['GO']" not in out:
    fail(f"a VERDICT disagreeing with the header: exit {got}\n{out}")
else:
    print("ok   a VERDICT disagreeing with the header")
expect("a verdict that is not a verdict",
       GOOD.replace("S12 VERDICT: {verdict}", "S12 VERDICT: YES"), 1,
       "the verdict is GO, HOLD or OPEN")
expect("basis naming a NOTE", swap("  basis: S1, S2, S6", "  basis: S1, S11"),
       1, "basis: S11 is a NOTE")
expect("basis naming an ASK", swap("  basis: S1, S2, S6", "  basis: S10"),
       1, "basis: S10 is a ASK")
expect("basis naming nothing", swap("  basis: S1, S2, S6", "  basis: S1, S40"),
       1, "basis: S40 does not exist")

# 6. questions and commitments
expect("a BLOCKING question with no breaks",
       swap("  target: NEXT-ROUND", "  target: BLOCKING"), 1,
       "names what it breaks in the pin")
expect("a target that is neither", swap("  target: NEXT-ROUND", "  target: SOON"),
       1, "target: is BLOCKING or NEXT-ROUND")
expect("a WILL with a date",
       swap("  when: once this round is closed on both gates",
            "  when: by 2026-10-01"), 1, "when: is a condition, never a date")
expect("a WILL with an unknown owner", swap("  owner: us", "  owner: someone"),
       1, "owner: is us, them or operator")

# 7. relays warn, prose is refused, and a prose lap cannot be checked at all
got, out = run(GOOD + "S13 FACT relayed: The operator said it is released.\n"
                      "  source: a chat message\n")
if got != 0 or "a relay is in neither repository" not in out:
    fail(f"a relay must warn and not refuse: exit {got}\n{out}")
else:
    print("ok   a relay warns")
expect("a line of prose between statements",
       swap("S11 NOTE:", "Some prose that is not a statement.\n\nS11 NOTE:"), 1,
       "not a statement, a field, a continuation or a heading")
expect("a field after a blank line",
       swap("  owner: us\n", "\n  owner: us\n"), 1,
       "not a statement, a field, a continuation or a heading")
got, out = run("", head=HEAD.replace("LSL: 1\n", ""))
if got != 2 or "not an LSL lap" not in out:
    fail(f"a prose lap must be CANNOT CHECK, exit 2: exit {got}\n{out}")
else:
    print("ok   a prose lap cannot be checked")
got, out = run(GOOD, head=HEAD.replace("LSL: 1", "LSL: 2"))
if got != 2 or "implements LSL 1 only" not in out:
    fail(f"an unimplemented LSL version must exit 2: exit {got}\n{out}")
else:
    print("ok   an unimplemented LSL version cannot be checked")

# 8. Platterpus's LSL amendments 1, F1, F3 and F4, each on a tree built for it.
#    The real history cannot supply a shallow clone, a commit on a side branch
#    only, or a commit on no branch on demand, so small repositories do.
GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
               GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")


def g(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       text=True, env=GIT_ENV)
    assert r.returncode == 0, (args, r.stderr)
    return r.stdout.strip()


def make_repo(path, branch, n):
    """A repository on `branch` with n commits of README; their SHAs, oldest first."""
    path.mkdir()
    g(path, "init", "-q", "-b", branch)
    shas = []
    for i in range(n):
        (path / "README").write_text("".join(f"line {j}\n" for j in range(i + 3)))
        g(path, "add", "README")
        g(path, "commit", "-q", "-m", f"c{i}")
        shas.append(g(path, "rev-parse", "HEAD"))
    return shas


def check_lap(text, *extra):
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "lap.md"
        p.write_text(text)
        r = subprocess.run([sys.executable, str(TOOL), str(p), *extra],
                           capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout + r.stderr


def lap_from(author, verdict, body):
    return (f"HANDSHAKE-PROTOCOL: 5\nHANDSHAKE-ROUND: 27\nHANDSHAKE-LAP: 9\n"
            f"HANDSHAKE-FROM: {author}\nHANDSHAKE-VERDICT: {verdict}\n\n"
            f"LSL: 1\n\n{body}")


def outcome(name, got, want_code, needles, absent=()):
    code, out = got
    missing = [n for n in needles if n not in out]
    present = [n for n in absent if n in out]
    if code != want_code or missing or present:
        fail(f"{name}: exit {code} (want {want_code}); missing {missing}; "
             f"unwanted {present}\n{out}")
    else:
        print(f"ok   {name}")


with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    peer = make_repo(tmp / "peer", "main", 2)

    # F1: in a lap Platterpus wrote, "we" is Platterpus. Their DID names their
    # commit and their measurement cites their tree, and both are theirs to cite.
    theirs = lap_from("platterpus", "OPEN",
                      f"S1 DID: Fixed a thing.\n  commit: {peer[1][:7]}\n\n"
                      f"S2 FACT measured: The README has four lines.\n"
                      f"  evidence: platterpus@{peer[1][:7]}:README:4\n\n"
                      f"S3 VERDICT: OPEN\n  basis: S2\n")
    outcome("F1: a Platterpus lap citing its own tree, with that tree",
            check_lap(theirs, "--peer", str(tmp / "peer")), 0,
            ["well formed, 0 warning(s)"])
    outcome("F1: the same lap without their tree is unchecked, not refused",
            check_lap(theirs), 0,
            ["[LSL.unchecked] UNCHECKED platterpus@", "well formed, 2 warning(s)"],
            absent=["REFUSED"])
    ours_claim = lap_from("cyanrip-fork", "OPEN",
                          f"S1 FACT measured: Their README has four lines.\n"
                          f"  evidence: platterpus@{peer[1][:7]}:README:4\n\n"
                          f"S2 VERDICT: OPEN\n  basis: S1\n")
    outcome("F1: a measurement of OURS citing only their tree is refused",
            check_lap(ours_claim, "--peer", str(tmp / "peer")), 1,
            ["[LSL.2] S1 FACT measured: measured by the lap's author (cyanrip)"])
    outcome("F1: a lap naming neither side has no 'us'",
            check_lap(lap_from("somebody", "OPEN", "S1 NOTE: x.\n\n"
                               "S2 VERDICT: OPEN\n  basis: S1\n")), 1,
            ["[LSL.header] HANDSHAKE-FROM is 'somebody'"])

    # F4: judged against the ref of record; a side branch warns; no branch refuses.
    ours = make_repo(tmp / "ours", "platterpus-fork", 2)
    g(tmp / "ours", "checkout", "-q", "-b", "claude/side")
    (tmp / "ours" / "README").write_text("side\n")
    g(tmp / "ours", "commit", "-q", "-am", "side")
    side = g(tmp / "ours", "rev-parse", "HEAD")
    g(tmp / "ours", "checkout", "-q", "platterpus-fork")
    tree = g(tmp / "ours", "rev-parse", "HEAD^{tree}")
    dangling = g(tmp / "ours", "commit-tree", tree, "-m", "dangling")

    def did(sha):
        return lap_from("cyanrip-fork", "OPEN",
                        f"S1 DID: A thing.\n  commit: {sha[:7]}\n\n"
                        f"S2 VERDICT: OPEN\n  basis: S1\n")
    # basis: S1 names a DID, which carries a claim; that is LSL 1's rule.
    outcome("F4: a commit on the ref of record is fine",
            check_lap(did(ours[0]), "--ours", str(tmp / "ours")), 0,
            ["well formed, 0 warning(s)"])
    outcome("F4: a commit on a side branch only is a warning, LSL.offrecord",
            check_lap(did(side), "--ours", str(tmp / "ours")), 0,
            ["[LSL.offrecord]", "only on claude/side"], absent=["REFUSED"])
    outcome("F4: a commit on no branch is refused",
            check_lap(did(dangling), "--ours", str(tmp / "ours")), 1,
            ["[LSL.4]", "on no branch"])
    outcome("F4: --ref moves the ref of record, and the side commit is then fine",
            check_lap(did(side), "--ours", str(tmp / "ours"),
                      "--ref", "cyanrip=claude/side"), 0,
            ["well formed, 0 warning(s)"])

    # F3: a shallow clone cannot tell a missing commit from one it never fetched.
    g(tmp, "clone", "-q", "--depth", "1", "--branch", "platterpus-fork",
      f"file://{tmp / 'ours'}", "shallow")
    outcome("F3: an old commit in a shallow clone is unchecked, not refused",
            check_lap(did(ours[0]), "--ours", str(tmp / "shallow")), 0,
            ["[LSL.unchecked]", "shallow"], absent=["REFUSED"])
    outcome("F3: the same commit in the full clone is fine",
            check_lap(did(ours[0]), "--ours", str(tmp / "ours")), 0,
            ["well formed, 0 warning(s)"])
    outcome("F3: a commit that is truly absent from a full clone is still refused",
            check_lap(did("1234567"), "--ours", str(tmp / "ours")), 1,
            ["[LSL.4] commit 1234567 does not resolve in cyanrip's tree"])

    # F4, as it bit the first fix: a fetch moves origin/<ref> and not a stale
    # local <ref>, so a commit only the fetch brought in is still on the
    # record. And origin/HEAD is an alias, never a branch to list.
    g(tmp, "clone", "-q", "--branch", "platterpus-fork",
      f"file://{tmp / 'ours'}", "stale")
    (tmp / "ours" / "README").write_text("newer\n")
    g(tmp / "ours", "commit", "-q", "-am", "newer")
    newer = g(tmp / "ours", "rev-parse", "HEAD")
    g(tmp / "stale", "fetch", "-q", "origin")
    outcome("F4: a commit only a fetch brought in is on the record",
            check_lap(did(newer), "--ours", str(tmp / "stale")), 0,
            ["well formed, 0 warning(s)"])
    # origin/HEAD pointing at the side branch is what puts the alias beside
    # it in the listing; pointing at the record, it could never appear.
    g(tmp / "stale", "remote", "set-head", "origin", "claude/side")
    outcome("F4: a remote side branch is named, and origin/HEAD is not",
            check_lap(did(side), "--ours", str(tmp / "stale")), 0,
            ["[LSL.offrecord]", "only on origin/claude/side:"],
            absent=["only on origin,", "only on origin:"])

# 9. The rule ids: the code, the table in RULES and the spec's table name the
#    same set, so a disagreement between the two checkers can name its rule.
src = TOOL.read_text()
body_src = src.split("class Lap")[1]
emitted = {a or b for a, b in re.findall(
    r'"(LSL\.[a-z0-9]+)"|\[(LSL\.[a-z0-9]+)\]', body_src)}
table = set(re.findall(r'^    "(LSL\.[a-z0-9]+)":', src, re.M))
spec_text = (ROOT / "docs" / "handshake" /
             "PROPOSAL-lap-statement-language.md").read_text()
spec = set(re.findall(r"^\| `(LSL\.[a-z0-9]+)` \|", spec_text, re.M))
if not (emitted == table == spec):
    fail(f"rule ids disagree: emitted-not-in-RULES {sorted(emitted - table)}, "
         f"RULES-not-emitted {sorted(table - emitted)}, "
         f"RULES-not-in-spec {sorted(table - spec)}, "
         f"spec-not-in-RULES {sorted(spec - table)}")
else:
    print(f"ok   {len(table)} rule ids, the same in the code, RULES and the spec")

# 10. every committed LSL lap of ours is well formed
laps = [p for p in sorted((ROOT / "docs" / "handshake").glob("round-*.md"))
        if re.search(r"^LSL: 1\s*$", p.read_text(encoding="utf-8"), re.M)]
for p in laps:
    r = subprocess.run([sys.executable, str(TOOL), str(p)],
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        fail(f"{p.name} is not a well-formed LSL lap:\n{r.stdout}")
    else:
        print(f"ok   {p.name} is well formed")
print(f"({len(laps)} committed LSL lap(s))")

if failures:
    print(f"\n{failures} failure(s)")
    sys.exit(1)
print("\nall checks passed")
