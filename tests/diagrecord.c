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

/* The -j record's /8 fields, built from a context rather than from a rip.
 *
 * Round 32 added them (our lap 1 S10, Platterpus's lap 2 S7 and S8). Most of
 * their states no disc image reaches: libcdio's image drivers never report
 * the ISRC capability, so `isrc_disc` is null on every image; no image has
 * pre-emphasis in its sub-channel; and an -f search on an image ends only one
 * way, with no AccurateRip entry. So the states are BUILT, the same move as
 * tests/diagcache.c and tests/logrender.c: fill a context in, call the shipped
 * snapshot and writer, and compare what they wrote.
 *
 * diagnostics.c writes one record per process, so each record is written by
 * a forked child and read back by the parent. */

#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#include "cyanrip_main.h"
#include "diagnostics.h"
#include "cache_probe.h"

static int failures;

#define CHECK(cond, ...)                                                      \
    do {                                                                      \
        if (!(cond)) {                                                        \
            failures++;                                                       \
            fprintf(stderr, "FAIL %s:%d: ", __func__, __LINE__);              \
            fprintf(stderr, __VA_ARGS__);                                     \
            fprintf(stderr, "\n");                                            \
        }                                                                     \
    } while (0)

/* What diagnostics.c expects from the rest of the program. Same stub set as
 * tests/diag.c and tests/diagcache.c. */
char *crip_invocation = (char *)"cyanrip (diag record unit test)";
volatile sig_atomic_t quit_now = 0;
volatile sig_atomic_t quit_signal = 0;
const char *vcstag = "diagrecord-unit-test";

void cyanrip_log(cyanrip_ctx *ctx, int verbose, const char *format, ...);
void cyanrip_log(cyanrip_ctx *ctx, int verbose, const char *format, ...)
{
    (void)ctx; (void)verbose; (void)format;
}

static const crip_cache_evidence_t no_probe;

const crip_cache_evidence_t *crip_cache_evidence(void)
{
    return &no_probe;
}

static char *slurp(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (!f)
        return NULL;
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = malloc(n + 1);
    if (buf && fread(buf, 1, n, f) != (size_t)n) {
        free(buf);
        buf = NULL;
    }
    if (buf)
        buf[n] = '\0';
    fclose(f);
    return buf;
}

/* Writes the record for ctx from a child process and returns its text. */
static char *write_record(cyanrip_ctx *ctx, const char *path)
{
    unlink(path);
    fflush(NULL);
    pid_t pid = fork();
    if (pid == 0) {
        crip_diag_enable(path);
        crip_diag_set_exit(0);
        crip_diag_snapshot(ctx);
        crip_diag_write();
        _exit(0);
    }
    int status = 0;
    if (pid < 0 || waitpid(pid, &status, 0) != pid || !WIFEXITED(status)) {
        CHECK(0, "the child writing %s did not exit normally", path);
        return NULL;
    }
    char *out = slurp(path);
    CHECK(out, "no record at %s", path);
    unlink(path);
    return out;
}

/* A line of the record must be exactly `want`, after its indentation. A
 * substring over the whole document would be satisfied by the document being
 * wrong somewhere else, so each track line is compared whole. */
static void expect_line(const char *out, const char *want, const char *what)
{
    const char *p = out;
    while (p && *p) {
        const char *eol = strchr(p, '\n');
        size_t len = eol ? (size_t)(eol - p) : strlen(p);
        const char *s = p;
        while (len && (*s == ' ')) {
            s++;
            len--;
        }
        if (len && s[len - 1] == ',')
            len--;
        if (len == strlen(want) && !strncmp(s, want, len))
            return;
        p = eol ? eol + 1 : NULL;
    }
    CHECK(0, "%s: no line\n  %s\nin\n%s", what, want, out);
}

static cyanrip_ctx *new_ctx(void)
{
    cyanrip_ctx *ctx = calloc(1, sizeof(*ctx));
    if (!ctx) {
        fprintf(stderr, "out of memory\n");
        exit(1);
    }
    for (int i = 0; i < 6; i++) {
        ctx->tracks[i].number = i + 1;
        ctx->tracks[i].cd_track_number = i + 1;
    }
    ctx->nb_tracks = ctx->nb_cd_tracks = 6;
    return ctx;
}

/* Every dictionary and string a test sets, for all six tracks whatever
 * nb_tracks was cut to: the sanitizer build's LeakSanitizer aborts on them. */
static void free_ctx(cyanrip_ctx *ctx)
{
    for (int i = 0; i < 6; i++) {
        av_dict_free(&ctx->tracks[i].meta);
        av_dict_free(&ctx->tracks[i].cdtext);
        av_freep(&ctx->tracks[i].isrc_disc);
        crip_error_pos_free(&ctx->tracks[i]);
        av_freep(&ctx->tracks[i].block_crcs);
        for (int j = 0; j < ctx->tracks[i].nb_reads; j++) {
            av_freep(&ctx->tracks[i].reads[j].block_crcs);
            av_freep(&ctx->tracks[i].reads[j].file);
        }
        av_freep(&ctx->tracks[i].reads);
    }
    av_dict_free(&ctx->cdtext);
    free(ctx);
}

