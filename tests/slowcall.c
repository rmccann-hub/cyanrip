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

/* ONE LIBCDIO CALL THAT TAKES LONGER THAN THE WATCHDOG WAITS.
 *
 * On 2026-11-11 a lone `cyanrip -I` printed nothing after `Opening drive...`
 * for 300 s on the BDR-209D (our round 39 lap 3 S13): past the named
 * drive open, in a command no wait named. The commands between the open and
 * the first pregap search now name themselves to the stall watchdog, and an
 * image reaches them too, so this shim makes one of them slow and a scenario
 * reads the watchdog's line for it.
 *
 *   CRIP_SLOW_CALL  cdio_get_last_session, or cdio_get_track_lsn for its
 *                   lead-out question only
 *   CRIP_SLOW_SECS  how long the first such call after the drive open sleeps
 *                   before it answers. Calls inside cdio_cddap_open() are
 *                   left alone: the open reads the TOC and asks the last
 *                   session itself, under its own named wait.
 *   CRIP_SLOW_OUT   a file created when it sleeps, so a test can prove the
 *                   shim took effect and the run was not vacuous
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <cdio/cdio.h>

#include <cdio/paranoia/cdda.h>

static int slept, opened;

int cdio_cddap_open(cdrom_drive_t *d)
{
    static int (*real)(cdrom_drive_t *);
    if (!real)
        real = (int (*)(cdrom_drive_t *))dlsym(RTLD_NEXT, "cdio_cddap_open");
    const int ret = real(d);
    opened = 1;
    return ret;
}

static void maybe_sleep(const char *name)
{
    const char *want = getenv("CRIP_SLOW_CALL");
    const char *secs = getenv("CRIP_SLOW_SECS");
    if (slept || !opened || !want || strcmp(want, name) || !secs)
        return;
    slept = 1;
    const char *out = getenv("CRIP_SLOW_OUT");
    if (out) {
        int fd = open(out, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd >= 0)
            close(fd);
    }
    sleep((unsigned)atoi(secs));
}

driver_return_code_t cdio_get_last_session(CdIo_t *p_cdio, lsn_t *i_last_session)
{
    static driver_return_code_t (*real)(CdIo_t *, lsn_t *);
    if (!real)
        real = (driver_return_code_t (*)(CdIo_t *, lsn_t *))dlsym(RTLD_NEXT, "cdio_get_last_session");
    maybe_sleep("cdio_get_last_session");
    return real(p_cdio, i_last_session);
}

lsn_t cdio_get_track_lsn(const CdIo_t *p_cdio, track_t i_track)
{
    static lsn_t (*real)(const CdIo_t *, track_t);
    if (!real)
        real = (lsn_t (*)(const CdIo_t *, track_t))dlsym(RTLD_NEXT, "cdio_get_track_lsn");
    if (i_track == CDIO_CDROM_LEADOUT_TRACK)
        maybe_sleep("cdio_get_track_lsn");
    return real(p_cdio, i_track);
}
