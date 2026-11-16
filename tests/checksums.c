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

/* AccurateRip's one-sector checksum, the `Accurip 450:` line, at the edges of
 * its window. crip_process_checksums() adds sample i, counted from 0, into
 * acu_sum_1_450 with weight i - 264599 when 450 * 588 <= i < 451 * 588: one
 * sector, the 451st. No fixture's audio lands on either edge with a value
 * that tells them apart, so a mutant that moved the lower bound by one sample
 * survived the suite (SETTLED.md, the checksums.h sweep). This feeds a track
 * a sample at each side of each edge, so either edge moved by one changes the
 * sum. */
#include "checksums.h"

#include <stdio.h>
#include <string.h>

#define FIRST 264600 /* 450 * 588, the window's first sample */
#define LAST  265187 /* 451 * 588 - 1, its last */

int main(void)
{
    const int nb = LAST + 2;
    uint8_t *audio = av_mallocz((size_t)nb * 4);
    cyanrip_track *t = av_mallocz(sizeof(*t));
    if (!audio || !t) {
        fprintf(stderr, "FAIL: out of memory\n");
        return 1;
    }
    t->nb_samples = nb;

    /* Inside at each edge, outside next to each */
    AV_WL32(audio + 4 * (FIRST - 1), 0x00030003);
    AV_WL32(audio + 4 * FIRST,       0x00010001);
    AV_WL32(audio + 4 * LAST,        0x00020002);
    AV_WL32(audio + 4 * (LAST + 1),  0x00050005);

    cyanrip_checksum_ctx s;
    crip_init_checksum_ctx(NULL, &s, t);
    /* In uneven pieces, as a read delivers them, one cut at the first edge */
    crip_process_checksums(&s, audio, 4 * FIRST);
    crip_process_checksums(&s, audio + 4 * FIRST, 4 * (nb - FIRST));

    const uint32_t want = 0x00010001u * 1 + 0x00020002u * (LAST - FIRST + 1);
    int fails = 0;
    if (s.acu_sum_1_450 != want) {
        fprintf(stderr, "FAIL: the 450 window summed %08X, want %08X: an edge "
                "moved, taking in or leaving out a sample beside it\n",
                (unsigned)s.acu_sum_1_450, (unsigned)want);
        fails++;
    }

    av_free(t->block_crcs);
    av_free(t);
    av_free(audio);
    if (!fails)
        printf("the 450 window's edges: the first and last sample in, their "
               "neighbours out\n");
    return !!fails;
}
