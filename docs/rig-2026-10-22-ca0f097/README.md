# Rig session 2026-10-22 — build `ca0f097`, Platterpus 0.7.112, **Full**, disc 3 of a set

**Read the build, not the date.** This is `ca0f097`, `+platterpus.26`, the
build round 36 reviews, through Platterpus **0.7.112** (`v0.7.112`). Fifteen
logs open with `cyanrip 0.9.4-rc3+platterpus.26 (platterpus-fork-gca0f097)`.
Two, `timing A1` and `timing A2`, are `.25` at `5f1d036`, for the timed rip.
It is the third of four runs of that pair, on disc 3 of the four-disc set
whose disc 1 is `docs/rig-2026-10-21b-ca0f097/`. `tools/ingest-bundle.py
--peer` reads 0.7.112 as the newest tag when the run began, 11:45:15Z, and
the ripper as two builds, as a timed rip is.

**The script's verdict is not a pass**: pass 480, fail 4, error 0, skipped 0,
blocked 0, unreachable 1, info 12, `ok: false`, `counts_as_evidence: true`,
run size full (`session/run/report.json`). **None of the four is a ripper
failure.**
- L726 and L1274, the album audit, warn that `the ripper reports the rip
  completed with 1 ripping errors` and `2`: track 16 is damaged, below, and
  the audit says so.
- L730 and L910 are the app's cover check, `the report says 0 file(s) took
  the cover; the files hold 16` and `2`.

The unreachable step is section E2 (L571), as on every run on this drive.

**Every member matches the sender's own hash**: all 136 members the bundle's
`MANIFEST.txt` hashes match it byte for byte.

**Filed under the names it was delivered with, with ten home paths
replaced.** `tools/ingest-bundle.py --into` filed 71 members and named 66 it
did not file, each in `SHA256SUMS`. Two filed files, the whole-disc rip's and
the secure re-read's `.platterpus-verified-read.txt`, carried five home-folder
paths each, which `tools/redact.py` replaced with `~`. No hostname was found.
The owner's name was not checked, because no local list of names exists here,
and not checked is not the same as not present.

| | |
|---|---|
| bundle | `platterpusbundle20261022t114515z.tar.gz`, handed over by the operator on 2026-10-25 |
| sha256 | `3e290b93b1f08f3fdf3aa21b823bdb22f93190b4ea5cdeee615f63500ee8b7db` |
| size | 7,678,567 bytes, 137 members, 136 of them hashed in its `MANIFEST.txt` |
| session | `20261022T114515Z`, `started_at` 11:45:15Z, ended 14:41Z at the earliest |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| disc | disc 3 of 4, 16 tracks, 57:47.65, `AccurateRip ID: 002086bf-0189efd1-f80d8b10` |

## What it shows

- **Track 16 is damaged, and paranoia skipped on it.**
  - The whole-disc rip reads `Ripping errors: 1 (including 1 paranoia skip)`,
    at LSN 248743, 3,608 sectors into the track.
  - Its securing pass (`-Z 2 -l 16`), the secure re-read (`-Z 2`) and that
    rip's securing pass each **hit the repeat limit on track 16**, five
    different checksums in five reads. Each kept the newest, which is the
    last, so the clause naming a last read not kept rightly did not print.
  - Those three passes read 2, 2 and 1 skips, all between LSN 250364 and
    251158, each in its `--diagnostics` record as `kind: skip`.
  - Track 16 matches only AccurateRip's one-frame entry in every whole-disc
    log: `Tracks ripped accurately: 15/16`, `Tracks matched on one frame only:
    1/16`.
- **The three lines.**
  - `Accurate stream: declared supported by drive (capabilities page, not
    measured)` in every `.26` log.
  - `Recordable: unknown (profile 0xffff is not a CD profile)` in every `.26`
    log, 15 of 15: the defect `docs/rig-2026-10-21-ca0f097/` describes.
  - No two-search clause printed.
- **`Gaps:`: ten pregaps, the same in every log, both builds**, and one
  difference.
  - **Three `.26` logs read `pregap of track 16 unknown (sub-channel CRC
    mismatches)`**: `cancel me`, `derived wavpack` and `r16deemphon`.
  - The other twelve `.26` logs and both `.25` logs find no pregap there. The
    whole-disc rip reads `Pregap length: 0 frames`, `Pregap source: sub-channel
    (not signalled by TOC)`.
  - The skips are thousands of sectors later in the track, so the main
    channel's damage does not explain it. The log cannot say whether the
    frames failed their CRC or answered for other sectors, the same
    uncertainty as the reference disc's track 9.
- **Every track's `Disc ISRC:` says what the Q frames showed**: `none (libcdio
  returned none, also after reading 200 Q frames of the track, none an ISRC
  frame)` in every `.26` track block. This disc carries no ISRC in its
  sub-channel, as far as 200 frames of each track can say. The `.25` logs read
  `none (libcdio returned none)`.
- **The timed rip: `.26` read tracks 1 to 3 in about a third of `.25`'s time.**
  - Platterpus's L1656 gives `B1/A1 = 0.354` (247.35 s against 697.84 s) and
    `B2/A2 = 0.354` (247.03 s against 697.94 s), agreeing within 0.001
    (`session/transcript.txt:2179-2182`).
  - All four rips verify tracks 1 to 3 whole, `Tracks ripped accurately: 3/16`.
- **The cancel step exits 143**: `cancel me` reads `Rip completed:  no
  (interrupted by SIGTERM, 1 of 16 tracks)` and `Ripping errors: 1`, with no
  skip, and its record has `exit_code` 143.
- **All seventeen cyanrip logs verify with `-Y`** and end in a signed footer:
  fifteen `.log` files and two securing passes. All seventeen ask for a
  `--diagnostics` record, the bundle has each, and every one is
  `cyanrip-diagnostics/10`. No read stalled past 10 s.
- **`-f` found `+667` at confidence 16** (`session/transcript.txt:1204`).
- **The cache probe said `128 to 255 sectors`** (uncached read 381.2 ms,
  cached 1.4 ms, `session/transcript.txt:1275`), beside `cd-paranoia -A`'s
  140 (`session/transcript.txt:1477`).

**It shows the two defects the reference disc's run shows.**
- `Recordable:` on every `.26` log.
- The pregap search's `unknown`, here on a track every other search reads as
  having none, three times in fifteen `.26` logs.

It shows the repeat limit and paranoia skips on a drive again, the timed rip
agreeing with the reference disc's, and no defect in the audio.

**Every fact above can be re-derived** with `tools/read-run.py
docs/rig-2026-10-22-ca0f097 --cyanrip build/src/cyanrip`, beside
`tools/ingest-bundle.py`'s verdict on the bundle itself. The `--diagnostics`
records are in the bundle, whose `SHA256SUMS` names each.
