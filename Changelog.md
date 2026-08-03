platterpus-fork r2 (2026-08-03)
===============================
Fork release 2. Version number stays upstream's `0.9.4-rc1` deliberately -- this
fork never renumbers upstream's releases, so the fork release counter and the
`platterpus-fork` build tag are what identify it. See `CLAUDE.md`.

Fixed
 - **Disc-image rips returned silence at any paranoia level above 0.** One
   correct sector followed by 99.7% zeroed samples, reported as
   `Ripping errors: 0`. Upstream sets paranoia's cache model to 1 sector for
   image drivers, and that size doubles as the read chunk size, leaving the
   verification logic no overlap. Raised to 16, clear of both the corruption
   boundary (<=4) and the leadout over-read that costs errors (>=512).
   Affects upstream 0.9.4-rc1 and every earlier build of this fork. Real
   drives were never affected; `-P 0` was always byte-perfect.

Added
 - CD-TEXT is read from the disc, disc level and per track, kept verbatim in
   the log and used to fill metadata only where nothing else claimed it
   (user `-a`/`-t` > MusicBrainz > CD-TEXT > defaults)
 - Per-track paranoia status counters, summing exactly to the disc totals
 - `Encoder:` names the libavformat/libavcodec that wrote the audio
 - `Cache model:` reports the size paranoia models, and says the drive was not
   probed -- deliberately not phrased as a cache defeat, which is not measured
 - `Sample peak level:` and `True peak level:`, each saying which peak
 - `Integrated loudness (R128):` and `Loudness range (R128):`, fork-owned so a
   consumer need not scrape libavfilter's wording
 - Read-liveness reporting from inside paranoia's callback while a frame read
   stalls, so a slow read is distinguishable from a wedged one
 - `-k` / `--stall-secs` sets that threshold (default 10, 0 disables)
 - `-V` accepted again as an alias for `--version`, after upstream's move from
   getopt to genopt dropped it and broke callers probing with it
 - Q sub-channel recovery for drives that return raw binary instead of BCD

Changed
 - `Cache defeat:` renamed to `Cache model:`, and `Peak level:` to
   `Sample peak level:`. Both labels claimed more than their values
   established. Consumers keying on the old names must update.
 - Log and cue files are line-buffered, so a cancelled rip leaves a partial
   record instead of an empty file
 - The log's first line and `Invoked as:` identify the fork and its arguments

platterpus-fork r1 (2026-08-02)
===============================
First tagged fork release, on upstream `0.9.4-rc1` (`958e1ad`).

 - Fork identifies itself as `platterpus-fork` in the version banner and on
   line 1 of every logfile; the version number stays upstream's
 - Pregap provenance reported per track, distinguishing `none` from
   `unknown (reason)`
 - `-Z` convergence verdict reported per track
 - Per-track extraction speed and elapsed time
 - Q sub-channel pregap detection for physical discs, carried from upstream
   PR #115 with three fixes
 - `tools/gen-provider-contract.py` generates the machine-readable interface
   contract consumed by Platterpus

Everything below this line is upstream cyanreg/cyanrip's changelog, unmodified.

0.9.4-rc1
=========
 - New option parser: long options, typed values, saner errors
 - CUE sheet-only mode, without ripping anything (-J)
 - Rip log checksum verification (-Y)
 - Label and catalog number tagging from MusicBrainz
 - Embedded cover art is now typed as a front cover, so file managers thumbnail it
 - Automatic deemphasis of preemphasized discs now actually happens
 - CUE sheets reference their files relative to the sheet
 - Naming schemes: stricter parsing, whitespace trimming, filename collision warnings
 - Data tracks no longer leave stray files
 - Fixed a crash on overlong filenames
 - FFmpeg 8.0+ compatibility

0.9.3
=====
 - FFmpeg 7.0 compatibility
 - Added an option to specify the image size for cover lookup
 - When only printing info, do not require an offset to be specified with -I
 - Fix default pregap action setting for tracks after the first
 - Better error handling

0.9.2
=====
 - ReplayGain 2.0 scanning and tagging
 - Preemphasis detection via both TOC and subchannel
 - Automatic deemphasis
 - CUE file writing
 - Repeat ripping mode for affirmation or badly damaged discs
 - Tagging improvements (setting the media_type tag)
 - Logfile reorganization and checksumming
 - Windows compatibility improvements
 - Migration to new FFmpeg 6.0 APIs

0.9.0
=====
 - Improve MusicBrainz query result handling and detect stub releases
 - For unknown discs, add an ID to the album name
 - Better error reporting when opening logfile
 - Fix crash when MCN is missing
 - Silence warning when writing cover art to a file
 - Fix compilation with FFmpeg 6.0

0.8.1
=====
 - __No need to rerip anything.__
 - Fix Musicbrainz album name setting.

0.8.0
=====
 - __No need to rerip anything.__
 - ETA printout
 - Minor bugfixes
 - Big endian fixes
 - Default bitrate for lossy files set to 256kbps
 - Fix minor compilation warnings
 - Fix compilation warnings with FFmpeg 5.0

0.7
===
 - __No need to rerip anything.__
 - Automated CD drive offset finding
 - Verification of partially damaged tracks
 - Tagging usability improvements
 - Even faster ripping
 - Arbitrary directory/file structure
 - Automatic cover art image downloading
 - ...and more

0.6.0
=====
 - __No change in actual audio data ripped, rerip if you want to verify with accurip.__
 - Fill disc count and disc number from musicbrainz.
 - Able to choose the MusicBrainz release to use for albums with multiple releases.
 - Tag improvements (discname is set when available for multi-disc releases).
 - Fix accurip v1 and v2 checksums (were calculated incorrectly). EAC CRC has always been correct.
 - Fix some minor and one large memory leak.

0.5.2
=====
 - __No need to rerip anything.__
 - Fix encoding while ripping from a real drive (broken by 0.5.0).

0.5.1
=====
 - __No need to rerip anything.__
 - Reduce FFmpeg library version requirements

0.5.0
=====
 - __No need to rerip anything.__
 - Rewritten audio muxing
       * Now properly sets the time base in all cases
 - Rewritten encoding code
 - Rewritten FIFO code
       * No longer deadlocks
 - Rewritten build system

Previous versions
=================
No history.
