#!/usr/bin/env python3
"""tools/rig-drivetest.sh, run end to end against stand-ins.

The runner is handed to the owner to run on the rig, where nothing of ours
can watch it, so every path it takes there is taken here first: distrobox, the
sg3_utils tools, eject, journalctl, strace, cyanrip and Platterpus's AppImage
are small scripts in a fake home, and the runner cannot tell.

Each case is a thing the 2026-11-05 drive test did, or one the runner exists
to survive (round 38):

  * Run A ended at its rescan step with two `cyanrip -I` disc reads running
    at once, the app having abandoned the first: the stand-in app fails its
    run exactly when the abandoned read is still alive at the end, so the
    probe guard is what makes the run rip.
  * A read killed for hanging lived on outside the killer's process group
    (the container's process): the stand-in's hung read escapes with setsid,
    and the check must find it holding the drive and stop it.
  * The first sitting left its files in ~/drivemode and the rig scripts in ~:
    the runner moves them into one folder and deletes nothing.
  * A run that rips nothing is retried once; two such runs end the app runs,
    and the reads that need no app still run.
  * Platterpus open stops the stage, and the upload is still made.
  * PureRead not put back: the settings bytes differ from the first read.

Every process the stand-ins start carries a name made for this run, and the
runner's process patterns are pointed at it, so nothing here can find or stop
a cyanrip that another test of the suite is running.
"""

import os
import pathlib
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNNER = ROOT / "tools" / "rig-drivetest.sh"
TOKEN = "dt" + uuid.uuid4().hex[:10]
FAKE_RIPPER = f"/usr/local/bin/cyanrip-{TOKEN}"
APP_NAME = f"platterpus-{TOKEN}.AppImage"

failures = 0


def check(cond, what):
    global failures
    if cond:
        print(f"ok   {what}")
    else:
        failures += 1
        print(f"FAIL {what}")


# The 256 bytes of Pioneer's settings block as sg_raw prints them, the shape of
# the 2026-11-05 read (not that read itself: a test reads no evidence path).
F4_ROWS = [" 00     ff ff 02 02 ff ff ff 00  00 00 00 ff ff ff ff 00    ................",
           " 10     00 ff ff 00 ff ff ff ff  ff ff ff ff 00 00 00 ff    ................",
           " 20     ff ff ff ff ff ff ff 00  ff ff ff 00 00 00 00 00    ................"]
F4_ROWS += [f" {o:02x}     " + "00 " * 8 + " " + "00 " * 7 + "00    ................"
            for o in range(0x30, 0x100, 0x10)]
F4_TEXT = "SCSI Status: Good \n\nReceived 256 bytes of data:\n" + "\n".join(F4_ROWS) + "\n"
TOC = "1+14+268857+150+14637+28217+50070+72720+90792+109325+128907+145812+159387+178482+201012+224660+246677"


def write(path, text, mode=0o755):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)


