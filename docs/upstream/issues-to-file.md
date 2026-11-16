# 31 upstream issues for cyanreg/cyanrip, ready to paste

**Generated, never edited.** `tools/gen-upstream-issues.py` renders it from `docs/upstream/defect-reports.md` and `docs/upstream-cachemodel-report.md`, whose combined sha256/16 is `7d27f109072a65af`; `--check` fails when either has moved. Every `file:line` below is upstream's, at the commit its source file names, and each report's row in `docs/SETTLED.md` re-checks it against `master`. Every fork commit linked below is on `platterpus-fork`, which is public, and every upstream commit links to upstream.

**Links were resolved against upstream's `master` at `648b1dd`**, our mirror's tip when this was rendered: a commit it reaches links to upstream, and any other commit our history reaches links to the fork. `--check` renders against that commit, not against what a clone's `master` holds, so every clone holding it gives the same answer; `git fetch origin master` brings it.

**Items 1 to 23 were filed on 2026-10-16**, by the operator, as one issue combining them in the order of importance below: <https://github.com/cyanreg/cyanrip/issues/167>. That link is the operator's word; this file's generator does not read upstream's tracker. An item asked for as an issue of its own is pasted from here. **Items 24 to 31 are not filed yet**: they go to the same issue as a comment, or each as an issue of its own, as the operator decides.

**How to file.** For each item: open <https://github.com/cyanreg/cyanrip/issues/new>, paste the **Title** line into the title box and everything between the two `BODY` markers into the body. File them in order: item 5 refers to item 4, so once item 4 is filed you can replace *"item 4 of this set"* in item 5 with its issue link. Before filing, a quick search of upstream's open issues for each title's key words avoids a duplicate; this list was not checked against their tracker.

**Suggested order of importance**, if you file only some: 6 (apostrophes corrupt metadata on real rips), 8 (disc images rip corrupted audio with `Ripping errors: 0`), 19 (with libcdio 2.3.0 or later, every image rip without `-s` stops at `Offset is unset!`), 1 and 2 (a hung or cut-off process with the drive held), 4 and 5 (`-H` silently drops de-emphasis and the log claims it), then the rest.

## Item 1 of 31

**Title:** The signal handler calls `cyanrip_log()`, which is not async-signal-safe

<!-- BODY START -->

**Where:** `src/cyanrip_main.c:1250-1258`, `on_quit_signal()`.

```c
static void on_quit_signal(int signo)
{
    if (quit_now) {
        cyanrip_log(NULL, 0, "Force quitting\n");
        exit(1);
    }
    cyanrip_log(NULL, 0, "\r\nTrying to quit\n");
    quit_now = 1;
}
```

**What happens:** `cyanrip_log()` takes the log mutex and writes with stdio, and
the second arm calls `exit()`, which runs `atexit` handlers and flushes stdio.
None of these is async-signal-safe. If the signal arrives while the main
thread holds the log mutex, the handler waits for a lock its own thread holds,
and the process hangs with the drive still held. This is from the source, not
from a reproduced hang.

