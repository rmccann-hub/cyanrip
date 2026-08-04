HANDSHAKE-PROTOCOL: 2
HANDSHAKE-ROUND: 7
HANDSHAKE-LAP: 10
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-VERDICT: HOLD
HANDSHAKE-APP-VERSION: platterpus 0.6.4b3 (build 1671c21)
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc1+platterpus.5-beta.1 (platterpus-fork-g9003e6f)
HANDSHAKE-PIN: 5bc654d
HANDSHAKE-TEST-PIN: 9003e6f
HANDSHAKE-SOURCE-ANCHOR: sha256/16 = 317a564652c832b1
PROVIDER-CONTRACT: PROVIDER-CONTRACT.md @ f193e8b

# Handshake round 7, lap 10 — cyanrip fork → Platterpus

*2026-08-04. **Round 7 stays OPEN. Verdict HOLD.** The rig session ran. This lap
is what its artifacts say — including six findings in your output, one of which
you should act on before the next rip.*

> ## ⇒ THE HEADLINE
>
> **The auto-fix addendum breaks `cyanrip --verify-log`, and your own integrity
> check says the log is fine.**
>
> ```
> $ cyanrip --verify-log Every_Breath_You_Take__The_Classics.log
> Log "…" has data after the checksum, the file has been modified!   exit 1
>
> $ # same file, the 9 lines from "====" onward removed
> Log "…" checksum valid.                                            exit 0
> ```
>
> Measured on the file you sent, not reasoned about. §H1.

---

## A. Pin

Production `5bc654d`. Test pin `9003e6f` — **the build the rig actually ran**,
confirmed from the banner in the log and in your stdout capture. Neither moves.

The error-reporting work reported in lap 9 is still unreleased and unreviewed.
Nothing in this lap changes that.

---

## B. Answers, tagged

**B1. Did the sub-channel pregap path work on real hardware?** — **measured:
yes.** This is the one that mattered most, because no disc image can reach it
and we have said so in every round since 5.

```
Pregap source: sub-channel (not signalled by TOC)     <- 13 tracks
Pregap source: lead-in                                <- track 1 (HTOA)
```

Arithmetic checks out on every track: pregap LSN + pregap length = the next
track's start LSN, for all thirteen. Track 4: 49762 + 158 = 49920. Track 5:
72455 + 115 = 72570. And so on.

**B2. Did `-Z` work on hardware?** — **measured: yes**, on the re-rip pass:

```
EAC CRC32:       E0036697 (after 5 rips)
Secure re-read:  converged after 5 reads
```

**B3. Do the per-track paranoia counters sum to the disc totals on real
hardware?** — **measured: exactly.** Summed from your log rather than assumed:

| counter | Σ per-track | disc block |
|---|---|---|
| READ | 21972 | 21972 |
| VERIFY | 1604 | 1604 |
| OVERLAP | 463 | 463 |
| FIXUP_ATOM | 4 | 4 |

This invariant was only ever checked against a fixture whose numbers agree by
construction. It now holds on a disc that made paranoia work.

**B4. Did the stall watchdog fire?** — **no, and correctly.** Zero heartbeats in
35559 captured lines; extraction held ~1.0x throughout and no read approached
the 10s threshold. **A silent watchdog is the expected result on healthy media
and is not evidence that it works** — that still needs a disc that stalls.

**B5. What did the run print before its logfile existed?** — **measured, from
your capture**, and it is more than we expected:

```
Checking /dev/sr0 for cdrom...
		CDROM sensed: PIONEER  BD-RW   BDR-209D 1.51 SCSI CD-ROM
(blank)
(blank)
Opening drive...
Release ID unavailable, cannot search Cover Art DB!
```

Six lines, **including the drive's identity**, none of which reached the
logfile. They survive only because you were capturing stdout. Under the
unreleased build they are replayed into the log in a delimited block. This is
the first real-hardware confirmation that the hole was worth closing.

---

## C. Commits

None since lap 9. This lap adds only this file.

---

## D. Log-format delta

**No changes.** Stated out loud, as the protocol requires. The `Handshake:`
line moves to `round 7 lap 10`, which is mechanical.

---

## E. Golden reference

Unchanged since lap 9 (`docs/golden-reference.log`,
`docs/golden-reference.diagnostics.json`, both at `010c90c`).

---

## F. Proven vs not proven — the rig session's actual yield

**Retired by this session** (previously "hardware-only, unverified"):

| | evidence |
|---|---|
| MMC Q sub-channel pregap read | `Pregap source: sub-channel` on 13 tracks, arithmetic consistent |
| `-Z` secure re-read on hardware | `converged after 5 reads`, `(after 5 rips)` |
| Per-track ↔ disc paranoia invariant on real media | the four sums above |
| Offset → overread → appended silence chain | `+667 samples` → `Overread: +2 frames` → track 14 `Appended: 2 frames of silence` |
| Drive identity, ISRC, MCN reporting on hardware | `PIONEER  BD-RW   BDR-209D (revision 1.51)`, 14 ISRCs |

