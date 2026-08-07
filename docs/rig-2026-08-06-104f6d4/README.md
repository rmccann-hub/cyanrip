# Rig session — build `104f6d4`, 2026-08-06

**The J1 rip.** The disc the whole of round 7 has been blocked on.

Dated by its build, not its date, per the lesson two sessions on 2026-08-04
taught: `9003e6f` and `c5fb909` ran on the same day and a claim about one was
checked against the other's log.

| | |
|---|---|
| Build | `cyanrip 0.9.4-rc1+platterpus.5-beta.8 (platterpus-fork-g104f6d4)` |
| Consumer | `platterpus/0.6.4b14` (recorded verbatim, not verified by us) |
| Drive | PIONEER BD-RW BDR-209D, firmware 1.51, `/dev/sr0` |
| Disc | The Police — *Every Breath You Take: The Classics*, 14 tracks |
| Offset | `+667` |
| Finished | 2026-08-06T19:13:12 |

**These files are byte-exact and must stay that way.** `cyanrip.log` carries its
own `FUN512`; altering a byte destroys the only self-check it has. `CHECKSUMS.txt`
records them as received.

---

## Recorded BEFORE reading Platterpus's lap

This file was written and committed **before** their reading of the same
artifacts was received, deliberately, so "our analysis was independent" is
checkable against a commit rather than asserted. The user is relaying between
two sessions; only the commit order proves which came first.

## The four J1 acceptance criteria — all four PASS

Platterpus's, from lap 29 plus the fourth added in lap 31.

| # | criterion | result |
|---|---|---|
| 1 | 14 ISRCs in the cue | **PASS** — `grep -c '^    ISRC '` = 14 |
| 2 | `INDEX 00` on exactly 2/4/5/7/8/9/10/13/14 and nowhere else | **PASS** — measured set is exactly `2 4 5 7 8 9 10 13 14` |
| 3 | `Offset:` unchanged | **PASS** — `Offset:         +667 samples` |
| 4 | a **real colon** in the cue's `TITLE` and the log's `album:` | **PASS** — both read `Every Breath You Take: The Classics`; **zero** U+2236 in either file |

Criterion 4 is the one neither side could prove alone. The escape survives the
whole chain: Platterpus emits `album=…You Take\: The Classics`, our
`append_missing_keys()` leaves the escape intact, `av_dict_parse_string()`
consumes it, and a real `U+003A` lands in both artifacts. **The `\:` escape is
now proven end-to-end**, which retires the hedge both laps carried.

Note the U+2236 substitution still appears in *directory names*
(`Every Breath You Take∶ The Classics/`) — that is a filesystem-safety
substitution in the path, not the metadata, and it is correct there. The
metadata fields carry the real colon.

## The paranoia invariant, on media that made paranoia work

Per-track counters must sum to the disc totals. Until this session that had only
ever been checked against a fixture whose numbers agree by construction, so it
could not discriminate.

| counter | Σ tracks | disc total | |
|---|---|---|---|
| READ | 21972 | 21972 | OK |
| VERIFY | 1591 | 1591 | OK |
| FIXUP_ATOM | 8 | 8 | OK |
| OVERLAP | 458 | 458 | OK |

`FIXUP_ATOM: 8` is the part that matters — paranoia performed real repair work,
so the totals are not trivially equal.

## Other measurements

- **Sub-channel pregap search: 13 of 14 tracks** reported
  `Pregap source: sub-channel (not signalled by TOC)`; track 1 reported
  `lead-in`. Nine of those have non-zero length and are the nine `INDEX 00`s.
- **`Read stalls: none (no read exceeded 10s)`** — the expected result on healthy
  media. A silent watchdog is not a working watchdog; this is still not evidence
  either way.
- **`Ripping errors: 0`**, `Rip completed: yes (14 of 14 tracks)`.
- **`Tracks ripped accurately: 13/14` / `partially accurately: 1/14`** — both
  denominators are 14, which is the denominator fix behaving on real data.
- **`C2 errors: unsupported by drive`** — C2 remains unexercised anywhere.
- **`Cache model: 1200 sectors (drive cache size not probed)`** — correct, and
  `-x` was **not** passed on either pass. **`-x` has still never executed on a
  real drive, in any session, on any build.**
- **`--verify-log` on this log returns valid**, run by us against the archived
  copy.

## Track 5, and a wording question for Platterpus

Track 5 is the one that failed AccurateRip v1/v2 (`+450` matched at confidence
200, "partially accurately ripped"). Platterpus re-ripped it in a **second
cyanrip invocation** with `-Z 2 -l 5`, and the addendum records
`Secure re-read: converged after 5 reads`.

