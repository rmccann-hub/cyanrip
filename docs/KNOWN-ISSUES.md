# Known issues — cyanrip fork

**What this is.** Every defect and gap in *our own* code and tools that we know
about and have not closed, in one place, with an honest status on each. Assembled
2026-08-13 by deriving from the tree — `grep` for `TODO`/`FIXME`, the handshake
laps' disposition tables, and the hardware list in `CLAUDE.md` — rather than from
memory.

**Why it exists.** The state was recoverable only by reading thirty append-only
lap files and reassembling their disposition tables. That is a real cost paid
every time anyone asks "what is still wrong?", and the answer was drifting
because each lap only knows about its own round.

**What it is not.** Not external bugs we work around — those are in `CLAUDE.md`,
"Known external bugs worked around here". Not designs we chose not to build —
those are `CLAUDE.md`, "Planned, not built". Not a description of behaviour we
*have* — that is `PROVIDER-CONTRACT.md`, and it is generated.

**Rules for this file.** An item leaves only when it is fixed and a test pins
it, or when it is shown never to have been real. An item that turns out to be
someone else's is moved, not deleted, with a note saying where. Nothing here may
say "probably" without saying what would settle it.

---

## Fixed 2026-09-16, round 21 — both agreed in round 20 and neither shipped inside it

*The middle row is the exception and says so in its own cell: it was FOUND
while doing round 21's work, deferred for a reason that was about round 21's
pin, and fixed in round 22 once that reason was spent. It stays here because
this is where a reader tracing the footer move lands, and a table grouped by
when something was found is not the same as one grouped by when it shipped —
the cell carries the second date so the two cannot be confused.*

| what | how it is pinned |
|---|---|
| **`Ripping errors:` was written before the encoders were asked how they did.** Under a 32 KiB write cap the muxer's trailer write fails, `-j` recorded 2 and the process exited 1, and the log said `Ripping errors: 0` and `Rip completed:  yes` over a 32768-byte file whose intact form is 253742 — two records of one run, and the human-readable one, the archival one, was the wrong one | `cyanrip_log_finish_report()` moved below the encoder-status loop, still inside `end:` so round 14's twenty-four-`goto` property is untouched. `sc_encode_failure_reaches_the_log()` asserts the two records are **equal** and separately that they are **non-zero**, so the property cannot be met by both being 0. Revert-proved with the build confirmed green |
| **A SOURCE COMMENT CITES A TEST THAT WAS RENAMED IN THE SAME ROUND.** `src/cyanrip_main.c:2703` — the long comment justifying the footer move — says the defect was *"demonstrated rather than argued in `sc_encode_failure_is_absent_from_the_log()`"*. That scenario is now `sc_encode_failure_reaches_the_log()` (`tests/rip_images.py:1706`, `tests/meson.build:517`), and the rename is recorded in the test's own docstring. **A `file:line`-style citation that resolves to nothing is the defect this project fixes everywhere else**, and a reader following it gets no hits. Found 2026-09-18 while writing the rig README that quotes the same comment | **FIXED IN ROUND 22**, at the commit carrying round 22's first log change. It was deferred *because of the pin*: `git diff --stat 3952c03 HEAD -- src/` was empty, so every claim about the reviewed pin's source held of `HEAD` too, and editing a comment would have moved that hash and `PROVIDER-CONTRACT.md`'s source anchor for a comment. **Round 22's first fix moves `src/` anyway**, so the reason is spent and the citation is corrected in the same change rather than carried another round. The comment now names both spellings and says which round renamed it. Round 21 lap 1 §1.2 keeps the old name, because a sent lap is never edited |
| **`Frame retries:` named half of what `-r` does** — it caps paranoia's per-frame retries *and* the whole-track repeat ceiling, and the log printed a bare number with nothing saying they were one knob | now `Retry limit:    N (per frame, and per whole-track re-read)`, the exact string Platterpus assented to in round 20 lap 2 §0.2. `-j`'s key follows it (`frame_retries` → `retry_limit`) and the record's schema moved twice inside round 21 — the rename took it to `cyanrip-diagnostics/5` and §4b's `cache_probe` block took it to **`/6`**, which is what the test pin emits. `src/diagnostics.c:371` is the artifact; this cell said `/5` for two days after `/6` shipped. `contract_covers_log` and `contract_diagnostics` both fired on the change and pass on the regenerated contract |

**The fix made two things visible that it did not fix**, and they went into the
open list below rather than being closed quietly: the per-track block said
`Track N ripped and encoded successfully!` over a `File(s):` list computed from
the request, and `Rip completed:  yes` now sits beside a non-zero error count.
**Both have since been answered and neither by this fix** — the first half of
the first was split in round 22 (`89a57d6`; `File(s):` is still open), and the
second was put to Platterpus, who ruled *leave it alone*.

**And one comment was wrong about Platterpus's code for four rounds.** The
schema-bump rationale in `diagnostics.c` cited `SUPPORTED_SCHEMAS = {1, 2}` as
an allowlist over *this* record. Read at
`platterpus@d94bd113:src/platterpus/deps/ripper_manifest.py:89`, it gates
`release-manifest.json`, whose schema is 2; nothing in their tree parses
`cyanrip-diagnostics` at all. Round 12's defect, re-imported into our own
source, surviving on its own closing clause — *"we cannot read their source and
do not claim to"* — which has been false since 2026-09-13.

---

## Fixed 2026-08-15, from Platterpus's known-issues hand-off and one rig hang

| what | how it is pinned |
|---|---|
| **`cdio_cddap_open()` can block forever with no output.** The stall watchdog started ~1700 lines later, so the one window where cyanrip can block before saying anything about the disc had no liveness signal. A rig session sat 300s on `Opening drive...` and left a 111-byte artifact | `crip_stall_wait_begin/end()`, 5 assertions in `tests/stall.c`; revert-proved. **The hang itself is hardware-only** — an image opens instantly |
| `-j` asserted `messages_are_complete: true` while 55 log lines were absent | `messages_scope` + `messages_complete_within_scope`, 4 assertions in `tests/diag.c` |
| `-p 99=drop` accepted, exit 0, never applied | bounded against the disc after the TOC read; `errors` scenario asserts both ends |
| `-l` wrote an `INDEX 00` into a FILE the rip never produced | rip-set input to the predicate + an EOF invariant; `cuegap.c` and the `pregap` scenario |
| the contract could not see composed lines, wrapper macros or ternary labels | generator follows one helper hop, finds wrappers structurally, enumerates ternary arms; 343 stable rows |
| nothing tied a lap's claim about the generating build to the contract | `contract_build` recomputes the source anchor |
| album loudness had no cyanrip-owned row at all | four owned rows, `album_loudness` scenario asserts them against libavfilter's own block |
| a zero AccurateRip checksum printed as `match found, confidence N` | distinct state, no confidence figure |
| `Elapsed:`/`Extraction speed:` interval undefined | defined in the contract's units block, derived from source |

