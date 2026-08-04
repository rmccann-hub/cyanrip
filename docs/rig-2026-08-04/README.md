# Rig session, 2026-08-04

The artifacts every claim in `docs/handshake/round-7-lap10.md` is checked
against. Archived here because a handshake file that cites evidence nobody else
can open is an assertion, not a verification — and because a rip is a
measurement of a physical object that will not be measured the same way twice.

```
ripper      cyanrip 0.9.4-rc1+platterpus.5-beta.1 (platterpus-fork-g9003e6f)
consumer    Platterpus 0.6.4b3 (build 1671c21)
drive       PIONEER  BD-RW   BDR-209D (revision 1.51)
disc        The Police - Every Breath You Take: The Classics, 14 tracks
            MusicBrainz pNtImOkdBm9RMBIalzx0w9cfsYY- / CDDB E20DFE0E
offset      +667 samples
```

| file | written by |
|---|---|
| `cyanrip.log` | cyanrip, **with Platterpus's auto-fix addendum appended** |
| `cyanrip.cue` | cyanrip |
| `platterpus-eac-compatible.log` | Platterpus |
| `platterpus.json` | Platterpus |

## `cyanrip.log` does not verify, and that is the point

```
$ cyanrip --verify-log cyanrip.log
Log "cyanrip.log" has data after the checksum, the file has been modified!   (exit 1)
```

Kept exactly as it arrived. The nine lines from `====` onward were appended by
Platterpus after the `Log FUN512:` line; removing them makes the same file
verify. This is finding H1 of lap 10, and the archived copy is the evidence — so
it is stored unmodified rather than repaired.

## Not archived

Platterpus's rotated stdout captures (~3.2 MB over five files, 35559 lines).
They are the source for lap 10 §B4 and §B5 — the zero stall heartbeats, and the
six pre-log lines including `CDROM sensed: PIONEER  BD-RW   BDR-209D 1.51 SCSI
CD-ROM` that reached no logfile. Left out for size; the two derived facts are
stated in the lap with how they were obtained.

## What this session does and does not establish

It retired the MMC sub-channel pregap read, `-Z` on hardware, and the
per-track/disc paranoia invariant on media that made paranoia work. It did not
touch `-x`, C2, `-f`, damaged media, CD-TEXT from a disc that has some, or the
diagnosed-abort exit code. The stall watchdog was silent because nothing
stalled, which is not evidence that it fires. Per-claim detail is lap 10 §F.
