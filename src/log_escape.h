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

#include <stdarg.h>
#include <stddef.h>

#include <libavutil/attributes.h>
#include <libavutil/bprint.h>

/* Appends `len` bytes of `s` to `b`, with every character that could end a
 * line, or that a reader cannot see, written as text naming it:
 *
 *   - a control character other than the tab, U+0000 to U+001F and U+007F,
 *     and U+0080 to U+009F, as <U+XXXX>;
 *   - the line and paragraph separators U+2028 and U+2029, as <U+XXXX>;
 *   - a byte that is not part of well-formed UTF-8, as <0xHH>.
 *
 * Everything else, the tab and every other well-formed character, is copied as
 * it is, so a value without these characters is written byte for byte. */
void crip_bprint_escaped(AVBPrint *b, const char *s, size_t len);

/* printf() into `b`, with each %s argument written through
 * crip_bprint_escaped(). The format itself and every other conversion are
 * printf()'s, so a format's own newlines stay newlines and a number reads as
 * it always has; only what an argument string carries is escaped. Precision
 * counts the argument's own bytes, before escaping, and width pads the result,
 * both as printf() would. */
void crip_vbprintf_escaped(AVBPrint *b, const char *format, va_list args)
    av_printf_format(2, 0);
