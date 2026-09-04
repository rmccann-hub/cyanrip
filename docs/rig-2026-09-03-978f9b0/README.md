# Rig session 2026-09-03 — build `978f9b0`, Platterpus 0.6.34

**Date the session by its build, never by its date.** This is `978f9b0` =
`cyanrip 0.9.4-rc2+platterpus.11`, the round-15 pin, driven by Platterpus
`0.6.34` on a PIONEER BD-RW BDR-209D, on the 14-track disc used since
2026-08-26.

Delivered as `platterpusbundle20260903t110812z.tar.gz`,
`sha256 28618b5a…1bd443c`. Every file under `rips/` and `session/` is
byte-exact from that archive and checksummed in `SHA256SUMS`; the names are
flattened to match the earlier sessions, and nothing else was touched.

**What is NOT here, and it is a choice rather than an omission.** The seven
per-rip `*.platterpus.json` reports total 19 MB, almost all of it their
embedded debug log and per-sample ETA trace. Their hashes are in `SHA256SUMS`
so a copy can be identified. The 2026-08-26 session filed no JSON either, and
`session/DIAGNOSTICS.txt` carries the diagnostic entries the findings below
rest on. The 219-file screenshot directory is likewise not filed.

## What this session is

**It is the CC-1 hardware evidence: a pass on the released pin.** Every rip
here reports `cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-g978f9b0)` and
`Consumer: platterpus/0.6.34`. Seven rips, of which two are whole-disc.

`rips/full-acceptance-angle-bracket.log` is the one to read: `Tracks to rip:
all`, `Ripping errors: 0`, `Rip completed:  yes (14 of 14 tracks)`.

**All seven logs verify.** `cyanrip -Y` returns 0 on each, run here against a
build *later* than the one that wrote them — so this re-confirms the
cross-build property 2026-08-26 established, and it independently proves the
flattening above altered no byte:

    for f in docs/rig-2026-09-03-978f9b0/rips/*.log; do
        case "$f" in *.eac.log) continue;; esac
        ./build/src/cyanrip -Y "$f" >/dev/null || echo "FAILED: $f"
    done

## The finding, and it is ours

`session/DIAGNOSTICS.txt` records **thirteen `[error]` entries**, of which the
recurring one is

    [error] ripper.fatal_message
      Done; (no matches found, but hit repeat limit of 3)
      tool: cyanrip

The same rip's own report reads `status: success`, `ripper_exit_code: 0`,
`14 of 14 tracks`, `health_status: No errors occurred` — beside
`error_count: 5`. In `rips/full-acceptance-angle-bracket.log` that string
appears three times, at lines 222, 305 and 387, and each is **immediately
followed by `Track N ripped and encoded successfully!`**.

**`PROVIDER-CONTRACT.md` listed that string in P5, under a heading reading
*"Every string reachable on a failure path"*.** It was there on the strength of
`goto finalize_ripping` and nothing else — no failure exit in the search
window, no diagnostic wording — and `finalize_ripping:` is the ordinary
continuation, which flushes encoders and falls into that success line. The
contract is the API. This is our defect whatever else contributed to the
consumer's reading, and stating more than that would be a claim about code we
cannot read.

Fixed at `896a80a`: a bare `goto` is no longer treated as failure evidence, and
the seven rows in that state moved to **P5a, "Strings this document does NOT
classify"** — not established in either direction, which is the only claim the
generator can support. Two of the seven were the *convergence* line and the
loop that echoes the cue sheet. Pinned by `contract_fatal_inventory`.

## What this session retires, and the list is shorter again

Each of these had never been produced by any run. All are in the artifacts
above, not recalled.

- **The abort footer, and a diagnosed non-zero exit.** `session/DIAGNOSTICS.txt`,
  the `deps.command_failed` entry: `cyanrip -N -l 1` exited **1** having
  printed `Offset is unset! To continue with an offset of 0, run with -s 0!`
  at column 0, then `Rip completed:  no (aborted, 0 of 14 tracks)`. A
  diagnosable line before a non-zero exit, which is the property CLAUDE.md
  requires of every fatal path, observed rather than asserted.

  It also **settles one `goto end` row by running it**, which is what P5's
  legend said those rows needed.

- **`Secure re-read:  did NOT converge after 3 reads (repeat limit hit)`** —
  the non-converged verdict, on three tracks of two whole-disc rips. Only the
  converged arm had ever been seen (T1, 2026-08-26).

- **The PLURAL `Read stalls:` rendering.** `after-cancel.log` carries
  `5 reads exceeded 10s; longest 11s (track 1, LSN 8322)` and `cancel-me.log`
  the same with `LSN 1169`. 2026-08-26 produced the singular; the plural arm
  was unobserved.

Still untouched by any run: C2 (the drive reports it unsupported), `-f`,
damaged media, CD-TEXT from a disc that has some, and `-x` alone on a drive
that goes on to rip.

## The cancel scenarios, again

**`cancel-me.log` does not show a cancel.** It reads `Tracks to rip: 1, 2, 3`
and `Rip completed:  yes (3 of 14 tracks)`, and it carries a `Log FUN512:`
line. Same as 2026-08-26: a folder name is not evidence.

**But this session does hold evidence that a cancel happened** — which is a
different claim, and the distinction is the point. `session/DIAGNOSTICS.txt`
records, at 14:15:25, `cyanrip exit 3: No FUN512 checksum found in ".../cancel
me ....log"`, which is what a rip killed before it writes its own signature
looks like. That log was then re-run to completion and the completed one is
what the bundle carries. So: **the interrupted artifact existed and is not
here.** `none` and `unknown (reason)` are different claims, and this is the
second.

## Numbers worth keeping

| | |
|---|---|
| paranoia, disc `READ` | 64994 |
| paranoia, track 1 `READ` | 1202, over `rip_count: 3` |
| pregap source | 13 × `sub-channel (not signalled by TOC)`, track 1 `lead-in` |
| AccurateRip | 12 of 14 exact; 2 matched an offset-variant pressing |
| elapsed | 3 h 5 m 19 s for a 59:42 disc — 3.1× realtime |

The paranoia figures are the corrected claim's shape again: per-track counters
describe the **last pass** and the disc counters sum **every** pass, so they do
not sum under `-Z`. Do not add the per-track blocks up.

## One thing that is theirs and correct

`ripper_handshake_approval: unapproved` — *"build platterpus-fork-g978f9b0 is
NOT the build this Platterpus was verified against (platterpus-fork-gd9c058c)"*.
That is round 14's pin, which is what `0.6.34` was verified against, so the
field is right. Round 15 is the round that changes it. It is also why
`session/DIAGNOSTICS.txt`'s banner names `+platterpus.10` while every rip in
this bundle was made by `+platterpus.11`: the banner names the **approved**
pair, not the running one.