**But the re-read produced a byte-identical result.** The addendum's CRC for
track 5 is `6902BCF0`; the first pass's `EAC CRC32` for track 5 is `6902BCF0`.
The three AccurateRip values are identical too.

So the addendum's sentence — *"were re-ripped to secure them; the **improved**
read was swapped in"* — is not supported for this track. Nothing improved. The
read was **confirmed** by convergence, which is a different and still useful
claim. Raise in §H: check the verb. This is the same shape as `defeat` versus
`model` on our own side.

## Provenance: the rip is one commit past the declared test pin

`104f6d4`, not the `92ceeed` lap 33 declared. Benign, and stated rather than
smoothed over:

```
$ git diff --stat 92ceeed 104f6d4 -- src/
(empty)
```

The range touches **no `src/` at all** — only `tests/`, the golden reference and
lap 33 itself. The rip code is identical; the sole compiled difference is the
handshake state, which is why the log reads `round 7 lap 33` rather than
`lap 32`. Lap 35 must name `104f6d4` as the build that ripped, not `92ceeed`.

## Checked and NOT filed as findings

Both nearly went in. Recording them because a rejected finding is evidence too.

- **The GUI's "Cache defeat: Yes — cache defeated on re-read (measured,
  cd-paranoia)"** looked like it re-introduced downstream the exact over-claim
  we removed from our own log when `Cache defeat:` became `Cache model:`. It
  does not. Their EAC-compatible log spells it out: *"measured for this drive
  with cd-paranoia -A, **not asserted from the ripper's log**"*. They measured
  it themselves, with a different tool, and disclaimed our log as the source.
  Correctly scoped, and `-x` never having run is irrelevant to it.
- **"Re-ripping track 5" on screen while the live log said "track 12".** Not a
  defect in either program — see below.

## The track 5 / track 12 display question

Reported by the user from the GUI: the status line read *"Re-ripping track 5 to
secure it… about 10s left in re-read 2"* while the Live log pane streamed
*"ripping and encoding track 12, progress - 7.22%"*.

Our progress line, `src/cyanrip_main.c:807`:

```c
"Ripping%strack %i, progress - %0.2f%%",
(!ctx->settings.ripping_retries || repeat_mode_encode) ? " and encoding " : " ",
t->number, ...
```

Two facts settle it, both from source rather than inference:

1. **`%i` is `t->number`** — the real CD track number. It is never an index and
   never an offset, so a printed "track 12" means track 12.
2. **`ripping_retries` is `-Z`**, not `-r` (`cyanrip_main.c:1499`,
   `settings.ripping_retries = repeat_rips`, declared at line 1363 as `"Z"`).

So the wording is itself diagnostic:

| pass | `-Z` | prints |
|---|---|---|
| whole-disc first pass | absent → `ripping_retries == 0` | `Ripping **and encoding** track N` |
| the track-5 re-rip | `-Z 2` | `Ripping track 5` (no "and encoding") except on the final encode pass |

The observed line has **both** "and encoding" *and* "track 12". The re-rip argv
recorded in `platterpus.json` is `-Z 2 -l 5`, which rips track 5 only. So that
line cannot have come from the re-rip pass by either the number or the wording —
it is whole-disc-first-pass output.

**Conclusion: not a cyanrip defect.** Two panes were showing different passes at
one moment. Which pane is stale, and why, is Platterpus's to answer — it is
their presentation layer, and by the ownership rule that is theirs. We can only
say what our line means and which pass emits which spelling.

## What this session still does NOT establish

- **`-x`** — never run on a real drive, here or anywhere.
- **C2** — this drive reports it unsupported.
- **`-f`** offset autodetection.
- **Damaged media**, and therefore a non-zero `Read stalls:` count.
- **CD-TEXT from a physical disc** — this disc reported none.
- **The diagnosed-abort exit code** — `Ripping errors: 0`.
- **`-j`** was not passed, so there is no diagnostics record from this rip. The
  JSON here is Platterpus's own, not ours.

---

## Correction, appended after reading Platterpus's lap 35

**Appended, not edited.** The text above is left exactly as committed at
`3eb7c08`, before their lap existed, because its whole value is being provably
prior. This section is the correction.

### The paranoia invariant section above is wrong

It says `FIXUP_ATOM: 8` means "paranoia performed real repair work, so the
totals are not trivially equal". The second half does not follow from the first,
and the conclusion is false.

