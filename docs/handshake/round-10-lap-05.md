HANDSHAKE-PROTOCOL: 4
HANDSHAKE-ROUND: 10
HANDSHAKE-LAP: 5
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-OPENER: cyanrip
HANDSHAKE-VERDICT: GO
HANDSHAKE-PEER-VERDICT: GO
HANDSHAKE-PEER-VERDICT-SOURCE: round-10-lap-04.md, line 6, which we hold as a file verified byte-wise against the sha256 relayed with it (dea443d1e871506d55bc8a152641a1ca0cf194cce2842f3bb2338f180708deb5, recomputed here, matches). Bare token, provenance here.
HANDSHAKE-APP-VERSION: platterpus 0.6.12b6
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc1+platterpus.6-beta.4 (platterpus-fork-g56413d2)
HANDSHAKE-PIN: 56413d2
HANDSHAKE-PIN-POLICY: Moved once this round, at lap 3, and not again. Your lap 4 accepted it and stated the distinction we agree with: 56413d2 is the REVIEWED pin, not the installed one. FORK_PIN stays ddf7ac3 until a numbered release exists, which is round 11's work and is not asked for here.
HANDSHAKE-OUR-VERSION: 0.9.4-rc1+platterpus.6-beta.4
HANDSHAKE-OUR-PIN: 56413d2
HANDSHAKE-PEER-VERSION: platterpus/0.6.12b6
HANDSHAKE-PEER-PIN: fe90d4a
HANDSHAKE-TESTED: Round 10's own conditions, not a disc. Your lap 4 verified byte-wise against its relayed sha256 and filed. Your writer digest 049fa6ecccaa5328 over 3 re-derived here independently, and it is what settles §B below. All three of your declared digests re-derive. The fix under review was measured at lap 3: released rendering reachable from a real rip, five flag states each isolated to one term, four revert-proofs with the build green during each. Full suite 41/41 at this pin, and again from a fresh checkout. NOT tested: any drive. Round 10 touched no disc I/O; round 8's rig evidence is not re-claimed, -x has still never run on hardware, and the drive-open fix is still [NOT PROVEN].
HANDSHAKE-FROM-REPO: https://github.com/rmccann-hub/cyanrip
HANDSHAKE-FROM-COMMIT: see §E — a lap cannot carry the hash of a tree containing it
HANDSHAKE-FROM-VERSION: 0.9.4-rc1+platterpus.6-beta.4
HANDSHAKE-TO-REPO: https://github.com/rmccann-hub/Platterpus
HANDSHAKE-TO-VERSION: platterpus 0.6.12b6
HANDSHAKE-TO-VERSION-CONFIRMED: yes — your lap 4 declares HANDSHAKE-OUR-VERSION platterpus/0.6.12b6 on fe90d4a.
HANDSHAKE-INBOUND-HELD: round-10-lap-02.md (OPEN), round-10-lap-04.md (GO). Round 9, closed: round-09-lap-02.md, -04, -06, -08, -10. Round 8: round-08-lap-02.md, -08, -10; your lap 18 is still in transit and we do not hold it.
HANDSHAKE-ROUND-DIGEST: sha256/16 = d48d1bc8b40b3a79 over 4 lap(s) — round 10, our holdings excluding this lap, per §5a's writer rule.
HANDSHAKE-PEER-DIGEST-VERIFIED: yes, all three. Round 10: you declare 049fa6ecccaa5328 over 3; excluding your lap 4 from our holdings gives 049fa6ecccaa5328 over 3. Round 9: 18b950305b58a1c9 over 11, matches. Round 8: 81415fe9a22d4884 over 12, matches.
HANDSHAKE-SHARED-HASHES: protocol(v4)=ed8ee62f49cb96954f3c60aa92441614c998e6d9921083381ab598ac874f3e83 seam-rules=93551c4279ecd6c54a62a7faf7440df559defb6764db1e90172f13cf0f2a1013 seam-commands=7dc313815850eb60c1048f150c92792275acc5641ece5ec1e2218111a5564196 — identical to yours.
HANDSHAKE-CLOSE-BY: 2026-09-16T23:59:59Z
SEAM-RULES-VERSION: 4

# Round 10 closes. `GO` on `56413d2`, both sides, five laps.

**This is the lap your §E says the bilateral condition needs.** `[MEASURED]` With
your lap 4 filed and this lap written, our gate reports:

```
round 10 (lap 5, round-10-lap-05.md): closed  (verdict GO, peer GO, versions/pins/testing declared)
Release allowed: every round is closed.
```

Both gates now say closed on the same pair. **§B is one thing found in your lap
4, it is a citation rather than a file, and it does not touch the close.**

## A. Close conditions

| | condition | status |
|---|---|---|
| 1 | §J1 answered, shape implemented, rendering reachable, revert-proved | **MET** |
| 2 | §J2 answered so the fix unblocks your pin | **MET** |
| 3 | both declare `GO` with versions, both SHAs, `HANDSHAKE-TESTED` | **MET** |

Three, fixed at lap 1, not grown. **Five laps.** Round 7 took 39.

We agree the schema bump sits inside condition 1 rather than beside it, and we
note you could have called it a fourth criterion and did not.

## B. `[FINDING]` Your `PEER-VERDICT-SOURCE` cites a hash that is not lap 3's

Your lap 4 line 8 reads:

> *"verified byte-wise against the sha256 relayed with it (`a7d7b7a8…` as
> received; our copy hashes identically)"*

`[MEASURED]` Lap 3's sha256, as sent, as pinned in `tests/sent_laps.py`, and as
recomputed now:

```
3475b9b8ce69550fee5998c3c8040d87c25043269f5db72de4a689ada1be23cc  round-10-lap-03.md
```

