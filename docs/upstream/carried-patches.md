# What this fork carries over upstream

Made on 2026-11-16 for `docs/OPEN-ITEMS.md` US-18. It answers P7 of
`docs/handshake/PROPOSAL-operator-seam-automation.md` (the patches we carry,
*"each with a retirement condition: landed upstream, superseded, or no longer
needed"*) and §7 of `docs/history/upstream-audit-2026-08-21-prs-and-forks.md`
(an index of what upstream could take). It has four lists: code carried from
upstream pull requests upstream has not merged (§1), our fixes to defects
upstream still has (§2), our workarounds for the libraries we link (§3), and
what is ours by design (§4). A retirement condition names the event that removes
a row and how that event is noticed.

| | |
|---|---|
| upstream | `origin/master` at `648b1dd` (0.9.4-rc3). On 2026-11-16, `git ls-remote` on upstream's repository returned the same commit for `refs/heads/master` |
| ours | `origin/platterpus-fork` at `6cd8b382` (0.9.4-rc3+platterpus.32) |
| merge base | `648b1dd`: 0 commits inbound and 2,185 ours. 2,061 of ours are not merges, and 262 of those touch `src/` or `meson.build` |
| `src/`, `meson.build` | 39 files, +11,297 −586 |
| authors | All 2,061 non-merge commits are authored `Claude`, so third-party code arrives only as a carry (§1). Carries are found by commit message and in `docs/`, not by author |

How to re-check it:

```sh
git fetch origin
git rev-parse --short origin/master origin/platterpus-fork
git merge-base origin/master origin/platterpus-fork
tools/upstream-delta.py --fork origin/platterpus-fork --upstream origin/master
git diff --shortstat origin/master origin/platterpus-fork -- src/ meson.build
git log --no-merges --format=%an origin/master..origin/platterpus-fork | sort | uniq -c
git log --oneline -i -E --grep='PR #1[0-9]{2}' origin/master..origin/platterpus-fork
tools/check-settled.py   # every row, some need build/; its upstream section re-checks §1's first row and §2's reports 1 to 31
```

§1's pull-request heads come from `git ls-remote` on upstream's repository
(`refs/pull/N/head`), fetched into a scratch bare repository, never into this
clone. `tools/upstream-delta.py` printed no CLI section, because it was given no
binaries, so §4's options were read from the two option tables, not measured.

## 1. Carried from upstream's unmerged pull requests

Each of these is absent from `origin/master` at `648b1dd`. Upstream's tracker
cannot be read from this session, so this file does not establish whether a pull
request is open or closed.

| Patch | Upstream pull request, head on 2026-11-16 | Our commits | Files | Retire when |
|---|---|---|---|---|
| Pregap detection from the Q sub-channel, with three review fixes: the failure sentinel, a leak, and `assert()` on I/O (`docs/pregap-carry.md`) | 115, `f22c3d3`, committed 2025-11-28 and unchanged since the carry | `aaa08923` is the carry. Follow-ups: `ec406acc`, `12127d2d`, `759606d0`, `e23a4c76`, and `316682e8`, which places each frame by its own address. Built on it: `9e1784ef` (ISRC from Q frames) and `8726bd3a` (`Pregap search:`) | `src/pregap.c`, `src/pregap.h`, the call sites in `src/cyanrip_main.c` and `src/cyanrip_log.c`, `src/meson.build`, `tests/subq.c` | Upstream's master gains `src/pregap.c`, through 115 or through 153 (below), and `docs/SETTLED.md`'s row `! git ls-tree --name-only $r src/ \| grep -q pregap` fails. Then diff ours against theirs. Ours has diverged well past 115, so retiring it is a merge, not a deletion, and every `Pregap …` log line is handshake material |
| The raw-binary Q sub-channel quirk: re-encode to BCD and re-check the CRC; an all-zero CRC is invalid. Only the algorithm is carried, not 153's restructure | 153, as it stood in round 5 (this file does not record that head) | `becbe4a4` | `src/pregap.c`, `tests/subq.c`, `tests/meson.build` | 153 merges; it retires with the row above. If 153 drops the quirk, this row stays ours, to report upstream |
| ebur128's sample peak, `ebur128=peak=true+sample`. **Not carried from the pull request**: we made the same change independently, so this row is a convergence | 116, `d2383a6`; its `src/cyanrip_encode.c:389` has `+sample` | `d559cbcc` (2026-07-31). `f750890e` cross-checks it (`Sample peak disagreement:`) | `src/cyanrip_encode.c` | Upstream's master carries `+sample`. Today its `src/cyanrip_encode.c:466` does not, and `git show origin/master:src/cyanrip_encode.c \| grep -c 'peak=true+sample'` prints 0. No `SETTLED.md` row checks it yet |

**Upstream pull request 153 has moved since the audit.** The audit recorded its
last commit as 2026-08-20 and said *"This one needs re-checking when it
moves"*. Its head is now `ca3ab44`, committed 2026-11-10. It is 20 commits on
`648b1dd`: one by UltraFuzzy (`0b94beb`, *"Add pregap detection for physical
CDs"*) and 19 by a second contributor. Three subjects match work we did on our
own: placing the pregap by its Q frame's absolute time (`e9d3b41`; ours
`316682e8`), reporting the search in the log (`17e02e8`; ours `8726bd3a`), and
reading raw P-W where the drive can (`2a5c437`; open here as US-12). Its
`src/meson.build` requires libcdio `>= 2.3.0` on macOS and `>= 2.0` elsewhere.
It reads through `cdio_read_audio_sectors_sub()` where libcdio has it, and its
macOS reader still calls `cdio_get_device_fd()`. We recorded that function as
absent from libcdio 2.1.0 (`docs/pregap-carry.md`), so it still blocks 153 at
our floor, `>= 2.1.0` everywhere (`src/meson.build:108`), though not at 153's.
**153 against our search, read in its code at `ca3ab44` on 2026-11-16, not
built or run.** It does not supersede the first row.

- **Equivalent:** 115's three review fixes (the failure sentinel, the leak, no
  `assert` on I/O), the track-address guard, the CRC (its `av_crc` matched ours
  on 2,000,000 random buffers), track 1's lead-in, and the raw-binary quirk.
