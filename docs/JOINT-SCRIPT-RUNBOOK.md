# Running the joint script — operator runbook

**DRAFT, and Platterpus owns it.** Every instruction here is about *their*
application: their `--run-script` runner, their sections A, B and D of the joint
script, their settings names, their transcript directory. We wrote it because
the operator asked for one and we had the script in front of us — not because
it is ours to specify.

**On adoption this file moves to `docs/rig-scripts/` in `rmccann-hub/Platterpus`,
beside the script it describes, and our copy is deleted.** One place, nowhere
else, exactly as the script's own header requires of the script. A faithful
second copy is still a second spec that can drift, and `PROTOCOL.md` already
diverged between the two repositories that way.

**Every claim below is tagged with where it came from.** That is the whole point
of the tagging: Platterpus only has to check the `[UNVERIFIED]` lines, because
the rest are quoted from their own file or measured on the rig.

| tag | means |
|---|---|
| `[SCRIPT]` | read out of `round-08-joint.txt` itself — quoted, not remembered |
| `[MEASURED]` | we ran it, on the rig or here, and this is the result |
| `[INFERRED]` | follows from something tagged above, but was not itself run |
| `[UNVERIFIED]` | **we assert it and cannot check it.** Platterpus must confirm or correct |

---

## 0. What this is

The joint script is **the test session**, not a document about one. One file
drives the whole rig pass and writes one transcript directory, which is the only
thing that travels back. The lap is the correspondence; this is the operating
procedure for the run.

`[SCRIPT]` The file's own header: *"THIS IS THE ONLY FILE EITHER SIDE SENDS. Not
a document about tests. The tests."*

---

## 1. Preconditions — four, and all four bite

### 1.1 Install the pinned ripper

```
~/Applications/platterpus-x86_64.AppImage --install-ripper 2ce8993
```

`[MEASURED]` The **path form is required**. `platterpus --install-ripper …` as
printed by the update dialog gives `bash: platterpus: command not found` on an
AppImage install. **This has now blocked the operator three times**, which is
what moves it from an annoyance to the single most expensive line in the
product: it is printed at the exact moment someone is trying to follow an
instruction, and it does not work. It is a finding against the dialog, in the
lap's §H.

If the AppImage is not where this runbook assumes, find it rather than guess:
```
ls ~/Applications/*.AppImage; command -v platterpus || echo 'not on PATH'
```

**Operator-side fix, so it stops recurring** — `~/.local/bin` is already on this
rig's PATH, since `~/.local/bin/cyanrip` resolves there:
```
ln -sf ~/Applications/platterpus-x86_64.AppImage ~/.local/bin/platterpus
```
After that the dialog's own command works verbatim. This is a workaround on the
operator's machine and **not a substitute for fixing the dialog** — anyone
installing fresh hits it again, and they have no symlink.

`[MEASURED]` `2ce8993` is `0.9.4-rc1+platterpus.6-beta.4`, ledger seq 15,
channel `beta`. 38 of 38 green from a fresh clone of that exact commit, built
and run rather than asserted.

Confirm it landed:
```
~/.local/bin/cyanrip -V
```
`[MEASURED]` Must print `cyanrip 0.9.4-rc1+platterpus.6-beta.4
(platterpus-fork-g2ce8993)`. If it says anything without `platterpus-fork`, you
are on stock upstream and — in the script's own words — *"everything below is
void."*

### 1.2 Confirm the app can run scripts at all

```
~/Applications/platterpus-x86_64.AppImage --help
```

`[MEASURED]` **Answered by the 2026-08-12 run: `--run-script` exists and
works.** The app log records *"unattended test script starting (--run-script)"*
and *"ui script run starting: 72 step(s), unsafe verbs refused"*. There is also
a GUI path — **Tools → Run test script…** — which opens a paste-and-Run console.
Both reach the same runner. This was `[UNVERIFIED]` until the run; it is not any
more.

### 1.3 Put the disc in the drive, first