def build(base):
    """A fake home holding the first sitting's leftovers, and the stand-ins."""
    home, stub, bin_, cbin = base / "home", base / "stub", base / "bin", base / "cbin"
    for d in (home, stub, bin_, cbin):
        d.mkdir(parents=True)
    write(stub / "f4.txt", F4_TEXT, 0o644)
    write(stub / "f4-alt.txt", F4_TEXT.replace(" 00     ff ff 02 02", " 00     ff ff 01 02"), 0o644)
    write(home / ".config/platterpus/config.toml", 'output_dir = "~/Music/rips"\n', 0o644)
    write(home / "drivemode.txt", "\0" * 8598, 0o644)
    write(home / "drivespeed.txt", "\0" * 9492, 0o644)
    write(home / "drivemode/dumps/pioneer-f4.txt", "Thu Nov  5 22:20:26 UTC 2026\n" + F4_TEXT, 0o644)
    write(home / "drivemode/dumps/before.txt", "sg_inq output\n", 0o644)
    bundles = home / ".local/share/platterpus/bundles"
    bundles.mkdir(parents=True)
    old = bundles / "platterpusbundle20261104t125346z.tar.gz"
    old.write_bytes(b"old")
    os.utime(old, (1762000000, 1762000000))
    os.utime(home / "drivemode/dumps/pioneer-f4.txt", (1762381226, 1762381226))
    (bundles / "platterpusbundle20261105t2224310000.tar.gz").write_bytes(b"run A, failed")

    write(bin_ / "distrobox", """#!/bin/bash
[ "$1" = version ] && { echo "distrobox: 1.8.1"; exit 0; }
while [ $# -gt 0 ] && [ "$1" != "--" ]; do shift; done; shift
PATH="$STUB/../cbin:$PATH" exec "$@"
""")
    write(bin_ / "fuser", """#!/bin/bash
if [ -e "$STUB/held" ] || pgrep -f "$DRIVETEST_RIPPER_RE" >/dev/null; then
  [ "$1" = -v ] && echo "/dev/sr0: user 4242 F.... cyanrip"; exit 0
fi
exit 1
""")
    # Nothing here reaches the network: a download the runner tries fails
    write(bin_ / "curl", '#!/bin/bash\necho "curl: (6) the test suite has no network" >&2\nexit 6\n')
    write(bin_ / "journalctl", """#!/bin/bash
echo "2026-11-05T22:24:40+00:00 host kernel: sr 0:0:0:0: [sr0] tag#0 timing out command, waited 30s"
echo "2026-11-05T22:25:00+00:00 host kernel: usb 1-1: new device"
""")
    write(cbin / "sg_raw", """#!/bin/bash
out=""; len=0; args=("$@")
for ((i=0;i<${#args[@]};i++)); do case "${args[i]}" in -o) out="${args[i+1]}";; -r) len="${args[i+1]}";; esac; done
if [ -n "$out" ]; then
  python3 - "$out" "$len" "$*" <<'PY'
import sys
out, n, args = sys.argv[1], int(sys.argv[2]), sys.argv[3].split()
data = bytearray(n)
i = args.index("be")
if n == 26 * 2646 and int("".join(args[i + 2:i + 6]), 16) == 83416:
    data[13 * 2646 + 2352 + 7] = 0b00000111      # track 5's window: frame 13
open(out, "wb").write(bytes(data))
PY
  exit 0
fi
case " $* " in *" 3c 02 f4 "*) if [ -n "${F4_ALT:-}" ]; then cat "$STUB/f4-alt.txt"; else cat "$STUB/f4.txt"; fi;; esac
exit 0
""")
    for t in ("sg_inq", "sg_get_config", "sg_modes"):
        write(cbin / t, f'#!/bin/bash\necho "{t} output"\n')
    write(cbin / "sg_turs", '#!/bin/bash\n[ -e "$STUB/ejected" ] && exit 2; exit 0\n')
    write(cbin / "eject", '#!/bin/bash\ntouch "$STUB/ejected"\n')
    write(cbin / "cdrdao", '#!/bin/bash\nfor a; do last="$a"; done; echo CD_DA > "$last"\n')
    write(cbin / "sudo", '#!/bin/bash\nexec "$@"\n')
    write(cbin / "strace", r"""#!/bin/bash
o=""; while [ "$1" != /usr/local/bin/cyanrip ]; do [ "$1" = -o ] && o="$2"; shift; done; shift
echo "12:00:00.000 ioctl(5, SG_IO, {interface_id='S', cmdp=\\"\\\\xbe\\\\x00\\"..." > "$o"
exec "$HOME/.local/bin/cyanrip" "$@"
""")
    # The host-side ripper. A second read while one runs hangs, as the
    # container's process: it escapes the killer's process group.
    write(home / ".local/bin/cyanrip", f"""#!/bin/bash
printf 'Checking /dev/sr0 for cdrom...\\n\\t\\tCDROM sensed: PIONEER  BD-RW   BDR-209D 1.51 SCSI CD-ROM\\n\\n\\nOpening drive...\\n'
if [ -n "${{STUB_HANG:-}}" ] && [ -e "$STUB/lock" ]; then
  setsid -w perl -e '$0="{FAKE_RIPPER} -I -N -d /dev/sr0"; sleep 1000' & wait
fi
touch "$STUB/lock"; sleep 3   # still running when the second read starts, 2.4 s later
echo "MusicBrainz URL:"
echo "https://musicbrainz.org/cdtoc/attach?toc={TOC}&tracks=14"
echo "cyanrip 0.9.4-rc3+platterpus.30 (platterpus-fork-g5cc1c6b)"
rm -f "$STUB/lock"
""")
    # The app: its start-up disc read, then the script's rescan 1 s later; it
    # rips nothing if the abandoned read is still alive when the rescan ends.
    write(home / "Applications" / APP_NAME, f"""#!/bin/bash
n=$(( $(cat "$STUB/appruns" 2>/dev/null || echo 0) + 1 )); echo $n > "$STUB/appruns"
echo "INFO platterpus.app: platterpus ${{STUB_VER:-0.7.121}} (build 2ca5196) starting; args: $*"
perl -e '$0="{FAKE_RIPPER} -I -N -d /dev/sr0"; sleep 1000' & p1=$!
sleep 1
echo "INFO platterpus.workers: worker thread DiscInfoWorker was superseded by a newer disc probe"
perl -e '$0="{FAKE_RIPPER} -I -N -d /dev/sr0"; sleep 2' & p2=$!
wait $p2
ok=1
if kill -0 $p1 2>/dev/null; then ok=0; kill $p1; fi
[ -n "${{STUB_ALWAYS_FAIL:-}}" ] && ok=0
b="$HOME/.local/share/platterpus/bundles/platterpusbundle$n$(date +%s%N).tar.gz"; echo bundle > "$b"
if [ "$ok" = 0 ]; then
  echo "INFO platterpus.uiscript.runner: ui script run ended: 1 step(s) have failed; the first was L90 ('rescan')"
else
  case "$(basename "$2")" in drivemode.txt) names="dmfiveearly1 dmthreeearly1";; *) names="dsnospeed1 ds4x1";; esac
  for d in $names; do mkdir -p "$HOME/Music/rips/$d"; echo log > "$HOME/Music/rips/$d/$d.log"; echo audio > "$HOME/Music/rips/$d/01.flac"; done
  echo "INFO platterpus.uiscript.runner: ui script run ended: DONE, every step passed"
fi
echo "INFO platterpus.uiscript.runner: SEND THIS ONE FILE: $b"
""")
    shutil.copy(RUNNER, home / "Downloads" / "drivetest.sh") if (home / "Downloads").mkdir() is None else None
    return home, stub, bin_


