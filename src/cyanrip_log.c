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

#include <stdarg.h>
#include <time.h>
#include <pthread.h>

#include <libavutil/avutil.h>
#include <libavformat/avformat.h>
#include <libavutil/sha512.h>
#include <libavutil/base64.h>

#include "cyanrip_encode.h"
#include "cyanrip_log.h"
#include "fun512.h"
#include "accurip.h"

#define CLOG(FORMAT, DICT, TAG)                                                \
    if (dict_get(DICT, TAG))                                                   \
        cyanrip_log(ctx, 0, FORMAT, dict_get(DICT, TAG));                      \

/* Prints one CD-TEXT dictionary as an aligned key: value block, matching the
 * Metadata block's layout. Returns nothing; an empty dictionary prints
 * nothing, so callers decide whether a heading is warranted. */
static void print_cdtext_fields(cyanrip_ctx *ctx, AVDictionary *cdtext,
                                const char *indent)
{
    int max_key_len = 0;
    const AVDictionaryEntry *d = NULL;
    while ((d = av_dict_get(cdtext, "", d, AV_DICT_IGNORE_SUFFIX)))
        max_key_len = FFMAX(strlen(d->key), max_key_len);

    d = NULL;
    while ((d = av_dict_get(cdtext, "", d, AV_DICT_IGNORE_SUFFIX))) {
        cyanrip_log(ctx, 0, "%s%s: ", indent, d->key);
        for (int i = 0; i < (max_key_len - (int)strlen(d->key)); i++)
            cyanrip_log(ctx, 0, " ");
        cyanrip_log(ctx, 0, "%s\n", d->value);
    }
}

static void print_cdtext(cyanrip_ctx *ctx)
{
    if (ctx->cdtext_status != CYANRIP_CDTEXT_PRESENT) {
        /* Not "the disc has none": libcdio returns the same nothing for a disc
         * without a CD-TEXT block and for a driver that cannot read one, and
         * exposes no way to tell the two apart. Say what was observed. */
        cyanrip_log(ctx, 0, "CD-TEXT:        none reported by libcdio "
                            "(absent, or unreadable by this driver)\n");
        return;
    }

    cyanrip_log(ctx, 0, "CD-TEXT:        present (%s, %i disc %s, %i of %i tracks tagged)\n",
                ctx->cdtext_language ? ctx->cdtext_language : "unknown language",
                ctx->cdtext_nb_disc_fields,
                ctx->cdtext_nb_disc_fields == 1 ? "field" : "fields",
                ctx->cdtext_nb_tagged_tracks, ctx->nb_tracks);

    print_cdtext_fields(ctx, ctx->cdtext, "    ");
}

/* Paranoia defeats a drive's read cache by modelling its size and seeking back
 * further than that before a re-read. Report the model that is in force.
 *
 * The label is "Cache model", not "Cache defeat", and deliberately not EAC's
 * "Defeat audio cache : Yes". We report the size paranoia *models*; we never
 * probe the drive for its real cache the way cd-paranoia -A does. A field named
 * for the defeating would assert an outcome no part of this run established,
 * and a reader who greps the field name would be entitled to believe it -- the
 * qualifier in the value cannot undo a claim the label already made. */
static void print_cache_model(cyanrip_ctx *ctx)
{
    if (!ctx->paranoia || !ctx->settings.paranoia_level) {
        cyanrip_log(ctx, 0, "Cache model:    not in use (paranoia disabled)\n");
        return;
    }

    /* -1 queries without setting, so this does not disturb the rip. */
    const int sectors = cdio_paranoia_cachemodel_size(ctx->paranoia, -1);

    switch (cdio_get_driver_id(ctx->cdio)) {
    case DRIVER_BINCUE:
    case DRIVER_NRG:
    case DRIVER_CDRDAO:
        cyanrip_log(ctx, 0, "Cache model:    %i sector%s "
                            "(disc image, no drive cache)\n",
                    sectors, sectors == 1 ? "" : "s");
        break;
    default:
        cyanrip_log(ctx, 0, "Cache model:    %i sector%s "
                            "(drive cache size not probed)\n",
                    sectors, sectors == 1 ? "" : "s");
        break;
    }
}

/* Prints the paranoia callback counters that are non-zero, aligned on the
 * longest name. Shared by the disc summary and the per-track block so the two
 * cannot drift apart in wording or padding. Returns how many were printed, so
 * a caller can tell "all zero" from "printed nothing". */
