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

/* Carried from upstream PR #115 ("Add pregap detection for physical CDs",
 * UltraFuzzy, https://github.com/cyanreg/cyanrip/pull/115), still unmerged
 * upstream as of this fork. Fixed here before integrating: a wrong error
 * sentinel that could make a failed detection look like a real pregap at a
 * bogus LSN, a buffer leak on one return path, and I/O-retry exhaustion
 * aborting the whole process instead of falling back cleanly. See
 * docs/pregap-carry.md for the full audit and what still needs
 * real-hardware verification. */

#include "pregap.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include <cdio/cdio.h>
#include <cdio/mmc_ll_cmds.h>

#ifdef __APPLE__
#include <IOKit/storage/IOCDTypes.h>
#include <IOKit/storage/IOCDMediaBSDClient.h>
#include <sys/errno.h>
#endif


// Size of reads of audio + subchannel Q data. 2352 bytes for audio + 16 bytes for subchannel Q
#define CYANRIP_CD_FRAMESIZE_RAW_AND_SUBQ (CDIO_CD_FRAMESIZE_RAW + 16)


// TODO The implementation for macOS currently requires access to private
// internal cdio data, namely p_cdio->env.fd. Right now we just copy-paste some
// struct definitions to work around this. libcdio accepted a pull request for
// a function cdio_get_device_fd() (https://github.com/libcdio/libcdio/pull/37)
// that solves this issue. When that works its way into package managers it
// should be used here.
#ifdef __APPLE__
// lib/driver/mmc/mmc_private.h
typedef driver_return_code_t (*mmc_run_cmd_fn_t)
     ( void *p_user_data,
       unsigned int i_timeout_ms,
       unsigned int i_cdb,
       const mmc_cdb_t *p_cdb,
       cdio_mmc_direction_t e_direction,
       unsigned int i_buf, void *p_buf);

// lib/driver/cdio_private.h
typedef struct {
    driver_return_code_t (*audio_get_volume)
         (void *p_env,  /*out*/ cdio_audio_volume_t *p_volume);
    driver_return_code_t (*audio_pause) (void *p_env);
    driver_return_code_t (*audio_play_msf) ( void *p_env,
                                             msf_t *p_start_msf,
                                             msf_t *p_end_msf );
    driver_return_code_t (*audio_play_track_index)
         ( void *p_env, cdio_track_index_t *p_track_index );
    driver_return_code_t (*audio_read_subchannel)
         ( void *p_env, cdio_subchannel_t *subchannel );
    driver_return_code_t (*audio_resume) ( void *p_env );
    driver_return_code_t (*audio_set_volume)
         ( void *p_env,  cdio_audio_volume_t *p_volume );
    driver_return_code_t (*audio_stop) ( void *p_env );
    driver_return_code_t (*eject_media) ( void *p_env );
    void (*free) (void *p_env);
    const char * (*get_arg) (void *p_env, const char key[]);
    int (*get_blocksize) ( void *p_env );
    cdtext_t * (*get_cdtext) ( void *p_env );
    uint8_t * (*get_cdtext_raw) ( void *p_env );
    char ** (*get_devices) ( void );
    char * (*get_default_device) ( void );
    lsn_t (*get_disc_last_lsn) ( void *p_env );
    discmode_t (*get_discmode) ( void *p_env );
    void (*get_drive_cap) (const void *p_env,
                           cdio_drive_read_cap_t  *p_read_cap,
                           cdio_drive_write_cap_t *p_write_cap,
                           cdio_drive_misc_cap_t  *p_misc_cap);
    track_t (*get_first_track_num) ( void *p_env );
    bool (*get_hwinfo)
         ( const CdIo_t *p_cdio, /* out*/ cdio_hwinfo_t *p_hw_info );
    driver_return_code_t (*get_last_session)
         ( void *p_env, /*out*/ lsn_t *i_last_session );
    int (*get_media_changed) ( const void *p_env );
    char * (*get_mcn) ( const void *p_env );
    track_t (*get_num_tracks) ( void *p_env );
    int (*get_track_channels) ( const void *p_env, track_t i_track );
    track_flag_t (*get_track_copy_permit) ( void *p_env, track_t i_track );
    lba_t (*get_track_lba) ( void *p_env, track_t i_track );
    lba_t (*get_track_pregap_lba) ( const void *p_env, track_t i_track );
    char * (*get_track_isrc) ( const void *p_env, track_t i_track );
    track_format_t (*get_track_format) ( void *p_env, track_t i_track );
    bool (*get_track_green) ( void *p_env, track_t i_track );
    bool (*get_track_msf) ( void *p_env, track_t i_track, msf_t *p_msf );
    track_flag_t (*get_track_preemphasis)
         ( const void  *p_env, track_t i_track );
    off_t (*lseek) ( void *p_env, off_t offset, int whence );
    ssize_t (*read) ( void *p_env, void *p_buf, size_t i_size );
    int (*read_audio_sectors) ( void *p_env, void *p_buf, lsn_t i_lsn,
                                unsigned int i_blocks );
    driver_return_code_t (*read_data_sectors)
         ( void *p_env, void *p_buf, lsn_t i_lsn, uint16_t i_blocksize,
           uint32_t i_blocks );
    int (*read_mode2_sector)
         ( void *p_env, void *p_buf, lsn_t i_lsn, bool b_mode2_form2 );
    int (*read_mode2_sectors)
         ( void *p_env, void *p_buf, lsn_t i_lsn, bool b_mode2_form2,
           unsigned int i_blocks );
    int (*read_mode1_sector)
         ( void *p_env, void *p_buf, lsn_t i_lsn, bool mode1_form2 );
    int (*read_mode1_sectors)
         ( void *p_env, void *p_buf, lsn_t i_lsn, bool mode1_form2,
           unsigned int i_blocks );
    bool (*read_toc) ( void *p_env ) ;
    mmc_run_cmd_fn_t run_mmc_cmd;
    int (*set_arg) ( void *p_env, const char key[], const char value[] );
    driver_return_code_t (*set_blocksize) ( void *p_env,
                                            uint16_t i_blocksize );
    int (*set_speed) ( void *p_env, int i_speed );
} cdio_funcs_t;

