# Plan: release channels, beta opt-in, and version checking

*Design only. Nothing here is implemented. To be carried in the next handshake
lap for Platterpus to agree, amend or reject before either side builds it.*

**The requirement, from the maintainer:** it must always be possible to upgrade
to a beta of Platterpus or any of its dependencies; the user must be **warned**
and given an **option**, never silently moved; there must be a way to **check**
what is available; and the **naming must be consistent** across projects.

---

## 1. The problem, measured rather than asserted

The two projects already disagree about how a beta is spelled:

```
cyanrip     0.9.4-rc1+platterpus.5-beta.1
Platterpus  v0.6.4b1
```

A checker written the obvious way — *"is `beta` in the version string?"* —
**finds ours and misses theirs.** A user on a Platterpus beta would be told they
are on a stable build. That is not hypothetical; it is true of both strings as
they exist today.

There is a second, harder problem underneath it. **cyanrip's version cannot be
ordered.** `0.9.4-rc1` is upstream's, deliberately copied verbatim, and the part
that actually advances is SemVer *build metadata* — which the SemVer spec says
is **ignored for precedence**. So "is there a newer cyanrip?" cannot be answered
by comparing version strings at all, and any checker that tries will be
comparing `0.9.4-rc1` against `0.9.4-rc1` forever.

Neither problem is fixed by picking a prettier version format. They are fixed by
**not deriving machine decisions from the human-facing string.**

## 2. Who owns what

Under the existing split — *cyanrip owns what requires the disc in the drive;
Platterpus owns what can be derived afterwards* — update policy is **downstream**.

| | |
|---|---|
| **cyanrip publishes** | what channel a build is on, what supersedes it, and where to look — as facts, in machine-readable form |
| **Platterpus decides** | whether to offer an upgrade, how to warn, what the user sees, and what happens if they decline |

**cyanrip must not implement the warning, the prompt, or the auto-update.** It has
no user interface and no business having an opinion about a user's risk appetite.
It has exactly one obligation: make the facts checkable without guessing.

## 3. Naming — declare the channel, do not parse it out

**Do not standardise the version strings.** Platterpus's `0.6.4b1` is idiomatic
for its ecosystem, ours is constrained by upstream's namespace, and forcing
either to change breaks tooling for cosmetic gain. This is the same reasoning
`PROTOCOL.md` §1 already uses for directory layout: standardise the *declaration*,
not the internals.

Proposed declared field, in the handshake header and in the manifest below:

```
RELEASE-CHANNEL: stable | beta | dev
```

| channel | meaning |
|---|---|
| `stable` | a released build from a **closed** handshake round. The only channel a user reaches without opting in. |
| `beta` | published deliberately, claims **no** joint verification. Requires opt-in. |
| `dev` | a branch tip or working build. Never offered by an updater at all. |

**Closed set.** An unrecognised channel is treated as `dev` — the most
restrictive reading — for the same reason an unrecognised verdict is "not
closed": an unknown value is not evidence of safety.

### Ordering: a sequence number, not a version comparison

Because our version string cannot be ordered, add a monotonic integer that can:

```
RELEASE-SEQ: <integer>
```

- Increments by one for **every published artifact**, stable or beta.
- **Never reused, never reset**, including across a version-scheme change.
- Owned per project; the two projects' sequences are unrelated and must never be
  compared with each other.

"Is there something newer?" becomes an integer comparison against a value the
publisher stated, rather than an inference from a string two ecosystems spell
differently. **It also survives our next upstream sync**, when the leading
version number changes for reasons that have nothing to do with our releases.

## 4. Discovery — a generated manifest, because tags do not work

The obvious mechanism is git tags or GitHub releases. **Neither is available from
cyanrip's build environment**: tag pushes are refused with `HTTP 403` (re-probed
every round) and no release-creation API is reachable. Any design resting on
them is a design that cannot ship from here.

So: a file on `platterpus-fork`, fetchable by raw URL, **generated** rather than
hand-maintained — for the same reason `PROVIDER-CONTRACT.md` is generated: a
hand-written manifest goes stale silently, which is the failure it exists to
prevent.

