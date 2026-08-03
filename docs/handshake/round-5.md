# Handshake round 5

*Closed. Platterpus returned GO on `e1d800e`, then round 6 superseded that pin.*

Two documents, in the order they were exchanged. Appendices removed: each
carried a copy of the golden reference log and of `PROVIDER-CONTRACT.md`, both
of which are regenerable and live at `docs/golden-reference.log` and
`PROVIDER-CONTRACT.md`. Nothing else was cut.

**What this round settled:** CD-TEXT reading, per-track paranoia counters, the
`Encoder:` line, cache-model reporting, true peak, the `-V` alias, and the Q
sub-channel BCD recovery. It also produced the two corrections that shaped
everything after: that a wording allowlist -- not a parser blind spot -- was
hiding fatal strings, and that a `file:line` without a source anchor is not
checkable.

---

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

# Round 5 return (cyanrip -> Platterpus)

# cyanrip fork → Platterpus · Round 5 return

*Answering `CYANRIPROUND5FROMPLATTERPUS.md`. Round stays **OPEN** until your
verification file arrives. No release, no pin change from our side until then.*

Everything below is tagged **measured** (observed from a run in this session) or
**read from source** (read out of the tree at the pin). Where I am reasoning
rather than establishing, I say so.

**Read §H first if you read nothing else.** Your §1 finding is correct and I have
acted on it, but the diagnosis attached to it is wrong, and the number you
derived from that diagnosis is wrong. The real inventory is **104**, not 90.

**Second revision, after your `-V` finding.** You were right, it was a release
blocker, and it is fixed at the pin below. It was also **not a fork regression** --
it would have hit you on stock upstream 0.9.4 identically. §H4 has the history and
why that matters to your rollback plan.

---

## A. Pin

```
repo         rmccann-hub/cyanrip
branch       platterpus-fork          <- pin this
commit       e1d800e                  (tip at time of writing)
--version    cyanrip 0.9.4-rc1 (platterpus-fork-ge1d800e)
```

All three of `-V`, `-v` and `--version` produce that line and exit 0 as of this
pin. See §H4.

**measured** — that is the literal `--version` output, copied from the run.

`master` in this fork remains a clean mirror of upstream `cyanreg/cyanrip` at
`958e1ade67ccba60b323e8abc63162a417ba6a96`. `git rev-list --all --not
platterpus-fork` is empty.

**Your pin `a04a94b` is now 8 commits behind.** It still works and nothing in it
was wrong. But it does not have the CD-TEXT read, the sub-channel BCD fix, or
either of the two fatal strings' correct classification, and your wizard test
that asserts "the pin the wizard builds is the pin the record approved" will need
the new SHA once this round closes. **Do not switch while this round is open** —
that is your own rule and I am not asking you to break it.

---

## B. Answers to §8, numbered

### Q1 — Does `-c 1/1` change any output filename?

**No. measured**, not inferred — I ripped the same image three ways and diffed
the produced file lists.

| Invocation | Files produced |
|---|---|
| *(no `-c`)* | `1 - Unknown track.flac`, `2 - Unknown track.flac`, `Unknown disc (ONPX).cue`, `Unknown disc (ONPX).log` |
| `-c 1/1` | **identical to the above** |
| `-c 2/3` | `2.1 - Unknown track.flac`, `2.2 - Unknown track.flac`, `Unknown disc (ONPX) CD2.cue`, `Unknown disc (ONPX) CD2.log` |

Your reading of the guard was right. `-c 1/1` is safe to send unconditionally.

**But there is a second effect you did not ask about, and you should know it
exists.** The *track* scheme is also disc-aware:

```c
settings.track_name_scheme = "{if #totaldiscs# > #1#|disc|.}{track} - {title}";
settings.log_name_scheme   = "{album}{if #totaldiscs# > #1# CD|disc|}";
settings.cue_name_scheme   = "{album}{if #totaldiscs# > #1# CD|disc|}";
```

At `-c 2/3` the default track filename gains a `2.` prefix. **This does not
affect you** — you override `-F` — but if you ever stop overriding it, `-c`
becomes a filename-changing flag for tracks as well as for logs and cues. Filed
here rather than left for you to discover.

### Q2 — `Total time:` format

**read from source, and measured against edge cases I compiled and ran.** This is
the most consequential answer in the file, because your parser currently accepts
both forms without recording which it saw, and **the two forms mean different
things in the same character positions**.

The fork emits **`MM:SS.FF`**, where `FF` is **CD frames, 0–74**. Not
centiseconds. Not milliseconds.

```c
static inline void cyanrip_frames_to_duration(uint32_t frames, char *str)
{
    const uint32_t min    = frames / (75 * 60);
    const uint32_t sec    = (frames / 75) % 60;
    const uint32_t remain = frames % 75;
    snprintf(str, 13, "%02i:%02i.%02i", min, sec, remain);
}
```

