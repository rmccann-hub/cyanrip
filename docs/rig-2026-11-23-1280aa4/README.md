# Rig session 2026-11-23: round 42's first Full run, `.35` through Platterpus 0.7.129

**What this is.** Round 42's first Full run. The owner ran Platterpus 0.7.129's
`--run-script fullacceptance` on the BDR-209D and the reference disc from 2026-11-23 23:49:48Z.
The app quit at 06:16:46Z on 2026-11-24, after writing the run's bundle. Our lap 3 S7 named this
run. The second Full run of 2026-11-24 is filed beside it (`docs/rig-2026-11-24-1280aa4/`), and
that one is G3's.

**This is not the run's bundle.** Platterpus wrote `platterpusbundle20261123t2349480000.tar.gz`
and told the owner to send it. Then it deleted the file under its own keep-20 rule at
2026-11-24 12:24:01Z, before it was sent. The app log in `docs/rig-2026-11-24b-c2probe/` has
each step: `applog/log.txt.1:34817` (written), `:34819` (`SEND THIS ONE FILE`) and `:49396`
(pruned). That is R42-1. This folder joins what survived:

- **The run's session folder,** `~/.local/share/platterpus/uiscript/20261123T234948+0000`, which
  the owner uploaded as `platterpusfullrun20261123.tar.gz` (sha256
  `d07baa8e3317b69b5a0fcf3f4c18eee65f28c982797649ad92cdf4b69ecbca82`, 3,546,617 bytes).
  - **Filed** under `scriptrun/`, the name the app's bundle gives it: 27 files, among them
    `report.json` and `transcript.txt`.
  - **Not filed:** its 30 screenshots, named in `SHA256SUMS`.
  - **No sender's hash** covers it, because it is not a bundle.
- **The rip folders,** collected by the owner from `~/Music/rips` as
  `platterpusfullruns42-rips.tar.gz` (sha256
  `ce279f9797697292a9f0143f8a037b936f3f19800187724493a9b3d0c26f15cd`).
  - **This run's share,** told apart by its album stamp `20261123t234948` and its records'
    times: 27 album folders (124 files) under `album/`, and 91 records under
    `ripperdiagnostics/`.
  - **Missing:** this run's `r16deemphon/` and `r16deemphoff/` logs. The second run overwrote
    them on disk.
- **The app log,** already filed and not repeated here: `docs/rig-2026-11-24-c2probe-stopped/`
  (`applog/log.txt`, to 06:16:47Z), and `docs/rig-2026-11-24b-c2probe/` (`applog/log.txt.1`).

**Checks.**

- **Signatures.** All 34 signed cyanrip logs, 27 `.log` files and Platterpus's 7 securing-pass
  and verified-read copies, verify with `-Y` on the delivered bytes and as filed.
- **Personal details.** `tools/redact.py` replaced 12,865 home paths, all outside the signed
  logs. No hostname was found, and the owner's name was not checked, for want of a local list.

**Read the build, not the date.**

- **The `.35` logs.** 28 are `cyanrip 0.9.4-rc3+platterpus.35 (platterpus-fork-g1280aa4)`, with
  `Consumer: platterpus/0.7.129`.
- **The `.34` logs.** Six are `.34`: the script's A-arm timing and accuracy rips.
- **The verdict.** `pass 647, fail 2, unreachable 1, info 25`; the run did not pass
  (`scriptrun/report.json`). The two failures are Platterpus's `expect-ctdb whole`, at L786 and
  L1389 (`scriptrun/transcript.txt:503`, `:1210`), each on track 5's minority CTDB match.

## What it establishes

1. **The section F rip meets G1 the way round 41's rips did.**
   - **The rip.** `album/full acceptance∶ angle‹bracket 20261123t234948 platterpus-fork-g1280aa4/`
     reads `Tracks ripped accurately: 12/14`.
   - **Track 3.** Read `2363932F`, which AccurateRip does not match. The securing pass read
     `3D8FCF0C`. Platterpus's chase read it 8 times and ended on `59D352DD`, which AccurateRip
     matches at confidence 200.
   - **Track 5.** Read `E0036697`, in the rip and in its securing pass.
   - **The record.** It repairs track 5 from CTDB. Platterpus's step reads `repaired from CTDB:
     [5]; reads disagreed: [3, 5]; G2: track 5's repaired audio is verified by AccurateRip v2
     BCF4E815 (confidence 200)` (`scriptrun/transcript.txt:506`).
   - **`Disc MCN:`** reads `none (libcdio returned none)`.
2. **Every `.35` log prints `Disc MCN:       none (libcdio returned none)`, all 28,** and all 34
   print `C2 errors:      not declared by drive (capabilities page, not measured)`.
3. **The rest reads as `.35` should.**
   - Every log ends `Ripping errors: 0`.
   - Every log completes but the one the script cancels.
   - Every record a log asks for is under `ripperdiagnostics/`.
   - Track 9's pregap is `94 or 95 frames (undecided)` in all 34 `Gaps:` lists (HW-6).
4. **The cache probe** reads `uncached read 362.5 ms, cached read 1.4 ms`, against
   `cd-paranoia -A`'s 140 sectors (`scriptrun/transcript.txt:1361`, `:1514`).

## What it does not establish

- **What the bundle held beyond these files.** It is gone. Its 62 files were, by the second run's
  bundle of the same kind, the session folder, the app log and the two script rips. That is an
  inference from a sibling, not a reading of this one.
- **Anything this run's `r16` pair showed.** Its logs are gone. The transcript prints their
  output (`scriptrun/transcript.txt:1559` on).

## Questions, gaps and next time

**Questioned:**
- **The prune that deleted the deliverable** (R42-1). Theirs; our next lap reports it.

**Possibly missing:**
- **The bundle's `MANIFEST.txt`,** and with it the sender's hashes. Nothing here is checked
  against the sender.
- **This run's de-emphasis pair logs** (above).

**To add next time:**
- **The bundle the operator is told to send, protected from the prune** until it is sent.
  Theirs.

**More than we asked:** the first probe's stop at 06:17:00Z is explained by this run's app log:
a desktop window was open from 23:04:47Z to 09:38:04Z (`docs/rig-2026-11-24-c2probe-stopped/`).
