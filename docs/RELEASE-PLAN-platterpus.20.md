# Release plan — `+platterpus.20`, round 30's beta

*Written 2026-10-05, **before its condition is met**, on the operator's
instruction to *"get everything ready for the next release"*, and under the
operator's word of the same day that round 30 stays open until everything is
fixed. **A plan, not a release.** `meson.build` says `0.9.4-rc2+platterpus.19`,
the ledger's last row is seq 29, and `tools/release-gate.py --release-gate`
exits 1 because round 30 is open. `.19`'s plan was written after its round
closed, on the operator's instruction then; this one is written early on the
operator's instruction now, so its §2 will move and its §4 says where.*

## 1. The condition

The operator, 2026-10-05, verbatim:

> *"want this round to look at everything and not end until we fix it. doesnt
> matter how many laps. fix, then we release betas of both applications, and
> test to acceptance of both to close the round"*

So `.20` is a **beta inside round 30**, not round 30's closing release:

- **A beta is permitted with a round open** (PROTOCOL v6 §6b): it claims no
  joint verification, and every rip it makes says so (§3). The gate's
  `--prerelease` prints the open round and permits it. v7 R8 point 2, the
  operator's O3, puts a provider's new release on beta until its run passes in
  any case.
- **Round 30's close conditions change, and that needs the operator's override
  recorded in a lap** (§6a-ter), since R1 fixed them at our lap 1. Our next lap
  carries it. As the instruction reads, the round closes when: (1) every finding
  either side holds is fixed, or carries a reason it cannot be fixed in this
  round that both sides accept; (2) both betas are released, ours first; (3) the
  Full acceptance run on that pair is filed in both trees and read by both; and
  (4) both closing laps declare `GO`.
- **Before the cut**, all of: every fix the round agrees is landed and the
  candidate named in a lap of ours; Platterpus has answered the P2 changes in §2
  (none removes a string they match, so round 20's order does not bind, but their
  health status and read-speed ladder key on the per-track arm); and
  `tools/release-gate.py --release-gate --prerelease` exits 0.
- **Their beta follows ours**, under option A: 0.6.66 naming `.20` as its build
  under review, with `FORK_PIN` the build round 29 or 30 last approved.

## 2. What `.20` contains, against `.19` at `174a134`

**Landed**, on `platterpus-fork` past the pin:

| change | commit | who can notice |
|---|---|---|
| **SIGHUP stops a rip like SIGTERM**: the stop marker, `Interrupted at:` and a signed footer, where a hangup killed the process with no footer | `1184a04` | a caller whose session ends mid-rip (their script console, round 30 lap 1 S25) |
| **The loudness figures are measured on the audio the encoders receive**, after de-emphasis or HDCD, where they described the read buffer | `cc79c5b` | a reader of the peak, R128 and `REPLAYGAIN_*` values on a de-emphasised or `-H` rip; no line's text changes |
| **Each `-Z` pass gets a fresh filter and loudness graph**, so the kept read is filtered as if it were the only one | `4c3bd3e` | the delivered audio of a de-emphasised `-Z` rip that encodes more than one pass |
| **A track paranoia skipped on reads `with errors`**: `read successfully!` was printed over 2,586 skips on 2026-10-04 | `e5a0897` | their per-track status and read-speed ladder, which key on the arm (`platterpus@5ec71f4e:src/platterpus/parsers/cyanrip_log.py:2848`). `Ripping errors:` is unchanged |
| **A `-Z` track that hit the repeat limit reads `with errors`**: five tracks read five ways each printed `read successfully!` | `4529810` | the same two; a separate commit so either can be dropped |
| **`Extraction speed:` keeps two significant figures below 1x**: 0.033x printed `0.0x` | `a72b162` | their `_TRACK_SPEED`, which reads three decimals at most, the most this prints |
| **A `-J` or `-f` run's footer says what it was**, `cue sheet only` or `offset search only`, where it said `aborted`; **a stop ends a `-f` search** instead of retrying | `aa1f067` | a caller of `-J` or `-f`. Both open no logfile. Their section O grades `-f` by its lines (`probe_grading.py:150-215` there). **A `-f` search that finds no offset still exits 0**: exiting 1 moves a row of the shared `seam-commands.md` §7, so it waits on a version of it both sides ship |
| **The `-Z` spool**: no pass is encoded while it is read; each goes to a `tmpfile()`, one per distinct checksum, and one is encoded when the track is decided, the read that converged or, at the repeat limit, the read the most reads agreed on, newest on a tie. The album loudness graph is fed that read alone. A full disk now stops a `-Z` rip: `Error creating the -Z spool: %s!` and three more spool errors, all beginning `Error`; `Error in encoding: %s` is gone | `d7ee6c4` | which bytes a non-converged `-Z` track delivers, and its EAC CRC32 and AccurateRip values with them; the album rows and `REPLAYGAIN_ALBUM_*`; their error matcher, whose `Error` prefix takes the new lines, and their message inventory, which names the removed one (`ripper_message_inventory.py:469` at `5ec71f4e`) |
| **A failed track aborts a rip of every track**, as it does under `-l`: `Error ripping: %s` and `Rip completed:  no (aborted, …)`, where the loop broke out and the footer said `yes` over a run that exited 1 | `c1e1ab1` | their tri-state footer reading, for a run that stopped on a failed track |
| **The cache probe scores a re-read by cd-paranoia's 6 ms** (`MIN_SEEK_MS`), not a quarter of a full-stroke seek, which every re-read beat; a slow re-read is tried three times. The `-j` record's `cache_probe.hit_ratio` becomes `hit_below_us`, schema `cyanrip-diagnostics/7` | `394ab17` | their section P, which runs `cd-paranoia -A` beside our probe: the two should now agree, and that run is the only test of it. Nothing of theirs parses the `-j` record |
| **A cache bracket carries the reads behind both ends**: on a miss the line adds `, 3 re-reads after a N-sector run took X ms or more`, the fastest of the three tries, where `128 to 255 sectors` on 2026-10-05 carried only the read behind 128; and it replaces `first uncached re-read`, which since `394ab17` printed the last of three | `6dd608c` | a reader of the line verbatim, as their rig-check surfaces it. No P2 row changes, since the clause fills the line's `%s`, and their parser reads nothing inside the line (`cyanrip_log.py:2324-2346` at `5ec71f4e`) |

