# Rig session 2026-09-07, build `978f9b0`

Dated by its build, never by its date -- two sessions have already run on one
calendar day here and a claim about one got checked against the other's log.

Received 2026-09-07 as `platterpusbundle20260907t030712z.tar.gz`, a Platterpus
evidence bundle from a real drive: **PIONEER BD-RW BDR-209D, firmware 1.51,
`/dev/sr0`**, ripping The Police, *Every Breath You Take: The Classics*, 14
tracks. Platterpus 0.6.40 (build `1654bdd`) driving
`cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-g978f9b0)`.

Their own summary: **222 of 230 steps passed, 8 failures.** Their manifest says
*"Send the file anyway: the failures are the point."* It was right to.

## What is here, and what is not

The bundle is 62 MB and 277 files. Filed here are the **1.6 MB of text**: every
rip's `.log`, `.cue` and EAC-companion log, the session transcript, Platterpus's
application log, its config, the argv-probe artifact, and the three bundle
headers.

**Deliberately not filed, and this is the list rather than a silence:**

* **229 PNG screenshots** of the Qt UI -- 229 of the bundle's 277 files, and
  very nearly the whole of its 62 MB. They are Platterpus's surface, not ours.
* **The eight `.platterpus.json` files**, 6.2 MB for one of them. Downstream
  derived data; we own none of it.
* **No cyanrip `-j` record is in the bundle at all**, and none could be filed
  because none was collected. Every rip was invoked with
  `-j cyanrip-diagnostics.json` -- a *relative* path, resolved against
  `cwd=/home/rmccann/Music/rips` -- so eight records exist on their disk and
  none travelled. Worth asking for; see finding 2.

## Finding 1 -- THE CANCEL DID NOT CANCEL, AND IT IS NOT OUR SIGNAL HANDLING

The single most consequential thing in this bundle, and the attribution took
three artifacts to settle.

Their check `expect-log-well-formed` failed with *"the log carries NO completion
footer ... NO `Log FUN512:` signature -- cyanrip writes it from `atexit`, so an
unattested log means the process never ran its normal shutdown."*

**The log filed here as `rips/cancel-me.log` is complete, signed, and says
`Rip completed:  yes (3 of 14 tracks)`.** Both statements are true, because they
describe the same file at two different times. The timeline, entirely from
`session/platterpus-app-log.txt` and the rip's own log:

| time | event | source |
|---|---|---|
| 00:03:21.802 | cyanrip starts, `-l 1,2,3` | app log |
| 00:04:52.150 | user cancel; **SIGTERM sent**, "arming the 5s force-stop rescue" | app log |
| 00:04:52.648 | `--verify-log` -> exit 3, no FUN512: the log is mid-write | app log |
| 00:04:52.650 | Platterpus reports `success=False`; the UI says cancelled | app log |
| 00:05:39.780 | **a SECOND cyanrip starts on the same `/dev/sr0`** | app log |
| 00:16:15 | that second rip finishes, 2 of 14, signed | `rips/after-cancel.log` |
| **00:20:25** | **the FIRST rip finishes -- 15 min 33 s after the SIGTERM** | `rips/cancel-me.log` |

No SIGKILL for the rip appears anywhere in the app log; the "5s force-stop
rescue" logged at 00:04:52.150 has no matching kill line.

**Why cyanrip ignored it: it never received it.** Platterpus launched
`/home/rmccann/.local/bin/cyanrip`; the rip's own `Invoked as:` line reports
`/usr/local/bin/cyanrip`. Two different paths for one process means an exec
happened in between, and the transcript names the mechanism --
`distrobox-enter -n ripping -- /usr/local/bin/cyanrip`. **The SIGTERM went to
the wrapper outside the container. `quit_now` was never set, because the
handler never ran.**

So `Rip completed:  yes` is exactly true: that process completed, and nothing
ever asked it to stop. **cyanrip behaved correctly at every step**, and the
finding is a signal-propagation defect in the launch path, which is theirs.

