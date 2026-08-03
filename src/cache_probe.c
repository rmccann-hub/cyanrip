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

#include "cache_probe.h"
#include "cyanrip_log.h"

/* After cache_probe.h: <cdio/read.h> uses CdIo_t and driver_return_code_t
 * without declaring them, so cdio/cdio.h must be in scope first. */
#include <cdio/read.h>
#include <libavutil/time.h>

/* Measures the drive's audio read cache, at rip time, on the disc that is
 * actually in the drive.
 *
 * Everywhere else cyanrip reports the size paranoia *models* and says plainly
 * that the drive was never probed ("Cache model:"). That is honest but it is a
 * gap: the number is an assumption, and a consumer wanting the real figure has
 * to run a separate cd-paranoia -A pass afterwards -- against a drive whose
 * state has moved on, and possibly a different disc.
 *
 * Method, which is the same idea cd-paranoia -A uses:
 *
 *   1. Read a run of sectors forward from a seed LSN. Whatever the drive
 *      caches, it caches during this.
 *   2. Seek back to the seed and read one sector again, timing it.
 *   3. A cached sector returns in microseconds; one that must come off the
 *      platter costs a seek and rotational latency, so it is slower by orders
 *      of magnitude. Growing the run until the re-read stops being fast finds
 *      the point where the seed fell out of cache -- that run length is the
 *      cache size in sectors.
 *
 * Everything here is read-only and runs before any track is ripped, so it
 * cannot affect the audio. It costs seconds of drive time, which is why it is
 * behind a flag and off by default.
 *
 * NOT VERIFIED ON HARDWARE. This environment has no drive, and no disc image
 * has a cache to measure -- an image driver returns every read at memory speed,
 * so the timing signal the method depends on does not exist. The code is
 * exercised only to the extent that it compiles and refuses to run on an image.
 * Treat a number it prints as unverified until a real drive has produced one.
 */

/* A re-read this much faster than the measured uncached cost is taken as a
 * cache hit. Deliberately generous: the two populations differ by orders of
 * magnitude on any real drive, so a loose threshold costs nothing and avoids
 * calling a merely-quick platter read a hit. */
#define CACHE_HIT_RATIO 4

/* Bounds on the search. Drives in the wild model out between roughly 64 KiB
 * and 8 MiB of audio cache; 1 to 2048 sectors spans that with room either
 * side. Stopping rather than running away matters more than the exact top. */
#define PROBE_MIN_SECTORS 1
#define PROBE_MAX_SECTORS 2048

static int64_t time_one_read(const CdIo_t *cdio, uint8_t *buf, lsn_t lsn)
{
    const int64_t t0 = av_gettime_relative();
    if (cdio_read_audio_sectors((CdIo_t *)cdio, buf, lsn, 1) != DRIVER_OP_SUCCESS)
        return -1;
    return av_gettime_relative() - t0;
}

int crip_probe_drive_cache(cyanrip_ctx *ctx, int *sectors_out)
{
    *sectors_out = 0;

    /* An image driver serves every read from the page cache, so there is no
     * timing signal to measure and any number produced would be noise. Refuse
     * rather than report one. */
    switch (cdio_get_driver_id(ctx->cdio)) {
    case DRIVER_BINCUE:
    case DRIVER_NRG:
    case DRIVER_CDRDAO:
        cyanrip_log(ctx, 0, "Cache probe:    not run (disc image has no drive cache)\n");
        return 0;
    default:
        break;
    }

    uint8_t *buf = av_malloc(CDIO_CD_FRAMESIZE_RAW * (size_t)PROBE_MAX_SECTORS);
    if (!buf) {
        cyanrip_log(ctx, 0, "Cache probe:    unknown (out of memory)\n");
        return AVERROR(ENOMEM);
    }

    /* Seed far enough in that a backseek is a real seek, and far enough from
     * the leadout that the longest forward run still lands on the disc. */
    const lsn_t seed = ctx->start_lsn + 1000;
    const lsn_t room = ctx->end_lsn - seed;
    int max_run = PROBE_MAX_SECTORS;
    if (room < max_run)
        max_run = room > 0 ? (int)room : 0;

    if (max_run < 8) {
        cyanrip_log(ctx, 0, "Cache probe:    unknown (disc too short to probe)\n");
        av_free(buf);
        return 0;
    }

    /* Establish what an uncached read costs on this drive: seek away, come
     * back, read once. Repeated because the first read after a seek can be
     * atypical, and the median of three is enough to be going on with. */
    int64_t uncached[3];
    for (int i = 0; i < 3; i++) {
        if (cdio_read_audio_sectors((CdIo_t *)ctx->cdio, buf, ctx->end_lsn - 10, 1)
            != DRIVER_OP_SUCCESS) {
            cyanrip_log(ctx, 0, "Cache probe:    unknown (read failed while calibrating)\n");
            av_free(buf);
            return 0;
        }
        uncached[i] = time_one_read(ctx->cdio, buf, seed);
        if (uncached[i] < 0) {
            cyanrip_log(ctx, 0, "Cache probe:    unknown (read failed while calibrating)\n");
            av_free(buf);
            return 0;
        }
    }

    /* Median of three, by hand -- three elements does not warrant a sort. */
    int64_t a = uncached[0], b = uncached[1], c = uncached[2];
    const int64_t miss_cost = FFMAX(FFMIN(a, b), FFMIN(FFMAX(a, b), c));

    if (miss_cost <= 0) {
        cyanrip_log(ctx, 0, "Cache probe:    unknown (drive returned reads too fast to time)\n");
        av_free(buf);
        return 0;
    }

    /* Grow the forward run until re-reading the seed is no longer fast. The
     * last run that still hit is the cache size. */
    int last_hit = 0;
    for (int run = PROBE_MIN_SECTORS; run <= max_run; run *= 2) {
        if (cdio_read_audio_sectors((CdIo_t *)ctx->cdio, buf, seed, run)
            != DRIVER_OP_SUCCESS)
            break;

        const int64_t t = time_one_read(ctx->cdio, buf, seed);
        if (t < 0)
            break;

        if (t * CACHE_HIT_RATIO < miss_cost)
            last_hit = run;
        else
            break;
    }

    av_free(buf);

    if (!last_hit) {
        /* The seed was already gone after the shortest possible run, so either
         * the drive caches nothing or it caches less than one sector. Both are
         * "no measurable cache", and neither is "the cache was defeated". */
        cyanrip_log(ctx, 0, "Cache probe:    no readback cache measured "
                            "(uncached read %.1f ms)\n", miss_cost / 1000.0);
        return 0;
    }

    *sectors_out = last_hit;
    cyanrip_log(ctx, 0, "Cache probe:    %i sectors measured "
                        "(%.1f KiB, uncached read %.1f ms)\n",
                last_hit, last_hit * CDIO_CD_FRAMESIZE_RAW / 1024.0,
                miss_cost / 1000.0);
    return 0;
}
