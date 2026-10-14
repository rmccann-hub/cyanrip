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

"""Read, fetch, file and check this repository's run evidence (HR-2).

HR-2 is PROTOCOL.md v9 §17. It moves what a run produced and nothing on the
default branch reads -- rig folders, logs, transcripts, diagnostics -- onto an
orphan branch named `evidence`, which only ever gains commits, and keeps
`docs/evidence-manifest.tsv` on the default branch: one row per file, with its
size, its SHA-256, the evidence commit that added it, and the last default
commit that held it. Laps cite a moved file as `cyanrip@<evidence commit>:<path>`
with its SHA-256. This tool is the one place that knows where a file is.

WHERE A FILE IS READ FROM, in this order:

  1. this checkout, when the file is in it -- every file until the move, and
     each run folder's README after it (HR-2 5a keeps it as the folder's index);
  2. this clone's object store, at the commit the manifest names: a clone that
     fetched the evidence branch, which is what CI's evidence job does;
  3. the evidence cache, a SEPARATE bare repository, `$CYANRIP_EVIDENCE_GIT` or
     `<git dir>/cyanrip-evidence.git`, which `fetch` fills. Never the working
     clone (HR-2 7): a --depth fetch into a full clone makes it shallow, and a
     shallow clone turns the lap checker's refusals into warnings.

Bytes read from 2 or 3 are checked against the row's size and SHA-256 before
anything sees them. A file found in none of them is NOT FETCHED, and a check
says so with exit 77 -- unprobed, never "absent" and never "passed". In CI's
evidence job `CYANRIP_EVIDENCE_REQUIRED=1` turns that into a failure (HR-2 6b,
8a). Nothing here reaches the network except `fetch`, `build --push` and
`file --push`: a check that reaches the network is not evidence about this
program.

    tools/evidence.py where docs/rig-2026-10-13-200530e/rips/full-acceptance.log
    tools/evidence.py cat PATH > out
    tools/evidence.py fetch [--branch]          # every commit the manifest names
    tools/evidence.py run [--folder F]... -- CMD...
    tools/evidence.py verify-rows [--base REV [--current REV]]
                                                # CI: each row against its file
    tools/evidence.py check-tags                # CI: no tag reaches evidence
    tools/evidence.py build --folders LIST --date ISO --manifest-out FILE [--push]
    tools/evidence.py verify-move EVIDENCE_COMMIT REMOVAL_COMMIT
    tools/evidence.py file STAGING --as docs/rig-NAME [--push]
"""

import argparse
import collections
import datetime
import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = "docs/evidence-manifest.tsv"
HEADER = "path\tbytes\tsha256\tevidence_commit\tlast_default_commit"
BRANCH = "evidence"
DEFAULT_BRANCH = "platterpus-fork"
REQUIRED_ENV = "CYANRIP_EVIDENCE_REQUIRED"
CACHE_ENV = "CYANRIP_EVIDENCE_GIT"
URL_ENV = "CYANRIP_EVIDENCE_URL"
# HR-2 5c: the move commit's author and committer, so either side can rebuild
# the other's commit from its folder list and compare IDs.
IDENTITY = ("evidence", "evidence@invalid")
UNPROBED = 77

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

Row = collections.namedtuple("Row", "path size sha256 commit last_default")


class ManifestError(Exception):
    pass


class NotFetched(Exception):
    """The manifest names the file and nothing here holds its bytes."""


class Mismatch(Exception):
    """Bytes were found and are not the ones the manifest names."""


def git(repo, *args, data=None, env=None, check=False):
    r = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed in {repo}: "
                           f"{r.stderr.decode('utf-8', 'replace').strip()}")
    return r


def out(r):
    return r.stdout.decode("utf-8", "surrogateescape").strip()


def required():
    """CI's evidence job: an unfetched file is a failure, not an unprobed one."""
    return os.environ.get(REQUIRED_ENV) == "1"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------
# The manifest (HR-2 4)

