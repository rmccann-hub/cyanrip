# cyanrip provider contract

**Generated** by `tools/gen-provider-contract.py` from the source tree and the
built binary. Do not edit by hand -- regenerate. A hand-written contract goes
stale silently, which is the failure this file exists to prevent.

Build: `cyanrip 0.9.4-rc1+platterpus.4 (platterpus-fork-g<commit>)`

**Source anchor:** `sha256/16 = c109971e81cbba95` over `src/*.c` and
`src/*.h`. **Every `file:line` below refers to exactly that source.** Line
numbers move between commits, so a citation without an anchor is not
checkable -- recompute this hash before quoting one back.

This is the provider half of the seam. Platterpus generates the consumer half
(`docs/cyanrip-consumer-contract.md`) from its parser tables. Neither side
describes behaviour it does not have.

## P1 - Inputs: every command line flag

From the binary's own `--help`, so it cannot drift from what the build accepts.


### General

| Short | Long | Meaning |
|---|---|---|
| `-h` | `--help` | Print this text |
| `-v` | `--version` | Print the version number (-V accepted as an alias) |

### Ripping options

| Short | Long | Meaning |
|---|---|---|
| `-d` | `--device` | Set device path (can be a TOC file) |
| `-s` | `--offset` | CD drive offset in samples (default: 0) |
| `-r` | `--retries` | Maximum number of retries for frames and repeated rips (default: 10) |
| `-Z` | `--repeat-rips` | Rip tracks until checksums match N times (for damaged CDs) (default: 0) |
| `-S` | `--speed` | Set drive speed (default: 0) |
| `-k` | `--stall-secs` | Seconds a frame read must stall before reporting liveness (0 disables) (default: 10) |
| `-x` | `--cache-probe` | Measure the drive's readback cache before ripping (costs seconds) (default: false) |
| `-u` | `--consumer` | Identify the calling program in the log (recorded verbatim, not verified) |
| `-p` | `--pregap` | Track pregap handling: N=default|drop|merge|track (repeatable) |
| `-P` | `--paranoia` | Paranoia level (0..max, or 'none'/'max') |
| `-O` | `--overread` | Enable overreading into lead-in and lead-out (default: false) |
| `-H` | `--hdcd` | Enable HDCD decoding (default: false) |
| `-E` | `--force-deemphasis` | Force CD deemphasis (default: false) |
| `-W` | `--no-deemphasis` | Disable automatic CD deemphasis (default: false) |
| `-K` | `--no-replaygain` | Disable ReplayGain tagging (default: false) |

### Output options