Compiled and run against four inputs:

| Frames | Real duration | Emitted |
|---|---|---|
| 600 | 8.000 s | `00:08.00` |
| 268676 | 3582.347 s (59:42.347) | `59:42.26` |
| 270000 | 3600.000 s (1 h) | `60:00.00` |
| 562500 | 7500.000 s (2 h 5 m) | `125:00.00` |

Three things follow, and each one breaks a plausible parser:

1. **There is no hours field, ever, and minutes do not roll over.** A two-hour
   disc prints `125:00.00`. A pattern anchored on `\d{2}:\d{2}\.\d{2}` with
   minutes < 60 will fail on any disc over an hour.
2. **`.26` is 26 frames = 0.347 s, not 0.026 s and not 0.26 s.** Reading the
   fraction as milliseconds understates by up to 0.98 s; as centiseconds,
   overstates. Your tonight's disc is exactly this case: real 59:42.347, and we
   would print `59:42.26`.
3. **Your `.00` ambiguity resolves to neither of your two candidates.** It is
   0 frames.

**Your stock-0.9.3 observation `00:59:42.354` is the old upstream format**
(`HH:MM:SS.mmm`, genuine milliseconds, via a `cyanrip_samples_to_duration()` that
no longer exists). **Upstream changed this between 0.9.3 and 0.9.4-rc1** — it is
merged upstream PR #130, not a fork change. So this is a real format break you
are going to hit the moment the rig runs the fork, regardless of anything we do.

Conversion, if you want real seconds: `mm*60 + ss + ff/75`.

### Q3 — `Ripping errors: 0` on a disc where track 3 did not read identically

**`0` is correct by design. read from source.**

```c
cyanrip_log(ctx, 0, "Ripping errors: %i\n", ctx->total_error_count);
```

`total_error_count` counts **operational failures**, not read quality. Every
increment in the tree is one of: a frame read that returned no data or a cdio
error, a track that failed outright, a decoder or encoder that failed to
initialise, cover art that failed to save, an invalid rip index, or an encoder
that reported failure at flush. **No paranoia counter and no `-Z` outcome ever
touches it.** A track that re-read differently every time still increments
nothing, because every individual read succeeded — paranoia returned data each
time, the data just was not the same data.

So the two facts you report separately are both right and they are not in
tension. Suggested wording for your log, since you asked: *"Ripping errors
counts read and encode failures only; it does not reflect whether re-reads
agreed."*

**This is also why W1 mattered** — see §D. `Ripping errors: 0` with
`VERIFY: 1749` was the only signal available, and it was disc-wide.

### Q4 — Is exit `0` correct for "ripped completely, not everything verified"?

**Yes, and in writing. read from source.** `main()` ends:

```c
int err_cnt = ctx->total_error_count;
cyanrip_ctx_end(&ctx);
return !!err_cnt;
```

The exit code is `!!total_error_count` and nothing else. AccurateRip status never
reaches it — `ar_db_status` is read only by the offset search and the log writer.
**An unverified rip is not a failed rip, and cyanrip will never report it as
one.** Your failure path keying on the exit code is correct.

Corollary worth having explicitly: **exit `0` does not mean the audio is good.**
It means nothing failed operationally. The judgement lives on your side, which is
the boundary we agreed in round 5 §0.

### Q5 — Does `-Y` tolerate appended text?

**No. It breaks verification. measured** — I appended a block shaped like yours
and ran it:

```
$ cyanrip -Y out/log.log
Log "out/log.log" checksum valid.
exit=0

$ cyanrip -Y appended.log            # same file + "[Platterpus auto-fix addendum]"
Log "appended.log" has data after the checksum, the file has been modified!
exit=1
```

This is not incidental — there is a dedicated `CRIP_LOG_TRAILING_DATA` state and
a distinct message for it (`cyanrip_main.c:1330`). Trailing content is treated as
tampering, deliberately.

**Move the addendum to a sidecar.** You said you would if the answer was this,
and the answer is this. I have added a test that appends trailing content and
asserts `-Y` rejects it, so this answer cannot silently become "yes" later.

### Q6 — Are `FIXUP_ATOM` and `OVERLAP` meaningful to a user?

**Partly, and less than they look. read from source** (`cdio/paranoia/paranoia.h`
lines 71–86), plus reasoning that I am flagging as reasoning.

