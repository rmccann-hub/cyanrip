# Known issues: the closed items moved on 2026-11-16, as they stood then

Moved here from `docs/KNOWN-ISSUES.md` at `7589d7b6`, word for word below this
header, under that file's rule that an item leaves only when it is fixed and a
test pins it, or is shown never to have been ours, to a dated file under
`docs/history/`; and the owner's word of 2026-11-16, to consolidate the
documentation before round 41. The table gives each item's fix, the release
that shipped it and the test that pins it; several items' own text still says
"not yet released" or "the build after", as it stood. Where an item kept an open part,
that part stays in `docs/KNOWN-ISSUES.md` as a short entry, and every open item
is a row of `docs/OPEN-ITEMS.md`. It is history and is not maintained; an item
that turns out not to be closed goes back.

| Item | Closed by | Pinned by |
|---|---|---|
| `C2 errors: unsupported by drive` is false | `372706fe`, released in `.32` | `tests/drivecaps.c` |
| Four drive answers (the four; six unchecked and the MCN read stay open) | `819c735b`, `.28` | `tests/drivecaps.c`, `tests/imagecap.c` |
| A value the log echoes could start a line (the `-d`/INQUIRY newline stays open) | `46cec2a1`, `.28` | `tests/logescape.c`, `log_values_cannot_forge_a_line` |
| `Embedded cover art:` names a cover the muxer dropped | `443cbeb9`, `.29` | `sc_cover_art_formats`, `tests/logrender.c` |
| A positive offset on an Enhanced CD (its drive run is OPEN-ITEMS HW-15) | `6fa6fe57`, `.29` | `sc_enhanced_cd` |
| The build tag in eight characters | `31afbf12`, `.30` | `tests/build_tag.py` |
| `Ripping errors:` leaves out a `-Z` track | `48037671`, `.29`; third form `220ee383`, `.32` | `sc_repeat_limit`, `tests/logrender.c` |
| The footer's tallies under `-l` and `-f`, and a cancel | `27d1c048` and `1695b5f2`, `.29` | `tests/logrender.c`, `sc_interrupt` |
| A closed console left no footer: ours done; the cause, Platterpus's, found in their round 30 lap 4 S8 | `1184a047`, `acfd48b0` | `sc_interrupt` |
| The four shared documents' table (rows 13 to 15 stay open) | rounds 25 and 30, v8 `5cadca3b` | `tools/seam-sync-check.py` |
| A track's per-track lines computed from the request (its drive run is OPEN-ITEMS HW-3) | `d33902d4`, `.27` | `sc_encode_failure_reaches_the_log` |
| The reference disc cannot test a correct AccurateRip skip: a note about the disc, never a defect | — | — |
| `read successfully!` over a track AccurateRip rejects | `ab130cca`, `.27` | `sc_encode_failure_reaches_the_log` |
| The table of what has not run on a drive | replaced by `docs/OPEN-ITEMS.md`, *Needs a drive* | — |

---

## Moved from *Open, ours, and solvable* on 2026-11-16

**Round 30 carried these, on the operator's word of 2026-10-05**, and closed
on 2026-10-06; entries below fixed since say so in their headings. The round
was to stay open until everything here that could be fixed was fixed, both applications
ship betas, and an acceptance run of both passes. So *"not now"* and *"round
31"* stopped being reasons. Where an entry below still says why it waited,
that was the reason before 2026-10-05, kept as the record.

### `C2 errors: unsupported by drive` is false on the BDR-209D

**Found 2026-11-11 by the C2 probe** (`docs/rig-2026-11-11b-c2probe/`). The line
prints libcdio's reading of the capabilities page, 2Ah, whose C2 pointers bit this
drive leaves clear under all four page controls, so every log on this drive says
`unsupported by drive`. Asked with READ CD byte 9 = `12h`, the drive returns C2
pointers, and it flags three bytes at track 5's 02:24:59 in four reads of four.

**What it costs**: a reader of the log takes the drive to be unable to report C2
errors, which it can. The label asserts what one declaration implied.

**Fixed in `.32`**, released 2026-11-13 at `edb73dd`, not in `.31`: the line says `not declared by drive
(capabilities page, not measured)` or `declared supported by drive (capabilities
page), not used`, our round 39 lap 3 S14's wordings, which Platterpus's 0.7.123
reads (their lap 4 S3) and our lap 5 S4 announced. A disc image, which has no
capabilities page and said `unsupported by drive`, says `unknown (image)`, as the
lines beside it do. `tests/drivecaps.c` holds each wording and fails with the old
ones restored. `.31`'s logs still say what this entry describes.

### Four drive answers the log states that are libcdio's defaults or its failure (fixed for `.28`)

**Found by the claude-code-skills session's review of 2026-10-26, item 3.3**,
which asked for drive answers printed without a sentinel check. A read-only
audit of `src/` listed candidates; these four were then read here, in our code
and in libcdio at `68ea374`:

- **`Speed: default (unchangeable)` is libcdio's constant, not the drive's
  answer.** The line reads `CDIO_DRIVE_CAP_MISC_SELECT_SPEED`
  (`src/cyanrip_log.c:1031-1032`), and libcdio never asks the drive. Its MMC
  page parser (`lib/driver/mmc/mmc_util.c:112`) never sets the bit, and it
  answers on Linux (`lib/driver/gnu_linux.c:1709-1713`, where the one setter is
  compiled out: `#undef USE_LINUX_CAP`, `:433`, `:490`), on Windows, NetBSD,
  Solaris and AIX, and on FreeBSD in its CAM and MMC access modes. On macOS
  the bit is set for every drive whose feature flags libcdio reads
  (`lib/driver/osx.c:838`), so the line says `changeable` there whatever the
  drive can do. All 21 `Speed:` lines in the drive logs copied to
  `tests/fixtures/evidence/` read `unchangeable`. This entry first called the
  constant Linux's only (`619dd07`); every driver's `.get_drive_cap` was then
  read for our round 36 lap 12.
