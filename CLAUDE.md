# cyanrip (fork)

A CD ripper in C (meson), linking FFmpeg and libcdio-paranoia: a fork of
upstream `cyanreg/cyanrip` that feeds **Platterpus** (`rmccann-hub/Platterpus`),
which parses this program's log as an archival record.

**Only the rules a session needs on every task, each with what fails without
it**, capped at 300 lines and 32 KiB (`tests/claude_md_cap.py`; the operator's
review of 2026-10-19, item 3). The reasons and citations behind them are in
`docs/history/CLAUDE-2026-10-21.md`, this file as it stood before the cut.
**Read `docs/SETTLED.md` before deriving anything, and the handshake README's
*Procedures* before rebuilding a step from git history**: a re-derived fact can
come out wrong, and a rebuilt step is how one gets dropped.

## Build and test

    meson setup build
    ninja -C build
    meson test -C build --print-errorlogs

A setup failure is almost always a missing `-dev` package. CI installs:

    apt-get install -y meson ninja-build pkg-config ffmpeg \
      libavcodec-dev libavformat-dev libavfilter-dev libavutil-dev \
      libswresample-dev libcdio-dev libcdio-cdda-dev libcdio-paranoia-dev \
      libmusicbrainz5-dev libcurl4-openssl-dev libqrencode-dev

`ffmpeg` is for the tests' `ffprobe`; `libchromaprint-dev` is optional and not
in CI. Minimum versions are pinned in `src/meson.build`.

**The full suite passes before every push** (the operator's rule, kept
2026-10-19): meson exit 0, `Fail: 0`, and exactly one `^Log of Meson test suite
run` header in `build/meson-logs/testlog.txt`. Remove that log first, check no
other run is going, by path or PID, and edit nothing while it runs: two runs on
one build directory write a log that is neither run.

Regenerate, never hand-edit, what is derived: `tools/gen-provider-contract.py >
PROVIDER-CONTRACT.md` after a `cyanrip_log()` call site or the option table
changes; `tools/gen-dependency-map.py` after a dependency, subprocess call or
URL; the golden reference after a lap or a log line. A check fails on each
when it is stale.

## Where things live

- `src/cyanrip_main.c`: argv, enumeration, the rip loop, `-Z` and its spool,
  pregap actions; `src/cyanrip_log.c` the log; `src/cue_writer.c` the CUE sheet.
- `src/pregap.c`, `src/cache_probe.c`, `src/stall_watchdog.c`,
  `src/diagnostics.c`: **read the header before changing one**; each records
  why it is built as it is.
- `tests/`: every test is registered in `tests/meson.build`, and a new
  `sc_<name>()` in `tests/rip_images.py` runs only once it is, so **register it
  in the same commit as the feature**, or that commit is not bisectable.
- `docs/KNOWN-ISSUES.md`: our open defects and the external bugs worked around
  here. `docs/upstream/`: syncs and defect reports.

## No CD drive in this environment

The suite rips BIN/CUE, NRG and `.toc` images through libcdio's image drivers.
Before accepting "no fixture can reach this", try another image format or build
the state directly (`tests/subq.c`, `tests/logrender.c`). **Flag any change to
drive I/O as needing hardware verification, name the row below it touches, and
never let a green suite imply coverage.** Date a rig session by its build.

| on a drive | state |
|---|---|
| C2 | cannot be done on this rig: its BDR-209D reports C2 unsupported |
| `-f` | ran from 2026-10-06 (`5704062`); a stopped search and one that finds nothing have not |
| damaged media | the read ran 2026-10-04 (`174a134`), the `-Z` arm 2026-10-06 and the skip arm 2026-10-21 (`ca0f097`); a drive that reports a failed read has not |
| CD-TEXT from a disc | not yet done: `mmc_read_cdtext` is not the `.toc` path |
| `Accurate stream:`, `Recordable:`, two-search `Pregap source:` | ran 2026-10-21 (`ca0f097`): `Accurate stream:` answers; `Recordable:` never does (libcdio), and `.27`'s own read of the profile has not run; the two-search clause has not printed |

