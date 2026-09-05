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
| **The gate cross-checks our transcription against the peer's actual lap.** Declaring `HANDSHAKE-PEER-VERDICT: GO` in our own lap does NOT close a round: it refuses with *"the newest peer lap we hold declares OPEN"* until a filed inbound lap itself declares `GO`. "They did not object" cannot become "they agreed" | — past: dry run on a throwaway clone, 2026-09-04. **Not checkable from this tree**: the message only appears when our lap transcribes `GO` while the newest peer lap does not, and our lap 10 transcribes `OPEN`. Reaching it needs a state the record does not contain, so a check here would test nothing |
| **The release path is dry-run and works end to end.** With a simulated inbound `GO` filed: gate closes round 15, `gen-release-manifest.py` emits seq 22 `0.9.4-rc2+platterpus.12`, both channels resolving, `round_closed=true`. It also refuses a ledger row whose commit is not a sha | — past: dry run on a throwaway clone, 2026-09-04; the real tree was untouched and verified clean afterwards |
| Round 14's pin is `d9c058c` = `0.9.4-rc2+platterpus.10`, seq 20, channel `beta` | `grep -m1 HANDSHAKE-PIN: docs/handshake/round-14-lap-15.md` |
| **`stable` is `978f9b0` = `0.9.4-rc2+platterpus.11`, seq 21**, authorised by round 14 closing `GO`/`GO`. The version string carries upstream's `-rc2` and is stable anyway — order by `release_seq`, read `channel`, never parse the version | `python3 tools/gen-release-manifest.py --check release-manifest.json` |
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
| **Never run anywhere:** C2 reporting (drive says unsupported), `-f`, damaged media, CD-TEXT from a physical disc, `-x` alone on a drive that goes on to rip | — structural: an absence. No fixture can produce any of these, which is the claim. **Four came off on 2026-09-03**; see the rows below |
| **CC-1 IS NOT MET, and we said it was.** What is measured: **two** whole-disc rips on the released pin completed cleanly — `Tracks to rip: all`, `Ripping errors: 0`, `Rip completed:  yes (14 of 14 tracks)`, `Log FUN512` intact, `-Y` exit 0. What is NOT established is the thing CC-1 asks for: their acceptance **run** timed out in section F at `10800.1`s and its ARCHIVAL section H produced no evidence at all. **We concluded the pass from the rips inside it** — "I verified the list you sent" is not "I verified your inventory" | `grep -c "^Rip completed:  yes (14 of 14 tracks)" docs/rig-2026-09-03-978f9b0/rips/full-acceptance-angle-bracket.log` — this checks the RIP, which is all it ever checked. — theirs: the run's failure is their lap 6 §C1, which we cannot re-run |
| **`0.6.34` is `dba2ab2`**, and we declared it `unknown` in a lap while holding it: the bundle's own per-rip JSON carries `generator.build_fingerprint: dba2ab2`. Confirmed independently by their lap 5's `HANDSHAKE-OUR-PIN` | — theirs: their lap 5 wire header. The bundle JSON that also carried it is not filed (19 MB); its hash is in `docs/rig-2026-09-03-978f9b0/SHA256SUMS` |
| **Six consecutive digest values agree across two independent implementations.** Their laps 4–9 declare `1ad28e7744de3d6b/3`, `ddc0d8a741f76b60/4`, `09268d7203773872/5`, `60a7c64dc252b1fa/6`, `44e14b452950ebb0/7` (ours, confirmed by their lap 9 §B2) and `35b861f25abfa69c/8`. They built `scripts/round_digest.py` from our written spec having never read our code | `python3 tools/round-digest.py 15 --exclude round-15-lap-09.md` (= `35b861f25abfa69c over 8`) |
| **`0.6.37` is `f3b60a0`** and is the agreed app half of round 15, accepted in our lap 8 §1 after their half moved four times, each move declared | `grep -m1 'HANDSHAKE-OUR-PIN' docs/handshake/inbound/round-15-lap-09.md` |
| **The abort footer and a diagnosed non-zero exit, together and on hardware.** `cyanrip -N -l 1` exited **1** having printed `Offset is unset!…` at column 0, then `Rip completed:  no (aborted, 0 of 14 tracks)`. It also settles one P5a `goto end` row by running it, which is what the legend said those rows needed | `grep -c "Rip completed:  no (aborted, 0 of 14 tracks)" docs/rig-2026-09-03-978f9b0/session/DIAGNOSTICS.txt` |
| **`Secure re-read:  did NOT converge after 3 reads (repeat limit hit)`** — the non-converged arm, three tracks on each whole-disc rip. Only the converged arm had ever been produced | `test $(grep -c "did NOT converge after 3 reads" docs/rig-2026-09-03-978f9b0/rips/secure-reread.log) -eq 3` |
| **The PLURAL `Read stalls:` rendering**, `5 reads exceeded 10s; longest 11s (track 1, LSN 8322)`. 2026-08-26 produced only the singular | `grep -c "^Read stalls:    5 reads exceeded 10s" docs/rig-2026-09-03-978f9b0/rips/after-cancel.log` |
| **Every 2026-09-03 log verifies against a LATER build.** `-Y` exits 0 on all seven, which re-confirms the cross-build property and proves the filing altered no byte | `for f in docs/rig-2026-09-03-978f9b0/rips/*.log; do case "$f" in *.eac.log) continue;; esac; ./build/src/cyanrip -Y "$f" >/dev/null 2>&1 \|\| exit 1; done` |
| **The 2026-09-03 `cancel me` rip does NOT show a cancel** — `Rip completed:  yes (3 of 14 tracks)`, third session running. But the session **does** hold evidence one happened: an exit 3 `No FUN512 checksum found`, a rip killed before it writes its signature. The interrupted artifact existed and is not in the bundle | `grep -c "No FUN512 checksum found" docs/rig-2026-09-03-978f9b0/session/DIAGNOSTICS.txt` |
| **`cyanrip --version` hung twice on the rig through `~/.local/bin/cyanrip`** (0-byte P3 artifact; `timeout -k 10 60` → exit 137) while Platterpus got the banner from the same path 3 s earlier in under a third of a second. **NOT reproduced here and NOT attributed:** interleaved on this tree, `--version` / `-v` / `-V` are indistinguishable at 0.034–0.042 s | `for f in --version -v -V; do ./build/src/cyanrip $f >/dev/null </dev/null; done` (all return at once) |

