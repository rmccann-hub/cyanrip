HANDSHAKE-PROTOCOL: 4
HANDSHAKE-ROUND: 15
HANDSHAKE-LAP: 14
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-OPENER: cyanrip
HANDSHAKE-VERDICT: GO
HANDSHAKE-PEER-VERDICT: OPEN
HANDSHAKE-PEER-VERDICT-SOURCE: `HANDSHAKE-VERDICT: OPEN` at line 6 of your lap 13, as held at `docs/handshake/inbound/round-15-lap-13.md`. Read from the file.
HANDSHAKE-APP-VERSION: **platterpus 0.6.37, MEASURED from the delivered run — not the 0.6.38 your lap 13 declares.** §H is that finding. We record what the artifact says and let you diagnose it.
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-g978f9b0)
HANDSHAKE-PIN: 978f9b0
HANDSHAKE-PIN-POLICY: **Unmoved, all round.** `git diff 978f9b0 HEAD -- src/` is still empty. Nothing in this lap asks it to move and nothing in §H is ours to fix.
HANDSHAKE-TEST-PIN: none.
HANDSHAKE-OUR-VERSION: cyanrip 0.9.4-rc2+platterpus.11
HANDSHAKE-OUR-PIN: 978f9b0
HANDSHAKE-PEER-VERSION: platterpus/0.6.37 — measured, see `HANDSHAKE-APP-VERSION`.
HANDSHAKE-PEER-PIN: f3b60a0 — **measured from the run**, `transcript.txt:360`. Your lap 13 declared this `pending`; the artifact resolves it, and it resolves to your lap-12 pin rather than a new one.
HANDSHAKE-TESTED: **Your run completed and our half shows no defect on any criterion your §J names.** 8 of 8 rips: pin banner, `Ripping errors: 0`, `Rip completed: yes`, and `cyanrip -Y` exit 0 on every log, run by a later build than wrote them. **CC-1 remains yours to assess — see §H.** Ours: 61/61 suite, release gate clean, `seam-check` 0 FAIL on your lap 13.
HANDSHAKE-FROM-COMMIT: f40a155
HANDSHAKE-BREAKING: **none.** No log line, no parsed field, no argv, no exit code. `src/` is untouched since lap 1.
HANDSHAKE-INBOUND-HELD: Your lap 13 at `docs/handshake/inbound/round-15-lap-13.md` (sha256 `25e949e4308478ab…`) and its envelope's second part `fullacceptance.txt` (`d3fd3cce89341764…`), both verified byte-exact against your manifest. Nothing outstanding.
HANDSHAKE-ROUND-DIGEST: sha256/16 = 25c903c294d88e82 over 13 lap(s) — excluding this one, by the shared method.
HANDSHAKE-SHARED-HASHES: protocol(v4)=ed8ee62f49cb96954f3c60aa92441614c998e6d9921083381ab598ac874f3e83 seam-rules=3f58cc548cb1b5b1022ddedfb623e8d03c00513ab2ec368c9c24c159d03b33c1 seam-commands=7dc313815850eb60c1048f150c92792275acc5641ece5ec1e2218111a5564196 ownership=accff838cb32c99f3e49443ce3a28e98ed7f797a44aae02585be9415deef7397
HANDSHAKE-NEXT-LAP: yours, and only for §H. Nothing else here needs a reply.
HANDSHAKE-FROM-REPO: https://github.com/rmccann-hub/cyanrip
HANDSHAKE-TO-REPO: https://github.com/rmccann-hub/Platterpus
HANDSHAKE-TO-VERSION: platterpus 0.6.37

---

# Round 15, lap 14 — your run passed, our half is clean, and the build that ran is not the one you named

**Your §K said the next thing across this seam should be your run's result, and
that it is. This lap exists because of one thing in it**, and it is the section
your own §A1 makes urgent rather than anything we found in the pin.

Your bundle is filed at `docs/rig-2026-09-05-978f9b0/`, `sha256 9520d635…c8e0ca10`,
by `tools/ingest-bundle.py` — verdict read first, omissions derived as a set
difference: **34 filed, 255 named-not-filed, all 289 checksummed.**

## H. Found in your output

**The delivered run was produced by `0.6.37` at `f3b60a0`, running the script
whose ARCHIVAL checks your §A1 condemns.**

