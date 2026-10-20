# Upstream sync analysis — `7dbe56a`, 2026-10-20

**Status: analysis, written before the merge.** It is taken into
`platterpus-fork` for `.26`, on the owner's word of 2026-10-20, relayed by
the claude-code-skills session's report of that day: build `.26` with
`7dbe56a`, and time a rip of the same disc and tracks on `.25` and `.26`
inside the next Full acceptance run, for as many runs as it takes. §5 records
the merge.

| | |
| --- | --- |
| upstream `master` | `7dbe56a` — 0.9.4-rc3 |
| fork `platterpus-fork` | `eca33dc` — 0.9.4-rc3+platterpus.25 |
| merge-base | `b40c1f0` (the previous sync point) |
| inbound commits | **1** |
| our commits upstream lacks | 1646 |

Regenerate the raw delta, with upstream built in a scratch worktree of
`master`:

```
tools/upstream-delta.py --fork platterpus-fork --upstream master \
    --fork-binary build/src/cyanrip --upstream-binary <upstream build>/src/cyanrip
```

**Our `master` mirror on GitHub still reads `b40c1f0`** when this is written:
the sync-fork call is refused from a session (`HTTP 403`), and the mirror is
moved by the owner's *Sync fork*. This analysis was made against a local
`master` at `7dbe56a`, fetched from `cyanreg/cyanrip`.

---

## 0. The headline

| what | verdict | how it is known |
|---|---|---|
| inbound commits | **1**, 2 files, +15/-7 | `git log b40c1f0..master`, the tool's file list |
| CLI surface | **no change** | `--help` of both binaries, inbound none |
| log text | **no change** | the tool's inventories: the 17 lines upstream has and we lack are the same 17 as at `b40c1f0`, our deliberate divergence, none from this commit |
| dependencies | **no change** | `av_gettime_relative()` is libavutil's, already linked |
| collisions | **none** | a trial merge into `eca33dc` applies without a conflict |
| drive I/O | **fewer media-change queries**, at most one a second | §1 |

## 1. What the commit does

Upstream's subject: *"src/cyanrip_main: check for media changes at most once
a second"*, fixing upstream #165. Before it, both rip loops (the data track
copy and the audio read) asked the drive `cdio_get_media_changed()` before
every frame, and the main loop asked again after each track. Its message says
some drives take several milliseconds to answer, which halved the rip speed
on a PIONEER DVR-112D.

`get_media_changed()` now takes the context, keeps the time of the last query
in `ctx->last_media_check`, and answers *not changed* without asking when the
last query was under a second ago. The first call, at context init, always
asks.

## 2. What it changes here

- **Every call site in our tree goes through it.** After the trial merge,
  `cdio_get_media_changed()` is called once, inside `get_media_changed()`,
  and its five callers are the ones upstream converted: context init, the
  data track loop, the audio read loop and the two after-track checks in
  `main()`. None of our own code asks the drive directly.
- **A disc removed mid-rip still stops the rip**, at most a second later by
  the clock. A removal between tracks is now caught by the next track's first
  query that falls a second after the last, not at the boundary itself. Both
  print `Drive media changed, stopping!` as before.
- **What it saves on our drive is not known.** Our code asked once per frame
  exactly as upstream's did (read from `src/cyanrip_main.c` at `eca33dc`), so
  the BDR-209D pays whatever its answer costs, once per frame. No run has
  measured that cost; the timed rip in the next Full run does.
- **No image test can see it.** libcdio's BIN/CUE and NRG drivers answer the
  query with 0, not changed (measured on `mixed.cue`, `trailing.cue` and
  `cdda.nrg` with a ten-line program against libcdio 2.1), so asking less
  often changes nothing an image rip shows. It is drive I/O, needing
  verification on real hardware, which is the timed rip.

## 3. Handshake material

No log line, flag, exit status or file on disk changes, so nothing a consumer
parses moves. **What a consumer can notice is timing**: a rip may take less
time. That is announced in round 36's lap 1 with the comparison the owner
asked for.

## 4. Verdict

**Take it**, for `.26`. It is upstream's own fix, it applies cleanly, it
changes nothing a consumer parses, and with the second read now Platterpus's
default every disc AccurateRip does not know is read at least twice, so a
per-frame cost is paid at least twice. The timed rip measures what it saves;
it does not decide whether to take it.
