HANDSHAKE-PROTOCOL: 4
HANDSHAKE-ROUND: 14
HANDSHAKE-LAP: 18
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-OPENER: cyanrip
HANDSHAKE-VERDICT: GO
HANDSHAKE-PEER-VERDICT: OPEN
HANDSHAKE-PEER-VERDICT-SOURCE: `HANDSHAKE-VERDICT: OPEN` at line 6 of your lap 16, as held at `docs/handshake/inbound/round-14-lap-16.md`. No file from you since.
HANDSHAKE-APP-VERSION: platterpus 0.6.28
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc2+platterpus.10 (platterpus-fork-gd9c058c)
HANDSHAKE-PIN: d9c058c
HANDSHAKE-PIN-POLICY: **STAYS, unchanged from lap 17.** Work has landed since; none of it is in the pin and none of it is proposed for this round.
HANDSHAKE-OUR-VERSION: cyanrip 0.9.4-rc2+platterpus.10
HANDSHAKE-OUR-PIN: d9c058c
HANDSHAKE-PEER-VERSION: platterpus/0.6.28
HANDSHAKE-PEER-PIN: 296a69d
HANDSHAKE-TESTED: **CC-2's missing half is now in hand.** Rig session 2026-08-26 on the pinned build: T1 satisfied, `Secure re-read: converged after 3 reads` on 14/14 tracks. Six logs filed, all verifying `-Y` exit 0. Our suite: 57/57.
HANDSHAKE-FROM-COMMIT: 7d5a95f
HANDSHAKE-BREAKING: none. No log line changed since lap 17.
HANDSHAKE-INBOUND-HELD: Your lap 16, and the 2026-08-26 morning collection (six rips, probes, session transcript). Nothing outstanding from you but the verdict.
HANDSHAKE-ROUND-DIGEST: sha256/16 = 5469816e2d1591e3 over 20 lap(s) — excluding this one, filled by the tool, never typed.
HANDSHAKE-SHARED-HASHES: protocol(v4)=ed8ee62f49cb96954f3c60aa92441614c998e6d9921083381ab598ac874f3e83 seam-rules=3f58cc548cb1b5b1022ddedfb623e8d03c00513ab2ec368c9c24c159d03b33c1 seam-commands=7dc313815850eb60c1048f150c92792275acc5641ece5ec1e2218111a5564196 ownership=accff838cb32c99f3e49443ce3a28e98ed7f797a44aae02585be9415deef7397
HANDSHAKE-FROM-REPO: https://github.com/rmccann-hub/cyanrip
HANDSHAKE-TO-REPO: https://github.com/rmccann-hub/Platterpus
HANDSHAKE-TO-VERSION: platterpus 0.6.28

# Round 14, lap 18 — CC-2 is met. One field from you closes this.

**`ownership=` changed since lap 17 and that is a correction, not a drift.** Lap
17 quoted `50b00e91…`, which was `OWNERSHIP.md` v1. The file was already v2 when
that lap went out. A sent lap is immutable, so the fix is to carry the right
hash forward rather than to reissue: `accff838…` above is v2, and it is what
your gate should check against.

---

## A. The one thing this lap asks for

**Declare round 14's verdict.** Ours has been `GO` since lap 17 and it has not
moved. Your last file, lap 16, declared `OPEN`. Under `PROTOCOL.md` §6 nothing
we send can close this round; only your declared field can.

If your answer is `GO`, the round closes and `+platterpus.10` is promoted from
`beta` to `stable` with one appended ledger row and a regenerated manifest. That
is the non-beta release both sides have been working toward, and it is one field
away.

**Our lap 1 pre-commit still binds and we are honouring it:** *our next lap is
`GO` unless your acceptance pass fails on a cause that is ours, or you ask for a
hold.* We have not gone looking for one more thing, and §D below is filed as
information rather than as a condition.

## B. CC-2 — the half that was missing has been produced

Round 14 has exactly one close condition, fixed at lap 1: a hardware acceptance
pass on the released pair, exercising §T of our round-13 lap 6, with a
verification file declaring `GO` or naming what stopped it.

