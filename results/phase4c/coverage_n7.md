# Phase 4c coverage report

code_version `8ee9d6a13e3cb3f5`, git `97712db8c215c8cdce00a29ffb74844f34681f36+dirty`, seed 20261121

Base pieces: data-free generative rules gen-cuts, gen-anticuts, gen-graphic, gen-multipartite, gen-avis-paths, gen-rays, gen-tree-suspension, gen-sporadic.
Moves: twin, dup, radial, radial2, radial3, lift-fiber, glue-all. Gluing overlap cap: none (uncapped).
Absolute closure: saturated = True after 2 rounds (643.0 s).

| n | Deza orbits | reached (absolute: base pieces + moves) | reached (tower: all smaller orbits + moves) | not reached (absolute) | not reached (tower) |
|---|---|---|---|---|---|
| 3 | 1 | 1 | 1 | — | — |
| 4 | 1 | 1 | 1 | — | — |
| 5 | 2 | 2 | 2 | — | — |
| 6 | 3 | 3 | 3 | — | — |
| 7 | 13 | 12 | 12 | #12 | #12 |

Orbit numbers #i are Deza's (data/deza/raw/metric_n.ext order).
Gluing cap: not applied — gluing ran uncapped for every pair, so every unreached orbit is a confirmed non-reach for this move set.

## n = 3

Shortest derivations (absolute closure):

| orbit | denominator | orbit size | derivation |
|---|---|---|---|
| #1 | 1 | 4 | `gen-cuts@3` |

## n = 4

Shortest derivations (absolute closure):

| orbit | denominator | orbit size | derivation |
|---|---|---|---|
| #1 | 1 | 8 | `gen-cuts@4` |

## n = 5

Shortest derivations (absolute closure):

| orbit | denominator | orbit size | derivation |
|---|---|---|---|
| #1 | 1 | 16 | `gen-cuts@5` |
| #2 | 3 | 16 | `gen-anticuts@5` |

## n = 6

Shortest derivations (absolute closure):

| orbit | denominator | orbit size | derivation |
|---|---|---|---|
| #1 | 1 | 32 | `gen-cuts@6` |
| #2 | 3 | 32 | `gen-anticuts@6` |
| #3 | 3 | 480 | `gen-graphic@6` |

## n = 7

Shortest derivations (absolute closure):

| orbit | denominator | orbit size | derivation |
|---|---|---|---|
| #1 | 1 | 64 | `gen-cuts@7` |
| #2 | 3 | 2240 | `glue-all(gen-anticuts@5, gen-graphic@6)` |
| #3 | 3 | 6720 | `gen-graphic@7` |
| #4 | 3 | 1344 | `gen-graphic@7` |
| #5 | 3 | 64 | `gen-anticuts@7` |
| #6 | 4 | 20160 | `gen-graphic@7` |
| #7 | 5 | 23040 | `gen-graphic@7` |
| #8 | 3 | 4480 | `gen-graphic@7` |
| #9 | 7 | 40320 | `gen-graphic@7` |
| #10 | 5 | 16128 | `gen-graphic@7` |
| #11 | 3 | 40320 | `gen-graphic@7` |
| #13 | 3 | 40320 | `gen-graphic@7` |

Not reached (absolute):

| orbit | representative | denominator | orbit size | incidence |
|---|---|---|---|---|
| #12 | (1/6)·(1 2 4 2 2 2 1 3 3 3 3 2 2 2 4 2 2 2 4 4 4) | 6 | 80640 | 23 |

Not reached (tower):

| orbit | representative | denominator | orbit size | incidence |
|---|---|---|---|---|
| #12 | (1/6)·(1 2 4 2 2 2 1 3 3 3 3 2 2 2 4 2 2 2 4 4 4) | 6 | 80640 | 23 |
