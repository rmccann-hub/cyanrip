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

#include <sys/stat.h>

#include <libavutil/avstring.h>
#include <libavutil/bprint.h>

#include "cyanrip_main.h"
#include "cyanrip_log.h"
#include "os_compat.h"

/* Key 1 and 2 must be set */
/* Escape apostrophes the caller left BARE, and only those.
 *
 * THE DEFECT. `-a`/`-t` values reach av_dict_parse_string(), whose tokeniser
 * treats `'` as a QUOTE character: a bare apostrophe opens a run that never
 * closes, so `-t "1=title=Don't Stop:artist=A:isrc=I"` yielded
 * `title: Dont Stop:artist=A:isrc=I` with artist and isrc never set, no
 * diagnostic, and the corrupted value written into the record as though it
 * were what was asked for. Announced as round 15 lap 14 §5 item 3.
 *
 * WHY NOT SIMPLY ESCAPE EVERY APOSTROPHE. Platterpus already escapes: their
 * cyanrip_backend.py:699 backslashes `\`, `=`, `'` and `:`, and every one of
 * their eleven -a/-t sites routes through it (their lap 15 §A2, read from
 * their source and confirmed by measuring `Don\'t Stop` through our own
 * binary). Escaping unconditionally would turn their `\'` into `\\'` and
 * put a literal backslash in the record -- fixing the defect for one consumer
 * by breaking it for the one we have.
 *
 * So this escapes an apostrophe ONLY when it is not already escaped. A
 * backslash consumes the character after it, exactly as the tokeniser will,
 * which leaves every already-correct input byte-identical. */
char *crip_escape_bare_quotes(const char *src)
{
    if (!src)
        return NULL;
    size_t n = strlen(src);
    char *out = av_mallocz(2 * n + 1);   /* every byte could need a backslash */
    if (!out)
        return NULL;
    size_t o = 0;

    for (size_t i = 0; i < n; i++) {
        if (src[i] == '\\' && (i + 1) < n) {
            out[o++] = src[i++];
            out[o++] = src[i];
            continue;
        }
        if (src[i] == '\'')
            out[o++] = '\\';
        out[o++] = src[i];
    }

    return out;
}

char *append_missing_keys(const char *src, const char *key1, const char *key2)
{
    if (!src)
        return NULL;
    /* Copy string with enough space to append extra */
    char *copy = av_mallocz(strlen(src) + strlen(key1) + strlen(key2) + 1);
    if (!copy)
        return NULL;
    memcpy(copy, src, strlen(src));

    int add_key1_offset = -1;
    int add_key2_offset = -1;

    /* Look for keyless entries in the first two, minding "\:" and "\="
     * escapes, which the dictionary parser will consume later */
    int count = 0, has_key = 0, esc = 0;
    int entry_start = 0;
    for (int i = 0; count < 2; i++) {
        char c = src[i];
        if (esc) {
            esc = 0;
        } else if (c == '\\') {
            esc = 1;
        } else if (c == '=') {
            has_key = 1;
        } else if (c == ':' || c == '\0') {
            if (!has_key && i > entry_start) {
                if (count == 0)
                    add_key1_offset = entry_start;
                else
                    add_key2_offset = entry_start;
            }
            count++;
            entry_start = i + 1;
            has_key = 0;
        }
        if (!c)
            break;
    }

    /* Prepend key1 if missing */
    if (add_key1_offset >= 0) {
        memmove(&copy[add_key1_offset + strlen(key1)], &copy[add_key1_offset], strlen(copy) - add_key1_offset);
        memcpy(&copy[add_key1_offset], key1, strlen(key1));
        if (add_key2_offset >= 0)
            add_key2_offset += strlen(key1);
    }

    /* Prepend key2 if missing */
    if (add_key2_offset >= 0) {
        memmove(&copy[add_key2_offset + strlen(key2)], &copy[add_key2_offset], strlen(copy) - add_key2_offset);
        memcpy(&copy[add_key2_offset], key2, strlen(key2));
    }

    return copy;
}

int crip_is_integer(const char *src)
{
    if (!src || !src[0])
        return 0;
    for (int i = 0; i < strlen(src); i++)
        if (!av_isdigit(src[i]))
            return 0;
    return 1;
}

