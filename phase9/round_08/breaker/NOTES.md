# Round 08 breaker notes

## 1. Structural rules
- Maker round 8: no `*.mpr` in `phase9/round_08/maker/` at any point while I worked (only analysis scripts), so there
  was nothing structural to attack. `rules/phase9_accepted.mpr` still holds only moves.
- Ledger rules: unchanged since round 7 (all open-domain rules held on all 1,056,367 Deza n = 9 reps in round 1). I
  did not rescan them. **Nothing new is broken.**

## 2. n = 9, small denominators (`localreach8.py`, a copy of round 7's `localreach7.py`)
I used a scratch `metricpoly.reach.Engine` with my rows as its only targets. Its skip set is the current
`checkpoints/phase9/reached.json`. The user moves come from `state.json`, which now holds all three:
partial-dup, dup-midshift and radial-lowend.
- **Validation:** with MAXSKIP = 7 (so the 8- and 9-node pieces had to be re-derived), the 3 round-7 rows that
  radial-lowend made reachable (52211 D=7, 312449 D=10, 224960 D=10) came out reached again (`valid8.json`).
- **Sample:** 84 design-A depth_detour = None rows that are neither judge targets nor tested or claimed in rounds 1–7
  (`rows8a.txt`, seed 8). Results are in `batch8a.json` and `batch8b.json` (about 3.5 min each, no timeout).

Rows still unreached, by denominator:

| D | unreached | note |
|---|---|---|
| 6 | 0/20 | D = 6 is covered |
| 7 | 16/26 | radial-lowend took only a few; D = 7 is the thinnest small denominator |
| 9 | 0/8 | still covered |
| 10 | 6/16 | |
| 12 | 4/16 | |

## 3. n = 10, cheap extensions of round-7 CONFIRMED unreachable n = 9 vertices (`gen8.py`)
- **Constructions:**
  - the twin, a zero-copy of node i. This is the trivial extension and an exact vertex;
  - outputs of the accepted moves on the seed that are exact vertices.
- **Dedupe:** by canon_large key against `results/phase9/large_orbits.json`.
- **Test:** `reach_large.reachable_bu` with all 3 accepted moves, which is the judge's n <= 12 search, with a budget
  of 18 s or 15 s.
- **Twins** (`gen8_a/b`): D=7 8/8 False, D=10 4/4 False, D=11 4/4 False, D=12 7/10 False (3 undecided).
  - The D=8 seeds behave differently: for seeds 97190 and 50048, one twin each is **reachable** (True) and the other
    is undecided.
  - So a trivial extension of an unreachable n = 9 vertex can be reachable. Reachability is not inherited upward
    through the twin; presumably a glue of twin pieces avoids the unreachable restriction.
- **dup-midshift outputs** (`gen8_c/d`): D=7 6/8 False, D=10 2/3 False (1 undecided), D=11 4/4 False.
  - Both tested outputs of one D=7 seed are **reachable**.

## 4. Submitted (`build8.py` -> `candidates.json`, 40 candidates)
- **n = 9:** 22 candidates (D = 7: 12, D = 10: 6, D = 12: 4), all Deza reps, locally unreached with all 3 moves.
- **n = 10:** 18 candidates. They are 6 twins (D = 7) and 12 dup-midshift extensions (D = 7: 6, D = 10: 2,
  D = 11: 4). All have reachable_bu = False.
- **Tool check:** `check_point.py chk8_norule.json` -> `check_vertex8.txt`.
  - 40/40 are exact vertices.
  - The 22 n = 9 points have 22 distinct keys, and none of them is a current target or unreached node.
  - The n = 9 keys were also checked against every n = 9 claim from rounds 1–7.

## Compute
About 16 min in total: 2 × 3.6 min engine runs, 47 s validation, about 4.8 min plus 3.3 min of reachable_bu with 2
processes. Each command used at most 4 processes. The scratch engine caches were deleted.
