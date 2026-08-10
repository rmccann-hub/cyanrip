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

/* Every wording the `Cache probe:` line can take.
 *
 * The probe reaches all but one of these only from a real drive, and until
 * 2026-08-10 no real drive had ever run it -- so the only wording anyone could
 * read was whichever one their disc produced, and the other eight existed
 * purely in the source. That first hardware run (PIONEER BD-RW BDR-209D,
 * pressed audio CD: hit at 32 sectors, miss at 64, 364.3 ms uncached read)
 * exposed two defects no disc-image fixture could have, and both are pinned
 * below:
 *
 *   D1  the doubling search can only ever return a power of two, so a hit at
 *       32 and a miss at 64 bounds the cache to [32, 64) -- it does not
 *       measure it. The line used to say "32 sectors measured".
 *
 *   D2  the search stops for four reasons and three of them are not "the cache
 *       ran out". All four printed the same line, so a failed read at 64
 *       sectors was indistinguishable from a genuine cache miss there.
 *
 * The D2 case is the one worth reading twice: identical (last_hit, stop_run)
 * with a different stop reason must produce different text, or the line has
 * gone back to collapsing a failure into a measurement. */

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "cache_probe.h"
#include "cyanrip_log.h"   /* for the prototype of the cyanrip_log() below */

int fails = 0;

/* cache_probe.c logs through this; the test supplies its own so the assertions
 * are against the composed string rather than scraped stdout. Nothing here
 * calls the emitter, but the object still has to link. */
void cyanrip_log(cyanrip_ctx *ctx, int verbose, const char *format, ...)
{
    (void)ctx; (void)verbose; (void)format;
}

static void expect(crip_cache_stop_t stop, int last_hit, int stop_run,
                   int64_t miss_us, const char *want)
{
    char got[160];
    crip_cache_probe_line(got, sizeof(got), stop, last_hit, stop_run, miss_us);
    if (strcmp(got, want)) {
        printf("FAIL: stop=%i last_hit=%i stop_run=%i\n  want: %s\n  got:  %s\n",
               (int)stop, last_hit, stop_run, want, got);
        fails++;
    }
}

int main(void)
{
    const int64_t MS364 = 364300; /* the measured uncached read, in ss */

    /* Never searched. Each says why, because "could not tell" and "no cache"
     * are different claims about the drive. */
    expect(CRIP_CACHE_IMAGE, 0, 0, 0,
           "not run (disc image has no drive cache)");
    expect(CRIP_CACHE_OOM, 0, 0, 0,
           "unknown (out of memory)");
    expect(CRIP_CACHE_SHORT_DISC, 0, 0, 0,
           "unknown (disc too short to probe)");
    expect(CRIP_CACHE_CALIB_READ_FAIL, 0, 0, 0,
           "unknown (read failed while calibrating)");
    expect(CRIP_CACHE_CALIB_TOO_FAST, 0, 0, 0,
           "unknown (drive returned reads too fast to time)");

    /* D1: the real hardware result. A bracket, not a measurement. */
    expect(CRIP_CACHE_MISS, 32, 64, MS364,
           "32 to 63 sectors (73.5 to 144.7 KiB, uncached read 364.3 ms)");

    /* Still hitting when the search ran out of room: a lower bound only. */
    expect(CRIP_CACHE_CEILING, 2048, 2048, MS364,
           "at least 2048 sectors, upper bound unknown "
           "(4704.0 KiB or more, search ceiling reached, uncached read 364.3 ms)");

    /* D2: same numbers as the hardware result, different reason for stopping.
     * These two lines must not be the same sentence. */
    expect(CRIP_CACHE_READ_FAIL, 32, 64, MS364,
           "at least 32 sectors, upper bound unknown "
           "(73.5 KiB or more, read failed while growing the run, "
           "uncached read 364.3 ms)");
    expect(CRIP_CACHE_TIME_FAIL, 32, 64, MS364,
           "at least 32 sectors, upper bound unknown "
           "(73.5 KiB or more, read could not be timed while growing the run, "
           "uncached read 364.3 ms)");

    /* Nothing hit at all. A drive that caches nothing is a measurement; a read
     * that failed before anything could hit is not, and must not borrow the
     * measurement's wording. Singular "sector" at 1. */
    expect(CRIP_CACHE_MISS, 0, 1, MS364,
           "no readback cache measured (uncached read 364.3 ms)");
    expect(CRIP_CACHE_READ_FAIL, 0, 1, MS364,
           "unknown (read failed at 1 sector, before any cache hit)");
    expect(CRIP_CACHE_TIME_FAIL, 0, 2, MS364,
           "unknown (read could not be timed at 2 sectors, before any cache hit)");

    /* The retired wording, asserted absent rather than merely not asserted:
     * "N sectors measured" is the claim the method cannot support. */
    char line[160];
    crip_cache_probe_line(line, sizeof(line), CRIP_CACHE_MISS, 32, 64, MS364);
    if (strstr(line, "sectors measured")) {
        printf("FAIL: the bracket line still claims to have measured a size: %s\n",
               line);
        fails++;
    }

    if (fails)
        printf("%i check(s) failed\n", fails);
    else
        printf("cache probe line: all wordings pinned\n");
    return !!fails;
}
