0.9.4-rc1+platterpus.5-beta.1 (2026-08-04) -- PRE-RELEASE
=========================================================
**A beta, not a release, and the distinction is the point.** Round 7 is open, so
this build claims no joint verification: every logfile it writes says
`NOT a released build`, and `tools/release-gate.py --release-gate` still refuses
a stable release against this record. It exists so the rig session can run the
hardware evidence a round close requires -- which cannot be gathered without
installing the build under review.

**No git tag.** The git proxy in this environment refuses tag pushes with
`HTTP 403`, re-probed for this release, and no release-creation API is reachable
either. **The commit SHA is the identifier.**

Fixed
 - **A diagnosed abort exited 0.** The exit code tracked `total_error_count`,
   which counts *read* errors, so a refusal to start or a rip that failed
   outright printed its reason and returned success. Still within `{0,1}`.
   **Unverified by any test**: the affected paths are hardware-gated, so this is
   an item for the rig session rather than something a fixture retires.
 - **`-x` could hang with no heartbeat.** The cache probe ran before the stall
   watchdog started, so the one read most likely to wedge on real hardware --
   raw MMC reads on a path that has never executed anywhere -- was the one read
   with no liveness reporting. The watchdog now starts first and the probe
   brackets its own reads.
 - **The golden reference was regenerated from a dirty tree** and committed with
   a `-dirty` banner, naming a build nobody can reproduce. Caught by A9's own
   marker. Regenerated clean, and the reference scenario now refuses one.

Added
 - **Sample-peak cross-check** (H6), printed only when ebur128's figure and a
   direct scan of the same frames disagree.
 - **`--prerelease`** on the release gate: a stable release stays refused while
   a round is open; a beta is permitted after printing every open round.
   Adopted from Platterpus, whose artifact is an installable release rather than
   a tree.
 - **`HANDSHAKE-TEST-PIN`**, breaking the deadlock where a round could not close
   without evidence that could not be gathered without installing the build the
   round was reviewing.

0.9.4-rc1+platterpus.4 (2026-08-04)
===================================
**Not `0.9.5-rc1`.** That was asked for and is not what shipped, for the reason
`0.9.4-rc3` was withdrawn a release earlier: it mints a number in upstream's
namespace, which upstream can mint too. It would also assert a base that does not
exist — upstream is at `0.9.4-rc1` and this tree is that plus fork patches, so a
leading `0.9.5` would be a provenance claim nothing supports. The fork release
number is the only number that moves, and it moved.

Fixed
 - **`catalog` → `catalognumber`** for the MusicBrainz catalogue tag, the
   Hydrogenaudio/Picard standard spelling. Found in `q3cpma/cyanrip` `0896ff3`,
   proposed in r3 rather than shipped, and shipped now because Platterpus ruled
   they are unaffected: they run with `-N` and supply tags explicitly, so cyanrip
   never derives that tag on their rips. **Breaking for any consumer that lets
   cyanrip do the MusicBrainz lookup and reads the old key.**

Added
 - **Sample-peak cross-check** (H6). The peak is measured a second way — max
   |sample| over the same frames the ebur128 filter sees — and a line is printed
   **only when the two disagree**, naming which value came from which method:

       Sample peak disagreement: ebur128 X dBFS, direct scan Y dBFS (Z dB apart)

   Silent on agreement, at Platterpus's request and for their reason: two
   always-present numbers for one fact invite a consumer to pick one, and
   whichever it picks will occasionally be the wrong one silently.
   **The firing path is unreachable from any disc image** — two correct
   measurements of identical input agree — so the decision is a pure function
   with its own unit test, and the wiring was proved by perturbation rather than
   assumed.
 - **`-dirty` in the build tag when the tree has uncommitted changes** (A9).
   Two golden references have carried a banner naming a commit three behind
   their stated pin; both were provable from content, but a stale banner on a
   reference built from a tree that still has the defect is the one failure
   that looks like success. Verified against a genuinely clean and a genuinely
   dirty tree, not against the tree that happened to be present.
 - **Paranoia counter scope and denominator, in the generated contract** (A8,
   Q10). Per-track blocks cover the final `-Z` pass; the disc-level block is
   cumulative across every pass; they are equal only at `-Z 0`. Under `-l` the
   disc-level block counts only what that invocation read, never the whole TOC.
 - **The handshake wire header** — `HANDSHAKE-FROM`, `-APP-VERSION`,
   `-RIPPER-VERSION`, `-PIN` — adopted from Platterpus's independent proposal,
   which named the *producing* pair on every file rather than only the agreeing
   pair on a closing one. Protocol bumped to **v2**; a v1 gate reading a v2 file
   refuses, which is why the number moved.

Unchanged
 - **No logfile line changed its text, indentation, field order or units.** The
   metadata *key* `catalog` became `catalognumber`, which is a value change in
   the metadata block rather than a format change.

0.9.4-rc1+platterpus.3 (2026-08-03)
===================================
**One version string, and only one number to track.** Releases r1 and r2 both
shipped carrying upstream's bare `0.9.4-rc1`, which made two fork builds
indistinguishable by version and left two counters to reconcile -- "fork release
r2" against a string that said `rc1`. From here the fork release is *in* the
version: `0.9.4-rc1+platterpus.3` is upstream's 0.9.4-rc1, fork release 3.

Advancing our own rc number instead (`0.9.4-rc3`) was tried and reverted before
release. It mints identifiers in upstream's namespace: nothing stops upstream
tagging its own `0.9.4-rc3`, at which point two different trees answer to one
string. `+platterpus.N` cannot collide, because upstream will never mint one.

