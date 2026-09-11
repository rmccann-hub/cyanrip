# Rig session 2026-09-11, build `ddc1e8c` — **Run B again. This is NOT Run A.**

Platterpus acceptance session `20260911T141012Z`, `platterpus 0.6.45` +
`cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-gddc1e8c)`, PIONEER BD-RW
BDR-209D. Delivered as `platterpusbundle20260911t141012z.tar.gz`.

## What it is, and what it is not

**It is the FIFTH Platterpus-driven session and it settles no close condition.** Eight
Platterpus-driven album rips, every one `-o flac -T unicode -r 3 -N`. **No
`-H`, no `-E`, no `-W`, no `-o pcm`** in any of the eight `Invoked as:` lines —
read from the logs, not from the folder names, because a folder name is not
evidence. So **clause 2 is untouched**, exactly as on 2026-09-10, and round
16's close condition still needs Run A: `tools/rig-round16.sh` at `5bbb5ae`.

Searched for Run A's own artifacts before concluding: no `banner.txt`, no
`hdcd-deemph/`, no `round16-accept.py` output anywhere in the bundle. The two
files that match `rig-round16` are a **comment** in their `report.json` citing
our script by name, and one line in a rotated app log. Neither is an execution.

## What it does establish

**Clause 1 again.** `AccurateRip:    found` in all eight logs, no `-A` passed,
over a live network. **Counted rather than guessed: ten of the twelve filed rig
bundles carry that line**, so this is confirmation and not new coverage. A first
draft of this file called it "a fourth time", which was invented.

**All eight logs verify.** Run against our own tool at `platterpus-fork-g84ce459`:

```
$ cyanrip --verify-log <each of the eight>
Log "…" checksum valid.          (8 of 8, exit 0)
```

**That includes `cancel-me.log`, which their record calls unverifiable** — and
this is the sharp part. `session/DIAGNOSTICS.txt` carries, for this session:

> `cancel me … .log` carries NO 'Log FUN512:' checksum line at all, so the
> ripper had nothing to verify it against (exit 3).

The file carries one, and it verifies. **The claim is false about the file**,
and the cause is the race their round-16 lap 10 §C1 diagnosed: the verify ran
at `15:17:36Z` and the log's own `Ripping finished at` is `15:17:43Z` —
**seven seconds before it existed in finished form.** Their §C1 fix is at
`81ca989`/`c394229` on an unmerged branch and is not in `0.6.45`, which they
said plainly, so this is a reproduction rather than a new finding. What is new
is that it is now provable in one command instead of inferred from timestamps.
The 2026-09-10 bundle's `cancel-me.log` verifies too — and **that one was
already run and recorded**, in `docs/SETTLED.md`'s interrupt-footer row, whose
check command is exactly `cyanrip -Y …/cancel-me.log`. A first draft of this
file said nobody had run it. Somebody had.

**A second SIGTERM that reached cyanrip mid-read.** `Ripping errors: 1`,
`Rip completed:  no (interrupted by SIGTERM, 0 of 14 tracks)`, `Interrupted at:
track 1, mid-read`, and a `Log FUN512:` line present. The first was 2026-09-10;
one observation is an anecdote and two are a behaviour.

**Not new, checked rather than assumed:** `Secure re-read:  did NOT converge
after 3 reads (repeat limit hit)` appears twice here, and it is **already** in
the 2026-09-03, 09-05, 09-07 and 09-10 evidence. The `Offset is unset!` abort
footer with exit 1 is likewise already settled — `docs/SETTLED.md`, 2026-09-03.
Both looked new and neither is.

**Still not travelling: our `-j` records — and "still" understates it.** Every
invocation passes `-j cyanrip-diagnostics-<stamp>.json` and the bundle contains
**zero** of them. Counted across every filed session rather than recalled:
**twelve bundles, zero `-j` records, ever.** Not "the second session running" —
it has never once happened. That is Platterpus's own lap 10 §I4 item and this
is the twelfth observation of it.

## Two more §I4 items, both still open, both checked here rather than assumed

* **Their application log still carries no UTC offset.** First line of
  `session/platterpus-app-log.txt` is `2026-09-09 23:13:47,388` — bare local
  time, while every other artifact in the bundle is offset-bearing. This is the
  ambiguity that made our own lap 9 §2 reason from a timezone difference that
  did not exist.
* **The `zz-` rotation prefix is still there** — `session/zz-applog-rotations/`.
  It is the sort order that hid the decisive file from us on 2026-09-10.

## Nothing on the never-run list is touched, and two hits looked like it did

C2, `-f`, damaged media, CD-TEXT from a disc that has some, and `-x` **alone**
returning a drive all remain unrun. Checked rather than assumed, because the
transcript appears to contain both:

* **`-x` matches nine times and every one is prose** saying the opposite —
  *"`-x` is not in the rip argv builder at all, so no Platterpus rip
  exercises the cache"*. A grep hit is not a fact.
* **`C2` matches seven times inside `rc2`**, in `0.9.4-rc2+platterpus.11`. A
  pattern that nearly matches is worse than one that does not.

## The rips were RENAMED when filed, and here is the mapping

