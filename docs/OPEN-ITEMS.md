# Open items: the one list

**Every item still open in this repository's work is a row here**: ours, what
waits on Platterpus, on the owner, on a drive, or on upstream. Detail stays
where it lives: a defect's evidence in `docs/KNOWN-ISSUES.md`, an exchange in
its lap, a run in its README. A row only names the item, where its detail is,
who owns it, and the next step.

- **`STATUS.md`'s `STATUS-OPEN` lines are the summary Platterpus reads.** They
  keep the shape its gate checks, and each names its row here.
- **A row leaves when its item closes,** in the commit that closes it, and the
  Changelog says so. A row that turns out not to be closed comes back.
- **The whole list is reviewed before each round's opening lap** (the owner's
  word of 2026-11-16). Last full review: 2026-11-16, after round 40 closed, at
  `6b5b9dc7`, from five audits of the documentation and of rounds 36 to 40.
- **Ids are stable.** `R41-n` is proposed for round 41's opening lap, `US-n` is
  ours, `PP-n` Platterpus's, `OW-n` the owner's, `HW-n` needs a drive, `UP-n` is
  upstream's. A source like `cyanrip:R38.L3.S17` is a lap statement: round 38,
  lap 3, statement 17.

## For round 42's opening lap: carried from round 41

Round 41 closed `GO`/`GO` on 2026-11-18, on our lap 5 and Platterpus's lap 6, approving
`.34` at `fb28088`. These rows came out of it and go to round 42's opening lap, on
`.35`; their ids stay. A row leaves when round 42 settles it.

| Id | Item | Source and state | Next step |
|---|---|---|---|
| R41-2 | **A declared speed line**, `Drive speed:    8x declared by drive (GET PERFORMANCE), not measured`, as a record field first | cyanrip:R38.L8.S19; **accepted** in platterpus:R38.L9.S12, "in round 39". **The record field is built for `.33`**: `drive_declared.read_performance`, GET PERFORMANCE's reply and descriptors, at `cyanrip-diagnostics/14`. The log line is not. Drive I/O: HW-12. **A drive answered on 2026-11-17**: the BDR-209D declares one descriptor, 1012 to 2469 kB/s across the disc, in all 37 `.34` records (`docs/rig-2026-11-17-fb28088/`) | Propose the line in a round, now that a drive has answered |
| R41-3 | **`Ripping errors:` with its parts named** | Our wording (cyanrip:R41.L1.S16) is **accepted as given** (platterpus:R41.L2.S8); their parser reads both forms at `f08e9b8e`, shipping in 0.7.127 (S9); we change it in our first build after that release (cyanrip:R41.L3.S5); 0.7.127 is tagged 2026-11-17 (platterpus:R41.L4.S7). **Building it found the five parts incomplete** (cyanrip:R41.L5.S8). **Counted completely on 2026-11-18**: the line prints `crip_ripping_errors()`, `total_error_count` plus paranoia's skips. There are 27 increments, all in `src/cyanrip_main.c`; lap 5 S8's 28 counted a comment. Six run before the log opens, and the `-l` check that `7c169ba7` moved ahead of the header leaves one unreachable. So a log can hold 21 sources in eight causes: frame reads failed (2), sectors failing EDC (1), paranoia skips (1), tracks not finished (2), decoder or encoder setup and encoder failure (5), arguments refused after the log opens (7), cover art (2), and out of memory (1). S16's `disc lookups failed` is always 0 in a log: a MusicBrainz failure ends the run before the log opens, and `crip_fill_accurip()` never returns an error. One failure can also count twice (US-41) | Propose the complete list in round 42's opening lap, each part counted where its increment happens; `.35` keeps the line as it is |
| R41-11 | **Five questions in our lap 3**: v10's renumbering of a sent lap (S20), and four audit defects, CD-TEXT's ISRC ranking (S22), the CD-TEXT language on a `.toc` (S23), an image's pregap outside its track (S24), the last-session cut (S25) | cyanrip:R41.L3; US-2 holds the evidence. **Answered** in platterpus:R41.L4.S13 to S17: the clause "if it is not yet sent"; the disc's ISRC wins by default; the language unknown on a `.toc` or inline CUE CD-TEXT; an image's pregap outside its track refused with exit 74; the last-session cut kept, with a line saying the drive did not answer | Our lap 5 S9 says each is built in `.35`, its new lines' wording announced in round 42's opening lap |