// lib/driver/cdio_private.h
typedef struct {
    uint16_t    u_type;
    uint16_t    u_flags;
} cdio_header_t;

// lib/driver/cdio_private.h
struct _CdIo {
    cdio_header_t header;
    driver_id_t   driver_id;
    cdio_funcs_t  op;
    void*         env;
};

// lib/driver/generic.h
typedef struct {
    char *source_name;
    bool  init;
    bool  toc_init;
    bool  b_cdtext_error;
    int   ioctls_debugged;
    void *data_source;
    int     fd;
} generic_img_private_t;


static driver_return_code_t read_audio_subq_sectors_mac(
    const CdIo_t *p_cdio,
    uint8_t *audio_subq_buf,
    const lsn_t lsn,
    const uint32_t blocks)
{
    generic_img_private_t *p_gen = (generic_img_private_t*)(p_cdio->env);
    const int fd = p_gen->fd;

    const unsigned block_size = CYANRIP_CD_FRAMESIZE_RAW_AND_SUBQ;
    dk_cd_read_t cd_read = {
        .offset = block_size*lsn,
        .sectorArea = kCDSectorAreaUser | kCDSectorAreaSubChannelQ,
        .sectorType = kCDSectorTypeCDDA,
        .bufferLength = block_size*blocks,
        .buffer = audio_subq_buf,
    };
    if (!ioctl(fd, DKIOCCDREAD, &cd_read))
        return DRIVER_OP_SUCCESS;
    // TODO More detailed error handling? errno will be one of:
    // EBADF
    // EINVAL
    // ENOTTY
    return DRIVER_OP_ERROR;
}
#endif


// Not on macOS, which reads through read_audio_subq_sectors_mac() above.
#ifndef __APPLE__
static driver_return_code_t read_audio_subq_sectors_mmc(
    const CdIo_t *p_cdio,
    uint8_t *audio_subq_buf,
    const lsn_t lsn,
    const uint32_t blocks)
{
    const int expected_sector_type = 1; /* CD-DA sectors */
    const bool b_digital_audio_play = false;
    const bool b_sync = false;
    const uint8_t header_codes = 0; /* no header information */
    const bool b_user_data = true;
    const bool b_edc_ecc = false;
    const uint8_t c2_error_information = 0;
    const uint8_t subchannel_selection = 2; /* Q sub-channel */
    const uint16_t i_blocksize = CYANRIP_CD_FRAMESIZE_RAW_AND_SUBQ;

    return mmc_read_cd(p_cdio, audio_subq_buf, lsn, expected_sector_type,
        b_digital_audio_play, b_sync, header_codes, b_user_data, b_edc_ecc,
        c2_error_information, subchannel_selection, i_blocksize, blocks);
}
#endif


