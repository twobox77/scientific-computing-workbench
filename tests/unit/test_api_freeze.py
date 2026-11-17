"""Unit tests for the public-API freeze tool (``scripts/public_api.py``)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "public_api.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("public_api", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pa = _load()


# --- discover: the surface is exactly each namespace's __all__ ----------------


def test_discover_covers_every_declared_namespace() -> None:
    surface = pa.discover()
    assert set(surface) == set(pa.NAMESPACES)


def test_discover_names_are_sorted_and_unique() -> None:
    for names in pa.discover().values():
        assert names == sorted(names)
        assert len(names) == len(set(names))


def test_discover_matches_each_module_all() -> None:
    """The discovered surface must be exactly the modules' own ``__all__``."""
    surface = pa.discover()
    for namespace, names in surface.items():
        module = __import__(namespace, fromlist=["__all__"])
        assert names == sorted(module.__all__)


def test_core_namespaces_are_non_empty() -> None:
    surface = pa.discover()
    for namespace in ("scw", "scw.math_core", "scw.numerical"):
        assert surface[namespace]


def test_public_namespaces_all_define_all() -> None:
    """A public namespace without ``__all__`` is an error, not a silent pass."""
    for namespace in pa.NAMESPACES:
        module = __import__(namespace, fromlist=["__all__"])
        assert hasattr(module, "__all__"), namespace


# --- render: the snapshot and the table are derived from the surface ---------


def test_render_snapshot_round_trips() -> None:
    surface = {"scw": {"stability": "stable", "names": ["Matrix", "Vector"]}}
    text = pa.render_snapshot(surface)
    assert json.loads(text) == {"namespaces": surface}
    assert text.endswith("\n")


def test_surface_attaches_a_stability_level_to_every_namespace() -> None:
    contract = pa.surface()
    assert set(contract) == set(pa.NAMESPACES)
    for entry in contract.values():
        assert entry["stability"] in pa.VALID_LEVELS
        assert entry["names"] == sorted(entry["names"])


def test_render_table_is_fenced_by_markers() -> None:
    table = pa.render_table({"scw": {"stability": "stable", "names": ["Vector"]}})
    lines = table.splitlines()
    assert lines[0] == pa.START
    assert lines[-1] == pa.END
    assert "| `scw` | stable | `Vector` |" in table


def test_render_table_lists_names_in_order() -> None:
    table = pa.render_table({"scw": {"stability": "stable", "names": ["A", "B", "C"]}})
    assert "`A`, `B`, `C`" in table


# --- check: drift is detected, a clean tree passes ---------------------------


def test_diff_reports_added_and_removed() -> None:
    committed = {"scw": {"stability": "stable", "names": ["A", "B"]}}
    discovered = {"scw": {"stability": "stable", "names": ["A", "C"]}}
    diff = pa._diff(committed, discovered)
    assert "+ scw.C" in diff
    assert "- scw.B" in diff


def test_diff_reports_new_and_gone_namespaces() -> None:
    diff = pa._diff(
        {"scw.a": {"stability": "stable", "names": ["X"]}},
        {"scw.b": {"stability": "stable", "names": ["Y"]}},
    )
    assert "+ scw.b.Y" in diff
    assert "- scw.a.X" in diff


def test_diff_reports_a_stability_change() -> None:
    diff = pa._diff(
        {"scw": {"stability": "provisional", "names": ["A"]}},
        {"scw": {"stability": "stable", "names": ["A"]}},
    )
    assert "~ scw stability: provisional -> stable" in diff


def test_diff_is_empty_when_identical() -> None:
    surface = {
        "scw": {"stability": "stable", "names": ["A"]},
        "scw.b": {"stability": "stable", "names": ["B"]},
    }
    assert pa._diff(surface, dict(surface)) == []


def test_check_detects_drift_against_a_temp_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A committed snapshot missing a name makes ``--check`` fail (exit 1)."""
    api_md = tmp_path / "api.md"
    api_md.write_text(f"# api\n\n{pa.START}\n{pa.END}\n", encoding="utf-8")
    stale = tmp_path / "frozen.json"
    stale.write_text(
        json.dumps(
            {"namespaces": {"scw": {"stability": "stable", "names": ["Vector"]}}}
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(pa, "API_MD", api_md)
    monkeypatch.setattr(pa, "SNAPSHOT", stale)
    assert pa.sync(check=True) == 1


def test_sync_rewrites_snapshot_and_table(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api_md = tmp_path / "api.md"
    api_md.write_text(
        f"# api\n\n{pa.START}\nSTALE_PLACEHOLDER\n{pa.END}\n", encoding="utf-8"
    )
    snapshot = tmp_path / "frozen.json"
    monkeypatch.setattr(pa, "API_MD", api_md)
    monkeypatch.setattr(pa, "SNAPSHOT", snapshot)
    assert pa.sync(check=False) == 0
    assert "STALE_PLACEHOLDER" not in api_md.read_text(encoding="utf-8")
    assert pa.load_snapshot(snapshot) == pa.surface()
    # and the freshly written state now passes the check
    assert pa.sync(check=True) == 0


def test_sync_requires_markers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    api_md = tmp_path / "api.md"
    api_md.write_text("# no markers\n", encoding="utf-8")
    monkeypatch.setattr(pa, "API_MD", api_md)
    monkeypatch.setattr(pa, "SNAPSHOT", tmp_path / "frozen.json")
    with pytest.raises(SystemExit):
        pa.sync(check=True)


def test_discover_rejects_a_namespace_without_all(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A public namespace that forgets ``__all__`` must fail loudly."""

    class Bare:
        pass

    monkeypatch.setattr(pa, "NAMESPACES", ["scw._no_all_probe"])
    monkeypatch.setitem(sys.modules, "scw._no_all_probe", Bare())
    with pytest.raises(SystemExit):
        pa.discover()


# --- the committed artifacts are current -------------------------------------


def test_committed_snapshot_matches_discovery() -> None:
    """Guard: the committed snapshot must equal the live surface."""
    assert pa.load_snapshot() == pa.surface()


def test_real_public_api_is_frozen() -> None:
    """Guard: the committed snapshot and api.md table must both be current."""
    assert pa.sync(check=True) == 0


def test_every_public_namespace_is_stable_at_1_0() -> None:
    """At 1.0 the whole public surface is frozen: no provisional names remain."""
    assert set(pa.STABILITY.values()) == {"stable"}
    assert set(pa.load_snapshot()) == set(pa.NAMESPACES)


def test_stability_levels_are_a_known_vocabulary() -> None:
    for level in pa.STABILITY.values():
        assert level in pa.VALID_LEVELS
