# Round 11 maker notes (base families, two-stage glue)

## Key idea: two-stage glue fibers (cheap version of gen-bipartite-glue)
For a one-node cover x^S|A = lam d_G, x^S|B = mu d_H of a target (|B| = 4), drop one node u of B \ {v}. If x|(V - u)
is a vertex of its own glue fiber (stage 1: G-piece glued with H - u at v), then x is a vertex of the stage-2 fiber
(stage-1 vertex glued with the whole H-piece on the 3 nodes of H - u), which has only n - 4 holes. stage.py checks
this exactly (rank of the tight triangle/perimeter rows restricted to the holes) for every cover and every u.
- D = 13 (K_{2,3} at 4/13 + C_4 at 5/13, v on the 2-side): dropping the C_4 antipode of v works for all 14 covered
  targets. The two-stage rule reproduces exactly the 168 vertices / 14 orbits of gen-bipartite-glue at n = 8 in
  23 s instead of 264 s (stage 1: 8 holes, 964 fiber vertices, 0.2 s; stage 2: 4 holes per fiber).
- n = 9 sizes (s1count.py, D = 15 version of 01): stage 1 has 10 holes, 5,733 vertices (2.4 s); stage-2 cdd
  about 57 s in total; interpreter overhead per stage-1 vertex is the rest.

## Proposals

| file | rule | reason | try_rule n = 7 | try_rule n = 8 | n = 9 |
|---|---|---|---|---|---|
| 01_bipartite_glue_2stage.mpr | gen-bipartite-glue-2stage, :domain (7) | cheap two-stage version of the accepted D = 2n-3 family (K_{2,n-5} at 4/(2n-3), C_4 at 5/(2n-3)) so n = 9 can be generated | 0 points, 0 hits (0.5 s) | 168 points, 168 vertices, 14 orbits = the accepted family's 14 orbits; **hits_unreached_nodes 0** (already reached since round 10), 23 s | NOT FINISHED: the first version (no denominator filter) was killed at 295 s; the filtered version was not re-run at n = 9 (budget). Estimate 4-10 min (02, same structure, did not finish at n = 9 in 240 s), so within the 900 s allowance is likely but NOT confirmed. |
| 02_house_c4_d11.mpr | gen-house-c4-d11, :domain (7) | D = 2n-5 sister: (4/(2n-5)) d(co-P_{n-3}) (= the house at n = 8, glued at a roof-base node = end of the path) + (4/(2n-5)) d(C_4) | 0 points (0.0 s) | 12 points, 12 vertices, 6 orbits, **hits_unreached_nodes 6, hits_unreached_targets 6** (D = 11), 21.6 s | NOT FINISHED within 240 s (killed by timeout, no output). Estimated from the 01 sizes: ~3-5 min, so it should fit the judge's 900 s generation allowance but is not confirmed. |
| 03_house_p4_d11.mpr | gen-house-p4-d11, :domain (7) | D = 2n-5 sister: house-type piece at 4/(2n-5) + (3/(2n-5)) d(P_4) glued at an end of P_4 | 0 points (0.0 s) | 6 points, 6 vertices, 6 orbits, **hits_unreached_nodes 6, hits_unreached_targets 6** (D = 11), 11.9 s | not run (budget) |

Targets: 02 gives ids 394, 396, 399, 477, 485, 494; 03 gives 396, 399, 405, 477, 482, 485 (showcov.py/stage.py);
union 8 of the 18 D = 11 targets at n = 8.

## Structural findings (exact, n = 8)
- **Correction to round 8:** the 5-node D = 11 piece is NOT K_{2,3} but the house (C_5 + one chord = complement of
  P_5); same degree sequence (2,2,2,3,3). (4/11) d(K_{2,3}) is not even in m_5 (three 3-side nodes at 8/11 give
  perimeter 24/11 > 2). v is always a roof-base (degree-3) node. My first K_{2,n-5} versions of 02/03 gave 0 points.
- Every D = 13 target has exactly 2 covers of the K_{2,3}/C_4 type (v on the 2-side and v on the 3-side). Cross
  entries (cross.py) take several values per distance class (3, 5, 7, 9 / 6, 8, 10 over 13): no closed formula for
  the cross block, so a direct pairs-point construction is not possible; the two-stage fiber is the cheap route.
- D = 11, other covers: 446 = 8-edge 5-node piece (degrees 3,3,3,3,4) at 4/11 + P_4 or K_{1,3} at 3/11 (stage
  condition holds); 180 = 6-node 8-edge piece at 3/11 + P_3 at 2/11 (stage condition holds). Single targets, no
  natural n-family, not submitted. Ids 93, 140, 159, 167, 215, 229, 470, 504 still have no one-node cover by scaled
  graph metrics (cover2.py, re-run).
- Dyadic D = 8 group: not attempted (budget).

## Compute
About 15-16 process-minutes: 295 s (killed n = 9 run of unfiltered 01), 240 s (killed n = 9 run of 02), try_rule n = 8 runs
(~2 min in total), analysis scripts (< 1 min). No process left running.
