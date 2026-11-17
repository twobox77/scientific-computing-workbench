# Installation

This page covers the supported ways to install SCW, how to verify the install,
and how to remove it. For a task-oriented introduction once it is installed,
see [Usage](usage.md); for the no-network walkthrough, see the (Chinese)
[離線使用](offline.md).

## Requirements

- **Python 3.12 or newer** (CI tests 3.12 and 3.13).
- Core runtime dependencies, installed automatically: **NumPy ≥ 2.0**,
  **SciPy ≥ 1.13**, **Typer ≥ 0.12**.
- Optional extras pull in their own dependencies: **SymPy** (`symbolic`) and
  **Matplotlib** (`visualization`).

## Install with uv (recommended)

From a checkout of the repository:

```bash
uv sync                 # core only
uv sync --all-extras    # core + every optional extra + dev tools
```

Pick individual extras with `--extra`:

```bash
uv sync --extra symbolic        # SymPy adapter
uv sync --extra visualization   # Matplotlib adapter
uv sync --extra notebook        # JupyterLab + ipykernel
uv sync --extra interactive     # matplotlib + JupyterLab + ipykernel + ipympl
```

!!! warning "`uv sync --extra <x>` replaces the environment"
    `uv sync --extra symbolic` removes the other extras and the dev tools from
    the environment. To keep everything, use `uv sync --all-extras`.

Run any command inside the project environment with `uv run`:

```bash
uv run scw version
uv run python examples/01_vectors.py
```

## Install with pip

Once the package is published, install it from PyPI:

```bash
pip install scw                 # core
pip install "scw[symbolic]"     # with the SymPy adapter
pip install "scw[visualization,notebook]"
```

To install the current source tree without `uv`:

```bash
pip install .                   # core
pip install ".[all]"            # every optional extra
```

The extras are named the same as in the `uv` section above.

## Verify the install

```bash
scw version     # prints the SCW, Python, NumPy and SciPy versions
scw doctor      # confirms the required dependencies import
```

In Python:

```python
import scw
print(scw.__version__)                 # the installed version

from scw.math_core import Vector
print(Vector([3.0, 4.0]).norm())       # 5.0
```

`scripts/verify_install.sh` runs this end to end in a throwaway environment
(it builds the wheel, installs it into a fresh virtual environment and imports
every public namespace), which is exactly what CI's `install` job does.

## Offline install

To install on a machine without network access, download the dependencies once
on a connected machine and transfer them. The step-by-step recipe is in the
[offline guide](offline.md) (離線使用), section 0.5.

## Uninstall

```bash
rm -rf .venv/          # remove just this project's virtual environment
uv cache clean         # clear uv's download cache
pip uninstall scw      # if it was installed with pip
```

The three levels (project environment → uv cache and managed Pythons → uv
itself) are described in the [offline guide](offline.md) (離線使用), section 5.
