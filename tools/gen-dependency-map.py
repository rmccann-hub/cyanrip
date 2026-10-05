#!/usr/bin/env python3
"""Derive this fork's dependency map: what it is written in, what it links,
what builds and tests it, what it contacts on the network, which projects it
sits between, and which external defects it carries a workaround for.

Writes two files from one model, so they cannot disagree:

  * sbom.cdx.json       -- CycloneDX 1.7 JSON (ECMA-424, 2nd edition), the
                           machine-readable form other applications read;
  * docs/DEPENDENCIES.md -- the same map for a person.

Asked for by the operator on 2026-10-05: "do a full map out of what
projects/languages/versions/applications/dependencies you have or rely on.
keep a detailed list somewhere standard that you and other applications can
see and use." CycloneDX is that standard here; SPDX 3.0.1 is the other, and
one format kept current beats two.

DERIVED, NOT DESCRIBED, as PROVIDER-CONTRACT.md is. Each list is read from
the file that decides it: the libraries and their minimum versions from
src/meson.build, the toolchain from meson.build, the programs the tools and
tests run from their subprocess calls, the network endpoints from src/'s
string literals, CI from .github/, the shared seam documents from
tools/seam-sync-check.py, the local workarounds from CLAUDE.md's section on
them, and the releases from release-manifest.json. What cannot be derived --
what a library is FOR -- sits in a table keyed by the derived name, and the
generator refuses when the two key sets differ, so a new dependency cannot
arrive undescribed and a removed one cannot linger.

MEASURED IS NOT DECLARED. The versions installed where this runs, the
licences confirmed from the installed packages' copyright files, the fork
point against upstream, and the machine itself are MEASURED: they describe
the machine that last generated the files, and they say so. --check compares
everything except them, so a different machine, CI included, does not read
as drift.

Usage:
    tools/gen-dependency-map.py            # write both files
    tools/gen-dependency-map.py --check    # exit 1 if either is stale
"""

import argparse
import ast
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "docs" / "DEPENDENCIES.md"
BOM_PATH = ROOT / "sbom.cdx.json"
REPO = "https://github.com/rmccann-hub/cyanrip"
UPSTREAM = "https://github.com/cyanreg/cyanrip"
CONSUMER = "https://github.com/rmccann-hub/Platterpus"
MEASURED = "cyanrip-fork:measured:"
MD_MEASURED_MARK = "## Measured where this was generated"

# What each linked library is for, keyed by its pkg-config name. The KEYS must
# equal the dependency() calls in src/meson.build; describe() refuses if not.
LIBS = {
    "libavcodec": ("FFmpeg", "https://ffmpeg.org/", "LGPL-2.1-or-later",
                   "encodes each output format"),
    "libavformat": ("FFmpeg", "https://ffmpeg.org/", "LGPL-2.1-or-later",
                    "muxes each output file and writes its tags"),
    "libavfilter": ("FFmpeg", "https://ffmpeg.org/", "LGPL-2.1-or-later",
                    "the de-emphasis, HDCD and loudness (ebur128) graphs"),
    "libavutil": ("FFmpeg", "https://ffmpeg.org/", "LGPL-2.1-or-later",
                  "CRC, dictionaries, frames, errors"),
    "libswresample": ("FFmpeg", "https://ffmpeg.org/", "LGPL-2.1-or-later",
                      "sample-format conversion for each encoder"),
    "libcdio": ("GNU libcdio", "https://www.gnu.org/software/libcdio/",
                "GPL-3.0-or-later",
                "drive and disc-image access: TOC, sub-channel, ISRC, MCN, "
                "CD-TEXT, MMC commands"),
    "libcdio_paranoia": ("libcdio-paranoia",
                         "https://github.com/rocky/libcdio-paranoia",
                         "GPL-3.0-or-later",
                         "the verified read and its status counters"),
    "libmusicbrainz5": ("libmusicbrainz", "https://musicbrainz.org/doc/libmusicbrainz",
                        "LGPL-2.1-or-later",
                        "MusicBrainz lookups by disc ID"),
    "libcurl": ("curl", "https://curl.se/", "curl",
                "AccurateRip and Cover Art Archive requests"),
    "threads": ("POSIX threads (the C library)", None, None,
                "encoder threads and the read-stall watchdog"),
    "libqrencode": ("libqrencode", "https://fukuchi.org/works/qrencode/",
                    "LGPL-2.1-or-later",
                    "prints MusicBrainz submission links as QR codes"),
}

