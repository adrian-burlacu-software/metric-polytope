# Round 12 maker notes (dyadic D = 8 group, n = 8)

## Proposals

| file | rule | reason | try_rule |
|---|---|---|---|
| 01_dyadic_tower_w1.mpr | gen-dyadic-tower-w1, :domain (6) | vertices of the (n-6)-fold one-node lift tower (each level: orbits of fiber vertices with denominator exactly 8) over the fixed 6-node dyadic core w1 = 6\|8\|2,2,3,3,3,2,3,3,5,5,5,3,6,2,4 (non-vertex) | n = 6: 0 points; n = 7: 0 points (0.2 s); **n = 8: 53 points, 53 vertices, 53 orbits, hits_unreached_nodes 41, hits_unreached_targets 41 (177 s)**. n = 9: NOT RUN (budget; see cost risk) |
| 02_dyadic_tower_w2.mpr | gen-dyadic-tower-w2, :domain (6) | same tower over the second core w2 = 6\|8\|2,2,2,3,3,2,4,3,3,4,5,5,5,5,6 (non-vertex) | **n = 8: 31 points, 31 vertices, 31 orbits, hits_unreached_nodes 19, hits_unreached_targets 19 (102 s)**. n = 6, 7 not re-run (same structure as 01: 0 points). n = 9: NOT RUN |

Union (from the peel analysis w6.py, which predicted exactly 41 and 19): **47 of the 49 D = 8 targets**; 02 adds 6 that 01
misses. Still uncovered: 2 targets (one needs core 6|8|1,2,2,4,4,3,3,3,3,4,2,6,2,6,6, one 6|8|2,2,3,3,4,4,5,5,2,5,5,4,6,3,3;
not proposed). I did not check the union directly from try_rule output (the emitted keys were not saved); the 41/19 numbers
match w6.py's prediction exactly.

**Honesty about the family:** the core w is a hard-coded 6-node point (a "fixed core"); the n-dependence is the lift tower
(level n - 6). The rule is defined at every n, but its only content beyond the core is iterated fiber vertices with a
denominator filter. The core is not a vertex; only the final outputs are (vertex? filter), so all base pieces are true
vertices.

**COST RISK (n = 9):** at n = 9 the tower has three levels. The level-7 set is the D = 8 fiber-vertex orbits over the
level-6 set (this is what made n = 8 take 100-180 s, mostly the 7-hole fibers in the interpreter). Level 8 would contain
all D = 8 fiber-vertex orbits at 8 nodes (thousands, non-vertices included), each needing an 8-hole fiber. That is very likely
beyond the 900 s allowance. Expect the family to be judged on n <= 8 only. A family that reaches m_8 targets but has no
n = 9 output is acceptable per the brief.

## How it was found (exact; scripts in this folder)
- r7.py: all 392 7-node restrictions of the 49 targets have D = 8 (182 orbits). fib7.py: the one-node fiber over the top
  two 7-node restriction orbits contains 22 and 12 targets; 8 such y's cover all 49 (none of these y are reached).
- peel.py: "x peels to x - v" if x is a vertex of the one-node fiber over x - v (rank of tight rows on the hole columns).
  **Every one of the 49 targets peels all the way down to 3 or 4 nodes** (32 to 3 nodes, 17 to 4). So the targets sit in
  lift-chains of non-vertex dyadic points. None of those points is reached, which explains why moves cannot help.
- liftcl.py: the unfiltered D = 8 lift closure from the 3-node seeds grows to 2,126 orbits at 7 nodes (8 s), and the
  8-node level would take more than 10 minutes, so I killed it. A full dyadic lift closure is too large.
- w6.py: double peel x -> y -> w (y a fiber vertex over w, x over y). **One 6-node core w1 covers 41 of 49**; a second, w2,
  adds 6 more (it covers 19 in all); two more cores cover 1 each. That gives proposals 01 and 02.
- Shapes (yshape.py): w1 in switching {4} is (1/8) d_W with W = weight-2 triangle {0,1,2} plus weight-2 star 3-{4,5},
  and weight-3 edges 0-3, 0-5, 1-3, 2-4, 2-5. w2 (canonical frame) is (1/8) d_W with W = weight-2 paw (triangle {0,1,2}
  + pendant 0-3), and nodes 4 and 5 each joined to 0 and 1 by weight-3 edges.
- wg4.py: the weight-2 / weight-3 decomposition of the targets themselves has no dominant type (best type: 11 targets).
  So I found no closed-form weighted-graph family. 6 targets (186, 221, 230, 291, 471, 492) have no switching with
  non-redundant weights in {2, 3}.

## Not done
- No characterisation of a natural n-family for the cores (task 1 only partly done: the structure found is
  "core + lift tower", not a graph family indexed by n).
- Task 2 (the 9 uncharacterised targets) and task 3 (odd D): not attempted.

## Compute
About 14 process-minutes: fib7.py 120 s, liftcl.py ~130 s (killed), peel/w6/analysis ~1 min, try_rule 01 177 s,
try_rule 02 102 s. No process is left running.
