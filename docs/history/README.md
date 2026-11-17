# History: documents kept as they stood

**Nothing here is maintained.** Each file is a record of how something stood
when it moved here, kept so a citation to it still resolves and so the
reasons behind a rule can be read. Where a file here and a living document
disagree, the living one is current. Laps and run evidence never come here:
they stay where they were filed, unedited (`CLAUDE.md`).

**What is still open lives in `docs/OPEN-ITEMS.md`.** On 2026-11-16 every
open step these plans carried was moved there, with its id given below.

**Files moved on 2026-11-16 moved byte for byte**, so git records each as a
rename. Three of them, `BETA-NOTE.md`, `round-14-acceptance-spec.md` and
`AUDIT-2026-09-05.md`, carry the owner's name from before the owner's rule of
2026-10-12, which leaves history as it is, and were not edited.

| File | What it is | Why it is here |
|---|---|---|
| `CLAUDE-2026-10-21.md` | `CLAUDE.md` before the cut to 300 lines | The reasons and citations behind its rules. `docs_do_not_contradict_themselves` reads its retired-rule markers |
| `Changelog-archive.md` | `Changelog.md`'s releases `.22` and earlier | `sc_changelog_names_every_release` reads it after `Changelog.md` |
| `KNOWN-ISSUES-2026-10-21.md`, `KNOWN-ISSUES-2026-11-04.md`, `KNOWN-ISSUES-2026-11-16.md` | Known issues closed and pinned by a test, moved when they closed; the 2026-11-16 file opens with a table of each item's fix, release and test | `docs/KNOWN-ISSUES.md`'s rule: an item leaves when it is fixed and a test pins it |
| `BETA-NOTE.md` | The note for beta.5 at `9048082` | Superseded 2026-09-13, as its banner says |
| `round-14-acceptance-spec.md` | Round 14's acceptance specification | Historical, as its banner says |
| `AUDIT-2026-08-05.md` | The audit of 2026-08-05 | Its §3 gaps are the drive rows of `docs/OPEN-ITEMS.md`, *Needs a drive* |
| `AUDIT-2026-09-05.md` | The audit of 2026-09-05 | §1.1 fixed at `9207def`, §1.2 by CI; leads c, g and l are OPEN-ITEMS US-20 |
| `upstream-audit-2026-08-21-prs-and-forks.md` | Upstream's pull requests and forks, 2026-08-21 | Answered "stay on our line"; rc2 merged at `1ee56fc`. Its §0, listing third-party forks, was declined on 2026-11-16; its §7 is `docs/upstream/carried-patches.md` since 2026-11-16; its §3, §4 and §7 count `-J` as ours, but it is upstream's `ca7e830c` (corrected in `docs/upstream/carried-patches.md` §1, 2026-11-16) |
| `OPTIMISATION-PLAN.md` | The suite and CI speed plan | A2, B, C and E built (`c085847`, `08cb71d`, `0698174`, `126c433`, `9d52271`); D is CI; F is `CLAUDE.md`'s cut. A1 was declined on 2026-11-16, so the sweep keeps running alone; D.2's ccache is not done and not decided |
| `UPGRADE-CHANNELS-PLAN.md` | The release-channel plan | §3 to §5 built and §6a retired on 2026-10-19, as its banner says. Whether a beta expires is PP-15 |
| `READINESS-PLAN.md` | The readiness plan of 2026-11-05 | P1 done when round 37 closed; P2's lap items shipped in `.29`; `.29` and `.30` cut. Its owner rows are OW-7, OW-9 and OW-11, and the copy of track 3's FLACs was dropped on 2026-11-16, overtaken by round 40's run; its drive rows are *Needs a drive* |
| `ROUND-37-READING-PLAN.md` | The checklist for reading `.28`'s Full run | The method is now the handshake README's *Filing and reading a run* |
| `2026-11-04-misreads-and-pregaps.md` | The synthesis of 2026-11-04's research on misreads and pregaps | R1, R2 and R4's undecided form are built, and observations 1 and 2 ran on 2026-11-09. R3, R4's cache defeat and R5 are US-12 and US-13. Its three sources stay in `docs/research/` |
| `UX-REVIEW-2026-11-17.md` | An outside end-user review of `fd20a0a`, filed verbatim | Triaged 2026-11-17 against `27728a75`, whose `src/` is the same: all 28 findings hold. Its open steps are OPEN-ITEMS US-31 and US-32; the owner chose on 2026-11-17 which go into `.35` and which round 42 proposes. Five things in it are corrected there and in the Changelog: P3 does not call the progress line unstable wording, since the contract lists it only as `\r` and `%s`; F5's `NOT a released build` prints only on a build not declared released; F22's key variable is in the README's AcoustID section, not its table; F19 is not Safe, since Platterpus's source matches `Trying to quit`; and F25 is not Safe either, since files on disk are handshake material. The reviewer's own copy, which ends with lessons for the reviewer's skills, is archived with the other outside reviews on the evidence branch under `docs/outside-reviews-2026-11-17/` |
