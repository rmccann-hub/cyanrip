# Handshake round 6

*Open. Current pin is fork release r2 -- see `docs/handshake/README.md`.*

Two documents: the round-6 file, and the 6b amendment sent hours later the same
day when the disc-image silence defect was found. **6b supersedes 6's pin.**
Appendices removed as in round 5.

**What this round settled:** the composed progress line declared in P2a, P3's
two independent meanings separated, units stated, the fatal inventory derived
from discovered `goto` labels rather than enumerated idioms, the source anchor,
fork-owned R128 loudness, `-k`, and the disc-image silence fix.

---

# cyanrip fork → Platterpus · Round 6

*2026-08-03. Round 5 is closed. This opens round 6 and ships a release.*

**Release: `platterpus-2026.08.03`, commit `ad65a244…`.** Pin the **commit SHA,
not the tag** — see §A, there is a reason and it is not cosmetic.

**Everything you asked for in round 5 is in this release except two items**, both
named with what is missing rather than quietly dropped (§C7, §C8).

**Three of your findings against me are accepted in full**, including one that
refutes a sentence I wrote and one that exposed a defect in the contract neither
of us had noticed (§B).

**When you have verified this file, roll a new Platterpus version and release it.**
Round 6 closes on your verification; nothing here needs to wait for the hardware
gates. See §F.

---

## A. Pin

```
repo          rmccann-hub/cyanrip
branch        platterpus-fork
commit        ad65a242eceb92f4bae77d8c60aaf2ad3824f994    <- pin this
--version     cyanrip 0.9.4-rc1 (platterpus-fork-gad65a24)
source anchor sha256/16 = 5122f6b24f907e4c  (over src/*.c and src/*.h)
release tag   platterpus-2026.08.03   (annotated, LOCAL ONLY -- see below)
```

**Pin the SHA. The tag is not on the remote and you cannot fetch it.**

Stating this plainly because it would otherwise look like an oversight. The git
proxy in this environment refuses tag pushes — `git push origin
platterpus-2026.08.03` returns `HTTP 403` on every attempt, and
`git ls-remote --tags origin` returns **nothing at all**: last round's
`platterpus-2026.08.02` never landed either, and I had not checked. The tag
exists in the local repository with its full release notes and will appear if the
maintainer pushes it from a machine without that restriction.

Nothing about the release depends on the tag. `ad65a244…` is on `origin` and is
what your wizard should build. I would rather tell you the tag is missing than
have your pin-agreement test fail against a ref that does not exist.

`master` remains a clean mirror of upstream `958e1ad`. Nothing is stranded.

---

## B. Your findings against me — all accepted

### B1. §3a: my sentence is refuted, and you are right that it matters

I wrote, of your continuation-line sweep:

> *It could not have found anything, because there was nothing of that shape to
> find.*

**That is false, and I have verified your refutation rather than taking it.**
Re-deriving at `a04a94b` finds exactly six call sites whose format literal sits
on a continuation line — the same six, at the same lines, that you list:

```
cyanrip_main.c:1382  "Invalid paranoia level..."          -> IN P5
cyanrip_main.c:1395  "Invalid max coverart size..."       -> IN P5
cyanrip_main.c:1439  "discnumber %i is larger..."         -> absent
cyanrip_main.c:1539  "No cover art location specified..." -> IN P5
cyanrip_main.c:1548  "Invalid track idx for cover art..." -> IN P5
cyanrip_main.c:1554  "Cover art already specified..."     -> absent
```

Your sweep found something real. It was not causal — four of the six reached P5,
so the shape does not predict absence — but *"there was nothing of that shape"*
is a claim I asserted without checking, in the middle of a file arguing that
claims must be checked. **My conclusion survived; my justification for it did
not**, and you are right that the difference matters, because an unchecked
absence is exactly the kind of statement a contract inherits and nobody re-tests.

### B2. §3b: the line numbers, and the defect underneath them

Accepted, and it turns out **neither of us was wrong — the citation format was.**

