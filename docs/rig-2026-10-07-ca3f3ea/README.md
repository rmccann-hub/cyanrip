# Rig session 2026-10-07 — build `ca3f3ea`, Platterpus 0.6.66, **Full**

**Read the build, not the date.** This is `ca3f3ea`, `+platterpus.21`, stable,
through Platterpus **0.6.66** (`v0.6.66`), whose `PIN_UNDER_REVIEW` is
`ca3f3ea`: the pair round 31 reviews. `tools/ingest-bundle.py --peer` reads both
as the newest when the run began. Every log opens with `cyanrip
0.9.4-rc2+platterpus.21 (platterpus-fork-gca3f3ea)` and reads `Handshake:
round 30 lap 17 closed, verdict GO -- released build`.

**The script's verdict is a pass**: pass 425, fail 0, error 0, skipped 0,
blocked 0, unreachable 1, info 5, `ok: true`, `counts_as_evidence: true`, run
size full (`session/run/report.json`). The unreachable step is section E2
(L567), as on 2026-10-06: the drive is in AccurateRip's list, so the offset
refusal it tests cannot be reached on it.

**Filed under the names it was delivered with**, so there is no rename mapping
to keep. `tools/ingest-bundle.py --into` copied 52 members, and each matches
the bundle's own `SHA256SUMS` (`sha256sum -c --ignore-missing`, 52 OK); the
audio and screenshots are not filed.

| | |
|---|---|
| bundle | `platterpusbundle20261007t033944z.tar.gz`, handed over by the operator on 2026-10-07 |
| sha256 | `a7e51546a8cd6dc14475a07de966a992305ad547410946bac284875abcb932fd` |
| size | 7,298,290 bytes, 105 members |
| session | `20261007T033944Z`, `started_at` 03:39:44Z |
| drive | PIONEER BD-RW BDR-209D, offset +667, C2 unsupported |
| disc | the reference disc, 14 tracks |

## What it shows

- **All eleven cyanrip logs verify with `-Y`** and end in a signed footer.
  `cancel me` is the one incomplete rip, `interrupted by SIGTERM, 0 of 14
  tracks`, as the section intends.
- **AccurateRip 12 of 14** in the full rip, tracks 3 and 5 matching on one
  frame only, as on every run of this disc. `tools/cross-rip.py` reads track 3
  sixteen times with thirteen checksums, none in the database whole. The secure
  re-read hit the repeat limit on track 3, five reads and five checksums,
  keeping the newest; and its track 5 kept `C96464AB`, which the database
  matches, where the first rip's securing pass converged on `E0036697`, which
  it does not.
- **`-f` found `+667` at confidence 14** (`session/transcript.txt:1188`),
  the second run to do so.
- **The cache probe said `128 to 255 sectors`** (uncached read 243.5 ms, cached
  1.8 ms, three re-reads after a 256-sector run at 31.8 ms or more), beside
  `cd-paranoia -A`'s **144 sectors** (`session/run/cacheprobe1348.txt:76`), whose
  capture is whole this time, 13,800 bytes. The second run in agreement.
- **Both `Gaps:` lists carry all nine pregaps**, so round 30's `Gaps:` finding
  did not show. **But track 9's pregap is 94 frames in one and 95 in the
  other**, two rips minutes apart. Across every filed log of this disc it reads
  94 and 95, in eleven sessions from 2026-09-03 on: a sub-channel measurement
  that varies between reads, which the log states as one value.
  `docs/KNOWN-ISSUES.md` has the entry.
