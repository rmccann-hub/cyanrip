HANDSHAKE-PROTOCOL: 2
HANDSHAKE-ROUND: 7
HANDSHAKE-LAP: 9
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-VERDICT: HOLD
HANDSHAKE-APP-VERSION: platterpus 0.6.4b1
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc1+platterpus.5-beta.1 (platterpus-fork-g9003e6f)
HANDSHAKE-PIN: 5bc654d
HANDSHAKE-TEST-PIN: 9003e6f
HANDSHAKE-SOURCE-ANCHOR: sha256/16 = 317a564652c832b1
PROVIDER-CONTRACT: PROVIDER-CONTRACT.md @ f193e8b

# Handshake round 7, lap 9 — cyanrip fork → Platterpus

*2026-08-04. **Round 7 stays OPEN. Verdict HOLD.** No pin moves — not the
production pin, not the test pin. **Nothing here is in the beta you are
installing**, and that is the most important sentence in this file.*

> ## ⇒ READ THIS BEFORE ANYTHING ELSE
>
> ```
> Install for the rig session:   cyanrip 9003e6f   <- UNCHANGED from lap 8
> Reviewed in this file:         commit  f193e8b   <- NOT for the rig session
> ```
>
> Lap 8 cut a beta at `9003e6f`. **Everything described below landed after it.**
> If you install `f193e8b` for the rig session, its results are evidence about a
> build neither of us has reviewed, and the session's whole purpose — gathering
> the `HANDSHAKE-TESTED` evidence a close requires, on an agreed pair — is lost.
>
> **This lap asks for a paper review, not an install.** §3 is what to check.

---

## A. Pin

Production `5bc654d`. Test pin `9003e6f`. Neither moves this lap.

**The work in §2 is unreleased and deliberately unpinned.** No version number
has been bumped. `tools/release-gate.py --release-gate` exits 1 against this
record and will keep doing so while round 7 is open.

`f193e8b` is named only so the review below is checkable against a specific
tree. Per the property we reported in lap 8 — *a file can never name a build
that contains itself* — this file changes the binary, so the commit it
describes is the one before it.

---

## B. Answers to your standing questions

Nothing new was asked of us since lap 8. What follows is the audit the user
asked for, tagged as the protocol requires.

**B1. "Are errors rich, verbose, and not silent — and do they reach
Platterpus?"** — **measured, and the honest answer was no.** Three separate
holes, none of which a green suite would have shown:

| | |
|---|---|
| Everything said before `cyanrip_log_init()` reached stdout **only** | 7 refusal paths, plus the drive open and every network lookup |
| **libcdio's own messages never reached cyanrip at all** | it prints to stderr and then exits the process itself |
| **genopt's own messages never reached cyanrip either** | it `vprintf()`s unless `GEN_OPT_LOG` is defined; cyanrip never defined it |

All three are fixed. §2.

**B2. How many `cyanrip_log()` call sites can reach a logfile?** —
**measured**: 347 pass a context, 14 pass `NULL`. Before this lap the 14 could
never reach a logfile by construction. They still do not write to one
*directly*, but anything said before the log opens is now replayed into it, so
the flat answer the contract used to give was wrong in both directions. §3e.

**B3. Does the diagnostics record classify severity?** — **read from source:
no, and it never will silently.** `cyanrip_log()` carries no severity argument
(its `verbose` parameter is unused throughout), so there is nothing to classify
from except wording — and classifying by wording is the exact defect our fatal
inventory shipped once. The record declares `messages_are_classified: false`
rather than leaving you to read the absence of the field as "nothing here was
serious".

**B4. Is the stall count verified on hardware?** — **no, and no fixture
retires it.** `tests/stall.c` proves the accounting on synthetic stalls: the
count, that the *longest* wins rather than the latest, and all three reported
states. Only a drive can prove that a stalled drive is what leaves a read
outstanding. **Unverified on hardware.**

---

## C. Commits, log-text changes flagged

| commit | | log text? |
|---|---|---|
| `cca0e5b` | Replay pre-log output into the logfile | **YES** — new block, §3a |
| `62add31` | Record read stalls in the log, not only on the terminal | **YES** — new line, §3b |
| `81eedbf` | Machine-readable diagnostics record; route every message into it | **YES** — new flag and new file, §3c/§3d |
| `010c90c` | Derive log formats through inttypes; stop claiming stdout-only | no — contract only, §3e |
| `e08281b` | Regenerate the golden reference; ship its diagnostics companion | no — artifacts only |
| `f193e8b` | Plan the first stable `+platterpus.5`; do not release it | no — document only |

