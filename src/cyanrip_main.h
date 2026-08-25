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

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <signal.h>
#include "../config.h"
#include "version.h"

#include "utils.h"

#include <cdio/paranoia/paranoia.h>
#include <cdio/logging.h>
#include <cdio/audio.h>
#include <libavutil/mem.h>
#include <libavutil/dict.h>
#include <libavutil/avstring.h>
#include <libavutil/intreadwrite.h>
#include <libavcodec/avcodec.h>

enum cyanrip_output_formats {
    CYANRIP_FORMAT_FLAC = 0,
    CYANRIP_FORMAT_TTA,
    CYANRIP_FORMAT_OPUS,
    CYANRIP_FORMAT_AAC,
    CYANRIP_FORMAT_WAVPACK,
    CYANRIP_FORMAT_ALAC,
    CYANRIP_FORMAT_ALAC_MP4,
    CYANRIP_FORMAT_MP3,
    CYANRIP_FORMAT_VORBIS,
    CYANRIP_FORMAT_WAV,
    CYANRIP_FORMAT_AAC_MP4,
    CYANRIP_FORMAT_OPUS_MP4,
    CYANRIP_FORMAT_PCM,

    CYANRIP_FORMATS_NB,
};

enum cyanrip_pregap_action {
    CYANRIP_PREGAP_DEFAULT = 0,
    CYANRIP_PREGAP_DROP,
    CYANRIP_PREGAP_MERGE,
    CYANRIP_PREGAP_TRACK,
};

enum CRIPAccuDBStatus {
    CYANRIP_ACCUDB_DISABLED = 0,
    CYANRIP_ACCUDB_NOT_FOUND,
    CYANRIP_ACCUDB_ERROR,
    CYANRIP_ACCUDB_MISMATCH,
    CYANRIP_ACCUDB_FOUND,
};

/* Where a track's pregap LSN came from, or why it isn't known. Recorded
 * during disc enumeration, which runs before the log file is open, and
 * reported later by the log writer. */
enum cyanrip_pregap_source {
    CYANRIP_PREGAP_SRC_NONE = 0, /* No pregap, and none looked for */
    CYANRIP_PREGAP_SRC_TOC, /* The disc's TOC signalled it */
    CYANRIP_PREGAP_SRC_LEADIN, /* First track, the standard lead-in */
    CYANRIP_PREGAP_SRC_SUBCHANNEL, /* Found by reading Q sub-channel data */
    CYANRIP_PREGAP_SRC_ERR_READ, /* Sub-channel unreadable, pregap unknown */
    CYANRIP_PREGAP_SRC_ERR_CRC, /* Sub-channel CRCs never agreed, unknown */
};

enum cyanrip_secure_rip_state {
    CYANRIP_SECURE_RIP_NA = 0, /* -Z was not requested for this track */
    CYANRIP_SECURE_RIP_CONVERGED, /* Matching checksums were found */
    CYANRIP_SECURE_RIP_LIMIT_HIT, /* Repeat limit hit before checksums matched */
    /* There is deliberately NO "interrupted" state, and the absence is load
     * bearing rather than an omission. An interrupted track emits no track
     * block at all -- cyanrip_rip_track()'s `if (!quit_now && !ret)` guard --
     * because its checksums would be over a partial read and its files are
     * unfinalised, so every measurement in that block would be a wrong claim.
     * A state added here therefore has nowhere to be printed.
     *
     * One WAS added, in this round, before generating a sample artifact showed
     * the line never appears. That the rest of the suite stayed green is the
     * point: no test asserted a line nobody emits. What a consumer loses by
     * this -- there is no record of WHICH track was in progress when the rip
     * stopped -- is real, and is round 12 §J rather than something to invent
     * here. */
};

/* Whether the disc carries CD-TEXT. libcdio hands back one NULL for both "the
 * disc has no CD-TEXT block" and "this driver cannot read one", and gives us no
 * way to tell them apart, so ABSENT means exactly "libcdio reported none" and
 * the log says so rather than claiming the disc is bare. */
enum cyanrip_cdtext_status {
    CYANRIP_CDTEXT_ABSENT = 0, /* libcdio reported no CD-TEXT */
    CYANRIP_CDTEXT_PRESENT, /* At least one field was read */
};

enum CRIPPathType {
    CRIP_PATH_COVERART, /* arg must be a CRIPArt * */
    CRIP_PATH_TRACK, /* arg must be a cyanrip_track * */
    CRIP_PATH_DATA, /* arg must be a cyanrip_track * */
    CRIP_PATH_LOG, /* arg must be NULL */
    CRIP_PATH_CUE, /* arg must be NULL */
};