Sketch, not a final schema:

```json
{
  "project": "cyanrip-fork",
  "channels": {
    "stable": { "version": "...", "commit": "...", "release_seq": 4,
                "handshake_round": 7, "round_closed": true },
    "beta":   { "version": "...", "commit": "...", "release_seq": 5,
                "handshake_round": 7, "round_closed": false }
  }
}
```

Three properties it must have, each preventing a specific failure:

- **`stable` never points at a beta.** A user who never opts in must be unable to
  reach one, even transiently, even if the file is generated wrong — so the
  generator asserts it and a test proves the assertion fires.
- **`stable` is retained when a beta exists.** Downgrade must always be possible.
  A beta that replaces the stable entry is a one-way door.
- **`round_closed` is derived** from the same round files `release-gate.py`
  reads, not stated separately. A manifest claiming a round closed while the gate
  says otherwise is the two-gates-disagree failure in a new place.

## 5. Warning and option — what cyanrip must guarantee

Platterpus builds the UI. These are the guarantees it needs from us for that UI
to be able to tell the truth:

1. **A beta is identifiable offline, from the artifact alone.** Already true:
   every logfile says `Handshake: … OPEN … NOT a released build`, and the
   `Consumer:`/banner pair records which build produced it. **No network call
   needed to answer "am I on a beta?"** — which matters because the answer must
   still be available years later, reading an archived log.
2. **A beta is never the default.** Enforced at the manifest, §4.
3. **The warning is repeatable, not once-ever.** Our contribution is that the
   fact is in *every* log, so a UI can re-derive it rather than remembering a
   flag it set at install time.
4. **Declining is a supported state, not an error.** A user who says no stays on
   stable and nothing degrades.

**One thing worth arguing about, and we would rather Platterpus ruled on it:**
should a beta *expire*? A build from a round that later closed with a different
pin is now strictly superseded, and a user could sit on it indefinitely.
Our inclination is **no expiry, but a louder notice** — a ripper that stops
working is worse than one that says it is out of date, which is the same
reasoning Platterpus used to reject a refuse-to-run flag.

## 6. Dependencies other than cyanrip

The requirement says *"any dependencies"*. Most of Platterpus's are OS packages
outside this seam, and neither project should pretend to manage them.

What already exists, and is probably enough:

```
Drive used:     libcdio CDRWIN (revision 2.1.)
Encoder:        libavformat 60.16.100, libavcodec 60.31.102 (6.1.1-3ubuntu5)
```

Every rip already records the libcdio and FFmpeg versions that produced it. So
the *reporting* half of dependency checking exists; what does not exist is any
claim that a newer one is available, and **we should not invent one** — cyanrip
cannot know what a distribution offers.

Proposed position: **cyanrip reports the dependency versions it was built and ran
against. Whether a newer one exists, and whether to install it, is entirely
Platterpus's.** That is the ownership split applied unchanged.

## 7. What this plan deliberately does not decide

Listed so they read as open questions rather than omissions:

- **The manifest's exact schema and location.** Sketched, not settled; Platterpus
  is the consumer and should shape it.
- **Whether `dev` is worth having at all.** It may be a channel nobody can ever
  select, in which case it is a label for "not offered" and could just be the
  absence of an entry.
- **Whether `RELEASE-SEQ` belongs in the handshake header** or only in the
  manifest. It is release metadata, not round metadata, and putting it in both is
  how two sources of truth start disagreeing.
- **Who publishes first.** If Platterpus adopts `RELEASE-CHANNEL` before cyanrip
  emits a manifest, nothing breaks — unknown fields are ignored — but the order
  should be deliberate rather than accidental.

## 8. Cost, honestly

Small on our side and mostly generation: a manifest generator, an assertion that
`stable` never points at a beta, a test, and two declared fields. Larger on
Platterpus's, because the UI, the opt-in state and the downgrade path are all
theirs.

**None of it is needed for the round-7 rig session**, and none of it should
be built before that session runs — a design agreed while the evidence it might
change is still uncollected is a design that gets rewritten.