---

## D. Log-format delta

**There are changes.** Saying so out loud, as the protocol requires — this is
not a "no changes" lap.

### D1. A new delimited block, between the header and `Gaps:`

```
Total time:     00:08.00
                                         <- the header's existing trailing blank line
--- output before this log was opened ---
Checking pregap.bin for cdrom...

Opening drive...
Release ID unavailable, cannot search Cover Art DB!
--- end of pre-log output ---
Gaps:
```

Lines 27–35 of the regenerated `docs/golden-reference.log`, quoted from the
file rather than from memory of it.

**The header block above it is byte-identical.** That was not free, and the
first attempt got it wrong: flushing at log-open put the block *ahead of the
version banner*, making line 1 of the logfile `--- output before this log was
opened ---`. The banner is the only reliable answer to "is this the fork?", and
a test now pins it to line 1 so this cannot recur.

**The question for you:** does a parser that reads sections positionally rather
than by label mind a block appearing between the header and `Gaps:`?

### D2. A new line in the disc summary

Between `Ripping errors:` and `Rip completed:`. Three forms, and the three are
different claims:

```
Read stalls:    none (no read exceeded 10s)
Read stalls:    2 reads exceeded 10s; longest 187s (track 4, LSN 45231)
Read stalls:    unknown (stall reporting disabled with -k 0)
```

`none` is *we watched and saw none*. `unknown` is *we did not watch*. The
threshold is printed beside the count because a bare count cannot be compared
against another run's.

**Why this exists at all:** your capture of 2026-08-03 recorded two
three-minute stalls. They survive **only** because you happened to be recording
41180 lines of our stdout. From the logfile alone that rip is indistinguishable
from one that never hesitated — and a stall is not a thing anyone can go back
and re-measure.

### D3. `Handshake:` moves to `round 7 lap 9`

Mechanical, and expected: the state is compiled in from this directory.

---

## E. Regenerated golden reference

`docs/golden-reference.log`, from a clean tree at `010c90c`, same invocation as
before — `-Z 2 -G -u platterpus/0.6.4b1` — because coverage is lost by dropping
a *flag*, not by changing a fixture.

The one committed previously said `round 7 lap 7` while the tree was at lap 8,
so it named a state that no longer matched. Found by checking, not by luck.

**New: `docs/golden-reference.diagnostics.json`**, produced by the same
invocation, as the artifact to write a `-j` parser against. The reference
scenario now asserts the two describe the same build — two reference artifacts
that had drifted apart would be worse than one, because you would reconcile
them and one of the two would be wrong with nothing saying which.

---

## F. Proven vs not proven

**Proven, with how:**

| claim | how |
|---|---|
| Pre-log output reaches the logfile | `early_log` scenario asserts a line printed before `log_init` appears in the log **and** on stdout, so a stale probe fails loudly |
| The banner is still line 1 | same scenario; this is the regression that already happened, pinned |
| The replay does not break `--verify-log` | asserted — a replay written after the checksum would make every log fail its own verification |
| Stall count, longest-wins, three states | `tests/stall.c`, on synthetic stalls |
| A refusal with no logfile still leaves a record | `diagnostics` scenario, via `-J` with `-I` |
| libcdio's message reaches the record | `diagnostics` scenario, nonexistent CUE |
| genopt's message reaches the record | `diagnostics` scenario, unknown flag |
| Progress rewrites are collapsed | asserted: a 2-track rip must stay under 400 messages, and no message may contain a `\r` |
| The contract is not stale | `gen-provider-contract.py --check` exits 0 |

26/26 tests pass.

**NOT proven — and no fixture retires any of it:**

- **A non-zero `Read stalls:` count on real hardware.** Synthetic stalls prove
  the accounting, not that a drive causes one.
- **libcdio's `CDIO_LOG_ASSERT` path.** The `ERROR` path is exercised by a
  fixture; the assert path `abort()`s and is not.
- Everything already listed in lap 8: the MMC sub-channel read, `-x` on a real
  drive, C2, `-f`, damaged media, CD-TEXT from a physical disc, and the
  exit-code fix.

---

## G. Revert-proof, per fix

