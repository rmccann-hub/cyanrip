# Rig session 2026-11-24: round 42's second Full run, `.35` through Platterpus 0.7.129

**What this is.** Round 42's Full run, the second of two. It is the run G3 files (our lap 1
S32). The owner ran Platterpus 0.7.129's `--run-script fullacceptance` on the BDR-209D and the
reference disc from 2026-11-24 09:38:25Z. Its steps' times add up to 16:02:37Z, and its bundle
was written at 16:04:14Z.

**Where it comes from.** This folder joins two deliveries:

- **The run's bundle,** `platterpusbundle20261124t0938250000.tar.gz` (sha256
  `88dcdc22c43bb48772185a834090356e847a247a20283c904dc12b828a453779`, 4,450,517 bytes).
  - **Integrity.** All 63 members its `MANIFEST.txt` lists match the sender's hashes.
  - **Filed** by `tools/ingest-bundle.py` as delivered: `applog/`, `scriptrips/` and
    `scriptrun/`.
  - **Not filed,** with their hashes in `SHA256SUMS`: the 30 screenshots, and `applog/log.txt.1`.
    That log is byte-identical to the copy filed with the C2 probe at `b263e0e`
    (`docs/rig-2026-11-24b-c2probe/applog/log.txt.1`, sha256 `1326658e…`).
  - **What it lacks.** Its manifest says `album folder (none)`: Platterpus's in-app bundle carries
    no whole-disc rip's log, CUE sheet or record.
- **The rip folders,** collected by the owner from `~/Music/rips` because the bundle has none, as
  `platterpusfullruns42-rips.tar.gz` (sha256
  `ce279f9797697292a9f0143f8a037b936f3f19800187724493a9b3d0c26f15cd`, 5,315,269 bytes).
  - **Scope.** Every `.log`, `.cue`, `.json`, `.txt`, `.md5`, `.sha256`, `.toml` and `.md` file
    written between 2026-11-23 23:49Z and 2026-11-24 16:05Z, which covers both Full runs.
  - **This run's share,** told apart by its album stamp `20261124t093825` and its records'
    times: 27 album folders (121 files) under `album/`, and 96 records under
    `ripperdiagnostics/`.
  - **Not here.** The archive's `r16deemphon/` and `r16deemphoff/` are byte-identical to the
    bundle's `scriptrips/` copies, so they are not filed twice.

**Checks.**

- **Signatures.** All 34 signed cyanrip logs, 27 `.log` files and Platterpus's 7
  securing-pass and verified-read copies, verify with `-Y` on the delivered bytes and as filed.
  So do the bundle's 2 script rips.
- **Personal details.** `tools/redact.py` replaced 12,786 home paths in the rip folders, all
  outside the signed logs. Platterpus's bundle had already written its own as `~`. No hostname
  was found, and the owner's name was not checked, for want of a local list.
- **Hashes.** `SHA256SUMS` gives each file's filed hash, and the delivered hash where one
  changed.

**Read the build, not the date.**

