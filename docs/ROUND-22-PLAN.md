# Round 22 — a plan, not a round

*Written 2026-09-16, while round 21 lap 1 was still held. Round 21's close
conditions were fixed and could not grow (R1), so every item below was
deliberately outside it.*

> **STATUS, 2026-09-18 — round 22 is open and this file is being worked.** It
> said *"nothing here is started"*, which was true for two days and is the kind
> of sentence that goes quietly false. **Item 1 is executed** (`89a57d6`, option
> 2 only; see its banner). **Items 1b, 2 and 3 are not started.** Each section
> carries its own banner; this line is the index and nothing more, so a reader
> who trusts it and reads no further is wrong about at most which section to
> open.

**Why this file exists.** Three defects are understood well enough to fix and
were each deliberately left alone, for three different reasons. *"We decided
against it"*, *"nobody got to it"* and *"it is waiting on evidence that does not
exist yet"* are three different states, and a list that cannot tell them apart
is the confusion `CLAUDE.md`'s "Planned, not built" section exists to prevent.

**What would make this file wrong.** Round 21's hardware session. Item 2 is
designed around a series of timings nobody has yet recorded; if the session does
not run `-x` with `-j`, item 2 does not start. Say so rather than quietly
re-planning it.

---

## 1. The per-track block is computed from the request, not the outcome

> **EXECUTED 2026-09-18, and only the option below that was chosen.** Shipped at
> `89a57d6` with the artifacts regenerated at `ae29818`. Option 2 was taken as
> written: the per-track line now reads `Track N read successfully!` and a new
> `Encoder errors:` line lands below `Ripping errors:` in the footer. **Option 3
> — marking failed entries in `File(s):` — is still not done**, and the plan's
> reason for deferring it holds exactly: it prints from the same pre-join
> moment, so it is possible only as a second pass now that the footer names the
> tracks. `docs/KNOWN-ISSUES.md` keeps it open. Announced to Platterpus in round
> 22 lap 1; everything below is the plan as written, kept because the rejections
> are the part worth reading.

### What is wrong

```
Track 2 ripped and encoded successfully!      <- the encode failed
  File(s):
    .../2.flac                                <- 32768 bytes; intact is 253742
```

Two causes that need different fixes:

| | mechanism |
|---|---|
| `File(s):` | built from `ctx->settings.outputs` and the naming scheme at `cyanrip_log.c:642`; consults nothing about what was written |
| `Track N ripped and encoded successfully!` | printed when the **read** finished. The encoders run asynchronously; **at the moment it prints, the fact it asserts is genuinely unknown** |

The second is not a wording defect. No rewording of a line printed at time T can
report a fact that exists at time T+1.

### The principle to fix it by

> **The per-track block reports the READ. The footer reports the ENCODE.**

This is the age defect one axis over, and this repository has already paid for
that lesson once: *event time and processing time are two independent ages, and
collapsing them is the exact failure mode that misleads an operator.* A
superseded track's `creation_time` describing the read that was thrown away is
the same shape. So is a per-track line describing an encode that has not
happened.

### Options, with the one to take

1. **Defer the whole per-track block until encoder status exists.** Rejected: it
   moves every per-track block to the end of the log, and the log is a progress
   record as well as an archival one. It would also be the largest log-format
   change this seam has ever shipped.
2. **Make the per-track line claim only the read, and add a footer block naming
   tracks whose encode failed.** **Take this one.** The reword is small and
   truthful at the moment it prints; the footer block is additive and lands
   where the outcome is known — beside `Ripping errors:`, which round 21 has
   just moved to the same place for the same reason.
3. **Mark entries in `File(s):` whose encode failed.** Rejected on its own: at
   print time the status does not exist. It becomes possible only *after* (2),
   as a second pass, and is not worth a separate round.

### What it costs

- Two P2 log lines change. **Both are contract surface**, so this is a handshake
  round and not a commit — the same discipline round 21 applied to the two
  changes it shipped.
- `sc_encode_failure_reaches_the_log()` already provokes the state with a 32 KiB
  `RLIMIT_FSIZE` cap and already asserts the log/`-j` agreement. It extends
  rather than needing a new fixture.
- **No hardware.** This reproduces on a disc image. It must not consume rig time.

### How to know it worked

The same scenario asserts that a track whose encode failed is **not** described
as having succeeded, and that the footer names it. Revert-proved by restoring
the old wording and watching that assertion fail — and, per today's lesson, by
checking the revert removes what the assertion reads rather than renaming a
wrapper around it.

---

## 1b. Two protocol proposals from Platterpus, arriving early and on purpose

