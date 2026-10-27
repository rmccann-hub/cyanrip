#!/usr/bin/env python3
"""tools/check-commit-subjects.py passes and fails the subjects it should.

It builds a scratch repository: an `upstream` branch standing for
origin/master, a base, and a change on top whose commits each carry one
subject. The tool must name exactly the three that break a rule (over 72
characters, a lower-case start, a full stop), and pass the one at exactly
72, the merge commit and the upstream commit, whose subjects break them too
but are not this change's to word. Then a range of good subjects alone
must pass, and a range git cannot resolve must exit 2.
"""

import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "check-commit-subjects.py"

failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t",
                           "-c", "user.email=t@example.invalid",
                           "-c", "commit.gpgsign=false", *args],
                          check=True, capture_output=True, text=True,
                          encoding="utf-8", timeout=60).stdout.strip()


def commit(repo, subject):
    git(repo, "commit", "-q", "--allow-empty", "-m", subject)
    return git(repo, "rev-parse", "--short", "HEAD")


def check(repo, base, head):
    return subprocess.run([sys.executable, str(TOOL), base, head,
                           "--upstream", "upstream", "--repo", str(repo)],
                          capture_output=True, text=True, encoding="utf-8",
                          timeout=60)


# One subject at the limit and one past it, by construction
EXACT = ("Keep a subject at the limit " + "x" * 72)[:72]
LONG = EXACT + "y"

with tempfile.TemporaryDirectory(prefix="cyanrip-subjects-") as d:
    repo = pathlib.Path(d)
    git(repo, "init", "-q", "-b", "main")
    commit(repo, "Start the history")
    base = git(repo, "rev-parse", "HEAD")

    # upstream's commit, merged into the change by a sync
    git(repo, "checkout", "-q", "-b", "upstream")
    up = commit(repo, "upstream's subject, in lower case and well over the limit of 72 characters.")
    git(repo, "checkout", "-q", "main")

    good = commit(repo, EXACT)
    long_ = commit(repo, LONG)
    lower = commit(repo, "fix the lower-case start")
    stop = commit(repo, "End with a full stop.")
    git(repo, "merge", "-q", "--no-ff", "upstream", "-m",
        "merge upstream's branch, a subject that breaks every rule there is, at length.")

    r = check(repo, base, "HEAD")
    named = {ln.split(" ", 1)[0] for ln in r.stdout.splitlines()
             if ln.split(" ", 1)[0] in (good, long_, lower, stop, up)}
    if r.returncode != 1:
        fail(f"a range with three bad subjects: exit {r.returncode}, expected 1")
    if named != {long_, lower, stop}:
        fail(f"named {sorted(named)}, expected {sorted([long_, lower, stop])}:\n{r.stdout}")
    for sha, why in ((long_, "73 characters, over 72"),
                     (lower, "does not begin with a capital letter"),
                     (stop, "ends with a full stop")):
        if not any(ln.startswith(sha) and ln.endswith(why) for ln in r.stdout.splitlines()):
            fail(f"{sha} is not named for {why!r}:\n{r.stdout}")
    if "3 problem(s) in 4 commit subject(s)" not in r.stdout:
        fail(f"the merge or upstream's commit was counted, or one was missed:\n{r.stdout}")

    r = check(repo, base, good)
    if r.returncode != 0 or "1 commit subject(s) checked" not in r.stdout:
        fail(f"a range of one good subject: exit {r.returncode}\n{r.stdout}")

    r = check(repo, base, "no-such-ref")
    if r.returncode != 2:
        fail(f"an unresolvable range: exit {r.returncode}, expected 2")

if failures:
    print(f"{failures} failure(s)")
    sys.exit(1)
print("commit subjects: three bad ones named, the limit, the merge and "
      "upstream's commit passed, a bad range refused")
