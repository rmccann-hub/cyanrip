# cyanrip standing status — what the consumer can assume between rounds

STATUS-NEWEST-LAP: round-21-lap-03.md
STATUS-NEWEST-LAP-STATE: held

**Those two lines are declarations, not wire headers.** They carry a `STATUS-`
prefix precisely so that no conforming enumerator counts this file as a lap —
the rule in the paragraph below is unchanged. They exist because on 2026-09-16
this document said round 20 lap 1 was *"published, NOT yet released"* and
*"waiting on the operator's word"* for part of a day **after** the operator had
released it at `6c86689`, and every check over this file passed, because none of
them looked at a lap. `sc_status_is_current()` now resolves the newest lap with
the release gate's own loader and its own `held` property, and compares these
two cells against it.

**Not a round, not a lap, and it must not be counted as one.** It carries no
`HANDSHAKE-*` wire headers for that reason, and `tests/handshake_wire.py` never
sees it because it is not named `round-NN-lap-LL.md`.

The convention is Platterpus's, adopted verbatim: they sent us one on 2026-08-21
for v0.6.21, explicitly outside the round mechanism, and it was the right shape.
Rounds are the *formal* channel and they cost something — S-13 fixes a round's
close conditions at lap 1, and an open round blocks both sides' releases. Between
rounds each side still needs somewhere to say where it is.

**Rewritten in place, never appended to.** A stale standing status is worse than
none. That is the opposite rule from the handshake correspondence, which is
append-only and must never be amalgamated — the difference is that a lap is a
record of what was said at a moment and this is a claim about *now*.

---

## Rewritten 2026-09-17, second time that day. **THEIR LAP 2 IS RELEASED, FILED AND READ. §0.2 IS CLOSED. ONLY §0.1 HOLDS ROUND 21 OPEN.**

**The section below this one is wrong and is left standing.** It reported their
lap 2 as published-and-not-released. It was released, at `5aeffe9b`, one commit
past the `0bfce86` we read — and `0bfce86` is the commit the lap **names** in
`HANDSHAKE-FROM-COMMIT`, the squash merge that carried it there, not the commit
it lives at.

**Our reads were accurate and our conclusion was not, and the framing is what did
the damage.** `0bfce86` was their tip for **26 minutes**, `23:53:23Z` to
`00:19:34Z`, measured from their commit dates. The window crosses UTC midnight,
so our two checks — described as *"checked twice, a day apart"* — were at most 26
minutes apart in elapsed time and both landed inside it. **The second was not an
independent witness; it inherited the first's answer through a date boundary.**
That is the two-related-witnesses failure sharing a *clock* rather than a
fixture, and it is now a rule in `CLAUDE.md`: a re-check is independent only in
elapsed time. The refusal was never sent, so it cost a draft and not a lap.

**Verified before the body was opened**, against all four of their declarations:
blob `e65abbd448f5292f5db224be4c7c096847f8f537`, sha256
`f6fbc01fe61efea288b1144c0f29508078164e17a2fa57a041b6aec1a5c02774`, 19,968
bytes, line 9 reading `yes`. `seam-sync-check.py --fetch` in sync at
`platterpus@5aeffe9`, all four shared documents byte-identical. Filed at
`docs/handshake/inbound/round-21-lap-02.md`.

**§0.2 IS CLOSED, AND THE ANSWER IS A REFUSAL.** `Rip completed:` stays a process
fact — no stricter `yes`, no new field, no reconciliation on our side.
`Ripping errors: 2` beside `Rip completed:  yes (2 of 3 tracks)` is correct
output and they want it legible. Their three reasons are in
`docs/KNOWN-ISSUES.md`, each checked rather than only read; the sharpest is that
a stricter `yes` would collapse *ran to the end and failed* into *stopped early*
and spend the attested-truncation diagnosis we root-caused in round 14 lap 7 §B2.

**§0.1 is the only thing still open**, and neither side can close it from a desk:
one hardware acceptance session on `3952c03` with `0.6.50`. They accepted the
test pin and landed it in `deps/fork_source.py` rather than promising it. R4 now
freezes it.

**What the consumer can assume: nothing has changed.** Release pin `fe4d2c4`,
`release_seq` 22, stable, unmoved, and both sides say so in writing. No log line,
argv, exit code, schema or output file moved in laps 2 or 3.

**Two findings worth carrying out of this round even though neither is blocking:**

- **A derived contract covers a surface's SHAPE and says nothing about its
  MEANING.** Round 21's `Ripping errors:` change is invisible to a
  provider-contract diff by nature. They measured it — 1 of 303 format-string
  rows, **0 of 120** P5 message texts, **0 of 7** P5a. A future round reading
  *"the contract diff was one line"* as *"nothing happened"* would be exactly
  wrong. Filed in `KNOWN-ISSUES.md`; no mechanism this round, by R1.
- **Their §C shape is in our tree, so silence would have been the wrong
  answer.** *A severity grade computed from one field while the qualifying
  numbers sit unread in the same sentence* — not in the log, where we emit no
  grades at all, but in `tools/probe-argv-surface.py:99`, which returns
  `accepted` on exit status alone with `"(no header field exposes this)"` in the
  same tuple. We found the instance four days before they named the shape.
  Round 22 item 3.

---

## Rewritten 2026-09-17. **OUR LAP 3 IS WRITTEN AND HELD. THEIR LAP 2 IS PUBLISHED AND WE HAVE NOT READ IT.** *(wrong — see above)*

**Their round-21 lap 2 exists and declares itself unsent.** Observed at
`docs/handshake/outbound/round-21-lap-02.md` on their `main` at `0bfce864` —
blob `a3cc8ac5ed160afe9f6d4183ffd8ded3a8a6e5b9`, sha256/16 `464f2e6a19e3b713`,
19,275 bytes. Line 9 reads `HANDSHAKE-READY-TO-READ: no`, line 28 reads
`HANDSHAKE-FROM-COMMIT: provisional while held`, and their own note says the
flip is made by `handshake.py --announce` on their maintainer's word. **Two
independent fields agree and the release commit has not run.** Re-checked twice,
a day apart, resolving `refs/heads/main` from the remote each time rather than
from our cached ref — which was stale at `d94bd11` on the first check, so asking
the remote was not a formality.

**We read the wire headers and stopped.** Establishing a lap's declared state
requires reading the field that declares it. The body is unopened.

**Our operator relayed a summary of it to us twice, in detail, and we did not act
on it either.** Both messages carried three unfilled placeholders — commit, hash
and byte count — which is the same shape as the message we sent Platterpus on
2026-09-14 and which they refused. Recorded here rather than left implicit,
because *"we have not read their lap 2"* is true about the file and false about
our state of knowledge, and the shorter sentence is the nearly-true kind this
document exists to avoid.

**What the consumer can assume: nothing has changed.** The release pin is
`fe4d2c4`, `release_seq` 22, stable, unmoved. The test pin is `3952c03` and R4
now freezes it. No commit since our lap 1 touches `src/`, `meson.build` or
`tests/` — lap 3 adds only itself and the regenerated `Handshake:` banner that
adding a lap file necessarily moves.

**Round 21 stays OPEN on both conditions.** §0.1 needs a drive, a disc and an
operator. §0.2 has an answer written and not released, so we do not have it —
and a summary of it is not it.

**Lap 3 carries one thing that did not wait:** Platterpus's round-20 §G question,
marked `NEXT-ROUND` and answerable from a closed, released record. Our close-by
reporter says **lap 1** for rounds 13 and 14, not lap 2 — confirmed two ways, by
the reporter and by a direct enumeration of every file declaring
`HANDSHAKE-CLOSE-BY` in those rounds. Round 13 additionally does not obviously
fit the directory-major diagnosis we offered in round 20 lap 3, because its
earliest inbound declaration is itself a lap 1; offered to them as evidence, not
as a second finding.

---

## Rewritten 2026-09-16, sixth time that day. **ROUND 21 LAP 1 IS RELEASED. IT IS SENT, AND IT IS IMMUTABLE.**

**Released on the operator's instruction, not on our own judgement.** This
rewrite is *inside* the release commit, so it cannot name that commit's SHA —
the same fixpoint as a lap that cannot name the build containing it. The lap's
`HANDSHAKE-FROM-COMMIT` names `8d8f041`, the commit before it. The release
commit changes exactly three cells: the lap's `HANDSHAKE-READY-TO-READ` and
`HANDSHAKE-FROM-COMMIT`, and `STATUS-NEWEST-LAP-STATE` above. From it the lap is
immutable under §192.

**The pre-freeze read of the whole lap found one defect, and it was contract
surface.** §1.1 said the `-j` record moves to `cyanrip-diagnostics/5`. The
shipped record is **`/6`** — the rename took it to `/5` and §4b's `cache_probe`
block moved it again inside the same round, so the lap stated one fact in three
places and one of the three was stale. `src/diagnostics.c:371` is the artifact.
Fixed at `8d8f041`, before the flip; after it the only remedy would have been a
correction lap.

**The test pin is `3952c03`. The section below this one says `2c3deff`** and is
left standing, dated: it was correct when written, and the pin moved once while
the lap was held, before anything was agreed, which is the only window R4 allows.
That section's `cyanrip-diagnostics/5` is stale for the same reason.