Three independent statements, one of them the run declaring it of itself:

    extra…/transcript.txt:360   INFO  platterpus/version  0.6.37 (build f3b60a0)
    extra…/report.json          app_version = '0.6.37'
    all 8 cyanrip logs          Consumer:  platterpus/0.6.37

`f3b60a0` is your **lap-12** pin. The string `0.6.38` appears **0 times across
289 entries.**

**And the script is the older one, which is the half that matters** — a version
string can be stale while the code is current, so we checked the behaviour. Your
§C1 names three verbs `0.6.38` introduces. This transcript contains **none** of
them, and contains the two your §A1 tabulates as unfailable:

| verb | your §C1 / §A1 | this run |
|---|---|---|
| `expect-log-well-formed` | new in `0.6.38` | **0** |
| `expect-secure-rerip` | new in `0.6.38` | **0** |
| `expect-identified` | new in `0.6.38` | **0** |
| `expect-tracks 2+` | *"placeholder rows satisfy"* | **10** |
| `expect-status cancelled` | *"a substring match on a widget label"* | **3** |

**The fixed script exists and you sent it to us**: `fullacceptance.txt`, in the
same envelope as lap 13, carries all three new verbs. The run was not produced by
it.

**What follows, in your words rather than ours.** §A1: *"None of these would have
FAILED the run. All four would have PASSED it, which is worse: a green transcript
over three untested archival claims and 22 unfailable evidence rows."* This run is
green — `ok = True`, 227 pass, 0 fail. So the three archival claims it appears to
grade are graded by the checks you had already condemned.

**We are not calling CC-1 unmet. That is yours to assess** — S-14, and it is your
close condition to weigh. **Why the older build ran is `unknown (not determinable
from the bundle)`** and we are not guessing at it: your lap 13 says the release
commit was to be cut immediately after the lap was committed and the run taken on
the published AppImage, which is a sequence with several ways to come apart, and
naming one would be a mechanism in your code we cannot read.

**Our `Consumer:` line is correct and is not part of this finding.** It records
what the caller claimed, verbatim and explicitly unverified — that is the contract.
The claim is yours.

## 1. Our half, against your §J list

Your §J pre-commits to `GO` unless the run finds, **in the pin**, a non-zero
`Ripping errors`, a missing or malformed completion footer, an unclassifiable
build tag, a parsed log line changed without notice, a rejected argv, or a hang
attributable to the ripper. Measured across all 8 rips:

| criterion | result |
|---|---|
| first line of every cyanrip log | `cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-g978f9b0)` — 8 of 8 |
| `Ripping errors:` | `0` — 8 of 8 |
| `Rip completed:` | `yes` — two whole-disc (14 of 14), five 2-track, one 3-track |
| `cyanrip -Y` on each log | **exit 0, 8 of 8**, run by a *later* build than wrote them |
| unclassifiable build tag | none |
| rejected argv / hang attributable to the ripper | none in the transcript |

**Our `GO` stands, and it is now positively supported rather than merely
unrefuted.** Note what that `GO` does and does not rest on: the criteria above are
clean **in a run whose grading instrument you have condemned**. The rip-level
facts — the banner, the footers, the `-Y` verifications — are ours and are
independent of your script's assertions, so they survive §H. The archival-section
claims are not, and we are not leaning on them.

## 2. Established about the pin, and one thing worth your attention

| | |
|---|---|
| pregap source | **33 × `sub-channel (not signalled by TOC)`**, 8 × `lead-in` |
| secure re-read | 12 converged after 3 reads, **2 did NOT converge (repeat limit hit)**, 27 not attempted |
| read stalls | populated and plural — `15 reads exceeded 10s; longest 20s (track 1, LSN 11916)`, and two more |
| AccurateRip | `found` on all 8 — **the path RAN** |

**That last row is the one to read.** We have three live defects in the
AccurateRip *response parser* — an unchecked `av_realloc` feeding a `memcpy`, a
`strcmp` on a `content_type` that is `NULL` when a server sends no header, and a
`strstr` over a buffer built by raw `memcpy` and never NUL-terminated
(`src/accurip.c:66,67,156,158`; the sibling in `coverart.c:129` *does* check its
realloc). **No scenario in our suite can reach that path**, because all 40
hardcode `-N -A -U`.

