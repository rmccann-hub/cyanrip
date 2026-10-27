#!/usr/bin/env python3
"""tools/tag-release-check.py must refuse every tag it has no grounds for.

The tag workflow (.github/workflows/tag-release.yml) creates a tag nobody can
move once rulesets protect it, and a workflow is tested only by running it. So
the decisions live in the tool, and this runs the tool against a repository it
builds: a release commit, a publish commit whose manifest names it, a topic
branch the release is not on, and manifests that disagree with themselves. Each
case asserts the exit code and the reason, because a refusal for the wrong
reason passes a test that checks the code alone.
"""

import json
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "tag-release-check.py"
VERSION = "0.9.4-rc2+platterpus.22"
SEQ = 7          # deliberately not 22: the message must carry the ledger's seq
failures = 0

ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def g(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True,
                          env=ENV).stdout.strip()


def commit(repo, name, text, msg):
    (repo / name).write_text(text)
    g(repo, "add", name)
    g(repo, "commit", "-q", "-m", msg)
    return g(repo, "rev-parse", "HEAD")


def manifest(channels):
    return json.dumps({"channels": channels, "schema": 2}, indent=1) + "\n"


def chan(version, sha, seq):
    return {"version": version, "commit": sha[:7], "release_seq": seq,
            "handshake_round": 32}


def run(repo, *args, msgfile=None):
    argv = [sys.executable, str(TOOL), *args, "--repo", str(repo)]
    if msgfile:
        argv += ["--message-file", str(msgfile)]
    p = subprocess.run(argv, capture_output=True, text=True, env=ENV)
    return p.returncode, p.stdout, p.stderr


def case(name, got, code, want=(), absent=()):
    global failures
    rc, out, err = got
    both = out + err
    bad = []
    if rc != code:
        bad.append(f"exit {rc}, wanted {code}")
    bad += [f"missing {w!r}" for w in want if w not in both]
    bad += [f"unexpected {w!r}" for w in absent if w in both]
    if bad:
        failures += 1
        print(f"FAIL: {name}: " + "; ".join(bad))
        print("  " + both.strip().replace("\n", "\n  "))
    else:
        print(f"ok: {name}")


with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    src = t / "src"
    src.mkdir()
    g(src, "init", "-q", "-b", "platterpus-fork")
    first = commit(src, "a", "1\n", "first")
    rel = commit(src, "a", "2\n", "the released build")
    commit(src, "release-manifest.json",
           manifest({"stable": chan(VERSION, rel, SEQ),
                     "beta": chan(VERSION, rel, SEQ)}), "publish")
    # A commit only a topic branch holds.
    g(src, "checkout", "-q", "-b", "claude/topic")
    topic = commit(src, "a", "3\n", "topic work")
    # Manifests that contradict themselves, each on its own branch from the
    # publish commit, so the release is still an ancestor of every one.
    for branch, chans in (
            ("seqs-disagree", {"stable": chan(VERSION, rel, SEQ),
                               "beta": chan(VERSION, rel, SEQ + 1)}),
            ("other-commit", {"stable": chan(VERSION, rel, SEQ),
                              "beta": chan(VERSION, first, SEQ)}),
            ("unresolvable", {"stable": dict(chan(VERSION, rel, SEQ),
                                             commit="0000000")})):
        g(src, "checkout", "-q", "-b", branch, "platterpus-fork")
        commit(src, "release-manifest.json", manifest(chans), branch)
    g(src, "checkout", "-q", "platterpus-fork")

    # The workflow's own shape: a clone, where the branch is origin/<name>.
    work = t / "work"
    subprocess.run(["git", "clone", "-q", "--no-local", "--branch",
                    "platterpus-fork", str(src), str(work)], check=True,
                   env=ENV)
    msg = t / "message"

    case("a release the manifest names at its commit is tagged",
         run(work, VERSION, rel, msgfile=msg), 0,
         ["tag=platterpus-fork-r22"])
    text = msg.read_text() if msg.exists() else ""
    for want in (f"commit: {rel}", f"release_seq: {SEQ}",
                 "channels: beta, stable", "Order releases by release_seq"):
        if want not in text:
            failures += 1
            print(f"FAIL: the tag message does not carry {want!r}")
    if "release_seq: 22" in text:
        failures += 1
        print("FAIL: release_seq was taken from the version, not the manifest")

    case("an abbreviated SHA is refused",
         run(work, VERSION, rel[:7]), 1, ["not a full 40-character"])
    case("a commit that does not exist is refused",
         run(work, VERSION, "1" * 40), 1, ["is not in this repository"])
    case("a version that is not this fork's is refused",
         run(work, "0.9.4-rc2", rel), 1, ["ends in +platterpus.N"])
    case("a commit only a topic branch holds is refused",
         run(work, VERSION, topic), 1,
         ["is not on origin/platterpus-fork"])
    case("a commit on the branch that the manifest does not name is refused",
         run(work, VERSION, first), 1,
         ["names 0.9.4-rc2+platterpus.22 at", f"not {first}"])
    case("a release the manifest does not name is refused",
         run(work, "0.9.4-rc2+platterpus.21", rel), 1,
         ["does not name 0.9.4-rc2+platterpus.21",
          "beta 0.9.4-rc2+platterpus.22"])
    case("channels disagreeing on release_seq are refused",
         run(work, VERSION, rel, "--ref", "origin/seqs-disagree"), 1,
         ["disagree on release_seq"])
    case("one channel naming the release at another commit is refused",
         run(work, VERSION, rel, "--ref", "origin/other-commit"), 1,
         ["beta channel names", f"not {rel}"])
    case("a manifest commit git cannot resolve is refused, not prefix-matched",
         run(work, VERSION, rel, "--ref", "origin/unresolvable"), 1,
         ["not exactly one commit here"])
    case("a ref that does not exist is refused",
         run(work, VERSION, rel, "--ref", "origin/nowhere"), 1,
         ["does not resolve"])

    g(work, "tag", "-a", "-m", "x", "platterpus-fork-r22", rel)
    case("a tag already at the commit is nothing to do",
         run(work, VERSION, rel), 3,
         ["tag=platterpus-fork-r22", "already exists at"])
    g(work, "tag", "-d", "platterpus-fork-r22")
    g(work, "tag", "-a", "-m", "x", "platterpus-fork-r22", first)
    case("a tag at another commit is never moved",
         run(work, VERSION, rel), 1, ["a tag is never moved"],
         absent=["tag=platterpus-fork-r22"])

if failures:
    print(f"{failures} failure(s)")
    sys.exit(1)
print("all cases pass")
