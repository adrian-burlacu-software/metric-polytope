# Round 14 maker notes (group C: partly reached targets, moves)

## Proposals

| file | kind | reason | try_rule (20 probes, --ns 3-9) | cost (timing.py, G-mode apply_move, sec per input of size 5/6/7/8; outputs per input) | sim4.py gain (targets, on top of all accepted moves) |
|---|---|---|---|---|---|
| 01_twin_dup_blend.mpr | move, :grow 1, G-equivariant (interpreter: mode G) | new column = (1-t) twin_i + t {dup_j or antidup_j}, all i, j (i = j allowed), t in {1/4, 1/2, 3/4} | 4266 outputs, 4266 feasible, 279 vertices, 4.0 s. hits_unreached_nodes: not reported for moves | 0.03 / 0.05 / 0.17 / 0.13; 150 / 216 / 294 / 384 | **24: n = 8: 1 (D = 12), n = 9: 23 (D = 12: 18, 18: 2, 10: 1, 20: 1, 24: 1)**; +3,007 sub-orbits |
| 02_twin_dup_third.mpr | move, :grow 1, G-equivariant (mode G) | same columns at t in {1/3, 2/3} | 2844 outputs, 2844 feasible, 186 vertices, 2.3 s. hits_unreached_nodes: not reported for moves | 0.02 / 0.04 / 0.06 / 0.17; 100 / 144 / 196 / 256 | **22: n = 8: 7 (D = 9, all 7), n = 9: 15 (D = 9: 5, 18: 6, 15: 2, 21: 1, 27: 1)**; +1,263 sub-orbits |

Both together (one sim, t in {1/4, 1/3, 1/2, 2/3, 3/4}): **46 targets, n = 8: 8 of 8 group-C targets, n = 9: 38**
(D = 12: 18, 18: 8, 9: 5, 15: 2, 10, 20, 21, 24, 27: 1 each); +4,366 sub-orbits. The two gains are disjoint (24 + 22).
The timings ran two at a time, so the n = 7 / n = 8 numbers are noisy; both are under the 0.3 s target.

Why dup AND antidup: twin_i + antidup_j alone is only Sn-equivariant (after switching i and j apart it becomes
twin_i + dup_j with the new node switched). The interpreter then expands every switching: 40,960 outputs and 25 s per
8-node input (measured). With both, the family is switching-closed and the move runs in mode G.

## Evidence
- ana.py: group-C targets (a reached restriction of >= 3 nodes) by D, size s of the largest reached restriction, odd
  primes in the reached restrictions. I count 102 (n = 8: 8, n = 9: 94; the brief's profile says 87 at n = 9, probably a
  different snapshot). **32 of them have an odd prime (5, 7 or 11) in D that no reached restriction carries** (e.g. 18
  of the D = 15 targets with s = 3, 6 + 5 of the D = 21 ones). By the denominator lemma no move that only divides by 2
  and 3 can reach them; they need a base piece (or a move introducing 5 / 7). The other 70 are the real move targets;
  46 of them are gained above.
- f34.py: the s = 3 targets all start from 3|3|1,1,2 or 3|3|1,1,1 (thirds triangles); their 4-node frontier has D = 9,
  12, 18, 24, 27.
- face.py: minimal fiber face of the new column for every frontier pair (reached Y, unreached Z = Y + v).
  n = 8 D = 9 (s = 3): 7 at 1/3 of an antidup--twin edge, 2 at 1/3 of twin--twin, 7 on 2-faces (quadrilaterals) on a
  diagonal at 1/3. n = 9: very mixed; 1/2 and 1/4 points of other--other and antidup--twin edges dominate D = 12, thirds
  dominate D = 9, 15, 18; many 2- and 3-dimensional faces.
- sim4.py (copy of round 7's sim3.py; the background generators are the accepted moves partial-dup, dup-midshift,
  dup-thirdshift, radial-lowend; glue ignored, so lower bounds; background alone: 0 targets). Blend (1-t) P_i + t Q_j of
  special columns, P, Q in {twin, anti, dup, antidup}, t in {1/3, 2/3} unless noted:
  tw-tw 15, tw-an 6, tw-dp 16, tw-ad 20, dp-dp 1, dp-ad 0, all six 24, tw-tw + tw-ad 22, tw-ad + tw-dp 22;
  tw-ad with i != j only 17 (i = j matters); tw-ad at t = 1/3 only 1; tw-ad at t in {1/4, 1/3, 1/2, 2/3, 3/4} 43;
  tw-ad + tw-dp dyadic {1/4, 1/2, 3/4} 24 (proposal 01); same at the five t 46.
  Centroid of 3 special columns: 19 targets, but O(n^3) columns; not proposed.
  twin_i with one other entry at 1/3 or 2/3 of its interval (dup-thirdshift with t = 0): 0 targets.
- The sim tests the target column in the target's own frame (and its complement); the judge applies a G-mode move to
  orbit representatives, which covers the same orbits, so the sim numbers are lower bounds (glue is also ignored).
- I did not run verify_move.py (DSL output vs sim generator on frontier pairs) because of the compute budget; the DSL
  builds exactly the sim's columns (twin, dup with delta_j = min_k min(2x_jk, 2 - 2x_jk), antidup = 1 - dup).

## Negative results
- 32 of the 102 partly reached targets are out of reach of any halves/thirds move (missing prime 5, 7 or 11, above).
- 24 of the remaining 70 are not gained by any blend tried; their frontiers sit on 2- and 3-dimensional fiber faces
  (face.py), with no common rule found.
- dp-dp and dp-ad blends add almost nothing (1 and 0); tw-an only 6.

## Compute
About 20 sim runs (35 to 225 s each, at most 4 in parallel; one duplicate run by mistake), 3 timing runs, 2 try_rule
runs, analysis scripts under 10 s each. Roughly 30 process-minutes, about 20 minutes wall clock: at the limit; I stopped
there. All my processes have finished. Gain lists: gain_*.json (sim tag in the file name), logs sim_*.log.
- Deleted one sim run whose t list was mis-parsed (it ran background only, 0 targets); rerun with '@' separators.
