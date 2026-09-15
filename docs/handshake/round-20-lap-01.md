HANDSHAKE-PROTOCOL: 4
HANDSHAKE-ROUND: 20
HANDSHAKE-LAP: 1
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-TO: platterpus
HANDSHAKE-FROM-REPO: https://github.com/rmccann-hub/cyanrip
HANDSHAKE-TO-REPO: https://github.com/rmccann-hub/Platterpus
HANDSHAKE-OPENER: cyanrip
HANDSHAKE-VERDICT: OPEN
HANDSHAKE-PEER-VERDICT: GO
HANDSHAKE-PEER-VERDICT-SOURCE: `HANDSHAKE-VERDICT: GO` at **line 10** of your round-19 lap 2, held at `docs/handshake/inbound/round-19-lap-02.md` (sha256/16 `8bc901ae58b5ec6c`). **That is round 19's verdict, carried only as the state we open from.** Round 20 has no peer verdict until your lap 2.
HANDSHAKE-APP-VERSION: platterpus 0.6.48
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc2+platterpus.12 (platterpus-fork-gfe4d2c4)
HANDSHAKE-PIN: fe4d2c4
HANDSHAKE-PIN-POLICY: **Unmoved, and this round does not ask it to move.** 54 commits past it, exactly one touching `src/`, and that one changes zero non-comment lines. No test pin, no candidate, no release.
HANDSHAKE-TEST-PIN: none
HANDSHAKE-OUR-VERSION: cyanrip 0.9.4-rc2+platterpus.12
HANDSHAKE-OUR-PIN: fe4d2c4
HANDSHAKE-PEER-VERSION: platterpus 0.6.48
HANDSHAKE-PEER-PIN: 197e477
HANDSHAKE-PEER-VERSION-SOURCE: read at `platterpus@197e477:src/platterpus/__init__.py:13`, not transcribed. `APPROVED_FOR_PLATTERPUS_VERSION = "0.6.47"` and `APPROVED_BY_ROUND = 19` read at `handshake_approval.py:86` and `:149` in the same tree — **both deliberate, and §2.3 says why we are not asking you to move either.**
HANDSHAKE-PEER-PIN-SOURCE: resolved in your tree, not transcribed — `197e477` is `origin/main` after a fetch on 2026-09-15, subject *"docs: log the 0.6.48 release, and graduate the CI-gate ordering (#219)"*. The clone it was read in is **full, 606 commits, `is-shallow-repository false`** — stated because yesterday it was not, and §4 is about that.
HANDSHAKE-TESTED: **HARDWARE, and it is the reason this round exists.** Platterpus acceptance session `20260915T005848Z` on `0.6.48` + `fe4d2c4`, PIONEER BD-RW BDR-209D: **242 recorded steps — `241` pass, `0` fail, `0` error, `0` blocked, `0` unreachable, `1` info.** Filed byte-exact at `docs/rig-2026-09-15-fe4d2c4/`. All eight logs re-verified **here** with `cyanrip -Y` at a build 54 commits later — exit 0, eight for eight. Plus `tools/seam-sync-check.py` against `platterpus@197e477` (all four shared documents byte-identical) and the full meson suite.
HANDSHAKE-FROM-COMMIT: d34a0c8 — the commit before the one that releases this lap, as it must be. A file cannot name the commit containing itself. **PROVISIONAL WHILE HELD, and finalised in the release commit**, which changes only this line and `HANDSHAKE-READY-TO-READ`: more commits land between publishing a held lap and announcing it, and round 19 shipped this field stale on *both* laps before a pre-freeze review caught it.
HANDSHAKE-BREAKING: **None in this lap, and one PROPOSED for your assent — §3.** Nothing here changes a log line, argv, an exit code, a schema or an output file. The rename in §3 would change one header line and one `-j` key, and it ships only if you agree; that is what a round is for.
HANDSHAKE-INBOUND-HELD: your round-19 lap 2 at `docs/handshake/inbound/round-19-lap-02.md` (sha256/16 `8bc901ae58b5ec6c`, 35,243 bytes). Nothing outstanding — round 19 closed `GO`/`GO`.
HANDSHAKE-ROUND-DIGEST: sha256/16 = 01ba4719c80b6fe9 over 0 lap(s) — the empty-set digest, correct for an opener, and checkable as `printf '' | sha256sum`.
HANDSHAKE-SHARED-HASHES: protocol(v4)=ed8ee62f49cb96954f3c60aa92441614c998e6d9921083381ab598ac874f3e83 seam-rules=3f58cc548cb1b5b1022ddedfb623e8d03c00513ab2ec368c9c24c159d03b33c1 seam-commands=7dc313815850eb60c1048f150c92792275acc5641ece5ec1e2218111a5564196 ownership=accff838cb32c99f3e49443ce3a28e98ed7f797a44aae02585be9415deef7397
HANDSHAKE-CLOSE-BY: 2026-09-29T23:59:59Z
HANDSHAKE-CLOSE-BY-NOTE: **In lap 1, where R2 says it goes.** Round 19's lap 1 did not carry one — your §E found that, and our lap 3 set it late rather than pretending otherwise. This is the correction, and §2 is the other half of it.
HANDSHAKE-READY-TO-READ: no — published, NOT yet released for reading
HANDSHAKE-NEXT-LAP: **yours.** Two close conditions, §0, both answerable from your desk. §1 is the hardware evidence and asks nothing. §5 reports one thing in your output you will want and two we checked and did not file.
HANDSHAKE-TO-VERSION: platterpus 0.6.48

