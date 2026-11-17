#!/usr/bin/env bash
# Build the wheel and prove it installs and imports cleanly in a fresh venv.
#
# This is the same end-to-end check CI's "install" job runs: it catches
# packaging mistakes (a module left out of the wheel, a missing dependency, a
# broken entry point) that unit tests against the source tree cannot.
#
# Usage: bash scripts/verify_install.sh [extra ...]
#   e.g. bash scripts/verify_install.sh            # core only
#        bash scripts/verify_install.sh symbolic visualization
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

EXTRAS=""
for extra in "$@"; do
  EXTRAS="${EXTRAS:+$EXTRAS,}$extra"
done
SPEC="."
if [ -n "$EXTRAS" ]; then
  SPEC=".[$EXTRAS]"
fi

echo "==> Building wheel and sdist"
uv build --out-dir "$WORKDIR/dist" >/dev/null

WHEEL="$(ls "$WORKDIR"/dist/*.whl | head -n1)"
echo "==> Wheel: $(basename "$WHEEL")"

echo "==> Creating a fresh virtual environment"
uv venv "$WORKDIR/venv" >/dev/null

echo "==> Installing the wheel (spec: $SPEC)"
VIRTUAL_ENV="$WORKDIR/venv" uv pip install "$WHEEL" >/dev/null
if [ -n "$EXTRAS" ]; then
  # Install the optional dependencies too, so the extras' imports resolve.
  VIRTUAL_ENV="$WORKDIR/venv" uv pip install "$SPEC" >/dev/null
fi

PY="$WORKDIR/venv/bin/python"

echo "==> Checking the console script"
VIRTUAL_ENV="$WORKDIR/venv" "$WORKDIR/venv/bin/scw" version
VIRTUAL_ENV="$WORKDIR/venv" "$WORKDIR/venv/bin/scw" doctor

echo "==> Importing every public namespace from the installed wheel"
SCW_VERIFY_EXTRAS="$EXTRAS" "$PY" - <<'PY'
import importlib
import os

import scw

#: Always available (no optional dependency).
CORE = [
    "scw",
    "scw.config",
    "scw.exceptions",
    "scw.math_core",
    "scw.numerical",
    "scw.manifold",
    "scw.physics",
    "scw.experiments",
]
#: Imported only when the matching extra was requested.
OPTIONAL = {"symbolic": "scw.symbolic", "visualization": "scw.visualization"}

extras = {e for e in os.environ.get("SCW_VERIFY_EXTRAS", "").split(",") if e}
namespaces = CORE + [ns for extra, ns in OPTIONAL.items() if extra in extras]

for namespace in namespaces:
    module = importlib.import_module(namespace)
    assert getattr(module, "__all__", None), f"{namespace} has no __all__"

from scw.math_core import Vector

assert Vector([3.0, 4.0]).norm() == 5.0
print(f"scw {scw.__version__}: {len(namespaces)} namespaces import from the wheel")
PY

echo "==> Install verification passed"
