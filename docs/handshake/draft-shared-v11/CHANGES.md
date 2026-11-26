# Next shared-document version: what changed and why

Drafted 2026-11-25 from the four shared files at `cyanrip@5b20a334`, byte-identical to `platterpus@4021f95c`; neither repository was edited. Three files change: `PROTOCOL.md` v10 to v11, `seam-rules.md` v9 to v10, and `seam-commands.md`, which declares no version and is named by its hash. `OWNERSHIP.md` has no change, so there is no copy.

Kinds: **(a)** agreed wording, quoted; **(b)** mechanical; **(c)** drafted here, needs both sides' accept. Line numbers are the new files'.

## PROTOCOL.md

| # | Where | Old | New | Source | Kind |
|---|---|---|---|---|---|
| P1 | :1 | `# Handshake protocol v10` | `# Handshake protocol v11` | v10's own bump, `1989c762` | b |
| P2 | :1279-1290 | nothing between §9 and §10 | `---`, `# Appendix A. Change history`, and one paragraph saying §1 to §9 bind, that HR-2, HR-2.1 and the README rule still bind, and that nothing moved | platterpus audit F16 (`platterpus@972b4d84:docs/cyanrip-fork.md:1943`); cyanrip:R43.L1.S34 | c |
| P3 | :305-306 | `…refs/heads/evidence` (§17). | adds: `A run folder's README filed there may be corrected on the default branch, as §19 says (v11).` | a pointer to P5 | c |
| P4 | :1843-1917 | none | `## 19. Changes in v11`, in §18's shape: summary, bullets, versions named, *Declaring 11*, *What v11 does not do* | cyanrip:R43.L1.S18, S34 | c |
| P5 | :1857-1865 | none | the README rule, word for word | cyanrip:R42.L1.S30, accepted platterpus:R42.L2.S18; text promised cyanrip:R42.L3.S6; platterpus:R42.L4.S5 waits for it | a |
| P6 | :1128-1137, §7 | `NOT a released build` otherwise, with no line beneath | adds the qualifier beneath each arm: `(not declared at build time; whether this commit was published is not checked by cyanrip)` or `(declared at build time, withdrawn: git reported changes in the tree)` under the second; the arms unchanged | cyanrip:R43.L1.S54 | c |
| P7 | :743-748, R1 | `R1 — Close conditions are fixed in lap 1 and cannot grow.` and its three lines | fixed when lap 1 is sent, and changed after only by one side's proposal and the other's next lap accepting it by name | cyanrip:R43.L1.S58; the week review of 2026-11-10, point 2 | c |
| P8 | :898-901, after R10 | none | `R11 — One builder per request (v11)` | cyanrip:R43.L1.S59; the week review of 2026-11-10, point 4 | c |

**Deviation from the brief: the history keeps its numbers, §10 to §18, and v11's entry is §19.** It is not renumbered A.1 to A.9, for three reasons:

1. Both sides' tooling finds a version by its `## N. Changes in vM` heading: ours at `tools/seam-check.py:131` (`^## \d+\. Changes in v(\d+)`), theirs at `platterpus@4021f95c:tests/test_handshake_tooling.py:1531-1536`, which fails once their gate implements 11 unless `^## \d+[a-z]?\. Changes in v11` matches. A.n headings break both; on the draft, ours reads 11 and theirs matches.
2. Unqualified citations live where nothing may be edited, or where the edit would fall to other people. HR-2.1's own header, the operator's words, says `added to PROTOCOL §17` (:1768). Others: our `docs/handshake/README.md:58`, `tools/ingest-bundle.py:80`, `tests/release_gate.py:650,685`, and the sent laps.
3. The sections already follow §9 (:1292-1917); "move to an appendix" needs only a divider.

Every §10 to §18 reference still resolves, unchanged. In the file: :305, :1498 (`§13`), :1535 (`§15`), :1553 (`§18`), :1768 (HR-2.1, verbatim), :1814 (`§14`), :1818 (`§17`). Elsewhere, each names its version and so still resolves: `seam-rules.md:415,422,429` (`PROTOCOL v7 §15`, `v8 §16`, `v10 §18`) and `OWNERSHIP.md:209` (`v10 (§18)`).

