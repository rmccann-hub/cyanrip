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

/* Q sub-channel decoding tests.
 *
 * These cover the one part of pregap detection a disc image can never reach:
 * images resolve pregaps straight from the TOC, so the sub-channel search,
 * its CRC validation, and the raw-binary drive workaround are dead code under
 * tests/rip_images.py no matter how many fixtures it rips. Everything below
 * runs on synthetic sectors and needs neither a drive nor a disc.
 *
 * The functions under test are static, so this includes the translation unit
 * rather than linking it. Nothing here calls the I/O paths. */
#include "pregap.c"

#include <stdio.h>
#include <string.h>

static int failures;

#define CHECK(cond, ...)                                                      \
    do {                                                                      \
        if (!(cond)) {                                                        \
            failures++;                                                       \
            fprintf(stderr, "FAIL %s:%d: ", __func__, __LINE__);              \
            fprintf(stderr, __VA_ARGS__);                                     \
            fprintf(stderr, "\n");                                            \
        }                                                                     \
    } while (0)

/* A spec-compliant Mode-1 Q sub-channel sector: adr 1, track 12, index 1,
 * relative 12:34:56, absolute 13:45:67, every numeric field BCD-encoded. The
 * CRC was computed independently (CRC-16/GSM: poly 0x1021, init 0x0000,
 * xorout 0xFFFF, unreflected, over the first 10 bytes), not by this code, so
 * it pins the polynomial rather than merely agreeing with itself. */
static const uint8_t sector_bcd[12] = {
    0x01, 0x12, 0x01, 0x12, 0x34, 0x56, 0x00, 0x13, 0x45, 0x67, 0x10, 0xB9,
};

/* The same sector as firmware that ignores the BCD requirement returns it:
 * identical CRC bytes (the CRC lives on the disc and is not recomputed by the
 * drive), but the numeric fields carry raw binary. */
static const uint8_t sector_binary[12] = {
    0x01, 0x0C, 0x01, 0x0C, 0x22, 0x38, 0x00, 0x0D, 0x2D, 0x43, 0x10, 0xB9,
};

static void test_crc(void)
{
    CHECK(crc_subq(sector_bcd) == 0x10B9,
          "crc_subq(BCD sector) = 0x%04X, wanted 0x10B9", crc_subq(sector_bcd));

    /* The whole reason the workaround exists: the binary form does not check
     * out against the CRC the disc carries. */
    CHECK(crc_subq(sector_binary) != 0x10B9,
          "binary-form sector must not validate against the on-disc CRC");
}

static void test_bcd_conversion(void)
{
    CHECK(bcd_to_bin(0x00) == 0,  "bcd_to_bin(0x00) = %u", bcd_to_bin(0x00));
    CHECK(bcd_to_bin(0x12) == 12, "bcd_to_bin(0x12) = %u", bcd_to_bin(0x12));
    CHECK(bcd_to_bin(0x99) == 99, "bcd_to_bin(0x99) = %u", bcd_to_bin(0x99));

    /* MMC-3 4.1.3.2.1: values from 0xA0 up are illegal BCD and pass through
     * untouched rather than being converted. */
    CHECK(subq_bcd_to_bin(0x99) == 99,   "subq_bcd_to_bin(0x99) = %u", subq_bcd_to_bin(0x99));
    CHECK(subq_bcd_to_bin(0xA0) == 0xA0, "subq_bcd_to_bin(0xA0) = %u", subq_bcd_to_bin(0xA0));
    CHECK(subq_bcd_to_bin(0xFF) == 0xFF, "subq_bcd_to_bin(0xFF) = %u", subq_bcd_to_bin(0xFF));
}

static void test_verify_compliant_drive(void)
{
    uint8_t buf[12];
    int fixup = 0;

    memcpy(buf, sector_bcd, sizeof(buf));
    CHECK(verify_subq_crc(buf, &fixup) == 1, "spec-compliant sector rejected");
    CHECK(fixup == 0, "compliant sector wrongly flagged as needing the fixup");
    CHECK(!memcmp(buf, sector_bcd, sizeof(buf)),
          "compliant sector must not be rewritten");
}