`[SCRIPT]` Section A's second line is `log Put the disc in the drive before
running this.` Section B then does `rescan`, `wait 20`, `expect-tracks 14`,
which fails immediately on an empty drive.

`[MEASURED]` `/dev/sr0` must exist. It vanished once on this rig and took three
checks down with it; a reboot restored it. Check before spending time:
```
ls -l /dev/sr0 /dev/cdrom
```

### 1.4 Check two settings, or B2 fails for a reason that is not a defect

`[SCRIPT]` B2 **asserts** these rather than setting them:

```
expect secure_rerip_dynamic True
expect secure_rerip_matches 2
```

`[MEASURED]` **On this rig `secure_rerip_dynamic` is `False`, and B2 fails
because of it** — *"expected secure_rerip_dynamic == True, got False"*. So this
section was wrong to say "check": **set it before running**, in Settings, or the
run reports a configuration mismatch as though it were a defect. `matches` was
not reported failing, so 2 appears to be correct already.

That is one of the four handoff questions in §9 answered by the run, and the
answer changes the instruction rather than confirming it.

---

## 2. Run it

### 2.0 First: confirm the pin survived

```
~/.local/bin/cyanrip -V
```

`[MEASURED]` Must still say `platterpus-fork-g2ce8993`. **Check this immediately
before the run, not once at the start of the day.**

`[MEASURED]` The reason is in the rig's own build-tree reflog: both earlier
`+platterpus.6` betas were installed and then moved back to `ddf7ac3` —
`cb440bd → ddf7ac3`, and `310dbd2 → ddf7ac3`. Twice.

`[UNVERIFIED]` **Whether that was the operator or Platterpus, we do not know.**
It is `J10` of the lap. What matters here is the consequence: if the pin has
reverted by the time section D rips, the transcript's section A banner says one
build and the rip happened on another, and the round's hardware evidence
describes a build nobody is reviewing. This check costs one second and is the
only thing standing between that and a silent invalidation.

If it has reverted, reinstall before running:
```
~/Applications/platterpus-x86_64.AppImage --install-ripper 2ce8993
```

**And run the same command again the moment the script finishes.** Before and
after is a complete guard where before alone is not: if both say `2ce8993`, no
substitution happened at any point during the session and the transcript
describes the build it claims to. One second, twice.

`[SCRIPT]` **The script cannot catch this itself, and that is worth knowing.**
Section A asserts `expect-cyanrip platterpus-fork`, which is an identity check,
not a pin check — `ddf7ac3` is also a `platterpus-fork` build, so that
assertion passes on the approved build just as happily as on the test pin. The
full banner *is* recorded in the transcript either way, so a substitution is
visible to anyone reading it; it is simply not asserted. Section A is
Platterpus's, so tightening it to the specific pin is theirs to decide.

### 2.1 Then run it

```
~/Applications/platterpus-x86_64.AppImage --run-script /path/to/round-08-joint.txt
```

`[MEASURED]` This is the exact form that ran on 2026-08-12. No other options
were needed. Whether the runner takes further flags is still Platterpus's to say.

### 2.2 IMPORTANT — launch first, identify the disc, THEN run the script

`[MEASURED]` **The 2026-08-12 run produced no rip at all**, and the cause was not
the disc, the drive or the ripper. Four seconds in, a second `drive changed:
/dev/sr0` event for the *same device* restarted disc identification, the teardown
gave the running worker **zero milliseconds**, and its in-flight `cyanrip -I -N
-d /dev/sr0` was **SIGKILLed** — `exit -9`, no output, because SIGKILL cannot be
caught. No disc identified, so no tracks, so the Start button stayed disabled,
so `rip` failed and everything after it was void:

```
19:18:06,823  drive changed: /dev/sr0
19:18:06,830  DiscInfoWorker did not stop within 0ms — abandoning it
19:18:06,831  cyanrip exited -9 … argv: cyanrip -I -N -d /dev/sr0
```

`[INFERRED]` **So do not launch straight into the script.** Start Platterpus
normally, wait until the track list is populated and the disc is identified, and
only then run the script from **Tools → Run test script…**. That skips the
launch-time drive-change entirely. It is a workaround, not a fix — the fix is
Platterpus's, and it is `J11`.

---

## 3. What it does, and how long it takes

### It is NOT a full-album rip

`[SCRIPT]` B1 asserts the disc has 14 tracks (`expect-tracks 14`). B3 then does
`select-tracks 1,3,5-7`, which is **6 tracks**.

`[INFERRED]` Section D's `rip` therefore rips those six, not the album.

`[SCRIPT]` `wait-for-rip 7200` is a **two-hour ceiling, not an estimate.**

`[INFERRED]` Expect roughly 15–20 minutes of disc time for six tracks on this
drive, based on the extraction speeds in the rig's own logs (1.0–2.7×).

### Section by section

| | owner | what happens |
|---|---|---|
| **A** | Platterpus | `[SCRIPT]` version banners for both builds, then `rig-check` with no album folder — the argv half only, no disc spent. Screenshots the dependencies dialog. |
| **B** | Platterpus | `[SCRIPT]` `rescan`, track-count floor, the two secure-rerip assertions, track selection, album title and artist, a snapshot. |
| **C** | **cyanrip** | `[SCRIPT]` C1–C6: cache probe, four segfault argv shapes, the memory-disclosure `-t` shape, genopt's fatal messages, `-f` offset autodetection, `--verify-log` refusing a foreign log. |
| **D** | Platterpus | `[SCRIPT]` the rip, `wait-for-rip 7200`, screenshot and snapshot, then `rig-check` **with** the album folder so it also parses the log the rip just wrote. |

---

## 4. The one line you may have to edit

`[SCRIPT]` Section D ends with:

```
rig-check ~/Music/The Police/Every Breath You Take (round 8 joint, pass 1)
```

`[INFERRED]` B4 sets exactly that album title and `The Police` as artist, so the
default naming scheme should produce that folder and it should need no change.

`[SCRIPT]` But the script says plainly: *"Replace the path with the folder the
rip actually wrote. If you leave it off, the log checks report SKIP — and SKIP
means DID NOT RUN, which is the honest answer but not the one this round
needs."*

**So: after the rip, look at what folder was actually written**, and if it
differs, correct that one line. It sits in Platterpus's section but the comment
above it makes it the operator's to adjust.

---

## 5. Expect failures. Do not stop.

`[SCRIPT]` *"A failing step does NOT stop the batch. Only `abort` does. So write
tests that fail loudly and keep going — a run that stops at the first problem
hides every problem behind it, and on real hardware a disc pass costs an hour
you do not get back."*

**A transcript with red in it is a successful run, not a failed one.**

Two failures are expected and are not regressions:

- `[MEASURED]` **C1's cache-probe number will be wrong.** On this drive
  `cd-paranoia -A` reports **137 sectors**, then **140** on a second run.
  `ddf7ac3` printed `32 sectors measured`; `310dbd2` printed `at least 2048
  sectors, upper bound unknown`. A factor of 64 between two of our own builds
  while the drive did not change. The mechanism is known and is in the lap's §E;
  the fix is next round and the pin does not move for it.
- `[SCRIPT]` **C1 logs its own untrustworthiness on purpose**, so nobody cites
  the figure later: *"the Cache probe: number is KNOWN UNTRUSTWORTHY — method
  defect"* and *"cd-paranoia -A on this drive: 137 sectors, then 140. Believe
  those, not ours."*

---

## 6. The one thing that can cost you 23 minutes

`[MEASURED]` **`-x` is the cache probe. `-O` is overread. `-O` is confirmed to
hang the PIONEER BD-RW BDR-209D for about 23 minutes.** They are one keystroke
apart. The script only ever uses `-x` — do not add `-O` by hand, and do not
"try it to see".

`[SCRIPT]` The script carries this warning itself, immediately above SECTION C's
markers.

---

## 7. When it finishes

`[SCRIPT]` The transcript directory:

```
~/.local/share/platterpus/uiscript/<timestamp>/
```

`[UNVERIFIED]` That path is quoted from the script's final `log` line. We have
never seen one.

`[SCRIPT]` *"Send the transcript directory, nothing else."*

**Nothing else** is the important half. Both sides read the same artifact; a
summary sent alongside it is a second description of the run that can disagree
with the run, and then nobody knows which to believe.

---

## 8. Optional pre-flight — ours, not theirs

`[MEASURED]` Every check that is **not** a rip, writing nothing into the music
library and requiring no disc to be spent:

```
~/.cache/platterpus/cyanrip-fork/tools/rig-check.py \
  --album-dir "/home/rmccann/Music/rips/The Police/Every Breath You Take - Archive files/<EAC folder>" \
  --device /dev/sr0
