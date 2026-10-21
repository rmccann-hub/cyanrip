# Known issues: the closed items, as they stood on 2026-10-21

Moved here from `docs/KNOWN-ISSUES.md` at `f1b7c69`, word for word below this
header, when that file was cut to the items still open, after the operator's
review of 2026-10-19, item 3, found it 178 KB. Every item here is fixed and
pinned by a test, landed in the shared protocol, or decided; each says which,
with its evidence. It is history and is not maintained; an item that turns out
not to be closed goes back to `docs/KNOWN-ISSUES.md`.

---

## Fixed 2026-10-16, round 34 — the Windows build's libraries pinned (I16)

### The Windows CI build cloned five dependencies unpinned

**Found 2026-10-05** by `tools/gen-dependency-map.py`. `.github/mingw-build.sh`
ran `git clone --depth 1` of curl, neon, `cyanreg/libmusicbrainz`, libqrencode
and FFmpeg, each at whatever its default branch held that day, so the Windows
artifact was a build of five moving targets and no two runs needed agree.
**Both halves were upstream's** (the workflow and script came with the fork),
and no consumer of this fork uses the Windows artifact: Platterpus builds from
source on Linux. **The operator first left it as upstream ships it**
(2026-10-05), since pinning means choosing five versions and keeping them
current, and then **asked for it in round 34** (2026-10-15, our round 34 lap 1
S10). The actions were pinned by commit on 2026-10-12.

**Now each library is one commit, fetched by its full SHA and named by the
release it is**: curl `curl-8_23_0`, neon `0.37.1` and libqrencode `v4.1.1`,
the newest release of each on 2026-10-16, read with `git ls-remote`,
`cyanreg/libmusicbrainz` at its default branch's commit that day, since it
has no releases, and FFmpeg `n9.0.2` from 2026-10-20. This said FFmpeg
`n8.1.3` was its newest release on 2026-10-16, and it was the newest tag by
date, a maintenance release of the older 8.1 branch: `n9.0.2` had been out
since 2026-09-18. Found on 2026-10-20 by listing each source's tags by
hand, since the weekly dependency check does not read this script. A new
version is a change to the script. The
`mingw` job caches what the five install, `.github/_install`, under a key made
from the script's hash and from the MSYS2 packages they were compiled
against, which `update: true` moves; a restored cache carries a stamp the
script writes only once all five installed, and a failed job saves nothing.
Each at its tag builds as it did at its branch's head: curl's `Makefile.am`,
from which autoreconf writes the `Makefile.in` the script's `sed` edits, has
the same `SUBDIRS` line at both, so the `sed` is a no-op at both, as it was. `tests/workflows.py` fails on a `cyan_do_vcs` call that
names no full SHA, or on a `git clone` in the script, and the dependency map
reads each pin. **Its first measurement is CI's**: the `mingw` job runs only
on GitHub's Windows runner, so whether the pinned build and its cache work is
known from that job's log, not from this environment.

**That first measurement found a failure the old script had always hidden.**
The pinned build stops at the first library that fails, where the old script
ran each step whatever the last one returned. neon's `make install` fails at
`install-man`, `cannot stat 'doc/man/*.3'`, because a git checkout has no
built man pages; every earlier Windows log carries that line (the last green
one, job `116784046263` at `d38e28d`, at its line 2634), and the build went on
because neon's library, headers and `neon.pc` install before the man pages. So
the first pinned run stopped at neon, and cyanrip's `meson setup` then found no
FFmpeg. The script now installs neon with `install-lib install-headers
install-config`, the three targets `install` runs before the documentation;
built here on Linux at the pinned commit, `make install` exits 2 with the same
line and those three exit 0, installing `libneon.a`, `neon.pc` and the headers.

## Fixed for `.20`, 2026-10-05, released on beta 2026-10-06 (`5704062`) — what waited for round 31, and what fixing it found

Put off on 2026-09-30 and 2026-10-04 because each changes what a P2 line says,
and brought into round 30 on the operator's word of 2026-10-05. **None changes
a line Platterpus matches on**: each was checked against their parser at
`platterpus@5ec71f4e` before it landed, and round 30's next lap of ours puts
each to them.

- **`Track N read successfully!` over paranoia's skips** (`e5a0897`). The
  2026-10-04 run on `.19` printed it for track 18 over **2,586 `SKIP`s**: the
  arm was decided by `ctx->total_error_count - start_err`, which moves only
  when the drive reports an error or returns no data, and a skip is neither.
  The condition was upstream's (`src/cyanrip_main.c:911` at `f8ebf48`), and is
  drafted as upstream report 15, with the repeat limit's arm. The arm
  now also counts the last read's `SKIP` counter, the baseline the per-track
  paranoia block uses (*"the last of N reads"*, its `Scope:` line). This said
  *"the kept pass's"*, true when written and made false at the repeat limit by
  the `-Z` spool, which can keep an earlier read there; the limit arm reads
  `with errors` in that case whatever the counts, so no outcome changed. `Ripping errors:` is unchanged and stays the drive's
  count, so a track can now read `with errors` beside `Ripping errors: 0`; the
  contract's units block says so. Reproduced with no drive by
  `sc_paranoia_skip()`: `tests/badsector.c`'s flip mode returns different
  bytes for one sector on every read at the default paranoia level, and before
  the fix the log said `SKIP: 1`, `read successfully!`, `Ripping errors: 0`.
  **And `Ripping errors:` now counts the skips too**, by the operator's word
  of 2026-10-05, with a suffix whenever it does: `Ripping errors: N (including
  M paranoia skips)`, M being the disc block's `SKIP:`. A line with no suffix
  counts no skips, whichever build wrote it. The `--diagnostics` record's
  `rip.ripping_errors` follows it and `rip.paranoia_skips` is new. **The exit
  code does not follow it**: a rip whose only errors are skips exits 0, because
  exiting 1 makes Platterpus skip the securing pass
  (`platterpus@bd508bf1:src/platterpus/workers/rip_worker.py:1905`, `if
  success`). Which way it should go is put to them in round 30 lap 9.
  `sc_paranoia_skip()` pins all four, each revert-proved.
- **…and over `-Z` reads that never agreed** (`4529810`). Tracks 12 to 15 and
  17 of the same run were read five times each with five different checksums
  and each printed `read successfully!`, under a `Secure re-read:  did NOT
  converge` line saying otherwise. A track that hits the repeat limit now reads
  `with errors`. Pinned by `sc_repeat_limit()`, where `-P 0` rules out skips and
  `Ripping errors: 0` rules out the drive. A separate commit from the skip
  term, so either can be taken back alone.
- **`Extraction speed: 0.0x` for 0.033x** (`a72b162`). One decimal from 1x up,
  as before; two from 0.1x; three below that. Three is the most Platterpus's
  `_TRACK_SPEED` reads (`\.\d{1,3}`), so **below 0.0005x it still prints
  `0.000x`**, and the contract says so. Pinned in `tests/logrender.c` on each
  side of each boundary and on track 18's own figures.
- **`-J` and `-f` said `aborted`** (`aa1f067`). A `-J` run that wrote its cue
  sheet now ends `Rip completed:  no (cue sheet only, 0 of N tracks)`, and a
  `-f` run that finished its search `no (offset search only, …)`. Each is set
  where the mode reaches its own end, so a refusal on the way still says
  `aborted`. Both runs open no logfile, so the footer reaches stdout only.
- **A stopped `-f` search retried** (`aa1f067`), upstream's structure too:
  `Stopping, offset finding incomplete!` jumped to `end:`, which retried at
  twice the radius whenever no offset had been found, so the run read on after
  the stop until the radius outgrew every track. A stop now ends the search.
  **Read from the source and not run**: the search needs AccurateRip data for
  the disc, and no fixture's disc has any. Drafted as upstream report 17,
  2026-10-05.

- **The -Z spool: the kept read at the repeat limit, and the album graph**
  (`d7ee6c4`). -Z encoded while it read, from the pass that might be the
  last, and rebuilt the encoders whenever that pass did not converge. So at
  the limit the read kept was the last one, whatever the earlier reads agreed
  on, and the album loudness graph, which spans every track and cannot be
  reset, was fed the first encoded pass: when a later pass was kept, the album
  rows and `REPLAYGAIN_ALBUM_*` described a read that was not on disk. Now each
  pass goes to a `tmpfile()`, one per distinct checksum, and one is encoded
  when the track is decided: the read that converged, or the read the most
  reads agreed on, the newest on a tie. Its checksums are derived again from
  the spool and must match. `sc_repeat_limit_keeps_most_agreed()` pins the
  rule on two read schedules, against the source's bytes and zlib's CRC32 of
  the delivered file, revert-proved three ways. **The album half is held by
  construction, not by a test**: the graph is fed only during the one encode,
  and the shim's flip moves one byte by at most 3, which no album row shows at
  0.1 dB. A full disk now stops a -Z rip where it stopped only the encode:
  `Error creating the -Z spool: %s!` at column 0, exit 1, pinned by
  `sc_spool_refusal()` with the shim's new `CRIP_NO_TMPFILE`.
- **A failed track in a rip of every track said `Rip completed:  yes`**
  (`c1e1ab1`). Found by `sc_spool_refusal()`. Without `-l`, the loop broke out
  on a failed track and fell through to the one assignment of
  `rip_ran_to_completion`, so a run that exited 1 printed `yes (0 of 2
  tracks)`; with `-l` the same failure aborts and prints `no (aborted, …)`.
  Any failed track reached it, a changed medium included. Both loops now
  abort and print `Error ripping: %s`. The asymmetry is upstream's too
  (`src/cyanrip_main.c:1937-1938` against `:2064-2067` at `f8ebf48`), where
  the loop over every track also finalises the album's loudness over a track
  that failed. Drafted as upstream report 16, 2026-10-05.
- **A cache bracket printed the evidence for one end only**, found reading the
  2026-10-05 run. `Cache probe:    128 to 255 sectors (…, cached read 1.5 ms)`
  carried the read behind 128 and nothing behind 255: the composer printed the
  stop read only when nothing had hit, so a bracket never showed the re-read
  that ended it, and that run's reading could say only that it took "at least"
  the threshold. And `394ab17` made a miss three slow tries, while the no-hit
  arm went on printing `first uncached re-read` over the **last** of them. A
  miss now adds `, 3 re-reads after a 256-sector run took X ms or more`, X the
  fastest of the three, so `or more` holds for each. The clause fills the line's
  `%s`, so no P2 row changes, and Platterpus reads nothing inside the line
  (`platterpus@5ec71f4e:src/platterpus/parsers/cyanrip_log.py:2324-2346`).
  `tests/cacheprobe.c` pins both arms and that a ceiling borrows no miss
  clause, revert-proved. **Taking the fastest is in the probe loop, which needs
  a drive: read from the source, not run.**
- **A one-frame AccurateRip entry under the threshold read `(not found)`**
  (`b1857d6`), found reading the tally for Platterpus's round 30 lap 10 S12.
  The `Accurip 450:` line credits a match only above `3*(max+1)/4`, and every
  result at or below it fell to `(not found)`, the words for a checksum no
  entry carries, so the log denied a lookup result it had. It now reads
  `(found in Accurip DB with a confidence of N, not above T, the threshold for
  a one-frame match; whole-track checksums not found)`. *"A confidence of N"*,
  never `confidence N`, which Platterpus reads in this parenthetical as a match
  (`platterpus@9425a524:src/platterpus/parsers/cyanrip_log.py:613`, applied at `:3312`). A zero
  checksum's caveat now holds at any confidence. One P2 row is added and the
  tally is unchanged. Upstream's too (`src/cyanrip_log.c:152-159` at
  `f8ebf48`), drafted as upstream report 14. `tests/logrender.c` had pinned
  the old wording as expected; it now pins the new, revert-proved four ways.
- **The footer could count a one-frame match no track line printed**
  (`8ab9a8d`), found writing up the open list for the operator. The tally
  counted a partial match where neither whole-track lookup returned more than
  0, while the track's `Accurip 450:` line is printed only when both returned
  less than 0; they part on a confidence of 0, which only a malformed response
  carries. The tally now uses the per-track gate. No wording changes, and no
  real response has been seen to reach it. Upstream's too, report 18.
  `tests/logrender.c` pins it, revert-proved.

**FIXED for `.20` (`0645ddb`): a `-f` search that finds no offset exits 1.**
It exited 0 (measured: `-N -f` on `basic.cue` printed `No track had AccuRip
entry, cannot find offset!` and exited 0). By the operator's word of
2026-10-05, agreed with Platterpus in round 30 (our lap 9 S16, their lap 10
S10): `search_for_drive_offset()` returns 1 when it did not print `Drive
offset of ... found`, and the call site then sets `fatal_abort`, not
`total_error_count`, so `Ripping errors:` claims no failed read. **`0645ddb`
had the return the other way, 1 for found**, and the contract's P5, which
reads a `return 1` after a message as its failure path, filed the success
line as fatal and the two lines that end a failed search as neither; found
reading the regenerated contract before committing it, and put in the
program's 0-for-success convention by `68f22ef`, the exit codes unchanged.
`sc_probe_runs_open_no_logfile()` expects 1, revert-proved. **It moved the `-f`
row of the jointly owned `docs/seam-commands.md` §7**, so it landed with the
text both trees agreed, §7 regenerated from `0645ddb`'s clean build, and with
`docs/SETTLED.md`'s row on the file rewritten, since its old check asserted
the `-D | directory` cell the text corrects; a rehearsal at `f6d72c0` had
found that row. Platterpus's section O grades `-f` by its lines, and their Full
script's `expect-exit 0` holds on the reference disc, where the search finds
an offset.

All four are pinned by `sc_probe_runs_open_no_logfile()`, `sc_paranoia_skip()`,
`sc_repeat_limit()` and `tests/logrender.c`, each revert-proved with the build
green. **The `-Z` limit arm ran on a drive on 2026-10-06**
(`docs/rig-2026-10-06-5704062/`, tracks 3 and 5); the skip arm, a speed below
1x and a `-f` search that finds nothing have not. The skip and the speed are
what the next acceptance run on a damaged disc would show.

## Fixed for `.20`, 2026-09-30, released on beta 2026-10-06 (`5704062`) — found fixing where loudness is measured

