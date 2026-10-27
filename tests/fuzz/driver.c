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

/* Runs a fuzz harness without libFuzzer: each file named on the command line
 * as it is, then MUTATIONS variants of it, each from a fixed-seed generator
 * so a failure repeats. A variant flips bytes, cuts the input short or
 * repeats a slice of it. Not a fuzzer, since nothing steers it, but it runs
 * every harness in every build, and in CI's sanitizer rows under ASan and
 * UBSan, which a harness built only for libFuzzer would not be. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "fuzz.h"

#define MUTATIONS 2000

static uint64_t rng = 0x2545f4914f6cdd1dULL;

static uint32_t next(void)
{
    rng ^= rng << 13;
    rng ^= rng >> 7;
    rng ^= rng << 17;
    return (uint32_t)(rng >> 16);
}

static uint8_t *read_file(const char *name, size_t *size)
{
    FILE *f = fopen(name, "rb");
    if (!f)
        return NULL;
    uint8_t *buf = NULL;
    size_t n = 0, cap = 0;
    int c;
    while ((c = getc(f)) != EOF) {
        if (n == cap) {
            cap = cap ? cap * 2 : 4096;
            uint8_t *grown = realloc(buf, cap);
            if (!grown) {
                free(buf);
                fclose(f);
                return NULL;
            }
            buf = grown;
        }
        buf[n++] = c;
    }
    int bad = ferror(f);
    fclose(f);
    if (bad) {
        free(buf);
        return NULL;
    }
    *size = n;
    return buf ? buf : calloc(1, 1);
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: %s SEED...\n", argv[0]);
        return 2;
    }
    LLVMFuzzerInitialize(&argc, &argv);

    int runs = 0;
    for (int a = 1; a < argc; a++) {
        size_t size = 0;
        uint8_t *seed = read_file(argv[a], &size);
        if (!seed) {
            fprintf(stderr, "cannot read seed %s\n", argv[a]);
            return 1;
        }
        LLVMFuzzerTestOneInput(seed, size);
        runs++;

        /* Room for a variant twice the seed's size */
        uint8_t *buf = malloc(2 * size + 1);
        if (!buf)
            return 1;
        for (int m = 0; m < MUTATIONS; m++) {
            size_t n = size;
            memcpy(buf, seed, size);
            switch (next() % 3) {
            case 0: /* flip a few bytes */
                for (int k = 1 + next() % 8; k > 0 && n; k--)
                    buf[next() % n] ^= 1 + next() % 255;
                break;
            case 1: /* cut it short */
                n = n ? next() % n : 0;
                break;
            case 2: /* repeat a slice of it at its end */
                if (n) {
                    size_t from = next() % n, len = next() % (n - from + 1);
                    memcpy(buf + n, buf + from, len);
                    n += len;
                }
                break;
            }
            LLVMFuzzerTestOneInput(buf, n);
            runs++;
        }
        free(buf);
        free(seed);
    }
    printf("%d inputs from %d seed(s), none failing\n", runs, argc - 1);
    return 0;
}
