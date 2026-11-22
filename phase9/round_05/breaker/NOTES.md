# Round 05 breaker notes (9c)

## 1. Walk-distance experiment (pre-registered design in walk5.py docstring)
Chains start at S0, a vertex built only from reached pieces. S0 is either a lift chain (RL) or a glue (RG) of reached
n = 7/8/9 Deza reps, and it must be within the bound and satisfy `reachable() == True`. Each chain then takes L = 4 steps.
Three step types (arms):
- d1 = EDGE step to an adjacent vertex of m_n (random rank-(N-1) subset of the tight rows, pushed along the feasible
  edge direction);
- d3 = random vertex of a random 3-dimensional face;
- d0 = the round-4 walk (1000 x random 60-96 % of the tight rows + noise).

Steps that land outside the bound are retried, so chains walk on within-bound vertices.

Seeds: d1 = 1, 2 (8 chains per n) and 11, 12 (20 per n); d3 = 3, 4 (8) and 13 (20); d0 = 14 (20). Seed 14 reached
its 230 s cap early: it ran all 20 n = 10 chains but only about 13 n = 11 chains. Each S_k gets one reachable(15 s)
test unless it is outbound, stuck, a duplicate orbit or known. 'dist' counts the steps since the last chain vertex
confirmed reachable. Full tables are in `table5.txt`.

Unreachable fraction (F / tested; all arms pooled; 'U' = undecided):

| n  | dist 1          | dist 2 | dist >= 3 |
|----|-----------------|--------|-----------|
| 10 | 9/197 (4.6 %)   | 2/16   | 1/4       |
| 11 | 8/290 (2.8 %) + 1 U | 3/16 | 0/3     |

By arm at dist 1:
- n = 10: d1 7/110, d3 2/67, d0 0/20;
- n = 11: d1 3/153, d3 3/104, d0 2/33.

By raw step from S0 (F / tested):
- n = 10: 6/90, 1/59, 2/43, 3/25;
- n = 11: 3/101 (with the U), 4/80, 3/72, 2/56.

Conclusion: unreachability already appears ONE EDGE away from a reachable vertex that was built only from reached
pieces. It is rare (about 3-5 % per edge step). It is about twice as frequent at n = 10 as at n = 11, where more
neighbours are glue or lift reachable. Most steps land on reachable vertices again, so chains seldom go 2 or more
steps without passing a reachable vertex. When they do, the rate rises (5/32 at dist 2), but those cells are small.

## Candidates: 24 new orbits (23 F + 1 top-down undecided)
All 24 are new orbits: none is in `large_orbits.json` or in the round 1-4 candidates, and there are no duplicates
across seeds. All 24 give reachable_bu (no moves) = False, in 1.3-22 s (`bu0_*.json`; `bu5_*.json` holds the runs
with the moves). check_point without the rule field: 24/24 vertex (`check_vertex5.txt`).

dist 1: 18, dist 2: 5, dist 3: 1.

| n  | D values (count)                                     |
|----|------------------------------------------------------|
| 10 | 9 (x6), 10 (x4), 11 (x2)                             |
| 11 | 8 (x2), 9 (x4), 12, 14 (x3), 15, 17                  |

Note: running check_point on a file whose items carry `"rule": "all-moves-cover"` triggers a slow evaluation.
I stripped the field (`chk5_norule.json`).

## 2. Maker proposals (partial-dup, partial-pendant)
The structural claims hold on inspection:
- Feasibility: δ_i ≤ 2d_ij and δ_i ≤ 2 - 2d_ij give the dup triangles. s ≤ (2 - max perimeter through i)/2 gives the
  pendant perimeters, with the degenerate j = k case included.
- Restriction preservation: only the new column is built.
- Switching invariance of δ_i holds, because min(2d, 2-2d) does not change under d -> 1-d.

No counterexample was found.

Move test (`final5.py`, reachable_bu with radial-normalized + partial-dup + partial-pendant, 40 s budget):
- 7/24 stay False (1.5-5.2 s);
- 17/24 undecided (timeout at 40-73 s);
- with no moves, the same 17 are False in ≤ 22 s.

With only the two maker moves: (10, D=10) was undecided after 69 s at a 60 s budget, and (11, D=9) did not finish in
100 s. A single move application is not interrupted by the budget. So the moves did not certify any candidate as
reachable, but they make the bottom-up search time out. Status: undecided, not broken.

## Files
walk5.py, tab5.py, final5.py, walk5_d*_*.json/.log, table5.txt, falses5.json, bu5_*.json/log, bu0_*.json/log,
bumk_*.json/log, check_vertex5.txt, candidates.json.

Compute: about 15 min wall time, with up to 4 processes. Process time was higher, roughly 40 min.