static void test_verify_binary_drive(void)
{
    uint8_t buf[12];
    int fixup = 0;

    /* Without the workaround this sector is indistinguishable from corruption,
     * and detection can only ever report "unknown (CRC mismatches)". */
    memcpy(buf, sector_binary, sizeof(buf));
    CHECK(verify_subq_crc(buf, &fixup) == 1, "raw-binary sector not recovered");
    CHECK(fixup == 1, "raw-binary sector did not set the sticky fixup flag");

    /* Recovery must leave the buffer in the encoding decode_subq() expects. */
    CHECK(!memcmp(buf, sector_bcd, sizeof(buf)),
          "recovered sector was not re-encoded to BCD");

    subq_t subq;
    decode_subq(&subq, buf);
    CHECK(subq.adr == 1,           "adr = %u",          subq.adr);
    CHECK(subq.track_number == 12, "track_number = %u", subq.track_number);
    CHECK(subq.index_number == 1,  "index_number = %u", subq.index_number);
    CHECK(subq.min == 12,          "min = %u",          subq.min);
    CHECK(subq.sec == 34,          "sec = %u",          subq.sec);
    CHECK(subq.frame == 56,        "frame = %u",        subq.frame);
    CHECK(subq.amin == 13,         "amin = %u",         subq.amin);
    CHECK(subq.asec == 45,         "asec = %u",         subq.asec);
    CHECK(subq.aframe == 67,       "aframe = %u",       subq.aframe);

    /* Once detected the flag is sticky, so later sectors take the fixup path
     * directly instead of paying for the detection retry every time. */
    memcpy(buf, sector_binary, sizeof(buf));
    CHECK(verify_subq_crc(buf, &fixup) == 1,
          "sticky fixup did not validate a later binary sector");
    CHECK(!memcmp(buf, sector_bcd, sizeof(buf)),
          "sticky fixup did not re-encode a later binary sector");
}

static void test_verify_rejects(void)
{
    uint8_t buf[12];
    int fixup = 0;

    /* A drive that returns no Q sub-channel data at all leaves zeroes. That is
     * an absence of data, not a sector that happens to check out. */
    memset(buf, 0, sizeof(buf));
    CHECK(verify_subq_crc(buf, &fixup) == 0, "all-zero sector accepted");
    CHECK(fixup == 0, "all-zero sector set the fixup flag");

    /* Genuine corruption stays rejected -- the workaround must not turn a bad
     * sector into a good one. */
    memcpy(buf, sector_bcd, sizeof(buf));
    buf[4] ^= 0xFF;
    CHECK(verify_subq_crc(buf, &fixup) == 0, "corrupt sector accepted");
    CHECK(fixup == 0, "corrupt sector set the fixup flag");

    /* A wrong CRC with otherwise sane fields must also be rejected. */
    memcpy(buf, sector_bcd, sizeof(buf));
    buf[11] ^= 0x01;
    CHECK(verify_subq_crc(buf, &fixup) == 0, "sector with bad CRC accepted");
}

/* Round 8, 2026-08-13. Neither cdio_get_track_lsn() return value was checked
 * before the pregap search used them in arithmetic. CDIO_INVALID_LSN is a
 * sentinel, not a sector, and a pregap LSN computed from one is a number that
 * was never measured. Unreachable from any fixture -- it needs a live libcdio
 * handle whose track lookup fails -- so the decision is tested here instead. */
static void test_track_lsns_usable(void)
{
    CHECK(track_lsns_usable(0, 0) == 1, "two valid LSNs rejected");
    CHECK(track_lsns_usable(150, 32000) == 1, "two valid LSNs rejected");
    CHECK(track_lsns_usable(CDIO_INVALID_LSN, 32000) == 0,
          "invalid current-track LSN accepted");
    CHECK(track_lsns_usable(150, CDIO_INVALID_LSN) == 0,
          "invalid previous-track LSN accepted");
    CHECK(track_lsns_usable(CDIO_INVALID_LSN, CDIO_INVALID_LSN) == 0,
          "two invalid LSNs accepted");
}

/* A drive of the test's own making, for the search itself. The disc has the
 * track before the one searched, from prev_start, this track's pregap from
 * pregap, and its INDEX 01 at start, so the right answer is always pregap.
 * Frames more than 300 sectors before prev_start belong to the track before
 * that, and one sector's frame can be mode 3 (an ISRC), which names no
 * track. What varies is which sector's frame answers a request, the case the
 * search could not tell before 2026-10-21 (subchannel-pregap-varies). */
struct fake_disc {
    track_t track;
    lsn_t prev_start;
    lsn_t pregap;
    lsn_t start;
    lsn_t mode3;
};