# A phrase each library's copyright file must contain for its licence above to
# count as confirmed here. Debian tags libcdio "GPL-3" while the text says
# "or (at your option) any later version", so the TEXT is what is checked.
LICENCE_PHRASE = {
    "GPL-3.0-or-later": "either version 3 of the License, or",
    "LGPL-2.1-or-later": "LGPL-2.1+",
    "curl": "License: curl",
}

# The programs the tools and tests run, keyed by name. The KEYS must equal what
# programs() finds in their subprocess calls; describe() refuses if not.
PROGRAMS = {
    "git": "reads history: lap commits, ledger publication dates, contract "
           "and upstream deltas",
    "ffmpeg": "makes the disc-image fixtures' audio and decodes rips for "
              "checksums",
    "ffprobe": "reads ripped files' tags, durations and encoder strings, as "
               "a witness independent of cyanrip",
    "meson": "configures the instrumented and mutated builds",
    "ninja": "builds them",
    "nm": "asks a binary whether sanitizer symbols are in it",
    "gcov": "coverage",
    "cd-paranoia": "on the rig only: the cache size the probe is measured "
                   "against",
    "cdparanoia": "on the rig only: the same, under its older name",
    "distrobox": "on the rig only: the container the rig's ripper runs in",
    "pkg-config": "this map's measured versions; the build finds every "
                  "library through it too",
    "dpkg": "this map: names the package that owns a library, to read its "
            "copyright file",
}

# Every http(s) literal in src/, keyed by host. The KEYS must equal what
# endpoints() finds; describe() refuses if not.
SERVICES = {
    "www.accuraterip.com": ("AccurateRip database", True, "-A",
                            "per-track checksums other rips of the disc "
                            "produced, compared with this rip's"),
    "coverartarchive.org": ("Cover Art Archive", True, "-U",
                            "the release's cover art"),
    "musicbrainz.org": ("MusicBrainz", False, "-N",
                        "the literal in src/ is the disc-submission link, "
                        "printed and never fetched; lookups reach "
                        "musicbrainz.org through libmusicbrainz5"),
}


def run(cmd, **kw):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                           cwd=kw.get("cwd", ROOT))
    except (OSError, subprocess.TimeoutExpired):
        return None
    return p.stdout.strip() if p.returncode == 0 else None


# --------------------------------------------------------------- derivation

def project():
    text = (ROOT / "meson.build").read_text(encoding="utf-8")
    name = re.search(r"project\(\s*'([^']+)'", text).group(1)
    version = re.search(r"^\s*version:\s*'([^']+)'", text, re.M).group(1)
    meson_min = re.search(r"meson_version:\s*'([^']+)'", text).group(1)
    opts = re.search(r"default_options:\s*\[([^\]]*)\]", text).group(1)
    c_std = re.search(r"c_std=(\w+)", opts).group(1)
    fork_id = re.search(r"set_quoted\('PROJECT_FORK_ID',\s*'([^']+)'\)",
                        text).group(1)
    werror = sorted(set(re.findall(r"'(-Werror=[\w-]+)'",
                                   text + (ROOT / "src" / "meson.build")
                                   .read_text(encoding="utf-8"))))
    header = (ROOT / "src" / "utils.c").read_text(encoding="utf-8")[:800]
    licence = ("LGPL-2.1-or-later"
               if "version 2.1 of the License, or (at your option) any later"
               in " ".join(header.replace("*", " ").split()) else None)
    return dict(name=name, version=version, meson=meson_min, c_std=c_std,
                fork_id=fork_id, werror=werror, licence=licence)


