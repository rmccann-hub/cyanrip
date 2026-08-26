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

/* Drives the record writer directly and reads back what it wrote.
 *
 * WHY THIS EXISTS, and it is a measurement rather than a hunch. A mutation
 * sweep of src/cyanrip_log.c -- the file that writes the archival record --
 * scored 44.3%: of 88 single-operator changes to the program, 49 were changes
 * that the ENTIRE suite agreed were fine. Twenty of those were in this block,
 * the AccurateRip verdict, which is the strongest claim the log makes about a
 * rip. Flip one comparison and a track that was never compared against
 * anything is reported as accurately ripped, and every one of the 55 tests
 * passes.
 *
 * The reason is not carelessness. It is that every scenario passes -A, because
 * the verdict needs the AccurateRip database and the suite has no network --
 * so the whole surface was unreachable and therefore untested. The same is
 * true of four of the six pregap provenances, which need a drive's Q
 * sub-channel.
 *
 * THE WAY OUT IS THE ONE CLAUDE.md ALREADY NAMES: before accepting "no fixture
 * can reach this", check whether something else can. cyanrip_log_track_end()
 * reads `ctx->settings` and the track struct and calls no drive and no network,
 * so the states can simply be BUILT. Point ctx->logfile[0] at a tmpfile, fill
 * in the track, call the real function, and compare the real bytes it wrote.
 *
 * WHAT THIS IS AND IS NOT. It is not a mock: cyanrip_log.c and accurip.c are
 * the shipped objects, linked unmodified, and the assertions are against the
 * exact contract wording in PROVIDER-CONTRACT.md P2 -- not against a branch
 * index, which would prove only that a switch has arms. It does not prove a
 * disc is in the AccurateRip database, or that a drive returns a sub-channel;
 * those are still the network's and the hardware's to establish. It proves
 * that GIVEN a state, the record says the right thing about it -- which is
 * exactly the half that was unguarded.
 *
 * EVERY ASSERTION HERE WAS BORN KILLING A MUTANT. Each block names the
 * src/cyanrip_log.c line whose mutation survived before it existed, so the
 * revert-proof is not a separate ceremony: re-apply that operator and this
 * test fails. tools/mutate.py regenerates the list.
 */

#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <unistd.h>

/* The real headers, so a stub whose signature drifts from the declaration it
 * stands in for is a compile error rather than a silent mismatch at link
 * time. */
#include "cyanrip_main.h"
#include "cyanrip_log.h"
#include "cyanrip_encode.h"
#include "diagnostics.h"
#include "fun512.h"
#include "stall_watchdog.h"

static int failures;
static char captured[65536];

/* ---- the handful of externals cyanrip_log.c refers to and this test does
 * not exercise. Stubbed rather than linked so the test pulls in neither the
 * encoder (libavformat/libavfilter) nor the option table. A stub that is ever
 * actually reached is a bug in the test, so the ones that return values
 * return something a wrong assertion would notice. ---- */
volatile sig_atomic_t quit_now = 0;
volatile sig_atomic_t quit_signal = 0;
char *crip_invocation = NULL;
const int crip_max_paranoia_level = 2;
const char *vcstag = "logrender-test";
uint64_t paranoia_status[PARANOIA_CB_FINISHED + 1] = { 0 };
const cyanrip_out_fmt crip_fmt_info[CYANRIP_FORMATS_NB] = { { 0 } };

const char *cyanrip_fmt_desc(enum cyanrip_output_formats format)
{
    (void)format;
    return "STUB-FORMAT";
}

char *crip_get_path(cyanrip_ctx *ctx, enum CRIPPathType type, int create_dirs,
                    const cyanrip_out_fmt *fmt, void *arg)
{
    (void)ctx; (void)type; (void)create_dirs; (void)fmt; (void)arg;
    return NULL;
}

void crip_diag_record(const char *format, va_list args)
{
    (void)format; (void)args;
}

void crip_log_fun512(const uint8_t *sha512_digest, int idx,
                     char digest_str[CRIP_FUN512_STR_SIZE])
{
    (void)sha512_digest; (void)idx;
    snprintf(digest_str, CRIP_FUN512_STR_SIZE, "STUB");
}

void crip_stall_stats(crip_stall_stats_t *s)
{
    if (s)
        memset(s, 0, sizeof(*s));
}

void crip_stall_summary_line(char *buf, size_t buf_size,
                             const crip_stall_stats_t *s)
{
    (void)s;
    snprintf(buf, buf_size, "none");
}

/* ---- harness ---- */

#define FAIL(...) do {                                                        \
        printf("FAIL: ");                                                     \
        printf(__VA_ARGS__);                                                  \
        printf("\n");                                                         \
        failures++;                                                           \
    } while (0)

static cyanrip_ctx *new_ctx(void)
{
    cyanrip_ctx *ctx = calloc(1, sizeof(*ctx));
    if (!ctx) {
        printf("FAIL: out of memory\n");
        exit(1);
    }
    ctx->settings.outputs_num = 1;
    ctx->logfile[0] = tmpfile();
    if (!ctx->logfile[0]) {
        printf("FAIL: could not open a tmpfile to capture the log\n");
        exit(1);
    }
    return ctx;
}