A.n numbering would take both regexes, the seven in-file references, and a mapping sentence for HR-2.1's unalterable header.

- HR-2 and HR-2.1 now sit under an appendix heading; P2's paragraph says they still bind.
- §10's last paragraph (:1306-1307, *"Widening either set is a visible edit…"*) reads like a §9 rule and now sits in the appendix. Left in place: in §9 it would soften *"may shrink, never grow"*.

## seam-rules.md (v9 to v10)

| # | Where | Old | New | Source | Kind |
|---|---|---|---|---|---|
| R1 | :21, :389 | `9` | `10` | v9's pattern | b |
| R2 | :280-285 | none | S-19, headed by the rule *"a close condition that names a filing names the repository and path it is filed in"* | platterpus:R39.L6.S29(e), from its S11; cyanrip:R39.L7.S4 agreed S11, and S24 quotes this wording | a (wording), c (number, `[BOTH]`, body) |
| R3 | :287-291 | none | S-20, *"a test or rig script names no round, release or build in what it writes, unless that name is read from the run"*, with its reason quoted | platterpus:R40.L4.S21(b); cyanrip:R41.L1.S21 "as written" | a (wording), c (number, tag, body) |
| R4 | :390, :393 | `BOTH(S-1..S-18)`, `all eighteen` | `BOTH(S-1..S-20)`, `all twenty` | follows R2 and R3 | b |
| R5 | :431-439 | none | the v10 paragraph: provenance, numbers new in v10, binds from round 44 | Platterpus TASKS R229 | c |

## seam-commands.md

| # | Where | Old | New | Source | Kind |
|---|---|---|---|---|---|
| C1 | :112, the meaning cell and CR's cell | meaning: `a code the disc returned is what the files … carry, over the one -t gave …`; CR: `HAVE — .24, 93afa15` | the flag does nothing from `.35`, which makes the disc's code the default over `-t` or CD-TEXT; a code that is not ISO 3901 is written to no file, from `.25`. CR adds `accepted and ignored from .35` with `cyanrip@1280aa4:src/cyanrip_main.c:1356-1373` | cyanrip:R41.L3.S22, platterpus:R41.L4.S14, cyanrip:R42.L1.S4; ISO 3901: cyanrip:R35.L5.S2, platterpus:R35.L6.S10, their R27. The meaning cell is Platterpus's wording (cyanrip:R35.L4.S7, which also promised this clause) | c |
| C2 | :140, §1b | none | `--overwrite-existing`, then `.36`'s help text plus ` (default: false)`, PP `?`, CR `HAVE from .36` | flag: cyanrip:R42.L1.S21, platterpus:R42.L2.S12; help text: cyanrip:R43.L1.S6 (held, not sent) | c |
| C3 | :261, CR | `?` | HAVE on a whole-disc rip with every track finished, no `-X`, and no `-p N=track` past track 1. Not under `-l`, not for an unfinished track, and not with `-p N=track` past 1. Under `-X` the cue names an unwritten `.bin` | code at `1280aa4` and a run of a `.35`-source build on `pregap.cue` and `mixed.cue` | c |
| C4 | :262, CR | `?` | what `Album:` prints, and where the value comes from. No substitution; `<U+XXXX>` escaping. Which test holds which case | `src/cyanrip_log.c:1385`, `src/cyanrip_main.c:4133-4187`, `:4250-4264`, `src/log_escape.c`; measured with `album=A\: B` | c |
| C5 | :464, :600-602, :614 (§7 generated block) | `.27` banner; three rows `**no record** \| 0 \| Couldn't open … for writing!`; count `61 refused, 3 …` | banner says these lines are drafted; rows `**refused** \| 64 \|` with the S19 line and reasons `No such file or directory` (twice) and `Is a directory`; count `64 refused, 0 …` | line: cyanrip:R42.L1.S19, platterpus:R42.L2.S11 | a (line), c (rows) |
| C6 | :620 | `As for a record that cannot be opened, above, the exit code stays at 0` | `Unlike a record that cannot be opened, which .36 refuses before anything is read (above; …S19, …S11), the exit code stays at 0` | as C5 | c |

