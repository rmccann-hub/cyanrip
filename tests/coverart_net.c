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
 * and its parts are called directly. Nothing here leaves the machine: every
 * fetch is to the loopback address, a closed port or a server of its own. */

#include "coverart.c"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <pthread.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

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

/* fetch_image() itself limits a DB fetch to HTTPS. Pointed at an http://
 * base it is refused before any connection; without its https_only() call it
 * would try the loopback's closed port and fail there instead. */
static void test_a_db_fetch_is_https_only(void)
{
    CURL *c = curl_easy_init();
    CRIPArt art = { 0 };
    check(c != NULL, "a curl handle");
    if (!c)
        return;
    coverart_db_url = "http://127.0.0.1:9/release";
    last_log[0] = '\0';
    check(fetch_image(NULL, c, &art, "0", "Front", 0, NULL) < 0,
          "a DB fetch from an http:// base fails");
    check(strstr(last_log, "Protocol \"http\"") != NULL,
          "a DB fetch is refused for its scheme, before any connection");
    coverart_db_url = COVERART_DB_URL_BASE;
    crip_free_art(&art);
    curl_easy_cleanup(c);
}

/* A one-connection HTTP server on the loopback, for the cap through
 * fetch_image() itself: it declares a body one byte past the cap and sends a
 * little of it. An image that declares no size is cut off by receive_image(),
 * whose own test is above; sending one past the cap here took more than the
 * test's 30 s under ASan, whose realloc() copies every time. */
typedef struct Server {
    int fd, port;
    pthread_t thread;
} Server;

static void *serve_one(void *opaque)
{
    Server *s = opaque;
    char req[4096], head[160];
    int c = accept(s->fd, NULL, NULL);
    if (c < 0)
        return NULL;
    (void)!recv(c, req, sizeof(req), 0);
    int n = snprintf(head, sizeof(head), "HTTP/1.1 200 OK\r\n"
                     "Content-Type: image/png\r\nContent-Length: %lld\r\n\r\n"
                     "0123456789abcdef", (long long)COVERART_MAX_BYTES + 1);
    (void)!send(c, head, n, 0);
    close(c);
    return NULL;
}

/* inet_pton(), not INADDR_LOOPBACK, which macOS hides under _XOPEN_SOURCE */
static int server_start(Server *s)
{
    struct sockaddr_in a = { .sin_family = AF_INET };
    socklen_t len = sizeof(a);
    s->fd = socket(AF_INET, SOCK_STREAM, 0);
    if (s->fd < 0 || inet_pton(AF_INET, "127.0.0.1", &a.sin_addr) != 1 ||
        bind(s->fd, (struct sockaddr *)&a, sizeof(a)) ||
        listen(s->fd, 1) || getsockname(s->fd, (struct sockaddr *)&a, &len) ||
        pthread_create(&s->thread, NULL, serve_one, s)) {
        if (s->fd >= 0)
            close(s->fd);
        return -1;
    }
    s->port = ntohs(a.sin_port);
    return 0;
}

static void server_stop(Server *s)
{
    pthread_join(s->thread, NULL);
    close(s->fd);
}

/* fetch_image() caps what it takes: an image that declares one byte past the
 * cap is refused by that size, with none of its body taken, and the line
 * names the cap */
static void test_a_fetch_past_the_cap_is_refused(void)
{
    Server s;
    CRIPArt art = { 0 };
    curl_off_t got = -1;
    char url[64];
    CURL *c = curl_easy_init();
    if (!c || server_start(&s)) {
        check(0, "a curl handle and a loopback server");
        if (c)
            curl_easy_cleanup(c);
        return;
    }
    snprintf(url, sizeof(url), "http://127.0.0.1:%i/front.png", s.port);
    last_log[0] = '\0';
    int ret = fetch_image(NULL, c, &art, NULL, "Front", 0, url);
    curl_easy_getinfo(c, CURLINFO_SIZE_DOWNLOAD_T, &got);
    curl_easy_cleanup(c);
    server_stop(&s);
    check(ret < 0, "an image declared past the cap is refused");
    check(strstr(last_log, "the image is larger than 64 MiB") != NULL,
          "the refusal names the cap");
    check(got == 0, "it is refused by its size, with none of its body taken");
    check(!art.data && !art.size, "no image is kept");
    crip_free_art(&art);
}

int main(void)
{
    /* Every fetch here is to the loopback, not through a proxy the
     * environment names, and a server whose client hung up is not killed */
    unsetenv("http_proxy");
    unsetenv("HTTP_PROXY");
    unsetenv("all_proxy");
    unsetenv("ALL_PROXY");
    signal(SIGPIPE, SIG_IGN);

    test_the_db_is_https();
    test_an_image_past_the_cap_is_refused();
    test_https_only_refuses_http();
    test_a_given_url_keeps_its_scheme();
    test_a_db_fetch_is_https_only();
    test_a_fetch_past_the_cap_is_refused();

    if (failures) {
        fprintf(stderr, "%i check(s) failed\n", failures);
        return 1;
    }
    printf("cover art fetch limits: all checks passed\n");
    return 0;
}
