# Full audit: upstream PRs, branches, and third-party forks — 2026-08-21

**Question being answered:** should this fork rebase onto `0.9.4-rc2` and rebuild
from there, or stay on its own line? And have we missed anything upstream has?

**Answer, up front: stay on our line, merge rc2 forward when round 12 opens, and
never rebase.** Reasoning below, with the measurements.

---

## 0. Scope, including what could NOT be audited

| what | covered | how |
|---|---|---|
| upstream `master` (`0.9.4-rc2`) | **yes** | built both binaries, diffed CLI + log + deps |
| upstream branches (`deemphasis`, `accurip_test`) | **yes** | signature strings against our tree |
| **all 42 upstream PR heads** | **yes** | content-based, below |
| **third-party forks of `cyanreg/cyanrip`** | **NO** | see below |

**Third-party forks could not be enumerated from this environment, and that is a
gap in this audit rather than a finding of "none".** Anonymous git *reads* of
public repositories work, but the GitHub **API** does not cover repositories that
are not attached to the session, and the fork list is an API-only query:

```
GET https://api.github.com/repos/cyanreg/cyanrip  ->  HTTP 403
"GitHub access to this repository is not enabled for this session."
```

Attaching upstream with `access: "push"` would grant API access, but that means
requesting write credentials on somebody else's repository, which is not
appropriate for a read-only audit. **What that would take:** the fork list from
any browser, then `git ls-remote` per fork — reads work fine once we know the
names. Until then this document says nothing about third-party forks, in either
direction.

## 1. Method, and two wrong answers it produced first

This audit was run three times because the first two methods gave confidently
wrong results. Both failures are the ones this repository already documents, and
both are worth keeping.

**Attempt 1 — ancestry.** `git merge-base --is-ancestor <pr-head> master` reported
**0 of 42 PRs merged**, including PR #158, which is demonstrably in `master`.
GitHub merges by squash or rebase, so a merged PR's head is never an ancestor of
the branch that took it. *History-based checks cannot answer "is this in?"*

**Attempt 2 — whole-tree content.** Comparing every string literal in each PR's
tree against ours reported **0 of 42 covered**. A PR branch carries its own stale
base, so most of what it contains is old upstream code, not the PR's
contribution.

**Attempt 3, used here — the diff's added lines only.** For each PR, take
`git diff $(git merge-base master <pr>)..<pr> -- src/`, extract the string
literals it *adds*, and check each against upstream `master`'s tree and ours.
That answers the actual question: did this PR's contribution reach either tree?

## 2. Result: 42 PR heads

