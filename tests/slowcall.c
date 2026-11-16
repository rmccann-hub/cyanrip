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
 *   CRIP_SLOW_CALL  cdio_get_last_session, cdio_get_track_lsn for its
 *                   lead-out question only, cdio_paranoia_init, or
 *                   cdio_cddap_track_audiop
 *   CRIP_SLOW_SECS  how long the first such call after the drive open sleeps
 *                   before it answers. Calls inside cdio_cddap_open() are
 *                   left alone: the open reads the TOC and asks the last
 *                   session itself, under its own named wait.
 *   CRIP_SLOW_OUT   a file created when it sleeps, so a test can prove the
 *                   shim took effect and the run was not vacuous
 *
 * Only a call made from cyanrip's own executable sleeps. Whether a library's
 * call to its own export passes through this shim depends on how it was
 * linked. Fedora 45's libcdio 2.3.0 calls cdio_get_track_lsn through its PLT
 * (an R_X86_64_JUMP_SLOT relocation), so the lead-out question that
 * cdio_paranoia_init() asks inside libcdio can reach the shim there; Ubuntu's
 * libcdio 2.1.0 has no such relocation and binds the call within itself. The
 * first run of a Fedora CI job, on 2026-11-16, printed no line for the
 * lead-out sleep, which fits that call taking it. The scenario asks about
 * cyanrip's own calls, so those are the ones counted, however a library was
 * linked.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <link.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <cdio/cdio.h>

#include <cdio/paranoia/cdda.h>
#include <cdio/paranoia/paranoia.h>

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

/* Whether the instruction at caller belongs to the main program, compared by
 * link map with the one dlopen(NULL) names. */
static int from_main_program(const void *caller)
{
    static struct link_map *main_map;
    if (!main_map) {
        void *self = dlopen(NULL, RTLD_NOW);
        if (!self || dlinfo(self, RTLD_DI_LINKMAP, &main_map) || !main_map)
            return 0;
    }
    Dl_info info;
    struct link_map *map = NULL;
    return dladdr1(caller, &info, (void **)&map, RTLD_DL_LINKMAP) &&
           map == main_map;
}

static void maybe_sleep(const char *name, const void *caller)
{
    const char *want = getenv("CRIP_SLOW_CALL");
    const char *secs = getenv("CRIP_SLOW_SECS");
    if (slept || !opened || !want || strcmp(want, name) || !secs ||
        !from_main_program(caller))
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
    maybe_sleep("cdio_get_last_session", __builtin_return_address(0));
    return real(p_cdio, i_last_session);
}

lsn_t cdio_get_track_lsn(const CdIo_t *p_cdio, track_t i_track)
{
    static lsn_t (*real)(const CdIo_t *, track_t);
    if (!real)
        real = (lsn_t (*)(const CdIo_t *, track_t))dlsym(RTLD_NEXT, "cdio_get_track_lsn");
    if (i_track == CDIO_CDROM_LEADOUT_TRACK)
        maybe_sleep("cdio_get_track_lsn", __builtin_return_address(0));
    return real(p_cdio, i_track);
}

cdrom_paranoia_t *cdio_paranoia_init(cdrom_drive_t *d)
{
    static cdrom_paranoia_t *(*real)(cdrom_drive_t *);
    if (!real)
        real = (cdrom_paranoia_t *(*)(cdrom_drive_t *))dlsym(RTLD_NEXT, "cdio_paranoia_init");
    maybe_sleep("cdio_paranoia_init", __builtin_return_address(0));
    return real(d);
}

int cdio_cddap_track_audiop(cdrom_drive_t *d, track_t i_track)
{
    static int (*real)(cdrom_drive_t *, track_t);
    if (!real)
        real = (int (*)(cdrom_drive_t *, track_t))dlsym(RTLD_NEXT, "cdio_cddap_track_audiop");
    maybe_sleep("cdio_cddap_track_audiop", __builtin_return_address(0));
    return real(d, i_track);
}
