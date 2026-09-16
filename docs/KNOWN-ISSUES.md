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

### `Lap commit list names its range` timed out once, and the cause is NOT established

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
| 1 | §7: *"Every value either took effect or was refused with a message"* | **49 of 111 rows** were graded from exit status alone | ours |
| 2 | line 504: `-p '99=drop'` accepted, exit 0 | the binary **refuses** it | theirs, lap 16 §B3 |
| 3 | line 97: `-D` is `directory` / `str, path` / `writable` / *"output directory"* | it is `folder_scheme`, *"Directory naming scheme"* (`cyanrip_main.c:1603` at the pin) — a **relative** scheme, with `-F` its per-track sibling | theirs, lap 16 §B3 |

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

### A superseded track has no recorded read time anywhere

Our album log gives each track a `creation_time` describing the **first pass**.
Platterpus's addendum supersedes that track and carries **no timestamp at all**.
So for any re-read track, the only time on record belongs to audio that is no
longer on disk.

The datum is not missing, only uncarried — their re-read is a cyanrip invocation
and writes its own `creation_time`. Asked as round 8 `J14`. **Unrecoverable
after the fact**, which is why it is asked at all: a read time is not derivable
a month later from anything on disk.

### `Ripping errors:` is written before the encoders are asked how they did

**Found 2026-09-15, provoked by Platterpus reporting the same shape in their
own code, and demonstrated rather than argued** —
`tests/rip_images.py sc_encode_failure_is_absent_from_the_log()`.

Cap every write at 32 KiB and rip `mixed.cue`. The muxer's trailer write fails.
**The failure is caught**: `cyanrip_end_track_encoding()` returns the encoder
thread's status, the collection loop in `cyanrip_main.c` counts it,
`ripping_errors` in `-j` reads **2**, and the process exits **1**. But the log
says:

```
Track 2 ripped and encoded successfully!
  File(s):
    …/2.flac                    <- 32768 bytes; the intact file is 253742
Ripping errors: 0
Rip completed:  yes (2 of 3 tracks)
Log FUN512: …                   <- and `-Y` exits 0 on it
```

**The diagnosable lines ARE in the logfile, six lines above that zero** —
`Error writing trailer: File too large!` and `Error writing packet: File too
large!` at lines 204 and 205, `Ripping errors: 0` at line 211, both at column 0
— so the rule that every failure prints a diagnosable line held. What failed is that **no field reflects them**, and a
parser grades fields, which is the whole reason the log is a contract.

**Two records of one run, disagreeing, and the human-readable one is wrong.**
That is the changelog-versus-ledger shape the operator caught on 2026-09-13,
one document over: three machine-read artifacts said `.12` and the human-read
one said `.11`.

**The mechanism is a deliberate choice whose consequence was not written
down.** `cyanrip_log_finish_report()` is called *before* the encoder-status
loop, and the comment at `cyanrip_main.c:2686` says why in as many words:
*"so that `Ripping errors:` counts exactly what it counted before — moving it
below would silently fold encoder failures into a contract line."* That
reasoning is right. What it did not say is that the log then makes a claim the
same program contradicts in the next file it writes.

**`File(s):` is the other half.** It is built from `ctx->settings.outputs` and
the naming scheme (`cyanrip_log.c:642`) and consults nothing about what was
written, so it names a path whatever happened to it. **A completeness field
computed from the REQUEST, read as the OUTCOME** — Platterpus's phrase for
their own defect, and ours fits it exactly.

**The fix is one line and is deliberately not made here.** Moving the footer
below the loop makes the two agree — measured: the scenario then reports
*"the log and -j now AGREE (2)"*. It also changes what a P2 contract line
counts, which is precisely the drive-by reword the seam forbids. It is a
handshake proposal; round 20 §5.4 carries it.

**Not promoted to blocking, and the reasoning is R3's.** It does not make
`fe4d2c4` unsafe for the consumer we have: Platterpus captures the exit code
(their own `DIAGNOSTICS.txt` shows `cyanrip exited 1` recorded from a different
failure), and `-j` is correct. It is unsafe for a **log-only** consumer — and
the log is the archival record, which is the one that outlives the exit code.
That is an argument for fixing it, not on its own for holding a release.

**RLIMIT_FSIZE stands in for ENOSPC**, which is the realistic case: both reach
the muxer as a write error rather than as a signal. With SIGXFSZ *not* ignored
the kernel kills the process outright — exit 153, no footer at all — which is a
different and safer failure.

### `Frame retries:` names half of what `-r` does

Found 2026-09-15 by reading `docs/rig-2026-09-15-fe4d2c4/rips/secure-reread.log`
whole: line 18 says `Frame retries:  3`, line 425 says
`Secure re-read:  did NOT converge after 3 reads (repeat limit hit)`, and
**both threes are the same knob**, which nothing in the log says.

`-r` is *"Maximum number of retries for frames and repeated rips"*. It is passed
to `cdio_paranoia_read_limited()` (`src/cyanrip_main.c:534`) **and** used as the
repeat-loop ceiling (`src/cyanrip_main.c:1011`). So on that rip it governed
paranoia's per-frame retries *and* decided that track 5 stopped after three
whole-track reads.

**The generated contract is right and the log line is what under-states.**
`PROVIDER-CONTRACT.md` P1 carries genopt's own text — *"for frames and repeated
rips"* — because P1 is derived from `--help`. P2's `Frame retries:` label is
hand-shaped and names one of the two. `-j`'s `"frame_retries"` field
(`src/diagnostics.c:458`) has the same name and the same gap.

This is `Cache defeat:` → `Cache model:` again, and `Peak level:` →
`Sample peak level:` again: **a label asserts, and a name that does not
discriminate becomes ambiguous the moment a sibling appears.** The sibling here
is `Secure re-read:`, which did not exist when the label was written.

**Deliberately not reworded.** `Frame retries:` is a stable log line, so a
silent rename is exactly the drive-by reword the seam forbids; and the JSON
field is a schema key a consumer may already read. It is a rename to propose,
not to ship — carried into round 20. Until then the line is not wrong, only
narrower than the number it prints.

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
