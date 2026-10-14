#!/usr/bin/env python3
"""The GitHub Actions workflows keep the hardening of 2026-10-12.

Actions had never run on this fork, so nothing would notice a workflow
regressing until it ran with a write token. Each property here is one the
outside read of 2026-10-12 asked for, checked on the files rather than on a run:

  * the workflow token is read-only by default, and `contents: write` is held
    only by the jobs named in WRITERS;
  * every job has `timeout-minutes`;
  * every action is pinned to a full commit SHA, with its version in a comment;
  * no `::set-output`, and no actions/upload-release-asset (archived);
  * upstream's nightly steps run only in cyanreg/cyanrip;
  * no `${{ }}` expression is pasted into a shell script, where a branch name
    or an input would be executed rather than read;
  * the push and pull_request triggers name platterpus-fork and not master;
  * there is no `.github/workflows/main.yml`, the path upstream's own file has
    on master: GitHub keys a workflow by path, so a file of ours there would be
    the same workflow as upstream's again and could not be disabled alone.

It reads the files line by line rather than with a YAML parser, which would be
a dependency for one test; every count it relies on is asserted, so a pattern
that stops matching fails instead of passing on nothing.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WF = ROOT / ".github" / "workflows"
WRITERS = {("ci.yml", "mingw-release"), ("ci.yml", "mingw-nightly"),
           ("tag-release.yml", "tag")}
UPSTREAM_ONLY = ("WebFreak001/deploy-nightly", "mknejp/delete-release-assets")
PIN = re.compile(r"^\s*(?:- )?uses:\s*([\w.-]+/[\w./-]+)@([0-9a-f]{40})"
                 r"\s+#\s*v\S+\s*$")
failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


def jobs(lines):
    """{job name: [lines]} for the jobs under the top-level `jobs:` key."""
    out, cur, inside = {}, None, False
    for line in lines:
        if re.match(r"^\S", line):
            inside = line.rstrip() == "jobs:"
            cur = None
            continue
        m = re.match(r"^  ([\w-]+):\s*$", line)
        if inside and m:
            cur = m.group(1)
            out[cur] = []
        elif inside and cur:
            out[cur].append(line)
    return out


def top_block(lines, key):
    """The lines indented under a top-level KEY, or None if it is absent."""
    for i, line in enumerate(lines):
        if line.rstrip() == f"{key}:":
            body = []
            for nxt in lines[i + 1:]:
                if re.match(r"^\S", nxt):
                    break
                if nxt.strip() and not nxt.strip().startswith("#"):
                    body.append(nxt.strip())
            return body
    return None


def run_blocks(lines):
    """Each `run:` script, as (first line number, text)."""
    out = []
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*)(?:- )?run:\s*(.*)$", line)
        if not m:
            continue
        indent, rest = len(m.group(1)), m.group(2)
        body = [rest] if rest not in ("|", ">") else []
        for nxt in lines[i + 1:]:
            if nxt.strip() and len(nxt) - len(nxt.lstrip()) <= indent:
                break
            body.append(nxt)
        out.append((i + 1, "\n".join(body)))
    return out


files = sorted(WF.glob("*.yml")) + sorted(WF.glob("*.yaml"))
names = [p.name for p in files]
if "ci.yml" not in names or "tag-release.yml" not in names:
    fail(f"expected ci.yml and tag-release.yml in .github/workflows, "
         f"found {names}")
if (WF / "main.yml").exists():
    fail(".github/workflows/main.yml exists: that is the path upstream's own "
         "workflow has on master, so GitHub would treat ours and theirs as "
         "one workflow again")

pins = writers = 0
for p in files:
    lines = p.read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines)
    perm = top_block(lines, "permissions")
    if perm != ["contents: read"]:
        fail(f"{p.name}: top-level permissions are {perm}, "
             "not exactly `contents: read`")
    if "::set-output" in text:
        fail(f"{p.name}: uses ::set-output; write to $GITHUB_OUTPUT")
    if "upload-release-asset" in text:
        fail(f"{p.name}: uses actions/upload-release-asset, which is archived")
    for n, line in enumerate(lines, 1):
        if re.match(r"^\s*(?:- )?uses:", line):
            m = PIN.match(line)
            if m:
                pins += 1
            else:
                fail(f"{p.name}:{n}: not pinned to a full commit SHA with its "
                     f"version in a comment: {line.strip()}")
    for n, body in run_blocks(lines):
        if "${{" in body:
            fail(f"{p.name}:{n}: a ${{{{ }}}} expression inside a run script; "
                 "pass it through env: instead")
    found = jobs(lines)
    if not found:
        fail(f"{p.name}: no jobs found under `jobs:`")
    for job, body in found.items():
        block = "\n".join(body)
        if not re.search(r"^    timeout-minutes:\s*\d+\s*$", block, re.M):
            fail(f"{p.name}: job {job} has no timeout-minutes")
        if re.search(r"^\s+contents:\s*write\s*$", block, re.M):
            writers += 1
            if (p.name, job) not in WRITERS:
                fail(f"{p.name}: job {job} holds contents: write and is not "
                     "one of the jobs allowed to")
        if any(a in block for a in UPSTREAM_ONLY):
            cond = re.search(r"^    if:\s*(.+)$", block, re.M)
            if not cond or ("github.repository == 'cyanreg/cyanrip'"
                            not in cond.group(1)):
                fail(f"{p.name}: job {job} runs upstream's nightly steps "
                     "without `if: github.repository == 'cyanreg/cyanrip'`")

if pins < 5:
    fail(f"only {pins} pinned actions found; the pattern has stopped matching")
if writers != len(WRITERS):
    fail(f"{writers} jobs hold contents: write, expected {len(WRITERS)}")

ci = (WF / "ci.yml").read_text(encoding="utf-8") if (WF / "ci.yml").exists() \
    else ""
for event in ("push", "pull_request"):
    m = re.search(rf"^  {event}:\n(?:\s+#.*\n)*\s+branches:\s*\[([^\]]*)\]",
                  ci, re.M)
    got = [b.strip() for b in m.group(1).split(",")] if m else None
    if got != ["platterpus-fork"]:
        fail(f"ci.yml: the {event} trigger names {got}, not [platterpus-fork]")

tag = (WF / "tag-release.yml").read_text(encoding="utf-8") \
    if (WF / "tag-release.yml").exists() else ""
if "tools/tag-release-check.py" not in tag:
    fail("tag-release.yml does not run tools/tag-release-check.py")
if re.search(r"git push[^\n]*(--force|\s-f\b|\+refs/)", tag):
    fail("tag-release.yml force-pushes a tag")

# HR-2 (PROTOCOL.md v9 §17), point 8: every job fetches only what it reads,
# by explicit refspec, and exactly one fetches the evidence branch, the job
# that runs every check reading run evidence.
evidence_jobs = []
for p in files:
    text = p.read_text(encoding="utf-8")
    if re.search(r"^\s*fetch-depth:\s*0\s*$", text, re.M):
        fail(f"{p.name}: fetch-depth: 0 fetches every branch and every tag, "
             "the evidence branch among them; fetch by refspec with "
             ".github/fetch-history.sh (HR-2 8b)")
    for job, body in jobs(text.splitlines()).items():
        block = "\n".join(ln for ln in body if not ln.lstrip().startswith("#"))
        if "--evidence" in block or "refs/heads/evidence" in block:
            evidence_jobs.append(f"{p.name}:{job}")
if evidence_jobs != ["ci.yml:evidence"]:
    fail(f"the jobs that fetch the evidence branch are {evidence_jobs}; HR-2 "
         "8a says exactly one, ci.yml's evidence job")
ci_jobs = jobs(ci.splitlines())
for job in ("linux", "macos"):
    cond = re.search(r"^    if:\s*(.+)$", "\n".join(ci_jobs.get(job, [])), re.M)
    if not cond or "github.event_name != 'release'" not in cond.group(1):
        fail(f"ci.yml: job {job} re-runs on a release event, on a commit its "
             "push already tested; give it `if: github.event_name != "
             "'release'`")
rel = "\n".join(ci_jobs.get("mingw-release", []))
if "merge-base --is-ancestor" not in rel or "origin/platterpus-fork" not in rel:
    fail("ci.yml: mingw-release attaches a binary without checking that the "
         "released commit is on platterpus-fork")
# Comments left out: a step named in a comment is not a step that runs.
ev = "\n".join(ln for ln in ci_jobs.get("evidence", [])
               if not ln.lstrip().startswith("#"))
# --current is HR-2.1 b: a removal's folders compared with the evidence commit
# on the default branch as it stands, before the removal merges.
for need in ("CYANRIP_EVIDENCE_REQUIRED", "verify-rows", "--current",
             "check-tags", "'Settled facts'",
             "cache_table_matches_the_transcripts", "filed_rig_is_mappable",
             "'No personal details in new evidence'"):
    if need not in ev:
        fail(f"ci.yml: the evidence job does not run {need}")

if failures:
    print(f"{failures} failure(s)")
    sys.exit(1)
print(f"ok: {len(files)} workflows, {pins} pinned actions, "
      f"{writers} jobs with contents: write")
