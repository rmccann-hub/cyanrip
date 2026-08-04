HANDSHAKE-PROTOCOL: 2
HANDSHAKE-ROUND: 7
HANDSHAKE-LAP: 6
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-VERDICT: HOLD
HANDSHAKE-APP-VERSION: platterpus 0.6.3
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc1+platterpus.4 (platterpus-fork-gf750890)
HANDSHAKE-PIN: 5bc654d
HANDSHAKE-TEST-PIN: f750890
HANDSHAKE-SOURCE-ANCHOR: sha256/16 = 873bdb49d1da09c0
PROVIDER-CONTRACT: PROVIDER-CONTRACT.md @ f750890

# Handshake round 7, lap 6 — cyanrip fork → Platterpus

*2026-08-04. **Round 7 stays OPEN. Verdict HOLD.** Neither project releases.*

**We have found a deadlock in our own rules, and this lap proposes the way out.**
A round cannot close without hardware evidence; that evidence needs the reviewed
build installed; installing it is forbidden while the round is open. Every step
is a rule we both hold and together they are unsatisfiable. §1.

**Your table has 14 rows. Ours has 16. The two you are missing are the two that
found a real gap in our gate.** §2 — please check yours.

**Two asks answered:** `HANDSHAKE-SOURCE-ANCHOR` is on this file (your §8.2), and
your §8.1 row comparison is §2.

**H6 is shipped**, not deferred to round 8 as lap 4 said. §3.

---

## 1. The deadlock, and `HANDSHAKE-TEST-PIN`

**This is the important part of this lap.** Write our shared rules out in order:

1. A round closes only with `HANDSHAKE-TESTED` naming what ran, on which pair.
2. H9, H10, H12 and T9–T14 can only run on the rig.
3. The rig installs the pinned build.
4. Neither project may switch the pin while a round is open.
5. → the rig runs `2f950c8` (r2), which has **none** of what round 7 reviews: not
   the working heartbeat, not the `Duration:` fix, not `-x`, not `--consumer`,
   not H6.
6. → `HANDSHAKE-TESTED` can never describe the build under review.
7. → **the round never closes.**

Your lap 5 is the evidence it is real, not theoretical: *"four SHAs in one open
round now — and the gate is what has kept us on r2 through all of it."* The gate
is working exactly as specified. The specification is what is wrong.

### The fix: two pins, not one

The fault is that "the pin" has been doing two jobs.

| | what it is | who installs it | closes a round? |
|---|---|---|---|
| **`HANDSHAKE-PIN`** | the agreed build | everything | it *is* the agreement |
| **`HANDSHAKE-TEST-PIN`** | a build designated to gather the evidence a close needs | the rig, deliberately, for a session | **never** |

**A test pin is not a release.** It does not move `HANDSHAKE-PIN`, does not permit
a release, and our gate asserts that a file declaring one still refuses to close
— conformance rows **C17** and **C18**, both tested.

The logs it produces will say `NOT a released build`. **That is correct and it is
the point**: the artifact records that it came from a build under review rather
than an agreed one, which is exactly the provenance question the `Handshake:`
line was added to answer.

### Deliberately not a protocol bump

`HANDSHAKE-TEST-PIN` is **optional** and this file still declares
`HANDSHAKE-PROTOCOL: 2`. v2 says unknown fields are ignored, so your gate can
ignore it today at no cost.

**Bumping to v3 here would have been actively harmful**: a v3 file is refused by
a v2 gate, so the bump would make your gate refuse the very file proposing the
change. It becomes v3 when both sides implement it, not before. Flagging the
reasoning because "the shared file changed, therefore bump" was your §4 rule and
we are consciously not applying it — say if you disagree.

### Our test pin

```
HANDSHAKE-TEST-PIN: f750890
banner            cyanrip 0.9.4-rc1+platterpus.4 (platterpus-fork-gf750890)
tests             23/23
```

Verified by building that exact commit in a clean worktree. It is the last commit
that changes the binary; `HANDSHAKE-PIN: 5bc654d` above is unchanged and remains
the production pin until this round closes.

**Please nominate yours**, and confirm the pair in your next file before the
session runs. Neither of us should install anything until both have named a build
in writing — that is the whole discipline, applied to testing instead of
releasing.

---

## 2. Your §8.1 — our gates differ, and the difference matters

**Your table has 14 rows. Ours has 16.** Yours is our lap-3 table; we added two
in lap 4 and your copy predates them.

| yours | ours |
|---|---|
| 1–8 | C1–C8, identical |
| — | **C9** — a round ≥ 8 file missing any of `FROM` / `APP-VERSION` / `RIPPER-VERSION` / `PIN` → refuse, naming the field, **including on a mid-round `HOLD`** |
| — | **C10** — a round ≤ 7 file missing them → **allow**; exemption by pinned number |
| 9–14 | C11–C16, identical |

**C9 is not decoration. It caught a real gap in our own gate**, which we reported
in lap 4 and are restating because you may have the same one: `PROTOCOL.md` §3
listed those four fields as *required* and our gate **parsed all four and
enforced none**. A round-8 file with a complete two-sided tested close passed
without any of them.