def libraries():
    """The dependency() calls in src/meson.build, in order."""
    text = (ROOT / "src" / "meson.build").read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"dependency\(\s*'([^']+)'([^)]*)\)", text):
        name, rest = m.group(1), m.group(2)
        v = re.search(r"version:\s*'([^']+)'", rest)
        out.append(dict(name=name,
                        declared=" ".join(v.group(1).split()) if v else None,
                        required="required: false" not in rest))
    return out


def programs():
    """Programs named first in a subprocess call in tools/ and tests/."""
    pat = re.compile(r"(?:subprocess\.(?:run|check_output|check_call|call|"
                     r"Popen)|shutil\.which)\(\s*\[?\s*[\"']([A-Za-z][\w.+-]*)"
                     r"[\"']")
    found = {}
    for p in sorted(list((ROOT / "tools").glob("*.py"))
                    + list((ROOT / "tests").glob("*.py"))):
        for m in pat.finditer(p.read_text(encoding="utf-8", errors="replace")):
            found.setdefault(m.group(1), set()).add(
                p.relative_to(ROOT).as_posix())
    return {k: sorted(v) for k, v in sorted(found.items())}


def python_imports():
    """Third-party modules the tools and tests import: none is the claim."""
    local = ({p.stem.replace("-", "_") for p in (ROOT / "tools").glob("*.py")}
             | {p.stem for p in (ROOT / "tests").glob("*.py")})
    third = {}
    for p in sorted(list((ROOT / "tools").glob("*.py"))
                    + list((ROOT / "tests").glob("*.py"))):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for n in ast.walk(tree):
            names = []
            if isinstance(n, ast.Import):
                names = [a.name.split(".")[0] for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.module and not n.level:
                names = [n.module.split(".")[0]]
            for m in names:
                if m not in sys.stdlib_module_names and m not in local:
                    third.setdefault(m, set()).add(p.relative_to(ROOT).as_posix())
    return {k: sorted(v) for k, v in sorted(third.items())}


def endpoints():
    """Every http(s) literal in src/, grouped by host."""
    out = {}
    for p in sorted((ROOT / "src").glob("*.[ch]")):
        for m in re.finditer(r"\"(https?://([^/\"]+)[^\"]*)",
                             p.read_text(encoding="utf-8", errors="replace")):
            out.setdefault(m.group(2), set()).add(
                (m.group(1), p.relative_to(ROOT).as_posix()))
    return {k: sorted(v) for k, v in sorted(out.items())}


def ci():
    """GitHub Actions: runners, actions, and packages installed."""
    wf = ROOT / ".github" / "workflows" / "main.yml"
    text = wf.read_text(encoding="utf-8")
    runners = sorted(set(re.findall(r"runs-on:\s*(\S+)", text)))
    actions = sorted(set(re.findall(r"uses:\s*([\w./-]+@[\w.-]+)", text)))
    # The package list continues over lines ending in a backslash.
    apt = re.search(r"apt-get install -y((?:[^\n]*\\\n)*[^\n]*)", text)
    apt = sorted(set(apt.group(1).replace("\\", " ").split())) if apt else []
    brew = re.search(r"brew install ([^\n]+)", text)
    brew = sorted(brew.group(1).split()) if brew else []
    msys = re.search(r"install:\s*([^\n]+)", text)
    msys = sorted(msys.group(1).split()) if msys else []
    script = (ROOT / ".github" / "mingw-build.sh").read_text(encoding="utf-8")
    clones = re.findall(r"cyan_do_vcs\s+\"(https://[^\"]+)\"", script)
    return dict(runners=runners, actions=actions, apt=apt, brew=brew,
                msys=msys, clones=clones,
                clone_pinned="--branch" in script or " -b " in script)


def shared_documents():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ssc_dep", ROOT / "tools" / "seam-sync-check.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return [dict(key=k, ours=o, theirs=t) for k, o, t in mod.SHARED]


def mitigations():
    """The bold lead of each bullet in CLAUDE.md's section on external bugs."""
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    m = re.search(r"^## Known external bugs worked around here\n(.*?)^## ",
                  text, re.S | re.M)
    out = []
    for b in re.finditer(r"^- \*\*(.+?)\*\*", m.group(1), re.S | re.M):
        out.append(" ".join(b.group(1).split()))
    return out


def releases():
    man = json.loads((ROOT / "release-manifest.json").read_text())
    return {ch: dict(version=c["version"], commit=c["commit"],
                     seq=c["release_seq"])
            for ch, c in sorted(man["channels"].items())}


def describe():
    """The whole model, minus what is measured. Refuses on a key mismatch."""
    libs = libraries()
    progs = programs()
    eps = endpoints()
    problems = []
    for what, derived, table in (("library", [l["name"] for l in libs], LIBS),
                                 ("program", list(progs), PROGRAMS),
                                 ("network host", list(eps), SERVICES)):
        for k in sorted(set(derived) - set(table)):
            problems.append(f"{what} {k!r} is used and not described in "
                            f"tools/gen-dependency-map.py")
        for k in sorted(set(table) - set(derived)):
            problems.append(f"{what} {k!r} is described and no longer used")
    if problems:
        sys.exit("refusing to write a map that disagrees with the tree:\n  "
                 + "\n  ".join(problems))
    return dict(project=project(), libs=libs, programs=progs,
                python_third_party=python_imports(), endpoints=eps, ci=ci(),
                shared=shared_documents(), mitigations=mitigations(),
                releases=releases())


# ---------------------------------------------------------------- measuring

def pc_version(name):
    return run(["pkg-config", "--modversion", name]) if shutil.which(
        "pkg-config") else None


def copyright_file(name):
    """The installed package's copyright file for a pkg-config name, via the
    .pc file's owning package. None wherever dpkg is not the packager."""
    if not shutil.which("dpkg") or not shutil.which("pkg-config"):
        return None
    pcdir = run(["pkg-config", "--variable=pcfiledir", name])
    if not pcdir:
        return None
    pc = pathlib.Path(pcdir) / f"{name}.pc"
    owner = run(["dpkg", "-S", str(pc)])
    if not owner:
        return None
    f = pathlib.Path("/usr/share/doc") / owner.split(":")[0] / "copyright"
    return f if f.exists() else None


def first_line(cmd):
    out = run(cmd)
    return out.splitlines()[0] if out else None


def measure(model):
    m = {}
    for lib in model["libs"]:
        n = lib["name"]
        lic = LIBS[n][2]
        cf = copyright_file(n)
        confirmed = None
        if cf and lic in LICENCE_PHRASE:
            txt = cf.read_text(encoding="utf-8", errors="replace")
            confirmed = f"{cf} contains \"{LICENCE_PHRASE[lic]}\"" \
                if LICENCE_PHRASE[lic] in txt else f"{cf} does not say so"
        version = pc_version(n)
        if n == "threads":
            version = "part of the C library, not a pkg-config package"
        m[n] = dict(version=version, licence_evidence=confirmed)
    os_name = None
    osr = pathlib.Path("/etc/os-release")
    if osr.exists():
        mm = re.search(r'^PRETTY_NAME="([^"]+)"', osr.read_text(), re.M)
        os_name = mm.group(1) if mm else None
    ff = run(["ffmpeg", "-version"]) or ""
    env = dict(
        os=os_name,
        python=sys.version.split()[0],
        cc=first_line(["cc", "--version"]),
        meson=run(["meson", "--version"]),
        ninja=run(["ninja", "--version"]),
        pkg_config=run(["pkg-config", "--version"]),
        git=first_line(["git", "--version"]),
        ffmpeg=first_line(["ffmpeg", "-version"]),
        ffmpeg_gpl=("--enable-gpl" in ff) if ff else None,
    )
    for prog in model["programs"]:
        env.setdefault(f"has {prog}", bool(shutil.which(prog)))
    base = None
    for ref in ("master", "origin/master"):
        base = run(["git", "merge-base", "HEAD", ref])
        if base:
            up = run(["git", "rev-parse", ref])
            break
    else:
        up = None
    m["_env"] = env
    m["_fork_point"] = base
    m["_upstream_tip"] = up
    return m


# ------------------------------------------------------------------ writing

def bom(model, meas):
    p = model["project"]
    comps, deps = [], []
    for lib in model["libs"]:
        n = lib["name"]
        proj, url, lic, why = LIBS[n]
        c = {"type": "library", "bom-ref": f"lib:{n}", "name": n,
             "scope": "required" if lib["required"] else "optional",
             "description": why,
             "properties": [{"name": "cyanrip-fork:project", "value": proj},
                            {"name": "cyanrip-fork:declared-constraint",
                             "value": lib["declared"] or "none"},
                            {"name": "cyanrip-fork:declared-in",
                             "value": "src/meson.build"}]}
        if lic:
            c["licenses"] = [{"license": {"id": lic}}]
        if url:
            c["externalReferences"] = [{"type": "website", "url": url}]
        if meas:
            mm = meas.get(n, {})
            if mm.get("version"):
                c["version"] = mm["version"]
                c["properties"].append({"name": MEASURED + "version",
                                        "value": mm["version"]})
            if mm.get("licence_evidence"):
                c["properties"].append({"name": MEASURED + "licence-evidence",
                                        "value": mm["licence_evidence"]})
        comps.append(c)
        deps.append(c["bom-ref"])
    tools = [("meson", "build system", f"meson.build requires {p['meson']}"),
             ("ninja", "build tool", "meson's backend"),
             ("pkg-config", "build tool", "finds every library above"),
             ("c-compiler", "compiler", f"C, c_std={p['c_std']}, "
              + ", ".join(p["werror"])),
             ("python3", "language runtime", "every tool and test script; "
              "standard library only")]
    for name, kind, why in tools:
        comps.append({"type": "application", "bom-ref": f"tool:{name}",
                      "name": name, "scope": "excluded",
                      "description": f"{kind}: {why}"})
    for prog, files in model["programs"].items():
        comps.append({"type": "application", "bom-ref": f"run:{prog}",
                      "name": prog, "scope": "excluded",
                      "description": PROGRAMS[prog],
                      "properties": [{"name": "cyanrip-fork:run-by",
                                      "value": f} for f in files]})
    services = []
    for host, uses in model["endpoints"].items():
        title, fetched, flag, why = SERVICES[host]
        services.append({
            "bom-ref": f"svc:{host}", "name": title,
            "endpoints": sorted({u for u, _ in uses}),
            "authenticated": False, "x-trust-boundary": True,
            "description": why,
            "properties": [{"name": "cyanrip-fork:fetched-by-cyanrip",
                            "value": "yes" if fetched else "no"},
                           {"name": "cyanrip-fork:disabled-by",
                            "value": flag}]
            + [{"name": "cyanrip-fork:named-in", "value": f}
               for f in sorted({f for _, f in uses})]})
    props = [{"name": "cyanrip-fork:fork-id", "value": p["fork_id"]},
             {"name": "cyanrip-fork:language", "value": f"C ({p['c_std']})"},
             {"name": "cyanrip-fork:consumer", "value": CONSUMER}]
    props += [{"name": "cyanrip-fork:shared-document",
               "value": f"{d['key']}: ours {d['ours']}, theirs {d['theirs']}"}
              for d in model["shared"]]
    props += [{"name": "cyanrip-fork:release",
               "value": f"{ch}: {r['version']} at {r['commit']}, "
                        f"release_seq {r['seq']}"}
              for ch, r in model["releases"].items()]
    props += [{"name": "cyanrip-fork:local-mitigation", "value": t}
              for t in model["mitigations"]]
    props += [{"name": "cyanrip-fork:ci-runner", "value": r}
              for r in model["ci"]["runners"]]
    props += [{"name": "cyanrip-fork:ci-action", "value": a}
              for a in model["ci"]["actions"]]
    props += [{"name": "cyanrip-fork:ci-unpinned-clone", "value": u}
              for u in model["ci"]["clones"]]
    ancestor = {"type": "application", "name": "cyanrip", "group": "cyanreg",
                "externalReferences": [{"type": "vcs", "url": UPSTREAM}]}
    if meas and meas.get("_fork_point"):
        ancestor["properties"] = [{"name": MEASURED + "fork-point",
                                   "value": meas["_fork_point"]}]
        if meas.get("_upstream_tip"):
            ancestor["properties"].append({"name": MEASURED + "upstream-tip",
                                           "value": meas["_upstream_tip"]})
    if meas:
        for k, v in meas["_env"].items():
            if v is not None:
                props.append({"name": MEASURED + "env:" + k.replace(" ", "-"),
                              "value": str(v)})
    component = {
        "type": "application", "bom-ref": "cyanrip", "name": p["name"],
        "version": p["version"],
        "description": "CD ripper; the Platterpus fork of cyanreg/cyanrip",
        "licenses": [{"license": {"id": p["licence"]}}],
        "externalReferences": [
            {"type": "vcs", "url": REPO},
            {"type": "documentation",
             "url": f"{REPO}/blob/platterpus-fork/PROVIDER-CONTRACT.md"},
            {"type": "documentation",
             "url": f"{REPO}/blob/platterpus-fork/docs/DEPENDENCIES.md"},
            {"type": "distribution",
             "url": f"{REPO}/blob/platterpus-fork/release-manifest.json"}],
        "pedigree": {"ancestors": [ancestor]},
        "properties": props,
    }
    doc = {
        "bomFormat": "CycloneDX", "specVersion": "1.7",
        "version": 1,
        "metadata": {
            "tools": {"components": [{
                "type": "application", "name": "gen-dependency-map.py",
                "group": "cyanrip-fork",
                "externalReferences": [{
                    "type": "vcs",
                    "url": f"{REPO}/blob/platterpus-fork/tools/"
                           f"gen-dependency-map.py"}]}]},
            "component": component},
        "components": comps,
        "services": services,
        "dependencies": [{"ref": "cyanrip",
                          "dependsOn": deps + [s["bom-ref"] for s in services]}]
                        + [{"ref": d, "dependsOn": []} for d in deps],
    }
    body = json.dumps(doc, sort_keys=True)
    doc["serialNumber"] = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL,
                                                       REPO + "#" + body))
    return doc


