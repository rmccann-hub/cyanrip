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
| Round 37's Full run, `.28` with 0.7.117, filed and read: no `.28` defect makes the pin unsafe to approve | evidence `dd48c1f`, reading `a4d9ec1` (merged in #83, `c0a52b5`) | `docs/rig-2026-11-03-3f288fb/README.md` |
| Their round 37 lap 5 filed. It crossed ours: theirs reached their `main` at 02:39:52Z (their #428, `platterpus@2522a1bb`) and ours `platterpus-fork` at 02:31:06Z, so under K1 the number is ours. This plan said 02:56:56Z, their next merge (#429): dumbass us read one merge past the one that carried it | `079ec02` (merged in #83) | `git merge-base --is-ancestor` over their first-parent merges |
| `STATUS.md`'s open items: 27 down to the 7 a run, Platterpus or upstream still owes | `be97b27` | its Changelog entry names each |
| `tools/redact.py`'s host-field pattern: 68 s to 0.4 s on 50,000 blank lines | `2accc2f` | the old pattern fails the new test's 5 s bound |
| CI's install steps stop at 10 minutes and retry a stalled mirror; the Windows job's downloads give up a stalled attempt after 60 s and retry it | `fe121f6` | the carried audit item; `tests/workflows.py` |

## P1: round 37's close: done

Round 37 closed on 2026-11-03 on our lap 7 and Platterpus's lap 6, both `GO`,
approving `.28` at `3f288fb` with their 0.7.117. Our lap 7 was published held in
#84 and released on the owner's word, *"release it"*. Their `FORK_PIN` rolls to
`3f288fb` on this close (their lap 6 S18). Round 38 opens with our lap 1, carrying
the proposals below.

## P2: needs a lap, and no drive (round 38, opened after round 37 closes)

Each is a line Platterpus parses or a count it acts on, so each is proposed in
a lap before it ships, `.29` included (the review of 2026-11-03, §2 and §4).

| Item | What settles it | Owner |
|---|---|---|
| **A5: `Ripping errors:` leaves out a `-Z` track whose re-reads never agreed**, while the track block says `Track 3 read with errors.` (the 2026-11-03 secure re-read: five reads, four checksums, footer `0`). `crip_ripping_errors()` counts the drive's errors and paranoia's skips, and the repeat-limit arm (`src/cyanrip_main.c:2154-2157`) adds to neither. **Folding it into the count is not a local fix:** Platterpus's read-speed ladder takes the count less the skips as what the drive failed (`platterpus@168761ef:src/platterpus/parsers/cyanrip_log.py:1089-1105`), so it would step the disc down for a disagreement no drive reported | a lap proposing a third part of the suffix, e.g. `(including 1 track whose re-reads never agreed)`, and their parser taking it | us, then Platterpus |
| **B5: the footer's denominators count the whole disc**: `-f` prints `Tracks ripped accurately: 0/14`, `-l 1` prints `1/14`; and a cancel's SIGTERM counts in `Ripping errors: 1` | a lap with the wordings: count against the tracks asked, and a cancel as a cancel | us, then Platterpus |
| **A6: `-H` on a disc without HDCD delivers a file 6 dB quieter** while the CRC and the AccurateRip verdict, taken before the filter, are unchanged | **Cause confirmed on an image, 2026-11-03**: libavfilter's `hdcd` shifts each 16-bit sample by 15 into s32, -6.02 dB, and every sample of the `-H` file is the plain one's shifted so (`KNOWN-ISSUES.md`). What remains: a lap proposing a line beside the CRC whenever a filter changed the delivered audio | us |
| **A7: track 9's pregap says `unknown` where the search narrowed to one sector** (LSN 145567): "94 or 95 frames, undecided", with both bounds for a cue's `INDEX 00` | a lap with the wording | us, then Platterpus |
| **B6: `Embedded cover art:` names a cover the muxer dropped** (`KNOWN-ISSUES.md`): an AV1 cover is logged as embedded in a FLAC that has none. The line is in the contract's P2. Platterpus passes only JPEG, PNG and GIF, so its rips cannot reach it | a lap proposing the fix, then a build, before `.29` | us |
| A checksum per second of audio for each kept read, in the `--diagnostics` record, so two rips can be compared region by region without the audio (the 2026-11-03 reading, *To add next time* 1) | a lap; a record field, not a log line | us |
| Their lap 5 S6: P5's lone `"` row for libcdio's identify message | optional | us |
| The K1 amendment (our lap 5 S10): a lap is sent when it reaches its side's default branch | a round of its own; round 37's crossing is its case | both, then the owners |

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
| EAC parity 6 (the review's A4): track 3 of the reference disc reads right on some reads and wrong on others. On 2026-11-03 it read wrong in all four rips of tracks 1 to 3 and right in all eight of track 3 alone; on 2026-10-28 the split ran the other way, so the rip mode alone does not decide it | Platterpus's ABBA test, tracks 2 and 3 together against track 3 alone, with these varied one at a time and each rip's AccurateRip verdict: the speed (no `-S`, then `-S 4`); `--cache-probe` on every rip, so each carries the cache model it read under; the paranoia level (`-P` max, then `-P 0`, which shows whether the difference arrives from the drive or from paranoia's fix-ups); and a second drive, which separates the disc from the drive. Overlap is not an option of ours: paranoia sets it, and exposing it is a feature for after `.29`. Track 3's FLAC from `timing B1` and from `accuracy B1`, still on the rig, would say where the wrong read differs |
| EAC parity 21: track 9's pregap, 94 frames to `.25` and EAC, `unknown` to `.27` and `.28`. `.28`'s `Pregap searches:` block narrowed it to LSN 145567, undecided after the 200-retry pass, in all 19 logs (A7 above words that) | that sector's Q frames, read raw on the rig, or a second drive |
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
| Cut `.29` (raised minimums, today's build and test changes, and the Enhanced CD offset fix; no log line's text changes) | a release no standing word covers | wait for the owner's word; round 37 has closed |
| A Fedora CI job (`docs/DEPENDENCY-PLAN.md` §4) | runner time and a new platform | none |
| Set `CYANRIP_REDACT_NAMES` where runs are filed | the name list lives outside the repository by design; without it the tools say *not checked* | not checked, said so |
| Read the repository's Security tab: Dependabot, code scanning and secret scanning alerts | nobody here has read them: GitHub refuses the Dependabot and code-scanning alert APIs to this session's credential ("Resource not accessible by integration"), and the session's proxy does not pass the secret-scanning one; read again 2026-11-03 | unread |
| File upstream items 24 to 28 (`docs/upstream/issues-to-file.md`) | filing upstream is the owner's act | unfiled |
| File the `skillcheck --verify` report with claude-code-skills | outside the two repositories | unfiled |
| Copy track 3's FLACs from `timing B1` and `accuracy B1` off the rig (`~/platterpus-rig/platterpustestsession20261103t023830z/rips/The Police/`) | the rig is the owner's | track 3's wrong reads stay unlocated |
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
