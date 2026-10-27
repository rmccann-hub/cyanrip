#!/usr/bin/env python3
"""Personal details stay out of what the filing and export tools write.

The owner's rule of 2026-10-12: home-folder paths become ~, the hostname
becomes host, and the owner's real name is not written, in new evidence and
laps, through the export or filing tools; the shared protocol's wire values
are left as they are. tools/redact.py is the one implementation;
tools/ingest-bundle.py applies it to what it files and tools/rig-check.py to
what it writes. Each case below is one way that could be wrong.

The names and hosts here are invented. A test that needed the owner's real
details to run would be the thing the rule forbids.

Usage: redaction.py <cyanrip binary>
"""

import hashlib
import importlib.util
import io
import os
import pathlib
import re
import socket
import subprocess
import sys
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import redact  # noqa: E402

CRIP = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "build" / "src" / "cyanrip")
failures = 0


def check(cond, msg):
    global failures
    if not cond:
        failures += 1
        print(f"FAIL: {msg}")


def sha(b):
    return hashlib.sha256(b).hexdigest()


NAME = "Alice Example"
HOST = "workstation-07.lan"
WIRE = "HANDSHAKE-READY-TO-READ: yes — operator (alice), /home/alice\n"

# ---- 1. redact() itself -------------------------------------------------
TEXT = (f"host:            Linux {HOST} 6.1.0-x #1 SMP\n"
        "appimage: /var/home/alice/Applications/p.AppImage\n"
        "rips in /home/alice/Music and /Users/alice/Desktop\n"
        "C:\\Users\\alice\\Music\n"
        f"reviewed on workstation-07 by {NAME}\n"
        + WIRE +
        "/mnt/home/data, workstation-07-backup, http://localhost:8080\n")
new, rep = redact.redact(TEXT, names=[NAME])
check("alice" not in "".join(l for l in new.splitlines(True) if not l.startswith("HANDSHAKE-")),
      f"a home folder's owner survived:\n{new}")
check("~/Applications/p.AppImage" in new and "~/Music" in new
      and "~/Desktop" in new and "~\\Music" in new,
      f"what follows a home folder must be kept:\n{new}")
check("Linux host 6.1.0" in new and "reviewed on host by" in new,
      f"the hostname, and its short form elsewhere, must become host:\n{new}")
check("workstation-07-backup" in new,
      "a longer word that starts with the hostname is not the hostname")
check("/mnt/home/data" in new, "/home under another directory is no home folder")
check("localhost" in new, "localhost identifies nobody and stays")
check(f"by {redact.PLACEHOLDER_NAME}" in new and NAME not in new,
      f"the name from the local list must be replaced:\n{new}")
check(WIRE in new, "a HANDSHAKE- wire line must be left exactly as it was")
check(rep.wire_lines_kept == 1 and "1 HANDSHAKE- line(s) left" in rep.summary(),
      f"the kept wire line must be counted: {rep.summary()}")

_, rep = redact.redact(TEXT, names=None)
check(not rep.names_checked and "names not checked" in rep.summary(),
      f"with no local list the report must say the name was not checked, not "
      f"that there was none: {rep.summary()}")

# A JSON string spells a newline as the two characters backslash and n, so a
# path, hostname or name that starts a line inside one follows the letter n,
# and a boundary that reads n as part of a longer word lets it through.
# Platterpus's export kept a username that way (their round 35 lap 18 S9),
# and every boundary here had the same shape (S10).
JSON = (r'{"log": "start\n/home/alice/Music\nC:\\Users\\alice\\x\n'
        r'workstation-07 ripped\tAlice Example\r/Users/alice/y"}' "\n")
jnew, _ = redact.redact(JSON, hosts=[HOST], names=[NAME])
check("alice" not in jnew,
      f"a home folder after a JSON escape survived:\n{jnew}")
check("workstation-07" not in jnew,
      f"a hostname after a JSON escape survived:\n{jnew}")
check(NAME not in jnew,
      f"the owner's name after a JSON escape survived:\n{jnew}")
check(r"\n~/Music\n" in jnew and r"\r~/y" in jnew,
      f"the escape before a replaced path must be kept:\n{jnew}")
jfound = {k.split(" '")[0] for _, k in redact.findings(JSON, [NAME])}
check("home path" in jfound and "the owner's name" in jfound,
      f"findings() must see what follows a JSON escape: {jfound}")

