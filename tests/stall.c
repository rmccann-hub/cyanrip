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

/* Stall-heartbeat tests.
 *
 * The property under test is the one the previous implementation did not have:
 * the heartbeat must fire while a read is blocked *and nothing is calling
 * back*. The earlier version was driven from libcdio-paranoia's status
 * callback, so a drive grinding inside one blocking SCSI command -- the only
 * stall anybody cares about -- produced silence. That shipped, and a real rig
 * stall of two three minute stretches produced not one heartbeat line.
 *
 * Every test below therefore simulates a blocked read by simply *not calling
 * anything*: begin, sleep, end. No callback exists in this binary to fire. If
 * the heartbeat is ever re-plumbed onto something the reader has to drive,
 * test_fires_with_no_callbacks() goes quiet and fails.
 *
 * No drive and no disc: the watchdog reasons about clocks and a thread, not
 * about I/O. Timings are milliseconds so the whole file runs in about a second.
 *
 * Real hardware is still the only place the *consequence* can be observed --
 * that a stalled drive is what leaves a read outstanding. This file proves the
 * reporting works when one is; it does not prove a drive causes one.
 */

#include "stall_watchdog.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <libavutil/time.h>

static int failures;

#define CHECK(cond, ...)                                                      \
    do {                                                                      \
        if (!(cond)) {                                                        \
            failures++;                                                       \
            fprintf(stderr, "FAIL %s:%d: ", __func__, __LINE__);              \
            fprintf(stderr, __VA_ARGS__);                                     \
            fprintf(stderr, "\n");                                            \
        }                                                                     \
    } while (0)

/* Stands in for the real cyanrip_log(). Capturing here rather than scraping
 * stdout means the assertions are against the message the watchdog actually
 * formatted, not against whatever survived a pipe. Written from the watchdog
 * thread, so it takes a lock of its own. */
static pthread_mutex_t cap_lock = PTHREAD_MUTEX_INITIALIZER;
static char cap[16384];
static size_t cap_len;

struct cyanrip_ctx;
void cyanrip_log(struct cyanrip_ctx *ctx, int verbose, const char *format, ...);
void cyanrip_log(struct cyanrip_ctx *ctx, int verbose, const char *format, ...)
{
    va_list args;
    pthread_mutex_lock(&cap_lock);
    va_start(args, format);
    if (cap_len < sizeof(cap) - 1)
        cap_len += vsnprintf(cap + cap_len, sizeof(cap) - cap_len, format, args);
    va_end(args);
    pthread_mutex_unlock(&cap_lock);
}

static void cap_reset(void)
{
    pthread_mutex_lock(&cap_lock);
    cap[0] = '\0';
    cap_len = 0;
    pthread_mutex_unlock(&cap_lock);
}

static int cap_count(const char *needle)
{
    int n = 0;
    pthread_mutex_lock(&cap_lock);
    for (const char *p = cap; (p = strstr(p, needle)); p += strlen(needle))
        n++;
    pthread_mutex_unlock(&cap_lock);
    return n;
}

/* The stall must survive into the log, not only onto the terminal.
 *
 * The heartbeat is progress output and stays on stdout; what the *log* carries
 * is this summary. Without it the 2026-08-03 rig capture's two three-minute
 * stalls existed only because the consumer happened to be recording 41180
 * lines of stdout -- from the log alone that rip looked untroubled, and a
 * stall is not a thing you can go back and re-measure.
 *
 * Runs first, and stalls longer than anything else in this file, so
 * test_stats_keep_the_longest() below can assert against a known winner.
 */
