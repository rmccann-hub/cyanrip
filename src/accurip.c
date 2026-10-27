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

#define ACCURIP_DB_BASE_URL "https://www.accuraterip.com/accuraterip"

/* The most a response is read to (review C item 1.5). A dBAR file holds one
 * entry per pressing, each 13 bytes plus 9 per track, so the largest real one
 * is a few hundred kilobytes; without a cap the buffer grew per callback until
 * the 60 s timeout, which bounds time and not size. */
#define ACCURIP_MAX_BYTES (4 << 20)

int crip_get_accurip_ids(cyanrip_ctx *ctx, uint32_t *id_type_1, uint32_t *id_type_2,
                         uint32_t *cddb_id)
{
    int audio_tracks = 0;
    uint64_t idt1 = 0x0;
    uint64_t idt2 = 0x0;

    /* AccurateRip drops data tracks from the TOC and renumbers the audio
     * tracks to be consecutive, but keeps the disc's real lead-out, with
     * any trailing data track still in front of it. */
    for (int i = 0; i < ctx->nb_cd_tracks; i++) {
        cyanrip_track *t = &ctx->tracks[i];
        if (t->track_is_data)
            continue;

        audio_tracks++;
        idt1 += t->start_lsn;
        idt2 += (t->start_lsn ? t->start_lsn : 1) * audio_tracks;
    }

    lsn_t last = ctx->end_lsn + 1;
    idt1 += last;
    idt2 += last * (audio_tracks + 1);

    idt1 &= 0xffffffff;
    idt2 &= 0xffffffff;

    *id_type_1 = idt1;
    *id_type_2 = idt2;

    /* The database URL carries a FreeDB ID computed over the full TOC,
     * data tracks and the real lead-out included, unlike the printed one,
     * which follows libdiscid in leaving trailing data tracks out. */
    uint32_t sum = 0;
    for (int i = 0; i < ctx->nb_cd_tracks; i++) {
        uint32_t m = (ctx->tracks[i].start_lsn + 150) / 75;
        while (m > 0) {
            sum += m % 10;
            m /= 10;
        }
    }

    uint32_t len = (last + 150) / 75 - (ctx->tracks[0].start_lsn + 150) / 75;
    *cddb_id = ((sum % 0xff) << 24) | (len << 8) | ctx->nb_cd_tracks;

    return audio_tracks;
}

typedef struct RecvCtx {
    cyanrip_ctx *ctx;
    uint8_t *data;
    size_t size;
    int too_big; /* The response passed ACCURIP_MAX_BYTES and was cut off */
} RecvCtx;

/* HTTPS only, for the request and any redirect (review C item 1.5); the
 * certificate is verified, as libcurl does unless told not to. Its string
 * option is libcurl 7.85's, and the bitmask it replaced is deprecated from
 * then, so a build uses the one its headers have. Same as https_only() in
 * coverart.c. */
static void https_only(CURL *curl_ctx)
{
#if LIBCURL_VERSION_NUM >= 0x075500
    curl_easy_setopt(curl_ctx, CURLOPT_PROTOCOLS_STR, "https");
    curl_easy_setopt(curl_ctx, CURLOPT_REDIR_PROTOCOLS_STR, "https");
#else
    curl_easy_setopt(curl_ctx, CURLOPT_PROTOCOLS, (long)CURLPROTO_HTTPS);
    curl_easy_setopt(curl_ctx, CURLOPT_REDIR_PROTOCOLS, (long)CURLPROTO_HTTPS);
#endif
}