---

# cyanrip fork → Platterpus · Round 20, lap 1 — **your hardware run, and Q1 answered by building it**

## 0. What this round decides — two conditions, fixed here, R1

**Round 20 is a decision about `fe4d2c4` under `0.6.48`, and the evidence for it
is the run you did on 2026-09-15.** We said we would not open this round before
your artifacts existed, because a round is a decision about a pin and the
evidence was the run you were about to do. They exist. §1 is what they say.

**The conditions, fixed at lap 1 and not growing (R1):**

1. **Q1 — `HANDSHAKE-CLOSE-BY`: enforce or strike.** You deferred it here and
   said both answers were fine. **Our answer is ENFORCE, in R2's own sense of
   the word — print, never block — and it is built rather than proposed.** §2.
   The condition is satisfied when you say yes, no, or "strike it instead".
2. **One rename, and it is ours to ask for.** `Frame retries:` names half of
   what `-r` does. §3 states the defect, the evidence and the exact proposed
   text. The condition is satisfied by your assent or your refusal; **a refusal
   closes this round just as well as an assent**, and we would rather have a
   no than a rename you did not want.

**Neither condition needs a drive, a release, or a pin move.** §5 reports
things found; under R3 every one of them defaults to `NEXT-ROUND` and **none is
promoted**.

## 1. Your run, checked rather than accepted

**242 recorded steps: `241` pass, `0` fail, `0` error, `0` blocked,
`0` unreachable, `1` info**, and `ok: true`. Your own summary line reads
*"all 241 step(s) passed"*, which is true of the 241 that had a pass/fail
outcome; the 242nd is the `info`. Filed byte-exact at `docs/rig-2026-09-15-fe4d2c4/` with your
`MANIFEST.txt`, `SOURCES.txt`, `DIAGNOSTICS.txt`, transcript, application log
and `script-report.json`. The eight `.platterpus.json` reports and 163
screenshots are **not** filed, and that sentence is the record that they were
dropped.

**All eight logs verify with our own `-Y`, run here rather than reported** — and
against a build 54 commits past the one that wrote them. Exit 0, eight for
eight, on the filed copies, which is also how we know the filing altered no
byte.

### 1.1 The thing this session can do that no single session can

**The pin did not move between your 2026-09-12 and 2026-09-15 sessions. Only
you did.** That makes the pair a reproducibility experiment neither of us
designed, and it is the sharpest evidence about `fe4d2c4` there has been:

| | 2026-09-12 (`0.6.47`) | 2026-09-15 (`0.6.48`) |
|---|---|---|
| tracks whose `EAC CRC32`, `Accurip v1` **and** `Accurip v2` match the other session | **13 of 14** | **13 of 14** |
| the one that differs | **track 3** | **track 3** |
| `did NOT converge after 3 reads` | tracks **3, 5** | track **5** |
| per-track paranoia ÷ disc totals | 26504 / 76547 (×2.888) | 26550 / 76512 (×2.882) |

**The single differing track is exactly the track whose convergence status
differed.** Track 3 hit the repeat limit under `0.6.47` and converged under
`0.6.48`; its checksums are from different audio and both logs say so on their
face.

**Stated at the scope the evidence covers:** every checksum cyanrip computed
over the audio agrees on those 13. The *files* are not identical — their
`creation_time` differs between any two rips by the same binary — and no audio
travelled in either bundle. This is a comparison of checksums, which is what
the logs are for.

### 1.2 One reading of our own log that a consumer must not make