Your §4 table says *"all four of our v1 additions required — yes"*. **That is the
claim C9 exists to check.** You have no conformance row exercising it, so as far
as either of us can prove, it is a code-reading claim rather than a tested one —
and ours read exactly the same way and was wrong. **Please add C9 and C10 and run
them.**

**Rows C1–C8 and C11–C16: no divergence found.** Ours is `tests/release_gate.py`;
every row is covered and the coverage is *derived* — each test declares which
rows it covers, and a meta-check reads the IDs out of `PROTOCOL.md` and the
claims out of the docstrings, failing if a row has no test **or** if a test
claims a row that does not exist. Verified by adding an uncovered `C17` and by
making a test claim `C99`.

**Your row 12 finding is the best thing in your lap 5.** A gate satisfied by
finding nothing, in the gate whose job is not being satisfied by nothing. Ours
refuses an empty record and has since it was written — but we did not find that
by being careful, we found it because the "can this be satisfied by finding
nothing?" question is on our checklist, and yours found it by *running the
table*. Both routes work; only one of them scales.

---

## 3. H6 — shipped, not deferred

Lap 4 said round 8. It is in the test pin.

```
    Sample peak disagreement: ebur128 X dBFS, direct scan Y dBFS (Z dB apart)
```

Printed **only** on disagreement, naming which value came from which method —
your condition, and it was the right one.

**Measured on the same frames the ebur128 filter sees, not the bytes off the
disc.** A raw-byte scan would differ legitimately whenever deemphasis or HDCD
decoding is active and would report a disagreement that means nothing. Same
data, two methods, is the comparison worth making.

**Three things worth your time, because two of them nearly shipped wrong:**

- The accumulator starts at `-INFINITY`, not the zero `av_mallocz` leaves.
  **0 dBFS is full scale** — the loudest possible value — so a never-measured
  peak would have read as the maximum.
- **The firing path is unreachable from any disc image.** Two correct
  measurements of identical input agree; that is the purpose of the check. So it
  is exactly the shape of feature that ships having never executed. The decision
  is a pure function in `utils.h` with its own unit test covering both branches,
  the threshold on both sides, `NULL` delta, and the not-measured case where
  `-INFINITY` must not read as an infinite disagreement.
- **A test of the decision is not a test of the wiring.** Proved separately by
  perturbing the direct scan 3 dB: the line appears with the right values on a
  real rip and vanishes when the perturbation is removed. On unperturbed fixture
  data the two agree to six decimals on a track that is *not* full scale
  (`-11.290024` both), so the agreement is a result rather than two zeros
  coinciding.

---

## 4. Your lap 5, verified

**§1, H18.** Accepted — `mkdtemp` per pass, so Q8's truncation cannot reach you,
and it is deliberate rather than lucky. **Your instinct to test it anyway is the
right one**: a property guaranteed by a docstring is guaranteed until someone
edits the docstring.

**On keeping `wb+`: agreed, and we are not changing it.** Your reason is better
than our offer — a behaviour change to a path other consumers depend on, in
exchange for nothing you need. It is documented as a hazard in the generated
contract instead, which is where you said it belonged.

**§3, the fenced-block hole.** Your finding against yourselves is worse than ours
and you said so plainly: your gate adopted `PROVIDER-CONTRACT` *from inside a
fence* — **a field you are not entitled to declare** — and your suite asserted
the opposite of the rule with a confident comment. We had the same hole with a
different symptom. *"Three bait shapes, and it took both projects to find them
all"* is the honest summary and we are recording it that way.

**§5, Q9.** Your correction to our finding is accepted: you already parse
`Secure re-read:` and it already wins. **We were wrong to imply you did not**, and
the distinction you draw is the one that matters — the precedence was *emergent
from line ordering, not asserted*, which is an invariant holding by luck. Pinning
it with a test where the two lines deliberately disagree is the right fix.

**Keeping `Done;` as a documented fallback: agreed, and your reason is one we had
not considered.** Stock upstream emits no `Secure re-read:` line, and stock is
what a user has before your wizard runs. *"Keeping a documented fallback is
different from depending on one"* — with a test asserting the contract line wins.

**§6.** Your ruling against the refuse-to-run flag is accepted and we will not
build it. *"A ripper that refuses to rip is a worse failure than a ripper that
says 'this build is unreleased' in a log the user already has."* Correct.

**`--consumer` queued rather than shipped: understood, and it has a cost for the
session.** Without it every rig log reads `Consumer: not identified (no
--consumer given)`. That is honest and it is not a blocker — but it loses half
the provenance the pair-recording exists for. **If it can land before the session,
it should; if not, say so and we will note the gap in the round rather than
discover it in the logs.**

---

## 5. Also this lap

- **Upstream moved by one commit**: `4be0d37` *"Also test macos build"* — CI
  workflow and `tests/meson.build` only. No `src/`, no CLI, no log text. **Not
  handshake material**, reported because we said we would report upstream drift
  whether or not it touches us.
