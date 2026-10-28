#!/usr/bin/env python3
"""Keep personal details out of what is committed: one implementation, used by
the tools that file evidence and export it.

THE RULE, the owner's, 2026-10-12, word for word:

    "From now on, keep personal details out of anything newly committed:
    home-folder paths become ~, the hostname becomes host, and the owner's
    real name isn't written. Apply this to new evidence and laps, through the
    export or filing tools rather than by hand. Leave the shared protocol
    document's wire values as they are unless both sides agree to change them.
    History stays as it is."

So this module is called by tools/ingest-bundle.py when it files a bundle and
by tools/rig-check.py when it writes its outputs, and tests/personal_details.py
checks what is newly committed. Nothing here touches a file already in the
repository.

WHAT IT REPLACES, and how each is known rather than guessed:

  * A HOME-FOLDER PATH -- `/home/<name>`, `/var/home/<name>` (an rpm-ostree
    system's real home, which the rig is), `/Users/<name>`, and
    `C:\\Users\\<name>` -- becomes `~`, with whatever follows it kept. The
    shape is the evidence: no list of user names is needed, so none is
    written anywhere.
  * A HOSTNAME becomes `host`. A hostname is not recognisable by its shape,
    so it is read from the material itself -- the second field of a
    `uname -a` line (`Linux <host> <release>`), and `host:`/`hostname:`
    fields -- plus any the caller knows exactly, as rig-check does from
    socket.gethostname(). It is never taken from a list in this repository:
    a list of the owner's hostnames would be the thing the rule forbids.
    Each is replaced as a whole word, case and all, with its short form
    before the first dot too.
  * THE OWNER'S REAL NAME becomes `the owner`, and only from a list kept
    OUTSIDE the repository: the file named by $CYANRIP_REDACT_NAMES, else
    ~/.config/cyanrip/redact-names, one name per line. Without one the name
    cannot be checked, and the report says exactly that: `unknown` and `none
    found` are different claims.

WHAT IT LEAVES ALONE: a line that begins `HANDSHAKE-` is a wire value of the
shared protocol (`HANDSHAKE-READY-TO-READ: yes -- operator (...)`), and the
rule leaves those as they are unless both sides agree. Such a line is copied
unchanged, whatever it holds, and counted so a reader can see it was skipped.

A redacted file is no longer the bytes that were delivered, so whoever calls
this must record both hashes. A cyanrip log also stops verifying with -Y once
a path inside it changes; tools/ingest-bundle.py runs -Y on the original
first and records the verdict.
"""

import os
import pathlib
import re

# A value can follow a JSON escape, which spells a newline as backslash and
# n: the n is then no part of a longer word, so each boundary below also
# accepts an escape before it. Platterpus's export kept a username after one
# (their round 35 lap 18 S9), and every boundary here had the same shape (S10).
AFTER_ESCAPE = r"(?<=\\[nrtbf])"

HOME_PATH = re.compile(
    r"(?:(?<![\w.~-])|" + AFTER_ESCAPE + r")(?:/var)?/home/[^/\s\"'<>|:;,)\]]+"
    r"|(?:(?<![\w.~-])|" + AFTER_ESCAPE + r")/Users/[^/\s\"'<>|:;,)\]]+"
    r"|(?:\b|" + AFTER_ESCAPE + r")[A-Za-z]:\\\\?Users\\\\?[^\\\s\"'<>|:;,)\]]+")

# `Linux <host> <release>` from `uname -a`, and a `host:`/`hostname:` field.
UNAME = re.compile(r"\b(?:Linux|Darwin|FreeBSD)\s+([A-Za-z0-9][A-Za-z0-9._-]*)"
                   r"\s+\d+\.\d+")
HOST_FIELD = re.compile(r"^\s*\"?(?:host|hostname|node)\"?\s*[:=]\s*\"?"
                        r"([A-Za-z0-9][A-Za-z0-9._-]*)\"?\s*$",
                        re.M | re.I)

WIRE = re.compile(r"^HANDSHAKE-[A-Z0-9-]+:")

# An AcoustID key given on the command line, as `Invoked as:` and the
# diagnostics record's `invocation` print it, bare or quoted. cyanrip withholds
# it itself once review C item 1.4 is fixed; this is the second line, for a log
# an older build wrote. Already withheld is not matched again. Any spelling of
# the flag, in any case, as the binary withholds it: a misspelt one genopt
# refused, and the `--flag=value` form, quoted whole when the value has a
# space. Not upstream's -k, which the binary also withholds after: in a log
# from before 2026-10-12 it was --stall-secs, and its value no secret.
ACOUSTID_KEYS = (
    re.compile(r'((?:\\"|")--(?i:acoustid)[\w-]*=)(?!\[withheld\])'
               r'((?:(?!\\?").)+)'),
    re.compile(r'(--(?i:acoustid)[\w-]*=)(?!\[withheld\])([^\s"\\]+)'),
    re.compile(r'(--(?i:acoustid)[\w-]*\s+)(?!\[withheld\])'
               r'(\\"(?:(?!\\").)*\\"|"[^"]*"|[^\s"\\]+)'),
)
PLACEHOLDER_KEY = "[withheld]"

