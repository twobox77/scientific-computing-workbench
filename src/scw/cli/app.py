"""SCW command-line entry point.

The CLI only parses arguments and calls the public Python API; it contains no
mathematical algorithms of its own.
"""

from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Annotated

import numpy as np
import scipy
import typer

import scw
from scw.experiments import ResultStore

app = typer.Typer(
    help="SCW — Scientific Computing Workbench command line.",
    no_args_is_help=True,
    add_completion=False,
)

experiments_app = typer.Typer(
    help="Inspect a directory of experiment run records.",
    no_args_is_help=True,
)
app.add_typer(experiments_app, name="experiments")


@app.command()
def version() -> None:
    """Show SCW, Python, NumPy and SciPy versions."""
    typer.echo(f"scw    {scw.__version__}")
    typer.echo(f"python {platform.python_version()}")
    typer.echo(f"numpy  {np.__version__}")
    typer.echo(f"scipy  {scipy.__version__}")


@app.command()
def doctor() -> None:
    """Check that required dependencies can be imported."""
    typer.echo(f"[ok] python {platform.python_version()}")
    # complexity: fixed set of two dependency modules, O(1) in any data size
    for name, module in {"numpy": np, "scipy": scipy}.items():
        mod_version = getattr(module, "__version__", "unknown")
        typer.echo(f"[ok] {name} {mod_version}")
    typer.echo("all required dependencies are available")


def _open_store(path: Path) -> ResultStore:
    store = ResultStore(path)
    if not store.root.exists():
        typer.echo(f"no result store at {store.root}", err=True)
        raise typer.Exit(code=1)
    return store


@experiments_app.command("summary")
def experiments_summary(
    store: Annotated[Path, typer.Argument(help="Directory of experiment run records.")],
) -> None:
    """Show how many runs a store holds, grouped by experiment."""
    summary = _open_store(store).summary()
    typer.echo(f"store      {summary['root']}")
    typer.echo(f"runs       {summary['total']}")
    typer.echo(f"failures   {summary['failures']}")
    # complexity: iterates the handful of experiment names in the index
    for name, count in sorted(summary["by_experiment"].items()):
        typer.echo(f"  {name}: {count}")


@experiments_app.command("list")
def experiments_list(
    store: Annotated[Path, typer.Argument(help="Directory of experiment run records.")],
    experiment: Annotated[
        str | None, typer.Option(help="Only this experiment name.")
    ] = None,
    tag: Annotated[
        str | None, typer.Option(help="Only runs carrying this tag.")
    ] = None,
) -> None:
    """List recorded runs, newest first."""
    records = _open_store(store).query(experiment=experiment, tag=tag)
    if not records:
        typer.echo("no runs match")
        return
    # complexity: prints the handful of runs the query returned
    for record in records:
        typer.echo(
            f"{record.run_id}  {record.status:<5}  {record.experiment}  "
            f"seed={record.seed}  {record.started_at}"
        )


@experiments_app.command("show")
def experiments_show(
    run_id: Annotated[str, typer.Argument(help="Run id to display.")],
    store: Annotated[Path, typer.Argument(help="Directory of experiment run records.")],
) -> None:
    """Print one run record as JSON."""
    record = _open_store(store).load(run_id)
    typer.echo(json.dumps(record.to_dict(), indent=2, sort_keys=True))


@experiments_app.command("best")
def experiments_best(
    key: Annotated[str, typer.Argument(help="Result key to optimize.")],
    store: Annotated[Path, typer.Argument(help="Directory of experiment run records.")],
    experiment: Annotated[
        str | None, typer.Option(help="Only this experiment name.")
    ] = None,
    minimize: Annotated[
        bool, typer.Option("--minimize", help="Pick the smallest value.")
    ] = False,
) -> None:
    """Show the successful run with the best (largest, or smallest) result."""
    record = _open_store(store).best(key, experiment=experiment, minimize=minimize)
    typer.echo(f"{record.run_id}  {key}={record.results[key]!r}  seed={record.seed}")


if __name__ == "__main__":
    app()