// Reading Q subchannel using the READ CD command is an MMC-2 feature. Ancient
// drives don't support it and will return zeroes.
static driver_return_code_t read_audio_subq_sector(
    const CdIo_t *p_cdio,
    uint8_t *audio_subq_buf,
    const lsn_t lsn)
{
    #ifdef __APPLE__
        return read_audio_subq_sectors_mac(p_cdio, audio_subq_buf, lsn, 1);
    #else
        return read_audio_subq_sectors_mmc(p_cdio, audio_subq_buf, lsn, 1);
    #endif
}


typedef struct subq_t {
    uint8_t  control;
    uint8_t  adr;
    uint8_t  track_number;
    uint8_t  index_number;
    uint8_t  min;
    uint8_t  sec;
    uint8_t  frame;
    uint8_t  amin;
    uint8_t  asec;
    uint8_t  aframe;
    unsigned crc;
} subq_t;

static inline uint8_t bcd_to_bin(uint8_t x){
    return 10*((x & 0xF0) >> 4) + (x & 0x0F);
}

/* MMC-3 4.1.3.2.1. Q sub-channel Mode-1: "Bytes in the Q sub-channel that
 * contains bcd contents may also contain illegal BCD values. Then values start
 * with 0A0h and continue to 0FFh. No conversion of these to hex for
 * transmission to/from the initiator is performed."
 */
static inline uint8_t subq_bcd_to_bin(uint8_t x){
    return x >= 0xA0 ? x : bcd_to_bin(x);
}

// CRC-16/GSM with length 10
static inline unsigned crc_subq(const uint8_t* subq_buf)
{
    int length = 10;
    const unsigned crc_poly = 0x1021;
    unsigned r = 0x0000;
    while (length--) {
        r ^= *subq_buf++ << 8;
        for (int i = 0; i < 8; i++)
            r = r & 0x8000 ? (r << 1) ^ crc_poly : r << 1;
    }
    return ~r & 0xFFFF;
}

// MMC-3 Table 38 - Formatted Q sub-channel response data
static void decode_subq(subq_t *subq, const uint8_t *src) {
    subq->control       = (src[0] & 0xF0) >> 4;
    subq->adr           = (src[0] & 0x0F) >> 0;
    // TODO Unclear if these will always be BCD.  From MMC-3, the answer is yes.
    subq->track_number  = subq_bcd_to_bin(src[1]);
    subq->index_number  = subq_bcd_to_bin(src[2]);
    subq->min           = subq_bcd_to_bin(src[3]);
    subq->sec           = subq_bcd_to_bin(src[4]);
    subq->frame         = subq_bcd_to_bin(src[5]);
    subq->amin          = subq_bcd_to_bin(src[7]);
    subq->asec          = subq_bcd_to_bin(src[8]);
    subq->aframe        = subq_bcd_to_bin(src[9]);
    subq->crc           = (src[10] << 8) | src[11];
}


/* Re-encodes the BCD-carrying Q sub-channel fields back to BCD, in place. */
static void fixup_subq_to_bcd(uint8_t *subq_buf)
{
    static const int fields[] = { 1, 2, 3, 4, 5, 7, 8, 9 };
    for (size_t i = 0; i < sizeof(fields) / sizeof(fields[0]); i++) {
        const uint8_t x = subq_buf[fields[i]];
        subq_buf[fields[i]] = (uint8_t)(((x / 10) << 4) | (x % 10));
    }
}

/* Validates a Q sub-channel sector's CRC, transparently applying the BCD
 * fixup above when this drive needs it.
 *
 * Some drives' firmware hands back the track/index/MSF fields as raw binary
 * instead of the BCD the spec calls for. The CRC on the disc is always
 * computed over the BCD encoding, so on such a drive every sector fails
 * validation and pregap detection can only ever report "unknown (sub-channel
 * CRC mismatches)" -- the detection never gets off the ground. Re-encoding to
 * BCD before checking recovers those drives. XLD carries a workaround for the
 * same firmware behaviour.
 *
 * Detected once per search and remembered in *needs_fixup, so the cost is one
 * extra CRC on the first sector rather than on every sector.
 *
 * Mutates subq_buf in place when a fixup is applied, so callers must
 * decode_subq() only after this returns, and must not call it twice on the
 * same buffer -- a second call would re-encode already-encoded fields.
 * Returns 1 if the sector is valid, 0 otherwise. */