static void test_stats_count_and_longest(void)
{
    crip_stall_stats_t s;

    crip_stall_stats(&s);
    CHECK(s.count == 0, "stall count started at %i, not 0", s.count);

    cap_reset();
    crip_stall_watchdog_config(200000, 200000);
    crip_stall_watchdog_start();

    crip_stall_read_begin(9, 999);
    av_usleep(900000);
    crip_stall_read_end();

    crip_stall_watchdog_end();

    crip_stall_stats(&s);

    /* The threshold comes back with the count because a count alone cannot be
     * compared against another run's -- "3 stalls" means nothing until you
     * know what counted as one. */
    CHECK(s.threshold_us == 200000,
          "threshold reported as %lldus, not the 200000 configured",
          (long long)s.threshold_us);
    CHECK(s.count == 1, "one 900ms stall counted as %i", s.count);
    CHECK(s.longest_us >= 900000,
          "longest stall reported as %lldus for a 900ms read",
          (long long)s.longest_us);
    CHECK(s.longest_track == 9 && s.longest_lsn == 999,
          "longest stall attributed to track %i LSN %i, not track 9 LSN 999",
          s.longest_track, (int)s.longest_lsn);
}

/* Runs last. Every stall after the first was shorter, so "longest" must still
 * name the first -- a implementation that simply records the most recent stall
 * passes every other check in this file and fails this one. */
static void test_stats_keep_the_longest(void)
{
    crip_stall_stats_t s;
    crip_stall_stats(&s);

    CHECK(s.count >= 2, "stalls stopped accumulating: count is %i after "
                        "several stalled reads", s.count);
    CHECK(s.longest_track == 9 && s.longest_lsn == 999,
          "longest stall is now track %i LSN %i -- the last stall overwrote "
          "the longest one", s.longest_track, (int)s.longest_lsn);
    CHECK(s.longest_us >= 900000,
          "longest stall shrank to %lldus", (long long)s.longest_us);
}

/* The whole point. A read is outstanding for 700 ms with a 200 ms threshold,
 * and in that time this thread calls nothing at all -- exactly the shape of a
 * drive blocked inside a single SCSI command. */
static void test_fires_with_no_callbacks(void)
{
    cap_reset();
    crip_stall_watchdog_config(200000, 200000);
    crip_stall_watchdog_start();

    crip_stall_read_begin(3, 123456);
    av_usleep(700000);
    crip_stall_read_end();

    crip_stall_watchdog_end();

    const char *hb_line = "Still reading track 3 - the read for LSN 123456 "
                          "has not returned";
    const char *ret_line = "Track 3 - the read for LSN 123456 returned after";
    const int hb = cap_count(hb_line);
    CHECK(hb >= 1, "no heartbeat for a 700ms read at a 200ms threshold");

    /* Rate limited to one per interval, so 700ms cannot produce a flood.
     * Upper bound is generous: a loaded machine may sleep long and emit fewer,
     * but it must never emit more than one per interval plus slop. */
    CHECK(hb <= 5, "heartbeat not rate limited: %i lines in 700ms at a 200ms "
                   "interval", hb);

    CHECK(cap_count(ret_line) == 1,
          "expected exactly one returned line, got %i", cap_count(ret_line));
}

/* An ordinary rip must stay silent: frames complete in milliseconds and a
 * heartbeat on every one of them would bury the progress output. */
static void test_silent_when_reads_are_fast(void)
{
    cap_reset();
    crip_stall_watchdog_config(200000, 200000);
    crip_stall_watchdog_start();

    for (int i = 0; i < 40; i++) {
        crip_stall_read_begin(1, 1000 + i);
        av_usleep(5000);
        crip_stall_read_end();
    }

    crip_stall_watchdog_end();

    CHECK(cap_count("Still reading") == 0,
          "heartbeat fired for reads well under the threshold: %i lines",
          cap_count("Still reading"));
    CHECK(cap_count("returned after") == 0,
          "resumed line printed with no preceding heartbeat");
}

/* -k 0. A consumer that does its own liveness tracking can turn ours off. */
static void test_threshold_zero_disables(void)
{
    cap_reset();
    crip_stall_watchdog_config(0, 0);
    crip_stall_watchdog_start();

    crip_stall_read_begin(2, 5000);
    av_usleep(400000);
    crip_stall_read_end();

    crip_stall_watchdog_end();

    CHECK(cap_count("Still reading") == 0,
          "heartbeat fired with the threshold disabled");
}

/* The heartbeat is armed per read, not per rip: a slow read followed by fast
 * ones must not leave the next read reporting a stale start time, and the
 * resumed line must be attributed to the read that actually stalled. */
