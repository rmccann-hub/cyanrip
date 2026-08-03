# cyanrip provider contract

**Generated** by `tools/gen-provider-contract.py` from the source tree and the
built binary. Do not edit by hand -- regenerate. A hand-written contract goes
stale silently, which is the failure this file exists to prevent.

Build: `cyanrip 0.9.4-rc1 (platterpus-fork-g<commit>)`

This is the provider half of the seam. Platterpus generates the consumer half
(`docs/cyanrip-consumer-contract.md`) from its parser tables. Neither side
describes behaviour it does not have.

## P1 - Inputs: every command line flag

From the binary's own `--help`, so it cannot drift from what the build accepts.


### General

| Short | Long | Meaning |
|---|---|---|
| `-h` | `--help` | Print this text |
| `-v` | `--version` | Print the version number |

### Ripping options

| Short | Long | Meaning |
|---|---|---|
| `-d` | `--device` | Set device path (can be a TOC file) |
| `-s` | `--offset` | CD drive offset in samples (default: 0) |
| `-r` | `--retries` | Maximum number of retries for frames and repeated rips (default: 10) |
| `-Z` | `--repeat-rips` | Rip tracks until checksums match N times (for damaged CDs) (default: 0) |
| `-S` | `--speed` | Set drive speed (default: 0) |
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

**37 flags total.** Notes that are not derivable from `--help`:

- `-O` is **overread**, not an options passthrough. Never repurpose it.
- `-v` is version; there is no `-V`.
- `-J` and `-I` are mutually exclusive; combining them exits 1.
- `-d` accepts a device path **or** a TOC/CUE/NRG image file.
- `-a`/`-t` values are `:`-separated; a literal colon must be escaped `\:`.
- `-t N=` and `-l N` are 1-based and validated against the disc's real track
  count; out of range exits 1 with a message naming both numbers.
