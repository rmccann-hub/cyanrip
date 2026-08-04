# Release plan — the first stable `+platterpus.5`

*Written 2026-08-04. **A plan, not a release.** Nothing here has been executed
and nothing should be until the conditions in §1 are met. `HANDSHAKE-PIN` still
points at `5bc654d`; the version number has not been bumped and must not be.*

The user's instruction was to get ready for a non-beta release and to plan it,
not to roll it. This file is that plan, so that "we decided to wait" and "nobody
got to it" stay distinguishable.

---

## 0. Where things actually stand

```
production pin      5bc654d      0.9.4-rc1+platterpus.4        <- what a consumer builds today
test pin            9003e6f      …+platterpus.5-beta.1         <- what the rig session installs
tip                 e08281b      (unreleased work on top)      <- this plan's subject
round 7             OPEN, verdict HOLD, lap 8
release gate        --release-gate exits 1; --prerelease exits 0
tests               26/26
```

**The beta the rig is testing does not contain the work in §2.** `9003e6f`
predates all of it. Anything the rig session finds is evidence about
`9003e6f`, and this plan must not quietly claim otherwise.

---

## 1. What has to be true before a stable release, in order

Each step depends on the one before it. This is the ordering from `CLAUDE.md`,
instantiated for this release.

**1a. The rig session runs, on the pinned pair.** cyanrip `9003e6f` and
Platterpus `v0.6.4b1`. Its outstanding items are H9, H10, H12, T9, T12, T13,
with stdout captured for every invocation. Nothing below can start until its
artifacts exist, because `HANDSHAKE-TESTED` cannot be filled from anything else.

**1b. A lap carrying the rig results, and a lap carrying §2.** These are
separate claims and should not be merged into one file: the rig is evidence
about `9003e6f`, and §2 is a change set they have not seen. If §2 ships in the
same lap, say plainly which findings apply to which commit.

**1c. Platterpus verifies §2 against their real parser.** Specifically the four
observable changes in §3 — a new block in the log, a new summary line, a new
flag, a new output file. Their verification file comes back with a declared
`HANDSHAKE-PEER-VERDICT`.

**1d. The round closes affirmatively.** All seven fields present, transcribed,
not inferred:

```
HANDSHAKE-VERDICT: GO
HANDSHAKE-PEER-VERDICT: GO
HANDSHAKE-OUR-VERSION / HANDSHAKE-OUR-PIN
HANDSHAKE-PEER-VERSION / HANDSHAKE-PEER-PIN
HANDSHAKE-TESTED: <what ran, on which pair>
```

`tools/release-gate.py --release-gate` must exit 0. **If it says no, the answer
is no.**

**1e. Only then**: bump to `0.9.4-rc1+platterpus.5`, write the `Changelog.md`
entry from the Unreleased section, regenerate `PROVIDER-CONTRACT.md` and both
golden references at the new version, and announce the pin as a **commit SHA**.

---

## 2. What the release would contain, beyond `+platterpus.4`

Everything in the beta (`Changelog.md`, `…-beta.1`), plus the error-reporting
work in the Unreleased section. In one sentence each:

| | |
|---|---|
| Pre-log output replayed into the logfile | a refusal's reason no longer depends on when it fired |
| libcdio's messages routed through ours | it was exiting the process with a message we never saw |
| genopt's messages routed through ours | every argument-parse error reached stdout only |
| `Read stalls:` in the disc summary | the rig's two three-minute stalls left no trace in any log |
| `-j` / `--diagnostics <path>` | a record for the runs that open no logfile at all |
| contract un-truncated through `PRId64` | two P2 lines were published ending in a bare `%` |
| contract's "reaches logfile" corrected | it was a yes/no that the replay made false |

Every behavioural item above is revert-proved with the build confirmed green
during the revert, individually rather than in a batch.

---

## 3. What Platterpus has to check — the observable surface

**This is the part that decides whether the release is safe**, and it is
larger than a log-text delta because two of the four are new surfaces rather
than changed ones.

**3a. A new delimited block in the logfile.** After the header's trailing blank
line and before `Gaps:`:

