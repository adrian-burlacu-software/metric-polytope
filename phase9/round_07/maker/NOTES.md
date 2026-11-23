# Round 07 maker notes

## Proposals

| file | kind | group | reason | try_rule (20 probes) | cost (timing7.py, G-mode apply_move, sec per input of size 5/6/7/8) | sim3.py gain (backward cascade, glue ignored = lower bound, start = current reached) |
|---|---|---|---|---|---|---|
| 01_radial_lowend.mpr | move, :grow 1, G-equivariant (switchings enumerated inside) | C, n = 8 (D = 10, 6) and n = 9 | in each switching frame z and for each node j of a maximum pair of z: new node at alpha = maxc(z minus j)/2 from every node but j (the Lambda^1 column of z restricted to all-but-j), and at the low end L_j of its feasible interval from j | 2565 outputs, all feasible, 158 vertices, 1.8 s. hits_unreached_nodes: not reported for moves | 0.02 / 0.05 / 0.10 / 0.26; outputs per input 50 / 112 / 196 / 439 | **39 targets: n = 8: 18 (D = 10: 16, D = 6: 2), n = 9: 21 (D = 10: 15, 12: 4, 14: 1, 20: 1)**; +848 nodes. The n = 8 gain is 18 of the 21 group-C targets "blocked above 5 nodes" |
| 02_dup_thirdshift.mpr | move, :grow 1, G-equivariant | C, n = 8 (D = 12) and n = 9 (D = 12, 15, 18) | partial-dup column of i at t in {1/4, 3/4, 1}, then one other entry j at 1/3 or 2/3 of [L_j, U_j] (cheap subset of round 6's dup-recentre, which was dropped for budget) | 3552 outputs, all feasible, 1440 vertices, 5.0 s. hits_unreached_nodes: not reported for moves | 0.05 / 0.10 / 0.21 / 0.26; outputs per input 120 / 180 / 252 / 336 | **15 targets: n = 8: 3 (D = 12: 3), n = 9: 12 (D = 12: 8, 15: 2, 18: 2)**; +864 nodes |

try_rule reports `hits_unreached_nodes` only for generative rules; for moves it only probes outputs. The hit evidence for
both moves is from sim3.py: the round-6 cascade with two new column generators added (`radx`, `radxm`), exact Fractions,
started from the current `checkpoints/phase9/reached.json` (after dup-midshift).

Direct check of the DSL move against the sim generator (verify_move.py, all 43 n = 8 frontier pairs, i.e. a reached
restriction of >= 4 nodes plus one more node, unreached): the DSL radial-lowend and the sim column test agree on all 43
pairs: 7 direct hits (Z of 5 nodes: 4, 6 nodes: 3); the remaining sim gain comes through lift/radial afterwards.
dup-thirdshift on 400 of the 971 n = 9 frontier pairs: 2 direct hits.

COST RISK: both moves cost about 0.26 s per 8-node input, 4 to 5 times dup-midshift (0.06 s) but about 5 times less
than dup-recentre (1.37 s, dropped at 300 s and at 900 s). The first version of 01 (every j, not only the nodes of a
maximum pair) gives 48 targets (n = 9: 30 instead of 21) but costs 0.57 s per 8-node input, so I restricted j.

## How 01 was found (fc.py, exact)
- For the group-C targets at n = 8 I took every unreached (s+1)-node restriction Z whose s-node restriction Y = Z - v is
  reached (s = largest reached size), and computed the face of the fiber over Y that contains the new column b.
  Almost all of them are on fiber edges (dim 1): D = 10 at s = 5: 13 targets with 3 edge cases each.
- The edges: 37 of 46 D = 10 cases are midpoints (t = 1/2) of edges between two fiber vertices that are not twins or
  dups, with direction a +-1 vector of full support. In a switched frame the column is constant (alpha) except one
  entry j, and alpha = half the maximum of z without node j (not the global maxc: with the global maxc, sim mode `radt`,
  only 12 targets).
- Sim variants (targets n = 8 / n = 9): radx, all j, entry j at the low end: 18 / 30; low end and high end give the
  same set; midpoint: 18 / 16; radxm (j on a maximum pair only, proposed): 18 / 21; radmid (global alpha, midpoint):
  0 / 1.

## Negative results (groups A and B, exact; no proposal)
- **Groups A and B at n = 8 can only be reached by base pieces at n = 8 itself.** Every proper restriction of a D = 11
  or 13 target carries 11 or 13 (no reached node or m_<=7 vertex does). For the D = 8 targets, a vertex restriction on
  <= 7 nodes would have D <= 4. All of those are reached, so it would appear in the shadow profile, and there is none.
  A base piece that is a restriction is therefore impossible, and a new family has to output these m_8 vertices
  directly. Moves cannot help (as the brief says).
- Structure found (vals.py, even.py): in a suitable switching, 17 of 18 D = 11 targets have values {2, 4, 6, 8}/11, and
  15 of 16 D = 13 targets have values {4, 6, 8, 10}/13. So x = (2/tau) d for an integer metric d with tau = 11 or 13,
  but d is never a graph metric (shift.py: no switching gives lam (d_G + c), c = 0..5, for any target in groups A or B
  at n = 8). 40 of 49 D = 8 targets have values {2, ..., 6}/8, and their non-redundant edge weights are {2, 3} (wg.py,
  wg2.py).
- Families tested and rejected on the data (none gives more than 1 target):
  - 7-node restriction = lam d_G up to switching (gm.py): D = 13: 1 of 16; D = 11: 0 of 18; D = 8: 0 of 49. At n = 9,
    no 8-node restriction of the D = 11, 13 or 17 targets is lam d_G (0 of 127, 106 and 27). So fiber vertices over
    scaled graph metrics cannot reach them.
  - Sum of two graph metrics lam (d_G + d_H) (sum2.py): D = 13: 1 of 16; D = 8, 11, 7, 14: 0.
  - Lift chain from a scaled graph metric: every D = 13 target has a 5-node restriction (4/13) d_G with G of
    diameter 2 (gm.py with k = 5: 16 of 16; D = 11: 17 of 18 with lam = 4/11 or 3/11). But a chain in which every step
    is a fiber vertex exists for only 2 of 16 (chain.py).
  - Two scaled-graph-metric restrictions covering all 8 nodes (cover.py): 16 of 16 D = 13 targets are covered by a
    5-node (4/13) d_G and a 4-node (5/13) d_G' with a 1-node overlap. So these targets are vertices of the
    corresponding glue polytope (12 holes). But I found no natural open-ended family here: the scales are ad hoc and
    the enumeration (graph pairs x overlaps x switchings x cdd) is too large. D = 11: 9 of 18 covered; D = 8: 5 of 49.
- Group C sim variants not proposed: pd2 with t = 1/2, s = 1/2: 0 targets; t in {1/3, 2/3}, s = 1/2: 8 (n = 9 only);
  t = 1/2, s in {1/3, 2/3}: 4 (n = 9). Full dup-recentre now gives 29 targets (n = 8: 3, n = 9: 26) at 1.37 s per input.

## Compute
About 14 process-minutes in total: about 3 minutes of data analysis scripts; 12 sims (13 to 50 s each, at most 4 in
parallel); timing x3; try_rule x3; verify_move x3. All my processes have finished. Gain lists:
gain_radxm_1_1.json (proposal 01) and gain_pd2_2_2.json (proposal 02, sim_q2_t.log). The gain_radx_1_* files come from
several runs with the same file name and were overwritten; the sim_*.log files are the record.