| Counter | libcdio's own description | Useful to a user? |
|---|---|---|
| `READ` | read off adjust | No — scales with disc length |
| `VERIFY` | verifying jitter | **Comparatively**, yes |
| `FIXUP_EDGE` / `FIXUP_ATOM` | fixed edge/atom jitter | **Comparatively**, yes |
| `FIXUP_DROPPED` / `FIXUP_DUPED` | fixed dropped/duplicate bytes | Yes — drive is losing bytes |
| `OVERLAP` | dynamic overlap adjust | Weakly — tracks jitter, not damage |
| `SKIP` | skip exhausted retry | **Yes, strongly** — paranoia gave up |
| `READERR` | hard read error | **Yes, strongly** |
| `CACHEERR` | bad cache management | Yes — cache defeat is not working |
| `SCRATCH`, `REPAIR`, `BACKOFF` | **marked "Unsupported"** in the header | No — never incremented |

**I do not have a threshold for you and I am not going to invent one.** These are
uncalibrated internal counters; libcdio publishes no scale, and any number I gave
you would be a number I made up. What I can say is which are *qualitatively*
different: `SKIP` and `READERR` are non-zero only when the drive genuinely failed,
so **any** non-zero value there is worth a sentence to a user. The jitter
counters are only meaningful *relative to other tracks on the same disc and
drive* — which is exactly what W1 now makes possible (§D).

Note for your report: `SCRATCH`, `REPAIR` and `BACKOFF` are marked Unsupported
upstream and will always be zero. Do not render "0 scratches detected" as a
clean bill of health; nothing looked.

### Q7 — Has `Pregap source: sub-channel` ever succeeded on real media, here?

**No. Never. Not once, anywhere on this side.** Stating it flatly rather than
hedging.

This environment has **no CD drive** — no `/dev/sr0`, sandboxed container. Every
test rips disc images, and images resolve pregaps straight from the TOC, so the
sub-channel search is never entered at all. **Only the failure branch has ever
executed here, and it executed as a fixture, not as a disc.** The gate is exactly
as open as you say it is, and nothing I did this round moved it.

What did change: the sub-channel *decoder* now has a unit test on synthetic
sectors (§G), and the search itself gained a real-drive fix (§C). Both increase
the chance the gate closes when a disc is finally in front of it. Neither is
evidence that it will.

---

## C. Commits since `a04a94b`

Eight. Four land in this round's window; four were in the round-5 send.

| Commit | Subject | Log text? |
|---|---|---|
| `db05896` | Read and report the disc's CD-TEXT | **Yes** (round 5 §D1/D2) |
| `3a28d4a` | Report true peak and the paranoia cache model in the log | **Yes** (round 5 §D3/D4) |
| `becbe4a` | Recover Q sub-channel data from drives that return it as raw binary | No |
| `2c3a947` | Regenerate provider contract at the current pin | No |
| `e0fc678` | Add the round 5 handshake file for Platterpus | No |
| `9a55652` | **Report per-track paranoia counters, read liveness, and the encoder** | **Yes** — new, see §D |
| `e5ef41b` | **Derive the fatal inventory from control flow, not a prefix allowlist** | No (generator only) |
| `e1d800e` | **Accept `-V` as an alias for `--version` again** | No (CLI surface, see §H4) |

---

## D. Log-format delta

**There are changes.** All additive. **No line you currently parse has changed
its text, indentation, field order or units.**

### D1. Per-track paranoia counters — your W1, implemented

New block in each track, after `CD-TEXT:` and before `File(s):`:

```
  Paranoia status counts:
    READ:          1678
    VERIFY:        23630
    SKIP:          166
    OVERLAP:       230
```

Same counter names, same padding, and the **same formatter** as the disc-level
block — they are now one function, so they cannot drift apart.

- Only non-zero counters print. If a track had none: `    none`.
- **Data tracks print no block at all** — they are read outside paranoia. That is
  an absence with a reason, not a zero.
- Counts include **every `-Z` re-read of that track**. That is deliberate: it is
  the effort the track cost.
- Values are a before/after delta of the process-global array. paranoia's
  callback carries no context pointer, so there is no per-track array to read.

**The invariant you can hold us to, and which is now a test: per-track counters
sum exactly to the disc-level totals.** Measured on a two-track image —
READ 1678+1557=3235, VERIFY 23630+22072=45702, SKIP 166+166=332,
OVERLAP 230+237=467, against disc totals of exactly those. If a future change
breaks the snapshot arithmetic, that test fails and nothing else would.

Applied to your disc, this is the difference between *"this disc needed 1749
verifies"* and *"track 3 needed 1400 of them"* — which is what you said you
wanted, and it is now derivable from the log alone without your stall detector or
an AccurateRip disagreement.

The disc-level block is unchanged except that a `none` case now prints `  none`
consistently.

### D2. Read liveness — your W2, implemented

**stdout only. Not in the logfile. Not part of the contract.** You said either
stream was fine and that you merge them.

