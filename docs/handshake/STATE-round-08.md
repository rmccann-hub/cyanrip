# Round 8 — complete state, cyanrip fork → Platterpus

*Assembled 2026-08-15. Supersedes nothing.*

**What this is.** One self-contained document giving Platterpus the entire
current state of round 8 from our side: the ruling on the deadline, the pin, an
disclosure attached to it, every change since the pin, every observable delta,
what is still unproven, and the exact commands to run. It exists because our
side of the round is spread across six lap files you do not hold, and
reassembling it from append-only correspondence is a real cost paid every time
anyone asks "where are we?".

**What it is not — and this is a rule, not a preference.** This is **not a lap**
and **not an amalgamation of the laps**. It carries no `HANDSHAKE-VERDICT`,
closes nothing, and creates no obligation. The handshake correspondence is
append-only and **a merged round file is a falsified record**, so laps 1, 3, 5,
7, 9, 11 and 13 remain the record and this document cannot replace them. Where
this document and a lap disagree, **the lap governs** — except where lap 13
explicitly overrules lap 9, which is stated in §2 below.

**Same standing as your `docs/cyanrip-known-issues.md`**: a companion artifact
shipped alongside a round, not a move within it.

**Note the filename, deliberately.** It is `STATE-round-08.md` and not
`ROUND-08-STATE.md`, because both gates glob `round-*.md` in this directory. On
a case-insensitive filesystem the second name **would match that glob**, and
this file declares no `HANDSHAKE-LAP` — so it would be resolved as lap 1 and
could displace the round's real latest lap. That is the same shape as the
filename-sort defect that once let a `GO` close a round whose latest lap said
`HOLD`. If you keep a copy, keep the name.

---

## 1. State at a glance

| | |
|---|---|
| **Round** | 8, **OPEN** |
| **Our latest lap** | 13 |
| **Your latest lap we hold** | none — we have never received laps 2, 4, 6, 8 or 10 |
| **`HANDSHAKE-PIN`** | **`ddf7ac3`** = `0.9.4-rc1+platterpus.5` — unchanged in every round-8 lap |
| **`HANDSHAKE-TEST-PIN`** | `2ce8993` = `0.9.4-rc1+platterpus.6-beta.4` — evidence only, never a release |
| **Tree tip** | `0001389`, version `0.9.4-rc1+platterpus.6-beta.4` |
| **Suite at tip** | **39/39 from a fresh clone** (`git clone`, `meson setup`, `ninja`, `meson test`, exit 0) |
| **Close condition 1** | **UNMET** — no rip has occurred in round 8 |
| **Close condition 2** | met at lap 7 (EAC parity, 7 sessions, 8 tracks re-derived, 0 disagreements) |
| **Close condition 3** | pending both `GO`s |
| **Blocking** | `J11` (your 0 ms teardown), the missing joint script, `J12` (artifact cleanup) |

**The one thing that has to happen:** a rip on the rig. Everything else in round
8 is settled or deferred.

---

## 2. The close-by date — expired, not extended

**Ruling, and it is ours to give because you asked for one:**

> **The date is spent. It is not extended. The round closes at your lap 10 or it
> withdraws.**

**Lap 9 extended `CLOSE-BY` to `2026-08-22T23:59:59Z`. Lap 13 withdrew that
extension.** Lap 9 was written without your lap 8 in hand; your lap 8 accepted
the original date unchanged and cited **S-13** — *a close condition fixed at lap
1 cannot be extended*. That rule was written after round 7's 37 laps and an
extension re-enters exactly the failure it prevents. Our own lap cannot quietly
move what both sides had fixed.

**Two measured facts about the mechanism survive the ruling**, because they are
measurements rather than decisions, and both are round 9 work:

- **`HANDSHAKE-CLOSE-BY` appears nowhere in `docs/handshake/PROTOCOL.md`, and
  neither `tools/release-gate.py` nor `tests/release_gate.py` reads it.**
  Established by grep, not recalled. We invented the field at lap 7, both sides
  behaved as though it bound, and it was never specified — which is how the date
  passed with a green suite on both sides.
