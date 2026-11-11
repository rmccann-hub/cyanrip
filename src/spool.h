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

#include <stdint.h>
#include <stdio.h>
#include <time.h>

/* One -Z spool: the bytes of the reads that gave one checksum. What the spool
 * is for, and why, is above crip_spool_write() in cyanrip_main.c.
 *
 * A header of its own so that the rule choosing the read kept at the repeat
 * limit can be tested: the reads that reach that limit come from a drive, or
 * from tests/badsector.c's shim, and AccurateRip is out of the suite's reach,
 * so tests/spool.c drives the rule directly. */
typedef struct crip_spool {
    uint32_t crc;   /* raw, before the final XOR, as last_checksums holds it */
    int reads;      /* how many reads gave it */
    int last_read;  /* the newest of them, counting from 1 */
    time_t began;   /* when the newest of them began */
    int64_t read_us; /* how long the newest of them took to read, in
                      * microseconds: Extraction speed:'s time under -Z */
    int ar_conf;    /* under --prefer-accuraterip-match or
                     * --reread-until-accuraterip, the confidence of the
                     * AccurateRip entry its v1 or v2 checksum matches, the
                     * higher; below 1 when none does, or without either */
    FILE *f;        /* their bytes, as checksummed */
    uint32_t ar_v1, ar_v2;   /* this read's AccurateRip checksums */
    uint32_t *block_crcs;    /* this read's per-second CRCs, or NULL */
    int nb_block_crcs;
} crip_spool;

/* At the repeat limit: the most reads, and on a tie the newest.
 *
 * With prefer_ar, --prefer-accuraterip-match (round 36: our lap 4 S11, which
 * Platterpus's lap 3 S4 accepted as given), a read AccurateRip matches at
 * confidence 1 or more is kept over one it does not, the higher confidence
 * first, and the rule above breaks a tie. On 2026-10-06 the rule alone kept
 * track 5's E0036697, reads 1 and 5, over C96464AB, reads 2 and 3, which
 * AccurateRip matches. A confidence of 0 is no match: only a malformed entry
 * carries one, and crip_find_ar() also answers 0 for a track not looked up. */
static inline int crip_spool_kept_at_limit(const crip_spool *spools, int nb_spools,
                                           int prefer_ar)
{
    int k = 0;
    for (int i = 1; i < nb_spools; i++) {
        if (prefer_ar) {
            const int ci = spools[i].ar_conf >= 1 ? spools[i].ar_conf : 0;
            const int ck = spools[k].ar_conf >= 1 ? spools[k].ar_conf : 0;
            if (ci != ck) {
                if (ci > ck)
                    k = i;
                continue;
            }
        }
        if (spools[i].reads > spools[k].reads ||
            (spools[i].reads == spools[k].reads &&
             spools[i].last_read > spools[k].last_read))
            k = i;
    }
    return k;
}

/* --reread-until-accuraterip CONF (round 38: our lap 16 S13, which
 * Platterpus's lap 17 S8 accepted as given): an agreement of -Z's reads does
 * not end the track when AccurateRip holds the track at confidence CONF or
 * more and matches neither whole-track checksum, v1 or v2, of the read agreed
 * on. ar_max_conf is the track's highest AccurateRip confidence, 0 when it
 * holds no entry; read_conf is the agreed read's ar_conf, below 1 for no
 * match. A match at frame 450 alone is no match: on 2026-11-10, -Z agreed on
 * track 5's E0036697 after 3 reads, which AccurateRip matches at frame 450
 * only (docs/rig-2026-11-10-5cc1c6b/). */
static inline int crip_agreement_overruled(int until_conf, int ar_max_conf,
                                           int read_conf)
{
    return until_conf >= 1 && ar_max_conf >= until_conf && read_conf < 1;
}

/* Once an agreement is overruled, the spool that ends the track: the one
 * --prefer-accuraterip-match's keep rule picks, when AccurateRip matches it at
 * until_conf or more; otherwise -1, and reading goes on. A read made before
 * the agreement counts, since it is a read AccurateRip matches. */
static inline int crip_spool_ar_verified(const crip_spool *spools, int nb_spools,
                                         int until_conf)
{
    if (nb_spools < 1 || until_conf < 1)
        return -1;
    const int k = crip_spool_kept_at_limit(spools, nb_spools, 1);
    return spools[k].ar_conf >= until_conf ? k : -1;
}
