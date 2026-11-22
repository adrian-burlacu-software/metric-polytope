# Round 03 maker notes

## Proposals

| file | kind | reason | try_rule |
|---|---|---|---|
| 01_radial_of_normalized.mpr | move, :grow 1 | Lambda^1 (C5) of the ray normalization 2x/tau(x) (C10) of a reached point | try_rule probe (20 random m_5..m_7 vertices): 20 outputs, 20 feasible, 1 vertex, 0.11 s. try_rule reports no hits_unreached_nodes for moves. My own one-step forward check over the reached nodes timed out twice (230 s and 110 s) and gave no result, so there is NO hit evidence. |

## Analysis (exact; scripts analyze*.py, minimal.py, scale_probe.py, grow1_probe.py in this folder)
- A vertex base piece can only hit unreached nodes at n = 8 (the 266 targets) or n = 9. Every unreached node is a
  restriction of a target. A restriction that is a vertex of m_k with k <= 7 is already reached, because all of
  m_7 is reached. So base families must produce the n = 8/9 targets themselves.
- Up to switching, the 266 unreached n = 8 targets are not of the form f(d_G), where G is the minimum-level graph and
  f is any function (0 hits). They are also not truncated unit graph metrics v*min(c, d_G) (0 hits). 78 of them take
  only the values (2/9){1,2,3} after switching, but their level graphs vary too much to give a small family.
- 21 targets (all D = 9) have 1 or 2 radial nodes. They are Lambda^m of unreached non-vertex points.
- Engine state: only 1,979 nodes are reached (3: 4, 4: 11, 5: 61, 6: 287, 7: 777, 8: 715, 9: 124).
- **Normalization probe (scale_probe.py):** rescale every switching of every reached node to its perimeter facet,
  2y/tau(y). In one step this gives 499 unreached nodes (size 3: 1, 4: 8, 5: 54, 6: 223, 7: 197, 8: 16), including
  10 unreached n = 8 targets. Normalization has :grow 0, which the engine does not accept, so it is folded into
  Lambda^1 in proposal 01. Its gain is unmeasured.
- Rejected attempt: the generative family "normalize switched fiber vertices over vertices of m_{n-1}" gave 0 points
  for n = 4..7. Switching keeps the restriction a vertex, so tau is always 2. It took 220 s at n = 7.

## Compute
About 20 min of process time in total. Two probes ran into their timeout. No background processes were left running.