def parse_manifest(text):
    """Rows of docs/evidence-manifest.tsv, or ManifestError naming the line.

    Read strictly, because a manifest a reader has to guess at resolves a bare
    path two ways: one header, five tab-separated fields a row, sorted by path,
    each path once, hashes and commits in full."""
    if text is None:
        return []
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    else:
        raise ManifestError("does not end in a newline")
    if not lines or lines[0] != HEADER:
        raise ManifestError(f"line 1 is not the header {HEADER!r}")
    rows, prev = [], None
    for i, ln in enumerate(lines[1:], 2):
        f = ln.split("\t")
        if len(f) != 5:
            raise ManifestError(f"line {i} has {len(f)} fields, not 5")
        path, size, digest, commit, last = f
        if not path or path.startswith("/") or ".." in path.split("/"):
            raise ManifestError(f"line {i}: {path!r} is not a repository path")
        if not size.isdigit():
            raise ManifestError(f"line {i}: bytes {size!r} is not a count")
        if not HEX64.match(digest):
            raise ManifestError(f"line {i}: {digest!r} is not a SHA-256")
        if not HEX40.match(commit):
            raise ManifestError(f"line {i}: evidence_commit {commit!r} is not "
                                f"a full 40-character commit")
        if last and not HEX40.match(last):
            raise ManifestError(f"line {i}: last_default_commit {last!r} is "
                                f"neither empty nor a full commit")
        if prev is not None and path.encode() <= prev.encode():
            raise ManifestError(f"line {i}: {path!r} is "
                                + ("listed twice" if path == prev else
                                   f"out of order after {prev!r}"))
        rows.append(Row(path, int(size), digest, commit, last))
        prev = path
    return rows


def format_manifest(rows):
    rows = sorted(rows, key=lambda r: r.path.encode())
    body = "".join(f"{r.path}\t{r.size}\t{r.sha256}\t{r.commit}\t"
                   f"{r.last_default}\n" for r in rows)
    return HEADER + "\n" + body


def manifest_at(repo, rev):
    """The manifest at a commit, as rows; [] if that commit has none."""
    r = git(repo, "show", f"{rev}:{MANIFEST}")
    if r.returncode != 0:
        return []
    return parse_manifest(r.stdout.decode("utf-8"))


def run_folder(path):
    """The run folder a path is in (HR-2 5a moves whole ones), or None.

    `docs/rig-*/` is ours; a folder under `docs/handshake/inbound/artifacts/`
    is a copy of the other side's run. A loose file there is not a folder."""
    parts = path.split("/")
    if len(parts) >= 3 and parts[0] == "docs" and parts[1].startswith("rig-"):
        return "/".join(parts[:2])
    if len(parts) >= 6 and parts[:4] == ["docs", "handshake", "inbound",
                                         "artifacts"]:
        return "/".join(parts[:5])
    return None


def tree_folders(repo, rev="HEAD"):
    """Every run folder a commit holds, ENUMERATED: git ls-tree treats a
    pattern such as `docs/rig-*` literally, prints nothing and exits 0
    (HR-2 5b), so the list is read from the tree and never passed as one."""
    found = []
    for parent, test in (("docs", lambda n: n.startswith("rig-")),
                         ("docs/handshake/inbound/artifacts", lambda n: True)):
        r = git(repo, "ls-tree", "-d", "-z", "--name-only", f"{rev}:{parent}")
        if r.returncode != 0:
            continue
        for name in r.stdout.decode("utf-8").split("\0"):
            if name and test(name):
                found.append(f"{parent}/{name}")
    return sorted(found)


# --------------------------------------------------------------------------
# Where a file is

def git_dir(root):
    r = git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return pathlib.Path(out(r)) if r.returncode == 0 else None


def cache_path(root):
    if os.environ.get(CACHE_ENV):
        return pathlib.Path(os.environ[CACHE_ENV])
    d = git_dir(root)
    return d / "cyanrip-evidence.git" if d else None


def remote_url(root):
    if os.environ.get(URL_ENV):
        return os.environ[URL_ENV]
    r = git(root, "remote", "get-url", "origin")
    return out(r) if r.returncode == 0 else None


