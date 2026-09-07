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

/* A SPURIOUS WAKEUP IS CONSTRUCTIBLE, so it does not have to be waited for.
 *
 * pthread_cond_wait() is permitted by POSIX to return without the predicate
 * holding, and the FIFO's three waits were guarded by a single `if` rather
 * than a `while`. That is not a style point here: with the `if`, fifo_pop()
 * fell through to `out = ctx->queued[0]` with num_queued still 0 -- reading a
 * slot nothing had written -- and then decremented num_queued to -1.
 *
 * Waiting for a real spurious wakeup would give a test that fails once a year
 * on somebody else's machine. But from the WAITER's point of view a spurious
 * wakeup is exactly "the condition variable was signalled and the predicate
 * did not change", and that can be produced deliberately: signal cond_in with
 * the queue still empty. The waiter cannot tell the difference, which is the
 * whole point -- it must not be able to.
 *
 * This includes fifo_frame.h rather than linking it, for the same reason
 * tests/subq.c includes pregap.c: the struct and its condition variables are
 * private to the translation unit, and reaching them is what makes the
 * scenario constructible at all.
 */

#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

/* The .c, not the .h: SNAME (CRFrameFIFO) and its condition
 * variables are defined inside fifo_template.c and are private to
 * the translation unit that includes it. Reaching them is what makes
 * a spurious wakeup constructible, and this is the same move
 * tests/subq.c makes with pregap.c. */
#include "../src/fifo_frame.c"

/* nanosleep, not usleep: the build compiles with -D_XOPEN_SOURCE=700, and
 * POSIX 2008 removed usleep -- so it is not declared and -Werror=implicit-
 * function-declaration turns that into a build failure. Compiling this file
 * with a bare `gcc` outside the project's flags did NOT catch it, which is
 * the reason to build the way the build builds. */
static void nap_ms(long ms)
{
    struct timespec ts = { ms / 1000, (ms % 1000) * 1000000L };
    nanosleep(&ts, NULL);
}

static int failures;

static void check(int cond, const char *what)
{
    printf("%-58s %s\n", what, cond ? "ok" : "FAIL");
    if (!cond)
        failures++;
}

/* The waiter's result, so the main thread can see what it got back. */
struct popper {
    AVBufferRef *fifo;
    AVFrame *got;
    /* ATOMIC, because the popper thread writes it and main reads it in a spin
     * loop with no lock between them. That is a data race even though every
     * run of it happens to work, and ThreadSanitizer says so: it was the ONLY
     * warning this test produced, and it was in the harness rather than in the
     * FIFO under test. A test that races is not a test of anything. */
    atomic_int returned;
};

static void *pop_thread(void *arg)
{
    struct popper *p = arg;
    p->got = cr_frame_fifo_pop(p->fifo);
    atomic_store(&p->returned, 1);
    return NULL;
}

/* Signal the condition variable a blocked popper waits on, with the queue
 * still empty. This is not a trick: from the waiter's side it is exactly what
 * a spurious return looks like, and the waiter must not be able to tell.
 *
 * The lock is held across the signal so this cannot race with the waiter
 * re-acquiring it -- and so the waiter is genuinely inside pthread_cond_wait
 * when the signal lands. cr_frame_fifo_create() returns an AVBufferRef whose
 * data is the CRFrameFIFO, which is how every function in the template
 * reaches it; this is the same access rather than a new one. */
static void signal_in_with_nothing_queued(AVBufferRef *ref)
{
    CRFrameFIFO *ctx = (CRFrameFIFO *)ref->data;
    pthread_mutex_lock(&ctx->lock);
    pthread_cond_signal(&ctx->cond_in);
    pthread_mutex_unlock(&ctx->lock);
}

int main(void)
{
    /* BLOCK_NO_INPUT: a pop on an empty queue waits rather than returning. */
    AVBufferRef *fifo = cr_frame_fifo_create(-1, FRAME_FIFO_BLOCK_NO_INPUT);
    check(!!fifo, "fifo_create returns a fifo");
    if (!fifo)
        return 1;

    struct popper p = { .fifo = fifo, .got = NULL };
    atomic_init(&p.returned, 0);
    pthread_t th;
    check(pthread_create(&th, NULL, pop_thread, &p) == 0,
          "a popper thread starts and blocks on an empty queue");

    /* Let it reach the wait. There is no portable way to observe that it has,
     * so this sleeps generously and then checks it has NOT returned -- which
     * is itself the assertion that it really did block. */
    nap_ms(200);
    check(atomic_load(&p.returned) == 0, "the popper is still blocked before any signal");

    /* THE SPURIOUS WAKEUP. Signal the condition variable the popper waits on,
     * without queueing anything. Indistinguishable, to the waiter, from the
     * spurious return POSIX allows. */
    signal_in_with_nothing_queued(fifo);
    nap_ms(200);

    check(atomic_load(&p.returned) == 0,
          "a signal with nothing queued does NOT wake the popper through");

    /* Now a real push. The popper must come back with the frame, and exactly
     * once -- so this also proves the loop above did not eat the real wakeup. */
    /* A REAL frame, with a buffer. An empty av_frame_alloc() clones to NULL,
     * so the push would queue NULL -- the end-of-stream sentinel -- and the
     * popper would correctly return NULL, which reads exactly like the defect
     * this test is here to catch. Checked, not assumed: that is what the first
     * run of this file did. */
    AVFrame *f = av_frame_alloc();
    check(!!f, "a frame is allocated for the real push");
    if (f) {
        f->format = AV_SAMPLE_FMT_S16;
        f->nb_samples = 64;
        f->sample_rate = 44100;
        av_channel_layout_default(&f->ch_layout, 2);
        check(av_frame_get_buffer(f, 0) == 0, "the frame gets a real buffer");
    }
    check(cr_frame_fifo_push(fifo, f) == 0, "the real push succeeds");

    for (int i = 0; i < 200 && !atomic_load(&p.returned); i++)
        nap_ms(10);
    check(atomic_load(&p.returned) == 1, "the popper returns once something is queued");
    pthread_join(th, NULL);
    check(p.got != NULL, "the popper returns a frame, not NULL");

    check(cr_frame_fifo_get_size(fifo) == 0,
          "the queue is empty again, so num_queued did not go negative");

    av_frame_free(&f);
    av_frame_free(&p.got);
    av_buffer_unref(&fifo);

    printf("\n%s\n", failures ? "FAILURES" : "all checks passed");
    return failures ? 1 : 0;
}
