/*
 * This file is part of cyanrip.
 *
 * cyanrip is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * cyanrip is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with cyanrip; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 */

/* The machine-readable record. See diagnostics.h for what it is for.
 *
 * Two decisions in here are worth reading before changing anything.
 *
 * 1. NO SEVERITY IS CLAIMED. cyanrip_log() carries no severity argument -- its
 *    `verbose` parameter is unused throughout -- so this module has no way to
 *    know whether a message is a failure, a warning or progress. The tempting
 *    fix is to classify by wording, and this repository has already shipped
 *    that defect once: the provider contract's fatal inventory was filtered by
 *    a list of opening words, so every differently-worded fatal message
 *    vanished from a document that presented itself as derived. Messages are
 *    therefore recorded in order and left unclassified, and the file says so in
 *    a field rather than leaving a consumer to assume. The structured facts
 *    beside them -- exit code, error counts, stall statistics, per-track
 *    completion -- are the things actually known, and they are what a consumer
 *    should judge a rip by.
 *
 * 2. PROGRESS IS COLLAPSED BY MODELLING THE TERMINAL, NOT BY MATCHING TEXT.
 *    The rip loop rewrites one line thousands of times with a leading '\r'.
 *    Recording each rewrite would bury the file in noise, but deciding which
 *    messages are "progress" from their content is the same guess as (1). So
 *    this keeps one line buffer and does what a terminal does: '\r' discards
 *    the line being built, '\n' commits it. What survives is exactly what a
 *    person watching would have been left looking at, and no knowledge of any
 *    message's wording is involved.
 */

#include "diagnostics.h"
#include "cyanrip_main.h"
#include "stall_watchdog.h"
#include "version.h"
#include "handshake_state.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include <libavutil/mem.h>
#include <libavutil/bprint.h>

/* Bounded so a long rip cannot grow this without limit. Overflow is counted
 * and reported rather than silently discarded: a diagnostics file that quietly
 * drops the message explaining a failure is worse than no file.
 *
 * HEAD *AND* TAIL, not head alone. The first version kept the first 20000 lines
 * and dropped everything after, which is the same sentence above inverted: **a
 * tool's fatal message is the last thing it prints**, so a head-only cap
 * discards precisely the line that explains the failure while
 * `messages_dropped` still makes the record look accounted for. Platterpus
 * found this by reading the design rather than the file (round 7 lap 11 §D),
 * and it is their mitigation for our stdout that they were describing.
 *
 * The two halves are separate fields rather than one array with an elision
 * marker in it. A synthetic "--- N elided ---" string sitting among real
 * messages would be a line the program never printed, in the record of what the
 * program printed. */
#define DIAG_MAX_HEAD 10000
#define DIAG_MAX_TAIL 10000
#define DIAG_MAX_LINE 8192

static const char *diag_path;
static int diag_written;
static int diag_registered;

static char **diag_lines;
static int diag_nb_lines;
static int diag_dropped_lines;

/* Ring of the most recent lines, once the head is full. diag_tail_next is where
 * the next one goes; diag_tail_count saturates at DIAG_MAX_TAIL. */
static char *diag_tail[DIAG_MAX_TAIL];
static int diag_tail_next;
static int diag_tail_count;

static char diag_cur[DIAG_MAX_LINE];
static size_t diag_cur_len;
static int diag_cur_truncated;

static int diag_exit_code = -1;
static int diag_have_exit;

/* The structured snapshot. `have` distinguishes "no disc was ever opened" from
 * "zero tracks", which are different claims. */
static int diag_have_snapshot;
static int snap_nb_tracks;
static int snap_nb_cd_tracks;
static int snap_tracks_completed;
static int snap_total_error_count;
static char *snap_device;
static char *snap_consumer;
static int snap_paranoia_level;
static int snap_max_retries;
static int snap_offset;
static int snap_ripping_retries;
static char **snap_track_state;
static int snap_nb_track_state;