class Store:
    """Every evidence path this tree can name, and the bytes of each."""

    def __init__(self, root=ROOT, manifest=None):
        self.root = pathlib.Path(root)
        if manifest is None:
            p = self.root / MANIFEST
            manifest = p.read_text(encoding="utf-8") if p.exists() else None
        self.rows = {r.path: r for r in parse_manifest(manifest)}
        self.cache = cache_path(self.root)

    def moved(self):
        """True once this tree has a manifest, i.e. after the move."""
        return bool(self.rows)

    def in_tree(self, path):
        return (self.root / path).is_file()

    def files(self, prefix):
        """Every file under `prefix`, in this checkout or in the manifest."""
        prefix = prefix.rstrip("/") + "/"
        found = set()
        base = self.root / prefix
        if base.is_dir():
            for p in base.rglob("*"):
                if p.is_file():
                    found.add(p.relative_to(self.root).as_posix())
        found |= {p for p in self.rows if p.startswith(prefix)}
        return sorted(found)

    def folders(self):
        """Every run folder, in this checkout or in the manifest."""
        found = set()
        for parent in (self.root / "docs",
                       self.root / "docs/handshake/inbound/artifacts"):
            if parent.is_dir():
                for d in parent.iterdir():
                    rel = d.relative_to(self.root).as_posix()
                    if d.is_dir() and run_folder(rel + "/x") == rel:
                        found.add(rel)
        found |= {run_folder(p) for p in self.rows if run_folder(p)}
        return sorted(found)

    def _blob(self, repo, commit, path):
        if repo is None or not pathlib.Path(repo).exists():
            return None
        r = git(repo, "cat-file", "blob", f"{commit}:{path}")
        return r.stdout if r.returncode == 0 else None

    def where(self, path):
        """'tree', 'clone', 'cache', or None if nothing here holds it."""
        if self.in_tree(path):
            return "tree"
        row = self.rows.get(path)
        if row is None:
            return None
        if git(self.root, "cat-file", "-e",
               f"{row.commit}:{path}").returncode == 0:
            return "clone"
        if self.cache and self.cache.exists() and git(
                self.cache, "cat-file", "-e",
                f"{row.commit}:{path}").returncode == 0:
            return "cache"
        return None

    def read(self, path):
        """The file's bytes, checked against its row when read from git."""
        if self.in_tree(path):
            return (self.root / path).read_bytes()
        row = self.rows.get(path)
        if row is None:
            raise FileNotFoundError(f"{path} is not in this checkout and has "
                                    f"no row in {MANIFEST}")
        for repo in (self.root, self.cache):
            data = self._blob(repo, row.commit, path)
            if data is None:
                continue
            if len(data) != row.size or sha256(data) != row.sha256:
                raise Mismatch(f"{path} at {row.commit[:12]} is {len(data)} "
                               f"bytes, sha256 {sha256(data)[:16]}..., and its "
                               f"manifest row says {row.size} bytes, "
                               f"{row.sha256[:16]}...")
            return data
        raise NotFetched(f"{path} is on the evidence branch at "
                         f"{row.commit[:12]} and this clone has not fetched "
                         f"it: run tools/evidence.py fetch")

    def missing(self, paths):
        """The paths among `paths` this tree cannot read, without reading."""
        return [p for p in paths if self.where(p) is None]


def unprobed_or_fail(why):
    """What a check does about an unfetched file: exit 77, or fail in CI's
    evidence job, where every check that reads evidence must actually run."""
    if required():
        print(f"FAIL: {why} ({REQUIRED_ENV}=1: this job must hold evidence)")
        return 1
    print(f"UNPROBED: {why}")
    return UNPROBED


# --------------------------------------------------------------------------
# Fetching, into the cache and never into the working clone (HR-2 7)

def ensure_cache(store):
    if store.cache is None:
        raise RuntimeError("not a git checkout, so there is no evidence cache")
    if not (store.cache / "HEAD").exists():
        store.cache.mkdir(parents=True, exist_ok=True)
        git(store.cache, "init", "--bare", "-q", check=True)
    return store.cache


def fetch(store, commits, url=None, branch=False):
    """Fetch each commit by its hash, depth 1, into the cache. With branch,
    fetch the evidence branch itself too, which is what reachability needs."""
    cache = ensure_cache(store)
    url = url or remote_url(store.root)
    if not url:
        raise RuntimeError("no URL: this clone has no origin and "
                           f"{URL_ENV} is unset")
    if branch:
        git(cache, "fetch", "-q", "--no-tags", url,
            f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}", check=True)
    for c in sorted(set(commits)):
        if git(cache, "cat-file", "-e", f"{c}^{{commit}}").returncode == 0:
            continue
        git(cache, "fetch", "-q", "--no-tags", "--depth", "1", url, c,
            check=True)
    return cache


def evidence_tips(store):
    """(repo, tip) for each place that holds the evidence branch's tip."""
    tips = []
    for repo in (store.root, store.cache):
        if repo is None or not pathlib.Path(repo).exists():
            continue
        for ref in (f"refs/heads/{BRANCH}", f"refs/remotes/origin/{BRANCH}"):
            r = git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
            if r.returncode == 0:
                tips.append((repo, out(r)))
    return tips