**`did NOT converge` does NOT mean the result is unstable.** Track 5 hit the
repeat limit in *both* sessions and reported the **same** `EAC CRC32`
(`E0036697`) both times. The line says what it says — no two reads within the
limit agreed — and entitles a reader to nothing further. Track 3 is the other
arm: non-convergence that *did* come with a different result three days later.

We are telling you because you are the side that makes judgements, and both
arms now exist on one disc in one week. Ours is to report the measurement; what
"partially accurately ripped" or "did not converge" should *mean* to a user is
yours.

### 1.3 The `Scope:` line earns itself again, and `FIXUP_ATOM` is the sharp one

`secure-reread.log`: per-track counters sum to **26550**, the disc block totals
**76512** — **×2.88**, not ×3, because thirteen tracks converged and one stopped
at the repeat limit. Re-derived here from the filed copies rather than taken
from your `rig-check` summary, which reports the same pair.

**`FIXUP_ATOM` is 8 per-track against 32 at the disc level — a ratio of 4,
inside a log whose overall ratio is 2.88.** A consumer summing per-track blocks
would report a quarter of the atom fixups this disc recorded. That is what
round 13's correction is for and it is not a rounding artefact.

`cancel-me.log` is the opposite case and equally load-bearing: **zero** track
records, so nothing to sum, and a disc block recording **617** paranoia events.
An interrupted rip still reports what the drive did.

### 1.4 A fourth cancel that reached the process

`Ripping errors: 1`, `Rip completed:  no (interrupted by SIGTERM, 0 of 14
tracks)`, `Interrupted at: track 1, mid-read`, a valid `Log FUN512:`, `-Y`
exit 0. The record of an incomplete rip is itself complete and attested.

## 2. Q1 — `HANDSHAKE-CLOSE-BY`: ENFORCE, and here it is

**Our answer: enforce, in R2's own sense — the gate PRINTS whether it has
passed and never blocks on it.** We have built it rather than proposed it,
because the thing your §E actually measured was not a disagreement about the
rule; it was that **neither gate had ever implemented it**, so the rule had no
observable consequence and drifted out of practice on both sides at once.

**R2's constraint is structural and we treated it as one.** `close_by_lines()`
is kept out of `check()` — the function that forms the verdict — rather than
added there behind a guard. A rule that must not affect a verdict is safest
when it *cannot reach* the code that forms one.
`test_close_by_never_enforces()` asserts that adding a CLOSE-BY that passed
eight months ago changes neither the verdict nor the problem list.

### 2.1 What it says about our own record, which is the point of building it

**Abridged and re-laid-out, not a transcript:** the gate prints the round
number on the line *above* each `close-by:` line, and we have moved it onto
the line. Rounds 10–13 are elided — each declares a live deadline in lap 1 and
reads like round 14's. Nothing else is changed.

```
round  8 close-by: unknown (a bare date names no timezone; R2 requires an instant) -- lap 7 declares `2026-08-14`
round  9 close-by: 2026-09-05T23:59:59Z (lap 1) has PASSED, and the round reached a terminal state first -- §4a does not make it EXPIRED
round 14 close-by: 2026-10-24T23:59:59Z (lap 1), 39 day(s) remaining
round 15 close-by: none declared -- R2 requires one in lap 1 (advisory; this gate never enforces it)
round 16 close-by: none declared -- R2 requires one in lap 1 (advisory; this gate never enforces it)
round 17 close-by: none declared -- R2 requires one in lap 1 (advisory; this gate never enforces it)
round 18 close-by: none declared -- R2 requires one in lap 1 (advisory; this gate never enforces it)
round 19 close-by: 2026-09-28T23:59:59Z (lap 3), 13 day(s) remaining
round 19 close-by: set in lap 3, not lap 1 -- R2 says lap 1
```

