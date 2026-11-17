"""Experiment tracking and reproducibility: sweeps, records and datasets.

Roadmap §11, milestone 0.8.  Run with::

    uv run python examples/11_experiments.py

It runs a tiny Monte Carlo estimate of pi under several sample sizes, records
each run in a temporary :class:`~scw.experiments.ResultStore`, then shows how
to query the store and how a seeded :class:`~scw.experiments.Dataset` makes
inputs reproducible.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np

from scw.experiments import Dataset, Experiment, ResultStore


def estimate_pi(experiment: Experiment) -> dict[str, float]:
    """Monte Carlo estimate of pi from the experiment's seeded generator."""
    samples = int(experiment.config["samples"])
    points = experiment.rng("pi").uniform(-1.0, 1.0, size=(samples, 2))
    inside = np.count_nonzero(np.sum(points**2, axis=1) <= 1.0)
    estimate = 4.0 * inside / samples
    return {"estimate": estimate, "error": abs(estimate - np.pi)}


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        store = ResultStore(directory)

        base = Experiment("monte-carlo-pi", seed=2026, tags=("demo",), store=store)
        print("sweep over sample size")
        # complexity: runs the handful of sweep points for the demo
        for experiment in base.sweep(samples=[500, 5000, 50000]):
            record = experiment.run(estimate_pi)
            print(
                f"  samples={experiment.config['samples']:>6}  "
                f"pi~{record.results['estimate']:.4f}  "
                f"error={record.results['error']:.4f}  id={record.run_id}"
            )

        print("\nreproducibility: same seed and config -> same run id and result")
        target = base.with_config(samples=5000)
        again = target.run(estimate_pi)
        print(f"  rerun id == recorded id: {again.run_id == target.run_id()}")
        print(f"  deterministic estimate: {again.results['estimate']:.6f}")

        print("\nquery the store")
        print("  summary:", store.summary())
        best = store.best("error", minimize=True)
        print(
            f"  closest to pi: id={best.run_id} estimate={best.results['estimate']:.4f}"
        )
        print(f"  runs tagged 'demo': {len(store.query(tag='demo'))}")

        print("\nrecord reloads from disk unchanged")
        reloaded = store.load(again.run_id)
        same = reloaded.results == again.results
        python_version = reloaded.environment["python"]
        numpy_version = reloaded.environment["numpy"]
        print(f"  reloaded results == in-memory: {same}")
        print(f"  recorded environment: python {python_version}, numpy {numpy_version}")

    dataset = Dataset.generate("points", generator="normal", shape=(1000, 2), seed=7)
    train, test = dataset.split([0.8, 0.2], seed=7)
    print("\nreproducible datasets")
    print(f"  {dataset.name}: {dataset.size} rows, fingerprint {dataset.fingerprint()}")
    print(f"  split -> train {train.size}, test {test.size}")
    regenerated = Dataset.from_spec("points", dataset.spec)
    matches = regenerated.fingerprint() == dataset.fingerprint()
    print(f"  regenerated fingerprint matches: {matches}")

    out = Path("scw_experiments") / "runs"
    print(f"\n(temporary store removed; write a lasting one under {str(out)!r})")


if __name__ == "__main__":
    main()
