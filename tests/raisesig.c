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
 * cyanrip writes stdout with vprintf(), which the project's -O2 build turns
 * into __vfprintf_chk(stdout, ...), so all three spellings are interposed and
 * only writes to stdout are matched.
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

static void maybe_raise(FILE *f, const char *format)
{
    const char *want = getenv("CRIP_RAISE_ON");
    const char *out = getenv("CRIP_RAISE_OUT");

    if (fired || f != stdout || !want || !format || !strstr(format, want))
        return;
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
