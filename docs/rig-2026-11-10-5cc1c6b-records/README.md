# The 26 `--diagnostics` records of 2026-11-10 — build `5cc1c6b` (`.30`), filed late

**Reworded 2026-11-12**, on the owner's word that a burn writes a disc (Platterpus's
round 39 lap 4 S10): round 39's five back-to-back rips are the five-rip run here. The
evidence's folder names keep the word their runner gave them.

**What this is.** These are the cyanrip records of the Full run of 2026-11-10,
filed on 2026-11-11 from the same bundle as `docs/rig-2026-11-10-5cc1c6b/`
(archive sha256 `985ac7d9…`). That bundle carried them under
`ripperdiagnostics/`, and `tools/ingest-bundle.py` dropped all 26 when the run
was filed, since it filed no `.json` that was not a verdict file. The tool
files cyanrip records by their schema from `b6e7755e`, and this folder is that
filing. Evidence folders only gain files, so they could not join the run's own
folder. `SHA256SUMS` gives each record's hash; none needed a personal detail
replaced.

## What it establishes

1. **The records exist for that run, contrary to our round 39 lap 1 S9 and
   S10,** which said no record of 2026-11-10 was filed and asked Platterpus to
   bundle them. They had, and we dropped them.
2. **Track 3's per-second CRCs:** `59D352DD` is kept in 3 records and
   `3D8FCF0C` in 6, and they differ in one second, 251 (04:11). That is the
   second the 2026-11-11 five-rip run's `3D8FCF0C` differs in
   (`docs/rig-2026-11-11-e531a33/README.md`). Each of the three values here
   has the same per-second CRCs as the same value in the five-rip run's records.
3. **Track 5:** `E0036697` is kept in 3 records and no other value appears.

## What it does not establish

- Anything about the run beyond these records: the run's reading is
  `docs/rig-2026-11-10-5cc1c6b/README.md`.

## Questions, gaps and next time

**Questioned:** none.

**Possibly missing:** the records of 2026-11-09, which Platterpus's runner
did not collect.

**To add next time:** nothing; from `b6e7755e` every record in a bundle is filed.

**More than we asked:** nothing.
