# Platterpus rig session 2026-08-25, cyanrip `d9c058c` with Platterpus 0.6.25

```
session     2026-08-25T08:29:59Z (00-summary.txt)
ripper      cyanrip 0.9.4-rc2+platterpus.10 (platterpus-fork-gd9c058c)
consumer    platterpus 0.6.25 (5f374aa)
```

Platterpus's rig script, run on the drive in round 14 against our test pin
`d9c058c`. `00-summary.txt` lists each step with its command, exit code and
output file, and the files beside it are those outputs: `rip-artifacts/` holds
the text files of the newest rip (tracks 1 and 2, never the audio), and `seam/`
is what Platterpus's `--rig-check` wrote. Filed at `e932ad0` with our round 14 lap 5, which
cites it.

**Where the files are.** This README was added on 2026-10-14, before HR-2's
move (`docs/handshake/PROTOCOL.md` §17), to be this folder's index on the
default branch. The other files are run evidence: from this repository's move
they are on the `evidence` branch, and `docs/evidence-manifest.tsv` gives each
one's size, SHA-256 and evidence commit. `tools/evidence.py` reads them.