static void diag_commit_line(void)
{
    if (!diag_cur_len && !diag_cur_truncated)
        return;

    if (diag_nb_lines < DIAG_MAX_HEAD) {
        char **grown = av_realloc_array(diag_lines, diag_nb_lines + 1,
                                        sizeof(*diag_lines));
        if (!grown) {
            diag_dropped_lines++;
        } else {
            diag_lines = grown;
            diag_lines[diag_nb_lines] = av_strdup(diag_cur);
            if (diag_lines[diag_nb_lines])
                diag_nb_lines++;
            else
                diag_dropped_lines++;
        }
    } else {
        /* Past the head: keep the newest, so the last thing said survives.
         * Whatever this evicts is what "dropped" counts. */
        char *copy = av_strdup(diag_cur);
        if (!copy) {
            diag_dropped_lines++;
        } else {
            if (diag_tail[diag_tail_next]) {
                av_freep(&diag_tail[diag_tail_next]);
                diag_dropped_lines++;
            }
            diag_tail[diag_tail_next] = copy;
            diag_tail_next = (diag_tail_next + 1) % DIAG_MAX_TAIL;
            if (diag_tail_count < DIAG_MAX_TAIL)
                diag_tail_count++;
        }
    }

    diag_cur[0] = '\0';
    diag_cur_len = 0;
    diag_cur_truncated = 0;
}

/* One character through the terminal model. */
static void diag_feed(char c)
{
    if (c == '\r') {
        /* The line just built is about to be overwritten on screen, so it was
         * never something a reader saw. Drop it. */
        diag_cur[0] = '\0';
        diag_cur_len = 0;
        diag_cur_truncated = 0;
        return;
    }

    if (c == '\n') {
        diag_commit_line();
        return;
    }

    if (diag_cur_len + 1 >= sizeof(diag_cur)) {
        diag_cur_truncated = 1;
        return;
    }

    diag_cur[diag_cur_len++] = c;
    diag_cur[diag_cur_len] = '\0';
}

void crip_diag_record(const char *format, va_list args)
{
    char buf[DIAG_MAX_LINE];
    va_list copy;
    va_copy(copy, args);
    const int n = vsnprintf(buf, sizeof(buf), format, copy);
    va_end(copy);

    if (n < 0)
        return;

    const size_t len = (size_t)n < sizeof(buf) - 1 ? (size_t)n : sizeof(buf) - 1;
    for (size_t i = 0; i < len; i++)
        diag_feed(buf[i]);
}

void crip_diag_enable(const char *path)
{
    diag_path = path;
    if (path && !diag_registered) {
        atexit(crip_diag_write);
        diag_registered = 1;
    }
}

void crip_diag_set_exit(int code)
{
    diag_exit_code = code;
    diag_have_exit = 1;
}

void crip_diag_snapshot(cyanrip_ctx *ctx)
{
    if (!ctx)
        return;

    diag_have_snapshot     = 1;
    snap_nb_tracks         = ctx->nb_tracks;
    snap_nb_cd_tracks      = ctx->nb_cd_tracks;
    snap_tracks_completed  = ctx->tracks_completed;
    snap_total_error_count = ctx->total_error_count;
    snap_paranoia_level    = ctx->settings.paranoia_level;
    snap_max_retries       = ctx->settings.max_retries;
    snap_offset            = ctx->settings.offset;
    snap_ripping_retries   = ctx->settings.ripping_retries;

    av_freep(&snap_device);
    if (ctx->settings.dev_path)
        snap_device = av_strdup(ctx->settings.dev_path);
    av_freep(&snap_consumer);
    if (ctx->settings.consumer_id)
        snap_consumer = av_strdup(ctx->settings.consumer_id);

    /* Per-track completion, so a partial rip says which tracks are missing
     * rather than only how many. */
    for (int i = 0; i < snap_nb_track_state; i++)
        av_freep(&snap_track_state[i]);
    av_freep(&snap_track_state);
    snap_nb_track_state = 0;

    if (ctx->nb_tracks > 0) {
        snap_track_state = av_calloc(ctx->nb_tracks, sizeof(*snap_track_state));
        if (snap_track_state) {
            snap_nb_track_state = ctx->nb_tracks;
            for (int i = 0; i < ctx->nb_tracks; i++) {
                const cyanrip_track *t = &ctx->tracks[i];
                char line[256];
                snprintf(line, sizeof(line),
                         "{\"number\":%i,\"cd_track\":%i,\"repeats\":%i,"
                         "\"crcs_computed\":%s,\"eac_crc\":\"%08X\","
                         "\"rip_time_us\":%lli}",
                         t->number, t->cd_track_number, t->total_repeats,
                         t->computed_crcs ? "true" : "false",
                         t->eac_crc, (long long)t->rip_time_us);
                snap_track_state[i] = av_strdup(line);
            }
        }
    }
}

