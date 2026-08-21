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

#include <stdint.h>

#define CRIP_LOG_FUN512_MARKER "Log FUN512: "

/* base64 of 64 bytes, including padding and NUL */
#define CRIP_FUN512_STR_SIZE 89

/* Compute the FUN512 string of a SHA-512 digest. idx is the index of the
 * output format the log belongs to, each simultaneous output is permuted
 * differently. */
void crip_log_fun512(const uint8_t *sha512_digest, int idx,
                     char digest_str[CRIP_FUN512_STR_SIZE]);

enum CRIPLogVerify {
    CRIP_LOG_VALID = 0,
    CRIP_LOG_MISMATCH,
    CRIP_LOG_NO_CHECKSUM,
    CRIP_LOG_TRAILING_DATA,
    CRIP_LOG_IO_ERROR,
};

/* The process exit code -Y reports each verdict as.
 *
 * Platterpus standing status 2026-08-21, ask 2: "absent" and "mismatched" are
 * different findings and only the second is a tamper claim. A log with no
 * footer is a rip that was killed mid-write -- which this program produced on
 * every SIGTERM until the same round fixed it -- and a log whose footer does
 * not match has been modified. Both exited 1, so the only way to tell them
 * apart was to parse the message, which we asked them NOT to build on (round 7
 * lap 12 J4). A code the caller can switch on is what closes that.
 *
 * These numbers are wire format from the moment they ship. They are declared
 * here, next to the verdicts, so the two cannot drift; and the mapping is
 * EXPLICIT rather than `return verdict`, so the enum stays free to gain a
 * member or change order without silently renumbering a published contract.
 *
 * 1 IS DELIBERATELY NOT USED. It is what cyanrip exits with for everything
 * else, including a rejected command line, so a caller receiving 1 knows only
 * that something went wrong before a verdict was reached -- which is a
 * different thing from every verdict here, and it is the reading a consumer
 * gets for free by not overloading it. That is also why MISMATCH did not keep
 * 1: the historically alarming code becoming one specific verdict among five
 * is what makes the other four legible. */
enum CRIPLogVerifyExit {
    CRIP_LOG_EXIT_VALID         = 0, /* footer present and matching */
    CRIP_LOG_EXIT_MISMATCH      = 2, /* footer present, does not match: modified */
    CRIP_LOG_EXIT_NO_CHECKSUM   = 3, /* no footer: incomplete, NOT a tamper claim */
    CRIP_LOG_EXIT_TRAILING_DATA = 4, /* footer present, content after it: modified */
    CRIP_LOG_EXIT_IO_ERROR      = 5, /* unreadable: no verdict was reached */
};

/* Check a written log against its FUN512 checksum line */
enum CRIPLogVerify cyanrip_verify_log(const char *path);
