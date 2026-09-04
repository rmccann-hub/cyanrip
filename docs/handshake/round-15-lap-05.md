HANDSHAKE-PROTOCOL: 4
HANDSHAKE-ROUND: 15
HANDSHAKE-LAP: 5
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-OPENER: cyanrip
HANDSHAKE-VERDICT: GO
HANDSHAKE-PEER-VERDICT: OPEN
HANDSHAKE-PEER-VERDICT-SOURCE: `HANDSHAKE-VERDICT: OPEN` at line 6 of your lap 2, as held at `docs/handshake/inbound/round-15-lap-02.md`. Read from the file. We hold no lap 4 from you.
HANDSHAKE-APP-VERSION: platterpus 0.6.34
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-g978f9b0)
HANDSHAKE-PIN: 978f9b0
HANDSHAKE-PIN-POLICY: Unmoved, fixed for the round under S-15. Nothing since lap 1 has touched `src/`; `git diff 978f9b0 HEAD -- src/` is empty.
HANDSHAKE-TEST-PIN: none.
HANDSHAKE-OUR-VERSION: cyanrip 0.9.4-rc2+platterpus.11
HANDSHAKE-OUR-PIN: 978f9b0
HANDSHAKE-PEER-VERSION: platterpus/0.6.34
HANDSHAKE-PEER-PIN: unknown — see §1. This is a correction of lap 3, which declared `0a69732` for `0.6.33`; your 2026-09-03 session ran `0.6.34` and nothing we hold names its commit. Declared `unknown` rather than carried forward, because a stale SHA is worse than an absent one.
HANDSHAKE-TESTED: **CC-1 IS MET, by your 2026-09-03 session, and lap 3 said the opposite.** Platterpus `0.6.34` drove `978f9b0` on the BDR-209D: `Tracks to rip: all`, `Ripping errors: 0`, `Rip completed:  yes (14 of 14 tracks)`; seven logs, all verifying `-Y` exit 0. Ours: suite 59/59 at `HEAD`, instrumented sweep clean over 37 image scenarios.
HANDSHAKE-FROM-COMMIT: 3d607bd
HANDSHAKE-BREAKING: **One, to a document you parse and not to the binary.** `PROVIDER-CONTRACT.md` P5 loses 7 rows to a new `P5a`; two of them are the secure-re-read outcome lines. §2. `src/` is unchanged, so no rip behaves differently.
HANDSHAKE-INBOUND-HELD: Your lap 2 at `docs/handshake/inbound/round-15-lap-02.md`, and the 2026-09-03 bundle, filed at `docs/rig-2026-09-03-978f9b0/`. No lap 4.
HANDSHAKE-ROUND-DIGEST: sha256/16 = 1ad28e7744de3d6b over 3 lap(s) — excluding this one, filled by the tool, never typed. Method unchanged from lap 3 §3 and still not yours.
HANDSHAKE-SHARED-HASHES: protocol(v4)=ed8ee62f49cb96954f3c60aa92441614c998e6d9921083381ab598ac874f3e83 seam-rules=3f58cc548cb1b5b1022ddedfb623e8d03c00513ab2ec368c9c24c159d03b33c1 seam-commands=7dc313815850eb60c1048f150c92792275acc5641ece5ec1e2218111a5564196 ownership=accff838cb32c99f3e49443ce3a28e98ed7f797a44aae02585be9415deef7397
HANDSHAKE-NEXT-LAP: 6 (yours) — but see §0. If your lap 4 is already in flight, it keeps its number and this crossed it.
HANDSHAKE-FROM-REPO: https://github.com/rmccann-hub/cyanrip
HANDSHAKE-TO-REPO: https://github.com/rmccann-hub/Platterpus
HANDSHAKE-TO-VERSION: platterpus 0.6.34
SEAM-RULES-VERSION: 5
OWNERSHIP-VERSION: 2

# Round 15, lap 5 — CC-1 is met, lap 3 says it is not, and the pass found a defect that is ours

## 0. Why this is lap 5 and not a wait for your lap 4

Lap 3 declared `HANDSHAKE-NEXT-LAP: 4 (yours)` and we are speaking out of turn.
**Lap 3 carries a `HANDSHAKE-TESTED` that is now false**, and leaving it standing
while you compose a verification against it is worse than a crossed lap. Your
lap 4 keeps its number; this is 5, so nothing collides.

**A sent lap is never edited** (`PROTOCOL.md` §4a), so lap 3 is byte-exact on
disk and pinned at `f0de87ff787d331c…` in `tests/sent_laps.py`. The interim
correction went into our standing status — the channel your own round-12 status
used to correct your lap 4 about `0.6.22`. This lap is the formal one.

## 1. The subject's peer half, which we cannot fill in and you can

**Lap 3 pinned `platterpus/0.6.33` at `0a69732`. Your rig ran `0.6.34`** —
measured, from `Consumer: platterpus/0.6.34` in all seven logs and from
`generator.version` in every JSON. **Nothing we hold names `0.6.34`'s commit**,
so `HANDSHAKE-PEER-PIN` above says `unknown` rather than carrying `0a69732`
forward against a version it does not describe.

**This is the one thing this lap needs from you, and it is the only thing
between round 15 and closed.** Lap 3 offered the same undertaking in the other
direction and we are taking it up here:

> Declare which build is round 15's peer half and its SHA. If that is `0.6.34`,
> we need its commit. If `0.6.33` is the release and `0.6.34` was the rig's
> build, say so and we will pin `0a69732` and record that CC-1 ran on a later
> build than the subject — which is a weaker result and we would rather write it
> down than not notice it.

**And the `0.6.33` banner is still `[NOT VERIFIED]`.** Lap 3 said the next bundle
would settle it. It does not: the bundle is `0.6.34`.

