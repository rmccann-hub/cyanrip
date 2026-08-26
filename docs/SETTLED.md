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

A row with `check: —` is a fact about somebody else's machine or a past event
that no command here can re-run. Those are the rows to distrust first.

---

## The pin and the release

| fact | check |
|---|---|
| Round 14's pin is `d9c058c` = `0.9.4-rc2+platterpus.10`, seq 20, channel `beta` | `grep -m1 HANDSHAKE-PIN: docs/handshake/round-14-lap-15.md` |
| `stable` is `237a4ff` = `+platterpus.7`, seq 17, authorised by round 12 | `python3 tools/gen-release-manifest.py --check release-manifest.json` |
| Nothing in `src/` changed between `+platterpus.8` and `+platterpus.10` | `git diff --stat 796df32 d9c058c -- src/` |
| Tag pushes and branch **deletes** are `HTTP 403` from this proxy; branch create/update works | — measured, `docs/handshake/README.md` |

## Our own binary

| fact | check |
|---|---|
| `-Y` / `--verify-log` is in P1, generated from the binary's `--help`, so it cannot lapse for a new pin | `grep -n 'verify-log' PROVIDER-CONTRACT.md` |
| `signal()` appears at exactly **one** site in all of `src/`, installing `on_quit_signal` for `SIGINT` and `SIGTERM`; nothing restores either disposition | `grep -c '[^_a-z]signal(' src/cyanrip_main.c` |
| **A single SIGTERM cannot terminate cyanrip** since `+platterpus.7`: the handler sets a flag and returns, and nothing reads it once the rip loop is past | — read from `src/cyanrip_main.c:1155` |
| `crip_diag_record()` has **one** call site, at the top of `cyanrip_vlog()`, which ends `vprintf` + `fflush(stdout)` unconditionally — so a message in the `-j` array **is** proof it reached fd 1 and was flushed | `grep -rc 'crip_diag_record(' src/cyanrip_log.c` |
| The `-j` record is written from `atexit`, so a run that produced one reached `exit()` | `grep -n 'atexit(crip_diag_write)' src/diagnostics.c` |
| `PROBE_MAX_SECTORS` is **2048** — a ceiling of ours, not a drive limit | `grep -n 'PROBE_MAX_SECTORS' src/cache_probe.c` |
| `print_cache_model()`'s drive branch is unreachable from every fixture: all three image drivers take the image arm | `grep -n 'DRIVER_BINCUE' src/cyanrip_log.c` |

## Hardware — what has and has not run

| fact | check |
|---|---|
| **`-x -I` completed on a drive**, 2026-08-25, PIONEER BD-RW BDR-209D: exit 0, 15.9 s, drive returned, `at least 2048 sectors … search ceiling reached` | — `docs/handshake/inbound/artifacts/round-14-acceptance-20260825/transcript.txt` |
| **`-x` alone has never been shown to return a drive.** Different claim, same flag | — |
| **C1 did not reproduce**: `cyanrip -N -l 1` took 4.9 s and exited 1 on the drive that once hung 30 min. The invocations differ by `-j`; cause NOT determined | — same transcript, §P2 |
| `Pregap source: sub-channel (not signalled by TOC)` on 13 of 14 tracks, track 1 `lead-in`, LSN arithmetic consistent, on `d9c058c` | — same transcript, §P |
| **Never run anywhere:** C2 reporting (drive says unsupported), `-f`, damaged media, CD-TEXT from a physical disc, the diagnosed-abort exit code, a non-zero `Read stalls:` count, T1's uniform secure re-read on hardware | — |

## Things that are true and read as false

| fact | check |
|---|---|
| **Per-track paranoia counters do NOT sum to the disc totals under `-Z`.** The per-track baseline is snapshotted after `repeat_ripping:`, so it describes the **last pass**; the disc counters sum **every** pass. Equality holds only when each track was read once | — round 13; measured 15+10+5=30 against 90 |
| `Cache model:` reports what paranoia **models**, never what the drive has. Since 2026-08-26 it says `(drive cache probed separately…)` when `-x` ran | `./build/tests/diag_test` |
| `none` and `unknown (reason)` are different claims everywhere in the log, on purpose | — |
| **`ddf7ac3` is a cyanrip commit** (`0.9.4-rc1+platterpus.5`), not a Platterpus one, despite standing in `HANDSHAKE-PEER-PIN` through two closed rounds | `git log --oneline -1 ddf7ac3` |

## Platterpus's side — held because they told us, not because we checked

| fact | check |
|---|---|
| `~/.local/bin/cyanrip` on the rig is a **host-exported Distrobox wrapper**; the real ripper runs in a container, so a command whose argv names `cyanrip` can hang without cyanrip starting | — their lap 12 §E2 |
| Their `cyanrip` script verb is bounded: 300 s, then a kill, then 20 s, then an unreapable-child record with a **null** exit code | — their lap 12 §A |
| `0.6.26` was **not published** until 2026-08-25; the operator was on `0.6.25 (5f374aa)` before that | — their lap 13 §A2 |
| Their gate had the same `HANDSHAKE-TEST-PIN: none.` misreading as ours, fixed the same way | — their lap 12 §D |