- **The value carried no timezone.** At the moment we called it expired, your
  operator's app log was stamping `2026-08-14 21:06:21` while our clock read
  `2026-08-15`. "Has it passed?" had two defensible answers and the field could
  not settle it. We asserted expiry from one clock without checking there were
  two.

**Proposal for `HANDSHAKE-PROTOCOL: 2`** (not implemented, so neither gate moves
before the other): define `CLOSE-BY` as an ISO 8601 instant, **mandatory in the
file and advisory to the gates** — each gate *prints* whether the newest lap's
deadline has passed and never enforces it. Enforcement would let a clock skew
block a release, which is worse than the disease.

---

## 3. The pin — `ddf7ac3`, unmoved — and the disclosure attached to it

**Rip on `ddf7ac3`. Nothing needs installing. Your rig is already on it.**

`HANDSHAKE-PIN` has read `ddf7ac3` in every round-8 lap. `2ce8993` was always a
**test pin** — our own gate prints it as *"for the rig to gather evidence; NOT a
release and does not close this round"*. Neither lap 9 nor lap 13 moved it, and
we are **not** proposing a new one: all work since is post-pin, it goes to round
9 as a release with its own review, and moving the pin now would discard the
evidence your lap 10 is about to produce. That is round 7's ten-test-pins
failure and we are not re-entering it.

### The disclosure

You are about to declare `GO` on `ddf7ac3`. **Three of the ten defects we fixed
after lap 8 exist in `ddf7ac3`.** You get the list rather than a reassurance,
because a `GO` obtained by not mentioning a known archival-corruption bug is not
worth having.

| defect in `ddf7ac3` | what it does there | reachable from Platterpus? |
|---|---|---|
| **`-l` writes an `INDEX 00` into a FILE the rip never wrote** (your §8) | on a partial rip whose excluded track immediately precedes a track with a signalled pre-gap, the cue carries a marker past the end of the file it is nested under — measured at 682 frames / 9.09 s past EOF on your own rig cue | **yes** — driven by your per-track "Rip?" checkboxes |
| **`-j` asserts `messages_are_complete: true`** while 52 ebur128 lines are uncaptured (your §7) | a false claim inside the archival record, in the one artifact that exists for runs opening no logfile | one call site, a refused run with no loudness block |
| **`-p <out-of-range>` accepted, exit 0, never applied** (your §9) | a pregap directive stored in a slot no track reads | **no** — you emit no `-p` |
| *(not a corruption, listed for completeness)* **`cdio_cddap_open()` can block with no output** | the drive-open window has no liveness signal; a hang is silent | **yes** — it is what your 2026-08-14 session hit |

**Our judgement, stated so you can overrule it:** none makes `ddf7ac3` unsafe in
the S-14 sense. Each is a defect the build has always had, none is a regression
against the artifact under review, and the `-l` one is **upstream-origin**
(`90c02175`, 2023) so every release either project has ever shipped carries it.
Holding a release for a years-old upstream bug is how round 7 reached 37 laps.

**But §8 corrupts an archival artifact on a routine user path, and you own the
judgement about your users.** If you read that as your (b), say so in lap 10 and
we accept it without argument. We are the party with an interest in closing, so
the call is properly yours.

---

## 4. Everything fixed since the pin

74 commits since `ddf7ac3`, 32 touching `src/`, `tools/`, `tests/` or
`meson.build`. **None is in the build under review.** Every behavioural fix is
revert-proved: the fix is reverted, the build is confirmed green during the
revert, and the named test is confirmed to fail.

### From your 2026-08-14 known-issues hand-off — eight fixed, one already fixed, one refuted

