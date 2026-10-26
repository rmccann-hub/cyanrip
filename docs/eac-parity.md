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
| 6 | Track 3 of the reference disc | No cause named. The track reads right on some reads and wrong on others, on one build at nearly one speed. The next Full run pairs `.25` and `.26` rips of it, on the owner's word of 2026-10-26 | Our round 36 lap 8 S8 |
| 8 | Saying a wrong track is wrong | `read successfully!` printed over tracks AccurateRip rejects. `.27` prints `Track N read with no error reported.` instead, as Platterpus's round 36 lap 9 S17 accepts | `docs/KNOWN-ISSUES.md`; our round 36 lap 8 S26 |
| 10 | Where a read was unsure | Positions are in the `--diagnostics` record from `.25`. Their wording in the EAC-layout log is Platterpus's R44, which we review | STATUS `error-positions`; Platterpus's TASKS R44 |
| 16 | Accurate stream | The drive's declaration is read and printed, "not measured". libcdio-paranoia neither reads it nor depends on it | Our round 36 lap 8 |
| 21 | Pregaps | `.26` never read the reference disc's track 9 as the 94 frames `.25` and EAC read. `.27` records what the search saw, in `Pregap search:` | STATUS `subchannel-pregap-varies`; `docs/KNOWN-ISSUES.md` |
| 23 | CD-R detection | `.26` printed libcdio's placeholder. `.27` reads the drive's current profile itself | STATUS `recordable-medium-line`; `docs/KNOWN-ISSUES.md` |
| — | `Extraction speed:` under `-Z` | It divides one track's audio by every read's time. The kept read's own speed is proposed | `docs/KNOWN-ISSUES.md`; our round 36 lap 8 |

Every row that needs the drive stays open until a rig run shows it. A green
suite is not that run (`CLAUDE.md`, *No CD drive in this environment*).