- **A `-Z` rip's kept pass was filtered with the previous pass's state.** The
  filter and loudness graphs were made once per track and
  `cyanrip_reset_encoding()` rebuilt only the encoders, so when more than one
  pass was encoded the kept one began with the de-emphasis or HDCD filter
  holding the discarded pass's state, and the per-track loudness graph held
  every encoded pass. On an image, a `-Z 2 -r 5 -E` rip whose kept read matched
  a single pass's delivered different audio in 31 of its first 38 sample
  frames, **with the same EAC CRC32 in both logs**: the checksum is over the
  read buffer and the difference was the filter's. It is reached whenever an
  encoded pass does not converge, as the `.19` Full run's track 5 did. Each
  pass now gets a fresh graph. Pinned by `sc_repeat_resets_filter()`, against a
  single-pass rip of the same final read; with the reset removed, 31 frames
  differ. **The album graph was not reset**, and that half was fixed by the -Z spool on 2026-10-05, above.

## Fixed 2026-09-24, from round 26's real test — two claims older than `.15`

Both were in logs we had filed for weeks. Neither was listed here, because
nobody had read them as claims. `docs/rig-2026-09-24-df91ae7/README.md` has
the evidence.

- **An interrupted track was counted in `Tracks ripped partially accurately:`.**
  A read stopped past sector 450 leaves a complete one-sector `Accurip 450`
  checksum, which matches, so every interrupted rip printed `1/14` above `0 of
  14 tracks`. It is in eight filed `cancel-me.log` files, and Platterpus's
  report flagged it before we did. The tally now counts only tracks with
  `audio_ripped` set. Pinned by `test_disc_tally_skips_an_interrupted_track` in
  `tests/logrender.c`.
- **`-H` tagged every file `media: HDCD`**, from the setting, beside `HDCD
  detected: no`. The tag is now `CD`. Pinned by the `media_tag` scenario, which
  reads the tag out of the FLAC file itself. Upstream's code.

## Fixed 2026-09-23 — a retry limit that could hang on one bad sector

### `-r` values that are not a multiple of 5 never returned on an unreadable sector

**Found by fault injection, not on a drive.** `tests/badsector.c` is an
`LD_PRELOAD` shim that fails every read of a disc image overlapping one sector,
the way a drive fails the whole command. At the **default** paranoia level with
sector 400 of `basic.cue` bad:

| `-r` | before | after |
|---|---|---|
| 3 | **did not return in 90 s** | 184 failed reads, returns in under a second |
| 0 | did not return (same cause) | 184 failed reads |
| 10 | 346 failed reads, returned in 1 s | unchanged |
| 20 | 640 failed reads | unchanged |

**Cause, read from the library rather than guessed.**
`cdio_paranoia_read_limited()` compares its retry counter with the limit only
inside `if (retry_count % 5 == 0)`, so no other value is ever matched and the
skip it gates never happens. The code is at `lib/paranoia/paranoia.c` in
upstream libcdio-paranoia, read at `384f4da`; the installed version is
10.2+2.0.1. **Platterpus exposes `-r` to its users** (`cyanrip_backend.py:237`,
range 0 up, default 5), and their rig was left at 3.

**Fix:** `crip_frame_retry_limit()` rounds the per-frame limit up to a multiple
of 5, with 5 as the floor. The whole-track `-Z` ceiling is our own loop and keeps
the value as given. When the two differ, `Retry limit:` says both. The leading
number is still the `-r` value, which is what `tools/probe-argv-surface.py` and
their parser read; their matcher is the label alone
(`platterpus@86f0547:src/platterpus/parsers/cyanrip_log.py:1983`). The
`--diagnostics` record's `retry_limit` stays the `-r` value.

**What the fix does to the audio**, checked against the source `.bin` rather than
against the log: at `-r 3` and `-r 10` alike, sectors 400–402 come back as zeros
and are counted in `Ripping errors:`, and every other sector of both tracks is
byte-identical to the source. **One bad sector costs three**, which is the
library's skip granularity. It is reported as errors, never presented as audio.

**Pinned** by `bad_sector` in `tests/rip_images.py`, which also covers
`Track N read with errors.`, the arm no test had reached (Platterpus's D4).
Revert-proved: with the raw value restored and the binary rebuilt, the scenario
fails on crip()'s 60-second timeout. **Upstream has the same exposure**, so it is
a `docs/SETTLED.md` upstream row. **Hardware:** the error path is the same code
on a drive. A real damaged disc also exercises the MMC read, which this does
not.

## Fixed 2026-09-16, round 21 — both agreed in round 20 and neither shipped inside it

*The middle row is the exception and says so in its own cell: it was FOUND
while doing round 21's work, deferred for a reason that was about round 21's
pin, and fixed in round 22 once that reason was spent. It stays here because
this is where a reader tracing the footer move lands, and a table grouped by
when something was found is not the same as one grouped by when it shipped —
the cell carries the second date so the two cannot be confused.*

| what | how it is pinned |
|---|---|
| **`Ripping errors:` was written before the encoders were asked how they did.** Under a 32 KiB write cap the muxer's trailer write fails, `-j` recorded 2 and the process exited 1, and the log said `Ripping errors: 0` and `Rip completed:  yes` over a 32768-byte file whose intact form is 253742 — two records of one run, and the human-readable one, the archival one, was the wrong one | `cyanrip_log_finish_report()` moved below the encoder-status loop, still inside `end:` so round 14's twenty-four-`goto` property is untouched. `sc_encode_failure_reaches_the_log()` asserts the two records are **equal** and separately that they are **non-zero**, so the property cannot be met by both being 0. Revert-proved with the build confirmed green |
| **A SOURCE COMMENT CITES A TEST THAT WAS RENAMED IN THE SAME ROUND.** `src/cyanrip_main.c:2703` — the long comment justifying the footer move — says the defect was *"demonstrated rather than argued in `sc_encode_failure_is_absent_from_the_log()`"*. That scenario is now `sc_encode_failure_reaches_the_log()` (`tests/rip_images.py:1706`, `tests/meson.build:517`), and the rename is recorded in the test's own docstring. **A `file:line`-style citation that resolves to nothing is the defect this project fixes everywhere else**, and a reader following it gets no hits. Found 2026-09-18 while writing the rig README that quotes the same comment | **FIXED IN ROUND 22**, at the commit carrying round 22's first log change. It was deferred *because of the pin*: `git diff --stat 3952c03 HEAD -- src/` was empty, so every claim about the reviewed pin's source held of `HEAD` too, and editing a comment would have moved that hash and `PROVIDER-CONTRACT.md`'s source anchor for a comment. **Round 22's first fix moves `src/` anyway**, so the reason is spent and the citation is corrected in the same change rather than carried another round. The comment now names both spellings and says which round renamed it. Round 21 lap 1 §1.2 keeps the old name, because a sent lap is never edited |
| **`Frame retries:` named half of what `-r` does** — it caps paranoia's per-frame retries *and* the whole-track repeat ceiling, and the log printed a bare number with nothing saying they were one knob | now `Retry limit:    N (per frame, and per whole-track re-read)`, the exact string Platterpus assented to in round 20 lap 2 §0.2. `-j`'s key follows it (`frame_retries` → `retry_limit`) and the record's schema moved twice inside round 21 — the rename took it to `cyanrip-diagnostics/5` and §4b's `cache_probe` block took it to **`/6`**, which is what the test pin emits. `src/diagnostics.c:371` is the artifact; this cell said `/5` for two days after `/6` shipped. `contract_covers_log` and `contract_diagnostics` both fired on the change and pass on the regenerated contract |

**The fix made two things visible that it did not fix**, and they went into the
open list below rather than being closed quietly: the per-track block said
`Track N ripped and encoded successfully!` over a `File(s):` list computed from
the request, and `Rip completed:  yes` now sits beside a non-zero error count.
**Both have since been answered and neither by this fix** — the first half of
the first was split in round 22 (`89a57d6`; `File(s):` is still open), and the
second was put to Platterpus, who ruled *leave it alone*.

**And one comment was wrong about Platterpus's code for four rounds.** The
schema-bump rationale in `diagnostics.c` cited `SUPPORTED_SCHEMAS = {1, 2}` as
an allowlist over *this* record. Read at
`platterpus@d94bd113:src/platterpus/deps/ripper_manifest.py:89`, it gates
`release-manifest.json`, whose schema is 2; nothing in their tree parses
`cyanrip-diagnostics` at all. Round 12's defect, re-imported into our own
source, surviving on its own closing clause — *"we cannot read their source and
do not claim to"* — which has been false since 2026-09-13.

---

## Fixed 2026-08-15, from Platterpus's known-issues hand-off and one rig hang

| what | how it is pinned |
|---|---|
| **`cdio_cddap_open()` can block forever with no output.** The stall watchdog started ~1700 lines later, so the one window where cyanrip can block before saying anything about the disc had no liveness signal. A rig session sat 300s on `Opening drive...` and left a 111-byte artifact | `crip_stall_wait_begin/end()`, 5 assertions in `tests/stall.c`; revert-proved. **The hang itself is hardware-only** — an image opens instantly |
| `-j` asserted `messages_are_complete: true` while 55 log lines were absent | `messages_scope` + `messages_complete_within_scope`, 4 assertions in `tests/diag.c` |
| `-p 99=drop` accepted, exit 0, never applied | bounded against the disc after the TOC read; `errors` scenario asserts both ends |
| `-l` wrote an `INDEX 00` into a FILE the rip never produced | rip-set input to the predicate + an EOF invariant; `cuegap.c` and the `pregap` scenario |
| the contract could not see composed lines, wrapper macros or ternary labels | generator follows one helper hop, finds wrappers structurally, enumerates ternary arms; 343 stable rows |
| nothing tied a lap's claim about the generating build to the contract | `contract_build` recomputes the source anchor |
| album loudness had no cyanrip-owned row at all | four owned rows, `album_loudness` scenario asserts them against libavfilter's own block |
| a zero AccurateRip checksum printed as `match found, confidence N` | distinct state, no confidence figure |
| `Elapsed:`/`Extraction speed:` interval undefined | defined in the contract's units block, derived from source |

**One of these was already fixed and we did not know it.** `C2 errors:` has said
`supported by drive, not used` since `8499890`; the contract published the row
as `%s`, so a delivered fix stayed invisible for a round. That is the same
defect as the composed-line gap, measured from the consumer's side.

---

## Fixed 2026-08-13, listed because they were open this morning

| what | how it is pinned |
|---|---|
| `cdio_get_track_lsn()` return values used unchecked in the pregap search — a `CDIO_INVALID_LSN` sentinel would have been used in arithmetic and the result reported as a measured pregap LSN | `track_lsns_usable()`, 5 assertions in `tests/subq.c`; revert-proved (dropping the guard fails exactly `subq_test`) |
| a stale `TODO` in `pregap.c` asking whether the drive returns Q data or zeroes — it was answered and tested, and the comment asserted an unaddressed problem | comment replaced with what is actually done, naming the test that pins it |

Neither was reachable from a fixture. The first needs a live libcdio handle
whose track lookup fails; the second was a claim in a comment, which no test can
reach at all. **Both were found by reading the tree rather than by running it**,
which is the only method that finds this class.

---

## Fixed or decided — moved out of *Open* on 2026-10-05

These sat under *Open, ours, and solvable* after they were fixed, or, for the
album loudness block, decided by the consumer's answer, so the heading said
more was open than was. Each entry is moved verbatim; only the repeat loop's
gains a first line, because its opening paragraph predates every fix.

### With paranoia disabled (`-P 0`), one unreadable sector hangs the rip at any retry limit

**FIXED for `.20`, 2026-10-05, released on beta 2026-10-06 (`5704062`).** At `-P 0` cyanrip wraps the cdda
layer's read (`crip_read_audio_salvaging()`, installed on `cdrom_drive_t`'s
public `read_audio` hook, `cdio/paranoia/cdda.h:124`): a request that comes
back short is completed one sector at a time, and a sector that still will not
read is filled with zeros, as paranoia pads a short read itself. The cdda
layer logs it (`010: Unable to access sector N: skipping...`), so the log
carries that line, `Ripping errors:` counts it and the track reads `with
errors`. **Reads that succeed take exactly the path they took before**, so
paranoia's counters and every checksum are unchanged: the golden reference,
ripped at `-P 0`, does not move. `sc_p0_bad_sector()` pins it: the rip returns
in about a second where it hung, exactly the bad sector is zero, every other
sector is the source `.bin`'s, and each track's `READ` count equals a clean
rip's. Revert-proved with the build green: without the hook the scenario times
out at 20 s. **Better than paranoia's own disable mode on a failure**: a
request that failed used to cost every sector in it, and now costs only the
unreadable ones. **Not run on a drive**, where the salvage reads one sector at
a time across a failed request only; a clean read is unchanged.

**The mechanism, corrected 2026-10-05 by tracing it rather than reading it.**
The paragraphs below said the skip *"does not move the read forward"* and
*"finds no block to graft from, the root does not grow"*. It does grow, in the
wrong place. In disable mode `i_read_c_block()` starts every block read with
`paranoia_resetall()`, so a block in which nothing reads leaves the root empty;
`verify_skip_case()` then takes `post = 0` from the empty root and writes its
zero frame at **word 0**, not at the cursor; and the next block read resets the
root again. Read at libcdio-paranoia `384f4da`; seen on the installed
10.2+2.0.1 as 17,498 of the same one-sector cache-defeat seek in six seconds
under `strace`. **Why one sector was enough here**: an image's cache model is
16 sectors (`src/cyanrip_main.c`), one read request, so one bad sector fails a
whole block. On a drive at the default 1200 it takes a stretch long enough to
fail every request in a block, which a long scratch or a dying drive can
produce.

The record before the fix:

**Measured 2026-09-23** with `tests/badsector.c`, at `-r 10` and at `-r 1`:
the read of the sector after the bad one never returned, the stall watchdog
reported it every 10 s, one SIGTERM printed `Trying to quit` and did not end
the process, and a second SIGTERM ended it **with no footer**. A backtrace put
the main thread in `cdio_paranoia_read_limited()` → `cdio_cddap_read_timed()`.
It was retrying the same sector, and libcdio's error buffer had grown to 1.5 MB
of `Unable to access sector 411: skipping...`.

**Cause:** in disable mode the skip that the retry limit gates does not move
the read forward, so the counter resets and the loop starts again (same
function as the `-r` defect above). **Rounding the limit does not help**:
`-r 10` hung too.

**Asked in round 30, 2026-10-05** (in our lap 9 as drafted; the lap as sent
records the fix in its S14): fix it for `.20` at
the cost below, or record it under the operator's close conditions with that
reason. **The mechanism, read from libcdio-paranoia at `384f4da`**: in
disable mode `paranoia_read_limited()` hands each block straight to its root
and keeps none in its cache (`lib/paranoia/paranoia.c:3025-3036`), so when a
read fails, `verify_skip_case()` (`:2350`) finds no block to graft from, the
root does not grow, and the loop repeats. It is the library's to fix.