There is no r1 or r2 equivalent of this string; those builds carry bare
`0.9.4-rc1` and are told apart only by their git tag and commit.

For a consumer parsing only the leading number, `PROJECT_FORK_ID` remains the
answer to "is this the fork?" -- match on `platterpus-fork` or on the
`+platterpus.` suffix, never on `0.9.4-rc1` alone, which upstream also answers
to.

Fixed
 - **`Duration:` was one frame (13.3 ms) too long for interior tracks whenever
   `-s` was nonzero**, which is every real rip, since a drive read offset is
   almost never zero. It was sourced from `t->frames`, which `setup_track_lsn()`
   widens by a frame at whichever end the offset shifts into; the sample count
   is taken before that adjustment, so the same block printed
   `Samples: 176400` (exactly 00:04.00) directly above `Duration: 00:04.01`.
   The log contradicted itself, and the shorter of the two fields was the wrong
   one. Now derived from `nb_samples`.

   **The sign is not uniform, and this matters more than the size of the
   error.** The offset shifts *both* ends of a track's range; on a track clamped
   at the disc boundary the shift is removed at one end only, leaving the other
   end's shift uncompensated in the opposite direction. Measured on the fixtures:

   | | track 1 | last track |
   |---|---|---|
   | `-s +667` | **+1** | **−1** |
   | `-s -667` | **−1** | **+1** |

   So a downstream repair written as *"add one frame back"* is wrong on the
   boundary track, in the opposite direction, on every disc. **The repair is
   "recompute from `Samples:`", never "adjust by a frame."** Platterpus found the
   inverted sign on their own rig log (track 14 of 14, `-s 667`); it was
   reproduced here on `basic.cue` and `pregap.cue` before being accepted, which
   is also where the symmetric start-boundary case came from.

   **`-s 0` never showed it**, which is why no fixture caught it and why the
   golden reference is unchanged: it is generated at `-s 0`. Found in
   `bovinemagnet/cyanrip` commit `3eb6e22` during a survey of other forks, and
   reproduced here before being taken.

   Deliberately *not* sourced from `end_lsn_sig - start_lsn_sig`, which is what
   the `Frames:` line prints: those are captured from the raw TOC before pregap
   merging and lead-out padding move the LSNs, so for a merged pregap they
   describe a different span than was ripped.
 - **The read-liveness heartbeat added in r2 never fired on a real stall.** It
   was emitted from libcdio-paranoia's status callback, so it could only report
   a read that was still making progress -- while a drive grinding on a bad
   sector blocks inside a single SCSI command, where paranoia is not running and
   never calls back. Confirmed against a real rip on 2026-08-03: two
   three-minute stalls, a build provably containing the r2 heartbeat, 41180
   lines of captured stdout, and not one heartbeat line among them. The
   heartbeat now runs on its own thread, which keeps ticking while the rip
   thread is blocked in the kernel.

   Anyone who took r2's silence as "no stalls occurred" was reading an absence
   of evidence as evidence of absence. r2's heartbeat could not distinguish
   them; r3's can.

Changed
 - The two liveness lines are reworded. Both are **stdout-only** progress output
   and neither reaches the logfile, but a consumer capturing stdout will see it:

       old  Still reading track N at LSN L - Ts so far, C paranoia callbacks
            since the frame began
       new  Still reading track N - the read for LSN L has not returned after Ts

       old  Track N resumed after Ts
       new  Track N - the read for LSN L returned after Ts

   The callback count is gone: nothing counts callbacks for this purpose now.
   The LSN names the frame the read was *asked* to return, which is all that is
   known -- paranoia over-reads and re-reads around it, so the old wording
   implied a drive position that was never measured.

Added
 - `-x` / `--cache-probe` measures the drive's readback cache at rip time, on
   the disc actually in the drive, by timing re-reads against a known uncached
   cost. Off by default; costs seconds of drive time. Refuses to report a
   number for a disc image, which has no cache to measure.
   **Not verified on hardware** -- no drive exists in the environment it was
   written in, and no image can produce the timing signal the method needs.
 - `tests/rip_images.py` scenario **duration**, which rips two fixtures at five
   read offsets and asserts each track's `Duration:` against the `Samples:`
   field beside it -- an independently sourced number, not the one it was
   computed from. It also asserts the offset reached the rip, so the four
   nonzero cases cannot silently degenerate into four copies of `-s 0`.
 - `tests/stall.c` (`meson test` name **Stall watchdog**), which asserts the
   heartbeat fires while a read is outstanding *and nothing is calling back* --
   the property r2 lacked. Reverting to a caller-driven poll fails four of its
   checks.

Unchanged
 - **No logfile line changed in this release**, and no line changed at all at
   `-s 0`. `Duration:` now reports a different *value* for interior tracks at a
   nonzero offset -- a corrected measurement, not a format change. The golden reference differs
   from r2's only in the version string, the timestamps, the wall-clock timing
   fields, and the checksum over all of them.

platterpus-fork r2 (2026-08-03)
===============================
Fork release 2. Shipped carrying upstream's version string `0.9.4-rc1`; see
the r3 entry above for why that changed.

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
   stalls, so a slow read is distinguishable from a wedged one.
   **Superseded in r3: this did not work.** It could only report reads that were
   still progressing, which are not the ones that matter. See the r3 entry.
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
First tagged fork release, on upstream `0.9.4-rc1` (`958e1ad`), and shipped
carrying that version string.

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
