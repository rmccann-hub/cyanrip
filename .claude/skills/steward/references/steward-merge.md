# Steward merge

Read this when a pull request here is green and ready to merge: the reads before the merge, the
merge itself, and the cleanup, report and check-ins around it.

It covers merging into `platterpus-fork`. Deciding green is `steward-checks`'s; a lap the merge
sends follows the handshake README's *Releasing our lap*, and a release its *Cutting a
release*, which this module names and does not restate.

## Rules

1. **Merge only on the owner's word** in the session, given for this pull request or a standing
   word whose scope covers it, and quote it with its date in the report (`SKILL.md`, *What this
   skill cannot do*).
2. **Merge only a green head:** all ten jobs passed at the head commit (`steward-checks`),
   `mergeable_state` `clean`, every review thread answered, and no push since the checks were
   read.
3. **Read Platterpus's record first.** In their clone, `git fetch origin main`, then list
   `docs/handshake/outbound/` at `origin/main`: a lap of theirs newer than the last one filed
   here, released to us, is taken in first (`tools/take-in-lap.py`), since a merge that sends a
   lap of ours must answer theirs. Then `python3 tools/seam-sync-check.py --fetch`: exit 0, or 1
   only for a shared document our last sent lap declares different in its
   `HANDSHAKE-SHARED-HASHES-SOURCE`. Any other difference stops the merge until it is resolved.
4. **A pull request carrying our lap** is merged as the README's *Releasing our lap* says: under
   a standing release word the lap is sent when the pull request merges green, so their `main`
   is read again just before.
5. **Merge with a merge commit, pinned to the head you checked:**

   ```sh
   gh api -X PUT repos/rmccann-hub/cyanrip/pulls/<n>/merge \
       -f merge_method=merge -f sha=<head you checked> \
       -f commit_title="Merge pull request #<n> from rmccann-hub/<branch>" \
       -f commit_message="<the pull request's title>"
   ```

   The `sha` makes GitHub refuse the merge if anything was pushed after the read. Squash and
   rebase merges are off here (fact `steward-merge-methods`), and would orphan commits a lap or
   a Changelog cites.
6. **Confirm on the remote:** `git ls-remote origin refs/heads/platterpus-fork` names the merge
   commit the call returned. A cache, such as `git branch -r`, is not the remote.
7. **Clean up after the merge.** GitHub deletes the pull request's branch when it merges (fact
   `steward-merge-settings`); a session cannot delete a branch itself (fact
   `steward-branch-delete`). Never push that branch name again for this pull request: later work
   restarts the designated branch from `platterpus-fork` and opens a new pull request. Then
   delete the local branch, unsubscribe from the pull request's activity, delete the check-in
   scheduled for it, and update the task list.
8. **Report it** with the merge commit, what it carried, the time in US Eastern with the zone
   and UTC, and the owner's word that covered it. End with the handoff block when the merge sent
   a lap, published a release, or merged anything Platterpus needs; otherwise `HANDOFF: none`
   (`CLAUDE.md`, *The operator, and Platterpus*).
9. **Keep one check-in while a pull request waits** on CI or reviewers: one about 50 minutes
   after the last activity, and its message self-contained, naming the pull request, its head,
   what to read and what to do on each outcome, because it fires into a context that may have
   been summarized. Delete it once the pull request merges or closes.
10. **A merged pull request is finished.** Follow-up work is a new pull request from a branch
    restarted at `platterpus-fork`; never stack commits on a merged branch.

## Mistakes

- **Merging a head nobody read.** A push after the check read is merged unseen unless the merge
  names the head's SHA.
- **Merging with a newer lap of theirs unread.** The seam can move under the merge; read their
  `main` first, every time.
- **Squash-merging.** In round 23 a squash merge, and the branch's deletion four minutes later,
  orphaned both commits the round's citations named, one of them in a lap already sent (the
  handshake README's round table). Squash merges are off here.
- **Pushing the branch again after its merge.** GitHub deleted it; a push recreates it with a
  stale tip that looks current.
- **Leaving the check-in armed.** It fires into the session after the merge and re-reads a closed
  pull request.
- **Forgetting the handoff.** The operator relays it to Platterpus; without it a sent lap goes
  unread until their next look.
