# Round 01 breaker notes (9a calibration, n <= 9)

Data: Deza's 1,056,367 n = 9 orbit representatives (`data/deza/orbits9`), which include every orbit (one D = 1 row,
trivial extensions with 0/1 entries, etc.), plus the design-A exact-engine records `results/n9/orbits_A.jsonl.gz`.
Scans are vectorized filters (scripts in this folder); every submitted point was re-checked with
`scripts/phase9/check_point.py` (output: `check_candidates.json`).

## Domain note
Rules with a capped `:domain` cannot take an n = 9 counterexample (the judge rejects n outside the domain):
`denominator-lemma-glue` (4 8), `denominator-prime-bound` (3 8), `vertex-moves-cover-M1` (3 7),
`three-projections-imply-vertex` (4 7), `no-cut-set` (6 6). Within their domains m_n is complete, so they cannot be
broken in this scope. (M1 at n = 8 would be outside its domain too.)

## Rules attacked at n = 9 (all 1,056,367 reps unless stated)

| rule | method | result |
|---|---|---|
| `at-least-two-cuts` | design-A records with `adj_cut = False` (89 rows); tool check | **BREAKS at n = 9** (row 19248, D = 6, adjacent to no cut; also row 300183). Smallest n, since it holds n = 5..8 exhaustively. Direct corollary of the known `dominating-set` failure. |
| `no-half-integral` | den.npy | holds (no D = 2) |
| `cuts-are-the-integral-vertices` | den.npy | holds (one D = 1 orbit: the cuts) |
| `incidence-bounds` | tight counts for all reps (triangle + perimeter) | holds: max fully fractional incidence 84 = C(9,3), attained only by row 4588 (an anticut, D = 3); max non-fully-fractional non-cut 144 <= 168 |
| `denominator-lemma-lift` | den of every one-node deletion | holds (0 failures) |
| `denominator-lemma-glue` | implied by lift (A = all-but-i is always an allowed cover piece and den is monotone under restriction); also out of domain | holds at n = 9 |
| `extension-denominator` | filter den(x) not in {d, 2d}, d != 1, before any vertex test | holds (0 candidates even before the vertex test) |
| `non-fully-fractional-is-trivial-ext` | all 3,403 non-cut reps with a 0/1 entry: twin/antitwin check + rank of the 8-node deletion | holds |
| `third-valued-is-graphic` | all 720 fully fractional D = 3 reps x all 256 switchings: 1/3-level graph of diameter 2 with an independent triple (= `graphic-point?`) | holds (2 spot-checked with the tool) |
| `switch-class-nonadjacent` | for every rep and switching S (255): common tight set of x and r_S(x) via per-triple permutation of tight masks; rank test when >= 35 common | holds (0 adjacent pairs; fully fractional and 0/1 reps) |
| `sporadic-are-vertices` | evaluated directly at n = 9 | holds |

Maker proposals (`phase9/round_01/maker/`): directory was still empty while I worked; nothing to attack.

## Unreachable candidates (claim `all-moves-cover`)
39 n = 9 Deza reps not among the judge's 1,000 targets, picked from the design-A records with `depth_detour = None`
(the judge's baseline validated these records equal to its own engine on the targets). 38,074 such rows exist; I
picked for spread in denominator: two each at D = 6 and 7 (the smallest unreachable denominators), one for each
D = 9 .. 43 present, preferring rows with `adj_cut = False`. No point needed to be built by gluing/lifting: every n = 9
vertex orbit is already one of Deza's reps, so a built point would coincide with a picked row.

## Tool check
`check_point.py candidates.json` (output saved as `aux/check_candidates.json.txt`): all 40 points are exact vertices
with 40 distinct orbit keys, none is a current target/unreached node; `rule_fails_here = True` for all 40, i.e. the
`at-least-two-cuts` counterexample fails the rule and the 39 unreachable points fail `all-moves-cover` (not derivable).
Auxiliary scan outputs were moved to `aux/*.json.txt` so that `candidates.json` is the only JSON file here.