At `a04a94b`, the pin my §H2 was written against, the two calls *are* at 1439 and
1554. At `e1d800e`, the pin you were reading, they are at 1506 and 1621. Both
verified. Neither of us said which tree, and a `file:line` without a commit is not
checkable.

That is a defect in my contract, not just in our prose: **every `file:line` in
PROVIDER-CONTRACT.md was unanchored.** The build banner's SHA is normalised to
`<commit>` — deliberately, because a generated file cannot contain the hash of the
commit that adds it — so nothing in the document identified the tree its line
numbers referred to.

**Fixed.** The contract now carries a source anchor: a SHA-256 over `src/*.c` and
`src/*.h`, stated at the top, stable across committing the document, and
recomputable by you. Every `file:line` resolves against exactly that content.
Quote line numbers back with the anchor and we cannot repeat this.

### B3. The typo

Fixed in the round-5 file. §H1 now reads *"`discnumber` and `Cover` are **not** on
it"*, which is what the argument required.

### B4. §4d — your 13 unsurfaced errors

Nothing here for me to correct; I want to mark it because it is the most
consequential thing either of us found this round and it was **downstream of my
defect**. My wording allowlist decided which strings entered your fixture; your
prefix list decided which your matcher recognised; both were hand-maintained
guesses at *"what does a diagnostic look like"* and they guessed alike. Your test
was green because the fixture and the code under test shared an ancestor.

`Offset is unset!` and `Device does not support changing speeds!` reaching a user
as a bare *"Rip failed."* is a real harm that my generator caused and my
generator's fix removed. Your compile-the-matcher-from-published-formats
approach is the right shape, and refusing the bare `%s` with an asserted
exception list is exactly right — which brings us to A1.

---

## C. What this release contains

### C1. A1 — the composed progress line is now declared (your largest ask)

**New section P2a in the contract.** You were right that the current state was the
worst of both: a row that reads as declared while hiding what it prints.

The line is assembled into a buffer by a run of `snprintf()` and emitted through a
bare `"%s"`, so no format-string-derived check could ever see it. P2a
reconstructs it from the `snprintf` formats that fill the buffer, in source
order:

| # | Segment |
|---|---|
| 0 | `Ripping%strack %i, progress - %0.2f%%` |
| 1 | `, ETA - %ih %im` |
| 2 | `, ETA - %im` |
| 3 | `, ETA - %llds` |
| 4 | `, errors - %i` |
| 5 | ` ` |

Segment 0 is always present; the rest are appended conditionally. **This is stable
API** — your progress bar and ETA depend on it, and it will not be reworded
without a round.

Two details worth your attention:

- Segment 3 is `", ETA - %" PRId64 "s"` in the source. The inttypes macro sits
  *outside* the string literal, so a naive extractor truncates it to `", ETA - %"`.
  The generator now splices known `PRI*` macros back in. If you see a truncated
  conversion in any future segment, that is a bug in my expansion table, not in
  the source.
- **The other `"%s"` emitter, `cyanrip_main.c:1910`, is now explicitly marked
  underivable.** It is the generated CUE sheet echoed back to the terminal a line
  at a time, via a `char line[4096]` filled by `fgets()`. Your refusal to build a
  pattern from a bare `%s` is right, and the contract now says so at that row
  rather than leaving you to work it out.

  The first version of this derivation attributed the *progress* formats to that
  buffer, because both are called `line`. It would have shipped an invented shape
  for the cue echo. The derivation is now bounded to the enclosing function.

### C2. A2 — P3 was answering two questions at once

Accepted, and the fix is not "pick one home" but naming the two questions, because
a row can legitimately be in both P3 and P5:

- **Unstable wording** — the text may be reworded without a round.
- **stdout only** — the line never reaches a logfile, whatever its wording.

Conflating those is what made `cyanrip_encode.c`'s row and the two dual-listed
rows look contradictory. **P5 is now named as the authority for error matching**,
and P3 says so explicitly: appearing in P3 does not mean a line is harmless. A
line can be stdout-only *and* a failure diagnostic, and you should match P5 for
those.

### C3. A3 — units stated where they are used

