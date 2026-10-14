# Rig session 2026-09-11, build `ddc1e8c` — Run A, round 16's close condition

```
ripper      cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-gddc1e8c)
drive       PIONEER  BD-RW   BDR-209D (revision 1.51)
script      tools/rig-round16.sh, graded by tools/round16-accept.py at 9ec722e
```

Run A of round 16: our script driving cyanrip directly on test pin `ddc1e8c`,
with no Platterpus in the loop. Its rips, named by their `-L`, are `accurip`
(tracks 1 to 3, FLAC, with the AccurateRip lookup), `hdcd-deemph` and
`hdcd-nodeemph` (track 1, PCM, `-H` with `-E` and with `-W`), and `plain`
(tracks 1 and 2, FLAC and PCM, `-Z 2`, with its `-j` record `plain.json`).
`accurip-probe` left a stdout and an exit code and no log. Every `.exit` file
reads 137, because the script's timeout killed the distrobox wrapper while the
rips ran on to the end; `docs/SETTLED.md` has the measurement.

Graded at the time, the run met round 16's close condition with 0 FAIL and
0 UNPROBED. The audio was not filed, so this copy grades with clause 2
UNPROBED. Filed at `a03c7a6`. It is not `docs/rig-2026-09-11-ddc1e8c/`, a
Platterpus session the same day.

**Where the files are.** This README was added on 2026-10-14, before HR-2's
move (`docs/handshake/PROTOCOL.md` §17), to be this folder's index on the
default branch. The other files are run evidence: from this repository's move
they are on the `evidence` branch, and `docs/evidence-manifest.tsv` gives each
one's size, SHA-256 and evidence commit. `tools/evidence.py` reads them.