## Ours

| Id | Item | Where the detail is | Next step |
|---|---|---|---|
| US-1 | A newline in the `-d` path or the drive's INQUIRY strings inside paranoia's identify message | `KNOWN-ISSUES.md`, *paranoia's identify message can still start a line…*; cyanrip:R38.L3.S19 (b), platterpus:R38.L4.S13 | Escape it when the rig can show it (HW-14) |
| US-4 | `Lap commit list names its range` timed out in full parallel suites; mechanism unknown | `KNOWN-ISSUES.md`; `STATUS-OPEN suite-timeouts-at-default` | Record the next occurrence; none since 2026-09-30 |
| US-5 | A superseded track's read time on a drive | `KNOWN-ISSUES.md`, *A superseded track…*; their R155, shipped in their 0.7.126 | File a log where a later read replaced the first |
| US-6 | A derived contract shows a surface's shape, not its meaning | `KNOWN-ISSUES.md`, *A derived contract…* | Joint; no proposal open |
| US-10 | `seam-commands.md` §4 NEED 1 (argument types in P1) and §5 WANT 1 (a machine-readable contract) | `docs/seam-commands.md` §4, §5 | Build, or decline in a round |
| US-11 | `seam-commands.md` §2a's CR cells still `?`, at :260 (`.cue` track numbering) and :261 (the `.log`'s `Album:` field) | `docs/seam-commands.md` §2a, whose columns run PP then CR | Fill them in a later shared-document version |
| US-12 | The pregap search on a drive: a pregap the TOC misses against the TOC-only answer; the binary-encoding quirk; the two-search clause never printed; cache defeat between sub-channel retries (`src/pregap.c` TODO); raw P-W mode, two-read confirmation, runs of sectors, the P channel | `docs/pregap-carry.md` (:173, :255, :311); `docs/research/2026-11-04-pregaps.md` (:452-459); `docs/history/2026-11-04-misreads-and-pregaps.md` (R4) | After HW-6's raw read on a second drive |
| US-13 | Speed change between passes (R3) and sector-level re-reads (R5) | `docs/history/2026-11-04-misreads-and-pregaps.md` | R3 is blocked: the BDR-209D read at 2.9x to 3.5x whatever `-S` asked; R5 waits on R1 and R2's results |
| US-14 | Log the READ CD request, sense data on a failed read, and per-read latency | `docs/research/2026-11-04-drive-settings.md` (options 2, 4, 5, 7) | Propose in a round |
| US-19 | macOS arm64 runner wait times | `docs/DEPENDENCY-PLAN.md`; on 2026-11-16, 3 of 6 `macos` attempts on pull requests #117 to #120 were cancelled unstarted, each annotated *"The job was not acquired by Runner of type hosted even after multiple attempts"*, and all 3 attempts on #121 the same way (a fourth, a re-run, was cancelled by the concurrency group); the owner's word that day lets a pull request with no `src/` change merge on the other jobs then, and on #121's `src/` changes the owner chose "Merge on the rest", so `bc72bb4c` is not yet built on macOS | Try another label on one pull request and compare, or drop |
| US-20 | Two audit leads still true, re-checked 2026-11-16; the third, g, was fixed by `8d465f1b` and `a723ae37`. c: of 167 error rows at `8b3174ae`, 41 have a test, 115 have none and 11 are too short to probe, and the gate's floor is 7. l: a 74-minute image peaked at 704.2 MiB at the defaults and 129.5 MiB with `-K`, since ReplayGain holds every encoded packet; nothing measures memory | `docs/history/AUDIT-2026-09-05.md` (:224, :233) | c: raise the floor toward 41; l: decide whether memory is a limit to state |
| US-21 | Our proposed `Pregap sample peak: …, not ripped` line has no answer | cyanrip:R36.L1.S17; UNVERIFIED whether superseded (their status lists `eac-htoa-log` as `cannot`) | Ask once in round 41's lap 1; withdraw it if they decline |
| US-29 | An HEVC cover would be saved as `Front.heif`, which FFmpeg 6.1.1's image muxer does not list, so its save likely fails as JPEG XL's did; no HEVC cover the loader takes was made here | `src/coverart.c`, the extension list | Make one, or refuse HEVC before the rip |
| US-30 | `CDIO returned invalid track N end LSN` returns from `cyanrip_ctx_init()` without tearing the context down, unlike its neighbours `Invalid number of tracks` and `Invalid TOC`; read, not run | `src/cyanrip_main.c`, the track loop | Tear it down as they do, with a test that reaches it |
| US-31 | **The UX review of 2026-11-17, the fixes that move no parsed line**: F28, a man page. Built for `.35`: F4, a quick start on the README's first screen and the package names under Compiling; F25, album folders made under the umask rather than 0700 (`album_folder_mode`); F13, the QR code skipped under `NO_COLOR` or `TERM=dumb` (`QR code colour opt-outs`); F17, `-l` checked before the header, with no log or CUE sheet left (`rip_index_checked_first`) | `docs/history/UX-REVIEW-2026-11-17.md`, triaged against `27728a75`, whose `src/` is the review's `fd20a0a`'s | F4, F13, F17 and F25 are built for `.35` (`f0d88e55`, `ed9a578d`, `7c169ba7`, `8f0a861d`) and announced in round 42's opening lap; F28, the man page, is not for now, the owner's word of 2026-11-17 |
| US-32 | **The UX review of 2026-11-17, the fixes that change what Platterpus parses**, each for a round: F1's hint after a failed open; F2, an unknown disc refused as a usage error, not a ripping error; F3's offset hint and `--help`'s `(default: 0)`; F5, a short terminal header; F6, `ebur128`'s block to the log only; F7, the album loudness rows gated when no track finished; F8, an `Output folder:` line; F9 and F10, the expected conditions and one spelling of AccurateRip; F11 and F12, `--help`'s layout, which regenerates P1; F14 and F15, argument errors and GNU forms (`genopt.h` is upstream's); F16, an unwritable `--diagnostics` path exiting 0, as `seam-commands.md` §7 records; F18, an unknown scheme tag; F19, the Ctrl-C wording, which Platterpus's source matches (`platterpus@ad5c4129`); F20, the progress line's rate, which their regexes read (`src/platterpus/workers/rip_worker.py:243`, `src/platterpus/inbound_text.py:175`) though the contract publishes it only as `\r` and `%s` (P3, `cyanrip_main.c:1367`, `:1427`); F21, `-J -`; F24, a re-rip overwriting the last, which their `overwrite answers` step runs; F26, `-q`; F27, `(skip with -N)` on the retry line; and one the review missed: `Unable to get AccuRIP DB data: %s` is followed by a line holding only `!` (`src/accurip.c:376`, `:386`), as upstream's is (`origin/master:src/accurip.c:161`, `:171`), a text Platterpus's inventory records (`platterpus@69483cf2:src/platterpus/ripper_message_inventory.py:139`), so its fix needs the round too. It is drafted as upstream report 33, with a second defect found on the same path: when `curl_easy_getinfo()` fails, the status is left unset and the log says `AccurateRip:    disabled` (`src/accurip.c:384-388`), a value Platterpus reads (`platterpus@5ce6641e:src/platterpus/parsers/cyanrip_log.py:354`) | `docs/history/UX-REVIEW-2026-11-17.md` | Round 42's opening lap proposes F2, F7, F16, F20 and F24, the progress line's wording and the two AccurateRip defects, the owner's word of 2026-11-17; the rest wait for a later round, and the saved settings F3 and F23 ask for are not for now |
| US-33 | **Move the stable channel to `.34`** once round 41 closes `GO`/`GO` | The owner's word of 2026-11-17, *"do all recommended"*; round 41 waits on Platterpus's lap 6 | On their lap 6's `GO`: a ledger row and the manifest, as `.32`'s move did (`f9fdd1a7`) |
| US-34 | **Read the rest of the outside audit log**, archived unread | On the evidence branch at `60ec8702`, `docs/outside-reviews-2026-11-17/imported/audit-log/`. The week review of 2026-11-10 is read, on 2026-11-18 (`docs/history/WEEK-REVIEW-2026-11-10-READ.md`, whose open points are US-36 to US-39); the rest is not: the research of 2026-11-03, the lessons, the proposal, the follow-ups and `kit/` | Read each against this tree, and move what still holds to a row here or a lap statement |
| US-35 | **Two run READMEs differ from their filed copies**: `docs/rig-2026-11-11-e531a33/README.md` and `docs/rig-2026-11-11b-c2probe/README.md` were corrected here on 2026-11-12 (`c59c9e53`, `b5010024`) after they were filed, and the evidence branch never changes, so `tools/evidence.py verify-rows` without `--base` fails on both. CI checks only the rows a change adds, so nothing has shown it | Found 2026-11-17 while filing the outside reviews | Decide how a correction to a filed README is recorded, since HR-2 5a has a folder's README on both branches; then mend these two |
| US-36 | **The evidence branch has no README at its root**, and nothing here answers the records standard's four questions as such | The week review of 2026-11-10, M62-63 and R128-135 (`docs/history/WEEK-REVIEW-2026-11-10-READ.md`); the branch's root holds only `docs/`, and `docs/README.md` maps the default branch's files by kind | Add a root README by an evidence commit, one that `tools/evidence.py verify-rows` accepts, or decline it; answer the four questions in `docs/README.md` |
| US-37 | **Three process points the week review asks both sides to agree**: a person's acceptance run goes between rounds on a released pair, with a mid-round fix waiting for the next pair; R1, overridden again in round 41 (our lap 5's two `override: R1` lines), goes up for amendment; one builder per request the owner gives both sessions | The week review of 2026-11-10, M18-33 (`docs/history/WEEK-REVIEW-2026-11-10-READ.md`) | Propose each in a round, worded the same on both sides, or answer `not doing` with a reason; the owner says which round |
| US-38 | **A lost drive's log does not say the drive is gone**: it says `Drive media change query failed (libcdio error N), stopping!` and then `Error ripping: Input/output error` | The week review of 2026-11-10, M44-45, its F2 (not the UX review's F2); `src/cyanrip_main.c`, the media-change check in the track read | Decide in a round: a line naming what was observed, since "gone" is an inference libcdio does not report, or `not doing`. The log is the API |
| US-39 | **The steward's one-re-run rule differs from Platterpus's** and does not say whether that is deliberate | The week review of 2026-11-10, R369-373 and M49-51; `.claude/skills/steward/SKILL.md` rule 4 and `references/steward-failures.md` | Read Platterpus's rule; say in the skill why ours differs, or align it |
| US-40 | **Say in round 42's opening lap that our gate implements protocol v10** | `PROTOCOL.md` §18: neither side declares 10 until both have said in a lap that their gate implements it. **Built 2026-11-18**: `PROTOCOL_VERSION = 10` in `tools/release-gate.py`, pinned by `tests/release_gate.py`'s `test_gate_implements_10_once_both_trees_hold_it`, once the file was byte-identical in both trees at `platterpus@0cb0889`; round 41's laps, declaring 9, stay readable. Theirs moves before their first lap of round 42 (their round 41 lap 6 S7) | Say it in round 42's opening lap |
| US-41 | **One encoder write failure counts twice in `Ripping errors:`**, and `Encoder errors:` beside it says `not applicable; no whole track was encoded` | `KNOWN-ISSUES.md`, *One encoder write failure counts twice…*: reproduced on `71430d40` with `-K` against a 64 KiB file-size limit, where one `File too large` gave `Ripping errors: 2`. Upstream's code has both increments too, read and not run | Fix it with R41-3's parts in a round, since both lines are parsed; then run it upstream and report it there if it holds |

