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

#include <stdio.h>

#include "drive_caps.h"

#define MODE_HEADER_10   8    /* MODE SENSE (10) parameter header */
#define CAPS_PAGE        0x2a
#define CAPS_STREAM_BYTE 5    /* byte 5 of page 2Ah... */
#define CAPS_STREAM_BIT  0x02 /* ...bit 1, CD-DA Stream is Accurate */

enum CripAccurateStream crip_accurate_stream_parse(const uint8_t *buf, size_t len)
{
    if (!buf || len < MODE_HEADER_10)
        return CRIP_ACCURATE_STREAM_UNREADABLE;

    /* Bytes 0-1 are the length of what follows them; a reply can be cut
     * short by the allocation length, so read no further than either. */
    size_t data = ((size_t)buf[0] << 8 | buf[1]) + 2;
    if (data < len)
        len = data;

    /* Bytes 6-7 are the length of the block descriptors before the pages.
     * Drives send none for page 2Ah, but a reply that declares some is read
     * past them rather than taken as a page. */
    size_t off = MODE_HEADER_10 + ((size_t)buf[6] << 8 | buf[7]);

    while (off + 2 <= len) {
        const uint8_t code = buf[off] & 0x3f;
        const size_t plen = buf[off + 1];
        if (code == CAPS_PAGE) {
            if (plen < CAPS_STREAM_BYTE - 1 || off + CAPS_STREAM_BYTE >= len)
                return CRIP_ACCURATE_STREAM_UNREADABLE;
            return (buf[off + CAPS_STREAM_BYTE] & CAPS_STREAM_BIT) ?
                   CRIP_ACCURATE_STREAM_SUPPORTED : CRIP_ACCURATE_STREAM_UNSUPPORTED;
        }
        off += plen + 2;
    }

    return CRIP_ACCURATE_STREAM_UNREADABLE;
}

const char *crip_recordable_text(char *buf, size_t size, int profile)
{
    switch (profile) {
    case CRIP_PROFILE_IMAGE:
        snprintf(buf, size, "unknown (image)");
        break;
    case CRIP_PROFILE_UNREADABLE:
        snprintf(buf, size, "unknown (profile not readable)");
        break;
    case 0x0008:
        snprintf(buf, size, "no, CD-ROM (drive's current profile)");
        break;
    case 0x0009:
        snprintf(buf, size, "yes, CD-R (drive's current profile)");
        break;
    case 0x000a:
        snprintf(buf, size, "yes, CD-RW (drive's current profile)");
        break;
    default:
        snprintf(buf, size, "unknown (profile 0x%04x is not a CD profile)",
                 (unsigned)profile & 0xffff);
        break;
    }
    return buf;
}

const char *crip_accurate_stream_text(enum CripAccurateStream s)
{
    switch (s) {
    case CRIP_ACCURATE_STREAM_SUPPORTED:
        return "declared supported by drive (capabilities page, not measured)";
    case CRIP_ACCURATE_STREAM_UNSUPPORTED:
        return "declared unsupported by drive";
    case CRIP_ACCURATE_STREAM_IMAGE:
        return "unknown (image)";
    case CRIP_ACCURATE_STREAM_UNREADABLE:
        break;
    }
    return "unknown (capabilities page not readable)";
}
