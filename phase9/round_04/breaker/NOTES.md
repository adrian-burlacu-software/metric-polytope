# Round 04 breaker notes (9c)

## Candidates: 29 within-bound unreachable vertices at n = 10, 11, built ONLY from reached pieces
Seeds = the 404 reached n = 7/8/9 Deza reps of `results/phase9/baseline.json` reached_targets (n = 7, 8 ids are
1-based into `load_ext`, n = 9 ids are rows of coords.npy). `gen4.py SEED SECS BUDGET` (seeds 1-4 at 200 s, 5-7 at
150 s with walk-heavy mixing) builds:
- RG: glue of two different reached reps over an exactly matching K (|K| = 5..7), fiber LP vertex;
- RL: lift chain of one reached rep to n = 10 / 11;
- RW: face walk (LP over all of m_n, objective 1000 x random 60-96 % of the tight rows + noise), chained up to ~5 steps,
  starting from RG / RL vertices;
- RM: LP with objective = random halves of the tight rows of two RG/RL vertices.
Only within-bound points (odd prime powers of D <= 2n-3), dedup by `canon_large.canonical_key`, known orbits
(`large_orbits.json` + round-3 candidates) skipped; each tested with `reach_large.reachable(budget 15)`.

Rate (all 7 seeds, distinct new orbits tested): RG 0/277 unreachable, RL 0/492 (2 undecided), RW 29/257 (11 %),
RM 1/18. Total 30/1044 = 2.9 %. As expected, RG/RL outputs of reached parts are always reachable (a vertex of m_n
whose two covering restrictions are reached is reached by glue/lift); unreachability appears only after walking
away on faces, typically 1-3 walk steps from a lift or glue of reached reps.

All 30 False points re-checked with `final.py` = `reachable_bu` + the round-3 accepted move `radial-normalized`
(rules/phase9_accepted.mpr is still empty, so loaded from round_03/maker): all False (1.2-52 s). Dropped the one
taking 52 s (too close to the judge's 60 s budget) -> 29 candidates. check_point (without the rule field) ->
`check_vertex.txt`: 29/29 vertex.
n = 10: D 9 x5, 10 x2, 11 x3 (one RM), 13, 15 x2.  n = 11: D 9 x5, 10, 11 x6, 12 x2, 13, 14.

## Maker proposals (fiber-midpoints, fiber-thirds)
`final.py` with radial-normalized + both proposals on the first candidate (n = 10, D = 9): reachable_bu returned
None after 60.1 s (budget hit), and the second point did not finish before my 290 s kill (a single forward
application of fiber-vertices over a 9-10 node subset is not interrupted by the budget). So I could NOT decide
whether the candidates survive these moves; note for the judge: with these moves the n = 10/11 search is likely to
time out (undecided) rather than certify. Not broken, not confirmed.

## Files
gen4.py, final.py, gen4_*.json / .log (tested points, reach results), false_a/b.json, bu_a/b.json (bottom-up
re-check), chk_norule.json, check_vertex.txt, candidates.json. Compute: about 25 min process time (over the ~20 min
target by ~5 min because the maker-move re-check ran into its timeout).
