# Platterpus acceptance run 2026-08-25, cyanrip `d9c058c` with Platterpus 0.6.26

```
run         2026-08-25T21:57:21+00:00 (transcript.txt)
ripper      cyanrip 0.9.4-rc2+platterpus.10 (platterpus-fork-gd9c058c)
consumer    platterpus 0.6.26 (build 37b0789)
```

Platterpus's full acceptance run, a UI script driving the app end to end, in
round 14 against our test pin `d9c058c`. Filed here: the script's
`transcript.txt`; the bundle's `MANIFEST.txt`, which lists 174 files, of which
only these were filed; what Platterpus's `--rig-check` wrote in `rig-check/`;
and `morning-versions.txt`, a version probe collected at 2026-08-25T22:40:20Z.
Filed at `d90e73c` with our round 14 lap 15, which cites it.

**Where the files are.** This README was added on 2026-10-14, before HR-2's
move (`docs/handshake/PROTOCOL.md` §17), to be this folder's index on the
default branch. The other files are run evidence: from this repository's move
they are on the `evidence` branch, and `docs/evidence-manifest.tsv` gives each
one's size, SHA-256 and evidence commit. `tools/evidence.py` reads them.