**To land before the cut** — in this round, on the operator's word:

- **The hang with paranoia disabled** (`-P 0`), pinned on an image by
  `tests/badsector.c`; its speed on a drive is not measurable here.
- **Whatever the laps add.** The 2026-10-05 acceptance run
  (`docs/rig-2026-10-05-174a134/`) added `6dd608c`, above, and showed no defect
  in `.19` that was not already recorded.

**The contract against `.19`'s, derived, not described**:
`tools/contract-delta.py --text 174a134 <candidate>`. At `1770d3c`, with the
contract `--check` exit 0, **P2 changes by content in eight rows**:
`Extraction speed:  %.1fx` becomes `%.*fx`; `Rip completed:` gains `no (cue
sheet only, %i of %i tracks)` and `no (offset search only, %i of %i tracks)`;
four `-Z` spool errors are added, `Error creating`, `writing`, `reading` and
`verifying the -Z spool`; and `Error in encoding: %s` is removed. P5 gains the
four and loses the one. P5a's two `Done;` rows now name the jump that follows
them, `goto spool_encode`, where they named `goto finalize_ripping`. P1, P3 and
P7 only moved; P4, P6 and P8 are identical. The
units block gains two paragraphs: what decides the per-track arm, and the
speed's precision. `-j` moves to `cyanrip-diagnostics/7`: `cache_probe.hit_ratio` is replaced by `hit_below_us`. **Re-derive it at the
candidate**; this paragraph is a reading of one commit.

## 3. The channel, and the decision it poses

**Beta.** `stable` stays `.19` at `174a134` (round 29, closed) and `beta`
resolves to `.20`. Their acceptance run's section A reads our manifest and
requires the installed build to be their build under review and our newest
release (D3), which a beta row satisfies.

**What `.20`'s rips say about themselves.** Its tree has round 30 open, so
`tools/gen-handshake-state.py` compiles `released = 0` whatever
`-Ddeclare_released` says, and every log reads `Handshake: round 30 lap N OPEN,
verdict … -- NOT a released build`. That is true, and it is the mark R8 point 2
allows. Platterpus reads it as unapproved, which agrees with their `FORK_PIN`.

**THE DECISION, for the operator: what goes to stable after round 30 closes.**

- **(a) Move `.20` itself to stable**, by a second ledger row naming the same
  version and commit: v7 R8 point 2's *"moves it to stable"*, and the build the
  run tested. **But its logs say `NOT a released build` forever.** Once
  Platterpus approves it, their `cross_check_note()`
  (`platterpus@5ec71f4e:src/platterpus/handshake_approval.py:563-603`) reports
  *"Two independent witnesses disagree"* on every rip: their approval says
  approved, our binary says not released.