**Why not now, as it stood before 2026-10-05.** The remedy is ours to write: at level 0, read with
`cdio_cddap_read()` and our own bounded retry instead of paranoia's loop. But
that changes the read path on a real drive. Paranoia reads in chunks and a
per-sector read may be much slower, so it is a drive change that needs a drive
to verify. **Exposure today:** Platterpus never passes `-P`
(`platterpus@86f0547:src/platterpus/adapters/cyanrip_backend.py`, no `-P` in
its argv), so their rips run at level 3, where the fixed path above applies.
Our own image suite passes `-P 0` and has no bad sectors. **An upstream report
belongs to libcdio-paranoia**, not to cyanrip.

### `EXCLUDED_TESTS` rests on a premise we recorded as lapsed, and nothing reads that premise

**FIXED 2026-09-27: the premise is now read by code, before every sweep.**
`tools/mutate.py`'s `inert_edit_probe()` appends a comment at EOF of
`src/utils.c`, runs the whole suite, re-runs any failure alone with the edit
still applied (this suite has a known timeout under load, and a flake is not an
edit detector), and **refuses to report a score** if a test outside
`EXCLUDED_TESTS` fails on the edit, or a test inside it no longer does.
`--probe-only` runs just that; `--skip-probe` prints `UNPROBED` over the score.
`sc_mutation_exclusions_are_pinned()` now also asserts that `sweep()` calls the
probe, and fails with the call removed. The entry below is the record of why.

**Found 2026-09-17 by checking Platterpus's round-21 lap 4 §H shape against our
own tree rather than assuming it was not here.** Their shape: *a guard widened
under an assumption, with the note recording that the assumption had lapsed
written one screen away by the same hand, and nothing connecting them.* They
asked for silence if it did not appear here. **It appears here.**

`tools/mutate.py:111` excludes one test from the mutation sweep:

```python
EXCLUDED_TESTS = {
    "contract_build": "hashes src/ into the contract's source anchor, so it "
                      "fails on any byte changed in src/ …",
}
```

**The premise is that exactly one test detects an EDIT rather than a DEFECT**,
and a sweep is vacuous if a second one exists — every mutant dies on the edit and
the score reads 100%.

**That premise has already lapsed once, within hours**, and `CLAUDE.md` records
it in prose: `tools/sanitize-run.py` ran the whole images suite in the
instrumented tree, `mutate.py`'s third stage picked `contract_build` up again
through `Sanitizer sweep`, and `src/cyanrip_encode.c` scored **100.0% over 125
mutants and meant nothing**.

**The remedy adopted was a procedure, not a check** — run the inert-edit probe
before reporting a sweep — **and the probe no longer runs.**
`tests/rip_images.py:3507` says so in as many words: *"Filed evidence for the
inert-edit row, which no longer re-runs the probe."* `docs/inert-edit-probe.log`
opens with *"FILED EVIDENCE, not a re-runnable gate."* It is asserted to be
**tracked**, not to be **true**.

So a third test that hashes `src/` would silently restore the vacuous 100%, and
the only thing standing between us and that is a person remembering a rule
written three hundred lines away in a different file.

**The counter-example is in our own tree and makes the point sharper rather than
softer.** `GRANDFATHERED = {5, 6}` in `tools/release-gate.py:79` is the same kind
of set resting on the same kind of premise, and `tests/release_gate.py:448`
pins it: *"grandfathered set changed"*. **We wrote the check once and not the
other time**, so the shape is not that the check is hard — it is that nothing
prompts you to write it when the premise is retired in prose instead of in code.

**Platterpus's general form, which we are adopting as stated:** *when a premise
is retired in prose, what reads that premise?* Nothing does, by construction — a
comment explaining why an assumption no longer holds is not a thing any checker
reads.

**Not fixed in this round.** R3 defaults a finding to the next round, round 21 is
open, and this makes nothing about the pin under review unsafe. The fix is cheap
and obvious — assert the exclusion set, and make the inert-edit probe a gate
again or say out loud that it is not one — but "cheap" is not a reason to widen a
round. `docs/ROUND-22-PLAN.md`.

### `Interrupted sample freshness` fails intermittently, and the second failure named the arm

**FIXED for `.18`, 2026-09-27, in the program, not in the check.** The third
occurrence named the route this entry left open: a signal that lands after a
pass's frame loop has finished reaches `goto finalize_ripping` (the `-Z` repeat
check) or falls through to `finalize_ripping:` (a single pass) without passing
the in-loop check that printed the marker. `Interrupted at: track 1, mid-read`
and no `Stopping, ripping incomplete!` was the log telling two different
stories about one stop. The marker is now printed once, at `fail:`, which every
signal exit from a track's read reaches with `ret` still 0; nothing reaches the
logfile between the frame loop and there, so the path that already printed it
writes the same log. **Pinned deterministically**, not on a timer:
`tests/raisesig.c` raises SIGTERM straight after the console-only `Flushing
encoders...` line, inside the window, and `sc_signal_after_last_frame()` fails
with the fix reverted (*"appears 0 times"*) and passes with it. The `-Z` route
between passes has no console output to key on, so it is covered by where the
fix sits rather than by a run. The generator now ties the marker to the arm:
required with `mid-read`, refused with `between tracks`. **A P2 line gains a
call site** (`cyanrip_main.c`, at `fail:`), so round 28's next lap announces it.

**The heading used to say "TWICE", which the third occurrence falsified**; the
dated occurrences below are the record. **Third occurrence 2026-09-26**, at
`0f5f935`, run by hand straight after regenerating the sample, not in a suite:
the fresh probe's log has `Repeating ripping (5 out of 200 …)`, then the album
summary, `Rip completed:  no (interrupted by SIGTERM, 0 of 3 tracks)` and
`Interrupted at: track 1, mid-read`, with no `Stopping, ripping incomplete!`.
So the SIGTERM landed between `-Z` passes, not inside a frame loop. Three
re-runs straight afterwards exit 0.


**Measured 2026-09-17, one occurrence, in a full suite run.** `Ok: 85 Fail: 1`,
and the message was precise:

```
a rip interrupted right now does not produce:
  ^Stopping, ripping incomplete!$
```

**Not reproducible standalone:** three consecutive runs immediately afterwards
passed. So the check is non-deterministic under load, and a green re-run is not
evidence that anything was fixed.

**What is narrowed.** `cyanrip_main.c:867` prints that line from **inside the
per-frame loop** of a track read:

```c
/* Stop now if requested */
if (quit_now) {
    cyanrip_log(ctx, 0, "\nStopping, ripping incomplete!\n");
    break;
}
```

So the line is produced only when `quit_now` is observed *while a read is in
flight*. `tools/gen-golden-reference.py` polls the child's stdout every 0.05 s
for `Ripping track` and signals the moment it appears — and the fixture is three
short tracks, 600 sectors, so a pass can finish inside that window. A signal
arriving after the frame loop has ended reaches a different check and this line
is never written.

**And the generator asserts the opposite as a guarantee.** `INTERRUPTED_SHAPES`
says of the two `Interrupted at:` arms: *"Only the first is produced by any test
here: sc_interrupt() signals once `Ripping track` has appeared, so the read is
always in flight."* **"Always" is the word that failed.** It was true in every
run anyone had constructed, which is not the same as true — the same shape as
the per-track paranoia invariant that survived four verifications because every
artifact it met had each track read once.

**WHICH ARM IT TOOK IS NOW ESTABLISHED, on the second occurrence — 2026-09-18,
one failure in a full suite run, five standalone re-runs immediately afterwards
all exit 0.** The paragraph this replaces said it could not be established,
because `generate_interrupted()` ran inside a `tempfile.TemporaryDirectory()`
and deleted the evidence. `6c507e3` fixed that, and this is the first failure
since. `build/interrupted-probe-failure/` holds both artifacts and they say:

```
Ripping errors: 1
Rip completed:  no (interrupted by SIGTERM, 0 of 3 tracks)
Interrupted at: track 1, mid-read
Log FUN512: SKQUXzRlvWeF6AasZe_SaqvCaenUQeoHvEn0Y161iIsQ…
```

with `-j` at `cyanrip-diagnostics/6` and `exit_code: 1`. **So the interrupt was
real, complete and attested** — every footer field present, the log signed and
verifiable — and the ONLY thing missing was the one line the check pins.

**AND `mid-read` IS NOT EVIDENCE THAT THE LINE-866 BRANCH RAN, which is the
subtlety and the reason to read the source before concluding.** The two are
written from **different conditions**:

- `Stopping, ripping incomplete!` (`cyanrip_main.c:866`) prints only when
  `quit_now` is observed **inside the per-frame loop**.
- `Interrupted at: track N, mid-read` (`cyanrip_log.c:897`) prints when
  `ctx->track_read_incomplete` is still set — and that is assigned **before**
  the loop and cleared only when the read *finishes*, so it means "the read did
  not complete **by any exit path**".

A first reading of these artifacts said they refuted the narrowing above. They
do not. **The read did not finish AND the line-866 check was not reached**, so
the loop left by some other route while the field was still set — which is a
narrower open question than the one this entry started with, not an answer.

**What is still NOT established:** which route. The candidates are a paranoia
read returning an error under the signal, or an earlier `break`/`goto` out of
the frame loop. Both are readable from the source and neither is confirmed by a
run, so neither is written here as the cause.

**The fix that made this paragraph possible cost nothing and settled the next
occurrence exactly as predicted** — which is the argument for the cheaper of
two candidate fixes being done first.

**Deliberately not fixed in this round.** Round 21 is open and this is not a
regression in the pin under review; R3 defaults it to round 22. The two candidate
fixes are not equivalent and should not be chosen under a round's clock: keeping
the failing run's artifacts costs nothing and settles the next occurrence, while
making the signal reliably land mid-read changes what the check exercises. **The
comment is corrected now regardless**, because a docstring claiming a guarantee
the code does not have is the defect that let this go unnoticed.

### The album loudness block describes whatever was read, and calls it the album

**Found in round 26's real test.** `docs/rig-2026-09-24-df91ae7/rips/cancel-me.log:75`
prints `Album integrated loudness (R128): -14.4 LUFS` for a rip interrupted
about 40% of the way into track 1, with `0 of 14 tracks` completed. It is the
loudness of the audio that passed through the `ebur128` graph, which on an
interrupted rip is a partial track, and on every `-l` rip is the selected
tracks only. The four owned rows and libavfilter's block both say "Album".

**Status: left as it is, by the consumer's answer below.** It was not fixed at
first because the fix is a wording decision. The candidates were
leaving the four owned rows out when not every track of the disc was ripped,
or adding a scope line beside them as `Scope:` does for paranoia. Both change
rows Platterpus parses into `album_loudness`. It belongs to the next round,
with the consumer's answer first.

**Their answer is in, in round 27 lap 2 B2, and it asks for no change.** Since
their 0.6.57 they label the figures by what they covered, read off our
`Rip completed:` and `Interrupted at:` lines. If we add a qualifier, **it must be
a NEW line**: their patterns anchor on the four labels, and a renamed row falls
back silently to libavfilter's block, keeping the figure and losing the stable
source.

### `Encoder errors:` counts an interrupted track's partial file as a track encoded

