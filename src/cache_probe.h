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

/* THE EVIDENCE THE VERDICT WAS FORMED FROM, recorded so a calibration fix can
 * be designed against data instead of against reasoning about data.
 *
 * `Cache probe:` publishes three numbers -- the calibration cost, the last
 * cached read, the first uncached one. That is enough to see THAT the
 * threshold is wrong and not enough to work out what it should be: the series
 * of per-run times is what carries the step, and the line has never carried
 * it. Eight filed rig sessions report `at least 2048 sectors ... search
 * ceiling reached` and not one of them recorded the twelve timings behind it,
 * so every one of those sessions is unusable for fixing the defect it
 * demonstrates.
 *
 * A read time is a measurement of a physical drive at a moment and cannot be
 * re-taken; not recording it is the same class of loss as a superseded track's
 * read time. So this is captured in round 21 and the DECISION RULE IS NOT
 * TOUCHED -- a rule redesigned before its evidence exists is the thing this
 * repository has a rule against.
 *
 * Bounded at 16: the search doubles from 1 to PROBE_MAX_SECTORS, which is 12
 * steps, and a bound that cannot be exceeded beats a growable buffer in a
 * process that must not fail here. */
#define CRIP_CACHE_MAX_STEPS 16

typedef struct {
    int     ran;                /* the probe got as far as recording anything */
    int64_t calib_us[3];        /* the three calibration reads, in order */
    int64_t miss_cost_us;       /* the median of them, which is the threshold */
    int     hit_ratio;          /* CACHE_HIT_RATIO as it was at the time */
    int     nb_steps;
    int     step_run[CRIP_CACHE_MAX_STEPS];   /* run length in sectors */
    int64_t step_us[CRIP_CACHE_MAX_STEPS];    /* the re-read that classified it */
    int     step_hit[CRIP_CACHE_MAX_STEPS];   /* what the CURRENT rule decided */
    crip_cache_stop_t stop;
} crip_cache_evidence_t;

/* Process-lifetime, owned here, read by the diagnostics record at exit. Never
 * NULL; `ran` is 0 when the probe did not run or refused. */
const crip_cache_evidence_t *crip_cache_evidence(void);

/* Composes the value half of the `Cache probe:` line into buf.
 *
 * Split out for the same reason crip_stall_summary_line() is: the branches are
 * reachable only from a real drive, so left inline the only wording anyone
 * could read was whichever one their disc happened to produce, and the rest
 * existed solely in the source. tests/cacheprobe.c pins all nine.
 *
 * last_hit is the largest run that still hit, stop_run the run the search
 * stopped at, and miss_cost_us the calibrated uncached read. Fields a given
 * outcome does not use are ignored.
 *
 * last_hit_us and stop_us are the timings of the reads the probe CLASSIFIED --
 * the last one it called cached, and the one that ended the search. Pass -1
 * for either that does not apply. They exist because the line used to report
 * miss_cost_us alone, which is one side of a two-sided comparison: a reader
 * could see the verdict and not the evidence, and could not tell a real cache
 * from a threshold every read beats. */
void crip_cache_probe_line(char *buf, size_t buf_size, crip_cache_stop_t stop,
                           int last_hit, int stop_run, int64_t miss_cost_us,
                           int64_t last_hit_us, int64_t stop_us);