**Their round-21 lap 4 §K, now released and read** — filed at
`docs/handshake/inbound/round-21-lap-04.md`. This section was first written
from the operator's relay while the lap was held and sourced to the relay
rather than to the lap; the lap now confirms it and the sourcing note is kept,
because *how we came to know something* is part of the record. Neither is a
round-21 condition and neither needed an answer before the close.

**K2 is closed and needs nothing from round 22 but the shared-file edit.** Both
fields — `HANDSHAKE-INBOUND-HELD` for sent laps, `HANDSHAKE-INBOUND-OBSERVED`
for held ones — are in both sides' lap headers already. **K1 is the one that
still needs a lap, and it is ours to carry into round 22's lap 1.**

**Why they arrived at their lap 4 rather than our lap 2, which is the part
worth keeping:** both are changes to `docs/handshake-protocol.md`, which
neither project owns, and **the fork opens every round**. An item raised at
their lap 2 costs a lap that the same item raised at our lap 1 does not. So
they sent them with the lap they were already writing, marked as not
conditions, with an explicit opt-out. **That is the cheapest possible place to
raise a shared-file change and we should do the same in reverse.**

1. **A lap number is claimed on RELEASE, not on writing.** Round 21 produced
   **two held lap 4s** — theirs and our withdrawn draft — because each side
   allocates the next number from its own tree and neither gate can see the
   other's held laps. **Already on our list independently**, which is worth
   more than either of us proposing it alone. The cause is recorded in
   `tests/release_gate.py`: *"the number is chosen when a lap is WRITTEN and
   the divergence appears when it is not immediately sent."*

2. **`HANDSHAKE-INBOUND-HELD` pins a hash of a document that declares itself
   mutable.** **Our own round-21 lap 5 is the worked example**, and they caught
   it in our text before we did: it recorded their held lap 4 as 31,732 bytes /
   sha256 `989427bd…` at `27a174dc` and told them to file against that hash.
   The read reproduces at that commit forever; the document was **47,478 bytes**
   two revisions later and still held. Our stopgap is two fields —
   `HANDSHAKE-INBOUND-HELD` for sent laps and `HANDSHAKE-INBOUND-OBSERVED` for
   held ones — but a local field is not a protocol change, which is exactly why
   this belongs in the shared document.

**A third thing came out of the same exchange and is ours to raise**, because
it has no home in either project's rules: **a warning about a held lap cannot
travel by lap.** They wrote *"the SHA you recorded is stale"* into the lap we
were blocked from reading, then sent it through the operator because they
noticed the problem. Had they not, we would have discovered it by a failed
filing. The standing status is the obvious channel — it is not a lap and both
sides read it between rounds — but nothing says so.

---

## 2. The cache probe's calibration

### What is wrong

`-x` reports **at least 2048 sectors**; `cd-paranoia -A` on the same drive and
disc reports **137, then 140**. High by roughly a factor of fifteen, and the
reference itself moves between runs, which caps how precisely any of this can
ever be stated.

The mechanism is understood: `miss_cost` is calibrated with a **full-stroke
seek** (`end_lsn - 10` back to the seed, measured at 342.9 ms) while the loop's
test read is a **backseek of at most the current run length** (2.22 ms/sector).
The threshold is `miss_cost / CACHE_HIT_RATIO` = 86 ms, so every test read scores
as a hit and the search runs to `PROBE_MAX_SECTORS`. **Raising the ceiling moves
the number and fixes nothing.**

### Why this could not have been planned before now

**NINE filed rig sessions demonstrate the defect and not one can be used to fix
it.** `Cache probe:` publishes three numbers; the step lives in the *series* of
per-run times, which was never recorded anywhere. A read time is a measurement of
a drive at a moment and cannot be re-taken. (This said *"eight"*, which was true
when written; counted 2026-09-18 by asking which rig directories hold the line
rather than from memory — the same undercount as `CLAUDE.md`'s *"all three"*,
which is the reason `sc_cache_table_matches_the_transcripts()` exists and checks
the count in both directions.)

**Round 21 fixes that and nothing else about this.** `-j` now carries a
`cache_probe` block with the calibration reads, the threshold, the ratio and one
entry per run. The decision rule is untouched on purpose.

### The steps, in order, and each one gated on the last

