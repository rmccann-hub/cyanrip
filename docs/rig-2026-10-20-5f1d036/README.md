# Rig session 2026-10-20 — build `5f1d036`, Platterpus 0.7.110, **Full**

**Read the build, not the date.** This is `5f1d036`, `+platterpus.25`, the
release round 35 reviews since our operator moved the round to it on
2026-10-19 (our round 35 lap 15), through Platterpus **0.7.110** (`v0.7.110`,
`e4b0115d`), whose `PIN_UNDER_REVIEW` is `5f1d036`. Every log opens with
`cyanrip 0.9.4-rc3+platterpus.25 (platterpus-fork-g5f1d036)` and reads
`Handshake: round 35 lap 12 OPEN, verdict OPEN -- released build`: `.25` was
built when our lap 12 was our newest, and a build can never name the lap that
announces it.

**It is round 35's test**: the Full run of our lap 15's S6, on `.25` with
0.7.110. `tools/ingest-bundle.py --peer` reads both as the newest when the
run began, 11:36:56Z: `.25` is `release_seq` 36, the newest ledger row, and
`v0.7.110` is the newest tag, created 2026-10-20T00:12:07Z.

**The script's verdict is not a pass**: pass 434, fail 1, error 0, skipped 0,
blocked 0, unreachable 1, info 6, `ok: false`, `counts_as_evidence: true`,
run size full (`session/run/report.json`). **The failure is in Platterpus's
script, not in `.25`.** Step L1408 expects `cyanrip -N -l 1`, a rip with no
offset set, to exit 1 (`session/transcript.txt:1506-1525`). `.25` refused it
as before, `Offset is unset! To continue with an offset of 0, run with -s 0!`,
and exited **64**, the class our round 35 lap 9 S12 proposed for this refusal
and Platterpus's lap 11 S7 accepted, *"`Offset is unset!` is `64`, its remedy
an argument"*. Their script still reads `expect-exit 1` there, at `v0.7.110`
(`platterpus@e4b0115:src/platterpus/rig_scripts/fullacceptance.txt:1408`) and
at their `main` (`platterpus@10e1b76`, line 1409). The step's other check,
L1409 `expect-cyanrip Offset is unset`, passed. `.25`'s Changelog said
`Offset is unset!`'s exit is now a class, and its list of what the run must
cover named the cancel step's new exit and not this one. The unreachable step
is section E2 (L569), as on every run on this drive: the disc is in
AccurateRip's list, so the offset refusal E2 tests cannot be reached on it.

**Every member matches the sender's own hash**: `tools/ingest-bundle.py`
checked each of the 106 members the bundle's `MANIFEST.txt` hashes against
it, and all 106 match byte for byte.

**Filed under the names it was delivered with.** `tools/ingest-bundle.py
--into` copied 51 members, each matching the archive (`sha256sum -c
SHA256SUMS`). The audio, the screenshots, the eleven `--diagnostics` records,
the `.platterpus.json` files and the app-log rotations are not filed, and
`SHA256SUMS` names each. **Nothing needed replacing**: no filed file carried a
home path. The owner's name was not checked, because no local list of names
exists here, and not checked is not the same as not present.

| | |
|---|---|
| bundle | `platterpusbundle20261020t113656z.tar.gz`, handed over by the operator on 2026-10-20 |
| sha256 | `0820bad8a5d190b9048e02a4cd888c7f4c383c8ff6036d5b8603aaa01929ef2c` |
| size | 7,741,731 bytes, 107 members, 106 of them hashed in its `MANIFEST.txt` |
| session | `20261020T113656Z`, `started_at` 11:36:56Z, ended 17:00Z at the earliest |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| disc | the reference disc, 14 tracks |

## What it shows

What `.25`'s Changelog asked the run to cover, items 1 to 5, first:

- **1. The sub-channel ISRC read ran on a drive, and the reference disc
  returned none.** Every track block of both whole-disc rips reads `Disc
  ISRC:     none (libcdio returned none)`, and every track of the first rip's
  record has `isrc_disc` null with `isrc_disc_reason` `libcdio returned
  none`, so the line and the record agree, 14 of 14. This is the disc that
  carries none, as on `.23`. The arm for a disc whose sub-channel carries
  ISRCs, and the ISO 3901 check `.25` added, have not run on a drive: no such
  disc was in the run.
- **2. `--prefer-disc-isrc` was sent and changed no file.** The rips that
  send it (both whole-disc rips among them) found no disc code, so each
  track's `ISRC:` stays the value passed with `-t`, `GBAAM0201086` for track
  1. That is what it should do on this disc; its other arm needs a disc that
  carries ISRCs.
- **3. The bounded `-O` read did not run.** The script sets `force_overread`
  off (L220, L399) and no step passes `-O`, so no log carries a `Beyond disc:`
  line. `overread-bounded` stays open until a drive shows it.