- **`Drive used:` on an image names libcdio's stand-in**, `libcdio CDRWIN
  (revision 2.1.)` in the golden reference's line 6, two lines above
  `Accurate stream: unknown (image)`.
- **A failed capabilities query reads as the drive's answer.** When MODE SENSE
  fails libcdio sets every capability word to `CDIO_DRIVE_CAP_ERROR`
  (`lib/driver/mmc/mmc.c:866-870`), and nothing in `src/` tests for it, so the
  log says `C2 errors: unsupported by drive`, and the disc ISRC and MCN reads
  that the capability bits gate are skipped as if the drive lacked them.
- **An error from the media-change query stops the rip as a changed disc.**
  `get_media_changed()` counts any return but 0 and `DRIVER_OP_UNSUPPORTED`
  (`src/cyanrip_main.c:118-125`), so a failed ioctl, `DRIVER_OP_ERROR`, ends
  the rip with `Drive media changed, stopping!`.

**Reported by the audit and not yet checked here**: the CD-TEXT language on an
image is always `English` (libcdio sets it so); a TOC whose starts do not
increase is printed raw while paranoia repairs its own copy; a failed
last-session query decides the CD-Extra cut; an image's TOC pregap is not
checked against the track's bounds; CD-TEXT's ISRC reaches the tags without the
ISO 3901 check; and the offset search numbers tracks by position.

**What it costs**: each prints a default or a failure as a measurement, which
is the first rule's failure.

**Fixed in `.28`** (`819c735`), in the wordings our round
36 lap 12 S11 proposed and Platterpus's lap 13 S5 accepted:
- `Speed:          default (drive not asked whether it can change speed)`.
- On an image, `Drive used:     none (disc image, read by libcdio's CDRWIN
  driver, revision 2.1.)`. The revision clause is ours, put to Platterpus in
  our round 37 lap 3, since it is the only place a log names libcdio's version.
- `C2 errors:      unknown (capabilities query failed)`, and the disc ISRC
  reason `the capabilities query failed`.
- `Drive media change query failed (libcdio error N), stopping!` for a query
  that failed, exit 74 as before.

With their lap 13 S5's change, a `-S` that cannot be set no longer stops the
rip. It reads at the drive's own speed, and `Speed:` says `default (setting
8x failed)` on a drive or `default (disc image, 8x not applied)` on an image.

The MCN read a failed query skips is still skipped without a word. Every drive
arm is unit-tested in `tests/drivecaps.c`, and the image arms on images with
`tests/imagecap.c`. **On a drive, 2026-11-03** (`docs/rig-2026-11-03-3f288fb/`,
`.28` at `3f288fb`, released with the fix at `819c735`): `Speed:` said the drive
was not asked, since no `-S` was sent; `C2 errors:` said unsupported by drive;
`Accurate stream:` gave the drive's declaration; `Recordable:` said `no`. A `-S`
sent, and one the drive refuses, have not run.

### A value the log echoes could start a line of its own (fixed for `.28`)

**Found by the claude-code-skills session's review of 2026-10-26, item 3.1**,
which searched `src/` for an escape of control characters as fields go into
the log and found none. Measured here before the fix: a `.toc` whose track 1
CD-TEXT title is `Probe Track One` + byte 0x85 + `Accurip: accurately ripped
(forged)` gave the log a line reading `Accurip: accurately ripped (forged)`
when split with Python's `str.splitlines()`, as Platterpus splits it
(`platterpus@d745464d:src/platterpus/parsers/cyanrip_log.py:1471`). libcdio
reads a `.toc`'s CD-TEXT as ISO-8859-1, so the byte arrives as U+0085. A
vertical tab in the performer did the same, and so did a `-t` title with a
newline, which also split `Invoked as:`. Upstream prints the same values the
same way (`src/cyanrip_log.c:207` at `7dbe56a`).

**What it costs**: a disc, a cue sheet, MusicBrainz or a caller's `-t` could
write a line Platterpus or a tracker's logchecker reads as the rip's own,
`Accurip:` or `Track N read with no error reported.` among them.

**Fixed for `.28`**: every `%s` the log writes is escaped (`src/log_escape.c`;
the rule is in the contract's P2). `tests/logescape.c` and
`log_values_cannot_forge_a_line` hold it, and both fail with the escape
removed. One newline is still kept: paranoia's own messages are written a line
at a time, and they name the `-d` path and the drive's INQUIRY strings, so a
newline in either still starts a line there. The escape's form, proposed to
Platterpus in our round 36 lap 12 S9 and accepted as given in their lap 13 S3,
shipped in `.28` (`46cec2a`).

### `Embedded cover art:` names a cover the muxer dropped (fixed for `.29`)

**Found 2026-10-27 while testing review C item 1.1.** A rip with an AV1 cover
(`tests/fixtures/art.avif`) and `-o flac` logs, for each track,
`Embedded cover art:` and `Front: 8x8 Alliance for Open Media AV1`, and saves
`Front.avif`, but `ffprobe` finds no picture in either FLAC. FFmpeg 6.1.1's
FLAC muxer drops an AV1 picture: it says `No mimetype is known for stream 1,
cannot write an attached picture.` and writes the file without it, measured
with `ffmpeg` alone, outside cyanrip. The log line is printed from what was asked for, not from
what the muxer wrote. Upstream prints it the same way
(`src/cyanrip_log.c:233` at `7dbe56a`).

**What it costs**: a reader of the log believes the files carry a cover they
do not. A PNG cover is embedded; the suite's `art` checks it.

**Not fixed**: the line is in the contract's P2, so its fix is proposed in a
lap first. Two shapes are open: refuse a cover the output's muxer cannot embed
before the rip, or print what was written, read back from the muxer.

**Worse for a GIF, measured 2026-11-04** with FFmpeg 6.1.1: its FLAC and MP4
muxers refuse one, so a `.28` rip with a GIF cover and `-o flac` lists the
cover in the track block and then fails with `Error writing to file: Not yet
implemented in FFmpeg, patches welcome!` and exit 1 (our round 38 lap 3 S12).

**Fixed for `.29`, not yet released**, as our round 38 lap 1 S9 proposed,
Platterpus's lap 2 S6 accepted, and our lap 3 S15 completes. Which output
holds which picture is `crip_fmt_holds_picture()`, a table of what FFmpeg
6.1.1's muxers keep. A user's own cover that an embedding output cannot hold
is refused before the rip, with exit 64 and a line naming the output and the
format. A cover is given only to an output that holds it, and the block lists
it only for the files that do: `none (the output cannot hold a GIF picture;
saved as <file>)` when none does, with no file for a track's own cover, which
is not saved, and `not in the <ext> file: ...` for each that does not.
`sc_cover_art_formats` holds the table against FFmpeg itself, pair by pair,
and the refusal; `tests/logrender.c` holds the lines. Each fails with its fix
reverted. It leaves this file once `.29` ships.

### A positive offset on an Enhanced CD read the session gap into the last audio track (fixed for the build after `.28`)

**Found 2026-11-03, checking upstream issue 168 against this fork** (the
owner's message of that day, §5): upstream's rip of an Enhanced CD with a
positive drive offset hangs at the end of the last audio track at `-P 0 -Z 2`.
The fork shares the read: the session gap is cut from the last audio track
(`src/cyanrip_main.c`, the `CRIP_XA_INTERVAL` branch), but the frame an offset
needs past its new end was bounded by the disc's end, so it was read from the
drive. On an image it did not hang, because `crip_read_audio_salvaging()` holds
at `-P 0` and the retry limit is rounded elsewhere; instead the gap's bytes went
into the track's last samples, and where that sector failed, a track whose own
sectors all read cleanly said `read with errors.` and the rip exited 1.

**Fixed**: the read is bounded by `audio_end_lsn`, the last audio track's end on
an Enhanced CD and the disc's end otherwise, in all three places the read
checked the disc's end. The frame is now appended silence, as at the end of a
one-session disc, and under `-O` it is read once (`Beyond disc:`, whose label
then covers session 1's lead-out, not only the disc's). `sc_enhanced_cd`'s
offset check rips the well-formed image at +6 samples and compares track 2
with the image's bytes; with the fix reverted it fails two checks.

**Needs a drive**: what a drive does with a read of session 1's lead-out, and
whether a pressed CD-Extra's TOC matches the image's, are unknown here. Listed
in `STATUS.md`'s `hardware-unverified`.

### The build tag names `.29` in eight characters from a full clone (fixed for the build after `.29`)

**Found 2026-11-04 by Platterpus** (platterpus@7fdc33a1), when their installer
refused the owner's install of `.29` with their 0.7.120. The build tag is `git
rev-parse --short HEAD`, whose length git takes from the repository's object
count: seven characters until about 16,000 objects, eight after. This
repository passed that line with `.29` (17,009 packed objects in a full clone
on 2026-11-04), so a full clone builds `platterpus-fork-g8d2ca726`, while the
release manifest, the ledger, our laps and Platterpus's pin say `8d2ca72`. Our
own `.29` Changelog records the eight-character tag, and our round 38 lap 5
still gave the banner as `g8d2ca72`.

**What it costs**: the same commit builds two banners depending on the clone,
and a consumer that checks the banner against the pin refuses a correct build.
Platterpus's installer now pins seven in its own clone.

**Fixed for the build after `.29`, not yet released**: the build asks `git
rev-parse --short=7`, which git lengthens only for a prefix that is ambiguous,
and an archive carries the full hash (`$Format:%H$`), cut to seven, since `%h`
is sized by whichever git made the archive. `tests/build_tag.py` runs the
build's own tag script in a repository abbreviating at twelve and in one with
no git, reads what `git archive` writes, and holds this build's banner to
`--short=7`. It fails with either half of the fix reverted. `.29` as released
still builds eight characters from a full clone. It leaves this file once the
fix ships.

### `Ripping errors:` leaves out a `-Z` track whose re-reads never agreed (fixed for `.29`)

**Found by the review of 2026-11-03 (A5)**, in that night's secure re-read
(`-Z 2 -r 5`): track 3 read five times to four checksums, the block printed
`Secure re-read:  did NOT converge after 5 reads (repeat limit hit)` and
`Track 3 read with errors.`, and the footer `Ripping errors: 0`.
`crip_ripping_errors()` (`src/cyanrip_main.h`) counts the drive's and the
encoders' errors and paranoia's skips, and the repeat-limit and time-limit arms
(`src/cyanrip_main.c:2154-2157`) add to neither.

**What it costs**: the footer says a rip had no errors when its own body says
one track's read was never confirmed.

**Not fixed, and not a local fix**: Platterpus's read-speed ladder takes the
count less the skips as what the drive failed
(`platterpus@168761ef:src/platterpus/parsers/cyanrip_log.py:1089-1105`), so
adding these to the count would step a disc down for a disagreement no drive
reported. Proposed in a lap first (round 38): a third part of the suffix, for
example `(including 1 track whose re-reads never agreed)`, which their
parser must accept before it ships.

**Fixed for `.29`, not yet released**, by a line of its own and not the
suffix: under `-Z`, directly above `Ripping errors:`, `Secure re-reads: N
track(s) did not converge (track(s) T)` or `Secure re-reads: every track
converged`, as our round 38 lap 1 S5 proposed and Platterpus's lap 2 S2
accepted; `Ripping errors:` keeps its count. A rip that stopped with no track
named prints no line, a case lap 1 did not cover, which our lap 3 gives them.
`tests/logrender.c` holds every arm and `sc_repeat_limit` the line on a rip,
by position; each fails with the fix reverted. It leaves this file once
`.29` ships.

### The footer's tallies count the whole disc under `-l` and `-f`, and a cancel as an error (fixed for `.29`)

**Found by the review of 2026-11-03 (B5)**: `-f` prints
`Tracks ripped accurately: 0/14`, `-l 1` prints `1/14`, and a rip cancelled by
SIGTERM counts the interrupted track in `Ripping errors: 1`. The tallies'
denominator is the disc's audio tracks since `.27` (the item on data tracks,
now in `docs/history/KNOWN-ISSUES-2026-11-04.md`), not the tracks asked for.

**What it costs**: a partial rip reads as a mostly failed one, and a cancel as
a read error.

**Fixed for `.29`, not yet released**, as our round 38 lap 1 S6 proposed and
Platterpus's lap 2 S3 accepted as given: the tallies divide by the audio
tracks the run asked for and `-f` prints neither (`27d1c048`,
`tests/logrender.c`); a track a cancel stopped with nothing failed adds
nothing to `Ripping errors:` (`sc_interrupt`). Each test fails on its fix
reverted. It leaves this file once `.29` ships.


## Moved from *Open, ours, and NOT solvable here — no drive in this environment* on 2026-11-16

Every one of these needs hardware. Listed so a green suite is never mistaken for
coverage.

| gap | status |
|---|---|
| `--cache-probe` (`-x` until 2026-10-12) correctness on a real drive | **measured seventeen times on builds up to `.19`, wrong sixteen times** — `at least 2048 sectors` against `cd-paranoia -A`'s 137–140 — and right once by the defect's own arithmetic, 2026-10-05's `128 to 255` (see the cache section). **`.20`'s fix (`394ab17`) has run nine times on a drive, 2026-10-06 to 2026-10-22, and agreed each time**: `128 to 255` beside `cd-paranoia -A`'s 137, 140 or 144. This cell said *"measured twice"* while the table above held nine rows |
| C2 error reporting | the rig's drive reports C2 unsupported; never exercised anywhere |
| `-f` offset autodetection | **partially retired 2026-08-12** — exited 0 and rediscovered `+667` on the rig. The *value* is now confirmed; behaviour on a drive with a different offset is not |
| damaged media | **read on hardware 2026-10-04**, `174a134` on the BDR-209D (`docs/rig-2026-10-04-174a134/`): a disc the drive reads differently each time from track 11 on. Measured: the drive reported no error (no `cdio error` or `Frame read failed` in any log), C2 is unsupported so it said nothing, reads slowed to **54 s**, one track took **8,161 s**, paranoia **skipped 2,586** times on it, and five `-Z` reads of each of five tracks gave five checksums. Whether the disc is damaged is an inference; the drive's behaviour is what was measured. No drive reported a read as failed in that run. From `.20` the `read with errors.` arm also takes a track paranoia skipped on, or one whose `-Z` reads never agreed, which this run's tracks 12 to 18 would have. The `-Z` arm printed it on a drive on 2026-10-06 (`docs/rig-2026-10-06-5704062/`, tracks 3 and 5), and **the skip arm on 2026-10-21**, `.26` on the same disc (`docs/rig-2026-10-21b-ca0f097/`): 2,106 skips, on exactly the four tracks that print it, with their positions in the record. Tracks 11, 12, 14 and 16 read no skip, print `read successfully!` and fail AccurateRip, so paranoia reported nothing on four wrong reads. Every position in that run is a skip. **A drive reporting failed reads, then unopenable, ran in the rig session of 2026-11-03**, `.28` at `3f288fb` on the reference disc (`docs/rig-2026-11-03b-3f288fb/`, whose README puts it down to the drive failing and says nothing in the bundle rules out the disc): in the secure re-read's track 10 the BDR-209D answered `Unknown, unrecoverable error reading data` 6,720 times, the track's `error_positions` holds 995 `read_error` and 5 `skip` with 5,748 more counted as dropped, and the rip stopped at `Drive media change query failed (libcdio error -1), stopping!`, exit 74, after which every call failed to open the drive. **Still not seen:** a track's `File(s):` naming one not written whole, since that rip stopped inside track 10, which the footer's `Partial files:` names as read not completed |
| CD-TEXT from a physical disc | `mmc_read_cdtext` is a different code path from the image parser, and no disc with CD-TEXT has been read |
| ~~the diagnosed-abort exit code~~ | **RETIRED 2026-09-22.** `cyanrip -N -l 1` with no `-s` exited **1** with `Offset is unset!` at column 0, `Rip completed:  no (aborted, 0 of 14 tracks)` and a complete footer — `docs/rig-2026-09-22-2cce60d/session/script-report.json` step 212. The reason given here (*"every rig rip so far had `Ripping errors: 0`"*) had **already been false since 2026-09-10**: seven filed rig logs carry `Ripping errors: 1`, counted off `docs/rig-*/rips/*.log` rather than remembered |
| ~~a non-zero `Read stalls:` count~~ | **RETIRED 2026-08-26**, and this row outlived the retirement by a month. **Five** filed rig logs carry a populated line, up to `5 reads exceeded 10s; longest 11s (track 1, LSN 8322)`, counted off `docs/rig-*/rips/*.log`. The rule it carried still holds and is why it is kept visible: **a silent watchdog is not a working watchdog**, and zero heartbeats on healthy media — which is what all eight rips of 2026-09-22 report — is the expected result and evidence of nothing |


## Moved from *Open, joint — belongs to the seam, not to one side* on 2026-11-16

### Closing Platterpus's script console mid-rip left a log with no footer — cause not determined

**Observed once, 2026-09-30, on `.18` through Platterpus 0.6.64**
(`docs/rig-2026-09-30-174a134/rips/full-acceptance-angle-bracket.log`). The
operator closed the script console 28.9 s into section F's rip. The log is 54
lines and ends at `Tracks:`: no track block, no completion footer, no `Log
FUN512:`, so `-Y` exits 3. Platterpus's record gives the wrapper's exit code as
1 at 01:32:32Z, the second the console closed, and **no `-j` record was in the
bundle**, which Platterpus collects from the rips root by name
(`platterpus@0981c69:src/platterpus/adapters/cyanrip_backend.py:745-747`). So
when the operator made the tarball, cyanrip had not exited through `atexit`.

**Which signals write the footer, measured 2026-09-30** on a fixture ripping
mid-read, `.19`'s code (Platterpus's round 30 lap 2 S22 asked):

| signal | exit | footer, `Log FUN512:` | `-Y` | `-j` record |
|---|---|---|---|---|
| SIGTERM, SIGINT | 1 | written, names the signal | 0 | written |
| SIGHUP | killed | **none** | 3 | none — **handled from `.20`**, below |
| SIGQUIT, SIGKILL | killed | none | 3 | none |
| SIGPIPE | **not stopped** | none while it runs on | 3 | none |

**SIGPIPE is ignored, and not by us.** libneon, linked through libmusicbrainz5,
calls `signal(SIGPIPE, SIG_IGN)` from `ne_sock_init()` as a library constructor,
before `main()`, under `-N` too (`strace -k`). So a consumer that stops reading
our stdout does not stop the rip: it runs on, holding the drive, and writes its
footer when it ends. That is this environment's libraries; the rig's container
links its own.

**So the closed-console log is one of two things**: a default-disposition death
(SIGHUP, SIGQUIT or SIGKILL), or a cyanrip still running inside the container
when the tarball was made. The rig can say which: if the log in
`~/platterpus-rig/platterpustestsession20260930t013138z/rips/` is now longer
than 54 lines and a `cyanrip-diagnostics-20260930T013204Z.json` sits beside
the album folder, it ran on; if neither, it was killed. What their console's
close sends is theirs to trace (their round 30 lap 2 S21, S23).

**2026-10-04 settles one such log as the second kind** (`docs/rig-2026-10-04-174a134/`).
Section N's `secure-reread.log` has no footer. Its last line is the app log's
line at 01:01:00.985Z. The script was stopped from the console 0.8 s later, and
the bundle was written in the same second. No line in between signals or reaps
the ripper, which was mid-re-read. The operator closed both programs before
sending the bundle, but the copy had already been made. So a bundle can hold a
log that is still being written, and the bundle did not say so. **Our side of
the check exists now**: `tools/ingest-bundle.py` names every cyanrip log that
did not reach a signed footer, and says what that can and cannot mean
(`acfd48b`). **Their side** is to make the bundle say the ripper was still
running, or wait for it.

**The same run's cancel: what the rescue is, corrected 2026-10-05.** This
said the cancel *"sent a second TERM 4.9 s after the first"*, Platterpus's
*post-cancel rescue*, `fuser -k TERM /dev/sr0`, and that a second signal ends
cyanrip with `_exit(1)` and no footer. The second half is true of our handler
(`cyanrip@174a134:src/cyanrip_main.c:1219-1220`). The first is not true on this rig: the
2026-10-05 run's cancel shows the cancel's own TERM stopping at the host
wrapper, the rescue's TERM finding cyanrip still holding the drive, and a
signed footer about 0.3 s later, which a second signal would have prevented
(`docs/rig-2026-10-05-174a134/README.md`). So the rescue's signal is the first
cyanrip receives. On 2026-10-04 it found cyanrip inside a read that had not
returned after 20 s, and that disc's reads took up to 54 s; the cancelled pass's
log was in a temporary directory and is not in the bundle, so whether it was
signed is still not known.

**SIGHUP is handled from `.20`**, like SIGTERM: the footer names it, `-Y`
verifies, and the `--diagnostics` record is written. A SIGHUP that arrives already ignored
stays ignored, so `nohup` still keeps a rip running (measured). `sc_interrupt`
pins it, revert-proved. SIGQUIT keeps its default, quit and dump core, which is
the debugging path it exists for.

### The four shared documents: every known defect, in one table

**Rows 1–7 were fixed in round 25 (2026-09-23)**, by `PROTOCOL.md` v6,
`OWNERSHIP.md` v3 and `seam-rules.md` v6, all byte-identical in both trees. Drafting found an eighth, in `OWNERSHIP.md`'s opening
paragraph: it says every consumer holds its copy at the same path, and
Platterpus's protocol is at `docs/handshake-protocol.md`. `OWNERSHIP-v3.md`
fixes that too. Rows 8–12, `seam-commands.md`, wait for round 26, because the
fix needs `tools/probe-argv-surface.py` to measure what it asserts.
**Row 13 was found on 2026-09-28** by a control in the round-28 close
rehearsal, and **row 14** the same day, filing Platterpus's round 28 lap 9.
Both are for round 29, and both are gaps in the spec, not false statements.
**Rows 15 and 16 are for v8**, from Platterpus's round 30 lap 6 S23 and S24,
read against v7 as proposed at `09f39bc` and still true of it at `2abeb5d`.
**Carried to round 31 by the operator's decision of 2026-10-05**: v7 governs
from round 31, so a v8 drafted in round 30 could govern nothing sooner, and
drafting it would add laps to a round whose close waits on a run. **v8 landed
at `5cadca3b`, as round 31 agreed, and its E3 rewrote R8 point 2** to *"Each
side chooses its own channel"*: row 16's *"accepts"* and row 15's *"the
consumer follows a build on beta"* went with the old sentence. Row 15's other
items were not re-read against v8 or v9 for this note.

**Consolidated 2026-09-22 by the pre-round-24 audit**, read against the four
files as they stand — byte-identical in both trees, `tools/seam-sync-check.py
--fetch` exit 0 at `platterpus@52b4428`. None of these breaks a gate. Each is a
statement a reader of the spec is entitled to believe and should not. **None can
be fixed from one side** (`OWNERSHIP.md` §4), so this is the bundle a joint
version bump would carry, and round 24 proposes it rather than editing it.

| # | file | what it says | what is true | detail |
|---|---|---|---|---|
| 1 | `PROTOCOL.md` | nothing on K1, K2 or K3 | all three agreed in round 22, and both sides practise them | `docs/history/KNOWN-ISSUES-2026-10-21.md`, *Three agreed protocol changes* |
| 2 | `PROTOCOL.md` §8, *"Rows added in v3/v4"* | *"These are not yet in force."* | the heading's own condition, *"required once both gates implement 4"*, is met: ours implements 5 (`tools/release-gate.py`, `PROTOCOL_VERSION = 5`), theirs 4 (`platterpus@52b44282:scripts/handshake.py:1093`) | here |
| 3 | `PROTOCOL.md` §8, *"Rows added in v5"* | *"Not yet in force."* | **False since `platterpus@c2f43d28`**, when their gate reached 5. This cell predicted that on the day it was written, and it happened the same evening. It is row 2 again: a spec frozen by version cannot be edited when a present-tense sentence goes stale. The conditional headings are already correct; the fix is to delete both body sentences | here |
| 4a | `PROTOCOL.md` §5b step 1 and row C37 | the candidate lap must be declared in the closing file's own `HANDSHAKE-INBOUND-HELD` | then step 3 and C40, *"the whole of v5's saving"*, cannot fire on a real record, because the saving lap is written after the closing file | the v5 entry below |
| 4 | `PROTOCOL.md` | `HANDSHAKE-FROM-COMMIT` defined once | the two projects read it two ways | round 23 lap 3 §D. v5 §13 says so itself, so this is a known gap rather than a false statement |
| 5 | `OWNERSHIP.md` §3 | *"we cannot run their program, read their source, or reproduce their environment"* | **"read their source" has been false since 2026-09-13.** Both repositories are public, and this environment reads theirs anonymously on every `seam-sync-check --fetch`. The other two clauses were not checked, so this makes no claim about them | `docs/history/CLAUDE-2026-10-21.md`, *"This rule used to carry the clause…"* |
| 6 | `OWNERSHIP.md` §5 | *"we cannot read each other's source"* | same as row 5 | same |
| 7 | `seam-rules.md` S-13 | round 7: *"laps to close: **37 and open**"*, *"releases produced: **0**"* | round 7 closed `GO` at **lap 39** (`round-07-lap-39.md`), and produced one release, `+platterpus.5`, at `release-ledger.tsv` row 11. `CLAUDE.md`'s copy of this table was corrected on 2026-09-16; the shared copy was not | here |
| 8–12 | `seam-commands.md` | five statements | **all fixed in round 30**, two at `83bcd70` and three by the text landed after `0645ddb` | *"`docs/seam-commands.md` carried FIVE known-wrong statements"*, above |
| 13 | `PROTOCOL.md` §5b, rows C39–C40 | step 2 cross-checks the closing file's transcription of the PEER's verdict against the lap its source names | **nothing asks a gate to check the peer's transcription of ITS OWN verdict**, so the two gates can split on one record. Rehearsed 2026-09-28 on copies of our record (control X-c3): our lap 6 `GO`, their lap 7 `GO`, released, at protocol 6, but transcribing our lap 6 as `OPEN`. **Our gate closes the round** on their lap 7 by step 3. **Theirs refuses it**: their closing file is their lap 7, its source names our lap 6, and the values disagree (`platterpus@785925a:scripts/handshake.py:2438-2447`, *"the transcription disagrees with its source"*). Their gate makes them correct their own file, so the split closes itself once they do; until then ours says CLOSED and theirs does not | found by a control in the round-28 close rehearsal, not by a real record. **For round 29, not round 28**: the candidate row is that a gate refuses when the newest peer lap's source names one of the gate's own laps and its `HANDSHAKE-PEER-VERDICT` disagrees with that lap's `HANDSHAKE-VERDICT` |
| 14 | `PROTOCOL.md` §5, `HANDSHAKE-OUR-VERSION` / `HANDSHAKE-PEER-VERSION` | *"which two programs agreed"* | **the two closing files of round 28 name different Platterpus builds as the party.** Our lap 8 names the build that was tested, `platterpus 0.6.61` at `59f4c00`. Their lap 9 names its own current release, `platterpus 0.6.62` at `9e96fa0` (their `v0.6.62` tag), while its `HANDSHAKE-APP-VERSION` and `HANDSHAKE-TESTED` say 0.6.61. Both are defensible readings. Neither gate cross-checks the two files, so one closed round quotes two different agreements | found 2026-09-28 filing their round 28 lap 9. For round 29: say whether the field names the build under test or the build declaring the verdict |
| 15 | `PROTOCOL.md` v7 and `seam-rules.md` v7 | nine wording items | each is a sentence v7 leaves imprecise, none a false rule: `HANDSHAKE-NEXT-LAP` with two grammars (§3, C46); R9 keeping the sentence §15 calls misleading; R8 point 2's unscoped *"the consumer follows a build on beta"*; §6d asking for the pair newest at the run's end where D3 checks only its start; a mid-round hotfix reading as a pin move against R4; §15 saying one v6 item was withdrawn; §6c's *"opens with"* and undefined `<owner>`; and five smaller | Platterpus's round 30 lap 6 S23, which gives each with its v7 line numbers at `09f39bc`. **R8 point 2's item is gone**: v8's E3 rewrote that point (`5cadca3b`); the others were not re-read against v8 or v9 |
| 16 | `PROTOCOL.md` v7 R8 point 2 | the provider's release goes to stable *"once the round its run opens accepts it"* | both sides read *"accepts"* as *"closes `GO`"*, which is how a run graded `partial`, as `.19`'s was, still reaches stable | Platterpus's lap 6 S24 and our lap 7. The reading is agreed; the word is for v8. **Gone in v8**: its E3 rewrote R8 point 2 as *"Each side chooses its own channel"* (`5cadca3b`), and *"accepts"* is not in it |

**Fix row 5 first.** It is a false premise under a rule that may still be
true. §3 argues that the systematic-gate duty is Platterpus's partly *because*
we cannot read their source. The duty may well stay with them, since they hold
the drive and run both sides' code. But part of the argument for it is now
false, and a rule defended by a false reason can be dismissed by refuting that
reason.

**Scope, stated so a blank is not read as a pass.** Checked: every dated,
versioned, counted or present-tense claim a grep for those shapes finds in all
four files, plus `seam-rules.md` read through, S-1 to S-18 and §4–§5. Its one
count about our binary, *"They document 41 flags"*, still matches `--help` on
`+platterpus.14`. **Not checked:** counts about Platterpus's argv builder
(*"we send 18"*, *"Seventeen flags reach the argv builder"*). Those are theirs
to state, under S-9.

### A track's per-track lines are computed from the REQUEST, not the outcome

**HALF FIXED, AND THAT HALF SHIPPED IN `+platterpus.14` AT `3e01bb3` ON
2026-09-22.** Written at `89a57d6` in round 22, released once Platterpus 0.6.53
accepted both wordings. **The half that remains is the harder one** — `File(s):`
still lists what was *requested* rather than what was written, because it prints
before the encoders are joined — and it is why this entry stays under *Open*: a
heading that said *fixed* over an entry describing a live defect is the label
rule this repository applies to log lines, turned on its own notes.

**Two sentences in the blockquote below were true when written and are now
false**, and they are kept because the record of why a release waited is worth
having: `+platterpus.14` *has* been cut, legitimately, after the release it
waited for; and *"naming it there is what enforces the order"* was refuted before
the round closed — a close cannot name a release that does not exist when it
happens, which `CLAUDE.md` records. **Nothing machine-checkable enforced the
order; the plan and the operator did.**

> **THE FIX IS NOT RELEASABLE ON ITS OWN, and the reason came back from
> Platterpus in round 22 after our lap 1 had already gone.** The renamed line is
> their **block delimiter**, not a field they read:
> `platterpus@417d61b:src/platterpus/parsers/cyanrip_log.py:212-215`,
> `_TRACK_START`, commented *"A track block opens with its outcome line"*,
> matching **both** arms we renamed. Line 2452 is the only `_TrackAcc(`
> construction site and sits inside that match, so no match means **no track is
> parsed**; `rip_completed_tracks` is set separately at 1458 from the disc-level
> footer. **The same parse therefore reports 14 of 14 tracks and
> `No errors occurred` over a record carrying zero tracks.** Read at the SHA
> they cited rather than taken on their word.
>
> **They did not veto it.** The ask is their round-20 ordering: their parser
> accepts both wordings additively, ships in a release, **then** `+platterpus.14`
> ships. `Encoder errors:` they accepted as a clean P2 — all three arms trip
> their completeness sweep, which is the sweep working, and tracks still parse.
>
> **So this entry is now two facts, not one.** The log is right and the release
> is blocked on a consumer-side prerequisite no release of this fork has had
> before. `+platterpus.14` must not be cut until that release exists; round 22
> cannot close without `HANDSHAKE-PEER-VERSION`, so naming it there is what
> enforces the order with machinery that already exists.
>
> **AND THE ZERO-TRACKS OUTCOME IS SILENT AT RUNTIME — do not write "wrong but
> loud" in lap 3.** Read at `417d61b`, their completeness enumeration is two
> mechanisms and neither reaches a user: their *test* walks their **committed**
> logs and fails on a top-level line matching neither the tables nor
> `_IGNORED_DISC_LINES` (`cyanrip_log.py:1082-1085`), and the parser itself logs
> an unclaimed top-level line **at debug** (`:1086-1087`). So the sweep that
> caught `Encoder errors:` fires on fixtures they hold, and a user running a tip
> build gets zero tracks with a debug line and nothing else. That makes their
> ordering ask stronger rather than weaker. **Lap 3 §H material at most, flagged
> read-from-source, and explicitly not a condition** — they said no new
> conditions and we are not adding one.

**What round 21 fixed was the COUNT, and this is what it made visible.** With
the completion footer moved below the encoder-status loop, `Ripping errors:`
reported the encoder failures — but the per-track block above it did not:

```
Track 2 ripped and encoded successfully!      <- the encode failed
  File(s):
    .../2.flac                                <- 32768 bytes; intact is 253742
Error writing packet: File too large!
Error writing trailer: File too large!
Ripping errors: 2                             <- fixed in round 21
Rip completed:  yes (2 of 3 tracks)
```

Two separate causes, and they need different answers:

- **`Track N ripped and encoded successfully!`** — **FIXED, round 22.** It was
  printed when the READ finished; the encoders run asynchronously and their
  status did not exist yet, so the line was not merely mis-worded — at the
  moment it printed, the fact it asserted was genuinely unknown. **No rewording
  of a line printed at time T can report a fact that comes into being at T+1**,
  so the claim is split rather than softened: the per-track line then read
  `Track N read successfully!` (`read with no error reported.` from round
  36) and the encode outcome lands in a new
  `Encoder errors:` line in the footer, below `Ripping errors:`, where the
  collection loop has joined every encoder thread. Three arms — `none; N tracks
  encoded`, `M tracks failed (…); N tracks encoded`, `not applicable; no track
  was encoded` — because `none` over an unstated population is the absence-of-
  evidence defect wearing a number.
- **`File(s):`** — **STILL OPEN.** It is built from `ctx->settings.outputs` and
  the naming scheme (`cyanrip_log.c:847`) and consults nothing about what was
  written, so it names a path whatever happened to it. Platterpus's phrase for
  their own version of this — *a completeness field computed from the REQUEST,
  read as the OUTCOME* — fits it exactly. **It prints from
  `cyanrip_log_track_end()`, which runs at the same pre-join moment**, so
  marking a failed entry there is the identical fixpoint one level down. It
  became *possible* only once the footer named the tracks, which is why
  `ROUND-22-PLAN.md` §1 rejected it as a standalone option and listed it as a
  second pass. **Nobody has got to it**; that is not the same as declining it.
  **Built for `.27`** (`d33902d`): our round 36 lap 4 S12 proposed, and
  Platterpus's lap 3 S5 accepted, that the footer list each file a failed
  encoder left, `    not written whole: <path>`, directly below an `Encoder
  errors:` line that names a failed track. `File(s):` stays the request. The
  line shipped in `.27`, released at `5aeefc4`.

**Why it waited for round 22, and what changed.** Round 21 shipped two agreed
changes; a third, unannounced, would have been the finish line moving inside the
round — R1. Platterpus's round-21 lap 2 then listed it under *"explicitly not
asking"*, with the reason *"a real design question, not a reword, and it should
not be decided under a round's clock"*. **That is an argument for deciding it in
a round that OPENS on it, which is what round 22 lap 1 does** — the design was
written out in full in `ROUND-22-PLAN.md` §1 before the round opened, options
and rejections included, so nothing about it is being settled under time
pressure.

Pinned by assertion now rather than by a docstring:
`sc_encode_failure_reaches_the_log()` requires the old string to be **absent**,
not merely joined by a new one, and compares the tracks `Encoder errors:` names
against the truncated files on disk rather than against the log's other half.
Revert-proved four times, one fix at a time.

### The reference disc cannot discriminate a correct AccurateRip skip (a note about the disc, not a defect)

`--first`/`--last` apply AccurateRip's 5-sector lead/tail skip. On this disc
those regions are digital silence, so the skip is a no-op and any golden log
derived from the disc is silent on that logic — **in both implementations.**

The Python copy of the algorithm is pinned by one synthetic vector, non-zero
including the edges, under three first/last settings in `audio-checksums.py
self-test`; the C is compared with it by the `audio_checksums` image
scenario. **Platterpus has none to cover**: it
computes no AccurateRip checksum and reads ours from the log (their round 28
lap 6 S7). Checked at `platterpus@808f8fb1` on 2026-10-12: nothing under their
`src/` computes one, and `ctdb/crc.py` is the CTDB CRC with CTDB's own trims.
So round 8 `J13` is answered, and this stays a note about the disc, not an open
question about them.

### `read successfully!` prints over a track AccurateRip then rejects (fixed in `.27`, `ab130cca`)

**Found by the EAC parity plan of record of 2026-10-26, row 8**, in round 36's
run on the damaged disc (`docs/rig-2026-10-21b-ca0f097/`). Tracks 11, 12, 14
and 16 printed `Track N read successfully!` and failed AccurateRip (our round
36 lap 8 S9).

The line reports the read alone: no error from the drive, no paranoia skip,
and no `-Z` repeat limit (`src/cyanrip_main.c`, the arm that prints `read with
errors.`). It is printed before AccurateRip is looked up, and a read with no
error reported can still be wrong. `successfully` claims more than the read
knows, which is the overstatement the plan's row 8 asks both sides to remove.

**Fixed for `.27`**: renamed `Track N read with no error reported.`, beside
the unchanged `read with errors.`, as our round 36 lap 8 S26 proposed and
Platterpus's lap 9 S17 accepted. Their 0.7.113 reads both wordings, and logs
written before `.27` keep the old one.