Platterpus's generated §1a region is byte-identical. No `docs/…md` path was added to any file; their pointer sweep's ratchet cannot grow.

**Checkable only once `.36` is built**

- C5. `tools/probe-argv-surface.py --check` on the draft with the `.35` build fails by design; the diff is exactly the banner, three rows and count, and the help-coverage half passes (51 flags).
- Regenerate the block with `--markdown` from `.36`'s build; that replaces the banner and confirms the reasons (glibc's strings here; the macOS job checks macOS's).
- C2's meaning cell must equal `.36`'s `--help` line. The ` (default: false)` suffix is my inference from how the generator prints every bool.
- C6's `/dev/full` row was measured on `.28`. Measure it again on `.36`.
- On `.35`'s code `Argv table in seam-commands.md` fails against this file, so the fork lands it with `.36`'s refusal, and lap 3's hashes follow the regeneration. These hashes are a draft's.

## Not included, and why

- **US-37's R1 amendment.** No lap of either side proposes a wording (rounds 41 to 43, their TASKS and outbound laps searched); `docs/history/WEEK-REVIEW-2026-11-10-READ.md:32` says only that it "goes up for amendment". §19 names it under *does not do*.
- **KNOWN-ISSUES rows 13 to 15** (`cyanrip@5b20a334:docs/KNOWN-ISSUES.md:864-881`). None has an agreed wording.
  - Row 13 would add a §5b check and a conformance row: a gate refuses when the peer's transcription of the gate's own verdict disagrees. The candidate is only in our list, never a lap.
  - Row 14 would say in §5 whether `HANDSHAKE-OUR-VERSION` names the build under test or the declaring build. The row asks; no text.
  - Row 15 would reword platterpus:R30.L6.S23's items in §3/C46, R9, R8, §6d, §6c and §15. No agreed replacement, and not re-read against v8 to v10.
- **The PP cell at :262** is Platterpus's (their PP-12, R228). C2's PP `?` is theirs too, and their S12 says they will send the flag. C1's range cell is theirs, unchanged.
- **The README rule's open points.** S30's wording is in, as agreed, but it does not fit HR-2 point 4 as both checkers enforce it: append-only, each path once, five fixed columns (`tools/evidence.py:136-140`, `:815-817`; `platterpus scripts/evidence_manifest.py:150-160`). No lap says:
  - which column names the correcting commit;
  - whether a second row may be added for the same path;
  - which copy's bytes and sha256 the row gives.

  cyanrip:R42.L3.S6 promised that text. Both sides must settle it before either checker implements the rule.

## Found along the way (not shared-file changes)

- **Under `-X` the CUE sheet names a data track's `.bin` that is never written.** It has a `FILE` and a `TRACK … MODE1/2352` line (`src/cyanrip_main.c:1872-1891` at `1280aa4`). Measured on `mixed.cue`, exit 0. I found no open item for it, and did not check upstream.
- `--prefer-disc-isrc`'s help says the disc's ISRC is "always used", but a code that is not ISO 3901 is not used (`src/cyanrip_main.c:1370-1373`). The same text reaches `PROVIDER-CONTRACT.md` P1.
- `tools/probe-argv-surface.py:145-152` describes `.35`'s exit-0 refusal; it needs updating with `.36`. `tests/release_gate.py:682-700` asserts the gate refuses 11.

## sha256

    580ac7204d6a6af3dda1660b2496e10f886ae4eeb71120fad95b970dc43c34cf  PROTOCOL.md
    505ba476295bccaefc9b7a8702392a9803410b3a317d70b1dd0ab01f39ac1fb1  seam-rules.md
    ed68538b5e11d3c5f9ad38a8b8d23057407499d210dc7dc97922a76ac0753952  seam-commands.md
