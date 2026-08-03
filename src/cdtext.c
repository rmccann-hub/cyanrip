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

#include <cdio/cdtext.h>

#include "cdtext.h"
#include "cyanrip_log.h"

/* The disc-level block is track 0 in libcdio's addressing; real tracks are
 * addressed by their CD track number. */
#define CDTEXT_DISC_TRACK 0

/* Lower-cased libcdio field names, used as the dictionary keys so the log and
 * anything reading it see the field names the CD-TEXT spec uses rather than
 * cyanrip's tag names. Indexed by cdtext_field_t. */
static const char *const field_keys[MAX_CDTEXT_FIELDS] = {
    [CDTEXT_FIELD_TITLE]      = "title",
    [CDTEXT_FIELD_PERFORMER]  = "performer",
    [CDTEXT_FIELD_SONGWRITER] = "songwriter",
    [CDTEXT_FIELD_COMPOSER]   = "composer",
    [CDTEXT_FIELD_MESSAGE]    = "message",
    [CDTEXT_FIELD_ARRANGER]   = "arranger",
    [CDTEXT_FIELD_ISRC]       = "isrc",
    [CDTEXT_FIELD_UPC_EAN]    = "upc_ean",
    [CDTEXT_FIELD_GENRE]      = "genre",
    [CDTEXT_FIELD_DISCID]     = "discid",
};

/* Reads every field of one CD-TEXT track into dst. Returns how many were set.
 *
 * cdtext_get_const() hands back a pointer libcdio owns; av_dict_set() copies,
 * so nothing here needs freeing. Empty strings are dropped rather than stored:
 * a present-but-empty field says nothing a missing one does not, and storing
 * it would make the field count overstate what the disc actually carries. */
static int read_track_fields(const cdtext_t *cdt, track_t track,
                             AVDictionary **dst)
{
    int count = 0;

    for (int f = MIN_CDTEXT_FIELD; f < MAX_CDTEXT_FIELDS; f++) {
        if (!field_keys[f])
            continue;

        const char *val = cdtext_get_const(cdt, (cdtext_field_t)f, track);
        if (!val || !val[0])
            continue;

        av_dict_set(dst, field_keys[f], val, 0);
        count++;
    }

    return count;
}

int crip_fill_cdtext(cyanrip_ctx *ctx)
{
    ctx->cdtext_status = CYANRIP_CDTEXT_ABSENT;
    ctx->cdtext_nb_disc_fields = 0;
    ctx->cdtext_nb_tagged_tracks = 0;
    ctx->cdtext_language = NULL;

    if (!ctx->cdio)
        return 0;

    /* Owned by libcdio and freed with the CdIo_t -- never destroy it here. */
    const cdtext_t *cdt = cdio_get_cdtext(ctx->cdio);
    if (!cdt)
        return 0;

    ctx->cdtext_language = cdtext_lang2str(cdtext_get_language((cdtext_t *)cdt));

    ctx->cdtext_nb_disc_fields = read_track_fields(cdt, CDTEXT_DISC_TRACK,
                                                   &ctx->cdtext);

    /* Iterate cyanrip's own tracks rather than cdtext_get_first_track() /
     * cdtext_get_last_track(): those two report 0/0 for CD-TEXT that came from
     * a disc image even when per-track fields are present, so bounding the
     * loop by them silently drops every track. Verified against libcdio 2.1.0
     * with a cdrdao .toc image (tests/fixtures/cdtext.toc). */
    for (int i = 0; i < ctx->nb_tracks; i++) {
        cyanrip_track *t = &ctx->tracks[i];

        if (t->cd_track_number < 1)
            continue;

        if (read_track_fields(cdt, t->cd_track_number, &t->cdtext))
            ctx->cdtext_nb_tagged_tracks++;
    }

    if (ctx->cdtext_nb_disc_fields || ctx->cdtext_nb_tagged_tracks)
        ctx->cdtext_status = CYANRIP_CDTEXT_PRESENT;

    return 0;
}

/* Copies one CD-TEXT field into a metadata dictionary if, and only if, the
 * target tag is still unset. CD-TEXT is the weakest metadata source we have --
 * it is whatever the plant wrote, with no way to correct it after pressing --
 * so it fills gaps and never overwrites. */
static void fill_gap(AVDictionary **meta, const char *tag,
                     AVDictionary *cdtext, const char *field)
{
    const char *val = dict_get(cdtext, field);

    if (!val || !val[0] || dict_get(*meta, tag))
        return;

    av_dict_set(meta, tag, val, 0);
}

void crip_cdtext_to_meta(cyanrip_ctx *ctx)
{
    if (ctx->cdtext_status != CYANRIP_CDTEXT_PRESENT)
        return;

    fill_gap(&ctx->meta, "album",        ctx->cdtext, "title");
    fill_gap(&ctx->meta, "album_artist", ctx->cdtext, "performer");
    fill_gap(&ctx->meta, "artist",       ctx->cdtext, "performer");
    fill_gap(&ctx->meta, "composer",     ctx->cdtext, "composer");
    fill_gap(&ctx->meta, "genre",        ctx->cdtext, "genre");
    fill_gap(&ctx->meta, "barcode",      ctx->cdtext, "upc_ean");

    for (int i = 0; i < ctx->nb_tracks; i++) {
        cyanrip_track *t = &ctx->tracks[i];

        fill_gap(&t->meta, "title",    t->cdtext, "title");
        fill_gap(&t->meta, "artist",   t->cdtext, "performer");
        fill_gap(&t->meta, "composer", t->cdtext, "composer");
        fill_gap(&t->meta, "isrc",     t->cdtext, "isrc");
    }
}
