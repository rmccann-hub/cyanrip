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

#pragma once

#include <stdint.h>
#include <cdio/cdio.h>

/* Set the stall threshold and the interval between repeat heartbeats, both in
 * microseconds. A threshold of 0 disables the watchdog entirely: start()
 * becomes a no-op. Call before crip_stall_watchdog_start(). */
void crip_stall_watchdog_config(int64_t threshold_us, int64_t interval_us);

/* Start/stop the watchdog thread. end() joins it, so no heartbeat can be
 * printed after it returns. Both are idempotent. */
void crip_stall_watchdog_start(void);
void crip_stall_watchdog_end(void);

/* Bracket one blocking read. begin() records when it started and what it is
 * reading; end() clears that and, if the watchdog reported a stall for this
 * read, prints the line saying it came back. */
void crip_stall_read_begin(int track, lsn_t lsn);
void crip_stall_read_end(void);

/* What the heartbeats added up to, for the log's disc summary.
 *
 * threshold_us is reported back rather than assumed by the caller, so the
 * summary can say what "a stall" meant for this run -- a count with no
 * threshold beside it is not a measurement anyone can compare. A threshold of
 * 0 means the watchdog was disabled, which is "we did not look", not "there
 * were none"; the two are different claims and the log must not merge them. */
typedef struct {
    int64_t threshold_us;
    int     count;
    int64_t longest_us;
    int     longest_track;
    lsn_t   longest_lsn;
} crip_stall_stats_t;

void crip_stall_stats(crip_stall_stats_t *s);
