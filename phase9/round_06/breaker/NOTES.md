# Round 06 breaker notes (9c)

## 1. Walk robustness with partial-dup (design pre-registered in retest6.py / walk6.py docstrings)
A = round 5's seeded walks (seeds 1-4, 11-14) replayed: T steps stay T; all 24 F/U steps re-tested with
reachable_bu([partial-dup], 45 s). B = fresh walks (walk6.py, seed 21 at n=10, seed 22 at n=11, 30 chains, L=4, edge
steps), test = reachable(15 s), then reachable_bu([partial-dup], 45 s). No undecided cases in A or B. Full tables: table6.txt.

F/(T+F) by (n, dist):

| n, dist | r5 no moves | A: r5 + partial-dup | B: fresh + partial-dup |
|---|---|---|---|
| 10, 1 | 9/197 (4.6 %) | 6/202 (3.0 %) | 2/57 (3.5 %) |
| 10, 2 | 2/16 | 0/13 | 1/9 |
| 10, >=3 | 1/4 | 0/2 | 0/2 |
| 11, 1 | 8/289 (2.8 %) + 1 U | 4/293 (1.4 %) | 3/93 (3.2 %) |
| 11, 2 | 3/16 | 2/15 | 0/2 |
| 11, >=3 | 0/3 | 0/1 | 0/1 |

By D: every walk F with 3 | D became T (A: n=10 D=9 6->0, n=11 D=9 4->0, D=12 U->T, D=15 1->0). The remaining F are
at D = 8, 10, 11, 13, 14, 17. The 1-step rate stays well above zero (about 1.5-3.5 %), but the walks no longer find
any unreachable vertex with 3 | D.

## 2. Candidates (30 total; all vertices by check_point without --rule, see check_vertex6.txt)
gen6.py / gen6b.py: edge walks starting from earlier unreachable candidates (outside the pre-registered experiment),
testing only 3 | D in gen6b. 3 | D tested in gen6: D=9 0/9 F, D=12 1/7, D=15 4/4, D=18 0/1, D=21 1/1.
So D = 9 looks covered, while D = 15 and 18 near unreachable regions are not.
Selected: n=10: D=15 x4, 8, 10 x2, 11 x2, 13, 14; n=11: D=12, 15 x5, 18 x5, 21, 24 x2, 42 x2, 8, 11, 13.
That is 20 candidates with 3 | D. All of them are new orbits, checked against large_orbits and the rounds 1-5 candidates.

## 3. Maker proposals 01 dup-recentre, 02 dup-midshift (attack6.py / attack6.json)
I applied both moves to 26 vertices (n=4-6 and Deza 7) and checked the outputs exactly:
- 0 infeasible outputs;
- 0 restriction failures;
- 0 orbit-set mismatches under random group elements.

Not broken. 02 alone (final5.py, 25 s) leaves 29/30 candidates False. It makes one n=10 D=10 candidate reachable
(mk6_*.json). 01 was not run against the candidates because of its output volume (about 800 outputs per input).