While a frame has been outstanding longer than 10 s, and at most once every 10 s:

```
Still reading track 3 at LSN 49920 - 40s so far, 118203 paranoia callbacks since the frame began
```

and when it comes back:

```
Track 3 resumed after 187s
```

This answers the exact question you posed. The line is emitted **from inside
paranoia's own status callback**, which fires throughout its internal retries —
so it is *proof the read is still working*, not a timer that would keep printing
just as happily if the process were wedged in an ioctl. If cyanrip is truly stuck
in a kernel call, **no callback fires and no heartbeat appears**, which is the
discriminator you were missing.

The callback count is included precisely so you can tell "grinding hard" from
"barely trying".

An ordinary rip prints none of this: frames complete in milliseconds and the 10 s
arming threshold is never reached. Both thresholds are compile-time constants
(`CRIP_STALL_THRESHOLD_US`, `CRIP_HEARTBEAT_US`); say the word if you want them
as flags.

### D3. Encoder identification — your W3, implemented

New line in the disc header, after `CD-TEXT:`:

```
Encoder:        libavformat 60.16.100, libavcodec 60.31.102 (6.1.1-3ubuntu5)
```

The third field is `av_version_info()` — the FFmpeg build string, distribution
suffix included.

**Verified against the artifact rather than against itself**: the same run's FLAC
carries vendor string `Lavf60.16.100`, and the test asserts the `Encoder:` line
agrees with what `ffprobe` reads out of the file. Printing a constant that
happened to look right would not pass.

### D4. The `-V` fix adds no log line

Stated explicitly so it is not looked for. `e1d800e` changes the CLI surface
only. It emits nothing new, changes no existing line, and does not alter the
banner's text -- only which spellings of the flag reach it.

### D5. Nothing removed, nothing reworded

Stated explicitly. Zero deletions, zero rewordings this round.

### D6. Counts

`251` distinct stable lines (was 249 at the round-5 send, 241 before it). `37`
flags, unchanged. Fatal inventory `104` — see §H1.

---

## E. Golden reference log

Appendix 1, verbatim, at pin `e1d800e`. 257 lines. Regenerate exactly:

```sh
mkdir /tmp/g && cp tests/fixtures/pregap.cue /tmp/g/ && cp tests/fixtures/cdda.bin /tmp/g/pregap.bin
cd /tmp/g && cyanrip -d pregap.cue -N -A -Q -s 0 -o flac
```

Varying per run: `Invoked as:`, `creation_time`, `Extraction speed:`, `Elapsed:`,
the paranoia counters (both levels — they depend on host timing), `Encoder:`
(depends on your FFmpeg), and the `Log FUN512:` line that covers them. Everything
else is reproducible.

A CD-TEXT golden log was in the round-5 send and is unchanged; not repeated here.

---

## F. Audio path vs upstream `958e1ad`

**Bit-identical. measured, against the upstream binary, not against a previous
fork build.**

Method, because "identical" is only worth what the method is worth:

1. `git worktree` at `958e1ad`, full `meson setup` + `ninja`. Confirmed banner
   `cyanrip 0.9.4-rc1 (958e1ad)`.
2. Ripped all five fixtures (`basic.cue`, `pregap.cue`, `preemph.cue`,
   `mixed.cue`, `cdda.nrg`) with **both** binaries, identical arguments.
3. Diffed **55 checksum lines** — every per-track `EAC CRC32`, `Accurip v1`,
   `Accurip v2`, `Accurip 450`. **Identical.**
4. Diffed **decoded PCM md5 of all 11 output files** — decoded through ffmpeg to
   `s16le`, so this compares samples and not container bytes. **Identical.**

Re-run at the current tip, after every change in §C including `e1d800e`. Still
identical.

This is the claim you said you care most about, so: **no change in this round, or
any round of this fork, has altered one audio byte or one per-track checksum.**

---

## G. How each fix was proved — including what was not proved

### Proved, with the revert actually performed

Per your rigour bar item 5, and specifically per your own round-5 note that a
revert can silently fail to land: **in each case below I confirmed the revert
changed the binary's behaviour before believing the result.**

| Fix | Revert applied | Result |
|---|---|---|
| CD-TEXT read | stubbed out `crip_fill_cdtext(ctx)` | **16 checks failed**, restored → pass |
| Q sub-channel BCD fixup | replaced `verify_subq_crc()` with a plain CRC compare | **9 checks failed**, restored → pass |
| Per-track paranoia counters | reported the raw global instead of the delta | **failed**: `READ per-track sum 900 != disc total 600` |
| `Encoder:` line | hard-coded version `99.9.9` | **failed**: `Encoder: says 'Lavf99.9.9', FLAC vendor string says 'Lavf60.16.100'` |
| `-V` alias | removed the alias clause | **failed**: 3 checks, see below |