struct CRIPCharReplacement {
    const char from;
    const char to;
    const char to_u[5];
    int is_avail_locally;
} crip_char_replacement[] = {
    { '<', '_', "‹", HAS_CH_LESS },
    { '>', '_', "›", HAS_CH_MORE },
    { ':', '_', "∶", HAS_CH_COLUMN },
    { '|', '_', "│", HAS_CH_OR },
    { '?', '_', "？", HAS_CH_Q },
    { '*', '_', "∗", HAS_CH_ANY },
    { '/', '_', "∕", HAS_CH_FWDSLASH },
    { '\\', '_', "⧹", HAS_CH_BWDSLASH },
    { '"', '\'', "“", HAS_CH_QUOTES },
    { '"', '\'', "”", HAS_CH_QUOTES },
    { 0 },
};

static int crip_bprint_sanitize(cyanrip_ctx *ctx, AVBPrint *buf, const char *str,
                                int sanitize_fwdslash)
{
    int32_t cp, ret, quote_match = 0;
    const char *pos = str, *end = str + strlen(str);

    int os_sanitize = (ctx->settings.sanitize_method == CRIP_SANITIZE_OS_SIMPLE) ||
                      (ctx->settings.sanitize_method == CRIP_SANITIZE_OS_UNICODE);

    while (str < end) {
        const char *cp_start = str;
        ret = av_utf8_decode(&cp, (const uint8_t **)&str, end, AV_UTF8_FLAG_ACCEPT_ALL);
        if (ret < 0) {
            /* SUBSTITUTE, DO NOT TRUNCATE, AND DO NOT LOG. Announced as items
             * 4 and 5 of round 15 lap 14 §5; item 5 cleared by their lap 15
             * §C1 (*"land it whenever it suits you; we are ready"*).
             *
             * The old `return ret` truncated the name at the bad byte, so
             * `START<bad>TAIL` produced a directory `START` and `<bad>TAIL`
             * produced NOTHING. An empty leading component then made a
             * multi-component scheme resolve to an ABSOLUTE path: measured
             * with the consumer's own `-D {album_artist}/{album}`, a whole rip
             * landed in `/Some Album` at exit 0. An explicitly empty value is
             * refused with exit 1, so a guard against an empty component
             * existed and this evaded it.
             *
             * And the log line was worse than it looked. It went through
             * cyanrip_log() BEFORE the header was written, so it became the
             * LOGFILE'S FIRST LINE -- displacing the banner that
             * PROJECT_FORK_ID is read from, while `-Y` still returned 0.
             * Their own dispatcher then read exactly the first non-blank line
             * and sent such a log to the wrong parser: fourteen tracks parsed
             * as zero, no error anywhere (their lap 15 §C1).
             *
             * U+FFFD is what the byte MEANT to a reader and costs neither the
             * rest of the name nor a line of the record. */
            av_bprint_append_data(buf, pos, cp_start - pos);
            av_bprint_append_data(buf, "\xEF\xBF\xBD", 3);
            str = cp_start + 1;
            pos = str;
            continue;
        }

        /* A TAG VALUE'S CONTROL CHARACTERS, U+0001 to U+001F: `_` in the
         * simple modes and the character's Control Picture, U+2401 to
         * U+241F, in the unicode ones, and in the os_ modes only where the
         * system refuses them, which is Windows. The second of round 36 lap
         * 12 S10's rules, which Platterpus's lap 13 S4 accepted: measured at
         * ed37997, a U+0001 and a newline in a value went into a directory's
         * name in all four modes. sanitize_fwdslash is 1 exactly when str is
         * a tag value (P7d), and the scheme's own text stays the caller's.
         * Checked before the table, so a control character never moves the
         * quotes' parity. */
        if (sanitize_fwdslash && cp >= 0x01 && cp <= 0x1F &&
            !(os_sanitize && HAS_CH_CONTROL)) {
            const uint8_t ctl_u[3] = { 0xE2, 0x90, 0x80 + cp };
            if (ctx->settings.sanitize_method == CRIP_SANITIZE_SIMPLE ||
                ctx->settings.sanitize_method == CRIP_SANITIZE_OS_SIMPLE)
                av_bprint_chars(buf, '_', 1);
            else
                av_bprint_append_data(buf, (const char *)ctl_u, sizeof(ctl_u));
            pos = str;
            continue;
        }

        struct CRIPCharReplacement *rep = NULL;
        for (int i = 0; crip_char_replacement[i].from; i++) {
            if (cp == crip_char_replacement[i].from) {
                int is_quote = crip_char_replacement[i].from == '"';
                rep = &crip_char_replacement[i + (is_quote && quote_match)];
                quote_match = (quote_match + 1) & 1;
                break;
            }
        }

        int skip = !rep;
        int skip_sanitation = rep && (os_sanitize && rep->is_avail_locally);
        int passthrough_slash = rep && !skip_sanitation && (rep->from == OS_DIR_CHAR && !sanitize_fwdslash);

        if (skip || skip_sanitation || passthrough_slash) {
            av_bprint_append_data(buf, pos, str - pos);
            pos = str;
            continue;
        } else if (ctx->settings.sanitize_method == CRIP_SANITIZE_SIMPLE ||
                   ctx->settings.sanitize_method == CRIP_SANITIZE_OS_SIMPLE) {
            av_bprint_chars(buf, rep->to, 1);
        } else if (ctx->settings.sanitize_method == CRIP_SANITIZE_UNICODE ||
                   ctx->settings.sanitize_method == CRIP_SANITIZE_OS_UNICODE) {
            av_bprint_append_data(buf, rep->to_u, strlen(rep->to_u));
        }

        pos = str;
    }

    return 0;
}

