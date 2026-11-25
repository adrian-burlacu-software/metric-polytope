# Phase 9 — Rule breaker brief (round 18, family study)

This round is different from rounds 1–17. The rule maker proposes **conditions on weighted graphs** that are claimed
to characterise one family of extreme rays of the metric cone for every number of nodes. You find counterexamples.
Your candidates count only when the judge (`scripts/phase9/judge_family.py`) confirms them exactly.

## The objects
- A weighted graph on nodes 0..k-1: `edges = [[a, b, w], ...]`, integer weights w. Its metric d is the weighted
  shortest-path metric.
- **Minimal:** the graph is exactly the minimal graph of d (a pair is an edge iff no third node lies exactly between
  its ends).
- **Ray:** d spans an extreme ray of the metric cone MET_k (tight triangle equalities of rank C(k,2) − 1).
- **The family:** rays whose minimal graph has all weights in {1, 2}. In scope for this round: connected, minimal
  graphs with weights in {1, 2}, rays or not.

## Claims to attack
The maker's files appear in `phase9/round_18/maker/*.py` during the round (each has NAME, KIND, STATEMENT and
`claim(k, edges)`). The maker works in parallel, so the folder may be empty at first: start with the generic work
below and look again later.
- KIND `necessary`: break it with a **ray** of the family on which `claim` is False.
- KIND `sufficient`: break it with an in-scope **non-ray** on which `claim` is True.
- KIND `iff`: either.

## Generic work (useful whatever the maker proposes)
The data are complete for k ≤ 8 and only a sample at k = 9, so new objects at k = 9, 10, 11 are what can break a
claim that fits the data:
1. **New rays on 9–11 nodes** of the family, built from known ones: e.g. add a node adjacent to a chosen set and
   test; duplicate a node at distance 2 (a "false twin"); join two rays along a common part; complete multipartite
   graphs and their relatives; subdivide or contract edges; unusual shapes (large girth, bipartite, high or low
   degree, many weight-2 edges, weight-2 edges forming a cycle or a matching). Save every ray you find with how you
   built it; odd-looking rays are the most valuable.
2. **Near misses:** in-scope non-rays that look as much like rays as possible (one short of the full rank, same
   degree sequence as a ray, one edge away from a ray).

## Data and tools (all in `results/phase9/family12/`)
- `rays_k5.json` … `rays_k8.json`: all rays of the family on 5–8 nodes up to relabelling (1, 3, 28, 925).
  `rays_k9.json`: a sample on 9 nodes. `nonrays_public_k6..9.json`: in-scope non-rays.
- Library `scripts/phase9/family12.py`: `metric(k, edges)`, `is_minimal(k, edges)`, `is_ray(d)`, `check(k, edges)`,
  `dedupe(items)`. Exact check from the shell: `.venv/Scripts/python scripts/phase9/family12.py check FILE.json` with
  `{"k": .., "edges": [[a, b, w], ...]}`.
- Background: `docs/phase9_report.md` (2 pages), `docs/phase9_status.md` §14–§17.

## Output
`phase9/round_18/breaker/candidates.json`: a JSON list of
`{"k": .., "edges": [[a, b, w], ...], "claim": "NAME of the maker claim, or generic", "how": "one line"}`.
At most 60 candidates, each checked with the tool first (connected, minimal, weights in {1, 2}; ray or non-ray as
intended). Also write all new rays you found on 9–11 nodes to `phase9/round_18/breaker/new_rays.json` (same format,
no limit): they are useful even when they break nothing.

## Rules of conduct
- Write only inside `phase9/round_18/breaker/`. Do not edit anything else, and do not run the judge.
- Compute: keep any single command under 5 minutes, at most 4 processes, about 20 minutes of compute in total.
- Add `phase9/round_18/breaker/NOTES.md`: what you attacked, how, what you found, and which claims you could not
  break.
- Finish with a short summary.
