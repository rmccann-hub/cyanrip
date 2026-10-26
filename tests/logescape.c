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

/* The log's formatter, against printf() itself and against the escapes it
 * promises.
 *
 * Two halves, and each answers a different way of being wrong. The first runs
 * every conversion this program's formats use through both crip_vbprintf_
 * escaped() and the C library's vsnprintf() and wants the same bytes: the
 * formatter replaces printf() under every line of the log, so a width, a
 * precision or a length modifier it misreads would silently move every
 * column, and the independent artifact to hold it to is the C library. The
 * second gives it each character the escape exists for, and each one it must
 * leave alone, and wants the exact text log_escape.h names. */

#include <inttypes.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include <libavutil/bprint.h>

#include "log_escape.h"

static int failures;

static void fmt_escaped(AVBPrint *b, const char *format, ...)
{
    va_list args;
    va_start(args, format);
    crip_vbprintf_escaped(b, format, args);
    va_end(args);
}

/* Formats the same arguments both ways and wants identical bytes */
#define SAME(...)                                                              \
    do {                                                                       \
        char want[512];                                                        \
        snprintf(want, sizeof(want), __VA_ARGS__);                             \
        AVBPrint got;                                                          \
        av_bprint_init(&got, 0, AV_BPRINT_SIZE_UNLIMITED);                     \
        fmt_escaped(&got, __VA_ARGS__);                                        \
        if (strcmp(got.str, want)) {                                           \
            fprintf(stderr, "FAIL line %i: printf gives [%s], ours [%s]\n",    \
                    __LINE__, want, got.str);                                  \
            failures++;                                                        \
        }                                                                      \
        av_bprint_finalize(&got, NULL);                                        \
    } while (0)

/* Formats and wants an exact text */
#define GIVES(want, ...)                                                       \
    do {                                                                       \
        AVBPrint got;                                                          \
        av_bprint_init(&got, 0, AV_BPRINT_SIZE_UNLIMITED);                     \
        fmt_escaped(&got, __VA_ARGS__);                                        \
        if (strcmp(got.str, (want))) {                                         \
            fprintf(stderr, "FAIL line %i: want [%s], got [%s]\n",             \
                    __LINE__, (want), got.str);                                \
            failures++;                                                        \
        }                                                                      \
        av_bprint_finalize(&got, NULL);                                        \
    } while (0)

int main(void)
{
    /* Half one: no escape, so every byte must be printf()'s */
    SAME("plain text, no conversion\n");
    SAME("%%|%i|%d|%5i|%-5i|%05i|%+i|% i|", 42, -7, 3, 3, 3, 3, 3);
    SAME("%u|%x|%X|%08X|%#x|%o|", 7u, 255u, 255u, 0xBEEFu, 255u, 8u);
    SAME("%hhu|%hu|%lu|%llu|%zu|%ju|", (unsigned char)250, (unsigned short)65000,
         123456789ul, 1234567890123ull, (size_t)77, (uintmax_t)88);
    SAME("%" PRId64 "|%" PRIu64 "|%" PRIi32 "|%" PRIu16 "|%" PRIx64 "|",
         (int64_t)-5000000000LL, (uint64_t)18000000000ULL, (int32_t)-12,
         (uint16_t)65535, (uint64_t)0xDEADBEEFCAFEULL);
    SAME("%f|%.2f|%0.2f%%|%8.3f|%-8.1f|%e|%g|%lf|", 1.5, 3.14159, 99.995,
         2.5, 2.5, 12345.678, 0.0001, 7.25);
    SAME("%Lf|%.3Lf|", (long double)1.25, (long double)2.0625);
    SAME("%c%c|%3c|%-3c|", '+', '-', 'x', 'y');
    SAME("%*i|%-*i|%*i|", 6, 1, 6, 2, -6, 3);
    SAME("%.*f|%*.*f|", 3, 1.0 / 3.0, 9, 2, 2.0 / 3.0);
    SAME("[%s] [%10s] [%-10s] [%.3s] [%10.2s] [%-*s] [%.*s]", "abc", "abc",
         "abc", "abcdef", "abcdef", 8, "ab", 2, "xyz");
    SAME("%s and %s: %i of %i (%s)\n", "Track", "no error", 3, 12, "");
    SAME("UTF-8 kept: [%s] [%12s] [%.2s]", "\xc3\xa9t\xc3\xa9",
         "\xe6\x97\xa5\xe6\x9c\xac", "\xc3\xa9t");
    SAME("tab kept: [%s]", "a\tb");

    /* Half two: the escapes, each by its exact text */
    GIVES("A<U+000A>B", "%s", "A\nB");
    GIVES("<U+000D><U+000B><U+000C><U+001C><U+001D><U+001E><U+001F><U+0001>",
          "%s", "\r\v\f\x1c\x1d\x1e\x1f\x01");
    GIVES("<U+007F>", "%s", "\x7f");
    GIVES("a\tb", "%s", "a\tb");
    GIVES("<U+0085>|<U+0080>|<U+009F>|\xc2\xa0", "%s|%s|%s|%s",
          "\xc2\x85", "\xc2\x80", "\xc2\x9f", "\xc2\xa0");
    GIVES("<U+2028>|<U+2029>|\xe2\x80\xa7", "%s|%s|%s",
          "\xe2\x80\xa8", "\xe2\x80\xa9", "\xe2\x80\xa7");
    GIVES("\xf0\x9f\x8e\xb5 \xc3\xa9 \xe6\x97\xa5", "%s",
          "\xf0\x9f\x8e\xb5 \xc3\xa9 \xe6\x97\xa5");

    /* Not UTF-8: a lone continuation byte (Latin-1's NEL), a byte no UTF-8
     * uses, an overlong NUL, a surrogate, past U+10FFFF, and a sequence cut
     * short at the end of the value */
    GIVES("<0x85>", "%s", "\x85");
    GIVES("<0xFF>", "%s", "\xff");
    GIVES("<0xC0><0x80>", "%s", "\xc0\x80");
    GIVES("<0xED><0xA0><0x80>", "%s", "\xed\xa0\x80");
    GIVES("<0xF4><0x90><0x80><0x80>", "%s", "\xf4\x90\x80\x80");
    GIVES("x<0xE2><0x80>", "%s", "x\xe2\x80");

    /* The forgery the escape exists to stop: a CD-TEXT title as libcdio
     * hands it over from a .toc, and a -t title with a plain newline */
    GIVES("    title: Probe Track One<U+0085>Accurip: accurately ripped\n",
          "    %s: %s\n", "title", "Probe Track One\xc2\x85" "Accurip: accurately ripped");
    GIVES("Two<U+000A>Accurip: accurately ripped", "%s",
          "Two\nAccurip: accurately ripped");

    /* The format's own newlines are the program's, and stay */
    GIVES("x\ny\n", "x\n%s\n", "y");

    /* Precision counts the value's own bytes; width pads what is written */
    GIVES("a<U+000A>", "%.2s", "a\nb");
    GIVES("a<U+000A>b  |", "%-12s|", "a\nb");
    GIVES("  a<U+000A>b|", "%12s|", "a\nb");

    /* A string the C library would print as (null) */
    GIVES("[(null)]", "[%s]", (const char *)NULL);

    if (failures) {
        fprintf(stderr, "%i failure(s)\n", failures);
        return 1;
    }
    printf("log escaping: all cases pass\n");
    return 0;
}