## Waiting on Platterpus

For information: their work, tracked in their `TASKS.md`. Each line names their
id.

| Id | Item | Source | State |
|---|---|---|---|
| PP-4 | **R150**: measure the read offset from a disc at drive setup, through `-f` | their `TASKS.md` | Open; needs a disc AccurateRip knows |
| PP-5 | **R151**: which cache probe their setup keeps | platterpus:R40.L2.S7, R40.L4.S3 | Keeps `cd-paranoia -A`; decides after a second drive (HW-16) |
| PP-6 | **R152**: read the drive's declarations once, at drive setup | cyanrip:R39.L7.S6, S7 answered | Their build |
| PP-7 | **R134**: rebuild a disputed second from several reads, accepted only on AccurateRip v1 and v2; the only planned sender of `--keep-every-read` | platterpus:R39.L2.S17, R39.L6.S30 | Held |
| PP-8 | **R131**: a re-read track's block CRCs describe the album pass | platterpus:R38.L7.S9 | Open |
| PP-9 | **R137** parts 2 and 3: a drive report in `--doctor` and every bundle, and a *Report this drive* action | part 1, ours, shipped in `.30` | Open |
| PP-10 | **R44**: the EAC-layout wording for error positions, through the handshake | their `TASKS.md` | No proposal sent |
| PP-12 | `seam-commands.md` §2a's PP cell still `?` at :261, the `.log`'s `Album:` field. The §1b cells for `-X`, `-C` and `-B` and the §1 cells for `-F` and `-I` are filled in protocol v10's texts, byte-identical in both trees since their round 41 lap 6 S7 | `STATUS-OPEN unsent-flag-rows` | Theirs, in a later shared-document version |
| PP-13 | Their footer within 8 s when the script console closes | `docs/history/KNOWN-ISSUES-2026-11-16.md`, *Closing Platterpus's script console…*; their round 30 lap 4 S9 | Their rig run |
| PP-14 | Their addendum carries no timestamp; the `--version` hang through the Distrobox wrapper | `SETTLED.md` (their addendum and wrapper rows) | Theirs |
| PP-15 | Should a beta expire? | `docs/history/UPGRADE-CHANNELS-PLAN.md` | Theirs; our stable channel moved to `.32` on 2026-11-16 |

