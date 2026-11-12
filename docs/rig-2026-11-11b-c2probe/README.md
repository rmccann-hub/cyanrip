# Rig session 2026-11-11b — the C2 probe and the two-read check, Platterpus's runner, the reference disc

**What this is.** Round 39's G4 probe: Platterpus's `docs/rig-scripts/drivetest.sh`, its `probe`
entry, run by the owner on the BDR-209D from 22:54:27Z, after the test burn
(`docs/rig-2026-11-11-e531a33/`). It ran three things:
- **The two-read check:** one `cyanrip -I -N` alone, then two 2.4 s apart, then the pair again
  under `strace`.
- **The C2 probe:** READ CD with byte 9 = `12h` (C2 error pointers, 2646 bytes a frame), three times
  at each of round 38's five LBAs, after a cache flush.
- **One read at track 5's LBA with byte 9 = `14h`:** C2 pointers and the block error byte, 2648
  bytes a frame.

The probe kept the C2 bytes of each read and dropped its audio (`probe/*.noaudio`, 294 or 296 bytes
a frame). Personal details were replaced by `tools/redact.py`, and `SHA256SUMS` gives each file's
filed and delivered hash. The app's own logs, 90 MB, are named there and not filed.

**Read the build, not the date.** The C2 reads are `sg_raw`, not cyanrip. The two-read check ran
`~/.local/bin/cyanrip`, and the pair under `strace` ran `/usr/local/bin/cyanrip`. Neither run
printed its banner, so the build is not in this delivery. Their `Still waiting:` lines name pregap
searches, a wording `.31` is the first release to carry.

## What it establishes

1. **This drive returns C2 error pointers, and they flag track 5's error.**
   - **Where.** At LBA 83416, all four reads (three at `12h`, one at `14h`) set the same three bits
     in frame 14 (LBA 83430): bytes 1004, 1043 and 1050 of the frame.
   - **On the track.** By the TOC (track 5 from LSN 72570) and the read offset of +667 samples,
     those are track 5's samples 6,385,264, 6,385,273 and 6,385,275, at 02:24.79, which is 02:24:59
     in frames.
   - **How it matches.** Platterpus's report of the test burn places `E0036697`'s three-sample
     difference from CTDB's 1,425-submission entry at "@02:24:59", and the burn's records put track
     5's every disagreement in second 144 (02:24).
   - **The block error byte.** The `14h` read also sets it for that frame, `38h`.
2. **No C2 bit is set at track 3's three LBAs** (46422, 46446 and 46911, three reads each) **or at
   the control** (LBA 5000).
3. **The two-read check did not finish, alone or in a pair.**
   - **The lone read** printed nothing after `Opening drive...` and no `Still waiting:` line in
     300 s, and was killed at 305 s (exit 137). The kernel logged `ata2: SATA link up 1.5 Gbps`
     and `configured for UDMA/33` at 22:56:11Z (`kernel.txt`), 92 s into it.
   - **In the pair,** A worked through the pregap searches and was still in the second ones at
     300 s, each named by the watchdog, 14 s to 82 s apiece (`probe/pairA.txt`,
     `probe/pairA-strace.txt`). B printed nothing (`probe/pairB.txt`, 0 bytes), and under
     `strace` only `Checking /dev/sr0 for cdrom...` (`probe/pairB-strace.txt`).
   - **Under `strace`,** both sent SCSI packets throughout the 300 s, 894 and 690 of them, about 140
     a minute each; B's last ones, half a second apart, each returned 0.

## What it does not establish

- **Whether the drive flags track 3's misreads.** The probe drops the audio, so whether any of its
  nine reads at track 3 returned a wrong value is unknown. Its windows also cover only part of the
  seconds the records name: 46422 to 46447 holds 20 sectors of second 244 (LSN 46367 to 46441), and
  46911 to 46936 holds 26 of second 251 (46892 to 46966), before the read offset's one sector.
- **Which command the lone read was in.** No trace was taken of it. The drive open is a named wait,
  and no `Still waiting:` line printed, so it was past the open, in a command no wait names. That
  the SATA link reset caused it is not established.
- **What B's packets were.** `strace` gives each packet's address, not its command.

## Questions, gaps and next time

**Questioned:**
- **The lone read's silence.** It contradicts what `.31`'s named waits were for. The commands
  between the drive open and the first pregap search carry no name: the capabilities and
  `drive_declared` queries and the TOC read. Ours to name. **Corrected 2026-11-12**: those are the
  wrong calls. The capabilities and `drive_declared` queries are made before `Opening drive...`
  prints, and libcdio reads the TOC inside the drive open, a named wait, so none of the three can
  be where the lone read sat. Between the open and the first pregap search, the build after `.31`
  names the speed setting, the lead-out and first track lookups, the last-session query and a data
  track's format query; whether the silence was in one of them is not known.
- **B's 690 packets with no output.** Ours, with the trace's commands decoded.

**Possibly missing:**
- **A trace of the lone read.**
- **The audio of the C2 reads at track 3,** to say whether each was right or wrong.

**To add next time:**
- **At track 3's LBAs, a C2 read that keeps its audio,** CRC'd per second against the burn's
  records, so each read is known right or wrong.
- **An LBA in second 252 (47004).**
- **`--version` before the two-read check,** so the build is in the delivery.

**More than we asked:** the block error byte at track 5.