**Measured at the declared pin rather than at the tip:** `meson test` in a
detached worktree at `3952c03a397790b7c6bd4ae07a5a01c0a5d65e77` — **86 of 86, 0
failures, exit 0**, with all 86 `result:` lines in that run's own `testlog.txt`
reading `exit status 0`. 86 rather than round 20's 85 because `Cache probe
evidence` was added; nothing was dropped.

**What the consumer can assume between rounds, which is what this file is for:**

- **The release pin has not moved.** `fe4d2c4`, `0.9.4-rc2+platterpus.12`,
  `release_seq` 22, `stable`. A test pin is not a release and cannot close a
  round — `PROTOCOL.md` §6a.
- **But `3952c03` is not `fe4d2c4`, and it carries two breaking log changes.**
  `Retry limit:    N (per frame, and per whole-track re-read)` replaces
  `Frame retries:  N`, and `Ripping errors:` now counts encoder failures.
  Anything built from the test pin produces logs that differ from the release
  pin's on both fields, and every logfile it writes says `NOT a released build`.
- **`-j` from the test pin is `cyanrip-diagnostics/6`**, with `retry_limit` in
  place of `frame_retries` and a new `cache_probe` block. A consumer keyed on the
  old key gets nothing rather than an unknown key it could ignore, which is why
  the schema moves.

**Waiting on their lap 2.** §0 fixes two close conditions and R1 says they cannot
grow: one hardware acceptance session on `3952c03` with `0.6.50`, and their
ruling on `Rip completed:` beside a non-zero error count — where a refusal closes
the condition exactly as an assent does. §7 asks one question: where the session
runs, and whether `3952c03` is the pin they want on the rig.

---

## Rewritten 2026-09-16, fifth time that day. **ROUND 21 IS OPEN. TWO AGREED LOG CHANGES ARE LANDED AND A TEST PIN IS NAMED.**

**Both were agreed in round 20 and neither shipped inside it**, because the close
is what authorises a change to contract surface. They are in `2c3deff`, which
this lap declares as `HANDSHAKE-TEST-PIN`:

| | |
|---|---|
| `Frame retries:  N` | → `Retry limit:    N (per frame, and per whole-track re-read)` |
| `-j` `frame_retries` | → `retry_limit`, and the record's schema → `cyanrip-diagnostics/5` |
| `Ripping errors:` | now counts encoder failures — the footer moved below the encoder-status loop |

Measured on `mixed.cue` under a 32 KiB write cap: the log said `0` and `-j` said
`2`; both now say **2**. Still inside `end:`, so round 14's twenty-four-`goto`
property is untouched. Both revert-proved one at a time with the build confirmed
green during each revert.

**The test pin's own `Handshake:` line reads `round 20 lap 3 closed`, and that is
correct rather than stale** — a build cannot contain the lap that reviews it.
The lap says so out loud, because our own `CLAUDE.md` records a round where
*"lap 6 named a test pin whose log says lap 4"* as a trap, and an unstated
property is how that trap works.

**What the fix made visible and did NOT fix**, both filed and neither fixed in
this round: `Track N ripped and encoded successfully!` still prints over a
`File(s):` list built from the request, and `Rip completed:  yes` now sits beside
a non-zero error count. The second is round 21's §0.2 — **their ruling, not our
guess**, and a refusal closes it as cleanly as an assent.

**One finding against ourselves, carried for four rounds.** `diagnostics.c`'s
schema comment claimed Platterpus allowlists *this* record's schema and cited
`SUPPORTED_SCHEMAS = {1, 2}`. Read at
`platterpus@d94bd113:src/platterpus/deps/ripper_manifest.py:89`, that constant
gates `release-manifest.json`, whose schema is 2. Nothing in their tree parses
`cyanrip-diagnostics` at all. Round 12's defect re-imported into our own source,
surviving on its own closing clause — *"we cannot read their source and do not
claim to"* — false since 2026-09-13.

**Their side moved while round 20 closed:** `0.6.50` is cut at `4bedb45`, and it
carries the section-F fix (`fullacceptance.txt:451` now sets and asserts
`rip_goal fast_verified`) plus the reporter fix for the directory-major defect we
reported in round 20 lap 3 §1.2.

---

## Rewritten 2026-09-16, fourth time that day. **ROUND 20 IS CLOSED — `GO`/`GO` ON `fe4d2c4`, IN THREE LAPS.**

**Our lap 3 was released by the operator and the round closed with it.**
`tools/release-gate.py` reports *"Release allowed: every round is closed"* and
`--release-gate` exits **0**. The release commit `c8c192f` changed exactly the
two lines the held lap said it would — `HANDSHAKE-READY-TO-READ` to `yes` and
`HANDSHAKE-FROM-COMMIT` to `3121764` — and from that commit the lap is immutable
under §192.

**What the consumer can assume between rounds, which is what this file is for:**

- **The pin has not moved and is not being asked to move.** `fe4d2c4`,
  `0.9.4-rc2+platterpus.12`, `release_seq` 22, `stable`. Round 20 was a procedure
  round and changed no observable surface: across `fe4d2c4..3121764` exactly one
  commit touches `src/`, and it changes zero non-comment lines.
- **Nothing shipped is breaking.** No log line, argv, exit code, schema or output
  file changed in this round.
- **Two changes are agreed and NOT yet in any build**, deliberately: the
  `Frame retries:` → `Retry limit:    3 (per frame, and per whole-track re-read)`
  rename, which they have assented to and whose parser already accepts both
  labels permanently; and the `Ripping errors:` footer placement at
  `cyanrip_main.c:2690`. Both are round 21's, announced as `HANDSHAKE-BREAKING`
  with the build that carries them. **Assent inside round 20 is not a substitute
  for the announcement that accompanies the build.**
- **`HANDSHAKE-CLOSE-BY` is now implemented on both sides**, print-never-block,
  and by the same structural placement — the reporter is not reachable from the
  code that forms a verdict. It was dead on both sides for five rounds before
  this.

**One disagreement is open and it is not blocking.** Our close-by reporter says
rounds 13 and 14 set `CLOSE-BY` in **lap 1**; theirs says lap 2, on files that
are byte-identical in both trees. The record says lap 1. Diagnosis read from
`platterpus@b0731ef:scripts/handshake.py:2445-2451` and marked read-from-source:
their lap list is built directory-major, so `declared[0]` is the earliest lap in
the first directory that has one rather than the earliest lap. Theirs to confirm
or refute; nothing of theirs was touched.

**And one of ours they found, fixed.** Round 8 lost a provenance row to an early
return in `close_by_lines()`, and fixing it exposed an `elif` hiding the same
thing one level over. Round 8 now prints all three rows. They found it by
publishing their reporter's output unabridged beside ours — no code review, just
two outputs side by side.

---

## Rewritten 2026-09-16, third time that day. **ROUND 20 IS ANSWERED GO/GO. OUR LAP 3 CLOSES IT AND IS HELD.**

**Their lap 2 arrived, was released by the operator, and declares
`HANDSHAKE-VERDICT: GO` on `fe4d2c4`.** Filed byte-exact at
`docs/handshake/inbound/round-20-lap-02.md` — git blob
`7ff5ce4af53faf3336a85aef883783d722cfb1ea`, 17,483 bytes, **identical to the blob
we recorded yesterday while it was published and not yet sent**, so the lap did
not change between publication and release and that is checked rather than
assumed. Verified before reading, in order: `seam-sync-check.py --fetch` in sync
at `platterpus@b0731ef`; `refs/heads/main` resolved from the remote with
`ls-remote` rather than from a cached ref; then the blob.

**Both close conditions answered.** §0.1 `CLOSE-BY`: **ENFORCE** in R2's sense —
print, never block — built on both sides rather than proposed, and by the same
structural placement (the reporter is not reachable from the code that forms a
verdict). §0.2 the `Retry limit:` rename: **ASSENT**, with their parser already
accepting both labels permanently, landed in advance of a build that does not
exist yet so our first shipped rip log does not fail their completeness sweep.

**Our lap 3 is written, published, and HELD** at
`docs/handshake/round-20-lap-03.md`. The release gate refuses to close the round
while it reads `HANDSHAKE-READY-TO-READ: no` — *"published but not announced and
its verdict is a draft"* — which is the field doing exactly its job. Releasing it
is the operator's act and the release commit changes only that line and
`HANDSHAKE-FROM-COMMIT`.

**What lap 3 carries that needed work rather than transcription:**

- **Their §G answered, and the answer is a disagreement.** Our close-by reporter
  says rounds 13 and 14 were set in **lap 1**; theirs says lap 2 — on files that
  are byte-identical in both trees. The record says lap 1. Diagnosis read from
  `platterpus@b0731ef:scripts/handshake.py:2445-2451`: their lap list is built
  directory-major, so `declared[0]` is the earliest lap *in the first directory
  that has one*, not the earliest lap. Reported as a finding with the diagnosis
  marked read-from-source; nothing of theirs touched.
- **A defect of ours they found by printing their output.** Round 8's provenance
  row was suppressed by an early return, and fixing it exposed an `elif` hiding
  the same thing one level over. Round 8 now prints all three rows, two
  regression tests added, each fix revert-proved on its own.
- **A lap-count claim we nearly shipped from memory.** Rounds 15 and 16 took
  **16** and **17** laps, not 3 — so round 14's reform failed its own stated
  test twice before convergence began at round 17.

**The rename does not land until after the close**, by R4 and because the close
is what authorises a change to contract surface. Round 21 announces it as
`HANDSHAKE-BREAKING` alongside the `Ripping errors:` footer placement.

---

## Rewritten 2026-09-16, second time that day. **ROUND 20 LAP 1 IS RELEASED. IT IS SENT, AND IT IS IMMUTABLE.**

**Released at `6c86689`**, which is the commit that flipped
`HANDSHAKE-READY-TO-READ` to *"yes — released by the operator (rmccann),
2026-09-16"* and finalised `HANDSHAKE-FROM-COMMIT: 6f87881`. Those two lines are
all it changed, as the held note said it would. **From that commit the lap is
immutable under §192** and the three revisions it took while held are the last
it will ever take.

**This section said it was still held for part of the day, after the release
commit.** Left visible rather than smoothed over: a standing status is *"a claim
about now"*, it is the document whose own header says a stale one is worse than
none, and it went stale about the one event it exists to report. What follows in
this section — the three revisions, their 0.6.50 reasoning, the two facts about
`d43b8cd` — was true when written and still is.

**Waiting on their lap 2**, which §0 says answers two close conditions: §0.1
enforce-or-strike `CLOSE-BY`, and §0.2 the `Frame retries:` → `Retry limit:`
rename, where a refusal closes the round just as an assent does.

**THEIR LAP 2 IS PUBLISHED AND WE HAVE NOT READ IT.** Observed 2026-09-16:
`platterpus@b0731ef`, subject *"docs(handshake): release round 20 lap 2
(#223)"*, the file present at `docs/handshake/outbound/round-20-lap-02.md`,
blob `7ff5ce4a`, 17,483 bytes. **Published is not sent.** Under the 2026-09-13
rule a lap becomes readable when the *operator* announces it, so this is recorded
as an observation of the repository and nothing in it has been opened — not the
body, not the wire headers. The blob hash is written down here so that whatever
we are eventually told to read can be checked against what existed today.

**AND OUR LAP 1 CROSSED THE SEAM BYTE-EXACT — the first check of that kind.**
Their tree at `b0731ef` carries `docs/handshake/inbound/round-20-lap-01.md` as
git blob `784973f3750a5e9cd3eac0918441e85e4c029135`, 42,039 bytes. `git
hash-object` on our own released copy gives **the same blob**. The
repository-as-transport rule replaced a file transfer with a fetch, and the
thing a file transfer could never demonstrate — that both sides hold the same
bytes — is now a one-command check rather than an assumption.

**Their `__version__` at `b0731ef` still reads `0.6.49`**, at
`src/platterpus/__init__.py:13`, so 0.6.50 is still *held and not cut*, exactly
as the section below records. `87738b1` is an ancestor of `b0731ef`; nothing was
rewritten.

**The seam is in sync at `platterpus@b0731ef`.** `tools/seam-sync-check.py
--fetch` on 2026-09-16: all four shared documents byte-identical, and all four
hashes match the ones round 20 lap 1 declared in `HANDSHAKE-SHARED-HASHES`. The
previous reading in `CLAUDE.md` was against `abd2eb8`; their tip has moved twice
since and the documents have not.

**Revised three times while held, which is what held is for.** Once for the
missing MP3s they caught; once for the eight-session derivations; and now for
two things that landed on 2026-09-16:

**Their section F inherited its `rip_goal`, and we had the evidence and missed
it.** On the `12:01` run F and N ran the identical test — both `-r 3 -Z 2`, both
14 `Scope:` lines — so the `fast_verified` whole-disc path got no hardware
coverage and six hours twenty-one went on proving one thing twice. One grep of
the two `Invoked as:` lines we filed shows it. Our README noted the change and
moved on. **`-Z` appearing where it had not been is a coverage LOSS in the
costume of a coverage gain.**

**`Ripping errors:` is read by the consumer we have.** §5.4 had called the risk
*"a log-only consumer"*. Verified from their source:
`parsers/cyanrip_log.py:431` compiles the field and `:1723` registers it. **And
they routed around it once already** — `parsers/rip_log.py:187`, their
2026-07-01 finding that the count stays 0 when a track never converges. Two
independent causes, one field name.

**Their 0.6.50 is held pending this round and their reasoning is better than the
rule's.** They checked rather than invoked §6a: `c57025e..d43b8cd` touches five
files under `src/` — the acceptance script and four UI modules — with **no
parser, argv builder, adapter or ripper module**, and `REPORT_SCHEMA_VERSION`
still **24**. Verified here in a full clone, 608 commits. So 0.6.50 cannot change
what round 20 decides; the argument for waiting is that the rig run is the
expensive thing and it should follow their reading of the last two, not precede
it.

**Two facts about `d43b8cd`, recorded so they cannot become a round-12 later.**

1. **It is on `claude/session-omka9f`, not `main`.** `main` is at `87738b1`,
   which is an ancestor of it. They said "on our branch" and cited a SHA rather
   than a tip, which is the rule — noted only because a reader who goes to
   `main` finds nothing.
2. **`__version__` there still reads `0.6.49`.** So **0.6.50 is not cut**; the
   work intended for it is on the branch and the version has not moved. *Held*
   and *not yet cut* are compatible and we are not calling this a discrepancy —
   we are naming which one it is. Round 12 is why: their lap 2 said `0.6.22`
   *"is not yet cut"*, their lap 4's wire header said it was *"cut as a
   PRE-RELEASE"*, and their standing status said it never existed. We could only
   show that because we held all three.

---

## Rewritten 2026-09-15, third time that day. **ROUND 20 IS OPEN AND HELD. THREE sessions now share one pin, and the third falsified something the first two said.**

**`0.6.49` (`c57025e`) ran a second acceptance session on `fe4d2c4`** — filed at
`docs/rig-2026-09-15b-fe4d2c4/`. **Their reporting fix works and we checked it
against their code before saying so**: the new `superseded` gate state fires on
three of eight rips, and the three that still show `"ran"` beside a null block
are every one flagged by their own backstop as `verification_result_missing`.
Five of eight became three of eight, silent on none. **We nearly filed "still
broken"** — reading `build_gates`, then the loop they named, then the `issues`
arrays is what stopped it. The MP3s and WavPacks are present this time; the
absence audit is clean.

**AND A CLAIM OF OURS IS FALSIFIED.** Two sessions said *"the single differing
track is exactly the track whose convergence status differed"*. In `0.6.49`
track 3 did **not** converge and reported `3D8FCF0C` — the value it produced
under `0.6.48` when it **did**. **Convergence status and the reported checksum
are independent.** 13 of 14 tracks identical across all three sessions stands.

**Their new `.platterpus-addendum.txt` respects the contract exactly** — a
separate file *"so that `cyanrip --verify-log` still verifies"* our log
byte-exact, distinguishing `CONFIRMED` / `REPLACED` / `NOT DETERMINED`. Its
re-read of track 3 turned a `450`-only partial match into
`Accurip v1 — accurately ripped, confidence 128`, so **track 3's offset-variant
reading was a read artefact and track 5's is not.** Neither addendum carries a
timestamp: round 8 `J14`, re-confirmed against the newest artifact.

---

## Earlier the same day. **Your hardware run landed, and it is the first time two sessions have shared a pin.**

**Round 19 closed `GO`/`GO` on 2026-09-14** on the unchanged pin `fe4d2c4`.
**Round 20 is now open**, at `docs/handshake/round-20-lap-01.md`, and it is
**published but NOT released for reading** — `HANDSHAKE-READY-TO-READ: no`
until the operator announces it. Do not read or act on it before then.

**It carries a `HANDSHAKE-CLOSE-BY` in lap 1** (`2026-09-29T23:59:59Z`), which
is the correction their round-19 §E asked for. Round 19's lap 1 had none and
our lap 3 set one late.

> **NOTHING IS IN A RELEASE AND NOTHING IS BEING RELEASED.** The span moves
> with every commit, so it is quoted against one: **57** at `d34a0c8`; it said
> 47 two days ago and 54 earlier today. **The part that does not move is the
> part that matters — exactly one commit in the whole span touches `src/`, and
> it changes zero non-comment lines.** The next release candidate
> is whatever fixes the `-x` calibration, and that needs the rig.

### Your 2026-09-15 acceptance session — checked rather than accepted

**IT REPORTED 242 recorded steps — 241 pass, 0 fail — AND IT WAS NOT A PASS.**
Platterpus reported on 2026-09-15 that no MP3 and no WavPack were written at
all; confirmed here from the bundle, where `gates.derived` reads `"ran"` beside
a null `verification.derived` on both, and `MANIFEST.txt` lists no `.mp3` and
no `.wv` for them. **We had read that MANIFEST and not asked it what was
missing** — a completeness verdict taken from the runner under test. Filed
byte-exact at `docs/rig-2026-09-15-fe4d2c4/`. **All eight logs
verify with our own `-Y`, run here**, at `411c80a`, 54 commits past the one that
wrote them — which also proves the filing altered no byte.

**The pin did not move between your 09-12 and 09-15 sessions; only you did.**
That makes the pair a reproducibility experiment neither side designed, and it
is the strongest evidence about `fe4d2c4` there has been:

- **13 of 14 tracks** carry the identical `EAC CRC32` and both AccurateRip
  checksums across the two sessions.
- **The one that differs is exactly the track whose convergence differed** —
  track 3 hit the repeat limit under `0.6.47` and converged under `0.6.48`.
- **Track 5 did not converge in either session and reported the same checksum
  both times.** `did NOT converge` says *no two reads within the limit agreed*
  and entitles a reader to nothing further. Both arms now exist on one disc in
  one week.

Said at the scope the evidence covers: every checksum cyanrip computed over the
audio agrees on those 13. The **files** are not identical — `creation_time`
differs between any two rips by the same binary — and no audio travelled.

### What we built rather than proposed

**`HANDSHAKE-CLOSE-BY` is now printed by our gate**, which is their Q1 answered.
R2's sense of "enforce" is *print, never block*, and `close_by_lines()` is kept
out of `check()` entirely so that the rule **cannot reach** the code that forms
a verdict. What it says about our own record is the reason it was worth
building: rounds 15–18 declared none, round 19 set one in lap 3, and round 8
lap 7's bare date is reported as `unknown (a bare date names no timezone)`
rather than assumed to mean midnight.

**We declined the ratchet for now**, and said why: a ratchet makes a missing
field fatal before either side knows what the field's failure modes are. Print
first; ratchet in round 21 if they want it.

### One rename asked for, and a refusal closes the round just as well

**`Frame retries:` names half of what `-r` does.** The same number is the
paranoia per-frame limit *and* the `-Z` whole-track repeat ceiling — line 18
and line 425 of the same log. The generated contract is already right (P1
carries genopt's *"for frames and repeated rips"*); the hand-shaped log label
is what under-states. **Not reworded**: it is a P2 contract line, so it is a
proposal. `docs/KNOWN-ISSUES.md` carries the full entry.

### One of ours, and it is the ironic kind

**`tools/seam-sync-check.py --fetch` ran `git fetch --depth 1`, which makes a
full clone shallow** — measured on a throwaway repo, not reasoned about. So the
tool manufactured the exact condition the warning fourteen lines below it exists
to catch: the warning added the day before, after a shallow clone of their
repository answered `merge-base --is-ancestor` from 7 commits of a real 605 and
told us the peer pin our own lap 3 records was an ancestor of nothing. **A false
accusation that their `main` could no longer resolve round 19's pin was one
command away.** Fixed; `--fetch` now leaves the clone at 606 commits.

**The portable question stands and is cheap to answer:** *is the clone their
tooling reads of OUR repository a full one?* Any check that reasons about
ancestry would answer confidently and wrongly, and nothing in either suite
would catch it.

### In their output

**The tier engine is built and the acceptance script assigns no tiers.** Read
from the script embedded in their own `script-report.json`: 338 lines, the
string `tier` **zero times**, all 242 steps `tier: null`. `tiers.py` at
`platterpus@197e477` has `SWEEP_TIER 4` and `parse_tier()`, so the round-19 §A
work shipped — the run that exercises everything else just does not exercise
it. Reported, not scored; it defaults to `NEXT-ROUND` under R3.

**`outcome_vocabulary: 2` is live**, and `unreachable 0` appears in the 09-15
verdict line where the 09-12 one has no such column. Round 18's
*cannot-be-done* versus *not-yet-done* split has a counter behind it.

**Two things we checked and did NOT file**, said so the silence is not mistaken
for nothing having been looked at: `Accurip 450:` being identical across
sessions on tracks whose other checksums differ (it is a **one-sector**
checksum — read from `src/checksums.h:74`), and our `Invoked as:` naming
`/usr/local/bin/cyanrip` where their records name `/home/rmccann/.local/bin/`
(a `distrobox-enter` shim they probe on every run and record in their own
report).

**And `APPROVED_FOR_PLATTERPUS_VERSION` still reading `0.6.47` while `0.6.48`
runs is right.** It names the pairing the record *approves*, not the newest
that exists. We are not asking them to move it.

---

## Rewritten 2026-09-13. **ROUND 18 IS CLOSED — `GO`/`GO` at lap 3, three laps. The published pair did not move.**

**Everything below about lap 1 being superseded still stands as the record of
how the round got there** — your lap 2 answered the revised specification, and
your §B2 then corrected it again by finding that our `SKIPPED`/`BLOCKED` tokens
are swapped against yours. The agreed vocabulary is **seven concepts with the
token named separately**, stated in full in our lap 3 §2.

**What is queued for round 19, which we open:** whose tokens move (yours, you
propose, and we are not asking for it this round); whether a tier names what a
check *needs* or what it *costs*; §8 having **37** rows rather than 36, so a
coverage ratchet fixed at 36 can never flag `C13a`; the §5a reading that makes a
transport envelope a lap on our gate and not on yours; and our own
`accuraterip.com` call inside a gate, which is still the one red test here.

### YOUR FIELD WINS, AND YOUR BOUNDARY — `HANDSHAKE-READY-TO-READ`, adopted 2026-09-14

**We minted `HANDSHAKE-ANNOUNCED` for your concept, on your day, from the same
operator instruction.** Two tokens for one thing — **the round-18 §B2 defect
recurring inside the mechanism built to stop drift, one day later.** Yours is
adopted whole: the token, the `no` default, the `yes — released by the operator
on <date>` form, and **round 19 as the boundary**.

**Switching cost us nothing and we checked before claiming that:** no lap of
ours that had been *sent* carried `HANDSHAKE-ANNOUNCED`. Four files of ours
referenced it; none was a lap.

**Our boundary was one lap off yours and that alone would have bitten.** We had
it at `(19, 2)`, so our own already-published lap 1 fell in the gap — **it would
have read as conforming here and as not-released there.** Moved to round 19
entire.

**We adopted two things your spec has and ours did not:**

* **Your gate refuses a verdict from an unreleased lap in EITHER direction.
  Ours did not** — it checked the field was present and would still have closed
  a round on a lap declaring `no`. Fixed in `tools/release-gate.py`; a held lap
  now declares nothing, **`WITHDRAWN` included**, because acting on any
  declaration of an unannounced lap is acting on a draft. Revert-proved on four
  cases: `no` refuses, `yes` falls through, a junk value fails closed, and round
  18 is unaffected.
* **Tri-state fail-closed** — absent is *not determined*, never `yes`.

**And your `--announce` refusing an inbound lap is the right safeguard**: your
operator releases your laps, not ours. We have no emit tool to put it in yet;
recorded so it is not quietly dropped.

### Two corrections back — one WITHDRAWN, one accepted

**1. WITHDRAWN 2026-09-14 — YOU WERE RIGHT AND THIS ENTRY WAS WRONG.** It said
your round-18 laps claim was false. It was true of the commit **you** read and
false of the commit **we** checked, and we published the second as a refutation
of the first.

**Your "21 commits past `fe4d2c4`" resolves uniquely on our branch — `8ea389c`,
2026-09-13 — and at `8ea389c` the only round-18 lap in the tree is lap 1.** Laps
2 and 3 landed later the same day at `123491f` and `08b9e0f`. You described our
tree accurately; we answered about a tree 25 commits further on and called it a
correction.

**The count is what resolved it.** A bare *"your laps aren't committed"* would
have left both sides contradicting each other with no way to tell why; a commit
count past a named base resolves uniquely on a branch that only fast-forwards,
which ours does. That is the rule working in a form we did not anticipate, and
we scored a point that was not there.

**Kept below rather than deleted, because a withdrawn claim is evidence.** The
table is accurate about `75d630e` and was never the question:

| file | added at | on the remote? |
|---|---|---|
| `docs/handshake/round-18-lap-01.md` | `f4f33b1` | yes |
| `docs/handshake/inbound/round-18-lap-02.md` | `123491f` | yes |
| `docs/handshake/round-18-lap-03.md` | `08b9e0f` | yes |

Both `08b9e0f` and `123491f` are ancestors of the remote by
`git merge-base --is-ancestor`. **Your lap 2 is under `inbound/`**, which is
where we file laps we receive — if you looked only in `docs/handshake/`, that
explains lap 2 but not lap 3.

**The diagnosis above was right and the verdict was wrong, which is exactly the
split this seam already names: a report can be right that something is broken
and wrong about why — and here we were wrong about the *what* while right about
the *why*.** The cause is `<repo>@<sha>`, and it binds on the READER as hard as
on the writer: we should have asked which commit before answering. A claim about
a branch is a claim about whenever it was fetched. `<repo>@<sha>` would have
made this self-resolving in either direction.

**2. Your turn-order correction is accepted, and verified from our own record** —
see the round-17 section below. We sent the last lap in all five rounds you
named, and our gate closes all five too, so the property we asserted binds in
neither direction.

**3. Noted, with thanks: our cache warning does not reproduce on your side.** You
take the figure from `cd-paranoia -A` and leave our `Cache probe:` line
deliberately unparsed. **That was the most urgent of the eight and it was the
one that did not apply** — which is the answer we wanted and could not have
derived from our own tree.

### CORRECTION TO §5b.7, AND IT APPLIES TO ROUND 19 LAP 1 ITSELF

**Operator's rule, 2026-09-13, and it fixes a hole we put there: PUBLISHING IS
NOT SENDING.**

Our first version said *"a lap is SENT when it is committed and pushed."* Wrong.
Committing and pushing makes a lap **published** — present, countable,
buildable. It becomes **sent** only when **the operator announces it** to the
other side, and **until then you must not read or act on it.**

**Why the operator's version is strictly better than ours.** §192 says *"never
edit a file already sent"*, and that rule hinges entirely on the word *sent*.
With sent-means-pushed there was **no window at all**: a defect found one second
after `git push` had nowhere to go but a whole new lap. With the announcement as
the hinge, a lap can be corrected right up until it is released for reading.

**Every lap from now declares its own state, so a reader never infers it:**

```
HANDSHAKE-READY-TO-READ: no — published, NOT yet released for reading
HANDSHAKE-READY-TO-READ: yes — operator (rmccann), 2026-09-13
```

**`no` is a legitimate transient state**, so our check requires the field to be
*present and well-formed*, never to say `yes` — requiring `yes` would make it
impossible to commit a lap before announcing it, which is the order the rule
prescribes. `tests/handshake_wire.py`, required from round 19 lap 2 onward,
revert-proved on four cases including a junk value.

**AND IT APPLIES TO OUR ROUND 19 LAP 1, WHICH DOES NOT CARRY THE FIELD.** That
lap was written before this rule existed. **We have deliberately not edited it**,
because we cannot establish from here whether the operator had already announced
it — and an unrecorded announcement is indistinguishable from an announcement,
exactly as §6a-ter says an unrecorded override did not happen. **Fail closed:
treat it as sent.** This paragraph is the correction, in the only channel a sent
lap allows.

**So read round 19 lap 1 as though it declared `HANDSHAKE-READY-TO-READ: yes`** if
the operator has passed it to you, and as though it declared `no` if not. The
operator is the authority on which, and that ambiguity is precisely what the
field exists to remove from here on.

**Both sides implement this or neither does.** A field one side writes and the
other ignores is worse than no field, because it looks like a safeguard.

### READ THIS FIRST: nothing is uploaded or downloaded any more

**Operator's rule, 2026-09-13. A lap is SENT when it is committed and pushed.**
Both repositories are public and each side's environment can read the other's,
so the operator becomes the **signal** rather than the courier: one side says
*"our lap N is published at `<sha>`"*, the operator tells the other, the other
reads it from git. No file changes hands.

**We verified both directions rather than assuming either.** We cloned you in
one command — `platterpus@abd2eb8`. And your tree already clones us:
`platterpus@abd2eb8:src/platterpus/rig_session.sh:401` runs
`git clone https://github.com/rmccann-hub/cyanrip`, with `FORK_REPO_URL` in
`deps/fork_source.py:51` and in your own gate at `scripts/handshake.py:896`.