**Found reading round 27's Full run** (`docs/rig-2026-09-26-221a1df/`), and it
was already in round 26's. `rips/cancel-me.log:87` reads `Encoder errors: none;
1 track encoded` two lines above `Rip completed:  no (interrupted by SIGTERM, 0
of 14 tracks)` and `Interrupted at: track 1, mid-read`. `.15`'s
`docs/rig-2026-09-24-df91ae7/rips/cancel-me.log:88` says the same.

**The count is exact about what it counts, and the noun is wider than that.**
Through `.17`, `ctx->tracks_encoded` is incremented for every track that had an
encoder context, once its contexts were joined (`cyanrip@e0471f4:src/cyanrip_main.c:2719-2740`).
Track 1's encoder did close cleanly, over the part of the track that was read.
So "1 track encoded" is true of an encoder and reads as a whole track. A reader
who takes the three footer lines together is not misled; one who reads
`Encoder errors:` alone is.

**Fixed in `.18`, released 2026-09-28 at `51cc789`.** Round 28 settled the wording: our lap 1 S15
asked which form they would read, and Platterpus's lap 2 S16 chose both halves,
*"count only tracks whose read completed, and name a partial file on its own
line, because a count over the record should count what the record holds"*.
Their parser reads only the failure count out of this line
(`platterpus@18823c8:src/platterpus/parsers/cyanrip_log.py:480-489`), so the
count can change under it. The same interrupted rip now reads:

```
Encoder errors: not applicable; no whole track was encoded
Partial files:  1 track (1), read not completed; encoder failures: none
```

`Partial files:` is a **new P2 line**, printed directly below `Encoder errors:`
and only when a track had an encoder and its read did not complete. The zero
arm keeps `no track was encoded` verbatim wherever that is still true, which is
every rip with no partial file. `.17` and every filed log keep the old count.
Pinned by `sc_interrupt()`, against the partial file on disk, and
`sc_encode_failure_reaches_the_log()`, where no read is partial.

### Every figure the log reports about the audio is measured BEFORE the filter graph

**FIXED for `.20`, 2026-09-30, released on beta 2026-10-06 (`5704062`).** `measure_frame()`
(`src/cyanrip_encode.c`) feeds the loudness graphs and the direct peak scan the
frames the encoders receive, converted to one planar-double format so one album
graph takes flagged and unflagged tracks alike. The read-path check keeps its
own scan of the frames built from the read buffer (`input_sample_peak`), since
post-filter audio legitimately differs from the bytes read. The checksums stay
on the read buffer. **An unfiltered rip measures exactly what it did**: the
golden reference's recipe, `-Z 2` included, gives the same 68 loudness lines at
the fix as in the committed log. **A filtered one now describes its file**:
`sc_loudness_after_filter()` rips a pre-emphasised 10 kHz tone and checks the
log's sample peak, album sample peak and `REPLAYGAIN_TRACK_PEAK` against the
delivered bytes, and the R128 difference against the delivered files' RMS
difference; with the fix reverted it fails seven checks. A `-H` rip of a
non-HDCD disc delivers audio 6.02 dB below its source (measured on the tone,
S32), and its log now says so, where it
reported the read buffer's 0 dBFS. Values change on every de-emphasised or
`-H` rip, and no line's text does. The history below is kept as the reason.

**Found by the 2026-09-22 acceptance session, and it is not the defect it looks
like.** Section P3 of that run ripped track 1 of a real disc twice, back to
back, changing one flag:

| | `-H -E` | `-H -W` |
|---|---|---|
| `EAC CRC32` | `B0D122E7` | `B0D122E7` |
| `Accurip v1` / `v2` | `5D3C90CB` / `22B9924D` | `5D3C90CB` / `22B9924D` |
| `Sample peak level` | `94.3% (-0.5 dBFS)` | `94.3% (-0.5 dBFS)` |
| `True peak level` | `0.3 dBFS` | `0.3 dBFS` |
| `Integrated loudness (R128)` | `-13.9 LUFS` | `-13.9 LUFS` |
| `REPLAYGAIN_TRACK_PEAK` | `1.029445` | `1.029445` |
| `Preemphasis` | `none detected (deemphasis forced)` | `none detected` |

`docs/rig-2026-09-22-2cce60d/session/script-report.json`, steps 217 and 221.
Identical to the digit on everything except the one field that reads a setting.

**That reads like the round-15 ternary cascade returning. It is not, and the
difference was measured rather than argued.** Six invocations on disc images,
`docs/rig-2026-09-22-2cce60d` notwithstanding — this part needs no drive:

| flags | fixture | output PCM sha256/16 | bytes |
|---|---|---|---|
| `-H -E` | plain | `05f1fe8cedaff2a4` | 2,822,400 |
| `-H` | pre-emphasised | `05f1fe8cedaff2a4` | 2,822,400 |
| `-H -W` | plain | `efc8702f95ebc8b3` | 2,822,400 |
| `-H -W` | pre-emphasised | `efc8702f95ebc8b3` | 2,822,400 |
| `-E` | plain | `fea860467bdb5368` | 1,411,200 |
| `-W` | plain | `e499ef1f978fe435` | 1,411,200 |

**Four distinct audio streams. One set of reported numbers.** The fix works —
forcing de-emphasis under `-H` changes the samples, disabling it changes them
back, and the automatic path on a flagged disc lands exactly on the forced one.
What the log cannot do is *witness* any of it.

**The mechanism, read from the source rather than inferred.** `filter_frame()`
pushes the **input** frame into the ebur128 graph
(`src/cyanrip_encode.c:656`) and only afterwards pushes the same frame into the
de-emphasis/HDCD graph (`:677`), whose *output* is what reaches the encoders
(`:715`). The two graphs are **siblings off one source, not a series**.
Separately, `crip_process_checksums()` takes the same `data` that is then handed
to `cyanrip_send_pcm_to_encoders()` (`src/cyanrip_main.c:872`), so the checksums
are over the raw disc bytes.

**The two halves want opposite things, and collapsing them would be the fix
going wrong.**

- **`EAC CRC32` and the AccurateRip checksums are CORRECT pre-filter** and must
  stay there. EAC and AccurateRip define theirs over the raw disc samples; a
  post-filter value stops matching the database on every de-emphasised or HDCD
  disc. What is missing is only that nothing says so — the same `Scope:`
  problem the paranoia counters already solved, one field over.
- **The loudness block is WRONG pre-filter.** `Sample peak level:`,
  `True peak level:`, both R128 figures and all five `REPLAYGAIN_*` tags
  (`src/cyanrip_main.c:433-449`) go into the delivered file and describe audio
  that is not in it. ReplayGain exists to normalise playback of *this file*.

**A source comment asserts the opposite of what the code does.**
`src/cyanrip_encode.c:597-602` says the peak is *"deliberately measured on the
same frames that go into the ebur128 filter rather than on the bytes off the
disc: a raw-byte measurement would differ legitimately whenever deemphasis or
HDCD decoding is active"*. The frames that go into the ebur128 filter **are** the
bytes off the disc. The two methods agree because they read the same thing, and
the case the comment names is exactly the case where that thing is the wrong
one — *a fixture whose numbers agree by construction cannot discriminate*, with
the comment as the tell.

**Reach, stated because a 247-of-247 acceptance pass invites the wrong
reading.** Only runs with `-H` and/or active de-emphasis. Without either,
`dec_ctx->filt.buffersrc_ctx` is NULL and the raw frame goes straight to the
encoders (`src/cyanrip_encode.c:674`), so pre- and post-filter are one frame and
every figure is right. **No Platterpus rip is affected today** — none of the
eight `Invoked as:` lines in the 2026-09-22 session carries `-H`, `-E`, `-W` or
`-x`, read off the logs rather than off their rig-check summary. So it is a real
defect with, right now, zero consumer exposure.

**"Zero consumer exposure" was wrong, corrected 2026-09-30: it counted flags,
and the automatic path needs none.** De-emphasis is on by default
(`settings.deemphasis = 1`, `src/cyanrip_main.c:1580`) and applies to any track
whose TOC or sub-channel flags pre-emphasis (`crip_deemphasis_active()`,
`src/cyanrip_main.h:479`). Platterpus passes none of `-E`, `-W`, `-H` or `-P`
(`platterpus@0981c69:src/platterpus/adapters/cyanrip_backend.py`, the argv it
builds), so **every Platterpus rip of a pre-emphasised disc takes this path**,
and their parser reads the figures it produces: the `REPLAYGAIN_*` tags
(`platterpus@0981c69:src/platterpus/parsers/cyanrip_log.py:643`), `Sample peak
level:` (`:962`) and the album loudness rows (`:730-747`). The rig disc is not
pre-emphasised, which is why no filed rip shows it. Measured at `8f4ae14` on
`preemph.cue` to raw PCM, default flags against `-W`: the two delivered files
differ (md5 `b1e6ed20…` against `63e60c84…`), and both logs print `-8.7 LUFS`,
`REPLAYGAIN_TRACK_GAIN: -9.30 dB` and `REPLAYGAIN_TRACK_PEAK: 1.005757`. **The
fixture cannot show the size of the error**: its square wave has little treble,
and the two files' RMS differ by 0.10 dB, below the log's 0.1 LU precision. A
test of the fix needs a pre-emphasised fixture with treble in it.

**Not fixed here, deliberately.** Moving the measurement downstream changes the
*values* of five P2 lines and five metadata tags on affected rips, which is
contract surface and wants a round — and the round in flight is pinned at
`2cce60d`, where a finding defaults to the next round. Reported in round 23 §H.

`sc_deemph_with_hdcd()` pins both halves: EAC CRC32 must not move between
`-H -E` and `-H`, and the loudness figures must. Since the fix (`cc79c5b`,
`.20`) a failure of either is a regression.

### A settled fact is re-checked by calling the internet, and it times the suite out

**Measured 2026-09-13**, by profiling `tools/check-settled.py` rather than
guessing at it: 136.8 s over 67 commands, of which **`tools/accurip-live-probe.py`
is 80.2 s — 59% of the whole check**. `probe-argv-surface.py --gate` is 26.7 s
and `tests/release_gate.py` 17.3 s; the remaining **64 commands total ~13 s**.

`tests/meson.build` gives `Settled facts` a 120 s timeout, chosen as roughly 4x
headroom over a measured 27-30 s. It now **exceeds that and the meson test
TIMEOUTs**, so the suite reports 80 OK and 1 timeout rather than 81 OK. The
check itself still returns **0 stale**; it is the clock that fails, not the
facts.

**Measured again on 2026-09-15 morning, at 101.20 s against the same 120 s
timeout over 72 runnable commands — and FIXED that afternoon**, so this
paragraph is the record of the last measurement taken while the network was
still in the gate, not a current state. It said *"whether it passes on any given
day is still decided by how fast `accuraterip.com` answers rather than by
anything in this tree."* That stopped being true a few hours later; see the
half-fix below, which took it to **54.6 s** over **77** commands.

**Left standing rather than deleted, because it is also an example.** A document
edited twice in one session contradicted itself in the same file — the exact
thing `sc_docs_do_not_contradict_themselves()` exists to catch, and it was
caught by grepping this file for its own numbers rather than by the test, which
checks CLAUDE.md and the handshake README and not this one.

**The cause is not size, and the first diagnosis of it here was wrong.** It was
attributed to documentation growth — ~380 lines added to `STATUS.md`,
`KNOWN-ISSUES.md` and `Changelog.md` in one session — on the reasoning that the
check greps `docs/`. Profiling says those greps are in the ~13 s tail. **80 of
the 137 seconds are one HTTP conversation with `accuraterip.com`**, and its
duration is set by the network that day.

**The defect is that the row exists in this form at all.** `SETTLED.md` row 84
states a fact about **our parser** — that the AccurateRip response parser runs
in this sandbox with no drive — and re-checks it by contacting a third-party
service. This repository already has the rule, and paid for it:

> *A check that reaches the network is not evidence about this program.* The
> first diagnostics refusal test drove cyanrip into a refusal reached **via a
> MusicBrainz lookup**, so what it asserted depended on whether the lookup
> failed by not-found or by timeout. It failed once and would not reproduce.

Two consequences, and the second is worse than the slowness:

1. **The runtime is unpredictable**, so any timeout is either too tight (today)
   or too loose to catch a real regression.
2. **A settled fact can go red because someone else's server is down.**
   `check-settled` cannot distinguish *"the parser broke"* from *"accuraterip.com
   did not answer"* — which is this project's own `none` versus
   `unknown (reason)` rule, failing in the tool that indexes the rule.

**FIXED 2026-09-27; half-fixed 2026-09-15, and the second half was deferred
for a named reason, below.**

**Done: the network is out of the gate.** `SETTLED.md`'s AccurateRip row no
longer re-runs the probe. The run is filed verbatim at `docs/accurip-probe.log`
(2026-09-15, `found`, confidence 200) and the row's check asserts the **claim
against the artifact** — edit the row's numbers without re-running the probe and
it fails. Measured: `check-settled.py` went from ~100 s to **54.6 s**, so
`Settled facts` now sits at 45% of its 120 s timeout instead of 84%, and no
verdict in the suite depends on somebody else's server.

**A first attempt at that check was near-vacuous and the revert-proof said so.**
`--toc-only` re-derived the reference TOC, on the theory that the query's one
local input could rot. Pointed at a *different* session's log it returned the
same `14 268707` — every session is the same disc. A check satisfied by the
wrong file is not a check; the flag stays as a tool affordance and the row's
check moved to the claim-versus-artifact comparison, which fails when the
artifact is edited.

**Done 2026-09-27: the parser is asserted against a recorded response.**
`crip_parse_accurip()` is split out of `crip_fill_accurip()`, a pure move, and
`tests/arresp.c` feeds it the rig disc's dBAR response, filed as
`tests/fixtures/accurip-dBAR-014-001d420f-013bb370-e20dfe0e.bin` (1,807 bytes,
fetched once, HTTP 200). The expected values come from an independent artifact,
`docs/rig-2026-09-10-ddc1e8c/rips/secure-reread.log`: 12 of its 14
`Accurip v1:` checksums are found at the confidence that log printed, and 2 are
not found, as it says. No network is involved, and mutating the parser's
checksum read fails it.

**Found by writing it, and FIXED the same day for `.18`: `mismatch` could not
be reported.** The parse set the disc status to `FOUND` before its loop, so the
`MISMATCH` assignment below it could never run. A response whose entries all
carry another disc's ids read `AccurateRip:    found`, an empty one did too, and
the report then printed `Tracks ripped accurately: 0/N` over a comparison that
never happened. The status now starts at `NOT_FOUND`: those two responses read
`mismatch` and `not found`, and print no tally, as a disc absent from the
database already did. `tests/arresp.c` builds both from the recorded response,
plus a foreign entry before and after the real ones, and fails on two checks
with the old line put back. Read from the source first: no real response has
had that shape. **What a consumer can notice:** the disc-level `AccurateRip:`
line's value in those two cases, and the tally's absence. Platterpus's parser
ignores the disc-level line (`platterpus@59f4c00:src/platterpus/parsers/cyanrip_log.py:2171`)
and reads the per-track rows, which do not change; the `-f` offset search ends
with the same message it did. It is upstream's code too, `accurip.c:171` at
`f8ebf48`, and `docs/SETTLED.md` checks both trees.

**What was still to do: assert the parser against a recorded response.** That is the real
fix — offline, deterministic, and it would cover the parse rather than a
recorded verdict about it. It needs the response parse split out of
`crip_fill_accurip()`, which does the curl fetch inline, exactly as
`tests/subq.c` needed the Q sub-channel decode split out.

**And it is NOT being done while round 20 is open.** Splitting it touches
`src/`, and round 20's own `HANDSHAKE-PIN-POLICY` — and Platterpus's round-19
§F1, which calls it *"a stronger statement than the pin has not moved"* — rest
on the span from `fe4d2c4` containing **exactly one `src/` commit changing zero
non-comment lines**. A refactor would end that, during the round that relies on
it. R4 says fixes queue; this one queues. **Raising the timeout was never the
fix** — it keeps a network-dependent verdict in a gate and moves where it
misfires.

**A timeout again on 2026-10-15, on CI's macOS runner, with no network in the
check.** Pull request #20 at `3e467b3`, `macos` job: `Settled facts TIMEOUT
120.05s`, killed by SIGTERM, every other test OK or skipped (116 OK, 12
skipped). On the same commit, `linux (default)` ran it in **53.07 s**; on the
base `21382e4`, `macos` ran it in **30.73 s**; the one re-run of the failed job
passed in 4 min 28 s. No `SETTLED.md` row reaches the network, and the pull
request changed a lap's ready line, `STATUS.md`, the round table, the changelog
and the golden reference. **No mechanism is established**, so it is recorded
here, as `STATUS.md`'s `suite-timeouts-at-default` says each occurrence is.

**And again the same day, on the push of `b06d20e`**, the merge that published
`.23`: `macos`, `Settled facts TIMEOUT 120.03s`, killed by SIGTERM, 116 OK, 12
skipped and none failed (run 38820348425, job 116715137866). **One tree, three
times on macOS within an hour**: `b06d20e`'s tree is the pull request head
`da0db2c`'s (`353b5ad`), whose own run passed it in **93.08 s**; the push
timed out at **120.03 s**; and the one re-run of the failed job passed it in
**28.26 s**. Earlier that day it took 30.73 s at `21382e4` and 37.06 s at
`9aee54a`. So the time does not follow the tree, and the content of the
change is not the cause; **what is, is still not established**, since CI keeps
no per-row timing and the runner's other load is not visible from the job's
log. It is our round 34 lap 1 S8, and was `STATUS.md`'s
`settled-facts-macos` until it closed on 2026-10-19, below.

**And twice in a row on one tree on 2026-10-16**, pull request #40 at
`b45029f`: `Settled facts TIMEOUT 120.04s` on the run and on its one re-run
(jobs 117241909752 and 117244235906), where pull request #39's tree had passed
it in **42.44 s** on macOS minutes earlier. The second run shows it is not
only load: `Black-box sweep` is `is_parallel: false`, so meson ran nothing
else beside `Settled facts` from 23:34:12, when the last other test ended,
until it killed it at 23:35:08, and it did not finish in those 56 s alone.
The killed test printed nothing, because `tools/check-settled.py` printed only
at the end. **It now prints each run's five slowest rows, and on SIGTERM, which
is how meson ends a test that overruns, the row that was running and the
slowest before it** (`tests/golden_libraries.py` case 6). Locally the same
tree takes 44.8 s inside meson, the slowest rows those reading run evidence at
about 6 s each. The next timeout names its row; the cause is still not
established.

**And a measurement that is a warning, not yet a fault.** Since HR-2's move,
the 32 rows that re-check a file on the evidence branch run only where that
file is fetched (`tools/check-settled.py` counts them unprobed otherwise). In
this environment's checkout with `tools/evidence.py fetch --branch` done,
`Settled facts` took **80.7 to 103.9 s** in seven full suites on 2026-10-15,
the last at `10f2352`, against **47.7 to 52.8 s** in two with nothing
fetched: up to about 87% of its 120 s timeout, and rising. CI's evidence job, which runs those rows, took 34.3 s on Linux
(pull request #16). Where a check reads evidence, its time now depends on
whether the evidence is fetched, and a timeout chosen before the move did not
account for that.

**The cause, established 2026-10-19 from the first killed run to name its
rows.** Pull request #43 at `8ee5138`, `macos`, `Settled facts TIMEOUT
120.03s` (job 118191184329): the slowest rows were `grep -h '^Rip
completed:' docs/rig-2026-0*/rips/cancel-me.log` at 25.39 s, two
`docs/rig-*/rips/secure-reread.log` rows at 22.95 and 19.80 s, and a third
running for 22.2 s when killed. Each named run evidence through a glob, and
`run_row` overlaid **every file of every folder** a path named: 660 files for
the first, 1,015 (about 114 MB) for the others, one `git cat-file` each, to
read 16 and 19. That only happens once the evidence can be read, and in a
suite job it becomes readable part-way through: `Lap statements are well
formed` fetches the evidence branch into `.git/cyanrip-evidence.git` when a
lap cites evidence (`tools/lap-statements.py`), beside `Settled facts`. A row
reached before the fetch is unprobed in milliseconds; one reached after it
reads the whole overlay, about 6 s here and 20 to 25 s on the macOS runner.
**That race is why the time never followed the tree**, and why the
measurement above found evidence rows slow wherever the branch was fetched.
**Fixed by `783ee7c`**: `evidence.files_named()` gives a row the files it
names, a folder or an unreadable pattern still giving every file, so the 36
rows' overlays go from 4,721 files to 317 and those two rows take 0.11 and
0.12 s here; `tests/evidence_tool.py` fails when either half is reverted.
**Still open, and not fixed by it:** whether those rows run or are unprobed
in a suite job still depends on which test reaches the cache first.
**And no run could show which, until 2026-10-19**: the timing step CI runs
after the suite printed only the slowest rows, so pull request #46's macOS job
(`45799e2`, job 118237544275) passed `Settled facts` in 42.5 s, 102 rows run
and the slowest 4.73 s, without saying whether those rows were among them. It
now prints each row it could not check, with its reason, and the count;
`tests/golden_libraries.py` fails when either is reverted.
**Closed the same day by the first run to print it**, pull request #47's
macOS job (`1dd06da`, job 118247330150): `Settled facts` passed in 46.1 s,
102 rows run and the slowest 5.02 s, with one row unprobed, the golden
reference's, which macOS skips by the owner's decision of 2026-10-12. So the
evidence rows ran there, and none was among the five slowest. Before it,
#43 timed out at 120.03 s, and #45 passed in 54.6 s and #46 in 42.5 s
without saying whether those rows ran. Which test reaches the evidence cache
first still varies, so a later run may count them unprobed, and now says so.

