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

/* Liveness while a single frame read is blocked.
 *
 * A frame read can sit inside cdio_paranoia_read_limited() for minutes on a
 * damaged sector, and until it returns the rip prints nothing at all -- which
 * is indistinguishable, from outside, from a process wedged in an ioctl that
 * will never come back.
 *
 * The first version of this emitted the heartbeat from paranoia's own status
 * callback, on the reasoning that a callback firing proves the read is still
 * working. That reasoning was wrong in exactly the case that matters. A real
 * rig stall was captured on 2026-08-03: two three-minute stalls, a build that
 * provably contained the callback version, and a consumer capturing every line
 * of our stdout -- 41180 lines of it -- with not one heartbeat among them. When
 * a drive grinds on a bad sector it does so inside a single blocking SCSI
 * command, so paranoia is not running and never calls back at all. A
 * callback-driven heartbeat can only report the stalls that were not the
 * problem.
 *
 * So the heartbeat runs on its own thread, which is the only thing that keeps
 * ticking while the rip thread is blocked in the kernel. It samples when the
 * current read began and reports on that, independent of anything paranoia
 * does. This is the whole reason the module exists, and it is what
 * tests/stall.c asserts: the heartbeat fires with no callback ever called.
 *
 * Rate-limited, and armed only once a read has been outstanding past the
 * threshold, so an ordinary rip stays silent -- frames normally complete in
 * milliseconds. stdout only: progress output, not part of the log contract.
 *
 * The LSN reported is the frame this read was *asked* to return, which is the
 * only thing we know. Paranoia over-reads and re-reads around it, so the drive
 * head may well be somewhere else; the line says "the read for LSN N has not
 * returned" rather than "the drive is at LSN N" for that reason.
 */

#include "stall_watchdog.h"
#include "cyanrip_log.h"

#include <inttypes.h>
#include <pthread.h>
#include <libavutil/time.h>

/* Configurable via -k. A consumer whose own stall detector fires at three
 * minutes does not want eighteen heartbeats before it would even call it a
 * stall (Platterpus, round 5 A6). A threshold of 0 disables reporting. */
static int64_t stall_threshold_us = 10LL * 1000000LL;
static int64_t heartbeat_us       = 10LL * 1000000LL;

/* Shared with the watchdog thread; every access takes live_lock.
 * read_started is 0 whenever no read is outstanding. */
static pthread_mutex_t live_lock = PTHREAD_MUTEX_INITIALIZER;
static int64_t read_started;
static int64_t last_heartbeat;
static int reading_track;
static lsn_t reading_lsn;

static pthread_t watchdog;
static int watchdog_running;
static int watchdog_stop;

/* Poll fast enough that the first heartbeat lands close to the threshold
 * rather than up to a full interval late, but not so fast that a long rip
 * wakes a thread thousands of times for nothing. Derived from the threshold so
 * a short test threshold gets a proportionally short tick -- there is no
 * test-only knob here. */
static int64_t tick_interval_us(void)
{
    int64_t tick = stall_threshold_us / 8;
    if (tick < 5000)
        tick = 5000;
    if (tick > 250000)
        tick = 250000;
    return tick;
}

/* Ticks regardless of what the rip thread is doing, which is the point. */
static void *watchdog_fn(void *unused)
{
    const int64_t tick = tick_interval_us();

    while (1) {
        av_usleep(tick);

        pthread_mutex_lock(&live_lock);
        if (watchdog_stop) {
            pthread_mutex_unlock(&live_lock);
            break;
        }

        const int64_t started = read_started;
        const int64_t now = av_gettime_relative();

        if (started && stall_threshold_us &&
            now - started >= stall_threshold_us &&
            (!last_heartbeat || now - last_heartbeat >= heartbeat_us)) {
            last_heartbeat = now;
            const int track = reading_track;
            const lsn_t lsn = reading_lsn;
            const int64_t secs = (now - started) / 1000000LL;
            pthread_mutex_unlock(&live_lock);
            cyanrip_log(NULL, 0,
                        "\nStill reading track %i - the read for LSN %i has not "
                        "returned after %" PRId64 "s\n", track, (int)lsn, secs);
            continue;
        }

        pthread_mutex_unlock(&live_lock);
    }

    return unused;
}

void crip_stall_watchdog_config(int64_t threshold_us, int64_t interval_us)
{
    pthread_mutex_lock(&live_lock);
    stall_threshold_us = threshold_us;
    heartbeat_us = interval_us;
    pthread_mutex_unlock(&live_lock);
}

void crip_stall_watchdog_start(void)
{
    if (watchdog_running || !stall_threshold_us)
        return;
    watchdog_stop = 0;
    if (!pthread_create(&watchdog, NULL, watchdog_fn, NULL))
        watchdog_running = 1;
}

void crip_stall_watchdog_end(void)
{
    if (!watchdog_running)
        return;
    pthread_mutex_lock(&live_lock);
    watchdog_stop = 1;
    pthread_mutex_unlock(&live_lock);
    pthread_join(watchdog, NULL);
    watchdog_running = 0;
}

void crip_stall_read_begin(int track, lsn_t lsn)
{
    pthread_mutex_lock(&live_lock);
    read_started = av_gettime_relative();
    last_heartbeat = 0;
    reading_track = track;
    reading_lsn = lsn;
    pthread_mutex_unlock(&live_lock);
}

void crip_stall_read_end(void)
{
    pthread_mutex_lock(&live_lock);
    const int64_t began = read_started;
    const int reported = !!last_heartbeat;
    const int track = reading_track;
    const lsn_t lsn = reading_lsn;
    read_started = 0;
    last_heartbeat = 0;
    pthread_mutex_unlock(&live_lock);

    /* Say the stall ended, so a reader who saw a heartbeat is not left
     * wondering whether the read ever came back. */
    if (reported)
        cyanrip_log(NULL, 0,
                    "\nTrack %i - the read for LSN %i returned after %" PRId64 "s\n",
                    track, (int)lsn, (av_gettime_relative() - began) / 1000000LL);
}
