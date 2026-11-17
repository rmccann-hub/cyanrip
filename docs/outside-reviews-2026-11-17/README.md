# Outside reviews of the fork, archived 2026-11-17

**What this is.** These are the reviews of this fork that the claude-code-skills session
wrote outside this repository, with the evidence they cite. That session filed them in the
owner's company audit repository. On 2026-11-17 the owner asked for them to live here, and
another session carried them to the branch `claude/outside-reviews-import`. That branch
held them at `87108765`: 96 files under `docs/incoming/outside-reviews-2026-11-17/`, two
commits on `platterpus-fork`'s `8b33a6c1`. The owner chose that day to archive all of them
on the evidence branch.

**Where each file is.** Everything that branch carried is under `imported/` at the same
relative path, the carrier's own `README.md` included:

- `imported/cyanrip/2026-10-27/`: the audit of 2026-10-27, its C-language companion, and
  the checks, reviews, answers and skill feedback that followed it.
- `imported/cyanrip/2026-11-17/`: the end-user UX review of 2026-11-17, and under
  `evidence/` the image rips, terminal captures, cue sheets and four screenshots it cites.
- `imported/audit-log/`: the audit log, with its instructions and verification keys
  (`kit/`), the messages sent to both repositories' sessions (`kit/messages/`), research of
  2026-11-03 and the week review of 2026-11-10 (`research/`), lessons, a proposal, and
  follow-ups.

**What was changed.** Every file is byte for byte as the branch carried it except nine
lines in eight files, changed by `tools/redact.py` as every filed file is, under the
owner's rule of 2026-10-12. Five home-folder paths became `~`, in
`audit-log/kit/audit/verify-cyanrip.md`, `audit-log/kit/audit/verify-platterpus.md`,
`audit-log/research/2026-11-03/repo-state-2026-11-03.md` (two) and
`cyanrip/2026-10-27/CHECK-2026-10-27.md`. Four lines that name the AcoustID key option have
what follows the option replaced by `[withheld]`: `audit-log/kit/messages/FORK-NEXT-MESSAGE-2.md`
line 8, `cyanrip/2026-10-27/ANSWERS-CHECK-2-2026-10-27.md` line 14,
`cyanrip/2026-10-27/AUDIT-2026-10-27.md` line 528 and
`cyanrip/2026-11-17/UX-REVIEW-2026-11-17.md` line 303. None of those four held a key. Each
names the option in prose, so one sentence lost its following word: line 528 read
`included;` after the option. No hostname, real name, email address or company name or
domain is in any of the 96, checked before filing. The only account name is `rmccann-hub`,
in repository addresses, as in every lap. The screenshots show a bare `$` prompt and
relative paths.

**What this repository has done with them.**

- **The UX review of 2026-11-17** is triaged and filed in `docs/history/UX-REVIEW-2026-11-17.md`,
  from the copy uploaded to this session. The copy here is the reviewer's own. Where the
  filed one opens with a header for this repository and cites its evidence in the audit
  repository, this one cites the reviewer's scratch folders, and it ends with a section,
  *Lessons for our skills*, that the filed one lacks. Its fixes are
  `docs/OPEN-ITEMS.md` US-31 and US-32: four shipped in `.35`, and round 42 is to
  propose others.
- **The reviews of 2026-10-27** were read here in October, on the operator's word. The
  Changelog's *Review C's first section* and *The operator's follow-ups to review C*
  carry their fixes, as does the CI mirror timeout.
- **The week review of 2026-11-10 and the rest of the audit log** are archived here unread
  by this repository's session. Reading them is open, not done.

Nothing on the default branch reads these files (HR-2 1). `tools/evidence.py` is the one
way to fetch them.
