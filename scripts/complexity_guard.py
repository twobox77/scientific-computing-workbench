#!/usr/bin/env python3
"""Complexity guard: keep per-element loops out of the core.

The core's per-element work must be delegated to NumPy/SciPy.  A Python
``for``/``while`` loop over the *elements* of a vector, matrix or tensor is the
signature of an accidental O(n) rewrite of a vectorized operation, and it is
easy to introduce by hand.

This guard is a static (AST) check, so it is deterministic, instant and needs
no interpreter tracing: it fails if a core module contains a loop that is not
explicitly justified with a ``# complexity: ...`` comment on or above the loop
line.  Loops over small *metadata* (a list of basis vectors, the terms of an
einsum spec) are legitimate and carry that comment.

Usage::

    python scripts/complexity_guard.py            # checks src/scw by default
    python scripts/complexity_guard.py PATH ...   # check specific files/dirs

Exit code is non-zero when an unjustified loop is found.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

DEFAULT_TARGETS = ["src/scw"]
JUSTIFICATION = "# complexity:"


def _loop_line(node: ast.AST) -> int:
    return node.lineno


def _is_justified(lines: list[str], lineno: int) -> bool:
    """True if a ``# complexity:`` note sits on or above the loop line."""
    for index in (lineno - 1, lineno - 2):
        if 0 <= index < len(lines) and JUSTIFICATION in lines[index]:
            return True
    return False


def check_file(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    tree = ast.parse(source, filename=str(path))
    problems: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            if not _is_justified(lines, _loop_line(node)):
                problems.append(
                    f"{path}:{node.lineno}: loop without a '{JUSTIFICATION}' "
                    "note; delegate per-element work to NumPy/SciPy, or justify "
                    "why this loop is O(1) in the data size"
                )
    return problems


def iter_python_files(targets: list[str]) -> list[Path]:
    files: list[Path] = []
    for target in targets:
        path = Path(target)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.py")))
        elif path.suffix == ".py":
            files.append(path)
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "targets", nargs="*", default=DEFAULT_TARGETS, help="files or directories"
    )
    args = parser.parse_args(argv)

    problems: list[str] = []
    for path in iter_python_files(args.targets):
        problems.extend(check_file(path))

    if problems:
        print("\n".join(problems), file=sys.stderr)
        print(f"\n{len(problems)} unjustified loop(s) found.", file=sys.stderr)
        return 1
    print("Complexity guard: no unjustified per-element loops. PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
