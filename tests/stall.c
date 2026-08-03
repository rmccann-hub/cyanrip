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

int main(void)
{
    test_fires_with_no_callbacks();
    test_silent_when_reads_are_fast();
    test_threshold_zero_disables();
    test_state_resets_between_reads();
    test_nothing_printed_after_end();

    if (failures)
        fprintf(stderr, "%d check(s) failed\n", failures);
    else
        printf("all stall watchdog checks passed\n");

    return !!failures;
}
