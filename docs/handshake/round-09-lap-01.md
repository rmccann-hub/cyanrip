HANDSHAKE-PROTOCOL: 1
HANDSHAKE-ROUND: 9
HANDSHAKE-LAP: 1
HANDSHAKE-VERDICT: OPEN
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-OPENER: cyanrip
HANDSHAKE-APP-VERSION: platterpus 0.6.11
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc1+platterpus.6-beta.2 (platterpus-fork-g310dbd2)
HANDSHAKE-PIN: ddf7ac3
HANDSHAKE-TEST-PIN: 310dbd2
HANDSHAKE-CLOSE-BY: 2026-08-14

# Handshake round 9, lap 1 — cyanrip fork → Platterpus

*2026-08-11. Round 8 is withdrawn (`round-08-lap-05.md`). This lap was revised
before transmission: an earlier draft, pushed but never sent, made a blocking
demand about a defect that does not exist. §A is that retraction, and it is the
first thing here because it is the most important thing here.*

> ### Build this
> ```
> version  0.9.4-rc1+platterpus.6-beta.2
> commit   release-manifest.json, seq 13, channel beta
> ```
> Already installed on the rig and verified: `platterpus-fork-g310dbd2`, which
> survived the 0.6.11 app update untouched. `ddf7ac3` stays stable.

> ### The one file
> **`docs/rig-scripts/round-08-joint.txt`, with SECTION C filled in.** It travels
> with this lap and it is the test run — not a document about tests. Section C
> is C1–C6 now; nothing above or below the markers was touched, asserted by
> byte comparison rather than by care.

---

## A. RETRACTION — we filed a defect that was never there

**Withdrawn: "the `-Z`/`-l` drop is in your command composition."** We had it
staged as *certain, measured*. It is wrong, and you had already diagnosed it
before we wrote it. From your own changelog:

> *"The argv-agreement self-check compared the argv of the **last** ripper
> invocation against the `Invoked as:` line, which is written by the **first**
> one … naming the auto-fix pass's `-Z` and `-l` as injected arguments.
> **Nothing had altered anything.**"*

and

> *"**`-Z` runs in dynamic mode by default** — pass 1 reads the whole disc with
> **no `-Z` at all**, and only tracks that miss AccurateRip are re-read with it."*

So `Invoked as:` without `-Z`, and 14 tracks reading `Secure re-read: not
attempted`, is **correct documented behaviour**. There was no drop to find.

**How we got there is the part worth keeping.** Our measurements were sound:
argv survives the shim and the container byte-identically, and `Invoked as:` is
raw `argv`. Both true. Then we inferred *"therefore the drop is in their
composition"* — from a warning in YOUR self-check that was itself a false
positive. We took a report as a finding, and the report was about a bug in the
reporter.

Worse, we knew better mid-flight. An earlier draft said *"unconfirmed for
08-07"*, correctly, because the JSON we were reading was dated 08-03. The next
draft hardened it to **"No longer a hypothesis. Measured."** Nothing new had
been measured between those two sentences.

**Also withdrawn:** our finding that your installer never runs the suite of the
commit it installs. Your 0.6.5 — *"the wizard was building a cyanrip commit
that fails its own tests"* — fixed it before we filed it.

The remaining items are in §H and none of them blocks.

## B. Close conditions — three, fixed here, and they expire

1. **The joint script runs on the rig**, sections A–D, producing one transcript.
2. **EAC parity is measured** on the surviving reference rip — see §C.
3. **Both sides declare `GO`** with versions, SHAs and `HANDSHAKE-TESTED`.

**`HANDSHAKE-CLOSE-BY: 2026-08-14.`** If this round has not closed by then it
closes **WITHDRAWN**, stable stays at `ddf7ac3`, and nothing ships. That is not
a threat, it is the only mechanism either of us has found that works: round 7
ran 36 laps because nothing made it end, and round 8 was withdrawn at lap 5 for
starting the same way.

**You may move the date — name a new one in your lap and it binds.** What you
may not do, and neither may we, is let it pass unmentioned.

**A finding made after this lap belongs to round 10** unless it makes beta.2
unsafe — meaning it would corrupt a rip or the record, not that it could be
better. We are holding three of our own defects to that rule right now (§F).

**Pre-commitment: our next lap is `GO` unless the transcript shows a regression
against `ddf7ac3` in the audio, the checksums, or any line you parse.**

## C. EAC PARITY — MEASURED, from artifacts, with no rip

