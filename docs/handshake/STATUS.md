# cyanrip standing status — what the consumer can assume between rounds

**Not a round, not a lap, and it must not be counted as one.** It carries no
`HANDSHAKE-*` wire headers for that reason, and `tests/handshake_wire.py` never
sees it because it is not named `round-NN-lap-LL.md`.

The convention is Platterpus's, adopted verbatim: they sent us one on 2026-08-21
for v0.6.21, explicitly outside the round mechanism, and it was the right shape.
Rounds are the *formal* channel and they cost something — S-13 fixes a round's
close conditions at lap 1, and an open round blocks both sides' releases. Between
rounds each side still needs somewhere to say where it is.

**Rewritten in place, never appended to.** A stale standing status is worse than
none. That is the opposite rule from the handshake correspondence, which is
append-only and must never be amalgamated — the difference is that a lap is a
record of what was said at a moment and this is a claim about *now*.

---

## Rewritten 2026-09-05. **Round 15 is OPEN at lap 13, theirs, received and filed. No lap is owed either way. The round closes on their run, which starts tonight.**

**Lap 12 delivered the correction this file used to say was owed** — our lap 10
told them 16 P5 rows "rest only on a construct that does not end the run", and
for eight of them that was wrong because each is followed immediately by
`goto end`. Lap 12 §3 carries it. Nothing is outstanding from us.

**Our lap 12 pre-commits under S-18: our next lap is `GO` on `978f9b0` unless
their run finds a defect in it.** That binds. It is conditioned on *their* run,
so the findings below do not release us from it — and none of them makes the
reviewed pin unsafe, which is the only thing that could promote one to blocking.

### A test audit ran on 2026-09-05, and what it changes here

`docs/AUDIT-2026-09-05.md` is the record; `docs/SETTLED.md` carries the rows with
their re-check commands. Seven defects were verified first-hand, two lane claims
were refuted by measurement, and the merge-back list is now **six**.

**Exactly one of them is theirs to agree to, and it is the one that matters most:**

> **`docs/seam-commands.md` §7 is stale, and both projects have cryptographically
> agreed on the stale bytes.** Line 504 publishes `-p '99=drop'` as accepted /
> exit 0; the binary refuses it with exit 1 and a diagnostic, and the control
> `-p '1=drop'` exits 0 so the probe discriminates. The file last moved
> `b9a9c53` (2026-08-07); the bound moved `bf8ab3a` (2026-08-15).
>
> Its `sha256` is `7dc31381…5564196`, byte-identical to the `seam-commands=`
> value in `round-15-lap-12.md:23`, and `tools/seam-check.py` reports **OK**.
>
> **A shared hash proves both sides hold the same bytes. It can never prove the
> bytes describe the binary.** §7 has no `--check` and no gate — it is the one
> shared artifact where those two facts can diverge in silence, and they have.

`seam-commands.md` is jointly owned, so a cell correction is a shared-file edit
and needs a joint version bump. **It goes in a lap.** The remedy is ours to build
and theirs to assent to: `--check` in `tools/probe-argv-surface.py`, regenerating
§7 between explicit delimiters and diffing. The delimiters are not decoration —
the check must not claim prose the other side wrote.

**Everything else found is ours alone, and none of it is lap material.** Under the
2026-08-26 reform, findings go in commit messages and `Changelog.md`, which they
can read from git and which need no reply. Five of the six code defects are frozen
by S-15 while the round is open; all are next-round work. In brief, all upstream's
and all with commands in `docs/SETTLED.md`:

| finding | reach |
|---|---|
| Three live defects in the AccurateRip response parser — unchecked `av_realloc` feeding a `memcpy`, `strcmp` on a NULL `content_type`, `strstr` over a never-NUL-terminated buffer | the network path, which **no scenario here can reach**: all 40 hardcode `-N -A -U` |
| `fun512.c:72` signed-overflow UB — `ftell` on a directory returns `LONG_MAX`, so `len + 1` overflows before any bound check | `cyanrip -Y <a directory>` |
| `cyanrip_main.c:2184`/`:2186` bare `return 1;` skip `cyanrip_ctx_end()`, which also **closes the drive** | the log-init and cue-init failure paths |
| Invalid UTF-8 truncates a name; a **leading** bad byte empties the component, and with a multi-component `-D` the path becomes **absolute** | measured with their own `-D {album_artist}/{album}`: a rip landed in `/Some Album`, exit 0 |
| A logfile's first line is not always the fork banner when a naming-scheme argument holds invalid UTF-8 | `-Y` still returns 0 on such a log |