def on_evidence(store, commit):
    """True or False when some repository here can tell; None when none can."""
    tips = evidence_tips(store)
    if not tips:
        return None
    for repo, tip in tips:
        if git(repo, "cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
            continue
        if git(repo, "merge-base", "--is-ancestor", commit, tip).returncode == 0:
            return True
    return False


# --------------------------------------------------------------------------
# An overlay: this checkout with evidence placed at its own paths

def _real_dir(dest, root, rel):
    """Make dest/rel a real directory whose entries mirror root/rel."""
    cur, src = dest, root
    for part in pathlib.PurePosixPath(rel).parts:
        cur, src = cur / part, src / part
        if cur.is_symlink():
            cur.unlink()
            cur.mkdir()
            if src.is_dir():
                for child in src.iterdir():
                    (cur / child.name).symlink_to(child)
        elif not cur.exists():
            cur.mkdir()


def overlay(store, paths, dest):
    """Fill `dest` with this checkout plus each path in `paths` the checkout
    lacks, read through the store. NotFetched propagates."""
    dest = pathlib.Path(dest)
    for child in store.root.iterdir():
        (dest / child.name).symlink_to(child)
    for p in sorted(paths):
        if store.in_tree(p):
            continue
        data = store.read(p)
        _real_dir(dest, store.root, str(pathlib.PurePosixPath(p).parent))
        target = dest / p
        if target.is_symlink():
            target.unlink()
        target.write_bytes(data)
    return dest


EVIDENCE_TOKEN = re.compile(
    r"docs/(?:rig-|handshake/inbound/artifacts/)[^\s\"'`|;<>()]*")


def folders_named(text, store):
    """The run folders a command or a line of code names, globs expanded
    against every folder this tree knows, in its checkout or its manifest."""
    import fnmatch
    known = store.folders()
    found = set()
    for token in EVIDENCE_TOKEN.findall(text):
        parts = token.rstrip(".,").split("/")
        depth = 2 if parts[1].startswith("rig-") else 5
        if len(parts) < depth:
            continue
        pattern = "/".join(parts[:depth])
        found |= {f for f in known if fnmatch.fnmatchcase(f, pattern)}
    return sorted(found)


def run_with_evidence(store, folders, argv, shell=False):
    """Run argv (or a shell string) where every file of `folders` is present.

    Before the move every file is in the checkout and this runs in place.
    Returns the command's exit status, or raises NotFetched."""
    need = [p for f in folders for p in store.files(f)]
    lacking = [p for p in need if not store.in_tree(p)]
    if not lacking:
        return subprocess.run(argv, cwd=store.root, shell=shell).returncode
    with tempfile.TemporaryDirectory(prefix="evidence-overlay-") as d:
        overlay(store, lacking, d)
        return subprocess.run(argv, cwd=d, shell=shell).returncode


# --------------------------------------------------------------------------
# Building and filing (HR-2 5b-5d, 10a)

def identity_env(date):
    env = dict(os.environ)
    for who in ("AUTHOR", "COMMITTER"):
        env[f"GIT_{who}_NAME"], env[f"GIT_{who}_EMAIL"] = IDENTITY
        env[f"GIT_{who}_DATE"] = date
    return env


def rows_for_tree(repo, rev, folders, commit, last_default):
    """One manifest row for every file the folders hold at rev."""
    rows = []
    r = git(repo, "ls-tree", "-r", "-z", "-l", rev, "--", *folders, check=True)
    for rec in r.stdout.decode("utf-8").split("\0"):
        if not rec:
            continue
        meta, path = rec.split("\t", 1)
        mode, kind, oid, size = meta.split()
        if kind != "blob":
            raise RuntimeError(f"{path} is a {kind}, not a file")
        if "\t" in path or "\n" in path:
            raise RuntimeError(f"{path!r} holds a tab or a newline and "
                               f"cannot be filed (HR-2 4)")
        data = git(repo, "cat-file", "blob", oid, check=True).stdout
        rows.append(Row(path, int(size), sha256(data), commit, last_default))
    return rows


def build_move(source, folders, date, push_url=None):
    """HR-2 5b-5d's first half: the move commit and its manifest rows.

    Built in a temporary `git clone --depth 1 --single-branch` of `source`, so
    a push from it sends trees and one commit and never the files themselves.
    Returns (commit, rows, last_default)."""
    with tempfile.TemporaryDirectory(prefix="evidence-build-") as d:
        tmp = pathlib.Path(d) / "clone"
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--single-branch",
                        "--branch", DEFAULT_BRANCH, source, str(tmp)],
                       check=True)
        last = out(git(tmp, "rev-parse", "HEAD", check=True))
        have = tree_folders(tmp)
        unknown = [f for f in folders if f not in have]
        if unknown:
            raise RuntimeError(f"not run folders at {last[:12]}: {unknown}")
        index = pathlib.Path(d) / "evidence.index"
        env = dict(os.environ, GIT_INDEX_FILE=str(index))
        git(tmp, "read-tree", "--empty", env=env, check=True)
        listing = git(tmp, "ls-tree", "-r", "-z", "HEAD", "--", *folders,
                      check=True).stdout
        git(tmp, "update-index", "-z", "--index-info", data=listing, env=env,
            check=True)
        tree = out(git(tmp, "write-tree", env=env, check=True))
        commit = out(git(tmp, "commit-tree", tree, "-m",
                         "evidence: move run evidence off the default branch",
                         env=identity_env(date), check=True))
        rows = rows_for_tree(tmp, commit, folders, commit, last)
        # 5d, before the push: the count and bytes match the rows.
        n = len(listing.split(b"\0")) - 1
        held = 0
        for rec in git(tmp, "ls-tree", "-r", "-l", "-z", commit,
                       check=True).stdout.decode("utf-8").split("\0"):
            if rec:
                held += int(rec.split("\t", 1)[0].split()[3])
        if n != len(rows) or held != sum(r.size for r in rows):
            raise RuntimeError(f"the commit holds {n} files, {held} bytes, and "
                               f"the rows say {len(rows)}, "
                               f"{sum(r.size for r in rows)}")
        if push_url:
            subprocess.run(["git", "-C", str(tmp), "-c", "push.negotiate=false",
                            "push", push_url,
                            f"{commit}:refs/heads/{BRANCH}"], check=True)
        return commit, rows, last


