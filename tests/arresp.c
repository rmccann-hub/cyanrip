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

/* The AccurateRip HTTP response path, which NO disc-image scenario can reach.
 *
 * tests/rip_images.py:88 passes -N -A -U on all 40 scenarios, so
 * crip_fill_accurip() returns at its first branch and none of this has ever
 * executed under test. Coverage says the same from the other side: accurip.c
 * is the least-covered real file in the tree.
 *
 * That is how three defects lived here -- an unchecked av_realloc() feeding a
 * memcpy(), a strcmp() on a content_type that is NULL when a 200 carries no
 * Content-Type header, and a strstr() over a buffer built by raw memcpy() and
 * never NUL-terminated.
 *
 * The functions under test are static, so this includes the translation unit
 * rather than linking it -- the same move tests/subq.c makes for pregap.c.
 *
 * ONE THING THIS FILE CANNOT DO ON ITS OWN. The over-read cases below allocate
 * their buffers to the EXACT length so that reading past the end is a real
 * heap overflow rather than a read into slack. Detecting it needs the
 * instrumented build: `meson test -C build-asan 'AccurateRip response'`.
 * Under the default build these cases assert the RETURN VALUE only, which is
 * necessary and not sufficient -- said here rather than left implied.
 */

#include "accurip.c"

#include <stdio.h>
#include <string.h>

static int failures;

static void check(int cond, const char *what)
{
    if (!cond) {
        fprintf(stderr, "FAIL: %s\n", what);
        failures++;
    }
}

/* accurip.c calls this; the real one needs a whole cyanrip_ctx. */
void cyanrip_log(cyanrip_ctx *ctx, int verbose, const char *format, ...)
{
    (void)ctx; (void)verbose; (void)format;
}

/* A buffer of exactly `n` bytes, so an over-read is a real overflow. */
static uint8_t *exact(const void *src, size_t n)
{
    uint8_t *p = av_malloc(n ? n : 1);
    if (n)
        memcpy(p, src, n);
    return p;
}

static void test_html_marker(void)
{
    /* The empty-body case: a 200 with Content-Length: 0 never fires the write
     * callback, so data is NULL. strstr(NULL, ...) was the old behaviour. */
    check(crip_find_html_marker(NULL, 0) == NULL, "NULL body must not match");
    check(crip_find_html_marker(NULL, 4096) == NULL,
          "NULL body with a nonzero size must not match");

    uint8_t *b;

    b = exact("html", 4);
    check(crip_find_html_marker(b, 4) == b, "match at offset 0");
    av_free(b);

    /* Offset 63 is the last legal start; 64 is the first illegal one. THIS
     * PAIR IS THE DISCRIMINATOR -- a scan with the wrong bound passes one and
     * fails the other, and a scan with no bound at all passes both. */
    {
        uint8_t buf[128];
        memset(buf, 'x', sizeof(buf));
        memcpy(buf + 63, "html", 4);
        b = exact(buf, sizeof(buf));
        check(crip_find_html_marker(b, sizeof(buf)) == b + 63,
              "match starting at offset 63 is inside the window");
        av_free(b);

        memset(buf, 'x', sizeof(buf));
        memcpy(buf + 64, "html", 4);
        b = exact(buf, sizeof(buf));
        check(crip_find_html_marker(b, sizeof(buf)) == NULL,
              "match starting at offset 64 is outside the window");
        av_free(b);
    }

    /* No NUL anywhere: what the old strstr() ran off the end of. */
    {
        uint8_t buf[80];
        memset(buf, 0xAA, sizeof(buf));
        memcpy(buf + 8, "<html>", 6);
        b = exact(buf, sizeof(buf));
        check(crip_find_html_marker(b, sizeof(buf)) == b + 9,
              "match inside a body with no terminator");
        av_free(b);
    }

    /* Truncated needle at the very end: must not read the fifth byte. */
    b = exact("xxxhtm", 6);
    check(crip_find_html_marker(b, 6) == NULL,
          "a 3-byte tail of the needle must not match");
    av_free(b);

    /* Shorter than the needle. */
    b = exact("ht", 2);
    check(crip_find_html_marker(b, 2) == NULL, "body shorter than the needle");
    av_free(b);
}

static void test_receive_data(void)
{
    RecvCtx rctx = { 0 };

    check(receive_data("abcd", 1, 4, &rctx) == 4, "first write is accepted");
    check(rctx.size == 4 && rctx.data && !memcmp(rctx.data, "abcd", 4),
          "first write lands");

    check(receive_data("efgh", 1, 4, &rctx) == 8 - 4, "second write accepted");
    check(rctx.size == 8 && !memcmp(rctx.data, "abcdefgh", 8),
          "second write appends");

    /* THE DEFECT. av_max_alloc() makes the next av_realloc() fail for real, so
     * this does not simulate the failure -- it causes it. Before the fix the
     * NULL result was stored and memcpy()d through; the process died with no
     * diagnosable line, mid-rip, after the disc had been read. */
    uint8_t *before = rctx.data;
    size_t size_before = rctx.size;
    /* The request is rctx.size + 4 == 12 bytes, so the cap must be below that.
     * Capping at 16 let the allocation SUCCEED and the two checks below failed
     * -- the test caught its own arithmetic before it could pass vacuously. */
    av_max_alloc(8);
    check(receive_data("ijkl", 1, 4, &rctx) == 0,
          "a failing realloc must return short, so curl reports it");
    av_max_alloc(INT_MAX);

    check(rctx.data == before,
          "a failing realloc must NOT clobber the buffer pointer");
    check(rctx.size == size_before,
          "a failing realloc must NOT advance the size");
    check(rctx.data && !memcmp(rctx.data, "abcdefgh", 8),
          "the bytes already received survive a failing realloc");

    av_freep(&rctx.data);
}

