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

#include <math.h>

#include <signal.h>
#include <stdio.h>
#include <stddef.h>
#include <string.h>

#include <libavutil/rational.h>
#include <libavutil/mathematics.h>
#include <libavutil/dict.h>

/* Sliding window */
#define MAX_ROLLING_WIN_ENTRIES 1024 * 16
typedef struct CRSlidingWinCtx {
    struct CRSlidingWinEntry {
        int64_t num;
        int64_t pts;
        AVRational tb;
    } entries[MAX_ROLLING_WIN_ENTRIES];
    int num_entries;
} CRSlidingWinCtx;

int64_t cr_sliding_win(CRSlidingWinCtx *ctx, int64_t num, int64_t pts,
                       AVRational tb, int64_t len, int do_avg);

char *cr_ffmpeg_file_path(const char *path);

static inline const char *dict_get(AVDictionary *dict, const char *key)
{
    AVDictionaryEntry *e = av_dict_get(dict, key, NULL, 0);
    return e ? e->value : NULL;
}

static inline void cyanrip_frames_to_cue(uint32_t frames, char *str)
{
    if (!str)
        return;
    const uint32_t min  = frames / (75 * 60);
    const uint32_t sec  = (frames - (min * 75 * 60)) / 75;
    const uint32_t left = frames - (min * 75 * 60) - (sec * 75);
    snprintf(str, 16, "%02i:%02i:%02i", min, sec, left);
}

/**
 * Writes the duration, in MSF as IEC/MMC specify the string (min:sec.ff), to
 * the char*. Min can be larger than 59. Make sure that the char* is at least 13
 * bytes long. Frames is nice to avoid any potential rounding error.
 */
static inline void cyanrip_frames_to_duration(uint32_t frames, char *str)
{
    if (!str)
        return;
    // 75 frames per second
    const uint32_t min    = frames / (75 * 60);
    const uint32_t sec    = (frames / 75) % 60;
    const uint32_t remain = frames % 75;
    snprintf(str, 13, "%02i:%02i.%02i", min, sec, remain);
}

/* Do two measurements of the same sample peak disagree enough to be worth
 * reporting? (H6, Platterpus round 7.)
 *
 * Pure and in a header so tests/peak.c can exercise it without linking the log
 * writer. The path that *fires* it cannot be reached from a disc image -- two
 * correct measurements of the same frames agree -- so the decision has to be
 * testable on its own or the feature is decoration that has never run.
 *
 * The threshold is not zero: both figures are doubles derived through a log and
 * ebur128 accumulates in float, so exact equality is not expected even when
 * nothing is wrong. 0.1 dB sits below the precision the peak lines are printed
 * at, so anything this catches is already visible in them.
 *
 * A non-finite input means "not measured" and is never a disagreement --
 * absence of a measurement is not evidence of one. */
#define CRIP_PEAK_DISAGREE_DB 0.1

static inline int crip_peaks_disagree(double a_db, double b_db, double *delta)
{
    if (delta)
        *delta = 0.0;
    if (!isfinite(a_db) || !isfinite(b_db))
        return 0;
    const double d = fabs(a_db - b_db);
    if (delta)
        *delta = d;
    return d >= CRIP_PEAK_DISAGREE_DB;
}

/* The name of a signal cyanrip installs a quit handler for.
 *
 * NULL for anything else, deliberately: a caller has to decide what to print
 * rather than being handed a plausible-looking guess. Both the logfile's
 * `Rip completed: no (interrupted by ...)` and the diagnostics record's
 * `interrupted_by` fall back to the number, so a signal added to the handler
 * and forgotten here is reported as a number and not as whichever name a
 * switch fell through to.
 *
 * Inline in a header rather than in cyanrip_main.c, and that placement is the
 * point: tests/diag.c links diagnostics.c without the disc context, so a
 * definition in cyanrip_main.c would have forced the test to carry its own
 * copy -- two implementations of one convention, able to differ silently while
 * every test on both sides passes. There is one definition and everything uses
 * it. */
static inline const char *crip_signal_name(int signo)
{
    switch (signo) {
    case SIGINT:  return "SIGINT";
    case SIGTERM: return "SIGTERM";
    default:      return NULL;
    }
}

static inline int cmp_numbers(const void *a, const void *b)
{
    return *((int *)a) > *((int *)b);
}
