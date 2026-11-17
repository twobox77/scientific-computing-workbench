# Physics models and simulation

`scw.physics` (roadmap §11, milestone 0.7) turns the mathematical core into
mechanics.  It builds on `scw.math_core` and `scw.numerical` and imports
neither the CLI, plotting, nor the file system.

## Point masses and forces

A `Particle` is a point mass: a positive, finite `mass` together with a
`position` and a `velocity`, both ordinary `Vector`s.  Its derived quantities
are `momentum` (`m v`) and `kinetic_energy` (`(1/2) m |v|^2`).

A `Force` answers one question — `force(particle, t) -> Vector`.  The forces
shipped here cover the classic introductory problems:

| Force | Law | Conservative |
|---|---|---|
| `ConstantForce(F)` | `F` (a uniform field, e.g. weight) | yes, `U = -F . x` |
| `SpringForce(anchor, stiffness=k)` | `-k (x - anchor)` | yes, `U = (1/2) k \|x - anchor\|^2` |
| `CentralGravity(centre, mu)` | `-mu m (x - c) / \|x - c\|^3` | yes, `U = -mu m / \|x - c\|` |
| `Drag(coefficient=c)` | `-c v` | no |

The conservative ones subclass `ConservativeForce`, so they also provide
`potential_energy(particle, t)` and satisfy `F = -grad U` — a property the test
suite checks numerically with central differences.

```python
from scw.math_core import Vector
from scw.physics import Particle, SpringForce

block = Particle(1.0, Vector([1.0]), Vector([0.0]))
spring = SpringForce([0.0], stiffness=4.0)
spring.force(block, 0.0).data        # [-4.0]
spring.potential_energy(block, 0.0)  # 2.0
```

## Systems and conserved quantities

A `System` groups the particles of one simulation with the forces that act on
all of them, and reports the totals that make conservation laws easy to check:

- `total_momentum()` — `sum_i m_i v_i`;
- `kinetic_energy()` — `sum_i (1/2) m_i |v_i|^2`;
- `potential_energy(t)` — the sum of every force's potential (only when all
  forces are conservative, otherwise `NumericalError`);
- `total_energy(t)` — `K + U`.

## Simulation

`simulate(system, t_span, ...)` writes the equations of motion as the
first-order system `dx/dt = v`, `dv/dt = F(x, t) / m`, packs the state as
`[positions..., velocities...]` and hands it to `scw.numerical.solve_ivp`.  The
result is a `Trajectory`:

```python
import numpy as np
from scw.math_core import Vector
from scw.physics import CentralGravity, Particle, System, simulate

satellite = Particle(1.0, Vector([1.0, 0.0]), Vector([0.0, 1.0]))
system = System([satellite], CentralGravity([0.0, 0.0], mu=1.0))

period = 2.0 * np.pi
traj = simulate(system, (0.0, period), method="DOP853",
                t_eval=np.linspace(0.0, period, 401), rtol=1e-11, atol=1e-13)

traj.positions(0)     # the satellite's path, shape (n_points, 2)
traj.total_energy()   # constant to ~1e-11 over a full orbit
traj.momentum()       # total momentum at each time
```

`simulate` accepts the same integrator options as `solve_ivp` (`method`,
`t_eval`, `rtol`, `atol`, `max_step`, `first_step`, `dense_output`); `method` is
one of `scw.numerical.METHODS`.

## Why it is built this way

The physics layer owns no integration code.  It expresses the model — masses,
forces, the second law — and delegates the number crunching to the numerical
layer's ODE solver, exactly as the numerical layer delegates to SciPy.  A
conservative force declares its potential so that energy conservation becomes a
*checkable* property of a simulation rather than an assumption.

## Errors

- `TypeError` — a non-`Particle` in a system, a non-`Force`, or a non-`Vector`
  position/velocity;
- `DimensionError` — mismatched position/velocity dimensions, particles of
  different dimensions, or a force whose dimension differs from the particle's;
- `ValueError` — non-positive or non-finite mass/stiffness/coefficient,
  duplicate particle names, or an empty system;
- `NonFiniteError` — non-finite vector data;
- `NumericalError` — asking a non-conservative system for its potential energy;
- `ZeroDivisionError` — evaluating central gravity exactly at its centre, where
  the force is singular.

See the runnable
[example](https://github.com/twobox77/scientific-computing-workbench/blob/main/examples/10_physics_simulation.py).