def run(base, home, stub, bin_, args, script=None, extra=None, reinsert=False):
    env = dict(os.environ, HOME=str(home), STUB=str(stub),
               PATH=f"{bin_}:{os.environ['PATH']}", CHECK_SECS="6",
               DRIVETEST_POLL_SECS="1", DRIVETEST_SETTLE_SECS="1",
               APP=str(home / "Applications" / APP_NAME),
               DRIVETEST_RIPPER_RE=f"^{FAKE_RIPPER}( |$)",
               DRIVETEST_PROBE_RE=f"^{FAKE_RIPPER} .*-I( |$)", **(extra or {}))
    env.pop("DRIVETEST_AWAKE", None)
    env["DRIVETEST_AWAKE"] = "not asked for (the test suite)"
    helper = None
    if reinsert:   # the owner: take the disc out when the tray opens, wipe it, put it back
        helper = subprocess.Popen(["bash", "-c", f'while [ ! -e "{stub}/ejected" ]; do sleep 0.5; done; sleep 2; rm -f "{stub}/ejected"'])
    p = subprocess.run(["bash", str(script or home / "Downloads" / "drivetest.sh"), *args],
                       cwd=home, env=env, capture_output=True, text=True,
                       encoding="utf-8", timeout=240)
    if helper:
        helper.kill()
    return p


def timeline(home):
    """The timeline's messages, without the two time columns."""
    tl = home / "platterpus-rig/drivetest-r38/timeline.txt"
    return [line.split(" | ", 2)[2] for line in tl.read_text(encoding="utf-8").splitlines()] if tl.exists() else []


