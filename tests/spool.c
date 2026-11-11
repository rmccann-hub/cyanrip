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

/* The read kept at the -Z repeat limit, the rule alone.
 *
 * A run reaches the repeat limit only when reads disagree, which takes a drive
 * or tests/badsector.c's shim, and --prefer-accuraterip-match acts only on a
 * disc AccurateRip holds, which no fixture is and the suite cannot ask. So the
 * rule is a function over spools, and this drives it with spools built to sit
 * on each side of each clause. The case it exists for is the 2026-10-06 run's
 * track 5, docs/rig-2026-10-06-5704062/: E0036697 by reads 1 and 5 kept over
 * C96464AB by reads 2 and 3, which AccurateRip matches. */
#include "spool.h"

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

#define NB(a) ((int)(sizeof(a) / sizeof((a)[0])))

/* Without the flag the rule is unchanged: the most reads, the newest on a
 * tie. A, A, B, B, C keeps B, and a confidence it cannot see changes nothing. */
static void test_without_the_flag(void)
{
    crip_spool s[] = {
        { .crc = 0xA, .reads = 2, .last_read = 2, .ar_conf = 9 },
        { .crc = 0xB, .reads = 2, .last_read = 4 },
        { .crc = 0xC, .reads = 1, .last_read = 5, .ar_conf = 5 },
    };
    int k = crip_spool_kept_at_limit(s, NB(s), 0);
    CHECK(k == 1, "kept spool %d, want 1 (B: two reads, the newer of a tie)", k);
}

/* The 2026-10-06 case: the rule alone keeps E0036697, and with the flag the
 * read AccurateRip matches is kept, though fewer reads gave it. */
static void test_a_match_beats_more_reads(void)
{
    crip_spool s[] = {
        { .crc = 0xE0036697, .reads = 2, .last_read = 5, .ar_conf = -1 },
        { .crc = 0xC96464AB, .reads = 2, .last_read = 3, .ar_conf = 2 },
        { .crc = 0x12345678, .reads = 1, .last_read = 4, .ar_conf = -1 },
    };
    CHECK(crip_spool_kept_at_limit(s, NB(s), 0) == 0,
          "without the flag the newest of the tie, E0036697, is kept");
    int k = crip_spool_kept_at_limit(s, NB(s), 1);
    CHECK(k == 1, "kept spool %d, want 1, the read AccurateRip matches", k);

    crip_spool t[] = {
        { .crc = 0xA, .reads = 4, .last_read = 4, .ar_conf = -1 },
        { .crc = 0xB, .reads = 1, .last_read = 5, .ar_conf = 1 },
    };
    k = crip_spool_kept_at_limit(t, NB(t), 1);
    CHECK(k == 1, "kept spool %d, want 1: confidence 1 is a match and four "
          "reads that AccurateRip does not match are not", k);
}

/* Two matches: the higher confidence, whatever the reads; and at equal
 * confidence the rule breaks the tie. */
static void test_the_higher_confidence_then_the_rule(void)
{
    crip_spool s[] = {
        { .crc = 0xA, .reads = 3, .last_read = 3, .ar_conf = 4 },
        { .crc = 0xB, .reads = 1, .last_read = 4, .ar_conf = 9 },
        { .crc = 0xC, .reads = 1, .last_read = 5, .ar_conf = -1 },
    };
    int k = crip_spool_kept_at_limit(s, NB(s), 1);
    CHECK(k == 1, "kept spool %d, want 1, confidence 9 over 4", k);

    crip_spool t[] = {
        { .crc = 0xA, .reads = 1, .last_read = 1, .ar_conf = 6 },
        { .crc = 0xB, .reads = 2, .last_read = 3, .ar_conf = 6 },
        { .crc = 0xC, .reads = 2, .last_read = 5, .ar_conf = 6 },
    };
    k = crip_spool_kept_at_limit(t, NB(t), 1);
    CHECK(k == 2, "kept spool %d, want 2: at equal confidence two reads over "
          "one, then the newer", k);
}

/* No match, or only a confidence of 0, which is no match: the rule alone. The
 * second case fails a rule that took 0 for a match. */