Same reason as the 2026-09-10 bundle, and the reason is theirs: their lap 14 §C
found that `*.eac.log` is a third spelling of their EAC export, and a
name-keyed exclusion that worked over their bundle failed over our filed copy.
**Renaming is a change to an artifact even when every byte survives.** Each row
below was produced by hashing the filed file, so the pairing is derived from the
bytes rather than from anyone's memory.

| filed here | as delivered in their bundle | sha256/16 |
|---|---|---|
| `after-cancel.cue` | `after cancel 20260911t141013 platterpus-fork-gddc1e8c.cue` | `a8ed110598279f7a…` |
| `after-cancel.eac.log` | `after cancel 20260911t141013 platterpus-fork-gddc1e8c (EAC-compatible).log` | `2eb90a2e6fde548e…` |
| `after-cancel.log` | `after cancel 20260911t141013 platterpus-fork-gddc1e8c.log` | `b7c8a8b0fc223ad4…` |
| `cancel-me.cue` | `cancel me 20260911t141013 platterpus-fork-gddc1e8c.cue` | `a53381c34b64e0aa…` |
| `cancel-me.eac.log` | `cancel me 20260911t141013 platterpus-fork-gddc1e8c (EAC-compatible).log` | `e5f7c0a2aedff9aa…` |
| `cancel-me.log` | `cancel me 20260911t141013 platterpus-fork-gddc1e8c.log` | `8003f8ecac3ead3d…` |
| `derived-mp3.cue` | `derived mp3 20260911t141013 platterpus-fork-gddc1e8c.cue` | `f5cfa96683ec588c…` |
| `derived-mp3.eac.log` | `derived mp3 20260911t141013 platterpus-fork-gddc1e8c (EAC-compatible).log` | `61982e3996399e0a…` |
| `derived-mp3.log` | `derived mp3 20260911t141013 platterpus-fork-gddc1e8c.log` | `16356c62eddf5e6e…` |
| `derived-wav.cue` | `derived wav 20260911t141013 platterpus-fork-gddc1e8c.cue` | `d1f832394e54ffd7…` |
| `derived-wav.eac.log` | `derived wav 20260911t141013 platterpus-fork-gddc1e8c (EAC-compatible).log` | `48266b6a85c637e0…` |
| `derived-wav.log` | `derived wav 20260911t141013 platterpus-fork-gddc1e8c.log` | `6b2e17c7037abe56…` |
| `derived-wavpack.cue` | `derived wavpack 20260911t141013 platterpus-fork-gddc1e8c.cue` | `bafba050aad050c5…` |
| `derived-wavpack.eac.log` | `derived wavpack 20260911t141013 platterpus-fork-gddc1e8c (EAC-compatible).log` | `1379d50c0fce5d19…` |
| `derived-wavpack.log` | `derived wavpack 20260911t141013 platterpus-fork-gddc1e8c.log` | `43e649822d9c05a8…` |
| `full-acceptance-angle-bracket-2.cue` | `full acceptance∶ angle‹bracket 20260911t141013 platterpus-fork-gddc1e8c.cue` | `47b123f60c605b6a…` |
| `full-acceptance-angle-bracket-2.eac.log` | `full acceptance∶ angle‹bracket 20260911t141013 platterpus-fork-gddc1e8c (EAC-compatible).log` | `bd0fc84076acec74…` |
| `full-acceptance-angle-bracket-2.log` | `full acceptance∶ angle‹bracket 20260911t141013 platterpus-fork-gddc1e8c.log` | `6c2cb9f933a5c956…` |
| `full-acceptance-angle-bracket.cue` | `full acceptance∶ angle‹bracket 20260911t141013 platterpus-fork-gddc1e8c.cue` | `7059a61c77028034…` |
| `full-acceptance-angle-bracket.eac.log` | `full acceptance∶ angle‹bracket 20260911t141013 platterpus-fork-gddc1e8c (EAC-compatible).log` | `39eed92ca12530f8…` |
| `full-acceptance-angle-bracket.log` | `full acceptance∶ angle‹bracket 20260911t141013 platterpus-fork-gddc1e8c.log` | `26479091f6e05755…` |
| `secure-reread.cue` | `secure reread 20260911t141013 platterpus-fork-gddc1e8c.cue` | `2bb07ce243a96711…` |
| `secure-reread.eac.log` | `secure reread 20260911t141013 platterpus-fork-gddc1e8c (EAC-compatible).log` | `d9f25cd3bd65b4ea…` |
| `secure-reread.log` | `secure reread 20260911t141013 platterpus-fork-gddc1e8c.log` | `7033adfab4bc20cd…` |

**Two rips share a delivered name** — their bundle carries two
`full acceptance∶ angle‹bracket …` runs in two directories distinguished only
by the directory, so the second takes a `-2` suffix here.

## What is NOT filed, and why

The delivered tarball is 59 MB. Filed: the eight rip logs, their EAC
companions, the eight cues, and the session's transcript, manifest, sources and
diagnostics, plus the current application log — 7.7 MB.

Not filed: 163 UI screenshots under `extra10…/`, the five rotated 8 MB
application logs, and the eight `.platterpus.json` per-rip reports (6.1 MB for
one of them). **These are evidence about Platterpus's UI and internals, not
about cyanrip's output**, and `session/SOURCES.txt` is filed whole so the full
inventory of what the session collected is recoverable from this directory.
Saying which is which is the point: an absence somebody can read is a finding.
