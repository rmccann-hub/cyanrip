# Rig session 2026-09-15 — **the same pin, a second time, three days apart**

Platterpus acceptance session `20260915T005848Z`: `platterpus 0.6.48` (`a7fdf98`)
driving `cyanrip 0.9.4-rc2+platterpus.12 (platterpus-fork-gfe4d2c4)`, PIONEER
BD-RW BDR-209D 1.51, on the reference 14-track disc.

**The pin is unchanged from the 2026-09-12 session.** Only Platterpus moved
(`0.6.47` → `0.6.48`). That is what makes this session worth more than another
green run: two acceptance sessions, same build, same disc, same offset, three
days apart, is a **reproducibility experiment nobody constructed** — and it is
the one thing a single session can never be.

## What it establishes

**Round 19's pin survives a second hardware session.** `241` steps, `0` fail,
`0` error, `0` blocked, `0` unreachable, `1` info. Eight rips: two whole-disc
(`14 of 14`), five partial (`2 of 14`), one deliberately interrupted. Seven
`Ripping errors: 0`, `Read stalls: none` on all eight, `AccurateRip: found` on
all eight.

**All eight logs verify against our own tool, run here rather than reported**,
and against a **different build from the one that wrote them**:
`build/src/cyanrip -Y <each>` at `411c80a` → exit **0**, eight for eight, on the
copies in `rips/`. So the `Log FUN512:` line is intact in the filed evidence
*and* the signature is stable across the 54 commits between `fe4d2c4` and
`411c80a`.

### The cross-session comparison — 13 of 14 tracks reproduce exactly

`secure-reread.log` here against `docs/rig-2026-09-12-fe4d2c4/rips/secure-reread.log`,
both `-Z 2 -r 3`:

| | 2026-09-12 | 2026-09-15 |
|---|---|---|
| tracks whose `EAC CRC32`, `Accurip v1` and `Accurip v2` all match the other session | **13 of 14** | **13 of 14** |
| the one that differs | **track 3** | **track 3** |
| `did NOT converge after 3 reads` | tracks **3, 5** | track **5** |
| per-track paranoia / disc totals | 26504 / 76547 (×2.888) | 26550 / 76512 (×2.882) |

**The single differing track is exactly the track whose convergence status
differed**, which is the result the corrected `-Z` semantics predict and the
only one that would be reassuring. Track 3 hit the repeat limit on 09-12 and
converged on 09-15; its checksums are from different audio, and the log says so
on both.

**Say it at the scope the evidence covers:** every checksum cyanrip computed
over the audio is identical on those 13 tracks. The *files* are not identical —
`creation_time` differs between any two rips by the same binary — and no audio
travelled in either bundle, so this is a comparison of checksums, which is what
the logs are for.

**Track 5 did not converge in either session and reported the same
`EAC CRC32` (`E0036697`) both times.** That is worth stating because it is
easy to read backwards: `did NOT converge` says *no two reads within the limit
agreed*, and **not** that the result is unstable. Track 3 shows the other arm —
non-convergence with a genuinely different result three days later. A consumer
must not infer either one from the label; the label means what it says.

**`Accurip 450:` is identical on tracks 3 and 5 across both sessions
(`BF62B1DA`, `4CCBCF89`) even where the track's other checksums differ. Checked
against the source, and it is not a defect:** `crip_process_checksums()`
(`src/checksums.h:74`) accumulates `acu_sum_1_450` over **one sector** — the
588 samples at sector 450 — so it identifies the pressing and says nothing
about the rest of the track. The log already carries the qualifier the value
needs (`track is partially accurately ripped`). Recorded here because anyone
diffing these two sessions will meet it and could reasonably read it as a bug.

### The paranoia `Scope:` caveat earns itself again

`secure-reread.log`: per-track counters sum to **26550**, the disc block totals
**76512** — a ratio of **2.88**, not 3, because one track stopped at the repeat
limit while thirteen converged. Independently re-derived here from the filed
copies rather than taken from Platterpus's `rig-check` summary, which reports
the same pair.

`FIXUP_ATOM` is the sharp one again: **8 per-track against 32 at the disc
level**, a ratio of 4 inside a log whose overall ratio is 2.88. A consumer
summing per-track blocks would report a quarter of the edge fixups this disc
actually recorded. That is what the `Scope:` line exists for, and it is present
on 14 of 14 tracks here.

`cancel-me.log` is the opposite case and equally load-bearing: **zero** track
records, so nothing to sum, and a disc block recording **617** paranoia events.
An interrupted rip still reports what the drive did.

### A fourth cancel that reached the process

`cancel-me.log`: `Ripping errors: 1`,
`Rip completed:  no (interrupted by SIGTERM, 0 of 14 tracks)`,
`Interrupted at: track 1, mid-read`, a valid `Log FUN512:`, `-Y` exit 0. The
record of an incomplete rip is itself complete and attested.

### The ripper wrapper is a `distrobox-enter` shim, and they instrument it