**What the fork did:** the handler writes its two messages with `write(2)`,
records the signal and sets the flag, and the second arm calls `_exit()`, all
async-signal-safe ([`20c2f77`](https://github.com/rmccann-hub/cyanrip/commit/20c2f77), "Make cancellation work: an unsafe signal handler,
SIGTERM, and a -Z loop that ignored both").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 2 of 31

**Title:** SIGTERM is not handled at all

<!-- BODY START -->

**Where:** `src/cyanrip_main.c:1467`, the only signal installation:
`signal(SIGINT, on_quit_signal)`. `SIGTERM` occurs nowhere in the file.

**What happens:** a supervising process, a service manager or `kill` stops
cyanrip with the default disposition. The process dies where it stands: the log
is cut off mid-line with no completion footer and no checksum, so a stopped rip
cannot be told from a truncated or tampered log. Observed on this fork before
the fix, with the same code: a supervisor's timeout left exactly that.

**How to reproduce:** start a rip of any disc image with `-L log`, send
`kill -TERM` once `Ripping track` has printed, and read the logfile.

**What the fork did:** `SIGTERM` gets the same handler as `SIGINT`, and the
footer names the signal (`Rip completed:  no (interrupted by SIGTERM, …)`), in
[`20c2f77`](https://github.com/rmccann-hub/cyanrip/commit/20c2f77).

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 3 of 31

**Title:** `cyanrip_log_finish_report()` sits above `end:`, so every `goto end` skips it

<!-- BODY START -->

**Where:** `src/cyanrip_main.c:2473-2475`:

```c
    if (!ctx->settings.print_info_only)
        cyanrip_log_finish_report(ctx);
end:
```

Twenty-three `goto end` statements in `main()`, which starts at line 1456,
jump to the label below the report.

**What happens:** a run that takes any of them writes a log with no completion
report, and then `cyanrip_log_end()` signs that log as though it were whole.
Observed on this fork: a rip cancelled mid-track produced a signed log with no
footer, which a downstream program checking the log read as *"the log was cut off"*.

**What the fork did:** the footer is written on every route out, inside `end:`,
after the encoders are joined, and says which route it was ([`4cfbe4f`](https://github.com/rmccann-hub/cyanrip/commit/4cfbe4f), "Write
the completion footer on every route out, and give Rip completed: a third
state").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 4 of 31

**Title:** The filter graph is a ternary cascade, so `-H` discards de-emphasis

<!-- BODY START -->

**Where:** `src/cyanrip_encode.c:464-467`:

```c
    const char *filter_desc = hdcd ? "hdcd" :
                              deemphasis ? "aemphasis=type=cd" :
                              peak ? "ebur128=peak=true,anullsink" :
                              NULL;
```

**What happens:** exactly one filter is ever built. With `-H`, de-emphasis is
never in the graph, so a pre-emphasised disc ripped with `-H` keeps its
emphasis, and `-E` (force de-emphasis) and `-W` (no de-emphasis) have no effect.
The peak measurement is dropped whenever either of the first two is chosen.

**What the fork did:** the graph is composed from the filters that apply, in
order ([`b866900`](https://github.com/rmccann-hub/cyanrip/commit/b866900), "Compose the filter graph, so -H stops swallowing
de-emphasis").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 5 of 31

**Title:** `(deemphasis applied)` is printed from the settings, not from what happened

<!-- BODY START -->

**Where:** `src/cyanrip_log.c:90-91`:

```c
        if (ctx->settings.deemphasis || ctx->settings.force_deemphasis)
            cyanrip_log(ctx, 0, " (deemphasis applied)\n");
```

**What happens:** under `-H`, the filter-graph issue (item 4 of this set) means de-emphasis is not applied, but the
log still says it was. The log is the only record of what was done to the audio,
and this line claims a step that did not run.

**What the fork did:** the line reports what the graph actually contained,
fixed with the filter-graph issue (item 4 of this set) in [`b866900`](https://github.com/rmccann-hub/cyanrip/commit/b866900).

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 6 of 31

**Title:** A bare apostrophe in `-a` or `-t` swallows every later field

<!-- BODY START -->

**Where:** `src/cyanrip_main.c:2055` and `:2140`,
`av_dict_parse_string(…, "=", ":", 0)`.

**What happens:** `av_dict_parse_string()`'s tokeniser treats `'` as a quote.
A bare apostrophe opens a quoted run that never closes, so
`-t "1=title=Don't Stop:artist=A:isrc=I"` sets the title to `Dont
Stop:artist=A:isrc=I` and never sets `artist` or `isrc`, with no diagnostic.
The corrupted value is written into the files and the log as though it were
what was asked for. It is the defect in this list most likely to corrupt a real
rip, because apostrophes are common in titles.

**What the fork did:** a bare apostrophe is escaped before parsing, and an
already-escaped one is left alone, so a caller that escapes correctly is not
double-escaped ([`c59dea3`](https://github.com/rmccann-hub/cyanrip/commit/c59dea3), "Escape bare apostrophes in -a/-t, without
double-escaping the consumer's").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 7 of 31

**Title:** An invalid UTF-8 byte truncates a name, and can make `-D` absolute

<!-- BODY START -->

**Where:** `src/naming.c:121-123`:

```c
        ret = av_utf8_decode(&cp, (const uint8_t **)&str, end, AV_UTF8_FLAG_ACCEPT_ALL);
        if (ret < 0) {
            cyanrip_log(ctx, 0, "Error parsing string: %s!\n", av_err2str(ret));
```

**What happens:** the name is cut at the first invalid byte, from a MusicBrainz
field, CD-TEXT or `-a`. A name that starts with one is cut to nothing, and an
empty leading component makes a multi-component `-D` scheme resolve to an
absolute path, so the rip is written outside the directory asked for.

**What the fork did:** an invalid sequence becomes U+FFFD and the rest of the
string is kept ([`c3482b0`](https://github.com/rmccann-hub/cyanrip/commit/c3482b0), "Substitute U+FFFD for invalid UTF-8 instead of
truncating and logging").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 8 of 31

**Title:** Ripping a disc image at any paranoia level above 0 returns corrupted audio and reports `Ripping errors: 0`

<!-- BODY START -->

Since [`c431d58`](https://github.com/cyanreg/cyanrip/commit/c431d58) ("Disable paranoia's drive cache modelling for disc images"),
ripping a BIN/CUE, NRG or CDRDAO image at the default paranoia level returns
audio that does not match the source, and reports success while doing it.

Real drives are unaffected — the code path is guarded on the image driver IDs —
and `-P 0` is byte-perfect either way. It is the default-paranoia image path
only.

### What happens

`src/cyanrip_main.c`:

```c
switch (cdio_get_driver_id(ctx->cdio)) {
case DRIVER_BINCUE:
case DRIVER_NRG:
case DRIVER_CDRDAO:
    cdio_paranoia_cachemodel_size(ctx->paranoia, 1);
    break;
```

The comment above it already identifies the coupling that causes this:

> *1, not 0, as the cachemodel size is also the c_block read chunk size, and 0
> never makes progress*

That is exactly right, and 1 is still inside the range where it goes wrong. The
cachemodel size being the read chunk size means a chunk of 1 sector leaves
paranoia's verification logic **no overlap between chunks to compare**, so it
emits zeroes rather than the sectors it read — and because nothing failed to
*read*, the error count stays 0.

### Reproduction

Any BIN/CUE image will do. With a 2-track synthetic image whose `.bin` is the
ground truth:

```sh
cyanrip -d image.cue -N -A -Q -s 0 -o pcm -D out -F '{track}'
cat out/1.pcm out/2.pcm | cmp - image.bin      # differs
cyanrip -d image.cue -N -A -Q -s 0 -o pcm -P 0 -D out0 -F '{track}'
cat out0/1.pcm out0/2.pcm | cmp - image.bin    # identical
```

`-o pcm` writes raw little-endian 16-bit stereo, so for an image with no
pregaps the tracks concatenated are the `.bin` byte for byte.

Sweeping the constant and comparing the decoded PCM against the source `.bin`
directly — not against another cyanrip build:

| `cachemodel_size` | matches source | non-zero samples | `Ripping errors:` |
|---|---|---|---|
| **1** (current) | **no** | **0.3 %** | **0** |
| **4** | **no** | 94.5 % | **0** |
| 5 | yes | 99.2 % | 0 |
| 16 | yes | 99.2 % | 0 |
| 512 | yes | — | 1 |
| 1200 (default) | yes | — | 2 |

Two things worth drawing out:

- **`Ripping errors: 0` throughout the corrupting range.** The failure is
  silent. A user has no signal that anything is wrong, which is what makes this
  worth fixing rather than documenting.
- **4 is corrupt too, and far less obviously.** At 1 the output is 99.7 %
  silence and unmistakable; at 4 it is 94.5 % non-zero and still does not match
  the source. Anyone testing a fix by ear, or by "is it mostly not silence",
  will pass a broken value.

The upper end is bounded by the original problem the commit fixed: at 512 and
above, the backseek probe over-reads the leadout and that gets counted as a read
error. So the workable window is roughly 5–256 for this image, and the upper
bound scales with the image's length.

### Suggested fix

One integer:

```c
cdio_paranoia_cachemodel_size(ctx->paranoia, 16);
```

16 sits an order of magnitude clear of the corruption boundary and an order of
magnitude below where over-reading the leadout starts costing errors. The margin
below the upper bound matters more than the exact figure, since that bound moves
with image size.

### Notes

- Affects `0.9.4-rc1` and anything after [`c431d58`](https://github.com/cyanreg/cyanrip/commit/c431d58), including `0.9.4-rc2`,
  `0.9.4-rc3` ([`e129ad9`](https://github.com/cyanreg/cyanrip/commit/e129ad9)) and `master` at [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a), where the switch above is
  unchanged (`src/cyanrip_main.c:271-276`); measured on [`f8ebf48`](https://github.com/cyanreg/cyanrip/commit/f8ebf48) on
  2026-09-27.
- Upstream's own image tests all rip at `-P 0` (`tests/rip_images.py` at
  [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a)), which may be why it has not been seen there.
- Real drives were never affected; the guard is on the image drivers only.
- `-P 0` is byte-perfect on both, so a caller that always passes `-P 0` sees nothing.
- Found and fixed downstream in `rmccann-hub/cyanrip` (`platterpus-fork`), where
  the same table is recorded in a comment beside the constant. Happy to open a
  PR if the value is agreed — the reason it is not attached here is that the
  right number is a judgement about the margin, not a mechanical change.

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 9 of 31

**Title:** `-r` reaches libcdio-paranoia unrounded, and `-r 3` never returns on a bad sector

<!-- BODY START -->

**Where:** `src/cyanrip_main.c:486`, `cdio_paranoia_read_limited(ctx->paranoia,
&status_cb, …)` with the `-r` value as the per-frame retry limit.

**What happens:** `cdio_paranoia_read_limited()` compares its retry counter with
the limit only inside `if (retry_count % 5 == 0)` (`lib/paranoia/paranoia.c`,
read at libcdio-paranoia `384f4da`). A limit that is not a multiple of 5 is
never matched, so on a sector that will not read the call does not return.
Measured on this fork before the fix, with the same call and one sector of a disc
image made unreadable: at the default paranoia level `-r 3` did not finish in
90 s, and `-r 10` finished in about a second. Upstream's default, 10, is safe;
`-r 3`, `-r 0` and any other non-multiple of 5 are not.

**What the fork did:** the per-frame half of `-r` is rounded up to a multiple of
5, at least 5, and the log says both numbers when they differ ([`2af669e`](https://github.com/rmccann-hub/cyanrip/commit/2af669e), "Round
the per-frame retry limit up to a multiple of 5, which libcdio-paranoia needs").
The library's check is arguably a libcdio-paranoia defect too, and worth a report
there.

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 10 of 31

**Title:** `media` is tagged from the `-H` setting, so every `-H` rip says HDCD

<!-- BODY START -->

**Where:** `src/cyanrip_main.c:1960`, `ctx->settings.decode_hdcd ? "HDCD" :
"CD"`, set before a sample is read. Related, not a duplicate: #50.

**What happens:** every file ripped with `-H` is tagged `media: HDCD`, whether or
not the disc carries HDCD, and the log reports `HDCD detected: no` for the same
rip. Observed on this fork on a real drive: every `-H` rip of a non-HDCD disc.

**What the fork did:** the tag is `CD`. Whether a disc is HDCD is a measurement
the log already reports, not a setting ([`ed4a377`](https://github.com/rmccann-hub/cyanrip/commit/ed4a377), "Tag media as CD whatever -H
says").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 11 of 31

**Title:** The AccurateRip tally counts a track whose read was interrupted

<!-- BODY START -->

**Where:** `src/cyanrip_log.c:357`, in `cyanrip_log_finish_report()`, which
tests only `t->ar_db_status == CYANRIP_ACCUDB_FOUND`.

**What happens:** a SIGINT during a track's read still reaches the report. If the
read got past sector 450, the one-sector `Accurip 450` checksum can match the
database, so the disc's partial-match tally counts a track that was not ripped.
This is read from upstream's source, not run upstream; it was found on this fork
in a real rip.

**What the fork did:** the tally counts only tracks whose read completed
([`f26668b`](https://github.com/rmccann-hub/cyanrip/commit/f26668b), "Leave an interrupted track out of the AccurateRip tally").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 12 of 31

**Title:** A 450 lookup falls through to the whole-track checksum on a miss

<!-- BODY START -->

**Where:** `src/accurip.c:264-267`:

```c
        if (is_450 && e->checksum_450 == checksum)
            return e->confidence;
        else if (e->checksum == checksum)
            return e->confidence;
```

**What happens:** when a 450 lookup misses an entry's frame checksum, the
one-frame checksum is then compared with the entry's whole-track checksum. A
false match has one chance in 2^32 per entry, so no real rip has been seen to
show it. But it reaches the `Accurip 450` log line and the `-f` offset search,
which scans thousands of offsets per track. Found by Platterpus, reading this
fork's copy of the same code.

**What the fork did:** a 450 lookup compares only 450 checksums ([`10f36fe`](https://github.com/rmccann-hub/cyanrip/commit/10f36fe),
"Compare only 450 checksums on a 450 AccurateRip lookup").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 13 of 31

**Title:** The AccurateRip disc status can never read `mismatch`

<!-- BODY START -->

**Where:** `src/accurip.c:196`, in `crip_fill_accurip()`, before the loop over
the response's entries:

```c
    ctx->ar_db_status = CYANRIP_ACCUDB_FOUND;
```

and the arm it disables, `:213-214`:

```c
            if (ctx->ar_db_status != CYANRIP_ACCUDB_FOUND)
                ctx->ar_db_status = CYANRIP_ACCUDB_MISMATCH;
```

**What happens:** the status is already `FOUND` when the first entry is read,
so the `MISMATCH` assignment never runs. A response whose entries all carry
another disc's ids reads `AccurateRip:    found`. The report then prints `Tracks ripped accurately: 0/N`, which reads as a comparison
that found nothing, over a comparison that never happened. Read from the
source: no real response has been seen to have that shape, because a dBAR file
is named by the ids it holds.

Upstream's [`76dcd5d`](https://github.com/cyanreg/cyanrip/commit/76dcd5d) ("Don't trust AccurateRip and cover art replies to be
well formed") fixed part of this: a reply with no body is now taken as no
entry, and reads `not found` (`:177-180`). A response holding only another
disc's entries still reads `found`. Related, not a duplicate: #24.

**How to reproduce:** call the parse on any recorded dBAR response with one
disc id changed, and read the disc status.

**What the fork did:** the status starts at `NOT_FOUND` and becomes `FOUND`
only when an entry for this disc is read, so that response reads `mismatch`
and prints no tally ([`64642db`](https://github.com/rmccann-hub/cyanrip/commit/64642db), "Let the AccurateRip
disc status say mismatch and not found"). The fork first split the parse out
of the fetch, unchanged, so a recorded response can be tested with no network
([`5b7493c`](https://github.com/rmccann-hub/cyanrip/commit/5b7493c)).

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 14 of 31

**Title:** A one-frame AccurateRip entry under the threshold is logged as `(not found)`

<!-- BODY START -->

**Where:** `src/cyanrip_log.c:180-187`, the `Accurip 450:` line, reached when
both whole-track checksums missed:

```c
            if (has_ar && (match_450 > (3*(t->ar_db_max_confidence+1)/4)) && (t->acurip_checksum_v1_450 == 0x0)) {
                ...
            } else if (has_ar && (match_450 > (3*(t->ar_db_max_confidence+1)/4))) {
                ...
            } else if (has_ar) {
                cyanrip_log(ctx, 0, " (not found)\n");
```

**What happens:** `crip_find_ar()` returns the matching entry's confidence, or
-1 when no entry carries the checksum. Every result at or below the threshold
falls to the last arm, so an entry that was found at a lower confidence is
logged as `(not found)`, the same words as a checksum no entry carries. The
log then denies a lookup result the program had. The threshold itself is not
in question; the words are. A zero checksum found under the threshold gets the
same `(not found)`, where above it the line says a zero is meaningless.

**How to reproduce:** any track whose whole-track checksums miss and whose
frame-450 checksum matches an entry at a confidence of at most
`3*(max+1)/4`, for example confidence 6 on a track whose top entry is 7.

**What the fork did:** the line says the entry was found, with its confidence
and the threshold it needed to pass, and a zero checksum's caveat holds at any
confidence ([`b1857d6`](https://github.com/rmccann-hub/cyanrip/commit/b1857d6), "Say a one-frame AccurateRip entry was found when the
threshold rejects it"). The tally of partial matches is unchanged.

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 15 of 31

**Title:** A track's success line ignores paranoia's skips and a `-Z` repeat limit

<!-- BODY START -->

**Where:** `src/cyanrip_main.c:1227-1230`, at the end of `cyanrip_rip_track()`:

```c
        if (ctx->total_error_count - start_err)
            cyanrip_log(ctx, 0, "Track %i ripped and encoded with errors.\n", t->number);
        else
            cyanrip_log(ctx, 0, "Track %i ripped and encoded successfully!\n", t->number);
```

and the repeat limit at `:1174-1177`, which reaches the same lines:

```c
        if (total_repeats >= ctx->settings.max_retries) {
            cyanrip_log(ctx, 0, "\nDone; (no matches found, but hit repeat limit of %i)\n",
                        ctx->settings.max_retries);
            goto finalize_ripping;
```

**What happens:** `total_error_count` moves only when the drive reports an
error or returns no data. A stretch paranoia gave up verifying and skipped is
neither, so a track with thousands of skips prints `ripped and encoded
successfully!`. So does a `-Z` track whose reads never agreed. On a real
damaged disc in the fork's testing, one track printed the success line over
2,586 skips, and five tracks read five ways each printed it too.

Upstream's #70, closed in October 2023, reported the same symptom, and the
maintainer declined it. What is new here is where it shows: the success line
itself, which a reader takes as the verdict on the track, and the `-Z` repeat
limit, which reaches the same line over reads that never agreed.

**How to reproduce:** rip a disc paranoia has to skip on, and compare the
track's success line with the per-track `SKIP` counter; or rip with `-Z 2`
and a repeat limit on a disc that reads differently each time.

**What the fork did:** the line reads `with errors` when the track's last read
skipped ([`e5a0897`](https://github.com/rmccann-hub/cyanrip/commit/e5a0897), "Read a track with paranoia skips as read with errors")
or when `-Z` hit the repeat limit ([`4529810`](https://github.com/rmccann-hub/cyanrip/commit/4529810), "Read a -Z track that hit the
repeat limit as read with errors").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 16 of 31

**Title:** A failed track ends a rip of every track silently, and the album is finalised over it

<!-- BODY START -->

**Where:** `src/cyanrip_main.c:2295-2296`, the loop over every track:

```c
                if (cyanrip_rip_track(ctx, t))
                    break;
```

against the loop over the tracks `-l` names, `:2425-2428`:

```c
            ret = cyanrip_rip_track(ctx, t);
            if (ret < 0) {
                cyanrip_log(ctx, 0, "Error ripping: %s\n", av_err2str(ret));
                goto end;
            }
```

**What happens:** with `-l`, a failed track prints `Error ripping:` and ends
the run. Without it, the same failure leaves the loop with no message and
carries on: the album's loudness is finalised (`:2303-2304`) and, with
ReplayGain on, the album tags are written (`:2306-2309`), over a disc whose
tracks were not all ripped. Any failure `cyanrip_rip_track()` returns reaches
it, a changed medium included.

**How to reproduce:** rip a disc without `-l` and make one track fail, for
example by changing the medium mid-rip, then compare with the same failure
under `-l`.

**What the fork did:** both loops print `Error ripping: %s` and end the run
([`c1e1ab1`](https://github.com/rmccann-hub/cyanrip/commit/c1e1ab1), "Abort the rip of every track on a failed track, as -l does").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 17 of 31

**Title:** A stopped `-f` search is retried with a larger radius

<!-- BODY START -->

**Where:** `src/cyanrip_main.c:582-585`, where a stop during a track's read
leaves the search:

```c
            if (quit_now) {
                cyanrip_log(ctx, 0, "Stopping, offset finding incomplete!\n");
                goto end;
            }
```

and `:623-635`, which the `goto` lands in:

```c
    if (!offset_found) {
        if (!had_ar) {
            ...
        } else if (had_ar && !did_check) {
            cyanrip_log(ctx, 0, "No track was long enough, unable to find drive offset!\n");
        } else {
            cyanrip_log(ctx, 0, "Was not able to find drive offset with a radius of %i frames"
                        ", trying again with a larger radius...\n", range);
            return search_for_drive_offset(ctx, 2*range);
        }
```

**What happens:** nothing after `end:` asks whether the search was stopped.
A track is marked checked (`did_check`, `:568`) before the frame-read loop
that holds the stop, so a stop always reaches the last arm: it prints `trying
again with a larger radius`, reads a frame, stops again, and repeats until the
radius outgrows every track.

**How to reproduce:** run `-f` on a disc in AccurateRip and send SIGINT
during the search.

**What the fork did:** a stop ends the search, and every stopped search prints
`Stopping, offset finding incomplete!` ([`aa1f067`](https://github.com/rmccann-hub/cyanrip/commit/aa1f067), "Say what a -J or -f run
was, and end a -f search on a stop").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 18 of 31

**Title:** The footer can count a one-frame match the track's lines never printed

<!-- BODY START -->

**Where:** `src/cyanrip_log.c:358-363`, the disc tally in
`cyanrip_log_finish_report()`:

```c
                if ((crip_find_ar(t, t->acurip_checksum_v1, 0) > 0) ||
                    (crip_find_ar(t, t->acurip_checksum_v2, 0) > 0))
                    accurip_verified++;
                else if (crip_find_ar(t, t->acurip_checksum_v1_450, 1) > (3*(t->ar_db_max_confidence+1)/4) &&
                         t->acurip_checksum_v1_450)
                    accurip_partial++;
```

against the gate on the track's own `Accurip 450:` line, `:176`:

```c
        if (!has_ar || ((match_v1 < 0) && (match_v2 < 0))) {
```

**What happens:** the track prints its 450 line only when both whole-track
lookups missed (`< 0`); the tally counts a partial match whenever neither
matched (`not > 0`). The two part on a confidence of exactly 0, which only a
malformed AccurateRip response carries: a track whose v1 matches such an entry
prints no 450 line, while the footer counts it in `Tracks ripped partially
accurately:` if another entry carries its frame checksum above the threshold.
Read from the source, not seen on a real response.

**How to reproduce:** feed the report a track whose v1 checksum matches an
entry of confidence 0, beside a second entry carrying the track's frame-450
checksum at a confidence over `3*(max+1)/4`.

**What the fork did:** the tally uses the per-track gate, so it counts exactly
the 450 lines that say `matches Accurip DB` ([`8ab9a8d`](https://github.com/rmccann-hub/cyanrip/commit/8ab9a8d), "Count a one-frame
match in the footer only where the track's line says so").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 19 of 31

**Title:** A disc image is taken for a drive with libcdio 2.3.0 or later

<!-- BODY START -->

**Where:** `src/cyanrip_main.c:1940-1945` at [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a), the offset check:

```c
    if (!settings.offset && !offset_set && !settings.print_info_only &&
        !find_drive_offset_range && (ctx->rcap & CDIO_DRIVE_CAP_READ_ISRC)) {
        cyanrip_log(ctx, 0, "Offset is unset! To continue with an offset of 0, run with -s 0!\n");
        ctx->total_error_count++;
        goto end;
    }
```

and `:667`, the gate on the sub-channel pre-emphasis read:

```c
        if (!t->preemphasis && (ctx->rcap & CDIO_DRIVE_CAP_READ_ISRC)) {
```

**What happens:** both use `CDIO_DRIVE_CAP_READ_ISRC` to tell a drive from a
disc image. libcdio's `998d123` ("Image driver supports ISRC", 2025-03-29,
first released in 2.3.0) added that bit to the capabilities of all three image
drivers. So with libcdio 2.3.0 or later, ripping a CUE, NRG or TOC image
without `-s` stops at `Offset is unset!` and exits 1. With `-s 0`, every track
that lacks the TOC pre-emphasis flag logs `Unable to read track N subchannel
info!`, because no image driver implements `cdio_audio_read_subchannel()`
(read from libcdio's source at 2.4.0). It showed on macOS, against Homebrew's
libcdio 2.4.

**How to reproduce:** with libcdio 2.3.0 or later, `cyanrip -d disc.cue -N -A
-U -o flac` exits 1 at `Offset is unset!`; add `-s 0` and every track logs the
sub-channel failure. Run here on a build of [`b40c1f0`](https://github.com/cyanreg/cyanrip/commit/b40c1f0) against libcdio 2.1,
through an `LD_PRELOAD` shim that adds the bit for an image driver as 2.3.0
does. Without the shim, a two-track CUE image rips and exits 0. With it, the
same command exits 1 at `Offset is unset!`, and with `-s 0` both tracks log
`Unable to read track N subchannel info!`.

**What the fork did:** both checks ask the driver, with `cdio_get_driver_id()`
against the three image drivers, as upstream's own cache-model switch already
does (`:271-274`). The ISRC read at `:648` is left alone, because from 2.3.0
an image really does serve one ([`faec396`](https://github.com/rmccann-hub/cyanrip/commit/faec396), "Tell an image from a drive by its
driver, not by CDIO_DRIVE_CAP_READ_ISRC").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 20 of 31

**Title:** `-Y` on a directory overflows a signed length

<!-- BODY START -->

**Where:** `src/fun512.c:69-75` at [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a), in `cyanrip_verify_log()`:

```c
    fseek(f, 0, SEEK_END);
    long int len = ftell(f);
    rewind(f);
    if (len <= 0 || !(data = av_mallocz(len + 1))) {
        fclose(f);
        return CRIP_LOG_IO_ERROR;
    }
```

**What happens:** `fopen()` on a directory succeeds, and on ext4 `ftell()`
then returns `LONG_MAX`. So `len <= 0` is false, and `len + 1` is signed
overflow, which C leaves undefined. A release build survives it only because
the wrapped value makes `av_mallocz()` fail, and the run then prints
`Couldn't read "<dir>"!`: the right answer, reached through undefined
behaviour.

**How to reproduce:** build with `-Db_sanitize=undefined` and run `cyanrip -Y
<a directory>` on ext4. Run here on a build of [`b40c1f0`](https://github.com/cyanreg/cyanrip/commit/b40c1f0): `fun512.c:72:45:
runtime error: signed integer overflow: 9223372036854775807 + 1 cannot be
represented in type 'long int'`, then `Couldn't read "adir"!`, exit 1.

**What the fork did:** the length is bounded before anything is added to it,
by a cap of 64 MiB, far above any rip log, and a file over the cap is an I/O
error ([`72975de`](https://github.com/rmccann-hub/cyanrip/commit/72975de), "Bound the FUN512 read, and run the teardown on the two
paths that skipped it").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 21 of 31

**Title:** A failed read in `-Y` is reported as a log with no checksum

<!-- BODY START -->

**Where:** `src/fun512.c:76-77` at [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a), in `cyanrip_verify_log()`:

```c
    len = fread(data, 1, len, f);
    data[len] = '\0';
```

**What happens:** what `fread()` returns becomes the length, and is never
compared with what `ftell()` gave; `ferror()` is not asked either. A read that
fails leaves an empty buffer, which is parsed, holds no checksum line, and is
reported as `No FUN512 checksum found`: a read that did not happen, reported as
a fact about the log. On macOS, `fopen()` on a directory succeeds, `ftell()`
gives the directory's own small size, and `fread()` fails, so `cyanrip -Y <a
directory>` says the log has no checksum rather than that it could not be
read. A file that shrinks between `ftell()` and `fread()` is parsed short in
the same way.

**How to reproduce:** on macOS, `cyanrip -Y <a directory>`. Not run here: no
filesystem in this Linux container gives a directory a small positive size.
It was seen in the fork's CI on macOS, where this read was still upstream's
line for line.

**What the fork did:** a read that fails, or returns fewer bytes than
`ftell()` gave, is an I/O error ([`d109c56`](https://github.com/rmccann-hub/cyanrip/commit/d109c56), "Report a log that cannot be read
as an I/O error, not as one without a checksum").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 22 of 31

**Title:** The paranoia counters are printed with `%lu` from `uint64_t`

<!-- BODY START -->

**Where:** `src/cyanrip_log.c:383` at [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a), in the `PCHECK()` macro,
which `:387-402` use sixteen times:

```c
        cyanrip_log(ctx, 0, "%lu\n", paranoia_status[PARANOIA_CB_ ## PROP]);   \
```

with `paranoia_status` declared `uint64_t` (`src/cyanrip_main.h:316`,
`src/cyanrip_main.c:472`).

**What happens:** `%lu` takes an `unsigned long`. `uint64_t` is
`unsigned long` on 64-bit Linux, so the line is right there. On macOS it is
`unsigned long long`, and on Windows `long` is 32 bits, so there the
conversion does not match its argument, which C99 7.19.6.1p9 makes undefined
behaviour. No compiler says so, because `cyanrip_log()` has no format
attribute (`src/cyanrip_log.h:33`). What a build for either platform prints
was not run here.

**How to reproduce:** give `cyanrip_log()` a printf format attribute and build
for macOS or Windows with `-Wformat`; all sixteen lines warn. Checked here with
clang on a minimal file holding the same call, `uint64_t` through `%lu` to a
function with that attribute: `--target=arm64-apple-darwin`,
`x86_64-apple-darwin`, `x86_64-w64-windows-gnu` and `i686-w64-windows-gnu`
each warn `format specifies type 'unsigned long' but the argument has type
'uint64_t' (aka 'unsigned long long')`, and `x86_64-linux-gnu` does not.

**What the fork did:** each counter is cast to `unsigned long long` and
printed with `%llu`, which prints the same digits everywhere ([`09492a5`](https://github.com/rmccann-hub/cyanrip/commit/09492a5),
"Print the paranoia counters with %llu, which fits uint64_t everywhere"). The
fork's `cyanrip_log()` carries a format attribute, which is how its macOS
build found this.

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 23 of 31

**Title:** Three start-up failures return without tearing the context down

<!-- BODY START -->

**Where:** `src/cyanrip_main.c:218-225` at [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a), in `cyanrip_ctx_init()`:

```c
    if (!(ctx->drive = cdio_cddap_identify_cdio(ctx->cdio, CDDA_MESSAGE_LOGIT, &msg))) {
        cyanrip_log(ctx, 0, "Unable to init cddap context!\n");
        if (msg) {
            cyanrip_log(ctx, 0, "cdio: \"%s\"\n", msg);
            cdio_cddap_free_messages(msg);
        }
        return AVERROR(EINVAL);
    }
```

and `:2082-2086`, in `main()`:

```c
    if (!ctx->settings.print_info_only) {
        if (!ctx->settings.generate_cue_only && cyanrip_log_init(ctx))
            return 1;
        if (cyanrip_cue_init(ctx))
            return 1;
```

**What happens:** the two failure paths before the first of these, in the same
function, call `cyanrip_ctx_end()`. These three return without it, so the
context is not freed and the device is not closed before the process exits.
Because the process exits straight after, what a user can see is small:
LeakSanitizer reports the context, and when the CUE sheet cannot be opened,
the logfile already created is left at 0 bytes, with nothing in it to say why.

**How to reproduce:** on a build of [`b40c1f0`](https://github.com/cyanreg/cyanrip/commit/b40c1f0) with `-Db_sanitize=address`, run
here:

- `cyanrip -d /dev/null -I`: `Unable to init cddap context!`, exit 1, and
  LeakSanitizer reports the 479,824-byte context.
- `cyanrip -d disc.cue -N -A -U -s 0 -o flac -D <a regular file>/out -L log`:
  `Couldn't open path ... Not a directory!`, exit 1, and 12,834,961 bytes
  leaked in 36 allocations.
- The same with `-D dir -M sheet`, where `dir/sheet.cue` is a directory: the
  CUE sheet fails the same way, with the same leak, and `dir/log.log` is left
  at 0 bytes.

**What the fork did:** all three call `cyanrip_ctx_end()` ([`3f0e161`](https://github.com/rmccann-hub/cyanrip/commit/3f0e161) for the
first, [`72975de`](https://github.com/rmccann-hub/cyanrip/commit/72975de) for the other two). The fork later sent the log and CUE
failures to `end:` instead, so the log that was opened carries the run's
completion footer ([`a79ac9e`](https://github.com/rmccann-hub/cyanrip/commit/a79ac9e), "Emit the completion footer on the last two
paths that skipped it").

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 24 of 31

**Title:** An argument that is only its separator crashes with no message

<!-- BODY START -->

**Where:** `src/cyanrip_main.c:1740-1741` at [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a), for `-c`:

```c
        p = av_strtok(disc, "/", &p_save);
        discnumber = strtol(p, NULL, 10);
```

and `:1806-1807`, for `-p`:

```c
        p = av_strtok(pregap[i], "=", &p_save);
        idx = strtol(p, NULL, 10);
```

**What happens:** a string of nothing but delimiters yields no token, so `p`
is `NULL` and `strtol()` dereferences it. The second `av_strtok()` in each
block is checked for `NULL`; the first is not, because a non-empty string was
assumed to yield a token. The process dies by signal before printing anything,
so a caller sees a non-zero exit and not one line saying why.

**How to reproduce:** on a build of [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a), with any disc image:

- `cyanrip -d disc.cue -I -N -A -U -s 0 -c /`: exit 139, no output.
- The same with `-c //`, `-p =` or `-p ==`: exit 139, no output.

**What the fork did:** both check the first token, and print `Missing
discnumber` or `Missing track idx for pregap` and exit 1 ([`58f5151`](https://github.com/rmccann-hub/cyanrip/commit/58f5151), "Fix two
NULL derefs on arguments that are only a separator"). Found on 2026-08-06 by
giving the fork's argument probe a malformed-shape axis; it had no report until
2026-10-19.

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 25 of 31

**Title:** A number past `INT_MAX` wraps and is used

<!-- BODY START -->

**Where:** `src/cyanrip_main.c` at [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a), six arguments genopt does not
parse, each read with `strtol()` straight into an `int`:

| line | argument | code |
|---|---|---|
| 1694 | `-P` | `settings.paranoia_level = (int)strtol(paranoia, NULL, 10);` |
| 1729 | `-R` | `mb_release_idx = strtol(release, &p, 10);` |
| 1741, 1748 | `-c` | `discnumber = strtol(p, NULL, 10);`, `totaldiscs = strtol(p, NULL, 10);` |
| 1807 | `-p` | `idx = strtol(p, NULL, 10);` |
| 1861 | `-C` | `idx = strtol(p, NULL, 10);` |
| 2119 | `-t` | `int u_nb = strtol(track_metadata_ptr[i], &end, 10);` |

**What happens:** on a 64-bit `long`, `strtol()` returns the whole value and
the assignment keeps its low 32 bits, so a value past `INT_MAX` becomes
whatever it wraps to, and the range check after it tests that instead. The
argument is then used, with exit 0, as a value the caller did not type.

**How to reproduce:** on a build of [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a), with any disc image and `-d
disc.cue -I -N -A -U -s 0`:

- `-c 4294967297/4294967297`: exit 0, `Disc number:    1`, and the log and CUE
  names lose their `CD` suffix, because the total read as 1.
- `-c 1/4294967298`: exit 0, disc 1 of 2.
- `-P 4294967296`: exit 0, `Paranoia level: none`. `-P 4294967297`: level 1.
- `-t 4294967297=title=x` and `-p 4294967297=drop`: exit 0, applied to track 1.
- `-R 4294967297`: exit 0, release 1.
- `-c 2147483648/2147483648`: refused, but as `Invalid discnumber
  -2147483648`, a number the caller did not type.

And one shape beside them: `av_strtok()` skips a leading delimiter, so `-c /2`
reads its total as the disc number and gives exit 0 and `Disc number:    2`.

**What the fork did:** each is read with `strtoll()` into a `long long` and
range-checked before it is narrowed, and refused with the message a smaller bad
value always got, printed with `%lli`, so it names the number typed; every
message that rendered before renders the same. `-c /2` is refused as `Missing
discnumber`. All in [`716a99b`](https://github.com/rmccann-hub/cyanrip/commit/716a99b), "Refuse integer arguments past INT_MAX instead
of using what they wrap to". Found on 2026-10-19, adding boundary rows to the
fork's argument probe.

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 26 of 31

**Title:** The AccurateRip tally divides by a count that includes data tracks

<!-- BODY START -->

**Where:** `src/cyanrip_log.c:366` at [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a), in
`cyanrip_log_finish_report()`:

```c
cyanrip_log(ctx, 0, "Tracks ripped accurately: %i/%i\n", accurip_verified, ctx->nb_tracks);
```

and the partial line beside it, which divides by `ctx->nb_tracks -
accurip_verified`. `ctx->nb_tracks` is `cdio_cddap_tracks()`, every track the
drive reports (`src/cyanrip_main.c:286`), with data tracks marked inside it
(`:307`); `crip_fill_accurip()` skips a data track (`src/accurip.c:224`), so
it never gets an AccurateRip status.

**What happens:** a data track can never be counted as verified, but it is
always counted in the total. On a mixed-mode or enhanced disc whose audio
tracks all verify, the footer reads `Tracks ripped accurately: 2/3`, and a
reader of that line alone sees a track left unverified. The partial line's
denominator counts the data track too. This is read from upstream's source,
not run upstream: no disc image is in AccurateRip's database. On the fork
before its fix, the footer printed `2/3` for a three-track disc whose track 1
is data and whose two audio tracks verify, a state built the way the fork's
`tests/logrender.c` builds the footer.

**What the fork did:** both lines divide by the disc's audio tracks, the tracks
the drive reports less those it reports as data ([`779549a`](https://github.com/rmccann-hub/cyanrip/commit/779549a), "Count the
footer's AccurateRip tally over the disc's audio tracks"). A rip of some
tracks with `-l` still divides by the disc's count. Found on 2026-10-21,
answering Platterpus's question.

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 27 of 31

**Title:** A value the log echoes can start a line of its own

<!-- BODY START -->

**Where:** `src/cyanrip_log.c:207` at [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a), in the track block's metadata
loop:

```c
cyanrip_log(ctx, 0, "%s\n", d->value);
```

and `cyanrip_log()` itself (`src/cyanrip_log.c:524-549`), which passes the
format and its arguments to `vfprintf()` for each logfile and to `vprintf()`
for stdout as they are. Every other line that prints a tag, a path or a
library's message through `%s` does the same.

**What happens:** a value carrying a line break is written as one, so the rest
of the value is a line of the log of the value's choosing. A title given with
`-t` as `Two`, a newline and `  Accurip\:       accurately ripped`, its colon
typed as `\:` so that `-t` does not split there, puts a line shaped like the
track block's own `  Accurip:` line into the log (run on a build of [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd)
on 2026-11-16, exit 0), and a
logchecker or any tool that reads the log a line at a time takes it for the
program's. A newline is not the only way in: a CD-TEXT field that carries the
byte 0x85 arrives as U+0085, NEXT LINE, because libcdio reads a cdrdao `.toc`'s
CD-TEXT as ISO-8859-1, and Python's `str.splitlines()`, among others, ends a
line there; so do a vertical tab, a form feed and U+2028. This is read from
upstream's source. On the fork, whose metadata loop and log function were
upstream's until the fix, a `.toc` whose track 1 CD-TEXT title carries 0x85
followed by `Accurip: accurately ripped (forged)` gave the log a line reading
exactly that, and a `-t` title with a newline did the same.

**What the fork did:** the log function formats each message once and writes
every `%s` argument escaped: each control character but the tab, and U+2028
and U+2029, as `<U+XXXX>`, and each byte that is not well-formed UTF-8 as
`<0xHH>`; every other conversion is `printf()`'s, so a value without those
characters is written byte for byte ([`46cec2a`](https://github.com/rmccann-hub/cyanrip/commit/46cec2a), "Escape every value the log
writes, so none can start a line of its own"). The tags written to the files
keep the value as it came. Found on 2026-10-26 by a review of the fork.

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `7dbe56a`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 28 of 31

**Title:** A path over 1,003 bytes is cut there, extension and all

<!-- BODY START -->

**Where:** `src/naming.c:410` at [`7dbe56a`](https://github.com/cyanreg/cyanrip/commit/7dbe56a) and at [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd), in
`crip_get_path()`:

```c
av_bprint_init(&buf, 0, AV_BPRINT_SIZE_AUTOMATIC);
```

`AV_BPRINT_SIZE_AUTOMATIC` limits the buffer to the one inside the `AVBPrint`
structure itself, which FFmpeg pads to 1,024 bytes, and
`av_bprint_finalize()` (`:453`) returns whatever fitted without saying that
anything did not. Every path the program writes comes from this function:
each track, the log, the CUE sheet and the cover art.

**What happens:** a path longer than 1,003 bytes is cut at byte 1,003, so the
file loses its extension and the end of its name, and every file whose path
shares those 1,003 bytes goes to the same file. Each component can be within
the 255 bytes a filesystem allows, so nothing refuses it. Run on the fork
before its fix, whose `crip_get_path()` was upstream's here: `basic.cue`, two
audio tracks, ripped with `-o flac`, an album of 200 bytes and `-D
"<root>/{album}/{album}/{album}/{album}/{album}"` from a 90-byte root, left
one file on disk, 1,003 bytes of path with no extension, a FLAC stream with
the log's text written into it. The log, the CUE sheet and both tracks had
been written to it. The rip printed `WARNING: tracks 1 and 2 resolve to the
same file` and `Rip completed:  yes (2 of 2 tracks)`, and exited 0. Run on a
build of upstream's [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd) on 2026-11-16, with a 92-byte root, a 200-byte
album and five `{album}` components, `-o flac`: exit 0, the same warning,
both tracks `ripped and encoded successfully!`, `Ripping errors: 0`, and one
file on disk whose path is 1,003 bytes with no extension. Which file is
written last differs from the fork's run, and the cut is the same.

**What the fork did:** `crip_get_path()` renders with
`AV_BPRINT_SIZE_UNLIMITED` and returns `NULL` if the buffer could not be
completed, so a path is either whole or not given ([`cfd738e`](https://github.com/rmccann-hub/cyanrip/commit/cfd738e), "Render a
path whole, past the 1,003 bytes an AVBPrint holds"). The same rip leaves
the log, the CUE sheet and both tracks, each under its own name. Found on
2026-10-30.

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `648b1dd`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 29 of 31

**Title:** `C2 errors: unsupported by drive` is printed for a disc image, and for a drive that returns C2 pointers

<!-- BODY START -->

**Where:** `src/cyanrip_log.c:275-276` at [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd), in `cyanrip_log_start_report()`:

```c
    cyanrip_log(ctx, 0, "C2 errors:      %s by drive\n", (ctx->rcap & CDIO_DRIVE_CAP_READ_C2_ERRS) ?
                "supported" : "unsupported");
```

`ctx->rcap` is what `cdio_get_drive_cap()` returned at start-up
(`src/cyanrip_main.c:215`). Nothing else in `src/` mentions C2. No read asks
the drive for C2 pointers.

**What happens:** the line turns one capability bit into a statement about
what the drive can do. In the fork's reading of libcdio, the bit is the C2
pointers bit of the drive's capabilities mode page, 2Ah: it says what the drive
declares, not what it can do. In three cases the line says something false:

- **A disc image** has no drive and no capabilities page. libcdio's BIN/CUE
  driver answers the query with a fixed set, and that set leaves the C2 bit
  clear. With libcdio 2.1.0 the read word is `0x0701e` and the misc word is
  `CDIO_DRIVE_CAP_MISC_FILE`, "drive is really a file". So a rip of a CUE image
  says `C2 errors:      unsupported by drive`, under `Drive used:     libcdio
  CDRWIN (revision 2.1.)`.
- **A drive can deny C2 in that page and still return C2 pointers when
  asked.** The fork measured its test drive, a PIONEER BD-RW BDR-209D (revision
  1.51):
  - Page 2Ah's byte 5 is `63h` under all four page controls, so its C2
    pointers bit is 0.
  - The CD Read feature (001Eh) of GET CONFIGURATION says `C2 flags=1`.
  - A READ CD with byte 9 = `12h`, which asks for C2 error pointers, returned
    them. In four reads of four, they flagged the same three bytes of one frame
    of track 5. That frame is where that disc's rips of track 5 differed from a
    CTDB entry by three samples.
  - Every log cyanrip writes on that drive says `unsupported by drive`.
- **A failed query.** In the fork's reading of libcdio at `68ea374`
  (`lib/driver/mmc/mmc.c:866-870`), a failed MODE SENSE sets every capability
  word to `CDIO_DRIVE_CAP_ERROR`. That leaves the C2 bit clear, so the line
  says `unsupported by drive` about a drive whose answer was never read.

The other arm also claims more than is true. `supported by drive` is printed on
a rip that never asks for C2 pointers, so a reader can take it that C2 was
used.

**How to reproduce:**

- **The image case**, on a build of [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd) against libcdio 2.1.0:
  1. Make a two-track image:

     ```
     ffmpeg -f lavfi -i "sine=frequency=440:duration=8:sample_rate=44100" -ac 2 -f s16le -acodec pcm_s16le disc.bin
     ```

     and a CUE sheet with `FILE "disc.bin" BINARY`, two `AUDIO` tracks, and
     `INDEX 01` at `00:00:00` and `00:04:00`.
  2. Run `cyanrip -d disc.cue -I -N -A -U -B -s 0`. It prints `C2 errors:
     unsupported by drive` and exits 0.

  The NRG and cdrdao drivers and later libcdio releases were not run.
- **The failed-query case** was not run on a drive. A preloaded
  `cdio_get_drive_cap()` that sets all three words to `CDIO_DRIVE_CAP_ERROR`
  makes the same command print `unsupported by drive`.
- **The drive case** needs a drive whose page 2Ah clears byte 5 bit 4, and
  whose READ CD still answers byte 9 = `12h` with 2,352 bytes of audio and 294
  of C2 pointers a frame. The fork's measurements above were taken with
  sg3_utils on its rig, on 2026-11-05 and 2026-11-11, not with cyanrip. Without
  such a drive they cannot be reproduced, and the case rests on the code above:
  the line's only input is the declared bit.

**What the fork did:** three changes to this one line:

- [`8499890`](https://github.com/rmccann-hub/cyanrip/commit/8499890) (2026-07-31) added `, not used` to the supported arm.
- [`819c735`](https://github.com/rmccann-hub/cyanrip/commit/819c735) (2026-10-29) prints `unknown (capabilities query failed)` when the
  read word carries `CDIO_DRIVE_CAP_ERROR`.
- [`372706f`](https://github.com/rmccann-hub/cyanrip/commit/372706f) (2026-11-13, "Say what the capabilities page declares on the C2
  errors line") says what was asked:
  - `declared supported by drive (capabilities page), not used`;
  - `not declared by drive (capabilities page, not measured)`;
  - `unknown (image)` for a disc image. The fork tells an image from a drive by
    its driver, as in item 19 ([`faec396`](https://github.com/rmccann-hub/cyanrip/commit/faec396)).
  - A failed query decides first. Log text only; no read changed.

In upstream's code the fix is this line alone. It can use the driver test
upstream already applies to the cache model (`src/cyanrip_main.c:271-274`):

```c
    int is_image = 0;
    switch (cdio_get_driver_id(ctx->cdio)) {
    case DRIVER_BINCUE:
    case DRIVER_NRG:
    case DRIVER_CDRDAO:
        is_image = 1;
        break;
    default:
        break;
    }
    cyanrip_log(ctx, 0, "C2 errors:      %s\n",
                (ctx->rcap & CDIO_DRIVE_CAP_ERROR) ? "unknown (capabilities query failed)" :
                is_image ? "unknown (disc image)" :
                (ctx->rcap & CDIO_DRIVE_CAP_READ_C2_ERRS) ?
                    "declared supported by drive (capabilities page), not used" :
                    "not declared by drive (capabilities page, not measured)");
```

The wordings are the fork's; any wording that says what was asked will do.
Applied to [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd) and run, this prints `unknown (disc image)` for the image
above. It prints `unknown (capabilities query failed)` under the preloaded
failure, which unchanged [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd) reports as `unsupported by drive`.

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `648b1dd`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 30 of 31

**Title:** A disc change mid-rip is reported as `Error ripping: Invalid argument`

<!-- BODY START -->

**Where:** `src/cyanrip_main.c:1074-1078` at [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd), in the read loop of
`cyanrip_rip_track()`:

```c
        if (get_media_changed(ctx)) {
            cyanrip_log(ctx, 0, "\nDrive media changed, stopping!\n");
            ret = AVERROR(EINVAL);
            goto fail;
        }
```

and `:903-907`, the same code in `cyanrip_rip_data_track()` with `goto end`.
Under `-l`, the loop over the listed tracks prints what comes back
(`:2425-2429`):

```c
            ret = cyanrip_rip_track(ctx, t);
            if (ret < 0) {
                cyanrip_log(ctx, 0, "Error ripping: %s\n", av_err2str(ret));
                goto end;
            }
```

**What happens:** `AVERROR(EINVAL)` renders as `Invalid argument`. So a rip
under `-l` that loses its disc ends its log on `Drive media changed,
stopping!`, then `Error ripping: Invalid argument`. That names an argument
nobody passed as the cause, right below a line that blames the device. A data
track's stop (`:905`) reaches the same line, because `cyanrip_rip_track()`
returns it (`:1001-1003`).

Without `-l`, the loop over every track does not print the return value
(`:2295-2296`, item 16), so the log stops at `Drive media changed,
stopping!`. Once that loop prints `Error ripping:` as the `-l` loop does, it
will say `Invalid argument` too.

The same two lines follow a media-change query that failed.
`get_media_changed()` counts every answer except 0 and `DRIVER_OP_UNSUPPORTED`
as a change (`:91`). So when a drive stops answering, its `DRIVER_OP_ERROR` is
logged as a changed disc and then an invalid argument. On the fork's rig on
2026-11-03, a drive failed mid-rip while the fork's stop still returned
`EINVAL`, and the fork's log ended on `Error ripping: Invalid argument`.

**How to reproduce:** no image driver reports a changed medium, so a preloaded
library answers libcdio's query instead:

```c
/* mediachanged.c: cc -shared -fPIC -o mediachanged.so mediachanged.c */
#include <stdlib.h>
#include <cdio/cdio.h>

/* Every media-change query answers $MC_ANSWER, 1 (changed) by default */
int cdio_get_media_changed(CdIo_t *p_cdio)
{
    const char *a = getenv("MC_ANSWER");
    (void)p_cdio;
    return a ? atoi(a) : 1;
}
```

The image needs two tracks and two minutes of audio, made as in item 29 with
`duration=120` and track 2's `INDEX 01` at `01:00:00`. The rip has to outlast
the once-a-second limit on the query (`:83`, `:87-88`): an 8-second image rips
before the loop asks again, and completes. On a build of [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd), on Linux,
each run below uses `-N -A -U -B -s 0 -o flac`:

- With `-l 1` and `LD_PRELOAD=./mediachanged.so`: `Drive media changed,
  stopping!`, then `Error ripping: Invalid argument`, exit 1. The log file
  ends on the same two lines, then `Log FUN512:`.
- The same without `-l`: `Drive media changed, stopping!` and no `Error
  ripping:` line; `Ripping errors: 1`, exit 1.
- `MC_ANSWER=-1` (`DRIVER_OP_ERROR`) with `-l 1`: the same two lines as the
  first run.
- Without the library, the `-l 1` rip completes with exit 0.
- A mixed-mode image whose track 1 is data, with `-l 1`: `Track 1 is data:`,
  then the same two lines, exit 1. Its data track is too short for the
  once-a-second limit, so for this run the library slept 1.1 s in its first
  call.

Not run on a drive.

**What the fork did:** two commits:

- [`30f1646`](https://github.com/rmccann-hub/cyanrip/commit/30f1646) ("Stop a lost drive's rip with EIO, not EINVAL"): each stop
  returns `AVERROR(EIO)` instead. The line then reads `Error ripping:
  Input/output error`, glibc's text, which names the device rather than the
  caller's arguments.
- [`819c735`](https://github.com/rmccann-hub/cyanrip/commit/819c735) (2026-10-29) separated a failed query from a change, as `Drive
  media change query failed (libcdio error N), stopping!`.

In upstream's code:

- Return `AVERROR(EIO)` at `:905` and `:1076`.
- Have `get_media_changed()` return libcdio's code for a failed query, `ret ==
  DRIVER_OP_UNSUPPORTED ? 0 : ret > 0 ? 1 : ret`, so each caller can tell a
  change from a failure. That includes the two `-I` loops (`:2265`, `:2373`),
  which today print `Drive media changed, stopping!` for both.

Applied to [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd) and run with the library above, the first run ends
`Error ripping: Input/output error`. With `MC_ANSWER=-1` the first line becomes
`Drive media change query failed (libcdio error -1), stopping!`.

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `648b1dd`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

## Item 31 of 31

**Title:** `Embedded cover art:` names the cover that was asked for, not what the file holds

<!-- BODY START -->

**Where:** `src/cyanrip_log.c:210` and `:229-234` at [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd), in `cyanrip_log_track_end()`:

```c
    if (!ctx->settings.disable_coverart_embedding && (t->art.source_url || ctx->nb_cover_arts)) {
```

```c
        if (ctx->settings.print_info_only)
            cyanrip_log(ctx, 0, "\n  Embedded cover art:\n    %s: %s\n",
                        dict_get(art->meta, "title"), art->source_url);
        else
            cyanrip_log(ctx, 0, "\n  Embedded cover art:\n    %s: %ix%i %s\n",
                        dict_get(art->meta, "title"), art->params->width, art->params->height, codec_name);
```

Compare the test that decides whether a muxer is given the picture at all,
`src/cyanrip_encode.c:1158-1159`:

```c
    if (art->pkt && cfmt->coverart_supported &&
        !ctx->settings.disable_coverart_embedding) {
```

**What happens:** the block is printed whenever there is a cover and `-G` is
not given, and it consults no output. Here are three ways it is false. The
first two were run.

- **An output that embeds no cover.**
  - These outputs have `coverart_supported` 0 (`src/cyanrip_main.c:67-79`):
    Opus, Vorbis, WAV, TTA, WavPack, AAC in ADTS, ALAC in `.m4a` and PCM. No
    picture stream is added for them, yet each track's block lists the cover.
  - With `-o opus -C Front=art.png`, both tracks' blocks read `Embedded cover
    art:` and `Front: 8x8 PNG (Portable Network Graphics) image`, and the run
    exits 0. Neither `.opus` file holds a picture: one stream each, and no PNG
    signature anywhere in the file.
  - The same happens with `-o wav`. For a control, the same cover with `-o
    flac` is in both files.
  - With several outputs, the one block speaks for all of them.
- **A picture the muxer refuses.**
  - FFmpeg's FLAC muxer will not write a GIF (`GIF image support is not
    implemented.`) and fails the header.
  - With `-o flac -C Front=art.gif`, both blocks list `Front: 8x8 CompuServe
    GIF (Graphics Interchange Format)`, and both tracks print `ripped and
    encoded successfully!`.
  - After the album summary come `Couldn't write header: Not yet implemented
    in FFmpeg, patches welcome!` and `Error writing to file: Not yet
    implemented in FFmpeg, patches welcome!`, twice each. The footer says
    `Ripping errors: 0`, the exit code is 1, and both `.flac` files are 0
    bytes.
  - The blocks were printed before the files were written. With ReplayGain on,
    the default (`src/cyanrip_main.c:194-195`), each file is written only after
    every track has been ripped (`:2306-2331`).
- **A picture the muxer drops.**
  - FFmpeg 6.1.1's FLAC muxer drops an AV1 or WebP picture with a warning, `No
    mimetype is known for stream 1, cannot write an attached picture.`, and
    writes the file without it.
  - This was measured with `ffmpeg` alone. The fork before its fix, whose
    block was upstream's, listed an AVIF cover as `Front: 8x8 Alliance for
    Open Media AV1` while neither FLAC held a picture.
  - Upstream does not get that far with an AVIF cover. A build of [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd)
    aborts before the first track with `free(): double free detected in tcache
    2`, exit 134, with `-o flac` or `-o pcm`. That is a separate defect: the
    cover's codec parameters are copied with `memcpy` (`src/coverart.c:62`,
    `:278`, `src/cyanrip_encode.c:1166`), so the copies share one extradata
    buffer. The fork fixed it in [`af89fcc`](https://github.com/rmccann-hub/cyanrip/commit/af89fcc).

The same `ffmpeg` 6.1.1, muxing each 8x8 picture into each container that
embeds covers, gives:

- FLAC keeps PNG, JPEG, BMP and TIFF. It drops AV1 and WebP, and fails on GIF.
- MP4 keeps PNG, JPEG and BMP. It fails on GIF, TIFF, AV1 and WebP.
- MP3 keeps PNG, JPEG, BMP, TIFF and GIF. It fails on AV1 and WebP.

**How to reproduce:** on a build of [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd), with the two-track image from
item 29, make a cover with `ffmpeg -f lavfi -i color=c=red:s=8x8 -frames:v 1
art.png` (or `art.gif`). Then run `cyanrip -d disc.cue -N -A -U -B -s 0 -o opus
-C Front=art.png`, and check the `.opus` files with `ffprobe`. For the refused
case, use `-o flac -C Front=art.gif`.

**What the fork did:** [`443cbeb`](https://github.com/rmccann-hub/cyanrip/commit/443cbeb) ("Embed a cover only where the output holds
it, and say so"):

- A table records which picture formats each output's muxer keeps, measured
  against FFmpeg 6.1.1.
- A cover goes only to an output that holds it.
- A user's own cover that a cover-embedding output cannot hold is refused
  before the rip.
- The block lists the cover only for the files that hold it:
  - `none (the output cannot hold a GIF picture; saved as <file>)` when no file
    does;
  - `not in the <ext> file: ...` for each file that does not.
- `-I`, which rips nothing, still says what it would embed.

In upstream's code there are two steps.

1. Count the outputs the encoder gives the picture to, with the same test as
   `src/cyanrip_encode.c:1158`. Print `none` when there are none, and name the
   outputs that lack it when only some hold it. Applied to [`648b1dd`](https://github.com/cyanreg/cyanrip/commit/648b1dd) and run:
   - `-o opus` reads `Embedded cover art: none (no output embeds cover art)`;
   - `-o flac,opus` lists the cover, then `not in the opus file: that output
     embeds no cover art`.
2. For a picture that a cover-embedding muxer refuses or drops, decide before
   the rip, either refusing the cover or leaving it out of that output, and say
   so in the block. The block is printed before the file is written, so the
   muxer's result is not yet known when the block is logged.

---
*Found in the fork `rmccann-hub/cyanrip` (branch `platterpus-fork`), which feeds the Platterpus ripper. Checked against `master` at `648b1dd`. The fix is linked above; happy to open a PR if it helps.*

<!-- BODY END -->