enum CRIPSanitize {
    CRIP_SANITIZE_SIMPLE, /* Replace unacceptable symbols with _ */
    CRIP_SANITIZE_OS_SIMPLE, /* Same as above, but only replaces symbols not allowed on current OS */
    CRIP_SANITIZE_UNICODE, /* Replace unacceptable symbols with visually identical unicode equivalents */
    CRIP_SANITIZE_OS_UNICODE, /* Same as above, but only replaces symbols not allowed on current OS */
};

enum coverart_lookup_sizes {
    COVERART_LOOKUP_SIZE_ORIGINAL = 0,
    COVERART_LOOKUP_SIZE_250,
    COVERART_LOOKUP_SIZE_500,
    COVERART_LOOKUP_SIZE_1200
};

typedef struct cyanrip_settings {
    char *dev_path;
    char *folder_name_scheme;
    char *track_name_scheme;
    char *log_name_scheme;
    char *cue_name_scheme;
    enum CRIPSanitize sanitize_method;
    int speed;
    int max_retries;
    int offset;
    int over_under_read_frames;
    int print_info_only;
    int disable_mb;
    float bitrate;
    int decode_hdcd;
    int disable_accurip;
    int disable_coverart_db;
    int overread_leadinout;
    int eject_on_success_rip;
    enum cyanrip_pregap_action pregap_action[198];
    int rip_indices_count;
    int rip_indices[198];
    int paranoia_level;
    int deemphasis;
    int force_deemphasis;
    int ripping_retries;
    int disable_coverart_embedding;
    enum coverart_lookup_sizes coverart_lookup_size;
    int enable_replaygain;
    int cache_probe;
    char *consumer_id; /* -x: measure the drive's readback cache before ripping */
    int generate_cue_only;

    enum cyanrip_output_formats outputs[CYANRIP_FORMATS_NB];
    int outputs_num;
} cyanrip_settings;

typedef struct CRIPAccuDBEntry {
    int confidence;
    uint32_t checksum; /* We don't know which version it is */
    uint32_t checksum_450;
} CRIPAccuDBEntry;

typedef struct CRIPArt {
    AVDictionary *meta;
    char *source_url;
    char *title; /* Temporary, used during parsing only, copied to meta, do not free */

    AVPacket *pkt;
    AVCodecParameters *params;

    uint8_t *data;
    size_t size;
    char *extension;
} CRIPArt;

/* The widest read offset -s will accept, in samples: ~23.8 seconds, three
 * orders of magnitude past any real drive. The bound exists so offset*4 and
 * -offset stay defined; see the note at the option table. */
#define CRIP_MAX_OFFSET_SAMPLES 1048576

