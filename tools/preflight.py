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

"""Everything that must be true before an artifact leaves this repository.

WHY, and it is measured rather than felt. Seven things got past me in one
session. Classified by what caught each:

    a check that already existed .... 2   (the typed digest, the cut wire fields)
    reading output after an edit .... 3   (P2's %s, a legend parsed as data,
                                           a column count that dropped 15 to 11)
    the other side ................. 2   (an unhedged relay, a probe watching
                                           the wrong process)

**Every one has the same generating function: something changed and the thing
that would have said so was not re-run.** Not ignorance -- omission of a cheap
step. So the fix cannot be "be more careful", because care is exactly what
failed; it has to be that omission stops being possible.

WHAT THIS ADDS OVER `meson test`. The suite checks the program. This checks the
*handover*: that the tree is committed and pushed, and that an outbound lap's
quoted hashes and fetch URLs actually resolve. Round 14 lap 17 quotes two
SHA-256s and two raw URLs for the peer to fetch, and until this existed nothing
verified a single character of them -- a wrong one costs a lap, which is the
currency this whole session has been spending.

IT REFUSES TO BE PARTIALLY SATISFIED. A check that cannot run is a failure, not
a skip. "Could not verify" and "verified" must never share an exit code, which
is the same `none` versus `unknown (reason)` rule the log lines live by.

    tools/preflight.py                          # tree only
    tools/preflight.py docs/handshake/round-14-lap-17.md
"""

import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRANCH = "platterpus-fork"

SHA_LINE = re.compile(r"sha256\s*=\s*([0-9a-f]{64})")
RAW_URL = re.compile(r"https://github\.com/[^/\s]+/[^/\s]+/raw/([^/\s]+)/(\S+?)(?=[\s`)]|$)")

results = []


def check(ok, name, detail, fix=None):
    results.append((ok, name, detail, fix))


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)


def check_tree():
    dirty = run(["git", "status", "--porcelain"]).stdout.strip()
    check(not dirty, "tree/committed",
          "working tree clean" if not dirty
          else f"{len(dirty.splitlines())} uncommitted path(s)",
          fix="commit them. An artifact that quotes this tree describes a state "
              "nobody else can fetch.")

    r = run(["git", "log", "--oneline", f"origin/{BRANCH}..HEAD"])
    ahead = [l for l in r.stdout.splitlines() if l.strip()]
    check(not ahead, "tree/pushed",
          "nothing unpushed" if not ahead else f"{len(ahead)} unpushed commit(s)",
          fix=f"push to {BRANCH}. Every fetch URL in an outbound lap resolves "
              f"against the REMOTE, so an unpushed commit makes the lap's own "
              f"instructions fail for the reader and nobody else.")


def check_suite():
    r = run(["meson", "test", "-C", "build"])
    m = re.search(r"^Fail:\s+(\d+)", r.stdout, re.M)
    ok_m = re.search(r"^Ok:\s+(\d+)", r.stdout, re.M)
    if not m:
        check(False, "suite/ran", "could not read a Fail: count from meson",
              fix="a suite whose result cannot be read is not a passing suite. "
                  "Run `meson test -C build` and look.")
        return
    n = int(m.group(1))
    check(n == 0, "suite/green",
          f"{ok_m.group(1) if ok_m else '?'} passed, {n} failed",
          fix="fix them. Nothing leaves over a red suite.")


