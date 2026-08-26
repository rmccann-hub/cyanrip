# Rig session 2026-08-26, build `d9c058c`

Named by its build, not its date, because two sessions have already run on one
date and a claim about one was checked against the other's log.

- **Ripper**: `cyanrip 0.9.4-rc2+platterpus.10 (platterpus-fork-gd9c058c)`,
  which is an ancestor of `platterpus-fork` (`git merge-base --is-ancestor`).
- **Consumer**: `platterpus 0.6.28 (296a69d)`, reported by the caller and, as
  every log says, not verified by cyanrip.
- **Drive**: `PIONEER  BD-RW   BDR-209D` revision 1.51, `/dev/sr0`, read offset
  `+667`, C2 `unsupported by drive`.
- **Disc**: a 14-track Police compilation, `AccurateRip: found`.
- Collected `20260826T125323Z`; the rips themselves ran at `091428`.

`SHA256SUMS` covers every file here. Six rips were made; each is a real read of
a physical disc and cannot be re-taken.

## What this retires, and each is checkable from the files here

**1. Secure re-read on hardware. This was T1, and no run had ever produced
it.** `rips/secure-reread.log` was ripped with `-Z 2 -r 3` and reports

    Secure re-read:  converged after 3 reads

on **all 14 tracks**, with the `Scope:` caveat beside each.

    grep -c "Secure re-read:  converged after 3 reads" rips/secure-reread.log   # 14

**2. A non-zero `Read stalls:` count.** `rips/cancel-me.log` carries

    Read stalls:    1 read exceeded 10s; longest 11s (track 3, LSN 37086)

which is the populated, singular rendering of `crip_stall_summary_line()`,
byte-for-byte against its format string -- and the shape `tests/stall.c:370`
pins from a synthetic stall. A real drive stalling on real media produced the
same line the unit test asserts. Until now the only wording any artifact had
ever shown was `none`.

**3. The `Cache model:` sector arm on a real drive.** `1200 sectors (drive
cache size not probed)`, plural, from `cyanrip_log.c:138`. Every disc-image
fixture takes the image arm, and the golden reference is generated with `-P 0`,
so no committed artifact had ever shown this one.

**4. `-Y` verifies a log written by a different build.** All six logs verify
exit 0 against a later binary, so the FUN512 chain holds across builds and off
real hardware, not only within one tree.

## What it confirms about `tests/logrender.c`, written the same day

That test builds AccurateRip states by hand because the suite has no network.
This disc **is** in the database, so for the first time the synthetic
renderings can be checked against a real one. Every rule agrees:

- **"not found" is attached only when NEITHER version matched.** Twelve tracks
  report `v1 (accurately ripped, N)` *and* `v2 (accurately ripped, 200)`; two
  report `not found` on *both*. There is no track anywhere in the log where one
  version claims an accurate rip and the other claims not found -- which is the
  rule the test pins, and which the first draft of that test asserted backwards.
- **The 450 fallback appears only when both versions failed.** Exactly two
  `Accurip 450:` lines, matching the two double-failures.
- **Both tally denominators are the disc's track count.** `Tracks ripped
  accurately: 12/14` above `Tracks ripped partially accurately: 2/14`; they add
  to 14 and are counts over one population.
- **The zero-checksum guard correctly stayed silent**: both 450 matches carry
  confidence 200, and both checksums are non-zero (`BF62B1DA`, `4CCBCF89`), so
  the caveat wording is not due and is not printed.

## The corrected paranoia invariant, re-checked on new evidence

Round 5 recorded "per-track counters sum to the disc totals" as verified. It is
false whenever anything re-read, and this disc re-read every track three times:

| counter | sum(per-track) | disc total | ratio |
|---|---|---|---|
| `READ` | 21630 | 65268 | **3.02** |
| `OVERLAP` | 525 | 1488 | 2.83 |
| `VERIFY` | 4355 | 9203 | 2.11 |
| `FIXUP_ATOM` | 24 | 38 | 1.58 |
| `FIXUP_EDGE` | **0** | **2** | — |

`READ` lands on 3.02 for three reads a track, as the corrected model predicts.
**`FIXUP_EDGE` is the sharpest case anyone has produced**: the last pass needed
no edge fixups on any track, so summing the per-track blocks gives **zero** for
a disc that recorded **two**. A consumer trusting the old invariant would report
none. The `Scope:` line exists to stop exactly that, and here is a disc nobody
constructed that demonstrates it.

## What it does NOT establish

- **The cancel path.** Two rips are named `cancel me` and `after cancel`, and
  **neither log shows an interrupted rip.** Both were invoked with a narrowed
  `Tracks to rip:` (`1, 2, 3` and `1, 2`), both finished normally, and both
  footers read `Rip completed:  yes`. cyanrip ripped exactly what it was asked
  for. If these were meant to exercise a mid-rip cancel, the artifacts do not
  show one, and the interrupt/abort footers stay without hardware evidence.
- **C2, `-f`, damaged media, CD-TEXT from a disc that has some, and the
  diagnosed-abort exit code.** Untouched again: the drive reports C2
  unsupported, and every rip here reported `Ripping errors: 0`.
- **`-x` on a drive that goes on to rip.** Not exercised in this session.

## The one open defect, and it is not attributed

`cyanrip --version` through the rig's `~/.local/bin/cyanrip` **hung and was
killed**, twice:

- `session/rigsession-stdout.txt` -- probe `P3` produced a 0-byte artifact and
  the session summary stops there with no exit line.
- `session/probes-versions.txt` -- `timeout -k 10 60 ... --version` returned
  **exit 137**, SIGKILL after the 60-second cap.

**Against which**: `session/probes-doctor.txt` shows Platterpus invoking the
same path at `08:54:33` and getting `cyanrip 0.9.4-rc2+platterpus.10
(platterpus-fork-gd9c058c)` back within a third of a second -- three seconds
before the rig probe hung on it.

**Not reproduced here, and not attributed to cyanrip.** Measured on this tree's
binary with no drive, interleaved, after a warm-up run: `--version` 0.039 /
0.042 / 0.041 s, `-v` 0.037 / 0.041 / 0.038 s, `-V` 0.038 / 0.038 / 0.034 s.
The three flags are indistinguishable. A first reading of 10.8 s for `--version`
was a freshly-linked binary, not the flag, and it did not survive a re-run --
recorded because it is exactly the shape of claim this seam exists to catch.

`~/.local/bin/cyanrip` is a host-exported wrapper on that machine rather than
the binary, so the artifacts locate the hang in the invocation and not in any
code either project can point at. **What would settle it** is one probe run on
the rig, and it belongs to whoever holds the machine:

    time timeout 60 ~/.local/bin/cyanrip -v            # short flag, same wrapper
    time timeout 60 <the real binary path> --version   # long flag, no wrapper
    time timeout 60 distrobox-enter -n <box> -- true   # the wrapper alone

If the third hangs, nothing in either program is involved.