/* A REAL RESPONSE, PARSED WITH NO NETWORK, CHECKED AGAINST A REAL DRIVE'S LOG.
 *
 * argv[1] is the reference disc's dBAR file, fetched once from accuraterip.com
 * on 2026-09-27 and committed (tests/fixtures/, 1807 bytes, 13 entries). The
 * request was derived from the rig log's TOC, and its CDDB ID reproduces the
 * one that log printed, E20DFE0E. argv[2] is that rig log: a rip of the same
 * disc on a real drive on 2026-09-10, whose `Accurip v1:` lines say which
 * whole-track checksums matched the database, at what confidence. The parse
 * is checked against those, which it did not produce, rather than against
 * numbers read back out of the fixture. */
static void test_recorded_response(const char *bin, const char *rig_log)
{
    enum { N = 14 };
    FILE *f = fopen(bin, "rb");
    uint8_t data[4096];
    size_t size = f ? fread(data, 1, sizeof(data), f) : 0;
    if (f)
        fclose(f);
    check(size == 1807, "the recorded response is the 1807 bytes committed");
    if (size != 1807)
        return;

    /* The context is large (its track array is fixed-size), so it is on the
     * heap rather than the stack. */
    cyanrip_ctx *ctx = av_mallocz(sizeof(*ctx));
    cyanrip_track *tracks = ctx->tracks;
    for (int i = 0; i < N; i++)
        tracks[i].number = i + 1;
    ctx->nb_tracks = N;

    crip_parse_accurip(ctx, data, size, N, 0x001d420f, 0x013bb370, 0xe20dfe0e);
    check(ctx->ar_db_status == CYANRIP_ACCUDB_FOUND, "the disc is found");
    for (int i = 0; i < N; i++) {
        check(tracks[i].ar_db_nb_entries == 13, "every track holds all 13 entries");
        /* Ascending: cmp_conf() returns a - b. This check first said
         * "highest first", which was an assumption and not the code. */
        for (int e = 1; e < tracks[i].ar_db_nb_entries; e++)
            check(tracks[i].ar_db_entries[e - 1].confidence <=
                  tracks[i].ar_db_entries[e].confidence,
                  "entries are sorted by confidence, lowest first");
    }

    /* The independent half. Each `Accurip v1:  X (accurately ripped,
     * confidence C)` line of the rig log, in track order, must be found by
     * crip_find_ar() over the parsed entries, at confidence C. */
    FILE *lf = fopen(rig_log, "r");
    check(lf != NULL, "the rig log opens");
    if (!lf) {
        av_free(ctx);
        return;
    }
    char line[512];
    int track = 0, matched = 0, not_found = 0;
    while (fgets(line, sizeof(line), lf) && track < N) {
        unsigned crc;
        int conf;
        const char *p = strstr(line, "Accurip v1:");
        if (!p)
            continue;
        if (sscanf(p, "Accurip v1: %8x (accurately ripped, confidence %d)",
                   &crc, &conf) == 2) {
            check(crip_find_ar(&tracks[track], crc, 0) == conf,
                  "a checksum the real rip matched is found at its confidence");
            matched++;
        } else {
            not_found++;
        }
        track++;
    }
    fclose(lf);
    check(track == N, "the rig log has one Accurip v1 line per track");
    check(matched == 12 && not_found == 2,
          "the rig log matched 12 tracks and not 2, as it says");

    /* And the one-frame checksum a wrong read of track 1 matched in round 26,
     * 57722DDE at confidence 200, is the top entry's 450. */
    check(crip_find_ar(&tracks[0], 0x57722DDE, 1) == 200,
          "track 1's frame-450 checksum is found at confidence 200");

    for (int i = 0; i < N; i++)
        av_freep(&tracks[i].ar_db_entries);
    av_free(ctx);
}

/* The disc-level status says what the response held. It was set to FOUND
 * before the loop that would downgrade it, so the MISMATCH arm could never
 * run: a response whose entries all carry another disc's ids, or none at
 * all, read `AccurateRip:    found`, and the report then printed a tally of
 * 0 of N over a comparison that never happened. Built from the recorded
 * response, so every entry is a real one and only the ids asked for, or the
 * bytes around it, differ. */
