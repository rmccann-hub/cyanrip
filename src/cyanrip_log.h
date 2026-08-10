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

#include "cyanrip_main.h"

int cyanrip_log_init(cyanrip_ctx *ctx);
void cyanrip_log_end(cyanrip_ctx *ctx);

void cyanrip_log_start_report(cyanrip_ctx *ctx);
void cyanrip_log_finish_report(cyanrip_ctx *ctx);
void cyanrip_log_track_end(cyanrip_ctx *ctx, cyanrip_track *t);

void cyanrip_set_av_log_capture(cyanrip_ctx *ctx, int enable,
                                int max_av_lvl);

/* Annotated so the compiler checks these format strings. Nothing did until
 * now: -Wformat only fires on functions it knows are printf-like, so not one
 * format string in this program had ever been checked -- in a program whose
 * output is an archival record. Six real mismatches were sitting in the tree
 * when the annotation was added, and a -t argument that read adjacent process
 * memory into a logfile had already shipped once. src/meson.build makes the
 * diagnostic an error rather than a warning, so the check cannot lapse. */
void cyanrip_log(cyanrip_ctx *ctx, int verbose, const char *format, ...)
    av_printf_format(3, 4);

/* Same, taking an assembled va_list, so another logging front end can forward
 * into this one instead of printing on its own. genopt's does exactly that:
 * left to itself it vprintf()s, which is how every argument-parsing error --
 * including the "Unable to parse command line argument: -V" that once read to
 * a consumer as "cyanrip is not installed" -- reached the terminal and nothing
 * else. */
void cyanrip_vlog(cyanrip_ctx *ctx, int verbose, const char *format,
                  va_list args) av_printf_format(3, 0);