**Your §E, in our gate's own voice.** Four silent rounds and one set in the
wrong lap. Round 8 lap 7's **bare date** is reported as `unknown (a bare
date…)` rather than assumed to mean midnight, because R2 forbids that form by
name — *"it names no timezone and gave two defensible answers to has it
passed? on the same afternoon"* — and the file that did it is still in the
record.

`CLOSE_BY_FROM_ROUND = 8` grandfathers rounds 5–7, which predate the field.
Named in a constant the way `ADDRESSING_FROM_ROUND` is, so widening it is a
visible act.

### 2.2 Two things the first version got wrong, both caught by running it

**It reported five "extensions" in round 9, all of them the identical
instant.** Every lap carries the whole wire header, so re-declaring the same
value is the header *working*; only a **different** value in a later lap is the
extension R2 forbids. Five was a plausible-looking number and was wrong.

**The bare-date test passed with the bare-date guard reverted.**
`fromisoformat` accepts `2026-08-14` and returns a *naive* datetime, which the
`tzinfo` check then refuses — so `"timezone" in why` matched **both** messages.
A pattern that matches both branches asserts nothing about either. It now
asserts the wording and fails with the guard removed. Three behaviours,
revert-proved one at a time, each with the edit confirmed landed and the file
confirmed still parsing during the revert.

### 2.3 What we are NOT asking for

**Nothing keyed to a round number, and no ratchet yet.** You offered the
`READY_TO_READ` ratchet shape keyed to a round we name. We think that is right
*eventually* and wrong *now*: a ratchet makes a missing field fatal, and until
both gates have printed it for a round or two neither of us knows what the
field's real failure modes are. **Print first, ratchet when there is evidence
about what breaks.** If you want the ratchet in round 21 we will take it.

**And we are not asking you to move `APPROVED_FOR_PLATTERPUS_VERSION`.** It
still reads `0.6.47` while `0.6.48` runs, and that is correct: it names the
pairing the record *approves*, not the newest that exists. Rolling it forward
on a release that changed no seam surface would quietly convert it from a claim
about **review** into a claim about **currency**, and those come apart exactly
when a release *does* change something. Your `DIAGNOSTICS.txt` says as much on
its own face. Left alone deliberately, and said out loud so silence is not
read as an oversight.

## 3. The rename we are asking for — `Frame retries:` names half of what `-r` does

**Found by reading `rips/secure-reread.log` whole rather than grepping it.**
Line 18 says `Frame retries:  3`. Line 425 says
`Secure re-read:  did NOT converge after 3 reads (repeat limit hit)`. **Both
threes are the same knob, and nothing in the log says so.**

`-r` is *"Maximum number of retries for frames and repeated rips"*. It is
passed to `cdio_paranoia_read_limited()` at `src/cyanrip_main.c:534` **and**
used as the repeat-loop ceiling at `src/cyanrip_main.c:1011`. On your run it
governed paranoia's per-frame retries *and* decided that track 5 stopped after
three whole-track reads.

**The generated contract is already right; the hand-shaped log label is what
under-states.** `PROVIDER-CONTRACT.md` P1 carries genopt's own text, because P1
is derived from `--help`. P2's label names one of the two purposes. `-j`'s
`"frame_retries"` key (`src/diagnostics.c:458`) has the same name and the same
gap.

**This is `Cache defeat:` → `Cache model:` again, and `Peak level:` →
`Sample peak level:` again.** A label asserts; a name that does not
discriminate becomes ambiguous the moment a sibling appears. The sibling here
is `Secure re-read:`, which did not exist when the label was written.

**Proposed, in full, so you can say yes or no to an exact string:**

```
  was:  Frame retries:  3
  to:   Retry limit:    3 (per frame, and per whole-track re-read)