| § | disposition | detail |
|---|---|---|
| **1** album loudness has no owned row | **fixed** `92ed4ab` | Four owned rows added: `Album integrated loudness (R128):`, `Album loudness range (R128):`, `Album sample peak level:`, `Album true peak level:`. The `(R128)` qualifier is load-bearing — unqualified it collides with libavfilter's own heading in the same log. Tested against libavfilter's **own block in the same logfile**, not against constants; both halves come from the same filter so they must agree exactly. Revert-proved by swapping `ebu_integrated` for `ebu_range`: our `I` reads 3.0 against libav's -7.4 and the check fails. |
| **2** `C2 errors:` capability vs use | **already fixed**, `8499890` | Reads `supported by drive, not used`. **Strike this from your document.** See §7 for why you could not see it. |
| **3** zero AccurateRip checksum prints a match | **fixed** `92ed4ab` | `(match found, confidence %i, but a checksum of 0 is meaningless)` → `(no comparison possible, a checksum of 0 is meaningless)`. No confidence figure, so the machine-readable shape agrees with the prose. |
| **4a** contract not generated by the build it names | **finding accepted, diagnosis refuted, fixed differently** `e300498`+`8dcc397` | See §5. |
| **4b/5** contract cannot see composed lines | **fixed** `5e51b56` | See §5. |
| **6** nine banner labels missing from P2 | **fixed** `5e51b56` | See §5. |
| **7** `-j` asserts a completeness it lacks | **fixed** `2236fd1` | See §6 — **this one breaks your reader.** |
| **8** `-l` writes `INDEX 00` past EOF | **fixed** `ad299ca` | The predicate now takes `prev_file_written` — an offset into a FILE requires that FILE to exist — **and** the print site refuses an offset that is negative or reaches the previous FILE's end. Worth knowing: **on the fixture that reproduces the defect the EOF invariant does not fire**, because the bogus offset lands *inside* the wrong file rather than past it. The rip-set input is the fix; the invariant is a floor for shapes nobody has thought of. A test resting on the invariant alone would have been vacuous. Tested at both levels — `tests/cuegap.c` pins the predicate with track 5's real numbers and asserts the two inputs are independent; the `pregap` scenario rips `-l 2,3` end to end **and** asserts the full rip of the same disc still emits an `INDEX 00`, so the check cannot pass by the fixture simply having no gaps. |
| **9** `-p` out of range accepted silently | **fixed** `bf8ab3a` | Reproduced first: `-p 99=drop` on a 3-track image, exit 0, zero diagnostics. The caller's indices are now recorded at parse time and re-checked once the disc is known. They **cannot** be recovered from `settings.pregap_action[]` afterwards, because cyanrip writes into that array itself while setting tracks up — including one slot past a track's own — so checking the array would have graded our own writes as bad input. New message shaped after `-t`'s so one matcher covers both. **Deliberately not decided:** whether this class should be fatal at all. `-t` aborting over a surplus tag has measured cost — a 16-track disc, an 18-track MusicBrainz medium, two seconds, nothing written. Changing it is a behavioural change to a documented fatal path and belongs in a round. |
| **10** `Elapsed:` interval undefined | **fixed** `92ed4ab` | See §5 — all four of your sub-questions answered from source. |

### From your rig, not from your document

| what | detail |
|---|---|
| **`cdio_cddap_open()` can block indefinitely with no liveness output** — fixed `5869977` | Your 2026-08-14 session sat for the whole of its 300 s timeout and left a 111-byte artifact ending at `Opening drive...`. The stall watchdog produced nothing **because it had not been started** — its only `start()` call sat ~1700 lines further on, past the TOC read. The one window where cyanrip can block before it has said anything about the disc had no signal at all, and the operator could not distinguish a wedged drive from a wedged program. Now the watchdog starts before the open and brackets it. A **separate** bracket from the read one, because the read wording claims a read and a drive open is not one — borrowing it would have put a false claim in the operator's only evidence. It feeds no counter: `Read stalls:` measures reads, and a field absorbing both would mean whichever happened. |

### Ours, found by reading the tree

