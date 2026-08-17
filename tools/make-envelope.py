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

**One file per exchange.** The operator moves these by hand, so a handshake
exchange is ONE attachment: the lap travels inside the envelope with everything
it references. Pass the operative lap with --lap and it is placed first and
named in the header, so a reader knows what the exchange is before splitting.
The only thing that may ever travel separately is a script meant to be run.

Usage:
    tools/make-envelope.py out.md [--lap LAP.md] FILE [FILE ...]
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
    argv = sys.argv[1:]
    lap = None
    if "--lap" in argv:
        i = argv.index("--lap")
        lap = pathlib.Path(argv[i + 1])
        del argv[i:i + 2]
    if len(argv) < 2:
        sys.exit("usage: make-envelope.py out.md [--lap LAP.md] FILE [FILE ...]")
    out = pathlib.Path(argv[0])
    paths = [pathlib.Path(p) for p in argv[1:]]
    # The name is DERIVED from the lap it carries, never typed. Platterpus's
    # drifted three times in one session because the property lived in a source
    # comment instead of a check, and an envelope named for a round but not a
    # lap silently overwrites the previous one on the operator's disk -- our own
    # two round-9 envelopes were `round09-exchange.md` and `round09-lap05.md`,
    # which is exactly the inconsistency they warned about (lap 6 §H). If a lap
    # is named, the filename comes from it.
    if lap is not None:
        head = lap.read_text(encoding="utf-8")
        r = re.search(r"^HANDSHAKE-ROUND:[ \t]*(\d+)", head, re.M)
        l = re.search(r"^HANDSHAKE-LAP:[ \t]*(\d+)", head, re.M)
        if r and l:
            derived = out.parent / f"round-{int(r.group(1)):02d}-lap-{int(l.group(1)):02d}-envelope.md"
            if derived != out:
                print(f"note: naming the envelope for the lap it carries: "
                      f"{derived.name} (not {out.name})")
            out = derived
    if lap is not None:
        paths = [lap] + [p for p in paths if p != lap]

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

    if lap is not None:
        head = lap.read_text(encoding="utf-8")
        verdict = re.search(r"^HANDSHAKE-VERDICT:[ \t]*(\S+)", head, re.M)
        lapno = re.search(r"^HANDSHAKE-LAP:[ \t]*(\d+)", head, re.M)
        rnd = re.search(r"^HANDSHAKE-ROUND:[ \t]*(\d+)", head, re.M)
        # Prose, deliberately -- PROTOCOL.md 2 rule 5 says a value quoted in
        # prose is not a declaration of it, so this tells a reader what the
        # exchange is without the envelope ever parsing as a lap.
        lead = (f"**The operative lap is `{lap.name}`, part 1 below** — round "
                f"{rnd.group(1) if rnd else '?'}, lap "
                f"{lapno.group(1) if lapno else '?'}, verdict stated in it as "
                f"{verdict.group(1) if verdict else 'none'}. Split first, then "
                f"read it; everything else here is what it references.\n\n")
        # The envelope RE-DECLARES the triple its operative lap declares, so
        # each field appears at least twice and §5a's exactly-once test excludes
        # this file by construction.
        #
        # Without it, an envelope carrying ONE lap and its artifacts is
        # indistinguishable from a lap -- one round, one lap, one from -- and
        # this tool refused to emit one at all. That is the single commonest
        # exchange there is, so "one file per exchange" and "attach what the lap
        # references" were in direct conflict, and round 10 lap 5 travelled bare
        # because of it. The prose below already claimed the envelope "declares
        # the wire headers of every lap it carries"; with one lap that was false,
        # and this makes it true rather than rewording it.
        #
        # Only when a lap is present: with no lap the parts declare nothing, the
        # counts are zero, and adding these would make them exactly one -- which
        # would refuse the artifacts-only envelope for the reason this fixes.
        fro = re.search(r"^HANDSHAKE-FROM:[ \t]*(\S+)", head, re.M)
        lead = (f"HANDSHAKE-ENVELOPE: 1\n"
                f"HANDSHAKE-ROUND: {rnd.group(1) if rnd else '?'}\n"
                f"HANDSHAKE-LAP: {lapno.group(1) if lapno else '?'}\n"
                f"HANDSHAKE-FROM: {fro.group(1) if fro else '?'}\n\n") + lead
    else:
        lead = ""

    doc = f"""# Transport envelope — {len(paths)} file(s)

{lead}**Not a merged file and not a lap.** Each part below is byte-identical to its
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