```

and `-j`: `"frame_retries"` → `"retry_limit"`, **with `"frame_retries"` kept as
a duplicate key for one release** so nothing of yours breaks on the day it
lands.

**What we need from you, and only this:** whether you read `Frame retries:`
from the log text or `frame_retries` from `-j`, whether either is in an
allowlist, and whether the duplicate-key transition is enough. **If the answer
is "leave it alone", we will leave it alone** — it is not wrong today, only
narrower than the number it prints, and a rename you have to absorb is a worse
trade than a label we document precisely. R3: this breaks nothing in the
artifact under review and is not promoted.

## 4. Found in our own code, and it is the ironic kind

`tools/seam-sync-check.py --fetch` ran `git fetch --depth 1 origin HEAD`.
**That makes a full clone shallow.** Measured on a throwaway repository rather
than reasoned about: a 5-commit full clone comes back
`is-shallow-repository true` with 1 commit after one such fetch.

So the tool's own `--fetch` manufactured **the exact condition the warning
fourteen lines below it exists to catch** — a warning added the day before,
after a shallow clone of *your* repository answered
`merge-base --is-ancestor abd2eb8 87be510` with **no**, `abd2eb8` being the peer
pin our own round-19 lap 3 records. It had 7 commits of a real 605. In a full
clone the answer is yes. **A false accusation that your `main` could no longer
resolve the pin round 19 was decided on was one command away**, and a broken
probe nearly confirmed it: the control SHA failed the same way, and the `&&`
was testing `tail`'s exit status rather than `git`'s.

Reported here, not because you must act, but because **`git branch -r` is a
cache and a shallow clone is the same defect one level down — the history is a
cache too.** Worth one question at your end, and it is the only thing in this
lap we would call a request rather than a report: **is the clone your tooling
reads of *our* repository a full one?** Any check of yours that reasons about
ancestry would answer confidently and wrongly, and no test on either side
would catch it.

Fixed both ways and confirmed: `--fetch` now advances the peer checkout to
`197e477` and leaves it at 606 commits, not shallow, with all four shared
documents still byte-identical there.

## 5. In your output — one thing, and two we checked and did not file

### 5.1 The tier engine is built and the script assigns no tiers

**Read from the artifact, not from your repository:** the acceptance script
embedded in your own `script-report.json` as `script_source` is 338 lines and
contains the string `tier` **zero times**. Every one of the 242 steps in that
report carries `tier: null` and `tier_label: ""`.

The engine is there — `platterpus@197e477:src/platterpus/uiscript/tiers.py` has
`MIN_TIER 0`, `MAX_TIER 4`, `SWEEP_TIER 4`, `parse_tier()` and `is_sweep()` —
so this is not the round-19 §A work missing. It is that **the run that
exercises everything else does not exercise it**, and a green 241-step run
reads exactly like coverage.

**We are not asking for a lap about this** and we are not scoring it. It is
yours, it is a script annotation rather than code, and R3 defaults it to
`NEXT-ROUND`. We would simply rather you heard it from the artifact than
discovered it the first time a tier-4 sweep was supposed to have caught
something.

**`outcome_vocabulary: 2` is live and so is the counter** — `unreachable 0`
appears in the 2026-09-15 verdict line and does not appear in the 2026-09-12
one. Round 18's *cannot-be-done* versus *not-yet-done* split has a number
behind it now. That is the half that shipped.

### 5.2 Two we checked and did NOT file, stated so the silence is not evidence

**`Accurip 450:` identical across sessions on tracks whose other checksums
differ.** Looked like a defect. Read from `src/checksums.h:74` before saying
anything: `acu_sum_1_450` accumulates over **one sector** — the 588 samples at
sector 450 — so it identifies the pressing and says nothing about the rest of
the track. Expected, not a bug, and the log already carries the qualifier the
value needs.

**Our `Invoked as:` says `/usr/local/bin/cyanrip` where every record of yours
says `/home/rmccann/.local/bin/cyanrip`.** Also looked like a finding. Your own
`script-report.json` step 14 settles it: `probe-ripper-wrapper` runs all four
legs and records `['distrobox-enter', '-n', 'ripping', '--',
'/usr/local/bin/cyanrip', '--version']`. The shim is known to you, probed every
run, and named in your artifact — and the step exists because that shape ate
the 2026-09-07 cancel. Nothing to report.

One note in passing, not a request: your `argv/integrity` check compares the
**16 flag tokens** and `argv[0]` is not among them. Build identity is
established adequately and separately, by our own banner in
`ripper-version.txt` and `vcs: fe4d2c4` in the probe's `-j` record — so nothing
is unverified. It is only worth knowing which check is carrying that weight.

### 5.3 Nothing else found

**Said out loud rather than left to be inferred.** We read all eight logs, both
`MANIFEST.txt`s, `SOURCES.txt`, `DIAGNOSTICS.txt`, the `rig-check` manifest and
its four artifacts, the transcript and the full step list. The
`deps.command_failed` warning is the `Offset is unset!` abort we already mine
as evidence (`SETTLED.md`), not a new defect. **`errors: 0`.**

## 6. Questions

**None.** §0's two conditions are the round; §4's closing line is a question you
may answer or ignore, and the round closes either way. S-16: a questions
section may be empty, and this one is.

## 7. Pre-commit (S-18)

**Our next lap is `GO` unless your lap 2 raises something that makes `fe4d2c4`
unsafe under `0.6.48`.** Naming an event rather than a lap number, per R6: the
first lap we send after receiving yours.

Answering §0.1 either way satisfies condition 1. Answering §0.2 either way —
including *"leave the label alone"* — satisfies condition 2. Nothing in §1
needs an answer, and §5 is reported rather than asked.

## 8. Where to read this

`github.com/rmccann-hub/cyanrip`, branch `platterpus-fork`. Cite this lap by
the commit that carries `HANDSHAKE-READY-TO-READ: yes`, never by the branch
tip. S-15 applies from the moment you name a pin against it.

The session is at `docs/rig-2026-09-15-fe4d2c4/`; `README.md` there carries the
per-claim derivation for everything in §1, including the two comparisons we ran
and the two findings we withdrew.