/* Both track LSNs must be real before either is used in arithmetic. Separated
 * out so tests/subq.c can assert it without a CdIo_t: the caller needs a live
 * libcdio handle whose track lookup fails, which no fixture can produce. */
static int track_lsns_usable(lsn_t track_start_lsn, lsn_t prev_track_start_lsn)
{
    return track_start_lsn != CDIO_INVALID_LSN &&
           prev_track_start_lsn != CDIO_INVALID_LSN;
}

static int verify_subq_crc(uint8_t *subq_buf, int *needs_fixup)
{
    const unsigned crc_read = (subq_buf[10] << 8) | subq_buf[11];

    /* An all-zero CRC is what a drive that does not return Q sub-channel data
     * at all leaves in the buffer; treat it as invalid rather than as a
     * sector that happens to check out. */
    if (!crc_read)
        return 0;

    if (*needs_fixup)
        fixup_subq_to_bcd(subq_buf);

    if (crc_read == crc_subq(subq_buf))
        return 1;

    if (!*needs_fixup) {
        fixup_subq_to_bcd(subq_buf);
        if (crc_read == crc_subq(subq_buf)) {
            *needs_fixup = 1;
            return 1;
        }
    }

    return 0;
}

/* Reads one sector's audio and its Q sub-channel frame into audio_subq_buf,
 * CYANRIP_CD_FRAMESIZE_RAW_AND_SUBQ bytes. The search reads through this
 * rather than through a CdIo_t, so tests/subq.c can hand it a drive of its
 * own making, including one whose frames answer for another sector, which no
 * disc image produces. */
typedef driver_return_code_t (*subq_read_fn)(void *opaque, uint8_t *audio_subq_buf,
                                             lsn_t lsn);

static driver_return_code_t read_subq_from_drive(void *opaque, uint8_t *audio_subq_buf,
                                                 lsn_t lsn)
{
    return read_audio_subq_sector(opaque, audio_subq_buf, lsn);
}

/* Returns the driver error code (if any) via the return value, and whether the
 * sector ended up CRC-valid via *out_valid. Callers must use *out_valid rather
 * than re-checking the CRC themselves: verify_subq_crc() may have rewritten
 * the buffer, so a second check would operate on already-fixed-up fields. */
static driver_return_code_t read_audio_subq_sector_with_retries(
    subq_read_fn read,
    void *opaque,
    uint8_t *audio_subq_buf,
    const lsn_t lsn,
    const int retry_max,
    int *needs_fixup,
    int *out_valid)
{
    driver_return_code_t ret = read(opaque, audio_subq_buf, lsn);
    uint8_t *subq_buf = audio_subq_buf + CDIO_CD_FRAMESIZE_RAW;
    int valid = !ret && verify_subq_crc(subq_buf, needs_fixup);
    int retry = 0;

    while (retry++ < retry_max && !valid) {
        // TODO Is a cache defeat here ever necessary? Testing on macOS with an
        // ASUS SDRW-08U7M-U, it didn't have an effect.
        // overflow_device_read_cache(p_cdio, lsn);
        if ((ret = read(opaque, audio_subq_buf, lsn))) {
            *out_valid = 0;
            return ret;
        }
        valid = verify_subq_crc(subq_buf, needs_fixup);
    }

    *out_valid = valid;
    return ret;
}

/* The sector a Q frame belongs to, which is not always the sector that was
 * read. A mode-1 frame carries its own absolute address in full. A mode-2
 * (catalogue number) or mode-3 (ISRC) frame carries only its frame number
 * within the second, so it is placed at the sector nearest `near` with that
 * frame number, and the caller decides whether that is close enough.
 * CDIO_INVALID_LSN for an address no disc carries. */
static lsn_t subq_frame_lsn(const subq_t *subq, lsn_t near)
{
    const int fps = CDIO_CD_FRAMES_PER_SEC;

    if (subq->aframe >= fps)
        return CDIO_INVALID_LSN;

    if (subq->adr == 1) {
        if (subq->amin > 99 || subq->asec >= CDIO_CD_SECS_PER_MIN)
            return CDIO_INVALID_LSN;
        return (subq->amin*CDIO_CD_SECS_PER_MIN + subq->asec)*fps + subq->aframe -
               CDIO_PREGAP_SECTORS;
    }

    int d = ((int)subq->aframe - (int)(((near % fps) + fps) % fps) + fps) % fps;
    if (d > fps/2)
        d -= fps;
    return near + d;
}

