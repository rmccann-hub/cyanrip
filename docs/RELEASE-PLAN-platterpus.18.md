# Release plan — `+platterpus.18`, round 28's fixes

*Written 2026-09-27, while round 28 is open and before its Full run. **A plan,
not a release.** `meson.build` says `0.9.4-rc2+platterpus.17`, the ledger's last
row is seq 27, and `tools/release-gate.py --release-gate` exits 1: round 28 is
open.*

**It is written now so that the release is a sequence to follow, not a document
to write**, at the moment round 28 closes. Everything it can say before the Full
run it says; what the run adds goes into §2 as it is fixed, and the plan names
its condition rather than a date.

## 1. The condition

- **The authorising round: 28**, closed `GO`/`GO`. Its close conditions are fixed
  in our lap 1 (S6–S8): the Full acceptance on `.17` installed through Platterpus
  0.6.61, each side's reading of the bundle, and R8's two releases named in the
  closing laps, their `FORK_PIN` roll to `e0471f4` and our `.18`. Our lap 3 S29
  pre-commits our lap after the run to `GO` unless the run shows a defect in
  `.17` that breaks the pin, or does not complete.
- **v6 R8** is the rule: a round's close authorises a release of both
  applications, provider first.
- **No consumer-side prerequisite, so far.** No string Platterpus matches is
  removed (§2). Their completeness test fails on a top-level line no rule of
  theirs claims, in a committed log, so they need a rule for `Partial files:`
  before they commit a `.18` interrupted log; their runtime parse logs an
  unknown line at debug and carries on (round 28 lap 3 S11, S12). That is theirs
  to schedule and does not gate this release. **If the run leads to a change
  that removes a string they match, this section changes**, and round 20's
  ordering rule applies: their both-wordings release first.

## 2. What `.18` contains so far, against `.17` at `e0471f4`

