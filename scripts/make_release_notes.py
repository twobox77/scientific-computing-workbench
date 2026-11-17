#!/usr/bin/env python3
"""Compose the GitHub release notes for a version.

Every SCW release gets the same Chinese companion guide (install /
appreciate / operate / uninstall), so the notes are built from a single
source rather than pasted by hand:

* the English "what changed" section is read from ``CHANGELOG.md``;
* the Chinese guide is read from ``docs/offline.md`` (the documentation
  page), with the version strings rewritten to the target release;
* the works (examples / notebooks) added by this release are derived from
  git history.

Usage::

    python scripts/make_release_notes.py 0.7.0            # print to stdout
    python scripts/make_release_notes.py v0.7.0 -o notes.md
    GITHUB_REF_NAME=v0.7.0 python scripts/make_release_notes.py
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
GUIDE = ROOT / "docs" / "offline.md"

FOOTER = "---\n_本說明由 AI agent（OpenHands）代為撰寫。_"

GUIDE_NOTE = (
    "> 本中文說明以目前版本的工具鏈為準；若你的版本較舊，"
    "部分範例或 optional extra 可能尚未提供。"
)

# Chinese one-liners for the works, keyed by repository path.  Add a row
# here when a new example or notebook lands so the release notes stay
# readable (the path itself is used as a fallback).
WORK_DESCRIPTIONS = {
    "examples/01_vectors_and_covectors.py": "向量、餘向量與自然配對",
    "examples/02_matrix_operations.py": "矩陣、線性映射與解線性系統",
    "examples/03_tensor_operations.py": "張量：外積、縮併與跡",
    "examples/04_bases_and_coordinates.py": "基底與座標：端到端數值流程",
    "examples/05_symbolic_algebra.py": "符號線性代數（需 symbolic extra）",
    "examples/06_decompositions.py": "矩陣分解：LU / QR / SVD / Cholesky / eigh",
    "examples/07_ode_solving.py": "常微分方程初值問題（衰減、簡諧振子）",
    "examples/08_visualization.py": "Matplotlib 繪圖（需 visualization extra）",
    "examples/09_manifolds.py": "流形：切空間、metric、flat/sharp",
    "examples/10_physics_simulation.py": "物理模擬：拋體、彈簧振子、行星軌道",
    "notebooks/01_scw_quickstart.ipynb": "基礎導覽",
    "notebooks/02_manifolds.ipynb": "流形靜態教學（已內嵌圖）",
    "notebooks/03_manifolds_interactive.ipynb": (
        "流形互動教學（3D 可拖曳，需 interactive extra）"
    ),
}


def current_version() -> str:
    """Version declared in ``pyproject.toml`` (the version being released)."""
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if match is None:
        raise SystemExit("could not read version from pyproject.toml")
    return match.group(1)


def changelog_section(version: str) -> str:
    """The ``## [version]`` block of ``CHANGELOG.md``, link refs excluded."""
    text = CHANGELOG.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|^\[Unreleased\]:)",
        re.DOTALL | re.MULTILINE,
    )
    match = pattern.search(text)
    if match is None:
        raise SystemExit(f"CHANGELOG.md has no section for {version}")
    return match.group(0).rstrip()


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return result.stdout


def _ref_exists(ref: str) -> bool:
    return bool(_git("rev-parse", "--verify", "--quiet", ref).strip())


def added_works(tag: str) -> list[str]:
    """Examples / notebooks first added between the previous tag and ``tag``."""
    if not _ref_exists(tag):
        tag = "HEAD"
    previous = _git("describe", "--tags", "--abbrev=0", f"{tag}^").strip()
    span = f"{previous}..{tag}" if previous else tag
    out = _git(
        "log",
        "--diff-filter=A",
        "--name-only",
        "--format=",
        span,
        "--",
        "examples",
        "notebooks",
    )
    return sorted({line.strip() for line in out.splitlines() if line.strip()})


def _demote_headings(text: str) -> str:
    """Demote ATX headings one level, leaving fenced code blocks untouched."""
    lines = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            lines.append(line)
            continue
        if not in_fence:
            if line.startswith("### "):
                line = "#" + line
            elif line.startswith("## "):
                line = "#" + line
        lines.append(line)
    return "\n".join(lines)


def guide(version: str) -> str:
    """The Chinese guide from ``docs/offline.md``, retargeted to ``version``.

    Only ``scw-<semver>`` tokens (tarball, wheel, ``cd`` target) are
    rewritten; unrelated version numbers such as uv's own ``0.5.0`` are left
    untouched.
    """
    text = GUIDE.read_text(encoding="utf-8")
    body = text[text.index("## ") :]
    body = re.sub(r"scw-\d+\.\d+\.\d+", f"scw-{version}", body)
    return _demote_headings(body).rstrip()


def works_section(tag: str) -> str:
    works = added_works(tag)
    if not works:
        return ""
    lines = ["### 本版新增作品", ""]
    for path in works:
        note = WORK_DESCRIPTIONS.get(path, "（見該檔說明）")
        lines.append(f"- `{path}` — {note}")
    lines.append("")
    return "\n".join(lines)


def render(version: str, tag: str) -> str:
    parts = [
        changelog_section(version),
        "",
        "---",
        "",
        "## 離線欣賞與操作（中文說明）",
        "",
        GUIDE_NOTE,
        "",
    ]
    section = works_section(tag)
    if section:
        parts.append(section)
    parts.append(guide(version))
    parts.append("")
    parts.append(FOOTER)
    return "\n".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "version",
        nargs="?",
        default=os.environ.get("GITHUB_REF_NAME", ""),
        help="version or tag, e.g. 0.7.0 or v0.7.0 (default: $GITHUB_REF_NAME)",
    )
    parser.add_argument("-o", "--output", help="write to this file instead of stdout")
    args = parser.parse_args(argv)

    if not args.version:
        raise SystemExit("no version given (pass it or set $GITHUB_REF_NAME)")

    version = args.version.lstrip("v")
    tag = args.version if args.version.startswith("v") else f"v{version}"
    notes = render(version, tag)

    if args.output:
        Path(args.output).write_text(notes, encoding="utf-8")
    else:
        print(notes, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
