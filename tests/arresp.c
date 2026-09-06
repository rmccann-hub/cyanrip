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

int main(void)
{
    test_html_marker();
    test_receive_data();

    if (failures) {
        fprintf(stderr, "%d check(s) failed\n", failures);
        return 1;
    }
    printf("AccurateRip response path: all checks passed\n");
    return 0;
}