static void free_ctx(cyanrip_ctx *ctx)
{
    if (ctx->logfile[0])
        fclose(ctx->logfile[0]);
    free(ctx);
}

/* Everything the writer put in the logfile since the last call. Read back from
 * the FILE the program actually wrote to, not from a buffer this test filled:
 * a test that compares a string to itself proves only that a constant can be
 * printed. */
static const char *drain(cyanrip_ctx *ctx)
{
    fflush(ctx->logfile[0]);
    rewind(ctx->logfile[0]);
    size_t n = fread(captured, 1, sizeof(captured) - 1, ctx->logfile[0]);
    captured[n] = '\0';
    /* Truncate for the next call. */
    if (ftruncate(fileno(ctx->logfile[0]), 0) != 0) { /* fall through */ }
    rewind(ctx->logfile[0]);
    return captured;
}

/* Substring is the wrong primitive for most of this file -- "assert against
 * the position, not the file" -- so every caller passes a whole line, and this
 * matches a whole line between newlines. A trailing-space or indentation
 * change is then a failure, which is the point: indentation is contract. */
static int has_line(const char *hay, const char *line)
{
    size_t len = strlen(line);
    const char *p = hay;
    while (*p) {
        const char *eol = strchr(p, '\n');
        size_t this_len = eol ? (size_t)(eol - p) : strlen(p);
        if (this_len == len && !memcmp(p, line, len))
            return 1;
        if (!eol)
            break;
        p = eol + 1;
    }
    return 0;
}

static void expect_line(const char *hay, const char *line, const char *what)
{
    if (!has_line(hay, line))
        FAIL("%s: no line %s", what, line);
}

static void expect_no_line(const char *hay, const char *line, const char *what)
{
    if (has_line(hay, line))
        FAIL("%s: line %s should not have been written", what, line);
}

/* A minimal audio track that renders without tripping anything. Callers
 * override the fields their case is about. */
static void base_track(cyanrip_track *t)
{
    memset(t, 0, sizeof(*t));
    t->number = 2;
    t->cd_track_number = 2;
    t->nb_samples = 176400;              /* 00:04.00 exactly */
    t->frames = 300;
    t->start_lsn = t->start_lsn_sig = 450;
    t->end_lsn = t->end_lsn_sig = 749;
    t->pregap_lsn = CDIO_INVALID_LSN;
    t->ebu_sample_peak = -1.0;
    t->ebu_true_peak = -0.5;
    t->direct_sample_peak = -1.0;
    t->sample_peak_rel_amp = pow(10.0, -1.0 / 20.0);
    t->ebu_integrated = -12.0;
    t->ebu_range = 3.0;
    t->ebu_lra_low = -14.0;
    t->ebu_lra_high = -11.0;
}

/* =====================================================================
 * The AccurateRip verdict.
 *
 * crip_find_ar() is three-valued and the whole block turns on it:
 *      0   the disc is not in the database at all
 *     >0   this checksum matched, and that is the confidence
 *     -1   the disc IS in the database and this checksum did not match
 *
 * so "no comparison was possible" and "compared and disagreed" are different
 * claims, and the log has separate words for them. Twenty mutants lived in
 * here.
 * ===================================================================== */

static CRIPAccuDBEntry ar_entries[4];

static void give_db(cyanrip_track *t, int nb, int max_conf)
{
    t->ar_db_status = CYANRIP_ACCUDB_FOUND;
    t->ar_db_entries = ar_entries;
    t->ar_db_nb_entries = nb;
    t->ar_db_max_confidence = max_conf;
    t->computed_crcs = 1;
}

static void test_accurip_disabled_says_disabled(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;
    base_track(&t);
    t.computed_crcs = 1;
    t.ar_db_status = CYANRIP_ACCUDB_DISABLED;
    ctx->settings.disable_accurip = 1;

    cyanrip_log_track_end(ctx, &t);
    const char *out = drain(ctx);

    /* "disabled" and "not found" are different claims about why there is no
     * verdict, and collapsing them is the defect this project is built to
     * avoid. Nothing asserted either until now. */
    expect_line(out, "  Accurip:       disabled", "accurip/disabled");
    expect_no_line(out, "  Accurip:       not found", "accurip/disabled");
    free_ctx(ctx);
}

static void test_accurip_disc_absent_says_not_found(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;
    base_track(&t);
    t.computed_crcs = 1;
    t.ar_db_status = CYANRIP_ACCUDB_NOT_FOUND;

    cyanrip_log_track_end(ctx, &t);
    const char *out = drain(ctx);

    expect_line(out, "  Accurip:       not found", "accurip/absent");
    /* No database, so no verdict may be attached to either checksum. */
    expect_line(out, "    Accurip v1:  00000000", "accurip/absent");
    expect_line(out, "    Accurip v2:  00000000", "accurip/absent");
    free_ctx(ctx);
}