static char *get_dir_tag_val(cyanrip_ctx *ctx, AVDictionary *meta,
                             const char *ofmt, const char *key)
{
    char *val = NULL;
    if (!strcmp(key, "year")) {
        const char *date = dict_get(meta, "date");
        if (date) {
            char *save_year, *date_dup = av_strdup(date);
            val = av_strdup(av_strtok(date_dup, ":-", &save_year));
            av_free(date_dup);
        }
    } else if (!strcmp(key, "format")) {
        val = av_strdup(ofmt);
    } else if (!strcmp(key, "track")) {
        const char *track = dict_get(meta, "track");
        if (crip_is_integer(track)) {
            int pad = 0, digits = strlen(track);
            if (((digits + pad) < 2) && ctx->nb_tracks >  9) pad++;
            if (((digits + pad) < 3) && ctx->nb_tracks > 99) pad++;
            val = av_mallocz(pad + digits + 1);
            for (int i = 0; i < pad; i++)
                val[i] = '0';
            memcpy(&val[pad], track, digits);
        } else {
            val = av_strdup(track);
        }
    } else {
        val = av_strdup(dict_get(meta, key));
    }

    return val;
}

/* WHERE EACH BYTE OF A RENDERED PATH CAME FROM. Round 36 lap 12 S10's rules,
 * which Platterpus's lap 13 S4 accepted, are for a path component a tag value
 * is part of, and leave one the scheme's own text makes to the caller, as
 * their guard on -D does. So each byte is recorded as 0 for the scheme's own
 * text and what crip_get_path() adds itself, or as the number of the tag
 * value it is part of, from 1 in the order rendered, with CRIP_FROM_NUMBER
 * set for {track}'s. */
#define CRIP_FROM_NUMBER 0x8000

typedef struct CRIPPathRender {
    AVBPrint buf;
    uint16_t *from;
    unsigned int from_size; /* in bytes, as av_fast_realloc() counts */
    unsigned int marked;    /* how many of buf's bytes have an origin */
    int nb_values;
    int failed;
} CRIPPathRender;

/* The bytes appended since the last call came from the tag named tag, or
 * from the scheme's own text when tag is NULL. A scheme of more than 32,766
 * tokens would give the rest one number between them. */
static void crip_render_mark(CRIPPathRender *r, const char *tag)
{
    uint16_t from = 0;
    if (tag) {
        if (r->nb_values < CRIP_FROM_NUMBER - 1)
            r->nb_values++;
        from = r->nb_values | (!strcmp(tag, "track") ? CRIP_FROM_NUMBER : 0);
    }

    if (!av_bprint_is_complete(&r->buf)) {
        r->failed = 1;
        return;
    }
    uint16_t *f = av_fast_realloc(r->from, &r->from_size,
                                  (r->buf.len + 1) * sizeof(*r->from));
    if (!f) {
        r->failed = 1;
        return;
    }
    r->from = f;
    for (; r->marked < r->buf.len; r->marked++)
        r->from[r->marked] = from;
}

