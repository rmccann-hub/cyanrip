#!/usr/bin/env python3
"""No lap or evidence committed from the owner's rule on carries a home path,
a hostname, or the owner's name.

The rule, 2026-10-12: "keep personal details out of anything newly committed
... Apply this to new evidence and laps, through the export or filing tools
rather than by hand ... History stays as it is." tests/redaction.py checks
the tools; this checks what was committed, because a lap is written by hand
and a bundle can be filed some other way.

WHAT IS NEW is derived, not listed: a file under the scope below that did not
exist before the commit adding THIS file. Everything older is history, and
the rule leaves it as it is. No cutoff SHA is written here, since a commit
cannot name itself; git answers it. Without that commit's parent -- a
tarball build, or a shallow clone cut at or after it, where the oldest commit
seems to add every file -- the check cannot tell new from old, and it says so
and skips (exit 77) rather than pass over files it did not judge.

SCOPE: our laps and standing status under docs/handshake/, and rig evidence
under docs/rig-*/. NOT docs/handshake/inbound/: those are Platterpus's sent
laps, filed byte-exact so their quoted hashes still verify, and editing one
is what the protocol forbids; their side keeps the rule for what they write.
A `HANDSHAKE-` line is a wire value and is skipped (tools/redact.py).

Hostnames are found as tools/redact.py finds them, in the file itself; a
list of the owner's would be the thing the rule forbids. The owner's name is
checked only from the local list outside the repository, and without one the
run says it was not checked.

WITH --evidence it checks what HR-2 files straight to the evidence branch
(PROTOCOL.md v9 §17): every docs/evidence-manifest.tsv row with no default
commit, read through tools/evidence.py. Those files never pass through this
checkout, so the check on them runs where they are fetched, which is CI's
evidence job; elsewhere it says it could not run (77). Files moved there from
this branch were committed here first, and are history.
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import redact  # noqa: E402
import evidence  # noqa: E402

THIS = "tests/personal_details.py"


def git(*args):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                       text=True, encoding="utf-8")
    return r.stdout if r.returncode == 0 else None


def in_scope(path):
    p = pathlib.PurePosixPath(path)
    if p.parts[:2] == ("docs", "handshake"):
        return len(p.parts) == 3   # not inbound/ or any other subdirectory
    return len(p.parts) >= 3 and p.parts[0] == "docs" and \
        p.parts[1].startswith("rig-")


def check_evidence():
    store = evidence.Store(ROOT)
    rows = [r for r in store.rows.values() if not r.last_default]
    names = redact.local_names()
    problems = unfetched = 0
    for r in rows:
        try:
            data = store.read(r.path)
        except evidence.NotFetched:
            unfetched += 1
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for line, kind in redact.findings(text, names):
            problems += 1
            print(f"FAIL: {r.path}:{line} (evidence {r.commit[:12]}): {kind}")
    print(f"{len(rows) - unfetched} of {len(rows)} file(s) filed straight to "
          f"evidence checked for home paths and hostnames"
          + ("" if names is not None else
             "; THE OWNER'S NAME WAS NOT CHECKED (no local list at "
             f"${redact.NAMES_ENV} or {redact.NAMES_FILE})"))
    if problems:
        return 1
    if unfetched:
        return evidence.unprobed_or_fail(f"{unfetched} file(s) not fetched")
    return 0


def main():
    if "--evidence" in sys.argv[1:]:
        return check_evidence()
    if git("rev-parse", "--is-inside-work-tree") is None:
        print("SKIP: not a git checkout, so a new file cannot be told from an "
              "old one, and nothing was checked")
        return 77
    # Every path list is read with -z. Without it git quotes a path holding a
    # byte above 0x7f -- `full acceptance∶ angle‹bracket` -- and a quoted path
    # starts with `"`, fails in_scope(), and is skipped without a word: eight
    # files of the 2026-10-13 bundle went unchecked that way.
    added = (git("log", "--diff-filter=A", "--format=%H", "--", THIS) or "")
    added = added.split()
    if not added:
        # This file is not committed yet: everything committed is history,
        # and the working tree's new files are what is being added.
        before = set((git("ls-files", "-z") or "").split("\0"))
        candidates = set((git("ls-files", "-z", "--others", "--exclude-standard")
                          or "").split("\0")) | set(
            (git("diff", "-z", "--name-only", "--diff-filter=A", "HEAD")
             or "").split("\0"))
    else:
        tree = git("ls-tree", "-r", "-z", "--name-only", added[-1] + "^")
        if tree is None:
            print(f"SKIP: the parent of {added[-1][:12]}, which added {THIS}, "
                  f"is not in this clone, so a new file cannot be told from "
                  f"an old one, and nothing was checked")
            return 77
        before = set(tree.split("\0"))
        candidates = set((git("ls-files", "-z") or "").split("\0"))
    new = sorted(p for p in candidates
                 if p and p not in before and in_scope(p))

    names = redact.local_names()
    problems = 0
    for path in new:
        f = ROOT / path
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line, kind in redact.findings(text, names):
            problems += 1
            print(f"FAIL: {path}:{line}: {kind}. Committed after the owner's "
                  f"rule of 2026-10-12; file it through tools/ingest-bundle.py, "
                  f"or write ~ / host in a lap")
    print(f"{len(new)} lap or evidence file(s) committed since the rule, "
          f"checked for home paths and hostnames"
          + ("" if names is not None else
             "; THE OWNER'S NAME WAS NOT CHECKED (no local list at "
             f"${redact.NAMES_ENV} or {redact.NAMES_FILE})"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
