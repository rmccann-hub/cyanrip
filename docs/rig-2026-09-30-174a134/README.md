# Rig session 2026-09-30 — build `174a134`, Platterpus 0.6.64, **stopped at section A**

**Read the build, not the date: two sessions, two builds.** `session/` is
`174a134`, `+platterpus.19`, through Platterpus **0.6.64** (`9b114c5`), and it
ended four seconds in. `session-51cc789/` and `rips/` are an earlier attempt the
same night on `51cc789`, `+platterpus.18`, stopped by the operator 28.9 s into
section F's rip. **Neither ran the Full test, and no rip of `.19` exists.**

## Provenance

| | |
|---|---|
| bundle | `platterpustestsession20260930t013.tar.gz`, as uploaded by the operator: the two session folders, tarred by hand, not an app bundle (there is no `COMPONENTS.json`) |
| sha256 | `5792e1030d381b1dc087662ec06924734cf9cf8b95ceea3af1cee2deb56c30c5` |
| size | 1,456,010 bytes, 21 files, 12 of them screenshots |
| sessions | `20260930T013138Z` (`.18`, `ended_reason` *"the console was closed"*) and `20260930T013523Z` (`.19`, ended by `abort-if-failed` after L277), each `run_size` full, app `0.6.64` (`script-report.json`) |
| drive | PIONEER BD-RW BDR-209D (revision 1.51), offset +667 |
| disc | DiscID `pNtImOkdBm9RMBIalzx0w9cfsYY-`, 14 tracks, the disc of every filed session |

**Every file here but this README is byte-identical to a member of that
tarball**, 7 of 7, each hashed against its original when it was copied:

| filed here | as delivered in their bundle | sha256/16 |
|---|---|---|
| `session/transcript.txt` | `platterpustestsession20260930t013523z/evidence/run/transcript.txt` | `547d6d47368f91cb…` |
| `session/script-report.json` | `platterpustestsession20260930t013523z/evidence/run/report.json` | `b786f57e73d036a8…` |
| `session-51cc789/transcript.txt` | `platterpustestsession20260930t013138z/evidence/run/transcript.txt` | `fb108483368a990e…` |
| `session-51cc789/script-report.json` | `platterpustestsession20260930t013138z/evidence/run/report.json` | `c1fab49de16734f4…` |
| `full-acceptance-angle-bracket.log` | `platterpustestsession20260930t013138z/rips/Platterpus Acceptance/full acceptance∶ angle‹bracket 20260930t013138 platterpus-fork-g51cc789/full acceptance∶ angle‹bracket 20260930t013138 platterpus-fork-g51cc789.log` | `7f764b1db1845a13…` |
| `full-acceptance-angle-bracket.eac.log` | `platterpustestsession20260930t013138z/rips/Platterpus Acceptance/full acceptance∶ angle‹bracket 20260930t013138 platterpus-fork-g51cc789/full acceptance∶ angle‹bracket 20260930t013138 platterpus-fork-g51cc789 (EAC-compatible).log` | `e20bb1bcd0bbca05…` |
| `full-acceptance-angle-bracket.cue` | `platterpustestsession20260930t013138z/rips/Platterpus Acceptance/full acceptance∶ angle‹bracket 20260930t013138 platterpus-fork-g51cc789/full acceptance∶ angle‹bracket 20260930t013138 platterpus-fork-g51cc789.cue` | `dcd541d532b3603a…` |

**Not filed**, with sha256/16: the 12 screenshots of section D, all from the
`.18` session; `01 - Roxanne.flac`, **0 bytes** (`e3b0c44298fc1c14`, the empty
file), so no audio was delivered; and the `.platterpus.json` report,
Platterpus's artifact, 95,551 bytes, `61f8b757661b5556`.

## Our reading

### `session/`: `.19` on 0.6.64 stops at section A, as it must

The ripper answered `cyanrip 0.9.4-rc2+platterpus.19 (platterpus-fork-g174a134)`
(`session/transcript.txt:105`), and `expect-ripper-under-review` failed at L277
(`:110`): *"the installed cyanrip is NOT platterpus-fork-g51cc789 — 51cc789 is
the APPROVED production pin (no handshake round is open, so there is no build
under review)"*. The run ended `pass=48 fail=1 blocked=274` (`:436`). **No drive
time was spent**: the only cyanrip invocations are `--version` at L274 and the
four of the wrapper probe, and there is no cyanrip log.

**No install could have passed that step**, which is what makes it a finding
about the cycle and not about the operator's install. Read at
`platterpus@9b114c5`: `PIN_UNDER_REVIEW` is `51cc789`
(`src/platterpus/deps/fork_source.py:675`), the same as `FORK_PIN`, so
`a_round_is_reviewing_a_build()` is false (`:1405`) and section A demands the
approved pin. And their test
`tests/test_handshake_pin_under_review.py:101-122` holds `PIN_UNDER_REVIEW` to
the `HANDSHAKE-PIN` of the newest inbound lap of ours, so no release of theirs
can name `174a134` until they hold a lap of ours that does. This is
misalignment 3 of `docs/handshake/PROPOSAL-release-cycle.md`, measured.

### `session-51cc789/` and `rips/`: a rip stopped by closing the console leaves no footer

Section F's rip of `.18` began at 01:32:04Z (its `-j` name) and the operator
closed the script console 28.9 s into the wait
(`session-51cc789/transcript.txt:381`, `:581`). **The log is 54 lines and ends
at `Tracks:`**: no track block, no completion footer, no `Log FUN512:`, and
`cyanrip -Y` exits **3**, *"No FUN512 checksum found"*. Platterpus's record,
not filed, gives the ripper's exit code as 1.

**The cause is not determined here.** `.18` writes the interrupt footer on a
SIGTERM mid-read (`docs/rig-2026-09-10-ddc1e8c/`), and a footerless log is what
a SIGKILL, a default-disposition SIGHUP, or a process still alive when these
files were collected would each leave. The console's close calls
`self._runner.stop("the console was closed")`
(`platterpus@9b114c5:src/platterpus/ui/dialogs/script_console.py:563`); what
that does to the app's own rip in flight we have not read. A consumer that
signals the wrapper rather than cyanrip has left cyanrip running before
(2026-09-07, 15m33s).

**Nothing here shows a defect in `.18` or `.19`.**
