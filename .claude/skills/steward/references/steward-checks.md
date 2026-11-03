# Steward checks

Read this for what green means on a pull request here: which jobs run, which skip, how to read
their results at the head commit, and what a green run does not cover.

It covers reading CI. A red job's causes and fixes are `steward-failures`'s, the merge is
`steward-merge`'s, and the suite run before a push is `steward-push`'s.

## Rules

1. **Green is ten jobs passed at the head commit:** `evidence`, `fuzz`, `lint`, `linux
   (default)`, `linux (released)`, `linux (sanitizers)`, `linux (released+sanitizers)`, `linux
   (thread)`, `macos` and `mingw`, with `mingw-nightly` and `mingw-release` skipped, as they are
   on every pull request (fact `steward-ci-jobs`). Anything else is not green: a job queued, in
   progress, cancelled, failed or missing.
2. **Read the check runs of the head commit, filtered to the latest attempt,** not the pull
   request's summary line and not a webhook alone:

   ```sh
   head=$(gh api repos/rmccann-hub/cyanrip/pulls/<n> --jq .head.sha)
   gh api "repos/rmccann-hub/cyanrip/commits/$head/check-runs?per_page=50&filter=latest" \
       --jq '.check_runs[] | "\(.name): \(.status) \(.conclusion)"' | sort
   gh api repos/rmccann-hub/cyanrip/pulls/<n> --jq '{mergeable, mergeable_state}'
   ```

   `mergeable_state` is `clean` only when the branch merges without conflict and the checks
   passed; `unstable` means a check is pending or failed, which the list above tells apart;
   `dirty` means a merge conflict, which `steward-push` resolves.
3. **Only the head commit counts.** A push cancels the pull request's older run (fact
   `steward-pr-concurrency`), so a cancelled run on a replaced commit is neither a failure nor a
   pass. Events can arrive late, out of order or not at all: re-read the state before acting on
   one.
4. **A skipped test is not a pass.** `tests/hardening_probe.py` needs clang, which no suite row
   installs, so it skips on every CI row, and only a local run under clang covers it. Before
   saying what a pull request proved, read the job's `SKIP` lines for any test it adds or
   changes.
5. **Green covers this tree on disc images, not a drive.** No job has a CD drive. A change to
   drive I/O names the row of `CLAUDE.md`'s drive table it touches, and a green run never
   stands in for that row (`CLAUDE.md`, *No CD drive in this environment*).
6. **The base branch has its own runs.** A failure that is red on `platterpus-fork`'s head too
   is not the pull request's; read that commit's check runs the same way before blaming the
   diff.
7. **Know what each job checks,** so a red one is read in the right place:
   - `linux (…)`: the full suite on Ubuntu 24.04 under five option sets, the default build,
     `-Ddeclare_released=true`, ASan with UBSan, both together, and TSan; the `default` row
     also runs GCC's analyzer and installs valgrind for the suite's memcheck rip, and the
     `released` row builds with the oldest Meson `meson.build` allows and installs ruff for the
     suite's Python lint;
   - `macos`: the full suite on the `macos-26` runner, on Homebrew's libraries;
   - `mingw`: the Windows build from pinned sources, and a smoke test of the binary: its banner,
     and an info read of a committed disc image;
   - `fuzz`: the fuzz harnesses, under clang and libFuzzer;
   - `lint`: ShellCheck, gitleaks over the history, actionlint and zizmor;
   - `evidence`: conflict markers, commit subjects over the pull request's range, the evidence
     manifest against its branch, no tag on that branch, and every check that reads run
     evidence.

## Mistakes

- **Merging on a summary line.** GitHub's checks badge counts a skipped job as passing and can
  lag a push. Read each job at the head, by name.
- **Calling a superseded run red.** Its cancellation came from the concurrency group, not a
  failure. Look at the head commit's runs instead.
- **Waiting on a queued `macos` job as though it were running.** It waits for a runner and can
  be cancelled without starting (`steward-failures`).
- **Counting a test the run skipped.** A green row with the new test skipped proves nothing
  about it; say so in the pull request.
- **Reading `git branch -r` for what the remote holds.** It is a cache. `git ls-remote` asks
  the remote.

## Audit

Severity uses the standard's status words.

