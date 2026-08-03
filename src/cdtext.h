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

/* Reads the disc's CD-TEXT, if it carries any, into ctx->cdtext (disc level)
 * and each track's t->cdtext. Both are kept verbatim and separate from the
 * metadata dictionaries: CD-TEXT is a measurement of what is on the disc, and
 * stays reportable even when MusicBrainz or a -a/-t value later supplies a
 * better tag. Gap-filling into the metadata is done separately by
 * crip_cdtext_to_meta().
 *
 * Sets ctx->cdtext_status, which distinguishes "the disc carries none" from
 * "we could not find out" -- never returns one for the other.
 *
 * Returns 0 always: a disc without CD-TEXT is not an error, and neither is a
 * drive that cannot report it. */
int crip_fill_cdtext(cyanrip_ctx *ctx);

/* Copies CD-TEXT into the metadata dictionaries, but only where nothing has
 * claimed the key yet. Call after the built-in defaults are in place and
 * before the MusicBrainz fill, so precedence ends up
 * user -a/-t > MusicBrainz > CD-TEXT > defaults. */
void crip_cdtext_to_meta(cyanrip_ctx *ctx);
