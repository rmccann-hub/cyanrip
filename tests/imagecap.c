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

/* AN IMAGE THAT REPORTS READING ISRC, AS ONE DOES FROM LIBCDIO 2.3.0.
 *
 * libcdio 998d123 ("Image driver supports ISRC", first released in 2.3.0)
 * added CDIO_DRIVE_CAP_READ_ISRC to the capabilities its three image drivers
 * report. cyanrip used that bit to tell a drive from an image, so on 2.3.0
 * and later every image rip without -s stopped at "Offset is unset!", and
 * every track tried a sub-channel read no image driver implements. CI's first
 * macOS run, on Homebrew's libcdio 2.4, is where it showed. The Linux jobs
 * build against 2.1 and could never see it.
 *
 * An LD_PRELOAD shim that reports the bit the way 2.3.0 does, for an image
 * driver only, so the `image_reports_isrc` scenario can hold the fix on 2.1.
 *
 *   CRIP_IMAGE_CAP_OUT  a file to create when the bit is added, so a test can
 *                       prove the shim took effect and the run was not vacuous
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>

#include <cdio/cdio.h>

void cdio_get_drive_cap(const CdIo_t *p_cdio,
                        cdio_drive_read_cap_t  *p_read_cap,
                        cdio_drive_write_cap_t *p_write_cap,
                        cdio_drive_misc_cap_t  *p_misc_cap)
{
    static void (*real)(const CdIo_t *, cdio_drive_read_cap_t *,
                        cdio_drive_write_cap_t *, cdio_drive_misc_cap_t *);
    if (!real)
        real = dlsym(RTLD_NEXT, "cdio_get_drive_cap");
    real(p_cdio, p_read_cap, p_write_cap, p_misc_cap);

    switch (cdio_get_driver_id(p_cdio)) {
    case DRIVER_BINCUE:
    case DRIVER_NRG:
    case DRIVER_CDRDAO:
        break;
    default:
        return;
    }
    if (!p_read_cap)
        return;
    /* CRIP_IMAGE_CAP_ERROR: answer as libcdio does when MODE SENSE fails,
     * every word CDIO_DRIVE_CAP_ERROR and nothing else (libcdio 68ea374,
     * lib/driver/mmc/mmc.c), for the arms of our round 36 lap 12 S11 (c). */
    if (getenv("CRIP_IMAGE_CAP_ERROR")) {
        *p_read_cap = CDIO_DRIVE_CAP_ERROR;
        if (p_write_cap)
            *p_write_cap = CDIO_DRIVE_CAP_ERROR;
        if (p_misc_cap)
            *p_misc_cap = CDIO_DRIVE_CAP_ERROR;
    } else {
        *p_read_cap |= CDIO_DRIVE_CAP_READ_ISRC;
    }

    const char *out = getenv("CRIP_IMAGE_CAP_OUT");
    if (out) {
        int fd = open(out, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd >= 0) {
            if (write(fd, "added\n", 6) < 0) {
                /* the marker is evidence, not a requirement */
            }
            close(fd);
        }
    }
}

/* CRIP_MEDIA_CHANGED: what the media-change query answers on an image, which
 * otherwise never reports a change, so the stop's two arms can be reached:
 * 1 for a change the drive reports, a negative libcdio error for a query
 * that failed (our round 36 lap 12 S11 (d)). */
int cdio_get_media_changed(CdIo_t *p_cdio)
{
    static int (*real)(CdIo_t *);
    const char *v = getenv("CRIP_MEDIA_CHANGED");
    if (v)
        return atoi(v);
    if (!real)
        real = dlsym(RTLD_NEXT, "cdio_get_media_changed");
    return real(p_cdio);
}
