# Phase 9 round 14

Main-track numbers only. Non-vertex variant proposals are marked VARIANT and are tracked in results/phase9/variant_nonvertex.json.

Judge time 1800.6 s; budget per rule 300 s (one retry at 900 s for rules still gaining); round cap 1800 s.

## Proposals (rule maker)

| file | name | kind | status | targets gained (n: count) | s |
|---|---|---|---|---|---|
| phase9/round_14/maker/02_twin_dup_third.mpr | twin-dup-third | move | dropped: no gain within budget | {} | 301.2 |
| phase9/round_14/maker/01_twin_dup_blend.mpr | twin-dup-blend | move | dropped: no gain within budget | {} | 300.7 |
| phase9/round_14/maker/02_twin_dup_third.mpr | twin-dup-third | move | ACCEPTED | {8: 7, 9: 18} | 472.3 |
| phase9/round_14/maker/01_twin_dup_blend.mpr |  |  | retry deferred: not enough time left in the round cap |  |  |

## Coverage of rules with gains (per size and denominator)

| rule | status | n | gained | share of unreached | denominators (D: count) | verdict |
|---|---|---|---|---|---|---|
| twin-dup-third | ACCEPTED | 8 | 7 | 23.3% | {9: 7} | broad |
| twin-dup-third | ACCEPTED | 9 | 18 | 3.2% | {9: 5, 15: 3, 18: 8, 21: 1, 27: 1} | broad |

## Candidates (rule breaker)

| file | claim | rule | n | D | vertex | status |
|---|---|---|---|---|---|---|
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 10 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_14/breaker/candidates.json | unreachable | all-moves-cover | 9 | 15 | True | CONFIRMED unreachable (exact engine) |

## Unreached targets (fraction)

| n | before | after |
|---|---|---|
| 7 | 0/13 (0.0%) | 0/13 (0.0%) |
| 8 | 30/533 (5.6%) | 23/533 (4.3%) |
| 9 | 555/1000 (55.5%) | 537/1000 (53.7%) |