static int process_cond(cyanrip_ctx *ctx, CRIPPathRender *r, AVDictionary *meta,
                        const char *ofmt, const char *scheme)
{
    char *scheme_copy = av_strdup(scheme);

    char *pos = scheme_copy;
    while (*pos) {
        /* Literal text outside of {} is emitted as-is, never substituted */
        if (*pos != '{') {
            char *next = strchr(pos, '{');
            char tmpc = next ? *next : 0;
            if (next)
                *next = '\0';
            crip_bprint_sanitize(ctx, &r->buf, pos, 0);
            crip_render_mark(r, NULL);
            if (!next)
                break;
            *next = tmpc;
            pos = next;
            continue;
        }

        char *end = strchr(pos + 1, '}');
        if (!end) {
            cyanrip_log(ctx, 0, "Invalid scheme syntax, unterminated \"{\"!\n");
            goto fail;
        }
        *end = '\0';
        char *tok = pos + 1;
        pos = end + 1;

        if (strchr(tok, '{')) {
            cyanrip_log(ctx, 0, "Invalid scheme syntax, \"{\" inside \"{\", "
                        "tags in conditions are written as |tag|!\n");
            goto fail;
        }

        if (!strncmp(tok, "if", strlen("if")) &&
            (tok[strlen("if")] == ' ' || tok[strlen("if")] == '#')) {
            char *cond = av_strdup(tok);
            char *cond_save, *cond_tok = av_strtok(cond, "#", &cond_save);

            cond_tok = av_strtok(NULL, "#", &cond_save);
            if (!cond_tok) {
                cyanrip_log(ctx, 0, "Invalid scheme syntax, no \"#\"!\n");
                av_free(cond);
                goto fail;
            }

            int val1_origin_is_tag = 1;
            char *val1 = get_dir_tag_val(ctx, meta, ofmt, cond_tok);
            if (!val1) {
                val1 = av_strdup(cond_tok);
                val1_origin_is_tag = 0;
            }

            cond_tok = av_strtok(NULL, "#", &cond_save);
            if (!cond_tok) {
                cyanrip_log(ctx, 0, "Invalid scheme syntax, no terminating \"#\"!\n");
                av_free(cond);
                av_free(val1);
                goto fail;
            }

            int cond_is_eq = 0, cond_is_not_eq = 0, cond_is_more = 0, cond_is_less = 0;
            if (strstr(cond_tok, "==")) {
                cond_is_eq = 1;
            } else if (strstr(cond_tok, "!=")) {
                cond_is_not_eq = 1;
            } else if (strstr(cond_tok, ">")) {
                cond_is_more = 1;
            } else if (strstr(cond_tok, "<")) {
                cond_is_less = 1;
            } else {
                cyanrip_log(ctx, 0, "Invalid condition syntax!\n");
                av_free(cond);
                av_free(val1);
                goto fail;
            }

            cond_tok = av_strtok(NULL, "#", &cond_save);
            if (!cond_tok) {
                cyanrip_log(ctx, 0, "Invalid scheme syntax, no terminating \"#\"!\n");
                av_free(cond);
                av_free(val1);
                goto fail;
            }

            int val2_origin_is_tag = 1;
            char *val2 = get_dir_tag_val(ctx, meta, ofmt, cond_tok);
            if (!val2) {
                val2 = av_strdup(cond_tok);
                val2_origin_is_tag = 0;
            }

            cond_tok = av_strtok(NULL, "#", &cond_save);
            if (!cond_tok) {
                cyanrip_log(ctx, 0, "Invalid scheme syntax, no terminating \"#\"!\n");
                av_free(cond);
                av_free(val1);
                av_free(val2);
                goto fail;
            }

            int cond_true = 0;
            cond_true |= cond_is_eq && !strcmp(val1, val2);
            cond_true |= cond_is_not_eq && strcmp(val1, val2);

            if (cond_is_less || cond_is_more) {
                int val1_is_int = crip_is_integer(val1), val2_is_int = crip_is_integer(val2);
                if (!val1_is_int && (val1_is_int == val2_is_int)) { /* None are int */
                    cond_true = cond_is_less ? (strcmp(val1, val2) < 0) : (cond_is_more ? strcmp(val1, val2) > 0 : 0);
                } else if (val1_is_int && (val1_is_int == val2_is_int)) { /* Both are int */
                    int64_t val1_dec = strtol(val1, NULL, 10);
                    int64_t val2_dec = strtol(val2, NULL, 10);
                    cond_true |= cond_is_less && val1_dec < val2_dec;
                    cond_true |= cond_is_more && val1_dec > val2_dec;
                } else {
                    ptrdiff_t val1_dec = val1_is_int ? strtol(val1, NULL, 10) : (!val1_origin_is_tag ? 0 : (ptrdiff_t)val1);
                    ptrdiff_t val2_dec = val2_is_int ? strtol(val2, NULL, 10) : (!val2_origin_is_tag ? 0 : (ptrdiff_t)val2);
                    cond_true |= cond_is_less && val1_dec < val2_dec;
                    cond_true |= cond_is_more && val1_dec > val2_dec;
                }
            }

            if (cond_true) {
                char *true_save, *true_tok = av_strtok(cond_tok, "|", &true_save);
                while (true_tok) {
                    int origin_is_tag = 1;
                    char *true_val = get_dir_tag_val(ctx, meta, ofmt, true_tok);
                    if (!true_val) {
                        true_val = av_strdup(true_tok);
                        origin_is_tag = 0;
                    }

                    crip_bprint_sanitize(ctx, &r->buf, true_val, origin_is_tag);
                    crip_render_mark(r, origin_is_tag ? true_tok : NULL);
                    av_free(true_val);

                    true_tok = av_strtok(NULL, "|", &true_save);
                }
            }

            av_free(val2);
            av_free(val1);
            av_free(cond);
            continue;
        }

        int origin_is_tag = 1;
        char *val = get_dir_tag_val(ctx, meta, ofmt, tok);
        if (!val) {
            val = av_strdup(tok);
            origin_is_tag = 0;
        }

        crip_bprint_sanitize(ctx, &r->buf, val, origin_is_tag);
        crip_render_mark(r, origin_is_tag ? tok : NULL);
        av_free(val);
    }

    av_free(scheme_copy);
    return 0;

fail:
    av_free(scheme_copy);
    return AVERROR(EINVAL);
}

