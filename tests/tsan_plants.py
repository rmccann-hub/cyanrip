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

"""The suppressions the TSan suite loads still let three handoff defects fail.

tests/tsan.supp drops reports by the function on the writing side, and its
header names three defects planted in the frame handoff (push_frame_to_encs()
and fifo_frame.c) that still fail with it, where the option it replaced,
ignore_noninstrumented_modules, hid every one. That was measured once, by
hand, on 2026-11-02. This makes it a test, so a suppression widened later, or
an option that hides FFmpeg's accesses again, fails here and not silently:

  write   the main thread writes a frame's samples after handing it over,
          against swr_convert() reading them (3 runs of 3 reported);
  struct  the encoders are given the frame itself, which the main thread then
          frees: a heap-use-after-free (3 of 3);
  buffer  the encoders are given the samples without a reference, so the main
          thread's unreference frees them early, and the block goes to a later
          frame while an encoder still reads it (13 of 13).

Each plant is built the way the build builds: the TSan build's own compile and
link commands, read with `ninja -t commands`, compile the planted copies of the
one or two files it changes into a scratch folder and link them with the
build's other objects, so the tree is not copied and nothing in the build
directory is written. Each binary then rips basic.cue to FLAC and MP3 at once,
under the TSAN_OPTIONS the suite's tsan setup gives every test, and must print
a ThreadSanitizer report. The unplanted binary rips the same first and must
print none, so a report is the plant's and not the environment's.

Registered only in a -Db_sanitize=thread build (CI's thread row). A plant whose
anchor is gone from the source fails, naming it: the plant then needs moving to
where the handoff now is, not deleting.

Usage: tsan_plants.py NINJA BUILD_DIR CYANRIP
"""

import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
FIXTURES = ROOT / "tests" / "fixtures"
REPORT = "WARNING: ThreadSanitizer:"

PLANT_CLONE = (
    "static AVFrame *plant_clone(const AVFrame *x)\n{\n"
    "    AVFrame *c = av_frame_alloc();\n    if (!c)\n        return NULL;\n"
    "    av_frame_copy_props(c, x);\n    c->format = x->format;\n"
    "    c->nb_samples = x->nb_samples;\n    c->sample_rate = x->sample_rate;\n"
    "    av_channel_layout_copy(&c->ch_layout, &x->ch_layout);\n"
    "    memcpy(c->data, x->data, sizeof(c->data));\n"
    "    memcpy(c->linesize, x->linesize, sizeof(c->linesize));\n"
    "    c->extended_data = c->data;\n    return c;\n}\n"
    "#define CLONE_FN(x)    ((x) ? plant_clone((x)) : NULL)")
CLONE = "#define CLONE_FN(x)    ((x) ? av_frame_clone((x)) : NULL)"

# name -> [(file, anchor, replacement)], each anchor exactly once in its file
PLANTS = {
    "write": [
        ("cyanrip_encode.c",
         "            return ret;\n        }\n    }\n\n    return 0;\n}\n",
         "            return ret;\n        }\n    }\n"
         "    if (frame && frame->nb_samples)\n"
         "        ((volatile uint8_t *)frame->data[0])[0] ^= 0;\n\n"
         "    return 0;\n}\n"),
    ],
    "struct": [
        ("fifo_frame.c", CLONE, "#define CLONE_FN(x)    (x)"),
        ("cyanrip_encode.c",
         "    ret = swr_convert_frame(ctx->swr, NULL, *input);\n\n"
         "    av_frame_free(input);\n",
         "    ret = swr_convert_frame(ctx->swr, NULL, *input);\n\n"
         "    *input = NULL;\n"),
    ],
    "buffer": [
        ("fifo_frame.c", CLONE, PLANT_CLONE),
    ],
}

failures = 0


def fail(msg):
    global failures
    failures += 1
    print(f"FAIL: {msg}")


def arg_after(tokens, flag):
    i = tokens.index(flag)
    return i + 1


