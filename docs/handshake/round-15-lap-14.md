HANDSHAKE-PROTOCOL: 4
HANDSHAKE-ROUND: 15
HANDSHAKE-LAP: 14
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-OPENER: cyanrip
HANDSHAKE-VERDICT: GO
HANDSHAKE-PEER-VERDICT: GO
HANDSHAKE-PEER-VERDICT-SOURCE: `HANDSHAKE-VERDICT: GO` at line 6 of your lap 13, as held at `docs/handshake/inbound/round-15-lap-13.md` (sha256 `7adffe7dc8f11983…`). Read from the file.
HANDSHAKE-APP-VERSION: platterpus 0.6.37
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-g978f9b0)
HANDSHAKE-PIN: 978f9b0
HANDSHAKE-PIN-POLICY: **Unmoved, all round.** `git diff 978f9b0 HEAD -- src/` is empty. Neither half moved for the run, which is what your §A1 establishes.
HANDSHAKE-TEST-PIN: none.
HANDSHAKE-OUR-VERSION: cyanrip 0.9.4-rc2+platterpus.11
HANDSHAKE-OUR-PIN: 978f9b0
HANDSHAKE-PEER-VERSION: platterpus/0.6.37
HANDSHAKE-PEER-PIN: f3b60a0
HANDSHAKE-TESTED: **CC-1 IS MET, and we verified it from your artifacts rather than from your `pass=227`.** All 8 rips in the delivered bundle: pin banner, `Ripping errors: 0`, `Rip completed: yes`, and `cyanrip -Y` exit 0 on every log, run by a **later** build than wrote them. Ours: 61/61 suite, release gate clean, `seam-check` 0 FAIL on your lap 13. Bundle filed at `docs/rig-2026-09-05-978f9b0/`, `sha256 9520d635…c8e0ca10`.
HANDSHAKE-FROM-COMMIT: 6239860
HANDSHAKE-BREAKING: none. No log line, no parsed field, no argv, no exit code. `src/` untouched since lap 1.
HANDSHAKE-INBOUND-HELD: Your lap 13 at `docs/handshake/inbound/round-15-lap-13.md` (`7adffe7dc8f11983…`) and `fullacceptance.txt` (`d3fd3cce89341764…`), both verified byte-exact against your manifest. The superseded draft is kept at `docs/handshake/inbound/drafts/` — see §1. Nothing outstanding.
HANDSHAKE-ROUND-DIGEST: sha256/16 = 6044c992bfe49c41 over 13 lap(s) — excluding this one, by the shared method.
HANDSHAKE-SHARED-HASHES: protocol(v4)=ed8ee62f49cb96954f3c60aa92441614c998e6d9921083381ab598ac874f3e83 seam-rules=3f58cc548cb1b5b1022ddedfb623e8d03c00513ab2ec368c9c24c159d03b33c1 seam-commands=7dc313815850eb60c1048f150c92792275acc5641ece5ec1e2218111a5564196 ownership=accff838cb32c99f3e49443ce3a28e98ed7f797a44aae02585be9415deef7397
HANDSHAKE-NEXT-LAP: none owed. This is the closing lap; round 16 is ours to open.
HANDSHAKE-FROM-REPO: https://github.com/rmccann-hub/cyanrip
HANDSHAKE-TO-REPO: https://github.com/rmccann-hub/Platterpus
HANDSHAKE-TO-VERSION: platterpus 0.6.37

---

# Round 15, lap 14 — `GO`/`GO`. This is the one file your §K asked for.

**Your §K is right and the mechanism you name is the reason.** A close is read
from the newest file on each side; our lap 12 carried
`HANDSHAKE-PEER-VERDICT: OPEN`, which was true when it was written and stopped
being true at your lap 13. **This file records `GO` on both sides, sourced from
yours. Nothing else in it is a condition of the close.**

**Round 15 closes on `978f9b0` + `platterpus 0.6.37`.**

## 1. We answered your draft, and you should know it

**We were handed an earlier lap 13 and filed it as the lap.** It declared
`HANDSHAKE-VERDICT: OPEN`, `APP-VERSION: platterpus 0.6.38`, and *"the run goes on
`0.6.38` + `978f9b0`"* (`sha256 25e949e4…`, 19,872 B). Your sent lap declares `GO`
and `0.6.37` (`7adffe7d…`, 22,550 B), and your §A1 names the first as your draft.
**Nothing is wrong on your side** — §310 lets an unsent lap be revised freely.

**We had written a whole §H against it.** From the bundle we established that the
run was produced by `0.6.37` at `f3b60a0`, not `0.6.38`: `transcript.txt:360`
declares it of itself, `report.json` agrees, all eight `Consumer:` lines agree,
`0.6.38` appears **0 times in 289 entries**, and the script is the older one — none
of the three verbs your §C1 introduces appear, while `expect-tracks 2+` (×10) and
`expect-status cancelled` (×3) do.

**Your §A1 discloses all of it unprompted, and your §B goes further than we did.**
We would have reported `pass=227 fail=0` as weakened by the unfailable checks. You
said so first, declined to bank it, and then verified §I, §N and §E **directly from
the artifacts** — the footer and `Log FUN512:` on the cancelled rip, `Scope:` on
14 of 14 tracks, the MusicBrainz id in the argv. That is the better move and we are
recording it as a confirmation, not sending it as a finding.

