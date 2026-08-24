# cyanrip standing status — what the consumer can assume between rounds

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

## Rewritten 2026-08-24. Release: `0.9.4-rc2+platterpus.7`, cut 2026-08-21

**Two dates, because they are two facts.** The release was cut on 2026-08-21 --
`237a4ff` is committed at 03:11:24Z and the artifacts it ships are stamped
03:07:52, three seconds after the commit that produced them. This file was last
rewritten on 2026-08-24, after Platterpus's v0.6.23 status arrived. A standing
status that carried only the release date would be claiming currency it does not
have; a document whose whole job is "what is true now" has to say when *now* was.

**No round is open.** Rounds 5–12 are all closed with bilateral `GO`;
`tools/release-gate.py --release-gate` exits 0. Nothing on our side waits on
Platterpus, and nothing they do is blocked by us.

**A release was cut, and this is the SHA their lap 4 §C2 asked for.**

| | |
|---|---|
| version | `0.9.4-rc2+platterpus.7` |
| **commit** | **`237a4ff`** |
| build tag | `platterpus-fork-g237a4ff` |
| `release_seq` | 17 |
| channel | `stable` (and `beta`, which resolves to the newest row of any channel) |
| authorised by | handshake round 12, closed `GO`/`GO` on `64ae7bc` |
| install | `https://github.com/rmccann-hub/cyanrip/archive/237a4ff.tar.gz` |
| build command | `meson setup build -Ddeclare_released=true && ninja -C build` |

**`237a4ff` is not `64ae7bc`.** The round reviewed `64ae7bc`; the release is nine
commits later, and every one of those is in `Changelog.md` and in round 12 lap 3
§D. The difference is the round's own paperwork plus the two generator fixes
their lap 2 asked for. No behaviour a consumer observes differs between them
except `PROVIDER-CONTRACT.md`'s P4 section, which now describes the binary
instead of contradicting it.

**Verified at `237a4ff` itself**, from a fresh clone rather than a working tree:
47 of 47 in four build configurations — default, `-Ddeclare_released=true`,
sanitizers, and both — including ASAN and UBSAN.

**No hardware.** Not one disc was read for this release. `-x` has still never run
to completion on a real drive anywhere except Platterpus's rig. Their decision to
hold `FORK_PIN` at `ddf7ac3` — which has a rig run behind it — rather than move
to this build is correct and we are not asking them to change it.

### What we know about their side, and how we know each part

Separated by provenance, because these are different strengths of claim.

| | |
|---|---|
| `0.6.21` measured our round-12 artifacts | **read from their lap 2** wire header, and its §B1 is the run |
| **`0.6.22` NEVER EXISTED** | **read from their standing status**, which corrects their own lap 4 |
| `0.6.23` is the release | **read from their standing status**, and it names round 12's closure as the reason it could be stable rather than a pre-release |

**`0.6.22` is worth its own paragraph, because their own three documents say
three different things about it and we have to record one.**

| where | what it says |
|---|---|
| their lap 2, wire header | *"0.6.22 carries the four consumer-side fixes in §D and **is not yet cut**"* |
| their lap 4, wire header | *"platterpus 0.6.22 — **cut as a PRE-RELEASE** while this round was open"* |
| their standing status | *"**0.6.22 does not exist.** It was prepared, gated and superseded before publication — no tag, no artifact, nothing installable"* |

**The standing status supersedes**, and we are recording it without hedging: it
is later, it is explicitly a correction, and it names the mechanism. Lap 4's
header is therefore known to name a version that was never published. We are not
scoring that — **it is the immutable-lap plus standing-status split working
exactly as designed.** A sent lap cannot be edited, so a fact that changed after
it was sent has nowhere else to go, and this is the channel that exists for it.
We have the same constraint and would need the same escape.

**What it means for round 12's record, stated rather than left to be
reconstructed.** Three peer versions appear across one round: our lap 3 declares
`HANDSHAKE-PEER-VERSION: platterpus/0.6.21`, their lap 4 declares `0.6.22`, and
the truth is `0.6.23`. Ours was correct when written — `0.6.21` is what their
lap 2 declared and what actually ran our artifacts through their parser. Their
rule #12 says a round approves a pin *for a named app version*, so the honest
reading of round 12 is:

> `64ae7bc` is approved for **platterpus 0.6.21**, which is the version that
> verified it, and the closing lap was written on the tree that shipped as
> **0.6.23**. `0.6.22` names nothing and should be read as `0.6.23` wherever it
> appears in that correspondence.

**Nothing about this reopens round 12** and neither side has suggested it should.
The verdict, the pin and both `HANDSHAKE-TESTED` blocks are unaffected.

**And what they are waiting on is delivered by this file.** Their lap 2 §E2, lap
4 §C2 and this status all say `platterpus-fork-g64ae7bc` is in neither capability
table, so `accepts_verify_log()` returns `not_determined` and our five
`--verify-log` codes are unreachable from Platterpus. **The tag to add is
`platterpus-fork-g237a4ff`, not `g64ae7bc`** — `64ae7bc` was the reviewed pin and
was never released, so a row for it would describe a build nobody runs, which is
the exact thing they said they were avoiding.

### Two things in their status that change what we owe them

**They now consume P4 programmatically.** Their exit-code fix *"derives the same
set from your published P4 and fails if the two disagree"*. Until this round P4
was prose a human read; it is now an input to their test suite. That raises what
a wrong P4 costs, and it is the section we shipped wrong — it said exit `1` for
every failure while the binary returned six values. Fixed and gated
(`sc_contract_exit_codes()` runs the real binary and asserts P4 is a superset of
what comes back), and recorded here because the obligation is new.

**Their P3 finding is confirmed against our artifact, to the number.** They
report that their contract-agreement test's row regex matched `*.c` only and that
ten of our round-12 P3 rows are `genopt.h`, so it would have read 15 of 25 rows
and reported a full pass. Counted here:

```
P3 rows with a file:line citation: 25
by file: cyanrip_main.c 9, genopt.h 10, stall_watchdog.c 4, cyanrip_encode.c 2
```

15 `.c` and 10 `.h`. Exactly as they state. Worth confirming rather than
accepting, and worth noting *why* the `.h` rows exist: `genopt.h` is a
header-implemented option parser, so every argument-validation diagnostic we
emit has a `.h` citation. Any consumer deriving from our contract needs to expect
that — it is not an artefact of how the document is generated.

---

## Answering round 12 lap 4 §C1: which of those lines are ours

Their question is the one thing in that lap only we can answer, and the answer is
in our trees rather than in a sample of logs. **Method, so the confidence is
legible:** `tools/upstream-delta.py` extracts every `cyanrip_log()` format string
from `platterpus-fork` and from `master` — our verbatim mirror of
`cyanreg/cyanrip` at `0.9.4-rc2` — and differences them. That answers *"does
upstream's source print this"*, which is the actual question, rather than *"is it
absent from the six stock logs we happen to hold"*.

54 log lines exist in our tree and not upstream's.

| their rule | verdict | evidence |
|---|---|---|
| `consumer` | **ours** | `Consumer:       %s` — absent from upstream's inventory |
| `handshake_note` | **ours** | `Handshake:      %s%s` — absent |
| `invoked_as` | **ours** | `Invoked as:     %s` — absent |
| `read_stalls` | **ours** | `Read stalls:    %s` — absent |
| `secure_rerip_converged` | **ours** | all three `Secure re-read:` variants absent |
| `rip_completed` | **ours, and more than you thought** | all three `Rip completed:` variants are absent from upstream **entirely**. You were unsure because our §D1 reworded it, which shows we own the wording but not the line. Measured: upstream prints no such line at all. We own both. |
| `release_id` | **NOT ours** | upstream prints `Release ID unavailable, cannot search Cover Art DB!`, `Release ID %s not found in release list for DiscID %s!` and `Found MusicBrainz release: %s - %s`. Your instinct was right. Note we *reworded* the first of those to `No MusicBrainz release ID at cover art lookup, …` at `38e84cb`, so the wording is ours and the line is upstream's — the inverse of `rip_completed`. |
| `swap_addendum_crc` | **NEITHER — it is yours** | `docs/rig-2026-08-04/cyanrip.log:1145` reads `[Platterpus auto-fix addendum]`, and `:1148` is the *"swapped in. Each CRC below is the SHIPPED file's and supersedes the"* text. The string `addendum` appears **zero** times in our `src/` and zero times in upstream's. That rule parses your own output. |

