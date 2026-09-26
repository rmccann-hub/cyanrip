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

## Fixed 2026-09-24, from round 26's real test — two claims older than `.15`

Both were in logs we had filed for weeks. Neither was listed here, because
nobody had read them as claims. `docs/rig-2026-09-24-df91ae7/README.md` has
the evidence.

- **An interrupted track was counted in `Tracks ripped partially accurately:`.**
  A read stopped past sector 450 leaves a complete one-sector `Accurip 450`
  checksum, which matches, so every interrupted rip printed `1/14` above `0 of
  14 tracks`. It is in eight filed `cancel-me.log` files, and Platterpus's
  report flagged it before we did. The tally now counts only tracks with
  `audio_ripped` set. Pinned by `test_disc_tally_skips_an_interrupted_track` in
  `tests/logrender.c`.
- **`-H` tagged every file `media: HDCD`**, from the setting, beside `HDCD
  detected: no`. The tag is now `CD`. Pinned by the `media_tag` scenario, which
  reads the tag out of the FLAC file itself. Upstream's code.

## Fixed 2026-09-23 — a retry limit that could hang on one bad sector

### `-r` values that are not a multiple of 5 never returned on an unreadable sector

**Found by fault injection, not on a drive.** `tests/badsector.c` is an
`LD_PRELOAD` shim that fails every read of a disc image overlapping one sector,
the way a drive fails the whole command. At the **default** paranoia level with
sector 400 of `basic.cue` bad:

| `-r` | before | after |
|---|---|---|
| 3 | **did not return in 90 s** | 184 failed reads, returns in under a second |
| 0 | did not return (same cause) | 184 failed reads |
| 10 | 346 failed reads, returned in 1 s | unchanged |
| 20 | 640 failed reads | unchanged |

**Cause, read from the library rather than guessed.**
`cdio_paranoia_read_limited()` compares its retry counter with the limit only
inside `if (retry_count % 5 == 0)`, so no other value is ever matched and the
skip it gates never happens. The code is at `lib/paranoia/paranoia.c` in
upstream libcdio-paranoia, read at `384f4da`; the installed version is
10.2+2.0.1. **Platterpus exposes `-r` to its users** (`cyanrip_backend.py:237`,
range 0 up, default 5), and their rig was left at 3.

**Fix:** `crip_frame_retry_limit()` rounds the per-frame limit up to a multiple
of 5, with 5 as the floor. The whole-track `-Z` ceiling is our own loop and keeps
the value as given. When the two differ, `Retry limit:` says both. The leading
number is still the `-r` value, which is what `tools/probe-argv-surface.py` and
their parser read; their matcher is the label alone
(`platterpus@86f0547:src/platterpus/parsers/cyanrip_log.py:1983`). The `-j`
record's `retry_limit` stays the `-r` value.

**What the fix does to the audio**, checked against the source `.bin` rather than
against the log: at `-r 3` and `-r 10` alike, sectors 400–402 come back as zeros
and are counted in `Ripping errors:`, and every other sector of both tracks is
byte-identical to the source. **One bad sector costs three**, which is the
library's skip granularity. It is reported as errors, never presented as audio.

