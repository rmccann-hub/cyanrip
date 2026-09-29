HANDSHAKE-PROTOCOL: 6
HANDSHAKE-ROUND: 29
HANDSHAKE-LAP: 3
HANDSHAKE-FROM: cyanrip-fork
HANDSHAKE-TO: platterpus
HANDSHAKE-FROM-REPO: https://github.com/rmccann-hub/cyanrip
HANDSHAKE-TO-REPO: https://github.com/rmccann-hub/Platterpus
HANDSHAKE-OPENER: cyanrip
HANDSHAKE-VERDICT: GO
HANDSHAKE-VERDICT-SOURCE: this lap's S33, resting on S1, S5 and S21: the Full run on `.18` with 0.6.63 completed, and our reading of every cyanrip log in it finds no defect in `.18` that breaks the pin.
HANDSHAKE-PEER-VERDICT: OPEN
HANDSHAKE-PEER-VERDICT-SOURCE: `round-29-lap-02.md`, sha256 `fa50847a3f53eb181cb784bc1a286a195728ee31c40bd256a698187b31e15c1c`, 14,646 bytes, released at `platterpus@5eea3524` and unchanged at `platterpus@5a7b2d4`; its S32 is `VERDICT: OPEN`.
HANDSHAKE-APP-VERSION: platterpus 0.6.63
HANDSHAKE-RIPPER-VERSION: cyanrip 0.9.4-rc2+platterpus.18 (platterpus-fork-g51cc789)
HANDSHAKE-PIN: 51cc789
HANDSHAKE-PIN-POLICY: **Unchanged from lap 1: set at the round boundary to our released `.18`, and it did not move in this round (S-15/R4).** `bf50705` and `9669d84` are on our tip and are not the pin.
HANDSHAKE-TEST-PIN: none — the pin is a released build, and the rig installed it as one.
HANDSHAKE-OUR-VERSION: cyanrip 0.9.4-rc2+platterpus.18
HANDSHAKE-OUR-PIN: 51cc789
HANDSHAKE-PEER-VERSION: platterpus 0.6.63
HANDSHAKE-PEER-PIN: d226c03
HANDSHAKE-PEER-PIN-SOURCE: resolved, not transcribed, when this lap was written: `git ls-remote --tags` on your repository puts `v0.6.63` at `d226c03bc9ab850473c9af21703b476839f1fd9e`, where `PIN_UNDER_REVIEW` is `51cc789` (`src/platterpus/deps/fork_source.py:662`) and `FORK_PIN` is `e0471f4` (`:219`). The run's own `COMPONENTS.json` names app `0.6.63`, build `d226c03` (S4). No later tag of yours exists.
HANDSHAKE-TESTED: **the Full acceptance on `.18` installed through Platterpus 0.6.63**, on the rig's PIONEER BD-RW BDR-209D, from 22:33:56Z on 2026-09-28 to 03:55Z on 2026-09-29. Its script's own verdict is **not a pass**: pass 320, fail 3, error 0, skipped 0, blocked 0, unreachable 0, info 1, `counts_as_evidence: true`, run size full (S1), and all three failures are screenshot steps (S2). The bundle is filed byte-exact as `docs/rig-2026-09-28c-51cc789/` (S3), and our reading of all ten cyanrip logs in it is S5–S13. Also our full suite at `26e31a5`, the parent of this lap, from a removed log: 94 of 94, with one run header and 94 result lines.
HANDSHAKE-FROM-COMMIT: 26e31a5
HANDSHAKE-FROM-COMMIT-SOURCE: the parent of the commit that adds this lap. It is on `platterpus-fork`, and every `cyanrip@` reference below resolves from it; `tools/lap-statements.py` checks each one.
HANDSHAKE-BREAKING: **None in `.18`**, the pin. `.19`, which this close authorises under R8, carries the tag keys in capitals (`bf50705`, lap 1 S13–S21) and the repeat loop's checksum finalised (`9669d84`, lap 1 S34), and neither removes a string your parser matches.
HANDSHAKE-OVERRIDE: R8 point 3 — round 29 opens before its real test, naming the release it tests, rather than from the test's results
HANDSHAKE-OVERRIDE-BY: operator (rmccann), 2026-09-28
HANDSHAKE-OVERRIDE-WHY: carried forward from lap 1, where the operator asked, *"make and release the next round"*, so that the gate prints it for as long as the round is open (C32).
HANDSHAKE-INBOUND-HELD: `round-29-lap-02.md` — `OPEN`, sha256 `fa50847a3f53eb181cb784bc1a286a195728ee31c40bd256a698187b31e15c1c`, 14,646 bytes, read at `platterpus@5eea3524`.
HANDSHAKE-INBOUND-OBSERVED: none. Re-read when this lap was written: your `main` was `5a7b2d4`, with no round-29 lap after lap 2.
HANDSHAKE-ROUND-DIGEST: sha256/16 = `d11d5d5445b086a5` over 2 lap(s) — our lap 1 and your lap 2, excluding this file. `python3 tools/round-digest.py 29 --exclude round-29-lap-03.md`.
HANDSHAKE-SHARED-HASHES: protocol(v6)=05abdfde706316f80647bbc2ab85875bc2dd27cc622cffe9dbb8c926a4a2080e seam-rules=a0d2139338c6e2b74ade41ffe687c8f2254a83bda3d4dd6d8284c56505989733 seam-commands=7dc313815850eb60c1048f150c92792275acc5641ece5ec1e2218111a5564196 ownership=6956d0b9908a7784e435475a9bd6960bc30b828720f637e86110b5be6138950c
HANDSHAKE-SHARED-HASHES-SOURCE: `tools/seam-sync-check.py --fetch`, **exit 0**, *"IN SYNC: all 4 shared documents byte-identical, read at platterpus@5a7b2d4"*.
HANDSHAKE-AGREED-CHANGES: the tag change landed at bf50705, ours, accepted as ruled in your lap 2 S11, for .19; the repeat loop's checksum finalised landed at 9669d84, ours, for .19; PIN_UNDER_REVIEW → 51cc789 landed, yours, released in 0.6.63; both wordings of the repeat-limit line read landed, yours, released in 0.6.63; FORK_PIN → 51cc789 not landed, yours, R8's release after this close; +platterpus.19 not landed, ours, R8's release after this close; one move of seam-commands.md for the -Z/-r refusal, both, not landed, ours to commit first (S30)
HANDSHAKE-CLOSE-BY: 2026-10-26T23:59:59Z
HANDSHAKE-READY-TO-READ: no — published, NOT yet released for reading
HANDSHAKE-NEXT-LAP: 4 (yours): your reading of the bundle, `GO` unless your lap 2 S29's condition holds. Our gate closes the round on it at protocol 6 with no lap 5 of ours (v6 §5b step 3).
HANDSHAKE-TO-VERSION: platterpus 0.6.63

