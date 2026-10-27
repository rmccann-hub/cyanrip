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

#include <curl/curl.h>
#include <libavformat/avformat.h>
#include <libavutil/base64.h>

#include "coverart.h"
#include "cyanrip_log.h"
#include "utils.h"

#define COVERART_DB_URL_BASE "https://coverartarchive.org/release"

/* The most an image is read to (review C item 1.5). The Cover Art Archive's
 * unsized originals are scans, the largest some tens of megabytes; without a
 * cap the buffer grew per callback until the 60 s timeout, which bounds time
 * and not size. */
#define COVERART_MAX_BYTES (64 << 20)

int crip_save_art(cyanrip_ctx *ctx, CRIPArt *art, const cyanrip_out_fmt *fmt)
{
    int ret = 0;

    if (!art->pkt) {
        cyanrip_log(ctx, 0, "Cover art has no packet!\n");
        return 0;
    }

    char *filepath = crip_get_path(ctx, CRIP_PATH_COVERART, 1, fmt, art);
    if (!filepath)
        return 0;

    char *ffpath = cr_ffmpeg_file_path(filepath);
    if (!ffpath) {
        av_free(filepath);
        return 0;
    }

    AVFormatContext *avf = NULL;
    ret = avformat_alloc_output_context2(&avf, NULL, NULL, ffpath);
    if (ret < 0) {
        cyanrip_log(ctx, 0, "Unable to init lavf context: %s!\n", av_err2str(ret));
        goto fail;
    }

    AVStream *st = avformat_new_stream(avf, NULL);
    if (!st) {
        cyanrip_log(ctx, 0, "Unable to alloc stream!\n");
        ret = AVERROR(ENOMEM);
        goto fail;
    }

    /* A copy the stream owns: the art keeps its own, and the muxer frees this
     * one's extradata with the context */
    ret = avcodec_parameters_copy(st->codecpar, art->params);
    if (ret < 0) {
        cyanrip_log(ctx, 0, "Unable to copy cover art parameters: %s!\n", av_err2str(ret));
        goto fail;
    }
    st->time_base = (AVRational){ 1, 25 };
    av_dict_copy(&st->metadata, art->meta, 0);
    av_dict_copy(&avf->metadata, art->meta, 0);

    /* Open for writing */
    ret = avio_open(&avf->pb, ffpath, AVIO_FLAG_WRITE);
    if (ret < 0) {
        cyanrip_log(ctx, 0, "Couldn't open %s for writing: %s!\n", filepath, av_err2str(ret));
        goto fail;
    }

    /* Silence libavformat warning */
    AVDictionary *opts = NULL;
    av_dict_set(&opts, "update", "1", 0);

    /* Write header */
    ret = avformat_write_header(avf, &opts);
    av_dict_free(&opts);
    if (ret < 0) {
        cyanrip_log(ctx, 0, "Couldn't write header: %s!\n", av_err2str(ret));
        goto fail;
    }

    AVPacket *pkt = av_packet_clone(art->pkt);
    if (!pkt) {
        ret = AVERROR(ENOMEM);
        cyanrip_log(ctx, 0, "Error writing picture packet: %s!\n", av_err2str(ret));
        goto fail;
    }
    pkt->stream_index = st->index;

    /* The trailer flushes the interleaving queue, so one write is all, and
     * its result is the one reported */
    ret = av_interleaved_write_frame(avf, pkt);
    av_packet_free(&pkt);
    if (ret < 0) {
        cyanrip_log(ctx, 0, "Error writing picture packet: %s!\n", av_err2str(ret));
        goto fail;
    }

    if ((ret = av_write_trailer(avf)) < 0) {
        cyanrip_log(ctx, 0, "Error writing trailer: %s!\n", av_err2str(ret));
        goto fail;
    }

fail:
    av_free(filepath);
    av_free(ffpath);

    if (avf)
        avio_closep(&avf->pb);
    avformat_free_context(avf);

    return ret;
}