## Say exactly what is true, and no more

The first rule; the rest is machinery for it. A rip measures an object that may
never be measured again, and every log line is a claim someone will rely on
without re-checking. **A nearly true claim is a wrong claim**, worse than none:
a missing field prompts a question and a confident wrong one does not. The
failure is almost always a word: a label asserts even when its value disclaims
(`Cache model:`, not `Cache defeat:`); a name stops discriminating when a
sibling appears (`Sample peak level:` beside `True peak level:`); say what was
observed, not what you infer ("none reported by libcdio").

Before a claim ships, in the log or in prose: **name the artifact** ("EAC's log
reports N"); **check the verb** (model or defeat, detect or fail to find, verify
or not contradict); **check the scope** ("16/16 pass" is not "works on
hardware"); **check what an absence means** (`none` and `unknown (reason)` are
different claims); **check the age** (never one timestamp for data of two ages);
and ask what a reader would be entitled to conclude. A frozen imprecise word is
documented and its rename proposed in a round, never reworded silently.

## The Platterpus seam: binding on both sides

**The log is an API.** Changing the text, indentation, field order or units of
a line Platterpus parses is a breaking change, and needs a handshake round
before it ships. The rules are `docs/handshake/PROTOCOL.md`. Four documents are
shared and owned by neither side (`tools/seam-sync-check.py`'s `SHARED` table;
Platterpus keeps the protocol at `docs/handshake-protocol.md`): a change to one
is a version both sides ship, never a local edit.

- **Run `tools/seam-sync-check.py --fetch` before acting on any lap of
  theirs** (1 disagreed, 2 could not check): two sides under different
  rulebooks agree about nothing, and every test still passes.
- **One file per exchange, and it is the lap**; the repository is the
  transport, and a lap is cited by commit SHA. A lap is sent when the operator
  releases it and says so in `HANDSHAKE-READY-TO-READ`: read the field, never a
  relay. A sent lap is never edited; when unsure, treat it as sent.
- **Answer from the artifact.** Never state a mechanism in their code without
  citing `platterpus@<sha>:<path>:<line>` (their repository is public). Read
  their parser before announcing a change they must absorb: a renamed line may
  be a delimiter. A removed string ships only after a release of theirs accepts
  both wordings. Read to verify, never to write their side for them.
- **A correction gets the same scrutiny as a claim.** Compare a described
  behaviour, do not acknowledge it; separate the finding from the diagnosis.
- **cyanrip opens rounds** (`PROTOCOL.md` §1a); a blocker goes first whoever
  opened. **cyanrip owns what needs the disc in the drive; Platterpus what can
  be derived afterwards** (`docs/OWNERSHIP.md`). We report measurements with
  provenance and never a verdict on a rip's quality.
- **Every fatal path prints a diagnosable line before exiting**, at column 0, to
  a stream the caller captures. **Never prompt or block on stdin.**
- **Identify as `platterpus-fork`** (`PROJECT_FORK_ID`) in the banner and every
  log's first line. Never mint a version in upstream's namespace: upstream's
  version verbatim, plus `+platterpus.N`.
- Anything the other side could notice (log, cue, CLI, exit codes, files on
  disk, dependencies, timing) is handshake material. Limits are found by running
  the binary (S-9); a seam defect's regression test lands with its fix, naming
  the round (S-11).
