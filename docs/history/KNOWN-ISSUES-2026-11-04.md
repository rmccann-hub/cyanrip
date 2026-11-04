# Known issues: the closed items moved on 2026-11-04, as they stood then

Moved here from `docs/KNOWN-ISSUES.md` at `b74a5fff`, word for word below this
header, under that file's rule that an item leaves only when it is fixed and a
test pins it, to a dated file under `docs/history/`. Every item here is fixed
in a release, `.26`, `.27` or `.28`, and names the test that pins it; each says
which, with its evidence. It is history and is not maintained; an item that
turns out not to be closed goes back to `docs/KNOWN-ISSUES.md`.

---

## Moved from *Open, ours, and solvable* on 2026-11-04, each fixed and pinned by a test

### The disc's ISRCs read as none on the rig's drive, while EAC's cue of the same disc has them (fixed in `.26`)

**Found by the claude-code-skills session's known fixes of 2026-10-21, item 8**,
and untracked here until then. On the BDR-209D, `.25` printed `Disc ISRC:
none (libcdio returned none)` for every track of the reference disc
(`docs/rig-2026-10-20-5f1d036/`, the secure re-read's log, lines 82 and 165 on),
while EAC's cue of the same disc on the same drive gives an ISRC for every
track, track 1's `GBAAM7800003`
(`platterpus@1b532e69:output_reference/EAC_flac/eac_baseline_police_classics.cue:13`).
Whether EAC read those codes from the disc's sub-channel is not stated in its
log; it is the only source a cue's `ISRC` lines have in EAC.

**What it costs**: the files carry MusicBrainz's ISRC, which names a recording
rather than this pressing, and `--prefer-disc-isrc` has nothing to prefer.

**What is known, read from libcdio, not run**: `cdio_get_track_isrc()` on Linux
is `mmc_get_track_isrc()`, a READ SUB-CHANNEL with format 03h and the track in
byte 6, the same from 2.1.1 to its master (`lib/driver/mmc/mmc.c`,
`mmc_get_mcn_isrc_private()`). It returns NULL for three different answers:
the command failing, a reply shorter than 21 bytes, and the drive's TCVal bit
clear, which is the drive saying it found none. Our log cannot tell them apart,
and it does not name the libcdio version the rig ran. The ISRC is read before
any sector of the track, while the pre-emphasis read beside it reads a sector
first because a drive answers for wherever it last read (upstream's `59b3f2d`).

**For `.26`, without a drive**: when libcdio returns none on a drive, cyanrip
reads 200 of the track's own Q frames with READ CD, the path the pregap search
has used on the BDR-209D since 2026-08-04, and takes the ISRC from the first
CRC-valid mode-3 frame; if none carries one, it asks libcdio again with the
head inside the track. Each outcome is a different measurement, and the reason
says which: a code; `none (libcdio returned none, also after reading 200 Q
frames of the track, none an ISRC frame)`, which would mean the drive builds
its formatted Q without mode-3 frames; or one of the counts for frames failing
their CRC or carrying no well-formed code. `tests/subq.c` holds the decode,
against an ISRC frame built from cdrdao's encoder, and the scan, on the
simulated drive. **The drive settles it**: the next rig rip of the reference
disc on `.26`. If formatted Q carries no mode-3 frames, the next step is the
raw P-W sub-channel, which a drive returns as recorded.

**The drive settled it, 2026-10-21** (`docs/rig-2026-10-21-ca0f097/`).
- **The reference disc.** Every `.26` track block read a code from the track's
  own Q frames, and the 14 codes match EAC's cue of the disc, 14 of 14.
- **Disc 4 of the four-disc set** (`docs/rig-2026-10-22b-ca0f097/`). It read
  codes for 13 of 16 tracks, the same code in every log.
- **Discs 1 and 3.** Their tracks read `none (libcdio returned none, also after
  reading 200 Q frames of the track, none an ISRC frame)`.

So the BDR-209D's formatted Q does carry mode-3 frames, and READ SUB-CHANNEL
is the path that returned none. With `--prefer-disc-isrc`, the files and the
cue now carry the disc's code. Platterpus's audit warns that it differs from
the one they sent, which is the option working
(`docs/rig-2026-10-21-ca0f097/`, L726).

### `Recordable:` never answers on the rig's drive: libcdio's profile search stops one descriptor short (fixed in `.27`)

**Found 2026-10-25, reading the four runs of `.26`** (`docs/rig-2026-10-21-ca0f097/`
and the three after it). All 38 `.26` logs, on four discs, read `Recordable:
unknown (profile 0xffff is not a CD profile)`.

`.26` takes the profile from libcdio's `mmc_get_disctype()`
(`cyanrip@ca0f097:src/cyanrip_main.c:326`). That function:
- sets `*p_disctype` to `CDIO_MMC_FEATURE_PROF_NON_CONFORM`, `0xffff`, before
  it searches GET CONFIGURATION's profile list;
- loops `q < p + profiles_list_length` with `q` starting at `p + 4`, so the
  list's last descriptor is never read;
- returns `DRIVER_OP_SUCCESS` either way.

The bound is the one the function was added with in 2010 (libcdio `2d3b7d28`),
and the function is the same at 2.1.1, at 2.3.0 (the rig's, by its install
step's `libcdio-devel-2.3.0-1.fc44`), at 2.4.0 and at master `68ea374`
(`lib/driver/mmc/mmc_hl_cmds.c`). So `0xffff` is libcdio's default, not the
drive's answer, and our line states it as the drive's profile. Which
descriptor the BDR-209D marks current, the log cannot show.

**What it costs**: the line meant to say whether the disc is a CD-R or CD-RW
says nothing on the one drive we have. And what it does say names a profile
the drive never reported.

**Fixed for `.27`, not yet shown on a drive**: cyanrip sends the command
libcdio's function sends and takes the current profile from the reply's feature
header, bytes 6 and 7, which MMC defines for it
(`crip_current_profile_parse()`, `src/drive_caps.c`). `tests/drivecaps.c`
builds a reply listing CD-ROM last and current, as a BD drive lists its
profiles: libcdio's search over it gives `0xffff`, and the header gives
`0x0008`. Only a drive run shows what the BDR-209D's header says. libcdio's
loop is an upstream defect of libcdio's, reported by our operator if they
choose.

**The drive confirmed it, 2026-10-28** (`docs/rig-2026-10-28-5aeefc4/`, `.27`
with Platterpus 0.7.114): all 23 `.27` logs of the reference disc read
`Recordable:     no, CD-ROM (drive's current profile)`, the 17 `.log` files,
the securing pass and the five logs of Platterpus's verified-read chase.

### The footer's AccurateRip tally divides by a count that includes data tracks (fixed for `.27`)

**Found 2026-10-21, answering Platterpus's round 36 lap 3 S8**, which asked
whether it does. `Tracks ripped accurately: %i/%i` and `Tracks matched on one
frame only: %i/%i` both divide by `ctx->nb_tracks`
(`src/cyanrip_log.c:1144-1147`). That is `cdio_cddap_tracks()`, every track the
drive reports (`src/cyanrip_main.c:439`), and data tracks are marked inside it
(`:460`). A data track never gets a per-track AccurateRip status
(`src/accurip.c:199`), so it can never reach the numerator. Built the way
`tests/logrender.c` builds the footer, a three-track disc whose track 1 is data
and whose two audio tracks both verify prints `Tracks ripped accurately: 2/3`;
that probe ran in the session and is not committed. Upstream's line is the same
at `7dbe56a` (`src/cyanrip_log.c:366`).

**What it costs**: on a mixed-mode or enhanced disc the line can never read
N/N, so the line alone shows a disc with a track left unverified.

**Proposed in our round 36 lap 5**: divide both lines by the disc's audio
tracks. The text does not change, but the value does on such a disc, and
Platterpus parses it, so it was built once they accepted. Upstream's report is
drafted with the fix, so that it can name the fork's commit. No fixture is in
AccurateRip's database, so no image rip reaches the line; the fix's test builds
the state in `tests/logrender.c`.

**Fixed for `.27`** (`779549a`), as Platterpus's round 36 lap 6 S2 accepted it:
both lines divide by the disc's audio tracks, and `tests/logrender.c` builds
mixed.cue's shape and reads both over 2. Upstream report 26 names the commit
(`f4da862`).

### A tag value of `..` puts the rip outside its folder, and `-T` passes control characters, a leading dot and reserved names (fixed for `.28`)

**Found by the claude-code-skills session's review of 2026-10-26, item 3.2**,
and measured here at `ed37997` on `tests/fixtures/basic.cue`, track 1, with
`-D <root>/{album_artist}/{album}`, in each of the four `-T` modes (`simple`,
`os_simple`, `unicode`, `os_unicode`), all four alike:

- `-a album=..:album_artist=..` wrote `1.flac`, `log.log` and a cue named
  `...cue` two directories above `<root>`, exit 0. `crip_bprint_sanitize()`
  (`src/naming.c:151`) replaces `< > : | ? * / \ "` and an invalid UTF-8 byte,
  and nothing else, so a value that is exactly `.` or `..` is a path
  component as it stands.
- `album=.hidden` made a directory `.hidden`, hidden on every Unix.
- `album=Ctl` + U+0001 + `x` + newline + `y` made a directory with both
  characters in its name; Windows refuses those characters in a name.
- `album=CON:album_artist=NUL` made `NUL/CON`; on Windows those are devices.

**What it costs**: a disc's CD-TEXT, MusicBrainz or a caller's `-a` can put a
rip's files outside the folder asked for, and on Windows a name can fail or
open a device. Platterpus's own default folder, `{album} [FLAC]`, cannot
traverse, since a suffix follows the value, but a track template with a folder
part can.

**Fixed for `.28`**, at `f69d414` and `ed50558`, after Platterpus accepted our
round 36 lap 12 S10's three rules in their round 36 lap 13 S4, with a fourth
for a component over 255 bytes, and our `Names shortened:` block in their
round 37 lap 2 S5: no component is `.` or `..`, U+0001 to U+001F are replaced,
Microsoft's reserved device names take a `_`, and a leading dot is kept.
Platterpus predicts the folders we
create, for its overwrite guard
(`platterpus@d745464d:src/platterpus/adapters/cyanrip_backend.py:1904-1915`),
so the rules were theirs to absorb first, and the contract's P7f states them.
`sc_path_component_rules()` in `tests/rip_images.py` checks each case in each
`-T` mode. This entry said "not fixed yet" until 2026-11-03, a month-old
sentence the release had already made false.

## Moved from *Open, joint* on 2026-11-04, fixed and pinned by a test

### Under `-Z`, `Extraction speed:` divides one track's audio by every read's time (fixed in `.27`, `db1bbe63`)

**Found by the EAC parity plan of record of 2026-10-26, Appendix H**, in round
36's securing pass of the damaged disc. Track 11 reads `Extraction speed:
1.4x` and `Elapsed: 131.75 s`: 188 seconds of audio over five reads of 23 to
29 seconds each, about 7x apiece.

The track's clock starts before the `-Z` loop and stops after the encode
(`src/cyanrip_main.c`, `track_start_time` and `rip_time_us`), so under `-Z` the
line gives the drive a speed it never read at. `Elapsed:` is right as it
stands: it is the time the track took.

**Fixed for `.27`**: under `-Z`, the speed of the kept read alone, timed from
the start of its pass to the end of its frame loop, with `Elapsed:` unchanged,
as our round 36 lap 8 S27 proposed and Platterpus's lap 9 S18 accepted.
`tests/badsector.c` slows an image's reads so `z_extraction_speed` can tell one
pass from three.
