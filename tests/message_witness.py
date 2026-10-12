#!/usr/bin/env python3
"""tools/message-witness.py's fills(): a citation may fill a conversion, and
a reworded message may not hide behind one.

Found by the upstream sync of 2026-10-12. Upstream's own test asserts
`Invalid track naming scheme`, which is exactly what the binary prints for
`Invalid %s naming scheme "%s"!`, and the census reported it as text the
binary cannot print: the message's literal prefix, `Invalid`, is shorter than
MIN_PROBE, so the prefix match had nothing to compare with. Each case below is
one way fills() could be wrong, in either direction.
"""

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "message_witness", ROOT / "tools" / "message-witness.py")
mw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mw)

failures = 0


def check(cond, msg):
    global failures
    if not cond:
        failures += 1
        print(f"FAIL: {msg}")


SCHEME = 'Invalid %s naming scheme \\"%s\\"!'   # as the contract prints it
PRI = 'Read %" PRIu64 " frames from track %i, expected more'

# What the binary prints is a citation of the message.
for cited in ("Invalid track naming scheme",
              'Invalid CUE naming scheme "{album',
              "Invalid track naming sch"):
    check(mw.fills(SCHEME, cited), f"{cited!r} must fill {SCHEME!r}")
check(mw.fills(PRI, "Read 12 frames from track 3, expected"),
      "an inttypes conversion must be fillable too")

# A reworded message must not: a conversion cannot swallow the words after it.
for cited in ("Invalid frob naming schema",
              "Invalid track name scheme",
              "Invalid track"):
    check(not mw.fills(SCHEME, cited), f"{cited!r} must NOT fill {SCHEME!r}")

# Too little literal text to identify the message is no match, whatever fills.
check(not mw.fills("Bad %s!", "Bad thing!"),
      "a match on fewer than MIN_PROBE literal characters identifies nothing")

# And the case the census found, against the real contract.
rows = mw.p5_rows(ROOT / "PROVIDER-CONTRACT.md")
segs = [seg for _, m in rows for seg in m.split("\\n")]
check(any(mw.fills(s, "Invalid track naming scheme") for s in segs),
      "the published contract's naming-scheme refusal is not found")

if failures:
    print(f"{failures} check(s) failed")
    sys.exit(1)
print("message-witness: a citation fills conversions and nothing more")
