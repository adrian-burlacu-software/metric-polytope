# Round 18 maker notes (family study, weights {1,2})

Data used: all rays for k = 5..8 (1, 3, 28, 925) and the k = 9 sample (27,963): 28,920 rays; public non-rays
k = 6..9 (56, 641, 1,466, 1,511): 3,674. The held-out files were not opened and the judge was not run.

## The one idea behind the claims

A solution x of the tight system satisfies x_ab = x_am + x_mb for every geodesic triple (m between a and b).
So x is fixed by its values on the edges, and the only constraints are "two geodesics of the same pair have the
same x-length". Everything below is a way of reading rigidity off these geodesic exchanges.

- **Geodesic rectangle** (a, a2, b, b2; a2 and b2 between a and b; a and b between a2 and b2): the two relations
  x_aa2 + x_a2b = x_ab2 + x_b2b and x_a2b + x_bb2 = x_a2a + x_ab2 subtract to x_aa2 = x_bb2, x_a2b = x_ab2.
  Opposite sides are equal in every solution. Induced 4-cycles are the unweighted case; this is why K_{2,3} and
  K_{3,3} are rays (all edges fall in one class).
- **Odd closed chain of exchanges**: any two geodesic triples sharing a term give A + B = C + D, i.e. the
  difference relations A − C = D − B and A − D = C − B. Chaining them (signed union-find on differences), a
  difference that comes back as its own negative is zero. The rectangle is the shortest such chain.
- **Propagation**: once classes are merged, a triple long = short1 + short2 with one unknown class fixes it. This
  is what ties a weight-2 edge to the weight-1 edges (a pair with one geodesic through the weight-2 edge and one
  avoiding it).

## Claims and self-test results

Shares: rays accepted out of 28,920; public non-rays rejected out of 3,674. No claim fails on any data item.

| file | kind | status | rays accepted | non-rays rejected |
|---|---|---|---|---|
| 01_unit_rectangle_class | sufficient | proved | 955 (3.3%) | 3,674 (100%) |
| 02_rectangle_propagation | sufficient | proved | 12,693 (43.9%) | 3,674 (100%) |
| 03_exchange_closure_sufficient | sufficient | proved | 28,844 (99.74%) | 3,674 (100%) |
| 04_unweighted_closure_necessary | necessary | **conjecture** | 28,920 (100%) | 670 (18.2%) |
| 05_split_prime | necessary | proved (Bandelt–Dress) | 28,920 (100%) | 2,448 (66.6%) |
| 06_geodesic_exchange_connected | necessary | proved | 28,920 (100%) | 2,696 (73.4%) |
| 07_exchange_quotient_connected | necessary | proved | 28,920 (100%) | 2,093 (57.0%) |
| 08_combined_necessary | necessary | proved | 28,920 (100%) | 3,375 (91.9%) |

Per k (accepted counts; rays 1, 3, 28, 925, 27,963; non-rays 56, 641, 1,466, 1,511):

| file | rays k5 | k6 | k7 | k8 | k9 | non-rays k6 | k7 | k8 | k9 |
|---|---|---|---|---|---|---|---|---|---|
| 01 | 1 | 3 | 10 | 105 | 836 | 0 | 0 | 0 | 0 |
| 02 | 1 | 3 | 19 | 527 | 12,143 | 0 | 0 | 0 | 0 |
| 03 | 1 | 3 | 28 | 925 | 27,887 | 0 | 0 | 0 | 0 |
| 04 | 1 | 3 | 28 | 925 | 27,963 | 29 | 459 | 1,114 | 1,402 |
| 05 | 1 | 3 | 28 | 925 | 27,963 | 6 | 102 | 448 | 670 |
| 06 | 1 | 3 | 28 | 925 | 27,963 | 3 | 58 | 423 | 494 |
| 07 | 1 | 3 | 28 | 925 | 27,963 | 11 | 179 | 601 | 790 |
| 08 | 1 | 3 | 28 | 925 | 27,963 | 0 | 10 | 81 | 208 |

Raw output: `_selftest_5_6_7_8.json`, `_selftest_9.json`. In `_selftest_9.json` the fourth column is still named
`04_exchange_closure_iff` (the dropped iff, same function as 03: 27,887 rays). The k = 9 numbers for the current
file 04 were measured separately: all 5,011 unweighted k = 9 rays accepted, 1,402 of 1,511 non-rays accepted; its
k = 9 ray count of 27,963 follows because it returns True on every weighted graph.