static int print_paranoia_counts(cyanrip_ctx *ctx, const uint64_t *counts,
                                 const char *indent)
{
    int printed = 0;

#define PCHECK(PROP)                                                           \
    if (counts[PARANOIA_CB_ ## PROP]) {                                        \
        const char *pstr = #PROP ": ";                                         \
        cyanrip_log(ctx, 0, "%s%s", indent, pstr);                             \
        int padding = strlen("FIXUP_DROPPED: ") - strlen(pstr);                \
        for (int i = 0; i < padding; i++)                                      \
            cyanrip_log(ctx, 0, " ");                                          \
        cyanrip_log(ctx, 0, "%lu\n", counts[PARANOIA_CB_ ## PROP]);            \
        printed++;                                                             \
    }

    PCHECK(READ)
    PCHECK(VERIFY)
    PCHECK(FIXUP_EDGE)
    PCHECK(FIXUP_ATOM)
    PCHECK(SCRATCH)
    PCHECK(REPAIR)
    PCHECK(SKIP)
    PCHECK(DRIFT)
    PCHECK(BACKOFF)
    PCHECK(OVERLAP)
    PCHECK(FIXUP_DROPPED)
    PCHECK(FIXUP_DUPED)
    PCHECK(READERR)
    PCHECK(CACHEERR)
    PCHECK(WROTE)
    PCHECK(FINISHED)

#undef PCHECK

    return printed;
}

static void print_offsets(cyanrip_ctx *ctx, cyanrip_track *t)
{
    if (t->pregap_lsn != CDIO_INVALID_LSN) {
        char pregap_duration[16];
        /* 2-second lead-in is conventionally counted as part of track 1 pre-gap duration.
         * It physically occupies LSN -150..-1, so it cannot be expressed by the pregap
         * LSN itself, which is 0 for track 1 -- only the length below carries it. */
        const int lead_in_sectors = 2*75;
        int pregap_frames = t->start_lsn_sig - t->pregap_lsn;
        if (t->number == 1)
            pregap_frames += lead_in_sectors;

        cyanrip_frames_to_duration(pregap_frames, pregap_duration);

        cyanrip_log(ctx, 0, "    Pregap LSN:  %i (duration: %s)\n",
                    t->pregap_lsn, pregap_duration);
        cyanrip_log(ctx, 0, "    Pregap length: %i frames\n", pregap_frames);
    } else if (t->pregap_source == CYANRIP_PREGAP_SRC_ERR_READ) {
        cyanrip_log(ctx, 0, "    Pregap LSN:  unknown (sub-channel unreadable)\n");
    } else if (t->pregap_source == CYANRIP_PREGAP_SRC_ERR_CRC) {
        cyanrip_log(ctx, 0, "    Pregap LSN:  unknown (sub-channel CRC mismatches)\n");
    } else {
        cyanrip_log(ctx, 0, "    Pregap LSN:  none\n");
    }

    /* Say where a pregap came from when it wasn't the TOC, so a reader can
     * tell a value this drive worked out from one the disc declared. */
    if (t->pregap_source == CYANRIP_PREGAP_SRC_SUBCHANNEL)
        cyanrip_log(ctx, 0, "    Pregap source: sub-channel (not signalled by TOC)\n");
    else if (t->pregap_source == CYANRIP_PREGAP_SRC_LEADIN)
        cyanrip_log(ctx, 0, "    Pregap source: lead-in\n");
    else if (t->pregap_source == CYANRIP_PREGAP_SRC_TOC)
        cyanrip_log(ctx, 0, "    Pregap source: TOC\n");

    if (t->frames_before_disc_start)
        cyanrip_log(ctx, 0, "    Prepended:   %i frames of silence\n", t->frames_before_disc_start);
    cyanrip_log(ctx, 0,     "    Start LSN:   %i", t->start_lsn_sig);
    if (t->start_lsn != t->start_lsn_sig)
        cyanrip_log(ctx, 0, " (with offset: %i)\n", t->start_lsn);
    else
        cyanrip_log(ctx, 0, "\n");

    cyanrip_log(ctx, 0,     "    End LSN:     %i", t->end_lsn_sig);
    if (t->end_lsn != t->end_lsn_sig)
        cyanrip_log(ctx, 0, " (with offset: %i)\n", t->end_lsn);
    else
        cyanrip_log(ctx, 0, "\n");

    if (t->frames_after_disc_end)
        cyanrip_log(ctx, 0, "    Appended:    %i frames of silence\n", t->frames_after_disc_end);
}

void cyanrip_log_track_end(cyanrip_ctx *ctx, cyanrip_track *t)
{
    char length[16];

    /* From nb_samples, not t->frames. setup_track_lsn() widens t->frames by a
     * frame at whichever end the read offset shifts into, so with a nonzero -s
     * an interior track's t->frames is one greater than the track really is and
     * the duration printed a frame (13.3 ms) long. The sample count is
     * deliberately taken before that adjustment, which is why the same log
     * simultaneously reported "Samples: 176400" (exactly 00:04.00) and
     * "Duration: 00:04.01". Found on bovinemagnet/cyanrip 3eb6e22 and
     * reproduced here.
     *
     * The error is not always +1. The offset shifts both ends of the range; a
     * track clamped at a disc boundary has the shift removed at one end only,
     * so its error inverts -- measured -1 on the last track at -s +667 and on
     * the first track at -s -667. Anything that "adds a frame back" is
     * therefore wrong on the boundary track of every disc.
     *
     * Not from end_lsn_sig - start_lsn_sig either, which is what the Frames:
     * line below prints: those are captured from the raw TOC before pregap
     * merging and lead-out padding move start_lsn/end_lsn, so for a merged
     * pregap they describe a different span than was ripped. nb_samples is
     * computed after the merge and before the offset, which is exactly the
     * span whose duration this is. */
    cyanrip_frames_to_duration(t->nb_samples / (CDIO_CD_FRAMESIZE_RAW >> 2),
                               length);

    cyanrip_log(ctx, 0, "  Preemphasis:   ");
    if (!t->preemphasis) {
        cyanrip_log(ctx, 0, "none detected");

        if (ctx->settings.force_deemphasis)
            cyanrip_log(ctx, 0, " (deemphasis forced)\n");
        else
            cyanrip_log(ctx, 0, "\n");
    } else {
        if (t->preemphasis_in_subcode)
            cyanrip_log(ctx, 0, "present (subcode)");
        else
            cyanrip_log(ctx, 0, "present (TOC)");

        if (ctx->settings.deemphasis || ctx->settings.force_deemphasis)
            cyanrip_log(ctx, 0, " (deemphasis applied)\n");
        else
            cyanrip_log(ctx, 0, "\n");
    }

    cyanrip_log(ctx, 0, "\n  Properties:\n");

    if (t->track_is_data) {
        cyanrip_log(ctx, 0, "    Data bytes:  %i (%.2f Mib)\n",
                    t->frames*CDIO_CD_FRAMESIZE_RAW,
                    t->frames*CDIO_CD_FRAMESIZE_RAW / (1024.0 * 1024.0));
        cyanrip_log(ctx, 0, "    Frames:      %u\n", t->end_lsn_sig - t->start_lsn_sig + 1);
        print_offsets(ctx, t);
        cyanrip_log(ctx, 0, "\n");
        return;
    }

    cyanrip_log(ctx, 0, "    Duration:    %s\n", length);
    cyanrip_log(ctx, 0, "    Samples:     %u\n", t->nb_samples);
    cyanrip_log(ctx, 0, "    Frames:      %u\n", t->end_lsn_sig - t->start_lsn_sig + 1);
    if (t->computed_crcs) {
        /* "Sample peak level", not "Peak level": a bare "Peak level" does not
         * say *which* peak, and a true peak is reported directly below it.
         * Both are named "... peak level" rather than "... peak" so neither can
         * be confused with libavfilter's own "  Sample peak:" / "  True peak:"
         * headings, which are FFmpeg's wording and move when FFmpeg does. */
        cyanrip_log(ctx, 0, "    Sample peak level: %.1f%% (%.1f dBFS)\n",
                    100.0 * pow(10.0, t->ebu_sample_peak / 20.0),
                    t->ebu_sample_peak);
        cyanrip_log(ctx, 0, "    True peak level:   %.1f dBFS\n", t->ebu_true_peak);
        /* EBU R128 loudness, ours rather than libavfilter's. The values were
         * already computed and held per track and then discarded -- the same
         * dead-field shape as the sample and true peaks above. Until now the
         * only place a consumer could read integrated loudness or loudness
         * range was FFmpeg's own summary block, whose wording is not ours and
         * moves when FFmpeg does (Platterpus, round 5 A5).
         *
         * "(R128)" is not decoration. libavfilter's own summary block already
         * prints headings spelled exactly "Integrated loudness:" and "Loudness
         * range:", so an unqualified label here would collide with it and a
         * consumer grepping the field name would match two different lines --
         * the same defect that made a bare "Peak level" ambiguous once a true
         * peak was printed beneath it.
         *
         * Units are not interchangeable: loudness is LUFS (absolute), range is
         * LU (a difference), and the LRA bounds are LUFS again. */
        cyanrip_log(ctx, 0, "    Integrated loudness (R128): %.1f LUFS\n",
                    t->ebu_integrated);
        cyanrip_log(ctx, 0, "    Loudness range (R128):      %.1f LU (%.1f to %.1f LUFS)\n",
                    t->ebu_range, t->ebu_lra_low, t->ebu_lra_high);
    }
    if (t->rip_time_us > 0) {
        cyanrip_log(ctx, 0, "    Extraction speed:  %.1fx\n",
                    (t->frames / 75.0) / (t->rip_time_us / 1000000.0));
        cyanrip_log(ctx, 0, "    Elapsed:            %.2f s\n", t->rip_time_us / 1000000.0);
    }

    print_offsets(ctx, t);

    int has_ar = t->ar_db_status == CYANRIP_ACCUDB_FOUND;

    if (t->computed_crcs) {
        cyanrip_log(ctx, 0, "\n  EAC CRC32:     %08X", t->eac_crc);
        if (t->total_repeats)
            cyanrip_log(ctx, 0, " (after %i rips)\n", t->total_repeats);
        else
            cyanrip_log(ctx, 0, "\n");
    }

    switch (t->secure_rip_state) {
    case CYANRIP_SECURE_RIP_CONVERGED:
        cyanrip_log(ctx, 0, "  Secure re-read:  converged after %i reads\n", t->total_repeats);
        break;
    case CYANRIP_SECURE_RIP_LIMIT_HIT:
        cyanrip_log(ctx, 0, "  Secure re-read:  did NOT converge after %i reads (repeat limit hit)\n",
                    t->total_repeats);
        break;
    case CYANRIP_SECURE_RIP_NA:
    default:
        cyanrip_log(ctx, 0, "  Secure re-read:  not attempted\n");
        break;
    }

    cyanrip_log(ctx, 0, "  Accurip:       %s",
                ctx->settings.disable_accurip ? "disabled" :
                has_ar ? "disc found in database" : "not found");
    if (has_ar)
        cyanrip_log(ctx, 0, " (max confidence: %i)\n", t->ar_db_max_confidence);
    else
        cyanrip_log(ctx, 0, "\n");

    if (t->computed_crcs) {
        int match_v1 = has_ar ? crip_find_ar(t, t->acurip_checksum_v1, 0) : 0;
        int match_v2 = has_ar ? crip_find_ar(t, t->acurip_checksum_v2, 0) : 0;

        cyanrip_log(ctx, 0, "    Accurip v1:  %08X", t->acurip_checksum_v1);
        if (has_ar && match_v1 > 0)
            cyanrip_log(ctx, 0, " (accurately ripped, confidence %i)\n", match_v1);
        else if (has_ar && (match_v2 < 1))
            cyanrip_log(ctx, 0, " (not found, either a new pressing, or bad rip)\n");
        else
            cyanrip_log(ctx, 0, "\n");

        cyanrip_log(ctx, 0, "    Accurip v2:  %08X", t->acurip_checksum_v2);
        if (has_ar && (match_v2 > 0))
            cyanrip_log(ctx, 0, " (accurately ripped, confidence %i)\n", match_v2);
        else if (has_ar && (match_v1 < 0))
            cyanrip_log(ctx, 0, " (not found, either a new pressing, or bad rip)\n");
        else
            cyanrip_log(ctx, 0, "\n");

        if (!has_ar || ((match_v1 < 0) && (match_v2 < 0))) {
            int match_450 = has_ar ? crip_find_ar(t, t->acurip_checksum_v1_450, 1) : 0;

            cyanrip_log(ctx, 0, "    Accurip 450: %08X", t->acurip_checksum_v1_450);
            if (has_ar && (match_450 > (3*(t->ar_db_max_confidence+1)/4)) && (t->acurip_checksum_v1_450 == 0x0)) {
                cyanrip_log(ctx, 0, " (match found, confidence %i, but a checksum of 0 is meaningless)\n",
                            match_450, t->ar_db_max_confidence);
            } else if (has_ar && (match_450 > (3*(t->ar_db_max_confidence+1)/4))) {
                cyanrip_log(ctx, 0, " (matches Accurip DB, confidence %i, track is partially accurately ripped)\n",
                            match_450, t->ar_db_max_confidence);
            } else if (has_ar) {
                cyanrip_log(ctx, 0, " (not found)\n");
            } else {
                cyanrip_log(ctx, 0, "\n");
            }
        }
    }

    cyanrip_log(ctx, 0, "\n  Metadata:\n", length);

    int max_key_len = 0;
    const AVDictionaryEntry *d = NULL;
    while ((d = av_dict_get(t->meta, "", d, AV_DICT_IGNORE_SUFFIX)))
        max_key_len = FFMAX(strlen(d->key), max_key_len);

    d = NULL;
    while ((d = av_dict_get(t->meta, "", d, AV_DICT_IGNORE_SUFFIX))) {
        int key_len = strlen(d->key);
        cyanrip_log(ctx, 0, "    %s: ", d->key);
        for (int i = 0; i < (max_key_len - key_len); i++)
            cyanrip_log(ctx, 0, " ");
        cyanrip_log(ctx, 0, "%s\n", d->value);
    }

    /* The disc's own words for this track, verbatim and separate from the
     * Metadata block above, which by now may have been overwritten by
     * MusicBrainz or by a -t value. Absent when the disc tagged no fields for
     * this track -- the disc-level CD-TEXT line says how many tracks were
     * tagged, so a missing block here is not ambiguous. */
    if (av_dict_count(t->cdtext)) {
        cyanrip_log(ctx, 0, "\n  CD-TEXT:\n");
        print_cdtext_fields(ctx, t->cdtext, "    ");
    }

    /* This track's share of the disc's paranoia work. The disc-level totals at
     * the end say how much effort the rip cost; these say which track cost it,
     * which is the difference between "this disc needed 1749 verifies" and
     * "track 3 needed 1400 of them". Counts include every -Z re-read of this
     * track. Data tracks are read outside paranoia, so they have none. */
    if (!t->track_is_data) {
        cyanrip_log(ctx, 0, "\n  Paranoia status counts:\n");
        if (!print_paranoia_counts(ctx, t->paranoia_status, "    "))
            cyanrip_log(ctx, 0, "    none\n");
    }

    if (!ctx->settings.disable_coverart_embedding && (t->art.source_url || ctx->nb_cover_arts)) {
        const char *codec_name = NULL;
        CRIPArt *art = &t->art;
        if (!art->source_url) {
            int i;
            for (i = 0; i < ctx->nb_cover_arts; i++)
                if (!strcmp(dict_get(ctx->cover_arts[i].meta, "title"), "Front"))
                    break;
            art = &ctx->cover_arts[i == ctx->nb_cover_arts ? 0 : i];
        }

        if (art->pkt && art->params) {
            const AVCodecDescriptor *cd = avcodec_descriptor_get(art->params->codec_id);
            if (cd)
                codec_name = cd->long_name;
            else
                codec_name = avcodec_get_name(art->params->codec_id);
        }

        if (ctx->settings.print_info_only)
            cyanrip_log(ctx, 0, "\n  Embedded cover art:\n    %s: %s\n",
                        dict_get(art->meta, "title"), art->source_url);
        else
            cyanrip_log(ctx, 0, "\n  Embedded cover art:\n    %s: %ix%i %s\n",
                        dict_get(art->meta, "title"), art->params->width, art->params->height, codec_name);
    }

    cyanrip_log(ctx, 0, "\n  File(s):\n");
    for (int f = 0; f < ctx->settings.outputs_num; f++) {
        char *path = crip_get_path(ctx, CRIP_PATH_TRACK, 0,
                                   &crip_fmt_info[ctx->settings.outputs[f]],
                                   t);
        cyanrip_log(ctx, 0, "    %s\n", path);
        av_free(path);
    }

    cyanrip_log(ctx, 0, "\n");
}

void cyanrip_log_start_report(cyanrip_ctx *ctx)
{
    cyanrip_log(ctx, 0, "cyanrip %s (%s-g%s)\n", PROJECT_VERSION_STRING,
                PROJECT_FORK_ID, vcstag);
    if (crip_invocation)
        cyanrip_log(ctx, 0, "Invoked as:     %s\n", crip_invocation);
    cdio_hwinfo_t hwinfo;
    const int hwinfo_success = cdio_get_hwinfo(ctx->cdio, &hwinfo);
    if (!hwinfo_success)
        cyanrip_log(ctx, 0, "Drive used:     error retrieving drive info\n");
    else
        cyanrip_log(ctx, 0, "Drive used:     %s %s (revision %s)\n", hwinfo.psz_vendor, hwinfo.psz_model, hwinfo.psz_revision);
    cyanrip_log(ctx, 0, "System device:  %s\n", ctx->settings.dev_path);
    if (ctx->drive->drive_model)
        cyanrip_log(ctx, 0, "Device model:   %s\n", ctx->drive->drive_model);
    cyanrip_log(ctx, 0, "Offset:         %c%i %s\n", ctx->settings.offset >= 0 ? '+' : '-', abs(ctx->settings.offset),
                abs(ctx->settings.offset) == 1 ? "sample" : "samples");
    cyanrip_log(ctx, 0, "%s%c%i %s\n",
                ctx->settings.over_under_read_frames < 0 ? "Underread:      " : "Overread:       ",
                ctx->settings.over_under_read_frames >= 0 ? '+' : '-',
                abs(ctx->settings.over_under_read_frames),
                abs(ctx->settings.over_under_read_frames) == 1 ? "frame" : "frames");
    cyanrip_log(ctx, 0, "%s%s\n",
                ctx->settings.over_under_read_frames < 0 ? "Underread mode: " : "Overread mode:  ",
                ctx->settings.overread_leadinout ? "read in lead-in/lead-out" : "fill with silence in lead-in/lead-out");
    if (ctx->settings.speed && (ctx->mcap & CDIO_DRIVE_CAP_MISC_SELECT_SPEED))
        cyanrip_log(ctx, 0, "Speed:          %ix\n", ctx->settings.speed);
    else
        cyanrip_log(ctx, 0, "Speed:          default (%s)\n",
                    (ctx->mcap & CDIO_DRIVE_CAP_MISC_SELECT_SPEED) ? "changeable" : "unchangeable");
    cyanrip_log(ctx, 0, "C2 errors:      %s\n", (ctx->rcap & CDIO_DRIVE_CAP_READ_C2_ERRS) ?
                "supported by drive, not used" : "unsupported by drive");
    print_cdtext(ctx);
    /* Name the library that actually encodes the audio, not just the ripper.
     * cyanrip encodes in-process through libavformat/libavcodec, so the FLAC
     * vendor string in the output files reads "LavfNN.nn.nn" and the log --
     * the archival record -- named the ripper and not the encoder. Two rips
     * made against different FFmpeg majors were indistinguishable from the log
     * alone. */
    cyanrip_log(ctx, 0, "Encoder:        libavformat %i.%i.%i, libavcodec %i.%i.%i (%s)\n",
                LIBAVFORMAT_VERSION_MAJOR, LIBAVFORMAT_VERSION_MINOR, LIBAVFORMAT_VERSION_MICRO,
                LIBAVCODEC_VERSION_MAJOR, LIBAVCODEC_VERSION_MINOR, LIBAVCODEC_VERSION_MICRO,
                av_version_info());
    if (ctx->settings.paranoia_level == crip_max_paranoia_level)
        cyanrip_log(ctx, 0, "Paranoia level: %s\n", "max");
    else if (ctx->settings.paranoia_level == 0)
        cyanrip_log(ctx, 0, "Paranoia level: %s\n", "none");
    else
        cyanrip_log(ctx, 0, "Paranoia level: %i\n", ctx->settings.paranoia_level);
    cyanrip_log(ctx, 0, "Frame retries:  %i\n", ctx->settings.max_retries);
    print_cache_model(ctx);
    cyanrip_log(ctx, 0, "HDCD decoding:  %s\n", ctx->settings.decode_hdcd ? "enabled" : "disabled");

    cyanrip_log(ctx, 0, "Album Art:      %s", ctx->nb_cover_arts == 0 ? "none" : "");
    for (int i = 0; i < ctx->nb_cover_arts; i++) {
        const char *title = dict_get(ctx->cover_arts[i].meta, "title");
        const char *source = dict_get(ctx->cover_arts[i].meta, "source");
        cyanrip_log(ctx, 0, "%s%s%s%s%s", title,
                    source ? " (From: " : "",
                    source ? source : "",
                    source ? ")" : "",
                    i != (ctx->nb_cover_arts - 1) ? ", " : "");
    }
    cyanrip_log(ctx, 0, "\n");

    cyanrip_log(ctx, 0, "Outputs:        ");
    for (int i = 0; i < ctx->settings.outputs_num; i++)
        cyanrip_log(ctx, 0, "%s%s", cyanrip_fmt_desc(ctx->settings.outputs[i]), i != (ctx->settings.outputs_num - 1) ? ", " : "");
    cyanrip_log(ctx, 0, "\n");
    CLOG("Disc number:    %s\n", ctx->meta, "disc");
    CLOG("Total discs:    %s\n", ctx->meta, "totaldiscs");
    cyanrip_log(ctx, 0, "Disc tracks:    %i\n", ctx->nb_cd_tracks);
    cyanrip_log(ctx, 0, "Tracks to rip:  %s", (ctx->settings.rip_indices_count == -1) ? "all" : !ctx->settings.rip_indices_count ? "none" : "");
    if (ctx->settings.rip_indices_count != -1) {
        for (int i = 0; i < ctx->settings.rip_indices_count; i++)
            cyanrip_log(ctx, 0, "%i%s", ctx->settings.rip_indices[i], i != (ctx->settings.rip_indices_count - 1) ? ", " : "");
    }
    cyanrip_log(ctx, 0, "\n");

    char duration[16];
    cyanrip_frames_to_duration(ctx->duration_frames, duration);

    CLOG("DiscID:         %s\n", ctx->meta, "musicbrainz_discid")
    CLOG("Release ID:     %s\n", ctx->meta, "musicbrainz_albumid")
    CLOG("CDDB ID:        %s\n", ctx->meta, "cddb")
    CLOG("Disc MCN:       %s\n", ctx->meta, "disc_mcn")
    CLOG("Album:          %s\n", ctx->meta, "album")
    CLOG("Album artist:   %s\n", ctx->meta, "album_artist")

    cyanrip_log(ctx, 0, "AccurateRip:    %s\n", ctx->ar_db_status == CYANRIP_ACCUDB_ERROR ? "error" :
                                                ctx->ar_db_status == CYANRIP_ACCUDB_NOT_FOUND ? "not found" :
                                                ctx->ar_db_status == CYANRIP_ACCUDB_FOUND ? "found" :
                                                ctx->ar_db_status == CYANRIP_ACCUDB_MISMATCH ? "mismatch" :
                                                "disabled");

    cyanrip_log(ctx, 0, "Total time:     %s\n", duration);

    cyanrip_log(ctx, 0, "\n");
}

void cyanrip_log_finish_report(cyanrip_ctx *ctx)
{
    char t_s[64];
    time_t t_c = time(NULL);
    struct tm *t_l = localtime(&t_c);
    strftime(t_s, sizeof(t_s), "%Y-%m-%dT%H:%M:%S", t_l);

    if (ctx->ar_db_status == CYANRIP_ACCUDB_FOUND) {
        int accurip_verified = 0;
        int accurip_partial = 0;
        for (int i = 0; i < ctx->nb_tracks; i++) {
            cyanrip_track *t = &ctx->tracks[i];
            if (t->ar_db_status == CYANRIP_ACCUDB_FOUND) {
                if ((crip_find_ar(t, t->acurip_checksum_v1, 0) > 0) ||
                    (crip_find_ar(t, t->acurip_checksum_v2, 0) > 0))
                    accurip_verified++;
                else if (crip_find_ar(t, t->acurip_checksum_v1_450, 1) > (3*(t->ar_db_max_confidence+1)/4) &&
                         t->acurip_checksum_v1_450)
                    accurip_partial++;
            }
        }
        cyanrip_log(ctx, 0, "Tracks ripped accurately: %i/%i\n", accurip_verified, ctx->nb_tracks);
        if (accurip_partial)
            cyanrip_log(ctx, 0, "Tracks ripped partially accurately: %i/%i\n",
                        accurip_partial, ctx->nb_tracks - accurip_verified);
        cyanrip_log(ctx, 0, "\n");
    }

    cyanrip_log(ctx, 0, "Paranoia status counts:\n");
    if (!print_paranoia_counts(ctx, paranoia_status, "  "))
        cyanrip_log(ctx, 0, "  none\n");
    cyanrip_log(ctx, 0, "\n");

    cyanrip_log(ctx, 0, "Ripping errors: %i\n", ctx->total_error_count);

    /* State plainly whether the rip ran to completion. Without this a rip
     * stopped part way through is only distinguishable from a whole one by
     * counting track blocks against the disc's track count, which a reader
     * can only do if it knows both. */
    if (quit_now)
        cyanrip_log(ctx, 0, "Rip completed:  no (interrupted by user, %i of %i tracks)\n",
                    ctx->tracks_completed, ctx->nb_tracks);
    else
        cyanrip_log(ctx, 0, "Rip completed:  yes (%i of %i tracks)\n",
                    ctx->tracks_completed, ctx->nb_tracks);

    cyanrip_log(ctx, 0, "Ripping finished at %s\n", t_s);
}

int cyanrip_log_init(cyanrip_ctx *ctx)
{
    for (int i = 0; i < ctx->settings.outputs_num; i++) {
        char *logfile = crip_get_path(ctx, CRIP_PATH_LOG, 1,
                                      &crip_fmt_info[ctx->settings.outputs[i]],
                                      NULL);

        ctx->logfile[i] = fopen(logfile, "wb+");

        /* Line buffer the log so a rip that is killed rather than ended
         * cleanly still leaves every completed track on disk. Ripping is
         * bound by the drive, so the extra write syscalls cost nothing
         * next to a 1x read. */
        if (ctx->logfile[i])
            setvbuf(ctx->logfile[i], NULL, _IOLBF, 0);

        if (!ctx->logfile[i]) {
            cyanrip_log(ctx, 0, "Couldn't open path \"%s\" for writing: %s!\n"
                        "Invalid folder name? Try -D <folder>.\n",
                        logfile, av_err2str(AVERROR(errno)));
            av_freep(&logfile);
            return 1;
        }

        av_freep(&logfile);
    }

    return 0;
}

void cyanrip_log_end(cyanrip_ctx *ctx)
{
    uint8_t digest[64];
    char digest_str[AV_BASE64_SIZE(64)];

    uint8_t *str_data = NULL;
    struct AVSHA512 *shactx = av_sha512_alloc();

    for (int i = 0; i < ctx->settings.outputs_num; i++) {
        if (!ctx->logfile[i])
            continue;

        if (!shactx)
            goto fail;

        av_sha512_init(shactx, 512);

        long int pos = ftell(ctx->logfile[i]);
        uint8_t *str_data_new = av_realloc(str_data, pos);
        if (!str_data_new)
            goto fail;
        str_data = str_data_new;

        rewind(ctx->logfile[i]);
        long int read_bytes = fread(str_data, 1, pos, ctx->logfile[i]);
        fseek(ctx->logfile[i], 0, SEEK_END);

        av_sha512_update(shactx, str_data, read_bytes);
        av_sha512_final(shactx, digest);

        crip_log_fun512(digest, i, digest_str);

        fprintf(ctx->logfile[i], CRIP_LOG_FUN512_MARKER "%s\n", digest_str);
fail:
        fclose(ctx->logfile[i]);
        ctx->logfile[i] = NULL;
    }

    av_free(str_data);
    av_free(shactx);
}

static cyanrip_ctx *av_global_ctx = NULL;
static int av_max_log_level = AV_LOG_QUIET;
static pthread_mutex_t log_lock = PTHREAD_MUTEX_INITIALIZER;

static void av_log_capture(void *ptr, int lvl, const char *format,
                           va_list args)
{
    pthread_mutex_lock(&log_lock);

    if (lvl > av_max_log_level)
        goto end;

    if (av_global_ctx) {
        for (int i = 0; i < av_global_ctx->settings.outputs_num; i++) {
            if (!av_global_ctx->logfile[i])
                continue;

            va_list args2;
            va_copy(args2, args);
            vfprintf(av_global_ctx->logfile[i], format, args2);
            va_end(args2);
        }
    }

    vprintf(format, args);

end:
    pthread_mutex_unlock(&log_lock);
}

void cyanrip_set_av_log_capture(cyanrip_ctx *ctx, int enable,
                                int max_av_lvl)
{
    pthread_mutex_lock(&log_lock);

    if (enable) {
        av_global_ctx = ctx;
        av_max_log_level = max_av_lvl;
        av_log_set_callback(av_log_capture);
    } else {
        av_log_set_callback(av_log_default_callback);
        av_global_ctx = NULL;
        av_max_log_level = AV_LOG_QUIET;
    }

    pthread_mutex_unlock(&log_lock);
}

void cyanrip_log(cyanrip_ctx *ctx, int verbose, const char *format, ...)
{
    pthread_mutex_lock(&log_lock);

    va_list args;
    va_start(args, format);

    if (ctx) {
        for (int i = 0; i < ctx->settings.outputs_num; i++) {
            if (!ctx->logfile[i])
                continue;

            va_list args2;
            va_copy(args2, args);
            vfprintf(ctx->logfile[i], format, args2);
            va_end(args2);
        }
    }

    vprintf(format, args);
    fflush(stdout);

    va_end(args);

    pthread_mutex_unlock(&log_lock);
}