static int parse_status(const uint8_t *data, size_t size, uint32_t id1,
                        int *entries_on_track_1)
{
    enum { N = 14 };
    cyanrip_ctx *ctx = av_mallocz(sizeof(*ctx));
    for (int i = 0; i < N; i++)
        ctx->tracks[i].number = i + 1;
    ctx->nb_tracks = N;
    crip_parse_accurip(ctx, data, size, N, id1, 0x013bb370, 0xe20dfe0e);
    int status = ctx->ar_db_status;
    *entries_on_track_1 = ctx->tracks[0].ar_db_nb_entries;
    for (int i = 0; i < N; i++)
        av_freep(&ctx->tracks[i].ar_db_entries);
    av_free(ctx);
    return status;
}

static void test_disc_status_says_what_the_response_held(const char *bin)
{
    enum { ENTRY = 1 + 12 + 14 * 9 };
    FILE *f = fopen(bin, "rb");
    uint8_t data[4096], mixed[4096];
    size_t size = f ? fread(data, 1, sizeof(data), f) : 0;
    if (f)
        fclose(f);
    if (size != 1807 || size % ENTRY)
        return;   /* test_recorded_response() has already failed on it */
    int n;

    check(parse_status(data, size, 0x001d420f, &n) == CYANRIP_ACCUDB_FOUND &&
          n == 13, "status/control: the right ids find the disc");

    check(parse_status(data, size, 0x001d4210, &n) == CYANRIP_ACCUDB_MISMATCH &&
          n == 0, "status/mismatch: entries for other ids read as mismatch");

    check(parse_status(data, 0, 0x001d420f, &n) == CYANRIP_ACCUDB_NOT_FOUND &&
          n == 0, "status/empty: an empty response reads as not found");

    /* One entry with a foreign id, before the real ones and after them. The
     * foreign one is skipped either way, and a match anywhere is FOUND. */
    memcpy(mixed, data, ENTRY);
    mixed[1] ^= 0x01;                      /* id_type_1, little-endian */
    memcpy(mixed + ENTRY, data, size);
    check(parse_status(mixed, size + ENTRY, 0x001d420f, &n) ==
          CYANRIP_ACCUDB_FOUND && n == 13,
          "status/foreign-first: a match after a foreign entry is found");

    memcpy(mixed, data, size);
    memcpy(mixed + size, data, ENTRY);
    mixed[size + 1] ^= 0x01;
    check(parse_status(mixed, size + ENTRY, 0x001d420f, &n) ==
          CYANRIP_ACCUDB_FOUND && n == 13,
          "status/foreign-last: a foreign entry after a match leaves it found");
}

/* A response whose size is not a whole number of entries is an ERROR, and the
 * parser says so by its return value rather than by printing: the caller
 * prints `AccuRIP DB data error, got unexpected number of bytes!` and leaves by
 * `goto end`, which is what keeps that line in the provider contract's P5a
 * (src/accurip.c, above crip_parse_accurip()). No test reached this branch
 * until round 28 lap 5 found the row missing from the contract. */
static void test_a_response_of_the_wrong_size_is_an_error(const char *bin)
{
    enum { N = 14 };
    FILE *f = fopen(bin, "rb");
    uint8_t data[4096];
    size_t size = f ? fread(data, 1, sizeof(data), f) : 0;
    if (f)
        fclose(f);
    if (size != 1807)
        return;   /* test_recorded_response() has already failed on it */

    cyanrip_ctx *ctx = av_mallocz(sizeof(*ctx));
    for (int i = 0; i < N; i++)
        ctx->tracks[i].number = i + 1;
    ctx->nb_tracks = N;
    int ret = crip_parse_accurip(ctx, data, size - 1, N, 0x001d420f,
                                 0x013bb370, 0xe20dfe0e);
    check(ret < 0, "size: a response one byte short returns an error");
    check(ctx->ar_db_status == CYANRIP_ACCUDB_ERROR,
          "size: a response one byte short reads as an error");
    check(ctx->tracks[0].ar_db_nb_entries == 0,
          "size: nothing is parsed from a response of the wrong size");

    ret = crip_parse_accurip(ctx, data, size, N, 0x001d420f,
                             0x013bb370, 0xe20dfe0e);
    check(ret == 0 && ctx->ar_db_status == CYANRIP_ACCUDB_FOUND,
          "size/control: the whole response parses and returns 0");
    for (int i = 0; i < N; i++)
        av_freep(&ctx->tracks[i].ar_db_entries);
    av_free(ctx);
}

int main(int argc, char **argv)
{
    test_html_marker();
    test_receive_data();
    if (argc < 3) {
        fprintf(stderr, "FAIL: usage: arresp_test RESPONSE.bin RIG.log\n");
        return 1;
    }
    test_recorded_response(argv[1], argv[2]);
    test_disc_status_says_what_the_response_held(argv[1]);
    test_a_response_of_the_wrong_size_is_an_error(argv[1]);

    if (failures) {
        fprintf(stderr, "%d check(s) failed\n", failures);
        return 1;
    }
    printf("AccurateRip response path: all checks passed\n");
    return 0;
}
