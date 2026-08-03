# cyanrip → Platterpus, round 5

**From:** `rmccann-hub/cyanrip`, branch `platterpus-fork`
**Pin:** the tip of `platterpus-fork`.
**Last commit that changes the binary:** `becbe4a4cb3fceb4607080966b74e4a8f844d919`
— everything after it touches only `PROVIDER-CONTRACT.md` and this file, so a
build of the tip is bit-identical to a build of `becbe4a`. Pinning the tip is
therefore safe, and this line is stated rather than a raw SHA because a document
cannot contain the hash of the commit that adds it.
**Banner:** `cyanrip 0.9.4-rc1 (platterpus-fork-g<commit>)`
**Round status:** **OPEN** until your verification file arrives. No release, no pin
switch, until then.

This round is bigger than the last few. It carries a completed audit of every
upstream branch, PR and fork; three new capabilities; and — because you asked —
an explicit decision about **which of the two projects owns what**. Section 0 is
the part to read first, because it changes what you should expect from us in
every future round.

---

## 0. The boundary: what lives in cyanrip, what lives in Platterpus

Until now this has been implicit and we have each been guessing. Here is the rule
we propose to hold to. Push back in your return file if any of it is wrong for
you — this is a proposal until you accept it, but we have already built to it.

### The governing principle

> **cyanrip owns everything that requires the disc to be in the drive.
> Platterpus owns everything that can be derived afterwards.**

The test is *recoverability*. If getting a fact wrong means putting the disc back
in the drive, it belongs to cyanrip and must be measured and reported at rip
time. If a bug can be fixed by re-reading the artifacts we left on disk, it
belongs to Platterpus — because putting it in cyanrip would mean **re-ripping the
disc to fix a software bug**, and re-ripping is the one thing an archival
pipeline should never need.

That principle has a corollary that matters more than the file lists below:

> **cyanrip reports measurements with provenance. Platterpus makes judgements.**

cyanrip never says a rip is *good*. It says what it measured, and how it knows.
This is why our log distinguishes `none` from `unknown (reason)`, why the new
cache line says "modelled" and not "defeated", and why the new CD-TEXT line says
"none reported by libcdio" rather than "the disc has none". Every time we have
been tempted to collapse one of those into a verdict, the honest version has
turned out to be the one you could actually act on.

### cyanrip owns

| Domain | Because |
|---|---|
| Drive I/O, TOC, pregaps, sub-channel | Only observable with the disc spinning |
| ISRC, MCN/UPC, CD-TEXT, pre-emphasis flags | On the platter; unrecoverable later |
| Drive vendor/model/revision, read offset, cache model, speed | State of the machine at rip time |
| C2 error counts, paranoia status counters, per-track timing | Transient; gone the instant the rip ends |
| Audio bytes, EAC CRC32, AccurateRip v1/v2/450, peak, loudness | Computed over the samples as they are read |
| The log and cue, as a **stable machine-readable record** of all the above | This is the API |
| **Being diagnosable on every failure path** | A non-zero exit with no output is the one failure you cannot explain to a user |

### Platterpus owns

| Domain | Because |
|---|---|
| Parsing the log/cue into your archival schema | Derived; fixable without the disc |
| MusicBrainz release *selection*, cover art sourcing | Network; you want to control and cache it |
| AccurateRip/CTDB interpretation beyond the numbers we print | Network lookups over checksums we already publish |
| Cross-disc state: dedup, release matching, library layout, renaming | Needs the collection, which we never see |
| The EAC-compatible log rendering, the JSON export, reports | Projections of data we already emit |
| Policy: what counts as an acceptable rip, retry/quarantine decisions | Judgement, not measurement |

### Three consequences we have already acted on

1. **Cache-defeat probing moves to us — stop shelling out to `cd-paranoia -A`.**
   You are currently probing a drive that may no longer hold the same disc, and
   the answer you get is about the drive's state *now*, not at rip time. We now
   report it. See §D3. Note carefully what we report and what we do not: we
   report the **modelled** cache size paranoia is using, and we say the drive was
   **not probed**. If you want a real probe we can add one, but it would be a new
   measurement and it needs its own round — see §J1.

2. **CD-TEXT moves to us.** You pass `-N`, which disables the MusicBrainz lookup,
   which meant *no* on-disc metadata reached you at all. CD-TEXT is the only
   metadata the disc itself carries and it cannot be re-fetched. We now read it.
   See §D1.