### `docs/seam-commands.md` carried FIVE known-wrong statements — ALL FIXED in round 30

**Consolidated here 2026-09-15.** They were recorded in two different files, one
of them a 1,100-line standing status, which is how a set of three reads as three
unrelated one-offs instead of a document to fix. Consolidation applies to
documentation and never to evidence; this is documentation.

| # | what it publishes | what is true | found |
|---|---|---|---|
| 1 | §7: *"Every value either took effect or was refused with a message"* | **48 of the 68 accepted rows** were graded from exit status alone — re-measured 2026-09-16, and the *"49 of 111"* this row carried was a count against an older binary. **The generator is fixed, 2026-09-27**: those rows are now `unobservable` (`--gate`: 111 probes, 47 refused, 16 seen to take effect, 48 unobservable), pinned by `sc_argv_probe_names_what_it_did_not_see()`. §7 itself is regenerated at the joint bump | ours |
| 2 | line 504: `-p '99=drop'` accepted, exit 0 | the binary **refuses** it | theirs, lap 16 §B3 |
| 3 | line 97: `-D` is `directory` / `str, path` / `writable` / *"output directory"* | it is `folder_scheme`, *"Directory naming scheme"* (`cyanrip_main.c:1603` at the pin) — a **relative** scheme, with `-F` its per-track sibling | theirs, lap 16 §B3 |
| 4 | the §1 provenance warning: *"The cyanrip column is `?` throughout below … Their half arrives in the round-8 return file"* | **0 of §1's 17 rows** carry `?` in the cyanrip column; all 17 say `HAVE`. Counted by reading the column, not the sentence | ours, 2026-09-22 audit |
| 5 | §4 NEED item 4 asks for *"an escape mechanism in the `-a` / `-t` grammar — or a written statement that there is none"* and describes a U+2236 workaround | **§1's own `-a` row, in the same file**, says both sides `HAVE` it: *"there IS an escape: `\\:`"* and *"escape shipped lap 31"*. The file contradicts itself; whether Platterpus's U+2236 substitution is still in their code is theirs to say, and is not claimed here | ours, 2026-09-22 audit |

**RE-MEASURED 2026-09-16, and the split of who fixes what is not what this entry
said.** Platterpus pointed out that §7 carries its own *"This section is
GENERATED by `tools/probe-argv-surface.py --markdown` … Never hand-edit it"*.
That is **our** tool, so rows 1 and 2 are ours to regenerate; only row 3 is
hand-written prose in a jointly-owned section.

**Row 2 is fixed by regenerating.** The live binary refuses `-p '99=drop'` with
`Invalid track number 99 for pregap, list has 2 tracks!`, exit 1.

**Row 1 is NOT, and it is a defect in the generator rather than in the committed
copy.** The sentence is emitted by the tool. Measured 2026-09-16 and **re-measured
2026-09-22 on `0.9.4-rc2+platterpus.14`, unchanged**: **116 rows, 48 refused, 68
accepted — and 48 of those 68 carry `(no header field exposes this)`.**
`probe-argv-surface.py:99` returns `accepted` on exit status
alone when no header field exists to check, so three quarters of the accepted
rows were never observed to take effect while the summary says they were. The
fix is a third outcome — `unobservable` — not a reword, and `--gate` must keep
firing only on a genuine silent drop.

**AND THE REASON ALL THREE DRIFTED IS A CHECK THAT COULD NOT FIRE.**
Until 2026-09-29, `python3 tools/probe-argv-surface.py --binary
build/src/cyanrip --check docs/seam-commands.md` refused outright: *"carries
no generated-block delimiters"*. §7 had declared itself generated since it was
written and **nothing verified that it was.** Planned in
`docs/ROUND-22-PLAN.md` §3; §7 has carried the delimiters since 2026-09-29, and
the `Argv table in seam-commands.md` test has run `--check` since `ae9764e`.

**Do not cite any of the five.** Row 3 is the one that has already cost
something: the real semantics are exactly why an empty leading component made a
multi-component scheme resolve **absolute**, and a reader who believed line 97
would not have looked.

**Rows 1 and 2 are FIXED, at `83bcd70` (2026-09-29), round 29's one joint move
of the file**, which regenerated §7 with the `unobservable` outcome and the
refused `-p '99=drop'`. This entry said *"NONE of them is fixed"* for a week
after that; found in round 30 by diffing §7 against the binary. **Rows 3 to 5
are FIXED in our tree by the text our round 30 lap 9 S16 proposed and
Platterpus's lap 10 S10 accepted**, landed with the `-f` exit row in the commit
after `0645ddb`; Platterpus lands the same bytes in the commit that files our
lap 11. Row 5's answer was checked against their code, which no longer writes
the U+2236 substitute
(`platterpus@bd508bf1:src/platterpus/adapters/cyanrip_backend.py:825-835`).

**Until then they were not fixed, and not for want of knowing the answer.** The file is
shared and neither project owns it — a one-sided edit is how two copies of one
spec come to disagree, which has already happened once to `PROTOCOL.md`. They go
in together at the next joint version bump.

**Deliberately NOT added to round 20.** R1 fixes a round's close conditions at
lap 1 and round 20 has two; a third arriving mid-round is the exact failure R1
exists to stop, and these break nothing in `fe4d2c4`.

**This paragraph then called them *"a round-21 bundle"*, and rounds 21, 22 and
23 all closed without it.** Nobody proposed the bump, because the entry that
named the round was not something any lap-1 author read. It is the same gap as
the joint entry below on K1–K3 — a change agreed or planned, and then left to
memory across a round boundary. **They are now listed in that section's
consolidated table of shared-document defects, which is what round 24's lap 1
cites**, so the bundle has a place to be picked up from rather than a round
number to go stale.

### The secure re-read's repeat loop: four things for round 29, all upstream's code

**All four are fixed**, added 2026-10-05: items 1, 3 and 4 for `.19` (`9669d84`,
`fb31a2b`, `22f7aae`), item 2 for `.20` by the `-Z` spool (`d7ee6c4`). The
paragraph below is how the entry read before any of them landed.

**Found by Platterpus reading round 28's Full run**, in their round 28 lap 9
(S9, S16, S17, S19), and each checked against our source at `e0471f4`, our own
filed copy of the bundle (`docs/rig-2026-09-28-e0471f4/rips/secure-reread.log`,
invoked with `-r 3 -Z 2`) and upstream's `f8ebf48`. The code is upstream's in
all four. None is a defect in `.17` that breaks its pin, and none is fixed in
`.18`; each changes a P1 or P2 surface, so each is round 29's to announce.
**Item 1 is fixed for `.19` at `9669d84`**, announced in round 29 lap 1; the
other three are proposed there.

