# Rig session 2026-09-24 — build `df91ae7`, Platterpus 0.6.55

**Read the build, not the date.** This is `df91ae7`, `+platterpus.15`: the
release, and round 26's reviewed pin. Every one of the eight rips, all four
direct invocations and `session/rig-check-ripper-version.txt` say
`platterpus-fork-gdf91ae7`. This is round 26 §0.1's real test.

## Provenance

| | |
|---|---|
| bundle | `platterpusbundle20260924t011421z.tar.gz`, handed over by the operator |
| sha256 | `f14864171bdbb215e555e777d51fc8dcbd466b4306d56a9441d42640d01a4571` |
| size | 8,586,192 bytes, 276 entries, 229 of them screenshots |
| session stamp | `20260924T011421Z` |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), `/dev/sr0` |
| disc | The Police, *Every Breath You Take: The Classics*, 14 tracks, MusicBrainz `65282302-368b-4ba2-953a-483bcdef2410` |
| ripper | `cyanrip 0.9.4-rc2+platterpus.15 (platterpus-fork-gdf91ae7)` |
| consumer | `platterpus/0.6.55` (build `629ffa2`, their `v0.6.55` tag) |
| script | `fullacceptance.txt`, 261 steps |
| outcome | **pass 258, fail 3, error 0, skipped 0, blocked 0, unreachable 0, info 1**. All three failures are one event: the container kill below |

**Every file here is byte-identical to a file in that tarball**, checked by
hashing each source and each copy, 40 of 40. Not filed: the 229 screenshots,
and six of the eight `.platterpus.json` reports, which are Platterpus's
artifact. Their sha256/16, so they stay verifiable: `ddfbde40d6bc8181`
after-cancel, `1a2a9c5fdf7858a9` derived-mp3, `17b2f1e57e09ef29` derived-wav,
`da914cdcac6f0125` derived-wavpack, `b79bb91f0f71c013`
full-acceptance-angle-bracket-2, `30601f0351de12a9` secure-reread. The two
that are filed, `cancel-me` and `full-acceptance-angle-bracket`, are the two a
claim below depends on.

**The `-2` suffix comes from content.** `full-acceptance-angle-bracket-2`
carries `-l 1,2` and `-D "{album_artist}/{album} (2)"`, so it is section H's
overwrite re-rip. `full-acceptance-angle-bracket` carries no `-l`: it is
section F's whole-disc rip, the one that was killed.

## Section F was killed, and neither program's log shows why

**This heading said *"killed from outside both programs"*, and that was half
wrong.** Corrected 2026-09-24 from Platterpus's round 27 lap 2, Correction 1,
which read the operator's host journal. **That journal is in neither
repository, so what follows is their reading, and we have not checked it.** The container belonged to **an earlier
Platterpus window's systemd unit**: that window started it at 20:20:29, updated
and relaunched itself inside the same unit at 21:12:50, and was closed at
21:13:02, and the unit stayed alive because the container's monitor (`conmon`)
was still in it. The acceptance run's new window, from 21:13:48, used that
container. The container died at 21:16:15 and that unit ended. Their account of
why `conmon` was in the unit is `INVOCATION_ID` left in the ripper wrapper's
environment (`containers/podman@5866b09:libpod/oci_conmon_linux.go:183-186`;
not read here, because a shortened SHA cannot be fetched by name), fixed in
their 0.6.59. **What struck the container is still not identified**:
their journal reading found no podman stop or kill, no systemd stop job, no OOM
kill and no logout. So the container's vulnerability came from Platterpus, and
the trigger came from something not yet identified. What follows is kept as
first written, from the logs in this bundle, which still say what they say.

Section F is the full-disc rip with every post-rip check on. It ran 1m 35s,
and the container it ran in was stopped. From
`session/platterpus-app-log.1.txt`, whose times are the host's local time
(UTC−4):