## Things that are true and read as false

| fact | check |
|---|---|
| **`-H` SILENTLY DISCARDS DE-EMPHASIS, and the log claims it was applied.** `init_filtering()`'s filter string is a ternary cascade — `hdcd ? "hdcd" : deemphasis ? "aemphasis=type=cd" : …` — so with `-H` the de-emphasis filter is never in the graph. Measured on `preemph.cue`: `-H`, `-H -W` and `-H -E` are **byte-identical**, so both the disable and the force flag are inert. Meanwhile `cyanrip_log.c:410` prints `(deemphasis applied)` from the SETTINGS, and `cue_writer.c:184` drops `FLAGS PRE` on the same reasoning. **Audio, log and cue are self-consistently wrong**: a reader checking one against another finds agreement. **All three halves are upstream's** — a merge-back candidate, not ours. Unreachable in Platterpus's usage: 0 uses of `-H` in their acceptance script or any 2026-09-03 rip | `grep -q 'hdcd ? "hdcd" :' src/cyanrip_encode.c` — the mechanism, still present. Goes stale when fixed, which is correct |
| **Per-track paranoia counters do NOT sum to the disc totals under `-Z`.** The per-track baseline is snapshotted after `repeat_ripping:`, so it describes the **last pass**; the disc counters sum **every** pass. Equality holds only when each track was read once | — past: round 13, measured 15+10+5=30 against a disc total of 90 |
| `Cache model:` reports what paranoia **models**, never what the drive has. Since 2026-08-26 it says `(drive cache probed separately…)` when `-x` ran | `./build/tests/diag_test` |
| `none` and `unknown (reason)` are different claims everywhere in the log, on purpose | — structural: a policy over every log line, not a single assertion |
| **`Done; (no matches found, but hit repeat limit of N)` is NOT an error.** It is the non-convergence *measurement*, followed immediately by `Track N ripped and encoded successfully!`. It sat in P5's failure inventory on `goto finalize_ripping` alone until 2026-09-03, and a consumer recorded five errors against a rip that completed 14 of 14 with none | `test $(grep -A1 "no matches found, but hit repeat limit" docs/rig-2026-09-03-978f9b0/rips/full-acceptance-angle-bracket.log \| grep -c "ripped and encoded successfully") -eq 3` |
| **A bare `goto` is not evidence of a failure path** — it is the absence of evidence plus a note about where control went. P5a carries the 7 rows in that state and claims nothing in either direction; `end:`, `end_meta:` and `finalize_ripping:` are all fall-through-reachable from success, so no rule separating them is about anything but the label's name | `python3 -c "import importlib.util as u,sys;s=u.spec_from_file_location('g','tools/gen-provider-contract.py');m=u.module_from_spec(s);s.loader.exec_module(m);e,o=m.partition_fatal(m.collect()[2]);sys.exit(0 if o and not any(m.GOTO_ONLY_RE.fullmatch(r[4] or '') for r in e) else 1)"` |
| **`ddf7ac3` is a cyanrip commit** (`0.9.4-rc1+platterpus.5`), not a Platterpus one, despite standing in `HANDSHAKE-PEER-PIN` through two closed rounds | `git log --oneline -1 ddf7ac3` |
| **A commit that RESOLVES is not thereby REACHABLE.** A clone holds every object its reflog still names, so `git log -1 <sha>` succeeds on a commit that `git commit --amend` orphaned — one that `git gc` destroys and a fresh clone never has. `merge-base --is-ancestor` is the only test that separates them, and `seam-check.py` now runs it on `HANDSHAKE-FROM-COMMIT`. Round 15 lap 3 declared such an orphan and every check passed it | `python3 tests/release_gate.py` — the regression test builds an orphan; **grading a well-formed lap does not discriminate**, since a reachable commit resolves too |
| **`HANDSHAKE-FROM-COMMIT` is the PARENT of the commit that adds the lap**, never the lap's own commit — the same fixpoint as a generated artifact naming its build. Every lap that declares a bare SHA obeys it | `n=0; for f in docs/handshake/round-*.md; do c=$(grep -c "^HANDSHAKE-FROM-COMMIT:" "$f"); [ "$c" = 1 ] \|\| continue; s=$(sed -n "s/^HANDSHAKE-FROM-COMMIT:[ \t]*\([0-9a-f]\{7,40\}\)[ \t]*$/\1/p" "$f"); [ -z "$s" ] \|\| { n=$((n+1)); git merge-base --is-ancestor "$s" HEAD \|\| exit 1; }; done; test "$n" -ge 10` |

