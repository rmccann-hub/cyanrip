# Rig session 2026-09-15b — **`0.6.49`. Their fix works, and a third session on one pin breaks a correlation we had already written down.**

Platterpus acceptance session `20260915T120109Z`: `platterpus 0.6.49` (`c57025e`)
driving `cyanrip 0.9.4-rc2+platterpus.12 (platterpus-fork-gfe4d2c4)`, PIONEER
BD-RW BDR-209D 1.51, on the reference 14-track disc.

**Third acceptance session on the same pin in four days.** `0.6.47` on 09-12,
`0.6.48` on 09-15T00:58, `0.6.49` here. Only Platterpus moved each time.

## The absence audit, first — and this time it is clean

**The 09-15a session reported `241 pass / 0 fail` and had written no MP3 and no
WavPack, and we did not catch it.** So this README starts where that one should
have: with what is *not* in the bundle.

| album | derived output listed in `MANIFEST.txt` |
|---|---|
| `derived wav` | **2 × `.wav`** |
| `derived mp3` | **2 × `.mp3`** |
| `derived wavpack` | **2 × `.wv`** |

All three present. The transcode half of what Platterpus reported on 2026-09-15
is fixed and the fix is visible in the artifact rather than asserted.

## Their reporting fix, verified against their own code and their own output

Their remedy is a new `superseded` state, read from
`platterpus@c57025e:src/platterpus/rip_report.py`. `build_gates()` still derives
from configuration — its docstring says so — and a caller now passes the gate
keys whose work was **dropped because a newer rip started**, which overwrite the
config-derived value. The docstring states the principle better than we would
have:

> *"they are a fact about what HAPPENED and the rest are facts about what was
> REQUESTED — and when those two disagree the second one is the one that lies."*

**It fires.** Three of the eight rips carry
`superseded — a newer rip started before this finished` on `ctdb` and
`flac_integrity`, each with the matching `verification_superseded` warning.

**And the backstop catches everything the named cause does not.** Three *other*
rips still show `"ran"` beside a null block — `cancel me`, `derived mp3`,
`derived wavpack` — and **every one of them is flagged by their own report** as
`verification_result_missing`: *"the two disagree, and the gate is the weaker
evidence because it is derived from the settings, not the work."*

So the state they reported still occurs, on **three of eight** rather than five,
and it is no longer silent on any of them. **We nearly filed "still broken";
reading their code and then their `issues` arrays is what stopped it.**

## The 244/0 verdict is again not a statement about the rips

`script-report.json`: 245 step records, **244 pass, 0 fail, 0 error,
0 unreachable, 1 info**, `ok: true`. The per-rip reports in the same bundle
carry `not_bit_perfect` twice, `heavy_reread` seven times,
`verification_result_missing` eight times across three rips,
`verification_superseded` six times, `rip_cancelled`, `unverified` and
`track_count_mismatch`.

**Both are true and they are about different things.** The runner's verdict
counts script steps; the rip verdicts live in the per-rip reports. Reading the
first as the second is the error the 09-15a session's README made, and it is
worth stating once in general rather than re-learning per session.

## Three sessions, one pin — and the correlation we wrote down does not hold

Comparing **what the ripper's log recorded** (scope stated deliberately; see the
addendum section, which supersedes one of these values on disk):

| track | 09-12 `0.6.47` | 09-15a `0.6.48` | 09-15b `0.6.49` | |
|---|---|---|---|---|
| 1, 2, 4–14 | identical | identical | identical | **12 tracks** |
| 5 | `E0036697` | `E0036697` | `E0036697` | identical |
| 3 | `62680376` | `3D8FCF0C` | `3D8FCF0C` | **differs** |

**13 of 14 identical across all three sessions.** And the non-convergence
pattern, which is the part that breaks a claim of ours:

| | 09-12 | 09-15a | 09-15b |
|---|---|---|---|
| `did NOT converge` | tracks **3, 5** | track **5** | track **3** |

**`docs/rig-2026-09-15-fe4d2c4/README.md` says *"The single differing track is
exactly the track whose convergence status differed"*, and round 20 lap 1 said
it too. A third session falsifies it.** Track 3 did *not* converge in 09-12 and
did *not* converge in 09-15b, and those two runs disagree about its value; it
*did* converge in 09-15a, which agrees with 09-15b. Track 5 never converged in
two of three and reported the same value all three times.

> **Convergence status and the reported checksum are independent.** A track can
> converge on a value it also produces without converging, and can fail to
> converge twice on two different values.