/* cyanrip_log.c:511 [> to >=], :511 [&& to ||], :519 [> to >=],
 * :519 [&& to ||] -- the "accurately ripped" verdict itself. */
static void test_accurip_exact_match_reports_confidence(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;
    base_track(&t);
    ar_entries[0] = (CRIPAccuDBEntry){ .confidence = 7,
                                       .checksum = 0xAAAABBBB,
                                       .checksum_450 = 0x11112222 };
    give_db(&t, 1, 7);
    t.acurip_checksum_v1 = 0xAAAABBBB;
    t.acurip_checksum_v2 = 0xCCCCDDDD;    /* no entry, so -1 */

    cyanrip_log_track_end(ctx, &t);
    const char *out = drain(ctx);

    expect_line(out, "  Accurip:       disc found in database (max confidence: 7)",
                "accurip/v1-exact");
    expect_line(out, "    Accurip v1:  AAAABBBB (accurately ripped, confidence 7)",
                "accurip/v1-exact");
    /* The v2 line must stay BARE. v2 did not match, but v1 did, so the track
     * is verified and v2 has nothing of its own to report -- "not found,
     * either a new pressing, or bad rip" beside a verified track would read as
     * a defect in a rip that is exactly right. */
    expect_line(out, "    Accurip v2:  CCCCDDDD", "accurip/v1-exact");
    expect_no_line(out,
                   "    Accurip v2:  CCCCDDDD (not found, either a new pressing, or bad rip)",
                   "accurip/v1-exact");
    /* And the 450 block is not reached at all when either version matched. */
    if (strstr(out, "Accurip 450"))
        FAIL("accurip/v1-exact: the 450 line was printed for a verified track");
    free_ctx(ctx);
}

/* The mirror of the case above, which is spelled differently in the source
 * (`match_v2 < 1` on the v1 line, `match_v1 < 0` on the v2 line) and must
 * still behave the same way. */
static void test_accurip_v2_match_reports_confidence(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;
    base_track(&t);
    ar_entries[0] = (CRIPAccuDBEntry){ .confidence = 3,
                                       .checksum = 0xCCCCDDDD,
                                       .checksum_450 = 0x0 };
    give_db(&t, 1, 3);
    t.acurip_checksum_v1 = 0xAAAABBBB;    /* no entry, so -1 */
    t.acurip_checksum_v2 = 0xCCCCDDDD;

    cyanrip_log_track_end(ctx, &t);
    const char *out = drain(ctx);

    expect_line(out, "    Accurip v2:  CCCCDDDD (accurately ripped, confidence 3)",
                "accurip/v2-exact");
    /* The v1 line stays BARE, and the first version of this test asserted the
     * opposite -- that v1 would say "not found, either a new pressing, or bad
     * rip". It does not, and the rule is worth stating because it is not
     * obvious from either line on its own: the "not found" note is attached
     * only when NEITHER version matched. v1 and v2 are two checksums over the
     * same audio, so a track that verified through one of them is verified,
     * and printing "bad rip" beside the other would be a scarier claim than
     * the evidence supports. This is the exact mirror of the v1-match case
     * above, and the source spells the two conditions differently
     * (`match_v2 < 1` against `match_v1 < 0`) which is what made it look
     * asymmetric. */
    expect_line(out, "    Accurip v1:  AAAABBBB", "accurip/v2-exact");
    expect_no_line(out,
                   "    Accurip v1:  AAAABBBB (not found, either a new pressing, or bad rip)",
                   "accurip/v2-exact");
    free_ctx(ctx);
}

/* The one input on which those two spellings genuinely diverge, pinned so a
 * change to it is visible.
 *
 * `match_v2 < 1` and `match_v1 < 0` agree over everything crip_find_ar() can
 * return when the disc IS in the database -- -1, or a confidence of at least
 * one. They part on a confidence of exactly 0, which a malformed database
 * response can produce: then the v1 line calls it not-found and the v2 line
 * does not, for one and the same pair of checksums.
 *
 * THIS TEST DOCUMENTS, IT DOES NOT ENDORSE. Unifying the two spellings is a
 * change to a P2 line's contents and belongs in a handshake round, not in a
 * test that noticed it. What the test buys meanwhile is that the divergence
 * cannot change by accident, and that the next person to read the two
 * conditions finds out it is real rather than guessing as I did. */
static void test_zero_confidence_entry_is_spelled_asymmetrically(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;
    base_track(&t);
    ar_entries[0] = (CRIPAccuDBEntry){ .confidence = 0,
                                       .checksum = 0xAAAABBBB,
                                       .checksum_450 = 0x0 };
    give_db(&t, 1, 0);
    t.acurip_checksum_v1 = 0xAAAABBBB;   /* matches, confidence 0 */
    t.acurip_checksum_v2 = 0xAAAABBBB;   /* same, so also 0 */

    cyanrip_log_track_end(ctx, &t);
    const char *out = drain(ctx);

    expect_line(out,
                "    Accurip v1:  AAAABBBB (not found, either a new pressing, or bad rip)",
                "accurip/zero-confidence");
    expect_line(out, "    Accurip v2:  AAAABBBB", "accurip/zero-confidence");
    expect_no_line(out,
                   "    Accurip v2:  AAAABBBB (not found, either a new pressing, or bad rip)",
                   "accurip/zero-confidence");
    /* And the 450 fallback is NOT reached: it is gated on both versions having
     * been compared and disagreed (`< 0`), which a confidence of 0 is not.
     * Asserting the absence is what pins the `< 0` -- the presence assertions
     * above are satisfied by `<= 0` just as well. */
    if (strstr(out, "Accurip 450"))
        FAIL("accurip/zero-confidence: the 450 fallback was reached for "
             "checksums that DID match the database");
    free_ctx(ctx);
}