/* RFC 8259 string escaping. Anything below 0x20 becomes \uXXXX, so a stray
 * control character in a filename cannot produce a file that will not parse. */
static void diag_json_str(AVBPrint *b, const char *s)
{
    av_bprint_chars(b, '"', 1);
    for (const unsigned char *p = (const unsigned char *)s; s && *p; p++) {
        switch (*p) {
        case '"':  av_bprintf(b, "\\\""); break;
        case '\\': av_bprintf(b, "\\\\"); break;
        case '\b': av_bprintf(b, "\\b");  break;
        case '\f': av_bprintf(b, "\\f");  break;
        case '\n': av_bprintf(b, "\\n");  break;
        case '\r': av_bprintf(b, "\\r");  break;
        case '\t': av_bprintf(b, "\\t");  break;
        default:
            if (*p < 0x20)
                av_bprintf(b, "\\u%04x", *p);
            else
                av_bprint_chars(b, (char)*p, 1);
            break;
        }
    }
    av_bprint_chars(b, '"', 1);
}

void crip_diag_write(void)
{
    if (!diag_path || diag_written)
        return;
    diag_written = 1;

    /* Whatever was still being built when the process ended -- a fatal message
     * with no trailing newline is exactly the case that matters. */
    diag_commit_line();

    AVBPrint b;
    av_bprint_init(&b, 0, AV_BPRINT_SIZE_UNLIMITED);

    av_bprintf(&b, "{\n");
    /* /3 adds rip.interrupted_by. A field ADDED to a record is harmless to a
     * consumer that ignores unknown keys and fatal to one that allowlists
     * schema strings, and Platterpus does the latter -- so the version moves
     * and round 12 carries the ask to widen SUPPORTED_SCHEMAS. Adding the
     * field without the bump was the tempting alternative and is the worse
     * one: two different records both calling themselves /2 is the same defect
     * as two builds answering to one version string, which this fork already
     * fixed once with +platterpus.N. */
    av_bprintf(&b, "  \"schema\": \"cyanrip-diagnostics/3\",\n");

    av_bprintf(&b, "  \"cyanrip\": {\n");
    av_bprintf(&b, "    \"version\": ");
    diag_json_str(&b, PROJECT_VERSION_STRING);
    av_bprintf(&b, ",\n    \"fork_id\": ");
    diag_json_str(&b, PROJECT_FORK_ID);
    av_bprintf(&b, ",\n    \"vcs\": ");
    diag_json_str(&b, vcstag);
    av_bprintf(&b, ",\n    \"handshake\": ");
    diag_json_str(&b, HANDSHAKE_STATE);
    /* `released_build_declared`, not `released_build`. Round 10 made this a
     * build-time assertion rather than a derivation, and the logfile says so
     * in words -- "declared at build time, not verified by cyanrip". The JSON
     * key said `released_build`, which asserts a verified fact, so the two
     * surfaces disagreed about the same bit: the human one disclaimed and the
     * machine one did not.
     *
     * A label asserts even when its value disclaims, and here the value could
     * not disclaim at all -- a bare `true` has nowhere to put a qualifier. The
     * provenance has to be in the name. Same defect and same remedy as
     * `Cache defeat:` -> `Cache model:`. */
    av_bprintf(&b, ",\n    \"released_build_declared\": %s\n",
               HANDSHAKE_RELEASED ? "true" : "false");
    av_bprintf(&b, "  },\n");

    av_bprintf(&b, "  \"invocation\": ");
    diag_json_str(&b, crip_invocation ? crip_invocation : "");
    av_bprintf(&b, ",\n");

    if (diag_have_exit)
        av_bprintf(&b, "  \"exit_code\": %i,\n", diag_exit_code);
    else
        /* The process left by a route that did not set it -- a signal, or an
         * exit() somewhere that does not know about this module. Saying null
         * is a smaller claim than guessing zero, and a consumer can tell the
         * two apart. */
        av_bprintf(&b, "  \"exit_code\": null,\n");

    /* Stall statistics, in the same three states the log reports: a threshold
     * of 0 means the watchdog was off, which is "we did not look" and not
     * "there were none". */
    crip_stall_stats_t st;
    crip_stall_stats(&st);
    av_bprintf(&b, "  \"read_stalls\": {\n");
    if (!st.threshold_us) {
        av_bprintf(&b, "    \"watched\": false,\n");
        av_bprintf(&b, "    \"reason\": \"stall reporting disabled with -k 0\",\n");
        av_bprintf(&b, "    \"count\": null, \"longest_seconds\": null,\n");
        av_bprintf(&b, "    \"longest_track\": null, \"longest_lsn\": null\n");
    } else {
        av_bprintf(&b, "    \"watched\": true,\n");
        av_bprintf(&b, "    \"threshold_seconds\": %lli,\n",
                   (long long)(st.threshold_us / 1000000LL));
        av_bprintf(&b, "    \"count\": %i,\n", st.count);
        av_bprintf(&b, "    \"longest_seconds\": %lli,\n",
                   (long long)(st.longest_us / 1000000LL));
        if (st.count) {
            av_bprintf(&b, "    \"longest_track\": %i, \"longest_lsn\": %i\n",
                       st.longest_track, (int)st.longest_lsn);
        } else {
            av_bprintf(&b, "    \"longest_track\": null, \"longest_lsn\": null\n");
        }
    }
    av_bprintf(&b, "  },\n");

    /* null rather than absent when no disc was ever opened, so a refusal is
     * distinguishable from a rip that found nothing. */
    if (!diag_have_snapshot) {
        av_bprintf(&b, "  \"rip\": null,\n");
    } else {
        av_bprintf(&b, "  \"rip\": {\n");
        av_bprintf(&b, "    \"device\": ");
        if (snap_device)
            diag_json_str(&b, snap_device);
        else
            av_bprintf(&b, "null");
        av_bprintf(&b, ",\n    \"consumer\": ");
        if (snap_consumer)
            diag_json_str(&b, snap_consumer);
        else
            av_bprintf(&b, "null");
        av_bprintf(&b, ",\n");
        av_bprintf(&b, "    \"consumer_verified\": false,\n");
        av_bprintf(&b, "    \"paranoia_level\": %i,\n", snap_paranoia_level);
        av_bprintf(&b, "    \"frame_retries\": %i,\n", snap_max_retries);
        av_bprintf(&b, "    \"offset_samples\": %i,\n", snap_offset);
        av_bprintf(&b, "    \"rip_repeats\": %i,\n", snap_ripping_retries);
        av_bprintf(&b, "    \"cd_tracks\": %i,\n", snap_nb_cd_tracks);
        av_bprintf(&b, "    \"tracks\": %i,\n", snap_nb_tracks);
        av_bprintf(&b, "    \"tracks_completed\": %i,\n", snap_tracks_completed);
        av_bprintf(&b, "    \"ripping_errors\": %i,\n", snap_total_error_count);
        /* Deliberately no "success" field. cyanrip_ctx has one and nothing
         * in the program ever assigns it, so emitting it would have put a
         * permanent "success": false into every record of a rip that
         * succeeded. More to the point a success flag is a verdict, and
         * verdicts belong downstream -- tracks_completed against tracks,
         * ripping_errors, interrupted and exit_code are the measurements
         * a consumer needs to reach one. */
        av_bprintf(&b, "    \"interrupted\": %s,\n", quit_now ? "true" : "false");
        /* Which signal, beside the bool, for the reason the logfile names it
         * too: SIGINT is a person at a terminal and SIGTERM is a supervising
         * process, and a record that says only "interrupted" invites the
         * consumer to assume the first. It is null when the rip was not
         * interrupted -- absence of an interruption, not an unknown signal --
         * and the two are distinguishable because `interrupted` is beside it.
         *
         * A name and not a number: a signal number is not portable and the
         * record is archival. crip_signal_name() answers NULL for a signal we
         * do not install, which becomes the number, so an unrecognised value
         * is reported rather than mis-named. */
        av_bprintf(&b, "    \"interrupted_by\": ");
        if (!quit_now) {
            av_bprintf(&b, "null");
        } else {
            const char *signame = crip_signal_name(quit_signal);
            if (signame) {
                diag_json_str(&b, signame);
            } else {
                char num[32];
                snprintf(num, sizeof(num), "signal %i", (int)quit_signal);
                diag_json_str(&b, num);
            }
        }
        av_bprintf(&b, ",\n");
        av_bprintf(&b, "    \"track_state\": [");
        for (int i = 0; i < snap_nb_track_state; i++) {
            av_bprintf(&b, "%s\n      %s", i ? "," : "",
                       snap_track_state[i] ? snap_track_state[i] : "null");
        }
        av_bprintf(&b, "%s]\n", snap_nb_track_state ? "\n    " : "");
        av_bprintf(&b, "  },\n");
    }

    /* Every message, in order, unclassified -- and saying so, because a
     * consumer must not read the absence of a severity field as "nothing here
     * was serious". */
    av_bprintf(&b, "  \"messages_are_classified\": false,\n");
    av_bprintf(&b, "  \"messages_note\": \"cyanrip_log() carries no severity, "
                   "so no severity is asserted here. Progress lines that were "
                   "overwritten on the terminal are collapsed to the final "
                   "state of each line.\",\n");
    av_bprintf(&b, "  \"messages_dropped\": %i,\n", diag_dropped_lines);
    /* What the array is complete *with respect to*, stated before the boolean
     * that answers it.
     *
     * `messages_are_complete` used to sit here and it was a wrong claim.
     * The computation is `!diag_dropped_lines` -- did the retention cap fire
     * -- but the name asserts the array holds everything cyanrip printed, and
     * it does not: the capture hook wraps cyanrip_log(), while libavfilter's
     * ebur128 blocks reach the logfile through av_log and never pass through
     * it. Measured on our own golden reference: 55 non-blank log lines absent
     * from messages[], 52 of them ebur128 content, beside `dropped: 0` and
     * `complete: true`. Platterpus found it (2026-08-14 hand-off §7) and
     * reproduced it across two builds; we reproduced it at the current one.
     *
     * The remedy is the rename, not a qualifier. This project has already
     * settled that a label asserts even when its value disclaims -- `Cache
     * defeat:` became `Cache model:` for exactly this reason -- so a scope
     * field beside a boolean called `..._are_complete` would not have undone
     * the claim the name already made.
     *
     * `messages_dropped` deliberately keeps its meaning: lines this record saw
     * and discarded. The ebur128 lines were never seen, so they cannot be
     * counted here, and counting an unknown quantity into a field that means
     * something else would be the same defect one field over. */
    av_bprintf(&b, "  \"messages_scope\": \"cyanrip_log() only. Output "
                   "libavfilter writes directly -- the ebur128 loudness "
                   "blocks -- reaches the logfile and not this array, and is "
                   "not counted in messages_dropped because it was never "
                   "seen here.\",\n");
    av_bprintf(&b, "  \"messages_complete_within_scope\": %s,\n",
               diag_dropped_lines ? "false" : "true");
    av_bprintf(&b, "  \"messages\": [");
    for (int i = 0; i < diag_nb_lines; i++) {
        av_bprintf(&b, "%s\n    ", i ? "," : "");
        diag_json_str(&b, diag_lines[i]);
    }
    av_bprintf(&b, "%s],\n", diag_nb_lines ? "\n  " : "");

    /* The last lines said, in order. Empty whenever nothing overflowed the
     * head, so the ordinary case is one array and the field is still present
     * rather than appearing only on failure. */
    av_bprintf(&b, "  \"messages_tail\": [");
    for (int i = 0; i < diag_tail_count; i++) {
        const int idx = diag_tail_count < DIAG_MAX_TAIL
                      ? i : (diag_tail_next + i) % DIAG_MAX_TAIL;
        av_bprintf(&b, "%s\n    ", i ? "," : "");
        diag_json_str(&b, diag_tail[idx] ? diag_tail[idx] : "");
    }
    av_bprintf(&b, "%s]\n", diag_tail_count ? "\n  " : "");
    av_bprintf(&b, "}\n");

    FILE *f = fopen(diag_path, "wb");
    if (!f) {
        /* Not through cyanrip_log(): this runs from atexit, after the logfile
         * has been closed, and a message that goes nowhere is the failure this
         * whole module exists to prevent. Column 0, on stderr, so a caller
         * capturing either stream sees it. */
        fprintf(stderr, "Couldn't open diagnostics path \"%s\" for writing!\n",
                diag_path);
        av_bprint_finalize(&b, NULL);
        return;
    }

    fwrite(b.str, 1, b.len, f);
    fclose(f);
    av_bprint_finalize(&b, NULL);
}
