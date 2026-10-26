# Rig session 2026-10-21b — build `ca0f097`, Platterpus 0.7.112, **Full**, a damaged disc

**Read the build, not the date.** This is `ca0f097`, `+platterpus.26`, the
build round 36 reviews, through Platterpus **0.7.112** (`v0.7.112`). Both logs
open with `cyanrip 0.9.4-rc3+platterpus.26 (platterpus-fork-gca0f097)` and read
`Handshake: round 36 lap 4 OPEN, verdict OPEN -- released build`. It is the
second of four runs of that pair: `docs/rig-2026-10-21-ca0f097/`, the
reference disc and round 36's test, ran that morning.
`tools/ingest-bundle.py --peer` reads both as the newest when the run began,
21:45:10Z: `.26` is `release_seq` 37, and `v0.7.112` is the newest tag.

**The disc is damaged, and this is the first filed rip of one with paranoia
skips on a drive.** It is disc 1 of a four-disc set (`-c 1/4`), 18 tracks,
`AccurateRip ID: 00244e5e-01e6a7bd-000dac12`. The run stopped at its first
whole-disc rip: the rip finished, and Platterpus's securing pass of tracks 11
to 18 was still reading when the script's six-hour wait ended.

**The script's verdict is not a pass**: pass 144, fail 1, error 0, skipped 0,
blocked 348, unreachable 1, info 4, `ok: false`, `counts_as_evidence: true`,
run size full (`session/run/report.json`). The failure is L664 `wait-for-rip
21600`, Platterpus's six-hour limit on one rip. That rip and its securing pass
were still running when it expired (`session/transcript.txt:421`), and the 348
steps after it were blocked. The unreachable step is section E2 (L571), as on
every run on this drive.

**Every member matches the sender's own hash**: all 35 members the bundle's
`MANIFEST.txt` hashes match it byte for byte.

**Filed under the names it was delivered with.** `tools/ingest-bundle.py
--into` filed 11 members and named 25 it did not file, each in `SHA256SUMS`:
the audio, the `--diagnostics` records and the app-log rotations. **Nothing
needed replacing.** The owner's name was not checked, because no local list of
names exists here, and not checked is not the same as not present.

| | |
|---|---|
| bundle | `platterpusbundle20261021t214509z.tar.gz`, handed over by the operator on 2026-10-25 |
| sha256 | `5a423751af670788dd6bf72bc578d716cb063cde9c60f626fbbad353c19a19f2` |
| size | 5,435,607 bytes, 36 members, 35 of them hashed in its `MANIFEST.txt` |
| session | `20261021T214510Z`, `started_at` 21:45:10Z, ended 2026-10-22T03:45Z at the earliest |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| disc | disc 1 of 4, 18 tracks, 58:20.25, `AccurateRip ID: 00244e5e-01e6a7bd-000dac12` |

## What it shows

- **The whole-disc rip completed, 18 of 18 tracks, with `Ripping errors: 2106
  (including 2106 paranoia skips)`.**
  - It took from 21:46Z to 00:19Z, about two and a half hours.
  - **Tracks 1 to 10 verify whole, and tracks 11 to 18 match only
    AccurateRip's one-frame entry**: `Tracks ripped accurately: 10/18`,
    `Tracks matched on one frame only: 8/18`.
  - The skips are on tracks 13, 15, 17 and 18 only. Tracks 11, 12, 14 and 16
    read no skip and still do not verify, so paranoia reported nothing on four
    reads that were wrong.
- **The `--diagnostics` record carries the skips' positions on a drive for the
  first time**, `cyanrip-diagnostics/10`:
  - Track 13 has 1, track 15 has 1 and track 17 has 28.
  - Track 18 has 1,000 kept, its first 500 and its last 500, LSN 242828 to
    261165, with 1,076 counted in `error_positions_dropped`.
  - That is 2,106 in all, the log's count exactly. Every one is `kind: skip`.
    **No read failed outright, so the drive never reported a failed read**,
    and that arm has still not run on a drive.
- **The stall report ran on a drive for the first time**: `Read stalls: 261
  reads exceeded 10s; longest 77s (track 18, LSN 253113)`. The record's
  `read_stalls` says the same: watched, threshold 10 s, count 261, longest 77
  s on track 18 at LSN 253113.
- **Platterpus's securing pass** (`-Z 2 -l 11,12,13,14,15,16,17,18`) **hit the
  repeat limit on tracks 11 to 17**, each `Done; (repeat limit of 5 reads
  reached; at most 1 read agreed)`.
  - Every one read five different checksums, four before the last, so the
    newest read, which is the last, was kept. The clause naming a last read not
    kept rightly did not print, and **that arm has still not run on a drive**.
  - The skips the pass reported are on tracks 12, 13, 15, 17 and 18, so on
    tracks 11, 14 and 16 the reads differed with no skip reported.
  - The pass reached track 18 and was stopped there by SIGTERM: `Rip
    completed: no (interrupted by SIGTERM, 7 of 18 tracks)`, `Interrupted at:
    track 18, mid-read`, `Partial files: 1 track (18), read not completed`. It
    exited 143.
  - Its footer printed, signed: `Ripping errors: 3390 (including 3389
    paranoia skips)`. The one that is not a skip is, as far as the record
    shows, the read the signal stopped: each cancel step of 2026-10-22 reads
    `Ripping errors: 1` with no skip, and its record has none either. `Read stalls: 347 reads exceeded 10s; longest 59s`.
  - Its record has 3,389 positions, all skips: tracks 12, 13 and 15 one each,
    track 17 142, and track 18 1,000 kept with 2,244 dropped.
- **Both logs verify with `-Y`**, the rip and the securing pass, which ended
  on a signal.
- **The three lines, as on the reference disc.** `Accurate stream: declared
  supported by drive (capabilities page, not measured)` in both logs, and
  `Recordable: unknown (profile 0xffff is not a CD profile)` in both, the
  defect `docs/rig-2026-10-21-ca0f097/` describes. No two-search clause
  printed.
- **Every track's `Disc ISRC:` says what the Q frames showed**: `none (libcdio
  returned none, also after reading 200 Q frames of the track, none an ISRC
  frame)`, 25 track blocks in all. This disc carries no ISRC in its
  sub-channel, as far as 200 frames of each track can say.
- **The two logs' `Gaps:` lists agree**, 15 pregaps each, and none is unknown.
- **No `-f` and no cache probe ran**: both are in steps the timeout blocked.

**It shows no defect in what `.26` changed, beyond the `Recordable:` line the
reference disc's run describes.** It does show what reached a drive for the
first time:
- paranoia's skips counted in `Ripping errors:` and placed in the record;
- the stall report.

A securing pass stopped mid-read by a signal after hours of reading still
signed its footer, as round 35's cancel step did.

It also shows four tracks that read wrong with no skip reported, which
AccurateRip alone caught. What did not run is a drive reporting a failed read,
and a repeat limit whose kept read is not the last.

**Every fact above can be re-derived** with `tools/read-run.py
docs/rig-2026-10-21b-ca0f097 --cyanrip build/src/cyanrip`, beside
`tools/ingest-bundle.py`'s verdict on the bundle itself. The `--diagnostics`
records are in the bundle, whose `SHA256SUMS` names each.