/* How far from the sector asked for a mode-1 frame may answer and still be
 * taken as this drive's alignment, for aiming the next read. A frame from
 * farther away is still placed where its own address says; it only stops
 * steering the reads. */
#define SUBQ_MAX_SHIFT CDIO_CD_FRAMES_PER_SEC

struct pregap_search {
    subq_read_fn read;
    void *opaque;
    uint8_t audio_subq_buf[CYANRIP_CD_FRAMESIZE_RAW_AND_SUBQ];
    track_t prev_track_number;
    track_t track_number;
    /* The last sector known to be the previous track's, and the first known
     * to be this track's. The pregap starts at right once they meet. */
    lsn_t left_bound;
    lsn_t right_bound;
    /* The sectors a read may be aimed at: never before the previous track,
     * and never into this track past its INDEX 01. */
    lsn_t first_readable;
    lsn_t last_readable;
    /* How far from the sector asked for this drive's frames answer, once two
     * in a row have agreed, and how far the last one did. */
    int shift;
    int last_delta;
    /* Whether this drive returns the Q sub-channel MSF/track fields as raw
     * binary instead of BCD. Detected on the first sector that validates only
     * after re-encoding, then reused for the rest of this search. Kept local
     * rather than on the context so one odd disc cannot poison the next. */
    int needs_bcd_fixup;
    int retry_max;
};

enum pregap_observation {
    PREGAP_OBS_NONE,        /* no frame: CRC mismatches, or an address no disc has */
    PREGAP_OBS_ELSEWHERE,   /* a frame of another sector than the one wanted */
    PREGAP_OBS_HERE,        /* the wanted sector's frame */
};

/* Reads the Q frame for sector `want` and moves the bounds by what that frame
 * says about the sector it belongs to.
 *
 * Until 2026-10-21 every frame was taken to belong to the sector asked for.
 * The search is otherwise a function of the frames it is given, so two
 * searches of one disc can only disagree if the drive answered some request
 * with another sector's frame, or a corrupt frame passed its CRC (one in
 * 65,536). The rig's filed rips of the reference disc, all on one drive, gave
 * track 9's pregap as 94 frames or 95, and track 4's as 158 or none
 * (subchannel-pregap-varies; tools/cross-rip.py counts them). tests/subq.c
 * reproduces both with the search as it was: one read answered by the next
 * sector's frame gives 95, and a first read answered by a frame of the
 * previous track gives none.
 * A frame's own address says which sector it is, so the frame is placed
 * there, and the reads after it are aimed by how far off the drive answers.
 * On a drive whose every frame answers for the sector asked, the answer is
 * the same as before.
 *
 * Returns a driver error, or 0 with *moved set when a bound moved and *seen
 * saying whose frame came back. */
static driver_return_code_t pregap_observe(struct pregap_search *s, lsn_t want,
                                           int *moved, enum pregap_observation *seen)
{
    lsn_t ask = want - s->shift;
    if (ask < s->first_readable)
        ask = s->first_readable;
    if (ask > s->last_readable)
        ask = s->last_readable;

    *moved = 0;
    *seen = PREGAP_OBS_NONE;

    int valid;
    driver_return_code_t ret = read_audio_subq_sector_with_retries(
        s->read, s->opaque, s->audio_subq_buf, ask, s->retry_max,
        &s->needs_bcd_fixup, &valid);
    if (ret || !valid)
        return ret;

    subq_t subq;
    decode_subq(&subq, s->audio_subq_buf + CDIO_CD_FRAMESIZE_RAW);

    const lsn_t expected = ask + s->shift;
    const lsn_t at = subq_frame_lsn(&subq, expected);
    if (at == CDIO_INVALID_LSN)
        return 0;

    if (subq.adr != 1) {
        *seen = at == expected && at == want ? PREGAP_OBS_HERE : PREGAP_OBS_ELSEWHERE;
        /* A mode-2 or mode-3 frame names no track. One right after the
         * previous track's last known sector is taken as the previous
         * track's, as it always was, but only where the drive's alignment
         * puts it: placed by its frame number alone, it could be a second
         * away. */
        if (at == expected && at == want && at == s->left_bound + 1) {
            s->left_bound = at;
            *moved = 1;
        }
        return 0;
    }

    *seen = at == want ? PREGAP_OBS_HERE : PREGAP_OBS_ELSEWHERE;

    /* One frame off is a slip; two in a row the same distance off is how this
     * drive answers, and the reads are aimed by it from then on. */
    const int delta = at - ask;
    if (delta <= SUBQ_MAX_SHIFT && -delta <= SUBQ_MAX_SHIFT) {
        if (delta == s->last_delta)
            s->shift = delta;
        s->last_delta = delta;
    }

    /* A frame of either track outside the bounds says nothing new, and one
     * that contradicts them, the previous track's at or after a sector known
     * to be this one's or the reverse, is not believed. A frame of any other
     * track says nothing about this boundary. */
    if (at <= s->left_bound || at >= s->right_bound)
        return 0;

    if (subq.track_number == s->prev_track_number) {
        s->left_bound = at;
        *moved = 1;
    } else if (subq.track_number == s->track_number) {
        s->right_bound = at;
        *moved = 1;
    }

    return 0;
}