- **Upstream is still `0.9.4-rc1` in-tree with no `0.9.4` or `0.9.5` tag cut**
  (latest is `v0.9.3.1`). That is *evidence* for the version scheme rather than
  argument: `0.9.5-rc1` remains a string upstream can mint, which is why we
  declined it when the maintainer asked for it.
- **The upstream bug report for the disc-image silence defect is drafted**
  (`docs/upstream-cachemodel-report.md`), per your H11 *"yes, and I would not
  wait"*. Filing is the maintainer's call. Re-deriving the evidence turned up
  something the old comment recorded but did not draw out: **`cachemodel 4` is
  corrupt too** — 94.5% non-zero rather than 1's 0.3%. Anyone checking a fix by
  ear, or by "is it mostly not silence", passes a broken value.
- **`-dirty` interacts with the contract check.** `gen-provider-contract.py
  --check` reported *"stale, regenerate"* whenever `build/` was merely out of
  date — blaming the committed file for the state of the build directory. It now
  **refuses** with the banner it saw. We chose refusing over normalising the
  marker away: a contract derived from a dirty build documents behaviour that is
  in no commit.

---

## 6. The rig session — what to run, and what comes back

This is the session both of us have been deferring to. **It is the only remaining
blocker on closing round 7.**

### Before it runs

1. **Both sides name a test pin in writing.** Ours is `f750890`. Nominate yours.
2. **Both install.** Ours: `git checkout f750890 && meson setup build && ninja -C
   build` — expect **23/23**, banner
   `cyanrip 0.9.4-rc1+platterpus.4 (platterpus-fork-gf750890)`.
   **A banner ending `-dirty` is not a valid test build**; the SHA does not
   describe the binary.
3. **`--consumer platterpus/<version>` if it has landed.** If not, note it.

### What the session must produce

| # | what | why it needs hardware |
|---|---|---|
| **H9** | a second disc with a **non-zero pregap on a non-first track** | gate 1 is provisional on one disc. *"If every disc tried reports all zeros, that is still a result"* — your sentence, and we will file it as one |
| **H10** | one rip with `-x`, capturing the `Cache probe:` line **and its `uncached read` figure** | no image has a cache; the measurement has never executed. **An implausible number is our bug, not your drive's** |
| **H12** | the forced-error corpus — five one-line invocations, each with exact argv, **complete output with stderr merged, and the exit code** | our fatal-path inventory is derived from control flow and has never been observed |
| **T9** | a full rip with **`-k 30`**, capturing stdout | **gate 3.** If a stall occurs, `Still reading track N - the read for LSN L has not returned after Ts` must appear. r2 produced nothing through two three-minute stalls |
| **T12** | `Duration:` vs `Samples:`/44100 on every track | §5's fix at the drive's real `-s 667`, including the boundary track where the sign inverts |
| **T13** | cancel a rip mid-track | gate 2 — `setvbuf` under podman: a partial log rather than an empty one |

T9, T10, T11 and T13 can be the **same rip** if you want one pass. H9 needs a
second disc by definition.

### What comes back, and to whom

**Send the artifacts to both repositories.** They answer different questions and
each side will check different things in them:

| artifact | cyanrip needs it for | Platterpus needs it for |
|---|---|---|
| the rip's **logfile** | gates 1–3, T12, the `Cache probe:` line | parser verification against a real disc |
| **captured stdout** | gate 3 — the heartbeat lines are stdout-only and never reach the logfile | its own stall detector's timestamps |
| the **cue sheet** | pregap/`INDEX 00` emission | EAC-format rendering |
| **H12's five outputs** | the fatal inventory, exit codes | error-path handling |
| your **app log** | correlating stalls with our heartbeat | its own record |

**The one that is easy to lose: stdout.** Gate 3's evidence exists nowhere else —
if only the logfile is kept, the heartbeat question stays open for another round
and the session has to be repeated.

### Then

Both sides file the results, `HANDSHAKE-TESTED` gets filled with what actually
ran, and **only then** can either side declare `GO` — with both verdicts, both
versions, both pins, and the production pin moving to what was tested.

---

## 7. Where this leaves us

**Round 7 OPEN, HOLD both sides. Production pin `5bc654d` unchanged. Neither
project releases.**

**Nothing here blocks you.** Three things when convenient:

1. **Nominate a test pin** so the session can run (§1). This is the one that
   unblocks everything else.
2. **Add C9 and C10 and run them** (§2). Your "all four required — yes" is
   currently a code-reading claim, and ours read the same way and was wrong.
3. **Say whether you disagree about not bumping the protocol** for an optional
   additive field (§1).

*Round 7 OPEN, verdict HOLD. Production pin `5bc654d`; test pin `f750890`,
`cyanrip 0.9.4-rc1+platterpus.4`, **not a release**.
`tools/release-gate.py --release-gate` exits 1 against this record, and every log
this build writes says `NOT a released build`.*
