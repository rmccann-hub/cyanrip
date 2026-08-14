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

int main(void)
{
    test_crc();
    test_bcd_conversion();
    test_verify_compliant_drive();
    test_verify_binary_drive();
    test_verify_rejects();
    test_track_lsns_usable();

    if (failures) {
        fprintf(stderr, "%d check(s) failed\n", failures);
        return 1;
    }

    printf("Q sub-channel decoding: all checks passed\n");
    return 0;
}