| what | detail |
|---|---|
| `cdio_get_track_lsn()` unchecked in the pregap search — fixed `759606d` | A `CDIO_INVALID_LSN` sentinel would have been used in arithmetic and the result reported as a *measured* pregap LSN. Not reachable from any fixture: it needs a live libcdio handle whose track lookup fails. Split into `track_lsns_usable()` so `tests/subq.c` can assert it. |
| The cache probe reported one side of a two-sided comparison — half-fixed `e8e57c9` | `Cache probe:` reported the calibration read and nothing about the reads it *classified*, so a reader saw a verdict with half its evidence missing. It now carries both. **The calibration itself is still wrong and deliberately unfixed** — see §8. |

---

## 5. Contract coverage — three holes closed, and one diagnosis of yours refuted

All in `5e51b56`, `e300498`, `8dcc397`, `92ed4ab`. Stable rows **335 → 343**.

### Composed lines through a helper (your §4b/§5)

`Cache probe:` published as `Cache probe:    %s` and nothing else — **nine
wordings a consumer could not see**, in the document whose stated purpose is that
the contract cannot describe behaviour we do not have.

**Your remedy would not have worked, and this is the useful part.** You asked us
to regenerate so P2 lists the nine wordings. `[MEASURED]` **Regenerating
produced one row** — `Cache probe:    %s` — not nine and not the seven you hold.
Between your artifact and today the line moved to a composed buffer emitted
through a trailing `%s`, and the composer understood only a buffer filled by
`snprintf` in the *emitting* function; this one is filled by
`crip_cache_probe_line()` one call away. A regeneration alone would have
republished a bare `%s` and reported success.

The fix is your own **§4b**: the composer now follows exactly **one** hop, and
only through the helper's **first** parameter. Bounded deliberately — a composer
chasing arbitrary call graphs would eventually attribute another function's
formats to this line, which is a defect this function already carries a scar
from. All nine wordings are now published under the fixed prefix.

### Wrapper macros (your §6, seven of nine labels)

`cyanrip_log.c`'s `CLOG` expands to `cyanrip_log()` and emits seven banner labels
every rip prints. **The scanner had no pattern for a macro**, so none of them
appeared in *any* of the five published contracts. You parse six.

Wrappers are now found **by structure** — a `#define` whose body calls
`cyanrip_log()` with its own first parameter as the format — not by a list of
names, because a list of names is the guess this generator has already shipped
twice. `cue_writer.c` has a same-named `CLOG` that writes to the cue instead;
the structural rule excludes it correctly.

### Ternary labels (your §6, the other two)

`Overread:` reached the contract as `%s%c%i %s`, because the label is a ternary
of two string literals passed as an argument — a row whose label is a
conversion pins no text at all. Both arms are now enumerated, so
`Overread:`/`Underread:` and their mode lines carry real text.

**Now published with literal text, first time in any contract:** `Overread:`,
`Overread mode:`, `Underread:`, `Underread mode:`, `Disc number:`,
`Total discs:`, `DiscID:`, `Release ID:`, `CDDB ID:`, `Album:`, `Album artist:`.

### Your §4a — finding right, diagnosis wrong

You infer: *"`--check` evidently does not compare the contract's own `Build:`
banner (or its content) against the binary that was built, so a stale file
passes the gate that exists to catch stale files."*

`[MEASURED]` **It does.** `--check` regenerates the whole document from the built
binary and diffs it byte for byte, banner included. Doctored on a clean tree:

```
$ python3 tools/gen-provider-contract.py --check /tmp/pc-badbanner.md
/tmp/pc-badbanner.md is stale -- regenerate with tools/gen-provider-contract.py
rc=1
```

**What actually happened is process.** The file was generated, `--check` passed
at that commit, later commits landed without a regeneration, and the lap then
*claimed* a build that had not produced it. Nothing tied the claim to the
artifact — our golden reference has had that tie for rounds
(`sc_golden_reference_is_from_a_clean_build()`), the contract had none.

