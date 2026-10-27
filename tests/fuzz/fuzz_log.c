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

/* -Y's check of a log on any bytes. cyanrip_verify_log() reads a path, so
 * each input is written to one scratch file, made once in the directory the
 * harness runs in and removed when it exits. */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "fuzz.h"
#include "fun512.h"

static char path[] = "cyanrip-fuzz-log-XXXXXX";

static void remove_scratch(void)
{
    unlink(path);
}

int LLVMFuzzerInitialize(int *argc, char ***argv)
{
    (void)argc; (void)argv;
    int fd = mkstemp(path);
    if (fd < 0) {
        perror("mkstemp");
        abort();
    }
    close(fd);
    atexit(remove_scratch);
    return 0;
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
    FILE *f = fopen(path, "wb");
    if (!f)
        abort();
    if (size && fwrite(data, 1, size, f) != size)
        abort();
    if (fclose(f))
        abort();
    (void)cyanrip_verify_log(path);
    return 0;
}