- **Our obligations are to any consumer.** A defect that exists upstream goes
  upstream (`docs/upstream/defect-reports.md`; filing is the operator's act). In
  commit messages and pull requests write *upstream issue 167*, never
  `cyanreg/cyanrip#167` or its URL: a commit with both posted a reference there.

## Rounds

A round decides one pin and must converge (round 7 took 39 laps).

- Close conditions are fixed in lap 1 and cannot grow; a finding needing no
  drive, no code of theirs and no operator's decision is fixed within the round.
  An agreed pin does not move without the operator's word. Pre-commit to the
  close: *"our next lap is `GO` unless X"*.
- No acknowledgement laps; findings go in commits and the Changelog. **But an
  answer is not a settlement** (operator, 2026-09-30): ask for missing reasons.
- **Give what you know, wait for the test** (operator, 2026-10-15): a lap goes
  once it carries something established, naming what only the run can settle.
- A close needs both verdicts, both versions and pins, and `HANDSHAKE-TESTED`;
  transcribe their declared verdict, never read prose as a `GO`.

`SETTLED.md` and `STATUS.md` are rewritten in place. Laps, filed statuses and
run evidence are never edited or merged: consolidation applies to
documentation, never to evidence.

## The operator, and Platterpus

- **Times to the operator are US Eastern on a 12-hour clock with the zone**
  (`1:45 PM EDT`; the operator's word of 2026-10-19). Wire values (lap headers
  and statements, commit dates, `STATUS.md`) stay UTC.
- Every lap ends with `## Diagnostics`, and a round's last lap carries
  `## Round summary` before it: the operator's items 2 and 3 of 2026-10-14, word
  for word in `docs/handshake/README.md`, *Writing our lap, held*.
- Item 4 of that message, word for word:

      4. A HANDOFF PROMPT AT THE END OF EVERY REPLY. Whenever you release a lap, push to evidence,
         merge a pull request the other side needs, or need something from anyone, end your reply to
         me with this block, filled in, and nothing after it. I copy it as-is to the other session
         and to the claude-code-skills session. Keep it to these lines:

         HANDOFF from <platterpus|fork>, <UTC time>
         DONE: <one line: what happened>
         READ: <repo> <branch> <path, PR or evidence commit> at <commit>
         NEXT: <one line: what the reader should do now, or "nothing, for information">
         ASK: <a question for the operator, or none>

         If a reply needs no handoff, end it with: HANDOFF: none

  Its time gives both zones: `HANDOFF from fork, 2:35 PM EDT (18:35 UTC)`.
- **A lap a standing release word covers is released in the pull request that
  publishes it**, sent when it merges green (operator, 2026-10-19); re-read
  their record before the merge. Otherwise a lap is published held.
- **Each side reads the other directly** (owner, 2026-10-19): at a session's
  start and before ending a turn, read Platterpus's `main`,
  `docs/handshake/outbound/`. A newer lap released to us is the cue to file it
  (`tools/take-in-lap.py`) and answer. `ASK:` carries only what the owner keeps:
  hardware runs, releases no standing word covers, overrides, the second-read
  default, and anything outside the two repositories.

## Personal details stay out of what is committed

The owner's rule, 2026-10-12: *"keep personal details out of anything newly
committed: home-folder paths become ~, the hostname becomes host, and the
owner's real name isn't written. Apply this to new evidence and laps, through
the export or filing tools rather than by hand. Leave the shared protocol
document's wire values as they are unless both sides agree to change them.
History stays as it is."*

`tools/redact.py` is the one implementation. The name comes only from a list
outside the repository (`$CYANRIP_REDACT_NAMES` or
`~/.config/cyanrip/redact-names`), and without one the tools say
*not checked*, which is not *not present*. A `HANDSHAKE-` line is never
rewritten. In a lap write `~` and `host` yourself.

## Run evidence lives on the `evidence` branch (HR-2)

Run folders are on the orphan `evidence` branch, which only gains commits;
`docs/evidence-manifest.tsv` has a row per file, and each folder's README stays
under `docs/`. **`tools/evidence.py` is the one place that knows where a file
is**, and nothing else may read an evidence path (`tests/evidence_readers.py`):
a test reads a copy under `tests/fixtures/evidence/`. Never fetch evidence into
the working clone with `--depth`. Filing a run, and keeping the branch out of
fetches where hooks do not run: the handshake README's *Procedures*.

## Verifying your own work

Each of these is a confident wrong answer this repository has produced.

- **Revert-prove every behavioural fix, one at a time**: the edit landed, the
  build is green, and the reverted binary behaves differently. A test that
  passes with the fix removed is decoration.
- **Assert against an independent artifact**, not what you wrote or a sibling
  build (two builds with one bug agree). Silence equals silence: check the data
  is non-trivial.
- **Count what a pattern returned** and ask whether that is the number you
  expected. Assert against a position, not a whole file: `identifier in text` is
  satisfied by a sentence denying the claim. A pattern matching both branches
  asserts nothing. `grep -c` over a glob prints one count per file.
- **Look at a whole log once** before concluding from a filtered view. **Wait
  on a PID, never a pattern** your own command line contains. **Build the way
  the build builds** (`-D_XOPEN_SOURCE=700`).
- **A check that reaches the network is not evidence about this program.** A
  check that cannot fire is worse than none: print `UNPROBED`.
- **A re-check is independent only in elapsed time**: give the gap, not the
  dates. `git ls-remote` asks the remote; `git branch -r` is a cache.
- `tools/mutate.py` measures what the suite misses; a 100% sweep means nothing
  until its inert-edit probe has run.
- **Derive, do not list**: a generator classifies from structure, never from a
  list of wordings. **Stage files by name, never `git add -A`.**

## Branches, merges and tags

- `master` mirrors upstream and is never committed to; the owner syncs it with
  GitHub's *Sync fork*. `platterpus-fork` is the default branch, the only ref a
  consumer builds from, and only moves forward.
- Work lands by pull request, merged with a merge commit, each commit green on
  its own. Push a topic branch only to open its pull request, never after it
  merges: a session cannot delete one, and a stale tip looks current.
- Rulesets block deleting and force-pushing `platterpus-fork`, `master` and
  `evidence`. A release is the commit `release-manifest.json` names and needs
  no tag; a tag, if the owner wants one, comes only from
  `.github/workflows/tag-release.yml`. Consumers pin a SHA, so never prune a
  ref a release can name: every log's build line would dangle.
- Lap files are compiled in (`tools/gen-handshake-state.py`), so choose a pin
  with `git log -- src/ meson.build docs/handshake/round-*.md
  docs/handshake/inbound/round-*.md tools/gen-handshake-state.py
  tools/release-gate.py`; a file can never name a build containing itself.
- A generated artifact needs two commits named: *generated by X, committed at
  Y*. Commit it on its own, never with `--amend` (X becomes unreachable). Never
  rewrite pushed history.

## Releases

Bump `+platterpus.N` and write the Changelog; from that clean commit regenerate
every derived file naming the version (contract, golden reference and
interrupted sample, dependency map); prove the candidate from a clean checkout
(`tools/record-release-suite.py`, under `docs/release-evidence/`, and a `git
archive` build whose rip verifies with `-Y`); then one publish commit appending
a `docs/release-ledger.tsv` row (append only) and regenerating
`release-manifest.json`. Commands: the handshake README, *Cutting a release*.

A release is published when `release-manifest.json` names it.
Choose the released commit after the artifacts agree, never at the bump. It
does not wait for a round (v8 §6b).
**Never decide by parsing the version**: order by `release_seq`.

## Watching upstream

When syncing, diff the CLI surface and the log text, not only the code
(`tools/upstream-delta.py`; verdicts in `docs/upstream/sync-*.md`, written
before anything merges). Compare merged trees (`git show <ref>:<path>`), never
one commit of a series. **An option this fork adds is long-only and named by
what it does**; the retired letters `-j`, `-k`, `-u` and `-x` go to nothing
until a decision says otherwise (`tests/option_letters.py`).

## Known external bugs and code style

External bugs worked around here are in `docs/KNOWN-ISSUES.md`, *Known external
bugs worked around here*; read it before touching libcdio, paranoia or the
cache model. Two bite tests: a cdrdao `.toc` loads only from its own directory,
and a synthetic signal can rip byte-reversed, so check it against its source.

C11, K&R-ish, 4 spaces, no tabs; each source file opens with the LGPL-2.1+
header from `src/utils.c`; log lines are column-aligned `label: value` within
their block, so read the neighbours first; match the nearest existing code.
Commit subjects are plain and imperative, one logical change per commit.