same, rep = redact.redact_bytes(b"\xff\xfe binary /home/alice", names=None)
check(same == b"\xff\xfe binary /home/alice" and not rep.changed(),
      "bytes that are not UTF-8 are not rewritten")

found = redact.findings(TEXT, [NAME])
kinds = {k.split(" '")[0] for _, k in found}
check({"home path", "a hostname", "the owner's name"} <= kinds,
      f"findings() must see every kind: {found}")
check(not any(i == 6 for i, _ in found),
      f"findings() must skip the wire line: {found}")
check(not any(NAME in k for _, k in found),
      "findings() must not write the name it found")

# Review C 1.4: an AcoustID key in a log an older build wrote, bare, quoted
# or JSON-escaped, is withheld; one already withheld is left alone
for given, want in (
        ("Invoked as:     cyanrip --acoustid-key AbC123 -o flac",
         "Invoked as:     cyanrip --acoustid-key [withheld] -o flac"),
        ('Invoked as:     cyanrip --acoustid-key "a b" -N',
         "Invoked as:     cyanrip --acoustid-key [withheld] -N"),
        ('  "invocation": "cyanrip --acoustid-key \\"a b\\" -o flac",',
         '  "invocation": "cyanrip --acoustid-key [withheld] -o flac",'),
        ("Invoked as:     cyanrip --acoustid-kye AbC123 -N",
         "Invoked as:     cyanrip --acoustid-kye [withheld] -N"),
        ("Invoked as:     cyanrip --AcoustID-Key=AbC123 -N",
         "Invoked as:     cyanrip --AcoustID-Key=[withheld] -N"),
        ('Invoked as:     cyanrip "--acoustid-key=a b" -N',
         'Invoked as:     cyanrip "--acoustid-key=[withheld]" -N'),
        ('  "invocation": "cyanrip \\"--acoustid-key=a b\\" -N",',
         '  "invocation": "cyanrip \\"--acoustid-key=[withheld]\\" -N",')):
    got, rep = redact.redact(given)
    check(got == want and rep.keys == 1 and rep.changed()
          and "1 AcoustID key(s)" in rep.summary(),
          f"the key must be withheld: {given!r} -> {got!r}")
    check([k for _, k in redact.findings(given)] == ["an AcoustID key"],
          f"findings() must see the key in {given!r}")
    check(redact.findings(got) == [],
          f"findings() must not see a withheld key: {got!r}")
for done in ("cyanrip --acoustid-key [withheld] -N",
             "cyanrip --acoustid-key=[withheld] -N",
             'cyanrip "--acoustid-key=[withheld]" -N'):
    _, rep = redact.redact(done)
    check(rep.keys == 0 and not rep.changed(),
          f"a withheld key is not withheld again: {done!r}")
same, rep = redact.redact("cyanrip -k 10 -N")
check(same == "cyanrip -k 10 -N" and rep.keys == 0,
      "-k is left alone: it was --stall-secs until 2026-10-12")

with tempfile.TemporaryDirectory() as d:
    p = pathlib.Path(d) / "names"
    p.write_text("# a comment\n\n" + NAME + "\n", encoding="utf-8")
    check(redact.local_names(p) == [NAME], "the local list reads one name a line")
    check(redact.local_names(pathlib.Path(d) / "absent") is None,
          "no list is None, not an empty list")

# ---- 2. tools/ingest-bundle.py ------------------------------------------
golden = (ROOT / "docs" / "golden-reference.log").read_bytes()
check(b"/home/" in golden and b"Log FUN512: " in golden,
      "the golden reference must be a signed log with a home path in it, or "
      "the -Y case below tests nothing")
tampered = golden.replace(b"Ripping errors: 0", b"Ripping errors: 9", 1)
check(tampered != golden, "the tampering did not land")

files = {
    "session/MANIFEST.txt": (f"host:            Linux {HOST} 6.1.0-x #1 SMP\n"
                             "appimage:        /var/home/alice/Applications/p.AppImage\n").encode(),
    "session/transcript.txt": (b"[  OK  ] copied to /home/alice/rips\n"
                               b"[  OK  ] on workstation-07\n"
                               + f"[  OK  ] reviewed by {NAME}\n".encode()),
    "session/report.json": b'{"ok": true, "dir": "/var/home/alice/x"}',
    "session/lap.md": (WIRE + "and /home/alice/y\n").encode(),
    "album/good/good.log": golden,
    "album/bad/bad.log": tampered,
}