1. **The session records a series.** Round 21 §4b, explicitly not a close
   condition. **If this does not happen, stop here.**

   **IT HAS NOT HAPPENED, TWICE, FOR TWO DIFFERENT REASONS — so this step is
   still the gate and the plan is still parked.** Both attempts are 2026-09-17:

   - `docs/rig-2026-09-17-fe4d2c4/` **ran the probe and got the old `-j`
     schema**, because the session was installed on the release pin rather than
     the test pin. The series block exists only in `3952c03`.
   - `docs/rig-2026-09-17-3952c03/` **has the right build and did not run the
     probe at all.** `-x` is absent from `Invoked as:`, the log reads `Cache
     model:    1200 sectors (drive cache size not probed)`, and `Cache probe`
     appears 0 times in that session's app log.

   *Did not happen* and *happened and produced the wrong thing* are different
   claims, and collapsing them here would lose the only actionable part: the
   next session needs `-x` **on `3952c03` or later**, and either half alone is
   not enough.
2. **Split the classification out of the I/O loop into a pure function.** Today
   the predicate `t * CACHE_HIT_RATIO < miss_cost` is inline in a loop that also
   issues reads, so it cannot be tested without a drive. Given the series it
   becomes a function of data — the same move as `tests/subq.c` for the Q
   sub-channel decode, and `tests/diagcache.c` already proves the shape works.
3. **Unit-test the pure function against the recorded series**, plus synthetic
   ones: a clean step, no step at all, a noisy step, and the degenerate
   all-hit series the current rule produces. **Write these before changing the
   rule**, so the tests are a specification rather than a description of
   whatever the new code does.
4. **Then change the rule.** The likely shape is step detection rather than an
   absolute threshold — find the run length at which the re-read time jumps,
   which needs no calibration read at all and so cannot be defeated by
   calibrating against the wrong seek distance. **Do not commit to this until
   step 3 shows it on real data.**
5. **Re-validate on hardware**, against `cd-paranoia -A` as an external
   reference, remembering that the reference moves 137→140 between runs and so
   cannot settle anything finer than that.

### What it costs

- `Cache probe:` is a P2 line and the number it prints would change. Handshake
  material, announced with the build that carries it.
- **`Cache model:` is a different line and must not move.** It reports what
  paranoia is configured with, not what the drive has.
- Steps 2 and 3 need no hardware. Steps 1 and 5 do.

### The trap to avoid

**Do not raise `PROBE_MAX_SECTORS`.** The header comment already says so and the
reason is worth repeating: the ceiling is not the cause, and moving it produces a
different wrong number while looking like progress.

---

## 3. `probe-argv-surface.py` asserts more than its method establishes

**Found 2026-09-16, while checking a correction from Platterpus**, and it is the
cause of two of the three known-wrong rows in `docs/seam-commands.md` rather than
a coincidence.

### Three findings, one root

1. **The classifier returns `accepted` on exit status alone.** At
   `probe-argv-surface.py:99`, when no header field exposes a flag, the outcome
   is `accepted` with the note `(no header field exposes this)`. Measured on the
   current binary: **116 rows, 48 refused, 68 accepted — and 48 of those 68 have
   no field to check.** So **three quarters of the accepted rows were never
   observed to take effect**, while the generated summary says *"Every value
   either took effect or was refused with a message."*
2. **`-p '99=drop'` is published as accepted, exit 0.** The live binary refuses
   it: `Invalid track number 99 for pregap, list has 2 tracks!`. A regeneration
   alone fixes this row.
3. **`--check` has never been able to run on that file.** It refuses with
   *"carries no generated-block delimiters"*. §7 has declared itself generated
   since it was written and **nothing has ever verified that it is** — which is
   how (1) and (2) drifted. A check that cannot fire.

### The fix

- **A third outcome**, not a reword. The tool already distinguishes `ignored`
  (a field exists and does not reflect the value) from `accepted`. It needs
  `unobservable` — exit 0, no field to check, **whether it took effect is
  unknown**. That is the `none` versus `unknown (reason)` rule applied inside the
  generator that publishes our own contract surface.
- **`--gate` must not change.** It fires on a silent drop; an unobservable flag
  is not one. Assert that separately or the fix quietly widens a CI gate.
- **Insert the delimiters, then regenerate.** After that `--check` is a gate and
  §7 cannot drift again.

### What it costs

`docs/seam-commands.md` is **jointly owned**. The content of §7 is ours to
generate, but any change moves the shared hash, so it ships as a version bump
both sides carry on the same day. **No hardware.** Round 21 §5 has already put
the choice to Platterpus: this round or the next.

---

## What this plan does not contain

- **C2** — `UNREACHABLE` on the rig's BDR-209D, which reports it unsupported. Not
  *not yet*; it needs a different drive or it stays unverified permanently.
- **`-f` offset autodetection** — not yet done, and testable on the reference
  disc now. Deliberately not added to round 21: R1.
- **damaged media**, **CD-TEXT from a physical disc** — both need a disc nobody
  has produced yet.
- **The `Lap commit list names its range` timeout** — one occurrence, cause not
  established. It gets a plan when it recurs, not before.
