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

"""Bundle several files into one transport envelope, hash-verified.

Platterpus's format, adopted verbatim in round 9 lap 3. Exact bytes between
column-0 delimiters, a SHA-256 per part, and the reader published inside the
envelope as code so the split is checkable rather than trusted.

An envelope is NOT a merged file. The parts stay byte-identical and the split
is exact; nothing is blended, so who-said-what-when survives.

**It is also not a lap, and that is now a rule rather than a hope.** Platterpus
built this format, and their own enumerator counted the envelope as a fourth
lap because it carries wire headers in its body. The fix is PROTOCOL.md v4
§5a "What counts as one lap": a file is a lap only if ROUND, LAP and FROM each
appear exactly once after fences are stripped. An envelope carrying N laps
declares each field N times, so it is excluded by construction -- by the rule
their defect produced, which is why the format is safe to use again.

This tool asserts that property on its own output before writing it, so an
envelope that would be mistaken for a lap is never produced in the first place.

Usage:
    tools/make-envelope.py out.md FILE [FILE ...]
"""

import hashlib
import pathlib
import re
import sys

READER = '''```python
import hashlib, re
PART = re.compile(
    r"^<{10} BEGIN (?P<name>\\S+) sha256=(?P<sha>[0-9a-f]{64}) >{10}$\\n"
    r"(?P<body>.*?)\\n^<{10} END (?P=name) >{10}$",
    re.MULTILINE | re.DOTALL,
)
for m in PART.finditer(open("ENVELOPE", encoding="utf-8").read()):
    data = (m["body"] + "\\n").encode("utf-8")
    assert hashlib.sha256(data).hexdigest() == m["sha"], m["name"]
    open(m["name"], "wb").write(data)
```'''

FENCE_RE = re.compile(r"^```.*?^```", re.M | re.S)


def not_a_lap(text):
    """PROTOCOL.md v4 §5a, asserted against our own output before it ships."""
    stripped = FENCE_RE.sub("", text)
    for field in ("HANDSHAKE-ROUND", "HANDSHAKE-LAP", "HANDSHAKE-FROM"):
        if len(re.findall(rf"^{field}:", stripped, re.M)) == 1:
            return False
    return True


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__.strip().splitlines()[-1].strip())
    out = pathlib.Path(sys.argv[1])
    paths = [pathlib.Path(p) for p in sys.argv[2:]]

    rows, body = [], []
    for p in paths:
        raw = p.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        rows.append(f"| `{p.name}` | {len(raw):,} | `{sha[:16]}…` |")
        text = raw.decode("utf-8")
        if text.endswith("\n"):
            text = text[:-1]
        body.append(f"<<<<<<<<<< BEGIN {p.name} sha256={sha} >>>>>>>>>>\n"
                    f"{text}\n"
                    f"<<<<<<<<<< END {p.name} >>>>>>>>>>")

    doc = f"""# Transport envelope — {len(paths)} file(s)

**Not a merged file and not a lap.** Each part below is byte-identical to its
original, between column-0 delimiters, with its own SHA-256. Split it before
reading; the reader is published here as code so you have an exact inverse
rather than a description of one.

**It cannot be counted as a lap.** It declares the wire headers of every lap it
carries, so under `PROTOCOL.md` v4 §5a it fails the exactly-once test and every
conforming enumerator excludes it. `tools/make-envelope.py` asserts that on this
file before writing it.

## Manifest

| file | bytes | sha256 |
| --- | --- | --- |
{chr(10).join(rows)}

## Reader

{READER.replace("ENVELOPE", out.name)}

---

{chr(10).join(body)}
"""

    if not not_a_lap(doc):
        sys.exit("refusing to write an envelope that a conforming enumerator "
                 "would read as a lap -- one of ROUND/LAP/FROM appears exactly "
                 "once in it after fences are stripped")

    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out} — {len(paths)} part(s), {len(doc):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
