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

#include "cyanrip_main.h"

/* Measures the drive's audio readback cache by timing re-reads, and logs the
 * result. Read-only, runs before ripping, cannot affect the audio.
 *
 * *sectors_out is the measured size, or 0 when nothing was measured -- which
 * covers "no cache", "disc image", and "could not tell", each of which the log
 * line distinguishes in words. Returns 0 unless allocation failed.
 *
 * NOT VERIFIED ON HARDWARE: see the comment block in cache_probe.c. */
int crip_probe_drive_cache(cyanrip_ctx *ctx, int *sectors_out);