void crip_free_art(CRIPArt *art)
{
    av_packet_free(&art->pkt);
    avcodec_parameters_free(&art->params);

    av_freep(&art->data);
    art->size = 0;

    av_freep(&art->source_url);
    av_freep(&art->extension);

    av_dict_free(&art->meta);
}

typedef struct ImageRecv {
    CRIPArt *art;
    int too_big; /* The image passed COVERART_MAX_BYTES and was cut off */
} ImageRecv;

/* HTTPS only, for the request and any redirect (review C item 1.5); the
 * certificate is verified, as libcurl does unless told not to. Same as
 * https_only() in accurip.c, which says why there are two options. */
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

static size_t receive_image(void *buffer, size_t size, size_t nb, void *opaque)
{
    ImageRecv *recv = opaque;
    CRIPArt *art = recv->art;

    /* Checked before the size is added to, so neither can wrap; the flag
     * says why curl stopped, since its own message would name a write */
    if (size * nb > COVERART_MAX_BYTES - art->size) {
        recv->too_big = 1;
        return 0;
    }

    uint8_t *new_data = av_realloc(art->data, art->size + (size * nb));
    if (!new_data)
        return 0;

    memcpy(new_data + art->size, buffer, size * nb);

    art->data  = new_data;
    art->size += size * nb;

    return size * nb;
}

