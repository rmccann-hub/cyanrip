# EAC parity: the fork's rows

The owner's goal, 2026-10-25: *"my goal is to be better or at best equal, to
eac, in all regards"*. The plan of record is the claude-code-skills session's
*EAC parity: the plan of record*, written 2026-10-26 for both sessions. Its
section 5 grades every regard, EAC against us. This file keeps the rows that
are the fork's, and where each is tracked. Platterpus keeps its own in its
`docs/eac-parity.md`.

**The yardstick is the plan's section 2, not a logchecker's score.** A track is
right when AccurateRip verifies its whole checksum at high confidence, or
CTDB's strongest entry agrees. The worst outcome is a wrong track reported as
fine.

| Row | Regard | Where we stand | Tracked in |
|---|---|---|---|
| 5 | A damaged disc | `-r` bounds paranoia's retries of a stretch, and `-Z`'s whole-track reads. It is not EAC's 82 reads of a sector; the two measure different things | Our round 36 lap 8 (what `-r` means); `src/cyanrip_main.h`, `crip_frame_retry_limit()` |
| 6 | Track 3 of the reference disc | No cause named. On 2026-11-03 all four timed rips read it wrong and all eight paired rips right, and on 2026-10-28 the reverse. On 2026-11-09 (`.30`) that clustering did not recur: verified and wrong reads alternated within each run, 7 verified in 22, ten of the fifteen wrong reads one value, `3D8FCF0C`, and the speed asked for did not change the speed read. Round 40's rip of 2026-11-14 (`.32`) read it wrong on all five whole-disc reads, and its securing pass delivered `59D352DD`, which AccurateRip matches, in four of the five; the disagreeing seconds were 244, 245, 251 and 252. Each wrong read logs `no error reported` and AccurateRip's `not found`, so none is called verified. What the drive does at those seconds is the C2 probe's question | `docs/rig-2026-11-03-3f288fb/README.md`; `docs/rig-2026-10-28-5aeefc4/README.md`; `docs/rig-2026-11-09-5cc1c6b/README.md`; `docs/rig-2026-11-14-edb73dd/README.md`; `docs/OPEN-ITEMS.md` R41-4, HW-1 |
| 8 | Saying a wrong track is wrong | `read successfully!` printed over tracks AccurateRip rejects. `.27` prints `Track N read with no error reported.` instead, as Platterpus's round 36 lap 9 S17 accepts | `docs/history/KNOWN-ISSUES-2026-11-16.md`; our round 36 lap 8 S26 |
| 10 | Where a read was unsure | Positions are in the `--diagnostics` record from `.25`. Their wording in the EAC-layout log is Platterpus's R44, which we review | STATUS `error-positions`; Platterpus's TASKS R44 |
| 16 | Accurate stream | The drive's declaration is read and printed, "not measured". libcdio-paranoia neither reads it nor depends on it | Our round 36 lap 8 |
| 21 | Pregaps | `.26` never read the reference disc's track 9 as the 94 frames `.25` and EAC read. `.27` records what the search saw, in `Pregap search:` | STATUS `subchannel-pregap-varies`; `docs/KNOWN-ISSUES.md` |
| 23 | CD-R detection | `.26` printed libcdio's placeholder. `.27` reads the drive's current profile itself | STATUS `recordable-medium-line`; `docs/history/KNOWN-ISSUES-2026-11-04.md` |
| — | `Extraction speed:` under `-Z` | It divided one track's audio by every read's time. `.27` gives the kept read's own speed, as Platterpus's round 36 lap 9 S18 accepts | `docs/history/KNOWN-ISSUES-2026-11-04.md`; our round 36 lap 8 S27 |

Every row that needs the drive stays open until a rig run shows it. A green
suite is not that run (`CLAUDE.md`, *No CD drive in this environment*).
