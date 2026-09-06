#include <libavutil/frame.h>

typedef struct SNAME {
    TYPE **queued;
    int num_queued;
    int max_queued;
    FNAME block_flags;
    unsigned int queued_alloc_size;
    pthread_mutex_t lock;
    pthread_cond_t cond_in;
    pthread_cond_t cond_out;
} SNAME;

static void PRIV_RENAME(fifo_destroy)(void *opaque, uint8_t *data)
{
    SNAME *ctx = (SNAME *)data;

    pthread_mutex_lock(&ctx->lock);

    for (int i = 0; i < ctx->num_queued; i++)
        FREE_FN(&ctx->queued[i]);
    av_freep(&ctx->queued);

    pthread_mutex_unlock(&ctx->lock);

    pthread_cond_destroy(&ctx->cond_in);
    pthread_cond_destroy(&ctx->cond_out);
    pthread_mutex_destroy(&ctx->lock);

    av_free(ctx);
}

AVBufferRef *RENAME(fifo_create)(int max_queued, FNAME block_flags)
{
    SNAME *ctx = av_mallocz(sizeof(*ctx));
    if (!ctx)
        return NULL;

    AVBufferRef *ctx_ref = av_buffer_create((uint8_t *)ctx, sizeof(*ctx), PRIV_RENAME(fifo_destroy), NULL, 0);
    if (!ctx_ref) {
        av_free(ctx);
        return NULL;
    }

    pthread_mutex_init(&ctx->lock, NULL);

    pthread_cond_init(&ctx->cond_in, NULL);
    pthread_cond_init(&ctx->cond_out, NULL);

    ctx->block_flags = block_flags;
    ctx->max_queued = max_queued;

    return ctx_ref;
}

int RENAME(fifo_is_full)(AVBufferRef *src)
{
    if (!src)
        return 0;

    SNAME *ctx = (SNAME *)src->data;
    pthread_mutex_lock(&ctx->lock);
    int ret = 0; /* max_queued == -1 -> unlimited */
    if (!ctx->max_queued)
        ret = 1; /* max_queued = 0 -> always full */
    else if (ctx->max_queued > 0)
        ret = ctx->num_queued > (ctx->max_queued + 1);
    pthread_mutex_unlock(&ctx->lock);
    return ret;
}

int RENAME(fifo_get_size)(AVBufferRef *src)
{
    if (!src)
        return 0;

    SNAME *ctx = (SNAME *)src->data;
    pthread_mutex_lock(&ctx->lock);
    int ret = ctx->num_queued;
    pthread_mutex_unlock(&ctx->lock);
    return ret;
}

int RENAME(fifo_get_max_size)(AVBufferRef *src)
{
    if (!src)
        return INT_MAX;

    SNAME *ctx = (SNAME *)src->data;
    pthread_mutex_lock(&ctx->lock);
    int ret = ctx->max_queued == -1 ? INT_MAX : ctx->max_queued;
    pthread_mutex_unlock(&ctx->lock);
    return ret;
}

void RENAME(fifo_set_max_queued)(AVBufferRef *dst, int max_queued)
{
    SNAME *ctx = (SNAME *)dst->data;
    pthread_mutex_lock(&ctx->lock);
    ctx->max_queued = max_queued;
    pthread_mutex_unlock(&ctx->lock);
}

void RENAME(fifo_set_block_flags)(AVBufferRef *dst, FNAME block_flags)
{
    SNAME *ctx = (SNAME *)dst->data;
    pthread_mutex_lock(&ctx->lock);
    ctx->block_flags = block_flags;
    pthread_mutex_unlock(&ctx->lock);
}

