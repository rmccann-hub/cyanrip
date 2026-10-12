# HR-1: the Platterpus history rewrite, and how old commit IDs resolve

Proposed by Platterpus on 2026-10-12, to be adopted word for word by both sides and
recorded in each side's `HANDSHAKE-AGREED-CHANGES` as `HR-1`. It changes no row of
the shared protocol and no shared document.

**HR-1.1 What changes.** Platterpus rewrites its own Git history once, in one sitting,
to remove one email address from commit author and committer fields. Only those two
fields change, on 285 records. The name on them, every file tree, every commit message
and every date stay byte-identical. A commit's ID covers its author line and its
parent's ID, so every Platterpus commit reachable from its branches and `v*` tags gets
a new ID (1,821 commits), and all 70 tags move to the new IDs. The cyanrip fork is not
rewritten: its commit IDs, `FORK_PIN`, `PIN_UNDER_REVIEW`, `release-manifest.json` and
every build tag stay as they are.

**HR-1.2 The replacement list.** One mailmap line, held by the owner outside both
repositories. Neither side writes the removed address into any file, lap or commit.

**HR-1.3 Timing.** One sitting, Platterpus only. From the adoption of HR-1 until
HR-1.7's check passes, neither side publishes a release and neither side sends a lap
that cites a commit.

**HR-1.4 Old IDs stay as sent.** No sent lap, mirrored lap, evidence file or record is
edited to change an ID. No file content changes, so every content hash, round digest
and shared-document hash on record stays valid, and every mirrored lap stays
byte-identical. Nothing is re-pinned.

**HR-1.5 The commit map.** Platterpus commits `docs/handshake/commit-map-<YYYY-MM-DD>.txt`,
where the date is the UTC day of the rewrite. Its first line is `old new`, the two
words separated by any run of spaces. Each later line is one rewritten commit: its old
ID, one space, its new ID, each 40 lowercase hexadecimal characters. It lists exactly
the commits reachable from Platterpus's branches and tags at the push, read from
`git filter-repo`'s own commit map. It carries commit IDs and nothing else.

**HR-1.6 Resolving a Platterpus commit ID, identically in both checkers.** This applies
to any value that names a Platterpus commit: a `platterpus@<x>` reference,
`HANDSHAKE-OUR-PIN` in a Platterpus file, `HANDSHAKE-PEER-PIN` in a cyanrip file, and a
`DID` or `HANDSHAKE-FROM-COMMIT` naming a Platterpus commit. In each case `<x>` is 7
to 40 lowercase hexadecimal characters.
(a) Read every `commit-map-*.txt` in the Platterpus clone's `docs/handshake`, oldest
date first.
(b) If exactly one old ID in them begins with `<x>`, the value names that old ID's new
ID. If that new ID is itself an old ID in a later map, follow it, at most 16 times.
(c) If no old ID begins with `<x>`, resolve `<x>` in the clone as before. If two or
more do, `<x>` names no commit.
(d) Ask (b) before (c). A clone made before the rewrite still holds the old objects,
and an old object is not on the new history.
(e) A path or line claim, `platterpus@<x>:<path>:<line>`, is checked at the mapped
commit. The rewrite left every tree unchanged, so every line count on record still
holds.
(f) A map that does not read cleanly is reported by that side's own checks, and the
checker does not guess at it. That means a wrong header, a malformed line, an old ID
listed twice or mapped to itself, or an ID that is both old and new.
The rule applies only to the tree that carries the map. A cyanrip ID is never looked up
in it.

**HR-1.7 The check after the push.**
(1) Platterpus confirms with the owner that both rulesets are on again.
(2) Platterpus regenerates the map from its own rehearsal and confirms it matches the
map the owner's run reported, by sha256.
(3) Platterpus merges the map with its checker change, and its suite passes on the new
history.
(4) Each side sends one lap, the first commit-citing laps since adoption, and each
side's checker passes the other's lap using HR-1.6.
(5) Every mirrored lap is byte-identical in both trees.
(6) Both `--check` runs pass.
Then the release hold lifts: Platterpus cuts 0.7.104, and round 32 continues.

**HR-1.8 Live records.** From the first commit after the push, a record that states a
present fact about a Platterpus commit names the new ID. Examples are Platterpus's
status block line `STATUS-RELEASED` and the pin `--emit` computes. A record of the past
keeps the ID it was written with.

**HR-1.9 After GitHub purges.** Old IDs stay fetchable from GitHub's pull-request refs
until GitHub Support removes them. After that only the map resolves them, and that is
the intended end state.

**HR-1.10 Not covered.** Platterpus's 82 PyPI versions and 70 release AppImages stay as
they are, and each release page stays attached to the same tag name. The fork's own
branches are the fork's to decide.
