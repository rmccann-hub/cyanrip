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

"""tools/evidence.py, through a whole HR-2 move on repositories built here.

HR-2 (PROTOCOL.md v9 §17) moves run evidence to an orphan `evidence` branch.
Every step is asserted on an origin and clones made in a temporary directory,
reached by file:// URL, so nothing here touches the network or this tree:
the move commit built from an enumerated folder list (5b), rebuilt to the same
ID from the same list and instant (5c), its rows matching its files (5d), the
removal checked against the manifest (5d) and built on the commit the move
was built from (HR-2.1 b), the default branch's folders compared with the
evidence commit's before a removal merges (HR-2.1 b), a moved file read from a
cache and
never from the working clone (7), unfetched reported as 77 or, in CI's
evidence job, as a failure (6b, 8a), the manifest's strictness (4), tags kept
off evidence (8a), and a later run filed on the tip (10a).
"""

import datetime
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import evidence  # noqa: E402

TOOL = ROOT / "tools" / "evidence.py"
fails = 0

# No automatic gc or maintenance in the repositories built here: on CI's git a
# detached one was still writing into `.git` when a temporary directory was
# removed (tests/lap_and_run_tools.py).
GIT_ENV = {"GIT_CONFIG_COUNT": "2",
           "GIT_CONFIG_KEY_0": "gc.auto", "GIT_CONFIG_VALUE_0": "0",
           "GIT_CONFIG_KEY_1": "maintenance.auto", "GIT_CONFIG_VALUE_1": "false"}
os.environ.update(GIT_ENV)
for k in (evidence.REQUIRED_ENV, evidence.CACHE_ENV, evidence.URL_ENV):
    os.environ.pop(k, None)


def check(ok, msg):
    global fails
    if ok:
        print(f"ok   {msg}")
    else:
        print(f"FAIL: {msg}")
        fails += 1


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), "-c", "user.name=t",
                        "-c", "user.email=t@t", *args], capture_output=True,
                       text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args}: {r.stderr}")
    return r.stdout.strip()


def tool(root, *args, env=None):
    r = subprocess.run([sys.executable, str(TOOL), "--root", str(root),
                        *map(str, args)], capture_output=True, text=True,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                            **(env or {})})
    return r.returncode, r.stdout + r.stderr


A = "docs/rig-2026-01-01-aaaaaaa"
B = "docs/rig-2026-01-02-bbbbbbb"
X = "docs/handshake/inbound/artifacts/run-x"
FILES = {
    f"{A}/README.md": b"# run A\n",
    f"{A}/rips/a.log": b"log A\n" * 50,
    f"{B}/README.md": b"# run B\n",
    f"{B}/rips/b.log": b"log B\n" * 70,
    f"{B}/session/transcript.txt": b"Cache probe: nothing\n",
    # A real filing's name: spaces and two characters outside ASCII.
    f"{B}/album/full acceptance∶ angle‹bracket.log": b"album\n",
    f"{X}/data.txt": b"theirs\n",
    "docs/handshake/inbound/artifacts/loose.txt": b"a loose file stays\n",
    "docs/other.md": b"prose\n",
}
DATE = "2026-10-14T00:00:00Z"

