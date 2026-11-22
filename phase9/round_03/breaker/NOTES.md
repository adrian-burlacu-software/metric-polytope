# Round 03 breaker notes (9c)

## Main result: 40 within-bound unreachable candidates at n = 10, 11
Every candidate satisfies the denominator lemma bound (all odd prime powers exactly dividing D are <= 2n - 3), so
the lemma does NOT explain them. Each was filtered with `metricpoly.reach_large.reachable(x, budget=20)` (the
judge's own n >= 10 search; no maker moves) and returned False = complete search, nothing reaches it
(968-1981 memo nodes, 2.7-9 s each). All 40 are exact vertices: `check_point.py chk_norule.json` -> `check_vertex.txt`
(run WITHOUT the rule field, which does not finish at n >= 10).

| n | D (construction G = glue, W = face walk, L = lift chain) |
|---|---|
| 10 | 7 G, 7 L, 8 G, 8 W, 9 G, 9 W, 9 L, 10 W, 10 L, 11 G, 12 G, 13 G, 14 G, 15 W, 16 W, 17 W, 18 W, 20 W, 21 L, 22 L, 24 L, 32 W |
| 11 | 7 G, 8 G, 9 G, 9 W, 9 L, 11 G, 12 G, 13 G, 14 G, 15 G, 16 G, 17 L, 18 G, 19 L, 20 W, 21 L, 22 L, 42 L |

Notable: D = 7 at n = 10 and 11 (smallest odd prime); D = 32 at n = 10 (no odd prime at all); D = 17 at n = 10 and
D = 19 at n = 11 sit exactly at the bound 2n - 3.

## Constructions (`gen3.py`, seeds: the 1,142 unreached n = 8 / 9 targets of `results/phase9/unreached_targets.json`)
- G: glue two DIFFERENT unreached targets over an exactly matching sub-configuration K (|K| = 6, 7; matched by a
  row-multiset invariant + backtracking permutation, no switching), random integer objective on the
  A\K x B\K holes (exact cddlib GMP LP, lib9b.py from round 2).
- L: lift chain (random fiber vertices) of one target to n = 10 / 11.
- W: face walk from an L/G vertex (maximize 1000 x a random 85-96 % of its tight rows + noise over all of m_n).
In 40 s it produced 1,513 within-bound vertices; `filt.py` ran reach_large on one or two per (n, kind, D):
106 tested, 72 False, 34 True (reachable ones are mostly small-D walk outputs D = 3..8 and a few lifts), 0 undecided.
n = 12 was not attempted: reach_large skips gluing for |T| > 11, so the judge cannot confirm n = 12 claims.

## Structural rules at n = 9
Round 1 already scanned every ledger rule with an open domain on all 1,056,367 n = 9 reps; all hold except
`at-least-two-cuts` (reported). Capped-domain rules cannot take an n = 9 point. I found no unreported n = 9
counterexample. `rules/phase9_accepted.mpr` is empty. The `block-fractal-*` rules are not in the rules.md ledger.

## Maker proposals
`phase9/round_03/maker/` contained only analysis scripts (no `*.mpr`) whenever I checked, so nothing was attacked.

## Files
gen3.py, filt.py, pool_1.json (generator output), filt_*.json / filt_*.log (reach results), chk_norule.json,
check_vertex.txt, candidates.json. Compute: about 10 min of process time.