- **Different:** the quirk is remembered for the whole disc, not per search;
  a frame is placed by its own address only when both bounds agree, so the
  subject that matches our `316682e8` is not its mechanism; its log has no
  `Pregap source:` and no read counts, and reports a failure only under
  `Gaps:`; its retries are 5 per sector and 100 per track, with no escalation
  to 200; and its macOS reader needs libcdio 2.3.0.
- **Ours, not in 153:** the zero-length pregap filter (`12127d2d`), the second
  search, and the ISRC read.
- **153's, not ours:** a test of the frame's index, raw P-W reads (US-12),
  one-bit repair of a damaged frame, frames accepted by position on a drive
  that gives no CRC, a data-track guard, and two sectors to confirm "no
  pregap".

`docs/pregap-carry.md` called 153 a later evolution of 115 *"by the same
author"*; at `ca3ab44` that holds for one commit in twenty, and its dated
correction says so.

**Not carried:** 153's restructure (`subq_read*.c`), for the libcdio floor
above; 127, a single cosmetic string (audit §3); and `-J` (upstream pull request
128), which is upstream's own `ca7e830c`, an ancestor of `958e1ad` where the
fork first diverged, so none of it is ours.

**Correction to the 2026-08-21 audit, made 2026-11-16.** Its §3 says `-J` was
"independently implemented here", its §4 counts `--cue-only` as ours, both
ahead of upstream and convergent with it, and its §7 lists it to offer
upstream. None of that holds. `-J` is upstream's `ca7e830c`, committed
2026-07-12, whose message says it reimplements upstream pull request 128 and
closes it. It is an ancestor of `958e1ad`, the upstream commit our first
commit `d559cbcc` (2026-07-31) was made on, and of every upstream `master`
our mirror has held since (`f8ebf48`, `b40c1f0`, `7dbe56a`, `648b1dd`). So
upstream had `-J` before the fork had a commit, and on the audit's day. No
commit of ours added it; ours touch it only later (`81eedbf8`, `ed50558d`).

