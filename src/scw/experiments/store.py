"""On-disk result store: a directory of run records with a queryable index.

A :class:`ResultStore` keeps every :class:`~scw.experiments.records.RunRecord`
as one JSON file and maintains an ``index.json`` listing them, so results can
be inspected, compared and reloaded long after the process that produced them
has exited.  It is the only place in the layer that touches the file system.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from scw.exceptions import ExperimentError
from scw.experiments.records import RunRecord

INDEX_NAME = "index.json"


class ResultStore:
    """A directory holding run records and their index.

    The store is created on demand.  Writes are atomic (write to a temporary
    file, then replace), so an interrupted save cannot leave a half-written
    record behind.
    """

    __slots__ = ("_root",)

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)

    @property
    def root(self) -> Path:
        """The directory the store lives in."""
        return self._root

    def _ensure(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True)

    def _record_path(self, run_id: str) -> Path:
        return self._root / f"{run_id}.json"

    def _index_path(self) -> Path:
        return self._root / INDEX_NAME

    def _load_index(self) -> dict[str, dict[str, Any]]:
        path = self._index_path()
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:  # pragma: no cover - corrupt store
            raise ExperimentError(f"corrupt result index at {path}") from exc
        if not isinstance(data, dict):
            raise ExperimentError(f"corrupt result index at {path}")
        return data

    def _write_json(self, path: Path, payload: Any) -> None:
        self._ensure()
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(path)

    def save(self, record: RunRecord) -> Path:
        """Persist ``record`` and update the index; return the record path."""
        if not isinstance(record, RunRecord):
            raise TypeError("record must be a RunRecord")
        self._write_json(self._record_path(record.run_id), record.to_dict())
        index = self._load_index()
        index[record.run_id] = {
            "experiment": record.experiment,
            "seed": record.seed,
            "label": record.label,
            "tags": list(record.tags),
            "status": record.status,
            "started_at": record.started_at,
            "duration_seconds": record.duration_seconds,
        }
        self._write_json(self._index_path(), index)
        return self._record_path(record.run_id)

    def load(self, run_id: str) -> RunRecord:
        """Load one record by id."""
        path = self._record_path(run_id)
        if not path.exists():
            raise ExperimentError(f"no run {run_id!r} in the store at {self._root}")
        return RunRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def run_ids(self) -> list[str]:
        """Every run id in the store, in the order the index was written."""
        return list(self._load_index())

    def records(self) -> Iterator[RunRecord]:
        """Iterate over every record, loading it from disk."""
        # complexity: one JSON file per run; this is I/O over the run list
        for run_id in self.run_ids():
            yield self.load(run_id)

    def query(
        self,
        *,
        experiment: str | None = None,
        status: str | None = None,
        tag: str | None = None,
        seed: int | None = None,
    ) -> list[RunRecord]:
        """Records matching every given filter, newest first.

        Filters are ANDed; passing none returns every record.  Ordering uses
        the recorded start time, so results are stable across stores.
        """
        if status is not None and status not in ("ok", "error"):
            raise ExperimentError(f"unknown run status {status!r}")
        index = self._load_index()
        selected: list[str] = []
        # complexity: filters the (small) run index by metadata, not data points
        for run_id, meta in index.items():
            if experiment is not None and meta.get("experiment") != experiment:
                continue
            if status is not None and meta.get("status") != status:
                continue
            if seed is not None and meta.get("seed") != seed:
                continue
            if tag is not None and tag not in meta.get("tags", ()):
                continue
            selected.append(run_id)
        records = [self.load(run_id) for run_id in selected]
        records.sort(key=lambda record: record.started_at, reverse=True)
        return records

    def best(
        self,
        key: str,
        *,
        experiment: str | None = None,
        minimize: bool = False,
        tag: str | None = None,
    ) -> RunRecord:
        """The successful record with the largest (or smallest) ``results[key]``.

        Only runs whose ``results`` contain a finite numeric ``key`` compete;
        a store with no such run raises :class:`~scw.exceptions.ExperimentError`.
        """
        candidates: list[tuple[float, RunRecord]] = []
        # complexity: scans the (small) matching run records for a result key
        for record in self.query(experiment=experiment, status="ok", tag=tag):
            value = record.results.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            candidates.append((float(value), record))
        if not candidates:
            raise ExperimentError(
                f"no successful run in the store records a numeric {key!r} result"
            )
        pick = min if minimize else max
        return pick(candidates, key=lambda item: item[0])[1]

    def summary(self) -> dict[str, Any]:
        """A small JSON-serializable overview of the store."""
        index = self._load_index()
        by_experiment: dict[str, int] = {}
        failures = 0
        # complexity: aggregates the (small) run index, not data points
        for meta in index.values():
            name = str(meta.get("experiment"))
            by_experiment[name] = by_experiment.get(name, 0) + 1
            if meta.get("status") == "error":
                failures += 1
        return {
            "root": str(self._root),
            "total": len(index),
            "failures": failures,
            "by_experiment": by_experiment,
        }
