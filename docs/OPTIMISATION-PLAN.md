# Optimisation plan — test suite, CI, and the documents every session loads

*Written 2026-09-26 at the operator's request: "shorten CI times and everything
else … if a refactor is needed we need to plan". **A plan, not a build.** §2 is
done; §3 needs a decision per item before any of it is built.*

**The rule that bounds all of it: nothing here may remove a check or weaken what
one asserts.** A faster suite that checks less is not an optimisation. Every
change is measured before and after, and a change to a checker carries the same
revert-proof a behavioural fix does.

## 1. Where the time goes, measured

**The local suite at `eb9bc06`** (4 CPUs, 90 tests): **404 s wall**, 542 s
summed over tests. From `build/meson-logs/testlog.txt`:

| test | seconds | why |
|---|---|---|
| Black-box sweep | **308** | 838 invocations, one at a time, and `is_parallel: false`, so nothing else runs beside it. It ran from 82 s to 390 s, and 54 tests waited for it |
| Settled facts | 76 | 64 s of it were two rows re-running whole tests the suite also runs (fixed, §2) |
| Release gate | 34 | 30 s of it were one test re-parsing every lap file per digest (fixed, §2) |
| Sanitizer sweep | 29 | re-runs 57 image scenarios against an instrumented build |
| Argv surface probe | 27 | 116 invocations, one at a time |
| everything else, 85 tests | 68 | none over 5.4 s |

So the wall time is the black-box sweep plus about 95 s. **Nothing but §3.A
moves it below five minutes.**

**GitHub Actions has never run.** `.github/workflows/main.yml` is active, and
the API lists **zero runs, ever**, on any branch. The likeliest cause is that
Actions is not enabled for this fork, which is the repository owner's setting.
So every "CI" result any lap has cited is the local suite. If Actions were
enabled as configured, each push would run the full suite **four times** on
Linux (default, released, sanitizers, released+sanitizers), plus macOS and a
MinGW build.

**The documents.** `CLAUDE.md` is 2,296 lines and 144 KB, loaded into every
session before any work. `docs/KNOWN-ISSUES.md` is 108 KB and `docs/SETTLED.md`
75 KB.

## 2. Done, with no behaviour change

| change | before | after | how it was shown unchanged |
|---|---|---|---|
| `is_a_lap()` memoised on the text (`f482a91`) | Release gate 38.3 s | **8.0 s** | every round's digest, `--check` and `--list`, rounds 7–27, byte-identical before and after |
| Settled-facts rows whose check is a meson test are delegated inside meson (`9465782`) | 78 s | **14.6 s** | standalone, nothing is delegated; with the target test renamed, its row runs again |

The suite's new wall time is measured in §4.

## 3. Planned, each needing a decision

### A. The black-box sweep — the only item that moves wall time a lot

| option | saves | cost |
|---|---|---|
| **A1. Let it run beside the other tests** (drop `is_parallel: false`) | about 290 s of wall | its outside-root check needs a quiet machine (`machine_is_quiet()`) and says `UNPROBED` when it is not. Since writes outside are now attributed **by name**, the quiet precondition may no longer be needed; deciding that is a design question about a containment check, so it is not changed here |
| **A2. Run its 838 invocations on a worker pool** | about 220 s at 4 workers (308 s → ~90 s) | a refactor of `invoke()`: concurrent invocations must not be able to claim each other's outside writes, so each needs a token no other invocation uses. Moderate |
| **A3. Move it to a `slow` meson suite**, run before push and release, not on every iteration | all of it, on iteration | loses per-iteration coverage; the rule that the full suite is green before a push still has to hold |

**Recommendation: A2**, then A1 once the parallel version has run clean for a
round. A3 is the fallback if A2 turns out harder than it looks.

### B. The argv surface probe (27 s)

Its 116 invocations are independent, so a worker pool at 4 workers should cut it to about 8 s. Needs a
check that no two invocations share an output path. **Low risk.**

### C. The sanitizer sweep (29 s)

Locally it is our only sanitizer coverage, so it stays. In a sanitized build,
which two of CI's four rows are, it repeats what the whole instrumented suite
already does. **Skip it when the binary under test is itself instrumented** (it
already asks `nm`), saying so. Saves nothing locally; saves one sweep per
sanitized CI row.

### D. GitHub CI — first decide whether it runs at all

1. **Enable Actions on the fork, or say we do not use it.** A workflow that never
   runs is worse than none, because it reads as CI.
2. If enabled:
   - cache apt packages and the build with ccache;
   - run the heavy tests (black-box, sanitizer sweep, argv probe) in **one** row,
     not all four;
   - drop the MinGW job's nightly-upload steps, which are upstream's and publish
     to GitHub releases; this fork has none (the API lists zero).

### E. The two flakes, because each one costs a full re-run

- **`Lap commit list names its range`**: twelve recorded timeouts, always its
  call #4, which takes about 1 s alone and over 27 s under load. The test's own
  git fixture is not the cause: it uses a throwaway repository. **Next step:
  time each git call under load.** If that finds nothing, raise its timeout to
  120 s like its neighbours, and record that it is slow rather than hung.
- **`Interrupted sample freshness`**: three misses, each a SIGTERM landing
  between `-Z` passes. **Make the probe deterministic**, for example by holding
  a read in flight with `tests/badsector.c`'s shim rather than racing it.

### F. "Everything else": what every session reads

`CLAUDE.md` holds rules and, far more, the history of how each rule was learned.
The history is valuable and already has homes: `docs/SETTLED.md`,
`docs/KNOWN-ISSUES.md` and the laps. **Proposed: keep each rule and its one-line
reason in `CLAUDE.md`, and move the narratives to those homes, linked.** A
target of under 600 lines. This is a documentation refactor of the file that
governs this project, so it needs the operator's agreement on the target and a
review of the result before it lands. `CLAUDE.md` is ours alone; the four shared
seam documents are not touched.

## 4. What to measure after each step

After every item: the full suite's wall time from a removed log, with exactly one
run header, and the per-test durations, compared with §1. An item that does not
move its number is reverted.
