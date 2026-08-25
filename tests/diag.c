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

/* Diagnostics-record retention tests.
 *
 * The property under test is one no rip can reach: what the record keeps when
 * more lines are printed than it can hold. A two-track image rip produces about
 * 124 messages and the cap is 20000, so the truncation path is unreachable from
 * tests/rip_images.py -- which is exactly how it shipped head-only, keeping the
 * first 10000 lines and discarding everything after.
 *
 * That is the failure mode Platterpus named in round 7 lap 11: **a tool's fatal
 * message is the last thing it prints**, so a head-only cap drops precisely the
 * line explaining the failure, while `messages_dropped` still makes the record
 * look accounted for. They found it by reading the design; nothing in this repo
 * could have, because nothing exercised it.
 *
 * So this links diagnostics.c and drives it past the cap directly. No disc, no
 * drive, no rip: the module reasons about a line buffer and a ring, and both
 * are testable on their own.
 */

#include "diagnostics.h"
#include "utils.h"

#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

/* What diagnostics.c expects from the rest of the program. Supplied here so the
 * module links without dragging in the disc context. */
char *crip_invocation = (char *)"cyanrip (diag unit test)";
volatile sig_atomic_t quit_now = 0;
volatile sig_atomic_t quit_signal = 0;
/* crip_signal_name() is NOT stubbed here. It is a static inline in utils.h, so
 * this test exercises the same function the program does -- a stub would let
 * an assertion here pass against a name cyanrip never prints. */
/* Normally generated into version.c at build time from git describe. Its value
 * is irrelevant here and pinning it keeps this test independent of the tree's
 * commit. */
const char *vcstag = "diag-unit-test";

struct cyanrip_ctx;
void cyanrip_log(struct cyanrip_ctx *ctx, int verbose, const char *format, ...);
void cyanrip_log(struct cyanrip_ctx *ctx, int verbose, const char *format, ...)
{
    (void)ctx; (void)verbose; (void)format;
}

static void record(const char *format, ...)
{
    va_list args;
    va_start(args, format);
    crip_diag_record(format, args);
    va_end(args);
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

/* The whole point. Print far more than the record can hold, and require that
 * both the first line and the LAST line survive. A head-only cap passes every
 * other assertion in this file and fails this one on the last line. */
static void test_keeps_the_last_line_said(void)
{
    const char *path = "diag_overflow.json";
    crip_diag_enable(path);
    crip_diag_set_exit(1);

    record("FIRST-LINE-MARKER\n");
    for (int i = 0; i < 25000; i++)
        record("filler line %i\n", i);
    /* Stands in for the message that explains why a run died. */
    record("FATAL-LAST-LINE-MARKER: the reason the rip failed\n");

    crip_diag_write();

    char *out = slurp(path);
    if (!out) {
        CHECK(0, "no diagnostics file written");
        return;
    }

    CHECK(strstr(out, "FIRST-LINE-MARKER") != NULL,
          "the first line said was dropped -- the head is not retained");
    CHECK(strstr(out, "FATAL-LAST-LINE-MARKER") != NULL,
          "the LAST line said was dropped -- a head-only cap discards exactly "
          "the message that explains a failure");

    /* Truncation must be declared, not inferred from a short array. */
    CHECK(strstr(out, "\"messages_complete_within_scope\": false") != NULL,
          "record does not declare itself incomplete after dropping lines");

    /* And the scope the boolean is relative to must be stated beside it. The
     * field this replaced was named `messages_are_complete`, which asserted
     * completeness over the logfile while computing something narrower -- 55
     * lines of it were missing on our own reference. A boolean about coverage
     * with no stated scope is the claim, not the qualifier. */
    CHECK(strstr(out, "\"messages_scope\":") != NULL,
          "no messages_scope field -- the completeness boolean has nothing to "
          "be relative to");
    CHECK(strstr(out, "\"messages_are_complete\"") == NULL,
          "the unscoped completeness field is back");
    CHECK(strstr(out, "\"messages_dropped\": 0,") == NULL,
          "messages_dropped is 0 after overflowing the record");

    /* Both halves are present as fields even so a consumer need not guess. */
    CHECK(strstr(out, "\"messages\":") != NULL, "no messages field");
    CHECK(strstr(out, "\"messages_tail\":") != NULL, "no messages_tail field");

    /* No synthetic entry may appear among things the program printed. */
    CHECK(strstr(out, "elided") == NULL && strstr(out, "truncated ---") == NULL,
          "a synthetic marker was written into the message record");

    free(out);
    remove(path);
}

/* THE `Cache model:` PARENTHETICAL, asserted directly because its call site
 * cannot be reached from a fixture.
 *
 * print_cache_model() needs a live cdio handle and a paranoia context, and all
 * three image drivers take the image arm before the drive arm is reached, so
 * no BIN/CUE, NRG or .toc rip in this suite can exercise the branch that was
 * wrong. Splitting the pure choice out is what makes it checkable at all.
 *
 * IT LIVES HERE because this test already builds against the module set that
 * carries utils.h and needs no disc context, which is exactly the property the
 * helper needs -- the same reason crip_signal_name() is in that header rather
 * than in cyanrip_main.c. utils.h is included directly above: it reached this
 * binary through diagnostics.c before, which links the symbol but does not
 * declare it in THIS translation unit, and an implicit declaration is how a
 * test comes to assert against a function nobody checked the signature of.
 *
 * The defect: the drive arm said "not probed" whatever -x did. Measured on the
 * 2026-08-25 acceptance run, whose §P log carried
 * `Cache model: 1200 sectors (drive cache size not probed)` in the header and
 * `Cache probe: at least 2048 sectors` below it. */
static void test_cache_model_note(void)
{
    const char *img_off = crip_cache_model_note(1, 0);
    const char *img_on  = crip_cache_model_note(1, 1);
    const char *drv_off = crip_cache_model_note(0, 0);
    const char *drv_on  = crip_cache_model_note(0, 1);

    /* An image has no drive cache whatever -x was asked for, so -x must not
     * change this arm -- on an image the probe refuses before doing anything
     * and a note claiming otherwise would be the same defect mirrored. */
    CHECK(strcmp(img_off, img_on) == 0,
          "-x changed the disc-image note, which has no drive cache to probe");
    CHECK(strstr(img_off, "disc image") != NULL,
          "the disc-image note stopped saying it is an image");

    /* The defect itself, both directions. */
    CHECK(strstr(drv_off, "not probed") != NULL,
          "a drive with no -x stopped saying the cache was not probed");
    CHECK(strstr(drv_on, "not probed") == NULL,
          "a drive WITH -x still claims the cache was not probed -- this is "
          "the false parenthetical this function exists to stop");
    CHECK(strstr(drv_on, "Cache probe:") != NULL,
          "the -x note does not point at the line carrying the measurement, "
          "so a reader has nothing to go to");

    /* And the four are not all one string: a note that never varied would
     * satisfy half the checks above by saying nothing. */
    CHECK(strcmp(drv_off, drv_on) != 0 && strcmp(drv_off, img_off) != 0,
          "the note does not discriminate its inputs");
}

int main(void)
{
    test_keeps_the_last_line_said();
    test_cache_model_note();

    if (failures)
        fprintf(stderr, "%d check(s) failed\n", failures);
    else
        printf("all diagnostics retention checks passed\n");

    return !!failures;
}