- Multiple `-o` formats produce **one logfile and one cue per format**.

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
| `cyanrip_encode.c:361` | `Error creating filter source: %s!` |
| `cyanrip_encode.c:372` | `Error creating filter sink: %s!` |
| `cyanrip_encode.c:386` | `Error setting filter sample format: %s!` |
| `cyanrip_encode.c:394` | `Error setting filter channel layout: %s!` |
| `cyanrip_encode.c:403` | `Error setting filter sample rate: %s!` |
| `cyanrip_encode.c:437` | `Error initializing filter sink: %s!` |
| `cyanrip_encode.c:471` | `Error parsing filter graph: %s!` |
| `cyanrip_encode.c:477` | `Error configuring filter graph: %s!` |
| `cyanrip_encode.c:536` | `Error pushing frame to FIFO: %s!` |
| `cyanrip_encode.c:555` | `Error filtering frame: %s!` |
| `cyanrip_encode.c:633` | `Error allocating frame!` |
| `cyanrip_encode.c:645` | `Error allocating frame: %s!` |
| `cyanrip_encode.c:757` | `Album Loudness` |
| `cyanrip_encode.c:776` | `Could not alloc swr context!` |
| `cyanrip_encode.c:794` | `Could not init swr context!` |
| `cyanrip_encode.c:969` | `Error while encoding: %s!` |
| `cyanrip_encode.c:991` | `Error encoding: %s!` |
| `cyanrip_encode.c:1022` | `Error pushing packet to FIFO: %s!` |
| `cyanrip_encode.c:1029` | `Error writing packet: %s!` |
| `cyanrip_encode.c:1059` | `Error writing to file: %s!` |
| `cyanrip_encode.c:1182` | `Codec not found (not compiled in lavc?)!` |
| `cyanrip_encode.c:1191` | `Unable to init output avctx!` |
| `cyanrip_encode.c:1202` | `Could not open output codec context!` |
| `cyanrip_encode.c:1209` | `Couldn't copy codec params!` |
| `cyanrip_encode.c:1216` | `Couldn't open %s: %s! Invalid folder name? Try -D <folder>.` |
| `cyanrip_log.c:49` | `%s%s:` |
| `cyanrip_log.c:52` | `%s` |
| `cyanrip_log.c:62` | `CD-TEXT:        none reported by libcdio (absent, or unreadable by this driver)` |
| `cyanrip_log.c:67` | `CD-TEXT:        present (%s, %i disc %s, %i of %i tracks tagged)` |
| `cyanrip_log.c:86` | `Cache defeat:   not in use (paranoia disabled)` |
| `cyanrip_log.c:97` | `Cache defeat:   %i sector%s modelled (disc image, no drive cache)` |
| `cyanrip_log.c:102` | `Cache defeat:   %i sector%s modelled (drive cache size not probed)` |
| `cyanrip_log.c:123` | `Pregap LSN:  %i (duration: %s)` |
| `cyanrip_log.c:125` | `Pregap length: %i frames` |
| `cyanrip_log.c:127` | `Pregap LSN:  unknown (sub-channel unreadable)` |
| `cyanrip_log.c:129` | `Pregap LSN:  unknown (sub-channel CRC mismatches)` |
| `cyanrip_log.c:131` | `Pregap LSN:  none` |
| `cyanrip_log.c:137` | `Pregap source: sub-channel (not signalled by TOC)` |
| `cyanrip_log.c:139` | `Pregap source: lead-in` |
| `cyanrip_log.c:141` | `Pregap source: TOC` |
| `cyanrip_log.c:144` | `Prepended:   %i frames of silence` |
| `cyanrip_log.c:145` | `Start LSN:   %i` |
| `cyanrip_log.c:147` | `(with offset: %i)` |
| `cyanrip_log.c:151` | `End LSN:     %i` |
| `cyanrip_log.c:158` | `Appended:    %i frames of silence` |
| `cyanrip_log.c:166` | `Preemphasis:` |
| `cyanrip_log.c:168` | `none detected` |
| `cyanrip_log.c:171` | `(deemphasis forced)` |
| `cyanrip_log.c:176` | `present (subcode)` |
| `cyanrip_log.c:178` | `present (TOC)` |
| `cyanrip_log.c:181` | `(deemphasis applied)` |
| `cyanrip_log.c:186` | `Properties:` |
| `cyanrip_log.c:189` | `Data bytes:  %i (%.2f Mib)` |
| `cyanrip_log.c:192` | `Frames:      %u` |
| `cyanrip_log.c:198` | `Duration:    %s` |
| `cyanrip_log.c:199` | `Samples:     %u` |
| `cyanrip_log.c:202` | `Peak level:  %.1f%%` |
| `cyanrip_log.c:206` | `True peak level: %.1f dBFS` |
| `cyanrip_log.c:209` | `Extraction speed:  %.1fx` |
| `cyanrip_log.c:211` | `Elapsed:            %.2f s` |
| `cyanrip_log.c:219` | `EAC CRC32:     %08X` |
| `cyanrip_log.c:221` | `(after %i rips)` |
| `cyanrip_log.c:228` | `Secure re-read:  converged after %i reads` |
| `cyanrip_log.c:231` | `Secure re-read:  did NOT converge after %i reads (repeat limit hit)` |
| `cyanrip_log.c:236` | `Secure re-read:  not attempted` |
| `cyanrip_log.c:240` | `Accurip:       %s` |
| `cyanrip_log.c:244` | `(max confidence: %i)` |
| `cyanrip_log.c:252` | `Accurip v1:  %08X` |
| `cyanrip_log.c:254` | `(accurately ripped, confidence %i)` |
| `cyanrip_log.c:256` | `(not found, either a new pressing, or bad rip)` |
| `cyanrip_log.c:260` | `Accurip v2:  %08X` |
| `cyanrip_log.c:271` | `Accurip 450: %08X` |
| `cyanrip_log.c:273` | `(match found, confidence %i, but a checksum of 0 is meaningless)` |
| `cyanrip_log.c:276` | `(matches Accurip DB, confidence %i, track is partially accurately ripped)` |
| `cyanrip_log.c:279` | `(not found)` |
| `cyanrip_log.c:286` | `Metadata:` |
| `cyanrip_log.c:296` | `%s:` |
| `cyanrip_log.c:308` | `CD-TEXT:` |
| `cyanrip_log.c:332` | `Embedded cover art:    %s: %s` |
| `cyanrip_log.c:335` | `Embedded cover art:    %s: %ix%i %s` |
| `cyanrip_log.c:339` | `File(s):` |
| `cyanrip_log.c:353` | `cyanrip %s (%s-g%s)` |
| `cyanrip_log.c:356` | `Invoked as:     %s` |
| `cyanrip_log.c:360` | `Drive used:     error retrieving drive info` |
| `cyanrip_log.c:362` | `Drive used:     %s %s (revision %s)` |
| `cyanrip_log.c:363` | `System device:  %s` |
| `cyanrip_log.c:365` | `Device model:   %s` |
| `cyanrip_log.c:366` | `Offset:         %c%i %s` |
| `cyanrip_log.c:368` | `%s%c%i %s` |
| `cyanrip_log.c:373` | `%s%s` |
| `cyanrip_log.c:377` | `Speed:          %ix` |
| `cyanrip_log.c:379` | `Speed:          default (%s)` |
| `cyanrip_log.c:381` | `C2 errors:      %s` |
| `cyanrip_log.c:385` | `Paranoia level: %s` |
| `cyanrip_log.c:389` | `Paranoia level: %i` |
| `cyanrip_log.c:390` | `Frame retries:  %i` |
| `cyanrip_log.c:392` | `HDCD decoding:  %s` |
| `cyanrip_log.c:394` | `Album Art:      %s` |
| `cyanrip_log.c:398` | `%s%s%s%s%s` |
| `cyanrip_log.c:406` | `Outputs:` |
| `cyanrip_log.c:412` | `Disc tracks:    %i` |
| `cyanrip_log.c:413` | `Tracks to rip:  %s` |
| `cyanrip_log.c:416` | `%i%s` |
| `cyanrip_log.c:430` | `AccurateRip:    %s` |
| `cyanrip_log.c:436` | `Total time:     %s` |
| `cyanrip_log.c:462` | `Tracks ripped accurately: %i/%i` |
| `cyanrip_log.c:464` | `Tracks ripped partially accurately: %i/%i` |
| `cyanrip_log.c:470` | `Paranoia status counts:` |
| `cyanrip_log.c:479` | `%lu` |
| `cyanrip_log.c:503` | `Ripping errors: %i` |
| `cyanrip_log.c:510` | `Rip completed:  no (interrupted by user, %i of %i tracks)` |
| `cyanrip_log.c:513` | `Rip completed:  yes (%i of %i tracks)` |
| `cyanrip_log.c:516` | `Ripping finished at %s` |
| `cyanrip_main.c:184` | `No device specified and unable to get default device!` |
| `cyanrip_main.c:192` | `Unable to open device: %s` |
| `cyanrip_main.c:201` | `Unable to init cddap context!` |
| `cyanrip_main.c:203` | `cdio: \"%s\"` |
| `cyanrip_main.c:214` | `Opening drive...` |
| `cyanrip_main.c:217` | `Unable to open device!` |
| `cyanrip_main.c:226` | `Device does not support changing speeds!` |
| `cyanrip_main.c:234` | `cdio error: %s` |
| `cyanrip_main.c:243` | `Unable to init paranoia!` |
| `cyanrip_main.c:272` | `Invalid number of tracks: %i!` |
| `cyanrip_main.c:295` | `CDIO returned invalid track %i end LSN` |
| `cyanrip_main.c:444` | `Frame read failed!` |
| `cyanrip_main.c:521` | `Loading data for track %i...` |
| `cyanrip_main.c:528` | `Stopping, offset finding incomplete!` |
| `cyanrip_main.c:536` | `Data loaded, searching for offsets...` |
| `cyanrip_main.c:545` | `Nothing found for track %i%s` |
| `cyanrip_main.c:550` | `Offset of %c%i found in track %i%s` |
| `cyanrip_main.c:555` | `Offset of %c%i confirmed (confidence: %i) in track %i%s` |
| `cyanrip_main.c:559` | `New offset of %c%i found at track %i, scrapping old offset of %c%i%s` |
| `cyanrip_main.c:573` | `No track had AccuRip entry, cannot find offset!` |
| `cyanrip_main.c:575` | `No track was long enough, unable to find drive offset!` |
| `cyanrip_main.c:577` | `Was not able to find drive offset with a radius of %i frames, trying again with a larger radius...` |
| `cyanrip_main.c:583` | `Drive offset of %c%i found (confidence: %i)!` |
| `cyanrip_main.c:613` | `Unable to read track %i subchannel info!` |
| `cyanrip_main.c:629` | `Track %i is data:` |
| `cyanrip_main.c:678` | `Error in decoding/sending frame: %s` |
| `cyanrip_main.c:690` | `Drive media changed, stopping!` |
| `cyanrip_main.c:721` | `Stopping, ripping incomplete!` |
| `cyanrip_main.c:839` | `Done; (%i out of %i matches for current checksum %08X)` |
| `cyanrip_main.c:845` | `Done; (no matches found, but hit repeat limit of %i)` |
| `cyanrip_main.c:861` | `Repeating ripping (%i out of %i matches for current checksum %08X)` |
| `cyanrip_main.c:876` | `Error in encoding: %s` |
| `cyanrip_main.c:892` | `Error sending flush signal to encoders: %s` |
| `cyanrip_main.c:899` | `Track %i ripped and encoded with errors.` |
| `cyanrip_main.c:901` | `Track %i ripped and encoded successfully!` |
| `cyanrip_main.c:981` | `Gaps:` |
| `cyanrip_main.c:986` | `%i frame gap between lead-in and track 1 pregap, merging into pregap` |
| `cyanrip_main.c:993` | `%i frame unmarked gap between lead-in and track 1, marking as a pregap` |
| `cyanrip_main.c:1015` | `%i frame pregap in track %i,` |
| `cyanrip_main.c:1022` | `unmerged` |
| `cyanrip_main.c:1024` | `merging into track %i` |
| `cyanrip_main.c:1030` | `dropping` |
| `cyanrip_main.c:1036` | `merging` |
| `cyanrip_main.c:1043` | `splitting off into a new track, number %i` |
| `cyanrip_main.c:1084` | `%i frame discontinuity between tracks %i and %i,` |
| `cyanrip_main.c:1089` | `padding track %i` |
| `cyanrip_main.c:1092` | `ignoring` |
| `cyanrip_main.c:1100` | `%i frame gap between last track and lead-out, padding track` |
| `cyanrip_main.c:1165` | `Can't init signal handler!` |
| `cyanrip_main.c:1385` | `Invalid paranoia level %i must be between 0 and %i!` |
| `cyanrip_main.c:1398` | `Invalid max coverart size %i (must be 250, 500, 1200 or -1)` |
| `cyanrip_main.c:1410` | `Invalid sanitation method %s` |
| `cyanrip_main.c:1422` | `Invalid release index %i!` |
| `cyanrip_main.c:1431` | `Invalid discnumber %i` |
| `cyanrip_main.c:1438` | `Invalid totaldiscs %i` |
| `cyanrip_main.c:1442` | `discnumber %i is larger than totaldiscs %i` |
| `cyanrip_main.c:1455` | `Supported output codecs:` |
| `cyanrip_main.c:1463` | `Invalid format \"%s\"` |
| `cyanrip_main.c:1468` | `Duplicated format \"%s\"` |
| `cyanrip_main.c:1483` | `Duplicated rip idx %i` |
| `cyanrip_main.c:1497` | `Invalid track idx for pregap: %i` |
| `cyanrip_main.c:1503` | `Missing pregap action` |
| `cyanrip_main.c:1511` | `Invalid pregap action %s` |
| `cyanrip_main.c:1542` | `No cover art location specified for \"%s\"` |
| `cyanrip_main.c:1551` | `Invalid track idx for cover art: %i` |
| `cyanrip_main.c:1557` | `Cover art already specified for track idx %i!` |
| `cyanrip_main.c:1569` | `Cover art \"%s\" already specified!` |
| `cyanrip_main.c:1575` | `Too many cover arts specified!` |
| `cyanrip_main.c:1585` | `Directory name scheme must contain {format} with multiple output formats!` |
| `cyanrip_main.c:1590` | `-J (only generate a CUE sheet) cannot be used with -I (only print info)!` |
| `cyanrip_main.c:1606` | `Searching for drive offset, enabling AccuRip and disabling MusicBrainz and Cover art fetching...` |
| `cyanrip_main.c:1614` | `Offset is unset! To continue with an offset of 0, run with -s 0!` |
| `cyanrip_main.c:1694` | `MusicBrainz URL:%s` |
| `cyanrip_main.c:1738` | `Error reading album tags: %s` |
| `cyanrip_main.c:1768` | `Log(s) will be written to:` |
| `cyanrip_main.c:1776` | `CUE files will be written to:` |
| `cyanrip_main.c:1808` | `Invalid track number %i, list has %i tracks!` |
| `cyanrip_main.c:1824` | `Error reading track tags: %s` |
| `cyanrip_main.c:1878` | `Cover art destination(s):` |
| `cyanrip_main.c:1913` | `WARNING: tracks %i and %i resolve to the same file \"%s\", one will overwrite the other!` |
| `cyanrip_main.c:1924` | `Tracks:` |
| `cyanrip_main.c:1934` | `Track %i info:` |
| `cyanrip_main.c:1952` | `Error initializing decoder: %s` |
| `cyanrip_main.c:1961` | `Error initializing encoder: %s` |
| `cyanrip_main.c:1995` | `Error encoding: %s` |
| `cyanrip_main.c:2015` | `Invalid rip index %i, list has %i tracks!` |
| `cyanrip_main.c:2097` | `Error ripping: %s` |
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

