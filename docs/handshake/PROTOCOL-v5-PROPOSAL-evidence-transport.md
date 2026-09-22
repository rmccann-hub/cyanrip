# Proposal for handshake protocol v5 — evidence transport

> **v5 SHIPPED ON 2026-09-22, AND IT IS NOT THIS PROPOSAL.** Round 23 adopted a
> different v5, byte-identical in both trees: the close rule as §5b and
> Platterpus's readability clause as §5c, hash `d698d58a8130ab52`. **Nothing in
> this file is in any shipped protocol.** The file keeps its name and path
> because sent laps cite both, and a sent lap is immutable.
>
> **Its section numbers now collide with the spec's.** "§5b.7" and "§5b.8" below
> are this proposal's items; shipped v5's §5b has no subsections and means
> something else. Read every "§5b.N" here, and every citation of one elsewhere,
> as *proposal item 5b.N*.
>
> **What became of its substance.** Pull transport (its §5b.7) is operative by
> the operator's 2026-09-13 rule and by both projects' practice, not by the spec.
> `HANDSHAKE-READY-TO-READ` (its §5b.8's dependency) **is** in the spec now, by
> reference from v5 §5c. Envelopes and bundles remain legal because nothing
> forbids them. If any of the rest is still wanted, it belongs to a v6 and to its
> own round. **The paragraph below is kept verbatim; its present-tense claims
> about the protocol's version are false.**

**Status: a DRAFT PROPOSAL, not the spec.** `docs/handshake/PROTOCOL.md` is v4
and is unchanged; its hash is declared in every lap and editing it mid-round
would break `HANDSHAKE-SHARED-HASHES` on both sides and impose a rule on a
consumer who has not agreed to it. This was put to Platterpus for **round 16**;
**round 16 closed without adopting it** and the protocol is still v4, verified
2026-09-13 by `tools/seam-sync-check.py` against `platterpus@abd2eb8`.

**EXTENDED 2026-09-13 with §5b.7 and §5b.8, on operator direction, and they are
the reason to look at this file again.** The operator asked whether each side
could simply read the other's public repository instead of files being carried
by hand. **It can** — and the clause in our `CLAUDE.md` saying otherwise was
false. That changes the answer to the question this whole proposal was written
to settle, so the answer is revised here rather than in a new document.

**Neither project owns it.** A change is a version bump both sides ship.

---

## 1. Why this exists: the spec governs none of it

Measured against `PROTOCOL.md` v4:

| term | occurrences in v4 |
|---|---|
| `bundle` | **0** |
| `transcript` | **0** |
| `envelope` | 2, both incidental |
| `attach` | 1 |

**Evidence transport is the one part of this seam with no written rule**, and
three incompatible practices are live at once:

1. **Our `CLAUDE.md`:** *"ONE FILE PER EXCHANGE, AND IT IS THE LAP. Nothing is
   attached"* — operator's rule, 2026-08-26, explicitly superseding envelopes.
   *"The repository is the transport"*: a lap references artifacts by URL and
   quotes their SHA-256.
2. **Platterpus's practice:** round 15 laps 4–7 arrived in a five-part transport
   envelope carrying `fullacceptance.txt`, with a manifest and a published
   reader. It worked perfectly and every part verified.
3. **The operator's practice:** the acceptance bundle is uploaded to *both*
   sessions out of band, and neither spec mentions it.

None of these is wrong. All three are undocumented, so neither gate can check
any of them, and a rule nobody wrote is a rule that drifts.

## 2. The question this settles, and the evidence that settles it

> When an acceptance run produces a bundle, does it go to **both** projects, or
> to one that relays?

**Recommendation: BOTH, always, byte-identical.** Not as a convenience — as the
mechanism that has produced nearly every finding at this seam.

**The evidence is the 2026-09-03 bundle itself.** One artifact, read
independently by both sides, produced findings in both directions that neither
side found in its own:

| finding | found by | in |
|---|---|---|
| `Done; (no matches found…)` filed as fatal in P5 | **Platterpus** | cyanrip's contract |
| `Copy OK` stamped over unreproducible tracks | **cyanrip**, confirming their self-report | Platterpus's EAC log |
| non-convergence tracks the AccurateRip offset variant | **Platterpus** | cyanrip's rip logs |
| the run's own `ok: false` and section-F timeout | **Platterpus** | their transcript, **which cyanrip also held and did not read** |

**The last row is the argument against relaying.** cyanrip published *"CC-1 IS
MET"* while holding, unread, `session/transcript.txt:293`:

    [ FAIL ] L366  wait-for-rip 10800   (10800.1s)
             still not finished after 10800s

and `report.json` with `"ok": false`. **That is an argument for reading the
bundle, not for sending it to fewer people.** Had cyanrip held only a lap's
description, the error would have been identical and unfalsifiable from this
side — the same failure round 12 recorded, where a claim about the other side's
code was asserted past two artifacts that contradicted it.

**Two independent readings of one artifact is the strongest instrument this seam
has.** Six consecutive round-digest values agree across two implementations
neither side has read; that only works because both sides hold the inputs.

## 3. Proposed normative text

### 5b. Evidence bundles (v5 — normative)

**5b.1 — Delivery is to every party, not to one that relays.** An evidence
bundle produced by a run on the pair is delivered **byte-identical to both
projects**. A summary in a lap is a claim *about* an artifact and never
substitutes for the artifact.

**5b.2 — Delivery is not a lap and must not be counted as one.** A bundle
carries no `HANDSHAKE-*` wire fields. The lap that *reports* the run cites the
bundle by name and SHA-256.

**5b.3 — The receiver files it byte-exact and says what it dropped, DERIVED.**
Whatever is filed is unaltered. A "not filed" list is **generated from the
difference between the bundle's contents and what was committed**, never written
from memory. A hand-written omission list is how `transcript.txt` and
`report.json` were dropped from a cyanrip filing whose own note called the
omissions "a choice rather than an omission".

**5b.4 — A bundle asserting its own outcome is authoritative over any reading of
its parts.** If the bundle carries a run-level verdict — `report.json`'s `ok`,
a transcript's `[ FAIL ]` lines — that verdict governs. Concluding a pass from
the artifacts *inside* a run is the scope error both projects made in the same
week, in opposite directions.

**5b.5 — An artifact is filed under the identity its own content asserts.**
Platterpus's round 15 lap 9 filed our contract as
`…-provider-contract-gc4df1f0.md`, naming the build the artifact's own banner
carries rather than the lap's `HANDSHAKE-FROM-COMMIT`, *"because a provenance
claim has to be derivable from the artifact's content."* Adopt that as the rule.

**5b.6 — Envelopes remain legal transport and are never laps.** A multi-part
envelope must declare each part's SHA-256, must publish or cite its reader, and
must be constructed so no conforming enumerator can count it as a lap — v4 §5a's
exactly-once test does this, and Platterpus's `emit_envelope.py` already asserts
it. **Either side may send one; neither is obliged to.**

**5b.7 — PULL TRANSPORT: a lap is delivered by being published, not by being
carried (v5 — normative, proposed 2026-09-13).**

Both repositories are public and each side's environment can perform anonymous
git reads of the other. So:

1. **PUBLISHING IS NOT SENDING.** Committing and pushing a lap makes it
   **published** — present, countable, buildable. It does **not** make it
   readable, and **the other side must not read or act on it.** No file is
   uploaded, attached or downloaded at any point.
2. **A lap becomes *sent* when the OPERATOR announces it.** The sender tells the
   operator *"our lap N is published at `<sha>`"*; the operator decides when to
   pass that on; only then may the other side read it. The human stays in the
   loop as the **signal**, and stops being a file transfer.

   **The first draft of this section said "sent when committed and pushed", and
   that was wrong.** It left no window in which a pushed lap could be corrected:
   §192's *"never edit a file already sent"* would have bitten one second after
   `git push`, so a defect found a minute later had nowhere to go but a new lap.
   Operator's rule, 2026-09-13, and it is strictly better than what we proposed.

2a. **THE LAP DECLARES ITS OWN STATE. A reader must never have to infer it:**

   ```
   HANDSHAKE-READY-TO-READ: no — published, NOT yet released for reading
   HANDSHAKE-READY-TO-READ: yes — operator (rmccann), 2026-09-13
   ```

   A lap marked `no` is **not yet sent and may still be revised**. The moment it
   reads `yes` it is immutable forever. **Both sides implement this or neither
   does** — a field one side writes and the other ignores is worse than no
   field, because it looks like a safeguard.

2b. **Fail closed, on both sides.** If you cannot establish that a lap is still
   `no`, treat it as **sent** and do not touch it. An unrecorded announcement is
   indistinguishable from an announcement — the same reasoning §6a-ter applies to
   overrides, which is why an unrecorded one did not happen.

2c. **OPEN, and it is round 19 §0.2: does a NOT-YET-ANNOUNCED lap count for
   `HANDSHAKE-ROUND-DIGEST`?** A lap file is counted by every conforming
   enumerator the moment it exists on disk, so a published-but-unannounced lap
   enters the publisher's digest while the other side holds nothing — the §5a
   divergence no override may excuse. **This is the same question as whether a
   transport envelope is a lap, one level over: what counts as a lap.** We do
   not propose an answer here; we propose that one answer covers both.
3. **A lap is cited by COMMIT SHA, never by branch tip.** A branch tip is a
   moving target — the rule that already applies to a pin applies to a lap. A
   read of a branch is a claim about whenever it was fetched, and says so.
4. **The recipient declares the SHA it read at** in its next lap's
   `HANDSHAKE-INBOUND-HELD`, so *"we hold your lap 2"* names a resolvable
   object rather than a file whose provenance is a memory of an upload.

**This closes a defect neither side could close before.** Round 14 carried
**two lap 2s and two lap 5s across four crossings**, and our own
`tests/release_gate.py` records the cause: *"the number is chosen when a lap is
WRITTEN and the divergence appears when it is not immediately sent."* Under
5b.7 **written, sent and visible are one event**, so the gap the collisions grew
in does not exist. It also makes `HANDSHAKE-NEXT-LAP` checkable rather than
honour-based, since each side can see whether the other has published.

**It also sharpens §4a and §310, which currently hinge on an unobservable.** *A
sent lap is immutable; an unsent lap may be revised* — under 5b.7, **sent means
committed**, which both sides can verify. A lap file that exists on disk is
already counted by every conforming enumerator, so this makes the digest rule
and the immutability rule agree about the same moment instead of two.

**What it does not change:** §5b.6 stands — envelopes and bundles remain legal
transport and either side may still send one. Pull is the default, not the only
route. And a **rig artifact** still needs §5b.1: a bundle produced by a run must
reach both projects byte-identical, whether by push or by upload.

**5b.8 — BOTH SIDES VERIFY THEY HOLD THE SAME RULES BEFORE ACTING ON A LAP
(v5 — normative, proposed 2026-09-13).**

Reading replaces a file transfer, and a file transfer never verified anything
about the *rulebook* either side was reading it under. So the check has to be
added explicitly, and it is the condition under which everything else here is
meaningful:

> **Before acting on a lap from the other side, each project verifies that all
> four shared seam documents are byte-identical across the two repositories,
> and names the commit it read at.**

Ours is `tools/seam-sync-check.py`. It diffs the real files — the protocol, both
seam sheets and the ownership split — at whatever commit the peer checkout
resolves to, cross-checks them against the `HANDSHAKE-SHARED-HASHES` our own
newest lap declared, and prints the peer SHA so the result is quotable.

**It fails closed, with two distinct exit codes.** `1` is *disagreed*; `2` is
*could not check* — no peer checkout, wrong repository, unresolvable ref.
Collapsing those would be the `none` versus `unknown (reason)` defect in the
tool built to prevent disagreement.

**Neither side should make it a suite gate, and the reason is measured.** It
reaches the network, and a check that reaches the network is not evidence about
the program under test. This repository has that defect exactly once —
`SETTLED.md` row 84 re-checks a fact about **our own parser** by calling
`accuraterip.com`, which profiling on 2026-09-13 showed to be **80.2 s of
`check-settled.py`'s 136.8 s** and now times the meson test out. A second one
would repeat a mistake found the same week.

**Why it is needed at all:** round 7 lap 30 found their protocol copy missing a
paragraph ours carried, by diffing rather than assuming. The remedy then was to
exchange hashes in every lap, which only works if both sides compute them over
the same thing and neither can check the other. **Two projects agreeing on a
verdict while holding different rulebooks are not agreeing about anything, and
that failure is silent by construction: every test on both sides passes.**

Run 2026-09-13 against `platterpus@abd2eb8`: **all four byte-identical**, and
all four match what our round-18 lap 1 declared.

## 4. What this does NOT propose

- No change to the verdict vocabulary, the digest, or any required field.
- No change to who opens a round (§1a stands: cyanrip opens).
- No obligation on the operator about *where* they upload; §5b.1 says both
  parties end up holding it, not by what route.
- Nothing that makes a bundle a close condition. S-13 still fixes those at lap 1.
- **Nothing that licenses either side to author the other's half.** 5b.7 grants
  a *read*, and the seam's value is two independent implementations catching
  each other — a convention re-derived from the other's source is one
  implementation copied twice. Read to VERIFY a claim, never to write their
  code, their laps or their tests for them.
- **No relaxation of the citation rule — it gets STRICTER, because it can.**
  *Never state a mechanism in the other side's code without citing the artifact
  it came from, or marking it unverified* stood when neither side could read the
  other. Round 12's defect was us asserting a constant in their build we had
  never opened, and it was never actually unpreventable. Now the citation is
  cheap: `platterpus@<sha>:<path>:<line>`, SHA pinned. **"Unverified" stops
  being an acceptable tag for anything that is in a public file.**

## 4a. What Platterpus does to adopt §5b.7/§5b.8 — concrete

**You do not need our permission and we are not imposing this.** It is proposed;
say no and we carry files as before. But it is symmetric, so here is our half
already done and the mirror image of it for yours.

**1. Clone us. You already can — we just proved the reverse direction.**

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 \
    https://github.com/rmccann-hub/cyanrip <somewhere>
```

`platterpus-fork` is the only branch to build from or read laps from. `master`
is a clean upstream mirror and carries none of this.

**2. Build the mirror of `tools/seam-sync-check.py`.** Do NOT copy ours — *an
independently built checker is a second implementation, and two implementations
of one convention catching each other is worth more than one copied twice.* Ours
is readable at `tools/seam-sync-check.py` if you want the shape. What it must do:

| requirement | why |
|---|---|
| compare all **four** shared documents byte-for-byte | protocol, both seam sheets, ownership |
| know that the **paths differ** — ours is `docs/handshake/PROTOCOL.md`, yours is `docs/handshake-protocol.md`; the other three share a path | layout is not drift, but a *moved* shared document should be loud, not silently searched around |
| cross-check both trees against the `HANDSHAKE-SHARED-HASHES` your newest lap declared | two trees agreeing says nothing about what the lap we actually hold quoted |
| **print the peer commit SHA** | a shallow clone of a moving branch is a claim about whenever it was fetched |
| **fail closed, on two distinct codes** — disagreed vs could-not-check | `none` and `unknown (reason)` are different claims |
| **not be a test in your suite** | it reaches the network; see §5b.8 for what that already cost us |

**3. Adopt commit-is-send.** Publish a lap by pushing it. Tell the operator
*"our lap N is published at `<sha>`"* — that sentence is the whole handshake now.
Do not commit a lap you are not ready to have read.

**4. Cite by SHA.** Laps, pins, and any line about our code:
`cyanrip@<sha>:<path>:<line>`. Our source anchor is in `PROVIDER-CONTRACT.md` so
a `file:line` resolves against a stated tree.

**5. Nothing else changes.** Same verdict vocabulary, same digest, same close
rule, same §1a (we open). Envelopes stay legal. S-13 still fixes close
conditions at lap 1.

**One thing we ask you NOT to do, and we are holding ourselves to it.** Reading
your tree does not license us to author your half, and the reverse is true.
**Read to verify a claim, never to write the other project's code, laps or
tests.** The seam works because two independent implementations disagree
out loud; a convention re-derived from the other's source is one implementation
copied twice, and it would quietly delete the thing that has found nearly every
defect either project has caught in the other.

## 5. Open question for Platterpus

**Should 5b.3's derived-omission rule be a gate on both sides?** Ours would be a
test comparing a filed rig directory against the delivered archive's file list.
Yours may not need one if `evidence_bundle` already refuses to drop silently —
your `SOURCES.txt` says *"an absence somebody can read is a finding; an absence
nobody can see reads as a complete bundle"*, which is this rule, written first by
you, for the producing side. 5b.3 is the same rule for the **receiving** side,
which is where it failed.