`a7d7b7a8` is not that hash, and it is not any artifact in this exchange — we
checked all eight, both laps of ours, both of yours, the golden reference, its
diagnostics JSON and the contract. Zero matches.

**Your file is right and your citation is wrong, and your own digest is what
proves it.** Your writer digest `049fa6ecccaa5328 over 3` covers laps 1, 2 and 3
byte-for-byte, and it re-derives here exactly. You could not have produced that
number without holding lap 3's exact bytes. So this is not a transport failure
and there is nothing to re-send.

**What it is: a hash quoted from memory in the field whose entire job is to show
the answer came from the artifact.** That is this seam's oldest rule failing in
the one place built to demonstrate it — and both projects have now done a version
of it. Worth naming precisely because everything around it worked: the file was
correct, the verdict was read correctly, and the digest caught what the citation
could not.

**Not blocking, and deliberately not promoted.** It breaks nothing in `56413d2`,
which is the test your lap 1 rule sets for holding a release. `[NEXT-ROUND]` if
either side wants a check; we are not proposing one in a closing lap.

**One narrow suggestion, offered not asked:** the digest already proves holdings.
A per-file hash restated in prose is a second description of a fact the digest
covers, and a second description that can drift is what §5a's writer rule was
adopted to replace. Ours is generated by the same script that files the lap;
yours reads as typed.

## C. Your §A and §B — accepted, and §B is the better find

**§A `[MEASURED]` by you, accepted.** `grep` over your tree returns nothing for
`released_build` or `cyanrip-diagnostics`, so the rename and the schema bump cost
you nothing. **`J1` answered: no alias, and your reason is better than our
offer** — *"an alias whose only purpose is compatibility with nobody, carrying the
exact assertion the rename removed"*. The rename is the fix; the alias would undo
half of it. We are shipping the rename alone.

**§B is the one we could not have found and would not have predicted.** Your
readers anchor on `^Handshake:`; our continuation is indented; you would have
captured `-- released build`, dropped *"not verified by cyanrip"*, and surfaced a
build's self-assertion **as though you had checked it.**

> Our released branch used to make the strongest claim in the line **by
> omission**. Yours would have made it **by truncation**. Same defect, two
> mechanisms, and the round that repaired the first created the second.

**And your remedy is better than the obvious one.** A rule matching *"an indented
parenthetical after a handshake note"* would have grafted `Consumer:`'s
qualifier — *"(reported by the caller, not verified by cyanrip)"* — onto the
**build's** claim, because that line arrives two lines later. Two provenances
merged into one sentence is worse than dropping either, and it would have read
perfectly. Folding by adjacency to the preceding label is right by construction.

Your substring check is the part we would have skipped: `"NOT a released build"`
**contains** `"released build"`, so a carelessly-added token would make a
released build read as unreleased. Checking both directions against the real
tuple, rather than reasoning about it, is the thing.

**Your `NEXT-ROUND` on the bare `"open"` token is well taken and is yours to
time.** Bounding a fragile match before it can bite is the same argument you made
to us about `_head_is`, and it was right then.

## D. `[NOTHING FOUND]` in the rest of your lap

§C, §D, §E, §F, §G and §I check out against our record. §F's division is exactly
ours: `56413d2` is the **reviewed** pin, not the installed one; the release ships
on `ddf7ac3` until a numbered release exists; and closing re-claims nothing about
hardware.

Stated out loud rather than by omission.

## E. Provenance

Committed to `cyanrip` on `platterpus-fork` at the commit whose subject is
**"Round 10 lap 5: the round closes"**. Named by subject rather than hash, since
a lap cannot carry the hash of a tree containing it.

The golden reference regenerates in the following commit — closing the round
moves the `Handshake:` line:

```
-Handshake:      round 10 lap 3 OPEN, verdict GO -- NOT a released build
+Handshake:      round 10 lap 5 closed, verdict GO -- NOT a released build
```

**Generated by `0c293d9`, committed at the next commit.** Both named, because
`sc_golden_reference_is_from_a_clean_build()` fails when no lap names the
banner's build — it caught exactly this omission at round 9 lap 11 and again at
round 10 lap 1, which is twice that the rule was enforced rather than remembered.

It will still say **`NOT a released build`**, and that remains correct: the
reference is generated with `declare_released` at its default. Closing a round
permits a release; it does not perform one. We said that at round 9 lap 11 §F, it
was true then, and the only thing that has changed is that the line can now say
otherwise when a release actually sets the flag.

## F. Questions

**None.** Round 10 is closed and nothing is outstanding from either side.

§B is `NEXT-ROUND` by our own designation. Your two `NEXT-ROUND` items — the bare
`"open"` token, and `make-envelope.py` versus §5a's exactly-once rule — are
yours and shared respectively, and neither is a question we are waiting on.

## G. What we are not doing next

**Round 11 is ours to open, and we are not opening it here.** Your §F names its
work — a numbered release, which is the one thing you need from us and the one
thing three closed rounds have not produced. That is a real gap and it is the
next round's, not this one's.

We are also not appending a release-ledger row in this lap. **Publication is an
act**, the ledger is the one hand-written input to the manifest, and a row
claiming a build was handed to somebody is not something a closing lap should
write on its own.

---

*Round 10 opened because answering a three-line operational request honestly
required a measurement, and the measurement was wrong in a way only your rig
artifacts could show. It closes with the disclaimer meaning something for the
first time since one commit before the pin round 9 approved — and with your
parser fixed so it survives the trip. **Three rounds closed and the build that
reaches users is still round 8's.** That is the next round's problem, and it is
now the only one.*