| line | time | what |
|---|---|---|
| 130 | 21:14:42.103 | the rip starts |
| 741 | 21:16:13.519 | the last progress line on schedule: track 1, 40.62% |
| 742 | 21:16:15.710 | the next one, **2.2 s later**. Every one before it came about 0.1 s apart |
| 743 | 21:16:15.711 | `Trying to quit`: cyanrip's handler received SIGINT or SIGTERM (`src/cyanrip_main.c:1180`, `:1494`) |
| 744 | 21:16:15.798 | **exit 137, 87 ms later**. That is SIGKILL, which no process can catch |
| 805 | 21:16:15.932 | `cyanrip -V` exits **125**: *"unable to start container … creating temporary passwd file … `/etc/passwd`: no such file or directory"*. The `ripping` container was not running |

**Neither program started it.** *(Still true of the stop, which neither
program logged, but the container's ownership was Platterpus's: see the
correction above.)* Platterpus installed handlers for SIGTERM and
SIGINT at line 9 and logged nothing on either one. It logged no cancel before
line 744. In section I, where Platterpus does cancel a rip, it logs the cancel,
a single SIGTERM and the footer's arrival. None of that is here.

**What stopped the container is not in this bundle.** The operator can check
the host journal, `journalctl --since "2026-09-23 21:15" --until "2026-09-23
21:17"`, both system and `--user`. One candidate is an automatic update service
that upgrades distrobox containers, which some Fedora Atomic images run. That
is a guess, and nothing here supports it. *(Platterpus's journal reading
found no podman stop or kill event, which such a service would be expected to
leave, so the guess is weaker still.)*

**The log it left is truthful.** `rips/full-acceptance-angle-bracket.log`
stops after `Tracks:`. It has no track block, no footer and no `Log FUN512:`,
and it claims nothing that did not happen. `cyanrip -Y` on it prints *No FUN512
checksum found*. Platterpus's `rig-check` refused to treat the empty parse as a
clean one, which is correct.

**Consequence:** section F's full-disc, all-checks-on rip did not happen.
Section N's whole-disc rip at `-Z 2` did, and so did five two-track rips and
the cancelled one.

## What this session establishes for `.15` on a drive

| | result | evidence |
|---|---|---|
| `.15`'s `Retry limit:` second form | **on hardware for the first time**. All eight rips print `3 (per whole-track re-read; 5 per frame, rounded up to a multiple of 5, the only values libcdio-paranoia checks)`. The `-x -I` run, with no `-r`, prints the single form `10 (per frame, and per whole-track re-read)` | `rips/*.log:18`; `session/transcript.txt` |
| the per-frame limit returning on an unreadable sector | **not exercised.** No read failed, so the path `.15` fixed was never reached on a drive | — |
| `Handshake:` on a release | `round 25 lap 5 closed, verdict GO -- released build`, on every rip. Correct for the tree `df91ae7` was built from | `rips/*.log:3` |
| secure re-read | 13 of 14 `converged after 3 reads`. Track 5 `did NOT converge after 3 reads (repeat limit hit)`, `EAC CRC32 E0036697`, the same CRC as on 2026-09-15. Platterpus re-read it with `-Z 2 -l 5`: it **converged, with the same CRC**. So on this run the non-convergence produced the same bytes | `rips/secure-reread.log`; `rips/secure-reread.platterpus-addendum.txt` |
| paranoia `Scope:` | present on 14 of 14 tracks of `secure-reread.log`. Per-track counters sum to 21,678 against a disc total of 65,406, a ratio of 3.02. On the five single-pass rips that wrote track blocks, the sums equal the disc totals exactly and `Scope:` is absent | re-derived here from the filed logs |
| AccurateRip | 13 of 14 exact; track 5 matches only `Accurip 450` at confidence 200, as on every whole-disc rip of this disc | `rips/secure-reread.log` |
| `Read stalls:` | `none (no read exceeded 10s)` on all seven footers. That is the expected result on healthy media and evidence of nothing | — |
| `Log FUN512:` | 7 of 8 logs verify with `cyanrip -Y`. The eighth is the killed log, which has none | run here |
| the interrupt footer | `cancel-me.log`: `Ripping errors: 1`, `Rip completed:  no (interrupted by SIGTERM, 0 of 14 tracks)`, `Interrupted at: track 1, mid-read`, `Log FUN512:` present. The footer arrived 7.3 s after the wrapper exited (app log, 21:34:56) | `rips/cancel-me.log:87-93` |
| `Encoder errors:` on hardware | **first time**, since `.14` introduced it. Two of its three arms: `none; 2 tracks encoded` (and 14, and 1) on rips, and `not applicable; no track was encoded` on the no-offset refusal. The `failed` arm was not reached | `rips/*.log`; `session/transcript.txt` |
| the abort footer | `cyanrip -N -l 1`, exit 1, `Offset is unset!` at column 0, `Rip completed:  no (aborted, 0 of 14 tracks)` | `session/transcript.txt` |
| pregaps | `sub-channel (not signalled by TOC)` on 13 tracks and `lead-in` on 1. The cue agrees: track 2's `INDEX 00 03:11:02` is 14,487 − 160 = 14,327 frames into file 1 | `rips/secure-reread.log`, `.cue` |
| `-x` | `at least 2048 sectors … search ceiling reached`, for the **eleventh** time, against `cd-paranoia -A`'s 137–140. **Do not cite our cache figure** | `session/transcript.txt:970` |

