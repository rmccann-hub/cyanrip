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


/* THE QR CODE HONOURS NO_COLOR AND TERM=dumb (the UX review of 2026-11-17,
 * F13). crip_print_qrcode() draws the MusicBrainz submission URL as a QR code
 * in 256-colour escapes whenever stdout is a terminal, and checked nothing
 * else, so a reader who had asked for no colour, or a terminal that cannot
 * show it, got the escapes. Each case runs it in a child whose stdout is a
 * pseudo-terminal and reads what reached it: the escapes with nothing set and
 * with NO_COLOR empty (no-color.org: "present and not an empty string"),
 * nothing with NO_COLOR=1 or TERM=dumb. A build without libqrencode draws
 * nothing in any case, so it skips. */

#define _XOPEN_SOURCE 700
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

#include "qrcode.h"

#ifdef TEST_HAVE_QRENCODE
/* Only a build with libqrencode draws, and main() asks this only there */
static int drawn(const char *no_color, const char *term)
{
    int master = posix_openpt(O_RDWR | O_NOCTTY);
    if (master < 0 || grantpt(master) || unlockpt(master))
        return -1;
    const char *name = ptsname(master);
    if (!name)
        return -1;

    pid_t pid = fork();
    if (pid < 0)
        return -1;
    if (!pid) {
        int slave = open(name, O_RDWR | O_NOCTTY);
        if (slave < 0 || dup2(slave, STDOUT_FILENO) < 0)
            _exit(2);
        unsetenv("NO_COLOR");
        setenv("TERM", "xterm-256color", 1);
        if (no_color)
            setenv("NO_COLOR", no_color, 1);
        if (term)
            setenv("TERM", term, 1);
        crip_print_qrcode("https://musicbrainz.org/cdtoc/attach?toc=1+1+300+150");
        fflush(stdout);
        _exit(0);
    }

    int status = 0;
    waitpid(pid, &status, 0);
    if (!WIFEXITED(status) || WEXITSTATUS(status))
        return -1;

    char buf[65536];
    size_t got = 0;
    fcntl(master, F_SETFL, O_NONBLOCK);
    for (;;) {
        ssize_t n = read(master, buf + got, sizeof(buf) - 1 - got);
        if (n <= 0)
            break;
        got += n;
    }
    close(master);
    buf[got] = '\0';
    return strstr(buf, "\033[38;5;") != NULL;
}
#endif

int main(void)
{
#ifndef TEST_HAVE_QRENCODE
    printf("built without libqrencode: no QR code to test\n");
    return 77;
#else
    static const struct { const char *no_color, *term; int want; } cases[] = {
        { NULL, NULL,   1 },
        { "",   NULL,   1 },
        { "1",  NULL,   0 },
        { NULL, "dumb", 0 },
    };
    int fails = 0;
    for (size_t i = 0; i < sizeof(cases)/sizeof(cases[0]); i++) {
        int got = drawn(cases[i].no_color, cases[i].term);
        if (got != cases[i].want) {
            printf("FAIL: NO_COLOR=%s TERM=%s: %s, want %s\n",
                   cases[i].no_color ? cases[i].no_color : "(unset)",
                   cases[i].term ? cases[i].term : "xterm-256color",
                   got < 0 ? "the child did not run" : got ? "drawn" : "not drawn",
                   cases[i].want ? "drawn" : "not drawn");
            fails++;
        }
    }
    printf("%d of %zu cases as expected\n",
           (int)(sizeof(cases)/sizeof(cases[0])) - fails, sizeof(cases)/sizeof(cases[0]));
    return fails ? 1 : 0;
#endif
}
