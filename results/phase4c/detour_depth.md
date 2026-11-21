# Derivation depth with and without non-vertex detours

code_version `21649659b6f8f414`, git `ebfa6d653f4b1b07b2fcf5eef9a16e8b8c6f0f4b+dirty`

d_V: shortest chain of single-node deletions to a base piece through **vertices** only; d_F: intermediates may be any feasible point that is a vertex of the fiber over the next one. ∞ = no such chain. Moves not represented: binary gluing, 2-/3-node radial.

## Base set: uniform

| n | orbits | d_V = ∞ | d_V histogram | d_F = ∞ | d_F histogram | max d_F | mean d_F | mean (d_V − d_F) where both finite |
|---|---|---|---|---|---|---|---|---|
| 4 | 1 | 0 | 0:1 | 0 | 0:1 | 0 | 0.00 | 0.00 |
| 5 | 2 | 0 | 0:2 | 0 | 0:2 | 0 | 0.00 | 0.00 |
| 6 | 3 | 0 | 0:3 | 0 | 0:3 | 0 | 0.00 | 0.00 |
| 7 | 13 | 5 | 0:6, 1:2 | 4 | 0:6, 1:3 | 1 | 0.33 | 0.00 |

## Base set: rich

| n | orbits | d_V = ∞ | d_V histogram | d_F = ∞ | d_F histogram | max d_F | mean d_F | mean (d_V − d_F) where both finite |
|---|---|---|---|---|---|---|---|---|
| 4 | 1 | 0 | 0:1 | 0 | 0:1 | 0 | 0.00 | 0.00 |
| 5 | 2 | 0 | 0:2 | 0 | 0:2 | 0 | 0.00 | 0.00 |
| 6 | 3 | 0 | 0:3 | 0 | 0:3 | 0 | 0.00 | 0.00 |
| 7 | 13 | 1 | 0:11, 1:1 | 0 | 0:11, 1:2 | 1 | 0.15 | 0.00 |

