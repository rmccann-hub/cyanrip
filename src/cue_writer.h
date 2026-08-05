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

#include "cyanrip_main.h"

/* Does this track have a pre-gap that was appended to the previous track, and
 * therefore needs an INDEX 00 in the cue sheet?
 *
 * Pure, and in a header, so tests/cuegap.c can exercise it: the case it exists
 * to get right is **unreachable from any disc image**. It needs a pre-gap that
 * is signalled and zero frames long, and no image driver produces one --
 * libcdio reports `unknown (sub-channel unreadable)` for a bincue track whose
 * INDEX 00 equals its INDEX 01, which was measured, not assumed. Only the Q
 * sub-channel search on a physical disc yields pregap_lsn == start_lsn_sig.
 *
 * **start_lsn_sig, not start_lsn.** They differ by the read offset:
 * setup_track_lsn() overwrites start_lsn with the offset-accounted first frame
 * *after* the gap decisions are taken, so by the time the cue is written a
 * +667 sample offset has moved start_lsn one frame past start_lsn_sig. The
 * guard used to compare against start_lsn, so a zero-length pre-gap looked
 * non-zero and the cue declared an INDEX 00 the log said did not exist -- on
 * four tracks of the 2026-08-04 and 2026-08-05 rig rips, at a timestamp one
 * frame past the end of the previous FILE. A pre-gap's length is defined
 * against the signalled start; the offset is a property of the read. */
static inline int crip_track_has_appended_pregap(lsn_t pregap_lsn,
                                                 lsn_t start_lsn_sig,
                                                 lsn_t dropped_pregap_start,
                                                 lsn_t merged_pregap_end,
                                                 int has_prev_track)
{
    return pregap_lsn != CDIO_INVALID_LSN
        && pregap_lsn != start_lsn_sig
        && has_prev_track
        && dropped_pregap_start == CDIO_INVALID_LSN
        && merged_pregap_end == CDIO_INVALID_LSN;
}

int cyanrip_cue_init(cyanrip_ctx *ctx);
void cyanrip_cue_start(cyanrip_ctx *ctx);
void cyanrip_cue_track(cyanrip_ctx *ctx, cyanrip_track *t);
void cyanrip_cue_end(cyanrip_ctx *ctx);
