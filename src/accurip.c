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

#include <stdlib.h>
#include <curl/curl.h>

#include "accurip.h"
#include "cyanrip_log.h"
#include "bytestream.h"

#define ACCURIP_DB_BASE_URL "http://www.accuraterip.com/accuraterip"

static int get_accurip_ids(cyanrip_ctx *ctx, uint32_t *id_type_1, uint32_t *id_type_2)
{
    int audio_tracks = 0;
    uint64_t idt1 = 0x0;
    uint64_t idt2 = 0x0;

    for (int i = 0; i < ctx->nb_cd_tracks; i++) {
        cyanrip_track *t = &ctx->tracks[i];
        if (t->track_is_data)
            continue;

        idt1 += t->start_lsn;
        idt2 += (t->start_lsn ? t->start_lsn : 1) * t->number;
        audio_tracks++;
    }

    lsn_t last = ctx->tracks[audio_tracks - 1].end_lsn + 1;
    idt1 += last;
    idt2 += last * (audio_tracks + 1);

    idt1 &= 0xffffffff;
    idt2 &= 0xffffffff;

    *id_type_1 = idt1;
    *id_type_2 = idt2;

    return audio_tracks;
}

typedef struct RecvCtx {
    cyanrip_ctx *ctx;
    uint8_t *data;
    size_t size;
} RecvCtx;

static size_t receive_data(void *buffer, size_t size, size_t nb, void *opaque)
{
    RecvCtx *rctx = opaque;

    /* av_realloc() returns NULL and leaves the old block intact when it cannot
     * satisfy the request, so the result has to be taken in a temporary.
     * Unchecked, the failure stored NULL and the memcpy() below wrote through
     * it. Returning short tells curl the write failed: curl_easy_perform()
     * then reports CURLE_WRITE_ERROR and the existing handler below logs it.
     * Same shape as receive_image() in coverart.c. */
    uint8_t *new_data = av_realloc(rctx->data, rctx->size + (size * nb));
    if (!new_data)
        return 0;

    memcpy(new_data + rctx->size, buffer, size * nb);

    rctx->data  = new_data;
    rctx->size += size * nb;

    return size * nb;
}

/* Whether an AccurateRip response body looks like an error page rather than
 * binary entry data: the literal "html" beginning within the first 64 bytes.
 *
 * SPLIT OUT SO IT CAN BE TESTED. Every scenario in tests/rip_images.py passes
 * -A, so crip_fill_accurip() returns before any of this and nothing in the
 * suite has ever executed the decision. tests/arresp.c includes this file to
 * reach it, the same move tests/subq.c makes for pregap.c's static decoders.
 *
 * The body is assembled by raw memcpy() in receive_data() and is NEVER
 * NUL-terminated, so it must not be handed to a str* function. This takes an
 * explicit length and reads no byte outside it. `data` may be NULL, which is
 * what a 200 with an empty body leaves behind. */
static const uint8_t *crip_find_html_marker(const uint8_t *data, size_t size)
{
    if (!data)
        return NULL;

    for (size_t i = 0; i < FFMIN(size, 64); i++) {
        if (size - i >= 4 && !memcmp(data + i, "html", 4))
            return data + i;
    }

    return NULL;
}

static int cmp_conf(const void *a, const void *b)
{
    return ((CRIPAccuDBEntry *)a)->confidence - ((CRIPAccuDBEntry *)b)->confidence;
}