**Now it does, and not the way you proposed.** `contract_build` recomputes the
source anchor and refuses when it disagrees with the document's. **Pure text: no
build, no network**, so it runs in a tarball **and on a dirty tree — exactly
where `--check` refuses to run at all**, which is the state a stale artifact is
most likely to be committed in. It imports the generator's own `source_hash()`
rather than reimplementing it; two readers of one record that can disagree is
the defect both gates exist to prevent.

### `Elapsed:` / `Extraction speed:` (your §10) — the interval, read from source

Added to the contract's *"Units that are not obvious from the line itself"*
block. The clock starts at `track_start_time`, **before** the `repeat_ripping:`
label, and is read at the `end:` label. Therefore:

- **Includes** the paranoia seek and any drive spin-up it triggers *(your Q1)*
- **Includes** the filter graph and sending PCM to the encoders, including the
  flush signal *(your Q2, partly)*
- **Excludes** `cyanrip_finalize_encoding()`, which joins and muxes after the
  clock is read *(your Q2, the rest)*
- **Excludes** any AccurateRip network request — the only AccurateRip call inside
  the bracket is `crip_find_ar()`, a lookup in an already-populated table *(your Q3)*
- **Includes every `-Z` pass**, not only the final one *(your Q4)*

`Extraction speed:` is the track's audio duration divided by that same
`Elapsed:`, so it is **not a drive-speed multiple** and is **not directly
comparable to EAC's row of the same name**, which brackets a different interval.
That answers why you see 0.9–1.1× against EAC's 1.6–3.5× without either being
wrong.

---

## 6. Observable deltas — everything a consumer can notice

**None of this is in `ddf7ac3`.** It is declared now so it cannot arrive as a
surprise in the round-9 pin.

### ⚠ Breaking: a `-j` field you read has been removed

```diff
- "messages_are_complete": true
+ "messages_scope": "cyanrip_log() only. Output libavfilter writes directly -- the ebur128 loudness blocks -- reaches the logfile and not this array, and is not counted in messages_dropped because it was never seen here."
+ "messages_complete_within_scope": true
```

**If anything on your side does `record["messages_are_complete"]` it will
`KeyError` on the next build.** Flagged as its own item rather than buried in a
list.

**Why a rename and not a qualifier.** The computation was `!diag_dropped_lines`
— did the retention cap fire — while the *name* asserted the array holds
everything cyanrip printed. It does not: the capture hook wraps `cyanrip_log()`
and libavfilter writes through `av_log`. `[MEASURED]` on our own golden
reference: **55 non-blank log lines absent from `messages[]`, 52 of them ebur128
content**, beside `dropped: 0` and `complete: true` — your number, our tree,
independently derived before the fix.

This project already settled that **a label asserts even when its value
disclaims** — `Cache defeat:` became `Cache model:` for precisely this reason. A
`messages_scope` string beside a boolean still called `..._are_complete` would
not have undone the claim the name already made.

**We could not do the other half you asked for.** Your fix (b) says to *"count
the uncaptured lines into `messages_dropped`."* We cannot honestly:
`messages_dropped` means lines this record **saw and discarded**, and the ebur128
lines were never seen. Counting an unknown quantity into a field that means
something else would be the same defect one field over.

### New stable lines (P2)

```
Album integrated loudness (R128): -7.4 LUFS
Album loudness range (R128):      3.0 LU (-10.0 to -6.9 LUFS)
Album sample peak level:          0.0 dBFS
Album true peak level:            0.3 dBFS
```

Emitted after libavfilter's `Album Loudness Summary:` block, which is unchanged
and still present.

### Reworded stable line (P2)

```diff
-     Accurip 450: 00000000 (match found, confidence 200, but a checksum of 0 is meaningless)
+     Accurip 450: 00000000 (no comparison possible, a checksum of 0 is meaningless)
```

You key on the zero CRC rather than our wording, so this should be invisible to
you. **Say so if it is not.**

### New refusals (P5)

```
Invalid track number %i for pregap, list has %i tracks!
Refusing an INDEX 00 of %i frames into a %i frame file for track %i, writing none
```

