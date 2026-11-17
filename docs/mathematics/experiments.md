# Experiments, datasets and reproducibility

`scw.experiments` (roadmap §11, milestone 0.8) is the layer that makes a
computation *trackable*.  It records what you ran, with which parameters and
which seed, so a result can be reproduced and compared long after the process
that produced it has exited.  It builds on `scw.math_core` and
`scw.exceptions`; only the result store touches the file system.

## Experiment

An `Experiment` bundles a name, a seed, a JSON-serializable configuration and
optional tags.  Calling `run` executes a function in a reproducible context
and captures a `RunRecord`:

```python
import numpy as np
from scw.experiments import Experiment, ResultStore

store = ResultStore("runs")

def estimate(experiment):
    samples = experiment.config["samples"]
    x = experiment.rng("sample").uniform(-1.0, 1.0, samples)
    return {"mean": float(x.mean())}

experiment = Experiment("mc", seed=42, config={"samples": 10000}, store=store)
record = experiment.run(estimate)
record.results["mean"]     # the numbers the run produced
record.run_id              # a deterministic id
record.environment         # python / numpy / scipy / scw versions
record.duration_seconds    # wall-clock time
```

`experiment.rng(label)` returns a `numpy.random.Generator` seeded from
`(seed, label)`, so two stages of one experiment get independent, reproducible
streams without extra seeds.  The same seed and configuration always give the
same `run_id` and the same numbers.

A function that raises is captured into a failed record (with the exception
text in `record.error`) instead of losing the run:

```python
record = experiment.run(might_fail, capture=True)
record.ok                  # False
record.error               # "ValueError: ..."
```

Without `capture=True` the exception propagates *after* the record is saved.
`with_config(**overrides)`, `with_seed(seed)` and `sweep(**axes)` return copies
— a sweep is the cartesian product of its axes, one experiment per point.

## Result store

A `ResultStore` keeps each record as one JSON file plus an `index.json`, and
answers queries over them:

```python
store.run_ids()                          # every recorded run
store.records()                          # load every record
store.query(experiment="mc", tag="demo") # matching records, newest first
store.best("mean", minimize=False)       # best successful run for a key
store.summary()                          # counts by experiment, failures
```

Writes are atomic (temporary file, then replace), so an interrupted save never
leaves a half-written record.  `load(run_id)` reads one record back.

## Dataset

A `Dataset` makes *inputs* reproducible too: it holds named columns and the
spec that generated them, so a large input can be described instead of shipped.

```python
from scw.experiments import Dataset

dataset = Dataset.generate("points", generator="normal", shape=(1000, 2), seed=7)
dataset["x0"]                 # read-only view of a column
dataset.fingerprint()         # stable hash of the data
train, test = dataset.split([0.8, 0.2], seed=7)

again = Dataset.from_spec("points", dataset.spec)   # regenerate exactly
```

`GENERATORS` lists the supported generators (`normal`, `uniform`, `integers`);
extra keyword arguments (such as `loc`, `scale`, `low`, `high`) are passed
through.  A split is a seeded permutation, so the parts are disjoint,
reproducible and keep the parent spec.

## Reproducibility guarantees

- The same `(seed, label)` always yields the same random stream
  (`derive_seed`).
- The same experiment, seed, config and label always yield the same `run_id`.
- A record round-trips through disk unchanged, and a dataset regenerates from
  its own spec with an identical fingerprint.

## Command line

```bash
scw experiments summary runs/          # counts by experiment, failures
scw experiments list runs/             # recorded runs, newest first
scw experiments show <run-id> runs/    # one record as JSON
scw experiments best loss runs/        # best successful run for a result key
```
