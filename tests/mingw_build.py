#!/usr/bin/env python3
"""The Windows build script stops where it fails (review C item 4.6).

.github/mingw-build.sh runs only under MSYS2 in CI, and a step that failed
there without stopping the script was found only by reading a log afterwards
(build_neon's comment). This sources its functions in Bash, replaces the
library builds and pkg-config with stubs, and checks each guard 4.6 added:

  * strict mode (-e, -u and pipefail) is on once the script is sourced;
  * a library that fails to build stops buildCyanrip before cyanrip is built
    and before the cache stamp is written, and a run where all succeed does
    both;
  * a curl without HTTPS stops it before cyanrip is built;
  * hiding shared libraries succeeds with none to hide and with one of its two
    directories absent, and hides only those with a static twin;
  * cyan_hide_files succeeds when the last file it is given is absent;
  * an empty build directory or library name stops cyan_do_vcs before its rm,
    which would otherwise remove a folder of that name where the script ran.

Nothing here is fetched or compiled. The script runs under MSYS2's GNU Bash
and xargs, so without Bash 4.4 or later and GNU xargs this exits 77, skipped.
"""

import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / ".github" / "mingw-build.sh"
LIBS = ("build_curl", "build_neon", "build_libmusicbrainz",
        "build_libqrencode", "build_ffmpeg")

failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


def bash(snippet, tmp, **env):
    """Run snippet in a Bash that has sourced the script, in tmp."""
    full = dict(os.environ, SCRIPT=str(SCRIPT), T=str(tmp),
                MINGW_PREFIX=str(tmp / "prefix"),
                MINGW_CHOST="x86_64-w64-mingw32", **env)
    return subprocess.run(["bash", "-c", 'source "$SCRIPT"\n' + snippet],
                          cwd=tmp, env=full, capture_output=True, text=True,
                          encoding="utf-8", timeout=60)


try:
    ver = subprocess.run(["bash", "-c", 'echo "${BASH_VERSINFO[0]} ${BASH_VERSINFO[1]}"'],
                         capture_output=True, text=True, encoding="utf-8",
                         timeout=30).stdout
except (OSError, subprocess.SubprocessError):
    ver = ""
parts = ver.split()
if len(parts) != 2 or (int(parts[0]), int(parts[1])) < (4, 4):
    print(f"SKIP: needs Bash 4.4 or later, as MSYS2 has; found {ver.strip() or 'none'}")
    sys.exit(77)
try:
    xargs = subprocess.run(["xargs", "--version"], capture_output=True,
                           text=True, encoding="utf-8", timeout=30).stdout
except (OSError, subprocess.SubprocessError):
    xargs = ""
if "GNU findutils" not in xargs:
    print("SKIP: needs GNU xargs (-r, -i), as MSYS2 has")
    sys.exit(77)

# The stubs buildCyanrip calls. LAME stands for whichever library fails.
STUBS = ('cyan_prepare() { CYANRIPINSTALLDIR=$T/inst; mkdir -p "$CYANRIPINSTALLDIR"; }\n'
         'build_lame() { echo "lame-3.100: stub"; return "${LAME_STATUS}"; }\n'
         + "".join(f"{f}() {{ echo ran-{f}; }}\n" for f in LIBS)
         + 'pkg-config() { echo "$PROTOCOLS"; }\n'
         'build_cyanrip() { echo ran-build_cyanrip; }\n'
         'buildCyanrip\n'
         'echo finished\n')

