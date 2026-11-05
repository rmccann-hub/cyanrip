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

/* `Speed:` and `C2 errors:`, every arm, the drive's among them, which no
 * image reaches: our round 36 lap 12 S11 (a) and (c) and round 37 lap 1 S8,
 * accepted by Platterpus's round 36 lap 13 S5 and round 37 lap 2 S6. */
static void expect_speed(int speed, int is_image, int failed, const char *want)
{
    char buf[64];
    const char *got = crip_speed_text(buf, sizeof(buf), speed, is_image, failed);
    if (strcmp(got, want)) {
        printf("FAIL: speed %i, image %i, failed %i reads \"%s\", want \"%s\"\n",
               speed, is_image, failed, got, want);
        fails++;
    }
}

static void expect_c2(int caps_failed, int c2, const char *want)
{
    const char *got = crip_c2_text(caps_failed, c2);
    if (strcmp(got, want)) {
        printf("FAIL: caps failed %i, C2 %i reads \"%s\", want \"%s\"\n",
               caps_failed, c2, got, want);
        fails++;
    }
}

/* The drive's declarations kept for the record (drive_caps.h): a check
 * of what crip_feature_take() or crip_mode_page_take() kept. */
static void expect_taken(const char *what, int got, const CripDeclared *d,
                         int want, int length, const uint8_t *bytes, int nb)
{
    if (got != want || d->found != want || (want && (d->length != length ||
        d->nb_bytes != nb || memcmp(d->bytes, bytes, nb)))) {
        printf("FAIL: %s: returned %i, found %i, length %i, %i bytes kept; "
               "want %i, length %i, %i bytes\n", what, got, d->found,
               d->length, d->nb_bytes, want, length, nb);
        fails++;
    }
}

