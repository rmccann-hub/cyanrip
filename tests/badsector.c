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

/* ONE UNREADABLE SECTOR, WITHOUT A DRIVE.
 *
 * An LD_PRELOAD shim for a disc-image rip. libcdio's image drivers read the
 * .bin through stdio, so interposing fread() lets a test declare one sector
 * bad: any read of the image whose byte range overlaps CRIP_BAD_SECTOR fails
 * with EIO, the way a drive fails the whole command. Every other read passes
 * through untouched.
 *
 * It exists because "damaged media" was on the hardware-only list, and part of
 * it is not. The MMC read itself and C2 still need a drive. What cyanrip and
 * libcdio-paranoia do once a read fails -- retry, skip, count, report -- is the
 * same code on an image, and this shim is how it got measured. That is how the
 * per-frame retry hang behind crip_frame_retry_limit() was found.
 *
 *   CRIP_BAD_PATH    substring of the image path to fail (e.g. "basic.bin")
 *   CRIP_BAD_SECTOR  the sector index within that file
 *   CRIP_BAD_OUT     where to write the number of reads failed, at exit, so a
 *                    test can prove the shim was active and not vacuous
 *
 * AND READS THAT DISAGREE, ON A SCHEDULE. An image reads the same bytes every
 * time, so `-Z` always converges on one and the repeat limit is unreachable.
 * With CRIP_FLIP_SECTOR set, the k-th read of that sector has its first byte
 * XORed with (k / CRIP_FLIP_RUN % CRIP_FLIP_CYCLE) + 1, so a cycle of 2 gives
 * reads A, B, A, a long cycle gives reads that all differ, and a run of 2 with
 * a cycle of 2 gives A, A, B. It never fails a read, and it
 * is independent of CRIP_BAD_SECTOR. Round 29 lap 1 S38's repeat-limit line is
 * what it was added for.
 *
 *   CRIP_FLIP_SECTOR the sector index within the file to vary
 *   CRIP_FLIP_CYCLE  how many distinct versions of it to cycle through
 *   CRIP_FLIP_RUN    how many reads in a row get each version (default 1)
 *   CRIP_FLIP_OUT    where to write the number of reads varied, at exit
 *
 * And CRIP_NO_TMPFILE, set to anything, makes tmpfile() fail with ENOSPC.
 */

/* The build passes -D_FILE_OFFSET_BITS=64, under which glibc renames fopen
 * to fopen64 by asm label, so defining both collides. Both are defined here
 * on purpose, because libcdio may call either, and the shim must catch
 * whichever it calls. */
#undef _FILE_OFFSET_BITS
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static FILE *victim;
static long bad_sector = -1;
static long failed_reads;
static long flip_sector = -1;
static long flip_cycle = 1;
static long flip_run = 1;
static long flipped_reads;

static void report(void)
{
    const char *out = getenv("CRIP_BAD_OUT");
    FILE *(*real_fopen)(const char *, const char *) = dlsym(RTLD_NEXT, "fopen");
    FILE *f;
    if (!out || !real_fopen || !(f = real_fopen(out, "w")))
        return;
    fprintf(f, "%ld\n", failed_reads);
    fclose(f);
}

static void report_flips(void)
{
    const char *out = getenv("CRIP_FLIP_OUT");
    FILE *(*real_fopen)(const char *, const char *) = dlsym(RTLD_NEXT, "fopen");
    FILE *f;
    if (!out || !real_fopen || !(f = real_fopen(out, "w")))
        return;
    fprintf(f, "%ld\n", flipped_reads);
    fclose(f);
}

FILE *fopen(const char *path, const char *mode)
{
    static FILE *(*real)(const char *, const char *);
    const char *want = getenv("CRIP_BAD_PATH");
    FILE *f;

    if (!real) {
        const char *s = getenv("CRIP_BAD_SECTOR");
        real = dlsym(RTLD_NEXT, "fopen");
        if (s)
            bad_sector = atol(s);
        if ((s = getenv("CRIP_FLIP_SECTOR")))
            flip_sector = atol(s);
        if ((s = getenv("CRIP_FLIP_CYCLE")) && atol(s) > 0)
            flip_cycle = atol(s);
        if ((s = getenv("CRIP_FLIP_RUN")) && atol(s) > 0)
            flip_run = atol(s);
        atexit(report);
        atexit(report_flips);
    }
    f = real(path, mode);
    if (f && want && strstr(path, want))
        victim = f;
    return f;
}

FILE *fopen64(const char *path, const char *mode)
{
    return fopen(path, mode);
}

/* CRIP_NO_TMPFILE makes tmpfile() fail with ENOSPC, as a full disk would, so
 * the refusal of the -Z spool (round 30) can be driven with no full disk.
 * Both names, for the same reason as fopen above. */
FILE *tmpfile(void)
{
    static FILE *(*real)(void);
    if (getenv("CRIP_NO_TMPFILE")) {
        errno = ENOSPC;
        return NULL;
    }
    if (!real)
        real = dlsym(RTLD_NEXT, "tmpfile");
    return real ? real() : NULL;
}

FILE *tmpfile64(void)
{
    return tmpfile();
}

size_t fread(void *ptr, size_t size, size_t n, FILE *f)
{
    static size_t (*real)(void *, size_t, size_t, FILE *);
    if (!real)
        real = dlsym(RTLD_NEXT, "fread");
    if (victim && f == victim && bad_sector >= 0) {
        long a = ftell(f), b = a + (long)(size * n);
        long lo = bad_sector * 2352, hi = lo + 2352;
        if (a >= 0 && a < hi && b > lo) {
            failed_reads++;
            errno = EIO;
            return 0;
        }
    }
    if (victim && f == victim && flip_sector >= 0) {
        long a = ftell(f);
        long lo = flip_sector * 2352;
        size_t got = real(ptr, size, n, f);
        long b = a + (long)(size * got);
        if (a >= 0 && lo >= a && lo < b) {
            ((unsigned char *)ptr)[lo - a] ^= (unsigned char)(flipped_reads / flip_run % flip_cycle + 1);
            flipped_reads++;
        }
        return got;
    }
    return real(ptr, size, n, f);
}