Two consequences worth stating plainly, because neither is cosmetic:

* A user who cancels gets a **complete, signed archival record of a rip they
  cancelled**, and nothing in that record says so. Nothing we can add fixes
  this from our side -- we were never told.
* **Two cyanrip processes read one drive concurrently for ten and a half
  minutes.** `rips/cancel-me.log` carries this session's only non-zero stall,
  `1 read exceeded 10s; longest 10s (track 3, LSN 40008)`, which is *consistent
  with* contention and is not proof of it.

This does **not** re-open SETTLED.md's "a single SIGTERM cannot terminate
cyanrip". That claim is about a window *after* the rip loop. This SIGTERM landed
90 s into a rip, where `quit_now` is read throughout the rip loop -- and it
changes nothing
here because the signal never arrived. The two facts are independent.

## Finding 2 -- a repeated `-j`, ours, and now fixed

**Seven of the eight failures are one line**, repeated: `argv/record  cyanrip
wrote no -j diagnostics record, so what it received cannot be read back`.

It had written one. `session/argv-probe-output.txt` shows the probe's argv
carrying **`-j` twice** -- their rig-check's own path, and their argv builder's
appended `-j cyanrip-diagnostics.json`. Reproduced from that exact argv, which
needs no drive: the record is written, complete, with `exit_code: 1` and the
libcdio message -- **at the last path**. Their check watched the first.

The finding was real, the diagnosis was wrong, and underneath was a real defect
of ours: `main()`'s pre-pass took the **first** `-j` and `break`ed while genopt
takes the **last**, so which file received the record depended on when the
process died. Fixed at `12f2081` with `sc_diag_repeated_flag`.

## Finding 3 -- `-Z` non-convergence is NOT deterministic

`rips/secure-reread.log`, `-Z 2 -r 3`: 12 of 14 tracks converged after 3 reads;
**tracks 3 and 5** report `Secure re-read:  did NOT converge after 3 reads
(repeat limit hit)`.

**This is not the first hardware evidence of that arm and the first draft of
this file said it was.** `docs/SETTLED.md` already carries it from
`docs/rig-2026-09-03-978f9b0`, four days earlier. Re-deriving a settled fact and
getting it wrong is exactly what that index exists to stop, and it was caught by
reading the index rather than by anything in the artifacts.

What IS new is the comparison, and it is more useful than the claim it replaces.
**Same disc, same build `978f9b0`, same `-Z 2 -r 3`, four days apart:**

| session | tracks that hit the repeat limit |
|---|---|
| `rig-2026-09-03-978f9b0` | 3, **4**, 5 |
| `rig-2026-09-07-978f9b0` | 3, 5 |

Track 4 did not converge on one run and did on the other, with nothing changed.
**Non-convergence is a property of the read, not of the track** -- so a consumer
must not treat a track's convergence as a stable attribute of the disc, and two
rips of one disc legitimately disagree about which tracks converged.

`Ripping errors: 0` on all eight rips; `AccurateRip: found`,
`Tracks ripped accurately: 12/14` -- the same two tracks as the non-converged
ones this time. The `Scope:` caveat is present on all 14 track blocks, which is
what a multi-pass rip must carry.

## What this session does NOT establish

It is on **`978f9b0`, the released build** -- not round 16's pin `a9aedf0`, and
not the test pin `ddc1e8c`. **It therefore does not satisfy round 16's close
condition, which requires a hardware run on that pin**, and it cannot: the
AccurateRip response parser it would exercise was rewritten after this build.

Also untouched by this session, checked by grepping every `Invoked as:` line
rather than assumed: **no `-H`, no `-E`, no `-x`** appears in any of the eight
rips. Close-condition clause 2 -- `-H` together with de-emphasis -- has still
never run on a drive.

## Things to raise with Platterpus

1. The `argv/record` message states a mechanism in our binary that is false.
   "cyanrip wrote no record" should be "no record at the path we gave".
