SKILL-FEEDBACK-FOR: rmccann-hub/claude-code-skills

# Skill feedback from an audit run, 2026-10-27

**Where these come from:** a read-only audit of a public C program built with meson. It's a fork
of an open-source project, with about 60 Python tool and test scripts and a few shell scripts,
run in a Claude Code cloud session.

**Skills loaded:** `project-bootstrap-and-audit` (standard 0.48.2), `coding` (reviewed
2026-10-26), `git-workflows` (reviewed 2026-10-16) and `house-style` (reviewed 2026-10-16). Every
skill expected loaded. The owner's request, word for word: *"Audit this repository: its setup,
CI, dependencies and context files against the PROJECT-BOOTSTRAP-AND-AUDIT standard, and its
code, Git workflows and prose with the skills that cover them. This is a review only."*

Each problem below is written as an issue to file, most consequential first.

## 1. `coding` has no C module, though the standard was built partly from a C fork

- **Skill and module:** `coding`, `SKILL.md`, the Modules table (`SKILL.md:54-70`); its
  frontmatter description lists Python, TypeScript and JavaScript, HTML and CSS, C#, PowerShell
  and Bash.
- **Version:** reviewed 2026-10-26.
- **What misled:** nothing misled. The gap is that the audited code was mostly C. The standard
  names "C with meson" among shapes not yet exercised (`PROJECT-BOOTSTRAP-AND-AUDIT-v0.48.2.md:181`)
  and says it was built from "Python web applications and a C fork".
- **What happened:** the review fell back on the 10-point contract alone. With no module, there
  were no audit rows for the defects that mattered most in the run:
  - shallow-copying a library's struct that owns heap memory, which gave a double free;
  - a fixed array whose bound is checked in one place and not in another;
  - `..` and empty path components built from outside data;
  - `fwrite`, `fclose` and `ferror` left unchecked;
  - a format-specific escape for a file another program parses.
- **What's right:** CERT C (SEI CERT C Coding Standard) covers each of these, for example
  FIO04-C (detect and handle I/O errors) and MEM30-C/MEM31-C (no use or free after free).
  Compiler hardening and sanitizers are the usual gate: `-fsanitize=address,undefined`, and
  meson's `b_sanitize` option.
- **Suggested fix:** a `c-coding` module (rules, mistakes, an Audit table rated in the
  standard's words, facts with dates) and a `c-security` module (bounds, ownership of library
  structs, path components, output escaping per format, checked writes). Add a row to the
  Modules table and the frontmatter description.

## 2. No path for an unattended audit that was given no answers