typedef struct cyanrip_track {
    int number; /* Human readable track number, may be 0 */
    int cd_track_number; /* Actual track on the CD, may be 0 */
    AVDictionary *meta; /* Disc's AVDictionary gets copied here */
    AVDictionary *cdtext; /* This track's CD-TEXT, verbatim, never overwritten */
    int total_repeats; /* How many times the track was re-ripped */
    /* This track's share of the paranoia callback counters, taken as a
     * before/after delta around the read so a disc total can be attributed to
     * the track that earned it.
     *
     * THE LAST PASS ONLY, and this comment used to claim the opposite. The
     * baseline is snapshotted AFTER the `repeat_ripping:` label, so every -Z
     * re-read resets it and what survives describes the read whose audio was
     * kept -- not the work the track cost. The disc-level counters are the
     * process-global ones and DO sum every pass.
     *
     * So per-track figures do NOT sum to the disc totals whenever anything
     * re-read, which is round 5's invariant and it is false in general.
     * Platterpus measured it on our own golden reference (15+10+5 against 90,
     * three reads a track, ratio exactly 3) and it is confirmed here from the
     * source. Both prior verifications of that invariant ran on artifacts
     * where every track reported `not attempted`, which is the one condition
     * that forces the sum arithmetically. */
    uint64_t paranoia_status[PARANOIA_CB_FINISHED + 1];
    enum cyanrip_secure_rip_state secure_rip_state; /* -Z convergence verdict */
    /* Whether this track's audio was ripped AND finalised. Set in the one
     * place ctx->tracks_completed is incremented, so the per-track flag and
     * the disc counter agree by construction rather than by two readings of
     * the same condition.
     *
     * Named for what it is, not "completed": a DATA track is false here and
     * nothing went wrong -- it is never ripped. An interrupted audio track is
     * also false, and the diagnostics record uses this to decide that its
     * checksum fields carry nothing. Before that, a rip stopped mid-track
     * published `crcs_computed: true` and an eac_crc computed over a partial
     * read, for audio that is not on disk: a confident wrong field in an
     * archival record, which is worse than a missing one. */
    int audio_ripped;
    /* Frames removed from end_lsn as a CD-Extra inter-session gap, else 0.
     * end_lsn differs from end_lsn_sig for TWO independent reasons -- the read
     * offset and this -- and the log said "with offset" for both, so an
     * 11400-frame session adjustment read as a read offset that is normally
     * one frame. This is what lets the two be told apart. */
    int end_lsn_session_gap;
    int64_t rip_time_us; /* Wall clock time spent ripping and encoding */
    int index; /* Array position + 1 */

    int track_is_data;
    int preemphasis;
    int preemphasis_in_subcode;

    size_t nb_samples; /* Track duration in samples */

    int frames_before_disc_start;
    lsn_t frames; /* Actual number of frames to read, != samples */
    int frames_after_disc_end;

    lsn_t pregap_lsn;
    enum cyanrip_pregap_source pregap_source; /* Provenance of pregap_lsn */
    lsn_t start_lsn;
    lsn_t start_lsn_sig;
    lsn_t end_lsn;
    lsn_t end_lsn_sig;

    /* CUE sheet generator only */
    /* Whether this track's own FILE line has been written to the cue. An
     * appended pre-gap's INDEX 00 is an offset into the PREVIOUS track's FILE,
     * so under -l the only honest question is "did we write that FILE", and
     * the rip set alone cannot answer it at this point. */
    int cue_file_written;
    lsn_t dropped_pregap_start;
    lsn_t merged_pregap_end;

    ptrdiff_t partial_frame_byte_offs;

    CRIPArt art; /* One cover art, will not be saved */

    int computed_crcs;
    uint32_t eac_crc;
    uint32_t acurip_checksum_v1;
    uint32_t acurip_checksum_v1_450;
    uint32_t acurip_checksum_v2;
    int acurip_track_is_first;
    int acurip_track_is_last;

    enum CRIPAccuDBStatus ar_db_status;
    CRIPAccuDBEntry *ar_db_entries;
    int ar_db_nb_entries;
    int ar_db_max_confidence;

    /* EBUR128 values */
    double ebu_integrated;
    double ebu_range;
    double ebu_lra_low;
    double ebu_lra_high;
    double ebu_sample_peak;
    double ebu_true_peak;
    /* THREE measurements of one fact, and the reason there are three is that
     * each is computed by a different route, so a disagreement localises a
     * defect instead of merely announcing one.
     *
     *   ebu_sample_peak      libavfilter's ebur128, dBFS
     *   direct_sample_peak   our own max |sample| over the AVFrames handed to
     *                        that filter, dBFS
     *   sample_peak_rel_amp  upstream's max |int16| over the raw bytes read
     *                        from the disc, linear 0.0-1.0
     *
     * They measure the SAME SAMPLES. The frames the first two see are built
     * verbatim from the bytes the third sees (S16, nb_samples = bytes >> 2) and
     * the deemphasis/HDCD filter is applied downstream of them, on the way to
     * the encoders only -- so agreement is the expected case on every disc, not
     * just an unfiltered one. Said plainly because the tempting reading is that
     * upstream's measures the pre-emphasised audio and ours the de-emphasised
     * one; it was checked in cyanrip_encode.c:filter_frame() and it does not.
     *
     * NONE of the three is printed unconditionally beside another. Two
     * always-present numbers for one fact invite a consumer to pick one, and
     * whichever it picks will occasionally be the wrong one silently (H6,
     * Platterpus round 7). Agreement is not information; a disagreement is a
     * finding, and only the finding is logged.
     *
     * direct_sample_peak is -INFINITY until measured; sample_peak_rel_amp is
     * 0.0 until measured and is reset per -Z attempt so a discarded pass cannot
     * leave a peak behind. */
    double direct_sample_peak;
    double sample_peak_rel_amp;

    struct cyanrip_track *pt;
    struct cyanrip_track *nt;

    struct cyanrip_dec_ctx *dec_ctx;
    struct cyanrip_enc_ctx *enc_ctx[CYANRIP_FORMATS_NB];
} cyanrip_track;

