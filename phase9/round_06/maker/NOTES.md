# Round 06 maker notes

## Proposals

| file | kind | reason | outputs/input (timing6.py, G-mode apply_move) | try_rule (20 probes) | sim3.py gain (backward cascade, glue ignored = lower bound, start = current reached incl. partial-dup) |
|---|---|---|---|---|---|
| 02_dup_midshift.mpr | move, :grow 1, G-equivariant | dup column of i (copy at delta_i), then ONE other entry j moved to the midpoint of its feasible triangle interval [L_j, U_j]: a fiber-edge direction off the dup vertex that partial-dup does not use | n(n-1): n=5: 20, 6: 30, 7: 42, 8: 56; 0.02-0.06 s | 592 outputs, all feasible, 340 vertices, 0.9 s | **68 targets: n=8: 32 (D10: 32); n=9: 36 (D7: 5, D10: 28, D12: 3)**; +826 nodes; saturated in 11 s |
| 01_dup_recentre.mpr | move, :grow 1, G-equivariant | general form of 02: partial-dup column (t in {1/4,1/3,1/2,2/3,3/4,1}) then one other entry j at s in {1/4,1/3,1/2,2/3,3/4} of [L_j, U_j] | 30 n(n-1): n=5: 600, 6: 900, 7: 1260, 8: 1680; 0.35 / 0.59 / 0.93 / 1.37 s | 17760 outputs, all feasible, 6450 vertices, 24 s | **97 targets: n=8: 35 (D10: 32, D12: 3); n=9: 62 (D7: 5, D9: 5, D10: 30, D12: 12, D15: 2, D18: 6, D27: 2)**; +3193 nodes; saturated in 46 s. Beyond 02: +29 targets (n=8: +3, n=9: +26), mostly D = 9, 12, 15, 18. COST RISK: ~1.4 s per size-8 input |

try_rule reports no hits_unreached_nodes for moves; hit evidence is from sim3.py (exact Fractions, round-5 sim2 with per-(n, D) breakdown).

## Negative results (exact, sim3.py)
- **Pushing the partial-dup q cap does not help.** sim with q <= 6 (sanity): 0 new (judge state is saturated). q <= 12 (45 fractions):
  +125 nodes, **2 targets** (n=9, D=21). q <= 16 (79 fractions): identical, 2 targets. So I do NOT propose a larger-q partial-dup.
- Two re-centred entries (dup, then j and k at midpoints, n(n-1)(n-2) outputs): 15 targets alone, +2 on top of 02. Not proposed.
- s in {1/4..3/4} with t = 1 only: 73 targets (+5 over 02). Not proposed.

## Analysis
- Current frontier (unreached nodes with a reached one-node deletion): 6234 nodes (sizes 4: 314, 5: 1081, 6: 2569, 7: 1939, 8: 331).
  No frontier node has D = 11, 13, 16. Only 94 of the 327 unreached targets with D in {8, 10, 14, 16} contain any frontier node.
- **Denominators 11 and 13 at n = 8 are blocked structurally.** m_7 has vertex denominators {1, 3, 4, 5, 6, 7} only; no reached node
  has 11 or 13 in its denominator. In a D = 11 (or 13) target every entry is a/11 with a in 0..11, so every restriction that carries
  any entry other than 0 or 1 has 11 in its denominator, and no such restriction of size <= 7 can be a vertex. By the denominator
  lemma, the 18 D=11 and 16 D=13 orbits of m_8 are reachable only (a) as base pieces themselves (a vertex family containing them), or
  (b) through a move that introduces the prime 11/13 by arithmetic (the q <= 16 sim shows partial-dup with such t does not).
  n = 9 D = 11/13 targets likewise need an 11/13 vertex of m_8 (or themselves) as base. I found no general vertex family for them
  in the time budget. Observed: 14/18 of the m_8 D=11 orbits have non-redundant edge weights {2,3,4}/11, and 14/16 of the D=13
  orbits have {3,4,5}/13 (weights.py); a weighted-graph-metric family might be the route, but it needs a generator that is
  feasible for every n.
- D = 8 and 16 gained nothing from any variant tested.

## Compute
About 9 process-minutes: frontier/classification scripts (~2 min), 10 sims (3-46 s each, max 4 in parallel), timing x2,
try_rule x2. All my processes have finished; the running gen6.py processes belong to the breaker.
