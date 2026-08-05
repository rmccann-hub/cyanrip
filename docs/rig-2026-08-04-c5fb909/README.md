# Rig session, 2026-08-04 — the **`c5fb909`** one

**There were two rig sessions on 2026-08-04 and our documents have been calling
both of them "the 2026-08-04 rig session".** This directory exists to end that.

| | this directory | `docs/rig-2026-08-04/` |
|---|---|---|
| cyanrip build | `c5fb909` — `…+platterpus.5-beta.2` | `9003e6f` — `…+platterpus.5-beta.1` |
| Platterpus | `0.6.4b4`, build `c7aa67c` | `0.6.4b3`, build `1671c21` |
| what it closed | `Read stalls:`, the pre-log replay block, `--verify-log` on a real log, `C2 errors: unsupported by drive`, 14/14 EAC parity | the first hardware `Pregap source: sub-channel` run, `-Z` convergence, per-track paranoia counters |
| cyanrip's own `.log` / `.cue` | **not held** — see below | held, and archived unmodified |

Same drive (PIONEER BD-RW BDR-209D 1.51), same disc (The Police, *Every Breath
You Take: The Classics*, 14 tracks, MusicBrainz DiscID
`pNtImOkdBm9RMBIalzx0w9cfsYY-`, CDDB ID `E20DFE0E`), same `+667` offset.

## What is here, and what it is not

| file | written by |
|---|---|
| `platterpus-results.md` | **Platterpus**, verbatim as received. Not ours, not edited. |

**cyanrip's own log and cue from this session are not in this repository.** That
matters, and it is why this README exists rather than a bare file drop:
`docs/AUDIT-2026-08-05.md` §2 lists what this session closed, and **every row of
that table rests on the document beside this one** — a report about artifacts,
not the artifacts. Our own protocol calls that an assertion rather than a
verification.

Archived anyway, because a report you can open is strictly better than one
quoted from memory in a handshake file. **Asking Platterpus for this session's
`cyanrip.log` and `cyanrip.cue` is round-8 work**, and until they arrive, §2's
rows should be read as *"Platterpus reports"* and not *"we checked"*.

## One thing found wrong in it

Line 4 reads *"DiscID `E20DFE0E`"*. **`E20DFE0E` is the CDDB ID**, not the
DiscID — cyanrip prints them as two separate fields, and
`docs/rig-2026-08-04/cyanrip.log` lines 25 and 27 give
`DiscID: pNtImOkdBm9RMBIalzx0w9cfsYY-` and `CDDB ID: E20DFE0E`. The number is
right and the label is wrong.

It is recorded here rather than corrected in their file, which is kept verbatim.
It also propagated into our own round-07 lap 24 and the first draft of lap 25
before being caught, so this is a note about both projects and not about theirs.
