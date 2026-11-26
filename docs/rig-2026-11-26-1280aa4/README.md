# Rig session 2026-11-26: round 43's second Full run, `.35` through Platterpus 0.7.130

**What this is.** A second Full acceptance run on round 43's pair, run by the owner on the
BDR-209D and the reference disc from 2026-11-26 00:58:46Z, 32 to 40 minutes after the first
ended (`docs/rig-2026-11-25-1280aa4/`), whose bundle reached us at 00:26Z. Its steps' times add up to 05:03:56Z.

**Where it comes from.** One rig-harness bundle, uploaded by the owner on 2026-11-26:
`platterpusbundle20261126t005846z.tar.gz`, sha256
`dda141978d7e8d9994f97118ba470cefdb7231b958eaa1842ea48b8e06f81883`, 6,204,684 bytes.
- **Integrity.** All 273 members its `MANIFEST.txt` hashes match the sender's hashes.
- **Filed** by `tools/ingest-bundle.py`: 68 files under `album/` from 17 album folders, 137
  records under `ripperdiagnostics/`, 18 files under `session/`, and the bundle's
  `MANIFEST.txt`, `DIAGNOSTICS.txt` and `SOURCES.txt`.
- **Not filed,** with their hashes in `SHA256SUMS`:
  - 29 screenshots and Platterpus's 15 `.platterpus.json` reports;
  - `COMPONENTS.json`, `SETTINGS.json` and `session/artifacts/04platterpus/config.toml`;
  - an app log rotation, `session/zz-applog-rotations/03platterpus/log.txt.1`.

**Checks.**
- **Signatures.** All 24 signed files verify with `-Y`, on the delivered bytes and as filed:
  17 cyanrip `.log` files and Platterpus's 7 securing-pass copies.
- **Personal details.** `tools/redact.py` replaced nothing. No hostname was found, and the
  owner's name was not checked, for want of a local list.

**Read the build, not the date.**
- **The pair.** All 17 logs open `cyanrip 0.9.4-rc3+platterpus.35 (platterpus-fork-g1280aa4)`,
  with `Consumer: platterpus/0.7.130`. The ingest reads `.35` and 0.7.130 as the newest pair
  when the run began.
- **The verdict.** `pass 531, fail 8, unreachable 128`, `ok: False`
  (`session/run/report.json`). **The run did not pass.** Its eight failures and 128 unreachable
  steps are the first run's, step for step:
  - every failure is Platterpus's `expect-album-audit` on
    `Handshake:      round 41 lap 5 OPEN, verdict GO -- NOT a released build`, in all 17 logs
    (`docs/rig-2026-11-25-1280aa4/README.md`, point 1; our OPEN-ITEMS R43-13);
  - 127 unreachable steps are the A/B sections, skipped because Platterpus's pin and build under
    review are both `1280aa4` (L1678, L1784), and the 128th is `expect-offset-refusal` (L625).

## What it establishes

1. **What `.35` read.**
   - **Every log.** All 17 end `Ripping errors: 0` and `Read stalls:    none (no read exceeded
     10s)`, and print `Disc MCN:       none (libcdio returned none)` and
     `C2 errors:      not declared by drive (capabilities page, not measured)`.
   - **Completion.** Every log reads `Rip completed:  yes` but `cancel me`, which the script
     stops.
2. **Track 3: no read matched AccurateRip.**
   - **The reads.** In 158 reads of track 3, 99 distinct checksums, including 112 records of
     Platterpus re-reading it alone (`-chase-t03`), none is matched by AccurateRip v1 or v2.
     Every checksum of them that was looked up matches AccurateRip's frame 450 only.
   - **The repair.** Platterpus's CTDB repair rewrote track 3 in all seven whole-disc rips:
     section F, the secure re-read and repeat rips 1 to 5 (`session/transcript.txt:515-519`,
     `:1234-1238`, `:2288-2386`).
   - **Against the first run.** That one read track 3 as `59D352DD`, which AccurateRip matches,
     in two rips. No read here has that checksum.
3. **Track 5: `--reread-until-accuraterip` kept the matching read every time.**
   - **The loops.** All 7 repeat loops that read track 5 kept `C96464AB`, matched by
     AccurateRip v1 `134C0B9D` at confidence 129 and v2 `BCF4E815` at 200. The first run's
     loops kept it in 5 of 8.
   - **Repeat rip 4's line** also names its last read: `kept C96464AB, read 1 time, which
     AccurateRip matches at confidence 200; last read 4065BECC, not kept`.
   - **Track 3 converged in none of the 8 loops.**
4. **Pregaps.** Every log agrees on eight of the nine pregaps. Track 9's is
   `94 or 95 frames (undecided)` in 7 of the 24 `Gaps:` lists and 95 frames in the rest (HW-6).
5. **The cache probe:** `128 to 255 sectors (… uncached read 245.1 ms, cached read 1.6 ms, 3
   re-reads after a 256-sector run took 30.3 ms or more)`, and `cd-paranoia -A`, run alone:
   `cache 137 sectors, defeated, exit 0` (`session/transcript.txt:1385`, `:1538`). `-f` found
   `+667` at confidence 14 (`:1317`).

## What it does not establish

- **Why track 3 read differently from the first run.** The disc, drive and build are the same;
  the second run's reads disagree among themselves as the first's did.
- **Which install produced the binary,** as for the first run.

## Questions, gaps and next time

**Questioned:**
- **Platterpus's audit failing its own production build,** as in the first run (R43-13), which
  their `23f790db` fixes on their `main`. Theirs.

**Possibly missing:**
- **The two rig checks of 2026-11-25:** `time cyanrip -I -N -d /dev/sr0` with Platterpus
  closed, and `cat /proc/sys/dev/cdrom/lock`. Not in this bundle either.

**To add next time:**
- **A run after Platterpus releases `23f790db`,** whose logs should read `-- released build`.

**More than we asked:**
- **The 112 chase records of track 3,** each a single read with its per-second CRCs, the
  densest sample of the disc's hardest track filed so far.