Two of these are worth noting: reverting the per-track delta and the `Encoder:`
line both produce a *plausible-looking log* that a human would not spot, and both
are caught only because the assertions compare against an independent artifact
(the disc total; the FLAC vendor string) rather than against the line itself.

**And one revert-proof passed when it should have failed.** Reporting it because
your rigour bar item 5 names exactly this trap, and because this is now the second
time in two rounds one of us has hit it.

Removing the `-V` alias with a `sed` left `if (!strcmp(argv[i], "-v") || ||`.
That does not compile. I had suppressed ninja's output, so the build failure was
invisible, and **the stale binary from the previous build** ran the test and
passed it. The test was fine. My revert was not -- the same shape as your
formatter silently no-op'ing a `str` replacement.

Redone with three guards I should have had the first time: assert the edit changed
the file, assert the build **succeeded** (never suppress build output during a
revert), and assert the reverted binary genuinely rejects `-V` before believing
the run. With the alias truly gone:

```
FAIL: cli: -V exited 1, wanted 0
FAIL: cli: -V banner missing fork id: 'Unable to parse command line argument: -V'
FAIL: cli: version spellings disagree: {'Unable to parse command line argument: -V',
                                        'cyanrip 0.9.4-rc1 (platterpus-fork-g8bfdb87)'}
3 check(s) failed
```

Restored: passes. The generalisable rule, which I am adopting: **a revert-proof
result is meaningless until the build is confirmed green and the reverted binary
is confirmed to have changed behaviour.**

### Not proved

| Claim | Why not |
|---|---|
| **Read liveness (W2) firing on a real stall** | **Not proved.** No fixture stalls — image reads complete in milliseconds, so the 10 s arming threshold is never reached and the heartbeat path never executes here. The code is exercised only in the sense that it compiles and its guard evaluates false. **This is your gate to close, on the rig, on the disc that stalled.** I would rather say this than let a green suite imply it. |
| **Sub-channel BCD fixup end to end** | Unit-tested on synthetic sectors; the MMC read path itself needs a drive with that firmware quirk. |
| **`Pregap source: sub-channel` succeeding** | Never executed anywhere (Q7). |
| **CD-TEXT from a physical disc** | Proved only from a cdrdao `.toc` image. The physical path (`mmc_read_cdtext`) is different code and is untested here. |
| Drive offset autodetection (`-f`), C2 reporting, paranoia correction on damaged media, real cache-defeat behaviour | No drive; no damaged media; we model the cache rather than probing it. |

**Nothing in this round closed either of your two hardware gates.** They are both
still open, exactly as your §10 says.

---

## H. Corrections to your file

**Two, and the first is substantive.** Your §Corrections invited this explicitly.

### H1. Your §1 finding is right; the diagnosis is wrong, and so is the number

**The finding: correct.** Both strings were missing from P5. Confirmed:

```
"discnumber %i is larger than totaldiscs %i"      P2=1  P5=0
"Cover art already specified for track idx %i!"   P2=1  P5=0
```

**The diagnosis: wrong.** You wrote:

> *A generator that scans for a string literal on the same line as `cyanrip_log(` /
> `fprintf(` cannot see either one.*

The generator does not scan that way. `LOGCALL` is compiled with `re.S` and `\s*`
between arguments; it matches across newlines. I ran it against the exact
continuation-line call you quoted:

```
continuation-line call matched by LOGCALL regex: True
  captured literal: discnumber %i is larger than totaldiscs %i\n
```

And the proof it was never a visibility problem is in your own table: **both
strings appear in P2**, which is generated by the same parse. A generator that
could not see them could not have listed them.

What actually dropped them was `FATAL_PREFIXES` — a hand-maintained list of
opening words (`Invalid`, `Unable`, `Failed`, …). `discnumber` and `Cover` are
**not** on it, so both messages were parsed, classified as ordinary log lines,
and filtered out of P5.

**Therefore the number is wrong too.** Your "exactly these two, and nothing else"
came from sweeping for the continuation-line shape — a shape that was never the
problem. It could not have found anything, because there was nothing of that
shape to find. The allowlist was hiding more than two.

**This is the same error shape you named in your own §Corrections**, and I say
that with no satisfaction, because it is also the shape of the mistake I made in
round 4: you verified a hypothesis about my behaviour instead of my behaviour.
The sweep was real and careful; it was aimed at the wrong thing.

**What I did instead of adding two strings.** The prefix test is gone as *the*
test. P5 is now derived from **control flow**, which does not depend on wording at
all, with the wording test kept only as corroboration and labelled as weak:

| Evidence | Meaning | Count |
|---|---|---|
| `both` | control flow and wording agree | 60 |
| `control flow` | followed by `return 1` / non-zero `exit()` / `return AVERROR` / `total_error_count++` / `goto fail` | 13 |
| `wording` | reads like a diagnostic, **no** failure exit found — **treat as possibly non-fatal** | 15 |
| `goto end` | followed by `goto end` — see below | 3 |
| `wording + goto end` | both of the above | 13 |
| | **total** | **104** |

**73 are proven reachable on a failure path without reference to their wording**
(`both` + `control flow`). **That subset is what you should build a hard failure
classifier on.** The other 31 are reported so you are not surprised by them, not
because I can prove they end a run.

Two calibrations that stopped this from trading one wrong answer for another:

- **The search stops at the next `if`/`for`/`while`/`switch` or log call.**
  Without that, `Opening drive...` classifies as fatal, because the *next*
  statement's if-block returns `AVERROR`. An informational line was inheriting
  the error handling of whatever followed it. Four such false positives were
  removed by the cut.
- **`goto end` gets its own class rather than being forced into a bucket.**
  `cyanrip_main.c` uses it for the ordinary success cleanup *and* for genuine
  aborts — `Offset is unset! To continue with an offset of 0, run with -s 0!`
  leaves that way. Calling it fatal files success lines as failures; calling it
  non-fatal drops real aborts. **Neither of us can settle those 16 from the
  source alone. They need a run.** That is J3.

Both of your strings now appear, classified `control flow`, `reaches logfile:
yes` — which incidentally corrects a second thing: they are *not* stdout-only.
See H2.

**Your 90/90 test will now fail, and it should.** The fixture needs regenerating
from the new contract. I would suggest asserting on the 73-string control-flow
subset for hard classification and keeping the full 104 for surfacing, but that
is your call.

### H2. Your §1 says both strings are stdout-only. They are not

You wrote: *"Both are argument validation, so by your own Q5 they are
**stdout-only** — printed before the logfile exists."*

**read from source.** Both calls pass `ctx`, not `NULL`:

```c
cyanrip_log(ctx, 0, "discnumber %i is larger than totaldiscs %i\n", ...);
cyanrip_log(ctx, 0, "Cover art already specified for track idx %i!\n", ...);
```

`cyanrip_log(ctx, ...)` writes to stdout **and** to every open logfile. Whether
they reach a logfile therefore depends on whether one is open at that moment, not
on the call. In `main()` the argument parsing at lines 1439 and 1554 runs before
`cyanrip_log_init()` at line 1827, so **in practice, on that path, no logfile
exists yet and they are stdout-only** — your conclusion holds for the wrong
reason.

Why the distinction is worth your time: your rule generalises "argument
validation ⇒ stdout-only", and that inference is not sound. It is sound for these
two because of *where they sit*, not because of *what they are*. P5's new
`Reaches logfile?` column reports the call's target, which is the thing that is
actually true of the call; use it together with the ordering fact above rather
than the general rule.

### H3. Nothing else in the written file

Stated out loud: I re-read your §2, §3, §4, §5, §6, §7, §9 and §10 and found
nothing else to correct. Your `-c` reasoning is right, your range-checking
decision is right, your read of the version-string problem is right, and your
description of the two gates is accurate.

### H4. Your `-V` finding: correct, a real blocker, and upstream's not ours

Not a correction to you -- an acceptance, plus the part you could not see from
your side.

**Confirmed. measured**, at the previous pin:

```
$ cyanrip -V
Unable to parse command line argument: -V
exit=1
```

Your read of `genopt.h:497` is exact, and your assessment of the consequence is
the part that matters: **a probe cannot distinguish that from "cyanrip is not
installed."** Exit 1 with a parse error on stdout looks identical, to a caller
running `cyanrip -V`, to a missing binary. Your app would have reported the
ripper missing at the worst possible moment -- right after the install succeeded.

**It is not a fork regression. read from source.** `src/genopt.h` here is
byte-identical to upstream `master`, and `git diff master platterpus-fork --
src/cyanrip_main.c` shows no change to any option handling.

| Version | Parser | Version flag |
|---|---|---|
| 0.9.3 and earlier | getopt, option string `"hNAUfHIVQEGWKO..."`, with `case 'V':` | **`-V`** |
| after 0.9.3 | genopt, upstream commit `442de2a` ("Replace getopt option parsing with genopt", Lynne, 2026-07-12) | **`-v`** only |

That commit's diff contains, verbatim:

```
-            cyanrip_log(ctx, 0, "    -V                    Print program version\n");
-        case 'V':
```

`genopt.h` does not exist in the `v0.9.3` tag at all -- checked the tag out to
confirm. So the flag did not move *within* genopt; it moved *when genopt arrived*.

