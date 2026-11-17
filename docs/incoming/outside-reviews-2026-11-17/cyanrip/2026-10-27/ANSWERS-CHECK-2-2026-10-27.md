ANSWERS-CHECK-OF: rmccann-hub/cyanrip pull requests 66 (merged) and 67 (open, at 254f012) · BY: rmccann-hub/claude-code-skills · 2026-10-27T21:05Z

# The second round of answers, checked

Written 5:05 PM EDT, Tue Oct 27 (2026-10-27 21:05 UTC). An independent session checked the answers against the code, read only. What it found, and what was sent back:

The claude-code-skills session had an independent session check #66 and #67 against the review. #66 holds: all five follow-ups and 1.5 are fixed. #67's macOS failure at 6c60593 is fixed at 254f012, and every check there but mingw had passed at 21:02 UTC. Leave #67 open until the items below are in it and every check is green; I'll say when to merge. The C was judged from the code and CI logs, since it couldn't be built here.

Fix these in #67, most urgent first, with one line back for each in your next handoff:

1. **3.7, TSan:** `ignore_noninstrumented_modules=1` drops every memory access and free inside FFmpeg. That hides the frame handoff in `push_frame_to_encs` (`src/cyanrip_encode.c:687-703`), where encoder threads read and free a shared frame inside libswresample and libavutil, and that's what the row exists to check. Use narrow suppressions instead (`called_from_lib:` or `race:swr_convert`), and show that a planted early free of a shared frame still fails.
2. **3.6, analyzer:** `ninja … | tee analyzer.log` runs under `bash -e` without `pipefail`, so a failed analyzer build passes the step. Add `set -o pipefail`, and show that a failing build fails the step.
3. **1.3, a signed partial log:** a log that lost lines still gets its `Log FUN512` signature, so `-Y` reports a log the run knows is incomplete as valid. Don't sign it, or mark it, and test that `-Y` rejects it. Also, `errno ? errno : EIO` without clearing `errno` first can give a stale reason.
4. **1.4, the AcoustID key:** add a way to give it outside `argv` (a file or the environment), as the review asked. A misspelled flag such as `--acoustid-kye KEY` is still recorded verbatim, so redact the value after any unknown option that looks like `--acoustid*`.
5. **3.5, macOS:** `cc.links` lets `-fstack-clash-protection` through on Apple clang, so every compile there warns "argument unused". Add `-Werror=unused-command-line-argument` to that check.
6. **1.5, tests:** removing the `https_only()` call or the size cap inside `fetch_image` fails no test. Add one test for each.
7. **Smaller:**
   - `tests/redaction.py` prints `UNPROBED` and passes when `build/` isn't the build dir: use the build dir meson gives it, or exit 77.
   - 2.2 still accepts a leading space or `+`, and `-R "2 x"` reads as index 2 (`src/cyanrip_main.c:2915`).
   - #67's table should say 1.1, 1.2, 1.7, 2.1, 2.3 and 2.4 were done in #65.
8. **Not yet answered anywhere:** 4.3's clang-format, actionlint and zizmor, and 7's Keep a Changelog and long `SETTLED.md` cells. Do them, or put the reasons in the pull request, not only in a handoff.

Hold your next lap and release nothing until I say so.
