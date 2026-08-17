#!/usr/bin/env python3
"""Every lap we have handed over still hashes to the bytes that left.

WHY THIS EXISTS, and it is not a hypothetical.

Round 9 lap 3 was sent, and then edited twice. The edits were real improvements
-- a transport paragraph the operator asked for, and a corrected provenance line
-- and both were wrong to make, because a sent lap is evidence. PROTOCOL.md v4
§4a says it in one sentence: *"SENT is irreversible. A sent lap is never edited;
a correction is a NEW LAP that says what it corrects."*

We wrote that rule. We adopted it byte-identical. We criticised Platterpus for
breaking it in round 9 lap 5 §B. And we had already broken it ourselves, one lap
earlier, while quoting it at them -- and told ourselves it was permitted because
the lap was "still DRAFT". It was not: it had been handed to the operator. A lap
is SENT when it is handed over, not when someone confirms forwarding it.

Nothing caught it. Every check we had was about a file's CONTENT; none was about
its IDENTITY OVER TIME. It surfaced only because the digest disagreed and
Platterpus traced it -- from OUR OWN file naming its own commit, which is
impossible, so two revisions had to exist.

THREE PROPERTIES, each because the obvious version would not have caught it.
Adopted from Platterpus's `tests/test_sent_laps_are_immutable.py` (round 9 lap 4
§A), which is better than anything we had.

  * KEYED ON THE HASH, NOT ON GIT. "Changed since the commit that sent it" needs
    to know which commit sent it, and that is not in the tree: a lap is sent when
    an operator attaches it to a message, an event git never sees. The hash is
    the only fact that crosses that boundary.

  * THE MAP MAY GROW AND MAY NEVER HAVE A VALUE EDITED. If this test fails,
    RESTORE THE FILE FROM THE COMMIT THAT SENT IT and issue a new lap saying what
    you corrected. Do NOT update the constant to match the drifted file. A guard
    whose remedy is "adjust the guard" is not one.

  * A PREMATURE PIN IS REMOVED, NOT EDITED, AND IT IS NOT THE SAME FAILURE.
    The map means "the bytes that LEFT". An entry added before the lap was handed
    over records a send that never happened, so the remedy is to DELETE the entry
    and re-add it when it actually goes -- not to edit the value, and not to
    freeze a draft. Round 10 lap 5 was pinned at write time, and then genuinely
    needed to change, because the operator had not sent it and the release landed
    in it. Editing the value would have been the forbidden move below; keeping the
    stale value would have frozen a lap that was still ours to write.

    A SENT lap that drifted is evidence tampering. An UNSENT lap that changed is
    just editing. What tells them apart is not in the tree -- it is whether an
    operator handed the file over -- so it is their answer, and the safe default
    when nobody says is to treat it as sent.

  * RESTORE FROM THE SEND COMMIT, NOT WITH `git checkout --`. Platterpus's first
    attempt used the latter and stayed red, because the repository's own history
    had the drifted copy as HEAD. That is what drift means.
"""

import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HS = ROOT / "docs" / "handshake"

