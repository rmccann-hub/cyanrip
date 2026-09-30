#!/usr/bin/env python3
"""tools/lap-statements.py must refuse every malformed statement it claims to.

The checker is the whole of LSL's value: a statement language nothing enforces
is prose with a stricter look. So each refusal in the spec's list gets a lap
built to trigger exactly it, and each assertion names the MESSAGE as well as
the exit code -- a lap refused for some other reason would otherwise pass a
test written for this one. The well-formed lap is checked too, and so is every
committed lap that declares `LSL: 1` or `LSL: 2`, so a lap of ours cannot be
sent malformed. LSL 2's amendments, A1-A8, are section 11, and section 12 reads
Platterpus's own worked example of them.

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
got, out = run(GOOD, head=HEAD.replace("LSL: 1", "LSL: 5"))
if got != 2 or "implements LSL 1, 2, 3 and 4 only" not in out:
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


def check_lap(text, *extra, stdin_text=None, env=None):
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "lap.md"
        p.write_text(text)
        r = subprocess.run([sys.executable, str(TOOL), str(p), *extra],
                           capture_output=True, text=True, cwd=ROOT,
                           input=stdin_text, env=env)
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
    # Our round 30 lap 1 S20, accepting Platterpus's round 29 lap 4 S33: a
    # file's final line counts whether or not it ends in a newline. Counting
    # newline characters alone made the last line of such a file uncitable.
    nl = tmp / "nl"
    nl.mkdir()
    g(nl, "init", "-q", "-b", "main")
    (nl / "END").write_text("first\nsecond")
    g(nl, "add", "END")
    g(nl, "commit", "-q", "-m", "no final newline")
    nl_sha = g(nl, "rev-parse", "HEAD")[:7]
    last = lap_from("platterpus", "OPEN",
                    f"S1 FACT read: The file's second line has no newline.\n"
                    f"  evidence: platterpus@{nl_sha}:END:2\n\n"
                    f"S2 VERDICT: OPEN\n  basis: S1\n")
    outcome("S20: an unterminated final line can be cited",
            check_lap(last, "--peer", str(nl)), 0,
            ["well formed, 0 warning(s)"])
    outcome("S20: the line after it still cannot",
            check_lap(last.replace(":END:2", ":END:3"), "--peer", str(nl)), 1,
            ["has 2 lines; line 3 does not exist"])

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
#    LSL 2's are A1-A8, Platterpus's ids; the ones REQUIRED2 carries are
#    emitted through it, so they count as emitted there.
ID = r"LSL\.[a-z0-9]+|A[1-8]|B[1-3]"
src = TOOL.read_text()
body_src = src.split("class Lap")[1]
emitted = {a or b for a, b in re.findall(
    rf'"({ID})"|\[({ID})\]', body_src)}
emitted |= set(re.findall(r'\("[a-z]+", "(A[1-8])"\)', src))
table = set(re.findall(rf'^    "({ID})":', src, re.M))
spec_text = (ROOT / "docs" / "handshake" /
             "PROPOSAL-lap-statement-language.md").read_text()
spec = set(re.findall(rf"^\| `({ID})` \|", spec_text, re.M))
if not (emitted == table == spec):
    fail(f"rule ids disagree: emitted-not-in-RULES {sorted(emitted - table)}, "
         f"RULES-not-emitted {sorted(table - emitted)}, "
         f"RULES-not-in-spec {sorted(table - spec)}, "
         f"spec-not-in-RULES {sorted(spec - table)}")
else:
    print(f"ok   {len(table)} rule ids, the same in the code, RULES and the spec")

# 10. every committed LSL lap of ours is well formed
laps = [p for p in sorted((ROOT / "docs" / "handshake").glob("round-*.md"))
        if re.search(r"^LSL: [123]\s*$", p.read_text(encoding="utf-8"), re.M)]
for p in laps:
    r = subprocess.run([sys.executable, str(TOOL), str(p)],
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        fail(f"{p.name} is not a well-formed LSL lap:\n{r.stdout}")
    else:
        print(f"ok   {p.name} is well formed")
print(f"({len(laps)} committed LSL lap(s))")

# 11. LSL 2: A1-A8, each refusal on a lap built to trigger it and nothing
#     else, and each rule that reads other laps on a round built for it in a
#     directory of its own (--laps), so the real record cannot move a result.

def lap2(author, rnd, lp, verdict, body):
    return (f"HANDSHAKE-PROTOCOL: 5\nHANDSHAKE-ROUND: {rnd}\n"
            f"HANDSHAKE-LAP: {lp}\nHANDSHAKE-FROM: {author}\n"
            f"HANDSHAKE-VERDICT: {verdict}\n\nLSL: 2\n\n{body}")


GOOD2 = """S1 FACT read: The banner is written as soon as the log opens.
  evidence: cyanrip@ee0221c:src/cyanrip_log.c:1-20
  holds: cyanrip@ee0221c
S2 FACT measured: The suite passes.
  evidence: run: meson test -C build => Ok: 91
  holds: 0.9.4-rc2+platterpus.17
  examined: 91 tests, closed
