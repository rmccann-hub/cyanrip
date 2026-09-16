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

/* The cache probe's EVIDENCE block in the -j record.
 *
 * ITS OWN BINARY, AND THAT IS NOT TIDINESS. crip_diag_write() latches on
 * `diag_written` so atexit cannot write the record twice, which means ONE
 * record per process -- so a second test that writes one gets an empty file
 * and fails for a reason that looks nothing like the latch. Found exactly that
 * way while adding this to tests/diag.c. The alternative was resetting the
 * latch from crip_diag_enable(), which is changing what the program does to
 * suit a test, and this repository has that the other way round.
 */

#include <errno.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "diagnostics.h"
#include "cache_probe.h"

static int failures;

/* The rest of the stub set diagnostics.c needs to link. Same list as
 * tests/diag.c: the record reads the invocation string and the quit flags, and
 * neither is what this test is about. */
char *crip_invocation = (char *)"cyanrip (cache-probe evidence unit test)";
volatile sig_atomic_t quit_now = 0;
volatile sig_atomic_t quit_signal = 0;

/* The build's own vcs tag is irrelevant here and pinning it keeps this test
 * independent of the tree's commit. */
const char *vcstag = "diagcache-unit-test";

struct cyanrip_ctx;
void cyanrip_log(struct cyanrip_ctx *ctx, int verbose, const char *format, ...);
void cyanrip_log(struct cyanrip_ctx *ctx, int verbose, const char *format, ...)
{
    (void)ctx; (void)verbose; (void)format;
}

/* THE CACHE PROBE'S EVIDENCE, SUPPLIED HERE RATHER THAN LINKED.
 *
 * Same move as tests/stall.c supplying its own cyanrip_log(): diag_test links
 * diagnostics.c and stall_watchdog.c, and pulling in cache_probe.c would drag
 * libcdio and a live drive handle into a test about JSON rendering.
 *
 * It is also strictly better than linking it, and that is the point. The real
 * probe REFUSES on an image driver, so no fixture in this repository can ever
 * make it emit a series -- exactly the "no fixture can reach this" claim that
 * is a statement about the harness rather than about the code. Driving the
 * struct directly reaches the state the harness cannot drive the program into,
 * which is the same move as splitting the Q sub-channel decode out for
 * tests/subq.c. */
static crip_cache_evidence_t fake_evidence;

const crip_cache_evidence_t *crip_cache_evidence(void)
{
    return &fake_evidence;
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

/* The series a rig session would produce, rendered without a rig.
 *
 * The numbers are the ones actually measured on the PIONEER BD-RW BDR-209D and
 * written up in docs/KNOWN-ISSUES.md: a full-stroke calibration around 342.9 ms
 * against short backseeks around 2.2 ms. Under the CURRENT rule every one of
 * those scores as a hit, which is why eight sessions reported "at least 2048
 * sectors ... search ceiling reached".
 *
 * THIS TEST DOES NOT ASSERT THAT THE RULE IS RIGHT. It asserts that the
 * evidence reaches the record, because until round 21 it did not reach
 * anything -- every one of those eight sessions is unusable for fixing the
 * defect it demonstrates, and a read time cannot be re-taken. */
static void test_cache_probe_evidence_reaches_the_record(void)
{
    char path[] = "/tmp/cripdiagXXXXXX";
    int fd = mkstemp(path);
    if (fd < 0) {
        fprintf(stderr, "FAIL: mkstemp: %s\n", strerror(errno));
        failures++;
        return;
    }
    close(fd);

    memset(&fake_evidence, 0, sizeof(fake_evidence));
    fake_evidence.ran          = 1;
    fake_evidence.miss_cost_us = 342900;
    fake_evidence.hit_ratio    = 4;
    fake_evidence.calib_us[0]  = 341800;
    fake_evidence.calib_us[1]  = 342900;
    fake_evidence.calib_us[2]  = 343500;
    for (int i = 0, run = 1; i < 12; i++, run *= 2) {
        fake_evidence.step_run[i] = run;
        fake_evidence.step_us[i]  = 2200 + i * 30;
        fake_evidence.step_hit[i] = 1;
        fake_evidence.nb_steps    = i + 1;
    }
    fake_evidence.stop = CRIP_CACHE_CEILING;

    crip_diag_enable(path);
    crip_diag_write();

    char *out = slurp(path);
    remove(path);
    if (!out)
        return;

    if (!*out) {
        fprintf(stderr, "FAIL: cache_probe evidence: the record is EMPTY. "
                        "crip_diag_write() latches on `diag_written` so only "
                        "the first caller in a process writes -- this test "
                        "must run before any other that writes a record\n");
        failures++;
        free(out);
        return;
    }

    /* Asserted on the VALUES, not on the key being present. A block that
     * renders its keys with zeroes in them would satisfy a presence check and
     * would be exactly as useless as no block at all. */
    const struct { const char *needle; const char *why; } want[] = {
        { "\"cache_probe\"",       "the block itself"                        },
        { "\"ran\": true",         "a probe that ran must not read as absent" },
        { "342900",                 "the median that became the threshold"    },
        { "341800",                 "the calibration reads, all three"        },
        { "\"hit_ratio\": 4",      "the ratio in force when it was decided"  },
        { "\"run_sectors\": 2048", "the series must reach the ceiling"       },
        { "\"reread_us\": 2200",   "the first re-read, in full"              },
        { "\"scored_hit\": true",  "what the CURRENT rule said, recorded"    },
    };
    for (size_t i = 0; i < sizeof(want) / sizeof(*want); i++) {
        if (!strstr(out, want[i].needle)) {
            fprintf(stderr, "FAIL: cache_probe evidence: %s absent -- %s\n",
                    want[i].needle, want[i].why);
            failures++;
        }
    }

    /* Twelve steps, not eleven and not thirteen: 1 doubling to 2048. A series
     * truncated at the bound would still contain every string above. */
    int n = 0;
    for (const char *p = out; (p = strstr(p, "\"run_sectors\"")); p++)
        n++;
    if (n != 12) {
        fprintf(stderr, "FAIL: cache_probe evidence: %d steps recorded, "
                        "expected 12 (1 doubling to 2048)\n", n);
        failures++;
    }

    free(out);
    memset(&fake_evidence, 0, sizeof(fake_evidence));
}

int main(void)
{
    test_cache_probe_evidence_reaches_the_record();

    if (failures)
        fprintf(stderr, "%d check(s) failed\n", failures);
    else
        printf("all cache-probe evidence checks passed\n");

    return !!failures;
}
