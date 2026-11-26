# Rig session 2026-11-25: round 43's Full run, `.35` through Platterpus 0.7.130

**What this is.** Round 43's run, the one our round 43 lap 1's G1 names. The owner ran
Platterpus 0.7.130's Full acceptance script on the BDR-209D and the reference disc from
2026-11-25 20:24:17Z. Its steps' times add up to 2026-11-26 00:18:22Z.

**Where it comes from.** One rig-harness bundle, uploaded by the owner on 2026-11-26:
`platterpusbundle20261125t202417z.tar.gz`, sha256
`0b6528e171d2c4191b6ed32a7a22d183c7911f4021a0a1c4bf656c3900d3cf4a`, 5,792,008 bytes.
- **Integrity.** All 247 members its `MANIFEST.txt` hashes match the sender's hashes.
- **Filed** by `tools/ingest-bundle.py`: 69 files under `album/` from 17 album folders, 111
  records under `ripperdiagnostics/`, 18 files under `session/`, and the bundle's
  `MANIFEST.txt`, `DIAGNOSTICS.txt` and `SOURCES.txt`.
- **Not filed,** with their hashes in `SHA256SUMS`: 29 screenshots, Platterpus's 15
  `.platterpus.json` reports, `COMPONENTS.json`, `SETTINGS.json` and
  `session/artifacts/03platterpus/config.toml`.
- **The album folders are back.** Round 42's in-app bundles carried none; this rig-harness
  bundle carries every rip's log, CUE sheet and record, as round 41's did.

**Checks.**
- **Signatures.** All 24 signed files verify with `-Y`, on the delivered bytes and as filed:
  17 cyanrip `.log` files and Platterpus's 7 securing-pass copies.
- **Personal details.** `tools/redact.py` replaced nothing: Platterpus had already written home
  paths as `~`. No hostname was found, and the owner's name was not checked, for want of a
  local list.

**Read the build, not the date.**
- **The pair.** All 17 logs open `cyanrip 0.9.4-rc3+platterpus.35 (platterpus-fork-g1280aa4)`,
  with `Consumer: platterpus/0.7.130`. The ingest reads `.35` (`release_seq` 50) and 0.7.130 as
  the newest pair when the run began.
- **No `.34` this time.** The script's A/B timing and accuracy sections compare Platterpus's
  `FORK_PIN` with its build under review. Both are `1280aa4` in 0.7.130, so the script skipped
  them (`skip-if-same-build`, L1678 and L1784), and those are the run's 128 `unreachable` steps.
  **Corrected 2026-11-26**, after filing at `6451c5c`: 127 of them are. The 128th is
  `expect-offset-refusal` (L625), which cannot run on a drive AccurateRip's list carries, as in
  round 42's runs.
- **The verdict.** `pass 531, fail 8, unreachable 128, info 8`, `ok: False`
  (`session/run/report.json`). **The run did not pass.** All eight failures are one check of
  Platterpus's, point 1.

## What it establishes

1. **The eight failures are Platterpus's album audit disagreeing with a build Platterpus made.**
   - **The check.** Every failure is `expect-album-audit`, at L784, L865, L908, L1010, L1166,
     L1194, L1222 and L1387, with one text: *"DISAGREEMENT: we score this ripper 'approved'
     while the binary itself says it was built from an open round"*
     (`platterpus@d15c0fff:src/platterpus/rip_audit.py:260-266`).
   - **What the binary says.** All 17 logs print
     `Handshake:      round 41 lap 5 OPEN, verdict GO -- NOT a released build`.
   - **The same commit said the opposite in round 42.** Its two Full runs, through 0.7.129,
     have 42 `.35` logs. Every one prints `round 41 lap 5 OPEN, verdict GO -- released build`
     (`docs/rig-2026-11-23-1280aa4/`, `docs/rig-2026-11-24-1280aa4/`). Those binaries were
     declared released at build time; this one was not.
   - **Which Platterpus build leaves the declaration out.** Our manifest names `1280aa4` on both
     channels with `meson setup build -Ddeclare_released=true` (`release-manifest.json`).
     Platterpus's in-app ripper update and `--install-ripper latest` pass that option
     (`platterpus@d15c0fff:src/platterpus/ui/main_window_update.py:794`,
     `src/platterpus/deps/ripper_latest.py:155`). Its production target passes none, on
     purpose: `PRODUCTION_TARGET.meson_options == ()` (`tests/test_fork_source.py:1577`), and
     its wizard builds the same object (`src/platterpus/deps/fork_source.py:3100`). Their test
     gives the reason: their build from source *"is not their published release artifact even
     when it is built from the released commit"* (`tests/test_fork_source.py:1421-1423`).
   - **What the rig asked for.** This bundle's manifest says it wanted
     *"platterpus-fork-g1280aa4 ONLY — the approved production pin"*; round 42's wanted
     *"the build under review"*.
   - **Which install built this binary is not recorded.** The run's app log opens at
     15:22:08 local (20:22:08Z) with `automatic cyanrip update check: up_to_date`, and the drive
     setup log of the same day (`docs/rig-2026-11-25-drivesetup/`) ends at 14:24 local. Neither
     shows a build.
   - **The audit's wording misreads the line.** The shared protocol defines the arm after `--`
     as the build's declaration alone: `NOT a released build` when the build did not declare
     itself released, with the round state kept in the line as information
     (`docs/handshake/PROTOCOL.md:1117-1124`, §7, from v8). Their own `handshake_note.py` says
     the same (`platterpus@d15c0fff:src/platterpus/handshake_note.py:9-21`).
     The audit's *"says it was built from an open round"* gives the reason as the round.
   - **Not a defect in `.35`.** The line prints what `.35` was built with
     (`cyanrip@1280aa4:src/cyanrip_log.c:1224-1226`, `tools/gen-handshake-state.py:143`, `:166`).