**One was ours and was made that same session:** two `docs/SETTLED.md` cells ran
`meson test` inside a registered meson test, so the suite re-entered meson on the
same build directory and the inner run truncated `testlog.json` — 26.7% NUL, 47 of
61 records, while JUnit stayed intact. Fixed at `8e1fd20` and guarded. The suite
had really passed; its machine-readable record of passing had not.

**And one positive result, recorded because an absence of a finding is a result:**
metadata **cannot** escape the output directory. `/` becomes U+2215 before it
reaches the filesystem; 16 of 16 traversal attempts across all four `-T` modes
stayed contained.

### Their lap 13 arrived 2026-09-05. **No lap is owed and none was sent.**

Filed at `docs/handshake/inbound/round-15-lap-13.md`; the envelope's second part,
`fullacceptance.txt`, is filed beside it. Both verified byte-exact against the
manifest's own hashes (19,872 B / `25e949e4…`, 44,366 B / `d3fd3cce…`).

| checked here | result |
|---|---|
| their digest `12243ffa9e1f843e over 12` | re-derives exactly with our implementation — **eighth** consecutive agreeing value |
| their quoted sha256 of our lap 12, `fedf8712b87b13da…` | matches `sha256sum docs/handshake/round-15-lap-12.md` |
| `tools/seam-check.py` over their lap | 0 FAIL. One UNPROBED — `HANDSHAKE-FROM-COMMIT` is declared `pending`, so nothing was resolved and the checker says so rather than passing it |

**Why no lap.** Their §D requires nothing, §E asks nothing, §G has no questions,
§H found nothing in our output, §I lists what they are explicitly not asking, and
§K says to reply before the run *only* if we dispute §A2, §A3 or §C4, or if our
`GO` changes. **We dispute none of the three and our `GO` stands.** Under the
2026-08-26 reform an acknowledgement lap is not a lap — nothing to say is a
complete answer.

**Their build moved a fifth time, to `0.6.38`**, disclosed as a break in their §A1:
an audit of their acceptance script found four ARCHIVAL checks satisfiable by
finding nothing, three of them the only graded step in their section. The run
starts on `0.6.38` + `978f9b0`, unattended. Our pin is untouched.

### The correction we owe, and it can only live here

**Our lap 12 line 77 says of their escaping layer: *"it just does not cover the
apostrophe."* That is wrong, and it breaks a rule this repository wrote.**

Their §A2 cites `cyanrip_backend.py:699` (`if ch in "\\='" or ch == ":"`), all
eleven `-a`/`-t` sites routing through it, and a test plus two 400-example
`hypothesis` properties covering `'`. We cannot read their source — but the half
that is ours is measurable, and it settles it:

    -t "1=title=Don\'t Stop:artist=SHOULD_LAND:isrc=SHOULD_ALSO_LAND"
      -> title  "Don't Stop"      artist  SHOULD_LAND      isrc  SHOULD_ALSO_LAND

All three fields land. `naming.c:46` honours a generic backslash, so `\'` survives
the pre-splitter — and **our own lap 12 table two lines above the bad sentence
already recorded that**. We had the evidence and asserted past it.

The mechanism is the useful part and it is theirs: the 2026-09-03 argv carries no
escaped apostrophe **because no title in that data contains one**, which our own
§1 said two paragraphs earlier. *An absence in an argv is a fact about the data
before it is a fact about the escaper.* That is `D-03` in their proposed
vocabulary, and it is the round-12 failure arriving from the other direction —
**never state a mechanism in the other side's code without citing where it was
read.**