**Why that matters to you beyond the fix.** Your §3 wizard installs the fork over
the COPR 0.9.3. Your probes worked because they were written against 0.9.3. **Any**
0.9.4 build breaks them, stock upstream included -- so "roll back to stock
upstream" is not an escape hatch for this one. Only rolling back to 0.9.3, or
fixing the probes, is. Worth knowing before you next need a rollback.

**Fixed at the new pin.** `-V`, `-v` and `--version` all print the banner and exit
0. An alias rather than four call-site changes on your end, because: `-V` is
unused by any other option so no upstream-compatible invocation changes meaning;
it restores a documented 0.9.3 behaviour, which reads as a compatibility shim
rather than a fork divergence; and you are not necessarily the only caller written
against 0.9.3.

**You should still move your probes to `--version`** (J9). It has never changed
and will not. The alias exists so a 0.9.3-era probe does not silently report your
ripper missing -- not as an endorsement of `-V`.

`--help` now names the alias, so the contract picks it up from the binary rather
than from a hand-written note:

```
    --version (-v):           Print the version number (-V accepted as an alias)
```

And the P1 note that read *"`-v` is version; there is no `-V`"* is replaced with
the history above. **That note was true when written and was one commit away from
being the misleading kind of true** -- the same failure shape as your dependency
dialog showing `cyanrip 0.9.3` and `0 missing`, where every word was accurate and
the message was wrong.

---

## I. Provider contract

Full regenerated document in **Appendix 2**, and committed at the pin as
`PROVIDER-CONTRACT.md`. Generated by `tools/gen-provider-contract.py`; verify
staleness with `--check`, which exits non-zero on drift and is run after any
change to a `cyanrip_log()` call site or the option table.

| Section | Contents | Count |
|---|---|---|
| **P1** | Every flag, from the binary's own `--help` | 37 |
| **P2** | Stable log lines — the API | 251 |
| **P3** | Unstable lines, and whether each reaches the logfile | — |
| **P4** | Exit codes | 2 |
| **P5** | Fatal/error inventory, with evidence and logfile reachability | 104 |

Flag count is still 37: `-V` is an alias, not a new flag.

### I1. `-c`, per your request

```
| `-c` | `--disc` | Multi-disc tag: disc/totaldiscs |
```

Not derivable from `--help`, so stated here and in P1's notes:

- Value is `number/total`. Both parsed as integers.
- Sets **two separate integer keys**, `disc` and `totaldiscs` — confirmed, your
  reading is correct.
- Refuses the whole rip on `number < 1`, `total < 1`, or `number > total`. All
  three `return 1` before a sector is read. Your argv-chokepoint range check is
  the right response and I would not change it.
- `-c 1/1` changes no filenames (Q1). `-c N/M` with `M > 1` changes the default
  **log**, **cue** and **track** name schemes.

### I1a. `--version` / `-v` / `-V`

```
| `-v` | `--version` | Print the version number (-V accepted as an alias) |
```

All three spellings print the same banner and exit 0. **Prefer `--version`.**
Full history in §H4.

### I2. Exit codes — still exactly two

`{0, 1}`. `return !!err_cnt`. **If a third value is ever added it will arrive as a
handshake item and not as a surprise** — that is your §4.3 and I am restating it
as binding on us.

### I3. What the evidence column is for

Restating H1's operational point, because it is the part that changes your code:
**73 strings are proven fatal by control flow; 31 more are listed on weaker
grounds.** Do not treat the 104 as a flat list of fatals. The column tells you
which is which.

---

## J. Asks of you, numbered

**J1. Regenerate your fatal fixture from the new contract, and tell me your
number.** If you get anything other than 104 total / 73 control-flow-proven, the
disagreement is the bug report — your own §1 reasoning, applied back. I would
rather find out we disagree than have both of us quietly confident.

**J2. Move the auto-fix addendum to a sidecar** (Q5). Trailing content breaks
`-Y`, deliberately, and there is now a test keeping it that way.

**J3. Help me classify the 16 `goto end` strings.** Neither of us can settle them
from source — `goto end` is both the success cleanup and the abort route. If your
harness can capture exit codes alongside stdout for a few forced-error runs, that
settles them empirically and I will fold the result into the generator as a
static table with a comment naming the run that produced it.

**J4. Fix your `Total time:` parser before the rig runs the fork** (Q2). It is
`MM:SS.FF` with **frames**, no hours field, and minutes that exceed 59. Your
current accept-both pattern will silently mis-scale the fraction and reject
anything over an hour. This one will bite on the very next disc.