def check_lap(path):
    """The quoted hashes and fetch URLs in an outbound lap."""
    text = path.read_text(encoding="utf-8", errors="replace")

    # Every `sha256 = ...` next to a path we can resolve locally.
    quoted = SHA_LINE.findall(text)
    if not quoted:
        check(True, "lap/hashes", "no sha256 quoted")
    else:
        # Map each quoted hash to the nearest preceding path-looking token, so
        # a wrong pairing is caught rather than a wrong hash only.
        found = 0
        for m in SHA_LINE.finditer(text):
            window = text[max(0, m.start() - 400):m.start()]
            # The path usually arrives INSIDE the fetch URL a line above, so
            # take the repo-relative tail rather than the whole token. Without
            # this the candidate is `…/raw/platterpus-fork/docs/…`, which
            # resolves to nothing and made every hash silently unmatched --
            # reported as "0 of 2 matched", which reads like a missing file
            # rather than a broken parser.
            cands = re.findall(r"[\w./-]+\.(?:md|sh|py|txt)", window)
            local, rel = None, None
            for c in reversed(cands):
                for tail in (c, c[c.find("docs/"):] if "docs/" in c else c,
                             c.split("/")[-1]):
                    if tail and (ROOT / tail).exists():
                        local, rel = ROOT / tail, tail
                        break
                if local:
                    break
            if not local:
                continue
            paths = [rel]
            found += 1
            ours = hashlib.sha256(local.read_bytes()).hexdigest()
            if ours == m.group(1):
                check(True, "lap/hash", f"{rel}: matches")
                continue

            # STALE IS NOT WRONG, and conflating them is the same defect as a
            # bare em dash standing for three confidences. A lap is immutable
            # once sent; if the file moved afterwards, the lap was correct when
            # written and the reader needs a NEWER lap, not a correction. So ask
            # git whether the quoted hash was ever this file's content.
            was = run(["git", "log", "--format=%H", "--", rel]).stdout.split()
            historical = any(
                hashlib.sha256(run(["git", "show", f"{c}:{rel}"],
                                   ).stdout.encode()).hexdigest() == m.group(1)
                for c in was[:40])
            check(False, "lap/hash",
                  f"{rel}: quoted {m.group(1)[:16]}…, file is {ours[:16]}… — "
                  + ("STALE: that hash is an earlier revision of this file"
                     if historical else
                     "WRONG: that hash was never this file's content"),
                  fix=("the file moved after the lap was written. A sent lap is "
                       "immutable, so it was right when written -- carry the new "
                       "hash in the NEXT lap rather than correcting this one."
                       if historical else
                       "re-read the file and quote what it hashes to. A wrong "
                       "hash makes the reader's fetch check fail and costs a "
                       "lap to explain."))
        check(found > 0, "lap/hashes",
              f"{found} of {len(quoted)} quoted hash(es) matched to a local file",
              fix="a hash quoted beside no resolvable path cannot be checked by "
                  "anyone, including the reader. Name the file next to it.")

    # Every raw fetch URL must name a path that exists on the pushed branch.
    urls = RAW_URL.findall(text)
    if not urls:
        check(True, "lap/urls", "no fetch URL quoted")
    for branch, relpath in urls:
        r = run(["git", "cat-file", "-e", f"origin/{branch}:{relpath}"])
        check(r.returncode == 0, "lap/url",
              f"origin/{branch}:{relpath}",
              fix="the URL in the lap points at something the remote does not "
                  "have. Push it, or fix the path -- the reader gets a 404 and "
                  "reports it as a missing lap, which is the argument this "
                  "session already spent two rounds on.")

    r = run([sys.executable, "tools/seam-check.py", str(path)])
    check(r.returncode == 0, "lap/seam-check",
          "clean" if r.returncode == 0 else "findings against our own lap",
          fix="run `tools/seam-check.py` on it and read the FIX lines. Sending "
              "a lap that fails our own checker is how the peer learns our "
              "gate is decoration.")


def main():
    laps = [pathlib.Path(a) for a in sys.argv[1:]]

    check_tree()
    check_suite()
    for lap in laps:
        if not lap.exists():
            check(False, "lap/missing", str(lap), fix="name a file that exists.")
            continue
        check_lap(lap)

    width = max(len(n) for _, n, _, _ in results)
    bad = 0
    for ok, name, detail, fix in results:
        print(f"{'OK  ' if ok else 'FAIL'}  {name:<{width}}  {detail}")
        if not ok:
            bad += 1
            if fix:
                print(f"{'':<6}{'':<{width}}  FIX: {fix}")

    print(f"\n{len(results)} check(s), {bad} failed"
          + ("" if laps else "  (no lap named -- tree checks only)"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