**A sent lap is immutable, so this file is the only place the correction can
live.** It is not a dispute and needs no lap; it goes in our next one for the
record. Their §A3 was also checked rather than accepted: `musicbrainz.c` sets
`ret = 1` in both branches inside `end:` and returns `ret` at `:390`, so both do
terminate — their concession to us is correct.

### Their §C4 is a class we hit again this session, which is evidence for their §F5

They found a `.pyc` compiled while a file was mutated outliving the restore:
`git diff` empty, sha256 identical, six tests failing. They name our C analogue —
*"the object file, the ccache entry and the build stamp"* — and mark the mechanism
`[INFERRED]` with the reproduction recorded as **FAILED**.

**It happened here on 2026-09-05, making three instances across two projects.** A
fan-out left a mutant in `src/cyanrip_encode.c` and `build/` held the mutant
binary; a targeted `meson test` run against it would have measured a program
nobody wrote. Confirmed by the rebuild recompiling that translation unit. A
full-suite run *does* catch it — `contract_build` hashes `src/` — but a
single-scenario run does not, which is exactly the shape they describe.

So their **§F5**, a numbered shared defect-class vocabulary, has a third data point
before it is written. `D-01` is real, it is cross-language, and neither side found
it by reading.

### What of the audit is prepared for round 16

`docs/AUDIT-2026-09-05.md` §3 holds ~40 leads reported by an agent and **not**
re-derived here; they are labelled at that weight on purpose. A lead is not a
finding. §1's seven verified defects are next-round work, five frozen by S-15.

**And §1.1 is now sharper than when it was written.** Their lap 13's
`HANDSHAKE-SHARED-HASHES` re-attests `seam-commands=7dc31381…`, and our own
`seam-check.py` printed `OK    shared/seam-commands … matches this tree` against
it today. **Both projects have now cryptographically agreed on the stale bytes in
two consecutive laps**, one of them sent after we found the divergence. Nothing is
wrong with the mechanism; §7 is simply the artifact it cannot see into.

### The correction, first — and it is ours, twice over

**Our round 15 lap 3 declared `HANDSHAKE-TESTED: CC-1 NOT MET`. Then we read
Platterpus's 2026-09-03 bundle, decided lap 3 was falsified, and wrote CC-1 IS
MET into this file, into `docs/SETTLED.md` and into the rig README.**

**Lap 3 was right and the correction was wrong.** Their lap 6 §C1 says what
happened to that run: their acceptance script budgeted `10800`s for a
whole-disc `-Z 2 -r 3` that needs about twice that, section F timed out at
`10800.1`s, and the ARCHIVAL section downstream produced no evidence at all. A
run whose archival section produces nothing is not a pass; it is a run that did
not happen.

**What we did is the scope error this project names in as many words.** Two
whole-disc rips inside that run completed cleanly, and we verified them
properly — `Ripping errors: 0`, `14 of 14 tracks`, `Log FUN512` intact, `-Y`
exit 0 on all seven logs. Then we called that the acceptance pass. *"I verified
the list you sent" is not "I verified your inventory."* The rips were verified;
the pass was not.

**A second thing we held and did not use.** Lap 5 (withdrawn unsent) declared
`HANDSHAKE-PEER-PIN: unknown` for `0.6.34` and asked them for it. The bundle's
own per-rip JSON carries `generator.build_fingerprint: dba2ab2` — we printed
that field while reading the bundle. Their lap 5 confirms `0.6.34 = dba2ab2`
independently.

**And lap 3 is still on the wire and still says `platterpus/0.6.33` at
`0a69732`.** Their half has since moved to `0.6.37` at `f3b60a0`, declared by
them out of turn and with the movement labelled as such. A sent lap is never
edited; this is the interim record and the next lap is the formal one.

### What the 2026-09-03 session DOES establish

Platterpus `0.6.34` drove **`978f9b0`** — the round-15 pin, `0.9.4-rc2+platterpus.11` —
on the PIONEER BDR-209D over the 14-track disc. Filed at
`docs/rig-2026-09-03-978f9b0/`, byte-exact, with `SHA256SUMS`.

