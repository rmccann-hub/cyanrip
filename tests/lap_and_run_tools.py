#!/usr/bin/env python3
#
# This file is part of cyanrip.
#
# cyanrip is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# cyanrip is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with cyanrip; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""tools/take-in-lap.py and tools/read-run.py, on records built here.

take-in-lap's refusals are what make it safe to run: a held lap, a lap whose
bytes differ from the announcement, and an inbound file it would overwrite
must each stop it before anything is written. Each is asserted against a
peer repository built here, so no network and no real record is touched.

read-run judges nothing, so what it must get right is what it reports. Its
sections were written after a hand reading of the 2026-10-13 run missed a
second securing pass and a pregap one list left out, so each is asserted on a
log built to carry exactly that.
"""

import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Meson passes the binary relative to the build directory, and the tools
# run from the source root, so it is resolved here, where it was given.
CRIP = str(pathlib.Path(sys.argv[1]).resolve()) if len(sys.argv) > 1 else None
fails = 0


def check(ok, msg):
    global fails
    if ok:
        print(f"ok   {msg}")
    else:
        print(f"FAIL: {msg}")
        fails += 1


def run(*args, cwd=ROOT):
    r = subprocess.run([sys.executable, *map(str, args)], capture_output=True,
                       text=True, cwd=cwd, env={"PYTHONDONTWRITEBYTECODE": "1",
                                                "PATH": "/usr/bin:/bin"})
    return r.returncode, r.stdout + r.stderr


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t",
                    "-c", "user.email=t@t", *args], check=True,
                   capture_output=True)


def lap(ready, rnd=99, number=2):
    return (f"HANDSHAKE-PROTOCOL: 8\nHANDSHAKE-ROUND: {rnd}\n"
            f"HANDSHAKE-LAP: {number}\nHANDSHAKE-FROM: platterpus\n"
            f"HANDSHAKE-VERDICT: OPEN\nHANDSHAKE-READY-TO-READ: {ready}\n"
            f"HANDSHAKE-NEXT-LAP: 3 (yours): your answer\n\n# a lap\n")


def take_in(tmp):
    up, peer, laps = tmp / "up", tmp / "peer", tmp / "laps"
    out = up / "docs" / "handshake" / "outbound"
    out.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(up)], check=True)
    name = "round-99-lap-02.md"
    (out / name).write_text(lap("no — published, NOT yet released"))
    git(up, "add", "-A")
    git(up, "commit", "-q", "-m", "held")
    subprocess.run(["git", "clone", "-q", str(up), str(peer)], check=True)
    (laps / "inbound").mkdir(parents=True)
    tool = ROOT / "tools" / "take-in-lap.py"
    base = [tool, "99", "2", "--peer", peer, "--laps", laps]
    dest = laps / "inbound" / name

    rc, o = run(*base, "--file")
    check(rc != 0 and "FAIL  released for reading" in o and not dest.exists(),
          "a held lap is refused and not filed")

    (out / name).write_text(lap("yes — operator, 2026-10-13"))
    git(up, "commit", "-q", "-am", "released")
    released = (out / name).read_bytes()

    rc, o = run(*base, "--sha256", "0" * 64, "--file")
    check(rc != 0 and "REFUSED before filing" in o and not dest.exists(),
          "a lap whose sha256 differs from the announcement is not filed")
    rc, o = run(*base, "--bytes", str(len(released) + 1), "--file")
    check(rc != 0 and not dest.exists(),
          "a lap whose size differs from the announcement is not filed")

    rc, o = run(*base, "--file")
    check(dest.exists() and dest.read_bytes() == released
          and "filed byte for byte" in o,
          "a released lap is filed byte for byte")

    dest.write_bytes(released + b"edited\n")
    rc, o = run(*base, "--file")
    check(rc != 0 and "WITH DIFFERENT BYTES" in o
          and dest.read_bytes() == released + b"edited\n",
          "an inbound file with other bytes is refused, not overwritten")

    (out / "round-99-lap-04.md").write_text(lap("yes — operator", number=3))
    git(up, "add", "-A")
    git(up, "commit", "-q", "-m", "misnamed")
    rc, o = run(tool, "99", "4", "--peer", peer, "--laps", laps)
    check(rc != 0 and "FAIL  it declares the round and lap its name says" in o,
          "a lap whose header disagrees with its name fails")


BANNER = "cyanrip 0.9.4-rc2+platterpus.99 (platterpus-fork-g1234567)\n"


def log(invoked, gaps, body, footer="Rip completed:  yes (1 of 3 tracks)\n"):
    return (BANNER + f"Invoked as:     cyanrip {invoked}\n"
            "Consumer:       platterpus/9.9.9\n"
            "Gaps:\n" + "".join(f"    {g}\n" for g in gaps) + "\nTracks:\n"
            + body + "Ripping errors: 0\n" + footer + "Log FUN512: x\n")


def read_run(tmp):
    run_dir = tmp / "docs" / "rig-2026-01-02-1234567"
    album = run_dir / "album"
    full = ["160 frame pregap in track 2, merging into track 1",
            "158 frame pregap in track 3, merging into track 2"]
    (album / "a").mkdir(parents=True)
    (album / "a" / "a.log").write_text(log(
        "-d /dev/sr0 -Z 2 --diagnostics rec-a.json", full,
        "Repeating ripping (0 out of 2 matches for current checksum 11111111)\n"
        "Repeating ripping (0 out of 2 matches for current checksum 22222222)\n"
        "\nDone; (repeat limit of 3 reads reached; at most 1 read agreed; "
        "last read 33333333, not kept)\nTrack 1 read with errors.\n"
        "  Secure re-read:  did NOT converge after 3 reads (repeat limit hit)\n"))
    (album / "a" / "a.platterpus-securing-pass.txt").write_text(log(
        "-d /dev/sr0 -Z 2 -l 1 --diagnostics rec-b.json", full[:1],
        "\nDone; (repeat limit of 3 reads reached; at most 1 read agreed)\n"
        "Track 1 read with errors.\n"))
    (album / "a" / "a (EAC-compatible).log").write_text(BANNER + "not ours\n")
    (run_dir / "SHA256SUMS").write_text(
        f"{'0' * 64}  (not filed) ripperdiagnostics/rec-a.json\n")
    if CRIP:
        (album / "g").mkdir()
        shutil.copy(ROOT / "docs" / "golden-reference.log", album / "g" / "g.log")
    rc, o = run(ROOT / "tools" / "read-run.py", run_dir,
                *(["--cyanrip", CRIP] if CRIP else []))
    check(rc == 0, f"read-run exits 0 on a filed session (exit {rc})")
    check(f"LOGS -- {3 if CRIP else 2} cyanrip log(s)" in o,
          "a securing pass's log counts as a log, an EAC rendering does not")
    check("clause naming a last read not kept: PRINTED" in o
          and "clause naming a last read not kept: not printed" in o,
          "each repeat-limit Done; line says whether the clause printed")
    check("track 3's pregap is in 1 list(s) and absent from 1" in o,
          "a pregap one list gives and another leaves out is reported")
    check("rec-a.json in the bundle" in o and "rec-b.json NOT IN THE BUNDLE" in o,
          "each log's --diagnostics record is looked up in the bundle")
    if CRIP:
        check("-Y:         verifies" in o and "DOES NOT VERIFY" in o,
              "-Y is run on every log, and a log that does not verify says so")
    else:
        print(f"UNPROBED: no cyanrip binary given, so -Y was not run")


def main():
    with tempfile.TemporaryDirectory() as d:
        take_in(pathlib.Path(d) / "take")
    with tempfile.TemporaryDirectory() as d:
        read_run(pathlib.Path(d))
    if fails:
        print(f"{fails} check(s) failed")
        return 1
    print("lap intake and run reader: every check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
