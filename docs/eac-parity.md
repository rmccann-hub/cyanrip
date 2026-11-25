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
| 6 | Track 3 of the reference disc | No cause named. Its reads disagree between rips and between runs on this drive, and each wrong read logs `no error reported` and AccurateRip's `not found`, so none is called verified. In round 42 (`.35`, 2026-11-23 and 24), counting re-reads, it came right from the drive in 13 of the 14 whole-disc rips and was repaired from CTDB in the fourteenth: Platterpus's count, `platterpus@562a5a3f:docs/eac-parity.md` H.1. Its C2 probe of 2026-11-24 found C2 bits at track 3's seconds 251 and 252 in some reads, and none at 240, 244 or 245. Each run's counts are in its README, not restated here | `docs/rig-2026-11-09-5cc1c6b/`, `docs/rig-2026-11-14-edb73dd/`, `docs/rig-2026-11-17-fb28088/`, `docs/rig-2026-11-23-1280aa4/`, `docs/rig-2026-11-24-1280aa4/` and `docs/rig-2026-11-24b-c2probe/` READMEs; `docs/OPEN-ITEMS.md` HW-1 |
| 8 | Saying a wrong track is wrong | `read successfully!` printed over tracks AccurateRip rejects. `.27` prints `Track N read with no error reported.` instead, as Platterpus's round 36 lap 9 S17 accepts | `docs/history/KNOWN-ISSUES-2026-11-16.md`; our round 36 lap 8 S26 |
| 10 | Where a read was unsure | Positions are in the `--diagnostics` record from `.25`. Their wording in the EAC-layout log is Platterpus's R44, which we review | STATUS `error-positions`; Platterpus's TASKS R44 |
| 16 | Accurate stream | The drive's declaration is read and printed, "not measured". libcdio-paranoia neither reads it nor depends on it | Our round 36 lap 8 |
| 21 | Pregaps | Track 9's pregap is `94 or 95 frames (undecided)` in all 14 of round 42's whole-disc rips. EAC reads 94 on this drive: all four of its sessions, by Platterpus's count (`platterpus@562a5a3f:docs/eac-parity.md` H.2, C2). The cue writes 95, the earlier bound, by `.29`'s rule, without saying it is undecided; R43-1 proposes saying so. Since `.26` no log has decided 94, and `.27` records what each search saw in `Pregap search:` | `docs/OPEN-ITEMS.md` HW-6 (the counts by round) and R43-1; `docs/KNOWN-ISSUES.md` |
| 23 | CD-R detection | `.27` reads the drive's current profile itself; round 42's `.35` logs print `Recordable:     no, CD-ROM (drive's current profile)`. No recordable disc has been read on a drive | `docs/OPEN-ITEMS.md` HW-5; `docs/history/KNOWN-ISSUES-2026-11-04.md` |
| — | `Extraction speed:` under `-Z` | It divided one track's audio by every read's time. `.27` gives the kept read's own speed, as Platterpus's round 36 lap 9 S18 accepts | `docs/history/KNOWN-ISSUES-2026-11-04.md`; our round 36 lap 8 S27 |

Every row that needs the drive stays open until a rig run shows it. A green
suite is not that run (`CLAUDE.md`, *No CD drive in this environment*).
