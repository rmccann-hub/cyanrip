# Rig session, 2026-08-05 — the first hardware run of **beta.4**

```
ripper      cyanrip 0.9.4-rc1+platterpus.5-beta.4 (platterpus-fork-gf5e11ba)
consumer    Platterpus 0.6.4b7 (build ce38deb)
drive       PIONEER  BD-RW   BDR-209D (revision 1.51)
disc        The Police - Every Breath You Take: The Classics, 14 tracks
            MusicBrainz DiscID pNtImOkdBm9RMBIalzx0w9cfsYY- / CDDB ID E20DFE0E
offset      +667 samples,  paranoia max,  -r 5,  no -Z
finished    2026-08-05T00:18:14, Rip completed: yes (14 of 14 tracks)
```

**Third session on this disc, and the naming is by build, not by date** — two
ran on 2026-08-04 (`docs/rig-2026-08-04/` is `9003e6f`/beta.1;
`docs/rig-2026-08-04-c5fb909/` is beta.2, report only).

| file | written by |
|---|---|
| `cyanrip.log` | cyanrip. **Verifies**: `--verify-log` → `checksum valid` |
| `cyanrip.cue` | cyanrip |
| `platterpus-eac-compatible.log` | Platterpus |
| `platterpus.json` | Platterpus |

Unlike the beta.1 log, this one is unmodified — no addendum was appended, so it
passes its own checksum as shipped.

## What this session is evidence of

**Both round-7 lap-25 proposals executed on hardware for the first time.**

- `No MusicBrainz release ID at cover art lookup, cannot search Cover Art DB!`
  — line 40, inside the replay block.
- `Tracks ripped accurately: 12/14` / `Tracks ripped partially accurately:
  2/14` — lines 1141-1142. **Under the old denominator the second line would
  have read `2/2`.** This is the first execution of that change anywhere, and
  the two lines now sum over one population.

**The replay block sits BELOW the header, settled by artifact.** `Release ID:`
is line 27; the replay runs 34–41. Both projects had described the ordering the
other way round, because both were describing when the events happened rather
than where the lines land. See round-07-lap-25 §A1(b).

**13 of 14 tracks are bit-identical to the beta.1 rip** ten hours earlier:
every `EAC CRC32` matches except track 3. Two different builds, same audio.

**The per-track paranoia counters sum exactly to the disc totals**, on media
that made paranoia work: `READ 22055`, `VERIFY 1610`, `FIXUP_ATOM 24`,
`OVERLAP 468`, each the sum of its fourteen per-track values.

**Zero stall heartbeats** across the session's full stdout capture (63419
lines, 21:24 → 00:29), consistent with `Read stalls: none (no read exceeded
10s)`. A silent watchdog is still not a working watchdog.

## What it found

**A cue-sheet defect of ours, fixed in `6400361`.** Four tracks (3, 6, 11, 12)
have `Pregap length: 0 frames` in the log and an `INDEX 00` in the cue anyway,
at a timestamp one frame past the end of the previous `FILE`. Present in the
beta.1 rip too, on the same four tracks, so it is not a beta.4 regression. The
guard compared against the offset-accounted `start_lsn` rather than the
signalled `start_lsn_sig`.

**Track 3 read differently this time.** `59D352DD` on 2026-08-04, `552673C3`
here, with `FIXUP_ATOM: 20` and AccurateRip v1/v2 both `not found` where the
earlier rip verified it. Nothing changed in the software between the two rips
that touches audio; this is the disc or the drive, and it is the reason
"14/14 bit-perfect" is a statement about one rip and not a property of a disc.

**Track 5 read the same way twice.** Identical CRC on both sessions, `FIXUP_ATOM:
4` both times, AccurateRip missing both times, and — from EAC's own audio for
that track — differing from EAC while agreeing with it on the sector-450
window. A stable, localised difference, not a random read error.

## What it is not evidence of

- **The securing pass did not finish, and the operator cancelled it.**
  `platterpus.json`'s capture records *"rip cancel requested by the user"* at
  00:29:00, after cyanrip had already finished at 00:18:14. The EAC-compatible
  log's `Secure re-read: the securing pass was INTERRUPTED` is **correct** and
  is about Platterpus's own pass, not a misreading of cyanrip's per-track
  `Secure re-read: not attempted` (which is right: no `-Z` was passed).
  This was nearly filed as a defect in their output. It is not one.
- **No `-Z`, no `-x`, no `-j`, no `-f`.** Those surfaces are untouched by this
  session, as they were by the previous two.
- **`-x` has still never executed on a real drive, anywhere.**
