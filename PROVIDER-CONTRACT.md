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
| `cyanrip_log.c:50` | `%s%s:` |
| `cyanrip_log.c:53` | `%s` |
| `cyanrip_log.c:63` | `CD-TEXT:        none reported by libcdio (absent, or unreadable by this driver)` |
| `cyanrip_log.c:68` | `CD-TEXT:        present (%s, %i disc %s, %i of %i tracks tagged)` |
| `cyanrip_log.c:87` | `Cache defeat:   not in use (paranoia disabled)` |
| `cyanrip_log.c:98` | `Cache defeat:   %i sector%s modelled (disc image, no drive cache)` |
| `cyanrip_log.c:103` | `Cache defeat:   %i sector%s modelled (drive cache size not probed)` |
| `cyanrip_log.c:122` | `%s%s` |
| `cyanrip_log.c:126` | `%lu` |
| `cyanrip_log.c:166` | `Pregap LSN:  %i (duration: %s)` |
| `cyanrip_log.c:168` | `Pregap length: %i frames` |
| `cyanrip_log.c:170` | `Pregap LSN:  unknown (sub-channel unreadable)` |
| `cyanrip_log.c:172` | `Pregap LSN:  unknown (sub-channel CRC mismatches)` |
| `cyanrip_log.c:174` | `Pregap LSN:  none` |
| `cyanrip_log.c:180` | `Pregap source: sub-channel (not signalled by TOC)` |
| `cyanrip_log.c:182` | `Pregap source: lead-in` |
| `cyanrip_log.c:184` | `Pregap source: TOC` |
| `cyanrip_log.c:187` | `Prepended:   %i frames of silence` |
| `cyanrip_log.c:188` | `Start LSN:   %i` |
| `cyanrip_log.c:190` | `(with offset: %i)` |
| `cyanrip_log.c:194` | `End LSN:     %i` |
| `cyanrip_log.c:201` | `Appended:    %i frames of silence` |
| `cyanrip_log.c:209` | `Preemphasis:` |
| `cyanrip_log.c:211` | `none detected` |
| `cyanrip_log.c:214` | `(deemphasis forced)` |
| `cyanrip_log.c:219` | `present (subcode)` |
| `cyanrip_log.c:221` | `present (TOC)` |
| `cyanrip_log.c:224` | `(deemphasis applied)` |
| `cyanrip_log.c:229` | `Properties:` |
| `cyanrip_log.c:232` | `Data bytes:  %i (%.2f Mib)` |
| `cyanrip_log.c:235` | `Frames:      %u` |
| `cyanrip_log.c:241` | `Duration:    %s` |
| `cyanrip_log.c:242` | `Samples:     %u` |
| `cyanrip_log.c:245` | `Peak level:  %.1f%%` |
| `cyanrip_log.c:249` | `True peak level: %.1f dBFS` |
| `cyanrip_log.c:252` | `Extraction speed:  %.1fx` |
| `cyanrip_log.c:254` | `Elapsed:            %.2f s` |
| `cyanrip_log.c:262` | `EAC CRC32:     %08X` |
| `cyanrip_log.c:264` | `(after %i rips)` |
| `cyanrip_log.c:271` | `Secure re-read:  converged after %i reads` |
| `cyanrip_log.c:274` | `Secure re-read:  did NOT converge after %i reads (repeat limit hit)` |
| `cyanrip_log.c:279` | `Secure re-read:  not attempted` |
| `cyanrip_log.c:283` | `Accurip:       %s` |
| `cyanrip_log.c:287` | `(max confidence: %i)` |
| `cyanrip_log.c:295` | `Accurip v1:  %08X` |
| `cyanrip_log.c:297` | `(accurately ripped, confidence %i)` |
| `cyanrip_log.c:299` | `(not found, either a new pressing, or bad rip)` |
| `cyanrip_log.c:303` | `Accurip v2:  %08X` |
| `cyanrip_log.c:314` | `Accurip 450: %08X` |
| `cyanrip_log.c:316` | `(match found, confidence %i, but a checksum of 0 is meaningless)` |
| `cyanrip_log.c:319` | `(matches Accurip DB, confidence %i, track is partially accurately ripped)` |
| `cyanrip_log.c:322` | `(not found)` |
| `cyanrip_log.c:329` | `Metadata:` |
| `cyanrip_log.c:339` | `%s:` |
| `cyanrip_log.c:351` | `CD-TEXT:` |
| `cyanrip_log.c:361` | `Paranoia status counts:` |
| `cyanrip_log.c:363` | `none` |
| `cyanrip_log.c:386` | `Embedded cover art:    %s: %s` |
| `cyanrip_log.c:389` | `Embedded cover art:    %s: %ix%i %s` |
| `cyanrip_log.c:393` | `File(s):` |
| `cyanrip_log.c:407` | `cyanrip %s (%s-g%s)` |
| `cyanrip_log.c:410` | `Invoked as:     %s` |
| `cyanrip_log.c:414` | `Drive used:     error retrieving drive info` |
| `cyanrip_log.c:416` | `Drive used:     %s %s (revision %s)` |
| `cyanrip_log.c:417` | `System device:  %s` |
| `cyanrip_log.c:419` | `Device model:   %s` |
| `cyanrip_log.c:420` | `Offset:         %c%i %s` |
| `cyanrip_log.c:422` | `%s%c%i %s` |
| `cyanrip_log.c:431` | `Speed:          %ix` |
| `cyanrip_log.c:433` | `Speed:          default (%s)` |
| `cyanrip_log.c:435` | `C2 errors:      %s` |
| `cyanrip_log.c:444` | `Encoder:        libavformat %i.%i.%i, libavcodec %i.%i.%i (%s)` |
| `cyanrip_log.c:449` | `Paranoia level: %s` |
| `cyanrip_log.c:453` | `Paranoia level: %i` |
| `cyanrip_log.c:454` | `Frame retries:  %i` |
| `cyanrip_log.c:456` | `HDCD decoding:  %s` |
| `cyanrip_log.c:458` | `Album Art:      %s` |
| `cyanrip_log.c:462` | `%s%s%s%s%s` |
| `cyanrip_log.c:470` | `Outputs:` |
| `cyanrip_log.c:476` | `Disc tracks:    %i` |
| `cyanrip_log.c:477` | `Tracks to rip:  %s` |
| `cyanrip_log.c:480` | `%i%s` |
| `cyanrip_log.c:494` | `AccurateRip:    %s` |
| `cyanrip_log.c:500` | `Total time:     %s` |
| `cyanrip_log.c:526` | `Tracks ripped accurately: %i/%i` |
| `cyanrip_log.c:528` | `Tracks ripped partially accurately: %i/%i` |
| `cyanrip_log.c:538` | `Ripping errors: %i` |
| `cyanrip_log.c:545` | `Rip completed:  no (interrupted by user, %i of %i tracks)` |
| `cyanrip_log.c:548` | `Rip completed:  yes (%i of %i tracks)` |
| `cyanrip_log.c:551` | `Ripping finished at %s` |
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
| `cyanrip_main.c:498` | `Frame read failed!` |
| `cyanrip_main.c:575` | `Loading data for track %i...` |
| `cyanrip_main.c:582` | `Stopping, offset finding incomplete!` |
| `cyanrip_main.c:590` | `Data loaded, searching for offsets...` |
| `cyanrip_main.c:599` | `Nothing found for track %i%s` |
| `cyanrip_main.c:604` | `Offset of %c%i found in track %i%s` |
| `cyanrip_main.c:609` | `Offset of %c%i confirmed (confidence: %i) in track %i%s` |
| `cyanrip_main.c:613` | `New offset of %c%i found at track %i, scrapping old offset of %c%i%s` |
| `cyanrip_main.c:627` | `No track had AccuRip entry, cannot find offset!` |
| `cyanrip_main.c:629` | `No track was long enough, unable to find drive offset!` |
| `cyanrip_main.c:631` | `Was not able to find drive offset with a radius of %i frames, trying again with a larger radius...` |
| `cyanrip_main.c:637` | `Drive offset of %c%i found (confidence: %i)!` |
| `cyanrip_main.c:667` | `Unable to read track %i subchannel info!` |
| `cyanrip_main.c:683` | `Track %i is data:` |
| `cyanrip_main.c:740` | `Error in decoding/sending frame: %s` |
| `cyanrip_main.c:752` | `Drive media changed, stopping!` |
| `cyanrip_main.c:783` | `Stopping, ripping incomplete!` |
| `cyanrip_main.c:901` | `Done; (%i out of %i matches for current checksum %08X)` |
| `cyanrip_main.c:907` | `Done; (no matches found, but hit repeat limit of %i)` |
| `cyanrip_main.c:923` | `Repeating ripping (%i out of %i matches for current checksum %08X)` |
| `cyanrip_main.c:938` | `Error in encoding: %s` |
| `cyanrip_main.c:954` | `Error sending flush signal to encoders: %s` |
| `cyanrip_main.c:961` | `Track %i ripped and encoded with errors.` |
| `cyanrip_main.c:963` | `Track %i ripped and encoded successfully!` |
| `cyanrip_main.c:1045` | `Gaps:` |
| `cyanrip_main.c:1050` | `%i frame gap between lead-in and track 1 pregap, merging into pregap` |
| `cyanrip_main.c:1057` | `%i frame unmarked gap between lead-in and track 1, marking as a pregap` |
| `cyanrip_main.c:1079` | `%i frame pregap in track %i,` |
| `cyanrip_main.c:1086` | `unmerged` |
| `cyanrip_main.c:1088` | `merging into track %i` |
| `cyanrip_main.c:1094` | `dropping` |
| `cyanrip_main.c:1100` | `merging` |
| `cyanrip_main.c:1107` | `splitting off into a new track, number %i` |
| `cyanrip_main.c:1148` | `%i frame discontinuity between tracks %i and %i,` |
| `cyanrip_main.c:1153` | `padding track %i` |
| `cyanrip_main.c:1156` | `ignoring` |
| `cyanrip_main.c:1164` | `%i frame gap between last track and lead-out, padding track` |
| `cyanrip_main.c:1229` | `Can't init signal handler!` |
| `cyanrip_main.c:1449` | `Invalid paranoia level %i must be between 0 and %i!` |
| `cyanrip_main.c:1462` | `Invalid max coverart size %i (must be 250, 500, 1200 or -1)` |
| `cyanrip_main.c:1474` | `Invalid sanitation method %s` |
| `cyanrip_main.c:1486` | `Invalid release index %i!` |
| `cyanrip_main.c:1495` | `Invalid discnumber %i` |
| `cyanrip_main.c:1502` | `Invalid totaldiscs %i` |
| `cyanrip_main.c:1506` | `discnumber %i is larger than totaldiscs %i` |
| `cyanrip_main.c:1519` | `Supported output codecs:` |
| `cyanrip_main.c:1527` | `Invalid format \"%s\"` |
| `cyanrip_main.c:1532` | `Duplicated format \"%s\"` |
| `cyanrip_main.c:1547` | `Duplicated rip idx %i` |
| `cyanrip_main.c:1561` | `Invalid track idx for pregap: %i` |
| `cyanrip_main.c:1567` | `Missing pregap action` |
| `cyanrip_main.c:1575` | `Invalid pregap action %s` |
| `cyanrip_main.c:1606` | `No cover art location specified for \"%s\"` |
| `cyanrip_main.c:1615` | `Invalid track idx for cover art: %i` |
| `cyanrip_main.c:1621` | `Cover art already specified for track idx %i!` |
| `cyanrip_main.c:1633` | `Cover art \"%s\" already specified!` |
| `cyanrip_main.c:1639` | `Too many cover arts specified!` |
| `cyanrip_main.c:1649` | `Directory name scheme must contain {format} with multiple output formats!` |
| `cyanrip_main.c:1654` | `-J (only generate a CUE sheet) cannot be used with -I (only print info)!` |
| `cyanrip_main.c:1670` | `Searching for drive offset, enabling AccuRip and disabling MusicBrainz and Cover art fetching...` |
| `cyanrip_main.c:1678` | `Offset is unset! To continue with an offset of 0, run with -s 0!` |
| `cyanrip_main.c:1758` | `MusicBrainz URL:%s` |
| `cyanrip_main.c:1802` | `Error reading album tags: %s` |
| `cyanrip_main.c:1832` | `Log(s) will be written to:` |
| `cyanrip_main.c:1840` | `CUE files will be written to:` |
| `cyanrip_main.c:1872` | `Invalid track number %i, list has %i tracks!` |
| `cyanrip_main.c:1888` | `Error reading track tags: %s` |
| `cyanrip_main.c:1942` | `Cover art destination(s):` |
| `cyanrip_main.c:1977` | `WARNING: tracks %i and %i resolve to the same file \"%s\", one will overwrite the other!` |
| `cyanrip_main.c:1988` | `Tracks:` |
| `cyanrip_main.c:1998` | `Track %i info:` |
| `cyanrip_main.c:2016` | `Error initializing decoder: %s` |
| `cyanrip_main.c:2025` | `Error initializing encoder: %s` |
| `cyanrip_main.c:2059` | `Error encoding: %s` |
| `cyanrip_main.c:2079` | `Invalid rip index %i, list has %i tracks!` |
| `cyanrip_main.c:2161` | `Error ripping: %s` |
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

