# Round 11 breaker notes

## 1. Round 10's family gen-bipartite-glue
- **Are its outputs vertices?** The 14 n = 8 orbits it added (`checkpoints/phase9/state.json` extra_base, read only)
  were checked with `check_point.py` (`extra_base_chk.json` -> `extra_base_check.txt`). All 14 are exact vertices
  (29 tight, rank 28, D = 13). They are Deza orbits 383, 385, 406, 407, 497, 498, 512–515, 517, 519, 522 and 524.
  The rule's non-vertex fiber points are filtered by the judge, so they are not counterexamples.
- **Do they violate a ledger rule?** No, and none can. Every open-domain structural rule in `rules.md` was verified on
  all Deza m_8 orbit reps, and these 14 are Deza m_8 reps. The n = 9 targets they reach are Deza n = 9 reps, and
  round 1 scanned all 1,056,367 of those against every open-domain rule; only at-least-two-cuts broke, and it is
  already reported.
- **n = 9 output of the rule:** not enumerated here. The judge could not generate it in 900 s, which is well over my
  budget.

## 2. Maker round 11 proposals
Files: `01_bipartite_glue_2stage`, `02_bipartite_c4_d11` (later renamed `02_house_c4_d11`), `03_bipartite_p4_d11`
(later `03_house_p4_d11`). All three are **generative** rules, each ending in `(where (vertex? z))`.
- There is no structural claim to falsify, and none of them can output a non-vertex.
- Any n <= 8 output is an m_8 vertex (m_8 is complete), so no new structural break can come from them in scope.
- **Nothing to break.**

## 3. Unreachable claims (`localreach11.py`, copy of round 8's `localreach8.py`)
- **Engine:** a scratch `metricpoly.reach.Engine` whose only targets are my rows.
  - skip = the current `checkpoints/phase9/reached.json`;
  - base = `load_base()` + the graph test + **state.json extra_base** (the gen-bipartite-glue orbits);
  - user moves = all 4 accepted moves from state.json (partial-dup, dup-midshift, radial-lowend, dup-thirdshift),
    applied forward as in the judge.
- **Row pool:** round 7's `pool7.json` (design-A depth_detour = None rows that are not judge targets). Rows claimed
  in rounds 1–10 and rows tested in rounds 7–8 were excluded.
- **Runs:** batch11a, batch11b and batch11c.
  - **batch11b hit the 240 s deadline** (`run info True`), so its "not reached" results were not certified.
  - Its 17 not-reached rows were rerun as batch11c, which finished in 90 s with no timeout. 3 of those 17 then came
    out *reached* (D = 7 rows 48312 and 45750, D = 8 row 166426). **A timed-out run gives false "unreached" results.**
  - Only batch11a and batch11c (both without timeout) are used for the claims.

| D | tested | unreached (certified) | note |
|---|---|---|---|
| 6 | 6 | 0 | still covered |
| 7 | 26 | 12 | |
| 8 | 6 | 5 | |
| 10 | 10 | 3 | |
| 13 | 30 | 28 | the new base pieces reach only 2/30 D = 13 non-target rows (675583 and 784703) |

## 4. Submitted (`build11.py` -> `candidates.json`, 40 candidates, all n = 9, kind unreachable)
- **By denominator:** D = 7: 12, D = 8: 5, D = 10: 3, D = 13: 20. Smallest D was taken first; D = 13 was capped at 20.
- **Tool check:** `check_point.py chk11_norule.json` -> `check_vertex11.txt`.
  - 40/40 are exact vertices with 40 distinct keys.
  - None of them is a current target or unreached node.
  - None of the keys equals the key of an n = 9 claim from rounds 1–10.

## Compute
About 9.5 min in total:
- engine runs: 150 s, 249 s and 90 s, with 3 workers each, one run at a time;
- check_point runs: about 1 min.

Scratch engine caches were deleted. No process of mine is still running.