- **The pair.** Every `.35` log's banner is `cyanrip 0.9.4-rc3+platterpus.35
  (platterpus-fork-g1280aa4)`, with `Consumer: platterpus/0.7.129`.
- **The `.34` logs.** Six are `.34` (`gfb28088`): the script's A-arm timing and accuracy rips,
  which install `.34` on purpose.
- **The newest pair.** The ingest reads `.35` and 0.7.129 as the newest pair when the run began.
- **The verdict.** `pass 650, fail 1, unreachable 1, info 23`; the run did not pass
  (`scriptrun/report.json`).

## What it establishes

1. **G1: one default whole-disc rip of `.35` with all 14 tracks AccurateRip-verified, each
   record saying how, and its `Disc MCN:` line.** The section F rip, `album/full acceptance∶
   angle‹bracket 20261124t093825 platterpus-fork-g1280aa4/`, does all of it:
   - **The read.** Its log reads `Tracks ripped accurately: 13/14` and `Ripping errors: 0`.
     Track 3 is `59D352DD`, matched by AccurateRip v1 at confidence 128 and v2 at 200.
   - **Track 5's read** is `6902BCF0`. AccurateRip's v1 and v2 do not find it; its frame-450
     checksum matches at confidence 200.
   - **The securing pass** read track 5 five times as `E0036697`. Its `Done;` line reads
     `agreement on E0036697 overruled by AccurateRip`, so nothing it read was kept.
   - **Platterpus's chase** read track 5 15 times, all `E0036697`.
   - **The record says how track 5 was verified.** It keeps the read's `copy_crc 6902BCF0` with
     `accuraterip_verified: false`, and its diagnostics say `CTDB repair repaired: track(s) 5
     rewritten toward entry 32115 (1,436 submissions)`.
   - **The repaired audio.** Platterpus's step reads it as `verified by AccurateRip v2 BCF4E815
     (confidence 200)` (`scriptrun/transcript.txt`, L789). That is the same audio and checksum
     round 41's repair reached. The repair and that reading are theirs.
   - **`Disc MCN:       none (libcdio returned none)`.** This is HW-19's first answer from a
     drive.
   - **So G1 holds as round 41's G2 did.** Thirteen tracks are verified from the drive's read
     and track 5 by its labeled repair.
2. **A whole-disc rip of `.35` with every track verified from the drive's reads,** repeat rip 4.
   - **The pass.** Its securing pass (`-Z 2 -l 3,5`, with `--reread-until-accuraterip`) read
     track 5 four times: `E0036697`, `C96464AB`, `E0036697`, `E0036697`. It kept read 2,
     `C96464AB`, matched by AccurateRip v1 `134C0B9D` at confidence 129 and v2 `BCF4E815` at 200.
   - **The log's line.** `Done; (read 2 matches AccurateRip at confidence 200; agreement on
     E0036697 overruled by AccurateRip; kept C96464AB, read 1 time)`.
   - **What it shows.** `.31`'s rule kept, on a drive, the one read AccurateRip matches over
     three reads that agreed.
   - **Nothing repaired.** Platterpus's record repairs nothing there (`repaired from CTDB:
     none`, L1944).
   - **A first for rounds 41 and 42.** No other filed read of track 5 in either round is
     `C96464AB`. Round 41's reading found every read `E0036697`
     (`docs/rig-2026-11-17-fb28088/README.md`).
3. **G2's `C2 errors:` half.** All 34 logs, `.34` and `.35`, print
   `C2 errors:      not declared by drive (capabilities page, not measured)`.
   - **What the drive does.** The C2 probe of the same day shows it returning C2 pointers at
     track 5's LBA 83430 and track 3's seconds 251 and 252 (`docs/rig-2026-11-24b-c2probe/`).
   - **So the line is true but incomplete.** The capabilities page does not declare C2, and
     cyanrip did not measure it.
   - **The records** carry no C2 count, because cyanrip reads no C2 (HW-1).
4. **Every `.35` log prints `Disc MCN:`, all 28 of them**, each as
   `none (libcdio returned none)`. The six `.34` logs print no such line, as `.34` did when the
   drive gave no code.
5. **The rest of the run reads as `.35` should.**
   - Every log ends with `Ripping errors: 0`.
   - Every log says `Rip completed:  yes`, but the one the script cancels:
     `no (interrupted by SIGTERM, 1 of 14 tracks)`.
   - Every log that asks for a record has it under `ripperdiagnostics/`.
   - Track 9's pregap is `94 or 95 frames (undecided)` in 30 of 34 `Gaps:` lists, and decided
     in the other 4 (HW-6).
6. **The run's one failure** is Platterpus's `expect-ctdb whole` on the secure re-read rip
   (`scriptrun/transcript.txt:1210`). Its track 5 matches only a CTDB minority, 2 of 1,538
   submissions, as in round 41's run and the three before it.
7. **The cache probe** reads `uncached read 362.6 ms, cached read 1.5 ms`, against
   `cd-paranoia -A`'s 140 sectors (`scriptrun/transcript.txt:1361`, `:1514`).

## What it does not establish

- **That any track 5 read but repeat rip 4's is the pressing.** `E0036697` and `6902BCF0`
  disagree with AccurateRip. Only `C96464AB` matches it.
- **That the C2 flags at LBA 83430 mark the samples CTDB's majority disagrees with.** The probe
  dropped its audio. That frame and CTDB's three samples at 02:24:59 fall in the same place, but
  their bytes have not been compared.
- **Anything about the first Full run.** That run is filed beside this one
  (`docs/rig-2026-11-23-1280aa4/`).

## Questions, gaps and next time

**Questioned:**
- **The in-app bundle's missing album folder** (`MANIFEST.txt`, `album folder (none)`).
  - **Why it matters.** A Full run's bundle is the file the operator is told to send, and G1 is
    read from the logs it leaves out.
  - **Round 41 had them.** Its rig-harness bundle carried 96 album files and 43 records.
  - **Owner.** Theirs; our next lap reports it.
- **The first run's bundle, deleted by Platterpus's prune before it was sent** (R42-1). Theirs.

**Possibly missing:**
- **The screenshots.** 30 are named in `SHA256SUMS` and not filed, as for earlier bundles.
- **The first run's `r16deemphon/` and `r16deemphoff/` logs.** This run's overwrote them on
  disk, so only this run's pair exists.

**To add next time:**
- **The in-app bundle to carry its run's album folders and records,** as the harness's did.
  Theirs.
- **Each run's scripted rip folders under the run's own stamp,** so a second run does not
  overwrite the first's. Theirs.

**More than we asked:**
- **Repeat rip 4** (point 2): `--reread-until-accuraterip` choosing the matching read on a
  drive.
- **The de-emphasis pair.** Both arms read track 1 identically (`5D3C90CB` / `22B9924D`), each
  verified by AccurateRip, so R185's two-arm grading did not come up.