| class | count | disposition |
|---|---|---|
| no merge base (unrelated history, PRs #1–#120) | 21 | ancient; spot-checked as long-merged |
| has merge base, contribution fully present | 17 | nothing to do |
| **has merge base, contribution in NEITHER tree** | **4** | §3 |

The 21 with no merge base predate a history rewrite upstream. Rather than assume,
three were spot-checked by signature against `master`: MusicBrainz support
(#3/#4/#5) → present; drive info in the log (#119) → present; win32 `os_compat`
(#10/#48) → present. They are merged; their branches simply no longer share
ancestry.

## 3. The four genuinely outstanding PRs — and we already have two of them

| PR | subject | date | status here |
|---|---|---|---|
| **#116** | Improve `sample_peak_rel_amp()` | 2025-11-28 | **we already have it** |
| **#128** | Add CLI option to "just makecue" | 2025-12-10 | **we already have it** |
| #127 | Changes from review | 2025-11-28 | one string, cosmetic |
| #153 | More simplifications and cleanups | **2026-08-20** | deliberately not carried |

### #116 — we fixed this independently, and upstream still has the bug

The PR is one character of substance:

```
-  peak ? "ebur128=peak=true,anullsink"
+  peak ? "ebur128=peak=true+sample,anullsink"
```

`[MEASURED]` in both trees today:

```
ours:     src/cyanrip_encode.c:469   "ebur128=peak=true+sample,anullsink"
upstream: src/cyanrip_encode.c:466   "ebur128=peak=true,anullsink"
```

Without `+sample`, ebur128 never computes the sample peak — the field is
requested and comes back unset. This is the *same defect* recorded here as
"Task 1: fix `ebu_sample_peak` dead field", and the one real finding the
seven-lane workflow audit returned before it died: **a peak computed and then
discarded.** We fixed it; upstream has an open PR to fix it and shipped `rc2`
without it.

**So `rc2`'s new `Sample peak:` line is computed by a hand-rolled scan
(`sample_peak_rel_amp()`) precisely because their ebur128 sample peak does not
work yet.** Ours works, which is why we can cross-check one against the other and
they cannot.

### #128 — also already ours

`[MEASURED]` `cyanrip --help`: `--cue-only (-J): Only generate and print a CUE
sheet, don't rip`. Upstream `master` contains zero occurrences of the PR's
string. Independently implemented here.

### #153 — active yesterday, and deliberately not carried

Touches `pregap.c/h`, `subq_read*.c/h` — the sub-channel code we carry from
PR #115. It is **not** stale: last commit 2026-08-20. It remains uncarried for
the recorded reason: its macOS path calls `cdio_get_device_fd()`, which is not in
libcdio 2.1.0 — verified against the installed headers *and* the `.so` export
table. `src/pregap.c` keeps its copy-pasted-struct workaround because of it.

**This one needs re-checking when it moves**, since it restructures code we
maintain a divergent copy of.

## 4. Where we stand against upstream, honestly

**Ahead** — implemented here, absent upstream: the ebur128 sample-peak fix
(#116), `--cue-only` (#128), plus everything the fork exists for (diagnostics
record, stall watchdog, cache probe, handshake state, four-state `Pregap LSN:`,
the log contract).

**Convergent** — same thing reached independently, three times now:
`catalognumber`; the direct sample-peak scan (`sample_peak_rel_amp` there,
`direct_sample_peak` here); `--cue-only` / "just makecue". Three independent
rediscoveries is a signal the fork is solving upstream's real problems rather
than only its own.

**Behind** — MusicBrainz track-title and artist-credit preference (#158, #159,
merged into rc2), QR codes, flatpak packaging, the `rc2` version string.

## 5. Should we rebuild onto rc2?

**No, and the strongest reason is not effort — it is that rebasing destroys
published history.**

`[MEASURED]` 22 of our own SHAs are published and reachable today: 16
release-ledger rows, the manifest pin `c4d1a00`, and every `HANDSHAKE-OUR-PIN`
in the correspondence. `ddf7ac3` is the build Platterpus is **running right
now**. A rebase orphans all of them, and `git gc` then destroys them. Beyond git,
every rip ever made writes its build SHA into the logfile permanently — rewriting
history turns those into claims about builds that no longer exist.

**Second reason: rc2 is not a stable base.** Upstream's tags stop at `v0.9.3.1`;
`rc2` is a version string on `master`, not a release. Its two newest features are
in flux — the peak function it shipped has an open PR improving it (#116), and
#153 restructures sub-channel code as of yesterday. Rebuilding onto a base that
is itself moving buys nothing.

**Third: the work is far smaller than "rebuild".** Only **74 of our 300 commits**
touch `src/` or `meson.build`; the rest is docs, correspondence, tools and tests.
And a trial merge of `master` into `platterpus-fork` conflicts in **3 files of
14** — `meson.build` (version), `cyanrip_log.c` (the peak lines),
`cyanrip_main.h` (the peak field). All three are already analysed.

## 6. Merge, don't cherry-pick — and why that answers the deviation worry

The concern that *"the further we deviate the harder it will be to merge"* is
correct, and the mechanism matters:

- **Cherry-picking** upstream commits leaves the merge-base at `958e1ad`
  forever. Every future delta run re-presents the same commits as inbound, and
  the divergence measurement rots until it is useless.
- **Merging** advances the merge-base. Next time we measure only what is
  genuinely new.

So: merge. The cost is a merge commit on `platterpus-fork`, which today has a
straight line for bisecting. That rule was written for *our* topic branches; an
upstream sync is not one, and the carve-out should be written down when it is
first used.

**Merging early and often is the cheap path, and it is what keeps the door open
for upstream to take our work.** The alternative — accumulate for a year, then
attempt one heroic sync — is how forks die.

## 7. What "so upstream could incorporate it" actually requires

This is achievable and worth doing, but it needs a discipline we do not have yet:
**our changes are not currently separable.** Our 299 commits mix two kinds:

- **Upstreamable**: the ebur128 sample-peak fix, segfault fixes, `--cue-only`,
  stall detection, the genopt `GEN_OPT_LOG` fix, the libcdio log-handler routing.
  Upstream would plausibly take these.
- **Fork-only by design**: the handshake state, the release manifest, the
  Platterpus seam, the diagnostics record, the log contract.

Nothing in the repository lets you *point at* the first set. Recommended, not
done: label commits or maintain an index of upstreamable changes as they are
made — incrementally, which is far cheaper than reconstructing it later.

## 8. And the line that must not be crossed

**Converge on code; do not converge on the contract.** The things that make this
fork worth pinning are exactly the things upstream would not take:

- upstream prints `Sample peak: 1.000000`; we print percentage, dBFS, *and* a
  disagreement check against a second measurement
- upstream has two `Pregap LSN:` states; we have four, because we distinguish
  two ways of *not knowing*
- upstream's `C2 errors:` says "by drive"; ours was reworded deliberately

Converging on those would cost the project the precision it exists for. The
answer to *"keep going on our own or not?"* is **both**: our own line, merged
forward continuously, contributing back what is genuinely general.

---

*Audit refs (42 PR heads, upstream branches, 6 tags) were deleted after this run;
leaving them makes `git rev-list --all --not platterpus-fork` report upstream
commits as stranded work of ours.*
