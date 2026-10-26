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

#include <cdio/cdio.h>

#include "cyanrip_main.h"

/* Returns the track's pregap LSN, or CDIO_INVALID_LSN if there is none or it
 * could not be determined. Those two are not the same thing, so *source is set
 * to say which, and why - see enum cyanrip_pregap_source. Pass NULL if the
 * distinction isn't wanted. *stats, when given, says what a sub-channel search
 * saw, and is all zero when none ran. */
lsn_t cyanrip_get_track_pregap_lsn(CdIo_t *p_cdio, track_t track_number,
                                   enum cyanrip_pregap_source *source,
                                   struct cyanrip_pregap_stats *stats);

static inline lba_t cyanrip_get_track_pregap_lba(CdIo_t *p_cdio, track_t track_number) {
    return cdio_lsn_to_lba(cyanrip_get_track_pregap_lsn(p_cdio, track_number, NULL, NULL));
}

/* What reading a track's own Q frames for its ISRC found, for the record. */
struct cyanrip_subq_isrc {
    int found;          /* isrc holds a code a CRC-valid mode-3 frame carried */
    int frames_read;    /* frames the drive returned */
    int frames_valid;   /* of those, frames whose CRC checked */
    int isrc_frames;    /* of those, mode-3 (ISRC) frames */
    int read_failed;    /* the drive refused a read, which ended the scan */
    char isrc[CDIO_ISRC_SIZE + 1];
};

/* Reads the Q sub-channel of up to `count` sectors from `first`, one READ CD
 * each, and stops at the first CRC-valid mode-3 frame whose twelve characters
 * are ones an ISRC frame can carry. For a drive whose READ SUB-CHANNEL answers
 * with no ISRC: the frames are the disc's own, checked by their CRC. A drive
 * that synthesises its formatted Q from the TOC returns no mode-3 frames, and
 * the counts say so. Not for image drivers, which have no sub-channel. */
void cyanrip_read_isrc_subq(CdIo_t *p_cdio, lsn_t first, int count,
                            struct cyanrip_subq_isrc *res);

/* The reason the log and the record give for a track whose READ SUB-CHANNEL
 * gave no ISRC before and after cyanrip_read_isrc_subq() found none in `res`:
 * what the scan saw, in counts. Written into buf, at most `size` bytes. */
void cyanrip_subq_isrc_reason(const struct cyanrip_subq_isrc *res, char *buf, size_t size);
