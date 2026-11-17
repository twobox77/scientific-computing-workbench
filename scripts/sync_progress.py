#!/usr/bin/env python3
"""Keep the README progress table in sync with the release history.

The table is generated, never hand-edited, so a new release cannot silently
leave the landing page stale.  Sources of truth:

* the version list and the roadmap wording come from the specification's
  roadmap (``docs/spec/...`` §11);
* a version counts as *released* once ``CHANGELOG.md`` carries a dated
  ``## [x.y.z] - YYYY-MM-DD`` section for it (the same section the release
  notes are built from), so no git tags are needed;
* ``MILESTONES`` below holds the curated Chinese one-liners; any version not
  listed there falls back to the specification wording.

Usage::

    python scripts/sync_progress.py            # rewrite README.md
    python scripts/sync_progress.py --check    # fail if README.md is stale
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"
SPEC = ROOT / "docs" / "spec" / "SCW_1.0_Technical_Specification_and_Phase1_Plan.md"

START = "<!-- progress:start -->"
END = "<!-- progress:end -->"

RELEASE_URL = (
    "https://github.com/twobox77/scientific-computing-workbench/releases/tag/v{version}"
)

# Curated Chinese summaries for released versions.  Planned versions are not
# listed here on purpose: they fall back to the specification roadmap, so a
# new milestone needs no edit until it is released.
MILESTONES = {
    "0.1.0": (
        "工程骨架 + 數學核心（`VectorSpace` / `Vector` / `Covector` / "
        "`Matrix` / `LinearMap`）"
    ),
    "0.2.0": "`Tensor`、`Basis`；性質測試（Hypothesis）與回歸測試層",
    "0.3.0": "`scw.symbolic`（SymPy adapter）、`einsum`、複雜度護欄",
    "0.4.0": "`scw.numerical`：線性系統、分解（LU/QR/SVD/Cholesky/eigh）、ODE solver",
    "0.5.0": "`scw.visualization`：Matplotlib adapter（2D/3D 繪圖）",
    "0.6.0": "`scw.manifold`：切／餘切空間、metric、`flat` / `sharp`",
    "0.7.0": "`scw.physics`：質點、力模型、系統與牛頓模擬",
    "0.8.0": "`scw.experiments`：實驗追蹤、執行紀錄、可重現資料集與結果索引",
    "0.9.0": "公開 API 凍結與穩定性分級；`docs/stability.md` 棄用政策",
}


def normalize(version: str) -> str:
    """Canonical ``x.y.z`` so the spec's ``0.2`` and the changelog's ``0.2.0`` merge."""
    parts = [int(p) for p in re.findall(r"\d+", version)]
    parts += [0] * (3 - len(parts))
    return f"{parts[0]}.{parts[1]}.{parts[2]}"


def _key(version: str) -> tuple[int, int, int]:
    a, b, c = (int(p) for p in normalize(version).split("."))
    return a, b, c


def spec_roadmap(spec: Path = SPEC) -> dict[str, str]:
    """Normalized version -> milestone wording, parsed from the spec roadmap (§11)."""
    text = spec.read_text(encoding="utf-8")
    section = re.search(r"^## 11\..*?$(.*?)^---", text, re.DOTALL | re.MULTILINE)
    if section is None:
        raise SystemExit("could not find the roadmap (§11) in the specification")
    return {
        normalize(version): description
        for version, description in re.findall(
            r"^-\s*\*\*(\d+\.\d+(?:\.\d+)?)：\*\*\s*(.+?)。?\s*$",
            section.group(1),
            re.MULTILINE,
        )
    }


def changelog_versions(changelog: Path = CHANGELOG) -> set[str]:
    """Normalized versions with a dated section in the changelog (released)."""
    text = changelog.read_text(encoding="utf-8")
    return {
        normalize(version)
        for version in re.findall(
            r"^## \[(\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}$", text, re.MULTILINE
        )
    }


def display(version: str) -> str:
    """Planned versions read better as ``0.7`` / ``1.0`` than ``0.7.0``."""
    major, minor, patch = normalize(version).split(".")
    return f"{major}.{minor}" if patch == "0" else normalize(version)


def render_table(
    spec: Path = SPEC,
    changelog: Path = CHANGELOG,
    milestones: dict[str, str] = MILESTONES,
) -> str:
    roadmap = spec_roadmap(spec)
    curated = {normalize(v): text for v, text in milestones.items()}
    released = changelog_versions(changelog)

    known = set(roadmap) | set(curated) | released
    latest = max(released, key=_key) if released else None

    lines = [
        START,
        "| 版本 | 里程碑內容 | 狀態 |",
        "| --- | --- | --- |",
    ]
    for version in sorted(known, key=_key):
        body = curated.get(version) or roadmap.get(version, "（見規格 §11）")
        if version in released:
            label = "✅ 最新" if version == latest else "✅ 已發行"
            cell = f"[{version}]({RELEASE_URL.format(version=version)})"
        else:
            label = "⏳ 規劃中"
            cell = display(version)
        lines.append(f"| {cell} | {body} | {label} |")
    lines.append(END)
    return "\n".join(lines)


def current_block(text: str) -> str:
    start = text.index(START)
    end = text.index(END) + len(END)
    return text[start:end]


def sync(
    readme: Path = README,
    spec: Path = SPEC,
    changelog: Path = CHANGELOG,
    *,
    check: bool,
    milestones: dict[str, str] = MILESTONES,
) -> int:
    """Rewrite (or, with ``check``, verify) the progress table inside ``readme``."""
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit(f"{readme.name} must contain {START} and {END} markers")

    expected = render_table(spec, changelog, milestones)
    if check:
        if current_block(text) != expected:
            print(
                f"{readme.name} progress table is stale; "
                "run: python scripts/sync_progress.py"
            )
            return 1
        print(f"{readme.name} progress table is up to date.")
        return 0

    updated = text[: text.index(START)] + expected + text[text.index(END) + len(END) :]
    if updated != text:
        readme.write_text(updated, encoding="utf-8")
        print(f"{readme.name} progress table updated.")
    else:
        print(f"{readme.name} progress table already up to date.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if README.md is not up to date instead of rewriting it",
    )
    args = parser.parse_args(argv)
    return sync(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
