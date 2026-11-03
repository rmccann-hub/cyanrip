# Readiness plan: what stands between the fork and "ready to go"

*Written 2026-11-03 on the owner's word: "fix everything else you can without
my input. look at open tasks, open items, fix them all or prioritize them for
next time … fix all bugs, fix our testing to be quicker, make sure we are using
the correct dependencies, reduce security issues, and have the best user
experience, while at the same time matching or improving on the EAC actual
output of correct bit correct files."* It is rewritten in place as items close.

**The yardstick for bit-correct output is `docs/eac-parity.md`'s, not a
logchecker's score:** a track is right when AccurateRip verifies its whole
checksum at high confidence, or CTDB's strongest entry agrees, and the worst
outcome is a wrong track reported as fine. Nothing in this environment can
show that: there is no drive here, and a green suite rips disc images only
(`CLAUDE.md`, *No CD drive in this environment*). Every row below that needs a
drive stays open until a rig run shows it.

## Done on 2026-11-03, without the owner's input

| What | Commit | Shown by |
|---|---|---|
| `-Wextra` shipped and gated at zero, less `-Wunused-parameter` and `-Wsign-compare`, whose 29 sites were read one by one | `fa8b314` | a planted `size_t < 0` fails the new gate and passed the old |
| The gate's claim that an unused `deemphasis` was the `-H` defect, corrected: it never was | `fa8b314` | the tree at `9995a10` |
| The tests build with no clang warning (16 before, all in `tests/`) | `7931e5d` | GCC 13.3 and clang 18.1, whole tree, 0 diagnostics |
| `No personal details in new evidence`: 17.6 s to 2.6 s, nothing checked less | `36e675d`, `0994170` | the old code as an oracle over 14,932 texts; a planted home path still fails |
| The black-box sweep's workers: 8 measured twice as slow as 4, so 4 stays | `445ebb6` | 188 s against 366 s, alone, same results |
| The last two `sprintf` calls in `src/` bounded | `2bd0c67` | the string sent is unchanged |
| The binary's hardening, read from the linked file | — | PIE, full RELRO (`BIND_NOW`), non-executable stack, stack protector and `_FORTIFY_SOURCE=3` |
| `.29`'s raised dependency minimums, each built by a CI job | `2f38264` (merged in #80) | `docs/DEPENDENCY-PLAN.md` §3 |
| Every run's reading ends with questions, gaps and next time; the checklist for `.28`'s run | #81, `21a8a52` | `docs/ROUND-37-READING-PLAN.md` |

## P1: the Full run on `.28` with Platterpus 0.7.117

Round 37 closes on it, and both sides have pre-committed: our first lap after
reading the run is `GO` unless it shows a defect in `.28` that makes the pin
unsafe to approve (our lap 5 S12, their lap 5 S8).

1. **The owner runs it and uploads the bundle.** Owner.
2. **We file it** on our evidence branch with `tools/ingest-bundle.py` and read
   it against `docs/ROUND-37-READING-PLAN.md`, sections A to F, ending with
   *Questions, gaps and next time*. Us, the session the bundle reaches.
3. **Our reading lap closes the round** with `## Round summary`. Us. Whether
   that lap goes on the standing word or needs the owner's is the open
   question in the handoff: a closing `GO` moves round 37's pin to approved,
   and a pin move stays the owner's.

## P2: needs a lap, and no drive

| Item | What settles it | Owner |
|---|---|---|
| **Platterpus's round 37 lap 5 crossed ours** at the same number: theirs reached their `main` at 02:56:56Z and ours `platterpus-fork` at 02:31:06Z, so under K1 the number is ours and theirs stays as sent. `tools/take-in-lap.py` refuses to file it while `seam-commands.md` differs | their copy of our `seam-commands.md` at `b99b286` (our lap 5 S5), then we file theirs | Platterpus, then us |
| **`Embedded cover art:` names a cover the muxer dropped** (`KNOWN-ISSUES.md`): an AV1 cover is logged as embedded in a FLAC that has none. The line is in the contract's P2 | a lap proposing the fix, then a build | us |
| Their lap 5 S6: P5's lone `"` row for libcdio's identify message | optional, next round | us |
| The K1 amendment (our lap 5 S10): a lap is sent when it reaches its side's default branch | a round of its own after round 37; tonight's second crossing is its case | both, then the owners |