| Check | What to look for | Severity | Fix |
|---|---|---|---|
| Every job at the head | ten passed, two skipped, at the head SHA | fail | wait, or work the red job in `steward-failures` |
| Latest attempt only | `filter=latest` in the query | warn | re-read with it: an old attempt's failure hides a re-run's pass |
| Skips named | the pull request says which of its tests skipped on CI | warn | add the line, and where it did run |
| Drive rows named | a change to drive I/O names its row and says hardware is needed | fail | add it before the merge |
| Base branch compared | a failure also on `platterpus-fork`'s head is reported as not this pull request's | warn | read the base's runs, and comment once |

## Why

### Read each job at the head

- **The advice:** list the head commit's check runs by name, latest attempt, before calling
  anything green.
- **The reason:** on 2026-11-02 pull request #75 had three runs going at once, two on replaced
  commits, and `macos` was cancelled several times before it ran; only the head's own list said
  which result was current.
- **What others do, and why:** many projects merge on a required-checks gate. No ruleset here
  requires a status check: both block only deletion and force-pushes (fact `steward-rulesets`),
  so GitHub would merge a red pull request, and the read is the gate.
- **What it costs:** one API call per check-in.
- **When to choose differently:** if a ruleset comes to require all ten jobs, the mergeable
  state answers most of it, though a skipped test still needs reading.

### A skipped test is not a pass

- **The advice:** name every test a pull request adds that skipped on CI, and where it did run.
- **The reason:** `CLAUDE.md`'s first rule: a green row with the test skipped is a nearly true
  claim about it.
- **What others do, and why:** most CI reports a skip as success, because a test that cannot
  run on a platform is not a failure there.
- **What it costs:** a line in the pull request.
- **When to choose differently:** never for a test the pull request exists to add.

## Facts

Versions, dates and defaults, each named elsewhere in this module by its ID. Checked
2026-11-03.

| ID | Fact | Source | Quote | Checked | Check by |
|---|---|---|---|---|---|
| `steward-ci-jobs` | The suite rows' names come from the matrix, five of them, and the two Windows publishing jobs run only on a release or upstream's push | [ci.yml](https://raw.githubusercontent.com/rmccann-hub/cyanrip/platterpus-fork/.github/workflows/ci.yml) | "if: github.event_name == 'release'" | 2026-11-03 | 2027-02-03 |
| `steward-pr-concurrency` | A pull request's run is cancelled when a newer commit is pushed to it; other runs are never cancelled | [ci.yml](https://raw.githubusercontent.com/rmccann-hub/cyanrip/platterpus-fork/.github/workflows/ci.yml) | "cancel-in-progress: ${{ github.event_name == 'pull_request' }}" | 2026-11-03 | 2027-02-03 |
| `steward-rulesets` | The two rulesets, on the default branch with `master` and on `evidence`, block deletion and non-fast-forward pushes, and require no status check | [rulesets](https://api.github.com/repos/rmccann-hub/cyanrip/rulesets) | "Protected Branches" | 2026-11-03 | 2027-02-03 |
| `steward-macos-runner` | The macOS job runs on the `macos-26` label | [ci.yml](https://raw.githubusercontent.com/rmccann-hub/cyanrip/platterpus-fork/.github/workflows/ci.yml) | "runs-on: macos-26" | 2026-11-03 | 2027-02-03 |

## Sources

Every source, with its license and how this module uses it: quoted, adapted with a notice, or
stated in our own words with a link.

| Source | Used for | License |
|---|---|---|
| [`.github/workflows/ci.yml`](https://github.com/rmccann-hub/cyanrip/blob/platterpus-fork/.github/workflows/ci.yml) | the jobs, their triggers and the concurrency group, quoted | LGPL-2.1-or-later, this repository's |
| [`CLAUDE.md`](https://github.com/rmccann-hub/cyanrip/blob/platterpus-fork/CLAUDE.md) | the rules this module points to, named and not restated | LGPL-2.1-or-later, this repository's |
| [GitHub REST API, pull requests](https://docs.github.com/en/rest/pulls/pulls) | `mergeable_state` and the merge endpoint, in our own words | CC BY 4.0 |
| [GitHub REST API, check runs](https://docs.github.com/en/rest/checks/runs) | listing a commit's check runs with `filter=latest`, in our own words | CC BY 4.0 |