**251 distinct stable lines.**

Field order within a block is fixed and is part of the contract. The golden
reference log in the handshake package is the authoritative example.

## P3 - Unstable lines: reworded without a handshake

Do not parse these. Most are stdout-only and never reach the logfile at all.

| File:line | Line | Reaches logfile? |
|---|---|---|
| `cyanrip_encode.c:105` | `%s folder: [%s] extension: %s%s` | **no, stdout only** |
| `cyanrip_encode.c:125` | `Encoder for %s not compiled in ffmpeg!` | **no, stdout only** |
| `cyanrip_main.c:459` | `Still reading track %i at LSN %li - %` | **no, stdout only** |
| `cyanrip_main.c:483` | `Track %i resumed after %` | **no, stdout only** |
| `cyanrip_main.c:801` | `\r` | **no, stdout only** |
| `cyanrip_main.c:867` | `%s` | **no, stdout only** |
| `cyanrip_main.c:948` | `Flushing encoders...` | **no, stdout only** |
| `cyanrip_main.c:990` | `Force quitting` | **no, stdout only** |
| `cyanrip_main.c:993` | `\rTrying to quit` | **no, stdout only** |
| `cyanrip_main.c:1387` | `Log \"%s\" checksum valid.` | **no, stdout only** |
| `cyanrip_main.c:1390` | `Log \"%s\" checksum mismatch, the file has been modified!` | **no, stdout only** |
| `cyanrip_main.c:1394` | `Log \"%s\" has data after the checksum, the file has been modified!` | **no, stdout only** |
| `cyanrip_main.c:1398` | `No FUN512 checksum found in \"%s\"!` | **no, stdout only** |
| `cyanrip_main.c:1402` | `Couldn't read \"%s\"!` | **no, stdout only** |

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

