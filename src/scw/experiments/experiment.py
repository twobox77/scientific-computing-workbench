"""Experiments: named configurations that run a function and record the result.

An :class:`Experiment` bundles a name, a seed, a configuration and optional
tags.  Calling :meth:`Experiment.run` executes a user function in a
reproducible context (a seeded generator derived from the experiment seed) and
captures a :class:`~scw.experiments.records.RunRecord` describing the run,
including timing, environment and any error the function raised.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any

import numpy as np

from scw.exceptions import ExperimentError
from scw.experiments.records import (
    Artifact,
    RunRecord,
    derive_seed,
    environment_fingerprint,
    jsonable,
    make_run_id,
)

#: A user function run by :meth:`Experiment.run`: it receives the experiment
#: (for its configuration and seeded generators) and returns the results.
RunFunction = Callable[["Experiment"], Mapping[str, Any]]


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


@dataclass(frozen=True)
class Experiment:
    """A reproducible unit of work: configuration plus a seeded context.

    ``seed`` seeds every generator the experiment hands out; the same seed and
    configuration therefore reproduce the same run.  ``config`` is any
    JSON-serializable mapping of parameters; ``store`` (optional) is the
    :class:`~scw.experiments.store.ResultStore` where runs are saved.
    """

    name: str
    seed: int = 0
    config: Mapping[str, Any] = field(default_factory=dict)
    tags: tuple[str, ...] = ()
    store: Any = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ExperimentError("an experiment name must be a non-empty string")
        if isinstance(self.seed, bool) or not isinstance(self.seed, (int, np.integer)):
            raise ExperimentError("seed must be an integer")
        object.__setattr__(self, "seed", int(self.seed))
        object.__setattr__(self, "config", MappingProxyType(dict(self.config)))
        object.__setattr__(self, "tags", tuple(str(tag) for tag in self.tags))
        # Validate the configuration eagerly so a bad parameter fails at
        # construction, not halfway through a long run.
        jsonable(self.config)

    def rng(self, label: str = "") -> np.random.Generator:
        """A generator seeded deterministically from ``(seed, label)``.

        Different labels yield independent streams, so a multi-stage
        experiment can seed each stage without hard-coding extra seeds.
        """
        return np.random.default_rng(derive_seed(self.seed, label))

    def run_id(self, *, label: str = "") -> str:
        """The deterministic id this experiment's next run will get."""
        return make_run_id(self.name, self.seed, self.config, label)

    def run(
        self,
        function: RunFunction,
        *,
        label: str = "",
        store: Any = None,
        capture: bool = False,
    ) -> RunRecord:
        """Run ``function`` and return its :class:`RunRecord`.

        The function receives this experiment and returns a mapping of
        results.  Its exception (if any) is captured into a failed record
        rather than propagating when ``capture`` is true; otherwise it
        propagates after the record is saved.  When a store is given (here or
        on the experiment) the record is persisted.
        """
        if not callable(function):
            raise TypeError("function must be callable")
        active_store = store if store is not None else self.store
        started = _utc_now()
        clock = time.perf_counter()
        status, error, results = "ok", None, {}
        try:
            produced = function(self)
            results = dict(produced) if produced is not None else {}
            jsonable(results)
        except Exception as exc:
            status, error, results = "error", f"{type(exc).__name__}: {exc}", {}
        duration = time.perf_counter() - clock
        record = RunRecord(
            run_id=self.run_id(label=label),
            experiment=self.name,
            seed=self.seed,
            config=dict(self.config),
            results=results,
            status=status,
            error=error,
            label=label,
            tags=self.tags,
            environment=environment_fingerprint(),
            started_at=started,
            finished_at=_utc_now(),
            duration_seconds=duration,
        )
        if active_store is not None:
            active_store.save(record)
        if status == "error" and not capture:
            raise ExperimentError(f"run {record.run_id} failed: {error}")
        return record

    def with_config(self, **overrides: Any) -> Experiment:
        """A copy of this experiment with ``overrides`` merged into the config."""
        merged = {**self.config, **overrides}
        return Experiment(self.name, self.seed, merged, self.tags, self.store)

    def with_seed(self, seed: int) -> Experiment:
        """A copy of this experiment with a new seed."""
        return Experiment(self.name, seed, self.config, self.tags, self.store)

    def sweep(self, **axes: Iterable[Any]) -> list[Experiment]:
        """The cartesian product of ``axes`` as one experiment per point.

        ``exp.sweep(rate=[0.1, 0.2], n=[10, 20])`` yields four experiments
        whose configs are the cross product, in a deterministic order.
        """
        if not axes:
            raise ExperimentError("sweep needs at least one axis")
        keys = sorted(axes)
        combos: list[dict[str, Any]] = [{}]
        # complexity: builds the (small) cross product of the sweep axes
        for key in keys:
            values = list(axes[key])
            combos = [{**combo, key: value} for combo in combos for value in values]
        # complexity: one experiment per (small) sweep point
        return [
            Experiment(
                self.name, self.seed, {**self.config, **combo}, self.tags, self.store
            )
            for combo in combos
        ]

    def artifacts(self, paths: Mapping[str, Any]) -> tuple[Artifact, ...]:
        """Turn a ``name -> path`` mapping into validated :class:`Artifact`s."""
        return tuple(
            Artifact(name=name, path=str(path)) for name, path in paths.items()
        )
