# Phase 9 — Rule maker brief (round 18, family study)

This round is different from rounds 1–17. You do not propose moves. You propose **conditions on a weighted graph**
that characterise one family of extreme rays of the metric cone, valid for every number of nodes. Your proposals count
only when the judge (`scripts/phase9/judge_family.py`) confirms them in code.

## The objects
- A weighted graph on nodes 0..k-1: `edges = [[a, b, w], ...]`, integer weights w. Its metric d is the weighted
  shortest-path metric.
- The graph is **minimal** if it is exactly the minimal graph of d: a pair is an edge iff no third node lies exactly
  between its ends (d_ab = d_am + d_mb for no m).
- It is a **ray** if d spans an extreme ray of the metric cone MET_k: the tight triangle equalities
  d_ij = d_im + d_mj have rank C(k,2) − 1.
- **The family:** rays whose minimal graph has all weights in {1, 2}. Weights all 1 are the classical "graphic" case.
- Why it matters: every vertex of the metric polytope m_n adjacent to a cut is a scaled ray, and the question of
  Phase 9 is whether any infinite family of them has a description valid for all n (`docs/phase9_report.md`, 2 pages;
  `docs/phase9_status.md` §14–§17 for the graph view).

## Data (all in `results/phase9/family12/`)
- `rays_k5.json` … `rays_k8.json`: **all** rays of the family on 5–8 nodes up to relabelling (1, 3, 28, 925; of which
  1, 3, 19, 485 unweighted). `rays_k9.json`: a large sample on 9 nodes (not complete).
- `nonrays_public_k6.json` … `_k9.json`: minimal {1,2}-weighted graphs that are **not** rays (perturbations of rays).
  The judge also has a held-out set you do not see.
- `summary.json`: counts of all rays per weight alphabet for k ≤ 8.
- Library: `scripts/phase9/family12.py` (`metric`, `is_minimal`, `is_ray`, `check`, `dedupe`);
  `.venv/Scripts/python scripts/phase9/family12.py check FILE.json` gives the exact verdict for
  `{"k": .., "edges": [...]}`.

## What to propose
Files `phase9/round_18/maker/NN_name.py`, at most 8, each defining:
```python
NAME = "short-name"
KIND = "necessary"      # or "sufficient" or "iff"
STATEMENT = "One sentence, true for every k, in plain mathematical language."
def claim(k, edges):    # edges: list of (a, b, w); return bool
    ...
```
- `necessary`: every ray of the family satisfies it. `sufficient`: every minimal {1,2}-weighted graph satisfying it
  is a ray. `iff`: both.
- The condition must be **combinatorial**: stated in terms of the graph (degrees, cycles, distances, neighbourhoods,
  bipartiteness, twins, subgraphs, weight-2 edge structure, ...). It must **not** compute the rank of the tight system,
  solve linear systems, or call `is_ray` / `check` or anything equivalent; such a claim is the definition, not a rule,
  and will be rejected. Computing shortest-path distances is allowed.
- No upper bound on k and no lookup tables of known rays.
- Value: a necessary condition is worth as much as the share of non-rays it rejects; a sufficient one as much as the
  share of rays it accepts. A trivial condition (True for everything) is worthless. The judge reports both shares.
  An `iff` that survives is the prize; a necessary and a sufficient condition that are close to each other are the
  realistic aim.

## Suggestions
- Start with the unweighted case (weights all 1): which graphs give rays? Known sufficient classes include complete
  multipartite graphs with enough parts of size ≥ 2 and their near relatives; look at what the 485 unweighted rays on
  8 nodes have in common (diameter, triangles, bipartite or not, twins, degree bounds).
- Then ask what a weight-2 edge needs: in the data, where do weight-2 edges sit relative to the weight-1 graph?
- Rigidity intuition: d is a ray iff the only way to perturb the distances while keeping every tight triangle
  tight is scaling. A tight triangle is a geodesic a–m–b. So the geodesic structure must tie all pairs together
  rigidly: look for a combinatorial reason (e.g. every pair lies on enough geodesics; odd closed chains of geodesic
  relations, as in the anchors of `docs/phase9_status.md` §10).
- Check each claim yourself on all the data before submitting, and report the two shares.

## Rules of conduct
- Write only inside `phase9/round_18/maker/`. Do not edit anything else, and do not run the judge.
- Compute: keep any single command under 5 minutes, at most 4 processes, about 20 minutes of compute in total.
- Add `phase9/round_18/maker/NOTES.md`: what you tried, what failed and why, and the shares for each claim.
- Finish with a short summary.
