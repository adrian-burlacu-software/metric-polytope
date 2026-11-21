# Phase 6: middle-region catalog

code_version `434d4056253d7be3`, git `f5df41f686f6ae6e0c32c7e54e2fb6a1ee5d9c71`

Middle region = cross block x[T, U], T and U disjoint nonempty node sets; type = canonical form up to row/column permutations, sign flips and transpose. Atom = neither constant up to flips nor one-step expressible (a bi-split whose two off-diagonal blocks are constant up to flips). 'recursive' = built entirely by the block rule from constant pieces (const: constant off-diagonals; structured: off-diagonals at most two-valued up to complement).

## Per n

| n | orbits | distinct types | new types (first seen at n) | new constant | new one-step expressible | new recursive (const) | new recursive (structured) | **new atoms** |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 2 | 2 | 2 | 0 | 2 | 2 | 0 |
| 4 | 1 | 4 | 2 | 2 | 0 | 2 | 2 | 0 |
| 5 | 2 | 12 | 8 | 8 | 0 | 8 | 8 | 0 |
| 6 | 3 | 26 | 14 | 6 | 4 | 10 | 10 | 4 |
| 7 | 13 | 361 | 335 | 42 | 218 | 222 | 267 | 75 |
| 8 | 533 | 41771 | 41410 | 161 | 19514 | 10361 | 33494 | 21735 |

## Most frequent middle types per n (share of orbits containing the type)

- n = 3: `2x1|1|0,0` 100% (first n=3); `1x1|1|0` 100% (first n=3)
- n = 4: `3x1|1|0,0,0` 100% (first n=4); `2x2|1|0,0` 100% (first n=4); `2x1|1|0,0` 100% (first n=3); `1x1|1|0` 100% (first n=3)
- n = 5: `4x1|3|1,1,1,1` 50% (first n=5); `4x1|1|0,0,0,0` 50% (first n=5); `3x2|3|5,5,5` 50% (first n=5); `3x2|1|0,0,0` 50% (first n=5); `3x1|3|1,1,1` 50% (first n=5); `3x1|1|0,0,0` 50% (first n=4); `2x2|3|5,5` 50% (first n=5); `2x2|1|0,0` 50% (first n=4)
- n = 6: `5x1|3|1,1,1,1,1` 67% (first n=6); `4x2|3|5,5,5,5` 67% (first n=6); `4x1|3|1,1,1,1` 67% (first n=5); `3x3|3|21,21,21` 67% (first n=6); `3x2|3|5,5,5` 67% (first n=5); `3x1|3|1,1,1` 67% (first n=5); `2x2|3|5,5` 67% (first n=5); `2x1|3|1,1` 67% (first n=5)
- n = 7: `5x1|3|1,1,1,1,1` 62% (first n=6); `4x2|3|5,5,5,5` 62% (first n=6); `4x1|3|1,1,1,1` 62% (first n=5); `3x3|3|21,21,21` 62% (first n=6); `3x2|3|5,5,5` 62% (first n=5); `3x1|3|1,1,1` 62% (first n=5); `2x2|3|5,5` 62% (first n=5); `2x1|3|1,1` 62% (first n=5)
- n = 8: `3x1|3|1,1,1` 50% (first n=5); `2x1|3|1,1` 50% (first n=5); `1x1|3|1` 50% (first n=5); `1x1|2|1` 49% (first n=7); `4x1|3|1,1,1,1` 49% (first n=5); `3x2|3|5,5,5` 49% (first n=5); `2x2|3|5,5` 49% (first n=5); `5x1|3|1,1,1,1,1` 48% (first n=6)

## n = 8: middle types of reachable vs unreachable orbits, same denominator

Top-level types (T ∪ U = V) and all cross-block types. 'exclusive' = present in ≥ 3 orbits of one group and in no orbit of the other group (same denominator).