## 2. Fixes upstream could take

The reports are in `docs/upstream/defect-reports.md`; report 8 is
`docs/upstream-cachemodel-report.md`. Reports 1 to 33 are rendered for upstream's
tracker in `docs/upstream/issues-to-file.md`. The operator says 1 to 23 were filed on
2026-10-16 as upstream issue 167; that is relayed, not read. Reports 24 to 33 are
drafted and not filed (UP-1, OW-8). Reports 1 to 28 had a check row in
`docs/SETTLED.md`'s upstream section when this list was made, and all of that
section's rows passed against `648b1dd` on 2026-11-16; 29 to 31 gained theirs
the same day, each run against upstream's tree and ours, 32 its own
the same day, and 33 its own on 2026-11-17.

**Retire when** a report's check fails against a synced `origin/master`: upstream
has changed that code. At that sync, read upstream's fix, keep one, and delete
the row.

| # | Defect in upstream | Our fix |
|---|---|---|
| | **Stopping, signals and the footer** | |
| 1 | The signal handler calls `cyanrip_log()`, which is not async-signal-safe | `20c2f77` |
| 2 | SIGTERM is not handled | `20c2f77` |
| 3 | `cyanrip_log_finish_report()` sits above `end:`, so every `goto end` skips it | `4cfbe4f` |
| 16 | A failed track ends a rip of every track silently, and the album is finalised over it | `c1e1ab1` |
| 17 | A stopped `-f` search is retried with a larger radius | `aa1f067` |
| 23 | Three start-up failures return without tearing the context down | `3f0e161`, `72975de`, `a79ac9e` |
| 30 | A media change returns `EINVAL`, so the log says `Error ripping: Invalid argument` (`src/cyanrip_main.c:904-905`, `:1075-1076` at `648b1dd`) | `30f16465` |
| | **The audio and its tags** | |
| 4 | The filter graph is a ternary cascade, so `-H` discards de-emphasis | `b866900` |
| 5 | `(deemphasis applied)` is printed from the settings, not from what happened | `b866900` |
| 8 | A disc image at any paranoia level above 0 returns corrupted audio with `Ripping errors: 0`: the cache model is 1 sector | `22de22fe` (16 sectors) |
| 9 | `-r` reaches libcdio-paranoia unrounded, and `-r 3` never returns on a bad sector | `2af669e` |
| 10 | `media` is tagged from the `-H` setting, so every `-H` rip says HDCD | `ed4a377` |
| 15 | A track's success line ignores paranoia's skips and a `-Z` repeat limit | `e5a0897`, `4529810` |
| | **AccurateRip** | |
| 11 | The tally counts a track whose read was interrupted | `f26668b` |
| 12 | A 450 lookup falls through to the whole-track checksum on a miss | `10f36fe` |
| 13 | The disc status can never read `mismatch` | `64642db` |
| 14 | A one-frame entry under the threshold is logged as `(not found)` | `b1857d6` |
| 18 | The footer can count a one-frame match the track's lines never printed | `8ab9a8d` |
| 26 | The tally divides by a count that includes data tracks | `779549a` |
| | **Arguments, names and paths** | |
| 6 | A bare apostrophe in `-a` or `-t` swallows every later field | `c59dea3` |
| 7 | An invalid UTF-8 byte truncates a name, and can make `-D` absolute | `c3482b0` |
| 24 | An argument that is only its separator crashes with no message | `58f5151` |
| 25 | A number past `INT_MAX` wraps and is used | `716a99b` |
| 28 | A path over 1,003 bytes is cut there, extension and all | `cfd738e` |
| | **What the log says** | |
| 27 | A value the log echoes can start a line of its own | `46cec2a` |
| 29 | `C2 errors: %s by drive` is printed from libcdio's capability bit (`src/cyanrip_log.c:275` at `648b1dd`) | `372706fe` |
| 31 | `Embedded cover art:` names what was asked for, not what was written (`src/cyanrip_log.c:230-233` at `648b1dd`) | `443cbeb9` |
| | **Platforms, and `-Y`** | |
| 19 | A disc image is taken for a drive with libcdio 2.3.0 or later | `faec396` |
| 20 | `-Y` on a directory overflows a signed length | `72975de` |
| 21 | A failed read in `-Y` is reported as a log with no checksum | `d109c56` |
| 22 | The paranoia counters are printed with `%lu` from `uint64_t` | `09492a5` |