int crip_check_scheme(cyanrip_ctx *ctx, const char *scheme)
{
    CRIPPathRender r = { 0 };
    av_bprint_init(&r.buf, 0, AV_BPRINT_SIZE_AUTOMATIC);
    int ret = process_cond(ctx, &r, NULL, "", scheme);
    av_bprint_finalize(&r.buf, NULL);
    av_free(r.from);
    return ret;
}

/* Schemes with conditionals easily produce spaces at the edges of path
 * components or before the extension, which no one ever wants. Each byte's
 * origin moves with it. */
static void crip_trim_path_components(char *path, uint16_t *from)
{
    char *dst = path, *src = path;

    while (*src) {
        /* Leading whitespace */
        while (*src == ' ' || *src == '\t')
            src++;

        /* Copy the component, tracking the end of its last non-space run */
        char *end = dst;
        while (*src && *src != OS_DIR_CHAR) {
            from[dst - path] = from[src - path];
            *dst++ = *src++;
            if (dst[-1] != ' ' && dst[-1] != '\t')
                end = dst;
        }
        dst = end;

        if (*src == OS_DIR_CHAR) {
            from[dst - path] = from[src - path];
            *dst++ = OS_DIR_CHAR;
            src++;
        }
    }
    *dst = '\0';

    /* Whitespace before the extension */
    char *dot = strrchr(path, '.');
    if (dot && dot > path) {
        char *ws = dot;
        while (ws > path && (ws[-1] == ' ' || ws[-1] == '\t'))
            ws--;
        if (ws != dot) {
            size_t len = strlen(dot);
            memmove(&from[ws - path], &from[dot - path], len * sizeof(*from));
            memmove(ws, dot, len + 1);
        }
    }
}

/* What a `.` or `..` component's dots become, by mode, as P7b's table gives
 * each character's: the first of the rules below */
static const struct CRIPDotReplacement {
    const char to;
    const char to_u[4];
} crip_dot_replacement = { '_', "․" };

/* The device names Microsoft reserves in every directory, in any case, from
 * "Naming Files, Paths, and Namespaces": the third rule below. A name
 * followed by an extension is the device too, so the name before the first
 * dot is what is compared. */
static const char *const crip_device_names[] = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "COM¹", "COM²", "COM³",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
    "LPT¹", "LPT²", "LPT³",
};

/* One path component a tag value is part of, as the rules see it: its
 * bytes, NUL-terminated, and where each came from */
typedef struct CRIPName {
    char *s;
    uint16_t *from;
    size_t len;
} CRIPName;