| den | group | orbits | distinct top types | top types exclusive (≥3 orbits) | distinct block types | block types exclusive (≥3 orbits) | new-at-8 atoms per orbit (mean) |
|---|---|---|---|---|---|---|---|
| 6 | reachable | 93 | 1151 | 418 | 2810 | 1092 | 41.5 |
| 6 | UNREACHABLE | 2 | 63 | 0 | 301 | 0 | 54.5 |
| 7 | reachable | 55 | 835 | 363 | 2148 | 688 | 91.7 |
| 7 | UNREACHABLE | 3 | 179 | 1 | 855 | 1 | 146.7 |
| 8 | reachable | 25 | 515 | 92 | 1672 | 163 | 127.4 |
| 8 | UNREACHABLE | 49 | 1074 | 279 | 2965 | 514 | 143.5 |
| 10 | reachable | 12 | 641 | 31 | 2904 | 74 | 307.0 |
| 10 | UNREACHABLE | 52 | 2038 | 351 | 6945 | 1474 | 393.9 |
| 14 | reachable | 2 | 128 | 0 | 862 | 0 | 228.5 |
| 14 | UNREACHABLE | 4 | 367 | 4 | 3158 | 517 | 771.5 |

## m7 #12

Distinct block types: 94; first seen at n = 7: 85 (atoms: 18); carried by #12 and by no other m7 orbit: 77.

- `4x3|6|114,114,116,171` = (1/6)·[[2, 2, 2], [2, 2, 2], [2, 2, 4], [3, 3, 3]]  one-step expressible, recursive(structured)
- `4x3|6|115,115,129,129` = (1/6)·[[2, 2, 3], [2, 2, 3], [2, 4, 3], [2, 4, 3]]  one-step expressible, recursive(structured)
- `4x3|6|59,114,114,128` = (1/6)·[[1, 1, 3], [2, 2, 2], [2, 2, 2], [2, 4, 2]]  one-step expressible, recursive(structured)
- `4x3|6|59,114,128,128` = (1/6)·[[1, 1, 3], [2, 2, 2], [2, 4, 2], [2, 4, 2]]  one-step expressible, recursive(structured)
- `4x3|6|65,163,163,163` = (1/6)·[[1, 2, 2], [3, 2, 2], [3, 2, 2], [3, 2, 2]]  one-step expressible, recursive(structured)
- `4x3|6|65,163,163,165` = (1/6)·[[1, 2, 2], [3, 2, 2], [3, 2, 2], [3, 2, 4]]  one-step expressible, recursive(structured)
- `4x3|6|65,163,165,165` = (1/6)·[[1, 2, 2], [3, 2, 2], [3, 2, 4], [3, 2, 4]]  one-step expressible, recursive(structured)
- `4x3|6|65,165,165,165` = (1/6)·[[1, 2, 2], [3, 2, 4], [3, 2, 4], [3, 2, 4]]  one-step expressible, recursive(structured)
- `4x3|6|73,114,114,114` = (1/6)·[[1, 3, 3], [2, 2, 2], [2, 2, 2], [2, 2, 2]]  one-step expressible, recursive(structured)
- `4x3|6|73,114,114,116` = (1/6)·[[1, 3, 3], [2, 2, 2], [2, 2, 2], [2, 2, 4]]  one-step expressible, recursive(structured)
- `4x3|6|73,114,114,130` = (1/6)·[[1, 3, 3], [2, 2, 2], [2, 2, 2], [2, 4, 4]]  one-step expressible, recursive(structured)
- `5x2|6|10,16,16,16,16` = (1/6)·[[1, 3], [2, 2], [2, 2], [2, 2], [2, 2]]  one-step expressible, recursive(structured)

Per m7 orbit: (orbit, new atoms at n=7 it carries, types carried by it alone): [(1, 0, 10), (2, 4, 14), (3, 1, 6), (4, 1, 0), (5, 0, 0), (6, 11, 52), (7, 11, 8), (8, 0, 0), (9, 29, 104), (10, 11, 12), (11, 0, 0), (12, 18, 77), (13, 0, 0)]