# The bytes that left. Append only.
SENT = {
    "round-08-lap-01.md":
        "04e42ef7d935ab92e4262ce80e77094a812a4d93576784dd2e6cb66be6c4e9eb",
    "round-08-lap-03.md":
        "9a6a7fef0dec28e5e15c7c6a9088109205e4428ba6ac8e97433237f0767f58bb",
    "round-08-lap-05.md":
        "63dcf828d76eaba5e689f471109330b4ffd60f0777ba264072a018b84caadd1b",
    "round-08-lap-07.md":
        "f57fa483d62c91a182f3531bfbd1809d2ed4b349688bff8f8973994a2d58d05e",
    "round-08-lap-09.md":
        "afa06bf65d53d7d7a37d21c20966c15ee585935238b778b85c9328bca3c5b827",
    "round-08-lap-11.md":
        "3139a65cfeebb62a3e1b1f062bbd1868d4881db862f5a5f0adb8c684d6c2bae0",
    "round-08-lap-13.md":
        "d3d886be30ee42cc483da870de8c1fe8d0feafb6c5fb98a8a5f8457316ccead1",
    "round-08-lap-15.md":
        "be6bc52f9ba3efc1c6113156dd0048dfd2c2299c0c21f50cf622fc64550a0ae3",
    "round-08-lap-17.md":
        "0f51fdeeaf3b4ffe26d5405948bba2fcb31ec58f7852f527a26d01d0f39d543a",
    "round-09-lap-01.md":
        "a1ee87461ab6373f1c124559eb478692ce2e99d71231d38344088ec4729d6a44",
    "round-09-lap-03.md":
        "38ab347ec8751274511ac863fd57fe93463adb3a5db2626046de17d449ca38f6",
    "round-09-lap-05.md":
        "45f28185707f73f5990fd1f0eaead29524106d3622446f8ac25d9fdffe66a82f",
    "round-09-lap-07.md":
        "8e3265a95f9063179faf2d69a33cc3fb0efaa5db658bd8b0a575572a3c0a7843",
    "round-09-lap-09.md":
        "2c7e7f85e58b1ea27a960f0f7b2fa554244a16967ae75e24de7bbbf129b8e795",
    "round-09-lap-11.md":
        "d361c1b9092e9fb088902e96fefb6f11ca6b56f1254c3e473cabcf02fc631c61",
    "round-10-lap-01.md":
        "0c33dea35fc3dda0c2cf67166d33116799aa62b3b3ad76cf1f757811d7703ef5",
    "round-10-lap-03.md":
        "3475b9b8ce69550fee5998c3c8040d87c25043269f5db72de4a689ada1be23cc",
    # Confirmed delivered by Platterpus quoting its §0 back to us in their own
    # changelog -- "their lap 5 §0 measured that a default build of that tarball
    # still renders NOT a released build". That citation is the send receipt this
    # map otherwise has no way to observe.
    "round-10-lap-05.md":
        "e9be4ae1496728a9f53886a3942e3714ba855e523d695218c8c5aae926232064",
    "round-11-lap-01.md":
        "cc74b3cf8d43d5f4acd4c555e44cbd447f53cbbf718e2fd0c80b78c1c46d19b8",
    "round-11-lap-03.md":
        "915ab34d89a0997e2721244786fe3abd31c6fa19203ee0f16011025ec80f985f",
}

failures = 0
for name, want in sorted(SENT.items()):
    path = HS / name
    if not path.exists():
        print(f"FAIL: {name} is pinned as sent but is not in the tree")
        failures += 1
        continue
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != want:
        print(f"FAIL: {name} has changed since it was sent\n"
              f"      sent {want}\n"
              f"      now  {got}\n"
              "      RESTORE IT from the commit that sent it, and issue a NEW LAP\n"
              "      saying what you corrected. Do NOT update the value above --\n"
              "      a guard whose remedy is 'adjust the guard' is not one.")
        failures += 1

# Every lap file must be pinned once sent. A lap that exists and is not in the
# map is either unsent (fine, and it will be added when it goes) or forgotten --
# and the two are indistinguishable without saying which, so say which.
# From round 8 onward, which is where this map begins. Round 7's laps were sent
# before it existed, and pinning them now would assert a hash nobody checked at
# send time -- a fabricated record, not a recovered one.
#
# The glob was `round-0[89]-lap-*.md`, which silently stopped covering anything
# the moment round 10 opened. That is how round 10 lap 5 came to be pinned before
# it was sent with nothing to notice: the one check that reports a lap's pin
# state had gone blind to the whole round.
def _round_of(name):
    m = re.match(r"round-(\d+)-lap-", name)
    return int(m.group(1)) if m else None

unpinned = sorted(p.name for p in HS.glob("round-*-lap-*.md")
                  if p.name not in SENT and (_round_of(p.name) or 0) >= 8)
if unpinned:
    print(f"not yet pinned (add on send): {', '.join(unpinned)}")

print(f"{len(SENT)} sent lap(s) checked, {failures} changed")
sys.exit(1 if failures else 0)