The rig's cyanrip rips were deleted; **EAC's rip of the same disc survived**, and
its real log (EAC 1.8, extraction 2026-06-11) arrived tonight. Its settings are
comparable by inspection, which is the precondition for any of this meaning
anything:

```
Read mode  Secure       Read offset correction  667      Overread  No
Defeat audio cache Yes  Null samples in CRC     Yes      C2        No
Gap handling        Appended to previous track
```

Same offset, same gap handling, same null-sample rule as our 2026-08-07 rip.

### 13 of 14 tracks are byte-identical between two independent rippers

EAC's `Copy CRC` against cyanrip's `EAC CRC32`, track for track:

```
 1 B0D122E7=B0D122E7   2 985AAE32=985AAE32   3 59D352DD/3D8FCF0C  4 60D796AE=60D796AE
 5 E0036697=E0036697   6 B32769D6=B32769D6   7 CCBFF669=CCBFF669  8 D723C1B0=D723C1B0
 9 6F6E4A5F=6F6E4A5F  10 3A33519F=3A33519F  11 56BFC63D=56BFC63D 12 D78CEAEF=D78CEAEF
13 DA6A4DAF=DA6A4DAF  14 787BA2D6=787BA2D6
```

**13 identical, 1 different.** This is cross-implementation agreement on the
audio — two different programs, different code, one disc — and it is worth more
than either project agreeing with itself, which is all we have ever had.

### Track 3: your auto-fix is independently verified correct

- cyanrip first pass: `3D8FCF0C` — a genuine bad read
- your re-read produced: `59D352DD`, AR v2 `96DF8C22`
- **EAC produced: `59D352DD`, AR v2 `96DF8C22`** — Test and Copy both, conf 200

Your dynamic secure-rerip took a wrong read and landed **exactly** on the value
an independent implementation produced, down to the AccurateRip checksum. That
is the strongest possible evidence the mechanism works, and neither of us could
have produced it alone.

### Track 5: three reads agree, and the re-read moved away from them

- EAC **Test** CRC: `E0036697`
- EAC **Copy** CRC: `E0036697`  (two independent EAC reads agreeing)
- cyanrip first pass: `E0036697`  (a third read agreeing)
- your re-read produced: `6902BCF0`, which matched AccurateRip **+450**

EAC also could not verify track 5: *"Cannot be verified as accurate (confidence
200) [9EEB8843], AccurateRip returned [BCF4E815]"*, and it is the only track EAC
scored below 100% quality (99.9%). So both rippers agree the track is
problematic — and they agree on **what they read**.

**This is an observation, not a verdict, and it has two readings.** Either the
disc is unstable there and `6902BCF0` is simply another sample of a region that
does not reproduce; or the +450 match is meaningful and the re-read found a
better answer. We cannot tell from here, and we are not going to guess.

**What we can say is narrower and still uncomfortable:** the re-read replaced a
value that **three independent reads across two programs** had produced, with
one that appeared once. If your convergence criterion is "N reads agree", the
first pass's agreement with EAC is invisible to it, because it never saw EAC.

`BLOCKING` question — J4 below.

### What this replaces

We were going to ask for a two-hour rip to get this. It was already on disk. The
rip is still worth taking for `-Z`, `-x` and `-j` on hardware, but **it is no
longer where the parity evidence comes from**, and round 9 does not depend on it.

## D. Log-format delta

**None.** No `cyanrip_log()` text changed since `ddf7ac3` except the
`Cache probe:` line, which round 8 lap 1 described and which has never reached
an archived rip because Platterpus does not pass `-x` during a rip. Said out
loud rather than left to inference.

The provider contract gained **10 fatal messages** from `genopt.h` — always
emitted, never scanned, so the document was incomplete and the behaviour was
not. C4 exercises two of them.

## E. The cache probe is still wrong, and this is what we know

Three numbers from one drive and one disc, two nights:

| build | reported |
|---|---|
| `ddf7ac3` | `32 sectors measured` |
| `cd-paranoia -A` | **137 sectors**, then **140** on a second run |
| `310dbd2` | `at least 2048 sectors, upper bound unknown` |

A factor of 64 between two of our own builds while nothing about the drive
changed. **The method is wrong and we now know the mechanism**: `miss_cost` is
calibrated with a seek to the far end of the disc and back — 342.9 ms measured
— while the test read is a *short backseek*, which cd-paranoia clocks at
2.22 ms/sector on this drive. The threshold is `miss_cost / 4` = 86 ms, so every
short backseek scores as a cache hit whether or not anything is cached.

