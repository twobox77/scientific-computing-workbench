# API stability and deprecation policy

This page is the contract for what SCW promises to keep working. It exists so
that a 0.x user can depend on the library without being surprised, and so that
1.0 can be a small step rather than a rewrite.

## What counts as public

The public surface is exactly what each public namespace re-exports in its
``__all__``. Concretely:

- **Public namespaces**: `scw`, `scw.config`, `scw.exceptions`,
  `scw.math_core`, `scw.numerical`, `scw.manifold`, `scw.physics`,
  `scw.experiments`, `scw.symbolic`, `scw.visualization`.
- **Public names**: the members of those namespaces' ``__all__``. The full,
  frozen list is [`docs/public-api-frozen.json`](public-api-frozen.json),
  rendered into [Public API](api.md) and checked by CI.

Everything else is **internal**: names starting with `_`, whole modules
starting with `_` (`_backend`, `_plot`, ...), non-``__all__`` module attributes,
submodule import paths (`scw.math_core.vector`), and the CLI's internal command
functions. Internal code may change in any release, without a deprecation
period.

### The frozen list is enforced, not aspirational

`scripts/public_api.py` imports every public namespace, reads its ``__all__``,
and compares the result against `docs/public-api-frozen.json` and the generated
table in `docs/api.md`. CI runs `python scripts/public_api.py --check`, so a
pull request that adds, removes or renames a public name must update the
snapshot — a deliberate, reviewable edit rather than a silent drift.

## Stability levels

Every public name is tagged with one of these levels (the tag appears on the
section that documents it in [Public API](api.md)):

| Level | Promise |
| --- | --- |
| **stable** | Frozen for 1.0. A breaking change happens only in a major release, after the deprecation process below. |
| **provisional** | Shipped and usable, but may change in a `0.y` release. A breaking change is still announced in `CHANGELOG.md` and, where practical, goes through the deprecation process. |
| **experimental** | May change or be removed in any release, with no deprecation period. |
| **deprecated** | Still works, but scheduled for removal; using it emits a `DeprecationWarning`. |

Current levels:

| Namespace | Level |
| --- | --- |
| `scw.math_core` | stable |
| `scw.numerical` | stable |
| `scw.exceptions` | stable (existing errors) |
| `scw.manifold` | provisional |
| `scw.physics` | provisional |
| `scw.experiments` | provisional |
| `scw.symbolic` | provisional |
| `scw.visualization` | provisional |

### Why the core is stable and the newer layers are not

The mathematical core (`scw.math_core`, `scw.numerical`) has been in use since
0.1 and its semantics are settled, so it is frozen. The layers added later
(manifold, physics, experiments, and the optional symbolic/visualization
adapters) are *provisional*: their shape is right, but a `0.y` release may still
refine a signature or a return type. They become **stable** at 1.0 unless a
release note says otherwise.

## Deprecation policy

When a **stable** (or, where practical, **provisional**) public name has to
change, we deprecate first and remove later:

1. **Announce.** Add a `### Deprecated` entry to the `[Unreleased]` section of
   `CHANGELOG.md`, naming the old and new spelling.
2. **Warn at runtime.** Keep the old name working and make it emit a
   `DeprecationWarning` (`warnings.warn(..., DeprecationWarning,
   stacklevel=2)`). The message states the replacement and the version that
   will remove it. Deprecated names stay in ``__all__`` (and the frozen
   snapshot) until they are removed, so imports keep working.
3. **Wait.** The name is removed no earlier than the **next major release**, and
   never in a patch (`x.y.Z`) release. A deprecation introduced in a `0.y`
   release is removed in the following `0.(y+n)` release at the earliest, and
   only once the replacement has shipped and been documented.
4. **Remove.** In the release that removes the name, move the entry from
   `### Deprecated` to `### Removed` in `CHANGELOG.md`, delete the name from the
   namespace's ``__all__``, and regenerate the snapshot
   (`python scripts/public_api.py`).

### Signature changes

- Adding an **optional** keyword argument with a default is not a breaking
  change and does not need deprecation.
- Making an optional argument **required**, changing a default in a way that
  alters results, or changing a return type *is* breaking: deprecate the old
  form, add the new one, and remove the old one per the schedule above.

### Exceptions

New `SCWError` subclasses may be added in a `0.y` release (they only ever catch
*more*, so existing handlers keep working). A change to the **base classes** of
an existing exception (for example dropping the `ValueError` mix-in) is a
breaking change and follows the deprecation policy.

## Semantic versioning

SCW follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **Major** (`1.0.0`): may break stable names, after the deprecation process.
- **Minor** (`0.y.0`): adds features; may change *provisional* names, with a
  CHANGELOG note. Does not break *stable* names.
- **Patch** (`0.y.z`): bug fixes only; no public-surface change.

Before 1.0 the minor number plays the role of "major" for the still-moving
layers, which is exactly why they are marked *provisional* rather than
*stable*.

## The road to 1.0

1. **0.9 (this milestone)** — freeze the public surface, tag every section with
   a stability level, wire the enforcement into CI, and publish this policy.
2. **1.0** — promote the provisional layers to *stable* once their signatures
   have settled, complete the install/usage documentation, and turn on the CI
   release pipeline. From then on, breaking a *stable* name requires a major
   release and the deprecation process above.

## Checking the surface yourself

```bash
uv sync --all-extras
uv run python scripts/public_api.py --check    # non-zero if the surface drifted
uv run python scripts/public_api.py            # refresh the snapshot and api.md
```