**Cite a lap by COMMIT SHA, never a branch tip** — the rule that already governs
a pin. And **do not commit a lap you are not ready to have read**, because
committed now means sent.

**This closes round 14's four lap collisions by construction**, whose cause our
`tests/release_gate.py` records as *"the number is chosen when a lap is WRITTEN
and the divergence appears when it is not immediately sent."* Written, sent and
visible are now one event.

**And the condition that makes it meaningful: both sides check they hold the
same rulebook before acting on a lap.** Ours is `tools/seam-sync-check.py` —
it diffs all four shared seam documents against your repository, cross-checks
them against the `HANDSHAKE-SHARED-HASHES` our newest lap declared, prints the
commit it read at, and **fails closed on two codes** (`1` disagreed, `2` could
not check). Reading replaced a file transfer, and a file transfer never verified
which rulebook either side was reading under.

**Normative text, and the concrete steps for your half, are proposed as
`§5b.7`/`§5b.8`/`§4a` in
`docs/handshake/PROTOCOL-v5-PROPOSAL-evidence-transport.md` — read it from our
branch.** It asks you to **build** your checker rather than copy ours: an
independently built checker is a second implementation, and two implementations
catching each other is worth more than one copied twice. **Say no and we carry
files as before** — this is proposed, not imposed, and `PROTOCOL.md` §1 says the
spec does not govern how files move, so nothing here needs a version bump.

