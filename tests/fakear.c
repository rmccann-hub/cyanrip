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

/* AN ACCURATERIP ANSWER WITHOUT THE NETWORK.
 *
 * `-f`'s offset search needs an AccurateRip entry for the disc, and no
 * fixture's disc is in AccurateRip, so the suite had never run the search
 * (the comment above search_for_drive_offset()'s end said so). This shim
 * answers every libcurl transfer itself:
 *
 *   CRIP_FAKEAR_URL   a file the request's URL is appended to, a line each,
 *                     so a test can read the disc IDs cyanrip asked for
 *   CRIP_FAKEAR_BODY  a file served as the body, with Content-Type
 *                     application/octet-stream; without it, or if it cannot
 *                     be opened, the transfer fails as a 404 would
 *
 * Found by the review of 2026-11-16's audit candidates, whose scratch shim
 * this is: the search could not find an offset of 0, and numbered tracks by
 * position.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>

/* curl.h otherwise defines both functions below as type-checking macros */
#define CURL_DISABLE_TYPECHECK
#include <curl/curl.h>

static curl_write_callback write_fn;
static void *write_data;

CURLcode curl_easy_setopt(CURL *c, CURLoption opt, ...)
{
    static CURLcode (*real)(CURL *, CURLoption, ...);
    if (!real)
        real = (CURLcode (*)(CURL *, CURLoption, ...))dlsym(RTLD_NEXT, "curl_easy_setopt");
    va_list ap;
    va_start(ap, opt);
    /* Every option cyanrip sets is a long, a pointer or a curl_off_t, each
     * passed in one register on the platforms the shims are built for */
    void *arg = va_arg(ap, void *);
    va_end(ap);
    if (opt == CURLOPT_WRITEFUNCTION)
        write_fn = (curl_write_callback)arg;
    else if (opt == CURLOPT_WRITEDATA)
        write_data = arg;
    else if (opt == CURLOPT_URL && arg && getenv("CRIP_FAKEAR_URL")) {
        FILE *f = fopen(getenv("CRIP_FAKEAR_URL"), "a");
        if (f) {
            fprintf(f, "%s\n", (const char *)arg);
            fclose(f);
        }
    }
    return real(c, opt, arg);
}

CURLcode curl_easy_perform(CURL *c)
{
    (void)c;
    const char *path = getenv("CRIP_FAKEAR_BODY");
    FILE *f = path ? fopen(path, "rb") : NULL;
    if (!f || !write_fn) {
        if (f)
            fclose(f);
        return CURLE_HTTP_RETURNED_ERROR;
    }
    char buf[65536];
    size_t n = fread(buf, 1, sizeof(buf), f);
    fclose(f);
    if (n && write_fn(buf, 1, n, write_data) != n)
        return CURLE_WRITE_ERROR;
    return CURLE_OK;
}

CURLcode curl_easy_getinfo(CURL *c, CURLINFO info, ...)
{
    static CURLcode (*real)(CURL *, CURLINFO, ...);
    if (!real)
        real = (CURLcode (*)(CURL *, CURLINFO, ...))dlsym(RTLD_NEXT, "curl_easy_getinfo");
    va_list ap;
    va_start(ap, info);
    void *arg = va_arg(ap, void *);
    va_end(ap);
    if (info == CURLINFO_CONTENT_TYPE) {
        *(const char **)arg = "application/octet-stream";
        return CURLE_OK;
    }
    return real(c, info, arg);
}