NAMES_ENV = "CYANRIP_REDACT_NAMES"
NAMES_FILE = pathlib.Path.home() / ".config" / "cyanrip" / "redact-names"

PLACEHOLDER_HOST = "host"
PLACEHOLDER_NAME = "the owner"


def local_names(path=None):
    """The owner's names, from a file outside the repository, or None when
    there is no such file -- which is "not checked", not "none"."""
    p = path or os.environ.get(NAMES_ENV) or NAMES_FILE
    p = pathlib.Path(p).expanduser()
    if not p.is_file():
        return None
    names = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            names.append(line)
    return names


# Names every machine answers to, which identify nobody.
NOT_PERSONAL = {PLACEHOLDER_HOST, "localhost", "localhost.localdomain"}


def hostnames_in(text):
    """Hostnames the material names about itself."""
    found = set(UNAME.findall(text)) | set(HOST_FIELD.findall(text))
    return {h for h in found if h.lower() not in NOT_PERSONAL}


def _forms(host):
    """A hostname and its short form, longest first, so the FQDN goes whole."""
    forms = {host}
    short = host.split(".")[0]
    if short:
        forms.add(short)
    return sorted(forms, key=len, reverse=True)


class Report:
    def __init__(self, names_checked):
        self.home = 0
        self.hosts = 0
        self.names = 0
        self.keys = 0
        self.wire_lines_kept = 0
        self.names_checked = names_checked

    def changed(self):
        return bool(self.home or self.hosts or self.names or self.keys)

    def summary(self):
        parts = [f"{self.home} home path(s)", f"{self.hosts} hostname(s)"]
        parts.append(f"{self.names} name(s)" if self.names_checked
                     else "names not checked (no local list)")
        if self.keys:
            parts.append(f"{self.keys} AcoustID key(s)")
        if self.wire_lines_kept:
            parts.append(f"{self.wire_lines_kept} HANDSHAKE- line(s) left as "
                         f"they are")
        return ", ".join(parts)


def redact(text, hosts=(), names=None):
    """Return (redacted text, Report). `hosts` adds hostnames the caller knows
    to the ones the text names; `names` is local_names()'s answer."""
    rep = Report(names is not None)
    all_hosts = set(hosts) | hostnames_in(text)
    host_res = [re.compile(r"(?:(?<![\w.-])|" + AFTER_ESCAPE + ")" + re.escape(f)
                           + r"(?![\w-])")
                for h in sorted(all_hosts, key=len, reverse=True)
                for f in _forms(h)]
    name_res = [re.compile(r"(?:\b|" + AFTER_ESCAPE + ")" + re.escape(n) + r"\b")
                for n in sorted(names or (), key=len, reverse=True)]

    out = []
    for line in text.splitlines(keepends=True):
        if WIRE.match(line):
            if (HOME_PATH.search(line) or any(r.search(line) for r in host_res)
                    or any(r.search(line) for r in name_res)):
                rep.wire_lines_kept += 1
            out.append(line)
            continue
        line, n = HOME_PATH.subn("~", line)
        rep.home += n
        for r in ACOUSTID_KEYS:
            line, n = r.subn(lambda m: m.group(1) + PLACEHOLDER_KEY, line)
            rep.keys += n
        for r in host_res:
            line, n = r.subn(PLACEHOLDER_HOST, line)
            rep.hosts += n
        for r in name_res:
            line, n = r.subn(PLACEHOLDER_NAME, line)
            rep.names += n
        out.append(line)
    return "".join(out), rep


def redact_bytes(data, hosts=(), names=None):
    """redact() for file contents. Bytes that are not UTF-8 are returned
    unchanged, with a report saying nothing was replaced: decoding them with
    replacement characters would rewrite bytes nobody asked to change."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data, Report(names is not None)
    new, rep = redact(text, hosts, names)
    return new.encode("utf-8"), rep


def findings(text, names=None):
    """What redact() would replace, as (line number, kind) pairs, for a check
    of what is newly committed. A name found is reported by kind only: the
    report must not write the name it found."""
    out = []
    hosts = hostnames_in(text)
    host_res = [re.compile(r"(?:(?<![\w.-])|" + AFTER_ESCAPE + ")" + re.escape(f)
                           + r"(?![\w-])")
                for h in hosts for f in _forms(h)]
    name_res = [re.compile(r"(?:\b|" + AFTER_ESCAPE + ")" + re.escape(n) + r"\b")
                for n in names or ()]
    for i, line in enumerate(text.splitlines(), 1):
        if WIRE.match(line):
            continue
        for m in HOME_PATH.finditer(line):
            out.append((i, f"home path {m.group(0)!r}"))
        if any(r.search(line) for r in host_res):
            out.append((i, "a hostname"))
        if any(r.search(line) for r in name_res):
            out.append((i, "the owner's name"))
        if any(r.search(line) for r in ACOUSTID_KEYS):
            out.append((i, "an AcoustID key"))
    return out
