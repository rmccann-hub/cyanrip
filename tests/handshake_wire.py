#!/usr/bin/env python3
"""Every handshake lap is well-formed enough for the other side's gate.

Not whether a round is closed -- an open round is the normal state and must
never fail a build. Only whether the files we SEND carry the fields the shared
protocol requires, because that is the failure that already happened: round-8
laps 1 and 3 went to Platterpus missing three required headers, and this
repository's whole suite was green at the time.

The requirement is PROTOCOL.md C9: a round >= 8 file missing any of FROM /
APP-VERSION / RIPPER-VERSION / PIN must be refused by the receiving gate,
naming the field. So a file like that is not a lap; it is a bounced message we
have not noticed bouncing.

It imports release-gate.py's own loader rather than re-parsing the headers.
Two readers of one record that can disagree is the defect both gates exist to
prevent, and a second copy of the parsing rules is how they come to disagree.
"""

import importlib.util
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

spec = importlib.util.spec_from_file_location("relgate", root / "tools" / "release-gate.py")
relgate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(relgate)

# Files that went out malformed and CANNOT be corrected, because the
# correspondence is append-only and editing a sent lap falsifies the record.
# They are named individually rather than waved through by round number, so
# adding to this set is a visible act -- and every addition is an admission
# that another malformed file reached the other side.
#
# Both of these are round-8 laps sent on 2026-08-10 missing three required v2
# headers. `round-08-lap-05.md` withdraws that round and says so on the record.
SENT_MALFORMED = {
    "round-08-lap-01.md",
    "round-08-lap-03.md",
}

fails = 0
laps = relgate.load_rounds(root / "docs" / "handshake", every_lap=True)
if not laps:
    print("FAIL: no handshake laps found at all -- an empty record is not a pass")
    sys.exit(1)

for lap in sorted(laps, key=lambda l: (l.number or 0, l.lap or 0)):
    missing = lap.missing_wire_header()
    if not missing:
        continue
    if lap.path.name in SENT_MALFORMED:
        print(f"known-bad (sent, cannot be edited): {lap.path.name} "
              f"-- missing {', '.join(missing)}")
        continue
    print(f"FAIL: {lap.path.name} is missing {', '.join(missing)} -- "
          "PROTOCOL.md C9 tells the receiving gate to refuse this file")
    fails += 1

print(f"{len(laps)} lap(s) checked, {fails} malformed")
sys.exit(1 if fails else 0)
