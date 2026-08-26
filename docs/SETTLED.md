# Settled — read this before deriving anything

**Why it exists.** Facts established in this project lived only in the prose of
whichever handshake lap or commit message established them. Fifteen lap files is
not an index, so the cheap move was always to re-derive — and a re-derivation can
come out wrong. That is how a hedge written into round 14 lap 11 §J7 became an
unhedged claim to the operator within the hour, and how the same three facts were
re-checked four times in one session.

**How to use it.** Look here first. If a fact is here, cite it and move on. Only
derive something that is not here, and add a line when it settles.

**Rewritten in place, never appended to.** It is a claim about *now*, the same
rule as `docs/handshake/STATUS.md`. It is **not** a record — the laps and the
commits are the record, and consolidation applies to documentation and never to
evidence.

**Every row carries a `check`**, so this file cannot rot quietly. Run them all:

    python3 tools/check-settled.py

**A row with no command must say WHY it has none**, because three very
different confidences were looking identical:

| tag | means | how much to trust it |
|---|---|---|
| `— past:` | a measurement taken once, on hardware or in a session that is gone | the artifact is cited; it cannot be re-run, only re-read |
| `— theirs:` | a fact about a machine or repository we cannot reach | **only as good as the lap that told us**, and laps get corrected |
| `— structural:` | true of our own code but **not observable from any fixture here** | read from source; a reader could check it, no command can |

**This distinction is the same `none` versus `unknown (reason)` rule this project
applies to every log line, turned on its own index.** A bare em dash said "not
checked" and hid whether that was *cannot*, *has not*, or *nobody can*.

---

## The pin and the release

| fact | check |
|---|---|
| Round 14's pin is `d9c058c` = `0.9.4-rc2+platterpus.10`, seq 20, channel `beta` | `grep -m1 HANDSHAKE-PIN: docs/handshake/round-14-lap-15.md` |
| `stable` is `237a4ff` = `+platterpus.7`, seq 17, authorised by round 12 | `python3 tools/gen-release-manifest.py --check release-manifest.json` |
| Nothing in `src/` changed between `+platterpus.8` and `+platterpus.10` | `git diff --stat 796df32 d9c058c -- src/` |
| Tag pushes and branch **deletes** are `HTTP 403` from this proxy; branch create/update works | — past: probed with a throwaway tag, `docs/handshake/README.md`. **Deliberately no test** — a check that reaches the network is not evidence about this program |

## Our own binary

| fact | check |
|---|---|
| `-Y` / `--verify-log` is in P1, generated from the binary's `--help`, so it cannot lapse for a new pin | `grep -n 'verify-log' PROVIDER-CONTRACT.md` |
| `signal()` appears at exactly **one** site in all of `src/`, installing `on_quit_signal` for `SIGINT` and `SIGTERM`; nothing restores either disposition | `grep -c '[^_a-z]signal(' src/cyanrip_main.c` |
| **A single SIGTERM cannot terminate cyanrip** since `+platterpus.7`: the handler sets a flag and returns, and nothing reads it once the rip loop is past | — structural: `src/cyanrip_main.c:1155`. The mid-rip half IS covered by `sc_interrupt`, which signals a live rip and asserts a graceful exit; **the half after the rip loop is a millisecond-wide window on an image**, so a timing test would be flaky and a flaky test is worse than none |
| `crip_diag_record()` has **one** call site, at the top of `cyanrip_vlog()`, which ends `vprintf` + `fflush(stdout)` unconditionally — so a message in the `-j` array **is** proof it reached fd 1 and was flushed | `grep -rc 'crip_diag_record(' src/cyanrip_log.c` |
| The `-j` record is written from `atexit`, so a run that produced one reached `exit()` | `grep -n 'atexit(crip_diag_write)' src/diagnostics.c` |
| `PROBE_MAX_SECTORS` is **2048** — a ceiling of ours, not a drive limit | `grep -n 'PROBE_MAX_SECTORS' src/cache_probe.c` |
| `print_cache_model()`'s drive branch is unreachable from every fixture: all three image drivers take the image arm | `grep -n 'DRIVER_BINCUE' src/cyanrip_log.c` |

## Hardware — what has and has not run

