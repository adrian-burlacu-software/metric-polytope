# Phase 9 round 0

Judge time 153.1 s; budget per rule 120.0 s; round cap 1800 s.

## Proposals (rule maker)

| file | name | kind | status | targets gained (n: count) | s |
|---|---|---|---|---|---|
| phase9/round_00/maker/t1_rays.mpr | test-rays-copy | generative (new base pieces) | dropped: no gain (no new base orbit) |  | 0.8 |
| phase9/round_00/maker/t3_claim.mpr | test-den-claim | structural claim | ACCEPTED (claim; open to the breaker) |  | 0.6 |
| phase9/round_00/maker/t2_twin.mpr | test-twin | move | dropped: no gain within budget | {} | 136.9 |

## Candidates (rule breaker)

| file | claim | rule | n | D | vertex | status |
|---|---|---|---|---|---|---|
| phase9/round_00/breaker/test.json | counterexample | no-simple-vertex | 8 | 3 | True | CONFIRMED counterexample |
| phase9/round_00/breaker/test.json | unreachable | all-moves-cover | 8 | 8 | True | CONFIRMED unreachable (exact engine) |
| phase9/round_00/breaker/test.json | unreachable | all-moves-cover | 8 | 1 | True | rejected: reachable by the current rule set |
| phase9/round_00/breaker/test.json | counterexample | no-simple-vertex | 4 | 1 | True | rejected: n = 4 outside the rule's domain [6] |

## Unreached targets (fraction)

| n | before | after |
|---|---|---|
| 7 | 0/13 (0.0%) | 0/13 (0.0%) |
| 8 | 266/533 (49.9%) | 266/533 (49.9%) |
| 9 | 876/1000 (87.6%) | 876/1000 (87.6%) |