| change | commit | who can notice |
|---|---|---|
| **`Encoder errors:` counts only tracks whose read completed**; its zero arm reads `no whole track was encoded` when a partial file exists; a new P2 line, `Partial files:  N track(s) (list), read not completed; encoder failures: none\|N`, follows it when one does | `f150c0c` | a reader of an interrupted rip's log. Agreed in round 28 (our lap 1 S15, their lap 2 S16), announced in our lap 3 S6–S13 |
| **`Stopping, ripping incomplete!` is printed whenever a signal stops a track's read**, from one place, `fail:`; it was printed only when the signal landed inside the frame loop | `9d52271` | a reader of a log whose signal landed after a pass's last frame or between `-Z` passes. Same string, one more path; **to announce in round 28's next lap of ours** |
| **The disc-level `AccurateRip:` line reads `mismatch` or `not found` when a response holds no entry for this disc**, instead of `found`, and no `Tracks ripped accurately:` tally is printed over it, as for a disc not in the database. The status was set to `found` before the loop that would downgrade it | `64642db` | nobody so far: no real response has had that shape. Platterpus's parser ignores the disc-level line (`platterpus@59f4c00:src/platterpus/parsers/cyanrip_log.py:2171`) and reads the per-track rows, which do not change. **To announce in round 28's next lap of ours**, with the stop marker |
| **The AccurateRip response parse is split out of the fetch**, unchanged, so a recorded response is tested with no network | `5b7493c` | no line changes. The contract's P5 moves one row, `AccuRIP DB data error, got unexpected number of bytes!`, out of the `goto end` class, because its exit is now a `return` with the same effect (`1268ccf`) |
| **Upstream's `f8ebf48`, merged**: MusicBrainz queries retry when the server is busy. Two log lines added (`Retrying in %i seconds (attempt %i out of %i)...`, `MusicBrainz lookup failed, try again later, or disable it via -N`) and two removed (`Connection failed, try again? Or disable via -N`, `Error fetching/requesting/auth, this shouldn't happen.`). No CLI or dependency change, measured from both binaries (`f2d0af3`) | `1fb6f07`, contract `06be426` | nobody who passes `-N`, which Platterpus does on every rip. The second removed string is an entry in their message inventory (`platterpus@785925a:src/platterpus/ripper_message_inventory.py:774`), which goes dormant. **To announce in our next round-28 lap**; merged on the operator's decision of 2026-09-28 |
| whatever the Full run leads us to fix | — | round 28 lap 1 S8 |
| tooling and tests: LSL 2 in the lap checker (`df67f5a`), a clean bundle transcript names its population (`f309743`), explicit test timeouts (`126c433`, `df67f5a`), `seam-sync-check.py` fetches `main` by name (`f5ba200`), the `raisesig` shim (`9d52271`), the inert-edit probe before every mutation sweep (`62aed42`), the argv probe's `unobservable` grade (`9207def`), the recorded AccurateRip response test (`5b7493c`, `64642db`), the encoder-failure arms of the log (`27d1616`), and a `seam-check --held` summary that names what it re-checked (`70ac25c`) | as named | our test suite |

`src/` changes at `f150c0c`, `9d52271`, `5b7493c` and `64642db`, and by the upstream merge `1fb6f07`, so far. The CLI is
unchanged and `-j` stays `cyanrip-diagnostics/6`.

**A row-by-row diff of `.18`'s contract against `.17`'s should expect three
changed stable rows, not two** (Platterpus's round 28 lap 4 S6, S7): the two
`Partial files:` rows added, and `no track was encoded` reworded to `no %strack
was encoded`. Beyond the stable table, P5 moves one row between classes (above),
and line numbers move in `accurip.c` and `cyanrip_main.c`.

## 3. The channel

**Decided 2026-09-28 by the operator: stable, after round 28 closes**, the Full
run on `.17` first. A beta now was considered and not taken: Platterpus 0.6.61
offers beta builds to a user who ticks it, and the operator's own app does, so
a `.18` beta would be offered on the rig whose acceptance run accepts only `.17`.

**Stable, both channels resolving to it**, as `.15`, `.16` and `.17` were, unless
round 28 decides otherwise. Platterpus's next release carries `FORK_PIN`
`e0471f4` (round 28's approval) and a `PIN_UNDER_REVIEW` of `.18`, so their app
offers `.18` marked `unapproved` until round 29 reviews it. That is v6 R8 point
2's mark, and it is not withheld: their offer states it, and a person decides.

## 4. The sequence

The same as `.17`'s, `docs/RELEASE-PLAN-platterpus.17.md` §4, which was followed
exactly:

1. **The gate**: `--release-gate` exits 0.
2. **Bump** `meson.build` to `0.9.4-rc2+platterpus.18`. Red by construction.
3. **Regenerate, never hand-edit**: the provider contract, the golden reference
   and the interrupted sample, in their own commit, labelled *"generated by X,
   committed at Y"*. Never `--amend`.
4. **Name the candidate** at the first commit where the version and every
   derived artifact agree. Prove it green on its own: the full suite in a fresh
   worktree from a removed log, and a `git archive` tarball built with
   `-Ddeclare_released=true` reporting `released build`. The tarball rip needs
   `pregap.bin` copied from `cdda.bin`.
5. **Publish**, in one commit: one ledger row (seq 28, round 28), the manifest
   regenerated with `--check` exit 0, the changelog heading, the handshake
   README's pin blocks, `STATUS.md`'s release rows, `CLAUDE.md`'s release
   paragraph, and this file's banner.
6. **Then round 29 lap 1**, naming the release commit as its pin, and the
   `.17` contract's successor with its sha256, as round 28 lap 3 S4 did.

No tag: tag push is `HTTP 403` here, and the commit SHA is the identifier.

## 5. What this release does NOT verify

- **Neither `src/` change has run on a drive.** Both are exercised on disc
  images only: `Partial files:` by `sc_interrupt()` against the file on disk,
  the stop marker by `sc_signal_after_last_frame()`, which raises the signal in
  the window a timer missed. **The `-Z` route between passes has no console
  output to key on**, so it is covered by where the fix sits, not by a run.
- **The `mismatch` and `not found` statuses have never come from a real
  response.** They are asserted on a recorded response altered to that shape
  (`tests/arresp.c`), which is what the fix changes, and no rip has reached it.
- **A wrong read still logs `Ripping errors: 0`.** `Ripping errors:` counts
  operational failures, not read quality, and that is documented, not changed.
- **The album loudness block still covers whatever was read**, and Platterpus
  labels it by coverage (round 27 lap 2 B2).
- **A sector that will not read is still untested on a drive**, and at `-P 0`
  one still hangs at any `-r`. Platterpus never passes `-P`.
- **The cache figure is still wrong** by roughly fifteen times. **Do not cite
  it.**
- **C2 stays `UNREACHABLE`** on the rig's drive. `-f` and CD-TEXT from a
  physical disc are *not yet done*, which is a different claim.