enum fake_answer {
    FAKE_ALIGNED,   /* every frame is the sector asked for */
    FAKE_SHIFTED,   /* every frame is `shift` sectors from the one asked for */
    FAKE_FLAKY,     /* one read in `every`, from `phase`, answers `shift` off */
    FAKE_STALE,     /* read number `stale_read` answers with `stale`'s frame */
};

struct fake_drive {
    struct fake_disc disc;
    enum fake_answer answer;
    int shift;
    int every;
    int phase;
    int stale_read;
    lsn_t stale;
    /* Frames of sectors bad_from..bad_to fail their CRC on their first
     * bad_reads reads; a negative bad_reads fails every read. */
    lsn_t bad_from;
    lsn_t bad_to;
    int bad_reads;
    int bad_seen[64];
    int read_fails;
    int reads;
    lsn_t lowest_ask;
    lsn_t highest_ask;
};

static uint8_t to_bcd(int v)
{
    return (uint8_t)(((v / 10) << 4) | (v % 10));
}

static void fake_frame(const struct fake_disc *disc, lsn_t at, uint8_t *q)
{
    const int addr = at + CDIO_PREGAP_SECTORS;

    memset(q, 0, 16);
    if (at == disc->mode3) {
        q[0] = 0x03;
        for (int i = 1; i < 9; i++)
            q[i] = 0x40 + i;
    } else {
        const int in_pregap = at >= disc->pregap && at < disc->start;
        track_t t = disc->track;
        lsn_t from = disc->start;
        if (at < disc->prev_start - 300) {
            t = disc->track - 2;
            from = disc->prev_start - 2000;
        } else if (at < disc->pregap) {
            t = disc->track - 1;
            from = disc->prev_start;
        }
        int rel = in_pregap ? disc->start - at : at - from;
        if (rel < 0)
            rel = -rel;
        q[0] = 0x01;
        q[1] = to_bcd(t);
        q[2] = to_bcd(in_pregap ? 0 : 1);
        q[3] = to_bcd(rel / 4500);
        q[4] = to_bcd((rel / 75) % 60);
        q[5] = to_bcd(rel % 75);
        q[7] = to_bcd(addr / 4500);
        q[8] = to_bcd((addr / 75) % 60);
    }
    q[9] = to_bcd(addr % 75);

    const unsigned crc = crc_subq(q);
    q[10] = crc >> 8;
    q[11] = crc & 0xFF;
}

static driver_return_code_t fake_read(void *opaque, uint8_t *audio_subq_buf, lsn_t ask)
{
    struct fake_drive *d = opaque;

    d->reads++;
    if (ask < d->lowest_ask)
        d->lowest_ask = ask;
    if (ask > d->highest_ask)
        d->highest_ask = ask;
    if (d->read_fails)
        return DRIVER_OP_ERROR;

    lsn_t at = ask;
    if (d->answer == FAKE_SHIFTED)
        at = ask + d->shift;
    else if (d->answer == FAKE_FLAKY && d->reads % d->every == d->phase)
        at = ask + d->shift;
    else if (d->answer == FAKE_STALE && d->reads == d->stale_read)
        at = d->stale;

    uint8_t *q = audio_subq_buf + CDIO_CD_FRAMESIZE_RAW;
    fake_frame(&d->disc, at, q);
    if (at >= d->bad_from && at <= d->bad_to &&
        (d->bad_reads < 0 || d->bad_seen[at - d->bad_from]++ < d->bad_reads))
        q[10] ^= 0x55;

    return DRIVER_OP_SUCCESS;
}

/* Track 9 of the reference disc, whose pregap read 94 frames in 46 filed rips
 * and 95 in 5: track 8 starts at 145662 - 16905 = 128757. */
static struct fake_drive fake_track9(void)
{
    struct fake_drive d = {
        .disc = { .track = 9, .prev_start = 128757, .pregap = 145568,
                  .start = 145662, .mode3 = -1 },
        .answer = FAKE_ALIGNED,
        .bad_from = 1,
        .bad_to = 0,
        .lowest_ask = 1 << 30,
        .highest_ask = -(1 << 30),
    };
    return d;
}

static lsn_t fake_search(struct fake_drive *d, enum cyanrip_pregap_source *src)
{
    return pregap_search_subq(fake_read, d, d->disc.track, d->disc.prev_start,
                              d->disc.start, src);
}

