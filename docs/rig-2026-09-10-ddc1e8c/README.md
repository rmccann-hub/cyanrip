# Rig session 2026-09-10, TEST PIN `ddc1e8c`

**The first hardware evidence on round 16's pair**, and the first session in
which a cancel actually reached cyanrip.

Platterpus `0.6.45` driving
`cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-gddc1e8c)`, PIONEER BD-RW
BDR-209D firmware 1.51, The Police *Every Breath You Take: The Classics*.
Eight rips. Their run: **237 of 238 steps passed, 1 failure.**

This is **Run B** — their application acceptance battery. Per their lap 3 §0 it
does **not** establish the round's close conditions; Run A does, and Run A has
not been run.

## The headline: a cancel worked, and the log says so correctly

Every previous session's `cancel me` was a rip that finished normally. 2026-09-03
completed 3 of 3 requested tracks. 2026-09-07 ran **15 minutes 33 seconds past
the cancel** because the SIGTERM went to a distrobox wrapper and never reached
the process. `docs/SETTLED.md` records both.

This one, from `rips/cancel-me.log`:

```
Ripping errors: 1
Rip completed:  no (interrupted by SIGTERM, 0 of 14 tracks)
Interrupted at: track 1, mid-read
```

with `Log FUN512:` present and **`cyanrip -Y` exiting 0** — a complete, attested
record of an incomplete rip, which is exactly what an archival record should be
after a cancel. Zero track blocks, correct for a rip stopped inside track 1.

**Three things that were separately uncertain are settled by that one file:**

1. **The INTERRUPT footer, on hardware.** `SETTLED.md` already carried the
   *abort* footer from 2026-09-03 (`Rip completed:  no (aborted, 0 of 14
   tracks)`). The interrupt arm — a signal arriving mid-read — had never run.
   These are different code paths and only one of them was settled.
2. **The `Interrupted at:` line has never appeared in any rig log before.**
3. **A single SIGTERM terminated the rip**, which does not contradict
   `SETTLED.md`'s *"a single SIGTERM cannot terminate cyanrip"* — that entry is
   precise about *"once the rip loop is past"*. This signal arrived **mid-read**,
   where `quit_now` is read, and the flag did its job. The entry and this
   measurement are about opposite sides of the same window.

## The one failure is theirs, and it is a false negative

`L561 expect-log-well-formed` reports:

> *the log carries NO completion footer … the log carries NO `Log FUN512:`
> signature … [footer says not determined; 0 track block(s); signature ABSENT]*

**The footer is present. The signature is present. `-Y` exits 0.** Only
"0 track blocks" is right, and it is correct rather than a defect.

**What we cannot say is why**, and the honest limit is worth stating: the app log
collected in this bundle ends at 01:48:46 UTC while the cancelled rip finished at
02:02:15 UTC, so the cancel sequence is not in it. Their 2026-09-07 run showed
this check reading a log 498 ms after signalling — a true reading of a file still
being written. The same shape would explain this, and **we have not shown it**.
What the artifacts establish is that the conclusion is false, not the mechanism.

## What this session does NOT establish

**No `-H`, no `-E`, no `-W`, no `-x`** appears in any of the eight rips —
checked by grepping every `Invoked as:` line, not assumed. The only relevant flag
present is `-Z 2`.

**So close-condition clause 2 — `-H` together with de-emphasis — has still never
run on a drive, and this bundle cannot close round 16.** Run A is what settles
clauses 1–3, and it is still outstanding.

## What is filed, and what is not

`rips/` carries all eight logs, their EAC companions and cues (236 KB).
`session/` carries the transcript, the manifest, the sources list, and their
application log.

### The rips were RENAMED when filed, and here is the mapping

**The bytes are untouched; the names are not, and until round 16 lap 14 this
file did not say so.** Their bundle names each rip from the album title, with
spaces, a timestamp, a build tag and a parenthesised `(EAC-compatible)` suffix.
Those were shortened to fit a repository. **Renaming is a change to an artifact
even when every byte survives**, and a filed copy that cannot be mapped back to
what was delivered is not fully evidence.

