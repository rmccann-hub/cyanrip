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

/* A relative amplitude in 0.0-1.0 as dBFS, for comparison against a figure
 * already in dBFS.
 *
 * Zero means "not measured", not "silence", and that reading is what makes the
 * cross-check usable: upstream's sample_peak_rel_amp starts at 0.0 and stays
 * there for a data track or a track that never ripped. -INFINITY is what
 * crip_peaks_disagree() treats as an absence rather than as a disagreement, so
 * such a track stays silent instead of reporting a cross-check failure of
 * infinite size.
 *
 * THE EXPLICIT ZERO TEST IS DEFENSIVE AND CHANGES NOTHING, said here because
 * the first draft of this comment claimed otherwise. log10(0.0) is already
 * -INFINITY under IEEE-754, so removing the branch gives identical results for
 * every value this can be called with -- which is why the revert-proof for it
 * failed to fail, correctly. It is kept because it states the intent at the
 * point of the decision, and because a negative input would otherwise be NaN;
 * both are non-finite and reach the same verdict, so even that is not
 * observable, and no caller can produce one.
 *
 * Pure and inline for the same reason as the function below: the caller is a
 * static in cyanrip_log.c on a path no disc image can reach, so this is the
 * only place the conversion can be exercised at all. */
static inline double crip_rel_amp_to_dbfs(double rel_amp)
{
    return rel_amp > 0.0 ? 20.0 * log10(rel_amp) : -INFINITY;
}

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

/* The parenthetical on the `Cache model:` line, chosen from two facts and
 * nothing else.
 *
 * A FUNCTION RATHER THAN AN `if` AT THE CALL SITE, for the same reason
 * crip_signal_name() is here: the call site is print_cache_model(), which needs
 * a live cdio handle and a paranoia context, so the physical-drive branch is
 * unreachable from every disc-image fixture -- all three image drivers take the
 * image arm before ever reaching it. The choice is pure, so it is separated out
 * and asserted directly rather than shipped on the strength of a code reading.
 *
 * THE DEFECT IT EXISTS FOR. The drive arm said "(drive cache size not probed)"
 * unconditionally, and `-x` can probe it. Measured 2026-08-25 on the first
 * `-x -I` ever to finish on real hardware: one log carried
 * `Cache model: 1200 sectors (drive cache size not probed)` in its header and
 * `Cache probe: at least 2048 sectors` forty lines below, in that order, so the
 * denial reads first.
 *
 * The two numbers stay separate and neither is derived from the other -- the
 * model is what paranoia was configured with, the probe is what the drive did.
 * All that changes is that the line stops denying the other one exists. */
enum {
    CRIP_CACHE_NOTE_IMAGE = 0,      /* no drive, so nothing to probe */
    CRIP_CACHE_NOTE_UNPROBED,       /* a drive, and -x was not asked for */
    CRIP_CACHE_NOTE_PROBED,         /* a drive, and -x measured it this run */
};

static inline int crip_cache_model_note(int is_image, int probe_requested)
{
    if (is_image)
        return CRIP_CACHE_NOTE_IMAGE;
    return probe_requested ? CRIP_CACHE_NOTE_PROBED : CRIP_CACHE_NOTE_UNPROBED;
}

static inline int cmp_numbers(const void *a, const void *b)
{
    return *((int *)a) > *((int *)b);
}
