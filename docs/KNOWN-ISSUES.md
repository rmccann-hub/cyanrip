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

**What would settle it:** one rig run on the new line. If it prints an uncached
read in the hundreds of milliseconds beside a cached read of a few, the
diagnosis is confirmed from the artifact and the fix is arithmetic. That is the
whole reason the evidence clause was added first.

### The provider contract cannot see composed log lines

`PROVIDER-CONTRACT.md` records `Cache probe:    %s` and **none of the nine
wordings that actually reach the log.** The document exists so the contract
"cannot describe behaviour we do not have", and on this line it describes
nothing at all — a consumer reading it learns a `%s`.

The machinery exists: `gen-provider-contract.py` already rebuilds one composed
line from the `snprintf` calls that fill its buffer. It is not applied here.

**Not urgent** — the nine wordings are pinned by `tests/cacheprobe.c`, so they
cannot drift silently; they are simply absent from the document Platterpus
reads. **What would settle it:** extend the composer to `cache_probe.c`, bounded
to that function's own buffer — the existing one was first written against a
different buffer of the same name in another function and would have published
an invented shape.

### `docs/seam-commands.md` §7 overclaims

It states *"Every value either took effect or was refused with a message"* when
**49 of 111 rows** were graded from exit status alone. **Do not cite that
sentence.**

**Not fixed because the file is shared** and neither project owns it. A
one-sided edit is how two copies of one spec come to disagree, which has already
happened once to `PROTOCOL.md`. It goes in at the next joint version bump.

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
