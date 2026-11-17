"""Experiments: configuration, run records, datasets and reproducibility.

This layer (roadmap §11, 0.8) turns the computational core into something you
can *track*: an :class:`Experiment` bundles a configuration and a seed, runs a
function reproducibly, and captures a :class:`RunRecord`; a
:class:`ResultStore` persists those records and answers queries over them; a
:class:`Dataset` makes inputs reproducible too.  It builds on
:mod:`scw.math_core` and :mod:`scw.exceptions` and imports neither the CLI,
plotting, nor (apart from :mod:`scw.experiments.store`) the file system.
"""

from __future__ import annotations

from scw.experiments.dataset import GENERATORS, Dataset
from scw.experiments.experiment import Experiment
from scw.experiments.records import (
    Artifact,
    RunRecord,
    canonical_json,
    derive_seed,
    environment_fingerprint,
    jsonable,
)
from scw.experiments.store import ResultStore

__all__ = [
    "GENERATORS",
    "Artifact",
    "Dataset",
    "Experiment",
    "ResultStore",
    "RunRecord",
    "canonical_json",
    "derive_seed",
    "environment_fingerprint",
    "jsonable",
]
