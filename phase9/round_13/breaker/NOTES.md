# Round 13 breaker notes

## 1. Structural rules
- **Maker proposals:** `phase9/round_13/maker/` was empty when I worked, so there was nothing to attack.
- **Accepted Phase 9 claims:** `rules/phase9_accepted.mpr` holds only moves (partial-dup, dup-midshift,
  radial-lowend, dup-thirdshift) and generators (gen-bipartite-glue, gen-house-c4-d11, gen-house-p4-d11, and since
  round 12 gen-dyadic-tower-w1 and gen-dyadic-tower-w2). There is no structural claim to falsify.
- **Ledger rules:** unchanged since round 12. The rules that still hold were scanned in round 1 against all Deza m_8
  reps and all n = 9 reps. m_7 and m_8 are complete, so no smaller counterexample exists. I did not try n = 10-11.
- **Result:** no structural break this round.

## 2. Unreachable claims
- **Engine** (`localreach13.py`, a copy of round 12's `localreach12.py`): a scratch `metricpoly.reach.Engine` whose
  targets are my rows only.
  - skip = the current `checkpoints/phase9/reached.json`;
  - base = `load_base()` + graph test + **all 398 `state.json` extra_base keys** (305 at n = 9, 93 at n = 8). The
    n = 8 count went up from 22 to 93 because round 12 added the gen-dyadic-tower-w1/w2 orbits. Their n = 9 output
    is not in state.json because the n = 9 generation did not finish. All my claims are D = 7, so none of them can be
    a D = 8 tower vertex.
  - moves = the 4 accepted moves, applied forward.
- **Positive controls:**
  - row 48312 (reached since round 11);
  - round 12's D = 8 claims 166852 and 200018. Both are **reached** now, which shows that the dyadic orbits are in
    the base. The third D = 8 claim, 71489, is still unreached; I did not resubmit it.
- **Runs:** fresh D = 7 rows from round 7's `pool7.json` that no earlier round had tested or claimed (`pick13.py`).
  The script excludes rows that appear in any `round_*/breaker` json or rows file.

| run | rows | time | not reached (new) |
|---|---|---|---|
| batch13a | 4 controls + 20 | 127 s, no timeout | 17 |
| batch13b | 2 controls + 20 | 137 s, no timeout | 15 |
| batch13c | 2 controls + 14 | 161 s, no timeout | 5 |
| batch13d | 2 controls + 10 | 122 s, no timeout | 8 |

  - All controls came out reached in every run, except 71489, as expected.
  - 45 new rows are certified unreachable.

## 3. Submitted (`build13.py` -> `candidates.json`)
- **40 candidates,** all n = 9, D = 7, kind unreachable, rule all-moves-cover. All are new rows; none was claimed
  in rounds 1-12.
- **Tool check:** `check_point.py chk13_norule.json` -> `check_vertex13.txt`.
  - 40/40 are exact vertices (dim 36) with 40 distinct keys;
  - 0 are unreached nodes, so none was already confirmed by the judge;
  - 0 are targets.
- **Left over:** 5 more certified rows that did not fit under the cap: 31255, 31273, 31274, 31276 and 31314 (all
  D = 7, from batch13d).

## Compute
- About 9.5 min in total: 4 engine runs with 3 workers each, run one at a time, plus a few seconds of check_point.
- The scratch caches were deleted. No process of mine is still running.