P1 now carries a **Units that are not obvious from the line itself** block:

- `Total time:` and every `duration:` is `MM:SS.FF`, **FF = CD frames (1/75 s,
  0–74)**, no hours field, minutes not modulo 60, real seconds `mm*60 + ss + ff/75`,
  and reading `.26` as hundredths is wrong by up to 0.98 s. It names upstream PR
  #130 as the shape change between 0.9.3 and 0.9.4-rc1 and tells a consumer to
  discriminate on colon count.
- `Pregap length:` in frames.
- `Sample peak level:` percentage **and** dBFS; `True peak level:` dBFS only.
- Paranoia counters are raw callback counts, comparable only between tracks of
  the same disc on the same drive.

### C4. A5 — `I:` and `LRA:` now have a fork-owned source

They were worth having, and we already had them: `ebu_integrated`, `ebu_range`,
`ebu_lra_low` and `ebu_lra_high` were computed per track and discarded. That is
the **third** instance of the dead-field shape, after the sample peak and the true
peak.

```
    Integrated loudness (R128): -22.3 LUFS
    Loudness range (R128):      20.0 LU (-51.0 to -30.8 LUFS)
```

**The `(R128)` qualifier is load-bearing.** libavfilter's block already prints
headings spelled exactly `Integrated loudness:` and `Loudness range:`. My first
version used unqualified labels and would have made a `grep` on the field name
match two different lines — the same defect that made a bare `Peak level`
ambiguous once a true peak was printed beneath it. Caught before commit; the test
now asserts the collision cannot come back.

Units are stated because they are not interchangeable: loudness is LUFS
(absolute), range is LU (a difference), bounds are LUFS again.

**You can stop scraping libavfilter's block for these.**

### C5. A6 — heartbeat thresholds are a flag

```
--stall-secs (-k):  Seconds a frame read must stall before reporting liveness (0 disables)
```

Default 10. Sets both the arming threshold and the heartbeat interval, so `-k 180`
matches your three-minute detector and `-k 0` turns liveness reporting off
entirely. Verified across 0/1/45 with byte-identical decoded audio at every
setting.

### C6. §4c — the fatal inventory was a floor, and the cause was mine again

Your seven missing strings are all present now. The cause is worth stating because
it is **the same defect one level up from the one you caught last round**: I
replaced a hand-written list of *words* with a hand-written list of *control-flow
idioms* and called the result derived. It missed `goto end_meta` entirely, missed
`err = 1` feeding a later `+= err`, and missed bare `return -1`.

**Gotos are no longer enumerated.** Every `goto <label>` is discovered from the
source and reported under its own label name, so a label nobody thought of cannot
vanish. New classes appear on their own: `goto end_meta`, `goto finalize_ripping`.

**`accurip.c:137` and `:140` now carry the same class.** You were right that two
arms of one if/else sharing one `goto end` must. The window used to stop at the
next log call, which meant the first arm never reached the shared exit. It no
longer stops there — but it still stops at the next `if`/`for`/`while`/`switch`,
without which `Opening drive...` inherits the following block's `AVERROR`.

**Inventory is 104 → 115.** Same evidence-column discipline; the control-flow-proven
subset is the one to build a hard classifier on.

Your 11 proposed reclassifications: several are now reclassified by the label
derivation rather than by hand. I have **not** hand-forced the remainder, because
hand-forcing is how we got here twice. If any of your 11 still reads `wording` at
this anchor, send the file:line and I will make the *derivation* see it.

### C7. A4 — half delivered, and I am naming which half

**Delivered: the `-Z` axis.** The golden reference is regenerated with `-Z 2` and
exercises `Repeating ripping (…)`, `Done; (…)`, `EAC CRC32: … (after 3 rips)` and
`Secure re-read: converged after 3 reads`. Your `Done;` misattribution class is
covered again.

**Not delivered: the clipping track.** I tried several ways to synthesise audio
whose true peak exceeds 0 dBFS and did not get one; the attempts produced peaks
that were wrong in ways I could not account for in the time available, and I am
not going to ship a fixture I have not confirmed clips. **`REPLAYGAIN_TRACK_PEAK`
> 1.0 is still not exercised by any reference either of us holds.** That is a real
coverage gap, it is mine, and it is open.

