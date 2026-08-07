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

"""Generate release-manifest.json -- the file a consumer polls to answer
"is there something newer, and is it a beta?" without guessing.

It exists because **neither of the obvious mechanisms works here**:

  * **Tags / GitHub releases.** Tag pushes are refused by this environment with
    HTTP 403, re-probed every round, and no release-creation API is reachable.
    Any design resting on them is a design that cannot ship from here.
  * **Comparing version strings.** Ours cannot be ordered. `0.9.4-rc1` is
    upstream's, copied verbatim, and the part that actually advances is
    `+platterpus.N` -- SemVer *build metadata*, which the spec says MUST be
    ignored for precedence. A checker comparing versions compares
    `0.9.4-rc1` against `0.9.4-rc1` forever. And a checker asking "is 'beta' in
    the string?" finds ours and misses Platterpus's `v0.6.4b1`, so it would
    report a beta user as stable.

So machine decisions are never derived from the human-facing string. The
manifest states the channel and a monotonic integer, both as facts.

**What is derived vs stated.** Publication is an act nobody can infer from a
tree, so `docs/release-ledger.tsv` is written by hand and is the single stated
input. Everything else here is derived -- the round state from the same files
release-gate.py reads, the version from the ledger row, the shape from the
rules below. A hand-maintained manifest goes stale silently, which is the exact
failure it exists to prevent.

Three properties are asserted at generation time rather than hoped for, each
blocking a specific way a user gets hurt:

  1. **`stable` never points at a beta.** A user who never opts in must be
     unable to reach one, even transiently, even if this file is generated
     wrong.
  2. **`stable` is retained when a beta exists.** Downgrade must always be
     possible; a beta that replaces the stable entry is a one-way door.
  3. **`round_closed` is derived**, not stated. A manifest claiming a round
     closed while the gate says otherwise is the two-gates-disagree failure in
     a new place.

Usage:
    tools/gen-release-manifest.py                     # write to stdout
    tools/gen-release-manifest.py --check FILE        # non-zero if FILE is stale
"""

import argparse
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = ROOT / "docs" / "release-ledger.tsv"

# The raw URL a consumer polls. Stated here so the manifest carries its own
# location -- a file that does not say where it lives cannot be re-fetched from
# a copy of itself.
MANIFEST_URL = ("https://raw.githubusercontent.com/rmccann-hub/cyanrip/"
                "platterpus-fork/release-manifest.json")
REPO_URL = "https://github.com/rmccann-hub/cyanrip"

CHANNELS = ("stable", "beta")


class LedgerError(Exception):
    pass


def load_ledger(path=None):
    """Parse and VALIDATE the ledger. Validation is the point: a sequence that
    is not monotonic is not a sequence, and finding that out at generation time
    beats finding it out when a consumer downgrades a user by accident.

    `path=None` and resolved here, NOT `path=LEDGER`. A default argument is
    evaluated once when the function is defined, so a caller that points this
    at a different ledger -- a test, or a check of another checkout -- would
    silently get the real one and report on the wrong file. release-gate.py
    carries this warning in a comment; the first draft of this file reproduced
    the defect anyway, and the test for the open-round refusal is what caught
    it, by passing when it should have failed."""
    if path is None:
        path = LEDGER
    rows, seen_seq = [], set()
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 5:
            raise LedgerError(
                f"{path.name}:{n}: expected 5 tab-separated fields, got "
                f"{len(parts)}: {raw!r}")
        seq_s, channel, version, commit, rnd_s = (p.strip() for p in parts)
        try:
            seq, rnd = int(seq_s), int(rnd_s)
        except ValueError:
            raise LedgerError(f"{path.name}:{n}: seq and round must be integers")
        if channel not in CHANNELS:
            raise LedgerError(
                f"{path.name}:{n}: channel {channel!r} is not one of {CHANNELS}. "
                "An unrecognised channel is not a channel a consumer can honour.")
        if seq in seen_seq:
            raise LedgerError(
                f"{path.name}:{n}: seq {seq} is reused. The sequence is the only "
                "orderable thing we publish; reusing a value destroys it.")
        if rows and seq != rows[-1]["seq"] + 1:
            raise LedgerError(
                f"{path.name}:{n}: seq {seq} does not follow {rows[-1]['seq']}. "
                "It increments by one per published artifact, stable or beta.")
        if not re.fullmatch(r"[0-9a-f]{7,40}", commit):
            raise LedgerError(f"{path.name}:{n}: commit {commit!r} is not a sha")
        seen_seq.add(seq)
        rows.append({"seq": seq, "channel": channel, "version": version,
                     "commit": commit, "round": rnd})
    if not rows:
        raise LedgerError(f"{path.name}: no rows. An empty ledger publishes nothing.")
    return rows


