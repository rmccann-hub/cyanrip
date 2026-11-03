# Rig session 2026-11-03 — build `3f288fb`, Platterpus 0.7.117, **Full**, the reference disc

**Read the build, not the date.** This is `3f288fb`, `+platterpus.28`, through
Platterpus **0.7.117** (`v0.7.117`, at `platterpus@104c82d2`). Nineteen logs
open with `cyanrip 0.9.4-rc3+platterpus.28 (platterpus-fork-g3f288fb)`, the two
securing-pass records among them. Six are `.27` at `5aeefc4`, installed for two
steps only: the timed rip's `timing A1` and `A2`, and the paired rips'
`accuracy A1` to `A4`. `tools/ingest-bundle.py --peer` reads 0.7.117 as the
newest tag when the run began, 02:38:30Z (the tag's date is 02:07:57Z), and the
ripper as two builds, as these two steps run.

**It is round 37's closing run**: the Full run of the reference disc on `.28`
through Platterpus's first release naming it (our lap 1 S10). It was read
against `docs/ROUND-37-READING-PLAN.md`, written before the run arrived.

**The script's verdict is a pass**: pass 553, fail 0, error 0, skipped 0,
blocked 0, unreachable 1, info 22, `ok: true`, `counts_as_evidence: true`, run
size full (`session/run/report.json`). The unreachable step is L573,
`expect-offset-refusal`, which this drive cannot reach because it is in
AccurateRip's drive list, as on every run on it.

**Every member matches the sender's own hash**: all 182 members the bundle's
`MANIFEST.txt` hashes match it byte for byte. `tools/ingest-bundle.py --into`
filed 101 members and named 82 it did not file, each in `SHA256SUMS`; the 25
`--diagnostics` records are among those named, and were read from the bundle.
**Nothing needed replacing.** The owner's name was not checked, because no
local list of names exists here, and not checked is not the same as not
present. **All 25 signed logs verify with `-Y`**, both securing-pass records
among them.

## What it shows

### Round 37's close conditions

- **No defect in `.28` makes the pin unsafe to approve.** Every log reaches
  its signed footer; every rip but the one the script cancels read every track
  it was asked for; the two wrong reads below happen on both builds, and on
  `.25` on 2026-10-28, and each log says so rather than calling the track
  verified.
- **Every unknown pregap has its own line in `Pregap searches:`, in all 19
  `.28` logs.** Track 9 is the only unknown one, in every log, with the reason
  `sub-channel search bounds did not meet`. The six `.27` logs lack the line
  and give the old reason, `sub-channel CRC mismatches`, as `.27` does.

### What `.28` changed, on a drive for the first time

- `Drive used:     PIONEER  BD-RW   BDR-209D (revision 1.51)`: the drive's
  vendor and model fields as INQUIRY returns them, padding included.
- `Speed:          default (drive not asked whether it can change speed)`:
  Platterpus passed no `-S`, so nothing was asked, and the line says that.
- `C2 errors:      unsupported by drive`, as this drive reports.
- `Accurate stream: declared supported by drive (capabilities page, not
  measured)`.
- `Recordable:     no, CD-ROM (drive's current profile)` for this pressed disc.
- `CD-TEXT:        none reported by libcdio (absent, or unreadable by this
  driver)`.
- **`Disc ISRC:` reads from the disc itself, for the first time on this
  drive**: every track of the full rip gives one, `GBAAM7800003` for track 1 to
  `GBAAM9500177` for track 14, and the record's `isrc_disc_read` says `q
  frames`. They are the original releases' codes; the `-t` values Platterpus
  passed from MusicBrainz are the 2002 ones (`GBAAM0201086` for track 1), and
  with `--prefer-disc-isrc` the disc's won, as designed. Item 8 is answered.
- The `--diagnostics` record is `/11` on every `.28` log:
  - `kept_read_began` is a string on the 55 tracks read, and null on the
    tracks a single-track rip did not read;
  - `isrc_disc_read` names `q frames` wherever the disc gave an ISRC;
  - `error_positions` is empty everywhere, as no read reported an error.
- `--reread-time-limit` is absent from every argv, as Platterpus's §1b cell
  says (`NO: read, not sent`).
- No log has `Names shortened:` or a media-change line, and none needed one.
- The album title carries `∶`, `‹` and an escaped `\:` through `-a`; every
  value is printed on its own line, and nothing broke a line.

### Track 3 and track 5: wrong reads that cluster in time, on every build

`tools/cross-rip.py` over the run's 25 logs:

| track | reads | distinct checksums | verified by AccurateRip |
|---|---|---|---|
| 3 | 21 | 8 | `59D352DD`, 14 times |
| 5 | 8 | 2 | neither; `E0036697` 7 times, frame 450 only |
| every other | 4 to 17 | 1 | yes |

- **Track 3 was read wrong in all four timed rips** (`-l 1,2,3`, 04:29Z to
  04:43Z), two on `.27` and two on `.28`, each with a different checksum and
  each matching AccurateRip on frame 450 only. It was **read right in all
  eight paired rips** (`-l 3`, 04:45Z to 04:59Z), four on each build, in the
  full rip at 02:41Z, and as the kept read of the `-Z 2` rip's repeat limit.
  Each wrong read logs `Track 3 read with no error reported.` and AccurateRip's
  `not found`; none is called verified.
- **The split does not follow the rip mode.** On 2026-10-28 it ran the other
  way: `.27`'s paired single-track rips were wrong in all four, and its timed
  rips right. `3D8FCF0C` is a wrong read of track 3 in both runs.
- **The wrong reads carry more of paranoia's jitter fixes**: `FIXUP_ATOM` 12 to
  24 in the four wrong reads, 0 to 8 in the ten right ones, at the same speed
  (2.8x to 3.1x).
- **Track 5 read `E0036697` seven times out of eight**, and the `-Z 2` rip and
  the securing pass each converged on it: two agreeing reads of a wrong value.
  It has read so since 2026-10-06, when the repeat limit first kept it over
  `C96464AB`, which AccurateRip matches.
- **What this says, and what it does not.** A read that is wrong the same way
  twice passes paranoia's verification and `-Z`'s agreement, and with C2
  unsupported nothing in the drive flags it; AccurateRip is what catches it,
  and catches it here. Nothing in this run points at cyanrip's code rather than
  the disc or the drive, and nothing rules it out: which samples differ is not
  in the bundle.

### Carried over

- Track 9's pregap: `unknown` in every log, `267 sectors asked … frames answer
  -1 sectors off; 200-retry pass ran; LSN 145567 to 145567 undecided`, as on
  `.27`. EAC and `.25` read 94 frames.
- The cache probe: `128 to 255 sectors`, uncached read 362.8 ms, cached read
  1.4 ms, three re-reads after 256 sectors at 58.7 ms or more, beside
  `cd-paranoia -A`'s 144 sectors (`session/transcript.txt:1277`, `:1430`).
- `-f`: `Drive offset of +667 found (confidence: 14)!`
  (`session/transcript.txt:1207`).
- The timed rip: `.28` over `.27`, 0.989 and 1.014, which agree within 0.05:
  `.28` reads no slower. Both read 2.6x to 4.5x, as `.27` did on 2026-10-28.
- The cancelled rip stops at `track 2, mid-read`, `Rip completed:  no
  (interrupted by SIGTERM, 1 of 14 tracks)`, and counts the interrupted track
  in `Ripping errors: 1`.
- The repeat limit: one case, track 3 of the `-Z 2` rip, `kept 59D352DD, read 2
  times, which AccurateRip matches at confidence 200`. The kept read was the
  last, so the clause naming a last read not kept is rightly absent.

## Questions, gaps and next time

**Questioned**

1. `Drive used:` keeps the drive's padding, `PIONEER  BD-RW   BDR-209D`; EAC
   prints `PIONEER BD-RW BDR-209D`. It is what the drive answered, so it is
   not wrong, but a reader matching drives across tools will need to collapse
   spaces. Every `.28` log, line 7. Settled by: Platterpus saying whether it
   wants the collapsed form. Owner: both sides, a lap.
2. Track 3 and track 5's wrong reads report `no error reported` with
   `FIXUP_ATOM` raised. Whether paranoia's fix-ups produce the difference, or
   the drive returns it, is undecided. Settled by: the samples (gap 1).
   Owner: us.
3. Platterpus's main window labels the cache line `Cache defeat:` (the
   operator's screenshot of 2026-11-03), where our log says `Cache model:`
   because the value is a model, not a measured defeat. Settled by: their
   wording. Owner: Platterpus.

**Possibly missing**

1. The audio. The bundle names no FLAC, so where a wrong read of track 3
   differs from `59D352DD` cannot be told: at the track's edges would point
   at the offset or the carry between tracks, inside it at the read. The rips
   are still on the rig, under
   `~/platterpus-rig/platterpustestsession20261103t023830z/rips/The Police/`.
   Settled by: track 3's FLAC from `timing B1` and from `accuracy B1`. Owner:
   the operator.
2. Which track a log's `Tracks matched on one frame only:` counts is not on
   that line; it takes a per-track search. Settled by: nothing needed, the
   per-track lines say it. Owner: none.

**To add next time**

1. A per-block checksum list for each kept read in the `--diagnostics` record
   (one CRC per 75 frames, a second of audio), so two rips can be compared
   region by region without the audio. Owner: us, proposed in a lap; it is a
   record field, not a log line.
2. Track 3 at a lower forced speed (`-S 4`), several times, and on a second
   drive, to separate the disc from the drive. Owner: the operator, Platterpus's
   script.
3. Track 5 cleaned and re-ripped, since it has read the same wrong value for
   four weeks. Owner: the operator.

**More than we asked**

1. The disc carries the original releases' ISRCs, which MusicBrainz's release
   does not list; `--prefer-disc-isrc` wrote the disc's.
2. `.28` reads no slower than `.27` on this drive (the timed rip's ratios).

**Every fact above can be re-derived** with `tools/read-run.py
docs/rig-2026-11-03-3f288fb --cyanrip build/src/cyanrip` and
`tools/cross-rip.py docs/rig-2026-11-03-3f288fb`, through `tools/evidence.py
run`.