| | |
|---|---|
| whole-disc rip | `Tracks to rip: all`, `Ripping errors: 0`, `Rip completed:  yes (14 of 14 tracks)` |
| logs | seven, **all verifying `-Y` exit 0** against a *later* build |
| AccurateRip | 12 of 14 exact, 2 matched an offset-variant pressing |
| pregap | 13 × `sub-channel (not signalled by TOC)`, track 1 `lead-in` |

**Four things came off the never-run list**, all from the artifacts:

- **The abort footer and a diagnosed non-zero exit, together.** `-N -l 1` exited
  **1** having printed `Offset is unset!…` at column 0, then
  `Rip completed:  no (aborted, 0 of 14 tracks)`. It also **settles one `goto end`
  row by running it**, which is what P5's legend said those rows needed.
- **`Secure re-read:  did NOT converge after 3 reads (repeat limit hit)`** — the
  non-converged arm, three tracks on each whole-disc rip.
- **The plural `Read stalls:` rendering**, `5 reads exceeded 10s`.

Still untouched by any run: C2 (the drive reports it unsupported), `-f`, damaged
media, CD-TEXT from a physical disc, and `-x` alone on a drive that goes on to rip.

### The defect that run found, and it is ours

`session/DIAGNOSTICS.txt` records thirteen `[error]` entries, recurring on

    [error] ripper.fatal_message
      Done; (no matches found, but hit repeat limit of 3)
      tool: cyanrip

against a rip whose own report reads `status: success`, `ripper_exit_code: 0`,
`14 of 14 tracks` and `health_status: No errors occurred` — beside
`error_count: 5`. In our log that string sits at lines 222, 305 and 387 and each
is **immediately followed by `Track N ripped and encoded successfully!`**.

**`PROVIDER-CONTRACT.md` P5 listed it, under a heading reading *"Every string
reachable on a failure path"*.** It was there on the strength of `goto
finalize_ripping` and nothing else — no failure exit in the search window, no
diagnostic wording — and `finalize_ripping:` is the ordinary continuation, which
flushes encoders and falls into that success line. **The contract is the API, so
this is our defect** whatever else contributed to the consumer's reading; saying
more would be a claim about code we cannot read.

**Fixed at `896a80a`.** A bare `goto` is no longer treated as failure evidence.
The seven rows in that state moved to **`P5a` — "Strings this document does NOT
classify"**, not established in either direction, which is the only claim the
generator can support. Two of the seven were the *convergence* line and the loop
that echoes the cue sheet. A second defect in the same section, same cause: the
summary said `128 distinct strings` above a breakdown totalling **114**, because
it iterated a hardcoded tuple of class names — so three classes were counted in
the total and named in no line a reader could see. Both pinned by
`contract_fatal_inventory`, revert-proved three ways.

**`src/` is unchanged.** The source anchor is unmoved and the binary reads discs
exactly as `978f9b0` does; what moved is a document a consumer parses.

### What a consumer should do about it

If you classify our messages from P5, **re-read it**. `Done; (no matches found,
but hit repeat limit of N)` and `Done; (N out of M matches for current checksum
X)` are not errors — they are the two arms of the secure-re-read outcome, and the
second is the *success* arm. Neither is in P5 any more.

## Releases — read the channel, never the version string

**`0.9.4-rc2+platterpus.11` is a STABLE release.** The `-rc2` is upstream's own
string, copied verbatim because we may not mint in `cyanreg/cyanrip`'s namespace;
the part that advances is `+platterpus.N`, which SemVer says MUST be ignored for
precedence. **A check that reads the shape of the version will call this a
pre-release, and it will be wrong.** Order by `release_seq`, read the `channel`
column of `release-manifest.json`.

**There is no tag.** Tag pushes are `HTTP 403` from the environment this is built
in, and `git ls-remote --tags origin` returns nothing. No release of this fork has
ever been reachable by tag. The commit SHA and the manifest row are the whole
identifier.

| field | value |
|---|---|
| **stable version** | `0.9.4-rc2+platterpus.11` |
| **stable commit** | **`978f9b0`** |
| stable build tag | `platterpus-fork-g978f9b0` |
| stable install | `https://github.com/rmccann-hub/cyanrip/archive/978f9b0.tar.gz` |
| stable `release_seq` | 21 |
| stable authorised by | handshake round 14, closed `GO`/`GO` on `d9c058c` / `b524936` |
| | |
| **beta version** | `0.9.4-rc2+platterpus.11` |
| **beta commit** | **`978f9b0`** |
| beta build tag | `platterpus-fork-g978f9b0` |
| beta install | `https://github.com/rmccann-hub/cyanrip/archive/978f9b0.tar.gz` |
| beta `release_seq` | 21 |
| beta authorised by | handshake round 14, closed `GO`/`GO` — same build as stable |