def strip_measured(doc):
    """What --check compares: the BOM without anything measured."""
    doc = json.loads(json.dumps(doc))
    doc.pop("serialNumber", None)

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("properties"), list):
                o["properties"] = [x for x in o["properties"]
                                   if not x["name"].startswith(MEASURED)]
                if not o["properties"]:
                    del o["properties"]
            if o.get("type") == "library":
                o.pop("version", None)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(doc)
    return doc


def markdown(model, meas):
    p = model["project"]
    w = []
    a = w.append
    a("# Dependency map — generated, do not edit")
    a("")
    a("Generated by `tools/gen-dependency-map.py` from the files that decide "
      "each list: `meson.build`, `src/meson.build`, the subprocess calls in "
      "`tools/` and `tests/`, the URL literals in `src/`, "
      "`.github/workflows/main.yml` and `.github/mingw-build.sh`, "
      "`tools/seam-sync-check.py`, `CLAUDE.md`'s section on external bugs, and "
      "`release-manifest.json`. **The machine-readable form is "
      "`sbom.cdx.json`**, CycloneDX 1.7 (ECMA-424, 2nd edition), for any "
      "application that reads a bill of materials. Regenerate with "
      "`tools/gen-dependency-map.py`; the suite's `Dependency map is current` "
      "fails when either file is stale.")
    a("")
    a("Everything above **Measured where this was generated** is declared by "
      "the tree and checked. Everything in that section describes the machine "
      "that last ran the generator and is not checked, so another machine is "
      "not drift.")
    a("")
    a("## The project")
    a("")
    a(f"- **{p['name']} {p['version']}**, the `{p['fork_id']}` build of "
      f"[cyanreg/cyanrip]({UPSTREAM}), at [{REPO.split('github.com/')[1]}]"
      f"({REPO}). The only branch a consumer builds is `platterpus-fork`; "
      f"`master` mirrors upstream.")
    a(f"- **Language: C**, `c_std={p['c_std']}`, built with meson "
      f"(`meson_version: '{p['meson']}'`), and "
      + ", ".join(f"`{x}`" for x in p["werror"]) + ".")
    a("- **Tools and tests: Python 3, standard library only**"
      + (" — derived: no third-party import in `tools/` or `tests/`."
         if not model["python_third_party"] else
         ". Third-party imports: " + ", ".join(
             f"`{k}` ({', '.join(v)})"
             for k, v in model["python_third_party"].items()) + ".")
      + " No minimum Python version is declared anywhere in the tree.")
    a(f"- **Licence: {p['licence']}**, read from `src/utils.c`'s header. "
      "The binary links libcdio and libcdio-paranoia, both GPL-3.0-or-later, "
      "so a built binary is subject to the GPL's terms; upstream's is too.")
    a("")
    a("## Libraries linked")
    a("")
    a("Declared in `src/meson.build`. The minimum is what the build requires; "
      "what is installed here is under *Measured*.")
    a("")
    a("| library | project | minimum | required | licence | used for |")
    a("|---|---|---|---|---|---|")
    for lib in model["libs"]:
        proj, url, lic, why = LIBS[lib["name"]]
        pj = f"[{proj}]({url})" if url else proj
        a(f"| `{lib['name']}` | {pj} | {lib['declared'] or 'none'} | "
          f"{'yes' if lib['required'] else 'no'} | {lic or '—'} | {why} |")
    a("")
    a("## Building and testing")
    a("")
    a(f"- **meson** {p['meson']}, **ninja**, **pkg-config** and a **C "
      f"compiler**, with " + ", ".join(f"`{x}`" for x in p["werror"])
      + " making those warnings errors.")
    a("- **Programs the tools and tests run**, derived from their subprocess "
      "calls:")
    a("")
    a("| program | run by | for |")
    a("|---|---|---|")
    for prog, files in model["programs"].items():
        shown = ", ".join(f"`{f}`" for f in files[:4]) + (
            f" and {len(files) - 4} more" if len(files) > 4 else "")
        a(f"| `{prog}` | {shown} | {PROGRAMS[prog]} |")
    a("")
    c = model["ci"]
    a("## Continuous integration")
    a("")
    a("GitHub Actions, `.github/workflows/main.yml`, on pushes to `master`, "
      "`workflow` and `platterpus-fork`.")
    a("")
    a("- **Runners:** " + ", ".join(f"`{r}`" for r in c["runners"]) + ".")
    a("- **Actions:** " + ", ".join(f"`{x}`" for x in c["actions"])
      + ". Each is pinned by tag, not by commit.")
    a("- **Linux packages (apt):** " + ", ".join(f"`{x}`" for x in c["apt"])
      + ".")
    a("- **macOS packages (brew):** " + ", ".join(f"`{x}`" for x in c["brew"])
      + ".")
    a("- **Windows packages (MSYS2):** " + ", ".join(f"`{x}`" for x in c["msys"])
      + ".")
    a("- **Sources the Windows build clones**, `.github/mingw-build.sh`, "
      + ("pinned" if c["clone_pinned"] else
         "**unpinned: `git clone --depth 1` of each default branch, so the "
         "Windows build is of whatever those branches held that day**")
      + ": " + ", ".join(f"<{u}>" for u in c["clones"]) + ".")
    a("")
    a("## Network services cyanrip contacts")
    a("")
    a("| service | endpoint in `src/` | fetched by cyanrip | disabled by | what for |")
    a("|---|---|---|---|---|")
    for host, uses in model["endpoints"].items():
        title, fetched, flag, why = SERVICES[host]
        eps = "<br>".join(f"`{u}` ({f})" for u, f in uses)
        a(f"| {title} | {eps} | {'yes' if fetched else 'no'} | `{flag}` | {why} |")
    a("")
    a("## Projects this one sits between")
    a("")
    a(f"- **Upstream: [cyanreg/cyanrip]({UPSTREAM}).** `master` mirrors it and "
      f"is never committed to. Defects found here that exist there go upstream: "
      f"`docs/upstream/defect-reports.md`, checked by `tools/check-settled.py`.")
    a(f"- **Consumer: [Platterpus]({CONSUMER}).** It installs the build "
      "`release-manifest.json` names and parses the log as "
      "`PROVIDER-CONTRACT.md` describes. The two projects exchange laps under "
      "`docs/handshake/` and share four documents, checked byte for byte by "
      "`tools/seam-sync-check.py --fetch`:")
    a("")
    a("| shared document | ours | theirs |")
    a("|---|---|---|")
    for d in model["shared"]:
        a(f"| {d['key']} | `{d['ours']}` | `{d['theirs']}` |")
    a("")
    a("- **Releases this tree publishes**, from `release-manifest.json`:")
    for ch, r in model["releases"].items():
        a(f"  - `{ch}`: `{r['version']}` at `{r['commit']}`, release_seq "
          f"{r['seq']}")
    a("- **Libraries whose defects are worked around here** are named in the "
      "next section; their upstreams are in the libraries table.")
    a("")
    a("## External defects worked around (local mitigations)")
    a("")
    a("Each is a liability with a removal condition, not a fix. The details "
      "and what would end each are in `CLAUDE.md`, *Known external bugs "
      "worked around here*, from which this list is read:")
    a("")
    for t in model["mitigations"]:
        a(f"- {t}")
    a("")
    a(MD_MEASURED_MARK)
    a("")
    if not meas:
        a("Nothing was measured.")
        return "\n".join(w) + "\n"
    env = meas["_env"]
    a(f"- **Machine:** {env.get('os') or 'unknown'}; Python {env['python']}; "
      f"{env.get('cc') or 'no cc'}; meson {env.get('meson')}; ninja "
      f"{env.get('ninja')}; pkg-config {env.get('pkg_config')}; "
      f"{env.get('git') or 'no git'}.")
    if env.get("ffmpeg"):
        a(f"- **FFmpeg:** {env['ffmpeg']}"
          + ("; configured `--enable-gpl`, so the FFmpeg libraries as built "
             "here are GPL-2.0-or-later rather than LGPL."
             if env.get("ffmpeg_gpl") else "."))
    if meas.get("_fork_point"):
        a(f"- **Fork point against upstream:** `{meas['_fork_point']}` "
          f"(`git merge-base HEAD master`); upstream mirror tip "
          f"`{meas.get('_upstream_tip')}`.")
    missing = [k[4:] for k, v in env.items() if k.startswith("has ") and not v]
    if missing:
        a("- **Programs above not installed here:** "
          + ", ".join(f"`{x}`" for x in missing)
          + ". The rig-only ones are expected to be missing.")
    a("")
    a("| library | installed here | licence confirmed from |")
    a("|---|---|---|")
    for lib in model["libs"]:
        mm = meas.get(lib["name"], {})
        a(f"| `{lib['name']}` | {mm.get('version') or 'not found'} | "
          f"{mm.get('licence_evidence') or 'not confirmed here'} |")
    return "\n".join(w) + "\n"