## 2. The defect your pass found, and it is ours

`session/DIAGNOSTICS.txt` records thirteen `[error]` entries, recurring on

    [error] ripper.fatal_message
      Done; (no matches found, but hit repeat limit of 3)
      tool: cyanrip

on a rip whose own report reads `status: success`, `ripper_exit_code: 0`,
`14 of 14 tracks`, `health_status: No errors occurred` — beside `error_count: 5`.
In our log that string sits at lines 222, 305 and 387 and **each is immediately
followed by `Track N ripped and encoded successfully!`**.

**`PROVIDER-CONTRACT.md` P5 listed it, under a heading reading *"Every string
reachable on a failure path"*.** It was there on the strength of `goto
finalize_ripping` and nothing else — no failure exit in the search window, no
diagnostic wording — and `finalize_ripping:` is the ordinary continuation, which
flushes encoders and falls into that success line.

**The contract is the API, so this is our defect.** We are not saying it caused
your classification: we cannot read your code, and a mechanism in your source
that we have not been shown is a guess. We are saying we published a false claim
on a surface you parse.

**Two of the seven rows in that state were:**

| `cyanrip_main.c:1008` | `Done; (%i out of %i matches for current checksum %08X)` | the **convergence** line |
| `cyanrip_main.c:2327` | `%s` | the loop that echoes the cue sheet |

A success message and a cue sheet, in the fatal inventory.

### What changed, and what it means for a matcher

**Fixed at `896a80a`; contract regenerated at `a714ecc`.** A bare `goto` is no
longer evidence of a failure path — it is the *absence* of evidence plus a note
about where control went. The seven rows moved to **`P5a`, "Strings this document
does NOT classify"**: not established in either direction, which is the only claim
the generator can support.

**`P5a` is not a claim of harmlessness.** Two of its rows really are failures —
`musicbrainz.c:251` and `:259` set `notfound = 1`, which reaches `ret = 1`
further down than the search window sees. A first draft kept `goto end` in P5 as
a special case and moved the rest; reading `musicbrainz.c` killed it, because
`end_meta:` is fall-through-reachable from the success path exactly like `end:`,
so any rule separating them is about the label's *name*. There is no label list.

**A second defect in the same section, same cause.** The summary said
`128 distinct strings` above a breakdown totalling **114** — it iterated a
hardcoded tuple of class names, so `genopt`, `goto finalize_ripping` and
`goto end_meta` were counted in the total and named in no line a reader could
see. That is how a class nobody recognised stayed invisible in a document that
presents itself as derived. The tally is now built from what was emitted and the
generator asserts it sums.

**If you classify our messages from P5, re-read it.** 121 rows in P5, 7 in P5a,
128 preserved. Pinned by `contract_fatal_inventory`, revert-proved three ways —
partition removed, tally reverted to the hardcoded tuple, P5a heading removed —
each failing on its own.

**And the first version of that test passed its own revert-proof**, which is the
part worth passing on. It applied the partition rule itself rather than calling
the generator's, so reverting the generator changed nothing it looked at. A test
that reimplements the thing under test asserts only that its own copy agrees with
itself. It now calls `partition_fatal()`, which has exactly two callers.

## 3. What your session retired, stated because none of it had ever run

All from the artifacts, filed at `docs/rig-2026-09-03-978f9b0/`.

- **The abort footer and a diagnosed non-zero exit, together.** Your
  `deps.command_failed` entry: `cyanrip -N -l 1` exited **1** having printed
  `Offset is unset! To continue with an offset of 0, run with -s 0!` at column 0,
  then `Rip completed:  no (aborted, 0 of 14 tracks)`. A diagnosable line before a
  non-zero exit, observed rather than asserted — **and it settles one `P5a`
  `goto end` row by running it**, which is what that class was always going to
  need.
- **`Secure re-read:  did NOT converge after 3 reads (repeat limit hit)`** — the
  non-converged arm, three tracks on each whole-disc rip. Only the converged arm
  had ever been produced.
- **The plural `Read stalls:` rendering**, `5 reads exceeded 10s; longest 11s
  (track 1, LSN 8322)`.

Still untouched by any run: C2 (your drive reports it unsupported), `-f`, damaged
media, CD-TEXT from a disc that has some, and `-x` alone on a drive that goes on
to rip.

**And your cancel scenarios still do not show a cancel** — `cancel me` reads
`Rip completed:  yes (3 of 14 tracks)`, third session running. **But this session
does hold evidence that one happened**, which is a different claim: an exit 3
`No FUN512 checksum found`, which is a rip killed before it writes its own
signature. So the interrupted artifact existed and is not in the bundle. `none`
and `unknown (reason)` again, and this is the second.

## 4. Found in your output

**Nothing.** Written out rather than left silent.

Two things we checked and are *not* filing. The addendum supersedes track 4 only,
while three tracks did not converge — and your own `retried_tracks` says track 4
alone was `replaced: true`, with `unstable_tracks: [3, 5]`, so the addendum
covers exactly what it should. And `DIAGNOSTICS.txt`'s banner names
`+platterpus.10` / `d9c058c` while every rip in the bundle was made by
`+platterpus.11` / `978f9b0`: that is the **approved** pair, not the running one,
and the field is right.

**One receipt worth having.** Your JSON's `artifacts.rip_log.sha256` is
`45097210fc26ac8c…`, and our filed copy of that log hashes to the same value. You
computed it on your machine and we recomputed it on ours; the filing altered no
byte.

## 5. Pre-commit, S-18

**Our next lap is `GO` unless you tell us to hold.** This lap is that `GO`. The
only thing outstanding is §1, which is a fact only you hold.
