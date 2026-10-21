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

**What it is not.** Not external bugs we work around — those are this file's
last section, kept apart from our own. Not designs we chose not to build —
those are `docs/history/CLAUDE-2026-10-21.md`, "Planned, not built". Not a
description of behaviour we *have* — that is `PROVIDER-CONTRACT.md`, and it is
generated.

**Where the closed items are.** Everything fixed, landed or decided by
2026-10-21 moved word for word to `docs/history/KNOWN-ISSUES-2026-10-21.md`,
which is not maintained. The cache probe's section stays here although its
defect is fixed, because its table gains a row with every run on a drive, and
`cache_table_matches_the_transcripts` reads it from this file.

**Rules for this file.** An item leaves only when it is fixed and a test pins
it, or when it is shown never to have been real, and it leaves to a dated file
under `docs/history/`. An item that turns out to be
someone else's is moved, not deleted, with a note saying where. Nothing here may
say "probably" without saying what would settle it.

---

## Open, ours, and solvable

**Round 30 carried these, on the operator's word of 2026-10-05**, and closed
on 2026-10-06; entries below fixed since say so in their headings. The round
was to stay open until everything here that could be fixed was fixed, both applications
ship betas, and an acceptance run of both passes. So *"not now"* and *"round
31"* stopped being reasons. Where an entry below still says why it waited,
that was the reason before 2026-10-05, kept as the record.

### A sub-channel pregap reads differently between rips, and the log states one value

**Found 2026-10-07, reading the run on `.21`** (`docs/rig-2026-10-07-ca3f3ea/`),
and as old as the filed record: section P3 ripped track 1 twice, minutes apart,
and one `Gaps:` list says `94 frame pregap in track 9` and the other `95`.
Counted again 2026-10-21 from the `Gaps:` lists of the reference disc's 227
filed logs, from 33 sessions on the BDR-209D: track 9's pregap read 94 frames
in 192, 95 in 34 and none in 1, and track 4's 158 in 221 and none in 6. No
other track's varied. The TOC signals neither, so each value is our sub-channel
search's, and the track block says so (`Pregap source: sub-channel`). This
entry said *"no other track's does"* of track 9 for two weeks while track 4's
zeroes were counted in `STATUS.md`.

**What it costs**: under the default action the pregap merges into the track
before, which ends at the track's `INDEX 01` either way, so no audio byte
moves; the cue sheet's `INDEX 00` does, by a frame for track 9 and by dropping
it for track 4. With `-p` set to drop or to a track of its own, the audio would
move.

**Fixed in the code for `.26`, without a drive, and the drive has to confirm
it.** The search's answer was a function of the Q frames the drive returned, one
per sector asked for, each taken to belong to that sector, so two searches
could disagree only if a frame answered for another sector, or a corrupt frame
passed its CRC. `tests/subq.c` reproduces both symptoms with the old search on
a simulated drive: one read answered by the next sector's frame gives 95, and a
first read answered by the previous track's frame gives none. Each mode-1 frame
carries its own address, so the search now places each frame there, aims later
reads by how far off the drive answers once two frames agree, and asks again
for a sector answered by another's frame. On a drive whose frames all answer
for the sector asked the answer is unchanged, compared over 200,000 simulated
searches. It also removes an assert a stale frame of a third track could reach,
which ended the process with exit 134. The reasoning, the comparison and the
revert-proof are in `docs/pregap-carry.md`. **What only a drive can say** is
whether the BDR-209D's frames do answer for other sectors: from `.26` a
disagreement between the two searches is printed on `Pregap source:`, so rig
rips of the reference disc with that line absent, and `Gaps:` reading 94 and
158 throughout, are the confirmation. `STATUS.md`'s `subchannel-pregap-varies`
tracks it.

### The disc's ISRCs read as none on the rig's drive, while EAC's cue of the same disc has them

