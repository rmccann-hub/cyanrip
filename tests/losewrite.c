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

/* ONE WRITE TO A FILE THAT FAILS, IN THE MIDDLE.
 *
 * An LD_PRELOAD shim that makes one fwrite() to a named file fail with ENOSPC
 * and write nothing: the first whose text contains a named substring. Every
 * write before and after it goes through, so the file on disk is whole as far
 * as it goes and lacks one message, which is what a disc that filled and then
 * had room again leaves. /dev/full cannot make that state, since there every
 * write fails. Review C item 1.3: a log in that state was signed, so -Y
 * called it valid.
 *
 *   CRIP_LOSE_PATH  the end of the path of the file whose write fails
 *   CRIP_LOSE_ON    a substring of the text whose write fails
 *   CRIP_LOSE_OUT   a file to create when the write is failed, so a test can
 *                   prove the shim fired and the run was not vacuous
 *   CRIP_LOSE_STALE if set, the failed write sets no errno, and every other
 *                   fwrite() and fflush() that succeeds leaves errno at
 *                   ENOENT, as C11 7.5p3 lets a call that succeeds do: a
 *                   reason read from errno without clearing it first is then
 *                   the wrong one
 *
 * cyanrip writes each log message with one fwrite() (src/cyanrip_log.c,
 * crip_log_put()), so fwrite() is the call failed, and fflush() is
 * interposed only to leave errno set. The file is named through
 * /proc/self/fd, which is Linux's, as the shims are.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static atomic_int fired;

static int names_the_file(FILE *f)
{
    const char *want = getenv("CRIP_LOSE_PATH");
    char link[64], path[PATH_MAX];
    int fd = fileno(f);

    if (!want || !*want || fd < 0)
        return 0;
    snprintf(link, sizeof(link), "/proc/self/fd/%d", fd);
    ssize_t n = readlink(link, path, sizeof(path) - 1);
    if (n <= 0)
        return 0;
    path[n] = '\0';

    size_t wl = strlen(want);
    return (size_t)n >= wl && !strcmp(path + n - wl, want);
}

size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream)
{
    static size_t (*real)(const void *, size_t, size_t, FILE *);
    const char *on = getenv("CRIP_LOSE_ON");
    int stale = getenv("CRIP_LOSE_STALE") != NULL;

    if (!real)
        *(void **)&real = dlsym(RTLD_NEXT, "fwrite");

    if (on && *on && size && nmemb && !atomic_load(&fired) &&
        memmem(ptr, size * nmemb, on, strlen(on)) && names_the_file(stream) &&
        !atomic_exchange(&fired, 1)) {
        const char *out = getenv("CRIP_LOSE_OUT");
        if (out) {
            int fd = open(out, O_WRONLY | O_CREAT | O_TRUNC, 0644);
            if (fd >= 0)
                close(fd);
        }
        if (!stale)
            errno = ENOSPC;
        return 0;
    }

    size_t ret = real(ptr, size, nmemb, stream);
    if (stale && ret == nmemb)
        errno = ENOENT;
    return ret;
}

int fflush(FILE *stream)
{
    static int (*real)(FILE *);

    if (!real)
        *(void **)&real = dlsym(RTLD_NEXT, "fflush");

    int ret = real(stream);
    if (!ret && getenv("CRIP_LOSE_STALE"))
        errno = ENOENT;
    return ret;
}
