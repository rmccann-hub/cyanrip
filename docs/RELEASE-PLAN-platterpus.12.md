# Release plan — `+platterpus.12`, if round 15 closes `GO`

*Written 2026-09-04. **A plan, not a release.** Nothing here is executed.
`meson.build` still says `0.9.4-rc2+platterpus.11`, the ledger's last row is
seq 21, and `tools/release-gate.py --release-gate` exits 1 naming round 15.*

Written now so that when lap 11 arrives the decision is a judgement already
reasoned about rather than one made in a hurry — and so **"we decided not to"
and "nobody got to it" stay distinguishable.**

---

## 0. Where things stand

```
stable pin      978f9b0    0.9.4-rc2+platterpus.11   seq 21, round 14
tip             HEAD       unreleased work on top
round 15        OPEN, our lap 10 GO, their lap 9 OPEN
release gate    --release-gate exits 1, names round 15
```

## 1. The condition, and it is one

**Round 15 closes.** That needs an inbound lap declaring `HANDSHAKE-VERDICT:
GO`, filed here. **Our own transcription is not enough** — the gate refuses with
*"the newest peer lap we hold declares OPEN"* until a peer lap itself says it.
Measured in a dry run, not assumed.

If lap 11 instead reports a defect in `978f9b0`, this plan does not apply: our
§7 pre-commit says we fix it and say so, and the release waits for the fix.

## 2. What a `.12` would actually contain — and the honest part is that a rip is unchanged

| | |
|---|---|
| `src/` files changed since `978f9b0` | **0** |
| source anchor at the pin | `96262d1ea8f282c3` |
| source anchor at `HEAD` | `96262d1ea8f282c3` — **identical** |

**No rip behaves differently.** Every audio byte, every checksum, every log
value a disc produces is what `+platterpus.11` produces. Said plainly because a
version bump normally implies otherwise.

**What a consumer CAN observe changes, and there are two things:**

1. **`PROVIDER-CONTRACT.md` is materially different.** P5 lost 7 rows to `P5a`;
   its preamble now derives its own mechanism table instead of describing five
   of seven from memory; and it publishes `PROJECT_FORK_ID`, the string a
   consumer is told to match on and which we had never printed. **A consumer
   installing from the manifest gets the contract in that commit** — so while
   `release-manifest.json` points at `978f9b0`, the contract a fresh install
   receives still files the secure-re-read verdict as a failure string.
2. **The compiled-in `Handshake:` line**, which lands in every logfile
   permanently and would move from `round 15 lap N OPEN` to the closed state.

## 3. The judgement, stated rather than assumed

**`CLAUDE.md` names this exact shape as the churn case.** `+platterpus.10` was
cut with no `src/` change, only correspondence, and the file records that as *"a
judgement call, and a fourth would be churn."* This would be that fourth.

**The argument for cutting it anyway is (2.1) and not the handshake line.** The
contract is the API. A defect in it that made a consumer file successful rips as
errors is fixed only in the tree, and the manifest is the only install mechanism
we have — tags are `HTTP 403` from here. Leaving `stable` at `978f9b0` ships the
uncorrected contract to anyone who installs tomorrow.

**The argument against** is that Platterpus does not install the contract; they
fetch it from the branch by URL, which is how they came to hold
`…-provider-contract-gc4df1f0.md`. For the one consumer we have, the fix has
already arrived. A release would be for the consumer we do not have yet.

**Recommendation: cut it, on (2.1) alone, and say in the changelog that the
binary is unchanged.** The obligations in `CLAUDE.md` are to *any* consumer, not
to Platterpus — *"Wherever a rule in this file names them, read 'the consumer'"*
— and a second consumer installing from the manifest is exactly who the stale
contract would mislead. **The operator decides; this records the reasoning.**

## 4. The sequence, if it is cut

Order matters and each step depends on the one before.

1. **File lap 11.** Verify the digest and shared hashes re-derive.
2. **Ingest the bundle** with `tools/ingest-bundle.py --into docs/rig-<stamp>-978f9b0`.
   It reads the run verdict first and exits non-zero if the run failed; the
   not-filed list is derived. **Do not describe the session before reading its
   own verdict** — that is what went wrong on 2026-09-03.
3. **Confirm the gate opens:** `tools/release-gate.py --release-gate` exits 0.
4. **Bump** `meson.build` to `0.9.4-rc2+platterpus.12`.
5. **Append one ledger row** — `22 stable 0.9.4-rc2+platterpus.12 <sha> 15`.
   Append only; a mistake is corrected by appending.
6. **Regenerate** `release-manifest.json`, `PROVIDER-CONTRACT.md` and the golden
   reference — commit, **rebuild**, regenerate, in that order.
7. **Name the released commit as the first one where the version and every
   derived artifact agree** — never the bump itself, which is red on
   `contract_build` and the reference check by construction.
8. **Announce the SHA.** There is no tag and cannot be one.

## 5. What this release would NOT verify

Stated because a green suite implies otherwise. Untouched by any run anywhere:
**C2 reporting** (the rig's drive reports it unsupported), **`-f`** offset
autodetection, **damaged media**, **CD-TEXT from a physical disc**, and **`-x`
alone** on a drive that goes on to rip.

And one that is round-16 material rather than a gap here: an adversarial audit
of `FAIL_PATH`'s mechanisms has established that `err = N` terminates neither
the function nor the run, and that **`goto fail` is only *sometimes* a failure
route** — which makes `GOTO_FATAL = ("fail",)` too strong in the same way
`goto end` is. **Not fixed in this release**, because changing it moves rows
between P5 and P5a and would stale the fixture Platterpus regenerated from our
filed artifact.
