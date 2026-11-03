# Dependency plan — what we build against, what we claim, and `.29`

*Written 2026-11-02 at the owner's request: "make sure we are using the newest
versions of all dependencies, or if a big move, make sure it is part of the
plan for the next release. do we need to still support those old versions?
check if there is a compelling reason not to, or if we should keep doing it.
this is about qol for the end user, security, and balancing what we need to
do". **§1 is built; §3 and §4 are a plan for `.29`**, the release after `.28`.
A dependency is handshake material, so each change in them is announced in a
lap before the release that carries it.*

## 1. Every pin at its newest release (built 2026-11-02)

Read with `git ls-remote --tags` against each upstream on 2026-11-02, release
candidates left out, and for LAME from its SourceForge file list.

| pin | was | now | where |
|---|---|---|---|
| uv | 0.13.5 | **0.13.6** | `ci.yml`, `dependencies.yml` |
| astral-sh/setup-uv | v10.3.2 | **v10.3.3** | both workflows |
| ruff | 0.15.8 | **0.17.3** | `ci.yml`'s lint row |
| LAME | 3.100 (2017) | **4.0** (2026-07-11) | the Windows build |

Already the newest: curl 8.23.0, FFmpeg n9.0.2, neon 0.37.1, libqrencode
4.1.1 and cyanreg/libmusicbrainz's head in the Windows build; zizmor 1.31.1,
actionlint 1.7.12; every action (checkout v7.0.1, cache v6.1.0,
upload-artifact v7.0.2, download-artifact v8.0.2, setup-msys2 v2.33.0); and
the runner labels, each the newest of its OS. The weekly `Dependencies`
workflow had caught uv and setup-uv; it reads no tarball pin, which is how
LAME sat two releases behind. LAME 3.101 fixed a buffer overflow in the
encoder (LAME bug #500) in the library the Windows binary links; the commit
moving it says what 4.0 adds and what does not apply.

## 2. Who builds cyanrip, and against what

**End users build it in one place: a Fedora container.** Platterpus is Linux
only and runs cyanrip inside Distrobox, from
`registry.fedoraproject.org/fedora-toolbox:latest`
(`platterpus@33573022:setup-host.sh:36`). Its in-app installer builds our fork
there from Fedora's own `-devel` packages, the five FFmpeg libraries, libcdio,
libcdio-paranoia, libmusicbrainz5 and libcurl, and not libqrencode or
libchromaprint (`platterpus@33573022:src/platterpus/deps/fork_source.py:2595`),
so unless the image already holds those an end user's build has no QR codes
and no AcoustID, and its libraries are whatever the newest Fedora ships. Its setup script's first install is
upstream's cyanrip, from a COPR (`platterpus@33573022:setup-host.sh:246-265`).

| | FFmpeg (libavcodec) | libcdio | paranoia | libcurl | meson | Python |
|---|---|---|---|---|---|---|
| **Fedora 44** | 8.1.3 | 2.3.0 | 10.2+2.0.2 | 8.18.0 | 1.11.2 | 3.14.10 |
| **Fedora 45** | 9.0.1 | unread | unread | 8.21.0 | 1.12.1 | 3.15.2 |
| CI, macOS 26 (full suite) | 63.1.102 | 2.4.0 | 10.2+2.0.2 | 8.23.0 | brew's | runner's |
| CI, Windows (smoke test) | n9.0.2, ours | 2.4.0 | 10.2+2.0.2 | 8.23.0, ours | 1.12.1 | — |
| CI, Linux: Ubuntu 24.04 | 6.1.1 (60.31.102) | 2.1.0 | 10.2+2.0.0 | 8.5.0 | 1.3.2; 0.62 in the floor row | 3.12; 3.11 in the floor row |
| **declared minimum** | 59.24.100 | 2.0 | 10.2 | 7.66.0 | 0.62 | 3.10 |

Fedora's are from `mdapi.fedoraproject.org`, read 2026-11-02 (four Fedora 45
packages did not answer). The macOS and Windows rows are from PR #75's CI logs
that day; Ubuntu 24.04's from the dependency map, generated on 24.04.4, the
archive CI's linux job installs from. libmusicbrainz5 is 5.1.0, its last
release, everywhere.

