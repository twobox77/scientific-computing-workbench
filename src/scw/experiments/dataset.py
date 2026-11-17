"""Deterministic datasets for experiments.

A :class:`Dataset` is a reproducible bundle of arrays plus its metadata.  The
same generator specification and seed always produce the same data, so an
experiment can record *how* its inputs were made instead of shipping a large
file.  The class builds on :class:`numpy.random.Generator` and stays
JSON-describable.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

import numpy as np

from scw.exceptions import ExperimentError
from scw.experiments.records import derive_seed

#: Generators :meth:`Dataset.generate` understands.
GENERATORS = ("normal", "uniform", "integers")


@dataclass(frozen=True)
class Dataset:
    """A named, reproducible collection of NumPy arrays.

    ``columns`` maps a name to a 1-D or 2-D array.  ``spec`` records how the
    data was produced (generator, parameters, seed) so the dataset can be
    regenerated exactly; :meth:`from_spec` is the inverse of :meth:`spec`.
    """

    name: str
    columns: Mapping[str, np.ndarray] = field(default_factory=dict)
    spec: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ExperimentError("a dataset name must be a non-empty string")
        prepared: dict[str, np.ndarray] = {}
        # complexity: validates the handful of named columns of the dataset
        for key, value in self.columns.items():
            array = np.array(value, dtype=float, copy=True)
            if array.ndim not in (1, 2):
                raise ExperimentError(
                    f"column {key!r} must be 1-D or 2-D, got {array.ndim}-D"
                )
            if not np.all(np.isfinite(array)):
                raise ExperimentError(f"column {key!r} contains non-finite values")
            prepared[str(key)] = array
        lengths = {len(array) for array in prepared.values()}
        if len(lengths) > 1:
            raise ExperimentError("every column of a dataset must share one length")
        object.__setattr__(self, "columns", MappingProxyType(prepared))
        object.__setattr__(self, "spec", MappingProxyType(dict(self.spec)))

    @property
    def size(self) -> int:
        """Number of rows (0 for an empty dataset)."""
        return next(iter(len(a) for a in self.columns.values()), 0)

    @property
    def keys(self) -> tuple[str, ...]:
        """Column names, in insertion order."""
        return tuple(self.columns)

    def __getitem__(self, key: str) -> np.ndarray:
        """Read-only view of one column."""
        array = self.columns[key]
        view = array.view()
        view.flags.writeable = False
        return view

    def split(self, fractions: Sequence[float], *, seed: int = 0) -> list[Dataset]:
        """Partition the rows into disjoint datasets of the given ``fractions``.

        The split is a seeded permutation, so the same dataset and seed give
        the same parts.  ``fractions`` must be positive and sum to one; each
        part keeps the parent's name (with an index suffix) and spec.
        """
        parts = [float(fraction) for fraction in fractions]
        if not parts or any(fraction <= 0.0 for fraction in parts):
            raise ExperimentError("split fractions must be positive")
        if abs(sum(parts) - 1.0) > 1e-9:
            raise ExperimentError("split fractions must sum to 1.0")
        total = self.size
        order = np.random.default_rng(derive_seed(seed, self.name)).permutation(total)
        cuts = np.cumsum([0, *(round(fraction * total) for fraction in parts)])
        cuts[-1] = total
        datasets: list[Dataset] = []
        # complexity: one slice per requested split part (a handful)
        for index, (start, stop) in enumerate(zip(cuts[:-1], cuts[1:], strict=True)):
            rows = order[start:stop]
            columns = {key: column[rows] for key, column in self.columns.items()}
            datasets.append(Dataset(f"{self.name}[{index}]", columns, self.spec))
        return datasets

    @classmethod
    def generate(
        cls,
        name: str,
        *,
        generator: str = "normal",
        shape: tuple[int, int] = (100, 3),
        seed: int = 0,
        **parameters: float,
    ) -> Dataset:
        """Build a dataset from a seeded generator.

        ``generator`` is one of :data:`GENERATORS`; ``shape`` is
        ``(rows, columns)``.  Extra keyword arguments are passed to the NumPy
        generator (for example ``loc``/``scale`` for ``"normal"``).  Each
        column is drawn from its own stream, so columns are independent and
        reproducible.
        """
        if generator not in GENERATORS:
            raise ExperimentError(
                f"unknown generator {generator!r}; expected one of {GENERATORS}"
            )
        if len(shape) != 2 or shape[0] <= 0 or shape[1] <= 0:
            raise ExperimentError("shape must be a positive (rows, columns) pair")
        rows, columns = shape
        rng = np.random.default_rng(derive_seed(seed, name))
        method = getattr(rng, generator)
        data = {
            f"x{index}": method(size=rows, **parameters) for index in range(columns)
        }
        spec = {
            "generator": generator,
            "shape": list(shape),
            "seed": int(seed),
            "parameters": dict(parameters),
        }
        return cls(name, data, spec)

    @classmethod
    def from_spec(cls, name: str, spec: Mapping[str, Any]) -> Dataset:
        """Regenerate a dataset from the ``spec`` of a previous one."""
        shape = spec.get("shape")
        if not isinstance(shape, Sequence) or len(shape) != 2:
            raise ExperimentError("spec must carry a (rows, columns) shape")
        return cls.generate(
            name,
            generator=spec.get("generator", "normal"),
            shape=(int(shape[0]), int(shape[1])),
            seed=int(spec.get("seed", 0)),
            **dict(spec.get("parameters", {})),
        )

    def fingerprint(self) -> str:
        """A stable hash of the data, for detecting changed inputs."""
        import hashlib

        digest = hashlib.sha256()
        # complexity: folds the handful of dataset columns into one hash
        for key in self.keys:
            digest.update(key.encode("utf-8"))
            digest.update(
                np.ascontiguousarray(self.columns[key], dtype=float).tobytes()
            )
        return digest.hexdigest()[:16]
