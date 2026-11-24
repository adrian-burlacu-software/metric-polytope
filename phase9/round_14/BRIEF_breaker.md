# Phase 9 — Rule breaker brief (round 14)

You try to break rules. Your candidates count only when the judge (`scripts/phase9/judge.py`) confirms them in code.
Every candidate must be an exact vertex: all triangle and perimeter inequalities hold, and the tight set has full
rank C(n,2). Check this yourself with the tool before submitting.

## Targets this round (n ≤ 9; this round, also n = 10–11 where cheap)
1. **Structural rules:**
   - the ledger in `rules.md`, sources in `rules/*.mpr`;
   - the accepted Phase 9 claims in `rules/phase9_accepted.mpr`, if any;
   - this round's maker proposals in `phase9/round_14/maker/*.mpr`.

   For each structural rule that currently **holds**, find the **smallest** counterexample (smallest n), if one
   exists in your scope. Rules already marked BREAKS in rules.md need nothing more unless you find a smaller n.
2. **Generative coverage:** find vertices that the current rule set cannot reach (claim `"unreachable"`). In this
   scope, those are n ≤ 9 vertices that are **not** among the judge's targets, which are listed in
   `results/phase9/baseline.json` under `n9_rows`; m_7 and m_8 are complete. Build them by search, by perturbing
   known vertices, by gluing or lifting known vertices, or by reasoning, then check them with the tool.

## Data and tools
- Coordinates are x = nums / D over the pairs (i, j), i < j, in lexicographic order.
- **Known vertices:** n ≤ 6, all of them, via `metricpoly.dsl.prims.p_vertices(n)`. n = 7, 8: Deza orbit
  representatives via `metricpoly.deza.load_ext(n)`. n = 9: `data/deza/orbits9/coords.npy` and `den.npy` hold
  Deza's 1,056,367 representatives (memory-map them).
- **Useful library code:**
  - `metricpoly/core.py`: slacks, tight_set, is_vertex;
  - `metricpoly/group.py`: canonical (n ≤ 9), apply, random_element;
  - `scripts/detour_depth2.py`: fiber_vertex, restrict, matrix;
  - `metricpoly/reach.py`: the reachability engine.
- **Exact check:** `.venv/Scripts/python scripts/phase9/check_point.py FILE.json [--rule NAME]` checks vertexhood, the
  orbit key, whether the point is a currently unreached node or target, and with `--rule` whether that structural
  rule FAILS on the point.

## Output
Write `phase9/round_14/breaker/candidates.json`: a JSON list with one object per candidate, of the form
`{"n": .., "D": .., "nums": [...], "kind": "counterexample" | "unreachable", "rule": "RULE NAME", "how": "one line on how it was found"}`.
For an unreachable claim, use `"rule": "all-moves-cover"`. Submit at most 40 candidates, each checked with the tool
first; prefer the smallest n.

## Rules of conduct
- Write only inside `phase9/round_14/breaker/`. Don't edit anything else, and don't run the judge.
- Compute: keep any single command under 5 minutes, use at most 4 processes, and use at most about 15 minutes of
  compute in total. A canonical form is ~0.05 s for a typical n = 9 point but several seconds for very symmetric
  ones.
- Add `phase9/round_14/breaker/NOTES.md` saying what you attacked, how, and what you found, including rules you
  could not break.
- Finish with a short summary.
