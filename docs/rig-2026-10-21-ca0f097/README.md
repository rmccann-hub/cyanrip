# Rig session 2026-10-21 — build `ca0f097`, Platterpus 0.7.112, **Full**, the reference disc

**Read the build, not the date.** This is `ca0f097`, `+platterpus.26`, the
build round 36 reviews since its release moved the round's pin on 2026-10-21,
through Platterpus **0.7.112** (`v0.7.112`), whose `PIN_UNDER_REVIEW` is
`ca0f097`. Eight logs open with `cyanrip 0.9.4-rc3+platterpus.26
(platterpus-fork-gca0f097)` and read `Handshake: round 36 lap 4 OPEN, verdict
OPEN -- released build`. Two, the timed rip's `timing A1` and `timing A2`, are
`.25` at `5f1d036`, installed for that step only.

**It is round 36's test**: the Full run of our lap 1 S18, on `.26` with
0.7.112, with `.25` timed against `.26` on tracks 1 to 3 (section P5, L1612 on).
`tools/ingest-bundle.py --peer` reads 0.7.112 as the newest tag when the run
began, 11:35:05Z. It reads the ripper as two builds, which a timed rip of two
builds is; `.26` is `release_seq` 37, the newest ledger row. Three more runs of
the same pair followed on three other discs:
`docs/rig-2026-10-21b-ca0f097/`, `docs/rig-2026-10-22-ca0f097/` and
`docs/rig-2026-10-22b-ca0f097/`.

**The script's verdict is not a pass**: pass 424, fail 60, error 0, skipped 0,
blocked 0, unreachable 1, info 12, `ok: false`, `counts_as_evidence: true`,
run size full (`session/run/report.json`). **None of the 60 is a ripper
failure.** Three causes:

- **55, L782 to L1086, are rips the app would not start.** From L782 no tracks
  were loaded and the Start button was disabled, and at L793 a `Pick a
  MusicBrainz release` dialog stood open that the script did not expect
  (`session/transcript.txt:503-516`). Sections H to the derived-wavpack rip
  failed in that state; the derived-wav section (L1097) ran.
- **3 are the album audit's cue check, L726, L1109 and L1274**:
  `cue_integrity warned: cue sheet — 14 ISRC(s) differ from what we sent`,
  track 1 `cue GBAAM7800003 vs sent GBAAM0201086`. The cue carries the disc's
  own code under `--prefer-disc-isrc`, which the run sends, because `.26`'s
  disc read returns codes on this drive (below). That is the option working,
  and Platterpus's check expects the code it sent.
- **2 are the app's tag and cover checks**, L729 and L730.

The unreachable step is section E2 (L571), as on every run on this drive.

**Every member matches the sender's own hash**: `tools/ingest-bundle.py`
checked each of the 100 members the bundle's `MANIFEST.txt` hashes against
it, and all 100 match byte for byte.

**Filed under the names it was delivered with.** `tools/ingest-bundle.py
--into` filed 46 members and named 55 it did not file, each in `SHA256SUMS`:
the audio, the screenshots, the `--diagnostics` records, the
`.platterpus.json` files and the app-log rotations. **Nothing needed
replacing**: no filed file carried a home path. The owner's name was not
checked, because no local list of names exists here, and not checked is not
the same as not present.

| | |
|---|---|
| bundle | `platterpusbundle20261021t113505z.tar.gz`, handed over by the operator on 2026-10-25 |
| sha256 | `719afa529a01067d6363e11932ee38bd1696f0a8ec3fbcc2d180014d44be86f6` |
| size | 7,368,024 bytes, 101 members, 100 of them hashed in its `MANIFEST.txt` |
| session | `20261021T113505Z`, `started_at` 11:35:05Z, ended 13:43Z at the earliest |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| disc | the reference disc, 14 tracks, `AccurateRip ID: 001d420f-013bb370-e20dfe0e` |

## What it shows

What `.26`'s Changelog asked the run to cover, first:

- **1. The three lines.**
  - `Accurate stream: declared supported by drive (capabilities page, not
    measured)` is in every `.26` log.
  - **`Recordable:` reads `unknown (profile 0xffff is not a CD profile)` in
    every `.26` log, 8 of 8, and that is a defect.** `.26` takes the profile from
    libcdio's `mmc_get_disctype()` (`cyanrip@ca0f097:src/cyanrip_main.c:326`).
    That function sets `0xffff`, `CDIO_MMC_FEATURE_PROF_NON_CONFORM`, before it
    searches GET CONFIGURATION's profile list for the current profile. Its loop
    stops 4 bytes short of the list's end, `q < p + profiles_list_length` with
    `q` starting at `p + 4`, so the list's last descriptor is never read. A
    drive lists its profiles from the highest number down, so CD-ROM, `0x0008`,
    usually comes last. The `0xffff` is libcdio's default, not the drive's
    answer, and the line states it as the drive's profile. It is the same in
    every libcdio from 2.1.1 to master `68ea374`
    (`lib/driver/mmc/mmc_hl_cmds.c`).
    All 30 `.26` logs of the three other runs read the same, on three more
    discs.
  - **The two-search clause did not print**: no `Gaps:` list says `two
    searches read`.