| Short | Long | Meaning |
|---|---|---|
| `-o` | `--outputs` | Comma separated list of output formats ('help' lists all) |
| `-b` | `--bitrate` | Bitrate of lossy files in kbps (default: 256.000000) |
| `-D` | `--folder-scheme` | Directory naming scheme (default: {album}{if #releasecomment# > #0# (|releasecomment|)} [{format}]) |
| `-F` | `--track-scheme` | Track naming scheme (default: {if #totaldiscs# > #1#|disc|.}{track} - {title}) |
| `-L` | `--log-scheme` | Log file name scheme (default: {album}{if #totaldiscs# > #1# CD|disc|}) |
| `-M` | `--cue-scheme` | CUE file name scheme (default: {album}{if #totaldiscs# > #1# CD|disc|}) |
| `-l` | `--tracks` | Comma separated list of tracks to rip (default: all) |
| `-T` | `--sanitize` | Filename sanitation: simple, os_simple, unicode, os_unicode |

### Metadata options

| Short | Long | Meaning |
|---|---|---|
| `-I` | `--info` | Only print CD and track info (default: false) |
| `-J` | `--cue-only` | Only generate and print a CUE sheet, don't rip (default: false) |
| `-a` | `--album-meta` | Album metadata, key=value:key=value |
| `-t` | `--track-meta` | Track metadata as N=key=value:key=value (repeatable) |
| `-R` | `--release` | MusicBrainz release: 1-based index or ID string |
| `-c` | `--disc` | Multi-disc tag: disc/totaldiscs |
| `-C` | `--cover` | Cover art: title=path (or N=path per-track, repeatable) |
| `-N` | `--no-musicbrainz` | Disable MusicBrainz lookup (default: false) |
| `-A` | `--no-accurip` | Disable AccurateRip database query and validation (default: false) |
| `-U` | `--no-coverart-db` | Disable Cover art DB query and retrieval (default: false) |
| `-m` | `--cover-size` | Cover art max size: 250, 500, 1200, or -1 for original (default: -1) |
| `-G` | `--no-coverart-embed` | Disable embedding of cover art images (default: false) |

### Misc. options

| Short | Long | Meaning |
|---|---|---|
| `-Q` | `--eject` | Eject tray once successfully done (default: false) |
| `-f` | `--find-offset` | Find drive offset (requires a disc with an AccuRip entry) (default: false) |
| `-Y` | `--verify-log` | Verify a rip log's FUN512 checksum |

**40 flags total.** Notes that are not derivable from `--help`:

- `-O` is **overread**, not an options passthrough. Never repurpose it.
- `-v`, `-V` and `--version` all print the version banner and exit 0.
  Upstream moved this flag from `-V` to `-v` when it replaced getopt with
  genopt after 0.9.3; a caller probing with `-V` against a stock 0.9.4 build
  gets exit 1 and `Unable to parse command line argument: -V`, which reads
  as "not installed" rather than "flag renamed". This fork accepts `-V`
  again. **Prefer `--version`** -- it has never changed and never will.
- `-J` and `-I` are mutually exclusive; combining them exits 1.
- `-d` accepts a device path **or** a TOC/CUE/NRG image file.
- `-a`/`-t` values are `:`-separated; a literal colon must be escaped `\:`.
- `-t N=` and `-l N` are 1-based and validated against the disc's real track
  count; out of range exits 1 with a message naming both numbers.
- Multiple `-o` formats produce **one logfile and one cue per format**.

**Units that are not obvious from the line itself:**

- `Total time:` and every `duration:` is **`MM:SS.FF`, where FF is CD frames
  (1/75 s, range 0-74)** - not centiseconds and not milliseconds. There is
  **no hours field** and minutes are **not** modulo 60: a 125-minute disc
  prints `125:00.00`. Real seconds are `mm*60 + ss + ff/75`. Reading `.26` as
  hundredths is wrong by up to 0.98 s. Upstream changed this shape from
  `HH:MM:SS.mmm` between 0.9.3 and 0.9.4-rc1 (upstream PR #130), so a
  consumer that has seen both must discriminate on the colon count: three
  fields is the legacy form, two is frames.
- `Pregap length:` is in **frames**, stated in the line.
- `Sample peak level:` is a percentage of full scale **and** dBFS;
  `True peak level:` is dBFS only.
- Paranoia counters are **raw callback counts**, not rates or scores, and are
  only comparable between tracks of the same disc on the same drive.
- **Paranoia counter scope (A8).** A per-track `Paranoia status counts:`
  block covers **the final `-Z` pass for that track only**; the disc-level
  block is **cumulative across every pass the invocation performed**. They
  are therefore equal only at `-Z 0`, where there is exactly one pass -
  confirmed on real hardware by Platterpus (round 7: 22055/1600/54/468,
  summing exactly across 14 tracks). Under `-Z N` the per-track figures sum
  to **less** than the disc block by the reads the earlier passes did. A
  consumer cross-checking the two blocks must condition on `-Z`.
- **Paranoia counter denominator under `-l` (Q10).** The disc-level block
  counts only what **this invocation** read, not the whole disc. Under
  `-l 3,5` it covers tracks 3 and 5 and nothing else, and `Rip completed:`
  says `yes (2 of 14 tracks)`. The denominator is the invocation, never the
  TOC.

## P2 - Outputs: stable log lines (the API)

Every line below reaches **both stdout and the logfile**. Changing the text,
indentation, field order or units of any of them is a breaking change and
requires a handshake round.

| File:line | Line |
|---|---|
| `accurip.c:97` | `Unable to get AccuRIP DB data: missing CDDB ID!` |
| `accurip.c:129` | `Unable to get AccuRIP DB data: missing entry!` |
| `accurip.c:137` | `Unable to get AccuRIP DB data: %s%s` |
| `accurip.c:140` | `Unable to get AccuRIP DB data: %s!` |
| `accurip.c:176` | `AccuRIP DB data error, got unexpected number of bytes!` |
| `cache_probe.c:108` | `Cache probe:    not run (disc image has no drive cache)` |
| `cache_probe.c:116` | `Cache probe:    unknown (out of memory)` |
| `cache_probe.c:129` | `Cache probe:    unknown (disc too short to probe)` |
| `cache_probe.c:141` | `Cache probe:    unknown (read failed while calibrating)` |
| `cache_probe.c:158` | `Cache probe:    unknown (drive returned reads too fast to time)` |
| `cache_probe.c:187` | `Cache probe:    no readback cache measured (uncached read %.1f ms)` |
| `cache_probe.c:193` | `Cache probe:    %i sectors measured (%.1f KiB, uncached read %.1f ms)` |
| `coverart.c:34` | `Cover art has no packet!` |
| `coverart.c:51` | `Unable to init lavf context: %s!` |
| `coverart.c:57` | `Unable to alloc stream!` |
| `coverart.c:70` | `Couldn't open %s for writing: %s!` |
| `coverart.c:82` | `Couldn't write header: %s!` |
| `coverart.c:92` | `Error writing picture packet: %s!` |
| `coverart.c:97` | `Error writing trailer: %s!` |
| `coverart.c:169` | `Downloading %s cover art...` |
| `coverart.c:177` | `Unable to get cover art \"%s\": not found!` |
| `coverart.c:186` | `Unable to get cover art \"%s\": %s%s!` |
| `coverart.c:189` | `Unable to get cover art \"%s\": %s!` |
| `coverart.c:262` | `Unable to open \"%s\": %s!` |
| `coverart.c:269` | `Unable to get cover image info: %s!` |
| `coverart.c:299` | `Error demuxing cover image: %s!` |
| `coverart.c:360` | `Release ID unavailable, cannot search Cover Art DB!` |
| `cue_writer.c:39` | `Couldn't open path \"%s\" for writing: %s!Invalid folder name? Try -D <folder>.` |
| `cyanrip_encode.c:364` | `Error creating filter source: %s!` |
| `cyanrip_encode.c:375` | `Error creating filter sink: %s!` |
| `cyanrip_encode.c:389` | `Error setting filter sample format: %s!` |
| `cyanrip_encode.c:397` | `Error setting filter channel layout: %s!` |
| `cyanrip_encode.c:406` | `Error setting filter sample rate: %s!` |
| `cyanrip_encode.c:440` | `Error initializing filter sink: %s!` |
| `cyanrip_encode.c:474` | `Error parsing filter graph: %s!` |
| `cyanrip_encode.c:480` | `Error configuring filter graph: %s!` |
| `cyanrip_encode.c:541` | `Error pushing frame to FIFO: %s!` |
| `cyanrip_encode.c:614` | `Error filtering frame: %s!` |
| `cyanrip_encode.c:692` | `Error allocating frame!` |
| `cyanrip_encode.c:704` | `Error allocating frame: %s!` |
| `cyanrip_encode.c:820` | `Album Loudness` |
| `cyanrip_encode.c:839` | `Could not alloc swr context!` |
| `cyanrip_encode.c:857` | `Could not init swr context!` |
| `cyanrip_encode.c:1032` | `Error while encoding: %s!` |
| `cyanrip_encode.c:1054` | `Error encoding: %s!` |
| `cyanrip_encode.c:1085` | `Error pushing packet to FIFO: %s!` |
| `cyanrip_encode.c:1092` | `Error writing packet: %s!` |
| `cyanrip_encode.c:1122` | `Error writing to file: %s!` |
| `cyanrip_encode.c:1245` | `Codec not found (not compiled in lavc?)!` |
| `cyanrip_encode.c:1254` | `Unable to init output avctx!` |
| `cyanrip_encode.c:1265` | `Could not open output codec context!` |
| `cyanrip_encode.c:1272` | `Couldn't copy codec params!` |
| `cyanrip_encode.c:1279` | `Couldn't open %s: %s! Invalid folder name? Try -D <folder>.` |
| `cyanrip_log.c:51` | `%s%s:` |
| `cyanrip_log.c:54` | `%s` |
| `cyanrip_log.c:64` | `CD-TEXT:        none reported by libcdio (absent, or unreadable by this driver)` |
| `cyanrip_log.c:69` | `CD-TEXT:        present (%s, %i disc %s, %i of %i tracks tagged)` |
| `cyanrip_log.c:90` | `Cache model:    not in use (paranoia disabled)` |
| `cyanrip_log.c:101` | `Cache model:    %i sector%s (disc image, no drive cache)` |
| `cyanrip_log.c:106` | `Cache model:    %i sector%s (drive cache size not probed)` |
| `cyanrip_log.c:140` | `%sSample peak disagreement: ebur128 %.2f dBFS, direct scan %.2f dBFS (%.2f dB apart)` |
| `cyanrip_log.c:154` | `%s%s` |
| `cyanrip_log.c:158` | `%lu` |
| `cyanrip_log.c:198` | `Pregap LSN:  %i (duration: %s)` |
| `cyanrip_log.c:200` | `Pregap length: %i frames` |
| `cyanrip_log.c:202` | `Pregap LSN:  unknown (sub-channel unreadable)` |
| `cyanrip_log.c:204` | `Pregap LSN:  unknown (sub-channel CRC mismatches)` |
| `cyanrip_log.c:206` | `Pregap LSN:  none` |
| `cyanrip_log.c:212` | `Pregap source: sub-channel (not signalled by TOC)` |
| `cyanrip_log.c:214` | `Pregap source: lead-in` |
| `cyanrip_log.c:216` | `Pregap source: TOC` |
| `cyanrip_log.c:219` | `Prepended:   %i frames of silence` |
| `cyanrip_log.c:220` | `Start LSN:   %i` |
| `cyanrip_log.c:222` | `(with offset: %i)` |
| `cyanrip_log.c:226` | `End LSN:     %i` |
| `cyanrip_log.c:233` | `Appended:    %i frames of silence` |
| `cyanrip_log.c:264` | `Preemphasis:` |
| `cyanrip_log.c:266` | `none detected` |
| `cyanrip_log.c:269` | `(deemphasis forced)` |
| `cyanrip_log.c:274` | `present (subcode)` |
| `cyanrip_log.c:276` | `present (TOC)` |
| `cyanrip_log.c:279` | `(deemphasis applied)` |
| `cyanrip_log.c:284` | `Properties:` |
| `cyanrip_log.c:287` | `Data bytes:  %i (%.2f Mib)` |
| `cyanrip_log.c:290` | `Frames:      %u` |
| `cyanrip_log.c:296` | `Duration:    %s` |
| `cyanrip_log.c:297` | `Samples:     %u` |
| `cyanrip_log.c:305` | `Sample peak level: %.1f%% (%.1f dBFS)` |
| `cyanrip_log.c:308` | `True peak level:   %.1f dBFS` |
| `cyanrip_log.c:327` | `Integrated loudness (R128): %.1f LUFS` |
| `cyanrip_log.c:329` | `Loudness range (R128):      %.1f LU (%.1f to %.1f LUFS)` |
| `cyanrip_log.c:333` | `Extraction speed:  %.1fx` |
| `cyanrip_log.c:335` | `Elapsed:            %.2f s` |
| `cyanrip_log.c:343` | `EAC CRC32:     %08X` |
| `cyanrip_log.c:345` | `(after %i rips)` |
| `cyanrip_log.c:352` | `Secure re-read:  converged after %i reads` |
| `cyanrip_log.c:355` | `Secure re-read:  did NOT converge after %i reads (repeat limit hit)` |
| `cyanrip_log.c:360` | `Secure re-read:  not attempted` |
| `cyanrip_log.c:364` | `Accurip:       %s` |
| `cyanrip_log.c:368` | `(max confidence: %i)` |
| `cyanrip_log.c:376` | `Accurip v1:  %08X` |
| `cyanrip_log.c:378` | `(accurately ripped, confidence %i)` |
| `cyanrip_log.c:380` | `(not found, either a new pressing, or bad rip)` |
| `cyanrip_log.c:384` | `Accurip v2:  %08X` |
| `cyanrip_log.c:395` | `Accurip 450: %08X` |
| `cyanrip_log.c:397` | `(match found, confidence %i, but a checksum of 0 is meaningless)` |
| `cyanrip_log.c:400` | `(matches Accurip DB, confidence %i, track is partially accurately ripped)` |
| `cyanrip_log.c:403` | `(not found)` |
| `cyanrip_log.c:410` | `Metadata:` |
| `cyanrip_log.c:420` | `%s:` |
| `cyanrip_log.c:432` | `CD-TEXT:` |
| `cyanrip_log.c:442` | `Paranoia status counts:` |
| `cyanrip_log.c:444` | `none` |
| `cyanrip_log.c:467` | `Embedded cover art:    %s: %s` |
| `cyanrip_log.c:470` | `Embedded cover art:    %s: %ix%i %s` |
| `cyanrip_log.c:474` | `File(s):` |
| `cyanrip_log.c:488` | `cyanrip %s (%s-g%s)` |
| `cyanrip_log.c:491` | `Invoked as:     %s` |
| `cyanrip_log.c:499` | `Handshake:      %s%s` |
| `cyanrip_log.c:505` | `Consumer:       %s` |
| `cyanrip_log.c:509` | `(reported by the caller, not verified by cyanrip)` |
| `cyanrip_log.c:513` | `Drive used:     error retrieving drive info` |
| `cyanrip_log.c:515` | `Drive used:     %s %s (revision %s)` |
| `cyanrip_log.c:516` | `System device:  %s` |
| `cyanrip_log.c:518` | `Device model:   %s` |
| `cyanrip_log.c:519` | `Offset:         %c%i %s` |
| `cyanrip_log.c:521` | `%s%c%i %s` |
| `cyanrip_log.c:530` | `Speed:          %ix` |
| `cyanrip_log.c:532` | `Speed:          default (%s)` |
| `cyanrip_log.c:534` | `C2 errors:      %s` |
| `cyanrip_log.c:543` | `Encoder:        libavformat %i.%i.%i, libavcodec %i.%i.%i (%s)` |
| `cyanrip_log.c:548` | `Paranoia level: %s` |
| `cyanrip_log.c:552` | `Paranoia level: %i` |
| `cyanrip_log.c:553` | `Frame retries:  %i` |
| `cyanrip_log.c:555` | `HDCD decoding:  %s` |
| `cyanrip_log.c:557` | `Album Art:      %s` |
| `cyanrip_log.c:561` | `%s%s%s%s%s` |
| `cyanrip_log.c:569` | `Outputs:` |
| `cyanrip_log.c:575` | `Disc tracks:    %i` |
| `cyanrip_log.c:576` | `Tracks to rip:  %s` |
| `cyanrip_log.c:579` | `%i%s` |
| `cyanrip_log.c:593` | `AccurateRip:    %s` |
| `cyanrip_log.c:599` | `Total time:     %s` |
| `cyanrip_log.c:625` | `Tracks ripped accurately: %i/%i` |
| `cyanrip_log.c:627` | `Tracks ripped partially accurately: %i/%i` |
| `cyanrip_log.c:637` | `Ripping errors: %i` |
| `cyanrip_log.c:644` | `Rip completed:  no (interrupted by user, %i of %i tracks)` |
| `cyanrip_log.c:647` | `Rip completed:  yes (%i of %i tracks)` |
| `cyanrip_log.c:650` | `Ripping finished at %s` |
| `cyanrip_main.c:188` | `No device specified and unable to get default device!` |
| `cyanrip_main.c:196` | `Unable to open device: %s` |
| `cyanrip_main.c:205` | `Unable to init cddap context!` |
| `cyanrip_main.c:207` | `cdio: \"%s\"` |
| `cyanrip_main.c:218` | `Opening drive...` |
| `cyanrip_main.c:221` | `Unable to open device!` |
| `cyanrip_main.c:230` | `Device does not support changing speeds!` |
| `cyanrip_main.c:238` | `cdio error: %s` |
| `cyanrip_main.c:247` | `Unable to init paranoia!` |
| `cyanrip_main.c:292` | `Invalid number of tracks: %i!` |
| `cyanrip_main.c:315` | `CDIO returned invalid track %i end LSN` |
| `cyanrip_main.c:475` | `Frame read failed!` |
| `cyanrip_main.c:552` | `Loading data for track %i...` |
| `cyanrip_main.c:562` | `Stopping, offset finding incomplete!` |
| `cyanrip_main.c:570` | `Data loaded, searching for offsets...` |
| `cyanrip_main.c:579` | `Nothing found for track %i%s` |
| `cyanrip_main.c:584` | `Offset of %c%i found in track %i%s` |
| `cyanrip_main.c:589` | `Offset of %c%i confirmed (confidence: %i) in track %i%s` |
| `cyanrip_main.c:593` | `New offset of %c%i found at track %i, scrapping old offset of %c%i%s` |
| `cyanrip_main.c:607` | `No track had AccuRip entry, cannot find offset!` |
| `cyanrip_main.c:609` | `No track was long enough, unable to find drive offset!` |
| `cyanrip_main.c:611` | `Was not able to find drive offset with a radius of %i frames, trying again with a larger radius...` |
| `cyanrip_main.c:617` | `Drive offset of %c%i found (confidence: %i)!` |
| `cyanrip_main.c:647` | `Unable to read track %i subchannel info!` |
| `cyanrip_main.c:663` | `Track %i is data:` |
| `cyanrip_main.c:720` | `Error in decoding/sending frame: %s` |
| `cyanrip_main.c:732` | `Drive media changed, stopping!` |
| `cyanrip_main.c:763` | `Stopping, ripping incomplete!` |
| `cyanrip_main.c:881` | `Done; (%i out of %i matches for current checksum %08X)` |
| `cyanrip_main.c:887` | `Done; (no matches found, but hit repeat limit of %i)` |
| `cyanrip_main.c:903` | `Repeating ripping (%i out of %i matches for current checksum %08X)` |
| `cyanrip_main.c:918` | `Error in encoding: %s` |
| `cyanrip_main.c:934` | `Error sending flush signal to encoders: %s` |
| `cyanrip_main.c:941` | `Track %i ripped and encoded with errors.` |
| `cyanrip_main.c:943` | `Track %i ripped and encoded successfully!` |
| `cyanrip_main.c:1025` | `Gaps:` |
| `cyanrip_main.c:1030` | `%i frame gap between lead-in and track 1 pregap, merging into pregap` |
| `cyanrip_main.c:1037` | `%i frame unmarked gap between lead-in and track 1, marking as a pregap` |
| `cyanrip_main.c:1059` | `%i frame pregap in track %i,` |
| `cyanrip_main.c:1066` | `unmerged` |
| `cyanrip_main.c:1068` | `merging into track %i` |
| `cyanrip_main.c:1074` | `dropping` |
| `cyanrip_main.c:1080` | `merging` |
| `cyanrip_main.c:1087` | `splitting off into a new track, number %i` |
| `cyanrip_main.c:1128` | `%i frame discontinuity between tracks %i and %i,` |
| `cyanrip_main.c:1133` | `padding track %i` |
| `cyanrip_main.c:1136` | `ignoring` |
| `cyanrip_main.c:1144` | `%i frame gap between last track and lead-out, padding track` |
| `cyanrip_main.c:1209` | `Can't init signal handler!` |
| `cyanrip_main.c:1443` | `Invalid paranoia level %i must be between 0 and %i!` |
| `cyanrip_main.c:1456` | `Invalid max coverart size %i (must be 250, 500, 1200 or -1)` |
| `cyanrip_main.c:1468` | `Invalid sanitation method %s` |
| `cyanrip_main.c:1480` | `Invalid release index %i!` |
| `cyanrip_main.c:1489` | `Invalid discnumber %i` |
| `cyanrip_main.c:1496` | `Invalid totaldiscs %i` |
| `cyanrip_main.c:1500` | `discnumber %i is larger than totaldiscs %i` |
| `cyanrip_main.c:1513` | `Supported output codecs:` |
| `cyanrip_main.c:1521` | `Invalid format \"%s\"` |
| `cyanrip_main.c:1526` | `Duplicated format \"%s\"` |
| `cyanrip_main.c:1541` | `Duplicated rip idx %i` |
| `cyanrip_main.c:1555` | `Invalid track idx for pregap: %i` |
| `cyanrip_main.c:1561` | `Missing pregap action` |
| `cyanrip_main.c:1569` | `Invalid pregap action %s` |
| `cyanrip_main.c:1600` | `No cover art location specified for \"%s\"` |
| `cyanrip_main.c:1609` | `Invalid track idx for cover art: %i` |
| `cyanrip_main.c:1615` | `Cover art already specified for track idx %i!` |
| `cyanrip_main.c:1627` | `Cover art \"%s\" already specified!` |
| `cyanrip_main.c:1633` | `Too many cover arts specified!` |
| `cyanrip_main.c:1643` | `Directory name scheme must contain {format} with multiple output formats!` |
| `cyanrip_main.c:1648` | `-J (only generate a CUE sheet) cannot be used with -I (only print info)!` |
| `cyanrip_main.c:1664` | `Searching for drive offset, enabling AccuRip and disabling MusicBrainz and Cover art fetching...` |
| `cyanrip_main.c:1672` | `Offset is unset! To continue with an offset of 0, run with -s 0!` |
| `cyanrip_main.c:1753` | `MusicBrainz URL:%s` |
| `cyanrip_main.c:1797` | `Error reading album tags: %s` |
| `cyanrip_main.c:1827` | `Log(s) will be written to:` |
| `cyanrip_main.c:1835` | `CUE files will be written to:` |
| `cyanrip_main.c:1889` | `Invalid track number %i, list has %i tracks!` |
| `cyanrip_main.c:1905` | `Error reading track tags: %s` |
| `cyanrip_main.c:1959` | `Cover art destination(s):` |
| `cyanrip_main.c:1994` | `WARNING: tracks %i and %i resolve to the same file \"%s\", one will overwrite the other!` |
| `cyanrip_main.c:2005` | `Tracks:` |
| `cyanrip_main.c:2015` | `Track %i info:` |
| `cyanrip_main.c:2033` | `Error initializing decoder: %s` |
| `cyanrip_main.c:2042` | `Error initializing encoder: %s` |
| `cyanrip_main.c:2078` | `Error encoding: %s` |
| `cyanrip_main.c:2098` | `Invalid rip index %i, list has %i tracks!` |
| `cyanrip_main.c:2180` | `Error ripping: %s` |
| `discid.c:31` | `Unable to init SHA for DiscID: %s!` |
| `musicbrainz.c:116` | `Invalid disc number %i, release only has %i CDs` |
| `musicbrainz.c:121` | `Got empty medium list.` |
| `musicbrainz.c:127` | `No mediums match DiscID!` |
| `musicbrainz.c:155` | `Medium has no track list.` |
| `musicbrainz.c:193` | `Could not connect to MusicBrainz.` |
| `musicbrainz.c:201` | `Missing DiscID!` |
| `musicbrainz.c:212` | `MusicBrainz query failed: %s` |
| `musicbrainz.c:219` | `Connection failed, try again? Or disable via -N` |
| `musicbrainz.c:224` | `Error fetching/requesting/auth, this shouldn't happen.` |
| `musicbrainz.c:247` | `MusicBrainz lookup failed: DiscID has no associated releases.` |
| `musicbrainz.c:255` | `MusicBrainz lookup failed: no releases found for DiscID.` |
| `musicbrainz.c:259` | `Multiple releases found in database for DiscID %s:` |
| `musicbrainz.c:280` | `%i (ID: %s): %s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s` |
| `musicbrainz.c:294` | `Please specify which release to use by adding the -R argument with an index or ID.` |
| `musicbrainz.c:299` | `Invalid release index %i specified, only have %i releases!` |
| `musicbrainz.c:317` | `Release ID %s not found in release list for DiscID %s!` |
| `musicbrainz.c:348` | `Found MusicBrainz release: %s - %s` |
| `musicbrainz.c:362` | `MusicBrainz lookup failed, but DiscID has a matching stub, consider verifying the data and creating a release here:` |
| `musicbrainz.c:366` | `Unable to find release info for this CD, and metadata hasn't been manually added!` |
| `musicbrainz.c:370` | `Unable to find metadata for this CD, but metadata has been manually specified, continuing.` |
| `musicbrainz.c:376` | `Please help improve the MusicBrainz DB by submitting the disc info via the following URL:` |
| `musicbrainz.c:382` | `To continue add metadata via -a or -t, or ignore via -N!` |
| `naming.c:123` | `Error parsing string: %s!` |
| `naming.c:215` | `Invalid scheme syntax, unterminated \"{\"!` |
| `naming.c:229` | `Invalid scheme syntax, no \"#\"!` |
| `naming.c:243` | `Invalid scheme syntax, no terminating \"#\"!` |
| `naming.c:259` | `Invalid condition syntax!` |

**264 distinct stable lines.**

Field order within a block is fixed and is part of the contract. The golden
reference log in the handshake package is the authoritative example.

### P2a - Composed lines

Lines assembled into a buffer by a run of `snprintf()` and emitted through a
bare `"%s"`. The emitting call site shows a consumer nothing, so the pieces
are reconstructed here from the `snprintf` formats that build the buffer, in
source order. Segments after the first are conditional.

**`cyanrip_main.c:847`** - reaches logfile: **no, stdout only**

| # | Segment |
|---|---|
| 0 | `Ripping%strack %i, progress - %0.2f%%` |
| 1 | `, ETA - %ih %im` |
| 2 | `, ETA - %im` |
| 3 | `, ETA - %llds` |
| 4 | `, errors - %i` |
| 5 | ` ` |

Segment 0 is always present; the rest are appended conditionally. This is
**stable API**: the progress bar and ETA of at least one consumer are
driven by it.

**`cyanrip_main.c:1927`** - reaches logfile: yes

Not derivable: the buffer is not built by `snprintf` in this function.
It emits arbitrary text - here, the generated CUE sheet echoed back to
the terminal a line at a time. **Do not pattern-match this row**; a
pattern built from its `"%s"` would match every line in the log.

## P3 - Unstable wording, and stdout-only routing

**This section answers two independent questions, and a row can be here for
either.** Conflating them is what put `cyanrip_encode.c` and two other rows in
both P3 and P5 and made the membership look contradictory (Platterpus, round 5
A2):

- **Unstable wording** - the text may be reworded without a handshake round.
  Do not depend on the exact string.
- **stdout only** - the line never reaches a logfile, whatever its wording.

**Appearing here does not mean a line is harmless.** A line can be
stdout-only *and* a failure diagnostic; those rows are also in P5, and P5 is
the authority on whether something is reachable on a failure path. Match
P5 rows for error detection even when they appear here.

| File:line | Line | Reaches logfile? |
|---|---|---|
| `cyanrip_encode.c:108` | `%s folder: [%s] extension: %s%s` | **no, stdout only** |
| `cyanrip_encode.c:128` | `Encoder for %s not compiled in ffmpeg!` | **no, stdout only** |
| `cyanrip_main.c:781` | `\r` | **no, stdout only** |
| `cyanrip_main.c:847` | `%s` | **no, stdout only** |
| `cyanrip_main.c:928` | `Flushing encoders...` | **no, stdout only** |
| `cyanrip_main.c:970` | `Force quitting` | **no, stdout only** |
| `cyanrip_main.c:973` | `\rTrying to quit` | **no, stdout only** |
| `cyanrip_main.c:1378` | `Log \"%s\" checksum valid.` | **no, stdout only** |
| `cyanrip_main.c:1381` | `Log \"%s\" checksum mismatch, the file has been modified!` | **no, stdout only** |
| `cyanrip_main.c:1385` | `Log \"%s\" has data after the checksum, the file has been modified!` | **no, stdout only** |
| `cyanrip_main.c:1389` | `No FUN512 checksum found in \"%s\"!` | **no, stdout only** |
| `cyanrip_main.c:1393` | `Couldn't read \"%s\"!` | **no, stdout only** |
| `stall_watchdog.c:118` | `Still reading track %i - the read for LSN %i has not returned after %` | **no, stdout only** |
| `stall_watchdog.c:182` | `Track %i - the read for LSN %i returned after %` | **no, stdout only** |

Also unstable, and **not ours**: the loudness block FFmpeg's `ebur128` filter
prints (`Integrated loudness`, `Loudness range`, `Sample peak:`, `True peak:`, ...). That wording
belongs to libavfilter and moves when FFmpeg does. Prefer the
`Sample peak level:` and `True peak level:` lines in P2, which are ours,
are gated on a completed rip, and each say which peak they report.

## P4 - Exit codes

| Code | Meaning |
|---|---|
| `0` | Success: completed rip, `-I`, `-J`, `-h`, `-v`, or a `-Y` that validated |
| `1` | Every failure, without exception |

Distinct exit values found in the tree: `0`, `1`.

**There is no per-failure-class code.** Classification must come from the text,
which is why P5 exists. No non-zero exit is silent: argument parse failures
print before returning, and every other `return 1` in `main()` is preceded by a
`cyanrip_log()` call.

Argument validation runs **before the logfile is opened**, so that whole class of
diagnosis is **stdout only**. A consumer that reads only the logfile cannot see it.

## P5 - Fatal and error message inventory

Every string reachable on a failure path. Use this to derive error matching
rather than guessing prefixes.

**Evidence** says why each string is here, and is reported rather than folded
into a bare verdict so you can see which entries rest on the weaker test:

- `control flow` - the call is followed by `return 1`, a non-zero `exit()`,
  `return AVERROR(...)`, `total_error_count++`, or `goto fail`. Does not
  depend on how the message is worded.
- `wording` - the message begins like a diagnostic, but no failure exit was
  found near it. Either the exit is further away than the search window, or
  the message is a warning that does not end the run. **Treat these as
  possibly non-fatal.**
- `both` - the two agree.
- `goto end` / `wording + goto end` - the call is followed by `goto end`,
  which in `cyanrip_main.c` is *both* the ordinary success cleanup and the
  route several genuine aborts take (`Offset is unset!` leaves that way).
  It is reported as its own class because calling it fatal would file
  success lines as failures, and calling it non-fatal would drop real
  aborts. **Neither of us can settle these from the source alone; they need
  a run to classify.**

The search stops at the next `if`/`for`/`while`/`switch`, so a message is
only credited with an exit that is its own -- without that cut,
`Opening drive...` reads as fatal because the *next* statement's if-block
returns `AVERROR`. It deliberately does *not* stop at the next log call:
two arms of one if/else that both log and then converge on a single exit
must carry the same class.

| File:line | Message | Evidence | Reaches logfile? |
|---|---|---|---|
| `accurip.c:97` | `Unable to get AccuRIP DB data: missing CDDB ID!` | wording + goto end | yes |
| `accurip.c:129` | `Unable to get AccuRIP DB data: missing entry!` | wording + goto end | yes |
| `accurip.c:137` | `Unable to get AccuRIP DB data: %s%s` | wording + goto end | yes |
| `accurip.c:140` | `Unable to get AccuRIP DB data: %s!` | wording + goto end | yes |
| `accurip.c:176` | `AccuRIP DB data error, got unexpected number of bytes!` | goto end | yes |
| `cache_probe.c:116` | `Cache probe:    unknown (out of memory)` | control flow | yes |
| `coverart.c:51` | `Unable to init lavf context: %s!` | both | yes |
| `coverart.c:57` | `Unable to alloc stream!` | both | yes |
| `coverart.c:70` | `Couldn't open %s for writing: %s!` | both | yes |
| `coverart.c:82` | `Couldn't write header: %s!` | both | yes |
| `coverart.c:92` | `Error writing picture packet: %s!` | both | yes |
| `coverart.c:97` | `Error writing trailer: %s!` | both | yes |
| `coverart.c:177` | `Unable to get cover art \"%s\": not found!` | wording + goto end | yes |
| `coverart.c:186` | `Unable to get cover art \"%s\": %s%s!` | wording + goto end | yes |
| `coverart.c:189` | `Unable to get cover art \"%s\": %s!` | wording + goto end | yes |
| `coverart.c:262` | `Unable to open \"%s\": %s!` | wording + goto end | yes |
| `coverart.c:269` | `Unable to get cover image info: %s!` | wording + goto end | yes |
| `coverart.c:299` | `Error demuxing cover image: %s!` | wording + goto end | yes |
| `cue_writer.c:39` | `Couldn't open path \"%s\" for writing: %s!Invalid folder name? Try -D <folder>.` | both | yes |
| `cyanrip_encode.c:128` | `Encoder for %s not compiled in ffmpeg!` | control flow | **no, stdout only** |
| `cyanrip_encode.c:364` | `Error creating filter source: %s!` | both | yes |
| `cyanrip_encode.c:375` | `Error creating filter sink: %s!` | both | yes |
| `cyanrip_encode.c:389` | `Error setting filter sample format: %s!` | both | yes |
| `cyanrip_encode.c:397` | `Error setting filter channel layout: %s!` | both | yes |
| `cyanrip_encode.c:406` | `Error setting filter sample rate: %s!` | both | yes |
| `cyanrip_encode.c:440` | `Error initializing filter sink: %s!` | both | yes |
| `cyanrip_encode.c:474` | `Error parsing filter graph: %s!` | both | yes |
| `cyanrip_encode.c:480` | `Error configuring filter graph: %s!` | both | yes |
| `cyanrip_encode.c:541` | `Error pushing frame to FIFO: %s!` | wording | yes |
| `cyanrip_encode.c:614` | `Error filtering frame: %s!` | both | yes |
| `cyanrip_encode.c:692` | `Error allocating frame!` | both | yes |
| `cyanrip_encode.c:704` | `Error allocating frame: %s!` | both | yes |
| `cyanrip_encode.c:839` | `Could not alloc swr context!` | wording | yes |
| `cyanrip_encode.c:857` | `Could not init swr context!` | wording | yes |
| `cyanrip_encode.c:1032` | `Error while encoding: %s!` | both | yes |
| `cyanrip_encode.c:1054` | `Error encoding: %s!` | both | yes |
| `cyanrip_encode.c:1085` | `Error pushing packet to FIFO: %s!` | both | yes |
| `cyanrip_encode.c:1092` | `Error writing packet: %s!` | both | yes |
| `cyanrip_encode.c:1122` | `Error writing to file: %s!` | both | yes |
| `cyanrip_encode.c:1245` | `Codec not found (not compiled in lavc?)!` | control flow | yes |
| `cyanrip_encode.c:1254` | `Unable to init output avctx!` | both | yes |
| `cyanrip_encode.c:1265` | `Could not open output codec context!` | both | yes |
| `cyanrip_encode.c:1272` | `Couldn't copy codec params!` | both | yes |
| `cyanrip_encode.c:1279` | `Couldn't open %s: %s! Invalid folder name? Try -D <folder>.` | both | yes |
| `cyanrip_main.c:188` | `No device specified and unable to get default device!` | both | yes |
| `cyanrip_main.c:196` | `Unable to open device: %s` | both | yes |
| `cyanrip_main.c:205` | `Unable to init cddap context!` | wording | yes |
| `cyanrip_main.c:207` | `cdio: \"%s\"` | control flow | yes |
| `cyanrip_main.c:221` | `Unable to open device!` | both | yes |
| `cyanrip_main.c:230` | `Device does not support changing speeds!` | control flow | yes |
| `cyanrip_main.c:247` | `Unable to init paranoia!` | both | yes |
| `cyanrip_main.c:292` | `Invalid number of tracks: %i!` | both | yes |
| `cyanrip_main.c:315` | `CDIO returned invalid track %i end LSN` | control flow | yes |
| `cyanrip_main.c:468` | `cdio error: %s` | control flow | yes |
| `cyanrip_main.c:475` | `Frame read failed!` | control flow | yes |
| `cyanrip_main.c:562` | `Stopping, offset finding incomplete!` | wording + goto end | yes |
| `cyanrip_main.c:647` | `Unable to read track %i subchannel info!` | wording | yes |
| `cyanrip_main.c:720` | `Error in decoding/sending frame: %s` | both | yes |
| `cyanrip_main.c:732` | `Drive media changed, stopping!` | both | yes |
| `cyanrip_main.c:763` | `Stopping, ripping incomplete!` | wording | yes |
| `cyanrip_main.c:881` | `Done; (%i out of %i matches for current checksum %08X)` | goto finalize_ripping | yes |
| `cyanrip_main.c:887` | `Done; (no matches found, but hit repeat limit of %i)` | goto finalize_ripping | yes |
| `cyanrip_main.c:918` | `Error in encoding: %s` | wording + goto end | yes |
| `cyanrip_main.c:934` | `Error sending flush signal to encoders: %s` | wording | yes |
| `cyanrip_main.c:970` | `Force quitting` | control flow | **no, stdout only** |
| `cyanrip_main.c:1389` | `No FUN512 checksum found in \"%s\"!` | control flow | **no, stdout only** |
| `cyanrip_main.c:1393` | `Couldn't read \"%s\"!` | both | **no, stdout only** |
| `cyanrip_main.c:1443` | `Invalid paranoia level %i must be between 0 and %i!` | both | yes |
| `cyanrip_main.c:1456` | `Invalid max coverart size %i (must be 250, 500, 1200 or -1)` | both | yes |
| `cyanrip_main.c:1468` | `Invalid sanitation method %s` | both | yes |
| `cyanrip_main.c:1480` | `Invalid release index %i!` | both | yes |
| `cyanrip_main.c:1489` | `Invalid discnumber %i` | both | yes |
| `cyanrip_main.c:1496` | `Invalid totaldiscs %i` | both | yes |
| `cyanrip_main.c:1500` | `discnumber %i is larger than totaldiscs %i` | control flow | yes |
| `cyanrip_main.c:1521` | `Invalid format \"%s\"` | both | yes |
| `cyanrip_main.c:1526` | `Duplicated format \"%s\"` | control flow | yes |
| `cyanrip_main.c:1541` | `Duplicated rip idx %i` | control flow | yes |
| `cyanrip_main.c:1555` | `Invalid track idx for pregap: %i` | both | yes |
| `cyanrip_main.c:1561` | `Missing pregap action` | both | yes |
| `cyanrip_main.c:1569` | `Invalid pregap action %s` | both | yes |
| `cyanrip_main.c:1600` | `No cover art location specified for \"%s\"` | both | yes |
| `cyanrip_main.c:1609` | `Invalid track idx for cover art: %i` | both | yes |
| `cyanrip_main.c:1615` | `Cover art already specified for track idx %i!` | control flow | yes |
| `cyanrip_main.c:1627` | `Cover art \"%s\" already specified!` | control flow | yes |
| `cyanrip_main.c:1633` | `Too many cover arts specified!` | control flow | yes |
| `cyanrip_main.c:1643` | `Directory name scheme must contain {format} with multiple output formats!` | control flow | yes |
| `cyanrip_main.c:1648` | `-J (only generate a CUE sheet) cannot be used with -I (only print info)!` | both | yes |
| `cyanrip_main.c:1672` | `Offset is unset! To continue with an offset of 0, run with -s 0!` | goto end | yes |
| `cyanrip_main.c:1797` | `Error reading album tags: %s` | both | yes |
| `cyanrip_main.c:1889` | `Invalid track number %i, list has %i tracks!` | both | yes |
| `cyanrip_main.c:1905` | `Error reading track tags: %s` | both | yes |
| `cyanrip_main.c:1927` | `%s` | goto end | yes |
| `cyanrip_main.c:2033` | `Error initializing decoder: %s` | both | yes |
| `cyanrip_main.c:2042` | `Error initializing encoder: %s` | both | yes |
| `cyanrip_main.c:2078` | `Error encoding: %s` | wording + goto end | yes |
| `cyanrip_main.c:2098` | `Invalid rip index %i, list has %i tracks!` | both | yes |
| `cyanrip_main.c:2180` | `Error ripping: %s` | wording + goto end | yes |
| `discid.c:31` | `Unable to init SHA for DiscID: %s!` | wording | yes |
| `musicbrainz.c:116` | `Invalid disc number %i, release only has %i CDs` | both | yes |
| `musicbrainz.c:121` | `Got empty medium list.` | control flow | yes |
| `musicbrainz.c:193` | `Could not connect to MusicBrainz.` | both | yes |
| `musicbrainz.c:201` | `Missing DiscID!` | wording | yes |
| `musicbrainz.c:224` | `Error fetching/requesting/auth, this shouldn't happen.` | both | yes |
| `musicbrainz.c:247` | `MusicBrainz lookup failed: DiscID has no associated releases.` | goto end_meta | yes |
| `musicbrainz.c:255` | `MusicBrainz lookup failed: no releases found for DiscID.` | goto end_meta | yes |
| `musicbrainz.c:294` | `Please specify which release to use by adding the -R argument with an index or ID.` | control flow | yes |
| `musicbrainz.c:299` | `Invalid release index %i specified, only have %i releases!` | both | yes |
| `musicbrainz.c:317` | `Release ID %s not found in release list for DiscID %s!` | control flow | yes |
| `musicbrainz.c:362` | `MusicBrainz lookup failed, but DiscID has a matching stub, consider verifying the data and creating a release here:` | control flow | yes |
| `musicbrainz.c:366` | `Unable to find release info for this CD, and metadata hasn't been manually added!` | both | yes |
| `musicbrainz.c:370` | `Unable to find metadata for this CD, but metadata has been manually specified, continuing.` | wording | yes |
| `naming.c:123` | `Error parsing string: %s!` | wording | yes |
| `naming.c:215` | `Invalid scheme syntax, unterminated \"{\"!` | both | yes |
| `naming.c:229` | `Invalid scheme syntax, no \"#\"!` | both | yes |
| `naming.c:243` | `Invalid scheme syntax, no terminating \"#\"!` | both | yes |
| `naming.c:259` | `Invalid condition syntax!` | both | yes |

**116 distinct strings.** By evidence: 63 both, 21 control flow, 11 wording, 3 goto end, 14 wording + goto end.

The `control flow` and `both` rows total 84 strings proven reachable on a
failure path without reference to their wording. That subset is the one to
build a hard failure classifier on.