## The owner's decisions and actions

| Id | Item | Source | Next step |
|---|---|---|---|
| OW-7 | A static Linux binary for users | `docs/DEPENDENCY-PLAN.md` §5; `docs/upstream/sync-2026-11-03-ci.md` §5 | Deferred on 2026-11-16 until CI's `fedora` job has run a while; it changes how every user gets the program, needs a round, and brings the GPL's source terms for every library linked in |
| OW-8 | File upstream items 24 to 33 as one comment on upstream issue 167 | `docs/upstream/issues-to-file.md`, items 24 to 33 | The owner files; 24 to 32 were re-checked against upstream's `648b1dd` on 2026-11-16, and 33 was drafted against it on 2026-11-17, when `git ls-remote` still gave it for `master` |
| OW-9 | Set `CYANRIP_REDACT_NAMES` where runs are filed; read the repository's Security tab (unread since 2026-11-03) | `docs/history/READINESS-PLAN.md` | Owner actions |
| OW-11 | Outside these repositories: skillcheck reading tarball pins, and the skillcheck `--verify` report | `docs/DEPENDENCY-PLAN.md`; `docs/history/READINESS-PLAN.md` | Handed to the claude-code-skills session in the fork's HANDOFF of 2026-11-16 |

## Needs a drive

No CD drive exists here. **A change to drive I/O names the row it touches, and
a green suite never stands in for one** (`CLAUDE.md`). Date a rig session by
its build. This table replaces `CLAUDE.md`'s, `KNOWN-ISSUES.md`'s and the list
in `STATUS-OPEN hardware-unverified`, which disagreed.

