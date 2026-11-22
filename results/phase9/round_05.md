# Phase 9 round 5

Main-track numbers only. Non-vertex variant proposals are marked VARIANT and are tracked in results/phase9/variant_nonvertex.json.

Judge time None s; budget per rule 300 s (one retry at 900 s for rules still gaining); round cap 3600 s.

## Proposals (rule maker)

| file | name | kind | status | targets gained (n: count) | s |
|---|---|---|---|---|---|
| phase9/round_05/maker/02_partial_pendant.mpr | partial-pendant |  | dropped: no gain within budget |  |  |
| phase9/round_05/maker/01_partial_dup.mpr | partial-dup | move | ACCEPTED | {'8': 114, '9': 212} |  |
| phase9/round_05/maker/02_partial_pendant.mpr | partial-pendant |  | dropped: no gain within budget |  |  |
| phase9/round_04/maker/03_twin_fiber_midpoints.mpr | twin-fiber-midpoints |  | dropped: no gain within budget |  |  |
| phase9/round_04/maker/01_fiber_midpoints.mpr | fiber-midpoints |  | dropped: no gain within budget |  |  |

## Coverage of rules with gains (per size and denominator)

| rule | status | n | gained | share of unreached | denominators (D: count) | verdict |
|---|---|---|---|---|---|---|
| partial-dup | ACCEPTED | 8 | 114 | 42.9% | {'9': 97, '10': 3, '12': 13, '15': 1} | broad |
| partial-dup | ACCEPTED | 9 | 212 | 24.2% | {'9': 81, '10': 4, '12': 81, '15': 35, '18': 11} | broad |

## Candidates (rule breaker)

| file | claim | rule | n | D | vertex | status |
|---|---|---|---|---|---|---|
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 10 | 9 | True | rejected: reachable by the current rule set |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 10 | 9 | True | rejected: reachable by the current rule set |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 10 | 9 | True | rejected: reachable by the current rule set |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 10 | 9 | True | rejected: reachable by the current rule set |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 10 | 10 | True | CONFIRMED unreachable (complete search) |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 10 | 10 | True | CONFIRMED unreachable (complete search) |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 10 | 10 | True | CONFIRMED unreachable (complete search) |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 10 | 11 | True | CONFIRMED unreachable (complete search) |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 10 | 11 | True | CONFIRMED unreachable (complete search) |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 11 | 8 | True | CONFIRMED unreachable (complete search) |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 11 | 9 | True | rejected: reachable by the current rule set |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 11 | 9 | True | rejected: reachable by the current rule set |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 11 | 9 | True | rejected: reachable by the current rule set |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 11 | 12 | True | rejected: reachable by the current rule set |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 11 | 14 | True | CONFIRMED unreachable (complete search) |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 11 | 14 | True | CONFIRMED unreachable (complete search) |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 11 | 15 | True | rejected: reachable by the current rule set |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 11 | 17 | True | CONFIRMED unreachable (complete search) |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 10 | 9 | True | rejected: reachable by the current rule set |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 10 | 10 | True | CONFIRMED unreachable (complete search) |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 11 | 8 | True | CONFIRMED unreachable (complete search) |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 11 | 9 | True | rejected: reachable by the current rule set |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 11 | 14 | True | CONFIRMED unreachable (complete search) |
| phase9/round_05/breaker/candidates.json | unreachable | all-moves-cover | 10 | 9 | True | rejected: reachable by the current rule set |

## Unreached targets (fraction)

| n | before | after |
|---|---|---|
| 7 | 0/13 (0.0%) | 0/13 (0.0%) |
| 8 | 266/533 (49.9%) | 152/533 (28.5%) |
| 9 | 876/1000 (87.6%) | 664/1000 (66.4%) |

Note: report rebuilt after a report-writing crash; judge state was written before the crash.