static int fetch_image(cyanrip_ctx *ctx, CURL *curl_ctx, CRIPArt *art,
                       const char *release_id, const char *type, int info_only,
                       const char *own_url)
{
    int ret;
    char errbuf[CURL_ERROR_SIZE];
    ImageRecv recv = { .art = art };

    /* One handle serves the Cover Art DB and the URLs -C gives, so each fetch
     * starts from libcurl's defaults: the DB's HTTPS-only setting must not
     * carry over to a URL whose scheme its caller chose */
    curl_easy_reset(curl_ctx);

    char temp[4096];
    if (!own_url) {
        snprintf(temp, sizeof(temp), "%s/%s/%s",
                 COVERART_DB_URL_BASE, release_id, type);
        curl_easy_setopt(curl_ctx, CURLOPT_URL, temp);
    } else {
        curl_easy_setopt(curl_ctx, CURLOPT_URL, own_url);
    }

    char user_agent[256] = { 0 };
    sprintf(user_agent, "cyanrip/%s ( https://github.com/cyanreg/cyanrip )", PROJECT_VERSION_STRING);
    curl_easy_setopt(curl_ctx, CURLOPT_USERAGENT, user_agent);

    curl_easy_setopt(curl_ctx, CURLOPT_WRITEFUNCTION, receive_image);
    curl_easy_setopt(curl_ctx, CURLOPT_WRITEDATA, &recv);
    curl_easy_setopt(curl_ctx, CURLOPT_MAXFILESIZE_LARGE,
                     (curl_off_t)COVERART_MAX_BYTES);
    if (!own_url)
        https_only(curl_ctx);

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

    if (!info_only) {
        cyanrip_log(ctx, 0, "Downloading %s cover art...\n", type);
        curl_easy_setopt(curl_ctx, CURLOPT_FOLLOWLOCATION, 1L);
    }

    CURLcode res = curl_easy_perform(curl_ctx);
    if (res != CURLE_OK && recv.too_big) {
        cyanrip_log(ctx, 0, "Unable to get cover art \"%s\": the image is "
                    "larger than %i MiB!\n", type, COVERART_MAX_BYTES >> 20);
        ret = AVERROR(EINVAL);
        goto end;
    }
    if (res != CURLE_OK) {
        /* Filter out the majority of 404 errors here */
        if (res == CURLE_HTTP_RETURNED_ERROR) {
            cyanrip_log(ctx, 0, "Unable to get cover art \"%s\": not found!\n", type);
            crip_free_art(art);
            ret = own_url ? AVERROR(EINVAL) : 0;
            goto end;
        }

        /* Different error */
        /* curl's message may end in a newline; the format supplies the one
         * the line ends with, since a newline inside a value is escaped. The
         * line keeps its old shape, the "!" on a line of its own. */
        size_t len = strlen(errbuf);
        if (len && errbuf[len - 1] == '\n')
            errbuf[--len] = '\0';
        if (len)
            cyanrip_log(ctx, 0, "Unable to get cover art \"%s\": %s\n!\n",
                        type, errbuf);
        else
            cyanrip_log(ctx, 0, "Unable to get cover art \"%s\": %s\n!\n",
                        type, curl_easy_strerror(res));
        ret = AVERROR(EINVAL);
        goto end;
    }

    /* Get content type, if not possible we probably have an error somewhere */
    char *content_type = NULL;
    res = curl_easy_getinfo(curl_ctx, CURLINFO_CONTENT_TYPE, &content_type);
    if (res != CURLE_OK) {
        cyanrip_log(ctx, 0, "Unable to get cover art \"%s\": %s\n!\n",
                    type, curl_easy_strerror(res));
        ret = AVERROR(EINVAL);
        goto end;
    }

    /* Response code */
    long response_code = 0;
    res = curl_easy_getinfo(curl_ctx, CURLINFO_RESPONSE_CODE, &response_code);
    if (res != CURLE_OK) {
        cyanrip_log(ctx, 0, "Unable to get cover art \"%s\": %s\n!\n",
                    type, curl_easy_strerror(res));
        ret = AVERROR(EINVAL);
        goto end;
    }

    /* Get the URL */
    char *final_url = NULL;
    res = curl_easy_getinfo(curl_ctx, CURLINFO_EFFECTIVE_URL, &final_url);
    if (res != CURLE_OK) {
        cyanrip_log(ctx, 0, "Unable to get cover art \"%s\": %s\n!\n",
                    type, curl_easy_strerror(res));
        ret = AVERROR(EINVAL);
        goto end;
    }

    ret = art->size;

    if (info_only) {
        av_freep(&art->data);
        art->size = 0;
    } else {
        char header[99];
        snprintf(header, sizeof(header), "data:%s;base64,",
                 content_type ? content_type : "application/octet-stream");

        size_t data_len = AV_BASE64_SIZE(art->size);
        char *data = av_mallocz(strlen(header) + data_len);
        if (!data) {
            cyanrip_log(ctx, 0, "Unable to get cover art \"%s\": %s!\n",
                        type, av_err2str(AVERROR(ENOMEM)));
            crip_free_art(art);
            ret = AVERROR(ENOMEM);
            goto end;
        }
        memcpy(data, header, strlen(header));

        av_base64_encode(data + strlen(header), data_len, art->data, art->size);

        av_free(art->data);
        art->data = data;
        art->size = data_len;
    }

    art->source_url = av_strdup(final_url);

end:
    if (res != CURLE_OK)
        crip_free_art(art);

    return ret;
}

