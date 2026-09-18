# Rig session 2026-09-17 — build `3952c03`, Platterpus 0.6.50

**Read the build, not the date.** This is the **second** session on 2026-09-17:
the first ran on `fe4d2c4`, the RELEASE pin, and was void for round 21's
purposes — `docs/rig-2026-09-17-fe4d2c4/`. This one ran on `3952c03`, the
**test pin** round 21 lap 1 declared, which is what §0.1 asked for. Two
sessions, one calendar date, different builds: the naming convention that
separates them exists because calling both "the 2026-09-17 session" is how a
claim about one comes to be checked against the other's log.

## Provenance

| | |
|---|---|
| bundle | `platterpusbundle20260917t233651z.tar.gz`, handed over by the operator |
| sha256 | `901d6f7e8896ebdf1ed76b0bc091cba059b1b216c8d9830bf0cb7e52f2ae8dac` |
| size | 3,968,724 bytes, 14 entries |
| session stamp | `20260917T233651Z` |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), `/dev/sr0` |
| disc | The Police, *Every Breath You Take: The Classics*, 14 tracks, MusicBrainz `d14a7546-815b-43c6-8af6-35cff6cee1d0` |
| ripper | `cyanrip 0.9.4-rc2+platterpus.12 (platterpus-fork-g3952c03)` — **the test pin** |
| consumer | Platterpus 0.6.50, build `4bedb45` |
| rip | one whole-disc pass, `rip_goal: fast_verified`, 58m38s wall clock |

Provenance, the full 14-file inventory with hashes, and what is *not* filed
here are in `session/SOURCES.txt`. The five filed files are byte-identical to
bundle files, checked by hashing all 14 bundle objects and requiring each
filed file to match one.

**It is one rip, and that was the agreed shape.** Platterpus's lap 4 kept
exactly this from our withdrawn draft — *"one whole-disc `fast_verified` rip
on `3952c03`, not another acceptance sweep"* — and the operator confirmed it.
So the single rip is the deliverable, not a shortfall.

**And it was driven from the GUI, not by the acceptance script.** There is no
`script-report.json`, no `rig-check-*` file and no transcript in this bundle,
and the app log's only driver is `platterpus.ui.main_window_rip`
(`rig_script`, `acceptance` and `script_report` appear **0** times in the
session window).

Said out loud because the **immediately preceding three sessions were
scripted** and this one is not — `docs/rig-2026-09-15-fe4d2c4/`,
`docs/rig-2026-09-15b-fe4d2c4/` and `docs/rig-2026-09-17-fe4d2c4/` are the
only filed sessions carrying `script-report.json` and `rig-check-*`, 3 of the
17 here, so a reader comparing this directory against the three most recent
would take a different method for a missing file. (This paragraph first said
*"every previous rig directory here was scripted"*, which is false by 14 of
17 — it was written from the three that were fresh in mind rather than
counted.)

## Against §0.1's three things

Round 21 lap 1 §0.1 fixed three, *"and no more than three"*. Scored one by
one, and **one of the three was asked for in words no run can satisfy** —
which is a defect in our condition, not in this session.

| | asked for | established | on what |
|---|---|---|---|
| 1 | the `fast_verified` whole-disc path runs on hardware | **yes** | `settings.rip_goal: "fast_verified"` with `rip.rip_completed: true`, `rip_completed_tracks: 14` of `14`, and `Rip completed:  yes (14 of 14 tracks)` in `rips/whole-disc-fast-verified.log`. Their `self_check` adds *"the ripper received the 13 flags we sent on the whole-disc pass"*. |
| 2 | *"your parser reads `Retry limit:` on real logs"* | **the risk is retired; the wording is not satisfiable** | see below |
| 3 | `Ripping errors:` on a real session is the moved field, and their EAC-compatible export's `health_status` reflects it | **yes** | `Ripping errors: 0` in our log; `No errors occurred` at line 252 of `rips/whole-disc-fast-verified.eac.log`; `health_status` in their report reads the same string |

### §0.1 item 2 — answered, and it answers our own lap rather than their build

The label reached their process. From the bundle's `applog/log.txt.1` —
**not filed here**, 8.4 MB and theirs; its hash and this quote are both in
`session/SOURCES.txt` so the line stays checkable against the operator's copy
— at 2026-09-17 18:38:19,346:

