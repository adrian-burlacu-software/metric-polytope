# Derivation depth with and without non-vertex detours

code_version `e091a409e797fa6a`, git `20f5cc1a0d1ec6df145d968e966799b666ee636c`

d_V: shortest chain of single-node deletions to a base piece through **vertices** only; d_F: intermediates may be any feasible point that is a vertex of the fiber over the next one. ∞ = no such chain. Moves not represented: binary gluing, 2-/3-node radial.

## Base set: uniform

| n | orbits | d_V = ∞ | d_V histogram | d_F = ∞ | d_F histogram | max d_F | mean d_F | mean (d_V − d_F) where both finite |
|---|---|---|---|---|---|---|---|---|
| 4 | 1 | 0 | 0:1 | 0 | 0:1 | 0 | 0.00 | 0.00 |
| 5 | 2 | 0 | 0:2 | 0 | 0:2 | 0 | 0.00 | 0.00 |
| 6 | 3 | 0 | 0:3 | 0 | 0:3 | 0 | 0.00 | 0.00 |
| 7 | 13 | 1 | 0:11, 1:1 | 0 | 0:11, 1:2 | 1 | 0.15 | 0.00 |
| 8 | 533 | 380 | 0:108, 1:44, 2:1 | 303 | 0:108, 1:74, 2:44, 3:2, 5:2 | 5 | 0.77 | 0.00 |

