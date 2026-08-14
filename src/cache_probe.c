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
#include "stall_watchdog.h"

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
 * RUN ONCE ON HARDWARE, 2026-08-10, and the date matters more than the fact.
 * A PIONEER BD-RW BDR-209D 1.51 with a pressed audio CD returned a hit at 32
 * sectors and a miss at 64, with an uncached single-sector read costing
 * 364.3 ms. That is one drive, one disc, one run: enough to say the method
 * produces a signal on real hardware, not enough to say it is right. Nothing
 * cross-checks it -- cd-paranoia -A on the same drive would, and has not been
 * run.
 *
 * That single run found two defects no fixture could have. It reported the
 * lower bound as though it were the size, and it printed the same line whether
 * the search ended in a cache miss, a failed read, or a read it could not
 * time. Both are fixed below. This environment still has no drive, and no disc
 * image has a cache to measure -- an image driver returns every read at memory
 * speed, so the timing signal the method depends on does not exist there, and
 * the code is still exercised in-tree only to the extent that it compiles and
 * refuses to run on an image.
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

/* Sectors per read COMMAND, which is not the same thing as sectors per run.
 *
 * The forward run is a warm-up whose only job is to put data in the drive's
 * cache; whether it arrives as one transfer or several does not change what
 * ends up cached. Issuing it as one transfer does, however, put a hard ceiling
 * on the search: a single command of 64 sectors is 150,528 bytes, and an sr
 * device's max_sectors_kb is commonly 128 KiB, so the read simply fails.
 *
 * Measured, 2026-08-10, PIONEER BD-RW BDR-209D: the search hit at 32 and the
 * 64-sector read FAILED, so the probe stopped and reported "at least 32
 * sectors". cd-paranoia -A on the same drive and disc reports an approximate
 * random-access cache of 137 sectors. The ceiling was ours, not the drive's,
 * and before the wording fix one commit earlier this same event printed
 * "32 sectors measured" -- a number wrong by a factor of four, in a line that
 * goes into an archival record.
 *
 * 25 sectors is 58,800 bytes, comfortably under even a 64 KiB limit. A read
 * that fails at this size is a real read failure and still ends the search,
 * which is what the STOP_READ_FAIL wording is for. */
#define PROBE_CHUNK_SECTORS 25

/* Every read here brackets itself for the stall watchdog. These are raw MMC
 * reads on a path that has never run on hardware, so a hang is a live
 * possibility -- and a hang with no heartbeat is indistinguishable from a
 * wedged process, which is the whole thing the watchdog exists to prevent.
 * Track 0 is not a real track number and is deliberate: it says "not ripping a
 * track" rather than blaming one. */
#define PROBE_PSEUDO_TRACK 0

/* One command. Callers wanting a run of arbitrary length use probe_read_run(). */
static driver_return_code_t probe_read(const CdIo_t *cdio, uint8_t *buf,
                                       lsn_t lsn, int sectors)
{
    crip_stall_read_begin(PROBE_PSEUDO_TRACK, lsn);
    const driver_return_code_t r =
        cdio_read_audio_sectors((CdIo_t *)cdio, buf, lsn, sectors);
    crip_stall_read_end();
    return r;
}

/* A run of `sectors`, issued as however many commands it takes. See
 * PROBE_CHUNK_SECTORS for why this is not one call. */
static driver_return_code_t probe_read_run(const CdIo_t *cdio, uint8_t *buf,
                                           lsn_t lsn, int sectors)
{
    for (int done = 0; done < sectors; ) {
        const int n = FFMIN(PROBE_CHUNK_SECTORS, sectors - done);
        const driver_return_code_t r =
            probe_read(cdio, buf + (size_t)done * CDIO_CD_FRAMESIZE_RAW,
                       lsn + done, n);
        if (r != DRIVER_OP_SUCCESS)
            return r;
        done += n;
    }
    return DRIVER_OP_SUCCESS;
}

static int64_t time_one_read(const CdIo_t *cdio, uint8_t *buf, lsn_t lsn)
{
    const int64_t t0 = av_gettime_relative();
    if (probe_read(cdio, buf, lsn, 1) != DRIVER_OP_SUCCESS)
        return -1;
    return av_gettime_relative() - t0;
}

