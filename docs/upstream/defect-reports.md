# Drafts: upstream bug reports for cyanreg/cyanrip

**Not filed.** These are drafts for the maintainer to review and submit. Filing
on upstream's tracker is outside this repository, so it is the maintainer's act;
what this file does is make each one a copy-and-paste. All eighteen are
rendered for upstream's tracker in `issues-to-file.md`, generated from this
file and the cache-model one by `tools/gen-upstream-issues.py`. `CLAUDE.md`'s rule is that
*"not filed is not fixed"*, and until 2026-09-27 only one of the defects this
fork found in upstream had a report written: the cache-model one, which stays in
its own file, `docs/upstream-cachemodel-report.md`. There are eighteen:
seventeen here, and that one. The thirteenth found, report 13, was found the
day this file was written. Reports 14 to 18 were drafted on 2026-10-05, when
`master` was still `f8ebf48` (`git ls-remote` again): 14 and 18 found that
day, and 15 to 17 found earlier in round 30 and fixed for the fork's `.20`
without a report until then.

**Checked against upstream `master` at `f8ebf48` on 2026-09-27**, which is also
our `master` (`git ls-remote https://github.com/cyanreg/cyanrip
refs/heads/master` returned `f8ebf48fc0d6926796c785fe2dbd9dec54ac15a5`). Every
`file:line` below was read at that commit, not recalled. Each defect's
re-check command is its row in `docs/SETTLED.md`'s upstream section, which
`tools/check-settled.py` runs, so a line here that stops being true fails
there.

Each report says what the fork did, by commit, so upstream can take the fix
or write its own. None of the fork's fixes changes upstream's command line.

---

## 1. The signal handler calls `cyanrip_log()`, which is not async-signal-safe