| fact | check |
|---|---|
| **`-x -I` completed on a drive**, 2026-08-25, PIONEER BD-RW BDR-209D: exit 0, 15.9 s, drive returned, `at least 2048 sectors … search ceiling reached` | — past: `docs/handshake/inbound/artifacts/round-14-acceptance-20260825/transcript.txt` |
| **`-x` alone has never been shown to return a drive.** Different claim, same flag | — structural: an absence, and a different claim from the row above |
| **C1 is `-j`-associated, cause NOT determined.** The controlled pair, same drive/disc/day: `-N -l 1` = 4.9 s exit 1; `-j -D -o -u …` = 1800 s and SIGKILL. Narrowed to which flag, not to where | — theirs: their lap 16 §D, with our transcript §P2 as the other half of the pair |
| `Pregap source: sub-channel (not signalled by TOC)` on 13 of 14 tracks, track 1 `lead-in`, LSN arithmetic consistent, on `d9c058c` | — past: same transcript, §P |
| **T1 IS DONE.** Secure re-read on hardware, 2026-08-26, build `d9c058c`, 14-track disc: `-Z 2 -r 3` gave `Secure re-read:  converged after 3 reads` on all 14 tracks | `grep -c "converged after 3 reads" docs/rig-2026-08-26-d9c058c/rips/secure-reread.log` (14) |
| **A non-zero `Read stalls:` is no longer hypothetical**, and its populated singular rendering matches the format string and `tests/stall.c:370` | `grep -c "1 read exceeded 10s; longest 11s (track 3, LSN 37086)" docs/rig-2026-08-26-d9c058c/rips/cancel-me.log` |
| The `Cache model:` **sector** arm has now been seen on a real drive: `1200 sectors (drive cache size not probed)`. Every image fixture takes the image arm and the golden reference runs `-P 0`, so no committed artifact had shown it | `grep -c "Cache model:    1200 sectors (drive cache size not probed)" docs/rig-2026-08-26-d9c058c/rips/secure-reread.log` |
| **`-Y` verifies a log written by a DIFFERENT build.** All six 2026-08-26 logs, written by `d9c058c`, verify exit 0 against a later binary | `for f in docs/rig-2026-08-26-d9c058c/rips/*.log; do ./build/src/cyanrip -Y "$f" >/dev/null 2>&1 \|\| exit 1; done` |
| The corrected paranoia claim, re-checked on that disc: three reads a track put `READ` at ratio **3.02**, and **`FIXUP_EDGE` summed to 0 per-track against a disc total of 2** — the sharpest case there has been of why the per-track blocks must not be summed | — past: the table in `docs/rig-2026-08-26-d9c058c/README.md`, recomputable from `rips/secure-reread.log` |
| **The 2026-08-26 `cancel me` / `after cancel` rips do NOT show a cancel.** Both were invoked with a narrowed `Tracks to rip:` and both footers read `Rip completed:  yes`. A folder name is not evidence | `grep -h "^Rip completed:" docs/rig-2026-08-26-d9c058c/rips/cancel-me.log docs/rig-2026-08-26-d9c058c/rips/after-cancel.log` |
| **Never run anywhere:** C2 reporting (drive says unsupported), `-f`, damaged media, CD-TEXT from a physical disc, the diagnosed-abort exit code, the interrupt/abort footers, `-x` alone on a drive that goes on to rip | — structural: an absence. No fixture can produce any of these, which is the claim |
| **`cyanrip --version` hung twice on the rig through `~/.local/bin/cyanrip`** (0-byte P3 artifact; `timeout -k 10 60` → exit 137) while Platterpus got the banner from the same path 3 s earlier in under a third of a second. **NOT reproduced here and NOT attributed:** interleaved on this tree, `--version` / `-v` / `-V` are indistinguishable at 0.034–0.042 s | `for f in --version -v -V; do ./build/src/cyanrip $f >/dev/null </dev/null; done` (all return at once) |

## Things that are true and read as false

| fact | check |
|---|---|
| **Per-track paranoia counters do NOT sum to the disc totals under `-Z`.** The per-track baseline is snapshotted after `repeat_ripping:`, so it describes the **last pass**; the disc counters sum **every** pass. Equality holds only when each track was read once | — past: round 13, measured 15+10+5=30 against a disc total of 90 |
| `Cache model:` reports what paranoia **models**, never what the drive has. Since 2026-08-26 it says `(drive cache probed separately…)` when `-x` ran | `./build/tests/diag_test` |
| `none` and `unknown (reason)` are different claims everywhere in the log, on purpose | — structural: a policy over every log line, not a single assertion |
| **`ddf7ac3` is a cyanrip commit** (`0.9.4-rc1+platterpus.5`), not a Platterpus one, despite standing in `HANDSHAKE-PEER-PIN` through two closed rounds | `git log --oneline -1 ddf7ac3` |

## Upstream `cyanreg/cyanrip` — what it still lacks, for merge-back

Checked against `master` at `f8ebf48`, not recalled. **`-Y` was on this list from
memory and is wrong: upstream has it.** That is the whole reason the list is
checked rather than written.

| fact | check |
|---|---|
| Upstream still calls `cyanrip_log()` **inside the signal handler** — a mutex and stdio in a handler, the deadlock that hangs the process with the drive held | `git show master:src/cyanrip_main.c \| grep -A3 'on_quit_signal(int'` |
| Upstream handles **no SIGTERM at all** — 0 occurrences | `test $(git show master:src/cyanrip_main.c \| grep -c SIGTERM) -eq 0` |
| Upstream has `cyanrip_log_finish_report()` immediately **above** `end:`, so every `goto end` skips the completion footer | `git show master:src/cyanrip_main.c \| grep -n -B1 '^end:' \| tail -3` |
| **`-Y` / `--verify-log` is already upstream** — not ours to contribute | `test $(git show master:src/cyanrip_main.c \| grep -c verify_log) -gt 0` |

## Platterpus's side — held because they told us, not because we checked

| fact | check |
|---|---|
| `~/.local/bin/cyanrip` on the rig is a **host-exported Distrobox wrapper**; the real ripper runs in a container. **ARCHITECTURE YES, CAUSE NO** — their lap 16 §D1(a) withdraws it as the explanation for the empty capture, because a later run's capture was 111 bytes and a theory predicting *always empty* does not predict *sometimes empty* | — theirs: their lap 12 §E2, corrected by their lap 16 §D1(a) |
| Their `cyanrip` script verb is bounded: 300 s, then a kill, then 20 s, then an unreapable-child record with a **null** exit code | — theirs: their lap 12 §A |
| `0.6.26` was **not published** until 2026-08-25; the operator was on `0.6.25 (5f374aa)` before that | — theirs: their lap 13 §A2 |
| Their gate had the same `HANDSHAKE-TEST-PIN: none.` misreading as ours, fixed the same way | — theirs: their lap 12 §D |