static void test_state_resets_between_reads(void)
{
    cap_reset();
    crip_stall_watchdog_config(200000, 200000);
    crip_stall_watchdog_start();

    crip_stall_read_begin(7, 700);
    av_usleep(500000);
    crip_stall_read_end();

    crip_stall_read_begin(8, 800);
    av_usleep(10000);
    crip_stall_read_end();

    crip_stall_watchdog_end();

    CHECK(cap_count("Still reading track 7") >= 1, "track 7 stall not reported");
    CHECK(cap_count("Track 7 - the read for LSN 700 returned after") == 1,
          "track 7 return not reported");
    CHECK(cap_count("Still reading track 8") == 0,
          "fast read after a stalled one reported as stalled");
    CHECK(cap_count("Track 8 -") == 0,
          "fast read after a stalled one printed a resume line");
}

/* Nothing may be printed after the watchdog is joined: the caller relies on
 * that to keep a heartbeat out of the middle of the final report. */
static void test_nothing_printed_after_end(void)
{
    crip_stall_watchdog_config(100000, 100000);
    crip_stall_watchdog_start();
    crip_stall_read_begin(4, 400);
    av_usleep(300000);
    crip_stall_watchdog_end();

    cap_reset();
    av_usleep(400000);

    CHECK(cap_count("Still reading") == 0,
          "watchdog printed after being joined");

    crip_stall_read_end();
}

/* The three shapes of the disc summary's `Read stalls:` value, exactly.
 *
 * The populated one is unreachable from any rip here -- an image read completes
 * in microseconds against a threshold in whole seconds -- so before this the
 * only wording anyone outside could see written down was `none`, and Platterpus
 * asked us for the other two rather than being able to read them (round 7 lap
 * 13 D1). Pinning the strings makes them quotable, and makes a reword a test
 * failure rather than a surprise in an archival log.
 *
 * Asserted with strcmp against whole expected strings rather than substrings:
 * a prefix check would pass while the tail of the line changed. */
static void test_summary_line_shapes(void)
{
    char buf[160];
    crip_stall_stats_t s;

    /* -k 0: we did not look. Not the same claim as "there were none". */
    s = (crip_stall_stats_t){ .threshold_us = 0 };
    crip_stall_summary_line(buf, sizeof(buf), &s);
    CHECK(!strcmp(buf, "unknown (stall reporting disabled with -k 0)"),
          "disabled shape is %s", buf);

    /* Watched, saw none. */
    s = (crip_stall_stats_t){ .threshold_us = 10000000LL, .count = 0 };
    crip_stall_summary_line(buf, sizeof(buf), &s);
    CHECK(!strcmp(buf, "none (no read exceeded 10s)"),
          "clean shape is %s", buf);

    /* Populated, plural. */
    s = (crip_stall_stats_t){ .threshold_us = 10000000LL, .count = 2,
                              .longest_us = 187000000LL, .longest_track = 4,
                              .longest_lsn = 45231 };
    crip_stall_summary_line(buf, sizeof(buf), &s);
    CHECK(!strcmp(buf, "2 reads exceeded 10s; longest 187s (track 4, LSN 45231)"),
          "populated shape is %s", buf);

    /* Populated, singular -- "1 reads" would be the kind of wrong nobody
     * notices until it is in an archive. */
    s = (crip_stall_stats_t){ .threshold_us = 30000000LL, .count = 1,
                              .longest_us = 42000000LL, .longest_track = 1,
                              .longest_lsn = 0 };
    crip_stall_summary_line(buf, sizeof(buf), &s);
    CHECK(!strcmp(buf, "1 read exceeded 30s; longest 42s (track 1, LSN 0)"),
          "singular shape is %s", buf);
}

int main(void)
{
    test_summary_line_shapes();
    test_stats_count_and_longest();
    test_fires_with_no_callbacks();
    test_silent_when_reads_are_fast();
    test_threshold_zero_disables();
    test_state_resets_between_reads();
    test_nothing_printed_after_end();
    test_stats_keep_the_longest();

    if (failures)
        fprintf(stderr, "%d check(s) failed\n", failures);
    else
        printf("all stall watchdog checks passed\n");

    return !!failures;
}
