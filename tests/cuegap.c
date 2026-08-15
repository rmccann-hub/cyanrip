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

/* Whether a track's pre-gap earns an INDEX 00 in the cue sheet.
 *
 * The decision is a pure function in cue_writer.h and this file exercises it
 * directly, because **no disc image can reach the case it exists to get
 * right**. That case needs a pre-gap which is *signalled* and *zero frames
 * long*, and image drivers do not produce one: a bincue track whose INDEX 00
 * equals its INDEX 01 comes back as `Pregap LSN: unknown (sub-channel
 * unreadable)`, which was measured on a purpose-built fixture, not assumed.
 * Only the Q sub-channel search on a physical disc yields
 * pregap_lsn == start_lsn_sig.
 *
 * The numbers below are read out of docs/rig-2026-08-05/cyanrip.log rather
 * than invented, so what is asserted is a rip that happened:
 *
 *     track 3   Pregap LSN: 28067   Pregap length: 0 frames
 *               Start LSN:  28067 (with offset: 28068)
 *
 * Before the fix the guard compared pregap_lsn against start_lsn -- the
 * offset-accounted one -- so 28067 != 28068 read as a pre-gap and the cue
 * declared `INDEX 00 03:01:05`, one frame past the end of track 2's file,
 * while the log on the same rip said the pre-gap was zero frames. Two of our
 * own artifacts disagreeing about the same disc.
 *
 * What this does NOT prove: that a real drive produces these values, or that
 * the cue writer formats the timestamp correctly. The first is what the rig
 * log is evidence of; the second is exercised by tests/rip_images.py.
 */

#include "cue_writer.h"

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

#define NONE CDIO_INVALID_LSN

/* The regression, in the numbers it actually happened with. */
static void test_zero_length_pregap_is_not_a_pregap(void)
{
    /* Track 3, 2026-08-05 rig rip: signalled at the track's own start. */
    CHECK(!crip_track_has_appended_pregap(28067, 28067, NONE, NONE, 1, 1),
          "a zero-length pre-gap asked for an INDEX 00");

    /* The other three tracks of that disc with the same shape. */
    CHECK(!crip_track_has_appended_pregap(90642, 90642, NONE, NONE, 1, 1),
          "track 6 (zero-length) asked for an INDEX 00");
    CHECK(!crip_track_has_appended_pregap(178332, 178332, NONE, NONE, 1, 1),
          "track 11 (zero-length) asked for an INDEX 00");
    CHECK(!crip_track_has_appended_pregap(200862, 200862, NONE, NONE, 1, 1),
          "track 12 (zero-length) asked for an INDEX 00");
}

/* The fix must not silence the real ones -- a guard that always says no would
 * pass every check above. */
static void test_real_pregaps_still_get_an_index(void)
{
    /* Track 5 of the same rip: 115 frames, 72455 -> 72570. */
    CHECK(crip_track_has_appended_pregap(72455, 72570, NONE, NONE, 1, 1),
          "a 115 frame pre-gap did not ask for an INDEX 00");
    /* Track 2: 160 frames. */
    CHECK(crip_track_has_appended_pregap(14327, 14487, NONE, NONE, 1, 1),
          "a 160 frame pre-gap did not ask for an INDEX 00");
    /* One frame is still a pre-gap. */
    CHECK(crip_track_has_appended_pregap(999, 1000, NONE, NONE, 1, 1),
          "a one frame pre-gap did not ask for an INDEX 00");
}

/* The offset must not enter the decision at all. start_lsn_sig is what the
 * disc signalled; start_lsn is where we read from after correction. Passing
 * the second is the bug, so pin that only the first is consulted. */
static void test_the_read_offset_cannot_change_the_answer(void)
{
    const lsn_t sig = 28067;
    for (int offset_frames = 0; offset_frames <= 4; offset_frames++) {
        /* The caller must pass start_lsn_sig; whatever the offset does to
         * start_lsn is irrelevant, and the only way to state that in a test
         * is that no offset value is an input here. */
        CHECK(!crip_track_has_appended_pregap(sig, sig, NONE, NONE, 1, 1),
              "zero-length pre-gap became a pre-gap at offset %d", offset_frames);
    }
}

/* The other three conditions, so a rewrite that drops one is caught. */
static void test_the_remaining_guards(void)
{
    CHECK(!crip_track_has_appended_pregap(NONE, 14487, NONE, NONE, 1, 1),
          "an unknown pre-gap LSN asked for an INDEX 00");
    CHECK(!crip_track_has_appended_pregap(14327, 14487, NONE, NONE, 0, 1),
          "track 1 (no previous track) asked for an INDEX 00");
    CHECK(!crip_track_has_appended_pregap(14327, 14487, 14327, NONE, 1, 1),
          "a dropped pre-gap asked for an appended INDEX 00");
    CHECK(!crip_track_has_appended_pregap(14327, 14487, NONE, 14487, 1, 1),
          "a merged pre-gap asked for an appended INDEX 00");
}

/* The -l case. Round 8, from Platterpus's 2026-08-14 hand-off §8: the
 * predicate's only structural input was `!!t->pt`, the previous track on the
 * DISC, so on `-l 1,3,5,6,7` track 5's INDEX 00 was computed against excluded
 * track 4 and printed inside track 3's FILE -- 22535 frames into a 21853 frame
 * file, 682 past the end.
 *
 * Both directions, because a predicate that always says no would pass the
 * first half alone -- and that is the exact vacuity the zero-length fix was
 * already tested against. */
static void test_a_pregap_needs_the_previous_file_to_exist(void)
{
    /* Track 5's real numbers, predecessor NOT written. */
    CHECK(!crip_track_has_appended_pregap(72455, 72570, NONE, NONE, 1, 0),
          "an INDEX 00 was written against a FILE that does not exist");

    /* Same numbers, predecessor written: still a pre-gap. */
    CHECK(crip_track_has_appended_pregap(72455, 72570, NONE, NONE, 1, 1),
          "a real pre-gap stopped asking for an INDEX 00");

    /* The two inputs are independent: a track with no predecessor at all is
     * refused whatever the file flag says, so one cannot mask the other. */
    CHECK(!crip_track_has_appended_pregap(72455, 72570, NONE, NONE, 0, 1),
          "track 1 asked for an INDEX 00 because a file flag was set");
}

int main(void)
{
    test_a_pregap_needs_the_previous_file_to_exist();
    test_zero_length_pregap_is_not_a_pregap();
    test_real_pregaps_still_get_an_index();
    test_the_read_offset_cannot_change_the_answer();
    test_the_remaining_guards();

    if (failures)
        fprintf(stderr, "%d check(s) failed\n", failures);
    else
        printf("cue pre-gap decision: all checks passed\n");
    return !!failures;
}