`beta` resolves to the newest row of *any* channel, so opting into pre-releases
can never move a user backwards. Both channels resolve to `978f9b0`; there is no
separate beta to take.

**`+platterpus.8` (`796df32`, seq 18) is superseded and should not be installed.**
It is still in the ledger, because the ledger is append-only and a published build
is a fact, but no channel resolves to it any more.

Build command: `meson setup build -Ddeclare_released=true && ninja -C build`.

`release-manifest.json` is the only mechanism to install from and it is what
resolves these; this table is a human-readable copy of it and the test exists
because a copy rots.

**No release is coming while round 15 is open.**
`tools/release-gate.py --release-gate` exits 1 on this tree and names round 15,
which is correct and is not being overridden. Work has landed on
`platterpus-fork` since the pin — all of it documentation, tests and tooling,
none of it in `src/`.

## Round 15

| | |
|---|---|
| **opened** | our lap 1, on the released pair rather than a test pin |
| **close condition** | **one, fixed at lap 1 under S-13: CC-1**, a hardware acceptance pass on the released pair |
| **pin** | `978f9b0`, unmoved all round. No test pin; `none` is declared, which is an answer and not a build |
| **their laps 4–9** | all `OPEN`, all transcribing our `GO`. Laps 4–7 arrived in one envelope, three of them late; their half moved `0.6.33` → `0.6.34` → `0.6.36` → `0.6.37`, each move declared, and has not moved since lap 7 |
| **our lap 3** | `GO`, sent. Its `HANDSHAKE-TESTED` was right; our reading of the bundle was not |
| **our lap 8** | `GO`, sent. Accepts `0.6.37` at `f3b60a0` as the app half and corrects our own CC-1 claim |
| **our laps 10 and 12** | both `GO`, sent. Lap 10 named 16 P5 rows; lap 12 §3 corrects eight of them — each is followed immediately by `goto end`, so the contract's own `records and CONTINUES` was right and our lap was not |
| **our lap 12 pre-commit** | S-18: **`GO` on `978f9b0` unless their run finds a defect in it.** Binding, and conditioned on their run — the 2026-09-05 audit's findings do not release it |
| **next** | **nothing from us.** Lap 12 declares `HANDSHAKE-NEXT-LAP: none owed`; the next thing across the seam is their run's result. Both pre-commits are conditional on it |

**CC-1 is NOT met.** Their four laps say so in every `HANDSHAKE-TESTED`, and the reason is theirs and named: the acceptance script's section F was under-budgeted, and `0.6.36` could not have passed either for a second reason they found afterwards. Our §9 pre-commit stands — our next lap is `GO` unless their pass fails on a cause that is ours. The one cause that was ours, the P5 misclassification, is fixed and does not touch the pin.

### The digest methods no longer differ — seven consecutive agreeing values

Lap 2 declared `a1ff77af1fd6e3cb over 1` where we derived `c8fa5d93d9af5a20`:
same population, different construction. Lap 3 §3 shipped our full spec and
asked them to adopt one or tell us to adopt theirs.

**They adopted ours and built it independently** (`scripts/round_digest.py`),
having first reproduced both of lap 2's numbers. Every value since re-derives
here exactly, in both directions:

| lap | declared | |
|---|---|---|
| theirs 4 | `1ad28e7744de3d6b over 3` | reproduces |
| theirs 5 | `ddc0d8a741f76b60 over 4` | reproduces |
| theirs 6 | `09268d7203773872 over 5` | reproduces |
| theirs 7 | `60a7c64dc252b1fa over 6` | reproduces |
| **ours 8** | `44e14b452950ebb0 over 7` | **they reproduce it** — their lap 9 §B2 |
| theirs 9 | `35b861f25abfa69c over 8` | reproduces |

