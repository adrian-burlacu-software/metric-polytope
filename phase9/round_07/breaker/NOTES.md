# Round 07 breaker notes (n <= 9, judge-target complement)

## 1. Structural rules
- Ledger rules that hold: round 1 scanned every open-domain rule on all 1,056,367 Deza n = 9 reps. The rules were
  cuts-are-the-integral-vertices, no-half-integral, non-fully-fractional-is-trivial-ext, extension-denominator,
  incidence-bounds, third-valued-is-graphic, switch-class-nonadjacent and denominator-lemma-lift. All of them held;
  at-least-two-cuts broke at n = 9 and is reported. The capped-domain rules (three-projections-imply-vertex (4 7),
  no-cut-set (6 6), vertex-moves-cover-M1 (3 7), denominator-lemma-glue (4 8), denominator-prime-bound (3 8)) are
  checked against complete m_n lists inside their domains, so this scope cannot hold a counterexample to them.
  sporadic-are-vertices (7 9) concerns a fixed literature list.
  No smaller counterexample is possible for the BREAKS rules: they were checked exhaustively below the breaking n.
  **Nothing new is broken.**
- `rules/phase9_accepted.mpr` holds only moves (partial-dup, dup-midshift) and no structural claims.
- Maker round 7: no `*.mpr` in `phase9/round_07/maker/` while I worked (only analysis scripts), so there was nothing
  to attack.

## 2. Unreachable candidates: 40 n = 9 Deza reps, each locally certified unreachable by the judge's own engine
Method:
- Pool (`select7.py` -> `pool7.json`): design-A records (`results/n9/orbits_A.jsonl.gz`) with
  depth_detour = None that are neither judge targets (`baseline.json` n9_rows) nor round-1 claims.
- Retention among the targets: of the design-A-None targets, the share still unreached under the current rules is:
  D = 7: 1/6, D = 9: 6/87, D = 10: 41/73, D = 12: 33/117, D = 15: 37/72, D = 18: 22/33.
  All other D are 100 %: D = 8, 11, 13, 14, 16, 17+.
- Local certificate (`localreach7.py`): a SCRATCH `metricpoly.reach.Engine` (in my temp dir) with my rows as
  its only targets. Already-reached nodes come from `checkpoints/phase9/reached.json` (read-only), restricted to the
  scratch engine's nodes. Base and graph test as in judge.py, and the accepted user moves are applied forward via
  `phase9_round.Forward`. This is the same fixpoint the judge runs on an added n = 9 claim. Every intermediate of a
  derivation is a restriction of the target, so the scratch node set is complete for these rows.
- Validation: 4 n = 9 targets that the judge reaches (rows 41383, 42772, 219124, 76612; D = 10) were run with skip
  limited to nodes of <= 7 points, so their 8- and 9-node pieces had to be re-derived. All 4 were reached again.
- Results (batch7a: 64 rows; batch7b: 40 rows of D = 7, 9, 10, 12, 15; about 2 min of compute in total):
  - D = 6: 0/4 unreached;
  - D = 7: 5/12;
  - D = 9: 0/12, which supports round 6's finding that D = 9 is covered;
  - D = 10: 4/12;
  - D = 12: 4/12;
  - D = 15: 3/12;
  - D = 18: 4/4;
  - every row with D = 8, 11, 13, 14, 16 or D >= 17: unreached.

Submitted (`build7.py` -> `candidates.json`; all n = 9 and 40 distinct orbit keys):

| D | count |
|---|---|
| 7 | 5 |
| 8 | 2 |
| 10 | 4 |
| 11 | 2 |
| 12 | 4 |
| 13 | 2 |
| 14 | 2 |
| 15 | 3 |
| 16 | 1 |
| 18 | 4 |
| 20, 21, 22, 24, 26, 28, 32, 33, 35 | 1 each |
| 17, 19 | 1 each; these violate the denominator-lemma bound |

38 of the 40 are within the denominator-lemma bound, so the lemma does not explain them. The smallest denominators
are D = 7 (prime, 5 orbits) and D = 8 (no odd prime).

## Tool check
`check_point.py chk7_norule.json` -> `check_vertex7.txt` (run without the rule field; with the rule field,
`all-moves-cover` derivability did not finish in 280 s): 40/40 exact vertices, 40 distinct orbit keys (identical to the
local engine's keys), none is a current target or unreached node.

## Files
select7.py, pool7.json, localreach7.py, pilot7.json, valid7.json, batch7a.json, batch7b.json, build7.py,
candidates.json, chk7_norule.json, check_vertex7.txt. Scratch engine caches were deleted.