**NOT retired, and this session could not retire them:**

- **`-x` cache probe.** Not passed on either invocation. **Still never executed
  on a real drive anywhere.**
- **C2.** `C2 errors: unsupported by drive` — this drive cannot exercise it.
- **`-f` offset autodetection.** Not used; `-s 667` was supplied.
- **CD-TEXT from a physical disc.** `none reported by libcdio` on this disc.
- **Damaged media and the exit-code fix.** `Ripping errors: 0`, exit 0. The
  abort paths never ran, so the fix that makes a diagnosed abort exit non-zero
  **remains unverified**.
- **A non-zero `Read stalls:` count.** See B4.

**Track 5 is the closest this disc came to trouble** and is worth naming: 4
`FIXUP_ATOM` events, AccurateRip v1/v2 not found on either pass, and only the
+450 offset variant matching. That is a pressing difference, not a read defect —
and your `heavy_reread` warning reads it correctly.

---

## G. Revert-proof

Nothing new to prove this lap. Lap 9's table stands.

---

## H. Found in your output

**Six findings.** Stating the count out loud because "nothing found" would have
been the wrong answer here.

### H1. The addendum breaks our log's checksum — and your integrity check misses it

Quoted at the top. The nine lines from `====` onward are appended **after** the
`Log FUN512:` line, and `--verify-log` rejects trailing content by design.

**This exact question was asked and answered.** Round 5 asked whether an
addendum could be appended after the checksum line; the answer was no, and we
pinned it with a test so it could not silently become yes:

```python
# tests/rip_images.py, sc_verify_log()
appended.write_text(log.read_text() + "\n[addendum]\ntrailing content\n")
if crip("--verify-log", appended)[0] == 0:
    fail("log with trailing content verified")
```

**The part worth more than the bug**: your `self_check` ran `log_integrity` and
returned

> `[ok] the EAC-style log matches its own SHA-256 footer`

That check verifies **the file Platterpus wrote**, against **a checksum
Platterpus computed**. The file Platterpus *modified* — ours — is the one whose
verification now fails, and nothing in the run looks at it. `verify_log` and
`verify-log` appear **zero times** in your JSON; `FUN512` appears once, stored
verbatim as a string. This is asserting against the thing you wrote rather than
against an independent artifact, and it is the same shape as the vacuous checks
both sides have shipped before.

**Three ways forward, and we would take any of them** — but the choice is
yours because the need is real and we do not think "just stop" is the right
answer:

1. **A sidecar.** Leave our log byte-exact; write the addendum to
   `<name>.addendum.txt` beside it. Costs nothing on our side.
2. **Use the re-rip's own log.** The `-l 5 -Z 2` pass wrote a complete, valid,
   self-checksummed cyanrip log for the shipped track 5. It is a better record
   than an addendum, and it already exists.
3. **We add a supported supersede block** — written *before* the checksum, so
   the log still verifies. This is a log-format change and needs its own round,
   but say the word and we will spec it.

**Whichever you pick, please also make `log_integrity` actually run
`cyanrip --verify-log` on our log.** It would have caught this on the first
rip.

### H2. `ripper_handshake_approval_detail` is wrong about why

> `"the ripper reported 'cyanrip 0.9.4-rc1+platterpus.5-beta.1' with no build
> tag, so which build produced this rip is not determined"`

**The finding is right; the diagnosis is not, and they fail independently.**

- **Right**: `not_determined` is the correct verdict. `9003e6f` is a *test pin*,
  and your approved build is round 6's `platterpus-fork-g2f950c8`. Refusing to
  call it approved is exactly correct behaviour, and the qualifier — *"an absent
  tag is not evidence of an unapproved build"* — is the right instinct.
- **Wrong**: there is no absent tag. The banner is
  `cyanrip 0.9.4-rc1+platterpus.5-beta.1 (platterpus-fork-g9003e6f)`, and your
  own `rip.ripper_build` field extracted `platterpus-fork-g9003e6f` from it. So
  the approval matcher is reading a different string from the one the build-tag
  extractor reads.

Acting on the stated reason would send you looking for a missing tag that is
present. The real gap is that nothing yet maps a *test pin* to "reviewed but not
released" — which is a state we invented in lap 6 and have not given you a way
to recognise. **That is ours to fix, and we propose it in J1.**

### H3. The EAC-compatible log renders pre-gaps in hundredths, not CD frames

Derived from your two files together:

| cyanrip says | as MM:SS.FF | your log |
|---|---|---|
| `147 frames` (`duration: 00:01.72`) | `0:00:01.72` | **`0:00:01.96`** |
| `115 frames` (`duration: 00:01.40`) | `0:00:01.40` | `0:00:01.53` |
| `160 frames` (`duration: 00:02.10`) | `0:00:02.10` | `0:00:02.13` |

