# Rig session 2026-08-27, build `978f9b0`

The morning after `0.9.4-rc2+platterpus.11` was published. **No rips: the
session died at its second probe**, which is the finding.

- **Ripper**: `cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-g978f9b0)` —
  our new stable release, installed on the rig.
- **Consumer**: `platterpus 0.6.29 (43a33b4)`, up from `0.6.28`.
- Collected `20260827T013150Z`. `MANIFEST.txt` reports `rip artifacts: 0`.
- `SHA256SUMS` covers every file here.

## 1. The release mechanism works, end to end

This is the first evidence that a consumer can resolve and install a cyanrip
release from `release-manifest.json` alone, with no tag anywhere:

- `probes-doctor.txt` — `[✓] cyanrip build — cyanrip 0.9.4-rc2+platterpus.11
  (platterpus-fork-g978f9b0) — the Platterpus fork`, and **11 OK, 0 warnings,
  0 blockers** across their whole preflight.
- Their install step took `978f9b0` and the expected build tag
  `platterpus-fork-g978f9b0` as arguments and refused to install anything whose
  banner did not match.

`+platterpus.11` therefore passes the consumer's own readiness check on real
hardware, which is worth having before round 15 opens against it.

## 2. `cyanrip --version` hangs through the host wrapper — AND IT IS NOT OURS

Second morning running, and this time it **stopped the rig session entirely**:
`00-summary.txt` ends mid-probe at `P3 ripper banner` with no exit line, and
no rip followed.

The shape changed, and the change is what isolates it. On 2026-08-26 the P3
artifact was **0 bytes**. This time:

    $ cyanrip --version
    cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-g978f9b0)
    …/platterpusmorning.sh: line 143: 221525 Killed  timeout -k 10 60 "$HOME/.local/bin/cyanrip" --version 2>&1
    (probe failed: exit 137)

**The banner is printed in full, and then the process does not exit.**
`02-ripper-version.txt` holds the same 59 bytes. So whatever hangs, hangs
*after* cyanrip has written its output.

### Three independent reasons it cannot be cyanrip

**(a) Structural, from our source.** `--version` is handled inside
`GEN_OPT_PARSE`, which prints the banner and returns `-EAGAIN`;
`cyanrip_main.c:1656` turns that into `return 0`. That is **65 lines before**
`crip_diag_enable()` at :1721 registers the `atexit` writer, and before
`crip_stall_watchdog_config()`. **On the `--version` path cyanrip registers no
atexit handler, starts no thread, and opens no device.** There is nothing in it
that can block after the write.

**(b) Measured, from the binary.**

    $ strace -f -e trace=write,exit_group,clone ./build/src/cyanrip --version
    write(1, "cyanrip 0.9.4-rc2+platterpus.11 "…, 65) = 65
    exit_group(0)                           = ?
    +++ exited with 0 +++

One write, then exit. No `clone`, so no thread exists to fail to join.

**(c) From THEIR OWN artifact, which is the strongest of the three.** Their
install script reads the banner off the freshly built in-container binary with

    _out="$("$built" "$_f" 2>/dev/null)"

for `-V` then `--version`, and **refuses to install if `$_banner` is empty**.
`978f9b0` is installed and their doctor reports it, so that command substitution
*returned* — a command substitution blocks until the child exits. **Their own
control flow proves cyanrip's `--version` terminates.**

The difference between the two invocations is not the binary and not the flag:
it is that one runs the binary and the other runs
`~/.local/bin/cyanrip`, the host export created by
`distrobox-export --bin /usr/local/bin/cyanrip`.

### What would settle it, and it is one command

**Hypothesis, offered as a hypothesis:** the export wrapper does not exit when
its child does — most commonly because it allocates a PTY and waits on it.
Platterpus's own invocations do not hang, and they run the binary with pipes;
the rig probe runs the wrapper from an interactive shell.

If that is right, closing stdin fixes it:

    time timeout 60 ~/.local/bin/cyanrip --version < /dev/null

and these separate wrapper from program:

    time timeout 60 /usr/local/bin/cyanrip --version     # in-container binary
    time timeout 60 distrobox-enter -n ripping -- true   # the wrapper alone

**We cannot read that wrapper and are not saying what it does.** If the third
command hangs, no part of either program is involved.

### The correction we are carrying forward

A first local reading showed `--version` at **10.8 s** against `-v` at 0.04 s —
a 260× difference that looked like the whole answer. **It was a freshly-linked
binary, not the flag, and it did not survive a re-run.** Interleaved after a
warm-up: `--version` 0.039 / 0.042 / 0.041 s, `-v` 0.037 / 0.041 / 0.038 s,
`-V` 0.038 / 0.038 / 0.034 s. Recorded because it is exactly the shape of claim
this seam exists to catch, and it nearly went out.

## 3. Their UI script still pins the previous round's build

`logs/log.txt`:

    ui script L150 fail: the installed cyanrip is NOT platterpus-fork-gd9c058c,
    the build the open handshake round is reviewing.

Round 14 is closed and `d9c058c` has been superseded by the release that closing
it authorised, so the assertion is now describing a state that no longer exists.
**Stated as an observation of the artifact, not a diagnosis of their code.**

It is worth naming because the new round cycle makes it recurring rather than
one-off: if a script asserts "the build under review", that value changes at
every close, and a check pinned to it fails every time the cycle advances
correctly.

## 4. What this session does NOT establish

- **No rip happened.** Nothing here says anything about ripping, checksums,
  pregaps or the log. The only cyanrip output in the whole bundle is the version
  banner.
- **`0.6.29`'s pin and channel are unknown to us.** `43a33b4` is the **build id
  from their banner**, and for `0.6.28` the banner id (`296a69d`) and their
  declared `HANDSHAKE-OUR-PIN` (`b524936`) were **different values**. We are not
  guessing which `0.6.29` is, and round 15 asks them to declare it.
