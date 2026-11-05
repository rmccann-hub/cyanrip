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

#pragma once

#include <stddef.h>
#include <stdint.h>

/* What the drive's MMC capabilities page (mode page 2Ah) declares about
 * accurate stream, byte 5 bit 1, "CD-DA Stream is Accurate". It is the
 * drive's own declaration, read once before ripping; nothing here measures
 * whether a stream is in fact accurate, and the log line says so. */
enum CripAccurateStream {
    CRIP_ACCURATE_STREAM_IMAGE = 0,  /* a disc image: no drive to ask */
    CRIP_ACCURATE_STREAM_UNREADABLE, /* MODE SENSE failed, or no page 2Ah in its reply */
    CRIP_ACCURATE_STREAM_SUPPORTED,
    CRIP_ACCURATE_STREAM_UNSUPPORTED,
};

/* Reads a MODE SENSE (10) reply: the 8-byte mode parameter header, any block
 * descriptors it declares, then the pages. Returns SUPPORTED or UNSUPPORTED
 * from page 2Ah, or UNREADABLE when the reply is too short to hold byte 5 of
 * that page, or holds no page 2Ah at all. Pure, so it is tested on built
 * replies; the read itself needs a drive. */
enum CripAccurateStream crip_accurate_stream_parse(const uint8_t *buf, size_t len);

/* The value of the `Accurate stream:` line, as round 32 lap 1 S19 proposed it. */
const char *crip_accurate_stream_text(enum CripAccurateStream s);

/* Whether the drive reports the disc as recordable, from its current
 * profile (GET CONFIGURATION): CD-ROM is pressed, CD-R and CD-RW were
 * written. It is the drive's report of the medium, not a judgement of the
 * disc; Platterpus's F9 asked for it as a tri-state. */
#define CRIP_PROFILE_IMAGE      (-1)  /* a disc image: no drive to ask */
#define CRIP_PROFILE_UNREADABLE (-2)  /* GET CONFIGURATION failed */

/* Reads a GET CONFIGURATION reply's feature header: bytes 0-3 the length of
 * what follows them, bytes 6-7 the drive's current profile, which MMC defines
 * there for this purpose. Returns that profile, or CRIP_PROFILE_UNREADABLE when
 * the reply is too short to hold it. Pure, so it is tested on built replies.
 *
 * Not libcdio's mmc_get_disctype(), which searches the profile list for one
 * with its current bit set: its loop stops one descriptor short of the list's
 * end, so a drive that lists CD-ROM last never answers, and it returns
 * success with its 0xffff placeholder whether or not it found one (the same
 * at 2.1.1, 2.3.0, 2.4.0 and master 68ea374). The rig's BDR-209D gave 0xffff
 * in all 38 logs of round 36's runs (our round 36 lap 8 S4). */
int crip_current_profile_parse(const uint8_t *buf, size_t len);

/* The value of the `Recordable:` line for a profile, or for one of the two
 * negatives above. Writes into buf, which 64 bytes always holds. */
const char *crip_recordable_text(char *buf, size_t size, int profile);

/* The `Speed:` value: `speed` is -S's (0 when not given), `is_image` that
 * the device is a disc image, and `failed` that libcdio could not set the
 * speed. Without -S nothing asks the drive whether it can change speed; with
 * it, a speed that could not be set reads at the drive's own speed and says
 * so, and an image has no speed to set (our round 36 lap 12 S11 (a) and
 * round 37 lap 1 S8, accepted by Platterpus's round 36 lap 13 S5 and round
 * 37 lap 2 S6). Writes into buf and returns it. */
const char *crip_speed_text(char *buf, size_t size, int speed, int is_image,
                            int failed);

/* The `C2 errors:` value: `caps_failed` that the capabilities query failed,
 * which sets every capability word to CDIO_DRIVE_CAP_ERROR, so the C2 bit's
 * absence says nothing (our round 36 lap 12 S11 (c), accepted by
 * Platterpus's lap 13 S5); `c2` that the drive declares C2 reporting. */
const char *crip_c2_text(int caps_failed, int c2);

/* WHAT THE DRIVE DECLARES, ASKED IN FULL AND KEPT AS IT ANSWERED (round 38,
 * for +platterpus.30; docs/research/2026-11-04-drive-settings.md). Three
 * standard read-only commands any MMC drive answers, new or legacy: INQUIRY,
 * GET CONFIGURATION for every feature, and MODE SENSE (10) for every mode
 * page (3Fh) under each page control. Kept whole and raw, so nothing has to
 * know in advance which byte matters on which drive: the CD Read feature's
 * DAP and C2 Flags bits, the error recovery and caching pages, and whatever a
 * later reader needs are read from these replies afterwards.
 *
 * Each is what the drive SAYS. Pioneer's BDR-203 command reference says that
 * drive ignores most of the error recovery page and that the caching page has
 * no effect, so nothing kept here measures what a drive does, and nothing
 * here writes a page or sends a vendor command. */
#define CRIP_FEATURE_CD_READ 0x001e
#define CRIP_REPLY_MAX       8192 /* bytes asked for, and at most kept, of a reply */
#define CRIP_INQUIRY_MAX     255  /* INQUIRY's: one byte, for drives that read one */
#define CRIP_DECLARED_MAX    64   /* bytes of one feature descriptor kept */

enum CripReplyKind {
    CRIP_REPLY_INQUIRY,
    CRIP_REPLY_CONFIGURATION,
    CRIP_REPLY_MODE_SENSE_10,
};

typedef struct CripReply {
    int asked;     /* the command was sent; 0 for a disc image */
    int answered;  /* it succeeded */
    int length;    /* the reply's whole length, as its own header declares it */
    int nb_bytes;  /* of it kept: that length, at most the allocation asked */
    uint8_t bytes[CRIP_REPLY_MAX];
} CripReply;

/* The whole length a reply declares in its own header: INQUIRY's byte 4 plus
 * 5, GET CONFIGURATION's bytes 0-3 plus 4, MODE SENSE (10)'s bytes 0-1 plus
 * 2. 0 when `len` is too short to hold that header. Pure. */
size_t crip_reply_length(enum CripReplyKind kind, const uint8_t *buf, size_t len);

/* One feature descriptor, found in a GET CONFIGURATION reply. */
typedef struct CripDeclared {
    int found;     /* the reply held a whole descriptor for it */
    int length;    /* the descriptor's whole length, as declared */
    int nb_bytes;  /* of it kept in bytes[], at most CRIP_DECLARED_MAX */
    uint8_t bytes[CRIP_DECLARED_MAX];
} CripDeclared;

/* Finds feature `code` in a GET CONFIGURATION reply: the 8-byte feature
 * header, bytes 0-3 the length of what follows them, then descriptors of 4
 * bytes plus their byte 3. Copies the descriptor into `out` and returns 1,
 * or returns 0 when the reply holds no whole descriptor for it. Pure. */
int crip_feature_take(const uint8_t *buf, size_t len, unsigned code,
                      CripDeclared *out);
