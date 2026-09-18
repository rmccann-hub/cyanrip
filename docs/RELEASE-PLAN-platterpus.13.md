# Release plan — `+platterpus.13`, once round 21 closes `GO`/`GO`

*Written 2026-09-18. **A plan, not a release.** Nothing here is executed.
`meson.build` says `0.9.4-rc2+platterpus.12`, the ledger's last row is seq 22,
and `tools/release-gate.py --release-gate` exits 1 naming round 21.*

**`CLAUDE.md` recorded for forty days that a plan existed for the next release
and pointed at `docs/RELEASE-PLAN-platterpus.5.md`, which had already shipped.**
It now says plainly that the next release is `+platterpus.13` and nothing is
written for it. This is that file, written before the close rather than during
it, so that *"we decided not to"* and *"nobody got to it"* stay
distinguishable.

**Bannered on the day it is executed, not when somebody notices.** The `.12`
banner is dated one day after its release commit; the `.5` one was forty days
late, and in between this repository pointed a reader at it as current.

---

## 0. Where things stand

| | |
|---|---|
| `meson.build` | `0.9.4-rc2+platterpus.12` |
| ledger | last row seq **22**, `stable`, `fe4d2c4`, round 17 |
| `release-manifest.json` | both channels resolve `fe4d2c4` at seq 22 |
| gate | exits **1** — round 21 not closed |
| round 21 | OPEN. Our lap 5 declares `GO` and is held; their lap 4 declares `GO` and is unreleased |

## 1. The condition, and it is a condition rather than a round number

> **`tools/release-gate.py --release-gate` exits 0.**

That is the whole of it, and it is deliberately not *"round 21 closes"*. The
`.12` plan was written to wait for round 15 and was authorised by **round 17**,
because round 15 closed before anyone actioned it. A plan that names a round
number is a plan that can be satisfied and still not executed, or executed
under a different authority than it names. **The gate is the condition** — it
reads declared verdicts from the record, refuses on anything it does not
recognise, and fails closed.

Today it exits 1 and names `round-21-lap-05.md`, with the reason spelled out:
*"NOT RELEASED FOR READING — HANDSHAKE-READY-TO-READ is not `yes`, so this lap
is published but not announced and its verdict is a draft."* **Two things flip
it, in this order and neither optional:**

1. **The operator releases Platterpus's lap 4.** We then file it under
   `docs/handshake/inbound/round-21-lap-04.md` byte-exact **against the hash
   that arrives with their release announcement**, and flip our
   `HANDSHAKE-PEER-VERDICT` from `OPEN` to `GO` with their released lap 4 as its
   source.

   **This step first said "against the sha256 our lap 5 already declares", and
   that would have failed.** `989427bd4ddacc0d…` is a correct reading of their
   commit `27a174dc` and still reproduces there. It is not a description of
   their lap 4: that file declares itself `READY-TO-READ: no`, and by their tip
   `0f1b54a4` it is **47,478 bytes** against the 31,732 we read. **A SHA-pinned
   read is durable; a hash of a held document is a claim about a moment.** Our gate's `stale_peer_verdict` cross-checks that transcription
   against the newest lap in `inbound/`, so the filing is not optional
   bookkeeping — it is what makes the cell legal.
2. **The operator releases our lap 5.** `HANDSHAKE-READY-TO-READ` flips to
   `yes`, `HANDSHAKE-FROM-COMMIT` is finalised to the commit before the release
   commit, and `STATUS-NEWEST-LAP-STATE` in the standing status changes from
   `held` to `sent` — three cells, and a check on our side compares the last
   against the gate's own reading.

**Neither is a judgement and both are the operator's act.** Publishing is not
sending; that is why there is a step here nothing in this tree can perform.

## 2. What a `.13` would contain — and unlike `.12`, a rip DOES change

The `.12` plan's honest paragraph was that a rip came out unchanged. **This one
is different, and both changes are ones a consumer parses.**

| change | surface | agreed in |
|---|---|---|
| `Frame retries:  N` → `Retry limit:    N (per frame, and per whole-track re-read)` | **P2 contract line** | round 20 lap 2 §0.2, announced in round 21 lap 1 |
| `cyanrip_log_finish_report()` below the encoder-status loop, so `Ripping errors:` counts encoder failures | **P2 contract line's meaning** | round 20 §5.4, confirmed as parsed in their lap 2 §F |
| `-j` key `frame_retries` → `retry_limit`, record schema → `cyanrip-diagnostics/6` | machine record | same |
| `-j` gains a `cache_probe` block — calibration reads, threshold, ratio, one entry per run | machine record, additive | round 21 §4a |

**The second one is the reason this release matters rather than tidies.** Under
a 32 KiB write cap the old placement wrote `Ripping errors: 0` and
`Rip completed:  yes` over a 253,742-byte file truncated to 32,768, while `-j`
said `2` and the process exited `1`. **Two records of one run, disagreeing, and
the human-readable one wrong** — and the log is the archival record, the one
that outlives the exit code.