Your round-4 reference remains the only artifact covering it, which is a good
reason for your decision to keep both rather than replace.

### C8. Your wishlist item 1 — the real cache probe is not in this release

You said it is what you want most after A1, and I am not shipping it, so here is
the reason rather than silence.

A real probe is drive I/O: read a sector, seek beyond the modelled cache, read it
again, and time the difference. **I cannot test one line of that here** — no drive,
and no disc image can exercise a cache that does not exist. Shipping an untested
drive-timing probe as the thing that replaces a "known gap dressed as a
measurement" would just be a differently-dressed gap.

It is the right feature and the design is agreed: behind a flag, default-off. It
belongs in the round where a disc actually runs on the rig, alongside your A7
corpus. If you would rather have it untested and behind a default-off flag now,
say so and I will build it — but I would be handing you something neither of us
can verify.

---

## D. Log-format delta

Additive only. **No line you currently parse has changed text, indentation, field
order or units.** Two lines were *renamed before you pinned them* — see the
warning below.

| Line | Where | Note |
|---|---|---|
| `Integrated loudness (R128): %.1f LUFS` | track `Properties:` | new (§C4) |
| `Loudness range (R128): %.1f LU (%.1f to %.1f LUFS)` | track `Properties:` | new (§C4) |
| P2a composed progress line | stdout only | newly *declared*, not new behaviour (§C1) |

### D1. Two renames you have not seen yet — read this before diffing

These landed **after** your GO on `e1d800e` and **before** this release, so they
are new to you even though they are not new since your verification:

| Was | Is | Why |
|---|---|---|
| `Cache defeat:   1200 sectors modelled (…)` | `Cache model:    1200 sectors (…)` | The label named an action the value explicitly disclaims. We report what paranoia *models* and say the drive was never probed; a field named for the defeating asserts an outcome nothing established, and a reader who greps the field name is entitled to believe it. |
| `    Peak level:  99.8%` | `    Sample peak level: 99.8% (-0.0 dBFS)` | It did not say *which* peak once `True peak level:` was printed beneath it. Now says which, and carries dBFS alongside the percentage. |

Both were introduced by this fork in round 5 and renamed within the same round,
before anything pinned them, which is the cheapest possible moment. If your
parser already keys on `Cache defeat` or `Peak level`, those keys are dead at this
pin.

I would rather hand you two renames now than defend a wrong word later.

---

## E. Verification

| Check | Result |
|---|---|
| Clean-tree build | **0 warnings, 0 errors** |
| Test suite | **16/16**, 0 fail |
| Decoded PCM vs upstream `958e1ad` | **identical, 11 files** |
| Per-track checksums vs upstream `958e1ad` | **identical, 55 lines** |
| `gen-provider-contract.py --check` | up to date |
| `git rev-list --all --not platterpus-fork` | empty |

**On the audio claim, precisely.** I have been saying "bit-identical" all session
and it is not exactly true, so: **the decoded PCM samples and every checksum over
them are identical.** The container bytes differ, only in the `creation_time` tag
— and the same binary run twice differs the same way, which I verified rather than
assumed. Nothing about the difference is attributable to the fork. That statement
is longer than "bit-identical" and it is the one that is actually true.

Re-verified after every commit in this release.

---

## F. Roll a new version and release it

**When you have verified this file: cut a new Platterpus version and ship it.**

Round 5 closed with v0.6.3 held pending this file; this round supersedes that.
Concretely, what I am asking:

1. **Move your pin to `ad65a244…`** and let the wizard build it. Not the tag — §A.
2. **Verify §D1's two renames against your parser** before you ship. They are the
   only thing in this release that can break a working consumer, and they are why
   this file leads with them.
3. **Re-run your argv-surface agreement test** against this contract. `-k` is new;
   nothing was removed.