def sendfile(home):
    sends = sorted((home / "platterpus-rig/drivetest-r38/SEND").glob("*.tar.gz"))
    return sends[-1] if sends else None


def stray():
    return subprocess.run(["pgrep", "-f", FAKE_RIPPER], capture_output=True).returncode == 0


def case_stage1(base):
    home, stub, bin_ = build(base)
    p = run(base, home, stub, bin_, ["1"], extra={"STUB_HANG": "1"}, reinsert=True)
    tl = timeline(home)
    check(p.returncode == 0, f"stage 1 exits 0 (exit {p.returncode})")
    check(not (home / "drivemode").exists() and (home / "platterpus-rig/drivetest-r38/earlier/drivemode/dumps/pioneer-f4.txt").exists(),
          "the first sitting's ~/drivemode is moved into earlier/, not deleted")
    moved = home / "platterpus-rig/drivetest-r38/scripts/drivemode.txt"
    check(moved.is_file() and moved.stat().st_size == 8598 and not (home / "drivemode.txt").exists(),
          "the rig scripts are moved from ~ into scripts/")
    copy = home / "platterpus-rig/drivetest.sh"
    check(copy.is_file() and copy.read_bytes() == RUNNER.read_bytes(),
          "the runner keeps one copy at ~/platterpus-rig/drivetest.sh")
    check("check: RESULT: with two reads at once, 1 of 2 stalled with Platterpus closed (one trial); repeating under strace to see where" in tl,
          "the check reports the stalled pair as one trial")
    check(tl.count("check (plain): stopped the leftover cyanrip read(s)") == 1,
          "the read that outlived its kill is found holding the drive and stopped")
    check(any(m.startswith("check (strace): pairB.txt.strace: last call: ") for m in tl),
          "the stalled pair is repeated under strace and its last call named")
    check("C2 probe: t5-c2-1.bin: frame 13 (3 bits)" in tl and "C2 probe: control-c2-1.bin: no C2 bit set in 26 frames" in tl,
          "the C2 probe names the flagged frame at track 5 and none at the control")
    guarded = [m for m in tl if m.startswith("probe guard: stopped the abandoned disc read, pid ")]
    check(len(guarded) == 3, f"the probe guard stops the abandoned read once in each of runs A, B, C ({len(guarded)})")
    for run_ in "ABC":
        check(any(m.startswith(f"Run {run_}: end, app exit 0, platterpus 0.7.121 (build 2ca5196); DONE") for m in tl),
              f"Run {run_} rips")
    check(any(m.startswith("WIPE THE DISC NOW") for m in tl) and "disc back; 1 seconds for it to settle" in tl,
          "the tray opens for the wipe and the stage goes on when the disc is back")
    check("phase 2: end, 6 of 6 track 9 reads saved" in tl, "phase 2 saves its six reads")
    check("no failures this stage" in tl, "no failure is recorded")
    s = sendfile(home)
    names = tarfile.open(s).getnames() if s else []
    check(s is not None and not any(n.endswith(".flac") for n in names), "one upload file, and no audio in it")
    for want in ("platterpus-rig/drivetest-r38/runs/runA-logs.tar.gz",
                 "platterpus-rig/drivetest-r38/earlier/drivemode/dumps/pioneer-f4.txt",
                 "platterpus-rig/drivetest-r38/MANIFEST.txt",
                 "platterpus-rig/drivetest-r38/kernel/stage1.txt",
                 ".local/share/platterpus/bundles/platterpusbundle20261105t2224310000.tar.gz"):
        check(want in names, f"the upload holds {want}")
    check(".local/share/platterpus/bundles/platterpusbundle20261104t125346z.tar.gz" not in names,
          "the upload leaves out a bundle older than the test")
    check(not stray(), "no stand-in ripper is left running")
    return home, stub, bin_