| Id | On a drive | State |
|---|---|---|
| HW-1 | C2 | Measured 2026-11-11 by `sg_raw`, not cyanrip: the BDR-209D returns C2 pointers, which its page 2Ah denies, and flags three bytes at track 5's 02:24:59, none at track 3's probe LBAs; cyanrip reads no C2. `.32`'s `not declared by drive (capabilities page, not measured)` printed on it 2026-11-14 (`edb73dd`). Next: the probe over seconds 144 of track 5, 240, 244, 245, 251 and 252 of track 3, and 162 of track 1, every second the records name (`docs/rig-2026-11-17-fb28088/`); their C2 probe is in their drive test, not the Full run (platterpus:R41.L2.S11), and round 41's rip bundle does not carry it Next: Platterpus's C2 probe at track 3's seconds 240, 244, 245, 251 and 252, track 5's 144 and track 1's 162 (platterpus:R41.L2.S11), at the next rig session, the owner's word of 2026-11-17 |
| HW-2 | `-f` | Ran from 2026-10-06 (`5704062`), and on `.34` 2026-11-17 (`fb28088`): +667, confidence 14, each track named by its own number. That disc numbers from 1 and needs +667, so neither half of `8610f3c1` shows. Not run: a drive whose offset is 0, a disc numbered from other than 1, a stopped search, one that finds nothing, `-f` on a second drive, `offset_search` in a drive's record |
| HW-3 | Damaged media | The read ran 2026-10-04 (`174a134`), the `-Z` arm 2026-10-06 and the skip arm 2026-10-21 (`ca0f097`); a drive reporting failed reads, then unopenable, 2026-11-03 (`3f288fb`). Not run: a track's `File(s):` naming one not written whole |
| HW-4 | CD-TEXT from a disc | Not run: `mmc_read_cdtext` is not the `.toc` path |
| HW-5 | `Accurate stream:`, `Recordable:`, two-search `Pregap source:` | Ran 2026-10-21 (`ca0f097`), 2026-10-28 (`5aeefc4`) and 2026-11-03 (`3f288fb`): `Accurate stream:` answers; `Recordable:` answers `no` for a pressed disc from the drive's own profile. Not run: a recordable disc; the two-search clause has not printed; whether paranoia reads differently on a drive without accurate stream |
| HW-6 | Track 9's pregap, LSN 145567 | `94 or 95 frames (undecided)` in 26 of round 40's 29 rip logs, 95 in 3, and in 28 of round 41's 29, 95 in 1; this drive's raw Q of that sector fails its CRC (2026-11-09). Next: a raw read on a second drive (cyanrip:R39.L1.S11; `STATUS-OPEN subchannel-pregap-varies`) |
| HW-7 | `-W` on a pre-emphasised disc | Not run |
| HW-8 | `-P 0`'s sector-by-sector salvage | Not run |
| HW-9 | `Speed:` when `-S` is sent, and the rip at drive speed after a `-S` the drive refuses | Not run |
| HW-10 | `-O`: a read past the lead-out, `Beyond disc:` | Ran 2026-11-17 on `.34`, Platterpus's `overreadprobe` (`docs/rig-2026-11-17b-overreadprobe/`): the BDR-209D refused 2 of 2 frames past the lead-out at +667 and 2 of 2 before LSN 0 at -667, each read once and written as silence, exit 0 in under 90 s each, and track 14's EAC CRC equals the default rips'. Not run: a drive that answers past its lead-out, the arm that keeps a frame read once (`STATUS-OPEN overread-bounded`) |
| HW-11 | Track 1's pregap counted from LBA 0 | Not decidable on the reference disc, whose track 1 starts at LSN 0; needs a disc with a pregap before track 1 (`STATUS-OPEN track1-pregap-base`) |
| HW-12 | The read performance the drive declares (R41-2) | Built for `.33`: GET PERFORMANCE, type 00h, asked once after any `-S`, kept in the record's `drive_declared.read_performance`. No image driver answers it, so the suite pins only the parse and the record's shapes (`tests/drivecaps.c`, `tests/diagrecord.c`). **Answered on the BDR-209D 2026-11-17** (`fb28088`): 24 bytes, one descriptor, LBA 0 at 1012 kB/s to LBA 268706 at 2469 kB/s, the same in all 37 records. Not run: a drive that refuses it, one with more than one descriptor, and the question after a `-S` |
| HW-13 | `.32`'s footer third form and its five `Still waiting:` names, and `.34`'s *the paranoia setup* and *the track format query for track N* on an audio track | Not printed on 2026-11-14 or 2026-11-17: track 5 converged in no `-Z` pass, and no call stalled; `.34`'s two are proved only on images through `tests/slowcall.c` |
| HW-14 | A newline in the `-d` path or the drive's INQUIRY strings | Not run (US-1) |
| HW-15 | A disc ISRC that is not an ISO 3901 code; `Tracks ripped accurately:` on a disc with a data track; an Enhanced CD with a positive offset (upstream issue 168's read) | Not run |
| HW-16 | A second drive for: the cache probe choice (PP-5); `A2`'s speed half, `A4` and `A5`, closed as unsettleable on this drive (platterpus:R38.L17.S5); redumper on the reference disc (US-12) | No second drive yet |
| HW-17 | Memory use at whole-disc scale | Not measured (`SETTLED.md`) |
| HW-18 | `Session gap: not determined (…)` on a drive whose last-session query fails | Built for `.35` and held on an image through the shim (`session_gap_assumed`); never printed by a drive. Linux answers the query, so the line should not print there; libcdio's macOS, FreeBSD and AIX drivers never answer it. Not run |
| HW-19 | `Disc MCN:` on a drive: a code, `none (libcdio returned none)`, or `unknown (…)` with the reason the capabilities query gave | Built for `.35` and held on images through the shim (`disc_mcn_always`); `.35` has not run on a drive. Not run |

## Upstream

| Id | Item | Source | Next step |
|---|---|---|---|
| UP-1 | Items 24 to 33, drafted and not filed; 29 to 32 drafted, and 24 to 32 re-checked, against `648b1dd` on 2026-11-16, and 33 drafted against it on 2026-11-17 | `docs/upstream/issues-to-file.md` | OW-8 |
| UP-3 | A JPEG XL cover failed a rip here, and by its source would upstream: its file is named `Front.jpegxl`, from the codec's name, which no muxer takes, so the save fails with *Unable to init lavf context: Invalid argument!*; `648b1dd`'s extension list (`src/coverart.c:280`) is the same, read and not yet run there; fixed here on 2026-11-16 | this list | Run on a build of `648b1dd`; draft as an item |
| UP-4 | `-f`'s offset search never tries an offset of 0, and numbers tracks by position, reading sectors before the disc when it starts above track 1: run here at `8b3174ae`, and `648b1dd`'s code is the same (`src/cyanrip_main.c:513`, `:529`, `:557`, `:576`), read and not run there; fixed here on 2026-11-16 | `KNOWN-ISSUES.md`, *Six drive answers an audit listed…* | Run on a build of `648b1dd`; draft as an item |
