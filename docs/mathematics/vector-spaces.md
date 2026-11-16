# Vector spaces, vectors and covectors

A `VectorSpace` is a finite-dimensional real vector space with a dimension and
an optional name.  Two spaces are equal when dimension and name match, which is
what lets operations reject vectors that belong to different spaces.

A `Vector` holds coordinates in an implicit, fixed basis as a `float64` array.
It supports addition, subtraction, scalar scaling, an explicit `dot` product,
and `norm`.  Coordinates are copied on construction and exposed read-only, so
external mutation cannot change a vector's state.

A `Covector` is an element of the dual space: a linear functional
`alpha: V -> R`.  It is a distinct type from `Vector` on purpose.  The natural
pairing `alpha.evaluate(v)` (also `alpha(v)`) requires matching dimensions and
is linear in both arguments.

A `Matrix` is a rectangular array.  As the representation of a linear map it
has `codomain.dimension` rows and `domain.dimension` columns; `LinearMap` makes
those input/output dimensions explicit and validates them on every `apply`.