**Fixed here, still present at `648b1dd`, and not drafted.** Each row was read
from source at `648b1dd` for this file and was not run on upstream's build. They
are candidates for reports 32 and up. None has a `SETTLED.md` row, so none has
an automatic retirement trigger.

| Defect in upstream, where at `648b1dd` | Our fix |
|---|---|
| `-Z` keeps repeating after a stop. After the read loop's `break` (`src/cyanrip_main.c:1105-1108`), nothing checks `quit_now` before `goto repeat_ripping` (`:1211`). Named in `docs/upstream/sync-2026-08-18-rc2.md` §10.4, and fixed in the same commit as reports 1 and 2 | `20c2f77` |
| The FIFO's three `pthread_cond_wait()` calls are guarded by `if`, not `while`, so a spurious wakeup pops an empty queue (`src/fifo_template.c:125-135`, `:164-173`, `:201-203`) | `9091540e` |
| `-t` steps past an `=` it never checked for, so `-t 1` reads past the end of argv into the tags and the log (`src/cyanrip_main.c:2119-2133`). The fix's commit message records this measured on our build before the fix | `3923deec` |
| `-s` accepts the full `int32` range, and `INT32_MIN` reaches undefined behaviour (`src/cyanrip_main.c:1529`, `src/cyanrip_log.c:261-262`) | `14bb6a2d` |
| `dev_path` is `strdup()`ed (`src/cyanrip_main.c:1653-1654`), and then 20 `return 1;` refusals come before `cyanrip_ctx_init()` (`:1921`). It is freed only in `cyanrip_ctx_end()` (`:137`), so every refusal leaks it | `830fc59a` |
| A cover packet's `av_packet_clone()` is never checked. `crip_save_art()` also writes the packet a second time after freeing it: a flush whose result replaces the first write's (`src/coverart.c:86-94`, `src/cyanrip_encode.c:955-957`) | `f0dd9637` |
| The log and the CUE sheet are fully buffered: `fopen()` at `src/cyanrip_log.c:418` and no `setvbuf()` in `src/`. A killed rip loses their tails, which compounds report 2 | `6bbd29d1` |

**Additions upstream could take.** None fixes a defect, and whether upstream
wants any is unknown; the audit's §7 named the first three. The stall watchdog
(`src/stall_watchdog.c`, `--stall-secs`, `ed701c64`). libcdio's messages routed
into the log, still terminating where libcdio would (`crip_cdio_log_handler()`,
`81eedbf8`); upstream's `src/` has no `cdio_log_set_handler`. genopt's messages
routed into the log by defining `GEN_OPT_LOG` (`81eedbf8`), where upstream's
`src/genopt.h:84-95` `vprintf()`s even its errors to stdout; here the route also
feeds the diagnostics record (§4). And `-V` accepted again for `--version` (`e1d800ef`).

**Fixed upstream as well, independently, and retired:** `catalognumber` (ours
`72080ca`, theirs `52fbc89`); AccurateRip replies checked before use (ours
`36385d9c`; theirs `76dcd5d`, whose cover-art half we took); a non-zero exit on refusing to rip
without an offset or when `-f` finds none (theirs `1689e84`); `Duration:` from
`nb_samples` (theirs `7ba4a3f`). The fork fixed the last three first
(`docs/upstream/sync-2026-10-12-rc3.md` §1h, §1i). `-Y` was always upstream's.

## 3. Workarounds for the libraries we link

From `docs/KNOWN-ISSUES.md`, *Known external bugs worked around here*. Our
floors are libcdio `>= 2.1.0` and libcdio-paranoia `>= 10.2` (`src/meson.build:108-109`).