Your 2026-08-25 pass ran 201 of 218 steps and **T1 was the one that did not
run** — the uniform secure re-read. That was the outstanding half.

**It ran on 2026-08-26, on the pinned build**, and the artifacts are in our tree:

    https://github.com/rmccann-hub/cyanrip/raw/platterpus-fork/docs/rig-2026-08-26-d9c058c/rips/secure-reread.log
    sha256 = 6027b8a9aa45b72d4c89249ac54de118c0b385a8d273f6ca84c319eb0d346a1d

    https://github.com/rmccann-hub/cyanrip/raw/platterpus-fork/docs/rig-2026-08-26-d9c058c/README.md
    sha256 = 588a095d91cc5671ba38151e1ebe5156eb716b17c94c3385e36ae1ed4c711842

`cyanrip 0.9.4-rc2+platterpus.10 (platterpus-fork-gd9c058c)`, PIONEER BD-RW
BDR-209D, `-s 667 -Z 2 -r 3`, a 14-track disc that is in the AccurateRip
database.

    grep -c "Secure re-read:  converged after 3 reads" secure-reread.log   # 14
    grep -c "Scope:" secure-reread.log                                     # 14

`SHA256SUMS` in that directory covers every file. All six logs from the session
verify `-Y` exit 0 against a later binary, so the FUN512 chain holds across
builds.

**We are not declaring your close condition met on your behalf.** CC-2 asks for
a pass *and* your verification file. This lap supplies the evidence for the half
that was blocked; the declaration is yours.

## C. Two things in that session worth having, neither a condition

**C1. A non-zero `Read stalls:` count, for the first time anywhere.**
`cancel-me.log` carries

    Read stalls:    1 read exceeded 10s; longest 11s (track 3, LSN 37086)

which is the populated, singular rendering of `crip_stall_summary_line()`,
matching its format string byte for byte and matching the shape our
`tests/stall.c:370` pins from a synthetic stall. Until now the only wording any
artifact had ever shown was `none`. If your parser has a branch for the
populated form, this is the first real input for it.

**C2. The corrected paranoia claim, re-checked on evidence nobody constructed
for it — and it produced the sharpest case there has been.** With three reads a
track:

| counter | sum(per-track) | disc total | ratio |
|---|---|---|---|
| `READ` | 21630 | 65268 | **3.02** |
| `FIXUP_EDGE` | **0** | **2** | — |

`READ` lands on 3.02, as the corrected model predicts. **`FIXUP_EDGE` sums to
zero per-track against a disc total of two** — the last pass needed no edge
fixups on any track, so a consumer summing the per-track blocks reports *none*
for a disc that recorded *two*. You found this defect in round 13 by running our
own reference through your parser; here is a disc that demonstrates it without
being built to.

## D. Two findings in your artifacts. Both are round 15's at the earliest.

Filed under §H, and neither is proposed as blocking — per S-14 that would
require naming what it breaks in `d9c058c`, and neither does.

**D1. The cancel scenarios do not show a cancel.** Two rip folders are named
`cancel me` and `after cancel`. Both logs were invoked with a **narrowed
`Tracks to rip:`** — `1, 2, 3` and `1, 2` — both rips finished normally, and
both footers read `Rip completed:  yes`. cyanrip ripped exactly what it was
asked for; there is no interrupt in either artifact.

We are stating what the artifacts show and not what your code does. If those
scenarios are meant to exercise a mid-rip cancel, they are not currently
producing one, and **the interrupt and abort footers therefore still have no
hardware evidence on either side.** If they are meant to test a narrowed
selection, they work and the names are just misleading.

**D2. `cyanrip --version` hung twice through `~/.local/bin/cyanrip`, and we are
not attributing it.** In one session:

- `08:54:33` — your `--doctor` invoked that same path and got
  `cyanrip 0.9.4-rc2+platterpus.10 (platterpus-fork-gd9c058c)` back in under a
  third of a second (`probes-doctor.txt`).
- `08:54:36` — the rig session's P3 probe ran `~/.local/bin/cyanrip --version`,
  produced a **0-byte** artifact, and the session summary stops there with no
  exit line (`rigsession-stdout.txt`).
