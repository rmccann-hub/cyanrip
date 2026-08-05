# cyanrip beta — `0.9.4-rc1+platterpus.5-beta.4`

*Information only. This file describes the beta and what to test in it, and
nothing else.*

---

## Identifiers

```
version   0.9.4-rc1+platterpus.5-beta.4
repo      rmccann-hub/cyanrip
branch    platterpus-fork
build     c36ad65      <- check this out
tests     30/30
anchor    sha256/16 = da96b1223b0e182b   (over src/*.c and src/*.h)
contract  PROVIDER-CONTRACT.md in that tree, and it describes that tree
```

**`f5e11ba` was named as the pin in an earlier draft of this file. Do not use
it** — read the box below. The *binary* is the same either way; the
`PROVIDER-CONTRACT.md` beside it is not.

**Why the pin is not the commit that bumped the version, and why this file names
a commit that is not its own.** A file cannot contain the hash of a commit
containing it, so this note lands as `c36ad65`'s child. That child changes no
source file and no handshake state, so the binary built from either is the same
program — only the SHA in the banner differs, and this note's own contents.

**The commit is the identifier.** There is no git tag and no GitHub release: the
git proxy in the build environment refuses tag pushes (`HTTP 403`,
`git ls-remote --tags origin` returns nothing) and no release-creation API is
reachable from it.

> **The pin is not the commit that bumped the version, and that is deliberate.**
> `tools/gen-provider-contract.py` reads the *built binary* and refuses on a
> dirty tree, so the contract can never be regenerated in the same commit as a
> version bump — the bump must be committed before a clean build exists to
> derive from. **Every release this fork has cut carried a contract describing
> the previous version:**
>
> ```
> c5fb909   meson.build beta.2   PROVIDER-CONTRACT.md says beta.1
> e61e75a   meson.build beta.3   PROVIDER-CONTRACT.md says beta.2
> f5e11ba   meson.build beta.4   PROVIDER-CONTRACT.md says beta.3
> ```
>
> Earlier notes published `PROVIDER-CONTRACT.md @ <release commit>`, so a
> consumer following them got the wrong anchor, the pre-change coverart string
> and six wrong `cyanrip_log.c` line numbers. **The pin above is the artifacts
> commit**, where `gen-provider-contract.py --check` exits 0 and the contract
> describes the binary you just built. `tests/rip_images.py contract_build`
> now fails on any tree where the two disagree — run against `f5e11ba` it fails
> with the message above.

**This is a pre-release.** It claims no joint verification, and says so in every
logfile it writes. Round 7 is open and both projects declare HOLD.

**It supersedes `…-beta.3` (`e61e75a`) and `…-beta.2` (`c5fb909`) as the build
to install — but read the next section before assuming the rig evidence carries
over. Unlike `beta.3`, this build is *not* observably identical to the one the
rig tested.**

## Build and verify

```sh
git clone <repo> && cd cyanrip
git checkout c36ad65
meson setup build && ninja -C build
meson test -C build --print-errorlogs
./build/src/cyanrip --version
python3 tools/gen-provider-contract.py --check PROVIDER-CONTRACT.md
```

Expected:

```
30/30 tests passing
cyanrip 0.9.4-rc1+platterpus.5-beta.4 (platterpus-fork-gc36ad65)
PROVIDER-CONTRACT.md is up to date
```

30, not 28: `contract_build` and the audio-checksum mirror's `self-test` are
new.

A banner ending `-dirty` means the tree had uncommitted changes and the commit
does not describe the binary.

**If you ran the previous beta's suite and saw 27/28, that was a defect in our
test harness and not in your setup.** `version_matrix` resolved upstream
`master` as a local branch, and `git clone` creates a local branch only for the
remote's HEAD — which is `platterpus-fork` — so a fresh clone had
`origin/master` and no `master`, and the check failed with *"master is
unreachable"*. It passed in our working tree, which happens to carry the
branch, so `beta.3`'s note claimed 28/28 from a clean checkout and that was not
true for anyone who cloned. Fixed here, and this beta's 28/28 was verified in a
fresh clone rather than in the tree that built it.

## Two artifacts in that tree describe an earlier commit, on purpose

Both are labelled here so neither reads as drift:

| artifact | describes | why it cannot describe the pin |
|---|---|---|
| `PROVIDER-CONTRACT.md` | **the pin** | nothing — it is correct, and that is the point of pinning `c36ad65` rather than `f5e11ba` |
| `docs/golden-reference.log` and its `.diagnostics.json` | build `f5e11ba` (banner says so) | a log contains the build tag of the binary that wrote it, so it can never sit inside that build's own commit |
| this note | build `c36ad65` | same reason: it names a commit, so it lands as that commit's child |

