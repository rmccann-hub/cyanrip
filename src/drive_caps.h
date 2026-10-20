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