def file_run(store, staging, dest, date=None, push_url=None):
    """HR-2 10a: one new run as one evidence commit on the current tip.

    Returns (commit, rows). The rows' last_default_commit is empty: the files
    were filed straight to evidence."""
    staging = pathlib.Path(staging)
    if run_folder(dest.rstrip("/") + "/x") != dest.rstrip("/"):
        raise RuntimeError(f"{dest} is not a run folder path (docs/rig-NAME)")
    dest = dest.rstrip("/")
    url = push_url or remote_url(store.root)
    date = date or datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    with tempfile.TemporaryDirectory(prefix="evidence-file-") as d:
        tmp = pathlib.Path(d) / "clone"
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--single-branch",
                        "--branch", BRANCH, "--no-checkout", url, str(tmp)],
                       check=True)
        tip = out(git(tmp, "rev-parse", "HEAD", check=True))
        if git(tmp, "cat-file", "-e", f"HEAD:{dest}").returncode == 0:
            raise RuntimeError(f"{dest} is already on {BRANCH}: evidence only "
                               f"gains files (HR-2 3)")
        index = pathlib.Path(d) / "evidence.index"
        env = dict(os.environ, GIT_INDEX_FILE=str(index))
        git(tmp, "read-tree", "HEAD", env=env, check=True)
        for p in sorted(staging.rglob("*")):
            if not p.is_file():
                continue
            rel = f"{dest}/{p.relative_to(staging).as_posix()}"
            if "\t" in rel or "\n" in rel:
                raise RuntimeError(f"{rel!r} holds a tab or a newline")
            oid = out(git(tmp, "hash-object", "-w", str(p), check=True))
            git(tmp, "update-index", "--add", "--cacheinfo",
                f"100644,{oid},{rel}", env=env, check=True)
        tree = out(git(tmp, "write-tree", env=env, check=True))
        commit = out(git(tmp, "commit-tree", tree, "-p", tip, "-m",
                         f"evidence: file {dest}", env=identity_env(date),
                         check=True))
        rows = rows_for_tree(tmp, commit, [dest], commit, "")
        if push_url:
            subprocess.run(["git", "-C", str(tmp), "-c", "push.negotiate=false",
                            "push", push_url,
                            f"{commit}:refs/heads/{BRANCH}"], check=True)
        return commit, rows