def round_state():
    """Round -> closed?, derived from the SAME loader the release gate uses.

    Imported rather than reimplemented on purpose: two readers of one record
    that can disagree is the failure both gates exist to prevent, and a second
    copy of the parsing rules is exactly how they come to disagree."""
    spec = importlib.util.spec_from_file_location(
        "release_gate", ROOT / "tools" / "release-gate.py")
    rg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rg)
    return {r.number: bool(r.closed) for r in rg.load_rounds()}


def build():
    rows = load_ledger()
    closed = round_state()

    manifest = {
        "schema": 1,
        "project": "cyanrip-fork",
        "manifest_url": MANIFEST_URL,
        "repo": REPO_URL,
        "note": ("Machine-readable. Order by release_seq -- the version string "
                 "cannot be ordered, because the part that advances is SemVer "
                 "build metadata, which is ignored for precedence."),
        "channels": {},
    }

    # A channel is a RISK TOLERANCE, not a separate lineage. `stable` is the
    # newest stable row; `beta` is the newest row of ANY channel, because
    # somebody who opted into pre-releases wants the newest thing, not the
    # newest thing that happens to be labelled beta.
    #
    # Getting this wrong offers a DOWNGRADE: the first generated manifest had
    # beta pointing at beta.8 (seq 10) while stable was seq 11, so opting into
    # betas would have moved a user backwards. Asserted below rather than left
    # to the reader.
    selectors = {
        "stable": lambda r: r["channel"] == "stable",
        "beta": lambda r: True,
    }

    for channel in CHANNELS:
        picked = [r for r in rows if selectors[channel](r)]
        if not picked:
            continue
        latest = max(picked, key=lambda r: r["seq"])
        manifest["channels"][channel] = {
            "version": latest["version"],
            "commit": latest["commit"],
            "release_seq": latest["seq"],
            "handshake_round": latest["round"],
            # Derived, never stated. See round_state().
            "round_closed": closed.get(latest["round"], False),
            "install": f"{REPO_URL}/archive/{latest['commit']}.tar.gz",
        }

    stable = manifest["channels"].get("stable")
    beta = manifest["channels"].get("beta")

    # Property 1. Checked against the ledger's own channel column rather than
    # by sniffing the version text -- string-sniffing is the defect this whole
    # file exists to avoid, and it would be absurd to reintroduce it here.
    if stable is not None:
        if any(r["channel"] != "stable" for r in rows
               if r["seq"] == stable["release_seq"]):
            raise LedgerError("stable channel resolved to a non-stable row")
        if not stable["round_closed"]:
            raise LedgerError(
                f"stable points at round {stable['handshake_round']}, which is "
                "NOT closed. A stable release claims joint verification; an open "
                "round means it does not have it.")

    # Property 2. A beta must never be the only thing on offer.
    if beta is not None and stable is None:
        raise LedgerError(
            "a beta is published with no stable entry -- downgrade would be "
            "impossible and a user who never opted in could reach the beta")

    # Property 4. Opting into pre-releases must never move a user backwards.
    if beta is not None and stable is not None:
        if beta["release_seq"] < stable["release_seq"]:
            raise LedgerError(
                f"beta channel (seq {beta['release_seq']}) is behind stable "
                f"(seq {stable['release_seq']}) -- switching to betas would "
                "offer a DOWNGRADE")

    # Property 3 is structural: round_closed came from round_state() above.

    # Advertise which channel a consumer gets when the user has expressed no
    # preference. Stated so a consumer cannot default to "newest seq".
    manifest["default_channel"] = "stable"
    manifest["latest_seq"] = max(r["seq"] for r in rows)
    return manifest


def render(manifest):
    return json.dumps(manifest, indent=2, sort_keys=True) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", metavar="FILE",
                    help="exit non-zero if FILE differs from what would be generated")
    a = ap.parse_args()
    try:
        text = render(build())
    except LedgerError as e:
        print(f"release manifest: {e}", file=sys.stderr)
        return 2

    if a.check:
        p = pathlib.Path(a.check)
        if not p.exists():
            print(f"{a.check}: missing", file=sys.stderr)
            return 1
        if p.read_text(encoding="utf-8") != text:
            print(f"{a.check} is STALE -- regenerate with "
                  "tools/gen-release-manifest.py", file=sys.stderr)
            return 1
        print(f"{a.check} is up to date")
        return 0

    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