/* The most bytes the rules add to a component: the first makes `..` two
 * three-byte dot leaders, and the third adds one `_` to a name it leaves
 * no longer than the device's */
#define CRIP_NAME_GROWTH 4

/* ins in place of the del bytes at pos, each inserted byte from `from` */
static void crip_name_splice(CRIPName *n, size_t pos, size_t del,
                             const char *ins, size_t ins_len, uint16_t from)
{
    memmove(n->s + pos + ins_len, n->s + pos + del, n->len - pos - del + 1);
    memmove(n->from + pos + ins_len, n->from + pos + del,
            (n->len - pos - del) * sizeof(*n->from));
    memcpy(n->s + pos, ins, ins_len);
    for (size_t i = 0; i < ins_len; i++)
        n->from[pos + i] = from;
    n->len = n->len - del + ins_len;
}

/* THE FIRST RULE, in every mode on every system: no component is `.` or
 * `..`. Measured at ed37997 with -D <root>/{album_artist}/{album}, `-a
 * album=..:album_artist=..` wrote the rip two directories above <root>, at
 * exit 0, in all four modes. */
static void crip_name_dots(cyanrip_ctx *ctx, CRIPName *n)
{
    if (strcmp(n->s, ".") && strcmp(n->s, ".."))
        return;

    const int u = ctx->settings.sanitize_method == CRIP_SANITIZE_UNICODE ||
                  ctx->settings.sanitize_method == CRIP_SANITIZE_OS_UNICODE;
    const char *to = u ? crip_dot_replacement.to_u : &crip_dot_replacement.to;
    const size_t to_len = u ? strlen(crip_dot_replacement.to_u) : 1;
    for (size_t i = 0; i < n->len; i += to_len)
        crip_name_splice(n, i, 1, to, to_len, n->from[i]);
}

/* THE THIRD RULE: a component whose name before its first dot is a device
 * name gets `_` after the name, `NUL_` and `CON_.flac`, in the simple and
 * unicode modes everywhere and in the os_ modes where the system reserves
 * them, which is Windows. Measured at ed37997, `album=CON:album_artist=NUL`
 * made `NUL/CON` in all four modes. The second rule, a value's control
 * characters, is crip_bprint_sanitize()'s, since it is a character's. */
static void crip_name_device(cyanrip_ctx *ctx, CRIPName *n)
{
    const int os = ctx->settings.sanitize_method == CRIP_SANITIZE_OS_SIMPLE ||
                   ctx->settings.sanitize_method == CRIP_SANITIZE_OS_UNICODE;
    if (os && HAS_NAME_DEVICES)
        return;

    const size_t stem = strcspn(n->s, ".");
    for (int i = 0; i < FF_ARRAY_ELEMS(crip_device_names); i++) {
        if (strlen(crip_device_names[i]) == stem &&
            !av_strncasecmp(n->s, crip_device_names[i], stem)) {
            crip_name_splice(n, stem, 0, "_", 1, 0);
            return;
        }
    }
}

/* The rules, for each component a tag value is part of. A component only
 * the scheme's own text makes is left as the caller wrote it. Kept, as the
 * lap that gave the rules said: a leading dot, which is a title's own text
 * and which no system refuses, and a name ending in a space or a dot. */
static char *crip_name_rules(cyanrip_ctx *ctx, const char *path,
                             const uint16_t *from)
{
    AVBPrint out;
    av_bprint_init(&out, 0, AV_BPRINT_SIZE_UNLIMITED);

    for (const char *c = path;;) {
        const char *e = strchr(c, OS_DIR_CHAR);
        const size_t len = e ? (size_t)(e - c) : strlen(c);
        const uint16_t *f = &from[c - path];

        int has_value = 0;
        for (size_t i = 0; i < len; i++)
            has_value |= !!f[i];

        if (!has_value) {
            av_bprint_append_data(&out, c, len);
        } else {
            CRIPName n = {
                .s = av_malloc(len + CRIP_NAME_GROWTH + 1),
                .from = av_malloc_array(len + CRIP_NAME_GROWTH, sizeof(*f)),
                .len = len,
            };
            if (!n.s || !n.from) {
                av_free(n.s);
                av_free(n.from);
                av_bprint_finalize(&out, NULL);
                return NULL;
            }
            memcpy(n.s, c, len);
            n.s[len] = '\0';
            memcpy(n.from, f, len * sizeof(*f));

            crip_name_dots(ctx, &n);
            crip_name_device(ctx, &n);

            av_bprint_append_data(&out, n.s, n.len);
            av_free(n.s);
            av_free(n.from);
        }

        if (!e)
            break;
        av_bprint_chars(&out, OS_DIR_CHAR, 1);
        c = e + 1;
    }

    char *ret = NULL;
    if (!av_bprint_is_complete(&out)) {
        av_bprint_finalize(&out, NULL);
        return NULL;
    }
    av_bprint_finalize(&out, &ret);
    return ret;
}

