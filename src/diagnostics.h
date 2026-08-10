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

#include <libavutil/attributes.h>

struct cyanrip_ctx;

/* A machine-readable record of what a run said and how it ended.
 *
 * Off unless -j names a path. It is deliberately not an unconditional extra
 * file in the output directory: a consumer that asserts the exact set of files
 * a rip produced would break, and our own cue_only test scenario is such a
 * consumer. Taking a path rather than deriving one from the naming scheme also
 * means it cannot collide with a track and the caller always knows where to
 * look.
 *
 * The point is the runs that produce no logfile at all. Every refusal between
 * argument parsing and cyanrip_log_init() exits with its reason on stdout and
 * nothing on disk, so a consumer that captures artifacts rather than terminals
 * has no record of why a rip did not happen. This file is written for those
 * runs too -- with the fields it cannot know set to null rather than omitted,
 * so "no disc was opened" and "this build does not report that" stay
 * distinguishable. */

/* Path to write to; NULL or unset disables writing. Recording happens
 * regardless and costs a bounded amount of memory, because messages are
 * printed before the command line has been parsed. */
void crip_diag_enable(const char *path);

/* Every cyanrip_log() message, before it is routed anywhere. */
void crip_diag_record(const char *format, va_list args) av_printf_format(1, 0);

/* Copy the structured facts out of ctx while it is still alive. Safe to call
 * more than once; the last call wins. Nothing else in this module dereferences
 * ctx, so the file can still be written after it has been freed. */
void crip_diag_snapshot(struct cyanrip_ctx *ctx);

/* The value main() is about to return. */
void crip_diag_set_exit(int code);

/* Write the file. Registered with atexit() by crip_diag_enable(), so every
 * path out of main() is covered rather than the ones someone remembered.
 * Idempotent. */
void crip_diag_write(void);
