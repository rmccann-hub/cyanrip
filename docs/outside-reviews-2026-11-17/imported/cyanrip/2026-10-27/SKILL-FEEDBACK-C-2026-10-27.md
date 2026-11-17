SKILL-FEEDBACK-FOR: rmccann-hub/claude-code-skills

# Feedback on the C modules of `coding`, from an audit on 2026-10-27

From an audit of a C program built with Meson, using the contract and the `c-coding`, `c-build`
and `c-security` modules. The modules were read at `d97d5e1` (`SKILL.md` frontmatter
`reviewed: "2026-10-27"`; the modules' facts are checked 2026-10-27). Line numbers are at that
commit. Each item gives the module, the line that misled, what happened, what's right with its
source, and a suggested fix. Twelve items, the most consequential first. Nothing here names the
audited program, its code or its findings.

## 1. The installed skill had no C modules

- **Module:** `SKILL.md`, the module table, lines 80-82.
- **Skill date:** the installed copy said `reviewed: "2026-10-26"`; the repository's says
  `"2026-10-27"`.
- **What happened:** the request was to load `c-coding`, `c-build` and `c-security`. The
  session's installed `coding` skill had no `references/c-*.md` and no C rows in its module
  table; its description listed no C. The modules existed only in the repository, merged
  2026-10-26T22:02:37-04:00, after the session's copy was synced. The audit could go ahead only
  by cloning the public repository and reading the modules from there.
- **What's right:** a skill named in a request should be the version the session has loaded,
  or the session should be able to tell that its copy is older.
- **Suggested fix:** state the plugin version or the module list in `SKILL.md`'s frontmatter,
  so a session can see its copy lacks a module. Or say, in *When something here is wrong*, what
  to do when a module named in a request isn't installed: fetch the repository's copy and record
  its commit.

## 2. `ckd_*` is prescribed, but the standard to target doesn't have it

- **Module:** `c-security`, line 15 (rule 3) and line 41; `c-coding`, line 14 (rule 1) and
  line 201.
- **Line that misled:** "run C23's `ckd_mul(&total, n, size)` (GCC 14, Clang 18) before
  `malloc(total)`", beside c-coding's "Target C17". c-coding's *Why* even lists "no `nullptr` or
  `ckd_*`" as C17's cost.
- **What happened:** for a C17 project (the modules' own default), the audit had no fix it could
  cite for an unchecked size product. The two modules point in different directions.
- **What's right:** `<stdckdint.h>` is C23 (fact `csec-ckd`). In C17 the equivalents are GCC's
  and Clang's `__builtin_mul_overflow` (GCC manual, *Integer Overflow Builtins*) or a portable
  `n > SIZE_MAX / size` test.
- **Suggested fix:** give the C17 form beside `ckd_mul` in c-security's rule 3 and its Numbers
  row.

## 3. The Numbers row misses `strtol(s, NULL, 10)` and has one severity

- **Module:** `c-security`, line 129 (Audit, *Numbers, sizes*).
- **Line that misled:** "`atoi`, `sscanf("%d")`; an unchecked index or size from input |
  `BLOCKER` if reachable".
- **What happened:** the program parsed option values with `strtoll(s, NULL, 10)`, discarding
  the end pointer. That loses errors just as `atoi` does: an option value of letters became 0
  and silently changed behavior. The row's patterns don't name it, and its only rating,
  `BLOCKER` if reachable, fits an index or size that reaches memory, not a validation defect.
  The audit rated it `GAP` and had to say why.
- **What's right:** the module's own text (line 39) requires `errno = 0`, digits, the
  terminator at `end` and a range check (fact `csec-numbers`).
- **Suggested fix:** add "`strtol` with the end pointer unchecked" to the row. Rate it
  `BLOCKER` where the number indexes or sizes memory, else `GAP`.

## 4. Paths: "reject, don't repair" doesn't fit names a program must make

- **Module:** `c-security`, lines 44-67 (*Paths from outside data*) and line 130.
- **Line that misled:** "Reject, don't repair: the allowlist refuses `/`, `..`, an empty name, a
  leading `-`, spaces and control bytes", and `create_output()`, which also refuses a leading
  `.`.
- **What happened:** the program builds a multi-directory path from a user's template filled
  with metadata fields. It has to produce a name for every record, including
  values that start with a dot or contain spaces. Rejecting would refuse real data, so the
  module's fix couldn't be applied as written, and its single-component model didn't cover a
  template that makes several components.
- **What's right:** for a name that must exist, validate each component after the template is
  filled: map a component that is exactly `.` or `..`, an empty component and control bytes to
  safe text, and keep the allowlist for names where refusal is acceptable.
- **Suggested fix:** add a "names you must produce" case: per-component mapping of `.`, `..`,
  empty and control bytes, applied after any template expansion. Keep "reject" for names a
  caller supplies.

## 5. The Warning gate row can pass a gate that measures the wrong build

- **Module:** `c-build`, line 165 (Audit, *Warning gate*), and lines 77-90.
- **Line that misled:** "None, or flags other than the release's", with a shell script as the
  model.
- **What happened:** the program's gate is a Meson `test()` that re-runs the compiler from a
  `compile_commands.json` at a fixed path (`<source>/build`), not the build under test. The row
  as written passes it, since the gate exists and uses the release's flags in CI. But under any
  other build directory it fails or gates another configuration.
- **What's right:** a gate measures the build it runs in: `meson.project_build_root()`.
- **Suggested fix:** add to the row: "a gate in `meson test` that reads a fixed build path
  rather than `meson.project_build_root()`: `DRIFT`".

## 6. The Standard row doesn't cover an older standard named while newer features are used

- **Module:** `c-coding`, line 188 (Audit, *Standard*), and line 23 (rule 7).
- **Line that misled:** "No `-std` or `c_std`; C23 features in a C17 project", and "let the
  compiler's errors list the work".
- **What happened:** the build named `c99` and used C11's `<stdatomic.h>`. The row's two cases
  didn't cover it, and rule 7's method fails: GCC 13.3 and Clang 18.1 at `-std=c99 -pedantic`
  compiled `atomic_int` and `atomic_store` with no diagnostic (tried in this audit), because
  the header is a system header.
- **What's right:** `<stdatomic.h>` is C11, section 7.17. A compiler doesn't reliably warn about
  a newer standard library header used under an older `-std`.
- **Suggested fix:** generalize the row to "features from a standard newer than the one named"
  (`DRIFT`), and note that library headers need a search (`stdatomic.h`, `threads.h`,
  `stdckdint.h`, `aligned_alloc`), not the compiler.

## 7. Targeted `-Werror=` flags: allowed or not?

- **Module:** `c-build`, line 14 (rule 3), line 164 (Audit, *Shipped flags*), and lines 32-34.
- **Line that misled:** "Ship without `werror`", and a row that names only `werror=true`, beside
  an example that ships `-Werror=format-security`, `-Werror=implicit`,
  `-Werror=incompatible-pointer-types` and `-Werror=int-conversion`.
- **What happened:** the program ships `-Werror=format`, a broad group whose members change
  between compiler versions, so a newer compiler can fail a user's build: the risk rule 3
  exists to avoid. The module doesn't say whether that is acceptable, so the audit could only
  leave it unrated.
- **What's right:** the module's fact `cb-openssf` quotes OpenSSF against `-Werror` "in this
  blanket form when distributing source code"; the module's own example ships only narrow
  `-Werror=` flags, which suggests the line it means but doesn't draw.
- **Suggested fix:** say in rule 3 which `-Werror=` flags are fine to ship (the narrow ones the
  example lists) and that a broad group such as `-Werror=format` is `DRIFT` for shipped
  source.

## 8. Valgrind and TSan are rules, but have no audit row

- **Module:** `c-build`, line 16 (rule 5), lines 110-112, and the Audit table, lines 161-170.
- **Line that misled:** the table, which has a Sanitizer row only.
- **What happened:** the program is threaded and its CI runs ASan and UBSan but neither Valgrind
  nor TSan. The audit had to cite the rule's prose rather than a row.
- **Suggested fix:** add rows: "Valgrind: no setup, or no `--error-exitcode` | `GAP`" and
  "Threads: threaded code with no `-Db_sanitize=thread` job | `GAP`".

## 9. Transport: no advice when a service's HTTPS is uncertain, and no size cap

- **Module:** `c-security`, line 134 (Audit, *Secrets, transport*), and line 110.
- **Line that misled:** "`http://` | `BLOCKER` if reachable".
- **What happened:** two fetched services were on `http://`. For one, whether its files are
  served over HTTPS with a valid certificate couldn't be settled from the session, so the fix
  depends on a fact the module doesn't ask for. Separately, a download with no size limit was
  appended into memory until a timeout, and no row covers that.
- **What's right:** check that the service answers over HTTPS before prescribing it. libcurl
  has `CURLOPT_MAXFILESIZE_LARGE` for a size cap
  (https://curl.se/libcurl/c/CURLOPT_MAXFILESIZE_LARGE.html).
- **Suggested fix:** in the row, "check the host answers HTTPS; if it doesn't, say so in the
  output and rate `GAP`". Add a line on capping a response's size.

## 10. Unprobed: what about one skipped sub-check among several?

- **Module:** `c-coding`, line 194 (Audit, *Unprobed tests*), and `SKILL.md`, lines 100-103.
- **Line that misled:** "Exit 0 when the test couldn't run".
- **What happened:** a test binary ran several checks, printed `UNPROBED` for one of them (the
  one its own comment calls discriminating) and exited 0. The others ran. The row's wording
  ("the test couldn't run") doesn't clearly cover that. The audit rated it `BLOCKER` on the
  ground that the skipped check was the one that fails a revert.
- **Suggested fix:** "Exit 0 when any check the test depends on couldn't run".

## 11. `/dev/full` doesn't reach a program that names its own files

- **Module:** `c-coding`, lines 159-160 (*Tests*).
- **Line that misled:** "Test write errors with Linux's `/dev/full`, which gives `ENOSPC`."
- **What happened:** the program builds its output paths from a folder and a name template, so
  `/dev/full` couldn't be named as an output. A 4 KiB `tmpfs` (which needs mount privilege)
  reproduced the failure. An `LD_PRELOAD` shim would be the unprivileged route.
- **Suggested fix:** add: "where output paths are built by the program, mount a small `tmpfs`
  (`mount -t tmpfs -o size=4k`) or point one output option at it".

## 12. The contract's version question doesn't name `meson.build`

- **Module:** `SKILL.md`, line 89 (*Check before you act*).
- **Line that misled:** "The manifest or a version file (`.python-version`, `.nvmrc`,
  `global.json`, `#Requires`)".
- **What happened:** for C the target standard is `c_std` in `meson.build`'s
  `default_options`; the table names no C source for it. Minor: c-build covers `c_std`.
- **Suggested fix:** add "`meson.build`'s `c_std`" to the list.

## Coverage the C modules don't have

What the audited program needed that no module covers: threads beyond one sentence on TSan
(mutexes, condition-variable loops, atomics); signal handlers and async-signal-safety;
Windows and MinGW (`wmain`, `-municode`, UTF-16 arguments, reserved device names); libcurl
beyond protocols and verification (timeouts, size caps); Meson build-time code
(`custom_target` and `vcs_tag` running `sh` or `python`); tests that read a fixed build path or
write into the source tree; device I/O needing hardware; and library allocators with their own
failure semantics (c-coding's `realloc` fact is about libc only).