- **Citing a setting only a credential can read.** The repository API shows
  `delete_branch_on_merge` and the merge methods only to a caller with write access. On
  2026-11-03 this module's fact quoted that API, `--verify` passed through the session's
  authenticated proxy, and the weekly job's first run, with no credentials, failed it. Such a
  setting is recorded in the handshake README and cited there.

## Audit

Severity uses the standard's status words.

| Check | What to look for | Severity | Fix |
|---|---|---|---|
| Authority | the report quotes the owner's word that covered the merge | fail | ask, and merge after |
| Head pinned | the merge call passed the head SHA that was checked | warn | pass it next time; confirm what merged |
| Their record read | their `main` and the seam check read just before the merge | fail | read them; take in a newer lap first |
| Merge commit | `git log -1 --format=%P <merge>` shows two parents | fail | none after the fact: report it |
| Remote confirmed | `git ls-remote` names the merge commit | warn | read it |
| Cleanup | local branch gone, unsubscribed, check-in deleted | info | do it |
| Handoff | a block when Platterpus needs the merge, `HANDOFF: none` otherwise | warn | give it |

## Why

### Read their record before every merge

- **The advice:** fetch Platterpus's `main` and run the seam check just before merging.
- **The reason:** a lap of ours is sent by the merge; one that misses a newer lap of theirs, or
  ships under a different rulebook, is wrong the moment it lands (`CLAUDE.md`, *The Platterpus
  seam*).
- **What others do, and why:** most projects have no peer to read; this one has a contract with
  one.
- **What it costs:** a fetch and a check, seconds.
- **When to choose differently:** never for a merge that sends a lap; for one that touches
  nothing the seam covers, it is still the turn's required read.

### Pin the merge to the checked head

- **The advice:** pass `sha=` with the merge call.
- **The reason:** the read and the merge are separate calls, and a push can land between them.
- **What others do, and why:** merge queues re-test what they merge; this repository has none.
- **What it costs:** nothing.
- **When to choose differently:** never.

## Facts

Versions, dates and defaults, each named elsewhere in this module by its ID. Checked
2026-11-03.

| ID | Fact | Source | Quote | Checked | Check by |
|---|---|---|---|---|---|
| `steward-merge-settings` | GitHub deletes a pull request's head branch when it merges, by the repository's setting | [the handshake README](https://raw.githubusercontent.com/rmccann-hub/cyanrip/platterpus-fork/docs/handshake/README.md) | "(the repository's `delete_branch_on_merge`, read" | 2026-11-03 | 2027-02-03 |
| `steward-merge-methods` | Only merge commits are allowed: squash and rebase merging are off | [the handshake README](https://raw.githubusercontent.com/rmccann-hub/cyanrip/platterpus-fork/docs/handshake/README.md) | "squash and rebase merging are off" | 2026-11-03 | 2027-02-03 |
| `steward-branch-delete` | A session cannot delete a branch: the git proxy answers HTTP 403 | [the handshake README](https://raw.githubusercontent.com/rmccann-hub/cyanrip/platterpus-fork/docs/handshake/README.md) | "branch delete is `HTTP 403` from" | 2026-11-03 | 2027-02-03 |

## Sources

Every source, with its license and how this module uses it: quoted, adapted with a notice, or
stated in our own words with a link.

| Source | Used for | License |
|---|---|---|
| [`docs/handshake/README.md`](https://github.com/rmccann-hub/cyanrip/blob/platterpus-fork/docs/handshake/README.md) | releasing a lap in its pull request, branches on the remote, round 23's squash, named and quoted | LGPL-2.1-or-later, this repository's |
| [`CLAUDE.md`](https://github.com/rmccann-hub/cyanrip/blob/platterpus-fork/CLAUDE.md) | the handoff block, the reads of Platterpus, branches and merges, named | LGPL-2.1-or-later, this repository's |
| [GitHub REST API, merge a pull request](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request) | the merge call and its `sha` parameter, in our own words | CC BY 4.0 |
| [GitHub REST API, repositories](https://docs.github.com/en/rest/repos/repos) | the merge settings, read with write access and recorded in the handshake README, since an unauthenticated read does not show them; in our own words | CC BY 4.0 |