That is the same lesson as the paranoia-sum "invariant": a correlation that held
on every case anyone had constructed is not a rule, and the third sample is what
says so. **Two samples produced a tidy story and it was wrong.**

**And deriving the WHOLE record rather than the newest slice settles it.** All
eight filed `secure-reread.log`s, four builds: track 3 has produced **four**
distinct values and track 5 **two**. `3D8FCF0C` is reported **converged twice
and not-converged three times**; `E0036697` likewise both ways; `6902BCF0` only
ever non-converged. Non-convergence hits track 3 in seven of eight sessions,
track 5 in five, track 4 in one, and 2026-08-26 converged on all fourteen.
`src/checksums.h` is byte-identical across all four builds and no commit between
them touches `last_checksums`, `total_repeats` or `max_retries`, so a value
difference is a difference in the read. `docs/SETTLED.md` carries all three
statements with runnable checks.

## The addendum — a new artifact, and it respects the contract exactly

Two rips carry a `.platterpus-addendum.txt` beside the log:
`secure-reread.addendum.txt` and `full-acceptance-angle-bracket.addendum.txt`.
Both supersede **track 3**.

**It exists as a separate file for our sake, and says so:**

> *"The ripper's log is left BYTE-EXACT so that `cyanrip --verify-log` still
> verifies it; that is why this is a separate file rather than text appended to
> it."*

Confirmed: `-Y` exits 0 on all eight filed logs.

**It distinguishes the three outcomes a re-read can have** — `CONFIRMED`,
`REPLACED`, or `NOT DETERMINED` when a CRC was unavailable — and says out loud
that *"a confirmed read is a good outcome: it means the disc reproduced."* That
is `none` versus `unknown (reason)` applied to a re-read, invented on their side.

**What it records for track 3 is the most interesting thing in this bundle:**

```
Re-read outcome:  the re-read produced different audio and REPLACED the first
                  pass, whose CRC32 was 3D8FCF0C
CRC 59D352DD
AccurateRip v1:   3C8BDDD2 — accurately ripped, confidence 128
AccurateRip v2:   96DF8C22 — accurately ripped, confidence 200
AccurateRip +450: n/a
Secure re-read:   converged after 3 reads
```

Our log for that track says `did NOT converge`, `EAC CRC32 3D8FCF0C`,
`Accurip v1 1B28C061 (not found, either a new pressing, or bad rip)` and a
`450` match at confidence 200. **The re-read turned an offset-variant partial
match into a genuine AccurateRip verification.**

**So track 3's `450`-only match is a read artefact, and track 5's is not.**
Track 5 carries the same `450`-only shape in all three sessions with a stable
checksum; track 3's disappears the moment the track is read again successfully.
Two tracks that looked like one phenomenon are two.

### And our own open item, re-confirmed live rather than remembered

**Neither addendum carries a timestamp** — measured, `grep -c` for any date or
clock pattern returns **0** on both files. `docs/KNOWN-ISSUES.md` says *"A
superseded track has no recorded read time anywhere"*, asked as round 8 `J14`,
and that is still exactly true of the newest artifact either side produces. Our
log's `creation_time` for track 3 describes the read that was thrown away; the
file that supersedes it is undated.

## Still unchanged

**The tier engine is built and the acceptance script assigns no tiers**, now
across two releases. The script embedded in `script-report.json` is 338 lines
and contains the string `tier` **zero times**; all 245 steps carry `tier: null`.

**Same pin, same approval string.** `rig-check` reports
`cyanrip 0.9.4-rc2+platterpus.12 (platterpus-fork-gfe4d2c4)` and *"the one
handshake round 19 approved … for Platterpus 0.6.47"*. `APPROVED_FOR_PLATTERPUS_VERSION`
still lags deliberately, now by two releases, and is still right to.

**A fifth cancel reached the process:** `Ripping errors: 1`,
`Rip completed:  no (interrupted by SIGTERM, 0 of 14 tracks)`,
`Interrupted at: track 1, mid-read`, valid `Log FUN512:`, `-Y` exit 0.

## Files

`rips/` — eight logs, cues, EAC-compatible logs and the two addenda, byte-exact.
`session/` — their `MANIFEST.txt`, `SOURCES.txt`, `DIAGNOSTICS.txt`, transcript,
application log, `config.toml`, `script-report.json` and the four `rig-check`
artifacts.

Not filed: the eight `.platterpus.json` per-rip reports and the screenshots.
Said out loud rather than left to be noticed.