static void test_track_fields(void)
{
    cyanrip_ctx *ctx = new_ctx();
    ctx->settings.deemphasis = 1;   /* -W: de-emphasise what is pre-emphasised */

    /* 1: no pre-emphasis; files ripped, carrying a -t ISRC with a quote and a
     * backslash in it, beside a different ISRC the disc reported. */
    cyanrip_track *t = &ctx->tracks[0];
    t->extra_read = 1;
    t->audio_ripped = 1;
    av_dict_set(&t->meta, "isrc", "AA\"BB\\CC", 0);
    t->isrc_disc = av_strdup("ZZZZZ9999999");
    t->isrc_disc_read = "q frames";
    t->kept_read_began = 1800000000;   /* /11: 2027-01-15T08:00:00Z */
    t->encode_failures = 1;

    /* 2: pre-emphasis in the sub-channel, de-emphasised; a -t ISRC, but no
     * files of this track, so the files carry nothing. */
    t = &ctx->tracks[1];
    t->extra_read = 1;
    t->preemphasis = t->preemphasis_in_subcode = 1;
    av_dict_set(&t->meta, "isrc", "YYYYY0000002", 0);
    t->isrc_disc_reason = "libcdio returned none";

    /* 3: pre-emphasis in the TOC, de-emphasised. */
    t = &ctx->tracks[2];
    t->extra_read = 1;
    t->audio_ripped = 1;
    t->preemphasis = 1;
    t->isrc_disc_reason = "libcdio returned an empty ISRC";

    /* 4: a data track whose sectors were copied: no extra read, the reason
     * says why, and data_ripped, not audio_ripped, is true. */
    ctx->tracks[3].track_is_data = 1;
    ctx->tracks[3].data_ripped = 1;

    /* 5: an audio track track_read_extra() never ran for. */

    /* 6: read, no pre-emphasis, and the driver cannot read ISRC. */
    t = &ctx->tracks[5];
    t->extra_read = 1;
    t->audio_ripped = 1;
    t->isrc_disc_reason = "the driver does not report reading ISRC";

    char *out = write_record(ctx, "diagrecord_tracks.json");
    free_ctx(ctx);
    if (!out)
        return;

    CHECK(strstr(out, "\"schema\": \"cyanrip-diagnostics/13\""),
          "the schema is not cyanrip-diagnostics/13");

    expect_line(out, "{\"number\":1,\"cd_track\":1,\"repeats\":0,\"audio_ripped\":true,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,\"data_ripped\":false,"
                     "\"preemphasis\":\"none\",\"deemphasis_applied\":false,"
                     "\"isrc_written\":\"AA\\\"BB\\\\CC\",\"isrc_disc\":\"ZZZZZ9999999\","
                     "\"isrc_disc_reason\":null,\"isrc_disc_read\":\"q frames\",\"kept_read_began\":\"2027-01-15T08:00:00Z\",\"block_crcs\":null,\"reads\":null,\"encode_failures\":1,\"paranoia_all_reads\":null,\"error_positions\":null,\"error_positions_dropped\":null}", "track 1");
    expect_line(out, "{\"number\":2,\"cd_track\":2,\"repeats\":0,\"audio_ripped\":false,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,\"data_ripped\":false,"
                     "\"preemphasis\":\"subcode\",\"deemphasis_applied\":true,"
                     "\"isrc_written\":null,\"isrc_disc\":null,"
                     "\"isrc_disc_reason\":\"libcdio returned none\",\"isrc_disc_read\":null,\"kept_read_began\":null,\"block_crcs\":null,\"reads\":null,\"encode_failures\":0,\"paranoia_all_reads\":null,\"error_positions\":null,\"error_positions_dropped\":null}",
                "track 2");
    expect_line(out, "{\"number\":3,\"cd_track\":3,\"repeats\":0,\"audio_ripped\":true,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,\"data_ripped\":false,"
                     "\"preemphasis\":\"toc\",\"deemphasis_applied\":true,"
                     "\"isrc_written\":null,\"isrc_disc\":null,"
                     "\"isrc_disc_reason\":\"libcdio returned an empty ISRC\","
                     "\"isrc_disc_read\":null,\"kept_read_began\":null,\"block_crcs\":null,\"reads\":null,\"encode_failures\":0,\"paranoia_all_reads\":null,\"error_positions\":null,\"error_positions_dropped\":null}", "track 3");
    expect_line(out, "{\"number\":4,\"cd_track\":4,\"repeats\":0,\"audio_ripped\":false,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,\"data_ripped\":true,"
                     "\"preemphasis\":null,\"deemphasis_applied\":null,"
                     "\"isrc_written\":null,\"isrc_disc\":null,"
                     "\"isrc_disc_reason\":\"data track\",\"isrc_disc_read\":null,\"kept_read_began\":null,\"block_crcs\":null,\"reads\":null,\"encode_failures\":0,\"paranoia_all_reads\":null,\"error_positions\":null,\"error_positions_dropped\":null}", "track 4");
    expect_line(out, "{\"number\":5,\"cd_track\":5,\"repeats\":0,\"audio_ripped\":false,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,\"data_ripped\":false,"
                     "\"preemphasis\":null,\"deemphasis_applied\":null,"
                     "\"isrc_written\":null,\"isrc_disc\":null,"
                     "\"isrc_disc_reason\":\"not read\",\"isrc_disc_read\":null,\"kept_read_began\":null,\"block_crcs\":null,\"reads\":null,\"encode_failures\":0,\"paranoia_all_reads\":null,\"error_positions\":null,\"error_positions_dropped\":null}", "track 5");
    expect_line(out, "{\"number\":6,\"cd_track\":6,\"repeats\":0,\"audio_ripped\":true,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,\"data_ripped\":false,"
                     "\"preemphasis\":\"none\",\"deemphasis_applied\":false,"
                     "\"isrc_written\":null,\"isrc_disc\":null,"
                     "\"isrc_disc_reason\":\"the driver does not report reading ISRC\","
                     "\"isrc_disc_read\":null,\"kept_read_began\":null,\"block_crcs\":null,\"reads\":null,\"encode_failures\":0,\"paranoia_all_reads\":null,\"error_positions\":null,\"error_positions_dropped\":null}", "track 6");

    /* No CD-TEXT and no -f: the absent arm names what libcdio reported, every
     * key is still written, and offset_search is null, not an object. */
    expect_line(out, "\"status\": \"none reported by libcdio\"", "cdtext absent");
    expect_line(out, "\"language\": null", "cdtext absent language");
    expect_line(out, "\"disc\": {\"title\":null,\"performer\":null,\"songwriter\":null,"
                     "\"composer\":null,\"message\":null,\"arranger\":null,\"isrc\":null,"
                     "\"upc_ean\":null,\"genre\":null,\"discid\":null}", "cdtext absent disc");
    expect_line(out, "\"offset_search\": null", "no -f");
    free(out);
}