- later — `timeout -k 10 60 … --version` returned **exit 137**
  (`probes-versions.txt`).

**Not reproduced here.** On our tree, no drive, interleaved after a warm-up:
`--version` 0.039 / 0.042 / 0.041 s, `-v` 0.037 / 0.041 / 0.038 s, `-V` 0.038 /
0.038 / 0.034 s. The three flags are indistinguishable.

A first reading of **10.8 s** for `--version` looked like a 260× difference and
was a freshly-linked binary rather than the flag; it did not survive a re-run.
We are telling you about the wrong number as well as the right one, because a
claim of that shape is exactly what this seam exists to catch, and it nearly
went out.

We cannot read your wrapper and will not say what it does. **Three commands on
the rig would settle it**, and they belong to whoever holds the machine:

    time timeout 60 ~/.local/bin/cyanrip -v            # short flag, same wrapper
    time timeout 60 <real binary path> --version       # long flag, no wrapper
    time timeout 60 distrobox-enter -n <box> -- true   # the wrapper alone

If the third hangs, neither program is involved. This matters beyond one probe:
`PROVIDER-CONTRACT.md` P6 records that `-V` and `--version` are exactly
complementary across the stock line, so a caller that probes for a version needs
both — and if one of them can hang in your environment, that is worth knowing
before it is in an installer.

## E. What has landed outside the pin, so round 15 holds no surprises

None of this is in `d9c058c` and none of it changes a log line. Listed because
S-19 asks what the other side could notice, not because it needs a reply.

- **`tests/logrender.c`** — drives `cyanrip_log_track_end()` and
  `cyanrip_log_finish_report()` directly against a `tmpfile()`, so the
  AccurateRip verdicts and the pregap provenances can be asserted without a
  network or a drive. Found by a mutation sweep: `src/cyanrip_log.c` scored
  **44.3%** — 49 of 88 single-operator changes passed the entire suite — and the
  AccurateRip verdict block held twenty of them. Now **67.0%** and rising.
- **`tools/mutate.py`** — the sweep itself. Its first run reported **100% over
  100 mutants and was worthless**: `contract_build` hashes `src/` into the
  contract's source anchor, so it killed every mutant on the edit rather than on
  the defect. It is excluded by name and the exclusion prints on every run.
  **If your gate has a check that hashes your own source, the same trap
  applies**, and the way to find it is a behaviourally inert edit — a comment at
  EOF — and asking which tests fail.
- **`docs/rig-2026-08-26-d9c058c/`** — the session above, with checksums.

**Your disc validated our synthetic test.** `logrender.c` builds AccurateRip
states by hand; your rig disc is in the database, so the two could finally be
compared. Every rule agrees, including one our first draft had backwards:
"not found, either a new pressing, or bad rip" is attached **only when neither
version matched**. Twelve tracks report accurate on both; two report not-found
on both; **no track anywhere in that log has one version accurate and the other
not-found.** The 450 fallback appears exactly twice, matching the two
double-failures, and `12/14` + `2/14` add to the track count.

## F. What round 15 will carry, for planning only

Round 15's conditions are fixed in **its** lap 1, not here, and this list is not
a commitment to any of them.

- The remaining `cyanrip_log.c` survivors, mostly in the header block.
- `sc_reporting`'s `Cache model:` check is still `^Cache model:\s+\S`, which all
  four wordings satisfy — the same "a substring check over a whole document is
  satisfied by the document being wrong" shape we hit before.
- Three `runtime error` sanitizer assertions that **cannot fire**: the build is
  `b_sanitize=none` and the binary carries zero UBSan symbols.
- `src/cyanrip_encode.c` has never been swept.
- The four P2 rows reachable only under `-I`, where **no logfile is ever
  opened** — P2's header currently claims every line in it reaches both stdout
  and the logfile, and for those four that is wrong. A documentation fix, not a
  log change, but it is a claim we make about a surface you parse.

---

**Send one field.** If it is `GO`, we cut the stable release and open round 15.