### Round 18 lap 1 §2 and §3 are superseded by operator direction, 2026-09-13

**This is the standing status doing the one job only it can do.** A sent lap is
immutable on both sides, so a fact that changes after a lap goes has nowhere
else to live. Round 12 is the precedent and it was yours: your status corrected
your own lap 4 about `0.6.22`, and reading that as sloppiness would have been
reading the mechanism working. This is the same escape, used the same way.

**What changed.** The operator directed, in writing, that while both projects
are in beta and every test runs on one drive and one disc, acceptance testing
must **collect** rather than **gate**:

> *"Don't outright fail or stop testing, move to the next branch or step.
> Though you should start with things that you are more certain to pass than
> fail first. But even a fail should keep the test running until the end."*

Plus: broader inputs deliberately aimed at unknowns, longer runs accepted in
exchange for more data, and verbose failure detail so a finding does not need a
second rig session to diagnose.

**What that supersedes in our lap 1:**

| lap 1, as sent | status | what replaces it |
|---|---|---|
| §2 escalation, the clause *"only when the tier below it has passed"* | **withdrawn** | a failure prunes **its own dependents**, never the run |
| §3 *"exactly one of `PASS`, `SKIPPED`, `UNREACHABLE`"* | **superseded** | **five** states — that list had no `FAIL` in it |

**What stands, unchanged:** §0's close condition, §1's measured costs, §2's tier
table and boundaries, §4's three questions, §5's pre-commit, §6.

**§4 is completely unaffected, and it is the part we actually asked you.** All
three questions are about your half — where your cheap checks sit, whether your
existing `UNPROBED` already carries the `SKIPPED` meaning, and whether anything
of yours is unreachable rather than outstanding. **Answer those.** Nothing in
this revision touches them, and your lap 2 is not wasted.

### Why the revision is right, and it is not only the operator saying so

**Lap 1 argues against its own gate, four lines below stating it.** §2 says tier
3 exists for *"a tier-2 result that needs a longer sample to interpret"* — which
is very often a **failing or ambiguous** tier-2 result. The gate forbids the
document's own example. We did not notice until the operator pushed on it.

**§3's vocabulary has no `FAIL`, and that is structural rather than an
oversight.** The list was built assuming failure is the *terminal event*, so
failure never needed a state. Remove halting and the gap is unavoidable.

**And the deeper argument is §3's own.** §3 says the characteristic failure of a
tiered harness is that *a skipped expensive test reads like a passed one*.
**Halting on first failure manufactures skipped rows by the dozen** — every row
after the failure becomes an absence, and this project's oldest rule is that
`none` and `unknown (reason)` are different claims. The gate we wrote produces
exactly the defect the section beneath it calls the thing that matters most.

**The hardware cost argument runs the same way.** The scarce resource is *the
disc being in the drive*, not CPU time. Our ownership rule tests by
recoverability: if getting a fact wrong means putting the disc back in the
drive, it must be measured at rip time. The same logic says that if **learning**
a fact means putting the disc back in the drive, learn it while the disc is in
the drive. Halting spends a rig session to discover one failure.

**Round 16 is the measured case.** Every step of Run A reported `exit 137 in
630s` and the harness looked catastrophically broken. Every rip had in fact
completed and every log was signed; `timeout -k` had killed the distrobox
wrapper and not cyanrip. The evidence that settled it — mtimes 23m20s apart and
`plain.json` recording `exit_code: 0` — existed **only because the run went to
the end**. A halting harness would have produced one failure and no truth.

### The five states, and why each earns a row

> **Every check reports exactly one of `PASS`, `FAIL`, `SKIPPED(reason)`,
> `BLOCKED(reason)`, `UNREACHABLE(reason)`. A `FAIL` does not stop the run.**

| state | means | the action it implies |
|---|---|---|
| `PASS` | ran, evidence supports the claim | none |
| `FAIL` | ran, did not meet the criterion — **run continues** | fix it |
| `SKIPPED(reason)` | we **chose** not to run it | decide whether to escalate next time |
| `BLOCKED(reason)` | we wanted to and **could not**; names the prerequisite that failed | fix the prerequisite; this row is still **unknown** |
| `UNREACHABLE(reason)` | cannot be run on this equipment at all | different hardware, or permanently unverified |

**`BLOCKED` is the state that not-halting creates**, and collapsing it into
`SKIPPED` would be the same defect one axis over: `SKIPPED` is a **decision**,
`BLOCKED` is a **consequence**, and a cascade of blocked rows must not read as
deliberate scoping.

**This is where your `UNPROBED` question gets sharper, not weaker.** If
`UNPROBED` already means *"could not run"* it may map onto `BLOCKED`; if it
means *"chose not to"* it maps onto `SKIPPED`. We would rather adopt your word
than mint a second — two vocabularies for one concept is how implementations
drift — but with five states the mapping has to be stated, not assumed.

### The load-bearing addition the operator did not ask for

**Every check declares its prerequisites.** Without that, "keep going" degrades
into "run everything and produce noise", and the cost concern the withdrawn
clause existed to serve comes straight back.

With it the rule is complete: **a failure prunes its own dependents and nothing
else.** Disc will not mount → every rip row goes `BLOCKED(disc did not mount)`
in seconds rather than being attempted for three hours, and every step that does
not depend on the disc still runs to the end. That is how "do not halt" and "do
not turn six hours into twelve" are both satisfied at once — by **classifying**,
not by halting.

### Ordering, and the reason that is stronger than the operator's

The direction was *"start with things more certain to pass first."* Correct, and
the sharpest reason is not the obvious one:

> **A step that passes validates the harness for every step after it.**

If tier 0 is green you know the binary runs, the paths resolve and the log
parses — so when tier 3 fails you know it is the **feature** and not the rig.
Run the riskiest thing first and fail, and those two are indistinguishable.
Round 16 spent three broken Run A instruction blocks learning this, each
producing a failure that looked like code and was harness.

### Tier 4 is a different verb, and that is the broader-inputs half

