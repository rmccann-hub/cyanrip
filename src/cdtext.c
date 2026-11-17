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

#include <stdio.h>
#include <string.h>

#include <cdio/cdtext.h>
#include <libavutil/avstring.h>

#include "cdtext.h"
#include "cyanrip_log.h"

/* The disc-level block is track 0 in libcdio's addressing; real tracks are
 * addressed by their CD track number. */
#define CDTEXT_DISC_TRACK 0

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
        if (!crip_cdtext_field_keys[f])
            continue;

        const char *val = cdtext_get_const(cdt, (cdtext_field_t)f, track);
        if (!val || !val[0])
            continue;

        av_dict_set(dst, crip_cdtext_field_keys[f], val, 0);
        count++;
    }

    return count;
}

/* WHETHER LIBCDIO'S CD-TEXT LANGUAGE IS THE SOURCE'S. libcdio 2.1.0 reads a
 * language from binary CD-TEXT, a drive's or a CUE sheet's CDTEXTFILE, but
 * gives a cdrdao .toc's CD-TEXT and a CUE sheet's inline CD-TEXT the language
 * English whatever the source says: a .toc whose LANGUAGE_MAP says German
 * logged `present (English, ...)` (US-2). Those two routes now log `unknown
 * language`, as Platterpus's lap 4 S15 answered our lap 3 S23. A CUE sheet is
 * read for a CDTEXTFILE command at the start of a line, the only route by
 * which its CD-TEXT is binary; libcdio names the sheet it parsed. */
static int cdtext_language_is_the_sources(cyanrip_ctx *ctx)
{
    switch (cdio_get_driver_id(ctx->cdio)) {
    case DRIVER_CDRDAO:
        return 0;
    case DRIVER_BINCUE: {
        const char *cue = cdio_get_arg(ctx->cdio, "cue");
        FILE *f = cue ? fopen(cue, "r") : NULL;
        if (!f)
            return 0;
        char line[1024];
        int binary = 0;
        while (!binary && fgets(line, sizeof(line), f)) {
            const char *p = line + strspn(line, " \t");
            binary = !av_strncasecmp(p, "CDTEXTFILE", 10) &&
                     (p[10] == ' ' || p[10] == '\t');
        }
        fclose(f);
        return binary;
    }
    default:
        return 1;
    }
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

    ctx->cdtext_language = cdtext_language_is_the_sources(ctx) ?
                           cdtext_lang2str(cdtext_get_language((cdtext_t *)cdt)) : NULL;

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
        /* Only a code ISO 3901 allows: a CD-TEXT ISRC pack is free text, and
         * a malformed one reached the tags and the CUE sheet's ISRC line
         * unchecked, where the disc's own code is checked (the review of
         * 2026-11-16's audit candidates). The CD-TEXT block's own `isrc:`
         * line still prints it, as the disc's text. */
        const char *isrc = dict_get(t->cdtext, "isrc");
        if (isrc && crip_isrc_is_iso3901(isrc))
            fill_gap(&t->meta, "isrc", t->cdtext, "isrc");
    }
}
