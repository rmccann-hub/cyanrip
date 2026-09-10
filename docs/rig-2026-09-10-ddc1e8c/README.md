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

**That app log is 7.2 MB of 66,452 lines**, most of it DEBUG-level echo of
cyanrip's own progress output. It is filed **whole and unedited**: it is
evidence, and trimming evidence to save space is falsifying it. The 2026-09-07
session is the precedent for why it is worth keeping — that log is what
identified the distrobox signal path.

Not filed: 15 UI screenshots and the per-rip `.platterpus.json` files, which are
downstream derived data.
