"""SCW command-line entry point.

The CLI only parses arguments and calls the public Python API; it contains no
mathematical algorithms of its own.
"""

from __future__ import annotations

import platform

import numpy as np
import scipy
import typer

import scw

app = typer.Typer(
    help="SCW — Scientific Computing Workbench command line.",
    no_args_is_help=True,
    add_completion=False,
)


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


if __name__ == "__main__":
    app()