## Three findings, all ours, all older than `.15`

### 1. An interrupted track is counted as "ripped partially accurately"

`rips/cancel-me.log`:

```
Tracks ripped accurately: 0/14
Tracks ripped partially accurately: 1/14
...
Rip completed:  no (interrupted by SIGTERM, 0 of 14 tracks)
Interrupted at: track 1, mid-read
```

No track completed, and no track block was written. The tally counted track
1 anyway. Its read had passed sector 450 before the signal, so `Accurip 450`,
a checksum over that one sector, matched the database, while v1 and v2 over a
partial read could not.

**Platterpus found it too, independently.** Their report for the same rip,
`rips/cancel-me.platterpus.json`, says in `partially_accurate_summary`: *"the
ripper's own tally reads 1/14, which does not agree with the 0 offset-variant
tracks listed per track in this log"*.

**It is in every interrupted rip we hold**: the eight filed `cancel-me.log`
files that carry `Interrupted at: track 1`, from 2026-09-10 to this one, all
print `1/14` over `0 of 14 tracks`. Nobody here noticed it in any of them.

**Cause:** `cyanrip_log_finish_report()` counts every track in the database,
whether or not its read finished. `t->audio_ripped` already marks a track
whose read finished, and the `-j` record already honours it for exactly this
reason (`src/cyanrip_main.h:223-235`). The log's tally did not. **Fixed for
`.16`.** Upstream has the same loop, and on SIGINT it `break`s to the same
report (`master:src/cyanrip_main.c:2070-2111`). That was read from the source,
not run.

### 2. `-H` tags every file `media: HDCD`, whatever the disc is

`session/transcript.txt`, the two P3 runs (`-H -E` and `-H -W`):

```
1366:             HDCD detected: no
1396:               media:                         HDCD
```

The tag is set from the setting (`src/cyanrip_main.c:2079-2080`), before any
audio is read, and it goes into every output file. It is the same shape as
upstream's `(deemphasis applied)` printed from the settings, which this fork
fixed in round 15, and it is upstream's code verbatim. It is in all eight
filed transcripts with a P3 section, from 2026-09-10 on, twice in each, and
none of them ever says `HDCD detected: yes`. **Fixed for `.16`**: the
tag says `CD`, which is true of every disc cyanrip reads. `HDCD detected:` is
the line that reports HDCD, per track.

### 3. The album loudness block describes whatever was read

`rips/cancel-me.log:75`: `Album integrated loudness (R128): -14.4 LUFS`, over
about 40% of track 1, the point the cancel reached. The same is true of every `-l` rip: two tracks'
loudness, labelled "Album". **Not fixed.** Changing it means changing or
qualifying four rows Platterpus parses, and that is a wording decision for the
next round. It is in `docs/KNOWN-ISSUES.md`.

## One thing in Platterpus's output

On the interrupted rip, `partially_accurate_summary` reads *"0 of 0 tracks
matched"*. The disc has 14. Their denominator comes from the track blocks they
parsed, not the disc's track count. It is a one-word nit in their report, and
their disagreement note beside it is correct.
