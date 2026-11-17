"""Serializable records and reproducibility helpers.

This module holds the *data* of the experiments layer: the
:class:`RunRecord` that captures one execution of an experiment, the
:class:`Artifact` files it produced, and the small deterministic helpers
(seed derivation, run identifiers, environment fingerprint) that make a run
reproducible.

Everything here is plain JSON-serializable data; the on-disk store lives in
:mod:`scw.experiments.store`.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import platform
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any

import numpy as np

from scw.exceptions import ExperimentError


def jsonable(value: Any) -> Any:
    """Return ``value`` as a structure of JSON primitives, or raise.

    NumPy scalars and arrays, the SCW domain objects (anything exposing a
    ``.data`` array), :class:`~pathlib.Path`, ``datetime`` and the usual
    containers are converted.  A value that cannot be represented raises
    :class:`~scw.exceptions.ExperimentError`, so a bad result fails loudly
    instead of being silently stringified.
    """
    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        return [jsonable(item) for item in sorted(value, key=repr)]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [jsonable(item) for item in value]
    data = getattr(value, "data", None)
    if isinstance(data, np.ndarray):
        return data.tolist()
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return jsonable(dataclasses.asdict(value))
    raise ExperimentError(
        f"value of type {type(value).__name__!r} is not JSON-serializable; "
        "convert it to numbers, strings, sequences or mappings first"
    )


def canonical_json(value: Any) -> str:
    """A stable JSON encoding (sorted keys, no spaces) used for hashing."""
    return json.dumps(jsonable(value), sort_keys=True, separators=(",", ":"))


def derive_seed(seed: int, label: str) -> int:
    """Derive a child seed from ``seed`` and ``label``, deterministically.

    The result is stable across runs and machines, so the same
    ``(seed, label)`` pair always yields the same stream — the basis of the
    layer's reproducibility guarantee.
    """
    digest = hashlib.sha256(f"{int(seed)}:{label}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % (2**63)


def make_run_id(
    experiment: str, seed: int, config: Mapping[str, Any], label: str
) -> str:
    """A deterministic identifier for a run.

    Two runs of the same experiment with the same seed, configuration and
    label get the same id, so re-running a reproducible experiment overwrites
    (rather than duplicates) its record.
    """
    payload = {
        "experiment": experiment,
        "seed": int(seed),
        "config": config,
        "label": label,
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()[:16]


def environment_fingerprint() -> dict[str, str]:
    """Versions of the interpreter and libraries a run depends on."""
    import scipy

    import scw

    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "scw": scw.__version__,
        "platform": platform.platform(),
    }


@dataclass(frozen=True)
class Artifact:
    """A file produced by a run, kept alongside its record."""

    name: str
    path: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ExperimentError("an artifact name must be a non-empty string")
        if not isinstance(self.path, str) or not self.path:
            raise ExperimentError("an artifact path must be a non-empty string")

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "path": self.path}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Artifact:
        return cls(name=data["name"], path=data["path"])


@dataclass(frozen=True)
class RunRecord:
    """The outcome of one experiment run.

    A record is immutable, JSON-serializable and self-describing: it carries
    the configuration, the results, the environment and the timing, so a run
    can be reproduced and compared later without the original process.
    """

    run_id: str
    experiment: str
    seed: int
    config: Mapping[str, Any] = field(default_factory=dict)
    results: Mapping[str, Any] = field(default_factory=dict)
    status: str = "ok"
    error: str | None = None
    label: str = ""
    tags: tuple[str, ...] = ()
    artifacts: tuple[Artifact, ...] = ()
    environment: Mapping[str, str] = field(default_factory=dict)
    started_at: str = ""
    finished_at: str = ""
    duration_seconds: float = 0.0

    def __post_init__(self) -> None:
        if self.status not in ("ok", "error"):
            raise ExperimentError(f"unknown run status {self.status!r}")
        if self.status == "error" and not self.error:
            raise ExperimentError("a failed run must carry an error message")
        object.__setattr__(self, "config", MappingProxyType(dict(self.config)))
        object.__setattr__(self, "results", MappingProxyType(dict(self.results)))
        object.__setattr__(
            self, "environment", MappingProxyType(dict(self.environment))
        )
        object.__setattr__(self, "artifacts", tuple(self.artifacts))
        object.__setattr__(self, "tags", tuple(self.tags))

    @property
    def ok(self) -> bool:
        """Whether the run finished without raising."""
        return self.status == "ok"

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serializable view of the record."""
        return {
            "run_id": self.run_id,
            "experiment": self.experiment,
            "seed": self.seed,
            "label": self.label,
            "tags": list(self.tags),
            "status": self.status,
            "error": self.error,
            "config": jsonable(self.config),
            "results": jsonable(self.results),
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "environment": jsonable(self.environment),
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": self.duration_seconds,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> RunRecord:
        """Rebuild a record from :meth:`to_dict` output."""
        return cls(
            run_id=data["run_id"],
            experiment=data["experiment"],
            seed=data["seed"],
            config=dict(data.get("config", {})),
            results=dict(data.get("results", {})),
            status=data.get("status", "ok"),
            error=data.get("error"),
            label=data.get("label", ""),
            tags=tuple(data.get("tags", ())),
            artifacts=tuple(
                Artifact.from_dict(item) for item in data.get("artifacts", ())
            ),
            environment=dict(data.get("environment", {})),
            started_at=data.get("started_at", ""),
            finished_at=data.get("finished_at", ""),
            duration_seconds=float(data.get("duration_seconds", 0.0)),
        )