| Library defect | Our workaround | Retire when |
|---|---|---|
| paranoia checks the per-frame retry limit only at multiples of 5 | `crip_frame_retry_limit()`, `2af669e` (report 9) | a paranoia release we require checks every retry |
| paranoia at `-P 0` never returns on an unreadable sector | `crip_read_audio_salvaging()`, `c57b5963`. Upstream takes the same `PARANOIA_MODE_DISABLE` path (`src/cyanrip_main.c:145`), so it is inferred to have this defect; not run | paranoia fixes the disabled-mode skip |
| paranoia's cache model doubles as its read chunk | 16 sectors on images, `22de22fe` (report 8) | paranoia separates the two, or upstream takes report 8 |
| libcdio's default log handler `exit()`s and `abort()`s inside a library call | `crip_cdio_log_handler()`, `81eedbf8` | not by a library fix: the handler must keep terminating, and it exists to route the messages |
| `mmc_get_disctype()` never reads the last profile descriptor | `crip_current_profile_parse()` in `src/drive_caps.c`, `571051e5` | a libcdio release fixes the bound, which is unchanged through 2.4.0 and master `68ea374` |
| `cdio_get_device_fd()` is absent from libcdio 2.1.0 | `src/pregap.c`'s copied private structs, macOS only | our macOS floor reaches a release that has it (see 153 in §1) |
| The CDRDAO driver opens a `.toc`'s `FILE` relative to the working directory | the tests set `cwd=` (`tests/rip_images.py`); nothing in `src/` | libcdio opens the resolved path |

## 4. Ours by design, not for upstream

Most of this serves one consumer, Platterpus, under a protocol upstream is not
party to, which is why none of it is offered (inferred from the design;
`docs/OWNERSHIP.md` and `docs/handshake/PROTOCOL.md` govern).

- **Fork identity.** `PROJECT_FORK_ID` `platterpus-fork` (`meson.build:53`) is
  in the banner and every log's first line; the version is upstream's plus
  `+platterpus.N`.
- **The handshake.** `docs/handshake/` (339 files), and the lap state that
  `tools/gen-handshake-state.py` compiles in, printed as `Handshake:` beside
  `Consumer:` from `--consumer`.
- **The diagnostics record.** `src/diagnostics.c`, written under
  `--diagnostics` and fed by `--read-vendor-settings`; its schema is seam contract.
- **Releases.** `release-manifest.json`, `docs/release-ledger.tsv`,
  `tools/release-gate.py` and `sbom.cdx.json` name releases by commit, ordered
  by `release_seq`.
- **The log contract.** `PROVIDER-CONTRACT.md` is generated by
  `tools/gen-provider-contract.py`. `tools/upstream-delta.py` counts 158 format
  strings we print that upstream does not, and 23 of upstream's that we reworded
  or did not take. Each sync record gives reasons for the ones it examined; the
  rc2 one lists eight. A line Platterpus parses moves only by a round. The log
  changes that fix a defect are in §2 (reports 27, 29 and 31).
- **Run evidence and CI.** The `evidence` branch, `docs/evidence-manifest.tsv`
  and `tools/evidence.py`; and `.github/workflows/ci.yml`, with upstream's
  `main.yml` kept deleted at each sync (`docs/upstream/sync-2026-11-03-ci.md`).
- **The CLI.** Eleven options are ours and long-only: `--cache-probe`,
  `--consumer`, `--diagnostics`, `--encoder-option`, `--keep-every-read`,
  `--prefer-accuraterip-match`, `--prefer-disc-isrc`, `--read-vendor-settings`,
  `--reread-time-limit`, `--reread-until-accuraterip` and `--stall-secs`.
  Upstream's `-k` is refused here: `--acoustid-key` became long-only at the rc3
  merge `56c1a56`, and the letter was retired by `dc0f79f9`
  (`tests/option_letters.py`). **Retire when** a decision of the owner's says
  otherwise. Nothing upstream does retires it.