int crip_fill_accurip(cyanrip_ctx *ctx)
{
    int ret = 0;
    char errbuf[CURL_ERROR_SIZE];
    RecvCtx rctx = { .ctx = ctx };

    if (ctx->settings.disable_accurip)
        return 0;

    CURL *curl_ctx = curl_easy_init();

    /* Get both accurip disc IDs */
    uint32_t id_type_1, id_type_2;
    int audio_tracks = get_accurip_ids(ctx, &id_type_1, &id_type_2);

    /* Get CDDB ID */
    const char *cddb_id_str = dict_get(ctx->meta, "cddb");
    if (!cddb_id_str) {
        cyanrip_log(ctx, 0, "Unable to get AccuRIP DB data: missing CDDB ID!\n");
        goto end;
    }

    /* Format all the data in the needed way */
    uint32_t cddb_id = strtoul(cddb_id_str, NULL, 16);
    char id_type_1_s[9] = { 0 };
    snprintf(id_type_1_s, sizeof(id_type_1_s), "%08x", id_type_1);

    /* Finally compose the URL */
    char request_url[512] = { 0 };
    snprintf(request_url, sizeof(request_url), "%s/%c/%c/%c/dBAR-%.3d-%s-%08x-%08x.bin",
             ACCURIP_DB_BASE_URL,
             id_type_1_s[7], id_type_1_s[6], id_type_1_s[5],
             audio_tracks, id_type_1_s, id_type_2, cddb_id);

    curl_easy_setopt(curl_ctx, CURLOPT_URL, request_url);

    char user_agent[256] = { 0 };
    sprintf(user_agent, "cyanrip/%s ( https://github.com/cyanreg/cyanrip )", PROJECT_VERSION_STRING);
    curl_easy_setopt(curl_ctx, CURLOPT_USERAGENT, user_agent);

    curl_easy_setopt(curl_ctx, CURLOPT_WRITEFUNCTION, receive_data);
    curl_easy_setopt(curl_ctx, CURLOPT_WRITEDATA, &rctx);

    curl_easy_setopt(curl_ctx, CURLOPT_ERRORBUFFER, errbuf);
    curl_easy_setopt(curl_ctx, CURLOPT_FAILONERROR, 1L); /* Explode on errors */

    CURLcode res = curl_easy_perform(curl_ctx);
    if (res != CURLE_OK) {
        /* Filter out the majority of 404 errors here */
        if (res == CURLE_HTTP_RETURNED_ERROR) {
            cyanrip_log(ctx, 0, "Unable to get AccuRIP DB data: missing entry!\n");
            ctx->ar_db_status = CYANRIP_ACCUDB_NOT_FOUND;
            goto end;
        }

        /* Different error */
        size_t len = strlen(errbuf);
        if (len)
            cyanrip_log(ctx, 0, "Unable to get AccuRIP DB data: %s%s",
                        errbuf, ((errbuf[len - 1] != '\n') ? "\n" : ""));
        else
            cyanrip_log(ctx, 0, "Unable to get AccuRIP DB data: %s\n!\n",
                        curl_easy_strerror(res));
        ctx->ar_db_status = CYANRIP_ACCUDB_ERROR;
        goto end;
    }

    /* Get content type, if not possible we probably have an error somewhere */
    char *content_type = NULL;
    res = curl_easy_getinfo(curl_ctx, CURLINFO_CONTENT_TYPE, &content_type);
    if (res != CURLE_OK) {
        cyanrip_log(ctx, 0, "Unable to get AccuRIP DB data: %s\n!\n",
                    curl_easy_strerror(res));
        goto end;
    }

    /* If we have a binary we're pretty sure we've found a match.
     *
     * content_type is NULL when the response carried no Content-Type header at
     * all, which curl reports as CURLE_OK -- a 200 with no Content-Type is
     * legal HTTP and is what a minimal server or an interposing proxy returns.
     * Treat the absent header as "not the binary type", which is the
     * conservative reading and the one that goes on to check for an error
     * page. */
    if (!content_type || strcmp(content_type, "application/octet-stream")) {
        /* Atrocious heuristics to determine whether we have an error or binary data, don't look */
        /* The body is assembled by raw memcpy() above and is never
         * NUL-terminated, so it cannot be handed to strstr(): that read off the
         * end of the allocation for any body without a zero byte, and passed
         * NULL outright when the write callback never fired. Search a bounded
         * window instead. The match must START before offset 64, which is what
         * the pointer arithmetic here used to express. */
        const uint8_t *html_loc = crip_find_html_marker(rctx.data, rctx.size);
        if (html_loc) {
            /* If we have "html" in the first 64 bytes its likely an error.
             * This is painful to write. */
            cyanrip_log(ctx, 0, "Unable to get AccuRIP DB data: missing entry!\n");
            ctx->ar_db_status = CYANRIP_ACCUDB_NOT_FOUND;
            goto end;
        }
    }

    GetByteContext gbc = { 0 };
    bytestream2_init(&gbc, rctx.data, rctx.size);

    ctx->ar_db_status = CYANRIP_ACCUDB_FOUND;

    int entry_size = 1 + 12 + audio_tracks * (1 + 8);

    if (rctx.size % entry_size) {
        cyanrip_log(ctx, 0, "AccuRIP DB data error, got unexpected number of bytes!\n");
        ctx->ar_db_status = CYANRIP_ACCUDB_ERROR;
        goto end;
    }

    int nb_entries = rctx.size / entry_size;

    for (int i = 0; i < nb_entries; i++) {
        if (bytestream2_get_byte(&gbc) != audio_tracks ||
            bytestream2_get_le32(&gbc) != id_type_1 ||
            bytestream2_get_le32(&gbc) != id_type_2 ||
            bytestream2_get_le32(&gbc) != cddb_id) {
            if (ctx->ar_db_status != CYANRIP_ACCUDB_FOUND)
                ctx->ar_db_status = CYANRIP_ACCUDB_MISMATCH;
            bytestream2_skip(&gbc, entry_size - (bytestream2_tell(&gbc) % entry_size));
            continue;
        }

        ctx->ar_db_status = CYANRIP_ACCUDB_FOUND;

        for (int j = 0; j < audio_tracks; j++) {
            cyanrip_track *t = &ctx->tracks[j];

            int confidence = bytestream2_get_byte(&gbc);
            uint32_t checksum = bytestream2_get_le32(&gbc);
            uint32_t checksum_450 = bytestream2_get_le32(&gbc);

            if (t->track_is_data)
                continue;

            t->ar_db_entries = av_realloc(t->ar_db_entries,
                                          sizeof(CRIPAccuDBEntry) * (t->ar_db_nb_entries + 1));

            t->ar_db_status = CYANRIP_ACCUDB_FOUND;
            t->ar_db_entries[t->ar_db_nb_entries].confidence = confidence;
            t->ar_db_entries[t->ar_db_nb_entries].checksum = checksum;
            t->ar_db_entries[t->ar_db_nb_entries].checksum_450 = checksum_450;
            t->ar_db_max_confidence = FFMAX(confidence, t->ar_db_max_confidence);

            t->ar_db_nb_entries++;
        }
    }

    for (int i = 0; i < audio_tracks; i++) {
        cyanrip_track *t = &ctx->tracks[i];
        if (t->ar_db_nb_entries)
            qsort(t->ar_db_entries, t->ar_db_nb_entries, sizeof(CRIPAccuDBEntry), cmp_conf);
    }

end:
    curl_easy_cleanup(curl_ctx);
    av_free(rctx.data);

    return ret;
}

int crip_find_ar(cyanrip_track *t, uint32_t checksum, int is_450)
{
    if (t->ar_db_status != CYANRIP_ACCUDB_FOUND)
        return 0;

    for (int i = 0; i < t->ar_db_nb_entries; i++) {
        CRIPAccuDBEntry *e = &t->ar_db_entries[i];
        if (is_450 && e->checksum_450 == checksum)
            return e->confidence;
        else if (e->checksum == checksum)
            return e->confidence;
    }

    return -1;
}