with tempfile.TemporaryDirectory(prefix="cyanrip-mingw-") as d:
    tmp = pathlib.Path(d)

    # Strict mode, read from the shell that sourced the script
    r = bash('echo "flags=$-"; shopt -qo pipefail && echo pipefail', tmp)
    flags = next((ln[6:] for ln in r.stdout.splitlines() if ln.startswith("flags=")), "")
    if r.returncode or "e" not in flags or "u" not in flags or "pipefail" not in r.stdout:
        fail(f"strict mode is not on once sourced: flags {flags!r}, "
             f"pipefail {'pipefail' in r.stdout} (exit {r.returncode})")

    # A failed library stops the build
    stamp = tmp / "inst" / ".libs-built"
    r = bash(STUBS, tmp, LAME_STATUS="1", PROTOCOLS="FILE HTTP HTTPS")
    if r.returncode != 1:
        fail(f"a failed library: exit {r.returncode}, expected 1")
    for ran in ("ran-build_curl", "ran-build_cyanrip", "finished"):
        if ran in r.stdout:
            fail(f"a failed library: {ran} printed, so the build went on")
    if "lame-3.100: stub" not in r.stdout:
        fail("a failed library: its own line is missing, so the stub never ran")
    if "A library failed to build" not in r.stderr:
        fail(f"a failed library is not named on stderr: {r.stderr!r}")
    if stamp.exists():
        fail("a failed library: the cache stamp was written")

    # All succeed: each runs, in order, then the stamp and cyanrip
    r = bash(STUBS, tmp, LAME_STATUS="0", PROTOCOLS="FILE HTTP HTTPS")
    ran = [ln for ln in r.stdout.splitlines() if ln.startswith("ran-")]
    want = [f"ran-{f}" for f in LIBS] + ["ran-build_cyanrip"]
    if r.returncode != 0 or ran != want or "finished" not in r.stdout:
        fail(f"every library built: exit {r.returncode}, ran {ran}, "
             f"expected {want}; stderr {r.stderr!r}")
    if not stamp.exists():
        fail("every library built: no cache stamp")

    # A curl without HTTPS stops before cyanrip, the cache restored
    r = bash(STUBS, tmp, LAME_STATUS="0", PROTOCOLS="DICT FILE HTTP")
    if r.returncode != 1 or "ran-build_cyanrip" in r.stdout:
        fail(f"a curl without HTTPS: exit {r.returncode}, cyanrip built "
             f"{'ran-build_cyanrip' in r.stdout}")
    if "curl was built without HTTPS: DICT FILE HTTP" not in r.stderr:
        fail(f"a curl without HTTPS is not named on stderr: {r.stderr!r}")
    if "restored from the cache" not in r.stdout:
        fail("a curl without HTTPS: the run did not take the cached path")

    # Shared libraries: none to hide, and the chost directory absent
    lib = tmp / "prefix" / "lib"
    lib.mkdir(parents=True)
    r = bash("cyan_do_hide_all_sharedlibs\necho finished", tmp)
    if r.returncode != 0 or "finished" not in r.stdout:
        fail(f"no shared library to hide: exit {r.returncode}, stderr {r.stderr!r}")

    # One with its static twin is hidden, one without is left
    for name in ("libfoo.dll.a", "libfoo.a", "libbar.dll.a"):
        (lib / name).write_bytes(b"")
    r = bash("cyan_do_hide_all_sharedlibs\necho finished", tmp)
    left = sorted(p.name for p in lib.iterdir())
    if r.returncode != 0 or left != ["libbar.dll.a", "libfoo.a", "libfoo.dll.a.dyn"]:
        fail(f"hiding a shared library: exit {r.returncode}, left {left}")

    # The last file absent
    (tmp / "present.a").write_bytes(b"")
    r = bash('cyan_hide_files "$T/present.a" "$T/absent.a"\necho finished', tmp)
    if r.returncode != 0 or "finished" not in r.stdout:
        fail(f"cyan_hide_files with its last file absent: exit {r.returncode}")
    if not (tmp / "present.a.bak").exists():
        fail("cyan_hide_files did not hide the file that was there")

    # An empty build directory, with a folder of the library's name here.
    # git is a stub, so nothing is fetched whatever happens.
    work = tmp / "work"
    (work / "curl").mkdir(parents=True)
    (work / "curl" / "keep").write_bytes(b"")
    vcs = ('git() { echo "git $*"; }\n'
           'cd "$T/work"\n'
           'cyan_do_vcs "https://github.com/curl/curl.git" "$C" test\n'
           'echo finished')
    r = bash(vcs, tmp, CYANRIPBUILDDIR="", C="0" * 40)
    if r.returncode == 0 or "finished" in r.stdout:
        fail(f"an empty build directory: exit {r.returncode}, the call went on")
    if "CYANRIPBUILDDIR" not in r.stderr:
        fail(f"an empty build directory is not named on stderr: {r.stderr!r}")
    if not (work / "curl" / "keep").exists():
        fail("an empty build directory: a folder of the library's name was removed")

    # An empty library name
    (tmp / "build").mkdir()
    r = bash('git() { echo "git $*"; }\ncyan_do_vcs "" "$C" test\necho finished',
             tmp, CYANRIPBUILDDIR=str(tmp / "build"), C="0" * 40)
    if r.returncode == 0 or "finished" in r.stdout or "vcsFolder" not in r.stderr:
        fail(f"an empty library name: exit {r.returncode}, stderr {r.stderr!r}")

if failures:
    print(f"{failures} failure(s)")
    sys.exit(1)
print("mingw-build.sh: strict mode, a failed library, no HTTPS, the hides and "
      "the empty names all stop or pass as they should")