**249 distinct stable lines.**

Field order within a block is fixed and is part of the contract. The golden
reference log in the handshake package is the authoritative example.

## P3 - Unstable lines: reworded without a handshake

Do not parse these. Most are stdout-only and never reach the logfile at all.

| File:line | Line | Reaches logfile? |
|---|---|---|
| `cyanrip_encode.c:105` | `%s folder: [%s] extension: %s%s` | **no, stdout only** |
| `cyanrip_encode.c:125` | `Encoder for %s not compiled in ffmpeg!` | **no, stdout only** |
| `cyanrip_main.c:739` | `\r` | **no, stdout only** |
| `cyanrip_main.c:805` | `%s` | **no, stdout only** |
| `cyanrip_main.c:886` | `Flushing encoders...` | **no, stdout only** |
| `cyanrip_main.c:926` | `Force quitting` | **no, stdout only** |
| `cyanrip_main.c:929` | `\rTrying to quit` | **no, stdout only** |
| `cyanrip_main.c:1323` | `Log \"%s\" checksum valid.` | **no, stdout only** |
| `cyanrip_main.c:1326` | `Log \"%s\" checksum mismatch, the file has been modified!` | **no, stdout only** |
| `cyanrip_main.c:1330` | `Log \"%s\" has data after the checksum, the file has been modified!` | **no, stdout only** |
| `cyanrip_main.c:1334` | `No FUN512 checksum found in \"%s\"!` | **no, stdout only** |
| `cyanrip_main.c:1338` | `Couldn't read \"%s\"!` | **no, stdout only** |