**Recommended shape for the cover-art fix:** print what the muxer wrote, read
back after the header is written, so the line can never claim a cover the file
does not hold; and, where the cover is the user's own file and its format is
known before the rip, refuse it up front with exit 64 naming the format. A
cover fetched from the Cover Art Archive arrives after the rip has started, so
refusing up front cannot cover that case alone.

## P2: needs a drive (the rig's BDR-209D unless named)

Each is a row of `CLAUDE.md`'s hardware table or of `docs/eac-parity.md`. The
`.28` Full run may reach some; its reading says which.

| Row | What would settle it |
|---|---|
| EAC parity 6: track 3 of the reference disc reads right on some reads and wrong on others, with no cause named | paired rips of track 3 at one speed and at another, with their AccurateRip verdicts |
| EAC parity 21: track 9's pregap, 94 frames to `.25` and EAC, `unknown` to `.27`, with LSN 145567 undecided | the same sector's sub-channel on `.28`'s `Pregap searches:` block |
| `-f`: a stopped search, and one that finds nothing | a disc AccurateRip lacks, and an interrupted `-f` |
| A drive that reports a failed read | a damaged disc on a drive that reports read errors, not only C2 |
| CD-TEXT from a physical disc | a disc with CD-TEXT; `mmc_read_cdtext` is not the `.toc` path the suite reaches |
| `Recordable:` on a recordable disc | any CD-R |
| `Pregap source:`'s two-search clause | a disc whose pregap needs both searches |
| C2 | a drive that reports C2 support; the BDR-209D reports it unsupported |
| `-W` on a pre-emphasised disc | a pressed disc with pre-emphasis |

## P3: the owner's decisions

| Decision | Why it is the owner's | Default if no word |
|---|---|---|
| Cut `.29` (raised minimums and today's build and test changes; no log line changes) | a release no standing word covers | wait for round 37 to close |
| A Fedora CI job (`docs/DEPENDENCY-PLAN.md` §4) | runner time and a new platform | none |
| May the session send the closing `GO` without asking again, if the run reads clean | a pin move | ask |
| Set `CYANRIP_REDACT_NAMES` where runs are filed | the name list lives outside the repository by design; without it the tools say *not checked* | not checked, said so |
| Read the repository's Security tab: Dependabot, code scanning and secret scanning alerts | nobody here has read them: GitHub refuses the Dependabot and code-scanning alert APIs to this session's credential ("Resource not accessible by integration"), and the session's proxy does not pass the secret-scanning one; read again 2026-11-03 | unread |
| File upstream items 24 to 28 (`docs/upstream/issues-to-file.md`) | filing upstream is the owner's act | unfiled |
| File the `skillcheck --verify` report with claude-code-skills | outside the two repositories | unfiled |
| Let the black-box sweep run beside the other tests (`docs/OPTIMISATION-PLAN.md` A1) | it changes a containment check's precondition | runs alone |

## P4: test time, what is left

Measured on this machine (4 CPUs). The black-box sweep runs alone for about
190 s, so it is most of the suite's wall time, and only A1 above moves that.
In the suite's last run the other slowest were `Settled facts` (89 s, 30.5 s
when idle), `Lap statements are well formed` (80 s), `Sanitizer sweep` (75 s)
and `Rip under memcheck` (64 s); each is CPU-bound and slower in the suite
because the others share its cores. None has a change that keeps every check
and is measured to help yet; each candidate goes in `docs/OPTIMISATION-PLAN.md`
with its before and after, under its rule that nothing may check less.