int RENAME(fifo_push)(AVBufferRef *dst, TYPE *in)
{
    if (!dst)
        return 0;

    int err = 0;
    TYPE *in_clone = CLONE_FN(in);

    SNAME *ctx = (SNAME *)dst->data;
    pthread_mutex_lock(&ctx->lock);

    if (ctx->max_queued == 0)
        goto unlock;

    /* Block or error, but only for non-NULL pushes.
     *
     * WHILE, NOT IF, AND POSIX REQUIRES IT. pthread_cond_wait may return
     * without the predicate holding -- a spurious wakeup -- and this program
     * makes that concretely reachable rather than theoretical: it installs
     * SIGINT and SIGTERM handlers and its encoder threads sit in these waits,
     * and signal delivery is one of the ways a wait returns early.
     *
     * Here the cost of the single `if` was a bounded queue that was not
     * bounded: one spurious wake and the push proceeded past its own limit.
     * In fifo_pop() below the same shape is worse.
     *
     * The loop re-reads block_flags as well as the count, so a shutdown that
     * clears the flag still lets a waiter leave. It cannot deadlock: the
     * end-of-stream sentinel is a NULL PUSH, which really does increment
     * num_queued, so the pop-side predicate genuinely becomes false. */
    while (in && (ctx->max_queued != -1) &&
           (ctx->num_queued > (ctx->max_queued + 1))) {
        if (!(ctx->block_flags & FRENAME(BLOCK_MAX_OUTPUT))) {
            err = AVERROR(ENOBUFS);
            FREE_FN(&in_clone);
            goto unlock;
        }

        pthread_cond_wait(&ctx->cond_out, &ctx->lock);
    }

    unsigned int oalloc = ctx->queued_alloc_size;
    TYPE **fq = av_fast_realloc(ctx->queued, &ctx->queued_alloc_size,
                                sizeof(TYPE *)*(ctx->num_queued + 1));
    if (!fq) {
        ctx->queued_alloc_size = oalloc;
        err = AVERROR(ENOMEM);
        FREE_FN(&in_clone);
        goto unlock;
    }

    ctx->queued = fq;
    ctx->queued[ctx->num_queued++] = in_clone;

    pthread_cond_signal(&ctx->cond_in);

unlock:
    pthread_mutex_unlock(&ctx->lock);

    return err;
}

TYPE *RENAME(fifo_pop)(AVBufferRef *src)
{
    if (!src)
        return NULL;

    TYPE *out = NULL;
    SNAME *ctx = (SNAME *)src->data;
    pthread_mutex_lock(&ctx->lock);

    /* WHILE, NOT IF -- and this is the site where it matters. With the single
     * `if`, a spurious wakeup fell straight through to `out = ctx->queued[0]`
     * with num_queued still 0: a read of a slot that was never written, and
     * then num_queued decremented to -1. The assert below catches it only in a
     * build that keeps asserts. See the note in fifo_push(). */
    while (!ctx->num_queued) {
        if (!(ctx->block_flags & FRENAME(BLOCK_NO_INPUT)))
            goto unlock;

        pthread_cond_wait(&ctx->cond_in, &ctx->lock);
    }

    out = ctx->queued[0];
    ctx->num_queued--;
    assert(ctx->num_queued >= 0);

    memmove(&ctx->queued[0], &ctx->queued[1], ctx->num_queued*sizeof(TYPE *));

    if (ctx->max_queued > 0)
        pthread_cond_signal(&ctx->cond_out);

unlock:
    pthread_mutex_unlock(&ctx->lock);

    return out;
}

TYPE *RENAME(fifo_peek)(AVBufferRef *src)
{
    if (!src)
        return NULL;

    TYPE *out = NULL;
    SNAME *ctx = (SNAME *)src->data;
    pthread_mutex_lock(&ctx->lock);

    /* Same as fifo_pop(): a spurious wakeup here cloned ctx->queued[0] with
     * nothing queued. */
    while (!ctx->num_queued) {
        if (!(ctx->block_flags & FRENAME(BLOCK_NO_INPUT)))
            goto unlock;

        pthread_cond_wait(&ctx->cond_in, &ctx->lock);
    }

    out = CLONE_FN(ctx->queued[0]);

unlock:
    pthread_mutex_unlock(&ctx->lock);

    return out;
}