def case_restored(base, home, stub, bin_):
    script = home / "platterpus-rig/drivetest.sh"
    if not script.is_file():
        check(False, "stage 4 needs the copy stage 1 makes")
        return
    p = run(base, home, stub, bin_, ["4"], script=script)
    check(p.returncode == 0 and "restored: the drive's 256 settings bytes match the first read (pioneer-f4.txt)" in timeline(home),
          "stage 4: the settings put back match the first read")
    run(base, home, stub, bin_, ["redo", "restored"], script=script)
    run(base, home, stub, bin_, ["4"], script=script, extra={"F4_ALT": "1"})
    check("FAILED: restored: the drive's settings bytes DIFFER from the first read; compare pioneer-f4.txt with pioneer-f4-restored-2.txt" in timeline(home),
          "stage 4: settings not put back are a failure, naming both files")
    p = run(base, home, stub, bin_, ["c2"], script=script)
    tl = timeline(home)
    check(p.returncode == 0 and tl.count("C2 probe: t5-c2-1.bin: frame 13 (3 bits)") >= 2,
          "c2 alone runs the probe again, as round 38 lap 16 S9's fallback asks")
    c2_sends = list((home / "platterpus-rig/drivetest-r38/SEND").glob("drivetest-r38-c2-*.tar.gz"))
    check(len(c2_sends) == 1, f"c2 alone makes its own upload file ({len(c2_sends)})")


def case_empty_runs(base):
    home, stub, bin_ = build(base)
    p = run(base, home, stub, bin_, ["1"], extra={"STUB_ALWAYS_FAIL": "1"}, reinsert=True)
    tl = timeline(home)
    starts = [m for m in tl if m.startswith("Run ") and ": start (attempt " in m]
    check(p.returncode == 0, f"runs that rip nothing do not stop the stage (exit {p.returncode})")
    check([m[:20] for m in starts] == ["Run A: start (attemp", "Run A: start (attemp", "Run B: start (attemp", "Run B: start (attemp"],
          "Runs A and B are each retried once, and Run C never starts")
    check("FAILED: Run C: not started: the last two app runs ripped nothing, so this one would not either" in tl,
          "Run C's not starting is written down with why")
    check("phase 2: end, 6 of 6 track 9 reads saved" in tl, "phase 2 still runs")
    fails = (home / "platterpus-rig/drivetest-r38/FAILURES.txt").read_text(encoding="utf-8")
    check(fails.count("\n=== ") == 5 and "--- last 60 lines of platterpus-rig/drivetest-r38/app-output/runA.txt" in fails,
          "FAILURES.txt holds five entries, each run's with its output")
    check("FAILURE(S) THIS STAGE" in p.stdout, "the failures are printed at the end of the stage")


def case_app_open(base):
    home, stub, bin_ = build(base)
    app = subprocess.Popen(["bash", "-c", 'exec -a "$0" sleep 60', str(home / "Applications" / APP_NAME)])
    try:
        p = run(base, home, stub, bin_, ["1"])
    finally:
        app.kill()
        app.wait()
    tl = timeline(home)
    check(p.returncode == 1, f"Platterpus open stops stage 1 (exit {p.returncode})")
    check("FAILED: STOPPED: Platterpus is open: close it, then run the same command again" in tl,
          "the stop says why and what to do")
    s = sendfile(home)
    check(s is not None and "-stage1-stopped-" in s.name, "a stopped stage still makes its upload file")
    check(not any(m.startswith("check:") for m in tl), "nothing touches the drive before the stop")


def main():
    for tool in ("perl", "setsid", "pgrep", "pkill", "python3", "timeout"):
        if not shutil.which(tool):
            print(f"SKIP: {tool} is not installed")
            return 77
    base = pathlib.Path(tempfile.mkdtemp(prefix="drivetest-"))
    try:
        home, stub, bin_ = case_stage1(base / "s1")
        case_restored(base / "s1", home, stub, bin_)
        case_empty_runs(base / "empty")
        case_app_open(base / "open")
    finally:
        subprocess.run(["pkill", "-KILL", "-f", FAKE_RIPPER])
        shutil.rmtree(base, ignore_errors=True)
    print(f"{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    sys.exit(main())