**`f5e11ba` and `c36ad65` differ in two observable ways and no others.**
`git diff f5e11ba..c36ad65 -- src/ meson.build` is empty, so the ripping code is
identical — but the `Handshake:` line is compiled in from `docs/handshake/`, and
lap 25 does not exist at `f5e11ba`. So:

```
f5e11ba   banner …-gf5e11ba    Handshake: round 7 lap 24 OPEN, verdict HOLD
c36ad65   banner …-gc36ad65    Handshake: round 7 lap 25 OPEN, verdict HOLD
```

A draft of this paragraph said the handshake state was the same. It is not, and
the check that caught it was running `git show f5e11ba:docs/handshake/round-07-lap-25.md`
rather than reasoning about what a doc-only commit can change.

## What changed, and it is exactly two log lines

Both were raised as non-blocking notes and both were carried as known
imprecision. They are **proposals shipped in a beta so they can be run**, and
either can be withdrawn.

`git diff e61e75a..f5e11ba -- src/` touches two files and nothing else.

### 1. Cover art — the line now names which release ID, and when

```diff
- Release ID unavailable, cannot search Cover Art DB!
+ No MusicBrainz release ID at cover art lookup, cannot search Cover Art DB!
```

The old line and the header's `Release ID: <uuid>` appear in the same log and
read as a contradiction. Both are true, and the ordering is worth stating
exactly because both projects have described it loosely:

- **Chronologically the refusal comes first.** `-R` and a user
  `-a musicbrainz_albumid=` are merged into the metadata **after**
  `crip_fill_coverart()` runs, so cyanrip genuinely had no ID of its own at
  that moment.
- **Positionally it comes second.** `crip_early_flush()` is the last statement
  of `cyanrip_log_start_report()` (`src/cyanrip_log.c:662`), so the replayed
  pre-log block is written *after* the header — in `docs/golden-reference.log`
  the header ends at line 27 and the replay runs 29–34.

So a parser reading top to bottom meets the `Release ID:` header first and the
refusal after it, which is the opposite of the order in which they happened.
The new line states what was observed rather than the stronger claim that the
release has no ID.

**The trailing `cannot search Cover Art DB!` is unchanged**, so a substring
match on the tail still works. An exact-string match does not.

### 2. AccurateRip — both tally lines now divide by the disc

```diff
  Tracks ripped accurately: 13/14
- Tracks ripped partially accurately: 1/1
+ Tracks ripped partially accurately: 1/14
```

The partial line divided by *tracks not fully verified* while the line above it
divides by the disc's track count, so `1/1` was a denominator derived from the
first line's result and the pair read as one tally over-reports. Both now
divide by the track count.

**The numerators are unchanged, and so is which track falls in which bucket.**
Same disc, same verdict, different denominator.

**This one changes a number, not only text.** The archived rig log
(`docs/rig-2026-08-04/cyanrip.log`, build `9003e6f`) has exactly this pair at
lines 1130-1131 against `Disc tracks: 14` on line 23. A stored `1/1` from that
disc becomes `1/14`.

## What to test

### Highest value, cheapest, and specific to this beta

**Re-rip the baseline disc (The Police, *Every Breath You Take: The Classics*,
14 tracks, MusicBrainz DiscID `pNtImOkdBm9RMBIalzx0w9cfsYY-`, CDDB ID
`E20DFE0E`) on `c36ad65` and diff the log against the one you already have.**

> **Which log?** Two rig sessions ran on 2026-08-04 — `9003e6f` (beta.1) and
> `c5fb909` (beta.2) — and our documents had been calling both "the 2026-08-04
> session". Diff against the **`c5fb909`** one: beta.1 predates the pre-log
> replay block and has no `Read stalls:` line, so half the table below has
> nothing to compare against in it.

**Diff it, but do not expect it to be nearly identical.** An earlier draft of
this file gave a short "everything must match except" table and told you that
anything else moving was a finding. That table was derived from
`docs/golden-reference.log` — a 3-track *image* rip with `-N -A -P 0`, which has
no AccurateRip block, no paranoia activity and one version string. **A reference
that does not contain the varying lines cannot tell you which lines vary.** The
list below is derived from `docs/rig-2026-08-04/cyanrip.log`, a real 14-track
disc rip, and it is longer.

