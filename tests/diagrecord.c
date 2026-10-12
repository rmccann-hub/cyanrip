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

    /* 4: a data track: nothing is read, and the reason says why. */
    ctx->tracks[3].track_is_data = 1;

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

    CHECK(strstr(out, "\"schema\": \"cyanrip-diagnostics/8\""),
          "the schema is not cyanrip-diagnostics/8");

    expect_line(out, "{\"number\":1,\"cd_track\":1,\"repeats\":0,\"audio_ripped\":true,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,"
                     "\"preemphasis\":\"none\",\"deemphasis_applied\":false,"
                     "\"isrc_written\":\"AA\\\"BB\\\\CC\",\"isrc_disc\":\"ZZZZZ9999999\","
                     "\"isrc_disc_reason\":null,\"encode_failures\":1}", "track 1");
    expect_line(out, "{\"number\":2,\"cd_track\":2,\"repeats\":0,\"audio_ripped\":false,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,"
                     "\"preemphasis\":\"subcode\",\"deemphasis_applied\":true,"
                     "\"isrc_written\":null,\"isrc_disc\":null,"
                     "\"isrc_disc_reason\":\"libcdio returned none\",\"encode_failures\":0}",
                "track 2");
    expect_line(out, "{\"number\":3,\"cd_track\":3,\"repeats\":0,\"audio_ripped\":true,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,"
                     "\"preemphasis\":\"toc\",\"deemphasis_applied\":true,"
                     "\"isrc_written\":null,\"isrc_disc\":null,"
                     "\"isrc_disc_reason\":\"libcdio returned an empty ISRC\","
                     "\"encode_failures\":0}", "track 3");
    expect_line(out, "{\"number\":4,\"cd_track\":4,\"repeats\":0,\"audio_ripped\":false,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,"
                     "\"preemphasis\":null,\"deemphasis_applied\":null,"
                     "\"isrc_written\":null,\"isrc_disc\":null,"
                     "\"isrc_disc_reason\":\"data track\",\"encode_failures\":0}", "track 4");
    expect_line(out, "{\"number\":5,\"cd_track\":5,\"repeats\":0,\"audio_ripped\":false,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,"
                     "\"preemphasis\":null,\"deemphasis_applied\":null,"
                     "\"isrc_written\":null,\"isrc_disc\":null,"
                     "\"isrc_disc_reason\":\"not read\",\"encode_failures\":0}", "track 5");
    expect_line(out, "{\"number\":6,\"cd_track\":6,\"repeats\":0,\"audio_ripped\":true,"
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,"
                     "\"preemphasis\":\"none\",\"deemphasis_applied\":false,"
                     "\"isrc_written\":null,\"isrc_disc\":null,"
                     "\"isrc_disc_reason\":\"the driver does not report reading ISRC\","
                     "\"encode_failures\":0}", "track 6");

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
                     "\"crcs_computed\":false,\"eac_crc\":null,\"rip_time_us\":0,"
                     "\"preemphasis\":\"none\",\"deemphasis_applied\":true,"
                     "\"isrc_written\":null,\"isrc_disc\":null,"
                     "\"isrc_disc_reason\":null,\"encode_failures\":0}", "forced");
    free(out);
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

int main(void)
{
    test_track_fields();
    test_deemphasis_forced();
    test_cdtext_present();
    test_offset_search();

    if (failures)
        fprintf(stderr, "%d check(s) failed\n", failures);
    else
        printf("all /8 record checks passed\n");

    return !!failures;
}