def verify_move(store, evidence_commit, removal_commit):
    """HR-2 5d's second half, and HR-2.1 b's parent: the removal commit is
    built on the commit the evidence commit was built from. Returns a list of
    problems, empty when it holds."""
    problems = []
    rows = [r for r in store.rows.values() if r.commit == evidence_commit]
    if not rows:
        return [f"no manifest row names {evidence_commit}"]
    lasts = sorted({r.last_default for r in rows if r.last_default})
    parent = git(store.root, "rev-parse", "--verify", "-q",
                 f"{removal_commit}^")
    if len(lasts) != 1:
        problems.append(f"the rows naming {evidence_commit[:12]} name "
                        f"{len(lasts)} last default commits; a move is built "
                        f"from one (HR-2.1 b)")
    elif parent.returncode != 0 or out(parent) != lasts[0]:
        problems.append(f"{removal_commit[:12]}'s parent is "
                        f"{out(parent)[:12] or 'none'}, and the evidence "
                        f"commit was built from {lasts[0][:12]}: the removal's "
                        f"first commit has that as its parent (HR-2.1 b)")
    folders = sorted({run_folder(r.path) for r in rows if r.last_default})
    for f in folders:
        lasts = {r.last_default for r in rows if run_folder(r.path) == f}
        for last in sorted(lasts):
            a = git(store.root, "rev-parse", f"{last}:{f}")
            b = None
            for repo in (store.root, store.cache):
                if repo is not None and pathlib.Path(repo).exists():
                    r = git(repo, "rev-parse", f"{evidence_commit}:{f}")
                    if r.returncode == 0:
                        b = out(r)
                        break
            if a.returncode != 0 or b is None:
                raise NotFetched(f"{f}: cannot read its tree at "
                                 f"{last[:12]} or at {evidence_commit[:12]}")
            if out(a) != b:
                problems.append(f"{f}: tree {out(a)[:12]} at {last[:12]} is "
                                f"not {b[:12]} at {evidence_commit[:12]}")
    deleted = git(store.root, "diff", "--name-only", "-z", "--no-renames",
                  "--diff-filter=D", f"{removal_commit}^", removal_commit,
                  check=True).stdout.decode("utf-8").split("\0")
    for p in deleted:
        if p and p not in store.rows:
            problems.append(f"{p} is deleted by {removal_commit[:12]} and has "
                            f"no manifest row")
    return problems


def moved_folders_unchanged(store, base, current=None):
    """HR-2.1 b: before a removal merges, each folder it moves holds, on the
    default branch as it now stands, the tree it has at the evidence commit.
    If not, a file changed after the build, and the removal waits.

    A removal is told by its rows: those added since `base` that name a last
    default commit, where a filing's name none (HR-2 4). `current` is the
    default branch now, `base` when not given. Returns (problems, unfetched,
    checked), checked being the (folder, evidence commit) pairs compared."""
    old = {r.path for r in manifest_at(store.root, base)}
    added = [r for p, r in store.rows.items() if p not in old and r.last_default]
    problems, unfetched = [], []
    for r in added:
        if run_folder(r.path) is None:
            problems.append(f"{r.path} names a last default commit and is in "
                            f"no run folder; a move takes whole folders "
                            f"(HR-2 5a, HR-2.1 a)")
    pairs = sorted({(run_folder(r.path), r.commit) for r in added
                    if run_folder(r.path)})
    ref = current or base
    now = git(store.root, "rev-parse", "--verify", "-q", f"{ref}^{{commit}}")
    if now.returncode != 0:
        raise RuntimeError(f"{ref} is not a commit in this clone, so the "
                           f"default branch as it stands cannot be read")
    now = out(now)
    for folder, commit in pairs:
        theirs = None
        for repo in (store.root, store.cache):
            if repo is not None and pathlib.Path(repo).exists():
                r = git(repo, "rev-parse", "--verify", "-q",
                        f"{commit}:{folder}")
                if r.returncode == 0:
                    theirs = out(r)
                    break
        if theirs is None:
            unfetched.append(f"{folder} at {commit[:12]}")
            continue
        ours = git(store.root, "rev-parse", "--verify", "-q", f"{now}:{folder}")
        if ours.returncode != 0:
            problems.append(f"{folder} is not on the default branch at "
                            f"{now[:12]}, and {commit[:12]} holds it: it "
                            f"changed after the build, so the removal waits "
                            f"(HR-2.1 b)")
        elif out(ours) != theirs:
            problems.append(f"{folder}: tree {out(ours)[:12]} on the default "
                            f"branch at {now[:12]} is not {theirs[:12]} at "
                            f"{commit[:12]}: a file changed after the build, "
                            f"so the removal waits (HR-2.1 b)")
    return problems, unfetched, pairs


