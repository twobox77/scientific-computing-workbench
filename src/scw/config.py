"""Global configuration and numerical policy for SCW.

The policy is intentionally small and explicit: a single default floating
point dtype and tolerance defaults that callers may override per call.  There
are no hidden global magic constants used implicitly by the algorithms.
"""

from __future__ import annotations

import numpy as np

#: Default floating-point dtype for every domain object.
DEFAULT_DTYPE = np.float64

#: Default relative tolerance for approximate comparisons.
DEFAULT_RTOL = 1e-9

#: Default absolute tolerance for approximate comparisons.
DEFAULT_ATOL = 1e-12