**One of these was already fixed and we did not know it.** `C2 errors:` has said
`supported by drive, not used` since `8499890`; the contract published the row
as `%s`, so a delivered fix stayed invisible for a round. That is the same
defect as the composed-line gap, measured from the consumer's side.

---

## Fixed 2026-08-13, listed because they were open this morning

| what | how it is pinned |
|---|---|
| `cdio_get_track_lsn()` return values used unchecked in the pregap search — a `CDIO_INVALID_LSN` sentinel would have been used in arithmetic and the result reported as a measured pregap LSN | `track_lsns_usable()`, 5 assertions in `tests/subq.c`; revert-proved (dropping the guard fails exactly `subq_test`) |
| a stale `TODO` in `pregap.c` asking whether the drive returns Q data or zeroes — it was answered and tested, and the comment asserted an unaddressed problem | comment replaced with what is actually done, naming the test that pins it |

Neither was reachable from a fixture. The first needs a live libcdio handle
whose track lookup fails; the second was a claim in a comment, which no test can
reach at all. **Both were found by reading the tree rather than by running it**,
which is the only method that finds this class.

---

## Open, ours, and solvable — but deliberately not now

### `EXCLUDED_TESTS` rests on a premise we recorded as lapsed, and nothing reads that premise

**Found 2026-09-17 by checking Platterpus's round-21 lap 4 §H shape against our
own tree rather than assuming it was not here.** Their shape: *a guard widened
under an assumption, with the note recording that the assumption had lapsed
written one screen away by the same hand, and nothing connecting them.* They
asked for silence if it did not appear here. **It appears here.**

`tools/mutate.py:111` excludes one test from the mutation sweep:

```python
EXCLUDED_TESTS = {
    "contract_build": "hashes src/ into the contract's source anchor, so it "
                      "fails on any byte changed in src/ …",
}
```

**The premise is that exactly one test detects an EDIT rather than a DEFECT**,
and a sweep is vacuous if a second one exists — every mutant dies on the edit and
the score reads 100%.

**That premise has already lapsed once, within hours**, and `CLAUDE.md` records
it in prose: `tools/sanitize-run.py` ran the whole images suite in the
instrumented tree, `mutate.py`'s third stage picked `contract_build` up again
through `Sanitizer sweep`, and `src/cyanrip_encode.c` scored **100.0% over 125
mutants and meant nothing**.

**The remedy adopted was a procedure, not a check** — run the inert-edit probe
before reporting a sweep — **and the probe no longer runs.**
`tests/rip_images.py:3507` says so in as many words: *"Filed evidence for the
inert-edit row, which no longer re-runs the probe."* `docs/inert-edit-probe.log`
opens with *"FILED EVIDENCE, not a re-runnable gate."* It is asserted to be
**tracked**, not to be **true**.

So a third test that hashes `src/` would silently restore the vacuous 100%, and
the only thing standing between us and that is a person remembering a rule
written three hundred lines away in a different file.

**The counter-example is in our own tree and makes the point sharper rather than
softer.** `GRANDFATHERED = {5, 6}` in `tools/release-gate.py:79` is the same kind
of set resting on the same kind of premise, and `tests/release_gate.py:430`
pins it: *"grandfathered set changed"*. **We wrote the check once and not the
other time**, so the shape is not that the check is hard — it is that nothing
prompts you to write it when the premise is retired in prose instead of in code.

**Platterpus's general form, which we are adopting as stated:** *when a premise
is retired in prose, what reads that premise?* Nothing does, by construction — a
comment explaining why an assumption no longer holds is not a thing any checker
reads.

**Not fixed in this round.** R3 defaults a finding to the next round, round 21 is
open, and this makes nothing about the pin under review unsafe. The fix is cheap
and obvious — assert the exclusion set, and make the inert-edit probe a gate
again or say out loud that it is not one — but "cheap" is not a reason to widen a
round. `docs/ROUND-22-PLAN.md`.

### `Interrupted sample freshness` has failed TWICE, and the second failure named the arm

**Measured 2026-09-17, one occurrence, in a full suite run.** `Ok: 85 Fail: 1`,
and the message was precise:

```
a rip interrupted right now does not produce:
  ^Stopping, ripping incomplete!$
```

**Not reproducible standalone:** three consecutive runs immediately afterwards
passed. So the check is non-deterministic under load, and a green re-run is not
evidence that anything was fixed.

**What is narrowed.** `cyanrip_main.c:867` prints that line from **inside the
per-frame loop** of a track read:

```c
/* Stop now if requested */
if (quit_now) {
    cyanrip_log(ctx, 0, "\nStopping, ripping incomplete!\n");
    break;
}
```

So the line is produced only when `quit_now` is observed *while a read is in
flight*. `tools/gen-golden-reference.py` polls the child's stdout every 0.05 s
for `Ripping track` and signals the moment it appears — and the fixture is three
short tracks, 600 sectors, so a pass can finish inside that window. A signal
arriving after the frame loop has ended reaches a different check and this line
is never written.

**And the generator asserts the opposite as a guarantee.** `INTERRUPTED_SHAPES`
says of the two `Interrupted at:` arms: *"Only the first is produced by any test
here: sc_interrupt() signals once `Ripping track` has appeared, so the read is
always in flight."* **"Always" is the word that failed.** It was true in every
run anyone had constructed, which is not the same as true — the same shape as
the per-track paranoia invariant that survived four verifications because every
artifact it met had each track read once.

**WHICH ARM IT TOOK IS NOW ESTABLISHED, on the second occurrence — 2026-09-18,
one failure in a full suite run, five standalone re-runs immediately afterwards
all exit 0.** The paragraph this replaces said it could not be established,
because `generate_interrupted()` ran inside a `tempfile.TemporaryDirectory()`
and deleted the evidence. `6c507e3` fixed that, and this is the first failure
since. `build/interrupted-probe-failure/` holds both artifacts and they say:

```
Ripping errors: 1
Rip completed:  no (interrupted by SIGTERM, 0 of 3 tracks)
Interrupted at: track 1, mid-read
Log FUN512: SKQUXzRlvWeF6AasZe_SaqvCaenUQeoHvEn0Y161iIsQ…
```

with `-j` at `cyanrip-diagnostics/6` and `exit_code: 1`. **So the interrupt was
real, complete and attested** — every footer field present, the log signed and
verifiable — and the ONLY thing missing was the one line the check pins.

**AND `mid-read` IS NOT EVIDENCE THAT THE LINE-866 BRANCH RAN, which is the
subtlety and the reason to read the source before concluding.** The two are
written from **different conditions**:

- `Stopping, ripping incomplete!` (`cyanrip_main.c:866`) prints only when
  `quit_now` is observed **inside the per-frame loop**.
- `Interrupted at: track N, mid-read` (`cyanrip_log.c:897`) prints when
  `ctx->track_read_incomplete` is still set — and that is assigned **before**
  the loop and cleared only when the read *finishes*, so it means "the read did
  not complete **by any exit path**".

A first reading of these artifacts said they refuted the narrowing above. They
do not. **The read did not finish AND the line-866 check was not reached**, so
the loop left by some other route while the field was still set — which is a
narrower open question than the one this entry started with, not an answer.