**Expected to differ, by cause:**

| cause | lines |
|---|---|
| **build identity** | the banner **and every per-track `comment:` tag** — the version string appears **15 times** in a real log, not once (`grep -c` on the rig log), plus `Handshake:` (this build says `round 7 lap 25`) |
| **invocation** | `Invoked as:`, `Consumer:` |
| **read timing** | `Extraction speed:`, `Elapsed:`, `Ripping finished at`, and `Read stalls:` if a read ever stalls |
| **read behaviour** | **every `Paranoia status counts:` block** — the rig log has 15 of them and they carry real activity (`FIXUP_ATOM: 4` on track 5). These are a measurement of that read, not of the disc, and two rips of one disc need not agree |
| **the AccurateRip database, not us** | `confidence N` on every `Accurip v1`/`v2` line, `max confidence:`, and therefore possibly `Tracks ripped accurately: N/M` if a track crosses the threshold between rips. The rig log shows `confidence 129`/`200`; those accumulate over time |
| **this beta's two changes** | §1 and §2 |
| **follows from all of the above** | `Log FUN512:` |

**What should be identical:** the TOC and disc identity (`DiscID`, `CDDB ID`,
`Disc tracks:`, `Total time:`), every pre-gap line, every `Pregap source:`, the
drive and offset block, and **every checksum over the audio** — `CRC32`,
`EAC CRC32`, `Accurip v1`/`v2` (the checksums, not their confidences).

**A checksum that moves is a finding. Anything in the table above is not.**

The second line is the one that matters most: **it has never executed
anywhere.** The block needs an AccurateRip database hit, the lookup fetches over
the network with no local-file input, and the synthetic test discs are not in
the database — measured, a fixture rip with lookups enabled reports
`AccurateRip:    not found` and prints no tally at all. Your baseline disc is
the only place this can be verified.

### Check the files against the log, not just log against log

`tools/audio-checksums.py` is new in this beta. It reimplements
`src/checksums.h` in Python, so any audio file can be checked against any
cyanrip log without the disc:

```sh
tools/audio-checksums.py check track05.flac --log cyanrip.log --track 5
tools/audio-checksums.py diff  ours.flac theirs.flac      # localise to the sector
tools/audio-checksums.py self-test                        # it has not drifted
```

Run over three tracks of the EAC baseline it reproduced the rig log exactly for
tracks 1 and 7, and for track 5 produced `E0036697` — the value the auto-fix
supersede recorded, not the `6902BCF0` in the log. **Both are right**: the log
describes the read that was thrown away. Worth knowing before you diff a
directory against a log and conclude something is corrupt.

### Everything else, unchanged from the previous beta

Nothing else in this build is new, so the standing list still stands. **In the
order it was asked for**, which is by cost-to-close and not by size of gap — the
gap inventory in `docs/AUDIT-2026-08-05.md` §3 is ordered differently on
purpose, and this file previously mixed the two:

1. **`-x` on one throwaway rip.** Never executed on a real drive, anywhere,
   ever — the largest single gap in the project, and the cheapest to close. It
   now reports a stall if it wedges rather than hanging silently, which is why
   asking is reasonable. **A hang is also a result** — send it either way.
2. **`-j <path>` on any one run.** The diagnostics record has only ever been
   written by image rips. Off by default and changes nothing else. Worth
   cross-checking `read_stalls` and `rip.track_state` against the same facts in
   the log.
3. **A deliberate abort** — eject mid-rip, or fill the write target. The
   diagnosed-abort exit code has never fired on hardware; the rig rip had
   `Ripping errors: 0`.
4. **Marginal media plus `-k 1`.** A non-zero `Read stalls:` count has never
   been produced anywhere. The `none` form is hardware-confirmed **by your
   report, not by anything in this repository** — the rig log archived here is
   the `9003e6f` session and has no `Read stalls:` line at all; the only record
   is `docs/rig-2026-08-04-c5fb909/platterpus-results.md:78`, and that session's
   cyanrip log is not held. The populated forms are unit-tested against the
   formatter and no drive has ever emitted one.
5. **CD-TEXT from a disc that has some**, opportunistically. A physical disc's
   CD-TEXT goes through `mmc_read_cdtext`, a different code path from the
   `.toc` image parser the suite uses.

**Not asked for:** `-f` offset autodetection, another EAC parity run, or
re-testing anything the 2026-08-04 session already closed. `-f` remains unrun
and is listed as a gap in the audit, but it is not worth a rig slot.