The search stops at the next `if`/`for`/`while`/`switch` or the next log
call, so a message is only credited with an exit that is its own. Without
that cut, `Opening drive...` reads as fatal because the *next* statement's
if-block returns `AVERROR`.

| File:line | Message | Evidence | Reaches logfile? |
|---|---|---|---|
| `accurip.c:97` | `Unable to get AccuRIP DB data: missing CDDB ID!` | wording + goto end | yes |
| `accurip.c:129` | `Unable to get AccuRIP DB data: missing entry!` | wording + goto end | yes |
| `accurip.c:137` | `Unable to get AccuRIP DB data: %s%s` | wording | yes |
| `accurip.c:140` | `Unable to get AccuRIP DB data: %s!` | wording + goto end | yes |
| `accurip.c:176` | `AccuRIP DB data error, got unexpected number of bytes!` | goto end | yes |
| `coverart.c:51` | `Unable to init lavf context: %s!` | both | yes |
| `coverart.c:57` | `Unable to alloc stream!` | both | yes |
| `coverart.c:70` | `Couldn't open %s for writing: %s!` | both | yes |
| `coverart.c:82` | `Couldn't write header: %s!` | both | yes |
| `coverart.c:92` | `Error writing picture packet: %s!` | both | yes |
| `coverart.c:97` | `Error writing trailer: %s!` | both | yes |
| `coverart.c:177` | `Unable to get cover art \"%s\": not found!` | wording + goto end | yes |
| `coverart.c:186` | `Unable to get cover art \"%s\": %s%s!` | wording | yes |
| `coverart.c:189` | `Unable to get cover art \"%s\": %s!` | wording + goto end | yes |
| `coverart.c:262` | `Unable to open \"%s\": %s!` | wording + goto end | yes |
| `coverart.c:269` | `Unable to get cover image info: %s!` | wording + goto end | yes |
| `coverart.c:299` | `Error demuxing cover image: %s!` | wording + goto end | yes |
| `cue_writer.c:39` | `Couldn't open path \"%s\" for writing: %s!Invalid folder name? Try -D <folder>.` | both | yes |
| `cyanrip_encode.c:361` | `Error creating filter source: %s!` | both | yes |
| `cyanrip_encode.c:372` | `Error creating filter sink: %s!` | both | yes |
| `cyanrip_encode.c:386` | `Error setting filter sample format: %s!` | both | yes |
| `cyanrip_encode.c:394` | `Error setting filter channel layout: %s!` | both | yes |
| `cyanrip_encode.c:403` | `Error setting filter sample rate: %s!` | both | yes |
| `cyanrip_encode.c:437` | `Error initializing filter sink: %s!` | both | yes |
| `cyanrip_encode.c:471` | `Error parsing filter graph: %s!` | both | yes |
| `cyanrip_encode.c:477` | `Error configuring filter graph: %s!` | both | yes |
| `cyanrip_encode.c:536` | `Error pushing frame to FIFO: %s!` | wording | yes |
| `cyanrip_encode.c:555` | `Error filtering frame: %s!` | both | yes |
| `cyanrip_encode.c:633` | `Error allocating frame!` | both | yes |
| `cyanrip_encode.c:645` | `Error allocating frame: %s!` | both | yes |
| `cyanrip_encode.c:776` | `Could not alloc swr context!` | wording | yes |
| `cyanrip_encode.c:794` | `Could not init swr context!` | wording | yes |
| `cyanrip_encode.c:969` | `Error while encoding: %s!` | both | yes |
| `cyanrip_encode.c:991` | `Error encoding: %s!` | both | yes |
| `cyanrip_encode.c:1022` | `Error pushing packet to FIFO: %s!` | both | yes |
| `cyanrip_encode.c:1029` | `Error writing packet: %s!` | both | yes |
| `cyanrip_encode.c:1059` | `Error writing to file: %s!` | both | yes |
| `cyanrip_encode.c:1182` | `Codec not found (not compiled in lavc?)!` | control flow | yes |
| `cyanrip_encode.c:1191` | `Unable to init output avctx!` | both | yes |
| `cyanrip_encode.c:1202` | `Could not open output codec context!` | both | yes |
| `cyanrip_encode.c:1209` | `Couldn't copy codec params!` | both | yes |
| `cyanrip_encode.c:1216` | `Couldn't open %s: %s! Invalid folder name? Try -D <folder>.` | both | yes |
| `cyanrip_main.c:184` | `No device specified and unable to get default device!` | both | yes |
| `cyanrip_main.c:192` | `Unable to open device: %s` | both | yes |
| `cyanrip_main.c:201` | `Unable to init cddap context!` | wording | yes |
| `cyanrip_main.c:203` | `cdio: \"%s\"` | control flow | yes |
| `cyanrip_main.c:217` | `Unable to open device!` | both | yes |
| `cyanrip_main.c:226` | `Device does not support changing speeds!` | control flow | yes |
| `cyanrip_main.c:243` | `Unable to init paranoia!` | both | yes |
| `cyanrip_main.c:272` | `Invalid number of tracks: %i!` | both | yes |
| `cyanrip_main.c:295` | `CDIO returned invalid track %i end LSN` | control flow | yes |
| `cyanrip_main.c:582` | `Stopping, offset finding incomplete!` | wording + goto end | yes |
| `cyanrip_main.c:667` | `Unable to read track %i subchannel info!` | wording | yes |
| `cyanrip_main.c:740` | `Error in decoding/sending frame: %s` | both | yes |
| `cyanrip_main.c:752` | `Drive media changed, stopping!` | both | yes |
| `cyanrip_main.c:783` | `Stopping, ripping incomplete!` | wording | yes |
| `cyanrip_main.c:938` | `Error in encoding: %s` | wording + goto end | yes |
| `cyanrip_main.c:954` | `Error sending flush signal to encoders: %s` | wording | yes |
| `cyanrip_main.c:990` | `Force quitting` | control flow | **no, stdout only** |
| `cyanrip_main.c:1402` | `Couldn't read \"%s\"!` | both | **no, stdout only** |
| `cyanrip_main.c:1449` | `Invalid paranoia level %i must be between 0 and %i!` | both | yes |
| `cyanrip_main.c:1462` | `Invalid max coverart size %i (must be 250, 500, 1200 or -1)` | both | yes |
| `cyanrip_main.c:1474` | `Invalid sanitation method %s` | both | yes |
| `cyanrip_main.c:1486` | `Invalid release index %i!` | both | yes |
| `cyanrip_main.c:1495` | `Invalid discnumber %i` | both | yes |
| `cyanrip_main.c:1502` | `Invalid totaldiscs %i` | both | yes |
| `cyanrip_main.c:1506` | `discnumber %i is larger than totaldiscs %i` | control flow | yes |
| `cyanrip_main.c:1527` | `Invalid format \"%s\"` | both | yes |
| `cyanrip_main.c:1532` | `Duplicated format \"%s\"` | control flow | yes |
| `cyanrip_main.c:1547` | `Duplicated rip idx %i` | control flow | yes |
| `cyanrip_main.c:1561` | `Invalid track idx for pregap: %i` | both | yes |
| `cyanrip_main.c:1567` | `Missing pregap action` | both | yes |
| `cyanrip_main.c:1575` | `Invalid pregap action %s` | both | yes |
| `cyanrip_main.c:1606` | `No cover art location specified for \"%s\"` | both | yes |
| `cyanrip_main.c:1615` | `Invalid track idx for cover art: %i` | both | yes |
| `cyanrip_main.c:1621` | `Cover art already specified for track idx %i!` | control flow | yes |
| `cyanrip_main.c:1633` | `Cover art \"%s\" already specified!` | control flow | yes |
| `cyanrip_main.c:1639` | `Too many cover arts specified!` | control flow | yes |
| `cyanrip_main.c:1649` | `Directory name scheme must contain {format} with multiple output formats!` | control flow | yes |
| `cyanrip_main.c:1654` | `-J (only generate a CUE sheet) cannot be used with -I (only print info)!` | both | yes |
| `cyanrip_main.c:1678` | `Offset is unset! To continue with an offset of 0, run with -s 0!` | goto end | yes |
| `cyanrip_main.c:1802` | `Error reading album tags: %s` | both | yes |
| `cyanrip_main.c:1872` | `Invalid track number %i, list has %i tracks!` | both | yes |
| `cyanrip_main.c:1888` | `Error reading track tags: %s` | both | yes |
| `cyanrip_main.c:1910` | `%s` | goto end | yes |
| `cyanrip_main.c:2016` | `Error initializing decoder: %s` | both | yes |
| `cyanrip_main.c:2025` | `Error initializing encoder: %s` | both | yes |
| `cyanrip_main.c:2059` | `Error encoding: %s` | wording + goto end | yes |
| `cyanrip_main.c:2079` | `Invalid rip index %i, list has %i tracks!` | both | yes |
| `cyanrip_main.c:2161` | `Error ripping: %s` | wording + goto end | yes |
| `discid.c:31` | `Unable to init SHA for DiscID: %s!` | wording | yes |
| `musicbrainz.c:116` | `Invalid disc number %i, release only has %i CDs` | both | yes |
| `musicbrainz.c:121` | `Got empty medium list.` | control flow | yes |
| `musicbrainz.c:193` | `Could not connect to MusicBrainz.` | both | yes |
| `musicbrainz.c:201` | `Missing DiscID!` | wording | yes |
| `musicbrainz.c:224` | `Error fetching/requesting/auth, this shouldn't happen.` | wording + goto end | yes |
| `musicbrainz.c:299` | `Invalid release index %i specified, only have %i releases!` | wording | yes |
| `musicbrainz.c:366` | `Unable to find release info for this CD, and metadata hasn't been manually added!` | wording | yes |
| `musicbrainz.c:370` | `Unable to find metadata for this CD, but metadata has been manually specified, continuing.` | wording | yes |
| `naming.c:123` | `Error parsing string: %s!` | wording | yes |
| `naming.c:215` | `Invalid scheme syntax, unterminated \"{\"!` | both | yes |
| `naming.c:229` | `Invalid scheme syntax, no \"#\"!` | both | yes |
| `naming.c:243` | `Invalid scheme syntax, no terminating \"#\"!` | both | yes |
| `naming.c:259` | `Invalid condition syntax!` | both | yes |

**104 distinct strings.** By evidence: 60 both, 13 control flow, 15 wording, 3 goto end, 13 wording + goto end.

The `control flow` and `both` rows total 73 strings proven reachable on a
failure path without reference to their wording. That subset is the one to
build a hard failure classifier on.