- **(b) Cut `.21` for stable from the tree in which round 30 is closed**, with
  `src/` byte-identical to `.20`'s. Its logs say `round 30 … closed, verdict GO
  -- released build`, and the two witnesses agree. It is the precedent of rounds
  7, 13 and 14 (betas `.5-beta.1`–`.8` then `.5`, and `.8`–`.10` then `.11`). The
  cost: the stable build is not byte-for-byte the build the run tested. Only its
  version string and compiled `Handshake:` line differ, which `tools/` can
  show by diffing the two trees' `src/` and the two binaries' `--version`.

**Recommended: (b).** (a) leaves a permanent disagreement in every stable rip,
which is the defect class this project exists to avoid; (b)'s difference is
two derived strings, stated and checkable. The next night's run then tests
`.21`, as R8 point 3 asks of a new pair.

## 4. The sequence

The same four steps as `.19`'s (`docs/RELEASE-PLAN-platterpus.19.md` §4), with
the gate's `--prerelease` and a beta row:

1. **The gate**: `tools/release-gate.py --release-gate --prerelease` exits 0,
   printing round 30 open.
2. **Bump** `meson.build` to `0.9.4-rc2+platterpus.20`. Red by construction.
3. **Regenerate, never hand-edit**: the provider contract, the golden reference
   and the interrupted sample, in their own commit, *"generated by X, committed
   at Y"*. Never `--amend`.
4. **Name the candidate** at the first commit where the version and every
   derived artifact agree, with the Changelog naming the golden reference's
   build, *"generated by X, committed at Y"*, which the suite checks. Prove it
   green on its own: the full suite in a fresh
   worktree from a removed log, and a `git archive` tarball built with
   `-Ddeclare_released=true` whose rip reports `NOT a released build`, since
   the round is open. The tarball rip needs `pregap.bin` copied from `cdda.bin`.
   Run `tools/record-release-suite.py` at the candidate.
5. **Publish**, in one commit: ledger row seq 30, **`beta`**, round 30; the
   manifest regenerated with `--check` exit 0; the changelog heading; the
   handshake README's pin blocks; `STATUS.md`'s `STATUS-RELEASED` and release
   rows; `CLAUDE.md`'s release paragraph; and this file's banner.
6. **Then the lap** naming the release commit, so their 0.6.66 can name it.

**A dry run of steps 2–4 was made on 2026-10-05**, in a scratch worktree at
the tip as it then stood, so that a defect like `.19`'s first candidate's turns up before the
real cut. The bump, the contract, the golden reference and the interrupted
sample regenerated cleanly, and the suite gave **99 of 102**, with one run in
its log. The three failures:

- **`Argv table in seam-commands.md`**, a real defect and not the bump's. The
  first version of the `-f` fix made a search that finds no offset exit 1,
  which changes a row of the jointly owned `seam-commands.md` §7. It was taken
  back before anything was pushed, by rewriting the unpushed commits, so the
  tip the dry run read is not on the branch; `aa1f067` is the fix without it,
  and it is
  proposed in round 30 instead.
- **`reference`, and `Sanitizer sweep`, which runs it again**: nothing named
  the build behind the regenerated golden reference. That is expected until
  step 4 names it. A dry Changelog line naming *"generated by X, committed at
  Y"* turned it green, so **step 4 must include that line at the candidate**,
  as `.19`'s did.

Nothing else moved: the argv table's banner normalisation (`1f850a1`) and
`STATUS-NEWEST-LAP` (`d93e56e`), the two things `.19`'s first candidate caught,
both held at the bumped version.

No tag: tag push is `HTTP 403` here, and the commit SHA is the identifier.

## 5. What this release does NOT verify

- **None of the eleven `src/` commits has run on a drive.** The skip arm is
  reproduced on an image by a shim that varies one sector's bytes on every
  read; a real disc's skips come from the drive. The acceptance run on a
  damaged disc is the first test, and only if the run includes one.
- **The `-f` stop path has never run**: the search needs AccurateRip data for
  the disc, and no fixture's disc has any. It is read from the source.
- **A wrong read with no skip and no `-Z` still reads `successfully!`**: a
  drive that returns the same wrong bytes twice gives paranoia nothing to skip.
  AccurateRip is what reports that, and only for a disc in its database.
- **`Ripping errors:` still counts only what the drive reports**, so a track
  can say `with errors` beside `Ripping errors: 0`. Whether it should count
  skips is Platterpus's question.
- **The cache figure's fix has never run on a drive.** Until the first `-x` run
  on `.20` agrees with `cd-paranoia -A`, do not cite it, and never cite `.19`'s.
- **C2 stays `UNREACHABLE`** on the rig's drive. `-f` and CD-TEXT from a
  physical disc are *not yet done*, which is a different claim.
