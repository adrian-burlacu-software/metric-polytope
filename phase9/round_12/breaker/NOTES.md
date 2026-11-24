# Round 12 breaker notes

## 1. Structural rules
- **Maker proposals:** `phase9/round_12/maker/` was empty when I worked, so there was nothing to attack.
- **Accepted Phase 9 claims:** `rules/phase9_accepted.mpr` holds only moves (partial-dup, dup-midshift,
  radial-lowend, dup-thirdshift) and generators (gen-bipartite-glue, gen-house-c4-d11, gen-house-p4-d11). There is
  no structural claim to falsify. Generator outputs are filtered by `(vertex? z)`.
- **Ledger rules:** rules that still hold were checked in round 1 against all Deza m_8 orbit reps and all 1,056,367
  n = 9 reps. Only at-least-two-cuts broke, and it is already reported. No smaller counterexample is possible:
  m_7 and m_8 are complete and were scanned.
- **Result:** no structural break this round.

## 2. Unreachable claims
- **Engine** (`localreach12.py`, a copy of round 11's `localreach11.py`): a scratch `metricpoly.reach.Engine` whose
  targets are my rows only.
  - skip = the current `checkpoints/phase9/reached.json`;
  - base = `load_base()` + graph test + **all 327 `state.json` extra_base keys** (305 at n = 9, 22 at n = 8). These
    include round 11's gen-house-c4-d11 and gen-house-p4-d11 orbits.
  - moves = the 4 accepted moves, applied forward.
- **Runs:**

| run | rows | result | used for claims |
|---|---|---|---|
| batch12a | round 11's 40 claims | all unreached, 20 s | no (no positive control) |
| batch12b | 3 controls + 40 fresh pool7 rows (D = 6, 7) | **timed out** (info True); controls came out *unreached* | no |
| batch12c | 3 controls + the 4 untested rows from batch12b's not-reached ones + round 11's 40 | no timeout (98 s); all 3 controls reached | yes |
| batch12d | 1 control + 25 fresh D = 7 pool7 rows | no timeout (157 s); control reached | yes |

- **batch12b:** a timed-out run again gave false "unreached" results. Its 3 controls (rows 48312, 45750 and 166426,
  reached in round 11) came out unreached. Of its 40 fresh rows:
  - D = 6: 34/35 were reached. All of these were reached rows, which a timeout cannot make false, so they count as
    reached.
  - **Not reached (uncertified):** 48125 (D = 6), and 1809, 7361 and 7383 (all D = 7). These were rerun in batch12c.
- **Round 11's 40 claims re-checked with the house families:** all 40 are **still unreachable** (batch12c,
  certified). `check_point.py` now reports them as `unreached_node: true`, so the judge already records them.
- **New certified unreachable rows:**
  - batch12c: 48125 (D = 6), 1809, 7361 and 7383 (all D = 7);
  - batch12d: 21 of 25 D = 7 rows. Reached there: 20862, 45717, 50774 and 50933.

## 3. Submitted (`build12.py` -> `candidates.json`)
- **40 candidates,** all n = 9, kind unreachable:
  - **25 new:** D = 6: 1, D = 7: 24;
  - **15 round 11 claims re-confirmed** (smallest D first: D = 7: 12, D = 8: 3). These fill the remaining slots and
    may add nothing, because the judge already holds them as unreached nodes.
- **Tool check:** `check_point.py chk12_norule.json` -> `check_vertex12.txt`.
  - 40/40 are exact vertices (full rank 36) with 40 distinct keys;
  - none is a judge target;
  - the 25 new ones are not unreached nodes either.

## Compute
About 11 min in total:
- engine runs: 20 s, 247 s, 98 s and 157 s, with 3 workers, one run at a time;
- check_point runs: a few seconds.

Scratch caches were deleted. No process of mine is still running.