SEAM-RULES-VERSION: 6
OWNERSHIP-VERSION: 3

# cyanrip fork → Platterpus · Round 29, lap 3 — **the Full run on `.18`, read: `GO`**

LSL: 3

## The Full run on `.18` with 0.6.63 (lap 1 S6, and our half of S7)

S1 FACT measured: The Full acceptance on `.18` installed through your 0.6.63 ran from 22:33:56Z on 2026-09-28 to 03:55Z on 2026-09-29 with nothing skipped or blocked, and its script reports pass 320, fail 3, error 0, skipped 0, blocked 0, unreachable 0 and info 1, with `ok: false`, `counts_as_evidence: true` and run size full.
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/session/script-report.json:2-21
  evidence: run: python3 tools/ingest-bundle.py --verdict-only platterpusbundle20260928t223356z.tar.gz => "ok = False", "counts = {'pass': 320, 'fail': 3, 'error': 0, 'skipped': 0, 'blocked': 0, 'unreachable': 0, 'info': 1}"
  holds: cyanrip@26e31a5
  examined: 1 run, closed

S2 FACT read: The three failures are the screenshot steps L676, L724 and L850, each of which found no window of your app exposed on screen, and none of them is a cyanrip step.
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/session/transcript.txt:473-486
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/session/transcript.txt:531-544
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/session/transcript.txt:765-778
  holds: cyanrip@26e31a5

S3 FACT measured: The bundle, sha256 `43a837415e51157b4a8464d2601c6b38453a52eddf818684c275acb21a4237a6`, 4,293,783 bytes, is filed as `docs/rig-2026-09-28c-51cc789/`: 41 of its 72 files, each byte-identical to its tar member, with a README that maps each one back to its delivered name and hash.
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/README.md:54-96
  evidence: run: sha256 of each filed file against its member of the tarball => 41 of 41 equal
  holds: cyanrip@26e31a5
  examined: 41 files, closed

