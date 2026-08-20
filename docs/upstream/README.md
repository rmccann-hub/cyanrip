# `docs/upstream/` — the fork, explained to upstream

**Audience: whoever maintains `cyanreg/cyanrip`, and anyone deciding whether to
pull an upstream change into this fork.**

`Changelog.md` at the repository root is unchanged in role: it is our releases,
by version, for people installing this fork. It is deliberately terse about
upstream.

This directory is the other half — **the full shape and the reasoning**. What
this fork changed relative to upstream and why, what upstream changed that we
have not taken and why, and what each sync would cost. `Changelog.md` links
here rather than growing a second voice inside itself.

## What is here

| file | what it is |
|---|---|
| `sync-YYYY-MM-DD-<upstream version>.md` | one per upstream sync analysis: what an inbound merge would bring, what it collides with, and the verdict |

Each sync file is written when `master` moves and **before** anything is merged
into `platterpus-fork`. It is a decision record, not a report of work done, so
a file saying *"we did not take this, here is why"* is a complete and expected
entry.

## How the two branches relate

- **`master`** is a clean mirror of `cyanreg/cyanrip`. Never committed to. It
  exists so we can *see* what upstream is doing.
- **`platterpus-fork`** is the only ref anything is built or installed from.

Syncing `master` never touches `platterpus-fork`; they diverged at `958e1ad`
and every consumer-facing reference resolves to a commit SHA, never to a branch.
So keeping `master` current is free, and is what makes these analyses possible.

## Regenerating the facts

```
tools/upstream-delta.py --fork-binary <fork build>/src/cyanrip \
                        --upstream-binary <upstream build>/src/cyanrip
```

It reports versions, inbound commits, files, **CLI flags measured from both
binaries' `--help`**, log-line inventories from both trees, and dependency
deltas. It judges nothing — whether a difference is a collision, a gap or a
non-event is a human call and lives in the sync file.

Build the upstream side with a worktree, so nothing on the fork branch moves:

```
git worktree add --detach /tmp/up master
meson setup /tmp/up/b -C /tmp/up && ninja -C /tmp/up/b
```

## Why this exists at all

Upstream changes reach this fork's consumer without touching a line of our
code, and twice they have broken it:

- **`-V` became `-v`** when getopt was replaced with genopt after 0.9.3. Every
  caller probing for the version with `-V` got exit 1 and
  *"Unable to parse command line argument"*, which reads to a user as *"cyanrip
  is not installed"*. This fork restores `-V` as an alias.
- **`Total time:` changed from `HH:MM:SS.mmm` to `MM:SS.FF`** — CD frames, no
  hours field, minutes that can exceed 59 — when upstream PR #130 merged.

Neither was a bug. Neither was visible to a *"does it still build?"* check.
Both were only findable by diffing **the CLI surface and the log text**, which
is what the tool does and what each sync file records.

## Two rules these files exist to keep

**Compare merged trees, never individual commits in a series.** Upstream's
`b227408` added a log line spelled `Peak: %.6f`; two later *"Address PR
comments"* commits in the same series renamed it to `Sample peak: %.6f`. Reading
the introducing commit produced a label that never shipped in any upstream
build, and it was reported as a finding before anyone opened the merged file.
See `sync-2026-08-18-rc2.md` §1.

**A gap in history is not a gap in content.** `git diff A...B` is
`diff(merge-base(A,B), B)`, and some upstream branches share no merge base at
all — the command answers `fatal: no merge base`, which reads as *"no changes"*
if stderr is discarded. Two upstream PRs looked like gaps this way and were
already present verbatim. Extract the feature's signature strings and grep the
tree instead.