3. **CTDB stays with you.** It is a network lookup keyed on checksums we already
   publish. Nothing about it needs the disc. We will not add it.

### Where the boundary will move next

The seam grows. When it does, the rule above decides, not this table. If a change
gives you something new to observe — a new output file, an environment variable,
a schema, a network call, a timing guarantee — it belongs in the contract and in
a round, whether or not any section here names it. When in doubt whether
something is observable: assume it is.

---

## A. Pin

```
repo         rmccann-hub/cyanrip
branch       platterpus-fork          <- pin this
last code    becbe4a4cb3fceb4607080966b74e4a8f844d919
banner       cyanrip 0.9.4-rc1 (platterpus-fork-g<commit>)
```

Nothing after `becbe4a` touches `src/`, `tests/` or `meson.build`, so pinning the
branch tip and pinning `becbe4a` produce the same binary.

The `A. Pin` section below repeats this. `master` in this fork is a clean mirror of upstream `cyanreg/cyanrip` at
`958e1ade67ccba60b323e8abc63162a417ba6a96`. `platterpus-fork` is 22 commits
ahead of it. `git rev-list --all --not platterpus-fork` is empty: nothing is
stranded on another branch.

**Use `platterpus-fork`.** It is the only branch to build against.

---

## B. Answers to your questions

*(Tags: **measured** = observed from a run in this session; **read-from-source** =
read out of the tree; **unverified** = neither.)*

**B1. Does the fork read CD-TEXT?** It does now — it did not before this round.
**measured.** Verified end to end against a cdrdao `.toc` image; disc-level and
per-track fields both parse. See §D1 and the golden log in §E2.

**B2. Is cache defeat reported?** Now yes, with an important qualification.
**measured.** We report the paranoia *cache model* size, not a probe of the
drive. See §D3 and §J1.

**B3. Did the audit find anything else we were missing?** Yes, and also a good
deal of "we already have it". Full results in §C1. Net: three real capability
gaps, all now closed; eleven upstream PRs confirmed already present; one upstream
PR deliberately not carried, with a reason.

---

## C. Commits since the last pin

| Commit | Subject | Touches log text? |
|---|---|---|
| `db05896` | Read and report the disc's CD-TEXT | **Yes** — 2 new lines |
| `3a28d4a` | Report true peak and the paranoia cache model in the log | **Yes** — 4 new lines |
| `becbe4a` | Recover Q sub-channel data from drives that return it as raw binary | No |
| `2c3a947` | Regenerate provider contract at the current pin | No (generated doc) |

Every log change is **additive**. No existing line changed its text, indentation,
field order or units. Nothing you currently parse moves.

### C1. The audit, in full

You asked whether anything had been missed across other branches, PRs and forks.
Method: fetched all 3 upstream branches and all 39 upstream PR heads into the
local clone and compared **actual file content**, not PR prose.

A correction on method, because it nearly produced a wrong answer: three-dot
diffs (`git diff ours...theirs`) against those PR branches are **useless here**.
Several PR branches share no common ancestor with the fork at all
(`git merge-base` errors), and others fork so far back that the diff shows the
entire intervening history. Two PRs first looked like gaps this way and turned
out to be present verbatim in our tree. Everything below was checked by reading
the file.

**Already present** — merged upstream, and in the fork:

`#104` pregap count with offset > 1 sector · `#106` data-track offset detection ·
`#114` `crip_stat` → `cyanrip_stat` rename · `#118` zero-duration cue PREGAP and
duplicate `TRACK` lines · `#119` `cdio_get_hwinfo` drive info · `#120` "ripped
and encoded with errors" · `#122` no-pregap merged-pregap cue fix · `#127` `.toc`
device detection · `#128` `-J` cue-only · `#130` MSF duration · `#131` cleanup
segfault · `#132` stdout flush · `#147` AccurateRip CDDB `strtoul`. Upstream
branches `accurip_test` and `deemphasis` are both merged.

**Gaps found and now closed:**

| Gap | Source | Commit |
|---|---|---|
| CD-TEXT never read; full libcdio API unused | our own tree | `db05896` |
| `t->ebu_true_peak` computed and discarded | our own tree | `3a28d4a` |
| Cache-defeat state never reported | EAC parity | `3a28d4a` |
| Q sub-channel BCD-vs-binary drive quirk | upstream `#153` | `becbe4a` |
| No hardware-free test for any sub-channel logic | upstream `#153` | `becbe4a` |