/* cyanrip_log.c:513 [< to <=] -- the boundary of "did the other version
 * match", which is spelled `match_v2 < 1` and therefore turns at a confidence
 * of exactly one. Every other case in this file uses a larger confidence, so
 * this is the single input that separates `< 1` from `<= 1`. */
static void test_accurip_other_matched_at_confidence_one(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;
    base_track(&t);
    ar_entries[0] = (CRIPAccuDBEntry){ .confidence = 1,
                                       .checksum = 0xCCCCDDDD,
                                       .checksum_450 = 0x0 };
    give_db(&t, 1, 1);
    t.acurip_checksum_v1 = 0xAAAABBBB;   /* absent, so -1 */
    t.acurip_checksum_v2 = 0xCCCCDDDD;   /* present at exactly 1 */

    cyanrip_log_track_end(ctx, &t);
    const char *out = drain(ctx);

    expect_line(out, "    Accurip v2:  CCCCDDDD (accurately ripped, confidence 1)",
                "accurip/confidence-one");
    /* One agreeing submission is thin evidence, but it IS a match, so the v1
     * line must stay bare exactly as it does at confidence 3. */
    expect_line(out, "    Accurip v1:  AAAABBBB", "accurip/confidence-one");
    expect_no_line(out,
                   "    Accurip v1:  AAAABBBB (not found, either a new pressing, or bad rip)",
                   "accurip/confidence-one");
    free_ctx(ctx);
}

/* cyanrip_log.c:530 [> to >=] -- the threshold inside the ZERO-checksum arm.
 *
 * The same 3/4 threshold is written twice, and the copy at :548 decides the
 * ordinary partial match while this one guards the zero-checksum caveat. A
 * test with a non-zero 450 checksum exercises :548 only, which is why :530's
 * comparison survived a sweep that killed :548's. This is the input that
 * separates them: a zero checksum whose database confidence sits exactly ON
 * the threshold. */
static void test_accurip_450_zero_checksum_at_the_threshold(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;
    base_track(&t);
    /* max confidence 7 -> threshold 3*(7+1)/4 = 6. Confidence exactly 6 is
     * NOT over it. */
    ar_entries[0] = (CRIPAccuDBEntry){ .confidence = 6,
                                       .checksum = 0x12345678,
                                       .checksum_450 = 0x0 };
    give_db(&t, 1, 7);
    t.acurip_checksum_v1 = 0xDEADBEEF;
    t.acurip_checksum_v2 = 0xFEEDFACE;
    t.acurip_checksum_v1_450 = 0x0;

    cyanrip_log_track_end(ctx, &t);
    const char *out = drain(ctx);

    expect_line(out, "    Accurip 450: 00000000 (not found)",
                "accurip/450-zero-at-threshold");
    expect_no_line(out,
                   "    Accurip 450: 00000000 (no comparison possible, a checksum of 0 is meaningless)",
                   "accurip/450-zero-at-threshold");
    free_ctx(ctx);
}

/* cyanrip_log.c:526 [< to <=], [&& to ||] -- whether the 450 block is
 * reached, i.e. whether BOTH versions failed. */
static void test_accurip_both_fail_reaches_the_450_block(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;
    base_track(&t);
    ar_entries[0] = (CRIPAccuDBEntry){ .confidence = 9,
                                       .checksum = 0x12345678,
                                       .checksum_450 = 0x9ABCDEF0 };
    give_db(&t, 1, 9);
    t.acurip_checksum_v1 = 0xDEADBEEF;
    t.acurip_checksum_v2 = 0xFEEDFACE;
    t.acurip_checksum_v1_450 = 0x0BADF00D;   /* no entry, so -1 */

    cyanrip_log_track_end(ctx, &t);
    const char *out = drain(ctx);

    expect_line(out,
                "    Accurip v1:  DEADBEEF (not found, either a new pressing, or bad rip)",
                "accurip/both-fail");
    expect_line(out,
                "    Accurip v2:  FEEDFACE (not found, either a new pressing, or bad rip)",
                "accurip/both-fail");
    expect_line(out, "    Accurip 450: 0BADF00D (not found)", "accurip/both-fail");
    free_ctx(ctx);
}

/* cyanrip_log.c:530 and :548 [> to >=] and [&& to ||] -- the partial-match
 * threshold, which is 3/4 of (max confidence + 1) and appears twice. */
