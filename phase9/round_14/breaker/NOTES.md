# Round 14 breaker notes

## 1. Structural rules
- **Maker proposals:** `phase9/round_14/maker/` held scripts, logs and gain_*.json files while I worked, but no
  `.mpr` proposal, so there was no structural claim to attack.
- **Accepted Phase 9 claims:** `rules/phase9_accepted.mpr` is unchanged since round 12. It holds only moves and
  generators, so there is nothing structural to falsify.
- **Ledger rules:** unchanged. Rules that still hold were scanned in round 1 against all m_8 reps and all n = 9 reps.
  m_7 and m_8 are complete, so no smaller counterexample exists. I did not try n = 10-11.
- **Result:** no structural break.

## 2. Unreachable claims (non-dyadic D, as the brief asked)
- **Engine:** `localreach14.py`, an unchanged copy of round 13's `localreach13.py`. It runs a scratch
  `metricpoly.reach.Engine` whose targets are my rows only.
  - skip = the current `checkpoints/phase9/reached.json`;
  - base = `load_base()` + the graph test + all 398 `state.json` extra_base keys;
  - moves = the 4 accepted moves (partial-dup, dup-midshift, radial-lowend, dup-thirdshift).
  - `state.json` has not changed since round 12, so this setup matches the current judge state.
  - Positive controls 48312 (D = 7) and 166852 (D = 8, reachable only through the dyadic towers) came out
    **reached** in every run. No run timed out (deadline 240 s).
- **Batch a** (`pick14.py`; the first fresh pool7 rows at D = 9, 10, 12, 15):
  - 18 of 20 rows were reached, nearly all by a one-step `lift` from an n = 8 vertex. m_8 is now fully reached, so
    any n = 9 vertex with a single-node restriction that is an m_8 vertex is covered at once.
  - Only 2 rows were not reached, both D = 15.
- **Prefilter** (`prefilter14.py`, `pick14b.py`):
  - keep only fresh rows where none of the 9 single-node restrictions is an m_8 vertex (float rank of the tight rows
    < 28);
  - then sort by the maximum restriction rank, lowest first (25 is the best available).
- **Batch b** (24 rows, D = 9, 10, 12, 15):
  - D = 9: 0/6 not reached;
  - D = 12: 0/6 not reached (reached at depth 2);
  - D = 10: 3/6 not reached;
  - D = 15: 5/6 not reached.
- **Batch c** (26 rows, D = 10 and D = 15 only): 11/13 not reached at D = 10, 8/13 not reached at D = 15.
- **Total:** 29 new rows certified not reachable (14 at D = 10, 15 at D = 15).
- **Pattern:** D = 9 and D = 12 rows are almost all reachable now, depth 1-2 from lifts. D = 10 and D = 15 rows with
  low restriction rank are mostly not reachable.

## 3. Submitted (`build14.py` -> `candidates.json`)
- **29 candidates,** all n = 9, kind unreachable, rule all-moves-cover: 14 at D = 10 and 15 at D = 15.
  - All are fresh rows: none was tested or claimed in rounds 1-13, and none is a judge target.
  - None has D = 8 or 16, so none can be an n = 9 dyadic-tower vertex that is missing from state.json.
- **Tool check:** `check_point.py chk14_norule.json` -> `check_vertex14.txt`.
  - 29/29 are exact vertices (dim 36) with 29 distinct keys;
  - 0 are unreached nodes; 0 are targets.

## Compute
- About 10.5 min in total: 3 engine runs with 3 workers each (about 196 s, 210 s and 193 s), run one at a time,
  plus a few seconds each for the prefilter and check_point.
- The scratch caches were deleted. No process of mine is still running.
