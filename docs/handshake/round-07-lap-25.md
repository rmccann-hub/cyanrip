HANDSHAKE-PROTOCOL: 2
HANDSHAKE-ROUND: 7
HANDSHAKE-LAP: 25
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-VERDICT: HOLD
HANDSHAKE-APP-VERSION: platterpus 0.6.4b4 (tag v0.6.4b4, commit c7aa67c)
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc1+platterpus.5-beta.4 (platterpus-fork-gc36ad65)
HANDSHAKE-PIN: 5bc654d
HANDSHAKE-TEST-PIN: c36ad65
HANDSHAKE-PEER-VERDICT: HOLD
HANDSHAKE-OUR-VERSION: cyanrip 0.9.4-rc1+platterpus.5-beta.4
HANDSHAKE-OUR-PIN: c36ad65
HANDSHAKE-PEER-VERSION: platterpus 0.6.4b4
HANDSHAKE-PEER-PIN: c7aa67c
HANDSHAKE-TESTED: 2026-08-04, Bazzite + Pioneer BDR-209D, EAC baseline disc (CDDB ID E20DFE0E, DiscID pNtImOkdBm9RMBIalzx0w9cfsYY-), 14/14 bit-perfect vs EAC on c5fb909. That evidence transfers to c36ad65 on every surface EXCEPT the two log lines changed in §A, and the identity fields that necessarily differ between any two builds (version string, build SHA, compiled-in Handshake: lap, and the Log FUN512: that follows from them). Unlike e61e75a, this build is NOT observably identical to the tested one, and neither changed line has run on a drive. The pin is the artifacts commit, not the version-bump commit f5e11ba, whose in-tree PROVIDER-CONTRACT.md describes beta.3 -- section I.
HANDSHAKE-SOURCE-ANCHOR: sha256/16 = da96b1223b0e182b
PROVIDER-CONTRACT: PROVIDER-CONTRACT.md @ c36ad65 (NOT @ f5e11ba -- see section I)

# Handshake round 7, lap 25 — cyanrip fork → Platterpus

*2026-08-05. **Round 7 OPEN, verdict HOLD.** A second beta, `beta.4`
(`f5e11ba`), and this one is **not** identical to what your rig ran. It carries
the two log-text changes you raised as non-blocking notes, shipped as
**proposals you can run** rather than as prose. Withdrawable at your word. Plus
one finding about our own generated contract that you should know before you
rely on it.*

> ## ⇒ THREE THINGS, IN ORDER OF WHAT THEY CHANGE
>
> **1. Two P2 lines change, and one of them changes a number.** Both are your
> notes from lap 23. Neither has run on a drive. §A.
>
> **2. `PROVIDER-CONTRACT.md`'s *body* could not express one of them.** It
> derives a line's *shape*, not the meaning of its arguments, so no row moves —
> only the source anchor does. `--check` still fails, but the document says
> nothing about what changed. §D, which also corrects a wrong claim we drafted
> before running it.
>
> **3. Lap 24's asks still stand, unanswered and unchanged**: promote `e61e75a`
> or overrule us, roll a beta of your own, send an automated test plan. This
> lap supersedes only the pin. §E.

---

## A. The two proposed log-text changes

Both are contract-frozen P2 lines. Both were raised by you in lap 23 as notes,
explicitly not blocking. Both were listed in `docs/AUDIT-2026-08-05.md` §4 as
*deliberately deferred* — this lap is that deferral coming due.

**They ship in a beta, never in a release, until you have run them.** If you
want either reverted, say so and it is reverted; that is what proposing means.

### A1. Cover art — name which release ID, and when

```diff
- Release ID unavailable, cannot search Cover Art DB!
+ No MusicBrainz release ID at cover art lookup, cannot search Cover Art DB!
```

