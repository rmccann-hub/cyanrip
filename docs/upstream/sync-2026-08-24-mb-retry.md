# Upstream sync analysis — `f8ebf48`, 2026-08-24

**Status: ANALYSIS ONLY. Nothing has been merged into `platterpus-fork`, and
nothing should be until round 13 closes.** `master` (our clean mirror) has been
fast-forwarded to `f8ebf48`; the fork is at `d024694` and does not contain it.
Syncing the mirror is free and touches no consumer-facing reference — this
document is what makes the delta visible, which is the only reason the mirror
is kept current.

| | |
| --- | --- |
| upstream `master` | `f8ebf48` — 0.9.4-rc2 |
| fork `platterpus-fork` | `d024694` — 0.9.4-rc2+platterpus.7 |
| merge-base | `4f28cf0` (the previous sync point) |
| inbound commits | **1** |
| our commits upstream lacks | 352 |

Regenerate the raw delta with:

```
tools/upstream-delta.py --upstream master
```

---

## 0. The headline

| what | verdict | why |
|---|---|---|
| inbound commits | **1** | `f8ebf48 src/musicbrainz: retry queries when busy` |
| files touched | 2 | `src/musicbrainz.c` (+82/-24), `src/cyanrip_main.h` (+3) |
| CLI surface | **not measured** | no upstream binary built; see §3 |
| **log text** | **TWO NEW LINES** | §2 — this is the handshake-material half |
| dependencies | no change | `tools/upstream-delta.py`: inbound none, ours-only none |
| collisions with our work | **none apparent** | we have not modified the retry path |

---

## 1. What the commit does

Upstream's own subject: *"src/musicbrainz: retry queries when busy"*. It adds a
bounded retry around MusicBrainz queries, with three new fields in
`cyanrip_settings`/`cyanrip_ctx` and a rewritten error path in
`src/musicbrainz.c`.

**We have not modified that path**, so a merge should be mechanical. That is a
prediction from the file list, not a claim about the merge — it has not been
attempted and this document changes no code.

---

## 2. Log text — the part that matters to the seam

**Two new format strings, measured by `tools/upstream-delta.py` from the
`cyanrip_log()` call sites in each tree:**

```
Retrying in %_ seconds (attempt %_ out of %_)...
MusicBrainz lookup failed, try again later,
```

**`MusicBrainz query failed: %_` is NOT new.** It exists at `4f28cf0`, at
`f8ebf48` and in our fork — counted in all three rather than assumed from the
diff, because a rewritten function makes an unchanged string look added.

### What this means for Platterpus, stated rather than assumed

**Neither line can ever appear in a Platterpus rip**, because Platterpus passes
`-N` on every invocation and `-N` disables MusicBrainz lookups entirely. They
told us so in round 13 lap 2, in the course of explaining why their `-G`
handling was backwards: *"it cannot succeed in any case, because `-N` means you
never resolve a release of your own."*

**That lowers the risk and does not remove the obligation.** The seam rule is
*"could the other side notice?"*, and the answer for these two lines is no —
but the contract is not only for Platterpus, `PROVIDER-CONTRACT.md` P5 is
generated from every `cyanrip_log()` call site, and a merge would move it. So
the merge is handshake material even though the specific consumer we have
cannot reach the new lines.

### The 61 lines we have and upstream does not

Listed by the tool and not reproduced here. They are our accumulated
divergence, not something this commit threatens. **A merge must not silently
drop any of them** — that is what the list is for, and it is why the tool
prints it on every run rather than only when something changes.

---

## 3. CLI surface — NOT MEASURED, and deliberately blank

`tools/upstream-delta.py` refuses to derive the flag list from the option
table, and it is right to: a flag list read from source is a claim about
behaviour nobody ran (seam-rules S-9). Measuring it needs an upstream build,
which this analysis did not do.

**The file list makes a CLI change unlikely** — `musicbrainz.c` and a struct
field are not where options live — but *unlikely* is not *measured*, and this
section says so rather than filling itself in with a guess.

Build both and pass `--fork-binary` / `--upstream-binary` before the merge.

---

## 4. Recommendation

**Do not merge while round 13 is open.**

Two reasons, and the second is the stronger one:

1. **S-15 freezes the pin**, and while new commits after the pin are allowed,
   log-text changes are contract surface. The round's whole subject is what
   `+platterpus.8` will contain.
2. **A release cut from a tree carrying unreviewed upstream log changes is
   exactly the thing the handshake exists to prevent.** It would not matter
   that Platterpus cannot reach the lines; what would matter is that we shipped
   contract surface neither side had looked at, in the round where we asked
   them to trust the build.

**Merge in round 14's window**, after `+platterpus.8` is cut and before
`+platterpus.9` — where it is one declared inbound change in a handshake file,
measured properly with both binaries built, rather than a surprise inside a
release.

**Nothing about this is urgent.** The feature helps users who let cyanrip do
its own MusicBrainz lookups; it is invisible to our one known consumer.

---

## 5. What was actually done today

- `master` fast-forwarded `4f28cf0` → `f8ebf48`. It had no local commits of its
  own, so this was a true fast-forward.
- `platterpus-fork` **untouched**, and confirmed by
  `git merge-base --is-ancestor f8ebf48 platterpus-fork`, which reports the
  commit is not an ancestor.
- This document written.

Nothing else. No merge, no cherry-pick, no code change.