**Two implementations of one written spec, agreeing on six consecutive values,
neither having read the other's code.** Their §B2 makes the point that matters:
two implementations agreeing is weak evidence when they share an ancestor and
strong evidence when they do not. These do not.

The allowlist entry in `tests/release_gate.py` stays pinned to lap 2's declared
value, because lap 2 is immutable and was computed by the old method.

### The process reform — 2026-08-26, on the maintainer's instruction

Round 14 ran to nineteen laps with every rule followed, which is round 7's failure
repeated. **Cut: §J as a requirement, acknowledgement laps, "send a file even when
nothing changed", and findings written up in laps.** Kept: every rule about
evidence. **One file per exchange and it is the lap** — the repository is the
transport, and a test does not travel, its specification does.

**The measure is lap count and round 15 is at 3.** `docs/SETTLED.md` is the index
that stops facts being re-derived, and `tools/check-settled.py` runs every row's
check.

---

## What we know about their side, and how we know each part

Separated by provenance, because these are different strengths of claim.

| | |
|---|---|
| `0.6.34` is what ran on 2026-09-03 | **measured**, from `Consumer:` in every log we hold |
| `0.6.33` at `0a69732` is their round-15 release | **read from their lap 2 §B** |
| `0.6.34`'s commit | **unknown.** Nothing we hold names it; the `Consumer:` string carries no SHA |
| their `0.6.33` banner reads `platterpus 0.6.33 (0a69732)` | **UNVERIFIED.** Lap 3 said the next bundle would answer it. It does not — the bundle is `0.6.34` |
| `0.6.34` treats `978f9b0` as `unapproved` | **measured**, from their JSON: *"NOT the build this Platterpus was verified against (platterpus-fork-gd9c058c)"* — which is round 14's pin, so the field is right and round 15 is what changes it |
| their `FORK_PIN` is `ddf7ac3`, unmoved | **read from their round-14 lap 7 §W2** |
| **`0.6.22` NEVER EXISTED** | **read from their standing status**, which corrects their own lap 4 |

**`session/DIAGNOSTICS.txt`'s banner names `+platterpus.10` / `d9c058c` while
every rip in that bundle was made by `+platterpus.11` / `978f9b0`.** Not a defect:
the banner names the **approved** pair, not the running one. Checked before it was
written down, because the shorter reading was "their diagnostics are stale".

### Where their statuses are filed

`docs/handshake/inbound/status-2026-08-21-v0.6.21.md`,
`status-2026-08-21-v0.6.23.md` and `status-2026-08-24-v0.6.23.md`. All three, kept
dated, even though *their* rule is to rewrite in place.

**The last two share a version and differ in date, which is the whole argument for
keeping both.** Same declared version, two different claims about the world. Under
their own rule the first no longer exists on their side; under ours it is evidence
and is kept. **The date in those filenames is the one the document declares, not
the day we received it**, and the two differ.

Neither declares a wire header, so no enumerator can count them — and
`test_a_standing_status_is_never_counted_as_a_lap()` executes that rather than
asserting it, including the case a rename would hit.

## Upstream: one commit inbound, deliberately not merged

Upstream moved on 2026-08-24: `f8ebf48`, *"src/musicbrainz: retry queries when
busy"*. **Our mirror is synced; `platterpus-fork` does not contain it.**

It adds two log lines — `Retrying in %_ seconds (attempt %_ out of %_)...` and
`MusicBrainz lookup failed, try again later,` — **neither of which can appear in a
Platterpus rip**, because they pass `-N` and `-N` disables the lookup entirely.
Recorded anyway, because a log line entering our contract is handshake material
whether or not the one consumer we have can reach it. The analysis is
`docs/upstream/sync-2026-08-24-mb-retry.md`.

**Three defects of ours are verified as present upstream and not yet contributed
back**: the signal-handler deadlock, SIGTERM unhandled, and the completion-footer
skip. Each has its re-check in `docs/SETTLED.md`.
