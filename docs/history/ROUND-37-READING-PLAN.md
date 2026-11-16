# Reading the Full run of `.28` (`3f288fb`) with Platterpus 0.7.117 — checklist

Written 2026-11-03, before the run arrived, so the reading is checked against a list fixed in advance. Each item ends up in the run folder's README: as a finding under *What it shows*, or under *Questions, gaps and next time*.

## A. Identity, before anything else

- [ ] Every `.log` file, and the securing pass's record, opens with `cyanrip 0.9.4-rc3+platterpus.28 (platterpus-fork-g3f288fb)`. No other build appears.
- [ ] Platterpus is 0.7.117: tag `v0.7.117` at `platterpus@104c82d2`. The About panel showed build `104c82d` on Fedora 44, Python 3.14.9, ffmpeg 8.1.3.
- [ ] `tools/ingest-bundle.py --peer` names both as the newest release of each side when the run began.
- [ ] Every member matches the bundle's own `MANIFEST.txt` hash.
- [ ] Redaction: home folders become `~`. The owner's name is *not checked* unless `CYANRIP_REDACT_NAMES` is set by then.

## B. Round 37's close conditions (our lap 1 S10, their lap 4 S10)

- [ ] No defect in `.28` makes the pin unsafe to approve. If one does, name it.
- [ ] Every track whose pregap is `unknown` on the reference disc has its own line in `Pregap searches:`. Count it in every log of the run, not one.
- [ ] The script's verdict: pass, fail, error, skipped, blocked, unreachable, `ok`, `counts_as_evidence`. Explain every unreachable step.

## C. What `.28` changed, on a drive for the first time

- [ ] `Drive used:` names the drive and revision (`PIONEER BD-RW BDR-209D (revision 1.51)`). The `none (disc image, …)` form is for images only.
- [ ] `Speed:` gives the drive's answer, not libcdio's default (`819c735`). If the ladder sent a `-S` the drive refused, the rip continues at drive speed and says so.
- [ ] `C2 errors:` on a drive that reports C2 unsupported: what it says, and whether its words claim more than the drive answered.
- [ ] The media-change line: present or absent, and why.
- [ ] `Recordable:` is `no` for a pressed disc, and `yes` for a CD-R if one was ripped.
- [ ] `Accurate stream:`.
- [ ] `Pregap searches:`: one block for every searched track, and `unknown` with the reason `sub-channel search bounds did not meet` where the bounds did not meet.
- [ ] `Names shortened:` appears only if a name passed 255 bytes; if it appears, check what it says.
- [ ] The `--diagnostics` record at `/11`:
  - `kept_read_began` is a string where a read was kept;
  - `isrc_disc_read` from a real disc, for the first time;
  - `error_positions` where a read was unsure.
- [ ] `--reread-time-limit` is absent from Platterpus's argv, as their §1b cell says (`NO: read, not sent`).
- [ ] The log escape: any title, CD-TEXT or MusicBrainz value with a control character is escaped, not broken across lines.
- [ ] Review C's changes:
  - a failed write named;
  - the AcoustID key withheld from the argv echo and the log, if a key was used;
  - AccurateRip and the Cover Art Archive reached over HTTPS only.
- [ ] The tally's denominator leaves out data tracks; this matters only on a mixed disc.

## D. Carried over from earlier runs: does `.28` change any of them?

- [ ] Track 9 of the reference disc. `.27` read `unknown` where `.25` and EAC read 94 frames, with LSN 145567 undecided. Check the same sector and the same counts.
- [ ] Track 3's accuracy (EAC parity row 6): right on some reads and wrong on others, with no cause named.
- [ ] The disc ISRC on the BDR-209D (item 8): what `isrc_disc_read` and `Disc ISRC:` say now.
- [ ] The cache probe's result against `KNOWN-ISSUES.md`'s cache table, which needs a row (`cache_table_matches_the_transcripts`).
- [ ] Repeat-limit cases, and whether each one's clause printed.
- [ ] `Extraction speed:` under `-Z`: the kept read's own speed.
- [ ] `Track N read with no error reported.` beside each AccurateRip verdict.
- [ ] `tools/cross-rip.py` against the earlier runs of this disc.

## E. Hardware rows still open in `CLAUDE.md`: did this run reach any?

- [ ] C2: this drive reports it unsupported, so expect not.
- [ ] `-f`: a stopped search, and one that finds nothing.
- [ ] Damaged media: a drive that reports a failed read.
- [ ] CD-TEXT from a physical disc.
- [ ] `Recordable:` on a recordable disc.
- [ ] `Pregap source:`'s two-search clause.

## F. Questions, gaps and next time (owner, 2026-11-03)

For each item: the log file and line, what would settle it, and who owns it.

1. **Questioned:** a value or wording that looks wrong, unexplained, or claims more than was observed.
2. **Possibly missing:**
   - a line, field or step expected and absent;
   - evidence the bundle does not carry;
   - a run section that did not run.
3. **To add next time:** log lines, record fields, run steps or discs that would have answered a question here.
4. **More than we asked:** information the logs carry beyond what was asked, and what it shows.

Each item that needs action becomes a `STATUS-OPEN` row, a lap statement or a task, named in the README.