**Where:** `src/cyanrip_main.c:934-942`, `on_quit_signal()`.

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
async-signal-safe (`20c2f77`, "Make cancellation work: an unsafe signal handler,
SIGTERM, and a -Z loop that ignored both").

## 2. SIGTERM is not handled at all

**Where:** `src/cyanrip_main.c:1144`, the only signal installation:
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
`20c2f77`.

## 3. `cyanrip_log_finish_report()` sits above `end:`, so every `goto end` skips it

**Where:** `src/cyanrip_main.c:2110-2112`:

```c
    if (!ctx->settings.print_info_only)
        cyanrip_log_finish_report(ctx);
end:
```

Twenty-two `goto end` statements in `main()`, which starts at line 1133, jump
to the label below the report.

**What happens:** a run that takes any of them writes a log with no completion
report, and then `cyanrip_log_end()` signs that log as though it were whole.
Observed on this fork: a rip cancelled mid-track produced a signed log with no
footer, which a downstream program checking the log read as *"the log was cut off"*.

**What the fork did:** the footer is written on every route out, inside `end:`,
after the encoders are joined, and says which route it was (`4cfbe4f`, "Write
the completion footer on every route out, and give Rip completed: a third
state").

## 4. The filter graph is a ternary cascade, so `-H` discards de-emphasis

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
order (`b866900`, "Compose the filter graph, so -H stops swallowing
de-emphasis").

## 5. `(deemphasis applied)` is printed from the settings, not from what happened

**Where:** `src/cyanrip_log.c:85-86`:

```c
        if (ctx->settings.deemphasis || ctx->settings.force_deemphasis)
            cyanrip_log(ctx, 0, " (deemphasis applied)\n");
```

**What happens:** under `-H`, report 4 means de-emphasis is not applied, but the
log still says it was. The log is the only record of what was done to the audio,
and this line claims a step that did not run.

**What the fork did:** the line reports what the graph actually contained,
fixed with report 4 in `b866900`.

## 6. A bare apostrophe in `-a` or `-t` swallows every later field

**Where:** `src/cyanrip_main.c:1704` and `:1789`,
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
double-escaped (`c59dea3`, "Escape bare apostrophes in -a/-t, without
double-escaping the consumer's").

## 7. An invalid UTF-8 byte truncates a name, and can make `-D` absolute

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
string is kept (`c3482b0`, "Substitute U+FFFD for invalid UTF-8 instead of
truncating and logging").

## 9. `-r` reaches libcdio-paranoia unrounded, and `-r 3` never returns on a bad sector

(Report 8 is `docs/upstream-cachemodel-report.md`.)

**Where:** `src/cyanrip_main.c:428`, `cdio_paranoia_read_limited(ctx->paranoia,
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
5, at least 5, and the log says both numbers when they differ (`2af669e`, "Round
the per-frame retry limit up to a multiple of 5, which libcdio-paranoia needs").
The library's check is arguably a libcdio-paranoia defect too, and worth a report
there.

## 10. `media` is tagged from the `-H` setting, so every `-H` rip says HDCD

**Where:** `src/cyanrip_main.c:1610`, `ctx->settings.decode_hdcd ? "HDCD" :
"CD"`, set before a sample is read.

**What happens:** every file ripped with `-H` is tagged `media: HDCD`, whether or
not the disc carries HDCD, and the log reports `HDCD detected: no` for the same
rip. Observed on this fork on a real drive: every `-H` rip of a non-HDCD disc.

**What the fork did:** the tag is `CD`. Whether a disc is HDCD is a measurement
the log already reports, not a setting (`ed4a377`, "Tag media as CD whatever -H
says").

## 11. The AccurateRip tally counts a track whose read was interrupted

**Where:** `src/cyanrip_log.c:318`, in `cyanrip_log_finish_report()`, which
tests only `t->ar_db_status == CYANRIP_ACCUDB_FOUND`.

**What happens:** a SIGINT during a track's read still reaches the report. If the
read got past sector 450, the one-sector `Accurip 450` checksum can match the
database, so the disc's partial-match tally counts a track that was not ripped.
This is read from upstream's source, not run upstream; it was found on this fork
in a real rip.

**What the fork did:** the tally counts only tracks whose read completed
(`f26668b`, "Leave an interrupted track out of the AccurateRip tally").

## 12. A 450 lookup falls through to the whole-track checksum on a miss

**Where:** `src/accurip.c:239-242`:

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

**What the fork did:** a 450 lookup compares only 450 checksums (`10f36fe`,
"Compare only 450 checksums on a 450 AccurateRip lookup").

## 13. The AccurateRip disc status can never read `mismatch`

**Where:** `src/accurip.c:171`, in `crip_fill_accurip()`, before the loop over
the response's entries:

```c
    ctx->ar_db_status = CYANRIP_ACCUDB_FOUND;
```

and the arm it disables, `:188-189`:

```c
            if (ctx->ar_db_status != CYANRIP_ACCUDB_FOUND)
                ctx->ar_db_status = CYANRIP_ACCUDB_MISMATCH;
```

**What happens:** the status is already `FOUND` when the first entry is read,
so the `MISMATCH` assignment never runs. A response whose entries all carry
another disc's ids reads `AccurateRip:    found`, and so does an empty one. The
report then prints `Tracks ripped accurately: 0/N`, which reads as a comparison
that found nothing, over a comparison that never happened. Read from the
source: no real response has been seen to have that shape, because a dBAR file
is named by the ids it holds.

**How to reproduce:** call the parse on any recorded dBAR response with one
disc id changed, or with an empty body, and read the disc status.

**What the fork did:** the status starts at `NOT_FOUND` and becomes `FOUND`
only when an entry for this disc is read, so those two responses read
`mismatch` and `not found` and print no tally (`64642db`, "Let the AccurateRip
disc status say mismatch and not found"). The fork first split the parse out
of the fetch, unchanged, so a recorded response can be tested with no network
(`5b7493c`).

## 14. A one-frame AccurateRip entry under the threshold is logged as `(not found)`

**Where:** `src/cyanrip_log.c:152-159`, the `Accurip 450:` line, reached when
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
confidence (`b1857d6`, "Say a one-frame AccurateRip entry was found when the
threshold rejects it"). The tally of partial matches is unchanged.

## 15. A track's success line ignores paranoia's skips and a `-Z` repeat limit

**Where:** `src/cyanrip_main.c:911-914`, at the end of `cyanrip_rip_track()`:

```c
        if (ctx->total_error_count - start_err)
            cyanrip_log(ctx, 0, "Track %i ripped and encoded with errors.\n", t->number);
        else
            cyanrip_log(ctx, 0, "Track %i ripped and encoded successfully!\n", t->number);
```

and the repeat limit at `:858-861`, which reaches the same lines:

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

**How to reproduce:** rip a disc paranoia has to skip on, and compare the
track's success line with the per-track `SKIP` counter; or rip with `-Z 2`
and a repeat limit on a disc that reads differently each time.

**What the fork did:** the line reads `with errors` when the track's last read
skipped (`e5a0897`, "Read a track with paranoia skips as read with errors")
or when `-Z` hit the repeat limit (`4529810`, "Read a -Z track that hit the
repeat limit as read with errors").

## 16. A failed track ends a rip of every track silently, and the album is finalised over it

**Where:** `src/cyanrip_main.c:1937-1938`, the loop over every track:

```c
                if (cyanrip_rip_track(ctx, t))
                    break;
```

against the loop over the tracks `-l` names, `:2064-2067`:

```c
            ret = cyanrip_rip_track(ctx, t);
            if (ret < 0) {
                cyanrip_log(ctx, 0, "Error ripping: %s\n", av_err2str(ret));
                goto end;
            }
```

**What happens:** with `-l`, a failed track prints `Error ripping:` and ends
the run. Without it, the same failure leaves the loop with no message and
carries on: the album's loudness is finalised (`:1945-1946`) and, with
ReplayGain on, the album tags are written (`:1948-1950`), over a disc whose
tracks were not all ripped. Any failure `cyanrip_rip_track()` returns reaches
it, a changed medium included.

**How to reproduce:** rip a disc without `-l` and make one track fail, for
example by changing the medium mid-rip, then compare with the same failure
under `-l`.

**What the fork did:** both loops print `Error ripping: %s` and end the run
(`c1e1ab1`, "Abort the rip of every track on a failed track, as -l does").

## 17. A stopped `-f` search is retried or misreported

**Where:** `src/cyanrip_main.c:523-526`, where a stop during a track's read
leaves the search:

```c
            if (quit_now) {
                cyanrip_log(ctx, 0, "Stopping, offset finding incomplete!\n");
                goto end;
            }
```

and `:564-576`, which the `goto` lands in:

```c
    if (!offset_found) {
        if (!had_ar) {
            ...
        } else if (had_ar && !did_check) {
            cyanrip_log(ctx, 0, "No track was long enough, unable to find drive offset!\n");
        } else {
            cyanrip_log(ctx, 0, "Was not able to find drive offset with a radius of %i frames"
                        ", trying again with a larger radius...\n", range);
            search_for_drive_offset(ctx, 2*range);
        }
```

**What happens:** nothing after `end:` asks whether the search was stopped.
Once a track has been checked, a stop prints `trying again with a larger
radius`, reads a frame, stops again, and repeats until the radius outgrows
every track. Before any track has been checked, a stop prints `No track was
long enough`, which is not why the search ended.

**How to reproduce:** run `-f` on a disc in AccurateRip and send SIGINT
during the search.

**What the fork did:** a stop ends the search, and every stopped search prints
`Stopping, offset finding incomplete!` (`aa1f067`, "Say what a -J or -f run
was, and end a -f search on a stop").

## 18. The footer can count a one-frame match the track's lines never printed

**Where:** `src/cyanrip_log.c:319-324`, the disc tally in
`cyanrip_log_finish_report()`:

```c
                if ((crip_find_ar(t, t->acurip_checksum_v1, 0) > 0) ||
                    (crip_find_ar(t, t->acurip_checksum_v2, 0) > 0))
                    accurip_verified++;
                else if (crip_find_ar(t, t->acurip_checksum_v1_450, 1) > (3*(t->ar_db_max_confidence+1)/4) &&
                         t->acurip_checksum_v1_450)
                    accurip_partial++;
```

against the gate on the track's own `Accurip 450:` line, `:148`:

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
the 450 lines that say `matches Accurip DB` (`8ab9a8d`, "Count a one-frame
match in the footer only where the track's line says so").
