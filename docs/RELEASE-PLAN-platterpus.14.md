# Release plan — `+platterpus.14`, now that its prerequisite is met

*Written 2026-09-22. **A plan, not a release.** Nothing here is executed.
`meson.build` says `0.9.4-rc2+platterpus.13`, the ledger's last row is seq 23,
and `tools/release-gate.py --release-gate` exits 0 — no round is open.*

**`.14` is the first release of this fork with a consumer-side prerequisite**,
and the prerequisite is now met. What is NOT settled is which channel it goes
to, and §3 is where that decision is posed rather than made. It is the
operator's, because publication is an act.

## 0. Where things stand

| | |
|---|---|
| released | `0.9.4-rc2+platterpus.13` at `2cce60d`, seq 23, stable, authorised by round 21 |
| authorising round for `.14` | **round 22**, closed `GO`/`GO` 2026-09-21, which reviewed and agreed the §0.3 change |
| consumer prerequisite | **met** — Platterpus 0.6.53, §1b |
| gate | `--release-gate` exits **0**. Round 23 closed 2026-09-22; round 24 is not yet open |
| their pin | `FORK_PIN = "2cce60d"` at `platterpus@52b44282:src/platterpus/deps/fork_source.py:183`, and they have said it **stays there until a round reviews `.14`** |

## 1. The condition — two halves, both met

### 1a. The authorising round

**Round 22.** It reviewed the §0.3 per-track split, graded it P1 on
Platterpus's measurement, and agreed the ordering in both directions.
`.13` is the precedent that a release need not be the round's reviewed pin: it
shipped at `2cce60d` on round 21's authority, where round 21's pin was
`fe4d2c4`, carrying two P2 changes that pin does not have. `.14` ships on round
22's authority the same way. **A plan names a condition, not a round number** —
`.12`'s was written for round 15 and authorised by round 17.

### 1b. The consumer prerequisite — their both-wordings release

**Met, in Platterpus 0.6.53**, and found by reading their parser rather than
from the status that announced 0.6.53, which did not mention it. At the tag, not
the branch: `git ls-remote --tags` puts `v0.6.53` at `52b44282`, which is also
their `main`, and there
`src/platterpus/parsers/cyanrip_log.py:237-244` reads

```python
_TRACK_START = re.compile(
    r"^Track (?P<number>\d+) "
    r"(?P<what>"
    r"ripped and encoded successfully!|ripped and encoded with errors\.|"  # <= .13
    r"read successfully!|read with errors\.|"  # >= .14, their §0.3
    r"is data:"
    r")"
)
```

`read successfully` appears in **v0.6.53 and in no earlier tag** — counted in
v0.6.50, .51, .52 and .53 rather than assumed: `0, 0, 0, 1`.

**And a pre-release counts**, which was the one open question. Platterpus
answered it and every part of the answer was verified at `52b44282`:

1. **Every `v0.*` tag is published pre-release by construction** —
   `.github/workflows/release.yml`, the `case "$TAG" in v0.*|…) PRERELEASE="--prerelease"`
   arm at line 343. So for their entire 0.x line the flag is a constant and
   carries no information.
2. **Their updater deliberately ignores that flag** —
   `src/platterpus/update_check.py:99-117`, `is_prerelease_version()`, which
   reads the version string instead because gating on the API flag *"would have
   left stable users with nothing on their channel, ever."* So 0.6.53 is offered
   on their stable channel.
3. **Round 20 already settled it by precedent.** `Retry limit:` first appears in
   their parser at **v0.6.50** — counted across v0.6.48–.51, `0, 0, 2, 2` —
   tagged 2026-09-16, a `v0.*` pre-release. `.13` followed on 2026-09-18. The
   ordering rule has already been satisfied once by a pre-release and nobody
   objected, because in their scheme a pre-release is the only kind there is.

Requiring a non-pre-release would have gated `.14` on something their versioning
does not produce — the condition-gated-on-the-unreachable shape this project
keeps finding.

## 2. What `.14` contains

Two commits change `src/` since `2cce60d`: `89a57d6` and `2f7d9c9`. Every
`cyanrip_log()` format string that changes, read off `git diff 2cce60d HEAD --
src/` rather than recalled:

| change | what it means |
|---|---|
| `Track %i ripped and encoded successfully!` → `Track %i read successfully!` | the line printed after the flush signal and before any encoder was joined, so the encode it asserted **did not exist yet**. Under a 32 KiB write cap it sat above a 253,742-byte file truncated to 32,768 |
| `Track %i ripped and encoded with errors.` → `Track %i read with errors.` | the other arm. The condition always measured the read alone |
| **new:** `Encoder errors:` below `Ripping errors:` | three arms — `none; N tracks encoded`, `N tracks failed (…); M tracks encoded`, `not applicable; no track was encoded` — three states rather than two, for the reason `Read stalls:` has three |

**Both renamed lines are Platterpus's `_TRACK_START` block delimiter**, which is
why this release needed their parser first: a delimiter rename loses every value
hanging off it, not one field.

Plus the compiled-in `Handshake:` state, which moves with every round file.
`-j` is unchanged; the diagnostics schema stays `cyanrip-diagnostics/6`.

**The provider contract ships from the release commit**, which discharges round
23 lap 3 §D3's undertaking — *generate the contract from the pin under review* —
because the release commit is what round 24 will review.

## 3. The judgement — cut it, and the decision is the CHANNEL

**Cut it.** The per-track line in `.13` asserts an encode that has not happened
when it is printed, on an archival record. `.13` already counts encoder failures
in `Ripping errors:`, so the disc-level record is honest; `.14` makes the
per-track line honest too.

**Which channel is the decision, and reading their updater is what makes it
one.** Verified at `platterpus@52b44282`, from the code rather than from a
comment:

- Their app reads **our** manifest, from our branch tip —
  `src/platterpus/deps/ripper_manifest.py:66-68`, `MANIFEST_URL` =
  `…/platterpus-fork/release-manifest.json`.
- It **offers and never installs** — `:10-16`, *"Notice, and offer. Never 'keep
  up to date'"* — a build newer than their pin, on the user's channel, **stable
  by default** (`:97-98`), and tells the user the consequence: every rip made
  with an unreviewed build is stamped `ripper_handshake_approval: unapproved`.
- Their approval verdict keys on `FORK_PIN`, which **stays at `2cce60d` until a
  round reviews `.14`**, by their own statement.

**So a stable `.14` would be offered to every Platterpus user on the default
channel, stamped `unapproved`, until round 24 closes and they roll their pin.**
Their own code calls that state out — `fork_source.py:167-175`: *"A closed round
whose pin has not rolled is not a neutral state; it is a window in which the
approved build is stamped as unapproved."* It has opened before: their comment
records it for `fe4d2c4`, and `.13` sat on our stable channel from 2026-09-18
until their pin rolled at round 22's close on 2026-09-21. For `.14` it would last
until a round has **reviewed** the build, which is later than a close.

| | **(A) stable now** | **(B) beta now, stable after round 24** |
|---|---|---|
| version | `0.9.4-rc2+platterpus.14` | `0.9.4-rc2+platterpus.14-beta.1`, the `.5-beta.N` precedent |
| ledger row | `24  stable  …  22` | `24  beta  …  22`, then later `25  stable  0.9.4-rc2+platterpus.14  …  24` |
| who is offered it | **every** Platterpus user on the default channel, stamped `unapproved` | only users who opted into beta — **the rig is one**: its saved config after 2026-09-22 reads `ripper_channel = "beta"` (`docs/rig-2026-09-22-2cce60d/session/config.toml:36`), set by the acceptance script at step 27 and **not restored** by its section Q, which restores everything else it changed |
| what it claims | *"jointly verified"* — CLAUDE.md: a stable release claims it. Platterpus's side says the build is not approved | *"no joint verification"* — which is exactly what is true |
| timing | must ship **before round 24 opens**, or it waits for round 24's close | C20: a pre-release is permitted with a round open, so it can ship **inside** round 24 |
| cost | none extra | one more ledger row and one more publish commit when round 24 closes; and the stable commit will differ from the reviewed beta by the version string, which is `.13`'s shape and was accepted |

**Recommendation: (B).** It is the only option under which every surface tells
the truth at once: our channel says *unverified*, their stamp says *unapproved*,
and no default-channel user is offered a build neither side has reviewed. It
puts `.14` exactly where the post-`.14` verification session needs it — on the
rig, which is already on beta — and that session is what round 24 exists to
report. **(A) is defensible and our gate permits it**; its cost lands on their
users rather than on us, which is the reason not to choose it without asking.

## 4. The sequence, whichever channel

Each step depends on the one before. The ordering is the point.

1. **The gate.** (A): `--release-gate` exits 0. (B): `--release-gate
   --prerelease` exits 0 and prints any open round first.
2. **Bump** `meson.build` — `0.9.4-rc2` verbatim, the suffix per §3. Red by
   construction: the artifacts still describe `.13`.
3. **Regenerate, never hand-edit**: `tools/gen-provider-contract.py >
   PROVIDER-CONTRACT.md`, the golden reference, the interrupted sample.
   `--check` must exit 0 on the contract.
4. **Commit the code, then the regenerated artifacts as their own commit.**
   Never `--amend`. Say *"generated by X, committed at Y"*.
5. **Name the candidate at the FIRST commit where the version and every derived
   artifact agree**, and prove it green on its own — the full suite from a
   removed log, one run header. Not at the bump: `+platterpus.5` was announced at
   `422d12a`, which fails 2 of 33 from a fresh clone.
6. **Append one row** to `docs/release-ledger.tsv` naming that candidate.
   Append only. It is the operator's act.
7. **Regenerate the manifest**: `tools/gen-release-manifest.py >
   release-manifest.json`, `--check` exit 0. **This is the moment Platterpus's
   app can see it**, because it reads the manifest from our branch tip.
8. **Changelog entry**, and **banner this file the same day** with the commit,
   the ledger row and the round.

**No tag** — tag push is `HTTP 403` here. The commit SHA is the only durable
identifier a consumer can resolve.

## 5. What this release would NOT verify

- **The new wording has never been parsed from a real log.** Both sides
  recorded that in round 22, and Platterpus repeated it in answering the
  pre-release question: *"the new-wording arm is still untested on real
  output."* The suite and the golden reference emit it and their 0.6.53 parser
  accepts it; **no rig session has produced it.** That is the post-`.14`
  session, and under (B) it is reported in round 24's lap 1 the way round 23's
  lap 1 reported the acceptance run.
- **The `Encoder errors:` failure arm has never run on hardware.** It is proved
  under an artificial write cap; a clean disc emits `none`.
- **Our loudness block is measured upstream of the filter graph** —
  `docs/KNOWN-ISSUES.md`. Not in `.14`; its fix changes five P2 values and
  wants a round of its own.
- **The cache figure is still wrong** by roughly fifteen times against
  `cd-paranoia -A`. **Do not cite it.**
- **C2 stays `UNREACHABLE`** on the rig's drive; **`-f`, damaged media and
  CD-TEXT from a physical disc** are *not yet done*, which is a different claim.
- **The approved pair after this release is `(the new SHA, 0.6.53)` and no run
  will have exercised it** until the post-`.14` session does — the same gap
  `.12` and `.13` shipped with, named rather than discovered.