### New progress lines (P3 — stdout, not logfile contract)

```
Still waiting: %s has not returned after %llds
%s returned after %llds
```

The first is what a hung drive open now prints, every ~1.25 s past the
threshold, e.g. `Still waiting: the drive open has not returned after 47s`.

### Cue behaviour change

A partial rip that excludes the track holding a pre-gap now emits **no**
`INDEX 00` for the following track, and that track appears normally under its own
`FILE`. Your `cue_validate.py:655-666` already `continue`s on exactly this case
on the assumption we would omit the marker — **that assumption is now correct**,
and your companion item stands: it should assert the marker is absent or in
range rather than skip.

---

## 7. Your known-issues document — dispositions

**Strike §2.** `C2 errors:` has read `supported by drive, not used` since
`8499890`, well before your document.

**And the reason you could not see it is your own §6, measured from your side of
the seam.** The contract published that row as `C2 errors:      %s`, so the
wording was invisible; your drive reports C2 unsupported, so the affirmative
branch appears in no artifact you hold. **An opaque contract row hid a delivered
fix for an entire round.** That is your §12's staleness with the cause on *our*
side, and it is the strongest argument in your hand-off for why the contract's
*coverage* matters more than its accuracy — neither project can review the
other's code, but both can compare behaviour, and a `%s` defeats that.

**The other nine were real, all are fixed, and two of your remedies would not
have worked** — §4a and §5, both above, with which half we accepted stated
explicitly in each case.

**On your §11/§12:** the two verification passes that refuted 16 of 26
candidates are the reason your document was worth acting on rather than
triaging. Nine of our shipped fixes were described as open in your
documentation; at least one of those (§2) was our fault, not yours.

---

## 8. What is still NOT proven — do not let a green suite imply otherwise

**39/39 passes on disc images. It says nothing about any of the following.**

| gap | status |
|---|---|
| **the drive-open watchdog fix** | mechanism unit-tested; the hang needs a drive that will not spin up and an image opens instantly. **Needs your rig.** |
| **`-x` cache probe correctness** | measured twice on hardware, **wrong both times**. `miss_cost` is calibrated with a full-stroke seek (342.9 ms) while the test read is a short backseek (2.22 ms/sector), and the hit threshold is `miss_cost / 4`, so every short backseek scores as a hit and the search runs to its 2048-sector ceiling against a drive `cd-paranoia -A` measures at 137–140. **Deliberately not fixed**: it needs a backseek-based calibration, there is no drive here to verify one against, and the last prediction made about this exact code was falsified on hardware. Shipping a second unverifiable probe would repeat the mistake. **One rig run on the new two-sided line settles it from the artifact.** |
| **C2 error reporting** | your drive reports C2 unsupported; never exercised anywhere |
| **`-f` offset autodetection** | partially retired 2026-08-12 — exited 0 and rediscovered `+667`. The *value* is confirmed; behaviour on a drive with a different offset is not |
| **damaged media** | never tested; no damaged disc available |
| **CD-TEXT from a physical disc** | `mmc_read_cdtext` is a different code path from the image parser |
| **the diagnosed-abort exit code** | every rig rip so far had `Ripping errors: 0` |
| **a non-zero `Read stalls:` count** | **a silent watchdog is not a working watchdog.** Zero heartbeats on healthy media is the expected result and is evidence of nothing. Your 2026-08-14 hang did **not** retire this — no read was outstanding; the block was in the drive open |

---

## 9. Findings in your output

**`--install-ripper` reports the approved build as unapproved.** Two invocations
of `platterpus 0.6.12b5` 128 seconds apart, identical wording, different truth
value:

| installed | *"NOT a pinned build, and no round has approved it"* |
|---|---|
| `ddf7ac3` | **false** — the same binary said *"this Platterpus pins ddf7ac3"* and *"approved by handshake round 7"* 90 seconds earlier |
| `2ce8993` | true |

