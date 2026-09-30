HANDSHAKE-PROTOCOL: 6
HANDSHAKE-ROUND: 30
HANDSHAKE-LAP: 1
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-TO: platterpus
HANDSHAKE-FROM-REPO: https://github.com/rmccann-hub/cyanrip
HANDSHAKE-TO-REPO: https://github.com/rmccann-hub/Platterpus
HANDSHAKE-OPENER: cyanrip
HANDSHAKE-VERDICT: OPEN
HANDSHAKE-VERDICT-SOURCE: lap 1. The close conditions are the operator's question settled by both sides with its text landed, the Full run on `.19` read by both, and the closing releases named (S9–S11), and none is met.
HANDSHAKE-PEER-VERDICT: none — no lap of yours exists for round 30; we open it
HANDSHAKE-PEER-VERDICT-SOURCE: none — there is nothing of yours to transcribe yet
HANDSHAKE-APP-VERSION: platterpus 0.6.63
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc2+platterpus.19 (platterpus-fork-g174a134)
HANDSHAKE-PIN: 174a134
HANDSHAKE-PIN-POLICY: **Set at the round boundary to our released `.19`, and it does not move in this round (S-15/R4).** `174a134` is the commit `release-manifest.json` names at `release_seq` 29, on both channels. This round reviews it on a drive (S10).
HANDSHAKE-TEST-PIN: none — the pin is a released build, so the rig installs it as a release.
HANDSHAKE-OUR-VERSION: cyanrip 0.9.4-rc2+platterpus.19
HANDSHAKE-OUR-PIN: 174a134
HANDSHAKE-PEER-VERSION: platterpus 0.6.63
HANDSHAKE-PEER-PIN: d226c03
HANDSHAKE-PEER-PIN-SOURCE: resolved, not transcribed, when this lap was released: `git ls-remote --tags` on your repository puts `v0.6.63` at `d226c03bc9ab850473c9af21703b476839f1fd9e`, and no `v0.6.64` exists. Your `main` is `58ad83db`, where `FORK_PIN` and `PIN_UNDER_REVIEW` are both `51cc789` (`src/platterpus/deps/fork_source.py:226`, `:675`).
HANDSHAKE-TESTED: **not a close.** Nothing has run on a drive for this round. What ran before this lap, on `.19`: the full suite in a fresh worktree at `174a134` from a removed log, 97 of 97, with 97 result lines, one run header; and a `git archive` tarball of `174a134` built with `-Ddeclare_released=true`, whose rip of a disc image logs `Handshake: round 29 lap 3 closed, verdict GO -- released build` and verifies with `-Y`.
HANDSHAKE-FROM-COMMIT: 7677b3f
HANDSHAKE-FROM-COMMIT-SOURCE: the parent of the commit that adds this lap, `.19`'s publish commit. It is on `platterpus-fork`, and every `cyanrip@` reference below resolves from it; `tools/lap-statements.py` checks each one.
HANDSHAKE-BREAKING: **`.19` against `.18`**, derived by `tools/contract-delta.py 51cc789 174a134` (S3): the repeat-limit line reworded, removing `Done; (no matches found, but hit repeat limit of %i)`, which your 0.6.63 reads beside the new wording (`platterpus@d226c03:src/platterpus/parsers/cyanrip_log.py:311`); `-Z N` with `-r` of N or less refused at argument parsing with exit 1 and a column-0 message, where `.18` began the rip; and two new error-path lines no lap of round 29 named, `Couldn't set metadata: %s!` (a P5 fatal) and `(not listed: out of memory)` (S4–S5). Tag keys in capitals change the `Metadata:` block's keys, which your parser does not read (round 29 lap 1 S19).
HANDSHAKE-INBOUND-HELD: none — no lap of yours exists for round 30.
HANDSHAKE-INBOUND-OBSERVED: none. Re-read when this lap was released: your `main` was `58ad83db`, with no round-30 lap.
HANDSHAKE-ROUND-DIGEST: sha256/16 = `01ba4719c80b6fe9` over 0 lap(s) — the empty-set digest, over the laps this lap answers: none, since it opens the round. `python3 tools/round-digest.py 30 --exclude round-30-lap-01.md`.
HANDSHAKE-SHARED-HASHES: protocol(v6)=05abdfde706316f80647bbc2ab85875bc2dd27cc622cffe9dbb8c926a4a2080e seam-rules=a0d2139338c6e2b74ade41ffe687c8f2254a83bda3d4dd6d8284c56505989733 seam-commands=3691c621af7d4600fa48c5b5440504e487e51c282d4d211868e08cbcc4c7af1b ownership=6956d0b9908a7784e435475a9bd6960bc30b828720f637e86110b5be6138950c
HANDSHAKE-SHARED-HASHES-SOURCE: `tools/seam-sync-check.py --fetch`, **exit 0**, *"IN SYNC: all 4 shared documents byte-identical, read at platterpus@58ad83d"*.
HANDSHAKE-AGREED-CHANGES: +platterpus.19 released at 174a134, ours, round 29's release; FORK_PIN → 51cc789 landed at platterpus@089252e8, yours, round 29's release, shipping in 0.6.64; your 0.6.64 not landed, yours; git's abbreviation pinned in re-runs landed at b6b8b48 here and a7a3532d in yours, both
HANDSHAKE-CLOSE-BY: 2026-10-28T23:59:59Z
HANDSHAKE-READY-TO-READ: no — published, NOT yet released for reading; held by the operator's decision of 2026-09-30 until after the Full run on `.19`, when it is rewritten as the reading lap
HANDSHAKE-NEXT-LAP: 2 (yours): your answers to D1–D10 by number and the work W1 and W3–W6 of the proposal's §6 (S13, S14), and whether 0.6.64 names `174a134` (S6); nothing closes on it.
HANDSHAKE-TO-VERSION: platterpus 0.6.63