- **Skill and module:** `project-bootstrap-and-audit`, `SKILL.md:19` ("Follow it as written,
  including both waits"), and the standard's Phase 3 at line 1323 ("An unattended run meets
  this wait with the answers it was given").
- **Version:** standard 0.48.2.
- **What misled:** the two lines together. The request asked for a full audit, said to stop
  where the standard waits and list the questions, and gave no answers. Neither line covers
  that.
- **What happened:** the run drafted every Phase 3 answer, rated on the lowest tier the
  evidence supports, marked the tier-dependent statuses, and listed the questions. That is a
  judgment call two runs could make differently, so reports may not diff.
- **What's right:** the standard's own rule that "a question the given answers leave out is
  `unanswered`" (line 1331) points the same way. It just isn't connected to a run with no
  answers at all.
- **Suggested fix:** one paragraph in Phase 3. Where the prompt says not to wait and gives no
  answers, record each as `unanswered`, rate on the draft tier with `tier_basis: draft`, and
  mark `UNVERIFIABLE-HERE` every status that would change at another tier.

## 3. Platform settings are read with `gh api`, which a cloud session may not have

- **Skill and module:** `project-bootstrap-and-audit`, standard line 1137 ("On GitHub that is
  `gh api repos/<owner>/<repo>` and its `rulesets`, …"). Also `git-workflows`, `SKILL.md`,
  *Check before you act*, which names `gh api` in both of its first two rows.
- **Version:** standard 0.48.2; git-workflows reviewed 2026-10-16.
- **What misled:** both assume the `gh` CLI. This session had no `gh`, and its GitHub MCP tools
  have no endpoint for rulesets or repository settings.
- **What happened:** unauthenticated `curl https://api.github.com/repos/<owner>/<repo>`, plus
  `/rulesets`, `/rulesets/<id>`, `/rules/branches/<branch>`,
  `/private-vulnerability-reporting` and `/immutable-releases`, all answered for a public
  repository. That included `security_and_analysis`, and `allow_merge_commit`,
  `allow_squash_merge`, `allow_rebase_merge` and `delete_branch_on_merge`. Neither skill says
  this works.
- **What's right:** the GitHub REST API documents these endpoints as readable for public
  repositories. It is worth checking per endpoint, since some fields need admin access.
- **Suggested fix:** next to each `gh api` command, give the `curl` form for public
  repositories, and say which fields need authentication.

## 4. `skillOverrides` keys: bare name or the synced skill's prefixed name?

- **Skill and module:** `project-bootstrap-and-audit`, `assets/skill-overrides.json:3` (keys
  such as `"algorithmic-art"`), and the standard's fact at line 777.
- **Version:** standard 0.48.2.
- **What misled:** this session listed the account's synced skills as
  `anthropic-skills:algorithmic-art`, `anthropic-skills:slack-gif-creator` and so on, while the
  exclusion list uses bare names. The fact at line 777 says `"off"` hid synced skills on
  2026-10-15, but not which key form it used.
- **What happened:** the run couldn't say whether proposing the list as it stands would hide
  anything.
- **What's right:** unverified. It needs one session that sets a bare key and one that sets a
  prefixed key, then reads the skill listing.
- **Suggested fix:** record the key form that was observed to work in the line 777 fact, and use
  that form in `skill-overrides.json`.

## 5. Commit subjects: `house-style` sets a rule, then hands the subject to `git-workflows`

- **Skill and module:** `house-style`, `SKILL.md:38` (rule 11, "Commit subjects read 'area:
  summary'"), against `SKILL.md:70` ("Commit subjects, branch names, pull requests and the
  changelog's structure: use git-workflows"). `git-workflows` `commits-and-pull-requests` allows
  Conventional Commits or "area: summary".
- **Version:** house-style reviewed 2026-10-16.
- **What misled:** three statements disagree about who decides the grammar and what it is.
- **What happened:** the audited repository records its own grammar ("plain and imperative").
  The run had to work out that the repository's recorded convention wins, as the standard's
  precedence rule says. It couldn't tell which skill to cite.
- **Suggested fix:** in `house-style`, make rule 11 read "Commit subjects follow the grammar the
  repository records (git-workflows)", and drop "area: summary" from the house rule.

## 6. `house-style`'s upstream carve-out is silent on fork-written text inside an upstream file

- **Skill and module:** `house-style`, `SKILL.md:46-48` ("Files a fork shares with its upstream
  project keep upstream's format"), against rule 10 (`SKILL.md:36-37`, the README's sections).
- **Version:** reviewed 2026-10-16.
- **What misled:** the README is upstream's file with about 150 lines the fork added. Rule 10
  wants seven sections, and the carve-out says not to reformat. Neither says what happens to a
  fork's own block inside a shared file. Nor does either cover a changelog upstream started that
  the fork now writes alone.
- **Suggested fix:** one sentence. The fork's own blocks inside a shared file follow the style,
  and required sections go inside the fork's block, not over upstream's structure.

## 7. `house-style`'s wrap check doesn't do what its row says, and the skill breaks the rule

- **Skill and module:** `house-style`, `references/writing-style.md:167`: "`awk 'length > 100'
  FILE`, leaving out tables, URLs and code".
- **Version:** reviewed 2026-10-16.
- **What misled:** the command leaves out nothing. In the run it flagged table rows, fenced code
  and machine-read wire lines that can't wrap.
- **What happened:** a subagent wrote its own fence-aware script to get a usable count.
- **The skill breaks its own rule:** `references/prose-check.md:119` is 140 characters long.
- **Suggested fix:** an awk that skips fenced blocks and lines starting with `|`. Add a line
  saying lines a program parses are exempt. Then fix `prose-check.md:119`.

## 8. `python-coding`'s encoding row misses `subprocess` text mode, and Ruff misses most sites

- **Skill and module:** `coding`, `references/python-coding.md:135` ("Text opened with no
  encoding | `open(` and `read_text(` with no `encoding=`").
- **Version:** reviewed 2026-10-26.
- **What misled:** the row names no tool.
- **What happened:** Ruff's `PLW1514` found 5 of about 290 sites, because it misses
  `Path.read_text` wherever it can't infer the type. The row also leaves out `subprocess` calls
  with `text=True` and no `encoding=`, which were 64 of 66 such calls in the run.
- **Suggested fix:** add `text=True` to the row. Say plainly that `PLW1514` is partial, and give
  a grep or an AST check that finds the rest.

## 9. `python-security`'s per-line suppression doesn't scale to a tools directory

- **Skill and module:** `coding`, `references/python-coding.md:154-155` (S603 and S607 "flag
  every `subprocess` call, safe ones included; review each, and suppress it with a comment"),
  with `python-security.md`'s audit rows at :114-119.
- **Version:** reviewed 2026-10-26.
- **What happened:** for a directory of maintenance scripts, that is about 206 suppression
  comments: 135 `S603` and 71 `S607` on calls that pass a list.
- **Suggested fix:** offer `per-file-ignores` for a tools directory, keeping the review, with a
  comment in the Ruff config naming what was checked.

## 10. `python-coding` assumes a package, with no shape for scripts in a non-Python project

- **Skill and module:** `coding`, `references/python-coding.md:15` and `:22` (pyproject, uv, src
  layout, `requires-python >=3.12`).
- **Version:** reviewed 2026-10-26.
- **What misled:** the repository has dependency-free Python scripts called by a C build. No
  package exists, and none is wanted.
- **What happened:** the run couldn't cite a module rule for what such a repository should
  declare. Line 22's `>=3.12` reads as a fixed value rather than "the oldest version you test".
- **Suggested fix:** a short section for scripts in a non-Python project: a tools-only Ruff
  config, a stated floor, and how the build checks for it.

## 11. `bash-coding` has no room for a documented decision to leave out `-e`

- **Skill and module:** `coding`, `references/bash-coding.md:15` and the audit row at `:168`
  (Bash without `set -euo pipefail` is `GAP`).
- **Version:** reviewed 2026-10-26.
- **What happened:** two scripts in the run omit `-e` on purpose: a hook that must never fail a
  session, and a probe that collects every result. Each says why in a comment. The row rates
  both `GAP`.
- **Suggested fix:** "`GAP`, unless a comment beside the `set` line says why `-e` is left out
  and the script checks each command it relies on."

## 12. `bash-security`'s delete row rates constants like input, and misses `cd ""`

- **Skill and module:** `coding`, `references/bash-security.md:125` ("`rm -r` or `rm -f` on a
  variable path without `:?` or `--` … `BLOCKER`").
- **Version:** reviewed 2026-10-26.
- **What misled:** in the run, the variable came from a constant in the same file. The row gives
  that the same rating as user input.
- **What else it misses:** `cd "$dir" && rm -rf "$sub"` is a common guard, and `cd ""` succeeds
  in Bash, so the guard doesn't stop an empty value. That's the case the row exists for.
- **Suggested fix:** `BLOCKER` where the value can come from input or the environment, `GAP`
  where it is a constant in the file. Add a line saying `cd "$dir" &&` doesn't guard an empty
  `$dir`.

## 13. `git-workflows` assumes a release is a tag

- **Skill and module:** `git-workflows`, `references/releases-and-versions.md:129` (the Audit
  table's first row) and `SKILL.md:32` (rule 7, "Release from an annotated tag").
- **Version:** reviewed 2026-10-16.
- **What misled:** the audited project defines a release as a commit named in a committed
  manifest, and its consumers pin that SHA. It had dozens of such releases and no tags.
- **What happened:** the row "rate how the next tag gets made" doesn't say whether a project
  with no tags, by design, has a gap at all.
- **Suggested fix:** one line. Where releases are commits named in a manifest that consumers pin
  by SHA, a tag is optional. Rate the tag route only if the project's own records say it tags.

## 14. A finished plan file has no status mapping

- **Skill and module:** `project-bootstrap-and-audit`, *File governance*, standard line 4403
  ("a plan file left after merge"), and *Merge, delete, leave alone*.
- **Version:** standard 0.48.2.
- **What happened:** the run found 16 superseded or executed plans in `docs/`. *File governance*
  says to delete them, but none of the ten dimensions says what status they get. The run chose
  `OVER` on dimension 3, and another run could choose `DRIFT` on dimension 10.
- **Suggested fix:** state it, for example "`OVER` on dimension 3; `DRIFT` on dimension 10 where
  the file also asserts something false today".

## Smaller notes

- **The standard's cooldown table (around line 2292)** rates a three-day Dependabot cooldown
  `OVER`. The repository's comment said it was set to match the wait of another scheduled
  check. A line would help: "aligned with another check" is a reason to record, not a reason to
  keep it.
- **`coding` `SKILL.md:93`:** the `BLOCKER` definition ("a check reporting success while
  measuring nothing") fit two tests that print "UNPROBED" and exit 0. No language module has an
  audit row for "a skip path exits 0". One row in `python-coding` would find them.

## Skills that didn't load

None. All four expected skills loaded.

## Coverage gaps (no skill covers these)

- **C code:** see item 1.
- **Meson build files:** whether the declared minimum version is true, options, custom targets
  that run interpreters.
- **Fuzzing and damaged-input harnesses for C parsers.**
- **Escaping output for a file format another program parses**, such as a text format or a log
  read line by line.
  `coding` says the `input-handling` and `logging-and-observability` modules are planned.
- **Test design, and Python test suites inside a non-Python build.** The testing skill is
  planned.
- **ShellCheck couldn't run in the session.** It wasn't installed, and fetching it was refused,
  so the shell review rested on reading alone. A note in `bash-coding` on what to do without it
  would help.