def rip(binary, work, label):
    """Rip basic.cue to FLAC and MP3; return (exit, reports, first report)."""
    out = work / label
    out.mkdir()
    shutil.copy(FIXTURES / "basic.cue", out / "basic.cue")
    shutil.copy(FIXTURES / "cdda.bin", out / "basic.bin")
    r = subprocess.run([str(binary), "-d", "basic.cue", "-N", "-A", "-U",
                        "-s", "0", "-P", "0", "-o", "flac,mp3",
                        "-D", "out/{format}", "-F", "{track}", "-L", "log"],
                       cwd=out, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    lines = r.stderr.splitlines()
    reports = [n for n, line in enumerate(lines) if REPORT in line]
    first = ""
    if reports:
        n = reports[0]
        frames = [ln.split()[1] for ln in lines[n + 1:n + 12]
                  if ln.strip().startswith("#") and len(ln.split()) > 1][:3]
        first = lines[n].strip() + " | " + " < ".join(frames)
    return r.returncode, len(reports), first


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    ninja, build = sys.argv[1], pathlib.Path(sys.argv[2]).resolve()
    # meson passes a built target relative to the build directory
    binary = (build / sys.argv[3]).resolve()

    # The suppressions must be the ones the suite loads, or this probes nothing
    opts = os.environ.get("TSAN_OPTIONS", "")
    supp = [o.split("=", 1)[1] for o in opts.replace(":", " ").split()
            if o.startswith("suppressions=")]
    if not any(pathlib.Path(s).resolve() == (ROOT / "tests" / "tsan.supp")
               for s in supp):
        print(f"UNPROBED: TSAN_OPTIONS is {opts!r}, with no suppressions= "
              "naming tests/tsan.supp; the suite's tsan setup sets it")
        return 1

    target = os.path.relpath(binary, build)
    cmds = subprocess.run([ninja, "-C", str(build), "-t", "commands", target],
                          capture_output=True, text=True, encoding="utf-8",
                          check=True)
    commands = [shlex.split(c) for c in cmds.stdout.splitlines() if c.strip()]
    link = [t for t in commands if "-o" in t and t[arg_after(t, "-o")] == target]
    if len(link) != 1:
        fail(f"expected one link command for {target}, found {len(link)}")
        return 1
    link = link[0]
    compiles = {}
    for t in commands:
        if "-c" in t and "-o" in t:
            source = (build / t[arg_after(t, "-c")]).resolve()
            if source.parent == SRC:
                compiles[source.name] = t
    files = {f for edits in PLANTS.values() for f, _, _ in edits}
    for f in sorted(files - set(compiles)):
        fail(f"no compile command for src/{f} in the build")
    if failures:
        return 1

    work = pathlib.Path(tempfile.mkdtemp(prefix="tsan-plants-"))
    try:
        code, reports, first = rip(binary, work, "unplanted")
        print(f"unplanted: exit {code}, {reports} TSan report(s)")
        if code != 0 or reports:
            fail(f"the unplanted build exits {code} with {reports} TSan "
                 f"report(s), so a plant's report would prove nothing: {first}")
            return 1

        for name, edits in PLANTS.items():
            pdir = work / f"plant-{name}"
            pdir.mkdir()
            texts = {}
            for f, anchor, new in edits:
                text = texts.get(f) or (SRC / f).read_text(encoding="utf-8")
                count = text.count(anchor)
                if count != 1:
                    fail(f"plant {name}: its anchor is in src/{f} {count} "
                         "times, not once; move the plant to where the "
                         "handoff now is")
                    break
                texts[f] = text.replace(anchor, new)
            else:
                objects = {}
                for f, text in texts.items():
                    (pdir / f).write_text(text, encoding="utf-8")
                    t = list(compiles[f])
                    obj = t[arg_after(t, "-o")]
                    mine = str(pdir / (f + ".o"))
                    t[arg_after(t, "-c")] = str(pdir / f)
                    t[arg_after(t, "-o")] = mine
                    if "-MQ" in t:
                        t[arg_after(t, "-MQ")] = mine
                    if "-MF" in t:
                        t[arg_after(t, "-MF")] = mine + ".d"
                    r = subprocess.run(t, cwd=build, capture_output=True,
                                       text=True, encoding="utf-8",
                                       errors="replace")
                    if r.returncode:
                        fail(f"plant {name}: src/{f} did not compile:\n"
                             + r.stderr[-2000:])
                        break
                    objects[obj] = mine
                else:
                    t = [objects.get(tok, tok) for tok in link]
                    planted = pdir / "cyanrip"
                    t[arg_after(t, "-o")] = str(planted)
                    r = subprocess.run(t, cwd=build, capture_output=True,
                                       text=True, encoding="utf-8",
                                       errors="replace")
                    if r.returncode:
                        fail(f"plant {name}: did not link:\n" + r.stderr[-2000:])
                        continue
                    code, reports, first = rip(planted, work, name)
                    print(f"plant {name}: exit {code}, {reports} TSan "
                          f"report(s); {first}")
                    if not reports:
                        fail(f"plant {name} ripped with no TSan report: the "
                             "suppressions or options now hide it")
    finally:
        shutil.rmtree(work, ignore_errors=True)

    if failures:
        return 1
    print(f"ok: {len(PLANTS)} planted handoff defects each reported under "
          "the suite's TSan options, and the unplanted build reported none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
