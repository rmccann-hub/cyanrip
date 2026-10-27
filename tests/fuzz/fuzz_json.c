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

/* The JSON reader on any bytes, read as acoustid.c reads a reply: its
 * status, the count of its submissions and its error's message. The text
 * is copied to a block of exactly its size, with no NUL after it, since the
 * reader's contract is that it reads nothing at or past end. */

#include <string.h>

#include <libavutil/mem.h>

#include "fuzz.h"
#include "json.h"

int LLVMFuzzerInitialize(int *argc, char ***argv)
{
    (void)argc; (void)argv;
    return 0;
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
    char *buf = av_malloc(size ? size : 1);
    if (!buf)
        return 0;
    memcpy(buf, data, size);
    const char *end = buf + size;

    av_free(crip_json_str(crip_json_get(buf, end, "status"), end));
    (void)crip_json_count(crip_json_get(buf, end, "submissions"), end);
    av_free(crip_json_str(crip_json_get(crip_json_get(buf, end, "error"),
                                        end, "message"), end));
    /* And the value at the start, whatever it is */
    av_free(crip_json_str(buf, end));
    (void)crip_json_count(buf, end);

    av_free(buf);
    return 0;
}