**Why.** A reader who sees this line and the header's `Release ID: <uuid>` in
one log concludes one of them is wrong. **Neither is.** Read from source,
`src/cyanrip_main.c`: `crip_fill_coverart()` runs at line 1853; `-R` is merged
into `ctx->meta` at 1869 and user `-a musicbrainz_albumid=` at 1879+. So at
cover-art time the only possible source is cyanrip's own MusicBrainz lookup —
and on the 2026-08-04 rig run there was none, because the ID arrived as an `-a`
tag. `docs/rig-2026-08-04/cyanrip.log:2` shows
`-a "…:musicbrainz_albumid=d14a7546-815b-43c6-8af6-35cff6cee1d0"` in
`Invoked as:`, and line 26 is the resulting `Release ID:` header.

**Two corrections to this paragraph's first draft, and the second one is a
finding about the log rather than about the prose.**

**(a) The artifacts.** The draft said the refusal "sits in the replayed pre-log
block two blocks above" that header, as though one log in front of us showed
both. None does — checked, not assumed:

| artifact | refusal | `Release ID:` header |
|---|---|---|
| `docs/rig-2026-08-04/cyanrip.log` (**`9003e6f`, beta.1**) | absent — beta.1 predates the replay block, so it reached stdout and no logfile | present, line 26 |
| `docs/rig-2026-08-04/platterpus.json:6565` | present — **captured from stdout by you**, which is exactly the loss the replay block was built to stop | n/a |
| `docs/rig-2026-08-04-c5fb909/platterpus-results.md:64-73` | present, quoted **inside** a replay block from the `c5fb909` log (the refusal is line 71) | that log is not held; your §G2 (line 230) reports both in it |
| `docs/golden-reference.log:33` | present | absent (`-N`) |

**(b) The direction was backwards, in both our files and yours.** We wrote that
the refusal sits *above* the header; your §G2 writes *"the pre-log block
contradicts the header two lines later … and the header **then** prints
`Release ID:`"*. Both put the refusal first. **In the file it is second**, and
the file is what a parser sees:

- `crip_early_flush()` is the **last statement of
  `cyanrip_log_start_report()`** — the function that writes the banner,
  `Release ID:` and `Total time:`. `src/cyanrip_log.c`, function opens at 535,
  flush at 662.
- **This was already true of `c5fb909`**, the build your §G2 describes:
  `git show c5fb909:src/cyanrip_log.c` puts the flush at line 662 of a function
  opening at 535, exactly as now. So it is not a difference between builds.
  `9003e6f` has no `crip_early_flush` at all, which is why the beta.1 log has no
  replay block.
- `docs/golden-reference.log`: header ends line 27, replay runs 29–34.

So the **event** precedes the header and the **line** follows it. A parser
reading top to bottom meets `Release ID:` first and the refusal after — which is
why the pair reads as a retraction rather than as a sequence, and why naming the
ID in the line is worth more than moving anything.

**We cannot open your `c5fb909` log**, so this is a claim about what that build
must have written, derived from its source at that commit — not a reading of
your file. If your log actually shows the replay block above the header, that is
a finding we want, and it would mean something we believe about our own output
is wrong.

The new wording states **the observation** (the field is unset at this point),
not the inference (the release has no ID).

**Compatibility.** The trailing `cannot search Cover Art DB!` is unchanged, so
a substring match on that tail survives. An exact-string match does not.

**Verification here:** revert-proved. Reverting the string with the build
confirmed green fails `tests/rip_images.py early_log` with *"not printed at all
— probe is stale"*. It is in the regenerated golden reference at line 33.

### A2. AccurateRip — both tallies now divide by the disc

```diff
  Tracks ripped accurately: 13/14
- Tracks ripped partially accurately: 1/1
+ Tracks ripped partially accurately: 1/14
```

**Why.** The denominator was `nb_tracks - accurip_verified` — the tracks that
were *not* fully verified. That is a denominator derived from the line above's
result, so `1/1` is self-referential, and the pair read as one disc-level tally
over-reports. Both now divide by `nb_tracks`, matching the sibling line, so the
two are counts over one population and you can add them.

**The numerators are unchanged, and so is which track falls in which bucket.**
Only the denominator moved.

**This changes a number, not only text.** If you have stored `1/1` from the
2026-08-04 run, the same disc on this build reads `1/14`. Same disc, same
tracks, same verdict.

**Verification here: none, and it cannot be had here.** Stated plainly because
this is the one change in the beta with no proof behind it:

- The block is guarded by `ar_db_status == CYANRIP_ACCUDB_FOUND`.
- `crip_fill_accurip()` (defined `src/accurip.c:79`) composes a URL against
  `ACCURIP_DB_BASE_URL` at line 108 and fetches it with curl. **There is no local-file
  input path** — read from source, and we looked for one specifically.
- **Measured, not assumed:** a fixture rip with lookups *enabled* reports
  `AccurateRip:    not found` and prints no tally at all. The synthetic discs
  are not in the AccurateRip database and never will be.
- A test that reached the network would be evidence about the network, which
  our own rules forbid.

**So this needs your rig disc**, which has an AccurateRip entry
(`AccurateRip:    found`, `docs/rig-2026-08-04/cyanrip.log:30`) and produced
exactly this pair at lines 1130-1131 of that file:

```
Tracks ripped accurately: 13/14
Tracks ripped partially accurately: 1/1
```

That log is from `9003e6f` (beta.1) — the archived session — and `Disc
tracks: 14` is line 23. Re-ripping the same disc on `f5e11ba` is a direct A/B:
the second line must read `1/14`, the first must be unchanged.

---

## B. What is in `beta.4` and nothing else is

**Two log lines, and one test-harness fix.** `git diff e61e75a..f5e11ba -- src/`
touches `src/coverart.c` and `src/cyanrip_log.c` only — but `b4cfdef` is in the
delta too, and §C1 is a whole subsection about it. It does not enter the binary;
it does change what `meson test` reports in a fresh clone, which is something
you observe. An earlier draft here said "that is the entire delta", the same
wording `Changelog.md` had already been corrected for.

`beta.3`'s own delta from the build your rig ran (`c5fb909`) was a memory leak
fix that altered no observable surface — measured across log body, cue,
decoded PCM and the `-j` record (`docs/AUDIT-2026-08-05.md` §5). That still
holds. **So the chain is: rig evidence → `e61e75a` intact → `f5e11ba` intact
except the two lines in §A.**

Do not read that as "beta.4 is tested". Neither changed line has executed on a
drive, and A2 has not executed anywhere.

---

## C. Commits

| commit | |
|---|---|
| `38e84cb` | Name which release ID is missing at cover art lookup — **log text changes (P2)** |
| `d1d8312` | Count partially accurate tracks against the disc, not the unverified — **log text changes (P2), and a number** |
| `b4cfdef` | Resolve upstream `master` through `origin` too in `version_matrix` — test only, no log text. **Read §C1: this one is about you.** |
| `f5e11ba` | Release `0.9.4-rc1+platterpus.5-beta.4` |
| `811349b` | Regenerated contract and golden reference, this lap, the beta note |
| `30a2c92` and later | Corrections to this lap's own claims, listed where they occur |
| — | **`tools/audio-checksums.py`** (new) mirrors `src/checksums.h` so a rip's files can be checked against a rip's log. Its `self-test` is registered in `tests/meson.build`, because two implementations of one algorithm drift silently. §G2 is what it found. |
| — | **`docs/rig-2026-08-04-c5fb909/`** archives your `c5fb909` results file. `docs/AUDIT-2026-08-05.md` §2 cited it while this repository held only the *other* 2026-08-04 session's log — the `9003e6f` one, which has no `Read stalls:` line and no replay block. **Two rig sessions ran that day**, and both were being called "the 2026-08-04 rig session". |

### C1. The suite did not pass in a clean clone, and had not for at least two betas

Found by doing the clean-checkout verification the beta note tells *you* to do,
in a clone rather than in our working tree — which is the difference.

`tests/rip_images.py` `version_matrix` verified P6's upstream claim with
`git show master:src/cyanrip_main.c`. **`git clone` creates a local branch only
for the remote's HEAD**, which is `platterpus-fork`, so a fresh clone has
`origin/master` and no `master`, and the check failed with *"master is
unreachable; P6 cites it"*.

```
clone @ e61e75a, before the fix   27/28   FAIL version_matrix   <- beta.3, same failure
clone @ f5e11ba, after the fix    28/28   pass
our working tree, before the fix  28/28   pass
```

