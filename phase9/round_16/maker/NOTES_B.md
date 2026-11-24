# Round 16 maker notes, track B (a move that brings in the prime 5 or 7)

## Proposals

| file | kind | reason | try_rule (20 probes, --ns 3-9) | cost (timing.py, G-mode, sec per input of size 5/6/7/8; outputs per input) | sim gain (sim4.py, on top of all accepted moves) |
|---|---|---|---|---|---|
| B01_twin_dup_fifths.mpr | move, :grow 1, mode G | new column = (1-t) twin_i + t {dup_j or antidup_j}, all i, j, t in {1/5, 2/5, 3/5, 4/5} | 5688 outputs, 5688 feasible, 372 vertices, 5.3 s. hits_unreached_nodes: not reported for moves | 0.06 / 0.11 / 0.11 / 0.27; 200 / 288 / 392 / 512 (two timings ran in parallel: noisy) | **21 targets, all n = 9, D = 15**; +845 sub-orbits (n=4..9: 6/56/245/336/173/29) |
| B02_twin_dup_sevenths.mpr | move, :grow 1, mode G | same columns at t = k/7, k = 1..6 | 8532 outputs, 8532 feasible, 558 vertices, 8.6 s. hits_unreached_nodes: not reported for moves | 0.06 / 0.12 / 0.27 / 0.49 (parallel, noisy; the fifths+sevenths move run alone was 0.44 at n = 8, so sevenths alone is probably about 0.27); 300 / 432 / 588 / 768 | **6 targets, all n = 9, D = 21**; +200 sub-orbits |

The two gains are disjoint (by D). Together in one sim (dp57): 27 targets (D = 15: 21, D = 21: 6), +1,048 sub-orbits.
n = 8 gain: 0 (no partly reached m_8 target is left). Sim numbers are lower bounds (glue ignored; sim tests the
target column in the target's frame and its complement).

## Evidence
- front.py: the 38 partly reached n = 9 targets with D = 15 / 21. 29 of them (D = 15: 19, D = 21: 10) have no reached
  restriction carrying 5 or 7; the other 9 (D = 15, largest reached restriction 5-7 nodes) already have one with 5.
  345 distinct frontier pairs (Y reached, Z = Y + v unreached) where Z carries the prime; 65 start from a 3-node
  thirds triangle (D = 3) and go to a 4-node Z with D = 15 or 21.
- face5.py (round 14's face.py, extended to dim 3 and to barycentric weights; log face5_intro.log): for pairs where
  Y has no 5 / 7, the new column sits on a fiber face at weights that are fifths / sevenths. Edges dominate the
  3-node frontier: twin--antidup at 1/5 (26 targets touch it), twin--twin at 2/5, antidup--twin at 1/7, 2/7, 3/7;
  2-faces with weights (1/5,1/5,3/5), (1/5,2/5,2/5), (1/7,2/7,4/7), ... and some 3/4-dim faces.
- Note: partial-dup already uses t = p/5 on the twin--dup edge (same node), so 5 was not strictly absent from the
  move set; what was missing is the twin_i--(anti)dup_j edge at fifths/sevenths with i != j.
- sim4.py (round 14's, output path changed) with the accepted twin-dup-blend / twin-dup-third added to the
  background (run "base": 0 targets, 1 sub-orbit, so the sim state agrees with reached.json):
  - dp57 = tw-dp + tw-ad at fifths and sevenths: 27 targets (D = 15: 21, D = 21: 6)
  - dp5 = fifths only: 21 (all D = 15); dp7 = sevenths only: 6 (all D = 21)
  - all57 = dp57 + tw-tw + tw-an at fifths and sevenths: 34 (D = 15: 27, D = 21: 7), timed out at 240 s (lower bound)
  - dptw5 = dp5 + tw-tw + tw-an at fifths: 27 (all D = 15), timed out at 180 s (lower bound)
- So twin--twin / twin--anti blends at fifths add at least 6 D = 15 targets on top of B01 (and 1 D = 21 with
  sevenths). Not proposed (limit of 2 proposals); a candidate for the next round, ~8 n^2 outputs per input.
- I did not run verify_move.py; the DSL builds the same columns as the sim generator (same template as the accepted
  twin-dup-blend, only the t list differs).

## Negative results
- Of the 38 targets, at least 4 (D = 15: 1, D = 21: 3, lower bound) are not gained by any of these blends; their
  prime-introducing frontier columns sit on 3- or 4-dimensional fiber faces.
- Cost: one move with all ten t values costs 0.44 s per 8-node input (above the 0.3 s target), hence the split.

## Compute
7 sim runs (58 to 240 s each, at most 3 in parallel), 3 timing runs, 2 try_rule runs, analysis under 30 s each:
about 19 process-minutes. All processes finished. Files in B_work/: front.py, face5.py, facelib.py, sim4.py,
timing.py, template_twin_dup_T.mpr, fp.json, gain_*.json, sim_*.log, timing_*.log, try_*.log.
