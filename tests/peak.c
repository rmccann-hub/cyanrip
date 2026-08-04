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

/* Sample-peak cross-check decision (H6, Platterpus round 7).
 *
 * The log line this drives is printed only when ebur128's sample peak and a
 * direct max|sample| scan of the same frames disagree. **No disc image can make
 * that happen** -- two correct measurements of identical input agree, which is
 * the whole point of the check -- so the firing path is unreachable from
 * tests/rip_images.py no matter how many fixtures it rips.
 *
 * That is exactly the shape of feature that ships having never executed. The
 * decision is therefore a pure function in utils.h and this file exercises it
 * directly: both branches, the threshold boundary, and the not-measured case.
 *
 * What this does NOT prove: that the two measurements are wired to the same
 * frames, or that a real disagreement would ever be produced by a real drive.
 * The first is a code-reading claim; the second is unfalsifiable until one
 * happens. Neither is asserted here.
 */

#include "utils.h"

#include <stdio.h>

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

/* Agreement is the expected case and must stay silent, or every rip grows a
 * line that says nothing. */
static void test_agreement_is_silent(void)
{
    double d = -1.0;
    CHECK(!crip_peaks_disagree(-3.5, -3.5, &d), "identical values disagreed");
    CHECK(d == 0.0, "delta should be 0 for identical values, got %f", d);

    CHECK(!crip_peaks_disagree(-0.0001, 0.0, NULL),
          "a rounding-scale difference must not be reported");
}

/* The branch the feature exists for. */
static void test_disagreement_fires(void)
{
    double d = 0.0;
    CHECK(crip_peaks_disagree(-3.0, -6.0, &d), "3 dB apart did not fire");
    CHECK(d > 2.99 && d < 3.01, "delta should be ~3.0, got %f", d);

    /* Symmetric: which one is larger must not change the verdict. */
    CHECK(crip_peaks_disagree(-6.0, -3.0, NULL), "not symmetric");
}

/* The threshold is a documented constant; pin both sides of it so a change to
 * it is a deliberate edit rather than a drift. */
static void test_threshold_boundary(void)
{
    CHECK(CRIP_PEAK_DISAGREE_DB == 0.1,
          "threshold changed to %f -- that is a contract change",
          (double)CRIP_PEAK_DISAGREE_DB);

    CHECK(crip_peaks_disagree(0.0, -0.1, NULL),
          "exactly at the threshold must fire (>=, not >)");
    CHECK(!crip_peaks_disagree(0.0, -0.09, NULL),
          "just under the threshold must stay silent");
}

/* "Not measured" and "measured and equal" are different claims. A never-set
 * peak is -INFINITY, and comparing against a sentinel would report a
 * disagreement of infinity on every track that was not measured. */
static void test_unmeasured_is_never_a_disagreement(void)
{
    double d = 1.0;
    CHECK(!crip_peaks_disagree(-INFINITY, -3.0, &d),
          "an unmeasured direct scan must not read as a disagreement");
    CHECK(d == 0.0, "delta should be 0 when nothing was measured, got %f", d);

    CHECK(!crip_peaks_disagree(-3.0, -INFINITY, NULL), "symmetric case");
    CHECK(!crip_peaks_disagree(-INFINITY, -INFINITY, NULL), "both unmeasured");
    CHECK(!crip_peaks_disagree(NAN, -3.0, NULL), "NaN must not fire");
    CHECK(!crip_peaks_disagree(-3.0, NAN, NULL), "NaN must not fire");
}

/* A NULL delta must be accepted -- the log path passes one, a caller that only
 * wants the verdict should not have to invent storage. */
static void test_null_delta_is_allowed(void)
{
    CHECK(crip_peaks_disagree(-1.0, -9.0, NULL), "NULL delta broke the verdict");
}

int main(void)
{
    test_agreement_is_silent();
    test_disagreement_fires();
    test_threshold_boundary();
    test_unmeasured_is_never_a_disagreement();
    test_null_delta_is_allowed();

    if (failures)
        fprintf(stderr, "%d check(s) failed\n", failures);
    else
        printf("all peak cross-check checks passed\n");

    return !!failures;
}