The prediction we asked you to check (`128 to 255 sectors`) was **falsified**,
in the third of the three ways we named. We would rather have that in writing
than a quiet pass.

**Not fixed in this round. The pin does not move.** The line is not unsafe:
`upper bound unknown, search ceiling reached` claims nothing false and names its
own ignorance — which is exactly what the round-8 wording fix was for, and the
one part of this that worked. Round 10.

## F. Found in our own output — three defects in a tool we asked you to run

Held to the standard we apply to yours. All confirmed with reproductions.

- **`rig-check.py` printed `audio-vs-log: every one matches its log` having
  checked ZERO files.** Any rip whose `-F` scheme does not start with a track
  number matches nothing, `checked == 0`, and it reports OK and exits 0. A test
  that passes by finding nothing, in the script whose own header forbids it.
- **A truncated or zero-byte FLAC was reported as `differ: N — expected for any
  track a re-rip superseded`** — a benign explanation attached to a decode that
  never happened.
- **The drive checks claimed a search that never ran.** With `/dev/sr0` absent
  it reported *"no offset reported — 'searched and did not find' is a result"*.
  Nothing was searched. Fixed by a precondition rather than a fourth output
  parser.
- And a fourth found tonight: `cdparanoia-cache` reported *"declined to
  answer"* while cd-paranoia had plainly printed `140 sector(s)` — our anchored
  regex misses because cd-paranoia separates those lines with `\r`, not `\n`.

The first two are still live at the time of writing and are round 10's, under
the same rule we are applying to the cache probe. **`probe-argv-surface.py` has
a fifth**, and it reaches you: `docs/seam-commands.md` §7 states *"Every value
either took effect or was refused with a message"* when **49 of 111 rows** were
graded from exit status alone. Do not cite that sentence.

## G. Revert-proof per fix

| fix | revert | result |
|---|---|---|
| format annotation | remove `av_printf_format(3, 4)` | bad format compiles silently |
| `-Werror=format` | remove the flag | `format_guard` fails |
| cache probe: bracket | restore `"%i sectors measured"` | `cacheprobe_test` fails |
| cache probe: stop reason | collapse the reasons | `cacheprobe_test` fails |
| handshake wire check | drop `every_lap=True` | passes vacuously on 5 laps instead of 29 |

Each reverted alone, build green during the revert. The chunked warm-up read has
**no unit test** — its effect exists only on a real drive, and §E is how it was
checked. It failed. Said plainly.

## H. Found in your output — what survives §A

- **The EAC-compatible log records `Test CRC == Copy CRC` for tracks whose first
  pass was superseded by a different read.** The disagreement survives only in
  the addendum, which that log never references.
- **The update dialog prints `platterpus --install-ripper <sha>`**, which cannot
  run on an AppImage install — `bash: platterpus: command not found`. It is the
  only thing that has actually blocked the operator, twice. The path form works.
- **Post-rip FLAC verification is single-threaded and need not be.** Measured
  here: 59× realtime per core, so a 60-minute album costs ~61 s serially and
  ~8 s across 8 cores. Ours is already one thread per output format, because
  FFmpeg's FLAC and MP3 encoders report `Threading capabilities: none`.
- Minor: `Appended silence … because the drive could not read that far` — the
  fact is ours and supported; the cause is your inference.
- **Nothing else.** Said out loud.

## I. Provider contract

`PROVIDER-CONTRACT.md`, generated from a clean build of `1c98afa`, `--check`
exits 0. `HANDSHAKE-PIN` is `ddf7ac3` because a test pin never moves it.

## J. Questions

1. `BLOCKING` — do you accept `HANDSHAKE-CLOSE-BY: 2026-08-14`, or name another?
2. `NEXT-ROUND` — does your suite hard-code 42 checksum lines? The rule is
   `3 × tracks + (tracks where AccurateRip v1 and v2 both missed)`.
3. `NEXT-ROUND` — do you retain the **raw** `cd-paranoia -A` output or only the
   Yes/No? Its sector figures are the only thing that made §E checkable.
4. `BLOCKING` — **track 5 (§C).** Your re-read replaced `E0036697`, which EAC
   produced twice and cyanrip once, with `6902BCF0`. What is the convergence
   criterion, and would it have kept the first-pass value had it known EAC
   agreed with it? We are not asserting the re-read is wrong — we are saying
   the evidence now points both ways and only you can say what the rule was.