def verify_rows(store, base=None):
    """HR-2 8a: every manifest row (added since `base`) against its file at its
    commit, the commit on the evidence branch, and the manifest append-only.

    Returns (problems, unfetched)."""
    problems, unfetched = [], []
    old = {}
    if base:
        try:
            old = {r.path: r for r in manifest_at(store.root, base)}
        except ManifestError as e:
            problems.append(f"the manifest at {base} does not read: {e}")
    for p, r in old.items():
        if store.rows.get(p) != r:
            problems.append(f"{p}: its row at {base} was changed or removed; "
                            f"the manifest is append-only (HR-2 4)")
    added = [r for p, r in sorted(store.rows.items()) if p not in old]
    for r in added:
        try:
            if store.in_tree(r.path):
                data = store.root.joinpath(r.path).read_bytes()
                if len(data) != r.size or sha256(data) != r.sha256:
                    problems.append(f"{r.path}: this checkout's copy is not "
                                    f"the bytes its row names")
            data = None
            for repo in (store.root, store.cache):
                data = store._blob(repo, r.commit, r.path)
                if data is not None:
                    break
            if data is None:
                unfetched.append(r.path)
                continue
            if len(data) != r.size or sha256(data) != r.sha256:
                problems.append(f"{r.path}: {len(data)} bytes, "
                                f"{sha256(data)[:16]}... at {r.commit[:12]}, "
                                f"and its row says {r.size}, {r.sha256[:16]}...")
        except OSError as e:
            problems.append(f"{r.path}: {e}")
    for c in sorted({r.commit for r in added}):
        reach = on_evidence(store, c)
        if reach is False:
            problems.append(f"{c[:12]} is not reachable from {BRANCH}")
        elif reach is None and c not in unfetched:
            unfetched.append(f"the {BRANCH} branch, to check {c[:12]} is on it")
    return problems, unfetched