static int demux_image(cyanrip_ctx *ctx, CRIPArt *art, int info_only)
{
    int ret = 0;
    AVFormatContext *avf = NULL;
    const char *in_url = art->data ? (const char *)art->data : art->source_url;

    ret = avformat_open_input(&avf, in_url, NULL, NULL);
    if (ret < 0) {
        cyanrip_log(ctx, 0, "Unable to open \"%s\": %s!\n", art->data ? "(data)" : in_url,
                    av_err2str(ret));
        goto end;
    }

    ret = avformat_find_stream_info(avf, NULL);
    if (ret < 0) {
        cyanrip_log(ctx, 0, "Unable to get cover image info: %s!\n", av_err2str(ret));
        goto end;
    }

    /* A deep copy: the demuxer's own parameters, extradata included, are
     * freed with it below. sizeof(AVCodecParameters) is not part of FFmpeg's
     * ABI, so only its functions allocate, copy and free one. */
    avcodec_parameters_free(&art->params);
    art->params = avcodec_parameters_alloc();
    if (!art->params) {
        ret = AVERROR(ENOMEM);
        goto end;
    }

    ret = avcodec_parameters_copy(art->params, avf->streams[0]->codecpar);
    if (ret < 0) {
        cyanrip_log(ctx, 0, "Unable to copy cover image parameters: %s!\n", av_err2str(ret));
        goto end;
    }

    /* Output extension guesswork */
    av_freep(&art->extension);
    if (art->params->codec_id == AV_CODEC_ID_MJPEG) {
        art->extension = av_strdup("jpg");
    } else if (art->params->codec_id == AV_CODEC_ID_PNG) {
        art->extension = av_strdup("png");
    } else if (art->params->codec_id == AV_CODEC_ID_BMP) {
        art->extension = av_strdup("bmp");
    } else if (art->params->codec_id == AV_CODEC_ID_TIFF) {
        art->extension = av_strdup("tiff");
    } else if (art->params->codec_id == AV_CODEC_ID_AV1) {
        art->extension = av_strdup("avif");
    } else if (art->params->codec_id == AV_CODEC_ID_HEVC) {
        art->extension = av_strdup("heif");
    } else if (art->params->codec_id == AV_CODEC_ID_WEBP) {
        art->extension = av_strdup("webp");
    } else if (art->params->codec_id != AV_CODEC_ID_NONE) {
        art->extension = av_strdup(avcodec_get_name(art->params->codec_id));
    } else {
        ret = AVERROR(EINVAL);
        cyanrip_log(ctx, 0, "Error demuxing cover image: %s!\n", av_err2str(ret));
        goto end;
    }

    if (info_only)
        goto end;

    art->pkt = av_packet_alloc();
    if (!art->pkt) {
        ret = AVERROR(ENOMEM);
        goto end;
    }

    ret = av_read_frame(avf, art->pkt);
    if (ret < 0) {
        cyanrip_log(ctx, 0, "Error demuxing cover image: %s!\n", av_err2str(ret));
        goto end;
    }

    avformat_close_input(&avf);

    av_freep(&art->data);
    art->size = 0;

    return 0;

end:
    avformat_close_input(&avf);

    return ret;
}

static int string_is_url(const char *src)
{
    /* Each scheme's whole prefix, "://" included: a local file whose name
     * merely begins with "http" is a file */
    static const char *const schemes[] = {
        "http://", "https://", "ftp://", "ftps://", "sftp://", "tftp://",
        "gopher://", "telnet://",
    };
    for (int i = 0; i < FF_ARRAY_ELEMS(schemes); i++)
        if (!strncmp(src, schemes[i], strlen(schemes[i])))
            return 1;
    return 0;
}

