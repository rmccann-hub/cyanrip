# Pregap-LSN detection: carried from upstream PR #115, with fixes

## What this is

`src/pregap.c`/`src/pregap.h` and the two call-site changes in `src/cyanrip_main.c` and
`src/cyanrip_log.c` are carried from upstream pull request
[cyanreg/cyanrip#115](https://github.com/cyanreg/cyanrip/pull/115), "Add pregap detection
for physical CDs", by **UltraFuzzy**. That PR is still open/unmerged upstream — checked
2026-09-16 against `master` at `f8ebf48`, where `src/pregap.c` does not exist, and
carried as a row in `docs/SETTLED.md` so the absence is re-checked rather than
re-read. It first said *"as of 2026-07-31"* and nothing would have noticed it
merging. This is a fork-local carry, not an independent reimplementation -- the
detection algorithm, its comments, and its design are UltraFuzzy's. Three bugs found during
review were fixed before integrating (below); everything else is unchanged from the PR.

**Scope, and how this differs from the fork's existing pregap support.** This fork already
had full `INDEX 00`/`PREGAP` cue-sheet *reporting* before this change (via separate,
already-merged upstream PRs #104/#118/#122) -- that part needed nothing from PR #115. What
was missing, and what this adds, is pregap *detection* accuracy: cyanrip previously only
trusted the disc's TOC (`cdio_get_track_pregap_lsn()`) to say where a pregap starts. Some
discs' TOCs don't declare a pregap that physically exists, which is exactly the gap EAC's
own gap-detection pass closes and cyanrip's TOC-only approach didn't. PR #115 closes it by
falling back to reading Q sub-channel data directly via MMC `READ CD` (or, on macOS, an
IOKit ioctl) and binary-searching for the boundary between the previous track's audio and
the pregap.

## Bugs found in PR #115 during audit, and the fixes applied

All three were confirmed either by reading the exact constant values involved or by direct
reproduction, not just inferred from reading the diff.

### 1. Wrong failure sentinel (confirmed via header values, not assumed)

The original code's final line was:

```c
lsn = (left_bound + 1 == right_bound) ? right_bound : DRIVER_OP_ERROR;
```

`DRIVER_OP_ERROR` is `-1` (`/usr/include/cdio/device.h`). `CDIO_INVALID_LSN` -- the sentinel
every caller in this codebase actually checks for (`cyanrip_main.c`'s pregap-handling loop,
`cyanrip_log.c`'s `print_offsets()`) -- is `-45301` (`/usr/include/cdio/types.h`, via
`CDIO_INVALID_LBA`). These are different values. On a failed detection (bounds never
converge after exhausting retries), the original code would return `-1`, which every
existing `!= CDIO_INVALID_LSN` check in this codebase would treat as **a genuine pregap at
LSN -1** -- corrupting the cue sheet's `INDEX 00`/`PREGAP` output in exactly the area the
original task brief flagged as highest-risk (the only pregap-related change with a
consumer-visible output-format effect). Fixed to return `CDIO_INVALID_LSN` on this path.

### 2. Buffer leak on one return path

```c
uint8_t *audio_subq_buf = malloc(...);
...
if (subq.crc == crc_comp && subq.adr == 1 && subq.track_number == prev_track_number)
    return track_start_lsn;   // <- buffer never freed here
...
free(audio_subq_buf);
return lsn;                  // <- only this path freed it
```

The "no pregap, confirmed by the sector immediately before track start" early-return path
skipped the `free()` entirely. Fixed by freeing before that return.

### 3. `assert()` used for expected I/O failure, not just programmer-error invariants

Three sites called `assert(!ret);` immediately after a subchannel read, where `ret` is a
`driver_return_code_t` from actual hardware I/O -- not a programmer-logic invariant. A
persistent read failure (which the PR's own comments acknowledge happens: "I've seen a
correct read first occur as late as 180 attempts") would call `abort()` and crash the
*entire rip in progress*, not just fail this one detection. Optical-drive read hiccups are
routine, expected conditions, not programming bugs -- this is exactly the class of failure
`assert()` is the wrong tool for. Fixed by converting all three sites to a graceful
`if (ret) { av_free(...); return CDIO_INVALID_LSN; }`, i.e. "detection inconclusive," which
correctly falls through cyanrip's existing pregap-handling logic as "no pregap known" (the
same outcome as before this feature existed at all -- a safe, no-worse-than-baseline
degradation, not a new failure mode).

**What was deliberately left alone:** the remaining `assert()` calls in the contraction loop
(`assert(left_bound >= prev_track_start_lsn)` and similar) check the algorithm's own
internal invariants, not I/O results -- if one of those fires, it's a genuine logic bug in
the bounds-contraction algorithm, which is legitimate `assert()` territory, so those were
kept as-is.

## Style/cleanup changes (not bug fixes, but worth listing since this is a carry)

- Removed a dead `#include <inttypes.h>` marked `// remove after testing` in the original
  (no `PRI*` macro is used anywhere in the file) and a `#ifdef N_DEBUG / #undef N_DEBUG`
  block that was very likely meant to be the standard `NDEBUG` -- as written it's a no-op
  (undefining a macro that was never defined), and this codebase's own `debugoptimized`
  meson build type doesn't define `NDEBUG` anyway, so no behavior actually depended on it.
- Switched `malloc`/`free` to `av_malloc`/`av_free`, matching this codebase's own allocator
  convention used everywhere else (`libavutil/mem.h`).

## What was NOT touched, and why

- **The core binary-search/contraction algorithm itself** -- the left/right-bound logic,
  the backtrack-then-contract strategy, the retry budget (5, escalating to 200 for sectors
  that can't be ruled out). This is UltraFuzzy's design; the audit's job was to fix
  confirmed defects, not redesign someone else's algorithm.
- **The macOS `ioctl`-based path** (`read_audio_subq_sectors_mac`), which reaches into
  libcdio's *private, unversioned* internal struct layout (`cdio_funcs_t`,
  `generic_img_private_t`, the `_CdIo` struct) because libcdio doesn't yet expose a public
  accessor for the underlying file descriptor -- the PR's own comment notes a libcdio PR
  (libcdio/libcdio#37) that would remove the need for this. Left as-is: it's `#ifdef
  __APPLE__`-gated (compiled only by the macOS CI job since 2026-10-12, and never run
  against a drive), and rewriting someone else's
  platform-specific low-level driver code without being able to build or test it on macOS
  at all would be a worse idea than leaving it exactly as submitted.
- **Six remaining `// TODO` comments** inherited from the PR, all pre-existing
  acknowledgments by the original author of open questions, not defects introduced by this
  carry: whether `track_number - 1` is always safe for non-contiguous track numbering,
  under what circumstances libcdio's first track isn't `1`, whether a cache-defeat is ever
  needed before a sub-channel read, and whether a drive returning all-zero sub-channel data
  should be detected and reported explicitly rather than just failing the CRC check. None of
  these are things this audit could resolve without real hardware to test against, so they're
  left as documented, inherited limitations rather than guessed-at fixes.

## Verification performed in this (hardware-free) environment

- Clean build: 0 warnings (`meson`'s configured `warning_level=1` plus
  `-Werror=implicit-function-declaration`).
- Full test suite: 12/12 passing (`fun512`/`naming` unit tests plus the
  `info`/`basic`/`nrg`/`mixed`/`cue_only`/`art`/`errors`/`filters`/`verify_log`/`pregap`
  disc-image integration scenarios).
- Full before/after log diff and `EAC CRC32` diff across `basic.cue`, `pregap.cue`, and
  `mixed.cue` (built the prior commit in a separate git worktree for a clean A/B): **CRCs
  byte-identical in every case** -- this feature only changes pregap-LSN *metadata*, never
  audio bytes. The pregap-handling code path that runs when a pregap is newly detected
  reports "0 frame pregap" for these fixtures (see below), meaning literally zero audio
  frames move between output files even where the reported metadata changed.
- Direct A/B timing (not the test harness, a controlled same-machine comparison): ~0.15-0.2s
  per rip either way, no measurable slowdown from this change against these fixtures.

## What changed in the log output, and why it's correct (not a regression)

Track 1 of `basic.cue` and `mixed.cue` now shows `Pregap LSN: 0 (duration: 00:02.00)` where
it previously showed `Pregap LSN: none`, even though neither fixture's TOC declares a
pregap. This is intentional, not a false positive: `cyanrip_get_track_pregap_lsn()`
unconditionally returns LSN `0` for the very first track when libcdio's own TOC lookup comes
back empty, reflecting the fact that *every* Red Book audio CD has a 2-second lead-in before
track 1 begins -- a physical/format constant, not something that varies per disc. The
`cyanrip_log.c` change adds those same 150 sectors (2 seconds) to the *displayed duration*
for track 1 specifically, matching EAC's own convention of always counting the lead-in as
part of track 1's reported pregap. `pregap.cue`'s track 1 (which already had a genuine
detected pregap independent of this change) correspondingly grew from a 2.00s to a 4.00s
displayed duration -- the original detected pregap plus the now-counted lead-in, not a
double-count of the same thing.

## What is NOT verified, and needs your own hardware

This environment has no physical CD drive (confirmed earlier in this session: no
`/dev/sr0`), and the disc-image test fixtures are built from a synthetic BIN/CUE/NRG image
via libcdio's own image driver, which does not implement real MMC `READ CD` sub-channel
commands. That means:

- **The actual sub-channel-reading algorithm never ran during any of the verification
  above.** Every test fixture's first `cdio_get_track_pregap_lsn()` call for every non-first
  track already returns a valid, TOC-based answer (these are synthetic images with a known,
  declared layout), so the new fallback code path was never exercised except for track 1's
  unconditional LSN-0 case, which requires no sub-channel I/O at all.
- **Whether this correctly detects a real, TOC-undeclared pregap on an actual disc is
  completely unverified.** That's the entire point of the feature, and it can only be tested
  with a real drive and a disc known to have (or suspected of having) a pregap the TOC
  doesn't declare.
- **Read-retry behavior against a real, imperfect drive** (the 5-attempt default, the
  200-attempt escalation for ambiguous sectors) has no equivalent to test against here --
  the graceful-fallback fix (bug #3 above) is confirmed to trigger correctly when reads
  fail, but how *often* real hardware triggers it, and how long that adds to a real rip, is
  unmeasured.
- **The macOS `ioctl` path** cannot be built or tested at all outside macOS.

**To validate on real hardware:** rip a disc through a drive with working MMC-2 `READ CD`
support (most drives from roughly the last two decades), ideally one where you already know
or suspect a pregap exists that the disc's TOC doesn't declare (this is more likely on
non-standard pressings, mixed-mode discs, or discs with hidden/HTOA content). Compare the
reported `Pregap LSN:`/cue `INDEX 00` output against what this same drive's TOC alone
reports (temporarily reverting the `cyanrip_main.c` call-site change back to
`cdio_get_track_pregap_lsn()` gives that baseline). **Confirm the per-track CRC is unchanged
either way** -- the same invariant this whole engagement has held to throughout.

---

# Addendum: round 5 changes to `pregap.c`

Everything above describes the original PR #115 carry and remains accurate as a
record of that audit. This section records what changed afterwards, so the
document does not quietly describe a file that has moved on.

## Carried from upstream PR #153: the raw-binary drive quirk

Upstream PR #153 ("Harden pregap Q sub-channel search and make it unit-testable")
is a later evolution of #115 by the same author. **The algorithm change was
carried; the restructure was not.**

Some drives' firmware returns the Q sub-channel track, index and MSF fields as
**raw binary instead of the BCD the spec requires**. The CRC is written on the
disc and computed over the BCD encoding, so on such a drive *every* sector fails
validation and the search could only ever end in `unknown (sub-channel CRC
mismatches)` — it never got off the ground. `verify_subq_crc()` now re-encodes to
BCD and re-checks before giving up. XLD carries a workaround for the same
firmware behaviour.

Details worth keeping:

- Detection is **sticky for the rest of one track's search**, so the cost is one
  extra CRC on the first sector rather than on every sector. It is kept **local
  to the search** rather than on the context — deliberately different from #153,
  which stores it per-context — so one odd disc cannot poison the next.
- `verify_subq_crc()` **mutates the buffer in place** when the fixup applies.
  Callers must therefore use the validity flag the read helper returns and must
  not re-check the CRC themselves; a second check would re-encode already-encoded
  fields. The three call sites were rewritten for this.
- An **all-zero CRC is now treated as invalid**. This resolves one of the six
  inherited `TODO`s listed above — "whether a drive returning all-zero
  sub-channel data should be detected rather than just failing the CRC check". It
  is what a drive that returns no sub-channel data at all leaves in the buffer,
  which is an absence of data, not a sector that happens to check out.

## What was still NOT carried from #153, and why

Its restructure moves the platform-specific read into `subq_read_mmc.c` /
`subq_read_macos.c` behind a common header, with an ops-table seam for testing.
The macOS file calls **`cdio_get_device_fd()`, which is not in libcdio 2.1.0** —
verified against both the installed headers and the `.so` export table, not
assumed. Carrying it would break the macOS build against current distributions,
so `pregap.c` keeps the copy-pasted-struct workaround described above.

The *testability* goal of #153 was met a different way: see below.

## The path is now unit-tested without hardware

`tests/subq.c` exercises the decoder on synthetic sectors — CRC, BCD conversion
including the MMC-3 illegal-BCD passthrough (`>= 0xA0`), the compliant-drive path,
the raw-binary recovery path and its stickiness, and the rejection cases
(all-zero, corrupted payload, corrupted CRC).

The CRC-16/GSM test vector was **computed independently of this code**, so the
test pins the polynomial rather than agreeing with itself. Removing the fixup
fails 9 of its checks.

It `#include`s `pregap.c` rather than linking it, because the functions under
test are static.

## What this does and does not retire

**Retired:** the risk that the sub-channel *decoder* is wrong. That is now
testable, tested, and revert-proofed in this environment.

**Not retired by the tests:** the MMC read itself. No disc image reaches it —
images resolve pregaps from the TOC. **A drive has run it**, which this section
denied until 2026-10-21: the BDR-209D printed `Pregap source: sub-channel (not
signalled by TOC)` on 13 tracks on 2026-08-04 (`docs/rig-2026-08-04/`) and on
every rig rip of the reference disc since. A drive exhibiting the
binary-encoding quirk remains untested end to end.

## The search places each frame by its own address (2026-10-21)

The algorithm was left as UltraFuzzy designed it until the rig showed it
varying. In the `Gaps:` lists of the reference disc's 227 filed logs, from 33
sessions on the BDR-209D, track 9's pregap read 94 frames in 192, 95 in 34 and
none in 1, and track 4's 158 in 221 and none in 6. No other track's varied.
Counted 2026-10-21 through `tools/evidence.py cat`, from the `Gaps:` list
because a track block exists only for the tracks a log ripped.

**Why it varied, from the code.** The search's answer is a function of the Q
frames it is given, one per sector it asks for, because each frame was taken
to belong to the sector asked for. Retries and CRC failures change which
sectors are read and when, never which sector the bounds settle on. So two
searches of one disc can only disagree if the drive answered some request with
another sector's frame, or a corrupt frame passed its CRC, one chance in
65,536. Which of the two happened on the rig is not measured; the first fits
both symptoms and `tests/subq.c` reproduces them with the old search: one read
answered by the next sector's frame gives 95 for track 9, and a first read
answered by a frame of track 3 gives none for track 4's 158.

**The change.** A mode-1 Q frame carries its own absolute address, so each
frame is placed at the sector it names, not the one asked for, and the bounds
move by what it says about that sector. The next read is aimed by how far off
the drive answers, once two frames in a row agree on it, so a drive whose every
frame is one sector off is followed and a single slip is not. A target answered
by another sector's frame is asked for again, as often as a frame failing its
CRC would be. A mode-2 or mode-3 frame names no track and carries only its
frame number within the second: the old rule that one right after the previous
track's last known sector belongs to the previous track is kept, but only where
the drive's alignment puts the frame, since by its frame number alone it could
be a second away.

**What it removes.** The assert in the backtrack, `subq.track_number ==
prev_track_number`, kept above as an invariant of the algorithm, was reachable
from the drive: a valid frame of any other track arriving while backtracking
ended the process with exit 134. A frame of another track now says nothing
about this boundary. The other asserts went with the code they guarded.

**What it keeps.** On a drive whose frames all answer for the sector asked, the
answer is the same: 200,000 random searches of aligned simulated drives, with
CRC failures and mode-3 frames placed at random, gave the same answer and
source from the old search and the new, and the same reads but for 551 where a
mode-3 frame right after the previous track's start let the new search stop one
read sooner. That comparison was run in the session, not committed;
`tests/subq.c` pins named cases instead.

**Revert-proof.** With the old search built into the tree, `tests/subq.c`
fails 17 checks and then aborts on the assert: every shifted drive, every
phase of a drive slipping one read in two to seven, and the stale first frame.

**Still needs the drive.** Whether the BDR-209D's frames ever answer for
another sector is the inference above, not a measurement. The next rig rips of
the reference disc settle it: from `.26` the log says when two searches
disagree (`Pregap source: sub-channel (not signalled by TOC; two searches read
… and … frames, the first is used)`), and with this change they should not.