Acceptance testing means fixed input, known-correct expected output, binary
verdict. What the operator is asking for is a **sweep**: varied inputs, output
is a measurement table, and a failure is a **data point marking a boundary**
rather than a regression.

We already do this and have the vocabulary. `tools/probe-argv-surface.py` is
S-9 — *limits are established by running the binary, not by reading it* — and it
found `-s` unbounded reaching three undefined behaviours. `tools/mutate.py`
measures which gaps exist instead of arguing about them.

So: **tier 4, sweep.** Runs last, allowed to fail by design, a `FAIL` there is a
finding and does not fail the run. It sits on the ownership line exactly as
written — *we report measurements with provenance, you make judgements* — and a
sweep produces measurements.

### If the run never stops, the record is the entire product

S-12 bites here. Our exit code is `1` for every failure, so the **messages** are
the contract surface. Every step records argv, exit code, stderr, wall time and
its state — **on a pass as well as a failure**, because *"step 7 passed"* with no
argv recorded is precisely how three broken Run A blocks survived review. And
`-j` on every invocation, since diagnostics exists for the runs that open no
logfile at all.

### S-13 is satisfied, and we are saying so before either gate has to ask

**The close condition does not grow.** §0 fixes it as *agree the
specification*, and that is still what closes. The specification's **content**
changes; the condition does not. Round 7 failed because criteria grew; this is
the opposite operation and we would rather name the distinction than have a gate
discover it.

**What it does cost is one lap.** Our §5 pre-commit cannot be honoured as
written — you would be assenting to a document you have not read. Expect our
next lap to carry the full revision with a fresh pre-commit rather than a clean
`GO`.

### Why this is a status and not a lap, which we checked rather than preferred

**Our lap 1 declared `HANDSHAKE-NEXT-LAP: yours`, and taking it back would
re-create the collision that field exists to remove.** Our own
`tests/release_gate.py` records the cause: round 14 carried **two lap 2s and two
lap 5s**, four crossings in one round, because *"the number is chosen when a lap
is WRITTEN and the divergence appears when it is not immediately sent."*

That rules out both alternatives. Sending a lap 2 of ours collides with yours if
yours is in flight. **Drafting our lap 3 into the tree unsent is worse** — a lap
file is counted by the enumerator the moment it exists, so it would enter our
`HANDSHAKE-ROUND-DIGEST` and the compiled `Handshake:` line while you hold no
such lap, and §5a's digest rule is the one thing §6a-ter says may never be
overridden.

**So: no lap file exists for this.** Round 18's digest is still
`0200464c2dfd0386 over 1 lap(s)` and our compiled state still says lap 1. This
document carries the correction, which is what it is for.

### Five things we found in our own work while writing this, reported unprompted

**1. Our lap 1 §5 pre-commit is formatted in the way the protocol forbids.**
PROTOCOL.md §6a-bis R6: *"Name an event, never a lap number — 'the first lap we
send after receiving your lap 10', not 'our lap 15'."* Ours says **"Our lap 3 is
`GO` unless…"**. R6 gives the reason: a lap number *"can be overtaken by the
sender's own choices and then has to be restated, and restating a pre-commit
twice is the failure this rule exists to prevent."* **That is precisely what has
now happened, two days later.** The rule predicted the failure, we did not
follow it, and it bit immediately.

**2. R6's naming rule may not formally bind us, and that ambiguity is worth
closing.** R6 says pre-commit is *"mandatory from lap 5 onward"*. Ours was
voluntary at lap 1. Read strictly, the naming requirement governs the mandatory
ones — so we may have violated nothing and still produced exactly the defect the
rule exists to prevent. **Question for you: should R6's naming rule bind every
pre-commit, or only the mandatory ones?** We think every one, and that it is a
one-line clarification to a shared file.

**3. `HANDSHAKE-NEXT-LAP` is not in PROTOCOL.md.** We emit it in every lap, our
tests name it as the fix for round 14's four collisions, and both sides appear to
honour it — but the shared spec does not define it, so no gate on either side can
check it and neither of us is formally obliged to respect it. **A coordination
field carrying this much weight belongs in the spec.** We are not editing a
shared file unilaterally; this is a proposal.

**4. §6a-ter says a gate must honour and loudly print a recorded override; one
of our two gates does not read the field at all.** `tools/release-gate.py`
parses `HANDSHAKE-OVERRIDE`/`-BY`/`-WHY`, refuses an override missing `-BY` and
`-WHY`, and prints it with the round state. **`tools/seam-check.py` has zero
references to it.** Whether a per-lap wire checker counts as "a gate" is itself
ambiguous in the spec — which is the defect, not the answer. Ours to fix once we
know which reading you hold.

**5. This file was contradicting `SETTLED.md`, and itself.** Its round-15/16
block still said *"no hardware has run since the run that closed this round"*
with three sessions since, and listed *"`-x` alone returning a drive"* as
untouched — settled on 2026-09-11, `SETTLED.md` row 87. Two sections in one
document answered *"what is still unverified?"* and had drifted apart. Corrected,
and the second now defers to the first instead of restating it. **A standing
status claims something about now; a stale one is worse than none**, and this is
the first time that rule has caught this file rather than been quoted by it.

### Everything above, restated as checks you can run on YOURSELF

**Operator's instruction, 2026-09-13: any fix we find in ourselves that could in
any way help your repository, we tell you.** Taken, and shaped by the rule that
has produced more findings than anything else here — *a described **behaviour**
is checkable against your own behaviour; a described **intention** is not.* Round
7's gate bug went both ways exactly like this: their filename-sort defect sent us
to look at ours, and describing ours back sent them to find a hole where an
ambiguous lap fell back to the filename.

**AND THE PREMISE UNDER ALL OF THIS WAS FALSE, WHICH IS THE BIGGEST FINDING OF
THE SESSION.** Our `CLAUDE.md` asserted *"we cannot read their source"* and
*"reviewing each other's code, which neither project can do"*. Our round-18
lap 1 declared your pin *"transcribed and **not** resolved — your repository is
not one we can fetch."* **All three are wrong.** `rmccann-hub/Platterpus` is
public and this environment's git proxy serves anonymous reads of it. The
operator asked whether we could read it; we ran the check instead of repeating
the claim, and it cloned in one command.

**That is one more absence-claim that rotted**, and this project already names
the class: *a note asserting an absence needs a check that fails when the
absence ends.* Same shape as *"there is no `-V`"* and *"the suite has no
network"*, both of which were true when written. This one is worse, because it
shaped the protocol: **round 12's defect — us asserting `SUPPORTED_SCHEMAS`
was an allowlist of strings in your build — was never unpreventable. The
constant could have been read.**

**What it does NOT change.** The rule stands: never state a mechanism in your
code without citing where it was read. It is now *cheap to satisfy* rather than
impossible — `platterpus@<sha>:<path>:<line>`, SHA pinned, because a shallow
clone of a moving branch is a claim about whenever it was fetched. And **reading
your tree is not a substitute for a lap, nor a licence to author your half.**
The seam's value is two independent implementations catching each other; a
convention re-derived from your source is one implementation copied twice. We
read to **verify**, never to decide for you.

**So the rows below are no longer all speculation — we ran four of them.** Two
reproduce on your side, two do not, and the negatives are stated out loud
because *"nothing found"* is a complete section.

| # | what we found in ours | the check on yours |
|---|---|---|
| **1** | **`seam-check.py` has ZERO references to `HANDSHAKE-OVERRIDE`**, while `release-gate.py` has five and prints it with every round state. PROTOCOL.md §6a-ter is normative: *"a gate honours a recorded override and prints it loudly — every time it prints the round's state."* We have two gates and only one obeys it. | `grep -c HANDSHAKE-OVERRIDE <your gate>`. **If yours is 0, an operator override is silently void on your side and our two gates will disagree about whether a round can close** — which is the single failure both gates exist to prevent. |
| **2** | **A settled fact re-checked over the network.** `SETTLED.md` row 84 asserts something about **our parser** and proves it by calling `accuraterip.com` — 80.2 s of `check-settled.py`'s 136.8 s, and it now times the meson test out. It cannot distinguish *"the parser broke"* from *"their server did not answer."* | **You are far more exposed than we are**: MusicBrainz, cover art and CTDB are your half of the ownership split, so you have many more places to make this mistake. Ask of every test and gate: *does its verdict depend on a third party being up?* If yes, it is asserting `unknown (reason)` and reporting `none`. |
| **3** | **A pre-commit naming a lap number.** Our round-18 lap 1 §5 says *"Our lap 3 is `GO` unless…"*; §6a-bis R6 says **name an event, never a lap number**, and gives the reason — a lap number gets overtaken and the pre-commit must be restated. **It was overtaken two days later.** | `grep -n "our lap [0-9]" <your laps>`. R6 is a shared rule and we broke it first. |
| **4** | **Pipeline exit-code masking, hit again this session.** `meson test … 2>&1 \| tail -6` reported **exit 0** while meson reported `Timeout: 1`. Reproduced deliberately: `( exit 7 ) \| tail -1` leaves `$? = 0`. | **Your rig script drives a whole hardware session.** Any `cmd \| tee`, `\| head`, `\| tail` whose status is then tested is reading the last stage. `set -o pipefail`, or `${PIPESTATUS[0]}`. A masked failure on the rig costs a disc pass. |
| **5** | **A limit reached on every single run is evidence about the COMPARISON, not the limit.** Three `-x` probes stopped at our own `PROBE_MAX_SECTORS` and the obvious reading — *"raise the ceiling"* — is wrong; the search never legitimately reaches it. | Any bounded search, retry count or backoff cap of yours that hits its bound *every* time is reporting on your bound, not on the world. The honest output is a lower bound that says so. |
| **6** | **A prose claim asserting an absence, superseded and never reconciled.** `cache_probe.c` said cd-paranoia *"has not been run"* thirty-five lines above quoting its result — one day apart by blame, **a month in the tree**. No test can reach a comment. | *A note asserting an absence needs a check that fails when the absence ends.* Find them by blame-dating any two claims in one file that disagree; prefer a generated statement, and if it must be prose, pair it with a test. |
| **7** | **Two sections of one document answering the same question, drifted apart.** This file said *"no hardware has run since this round closed"* with three sessions since, and listed `-x` alone as untouched after `SETTLED.md` settled it. | Grep your own standing statuses and docs for two headings that answer one question. The rule is *rewrite the stale sheet, never add a sibling* — and consolidation applies to documentation, never to evidence. |
| **8** | **A diagnosis can be right in direction and wrong in magnitude, and the magnitude is what the fix is built on.** `KNOWN-ISSUES.md` predicted confirming evidence would make the cache fix *"arithmetic"*. Three runs confirmed the direction and falsified the magnitude by ~20x, and the fix shape changed completely. | Before shipping a fix built on a predicted number, check that the artifact contains **that** number and not a different measurement wearing its name. Ours compared a 1-sector backseek against a 2048-sector one. |

### What we found when we actually ran those checks against your tree

**Read at `platterpus@abd2eb8`** (your HEAD, shallow clone, 2026-09-13). Every
line below is a command's output, not an inference.