static void test_accurip_450_partial_needs_three_quarters(void)
{
    /* max_conf 7 -> threshold is 3*(7+1)/4 = 6, so 7 is over and 6 is not.
     * Both sides of the boundary, because a threshold tested from one side
     * only is satisfied by any threshold at all. */
    const struct { int conf; int partial; } cases[] = {
        { 7, 1 },
        { 6, 0 },
    };

    for (size_t i = 0; i < sizeof(cases)/sizeof(*cases); i++) {
        cyanrip_ctx *ctx = new_ctx();
        cyanrip_track t;
        base_track(&t);
        ar_entries[0] = (CRIPAccuDBEntry){ .confidence = cases[i].conf,
                                           .checksum = 0x12345678,
                                           .checksum_450 = 0x0BADF00D };
        give_db(&t, 1, 7);
        t.acurip_checksum_v1 = 0xDEADBEEF;
        t.acurip_checksum_v2 = 0xFEEDFACE;
        t.acurip_checksum_v1_450 = 0x0BADF00D;

        cyanrip_log_track_end(ctx, &t);
        const char *out = drain(ctx);

        char want[160];
        snprintf(want, sizeof(want),
                 "    Accurip 450: 0BADF00D (matches Accurip DB, confidence %i, "
                 "track is partially accurately ripped)", cases[i].conf);
        if (cases[i].partial) {
            expect_line(out, want, "accurip/450-over-threshold");
        } else {
            expect_no_line(out, want, "accurip/450-under-threshold");
            expect_line(out, "    Accurip 450: 0BADF00D (not found)",
                        "accurip/450-under-threshold");
        }
        free_ctx(ctx);
    }
}

/* cyanrip_log.c:530 [== to !=] -- the zero-checksum guard.
 *
 * A checksum of zero compares equal to every other zero in the database, so a
 * "match" is an artifact of the value and not evidence about this audio. The
 * old wording carried "confidence 200" in the same parenthetical as the
 * caveat, so a consumer keying on (result, confidence) read a verification for
 * audio nothing was compared against. Nothing has asserted the fix since it
 * shipped. */
static void test_accurip_450_zero_checksum_claims_nothing(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;
    base_track(&t);
    ar_entries[0] = (CRIPAccuDBEntry){ .confidence = 200,
                                       .checksum = 0x12345678,
                                       .checksum_450 = 0x0 };
    give_db(&t, 1, 7);
    t.acurip_checksum_v1 = 0xDEADBEEF;
    t.acurip_checksum_v2 = 0xFEEDFACE;
    t.acurip_checksum_v1_450 = 0x0;

    cyanrip_log_track_end(ctx, &t);
    const char *out = drain(ctx);

    expect_line(out,
                "    Accurip 450: 00000000 (no comparison possible, a checksum of 0 is meaningless)",
                "accurip/450-zero");
    /* The number must not appear anywhere on that line: the machine-readable
     * shape has to agree with the prose, or a consumer reading (result,
     * confidence) still sees a confidence. */
    if (strstr(out, "confidence 200"))
        FAIL("accurip/450-zero: a confidence figure was published for a "
             "checksum that was never compared against anything");
    free_ctx(ctx);
}

/* cyanrip_log.c:526 [< to <=] -- the gate on the 450 fallback, which asks
 * whether BOTH versions were compared and disagreed.
 *
 * `match < 0` is "compared, did not match"; a confidence of 0 is "matched, but
 * nobody agrees", which is a different thing and must not open the fallback.
 * The two comparisons are separate operators, so a single-operator mutation
 * flips only one of them -- and the case that separates them therefore needs
 * the two versions to differ. Both orders, because mutating the other
 * comparison is a different mutant. */
static void test_accurip_450_gate_needs_both_compared_and_failed(void)
{
    for (int zero_is_v1 = 0; zero_is_v1 < 2; zero_is_v1++) {
        cyanrip_ctx *ctx = new_ctx();
        cyanrip_track t;
        base_track(&t);
        ar_entries[0] = (CRIPAccuDBEntry){ .confidence = 0,
                                           .checksum = 0xAAAABBBB,
                                           .checksum_450 = 0x33334444 };
        give_db(&t, 1, 5);
        /* One version matches at confidence 0, the other is absent (-1). */
        t.acurip_checksum_v1 = zero_is_v1 ? 0xAAAABBBB : 0x99998888;
        t.acurip_checksum_v2 = zero_is_v1 ? 0x99998888 : 0xAAAABBBB;
        t.acurip_checksum_v1_450 = 0x33334444;

        cyanrip_log_track_end(ctx, &t);
        const char *out = drain(ctx);

        if (strstr(out, "Accurip 450"))
            FAIL("accurip/450-gate: the fallback was reached with %s matched "
                 "at confidence 0 -- that is a match, not a disagreement",
                 zero_is_v1 ? "v1" : "v2");
        free_ctx(ctx);
    }
}