```
DEBUG platterpus.workers.rip_worker: cyanrip │ Retry limit:    3 (per frame, and per whole-track re-read)
```

**But nothing in their report is derived from it, and that is deliberate and
documented.** Read at
`platterpus@4bedb45:src/platterpus/parsers/cyanrip_log.py:1876-1879`, the
label is an entry in `_IGNORED_DISC_LINES` — the allowlist of disc rows the
parser recognises and extracts nothing from:

```python
(
    re.compile(r"^(?:Frame retries|Retry limit):\s"),
    "candidate: rip-effort setting (renamed Retry limit in round 20)",
),
```

and the comment above it says so in as many words:

> *"We extract nothing from it either way, so the rename is invisible to the
> PARSE — but this file's completeness sweep fails on any unrecognised disc
> line, so the new label has to be here BEFORE their build ships or every rip
> log trips it."*

So **"your parser reads it" was never a property their code had**, for the new
label or the old one. What §0.1 item 2 was actually guarding is the sentence
after the dash — that an unrecognised disc line trips their completeness
sweep on every rip — and **that is retired on hardware**: their report carries
`log_parse: {"ok": true, "note": null}` and is fully populated from our log,
on a real session, with the new label present.

**This is our defect, in the same family as round 12's.** We wrote a close
condition that asserts a mechanism in their code without citing where it was
read. The remedy `CLAUDE.md` already gives is the one that applies, and it is
cheap: cite `platterpus@<sha>:<path>:<line>`. Doing that *before* writing the
condition would have caught it — the comment was in their tree, at that path,
when lap 1 was written.

### §0.1 item 3 — established as worded, and this artifact cannot discriminate the move

`_take_rip_errors` at
`platterpus@4bedb45:src/platterpus/parsers/cyanrip_log.py:1617-1624` turns a
count of 0 into `health_status = "No errors occurred"`, and that string is at
line 252 of their EAC-compatible export for this rip. The field is read, on a
real session, from the build where the footer sits below the encoder-status
loop. **That is what item 3 asked for and it holds.**

**What it does not do is prove the move mattered, and no clean rip can.**
`git diff fe4d2c4 3952c03 -- src/cyanrip_main.c` moves
`cyanrip_log_finish_report()` from above the encoder-status loop to below it;
the loop's only effect on the printed value is `ctx->total_error_count++` on
an encoder failure. **With zero encoder failures the two placements emit
byte-identical output.** This rip had zero. So the discriminating evidence is
`sc_encode_failure_reaches_the_log()` in our own suite — cap every write at
32 KiB, and the pre-move build reports `Ripping errors: 0` and
`Rip completed:  yes` over a 32,768-byte file whose intact form is 253,742 —
and it is **not** hardware evidence. (That test was **renamed in round 21**,
from `sc_encode_failure_is_absent_from_the_log()`, and the comment in
`src/cyanrip_main.c:2703` that justifies the move still names the old one; see
`docs/KNOWN-ISSUES.md`.) Stated because a green close condition
here must not be read as a hardware demonstration of the fix.

## What it did NOT establish, and why — `-x` was not run

§4b asked for the cache-probe **calibration series**: the calibration reads,
the median that became the threshold, and one line per run with what the rule
scored it. It is **still unmet**, and the reason is different from last time,
which is the whole point of recording it:

- the **2026-09-17 `fe4d2c4`** session ran the probe and got the old `-j`
  schema, because the build was wrong.
- **this** session has the right build and **did not run the probe at all**.
  `-x` is absent from `Invoked as:`; the log reads `Cache model:    1200
  sectors (drive cache size not probed)`; `Cache probe` appears **0** times in
  the session's app log.

*Did not happen* and *happened and produced the wrong thing* are different
claims, and `docs/ROUND-22-PLAN.md` §2 stays gated on the first one now rather
than the second.

There is also **no `-j` record in this bundle.** `-j
cyanrip-diagnostics-20260917T223814Z.json` is on the command line, so
`3952c03` wrote one at schema `cyanrip-diagnostics/6`; it is not among the 14
entries. Absent, not empty.

## Two observations, each with its status

