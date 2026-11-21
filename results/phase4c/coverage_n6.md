# Phase 4c coverage report

code_version `8ee9d6a13e3cb3f5`, git `97712db8c215c8cdce00a29ffb74844f34681f36+dirty`, seed 20261121

Base pieces: data-free generative rules gen-cuts, gen-anticuts, gen-graphic, gen-multipartite, gen-avis-paths, gen-rays, gen-tree-suspension, gen-sporadic.
Moves: twin, dup, radial, radial2, radial3, lift-fiber, glue-all. Gluing overlap cap: none (uncapped).
Absolute closure: saturated = True after 1 rounds (9.5 s).

| n | Deza orbits | reached (absolute: base pieces + moves) | reached (tower: all smaller orbits + moves) | not reached (absolute) | not reached (tower) |
|---|---|---|---|---|---|
| 3 | 1 | 1 | 1 | — | — |
| 4 | 1 | 1 | 1 | — | — |
| 5 | 2 | 2 | 2 | — | — |
| 6 | 3 | 3 | 3 | — | — |

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