with tempfile.TemporaryDirectory() as d:
    d = pathlib.Path(d)
    origin = d / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "platterpus-fork",
                    str(origin)], check=True)
    git(origin, "config", "uploadpack.allowAnySHA1InWant", "true")
    url = f"file://{origin}"
    work = d / "work"
    subprocess.run(["git", "clone", "-q", url, str(work)], check=True,
                   capture_output=True)
    git(work, "checkout", "-q", "-b", "platterpus-fork")
    for p, data in FILES.items():
        f = work / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "files")
    git(work, "push", "-q", "origin", "platterpus-fork")
    held = git(work, "rev-parse", "HEAD")

    # --- 5b: folders are enumerated from the tree, never passed as a pattern
    folders = evidence.tree_folders(work)
    check(folders == [X, A, B], f"three run folders found, the loose file is "
                                f"not one: {folders}")
    r = subprocess.run(["git", "-C", str(work), "ls-tree", "-r", "HEAD", "--",
                        "docs/rig-*"], capture_output=True, text=True)
    check(r.returncode == 0 and r.stdout == "",
          "git ls-tree with a pattern prints nothing and exits 0, which is why "
          "the list is enumerated (HR-2 5b)")
    bad = d / "bad.txt"
    bad.write_text("docs/rig-*\n")
    rc, o = tool(work, "build", "--folders", bad, "--date", DATE,
                 "--manifest-out", d / "x.tsv", "--source", url)
    check(rc == 1 and "not run folders" in o,
          f"a pattern in the folder list is refused: {rc} {o.strip()[-80:]}")

    # --- 5b-5d: the move commit, built twice from one list and one instant
    lst = d / "folders.txt"
    lst.write_text("\n".join(folders) + "\n")
    rc, o = tool(work, "build", "--folders", lst, "--date", DATE,
                 "--manifest-out", d / "m.tsv", "--source", url, "--push", url)
    check(rc == 0, f"build and push: {o.strip()}")
    rows = evidence.parse_manifest((d / "m.tsv").read_text())
    C = rows[0].commit
    moved = [p for p in FILES if evidence.run_folder(p)]
    check(sorted(r.path for r in rows) == sorted(moved),
          f"one row per moved file, READMEs included: {len(rows)}")
    check(all(r.last_default == held for r in rows),
          "every row names the default commit that held it")
    check(all(r.sha256 == evidence.sha256(FILES[r.path]) and
              r.size == len(FILES[r.path]) for r in rows),
          "each row's size and SHA-256 are the file's")
    # Each date as the instant it records, in seconds since the epoch: git's
    # text for an instant is not stable across versions (2.43 prints
    # 2026-10-14T00:00:00+00:00 for %aI and CI's 2.55 prints ...Z).
    instant = int(datetime.datetime(2026, 10, 14, tzinfo=datetime.timezone.utc)
                  .timestamp())
    who = git(origin, "log", "-1", "--format=%an <%ae> %at|%cn <%ce> %ct|%P", C)
    check(who == (f"evidence <evidence@invalid> {instant}|"
                  f"evidence <evidence@invalid> {instant}|"),
          f"identity, both dates and no parent are HR-2 5c's: {who}")
    check(git(origin, "rev-parse", "evidence") == C, "the push made evidence")
    rc, o = tool(work, "build", "--folders", lst, "--date", DATE,
                 "--manifest-out", d / "m2.tsv", "--source", url)
    check(rc == 0 and evidence.parse_manifest((d / "m2.tsv").read_text())[0]
          .commit == C, "rebuilt from the same list and instant, the commit ID "
                        "is the same (HR-2 5c)")
    check(git(work, "rev-parse", "--is-shallow-repository") == "false",
          "building never made the working clone shallow")

    # --- the removal commit: folders go, READMEs and the manifest stay
    before = evidence.Store(work)
    check(not before.moved() and before.where(f"{A}/rips/a.log") == "tree",
          "before the move every file is read from the checkout")
    for p in moved:
        if not p.endswith("/README.md"):
            git(work, "rm", "-q", "--", p)
    (work / evidence.MANIFEST).write_text((d / "m.tsv").read_text())
    git(work, "add", evidence.MANIFEST)
    git(work, "commit", "-q", "-m", "move")
    R = git(work, "rev-parse", "HEAD")
    store = evidence.Store(work)
    check(store.moved() and store.where(f"{A}/README.md") == "tree",
          "a README stays in the checkout as its folder's index")
    check(store.where(f"{A}/rips/a.log") is None,
          "a moved file this clone never fetched is held nowhere here")
    check(store.files(B) == sorted(p for p in moved if p.startswith(B + "/")),
          "a folder's files are listed from the manifest after the move")
    check(store.folders() == [X, A, B], f"folders after the move: "
                                        f"{store.folders()}")

    rc, o = tool(work, "cat", f"{A}/rips/a.log")
    check(rc == 77 and "UNPROBED" in o, f"unfetched is 77, never absent: {rc}")
    rc, o = tool(work, "cat", f"{A}/rips/a.log",
                 env={evidence.REQUIRED_ENV: "1"})
    check(rc == 1 and "FAIL" in o, "in CI's evidence job it is a failure")

    # --- 7: fetched into the cache, never into the working clone
    rc, o = tool(work, "fetch")
    check(rc == 0, f"fetch: {o.strip()}")
    check(git(work, "rev-parse", "--is-shallow-repository") == "false",
          "the --depth 1 fetch went to the cache, so the clone is not shallow")
    check(subprocess.run(["git", "-C", str(work), "cat-file", "-e", C],
                         capture_output=True).returncode != 0,
          "the working clone still does not hold the evidence commit")
    store = evidence.Store(work)
    check(store.where(f"{A}/rips/a.log") == "cache"
          and store.read(f"{A}/rips/a.log") == FILES[f"{A}/rips/a.log"],
          "after fetching, a moved file is read from the cache, byte for byte")
    name = f"{B}/album/full acceptance∶ angle‹bracket.log"
    check(store.read(name) == FILES[name], "a name with spaces and non-ASCII "
                                           "characters survives the move")

    # --- 5d after the push
    rc, o = tool(work, "verify-move", C, R)
    check(rc == 0, f"verify-move: {o.strip()}")
    short = [r for r in rows if r.path != f"{B}/rips/b.log"]
    s2 = evidence.Store(work, evidence.format_manifest(short))
    probs = evidence.verify_move(s2, C, R)
    check(any("b.log is deleted" in p and "no manifest row" in p
              for p in probs), f"a deleted path with no row is named: {probs}")
    check(git(work, "rev-parse", f"{R}^") == held,
          "the removal's first commit has the build's default commit as its "
          "parent (HR-2.1 b)")

    # --- 8a: rows against their files, the commit on evidence
    rc, o = tool(work, "verify-rows")
    check(rc == 77, f"without the branch, reachability is unprobed: {rc} {o}")
    rc, o = tool(work, "fetch", "--branch")
    rc, o = tool(work, "verify-rows")
    check(rc == 0, f"verify-rows with the branch fetched: {o.strip()}")
    tampered = [r._replace(sha256="0" * 64) if r.path == f"{A}/rips/a.log"
                else r for r in rows]
    probs, _ = evidence.verify_rows(
        evidence.Store(work, evidence.format_manifest(tampered)))
    check(any("a.log" in p for p in probs), f"a wrong hash is named: {probs}")
    base = d / "base"
    subprocess.run(["git", "clone", "-q", url, str(base)], check=True,
                   capture_output=True)

    # --- HR-2.1 b: before a removal merges, each folder it moves is the same
    # on the default branch as it stands as at the evidence commit
    rc, o = tool(work, "verify-rows", "--base", held)
    check(rc == 0 and "3 moved folder(s) the same on the default branch" in o,
          f"a removal over an unchanged default branch passes: {o.strip()}")
    rc, o = tool(work, "verify-rows", "--current", held)
    check(rc == 2 and "--current needs --base" in o,
          f"--current alone is refused: {rc}")
    git(base, "checkout", "-q", "-b", "late")
    (base / A / "rips" / "a.log").write_bytes(b"changed after the build\n")
    git(base, "rm", "-q", "-r", "--", X)
    git(base, "commit", "-q", "-am", "late")
    late = git(base, "rev-parse", "HEAD")
    git(work, "fetch", "-q", str(base), "late")
    rc, o = tool(work, "verify-rows", "--base", held, "--current", late)
    check(rc == 1 and f"FAIL: {A}: tree" in o
          and "a file changed after the build, so the removal waits" in o
          and f"FAIL: {X} is not on the default branch" in o and B not in o,
          f"a folder changed or gone since the build holds the removal, and "
          f"only those are named: {o.strip()}")
    # The removal built on a later commit than the move was built from.
    git(base, "checkout", "-q", "-b", "slow", held)
    (base / "docs" / "other.md").write_bytes(b"prose, edited first\n")
    git(base, "commit", "-q", "-am", "first")
    for p in moved:
        if not p.endswith("/README.md"):
            git(base, "rm", "-q", "--", p)
    (base / evidence.MANIFEST).write_text((d / "m.tsv").read_text())
    git(base, "add", evidence.MANIFEST)
    git(base, "commit", "-q", "-m", "move, second")
    R2 = git(base, "rev-parse", "HEAD")
    git(work, "fetch", "-q", str(base), "slow")
    probs = evidence.verify_move(evidence.Store(work), C, R2)
    check(len(probs) == 1 and "parent is" in probs[0] and "HR-2.1 b" in probs[0],
          f"a removal not built on the move's default commit is named: {probs}")

    # --- 4: the manifest is read strictly
    head = evidence.HEADER + "\n"
    ok_row = f"a/b\t1\t{'a' * 64}\t{'b' * 40}\t\n"
    for text, what in ((head + ok_row, None),
                       (head + ok_row.rstrip("\n"), "newline"),
                       ("path\tbytes\n" + ok_row, "header"),
                       (head + ok_row + ok_row, "twice"),
                       (head + ok_row.replace("a/b", "b/c") + ok_row, "order"),
                       (head + ok_row.replace("a" * 64, "a" * 63), "SHA-256"),
                       (head + ok_row.replace("b" * 40, "b" * 7), "40-char"),
                       (head + ok_row.replace("\t\n", "\tzz\n"), "neither"),
                       (head + "a\tb\t1\n", "fields")):
        try:
            evidence.parse_manifest(text)
            got = None
        except evidence.ManifestError as e:
            got = str(e)
        check((got is None) if what is None else (got and what in got),
              f"manifest {'accepted' if what is None else 'refused: ' + what}"
              f" ({got})")

    # --- 8a: no tag reaches evidence (in a clone holding it, as CI's job is)
    ci = d / "ci"
    subprocess.run(["git", "clone", "-q", url, str(ci)], check=True,
                   capture_output=True)
    git(ci, "fetch", "-q", "origin",
        "+refs/heads/evidence:refs/remotes/origin/evidence")
    git(ci, "tag", "fine", "origin/platterpus-fork")
    rc, o = tool(ci, "check-tags")
    check(rc == 0, f"a tag on the default branch is fine: {o.strip()}")
    git(ci, "tag", "bad", C)
    rc, o = tool(ci, "check-tags")
    check(rc == 1 and "bad reaches" in o, f"a tag on evidence fails: {o}")
    git(ci, "tag", "-d", "bad")

    # --- an overlay runs a command where the moved files are
    rc, o = tool(work, "run", "--folder", B, "--", "sh", "-c",
                 f"cat {B}/rips/b.log | wc -l")
    check(rc == 0 and o.strip().endswith("70"),
          f"run places a moved folder at its own path: {o.strip()}")
    rc, o = tool(work, "run", "--folder", B, "--", "true",
                 env={evidence.CACHE_ENV: str(d / "empty.git")})
    check(rc == 77, f"run over an unfetched folder is 77: {rc}")
    check(not (work / B / "rips").exists(),
          "the overlay wrote nothing into the checkout")

    # --- a row is given the files it names, not every file of its folders:
    # every file took a Settled facts row 20 to 25 s on CI's macOS runner
    # (2026-10-19, pull request #43), four such rows, and the test was killed
    s2 = evidence.Store(work)
    in_b = sorted(p for p in FILES if p.startswith(B + "/"))
    got = evidence.files_named(f"grep x {A[:18]}*/rips/b.log", s2)
    check(got == [f"{B}/rips/b.log"],
          f"a glob over two folders naming one file gives that file: {got}")
    got = evidence.files_named(f"grep -r x {B}/session", s2)
    check(got == [f"{B}/session/transcript.txt"],
          f"a folder inside a run folder gives the files under it: {got}")
    got = evidence.files_named(f"ls {B}/", s2)
    check(got == in_b, f"a run folder gives every file in it: {got}")
    got = evidence.files_named(f"cat {B}/rips/{{a,b}}.log", s2)
    check(got == in_b, f"a pattern fnmatch cannot read gives every file of "
                       f"its folder: {got}")

    # --- 10a: a later run, filed on the tip, never changing what is there
    staging = d / "staging"
    (staging / "rips").mkdir(parents=True)
    (staging / "README.md").write_bytes(b"# run C\n")
    (staging / "rips" / "c.log").write_bytes(b"log C\n")
    Cn = "docs/rig-2026-01-03-ccccccc"
    rc, o = tool(work, "file", staging, "--as", Cn, "--date", DATE,
                 "--push", url)
    check(rc == 0, f"file: {o.strip()}")
    E2 = git(origin, "rev-parse", "evidence")
    check(git(origin, "rev-parse", f"{E2}^") == C,
          "the new commit's only parent is the previous tip")
    check(git(origin, "diff", "--name-only", "--diff-filter=MD", C, E2) == "",
          "it changes and removes nothing")
    store = evidence.Store(work)
    new = [r for r in store.rows.values() if r.path.startswith(Cn + "/")]
    check(len(new) == 2 and all(r.commit == E2 and r.last_default == ""
                                for r in new),
          "its rows name the new commit and no default commit")
    check((work / Cn / "README.md").read_bytes() == b"# run C\n"
          and not (work / Cn / "rips").exists(),
          "its README is copied into the checkout, and nothing else")
    check(f"cyanrip@{E2}:{Cn}/rips/c.log sha256 " in o,
          "it prints each file's citation in HR-2 6a's form")
    rc, o = tool(work, "file", staging, "--as", Cn, "--push", url)
    check(rc == 1 and "already on evidence" in o,
          "a folder already on evidence is refused (HR-2 3)")

    # --- reachability through a cache that fetched the tip by hash first.
    # `fetch` takes each commit at depth 1, which marks the tip shallow; a
    # branch fetch after it did not deepen past that mark, so the earlier
    # commit read as NOT on evidence, and the lap checker refused a citation
    # of it. Found 2026-10-16, the first time the branch had two commits.
    late = {evidence.CACHE_ENV: str(d / "late.git")}
    rc, o = tool(work, "fetch", env=late)
    check(rc == 0, f"fetch every commit by hash first: {o.strip()}")
    rc, o = tool(work, "fetch", "--branch", env=late)
    check(rc == 0, f"then the branch: {o.strip()}")
    os.environ.update(late)
    try:
        s3 = evidence.Store(work)
        check(evidence.on_evidence(s3, C) is True,
              "the earlier evidence commit is on evidence after the branch "
              "fetch, though its child was fetched shallow first")
        check(evidence.on_evidence(s3, E2) is True, "and so is the tip")
    finally:
        del os.environ[evidence.CACHE_ENV]

print(f"\n{'all ok' if not fails else f'{fails} failure(s)'}")
sys.exit(1 if fails else 0)
