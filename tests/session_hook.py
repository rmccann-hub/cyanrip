#!/usr/bin/env python3
"""The session-start hook says it excluded the evidence branch only when it did.

.claude/hooks/session-start.sh adds `^refs/heads/evidence` to each remote's
fetch refspecs (HR-2, PROTOCOL.md v9 §17, point 7) and prints a line saying
so. It printed that line whether or not `git config --add` had worked (review
C item 4.7). This runs the hook, as Claude Code does, on scratch repositories:

  * one with a remote: the line is printed and the refspec is in the config;
  * the same again: nothing is printed, nothing is added twice;
  * one whose config is locked (`config.lock` present, which stops git even
    for root): the line says the branch is still fetched, and nothing claims
    otherwise.

The hook never fails a session, so each run must exit 0. Needs git 2.29 or
later, as the hook does; with an older git the hook says so, and this exits
77, skipped.
"""

import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOK = ROOT / ".claude" / "hooks" / "session-start.sh"
SPEC = "^refs/heads/evidence"

failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


def hook(repo):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo))
    return subprocess.run(["sh", str(HOOK)], cwd=repo, env=env,
                          capture_output=True, text=True, encoding="utf-8",
                          timeout=60)


def fetch_specs(repo):
    r = subprocess.run(["git", "-C", str(repo), "config", "--get-all",
                        "remote.origin.fetch"], capture_output=True,
                       text=True, encoding="utf-8", timeout=60)
    return r.stdout.splitlines()


def new_repo(path):
    for args in (["init", "-q", str(path)],
                 ["-C", str(path), "remote", "add", "origin",
                  "https://example.invalid/none.git"]):
        subprocess.run(["git"] + args, check=True, capture_output=True,
                       timeout=60)


with tempfile.TemporaryDirectory(prefix="cyanrip-hook-") as d:
    tmp = pathlib.Path(d)

    repo = tmp / "plain"
    new_repo(repo)
    r = hook(repo)
    if "no negative refspecs" in r.stdout:
        print(f"SKIP: {r.stdout.strip()}")
        sys.exit(77)
    if r.returncode != 0:
        fail(f"first run: exit {r.returncode}, stderr {r.stderr!r}")
    if r.stdout.strip() != "evidence: remote origin no longer fetches refs/heads/evidence":
        fail(f"first run printed {r.stdout!r}")
    specs = fetch_specs(repo)
    if specs.count(SPEC) != 1 or len(specs) != 2:
        fail(f"first run left the fetch refspecs {specs}, expected the "
             f"default and {SPEC}")

    r = hook(repo)
    if r.returncode != 0 or r.stdout.strip():
        fail(f"second run: exit {r.returncode}, printed {r.stdout!r}, "
             "expected nothing")
    if fetch_specs(repo).count(SPEC) != 1:
        fail(f"second run added {SPEC} again: {fetch_specs(repo)}")

    locked = tmp / "locked"
    new_repo(locked)
    (locked / ".git" / "config.lock").write_bytes(b"")
    r = hook(locked)
    if r.returncode != 0:
        fail(f"locked config: exit {r.returncode}; the hook must never fail "
             "a session")
    if "no longer fetches" in r.stdout:
        fail(f"locked config: the hook claimed the exclusion: {r.stdout!r}")
    if "evidence: remote origin still fetches refs/heads/evidence" not in r.stdout:
        fail(f"locked config: the failure is not said: {r.stdout!r}")
    (locked / ".git" / "config.lock").unlink()
    if SPEC in fetch_specs(locked):
        fail("locked config: the refspec was written after all, so the lock "
             "did not stop git and this case tests nothing")

if failures:
    print(f"{failures} failure(s)")
    sys.exit(1)
print("session-start hook: says the evidence branch is excluded only when git "
      "wrote it")