**Pinned** by `bad_sector` in `tests/rip_images.py`, which also covers
`Track N read with errors.`, the arm no test had reached (Platterpus's D4).
Revert-proved: with the raw value restored and the binary rebuilt, the scenario
fails on crip()'s 60-second timeout. **Upstream has the same exposure**, so it is
a `docs/SETTLED.md` upstream row. **Hardware:** the error path is the same code
on a drive. A real damaged disc also exercises the MMC read, which this does
not.

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

### With paranoia disabled (`-P 0`), one unreadable sector hangs the rip at any retry limit

**Measured 2026-09-23** with `tests/badsector.c`, at `-r 10` and at `-r 1`:
the read of the sector after the bad one never returned, the stall watchdog
reported it every 10 s, one SIGTERM printed `Trying to quit` and did not end
the process, and a second SIGTERM ended it **with no footer**. A backtrace put
the main thread in `cdio_paranoia_read_limited()` → `cdio_cddap_read_timed()`.
It was retrying the same sector, and libcdio's error buffer had grown to 1.5 MB
of `Unable to access sector 411: skipping...`.

**Cause:** in disable mode the skip that the retry limit gates does not move
the read forward, so the counter resets and the loop starts again (same
function as the `-r` defect above). **Rounding the limit does not help**:
`-r 10` hung too.

**Why not now.** The remedy is ours to write: at level 0, read with
`cdio_cddap_read()` and our own bounded retry instead of paranoia's loop. But
that changes the read path on a real drive. Paranoia reads in chunks and a
per-sector read may be much slower, so it is a drive change that needs a drive
to verify. **Exposure today:** Platterpus never passes `-P`
(`platterpus@86f0547:src/platterpus/adapters/cyanrip_backend.py`, no `-P` in
its argv), so their rips run at level 3, where the fixed path above applies.
Our own image suite passes `-P 0` and has no bad sectors. **An upstream report
belongs to libcdio-paranoia**, not to cyanrip.

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
of set resting on the same kind of premise, and `tests/release_gate.py:448`
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

### `Interrupted sample freshness` fails intermittently, and the second failure named the arm

**The heading used to say "TWICE", which the third occurrence falsified**; the
dated occurrences below are the record. **Third occurrence 2026-09-26**, at
`0f5f935`, run by hand straight after regenerating the sample, not in a suite:
the fresh probe's log has `Repeating ripping (5 out of 200 …)`, then the album
summary, `Rip completed:  no (interrupted by SIGTERM, 0 of 3 tracks)` and
`Interrupted at: track 1, mid-read`, with no `Stopping, ripping incomplete!`.
So the SIGTERM landed between `-Z` passes, not inside a frame loop. Three
re-runs straight afterwards exit 0.


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

### `Lap commit list names its range` times out under parallel load, and the call that hangs is now named

**THE HEADING USED TO PIN A COUNT — "FOUR times", then "FIVE" — and every
occurrence falsified it.** That is the number-incremented-rather-than-derived
defect, in the file that records it, and it is the same one that turned three
`SETTLED.md` rows stale on 2026-09-22. The dated occurrences below are the
record; the heading states the property. **Thirteenth occurrence 2026-09-26**, with
`2e9884d`'s tree before its commit, in a full suite of 91 that ran at about half
speed throughout (the black-box sweep took 422 s against 217 s an hour earlier):
`Ok: 90  Timeout: 1`, `30.02s`, call #4 again after three calls took 2.09 s, and
**1.20 s** standalone straight afterwards, exit 0.
**Twelfth occurrence 2026-09-25** at
`2966369`, in a full suite of 90: `Ok: 89  Timeout: 1`, `30.01s`, call #4 again
after three calls took 2.03 s, and **0.82 s** standalone straight afterwards, exit 0.
**Eleventh occurrence 2026-09-25** at
`8825255`, in a full suite: `Ok: 88  Timeout: 1`, `30.02s`, call #4 again after
three calls took 2.23 s, and **1.04 s** standalone straight afterwards, exit 0.
**Tenth occurrence 2026-09-24** at
`0698258`, in a full suite: `Ok: 88  Timeout: 1`, `30.01s`, call #4 again after
three calls took 3.61 s, and **1.13 s** standalone straight afterwards.
**Ninth occurrence 2026-09-24** at
`eb29e6b`, in a full suite: `Ok: 88  Timeout: 1`, `30.09s`, call #4 again after
three calls took 3.29 s, and **1.20 s** standalone straight afterwards.
**Eighth occurrence 2026-09-24** at
`22dc7d7`, in a full suite: `Ok: 88  Timeout: 1`, `30.01s`, `SIGTERM`, and again
*"THE CALL THAT HUNG IS #4: 16 9 --head 59cb5a9"* after three calls took
2.22 s. **1.23 s** standalone immediately afterwards. **Seventh occurrence 2026-09-23** at
`9dccde7`, in a full suite: `Ok: 86  Timeout: 1`, `30.01s`, `SIGTERM`, and the
instrument named the hung call — *"killed by signal 15 after 3 completed
call(s) … THE CALL THAT HUNG IS #4: 16 9 --head 59cb5a9"*, the first three
taking 1.90 s together. **1.17 s** standalone immediately afterwards. Call #4
after three completed is the same stopping point `tests/lap_commits.py` records
for the 2026-09-18 occurrences. **Sixth occurrence 2026-09-22** at
`460599f`: `30.01s`, `SIGTERM`, **1.22 s** standalone immediately afterwards.
Same bimodality, nothing new.

**Fifth occurrence 2026-09-22**, at `11667d6`, in a full suite:
`Ok: 85  Fail: 1  Timeout: 1`, exit 1, `30.01s`, `SIGTERM`. Standalone
immediately afterwards: **1.12 s**. Same test, same limit, same
full-suite-only context, same bimodality — a 27-fold gap between the two
modes with nothing in between. Nothing new; recorded because a timeout is
neither a pass nor a fail, and an unrecorded one reads as a green suite.
The same run's other failure (`Settled facts`) was real and is fixed —
three rows pinned literals that a new rig session falsified.

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

### `track is partially accurately ripped` is said of a track whose bytes are wrong

**Found by Platterpus in round 26's real test** (their lap 5 §B3), and
confirmed here from our filed copy. `docs/rig-2026-09-24-df91ae7/rips/after-cancel.log`
reads track 1 as `EAC CRC32: 0E91CD1A`, with 20 `FIXUP_ATOM`s and `Ripping
errors: 0`. The five other rips of track 1 in that session read `B0D122E7`, each
an exact AccurateRip match. Its v1 and v2 are `not found`, and only
`Accurip 450: 57722DDE (matches Accurip DB, confidence 200, track is partially
accurately ripped)` matched. The footer counts it in `Tracks ripped partially
accurately: 1/14`.

**It is not a one-off, and our own record held the proof for thirteen days.**
`docs/rig-2026-09-11-ddc1e8c/rips/derived-wavpack.log` has the same track 1, the
same `0E91CD1A` and the same `Accurip 450: 57722DDE`, on another build, in
section K2, two rips after the cancel rather than straight after it, where that
session's own J read track 1 correctly. So the drive returned the same wrong bytes twice, and paranoia
accepted them twice. Found by scanning every filed track-1 read, not by memory.
Nothing in this repository mentioned it until now.
**That scan is now a tool**: `tools/cross-rip.py <bundle>` compares every read
of each track across a bundle's cyanrip logs, grouped by disc and read offset,
and names both of these logs. `tests/cross_rip.py` asserts it does.

**What is wrong is the label, not a number.** Every checksum is truthful.
`Accurip 450` covers one sector (`src/checksums.h`), so a match says that sector
is right and says nothing about the other 14,486. *"Partially accurately
ripped"* reads as mostly right, and here the track was wrong. The wording is
upstream's. **Not changed in `.16`**: it is a line Platterpus parses, so the
wording is round 27's, with their answer first. Their side is re-reading by
default and saying what matched.

**Their answer is in, in round 27 lap 2 B1.** Inside the parenthetical they read
only `confidence\s+(\d+)`, and treat confidence ≥ 1 with a non-zero CRC as a
match. So the words can change freely, **provided `confidence N` appears only on
a match**. `Tracks ripped partially accurately: N/M` they match by its exact
label and use only as a cross-check, so renaming that label needs their
both-wordings release first. Their EAC-compatible log's proposed wording is
theirs, under H4.

**Reworded for `.17`, not released.** The match now reads `(matches Accurip DB,
confidence N, one frame only; whole-track checksums not found)`: `confidence N`
stays on the match alone, as their condition asks, and `matches Accurip DB` is
kept. No string they match is removed, so nothing of theirs has to ship first.
It is a P2 line, so round 27 lap 4 announces it. `.16` and every filed log keep
the old tail. The tally label is unchanged: renaming it needs their
both-wordings release first.

**Our answer to their EAC-log wording, for round 27 lap 4: amend one clause,
accept the rest.** They proposed, per track, `Only one frame matched AccurateRip
— rest of track unverified (confidence 200)  [57722DDE]  (AR frame 450)`, and in
the summary `1 track(s) matched AccurateRip on one frame only`. The summary is
accepted as written. **The per-track line says less than was established**: the
450 line is printed only when both whole-track lookups returned −1, compared and
not found (`src/cyanrip_log.c:594`). *"Unverified"* reads as *not checked*,
which is round 7 H4's own distinction: *"it failed to match the database, and
those are different claims."* And the confidence belongs to the frame that
matched, not to the rest. Proposed: `Only one frame matched AccurateRip
(confidence 200); whole-track checksums not found  [57722DDE]  (AR frame 450)`.

**A second defect was sitting under the same line, and it is fixed.** A 450
lookup that missed fell through to the whole-track checksum
(`crip_find_ar()`, their B1a). See `docs/SETTLED.md`'s upstream section.

### The album loudness block describes whatever was read, and calls it the album

**Found in round 26's real test.** `docs/rig-2026-09-24-df91ae7/rips/cancel-me.log:75`
prints `Album integrated loudness (R128): -14.4 LUFS` for a rip interrupted
about 40% of the way into track 1, with `0 of 14 tracks` completed. It is the
loudness of the audio that passed through the `ebur128` graph, which on an
interrupted rip is a partial track, and on every `-l` rip is the selected
tracks only. The four owned rows and libavfilter's block both say "Album".

**Not fixed, because the fix is a wording decision.** The candidates are
leaving the four owned rows out when not every track of the disc was ripped,
or adding a scope line beside them as `Scope:` does for paranoia. Both change
rows Platterpus parses into `album_loudness`. It belongs to the next round,
with the consumer's answer first.

**Their answer is in, in round 27 lap 2 B2, and it asks for no change.** Since
their 0.6.57 they label the figures by what they covered, read off our
`Rip completed:` and `Interrupted at:` lines. If we add a qualifier, **it must be
a NEW line**: their patterns anchor on the four labels, and a renamed row falls
back silently to libavfilter's block, keeping the figure and losing the stable
source.

### `Encoder errors:` counts an interrupted track's partial file as a track encoded

**Found reading round 27's Full run** (`docs/rig-2026-09-26-221a1df/`), and it
was already in round 26's. `rips/cancel-me.log:87` reads `Encoder errors: none;
1 track encoded` two lines above `Rip completed:  no (interrupted by SIGTERM, 0
of 14 tracks)` and `Interrupted at: track 1, mid-read`. `.15`'s
`docs/rig-2026-09-24-df91ae7/rips/cancel-me.log:88` says the same.

**The count is exact about what it counts, and the noun is wider than that.**
`ctx->tracks_encoded` is incremented for every track that had an encoder
context, once each context closed without error (`src/cyanrip_main.c:2719-2740`).
Track 1's encoder did close cleanly, over the part of the track that was read.
So "1 track encoded" is true of an encoder and reads as a whole track. A reader
who takes the three footer lines together is not misled; one who reads
`Encoder errors:` alone is.

**Not fixed.** The candidates are counting only tracks whose read completed, or
saying which encoded tracks were partial. Either changes a P2 line Platterpus
parses, so it belongs to a round, with the consumer's answer first, like the
album loudness entry above.

### Every figure the log reports about the audio is measured BEFORE the filter graph

**Found by the 2026-09-22 acceptance session, and it is not the defect it looks
like.** Section P3 of that run ripped track 1 of a real disc twice, back to
back, changing one flag:

| | `-H -E` | `-H -W` |
|---|---|---|
| `EAC CRC32` | `B0D122E7` | `B0D122E7` |
| `Accurip v1` / `v2` | `5D3C90CB` / `22B9924D` | `5D3C90CB` / `22B9924D` |
| `Sample peak level` | `94.3% (-0.5 dBFS)` | `94.3% (-0.5 dBFS)` |
| `True peak level` | `0.3 dBFS` | `0.3 dBFS` |
| `Integrated loudness (R128)` | `-13.9 LUFS` | `-13.9 LUFS` |
| `REPLAYGAIN_TRACK_PEAK` | `1.029445` | `1.029445` |
| `Preemphasis` | `none detected (deemphasis forced)` | `none detected` |

`docs/rig-2026-09-22-2cce60d/session/script-report.json`, steps 217 and 221.
Identical to the digit on everything except the one field that reads a setting.

**That reads like the round-15 ternary cascade returning. It is not, and the
difference was measured rather than argued.** Six invocations on disc images,
`docs/rig-2026-09-22-2cce60d` notwithstanding — this part needs no drive:

| flags | fixture | output PCM sha256/16 | bytes |
|---|---|---|---|
| `-H -E` | plain | `05f1fe8cedaff2a4` | 2,822,400 |
| `-H` | pre-emphasised | `05f1fe8cedaff2a4` | 2,822,400 |
| `-H -W` | plain | `efc8702f95ebc8b3` | 2,822,400 |
| `-H -W` | pre-emphasised | `efc8702f95ebc8b3` | 2,822,400 |
| `-E` | plain | `fea860467bdb5368` | 1,411,200 |
| `-W` | plain | `e499ef1f978fe435` | 1,411,200 |

**Four distinct audio streams. One set of reported numbers.** The fix works —
forcing de-emphasis under `-H` changes the samples, disabling it changes them
back, and the automatic path on a flagged disc lands exactly on the forced one.
What the log cannot do is *witness* any of it.

**The mechanism, read from the source rather than inferred.** `filter_frame()`
pushes the **input** frame into the ebur128 graph
(`src/cyanrip_encode.c:656`) and only afterwards pushes the same frame into the
de-emphasis/HDCD graph (`:677`), whose *output* is what reaches the encoders
(`:715`). The two graphs are **siblings off one source, not a series**.
Separately, `crip_process_checksums()` takes the same `data` that is then handed
to `cyanrip_send_pcm_to_encoders()` (`src/cyanrip_main.c:872`), so the checksums
are over the raw disc bytes.

**The two halves want opposite things, and collapsing them would be the fix
going wrong.**

- **`EAC CRC32` and the AccurateRip checksums are CORRECT pre-filter** and must
  stay there. EAC and AccurateRip define theirs over the raw disc samples; a
  post-filter value stops matching the database on every de-emphasised or HDCD
  disc. What is missing is only that nothing says so — the same `Scope:`
  problem the paranoia counters already solved, one field over.
- **The loudness block is WRONG pre-filter.** `Sample peak level:`,
  `True peak level:`, both R128 figures and all five `REPLAYGAIN_*` tags
  (`src/cyanrip_main.c:433-449`) go into the delivered file and describe audio
  that is not in it. ReplayGain exists to normalise playback of *this file*.

**A source comment asserts the opposite of what the code does.**
`src/cyanrip_encode.c:597-602` says the peak is *"deliberately measured on the
same frames that go into the ebur128 filter rather than on the bytes off the
disc: a raw-byte measurement would differ legitimately whenever deemphasis or
HDCD decoding is active"*. The frames that go into the ebur128 filter **are** the
bytes off the disc. The two methods agree because they read the same thing, and
the case the comment names is exactly the case where that thing is the wrong
one — *a fixture whose numbers agree by construction cannot discriminate*, with
the comment as the tell.

**Reach, stated because a 247-of-247 acceptance pass invites the wrong
reading.** Only runs with `-H` and/or active de-emphasis. Without either,
`dec_ctx->filt.buffersrc_ctx` is NULL and the raw frame goes straight to the
encoders (`src/cyanrip_encode.c:674`), so pre- and post-filter are one frame and
every figure is right. **No Platterpus rip is affected today** — none of the
eight `Invoked as:` lines in the 2026-09-22 session carries `-H`, `-E`, `-W` or
`-x`, read off the logs rather than off their rig-check summary. So it is a real
defect with, right now, zero consumer exposure.

**Not fixed here, deliberately.** Moving the measurement downstream changes the
*values* of five P2 lines and five metadata tags on affected rips, which is
contract surface and wants a round — and the round in flight is pinned at
`2cce60d`, where a finding defaults to the next round. Reported in round 23 §H.

`sc_deemph_with_hdcd()` now pins both halves with opposite intents and says
which is which; the checksum half failing is a regression, the loudness half
failing is the fix landing.

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
session that produced a `Cache probe:` line is here now: twelve of them**, derived
by scanning `docs/rig-*/session/transcript.txt` rather than by adding the ones
anyone remembered. **This sentence said "eight" while the table held nine rows**
— written 2026-09-15 and never recounted when 09-17 was added, which is the same
stale-tally defect the section is about. The count is now taken from the table
and the table from the transcripts, and `sc_cache_table_matches_the_transcripts()`
prints both totals when they disagree. The prediction this section made was *"an
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
| 2026-09-22 `2cce60d` | 251.4 ms | 42.1 ms | 62.9 ms | 67% |
| 2026-09-24 `df91ae7` | 382.7 ms | 82.2 ms | 95.7 ms | 86% |
| 2026-09-26 `221a1df` | 362.8 ms | 62.2 ms | 90.7 ms | 69% |

**Each row names its directory**, `docs/rig-<row>-<build>/` — so `2026-09-15` is
the `00:58` session and `2026-09-15b` the `12:01` one, which is how they are
filed. `sc_cache_table_matches_the_transcripts()` resolves every row that way
and fails on a row that names no session **and** on a session with no row; the
label read `2026-09-15a` until that test was written and pointed at nothing.

**Hundreds of ms uncached: confirmed, twelve times. "A cached read of a few ms":
FALSIFIED** — 42 to 82, not 2.2. All twelve end identically, at
`at least 2048 sectors … search ceiling reached`. The tenth, 2026-09-22, is the
first on `2cce60d` and the first taken inside a full acceptance session; it
changes nothing, which is the point — **ten runs, three builds, four calibration
clusters, one answer.** The eleventh, 2026-09-24 on `df91ae7`, round 26's real
test, calibrated `miss_cost` at 382.7 ms, higher than any row above, and ended
the same way. The twelfth, 2026-09-26 on `221a1df`, round 27's Full run,
read 362.8 ms and 62.2 ms, the same two figures as 2026-09-17 to the tenth of a
millisecond, and ended the same way again.

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

### Our gate has four defects, two found by Platterpus's questions, and none was fixed on finding

**Items 1 and 3 FIXED 2026-09-23, before round 25 opened**, by the change that
added `version_refusal()`, `declared_version()` and `C29_FROM_ROUND` to
`tools/release-gate.py`. Every file of a round, ours and inbound, is now read
for its version: one declaring more than we implement refuses the round, naming
the file (C15), and from round 25 a lap declaring less than an earlier lap of
either side refuses it too (C29). Tests
`test_a_peer_lap_above_our_protocol_refuses_the_round` and
`test_a_peer_lap_below_an_earlier_lap_refuses_the_round`, revert-proved one half
at a time. **The C29 boundary is load-bearing, not caution:** moved to 0, it
reopens round 8, whose laps 3–15 of ours declared 1 after their lap 2 declared
2, and the real gate refuses a release. Platterpus's gate already had the C15
half (`platterpus@86f0547:scripts/handshake.py:1920`, `refused_round_files`).

**Item 2's coverage half FIXED the same day; its behaviour is not, on purpose.**
The meta-check now admits a letter suffix, so C13a is a row it can see. It
turns rows on by the version each block's heading names rather than splitting
once at v3. And it carries `KNOWN_DIVERGENCES`, printed on every run, which
fails if an entry stops being true. C13a is the one entry. **Replaying every
round lap by lap found the premise of "latent" was wrong and the conclusion
right.** Six laps, in rounds 7, 8, 11, 12 and 15, follow the lap at which our
gate first reads the round closed. All six declare `GO`, each the other side's
closing lap, so reopening and staying closed agree on every one. **C13a as
written would refuse all six**, which is why round 25 proposes amending the row
rather than implementing it. Three labels were wrong too.
`test_latest_lap_can_reopen` claimed C13 and built C13a's case. Two ambiguity
tests claimed *"C13 (S2 rule 3)"*. So C13 read as covered three times and had
no test of its own case. It has one now, and removing its claim leaves C13
uncovered. Item 4 remains, below.

**Item 4, and v5's C40 fixture, are written out of the v6 path, 2026-09-23.**
For a file declaring 6, `peer_verdict_resolution` no longer consults the
closing file's `INBOUND-HELD`. The candidate is the newest peer lap in our own
`inbound/`, which is what v6 §5b step 1 says. So no literal
filename is matched. `test_v6_closes_on_a_record_that_can_occur` uses the
fixture a real round produces, with v5 on the same bytes as the control, and
the control does not close. The same change requires `HANDSHAKE-AGREED-CHANGES`
on a v6 `GO` (C44). **Both are live from `643631b`**, where v6 landed and
`PROTOCOL_VERSION` went to 6 with no other change to this code. They apply to a
file declaring 6, and no lap has declared 6 yet: v6 §14 waits for both gates to
say in a lap that they implement it. Both halves are revert-proved.

**Found 2026-09-22, answering their post-round-23 standing status**
(`docs/handshake/inbound/status-2026-09-22-v0.6.53-c2f43d28.md`, the
**protocol** row). They described two defects in their own gate as *"portable
shapes, so we are telling you rather than checking your tree"*. **Both are in
ours.** That is the compare-do-not-acknowledge rule paying out twice.

1. **A peer lap declaring a protocol we do not implement still decides a
   close.** `tools/release-gate.py` refuses a higher `HANDSHAKE-PROTOCOL` on our
   own laps (`why`, `protocol_ok`). But the inbound loader
   (`load_rounds`, the `peer_latest` block) reads the peer lap's verdict and
   release state without reading its version. Measured: our lap 3 declaring 5,
   their lap 4 declaring **6**, `GO`, released — **our gate closes the round**,
   *"peer GO resolved per v5 §5b from round-30-lap-04.md"*. Refusing rather than
   guessing (C15) applies to the file we wrote and not to the file we act on.
2. **Row C13a has no test, and our gate does the opposite of it.** C13a says a
   lap arriving after a round is terminal is refused as an illegal transition,
   and the round stays closed. The coverage meta-check,
   `test_every_conformance_row_has_a_test()`, collects row IDs with
   `^\| (C\d+) \|`, which cannot match `C13a`. So the row is invisible to the
   check that exists to find uncovered rows. `test_latest_lap_can_reopen()`
   claims `Covers: C13` and asserts that a complete `GO` followed by a `HOLD`
   **reopens** the round. That is v2 behaviour, which v3 removed. Their
   defect was that the coverage check exempted rows by heading; ours is that
   the row pattern drops a row by spelling. Same outcome: a row in force with
   no test.

**Two more, found 2026-09-23 by dry-running round 24's close on a throwaway
record** — our real lap 1, a synthetic lap 2 and a draft lap 3, nothing read
from Platterpus's real lap 2, which is held:

3. **C29 is not applied to peer laps.** A peer lap 2 declaring protocol **4**
   after our lap 1 declared 5 closes the round on our gate. C29 refuses a
   lower version than an earlier lap of the same record. Same root as item 1:
   the inbound loader never reads the peer lap's version at all.
4. **Under v5, C37 matches the peer lap's FILENAME inside our
   `HANDSHAKE-INBOUND-HELD`.** `peer_name in self.inbound_held`, so a closing
   lap that describes the lap — *"your round 24 lap 2 — sha256 …"*, which is
   how every one of our `INBOUND-HELD` lines has been written — is refused with
   *"not named in our HANDSHAKE-INBOUND-HELD"*. Round 23 lap 5 is written that
   way and declared 4, so it never met the check. **Until the gate reads a
   `round N lap L` reference, a v5 closing lap must name `round-NN-lap-LL.md`
   literally.** That is a rule for whoever writes the lap, and a brittleness in
   the gate, not a defect in any lap already sent.

**Why none was fixed on finding, and why 2 and 4 still are not.** All four
were latent: no peer lap declared more than 5 or less than an earlier lap, and a
closing lap can name the file. This paragraph also said *"no lap has followed a
closed round"*, which the replay above shows is false: six have, all `GO`.
Items 1 and 3 are fixed. **Items 2 and 4 wait for v6, and on purpose.** Item 4
is v5's literal reading of C37, which v6 replaces. Item 2's row is proposed for
amendment rather than implementation, because as written it refuses those six
laps.

### `docs/seam-commands.md` carries FIVE known-wrong statements

**Consolidated here 2026-09-15.** They were recorded in two different files, one
of them a 1,100-line standing status, which is how a set of three reads as three
unrelated one-offs instead of a document to fix. Consolidation applies to
documentation and never to evidence; this is documentation.

| # | what it publishes | what is true | found |
|---|---|---|---|
| 1 | §7: *"Every value either took effect or was refused with a message"* | **48 of the 68 accepted rows** were graded from exit status alone — re-measured 2026-09-16, and the *"49 of 111"* this row carried was a count against an older binary | ours |
| 2 | line 504: `-p '99=drop'` accepted, exit 0 | the binary **refuses** it | theirs, lap 16 §B3 |
| 3 | line 97: `-D` is `directory` / `str, path` / `writable` / *"output directory"* | it is `folder_scheme`, *"Directory naming scheme"* (`cyanrip_main.c:1603` at the pin) — a **relative** scheme, with `-F` its per-track sibling | theirs, lap 16 §B3 |
| 4 | the §1 provenance warning: *"The cyanrip column is `?` throughout below … Their half arrives in the round-8 return file"* | **0 of §1's 17 rows** carry `?` in the cyanrip column; all 17 say `HAVE`. Counted by reading the column, not the sentence | ours, 2026-09-22 audit |
| 5 | §4 NEED item 4 asks for *"an escape mechanism in the `-a` / `-t` grammar — or a written statement that there is none"* and describes a U+2236 workaround | **§1's own `-a` row, in the same file**, says both sides `HAVE` it: *"there IS an escape: `\\:`"* and *"escape shipped lap 31"*. The file contradicts itself; whether Platterpus's U+2236 substitution is still in their code is theirs to say, and is not claimed here | ours, 2026-09-22 audit |

**RE-MEASURED 2026-09-16, and the split of who fixes what is not what this entry
said.** Platterpus pointed out that §7 carries its own *"This section is
GENERATED by `tools/probe-argv-surface.py --markdown` … Never hand-edit it"*.
That is **our** tool, so rows 1 and 2 are ours to regenerate; only row 3 is
hand-written prose in a jointly-owned section.

**Row 2 is fixed by regenerating.** The live binary refuses `-p '99=drop'` with
`Invalid track number 99 for pregap, list has 2 tracks!`, exit 1.

**Row 1 is NOT, and it is a defect in the generator rather than in the committed
copy.** The sentence is emitted by the tool. Measured 2026-09-16 and **re-measured
2026-09-22 on `0.9.4-rc2+platterpus.14`, unchanged**: **116 rows, 48 refused, 68
accepted — and 48 of those 68 carry `(no header field exposes this)`.**
`probe-argv-surface.py:99` returns `accepted` on exit status
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

**Do not cite any of the five.** Row 3 is the one that has already cost
something: the real semantics are exactly why an empty leading component made a
multi-component scheme resolve **absolute**, and a reader who believed line 97
would not have looked.

**NONE of them is fixed, and not for want of knowing the answer.** The file is
shared and neither project owns it — a one-sided edit is how two copies of one
spec come to disagree, which has already happened once to `PROTOCOL.md`. They go
in together at the next joint version bump.

**Deliberately NOT added to round 20.** R1 fixes a round's close conditions at
lap 1 and round 20 has two; a third arriving mid-round is the exact failure R1
exists to stop, and these break nothing in `fe4d2c4`.

**This paragraph then called them *"a round-21 bundle"*, and rounds 21, 22 and
23 all closed without it.** Nobody proposed the bump, because the entry that
named the round was not something any lap-1 author read. It is the same gap as
the joint entry below on K1–K3 — a change agreed or planned, and then left to
memory across a round boundary. **They are now listed in that section's
consolidated table of shared-document defects, which is what round 24's lap 1
cites**, so the bundle has a place to be picked up from rather than a round
number to go stale.

---

## Open, ours, and NOT solvable here — no drive in this environment

Every one of these needs hardware. Listed so a green suite is never mistaken for
coverage.

| gap | status |
|---|---|
| `-x` correctness on a real drive | **measured twelve times, wrong every time** — `at least 2048 sectors` against `cd-paranoia -A`'s 137–140, latest 2026-09-26. This cell said *"measured twice"* while the table above held nine rows |
| C2 error reporting | the rig's drive reports C2 unsupported; never exercised anywhere |
| `-f` offset autodetection | **partially retired 2026-08-12** — exited 0 and rediscovered `+667` on the rig. The *value* is now confirmed; behaviour on a drive with a different offset is not |
| damaged media | never tested; no damaged disc available |
| CD-TEXT from a physical disc | `mmc_read_cdtext` is a different code path from the image parser, and no disc with CD-TEXT has been read |
| ~~the diagnosed-abort exit code~~ | **RETIRED 2026-09-22.** `cyanrip -N -l 1` with no `-s` exited **1** with `Offset is unset!` at column 0, `Rip completed:  no (aborted, 0 of 14 tracks)` and a complete footer — `docs/rig-2026-09-22-2cce60d/session/script-report.json` step 212. The reason given here (*"every rig rip so far had `Ripping errors: 0`"*) had **already been false since 2026-09-10**: seven filed rig logs carry `Ripping errors: 1`, counted off `docs/rig-*/rips/*.log` rather than remembered |
| ~~a non-zero `Read stalls:` count~~ | **RETIRED 2026-08-26**, and this row outlived the retirement by a month. **Five** filed rig logs carry a populated line, up to `5 reads exceeded 10s; longest 11s (track 1, LSN 8322)`, counted off `docs/rig-*/rips/*.log`. The rule it carried still holds and is why it is kept visible: **a silent watchdog is not a working watchdog**, and zero heartbeats on healthy media — which is what all eight rips of 2026-09-22 report — is the expected result and evidence of nothing |

The remaining `TODO`s in `src/pregap.c` are upstream's, carried with the feature
from PR #115, and are open questions rather than known defects: whether libcdio
can report a first track other than 1, and whether the macOS path can be
restored (it needs `cdio_get_device_fd()`, which is not in libcdio 2.1.0 —
verified against the installed headers *and* the `.so` export table).

---

## Open, joint — belongs to the seam, not to one side

### Three agreed protocol changes never reached the spec, and both sides certified v5 as complete — LANDED IN v6, 2026-09-23

**Landed in round 25.** All three are in `docs/handshake/PROTOCOL.md` v6: K1 in
§4a, K2 in §5a, K3 as §5d. So is the agreed-change ledger, §5e, which exists
because of this entry. v6 is byte-identical in both trees (`643631b`,
`platterpus@53b3c04`), and round 25's closing lap is the first to carry the
ledger with every entry named. The history below is kept as the reason.

**Found 2026-09-22 by the pre-round-24 document audit, and it is the most
important thing that audit found.** Round 22 agreed three changes to the shared
protocol and **none of them is in `PROTOCOL.md`**:

| item | agreed where | what it says | in the spec? |
|---|---|---|---|
| **K1** | round 22 lap 1 §0.1, their lap 2 §0.1 *"agreed … with no amendment"* | a lap number is claimed on **release**, not on writing | **no** |
| **K3** | the same two laps | a warning about a **held** lap cannot travel inside it — the one legitimate relay | **no** |
| **K2** | round 21 lap 4 §K, *"needs nothing from round 22 but the shared-file edit"* | `HANDSHAKE-INBOUND-HELD` for sent laps, `HANDSHAKE-INBOUND-OBSERVED` for held ones | **no** — `grep -c INBOUND-OBSERVED docs/handshake/PROTOCOL.md` is `0`, though both sides have declared the field in every lap since |

**How they fell out, and it is a gap between rounds rather than inside one.**
Round 22 lap 1 declared protocol 4 *"deliberately not 5, although §K1 and §K3
below propose the v5 text"* — correctly, because a version bump is something
both sides ship. So the text waited for a v5. Round 23 then drafted v5 from
**its own** §0.1 — the close rule and its readability condition — and its §13
says *"v5 is v4 plus the two clauses round 23 §0.1 named, and nothing else."*
Nobody carried round 22's agreed clauses across. **Platterpus re-derived v5's
diff in their lap 4 §B and confirmed "the two clauses and nothing else"; we
wrote that sentence.** Both sides certified it as complete, accurately, against
the wrong list.

**Round 23's own §0.2 is the same failure one level down**, and the audit found
that too: the condition was *assent, an amendment or a refusal*, Platterpus
assented, and the banner qualifier it agreed was never implemented. **A round
closes on agreement, which is correct — and then the building is left to
memory, and memory does not survive a round boundary.** Nothing in either
tree tracks an agreed change from *agreed* to *landed*.

**What it costs today: nothing that breaks, and something that will.** Both
sides already behave as K1, K2 and K3 say — the rules are practised, just not
written. But a third consumer, or either side in six months, reads the spec, and
the spec is silent on three rules both projects follow. **A practised rule the
spec does not state is the drift the shared spec exists to prevent.**

**Round 24, and it is a proposal, not an edit:** a v6 carrying K1, K2 and K3 —
their text is already agreed, so drafting is transcription — and a mechanism so
this does not recur. The obvious shape is that a closing lap enumerates every
change the round agreed, each with the commit that landed it or `not landed`,
so a close cannot silently leave work behind. **That mechanism is itself a
protocol change and needs their assent**, so it is proposed, not built.


### The four shared documents: every known defect, in one table

**Rows 1–7 were fixed in round 25 (2026-09-23)**, by `PROTOCOL.md` v6,
`OWNERSHIP.md` v3 and `seam-rules.md` v6, all byte-identical in both trees. Drafting found an eighth, in `OWNERSHIP.md`'s opening
paragraph: it says every consumer holds its copy at the same path, and
Platterpus's protocol is at `docs/handshake-protocol.md`. `OWNERSHIP-v3.md`
fixes that too. Rows 8–12, `seam-commands.md`, wait for round 26, because the
fix needs `tools/probe-argv-surface.py` to measure what it asserts.

**Consolidated 2026-09-22 by the pre-round-24 audit**, read against the four
files as they stand — byte-identical in both trees, `tools/seam-sync-check.py
--fetch` exit 0 at `platterpus@52b4428`. None of these breaks a gate. Each is a
statement a reader of the spec is entitled to believe and should not. **None can
be fixed from one side** (`OWNERSHIP.md` §4), so this is the bundle a joint
version bump would carry, and round 24 proposes it rather than editing it.

| # | file | what it says | what is true | detail |
|---|---|---|---|---|
| 1 | `PROTOCOL.md` | nothing on K1, K2 or K3 | all three agreed in round 22, and both sides practise them | the entry above |
| 2 | `PROTOCOL.md` §8, *"Rows added in v3/v4"* | *"These are not yet in force."* | the heading's own condition, *"required once both gates implement 4"*, is met: ours implements 5 (`tools/release-gate.py`, `PROTOCOL_VERSION = 5`), theirs 4 (`platterpus@52b44282:scripts/handshake.py:1093`) | here |
| 3 | `PROTOCOL.md` §8, *"Rows added in v5"* | *"Not yet in force."* | **False since `platterpus@c2f43d28`**, when their gate reached 5. This cell predicted that on the day it was written, and it happened the same evening. It is row 2 again: a spec frozen by version cannot be edited when a present-tense sentence goes stale. The conditional headings are already correct; the fix is to delete both body sentences | here |
| 4a | `PROTOCOL.md` §5b step 1 and row C37 | the candidate lap must be declared in the closing file's own `HANDSHAKE-INBOUND-HELD` | then step 3 and C40, *"the whole of v5's saving"*, cannot fire on a real record, because the saving lap is written after the closing file | the v5 entry below |
| 4 | `PROTOCOL.md` | `HANDSHAKE-FROM-COMMIT` defined once | the two projects read it two ways | round 23 lap 3 §D. v5 §13 says so itself, so this is a known gap rather than a false statement |
| 5 | `OWNERSHIP.md` §3 | *"we cannot run their program, read their source, or reproduce their environment"* | **"read their source" has been false since 2026-09-13.** Both repositories are public, and this environment reads theirs anonymously on every `seam-sync-check --fetch`. The other two clauses were not checked, so this makes no claim about them | `CLAUDE.md`, *"This rule used to carry the clause…"* |
| 6 | `OWNERSHIP.md` §5 | *"we cannot read each other's source"* | same as row 5 | same |
| 7 | `seam-rules.md` S-13 | round 7: *"laps to close: **37 and open**"*, *"releases produced: **0**"* | round 7 closed `GO` at **lap 39** (`round-07-lap-39.md`), and produced one release, `+platterpus.5`, at `release-ledger.tsv` row 11. `CLAUDE.md`'s copy of this table was corrected on 2026-09-16; the shared copy was not | here |
| 8–12 | `seam-commands.md` | five statements | see that entry's table | *"`docs/seam-commands.md` carries FIVE known-wrong statements"*, above |

**Fix row 5 first.** It is a false premise under a rule that may still be
true. §3 argues that the systematic-gate duty is Platterpus's partly *because*
we cannot read their source. The duty may well stay with them, since they hold
the drive and run both sides' code. But part of the argument for it is now
false, and a rule defended by a false reason can be dismissed by refuting that
reason.

**Scope, stated so a blank is not read as a pass.** Checked: every dated,
versioned, counted or present-tense claim a grep for those shapes finds in all
four files, plus `seam-rules.md` read through, S-1 to S-18 and §4–§5. Its one
count about our binary, *"They document 41 flags"*, still matches `--help` on
`+platterpus.14`. **Not checked:** counts about Platterpus's argv builder
(*"we send 18"*, *"Seventeen flags reach the argv builder"*). Those are theirs
to state, under S-9.

### A cited commit was orphaned by a squash merge and a branch delete — it HAPPENED, and the recovery was luck

**Filed as an event rather than a hazard, because a near miss recorded as a
success is a hazard that comes back.**

Round 23 lap 3 §D2 warned Platterpus that their work reaches `main` by **squash
merge**, so a commit on their working branch never becomes an ancestor of
anything there; delete the branch and routine `git gc` **destroys** it rather
than hiding it, breaking any citation that names it. Their lap 4 accepted the
reasoning, checked it rather than taking it, and recorded *"`claude/session-omka9f`
will not be deleted"* in their `TASKS.md`.

**The PR squash-merged and the branch was deleted four minutes later.**
`b5af9bec` and `19c8ad20` — the two commits round 23's citations name, one of
them in **our lap 3, which was already sent and immutable** — became unreachable
on their remote. They were recovered because a session clone still held the
objects and the branch was pushed back at the same tip, and because GitHub had
not run `gc` in the interval. Verified here afterwards against their remote:
both are reachable as ancestors of `refs/heads/claude/session-omka9f`, now at
`e8a47562`. Neither is directly fetchable by SHA, which is GitHub refusing
arbitrary-SHA fetches rather than evidence of absence — **reachability through
the ref is the whole of what makes them resolvable, and it is exactly what a
second delete removes.**

**THE FIRST DIAGNOSIS WAS WRONG, WE ADOPTED IT, AND IT IS CORRECTED HERE.**
Platterpus first reported that a human had clicked *delete branch on merge*
despite a warning that was in the PR body twice, in bold, at the top, and in two
separate operator messages — and offered the memorable framing that *the delete
is a button that appears after the merge succeeds, when no PR text is on
screen.* **That account was filed in this entry verbatim and it is false.** They
retracted it in their post-round-23 status: the cause was the repository's
**"Automatically delete head branches" setting**, proven rather than supposed —
a merge performed over the API, with **no human present**, deleted the branch
again. The setting is now off, which is the durable fix, and the branch is
restored and will stay.

**This is `separate the finding from the diagnosis` failing in the entry filed
about a diagnosis failure.** The finding — two cited commits orphaned, one named
by a sent lap — was right and is unchanged. The cause was not. And the remedy
the wrong cause implies, *remind the human not to click it*, **would have
changed nothing**, which is exactly why this file says to reproduce a cause
before adopting its remedy. We did not; we adopted it inside the same commit
that praised the reasoning.

**The corrected lesson is stronger than the one it replaces.** A warning was
written, escalated, and re-escalated at an actor who was never in the loop.
Their words still hold and now bite harder: **a comment where a check belongs is
not a fix, arriving through a UI instead of through code** — and *the response
each time the risk came up was to write the warning more emphatically rather
than notice that emphasis was not the failing axis.* The axis was not emphasis
and it was not the reader either. **It was a repository setting, and no amount
of prose addressed to anybody could reach it.**

**Verified here rather than taken on the correction.** Both `b5af9bec` and
`19c8ad20` are reachable as ancestors of `refs/heads/claude/session-omka9f`,
now at `9cc23eab`, on their remote. A first pass of that check said NOT
reachable and was wrong — it scanned stale `refs/remotes/origin/*` without
fetching the branch, which is this file's own *`git branch -r` is a cache, not
the remote* rule biting in the middle of verifying somebody else's claim.

**We have the same shape, and looking for it is the point of filing this.**
`CLAUDE.md` carries *"never push a topic branch — the deletion is not available
to us"* as prose backed by an observed `HTTP 403`, with an explicit note that
there is deliberately no test because the only check would reach the network.
That reasoning still holds and the exposure is still real: **the rule holds here
because the proxy refuses, not because anything of ours checks.** Prose plus an
accident of the environment is the same class as a bolded PR body; it just
happens to have a stronger accident behind it.

**The general fix is Platterpus's and it is a round-24 item: the sha256 is the
anchor, the commit is a fetch hint.** Both sides already declare a lap's hash and
both reproduce it before filing. A content hash cannot be pruned. If a citation
names the hash first, a pruned ref degrades it from *fetchable* to *verifiable*
instead of to nothing. Round 23 lap 5 adopts it for its own citations a round
early; settling it in the spec is joined with §D1's two meanings of
`HANDSHAKE-FROM-COMMIT`, because both are the same question — **what does a
citation name?**

**And our lap 3's citation of `b5af9bec` cannot be re-anchored**, because lap 3
is sent. That is the argument for the proposal rather than an objection to it:
the one artifact that could not be fixed is the one naming a commit and not a
hash. Lap 3 does declare lap 2's sha256 and byte count in
`HANDSHAKE-INBOUND-HELD`, so it degrades to verifiable — which is precisely the
property the proposal would make the rule.


### The close condition cannot be satisfied by the side that speaks first — ADOPTED AS v5 §5b, AND AS WRITTEN IT CANNOT DO THAT

**Status 2026-09-22, evening: in the spec, built in both gates, and unable to
save the lap it was adopted to save.** Round 23 adopted `PROTOCOL.md` v5,
byte-identical in both trees, with this as §5b and Platterpus's readability
condition as §5c. Our gate implements it, keyed on each file's declared
version. Theirs implements it from `platterpus@c2f43d28` (21:30Z by commit
date). At `52b44282` it still implemented 4, and this entry said so twelve
minutes before it stopped being true.

**The defect is in the text, and we drafted it.** Step 1 and row C37 require
the candidate peer lap to be one the closing file *declares* in its own
`HANDSHAKE-INBOUND-HELD`. The peer lap that would make a transcription lap
unnecessary is always written after that file, so it can never be declared in
it, and step 3 — *"the whole of v5's saving"* — cannot fire on any real
record. Platterpus found it from the other end: C40 is unreachable under that
reading, so they read *"enumerated"* as enumerated by the gate when it
decides. Their post-round-23 status asks whether ours differs. **It does**,
measured 2026-09-22 with our own loader:

| record | our gate |
|---|---|
| our lap 3 holds their lap 2; their lap 4 (`GO`, released) arrives later | **not closed** — *"round-30-lap-04.md is not named in our HANDSHAKE-INBOUND-HELD"* |
| the same, except lap 3 declares it holds lap 4 | closed — the only way C40 fires, and the lap could not have existed when lap 3 was written |

**And our test proves the code, not the rule.** `test_v5_close_rule_and_the_v4_control`
passes on the second record: `_v5_ours()` defaults to
`held="round-30-lap-04.md"` (`tests/release_gate.py:2928`). A fixture that
cannot occur made the one mechanism v5 exists for look exercised.

**The remedy is v6 wording, not a gate edit by one side.** Their reading is
the one under which §5b does what it says, and C42 already makes the gate print
the lap it resolved from, so audit does not depend on the closing file's
declaration. Proposed in round 24 lap 1, and landed in round 25 as v6 §5b
step 1 and C37. **The divergence is not gone yet.** Our gate reads a file
declaring 6 the decision-time way, and every lap so far declares 5, which our
gate still reads literally. So the two gates keep two readings until laps
declare 6. Round 25 closed on our gate by ordinary transcription, not by
step 3. Kept under *Open* until a round has closed under §5b step 3.


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

### A HELD lap's draft verdict reaches the compiled `Handshake:` line — AGREED IN ROUND 23, BUILT 2026-09-23

**Built 2026-09-23 in `tools/gen-handshake-state.py`, as `DRAFT_QUALIFIER`.**
When the newest lap is held, the open state now ends ` (draft — lap not released
for reading)`. Closed and released states are unchanged. The test,
`test_a_held_lap_banner_says_it_is_a_draft`, reads the expected string out of
Platterpus's round 23 lap 2 table, the shape they ran through their parser,
rather than retyping it. It is revert-proved. **It ships in no release yet**: a
build of the tip carries it, and `+platterpus.15` is the first release that
can. The history below is kept because it is why the ledger in v6 §5e
exists.

**Status 2026-09-22, found by the pre-round-24 document audit: the change was
agreed and nobody implemented it.** Round 23 §0.2 asked for a qualifier —
`round N lap L OPEN, verdict GO (draft — lap not released for reading)` — and
Platterpus assented in their lap 2 §C.2 after running four banner shapes
through their real parser and their real classifier, both safe, ending *"Go
ahead and land it."* Our laps 3 and 5 correctly say the **condition** closed,
since the condition was assent, an amendment or a refusal. **But
`grep -rn "not released for reading" src/ tools/gen-handshake-state.py` returns
nothing**: the change itself was never written, and `+platterpus.14`, cut the
same day, does not carry it.

**A condition satisfied is not a change shipped, and the audit is the only thing
that noticed.** Nothing in either gate checks that an agreed change landed; the
round closed on the agreement, which is correct, and the building was left to
memory. It is authorised by round 23 and is ours to build; the next release is
the first that can carry it, the way `.14` carried round 22's. **Nothing is
written for that release yet**, so that is a plan, not a fact. Round 24's
opening lap should say the change was missed.


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

**A CLAIM THAT THIS HAPPENED ON 2026-09-22 STOOD HERE AND WAS FALSE.** It read
that tracks 3 and 5 were superseded by an automatic re-rip whose log reached
neither project. Platterpus refuted it in round 23 lap 2 §A and the refutation
was verified rather than accepted: the session's own report carries
`retried_tracks: [{track 3, converged false, replaced false}, {track 5, ...}]`,
and a swap happens only on a **converged** re-read --
`platterpus@a0aed36:src/platterpus/workers/rip_worker.py:2705-2708`, read at
that SHA. Neither converged, nothing was swapped, the first pass's bytes are on
disk, and the album log describing them is the correct log. Their
`SupersededTrack` addendum exists (`:2673`) and was not due, so **its absence was
a correct negative** -- this file's own `none` versus `unknown (reason)` rule,
failed from the other direction.

**The cause was a filing decision.** The eight `.platterpus.json` records were
left out of `docs/rig-2026-09-22-2cce60d/` as the consumer's artifact, and then a
claim was made about a question one field in them answers. It is the second time
in four days that file has carried an answer nobody opened -- the 2026-09-19
bundle's `.log` showed no `-l` while its report showed `-l 3,5`. The one that
settles this is now filed at
`docs/rig-2026-09-22-2cce60d/rips/secure-reread.platterpus.json`.

**So this entry is still open and still ours, and the 2026-09-22 run is NOT
evidence for it.** It needs a case where a swap actually happened. Platterpus's
§E Q1 asks whether it stands on other evidence; it does -- round 8 `J14`, and the
2026-09-15b session, which filed a real `secure-reread.addendum.txt`. Their Q2
offers the sharper version: they will capture the discarded re-rip's log in their
own report, and would rather emit a marker we define than keep a private field.
**That is the round-24 item** -- not the superseded-timestamp complaint, but
whether our format grows a way to mark a superseded or abandoned read at all.

### A track's per-track lines are computed from the REQUEST, not the outcome

**HALF FIXED, AND THAT HALF SHIPPED IN `+platterpus.14` AT `3e01bb3` ON
2026-09-22.** Written at `89a57d6` in round 22, released once Platterpus 0.6.53
accepted both wordings. **The half that remains is the harder one** — `File(s):`
still lists what was *requested* rather than what was written, because it prints
before the encoders are joined — and it is why this entry stays under *Open*: a
heading that said *fixed* over an entry describing a live defect is the label
rule this repository applies to log lines, turned on its own notes.

**Two sentences in the blockquote below were true when written and are now
false**, and they are kept because the record of why a release waited is worth
having: `+platterpus.14` *has* been cut, legitimately, after the release it
waited for; and *"naming it there is what enforces the order"* was refuted before
the round closed — a close cannot name a release that does not exist when it
happens, which `CLAUDE.md` records. **Nothing machine-checkable enforced the
order; the plan and the operator did.**

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