void crip_cache_probe_line(char *buf, size_t buf_size, crip_cache_stop_t stop,
                           int last_hit, int stop_run, int64_t miss_cost_us,
                           int64_t last_hit_us, int64_t stop_us)
{
    const double miss_ms = miss_cost_us / 1000.0;
    /* Both sides of the comparison, or neither is checkable. `hit` is the read
     * the probe called cached; `miss` is the calibration read. A reader who
     * sees only the second cannot tell a real cache from a threshold that
     * every read beats -- which is exactly what happened on 2026-08-11, where
     * a 342.9 ms calibration and ~2 ms test reads made every run a "hit" up to
     * the search ceiling. The ratio is now in the artifact rather than in
     * somebody's reasoning about the artifact. */
    char ev[64] = "";
    if (last_hit_us >= 0)
        snprintf(ev, sizeof(ev), ", cached read %.1f ms", last_hit_us / 1000.0);
    else if (stop_us >= 0)
        snprintf(ev, sizeof(ev), ", first uncached re-read %.1f ms", stop_us / 1000.0);
    const double lo_kib  = last_hit * CDIO_CD_FRAMESIZE_RAW / 1024.0;

    switch (stop) {
    case CRIP_CACHE_IMAGE:
        snprintf(buf, buf_size, "not run (disc image has no drive cache)");
        return;
    case CRIP_CACHE_OOM:
        snprintf(buf, buf_size, "unknown (out of memory)");
        return;
    case CRIP_CACHE_SHORT_DISC:
        snprintf(buf, buf_size, "unknown (disc too short to probe)");
        return;
    case CRIP_CACHE_CALIB_READ_FAIL:
        snprintf(buf, buf_size, "unknown (read failed while calibrating)");
        return;
    case CRIP_CACHE_CALIB_TOO_FAST:
        snprintf(buf, buf_size, "unknown (drive returned reads too fast to time)");
        return;
    default:
        break;
    }

    if (!last_hit) {
        /* Nothing hit, even at one sector -- but that is not one fact. A read
         * that failed says nothing whatever about the cache, and must not be
         * reported as an absence of one. */
        if (stop == CRIP_CACHE_READ_FAIL || stop == CRIP_CACHE_TIME_FAIL)
            snprintf(buf, buf_size,
                     "unknown (%s at %i sector%s, before any cache hit)",
                     stop == CRIP_CACHE_READ_FAIL ? "read failed"
                                                  : "read could not be timed",
                     stop_run, stop_run == 1 ? "" : "s");
        else
            /* The seed was already gone after the shortest possible run, so
             * either the drive caches nothing or it caches less than one
             * sector. Both are "no measurable cache", and neither is "the
             * cache was defeated". */
            snprintf(buf, buf_size,
                     "no readback cache measured (uncached read %.1f ms%s)",
                     miss_ms, ev);
        return;
    }

    if (stop == CRIP_CACHE_MISS)
        snprintf(buf, buf_size,
                 "%i to %i sectors (%.1f to %.1f KiB, uncached read %.1f ms%s)",
                 last_hit, stop_run - 1, lo_kib,
                 (stop_run - 1) * CDIO_CD_FRAMESIZE_RAW / 1024.0, miss_ms, ev);
    else
        snprintf(buf, buf_size,
                 "at least %i sectors, upper bound unknown "
                 "(%.1f KiB or more, %s, uncached read %.1f ms%s)",
                 last_hit, lo_kib,
                 stop == CRIP_CACHE_CEILING   ? "search ceiling reached" :
                 stop == CRIP_CACHE_READ_FAIL ? "read failed while growing the run"
                                              : "read could not be timed while growing the run",
                 miss_ms, ev);
}

/* Emits it. Every exit from the probe goes through here, so no wording can
 * exist that the composer -- and therefore the test -- does not know about. */
