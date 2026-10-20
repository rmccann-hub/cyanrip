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

/* Every value of the `Accurate stream:` line, and the parse of page 2Ah that
 * decides it. The read is a MODE SENSE (10) only a drive answers, so its
 * replies are built here byte by byte; the image arm is pinned by the
 * golden reference, which every image rip writes. */

#include <stdio.h>
#include <string.h>

#include "drive_caps.h"

static int fails = 0;

/* A MODE SENSE (10) reply: the 8-byte header with `bdlen` bytes of block
 * descriptors, then page 2Ah with `plen` bytes after its first two, byte 5
 * set to `byte5`. Returns the reply's length. */
static size_t reply(uint8_t *buf, size_t size, int bdlen, int plen, uint8_t byte5)
{
    memset(buf, 0, size);
    size_t page = 8 + bdlen;
    size_t len = page + 2 + plen;
    buf[0] = (len - 2) >> 8;
    buf[1] = (len - 2) & 0xff;
    buf[6] = bdlen >> 8;
    buf[7] = bdlen & 0xff;
    buf[page] = 0x2a;
    buf[page + 1] = plen;
    if (plen >= 4)
        buf[page + 5] = byte5;
    return len;
}

static void expect(const char *what, enum CripAccurateStream got,
                   enum CripAccurateStream want)
{
    if (got != want) {
        printf("FAIL: %s: got \"%s\", want \"%s\"\n", what,
               crip_accurate_stream_text(got), crip_accurate_stream_text(want));
        fails++;
    }
}

static void expect_text(enum CripAccurateStream s, const char *want)
{
    if (strcmp(crip_accurate_stream_text(s), want)) {
        printf("FAIL: value %i reads \"%s\", want \"%s\"\n", (int)s,
               crip_accurate_stream_text(s), want);
        fails++;
    }
}

int main(void)
{
    uint8_t buf[256];
    size_t len;

    /* The four wordings, as round 32 lap 1 S19 proposed them */
    expect_text(CRIP_ACCURATE_STREAM_SUPPORTED,
                "declared supported by drive (capabilities page, not measured)");
    expect_text(CRIP_ACCURATE_STREAM_UNSUPPORTED, "declared unsupported by drive");
    expect_text(CRIP_ACCURATE_STREAM_UNREADABLE,
                "unknown (capabilities page not readable)");
    expect_text(CRIP_ACCURATE_STREAM_IMAGE, "unknown (image)");

    /* Byte 5 bit 1 alone decides it: every other bit of byte 5 is set in
     * the clear case, so a test of the wrong bit cannot pass */
    len = reply(buf, sizeof(buf), 0, 20, 0x02);
    expect("bit 1 set", crip_accurate_stream_parse(buf, len),
           CRIP_ACCURATE_STREAM_SUPPORTED);
    len = reply(buf, sizeof(buf), 0, 20, 0xfd);
    expect("bit 1 clear, the rest set", crip_accurate_stream_parse(buf, len),
           CRIP_ACCURATE_STREAM_UNSUPPORTED);

    /* The page code's top two bits are flags, not part of the code */
    len = reply(buf, sizeof(buf), 0, 20, 0x02);
    buf[8] |= 0x80;
    expect("PS bit set on the page code", crip_accurate_stream_parse(buf, len),
           CRIP_ACCURATE_STREAM_SUPPORTED);

    /* Block descriptors before the page are skipped, not read as a page: an
     * 8-byte descriptor whose first byte is 0x2a and whose sixth has bit 1
     * clear would read as an unsupported page */
    len = reply(buf, sizeof(buf), 8, 20, 0x02);
    buf[8] = 0x2a;
    buf[9] = 6;
    buf[13] = 0x00;
    expect("block descriptors skipped", crip_accurate_stream_parse(buf, len),
           CRIP_ACCURATE_STREAM_SUPPORTED);

    /* Page 2Ah after another page is found by walking the page lengths */
    memset(buf, 0, sizeof(buf));
    buf[8] = 0x01;            /* page 01h, 10 bytes */
    buf[9] = 10;
    buf[20] = 0x2a;           /* then page 2Ah */
    buf[21] = 20;
    buf[25] = 0x02;
    len = 20 + 2 + 20;
    buf[0] = (len - 2) >> 8;
    buf[1] = (len - 2) & 0xff;
    expect("page 2Ah after page 01h", crip_accurate_stream_parse(buf, len),
           CRIP_ACCURATE_STREAM_SUPPORTED);

    /* A reply with no page 2Ah: unknown, never unsupported */
    memset(buf, 0, sizeof(buf));
    buf[8] = 0x01;
    buf[9] = 10;
    len = 8 + 2 + 10;
    buf[1] = len - 2;
    expect("no page 2Ah", crip_accurate_stream_parse(buf, len),
           CRIP_ACCURATE_STREAM_UNREADABLE);

    /* A page too short to hold byte 5, and a reply cut off before it */
    len = reply(buf, sizeof(buf), 0, 3, 0x02);
    expect("page 2Ah of 3 bytes", crip_accurate_stream_parse(buf, len),
           CRIP_ACCURATE_STREAM_UNREADABLE);
    len = reply(buf, sizeof(buf), 0, 20, 0x02);
    expect("reply cut before byte 5", crip_accurate_stream_parse(buf, 8 + 5),
           CRIP_ACCURATE_STREAM_UNREADABLE);
    expect("reply holding byte 5 exactly", crip_accurate_stream_parse(buf, 8 + 6),
           CRIP_ACCURATE_STREAM_SUPPORTED);

    /* The header's own length bounds the read, even in a larger buffer: a
     * 2Ah page beyond it is not part of the reply */
    memset(buf, 0, sizeof(buf));
    buf[1] = 6;               /* the header and nothing else */
    buf[8] = 0x2a;
    buf[9] = 20;
    buf[13] = 0x02;
    expect("page beyond the declared length", crip_accurate_stream_parse(buf, sizeof(buf)),
           CRIP_ACCURATE_STREAM_UNREADABLE);

    /* No reply at all */
    expect("NULL", crip_accurate_stream_parse(NULL, 0), CRIP_ACCURATE_STREAM_UNREADABLE);
    expect("shorter than the header", crip_accurate_stream_parse(buf, 7),
           CRIP_ACCURATE_STREAM_UNREADABLE);

    if (fails)
        printf("%i check(s) failed\n", fails);
    else
        printf("accurate stream: every wording and parse pinned\n");
    return !!fails;
}