/* cyanrip_log.c:607 [> to >=] -- the `Scope:` line.
 *
 * This is the line that stops a consumer adding the per-track paranoia
 * counters up and expecting the disc total. They only sum when nothing
 * re-read: the per-track baseline is snapshotted after `repeat_ripping:`, so a
 * -Z re-read resets it and the per-track figure describes the LAST pass while
 * the disc counters are process-global and sum every pass. Round 5 recorded
 * the opposite as a verified invariant and it survived four checks, because
 * every artifact anyone checked it against had read each track exactly once.
 *
 * The line exists to say so, and it is printed only when a track was actually
 * re-read -- so a single-pass rip stays byte-identical. Both halves are
 * asserted: a re-read must carry the caveat, and a single read must not. */
static void test_scope_line_marks_a_re_read(void)
{
    const struct { int repeats; int want_scope; } cases[] = {
        { 0, 0 }, { 1, 0 }, { 3, 1 },
    };

    for (size_t i = 0; i < sizeof(cases)/sizeof(*cases); i++) {
        cyanrip_ctx *ctx = new_ctx();
        cyanrip_track t;
        base_track(&t);
        t.total_repeats = cases[i].repeats;

        cyanrip_log_track_end(ctx, &t);
        const char *out = drain(ctx);

        expect_line(out, "  Paranoia status counts:", "scope/block");
        char want[160];
        snprintf(want, sizeof(want),
                 "    Scope:         the last of %i reads; the disc totals "
                 "below sum all of them", cases[i].repeats);
        if (cases[i].want_scope)
            expect_line(out, want, "scope/present");
        else if (strstr(out, "Scope:"))
            FAIL("scope: a Scope: line was written for a track read %i time(s), "
                 "which makes a single-pass rip differ from every previous one",
                 cases[i].repeats);
        free_ctx(ctx);
    }
}

/* =====================================================================
 * Pregap provenance. Four of the six states need a drive's Q sub-channel and
 * no disc image can produce them, so until now the only wordings any artifact
 * had ever shown were `unknown (sub-channel unreadable)` and a plain LSN.
 * cyanrip_log.c:315 [== to !=] swapped two REASONS and nothing noticed.
 * ===================================================================== */

static void test_pregap_reasons_are_distinct(void)
{
    const struct {
        enum cyanrip_pregap_source src;
        lsn_t lsn;
        const char *reason;
        const char *provenance;    /* NULL when none is printed */
    } cases[] = {
        { CYANRIP_PREGAP_SRC_ERR_READ, CDIO_INVALID_LSN,
          "    Pregap LSN:  unknown (sub-channel unreadable)", NULL },
        { CYANRIP_PREGAP_SRC_ERR_CRC, CDIO_INVALID_LSN,
          "    Pregap LSN:  unknown (sub-channel CRC mismatches)", NULL },
        { CYANRIP_PREGAP_SRC_NONE, CDIO_INVALID_LSN,
          "    Pregap LSN:  none", NULL },
        { CYANRIP_PREGAP_SRC_TOC, 300,
          "    Pregap LSN:  300 (duration: 00:02.00)",
          "    Pregap source: TOC" },
        { CYANRIP_PREGAP_SRC_SUBCHANNEL, 300,
          "    Pregap LSN:  300 (duration: 00:02.00)",
          "    Pregap source: sub-channel (not signalled by TOC)" },
        { CYANRIP_PREGAP_SRC_LEADIN, 300,
          "    Pregap LSN:  300 (duration: 00:02.00)",
          "    Pregap source: lead-in" },
    };

    for (size_t i = 0; i < sizeof(cases)/sizeof(*cases); i++) {
        cyanrip_ctx *ctx = new_ctx();
        cyanrip_track t;
        base_track(&t);
        t.pregap_source = cases[i].src;
        t.pregap_lsn = cases[i].lsn;
        t.start_lsn = t.start_lsn_sig = 450;   /* 450 - 300 = 150 frames */

        cyanrip_log_track_end(ctx, &t);
        const char *out = drain(ctx);

        expect_line(out, cases[i].reason, "pregap/reason");
        if (cases[i].provenance)
            expect_line(out, cases[i].provenance, "pregap/provenance");

        /* Each reason excludes the other two. `none` and `unknown (reason)`
         * are different claims and a log that could say either must never say
         * the wrong one. */
        for (size_t j = 0; j < sizeof(cases)/sizeof(*cases); j++)
            if (strcmp(cases[j].reason, cases[i].reason))
                expect_no_line(out, cases[j].reason, "pregap/reason-exclusive");

        free_ctx(ctx);
    }
}

/* cyanrip_log.c:305 [== to !=] -- the track-1 lead-in.
 *
 * A disc with no HTOA expresses track 1's pregap only as the 2-second lead-in,
 * which the LSN arithmetic yields as 0 -- so 150 is added. When track 1 DOES
 * signal a pregap the subtraction already is those sectors, and adding them
 * counts the same physical sectors twice: the pregap.cue fixture once reported
 * `300 frames` for a gap its own cue sheet put at 150. Both halves are pinned,
 * plus a non-first track, which must never get the addition. */
