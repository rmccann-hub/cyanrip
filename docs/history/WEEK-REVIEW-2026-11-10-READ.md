# The outside week review of 2026-11-10, read against this tree on 2026-11-18

**What this is.** The claude-code-skills session reviewed both repositories for
2026-11-03 to 2026-11-10 and sent both sessions a note asking for `done`,
`already`, `not doing` or `wrong` on each point. Both files are archived on the
evidence branch at `60ec8702`, under
`docs/outside-reviews-2026-11-17/imported/audit-log/`:
`research/2026-11-10/week-review-2026-11-10.md`, the review (R below), and
`kit/messages/FOR-BOTH-2026-11-10-week-review.md`, the note (M below). This
repository had not read them (`docs/OPEN-ITEMS.md` US-34). This file records
the reading, at `71430d40`, with the evidence branch at `73d45f9`. The rest of
the audit log is still unread, and US-34 keeps it.

**How it was read.** A reading pass compared each point that names this fork
with the tree. Its verdicts were then checked here against the sources for
every point that is still open:

- the note's text;
- `PROTOCOL.md` R1, and the two overrides of it in our round 41 lap 5;
- the evidence branch's root;
- the lost-drive lines in `src/cyanrip_main.c`;
- `STATUS.md`.

Points about the reviewer's own skills and standard (R §3 and §4) are left
out, except where they name a file here.

## Still holds, and where each is now tracked

| Point | What holds | Now |
|---|---|---|
| M18-22, "a person's acceptance run goes between rounds, on the released pair" | Round 41 moved its pin from `.33` to `.34` in lap 3 and ran its rip inside the round | US-37 |
| M23-25, R1 "goes up for amendment" | R1 (`PROTOCOL.md`, *R1 — Close conditions are fixed in lap 1*) is unchanged, and round 41 overrode it again, on both sides (our lap 5, its two `override: R1` lines) | US-37 |
| M31-33, "the request names its builder" | No rule here says so | US-37 |
| M44-45, the fork's F2 | A drive lost mid-rip logs `Drive media change query failed (libcdio error N), stopping!`, then `Error ripping: Input/output error`; nothing says the drive is gone. That is what libcdio reported; "gone" would be an inference | US-38 |
| M62-63, R128-135, no README at the evidence branch's root; the standard's four questions on records | The evidence branch's root holds only `docs/`. `docs/README.md` maps the files by kind, and nothing answers the four questions as such | US-36 |
| R287-290, `STATUS.md`'s *Now* stale under a checked block | **Fixed 2026-11-18**: on 2026-11-17 it still said `.34` was on beta, `.33` stood, v9 governed and Platterpus's newest release was 0.7.125. The section is rewritten, and `status_now_is_current` now fails when it is older than the newest lap or release | Closed in the same pull request |
| R369-373, M49-51, the steward's one-re-run rule differs from Platterpus's | The steward skill's mirror rule says nothing of Platterpus's | US-39 |
| The note's ask itself | No reply was recorded here | This file is the reply's substance; sending it to the reviewer is outside the two repositories and so the owner's |

## Already done, or overtaken

| Point | Verdict | Evidence |
|---|---|---|
| M26-29, turns: whose number is next, a lap out of turn held, a clash renumbered | Done | v10 §4a, `PROTOCOL.md`, *Whose number is next*; in both trees byte-identical at `platterpus@25cc0dd` |
| M30-33, two drive-test runners | Done | `085e394c` retired ours, per our round 38 lap 18 S3 |
| M37-39, R99-106, stable still `.23` | Done | `f9fdd1a7` put `.32` on stable on 2026-11-16; US-33 moves it to `.34` when round 41 closes |
| M64-65, the owner's runs of 2026-11-09 on no evidence branch | Done | Evidence `198ee582`, `docs/rig-2026-11-09-5cc1c6b`; `511dac32` on the default branch |
| R75-77, the `C2 errors:` wording | Done | Proposed in round 39, shipped in `.32`; reading C2 ourselves is HW-1 |
| R80-81, the liveness gap | Done, not run on a drive | `b1264f9c` and `3e43ca74` in `.31`; HW-13 |
| R171-176, the gate not fail-closed on unknown header keys | Already done when written | `7d40024e`, 2026-11-05 |
| R111, track 3 under `-Z` settled only by a drive test | Overtaken | Track 3 read `59D352DD` in all five rips of round 39, and all 14 tracks verified in all five of round 41 |
| R78-79, the fork's Quiet Drive position | Overtaken | Pioneer's utility cannot reach the drive (their round 38 lap 15); our lap 16 marks it unsettleable |
| R114-127, no `archive` branch | Still none, by choice | The `evidence` branch does that job: run folders since 2026-10-14 and the outside reviews since `60ec8702`, indexed by `docs/evidence-manifest.tsv` |
| R107, R216-219, the macOS runner and the slow package mirror | Tracked | US-19; the steward's failure table re-runs a mirror timeout once and never raises the limit |
| R343-348, `skillcheck --verify`'s report | Tracked | OW-11 |
| R387-393, `CLAUDE.md`'s size and the tone rule's count | Overtaken | `tests/claude_md_cap.py` caps the file; the counts have moved |
