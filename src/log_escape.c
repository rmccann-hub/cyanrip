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

/* No value written into the log can start a line of its own.
 *
 * THE DEFECT. Every value the log echoes -- a title from -t, CD-TEXT from the
 * disc or its image, MusicBrainz's answer, the drive's own strings, the
 * command line -- went into the log through a bare %s. A CD-TEXT title
 * carrying "\x85Accurip: accurately ripped" put a line reading exactly
 * `Accurip: accurately ripped` into the track block, and Platterpus's parser,
 * which splits the log with Python's str.splitlines()
 * (platterpus@d745464d:src/platterpus/parsers/cyanrip_log.py:1471), read it
 * as one. libcdio converts a cdrdao .toc's CD-TEXT from ISO-8859-1, so the
 * byte 0x85 arrives as U+0085, NEXT LINE, which splitlines() ends a line on;
 * a -t value can carry a plain newline. Found by the claude-code-skills
 * session's review of 2026-10-26, item 3.1.
 *
 * WHAT IS ESCAPED, and why exactly this set. Every character str.splitlines()
 * ends a line on -- \n, \r, \v, \f, \x1c, \x1d, \x1e, U+0085, U+2028 and
 * U+2029 -- and, with them, every other control character but the tab, since a
 * reader cannot see one either. The tab stays: it ends no line in any reader
 * we know of, and the paranoia library's own messages indent with it. A byte
 * that is not well-formed UTF-8 is escaped too, so the log is always valid
 * UTF-8 and no reader's fallback decoding can turn a stray 0x85 into a line
 * break.
 *
 * WHY THE SINK AND NOT EACH CALL SITE. There are some two hundred calls that
 * print a string, and a list of the ones that carry outside text is the kind
 * of list that rots: the next call that echoes a title would be safe only if
 * its author remembered. Here every %s argument is escaped unless the call
 * puts its newline in the format, which is where every one of this program's
 * own newlines already is.
 *
 * WHY <U+XXXX> AND NOT A BACKSLASH. A Windows path is full of backslashes, so
 * `\x0a` could be a directory's name; `<` and `>` cannot appear in a Windows
 * path, and the form names the character in the notation Unicode itself uses. */

#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "log_escape.h"

/* The length of the well-formed UTF-8 sequence at `p`, or 0 when it is not
 * one: the Unicode Standard's Table 3-7, so an overlong form, a surrogate and
 * anything past U+10FFFF are all ill-formed. */
static size_t utf8_seq_len(const unsigned char *p, size_t avail)
{
    const unsigned c = p[0];
    unsigned lo = 0x80, hi = 0xBF;
    size_t n;

    if (c >= 0xC2 && c <= 0xDF) {
        n = 2;
    } else if (c >= 0xE0 && c <= 0xEF) {
        n = 3;
        if (c == 0xE0)
            lo = 0xA0;
        else if (c == 0xED)
            hi = 0x9F;
    } else if (c >= 0xF0 && c <= 0xF4) {
        n = 4;
        if (c == 0xF0)
            lo = 0x90;
        else if (c == 0xF4)
            hi = 0x8F;
    } else {
        return 0;
    }

    if (avail < n || p[1] < lo || p[1] > hi)
        return 0;
    for (size_t k = 2; k < n; k++)
        if (p[k] < 0x80 || p[k] > 0xBF)
            return 0;

    return n;
}

static uint32_t utf8_decode(const unsigned char *p, size_t n)
{
    switch (n) {
    case 2: return ((p[0] & 0x1Fu) << 6) | (p[1] & 0x3Fu);
    case 3: return ((p[0] & 0x0Fu) << 12) | ((p[1] & 0x3Fu) << 6) |
                   (p[2] & 0x3Fu);
    default: return ((p[0] & 0x07u) << 18) | ((p[1] & 0x3Fu) << 12) |
                    ((p[2] & 0x3Fu) << 6) | (p[3] & 0x3Fu);
    }
}

