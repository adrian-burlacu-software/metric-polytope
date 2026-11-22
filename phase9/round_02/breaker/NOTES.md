# Round 02 breaker notes (9b: large n, 10 <= n <= 20)

## Goal
Exact vertices of m_n, n = 10..20, that the current rule set (base: cuts + all graph metrics; moves: lift, radial
Lambda^1..3, gluing with any overlap; non-vertex intermediates allowed) cannot reach.

## Main result: the denominator lemma settles 37 of the 40 candidates
Theorem 4 of `docs/denominator_lemma.md`: a derivable x in m_n has every odd prime power p^e || den(x) at most 2n - 3.
37 of the 40 candidates have an odd prime power above 2n - 3, so they are **provably unreachable** (given the lemma):

| n | 2n-3 | candidates (D, largest odd prime power) |
|---|---|---|
| 10 | 17 | 50 (25), 43, 41, 37, 31, 29, 27, 25, 23, 19, plus plain lifts with D = 43, 41 |
| 11 | 19 | 53, 49 (7^2), 47, 43, 41, 37, 31, 29 |
| 12 | 21 | 69 (23), 53, 49, 47, 46 (23), 43, 41, 37 |
| 15 | 27 | 43, 53, 47, 49 |
| 17 | 31 | 41 |
| 20 | 37 | 53, 41, 47, 43 |

The three remaining n = 10 candidates (D = 15, 14, 14) come from unreached n = 8 targets (two self-glues over 6 nodes,
one double lift). Their denominators satisfy the bound; whether they are unreachable is up to the judge.

Smallest n with such a vertex: **n = 10** is already enough (e.g. D = 19, 23, 25 > 17), and in fact the lemma's bound
is already exceeded at n = 9 by Deza's own orbits (D = 41, 43 occur among the n = 9 reps, bound 15; these are
unreachable, consistent with the lemma); any fiber vertex of a
lift keeps the n = 9 restriction, so den stays a multiple of 43 for every n with 2n - 3 < 43, i.e. up to n = 22.
Primes that do **not** occur at n = 9 also appear: 47 and 53 at n = 11 (and 47 at n = 11 and 12 again), 7^2 = 49 at
n = 11, 25*2 = 50 at n = 10. With 53, lifting keeps the vertex provably unreachable up to n = 27.

## How the points were built (scripts in this folder)
- `lib9b.py`: exact fiber vertices with cddlib's GMP LP (pycddlib 3, no float rounding): `lift` (holes = pairs through
  the new node), `glue` (holes = A\K x B\K), `free_lp` (all pairs free). Random integer objectives on the holes.
  A fiber vertex over vertex data is a vertex of m_n (block-triangular tight system); every point is re-checked.
- `walk.py` (gen 1): take a Deza n = 9 rep with D in {43, 41, 37, 31, 29, 27, 25, 23}, lift it to n = 10/11/12 by
  random fiber vertices, then maximize 1000 * (sum of a random 75-96 % of its tight rows) + random +-3 integer noise
  over all of m_n. The optimum lies on the face cut out by the kept rows, so it is a nearby vertex, frequently with a new
  denominator. (Pure random weighted max-cut objectives gave cuts ~97 % of the time - useless.)
- `walk2.py` (gen 2): same, seeded from the gen-1 vertices with odd prime power >= 25/41. This produced 47, 49, 53.
- `assemble.py`: picks one vertex per (n, D), adds plain lifts, self-glues (copy relabelled so the overlap matches) and
  lift chains up to n = 15, 17, 20, and writes `candidates.json` (extra fields `max_odd_prime_power`, `bound_2n_3`).
- `walk_*.json`, `walk2_*.json`: raw search output (first vertex found per denominator).

Denominator spectrum seen in the walks (counts, ~6,000 LPs at n = 10..12): denominators up to 57 (n = 12), 69 and 114
(n = 12); the largest odd prime is 53.

## Check
- `check_point.py chk_norule.json` (the 40 points without the `rule` field) -> `check_vertex.txt`: **all 40 feasible
  and exact vertices** (tight-set rank C(n,2)); tight counts range from 46 (n = 10) to 335 (n = 20).
- `check_point.py candidates.json` (with `"rule": "all-moves-cover"`) does **not finish**: it evaluates `derivable?` on
  the point, and four parallel runs (n = 10 / 11-12 / 15-17 / 20) all hit the 290 s timeout, even the n = 10 group.
  So `rule_fails_here` is not available for these points; note that `all-moves-cover` has `:domain (3 8)`.
  The judge will need the denominator lemma (or a cheaper test) to confirm n >= 10 claims.
- Independently, `assemble.py` asserts `verify_vertex` on every point before writing it.

## Compute
About 30 minutes of process time: walks 2 x 4 x ~80 s, assembly ~3 min, and ~20 min lost to the timed-out
check_point runs with the rule field (over the 20-minute budget; sorry).
