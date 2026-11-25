# Rig session 2026-11-25: drive setup on Platterpus 0.7.130 with `.35`, a cache check killed mid-test

**What this is.** Platterpus's app log from the owner's machine, which the owner uploaded on
2026-11-25 with the message the app showed them: *"Audio cache: cd-paranoia ran but didn't
report a cache verdict we recognise, so it was recorded as unknown rather than guessed."*
The log covers the BDR-209D and a disc other than the reference disc: MusicBrainz disc ID
`pNtImOkdBm9RMBIalzx0w9cfsYY-`, CDDB `E20DFE0E`, which MusicBrainz knows (4 candidates).

**The log's clock is local time, UTC−5.** Build `d15c0ff` (0.7.130) did not exist until
2026-11-25 16:31Z, yet the log shows it starting at `14:17:46`. The app logs filed in
round 42 show the same offset: their bundle names are in UTC and are 5 hours ahead of the
lines that write them (`docs/rig-2026-11-24b-c2probe/`). Times below give both.

**Where it comes from.** One file, `log.txt`, 815,707 bytes, sha256
`4fa859f29b30a737fe4eabefb7d428bab6a12bb5026496a256fc5b3b2a86cecc`, filed as
`applog/log.txt`.
- **Start.** It begins mid-way through the second Full run of 2026-11-24, at
  `10:20:50` local. Its lines 2 to 5,816 are those of the copy filed at `b263e0e`
  (`docs/rig-2026-11-24b-c2probe/applog/log.txt`), line for line.
- **What is new.** From line 5,817: two launches on 2026-11-25, 0.7.129 at `14:17:29`
  and 0.7.130 at `14:17:46` local (19:17Z).
- **Truncated by Platterpus.** It keeps 12,077 characters of the killed read's output,
  with `… [192 line(s) omitted] …` in the middle.

**Checks.**
- **Personal details.** `tools/redact.py` replaced 108 home paths; no hostname was found;
  the owner's name was not checked, for want of a local list. `SHA256SUMS` gives the filed
  hash and the delivered one.
- **No sender's hash.** This is a single uploaded file, not a bundle, so nothing checks it
  against the sender.

## What it establishes

1. **The cache verdict is unknown because Platterpus killed cd-paranoia.**
   - **The kill.** At `14:22:47.698` local (19:22:47Z) the app ran `fuser -k (SIGKILL)
     /dev/sr0` to free the drive (`free_drive: killed=True`).
   - **The result.** `cd-paranoia -A` exited 137, 128 plus SIGKILL's 9, its timing test
     cut mid-line at `[40:00.00]:`.
   - **The app's own record.** Its diagnostic says so: *"exited 137 — … a tool failure
     rather than an inconclusive measurement"*. The message the owner saw says
     *"didn't report a cache verdict we recognise"*.
2. **The kill followed Platterpus giving up on our `cyanrip -I -N -d /dev/sr0`** at its
   300 s limit, at `14:22:47.601` local. The read began after `14:17:47.571`.
3. **cd-paranoia was timing the drive while that read ran.** At `14:20:09` the app's
   automatic cache check reported `drive busy True`. cd-paranoia's output was still in
   progress at the kill, so the two programs read the drive at once for some of that time.
   A verdict from that test would have measured a busy drive.
4. **`.35`'s watchdog named every wait on a drive.** After `Opening drive...` it printed
   `Still waiting:` lines and their returns:

   | Search | Took |
   |---|---|
   | track 2's pregap | 22 s |
   | track 4's pregap | 23 s |
   | track 2's second pregap search | 32 s |
   | track 4's second pregap search | 41 s |
   | track 5's second pregap search | 13 s |
   | track 7's second pregap search | 12 s |
   | track 8's second pregap search | 18 s |
   | track 6's ISRC search of the Q frames | over 10 s, still running at the kill |

5. **This disc has sub-channel pregaps the TOC does not signal.** Track 5's is 115 frames.
   Track 4's search asked 155 sectors and found 10 frames that were another sector's.

## What it does not establish

- **How long `-I` takes on this disc with the drive to itself.** The cache test shared the
  drive for an unknown part of the 300 s. An `automatic re-read` at `14:22:51` found the
  disc in MusicBrainz by `14:23:14`, but the log does not say what that re-read ran.
- **When cd-paranoia started, or who started it.** No line records its start. The
  automatic check declined at `14:20:09`, and debug logging was off.
- **Anything about the reference disc.**

## Questions, gaps and next time

**Questioned:**
- **The cache test running beside another read of the drive, and the `fuser -k` that
  killed it.** Theirs.
- **The message that calls a SIGKILL an unrecognised verdict.** Theirs.
- **`-I`'s sub-channel searches, two per track where a pregap is found, each up to 41 s on
  this drive.** Ours.

**To add next time:** the cache test run alone, and `cyanrip -I -N` timed alone on this
disc. `-I` can run with the drive to itself in a terminal:
`time cyanrip -I -N -d /dev/sr0`, with Platterpus closed.
