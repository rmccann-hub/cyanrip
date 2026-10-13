# Rig session 2026-10-13 — build `200530e`, Platterpus 0.7.104, **Full**

**Read the build, not the date.** This is `200530e`, `+platterpus.22`, the
release round 32 reviews, through Platterpus **0.7.104** (`v0.7.104`,
`3577be65`), whose `PIN_UNDER_REVIEW` is `200530e`. Every log opens with
`cyanrip 0.9.4-rc2+platterpus.22 (platterpus-fork-g200530e)` and reads
`Handshake: round 32 lap 1 OPEN, verdict OPEN (draft — lap not released for
reading) -- released build`, which is the line `.22` was built to print: lap 1
named `.22`'s own commit, so it was released after it (`Changelog.md`, `.22`).

**It is round 32's test**: the Full run of our lap 1's S6, as Platterpus's
lap 2 S3 amends it, on `.22` with 0.7.104. `tools/ingest-bundle.py --peer`
reads both as the newest when the run began, 11:29:19Z: `.22` is
`release_seq` 32, the newest ledger row, and `v0.7.104` is the newest tag,
created 2026-10-13T03:41:58Z.

**The script's verdict is a pass**: pass 424, fail 0, error 0, skipped 0,
blocked 0, unreachable 1, info 5, `ok: true`, `counts_as_evidence: true`, run
size full (`session/run/report.json`). The unreachable step is section E2
(L566), as on every run on this drive: it is in AccurateRip's list, so the
offset refusal E2 tests cannot be reached on it. The five `info` steps are the
same five as on 2026-10-12.

**Filed under the names it was delivered with.** `tools/ingest-bundle.py
--into` copied 52 members, each matching the archive (`sha256sum -c
SHA256SUMS`, 52 OK). The audio, the screenshots, the nine `--diagnostics`
records, the `.platterpus.json` files and the app-log rotations are not
filed, and `SHA256SUMS` names each. Home paths in nine filed files are
replaced by `~`. The owner's name was not checked, because no local list of
names exists here, and not checked is not the same as not present.

| | |
|---|---|
| bundle | `platterpusbundle20261013t112919z.tar.gz`, handed over by the operator on 2026-10-13 |
| sha256 | `8ef9c63f45cc993c52b699bb74bbcc1b0fb8ec34d7d9584a94ebb537bfc4323e` |
| size | 7,430,485 bytes, 105 members |
| session | `20261013T112919Z`, `started_at` 11:29:19Z, ended 16:48Z at the earliest |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| disc | the reference disc, 14 tracks |

## What it shows

- **All eleven cyanrip logs verify with `-Y`** and end in a signed footer.
  `cancel me` is the one incomplete rip, `interrupted by SIGTERM, 0 of 14
  tracks`, as the section intends. Nine logs carry `Consumer:
  platterpus/0.7.104`. The two pre-emphasis rips, which the script runs
  directly, read `not identified (no --consumer given)`.
- **The one-frame tally reads under its new label on a drive**: `Tracks
  matched on one frame only: 2/14` in both whole-disc rips, beside `Tracks
  ripped accurately: 12/14`. Tracks 3 and 5 match on one frame only, as on
  every run of this disc. No read stalled past 10 s in any rip, and every
  rip but `cancel me` reads `Ripping errors: 0`.
- **The repeat limit's new clause had no cause to print.** Track 3 hit the
  limit twice: in the secure re-read (`-Z 2`) and in the first rip's
  securing pass (`-Z 2 -l 3,5`). Both times its five reads gave five
  different checksums, so the newest read was kept, and that is the last.
  The clause names the last read's checksum only when the kept read is not
  the last, so it rightly stays silent. Both times the track reads `read with
  errors`, `.20`'s wording for a `-Z` read that never agreed. **The arm that
  prints has not run on a drive.**
- **No pregap search failed**, so the `Gaps:` list's new `pregap of track N
  unknown (reason)` line had no cause to print either. Nine pregaps printed,
  and no `None signalled`. **The arm that prints has not run on a drive.**
- **`--diagnostics` writes its record on `.22`.** 0.7.104 sends the long name
  in place of `-j`, and each of the nine logs that asks for a record has its
  record in the bundle, schema `cyanrip-diagnostics/7`, under the name the log
  gives. Until this run, that `.22` writes the record under the long name was
  read from its pre-pass (`src/cyanrip_main.c:3205` at `200530e`), not run.
- **The securing pass's record is not in the bundle, by Platterpus's
  design.** The pass asked for `cyanrip-diagnostics-20261013T121955Z.json`.
  The bundle's manifest counts nine records found in the rips folders, and
  2026-10-12's bundle lacks its securing pass's record the same way.
  Platterpus runs that pass in a temporary folder that it deletes afterwards
  (`platterpus@39b6c366:src/platterpus/workers/rip_worker.py:2338-2341`).
  `.22` built from `200530e`, given the pass's own arguments on a disc image,
  writes the record and exits 0.
- **The secure re-read** (`-Z 2`): twelve tracks converged after 3 reads,
  track 4 after 5, and track 3 hit the repeat limit as above. Track 5
  converged after 3 reads on `E0036697`, which AccurateRip does not hold
  whole.
- **The first rip's securing pass** (`-Z 2 -l 3,5`): track 3 hit the repeat
  limit as above. Track 5 first read `C96464AB`, then `E0036697` three times,
  and kept `E0036697`. **`C96464AB` is the one checksum of track 5 that
  AccurateRip matches whole** (v1 confidence 129, v2 200), and, as on
  2026-10-12, it was read once and not kept. The log cannot show that, since
  only the kept read is looked up.
- **Across every filed log**, `tools/cross-rip.py docs/rig-*` counts 88 reads
  of track 5 with five checksums: `E0036697` 52, `6902BCF0` 22, `C96464AB` 9,
  `4065BECC` 4, `BBB13C9B` 1. Track 3 has 114 reads with 58 checksums, and
  `59D352DD`, read 12 times, is still the one AccurateRip matches.
- **`-f` found `+667` at confidence 14** (`session/transcript.txt:1186`), the
  fourth run to do so and the first on `.22`.
- **The cache probe said `128 to 255 sectors`** (uncached read 244.7 ms,
  cached 1.9 ms, three re-reads after a 256-sector run at 32.4 ms or more,
  `session/transcript.txt:1253`), beside `cd-paranoia -A`'s **144 sectors**
  (`session/run/cacheprobe1347.txt`). The fourth run in agreement.
- **Track 9's pregap is 95 frames in the whole-disc rip and 94 in its
  securing pass**, the variation `STATUS.md`'s `subchannel-pregap-varies`
  records.
- **The cancel** (L863, `info`): podman does not forward the wrapper's
  SIGTERM, so the ripper still held the drive when Platterpus's rescue fired
  5 s after Cancel, and it signed its log after the rescue's SIGTERM.

**Nothing in it is a defect of ours** that this reading found. It is our
reading of round 32's run, and round 32's S6 needs Platterpus's too, in their
lap 8.