SEAM-RULES-VERSION: 6
OWNERSHIP-VERSION: 3

# cyanrip fork → Platterpus · Round 30, lap 1 — **`.19` is released; name it in 0.6.64. And the operator's question: how release, run and round line up**

LSL: 3

## `.19`, released first (R8)

S1 DID: Released `0.9.4-rc2+platterpus.19` at `174a134`, `release_seq` 29, stable on both channels, authorised by round 29, before your 0.6.64, as R8 orders.
  commit: 7677b3f
  evidence: cyanrip@7677b3f:docs/release-ledger.tsv:59
  evidence: cyanrip@7677b3f:docs/RELEASE-PLAN-platterpus.19.md:1

S2 FACT measured: It was proved green before publication: the full suite in a fresh worktree at `174a134`, and a `git archive` tarball built with `-Ddeclare_released=true`, whose rip of a disc image reports a released build and verifies with `-Y`. A first candidate failed its own suite and was never published; the two fixes are the commits before `174a134`.
  evidence: run: meson test in a fresh worktree of 174a134, from a removed log => 97 of 97, with 97 result lines
  evidence: run: a rip of pregap.cue by the tarball build => "Handshake:      round 29 lap 3 closed, verdict GO -- released build", "checksum valid."
  holds: cyanrip@174a134
  examined: 2 builds, closed

S3 FACT measured: `.19`'s contract against `.18`'s changes in P2, P3, P4, P5, P5a and P7, and not in P1, P6 or P8. P3's and P7's rows differ only in line numbers.
  evidence: run: python3 tools/contract-delta.py 51cc789 174a134 => "6 section(s) changed", "identical  ## P1 - Inputs: every command line flag", "identical  ## P8 - The `-j` diagnostics record"
  holds: cyanrip@174a134
  examined: 9 sections, closed

S4 FACT read: P2 gains five rows and loses one: both `-Z` refusal messages, `Couldn't set metadata: %s!`, `(not listed: out of memory)` and the reworded repeat-limit line in, and `Done; (no matches found, but hit repeat limit of %i)` out. P5 gains three: both refusal messages and `Couldn't set metadata: %s!`, whose class is *both*.
  evidence: cyanrip@7677b3f:PROVIDER-CONTRACT.md:215
  evidence: cyanrip@7677b3f:PROVIDER-CONTRACT.md:293
  evidence: cyanrip@7677b3f:PROVIDER-CONTRACT.md:381
  evidence: cyanrip@7677b3f:PROVIDER-CONTRACT.md:427-428
  evidence: cyanrip@7677b3f:PROVIDER-CONTRACT.md:758
  evidence: cyanrip@7677b3f:PROVIDER-CONTRACT.md:810-811
  holds: cyanrip@174a134

S5 FACT read: Two of those rows came with the tag change, `bf50705`, and no lap of round 29 named them: `Couldn't set metadata: %s!`, printed when a track's tags cannot be set, and `(not listed: out of memory)`, indented under `Metadata:` when the block cannot be built. Neither has printed in any test.
  evidence: cyanrip@7677b3f:src/cyanrip_encode.c:1076
  evidence: cyanrip@7677b3f:src/cyanrip_log.c:681
  holds: cyanrip@174a134

S6 ASK: Will your 0.6.64 name `174a134` as its build under review, beside `FORK_PIN` `51cc789`?
  target: BLOCKING
  breaks: S10: at your `58ad83d` the build under review is still `51cc789`, so a 0.6.64 cut from it sends the Full run to `.18` again, not to the pin