int main(void)
{
    uint8_t buf[256];
    size_t len;

    expect_speed(0, 0, 0, "default (drive not asked whether it can change speed)");
    expect_speed(0, 1, 0, "default (drive not asked whether it can change speed)");
    expect_speed(8, 0, 0, "8x");
    expect_speed(8, 0, 1, "default (setting 8x failed)");
    expect_speed(8, 1, 1, "default (disc image, 8x not applied)");
    expect_speed(48, 1, 0, "default (disc image, 48x not applied)");
    expect_c2(0, 1, "supported by drive, not used");
    expect_c2(0, 0, "unsupported by drive");
    /* A failed query's words carry CDIO_DRIVE_CAP_ERROR alone, so the C2
     * bit cannot be set beside it; the failure decides either way */
    expect_c2(1, 0, "unknown (capabilities query failed)");
    expect_c2(1, 1, "unknown (capabilities query failed)");

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

    /* Every value of the `Recordable:` line: the three CD profiles, one
     * that is not a CD's, and the two reasons there is no profile */
    {
        const struct { int profile; const char *want; } rec[] = {
            { 0x0008, "no, CD-ROM (drive's current profile)" },
            { 0x0009, "yes, CD-R (drive's current profile)" },
            { 0x000a, "yes, CD-RW (drive's current profile)" },
            { 0x0010, "unknown (profile 0x0010 is not a CD profile)" },
            { CRIP_PROFILE_UNREADABLE, "unknown (profile not readable)" },
            { CRIP_PROFILE_IMAGE, "unknown (image)" },
        };
        for (size_t i = 0; i < sizeof(rec)/sizeof(*rec); i++) {
            char got[64];
            crip_recordable_text(got, sizeof(got), rec[i].profile);
            if (strcmp(got, rec[i].want)) {
                printf("FAIL: profile %i reads \"%s\", want \"%s\"\n",
                       rec[i].profile, got, rec[i].want);
                fails++;
            }
        }
    }

    /* The current profile comes from the feature header's bytes 6-7. The
     * reply below is shaped as a BD drive lists its profiles, highest first,
     * CD-ROM last and current: libcdio's mmc_get_disctype() stops one
     * descriptor short of the list's end and returns its 0xffff placeholder
     * for it, which is what the rig's BDR-209D printed in round 36's runs.
     * The header says 0x0008 whatever the list holds. */
    {
        const uint16_t listed[] = { 0x0043, 0x0042, 0x0041, 0x0040, 0x0010,
                                    0x000a, 0x0009, 0x0008 };
        const size_t n = sizeof(listed)/sizeof(*listed);
        memset(buf, 0, sizeof(buf));
        const size_t conf_len = 8 + 4 + 4*n;   /* header, feature 0, its list */
        buf[3] = conf_len - 4;
        buf[6] = 0x00;
        buf[7] = 0x08;
        buf[8 + 3] = 4*n;                       /* feature 0's additional length */
        for (size_t i = 0; i < n; i++) {
            buf[12 + 4*i] = listed[i] >> 8;
            buf[12 + 4*i + 1] = listed[i] & 0xff;
            buf[12 + 4*i + 2] = i == n - 1;     /* the current bit */
        }

        /* libcdio's search, as mmc_hl_cmds.c has it at 68ea374, on the same
         * reply: shows the defect the header parse is not subject to */
        int libcdio = 0xffff;
        const uint8_t *p = buf + 8, *q = p + 4;
        while (libcdio == 0xffff && q < p + p[3]) {
            if (q[2] & 0x01)
                libcdio = q[0] << 8 | q[1];
            q += 4;
        }

        const struct { const char *what; int got, want; } prof[] = {
            { "libcdio's search, CD-ROM listed last", libcdio, 0xffff },
            { "header, CD-ROM current", crip_current_profile_parse(buf, conf_len), 0x0008 },
            { "header alone", crip_current_profile_parse(buf, 8), 0x0008 },
            { "reply shorter than the header", crip_current_profile_parse(buf, 7),
              CRIP_PROFILE_UNREADABLE },
            { "NULL reply", crip_current_profile_parse(NULL, 0), CRIP_PROFILE_UNREADABLE },
        };
        for (size_t i = 0; i < sizeof(prof)/sizeof(*prof); i++) {
            if (prof[i].got != prof[i].want) {
                printf("FAIL: %s: profile 0x%04x, want 0x%04x\n", prof[i].what,
                       (unsigned)prof[i].got & 0xffff, (unsigned)prof[i].want & 0xffff);
                fails++;
            }
        }

        /* A header declaring fewer bytes than its own holds no profile */
        buf[3] = 3;
        if (crip_current_profile_parse(buf, conf_len) != CRIP_PROFILE_UNREADABLE) {
            printf("FAIL: a header declaring 3 bytes still gave a profile\n");
            fails++;
        }

        /* A CD-R current, the header's other value */
        buf[3] = conf_len - 4;
        buf[7] = 0x09;
        if (crip_current_profile_parse(buf, conf_len) != 0x0009) {
            printf("FAIL: header naming CD-R did not give 0x0009\n");
            fails++;
        }
    }

    /* No reply at all */
    expect("NULL", crip_accurate_stream_parse(NULL, 0), CRIP_ACCURATE_STREAM_UNREADABLE);
    expect("shorter than the header", crip_accurate_stream_parse(buf, 7),
           CRIP_ACCURATE_STREAM_UNREADABLE);

    /* The CD Read feature, GET CONFIGURATION 001Eh, found by walking the
     * descriptors: 0000h (profile list, 8 bytes), then 001Eh (8 bytes) with
     * DAP and C2 Flags set; the walk must skip the first by its own length */
    {
        uint8_t c[64] = { 0 }, want[8] = { 0x00, 0x1e, 0x09, 0x04, 0x82, 0, 0, 0 };
        CripDeclared d = { 0 };
        c[3] = 8 + 12 + 8 - 4;
        c[7] = 0x08;                         /* current profile: CD-ROM */
        c[8 + 3] = 8;                        /* 0000h, 4 + 8 bytes */
        memcpy(c + 8 + 12, want, sizeof(want));
        expect_taken("feature 001Eh after 0000h",
                     crip_feature_take(c, sizeof(c), CRIP_FEATURE_CD_READ, &d), &d,
                     1, 8, want, 8);
        memset(&d, 0, sizeof(d));
        expect_taken("feature 001Eh beyond the declared length",
                     crip_feature_take(c, 8 + 12 + 4, CRIP_FEATURE_CD_READ, &d), &d,
                     0, 0, NULL, 0);
        memset(&d, 0, sizeof(d));
        c[3] = 8 + 12 - 4;                   /* the header ends before it */
        expect_taken("feature 001Eh past the header's length",
                     crip_feature_take(c, sizeof(c), CRIP_FEATURE_CD_READ, &d), &d,
                     0, 0, NULL, 0);
        memset(&d, 0, sizeof(d));
        expect_taken("no reply", crip_feature_take(NULL, 0, CRIP_FEATURE_CD_READ, &d),
                     &d, 0, 0, NULL, 0);
    }

    /* The whole length each reply declares in its own header, read from the
     * header's own bytes and never from the buffer's size */
    {
        uint8_t r[8] = { 0 };
        const struct { enum CripReplyKind kind; uint8_t b[4]; size_t len, want;
                       const char *what; } lens[] = {
            { CRIP_REPLY_INQUIRY, { 0, 0, 0, 0 }, 8, 5, "INQUIRY, additional length 0" },
            { CRIP_REPLY_INQUIRY, { 0x12, 0x34, 0x56, 0x78 }, 4, 0, "INQUIRY cut before byte 4" },
            { CRIP_REPLY_CONFIGURATION, { 0x00, 0x01, 0x02, 0x03 }, 8, 0x010203 + 4,
              "GET CONFIGURATION, all four length bytes" },
            { CRIP_REPLY_CONFIGURATION, { 0x00, 0x01, 0x02, 0x03 }, 3, 0,
              "GET CONFIGURATION cut before byte 3" },
            { CRIP_REPLY_MODE_SENSE_10, { 0x01, 0x02, 0xff, 0xff }, 8, 0x0102 + 2,
              "MODE SENSE (10), two length bytes only" },
            { CRIP_REPLY_MODE_SENSE_10, { 0x01, 0x02 }, 1, 0,
              "MODE SENSE (10) cut before byte 1" },
        };
        for (size_t k = 0; k < sizeof(lens)/sizeof(*lens); k++) {
            memset(r, 0, sizeof(r));
            memcpy(r, lens[k].b, 4);
            size_t got = crip_reply_length(lens[k].kind, r, lens[k].len);
            if (got != lens[k].want) {
                printf("FAIL: %s: length %zu, want %zu\n", lens[k].what, got, lens[k].want);
                fails++;
            }
        }
        memset(r, 0, sizeof(r));
        r[4] = 91;                           /* additional length: a 96-byte INQUIRY */
        if (crip_reply_length(CRIP_REPLY_INQUIRY, r, 8) != 96) {
            printf("FAIL: INQUIRY of additional length 91 is not 96 bytes long\n");
            fails++;
        }
        if (crip_reply_length(CRIP_REPLY_INQUIRY, NULL, 8) != 0) {
            printf("FAIL: no reply has a length\n");
            fails++;
        }
        if (crip_reply_length(CRIP_REPLY_FIXED, r, 256) != 256) {
            printf("FAIL: a reply with no header is the length asked\n");
            fails++;
        }
    }

    /* --read-vendor-settings: the table row an INQUIRY's vendor names, by
     * exact match on bytes 8 to 15 less their padding, and nothing for any
     * other drive or a reply too short to name one */
    {
        static const uint8_t f4[10] = { 0x3c, 0x02, 0xf4, 0, 0, 0, 0, 0x01, 0, 0 };
        const struct { const char *vendor; size_t len; int match; const char *what; } v[] = {
            { "PIONEER ", 36, 1, "PIONEER, space-padded" },
            { "PIONEER\0", 36, 1, "PIONEER, NUL-padded" },
            { "PIONEER ", 16, 1, "a reply just long enough" },
            { "PIONEER ", 15, 0, "a reply too short to hold the vendor" },
            { "PIONEERX", 36, 0, "a longer vendor that starts the same" },
            { "PIONEE  ", 36, 0, "a shorter vendor" },
            { "pioneer ", 36, 0, "another case" },
            { "PLEXTOR ", 36, 0, "another vendor" },
            { "        ", 36, 0, "no vendor" },
        };
        for (size_t i = 0; i < sizeof(v) / sizeof(v[0]); i++) {
            uint8_t inq[36] = { 0x05, 0x80, 0x00, 0x32, 31 };
            memcpy(inq + 8, v[i].vendor, 8);
            memcpy(inq + 16, "BD-RW   BDR-209D", 16);
            const CripVendorQuery *q = crip_vendor_query_for(inq, v[i].len);
            if (!!q != v[i].match) {
                printf("FAIL: vendor table, %s: %s\n", v[i].what,
                       q ? "a row matched" : "no row matched");
                fails++;
            }
        }
        if (crip_vendor_query_for(NULL, 36)) {
            printf("FAIL: vendor table: no reply matched a row\n");
            fails++;
        }
        uint8_t inq[36] = { 0 };
        memcpy(inq + 8, "PIONEER ", 8);
        const CripVendorQuery *q = crip_vendor_query_for(inq, sizeof(inq));
        if (!q || strcmp(q->id, "pioneer-f4") || memcmp(q->cdb, f4, sizeof(f4)) ||
            q->alloc != 256 || !strstr(q->source, "pioneer-optical@d2cbbf2")) {
            printf("FAIL: Pioneer's row is not READ BUFFER mode 02h buffer F4h for 256 bytes, cited\n");
            fails++;
        }
        if (q && q->cdb[0] != 0x3c) {
            printf("FAIL: Pioneer's row is not a READ BUFFER\n");
            fails++;
        }
    }

    /* Pioneer's settings block, decoded as pioneer-optical decodes it: the
     * shape check first, then byte 9's support, then bytes 4 and 5's mode
     * only where supported */
    {
        const struct { int b0, b1, tail_ff, b4, b5, b9; size_t len; int valid;
                       enum CripTriState sup; const char *mode; const char *what; } c[] = {
            { 1, 0, 1, 1, 8,   1, 256, 1, CRIP_YES, "master", "Master" },
            { 1, 0, 1, 0, 0,   1, 256, 1, CRIP_YES, "standard", "Standard" },
            { 1, 0, 1, 0, 77,  1, 256, 1, CRIP_YES, "standard", "Standard, byte 5 not read" },
            { 1, 0, 1, 1, 254, 1, 256, 1, CRIP_YES, "perfect", "Perfect" },
            { 1, 0, 1, 1, 7,   1, 256, 1, CRIP_YES, NULL, "an unknown level" },
            { 1, 0, 1, 255, 0, 1, 256, 1, CRIP_YES, NULL, "mode not reported" },
            { 1, 0, 1, 2, 8,   1, 256, 1, CRIP_YES, NULL, "an unknown mode byte" },
            { 1, 0, 1, 1, 8,   0, 256, 1, CRIP_NO, NULL, "unsupported, mode not read" },
            { 1, 0, 1, 1, 8,   2, 256, 1, CRIP_UNDETERMINED, NULL, "support byte 2" },
            { 1, 0, 1, 1, 8, 255, 256, 1, CRIP_UNDETERMINED, NULL, "support byte FFh" },
            { 255, 255, 0, 1, 8, 1, 256, 1, CRIP_YES, "master", "the sentinel prefix" },
            { 0, 1, 1, 1, 8,   1, 256, 1, CRIP_YES, "master", "feature flags 0 and 1" },
            { 1, 0, 0, 1, 8,   1, 256, 0, CRIP_UNDETERMINED, NULL, "bytes 11 to 14 not FFh" },
            { 2, 0, 1, 1, 8,   1, 256, 0, CRIP_UNDETERMINED, NULL, "byte 0 not a flag" },
            { 1, 3, 1, 1, 8,   1, 256, 0, CRIP_UNDETERMINED, NULL, "byte 1 not a flag" },
            { 1, 0, 1, 1, 8,   1, 255, 0, CRIP_UNDETERMINED, NULL, "a block one byte short" },
            { 0, 0, 0, 0, 0,   0, 256, 0, CRIP_UNDETERMINED, NULL, "a zero-filled buffer" },
        };
        for (size_t i = 0; i < sizeof(c) / sizeof(c[0]); i++) {
            uint8_t b[256];
            memset(b, 0x5a, sizeof(b));
            if (!strcmp(c[i].what, "a zero-filled buffer"))
                memset(b, 0, sizeof(b));
            b[0] = c[i].b0; b[1] = c[i].b1;
            if (c[i].tail_ff)
                memset(b + 11, 0xff, 4);
            b[4] = c[i].b4; b[5] = c[i].b5; b[9] = c[i].b9;
            CripPureRead p;
            crip_pioneer_f4_decode(b, c[i].len, &p);
            const int mode_ok = c[i].mode ? p.mode && !strcmp(p.mode, c[i].mode) : !p.mode;
            if (p.block_valid != c[i].valid || p.supported != c[i].sup || !mode_ok) {
                printf("FAIL: F4h block, %s: valid %i support %i mode %s\n", c[i].what,
                       p.block_valid, (int)p.supported, p.mode ? p.mode : "(none)");
                fails++;
            }
        }
        uint8_t one[256];
        memset(one, 0x5a, sizeof(one));
        one[0] = 1; one[1] = 0; one[4] = 1; one[5] = 8; one[9] = 1;
        for (int k = 11; k <= 14; k++) {
            memset(one + 11, 0xff, 4);
            one[k] = 0x5a;
            CripPureRead p1;
            crip_pioneer_f4_decode(one, sizeof(one), &p1);
            if (p1.block_valid) {
                printf("FAIL: F4h block, byte %i alone not FFh: read as state\n", k);
                fails++;
            }
        }
        uint8_t ff[256];
        memset(ff, 0xff, sizeof(ff));
        CripPureRead p;
        crip_pioneer_f4_decode(ff, sizeof(ff), &p);
        if (p.block_valid || p.supported != CRIP_UNDETERMINED || p.mode) {
            printf("FAIL: F4h block, every byte FFh: read as state\n");
            fails++;
        }
        crip_pioneer_f4_decode(NULL, 256, &p);
        if (p.block_valid || p.supported != CRIP_UNDETERMINED || p.mode) {
            printf("FAIL: F4h block, no reply: read as state\n");
            fails++;
        }
    }

    if (fails)
        printf("%i check(s) failed\n", fails);
    else
        printf("accurate stream, recordable, the declarations kept and the vendor table: every wording and parse pinned\n");
    return !!fails;
}