The gap between the best sufficient (03) and the best necessary (08): 76 rays (0.26%) on one side, 299 public
non-rays (8.1%) on the other.

## What failed or was dropped

- **Iff for the whole family: dropped.** "Ray iff the exchange closure succeeds" held for every ray with k ≤ 8 and
  rejects every non-ray by proof, but fails on 76 of the 27,963 k = 9 rays (all with weight-2 edges; listed in
  `_k9_closure_misses.json`). In the misses the quotient is left with 5 classes and relations such as
  C = 2D, E = A + D, C = A + E, which give D = 2A only when three relations are combined. The closure only ever
  combines two. Allowing longer combinations is Gaussian elimination, which the brief excludes, so I stopped.
- **I found no iff.** What remains is 03 (sufficient, 99.74% of rays) and 08 (necessary, 91.9% of public non-rays).
- First version of the closure (two midpoints of the same pair only, before working on classes) missed 21 of the
  925 k = 8 rays; the class-level version (any two triples sharing a class) fixed that.
- Simple structural tests are weak: 2-connectedness alone rejects 17 / 153 / 160 non-rays at k = 6 / 7 / 8;
  "every pair is in a tight triangle and the tight triangles connect all pairs" rejects 28 / 182 / 263; the bare
  count "tight triangles ≥ C(k,2) − 1" rejects 33 / 272 / 351. They are subsumed by 06–08 or folded into 08.
- I did not find a static description (degrees, twins, bipartiteness, forbidden subgraphs) that separates rays
  from non-rays; I did not spend time on such features once the exchange view worked.

## Check beyond the data (k = 10)

`_stress_iff.py`: 1,200 new minimal {1,2}-graphs on 10 nodes, made by adding a node (a twin or a random
neighbourhood) to k = 9 rays, with the exact verdict from `family12.is_ray` (used for testing only; no claim
calls it). 899 rays, 301 non-rays. 03 accepted 897 of the rays and none of the non-rays; 08 accepted all 899 rays
and rejected 265 of the 301 non-rays; the 2 misses of 03 both have weight-2 edges. Output `_stress_k9_s1.json`.
This is a biased sample (children of rays), not evidence about typical 10-node graphs.

## Things the judge should know / where I am unsure

1. **Are 02, 03, 04, 07 "combinatorial"?** They do not compute a rank and do not solve a general system: only
   union-find merges, a signed union-find on differences, and substitution into a single three-term relation with
   one unknown. 03 is provably weaker than elimination (the 76 misses show it). But they are deduction procedures
   on the tight relations, not static graph properties. If that is judged too close to the definition, 01, 05, 06
   and the 2-connectivity + 05 + 06 part of 08 are the claims free of this objection (06 on its own rejects 73.4%;
   I did not measure 2-connected + 05 + 06 without 07).
2. **04 is a conjecture.** No proof; supported by 5,519 unweighted rays (complete for k ≤ 8) and nothing else.
   I would not be surprised if it failed at some larger k, since the weighted analogue already fails at k = 9.
3. **Proofs are sketches** in the file docstrings, not written out formally. The two that carry weight:
   (a) soundness of the closure (every merge is a linear consequence of tight equalities; at the end every class
   is a rational multiple of the seed); (b) the edge reduction behind 06 (solutions = edge assignments in which
   all geodesics of a pair have equal length). 05 relies on the Bandelt–Dress theorem that d − α·cut is a metric
   when α is the isolation index; quoted from memory, not re-derived.
4. **Cost.** 05 is 2^(k−1)·O(k^4); 06 enumerates all geodesics (exponential in the worst case). Fine for k ≤ 10,
   not for large k. 01–04 and 07 are polynomial.
5. **Compute rule broken once.** The k = 9 self-test of all 8 files took 5 min 46 s in one command (limit 5 min).
   Total compute was about 9 minutes wall-clock, at most 4 worker processes.
6. `rays_k9.json` is a sample, so "share of rays accepted" at k = 9 is a share of the sample.

## Files

Claims: `01_…py` … `08_…py` (self-contained, pure Python, generated by `_gen.py`). Tooling: `_gen.py`,
`_test_all.py` (self-test), `_k9_fail.py`, `_stress_iff.py`. Outputs: `_selftest_*.json`,
`_k9_closure_misses.json`, `_stress_k9_s1.json`.