/* Kept NUL-terminated, for the error page check */
static size_t receive_data(void *buffer, size_t size, size_t nb, void *opaque)
{
    RecvCtx *rctx = opaque;

    /* Checked before the size is added to, so neither can wrap. Returning
     * short makes curl stop with CURLE_WRITE_ERROR, whose own message would
     * say a write failed, so the flag tells the caller what happened. */
    if (size * nb > ACCURIP_MAX_BYTES - rctx->size) {
        rctx->too_big = 1;
        return 0;
    }

    /* av_realloc() returns NULL and leaves the old block intact when it cannot
     * satisfy the request, so the result has to be taken in a temporary.
     * Unchecked, the failure stored NULL and the memcpy() below wrote through
     * it. Returning short tells curl the write failed: curl_easy_perform()
     * then reports CURLE_WRITE_ERROR and the existing handler below logs it.
     * Same shape as receive_image() in coverart.c. One byte more than the
     * data, for the NUL written below (upstream's 76dcd5d). */
    uint8_t *new_data = av_realloc(rctx->data, rctx->size + (size * nb) + 1);
    if (!new_data)
        return 0;

    memcpy(new_data + rctx->size, buffer, size * nb);

    rctx->data  = new_data;
    rctx->size += size * nb;
    rctx->data[rctx->size] = '\0';

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
 * The body is assembled by raw memcpy() in receive_data(). It was never
 * NUL-terminated, so it could not be handed to a str* function; since
 * upstream's 76dcd5d it is, and this still takes an explicit length and reads
 * no byte outside it, so it does not depend on that. `data` may be NULL,
 * which is what a 200 with an empty body leaves behind. */
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

/* THE RESPONSE PARSE, split out of crip_fill_accurip() so it runs on a recorded
 * response with no network. It was inline after the fetch, so the one test that
 * reached it, tools/accurip-live-probe.py, had to call accuraterip.com, and a
 * settled fact about this parser was re-checked by somebody else's server
 * (docs/KNOWN-ISSUES.md). tests/arresp.c now parses a real response recorded
 * for the reference disc and checks it against the checksums that disc's rig
 * log matched. Moved, and then changed in two places: the disc status starts
 * at NOT_FOUND, below, and a response of the wrong size is reported by the
 * caller rather than here.
 *
 * That second change is for the provider contract, not the behaviour. The
 * first version of the split logged the size error here and left with a bare
 * `return;`, which tools/gen-provider-contract.py does not count as a jump, so
 * the message dropped out of P5a altogether -- and Platterpus builds its error
 * matcher from P5 and P5a and names this string in a test. Returning an error
 * and letting the caller log it before its `goto end` keeps the row exactly
 * where .17 had it. Found writing round 28 lap 5. */
static int crip_parse_accurip(cyanrip_ctx *ctx, const uint8_t *data, size_t size,
                              int audio_tracks, uint32_t id_type_1,
                              uint32_t id_type_2, uint32_t cddb_id)
{
    GetByteContext gbc = { 0 };
    bytestream2_init(&gbc, data, size);

    /* NOT_FOUND until an entry for this disc is read. This was FOUND, set
     * before the loop, so the MISMATCH arm below could never run: a response
     * holding only other discs' entries, or none, read as found, and the
     * report then printed a tally of 0 of N over a comparison that never
     * happened (docs/KNOWN-ISSUES.md). The same code is in upstream. */
    ctx->ar_db_status = CYANRIP_ACCUDB_NOT_FOUND;

    int entry_size = 1 + 12 + audio_tracks * (1 + 8);

    if (size % entry_size) {
        ctx->ar_db_status = CYANRIP_ACCUDB_ERROR;
        return AVERROR_INVALIDDATA;
    }

    int nb_entries = size / entry_size;

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

        /* One entry per AUDIO track, in order; a data track has none. This
         * walked the first audio_tracks slots of the CD track table and read
         * an entry for a data track too, so on a disc with one, every audio
         * track after it got its neighbour's checksums and the last ones got
         * none. Upstream's e159954 found it on a real mixed mode disc; the
         * same fix, in this function. */
        for (int j = 0; j < ctx->nb_cd_tracks; j++) {
            cyanrip_track *t = &ctx->tracks[j];
            if (t->track_is_data)
                continue;

            int confidence = bytestream2_get_byte(&gbc);
            uint32_t checksum = bytestream2_get_le32(&gbc);
            uint32_t checksum_450 = bytestream2_get_le32(&gbc);

            /* A temporary, so the old block can be freed if the realloc fails.
             * Then nothing read so far is kept: every track goes back to how
             * it was before the parse, as a response of the wrong size leaves
             * them, so no track reads as found from part of a response and
             * none is left unsorted. The rip goes on, as after any AccurateRip
             * failure, with the disc's status an error. */
            CRIPAccuDBEntry *grown = av_realloc(t->ar_db_entries,
                                                sizeof(CRIPAccuDBEntry) * (t->ar_db_nb_entries + 1));
            if (!grown) {
                for (int k = 0; k < ctx->nb_cd_tracks; k++) {
                    cyanrip_track *u = &ctx->tracks[k];
                    av_freep(&u->ar_db_entries);
                    u->ar_db_nb_entries = 0;
                    u->ar_db_max_confidence = 0;
                    u->ar_db_status = CYANRIP_ACCUDB_DISABLED;
                }
                ctx->ar_db_status = CYANRIP_ACCUDB_ERROR;
                return AVERROR(ENOMEM);
            }
            t->ar_db_entries = grown;

            t->ar_db_status = CYANRIP_ACCUDB_FOUND;
            t->ar_db_entries[t->ar_db_nb_entries].confidence = confidence;
            t->ar_db_entries[t->ar_db_nb_entries].checksum = checksum;
            t->ar_db_entries[t->ar_db_nb_entries].checksum_450 = checksum_450;
            t->ar_db_max_confidence = FFMAX(confidence, t->ar_db_max_confidence);

            t->ar_db_nb_entries++;
        }
    }

    for (int i = 0; i < ctx->nb_cd_tracks; i++) {
        cyanrip_track *t = &ctx->tracks[i];
        if (t->ar_db_nb_entries)
            qsort(t->ar_db_entries, t->ar_db_nb_entries, sizeof(CRIPAccuDBEntry), cmp_conf);
    }

    return 0;
}

