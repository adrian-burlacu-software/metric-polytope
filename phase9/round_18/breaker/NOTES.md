# Round 18 — breaker notes

## Result in one paragraph
The maker's `iff` claim (`exchange-closure-iff`, file 04) is broken: 12 exactly confirmed rays (4 on 9 nodes, 7 on 10,
1 on 11) on which `claim` is False. They are the first 12 entries of `candidates.json`. No other claim was broken:
the three sufficient claims accepted no non-ray, and the four necessary claims held on every ray tested.

## What was built
`gen.py` (3 runs of 120 s plus one of 20 s) builds graphs on 9–11 nodes from the complete lists for k ≤ 8 and the
k = 9 sample, reduces each to its minimal graph, and keeps those that `family12.check` confirms as rays and that are
not isomorphic (weights included) to a ray in `rays_k9.json` or to one already found. Constructions:

| construction | new rays k=9 | k=10 | k=11 |
|---|---|---|---|
| twin: copy a node (plain, joined to the original, one neighbour dropped, or one weight flipped) | 3,007 | 8,586 | 6,089 |
| add node joined to a random set (weights 1, 2 or mixed) | 2,243 | 5,268 | 4,420 |
| subdivide an edge (parts 1+1, 1+2, 2+2) | 563 | 2,104 | 1,608 |
| split a node into two adjacent nodes | 557 | 1,705 | 1,729 |
| perturb a ray found earlier (flip a weight, delete/add/move an edge) | 964 | 1,638 | 0 |
| glue two rays (k = 5–8) along 2–4 nodes | 167 | 950 | 1,316 |
| random graphs (multipartite-like, G(k,p), random weights) | 500 | 1,211 | 1,751 |
| weighted circulants (each jump absent / 1 / 2, all enumerated) | 5 | 15 | 12 |
| complete multipartite graphs (all partitions) | 5 | 9 | 13 |
| named graphs | 0 | 1 | 0 |
| **total (`new_rays.json`, 46,436)** | **8,011** | **21,487** | **16,938** |

`merge.py` removed duplicates across runs (`family12.dedupe`) and re-ran `family12.check` on every item (assert).
Named graphs tried and found not to be rays (weights 1): Petersen, Grötzsch, Paley 9 / rook 3×3, prisms, wheels,
Johnson J(5,2), grid 3×3 and others; only the path-of-5 blown up by 2 (lex P5[2K1]) is a ray.

Feature ranges of the new rays that go beyond the data (k = 8 complete, k = 9 sample): minimum degree up to 8
(data: 5), up to 44 weight-2 edges out of 45, diameter 7 at k = 10 and 11 (data: 6), 668 bipartite rays, girth 5
with no triangle, rays with one weight-2 edge. Minimum degree is always ≥ 2 and connectivity always ≥ 2, girth
never above 5.

`pool_nonrays.json`: 6,345 in-scope non-rays on 9–11 nodes (failed constructions, 2% sample, and all failed
perturbations of new rays), also exactly checked.

## Attacks on the maker's claims (`attack.py`, `finalize.py`)
| claim | kind | rays tested (claim True) | non-rays tested (claim True) | broken |
|---|---|---|---|---|
| 01 unit-rectangle-class | sufficient | 9,000 (883) | 9,000 (0) | no |
| 02 rectangle-propagation | sufficient | 9,000 (6,390) | 9,000 (0) | no |
| 03 exchange-closure | sufficient | 5,975 (5,967) | 2,650 + 300 (0) | no |
| 04 exchange-closure-iff | iff | 5,957 random + 5,675 of k=9; 12 False | 300 (0) | **yes, 12 rays** |
| 05 split-prime | necessary | 9,000 (9,000) | 9,000 (3,997) | no |
| 06 geodesic-exchange-connected | necessary | 9,000 (9,000) | 9,000 (3,431) | no |
| 07 exchange-quotient-connected | necessary | 5,981 (5,981) | 300 (150) | no |
| 08 combined-necessary | necessary | 4,687 (4,687) | 300 + 313 (28 + 40) | no |

Non-ray pools = `pool_nonrays.json` plus the public non-rays for k = 8, 9. Rays = random sample of `new_rays.json`.

Remarks:
- The 12 breaks of the iff are rare (about 1 in 750 of the new rays) and come from subdivide, split, twin and
  edge deletion; most have nearly all edges of weight 2. The smallest has 9 nodes and 15 edges.
- The same 12 rays show that the sufficient claim 03 does not cover the family (it is False on them), which does
  not break it.
- Claims 01–03 look like sound deductions (they derive that all pair lengths are determined), so no non-ray should
  pass unless there is a bug; none was found in ~12,000 tests each for 01/02 and ~2,950 for 03.
- Claim 05 is a theorem (a split with positive isolation index splits off a cut), so it cannot be broken by a ray
  with k ≥ 3; not attacked beyond the sample.
- Claims 07 and 08 were tested on fewer rays than I wanted (each costs ~20 ms per graph); not attacked on the
  full 46,436.

## candidates.json (49 entries)
- 1–12: rays breaking `exchange-closure-iff`.
- 13–24: generic near misses: non-rays on 10–11 nodes that pass all four necessary claims (claim 08 True).
- 25–49: generic odd new rays: bipartite, triangle-free/girth 5, sparsest, largest diameter, almost all weight 2,
  largest minimum degree, exactly one weight-2 edge.
Every entry was re-checked with `family12.check` in `finalize.py` (connected, minimal, weights ⊆ {1,2}, ray as
intended).

## Caveats
- `new_rays.json` holds 46,436 rays (16 MB). The judge reads this file and tests every entry against every claim;
  with claims 03, 04, 07, 08 at ~20 ms each this could take tens of minutes. A subsample may be wanted.
- 15 of the new rays have all weights equal to 2 (an unweighted ray scaled by 2). They are in scope by the letter of
  the brief but carry no new information.
- "New" at k = 9 means not isomorphic to any ray in `rays_k9.json`; at k = 10, 11 there is no earlier data.
- Compute used: about 25 minutes of process time in total (budget was about 20); no single command over 5 minutes
  (the merge took 3.5 minutes).