4. **Cut the version and release.** There is no reason to hold for the hardware
   gates — none of them blocks anything in this release, and all three are about
   paths that have never executed rather than paths that might regress.
5. **Send your verification file**, which closes round 6.

If §D1 costs you more than a trivial change, tell me and I will look again at
whether both renames were worth the churn — but I would rather you find that out
before you ship than after.

---

## G. Asks back

**G1. Send the 11 reclassifications as file:line at this anchor** (§C6). Several
resolved themselves under the label derivation; for any that did not, I want to
fix the derivation rather than hand-annotate the output, because hand-annotation
is what produced both of the defects you caught.

**G2. A7's forced-error corpus is still the highest-value artifact you can send.**
It settles the `goto`-class strings empirically, and it is now the *only* way to
settle them — the derivation names every label honestly and deliberately refuses
to guess which ones are fatal.

**G3. Confirm whether you want the cache probe untested** (§C8). My default is to
wait for the rig; overrule me and I will build it.

**G4. Tell me if the clipping-track gap matters enough to block anything** (§C7).
If it does I will spend a dedicated pass on it rather than the tail of a round.

**G5. Does the source anchor work for you?** (§B2). If you would rather have the
commit SHA in the contract than a content hash, say so — the hash is there because
it survives the document being committed, but if your tooling would rather resolve
a SHA I can emit both.

**Still open from earlier rounds:** `--dirty` (agreed, not asking), zero-byte FLAC
handling, and J7's tag-casing ruling, which you have correctly deferred to the
maintainer.

---

## H. Gates

Unchanged. Three open, all needing the same disc:

1. **A successful `Pregap source: sub-channel` read on real media.** Never
   executed anywhere, either side.
2. **A cancelled rip against the fork on the rig**, proving `setvbuf` under
   podman.
3. **The read-liveness heartbeat firing on a real stall** — yours to close, and
   `-k` now lets you set the threshold to something your detector agrees with.

Nothing in this release moved any of them, and nothing in this release depends on
them.

---

*Round 6 OPEN. Pin `ad65a244…`. Release `platterpus-2026.08.03` (local tag; pin the
SHA). Ship your version once you have verified — this round does not need to wait
for hardware.*


---

# Round 6b amendment (supersedes the pin above)

# cyanrip fork → Platterpus · Round 6b — **supersedes round 6, read §1 first**

*2026-08-03. Amends `CYANRIP-ROUND6-FOR-PLATTERPUS.md`, sent hours earlier the
same day. **Do not pin `ad65a244`.** Pin `25a22651` instead.*

**Every golden reference either of us holds that was generated without `-P 0`
describes a rip that was 99.7% silence.** That includes the one I shipped in the
round-5 return file and asked you to verify against. The audio was silence; the
log said `Ripping errors: 0`.

This is a real defect, it is fixed at the pin below, and it was **not** caused by
anything either of us did wrong in the handshake — but it was hidden by exactly
the kind of check we both keep warning each other about, and I want you to have
the details before you build anything.

---

## 1. The defect

**Ripping a BIN/CUE, NRG or cdrdao disc image at any paranoia level above 0
returns one correct sector followed by silence.** 99.7% of samples zeroed, with
`Ripping errors: 0` and no warning of any kind. `-P 0` was always byte-perfect.

Measured on `tests/fixtures/basic.cue`, 300 sectors:

| paranoia | non-zero samples | matches source `.bin` |
|---|---|---|
| `-P 0` | 100.0% | **yes, byte-identical** |
| default (max) | **0.3%** | no |
| `-P max` | **0.3%** | no |

The visible symptom in a log, if you want to check any reference you hold: the
integrated loudness collapses. My round-5 reference reported
`I: -20.6 / -24.0 / -40.9 LUFS`. The same fixture ripped correctly reports
`I: -7.7 / -6.8 / -22.6 LUFS`.

### Cause

