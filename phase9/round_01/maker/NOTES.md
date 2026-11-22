# Round 01 maker notes

## Proposals

| file | kind | reason | try_rule (--ns 3-7) hits_unreached_nodes / hits_unreached_targets |
|---|---|---|---|
| 01_scaled_graph_metrics.mpr | generative, domain (3 7) | d_G/k for connected G with tau(G) < 2k <= 4n: non-graphic points with odd denominators k (5, 9, 11, 13) | n3: 7/0 (9 pts); n4: 19/0 (35); n5: 28/0 (156 pts, 151 orbits); n6: 27/0 (1011 pts, 985 orbits); n7: 4/0 (9193 pts, 9060 orbits, 9.7 s) |

All generated points are feasible and none is a vertex. n = 8, 9 were not run: `graphs` stops at n = 8, and the n = 8
generation (11,117 graphs) would probably not fit the judge's half-budget of 150 s. Hits are on unreached sub-orbits
only. No target is hit directly, so the judge's propagation decides whether any target is gained. This is unverified.

## Analysis (exact, from engine.pkl + unreached_nodes.json; n = 8, 266 unreached targets)
- Minimal restrictions that carry each odd prime power of den(x) are triangles. For q = 5, 7, 9, 11, 13 these
  triangles are already reached in every target (as non-vertex points). The obstruction is therefore a missing larger
  carrier, not a missing triangle. For q = 3, 20 targets have some reached minimal carrier, but two triangle orbits with
  den 3 are unreached.
- Counts per q: 5: 53, 7: 7, 9: 104, 11: 18, 13: 16 targets.

## Caveats
- The judge accepts any FEASIBLE point as a base piece (phase9_round.py keeps `feasible`, not `vertex`). This proposal
  adds non-vertex points. Whether such base pieces fit the intended notion of reachability is for the user to decide.
- Only one proposal was made. Two earlier analysis runs were lost: an infinite loop in my prime-factor helper on even
  D, about 7 minutes of wasted compute. That left no budget for more candidates within the ~15 min limit.