**It had a consequence, measured rather than imagined.** Their
`scripts/verify_log_surface.py` excluded *their own* EAC exports by NAME. Over
their bundle that worked; over this filed copy it did not, because `*.eac.log`
is a third spelling of the same artifact — so 43 lines of their own export were
reported as evidence that *our* log format had moved. Their lap 14 §C fixes
their half by asking the document what it is instead of trusting its name. This
table is our half: **the rename is now recorded, so the mapping is recoverable
from the repository rather than from the tarball.**

Each row was produced by hashing the filed file and looking that hash up among
the bundle's originals — so the pairing is derived from the bytes, not from
anyone's memory of which file was which.

| filed here | as delivered in their bundle | sha256/16 |
|---|---|---|
| `after-cancel.eac.log` | `after cancel 20260910t005434 platterpus-fork-gddc1e8c (EAC-compatible).log` | `598866e874b870d0…` |
| `after-cancel.log` | `after cancel 20260910t005434 platterpus-fork-gddc1e8c.log` | `9a902659fac06cb8…` |
| `cancel-me.eac.log` | `cancel me 20260910t005434 platterpus-fork-gddc1e8c (EAC-compatible).log` | `4c89980eb76498a7…` |
| `cancel-me.log` | `cancel me 20260910t005434 platterpus-fork-gddc1e8c.log` | `2935f0ef8f621876…` |
| `derived-mp3.eac.log` | `derived mp3 20260910t005434 platterpus-fork-gddc1e8c (EAC-compatible).log` | `c8b40f1c711543e0…` |
| `derived-mp3.log` | `derived mp3 20260910t005434 platterpus-fork-gddc1e8c.log` | `3bf251e1cb532634…` |
| `derived-wav.eac.log` | `derived wav 20260910t005434 platterpus-fork-gddc1e8c (EAC-compatible).log` | `cfb0038efe7a295d…` |
| `derived-wav.log` | `derived wav 20260910t005434 platterpus-fork-gddc1e8c.log` | `2db69e1cab3f6cb2…` |
| `derived-wavpack.eac.log` | `derived wavpack 20260910t005434 platterpus-fork-gddc1e8c (EAC-compatible).log` | `29112b14f18104dd…` |
| `derived-wavpack.log` | `derived wavpack 20260910t005434 platterpus-fork-gddc1e8c.log` | `79623576292602ca…` |
| `full-acceptance-angle-bracket-2.eac.log` | `full acceptance∶ angle‹bracket 20260910t005434 platterpus-fork-gddc1e8c (EAC-compatible).log` | `b5d1052290b61c2a…` |
| `full-acceptance-angle-bracket-2.log` | `full acceptance∶ angle‹bracket 20260910t005434 platterpus-fork-gddc1e8c.log` | `b67ddb2463980574…` |
| `full-acceptance-angle-bracket.eac.log` | `full acceptance∶ angle‹bracket 20260910t005434 platterpus-fork-gddc1e8c (EAC-compatible).log` | `16df2c015557264e…` |
| `full-acceptance-angle-bracket.log` | `full acceptance∶ angle‹bracket 20260910t005434 platterpus-fork-gddc1e8c.log` | `f4987f331f1bb3db…` |
| `secure-reread.eac.log` | `secure reread 20260910t005434 platterpus-fork-gddc1e8c (EAC-compatible).log` | `642366537ae4dbc7…` |
| `secure-reread.log` | `secure reread 20260910t005434 platterpus-fork-gddc1e8c.log` | `18d1dd0a602a36e6…` |

**Two rows share a delivered name and that is not an error.** Their bundle
carries two `full acceptance∶ angle‹bracket …` rips in two different
directories, distinguished only by the directory. Flattening into one folder
would have collided them, so the second took a `-2` suffix — the four files
involved have four distinct hashes, checked. **Our suffix preserves a
distinction their basename alone loses.**

**That app log is 7.2 MB of 66,452 lines**, most of it DEBUG-level echo of
cyanrip's own progress output. It is filed **whole and unedited**: it is
evidence, and trimming evidence to save space is falsifying it. The 2026-09-07
session is the precedent for why it is worth keeping — that log is what
identified the distrobox signal path.

Not filed: 15 UI screenshots and the per-rip `.platterpus.json` files, which are
downstream derived data.
