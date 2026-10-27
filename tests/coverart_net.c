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

/* What a cover art fetch accepts: review C items 1.5 and 2.3. No scenario
 * reaches the Cover Art DB, which needs the network, so the file is included
 * and its parts are called directly. Nothing here leaves the machine: the one
 * fetch made is to a closed port on the loopback address. */

#include "coverart.c"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

static int failures;
static char last_log[1024];

static void check(int cond, const char *what)
{
    if (!cond) {
        fprintf(stderr, "FAIL: %s\n", what);
        failures++;
    }
}

/* coverart.c calls these; the real ones need a whole cyanrip_ctx. The log
 * keeps its last line, so a test can read what a fetch said. */
void cyanrip_log(cyanrip_ctx *ctx, int verbose, const char *format, ...)
{
    va_list args;
    (void)ctx; (void)verbose;
    va_start(args, format);
    vsnprintf(last_log, sizeof(last_log), format, args);
    va_end(args);
}

char *crip_get_path(cyanrip_ctx *ctx, enum CRIPPathType type, int create_dirs,
                    const cyanrip_out_fmt *fmt, void *arg)
{
    (void)ctx; (void)type; (void)create_dirs; (void)fmt; (void)arg;
    return NULL;
}

char *cr_ffmpeg_file_path(const char *path)
{
    return av_strdup(path);
}

static void test_the_db_is_https(void)
{
    check(!strncmp(COVERART_DB_URL_BASE, "https://", 8),
          "the Cover Art DB is fetched over HTTPS");
}

static void test_an_image_past_the_cap_is_refused(void)
{
    CRIPArt art = { 0 };
    ImageRecv recv = { .art = &art };

    check(receive_image("abcd", 1, 4, &recv) == 4 && art.size == 4 &&
          !recv.too_big, "an image under the cap is taken");

    /* The check comes before the allocation, so the size can be set past
     * what was received without allocating the cap's worth */
    art.size = COVERART_MAX_BYTES - 4;
    check(receive_image("efgh", 1, 4, &recv) == 4 && !recv.too_big,
          "an image that reaches the cap exactly is taken");
    check(receive_image("i", 1, 1, &recv) == 0 && recv.too_big,
          "one byte past the cap is refused, and the refusal says why");
    check(art.size == COVERART_MAX_BYTES, "a refused write adds nothing");

    art.size = 0;
    av_freep(&art.data);
}

static void test_https_only_refuses_http(void)
{
    CURL *c = curl_easy_init();
    check(c != NULL, "a curl handle");
    if (!c)
        return;
    https_only(c);
    curl_easy_setopt(c, CURLOPT_URL, "http://127.0.0.1:9/");
    curl_easy_setopt(c, CURLOPT_NOPROXY, "*");
    check(curl_easy_perform(c) == CURLE_UNSUPPORTED_PROTOCOL,
          "a handle limited to HTTPS refuses http:// before connecting");
    curl_easy_cleanup(c);
}

/* One handle serves the DB and the URLs -C gives. The DB's limit must not
 * carry over: a URL its caller gave as http:// is tried, and fails here only
 * because nothing listens on the port. */
static void test_a_given_url_keeps_its_scheme(void)
{
    CURL *c = curl_easy_init();
    CRIPArt art = { 0 };
    check(c != NULL, "a curl handle");
    if (!c)
        return;
    https_only(c);
    last_log[0] = '\0';
    check(fetch_image(NULL, c, &art, NULL, "Front", 0,
                      "http://127.0.0.1:9/front.png") < 0,
          "a fetch from a closed port fails");
    check(last_log[0] && !strstr(last_log, "Protocol \"http\""),
          "the URL -C gave was tried over http, not refused for its scheme");
    crip_free_art(&art);
    curl_easy_cleanup(c);
}

int main(void)
{
    test_the_db_is_https();
    test_an_image_past_the_cap_is_refused();
    test_https_only_refuses_http();
    test_a_given_url_keeps_its_scheme();

    if (failures) {
        fprintf(stderr, "%i check(s) failed\n", failures);
        return 1;
    }
    printf("cover art fetch limits: all checks passed\n");
    return 0;
}