static void log_cache_probe(cyanrip_ctx *ctx, crip_cache_stop_t stop,
                            int last_hit, int stop_run, int64_t miss_cost_us,
                            int64_t last_hit_us, int64_t stop_us)
{
    char line[224];
    crip_cache_probe_line(line, sizeof(line), stop, last_hit, stop_run,
                          miss_cost_us, last_hit_us, stop_us);
    cyanrip_log(ctx, 0, "Cache probe:    %s\n", line);
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
        log_cache_probe(ctx, CRIP_CACHE_IMAGE, 0, 0, 0, -1, -1);
        return 0;
    default:
        break;
    }

    uint8_t *buf = av_malloc(CDIO_CD_FRAMESIZE_RAW * (size_t)PROBE_MAX_SECTORS);
    if (!buf) {
        log_cache_probe(ctx, CRIP_CACHE_OOM, 0, 0, 0, -1, -1);
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
        log_cache_probe(ctx, CRIP_CACHE_SHORT_DISC, 0, 0, 0, -1, -1);
        av_free(buf);
        return 0;
    }

    /* Establish what an uncached read costs on this drive: seek away, come
     * back, read once. Repeated because the first read after a seek can be
     * atypical, and the median of three is enough to be going on with. */
    int64_t uncached[3];
    for (int i = 0; i < 3; i++) {
        if (probe_read(ctx->cdio, buf, ctx->end_lsn - 10, 1)
            != DRIVER_OP_SUCCESS) {
            log_cache_probe(ctx, CRIP_CACHE_CALIB_READ_FAIL, 0, 0, 0, -1, -1);
            av_free(buf);
            return 0;
        }
        uncached[i] = time_one_read(ctx->cdio, buf, seed);
        if (uncached[i] < 0) {
            log_cache_probe(ctx, CRIP_CACHE_CALIB_READ_FAIL, 0, 0, 0, -1, -1);
            av_free(buf);
            return 0;
        }
    }

    /* Median of three, by hand -- three elements does not warrant a sort. */
    int64_t a = uncached[0], b = uncached[1], c = uncached[2];
    const int64_t miss_cost = FFMAX(FFMIN(a, b), FFMIN(FFMAX(a, b), c));

    if (miss_cost <= 0) {
        log_cache_probe(ctx, CRIP_CACHE_CALIB_TOO_FAST, 0, 0, 0, -1, -1);
        av_free(buf);
        return 0;
    }

    /* Grow the forward run until re-reading the seed is no longer fast.
     *
     * The last run that still hit is a LOWER BOUND on the cache, not its size.
     * The search doubles, so a hit at 32 and a miss at 64 establishes only
     * that the cache holds at least 32 sectors and fewer than 64 -- and the
     * answer can never be anything but a power of two. The first version
     * printed "32 sectors measured", which claimed a precision the method
     * cannot deliver. Found by the first run this code ever had on real
     * hardware, 2026-08-10; every disc image refuses the probe, so no fixture
     * could have caught it.
     *
     * Why the search stopped is recorded too, because three different endings
     * used to print the same line: a genuine cache miss, a failed read, and a
     * read that could not be timed. "The cache ran out at 64 sectors" and
     * "the read at 64 sectors failed" are different claims about the drive,
     * and a consumer cannot act on the second if it arrives dressed as the
     * first. */
    crip_cache_stop_t stop = CRIP_CACHE_CEILING;
    int last_hit = 0, stop_run = 0;
    /* The reads that were CLASSIFIED, not just the one used to calibrate. The
     * probe reported `uncached read N ms` and nothing about the other side of
     * its own comparison, so a reader could see the verdict and not the
     * evidence for it -- which is the shape this project treats as a defect
     * wherever it appears in someone else's output. */
    int64_t last_hit_us = -1, stop_us = -1;

    for (int run = PROBE_MIN_SECTORS; run <= max_run; run *= 2) {
        stop_run = run;

        if (probe_read_run(ctx->cdio, buf, seed, run) != DRIVER_OP_SUCCESS) {
            stop = CRIP_CACHE_READ_FAIL;
            break;
        }

        const int64_t t = time_one_read(ctx->cdio, buf, seed);
        if (t < 0) {
            stop = CRIP_CACHE_TIME_FAIL;
            break;
        }

        if (t * CACHE_HIT_RATIO < miss_cost) {
            last_hit = run;
            last_hit_us = t;
            stop = CRIP_CACHE_CEILING;   /* until a later iteration says otherwise */
        } else {
            stop = CRIP_CACHE_MISS;
            stop_us = t;
            break;
        }
    }

    av_free(buf);

    /* The lower bound is what the caller gets: it is the figure the evidence
     * supports, and erring low is the safe direction for anything downstream
     * that seeks back past a cache. */
    if (stop == CRIP_CACHE_MISS || stop == CRIP_CACHE_CEILING)
        *sectors_out = last_hit;

    log_cache_probe(ctx, stop, last_hit, stop_run, miss_cost,
                    last_hit_us, stop_us);
    return 0;
}