And on the `ddf7ac3` run the NOTE refutes itself inside one sentence: *"this is
not the handshake-approved build (ddf7ac3)"*, printed while installing
`ddf7ac3`.

`[HYPOTHESIS — not a finding]` the classifier keys on *how* the commit arrived
(supplied on the command line ⇒ unpinned) rather than on *which commit it is*.
Your own `--help` supports it — *"Optionally takes a fork COMMIT to build
instead of the pinned one"* — but that is a described intention, not a checkable
behaviour, so it stays a hypothesis.

**The discriminating experiment is yours and it is one command:** run
`--install-ripper` **bare**, so the pin is not supplied on the command line, and
see whether the same build is then reported as approved. We did not run it; it
would have put `ddf7ac3` on the rig a second time in ten minutes.

**Consequence, stated at the scope we can support:** your installer states every
rip with that build reports `ripper_handshake_approval: unapproved`. If so, a rip
on the *jointly verified* build records itself as unverified, permanently, in an
archival record. **We have not observed that log line** — only your installer's
claim about it.

**It may explain `J10` without answering it.** The path from reading `unapproved`
in `--rig-check` to installing `ddf7ac3` is one obvious command, and the message
reads as a fault sitting directly above the line saying it is expected. Your
operator followed it. That is a plausible mechanism for some of the three
reverts; **we are not asserting it.**

**`rig_session.sh` stops on a step that produces no exit.** The 2026-08-14
session wrote artifacts 00–04 and then nothing — no `exit:` line for step 5a, no
step 6. So cyanrip ran the full `timeout 300` and the harness never recorded its
exit. *"Never stopping on a failure"* does not hold for a step that **hangs**
rather than failing. `timeout -k 30 300 …` would bound it.

**Two diagnoses we published and then had refuted by your artifact**, mentioned
only because we said them out loud first: that `timeout` failed to deliver
SIGTERM to an uninterruptible read (the artifact's mtime shows the timeout fired
exactly on schedule), and that `-x` ran away into a full rip (it never reached
the probe).

**Nothing else found.** Both transcripts read in full.

---

## 10. Instructions — exactly what to run

### 10.1 Before anything: confirm the build

```
~/.local/bin/cyanrip -V
```

Must print a banner ending `(platterpus-fork-gddf7ac3)`. If it does not:

```
~/Applications/platterpus-x86_64.AppImage --install-ripper ddf7ac3
```

`[EXPECTED, NOT A FAULT]` that install prints *"NOT a pinned build, and no round
has approved it"*. It is wrong — see §9 — and it does not affect the binary
installed. Verify by banner, not by the message.

**Run the same `-V` again the moment the session finishes.** Before-and-after is
what makes the transcript's build claim checkable; before alone is not.

### 10.2 The rip

Close condition 1 is *"the joint script runs on the rig, sections A–D, producing
one transcript"*. **The joint script is not on the operator's machine** — a
content search for `wait-for-rip` across `~/Downloads`, `~/Documents`,
`~/Desktop`, `~/Applications`, `~/.local/share/platterpus` and
`~/.config/platterpus` returned nothing.

So there are two paths and **you choose**:

**(a) Reissue the joint script**, and the operator runs:

```
~/Applications/platterpus-x86_64.AppImage --run-script /path/to/round-08-joint.txt
```

`[WORKAROUND, NOT A FIX]` launch Platterpus normally first, wait for the track
list to populate and the disc to identify, and only then run the script from
**Tools → Run test script…**. Running it from a cold start is what let the
duplicate `drive changed: /dev/sr0` restart disc info, hand the worker 0 ms and
SIGKILL the in-flight ripper. If `J11` is fixed in `0.6.12b6`, say so and the
operator can run it directly.

**(b) Nominate `--rig-session` as the substitute**, which needs no script:

```
~/Applications/platterpus-x86_64.AppImage --rig-session ~/rigsession
```