Their lap 35 §C challenged the claim, arguing the sum is forced on a rip without
`-Z`. **They are right that the check is vacuous and wrong about why**, and the
difference matters because it changes what would fix it. From our own source:

```
cyanrip_main.c:676   static int cyanrip_rip_track(...)
cyanrip_main.c:717     memcpy(start_paranoia, paranoia_status, ...)   <- snapshot
cyanrip_main.c:~940    goto repeat_ripping;                           <- the -Z loop
cyanrip_main.c:973     t->paranoia_status[i] = paranoia_status[i] - start_paranoia[i]
```

`paranoia_status[]` is a process-global the libcdio callback increments. The
per-track figure is a **delta of that same global**, snapshotted once before the
`-Z` repeat loop and differenced once after it. The disc total *is* that global.

So Σ(per-track deltas) telescopes to the global total whenever every read falls
inside some track's window — which is the normal case **with or without `-Z`**.
`-Z` repeats are already inside the window, so they change nothing.

Three consequences:

1. **Our claim was an over-claim.** Repair work inside one pass does not make
   the sum non-trivial. `FIXUP_ATOM: 8` shows paranoia worked; it says nothing
   about whether the arithmetic could have come out any other way.
2. **Their diagnosis is wrong**, and it is the actionable half. The sum is not
   forced "because there was no `-Z`" — it is forced by the delta construction.
3. **Their proposed remedy would not discriminate either.** Their lap says the
   honest test is "a `-Z`-on-every-track rip" and their rig sheet now asks for
   one. That rip would produce another forced equality and read as a third
   confirmation. **It is a rig session that cannot fail**, and they should not
   spend it on our account.

What the check *does* test, narrowly: that no paranoia read occurs outside any
track's snapshot window. That is a real property and worth keeping. It is not
"the per-track accounting survives re-reads", which is what both sides thought
they were confirming.

Filed to Platterpus in lap 36 §C.

---

## Second correction — the first correction was also wrong

Appended again, for the same reason: the record of what we believed, and when,
is worth more than a tidy file.

**The correction above is wrong, and Platterpus refuted it with measurement in
lap 37.** The claim was that Σ(per-track) equals the disc total "by construction,
with or without `-Z`", so the check could never discriminate and a
`-Z`-on-every-track rig session could not fail.

It discriminates. It has already failed, in this very session's artifacts:

| pass | argv | tracks | per-track READ | disc READ | |
|---|---|---|---|---|---|
| album | no `-Z` | 14 | 21972 | 21972 | equal |
| refix | `-Z 2 -l 5` | **1** | **1538** | **7738** | **not equal** |

One track in the refix pass, so there is no summation to argue about. Track 5
converged after 5 reads and 7738 / 1538 = 5.03.

**Why we got it wrong, exactly.** The delta construction was read correctly; the
loop boundary was not:

```
cyanrip_main.c:702   repeat_ripping:;                                <- the label
cyanrip_main.c:717     memcpy(start_paranoia, paranoia_status, ...)  <- INSIDE the loop
cyanrip_main.c:~940    goto repeat_ripping;
cyanrip_main.c:973     t->paranoia_status[i] = paranoia_status[i] - start_paranoia[i]
```

The snapshot is **re-taken on every repeat**, so the per-track figure describes
the **final read only**, while the process-global accumulates every read. They
diverge by the repeat count exactly as measured.

We searched the range 717..973, found `goto repeat_ripping` inside it, and
concluded the loop sat between snapshot and delta. **We located the goto and
inferred the label.** The label is at 702, fifteen lines above the snapshot.

That is this repo's own rule, failed on our own source: *bound every scan, or a
line inherits its neighbour's meaning*. A `goto` proves nothing about where its
label is, and "the loop sits between the two" was asserted, never checked — in a
paragraph that was itself correcting an over-claim.

**What is actually true:**

- Without `-Z`, each track is read once, so the delta covers the whole track and
  the sum matches. That is why the album pass agrees.
- With `-Z`, the per-track counters under-report by the repeat count, and the
  disc total cannot be reconstructed from them.
- So the invariant is real, checkable, and **false under `-Z`** — which makes
  every previous "confirmation" of it a measurement taken only in the case where
  it holds.

Not a regression in `104f6d4`: the behaviour predates it and breaks nothing in
the artifact under review. Round 8 by S-14, and the pin does not move for it by
S-15 — the first outing of both rules, and they hold.

Filed to Platterpus in lap 38 §B, with the retraction stated plainly.