**What is still NOT established:** which route. The candidates are a paranoia
read returning an error under the signal, or an earlier `break`/`goto` out of
the frame loop. Both are readable from the source and neither is confirmed by a
run, so neither is written here as the cause.

**The fix that made this paragraph possible cost nothing and settled the next
occurrence exactly as predicted** — which is the argument for the cheaper of
two candidate fixes being done first.

**Deliberately not fixed in this round.** Round 21 is open and this is not a
regression in the pin under review; R3 defaults it to round 22. The two candidate
fixes are not equivalent and should not be chosen under a round's clock: keeping
the failing run's artifacts costs nothing and settles the next occurrence, while
making the signal reliably land mid-read changes what the check exercises. **The
comment is corrected now regardless**, because a docstring claiming a guarantee
the code does not have is the defect that let this go unnoticed.

### `Lap commit list names its range` has timed out FOUR times, and the call that hangs is now named

**Second occurrence 2026-09-17**, at the tip `dcd6f95`, in a full suite:
`Ok: 85  Fail: 0  Timeout: 1`, exit 1.

```
23/86 cyanrip:Lap commit list names its range   TIMEOUT   30.01s  killed by signal 15 SIGTERM
```

**Identical to the first in every measured respect**: same test, same 30.01 s,
same `SIGTERM` at meson's default limit, same full-suite-only context.

**What the second occurrence rules OUT, measured rather than assumed.**
Standalone immediately afterwards: **0.88 s, 0.89 s, 0.88 s** — against 0.89,
0.89, 0.94 on 2026-09-16. **The test has not got slower**, although the tree has
gained laps, a 34-file rig session and three weeks of commits since. **Growth in
what it walks is not the cause.**

**And the distribution is bimodal, which is the sharpest thing we have.** Every
observation is either ~0.9 s or ≥30 s; nothing in between, across two timeouts
and a dozen normal runs. Ordinary CPU contention in an 86-test parallel suite
produces a spread, not a 34× cliff. **A bimodal time is the shape of waiting on
something, not of competing for something** — which is the direction to look next,
and is not yet evidence for any particular lock.

**Deliberately NOT given a wider `timeout:`.** It has no explicit one and takes
meson's default 30 s, so widening it is the available move and it is the wrong
one: it would convert the only signal we have into silence, and this file already
records that treatment as the defect. **The useful change is instrumentation, not
tolerance** — the test should record its own elapsed time per peer entry, so the
third occurrence says *where* the 30 seconds went instead of only that they went.

**THAT PREDICTION WAS MADE, THE INSTRUMENT SHIPPED AT `122af59`, AND THE THIRD
OCCURRENCE SCORED IT — 2026-09-18, in a full suite, same 30.01 s, same SIGTERM.**
For the first time the test said something on its way out:

```
killed by signal 15 after 3 completed call(s) -- the call in flight is the one
that hung, and is NOT in the list below
timings: 3 call(s), 1.40 s total
     1.18 s  --since 343ebd1 --head 59cb5a9
     0.12 s  --since 8880d8f --head 59cb5a9
     0.10 s  --since 8880d8f --head 59cb5a9
```

**What that establishes, against a complete passing run measured immediately
afterwards — 8 calls, 0.78 s total, three standalone runs at ~1 s each, all
exit 0:**

- **The test does 8 subprocess calls and they cost under a second together.**
  So roughly **28.6 s went into ONE call** whose siblings each take ~0.1 s.
- **It is not the test that waits, it is one subprocess.** The bimodal
  distribution recorded above now has a mechanism-shaped explanation rather than
  only a shape: a single `git` invocation that does not return.
- **A new datum nobody had:** the failing run's *first* call took **1.18 s
  against 0.16 s** in a normal run — **7× slower before anything hung at all**.
  Whatever the run was contending with was already visible in call one.

**FOURTH OCCURRENCE, 2026-09-18, AND IT REPEATED THE THIRD EXACTLY** — same
suite, `Ok: 86  Fail: 0  Timeout: 1`, three standalone re-runs at ~1 s
immediately afterwards. The dump:

```
killed by signal 15 after 3 completed call(s)
timings: 3 call(s), 2.75 s total
     2.53 s  --since 343ebd1 --head 59cb5a9
     0.11 s  --since 8880d8f --head 59cb5a9
     0.10 s  --since 8880d8f --head 59cb5a9
```

**Two occurrences, one shape, and it is sharper than "bimodal":** exactly **3**
completed calls both times; the **first** call abnormally slow both times
(1.18 s then 2.53 s, against 0.13 s normal — 9× and 19×); calls 2 and 3
ordinary at ~0.1 s; and the 4th never returning. **Whatever this contends with
is already visible in call one**, and it is not general slowness, because the
two calls after the slow one are normal.

**THE HANGING CALL IS #4, `16 9 --head 59cb5a9`** — derived, and say so: the
instrument now prints in call order, a clean run is
`#1 --since 343ebd1`, `#2 --since 8880d8f`, `#3 --since 8880d8f`,
`#4 16 9 --head 59cb5a9`, and **both timeout dumps match #1–#3 of that sequence
exactly.** So #4 is the next one. This is inference from two artifacts rather
than a direct observation; **the next occurrence will simply say it**, because
the handler now prints `THE CALL THAT HUNG IS #N: <args>`.