typedef struct cyanrip_ctx {
    cdrom_drive_t     *drive;
    cdrom_paranoia_t  *paranoia;
    CdIo_t            *cdio;
    FILE              *logfile[CYANRIP_FORMATS_NB];
    FILE              *cuefile[CYANRIP_FORMATS_NB];
    cyanrip_settings   settings;

    cyanrip_track tracks[198];
    int nb_tracks; /* Total number of output tracks */
    int nb_cd_tracks; /* Total tracks the CD signals */
    int disregard_cd_isrc; /* If one track doesn't have ISRC, universally the rest won't */

    char *mb_submission_url;

    /* Non-track bound cover art */
    CRIPArt cover_arts[32];
    int nb_cover_arts;

    /* Drive caps */
    cdio_drive_read_cap_t  rcap;
    cdio_drive_write_cap_t wcap;
    cdio_drive_misc_cap_t  mcap;

    /* Metadata */
    AVDictionary *meta;
    enum CRIPAccuDBStatus ar_db_status;

    /* Disc-level CD-TEXT, verbatim. Kept apart from meta so it stays
     * reportable no matter what later overwrites the tags. */
    AVDictionary *cdtext;
    enum cyanrip_cdtext_status cdtext_status;
    int cdtext_nb_disc_fields;
    int cdtext_nb_tagged_tracks;
    const char *cdtext_language; /* Owned by libcdio, do not free */

    /* State */
    int success;
    int total_error_count;
    int tracks_completed; /* Tracks fully ripped, for the completion line */
    /* CD track number of a read that STARTED and has not completed, else 0.
     * Set as the read loop is entered and cleared only when that loop exits
     * normally, so every abort out of it -- a signal, an error, a goto --
     * leaves the track named rather than needing its own clear. Reported by
     * `Interrupted at:`; a consumer could otherwise only infer it by counting
     * track blocks against the disc's track count. */
    int track_read_incomplete;
    /* Set at the ONE point where the rip loop falls out normally, immediately
     * before `end:`. Everything else in cyanrip_run() leaves it 0 -- and there
     * are twenty-four `goto end` sites, so a per-site flag would be twenty-four
     * chances to forget one. The single assignment is the discriminator, in the
     * same shape and for the same reason as track_read_incomplete above.
     *
     * `Rip completed:` needs THREE states and had two. `no (interrupted by
     * SIGTERM…)` was the only "no", so every abort that was not a signal --
     * every one of those twenty-four -- fell to the `else` and printed
     * `yes`. That never showed, because the footer sat above `end:` and no
     * abort reached it at all; moving the footer where aborts can reach it
     * turned a silent omission into a confident false claim, which is worse.
     * Both halves are fixed together for that reason. */
    int rip_ran_to_completion;
    lsn_t start_lsn;
    lsn_t end_lsn;
    lsn_t duration_frames;

    /* ETA */
    CRSlidingWinCtx eta_ctx;
    lsn_t frames_read;
    lsn_t frames_to_read;

    /* Album EBUR128 values */
    struct cyanrip_dec_ctx *peak_ctx;
    double ebu_integrated;
    double ebu_range;
    double ebu_lra_low;
    double ebu_lra_high;
    double ebu_sample_peak;
    double ebu_true_peak;
    /* The same sample peak measured a second way -- max |sample| over the
     * frames handed to the ebur128 filter, in dBFS. Reported only when the two
     * disagree (H6, Platterpus round 7): agreement is the expected case and a
     * second always-present number invites a consumer to pick one, which will
     * occasionally be the wrong one silently. -INFINITY until measured. */
    double direct_sample_peak;
} cyanrip_ctx;

typedef struct cyanrip_out_fmt {
    const char *name;
    const char *folder_suffix;
    const char *ext;
    const char *lavf_name;
    int coverart_supported;
    int compression_level;
    int lossless;
    enum AVCodecID codec;
} cyanrip_out_fmt;

extern const cyanrip_out_fmt crip_fmt_info[];

char *crip_get_path(cyanrip_ctx *ctx, enum CRIPPathType type, int create_dirs,
                    const cyanrip_out_fmt *fmt, void *arg);

/* Prepend key1= and key2= to the first two keyless entries of a
 * key=value:key=value string, minding escapes. Key 1 and 2 must be set. */
char *append_missing_keys(const char *src, const char *key1, const char *key2);

int crip_is_integer(const char *src);

/* Set from a signal handler, so volatile sig_atomic_t rather than int: an int
 * written in a handler and read from the rip loop may be cached in a register
 * and never re-read, which is the compiler being allowed to ignore the only
 * thing telling it to stop. It has always behaved here; that is not the same
 * as being correct, and the fix costs a type. */
extern volatile sig_atomic_t quit_now;

/* Which signal set quit_now, or 0 if none has. Recorded rather than inferred
 * because the log has to say *what* stopped the rip: SIGINT is a person at a
 * terminal, SIGTERM is a supervising process, and calling a supervisor's
 * timeout "interrupted by user" is a wrong claim in an archival record. */
extern volatile sig_atomic_t quit_signal;
/* crip_signal_name() turns it into text, and lives in utils.h so tests/diag.c
 * can use the same one rather than carrying a second copy. */

/* The command line as received, or NULL before it is recorded */
extern char *crip_invocation;

extern uint64_t paranoia_status[PARANOIA_CB_FINISHED + 1];
extern const int crip_max_paranoia_level;
