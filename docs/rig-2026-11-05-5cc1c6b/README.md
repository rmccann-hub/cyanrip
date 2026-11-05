# Rig session 2026-11-05 — build `5cc1c6b` (`.30`), Platterpus 0.7.121, round 38's drive test up to Run A

**Read the build, not the date.** `.30` (`0.9.4-rc3+platterpus.30`,
`platterpus-fork-g5cc1c6b`) through Platterpus **0.7.121**, the BDR-209D
(firmware 1.51) and the reference disc. This is the first sitting of the
round 38 drive test, printed from Platterpus's `docs/rig-session.md`, as far as
its step 1.4, Run A, which ended at its step L90 before any rip.

**What is here.** Five files the owner uploaded at 22:32Z, as delivered except
for personal details, which `tools/redact.py` replaced (`SHA256SUMS` gives both
hashes of each):

| File | What it is |
|---|---|
| `session/owner-sheet-annotated.md` | the printed sheet with the owner's notes and terminal output for phase 0 and steps 1.1 to 1.4, Run A's app log among them |
| `session/dumps/pioneer-f4.txt` | Pioneer's settings read, `sg_raw … 3c 02 f4 …`, at 22:20:26Z |
| `session/dumps/before.txt` | `sg_inq`, `sg_get_config` twice and `sg_modes -a` for page controls 0 to 3 |
| `session/dumps/cyanrip-vendor.json` | `.30`'s `--diagnostics` record of `-I … --read-vendor-settings` |
| `session/dumps/cyanrip-vendor.txt` | that run's output |

**Run A's bundle is not here**: `platterpusbundle20261105t2224310000.tar.gz`
(`owner-sheet-annotated.md:461`) has not reached this session.

## What it establishes

1. **Phase 0**: About showed 0.7.121 and `.30` at 5:15 PM EST, 22:15Z (the
   owner's note, `owner-sheet-annotated.md:65-66`). Step 1.1's rig scripts are
   8598 and 9492 bytes (`:97-98`), the sizes the sheet names.
2. **Two programs read the same 256 bytes of Pioneer's settings block.**
   `sg_raw` at 22:20:26Z (`pioneer-f4.txt:4-20`) and `.30`'s
   `drive_declared.vendor_settings.bytes` (`cyanrip-vendor.json`) are byte
   identical: `ff ff 02 02 ff ff ff 00 00 00 00 ff ff ff ff 00 | 00 ff ff 00
   ff ff ff ff ff ff ff ff 00 00 00 ff | ff ff ff ff ff ff ff 00 ff ff ff 00
   00 00 00 00`, then 208 zero bytes. `.30`'s first vendor read on a drive.
3. **`.30`'s reading of it**: `block_valid` true (bytes 0-1 are the `ff ff`
   sentinel), `support` `unsupported` (byte 9 is 0), `mode` null, which is
   `crip_pioneer_f4_decode` applying pioneer-optical's reading
   (`pioneer-optical@d2cbbf2:src/settings/f4.rs`). Whether that reading holds
   for this drive's firmware is what Pioneer's utility, in phase 3, can say.
4. **The drive declares C2 two ways, and they disagree.** Its capabilities
   page, 2Ah, has byte 5 = `63h` (`before.txt:208`, `2a 36 3f 17 f1 63 …`):
   bit 4, *C2 pointers supported*, is 0, while bits 0, 1, 5 and 6 (CD-DA,
   accurate stream, ISRC, UPC) are 1. Its CD Read feature, 001Eh, says
   `C2 flags=1` (`before.txt:56-58`). `.30`'s header line `C2 errors:
   unsupported by drive` reads the first only. Neither is a measurement of
   what a READ CD asking for C2 pointers returns.
5. **Run A ended at L90 with two disc reads running at once**
   (`owner-sheet-annotated.md:377-461`). The app started at 22:24:30Z; it
   reported `drive changed` at 22:24:31.574 and again at 22:24:34.185, and
   7 ms later that the first `DiscInfoWorker` *"was superseded by a newer disc
   probe — abandoned while it finishes its current step"* (`:394`). Each
   probe, `cyanrip -I -N -d /dev/sr0`, was killed at 120.0 s having written
   109 characters (`:395-419`): the two lines of libcdio's drive check and
   `Opening drive...`, nothing else. L90's rescan failed at 22:26:34.309
   (`:423`); `fuser -k` freed the drive (`:424`); the app's own re-read at
   22:26:38 reached MusicBrainz 15 s later (`:426-427`); the run ended
   saying *"no disc with five tracks is loaded"* (`:431`), with the disc in
   the drive.
6. **Our open was not where it stalled.** `.30` arms its watchdog before
   `cdio_cddap_open()` (`src/cyanrip_main.c:484-486`), which prints `Still
   waiting: the drive open has not returned after 10s` to stdout and flushes
   (`src/stall_watchdog.c:178-189`, `src/cyanrip_log.c:1645-1655`; held by
   `tests/stall.c:228`). Neither capture holds it, so the open returned within
   10 s and each process then sat for 110 s in the stretch from the open to
   `MusicBrainz URL:`: the TOC, the pregap searches, MCN, CD-TEXT and ISRC,
   none of which has a liveness line. That is a reading of our code, not a
   measurement of the drive.

## What it does not establish

- That two reads at once stall this drive: one occurrence, inside the app.
  The two-read check in `tools/rig/drivetest.sh` measures it with the app
  closed, and names the stalled command under `strace` if it stalls.
- Which SCSI command each process waited in.
- Anything of Runs A to D, phase 2 or phase 4: none had run.

## Questions, gaps and next time

**Questioned:**
- `owner-sheet-annotated.md:431`: *"no disc with five tracks is loaded"* is
  false; the disc was in, and the scan had timed out. Platterpus's wording.
- `cyanrip-vendor.txt:24`, `C2 errors: unsupported by drive`: true of page 2Ah,
  contradicted by feature 001Eh (item 4). Ours: a rename goes to a round, not
  a silent edit.

**Possibly missing:**
- Run A's bundle, and the app's diagnostic records for the two probes
  (`:395` *"see the diagnostic record"*). The owner's next upload carries them.

**To add next time:**
- A liveness line for the stretch after the open (ours, `.31`).
- A READ CD with C2 pointers requested at the wrong samples' places: the C2
  probe in `tools/rig/drivetest.sh`.
- The kernel's messages about the drive for the run's span: the runner
  collects them.

**More than we asked:** `cyanrip-vendor.json` carries `drive_declared` in full
for the first time on this drive: INQUIRY 96 bytes, configuration 436 bytes,
four page controls of 180 bytes each.