/* The search proper: from the TOC's start of the previous track and of this
 * one, find the first sector whose Q frame names this track. */
static lsn_t pregap_search_subq(subq_read_fn read, void *opaque,
                                const track_t track_number,
                                const lsn_t prev_track_start_lsn,
                                const lsn_t track_start_lsn,
                                enum cyanrip_pregap_source *source)
{
#define SET_SOURCE(v) do { if (source) *source = (v); } while (0)

    struct pregap_search s = {
        .read = read,
        .opaque = opaque,
        .prev_track_number = track_number - 1,
        .track_number = track_number,
        .left_bound = prev_track_start_lsn,
        .right_bound = track_start_lsn,
        .first_readable = prev_track_start_lsn,
        .last_readable = track_start_lsn - 1,
        // UltraFuzzy: Based on brief informal testing, successful subchannel Q read
        // retries become rare after ~5-10 attempts but I've seen a correct read
        // first occur as late as 180 attempts. The large harder_retry_max value
        // will only be used for bad sectors that cannot be ruled out as possibly
        // containing the start of a pregap. This should be rare and when it does
        // happen these sectors must be read for pregap finding to succeed.
        .retry_max = 5,
    };
    const int harder_retry_max = 200;
    driver_return_code_t ret;
    int moved;
    enum pregap_observation seen;

    // The main idea of this algorithm is to track a left bound, representing
    // our current latest known sector that belongs to the previous track, and a
    // right bound, representing our current earliest known sector that belongs
    // to the pregap. We traverse between our known boundaries contracting
    // them when possible until they converge or until CRC mismatches make that
    // impossible. When encountering bad sectors with repeated CRC mismatches we
    // sometimes attempt to skip over them and find a good sector that we can
    // use to contract our bounds and rule out the bad sectors from containing
    // the start of the pregap.

    // A previous track of a single sector leaves nothing to search.
    if (s.left_bound + 1 == s.right_bound) {
        SET_SOURCE(CYANRIP_PREGAP_SRC_SUBCHANNEL);
        return s.right_bound;
    }

    // Check one sector before track start to see if there is any pregap.
    if ((ret = pregap_observe(&s, track_start_lsn - 1, &moved, &seen))) {
        /* Persistent read failure: give up on detection rather than crash the
         * rip over what optical drives treat as a routine condition. */
        SET_SOURCE(CYANRIP_PREGAP_SRC_ERR_READ);
        return CDIO_INVALID_LSN;
    }

    // There is a pregap or the result was ambiguous. Backtrack in 2
    // second increments until we find a position that can be confirmed to be
    // before any pregap. A 2 second pregap is common so this will often
    // backtrack right to the pregap boundary.
    const lsn_t backtrack = 150;
    lsn_t lsn = track_start_lsn - 1;
    while (s.left_bound + 1 != s.right_bound && s.left_bound < lsn) {
        lsn = lsn - backtrack >= prev_track_start_lsn ? lsn - backtrack : prev_track_start_lsn;
        if (lsn <= s.left_bound)
            break;
        if ((ret = pregap_observe(&s, lsn, &moved, &seen))) {
            SET_SOURCE(CYANRIP_PREGAP_SRC_ERR_READ);
            return CDIO_INVALID_LSN;
        }
    }