def check_tags(store):
    """HR-2 8a: no tag points at or reaches an evidence commit. Every commit
    on the branch reaches its root, so a tag that reaches any of them reaches
    the root. Returns problems, or None when no evidence tip is held."""
    tips = evidence_tips(store)
    if not tips:
        return None
    repo, tip = tips[0]
    roots = out(git(repo, "rev-list", "--max-parents=0", tip)).split()
    # The tags are in this clone, so the ancestry is asked here. A clone that
    # lacks the branch would answer "not an ancestor" to every tag, which is a
    # check satisfied by finding nothing.
    for root_commit in roots:
        if git(store.root, "cat-file", "-e",
               f"{root_commit}^{{commit}}").returncode != 0:
            raise NotFetched(f"{BRANCH} is not in this clone, where the tags "
                             f"are; fetch it here to check them")
    problems = []
    tags = out(git(store.root, "for-each-ref", "--format=%(refname)",
                   "refs/tags")).split()
    for t in tags:
        c = out(git(store.root, "rev-parse", f"{t}^{{commit}}"))
        for root_commit in roots:
            if git(store.root, "merge-base", "--is-ancestor", root_commit,
                   c).returncode == 0:
                problems.append(f"{t} reaches the {BRANCH} branch "
                                f"({root_commit[:12]})")
    return problems


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=pathlib.Path, default=ROOT)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("where")
    p.add_argument("paths", nargs="+")
    p = sub.add_parser("cat")
    p.add_argument("path")
    p = sub.add_parser("fetch")
    p.add_argument("--branch", action="store_true",
                   help=f"also fetch the {BRANCH} branch, for reachability")
    p.add_argument("--url")
    p = sub.add_parser("run")
    p.add_argument("--folder", action="append", default=[])
    p.add_argument("argv", nargs=argparse.REMAINDER)
    p = sub.add_parser("verify-rows")
    p.add_argument("--base")
    p.add_argument("--current", help="the default branch as it stands, for "
                   "HR-2.1 b's check of a removal (default: --base)")
    sub.add_parser("check-tags")
    p = sub.add_parser("build")
    p.add_argument("--folders", required=True, type=pathlib.Path,
                   help="a file naming each folder to move, one a line")
    p.add_argument("--date", required=True,
                   help="the instant round 33's lap 1 fixes (HR-2 5c)")
    p.add_argument("--source", help="what to clone (default: this checkout)")
    p.add_argument("--manifest-out", required=True, type=pathlib.Path)
    p.add_argument("--push", metavar="URL")
    p = sub.add_parser("verify-move")
    p.add_argument("evidence_commit")
    p.add_argument("removal_commit")
    p = sub.add_parser("file")
    p.add_argument("staging", type=pathlib.Path)
    p.add_argument("--as", dest="dest", required=True)
    p.add_argument("--date")
    p.add_argument("--push", metavar="URL")
    args = ap.parse_args()

    try:
        store = Store(args.root)
    except ManifestError as e:
        print(f"FAIL: {MANIFEST}: {e}")
        return 1

    try:
        if args.cmd == "where":
            for path in args.paths:
                print(f"{store.where(path) or 'NOT FETCHED'}\t{path}")
            return 0
        if args.cmd == "cat":
            sys.stdout.buffer.write(store.read(args.path))
            return 0
        if args.cmd == "fetch":
            commits = sorted({r.commit for r in store.rows.values()})
            if not commits and not args.branch:
                print(f"nothing to fetch: {MANIFEST} names no commit")
                return 0
            cache = fetch(store, commits, args.url, args.branch)
            print(f"fetched {len(commits)} commit(s) into {cache}")
            return 0
        if args.cmd == "run":
            argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
            if not argv:
                ap.error("run needs a command after --")
            return run_with_evidence(store, args.folder or store.folders(),
                                     argv)
        if args.cmd == "verify-rows":
            if args.current and not args.base:
                ap.error("--current needs --base: the rows a removal adds are "
                         "those since --base")
            problems, unfetched = verify_rows(store, args.base)
            moved = []
            if args.base:
                more, missing, moved = moved_folders_unchanged(
                    store, args.base, args.current)
                problems += more
                unfetched += missing
            for pr in problems:
                print(f"FAIL: {pr}")
            if problems:
                return 1
            if unfetched:
                return unprobed_or_fail(f"{len(unfetched)} row(s) not fetched,"
                                        f" first {unfetched[0]}")
            print(f"ok: {len(store.rows)} row(s) read cleanly"
                  + (f", those added since {args.base} checked against their "
                     f"files" if args.base else ", each checked against its "
                     f"file")
                  + (f"; {len(moved)} moved folder(s) the same on the default "
                     f"branch at {args.current or args.base} as at their "
                     f"evidence commit (HR-2.1 b)" if moved else ""))
            return 0
        if args.cmd == "check-tags":
            problems = check_tags(store)
            if problems is None:
                if store.moved():
                    return unprobed_or_fail(f"no {BRANCH} tip is held here")
                print(f"ok: no {BRANCH} branch yet, so no tag can reach it")
                return 0
            for pr in problems:
                print(f"FAIL: {pr}")
            if not problems:
                print(f"ok: no tag points at or reaches {BRANCH}")
            return 1 if problems else 0
        if args.cmd == "build":
            folders = [ln.strip() for ln in args.folders.read_text().splitlines()
                       if ln.strip() and not ln.startswith("#")]
            source = args.source or f"file://{store.root}"
            commit, rows, last = build_move(source, folders, args.date,
                                            args.push)
            args.manifest_out.write_text(format_manifest(rows), encoding="utf-8")
            print(f"commit {commit}: {len(rows)} file(s), "
                  f"{sum(r.size for r in rows)} bytes, from {len(folders)} "
                  f"folder(s) at {last}"
                  + (f"; pushed to {args.push}" if args.push else ""))
            return 0
        if args.cmd == "verify-move":
            problems = verify_move(store, args.evidence_commit,
                                   args.removal_commit)
            for pr in problems:
                print(f"FAIL: {pr}")
            if not problems:
                print("ok: every moved folder's tree matches, and every "
                      "deleted path has one row")
            return 1 if problems else 0
        if args.cmd == "file":
            commit, rows = file_run(store, args.staging, args.dest, args.date,
                                    args.push)
            merged = {**store.rows, **{r.path: r for r in rows}}
            (store.root / MANIFEST).write_text(format_manifest(merged.values()),
                                               encoding="utf-8")
            readme = args.staging / "README.md"
            if readme.is_file():
                target = store.root / args.dest.rstrip("/") / "README.md"
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(readme, target)
            print(f"commit {commit}: {len(rows)} file(s) under {args.dest}"
                  + (f", pushed to {args.push}" if args.push else
                     ", NOT pushed")
                  + f"; {len(rows)} row(s) added to {MANIFEST}")
            for r in rows:
                print(f"  cyanrip@{commit}:{r.path} sha256 {r.sha256}")
            return 0
    except NotFetched as e:
        return unprobed_or_fail(str(e))
    except (Mismatch, ManifestError, RuntimeError, FileNotFoundError,
            subprocess.CalledProcessError) as e:
        print(f"FAIL: {e}")
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