- **4. The cancel step exits 143.** `cancel me` reads `Rip completed:  no
  (interrupted by SIGTERM, 0 of 14 tracks)` and `Ripping errors: 1`, and its
  record (`cyanrip-diagnostics-20261020T131854Z.json`) has `exit_code` 143,
  where `.24` and earlier exited 1. The rig is still in the one-signal world
  (L871, `session/transcript.txt:583`): podman does not forward the wrapper's
  SIGTERM, so the rescue's was the first. The forced quit after a second
  signal and `-I` with the tray empty did not run.
- **5. The `/10` record ran on a drive.** All eleven records read
  `cyanrip-diagnostics/10` and every track has `error_positions`,
  `error_positions_dropped` and `paranoia_all_reads`, null for a track the
  rip did not read. On the secure re-read, `paranoia_all_reads` is at least
  the log's last-read counters for all 14 tracks (track 3: `READ` 5,237 over
  its reads against 1,730 for the last); on the first rip, which read each
  track once, the two are equal for all 14. `error_positions` is empty in
  every record: paranoia reported no read error or skip, even on the reads
  AccurateRip shows were wrong.

And the rest, as regression checks:

- **All twelve cyanrip logs verify with `-Y`** and end in a signed footer:
  the eleven `.log` files and the log of the first rip's securing pass.
  `cancel me` is the one incomplete rip and the one with `Ripping errors: 1`;
  every other reads 0. No read stalled past 10 s.
- **AccurateRip**: both whole-disc rips read `Tracks ripped accurately: 12/14`
  and `Tracks matched on one frame only: 2/14`, tracks 3 and 5, as on every
  run of this disc. `AccurateRip ID: 001d420f-013bb370-e20dfe0e`.
- **The secure re-read** (`-Z 2`): all 14 tracks converged after 3 reads, and
  two converged on a wrong value: track 3 on `3D8FCF0C`, the fourth time a
  filed `-Z` rip has done so, and track 5 on `E0036697`. Each reads `not
  found` whole and matches only AccurateRip's one-frame entry.
- **The first rip's securing pass** (`-Z 2 -l 3,5`): track 3 converged after
  3 reads on `59D352DD`, which AccurateRip matches whole (v1 confidence 128,
  v2 200), and track 5 converged after 5 reads on `6902BCF0`, which it does
  not. **So of the four `-Z` results for tracks 3 and 5 in this run, three
  agreed on a wrong value and one was right; none was flagged by failing to
  converge.**
- **No read hit the repeat limit**, so the repeat limit's clause had no cause
  to print. **That arm has not run on a drive.**
- **No pregap search failed**, so no `Gaps:` list printed `pregap of track N
  unknown (reason)`. **That arm has not run on a drive either.**
- **Track 4's pregap read 158 frames in all twelve logs**, where round 34's
  run read zero in two.
- **Track 9's pregap is 95 frames in two logs**, the secure re-read and the
  second `full acceptance` rip, **and 94 in the other ten.** Platterpus's
  L1567 `expect-pregaps-agree` reports the same, graded `info`, naming the
  fork's `subchannel-pregap-varies` (`session/transcript.txt:1992-1996`).
- **Track 1's pregap reads 150 frames from the lead-in**, which this disc
  cannot tell apart from the old count, as on `.23`.
- **One of the two pre-emphasis rips names no caller again, for the same
  cause in Platterpus's runner as on 2026-10-16.** `r16deemphon` reads
  `Consumer: not identified (no --consumer given)` and asks for no record;
  the runner's note says the build was `no read exceeded 10s`
  (`session/transcript.txt:1544`), the first parenthesis of the C1
  refusal's output, which its banner latch takes as the build tag
  (`platterpus@e4b0115:src/platterpus/uiscript/runner.py:1954-1975`,
  `_latch_ripper_identity`). Our round 34 lap 3 S22 reported it; it is
  unchanged in 0.7.110. `r16deemphoff`, after the `-E` rip's banner reset the tag, names
  `platterpus/0.7.110`.
- **`-f` found `+667` at confidence 14** (`session/transcript.txt:1203`), the
  sixth run to do so: `.20`, `.21` twice, `.22`, `.23` and now `.25`.
- **The cache probe said `128 to 255 sectors`** (uncached read 362.7 ms,
  cached 1.5 ms, three re-reads after a 256-sector run at 58.7 ms or more,
  `session/transcript.txt:1271`), beside `cd-paranoia -A`'s **140 sectors**
  (`session/run/cacheprobe1360.txt`). The sixth run in agreement.

**It shows no defect in what `.25` changed.** The run's one failure is
Platterpus's script expecting the exit `.25` agreed to replace, and its other
finding for them, the build tag their runner takes from a refused rip, is the
one round 34 reported. Our round 35 lap 15 S18 said our first lap after this
run is `GO` unless the run shows a defect in `.25` that makes the pin unsafe;
this reading finds none. What the run did not reach, the bounded `-O`, a disc
that carries ISRCs, and the repeat limit's and the failed pregap search's
printing arms, stays open, and none of it is a defect shown.

**Every fact above can be re-derived** with `tools/read-run.py
docs/rig-2026-10-20-5f1d036 --cyanrip build/src/cyanrip`, beside
`tools/ingest-bundle.py`'s verdict on the bundle itself, and the records
with the bundle, whose `SHA256SUMS` names each.