    // Loop over sectors from left bound to right bound attempting to contract
    // bounds until they meet. Skip over sectors with repeated bad CRCs and
    // attempt to find a good sector that allows us to contract the bounds and
    // rule out those bad sectors as the pregap start.
    lsn = s.left_bound;
    int elsewhere = 0;
    while (s.left_bound + 1 != s.right_bound) {
        lsn += 1;
        if (lsn >= s.right_bound) {
            // Skipping over sectors with bad CRCs failed.
            // If we've already been here, give up.
            if (s.retry_max == harder_retry_max)
                break;
            // Getting here means we skipped over bad sectors that it turns must
            // be read in order to decide where the pregap starts. TRY HARDER.
            s.retry_max = harder_retry_max;
            lsn = s.left_bound;
            continue;
        }
        if ((ret = pregap_observe(&s, lsn, &moved, &seen))) {
            SET_SOURCE(CYANRIP_PREGAP_SRC_ERR_READ);
            return CDIO_INVALID_LSN;
        }
        if (moved) {
            // A bound moved: carry on from the previous track's last known sector.
            lsn = s.left_bound;
            elsewhere = 0;
        } else if (seen == PREGAP_OBS_ELSEWHERE && elsewhere++ < s.retry_max) {
            // Another sector's frame said nothing new: ask for this one again,
            // as often as a frame that fails its CRC would be.
            lsn -= 1;
        } else {
            elsewhere = 0;
        }
    }

    // Bounds failed to converge (repeated CRC mismatches even at harder_retry_max):
    // report "unknown" rather than a bogus LSN. CDIO_INVALID_LSN is the sentinel
    // every caller in this codebase already checks for, unlike DRIVER_OP_ERROR
    // (a small negative driver-error code, easily mistaken for a real LSN by a
    // caller that only ever compares against CDIO_INVALID_LSN).
    if (s.left_bound + 1 == s.right_bound) {
        SET_SOURCE(CYANRIP_PREGAP_SRC_SUBCHANNEL);
        return s.right_bound;
    }

    SET_SOURCE(CYANRIP_PREGAP_SRC_ERR_CRC);
    return CDIO_INVALID_LSN;
#undef SET_SOURCE
}


/* The twelve characters of the ISRC a mode-3 Q frame carries, in its bytes 1
 * to 8: five of six bits each, '0' to '9' as 0 to 9 and 'A' to 'Z' as 17 to
 * 42, two zero bits, then seven of four bits each, the digits, and four zero
 * bits (IEC 60908; cdrdao's SubChannel::decodeIsrcCode() reads it the same
 * way). Returns 0 for a value no ISRC character has. */
static int subq_decode_isrc(const uint8_t *q, char isrc[CDIO_ISRC_SIZE + 1])
{
    const uint32_t a = (uint32_t)q[1] << 24 | (uint32_t)q[2] << 16 |
                       (uint32_t)q[3] << 8 | q[4];

    for (int i = 0; i < 5; i++) {
        const int c = (a >> (26 - 6*i)) & 0x3F;
        if (c <= 9)
            isrc[i] = '0' + c;
        else if (c >= 17 && c <= 42)
            isrc[i] = 'A' + c - 17;
        else
            return 0;
    }

    for (int i = 0; i < 7; i++) {
        const int c = (q[5 + i/2] >> (i % 2 ? 0 : 4)) & 0x0F;
        if (c > 9)
            return 0;
        isrc[5 + i] = '0' + c;
    }

    isrc[CDIO_ISRC_SIZE] = '\0';
    return 1;
}

/* Whether a frame's CRC checks, as read or with the raw-binary drive's fields
 * re-encoded to BCD, on a copy: a mode-3 frame's bytes are not BCD fields, so
 * the pregap search's sticky fixup would turn a good one into a bad one. */
static int subq_frame_valid(const uint8_t *q)
{
    const unsigned crc_read = (q[10] << 8) | q[11];
    uint8_t copy[12];

    if (!crc_read)
        return 0;
    if (crc_read == crc_subq(q))
        return 1;
    memcpy(copy, q, sizeof(copy));
    fixup_subq_to_bcd(copy);
    return crc_read == crc_subq(copy);
}

static void subq_isrc_scan(subq_read_fn read, void *opaque, lsn_t first, int count,
                           struct cyanrip_subq_isrc *res)
{
    uint8_t audio_subq_buf[CYANRIP_CD_FRAMESIZE_RAW_AND_SUBQ];
    const uint8_t *q = audio_subq_buf + CDIO_CD_FRAMESIZE_RAW;

    memset(res, 0, sizeof(*res));

