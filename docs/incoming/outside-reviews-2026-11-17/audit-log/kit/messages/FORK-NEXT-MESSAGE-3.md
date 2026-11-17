The claude-code-skills session had an independent session check #68 at 60825d6. These are done:
- pipefail, proven by reverting it;
- the unsigned partial log;
- the macOS flags;
- the HTTPS and size-cap tests;
- the redaction test's exit 77;
- the number parsing;
- #67's credit line;
- actionlint and zizmor.

Your reasons for clang-format and for the `SETTLED.md` cells hold. The C was judged from the code, since it couldn't be built here.

**Fix these in #68 before it merges, most urgent first:**

1. **A new bug in #68: logging resets `errno`.** `crip_log_put` and `crip_stdout_put` set `errno = 0` on every line, and FFmpeg's and libcdio's log callbacks go through them (`src/cyanrip_log.c:1594`, `src/cyanrip_main.c:2481`). Library code that logs and then reads `errno` now sees 0. If libcdio logs during a failed read, `crip_read_audio_salvaging`'s ENOMEDIUM test (`src/cyanrip_main.c:273,284`) fails, and a missing disc is zero-filled instead of stopping the rip. Save `errno` before the clear and restore it after.
2. **The AcoustID key still leaks:**
   - `--acousticid-key K`, `--acoustd-key K` and `-acoustid-key K` all reach the log. A prefix match on `--acoustid` can't catch misspellings. Also redact the key's value itself wherever it appears in the recorded `argv`.
   - Trim a trailing newline or space from `CYANRIP_ACOUSTID_KEY`.
   - Add the test the pull request says is missing: the variable is read, and its value appears nowhere in the log, the diagnostics or `stdout`.
3. **Unchecked data-track writes:** `src/cyanrip_main.c:1385,1467,1497` use `AVERROR(errno)` with no clear and no EIO fallback. A failed `fwrite` that sets no `errno` gives `ret=0`, and the track counts as successful. This was there before #68, but it's the same class as 1.3.

**Record these in your task list. They don't hold up the merge:**
- **TSan:** `race:^av_buffer_unref$` also hides frees racing against reads of buffers in your own code, such as `cyanrip_encode.c:1149`. Say so in `tests/tsan.supp`'s header, note that ASan is what covers those frees, and plan `__tsan_release`/`__tsan_acquire` annotations around your own `av_frame_free` calls. Make the three planted defects real tests if that's cheap. The guard against the old option checks `ci.yml` only.
- **`tools/redact.py`:** it redacts the word after `--acoustid-key` even in prose, so "via --acoustid-key or CYANRIP_ACOUSTID_KEY" gets mangled.
- **The fallback test:** `fetch_image` has no test for a response with no declared size.
- **Hardening:** under clang, an unused user CFLAGS argument fails all four `cc.links` checks, silently dropping every hardening flag. Print a message when that happens.

When #68 is green with items 1 to 3, tell me, and leave it unmerged. Hold your next lap and release nothing until I say so.