/* -W with a track that is not pre-emphasised, and -E (forced): the predicate is
 * the one the log and the cue use, so forced reads true even without it. */
static void test_deemphasis_forced(void)
{
    cyanrip_ctx *ctx = new_ctx();
    ctx->settings.force_deemphasis = 1;
    ctx->tracks[0].extra_read = 1;
    ctx->nb_tracks = 1;

    char *out = write_record(ctx, "diagrecord_forced.json");
    free_ctx(ctx);
    if (!out)
        return;
    expect_line(out, "{\"number\":1,\"cd_track\":1,\"repeats\":0,\"audio_ripped\":false,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,\"data_ripped\":false,"
                     "\"preemphasis\":\"none\",\"deemphasis_applied\":true,"
                     "\"isrc_written\":null,\"isrc_disc\":null,"
                     "\"isrc_disc_reason\":null,\"isrc_disc_read\":null,\"kept_read_began\":null,\"block_crcs\":null,\"reads\":null,\"encode_failures\":0,\"paranoia_all_reads\":null,\"error_positions\":null,\"error_positions_dropped\":null}", "forced");
    free(out);
}

/* A code the disc returned that is not an ISO 3901 code (round 35, our lap 4
 * S5): kept as isrc_disc, with the reason beside it that a code alone never
 * has, the words the Disc ISRC: line prints. */
static void test_isrc_disc_malformed(void)
{
    cyanrip_ctx *ctx = new_ctx();
    ctx->tracks[0].extra_read = 1;
    ctx->tracks[0].audio_ripped = 1;
    ctx->tracks[0].isrc_disc = av_strdup("1234567890AB");
    ctx->tracks[0].isrc_disc_reason = "not an ISO 3901 code, so not used";
    ctx->tracks[0].isrc_disc_malformed = 1;
    ctx->nb_tracks = 1;

    char *out = write_record(ctx, "diagrecord_malformed.json");
    free_ctx(ctx);
    if (!out)
        return;
    expect_line(out, "{\"number\":1,\"cd_track\":1,\"repeats\":0,\"audio_ripped\":true,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,\"data_ripped\":false,"
                     "\"preemphasis\":\"none\",\"deemphasis_applied\":false,"
                     "\"isrc_written\":null,\"isrc_disc\":\"1234567890AB\","
                     "\"isrc_disc_reason\":\"not an ISO 3901 code, so not used\","
                     "\"isrc_disc_read\":null,\"kept_read_began\":null,\"block_crcs\":null,\"reads\":null,\"encode_failures\":0,\"paranoia_all_reads\":null,\"error_positions\":null,\"error_positions_dropped\":null}", "malformed");
    free(out);
}

/* /12's block_crcs (our round 38 lap 1 S10, Platterpus's lap 2 S7): the
 * per-second CRCs as 8-digit hex strings, in order, for a finished read;
 * null as a whole when memory for them could not be had, as eac_crc is null
 * where no read finished. */