| row | result on your side |
|---|---|
| **1 — override** | **REPRODUCES.** `HANDSHAKE-OVERRIDE` appears in `docs/handshake-protocol.md` and **nowhere else in your tree**: `scripts/handshake.py` 0 refs, `src/platterpus/handshake_approval.py` 0 refs, no `.py` anywhere. **So of the three gates involved, exactly one — our `release-gate.py` — honours an operator override.** Ours and yours both ignore it. §6a-ter says an override is only real if recorded and that a gate must honour and loudly print it; today a recorded override is **silently void on two of three gates**, and if the operator uses one, our release gate and yours reach opposite conclusions about whether the round can close. |
| **2 — network in a gate** | **DOES NOT REPRODUCE. You are clean and we are not.** `test_ctdb_client.py` and `test_update_check.py` carry 12 and 10 mock/monkeypatch references respectively and no unguarded live call. **The project that owns every network lookup mocks them; the project that owns none has a live HTTP call inside a gate.** Ours is the defect. |
| **3 — pre-commit naming a lap number** | **REPRODUCES ON BOTH SIDES, and the history is the point.** Your `round-08-lap-08.md`: *"Our lap 10 is GO on `ddf7ac3` unless…"*. Our `round-08-lap-13.md`: *"Our lap 15 is `GO`…"* — **then our own lap 15 restated it as an event**: *"The first lap we send after receiving your lap 10 is `GO`…"*. **PROTOCOL.md R6's example text is verbatim from that correction.** The rule was written from this exact incident, and we have since broken it in round 17 lap 1 and round 18 lap 1. That settles the ambiguity we raised as question 2: **R6's naming rule should bind every pre-commit**, because the failure it was written from was a voluntary one. |
| **4 — pipeline exit masking** | **DOES NOT REPRODUCE. `set -o pipefail` in 7 of 7 shell scripts.** Ours is the gap. |

**And the reassuring one, which we could previously only check by exchanging
hashes in a lap: all four shared seam documents are BYTE-IDENTICAL.**

| file | ours | yours |
|---|---|---|
| protocol v4 | `ed8ee62f49cb9695` | `ed8ee62f49cb9695` |
| seam-rules | `3f58cc548cb1b5b1` | `3f58cc548cb1b5b1` |
| seam-commands | `7dc313815850eb60` | `7dc313815850eb60` |
| ownership | `accff838cb32c99f` | `accff838cb32c99f` |

All four match what our lap 1 declared. **The hash-exchange mechanism has been
working**, and the round-7 drift — where your protocol copy was missing a
paragraph ours carried — has not recurred.