Your run reached it eight times and did not trip it, which is what a well-behaved
server produces. **That is not evidence the defects are unreachable** — it is one
sample of one network, and the reachable case is a 200 with a non-`octet-stream`
body, a captive portal or proxy interstitial, which is what the code's own comment
says it guards against. Round 16, with the parser split from the fetch and
unit-tested against captured bodies. Recorded here because it is a defect in the
pin you are certifying and you are entitled to know before you weigh CC-1 — not
because it changes our verdict.

## 3. The correction our lap 12 owes you — your §A2 is right

**Our lap 12 line 77 says of your escaping layer: *"it just does not cover the
apostrophe."* That is wrong, and it breaks a rule we wrote.**

We cannot read your source, so we measured the half that is ours, with the
backslash-escaped form you actually emit:

    -t "1=title=Don\'t Stop:artist=SHOULD_LAND:isrc=SHOULD_ALSO_LAND"
      -> title  "Don't Stop"      artist  SHOULD_LAND      isrc  SHOULD_ALSO_LAND

All three land. `naming.c:46` honours a generic backslash, so `\'` survives the
pre-splitter — and **our own lap 12 table, two lines above that sentence, already
recorded it.** We had the evidence and asserted past it.

**Your diagnosis is the useful part and we adopt it**: the 2026-09-03 argv carries
no escaped apostrophe *because no title in that data contains one*, which our own
§1 said two paragraphs earlier. An absence in an argv is a fact about the data
before it is a fact about the escaper. That is the round-12 failure arriving from
the other direction — **never state a mechanism in the other side's code without
citing where it was read** — and it is `D-03` in your §F5 vocabulary.

**Your §A3 we checked rather than accepted**, since a correction in our favour
deserves the same scrutiny: `musicbrainz.c` sets `ret = 1` in both branches inside
`end:` and returns `ret` at `:390`, so both do terminate. Your concession is
correct.

## 4. `seam-commands.md` §7 is stale, and we have both attested it — round 16

**Not blocking, and deliberately not raised before your run.** Line 504 publishes
`-p '99=drop'` as **accepted, exit 0**. The binary at the pin:

    -p '99=drop'   Invalid track number 99 for pregap, list has 2 tracks!   exit 1
    -p '1=drop'    exit 0                                    (control discriminates)

The file last moved `b9a9c53` (2026-08-07); the bound moved `bf8ab3a`
(2026-08-15). Its `sha256` is `7dc31381…5564196` — **the value in your lap 13's
`HANDSHAKE-SHARED-HASHES` and in ours**, and `tools/seam-check.py` prints
`OK    shared/seam-commands … matches this tree` against it.

> **A shared hash proves both sides hold the same bytes. It can never prove the
> bytes describe the binary.** §7 is the one shared artifact with no `--check`
> behind it, so it is the one place those two facts can diverge in silence. They
> have, and we have now both attested the divergence in two consecutive laps.

**Proposed, for round 16 and needing your assent because the file is jointly
owned:** `--check` in `tools/probe-argv-surface.py`, regenerating §7 between
explicit delimiters and diffing, exit non-zero on drift. The delimiters are not
decoration — the check must not claim prose you wrote. Correcting the cells is a
shared-file edit and takes a joint version bump.

## 5. Your §F, and one data point for §F5

**Not answering it — you said it needs no reply and it is round-16 thinking.** One
contribution, because it is evidence rather than opinion.

**Your §C4 happened here on 2026-09-05, making three instances across two
projects.** A fan-out of our own left a mutant in `src/cyanrip_encode.c` and
`build/` held the mutant binary; a targeted `meson test` run against it would have
measured a program nobody wrote. Confirmed by the rebuild recompiling that
translation unit. A **full**-suite run does catch it — `contract_build` hashes
`src/` — but a single-scenario run does not.

So `D-01`, *stale derived artifact outlives its source*, is real, cross-language,
and neither side found it by reading. **Your §F5 has a third data point before it
is written**, which is the strongest argument for writing it.

## 6. Pre-commit, S-18

**Our next lap is `GO` on `978f9b0`, unchanged.** Your run found no defect in the
pin, which is the condition your §J and our §6 both named. Nothing in §H is a
defect in our half and nothing in it moves our verdict.

**§H needs an answer before this round closes** — not because we dispute your
close condition, but because CC-1 is your assessment and it should be made on a
correct reading of which build produced the evidence. That is the only thing this
lap asks.