static void test_block_crcs(void)
{
    cyanrip_ctx *ctx = new_ctx();
    for (int i = 0; i < 2; i++) {
        cyanrip_track *t = &ctx->tracks[i];
        t->audio_ripped = 1;
        t->computed_crcs = 1;
        t->eac_crc = 0xCAFEF00D;
        t->block_crcs = av_malloc_array(2, sizeof(*t->block_crcs));
        if (!t->block_crcs) {
            free_ctx(ctx);
            CHECK(0, "out of memory");
            return;
        }
        t->block_crcs[0] = 0x0000ABCD;
        t->block_crcs[1] = 0x12345678;
        t->nb_block_crcs = 2;
    }
    ctx->tracks[1].block_crcs_failed = 1;
    ctx->nb_tracks = 2;

    char *out = write_record(ctx, "diagrecord_block_crcs.json");
    free_ctx(ctx);
    if (!out)
        return;
    CHECK(strstr(out, "\"eac_crc\":\"CAFEF00D\""), "no eac_crc for the finished read");
    CHECK(strstr(out, "\"block_crcs\":[\"0000ABCD\",\"12345678\"]"),
          "track 1's block_crcs are not its two CRCs, in order, as hex strings");
    const char *two = strstr(out, "{\"number\":2,");
    CHECK(two && strstr(two, "\"block_crcs\":null"),
          "track 2's block_crcs are not null after memory failed");
    free(out);
}

/* /13's reads (round 38, Platterpus's docs/eac-parity.md Part G.5): every
 * distinct -Z read, in the order first read, with its own block_crcs, null
 * as a whole when memory for them could not be had, and the file it was
 * saved to as a JSON string, null when none was. The image scenario
 * every_read cannot reach either null, nor a name that needs escaping. */
static void test_reads(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track *t = &ctx->tracks[0];
    ctx->nb_tracks = 2;
    t->reads = av_calloc(2, sizeof(*t->reads));
    if (!t->reads || !(t->reads[0].block_crcs = av_malloc_array(2, sizeof(uint32_t))) ||
        !(t->reads[0].file = av_strdup("dir/\"q\".wav"))) {
        free_ctx(ctx);
        CHECK(0, "out of memory");
        return;
    }
    t->nb_reads = 2;
    t->reads[0] = (crip_read){ .crc = 0x0BADF00D, .count = 2, .last_read = 3,
                               .ar_v1 = 0x1, .ar_v2 = 0xFFFFFFFF,
                               .block_crcs = t->reads[0].block_crcs,
                               .nb_block_crcs = 2, .file = t->reads[0].file };
    t->reads[0].block_crcs[0] = 0x0000ABCD;
    t->reads[0].block_crcs[1] = 0x12345678;
    t->reads[1] = (crip_read){ .crc = 0xCAFEF00D, .count = 1, .last_read = 4,
                               .kept = 1, .ar_v1 = 0xA, .ar_v2 = 0xB };

    char *out = write_record(ctx, "diagrecord_reads.json");
    free_ctx(ctx);
    if (!out)
        return;
    CHECK(strstr(out, "\"reads\":[{\"eac_crc\":\"0BADF00D\",\"count\":2,\"last_read\":3,"
                      "\"kept\":false,\"accurip_v1\":\"00000001\",\"accurip_v2\":\"FFFFFFFF\","
                      "\"block_crcs\":[\"0000ABCD\",\"12345678\"],\"file\":\"dir/\\\"q\\\".wav\"},"
                      "{\"eac_crc\":\"CAFEF00D\",\"count\":1,\"last_read\":4,\"kept\":true,"
                      "\"accurip_v1\":\"0000000A\",\"accurip_v2\":\"0000000B\","
                      "\"block_crcs\":null,\"file\":null}]"),
          "track 1's reads are not its two reads, in order, with the second's "
          "block_crcs and file null and the first's file escaped");
    const char *two = strstr(out, "{\"number\":2,");
    CHECK(two && strstr(two, "\"reads\":null"), "track 2, never read, has reads");
    free(out);
}

/* /13's drive_declared (drive_caps.h): null where nothing was asked, as on
 * every image; otherwise each reply as answered, whole, in hex, with the
 * length its header declares and whether that is more than was kept, the CD
 * Read feature read out of the GET CONFIGURATION reply, and the four MODE
 * SENSE replies in page-control order. Only a drive answers, so the shapes
 * an image cannot reach are built here: a reply kept whole, one cut short,
 * one refused, and a feature list without 001Eh. */
static void set_reply(CripReply *r, int answered, int length, const uint8_t *b, int nb)
{
    *r = (CripReply){ .asked = 1, .answered = answered, .length = length,
                      .nb_bytes = nb };
    if (nb)
        memcpy(r->bytes, b, nb);
}

/* --read-vendor-settings, in drive_declared's vendor_settings: asked for or
 * not; for a drive no table row names, nothing sent and every field after
 * "requested" null; for Pioneer's row, its source and command, the reply
 * whole in hex, and PureRead read from it, tri-state, the mode only where
 * supported. Only a Pioneer drive answers, so each shape is built here. */