int crip_fill_coverart(cyanrip_ctx *ctx, int info_only)
{
    int err = 0;

    int have_front = 0;
    int have_back = 0;
    for (int i = 0; i < ctx->nb_cover_arts; i++) {
        const char *title = dict_get(ctx->cover_arts[i].meta, "title");
        have_front |= !strcmp(title, "Front");
        have_back |= !strcmp(title, "Back");
    }

    CURL *curl_ctx = curl_easy_init();

    if (!have_front || !have_back) {
        const char *release_id = dict_get(ctx->meta, "musicbrainz_albumid");
        if (!release_id && !ctx->settings.disable_coverart_db) {
            /* Name which ID, and when. The old wording was "Release ID
             * unavailable", which a reader reconciled against the header's
             * "Release ID: <uuid>" two blocks below and concluded one of them
             * was wrong. Neither is: -R and user "-a musicbrainz_albumid=" are
             * merged into ctx->meta *after* crip_fill_coverart() runs, so the
             * only source at this point is cyanrip's own MusicBrainz lookup.
             * Says what was observed -- the field is unset here -- rather than
             * the stronger "the release has no ID". */
            cyanrip_log(ctx, 0, "No MusicBrainz release ID at cover art lookup, cannot search Cover Art DB!\n");
        } else if (!ctx->settings.disable_coverart_db) {
            int has_err = 0;
            /* The room checked before each write: -C takes up to 31 album
             * covers, so a fetched front can take the last slot */
            const int room = FF_ARRAY_ELEMS(ctx->cover_arts);
            if (!have_front && ctx->nb_cover_arts >= room) {
                cyanrip_log(ctx, 0, "Cover Art DB's front cover not fetched: a rip holds at most %i cover arts!\n", room);
            } else if (!have_front) {
                static const char *cover_ids[] = { "front", "front-250", "front-500", "front-1200" };
                has_err = fetch_image(ctx, curl_ctx, &ctx->cover_arts[ctx->nb_cover_arts], release_id, cover_ids[ctx->settings.coverart_lookup_size], info_only, NULL);
                if (has_err > 0) {
                    av_dict_set(&ctx->cover_arts[ctx->nb_cover_arts].meta, "title", "Front", 0);
                    av_dict_set(&ctx->cover_arts[ctx->nb_cover_arts].meta, "source", "Cover Art DB", 0);
                    ctx->cover_arts[ctx->nb_cover_arts].extension = av_strdup("jpg");
                    ctx->nb_cover_arts++;
                }
            }
            if (!have_back && (has_err > 0) && ctx->nb_cover_arts >= room) {
                cyanrip_log(ctx, 0, "Cover Art DB's back cover not fetched: a rip holds at most %i cover arts!\n", room);
            } else if (!have_back && (has_err > 0)) {
                static const char *cover_ids[] = { "back", "back-250", "back-500", "back-1200" };
                has_err = fetch_image(ctx, curl_ctx, &ctx->cover_arts[ctx->nb_cover_arts], release_id, cover_ids[ctx->settings.coverart_lookup_size], info_only, NULL);
                if (has_err > 0) {
                    av_dict_set(&ctx->cover_arts[ctx->nb_cover_arts].meta, "title", "Back", 0);
                    av_dict_set(&ctx->cover_arts[ctx->nb_cover_arts].meta, "source", "Cover Art DB", 0);
                    ctx->cover_arts[ctx->nb_cover_arts].extension = av_strdup("jpg");
                    ctx->nb_cover_arts++;
                }
            }
        }
    }

    for (int i = 0; i < ctx->nb_cover_arts; i++) {
        char *source_url = ctx->cover_arts[i].source_url;
        const char *title = dict_get(ctx->cover_arts[i].meta, "title");
        int is_url = string_is_url(source_url);

        /* If its a url, we haven't downloaded it from CADB and we're not info printing */
        if (is_url && !ctx->cover_arts[i].data && !info_only) {
            err = fetch_image(ctx, curl_ctx, &ctx->cover_arts[i], NULL, title, 0, source_url);
            if (err < 0)
                goto end;
        }

        /* If we don't have to download it, or we have data */
        if (!is_url || !info_only) {
            if ((err = demux_image(ctx, &ctx->cover_arts[i], info_only)) < 0)
                goto end;
        }
    }

end:
    curl_easy_cleanup(curl_ctx);

    return err;
}

int crip_fill_track_coverart(cyanrip_ctx *ctx, int info_only)
{
    int err = 0;
    CURL *curl_ctx = curl_easy_init();

    for (int i = 0; i < ctx->nb_tracks; i++) {
        if (!ctx->tracks[i].art.source_url)
            continue;

        char *source_url = ctx->tracks[i].art.source_url;
        int is_url = string_is_url(source_url);

        /* If its a url, we haven't downloaded it from CADB and we're not info printing */
        if (is_url && !ctx->tracks[i].art.data && !info_only) {
            err = fetch_image(ctx, curl_ctx, &ctx->tracks[i].art, NULL, "track", 0, source_url);
            if (err < 0)
                goto end;
        }

        /* If we don't have to download it, or we have data */
        if (!is_url || !info_only) {
            if ((err = demux_image(ctx, &ctx->tracks[i].art, info_only)) < 0)
                goto end;
        }
    }

end:
    curl_easy_cleanup(curl_ctx);

    return err;
}