char *crip_get_path(cyanrip_ctx *ctx, enum CRIPPathType type, int create_dirs,
                    const cyanrip_out_fmt *fmt, void *arg)
{
    char *ret = NULL;
    CRIPPathRender r = { 0 };
    /* UNLIMITED, never AUTOMATIC. AUTOMATIC is the buffer inside the AVBPrint
     * itself, 1,003 bytes and a terminator, and av_bprint_finalize() hands
     * back whatever fitted without a word. Upstream renders here with it, so
     * a path past 1,003 bytes was cut there, extension and all: with -D
     * "<root>/{album}" five times over and a 200-byte album, basic.cue's log,
     * cue sheet and both tracks went to one file with no extension, and the
     * rip said `Rip completed:  yes (2 of 2 tracks)` at exit 0 (upstream
     * report 28). A path a buffer could not hold is no path at all. */
    av_bprint_init(&r.buf, 0, AV_BPRINT_SIZE_UNLIMITED);

    /* A drive letter's colon would get sanitized like any other */
    const char *folder = ctx->settings.folder_name_scheme;
    if (av_toupper(folder[0]) >= 'A' && av_toupper(folder[0]) <= 'Z' &&
        folder[1] == ':' && (folder[2] == '/' || folder[2] == '\\')) {
        av_bprint_append_data(&r.buf, folder, 2);
        crip_render_mark(&r, NULL);
        folder += 2;
    }

    if (process_cond(ctx, &r, ctx->meta, fmt->folder_suffix, folder))
        goto end;

    av_bprint_chars(&r.buf, OS_DIR_CHAR, 1);
    crip_render_mark(&r, NULL);

    char *ext = NULL;
    if (type == CRIP_PATH_COVERART) {
        CRIPArt *art = arg;
        crip_bprint_sanitize(ctx, &r.buf, dict_get(art->meta, "title"), 0);
        crip_render_mark(&r, NULL);
        ext = art->extension ? av_strdup(art->extension) : av_strdup("<extension>");
    } else if (type == CRIP_PATH_LOG) {
        if (process_cond(ctx, &r, ctx->meta, fmt->name,
                         ctx->settings.log_name_scheme))
            goto end;
        ext = av_strdup("log");
    } else if (type == CRIP_PATH_CUE) {
        if (process_cond(ctx, &r, ctx->meta, fmt->name,
                         ctx->settings.cue_name_scheme))
            goto end;
        ext = av_strdup("cue");
    } else {
        cyanrip_track *t = arg;
        if (process_cond(ctx, &r, t->meta, fmt->name,
                         ctx->settings.track_name_scheme))
            goto end;
        ext = av_strdup(t->track_is_data ? "bin" : fmt->ext);
    }

    if (ext)
        av_bprintf(&r.buf, ".%s", ext);
    av_free(ext);

end:
    /* What crip_get_path() wrote itself is the scheme's, not a value's */
    crip_render_mark(&r, NULL);
    if (r.failed || !av_bprint_is_complete(&r.buf)) {
        av_bprint_finalize(&r.buf, NULL);
        av_free(r.from);
        return NULL;
    }
    av_bprint_finalize(&r.buf, &ret);
    if (!ret) {
        av_free(r.from);
        return NULL;
    }

    crip_trim_path_components(ret, r.from);

    char *named = crip_name_rules(ctx, ret, r.from);
    av_free(r.from);
    av_free(ret);
    if (!named)
        return NULL;
    ret = named;

    if (create_dirs) {
        /* Create every directory making up the path */
        for (char *p = strchr(ret + 1, OS_DIR_CHAR); p;
             p = strchr(p + 1, OS_DIR_CHAR)) {
            *p = '\0';
            cyanrip_stat_t st_req = { 0 };
            if (cyanrip_stat(ret, &st_req) == -1)
                mkdir(ret, 0700);
            *p = OS_DIR_CHAR;
        }
    }

    return ret;
}
