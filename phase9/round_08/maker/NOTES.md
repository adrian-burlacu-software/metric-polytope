# Round 08 maker notes (group B base families)

## Proposal

| file | kind | reason | try_rule |
|---|---|---|---|
| 01_bipartite_glue.mpr | generative, :domain (7) | all vertices of the one-node glue fiber of (4/(2n-3)) d(K_{2,n-5}) (glued at a node on the 2-side) and (5/(2n-3)) d(C_4); at n = 8 this is K_{2,3} at 4/13 and C_4 at 5/13 | n = 7: 802 points, 0 vertices, 0 hits (1 s). **n = 8: 34,916 points, all feasible, 168 vertices, hits_unreached_nodes 32, hits_unreached_targets 14** (264 s, mostly try_rule canonicalising all 34,916 points; cdd alone takes 87 s). **n = 9: NOT RUN.** The fiber has 15 holes, against 12 at n = 8, and would far exceed the 5-minute command limit. I had also used up the compute budget. |

The 14 targets are D = 13 at n = 8 (exp2.py: 168 m_8 vertices in 14 orbits; every one is an unreached D = 13 target).
COST RISK: at n = 8 alone the rule is near the judge's 300 s budget. n = 9 will very likely exceed it unless the judge
caches fiber-vertices or runs n = 8 first. If the family is accepted only in spirit, the D = 13 part could be confirmed
with n = 8 only.

## Structural findings (exact)
- **Every m_8 vertex orbit with D = 11 (18) or D = 13 (16) is unreached, and none is a graph metric** (down.py over the
  Deza reps). All reached n = 8 vertices with odd D are D ≤ 9 or the sporadic D = 15. At n = 7, every odd-D vertex is a
  graph metric (D = 5, 7) or D = 3. So there is no "downward" family with D = 2k-3 or 2k-5 on k ≤ 7 nodes to continue.
- **Every odd-D target (n = 8: D = 7, 11, 13; n = 9: D = 17, 19, 23, 31) is x = (2/τ) d with τ = D.** Here d is an
  integer **extreme ray of MET_n** (the triangle-tight rank is C(n,2) - 1, forced because x is a vertex). For odd D, the
  even switching frame is unique, so d is canonical (dmet.py, dmet_n8.json, dmet_n9_big.json). D = 11: values 1..4
  (one has 5). D = 13: values 2..5 (one has 1).
- Symmetry: |Aut(d)| ≤ 4. Most have trivial automorphism group, and so do all the n = 9 D = 17/19 targets (aut.py). So
  no symmetric family (circulants and the like) can hit them.
- Negative (fam1.py): no target is a·d_G + b·δ(S) + c·(J - I) with a ≤ 3, |b|, |c| ≤ 3 and any S.
- Negative (rayres.py): no 7-node restriction of a D = 13 target, in any switching frame, lies on an extreme ray of
  MET_7 (only 1 of 16, #503). So lift-type families over scaled m_7 vertices cannot work.
- **Positive (cover2.py, cover3.py): 14 of 16 D = 13 targets are glues at one node of (4/13) d(K_{2,3}) on 5 nodes and
  (5/13) d(C_4) on 4 nodes.** The shared node is on the 2-side of K_{2,3}. Because the overlap is one node, the two
  frames combine into one global switching, so no switching enumeration is needed. The other 2 (#503, #508) are covered
  by K_{2,3}-type 5- or 6-node pieces together with C_4 at 4/13, P_4 at 3/13 or 3-node pieces.
- D = 11 (n = 8): 10 of 18 have one-node covers by scaled graph metrics. The common types are K_{2,3} at 4/11 with
  C_4 at 4/11 (6 targets), K_{2,3} at 4/11 with P_4 at 3/11 (6), and a 6-node piece at 4/11 with a 3-node path (5).
  The other 8 (ids 93, 140, 159, 167, 215, 229, 470, 504) have no such cover and are untouched. A sister rule (K_{2,3} at 4/11,
  C_4 at 4/11) is guaranteed to contain every target that has that cover type and the matching overlap side, because a
  vertex of m_8 in the fiber is a fiber vertex. I did not submit it: it is untested, and I was out of budget.

## Compute
About 19 process-minutes, over the ~15-minute budget. That is: exp1.py killed at 280 s (the full scale scan is too
slow), exp2.py 105 s plus a killed second half, try_rule 264 s, cover2 x3, rayres, fam1 and aut about 4 min. All
processes have finished.
