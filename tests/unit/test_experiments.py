"""Unit tests for :mod:`scw.experiments` (records, experiments, store, datasets)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from scw.exceptions import ExperimentError
from scw.experiments import (
    GENERATORS,
    Artifact,
    Dataset,
    Experiment,
    ResultStore,
    RunRecord,
    canonical_json,
    derive_seed,
    environment_fingerprint,
    jsonable,
)


# --------------------------------------------------------------------------- #
# records helpers
# --------------------------------------------------------------------------- #
def test_jsonable_converts_common_types() -> None:
    assert jsonable(np.int64(3)) == 3
    assert jsonable(np.float64(1.5)) == 1.5
    assert jsonable(np.array([1.0, 2.0])) == [1.0, 2.0]
    assert jsonable(Path("/tmp/x")) == "/tmp/x"
    assert jsonable({1: np.float32(2.0)}) == {"1": 2.0}
    assert jsonable({3, 1, 2}) == [1, 2, 3]


def test_jsonable_uses_domain_data_attribute() -> None:
    from scw.math_core import Vector

    assert jsonable(Vector([1.0, 2.0])) == [1.0, 2.0]


def test_jsonable_rejects_unknown_type() -> None:
    with pytest.raises(ExperimentError):
        jsonable(object())


def test_canonical_json_is_key_order_independent() -> None:
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})


def test_derive_seed_is_deterministic_and_label_sensitive() -> None:
    assert derive_seed(42, "a") == derive_seed(42, "a")
    assert derive_seed(42, "a") != derive_seed(42, "b")
    assert 0 <= derive_seed(42, "a") < 2**63


def test_environment_fingerprint_has_versions() -> None:
    fingerprint = environment_fingerprint()
    assert set(fingerprint) >= {"python", "numpy", "scipy", "scw"}


# --------------------------------------------------------------------------- #
# Artifact / RunRecord
# --------------------------------------------------------------------------- #
def test_artifact_requires_name_and_path() -> None:
    with pytest.raises(ExperimentError):
        Artifact("", "x")
    with pytest.raises(ExperimentError):
        Artifact("x", "")


def test_run_record_round_trips_through_dict() -> None:
    record = RunRecord(
        run_id="abc",
        experiment="exp",
        seed=1,
        config={"a": 1},
        results={"loss": 0.5},
        tags=("t",),
        artifacts=(Artifact("plot", "p.png"),),
        environment={"python": "3.12"},
        started_at="2026-01-01T00:00:00+00:00",
        duration_seconds=0.25,
    )
    assert RunRecord.from_dict(record.to_dict()) == record


def test_run_record_error_status_requires_message() -> None:
    with pytest.raises(ExperimentError):
        RunRecord("abc", "exp", 0, status="error")
    with pytest.raises(ExperimentError):
        RunRecord("abc", "exp", 0, status="weird")


def test_run_record_config_is_immutable() -> None:
    record = RunRecord("abc", "exp", 0, config={"a": 1})
    with pytest.raises(TypeError):
        record.config["a"] = 2  # type: ignore[index]


# --------------------------------------------------------------------------- #
# Experiment
# --------------------------------------------------------------------------- #
def test_experiment_validates_name_and_seed() -> None:
    with pytest.raises(ExperimentError):
        Experiment("")
    with pytest.raises(ExperimentError):
        Experiment("ok", seed=1.5)  # type: ignore[arg-type]
    with pytest.raises(ExperimentError):
        Experiment("ok", seed=True)


def test_experiment_rejects_unserializable_config() -> None:
    with pytest.raises(ExperimentError):
        Experiment("ok", config={"bad": object()})


def test_experiment_rng_is_reproducible_and_labeled() -> None:
    exp = Experiment("e", seed=7)
    a = exp.rng("x").normal(size=5)
    b = exp.rng("x").normal(size=5)
    c = exp.rng("y").normal(size=5)
    np.testing.assert_array_equal(a, b)
    assert not np.array_equal(a, c)


def test_experiment_run_records_results_and_environment() -> None:
    exp = Experiment("e", seed=3, config={"n": 2}, tags=("t",))
    record = exp.run(lambda e: {"value": e.config["n"] * 2})
    assert record.ok
    assert record.results["value"] == 4
    assert record.tags == ("t",)
    assert "python" in record.environment
    assert record.duration_seconds >= 0.0


def test_experiment_run_id_is_deterministic() -> None:
    exp = Experiment("e", seed=1, config={"n": 2})
    assert exp.run_id() == exp.run_id()
    assert exp.run_id(label="a") != exp.run_id(label="b")


def test_experiment_run_captures_error_when_asked() -> None:
    exp = Experiment("e", seed=1)

    def boom(_: Experiment) -> dict[str, float]:
        raise RuntimeError("nope")

    record = exp.run(boom, capture=True)
    assert not record.ok
    assert "nope" in (record.error or "")


def test_experiment_run_raises_by_default_on_error() -> None:
    exp = Experiment("e", seed=1)

    def boom(_: Experiment) -> dict[str, float]:
        raise RuntimeError("nope")

    with pytest.raises(ExperimentError):
        exp.run(boom)


def test_experiment_run_rejects_non_callable() -> None:
    with pytest.raises(TypeError):
        Experiment("e").run(42)  # type: ignore[arg-type]


def test_experiment_run_rejects_unserializable_results() -> None:
    exp = Experiment("e")
    with pytest.raises(ExperimentError):
        exp.run(lambda e: {"bad": object()}, capture=False)


def test_experiment_with_config_and_seed_return_copies() -> None:
    exp = Experiment("e", seed=1, config={"a": 1})
    other = exp.with_config(a=2, b=3)
    assert other.config == {"a": 2, "b": 3}
    assert exp.config == {"a": 1}
    assert other.with_seed(9).seed == 9


def test_experiment_sweep_is_cartesian_and_sorted() -> None:
    exp = Experiment("e", seed=0)
    variants = exp.sweep(rate=[0.1, 0.2], n=[10, 20])
    combos = [dict(v.config) for v in variants]
    assert len(combos) == 4
    assert {"rate": 0.1, "n": 10} in combos
    assert {"rate": 0.2, "n": 20} in combos
    assert combos == sorted(combos, key=lambda c: (c["n"], c["rate"]))


def test_experiment_sweep_needs_an_axis() -> None:
    with pytest.raises(ExperimentError):
        Experiment("e").sweep()


def test_experiment_artifacts_builds_records() -> None:
    artifacts = Experiment("e").artifacts({"plot": Path("p.png")})
    assert artifacts == (Artifact("plot", "p.png"),)


# --------------------------------------------------------------------------- #
# ResultStore
# --------------------------------------------------------------------------- #
def _record(run_id: str, *, value: float = 1.0, status: str = "ok") -> RunRecord:
    return RunRecord(
        run_id=run_id,
        experiment="exp",
        seed=0,
        results={} if status == "error" else {"loss": value},
        status=status,
        error="boom" if status == "error" else None,
        started_at=f"2026-01-01T00:00:{run_id[-2:].zfill(2)}+00:00",
    )


def test_store_save_load_round_trip(tmp_path: Path) -> None:
    store = ResultStore(tmp_path)
    record = _record("run01", value=2.0)
    path = store.save(record)
    assert path.exists()
    assert store.load("run01") == record
    assert store.run_ids() == ["run01"]
    assert list(store.records()) == [record]


def test_store_missing_run_raises(tmp_path: Path) -> None:
    with pytest.raises(ExperimentError):
        ResultStore(tmp_path).load("nope")


def test_store_save_rejects_non_record(tmp_path: Path) -> None:
    with pytest.raises(TypeError):
        ResultStore(tmp_path).save({"run_id": "x"})  # type: ignore[arg-type]


def test_store_query_filters_and_orders(tmp_path: Path) -> None:
    store = ResultStore(tmp_path)
    store.save(_record("run01", value=1.0))
    store.save(_record("run02", value=2.0))
    store.save(_record("run03", status="error"))
    assert len(store.query()) == 3
    assert [r.run_id for r in store.query(status="error")] == ["run03"]
    assert [r.run_id for r in store.query(experiment="exp")] == [
        "run03",
        "run02",
        "run01",
    ]
    assert [r.run_id for r in store.query(seed=0)] == ["run03", "run02", "run01"]
    assert store.query(experiment="other") == []


def test_store_query_rejects_bad_status(tmp_path: Path) -> None:
    with pytest.raises(ExperimentError):
        ResultStore(tmp_path).query(status="bad")


def test_store_query_by_tag(tmp_path: Path) -> None:
    store = ResultStore(tmp_path)
    tagged = RunRecord("run01", "exp", 0, results={"x": 1}, tags=("keep",))
    plain = RunRecord("run02", "exp", 0, results={"x": 2})
    store.save(tagged)
    store.save(plain)
    assert [r.run_id for r in store.query(tag="keep")] == ["run01"]


def test_store_best_max_and_min(tmp_path: Path) -> None:
    store = ResultStore(tmp_path)
    store.save(_record("run01", value=5.0))
    store.save(_record("run02", value=1.0))
    store.save(_record("run03", status="error"))
    assert store.best("loss").run_id == "run01"
    assert store.best("loss", minimize=True).run_id == "run02"


def test_store_best_ignores_non_numeric(tmp_path: Path) -> None:
    store = ResultStore(tmp_path)
    store.save(RunRecord("run01", "exp", 0, results={"loss": "high"}))
    with pytest.raises(ExperimentError):
        store.best("loss")


def test_store_summary_counts(tmp_path: Path) -> None:
    store = ResultStore(tmp_path)
    store.save(_record("run01", value=1.0))
    store.save(_record("run02", status="error"))
    summary = store.summary()
    assert summary["total"] == 2
    assert summary["failures"] == 1
    assert summary["by_experiment"] == {"exp": 2}


def test_store_survives_a_reopened_directory(tmp_path: Path) -> None:
    ResultStore(tmp_path).save(_record("run01", value=3.0))
    reopened = ResultStore(tmp_path)
    assert reopened.load("run01").results["loss"] == 3.0


# --------------------------------------------------------------------------- #
# Dataset
# --------------------------------------------------------------------------- #
def test_dataset_validates_columns() -> None:
    with pytest.raises(ExperimentError):
        Dataset("")
    with pytest.raises(ExperimentError):
        Dataset("d", {"x": np.zeros((2, 2, 2))})
    with pytest.raises(ExperimentError):
        Dataset("d", {"x": np.array([1.0, 2.0]), "y": np.array([1.0])})
    with pytest.raises(ExperimentError):
        Dataset("d", {"x": np.array([1.0, np.inf])})


def test_dataset_getitem_is_read_only() -> None:
    ds = Dataset("d", {"x": np.array([1.0, 2.0])})
    with pytest.raises(ValueError):
        ds["x"][0] = 5.0


def test_dataset_generate_is_reproducible() -> None:
    a = Dataset.generate("d", shape=(10, 2), seed=1)
    b = Dataset.generate("d", shape=(10, 2), seed=1)
    c = Dataset.generate("d", shape=(10, 2), seed=2)
    np.testing.assert_array_equal(a["x0"], b["x0"])
    assert not np.array_equal(a["x0"], c["x0"])
    assert a.size == 10
    assert a.keys == ("x0", "x1")


def test_dataset_generate_validates_generator_and_shape() -> None:
    assert "normal" in GENERATORS
    with pytest.raises(ExperimentError):
        Dataset.generate("d", generator="nope")
    with pytest.raises(ExperimentError):
        Dataset.generate("d", shape=(0, 2))


def test_dataset_from_spec_round_trips() -> None:
    ds = Dataset.generate("d", generator="uniform", shape=(8, 1), seed=4)
    regenerated = Dataset.from_spec("d", ds.spec)
    assert regenerated.fingerprint() == ds.fingerprint()


def test_dataset_from_spec_rejects_bad_shape() -> None:
    with pytest.raises(ExperimentError):
        Dataset.from_spec("d", {"generator": "normal"})


def test_dataset_split_is_disjoint_and_reproducible() -> None:
    ds = Dataset.generate("d", shape=(100, 2), seed=0)
    train, test = ds.split([0.7, 0.3], seed=1)
    assert train.size == 70 and test.size == 30
    assert train.name == "d[0]" and test.name == "d[1]"
    again = ds.split([0.7, 0.3], seed=1)
    np.testing.assert_array_equal(train["x0"], again[0]["x0"])


def test_dataset_split_validates_fractions() -> None:
    ds = Dataset.generate("d", shape=(10, 1), seed=0)
    with pytest.raises(ExperimentError):
        ds.split([])
    with pytest.raises(ExperimentError):
        ds.split([0.0, 1.0])
    with pytest.raises(ExperimentError):
        ds.split([0.5, 0.6])


def test_dataset_fingerprint_changes_with_data() -> None:
    a = Dataset("d", {"x": np.array([1.0, 2.0])})
    b = Dataset("d", {"x": np.array([1.0, 3.0])})
    assert a.fingerprint() != b.fingerprint()