### One thing to know before relying on `PROVIDER-CONTRACT.md`

**A change to a number's meaning is indistinguishable, in the contract, from a
comment being added.** That is the finding, and it took two wrong drafts to
state correctly.

Measured, by reverting the denominator **alone** on a clean build and
regenerating: the entire diff is the source anchor —
`da96b1223b0e182b` → `41317a8af0d9bd9e` — and every P2 row is byte-identical,
because P2 derives each entry from the *format string* and §2 changed an
argument.

But change §2 **as shipped** (`d1d8312`) also carries a seven-line comment
explaining it, and that moves six `cyanrip_log.c` rows: 686→693, 688→695,
698→705, 707→714, 710→717, 713→720. §1 moves a seventh, `coverart.c:360→368`,
and is the only row whose **text** changes.

So the contract does not go quiet — it emits a line-number shift. **It emits
exactly the same line-number shift for a comment, a blank line, or a
refactor.** A consumer diffing two contracts sees six rows move and cannot tell
whether a denominator changed or someone documented it.

Two earlier drafts of this paragraph were wrong in opposite directions: the
first said `--check` exits 0 across the change (it does not — the anchor moves),
the second said not one row of the body changes (six do, once the comment is
counted).

Deliberately not patched: a half-working argument extractor would put wrong text
into a document that presents itself as derived. Proposed as round 8 work with
the cost stated.

## What every logfile from this build contains

```
cyanrip 0.9.4-rc1+platterpus.5-beta.4 (platterpus-fork-gc36ad65)
Invoked as:     …
Handshake:      round 7 lap 25 OPEN, verdict HOLD -- NOT a released build
Consumer:       <whatever --consumer was given>
                (reported by the caller, not verified by cyanrip)
```

`Handshake:` is derived from `docs/handshake/` at build time, so it reports the
newest lap the *tree* contains — `lap 25` at `c36ad65`. Building `f5e11ba`
instead reports `lap 24`, which is not a discrepancy: lap 25 did not exist yet.
`Consumer:` is whatever you pass to `-u`, recorded verbatim and explicitly not
verified.

## Flags relevant to this build

| flag | |
|---|---|
| `-u` / `--consumer <string>` | recorded verbatim in the log, explicitly not verified |
| `-j` / `--diagnostics <path>` | machine-readable JSON record; off unless given |
| `-k` / `--stall-secs <seconds>` | seconds a frame read must stall before liveness is reported (default 10, `0` disables) |
| `-x` / `--cache-probe` | measure the drive's readback cache before ripping; refuses on a disc image. **Never executed on real hardware** |

Flag count: 41. Full generated interface in `PROVIDER-CONTRACT.md` **in the
`c36ad65` tree** — not in `f5e11ba`'s, which carries `beta.3`'s.

## What this build still cannot claim

Full list with the cost to close each: `docs/AUDIT-2026-08-05.md` §3.

- **The two changed lines have not run on a drive**, and §2 has not run
  anywhere at all.
- **`-x` has never produced a measurement on a real drive.**
- **A non-zero `Read stalls:` count has never been produced anywhere**, and the
  `none` form is confirmed only by Platterpus's report of the `c5fb909` session,
  whose cyanrip log this repository does not hold. A silent watchdog is not a
  working watchdog — zero heartbeats on healthy media is the expected result and
  is not evidence either way.
- **The diagnosed-abort exit code has never fired on hardware.**
- **`-j` has never been written by a rip from a physical drive.**
- **`-f` and CD-TEXT from a disc that has some** remain unrun.
- **The track-1 pre-gap fix has never fired on a real TOC** — and that is the
  whole of what is missing, because **the image case is already closed**.
  `tests/fixtures/pregap.cue` declares a track-1 HTOA and
  `docs/golden-reference.log:77-80` shows the fix working on it:
  `Pregap LSN: 0`, `Pregap length: 150 frames`, `Pregap source: TOC`,
  `Start LSN: 150`. An earlier draft of this file called a disc image "the
  cheapest route left", presenting a closed route as the open one; the audit
  (§3.7) had it right and this file contradicted it.

  What remains is a *physical* disc whose TOC declares the pre-gap, and there
  may not be one to hand: *Platterpus measured* 40+ `Pregap source:` lines
  across three days of rips and **zero** say `TOC` — their measurement, stated
  as theirs. The one rig log archived here has 14 such lines, 13 `sub-channel`
  and 1 `lead-in`. **This is a measured "no candidate exists", not "untested".**
