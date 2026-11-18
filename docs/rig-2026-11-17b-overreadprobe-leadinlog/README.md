# Rig session 2026-11-17b, the overread probe's lead-in log, Platterpus's copy

**What this is.** The log of the overread probe's second rip, track 1 at -667 with `-O`, which
`.34` wrote to `overreadleadin/`. Neither the owner's delivery to this repository nor
Platterpus's first filing held it (`docs/rig-2026-11-17b-overreadprobe-leadin/` says so).
Platterpus filed it on their evidence branch at `platterpus@f63869fe`, as
`docs/handshake/artifactsround41/round41overreadprobeoverreadleadin.log`: git blob `d1244f45`,
7,717 bytes, SHA-256 `f9e772f20072ee0dbb281828ea563a9e238ad007fa982a65ee3fd38d09516bce`. This is
that file, byte for byte, as HR-2 6c has a copy of the other side's evidence held on our own
branch, under the name the probe gave it.

## What it establishes

1. **The log is the program's own, unedited.** `cyanrip -Y` reports its FUN512 checksum valid. It
   names the run: `Invoked as:` gives `-N -s -667 -l 1 -O -D overreadleadin`, the
   `--diagnostics` file of 22:59:39Z, and `Ripping finished at 2026-11-17T18:01:06-05:00`.
2. **It holds what the runner's transcript holds of that step.** Taken as sets of lines, with
   the transcript's 11-space indent removed, the two differ only by these:
   - **Lines only the log has:** its two pre-log markers and its `Log FUN512:` line.
   - **Lines only standard output has:** `Flushing encoders...` and the folded progress line.

   So the reading of `docs/rig-2026-11-17b-overreadprobe/` stands on the log itself for this
   rip as well: `Underread: -2 frames`, `Start LSN: 0 (with offset: -2)`, `Beyond disc: 2 of 2
   frames refused (written as silence)`, `Accurip v1: AB78CDFB` and `v2: B75F1E79` each `not
   found`, and `Ripping errors: 0`.

**Still not held by either side**, on 2026-11-18: both rips' diagnostics records,
`cyanrip-diagnostics-20261117T225825Z.json` and `cyanrip-diagnostics-20261117T225939Z.json`, which
the runner's argv names.