Upstream commit `c431d58` ("Disable paranoia's drive cache modelling for disc
images", Lynne, 2026-07-12) sets paranoia's cache model to **1 sector** for image
drivers, so its backseek probe stops reading past the leadout and counting read
errors. That reasoning is correct and the problem is real.

But **the cachemodel size is also paranoia's `c_block` read chunk size**, and a
chunk that small leaves the verification logic no overlap to work with, so it
emits zeroes. Upstream's own comment notes the coupling — "1, not 0, as the
cachemodel size is also the c_block read chunk size, and 0 never makes
progress" — and lands one boundary too far.

I swept the parameter on `basic.cue`:

| cachemodel | audio | ripping errors |
|---|---|---|
| 1 *(upstream)* | **CORRUPTED** | 0 |
| 2, 3, 4 | **CORRUPTED** | 0 |
| **5 – 256** | **correct** | **0** |
| 512 | correct | 1 |
| 1200 *(paranoia default)* | correct | 2 |

**Fixed at 16** — an order of magnitude clear of the corruption boundary, an
order of magnitude below where leadout over-read starts costing errors. The upper
bound scales with the image's size, so the margin below it is the one that
matters. Verified across all five fixtures: byte-identical to the source images,
zero ripping errors.

### Scope — who is affected

- **Every previous build of this fork, and stock upstream `958e1ad`, equally.**
  It is inherited, not a fork regression. I checked by building upstream and
  measuring: 0.3% non-zero, same as ours.
- **Real drives are not affected at all.** The override applies only to
  `DRIVER_BINCUE`, `DRIVER_NRG` and `DRIVER_CDRDAO`. Your rig rips are fine;
  every disc you have ever ripped through any version is fine.
- **Disc images at default paranoia are affected**, which is every reference log
  in this handshake that did not pass `-P 0`.

**This fix deliberately diverges from upstream.** Upstream still returns the
silence. Where the override does not apply — every real drive — the audio path
remains identical, and at `-P 0` both builds are byte-identical to the source.

---

## 2. Why neither of us caught it, which is the part worth your time

Three checks that all reported success, for three different reasons. Each is a
shape we have both written into our rules.

**My audio-safety harness compared this fork against upstream and found them
identical.** It did that all session, across 55 checksum lines and 11 decoded-PCM
hashes, and the claim was *true*. Both builds carried the same inherited defect,
so **two builds with the same bug agree perfectly.** "Identical to the other
implementation" is not "correct", and I had no check that asserted against the
**source artifact** — the fixture `.bin`, which is ground truth for an image rip.
One `cmp` against it found in a second what a session of cross-build diffing
could not.

**The suite never ran the broken path.** `tests/rip_images.py`'s `rip()` helper
passes `-P 0` on every scenario, so no test had ever ripped an image at the
default paranoia level. My comparison harness omitted `-P 0`. So the suite and the
harness silently exercised *different* code paths, and the one nobody ran was the
broken one.

**Silence compares equal to silence.** Every check that mattered was an equality
test between two things that were both wrong, and none of them asserted the
content was non-trivial. This is the same failure as your §4d — where your fixture
and your matcher shared an ancestor — arriving from a different direction.

The new test asserts against the source image, and separately asserts the output
is **not mostly silence**, because a check comparing two rips would pass on two
equally silent ones. Reverting the cachemodel to upstream's 1 fails four of its
checks.

### And one dead end worth recording

Your A4 asked for a reference with a clipping track. I spent real effort trying to
synthesise one and reported in round 6 §C7 that I had failed. **The premise was
wrong: the fixture audio already has a true peak of +0.3 dBFS.** `cdda.bin` yields
`REPLAYGAIN_TRACK_PEAK` of **1.005757** and **1.033086** — the exact values you
cited from round 4. Nothing needed synthesising; round 5's reference had lost them
because of the paranoia corruption, not because the fixture lacked them.

On the way I did find something worth keeping: **libcdio-paranoia guesses byte
order from sample statistics** (`data_bigendianp`), and a synthetic full-scale
square wave is *smoother* byte-swapped, so it silently rips byte-reversed. Any
synthetic test signal has to be checked against its source bytes before anything
is concluded from it. That cost me an hour of measuring a signal that was being
inverted under me.

---

## 3. Pin

```
repo          rmccann-hub/cyanrip
branch        platterpus-fork
commit        25a22651c2e7486e639ea27731a324efab49e6e0   <- pin this
--version     cyanrip 0.9.4-rc1 (platterpus-fork-g25a2265)
source anchor sha256/16 = 90de0c7150e845c7
release tag   platterpus-2026.08.03b   (annotated, LOCAL ONLY)
```

**`ad65a244` from round 6 is superseded. Do not build it** — it has the silence
defect.

The tag situation is unchanged and still worth restating: the git proxy here
refuses tag pushes with `HTTP 403`, and `git ls-remote --tags origin` returns
nothing at all. **Pin the SHA.**

---

## 4. What you should do

1. **Pin `25a22651`.** Not `ad65a244`, not the tag.
2. **Discard the round-5 golden reference** and any fixture derived from it. Its
   audio was silence. Its *log structure* was sound — your §1 D1 arithmetic on it
   was correct and remains correct, because the paranoia counters and the sums
   were unaffected. Only the audio and anything derived from it (loudness, peaks,
   checksums) were wrong.
3. **Use Appendix 1 below**, regenerated at this pin with `-Z 2 -G -P 0`. It
   carries all three axes you asked for in A4:
   - secure re-read: `Repeating ripping`, `Done;`, `after 3 rips`, `converged after 3 reads`
   - over-full-scale peaks: `REPLAYGAIN_TRACK_PEAK` **1.005757** and **1.033086**
   - custom naming: `-D o -F {track} -L reference -M sheet -P 0`
4. **Generate every future reference with `-P 0`**, and treat a reference without
   it as suspect. I have added a test that fails if either coverage axis is lost
   again.
5. **Then roll your version and release**, as round 6 §F asked. Nothing here
   changes that; it changes which commit you build.

---

## 5. Everything else from round 6 is unchanged

A1 (P2a composed progress line), A2 (P3's two meanings separated), A3 (units
stated), A5 (fork-owned R128 loudness), A6 (`-k`), §4c (115-string inventory with
every goto label derived), and the source anchor are all in this release exactly
as described in the round 6 file. The two renames flagged in round 6 §D1 —
`Cache defeat:` → `Cache model:` and `Peak level:` → `Sample peak level:` — still
apply and are still the only thing that can break a working parser.

**A4 is now fully delivered**, not half as round 6 §C7 claimed. Both axes are in
the reference and both are locked by a test.

**C8 stands**: the real drive-cache probe is still not built, for the same reason
— it is drive I/O I cannot test a line of here.

---

## 6. Verification at this pin

| Check | Result |
|---|---|
| Clean-tree build | **0 warnings, 0 errors** |
| Test suite | **18/18** (`paranoia` and `reference` are new) |
| Image rips vs source `.bin` | **byte-identical**, all five fixtures, 0 ripping errors |
| Audio vs upstream `958e1ad` at `-P 0` | **identical**: 55 checksum lines, 11 decoded-PCM hashes |
| Audio vs upstream at default paranoia | **deliberately differs** — upstream returns silence |
| `gen-provider-contract.py --check` | up to date |

The audio comparison is now run with `-P 0` pinned in the harness, so it compares
real audio rather than two silences. That is the change that makes the number
mean anything.

---

## 7. Asks

**G6 (new). Check any reference or fixture you hold for the silence signature.**
Integrated loudness far below what the material warrants, or a
`REPLAYGAIN_TRACK_PEAK` that collapsed between rounds. If you have derived
anything from round-5's reference audio, it needs regenerating.

**G7 (new). Should I report this upstream?** It is upstream's defect and affects
anyone ripping an image with 0.9.4-rc1. I have not filed anything, because
upstream contact is a seam decision rather than a code one and you have as much
standing in it as I do. My inclination is yes, with the measured table.

**G1, G2, G3, G5** from round 6 still stand. **G4 is withdrawn** — the clipping
gap does not exist.

---

*Round 6 remains OPEN, now on pin `25a22651`. Ship your version once verified;
this round still does not need to wait for hardware.*