static void test_track_one_lead_in_is_added_once(void)
{
    const struct { int number; lsn_t pregap; lsn_t start; int want; } cases[] = {
        { 1, 0,   0,   150 },   /* no HTOA: arithmetic gives 0, lead-in is all of it */
        { 1, 0,   150, 150 },   /* HTOA of 150: already the lead-in, not doubled */
        { 2, 300, 450, 150 },   /* a later track: no lead-in involved */
    };

    for (size_t i = 0; i < sizeof(cases)/sizeof(*cases); i++) {
        cyanrip_ctx *ctx = new_ctx();
        cyanrip_track t;
        base_track(&t);
        t.number = cases[i].number;
        t.pregap_source = CYANRIP_PREGAP_SRC_TOC;
        t.pregap_lsn = cases[i].pregap;
        t.start_lsn = t.start_lsn_sig = cases[i].start;

        cyanrip_log_track_end(ctx, &t);
        const char *out = drain(ctx);

        char want[80];
        snprintf(want, sizeof(want), "    Pregap length: %i frames", cases[i].want);
        expect_line(out, want, "pregap/lead-in");
        free_ctx(ctx);
    }
}

/* =====================================================================
 * Pre-emphasis, and the two independent flags that can de-emphasise.
 * cyanrip_log.c:410 [|| to &&] survived: the fixture with pre-emphasis is
 * never ripped with -f/--deemphasis, so only one of the four states was ever
 * rendered.
 * ===================================================================== */

static void test_preemphasis_states(void)
{
    const struct {
        int preemph, in_subcode, deemph, force;
        const char *want;
    } cases[] = {
        { 0, 0, 0, 0, "  Preemphasis:   none detected" },
        { 0, 0, 0, 1, "  Preemphasis:   none detected (deemphasis forced)" },
        { 1, 0, 0, 0, "  Preemphasis:   present (TOC)" },
        { 1, 1, 0, 0, "  Preemphasis:   present (subcode)" },
        { 1, 0, 1, 0, "  Preemphasis:   present (TOC) (deemphasis applied)" },
        { 1, 1, 0, 1, "  Preemphasis:   present (subcode) (deemphasis applied)" },
    };

    for (size_t i = 0; i < sizeof(cases)/sizeof(*cases); i++) {
        cyanrip_ctx *ctx = new_ctx();
        cyanrip_track t;
        base_track(&t);
        t.preemphasis = cases[i].preemph;
        t.preemphasis_in_subcode = cases[i].in_subcode;
        ctx->settings.deemphasis = cases[i].deemph;
        ctx->settings.force_deemphasis = cases[i].force;

        cyanrip_log_track_end(ctx, &t);
        expect_line(drain(ctx), cases[i].want, "preemphasis");
        free_ctx(ctx);
    }
}

/* =====================================================================
 * The secure re-read verdict, all three arms. `not attempted` and `did NOT
 * converge` are the two a consumer must never confuse, and only `converged`
 * appears in any committed artifact.
 * ===================================================================== */

static void test_secure_reread_verdicts(void)
{
    const struct {
        enum cyanrip_secure_rip_state state;
        int repeats;
        const char *want;
    } cases[] = {
        { CYANRIP_SECURE_RIP_NA,        0, "  Secure re-read:  not attempted" },
        { CYANRIP_SECURE_RIP_CONVERGED, 3, "  Secure re-read:  converged after 3 reads" },
        { CYANRIP_SECURE_RIP_LIMIT_HIT, 9,
          "  Secure re-read:  did NOT converge after 9 reads (repeat limit hit)" },
    };

    for (size_t i = 0; i < sizeof(cases)/sizeof(*cases); i++) {
        cyanrip_ctx *ctx = new_ctx();
        cyanrip_track t;
        base_track(&t);
        t.secure_rip_state = cases[i].state;
        t.total_repeats = cases[i].repeats;

        cyanrip_log_track_end(ctx, &t);
        const char *out = drain(ctx);
        expect_line(out, cases[i].want, "secure-reread");
        for (size_t j = 0; j < sizeof(cases)/sizeof(*cases); j++)
            if (j != i)
                expect_no_line(out, cases[j].want, "secure-reread-exclusive");
        free_ctx(ctx);
    }
}

/* cyanrip_log.c:607 [> to >=] -- the EAC CRC's "(after N rips)" suffix, which
 * must appear only when the track was actually re-read. */
static void test_eac_crc_repeat_suffix(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;
    base_track(&t);
    t.computed_crcs = 1;
    t.eac_crc = 0x1234ABCD;
    t.total_repeats = 0;
    t.ar_db_status = CYANRIP_ACCUDB_NOT_FOUND;

    cyanrip_log_track_end(ctx, &t);
    expect_line(drain(ctx), "  EAC CRC32:     1234ABCD", "eac-crc/single");

    base_track(&t);
    t.computed_crcs = 1;
    t.eac_crc = 0x1234ABCD;
    t.total_repeats = 4;
    t.ar_db_status = CYANRIP_ACCUDB_NOT_FOUND;

    cyanrip_log_track_end(ctx, &t);
    expect_line(drain(ctx), "  EAC CRC32:     1234ABCD (after 4 rips)",
                "eac-crc/repeated");
    free_ctx(ctx);
}