def make(members):
    d = pathlib.Path(tempfile.mkdtemp())
    p = d / "bundle.tar.gz"
    with tarfile.open(p, "w:gz") as tf:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return p


def ingest(archive, into, names):
    env = dict(os.environ, **{redact.NAMES_ENV: str(names)})
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "ingest-bundle.py"),
                        str(archive), "--into", str(into), "--cyanrip", CRIP],
                       capture_output=True, text=True, timeout=120, env=env, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


with tempfile.TemporaryDirectory() as d:
    d = pathlib.Path(d)
    names = d / "names"
    names.write_text(NAME + "\n", encoding="utf-8")
    rc, out = ingest(make(files), d / "filed", names)
    filed = d / "filed"
    sums = (filed / "SHA256SUMS").read_text(encoding="utf-8")
    for name in files:
        f = filed / name
        if not f.exists():
            check(False, f"{name} was not filed")
            continue
        body = f.read_bytes()
        rest = b"".join(l for l in body.splitlines(True)
                        if not l.startswith(b"HANDSHAKE-"))
        check(b"/home/alice" not in rest and b"/var/home/" not in rest
              and b"/home/user/" not in rest,
              f"{name}: a home path was filed")
        check(b"workstation-07" not in body, f"{name}: the hostname was filed")
        check(NAME.encode() not in body, f"{name}: the owner's name was filed")
        check(f"{sha(body)}  {name}\n" in sums,
              f"{name}: SHA256SUMS does not give the hash of the file as filed")
        if body != files[name]:
            check(f"the bundle's bytes were {sha(files[name])}" in sums,
                  f"{name}: a redacted file's original hash is not recorded")
    check(WIRE.encode() in (filed / "session/lap.md").read_bytes(),
          "the wire line must be filed exactly as delivered")

    def verdict_for(name):
        lines = sums.splitlines()
        for i, l in enumerate(lines):
            if l.endswith(f"  {name}"):
                for k in lines[i + 1:i + 3]:
                    m = re.match(r"#   -Y on the bundle's bytes, before "
                                 r"redaction: (.*)$", k)
                    if m:
                        return m.group(1)
        return None

    if pathlib.Path(CRIP).is_file():
        check(verdict_for("album/good/good.log") == "verifies",
              f"the real signed log must verify before redaction: "
              f"{verdict_for('album/good/good.log')!r}\n{sums}")
        check((verdict_for("album/bad/bad.log") or "").startswith("does NOT verify"),
              f"a tampered log must not: {verdict_for('album/bad/bad.log')!r}")
    else:
        print(f"UNPROBED: no cyanrip binary at {CRIP}, so -Y was not run")
    check("THE OWNER'S NAME WAS NOT CHECKED" not in out,
          "with a list given, the name was checked")

    rc, out = ingest(make({"session/transcript.txt": b"[  OK  ] fine\n"}),
                     d / "filed2", d / "no-such-list")
    check("THE OWNER'S NAME WAS NOT CHECKED" in out,
          f"with no list, the run must say the name was not checked:\n{out[-800:]}")

# ---- 3. tools/rig-check.py writes through the same rule -----------------
spec = importlib.util.spec_from_file_location("rig_check", ROOT / "tools" / "rig-check.py")
rc_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc_mod)
home, hostname = str(pathlib.Path.home()), socket.gethostname()
with tempfile.TemporaryDirectory() as d:
    rc_mod.save(pathlib.Path(d), "out.txt",
                f"binary {home}/.local/bin/cyanrip on {hostname}\n")
    got = (pathlib.Path(d) / "out.txt").read_text(encoding="utf-8")
check(home not in got and "~/.local/bin/cyanrip" in got,
      f"rig-check must write its own home as ~: {got!r}")
if hostname and hostname.lower() not in ("host",):
    check(f" on {redact.PLACEHOLDER_HOST}\n" in got,
          f"rig-check must write its own hostname as host: {got!r}")

if failures:
    print(f"{failures} check(s) failed")
    sys.exit(1)
print("redaction: home folders, hostnames and the owner's name stay out of "
      "what is filed and exported, and wire values stay as they are")