static void expect_vendor(cyanrip_ctx *ctx, const char *file, const char *pureread,
                          const char *what)
{
    char *out = write_record(ctx, file);
    if (!out)
        return;
    char want[1024], hex[513] = "";
    for (int i = 0; ctx->drive_vendor.answered && i < ctx->drive_vendor.nb_bytes; i++)
        snprintf(hex + 2 * i, 3, "%02X", ctx->drive_vendor.bytes[i]);
    if (ctx->drive_vendor.answered)
        snprintf(want, sizeof(want),
                 "\"vendor_settings\": {\"requested\":true,\"query\":\"pioneer-f4\","
                 "\"source\":\"pioneer-optical@d2cbbf2:src/settings/f4.rs:92-94 "
                 "(READ BUFFER, mode 02h, buffer F4h, 256 bytes)\","
                 "\"cdb\":\"3C02F400000000010000\",\"answered\":true,\"length\":256,"
                 "\"truncated\":false,\"bytes\":\"%s\",\"pureread\":%s}", hex, pureread);
    else
        snprintf(want, sizeof(want),
                 "\"vendor_settings\": {\"requested\":true,\"query\":\"pioneer-f4\","
                 "\"source\":\"pioneer-optical@d2cbbf2:src/settings/f4.rs:92-94 "
                 "(READ BUFFER, mode 02h, buffer F4h, 256 bytes)\","
                 "\"cdb\":\"3C02F400000000010000\",\"answered\":false,\"length\":null,"
                 "\"truncated\":null,\"bytes\":null,\"pureread\":null}");
    expect_line(out, want, what);
    free(out);
}

static void test_vendor_settings(cyanrip_ctx *ctx)
{
    uint8_t inq[36] = { 0x05, 0x80, 0x00, 0x32, 31 };
    memcpy(inq + 8, "PIONEER BD-RW   BDR-209D", 24);
    set_reply(&ctx->drive_inquiry, 1, 36, inq, 36);
    ctx->settings.read_vendor_settings = 1;

    /* Asked for, and a drive no row names: nothing sent */
    ctx->drive_vendor_query = NULL;
    char *out = write_record(ctx, "diagrecord_vendor_none.json");
    if (out) {
        expect_line(out, "\"vendor_settings\": {\"requested\":true,\"query\":null,"
                         "\"source\":null,\"cdb\":null,\"answered\":null,\"length\":null,"
                         "\"truncated\":null,\"bytes\":null,\"pureread\":null}",
                    "asked for, no row for the drive");
        free(out);
    }

    /* Pioneer's row, a valid block: support 1, Master (1, 8) */
    uint8_t f4[256];
    memset(f4, 0x00, sizeof(f4));
    f4[0] = 1;
    memset(f4 + 11, 0xff, 4);
    f4[4] = 1; f4[5] = 8; f4[9] = 1;
    ctx->drive_vendor_query = crip_vendor_query_for(inq, sizeof(inq));
    set_reply(&ctx->drive_vendor, 1, 256, f4, 256);
    expect_vendor(ctx, "diagrecord_vendor_master.json",
                  "{\"block_valid\":true,\"support\":\"supported\",\"mode\":\"master\"}",
                  "Pioneer's block, PureRead Master");

    /* Supported, at a level nobody has named */
    ctx->drive_vendor.bytes[5] = 7;
    expect_vendor(ctx, "diagrecord_vendor_level.json",
                  "{\"block_valid\":true,\"support\":\"supported\",\"mode\":\"not determined\"}",
                  "Pioneer's block, an unknown level");

    /* Unsupported: the mode is not read */
    ctx->drive_vendor.bytes[5] = 8;
    ctx->drive_vendor.bytes[9] = 0;
    expect_vendor(ctx, "diagrecord_vendor_unsupported.json",
                  "{\"block_valid\":true,\"support\":\"unsupported\",\"mode\":null}",
                  "Pioneer's block, PureRead unsupported");

    /* Answered with a block that fails its shape check: no state in it */
    memset(f4, 0x00, sizeof(f4));
    set_reply(&ctx->drive_vendor, 1, 256, f4, 256);
    expect_vendor(ctx, "diagrecord_vendor_zero.json",
                  "{\"block_valid\":false,\"support\":\"not determined\",\"mode\":null}",
                  "a zero-filled block");

    /* Refused, with the earlier block's bytes still in the buffer */
    f4[0] = 1;
    memset(f4 + 11, 0xff, 4);
    f4[4] = 1; f4[5] = 8; f4[9] = 1;
    set_reply(&ctx->drive_vendor, 0, 256, f4, 256);
    expect_vendor(ctx, "diagrecord_vendor_refused.json", NULL, "Pioneer's query refused");

    ctx->settings.read_vendor_settings = 0;
    ctx->drive_vendor_query = NULL;
    ctx->drive_vendor = (CripReply){ 0 };
    set_reply(&ctx->drive_inquiry, 1, 8, inq, 8);
}