static void test_no_match_falls_back_to_the_rule(void)
{
    crip_spool s[] = {
        { .crc = 0xA, .reads = 1, .last_read = 1, .ar_conf = 0 },
        { .crc = 0xB, .reads = 2, .last_read = 3, .ar_conf = -1 },
        { .crc = 0xC, .reads = 1, .last_read = 4, .ar_conf = 0 },
    };
    int k = crip_spool_kept_at_limit(s, NB(s), 1);
    CHECK(k == 1, "kept spool %d, want 1: no read matches, so the most reads", k);

    crip_spool t[] = {
        { .crc = 0xA, .reads = 2, .last_read = 2, .ar_conf = -1 },
        { .crc = 0xB, .reads = 1, .last_read = 3, .ar_conf = 0 },
    };
    k = crip_spool_kept_at_limit(t, NB(t), 1);
    CHECK(k == 0, "kept spool %d, want 0: a confidence of 0 is no match", k);
}

/* --reread-until-accuraterip: an agreement is overruled only when AccurateRip
 * holds the track at CONF or more and matches none of the agreed read. Each
 * case moves one argument across its boundary, so a rule that dropped any
 * clause fails one. */
static void test_an_agreement_is_overruled(void)
{
    CHECK(crip_agreement_overruled(2, 5, -1),
          "AccurateRip holds the track at 5 and matches no agreed read: overruled");
    CHECK(crip_agreement_overruled(2, 2, -1),
          "a track held at exactly CONF is held at CONF or more: overruled");
    CHECK(crip_agreement_overruled(2, 5, 0),
          "a confidence of 0 is no match: overruled");
    CHECK(!crip_agreement_overruled(0, 5, -1), "without the option nothing is overruled");
    CHECK(!crip_agreement_overruled(2, 1, -1),
          "a track held only at 1 is not held at 2: the agreement stands");
    CHECK(!crip_agreement_overruled(2, 0, 0),
          "a track AccurateRip holds no entry for: the agreement stands");
    CHECK(!crip_agreement_overruled(2, 5, 1),
          "AccurateRip matches the agreed read, at 1 though CONF is 2: it stands");
}

/* After an overrule: the read AccurateRip matches at CONF or more ends the
 * track, an earlier read included; one below CONF does not. The first case is
 * 2026-11-10's track 5, E0036697 agreed on three times. */
static void test_a_verified_read_ends_the_track(void)
{
    crip_spool s[] = {
        { .crc = 0xE0036697, .reads = 3, .last_read = 3, .ar_conf = -1 },
        { .crc = 0xC96464AB, .reads = 1, .last_read = 4, .ar_conf = 5 },
    };
    CHECK(crip_spool_ar_verified(s, 1, 2) == -1, "E0036697 alone: reading goes on");
    int k = crip_spool_ar_verified(s, NB(s), 2);
    CHECK(k == 1, "verified spool %d, want 1, C96464AB at 5", k);

    crip_spool t[] = {
        { .crc = 0xA, .reads = 1, .last_read = 1, .ar_conf = 3 },
        { .crc = 0xB, .reads = 2, .last_read = 3, .ar_conf = -1 },
    };
    k = crip_spool_ar_verified(t, NB(t), 3);
    CHECK(k == 0, "verified spool %d, want 0: read 1, before the agreement, "
          "matches at CONF", k);
    CHECK(crip_spool_ar_verified(t, NB(t), 4) == -1,
          "a match at 3 when CONF is 4: reading goes on");
    CHECK(crip_spool_ar_verified(t, 0, 3) == -1, "no spools: reading goes on");
    CHECK(crip_spool_ar_verified(t, NB(t), 0) == -1, "without the option: -1");
}

/* One spool, whatever it says. */
static void test_one_spool(void)
{
    crip_spool s[] = { { .crc = 0xA, .reads = 3, .last_read = 3, .ar_conf = -1 } };
    CHECK(crip_spool_kept_at_limit(s, 1, 1) == 0, "the only spool is kept");
}

int main(void)
{
    test_without_the_flag();
    test_a_match_beats_more_reads();
    test_the_higher_confidence_then_the_rule();
    test_no_match_falls_back_to_the_rule();
    test_one_spool();
    test_an_agreement_is_overruled();
    test_a_verified_read_ends_the_track();

    if (failures) {
        printf("%i check(s) failed\n", failures);
        return 1;
    }
    printf("spool: all checks passed\n");
    return 0;
}