2. **G1's run, and what `.35` read.** The seven whole-disc rips (section F, the secure re-read
   and repeat rips 1 to 5) and the ten partial ones all end `Ripping errors: 0`,
   `Read stalls:    none (no read exceeded 10s)` and `Rip completed:  yes`. The exception is
   `cancel me`, which the script stops: `no (interrupted by SIGTERM, 2 of 14 tracks)`.
   - **Section F,** `album/full acceptance∶ angle‹bracket 20261125t202417 …/`. Its log reads
     `Tracks ripped accurately: 12/14` and `Tracks matched on one frame only: 2/14`: track 3
     `3B9C3001` and track 5 `4065BECC` each match AccurateRip's frame 450 only.
   - **Its securing pass** (`-Z 2 -l 3,5`) did not converge on either track. On track 5,
     agreement on `E0036697` was overruled by AccurateRip.
   - **Platterpus's re-read** replaced track 5 with `C96464AB`, AccurateRip v1 `134C0B9D` at
     confidence 129 and v2 `BCF4E815` at 200 (the folder's `.platterpus-addendum.txt`).
   - **Platterpus's CTDB repair** rewrote track 3 toward entry 32115 (1,436 submissions),
     after which CTDB matched (L786).
   - **Repeat rips 2 and 3 verified all 14 tracks from the drive's reads**, some of them
     Platterpus's re-reads, with no repair (L1923, L1933). Track 3 there is `59D352DD`, matched
     by AccurateRip v1 and v2, the read round 42's section F kept. Repeat rips 1 and 5 and the
     secure re-read had track 3 repaired from CTDB, and repeat rip 4 track 5.
   - **So G1's run happened and shows no defect in `.35`.** Tracks 3 and 5 behave as in rounds
     41 and 42: thirteen tracks verified from reads, and one repaired from CTDB with its repair
     labeled, in all but two rips.
3. **`--reread-until-accuraterip` kept the matching read of track 5 in 5 of its 8 repeat
   loops.**
   - **Kept.** Repeat rips 1, 3 and 5's securing passes and both of the secure re-read's loops
     kept `C96464AB`, each line naming the read AccurateRip matches at confidence 200. Repeat
     rip 5's: `kept C96464AB, read 2 times, which AccurateRip matches at confidence 200`.
   - **Nothing to keep.** In the other three (section F, repeat rips 2 and 4) no read matched,
     and each `Done;` line says `agreement on E0036697 overruled by AccurateRip`.
   - **Track 3 converged in none of the 8**, each ending at the repeat limit with at most 2
     reads agreeing.
4. **The header lines are the same in all 17 logs**: `C2 errors:      not declared by drive
   (capabilities page, not measured)`, `Disc MCN:       none (libcdio returned none)`,
   `CD-TEXT:        none reported by libcdio (absent, or unreadable by this driver)` and
   `Cache model:    1200 sectors (drive cache size not probed)`.
5. **Pregaps.** Every log agrees on eight of the nine pregaps. Track 9's is
   `94 or 95 frames (undecided)` in 4 of the 24 `Gaps:` lists and 95 frames in the other 20
   (HW-6). Repeat rip 3's search answered `-3 sectors off` and repeat rip 1's `+8 sectors off`
   at LSN 145567 (L1984).
6. **The cache probe**, `cyanrip -N --cache-probe -I`, alone on the drive: `128 to 255 sectors
   (294.0 to 585.7 KiB, uncached read 237.8 ms, cached read 1.6 ms …)`. `cd-paranoia -A`, run
   alone: `cache 137 sectors, defeated, exit 0` (`session/transcript.txt:1374`, `:1527`). The
   range is the one every run since `.20` has reported; round 42's second run had
   `cd-paranoia -A` at 140 sectors and an uncached read of 362.6 ms.
7. **`-f`** found `+667` at confidence 14 (`session/transcript.txt:1305`).
8. **The de-emphasis pair** read track 1 identically, `B0D122E7`, each AccurateRip-verified
   (`5D3C90CB` / `22B9924D`), with `Filtered: hdcd, de-emphasis` under `-E` and
   `Filtered: hdcd` under `-W`.

## What it does not establish

- **Which install produced this binary,** or when (point 1).
- **That `C96464AB` is the pressing's track 5.** It is the read AccurateRip matches; the
  pressing is not measured here.
- **Anything about `.36`,** which is not built.

## Questions, gaps and next time

**Questioned:**
- **Platterpus's production target building the approved pin without the manifest's
  declaration, and its audit failing the result.** Two of Platterpus's install paths build the
  same commit with different claims. The audit then fails its own production build, and gives
  the round as the reason. Theirs; our round 43 lap 1 asks which side of it they change.
- **The negative arm, `NOT a released build`.** For a build without the declaration it says
  more than the binary knows: it was not declared, not that it is not the release. Ours. A
  rename is a line Platterpus parses (`handshake_note.py:41-80`, where any arm containing
  `released build` reads as released), so it waits for a round.

**Possibly missing:**
- **The install.** Neither app log covers 14:24 to 15:22 local, when the binary may have been
  built.
- **The screenshots and Platterpus's reports,** named in `SHA256SUMS`, not filed, as before.

**To add next time:**
- **The ripper install step in the run's own record,** with the options it built with.
  Theirs.
- **The two rig checks still open from 2026-11-25:** `time cyanrip -I -N -d /dev/sr0` with
  Platterpus closed, and `cat /proc/sys/dev/cdrom/lock`. Neither is in this bundle. The owner's.

**More than we asked:**
- **Repeat rips 2 and 3,** two whole-disc rips of this disc verified from reads alone in one
  session, a first since round 41.