**Deliberately not carried:** the rest of upstream `#153`. Its restructure is
good, but its macOS path calls `cdio_get_device_fd()`, which **is not in libcdio
2.1.0** — verified against both the installed headers and the `.so` export table,
not assumed. Carrying it would break the macOS build against current
distributions. We took the algorithm and left the plumbing; our own macOS
workaround stays.

**Not a gap, deliberately:** CTDB, and an EAC-format log writer. Both are
Platterpus's side of the boundary — see §0.

---

## D. Log-format delta

**There are changes this round.** Seven new lines. No line you currently parse
has changed.

### D1. CD-TEXT — disc level

Emitted in the disc header block, immediately after `C2 errors:`. Exactly one of:

```
CD-TEXT:        present (English, 5 disc fields, 2 of 2 tracks tagged)
CD-TEXT:        none reported by libcdio (absent, or unreadable by this driver)
```

When present, an aligned block of the disc-level fields follows, 4-space indented,
using the CD-TEXT spec's own field names lowercased:

```
    title:     Probe Disc Title
    performer: Probe Disc Performer
    message:   Probe disc message
    upc_ean:   0123456789012
    discid:    PROBE-DISCID
```

Possible keys: `title` `performer` `songwriter` `composer` `message` `arranger`
`isrc` `upc_ean` `genre` `discid`. Only non-empty fields appear. Alignment
padding is computed per block from the longest key present, so **do not assume a
fixed column** — split on the first `: `.

**Read the negative case carefully.** It does not say the disc has no CD-TEXT. It
says libcdio reported none. `cdio_get_cdtext()` returns the same NULL for a disc
without a CD-TEXT block and for a driver that cannot read one, and exposes no way
to tell them apart. Please do not render this as "no CD-TEXT on disc" in your
output — that is a stronger claim than the data supports.

### D2. CD-TEXT — per track

In the track block, after `Metadata:` and before `Embedded cover art:` /
`File(s):`. Present only for tracks the disc actually tagged:

```
  CD-TEXT:
    title:      Probe Track One
    performer:  Probe Artist One
    songwriter: Probe Writer One
    composer:   Probe Composer One
    arranger:   Probe Arranger One
```

A missing block is unambiguous: the disc-level line already told you how many of
how many tracks were tagged.

**These fields are verbatim and are never overwritten.** They are what the disc
says, held separately from the `Metadata:` block above them, which by that point
may have been replaced by MusicBrainz or by a `-a`/`-t` value. If you want to
record what the plant pressed, this block is the one to read — not `Metadata:`.

### D3. Cache defeat

In the disc header block, immediately after `Frame retries:`. Exactly one of:

```
Cache defeat:   1200 sectors modelled (drive cache size not probed)
Cache defeat:   1 sector modelled (disc image, no drive cache)
Cache defeat:   not in use (paranoia disabled)
```

Note "sector" vs "sectors" — the singular is used for 1.

**This is not EAC's `Defeat audio cache : Yes`, and should not be rendered as
one.** The number is the size paranoia *models*, not a measurement of the drive.
cyanrip never probes the drive the way `cd-paranoia -A` does. Reporting a
defeated cache would assert something no part of the run established. See §J1 if
you want the real probe.

### D4. True peak

In the track `Properties:` block, on the line after `Peak level:`:

```
    Peak level:  99.8%
    True peak level: -0.0 dBFS
```

Named `True peak level`, deliberately, so it cannot be confused with
libavfilter's own `  True peak:` heading two-space-indented elsewhere in the
track block. **That other one is FFmpeg's wording and moves when FFmpeg does — do
not parse it.** This one is ours and is covered by the contract.

### D5. Full stable-line count

`249` distinct stable lines, up from `241`. `37` flags, unchanged. `88` distinct
fatal/error strings, unchanged. Generated inventory in §I.

---

## E. Golden logs

Two, because the CD-TEXT path needs its own.

### E1. `tests/fixtures/pregap.cue` — 238 lines

Regenerate exactly:

```sh
cp tests/fixtures/pregap.cue tests/fixtures/cdda.bin /tmp/g/ && mv /tmp/g/cdda.bin /tmp/g/pregap.bin
cd /tmp/g && cyanrip -d pregap.cue -N -A -Q -s 0 -o flac
```

### E2. `tests/fixtures/cdtext.toc` — 200 lines

