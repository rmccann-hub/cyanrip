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

/* AccurateRip's response on any bytes. accurip.c is included, as
 * tests/arresp.c includes it, for its static crip_parse_accurip().
 *
 * The first byte gives the disc: 1 to 99 tracks, its low bit making the
 * first a data track and its next bit the last, as on an Enhanced CD. The
 * ids asked for are those of the response's first entry, so the fuzzer
 * reaches the entries that match as readily as those that do not. */

#include "accurip.c"

#include "fuzz.h"

void cyanrip_log(cyanrip_ctx *ctx, int verbose, const char *format, ...)
{
    (void)ctx; (void)verbose; (void)format;
}

static uint32_t le32(const uint8_t *p)
{
    return p[0] | p[1] << 8 | p[2] << 16 | (uint32_t)p[3] << 24;
}

int LLVMFuzzerInitialize(int *argc, char ***argv)
{
    (void)argc; (void)argv;
    return 0;
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
    if (size < 2)
        return 0;
    int nb = 1 + data[0] % 99;
    int data_first = data[1] & 1, data_last = (data[1] >> 1) & 1;
    data += 2;
    size -= 2;

    /* The context is large, so it is on the heap, as in arresp.c */
    cyanrip_ctx *ctx = av_mallocz(sizeof(*ctx));
    if (!ctx)
        return 0;
    int audio = 0;
    for (int i = 0; i < nb; i++) {
        ctx->tracks[i].number = i + 1;
        ctx->tracks[i].track_is_data = (i == 0 && data_first) ||
                                       (i == nb - 1 && data_last && nb > 1);
        audio += !ctx->tracks[i].track_is_data;
    }
    ctx->nb_tracks = ctx->nb_cd_tracks = nb;

    uint32_t id1 = size >= 13 ? le32(data + 1) : 0;
    uint32_t id2 = size >= 13 ? le32(data + 5) : 0;
    uint32_t cddb = size >= 13 ? le32(data + 9) : 0;
    crip_parse_accurip(ctx, data, size, audio, id1, id2, cddb);

    for (int i = 0; i < nb; i++)
        av_freep(&ctx->tracks[i].ar_db_entries);
    av_free(ctx);
    return 0;
}
