# Round 05 maker notes

## Proposals

| file | kind | reason | cost per input (timing.py, apply_move as_orbits, after warm-up) | evidence |
|---|---|---|---|---|
| 01_partial_dup.mpr | move, :grow 1, G-equivariant | copy of node i at distance t*delta_i from i, delta_i = min_j min(2d_ij, 2-2d_ij), t = p/q, 0<p<q<=6 (t=1 is stdlib dup, t=0 the twin): points on the twin--dup fiber edge | 11n outputs: n=6: 66, n=7: 77, n=8: 88 outputs; 0.01-0.02 s | try_rule (20 probes): 1309 outputs, all feasible, 429 vertices, 2.1 s (includes one-time equivariance check). Cascade sim (sim2.py rc_twin, 11 fractions): +2725 nodes (4:17, 5:101, 6:385, 7:1076, 8:955, 9:191), **299 unreached targets (n=8: 114, n=9: 185)**, target D: 9:172, 10:6, 12:86, 15:26, 18:9; saturated in 26 s |
| 02_partial_pendant.mpr | move, :grow 1, Sn-equivariant only | new node hanging off node i at distance s = t*s_max, d(v,j) = d(i,j)+s, s_max = (2 - max perimeter through i)/2, t = p/q, q<=4 | 5n per switching; the judge expands switching classes: n=6: 960, n=7: 2240, n=8: 5120 outputs; 0.55 / 1.8 / 5.3 s | try_rule: 595 outputs, all feasible, 515 vertices, 0.6 s. Sim (target frame only, so a lower bound): +1056 nodes, **131 targets (n=8: 39, n=9: 92)**, D: 6:2, 9:52, 10:4, 12:70, 18:3 |

Union of both (sim, 11 fractions for both): 352 targets (n=8: 120, n=9: 232), D in {6, 9, 10, 12, 15, 18}.
Both moves build only the new column, so x stays the restriction on the first n nodes (restriction-preserving also
on non-vertex inputs). Neither enumerates fiber vertices.

Note: try_rule reports no hits_unreached_nodes for moves, so the hit evidence comes from sim2.py. That is the
round-4 backward cascade (simulate.py) with cheap column generators. It is an exact Fraction test, propagated with the
engine's cached lift/radial predecessors, and it ignores glue, so its counts are lower bounds.

## Analysis (exact; hyp.py, edges2.py, cls.py, cheapcols.py, sim2.py)
- Fiber-edge directions at frontier nodes always have entries in {0, +-1}. Positions are t = 1/2, 1/3, 1/4, and a few 1/6, 2/5.
- For twin columns, the only non-degenerate one-entry move is entry i, which gives the twin--dup edge. Other entries are pinned
  because d(v,i) = 0. On that edge, t = 1/2 alone gives only 6 targets (round 4's "dup/2" tag was rare). t = 1/3, 2/3
  gives 176 targets (D = 9) and t = 1/4, 3/4 gives 87 (D = 12). q <= 6 gives 299.
- Shift of a twin by s*1 ("pendant") is the other cheap fiber edge: 131 targets with q <= 4, 76 with q <= 3.
- Other variants I tested: one-entry re-centring of ALL fiber vertices (rc_fiber, t = 1/2) gives 142 targets but needs
  |V|*n outputs (up to 4046 columns per size-7 input). Midpoints and thirds of twin pairs: only 184 frontier nodes, so I
  did not propose them.

## Compute
About 12 process-minutes: sims of 4-140 s, try_rule x2, timing x2. All my processes finished. The python processes
still running (final5.py) belong to the breaker.