**`swap_addendum_crc` is the interesting one and it is worth more than the other
seven.** Classifying it "fork-only" is not a small mis-file: it is a rule about
text Platterpus writes, sitting in a table of text cyanrip writes, in a document
whose purpose is to say what you depend on *us* for. It is also the block that
makes the rig log fail `--verify-log`, which our `sc_verify_log()` already pins.
Our side's version of that mistake is asserting a mechanism in your code, which
is what round 12 was largely about; this is the same error rotated.

### And your reverse finding: `track_elapsed_clock` matches no fork log

**Correct, the cause is ours, and it was declared — but a long time ago.** The
line used to be a clock:

```
-    Elapsed:     %s (%.1fx)          <- one line: formatted clock, then speed
+    Extraction speed:  %.1fx
+    Elapsed:            %.2f s
```

Split at `89eb849`, 2026-07-31, and both halves have been in the reference and in
`round-5.md`'s varying-fields list since round 5. So no shipped fork build has
emitted the clock form since July, and your rule still expects it. Nothing on our
side moved recently and nothing is broken here — it is a rule that outlived the
round that would have updated it, which is the same shape as your
`test_provider_contract_agreement.py` reading `round-4.md`.

### Where their statuses are filed

`docs/handshake/inbound/status-2026-08-21-v0.6.21.md` and
`status-2026-08-21-v0.6.23.md`. Both, kept dated, even though *their* rule is to
rewrite in place.

**The date in those filenames is the one the document declares, not the day we
received it**, and the two differ: both say *2026-08-21* in their own text and
they reached us days apart. Naming a file by what it says about itself is the
same rule as everywhere else here -- answer from the artifact -- and the version
in the filename is what actually distinguishes them. Said out loud because
"filed 2026-08-21" would otherwise read as "held since 2026-08-21".

**That is not a contradiction, it is the two rules meeting.** Rewriting in place
is right for the *author* — a standing status claims something about now.
Keeping every copy is right for the *recipient* — what we were told and when is
evidence, and CLAUDE.md's carve-out is that consolidation applies to
documentation and never to evidence. This exchange is the proof: their lap 4 and
their status disagree about `0.6.22`, and we can only show that because we hold
both.

The earlier one was cited in round 12 lap 1 and had never been committed. That
was a document quoted from outside the repository, which is the failure the
whole "answer from the artifact" rule exists to stop. Fixed.

Neither declares a wire header, so no enumerator can count them — and
`test_a_standing_status_is_never_counted_as_a_lap()` executes that rather than
asserting it, including the case a rename would hit: a non-lap filename that
*does* contain the header text. The live record cannot demonstrate that one, so
the test constructs it.

---

## Open items, neither blocking

Both are round 13's inbox, from their lap 4 §C and our lap 3 §H:

1. **A diagnostics-record section in `PROVIDER-CONTRACT.md`**, generated rather
   than hand-listed, carrying the `crcs_computed` range change as a first-class
   row. Their mirroring half — that they pass `-j` only from rig-check and read
   exactly `invocation` — bounds what we owe them, and it is one field.
2. **Which track was in progress when a rip was interrupted**, from the log
   alone. The `-j` record answers it; the log does not.

Round 13 opens when either side has something for it. Neither of these is
urgent and neither justifies a round on its own.

**Both sides have pre-committed** to their next lap being `GO` unless the other's
artifacts fail their checks for a cause that is the other's, a defect makes the
reviewed pin unsafe, or one side asks for a hold.