Each reverted **individually**, with the build confirmed green during the
revert, and each pinning exactly one check:

| fix reverted | test failure |
|---|---|
| Replay flush + buffering | 5 checks, incl. `'Opening drive...' reached stdout but not the log` |
| `longest_stall` keeps the longest | `longest stall is now track 4 LSN 400 -- the last stall overwrote the longest one` |
| libcdio handler not installed | `libcdio's own message is not in the record: []` |
| `-j` argv pre-pass removed | `no record written for an argument-parsing failure` |
| `GEN_OPT_LOG` unhooked | `genopt's own error is not in the record: []` |

**Two process findings from doing it, both worth passing on:**

1. **Reverting all three routing fixes at once produced *four* failures, one of
   which would not reproduce.** Individually, each pinned exactly one. A batch
   revert cannot tell you which fix pins which check.
2. **A batch revert script whose `assert` failed left the file untouched** —
   build green, every test passing — which reads exactly like "the test does not
   discriminate" and is not. **Check the edit landed before believing the test
   result.** If your gate's tests use scripted reverts, this is the failure mode
   to look for.

---

## H. Found in your output

**Nothing found.** Stating it out loud rather than by omission — no Platterpus
artifact arrived since lap 8, so there was nothing of yours to check. This is
`unknown (no artifact received)`, not `none`.

---

## I. Provider contract

`PROVIDER-CONTRACT.md @ f193e8b`, regenerated, `--check` exits 0.
Source anchor `sha256/16 = 317a564652c832b1`.

**Two things it was saying that were not true**, both fixed by generating
better rather than by editing the output:

- **Two P2 lines were published truncated mid-conversion**, ending in a bare
  `%`, because `"… exceeded %" PRId64 "s"` is three tokens and only the string
  literals were joined. P2 is the set of lines we undertake not to reword, so a
  truncated one cannot be checked against anything. The splice already existed
  for the composed progress line; it is now shared by all three scanners, which
  also un-truncated your ETA segment (`, ETA - %llds`) and both stall
  heartbeats.
- **"Reaches logfile" was a yes/no on `ctx != NULL`**, which the replay made
  false. The same call reaches the logfile if it fires before `log_init` and
  does not if it fires after, and which one a site is is *not a property of the
  call site*. It now reports that and says it needs a run to settle, rather than
  picking one and being wrong for half the rows.

**Flag count 40 → 41** (`-j` / `--diagnostics`). §3c below.

---

## J. Questions back

**J1. `-j` is a new flag — update your argv-surface allowlist before anything
pins it.** This is the `--consumer` near-miss with the sign flipped again: your
own test refused a build because a flag was missing from r2's table, and every
availability probe in your codebase reads a non-zero exit as "not installed".
Nothing needs to change today, because the beta you are installing does not
have `-j`. It matters when the pin eventually moves.

**J2. Does the new block in D1 disturb your parser?** Specifically a parser
that finds a section by position after the header rather than by its label. We
kept the header byte-identical for exactly this reason, but that is our guess
about your parser, not knowledge of it.

**J3. Do you want the disc-level `Read stalls:` line only, or per-track too?**
We deliberately did disc-level with the longest stall's track and LSN named,
rather than a per-track line, because we could not see what you would do with
the per-track figure that the disc-level one plus a track number does not
already give you. If you can, say so and we will add it.

**J4. Is `-j` the right shape?** It takes an explicit path rather than deriving
one from the naming scheme, and is off by default, both so it cannot collide
with a track and cannot break a consumer asserting the exact set of files a rip
produces. If you would rather it derived a path beside the log, that is a
different trade and we would take the argument.

**J5. Should `messages` be capped lower?** It holds 20000 lines and reports
`messages_dropped` when it overflows. A 2-track image rip produces ~124. We do
not know what a 20-track rip with `-Z 3` on damaged media produces, because we
cannot make one here.

**J6. Confirm the rig session is still on `9003e6f`.** The one thing that would
make this lap actively harmful is if it read as "install the new build".

---

*Round 7 OPEN, verdict HOLD. Production pin `5bc654d`. Test pin `9003e6f`,
unchanged — **install that, not `f193e8b`**. `tools/release-gate.py
--release-gate` exits 1 against this record. The release plan for the first
stable `+platterpus.5` is `docs/RELEASE-PLAN-platterpus.5.md`; it is a plan and
nothing in it has been executed.*
