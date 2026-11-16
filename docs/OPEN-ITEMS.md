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

## Round 41: open since our lap 1 of 2026-11-16

Our lap 1 (`docs/handshake/round-41-lap-01.md`) proposes each row below,
and none is agreed until Platterpus answers. The build under review is `.33`
at `13bec0a`. A row leaves when the round settles it.

| Id | Item | Source and state | Next step |
|---|---|---|---|
| R41-1 | **`Disc MCN:` printed always**, with `Disc ISRC:`'s reasons: `none (libcdio returned none)`, `unknown (the driver does not report reading MCN)`, `unknown (capabilities query failed)` | cyanrip:R38.L3.S17; **accepted as given** in platterpus:R38.L4.S11, their reader to be built first. Not built on either side: we print the line only when an MCN was read (`src/cyanrip_log.c`, `Disc MCN:`) | Hold until their reader exists (PP-11); not in `.33` (the owner's word of 2026-11-16) |
| R41-2 | **A declared speed line**, `Drive speed:    8x declared by drive (GET PERFORMANCE), not measured`, as a record field first | cyanrip:R38.L8.S19; **accepted** in platterpus:R38.L9.S12, "in round 39". **The record field is built for `.33`**: `drive_declared.read_performance`, GET PERFORMANCE's reply and descriptors, at `cyanrip-diagnostics/14`. The log line is not. Drive I/O: HW-12 | Announce the field in lap 1; propose the line once a drive has answered (HW-12) |
| R41-3 | **`Ripping errors:` as three named counts**: failed frame reads, paranoia's skips, tracks that did not finish | Their counter-ask, platterpus:R38.L4.S12, to our S18; we took it as given (cyanrip:R38.L5.S8). No wording proposed. Their read-speed ladder reads the count, so the wording breaks a parsed line | Propose the wording in lap 1 |
| R41-4 | **Second 245 in the C2 probe** | Round 40's run placed track 3's misreads in seconds 244, 245, 251 and 252 (`docs/rig-2026-11-14-edb73dd/README.md`). Their `drivetest.sh` probes 244, 251, 252 and 144 only (`platterpus@34d20333:docs/rig-scripts/drivetest.sh:689`) | Ask before the owner's next run (HW-1) |
| R41-5 | **One version of the four shared documents** carrying what both sides accepted and the stale text found on 2026-11-16 | K1's amendment, "a lap is sent when it reaches its side's default branch", is accepted (cyanrip:R37.L5.S10, platterpus:R37.L6.S4 and S24, R38.L2.S9) and absent from `PROTOCOL.md` §5c's K1 text. Moving `--prefer-accuraterip-match` from `seam-commands.md` §1b to §1 is accepted (cyanrip:R38.L1.S11, platterpus:R38.L2.S9), not done; `--reread-until-accuraterip`'s move is ours to propose, since they send it. Stale: `OWNERSHIP.md` `-x`/`-j` (:59, :75), "new" (:82), "two kinds" over four rows (:130), a blank line breaking its table (:138); `seam-rules.md` the 41-versus-18 gap (:86-90), `-I`/`-J` (:113), `-t` as track selection (:340); `seam-commands.md` "all 17 rows" (:82-85), `-t` (:100), `-F` (:109), the `--keep-every-read` cell (:137), "ours currently does not" (:167), the round-7 CR cell (:255), "every refusal exits 1" (:627), exit codes "for round 8" (:630-632), answered WANTs (:324-339); `KNOWN-ISSUES.md`'s shared-document rows 13 to 15; the v5 proposal's §5b.1 to §5b.8, adopted or retired (`PROTOCOL.md:1517`) Their transport rule joins it (platterpus:R38.L15.S7): a lap written out of turn is held, numbered after the lap it waits for, and renumbered on a clash; our owner chose on 2026-11-16 to adopt it into the protocol rather than into both `CLAUDE.md` files | Propose as protocol v10 in lap 1; our owner adopted K1's amendment and the transport rule on 2026-11-16, and theirs adopts |
| R41-9 | **`-O` sent in a run**, so `Beyond disc:` shows on a drive | `overread-bounded` (`STATUS.md`): no run through round 40 sent `-O`, and no log has printed `Beyond disc:` (round 40's 75 logs: 0) | Ask, as HW-10 |

## Ours

| Id | Item | Where the detail is | Next step |
|---|---|---|---|
| US-1 | A newline in the `-d` path or the drive's INQUIRY strings inside paranoia's identify message | `KNOWN-ISSUES.md`, *paranoia's identify message can still start a line…*; cyanrip:R38.L3.S19 (b), platterpus:R38.L4.S13 | Escape it when the rig can show it (HW-14) |
| US-2 | Six candidates from the 2026-10-26 audit, never checked: CD-TEXT language, a TOC whose starts do not increase, a failed last-session query, an image's TOC pregap bounds, CD-TEXT ISRC skipping the ISO 3901 check, offset-search numbering | `KNOWN-ISSUES.md`, *Six drive answers an audit listed…* | Check each in the code; any that changes log text goes to a round |
| US-4 | `Lap commit list names its range` timed out in full parallel suites; mechanism unknown | `KNOWN-ISSUES.md`; `STATUS-OPEN suite-timeouts-at-default` | Record the next occurrence; none since 2026-09-30 |
| US-5 | A superseded track's read time on a drive | `KNOWN-ISSUES.md`, *A superseded track…*; their R155, shipped in their 0.7.126 | File a log where a later read replaced the first |
| US-6 | A derived contract shows a surface's shape, not its meaning | `KNOWN-ISSUES.md`, *A derived contract…* | Joint; no proposal open |
| US-9 | The inert-edit probe last ran 2026-09-16 (`d92c4e1`) | `SETTLED.md`; `docs/inert-edit-probe.log` | Run it before trusting a mutation sweep again |
| US-10 | `seam-commands.md` §4 NEED 1 (argument types in P1) and §5 WANT 1 (a machine-readable contract) | `docs/seam-commands.md` §4, §5 | Build, or decline in a round |
| US-11 | `seam-commands.md` §2a CR cells still `?` (:255, :259) | `docs/seam-commands.md` §2a | Fill in a shared-document version (R41-5) |
| US-12 | The pregap search on a drive: a pregap the TOC misses against the TOC-only answer; the binary-encoding quirk; the two-search clause never printed; cache defeat between sub-channel retries (`src/pregap.c` TODO); raw P-W mode, two-read confirmation, runs of sectors, the P channel | `docs/pregap-carry.md` (:173, :255, :311); `docs/research/2026-11-04-pregaps.md` (:452-459); `docs/history/2026-11-04-misreads-and-pregaps.md` (R4) | After HW-6's raw read on a second drive |
| US-13 | Speed change between passes (R3) and sector-level re-reads (R5) | `docs/history/2026-11-04-misreads-and-pregaps.md` | R3 is blocked: the BDR-209D read at 2.9x to 3.5x whatever `-S` asked; R5 waits on R1 and R2's results |
| US-14 | Log the READ CD request, sense data on a failed read, and per-read latency | `docs/research/2026-11-04-drive-settings.md` (options 2, 4, 5, 7) | Propose in a round |
| US-19 | macOS arm64 runner wait times | `docs/DEPENDENCY-PLAN.md`; on 2026-11-16, 3 of 6 `macos` attempts on pull requests #117 to #120 were cancelled unstarted, each annotated *"The job was not acquired by Runner of type hosted even after multiple attempts"*; the owner's word that day lets a pull request with no `src/` change merge on the other jobs then | Try another label on one pull request and compare, or drop |
| US-20 | Three audit leads never re-checked: c, g, l | `docs/history/AUDIT-2026-09-05.md` (:224, :228, :233) | Re-check, then close or list |
| US-21 | Our proposed `Pregap sample peak: …, not ripped` line has no answer | cyanrip:R36.L1.S17; UNVERIFIED whether superseded (their status lists `eac-htoa-log` as `cannot`) | Ask once in round 41's lap 1; withdraw it if they decline |
| US-25 | Two comments may misdescribe FFmpeg 6.1.1's muxers: `src/cyanrip_main.h` says FLAC drops a GIF cover with a warning, `src/cyanrip_encode.c` that MP3 drops other formats; a run of upstream's `648b1dd` on 2026-11-16 saw FLAC fail its header on a GIF and MP3 fail on AV1 and WebP. The fork sends neither, so no output changes | the upstream drafts of 2026-11-16 (UP-2) | Re-measure both through our encoder, then correct the comments |
| US-26 | Upstream pull request 153 moved to `ca3ab44` (2026-11-10), 20 commits on `648b1dd`, three of whose subjects match work done here; `docs/pregap-carry.md` still calls it a later evolution of 115 by the same author, and the 2026-08-21 audit's §3 calls `-J` independently implemented here, though it is upstream's own `ca7e830c` | `docs/upstream/carried-patches.md` §1 | Read 153's code against ours; correct `pregap-carry.md`'s and the audit's sentences in a dated note |
| US-23 | A Fedora CI job building what end users build. Its first run, on PR #120 at `ce969c5e` (Fedora 45: FFmpeg 9.0.2, libcdio 2.3.0, libcdio-paranoia 10.2+2.0.2), passed 165 tests, skipped 6 and failed 2, US-27 and `named_waits_after_the_open`, so it was taken out of that pull request. The second is fixed in `tests/slowcall.c` on 2026-11-16, proved on Fedora only when the job runs again | `docs/DEPENDENCY-PLAN.md` §4; the owner's word of 2026-11-16 | Land it with US-27 fixed |
| US-27 | FFmpeg 9.0.2's FLAC and MP3 muxers keep a WebP cover that our table, measured on FFmpeg 6.1.1, refuses before the rip (`crip_fmt_holds_picture()`), so a Fedora user's WebP cover is refused where it would embed: `cover_art_formats` on the first Fedora run | the run of PR #120's `fedora` job | Find which FFmpeg version changed it; make the table follow the linked libavformat; announce the refusal's change in a lap |

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
| PP-11 | Their reader for `Disc MCN:` | platterpus:R38.L4.S11 | Not built; before R41-1 ships |
| PP-12 | `seam-commands.md` §1b PP cells `?` for `-X`, `-C` and `-B`; §1 PP cells for `-F` and `-I`; §2a :260 (both sides) | `STATUS-OPEN unsent-flag-rows` | Theirs, in R41-5's version |
| PP-13 | Their footer within 8 s when the script console closes | `docs/history/KNOWN-ISSUES-2026-11-16.md`, *Closing Platterpus's script console…*; their round 30 lap 4 S9 | Their rig run |
| PP-14 | Their addendum carries no timestamp; the `--version` hang through the Distrobox wrapper | `SETTLED.md` (their addendum and wrapper rows) | Theirs |
| PP-15 | Should a beta expire? | `docs/history/UPGRADE-CHANNELS-PLAN.md` | Theirs; our stable channel moved to `.32` on 2026-11-16 |

## The owner's decisions and actions

| Id | Item | Source | Next step |
|---|---|---|---|
| OW-7 | A static Linux binary for users | `docs/DEPENDENCY-PLAN.md` §5; `docs/upstream/sync-2026-11-03-ci.md` §5 | Deferred on 2026-11-16 until the Fedora CI job (US-23) has run a while; it changes how every user gets the program, needs a round, and brings the GPL's source terms for every library linked in |
| OW-8 | File upstream items 24 to 31 as one comment on upstream issue 167 | `docs/upstream/issues-to-file.md`, items 24 to 31 | The owner files; all eight were re-checked against upstream's `648b1dd` on 2026-11-16 |
| OW-9 | Set `CYANRIP_REDACT_NAMES` where runs are filed; read the repository's Security tab (unread since 2026-11-03) | `docs/history/READINESS-PLAN.md` | Owner actions |
| OW-11 | Outside these repositories: skillcheck reading tarball pins, and the skillcheck `--verify` report | `docs/DEPENDENCY-PLAN.md`; `docs/history/READINESS-PLAN.md` | Handed to the claude-code-skills session in the fork's HANDOFF of 2026-11-16 |

## Needs a drive

No CD drive exists here. **A change to drive I/O names the row it touches, and
a green suite never stands in for one** (`CLAUDE.md`). Date a rig session by
its build. This table replaces `CLAUDE.md`'s, `KNOWN-ISSUES.md`'s and the list
in `STATUS-OPEN hardware-unverified`, which disagreed.

| Id | On a drive | State |
|---|---|---|
| HW-1 | C2 | Measured 2026-11-11 by `sg_raw`, not cyanrip: the BDR-209D returns C2 pointers, which its page 2Ah denies, and flags three bytes at track 5's 02:24:59, none at track 3's probe LBAs; cyanrip reads no C2. `.32`'s `not declared by drive (capabilities page, not measured)` printed on it 2026-11-14 (`edb73dd`). Next: the probe over seconds 144, 244, 245, 251 and 252 (R41-4) |
| HW-2 | `-f` | Ran from 2026-10-06 (`5704062`). Not run: a stopped search, one that finds nothing, `-f` on a second drive, `offset_search` in a drive's record |
| HW-3 | Damaged media | The read ran 2026-10-04 (`174a134`), the `-Z` arm 2026-10-06 and the skip arm 2026-10-21 (`ca0f097`); a drive reporting failed reads, then unopenable, 2026-11-03 (`3f288fb`). Not run: a track's `File(s):` naming one not written whole |
| HW-4 | CD-TEXT from a disc | Not run: `mmc_read_cdtext` is not the `.toc` path |
| HW-5 | `Accurate stream:`, `Recordable:`, two-search `Pregap source:` | Ran 2026-10-21 (`ca0f097`), 2026-10-28 (`5aeefc4`) and 2026-11-03 (`3f288fb`): `Accurate stream:` answers; `Recordable:` answers `no` for a pressed disc from the drive's own profile. Not run: a recordable disc; the two-search clause has not printed; whether paranoia reads differently on a drive without accurate stream |
| HW-6 | Track 9's pregap, LSN 145567 | `94 or 95 frames (undecided)` in 26 of round 40's 29 rip logs, 95 in 3; this drive's raw Q of that sector fails its CRC (2026-11-09). Next: a raw read on a second drive (cyanrip:R39.L1.S11; `STATUS-OPEN subchannel-pregap-varies`) |
| HW-7 | `-W` on a pre-emphasised disc | Not run |
| HW-8 | `-P 0`'s sector-by-sector salvage | Not run |
| HW-9 | `Speed:` when `-S` is sent, and the rip at drive speed after a `-S` the drive refuses | Not run |
| HW-10 | `-O`: a read past the lead-out, `Beyond disc:` | Not run: no run through round 40 sent `-O` (R41-9; `STATUS-OPEN overread-bounded`) |
| HW-11 | Track 1's pregap counted from LBA 0 | Not decidable on the reference disc, whose track 1 starts at LSN 0; needs a disc with a pregap before track 1 (`STATUS-OPEN track1-pregap-base`) |
| HW-12 | The read performance the drive declares (R41-2) | Built for `.33`: GET PERFORMANCE, type 00h, asked once after any `-S`, kept in the record's `drive_declared.read_performance`. Not yet sent to a drive: no image driver answers it, so the suite pins only the parse and the record's shapes (`tests/drivecaps.c`, `tests/diagrecord.c`) |
| HW-13 | `.32`'s footer third form and its five `Still waiting:` names | Not printed on 2026-11-14: track 5 converged in no `-Z` pass, and no call stalled |
| HW-14 | A newline in the `-d` path or the drive's INQUIRY strings | Not run (US-1) |
| HW-15 | A disc ISRC that is not an ISO 3901 code; `Tracks ripped accurately:` on a disc with a data track; an Enhanced CD with a positive offset (upstream issue 168's read) | Not run |
| HW-16 | A second drive for: the cache probe choice (PP-5); `A2`'s speed half, `A4` and `A5`, closed as unsettleable on this drive (platterpus:R38.L17.S5); redumper on the reference disc (US-12) | No second drive yet |
| HW-17 | Memory use at whole-disc scale | Not measured (`SETTLED.md`) |

## Upstream

| Id | Item | Source | Next step |
|---|---|---|---|
| UP-1 | Items 24 to 31, drafted and not filed; 29 to 31 drafted, and all eight re-checked, against `648b1dd` on 2026-11-16 | `docs/upstream/issues-to-file.md` | OW-8 |
| UP-2 | An AVIF cover aborts upstream with `free(): double free detected`, exit 134: the cover's codec parameters are copied with `memcpy` (`src/coverart.c:62`, `:278`, `src/cyanrip_encode.c:1166` at `648b1dd`), run on a build of it on 2026-11-16; fixed here at `af89fcc` | the upstream drafts of 2026-11-16 | Draft as item 32 |