static void test_search_aligned(void)
{
    static const int lengths[] = { 0, 1, 2, 94, 95, 149, 150, 151, 158, 300 };
    for (size_t i = 0; i < sizeof(lengths)/sizeof(lengths[0]); i++) {
        struct fake_drive d = fake_track9();
        d.disc.pregap = d.disc.start - lengths[i];
        enum cyanrip_pregap_source src = CYANRIP_PREGAP_SRC_NONE;
        lsn_t got = fake_search(&d, &src);
        CHECK(got == d.disc.pregap && src == CYANRIP_PREGAP_SRC_SUBCHANNEL,
              "%i-frame pregap read as %i (source %i)", lengths[i],
              got == CDIO_INVALID_LSN ? -1 : d.disc.start - got, src);
        CHECK(d.lowest_ask >= d.disc.prev_start && d.highest_ask < d.disc.start,
              "%i-frame pregap: asked for %i to %i, outside %i to %i", lengths[i],
              d.lowest_ask, d.highest_ask, d.disc.prev_start, d.disc.start - 1);
    }

    /* A previous track of one sector leaves nothing to read. */
    struct fake_drive d = fake_track9();
    d.disc.prev_start = d.disc.start - 1;
    d.disc.pregap = d.disc.start;
    enum cyanrip_pregap_source src = CYANRIP_PREGAP_SRC_NONE;
    CHECK(fake_search(&d, &src) == d.disc.start && d.reads == 0 &&
          src == CYANRIP_PREGAP_SRC_SUBCHANNEL,
          "single-sector previous track: %i reads", d.reads);
}

/* A drive whose every frame is one sector off answered the old search with a
 * pregap one frame long or short, every time. */
static void test_search_shifted(void)
{
    static const int shifts[] = { 1, -1, 2, -3 };
    for (size_t i = 0; i < sizeof(shifts)/sizeof(shifts[0]); i++) {
        struct fake_drive d = fake_track9();
        d.answer = FAKE_SHIFTED;
        d.shift = shifts[i];
        enum cyanrip_pregap_source src = CYANRIP_PREGAP_SRC_NONE;
        lsn_t got = fake_search(&d, &src);
        CHECK(got == d.disc.pregap && src == CYANRIP_PREGAP_SRC_SUBCHANNEL,
              "drive %+i sectors off read the 94-frame pregap as %i (source %i)",
              shifts[i], got == CDIO_INVALID_LSN ? -1 : d.disc.start - got, src);
    }
}

/* One read in a few answering for the next sector is the shape that fits
 * track 9's 94 and 95: the old search's answer depended on which read the
 * drive slipped on. Every phase of the slip must give the same answer. */
static void test_search_flaky(void)
{
    for (int shift = -1; shift <= 1; shift += 2) {
        for (int every = 2; every <= 7; every++) {
            for (int phase = 0; phase < every; phase++) {
                struct fake_drive d = fake_track9();
                d.answer = FAKE_FLAKY;
                d.shift = shift;
                d.every = every;
                d.phase = phase;
                enum cyanrip_pregap_source src = CYANRIP_PREGAP_SRC_NONE;
                lsn_t got = fake_search(&d, &src);
                CHECK(got == d.disc.pregap && src == CYANRIP_PREGAP_SRC_SUBCHANNEL,
                      "one read in %i answering %+i off, from read %i: 94 read as %i",
                      every, shift, phase,
                      got == CDIO_INVALID_LSN ? -1 : d.disc.start - got);
            }
        }
    }
}

/* Track 4 of the reference disc: a 158-frame pregap read as none in two filed
 * rips. That needs the first read, the sector before INDEX 01, to have
 * answered with a frame of track 3, so from 158 or more sectors away. */
static void test_search_stale(void)
{
    struct fake_drive d = fake_track9();
    d.disc.track = 4;
    d.disc.prev_start = 28067;
    d.disc.start = 49920;
    d.disc.pregap = 49762;
    d.answer = FAKE_STALE;
    d.stale_read = 1;
    d.stale = 40000;
    enum cyanrip_pregap_source src = CYANRIP_PREGAP_SRC_NONE;
    lsn_t got = fake_search(&d, &src);
    CHECK(got == d.disc.pregap && src == CYANRIP_PREGAP_SRC_SUBCHANNEL,
          "stale first frame: the 158-frame pregap read as %i",
          got == CDIO_INVALID_LSN ? -1 : d.disc.start - got);

    /* A stale frame of the track before the previous one, while backtracking,
     * tripped an assert in the old search, which ends the process. */
    for (int n = 2; n <= 3; n++) {
        d = fake_track9();
        d.answer = FAKE_STALE;
        d.stale_read = n;
        d.stale = d.disc.prev_start - 1000;
        src = CYANRIP_PREGAP_SRC_NONE;
        got = fake_search(&d, &src);
        CHECK(got == d.disc.pregap && src == CYANRIP_PREGAP_SRC_SUBCHANNEL,
              "track 7 frame on read %i: 94 read as %i", n,
              got == CDIO_INVALID_LSN ? -1 : d.disc.start - got);
    }
}