    for (int i = 0; i < count; i++) {
        if (read(opaque, audio_subq_buf, first + i)) {
            res->read_failed = 1;
            return;
        }
        res->frames_read++;
        if (!subq_frame_valid(q))
            continue;
        res->frames_valid++;
        if ((q[0] & 0x0F) != 3)
            continue;
        res->isrc_frames++;
        if (subq_decode_isrc(q, res->isrc)) {
            res->found = 1;
            return;
        }
    }
}

void cyanrip_read_isrc_subq(CdIo_t *p_cdio, lsn_t first, int count,
                            struct cyanrip_subq_isrc *res)
{
    subq_isrc_scan(read_subq_from_drive, p_cdio, first, count, res);
}

void cyanrip_subq_isrc_reason(const struct cyanrip_subq_isrc *res, char *buf, size_t size)
{
    if (res->read_failed && !res->frames_read)
        snprintf(buf, size, "libcdio returned none, also after the drive refused "
                 "to read the track's Q frames");
    else if (!res->frames_valid)
        snprintf(buf, size, "libcdio returned none, also after reading %i Q frames "
                 "of the track, none passing its CRC", res->frames_read);
    else if (!res->isrc_frames)
        snprintf(buf, size, "libcdio returned none, also after reading %i Q frames "
                 "of the track, none an ISRC frame", res->frames_read);
    else
        snprintf(buf, size, "libcdio returned none, also after reading %i Q frames "
                 "of the track, %i ISRC frames, none well formed",
                 res->frames_read, res->isrc_frames);
}

/* An earlier TODO here asked whether the drive is actually returning Q
 * sub-channel data rather than zeroes. It is: verify_subq_crc() rejects a
 * zero CRC outright, because a drive that returns nothing leaves the buffer
 * zeroed and an all-zero block checksums as valid. tests/subq.c pins it
 * (`all-zero sector accepted`). The comment outlived the fix and was asserting
 * an unaddressed problem that is addressed -- removed 2026-08-13. */
lsn_t cyanrip_get_track_pregap_lsn(CdIo_t *p_cdio, const track_t track_number,
                                   enum cyanrip_pregap_source *source) {
#define SET_SOURCE(v) do { if (source) *source = (v); } while (0)

    SET_SOURCE(CYANRIP_PREGAP_SRC_NONE);

    // Try to use libcdio. If libcdio doesn't implement pregap finding
    // for a driver, it will return CDIO_INVALID_LSN.
    const lsn_t cdio_track_pregap_lsn = cdio_get_track_pregap_lsn(p_cdio, track_number);
    if (cdio_track_pregap_lsn != CDIO_INVALID_LSN) {
        SET_SOURCE(CYANRIP_PREGAP_SRC_TOC);
        return cdio_track_pregap_lsn;
    }

    // First track pregap is lsn = 0, lba = CDIO_PREGAP_SECTORS.
    // TODO Under what circumstances does libcdio give a first track not equal
    // to 1? Does this ever happen for a rippable CD?
    const track_t first_track_number = cdio_get_first_track_num(p_cdio);
    if (track_number == first_track_number) {
        SET_SOURCE(CYANRIP_PREGAP_SRC_LEADIN);
        return 0;
    }

    const lsn_t track_start_lsn = cdio_get_track_lsn(p_cdio, track_number);
    // TODO Is (track_number - 1) always safe? e.g. non-continuous track numbers?
    const uint8_t prev_track_number = track_number - 1;
    const lsn_t prev_track_start_lsn = cdio_get_track_lsn(p_cdio, prev_track_number);

    /* Neither return value was checked before 2026-08-13. cdio_get_track_lsn()
     * answers CDIO_INVALID_LSN when it cannot say, and the comparison below
     * would then do arithmetic on a sentinel and report the result as a pregap
     * LSN -- a number that was never measured, in a record whose whole purpose
     * is that its numbers were. No disc has been seen to reach this, which is
     * exactly why it is a guard and not a fix: the cost is three lines and the
     * failure it prevents is unfalsifiable after the fact. */
    if (!track_lsns_usable(track_start_lsn, prev_track_start_lsn)) {
        SET_SOURCE(CYANRIP_PREGAP_SRC_ERR_READ);
        return CDIO_INVALID_LSN;
    }

    return pregap_search_subq(read_subq_from_drive, p_cdio, track_number,
                              prev_track_start_lsn, track_start_lsn, source);
#undef SET_SOURCE
}