```

`[MEASURED]` Use the beta.4 copy. Earlier versions could report a check that
never ran — four separate ways, all fixed in this release and listed in the
lap's §F. Exit status is 0 when nothing FAILED; a SKIP is not a failure, and the
summary keeps "did not run" and "ran and found nothing" apart on purpose.

`[MEASURED]` And if you want a parity block for an album without moving any
audio anywhere:

```
~/.cache/platterpus/cyanrip-fork/tools/audio-checksums.py digest \
  "/path/to/album" --tracktotal 14
```

About 60 bytes per track, pasteable into a lap. It refuses rather than guessing
when the directory is ambiguous — two files claiming one track number, a
`--tracktotal` below the highest track present, a numbered file that is not
audio. Every one of those refusals is a defect it had on the day it was written.

---

## 9. What Platterpus needs to verify in this file

This is the handoff. Four `[UNVERIFIED]` claims, and each is a yes/no:

1. **Does 0.6.11 implement `--run-script`, spelled exactly that way?** §1.2.
2. **Is the transcript path `~/.local/share/platterpus/uiscript/<timestamp>/`?**
   §7 — quoted from the script's own last line, never seen by us.
3. **Does the runner take any other options** the operator should know about —
   a dry-run, a resume, a way to run one section? §2 says "no other options"
   and that is an assumption, not a finding.
4. **Are `secure_rerip_dynamic` and `secure_rerip_matches` the correct
   `config.toml` names**, and are `True` / `2` the values a default install
   has? §1.4 — if a default install fails B2, this runbook should say to set
   them rather than to check them.

Correct anything else you like: **you own the app, so you own this.** Send it
back changed rather than commented on — a correction we apply ourselves is a
second implementation of your intent, and this whole seam exists because those
drift.