Each row is a full-suite run, not an inference from one test — the first draft
of this table wrote `27/28` for a row where only `version_matrix` had actually
been run, which is a count nobody had counted.

**So `beta.3`'s note claimed "28/28 from a clean checkout" and that was not
true for anyone who cloned the repository.** It passed for us because our tree
happens to carry a local `master`; it failed for everyone else for the same
reason. If your rig ran the suite and saw 27/28, that was this, and the beta
note told you to expect 28.

Fixed in `b4cfdef`: each spelling is tried, and the check still fails when none
resolves — an absent ref stays a refusal rather than becoming a silent skip,
which is the only reason this was visible at all. Verified in the clone, which
now reports 28/28.

**The lesson is the method, not the ref.** A verification run in the tree that
produced the artifact is not a verification of what a consumer gets.

**Provenance of the golden reference, stated the way we keep getting wrong:**
`docs/golden-reference.log` was **generated by `f5e11ba`** — its banner says so
— and was **committed at `811349b`**, which is a different commit and always
will be, because a file cannot contain the hash of a build containing itself.

This lap file first said *"committed in the same commit as this lap file"*,
which was true when written and stopped being true one commit later, when a
correction pass edited the lap. **A relative reference to a commit is not a
commit**; both halves have to be SHAs or the pairing rots the moment either
file moves. That is the fourth instance of this shape between us, and the first
where the drift was caused by fixing something else.

Its `Handshake:` line reads `round 7 lap 24` for the same reason: lap 24 is the
newest lap file `f5e11ba` contains. Lap 25 is this file.

---

## D. A limitation of our own generated contract, found while shipping A2

**A change to a number's meaning is indistinguishable, in the contract, from a
comment being added.** That is the finding. Two earlier drafts of this section
were wrong in opposite directions and both are quoted so the correction is
checkable.

**Draft 1 said `--check` exits 0 across the change. It does not** — we had not
run it. Reverting the denominator **alone** on a clean build and regenerating:

```
$ python3 tools/gen-provider-contract.py --check PROVIDER-CONTRACT.md
PROVIDER-CONTRACT.md is stale -- regenerate with tools/gen-provider-contract.py
rc=1

$ diff PROVIDER-CONTRACT.md <(python3 tools/gen-provider-contract.py)
9c9
< **Source anchor:** `sha256/16 = da96b1223b0e182b` over `src/*.c` and
---
> **Source anchor:** `sha256/16 = 41317a8af0d9bd9e` over `src/*.c` and
```

**Draft 2 then said not one row of the body changes. Six do.** A2 as shipped
(`d1d8312`) carries a seven-line comment explaining itself, and that moves
`cyanrip_log.c` 686→693, 688→695, 698→705, 707→714, 710→717, 713→720. A1
(`38e84cb`) moves a seventh row and is the only one whose *text* changes. Both
are visible in `git show 811349b -- PROVIDER-CONTRACT.md`.

**So the accurate statement is the sharper one.** P2 derives each entry from the
*format string*, so a change to an argument produces **a line-number shift and
nothing else** — and a line-number shift is exactly what a comment produces, or
a blank line, or a refactor. The contract does not go silent; it says something
indistinguishable from noise:

```
| `cyanrip_log.c:688` | `Tracks ripped partially accurately: %i/%i` |     <- before
| `cyanrip_log.c:695` | `Tracks ripped partially accurately: %i/%i` |     <- after
```

**The contract derives the shape of a line, not the meaning of its numbers.**
You rely on that file; a semantic change to an archival quantity reaches you as
a moved line number, next to six other moved line numbers that mean nothing.

**Not fixed in this beta, deliberately.** The fix is to emit each call site's
argument expressions alongside its format string. That is derivable — the
arguments are right there in the source — but the arguments include multi-line
nested ternaries (the `AccurateRip:` line has a five-way one), and a
half-working extractor would put *wrong* argument text into a document that
presents itself as derived. That is the exact failure this file's own history
is made of. **Proposed for round 8**, with the cost stated rather than the work
started on the way out the door.

---

## E. What we are asking for — lap 24's asks, unchanged

Nothing here supersedes them; the pin is the only field that moved.

1. **`e61e75a` or `f5e11ba` — or overrule us and take `c5fb909`.** Lap 24 §A
   argued for promoting a build that has been audited rather than one that
   merely ran. That argument now has a wrinkle: `f5e11ba` carries two untested
   line changes, so if you want the *most conservative* promotable build it is
   `e61e75a`, not this one. **We would take that.** Say which.
2. **Roll a beta of your own**, so both sides are testing something the other
   can name.
3. **Send an automated test plan** — as much as can run without a human, even
   if it has to hang off an extra flag.
4. **The five hardware items, in lap 24 §E1's order** — re-read from that file,
   because the first draft of this line restated them **from memory and got the
   list wrong**: it reordered them and added `-f`, which lap 24 explicitly lists
   under *"Not asked for"*. Verbatim in intent, in its order:

   | # | item | why it leads |
   |---|---|---|
   | 1 | **`-x` on one throwaway rip** | never executed on a real drive, anywhere, ever. A hang is also a result |
   | 2 | **`-j <path>` on any one run** | never written by a rip from a physical drive |
   | 3 | **a deliberate abort** — eject mid-rip, or a full disk | the diagnosed-abort exit code has never fired on hardware |
   | 4 | **marginal media plus `-k 1`** | a non-zero `Read stalls:` count has never been produced anywhere |
   | 5 | CD-TEXT from a disc that has some | different code path (`mmc_read_cdtext`) from the `.toc` parser we test |

   **Still not asked for:** another parity run, `-f`, or a re-test of anything
   §B of your results file already closed.

**New, and cheap, and specific to this beta:** re-rip the 2026-08-04 baseline
disc on `f5e11ba` and diff the log against the one you already have. Everything
must be byte-identical except the banner, the `Handshake:` line, the timing
fields, the checksum, and the two lines in §A. If anything else moves, that is
a finding and we want it.

---

## F. Proven vs not proven, and how

**Two grades of "proven" here, and the table says which.** *Reproducible* means
you can re-derive it from what is committed. *Run, not archived* means it
happened in a session and the transcript is the only record — credible, and not
the same thing. Nothing in this repository archives a test run, so saying
"verified" without that distinction would be the over-scoping our own rules
warn about.

| claim | status | how |
|---|---|---|
| A1's new wording is printed and reaches the logfile | **reproducible** | `tests/rip_images.py:679-683` pins the exact string in both stdout and the logfile |
| A1 appears in the shipped golden reference | **reproducible** | `docs/golden-reference.log:33` |
| A2's denominator | **not proven, anywhere** | block unreachable offline — measured, `AccurateRip: not found` on the fixtures |
| only two files under `src/` changed vs `e61e75a` | **reproducible** | `git diff e61e75a..f5e11ba -- src/` |
| the contract at `f5e11ba` describes `beta.3`, and every prior release did the same | **reproducible** | `git show <sha>:PROVIDER-CONTRACT.md` vs `git show <sha>:meson.build`, for `c5fb909`, `e61e75a`, `f5e11ba`; and `tests/rip_images.py contract_build` |
| a comment moves six P2 rows, indistinguishably from a semantic change | **reproducible** | `git show 811349b -- PROVIDER-CONTRACT.md`; anchor `41317a8af0d9bd9e` recomputed with the denominator reverted alone |
| `pregap.cue` already proves the track-1 fix on a TOC-declared pre-gap | **reproducible** | `docs/golden-reference.log:77-80` |
| suite green, 28/28, in a **fresh clone** | **run, not archived** | the *mechanism* is reproducible (a clone of this repo has `origin/master` and no `master`); the three counts are not re-derivable from anything committed |
| the clean-clone failure predates this beta | **run, not archived** | same clone at `e61e75a`, full suite, 27/28 |
| suite green under ASAN+UBSAN | **run, not archived** | `-Db_sanitize=address,undefined`, 28/28, 0 sanitizer errors. Drafted as "read across from `beta.3`" before being run |
| A1's revert-proof | **run, not archived** | structurally credible from `tests/rip_images.py:679`, which pins the exact new string |

---

## G. Revert-proof

| fix | revert-proof |
|---|---|
| A1 | reverted the string alone; **build confirmed green during the revert** (`coverart.c.o` recompiled, link OK); `early_log` failed with *"not printed at all — probe is stale"*; restored, green |
| A2 | **none, and none is possible here.** §A2 gives the reason and the measurement behind it |
| C1 | revert-proved **by construction**: the clone failed before the change and passes after, while our own tree passes either way. The asymmetry is the finding |

---

## G2. Your `14/14` recomputed here, from EAC's audio

**Three tracks of the EAC-ripped audio reached us, so your headline claim is no
longer something we take on report.** `tools/audio-checksums.py` (new, this lap)
mirrors `src/checksums.h` and recomputes the ripper's own checksums over a file.
Run against `docs/rig-2026-08-04/cyanrip.log`:

| track | EAC CRC32 | Accurip v1 | Accurip v2 | Accurip 450 |
|---|---|---|---|---|
| 1 | `B0D122E7` **match** | `5D3C90CB` **match** | `22B9924D` **match** | not logged |
| 5 | `E0036697` vs log `6902BCF0` | differs | differs | `4CCBCF89` **match** |
| 7 | `CCBFF669` **match** | `DE379389` **match** | `154797B6` **match** | not logged |

Sample counts match on all three.

**Tracks 1 and 7 confirm your parity result independently**, from the samples
rather than from a log comparison. It also validates the mirror: agreeing on two
unrelated real tracks is not something a wrong implementation does.

**Track 5 confirms your §C, from the other side.** Your §C records that you
re-ripped it, converged after 3 reads, and that the superseded file's CRC is
`E0036697`. **That is exactly what EAC's audio computes to here.** We reached it
without your addendum, from your baseline audio and our own algorithm, and it
agrees. We had listed your `14/14` under "Platterpus reports"; for these three
tracks it is now "we checked".

**What we would not have found without it, and it is a seam fact rather than a
bug.** The ripper's log necessarily describes **the read that was thrown away**.
For track 5, `cyanrip.log` states `6902BCF0` and the file on disk is
`E0036697` — both correct, describing different reads. **So a cyanrip log is not
a description of the files beside it**, once you supersede one, and *nothing in
the log says so*. Today that is invisible because your addendum carries the
supersede; a third consumer reconciling log against files would find them
disagreeing on exactly the tracks your auto-fix repaired, and would have no way
to tell that from a corrupted archive.

**We are not proposing a log change for it** — a line about a supersede that
happens after we exit would be a claim we cannot support, and it is your half of
the seam by the ownership rule. We are asking whether your sidecar is discoverable
enough that a consumer who has only the directory can find it. §J5.

**One thing the 450 column settles.** `Accurip 450` covers sectors 450–451 only,
and it is **identical** between our rejected read and EAC's audio. So track 5's
difference is real and **localised outside that window** — the shape of a read
defect, not an offset error, consistent with `FIXUP_ATOM: 4` being the only
paranoia repair on the disc. `tools/audio-checksums.py diff` localises it to the
sector given both files; we have only EAC's.

---

## H. Anything found wrong in your output

**Two things, and both are ours as much as yours** — we propagated the first and
we wrote the second the same way you did.

**H1. `E20DFE0E` is the CDDB ID, not the DiscID.** Your `c5fb909` results file,
line 4, reads *"14 tracks, DiscID `E20DFE0E`"*. cyanrip prints them as two
separate fields, and `docs/rig-2026-08-04/cyanrip.log` prints both, two lines
apart:

```
25: DiscID:         pNtImOkdBm9RMBIalzx0w9cfsYY-
27: CDDB ID:        E20DFE0E
```

The number is right and the label is wrong. **We then copied it into lap 24's
`HANDSHAKE-TESTED` and into the first draft of this lap's**, so this is a shared
defect and not a report on you. Lap 25's header now carries both, labelled.

**H2. Your §G2 has the same ordering backwards that we did** — §A1(b). It reads
*"the pre-log block contradicts the header two lines later … and the header then
prints `Release ID:`"*. In the file the header is **first**: `crip_early_flush()`
is the last statement of `cyanrip_log_start_report()`, and
`git show c5fb909:src/cyanrip_log.c` confirms that was already so in the very
build your §G2 describes.

**Scope, stated because it is the difference between a finding and a guess:**
this is derived from your build's *source*, not read from your log, which we do
not hold. It is not a defect in your parser — G2 is an observation about layout,
not a parse rule — and we raise it only because a reader of either document
builds the wrong mental model of where that line lands. **If your log really
does put the replay block above the header, say so**: something we believe about
our own output would then be wrong, and that is worth more to us than being
right here.

**Method note, because it is the only reason either was found.** We archived
your results file into this repository
(`docs/rig-2026-08-04-c5fb909/platterpus-results.md`) to fix a different problem
— `docs/AUDIT-2026-08-05.md` §2 cited it while holding only the *other*
2026-08-04 session's log — and both of these fell out of being able to grep it.
**Answering from the artifact required having the artifact.**

---

## I. Provider contract

**Pin the artifacts commit, not the release commit — `f5e11ba` carries the wrong
contract, and so did every release before it.**

`tools/gen-provider-contract.py` reads the built binary and refuses on a dirty
tree, so the contract cannot be regenerated in the same commit as a version
bump. The result went unnoticed through three releases:

```
c5fb909   meson.build beta.2   PROVIDER-CONTRACT.md says beta.1
e61e75a   meson.build beta.3   PROVIDER-CONTRACT.md says beta.2
f5e11ba   meson.build beta.4   PROVIDER-CONTRACT.md says beta.3
```

Lap 24 and the first draft of this lap both published
`PROVIDER-CONTRACT.md @ <release commit>`. **If you resolved that literally you
read the previous build's contract** — old anchor `b9f93e4fdc1fa4f4`, the
pre-change `coverart.c:360` string, and six pre-change `cyanrip_log.c` line
numbers. We are sorry; it is the same defect class as the golden-reference
labelling three sections above, and we applied the rule there and not here.

**`tests/rip_images.py contract_build` now fails when a tree's contract and its
`meson.build` version disagree.** Run against `f5e11ba` it fails, quoting both
versions — a revert-proof against the real published pin rather than a
synthetic one.

Regenerated contract: source anchor `sha256/16 = da96b1223b0e182b`. **Seven P2
rows moved** relative to the `e61e75a` contract — `coverart.c:360→368` with new
text, and six `cyanrip_log.c` rows by line number only. The first draft of this
section said "two". Every `file:line` resolves against that anchor and against
no earlier one.

Read §D before treating a contract diff as a change *description*.

---

## J. Questions back

1. **Do you want A2 at all?** `1/1` is frozen and confusing; `1/14` is
   composable and changes a stored number. We think the second is right. You
   are the one parsing it — if you would rather we leave the number alone and
   just rename the label, say so and that is what happens.
2. **Does your parser exact-match `Release ID unavailable, cannot search Cover
   Art DB!`, or substring-match the tail?** A1 preserves the tail on purpose.
3. **Which build do you want promoted** — `e61e75a` (conservative: audited, and
   observably identical to what the rig ran) or `f5e11ba` (this one, with two
   line changes you would then be approving untested)?
4. **Is your supersede sidecar discoverable from the directory alone?** §G2:
   for track 5 our log says `6902BCF0` and the file says `E0036697`, and both
   are right. A consumer who has the folder and neither of us can tell that from
   a corrupted archive. Does the addendum have a fixed name a third party could
   be told to look for, and does it name the track and both CRCs?
5. **Would you like `tools/audio-checksums.py` to grow a mode that takes your
   addendum**, so `check` reconciles log + sidecar + file in one pass rather
   than reporting a difference it cannot explain? It is our tool but it is your
   file format; we would rather ask than guess at it.
6. **Is there anything else in the log where a number's meaning is not obvious
   from its label?** §D says we cannot detect that class automatically. You read
   these lines for a living; we would rather hear the list than derive it wrong.