**And #4 is the first call of a different kind.** Calls 1–3 pass `--since
<sha>`; #4 is the first to use the **positional round/lap form**, which has to
resolve a lap's commit range out of the record rather than being handed one.
That is a direction to look and **not yet a cause** — no run has demonstrated
it, and the distinction between narrowing and establishing is the whole point
of this entry.

**The instrument's limit is fixed, and it was the identified next step.** It
sorted by duration, which reads well and destroys the one fact a hang needs:
what came next. It now prints in call order with an index, and holds the call
in flight. **Revert-proved**: SIGTERM at 0.30 s into a run printed
`killed by signal 15 after 2 completed call(s)` / `THE CALL THAT HUNG IS #3:
--since 8880d8f --head 59cb5a9`, which is exactly what occurrences 3 and 4
could not produce.

**What is still NOT established**, and it is now one question rather than two:
**why** #4 does not return.

**Superseded — what this entry said before the fourth occurrence.** Which
call hung. The dump is **sorted by duration, not by order**, so the three
survivors cannot be placed in sequence and the fourth cannot be named from a
passing run's list either. The instrument answered *how many completed* and not
*which one is next* — **a cheap fix, and the next one to make**: record the call
index alongside the duration. Recorded here rather than done now because round
21 is closing and this is not a regression in the pin under review; R3 defaults
it to round 22.

**The pattern is worth naming because it has now happened twice in one day.**
Both this and the interrupted-probe race were entries that said *"the cause is
not established, and here is the cheap instrument that would settle the next
occurrence"*. Both instruments shipped. **Both fired on their first real
occurrence and both moved the entry forward** — one named the arm, this one named
the shape. *The cheap instrument first* is not a compromise; it is the thing that
turns an unreproducible failure into evidence.

**First occurrence, kept verbatim below, because two data points are the finding
and consolidating them would destroy it.**

**Measured 2026-09-16, one occurrence, immediately after round 20 closed.** The
suite reported `Ok: 84  Fail: 0  Timeout: 1`, exit 1 — and **84 + 0 is not 85**,
which is the only thing that made it visible. Read as the two lines the previous
runs trained the eye to look at, *"84 Ok, 0 Fail"* reads as a pass.

```
22/85 cyanrip:Lap commit list names its range   TIMEOUT   30.01s  killed by signal 15 SIGTERM
```

**What is measured:**

| | |
|---|---|
| standalone, three runs | **0.89 s, 0.89 s, 0.94 s** |
| in every earlier full suite that day | 0.98 s, 1.04 s, 1.12 s, 1.95 s |
| the one timeout | **30.01 s**, meson's default limit |
| the immediate re-run of the whole suite | **OK in 1.07 s**, and 85/85 green |

**What is ruled out**, checked rather than assumed: no `gc.pid`, no stale
`.git/*.lock`, and 1,926 loose objects — below git's auto-gc threshold. The
tempting hypothesis, a background `git gc` holding a lock, is **not supported**.

**What is narrowed but NOT established.** `tests/lap_commits.py` spawns a fresh
Python interpreter per peer entry in a loop and shells out to git, and it has
**no explicit `timeout:` in `tests/meson.build`**, so it gets meson's default 30
seconds. Meson runs tests in parallel, and its neighbours include `Sanitizer
sweep` — a full `meson setup` plus `ninja` build of a second tree — the
838-invocation black-box sweep, and the argv probe. Contention is a plausible
mechanism for a slowdown. **It is not a plausible mechanism for 30×, and saying
so is the point of this entry.**

**Deliberately NOT fixed by widening the timeout.** A number chosen without the
mechanism is a guess, and changing a test so it stops reporting is the move this
repository has a rule against. The flake is recorded instead, with what would
settle it: **run the suite with `--num-processes 1` and time this test, and run
it under a deliberate parallel load.** If it recurs, that is evidence to act on
and an explicit `timeout:` becomes a *declaration* rather than a suppression —
the same standing `Black-box sweep` already has.

**Why it matters beyond one flake.** A gate that can fail for a reason unrelated
to the code is the exact disease `PROTOCOL.md` R2 names when it forbids
enforcing `HANDSHAKE-CLOSE-BY`: *enforcement lets a clock skew block a release*.
A 30-second default doing the same thing to a release is the same shape, one
layer down.

### The cache probe's calibration is wrong

`-x` reports `at least 2048 sectors, upper bound unknown` on a drive
`cd-paranoia -A` measures at 137–140 sectors. The mechanism is known: `miss_cost`
is calibrated with a full-stroke seek (342.9 ms measured) while the test read is
a *short backseek* (2.22 ms/sector on the same drive). The threshold is
`miss_cost / 4` = 86 ms, so every short backseek scores as a hit and the search
runs to its ceiling.

**Diagnosis re-derived from the source 2026-08-13** rather than trusted from the
earlier claim, because both this file and lap 7 assert it: calibration is
`probe_read(end_lsn - 10)` then `time_one_read(start_lsn + 1000)` — a full
stroke — while the loop's test read is a short backseek, and the hit test is
`t * CACHE_HIT_RATIO < miss_cost` with the ratio at 4. It holds.

**Half-fixed 2026-08-13.** The line reported the calibration read and nothing
about the reads it *classified* — one side of a two-sided comparison, so a
reader saw a verdict with half its evidence missing. It now carries both, so
`uncached read 342.9 ms, cached read 2.2 ms` states its own implausibility in
the artifact instead of requiring someone to reason about the source.

**The calibration itself is still wrong and is deliberately not fixed.** It
needs a backseek-based `miss_cost`, there is no drive here to verify one
against, and the last prediction made about this exact code was falsified on
hardware. Shipping a second unverifiable probe would repeat the mistake.

**SETTLED IN DIRECTION, FALSIFIED IN MAGNITUDE — and the table below was
INCOMPLETE for two days.** It carried three rows, then four. **Every filed rig
session that produced a `Cache probe:` line is here now: eight of them**,
derived 2026-09-15 by scanning `docs/rig-*/session/transcript.txt` rather than
by adding the ones anyone remembered. The prediction this section made was *"an
uncached read in the hundreds of milliseconds beside a cached read of a few."*

| session | uncached (`miss_cost`) | cached | threshold (`miss_cost / 4`) | margin |
|---|---|---|---|---|
| 2026-09-03 `978f9b0` | 244.7 ms | 43.1 ms | 61.2 ms | 70% |
| 2026-09-05 `978f9b0` | 237.6 ms | 56.4 ms | 59.4 ms | **95%** |
| 2026-09-07 `978f9b0` | 245.3 ms | 42.4 ms | 61.3 ms | 69% |
| 2026-09-10 `ddc1e8c` | 363.2 ms | 82.0 ms | 90.8 ms | **90%** |
| 2026-09-11 `ddc1e8c` | 362.5 ms | 61.9 ms | 90.6 ms | 68% |
| 2026-09-12 `fe4d2c4` | 250.6 ms | 42.3 ms | 62.6 ms | 68% |
| 2026-09-15 `fe4d2c4` | 362.6 ms | 61.7 ms | 90.7 ms | 68% |
| 2026-09-15b `fe4d2c4` | 362.7 ms | 81.6 ms | 90.7 ms | **90%** |
| 2026-09-17 `fe4d2c4` | 362.8 ms | 62.2 ms | 90.7 ms | 69% |

**Each row names its directory**, `docs/rig-<row>-<build>/` — so `2026-09-15` is
the `00:58` session and `2026-09-15b` the `12:01` one, which is how they are
filed. `sc_cache_table_matches_the_transcripts()` resolves every row that way
and fails on a row that names no session **and** on a session with no row; the
label read `2026-09-15a` until that test was written and pointed at nothing.

**Hundreds of ms uncached: confirmed, eight times. "A cached read of a few ms":
FALSIFIED** — 42 to 82, not 2.2. All eight end identically, at
`at least 2048 sectors … search ceiling reached`.

**THE FOUR-RUN CONTROL, which is what the missing rows were hiding.** Sessions
09-10, 09-11, 09-15 and 09-15b calibrated `miss_cost` at **363.2, 362.5, 362.6
and 362.7 ms** — a spread of **0.7 ms**, as close to one calibration as a
mechanical drive gets. Their *classified* reads split into two tight clusters,
**61.7–61.9 ms** and **81.6–82.0 ms**, giving margins of **68%** and **90%**.

**So the margin's variance does not come from the calibration.** Hold
`miss_cost` fixed to within a fifth of a percent and the verdict still lands in
one of two places 22 points apart. This was previously argued from the source —
`last_hit_us` is overwritten on every hit, so the figure printed is the re-read
after the longest forward run the search performed — and it is now measured over
four runs rather than inferred from two.

**And the closest call was in a row that had been left out.** 2026-09-05 sits at
**95% of its threshold**. A `CACHE_HIT_RATIO` of 3.8 instead of 4 would have
stopped that search, at a run length with no physical meaning — so the constant
does not merely swing the answer by a factor of sixteen on its third significant
figure, it comes within five percent of swinging it on noise. **The table was
understating its own case.**

Evidence: `docs/rig-*/session/transcript.txt`, all eight. Re-derive with
`grep -h "Cache probe:" docs/rig-*/session/transcript.txt` — and note that
`cached read` must be matched with a guard, because **`uncached` contains
`cached`**: the first derivation of this table read the same number into both
columns and produced a margin of exactly 400% on every row, which is what a
pattern that nearly matches looks like when it is wrong in a plausible way.

The gap is structural rather than noise, and it changes the fix. `last_hit_us`
is overwritten on every hit, so the figure printed is the re-read after the
**2048-sector** forward run — the longest backseek the search ever performs. The
2.22 ms figure came from a 1-sector run. **They were never the same
measurement**, and the earlier prediction compared them as though they were.

**So the fix is not "arithmetic", as this section previously claimed.** One
corrected `miss_cost` constant cannot be right at both ends: the test read's
cost grows with the run length — a backseek of 1 sector at the start, 2048 at
the ceiling — while the calibration is a single fixed full-stroke figure. The
comparison needs a baseline that **tracks the run length**, or the search must
seek away by a comparable distance before each timed re-read so that one
baseline is valid throughout. Which of those is right is not settled.

**The margin column is why retuning `CACHE_HIT_RATIO` is not the fix either.**
The `ddc1e8c` row sits at **90%** of its threshold: a ratio of 3.5 instead of 4
would have stopped that search, at a run length with no physical meaning. A
constant that swings the answer by a factor of sixteen on its third significant
figure is not calibrated, it is coincidental.

**Still deliberately not fixed, and now for a better-evidenced reason:** the
shape of the correct fix changed the moment the magnitude arrived, which is
precisely what shipping the "arithmetic" version on 2026-08-13 would have got
wrong. The evidence clause was added first so this could be seen rather than
argued, and it worked.

**Believe `cd-paranoia -A` — 137 sectors, then 140 — not our figure.** Note that
the reference moves between its own runs, which caps how precisely any of this
can ever be stated.

**Raising `PROBE_MAX_SECTORS` is not the fix and never was.** The search is
stopped by the comparison, not by the limit; raising the limit moves the number
the probe reports and changes nothing about whether it is right. Recorded
because the question keeps arising from the `search ceiling reached` wording,
which is accurate and reads like a complaint about the ceiling.

### A settled fact is re-checked by calling the internet, and it times the suite out

**Measured 2026-09-13**, by profiling `tools/check-settled.py` rather than
guessing at it: 136.8 s over 67 commands, of which **`tools/accurip-live-probe.py`
is 80.2 s — 59% of the whole check**. `probe-argv-surface.py --gate` is 26.7 s
and `tests/release_gate.py` 17.3 s; the remaining **64 commands total ~13 s**.

`tests/meson.build` gives `Settled facts` a 120 s timeout, chosen as roughly 4x
headroom over a measured 27-30 s. It now **exceeds that and the meson test
TIMEOUTs**, so the suite reports 80 OK and 1 timeout rather than 81 OK. The
check itself still returns **0 stale**; it is the clock that fails, not the
facts.

**Measured again on 2026-09-15 morning, at 101.20 s against the same 120 s
timeout over 72 runnable commands — and FIXED that afternoon**, so this
paragraph is the record of the last measurement taken while the network was
still in the gate, not a current state. It said *"whether it passes on any given
day is still decided by how fast `accuraterip.com` answers rather than by
anything in this tree."* That stopped being true a few hours later; see the
half-fix below, which took it to **54.6 s** over **77** commands.

**Left standing rather than deleted, because it is also an example.** A document
edited twice in one session contradicted itself in the same file — the exact
thing `sc_docs_do_not_contradict_themselves()` exists to catch, and it was
caught by grepping this file for its own numbers rather than by the test, which
checks CLAUDE.md and the handshake README and not this one.

**The cause is not size, and the first diagnosis of it here was wrong.** It was
attributed to documentation growth — ~380 lines added to `STATUS.md`,
`KNOWN-ISSUES.md` and `Changelog.md` in one session — on the reasoning that the
check greps `docs/`. Profiling says those greps are in the ~13 s tail. **80 of
the 137 seconds are one HTTP conversation with `accuraterip.com`**, and its
duration is set by the network that day.

**The defect is that the row exists in this form at all.** `SETTLED.md` row 84
states a fact about **our parser** — that the AccurateRip response parser runs
in this sandbox with no drive — and re-checks it by contacting a third-party
service. This repository already has the rule, and paid for it:

> *A check that reaches the network is not evidence about this program.* The
> first diagnostics refusal test drove cyanrip into a refusal reached **via a
> MusicBrainz lookup**, so what it asserted depended on whether the lookup
> failed by not-found or by timeout. It failed once and would not reproduce.

Two consequences, and the second is worse than the slowness:

1. **The runtime is unpredictable**, so any timeout is either too tight (today)
   or too loose to catch a real regression.
2. **A settled fact can go red because someone else's server is down.**
   `check-settled` cannot distinguish *"the parser broke"* from *"accuraterip.com
   did not answer"* — which is this project's own `none` versus
   `unknown (reason)` rule, failing in the tool that indexes the rule.

**HALF-FIXED 2026-09-15, and the half that is left is DEFERRED FOR A NAMED
REASON.**

**Done: the network is out of the gate.** `SETTLED.md`'s AccurateRip row no
longer re-runs the probe. The run is filed verbatim at `docs/accurip-probe.log`
(2026-09-15, `found`, confidence 200) and the row's check asserts the **claim
against the artifact** — edit the row's numbers without re-running the probe and
it fails. Measured: `check-settled.py` went from ~100 s to **54.6 s**, so
`Settled facts` now sits at 45% of its 120 s timeout instead of 84%, and no
verdict in the suite depends on somebody else's server.

**A first attempt at that check was near-vacuous and the revert-proof said so.**
`--toc-only` re-derived the reference TOC, on the theory that the query's one
local input could rot. Pointed at a *different* session's log it returned the
same `14 268707` — every session is the same disc. A check satisfied by the
wrong file is not a check; the flag stays as a tool affordance and the row's
check moved to the claim-versus-artifact comparison, which fails when the
artifact is edited.

**Still to do: assert the parser against a recorded response.** That is the real
fix — offline, deterministic, and it would cover the parse rather than a
recorded verdict about it. It needs the response parse split out of
`crip_fill_accurip()`, which does the curl fetch inline, exactly as
`tests/subq.c` needed the Q sub-channel decode split out.

**And it is NOT being done while round 20 is open.** Splitting it touches
`src/`, and round 20's own `HANDSHAKE-PIN-POLICY` — and Platterpus's round-19
§F1, which calls it *"a stronger statement than the pin has not moved"* — rest
on the span from `fe4d2c4` containing **exactly one `src/` commit changing zero
non-comment lines**. A refactor would end that, during the round that relies on
it. R4 says fixes queue; this one queues. **Raising the timeout was never the
fix** — it keeps a network-dependent verdict in a gate and moves where it
misfires.

### `docs/seam-commands.md` carries THREE known-wrong statements

**Consolidated here 2026-09-15.** They were recorded in two different files, one
of them a 1,100-line standing status, which is how a set of three reads as three
unrelated one-offs instead of a document to fix. Consolidation applies to
documentation and never to evidence; this is documentation.

| # | what it publishes | what is true | found |
|---|---|---|---|
| 1 | §7: *"Every value either took effect or was refused with a message"* | **48 of the 68 accepted rows** were graded from exit status alone — re-measured 2026-09-16, and the *"49 of 111"* this row carried was a count against an older binary | ours |
| 2 | line 504: `-p '99=drop'` accepted, exit 0 | the binary **refuses** it | theirs, lap 16 §B3 |
| 3 | line 97: `-D` is `directory` / `str, path` / `writable` / *"output directory"* | it is `folder_scheme`, *"Directory naming scheme"* (`cyanrip_main.c:1603` at the pin) — a **relative** scheme, with `-F` its per-track sibling | theirs, lap 16 §B3 |

**RE-MEASURED 2026-09-16, and the split of who fixes what is not what this entry
said.** Platterpus pointed out that §7 carries its own *"This section is
GENERATED by `tools/probe-argv-surface.py --markdown` … Never hand-edit it"*.
That is **our** tool, so rows 1 and 2 are ours to regenerate; only row 3 is
hand-written prose in a jointly-owned section.

**Row 2 is fixed by regenerating.** The live binary refuses `-p '99=drop'` with
`Invalid track number 99 for pregap, list has 2 tracks!`, exit 1.

**Row 1 is NOT, and it is a defect in the generator rather than in the committed
copy.** The sentence is emitted by the tool. Measured on the current binary:
**116 rows, 48 refused, 68 accepted — and 48 of those 68 carry `(no header field
exposes this)`.** `probe-argv-surface.py:99` returns `accepted` on exit status
alone when no header field exists to check, so three quarters of the accepted
rows were never observed to take effect while the summary says they were. The
fix is a third outcome — `unobservable` — not a reword, and `--gate` must keep
firing only on a genuine silent drop.

**AND THE REASON ALL THREE DRIFTED IS A CHECK THAT COULD NOT FIRE.**
`python3 tools/probe-argv-surface.py --binary build/src/cyanrip --check
docs/seam-commands.md` refuses outright: *"carries no generated-block
delimiters"*. §7 has declared itself generated since it was written and
**nothing has ever verified that it is.** Planned in
`docs/ROUND-22-PLAN.md` §3.

**Do not cite any of the three.** Row 3 is the one that has already cost
something: the real semantics are exactly why an empty leading component made a
multi-component scheme resolve **absolute**, and a reader who believed line 97
would not have looked.

**NONE of them is fixed, and not for want of knowing the answer.** The file is
shared and neither project owns it — a one-sided edit is how two copies of one
spec come to disagree, which has already happened once to `PROTOCOL.md`. They go
in together at the next joint version bump.

**Deliberately NOT added to round 20.** R1 fixes a round's close conditions at
lap 1 and round 20 has two; a third arriving mid-round is the exact failure R1
exists to stop, and these break nothing in `fe4d2c4`. They are a round-21
bundle — one version bump, three rows, shipped by both sides on one day.

---

## Open, ours, and NOT solvable here — no drive in this environment

Every one of these needs hardware. Listed so a green suite is never mistaken for
coverage.

| gap | status |
|---|---|
| `-x` correctness on a real drive | measured twice, wrong both times — see above |
| C2 error reporting | the rig's drive reports C2 unsupported; never exercised anywhere |
| `-f` offset autodetection | **partially retired 2026-08-12** — exited 0 and rediscovered `+667` on the rig. The *value* is now confirmed; behaviour on a drive with a different offset is not |
| damaged media | never tested; no damaged disc available |
| CD-TEXT from a physical disc | `mmc_read_cdtext` is a different code path from the image parser, and no disc with CD-TEXT has been read |
| the diagnosed-abort exit code | every rig rip so far had `Ripping errors: 0` |
| a non-zero `Read stalls:` count | **a silent watchdog is not a working watchdog.** Zero heartbeats on healthy media is the expected result and is evidence of nothing |

The remaining `TODO`s in `src/pregap.c` are upstream's, carried with the feature
from PR #115, and are open questions rather than known defects: whether libcdio
can report a first track other than 1, and whether the macOS path can be
restored (it needs `cdio_get_device_fd()`, which is not in libcdio 2.1.0 —
verified against the installed headers *and* the `.so` export table).

---

## Open, joint — belongs to the seam, not to one side

### The close condition cannot be satisfied by the side that speaks first — round-23 item

`PROTOCOL.md` §5 requires `HANDSHAKE-PEER-VERDICT: GO`, *"transcribed from the
file they actually sent"*, in each side's own newest lap. **The side that speaks
last can do that; the side that speaks first cannot**, because its file was
written before the other side's answer existed. So a round is mutually closeable
only if the first speaker writes one more lap — which makes the other side the
first speaker.

Not hypothetical and not new. `SETTLED.md` row 102 records it from **round 17**,
where we spoke last and Platterpus's `--status` held the round `OPEN`; they filed
their acceptance as a `verified/` record. **Round 22 is the first time they spoke
last**, and we cannot use that escape: `tools/release-gate.py --release-gate`
refuses while any round is open, so an unclosed round 22 blocks
`+platterpus.14` permanently. Our lap 5 is that extra lap, and it closes the
round rather than reopening anything.

Measured on our side rather than assumed: with their lap 4 filed,
`stale_peer_verdict` **is** satisfied and `closed()` still returns False one line
earlier, on `self.peer_verdict not in CLOSING` — our own lap 3's cell, correctly
declaring `OPEN`.

**This is a condition gated on a consequence of itself**, the family Platterpus's
round-22 lap 4 C1 named, and the third instance in that round alone: §6a's
test-pin deadlock, their verdict-note circularity, and this. Their formulation is
the one to keep — *state what must be TRUE, never what must have HAPPENED* — and
`HANDSHAKE-PEER-VERDICT` is a has-happened condition in a must-be-true field.

**Proposed for v5 in lap 5 §H1 and deliberately not implemented.** The close rule
is shared, and relaxing a match rule on one side is how two gates come to
disagree about whether a round is closed. The proposal: read the peer verdict
from the newest peer lap the writer holds and has enumerated in
`HANDSHAKE-INBOUND-HELD`, keeping `HANDSHAKE-PEER-VERDICT` as the declaration and
cross-checking it against that — which is what `stale_peer_verdict` already does
in one direction. Needs a `HANDSHAKE-PROTOCOL` bump shipped to both sides before
either gate implements it.

**ASSENTED 2026-09-21, WITH ONE CONDITION, AND THE CONDITION IS A HOLE IN THE
PROPOSAL.** Recorded in their standing status — filed byte-exact at
`docs/handshake/inbound/status-2026-09-21-v0.6.52.md`, sha256
`9c0a37507f2d1839…`, 38,037 bytes, read at `platterpus@a0aed36`, under
*"ASSENT — your §H1 `PROTOCOL.md` v5 close-rule proposal, with one condition"*.
It is in a standing status rather than a lap because **round 23 is ours to open
under §1a**, so their next lap cannot exist yet. They verified our diagnosis in
our source before assenting — `release-gate.py:727-732` and `:552-556`, both
reproducing at `cyanrip@b293f32` — and changed nothing in their gate.

**The condition: the released-for-reading check must be NORMATIVE in the spec,
not one implementation's habit.** Their reasoning, and it is correct: the
proposal moves the verdict from *their transcription of our lap* to *our lap
itself*, and both repositories are public — so under v5 a side can read a lap
**before its operator has released it**, and *"acting on a held lap would make
your draft our decision."* Today `HANDSHAKE-READY-TO-READ` is what stops that,
and today it is a property of each gate rather than of the spec; under v5 it
becomes **the only thing between "we can see it" and "we may act on it."**

So v5 must state that a lap read for its verdict has to declare
`HANDSHAKE-READY-TO-READ: yes`, and that an unreleased or undeclared lap is
**not** a readable verdict — fail-closed, naming which lap is being held. They
are not attached to the drafting, only to it being in the shared spec before
either gate changes.

**Accepted, and it is a real gap in what we proposed, not a formality.** Our own
gate already refuses a held lap (`closed()` returns False on `self.held`, which
is why the round-22 gate reported lap 5's verdict as a draft) — and we wrote the
proposal without noticing that it **promotes that check from a safety net to the
load-bearing element**. The publishing-is-not-sending distinction did work four
times across rounds 21 and 22, including on our own lap 5, and we still missed
it here. Their addition goes into round 23's lap 1 as part of the v5 clause.

### A HELD lap's draft verdict reaches the compiled `Handshake:` line — round-23 item

`tools/gen-handshake-state.py` takes `latest.verdict` verbatim, so with lap 5
published and `HANDSHAKE-READY-TO-READ: no` the banner reads `round 22 lap 5
OPEN, verdict GO` — a verdict the release gate itself declines to act on,
reporting *"its verdict is a draft"*. A held lap may still be revised; the banner
publishes its verdict as though it were settled.

**Pre-existing, not introduced by lap 5.** Checked by generating the state in a
throwaway worktree at `623251c`, where lap 3 was held: it produced `round 22 lap
3 OPEN, verdict GO` the same way. Every held lap since the field existed has done
this.

**Bounded, and that is why it is not urgent.** `HANDSHAKE_RELEASED` is separately
`0` for any open round, so every log such a build writes also says **`NOT a
released build`**, and a *released* build cannot carry a draft verdict at all —
a release needs a closed round, and the gate refuses to close on a held lap. So
the exposure is unreleased builds, which already disclaim themselves on the line
below.

**The fix is contract surface, which is why it waits.** `Handshake:` is a line a
consumer parses, so adding a qualifier to its value vocabulary is a handshake
matter and not a drive-by reword. Round 23, with the v5 item above.

### A superseded track has no recorded read time anywhere

Our album log gives each track a `creation_time` describing the **first pass**.
Platterpus's addendum supersedes that track and carries **no timestamp at all**.
So for any re-read track, the only time on record belongs to audio that is no
longer on disk.

The datum is not missing, only uncarried — their re-read is a cyanrip invocation
and writes its own `creation_time`. Asked as round 8 `J14`. **Unrecoverable
after the fact**, which is why it is asked at all: a read time is not derivable
a month later from anything on disk.

### A track's per-track lines are computed from the REQUEST, not the outcome

**HALF FIXED IN ROUND 22, at `89a57d6`, and the half that remains is the harder
one.** Kept here rather than moved to the fixed section, because a heading that
said *fixed* over an entry describing a live defect is the label rule this
repository applies to log lines, turned on its own notes.

> **THE FIX IS NOT RELEASABLE ON ITS OWN, and the reason came back from
> Platterpus in round 22 after our lap 1 had already gone.** The renamed line is
> their **block delimiter**, not a field they read:
> `platterpus@417d61b:src/platterpus/parsers/cyanrip_log.py:212-215`,
> `_TRACK_START`, commented *"A track block opens with its outcome line"*,
> matching **both** arms we renamed. Line 2452 is the only `_TrackAcc(`
> construction site and sits inside that match, so no match means **no track is
> parsed**; `rip_completed_tracks` is set separately at 1458 from the disc-level
> footer. **The same parse therefore reports 14 of 14 tracks and
> `No errors occurred` over a record carrying zero tracks.** Read at the SHA
> they cited rather than taken on their word.
>
> **They did not veto it.** The ask is their round-20 ordering: their parser
> accepts both wordings additively, ships in a release, **then** `+platterpus.14`
> ships. `Encoder errors:` they accepted as a clean P2 — all three arms trip
> their completeness sweep, which is the sweep working, and tracks still parse.
>
> **So this entry is now two facts, not one.** The log is right and the release
> is blocked on a consumer-side prerequisite no release of this fork has had
> before. `+platterpus.14` must not be cut until that release exists; round 22
> cannot close without `HANDSHAKE-PEER-VERSION`, so naming it there is what
> enforces the order with machinery that already exists.
>
> **AND THE ZERO-TRACKS OUTCOME IS SILENT AT RUNTIME — do not write "wrong but
> loud" in lap 3.** Read at `417d61b`, their completeness enumeration is two
> mechanisms and neither reaches a user: their *test* walks their **committed**
> logs and fails on a top-level line matching neither the tables nor
> `_IGNORED_DISC_LINES` (`cyanrip_log.py:1082-1085`), and the parser itself logs
> an unclaimed top-level line **at debug** (`:1086-1087`). So the sweep that
> caught `Encoder errors:` fires on fixtures they hold, and a user running a tip
> build gets zero tracks with a debug line and nothing else. That makes their
> ordering ask stronger rather than weaker. **Lap 3 §H material at most, flagged
> read-from-source, and explicitly not a condition** — they said no new
> conditions and we are not adding one.

**What round 21 fixed was the COUNT, and this is what it made visible.** With
the completion footer moved below the encoder-status loop, `Ripping errors:`
reported the encoder failures — but the per-track block above it did not:

```
Track 2 ripped and encoded successfully!      <- the encode failed
  File(s):
    .../2.flac                                <- 32768 bytes; intact is 253742
Error writing packet: File too large!
Error writing trailer: File too large!
Ripping errors: 2                             <- fixed in round 21
Rip completed:  yes (2 of 3 tracks)
```

Two separate causes, and they need different answers:

- **`Track N ripped and encoded successfully!`** — **FIXED, round 22.** It was
  printed when the READ finished; the encoders run asynchronously and their
  status did not exist yet, so the line was not merely mis-worded — at the
  moment it printed, the fact it asserted was genuinely unknown. **No rewording
  of a line printed at time T can report a fact that comes into being at T+1**,
  so the claim is split rather than softened: the per-track line now reads
  `Track N read successfully!` and the encode outcome lands in a new
  `Encoder errors:` line in the footer, below `Ripping errors:`, where the
  collection loop has joined every encoder thread. Three arms — `none; N tracks
  encoded`, `M tracks failed (…); N tracks encoded`, `not applicable; no track
  was encoded` — because `none` over an unstated population is the absence-of-
  evidence defect wearing a number.
- **`File(s):`** — **STILL OPEN.** It is built from `ctx->settings.outputs` and
  the naming scheme (`cyanrip_log.c:642`) and consults nothing about what was
  written, so it names a path whatever happened to it. Platterpus's phrase for
  their own version of this — *a completeness field computed from the REQUEST,
  read as the OUTCOME* — fits it exactly. **It prints from
  `cyanrip_log_track_end()`, which runs at the same pre-join moment**, so
  marking a failed entry there is the identical fixpoint one level down. It
  became *possible* only once the footer named the tracks, which is why
  `ROUND-22-PLAN.md` §1 rejected it as a standalone option and listed it as a
  second pass. **Nobody has got to it**; that is not the same as declining it.

**Why it waited for round 22, and what changed.** Round 21 shipped two agreed
changes; a third, unannounced, would have been the finish line moving inside the
round — R1. Platterpus's round-21 lap 2 then listed it under *"explicitly not
asking"*, with the reason *"a real design question, not a reword, and it should
not be decided under a round's clock"*. **That is an argument for deciding it in
a round that OPENS on it, which is what round 22 lap 1 does** — the design was
written out in full in `ROUND-22-PLAN.md` §1 before the round opened, options
and rejections included, so nothing about it is being settled under time
pressure.

Pinned by assertion now rather than by a docstring:
`sc_encode_failure_reaches_the_log()` requires the old string to be **absent**,
not merely joined by a new one, and compares the tracks `Encoder errors:` names
against the truncated files on disk rather than against the log's other half.
Revert-proved four times, one fix at a time.

### `Rip completed:` and `Ripping errors:` can now disagree on their face

`Rip completed:  yes (2 of 3 tracks)` beside `Ripping errors: 2`. Both are
true — the rip loop ran to completion and the encoders failed, which are two
facts — and before round 21 they agreed by both being wrong.

**ASKED, AND THEY RULED: LEAVE IT ALONE.** Round 21 lap 1 put it to Platterpus —
whether the footer should distinguish *the loop finished* from *the run produced
what it claimed*. Their round-21 lap 2 §0.2, released 2026-09-16 and filed at
`docs/handshake/inbound/round-21-lap-02.md`, is a **refusal to change the field**,
and our lap 1 had already said a refusal closes that condition as cleanly as an
assent. `Ripping errors: 2` beside `Rip completed:  yes (2 of 3 tracks)` is
**correct output and stays**. Three reasons, each checked here rather than only
read:

1. **Their parser's tri-state depends on `yes` meaning the loop reached its own
   end.** `None` is an absent footer — what a killed rip looks like — and must
   never read as `False`. A stricter `yes` would collapse *ran to the end and
   failed* into *stopped early*, and that distinction is the **attested
   truncation** finding we root-caused in round 14 lap 7 §B2: the completion
   footer twenty-four `goto end` sites can skip, signed anyway by
   `cyanrip_log_end()`. Tightening the field would spend a diagnosis that cost a
   round to find.
2. **The `(N of M)` denominator is the disc, not the selection** — confirmed in
   our own source at `cyanrip_log.c:917`, which prints `tracks_ripped` against
   the disc's track count, so a narrowed `Tracks to rip:` produces the same
   shape. `done < total` is therefore the ordinary form of a partial rip and can
   never be a failure signal. They measured it on seven rips in their 2026-09-03
   bundle, and an earlier version of their own handler asserted `done == total`
   and would have failed all five partial-rip sites it was added to.
3. **The floor that works is `done == len(tracks)`** — the record agreeing with
   itself, disc- and selection-independent, already in their tree, and needing
   nothing from us.

They also read `rig_check.py` before answering, which we asked for: it consumes
`rip_completed` only as context for `Interrupted at:`, tri-state, `INFO`-only,
and the change does not perturb it.

**So this entry stays open as a description and is closed as a question.** It is
not a defect and there is nothing to fix; it is recorded because the two states
*"nobody asked"* and *"asked, and they said leave it"* are different claims, and
this is now firmly the second.

### A derived contract covers a surface's SHAPE and says nothing about its MEANING

Round 21's second breaking change — `Ripping errors:` now counting encoder
failures — **is invisible to a provider-contract diff by nature.** It changes no
format string, no message text, no exit code and no option; it changes what a
counted thing counts.

Platterpus measured it across the two contracts in their round-21 lap 2 §E:
**1 of 303** two-column format-string rows changed (the `Retry limit:` rename
only), **0 of 120** P5 message texts, **0 of 7** P5a, and one citation moved
(`diagnostics.c:572` → `:618`). A green argv-surface suite and a byte-clean
inventory regeneration say **nothing** about the semantic change.

`tools/gen-provider-contract.py` derives from format strings, the option table
and control flow, so there is no wording for it to notice. **The hazard is a
future round reading *"the contract diff was one line"* as *"nothing
happened"*** — which here would be exactly backwards. `CLAUDE.md` already states
the test as *"could the other side notice?"* rather than *"did I edit a
`cyanrip_log()` line"*; this is that rule with a measured example attached.

No mechanism is proposed yet, deliberately. R1 fixed round 21's conditions at
lap 1, and a semantic-change marker designed in a hurry would be a field nobody
can derive. Round 22.

### The reference disc cannot discriminate a correct AccurateRip skip

`--first`/`--last` apply AccurateRip's 5-sector lead/tail skip. On this disc
those regions are digital silence, so the skip is a no-op and any golden log
derived from the disc is silent on that logic — **in both implementations.**

Ours is covered by three synthetic vectors in `audio-checksums.py self-test`,
non-zero everywhere including the edges. Whether Platterpus's is covered is round
8 `J13`.

---

## Open, theirs — tracked here only because it blocks us

Full detail in `docs/handshake/round-08-lap-07.md` §0b and §H. Summarised so
this file answers "why is the round not closing?" without a second lookup.

| what | round 8 ref |
|---|---|
| a duplicate `drive changed` restarts disc info; the teardown gives the worker 0 ms and SIGKILLs an in-flight ripper | `J11` — **blocking**, this is why no rip exists |
| a refused command leaves the previous result live, so the next assertion grades the wrong invocation | §H |
| `wait-for-rip` returns `ok` after `rip` failed | §H |
| the script language cannot express a literal `"`, so an assertion on a quoted message is unmatchable | §H |
| the `-t` guard blocks a defect fixed in round 7 lap 32 | §H |
