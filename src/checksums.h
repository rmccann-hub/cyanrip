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

#include <stdint.h>
#include <libavutil/crc.h>
#include <libavutil/mem.h>

#include "cyanrip_main.h"

typedef struct cyanrip_checksum_ctx {
    const AVCRC *eac_ctx;
    uint32_t eac_crc;
    uint32_t acu_start;
    uint32_t acu_end;
    uint32_t acu_mult;
    uint32_t acu_sum_1;
    uint32_t acu_sum_1_450;
    uint32_t acu_sum_2;
    /* One CRC32 per CRIP_BLOCK_CRC_BYTES of the bytes the EAC CRC32 covers,
     * written to blk_track as each block ends */
    cyanrip_track *blk_track;
    uint32_t blk_crc;
    int blk_bytes;
} cyanrip_checksum_ctx;

/* 75 frames, a second of audio: block_crcs' unit */
#define CRIP_BLOCK_CRC_BYTES (75 * CDIO_CD_FRAMESIZE_RAW)

static inline void crip_block_crc_push(cyanrip_track *t, uint32_t crc)
{
    if (t->block_crcs_failed)
        return;
    if (t->nb_block_crcs == t->block_crcs_alloc) {
        const int n = t->block_crcs_alloc ? 2 * t->block_crcs_alloc : 512;
        uint32_t *g = av_realloc_array(t->block_crcs, n, sizeof(*g));
        if (!g) {
            t->block_crcs_failed = 1;
            return;
        }
        t->block_crcs = g;
        t->block_crcs_alloc = n;
    }
    t->block_crcs[t->nb_block_crcs++] = crc;
}

static inline void crip_init_checksum_ctx(cyanrip_ctx *ctx, cyanrip_checksum_ctx *s, cyanrip_track *t)
{
    s->eac_ctx   = av_crc_get_table(AV_CRC_32_IEEE_LE);
    s->eac_crc   = UINT32_MAX;
    s->acu_start = 0;
    s->acu_end   = t->nb_samples;
    s->acu_mult  = 1;
    s->acu_sum_1 = 0x0;
    s->acu_sum_1_450 = 0x0;
    s->acu_sum_2 = 0x0;
    s->blk_track = t;
    s->blk_crc = UINT32_MAX;
    s->blk_bytes = 0;

    t->computed_crcs = 0;
    t->nb_block_crcs = 0;
    t->block_crcs_failed = 0;

    if (t->acurip_track_is_first)
        s->acu_start += (CDIO_CD_FRAMESIZE_RAW * 5) >> 2;
    if (t->acurip_track_is_last)
        s->acu_end   -= (CDIO_CD_FRAMESIZE_RAW * 5) >> 2;
}

static inline void crip_process_checksums(cyanrip_checksum_ctx *s, const uint8_t *data, int bytes)
{
    if (!bytes)
        return;

    s->eac_crc = av_crc(s->eac_ctx, s->eac_crc, data, bytes);

    /* The same bytes, cut at every second of audio */
    for (int done = 0; done < bytes;) {
        const int n = FFMIN(bytes - done, CRIP_BLOCK_CRC_BYTES - s->blk_bytes);
        s->blk_crc = av_crc(s->eac_ctx, s->blk_crc, data + done, n);
        s->blk_bytes += n;
        done += n;
        if (s->blk_bytes == CRIP_BLOCK_CRC_BYTES) {
            crip_block_crc_push(s->blk_track, s->blk_crc ^ UINT32_MAX);
            s->blk_crc = UINT32_MAX;
            s->blk_bytes = 0;
        }
    }

    /* Loop over samples */
    for (int j = 0; j < (bytes >> 2); j++) {
        if (s->acu_mult >= s->acu_start && s->acu_mult <= s->acu_end) {
            uint32_t val = AV_RL32(&data[j*4]);
            uint64_t tmp = (uint64_t)val  * (uint64_t)s->acu_mult;
            uint32_t lo  = (uint32_t)(tmp & (uint64_t)UINT32_MAX);
            uint32_t hi  = (uint32_t)(tmp / (uint64_t)0x100000000);
            s->acu_sum_1 += s->acu_mult * val;
            s->acu_sum_2 += hi;
            s->acu_sum_2 += lo;
        }
        if (((s->acu_mult - 1) >= (450 * (CDIO_CD_FRAMESIZE_RAW >> 2))) &&
            ((s->acu_mult - 1)  < (451 * (CDIO_CD_FRAMESIZE_RAW >> 2)))) {
            uint32_t mult = s->acu_mult - (450 * (CDIO_CD_FRAMESIZE_RAW >> 2));
            s->acu_sum_1_450 += AV_RL32(&data[j*4]) * mult;
        }
        s->acu_mult++;
    }
}

static inline void crip_finalize_checksums(cyanrip_checksum_ctx *s, cyanrip_track *t)
{
    t->computed_crcs = 1;
    t->eac_crc = s->eac_crc ^ UINT32_MAX;
    if (s->blk_bytes) {
        crip_block_crc_push(t, s->blk_crc ^ UINT32_MAX);
        s->blk_crc = UINT32_MAX;
        s->blk_bytes = 0;
    }
    t->acurip_checksum_v1 = s->acu_sum_1;
    t->acurip_checksum_v1_450 = s->acu_sum_1_450;
    t->acurip_checksum_v2 = s->acu_sum_2;
}