/* cyanrip_log.c:466 [> to >=] -- the timing block is written only when a time
 * was actually measured. Zero is "not measured", and printing "0.00 s" and an
 * infinite speed for it would be a confident wrong field. */
static void test_timing_block_only_when_measured(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;
    base_track(&t);
    t.rip_time_us = 0;

    cyanrip_log_track_end(ctx, &t);
    const char *out = drain(ctx);
    if (strstr(out, "Extraction speed") || strstr(out, "Elapsed:"))
        FAIL("timing: a timing block was written for a track that was never timed");

    base_track(&t);
    t.frames = 300;                 /* 300/75 = 4.0 s of audio */
    t.rip_time_us = 2000000;        /* in 2.0 s, so 2.0x */
    cyanrip_log_track_end(ctx, &t);
    out = drain(ctx);
    expect_line(out, "    Extraction speed:  2.0x", "timing/speed");
    expect_line(out, "    Elapsed:            2.00 s", "timing/elapsed");
    free_ctx(ctx);
}

/* =====================================================================
 * The two independent reasons End LSN can differ from End LSN sig. One label
 * for two causes is the defect that made an 11400-frame CD-Extra session gap
 * read as a read offset, a field normally worth one frame.
 * ===================================================================== */

static void test_end_lsn_suffixes_name_their_cause(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;

    base_track(&t);                              /* neither */
    cyanrip_log_track_end(ctx, &t);
    expect_line(drain(ctx), "    End LSN:     749", "end-lsn/plain");

    base_track(&t);                              /* read offset only */
    t.end_lsn = 750;
    cyanrip_log_track_end(ctx, &t);
    expect_line(drain(ctx), "    End LSN:     749 (with offset: 750)",
                "end-lsn/offset");

    base_track(&t);                              /* session gap */
    t.end_lsn = 749 - 11400;
    t.end_lsn_session_gap = 11400;
    cyanrip_log_track_end(ctx, &t);
    const char *out = drain(ctx);
    expect_line(out,
                "    End LSN:     749 (less 11400 frame CD-Extra session gap, read to: -10651)",
                "end-lsn/session-gap");
    expect_no_line(out, "    End LSN:     749 (with offset: -10651)",
                   "end-lsn/session-gap");

    free_ctx(ctx);
}

/* The lead-in/lead-out padding lines, which say how many frames of the file
 * are silence this program inserted rather than audio it read. Neither has
 * ever appeared in a committed artifact. */
static void test_padding_lines(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;
    base_track(&t);
    t.frames_before_disc_start = 1;
    t.frames_after_disc_end = 2;
    t.pregap_source = CYANRIP_PREGAP_SRC_TOC;
    t.pregap_lsn = 300;

    cyanrip_log_track_end(ctx, &t);
    const char *out = drain(ctx);
    expect_line(out, "    Prepended:   1 frames of silence", "padding/before");
    expect_line(out, "    Appended:    2 frames of silence", "padding/after");
    free_ctx(ctx);
}

/* A data track is never decoded, so it reports its size and stops. The
 * `Data bytes:` line is in P2 and appears in no committed artifact. */
static void test_data_track_reports_bytes_and_stops(void)
{
    cyanrip_ctx *ctx = new_ctx();
    cyanrip_track t;
    base_track(&t);
    t.track_is_data = 1;
    t.frames = 1000;

    cyanrip_log_track_end(ctx, &t);
    const char *out = drain(ctx);
    expect_line(out, "    Data bytes:  2352000 (2.24 Mib)", "data-track");
    /* And none of the audio-only blocks. */
    if (strstr(out, "Duration:") || strstr(out, "Sample peak level")
        || strstr(out, "Secure re-read"))
        FAIL("data-track: an audio-only block was written for a data track");
    free_ctx(ctx);
}

int main(void)
{
    test_accurip_disabled_says_disabled();
    test_accurip_disc_absent_says_not_found();
    test_accurip_exact_match_reports_confidence();
    test_accurip_v2_match_reports_confidence();
    test_zero_confidence_entry_is_spelled_asymmetrically();
    test_accurip_other_matched_at_confidence_one();
    test_accurip_450_zero_checksum_at_the_threshold();
    test_accurip_450_gate_needs_both_compared_and_failed();
    test_scope_line_marks_a_re_read();
    test_accurip_both_fail_reaches_the_450_block();
    test_accurip_450_partial_needs_three_quarters();
    test_accurip_450_zero_checksum_claims_nothing();

    test_pregap_reasons_are_distinct();
    test_track_one_lead_in_is_added_once();

    test_preemphasis_states();
    test_secure_reread_verdicts();
    test_eac_crc_repeat_suffix();
    test_timing_block_only_when_measured();

    test_end_lsn_suffixes_name_their_cause();
    test_padding_lines();
    test_data_track_reports_bytes_and_stops();

    if (failures) {
        printf("%i check(s) failed\n", failures);
        return 1;
    }
    printf("log rendering: all checks passed\n");
    return 0;
}