int crip_fill_accurip(cyanrip_ctx *ctx)
{
    int ret = 0;
    char errbuf[CURL_ERROR_SIZE];
    RecvCtx rctx = { .ctx = ctx };

    if (ctx->settings.disable_accurip)
        return 0;

    CURL *curl_ctx = curl_easy_init();

    /* Get both accurip disc IDs and the FreeDB ID the URL wants */
    uint32_t id_type_1, id_type_2, cddb_id;
    int audio_tracks = crip_get_accurip_ids(ctx, &id_type_1, &id_type_2, &cddb_id);
    if (!audio_tracks) {
        cyanrip_log(ctx, 0, "Disc has no audio tracks, skipping AccuRIP DB!\n");
        goto end;
    }

    /* Format all the data in the needed way */
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

    /* BOUND EVERY TRANSFER. There was no timeout of any kind on any handle,
     * so a server that accepted a connection and then said nothing hung the
     * rip indefinitely -- after the disc had been read, with the drive still
     * open. Platterpus's own §J names "a hang attributable to the ripper" as a
     * defect that would break their pre-commit, and their acceptance run is
     * unattended overnight.
     *
     * Announced as round 15 lap 14 §5 item 6 rather than shipped quietly: a
     * timeout is a TIMING GUARANTEE, which this project's own rules count as
     * contract surface even though the failure reuses the existing
     * curl_easy_strerror() message and adds no new string. Their lap 15 §C3:
     * "sound, and we are not going to argue a peer into weakening their own
     * rule."
     *
     * NOSIGNAL because libcurl's default timeout implementation uses SIGALRM
     * and this program installs its own handlers and runs encoder threads.
     * MAXREDIRS only matters where FOLLOWLOCATION is set, and is set here
     * anyway so a future caller cannot enable one without the other. */
    curl_easy_setopt(curl_ctx, CURLOPT_CONNECTTIMEOUT, 15L);
    curl_easy_setopt(curl_ctx, CURLOPT_TIMEOUT, 60L);
    curl_easy_setopt(curl_ctx, CURLOPT_NOSIGNAL, 1L);
    curl_easy_setopt(curl_ctx, CURLOPT_MAXREDIRS, 8L);
    curl_easy_setopt(curl_ctx, CURLOPT_MAXFILESIZE_LARGE,
                     (curl_off_t)ACCURIP_MAX_BYTES);
    https_only(curl_ctx);

    CURLcode res = curl_easy_perform(curl_ctx);
    if (res != CURLE_OK && rctx.too_big) {
        cyanrip_log(ctx, 0, "Unable to get AccuRIP DB data: the response is "
                    "larger than %i MiB!\n", ACCURIP_MAX_BYTES >> 20);
        ctx->ar_db_status = CYANRIP_ACCUDB_ERROR;
        goto end;
    }
    if (res != CURLE_OK) {
        /* Filter out the majority of 404 errors here */
        if (res == CURLE_HTTP_RETURNED_ERROR) {
            cyanrip_log(ctx, 0, "Unable to get AccuRIP DB data: missing entry!\n");
            ctx->ar_db_status = CYANRIP_ACCUDB_NOT_FOUND;
            goto end;
        }

        /* Different error */
        /* curl's message may end in a newline; the format supplies the one
         * the line ends with, since a newline inside a value is escaped */
        size_t len = strlen(errbuf);
        if (len && errbuf[len - 1] == '\n')
            errbuf[--len] = '\0';
        if (len)
            cyanrip_log(ctx, 0, "Unable to get AccuRIP DB data: %s\n", errbuf);
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
     * A 200 with no body is no entry (upstream's 76dcd5d). content_type is
     * NULL when the response carried no Content-Type header at all, which
     * curl reports as CURLE_OK -- a 200 with no Content-Type is legal HTTP and
     * is what a minimal server or an interposing proxy returns. Treat the
     * absent header as "not the binary type", which is the conservative
     * reading and the one that goes on to check for an error page. */
    if (!rctx.data) {
        cyanrip_log(ctx, 0, "Unable to get AccuRIP DB data: missing entry!\n");
        ctx->ar_db_status = CYANRIP_ACCUDB_NOT_FOUND;
        goto end;
    } else if (!content_type || strcmp(content_type, "application/octet-stream")) {
        /* Atrocious heuristics to determine whether we have an error or binary data, don't look */
        /* The body was never NUL-terminated, so strstr() read off the end
         * of the allocation for any body without a zero byte, and was passed
         * NULL outright when the write callback never fired. Search a bounded
         * window instead, whether or not a NUL now follows the data. The match must START before offset 64, which is what
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

    /* Only a size the entries cannot divide is a data error; a failed
     * allocation says so */
    int perr = crip_parse_accurip(ctx, rctx.data, rctx.size, audio_tracks,
                                  id_type_1, id_type_2, cddb_id);
    if (perr == AVERROR_INVALIDDATA) {
        cyanrip_log(ctx, 0, "AccuRIP DB data error, got unexpected number of bytes!\n");
        goto end;
    } else if (perr < 0) {
        cyanrip_log(ctx, 0, "Unable to read AccuRIP DB data: %s!\n", av_err2str(perr));
        goto end;
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

    /* One comparison per entry, chosen by is_450. This was an if/else-if, so
     * a 450 lookup that missed an entry's frame checksum fell through and
     * compared the one-frame value against its whole-track checksum. */
    for (int i = 0; i < t->ar_db_nb_entries; i++) {
        CRIPAccuDBEntry *e = &t->ar_db_entries[i];
        uint32_t want = is_450 ? e->checksum_450 : e->checksum;
        if (want == checksum)
            return e->confidence;
    }

    return -1;
}