2. Their `[plan]` block prints *"Diagnostics (-j) and cache probe (-x): NEVER
   sent by a rip. Neither is part of the rip argv"* **270 ms before** logging an
   argv ending `-G -j cyanrip-diagnostics.json`. Both lines are in
   `session/platterpus-app-log.txt`.
3. `parser/interrupted` prints *"expected for a rip that ran to the end"* when
   `rip_completed=None`, not only when it is `True`. For a cancelled rip the
   absence of `Interrupted at:` is the finding, not the expectation.
4. The eight `-j` records were never collected. A relative `-j` path is the
   reason; an absolute one would put them beside the log.

## Rename mapping

**Backfilled 2026-09-29**, derived by hashing each file filed here against
the members of `platterpusbundle20260907t030712z.tar.gz`; round 16 lap 14 §C's rule, which this filing
had not followed until then. The first column is how the file is filed
here, the second how it was delivered.

| filed here | as delivered in their bundle | sha256/16 |
|---|---|---|
| `after-cancel.cue` | `album/after cancel 20260907t030712 platterpus-fork-g978f9b0/after cancel 20260907t030712 platterpus-fork-g978f9b0.cue` | `9e9cbb06902853a1…` |
| `after-cancel.eac.log` | `album/after cancel 20260907t030712 platterpus-fork-g978f9b0/after cancel 20260907t030712 platterpus-fork-g978f9b0 (EAC-compatible).log` | `b6bfd36ff40ac84a…` |
| `after-cancel.log` | `album/after cancel 20260907t030712 platterpus-fork-g978f9b0/after cancel 20260907t030712 platterpus-fork-g978f9b0.log` | `c7c1e66d19c75b41…` |
| `cancel-me.cue` | `album/cancel me 20260907t030712 platterpus-fork-g978f9b0/cancel me 20260907t030712 platterpus-fork-g978f9b0.cue` | `59596a9b9a8d8b67…` |
| `cancel-me.eac.log` | `album/cancel me 20260907t030712 platterpus-fork-g978f9b0/cancel me 20260907t030712 platterpus-fork-g978f9b0 (EAC-compatible).log` | `34bb14d1dab3a160…` |
| `cancel-me.log` | `album/cancel me 20260907t030712 platterpus-fork-g978f9b0/cancel me 20260907t030712 platterpus-fork-g978f9b0.log` | `b3e31a518251d271…` |
| `derived-mp3.cue` | `album/derived mp3 20260907t030712 platterpus-fork-g978f9b0/derived mp3 20260907t030712 platterpus-fork-g978f9b0.cue` | `fa5b68a5de4e13b7…` |
| `derived-mp3.eac.log` | `album/derived mp3 20260907t030712 platterpus-fork-g978f9b0/derived mp3 20260907t030712 platterpus-fork-g978f9b0 (EAC-compatible).log` | `1ef4bbb3bbf870a6…` |
| `derived-mp3.log` | `album/derived mp3 20260907t030712 platterpus-fork-g978f9b0/derived mp3 20260907t030712 platterpus-fork-g978f9b0.log` | `664bad5727c01f95…` |
| `derived-wav.cue` | `album/derived wav 20260907t030712 platterpus-fork-g978f9b0/derived wav 20260907t030712 platterpus-fork-g978f9b0.cue` | `0857af578a7d2a9c…` |
| `derived-wav.eac.log` | `album/derived wav 20260907t030712 platterpus-fork-g978f9b0/derived wav 20260907t030712 platterpus-fork-g978f9b0 (EAC-compatible).log` | `592947fae30d562c…` |
| `derived-wav.log` | `album/derived wav 20260907t030712 platterpus-fork-g978f9b0/derived wav 20260907t030712 platterpus-fork-g978f9b0.log` | `9585d920a2fac334…` |
| `derived-wavpack.cue` | `album/derived wavpack 20260907t030712 platterpus-fork-g978f9b0/derived wavpack 20260907t030712 platterpus-fork-g978f9b0.cue` | `3ba9e8884bdcf0c1…` |
| `derived-wavpack.eac.log` | `album/derived wavpack 20260907t030712 platterpus-fork-g978f9b0/derived wavpack 20260907t030712 platterpus-fork-g978f9b0 (EAC-compatible).log` | `45f86f7d11736224…` |
| `derived-wavpack.log` | `album/derived wavpack 20260907t030712 platterpus-fork-g978f9b0/derived wavpack 20260907t030712 platterpus-fork-g978f9b0.log` | `38d9009b21583687…` |
| `full-acceptance-angle-bracket-2.cue` | `album/full acceptance_ angle_bracket 20260907t030712 platterpus-fork-g-2/full acceptance∶ angle‹bracket 20260907t030712 platterpus-fork-g978f9b0.cue` | `37dacf86f62a898a…` |
| `full-acceptance-angle-bracket-2.eac.log` | `album/full acceptance_ angle_bracket 20260907t030712 platterpus-fork-g-2/full acceptance∶ angle‹bracket 20260907t030712 platterpus-fork-g978f9b0 (EAC-compatible).log` | `36e31897bbcdeaaa…` |
| `full-acceptance-angle-bracket-2.log` | `album/full acceptance_ angle_bracket 20260907t030712 platterpus-fork-g-2/full acceptance∶ angle‹bracket 20260907t030712 platterpus-fork-g978f9b0.log` | `c5e6b4fc0d0d10b1…` |
| `full-acceptance-angle-bracket.cue` | `album/full acceptance_ angle_bracket 20260907t030712 platterpus-fork-g/full acceptance∶ angle‹bracket 20260907t030712 platterpus-fork-g978f9b0.cue` | `e40114a30858e6d4…` |
| `full-acceptance-angle-bracket.eac.log` | `album/full acceptance_ angle_bracket 20260907t030712 platterpus-fork-g/full acceptance∶ angle‹bracket 20260907t030712 platterpus-fork-g978f9b0 (EAC-compatible).log` | `6104da776c39c4d8…` |
| `full-acceptance-angle-bracket.log` | `album/full acceptance_ angle_bracket 20260907t030712 platterpus-fork-g/full acceptance∶ angle‹bracket 20260907t030712 platterpus-fork-g978f9b0.log` | `319805614a27d006…` |
| `secure-reread.cue` | `album/secure reread 20260907t030712 platterpus-fork-g978f9b0/secure reread 20260907t030712 platterpus-fork-g978f9b0.cue` | `7b81d88502483b25…` |
| `secure-reread.eac.log` | `album/secure reread 20260907t030712 platterpus-fork-g978f9b0/secure reread 20260907t030712 platterpus-fork-g978f9b0 (EAC-compatible).log` | `880cb1d14e4be3be…` |
| `secure-reread.log` | `album/secure reread 20260907t030712 platterpus-fork-g978f9b0/secure reread 20260907t030712 platterpus-fork-g978f9b0.log` | `10a401b061af0e42…` |
| `session/DIAGNOSTICS.txt` | `DIAGNOSTICS.txt` | `1af2ebaa84534373…` |
| `session/MANIFEST.txt` | `MANIFEST.txt` | `01ad05fe7709801d…` |
| `session/SOURCES.txt` | `SOURCES.txt` | `3625671fa3005d6a…` |
| `session/argv-probe-output.txt` | `extra0920260907T030712_0000/rig-check/argv-probe-output.txt` | `8adfa212a38c33f3…` |
| `session/config.toml` | `session/artifacts/08platterpus/config.toml` | `bc466ae99ed84df8…` |
| `session/platterpus-app-log.txt` | `session/artifacts/02platterpus/log.txt` | `b6a59505e4c354ff…` |
| `session/ripper-version.txt` | `extra0920260907T030712_0000/rig-check/ripper-version.txt` | `e386e7ac571f38e2…` |
| `session/transcript.txt` | `session/transcript.txt` | `78afdd896883bb50…` |

`session/transcript.txt` is also byte-identical to the bundle's `extra0920260907T030712_0000/transcript.txt`.