- **2. `Gaps:` on this disc.**
  - **Track 4 reads 158 frames in all ten logs**, both builds.
  - **Track 9 is where `.26` differs from `.25` and from EAC.** Both `.25` logs
    read 94 frames. So did ten of round 35's twelve `.25` logs
    (`docs/rig-2026-10-20-5f1d036/`), and so does EAC's log of this disc on
    this drive, `Pre-gap length 0:00:01.25`
    (`platterpus@bba81563:output_reference/EAC_flac/eac_baseline_police_classics.log:162`).
  - **No `.26` log reads 94.** Three read 95: the derived-wav rip, the secure
    re-read and the first rip's securing pass. Five read `pregap of track 9
    unknown (sub-channel CRC mismatches)`: the whole-disc rip, both
    pre-emphasis rips, and `timing B1` and `B2`.
  - `.26`'s Changelog said every log of this disc would read 94.
  - The `unknown` names CRC mismatches as its cause, but the search reaches
    that arm whenever its bounds fail to meet
    (`cyanrip@ca0f097:src/pregap.c:663-673`). That includes frames that pass
    their CRC and answer for another sector, which `.26` asks for again
    (`:654`). The log does not say which happened.
- **3. The disc ISRC read works on this drive.**
  - Every `.26` track block reads a code from the track's own Q frames, where
    libcdio returned none.
  - The 14 codes match EAC's cue of this disc, 14 of 14, track 1 `GBAAM7800003`
    to track 14 `GBAAM9500177`
    (`platterpus@bba81563:output_reference/EAC_flac/eac_baseline_police_classics.cue`).
  - The two `.25` logs read `none (libcdio returned none)` for tracks 1 to 3,
    as `.25` always has here.
- **4. The timed rip: `.26` read tracks 1 to 3 in a third of `.25`'s time.**
  - Platterpus's L1656 gives `B1/A1 = 0.348` (246.96 s against 709.05 s) and
    `B2/A2 = 0.346` (245.90 s against 709.72 s); the two agree within 0.002
    (`session/transcript.txt:2206-2209`).
  - The logs' `Extraction speed:` reads 0.90x to 0.96x for `.25` and 2.6x to
    2.8x for `.26`.
  - Tracks 1 and 2 verify whole in all four.
  - **Track 3 verifies in both `.25` rips and in neither `.26` rip**
    (`D7314554` and `2363932F`, each matching only AccurateRip's one-frame
    entry). This disc's track 3 reads wrong at every speed on every build:
    - `.25` read `3D8FCF0C` at 0.96x on 2026-10-20 (`docs/rig-2026-10-20-5f1d036/`);
    - `.23` read four wrong values at 0.23x and 1.2x on 2026-10-16;
    - `.22` read four wrong values on 2026-10-13;
    - in this run, `.26`'s securing pass read it right at 0.99x and its secure
      re-read converged wrong at 0.74x.
  - Two rips a side cannot separate the build from the disc.

And the rest, as regression checks:

- **All ten cyanrip logs verify with `-Y`** and end in a signed footer: nine
  `.log` files and the first rip's securing pass. Every one reads `Ripping
  errors: 0` and `Read stalls: none (no read exceeded 10s)`.
- **AccurateRip**: the whole-disc rip and the secure re-read read `Tracks
  ripped accurately: 12/14` and `Tracks matched on one frame only: 2/14`,
  tracks 3 and 5, as on every run of this disc.
- **The secure re-read** (`-Z 2`): 13 tracks converged after 3 reads and track
  3 after 4. Two converged on a wrong value: track 3 on `3D8FCF0C`, the fifth
  filed `-Z` rip to do so, and track 5 on `6902BCF0`. The first rip's
  securing pass (`-Z 2 -l 3,5`) converged on `59D352DD` for track 3, which
  AccurateRip matches whole.
- **No read hit the repeat limit**, and no pregap search printed `pregap of
  track N unknown` for any reason but the one above.
- **All ten logs ask for a `--diagnostics` record, and the bundle has each**,
  `cyanrip-diagnostics/10`. Every `error_positions` is empty, and each record's
  exit code is 0.
- **Both pre-emphasis rips name their caller**, `Consumer: platterpus/0.7.112`.
  Round 35's `r16deemphon` named none, for a cause in Platterpus's runner
  (our round 34 lap 3 S22), so that is fixed on their side.
- **`-f` found `+667` at confidence 14** (`session/transcript.txt:1212`).
- **The cache probe said `128 to 255 sectors`** (uncached read 363.1 ms,
  cached 1.3 ms, `session/transcript.txt:1282`), beside `cd-paranoia -A`'s
  140 (`session/transcript.txt:1500`).

**It shows two defects in what `.26` changed, and neither is in the audio.**
- **`Recordable:`** cannot answer on this drive, for a libcdio loop that never
  reads a CD drive's last profile.
- **The pregap search** read the reference disc's track 9 as 95 or unknown,
  never the 94 that `.25` and EAC read. Its `unknown` gives a cause the code
  cannot tell apart from another.

A pregap here merges into the track before it (`merging into track 8`), so
it moves no sample between files. It changes the cue's `INDEX 00`
and the log's `Gaps:` list. Every rip's AccurateRip result is as on
`.25`.

What `.26` changed and the run shows working:
- the disc's ISRCs, 14 of 14 matching EAC;
- the media-change query, a third of `.25`'s time on tracks 1 to 3;
- `Accurate stream:`.

Our round 36 lap 5 S20 said our first lap after this run is `GO` unless the
run shows a defect in `.26` that makes the pin unsafe, or the three lines, the
pregap search, the disc ISRC read or the timed rip show one, and names it. Two
of those show one, and the lap names them.

**Every fact above can be re-derived** with `tools/read-run.py
docs/rig-2026-10-21-ca0f097 --cyanrip build/src/cyanrip`, beside
`tools/ingest-bundle.py`'s verdict on the bundle itself. The `--diagnostics`
records are in the bundle, whose `SHA256SUMS` names each.
