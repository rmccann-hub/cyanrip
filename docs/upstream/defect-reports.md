# Upstream bug reports for cyanreg/cyanrip

**Filed on 2026-10-16, all twenty-three as one issue: [cyanreg/cyanrip#167](https://github.com/cyanreg/cyanrip/issues/167)**, by the
operator, combined in the order of importance `issues-to-file.md` suggests.
That is the operator's word: this file's author could not open it, since this session's proxy answers HTTP 403 for upstream's tracker and refuses to attach upstream beside the fork, so the link is relayed, not read. A reply that asks for a pull request, or for any report as
an issue of its own, goes to the operator, who files it. Filing on upstream's
tracker is outside this repository, so it is the maintainer's act; what this
file does is make each one a copy-and-paste. All twenty-three are
rendered for upstream's tracker in `issues-to-file.md`, generated from this
file and the cache-model one by `tools/gen-upstream-issues.py`. `CLAUDE.md`'s rule is that
*"not filed is not fixed"*, and until 2026-09-27 only one of the defects this
fork found in upstream had a report written: the cache-model one, which stays in
its own file, `docs/upstream-cachemodel-report.md`. There are twenty-three:
twenty-two here, and that one. The thirteenth found, report 13, was found the
day this file was written. Reports 14 to 18 were drafted on 2026-10-05, when
`master` was still `f8ebf48` (`git ls-remote` again): 14 and 18 found that
day, and 15 to 17 found earlier in round 30 and fixed for the fork's `.20`
without a report until then. Reports 19 to 23 were drafted on 2026-10-12, the
day the fork merged upstream's `b40c1f0`: 19, 21, 22 and the first arm of 23
were found by the fork's first macOS and sanitizer CI runs on the merged tree,
and 20 and the other two arms of 23 were fixed here on 2026-09-06 and had no
report until a grep of the fork's history for upstream's code found them.

**Checked against upstream `master` at `7dbe56a` on 2026-10-16** (`git ls-remote
https://github.com/cyanreg/cyanrip refs/heads/master` returned
`7dbe56aad2f0ab039ab7b238a30ed662b1c017de`). Every `file:line` below was read
at that commit, in a clone of upstream, not recalled, and every quoted line of
code was checked to be there. Each defect's re-check command is its row in
`docs/SETTLED.md`'s upstream section, which `tools/check-settled.py` runs, so a
line here that stops being true fails there; on 2026-10-16 every row passed
against `7dbe56a`. Reports 1 to 18 were first checked against `f8ebf48`, on
2026-09-27, and reports 19 to 23 against `b40c1f0`, on 2026-10-12; a report
that was run says which build it was run on.

**What `7dbe56a` changes.** It is one commit after `b40c1f0`, the last upstream
commit merged into the fork, and it checks for a changed medium at most once a
second, where every frame read asked before ("check for media changes at most
once a second", fixing upstream's #165). It changes no report's substance; it
moves `cyanrip_main.c`'s line numbers, which are `7dbe56a`'s below. The fork's
`+platterpus.24` does not take it: a later upstream sync does, written up in
`docs/upstream/` before it merges, as every sync is. The fork asks once a frame
too, so the slowdown it fixes is the fork's as well.

**The upstream issues cited** in reports 10, 13 and 15 (#50, #24 and #70) are
the operator's reading of upstream's tracker on 2026-10-15. This file's author
could not open the tracker (its proxy answers HTTP 403), so they are relayed,
not read.

Each report says what the fork did, by commit, so upstream can take the fix
or write its own. None of the fork's fixes changes upstream's command line.

---

## 1. The signal handler calls `cyanrip_log()`, which is not async-signal-safe

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
async-signal-safe (`20c2f77`, "Make cancellation work: an unsafe signal handler,
SIGTERM, and a -Z loop that ignored both").

## 2. SIGTERM is not handled at all

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
`20c2f77`.

## 3. `cyanrip_log_finish_report()` sits above `end:`, so every `goto end` skips it

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

**Where:** `src/cyanrip_log.c:90-91`:

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
5, at least 5, and the log says both numbers when they differ (`2af669e`, "Round
the per-frame retry limit up to a multiple of 5, which libcdio-paranoia needs").
The library's check is arguably a libcdio-paranoia defect too, and worth a report
there.

## 10. `media` is tagged from the `-H` setting, so every `-H` rip says HDCD

**Where:** `src/cyanrip_main.c:1960`, `ctx->settings.decode_hdcd ? "HDCD" :
"CD"`, set before a sample is read. Related, not a duplicate: #50.

**What happens:** every file ripped with `-H` is tagged `media: HDCD`, whether or
not the disc carries HDCD, and the log reports `HDCD detected: no` for the same
rip. Observed on this fork on a real drive: every `-H` rip of a non-HDCD disc.

**What the fork did:** the tag is `CD`. Whether a disc is HDCD is a measurement
the log already reports, not a setting (`ed4a377`, "Tag media as CD whatever -H
says").

## 11. The AccurateRip tally counts a track whose read was interrupted

**Where:** `src/cyanrip_log.c:357`, in `cyanrip_log_finish_report()`, which
tests only `t->ar_db_status == CYANRIP_ACCUDB_FOUND`.

**What happens:** a SIGINT during a track's read still reaches the report. If the
read got past sector 450, the one-sector `Accurip 450` checksum can match the
database, so the disc's partial-match tally counts a track that was not ripped.
This is read from upstream's source, not run upstream; it was found on this fork
in a real rip.

**What the fork did:** the tally counts only tracks whose read completed
(`f26668b`, "Leave an interrupted track out of the AccurateRip tally").

## 12. A 450 lookup falls through to the whole-track checksum on a miss

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

**What the fork did:** a 450 lookup compares only 450 checksums (`10f36fe`,
"Compare only 450 checksums on a 450 AccurateRip lookup").

## 13. The AccurateRip disc status can never read `mismatch`

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

Upstream's `76dcd5d` ("Don't trust AccurateRip and cover art replies to be
well formed") fixed part of this: a reply with no body is now taken as no
entry, and reads `not found` (`:177-180`). A response holding only another
disc's entries still reads `found`. Related, not a duplicate: #24.

**How to reproduce:** call the parse on any recorded dBAR response with one
disc id changed, and read the disc status.

**What the fork did:** the status starts at `NOT_FOUND` and becomes `FOUND`
only when an entry for this disc is read, so that response reads `mismatch`
and prints no tally (`64642db`, "Let the AccurateRip
disc status say mismatch and not found"). The fork first split the parse out
of the fetch, unchanged, so a recorded response can be tested with no network
(`5b7493c`).

## 14. A one-frame AccurateRip entry under the threshold is logged as `(not found)`

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
confidence (`b1857d6`, "Say a one-frame AccurateRip entry was found when the
threshold rejects it"). The tally of partial matches is unchanged.

## 15. A track's success line ignores paranoia's skips and a `-Z` repeat limit

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
skipped (`e5a0897`, "Read a track with paranoia skips as read with errors")
or when `-Z` hit the repeat limit (`4529810`, "Read a -Z track that hit the
repeat limit as read with errors").

## 16. A failed track ends a rip of every track silently, and the album is finalised over it

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
(`c1e1ab1`, "Abort the rip of every track on a failed track, as -l does").

## 17. A stopped `-f` search is retried with a larger radius

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
`Stopping, offset finding incomplete!` (`aa1f067`, "Say what a -J or -f run
was, and end a -f search on a stop").

## 18. The footer can count a one-frame match the track's lines never printed

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
the 450 lines that say `matches Accurip DB` (`8ab9a8d`, "Count a one-frame
match in the footer only where the track's line says so").

## 19. A disc image is taken for a drive with libcdio 2.3.0 or later

**Where:** `src/cyanrip_main.c:1940-1945` at `7dbe56a`, the offset check:

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
sub-channel failure. Run here on a build of `b40c1f0` against libcdio 2.1,
through an `LD_PRELOAD` shim that adds the bit for an image driver as 2.3.0
does. Without the shim, a two-track CUE image rips and exits 0. With it, the
same command exits 1 at `Offset is unset!`, and with `-s 0` both tracks log
`Unable to read track N subchannel info!`.

**What the fork did:** both checks ask the driver, with `cdio_get_driver_id()`
against the three image drivers, as upstream's own cache-model switch already
does (`:271-274`). The ISRC read at `:648` is left alone, because from 2.3.0
an image really does serve one (`faec396`, "Tell an image from a drive by its
driver, not by CDIO_DRIVE_CAP_READ_ISRC").

## 20. `-Y` on a directory overflows a signed length

**Where:** `src/fun512.c:69-75` at `7dbe56a`, in `cyanrip_verify_log()`:

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
<a directory>` on ext4. Run here on a build of `b40c1f0`: `fun512.c:72:45:
runtime error: signed integer overflow: 9223372036854775807 + 1 cannot be
represented in type 'long int'`, then `Couldn't read "adir"!`, exit 1.

**What the fork did:** the length is bounded before anything is added to it,
by a cap of 64 MiB, far above any rip log, and a file over the cap is an I/O
error (`72975de`, "Bound the FUN512 read, and run the teardown on the two
paths that skipped it").

## 21. A failed read in `-Y` is reported as a log with no checksum

**Where:** `src/fun512.c:76-77` at `7dbe56a`, in `cyanrip_verify_log()`:

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
`ftell()` gave, is an I/O error (`d109c56`, "Report a log that cannot be read
as an I/O error, not as one without a checksum").

## 22. The paranoia counters are printed with `%lu` from `uint64_t`

**Where:** `src/cyanrip_log.c:383` at `7dbe56a`, in the `PCHECK()` macro,
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
printed with `%llu`, which prints the same digits everywhere (`09492a5`,
"Print the paranoia counters with %llu, which fits uint64_t everywhere"). The
fork's `cyanrip_log()` carries a format attribute, which is how its macOS
build found this.

## 23. Three start-up failures return without tearing the context down

**Where:** `src/cyanrip_main.c:218-225` at `7dbe56a`, in `cyanrip_ctx_init()`:

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

**How to reproduce:** on a build of `b40c1f0` with `-Db_sanitize=address`, run
here:

- `cyanrip -d /dev/null -I`: `Unable to init cddap context!`, exit 1, and
  LeakSanitizer reports the 479,824-byte context.
- `cyanrip -d disc.cue -N -A -U -s 0 -o flac -D <a regular file>/out -L log`:
  `Couldn't open path ... Not a directory!`, exit 1, and 12,834,961 bytes
  leaked in 36 allocations.
- The same with `-D dir -M sheet`, where `dir/sheet.cue` is a directory: the
  CUE sheet fails the same way, with the same leak, and `dir/log.log` is left
  at 0 bytes.

**What the fork did:** all three call `cyanrip_ctx_end()` (`3f0e161` for the
first, `72975de` for the other two). The fork later sent the log and CUE
failures to `end:` instead, so the log that was opened carries the run's
completion footer (`a79ac9e`, "Emit the completion footer on the last two
paths that skipped it").
