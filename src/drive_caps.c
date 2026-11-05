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
#include <string.h>

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

#define CONF_HEADER 8 /* GET CONFIGURATION's feature header */

int crip_current_profile_parse(const uint8_t *buf, size_t len)
{
    if (!buf || len < CONF_HEADER)
        return CRIP_PROFILE_UNREADABLE;

    /* Bytes 0-3 are the length of what follows them; a header that declares
     * less than its own last four bytes holds no current profile. */
    const uint32_t data = (uint32_t)buf[0] << 24 | (uint32_t)buf[1] << 16 |
                          (uint32_t)buf[2] << 8 | buf[3];
    if (data < CONF_HEADER - 4)
        return CRIP_PROFILE_UNREADABLE;

    return buf[6] << 8 | buf[7];
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

const char *crip_speed_text(char *buf, size_t size, int speed, int is_image,
                            int failed)
{
    if (!speed)
        snprintf(buf, size, "default (drive not asked whether it can change speed)");
    else if (is_image)
        snprintf(buf, size, "default (disc image, %ix not applied)", speed);
    else if (failed)
        snprintf(buf, size, "default (setting %ix failed)", speed);
    else
        snprintf(buf, size, "%ix", speed);
    return buf;
}

const char *crip_c2_text(int caps_failed, int c2)
{
    if (caps_failed)
        return "unknown (capabilities query failed)";
    return c2 ? "supported by drive, not used" : "unsupported by drive";
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

size_t crip_reply_length(enum CripReplyKind kind, const uint8_t *buf, size_t len)
{
    if (!buf)
        return 0;
    switch (kind) {
    case CRIP_REPLY_INQUIRY:
        return len >= 5 ? (size_t)buf[4] + 5 : 0;
    case CRIP_REPLY_CONFIGURATION:
        return len >= 4 ? ((size_t)buf[0] << 24 | (size_t)buf[1] << 16 |
                           (size_t)buf[2] << 8 | buf[3]) + 4 : 0;
    case CRIP_REPLY_MODE_SENSE_10:
        return len >= 2 ? ((size_t)buf[0] << 8 | buf[1]) + 2 : 0;
    case CRIP_REPLY_FIXED:
        return len;
    }
    return 0;
}

int crip_feature_take(const uint8_t *buf, size_t len, unsigned code,
                      CripDeclared *out)
{
    if (!buf || len < CONF_HEADER)
        return 0;

    /* Read no further than the reply declares, or than was returned. */
    const size_t data = crip_reply_length(CRIP_REPLY_CONFIGURATION, buf, len);
    if (data < len)
        len = data;

    for (size_t off = CONF_HEADER; off + 4 <= len;) {
        const size_t whole = 4 + (size_t)buf[off + 3];
        if (off + whole > len)
            return 0;
        if (((unsigned)buf[off] << 8 | buf[off + 1]) == code) {
            out->found = 1;
            out->length = (int)whole;
            out->nb_bytes = (int)(whole < CRIP_DECLARED_MAX ? whole : CRIP_DECLARED_MAX);
            memcpy(out->bytes, buf + off, out->nb_bytes);
            return 1;
        }
        off += whole;
    }
    return 0;
}

/* The table. One row so far; a row is added only with its source, and only
 * for a command that reads. */
static const CripVendorQuery vendor_queries[] = {
    {
        .id     = "pioneer-f4",
        .vendor = "PIONEER",
        .source = "pioneer-optical@d2cbbf2:src/settings/f4.rs:92-94 "
                  "(READ BUFFER, mode 02h, buffer F4h, 256 bytes)",
        .cdb    = { 0x3c, 0x02, 0xf4, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00 },
        .alloc  = 256,
    },
};

const CripVendorQuery *crip_vendor_query_for(const uint8_t *inquiry, size_t len)
{
    /* INQUIRY's vendor identification is bytes 8 to 15, ASCII, padded with
     * spaces (SPC-4 6.4.2). A reply too short to hold it matches nothing. */
    if (!inquiry || len < 16)
        return NULL;
    size_t n = 8;
    while (n && (inquiry[8 + n - 1] == ' ' || inquiry[8 + n - 1] == '\0'))
        n--;
    for (size_t i = 0; i < sizeof(vendor_queries) / sizeof(vendor_queries[0]); i++) {
        const CripVendorQuery *q = &vendor_queries[i];
        if (strlen(q->vendor) == n && !memcmp(q->vendor, inquiry + 8, n))
            return q;
    }
    return NULL;
}

void crip_pioneer_f4_decode(const uint8_t *buf, size_t len, CripPureRead *out)
{
    memset(out, 0, sizeof(*out));
    if (!buf || len < 256)
        return;

    int all_ff = 1;
    for (int i = 0; i < 256; i++)
        all_ff &= buf[i] == 0xff;
    const int sentinel = buf[0] == 0xff && buf[1] == 0xff;
    const int feature = (buf[0] <= 1 || buf[0] == 0xff) &&
                        (buf[1] <= 1 || buf[1] == 0xff) &&
                        buf[11] == 0xff && buf[12] == 0xff &&
                        buf[13] == 0xff && buf[14] == 0xff;
    if ((!sentinel && !feature) || all_ff)
        return;
    out->block_valid = 1;

    out->supported = buf[9] == 1 ? CRIP_YES : buf[9] == 0 ? CRIP_NO
                                                          : CRIP_UNDETERMINED;
    if (out->supported != CRIP_YES)
        return;
    if (buf[4] == 0)
        out->mode = "standard";
    else if (buf[4] == 1 && buf[5] == 8)
        out->mode = "master";
    else if (buf[4] == 1 && buf[5] == 254)
        out->mode = "perfect";
}