```sh
cp tests/fixtures/cdtext.toc tests/fixtures/cdda.bin /tmp/c/ && mv /tmp/c/cdda.bin /tmp/c/cdtext.bin
cd /tmp/c && cyanrip -d cdtext.toc -N -A -Q -s 0 -o flac
```

**The `cd` is not optional.** libcdio's cdrdao driver opens a `.toc`'s `FILE`
with the raw relative path instead of the absolute one it just computed
(`lib/driver/image/cdrdao.c` — `cdio_stdio_new(psz_field)` where it should pass
`psz_filename`; `bincue.c` gets this right). A `.toc` therefore only loads when
the process's working directory is the image's directory. This is upstream
libcdio's bug, not ours, and we cannot fix it from here. **If you ever feed
cyanrip a `.toc`, set cwd accordingly or it will fail to open.** `.cue` and
`.nrg` are unaffected.

---

## F. Proven vs not proven

### Proven — with how

| Claim | How |
|---|---|
| No change alters one audio byte or one checksum | Built upstream `958e1ad` in a worktree, ripped all 5 fixtures with both binaries, diffed **55 checksum lines** (EAC CRC32 + AccurateRip v1/v2/450) and **11 decoded-PCM md5s**. Identical. |
| Builds clean | Clean-tree `meson setup` + `ninja`: **0 warnings, 0 errors** |
| Suite green | **14/14** (`meson test`), up from 12 — two new tests this round |
| Each commit is independently buildable | Checked out and built each of the 3 code commits: 0 issues, tests green at each |
| CD-TEXT reads disc-level and per-track | `.toc` fixture; both parse; see §E2 |
| CD-TEXT never overrides user metadata | Test asserts `-a album=…` wins **and** that the verbatim CD-TEXT block survives it |
| CD-TEXT absent case reports correctly | Test asserts the `none reported by libcdio` line on `basic.cue` |
| BCD sub-channel fixup is correct | Unit test on synthetic sectors, CRC-16/GSM vector computed **independently of this code**, so it pins the polynomial rather than agreeing with itself |
| Nothing stranded on another branch | `git rev-list --all --not platterpus-fork` → empty |
| The contract is not stale | `tools/gen-provider-contract.py --check` exits 0 |

### Not proven — needs real hardware

This is the part a green suite must not be read as covering.

| Not proven | Why no fixture can |
|---|---|
| **The BCD-binary drive quirk end to end** | Disc images resolve pregaps from the TOC. The MMC sub-channel read path is never entered. The unit test proves the *decoder*; only a drive with that firmware proves the *fix*. |
| Sub-channel pregap detection on a physical disc | Same reason |
| Drive read-offset autodetection (`-f`) | Needs a drive |
| C2 error reporting | No image reports C2 |
| Paranoia error correction on damaged media | No image is damaged |
| Real cache-defeat behaviour | We model it; we do not measure it (§D3) |
| CD-TEXT from a **real disc** | Proven only from a `.toc` image. The libcdio parse path for a physical disc (`mmc_read_cdtext`) is a different code path from the image parser and is untested here. |

The last row is new and matters: **do not read §F's CD-TEXT rows as covering
physical discs.** They cover the image path only.

---

## G. Revert-proof, per fix

Each was actually reverted, rebuilt, and the test watched to fail.

| Fix | Reverted by | Result |
|---|---|---|
| CD-TEXT read | Stubbing out `crip_fill_cdtext(ctx)` | **16 checks failed**; restored → pass |
| BCD sub-channel fixup | Replacing `verify_subq_crc()` with a plain CRC compare | **9 checks failed**; restored → pass |

True peak and cache defeat are additive reporting of values the program already
had; there is no behaviour to revert-prove beyond the lines appearing, which §E
shows.

---

## H. Anything found wrong in *your* output

**Nothing found in your parser output this round** — stating it out loud, as the
protocol requires, rather than leaving the section empty.

Two findings that are adjacent, and are about your *pipeline* rather than your
parser:

**H1. `cd-paranoia -A` as a cache probe is in the wrong place.** It probes the
drive's state at the moment you run it, which is not the moment of the rip, and
possibly not even the same disc. It also cannot be correlated to a specific rip
in your archive. This is a boundary error, not a bug — see §0 and §D3. We now
report the cache model at rip time. Whether you want a real probe is §J1.

**H2. If you render our new CD-TEXT absent-line as "no CD-TEXT on disc", that
will be a wrong claim in your archive.** It is not what the line says and not
what libcdio can tell us. Flagging pre-emptively because the shorter phrasing is
the tempting one.