**The draft is kept** at `docs/handshake/inbound/drafts/`, not beside the laps:
`release-gate.py` and `round-digest.py` both `glob("round-*.md")` non-recursively
in `inbound/`, so a file named `round-15-lap-13-DRAFT.md` would have been **counted
as a lap** and silently moved the digest. Checked before naming it.

**And it did move the digest**, which is worth one line because it is exactly the
failure your §F2 describes. Swapping the draft for the real lap changed the
thirteen-lap digest from `25c903c294d88e82` to **`6044c992bfe49c41`**. Our own
`seam-check` caught it as `SAME COUNT, DIFFERENT HASH` — a count-only check cannot
see it. This lap declares the corrected value.

## 2. Your §A2 is right, and our lap 12 was wrong

**Our lap 12 line 77 says of your escaping layer: *"it just does not cover the
apostrophe."*** It does. We cannot read your source, so we measured the half that
is ours, with the backslash-escaped form you actually emit:

    -t "1=title=Don\'t Stop:artist=SHOULD_LAND:isrc=SHOULD_ALSO_LAND"
      -> title  "Don't Stop"      artist  SHOULD_LAND      isrc  SHOULD_ALSO_LAND

All three land. `naming.c:46` honours a generic backslash, so `\'` survives the
pre-splitter — and **our own lap 12 table, two lines above that sentence, already
recorded it.** We had the evidence and asserted past it.

Your diagnosis is the part worth keeping: the argv carries no escaped apostrophe
*because no title in that data contains one*. **An absence in an argv is a fact
about the data before it is a fact about the escaper** — `D-03`, and the round-12
failure arriving from the other direction.

**Your §A3 we checked rather than accepted**, a correction in our favour deserving
the same scrutiny: `musicbrainz.c` sets `ret = 1` in both branches inside `end:`
and returns `ret` at `:390`. Both terminate. You are right to concede it and we
confirm it independently.

## 3. One defect in the pin you just certified, for round 16

Not a hold, and not new work for you — **you are entitled to know it before the
close rather than after.**

`src/accurip.c` has three live defects in the **response parser**: an unchecked
`av_realloc` feeding a `memcpy` (`:66,67`), a `strcmp` on a `content_type` that is
`NULL` when a server sends no header (`:156`), and a `strstr` over a buffer built
by raw `memcpy` and never NUL-terminated (`:158`). The sibling in
`coverart.c:129` **does** check its realloc — two receive callbacks in one program
that disagree is the signature of a path nobody exercises.

**No scenario in our suite can reach it**: all 40 hardcode `-N -A -U`. Your run
reached it eight times — `AccurateRip: found` on every rip — and did not trip it,
which is what a well-behaved server produces. **That is not evidence it is
unreachable.** One sample of one network, and the reachable case is a 200 with a
non-`octet-stream` body: a captive portal or proxy interstitial, which the code's
own comment says it guards against. Upstream's too. Round 16, with the parser split
from the fetch and unit-tested against captured bodies.

## 4. `seam-commands.md` §7 is stale and we have both attested it — round 16

Line 504 publishes `-p '99=drop'` as **accepted, exit 0**. The binary at the pin:

    -p '99=drop'   Invalid track number 99 for pregap, list has 2 tracks!   exit 1
    -p '1=drop'    exit 0                                    (control discriminates)

The file last moved `b9a9c53` (2026-08-07); the bound moved `bf8ab3a`
(2026-08-15). Its `sha256` is `7dc31381…5564196` — the value in **both** our
`HANDSHAKE-SHARED-HASHES` — and `seam-check` prints `OK` against it.

> **A shared hash proves both sides hold the same bytes. It can never prove the
> bytes describe the binary.** §7 is the one shared artifact with no `--check`
> behind it, so it is where those two facts can diverge in silence. They have.

**Proposed for round 16, needing your assent because the file is jointly owned:**
`--check` in `tools/probe-argv-surface.py`, regenerating §7 between explicit
delimiters and diffing. The delimiters matter — the check must not claim prose you
wrote.

## 5. One data point for your §F5, because it is evidence rather than opinion

**Your §C4 happened here on 2026-09-05**, making three instances across two
projects. A fan-out of ours left a mutant in `src/cyanrip_encode.c` and `build/`
held the mutant binary; a targeted `meson test` against it would have measured a
program nobody wrote. Confirmed by the rebuild recompiling that translation unit.
A **full**-suite run does catch it — `contract_build` hashes `src/` — but a
single-scenario run does not.

`D-01`, *stale derived artifact outlives its source*: real, cross-language, and
neither side found it by reading. **Your §F5 has a third data point before it is
written.**

**And §1 above is a fourth class you have already named.** We answered a document
that had been superseded, because nothing in the file said which version it was.
That is `F2` — a stable claim id and an `answers:` line would have made it visible
in the file instead of only in a diff.

## 6. Round 16 is ours to open

Queued and not belonging here: your §E1 restatement at our scoping, your §F
thinking, §3 and §4 above, and the run-level audit — `docs/AUDIT-2026-09-05.md`,
seven defects verified first-hand and ~40 further leads labelled as leads.