void crip_bprint_escaped(AVBPrint *b, const char *s, size_t len)
{
    const unsigned char *p = (const unsigned char *)s;
    size_t i = 0;

    while (i < len) {
        /* The common case, a run of printable ASCII, is copied in one go */
        size_t run = i;
        while (run < len && ((p[run] >= 0x20 && p[run] < 0x7F) || p[run] == '\t'))
            run++;
        if (run > i) {
            av_bprint_append_data(b, s + i, run - i);
            i = run;
            continue;
        }

        if (p[i] < 0x80) {
            av_bprintf(b, "<U+%04X>", p[i]);
            i++;
            continue;
        }

        const size_t n = utf8_seq_len(p + i, len - i);
        if (!n) {
            av_bprintf(b, "<0x%02X>", p[i]);
            i++;
            continue;
        }

        const uint32_t cp = utf8_decode(p + i, n);
        if (cp <= 0x9F || cp == 0x2028 || cp == 0x2029)
            av_bprintf(b, "<U+%04X>", (unsigned)cp);
        else
            av_bprint_append_data(b, s + i, n);
        i += n;
    }
}

enum crip_len {
    LEN_NONE, LEN_HH, LEN_H, LEN_L, LEN_LL, LEN_J, LEN_Z, LEN_T, LEN_BIG_L,
};

/* Pads `body` to `width` bytes, as printf() pads a string */
static void put_padded(AVBPrint *b, const char *body, size_t len, int width,
                       int left)
{
    const unsigned pad = width > 0 && (size_t)width > len ?
                         (unsigned)((size_t)width - len) : 0;
    if (!left && pad)
        av_bprint_chars(b, ' ', pad);
    av_bprint_append_data(b, body, len);
    if (left && pad)
        av_bprint_chars(b, ' ', pad);
}

