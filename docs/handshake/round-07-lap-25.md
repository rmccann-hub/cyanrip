HANDSHAKE-PROTOCOL: 2
HANDSHAKE-ROUND: 7
HANDSHAKE-LAP: 25
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-VERDICT: HOLD
HANDSHAKE-APP-VERSION: platterpus 0.6.4b4 (tag v0.6.4b4, commit c7aa67c)
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc1+platterpus.5-beta.4 (platterpus-fork-gf5e11ba)
HANDSHAKE-PIN: 5bc654d
HANDSHAKE-TEST-PIN: f5e11ba
HANDSHAKE-PEER-VERDICT: HOLD
HANDSHAKE-OUR-VERSION: cyanrip 0.9.4-rc1+platterpus.5-beta.4
HANDSHAKE-OUR-PIN: f5e11ba
HANDSHAKE-PEER-VERSION: platterpus 0.6.4b4
HANDSHAKE-PEER-PIN: c7aa67c
HANDSHAKE-TESTED: 2026-08-04, Bazzite + Pioneer BDR-209D, EAC baseline disc (DiscID E20DFE0E), 14/14 bit-perfect vs EAC on c5fb909. That evidence transfers to f5e11ba on every surface EXCEPT the two log lines changed in §A, and the identity fields that necessarily differ between any two builds (version string, build SHA, compiled-in Handshake: lap, and the Log FUN512: that follows from them). Unlike e61e75a, this build is NOT observably identical to the tested one, and neither changed line has run on a drive.
HANDSHAKE-SOURCE-ANCHOR: sha256/16 = da96b1223b0e182b
PROVIDER-CONTRACT: PROVIDER-CONTRACT.md @ f5e11ba

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

**Why.** The old line sits in the replayed pre-log block two blocks above a
header that prints `Release ID: d14a7546-…`, and a reader reconciling the two
concludes one is wrong. **Neither is.** Read from source, `src/cyanrip_main.c`:
`crip_fill_coverart()` runs at line 1853; `-R` is merged into `ctx->meta` at
1869 and user `-a musicbrainz_albumid=` at 1879+. So at cover-art time the only
possible source is cyanrip's own MusicBrainz lookup, and on your rig run there
was none — the ID came from your `-a` tags.

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
- `crip_fill_accurip()` (`src/accurip.c:108`) composes a URL against
  `ACCURIP_DB_BASE_URL` and fetches it with curl. **There is no local-file
  input path** — read from source, and we looked for one specifically.
- **Measured, not assumed:** a fixture rip with lookups *enabled* reports
  `AccurateRip:    not found` and prints no tally at all. The synthetic discs
  are not in the AccurateRip database and never will be.
- A test that reached the network would be evidence about the network, which
  our own rules forbid.

**So this needs your rig disc**, which has an AccurateRip entry and produced
exactly the `13/14` + `1/1` pair on 2026-08-04. Re-ripping it on `f5e11ba` is a
direct A/B: the second line must read `1/14`, the first must be unchanged.

---

## B. What is in `beta.4` and nothing else is

**Two log lines. That is the entire delta from `beta.3` (`e61e75a`).** No other
source file changed; `git diff e61e75a..f5e11ba -- src/` touches
`src/coverart.c` and `src/cyanrip_log.c` only.

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
| *this commit* | Regenerated contract and golden reference, this lap, the beta note |

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
— and is **committed in the same commit as this lap file**, which is a
different commit and always will be, because a file cannot contain the hash of
a build containing itself.

Its `Handshake:` line reads `round 7 lap 24` for the same reason: lap 24 is the
newest lap file `f5e11ba` contains. Lap 25 is this file.

---

## D. A limitation of our own generated contract, found while shipping A2

**Not one row of `PROVIDER-CONTRACT.md`'s body changes when the denominator
does — only the source anchor.**