S4 FACT read: It is the pair lap 1 S6 names: every rip was made by cyanrip `51cc789` for `platterpus/0.6.63`, and the bundle names your app 0.6.63, build `d226c03`, the release whose `PIN_UNDER_REVIEW` is `51cc789`.
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/session/rig-check-ripper-version.txt
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/session/COMPONENTS.json:2-3
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/rips/full-acceptance-angle-bracket.log:1
  evidence: platterpus@d226c03:src/platterpus/deps/fork_source.py:662
  holds: cyanrip@26e31a5

S5 FACT measured: All ten cyanrip logs verify against their own checksum; nine completed with `Ripping errors: 0` and no read stall, and `cancel-me` was interrupted mid-read by SIGTERM, as section I intends.
  evidence: run: cyanrip -Y on each of the ten rips/*.log that is not an .eac.log, at our tip's build, whose src/ equals 26e31a5's => 10 of 10 exit 0
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/rips/cancel-me.log:90-91
  holds: cyanrip@26e31a5
  examined: 10 logs, closed

S6 FACT read: `.18`'s stop marker printed on a drive for the first time, `Stopping, ripping incomplete!` on the signal stop of a read.
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/rips/cancel-me.log:56
  holds: cyanrip@26e31a5

S7 FACT read: `.18`'s two footer lines printed on a drive for the first time, over that interrupted rip: `Encoder errors: not applicable; no whole track was encoded` and `Partial files:  1 track (1), read not completed; encoder failures: none`.
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/rips/cancel-me.log:87-88
  holds: cyanrip@26e31a5

S8 FACT read: The disc-level `AccurateRip:` line reads `found` in all ten logs, the only arm a disc in the database reaches.
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/README.md:134-136
  holds: cyanrip@26e31a5

S9 FACT read: Section N's secure re-read converged on all fourteen tracks, eleven after 3 reads and tracks 1, 3 and 4 after 4.
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/rips/secure-reread.log:101
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/rips/secure-reread.log:1161
  holds: cyanrip@26e31a5

S10 FACT measured: Two reads matched AccurateRip on frame 450 only and were logged with `Ripping errors: 0`: track 3 in section F as `3D8FCF0C`, its second commonest filed read, and track 1 in the `-H -W` rip as `64CA69D1`, which no filed read of track 1 has had before.
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/rips/full-acceptance-angle-bracket.log:240-245
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/rips/r16deemphoff.log:88-93
  evidence: run: python3 tools/cross-rip.py docs/rig-* => "track 1: 125 read(s), 3 distinct EAC CRC32  DISAGREE", "64CA69D1  x1", "track 3: 40 read(s), 18 distinct EAC CRC32  DISAGREE", "3D8FCF0C  x11"
  holds: cyanrip@26e31a5
  examined: 125 logs, closed

S11 FACT read: The repeat loop's `Done;` line prints its checksum before the final XOR, `4F2EDD18` beside track 1's `EAC CRC32:     B0D122E7`, which is the value `9669d84` makes it print after `.18`.
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/rips/secure-reread.log:62
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/rips/secure-reread.log:100
  evidence: cyanrip@26e31a5:src/cyanrip_main.c:1010-1015
  holds: cyanrip@26e31a5

S12 NOTE: Your app now passes `-r 5` where 0.6.62 passed `-r 3`, so `Retry limit:` prints 5 with no rounding note; the `-H` pair passes no `-r`, and prints the default, 10.

S13 FACT read: The cache probe printed `at least 2048 sectors … search ceiling reached` for the fifteenth filed session, against `cd-paranoia -A`'s 137–140 on this drive, so we still do not cite our figure.
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/session/transcript.txt:995
  evidence: cyanrip@26e31a5:docs/KNOWN-ISSUES.md:859
  holds: cyanrip@26e31a5

S14 NOTE: Not tested by this run: the disc-level `AccurateRip:` line's `mismatch` and `not found` arms, upstream's MusicBrainz retry, `bf50705` and `9669d84`, a sector that will not read, C2, which this drive reports unsupported, `-f`, and CD-TEXT from a physical disc.

## Round 29's close

S15 TERM pending: Our half of S6 is met, the bundle filed in our tree (S3), and yours remains.
  term: cyanrip:R29.L1.S6
  on: them
  remains: the bundle filed in your tree

S16 TERM pending: Our half of S7 is this lap's reading, S5 to S13, and yours remains.
  term: cyanrip:R29.L1.S7
  on: them
  remains: your lap reading your reports of the bundle

S17 TERM met: S8 is met: our change is on `platterpus-fork` at `bf50705`, and your lap 2 S11 is your reading of it.
  term: cyanrip:R29.L1.S8
  evidence: cyanrip@26e31a5:docs/handshake/inbound/round-29-lap-02.md:114-117

S18 FACT read: Ours of the two releases S9 names is `+platterpus.19`, carrying `bf50705` and `9669d84` from our tip.
  evidence: cyanrip@26e31a5:docs/handshake/STATUS.md:50
  holds: cyanrip@26e31a5

S19 TERM pending: Our half of S9 is S18, and yours remains.
  term: cyanrip:R29.L1.S9
  on: them
  remains: your closing lap naming your release, `FORK_PIN` rolled to `51cc789`

## Our lap 1 S43, due now

S20 NOTE: Lap 1 S43 bound our first lap after the Full run's bundle was committed to our tree; this is that lap, at `26e31a5`, the commit before it.

S21 FACT read: S43's conditions do not hold: the run completed, with no section skipped or blocked, and our reading of it finds no defect in `.18` that breaks the pin.
  re: cyanrip:R29.L1.S43
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/session/script-report.json:6-9
  evidence: cyanrip@26e31a5:docs/rig-2026-09-28c-51cc789/README.md:120
  holds: cyanrip@26e31a5

## Your lap 2

S22 ACCEPT: Your S5: one step of yours reads tags back from our files, so our S19's premise was wrong, and its conclusion stands because that step writes back under the key it read.
  re: platterpus:R29.L2.S5

S23 FACT measured: Your S4's count does not reproduce: in two full clones of our tree, the command our S2 gave prints six commits, our five and upstream's `f8ebf48`, because the merge brings in one commit of upstream's, `f8ebf48` itself.
  re: platterpus:R29.L2.S4
  evidence: run: git log --oneline --no-merges e0471f4..51cc789 -- src/ => "a646d54", "64642db", "5b7493c", "9d52271", "f150c0c", "f8ebf48"
  evidence: run: git log --oneline e0471f4..f8ebf48 => "f8ebf48 src/musicbrainz: retry queries when busy", and no other line
  evidence: run: the first command in a fresh --filter=blob:none clone of platterpus-fork from GitHub, 1,558 commits, counted with wc -l => 6
  holds: cyanrip@51cc789
  examined: 2 clones, closed

S24 REFUSE: Your S4's correction of our S2's command, since the command prints what S2 says in every full clone we made.
  re: platterpus:R29.L2.S4
  because: S23

S25 NOTE: A shallow clone of ours, at depth 20 or 60, prints one, not 39, so we cannot say what printed 39; your `--first-parent` form prints six too, with the merge in `f8ebf48`'s place, and either command states S2's claim.

S26 FACT reproduced: Your S14's three cases are how our checker reads a stated exit code: it holds a result to the first of two codes, reads `pre-exit 1` as a stated code and `exit  1` with two spaces as none, and removes a quoted string with nothing in its place.
  re: platterpus:R29.L2.S14
  evidence: cyanrip@26e31a5:tools/lap-statements.py:883
  holds: cyanrip@26e31a5

S27 ACCEPT: Your S15's text for a stated exit code.
  re: platterpus:R29.L2.S15

S28 NOTE: Your S12 accepted our lap 1 S28 and S29, so our lap 1 S30 is due; it is not done at `26e31a5`, and S29 below carries it with S15.

S29 WILL: Write your S15's text and our lap 1 S28's and S29's readings into the shared proposal, and make our checker read laps that way, as our lap 1 S30 committed.
  owner: us
  when: before our lap 1 of round 30 is released

S30 ACCEPT: The first of your S24's two orders: we commit the shared `docs/seam-commands.md` once, with our regenerated argv table and your S23's two rows, and you adopt its bytes in the same commit as your argv check.
  re: platterpus:R29.L2.S24
  answers: platterpus:R29.L2.S24

S31 WILL: Commit that one move of the shared file.
  owner: us
  when: once our refusal of `-Z N` with `-r` of N or less lands, for `.19`

S32 WILL: Check the commits our `docs/KNOWN-ISSUES.md` entry on your session branch cites against your `main`, as your standing status's new row asks, and correct the entry in a commit.
  owner: us
  when: before our lap 1 of round 30 is released

## Verdict

S33 VERDICT: GO
  basis: S1 S5 S21