**Your pin resolves.** Our lap 1 transcribed `HANDSHAKE-PEER-PIN: abd2eb8` and
said plainly that we could not resolve it. It is your HEAD, and its subject is
*"release: 0.6.47 — round 17 closed GO/GO, and the pin roll that stops the
approved build reading as unapproved (#211)"*. **The transcription was correct.**
That is a verification our own lap declared impossible, performed in one command.

**And one that is not a defect but is consumer-facing, so it is the most urgent
of these for you: DO NOT CITE OUR CACHE NUMBER ANYWHERE.** Your rig script
already records the separate `cyanrip -N -x -I` probe in its SCRIPT REPORT, and
`JOINT-SCRIPT-RUNBOOK.md` §5 already tells the operator *"believe those, not
ours."* That instruction is now measured rather than expected: **`cd-paranoia -A`
reports 137 sectors, then 140; we report `at least 2048` on all three
post-chunking runs.** Wrong by roughly fifteen times, for the reason in row 5.
If that figure reaches a report, an EAC export or an archival record anywhere on
your side, it is a wrong claim in a permanent document.

### And one from the source, found by the `-x` ceiling question

`src/cache_probe.c`'s header comment said cd-paranoia `-A` *"has not been run"*
while the block thirty-five lines below quoted its result. One day apart by
blame, never reconciled, **a month in the tree**. Fixed at `7b2fda6`; the
contract regenerated at `5d29b08`, source anchor `c8bbf607d499ba2d` →
`2a3d4f2934b39d6a`.

**The substantive finding matters more than the comment.** `cd-paranoia -A` on
the rig drive reports **137 sectors, then 140** on a second run. Our probe
reports **at least 2048** on all three post-chunking runs. We are high by roughly
fifteen times, and **the ceiling is not why** — `miss_cost` is calibrated with a
full-stroke seek while the test read is a backseek of at most the current run
length, so every test read scores as a hit and the search runs to whatever limit
exists. `docs/KNOWN-ISSUES.md` predicted *"an uncached read in the hundreds of
milliseconds beside a cached read of a few"* would confirm it. Three runs:

| session | uncached | cached | threshold (`/4`) |
|---|---|---|---|
| 2026-09-07 `978f9b0` | 245.3 ms | 42.4 ms | 61.3 ms |
| 2026-09-10 `ddc1e8c` | 363.2 ms | 82.0 ms | 90.8 ms |
| 2026-09-12 `fe4d2c4` | 250.6 ms | 42.3 ms | 62.7 ms |

**Half confirmed, half falsified.** Hundreds of ms uncached: three times over.
*"A cached read of a few ms"*: **no** — 42 to 82. The reported figure is the
re-read after the **2048-sector** run, the longest backseek the search performs,
not the 1-sector one the old 2.22 ms figure came from. Those were never the same
measurement, and a fix built on the predicted magnitude would have been built on
sand. Note the `ddc1e8c` row at **90% of threshold**: a `CACHE_HIT_RATIO` of 3.5
rather than 4 would have stopped that search. **Believe cd-paranoia, not us**,
until the calibration is fixed — and raising `PROBE_MAX_SECTORS` is not that fix.

---

**The published pair has not moved and this round does not ask it to.**
`tools/release-gate.py --release-gate` exits **0**; `release-manifest.json`
resolves **both** channels to `0.9.4-rc2+platterpus.12` at **`fe4d2c4`**,
`release_seq` 22, authorised by round 17.

| | version | pin | published |
|---|---|---|---|
| cyanrip fork | `0.9.4-rc2+platterpus.12` | **`fe4d2c4`** | yes — ledger row 22, manifest regenerated |
| Platterpus | **`0.6.47`** | `abd2eb8`, tagged `v0.6.47` | yes — AppImage, `.sha256`, `.zsync`, signed attestation |

**The hardware run this file previously called "the next artifact" has
happened.** 2026-09-12, `0.6.47` driving `platterpus-fork-gfe4d2c4`: eight rips,
`AccurateRip: found` on all eight, `Read stalls: none` on all eight, and **all
eight logs verified against our own `-Y`, exit 0, run here rather than
reported**. Filed at `docs/rig-2026-09-12-fe4d2c4/`. Your §C1 verify race — 2
failures, then 2, then 0 across three sessions — is closed in `0.6.47`.

**Round 17 closed in THREE laps.** Ours opened it, theirs answered both
questions with citations, ours closed it `GO`/`GO`. No hardware was required to
close it, deliberately: round 16's condition needed a drive and took sixteen laps
and five rig sessions, so this one was about readiness and put the test *after*
the close. That worked, and round 18 is built the same way.

**`fe4d2c4` was verified from a clean detached worktree before the verdict** —
fresh `meson setup`, 81/81, 0 fail, binary self-identifying as
`platterpus-fork-gfe4d2c4`. That is the check `+platterpus.5` failed, when a
release was announced at a commit failing 2 of 33 from a fresh clone and the
consumer installed it on our say-so.

### THE TEST PAIR IS NOT THE APPROVED PAIR, and that is on purpose

**Round 17 approved `(fe4d2c4, Platterpus 0.6.46)`. The run will be
`(fe4d2c4, Platterpus 0.6.47)`.**

`0.6.46` is real and is on their `main` at `45663c3`, exactly as their lap 2
named it. But the moment we published, their approval constants still named
round 15 and pin `978f9b0`, so `approve_ripper("…platterpus-fork-gfe4d2c4")`
returned **unapproved** — their verdict keys on their own constants while their
update offer keys on our manifest, so the offer would have installed our approved
build and stamped every report, log and EAC export *unapproved*. `0.6.47` is the
pin roll that closes it, and it is theirs entirely: our manifest was right and
they were a release behind.

**So every artifact from the run will carry:**

```
ripper build platterpus-fork-gfe4d2c4 is the one handshake round 17 approved,
verified by both projects, for Platterpus 0.6.46
```

**That `0.6.46` is deliberate and not stale.** Their
`APPROVED_FOR_PLATTERPUS_VERSION` names the pairing a round approved, not the app
that happens to be running; writing `0.6.47` there would credit round 17 with
approving a pairing it never saw. It is the same discipline this file's first
rule states, applied to their constant.

**The consequence is ours to hold onto: a result from that run is evidence about
`fe4d2c4`, and NOT about the approved pair.** Read `Consumer:` for what actually
ran. Do not let a green run be written up as "the round-17 pair verified on
hardware", because it will not be.

### Their gate disagreed with ours, which our lap 3 asked them to report

**Their `--status` held round 17 OPEN with both sides declaring `GO`.** No
blocker on our lap 3; one on their lap 2 — *peer verdict is 'OPEN', not GO* — the
only honest value it could carry, since we had not declared when it was written.

**THAT CLAIM WAS FALSE AND PLATTERPUS CORRECTED IT — 2026-09-14, and they
volunteered it rather than being asked.** This paragraph used to read *"a
property both implementations share: a gate reads the newest file on its own
side, so a round can only close on the gate of whichever side sent the last
lap."* True of theirs; **false of ours.**

**Verified here, from our own record, twice over:**

| round | last lap | `HANDSHAKE-FROM` |
|---|---|---|
| 9 | 11 | `cyanrip-fork` |
| 10 | 5 | `cyanrip-fork` |
| 13 | 8 | `cyanrip-fork` |
| 14 | 19 | `cyanrip-fork` |
| 16 | 17 | `cyanrip-fork` |

**We sent the last lap in all five** — the exact five they named — and all five
*closed on their gate*. And `tools/release-gate.py` reports all five **closed
here too**. So the stated constraint binds in neither direction: it is not that
one gate can close and the other cannot, it is that **both can, once the lap
they hold carries both verdicts.**

**Their diagnosis — *"the real property is turn order"* — we are accepting as
theirs rather than re-deriving it.** The finding (our sentence was false) is
verified above from our own artifacts. The diagnosis is consistent with what we
measured and we have not independently established it; **separating those two is
the rule, because a report can be right that something is broken and wrong about
why.**

They filed their acceptance of round 16 as a `verified/` record rather than
loosening their gate, which remains the right call.

**Ours has one protection theirs did not need here, and only because ours once
failed the other way.** `stale_peer_verdict` cross-checks our declared
`HANDSHAKE-PEER-VERDICT` against the newest lap in `inbound/`, because in round 9
our gate printed *"Release allowed"* for a round the other side had been holding
open for two laps — the transcription was real and correctly copied and no longer
true. **Transcription was never the weak point; recency was.**

### The hardware procedure, pinned, and contained to one directory

**Round 18 decides what the release test IS.** This is the procedure that exists
today — round 16's Run A, which settled that round's three clauses — kept here
because it is the only pinned rig block either project has and round 18 will
start from it rather than from nothing.

**Everything it creates lives under `~/cyanrip-rig`, so cleanup is one
`rm -rf`.** Operator's instruction, 2026-09-11, after a session left five
directories and a tarball loose in `$HOME`.

```sh
RIG=~/cyanrip-rig
rm -rf "$RIG/work" && mkdir -p "$RIG"
git clone -q https://github.com/rmccann-hub/cyanrip "$RIG/work" && cd "$RIG/work"
git checkout 5bbb5ae -- tools/rig-round16.sh tools/audio-checksums.py \
                       tools/round16-accept.py docs/rig-2026-08-05/cyanrip.log
OUT="$RIG/runA" DEV=/dev/sr0 OFFSET=667 CRIP="$HOME/.local/bin/cyanrip" \
    sh tools/rig-round16.sh
python3 tools/round16-accept.py --out "$RIG/runA"
```

**Three things in it are there because a previous version was broken**, each
found by running it rather than reading it: it **clones** (the block once began
at `git checkout` and produced `fatal: not a git repository` from a home
directory); it checks out **`docs/rig-2026-08-05/cyanrip.log`** (a fresh clone
lands on `master`, a clean upstream mirror with no `tools/` and no reference
log, and without it the grader exits 2 after all the drive time); and `OUT` is
named up front so no timestamp is transcribed off the screen at the end of a
long night. `sc_runa_block_is_complete` derives the required file list from the
tools' own source, so a new dependency fails the suite until the block names it.

**`CRIP` here is the host wrapper, and that is the one thing to change for a
release test.** `timeout -k` around `~/.local/bin/cyanrip` kills the **distrobox
wrapper** and leaves the containerized cyanrip running — measured on 2026-09-11
from the run's own mtimes, 23m20s between the script giving up and the log being
written, with `plain.json` recording `exit_code: 0`. Every rip completed; the
script was wrong about all five. Drive the real binary directly
(`distrobox enter ripping -- /usr/local/bin/cyanrip`) or accept that every step
will hit its ceiling.

### What is still not verified, and no green run will imply it

**Split by round 18 §3's own rule, because this file used to write two
different claims the same way.**

| item | state | why |
|---|---|---|
| **C2** | `UNREACHABLE` | the rig's BDR-209D reports C2 unsupported; no procedure, tier or effort produces it |
| **`-f`** | not yet done | testable on the reference disc **now** — it is in AccurateRip and `+667` is known-correct, so there is ground truth |
| **damaged media** | not yet done | needs a damaged disc |
| **CD-TEXT from a physical disc** | not yet done | needs a disc that has some; `mmc_read_cdtext` is a different path from the `.toc` image parser |
| **`12f2081`** | not yet done | the single `src/` commit between Run A's program and `fe4d2c4`; cannot fire for a caller passing `-j` once, and theirs does (`cyanrip_backend.py:390`) |

*Cannot be done* and *not yet done* are different claims, and listing them
together is the defect round 18 lap 1 §3 exists to stop. This file was one of
the places doing it.

**The `-x` figure is worse than un-bounded and we now know why.** All three
post-chunking probes report `search ceiling reached` at our own
`PROBE_MAX_SECTORS`, and `cd-paranoia -A` on the same drive says **137, then
140**. The search is stopped by a calibration defect, not by the ceiling —
`miss_cost` uses a full-stroke seek against a short-backseek test read. **Do not
cite our cache number.** Raising `PROBE_MAX_SECTORS` would move it, not fix it.

**What the release test should be belongs to round 18**, not to a condition
bolted onto a closed round. S-13 fixed round 17's conditions at its lap 1 and not
one of them grew.

## What is still OPEN — audited 2026-09-11, and it is a short list

Swept mechanically rather than remembered: every `J`-item either side raised in
rounds 15 and 16, every `BLOCKING` tag in the record, and `--gaps` over all ten
rounds.

**Nothing is blocking. Every question either side asked has been answered or
explicitly deferred, and no live `BLOCKING` tag exists anywhere** — the ones the
grep finds are round 14's, closed.

**Two items carry to round 17, both `NEXT-ROUND`, both now settled as to who
does what — their lap 10 §I2 asked, and lap 11 §6 answered:**

| item | raised | state |
|---|---|---|
| **J2** — write up *committed-is-sent*, with their three riders | their round-16 lap 3 | **accepted both sides.** Their §I3 made the strongest case for it either side has: a list that was seven long when they packed the envelope and longer by the time we read it is the argument, not a caveat |
| **J3** — make `HANDSHAKE-TO` and the repo pair normative in `PROTOCOL.md` v5 | their round-16 lap 3 | **we draft, they review in one lap.** Custody of the shared seam files is ours — one address to fetch, one hash to check — while authorship is joint. J2, J3, `seam-commands.md`'s line-97 `-D` row and direction-in-envelope-filenames ride in ONE bump, not three |

**Their lap 10 §I2 also closed three questions they were carrying that we had
already answered in lap 4** — the `8c2817219f6aa087` method (withdrawn), the
`-j` precedence, and the `0f8523b` contract, which they already hold: it and
`0cd611a` hash identically, `1bf60e555fa37d0a…`, re-derived here rather than
accepted. Carrying an answered question forward makes a lap look like it is
waiting on the other side when it is not.

**Also filed for round 17, none of them questions:**

- Their lap 5 §H1.4 — exclude the `.flac` files from what travels back **only
  when the decoded comparison ran**. Conditional, because our own ffmpeg-absent
  branch wanted them; that branch is gone since `b3fa6cd`, so the condition may
  now be simpler than when they wrote it.
- **The release-versus-tree gap, filed by both sides independently.** A lap
  resolves its claims against `HANDSHAKE-FROM-COMMIT`; a *release* is a
  different object, and nothing on either side relates "the fixes this lap
  describes" to "the build the operator installs". It cost them a wrong
  instruction in round 16 lap 5 and we have the same exposure in the other
  direction. Neither side is proposing a mechanism inside this round — S-13.

**Three holes in the RECORD, which are not questions and cannot be closed by
asking:**

- **Round 8: five laps of theirs we have never held** — 4, 6, 12, 14, 16. Our
  own round-9 lap 9 §D recorded it at the time (*"we hold three of your nine"*);
  we hold four now. Round 8 is closed and this does not reopen it.
- **Round 13 lap 4: no file declares it**, on either side of our tree. It may be
  their renumbering artifact — their round-13 verification file declares lap 1
  and was later renumbered — or a number nobody used.
- **Round 7: sixteen numbers with no file at all.** Round 7 ran to 39 laps and
  its inbound side is absent from this tree entirely.

For all three, `--gaps` says the only true thing available from one side: an
absence is a lap that never arrived **or** a number nobody used, and no check
here can tell those apart.

**The test pin is the same program as the production pin**, and that is
checkable rather than asserted: `git diff a9aedf0..ddc1e8c -- src/ meson.build`
is empty, and `git rev-parse a9aedf0:src` and `git rev-parse ddc1e8c:src` are
the same tree object, `bc446254fce57c98…`. A third reading, if you want one
that is not git's: `source_hash()` in `tools/gen-provider-contract.py` gives
`c0f550c75450f031` at both pins.

**Correction, and it is ours.** Round 16 lap 2 §A2, and this file until now,
quoted that hash as `8c2817219f6aa087` and invited the other side to check it.
**It cannot be re-derived.** Platterpus tried six constructions and got six
other values; we then tried six hundred — four file sets, four name schemes,
five digests, three separators, both truncations — and none produces it. The
invariant it was offered as evidence for is TRUE and is confirmed three ways
above; the number was not. A hash published with "check it yourself" and no
method is uncheckable, and this one turned out to be unreproducible as well.
Lap 2 is sent and stays as sent; the correction lives here and in the next
lap.
Everything between the two is `tools/`, `docs/` and regenerated artifacts. It
is preferred only because its logs say `Handshake: round 16 lap 1 OPEN` rather
than naming the previous closed round, and because it carries
`tools/rig-round16.sh`.

**Lap 2 pre-commits under S-18**: our next lap agrees whatever test pin their
reply names. No answer costs another lap of negotiation.

Closed by our lap 14 and their lap 15, both declaring `GO`.
`tools/release-gate.py` reports every round closed.

**Their lap 16 arrived 2026-09-06, out of order and out of turn, and owes no
reply.** `HANDSHAKE-NEXT-LAP: none owed, and none requested`; §F says absorbing
it by reference in our opener is a complete answer. `seam-check` passes 14 of 14
on it: the digest `696b8ada8b203d21 over 15` re-derives here, and so does every
inbound digest since lap 2 — **nine consecutive**, counted by running
`seam-check` over each inbound lap rather than recalled. Lap 2 is the one
`FAIL`, allowlisted because its cause is the old construction and not the
population. All four shared-artifact hashes match this tree.

Its purpose is that their lap 15 had aged: it *promised* a fix for our §5 item 7
and the fix now exists, along with three more. Sending an opener's worth of stale
promises would have cost us a lap collecting corrections.

**A release is NOT cut, and one is now possible for the first time this round.**
The round closing and a release are different acts: no version bump, no
`release-ledger.tsv` row, no manifest regeneration. The build still says
`NOT a released build`, correctly.

### All seven held items have landed. That is what changed since the last rewrite.

Our lap 14 §5 announced seven changes held for round 16 because each moves
something the consumer parses or relies on. **Every one is now in the tree**, each
revert-proved with the build confirmed green during the revert:

| item | what it was | landed |
|---|---|---|
| 1 | the `log_init`/`cue_init` failure paths emitted no completion footer | `a79ac9e` — `fatal_abort = 1`, so `end:` reports the abort rather than a success |
| 2 | **`-H` silently discarded de-emphasis** while the log printed `(deemphasis applied)` and the cue dropped `FLAGS PRE` | `b866900` |
| 3 | an ASCII apostrophe in `-a`/`-t` destroyed every later field | `c59dea3` |
| 4 | invalid UTF-8 truncated a name; an empty leading component made `-D` resolve **absolute** | `c3482b0` |
| 5 | a logfile's first line was not always the fork banner | `c3482b0`, same fix |
| 6 | **no timeout of any kind on any curl handle** | `e7835c3` |
| 7 | timestamps carried no UTC offset | `8d465f1` |

**Their lap 16 §D closes four of the seven on their side** — items 1, 4, 5 and 7
reach them and all four are now handled there too. Item 2 does not reach them at
all (*"we never pass `-H`. Measured across the codebase."*), item 3 is covered by
their escaping, and item 6 they decline to argue us out of.

**Item 2 is the one worth reading.** The filter description was a ternary cascade,
so `hdcd` matched first and `aemphasis` was never reached; audio, log and cue were
**self-consistently wrong**, and a reader checking one against another found
agreement. The composed chain needs two explicit `aresample` bridges, because
libavfilter's `hdcd` filter calls `avfilter_graph_set_auto_convert(NONE)` in its
own init and that setting is **graph-wide** — the plain chain does not mis-render,
it fails to configure. `aformat` cannot substitute: it constrains a link and
relies on the converter that is switched off. Both were tried against libavfilter
directly before either was written.

### Four things found here since the close, none of them lap material

Under the 2026-08-26 reform findings go in commit messages and `Changelog.md`,
which they can read from git and which need no reply.

- **The provider contract published lines the binary never printed.** The
  generator deleted every `\n` in a format string, including **interior** ones,
  fusing two printed lines into one string. It reached **P2** — the surface we
  undertake not to reword without a round — where `cyanrip_log.c:635` published
  `Embedded cover art:    %s: %ix%i %s` while a real rip prints the label and the
  value on separate lines. P5 was worse: `...for writing: %s!Invalid folder name?
  Try -D <folder>.` ran two sentences together with no separator at all. **Nine
  rows** across P2, P3 and P5. Fixed at `1c96c8d`; the corrected contract is the
  commit after. **This is a change to what the contract publishes and is round-16
  material**, even though the binary did not move.
- **`tools/message-witness.py`** answers a question P5 could not: which of its
  messages does anything here actually assert? The 2026-09-05 audit put it at
  "~20 of ~128" as a lead. **Measured: 7 witnessed, 107 with no witness, 6
  unprobable** — a literal prefix too short for a probe to discriminate, counted
  in neither column. It found the fused-line defect on its first run. It gates
  drift and a floor, never full coverage: most of P5 needs a drive, a network or
  an allocation failure, and a permanently red gate is one nobody reads.
- **`check-settled.py` truncated any check command containing a backtick** and
  handed the fragment to the shell, which then failed on an unterminated quote —
  reported as a **stale fact** rather than an unreadable row. Fixed at `c399f44`,
  and the first diagnosis was wrong: the note blamed the `\|` escape, which
  survives fine.
- **`README.md` displayed upstream's green CI badge** at the head of a section in
  this fork's README, for a repository whose own CI has never executed a run.
  Now says whose it is (`6e74343`).

### The shared file has a SECOND wrong row, and they found it

`docs/seam-commands.md` line 504 publishes `-p '99=drop'` as accepted / exit 0;
the binary refuses it. **Line 97 publishes `-D` as `directory` / `str, path` /
`writable` / "output directory".** It is `folder_scheme`, *"Directory naming
scheme"* (`cyanrip_main.c:1603` at the pin) — a **relative scheme**, with `-F` its
per-track sibling. Their lap 16 §B3, read from our source at `978f9b0` and
re-checked here.

**Two is a pattern where one was a coincidence**, and the `-D` row is not
incidental: its real semantics are exactly why held item 4 mattered, since an
empty leading component made a multi-component scheme resolve **absolute**. A
reader who believed line 97 would not have looked.

**THREE, counting §7's overclaim, and all three now live in one place** —
`docs/KNOWN-ISSUES.md`, *"`docs/seam-commands.md` carries THREE known-wrong
statements"*. They were split across this file and that one, which is how a set
of three reads as three unrelated one-offs instead of a document to fix. They
are a **round-21 bundle**: one joint version bump, three rows, shipped by both
sides on one day. Not added to round 20 — R1 fixes the conditions at lap 1 and
none of these breaks anything in `fe4d2c4`.

**Neither cell is corrected.** The file is jointly owned; a correction is a
version bump both sides ship. **They assent to the `--check` remedy** (lap 16 §D)
with two riders we accept: the delimiters must not claim prose either side wrote,
and **the regenerated table must name the build it was measured from** — a shared
hash cannot prove the bytes describe the binary, and neither can its replacement
unless it says which binary.

### Their §G asks one question, and our answer is no

They ask whether our side has a mechanism making a lap's **sent/unsent** state
visible in the tree. **We do not, and we have the same failure at least three
times**: `56e7d71` withdrew a committed lap 5 that was never sent, `d360c38`
edited lap 14 after committing it, `6239860` replaced a lap 13 we had already
answered. Each was stopped by the operator, not by a check.

The reason is structural rather than an oversight: **"sent" is an event outside
both repositories**, so neither tree can observe it. The only in-tree evidence is
the peer quoting the hash back — the check they built, and which they correctly
say is not sufficient. Whether *committed* can stand in for *sent* is a real
trade with a real cost: it is strictly stronger and checkable, and it would have
forbidden our own `56e7d71` withdrawal. That belongs in the round-16 opener.

### What is still not verified, and no green suite implies it

**This section went stale and was contradicting both `SETTLED.md` and the
canonical list above.** It said *"no hardware has run since the run that closed
this round"* — three rig sessions have run since (2026-09-10 `ddc1e8c`,
2026-09-11, 2026-09-12 `fe4d2c4`) — and it listed *"`-x` alone returning a
drive"* as untouched, which `SETTLED.md` row 87 settled on **2026-09-11**:
`-x -l 1 -o pcm` direct to the container binary, exit 0 in 3m51s, with the
`Cache model:` line taking its `-x` arm for the first time on hardware.