---

## I. Provider contract

Generated, never hand-written, by `tools/gen-provider-contract.py` from the
source tree and the built binary:

- **P1** every flag, from the binary's own `--help` (37)
- **P2** every stable log line — the API (249)
- **P3** every unstable line, and whether it reaches the logfile
- **P4** exit codes, and whether any non-zero exit can be silent
- **P5** the fatal/error message inventory with `file:line` (88)

Ship-and-check: `tools/gen-provider-contract.py --check PROVIDER-CONTRACT.md`
exits non-zero when the committed copy is stale. It is run after any change to a
`cyanrip_log()` call site or the option table.

The full generated document is `PROVIDER-CONTRACT.md` at the pin. It is 492 lines
and is committed alongside this file rather than pasted here — **read it from the
repo at the pinned commit**, so you get the version that matches the binary you
are building.

---

## J. Questions back

**J1. Do you want a real drive-cache probe?** We can implement the
`cd-paranoia -A`-style probe inside cyanrip so it happens at rip time on the
right disc, and report a measured cache size instead of a modelled one. It costs
seconds of drive time per rip and it is a genuinely new measurement, so it needs
its own round. Say whether you want it, and whether you want it default-on,
default-off, or behind a flag.

**J2. Should CD-TEXT gap-fill metadata at all, or only be reported?** Today it
does both: reported verbatim (never overwritten), *and* used to fill tags nothing
else claimed, giving user `-a`/`-t` > MusicBrainz > CD-TEXT > defaults. That
means filenames can now come from CD-TEXT where they previously said "Unknown
disc". If you would rather cyanrip never let CD-TEXT touch the tags — reporting
only, you decide precedence — say so; it is a one-line change and it is your call
under §0.

**J3. Do you want `songwriter` and `arranger` mapped to file tags?** They come
through in CD-TEXT and are reported, but they reach no output-file tag, because
neither has a standard FFmpeg key and we would be inventing one. Currently they
exist only in the log's CD-TEXT block.

**J4. Do you accept §0 as the boundary?** This is the one that matters. If you
disagree with any row, say which — we have built to it, but it is a proposal
until you have verified it against what your pipeline actually does.

