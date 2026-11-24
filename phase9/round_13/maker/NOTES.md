# Round 13 maker notes (explaining round 12's dyadic towers; n = 9)

## Proposal

| file | rule | reason | try_rule |
|---|---|---|---|
| 01_dyadic_star.mpr | gen-dyadic-star, :domain (6) | stars over the cores w1, w2: n - 6 D = 8 lift columns of the core, each distance between two non-core nodes at an END of its interval over the core (no fibers above 7 nodes); columns pruned to those occurring in an m_8 star vertex for n >= 9 | n = 6: 0 points (0.05 s); n = 7: 0 points (0.1 s); **n = 8: 226 points, 226 vertices, 64 orbits, hits_unreached_nodes 0, hits_unreached_targets 0 (30 s; round 12 needed 177 s + 102 s)**. **n = 9: did NOT finish within a 300 s timeout** (try01_n9.log). Python simulation of the same construction (starsim.py) did not finish its first core within 290 s either. |

Expected value at n = 9 if it could run (exact checks in star.py / star3.py, not from try_rule): the star structure
holds for 5 of the 15 unreached n = 9 D = 8 targets (32300, 177660, 183143, 192595 over w1; 71763 over w2), all with
every pair distance at an interval end. With the m_8-column pruning used in 01, only 3 remain (177660, 183143, 192595);
32300 and 71763 use columns that occur in no m_8 star vertex. **Honest verdict: 01 is cheap at n = 8 but gains nothing
there, and it does not finish at n = 9, so it will very likely gain nothing. I submit it for the record of the
explanation; drop it if n = 9 cannot be run.**

## What was found (task 1)
All exact; scripts in this folder.
- **Peeling the n = 9 dyadic targets (peel9.py).** Every one-node deletion of a vertex is a peel step (a vertex of
  m_n is always a vertex of the fiber over any restriction), so peeling at the top says nothing. All 8-node
  restrictions of all 15 D = 8 and 59 D = 16 targets are unreached. The D = 16 targets have D = 16 already on their
  8-node restrictions (only one target, 877206, has a D = 8 restriction), so **D = 16 at n = 9 is NOT a halving of
  n = 8 D = 8 points**. Minimal peel size: D = 8: 3 nodes (7), 4 nodes (8); D = 16: 3 (27), 4 (32).
- **Cores at n = 9 (cores9.py).** D = 8: 585 distinct 6-node peel cores; w1 lies under 10 of the 15 targets, w2 under 7;
  a greedy cover needs w1 + two other cores (3 + 2). D = 16: 3,819 distinct 6-node cores, all with D = 16; the best one
  (6|16|4,5,5,6,6,5,5,6,10,10,11,5,11,5,6) covers 16 of 59, and 17 cores are needed. So the n = 9 D = 16 targets sit on
  their own towers over D = 16 cores, not over w1, w2.
- **Tower sizes (tower.py, level8.py).** In plain Python the n = 8 towers take 15 s (w1) and 10 s (w2), reproducing
  53 and 31 outputs. Level 7: 83 (w1) and 56 (w2) orbits, deficiency (C(k,2) - tight rank) 1-3; the core w1 has
  deficiency 3. Deficiency never increases along a fiber-vertex lift. **Level 8 over w1 has 7,648 orbits** (deficiency
  0: 53, 1: 343, 2: 2,674, 3: 4,578), 173 s in Python, so a full n = 9 tower needs ~7.6k eight-hole fibers per core:
  out of reach. Restricting level 8 to deficiency <= 1 would keep 9 of the 15 n = 9 targets (chains9.py), but the DSL
  has no rank primitive, so that filter cannot be written.
- **The star description (star.py, star2.py, star3.py)**: the explanation found. Most tower outputs are stars over the
  core: X contains w on a 6-set C; every other node a has X|C+a a vertex of the one-node fiber over w (a "D = 8 lift
  column" of w; w1 has 166 such columns in 83 switching pairs c, 1 - c; w2 has 164); and every distance between two
  non-core nodes is lo(a,b) = max_k |c_a(k) - c_b(k)| or hi(a,b) = min_k min(c_a(k) + c_b(k), 2 - c_a(k) - c_b(k)),
  the ends of its interval over the core alone. This holds for 46 of the 53 w1 outputs and 27 of the 31 w2 outputs at
  n = 8, and for 5 of the 15 n = 9 D = 8 targets (all their pairs at interval ends). The core w1 has no symmetry beyond
  switching the new node (each 7-node orbit is exactly one column pair), so columns cannot be reduced further by
  symmetry. Useful columns are mostly ones with entries in 2..6 (/8), but some use 1 and 7, so there is no clean
  entry filter.
- **Not found:** a description of the cores themselves, or a family of cores indexed by n. The n = 9 targets need
  hundreds of different 6-node cores (585 for D = 8, 3,819 for D = 16), so a rule with a few hard-coded cores cannot
  cover them. My reading: the dyadic vertices are not built by a short rule from a few cores. Stars over a core explain
  most of the n = 8 outputs, but at n = 9 they cover only 5 of the 15 D = 8 targets and none of the D = 16 targets, and
  even that is too slow (about 90k column triples x 4 endpoint choices per core, each needing an n = 9 vertex test).

## Cost problem at n = 9 (task 2: not solved)
gen-dyadic-star avoids fibers, but at n = 9 it must test triples of columns: with the pruning to columns found in an
m_8 star vertex, about 40 columns per core, so about 10k triples x 4 endpoint choices, each needing a feasibility test
and an exact rank-36 vertex test. Unpruned, about 90k triples. Neither finished in Python within 290 s, so the
interpreted DSL is slower still.

## Compute
About 25 process-minutes in all: peel/core/chain/star analyses about 6 min; tower.py 25 s; level8.py 290 s (killed at
its timeout after w1); starsim.py 290 s (timeout, no output); try_rule 01 at n = 6-8 31 s; try_rule 01 at n = 9 300 s
(timeout). No process is left running.