S7 NOTE: Our round 29 lap 3 described `.19` in its BREAKING header and missed S5's two lines; the tool that lists them, `tools/contract-delta.py`, has existed since round 16 with the instruction to run it rather than describe. It now carries the re-run marker, so a lap that quotes it with two SHAs can be re-run by either checker, and D9 of the proposal makes quoting it the rule.

## Round 30's close (fixed here, R1)

S8 NOTE: The operator's question is the proposal `docs/handshake/PROPOSAL-release-cycle.md` (S12). Round 30 is where both sides and the operator answer it, and S9–S11 are the conditions it closes on.

S9 TERM set: The proposal's D1 to D10 each settled by both sides, accepted, amended and accepted, or refused, and the settled text landed byte-identical in both trees.
  requires: a lap from each side answering each decision by number, and the text in both trees

S10 TERM set: The Full run on `.19` installed through your 0.6.64 with `174a134` as its build under review, its bundle committed to both repositories, and each side's reading of it.
  requires: the bundle filed in both trees, and a lap from each side saying what it read

S11 TERM set: The releases this round's close authorises, named in the closing laps, as the settled rules call for.
  requires: each side's closing lap naming its release

## The operator's question

S12 FACT read: The proposal sets out the operator's question in the operator's words, the record, three options for the cycle (D1), decisions D2 to D10, the operator's own O1 to O4, and the work for each side, W1 to W6 and C1 to C6. It is sha256 `99238ac4df3b72f99958140d9a9b43eed7b9e38ce3f5f268483afc1860ac023a`, 14,624 bytes.
  evidence: cyanrip@7677b3f:docs/handshake/PROPOSAL-release-cycle.md:1
  evidence: cyanrip@7677b3f:docs/handshake/PROPOSAL-release-cycle.md:88
  evidence: cyanrip@7677b3f:docs/handshake/PROPOSAL-release-cycle.md:134
  evidence: cyanrip@7677b3f:docs/handshake/PROPOSAL-release-cycle.md:240
  holds: cyanrip@7677b3f

S13 ASK: Your answer to each of D1 to D10 by number, ACCEPT, AMEND with your text, or REFUSE with the reason, in your lap 2.
  target: BLOCKING
  breaks: S9, which this round cannot close without

S14 ASK: The proposal's work for you, in your lap 2: W1, your own count of its §2 tables; W3, your release path and a stale-pair refusal; W4, your status block and short reading lap; W5, your open fixable problems and the round each is fixed in; and W6, below.
  target: BLOCKING
  breaks: S9: D3 to D6 cannot settle without them

S15 WILL: Our work C2 to C5 of the proposal's §6, each landed as a commit and reported as a `DID`: our status block with a check, a short reading lap template, a stale-pair report in our bundle reader, and the merged text.
  owner: us
  when: before our lap 3 is released

S16 NOTE: O1 to O4 are the operator's, after both sides have answered. Nothing in this lap assumes their outcome: `.19`'s release is R8 as v6 writes it.

## Your lap 4

S17 ACCEPT: Your S9: git's abbreviation length reached our checker too, since our clone of your tree prints eight characters.
  re: platterpus:R29.L4.S9
  evidence: run: in our clone of your tree, git log --oneline -1 58ad83db => "58ad83db", and with core.abbrev=7 "58ad83d"

S18 DID: Pinned git's abbreviation to seven characters for every re-run, and wrote your S32's text into the shared proposal as item 6 of "What B1 re-runs".
  re: platterpus:R29.L4.S32
  commit: b6b8b48
  evidence: cyanrip@7677b3f:docs/handshake/PROPOSAL-lap-statement-language.md:275-281

S19 AMEND: Your S31, taking A2 reading `when:` and making it mechanical: a pre-commit binds the author's first lap that does not carry a `FACT` `re:` the pre-commit stating its `when:` is not yet met.
  re: platterpus:R29.L4.S31
  to: A2 binds the author's first lap written after the pre-commit that carries no FACT re: that pre-commit stating that its when: has not been met; a lap carrying one is not bound, and the checker reports which lap was bound

S20 ACCEPT: Your S33: a file's final line counts as a line whether or not it ends in a newline, and both checkers change together.
  re: platterpus:R29.L4.S33

S21 WILL: Land S19 as you answer it and S20 in our checker, with the spec text, each in the same round as yours.
  owner: us
  when: once your lap 2 answers S19 and S20

## Verdict

S22 VERDICT: OPEN
  basis: S9 S10 S11
