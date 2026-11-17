"""Property-based tests for :mod:`scw.experiments`.

The invariants checked here are the layer's reason to exist: that a seed and
configuration determine a run (same id and same numbers every time), that a
dataset regenerates from its own spec, that a store round-trips a record
through disk unchanged, and that splitting a dataset keeps every row exactly
once.
"""

from __future__ import annotations

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from scw.experiments import Dataset, Experiment, ResultStore

_seed = st.integers(0, 2**31 - 1)
_size = st.integers(1, 50)
_rows = st.integers(1, 40)
_cols = st.integers(1, 4)


@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(seed=_seed, n=_size)
def test_same_seed_and_config_reproduce_results(
    tmp_path_factory, seed: int, n: int
) -> None:
    exp = Experiment("e", seed=seed, config={"n": n})
    first = exp.run(
        lambda e: {"mean": float(e.rng("m").normal(size=e.config["n"]).mean())}
    )
    again = exp.run(
        lambda e: {"mean": float(e.rng("m").normal(size=e.config["n"]).mean())}
    )
    assert first.run_id == again.run_id
    assert first.results == again.results


@given(seed=_seed)
def test_different_labels_give_independent_streams(seed: int) -> None:
    exp = Experiment("e", seed=seed)
    a = exp.rng("a").normal(size=8)
    b = exp.rng("b").normal(size=8)
    assert not np.array_equal(a, b)


@settings(max_examples=40, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(seed=_seed, rows=_rows, cols=_cols)
def test_store_round_trips_records(
    tmp_path_factory, seed: int, rows: int, cols: int
) -> None:
    store = ResultStore(tmp_path_factory.mktemp("store"))
    exp = Experiment("e", seed=seed, config={"rows": rows, "cols": cols})
    record = exp.run(
        lambda e: {
            "sum": float(
                np.sum(e.rng("x").normal(size=(e.config["rows"], e.config["cols"])))
            )
        },
        store=store,
    )
    assert store.load(record.run_id) == record


@settings(max_examples=40, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(seed=_seed, rows=_rows, cols=_cols)
def test_dataset_regenerates_from_spec(seed: int, rows: int, cols: int) -> None:
    ds = Dataset.generate("d", shape=(rows, cols), seed=seed)
    regenerated = Dataset.from_spec("d", ds.spec)
    assert regenerated.fingerprint() == ds.fingerprint()


@settings(max_examples=40, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(seed=_seed, rows=_rows)
def test_split_partitions_every_row_once(seed: int, rows: int) -> None:
    ds = Dataset.generate("d", shape=(rows, 2), seed=seed)
    parts = ds.split([0.5, 0.5], seed=seed)
    assert sum(part.size for part in parts) == rows
    merged = np.concatenate([part["x0"] for part in parts])
    assert sorted(merged.tolist()) == sorted(ds["x0"].tolist())


@given(seed=_seed, n=_size)
def test_derive_seed_is_bounded(seed: int, n: int) -> None:
    from scw.experiments import derive_seed

    assert 0 <= derive_seed(seed, str(n)) < 2**63
