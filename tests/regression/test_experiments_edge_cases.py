"""Regression tests for :mod:`scw.experiments`.

These pin the edge cases that are easy to get subtly wrong and would silently
break reproducibility: that the store writes atomically and reloads
identically, that a record's config and a dataset's columns cannot be mutated
through the returned object, that a dataset copies its input, and that a
non-finite dataset or an unserializable result is rejected rather than stored.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from scw.exceptions import ExperimentError
from scw.experiments import Dataset, Experiment, ResultStore, RunRecord
from scw.experiments.store import INDEX_NAME


def test_store_writes_no_temporary_leftovers(tmp_path: Path) -> None:
    store = ResultStore(tmp_path)
    store.save(RunRecord("run01", "exp", 0, results={"x": 1.0}))
    leftovers = [p.name for p in tmp_path.iterdir() if p.suffix == ".tmp"]
    assert leftovers == []
    assert (tmp_path / INDEX_NAME).exists()


def test_store_index_is_valid_json(tmp_path: Path) -> None:
    store = ResultStore(tmp_path)
    store.save(RunRecord("run01", "exp", 0, results={"x": 1.0}))
    index = json.loads((tmp_path / INDEX_NAME).read_text(encoding="utf-8"))
    assert index["run01"]["experiment"] == "exp"


def test_record_config_cannot_be_mutated_through_the_record() -> None:
    raw = {"a": 1}
    record = RunRecord("run01", "exp", 0, config=raw)
    raw["a"] = 99
    assert record.config["a"] == 1
    with pytest.raises(TypeError):
        record.config["b"] = 2  # type: ignore[index]


def test_dataset_copies_its_input_columns() -> None:
    raw = np.array([1.0, 2.0, 3.0])
    dataset = Dataset("d", {"x": raw})
    raw[0] = 99.0
    np.testing.assert_allclose(dataset["x"], [1.0, 2.0, 3.0])


def test_dataset_rejects_non_finite_columns() -> None:
    with pytest.raises(ExperimentError):
        Dataset("d", {"x": np.array([1.0, np.nan])})
    with pytest.raises(ExperimentError):
        Dataset("d", {"x": np.array([1.0, np.inf])})


def test_experiment_rejects_result_that_is_not_json_serializable() -> None:
    exp = Experiment("e", seed=1)

    def bad(_: Experiment) -> dict[str, object]:
        return {"handle": object()}

    with pytest.raises(ExperimentError):
        exp.run(bad)


def test_experiment_run_returns_none_results_as_empty() -> None:
    record = Experiment("e").run(lambda e: None)  # type: ignore[arg-type,return-value]
    assert record.ok
    assert dict(record.results) == {}


def test_store_query_returns_newest_first(tmp_path: Path) -> None:
    store = ResultStore(tmp_path)
    records = [
        RunRecord("a", "exp", 0, started_at="2026-01-01T00:00:01+00:00"),
        RunRecord("b", "exp", 0, started_at="2026-01-01T00:00:03+00:00"),
        RunRecord("c", "exp", 0, started_at="2026-01-01T00:00:02+00:00"),
    ]
    for record in records:
        store.save(record)
    assert [r.run_id for r in store.query()] == ["b", "c", "a"]


def test_dataset_split_preserves_spec_for_regeneration() -> None:
    ds = Dataset.generate("d", shape=(20, 1), seed=3)
    parts = ds.split([0.5, 0.5], seed=3)
    for part in parts:
        assert dict(part.spec) == dict(ds.spec)


def test_reopening_a_store_keeps_query_order(tmp_path: Path) -> None:
    store = ResultStore(tmp_path)
    store.save(RunRecord("a", "exp", 0, started_at="2026-01-01T00:00:01+00:00"))
    store.save(RunRecord("b", "exp", 0, started_at="2026-01-01T00:00:02+00:00"))
    reopened = ResultStore(tmp_path)
    assert [r.run_id for r in reopened.query()] == ["b", "a"]