def declared_md(text):
    return text.split(MD_MEASURED_MARK)[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when either file is stale; measured parts "
                         "are not compared")
    args = ap.parse_args()
    model = describe()
    if args.check:
        stale = []
        want = strip_measured(bom(model, None))
        try:
            have = strip_measured(json.loads(BOM_PATH.read_text()))
        except (OSError, ValueError) as e:
            have = None
            stale.append(f"{BOM_PATH.name}: unreadable ({e})")
        if have is not None and have != want:
            stale.append(f"{BOM_PATH.name} differs from what the tree declares")
        try:
            md = MD_PATH.read_text(encoding="utf-8")
        except OSError as e:
            md = None
            stale.append(f"{MD_PATH.relative_to(ROOT)}: unreadable ({e})")
        if md is not None and declared_md(md) != declared_md(markdown(model, None)):
            stale.append(f"{MD_PATH.relative_to(ROOT)} differs from what the "
                         f"tree declares")
        if stale:
            print("STALE: " + "; ".join(stale)
                  + "\nRegenerate with tools/gen-dependency-map.py.")
            return 1
        print("dependency map is current (measured parts not compared)")
        return 0
    meas = measure(model)
    BOM_PATH.write_text(json.dumps(bom(model, meas), indent=2,
                                   ensure_ascii=False) + "\n", encoding="utf-8")
    MD_PATH.write_text(markdown(model, meas), encoding="utf-8")
    print(f"wrote {BOM_PATH.relative_to(ROOT)} and {MD_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