Our `Invoked as:` says `/usr/local/bin/cyanrip`; every Platterpus record of the
same launch says `/home/rmccann/.local/bin/cyanrip`. That is not a
contradiction and neither side is wrong — `record_invocation()`
(`src/cyanrip_main.c:1364`) prints argv as **this process received it**, which
is the whole reason the field exists.

`session/script-report.json` step 14 settles what sits between them: their
`probe-ripper-wrapper` step runs all four legs and records
`['distrobox-enter', '-n', 'ripping', '--', '/usr/local/bin/cyanrip', '--version']`.
So the shim is known to them, probed every run, and named in their own
artifact — it is not an undeclared layer. It is also the exact shape that ate
the 2026-09-07 cancel, which is why they probe it; the step is scored `info`
and reads *"The 2026-08-27 hang does not reproduce here."*

Note what their `argv/integrity` check does and does not cover: it compares the
**16 flag tokens** against our record of the 30 args. `argv[0]` is not among
them. Build identity is established separately and adequately, by our own
banner (`ripper-version.txt`, and `vcs: fe4d2c4` in the probe's `-j` record) —
so nothing here is unverified. It is only worth knowing that *which binary ran*
comes from the banner and not from that check.

### Round 18's outcome vocabulary is live; the tier scaffolding is not yet populated

`session/script-report.json` declares `outcome_vocabulary: 2`, and the verdict
line carries a **new `unreachable` counter** (`unreachable 0`) that the
2026-09-12 session's did not. That is the round-18 §3 split — *cannot be done*
versus *not yet done* — with a counter behind it.

**Every one of the 242 steps has `tier: null` and `tier_label: ""`.** The
fields are in the schema; no step is assigned a tier, and no tier-4 sweep ran.
Stated as observed: the scaffolding they described in round 18 is present and
the tiering is not yet switched on. Nothing in this run depended on it.

## What it does NOT establish

**It is evidence about `fe4d2c4` under `0.6.48`.** It is not evidence about the
pairing the record *approves* — their `handshake_approval.py` deliberately
still names `0.6.47`, and their own `DIAGNOSTICS.txt` says so in as many words.
Both facts are true and they are different facts.

**Nothing came off the hardware list.** C2 stays `UNREACHABLE` — this drive
reports it unsupported, in this session's header as in every other. `-f`,
damaged media and CD-TEXT from a physical disc are all still *not yet done*;
none was exercised.

**The cache calibration is not fixed and this run does not fix it** — see
below. It adds a fourth measurement, which changes the argument.

**The `x2` folder is not the two-track rip by virtue of its name.** In this
session `full-acceptance-angle-bracket.log` is the **14-track** rip and
`full-acceptance-angle-bracket-2.log` is the **2-track** one. In the 2026-09-12
session the assignment is the other way round. The `(2)` in the on-disk folder
name is Platterpus's collision suffix, not a track count — read
`Rip completed:` before crediting either file with anything.

## The fourth cache probe, and what the fourth run is for

`cyanrip -N -x -I`, exit 0 in 15.9 s (`session/transcript.txt`, acceptance-script
step `L840` — their script's line number, not the transcript's):

```
Cache probe:    at least 2048 sectors, upper bound unknown (4704.0 KiB or more,
                search ceiling reached, uncached read 362.6 ms, cached read 61.7 ms)
```

Same ceiling, fourth time. The number is still one we set, and
`cd-paranoia -A` still says 137 then 140 on this drive — **do not cite our cache
figure.** What this run adds is in `docs/KNOWN-ISSUES.md`: it has essentially
the same `miss_cost` as the 2026-09-10 run (362.6 ms against 363.2 ms, 0.17%
apart) and a classified read 25% lower, which moves the margin from 90% of
threshold to 68%. Two runs of the same drive with the same calibration land a
third apart, which is the clearest evidence yet that `CACHE_HIT_RATIO` is not
calibrating anything.

## One thing this session put a number on, in our own log

`Frame retries:  3` on line 18 of `rips/secure-reread.log` and
`Secure re-read:  did NOT converge after 3 reads (repeat limit hit)` on line 425
are **the same three, and the log does not say so.** `-r` is *"Maximum number of retries for
frames and repeated rips"* — `PROVIDER-CONTRACT.md` P1 says so, derived from
`--help` — and it is passed both to `cdio_paranoia_read_limited()`
(`src/cyanrip_main.c:534`) and to the repeat-loop limit
(`src/cyanrip_main.c:1011`). The log line names one of the two.

Not reworded here. It is a P2 contract line, so the rename is a handshake
proposal; recorded in `docs/KNOWN-ISSUES.md` and carried into round 20.

## Files

`rips/` — the eight logs, cues and EAC-compatible logs, byte-exact from the
bundle. No audio travelled; per-track CRCs are the record.
`session/` — Platterpus's `MANIFEST.txt`, `SOURCES.txt`, `DIAGNOSTICS.txt`,
`transcript.txt`, application log, `config.toml`, the acceptance script report
(`script-report.json`) and the four `rig-check` artifacts.

Not filed: the eight `.platterpus.json` per-rip reports (6.2 MB for one of
them) and 163 screenshots. Said out loud rather than left to be noticed —
an absence somebody can read is a finding.