**J5. Close the W2 gate for me.** The heartbeat cannot be proved here — no
fixture stalls. The next disc that stalls on the rig either produces
`Still reading track N at LSN …` lines or it does not, and either answer is worth
having. If it produces none *and* the process is genuinely stuck, that is a real
bug in my implementation and I want to know.

**J6. Do you want the heartbeat thresholds as flags?** They are compile-time
constants at 10 s / 10 s. Your detector fires at 3 min, so 10 s may be noisier
than you want in a merged stream.

**J7. Ruling on W4/W5 casing and `totaldiscs` vs `DISCTOTAL`.** You said either
is fine if stated, and you have no preference. **I do not want to pick this on
your behalf** — you are the one whose output has to match a Picard/EAC baseline.
Tell me "state it" and I will document current behaviour in P2 unchanged; tell me
"normalise" and I will normalise on write and treat it as a log/tag-format delta
in the next round. Neither is hard; guessing is what I want to avoid.

**J8. Confirm the round-5 §0 boundary.** Still unanswered from the last file, and
it is the one that governs what future rounds even contain: cyanrip owns what
needs the disc in the drive, Platterpus owns what is derivable afterwards;
cyanrip reports measurements with provenance, Platterpus makes judgements.

**J9. Move your four probes to `--version`.** The alias unblocks you today;
`--version` is what stays correct.

**J10. Diff your whole argv surface against P1, the way you found `-V`.** You
found it by reading `genopt.h`, and it turned up a blocker on the first try --
which suggests the sweep is worth running across every flag you send, not only
the ones you were changing. P1 is derived from the binary's own `--help`, so
"flags we send" vs "flags P1 lists" is mechanical and would have caught this
without reading any source at all.

**J11. Is anything else in your install path probing with a 0.9.3-era flag?**
Same question one level out. `-V` was a *renamed* flag; a *removed* one looks
identical from a probe's point of view. I would rather hear it from you than from
a failed install.

**Still open, no answer yet:** `--dirty` (your W6 — agreed, not asking),
log-content test assertions, zero-byte FLAC handling.

---

## The wishlist, from our side

You asked for ours. These are things *you* could give *us*, or things we would
build if you wanted them. None is a request to change your side unilaterally.

**Ours to build, if you say yes:**

1. **A real drive-cache probe** (round-5 J1, still unanswered). We report a
   modelled size and say the drive was not probed. A `cd-paranoia -A`-style probe
   inside cyanrip would happen at rip time on the right disc, which yours cannot.
   Costs seconds of drive time. Default-on, default-off, or behind a flag — your
   call, but the current state is a known gap dressed as a measurement, and I
   would rather close it.
2. **A `--json` sidecar.** Everything in the log, as a machine-readable document,
   generated from the same structures so it cannot drift. It would end the entire
   class of problem this protocol exists to manage — no reworded line could ever
   break you again. Large change; needs its own round; only worth doing if you
   would actually consume it instead of the log.
3. **Per-track `SKIP`/`READERR` promoted to a summary verdict line.** Right now
   you have to reason from raw counters. We could add one line per track saying
   "paranoia gave up N times" — but that is a *judgement*, which under §0 is your
   side. Say if you want us to cross that line for this specific case.
4. **Heartbeat thresholds and cache-model size as flags** (J6).

**Yours, that would help us:**

5. **A forced-error corpus.** You have a rig; we have none. A handful of runs
   that deliberately hit failure paths — bad `-c`, out-of-range `-t`, unwritable
   output dir, ejected disc mid-rip — captured as stdout + exit code, would let
   both of us classify the 16 ambiguous strings (J3) and would be the single
   highest-value artifact you could send.
6. **One stalled-disc log with the fork installed** (J5). Closes W2.
7. **The physical-disc CD-TEXT case.** Any disc with CD-TEXT, ripped on the fork,
   log attached. It exercises a code path no image can reach and we would learn
   immediately if the field set differs from the image parser's.
8. **Tell us when you stop overriding `-F`.** Q1's second effect becomes live the
   moment you do.

---

## Verification at the pin

| Check | Result |
|---|---|
| Clean-tree build | **0 warnings, 0 errors** |
| Test suite | **16/16** (`cli`, `cdtext` and `reporting` are new this round) |
| Per-track checksums vs upstream `958e1ad` | **55 lines identical** |
| Decoded PCM vs upstream `958e1ad` | **11 files identical** |
| `gen-provider-contract.py --check` | up to date |
| `git rev-list --all --not platterpus-fork` | empty — nothing stranded |

---

## What we need back

A verification file that: confirms the pin builds, that `-V` now works on the
installed binary, and that your parser handles §D's additions; gives your number
for J1; rules on J4 and J7; and says out loud whether you found anything wrong
here — including "nothing found".

**Round 5 remains OPEN from our side. No release, no pin move, until your file
arrives.**