1. **The loop prints its checksum before the final XOR, so it never equals
   the track's `EAC CRC32:`.** `Repeating ripping (… current checksum %08X)`
   and `Done; (N out of N matches for current checksum %08X)` print
   `checksum_ctx.eac_crc` (`cyanrip@e0471f4:src/cyanrip_main.c:1006-1007`,
   `:1028-1029`). The track block prints that value XORed with `UINT32_MAX`
   (`src/checksums.h:86`). Track 3's converged read is `Done; (2 out of 2
   matches for current checksum A62CAD22)` at `secure-reread.log:222` and
   `EAC CRC32:     59D352DD` at `:260`, and `0x59D352DD ^ 0xFFFFFFFF` is
   `0xA62CAD22`. So a reader comparing the loop's checksums with AccurateRip,
   EAC, CTDB or our own track block compares complements, and nothing in the
   log says so. Platterpus found it by working the arithmetic (their S9). Their
   parser matches those lines on the counts only and captures no checksum
   (`platterpus@41f92220:src/platterpus/parsers/cyanrip_log.py:269-273`), so
   printing the finalised value would not break that parse. It still changes
   what a P2 line's number means, which is why it needs a round. **Fixed at
   `9669d84`**: both lines print the finalised value, the comparisons keep the
   raw one, and `sc_reference` requires each converged track's `Done;` checksum
   to equal its `EAC CRC32:`.
2. **At the repeat limit, the audio kept is the last read** (their S16).
   Lines 1018-1021 switch encoding on for the read that may be the last, so
   when the limit is hit, that read is encoded whatever the earlier reads agreed
   on. Track 5 read `E0036697` twice and then `6902BCF0`, and `6902BCF0` is the
   read kept (`secure-reread.log:381-385`, `:423`). Their proposal is to keep
   the read that agreed most. Which bytes land on disk is ours to decide
   (`docs/OWNERSHIP.md:61`, *"The audio bytes and every checksum over them"*).
   **FIXED for `.20` by the -Z spool (`d7ee6c4`)**, the rule proposed in our
   round 30 lap 5 S23 and its cost accepted in their lap 6 S9: the read the
   most reads agreed on is kept, the newest of them on a tie, so track 5 above
   would now deliver `E0036697`. Pinned by `sc_repeat_limit_keeps_most_agreed()`.
   Before that: round 29 lap 1 S36 said *"We will propose the rule in a later
   lap"*, and no lap until round 30's lap 5 did. Counted 2026-09-30
   off `docs/rig-*/rips/*.log`: 24 limit hits in 15 filed logs, on tracks 3
   (12), 5 (10) and 4 (2), every one under `-r 3 -Z 2`. The one filed `.19`
   secure re-read, `-r 5 -Z 2`, converged on all 14 tracks
   (`docs/rig-2026-09-30b-174a134/rips/secure-reread.log`).
3. **`Done; (no matches found, but hit repeat limit of %i)` is printed whatever
   the count** (their S17): line 1012's format has no count and never reads
   `matches`. On track 5 it was true of the read it follows, which matched
   neither earlier read. It was false of the track, whose first two reads
   agreed, and that second sense is the one a consumer takes. Platterpus's own
   parser comment reads the line as *"it gave up without any two reads
   agreeing"* (`platterpus@41f92220:src/platterpus/parsers/cyanrip_log.py:251`).
   A `-Z 3 -r 3` rip of three identical reads would print it with two matches.
   Their `_SECURE_DONE_FAIL` matches `no matches found` (`:273`), so rewording
   it removes a string a consumer matches on: their both-wordings release comes
   first (round 20's ordering rule). **Fixed at `fb31a2b`, for `.19`**, after
   that release: their 0.6.63 reads both wordings, and the line is now
   `Done; (repeat limit of N reads reached; at most M reads agreed)`, M being the
   largest number of reads that share one checksum. The `repeat_limit` scenario
   reaches it on an image by varying one sector per read (`tests/badsector.c`),
   including A, A, B, where the last read agrees with nobody and M is 2.
4. **`-Z N` with `-r` of N or less can never converge** (their S19).
   Convergence needs N matches against earlier reads, so N + 1 reads (`:1005`).
   The limit counts every read from 0 (`:762`, `:1004`, `:1011`), so `-r N + 1`
   tolerates no read that disagrees. Our argument parsing accepted `-Z 2 -r 2`.
   Their settings refuse it now. **Refused here too at `22f7aae`, for `.19`**,
   before any disc is opened, at column 0 with both values and a remedy that
   exists (`zr_refusal`); an invocation that exited 0 now exits 1, which is the
   P1/P4 change round 29 carried, with the shared `seam-commands.md` moved once
   for both sides' argv tables (`83bcd70`).

---

## Moved from *Open, ours, and solvable* on 2026-10-21, each fixed

### At the repeat limit the last read's checksum is not printed, and the spool can leave it in no line (fixed for `.22`)

**Fixed for `.22`, in round 31**: when the kept read is not the last, the
line that ends the loop names it, `Done; (repeat limit of 5 reads reached; at
most 2 reads agreed; last read EE58174A, not kept)`, our round 31 lap 1 S26's
wording, which Platterpus's lap 2 S14 accepted and their 0.7.101 reads.
`sc_repeat_limit_keeps_most_agreed()` and `sc_repeat_limit()` pin it, with the
last read's checksum computed from the source bytes. The entry below is the
record of the defect.

**Left for round 31 by the operator's word of 2026-10-06**, which closes round
30 on the run that found it; the exception to the rule above is theirs, and
round 31 fixes it within the round (v7 R3).

**Found 2026-10-06, reading the closing run on `.20`**
(`docs/rig-2026-10-06-5704062/`), and **introduced by `.20`'s `-Z` spool**
(`d7ee6c4`). The repeat loop prints `Repeating ripping (... current checksum X)`
after every read but the last, then `Done; (repeat limit of N reads reached; at
most M reads agreed)`, and the block's `EAC CRC32` is the kept read's. Up to
`.19` the kept read was the last read, so the log carried every checksum. From
`.20` it is the read the most reads agreed on, the newest on a tie
(`crip_spool_kept_at_limit()`, `cyanrip@174a134:src/cyanrip_main.c:868`), so **a track read A,
A, B, B, C keeps B, and C is in no line of the log**. The block's paranoia
counters are the last read's (`Scope:  the last of 5 reads`), so in that case
they describe C while every other figure in the block describes B, and nothing
says which pass was kept.

**Reproduced with no drive**: `tests/badsector.c`'s flip schedule `CRIP_FLIP_RUN=2
CRIP_FLIP_CYCLE=3` at `-Z 2 -r 5` on `basic.cue` (the second case of
`sc_repeat_limit_keeps_most_agreed()`) prints `B664A115` twice and `2FFECF45`
twice, keeps `2FFECF45`, and the fifth read, `EE58174A` by `zlib.crc32` of the
source with the flip applied, is nowhere. **The closing run did not show it**:
in all three limit-hit tracks the kept read was the last one, which for section
N's track 5 is known only by the rule (the README says how).

**It already cost a wrong count.** `tools/cross-rip.py` counted the kept block
as the last read, so over that log it reported `2FFECF45` three times and two
distinct checksums where there were three. Fixed in the commit after the run's
filing: the tool now tells the case from the log (the kept checksum, `M`, and how many printed passes read
it), counts the missing read as one the log does not carry, and
`tests/cross_rip.py` pins both cases on the filed log.

**The fix to the log, not yet made, and what it costs.** Name the last read
when it is not the kept one, inside the line that ends the loop: `Done; (repeat
limit of 5 reads reached; at most 2 reads agreed; last read EE58174A, not kept)`.
It is a P2 line. Platterpus reads it with two patterns, the prefix `Done;
(repeat limit` and the fragment `at most M reads? agreed`
(`platterpus@9ecd1147:src/platterpus/parsers/cyanrip_log.py:341-352`), and an
addition after `agreed` leaves both matching, so no string they match is
removed and nothing of theirs has to ship first. It wants announcing in a lap.

### The `Gaps:` list leaves out a pregap it could not determine, so it reads as none (fixed for `.22`)

**Fixed for `.22`, in round 31**: each pregap whose search failed has a line,
`pregap of track N unknown (sub-channel unreadable)` or `(sub-channel CRC
mismatches)`, the track block's own reason, and `None signalled` is printed
only when every search succeeded. Our round 31 lap 1 S27's wording, which
Platterpus's lap 2 S15 accepted and their 0.7.101 reads.
`sc_gaps_unknown_pregap()` pins it on `basic.cue`, whole and with `-l 1`, with
`cdda.nrg` as the control. **Every image rip changes with it**: an image's
sub-channel cannot be read, so a track whose pregap the image's TOC does not
give now has a line. The entry below is the record of the defect.

**Left for round 31 by the operator's word of 2026-10-06**, as the entry above.

**Found 2026-10-06, reading the closing run on `.20`**, and older than it: our
sub-channel pregap search, carried from upstream PR #115, is what makes a
pregap undeterminable. `setup_track_offsets_and_report()` skips a track whose
pregap LSN is `CDIO_INVALID_LSN` without a line (`src/cyanrip_main.c:1535-1536`),
and that is what a failed search returns. The track's own block says `Pregap
LSN:  unknown (sub-channel unreadable)` or `(sub-channel CRC mismatches)`, but a
rip of selected tracks prints only their blocks, so for every other track the
list is the only record, and its silence reads as no pregap. With every search
failed, the list reads `None signalled`.

**On the drive**: section P3 of the closing run ripped track 1 twice; the `-H -E`
log lists nine pregaps and the `-H -W` log eight, without `158 frame pregap in
track 4` (`docs/rig-2026-10-06-5704062/rips/r16deemphoff.log`). That is two of
the 153 filed logs of the reference disc that carry the list; the other is
`docs/rig-2026-09-22-2cce60d/rips/derived-wavpack.log`. Whether track 4's search
failed or returned a pregap of zero, which the list also leaves out, the log
cannot say.

**Recounted 2026-10-13, and that count was short**: 4 of the 211 filed logs
of the reference disc that carry a `Gaps:` list leave track 4 out. The two
above, and two secure re-reads, which rip track 4 and so print its block:
2026-09-05 on `978f9b0`, which the count above missed, and 2026-10-13 on `.22`
(`docs/rig-2026-10-13-200530e/`). Both blocks read `Pregap length: 0 frames`
and `Pregap source: sub-channel (not signalled by TOC)`, where a failed search
reads `Pregap LSN: unknown (...)`, and on `.22` the list would also have
printed `pregap of track 4 unknown (...)`. So **in those two, the search
returned zero**: the sub-channel variation of the next entry, at 158 frames
rather than one. The `.22` rip's cue sheet gives track 4 no `INDEX 00`, where
the same run's whole-disc rip gives `INDEX 00 04:49:20`; no audio byte moves
under the default action. The secure re-reads of 2026-10-07 and 2026-10-12
read 158, so a secure re-read does not always read it as zero; why these two
did is not known. `tools/read-run.py`
reports a pregap one list leaves out, which is how this one was found.

**Two more on 2026-10-16, on `.23`** (`docs/rig-2026-10-16-891c79e/`): 11 of
the run's 13 lists give track 4's 158 frames and two leave it out, the
`derived mp3` rip (tracks 1 and 2) and the secure re-read's securing pass
(track 3). Neither ripped track 4, but neither list prints `pregap of track 4
unknown (...)`, which `.23` would for a failed search, so **both searches
returned zero**. Six filed logs of the reference disc now leave track 4 out.
Platterpus's own script found the same pair, by comparing the run's lists
(their step L1554, `expect-pregaps-agree`, graded `info`). **None on 2026-10-20,
on `.25`** (`docs/rig-2026-10-20-5f1d036/`): all twelve lists give track 4's 158
frames, track 9 reading 94 or 95 as before. **With no drive, before `.22`**: `-l 1` of `tests/fixtures/basic.cue`
printed `None signalled` while the whole-disc rip's track 2 block read
`unknown (sub-channel unreadable)`; from `.22` it prints `pregap of track 2
unknown (sub-channel unreadable)`.

**No audio byte depends on it**: the default action merges a pregap into the
track before it, whose end the TOC already gives. The cue sheet's `INDEX 00` for
that track does, and is the next thing to check. **The fix, not yet made**: a
line in the list for each undetermined pregap, `pregap of track N unknown
(reason)`, and `None signalled` only when every search succeeded. P2 again;
Platterpus renders the list's first line as EAC's `Gap handling` row
(`platterpus@9ecd1147:src/platterpus/parsers/cyanrip_log.py:199-204`), so a
first line that changes is a value they show.

### `track is partially accurately ripped` is said of a track whose bytes are wrong (tally renamed for `.22`)

**Found by Platterpus in round 26's real test** (their lap 5 §B3), and
confirmed here from our filed copy. `docs/rig-2026-09-24-df91ae7/rips/after-cancel.log`
reads track 1 as `EAC CRC32: 0E91CD1A`, with 20 `FIXUP_ATOM`s and `Ripping
errors: 0`. The five other rips of track 1 in that session read `B0D122E7`, each
an exact AccurateRip match. Its v1 and v2 are `not found`, and only
`Accurip 450: 57722DDE (matches Accurip DB, confidence 200, track is partially
accurately ripped)` matched. The footer counts it in `Tracks ripped partially
accurately: 1/14`.

**It is not a one-off, and our own record held the proof for thirteen days.**
`docs/rig-2026-09-11-ddc1e8c/rips/derived-wavpack.log` has the same track 1, the
same `0E91CD1A` and the same `Accurip 450: 57722DDE`, on another build, in
section K2, two rips after the cancel rather than straight after it, where that
session's own J read track 1 correctly. So the drive returned the same wrong bytes twice, and paranoia
accepted them twice. Found by scanning every filed track-1 read, not by memory.
Nothing in this repository mentioned it until now.
**That scan is now a tool**: `tools/cross-rip.py <bundle>` compares every read
of each track across a bundle's cyanrip logs, grouped by disc and read offset,
and names both of these logs. `tests/cross_rip.py` asserts it does.

**What is wrong is the label, not a number.** Every checksum is truthful.
`Accurip 450` covers one sector (`src/checksums.h`), so a match says that sector
is right and says nothing about the other 14,486. *"Partially accurately
ripped"* reads as mostly right, and here the track was wrong. The wording is
upstream's. **Not changed in `.16`**: it is a line Platterpus parses, so the
wording is round 27's, with their answer first. Their side is re-reading by
default and saying what matched.

**Their answer is in, in round 27 lap 2 B1.** Inside the parenthetical they read
only `confidence\s+(\d+)`, and treat confidence ≥ 1 with a non-zero CRC as a
match. So the words can change freely, **provided `confidence N` appears only on
a match**. `Tracks ripped partially accurately: N/M` they match by its exact
label and use only as a cross-check, so renaming that label needs their
both-wordings release first. Their EAC-compatible log's proposed wording is
theirs, under H4.

**Reworded in `.17`, released 2026-09-26 at `e0471f4`.** The match reads `(matches Accurip DB,
confidence N, one frame only; whole-track checksums not found)`: `confidence N`
stays on the match alone, as their condition asks, and `matches Accurip DB` is
kept. No string they match is removed, so nothing of theirs has to ship first.
It is a P2 line, and round 27 lap 4 announced it; their lap 5 accepted it.
`.16` and every log filed before `.17` keep the old tail. The tally label is unchanged: renaming it needs their
both-wordings release first.

**The first `.17` rip to show it on the drive is round 28's Full run**
(`docs/rig-2026-09-28-e0471f4/`): section F read track 3 as `15D16895`, a
wrong read never filed before, and its 450 line reads *"one frame only;
whole-track checksums not found"* (`rips/full-acceptance-angle-bracket.log:245`),
while the footer still says `Tracks ripped partially accurately: 2/14`.

**And 2026-10-04 is the plainest case yet** (`docs/rig-2026-10-04-174a134/`):
`Tracks ripped partially accurately: 6/18` over tracks 12, 13, 14, 15, 17 and
18, five of which were then read five times each with five distinct checksums.
The label calls them partly right, and the record shows they never read the
same way twice.

**The tally is renamed for `.22`, in round 31**: `Tracks matched on one frame
only: N/M`, the same numerator and denominator, as agreed in round 30 (our lap
11 S16, their lap 12 S11). Round 20's order is met: their both-wordings reader,
`platterpus@fd439881`, is an ancestor of their `v0.6.66b1`, a release.
`tests/logrender.c` pins the new wording and refuses the old one.

**Our answer to their EAC-log wording, sent in round 27 lap 4 and accepted in
their lap 5: amend one clause, accept the rest.** They proposed, per track, `Only one frame matched AccurateRip
— rest of track unverified (confidence 200)  [57722DDE]  (AR frame 450)`, and in
the summary `1 track(s) matched AccurateRip on one frame only`. The summary is
accepted as written. **The per-track line says less than was established**: the
450 line is printed only when both whole-track lookups returned −1, compared and
not found (`cyanrip@174a134:src/cyanrip_log.c:594`). *"Unverified"* reads as *not checked*,
which is round 7 H4's own distinction: *"it failed to match the database, and
those are different claims."* And the confidence belongs to the frame that
matched, not to the rest. Proposed: `Only one frame matched AccurateRip
(confidence 200); whole-track checksums not found  [57722DDE]  (AR frame 450)`.

**A second defect was sitting under the same line, and it is fixed.** A 450
lookup that missed fell through to the whole-track checksum
(`crip_find_ar()`, their B1a). See `docs/SETTLED.md`'s upstream section.

### Our gate has four defects, two found by Platterpus's questions, and none was fixed on finding

**Items 1 and 3 FIXED 2026-09-23, before round 25 opened**, by the change that
added `version_refusal()`, `declared_version()` and `C29_FROM_ROUND` to
`tools/release-gate.py`. Every file of a round, ours and inbound, is now read
for its version: one declaring more than we implement refuses the round, naming
the file (C15), and from round 25 a lap declaring less than an earlier lap of
either side refuses it too (C29). Tests
`test_a_peer_lap_above_our_protocol_refuses_the_round` and
`test_a_peer_lap_below_an_earlier_lap_refuses_the_round`, revert-proved one half
at a time. **The C29 boundary is load-bearing, not caution:** moved to 0, it
reopens round 8, whose laps 3–15 of ours declared 1 after their lap 2 declared
2, and the real gate refuses a release. Platterpus's gate already had the C15
half (`platterpus@86f0547:scripts/handshake.py:1920`, `refused_round_files`).

**Item 2's coverage half FIXED the same day; its behaviour was left, on
purpose, until 2026-10-11 (below).**
The meta-check now admits a letter suffix, so C13a is a row it can see. It
turns rows on by the version each block's heading names rather than splitting
once at v3. And it carries `KNOWN_DIVERGENCES`, printed on every run, which
fails if an entry stops being true. C13a is the one entry. **Replaying every
round lap by lap found the premise of "latent" was wrong and the conclusion
right.** Six laps, in rounds 7, 8, 11, 12 and 15, follow the lap at which our
gate first reads the round closed. All six declare `GO`, each the other side's
closing lap, so reopening and staying closed agree on every one. **C13a as
written would refuse all six**, which is why round 25 proposes amending the row
rather than implementing it. Three labels were wrong too.
`test_latest_lap_can_reopen` claimed C13 and built C13a's case. Two ambiguity
tests claimed *"C13 (S2 rule 3)"*. So C13 read as covered three times and had
no test of its own case. It has one now, and removing its claim leaves C13
uncovered. Item 4 remains, below.

**Item 2's behaviour FIXED 2026-10-11, for round 31** (our lap 1 S25 said it
would land before our closing lap). The gate replays each round in one
sequence by declared lap number, ours and theirs, finds where it first became
terminal, and refuses as a file any later lap of either side that declares a
different verdict; the round stays where it was. A later lap of the same
verdict is no transition, so the six laps above are untouched, and every one
of the 27 rounds on the record resolves as before. A lap of theirs counts only
when it declares itself released, as C38 reads one. `KNOWN_DIVERGENCES` is now
empty. Tests `test_a_different_verdict_after_a_close_is_refused_and_the_round_stays_closed`
and `test_a_peer_lap_after_a_close_is_refused_too`, revert-proved one piece at
a time.

**Item 4, and v5's C40 fixture, are written out of the v6 path, 2026-09-23.**
For a file declaring 6, `peer_verdict_resolution` no longer consults the
closing file's `INBOUND-HELD`. The candidate is the newest peer lap in our own
`inbound/`, which is what v6 §5b step 1 says. So no literal
filename is matched. `test_v6_closes_on_a_record_that_can_occur` uses the
fixture a real round produces, with v5 on the same bytes as the control, and
the control does not close. The same change requires `HANDSHAKE-AGREED-CHANGES`
on a v6 `GO` (C44). **Both are live from `643631b`**, where v6 landed and
`PROTOCOL_VERSION` went to 6 with no other change to this code. They apply to a
file declaring 6; the first was round 28 lap 5, once both gates had said in a
lap that they implement it, as v6 §14 asks. Both halves are revert-proved.

**Found 2026-09-22, answering their post-round-23 standing status**
(`docs/handshake/inbound/status-2026-09-22-v0.6.53-c2f43d28.md`, the
**protocol** row). They described two defects in their own gate as *"portable
shapes, so we are telling you rather than checking your tree"*. **Both are in
ours.** That is the compare-do-not-acknowledge rule paying out twice.

1. **A peer lap declaring a protocol we do not implement still decides a
   close.** `tools/release-gate.py` refuses a higher `HANDSHAKE-PROTOCOL` on our
   own laps (`why`, `protocol_ok`). But the inbound loader
   (`load_rounds`, the `peer_latest` block) reads the peer lap's verdict and
   release state without reading its version. Measured: our lap 3 declaring 5,
   their lap 4 declaring **6**, `GO`, released — **our gate closes the round**,
   *"peer GO resolved per v5 §5b from round-30-lap-04.md"*. Refusing rather than
   guessing (C15) applies to the file we wrote and not to the file we act on.
2. **Row C13a has no test, and our gate does the opposite of it.** C13a says a
   lap arriving after a round is terminal is refused as an illegal transition,
   and the round stays closed. The coverage meta-check,
   `test_every_conformance_row_has_a_test()`, collects row IDs with
   `^\| (C\d+) \|`, which cannot match `C13a`. So the row is invisible to the
   check that exists to find uncovered rows. `test_latest_lap_can_reopen()`
   claims `Covers: C13` and asserts that a complete `GO` followed by a `HOLD`
   **reopens** the round. That is v2 behaviour, which v3 removed. Their
   defect was that the coverage check exempted rows by heading; ours is that
   the row pattern drops a row by spelling. Same outcome: a row in force with
   no test.

**Two more, found 2026-09-23 by dry-running round 24's close on a throwaway
record** — our real lap 1, a synthetic lap 2 and a draft lap 3, nothing read
from Platterpus's real lap 2, which is held:

3. **C29 is not applied to peer laps.** A peer lap 2 declaring protocol **4**
   after our lap 1 declared 5 closes the round on our gate. C29 refuses a
   lower version than an earlier lap of the same record. Same root as item 1:
   the inbound loader never reads the peer lap's version at all.
4. **Under v5, C37 matches the peer lap's FILENAME inside our
   `HANDSHAKE-INBOUND-HELD`.** `peer_name in self.inbound_held`, so a closing
   lap that describes the lap — *"your round 24 lap 2 — sha256 …"*, which is
   how every one of our `INBOUND-HELD` lines has been written — is refused with
   *"not named in our HANDSHAKE-INBOUND-HELD"*. Round 23 lap 5 is written that
   way and declared 4, so it never met the check. **Until the gate reads a
   `round N lap L` reference, a v5 closing lap must name `round-NN-lap-LL.md`
   literally.** That is a rule for whoever writes the lap, and a brittleness in
   the gate, not a defect in any lap already sent.

**Why none was fixed on finding.** All four
were latent: no peer lap declared more than 5 or less than an earlier lap, and a
closing lap can name the file. This paragraph also said *"no lap has followed a
closed round"*, which the replay above shows is false: six have, all `GO`.
Items 1 and 3 were fixed on 2026-09-23. Items 2 and 4 waited for v6, on
purpose: item 4 was v5's literal reading of C37, which v6 replaces, and was
written out of the v6 path the same day; item 2's row was proposed for
amendment rather than implementation, because as written it refused those six
laps, and its behaviour was fixed on 2026-10-11 (above).

## Moved from *Open, joint* on 2026-10-21, each landed or decided

### Three agreed protocol changes never reached the spec, and both sides certified v5 as complete — LANDED IN v6, 2026-09-23

**Landed in round 25.** All three are in `docs/handshake/PROTOCOL.md` v6: K1 in
§4a, K2 in §5a, K3 as §5d. So is the agreed-change ledger, §5e, which exists
because of this entry. v6 is byte-identical in both trees (`643631b`,
`platterpus@53b3c04`), and round 25's closing lap is the first to carry the
ledger with every entry named. The history below is kept as the reason.

**Found 2026-09-22 by the pre-round-24 document audit, and it is the most
important thing that audit found.** Round 22 agreed three changes to the shared
protocol and **none of them is in `PROTOCOL.md`**:

| item | agreed where | what it says | in the spec? |
|---|---|---|---|
| **K1** | round 22 lap 1 §0.1, their lap 2 §0.1 *"agreed … with no amendment"* | a lap number is claimed on **release**, not on writing | **no** |
| **K3** | the same two laps | a warning about a **held** lap cannot travel inside it — the one legitimate relay | **no** |
| **K2** | round 21 lap 4 §K, *"needs nothing from round 22 but the shared-file edit"* | `HANDSHAKE-INBOUND-HELD` for sent laps, `HANDSHAKE-INBOUND-OBSERVED` for held ones | **no** — `grep -c INBOUND-OBSERVED docs/handshake/PROTOCOL.md` is `0`, though both sides have declared the field in every lap since |

**How they fell out, and it is a gap between rounds rather than inside one.**
Round 22 lap 1 declared protocol 4 *"deliberately not 5, although §K1 and §K3
below propose the v5 text"* — correctly, because a version bump is something
both sides ship. So the text waited for a v5. Round 23 then drafted v5 from
**its own** §0.1 — the close rule and its readability condition — and its §13
says *"v5 is v4 plus the two clauses round 23 §0.1 named, and nothing else."*
Nobody carried round 22's agreed clauses across. **Platterpus re-derived v5's
diff in their lap 4 §B and confirmed "the two clauses and nothing else"; we
wrote that sentence.** Both sides certified it as complete, accurately, against
the wrong list.

**Round 23's own §0.2 is the same failure one level down**, and the audit found
that too: the condition was *assent, an amendment or a refusal*, Platterpus
assented, and the banner qualifier it agreed was never implemented. **A round
closes on agreement, which is correct — and then the building is left to
memory, and memory does not survive a round boundary.** Nothing in either
tree tracks an agreed change from *agreed* to *landed*.

**What it costs today: nothing that breaks, and something that will.** Both
sides already behave as K1, K2 and K3 say — the rules are practised, just not
written. But a third consumer, or either side in six months, reads the spec, and
the spec is silent on three rules both projects follow. **A practised rule the
spec does not state is the drift the shared spec exists to prevent.**

**Round 24, and it is a proposal, not an edit:** a v6 carrying K1, K2 and K3 —
their text is already agreed, so drafting is transcription — and a mechanism so
this does not recur. The obvious shape is that a closing lap enumerates every
change the round agreed, each with the commit that landed it or `not landed`,
so a close cannot silently leave work behind. **That mechanism is itself a
protocol change and needs their assent**, so it is proposed, not built.

### A cited commit was orphaned by a squash merge and a branch delete — it HAPPENED, and the recovery was luck

**Filed as an event rather than a hazard, because a near miss recorded as a
success is a hazard that comes back.**

**No citation depends on the branch any more, whether it exists or not.**
Platterpus's operator deleted `claude/session-omka9f` on 2026-09-29, after a
re-check found it an ancestor of their `main` with no commits of its own (their
standing status, `platterpus@5a7b2d4:docs/handshake/outbound/platterpusstatus.md:315`),
**and recreated it from `main` the same day** for later work. Read 2026-09-30 with
`git ls-remote`: its tip `fdaa50bd` is an ancestor of their `main` at `58ad83db`,
with no commits of its own. So whether the branch exists is no longer a fact any
citation here rests on.
**Checked here rather than taken on that**, in a full clone of their tree: the
four commits this entry names, `b5af9bec`, `19c8ad20`, `e8a47562` and
`9cc23eab`, and the three more their `TASKS.md` lists beside them, `81ca989`,
`c394229` and `926dcb3`, are each an ancestor of their `main` at `5a7b2d4`, so
every citation of them resolves through `main`. Wider, at our `26e31a5`: of the
1,947 distinct hex tokens in our tree, 165 resolve as their commits, none as
ours too, and all 165 are ancestors of that `main`. **One sentence of theirs
did not match**: `TASKS.md:692-695` at `5a7b2d4` said those seven resolve in
neither tree, and all seven resolve in theirs. Our round 29 lap 3 S35 said so,
and their lap 4 S3–S4 corrected the row (`platterpus@b56d0b17`). The paragraphs below are the
record of the entry before the delete, and stand as written.

Round 23 lap 3 §D2 warned Platterpus that their work reaches `main` by **squash
merge**, so a commit on their working branch never becomes an ancestor of
anything there; delete the branch and routine `git gc` **destroys** it rather
than hiding it, breaking any citation that names it. Their lap 4 accepted the
reasoning, checked it rather than taking it, and recorded *"`claude/session-omka9f`
will not be deleted"* in their `TASKS.md`.

**The PR squash-merged and the branch was deleted four minutes later.**
`b5af9bec` and `19c8ad20` — the two commits round 23's citations name, one of
them in **our lap 3, which was already sent and immutable** — became unreachable
on their remote. They were recovered because a session clone still held the
objects and the branch was pushed back at the same tip, and because GitHub had
not run `gc` in the interval. Verified here afterwards against their remote:
both are reachable as ancestors of `refs/heads/claude/session-omka9f`, now at
`e8a47562`. Neither is directly fetchable by SHA, which is GitHub refusing
arbitrary-SHA fetches rather than evidence of absence — **reachability through
the ref is the whole of what makes them resolvable, and it is exactly what a
second delete removes.**

**THE FIRST DIAGNOSIS WAS WRONG, WE ADOPTED IT, AND IT IS CORRECTED HERE.**
Platterpus first reported that a human had clicked *delete branch on merge*
despite a warning that was in the PR body twice, in bold, at the top, and in two
separate operator messages — and offered the memorable framing that *the delete
is a button that appears after the merge succeeds, when no PR text is on
screen.* **That account was filed in this entry verbatim and it is false.** They
retracted it in their post-round-23 status: the cause was the repository's
**"Automatically delete head branches" setting**, proven rather than supposed —
a merge performed over the API, with **no human present**, deleted the branch
again. The setting is now off, which is the durable fix, and the branch is
restored and will stay.

**This is `separate the finding from the diagnosis` failing in the entry filed
about a diagnosis failure.** The finding — two cited commits orphaned, one named
by a sent lap — was right and is unchanged. The cause was not. And the remedy
the wrong cause implies, *remind the human not to click it*, **would have
changed nothing**, which is exactly why this file says to reproduce a cause
before adopting its remedy. We did not; we adopted it inside the same commit
that praised the reasoning.

**The corrected lesson is stronger than the one it replaces.** A warning was
written, escalated, and re-escalated at an actor who was never in the loop.
Their words still hold and now bite harder: **a comment where a check belongs is
not a fix, arriving through a UI instead of through code** — and *the response
each time the risk came up was to write the warning more emphatically rather
than notice that emphasis was not the failing axis.* The axis was not emphasis
and it was not the reader either. **It was a repository setting, and no amount
of prose addressed to anybody could reach it.**

**Verified here rather than taken on the correction.** Both `b5af9bec` and
`19c8ad20` are reachable as ancestors of `refs/heads/claude/session-omka9f`,
now at `9cc23eab`, on their remote. A first pass of that check said NOT
reachable and was wrong — it scanned stale `refs/remotes/origin/*` without
fetching the branch, which is this file's own *`git branch -r` is a cache, not
the remote* rule biting in the middle of verifying somebody else's claim.

**We have the same shape, and looking for it is the point of filing this.**
`CLAUDE.md` carried *"never push a topic branch — the deletion is not
available to us"* until 2026-10-12, as prose backed by an observed `HTTP 403`,
with an explicit note that there is deliberately no test because the only check
would reach the network; it now says to push one only to open its pull request,
and still records branch delete as `HTTP 403`.
That reasoning still holds and the exposure is still real: **the rule holds here
because the proxy refuses, not because anything of ours checks.** Prose plus an
accident of the environment is the same class as a bolded PR body; it just
happens to have a stronger accident behind it.

**The general fix is Platterpus's and it is a round-24 item: the sha256 is the
anchor, the commit is a fetch hint.** Both sides already declare a lap's hash and
both reproduce it before filing. A content hash cannot be pruned. If a citation
names the hash first, a pruned ref degrades it from *fetchable* to *verifiable*
instead of to nothing. Round 23 lap 5 adopts it for its own citations a round
early; settling it in the spec is joined with §D1's two meanings of
`HANDSHAKE-FROM-COMMIT`, because both are the same question — **what does a
citation name?**

**And our lap 3's citation of `b5af9bec` cannot be re-anchored**, because lap 3
is sent. That is the argument for the proposal rather than an objection to it:
the one artifact that could not be fixed is the one naming a commit and not a
hash. Lap 3 does declare lap 2's sha256 and byte count in
`HANDSHAKE-INBOUND-HELD`, so it degrades to verifiable — which is precisely the
property the proposal would make the rule.

### The close condition cannot be satisfied by the side that speaks first — ADOPTED AS v5 §5b, AND AS WRITTEN IT CANNOT DO THAT

**Status 2026-09-22, evening: in the spec, built in both gates, and unable to
save the lap it was adopted to save.** Round 23 adopted `PROTOCOL.md` v5,
byte-identical in both trees, with this as §5b and Platterpus's readability
condition as §5c. Our gate implements it, keyed on each file's declared
version. Theirs implements it from `platterpus@c2f43d28` (21:30Z by commit
date). At `52b44282` it still implemented 4, and this entry said so twelve
minutes before it stopped being true.

**The defect is in the text, and we drafted it.** Step 1 and row C37 require
the candidate peer lap to be one the closing file *declares* in its own
`HANDSHAKE-INBOUND-HELD`. The peer lap that would make a transcription lap
unnecessary is always written after that file, so it can never be declared in
it, and step 3 — *"the whole of v5's saving"* — cannot fire on any real
record. Platterpus found it from the other end: C40 is unreachable under that
reading, so they read *"enumerated"* as enumerated by the gate when it
decides. Their post-round-23 status asks whether ours differs. **It does**,
measured 2026-09-22 with our own loader:

| record | our gate |
|---|---|
| our lap 3 holds their lap 2; their lap 4 (`GO`, released) arrives later | **not closed** — *"round-30-lap-04.md is not named in our HANDSHAKE-INBOUND-HELD"* |
| the same, except lap 3 declares it holds lap 4 | closed — the only way C40 fires, and the lap could not have existed when lap 3 was written |

**And our test proves the code, not the rule.** `test_v5_close_rule_and_the_v4_control`
passes on the second record: `_v5_ours()` defaults to
`held="round-30-lap-04.md"` (`tests/release_gate.py:3182`). A fixture that
cannot occur made the one mechanism v5 exists for look exercised.

**The remedy is v6 wording, not a gate edit by one side.** Their reading is
the one under which §5b does what it says, and C42 already makes the gate print
the lap it resolved from, so audit does not depend on the closing file's
declaration. Proposed in round 24 lap 1, and landed in round 25 as v6 §5b
step 1 and C37. **The divergence is gone.** Our gate reads a file
declaring 6 the decision-time way, and laps declare 6 from round 28 lap 5 on.
Round 25 closed on our gate by ordinary transcription, not by step 3; round 28
closed under §5b step 3 on Platterpus's lap 9, which was this entry's exit
condition, and rounds 30 and 31 closed the same way.


`PROTOCOL.md` §5 requires `HANDSHAKE-PEER-VERDICT: GO`, *"transcribed from the
file they actually sent"*, in each side's own newest lap. **The side that speaks
last can do that; the side that speaks first cannot**, because its file was
written before the other side's answer existed. So a round is mutually closeable
only if the first speaker writes one more lap — which makes the other side the
first speaker.

Not hypothetical and not new. `SETTLED.md` row 102 records it from **round 17**,
where we spoke last and Platterpus's `--status` held the round `OPEN`; they filed
their acceptance as a `verified/` record. **Round 22 is the first time they spoke
last**, and we could not use that escape: `tools/release-gate.py
--release-gate` refused while any round was open (until protocol 8), so an
unclosed round 22 blocked `+platterpus.14` permanently. Our lap 5 is that extra lap, and it closes the
round rather than reopening anything.

Measured on our side rather than assumed: with their lap 4 filed,
`stale_peer_verdict` **is** satisfied and `closed()` still returns False one line
earlier, on `self.peer_verdict not in CLOSING` — our own lap 3's cell, correctly
declaring `OPEN`.

**This is a condition gated on a consequence of itself**, the family Platterpus's
round-22 lap 4 C1 named, and the third instance in that round alone: §6a's
test-pin deadlock, their verdict-note circularity, and this. Their formulation is
the one to keep — *state what must be TRUE, never what must have HAPPENED* — and
`HANDSHAKE-PEER-VERDICT` is a has-happened condition in a must-be-true field.

**Proposed for v5 in lap 5 §H1 and deliberately not implemented.** The close rule
is shared, and relaxing a match rule on one side is how two gates come to
disagree about whether a round is closed. The proposal: read the peer verdict
from the newest peer lap the writer holds and has enumerated in
`HANDSHAKE-INBOUND-HELD`, keeping `HANDSHAKE-PEER-VERDICT` as the declaration and
cross-checking it against that — which is what `stale_peer_verdict` already does
in one direction. Needs a `HANDSHAKE-PROTOCOL` bump shipped to both sides before
either gate implements it.

**ASSENTED 2026-09-21, WITH ONE CONDITION, AND THE CONDITION IS A HOLE IN THE
PROPOSAL.** Recorded in their standing status — filed byte-exact at
`docs/handshake/inbound/status-2026-09-21-v0.6.52.md`, sha256
`9c0a37507f2d1839…`, 38,037 bytes, read at `platterpus@a0aed36`, under
*"ASSENT — your §H1 `PROTOCOL.md` v5 close-rule proposal, with one condition"*.
It is in a standing status rather than a lap because **round 23 is ours to open
under §1a**, so their next lap cannot exist yet. They verified our diagnosis in
our source before assenting — `release-gate.py:727-732` and `:552-556`, both
reproducing at `cyanrip@b293f32` — and changed nothing in their gate.

**The condition: the released-for-reading check must be NORMATIVE in the spec,
not one implementation's habit.** Their reasoning, and it is correct: the
proposal moves the verdict from *their transcription of our lap* to *our lap
itself*, and both repositories are public — so under v5 a side can read a lap
**before its operator has released it**, and *"acting on a held lap would make
your draft our decision."* Today `HANDSHAKE-READY-TO-READ` is what stops that,
and today it is a property of each gate rather than of the spec; under v5 it
becomes **the only thing between "we can see it" and "we may act on it."**

So v5 must state that a lap read for its verdict has to declare
`HANDSHAKE-READY-TO-READ: yes`, and that an unreleased or undeclared lap is
**not** a readable verdict — fail-closed, naming which lap is being held. They
are not attached to the drafting, only to it being in the shared spec before
either gate changes.

**Accepted, and it is a real gap in what we proposed, not a formality.** Our own
gate already refuses a held lap (`closed()` returns False on `self.held`, which
is why the round-22 gate reported lap 5's verdict as a draft) — and we wrote the
proposal without noticing that it **promotes that check from a safety net to the
load-bearing element**. The publishing-is-not-sending distinction did work four
times across rounds 21 and 22, including on our own lap 5, and we still missed
it here. Their addition goes into round 23's lap 1 as part of the v5 clause.

### A HELD lap's draft verdict reaches the compiled `Handshake:` line — AGREED IN ROUND 23, BUILT 2026-09-23

**Built 2026-09-23 in `tools/gen-handshake-state.py`, as `DRAFT_QUALIFIER`.**
When the newest lap is held, the open state now ends ` (draft — lap not released
for reading)`. Closed and released states are unchanged. The test,
`test_a_held_lap_banner_says_it_is_a_draft`, reads the expected string out of
Platterpus's round 23 lap 2 table, the shape they ran through their parser,
rather than retyping it. It is revert-proved. **It first shipped in
`+platterpus.15`** (`df91ae7`). The history below is kept because it is why the ledger in v6 §5e
exists.

**Status 2026-09-22, found by the pre-round-24 document audit: the change was
agreed and nobody implemented it.** Round 23 §0.2 asked for a qualifier —
`round N lap L OPEN, verdict GO (draft — lap not released for reading)` — and
Platterpus assented in their lap 2 §C.2 after running four banner shapes
through their real parser and their real classifier, both safe, ending *"Go
ahead and land it."* Our laps 3 and 5 correctly say the **condition** closed,
since the condition was assent, an amendment or a refusal. **But
`grep -rn "not released for reading" src/ tools/gen-handshake-state.py` returns
nothing**: the change itself was never written, and `+platterpus.14`, cut the
same day, does not carry it.

**A condition satisfied is not a change shipped, and the audit is the only thing
that noticed.** Nothing in either gate checks that an agreed change landed; the
round closed on the agreement, which is correct, and the building was left to
memory. It is authorised by round 23 and is ours to build; the next release is
the first that can carry it, the way `.14` carried round 22's. **Nothing is
written for that release yet**, so that is a plan, not a fact. Round 24's
opening lap should say the change was missed.


`tools/gen-handshake-state.py` takes `latest.verdict` verbatim, so with lap 5
published and `HANDSHAKE-READY-TO-READ: no` the banner reads `round 22 lap 5
OPEN, verdict GO` — a verdict the release gate itself declines to act on,
reporting *"its verdict is a draft"*. A held lap may still be revised; the banner
publishes its verdict as though it were settled.

**Pre-existing, not introduced by lap 5.** Checked by generating the state in a
throwaway worktree at `623251c`, where lap 3 was held: it produced `round 22 lap
3 OPEN, verdict GO` the same way. Every held lap since the field existed has done
this.

**Bounded, and that is why it is not urgent.** `HANDSHAKE_RELEASED` is separately
`0` for any open round, so every log such a build writes also says **`NOT a
released build`**, and a *released* build cannot carry a draft verdict at all —
a release needs a closed round, and the gate refuses to close on a held lap. So
the exposure is unreleased builds, which already disclaim themselves on the line
below.

**The fix is contract surface, which is why it waits.** `Handshake:` is a line a
consumer parses, so adding a qualifier to its value vocabulary is a handshake
matter and not a drive-by reword. Round 23, with the v5 item above.

### `Rip completed:` and `Ripping errors:` can now disagree on their face

`Rip completed:  yes (2 of 3 tracks)` beside `Ripping errors: 2`. Both are
true — the rip loop ran to completion and the encoders failed, which are two
facts — and before round 21 they agreed by both being wrong.

**ASKED, AND THEY RULED: LEAVE IT ALONE.** Round 21 lap 1 put it to Platterpus —
whether the footer should distinguish *the loop finished* from *the run produced
what it claimed*. Their round-21 lap 2 §0.2, released 2026-09-16 and filed at
`docs/handshake/inbound/round-21-lap-02.md`, is a **refusal to change the field**,
and our lap 1 had already said a refusal closes that condition as cleanly as an
assent. `Ripping errors: 2` beside `Rip completed:  yes (2 of 3 tracks)` is
**correct output and stays**. Three reasons, each checked here rather than only
read:

1. **Their parser's tri-state depends on `yes` meaning the loop reached its own
   end.** `None` is an absent footer — what a killed rip looks like — and must
   never read as `False`. A stricter `yes` would collapse *ran to the end and
   failed* into *stopped early*, and that distinction is the **attested
   truncation** finding we root-caused in round 14 lap 7 §B2: the completion
   footer twenty-four `goto end` sites can skip, signed anyway by
   `cyanrip_log_end()`. Tightening the field would spend a diagnosis that cost a
   round to find.
2. **The `(N of M)` denominator is the disc, not the selection** — confirmed in
   our own source at `cyanrip_log.c:917`, which prints `tracks_ripped` against
   the disc's track count, so a narrowed `Tracks to rip:` produces the same
   shape. `done < total` is therefore the ordinary form of a partial rip and can
   never be a failure signal. They measured it on seven rips in their 2026-09-03
   bundle, and an earlier version of their own handler asserted `done == total`
   and would have failed all five partial-rip sites it was added to.
3. **The floor that works is `done == len(tracks)`** — the record agreeing with
   itself, disc- and selection-independent, already in their tree, and needing
   nothing from us.

They also read `rig_check.py` before answering, which we asked for: it consumes
`rip_completed` only as context for `Interrupted at:`, tri-state, `INFO`-only,
and the change does not perturb it.

**So this entry stays open as a description and is closed as a question.** It is
not a defect and there is nothing to fix; it is recorded because the two states
*"nobody asked"* and *"asked, and they said leave it"* are different claims, and
this is now firmly the second.

## Retired 2026-09-28: the five Platterpus defects that blocked round 8

This section was *"Open, theirs — tracked here only because it blocks us"*,
five rows from `docs/handshake/round-08-lap-07.md` §0b and §H. None has blocked
anything since round 8 closed. Platterpus's round 28 lap 6 S8 and S9 asked us to
retire the first four as fixed and to read the fifth as their guard. **Read in
their tree at `platterpus@764c3e7`, row by row, not taken on their word except
where it says so:**

| what the row said | now |
|---|---|
| a duplicate `drive changed` restarts disc info, and the teardown SIGKILLs an in-flight ripper (`J11`) | **fixed**: the picker emits `drive_changed` only when the device actually changed (`src/platterpus/ui/drive_picker.py:216`) |
| a refused command leaves the previous result live, so the next assertion grades the wrong invocation | **fixed at its root**: every `cyanrip` step clears the last result first, before anything can refuse it (`src/platterpus/uiscript/runner.py:1588-1599`) |
| `wait-for-rip` returns `ok` after `rip` failed | **taken on their S8, not re-read**: we did not find the code path |
| the script language cannot express a literal `"` | **fixed**: the tokeniser unescapes `\"` in a quoted run (`src/platterpus/uiscript/script.py:109`) |
| the `-t` guard blocks a defect fixed in round 7 lap 32 | **their guard working**: it refuses a malformed `-t` before it reaches any build, and says which builds it protects (`src/platterpus/adapters/cyanrip_backend.py:1456-1463`) |
