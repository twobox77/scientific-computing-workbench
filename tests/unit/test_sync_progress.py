"""Unit tests for the README progress-table generator (``scripts/sync_progress.py``)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "sync_progress.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("sync_progress", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sp = _load()

SPEC_TEXT = """\
# Spec

## 11. 後續版本方向

- **0.2：** Tensor、tensor product、contraction、基底與座標表示。
- **0.7：** Physics models 與 simulation。
- **1.0：** 穩定公開 API。

---

## 12. Next
"""

CHANGELOG_TEXT = """\
# Changelog

## [Unreleased]

## [0.2.0] - 2026-11-16

- Tensor.

## [0.1.0] - 2026-11-16

- Core.
"""

README_TEXT = f"""\
# Title

各版本狀態：

{sp.START}
old stale row
{sp.END}

after.
"""


@pytest.fixture
def repo(tmp_path: Path) -> tuple[Path, Path, Path]:
    spec = tmp_path / "spec.md"
    changelog = tmp_path / "CHANGELOG.md"
    readme = tmp_path / "README.md"
    spec.write_text(SPEC_TEXT, encoding="utf-8")
    changelog.write_text(CHANGELOG_TEXT, encoding="utf-8")
    readme.write_text(README_TEXT, encoding="utf-8")
    return readme, spec, changelog


def test_normalize_pads_to_three_parts() -> None:
    assert sp.normalize("0.2") == "0.2.0"
    assert sp.normalize("1.0") == "1.0.0"
    assert sp.normalize("0.6.0") == "0.6.0"


def test_display_drops_zero_patch() -> None:
    assert sp.display("0.7") == "0.7"
    assert sp.display("1.0") == "1.0"
    assert sp.display("0.6.1") == "0.6.1"


def test_spec_roadmap_parses_section_11(repo: tuple[Path, Path, Path]) -> None:
    _, spec, _ = repo
    roadmap = sp.spec_roadmap(spec)
    assert roadmap == {
        "0.2.0": "Tensor、tensor product、contraction、基底與座標表示",
        "0.7.0": "Physics models 與 simulation",
        "1.0.0": "穩定公開 API",
    }


def test_changelog_versions_only_dated_sections(repo: tuple[Path, Path, Path]) -> None:
    _, _, changelog = repo
    assert sp.changelog_versions(changelog) == {"0.2.0", "0.1.0"}


def test_spec_and_changelog_versions_merge(repo: tuple[Path, Path, Path]) -> None:
    """The spec's ``0.2`` and the changelog's ``0.2.0`` must be one row, not two."""
    _, spec, changelog = repo
    table = sp.render_table(spec, changelog, {})
    assert table.count("[0.2.0]") == 1  # one row, not a released + a planned twin
    assert "| 0.2 |" not in table  # no duplicate unnormalized row


def test_released_and_planned_status(repo: tuple[Path, Path, Path]) -> None:
    _, spec, changelog = repo
    table = sp.render_table(spec, changelog, {})
    # 0.2.0 is the newest dated section -> latest; 0.1.0 is released but older.
    assert table.count("✅ 最新") == 1
    assert "✅ 已發行" in table
    assert "| 0.7 | Physics models 與 simulation | ⏳ 規劃中 |" in table
    assert "| 1.0 | 穩定公開 API | ⏳ 規劃中 |" in table


def test_sync_rewrites_stale_block(repo: tuple[Path, Path, Path]) -> None:
    readme, spec, changelog = repo
    assert sp.sync(readme, spec, changelog, check=False, milestones={}) == 0
    text = readme.read_text(encoding="utf-8")
    assert "old stale row" not in text
    assert text.startswith("# Title")
    assert text.rstrip().endswith("after.")


def test_sync_check_flags_stale_then_passes(repo: tuple[Path, Path, Path]) -> None:
    readme, spec, changelog = repo
    assert sp.sync(readme, spec, changelog, check=True, milestones={}) == 1  # stale
    sp.sync(readme, spec, changelog, check=False, milestones={})
    assert sp.sync(readme, spec, changelog, check=True, milestones={}) == 0  # now fresh


def test_sync_is_idempotent(repo: tuple[Path, Path, Path]) -> None:
    readme, spec, changelog = repo
    sp.sync(readme, spec, changelog, check=False, milestones={})
    once = readme.read_text(encoding="utf-8")
    sp.sync(readme, spec, changelog, check=False, milestones={})
    assert readme.read_text(encoding="utf-8") == once


def test_sync_requires_markers(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("# no markers here\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        sp.sync(
            readme,
            tmp_path / "spec.md",
            tmp_path / "CHANGELOG.md",
            check=True,
            milestones={},
        )


def test_real_readme_progress_table_is_current() -> None:
    """Guard: the committed README must match the generator's output."""
    assert sp.sync(check=True) == 0