**Still open from round 4**, no answer received: log-content test assertions
(J1'), `--dirty` in the build tag (J2'), zero-byte FLAC handling (J3').

---

## What we need back

A verification file that (a) confirms the pin builds and your parser handles the
seven new lines, (b) rules on §J1–J4, and (c) states out loud whether you found
anything wrong here — including "nothing found". Until it arrives this round is
**OPEN**, and we will not cut a release or move the pin.

---

## Appendix 1 — golden log, `pregap.cue` (238 lines)

Byte-for-byte as emitted at the pin. The `Invoked as:` and `creation_time`
lines vary per run; everything else is reproducible.

```
cyanrip 0.9.4-rc1 (platterpus-fork-gbecbe4a)
Invoked as:     /home/user/cyanrip/build/src/cyanrip -d pregap.cue -N -A -Q -s 0 -o flac
Drive used:     libcdio CDRWIN (revision 2.1.)
System device:  pregap.cue
Offset:         +0 samples
Overread:       +0 frames
Overread mode:  fill with silence in lead-in/lead-out
Speed:          default (unchangeable)
C2 errors:      unsupported by drive
CD-TEXT:        none reported by libcdio (absent, or unreadable by this driver)
Paranoia level: max
Frame retries:  10
Cache defeat:   1 sector modelled (disc image, no drive cache)
HDCD decoding:  disabled
Album Art:      none
Outputs:        flac
Disc tracks:    3
Tracks to rip:  all
DiscID:         oMp2k.ixH0QqrdaZzsARoRS.p6c-
CDDB ID:        14000603
Album:          Unknown disc (OMP2)
AccurateRip:    disabled
Total time:     00:08.00

Gaps:
    150 frame pregap in track 1, unmerged
    75 frame pregap in track 2, merging into track 1

Tracks:
Track 1 ripped and encoded successfully!
Summary:

  Integrated loudness:
    I:         -20.6 LUFS
    Threshold: -30.6 LUFS

  Loudness range:
    LRA:        20.0 LU
    Threshold: -49.4 LUFS
    LRA low:   -49.4 LUFS
    LRA high:  -29.4 LUFS

  Sample peak:
    Peak:       -0.0 dBFS

  True peak:
    Peak:       -0.0 dBFS

  Preemphasis:   none detected

  Properties:
    Duration:    00:03.00
    Samples:     132300
    Frames:      225
    Peak level:  99.7%
    True peak level: -0.0 dBFS
    Extraction speed:  16.1x
    Elapsed:            0.19 s
    Pregap LSN:  0 (duration: 00:04.00)
    Pregap length: 300 frames
    Pregap source: TOC
    Start LSN:   150
    End LSN:     374

  EAC CRC32:     D5F7BC20
  Secure re-read:  not attempted
  Accurip:       disabled
    Accurip v1:  00000000
    Accurip v2:  00000000
    Accurip 450: 00000000

  Metadata:
    track:                         1
    tracktotal:                    3
    musicbrainz_discid:            oMp2k.ixH0QqrdaZzsARoRS.p6c-
    cddb:                          14000603
    media:                         CD
    comment:                       cyanrip 0.9.4-rc1
    album:                         Unknown disc (OMP2)
    title:                         Unknown track
    creation_time:                 2026-08-03T01:39:34
    REPLAYGAIN_TRACK_GAIN:         2.64 dB
    R128_TRACK_GAIN:               1956
    REPLAYGAIN_TRACK_RANGE:        20.00 dB
    REPLAYGAIN_TRACK_PEAK:         0.998996
    REPLAYGAIN_REFERENCE_LOUDNESS: -18.00 LUFS

  File(s):
    Unknown disc (OMP2) [FLAC]/1 - Unknown track.flac

Track 2 ripped and encoded successfully!
Summary:

  Integrated loudness:
    I:         -24.0 LUFS
    Threshold: -34.0 LUFS

  Loudness range:
    LRA:         0.0 LU
    Threshold:   0.0 LUFS
    LRA low:     0.0 LUFS
    LRA high:    0.0 LUFS

  Sample peak:
    Peak:       -2.8 dBFS

  True peak:
    Peak:       -2.6 dBFS

  Preemphasis:   none detected

  Properties:
    Duration:    00:02.00
    Samples:     88200
    Frames:      150
    Peak level:  72.4%
    True peak level: -2.6 dBFS
    Extraction speed:  16.4x
    Elapsed:            0.12 s
    Pregap LSN:  300 (duration: 00:01.00)
    Pregap length: 75 frames
    Pregap source: TOC
    Start LSN:   375
    End LSN:     524

  EAC CRC32:     9869CDF5
  Secure re-read:  not attempted
  Accurip:       disabled
    Accurip v1:  956D1AF6
    Accurip v2:  956E22AE
    Accurip 450: 00000000

  Metadata:
    track:                         2
    tracktotal:                    3
    musicbrainz_discid:            oMp2k.ixH0QqrdaZzsARoRS.p6c-
    cddb:                          14000603
    media:                         CD
    comment:                       cyanrip 0.9.4-rc1
    album:                         Unknown disc (OMP2)
    title:                         Unknown track
    creation_time:                 2026-08-03T01:39:34
    REPLAYGAIN_TRACK_GAIN:         5.97 dB
    R128_TRACK_GAIN:               2808
    REPLAYGAIN_TRACK_RANGE:        0.00 dB
    REPLAYGAIN_TRACK_PEAK:         0.738850
    REPLAYGAIN_REFERENCE_LOUDNESS: -18.00 LUFS

  File(s):
    Unknown disc (OMP2) [FLAC]/2 - Unknown track.flac

Track 3 ripped and encoded successfully!
Summary:

  Integrated loudness:
    I:         -40.9 LUFS
    Threshold: -50.9 LUFS

  Loudness range:
    LRA:         0.0 LU
    Threshold:   0.0 LUFS
    LRA low:     0.0 LUFS
    LRA high:    0.0 LUFS

  Sample peak:
    Peak:      -21.0 dBFS

  True peak:
    Peak:      -21.0 dBFS

  Preemphasis:   none detected

  Properties:
    Duration:    00:01.00
    Samples:     44100
    Frames:      75
    Peak level:  8.9%
    True peak level: -21.0 dBFS
    Extraction speed:  16.9x
    Elapsed:            0.06 s
    Pregap LSN:  unknown (sub-channel unreadable)
    Start LSN:   525
    End LSN:     599

  EAC CRC32:     9F27F613
  Secure re-read:  not attempted
  Accurip:       disabled
    Accurip v1:  84F0CFDC
    Accurip v2:  84F20136
    Accurip 450: 00000000

  Metadata:
    track:                         3
    tracktotal:                    3
    musicbrainz_discid:            oMp2k.ixH0QqrdaZzsARoRS.p6c-
    cddb:                          14000603
    media:                         CD
    comment:                       cyanrip 0.9.4-rc1
    album:                         Unknown disc (OMP2)
    title:                         Unknown track
    creation_time:                 2026-08-03T01:39:35
    REPLAYGAIN_TRACK_GAIN:         22.93 dB
    R128_TRACK_GAIN:               7150
    REPLAYGAIN_TRACK_RANGE:        0.00 dB
    REPLAYGAIN_TRACK_PEAK:         0.088933
    REPLAYGAIN_REFERENCE_LOUDNESS: -18.00 LUFS

  File(s):
    Unknown disc (OMP2) [FLAC]/3 - Unknown track.flac

Album Loudness Summary:

  Integrated loudness:
    I:         -23.1 LUFS
    Threshold: -35.6 LUFS

  Loudness range:
    LRA:         0.1 LU
    Threshold: -52.5 LUFS
    LRA low:   -32.7 LUFS
    LRA high:  -32.6 LUFS

  Sample peak:
    Peak:       -0.0 dBFS

  True peak:
    Peak:       -0.0 dBFS

Paranoia status counts:
  READ:          2657
  VERIFY:        37559
  SKIP:          272
  OVERLAP:       445

Ripping errors: 0
Rip completed:  yes (3 of 3 tracks)
Ripping finished at 2026-08-03T01:39:35
Log FUN512: Vbnb9eWSYtWLubx6ru09kZUEnqzc6kZEUJzXSQL4L9y2SoPBag_eNAYhogkYGJJENkKEk.51mKLv8PTqOfOwBg
```

## Appendix 2 — golden log, `cdtext.toc` (200 lines)

The CD-TEXT path. Note the disc-level `CD-TEXT:` block after `C2 errors:`,
the per-track `CD-TEXT:` blocks after each `Metadata:`, and that `Album:` and
`Album artist:` came from the disc rather than from "Unknown disc".

```
cyanrip 0.9.4-rc1 (platterpus-fork-gbecbe4a)
Invoked as:     /home/user/cyanrip/build/src/cyanrip -d cdtext.toc -N -A -Q -s 0 -o flac
Drive used:     libcdio cdrdao (revision 2.1.)
System device:  cdtext.toc
Offset:         +0 samples
Overread:       +0 frames
Overread mode:  fill with silence in lead-in/lead-out
Speed:          default (unchangeable)
C2 errors:      unsupported by drive
CD-TEXT:        present (English, 5 disc fields, 2 of 2 tracks tagged)
    title:     Probe Disc Title
    performer: Probe Disc Performer
    message:   Probe disc message
    upc_ean:   0123456789012
    discid:    PROBE-DISCID
Paranoia level: max
Frame retries:  10
Cache defeat:   1 sector modelled (disc image, no drive cache)
HDCD decoding:  disabled
Album Art:      none
Outputs:        flac
Disc tracks:    2
Tracks to rip:  all
DiscID:         OnpX1oVWL7CypwcIA.ZsRybkaBw-
CDDB ID:        08000802
Album:          Probe Disc Title
Album artist:   Probe Disc Performer
AccurateRip:    disabled
Total time:     00:08.00

Gaps:
    None signalled

Tracks:
Track 1 ripped and encoded successfully!
Summary:

  Integrated loudness:
    I:         -22.3 LUFS
    Threshold: -32.3 LUFS

  Loudness range:
    LRA:        20.0 LU
    Threshold: -51.0 LUFS
    LRA low:   -51.0 LUFS
    LRA high:  -31.0 LUFS

  Sample peak:
    Peak:       -0.0 dBFS

  True peak:
    Peak:       -0.0 dBFS

  Preemphasis:   none detected

  Properties:
    Duration:    00:04.00
    Samples:     176400
    Frames:      300
    Peak level:  99.8%
    True peak level: -0.0 dBFS
    Extraction speed:  14.8x
    Elapsed:            0.27 s
    Pregap LSN:  0 (duration: 00:02.00)
    Pregap length: 150 frames
    Pregap source: lead-in
    Start LSN:   0
    End LSN:     299

  EAC CRC32:     73078F44
  Secure re-read:  not attempted
  Accurip:       disabled
    Accurip v1:  00000000
    Accurip v2:  00000000
    Accurip 450: 00000000

  Metadata:
    title:                         Probe Track One
    artist:                        Probe Artist One
    composer:                      Probe Composer One
    track:                         1
    tracktotal:                    2
    musicbrainz_discid:            OnpX1oVWL7CypwcIA.ZsRybkaBw-
    cddb:                          08000802
    album:                         Probe Disc Title
    album_artist:                  Probe Disc Performer
    barcode:                       0123456789012
    comment:                       cyanrip 0.9.4-rc1
    media:                         CD
    creation_time:                 2026-08-03T01:39:35
    REPLAYGAIN_TRACK_GAIN:         4.27 dB
    R128_TRACK_GAIN:               2373
    REPLAYGAIN_TRACK_RANGE:        20.00 dB
    REPLAYGAIN_TRACK_PEAK:         0.999750
    REPLAYGAIN_REFERENCE_LOUDNESS: -18.00 LUFS

  CD-TEXT:
    title:      Probe Track One
    performer:  Probe Artist One
    songwriter: Probe Writer One
    composer:   Probe Composer One
    arranger:   Probe Arranger One

  File(s):
    Probe Disc Title [FLAC]/1 - Probe Track One.flac

Track 2 ripped and encoded successfully!
Summary:

  Integrated loudness:
    I:         -22.0 LUFS
    Threshold: -32.0 LUFS

  Loudness range:
    LRA:        20.0 LU
    Threshold: -50.8 LUFS
    LRA low:   -50.8 LUFS
    LRA high:  -30.8 LUFS

  Sample peak:
    Peak:       -1.8 dBFS

  True peak:
    Peak:       -1.7 dBFS

  Preemphasis:   none detected

  Properties:
    Duration:    00:04.00
    Samples:     176400
    Frames:      300
    Peak level:  81.6%
    True peak level: -1.7 dBFS
    Extraction speed:  13.3x
    Elapsed:            0.30 s
    Pregap LSN:  unknown (sub-channel unreadable)
    Start LSN:   300
    End LSN:     599

  EAC CRC32:     376A2BE1
  Secure re-read:  not attempted
  Accurip:       disabled
    Accurip v1:  31C74DF1
    Accurip v2:  31C888E0
    Accurip 450: 00000000

  Metadata:
    title:                         Probe Track Two
    artist:                        Probe Artist Two
    track:                         2
    tracktotal:                    2
    musicbrainz_discid:            OnpX1oVWL7CypwcIA.ZsRybkaBw-
    cddb:                          08000802
    album:                         Probe Disc Title
    album_artist:                  Probe Disc Performer
    barcode:                       0123456789012
    comment:                       cyanrip 0.9.4-rc1
    media:                         CD
    creation_time:                 2026-08-03T01:39:35
    REPLAYGAIN_TRACK_GAIN:         4.04 dB
    R128_TRACK_GAIN:               2314
    REPLAYGAIN_TRACK_RANGE:        20.00 dB
    REPLAYGAIN_TRACK_PEAK:         0.820381
    REPLAYGAIN_REFERENCE_LOUDNESS: -18.00 LUFS

  CD-TEXT:
    title:     Probe Track Two
    performer: Probe Artist Two

  File(s):
    Probe Disc Title [FLAC]/2 - Probe Track Two.flac

Album Loudness Summary:

  Integrated loudness:
    I:         -22.1 LUFS
    Threshold: -32.1 LUFS

  Loudness range:
    LRA:         0.0 LU
    Threshold: -50.8 LUFS
    LRA low:   -30.8 LUFS
    LRA high:  -30.8 LUFS

  Sample peak:
    Peak:       -0.0 dBFS

  True peak:
    Peak:       -0.0 dBFS

Paranoia status counts:
  READ:          3235
  VERIFY:        45702
  SKIP:          332
  OVERLAP:       467

Ripping errors: 0
Rip completed:  yes (2 of 2 tracks)
Ripping finished at 2026-08-03T01:39:35
Log FUN512: U3YgL7c2ncb3zDpVIx.b_jXFO0phPWTXqydOnsGR7OiQ194xqr9bRdHwW9fjEzCx83inok8esoMXRMhv.w6Qhg
```

## Appendix 3 — provider contract

Generated. Reproduce with `tools/gen-provider-contract.py` at the pin;
verify with `--check`. Reproduced in full below so this file stands alone.

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

