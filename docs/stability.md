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
| **stable** | Frozen since 1.0. A breaking change happens only in a major release, after the deprecation process below. |
| **provisional** | Shipped and usable, but may change in a `0.y` release. A breaking change is still announced in `CHANGELOG.md` and, where practical, goes through the deprecation process. |
| **experimental** | May change or be removed in any release, with no deprecation period. |
| **deprecated** | Still works, but scheduled for removal; using it emits a `DeprecationWarning`. |

Current levels — at 1.0 every public namespace is **stable**:

| Namespace | Level |
| --- | --- |
| `scw.math_core` | stable |
| `scw.numerical` | stable |
| `scw.exceptions` | stable |
| `scw.manifold` | stable |
| `scw.physics` | stable |
| `scw.experiments` | stable |
| `scw.symbolic` | stable |
| `scw.visualization` | stable |

The level of every namespace is recorded in
[`docs/public-api-frozen.json`](public-api-frozen.json) and checked by
`scripts/public_api.py --check`, so promoting or demoting a namespace is a
reviewable change to a single source (`STABILITY` in that script).

### How the levels were decided

The mathematical core (`scw.math_core`, `scw.numerical`) has been in use since
0.1 and its semantics are settled. The layers added later (manifold, physics,
experiments, and the optional symbolic/visualization adapters) were
*provisional* during 0.x while their signatures settled; at **1.0** their
public surface has been reviewed and frozen, so all of them are now **stable**.
The vocabulary above is kept because a future major cycle may introduce a
genuinely new, provisional layer.

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

- **Major** (`1.0.0`, `2.0.0`, ...): may break stable names, after the
  deprecation process.
- **Minor** (`1.y.0`): adds features; does not break *stable* names.
- **Patch** (`1.y.z`): bug fixes only; no public-surface change.

During 0.x the minor number played the role of "major" for the still-moving
layers; that is why they were marked *provisional* rather than *stable* until
1.0.

## The road to 1.0

1. **0.9** — froze the public surface, tagged every section with a stability
   level, wired the enforcement into CI, and published this policy.
2. **1.0 (this release)** — promoted every layer to *stable* once the public
   signatures had been reviewed, completed the install/usage documentation,
   and turned on the CI release pipeline. From now on, breaking a *stable* name
   requires a major release and the deprecation process above.

Beyond 1.0 the same policy governs: a new feature may ship as *provisional* in
a minor release and be promoted to *stable* later; a removal starts with a
deprecation and lands no earlier than the next major release.

## Checking the surface yourself

```bash
uv sync --all-extras
uv run python scripts/public_api.py --check    # non-zero if the surface drifted
uv run python scripts/public_api.py            # refresh the snapshot and api.md
```