S3 NONE: No test reads the network.
  scope: tests/*.py
  evidence: run: grep -l urlopen tests/*.py => nothing
  examined: 3 files, open
  missing: the files added since
S4 TERM set: The suite passes on the pin.
  requires: 91 of 91
S5 TERM met: It did.
  term: S4
  evidence: run: meson test -C build => Ok: 91
S6 TERM set: Their release names the pin.
  requires: their FORK_PIN at the pin
S7 TERM pending: Ours is done, and theirs remains.
  term: S6
  on: them
  remains: their release
S8 FINDING ours: A clean result was printed over nothing.
  in: cyanrip@ee0221c:src/cyanrip_log.c
  shape: a success message that does not name its population
  target: FIXED
  landed: cyanrip@ee0221c:src/cyanrip_log.c:1
  evidence: run: python3 tests/ingest_bundle.py => all ingest-bundle checks passed
  portable: yes
S9 CORRECT: S1 said the wrong thing.
  re: S1
  was: late
  now: early
  evidence: cyanrip@ee0221c:src/cyanrip_log.c:1-20
S10 WILL: Our next lap is GO.
  owner: us
  when: once the run is filed
  verdict: GO
  unless: the run fails
S11 UNKNOWN: Whether the drive caches.
  reason: our probe is wrong
S12 FACT relayed: The operator said so.
  source: a chat message
S13 VERDICT: {verdict}
  basis: S1, S5
"""


def check2(text, laps, *extra, stdin_text=None, env=None):
    return check_lap(text, "--laps", str(laps), *extra, stdin_text=stdin_text,
                     env=env)


def swap2(old, new):
    assert GOOD2.count(old) == 1, old
    return GOOD2.replace(old, new)


with tempfile.TemporaryDirectory() as tmp:
    empty = pathlib.Path(tmp) / "empty"
    (empty / "inbound").mkdir(parents=True)

    def expect2(name, body, code, needles, absent=(), verdict="GO", lp=1):
        outcome(name, check2(lap2("cyanrip-fork", 30, lp, verdict,
                                  body.replace("{verdict}", verdict)), empty),
                code, needles, absent)

    expect2("LSL 2: every new kind and field, well formed", GOOD2, 0,
            ["LSL 2:", "well formed", "checked against 2 close condition(s)"],
            absent=["REFUSED"])
    outcome("LSL 1 still refuses LSL 2's kinds and fields",
            check2(lap2("cyanrip-fork", 30, 1, "GO", GOOD2.replace(
                "{verdict}", "GO")).replace("LSL: 2", "LSL: 1"), empty), 1,
            ["[LSL.1] S4 TERM set: TERM is not a kind",
             "[LSL.1] S8 FINDING ours: FINDING is not a kind",
             "[LSL.field] S1 FACT read: holds: is not a field"],
            absent=["[A1]", "[A4]"])

    # A4
    expect2("A4: a FACT with no holds:",
            swap2("  holds: cyanrip@ee0221c\n", ""), 1,
            ["[A4] S1 FACT read: needs a holds: field"])
    expect2("A4: holds: naming neither a commit nor a version",
            swap2("  holds: cyanrip@ee0221c", "  holds: the current build"), 1,
            ["[A4] S1 FACT read: holds: names a commit or a version"])
    # A5
    expect2("A5: a measurement with no examined:",
            swap2("  examined: 91 tests, closed\n", ""), 1,
            ["[A5] S2 FACT measured: needs a examined: field"])
    expect2("A5: a measurement over nothing",
            swap2("  examined: 91 tests, closed", "  examined: 0 tests, closed"),
            1, ["[A5] S2 FACT measured: examined: 0"])
    expect2("A5: an open population with nothing named missing",
            swap2("  missing: the files added since\n", ""), 1,
            ["[A5] S3 NONE: an open population names what is missing"])
    expect2("A5: examined: in the wrong shape",
            swap2("  examined: 91 tests, closed", "  examined: all of them"), 1,
            ["[A5] S2 FACT measured: examined: is '<n> <unit>, closed'"])
    # A8
    expect2("A8: a CORRECT with no evidence",
            swap2("  now: early\n  evidence: cyanrip@ee0221c:src/cyanrip_log.c:1-20\n",
                  "  now: early\n"), 1,
            ["[A8] S9 CORRECT: needs a evidence: field"])
    # A1, in one lap
    expect2("A1: a status with no term:", swap2("  term: S4\n", ""), 1,
            ["[A1] S5 TERM met: needs a term: field"])
    expect2("A1: term: naming what is not a TERM set",
            swap2("  term: S4\n", "  term: S1\n"), 1,
            ["[A1] S5 TERM met: term: S1 does not name a TERM set"])
    expect2("A1: on: that is neither side",
            swap2("  on: them", "  on: somebody"), 1,
            ["[A1] S7 TERM pending: on: is us or them"])
    expect2("A1: a GO over a close condition with no status",
            swap2("S5 TERM met: It did.\n  term: S4\n",
                  "S5 TERM met: It did.\n  term: S6\n"), 1,
            ["[A1] S13 VERDICT: close condition cyanrip:R30.L1.S4 has no status"])
    expect2("A1: a GO over an unmet close condition",
            swap2("S5 TERM met: It did.\n  term: S4\n  evidence: run: meson test -C build => Ok: 91\n",
                  "S5 TERM unmet: It did not.\n  term: S4\n  reason: two failed\n"), 1,
            ["[A1] S13 VERDICT: close condition cyanrip:R30.L1.S4 is unmet"])
    expect2("A1: a GO over the author's own pending half",
            swap2("  on: them", "  on: us"), 1,
            ["[A1] S13 VERDICT: close condition cyanrip:R30.L1.S6 is pending "
             "on the author's own side"])
    expect2("A1: an OPEN over an unmet condition is not refused",
            swap2("S5 TERM met: It did.\n  term: S4\n  evidence: run: meson test -C build => Ok: 91\n",
                  "S5 TERM unmet: It did not.\n  term: S4\n  reason: two failed\n"), 0,
            ["well formed"], verdict="OPEN")
    expect2("A1: after lap 1, a TERM set that restates nothing",
            GOOD2, 1, ["[A1] S4 TERM set: close conditions are fixed in lap 1"],
            lp=3)
    # A2, in one lap
    expect2("A2: a verdict: on something other than a WILL",
            swap2("  holds: cyanrip@ee0221c\n",
                  "  holds: cyanrip@ee0221c\n  verdict: GO\n"), 1,
            ["[A2] S1 FACT read: only a WILL carries a pre-committed verdict:"])
    expect2("A2: a verdict: that is not GO or HOLD",
            swap2("  verdict: GO\n", "  verdict: SOON\n"), 1,
            ["[A2] S10 WILL: verdict: is GO or HOLD"])
    expect2("A2: a pre-committed verdict owned by the other side",
            swap2("S10 WILL: Our next lap is GO.\n  owner: us",
                  "S10 WILL: Our next lap is GO.\n  owner: them"), 1,
            ["[A2] S10 WILL: a pre-committed verdict: is the author's"])
    expect2("A2: unless: with no verdict:",
            swap2("  verdict: GO\n", ""), 1,
            ["[A2] S10 WILL: unless: qualifies a verdict:"])
    # LSL 4: a pre-commit's when: is the literal A2 binds (our round 30 lap 3
    # S10, amended by Platterpus's lap 4 S36). GOOD2 is an LSL 2 lap, so under
    # LSL 3 and 4 it also meets B1-B3; these assert on the A2 literal alone.
    def at_lsl(n, body):
        return check2(lap2("cyanrip-fork", 30, 1, "GO",
                           body.replace("{verdict}", "GO")
                           ).replace("LSL: 2", f"LSL: {n}"), empty)
    literal = "in LSL 4 a WILL carrying verdict: says exactly 'when: our next lap'"
    outcome("LSL 4: a pre-commit whose when: is not the literal is refused",
            at_lsl(4, GOOD2), 1,
            [f"[A2] S10 WILL: {literal}", "'once the run is filed'"])
    code, out = at_lsl(4, swap2("  when: once the run is filed\n",
                                "  when: our next lap\n"))
    outcome("LSL 4: the literal is accepted", (0, out), 0, [], absent=[literal])
    code, out = at_lsl(3, GOOD2)
    outcome("LSL 3 keeps the rule it was written under", (0, out), 0, [],
            absent=[literal])
    # A3
    expect2("A3: a finding of ours with no portable:",
            swap2("  portable: yes\n", ""), 1,
            ["[A3] S8 FINDING ours: a finding of ours says whether"])
    expect2("A3: a FIXED finding with no landed:",
            swap2("  landed: cyanrip@ee0221c:src/cyanrip_log.c:1\n", ""), 1,
            ["[A3] S8 FINDING ours: a FIXED finding names where"])
    expect2("A3: a BLOCKING finding with no breaks:",
            swap2("  target: FIXED\n  landed: cyanrip@ee0221c:src/cyanrip_log.c:1\n",
                  "  target: BLOCKING\n"), 1,
            ["[A3] S8 FINDING ours: a BLOCKING finding names what it breaks"])
    expect2("A3: a FINDING target that is not one of its three",
            swap2("  target: FIXED\n", "  target: SOON\n"), 1,
            ["[A3] S8 FINDING ours: a FINDING's target: is NEXT-ROUND, "
             "BLOCKING or FIXED"])
    expect2("A3: a finding of ours in the other side's tree",
            swap2("  in: cyanrip@ee0221c:src/cyanrip_log.c\n",
                  "  in: platterpus@183073b:README\n"), 1,
            ["[A3] S8 FINDING ours: a finding of ours is in cyanrip's tree"])
    expect2("A3: a finding of yours in the author's own tree",
            swap2("S8 FINDING ours:", "S8 FINDING yours:"), 1,
            ["[A3] S8 FINDING yours: a finding of yours cannot be in the "
             "author's own tree"])
    nr = swap2("  target: FIXED\n  landed: cyanrip@ee0221c:src/cyanrip_log.c:1\n",
               "  target: NEXT-ROUND\n")
    expect2("A3 as amended: ours, not portable, blocking nothing, is for a commit",
            nr.replace("  portable: yes", "  portable: no"), 1,
            ["[A3] S8 FINDING ours: a finding of ours that cannot hold"])
    expect2("A3 as amended: ours and not portable is fine when it blocks",
            nr.replace("  target: NEXT-ROUND\n",
                       "  target: BLOCKING\n  breaks: the pin's log\n")
              .replace("  portable: yes", "  portable: no"), 0, ["well formed"])
    # A6
    expect2("A6: a basis naming a WILL",
            swap2("  basis: S1, S5", "  basis: S1, S10"), 1,
            ["[A6] S13 VERDICT: basis: S10 is a WILL"])
    expect2("A6: a basis naming an UNKNOWN",
            swap2("  basis: S1, S5", "  basis: S11"), 1,
            ["[A6] S13 VERDICT: basis: S11 is a UNKNOWN"])
    expect2("A6: a basis naming a relayed fact",
            swap2("  basis: S1, S5", "  basis: S12"), 1,
            ["[A6] S13 VERDICT: basis: S12 is a FACT relayed"])
    expect2("A6: a refusal whose only reason is a relay",
            GOOD2 + "S14 REFUSE: Their wording.\n  re: S1\n  because: S12\n", 1,
            ["[A6] S14 REFUSE: because: S12 is a FACT relayed"])
    # A7, in one lap
    expect2("A7: answers: naming a statement of our own",
            GOOD2 + "S14 ACCEPT: Our own point.\n  re: S1\n  answers: S1\n", 1,
            ["[A7] S14 ACCEPT: answers: S1 does not name an ASK of the other side's"])

    # Rules that read the round: A1 across laps, A2 and A7.
    rnd = pathlib.Path(tmp) / "round"
    (rnd / "inbound").mkdir(parents=True)
    (rnd / "round-31-lap-01.md").write_text(lap2("cyanrip-fork", 31, 1, "OPEN",
        "S1 TERM set: The Full run passes.\n  requires: the Full run\n\n"
        "S2 WILL: Our lap 3 is GO.\n  owner: us\n  when: once lap 2 lands\n"
        "  verdict: GO\n  unless: the run fails\n\n"
        "S3 VERDICT: OPEN\n  basis: S1\n"))
    theirs2 = ("S1 TERM {g}: Our half is done.\n  term: cyanrip:R31.L1.S1\n"
               "{f}\n"
               "S2 ASK: Will you name the pin?\n  target: BLOCKING\n"
               "  breaks: the pin's approval\n\n"
               "S3 VERDICT: OPEN\n  basis: S1\n")
    lap2_path = rnd / "inbound" / "round-31-lap-02.md"

    def their_lap2(g, f):
        lap2_path.write_text(lap2("platterpus", 31, 2, "OPEN",
                                  theirs2.format(g=g, f=f)))

    ANSWER = ("S1 ACCEPT: Yes, the pin is named.\n  re: platterpus:R31.L2.S2\n"
              "  answers: platterpus:R31.L2.S2\n\n")

    def our_lap3(verdict, body):
        return lap2("cyanrip-fork", 31, 3, verdict, body)

    GO3 = ANSWER + "S2 VERDICT: GO\n  basis: S1\n"
    their_lap2("met", "  evidence: run: true => ok")
    outcome("A1/A7 across laps: met by them and answered by us, GO is fine",
            check2(our_lap3("GO", GO3), rnd), 0,
            ["checked against 1 close condition(s)", "1 answered", "well formed"])
    outcome("A7: their blocking question unanswered holds our GO",
            check2(our_lap3("GO", "S1 NOTE: no answer.\n\n"
                            "S2 FACT measured: x.\n  evidence: run: true => ok\n"
                            "  holds: 0.9.4\n  examined: 1 run, closed\n\n"
                            "S3 VERDICT: GO\n  basis: S2\n"), rnd), 1,
            ["[A7] S3 VERDICT: platterpus:R31.L2.S2 is a BLOCKING question "
             "with no answers: from the author"])
    their_lap2("pending", "  on: us\n  remains: their release")
    outcome("A1: pending on THEIR side (their on: us) does not hold our GO",
            check2(our_lap3("GO", GO3), rnd), 0, ["well formed"])
    their_lap2("pending", "  on: them\n  remains: your release")
    outcome("A1: pending on OUR side (their on: them) holds our GO",
            check2(our_lap3("GO", GO3), rnd), 1,
            ["[A1] S2 VERDICT: close condition cyanrip:R31.L1.S1 is pending on "
             "the author's own side"])
    lap2_path.unlink()
    code, out = check2(our_lap3("GO", "S1 FACT measured: x.\n"
                                "  evidence: run: true => ok\n  holds: 0.9.4\n"
                                "  examined: 1 run, closed\n\n"
                                "S2 VERDICT: GO\n  basis: S1\n"), rnd)
    refused = re.findall(r"^REFUSED .*$", out, re.M)
    if code != 1 or len(refused) != 1 or "[A1] S2 VERDICT: close condition " \
            "cyanrip:R31.L1.S1 has no status" not in refused[0]:
        fail(f"A1: without their lap, the condition has no status, and that "
             f"is the only refusal: exit {code}\n{out}")
    else:
        print("ok   A1: without their lap, the condition has no status")
    their_lap2("met", "  evidence: run: true => ok")
    outcome("A2: our lap 1 pre-committed GO, and an OPEN lap 3 must say why",
            check2(our_lap3("OPEN", ANSWER + "S2 VERDICT: OPEN\n  basis: S1\n"),
                   rnd), 1,
            ["[A2] S2 VERDICT: says OPEN, and cyanrip:R31.L1.S2 pre-committed GO"])
    outcome("A2: the same OPEN naming the unless that came true is fine",
            check2(our_lap3("OPEN", ANSWER +
                   "S2 FACT measured: The run failed.\n  evidence: run: true => ok\n"
                   "  holds: 0.9.4\n  examined: 1 run, closed\n"
                   "  triggers: cyanrip:R31.L1.S2\n\n"
                   "S3 VERDICT: OPEN\n  basis: S2\n"), rnd), 0, ["well formed"])
    outcome("A2: triggers: naming a statement that is not a pre-commit",
            check2(our_lap3("GO", ANSWER.replace(
                "  answers:", "  triggers: cyanrip:R31.L1.S1\n  answers:")
                + "S2 VERDICT: GO\n  basis: S1\n"), rnd), 1,
            ["[A2] S1 ACCEPT: triggers: cyanrip:R31.L1.S1 does not name a "
             "pre-committed WILL"])
    # The lap under check stands in for a held copy of itself.
    # The stale copy is well formed and answers nothing, so reading it in
    # place of the lap under check would fail A7.
    (rnd / "round-31-lap-03.md").write_text(our_lap3("GO", "S1 FACT measured: x.\n"
        "  evidence: run: true => ok\n  holds: 0.9.4\n  examined: 1 run, closed\n\n"
        "S2 VERDICT: GO\n  basis: S1\n"))
    outcome("the lap under check stands in for a stale held copy of itself",
            check2(our_lap3("GO", GO3), rnd), 0, ["well formed"])

# 13. LSL 3: B1-B3, accepted in round 28. Each refusal on a lap built for it,
#     and B1's re-run against a repository built here, so no real tree or
#     network can move a result.

def lap3(author, rnd, lp, verdict, body, from_commit="ee0221c"):
    head = (f"HANDSHAKE-PROTOCOL: 5\nHANDSHAKE-ROUND: {rnd}\n"
            f"HANDSHAKE-LAP: {lp}\nHANDSHAKE-FROM: {author}\n"
            f"HANDSHAKE-VERDICT: {verdict}\n")
    if from_commit:
        head += f"HANDSHAKE-FROM-COMMIT: {from_commit}\n"
    return f"{head}\nLSL: 3\n\n{body}"


with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    empty = tmp / "empty"
    (empty / "inbound").mkdir(parents=True)

    def v3(body, verdict="GO", **kw):
        return check2(lap3("cyanrip-fork", 30, 1, verdict,
                           body.replace("{verdict}", verdict), **kw), empty)

    outcome("LSL 3: LSL 2's example is well formed under it", v3(GOOD2), 0,
            ["LSL 3:", "well formed", "B1: 4 run: result(s) in this lap, none "
             "re-run: --rerun was not given"], absent=["REFUSED"])

    # B2
    BARE = ("S1 FACT measured: The suite passes.\n"
            "  evidence: run: meson test -C build => Ok: 91\n"
            "  holds: 0.9.4\n  examined: 91 tests, closed\n\n"
            "S2 VERDICT: {verdict}\n  basis: S1\n")
    outcome("B2: a GO over a round with no close condition is refused",
            v3(BARE), 1,
            ["[B2] S2 VERDICT: a GO in LSL 3 waits for at least one close "
             "condition"])
    outcome("B2 is LSL 3's: the same GO in LSL 2 only says A1 found none",
            check2(lap2("cyanrip-fork", 30, 1, "GO",
                        BARE.replace("{verdict}", "GO")), empty), 0,
            ["none is, so A1 had nothing to wait for", "well formed"],
            absent=["[B2]"])
    outcome("B2: an OPEN over no close condition is not refused",
            v3(BARE, verdict="OPEN"), 0, ["well formed"], absent=["[B2]"])

    # B1, the shape
    outcome("B1: a run: with no commit to have run at",
            v3(GOOD2, from_commit=None), 1,
            ["[B1] S2 FACT measured: a run: in LSL 3 names the commit it ran "
             "at"])
    outcome("B1: an at: that is not a commit of the author's tree",
            v3(GOOD2.replace("  examined: 91 tests, closed\n",
                             "  examined: 91 tests, closed\n"
                             "  at: platterpus@183073b\n")), 1,
            ["[B1] S2 FACT measured: at: names a commit of the author's tree"])

    # B3, and what it does to A7, on a round whose other side asks BLOCKING
    rnd3 = tmp / "round"
    (rnd3 / "inbound").mkdir(parents=True)
    (rnd3 / "round-32-lap-01.md").write_text(lap2("cyanrip-fork", 32, 1, "OPEN",
        "S1 TERM set: The Full run passes.\n  requires: the Full run\n\n"
        "S2 VERDICT: OPEN\n  basis: S1\n"))
    (rnd3 / "inbound" / "round-32-lap-02.md").write_text(lap2(
        "platterpus", 32, 2, "OPEN",
        "S1 TERM met: It passed.\n  term: cyanrip:R32.L1.S1\n"
        "  evidence: run: true => ok\n\n"
        "S2 ASK: Will you name the pin?\n  target: BLOCKING\n"
        "  breaks: the pin's approval\n\n"
        "S3 VERDICT: OPEN\n  basis: S1\n"))
    NOTE_ANSWER = ("S1 NOTE: We will get to it.\n  answers: platterpus:R32.L2.S2\n\n"
                   "S2 FACT measured: x.\n  evidence: run: true => ok\n"
                   "  holds: 0.9.4\n  examined: 1 run, closed\n\n"
                   "S3 VERDICT: GO\n  basis: S2\n")
    outcome("B3: answers: on a NOTE is refused, and answers nothing for A7",
            check2(lap3("cyanrip-fork", 32, 3, "GO", NOTE_ANSWER), rnd3), 1,
            ["[B3] S1 NOTE: answers: on a NOTE, which carries no claim",
             "[A7] S3 VERDICT: platterpus:R32.L2.S2 is a BLOCKING question "
             "with no answers: from the author"])
    outcome("B3 is LSL 3's: under LSL 2 the NOTE's answers: still counts",
            check2(lap2("cyanrip-fork", 32, 3, "GO", NOTE_ANSWER), rnd3), 0,
            ["1 answered", "well formed"], absent=["[B3]"])
    outcome("B3: an ACCEPT that answers is fine under LSL 3",
            check2(lap3("cyanrip-fork", 32, 3, "GO", NOTE_ANSWER.replace(
                "S1 NOTE: We will get to it.\n",
                "S1 ACCEPT: Yes, the pin is named.\n  re: platterpus:R32.L2.S2\n")),
                rnd3), 0, ["1 answered", "well formed"], absent=["[B3]"])

    # B1 --rerun, against a repository of our own side built here: a marked
    # tool, an unmarked one, and git itself.
    repo = tmp / "ours"
    repo.mkdir()
    g(repo, "init", "-q", "-b", "platterpus-fork")
    (repo / "tools").mkdir()
    (repo / "tools" / "say.py").write_text(
        "#!/usr/bin/env python3\n# LSL-RERUN: commit-only\nprint('hello 42')\n")
    (repo / "tools" / "unmarked.py").write_text("print('hello 42')\n")
    # Round 28 lap 6 S27's cases: a marked tool that fails, one that reads its
    # standard input, and one whose output is not UTF-8.
    (repo / "tools" / "fails.py").write_text(
        "#!/usr/bin/env python3\n# LSL-RERUN: commit-only\n"
        "import sys\nprint('hello 42')\nsys.exit(1)\n")
    (repo / "tools" / "reads.py").write_text(
        "#!/usr/bin/env python3\n# LSL-RERUN: commit-only\n"
        "import sys\nprint('read', len(sys.stdin.read()))\n")
    (repo / "tools" / "bytes.py").write_text(
        "#!/usr/bin/env python3\n# LSL-RERUN: commit-only\n"
        "import sys\nsys.stdout.buffer.write(b'\\xff\\xfe hello 42\\n')\n")
    # Round 29 lap 1 S29: the marker is a line, not a substring anywhere.
    (repo / "tools" / "codemark.py").write_text(
        "#!/usr/bin/env python3\nx = 'LSL-RERUN: commit-only'\nprint('hello 42')\n")
    g(repo, "add", "tools")
    g(repo, "commit", "-q", "-m", "tools")
    at = g(repo, "rev-parse", "--short=12", "HEAD")

    def rr(cmd_result, *extra, fields="", stdin_text=None, env=None):
        body = ("S1 FACT measured: The tool said so.\n"
                f"  evidence: run: {cmd_result}\n{fields}"
                "  holds: 0.9.4\n  examined: 1 run, closed\n\n"
                "S2 VERDICT: OPEN\n  basis: S1\n")
        return check2(lap3("cyanrip-fork", 30, 1, "OPEN", body,
                           from_commit=at), empty, "--ours", str(repo), *extra,
                      stdin_text=stdin_text, env=env)

    outcome("B1: a marked tool re-run at its commit matches its quoted result",
            rr('python3 tools/say.py => "hello 42"', "--rerun"), 0,
            ["1 re-run and matched, 0 re-run and not matched", "well formed"],
            absent=["UNCHECKED"])
    outcome("B1: a quoted result the re-run did not print is refused",
            rr('python3 tools/say.py => "hello 43"', "--rerun"), 1,
            [f"[B1] S1 FACT measured: re-run at cyanrip@{at}, and its output "
             "does not contain the quoted result \"hello 43\""])
    outcome("B1: an elided quote matches its parts in order",
            rr('python3 tools/say.py => "hel…42"', "--rerun"), 0,
            ["1 re-run and matched"])
    outcome("B1: parts in the wrong order do not match",
            rr('python3 tools/say.py => "42…hel"', "--rerun"), 1, ["[B1]"])
    outcome("B1: a read-only git query is re-run",
            rr('git show HEAD:tools/say.py => "hello 42"', "--rerun"), 0,
            ["1 re-run and matched"])
    outcome("B1: a tool that does not declare itself is not re-run",
            rr('python3 tools/unmarked.py => "hello 42"', "--rerun"), 0,
            ["UNCHECKED run: tools/unmarked.py does not declare "
             "'LSL-RERUN: commit-only'", "0 re-run and matched"])
    outcome("B1: a command that needs a shell is not re-run",
            rr('python3 tools/say.py | cat => "hello 42"', "--rerun"), 0,
            ["UNCHECKED run: not a simple command"])
    outcome("B1: a git command that is not a read-only query is not re-run",
            rr('git commit -m x => "hello 42"', "--rerun"), 0,
            ["UNCHECKED run: git commit is not one of the read-only queries"])
    outcome("B1: a result with nothing quoted is not compared",
            rr('python3 tools/say.py => hello 42', "--rerun"), 0,
            ["UNCHECKED run: its result quotes no output to compare"])
    # Platterpus round 29 lap 4 S9: git sizes an abbreviated hash by the
    # clone's object count. core.abbrev=12 in the checker's own environment
    # stands in for a clone big enough to print longer hashes; the re-run
    # pins seven, so a seven-character quote followed by text still matches.
    short7 = g(repo, "rev-parse", "--short=7", "HEAD")
    abbrev12 = dict(os.environ, GIT_CONFIG_COUNT="1",
                    GIT_CONFIG_KEY_0="core.abbrev", GIT_CONFIG_VALUE_0="12")
    outcome("B1: a re-run pins git's abbreviation, whatever the clone would print",
            rr(f'git log --oneline -1 {at} => "{short7} tools"', "--rerun",
               env=abbrev12), 0,
            ["1 re-run and matched, 0 re-run and not matched", "well formed"],
            absent=["UNCHECKED"])
    outcome("B1: without --rerun nothing is executed, and the checker says so",
            rr('python3 tools/say.py => "hello 43"'), 0,
            ["none re-run: --rerun was not given", "well formed"])

    # Round 28 lap 6 S27: the four --rerun defects, each a case.
    outcome("B1: a quote that is only an elision compares nothing, so it is "
            "unchecked, not matched",
            rr('python3 tools/say.py => "…"', "--rerun"), 0,
            ["UNCHECKED run: its result quotes only an elision",
             "0 re-run and matched"])
    outcome("B1: a command that failed does not match on its output",
            rr('python3 tools/fails.py => "hello 42"', "--rerun"), 0,
            ["UNCHECKED run: it exited 1, and its result does not say it "
             "expected a non-zero exit", "0 re-run and matched"])
    outcome("B1: a result that states its exit is held to it, and matches",
            rr('python3 tools/fails.py => exit 1, "hello 42"', "--rerun"), 0,
            ["1 re-run and matched"])
    outcome("B1: a result that states the wrong exit is refused",
            rr('python3 tools/say.py => exit 1, "hello 42"', "--rerun"), 1,
            ["[B1]", "it exited 0, and its result says exit 1"])
    outcome("B1: the re-run reads no standard input of the checker's",
            rr('python3 tools/reads.py => "read 0"', "--rerun",
               stdin_text="the checker's own input\n"), 0,
            ["1 re-run and matched"])
    outcome("B1: output that is not UTF-8 is compared, not raised",
            rr('python3 tools/bytes.py => "hello 42"', "--rerun"), 0,
            ["1 re-run and matched"])

    # Round 28 lap 6 S26: at: as B1's text has it, on any statement, once,
    # and naming a commit of the author's tree.
    outcome("B1: a statement with two at: fields is refused",
            rr('python3 tools/say.py => "hello 42"',
               fields=f"  at: {at}\n  at: {at}\n"), 1,
            ["[B1]", "this statement has 2"])
    outcome("B1: an at: naming no commit of the author's tree is refused",
            rr('python3 tools/say.py => "hello 42"',
               fields="  at: 0123456789ab\n"), 1,
            ["[B1]", "does not resolve"])
    outcome("B1: an at: on a statement with no run: is checked too",
            check2(lap3("cyanrip-fork", 30, 1, "OPEN",
                        "S1 NOTE: Nothing ran.\n  at: 0123456789ab\n\n"
                        "S2 VERDICT: OPEN\n  basis: S1\n", from_commit=at),
                   empty, "--ours", str(repo)), 1,
            ["[B1]", "does not resolve"])
    # Round 29 lap 1 S28-S29 and their lap 2 S15, as the shared text now
    # states them: each case fails if its reading is undone alone.
    outcome("B1: the marker inside a string of the tool's code does not mark it",
            rr('python3 tools/codemark.py => "hello 42"', "--rerun"), 0,
            ["UNCHECKED run: tools/codemark.py does not declare "
             "'LSL-RERUN: commit-only'", "0 re-run and matched"])
    outcome("B1: python is not python3",
            rr('python tools/say.py => "hello 42"', "--rerun"), 0,
            ["UNCHECKED run:", "0 re-run and matched"])
    outcome("B1: a word a shell would read as a comment is not re-run",
            rr('git show HEAD:tools/say.py #x => "hello 42"', "--rerun"), 0,
            ["UNCHECKED run: a shell would read '#x' as the start of a comment"])
    outcome("B1: .. after the colon of REV:path climbs out",
            rr('git show HEAD:../x => "hello 42"', "--rerun"), 0,
            ["UNCHECKED run: names a path outside the tree"])
    outcome("B1: a git query naming a branch is not re-run, since it moves",
            rr('git show platterpus-fork:tools/say.py => "hello 42"', "--rerun"), 0,
            ["UNCHECKED run: platterpus-fork:tools/say.py names the ref "
             "platterpus-fork, which can move"])
    outcome("B1: a git query reading the clock is not re-run",
            rr('git log -1 --format=%ar => "ago"', "--rerun"), 0,
            ["UNCHECKED run: --format=%ar reads the clock"])
    outcome("B1: a git query printing the checkout's path is not re-run",
            rr('git rev-parse --show-toplevel => "ours"', "--rerun"), 0,
            ["UNCHECKED run: --show-toplevel prints where the checkout is"])
    outcome("B1: a quoted string with no elision keeps its spaces",
            rr('python3 tools/say.py => " hello 42"', "--rerun"), 1,
            ["[B1]", "does not contain the quoted result \" hello 42\""])
    outcome("B1: the spaces beside an elision come off",
            rr('python3 tools/say.py => "hello …42"', "--rerun"), 0,
            ["1 re-run and matched"])
    outcome("B1: pre-exit 1 states no exit code",
            rr('python3 tools/fails.py => pre-exit 1, "hello 42"', "--rerun"), 0,
            ["UNCHECKED run: it exited 1, and its result does not say it "
             "expected a non-zero exit"])
    outcome("B1: exit with two spaces states no exit code",
            rr('python3 tools/fails.py => exit  1, "hello 42"', "--rerun"), 0,
            ["UNCHECKED run: it exited 1, and its result does not say it "
             "expected a non-zero exit"])
    outcome("B1: a result stating two different exit codes is refused",
            rr('python3 tools/fails.py => exit 1, exit 2, "hello 42"', "--rerun"), 1,
            ["[B1]", "its result states 2 different exit codes, 1, 2"])
    outcome("B1: a quoted string is a gap between words, so ex\"…\"it 1 "
            "states no code",
            rr('python3 tools/fails.py => ex"hello 42"it 1', "--rerun"), 0,
            ["UNCHECKED run: it exited 1, and its result does not say it "
             "expected a non-zero exit"])
    left = g(repo, "worktree", "list").splitlines()
    if len(left) != 1:
        fail(f"B1: --rerun left worktrees behind in the author's clone: {left}")
    else:
        print("ok   B1: --rerun leaves no worktree behind")

# 12. Platterpus's worked example, filed byte-exact from platterpus@18823c8
#     (sha256 ac34dbb7...). A second implementation's fixture, so agreement
#     here is two checkers built from one text, not one checker agreeing with
#     itself. Their LSL amendments 1 §6 states what each checker must say.
WEX = ROOT / "docs/handshake/inbound/artifacts/lap_language_round27_lap05.md"
wex = WEX.read_text(encoding="utf-8")
code, out = check_lap(wex)
ids = re.findall(r"^REFUSED .*?\[([A-Za-z0-9.]+)\]", out, re.M)
if (code, sorted(set(ids)), ids.count("LSL.1"), ids.count("LSL.field")) != \
        (1, ["LSL.1", "LSL.field"], 12, 14):
    fail(f"their example under LSL 1 must refuse exactly 12 kinds and 14 "
         f"fields, as their §6 says: exit {code}\n{out}")
else:
    print("ok   their example under LSL 1: 12 kinds and 14 fields, nothing else")
v2 = wex.replace("\nLSL: 1\n", "\nLSL: 2\n")
assert v2 != wex
outcome("their example under LSL 2 is well formed", check_lap(v2), 0,
        ["well formed", "checked against 4 close condition(s)"],
        absent=["REFUSED"])
# Their §6: "Remove its TERM pending and A1 refuses the GO." S10 becomes a
# status of S3 instead, so the numbering, the basis and every field stay
# valid and the one thing removed is S6's status.
pend = ("S10 TERM pending: Our half lands in the commit that releases this "
        "lap, and yours remains.\n  term: S6\n  on: them\n"
        "  remains: +platterpus.17, named in your closing lap\n")
assert v2.count(pend) == 1
code, out = check_lap(v2.replace(pend, "S10 TERM met: S3 again.\n  term: S3\n"
        "  evidence: cyanrip@e9d3868:docs/handshake/round-27-lap-04.md:60\n"))
refused = re.findall(r"^REFUSED .*$", out, re.M)
if code != 1 or len(refused) != 1 or \
        "[A1] S31 VERDICT: close condition platterpus:R27.L5.S6 has no status" \
        not in refused[0]:
    fail(f"their example with its pending half removed must be refused by "
         f"A1 alone: exit {code}\n{out}")
else:
    print("ok   their example with its pending half removed: A1 alone holds the GO")

# PROTOCOL v7 §6d, the short reading lap. Platterpus's round 30 lap 6 S18:
# the template as first proposed carries no TERM, so the lap it specifies is
# refused, because B2 will not let a GO stand over no close condition. Their
# S19 adds the conditions; our lap 7 amends it so that the opener's lap 1,
# whose reading comes before the other side's, says the other half is
# pending rather than met. Filled in by hand as the opener's lap 1 of an
# option-A round. The last two are both well formed, so a checker cannot
# tell them apart; what separates them is whether "read by both sides" is
# true when the second side has not read yet.
SD_HEAD = """HANDSHAKE-PROTOCOL: 6
HANDSHAKE-ROUND: 31
HANDSHAKE-LAP: 1
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-TO: platterpus
HANDSHAKE-OPENER: cyanrip
HANDSHAKE-VERDICT: GO

LSL: 4

## The run

S1 FACT read: The bundle is filed at `docs/rig-2026-09-30b-174a134`.
  evidence: cyanrip@c1a43dd:docs/rig-2026-09-30b-174a134/README.md:1
  holds: cyanrip@174a134
S2 FACT read: The pair was the newest when the run began, and still was when it ended.
  evidence: cyanrip@c1a43dd:docs/rig-2026-09-30b-174a134/README.md:1
  holds: cyanrip@174a134
S3 FACT read: Every cyanrip log in the bundle verifies.
  evidence: cyanrip@c1a43dd:docs/rig-2026-09-30b-174a134/README.md:1
  holds: cyanrip@174a134
S4 NONE: No defect in `+platterpus.19` in the run.
  scope: every cyanrip log in the bundle
  evidence: cyanrip@c1a43dd:docs/rig-2026-09-30b-174a134/README.md:1
  examined: 10 logs, closed
"""
SD_SETS = """
## Close conditions

S5 TERM set: The Full run on the pair, read by both sides.
  requires: our reading in this lap, and yours in your lap 2
S6 TERM set: The closing releases, named in the closing laps.
  requires: each side's closing lap naming its release
"""
SD_MET = """S7 TERM met: The Full run on the pair, read by both sides.
  term: cyanrip:R31.L1.S5
  evidence: cyanrip@c1a43dd:docs/rig-2026-09-30b-174a134/README.md:1
S8 TERM met: The closing releases, named in the closing laps.
  term: cyanrip:R31.L1.S6
  evidence: cyanrip@c1a43dd:docs/rig-2026-09-30b-174a134/README.md:1
"""
SD_PENDING = """S7 TERM pending: The Full run on the pair, read by both sides.
  term: cyanrip:R31.L1.S5
  on: them
  remains: your reading, in your lap 2
S8 TERM pending: The closing releases, named in the closing laps.
  term: cyanrip:R31.L1.S6
  on: them
  remains: your closing lap naming your release; ours is named in this lap
"""
def sd_verdict(n, basis):
    return f"\n## Verdict\n\nS{n} VERDICT: GO\n  basis: {basis}\n"

code, out = check_lap(SD_HEAD + sd_verdict(5, "S1 S2 S3 S4"))
refused = re.findall(r"^REFUSED .*$", out, re.M)
if code != 1 or len(refused) != 1 or "[B2]" not in refused[0]:
    fail(f"§6d as first proposed, with no TERM, must be refused by B2 alone "
         f"(round 30 lap 6 S18): exit {code}\n{out}")
else:
    print("ok   §6d as first proposed: B2 refuses its GO, as round 30 lap 6 S18 says")
for name, body in (("every condition met (lap 6 S19 as written)", SD_SETS + SD_MET),
                   ("the other half pending (lap 7's amendment)", SD_SETS + SD_PENDING)):
    outcome(f"§6d with {name}",
            check_lap(SD_HEAD + body + sd_verdict(9, "S1 S2 S3 S4")), 0,
            ["well formed", "checked against 2 close condition(s)"],
            absent=["REFUSED"])

# A statement in a held lap of every LSL version can be cited. The version
# list lived in two places, parse() and LSL_RE, and LSL 4 (049886f) reached
# only the first: a held LSL 4 lap parsed, and `re:` to one of its statements
# was refused as "a prose lap and has no statement numbers". Found writing
# our round 30 lap 7, whose AMENDs cite Platterpus's LSL 4 lap 6.
for held_v in (3, 4):
    with tempfile.TemporaryDirectory() as tmp:
        laps = pathlib.Path(tmp)
        (laps / "inbound").mkdir()
        (laps / "inbound" / "round-31-lap-01.md").write_text(
            "HANDSHAKE-PROTOCOL: 6\nHANDSHAKE-ROUND: 31\nHANDSHAKE-LAP: 1\n"
            "HANDSHAKE-FROM: platterpus\nHANDSHAKE-VERDICT: OPEN\n\n"
            f"LSL: {held_v}\n\nS1 ASK: Is the line stable?\n  target: NEXT-ROUND\n\n"
            "S2 VERDICT: OPEN\n  basis: S1\n", encoding="utf-8")
        ours = ("HANDSHAKE-PROTOCOL: 6\nHANDSHAKE-ROUND: 31\nHANDSHAKE-LAP: 2\n"
                "HANDSHAKE-FROM: cyanrip-fork\nHANDSHAKE-VERDICT: OPEN\n\n"
                "LSL: 4\n\nS1 ACCEPT: Yes.\n  re: platterpus:R31.L1.S1\n\n"
                "S2 VERDICT: OPEN\n  basis: S1\n")
        outcome(f"re: to a statement in a held LSL {held_v} lap",
                check_lap(ours, "--laps", str(laps)), 0, ["well formed"],
                absent=["prose lap", "REFUSED"])

if failures:
    print(f"\n{failures} failure(s)")
    sys.exit(1)
print("\nall checks passed")
