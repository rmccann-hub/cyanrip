# Rig session 2026-11-17b, the overread probe's lead-out log

**What this is.** These are the log and CUE sheet of the overread probe's first rip: track 14 at
+667 with `-O`, which `.34` wrote to `overreadleadout/`. The owner delivered them after the probe
itself was filed, at `1a16efe` in `docs/rig-2026-11-17b-overreadprobe/`. That folder's README
lists them as possibly missing. The evidence branch only gains files and a filed folder never
changes, so they are filed here, beside it, byte for byte as delivered. `SHA256SUMS` gives each
file's hash.

## What it establishes

1. **The log is the program's own, unedited.** `cyanrip -Y` reports its FUN512 checksum valid. It
   names the run: `Invoked as:` gives `-N -s 667 -l 14 -O -D overreadleadout`, the
   `--diagnostics` file of 22:58:25Z, and `Ripping finished at 2026-11-17T17:59:38-05:00`.
2. **It holds what the runner's transcript holds of that step.** Taken as sets of lines, the two
   differ only by these:
   - **Lines only the log has:** its two pre-log markers (`--- output before this log was opened
     ---`, `--- end of pre-log output ---`) and its `Log FUN512:` line.
   - **A line only standard output has:** `Flushing encoders...`.
   - **What the runner left out:** the progress redraws it folds and its own `argv:`, `cwd:` and
     `exit:` lines.

   So the reading of `docs/rig-2026-11-17b-overreadprobe/` stands on the log itself for this rip:
   `Beyond disc: 2 of 2 frames refused (written as silence)`, EAC CRC32 `787BA2D6`, and
   `Ripping errors: 0`.
3. **The CUE sheet** names one file, `14 - Unknown track.flac`. It gives `TRACK 14` with ISRC
   `GBAAM9500177` and `INDEX 01 00:00:00`, and its `REM COMMENT` names `.34`.

**Still not delivered:** the lead-in rip's log, in `overreadleadin/`, and both rips' diagnostics
records.