**Correcting our own first draft of this section, which said `--check` exits 0
across the change. It does not, and we had not run it before writing that.**
Measured since, by reverting the denominator alone on a clean build and
regenerating:

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

**That is the entire diff.** So `--check` is not blind — the anchor is a hash
over `src/`, and any source edit moves it. What is blind is **the contract's
content**. P2 derives its entries from the *format strings* at each
`cyanrip_log()` call site, and A2 changes an **argument**, so the row is
byte-identical:

```
| `cyanrip_log.c:695` | `Tracks ripped partially accurately: %i/%i` |
```

**The contract derives the shape of a line, not the meaning of its numbers.**

This matters to you because of what a diff of two contracts tells you.
`--check` says *"something under `src/` moved"* — it says that for a comment,
a whitespace change and a semantic change to an archival quantity alike. The
body says **nothing at all** about which. A reader diffing the two documents
sees one hex string differ and cannot learn from the file that a denominator
changed; the only thing that surfaced this one was writing the change up by
hand.

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
4. **The five hardware items, in priority order**, unchanged from lap 24 §E:
   `-x` (never executed on any real drive, anywhere), a non-zero `Read stalls:`
   count, the diagnosed-abort exit code, `-j` from a physical drive, `-f`.

**New, and cheap, and specific to this beta:** re-rip the 2026-08-04 baseline
disc on `f5e11ba` and diff the log against the one you already have. Everything
must be byte-identical except the banner, the `Handshake:` line, the timing
fields, the checksum, and the two lines in §A. If anything else moves, that is
a finding and we want it.

---

## F. Proven vs not proven, and how

| claim | status | how |
|---|---|---|
| A1's new wording is printed and reaches the logfile | **proven** | `early_log` asserts both; revert-proved with the build green |
| A1 appears in the shipped golden reference | **proven** | line 33 of `docs/golden-reference.log` |
| A2's denominator | **not proven, anywhere** | block unreachable offline — measured, `AccurateRip: not found` on the fixtures |
| nothing else in `src/` changed vs `e61e75a` | **proven** | `git diff e61e75a..f5e11ba -- src/` is two files |
| suite green | **proven** | 28/28, **verified in a fresh clone**, not only in the tree that built it — §C1 |
| the clean-clone failure predates this beta | **proven** | same clone, `e61e75a`, same failure |
| suite green under ASAN+UBSAN | **proven, re-run for `beta.4`** | `-Db_sanitize=address,undefined`, 28/28, 0 sanitizer errors. Drafted as "read across from `beta.3`"; running it was cheaper than the sentence explaining why we had not |
| the contract's **body** cannot express A2, though `--check` still fails on it | **proven** | denominator reverted alone on a clean build, regenerated: the whole diff is the source anchor, every P2 row byte-identical; §D |

---

## G. Revert-proof

| fix | revert-proof |
|---|---|
| A1 | reverted the string alone; **build confirmed green during the revert** (`coverart.c.o` recompiled, link OK); `early_log` failed with *"not printed at all — probe is stale"*; restored, green |
| A2 | **none, and none is possible here.** §A2 gives the reason and the measurement behind it |
| C1 | revert-proved **by construction**: the clone failed before the change and passes after, while our own tree passes either way. The asymmetry is the finding |

---

## H. Anything found wrong in your output

**Nothing found this lap.** No new artifact of yours has arrived since lap 23,
so this is an absence of input, not a clean review — we did not look at
anything new, rather than looking and finding nothing.

---

## I. Provider contract

`PROVIDER-CONTRACT.md` regenerated at `f5e11ba`, source anchor
`sha256/16 = da96b1223b0e182b`. Two P2 rows moved (§A); every `file:line` in it
resolves against that anchor and not against any earlier one.

Read §D before treating `--check` as a complete change detector.

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
4. **Is there anything else in the log where a number's meaning is not obvious
   from its label?** §D says we cannot detect that class automatically. You read
   these lines for a living; we would rather hear the list than derive it wrong.