```
--- output before this log was opened ---
Checking <image> for cdrom...

Opening drive...
Release ID unavailable, cannot search Cover Art DB!
--- end of pre-log output ---
```

The header block above it is **byte-identical** to before, deliberately: the
first version flushed at log-open and pushed the version banner to line 8,
which would have broken the one reliable answer to "is this the fork?". A test
now pins the banner in place. The question for Platterpus is whether a parser
that reads sections positionally, rather than by label, is disturbed by a block
appearing between the header and `Gaps:`.

**3b. One new line in the disc summary**, between `Ripping errors:` and
`Rip completed:`, in one of three forms:

```
Read stalls:    none (no read exceeded 10s)
Read stalls:    2 reads exceeded 10s; longest 187s (track 4, LSN 45231)
Read stalls:    unknown (stall reporting disabled with -k 0)
```

`none` and `unknown` are different claims and must not be collapsed.

**3c. A new flag, `-j` / `--diagnostics <path>`.** Flag count 40 → 41. **This is
the `--consumer` near-miss again**: an argv-surface test that pins the flag
table will refuse a build carrying a flag it does not know, and every
availability probe reads a non-zero exit as "not installed". Add it to the
table *before* the pin moves, not after.

**3d. A new output file, but only when asked for.** `-j` is off by default and
deliberately takes a path rather than deriving one, so it cannot collide with a
track and never appears in the output directory uninvited. A consumer asserting
the exact set of files a rip produces is unaffected unless it passes `-j`.

Schema is `cyanrip-diagnostics/1`. `docs/golden-reference.diagnostics.json` is
the reference to write a parser against. Two properties are load-bearing and
should be read as commitments, not implementation detail:

- **No severity is claimed**, and `messages_are_classified: false` says so.
  `cyanrip_log()` carries no severity, and classifying by wording is the defect
  the contract's fatal inventory already shipped once. Judge a rip by
  `exit_code`, `ripping_errors`, `tracks_completed` and `read_stalls`.
- **`null` is used where a fact is unknown, never omission.** `rip: null` means
  no disc was ever opened; `exit_code: null` means the process left by a route
  that produced no code (libcdio's `abort()` on `CDIO_LOG_ASSERT`).

---

## 4. What this release still would not verify

Stated so a green suite cannot imply coverage. **None of this is retired by any
fixture**, and the release must say so rather than letting 26/26 speak for it:

- **The MMC sub-channel read**, so a real `Pregap source: sub-channel` success.
- **`-x` on a real drive.** It has never produced a measurement on hardware.
  Any number it prints is unverified.
- **C2 reporting, `-f` offset autodetection, damaged media**, and CD-TEXT from
  a physical disc (a different code path from the image parser).
- **The exit-code fix.** Its paths are hardware-gated; the `exit_codes`
  scenario's revert-proof came back green and the scenario's docstring says so.
- **A non-zero `Read stalls:` count on real hardware.** `tests/stall.c` proves
  the accounting on synthetic stalls — count, longest-wins, and the three
  states — but only a drive can prove that a stalled *drive* is what leaves a
  read outstanding.
- **libcdio's `CDIO_LOG_ASSERT` path.** The `CDIO_LOG_ERROR` path is exercised
  by a fixture; the assert path is not, and it is the one that `abort()`s.

---

## 5. Version numbering, restated

`0.9.4-rc1` is upstream's and is copied verbatim. **`N` in `+platterpus.N` is
the only number that moves**, and it moves by one. Never mint an identifier in
upstream's namespace — `0.9.4-rc3` was written once and withdrawn, because
upstream can tag that string and then two trees answer to one name.

The beta already spent `+platterpus.5` as `…+platterpus.5-beta.1`. The stable
release is `0.9.4-rc1+platterpus.5` — the same N, without the pre-release
suffix, which is the ordering SemVer gives for free and the only part of our
version string that is orderable at all. (The build-metadata part is ignored for
precedence, which is why `docs/UPGRADE-CHANNELS-PLAN.md` declares a channel and
a sequence rather than parsing the human-facing string.)

**No tag.** The git proxy refuses tag pushes with `HTTP 403`, re-probed each
release. **The commit SHA is the identifier**, and a `release/*` marker branch
is the only named ref this environment can publish.