**Found by the claude-code-skills session's known fixes of 2026-10-21, item 8**,
and untracked here until then. On the BDR-209D, `.25` printed `Disc ISRC:
none (libcdio returned none)` for every track of the reference disc
(`docs/rig-2026-10-20-5f1d036/`, the secure re-read's log, lines 82 and 165 on),
while EAC's cue of the same disc on the same drive gives an ISRC for every
track, track 1's `GBAAM7800003`
(`platterpus@1b532e69:output_reference/EAC_flac/eac_baseline_police_classics.cue:13`).
Whether EAC read those codes from the disc's sub-channel is not stated in its
log; it is the only source a cue's `ISRC` lines have in EAC.

**What it costs**: the files carry MusicBrainz's ISRC, which names a recording
rather than this pressing, and `--prefer-disc-isrc` has nothing to prefer.

**What is known, read from libcdio, not run**: `cdio_get_track_isrc()` on Linux
is `mmc_get_track_isrc()`, a READ SUB-CHANNEL with format 03h and the track in
byte 6, the same from 2.1.1 to its master (`lib/driver/mmc/mmc.c`,
`mmc_get_mcn_isrc_private()`). It returns NULL for three different answers:
the command failing, a reply shorter than 21 bytes, and the drive's TCVal bit
clear, which is the drive saying it found none. Our log cannot tell them apart,
and it does not name the libcdio version the rig ran. The ISRC is read before
any sector of the track, while the pre-emphasis read beside it reads a sector
first because a drive answers for wherever it last read (upstream's `59b3f2d`).

**For `.26`, without a drive**: when libcdio returns none on a drive, cyanrip
reads 200 of the track's own Q frames with READ CD, the path the pregap search
has used on the BDR-209D since 2026-08-04, and takes the ISRC from the first
CRC-valid mode-3 frame; if none carries one, it asks libcdio again with the
head inside the track. Each outcome is a different measurement, and the reason
says which: a code; `none (libcdio returned none, also after reading 200 Q
frames of the track, none an ISRC frame)`, which would mean the drive builds
its formatted Q without mode-3 frames; or one of the counts for frames failing
their CRC or carrying no well-formed code. `tests/subq.c` holds the decode,
against an ISRC frame built from cdrdao's encoder, and the scan, on the
simulated drive. **The drive settles it**: the next rig rip of the reference
disc on `.26`. If formatted Q carries no mode-3 frames, the next step is the
raw P-W sub-channel, which a drive returns as recorded.

### `Lap commit list names its range` times out under parallel load, and the call that hangs is now named

**THE HEADING USED TO PIN A COUNT — "FOUR times", then "FIVE" — and every
occurrence falsified it.** That is the number-incremented-rather-than-derived
defect, in the file that records it, and it is the same one that turned three
`SETTLED.md` rows stale on 2026-09-22. The dated occurrences below are the
record; the heading states the property. **Fourteenth occurrence 2026-09-26**, in
a fresh worktree at `e0471f4`, the first suite proving `.17`'s candidate, 91
tests: `Timeout: 1`, `30.02s`, and **1.38 s** alone straight afterwards; the
second proving suite passed. Which call hung was not captured.
**Thirteenth occurrence 2026-09-26**, with
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
Python interpreter per peer entry in a loop and shells out to git, and until
2026-09-27 it had **no explicit `timeout:` in `tests/meson.build`**, so it got
meson's default 30 seconds. Meson runs tests in parallel, and its neighbours include `Sanitizer
sweep` — a full `meson setup` plus `ninja` build of a second tree — the
838-invocation black-box sweep, and the argv probe. Contention is a plausible
mechanism for a slowdown. **It is not a plausible mechanism for 30×, and saying
so is the point of this entry.**

**The timeout is now explicit, 120 s, and it is a declaration, not a fix.**
This paragraph said the flake would not be fixed by widening the timeout, and
that if it recurred an explicit `timeout:` would become a declaration rather
than a suppression. It recurred, fourteen times. Two things settled it on
2026-09-27. Platterpus's round 28 lap 2 S21–S22 named the shape from their own
tree: *a wall-clock limit set by a library default in a parallel run*. And one
run, the first after this container started, took **48.4 s wall over 0.73 s of
CPU**, while the next run's timed calls added up to **0.84 s**. So the test waits
rather than works, and the wait can outlast 30 s. With 120 s, a pass between
30 and 120 s says *slow*, and a kill at 120 s says *hung*. **The mechanism is
still not established**, and the settling runs this paragraph named are still
the ones to do: the suite at `--num-processes 1`, and this test under a deliberate
parallel load. Every other test still on meson's default was measured at 9.2 s
or under.

**A second test has now timed out the same way, and it is not waiting: it is
starved.** 2026-09-30, at `5a0dc2f`, in a full suite of 97 on 4 cores:
`Round 16 acceptance checker` `TIMEOUT 30.07s`, `Ok: 96  Timeout: 1`, in the
suite straight after another full suite and a fixture rip. Alone straight
afterwards: **3.02 s, 2.94 s, 2.91 s**, and one run measured **2.97 s wall over
2.63 s of CPU**. So unlike `Lap commit list`, which spent 48 s of wall over
0.73 s of CPU, this one computes for its whole run, so what it lost in the
suite was CPU share, not a wait. **Why it lost that much in this run is not
established**: that run's `Black-box sweep` took 300.8 s, and in the green suite
that ended nine minutes before it, by its output file's time, the sweep took
317.7 s and this test 3.82 s. So the load was no heavier than in a run where
this test passed. **Not widened**, for the reason above.

**THE TWO SETTLING RUNS ARE DONE, 2026-09-30, and neither reproduces a
timeout.** The whole suite at `--num-processes 1`, at `97e8c4d`: 100 of 100 in
8 min 40 s of wall time, one run header in its testlog, with `Round 16
acceptance checker` at 3.26 s and `Lap commit list names its range` at 1.81 s,
which is what each takes in a normal parallel run (3.46 to 3.82 s and 1.77 to
2.04 s in the three full suites of the same afternoon). And each test ten times
while `Black-box sweep` and `Sanitizer sweep` ran beside them: `Round 16` 2.99
to 4.21 s of wall over 2.75 to 3.62 s of CPU, `Lap commit list` 1.41 to 1.79 s,
every run exit 0. **So the load these experiments can make does not slow
either test near 30 s**, and the timeouts stay rare events whose mechanism is
not established. There is nothing to fix until one reproduces, and each
occurrence is recorded here with the run it happened in.

**Why it matters beyond one flake.** A gate that can fail for a reason unrelated
to the code is the exact disease `PROTOCOL.md` R2 names when it forbids
enforcing `HANDSHAKE-CLOSE-BY`: *enforcement lets a clock skew block a release*.
A 30-second default doing the same thing to a release is the same shape, one
layer down.

### The cache probe's calibration was wrong (fixed for `.20`)

**FIXED for `.20`, 2026-10-05, released on beta 2026-10-06, and MEASURED FIVE
TIMES, IN AGREEMENT** (`394ab17`).
The probe now asks `cd-paranoia -A`'s question: a re-read is a hit when it is
faster than `MIN_SEEK_MS`, 6 ms (libcdio-paranoia `src/cachetest.c:41`, read at
`384f4da`), on its reasoning that no seek on a CD costs under ~10 ms. By that
criterion every "cached read" in the first sixteen rows below, 42 to 82 ms,
was a seek, which is how all sixteen sessions ran to the ceiling. A slow
re-read is tried three
times before it ends the search. `miss_cost` is still measured and printed, and
a drive whose full-stroke read beats 6 ms is refused as untimeable. The
`--diagnostics` record's `hit_ratio` is `hit_below_us` from
`cyanrip-diagnostics/7`.
`tests/cacheprobe.c` pins the decision against the table's own figures,
revert-proved. **What was not established was that it agrees with cd-paranoia on
a drive**: the first `-x` run on `.20`, beside section P's `cd-paranoia -A`, is
that measurement, and the doubling search can still only bracket the size
between two powers of two, so agreement means 137 to 140 falling inside the
bracket. **It did, six times**: the 2026-10-06 run on `.20` printed `128 to
255 sectors`, with a 1.7 ms re-read after 128 sectors and three re-reads of at
least 32.6 ms after 256, and `cd-paranoia -A`, run straight after it, reported
137 (`docs/rig-2026-10-06-5704062/`); the 2026-10-07 run on `.21` printed the
same bracket beside 144, the 2026-10-12 run on `.21` the same again beside
137 (`docs/rig-2026-10-12-ca3f3ea/`), the 2026-10-13 run on `.22` the same
beside 144 (`docs/rig-2026-10-13-200530e/`), the 2026-10-16 run on `.23`
the same beside 137 (`docs/rig-2026-10-16-891c79e/`), and the 2026-10-20 run
on `.25` the same beside 140 (`docs/rig-2026-10-20-5f1d036/`, the table's last
row). Six runs on one drive, and the search can say no more than a power of two. Everything below is the record of
the defect, kept because the table is checked against the transcripts.

**The seventeenth session, 2026-10-05 on `.19`, bracketed 128 to 255, and that
is the defect, not a fix.** Its calibration read was 304.2 ms, so `.19`'s
threshold was 76.05 ms, under the 81.3 to 82.2 ms classified reads of six
earlier rows. The search stopped at 256 sectors because the re-read there took
at least 76.05 ms, a figure the line does not print. Twelve rows calibrated
near 363 ms, and on any of them that re-read would have scored a hit. The same
row carries the first classified read under 6 ms in any filed transcript:
`cached read 1.5 ms`, after a 128-sector run, inside the cache `cd-paranoia -A`
measures. That is one sample in favour of `394ab17`'s premise and is not a test
of it (`docs/rig-2026-10-05-174a134/README.md`).

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
session that produced a `Cache probe:` line is here now: twenty-two of them**, derived
by scanning `docs/rig-*/session/transcript.txt` rather than by adding the ones
anyone remembered. **This sentence said "eight" while the table held nine rows**
— written 2026-09-15 and never recounted when 09-17 was added, which is the same
stale-tally defect the section is about. The count is now taken from the table
and the table from the transcripts, and `sc_cache_table_matches_the_transcripts()`
prints both totals when they disagree. The prediction this section made was *"an
uncached read in the hundreds of milliseconds beside a cached read of a few."*

| session | uncached (`miss_cost`) | cached | threshold (`miss_cost / 4` to `.19`) | margin |
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
| 2026-09-28 `e0471f4` | 362.7 ms | 81.3 ms | 90.7 ms | **90%** |
| 2026-09-28b `e0471f4` | 362.6 ms | 62.4 ms | 90.7 ms | 69% |
| 2026-09-28c `51cc789` | 362.0 ms | 81.6 ms | 90.5 ms | **90%** |
| 2026-09-30b `174a134` | 363.0 ms | 82.0 ms | 90.8 ms | **90%** |
| 2026-10-05 `174a134` | 304.2 ms | 1.5 ms | 76.1 ms | 2%, and **not** the ceiling: `128 to 255 sectors` |
| 2026-10-06 `5704062` | 251.0 ms | 1.7 ms | **6 ms**, `.20`'s threshold, `cd-paranoia`'s `MIN_SEEK_MS` | 28%; `128 to 255 sectors`, three re-reads after 256 sectors at 32.6 ms or more |
| 2026-10-07 `ca3f3ea` | 243.5 ms | 1.8 ms | **6 ms** | 30%; `128 to 255 sectors`, three re-reads after 256 sectors at 31.8 ms or more, beside `cd-paranoia -A`'s 144 |
| 2026-10-12 `ca3f3ea` | 244.2 ms | 1.6 ms | **6 ms** | 27%; `128 to 255 sectors`, three re-reads after 256 sectors at 29.9 ms or more, beside `cd-paranoia -A`'s 137 |
| 2026-10-13 `200530e` | 244.7 ms | 1.9 ms | **6 ms** | 32%; `128 to 255 sectors`, three re-reads after 256 sectors at 32.4 ms or more, beside `cd-paranoia -A`'s 144 |
| 2026-10-16 `891c79e` | 244.5 ms | 1.7 ms | **6 ms** | 28%; `128 to 255 sectors`, three re-reads after 256 sectors at 31.9 ms or more, beside `cd-paranoia -A`'s 137 |
| 2026-10-20 `5f1d036` | 362.7 ms | 1.5 ms | **6 ms** | 25%; `128 to 255 sectors`, three re-reads after 256 sectors at 58.7 ms or more, beside `cd-paranoia -A`'s 140 |

**Each row names its directory**, `docs/rig-<row>-<build>/` — so `2026-09-15` is
the `00:58` session and `2026-09-15b` the `12:01` one, which is how they are
filed. `sc_cache_table_matches_the_transcripts()` resolves every row that way
and fails on a row that names no session **and** on a session with no row; the
label read `2026-09-15a` until that test was written and pointed at nothing.

**Hundreds of ms uncached: confirmed, twenty-two times. "A cached read of a
few ms": FALSIFIED** by the first sixteen — 42 to 82, not 2.2 — and seen six
times, in the seventeenth to the twenty-second at 1.5, 1.7, 1.8, 1.6, 1.9 and
1.7 ms,
each after a run inside the cache. This said "eighteen" and "twice" for five days after the
nineteenth row was added, the stale tally this section is about, found adding
the twentieth. The first sixteen end
identically, at
`at least 2048 sectors … search ceiling reached`. The tenth, 2026-09-22, is the
first on `2cce60d` and the first taken inside a full acceptance session; it
changes nothing, which is the point — **ten runs, three builds, four calibration
clusters, one answer.** The eleventh, 2026-09-24 on `df91ae7`, round 26's real
test, calibrated `miss_cost` at 382.7 ms, higher than any row above, and ended
the same way. The twelfth, 2026-09-26 on `221a1df`, round 27's Full run,
read 362.8 ms and 62.2 ms, the same two figures as 2026-09-17 to the tenth of a
millisecond, and ended the same way again. The thirteenth, 2026-09-28 on
`e0471f4`, round 28's Full run, read 362.7 ms and 81.3 ms, a cached read at
90% of its threshold, and ended the same way. The fourteenth, 2026-09-28b, is
the same build on the same day through Platterpus 0.6.62: 362.6 ms and 62.4 ms,
a margin of 69%, and the same end. **Two runs of one build on one day
calibrated 0.1 ms apart and landed in different clusters of the four-run
control below**, 90% and 69%. The fifteenth, 2026-09-28c on `51cc789`, round
29's real test and the first on `.18`, read 362.0 ms and 81.6 ms, 90% of its
threshold, and ended the same way. The sixteenth, 2026-09-30b on `174a134`,
round 30's real test and the first on `.19`, read 363.0 ms and 82.0 ms, 90% of
its threshold, and ended the same way. **The seventeenth, 2026-10-05 on the same
build, did not**: a calibration read of 304.2 ms set the threshold under the
82 ms cluster, and the search stopped at 256 sectors, as the paragraph at the
head of this section says.

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

Evidence: `docs/rig-*/session/transcript.txt`, one per row: this said *"all
eight"* from the day the table held eight until 2026-10-05, when it held
seventeen, and the test below checks the rows rather than the count. The
transcripts are on the `evidence` branch since HR-2's move; re-derive with
`tools/evidence.py fetch`, then `tools/evidence.py cat
docs/rig-<row>/session/transcript.txt | grep "Cache probe:"` per row — and note that
`cached read` must be matched with a guard, because **`uncached` contains
`cached`**: the first derivation of this table read the same number into both
columns and produced a margin of exactly 400% on every row, which is what a
pattern that nearly matches looks like when it is wrong in a plausible way.

The gap is structural rather than noise, and it changes the fix. `last_hit_us`
is overwritten on every hit, so the figure printed is the re-read after the
last run that hit: in the first sixteen rows the **2048-sector** forward run,
the longest backseek the search ever performs, and in the seventeenth the
128-sector one. The
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

## Open, ours, and NOT solvable here — no drive in this environment

Every one of these needs hardware. Listed so a green suite is never mistaken for
coverage.

| gap | status |
|---|---|
| `--cache-probe` (`-x` until 2026-10-12) correctness on a real drive | **measured seventeen times on builds up to `.19`, wrong sixteen times** — `at least 2048 sectors` against `cd-paranoia -A`'s 137–140 — and right once by the defect's own arithmetic, 2026-10-05's `128 to 255` (see the cache section). **`.20`'s fix (`394ab17`) has run six times on a drive, 2026-10-06 to 2026-10-20, and agreed each time**: `128 to 255` beside `cd-paranoia -A`'s 137, 140 or 144. This cell said *"measured twice"* while the table above held nine rows |
| C2 error reporting | the rig's drive reports C2 unsupported; never exercised anywhere |
| `-f` offset autodetection | **partially retired 2026-08-12** — exited 0 and rediscovered `+667` on the rig. The *value* is now confirmed; behaviour on a drive with a different offset is not |
| damaged media | **read on hardware 2026-10-04**, `174a134` on the BDR-209D (`docs/rig-2026-10-04-174a134/`): a disc the drive reads differently each time from track 11 on. Measured: the drive reported no error (no `cdio error` or `Frame read failed` in any log), C2 is unsupported so it said nothing, reads slowed to **54 s**, one track took **8,161 s**, paranoia **skipped 2,586** times on it, and five `-Z` reads of each of five tracks gave five checksums. Whether the disc is damaged is an inference; the drive's behaviour is what was measured. **Still not seen:** a drive that reports a read as failed. From `.20` the `read with errors.` arm also takes a track paranoia skipped on, or one whose `-Z` reads never agreed, which this run's tracks 12 to 18 would have. The `-Z` arm printed it on a drive on 2026-10-06 (`docs/rig-2026-10-06-5704062/`, tracks 3 and 5); the skip arm has run only on the fixture (`tests/badsector.c`) |
| CD-TEXT from a physical disc | `mmc_read_cdtext` is a different code path from the image parser, and no disc with CD-TEXT has been read |
| ~~the diagnosed-abort exit code~~ | **RETIRED 2026-09-22.** `cyanrip -N -l 1` with no `-s` exited **1** with `Offset is unset!` at column 0, `Rip completed:  no (aborted, 0 of 14 tracks)` and a complete footer — `docs/rig-2026-09-22-2cce60d/session/script-report.json` step 212. The reason given here (*"every rig rip so far had `Ripping errors: 0`"*) had **already been false since 2026-09-10**: seven filed rig logs carry `Ripping errors: 1`, counted off `docs/rig-*/rips/*.log` rather than remembered |
| ~~a non-zero `Read stalls:` count~~ | **RETIRED 2026-08-26**, and this row outlived the retirement by a month. **Five** filed rig logs carry a populated line, up to `5 reads exceeded 10s; longest 11s (track 1, LSN 8322)`, counted off `docs/rig-*/rips/*.log`. The rule it carried still holds and is why it is kept visible: **a silent watchdog is not a working watchdog**, and zero heartbeats on healthy media — which is what all eight rips of 2026-09-22 report — is the expected result and evidence of nothing |

The six remaining `TODO`s in `src/pregap.c` are upstream's, carried with the
feature from PR #115, and are open questions rather than known defects: whether
libcdio can report a first track other than 1, whether `track_number - 1` is
always safe, whether the Q fields are always BCD, whether a cache defeat is
ever needed, finer error handling, and whether the macOS path can be
restored (it needs `cdio_get_device_fd()`, which is not in libcdio 2.1.0 —
verified against the installed headers *and* the `.so` export table).

---

## Open, joint — belongs to the seam, not to one side

### Closing Platterpus's script console mid-rip left a log with no footer — cause not determined

**Observed once, 2026-09-30, on `.18` through Platterpus 0.6.64**
(`docs/rig-2026-09-30-174a134/rips/full-acceptance-angle-bracket.log`). The
operator closed the script console 28.9 s into section F's rip. The log is 54
lines and ends at `Tracks:`: no track block, no completion footer, no `Log
FUN512:`, so `-Y` exits 3. Platterpus's record gives the wrapper's exit code as
1 at 01:32:32Z, the second the console closed, and **no `-j` record was in the
bundle**, which Platterpus collects from the rips root by name
(`platterpus@0981c69:src/platterpus/adapters/cyanrip_backend.py:745-747`). So
when the operator made the tarball, cyanrip had not exited through `atexit`.

**Which signals write the footer, measured 2026-09-30** on a fixture ripping
mid-read, `.19`'s code (Platterpus's round 30 lap 2 S22 asked):

| signal | exit | footer, `Log FUN512:` | `-Y` | `-j` record |
|---|---|---|---|---|
| SIGTERM, SIGINT | 1 | written, names the signal | 0 | written |
| SIGHUP | killed | **none** | 3 | none — **handled from `.20`**, below |
| SIGQUIT, SIGKILL | killed | none | 3 | none |
| SIGPIPE | **not stopped** | none while it runs on | 3 | none |

**SIGPIPE is ignored, and not by us.** libneon, linked through libmusicbrainz5,
calls `signal(SIGPIPE, SIG_IGN)` from `ne_sock_init()` as a library constructor,
before `main()`, under `-N` too (`strace -k`). So a consumer that stops reading
our stdout does not stop the rip: it runs on, holding the drive, and writes its
footer when it ends. That is this environment's libraries; the rig's container
links its own.

**So the closed-console log is one of two things**: a default-disposition death
(SIGHUP, SIGQUIT or SIGKILL), or a cyanrip still running inside the container
when the tarball was made. The rig can say which: if the log in
`~/platterpus-rig/platterpustestsession20260930t013138z/rips/` is now longer
than 54 lines and a `cyanrip-diagnostics-20260930T013204Z.json` sits beside
the album folder, it ran on; if neither, it was killed. What their console's
close sends is theirs to trace (their round 30 lap 2 S21, S23).

**2026-10-04 settles one such log as the second kind** (`docs/rig-2026-10-04-174a134/`).
Section N's `secure-reread.log` has no footer. Its last line is the app log's
line at 01:01:00.985Z. The script was stopped from the console 0.8 s later, and
the bundle was written in the same second. No line in between signals or reaps
the ripper, which was mid-re-read. The operator closed both programs before
sending the bundle, but the copy had already been made. So a bundle can hold a
log that is still being written, and the bundle did not say so. **Our side of
the check exists now**: `tools/ingest-bundle.py` names every cyanrip log that
did not reach a signed footer, and says what that can and cannot mean
(`acfd48b`). **Their side** is to make the bundle say the ripper was still
running, or wait for it.

**The same run's cancel: what the rescue is, corrected 2026-10-05.** This
said the cancel *"sent a second TERM 4.9 s after the first"*, Platterpus's
*post-cancel rescue*, `fuser -k TERM /dev/sr0`, and that a second signal ends
cyanrip with `_exit(1)` and no footer. The second half is true of our handler
(`cyanrip@174a134:src/cyanrip_main.c:1219-1220`). The first is not true on this rig: the
2026-10-05 run's cancel shows the cancel's own TERM stopping at the host
wrapper, the rescue's TERM finding cyanrip still holding the drive, and a
signed footer about 0.3 s later, which a second signal would have prevented
(`docs/rig-2026-10-05-174a134/README.md`). So the rescue's signal is the first
cyanrip receives. On 2026-10-04 it found cyanrip inside a read that had not
returned after 20 s, and that disc's reads took up to 54 s; the cancelled pass's
log was in a temporary directory and is not in the bundle, so whether it was
signed is still not known.

**SIGHUP is handled from `.20`**, like SIGTERM: the footer names it, `-Y`
verifies, and the `--diagnostics` record is written. A SIGHUP that arrives already ignored
stays ignored, so `nohup` still keeps a rip running (measured). `sc_interrupt`
pins it, revert-proved. SIGQUIT keeps its default, quit and dump core, which is
the debugging path it exists for.

### The four shared documents: every known defect, in one table

**Rows 1–7 were fixed in round 25 (2026-09-23)**, by `PROTOCOL.md` v6,
`OWNERSHIP.md` v3 and `seam-rules.md` v6, all byte-identical in both trees. Drafting found an eighth, in `OWNERSHIP.md`'s opening
paragraph: it says every consumer holds its copy at the same path, and
Platterpus's protocol is at `docs/handshake-protocol.md`. `OWNERSHIP-v3.md`
fixes that too. Rows 8–12, `seam-commands.md`, wait for round 26, because the
fix needs `tools/probe-argv-surface.py` to measure what it asserts.
**Row 13 was found on 2026-09-28** by a control in the round-28 close
rehearsal, and **row 14** the same day, filing Platterpus's round 28 lap 9.
Both are for round 29, and both are gaps in the spec, not false statements.
**Rows 15 and 16 are for v8**, from Platterpus's round 30 lap 6 S23 and S24,
read against v7 as proposed at `09f39bc` and still true of it at `2abeb5d`.
**Carried to round 31 by the operator's decision of 2026-10-05**: v7 governs
from round 31, so a v8 drafted in round 30 could govern nothing sooner, and
drafting it would add laps to a round whose close waits on a run.

**Consolidated 2026-09-22 by the pre-round-24 audit**, read against the four
files as they stand — byte-identical in both trees, `tools/seam-sync-check.py
--fetch` exit 0 at `platterpus@52b4428`. None of these breaks a gate. Each is a
statement a reader of the spec is entitled to believe and should not. **None can
be fixed from one side** (`OWNERSHIP.md` §4), so this is the bundle a joint
version bump would carry, and round 24 proposes it rather than editing it.

| # | file | what it says | what is true | detail |
|---|---|---|---|---|
| 1 | `PROTOCOL.md` | nothing on K1, K2 or K3 | all three agreed in round 22, and both sides practise them | `docs/history/KNOWN-ISSUES-2026-10-21.md`, *Three agreed protocol changes* |
| 2 | `PROTOCOL.md` §8, *"Rows added in v3/v4"* | *"These are not yet in force."* | the heading's own condition, *"required once both gates implement 4"*, is met: ours implements 5 (`tools/release-gate.py`, `PROTOCOL_VERSION = 5`), theirs 4 (`platterpus@52b44282:scripts/handshake.py:1093`) | here |
| 3 | `PROTOCOL.md` §8, *"Rows added in v5"* | *"Not yet in force."* | **False since `platterpus@c2f43d28`**, when their gate reached 5. This cell predicted that on the day it was written, and it happened the same evening. It is row 2 again: a spec frozen by version cannot be edited when a present-tense sentence goes stale. The conditional headings are already correct; the fix is to delete both body sentences | here |
| 4a | `PROTOCOL.md` §5b step 1 and row C37 | the candidate lap must be declared in the closing file's own `HANDSHAKE-INBOUND-HELD` | then step 3 and C40, *"the whole of v5's saving"*, cannot fire on a real record, because the saving lap is written after the closing file | the v5 entry below |
| 4 | `PROTOCOL.md` | `HANDSHAKE-FROM-COMMIT` defined once | the two projects read it two ways | round 23 lap 3 §D. v5 §13 says so itself, so this is a known gap rather than a false statement |
| 5 | `OWNERSHIP.md` §3 | *"we cannot run their program, read their source, or reproduce their environment"* | **"read their source" has been false since 2026-09-13.** Both repositories are public, and this environment reads theirs anonymously on every `seam-sync-check --fetch`. The other two clauses were not checked, so this makes no claim about them | `docs/history/CLAUDE-2026-10-21.md`, *"This rule used to carry the clause…"* |
| 6 | `OWNERSHIP.md` §5 | *"we cannot read each other's source"* | same as row 5 | same |
| 7 | `seam-rules.md` S-13 | round 7: *"laps to close: **37 and open**"*, *"releases produced: **0**"* | round 7 closed `GO` at **lap 39** (`round-07-lap-39.md`), and produced one release, `+platterpus.5`, at `release-ledger.tsv` row 11. `CLAUDE.md`'s copy of this table was corrected on 2026-09-16; the shared copy was not | here |
| 8–12 | `seam-commands.md` | five statements | **all fixed in round 30**, two at `83bcd70` and three by the text landed after `0645ddb` | *"`docs/seam-commands.md` carried FIVE known-wrong statements"*, above |
| 13 | `PROTOCOL.md` §5b, rows C39–C40 | step 2 cross-checks the closing file's transcription of the PEER's verdict against the lap its source names | **nothing asks a gate to check the peer's transcription of ITS OWN verdict**, so the two gates can split on one record. Rehearsed 2026-09-28 on copies of our record (control X-c3): our lap 6 `GO`, their lap 7 `GO`, released, at protocol 6, but transcribing our lap 6 as `OPEN`. **Our gate closes the round** on their lap 7 by step 3. **Theirs refuses it**: their closing file is their lap 7, its source names our lap 6, and the values disagree (`platterpus@785925a:scripts/handshake.py:2438-2447`, *"the transcription disagrees with its source"*). Their gate makes them correct their own file, so the split closes itself once they do; until then ours says CLOSED and theirs does not | found by a control in the round-28 close rehearsal, not by a real record. **For round 29, not round 28**: the candidate row is that a gate refuses when the newest peer lap's source names one of the gate's own laps and its `HANDSHAKE-PEER-VERDICT` disagrees with that lap's `HANDSHAKE-VERDICT` |
| 14 | `PROTOCOL.md` §5, `HANDSHAKE-OUR-VERSION` / `HANDSHAKE-PEER-VERSION` | *"which two programs agreed"* | **the two closing files of round 28 name different Platterpus builds as the party.** Our lap 8 names the build that was tested, `platterpus 0.6.61` at `59f4c00`. Their lap 9 names its own current release, `platterpus 0.6.62` at `9e96fa0` (their `v0.6.62` tag), while its `HANDSHAKE-APP-VERSION` and `HANDSHAKE-TESTED` say 0.6.61. Both are defensible readings. Neither gate cross-checks the two files, so one closed round quotes two different agreements | found 2026-09-28 filing their round 28 lap 9. For round 29: say whether the field names the build under test or the build declaring the verdict |
| 15 | `PROTOCOL.md` v7 and `seam-rules.md` v7 | nine wording items | each is a sentence v7 leaves imprecise, none a false rule: `HANDSHAKE-NEXT-LAP` with two grammars (§3, C46); R9 keeping the sentence §15 calls misleading; R8 point 2's unscoped *"the consumer follows a build on beta"*; §6d asking for the pair newest at the run's end where D3 checks only its start; a mid-round hotfix reading as a pin move against R4; §15 saying one v6 item was withdrawn; §6c's *"opens with"* and undefined `<owner>`; and five smaller | Platterpus's round 30 lap 6 S23, which gives each with its v7 line numbers at `09f39bc` |
| 16 | `PROTOCOL.md` v7 R8 point 2 | the provider's release goes to stable *"once the round its run opens accepts it"* | both sides read *"accepts"* as *"closes `GO`"*, which is how a run graded `partial`, as `.19`'s was, still reaches stable | Platterpus's lap 6 S24 and our lap 7. The reading is agreed; the word is for v8 |

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
  the naming scheme (`cyanrip_log.c:847`) and consults nothing about what was
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

The Python copy of the algorithm is pinned by one synthetic vector, non-zero
including the edges, under three first/last settings in `audio-checksums.py
self-test`; the C is compared with it by the `audio_checksums` image
scenario. **Platterpus has none to cover**: it
computes no AccurateRip checksum and reads ours from the log (their round 28
lap 6 S7). Checked at `platterpus@808f8fb1` on 2026-10-12: nothing under their
`src/` computes one, and `ctdb/crc.py` is the CTDB CRC with CTDB's own trims.
So round 8 `J13` is answered, and this stays a note about the disc, not an open
question about them.

---

## Known external bugs worked around here

Moved here from `CLAUDE.md` on 2026-10-21, word for word below this
paragraph, when that file was cut to its cap. These are defects in what we
link or run, not in our code; `tools/gen-dependency-map.py` reads each
bullet's bold lead into `docs/DEPENDENCIES.md` and `sbom.cdx.json`.

Record these rather than rediscovering them:

- **libcdio CDRDAO driver, relative `FILE` paths.** `lib/driver/image/cdrdao.c`
  computes the absolute path of a `.toc`'s `FILE` and then opens the *raw
  relative* one (`cdio_stdio_new(psz_field)` where it should pass
  `psz_filename`; `bincue.c` gets this right). A `.toc` therefore only loads
  when the process's working directory is the image's directory —
  `tests/rip_images.py` sets `cwd=` for exactly this.
- **libcdio-paranoia sniffs sample data to guess byte order.** `data_bigendianp()`
  votes on which interpretation looks more like audio. Real music votes
  correctly; a synthetic full-scale square wave is *smoother* byte-swapped, so
  it silently rips byte-reversed. Any synthetic test signal must be checked
  against its source bytes before conclusions are drawn from it.
- **Paranoia's cache model doubles as its read chunk size.** Setting it small
  enough to stop the backseek probe over-reading the leadout leaves the
  verification logic no overlap and it emits zeroes. On disc images the safe
  window measured 5-256 sectors; upstream ships 1. See the table in
  `cyanrip_main.c`.
- **`cdio_get_device_fd()` is not in libcdio 2.1.0.** Verified against the
  installed headers *and* the `.so` export table. Upstream PR #153's macOS
  sub-channel path calls it, which is why that PR's restructure is not carried
  and `pregap.c` keeps its copy-pasted-struct workaround.
- **libcdio does not distinguish "no CD-TEXT on disc" from "driver cannot read
  CD-TEXT".** `cdio_get_cdtext()` returns the same `NULL` for both. Report what
  was observed ("none reported by libcdio"), never the stronger claim.
- **EAC's `Pre-gap length` field is hundredths of a second, not CD frames.**
  Settled from a genuine EAC 1.8 log of the rig disc, which Platterpus opened
  and we cannot (round 7 lap 11 §B). Our `Pregap length: N frames` states its
  unit and is unaffected, but the two logs differ by design on every non-zero
  pregap and **that is not a defect in either**. The reasoning that made it look
  like one was sound and wrong: `0:00:01.96` cannot be a frame count, so we
  correctly inferred the field was not frames — and then had no artifact to say
  which of us matched EAC. Do not re-litigate this without opening an EAC log.
- **libcdio terminates the process from inside a library call.** Its default
  log handler `exit(EXIT_FAILURE)`s on `CDIO_LOG_ERROR` and `abort()`s on
  `CDIO_LOG_ASSERT`, printing straight to stderr. So `-d` on an unparseable CUE
  was a non-zero exit that cyanrip never saw and could not report the code of
  -- measured, not assumed: that run's diagnostics record read `exit_code:
  null`. `crip_cdio_log_handler()` now routes the message through ours first.
  **It must keep terminating**: libcdio's internal callers are written assuming
  `cdio_error()` does not return, so code after such a call runs in a state its
  author never intended it to reach.
- **libcdio-paranoia checks the per-frame retry limit only at multiples of 5.**
  `cdio_paranoia_read_limited()` tests `retry_count == max_retries` inside
  `if (retry_count % 5 == 0)` (`lib/paranoia/paranoia.c`, read at upstream
  `384f4da`). Any other limit is never matched, and on a sector that will not
  read the call does not return. Measured with one injected bad sector at the
  default level: `-r 3` hung past 90 s, and `-r 10` finished in a second.
  `crip_frame_retry_limit()` rounds up (minimum 5) and the `Retry limit:` line
  says both numbers when they differ. **The whole-track `-Z` ceiling is ours
  and keeps the value as given.**
- **And with paranoia disabled (`-P 0`), an unreadable sector never returned
  at any retry limit.** In disable mode every block read starts with
  `paranoia_resetall()`, so a block in which nothing reads leaves the root
  empty, and the skip then writes its zero frame at word 0 instead of at the
  cursor; the next read resets the root again. Measured at `-r 10` and `-r 1`,
  and traced 2026-10-05. **Worked around for `.20`** without leaving paranoia's
  read path: at level 0 the cdda layer's public `read_audio` hook is wrapped
  (`crip_read_audio_salvaging()`), so a short request is completed one sector
  at a time and only an unreadable sector is zeroed. Reads that succeed are
  untouched, so the counters and the golden reference do not move. Bypassing
  paranoia at level 0 was rejected, because every image scenario runs at
  `-P 0` and the counters it would have emptied are the ones the suite checks.
  Platterpus never passes `-P`. Recorded in `docs/KNOWN-ISSUES.md`.
- **genopt prints its own errors unless you take them.** `GEN_OPT_LOG` is
  documented in `genopt.h` and cyanrip did not define it, so every
  argument-parsing failure went to stdout via `vprintf` and reached no logfile
  and no record. That includes the exact message that once read to a consumer
  as "cyanrip is not installed".
