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
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import redact  # noqa: E402

THIS = "tests/personal_details.py"


def git(*args):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                       text=True)
    return r.stdout if r.returncode == 0 else None


def in_scope(path):
    p = pathlib.PurePosixPath(path)
    if p.parts[:2] == ("docs", "handshake"):
        return len(p.parts) == 3   # not inbound/ or any other subdirectory
    return len(p.parts) >= 3 and p.parts[0] == "docs" and \
        p.parts[1].startswith("rig-")


def main():
    if git("rev-parse", "--is-inside-work-tree") is None:
        print("SKIP: not a git checkout, so a new file cannot be told from an "
              "old one, and nothing was checked")
        return 77
    added = (git("log", "--diff-filter=A", "--format=%H", "--", THIS) or "")
    added = added.split()
    if not added:
        # This file is not committed yet: everything committed is history,
        # and the working tree's new files are what is being added.
        before = set((git("ls-files") or "").split("\n"))
        candidates = set((git("ls-files", "--others", "--exclude-standard")
                          or "").split("\n")) | set(
            (git("diff", "--name-only", "--diff-filter=A", "HEAD") or "").split("\n"))
    else:
        tree = git("ls-tree", "-r", "--name-only", added[-1] + "^")
        if tree is None:
            print(f"SKIP: the parent of {added[-1][:12]}, which added {THIS}, "
                  f"is not in this clone, so a new file cannot be told from "
                  f"an old one, and nothing was checked")
            return 77
        before = set(tree.split("\n"))
        candidates = set((git("ls-files") or "").split("\n"))
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
