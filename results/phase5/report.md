# Phase 5: block / fractal decomposition

code_version `dc0c4e1b86686246`, git `427904cef14fdf8389881aed8f65ea2e11fee6a6`

X* = smallest middle class for which a full recursive decomposition exists (const = constant up to flips, twin, 2val = two-valued up to complement, any). 'free': blocks arbitrary; 'vertex-blocks': every block must be a vertex of its own metric polytope ('none' = no decomposition at any level). With free blocks 'any' always succeeds (peeling), so the informative columns are const/twin/2val and whether a non-peeling top split exists.

## By n

| group | orbits | X* free: const | twin | 2val | any | nontrivial top split at X* | X* vertex-blocks: const | twin | 2val | any | none | top-level middle levels (all splits) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| n = 3 | 1 | 1 (100%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 1 (100%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | const 100%, twin 0%, 2val 0%, any 0% |
| n = 4 | 1 | 1 (100%) | 0 (0%) | 0 (0%) | 0 (0%) | 1 (100%) | 1 (100%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | const 100%, twin 0%, 2val 0%, any 0% |
| n = 5 | 2 | 2 (100%) | 0 (0%) | 0 (0%) | 0 (0%) | 2 (100%) | 1 (50%) | 0 (0%) | 0 (0%) | 0 (0%) | 1 (50%) | const 100%, twin 0%, 2val 0%, any 0% |
| n = 6 | 3 | 3 (100%) | 0 (0%) | 0 (0%) | 0 (0%) | 3 (100%) | 1 (33%) | 0 (0%) | 0 (0%) | 0 (0%) | 2 (67%) | const 83%, twin 1%, 2val 16%, any 0% |
| n = 7 | 13 | 8 (62%) | 0 (0%) | 5 (38%) | 0 (0%) | 13 (100%) | 1 (8%) | 0 (0%) | 0 (0%) | 0 (0%) | 12 (92%) | const 27%, twin 1%, 2val 63%, any 9% |
| n = 8 | 533 | 53 (10%) | 0 (0%) | 455 (85%) | 25 (5%) | 519 (97%) | 1 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 532 (100%) | const 1%, twin 0%, 2val 23%, any 75% |

## n = 8 by reachability

| group | orbits | X* free: const | twin | 2val | any | nontrivial top split at X* | X* vertex-blocks: const | twin | 2val | any | none | top-level middle levels (all splits) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| n = 8, reachable with detours | 267 | 53 (20%) | 0 (0%) | 213 (80%) | 1 (0%) | 257 (96%) | 1 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 266 (100%) | const 3%, twin 0%, 2val 41%, any 56% |
| n = 8, UNREACHABLE (the 266) | 266 | 0 (0%) | 0 (0%) | 242 (91%) | 24 (9%) | 262 (98%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 266 (100%) | const 0%, twin 0%, 2val 5%, any 95% |
| n = 8, vertex-only reachable | 153 | 53 (35%) | 0 (0%) | 100 (65%) | 0 (0%) | 143 (93%) | 1 (1%) | 0 (0%) | 0 (0%) | 0 (0%) | 152 (99%) | const 5%, twin 0%, 2val 63%, any 32% |
| n = 8, vertex-only unreachable | 380 | 0 (0%) | 0 (0%) | 355 (93%) | 25 (7%) | 376 (99%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 380 (100%) | const 0%, twin 0%, 2val 7%, any 93% |

## n = 7, orbit by orbit

| orbit | den | X* free | top split | nontrivial top split | X* vertex-blocks | tree depth |
|---|---|---|---|---|---|---|
| #1 | 1 | const | [3, 4] | True | const | 2 |
| #2 | 3 | const | [4, 3] | True | none | 3 |
| #3 | 3 | const | [4, 3] | True | none | 2 |
| #4 | 3 | const | [4, 3] | True | none | 2 |
| #5 | 3 | const | [3, 4] | True | none | 2 |
| #6 | 4 | 2val | [3, 4] | True | none | 2 |
| #7 | 5 | 2val | [3, 4] | True | none | 2 |
| #8 | 3 | const | [4, 3] | True | none | 2 |
| #9 | 7 | 2val | [4, 3] | True | none | 2 |
| #10 | 5 | 2val | [3, 4] | True | none | 2 |
| #11 | 3 | const | [5, 2] | True | none | 3 |
| #12 **← #12** | 6 | 2val | [3, 4] | True | none | 2 |
| #13 | 3 | const | [5, 2] | True | none | 3 |

## m7 #12 on its own

representative: 1/6 1/3 2/3 1/3 1/3 1/3 1/6 1/2 1/2 1/2 1/2 1/3 1/3 1/3 2/3 1/3 1/3 1/3 2/3 2/3 2/3

X* free = 2val, X* vertex-blocks = none

Top-level middle levels over all 63 splits: {'2val': 19, 'any': 44}

Tree at X* (free blocks):
```
split T=[1, 2, 3] | T̄=[4, 5, 6, 7]  middle level 2val  middle = (1/6)·[[4, 2, 2, 2], [3, 3, 3, 3], [2, 2, 2, 4]]
  A:
    split T=[1] | T̄=[2, 3]  middle level 2val  middle = (1/6)·[[1, 2]]
      A:
        leaf [1]
      M:
        mleaf 1x2 level 2val
      B:
        leaf [2, 3]
  M:
    msplit rows [0] cols [0, 1]  off-diagonal levels ['const', '2val']
      mleaf 1x2 level const
      msplit rows [0] cols [0]  off-diagonal levels ['const', 'const']
        mleaf 1x1 level const
        mleaf 1x1 level const
  B:
    split T=[4, 5] | T̄=[6, 7]  middle level const  middle = (1/6)·[[2, 2], [4, 4]]
      A:
        leaf [4, 5]
      M:
        msplit rows [0] cols [0]  off-diagonal levels ['const', 'const']
          mleaf 1x1 level const
          mleaf 1x1 level const
      B:
        leaf [6, 7]
```
