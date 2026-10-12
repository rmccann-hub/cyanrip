# Rig session 2026-10-12 — build `ca3f3ea`, Platterpus 0.7.103, **Full**

**Read the build, not the date.** This is `ca3f3ea`, `+platterpus.21`, stable,
through Platterpus **0.7.103** (`v0.7.103`, `2f7855b`), whose `MANIFEST.txt`
says *"ripper build wanted platterpus-fork-gca3f3ea ONLY — the approved
production pin"*. Every log opens with `cyanrip 0.9.4-rc2+platterpus.21
(platterpus-fork-gca3f3ea)` and reads `Handshake: round 30 lap 17 closed,
verdict GO -- released build`.

**It is not round 32's test.** Round 32's lap 1 names `.22` with 0.7.103
(S6). `tools/ingest-bundle.py --peer` reads `.21` and 0.7.103 as the newest
pair when the run began, 04:09:47Z; `.22` was committed by `d92bc5a` at
04:39:21Z and reached the remote at 04:50:27Z (our push reflog), 41 minutes
into the run. 0.7.103 installs `.21`, its approved pin, so this is that pair
on the reference disc, and evidence about it, not about `.22`.

**The script's verdict is a pass**: pass 424, fail 0, error 0, skipped 0,
blocked 0, unreachable 1, info 5, `ok: true`, `counts_as_evidence: true`, run
size full (`session/run/report.json`). The unreachable step is section E2
(L566), as on 2026-10-06 and 2026-10-07: the drive is in AccurateRip's list,
so the offset refusal it tests cannot be reached on it.

**Filed under the names it was delivered with.** `tools/ingest-bundle.py
--into` copied 51 members, each matching the archive (`sha256sum -c
SHA256SUMS`, 51 OK); the bundle carries no checksum list of its own this time.
The audio, the screenshots, the nine `-j` records, the `.platterpus.json`
files and the app-log rotations are not filed, and `SHA256SUMS` names each.

| | |
|---|---|
| bundle | `platterpusbundle20261012t040947z.tar.gz`, handed over by the operator on 2026-10-12 |
| sha256 | `5d9e90382f76f8459975706fa5b6509964781986601e8764d02e7c227e69ae9a` |
| size | 7,309,055 bytes, 104 members |
| session | `20261012T040947Z`, `started_at` 04:09:47Z, ended 09:27Z at the earliest |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667, C2 unsupported |
| disc | the reference disc, 14 tracks |

## What it shows

- **All eleven cyanrip logs verify with `-Y`** and end in a signed footer.
  `cancel me` is the one incomplete rip, `interrupted by SIGTERM, 0 of 14
  tracks`, as the section intends. Nine logs carry `Consumer:
  platterpus/0.7.103`; the two pre-emphasis rips, which the script invokes
  directly (`cyanrip -N -s 667 -l 1 -H -W`, and `-E`), read `not identified`.
- **AccurateRip 12 of 14 in both whole-disc rips**, tracks 3 and 5 matching on
  one frame only, as on every run of this disc. `.21` prints that tally as
  `Tracks ripped partially accurately: 2/14`; `.22` renames it. No read
  stalled past 10 s in either, and both read `Ripping errors: 0`.
- **The secure re-read** (`-Z 2`): twelve tracks converged after 3 reads,
  track 4 after 4, and track 3 hit the repeat limit: four reads with four
  checksums, then a fifth agreeing with the first, so it kept `029BB984`.
  Track 5 converged after 3 reads on `E0036697`, which the database does not
  hold whole.
- **The first rip's securing pass** (`-Z 2 -l 3,5`): track 3 read five
  checksums in five reads and kept the last, `750F8F8A`. Track 5 read
  `C96464AB`, `4065BECC`, `E0036697`, `E0036697` and, derived from the tie rule
  and the kept checksum, `4065BECC` again, and kept `4065BECC`: two reads, the
  newer of the two pairs. **`C96464AB` is the one checksum of track 5 that
  AccurateRip matches whole** (v1 confidence 129, v2 200), and it was read once
  and not kept. The log cannot show that, since only the kept read is looked
  up.
- **Across every filed log**, `tools/cross-rip.py docs/rig-*` counts 80 reads
  of track 5 with five checksums: `E0036697` 45, `6902BCF0` 22, `C96464AB` 8,
  `4065BECC` 4, `BBB13C9B` 1. Track 3 has 98 reads with 51 checksums, and
  `59D352DD`, read 12 times, is the one AccurateRip matches.
- **`.22`'s new repeat-limit clause would not have printed in this run**, read
  from source rather than run: at the limit the kept read is the one with the
  most reads, the newest on a tie (`src/cyanrip_main.c:868-877`), and in all
  three repeat-limit cases here that read includes the last, so `kept !=
  filed` (`src/cyanrip_main.c:1234`) is false.
- **`-f` found `+667` at confidence 14** (`session/transcript.txt:1185`), the
  third run to do so.
- **The cache probe said `128 to 255 sectors`** (uncached read 244.2 ms,
  cached 1.6 ms, three re-reads after a 256-sector run at 29.9 ms or more,
  `session/transcript.txt:1251`), beside `cd-paranoia -A`'s **137 sectors**
  (`session/run/cacheprobe1347.txt:69`). The third run in agreement, after
  137 on 2026-10-06 and 144 on 2026-10-07.
- **Track 9's pregap is 94 frames in both `Gaps:` lists** this time; on
  2026-10-07 it was 94 in one and 95 in the other.
- **The cancel** (L863, `info`): podman does not forward the wrapper's
  SIGTERM, so the ripper still held the drive when Platterpus's rescue fired
  5 s after Cancel, and it signed its log after the rescue's SIGTERM.