**The canonical unverified list is the one above**, under *"What is still not
verified, and no green run will imply it"*, and it is the only one this file
should carry. Two sections answering one question is how the answers come to
differ — the sibling problem this project's document rule names, found here in
our own file while auditing lap 1.

What remains true of this round's landed work: **none of it has been on a
drive.** In particular item 2 changes **audio** for `-H` on a pre-emphasised
disc, and item 6 changes what happens when a network endpoint stalls — neither
of which any fixture here can exercise.

**Nothing in this section's landed work has been on a drive.** In particular
item 2 changes **audio** for `-H` on a pre-emphasised disc, and item 6 changes
what happens when a network endpoint stalls — neither of which any fixture here
can exercise.

## Releases — read the channel, never the version string

**`0.9.4-rc2+platterpus.11` is a STABLE release.** The `-rc2` is upstream's own
string, copied verbatim because we may not mint in `cyanreg/cyanrip`'s namespace;
the part that advances is `+platterpus.N`, which SemVer says MUST be ignored for
precedence. **A check that reads the shape of the version will call this a
pre-release, and it will be wrong.** Order by `release_seq`, read the `channel`
column of `release-manifest.json`.

**There is no tag.** Tag pushes are `HTTP 403` from the environment this is built
in, and `git ls-remote --tags origin` returns nothing. No release of this fork has
ever been reachable by tag. The commit SHA and the manifest row are the whole
identifier.

| field | value |
|---|---|
| **stable version** | `0.9.4-rc2+platterpus.12` |
| **stable commit** | **`fe4d2c4`** |
| stable build tag | `platterpus-fork-gfe4d2c4` |
| stable install | `https://github.com/rmccann-hub/cyanrip/archive/fe4d2c4.tar.gz` |
| stable `release_seq` | 22 |
| stable authorised by | handshake round 17, closed `GO`/`GO` on `fe4d2c4` / `45663c3` |
| | |
| **beta version** | `0.9.4-rc2+platterpus.12` |
| **beta commit** | **`fe4d2c4`** |
| beta build tag | `platterpus-fork-gfe4d2c4` |
| beta install | `https://github.com/rmccann-hub/cyanrip/archive/fe4d2c4.tar.gz` |
| beta `release_seq` | 22 |
| beta authorised by | handshake round 17, closed `GO`/`GO` — same build as stable |

`beta` resolves to the newest row of *any* channel, so opting into pre-releases
can never move a user backwards. Both channels resolve to `978f9b0`; there is no
separate beta to take.

**`+platterpus.8` (`796df32`, seq 18) is superseded and should not be installed.**
It is still in the ledger, because the ledger is append-only and a published build
is a fact, but no channel resolves to it any more.

Build command: `meson setup build -Ddeclare_released=true && ninja -C build`.

`release-manifest.json` is the only mechanism to install from and it is what
resolves these; this table is a human-readable copy of it and the test exists
because a copy rots.

**No release is coming while round 16 is open.**
`tools/release-gate.py --release-gate` exits 1 on this tree and names round 16,
which is correct and is not being overridden. Work has landed on
`platterpus-fork` since the pin — all of it documentation, tests and tooling,
none of it in `src/`.

## Round 15 — closed at 16 laps

| | |
|---|---|
| **opened** | our lap 1, on the released pair rather than a test pin |
| **close condition** | **one, fixed at lap 1 under S-13: CC-1**, a hardware acceptance pass on the released pair. **Met** |
| **pin** | `978f9b0`, unmoved all round on both sides. No test pin was ever declared |
| **closed by** | our lap 14 (`GO`) and their lap 15 (`GO`), each transcribing the other |
| **their lap 16** | out of order, `GO`/`GO`, **no reply owed**. Four fixes on their side, an assent, and one question (§G, answered above) |
| **next** | **round 16, ours to open.** Not yet open |

**The reform's measure is lap count, and round 15 ran to 16.** Round 14 ran to
nineteen; the reform's own test was *"round 15 closes in three laps or the reform
failed"*. It did not. Sixteen is better than nineteen and it is not three, and
saying so is cheaper than explaining it away.

### The digest methods no longer differ — seven consecutive agreeing values

Lap 2 declared `a1ff77af1fd6e3cb over 1` where we derived `c8fa5d93d9af5a20`:
same population, different construction. Lap 3 §3 shipped our full spec and
asked them to adopt one or tell us to adopt theirs.

**They adopted ours and built it independently** (`scripts/round_digest.py`),
having first reproduced both of lap 2's numbers. Every value since re-derives
here exactly, in both directions:

| lap | declared | |
|---|---|---|
| theirs 4 | `1ad28e7744de3d6b over 3` | reproduces |
| theirs 5 | `ddc0d8a741f76b60 over 4` | reproduces |
| theirs 6 | `09268d7203773872 over 5` | reproduces |
| theirs 7 | `60a7c64dc252b1fa over 6` | reproduces |
| **ours 8** | `44e14b452950ebb0 over 7` | **they reproduce it** — their lap 9 §B2 |
| theirs 9 | `35b861f25abfa69c over 8` | reproduces |

**Two implementations of one written spec, agreeing on six consecutive values,
neither having read the other's code.** Their §B2 makes the point that matters:
two implementations agreeing is weak evidence when they share an ancestor and
strong evidence when they do not. These do not.

The allowlist entry in `tests/release_gate.py` stays pinned to lap 2's declared
value, because lap 2 is immutable and was computed by the old method.

### The process reform — 2026-08-26, on the maintainer's instruction

Round 14 ran to nineteen laps with every rule followed, which is round 7's failure
repeated. **Cut: §J as a requirement, acknowledgement laps, "send a file even when
nothing changed", and findings written up in laps.** Kept: every rule about
evidence. **One file per exchange and it is the lap** — the repository is the
transport, and a test does not travel, its specification does.

**The measure is lap count and round 15 is at 3.** `docs/SETTLED.md` is the index
that stops facts being re-derived, and `tools/check-settled.py` runs every row's
check.

---

## What we know about their side, and how we know each part

Separated by provenance, because these are different strengths of claim.

| | |
|---|---|
| `0.6.34` is what ran on 2026-09-03 | **measured**, from `Consumer:` in every log we hold |
| `0.6.33` at `0a69732` is their round-15 release | **read from their lap 2 §B** |
| `0.6.34`'s commit | **unknown.** Nothing we hold names it; the `Consumer:` string carries no SHA |
| their `0.6.33` banner reads `platterpus 0.6.33 (0a69732)` | **UNVERIFIED.** Lap 3 said the next bundle would answer it. It does not — the bundle is `0.6.34` |
| `0.6.34` treats `978f9b0` as `unapproved` | **measured**, from their JSON: *"NOT the build this Platterpus was verified against (platterpus-fork-gd9c058c)"* — which is round 14's pin, so the field is right and round 15 is what changes it |
| their `FORK_PIN` is `ddf7ac3`, unmoved | **read from their round-14 lap 7 §W2** |
| **`0.6.22` NEVER EXISTED** | **read from their standing status**, which corrects their own lap 4 |

**`session/DIAGNOSTICS.txt`'s banner names `+platterpus.10` / `d9c058c` while
every rip in that bundle was made by `+platterpus.11` / `978f9b0`.** Not a defect:
the banner names the **approved** pair, not the running one. Checked before it was
written down, because the shorter reading was "their diagnostics are stale".

### Where their statuses are filed

`docs/handshake/inbound/status-2026-08-21-v0.6.21.md`,
`status-2026-08-21-v0.6.23.md` and `status-2026-08-24-v0.6.23.md`. All three, kept
dated, even though *their* rule is to rewrite in place.

**The last two share a version and differ in date, which is the whole argument for
keeping both.** Same declared version, two different claims about the world. Under
their own rule the first no longer exists on their side; under ours it is evidence
and is kept. **The date in those filenames is the one the document declares, not
the day we received it**, and the two differ.

Neither declares a wire header, so no enumerator can count them — and
`test_a_standing_status_is_never_counted_as_a_lap()` executes that rather than
asserting it, including the case a rename would hit.

## Upstream: one commit inbound, deliberately not merged

Upstream moved on 2026-08-24: `f8ebf48`, *"src/musicbrainz: retry queries when
busy"*. **Our mirror is synced; `platterpus-fork` does not contain it.**

It adds two log lines — `Retrying in %_ seconds (attempt %_ out of %_)...` and
`MusicBrainz lookup failed, try again later,` — **neither of which can appear in a
Platterpus rip**, because they pass `-N` and `-N` disables the lookup entirely.
Recorded anyway, because a log line entering our contract is handshake material
whether or not the one consumer we have can reach it. The analysis is
`docs/upstream/sync-2026-08-24-mb-retry.md`.

**Three defects of ours are verified as present upstream and not yet contributed
back**: the signal-handler deadlock, SIGTERM unhandled, and the completion-footer
skip. Each has its re-check in `docs/SETTLED.md`.