## Upstream `cyanreg/cyanrip` — what it still lacks, for merge-back

Checked against `master` at `f8ebf48`, not recalled. **`-Y` was on this list from
memory and is wrong: upstream has it.** That is the whole reason the list is
checked rather than written.

| fact | check |
|---|---|
| Upstream still calls `cyanrip_log()` **inside the signal handler** — a mutex and stdio in a handler, the deadlock that hangs the process with the drive held | `r=$(git rev-parse -q --verify master \|\| git rev-parse -q --verify origin/master) && u=$(git show $r:src/cyanrip_main.c) && printf '%s' "$u" \| awk '/on_quit_signal\(int/,/^}/' \| grep -q cyanrip_log` |
| Upstream handles **no SIGTERM at all** — 0 occurrences | `r=$(git rev-parse -q --verify master \|\| git rev-parse -q --verify origin/master) && u=$(git show $r:src/cyanrip_main.c) && printf '%s' "$u" \| grep -q on_quit_signal && ! printf '%s' "$u" \| grep -q SIGTERM` |
| Upstream has `cyanrip_log_finish_report()` immediately **above** `end:`, so every `goto end` skips the completion footer | `r=$(git rev-parse -q --verify master \|\| git rev-parse -q --verify origin/master) && u=$(git show $r:src/cyanrip_main.c) && printf '%s' "$u" \| grep -B1 '^end:' \| grep -q cyanrip_log_finish_report` |
| **`-Y` / `--verify-log` is already upstream** — not ours to contribute | `r=$(git rev-parse -q --verify master \|\| git rev-parse -q --verify origin/master) && u=$(git show $r:src/cyanrip_main.c) && printf '%s' "$u" \| grep -q verify_log` |

## Platterpus's side — held because they told us, not because we checked

| fact | check |
|---|---|
| `~/.local/bin/cyanrip` on the rig is a **host-exported Distrobox wrapper**; the real ripper runs in a container. **ARCHITECTURE YES, CAUSE NO** — their lap 16 §D1(a) withdraws it as the explanation for the empty capture, because a later run's capture was 111 bytes and a theory predicting *always empty* does not predict *sometimes empty* | — theirs: their lap 12 §E2, corrected by their lap 16 §D1(a) |
| Their `cyanrip` script verb is bounded: 300 s, then a kill, then 20 s, then an unreapable-child record with a **null** exit code | — theirs: their lap 12 §A |
| `0.6.26` was **not published** until 2026-08-25; the operator was on `0.6.25 (5f374aa)` before that | — theirs: their lap 13 §A2 |
| Their gate had the same `HANDSHAKE-TEST-PIN: none.` misreading as ours, fixed the same way | — theirs: their lap 12 §D |