**1. The spawn path and the `Invoked as:` path differ, and both records are
right.** Platterpus spawned `/home/rmccann/.local/bin/cyanrip`
(`outcome.ripper_argv[0]`, and `adapters.rip_backend` at 19:36:50,838). Our
log's `Invoked as:` records `/usr/local/bin/cyanrip`. `record_invocation()`
(`src/cyanrip_main.c:1364-1380`) prints `argv[0]` verbatim — *"the command
line as this process actually received it, recorded so a log states what was
run rather than what a caller believes it ran"* — so the process genuinely
received the second path. `/usr/local` appears **0** times in their app log
and 4 times in their report, all four inside embedded copies of our own text.

**Not a defect, not new, and the mechanism is already settled — which this
section first said was "not determinable from this bundle".** It is
determinable from `docs/SETTLED.md`, which the rule says to read *before*
deriving anything, and the row is there: *"`~/.local/bin/cyanrip` on the rig
is a host-exported Distrobox wrapper; the real ripper runs in a container"*
(theirs, their lap 12 §E2). So `.local/bin/cyanrip` is the host-side wrapper
Platterpus spawns and `/usr/local/bin/cyanrip` is the binary inside the
container, which is why our `argv[0]` differs and why `/usr/local` appears
nowhere in their log. `/usr/local/bin/cyanrip` is in the `Invoked as:` line of
the 2026-08-04 session too, so it is six weeks old.

**Taken together the two records are informative rather than confusing**, and
that is the line worth keeping: `ripper_argv[0]` is what Platterpus asked
for, `invoked_as` is what ran, and the pair says the rip happened in the
container. **It is three fields and two answers**: `outcome.ripper_argv[0]`
and `ripper_command_display` both give the wrapper, `rip.invoked_as` gives the
container binary, and nothing in the report states that they can differ —
which is the only thing here a reader could trip on. That row also carries its own
warning — **ARCHITECTURE YES, CAUSE NO** — so the wrapper explains *these two
paths* and is explicitly not licensed to explain anything else about the rig.

**2. Their `self_check` flagged the open round from our own `Handshake:`
line**, as a `warn`:

> *"the ripper says it was built from an OPEN round: 'round 21 lap 1 OPEN,
> verdict OPEN -- NOT a released build' — rips from this build carry that
> sentence permanently in their log"*

The previous session's README recorded that line answering a question for the
first time, on our side, about a wrong build. Here it does the same job from
the consumer's side, on the right one. **The mechanism is not new** — 22
previously filed rig rips carry `NOT a released build`, from the round-14 and
round-16 test pins — and this is the **first** rip filed here from `3952c03`
and the first in round 21.

## What is routine and was checked rather than assumed

`Tracks ripped partially accurately: 1/14`, from `Accurip 450: 4CCBCF89
(matches Accurip DB, confidence 200, track is partially accurately ripped)` on
track 5 — v1 and v2 both `not found`, the 450 checksum matching an
offset-variant pressing. This looked like a first and **is not**: the line is
non-zero in **27** filed rig logs going back to 2026-08-26, at 1/14, 2/14 and
3/14 on this same disc and drive. Their export renders it as *"1 track(s)
matched only an offset-variant pressing (partially accurate)"* and their
report carries `partially_accurate_reported: "1/14"`.

`Pregap source: sub-channel (not signalled by TOC)` on 13 tracks and `lead-in`
on 1 — **which every whole-disc rip of this disc has reported, 18 of 18 across
nine sessions and four builds.** Scoped deliberately: the shared condition is
*the same disc in the same drive*, so this is a fact about that disc and not an
invariant of the pregap search. The 52 narrowed rips filed here report 1/1,
2/1 or 0/0 according to how few tracks they asked for, which is why the count
has to be read beside `Tracks to rip:` and not on its own. (This section first
said *"consistent with every previous session"*, which the distribution
refutes.)

Also routine: `C2 errors: unsupported by drive`; and `Read stalls: none (no
read exceeded 10s)`, which is the expected result on healthy media and **is not
evidence either way** about the watchdog.

## The filed log is provably unmodified

Platterpus ran `cyanrip --verify-log` on the rig and recorded `checksum valid`
— one program checking itself. Re-run here against a different build on a
different machine:

```
$ ./build/src/cyanrip --verify-log docs/rig-2026-09-17-3952c03/rips/whole-disc-fast-verified.log
Log "...whole-disc-fast-verified.log" checksum valid.
exit 0
```

by `platterpus-fork-g122af59`, not by `3952c03`.
