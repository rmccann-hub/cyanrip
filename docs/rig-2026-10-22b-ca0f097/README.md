# Rig session 2026-10-22b — build `ca0f097`, Platterpus 0.7.112, **Full**, disc 4 of a set

**Read the build, not the date.** This is `ca0f097`, `+platterpus.26`, the
build round 36 reviews, through Platterpus **0.7.112** (`v0.7.112`). Thirteen
logs open with `cyanrip 0.9.4-rc3+platterpus.26 (platterpus-fork-gca0f097)`.
Two, `timing A1` and `timing A2`, are `.25` at `5f1d036`, for the timed rip.
It is the last of four runs of that pair, on disc 4 of the set whose discs 1
and 3 are `docs/rig-2026-10-21b-ca0f097/` and `docs/rig-2026-10-22-ca0f097/`.
`tools/ingest-bundle.py --peer` reads 0.7.112 as the newest tag when the run
began, 21:57:02Z, and the ripper as two builds, as a timed rip is.

**The script's verdict is not a pass**: pass 481, fail 2, error 0, skipped 0,
blocked 1, unreachable 1, info 12, `ok: false`, `counts_as_evidence: true`,
run size full (`session/run/report.json`). **Neither failure is a ripper
failure.** L726 and L1274, the album audit, warn that `cue sheet — 1 ISRC(s)
differ from what we sent: track 10: cue USZO10001709 vs sent USZ010001709`.
The cue carries the disc's own code under `--prefer-disc-isrc`, which the run
sends. The two codes differ in one character: the disc's has the letter O,
and MusicBrainz's, which Platterpus sent, has the digit zero. The blocked step
is L730, the app's cover check. The unreachable step is section E2 (L571), as
on every run on this drive.

**Every member matches the sender's own hash**: all 129 members the bundle's
`MANIFEST.txt` hashes match it byte for byte.

**Filed under the names it was delivered with.** `tools/ingest-bundle.py
--into` filed 66 members and named 64 it did not file, each in `SHA256SUMS`.
**Nothing needed replacing.** The owner's name was not checked, because no
local list of names exists here, and not checked is not the same as not
present.

| | |
|---|---|
| bundle | `platterpusbundle20261022t215702z.tar.gz`, handed over by the operator on 2026-10-25 |
| sha256 | `5a8181862074a5fc341fcea7194938e9fc2cb942cda64e6ac4571f1ffc13f249` |
| size | 7,500,158 bytes, 130 members, 129 of them hashed in its `MANIFEST.txt` |
| session | `20261022T215702Z`, `started_at` 21:57:02Z, ended 23:34Z at the earliest |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| disc | disc 4 of 4, 16 tracks, 61:34.30, `AccurateRip ID: 0024d7eb-01b5ecd5-d30e6e10` |

## What it shows

- **A clean disc, read clean.** The whole-disc rip reads `Tracks ripped
  accurately: 16/16` and `Ripping errors: 0`. The secure re-read (`-Z 2`)
  converged on all 16 tracks after 3 reads and verifies 16/16. No read hit the
  repeat limit and none stalled past 10 s.
- **The disc ISRC read works on this disc too.** Every `.26` whole-disc log
  reads a code for 13 of the 16 tracks, the same code for each track in every
  `.26` log that rips it, track 1 `USRO28102801`.
  - Tracks 4, 8 and 15 read `none (libcdio returned none, also after reading
    200 Q frames of the track, none an ISRC frame)`.
  - The two `.25` logs read `none (libcdio returned none)` for tracks 1 to 3,
    where `.26` reads codes for all three.
  - Track 10's code is `USZO10001709` in every `.26` log that rips it, where
    MusicBrainz has `USZ010001709`. A six-bit ISRC character for the letter O
    is 31 and for the digit zero is 0, five bits apart, so neither is one
    misread character of the other. The disc carries the letter. Which code
    the recording was registered under, neither the disc nor this run can
    say.
- **The three lines.**
  - `Accurate stream: declared supported by drive (capabilities page, not
    measured)` in every `.26` log.
  - `Recordable: unknown (profile 0xffff is not a CD profile)` in every `.26`
    log, 13 of 13: the defect `docs/rig-2026-10-21-ca0f097/` describes.
  - No two-search clause printed.
- **`Gaps:`: every `.26` log lists the same 14 pregaps; the `.25` logs list
  13.**
  - **Track 5's 175-frame pregap** (`Pregap source: sub-channel (not signalled
    by TOC)`, LSN 76120 to 76294) is in all thirteen `.26` lists and absent
    from both `.25` lists. Every other pregap is the same in all fifteen.
  - A search answered first by a frame of the previous track gave `none` on
    `.25`, the failure `tests/subq.c` reproduces and `.26`'s search was built
    to remove, and that fits what `.25` printed here.
  - No EAC log of this disc exists to settle it.
- **The timed rip: `.26` read tracks 1 to 3 in a fifth of `.25`'s time.**
  - Platterpus's L1656 gives `B1/A1 = 0.197` (137.15 s against 697.22 s) and
    `B2/A2 = 0.193` (134.65 s against 698.24 s), agreeing within 0.004
    (`session/transcript.txt:2179-2182`).
  - All four rips verify tracks 1 to 3 whole, `Tracks ripped accurately: 3/16`.
- **The cancel step exits 143**: `cancel me` reads `Rip completed:  no
  (interrupted by SIGTERM, 1 of 16 tracks)` and `Ripping errors: 1`, with no
  skip, and its record has `exit_code` 143.
- **All fifteen cyanrip logs verify with `-Y`** and end in a signed footer.
  All fifteen ask for a `--diagnostics` record, the bundle has each, and every
  one is `cyanrip-diagnostics/10` with empty `error_positions`.
- **`-f` found `+667` at confidence 16** (`session/transcript.txt:1191`).
- **The cache probe said `128 to 255 sectors`** (uncached read 253.6 ms,
  cached 1.7 ms, `session/transcript.txt:1262`), beside `cd-paranoia -A`'s
  137 (`session/transcript.txt:1475`).

**It shows `.26`'s disc ISRC read and its timed rip working on a second disc
that carries ISRCs, and the `Recordable:` defect again.** Its one pregap
difference from `.25` is the kind `.26` set out to fix, and no third source
says which build is right.

**Every fact above can be re-derived** with `tools/read-run.py
docs/rig-2026-10-22b-ca0f097 --cyanrip build/src/cyanrip`, beside
`tools/ingest-bundle.py`'s verdict on the bundle itself. The `--diagnostics`
records are in the bundle, whose `SHA256SUMS` names each.
