#!/usr/bin/env python3
"""Every text read, write and subprocess pipe in tools/ and tests/ names its
encoding (review C item 6.5).

Without one, Python uses the locale's: UTF-8 on the Linux and macOS machines
that run these today, and something else on a machine set up otherwise, where
a log, a lap or git's output would be read differently. Found by the AST, not
by a pattern, so a call split over lines counts:

  * Path.read_text() and Path.write_text(data);
  * open() in a text mode;
  * subprocess's run, check_output, check_call, call and Popen with text=True
    or universal_newlines=True.

A call passing *args or **kwargs is not judged, since what it passes cannot be
read here; nor is open() with a mode computed at run time.
"""

import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUBPROC = {"run", "check_output", "check_call", "call", "Popen"}


def kw(call, name):
    return next((k for k in call.keywords if k.arg == name), None)


def unnamed(call):
    """True when the call does text I/O and names no encoding"""
    if any(isinstance(a, ast.Starred) for a in call.args):
        return False
    if any(k.arg is None for k in call.keywords) or kw(call, "encoding"):
        return False
    f = call.func
    if isinstance(f, ast.Attribute) and f.attr == "read_text":
        return not call.args
    if isinstance(f, ast.Attribute) and f.attr == "write_text":
        return len(call.args) == 1
    if isinstance(f, ast.Name) and f.id == "open":
        if len(call.args) > 3:
            return False
        mode = call.args[1] if len(call.args) > 1 else (
            kw(call, "mode").value if kw(call, "mode") else None)
        if mode is None:
            return True
        if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
            return "b" not in mode.value
        return False
    name = f.attr if isinstance(f, ast.Attribute) else (
        f.id if isinstance(f, ast.Name) else None)
    if name in SUBPROC and (isinstance(f, ast.Name) or (
            isinstance(f.value, ast.Name) and f.value.id == "subprocess")):
        for flag in ("text", "universal_newlines"):
            k = kw(call, flag)
            if k and isinstance(k.value, ast.Constant) and k.value.value is True:
                return True
    return False


files = sorted(p for d in ("tools", "tests") for p in (ROOT / d).glob("*.py"))
if len(files) < 50:
    print(f"FAIL: {len(files)} Python files in tools/ and tests/, expected "
          "over 50; the glob has stopped matching")
    sys.exit(1)

calls = bad = 0
for p in files:
    tree = ast.parse(p.read_text(encoding="utf-8"), str(p))
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        name = f.attr if isinstance(f, ast.Attribute) else (
            f.id if isinstance(f, ast.Name) else None)
        if name in {"read_text", "write_text", "open"} | SUBPROC:
            calls += 1
        if unnamed(n):
            bad += 1
            print(f"FAIL: {p.relative_to(ROOT)}:{n.lineno}: {name}() names "
                  "no encoding")

if bad:
    print(f"{bad} call(s) without an encoding")
    sys.exit(1)
if calls < 300:
    print(f"FAIL: only {calls} I/O calls seen; the walk has stopped finding them")
    sys.exit(1)
print(f"{calls} I/O calls in {len(files)} files: each text one names its encoding")