static void test_drive_declared(void)
{
    cyanrip_ctx *ctx = new_ctx();
    ctx->nb_tracks = 1;
    char *out = write_record(ctx, "diagrecord_declared_none.json");
    if (out) {
        expect_line(out, "\"drive_declared\": null", "nothing asked");
        free(out);
    }

    const uint8_t inq[8] = { 0x05, 0x80, 0x00, 0x32, 0x03, 'P', 'I', 'O' };
    /* A feature list: header (current profile CD-ROM), 0000h with 4 bytes,
     * then 001Eh with DAP and C2 Flags set and its current bit */
    const uint8_t conf[24] = { 0, 0, 0, 20, 0, 0, 0, 0x08,
                               0x00, 0x00, 0x03, 0x04, 0x00, 0x08, 0x01, 0x00,
                               0x00, 0x1e, 0x09, 0x04, 0x82, 0x00, 0x00, 0x00 };
    const uint8_t page[16] = { 0x00, 0x0e, 0, 0, 0, 0, 0, 0,
                               0x01, 0x06, 0x24, 0x05, 0, 0, 0, 0 };
    set_reply(&ctx->drive_inquiry, 1, 8, inq, 8);
    set_reply(&ctx->drive_configuration, 1, 24, conf, 24);
    set_reply(&ctx->drive_mode_pages[0], 1, 16, page, 16);
    set_reply(&ctx->drive_mode_pages[1], 1, 40, page, 16);  /* cut short */
    set_reply(&ctx->drive_mode_pages[2], 1, 16, page, 16);
    ctx->drive_mode_pages[2].bytes[10] = 0x00;            /* defaults differ */
    set_reply(&ctx->drive_mode_pages[3], 0, 0, NULL, 0);    /* saved refused */

    out = write_record(ctx, "diagrecord_declared.json");
    if (out) {
        expect_line(out, "\"inquiry\": {\"answered\":true,\"length\":8,\"truncated\":false,"
                         "\"bytes\":\"058000320350494F\"}", "INQUIRY");
        expect_line(out, "\"configuration\": {\"answered\":true,\"length\":24,\"truncated\":false,"
                         "\"bytes\":\"00000014000000080000030400080100001E090482000000\"}",
                    "GET CONFIGURATION");
        expect_line(out, "\"cd_read_feature\": {\"found\":true,\"bytes\":\"001E090482000000\","
                         "\"current\":true,\"dap\":true,\"c2_flags\":true,\"cd_text\":false}",
                    "the CD Read feature, read from the feature list");
        expect_line(out, "{\"page_control\":\"current\",\"answered\":true,\"length\":16,"
                         "\"truncated\":false,\"bytes\":\"000E0000000000000106240500000000\"}",
                    "MODE SENSE, current");
        expect_line(out, "{\"page_control\":\"changeable\",\"answered\":true,\"length\":40,"
                         "\"truncated\":true,\"bytes\":\"000E0000000000000106240500000000\"}",
                    "MODE SENSE, changeable, cut short");
        expect_line(out, "{\"page_control\":\"default\",\"answered\":true,\"length\":16,"
                         "\"truncated\":false,\"bytes\":\"000E0000000000000106000500000000\"}",
                    "MODE SENSE, default");
        expect_line(out, "{\"page_control\":\"saved\",\"answered\":false,\"length\":null,"
                         "\"truncated\":null,\"bytes\":null}",
                    "MODE SENSE, saved, refused, last");
        expect_line(out, "\"vendor_settings\": {\"requested\":false,\"query\":null,"
                         "\"source\":null,\"cdb\":null,\"answered\":null,\"length\":null,"
                         "\"truncated\":null,\"bytes\":null,\"pureread\":null}",
                    "no vendor query without --read-vendor-settings");
        free(out);
    }

    test_vendor_settings(ctx);

    /* A feature list without 001Eh gives the feature's bits as null, never
     * false, and a refused list the same */
    set_reply(&ctx->drive_configuration, 1, 16, conf, 16);
    out = write_record(ctx, "diagrecord_declared_nofeature.json");
    if (out) {
        expect_line(out, "\"cd_read_feature\": {\"found\":false,\"bytes\":null,\"current\":null,"
                         "\"dap\":null,\"c2_flags\":null,\"cd_text\":null}",
                    "the CD Read feature, not in the list");
        free(out);
    }
    /* Refused, with the earlier list's bytes still in the buffer: a reply
     * the drive did not give is never read */
    set_reply(&ctx->drive_configuration, 0, 24, conf, 24);
    out = write_record(ctx, "diagrecord_declared_noconf.json");
    free_ctx(ctx);
    if (out) {
        expect_line(out, "\"configuration\": {\"answered\":false,\"length\":null,"
                         "\"truncated\":null,\"bytes\":null}", "GET CONFIGURATION refused");
        expect_line(out, "\"cd_read_feature\": {\"found\":false,\"bytes\":null,\"current\":null,"
                         "\"dap\":null,\"c2_flags\":null,\"cd_text\":null}",
                    "the CD Read feature, list refused");
        free(out);
    }
}

