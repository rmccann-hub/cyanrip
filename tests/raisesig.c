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

/* A SIGNAL AT A NAMED MOMENT, WITHOUT A CLOCK.
 *
 * An LD_PRELOAD shim that raises SIGTERM once, straight after a named line is
 * written to stdout. A test that sends a signal on a timer lands wherever the
 * rip happens to be, which is how the interrupted sample's freshness check
 * failed three times and passed on every re-run: the stop marker was printed
 * only when the signal landed inside the frame loop. The window it missed --
 * after a pass's last frame, before the track's read is finished -- has no
 * library call a shim could key on, but it does print one console line,
 * `Flushing encoders...`, so this raises the signal there, every time.
 *
 *   CRIP_RAISE_ON   a substring of the stdout format string to raise after
 *   CRIP_RAISE_OUT  a file to create when the signal is raised, so a test can
 *                   prove the shim fired and the run was not vacuous
 *
 * cyanrip formats each message once and writes the escaped text to stdout
 * with fwrite() (src/log_escape.c), so fwrite() is interposed and the text it
 * writes is matched. Until then it wrote with vprintf(), which the -O2 build
 * turns into __vfprintf_chk(stdout, ...), and those three spellings are still
 * interposed for a library that prints for itself; there the format string is
 * matched. Only writes to stdout are.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int fired;

static void raise_now(void)
{
    const char *out = getenv("CRIP_RAISE_OUT");

    fired = 1;
    if (out) {
        int fd = open(out, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd >= 0) {
            if (write(fd, "raised\n", 7) < 0) {
                /* the marker is evidence, not a requirement */
            }
            close(fd);
        }
    }
    raise(SIGTERM);
}

static void maybe_raise(FILE *f, const char *format)
{
    const char *want = getenv("CRIP_RAISE_ON");

    if (fired || f != stdout || !want || !format || !strstr(format, want))
        return;
    raise_now();
}

size_t fwrite(const void *ptr, size_t size, size_t n, FILE *f)
{
    static size_t (*real)(const void *, size_t, size_t, FILE *);
    if (!real)
        real = dlsym(RTLD_NEXT, "fwrite");
    const size_t ret = real(ptr, size, n, f);

    const char *want = getenv("CRIP_RAISE_ON");
    if (!fired && f == stdout && want && *want && size && n &&
        memmem(ptr, size * n, want, strlen(want)))
        raise_now();
    return ret;
}

int __vfprintf_chk(FILE *f, int flag, const char *format, va_list ap)
{
    static int (*real)(FILE *, int, const char *, va_list);
    int ret;
    if (!real)
        real = dlsym(RTLD_NEXT, "__vfprintf_chk");
    ret = real(f, flag, format, ap);
    maybe_raise(f, format);
    return ret;
}

int vfprintf(FILE *f, const char *format, va_list ap)
{
    static int (*real)(FILE *, const char *, va_list);
    int ret;
    if (!real)
        real = dlsym(RTLD_NEXT, "vfprintf");
    ret = real(f, format, ap);
    maybe_raise(f, format);
    return ret;
}

int vprintf(const char *format, va_list ap)
{
    return vfprintf(stdout, format, ap);
}