## 3. The minimums: raise them to what CI tests (proposed for `.29`)

**A minimum is a claim that the build works there, and nothing runs ours.**
No job builds FFmpeg 5.1, libcdio 2.0, curl 7.66 or Python 3.10; the oldest
each meets is the Linux job's Ubuntu 24.04, and Meson's 0.62 is the one
minimum CI builds with (the floor row). An untested minimum is the "nearly
true" claim `CLAUDE.md` warns about.

**What raising them buys.**
- *Security:* of the four places the code chooses by a library's version,
  the one branch no CI job compiles is curl's before 7.85.0
  (`src/accurip.c:96`, `src/coverart.c:159`): the one that limits
  AccurateRip's and the Cover Art Archive's requests to HTTPS, through the
  deprecated `CURLOPT_PROTOCOLS`. Every build anyone makes takes the other
  branch. With a minimum of 7.85.0 or later it goes, and the HTTPS limit has
  one path, the tested one. Python 3.10 left security support in October
  2026.
- *Quality of life:* none for end users today, since Fedora is far past every
  minimum; the gain is that the dependency map and `meson setup` stop
  promising builds nobody has made.

**What keeping them buys.**
- Someone building by hand on Debian 12 (FFmpeg 5.1, curl 7.88.1, Python
  3.11) can today; with FFmpeg's minimum at 6.1 they could not. Debian 12 is
  oldstable now, on Debian's long-term support, and no such builder is known.
- One line fewer to merge in `src/meson.build` at each upstream sync.
- Not patched libraries: a distribution backports fixes into its old
  versions, so a minimum does not keep a vulnerable library out.

**Proposed for `.29`:** libavcodec and its four siblings at Ubuntu 24.04's
FFmpeg 6.1.1 versions, libcdio 2.1.0, libcurl 8.5.0 (and the pre-7.85 branch
deleted), Python 3.11, each the oldest a CI job builds or runs; libcdio-
paranoia, libmusicbrainz5, Meson, and the optional libqrencode and
libchromaprint left as they are. Platterpus's build is unaffected, as Fedora
44 and 45 exceed each; it is still announced in a lap first.

## 4. A bigger gap than the minimums: no CI job builds what users build

End users build on the newest Fedora, with libcdio 2.3 and FFmpeg 8 or 9; the
Linux job builds on Ubuntu 24.04, with libcdio 2.1 and FFmpeg 6.1, because
the golden reference is generated there. macOS runs the full suite on newer
libraries than Fedora's (libcdio 2.4.0, FFmpeg 9), but not Linux's drive code
in libcdio, and not Fedora's `ffmpeg-free`, which is built without some
encoders. Upstream report 19 is libcdio 2.3.0 changing behaviour under
upstream's cyanrip, the version Fedora 44 ships.

**Proposed:** a `fedora` job in a `fedora-toolbox:latest` container,
installing Platterpus's package list and running the suite. One more Linux
job, about the length of the others, and the only one that builds what end
users run. It needs the owner's word, being CI time every run.

## 5. Watch list, no action yet

- **The weekly dependency check reads no tarball pin**, so LAME went
  unnoticed; teaching `skillcheck` a SourceForge file list is the fix, in the
  owner's other repository.
- **`tests/personal_details.py --evidence`** tries each of the 566 manifest
  rows in turn before it skips where evidence is not fetched; one call
  instead of 566 belongs in `tools/evidence.py`. It got a 120 s timeout in PR
  #75 after macOS killed it at 30 s.
- **macOS arm64 runners** went unacquired five times on 2026-11-02; whether
  another label waits less was not measured.
- **A static Linux binary for end users.** Upstream's CI has built one for
  each release since `e5ac607` (Alpine, musl, every library linked in, QR
  codes and AcoustID among them). One of ours, named with its SHA-256 by
  `release-manifest.json`, would let Platterpus's installer fetch what our CI
  tested instead of building in the Fedora container what no CI job builds.
  It changes how every user gets the program, so it needs the owner's word and
  a round; `docs/upstream/sync-2026-11-03-ci.md` §5.