void crip_vbprintf_escaped(AVBPrint *b, const char *format, va_list ap)
{
    va_list args;
    va_copy(args, ap);

    const char *p = format;
    while (*p) {
        const char *pct = strchr(p, '%');
        if (!pct) {
            av_bprint_append_data(b, p, strlen(p));
            break;
        }
        if (pct > p)
            av_bprint_append_data(b, p, pct - p);
        p = pct + 1;

        if (*p == '%') {
            av_bprint_chars(b, '%', 1);
            p++;
            continue;
        }

        /* The conversion is rebuilt with any '*' resolved, so printf() itself
         * formats every argument but a string, exactly as before. */
        char spec[48];
        size_t sl = 0;
        int left = 0, width = -1, prec = -1;
        spec[sl++] = '%';

        while (*p && strchr("-+ #0'", *p)) {
            if (*p == '-')
                left = 1;
            if (sl < 8)
                spec[sl++] = *p;
            p++;
        }

        if (*p == '*') {
            width = va_arg(args, int);
            if (width < 0) {
                left = 1;
                width = width == INT_MIN ? INT_MAX : -width;
                if (sl < 9)
                    spec[sl++] = '-';
            }
            p++;
        } else if (*p >= '0' && *p <= '9') {
            width = 0;
            while (*p >= '0' && *p <= '9') {
                if (width < 100000)
                    width = width * 10 + (*p - '0');
                p++;
            }
        }

        if (*p == '.') {
            p++;
            if (*p == '*') {
                prec = va_arg(args, int);
                if (prec < 0)
                    prec = -1;
                p++;
            } else {
                prec = 0;
                while (*p >= '0' && *p <= '9') {
                    if (prec < 100000)
                        prec = prec * 10 + (*p - '0');
                    p++;
                }
            }
        }

        if (width >= 0)
            sl += snprintf(spec + sl, sizeof(spec) - sl, "%i", width);
        if (prec >= 0)
            sl += snprintf(spec + sl, sizeof(spec) - sl, ".%i", prec);

        /* Microsoft's I64, I32 and I are read as ll, nothing and z: the
         * Windows build asks for the C99 forms, but a library's own message
         * may still carry these. */
        enum crip_len len = LEN_NONE;
        const char *len_txt = "";
        if (p[0] == 'h' && p[1] == 'h') { len = LEN_HH; len_txt = "hh"; p += 2; }
        else if (p[0] == 'h')           { len = LEN_H;  len_txt = "h";  p += 1; }
        else if (p[0] == 'l' && p[1] == 'l') { len = LEN_LL; len_txt = "ll"; p += 2; }
        else if (p[0] == 'l')           { len = LEN_L;  len_txt = "l";  p += 1; }
        else if (p[0] == 'j')           { len = LEN_J;  len_txt = "j";  p += 1; }
        else if (p[0] == 'z')           { len = LEN_Z;  len_txt = "z";  p += 1; }
        else if (p[0] == 't')           { len = LEN_T;  len_txt = "t";  p += 1; }
        else if (p[0] == 'L')           { len = LEN_BIG_L; len_txt = "L"; p += 1; }
        else if (p[0] == 'I' && p[1] == '6' && p[2] == '4') { len = LEN_LL; len_txt = "ll"; p += 3; }
        else if (p[0] == 'I' && p[1] == '3' && p[2] == '2') { p += 3; }
        else if (p[0] == 'I')           { len = LEN_Z;  len_txt = "z";  p += 1; }

        const char conv = *p;
        if (!conv)
            break;
        p++;

        sl += snprintf(spec + sl, sizeof(spec) - sl, "%s%c", len_txt, conv);

        switch (conv) {
        case 'd':
        case 'i':
            switch (len) {
            case LEN_L:  av_bprintf(b, spec, va_arg(args, long));      break;
            case LEN_LL: av_bprintf(b, spec, va_arg(args, long long)); break;
            case LEN_J:  av_bprintf(b, spec, va_arg(args, intmax_t));  break;
            case LEN_Z:  av_bprintf(b, spec, va_arg(args, size_t));    break;
            case LEN_T:  av_bprintf(b, spec, va_arg(args, ptrdiff_t)); break;
            default:     av_bprintf(b, spec, va_arg(args, int));       break;
            }
            break;
        case 'o':
        case 'u':
        case 'x':
        case 'X':
            switch (len) {
            case LEN_L:  av_bprintf(b, spec, va_arg(args, unsigned long));      break;
            case LEN_LL: av_bprintf(b, spec, va_arg(args, unsigned long long)); break;
            case LEN_J:  av_bprintf(b, spec, va_arg(args, uintmax_t));          break;
            case LEN_Z:  av_bprintf(b, spec, va_arg(args, size_t));             break;
            case LEN_T:  av_bprintf(b, spec, va_arg(args, ptrdiff_t));          break;
            default:     av_bprintf(b, spec, va_arg(args, unsigned int));       break;
            }
            break;
        case 'f': case 'F':
        case 'e': case 'E':
        case 'g': case 'G':
        case 'a': case 'A':
            if (len == LEN_BIG_L)
                av_bprintf(b, spec, va_arg(args, long double));
            else
                av_bprintf(b, spec, va_arg(args, double));
            break;
        case 'c':
            av_bprintf(b, spec, va_arg(args, int));
            break;
        case 'p':
            av_bprintf(b, spec, va_arg(args, void *));
            break;
        case 'n':
            /* Never written through: nothing here is a count to report */
            (void)va_arg(args, void *);
            break;
        case 's': {
            if (len == LEN_L) {
                (void)va_arg(args, void *);
                put_padded(b, "(wide string)", strlen("(wide string)"), width, left);
                break;
            }
            const char *s = va_arg(args, const char *);
            if (!s)
                s = "(null)";
            size_t n;
            if (prec >= 0) {
                const char *end = memchr(s, '\0', (size_t)prec);
                n = end ? (size_t)(end - s) : (size_t)prec;
            } else {
                n = strlen(s);
            }

            AVBPrint esc;
            av_bprint_init(&esc, 0, AV_BPRINT_SIZE_UNLIMITED);
            crip_bprint_escaped(&esc, s, n);
            put_padded(b, esc.str, esc.len, width, left);
            av_bprint_finalize(&esc, NULL);
            break;
        }
        default:
            /* A conversion this does not know: its argument's type cannot be
             * known either, so nothing after it can be read safely. Say so in
             * the text rather than guess. -Wformat has checked every format in
             * this program, so only a library's message could reach here. */
            av_bprintf(b, "%%%c<unknown conversion; rest of message not "
                       "formatted>%s", conv, p);
            va_end(args);
            return;
        }
    }

    va_end(args);
}