Also unstable, and **not ours**: the loudness block FFmpeg's `ebur128` filter
prints (`Integrated loudness`, `Loudness range`, `Sample peak:`, `True peak:`, ...). That wording
belongs to libavfilter and moves when FFmpeg does. Prefer the `Peak level:`
line in P2, which is ours and is gated on a completed rip.

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

Every string a failure can print. Use this to derive error matching rather than
guessing prefixes.

| File:line | Message |
|---|---|
| `accurip.c:97` | `Unable to get AccuRIP DB data: missing CDDB ID!` |
| `accurip.c:129` | `Unable to get AccuRIP DB data: missing entry!` |
| `accurip.c:137` | `Unable to get AccuRIP DB data: %s%s` |
| `accurip.c:140` | `Unable to get AccuRIP DB data: %s!` |
| `coverart.c:51` | `Unable to init lavf context: %s!` |
| `coverart.c:57` | `Unable to alloc stream!` |
| `coverart.c:70` | `Couldn't open %s for writing: %s!` |
| `coverart.c:82` | `Couldn't write header: %s!` |
| `coverart.c:92` | `Error writing picture packet: %s!` |
| `coverart.c:97` | `Error writing trailer: %s!` |
| `coverart.c:177` | `Unable to get cover art \"%s\": not found!` |
| `coverart.c:186` | `Unable to get cover art \"%s\": %s%s!` |
| `coverart.c:189` | `Unable to get cover art \"%s\": %s!` |
| `coverart.c:262` | `Unable to open \"%s\": %s!` |
| `coverart.c:269` | `Unable to get cover image info: %s!` |
| `coverart.c:299` | `Error demuxing cover image: %s!` |
| `cue_writer.c:39` | `Couldn't open path \"%s\" for writing: %s!Invalid folder name? Try -D <folder>.` |
| `cyanrip_encode.c:361` | `Error creating filter source: %s!` |
| `cyanrip_encode.c:372` | `Error creating filter sink: %s!` |
| `cyanrip_encode.c:386` | `Error setting filter sample format: %s!` |
| `cyanrip_encode.c:394` | `Error setting filter channel layout: %s!` |
| `cyanrip_encode.c:403` | `Error setting filter sample rate: %s!` |
| `cyanrip_encode.c:437` | `Error initializing filter sink: %s!` |
| `cyanrip_encode.c:471` | `Error parsing filter graph: %s!` |
| `cyanrip_encode.c:477` | `Error configuring filter graph: %s!` |
| `cyanrip_encode.c:536` | `Error pushing frame to FIFO: %s!` |
| `cyanrip_encode.c:555` | `Error filtering frame: %s!` |
| `cyanrip_encode.c:633` | `Error allocating frame!` |
| `cyanrip_encode.c:645` | `Error allocating frame: %s!` |
| `cyanrip_encode.c:776` | `Could not alloc swr context!` |
| `cyanrip_encode.c:794` | `Could not init swr context!` |
| `cyanrip_encode.c:969` | `Error while encoding: %s!` |
| `cyanrip_encode.c:991` | `Error encoding: %s!` |
| `cyanrip_encode.c:1022` | `Error pushing packet to FIFO: %s!` |
| `cyanrip_encode.c:1029` | `Error writing packet: %s!` |
| `cyanrip_encode.c:1059` | `Error writing to file: %s!` |
| `cyanrip_encode.c:1191` | `Unable to init output avctx!` |
| `cyanrip_encode.c:1202` | `Could not open output codec context!` |
| `cyanrip_encode.c:1209` | `Couldn't copy codec params!` |
| `cyanrip_encode.c:1216` | `Couldn't open %s: %s! Invalid folder name? Try -D <folder>.` |
| `cyanrip_main.c:184` | `No device specified and unable to get default device!` |
| `cyanrip_main.c:192` | `Unable to open device: %s` |
| `cyanrip_main.c:201` | `Unable to init cddap context!` |
| `cyanrip_main.c:217` | `Unable to open device!` |
| `cyanrip_main.c:243` | `Unable to init paranoia!` |
| `cyanrip_main.c:272` | `Invalid number of tracks: %i!` |
| `cyanrip_main.c:528` | `Stopping, offset finding incomplete!` |
| `cyanrip_main.c:613` | `Unable to read track %i subchannel info!` |
| `cyanrip_main.c:678` | `Error in decoding/sending frame: %s` |
| `cyanrip_main.c:690` | `Drive media changed, stopping!` |
| `cyanrip_main.c:721` | `Stopping, ripping incomplete!` |
| `cyanrip_main.c:876` | `Error in encoding: %s` |
| `cyanrip_main.c:892` | `Error sending flush signal to encoders: %s` |
| `cyanrip_main.c:1338` | `Couldn't read \"%s\"!` |
| `cyanrip_main.c:1385` | `Invalid paranoia level %i must be between 0 and %i!` |
| `cyanrip_main.c:1398` | `Invalid max coverart size %i (must be 250, 500, 1200 or -1)` |
| `cyanrip_main.c:1410` | `Invalid sanitation method %s` |
| `cyanrip_main.c:1422` | `Invalid release index %i!` |
| `cyanrip_main.c:1431` | `Invalid discnumber %i` |
| `cyanrip_main.c:1438` | `Invalid totaldiscs %i` |
| `cyanrip_main.c:1463` | `Invalid format \"%s\"` |
| `cyanrip_main.c:1497` | `Invalid track idx for pregap: %i` |
| `cyanrip_main.c:1503` | `Missing pregap action` |
| `cyanrip_main.c:1511` | `Invalid pregap action %s` |
| `cyanrip_main.c:1542` | `No cover art location specified for \"%s\"` |
| `cyanrip_main.c:1551` | `Invalid track idx for cover art: %i` |
| `cyanrip_main.c:1590` | `-J (only generate a CUE sheet) cannot be used with -I (only print info)!` |
| `cyanrip_main.c:1738` | `Error reading album tags: %s` |
| `cyanrip_main.c:1808` | `Invalid track number %i, list has %i tracks!` |
| `cyanrip_main.c:1824` | `Error reading track tags: %s` |
| `cyanrip_main.c:1952` | `Error initializing decoder: %s` |
| `cyanrip_main.c:1961` | `Error initializing encoder: %s` |
| `cyanrip_main.c:1995` | `Error encoding: %s` |
| `cyanrip_main.c:2015` | `Invalid rip index %i, list has %i tracks!` |
| `cyanrip_main.c:2097` | `Error ripping: %s` |
| `discid.c:31` | `Unable to init SHA for DiscID: %s!` |
| `musicbrainz.c:116` | `Invalid disc number %i, release only has %i CDs` |
| `musicbrainz.c:193` | `Could not connect to MusicBrainz.` |
| `musicbrainz.c:201` | `Missing DiscID!` |
| `musicbrainz.c:224` | `Error fetching/requesting/auth, this shouldn't happen.` |
| `musicbrainz.c:299` | `Invalid release index %i specified, only have %i releases!` |
| `musicbrainz.c:366` | `Unable to find release info for this CD, and metadata hasn't been manually added!` |
| `musicbrainz.c:370` | `Unable to find metadata for this CD, but metadata has been manually specified, continuing.` |
| `naming.c:123` | `Error parsing string: %s!` |
| `naming.c:215` | `Invalid scheme syntax, unterminated \"{\"!` |
| `naming.c:229` | `Invalid scheme syntax, no \"#\"!` |
| `naming.c:243` | `Invalid scheme syntax, no terminating \"#\"!` |
| `naming.c:259` | `Invalid condition syntax!` |

**88 distinct strings.**