static void test_cdtext_present(void)
{
    cyanrip_ctx *ctx = new_ctx();
    ctx->nb_tracks = 2;
    ctx->cdtext_status = CYANRIP_CDTEXT_PRESENT;
    ctx->cdtext_language = "English";
    av_dict_set(&ctx->cdtext, "title", "Disc \"T\"", 0);
    av_dict_set(&ctx->cdtext, "genre", "Rock", 0);
    av_dict_set(&ctx->tracks[0].cdtext, "performer", "P1", 0);
    av_dict_set(&ctx->tracks[0].cdtext, "discid", "D1", 0);

    char *out = write_record(ctx, "diagrecord_cdtext.json");
    free_ctx(ctx);
    if (!out)
        return;
    expect_line(out, "\"status\": \"present\"", "cdtext status");
    expect_line(out, "\"language\": \"English\"", "cdtext language");
    expect_line(out, "\"disc\": {\"title\":\"Disc \\\"T\\\"\",\"performer\":null,"
                     "\"songwriter\":null,\"composer\":null,\"message\":null,"
                     "\"arranger\":null,\"isrc\":null,\"upc_ean\":null,\"genre\":\"Rock\","
                     "\"discid\":null}", "cdtext disc");
    expect_line(out, "{\"number\":1,\"title\":null,\"performer\":\"P1\",\"songwriter\":null,"
                     "\"composer\":null,\"message\":null,\"arranger\":null,\"isrc\":null,"
                     "\"upc_ean\":null,\"genre\":null,\"discid\":\"D1\"}", "cdtext track 1");
    expect_line(out, "{\"number\":2,\"title\":null,\"performer\":null,\"songwriter\":null,"
                     "\"composer\":null,\"message\":null,\"arranger\":null,\"isrc\":null,"
                     "\"upc_ean\":null,\"genre\":null,\"discid\":null}", "cdtext track 2");
    free(out);
}

/* Every ending of an -f search, each with the line its record must carry. Only
 * the found arm has an offset and a confidence: a stopped search is not
 * offset 0 at confidence 0. */
static void test_offset_search(void)
{
    const struct { int result; const char *want; } cases[] = {
        { CRIP_OFFSET_SEARCH_FOUND,    "\"result\": \"found\"" },
        { CRIP_OFFSET_SEARCH_NO_AR,    "\"result\": \"no AccurateRip entry\"" },
        { CRIP_OFFSET_SEARCH_NO_TRACK, "\"result\": \"no track long enough\"" },
        { CRIP_OFFSET_SEARCH_STOPPED,  "\"result\": \"stopped\"" },
    };
    for (size_t i = 0; i < sizeof(cases)/sizeof(*cases); i++) {
        cyanrip_ctx *ctx = new_ctx();
        ctx->offset_search = cases[i].result;
        ctx->offset_search_samples = -667;
        ctx->offset_search_confidence = 14;

        char path[64];
        snprintf(path, sizeof(path), "diagrecord_offset_%zu.json", i);
        char *out = write_record(ctx, path);
        free_ctx(ctx);
        if (!out)
            continue;
        expect_line(out, cases[i].want, "offset_search result");
        if (cases[i].result == CRIP_OFFSET_SEARCH_FOUND) {
            expect_line(out, "\"offset_samples\": -667", "found offset");
            expect_line(out, "\"confidence\": 14", "found confidence");
        } else {
            expect_line(out, "\"offset_samples\": null", "no offset");
            expect_line(out, "\"confidence\": null", "no confidence");
        }
        free(out);
    }
}

/* Counts entries in the one track line that starts with `prefix`. */
static int count_in_line(const char *out, const char *prefix, const char *needle)
{
    const char *p = strstr(out, prefix);
    if (!p)
        return -1;
    const char *eol = strchr(p, '\n');
    int n = 0;
    for (const char *q = p; (q = strstr(q, needle)) && (!eol || q < eol); q++)
        n++;
    return n;
}

/* Whether `needle` occurs in the line starting with `prefix`, and where. */
static const char *find_in_line(const char *out, const char *prefix, const char *needle)
{
    const char *p = strstr(out, prefix);
    if (!p)
        return NULL;
    const char *eol = strchr(p, '\n');
    const char *q = strstr(p, needle);
    return (q && (!eol || q < eol)) ? q : NULL;
}

/* /10, round 35: paranoia_all_reads, error_positions and
 * error_positions_dropped (our lap 7 S18 and S20, Platterpus's lap 8 S8 and
 * S10). The cap keeps the first 500 and the last 500, as their S8 amended
 * it, so each boundary is driven: a list that fits, one whose ring is not
 * yet full, one past the cap by one, and one well past it. */