**What it would NOT contain**, because the round is reviewing `3952c03` and
`git diff --stat 3952c03 HEAD -- src/` is empty: nothing else. The three fixes
that landed after the test pin are in `tests/` and `tools/` only. A consumer
sees exactly the four rows above.

## 3. The judgement — cut it, and the reason is the encoder-failure arm

**Recommend cutting `.13` as `stable` once the gate allows it**, for one reason
that is not "the round closed":

`+platterpus.12` is what `release-manifest.json` resolves today, and it is the
build that **stamps `No errors occurred` onto an archival artifact for a rip
that lost data.** That is not a latent defect — Platterpus's `_take_rip_errors`
turns our `0` into that exact string, and their EAC-compatible export writes it.
Every day `fe4d2c4` stays the stable pin is a day a truncated rip can be filed
as clean.

**The counter-argument, stated rather than skipped:** the failure needs a write
error, and a rig with free disk does not produce one. It is rare. **It is also
silent, unrecoverable and in the one artifact a consumer cannot re-derive** —
which is the trade this project resolves the same way every time.

**Channel: `stable`, not `beta`.** A `beta` row would resolve for `stable` users
too under the manifest's own rule that a channel is a risk tolerance and not a
lineage, and there is nothing experimental here: both changes were agreed a
round before they shipped and both are now exercised on hardware.

## 4. The sequence, if it is cut

Each step depends on the one before. **The ordering is the point** — skipping
one is how a release ships a claim nobody checked.

1. **The gate exits 0.** §1. Nothing below starts before this.
2. **Bump** `meson.build` to `0.9.4-rc2+platterpus.13`. **Upstream's
   `0.9.4-rc2` is copied verbatim**; `+platterpus.N` is the only number that
   moves, and it cannot collide with anything upstream can mint.
3. **Append one row** to `docs/release-ledger.tsv`: `23  stable
   0.9.4-rc2+platterpus.13  <sha>  21`. Append only — a mistake is corrected by
   appending, exactly like a lap. It is the one hand-written input, because
   **publication is an act** and no amount of reading this tree reveals that a
   build was handed to somebody.
4. **Regenerate, never hand-edit**: `tools/gen-provider-contract.py >
   PROVIDER-CONTRACT.md`, then the golden reference and the interrupted sample.
   `--check` must exit 0 on the contract and the manifest.
   `tools/gen-release-manifest.py > release-manifest.json`.
5. **Commit the code, then commit the regenerated artifacts as their own
   commit.** Never `--amend`: the artifact's banner names the pre-amend commit,
   which amending leaves reachable only from the reflog, so a fresh clone cannot
   resolve it and routine `git gc` destroys it. Say *"generated by X, committed
   at Y"*.
6. **Announce the release at the FIRST COMMIT WHERE THE VERSION AND EVERY
   DERIVED ARTIFACT AGREE** — not at the bump. The bump commit necessarily fails
   its own suite: the version moves and the artifacts still describe the
   previous one, so `contract_build` and the golden-reference version check both
   fire, which is exactly what they are for. **`+platterpus.5` was announced at
   `422d12a`, which fails 2 of 33 from a fresh clone, and the consumer installed
   it on our say-so.**
7. **Changelog entry** by version, linking `docs/upstream/` rather than growing
   a second voice.
8. **Banner this file the same day**, with the commit, the ledger row and the
   round that authorised it.

**No tag.** Tag push is `HTTP 403` from this environment and
`git ls-remote --tags origin` returns nothing, so no release of this fork has
ever been reachable by tag. **The commit SHA is the only durable release
identifier a consumer can resolve**, which is why the manifest and the
handshake both pin a SHA and say the tag is local-only.

## 5. What this release would NOT verify, so a green suite cannot imply coverage

Stated because 87 green tests and one clean 14-track rip are both easy to
over-read.

- **The encoder-failure arm has never run on hardware.** It is proved by
  `sc_encode_failure_reaches_the_log()` under an artificial 32 KiB write cap.
  The rig rip that authorises this release had `Ripping errors: 0`, so **it
  cannot distinguish the fixed build from the broken one** — with zero encoder
  failures the two placements emit byte-identical output. The fix is right and
  the hardware evidence is about everything else.
- **`Retry limit:` is read by no Platterpus field.** It is in their
  `_IGNORED_DISC_LINES` by design. What is established is that it does not trip
  their completeness sweep.
- **C2 stays `UNREACHABLE`** — the rig's BDR-209D reports it unsupported. Not
  *not yet done*; a different drive or never.
- **`-f`, damaged media, and CD-TEXT from a physical disc** are all *not yet
  done*, which is a different claim.
- **`-x`'s calibration series is still unrecorded**, so the cache figure stays
  wrong by roughly fifteen times against `cd-paranoia -A` and
  `docs/ROUND-22-PLAN.md` §2 stays gated. **Do not cite our cache figure.**
- **The approved pair after this release is `(the new SHA, 0.6.50)`**, and no
  run will have exercised it: the session ran `(3952c03, 0.6.50)` and `3952c03`
  is the test pin, not the release. That is the same gap `.12` shipped with and
  it is worth naming rather than discovering.
