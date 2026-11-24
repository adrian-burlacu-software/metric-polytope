# Round 16 maker, track A: n = 9 base pieces for D = 11 and D = 13, built targets-first

Scripts and logs in `A_work/`. All analysis is over the n = 9 targets in `results/phase9/unreached_targets.json` with
D = 11 (98) or D = 13 (116); all of them have no reached restriction (shadow_ladder_n9.json).

## Structural findings (exact)

- **Scaled graph metric restrictions** (cov9.py, any switching frame, goods_n9_{11,13}.json): the largest restriction
  of the form (a/D) d_G has 4-7 nodes (D = 13: max 5 for 53 targets, 6 for 41, 7 for 9; D = 11: similar).
- **One-node covers by two scaled graph metrics** (cov_types.py, cov_detail.py): D = 13: only 24 of 116 targets have
  one, and no (G, H, v) type covers more than 2 targets. D = 11: 28 of 98, at most 4 per type. Two-node overlap covers:
  11 targets each. So for D = 13 there is no common glue-of-graph-metrics shape at all.
- **The one recurring D = 11 shape:** G = complement of P_6 at 4/11 (6 nodes) glued at one node with a 4-node H
  (C_4 at 4/11, P_4 at 3/11, K_{1,3} at 3/11, paw, diamond). 14 targets have such a cover; for 13 of them the two-stage
  condition of round 11 holds (stage9.py). This is the house family pattern (co-P_{n-3}) with D = 2n - 7 instead of
  2n - 5. Complements of other linear forests (P_4 + K_2, P_5 + K_1, P_3 + P_3) at 4/11: 11 more targets, but every
  (forest, v, H) type covers 1 target (stage9b.py).
- **Even-frame integer metrics** (dmet.py; x = 2d/D, all but one target per D have an even frame): D = 11 has values
  1..4 (90 of 97), D = 13 has values 1..5 (67) or 2..5 (42); the maximum perimeter equals D in every case.
- **Extreme-ray restrictions** (rays.py, rays2.py, even frame): only 4 of 115 D = 13 and 2 of 97 D = 11 targets have an
  8-node restriction on an extreme ray of MET_8; no D = 13 target has a one- or two-node-overlap cover by extreme-ray
  restrictions. Lift- or glue-type families over rescaled smaller vertices cannot reach these targets.

## Proposals

**No proposal submitted by track A.** One rule was built and withdrawn:

| file | rule | reason | try_rule |
|---|---|---|---|
| A_work/A01_cop_glue_d2n7_WITHDRAWN.mpr | gen-cop-glue-d2n7, :domain (9) | round 11 two-stage glue with D = 2n - 7: (4/D) d(co-P_{n-3}) at path position 0, 1, 2 glued with C_4 at 4/D (u = neighbour of v) or P_4 at 3/D (v an end, u its neighbour); 5 fiber pairs | n = 8: 0 points (co-P_5 at 4/9 is not in m_5, so :domain raised to 9). **n = 9: NOT FINISHED in 600 s** (timeout, no output). A one-pair version (C_4, position 0; A_work/A01_single.mpr) also did not finish in 290 s. |

Expected reach if generation could finish (from stage9.py, not confirmed by try_rule): at most 9 of the 98 D = 11
targets (330509, 374584, 504082, 139506, 378070, 386038, 459358, 375846, 444761), 0 of D = 13. That is narrow, and the
generation cost would very likely exceed the judge's 900 s allowance, so I withdrew it instead of spending judge time.

## Conclusion
Targets-first, the n = 9 D = 13 targets have no shared glue-of-graph-metrics or extreme-ray-restriction structure (at
most 2 targets per cover type); D = 11 has one weak recurring shape (co-P_6 at 4/11, 14 targets, split over ~10
(position, H, u) types). Two-stage fiber enumeration at n = 9 costs more than 5 minutes per fiber pair in the DSL,
so even that shape cannot be turned into a family that the judge can generate. This supports option 4 of
docs/phase9_status.md §8: the D = 11/13 n = 9 targets need base pieces that are new at n = 9 and do not come in
large families of this kind.

## Compute
About 19 process-minutes: try_rule n = 9 600 s (timed out) + 290 s (timed out), analysis scripts about 1 min in total.
No process left running.