/* A mode-3 frame names no track. One right after the previous track's last
 * sector has always been taken as the previous track's, so a pregap that
 * starts on one reads a frame short; that is the convention carried from
 * upstream's PR #115 and this pins it, on an aligned drive and a slipping
 * one alike. */
static void test_search_mode3(void)
{
    for (int every = 0; every <= 5; every++) {
        for (int phase = 0; phase < (every ? every : 1); phase++) {
            struct fake_drive d = fake_track9();
            d.disc.mode3 = d.disc.pregap;
            if (every) {
                d.answer = FAKE_FLAKY;
                d.shift = 1;
                d.every = every;
                d.phase = phase;
            }
            enum cyanrip_pregap_source src = CYANRIP_PREGAP_SRC_NONE;
            lsn_t got = fake_search(&d, &src);
            CHECK(got == d.disc.pregap + 1 && src == CYANRIP_PREGAP_SRC_SUBCHANNEL,
                  "mode-3 frame first in the pregap, slip 1 in %i from %i: read %i",
                  every, phase, got == CDIO_INVALID_LSN ? -1 : d.disc.start - got);
        }
    }

    /* Inside the previous track, or inside the pregap, it changes nothing. */
    static const int at[] = { -1, -2, 1, 40 };
    for (size_t i = 0; i < sizeof(at)/sizeof(at[0]); i++) {
        struct fake_drive d = fake_track9();
        d.disc.mode3 = d.disc.pregap + at[i];
        enum cyanrip_pregap_source src = CYANRIP_PREGAP_SRC_NONE;
        lsn_t got = fake_search(&d, &src);
        CHECK(got == d.disc.pregap, "mode-3 frame at pregap %+i: read %i",
              at[i], got == CDIO_INVALID_LSN ? -1 : d.disc.start - got);
    }
}

static void test_search_bad_frames(void)
{
    /* Frames around the boundary that fail a few times are read again. */
    struct fake_drive d = fake_track9();
    d.bad_from = d.disc.pregap - 2;
    d.bad_to = d.disc.pregap + 2;
    d.bad_reads = 10;
    enum cyanrip_pregap_source src = CYANRIP_PREGAP_SRC_NONE;
    lsn_t got = fake_search(&d, &src);
    CHECK(got == d.disc.pregap && src == CYANRIP_PREGAP_SRC_SUBCHANNEL,
          "boundary frames failing ten times: read %i (source %i)",
          got == CDIO_INVALID_LSN ? -1 : d.disc.start - got, src);

    /* One that never reads leaves the answer unknown, and says why. */
    d = fake_track9();
    d.bad_from = d.bad_to = d.disc.pregap - 1;
    d.bad_reads = -1;
    src = CYANRIP_PREGAP_SRC_NONE;
    got = fake_search(&d, &src);
    CHECK(got == CDIO_INVALID_LSN && src == CYANRIP_PREGAP_SRC_ERR_CRC,
          "unreadable boundary frame: got %i, source %i", got, src);

    /* A driver error ends the search as unreadable. */
    d = fake_track9();
    d.read_fails = 1;
    src = CYANRIP_PREGAP_SRC_NONE;
    got = fake_search(&d, &src);
    CHECK(got == CDIO_INVALID_LSN && src == CYANRIP_PREGAP_SRC_ERR_READ,
          "failing drive: got %i, source %i", got, src);
}

int main(void)
{
    test_crc();
    test_bcd_conversion();
    test_verify_compliant_drive();
    test_verify_binary_drive();
    test_verify_rejects();
    test_track_lsns_usable();
    test_search_aligned();
    test_search_shifted();
    test_search_flaky();
    test_search_stale();
    test_search_mode3();
    test_search_bad_frames();

    if (failures) {
        fprintf(stderr, "%d check(s) failed\n", failures);
        return 1;
    }

    printf("Q sub-channel decoding: all checks passed\n");
    return 0;
}