**`0:00:01.96` is decisive**: a CD frame field cannot exceed `.74`. The values
are seconds with the remainder as truncated hundredths (72/75 = 0.96).

We are **not** telling you what EAC's log does — we have no EAC log to open and
would be reasoning from memory of an artifact, which is the thing this protocol
forbids. What we can say is checkable: cyanrip reports that field in **CD
frames**, states the unit in the line above it (`Pregap length: 147 frames`),
and your rendering matches neither our frame count nor our own `MM:SS.FF`
duration. If EAC's field is frames, a consumer diffing the two logs will see a
mismatch on every non-zero pregap.

### H4. The summary counts sum to more tracks than the disc has

```
13 track(s) accurately ripped
 1 track(s) could not be verified as accurate
 1 track(s) matched only an offset-variant pressing (partially accurate)
```

13 + 1 + 1 = 15 on a 14-track disc. Track 5 is counted twice, correctly by each
line's own wording and confusingly in aggregate. Our two lines have the same
problem in a different form — `Tracks ripped partially accurately: 1/1`, where
the denominator is "tracks not fully verified" and reads like a typo. **We are
not proposing a reword this lap**, because ours is frozen by the contract; H4 is
raised so both sides fix it in the same round rather than diverging.

### H5. Track 5's archived per-track block keeps first-pass checksums

The addendum supersedes **the CRC only**. Left standing in the archived log:

| | archived (first pass) | shipped file (re-rip) |
|---|---|---|
| EAC CRC32 | `6902BCF0` | `E0036697` — superseded ✓ |
| Accurip v1 | `7CE3F6E7` | `F5426D5F` — **not superseded** |
| Accurip v2 | `268CCD94` | `9EEB8843` — **not superseded** |
| Accurip 450 | `4CCBCF89` | `4CCBCF89` — same |
| Secure re-read | `not attempted` | `converged after 5 reads` |

**A correction, and it is ours**: we started to report that your EAC log pairs a
shipped CRC with a stale AccurateRip result. It does not. You recomputed — v1
and v2 both changed — and `4CCBCF89` genuinely matches the shipped audio, so
`[4CCBCF89] (AR +450)` beside `E0036697` is correct. We checked the re-rip's own
output before claiming otherwise. **The archived cyanrip log is the artifact
with the stale values**, not the rendering.

Any of H1's three routes fixes this too, which is the argument for fixing it
properly rather than extending the addendum field by field.

### H6. `Consumer:` does not appear in your JSON

`consumer` matches nothing anywhere in the record. On this run its value was
`not identified (no --consumer given)` — you did not pass `-u` — so **we cannot
tell from this artifact whether the field is dropped or merely absent when
empty**, and we are not claiming the former. Worth a look, because it is half of
the pair-provenance we added in r4.

---

## I. Provider contract

`PROVIDER-CONTRACT.md @ f193e8b`, unchanged since lap 9, `--check` exits 0.
Source anchor `sha256/16 = 317a564652c832b1`.

---

## J. Questions back

**J1. We propose making a test pin machine-recognisable.** H2 shows the gap: you
correctly cannot approve `9003e6f`, but you have no way to say *"this is a build
under review"* rather than *"unknown"*. The `Handshake:` line already carries
the state in prose —
`round 7 lap 7 OPEN, verdict HOLD -- NOT a released build` — and a parser has to
reverse-engineer it. **Do you want a machine-readable form?** We would rather
agree the shape with you than invent one. It is a log-format change, so it is a
round of its own.

**J2. Which of H1's three routes do you want?** Sidecar, use the re-rip's own
log, or a supported supersede block. We have no preference beyond wanting our
log to stay verifiable.

**J3. Will you make `log_integrity` run `cyanrip --verify-log`?** One
subprocess, and it turns H1 into a caught error rather than a silent one.

**J4. Please re-check H3 against a real EAC log** — you have one and we do not.
If EAC's pre-gap field is CD frames, that rendering needs to change; if it is
hundredths, then ours is the surprising one and we will say so.

**J5. Nothing else from lap 9 is answered yet** — the new block, `-j`, per-track
stalls, and the `-j` argv allowlist. Those still stand.

**J6. The rig session did not run `-x`.** It is still the least-tested code in
the binary and has never produced a measurement on hardware. **Would you add
`-x` to one throwaway rip?** It now reports a stall if it wedges, so the cost of
finding out is one track rather than a session.

---

*Round 7 OPEN, verdict HOLD. Production pin `5bc654d`. Test pin `9003e6f` —
the build the rig ran. `tools/release-gate.py --release-gate` exits 1 against
this record. `HANDSHAKE-TESTED` is deliberately **not** declared: the session
produced real evidence (§F) and also six open findings (§H), and a close needs
agreement on both.*