static void test_error_positions(void)
{
    cyanrip_ctx *ctx = new_ctx();

    /* 1: read, nothing reported: every counter key, 0 where nothing was
     * counted, an empty list and 0 dropped. Not null: the read ran. */
    cyanrip_track *t = &ctx->tracks[0];
    t->read_attempted = 1;
    t->paranoia_status_all[PARANOIA_CB_READ] = 7;
    t->paranoia_status_all[PARANOIA_CB_VERIFY] = 70;

    /* 2: 700 positions, the ring half full: nothing dropped. */
    t = &ctx->tracks[1];
    t->read_attempted = 1;
    for (int i = 0; i < 700; i++)
        crip_error_pos_add(t, 1000 + i, CRIP_ERROR_POS_READ_ERROR);

    /* 3: 1001 positions: one past the cap, so exactly one is dropped, and it
     * is the first of the tail, 500, not the last. */
    t = &ctx->tracks[2];
    t->read_attempted = 1;
    for (int i = 0; i < 1001; i++)
        crip_error_pos_add(t, i, CRIP_ERROR_POS_READ_ERROR);

    /* 4: 1234 positions, every seventh a skip: the first 500, the last 500
     * oldest first, and 234 dropped from the middle. */
    t = &ctx->tracks[3];
    t->read_attempted = 1;
    t->paranoia_status_all[PARANOIA_CB_READERR] = 1057;
    t->paranoia_status_all[PARANOIA_CB_SKIP] = 177;
    for (int i = 0; i < 1234; i++)
        crip_error_pos_add(t, 5000 + i, i % 7 ? CRIP_ERROR_POS_READ_ERROR :
                                                CRIP_ERROR_POS_SKIP);

    /* 5: never read, so every one of the three is null. */

    char *out = write_record(ctx, "diagrecord_positions.json");
    free_ctx(ctx);
    if (!out)
        return;

    const char *t1 = "{\"number\":1,";
    CHECK(find_in_line(out, t1, ",\"paranoia_all_reads\":{\"READ\":7,\"VERIFY\":70,"
                       "\"FIXUP_EDGE\":0,\"FIXUP_ATOM\":0,\"SCRATCH\":0,\"REPAIR\":0,"
                       "\"SKIP\":0,\"DRIFT\":0,\"BACKOFF\":0,\"OVERLAP\":0,"
                       "\"FIXUP_DROPPED\":0,\"FIXUP_DUPED\":0,\"READERR\":0,"
                       "\"CACHEERR\":0,\"WROTE\":0,\"FINISHED\":0},"
                       "\"error_positions\":[],\"error_positions_dropped\":0}"),
          "track 1: a read with nothing reported is not every key, [] and 0");

    const char *t2 = "{\"number\":2,";
    CHECK(count_in_line(out, t2, "\"lsn\":") == 700,
          "track 2: %i entries, want all 700", count_in_line(out, t2, "\"lsn\":"));
    CHECK(find_in_line(out, t2, "\"error_positions\":[{\"lsn\":1000,\"kind\":\"read_error\"},"),
          "track 2: the list does not open with the first position");
    CHECK(find_in_line(out, t2, "{\"lsn\":1699,\"kind\":\"read_error\"}],"
                       "\"error_positions_dropped\":0}"),
          "track 2: the list does not close with the last position, 0 dropped");

    const char *t3 = "{\"number\":3,";
    CHECK(count_in_line(out, t3, "\"lsn\":") == 1000,
          "track 3: %i entries, want 1000", count_in_line(out, t3, "\"lsn\":"));
    CHECK(find_in_line(out, t3, "{\"lsn\":499,\"kind\":\"read_error\"},"
                       "{\"lsn\":501,\"kind\":\"read_error\"}"),
          "track 3: the head's last is not followed by the tail's oldest kept, 501");
    CHECK(!find_in_line(out, t3, "{\"lsn\":500,"),
          "track 3: 500, the one dropped, is in the list");
    CHECK(find_in_line(out, t3, "{\"lsn\":1000,\"kind\":\"read_error\"}],"
                       "\"error_positions_dropped\":1}"),
          "track 3: the list does not end at 1000 with 1 dropped");

    const char *t4 = "{\"number\":4,";
    CHECK(count_in_line(out, t4, "\"lsn\":") == 1000,
          "track 4: %i entries, want 1000", count_in_line(out, t4, "\"lsn\":"));
    /* Multiples of 7 among 0..499 and 734..1233: 72 in each half. */
    CHECK(count_in_line(out, t4, "\"kind\":\"skip\"") == 144,
          "track 4: %i skips kept, want 144", count_in_line(out, t4, "\"kind\":\"skip\""));
    CHECK(find_in_line(out, t4, "\"error_positions\":[{\"lsn\":5000,\"kind\":\"skip\"},"
                       "{\"lsn\":5001,\"kind\":\"read_error\"}"),
          "track 4: the list does not open 5000 skip, 5001 read_error");
    CHECK(find_in_line(out, t4, "{\"lsn\":5499,\"kind\":\"read_error\"},"
                       "{\"lsn\":5734,\"kind\":\"read_error\"}"),
          "track 4: the head's last, 5499, is not followed by the tail's oldest, 5734");
    CHECK(find_in_line(out, t4, "{\"lsn\":6233,\"kind\":\"read_error\"}],"
                       "\"error_positions_dropped\":234}"),
          "track 4: the list does not end at 6233 with 234 dropped");
    CHECK(find_in_line(out, t4, "\"SKIP\":177,") && find_in_line(out, t4, "\"READERR\":1057,"),
          "track 4: paranoia_all_reads does not carry the counters set");

    CHECK(find_in_line(out, "{\"number\":5,",
                       ",\"paranoia_all_reads\":null,\"error_positions\":null,"
                       "\"error_positions_dropped\":null}"),
          "track 5: a track never read is not null in all three");
    free(out);
}

int main(void)
{
    test_track_fields();
    test_deemphasis_forced();
    test_isrc_disc_malformed();
    test_block_crcs();
    test_reads();
    test_drive_declared();
    test_cdtext_present();
    test_offset_search();
    test_error_positions();

    if (failures)
        fprintf(stderr, "%d check(s) failed\n", failures);
    else
        printf("all /10 record checks passed\n");

    return !!failures;
}
