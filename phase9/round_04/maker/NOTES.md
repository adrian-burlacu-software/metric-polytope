# Round 04 maker notes

## Proposals

| file | kind | reason | evidence |
|---|---|---|---|
| 01_fiber_midpoints.mpr | move, :grow 1 | new column = (a+b)/2 for two vertices a, b of the lift fiber over x | try_rule (20 probes on m_5..m_7 vertices): 3745 outputs, all feasible, 0 vertices, 4.9 s. Cascade simulation (simulate.py mid): +8720 nodes, **234 unreached targets**, saturated (5 rounds, 213 s) |
| 02_fiber_thirds.mpr | move, :grow 1 | new column = (2a+b)/3 for ordered pairs of fiber vertices | try_rule: 7490 outputs, all feasible, 0 vertices, 14.3 s. Simulation (third): +5340 nodes, **232 targets**, saturated |
| 03_twin_fiber_midpoints.mpr | move, :grow 1 | cheaper subset of 01: midpoint of a twin/antitwin column of node i and any fiber vertex (2n·|V| outputs, not |V|²/2) | try_rule: 3596 outputs, all feasible, 238 vertices, 4.1 s. **No hit simulation** (compute budget spent) |

All three moves build only the new column, so x stays the restriction to the first n nodes (restriction-preserving
also on non-vertex inputs). Twin/antitwin columns and fiber vertices are G-equivariant constructions.

## Analysis (exact; frontier.py, edges.py, simulate.py)
- Frontier = unreached nodes with a reached one-node deletion: 2429 (sizes 4: 331, 5: 606, 6: 865, 7: 523, 8: 104).
  No unreached target is on it directly.
- Face of the lift fiber that contains the new column: dimension 1 (an edge) in 864 cases. On those edges the
  position is t = 1/2 in about 580 cases, then 1/3 (about 160) and 1/4 (about 95). Constant columns (radial with
  another radius) and "copy node i with a changed entry" are rare.
- simulate.py: a backward test of the move (is c = (a+b)/2, or (2a+b)/3, for some fiber vertices of y = u - v, with y
  reached) plus the engine's cached lift and radial predecessor lists, iterated to a fixpoint. Glue is ignored, so
  these are lower bounds for the cascade. Combined mid+third+quarter, cut at 240 s: 444 targets (not saturated).
- I did not split the target counts by n (8 vs 9).

## Cost risk (important)
Fiber vertex counts |V| for reached inputs: size 6: 46-276; size 7: 120-682; size 8: 134-2288 (timing.py, 5 samples
each). 01 then makes up to about 2.6M outputs for one size-8 input, and 02 twice that. In the judge's 300 s forward
budget, 01 and 02 will likely not finish the size-7/8 inputs. The engine processes the smallest inputs first, so
part of the gain may still land, but this is unmeasured. 03 is the hedge (about 37k outputs at |V| = 2288), but its
hit count is unknown.

## Compute
About 24 process-minutes, slightly over the ~20 min target: 3 parallel 4-min simulations, try_rule x3, small scripts.
One endpoint-classification script hit its timeout and gave no result (deleted). No processes of mine are left running.
The Python process still running (final.py, PID 27696/28272) is the breaker's, not mine.
