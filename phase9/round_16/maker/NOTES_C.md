# Round 16 maker notes, track C (2-faces of the one-node fiber)

## Proposal

| file | kind | reason | try_rule (20 probes, --ns 3-9) | cost (timing.py, G mode, sec per input n = 5/6/7/8; outputs per input) | simulated gain (simC.py, on top of all six accepted moves) |
|---|---|---|---|---|---|
| C01_twin_dup_fifth.mpr | move, :grow 1, G-equivariant (mode G) | new column = (1-t) twin_i + t {dup_j or antidup_j}, all i, j, t in {1/5, 2/5, 3/5, 4/5}: an **edge** rule, not a 2-face rule (see below) | 5688 outputs, 5688 feasible, 372 vertices, 5.4 s; hits_unreached_nodes not reported for moves | 0.04 / 0.09 / 0.22 / 0.32 (run next to a sim, so noisy); 200 / 288 / 392 / 512 | **21 targets: n = 8: 0, n = 9: 21 (all D = 15)**; +845 sub-orbits |

Overlap warning: this move brings in the prime 5, which is track B's topic. Of the 21 targets, 10 already have a reached
restriction carrying 5 (my track's group) and 11 need the 5 brought in. If track B submits the same fifths blend, the
two are duplicates and only one can gain.

## What I found (track C question: is there a cheap 2-face rule?)
- Group C now (front_c.py, current reached.json): 47 partly reached n = 9 targets. 30 of them have an odd prime (5 or 7)
  in D that no reached restriction carries. That leaves 17: D = 15 (9), 18 (3), 24 (3), 27 (2). No n = 8 target is
  partly reached.
- Frontier pairs of the 17 (tri_c.py, tri2.py; 361 pairs, Y reached, Z = Y + v unreached): 40 columns lie on a
  segment of special columns (twin, anti, dup, antidup, the constant 1/2 column), 120 only in a triangle, 201 in
  neither. Every one of the 17 targets has a frontier column on a triangle. **The D = 15 ones also have frontier
  columns on segments at fifths**: (3/5 antidup_i + 2/5 twin_i), (4/5 antidup_i + 1/5 twin_j), and others. The edge
  move at fifths is therefore enough for them, and no 2-face is needed (C01).
- The 2,3-denominator targets (D = 18, 24, 27) have segment columns only at 1/6, 3/8, 5/8, 1/8, 1/9, 2/9, 4/9:
  t-values the accepted moves lack. But the sim with all of those t added (S1: t in fifths, sixths, eighths and
  ninths) gained **no** target beyond the 21 D = 15 ones. So the edge columns at those t do not finish a chain.
- Full centroid of 3 special columns (round 14's O(n^3) `cen`), rerun against today's state: **2 targets** (n = 9,
  D = 12 and 18). In round 14 it gained 19, but twin-dup-third and twin-dup-blend have since taken almost all of them.
  So even the expensive 2-face rule is now worth 2 targets.
- Structured O(n^2) 2-face rule: triangle {twin_i, dup_i or antidup_i, twin_j or anti_j}, eight weight shapes in
  every permutation, with 2,3-weights only (S5). About 12k columns per 8-node input. In the sim, its first round adds
  291 sub-orbits, but the 250 s limit stopped it before any target was counted. **Inconclusive**, and far too
  expensive for the 0.3 s per input budget in any case. Not proposed.
- Negative result: on today's state, the 2-face direction is worth at most about 2 n = 9 targets (the centroid upper
  bound for special-column triangles). The 9 targets with denominators built from 2 and 3 are not reached by any
  special-column 2-face or edge blend I tried. Their frontier columns are mostly in no triangle of special columns
  (201 of 361 pairs).

## Sim details
simC.py is round 14's sim4.py, with the background extended by twin-dup-third and twin-dup-blend (tw-dp and tw-ad at
{1/4, 1/3, 1/2, 2/3, 3/4}). Glue is ignored, so the gains are lower bounds.
- S1: tw-ad and tw-dp at 16 values of t: 21 targets.
- S6: tw-ad and tw-dp at fifths only: the same 21 targets, 845 sub-orbits.
- S3: cen: 2 targets.
- S5: triangle: timed out.
- Two runs (S2 and S5, first attempt) crashed on a weight-parsing bug and their logs were deleted. S2 (the triangle
  with fifths) was never rerun, because of the budget.

## Compute
6 sim runs (about 2.5 to 4.5 min each, at most 3 in parallel, 2 of them crashed after about 2 min), 1 timing run, 1
try_rule run, analysis under 1 min each. About 22 process-minutes in total: at the limit. All processes have finished.