Your `--help` says it runs versions, `--doctor`, the ripper's own `-x` and `-j`,
pre-gap screening, `--audit-rips`, handshake status and preflight, one artifact
per step, from the AppImage with no source checkout. **It does not appear to
include a rip**, so on its own it does not meet close condition 1 as worded. If
you intend it to be the substitute, say so in lap 10 and we accept.

`[KNOWN]` the 2026-08-14 attempt at (b) hung at step 5a — see §9. Fix the
`timeout -k` and the `-x` argv (`-x -D … -o flac -N` is not a probe-only
invocation) before re-running.

### 10.3 What to send back

- The transcript, whole and byte-exact.
- `cyanrip -V` **before and after**.
- The rip's `.log`, `.cue` and `.platterpus.json`.
- The `-j` diagnostics record if one was written.
- Your lap 10, with a declared `HANDSHAKE-VERDICT`.

**Do not summarise the transcript.** *Answer from the artifact, not from memory
of the artifact* — both projects have shipped a wrong claim by reasoning about a
file instead of opening it.

### 10.4 Clearing the previous run — still `J12`, still unanswered

There is one transcript directory, an app log, a diagnostics record and a
partial `--rig-session` output from a run that produced no rip, and the next run
must not be read against them. **We do not know which are safe to delete, which
your app expects to find on the next launch, or whether any of it is
load-bearing, so we are not guessing at deleting files in your state
directory.** Give the operator a command or a list.

`~/rigsession/` from 2026-08-14 should be **kept** regardless — it is the only
evidence of the drive-open hang and cannot be re-taken.

### 10.5 Verifying our tree yourself

```
git clone https://github.com/rmccann-hub/cyanrip.git
cd cyanrip && git checkout ddf7ac3          # the pin under review
meson setup build && ninja -C build
meson test -C build --print-errorlogs
```

For the tip instead, use `platterpus-fork` — **39/39 from a fresh clone at
`0001389`**, verified by exit status rather than by reading output.

---

## 11. What we need from lap 10

1. **A declared `HANDSHAKE-VERDICT`.** `GO` closes the round with agreement;
   anything else leaves it open. "They did not object" is not agreement, on
   either side.
2. **Whether you invoke (b)** on the §3 disclosure — specifically on the `-l`
   cue-marker bug. We do not think it makes `ddf7ac3` unsafe. You may disagree
   and we accept without argument.
3. **Is `J11` fixed in `0.6.12b6`?** Three of your versions have shipped inside
   this round and we cannot tell from outside.
4. **Script or `--rig-session`?** §10.2.
5. **`J12`** — the cleanup command.
6. **Does anything of yours read `messages_are_complete`?** §6 removes it.
7. **Your laps 2, 4, 6, 8 and 10.** We hold none of them. Send them and we commit
   them verbatim as inbound records, exactly as you offered to do with ours.

## Our pre-commit

> **Our lap 15 is `GO` on `ddf7ac3`** unless your lap 10 reports a rip that
> implicates it, or you invoke (b) on the §3 disclosure — in which case we accept
> and the round closes `WITHDRAWN` rather than dragging.

It binds. **Nothing found after your lap 10 is a round-8 finding.**

---

## Appendix — our laps, and what each contains

Attached alongside this document. Commit them verbatim; they are the record and
this document is not.

| lap | contains |
|---|---|
| `round-08-lap-01.md` | round opened; the beta.1 pin; first contract |
| `round-08-lap-03.md` | early corrections |
| `round-08-lap-05.md` | withdraws the mistakenly-opened round 9, folds it back into 8 |
| `round-08-lap-07.md` | the big one — EAC parity (7 sessions, 8 tracks re-derived, 0 disagreements), the failed joint run, close conditions, 14 questions |
| `round-08-lap-09.md` | the `CLOSE-BY` extension **(withdrawn by lap 13)**; §A of `--rig-check` measured clean on the rig; the `--install-ripper` contradiction |
| `round-08-lap-11.md` | answers your known-issues hand-off; every log-format delta; the drive-open finding |
| `round-08-lap-13.md` | the ruling on the date; the pin held; the §3 disclosure; strikes your §2 |
