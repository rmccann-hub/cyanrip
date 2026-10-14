# Rig session 2026-08-05, build `f5e11ba`, with Platterpus 0.6.4b8

```
ripper      cyanrip 0.9.4-rc1+platterpus.5-beta.4 (platterpus-fork-gf5e11ba)
consumer    Platterpus 0.6.4b8 (build 38c178f)
drive       PIONEER  BD-RW   BDR-209D (revision 1.51)
disc        The Police - Every Breath You Take: The Classics, 14 tracks
finished    Ripping finished at 2026-08-05T01:30:58, Rip completed: yes (14 of 14 tracks)
```

A Platterpus-driven rip of the reference disc, the second run of beta.4 on
hardware; the first, with Platterpus 0.6.4b7 the same day, is
`docs/rig-2026-08-05/`. Platterpus re-ripped tracks 3 and 5 after the rip, and
`platterpus-addendum.txt` gives the values of the files that replaced them, so
for those two tracks it supersedes `cyanrip.log`. Filed at `e40d3aa`; round 7
lap 25 cites it.

| file | written by |
|---|---|
| `cyanrip.log`, `cyanrip.cue` | cyanrip |
| `platterpus-addendum.txt`, `platterpus-eac-compatible.log`, `platterpus.json`, `platterpus-stdout.log` | Platterpus |

**Where the files are.** This README was added on 2026-10-14, before HR-2's
move (`docs/handshake/PROTOCOL.md` §17), to be this folder's index on the
default branch. The other files are run evidence: from this repository's move
they are on the `evidence` branch, and `docs/evidence-manifest.tsv` gives each
one's size, SHA-256 and evidence commit. `tools/evidence.py` reads them.
