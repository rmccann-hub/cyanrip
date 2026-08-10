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

#include "cyanrip_main.h"

/* Measures the drive's audio readback cache by timing re-reads, and logs the
 * result. Read-only, runs before ripping, cannot affect the audio.
 *
 * *sectors_out is the measured size, or 0 when nothing was measured -- which
 * covers "no cache", "disc image", and "could not tell", each of which the log
 * line distinguishes in words. Returns 0 unless allocation failed.
 *
 * Run once on hardware, 2026-08-10: see the comment block in cache_probe.c. */
int crip_probe_drive_cache(cyanrip_ctx *ctx, int *sectors_out);

/* Every way the probe can end. The search stops for four different reasons and
 * three of them are not "the cache ran out", which the first version could not
 * say -- it printed one line for all of them. */
typedef enum {
    CRIP_CACHE_MISS,            /* seed fell out of cache: a real upper bound */
    CRIP_CACHE_CEILING,         /* still hitting when the search ran out of room */
    CRIP_CACHE_READ_FAIL,       /* a read failed while growing the run */
    CRIP_CACHE_TIME_FAIL,       /* a read could not be timed while growing */
    CRIP_CACHE_SHORT_DISC,      /* never searched: no room between seed and leadout */
    CRIP_CACHE_CALIB_READ_FAIL, /* never searched: calibration read failed */
    CRIP_CACHE_CALIB_TOO_FAST,  /* never searched: reads too fast to time */
    CRIP_CACHE_IMAGE,           /* refused: an image driver has no cache */
    CRIP_CACHE_OOM,
} crip_cache_stop_t;

/* Composes the value half of the `Cache probe:` line into buf.
 *
 * Split out for the same reason crip_stall_summary_line() is: the branches are
 * reachable only from a real drive, so left inline the only wording anyone
 * could read was whichever one their disc happened to produce, and the rest
 * existed solely in the source. tests/cacheprobe.c pins all nine.
 *
 * last_hit is the largest run that still hit, stop_run the run the search
 * stopped at, and miss_cost_us the calibrated uncached read. Fields a given
 * outcome does not use are ignored. */
void crip_cache_probe_line(char *buf, size_t buf_size, crip_cache_stop_t stop,
                           int last_hit, int stop_run, int64_t miss_cost_us);
