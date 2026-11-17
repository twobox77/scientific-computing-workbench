#!/usr/bin/env python3
"""Freeze and verify SCW's public API surface.

The public surface is exactly what each public namespace re-exports in its
``__all__``; nothing else is promised, and private modules (``_backend``,
``objects``, ...) may change freely.  This tool has two jobs:

* **freeze** — discover the surface and write it to
  ``docs/public-api-frozen.json`` (the committed contract) and to the
  generated block inside ``docs/api.md``;
* **check** — compare the discovered surface against the committed JSON and
  fail (non-zero) if a name or a stability level changed, so an accidental
  public change cannot slip in unnoticed.

The per-namespace stability level is editorial and lives in ``STABILITY``
below (the single source of truth), the same way ``sync_progress.MILESTONES``
holds the curated release blurbs.  It is written into the snapshot too, so the
level is machine-checked rather than only prose.

Usage::

    python scripts/public_api.py            # rewrite the snapshot and api.md
    python scripts/public_api.py --check    # fail if either is stale
"""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
API_MD = ROOT / "docs" / "api.md"
SNAPSHOT = ROOT / "docs" / "public-api-frozen.json"

START = "<!-- public-api:start -->"
END = "<!-- public-api:end -->"

#: The public namespaces, in documentation order.  Adding a layer is a
#: deliberate act: extend this list *and* the snapshot together.
NAMESPACES = [
    "scw",
    "scw.config",
    "scw.exceptions",
    "scw.math_core",
    "scw.numerical",
    "scw.manifold",
    "scw.physics",
    "scw.experiments",
    "scw.symbolic",
    "scw.visualization",
]

#: Stability level per public namespace (see ``docs/stability.md``).  At 1.0
#: every public namespace is ``stable``; the vocabulary (``provisional``,
#: ``experimental``, ``deprecated``) stays available for future evolution.
STABILITY = {namespace: "stable" for namespace in NAMESPACES}

VALID_LEVELS = ("stable", "provisional", "experimental", "deprecated")


def discover() -> dict[str, list[str]]:
    """Import every public namespace and read the names it re-exports."""
    surface: dict[str, list[str]] = {}
    for namespace in NAMESPACES:
        try:
            module = importlib.import_module(namespace)
        except ImportError as exc:  # an optional extra is not installed
            raise SystemExit(
                f"cannot import {namespace}: {exc}\n"
                "install every extra first: uv sync --all-extras"
            ) from exc
        names = getattr(module, "__all__", None)
        if names is None:
            raise SystemExit(
                f"{namespace} does not define __all__; the public surface is "
                "defined by __all__, so every public namespace must have one"
            )
        surface[namespace] = sorted(names)
    return surface


def surface() -> dict[str, dict[str, Any]]:
    """The full contract: each namespace's stability level and names."""
    names = discover()
    return {
        namespace: {"stability": STABILITY[namespace], "names": names[namespace]}
        for namespace in NAMESPACES
    }


def load_snapshot(path: Path = SNAPSHOT) -> dict[str, dict[str, Any]]:
    data: dict[str, dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))[
        "namespaces"
    ]
    return data


def _diff(
    committed: dict[str, dict[str, Any]],
    discovered: dict[str, dict[str, Any]],
) -> list[str]:
    """Human-readable differences between the snapshot and reality."""
    lines: list[str] = []
    for namespace in sorted(set(committed) | set(discovered)):
        old = committed.get(namespace, {})
        new = discovered.get(namespace, {})
        old_names = set(old.get("names", []))
        new_names = set(new.get("names", []))
        for name in sorted(new_names - old_names):
            lines.append(f"+ {namespace}.{name}")
        for name in sorted(old_names - new_names):
            lines.append(f"- {namespace}.{name}")
        if old.get("stability") != new.get("stability") and old and new:
            lines.append(
                f"~ {namespace} stability: "
                f"{old.get('stability')} -> {new.get('stability')}"
            )
    return lines


def render_snapshot(surface: dict[str, dict[str, Any]]) -> str:
    return json.dumps({"namespaces": surface}, indent=2, sort_keys=True) + "\n"


def render_table(surface: dict[str, dict[str, Any]]) -> str:
    lines = [
        START,
        "| Namespace | Stability | Public names |",
        "| --- | --- | --- |",
    ]
    for namespace, entry in surface.items():
        names = ", ".join(f"`{name}`" for name in entry["names"])
        lines.append(f"| `{namespace}` | {entry['stability']} | {names} |")
    lines.append(END)
    return "\n".join(lines)


def _current_block(text: str) -> str:
    return text[text.index(START) : text.index(END) + len(END)]


def sync(check: bool) -> int:
    """Rewrite (or, with ``check``, verify) the snapshot and the api.md block."""
    for namespace, level in STABILITY.items():
        if level not in VALID_LEVELS:
            raise SystemExit(f"{namespace}: unknown stability level {level!r}")
    discovered = surface()

    if check:
        committed = load_snapshot()
        problems: list[str] = []
        if committed != discovered:
            problems += _diff(committed, discovered)
        text = API_MD.read_text(encoding="utf-8")
        if START not in text or END not in text:
            raise SystemExit(f"{API_MD.name} must contain {START} and {END} markers")
        if _current_block(text) != render_table(discovered):
            problems.append("api.md frozen table is stale")
        if problems:
            print("public API surface changed:")
            for problem in problems:
                print(f"  {problem}")
            print("run: python scripts/public_api.py")
            return 1
        print("public API surface matches the frozen snapshot.")
        return 0

    SNAPSHOT.write_text(render_snapshot(discovered), encoding="utf-8")
    text = API_MD.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit(f"{API_MD.name} must contain {START} and {END} markers")
    table = render_table(discovered)
    updated = text[: text.index(START)] + table + text[text.index(END) + len(END) :]
    if updated != text:
        API_MD.write_text(updated, encoding="utf-8")
    total = sum(len(entry["names"]) for entry in discovered.values())
    print(f"public API surface: {total} names across {len(discovered)} namespaces.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the surface or the api.md table is stale",
    )
    args = parser.parse_args(argv)
    return sync(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
