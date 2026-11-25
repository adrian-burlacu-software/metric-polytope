# Phase 9 status after round 17 (2026-11-24)

Phase 9 is the rule game. A rule maker proposes ways to build vertices of the metric polytope m_n from smaller
pieces, a rule breaker looks for vertices the rules cannot build and for counterexamples to claims, and an exact judge
(`scripts/phase9/judge.py`, `scripts/phase9/phase9_round.py`) decides. The point is to find shortcuts, rules that
describe many vertices at once, and to find exactly where each one stops working.

This note records where the game stands after 15 rounds: what was accepted, what each rule reaches, where the
shortcuts break, what is left, and the negative results. Every number below comes from an exact check. Sources are
`results/phase9/round_*.md`, `results/phase9/shadow_ladder_n{8,9}.json` and the round folders `phase9/round_NN/`.

## 1. Setting

- **Targets.**
  - All vertex orbits of m_7 (13) and m_8 (533; complete, from Deza et al.).
  - 1,000 seeded orbits of m_9, out of Deza's 1,056,367 representatives.
- **Reaching.** A target is reached if some chain of moves from base pieces produces it (`metricpoly/reach.py`).
  - Base pieces: cuts, anticuts, complete multipartite metrics, tree suspensions, Avis paths, all graph metrics
    (2/τ)·d_G, plus the accepted base families below.
  - Moves: lift (a vertex of the one-node fiber), radial Λ¹–Λ³, gluing with any overlap, plus the accepted moves below.
    Intermediate points may be non-vertices.
- **Hard rules** (user decisions after round 1):
  - Base pieces must be exact vertices.
  - Main-track moves must keep their input as a restriction.
  - Every rule must be defined for every n.

  With these rules, "unreachable" is an exact verdict. Non-vertex seeds and rescaling moves live on a separate
  variant track (`results/phase9/variant_nonvertex.json`) and never enter the main numbers.
- **Judge settings:**
  - 300 s propagation budget per rule, with one 900 s retry for rules still gaining sub-orbits.
  - A separate 900 s allowance for generating a base family, run one n at a time. A family is judged on the sizes
    that finish.
  - 30 min per round. Rounds 11 and 12 had 60 min by user decision.

## 2. Progress

Unreached targets on the main track. m_7 was fully reached throughout.

| after round | m_8 unreached (of 533) | m_9 unreached (of 1,000) | accepted this round |
|---|---|---|---|
| start (main track) | 266 (49.9%) | 876 (87.6%) | — |
| 5 | 152 | 664 | move partial-dup |
| 6 | 120 | 628 | move dup-midshift |
| 7 | 102 | 601 | move radial-lowend |
| 8 | 99 | 589 | move dup-thirdshift (retry) |
| 10 | 85 | 578 | base family gen-bipartite-glue (judged on n ≤ 8) |
| 11 | 77 | 570 | base families gen-house-c4-d11, gen-house-p4-d11 |
| 12 | 30 | 555 | base families gen-dyadic-tower-w1, -w2 (judged on n ≤ 8) |
| 14 | 23 | 537 | move twin-dup-third (retry) |
| 15 | 22 | 515 | move twin-dup-blend (retry) |
| 16 | 22 | 494 | move twin-dup-fifths (retry) |
| 17 | **22 (4.1%)** | **487 (48.7%)** | move twin-dup-sevenths (retry) |

Rounds 1–4, 9 and 13 accepted nothing on the main track. Rounds 15–17 gained only at n = 9; the 22 remaining m_8
targets have nothing reached. Round 1's scaled graph metrics and round 3's
radial-normalized were later moved to the variant track because they break the hard rules.

The breaker's unreachable claims were confirmed 387 times in rounds 1–14. Some points were confirmed again in later
rounds. Rounds 11–14 submitted only n = 9 points that are not targets.

## 3. Accepted rules (`rules/phase9_accepted.mpr`)

### Moves (all `:grow 1`, keep the input, defined for every n)

| move | round | what the new column is | targets gained (n = 8 / n = 9) |
|---|---|---|---|
| partial-dup | 5 | copy of node i at distance t·δ_i from it (t = p/q, q ≤ 6): the twin–dup fiber edge | 114 / 212 |
| dup-midshift | 6 | dup column of i, with one other entry moved to the midpoint of its feasible interval | 32 / 36 |
| radial-lowend | 7 | radial value maxc(x − j)/2 for all nodes except j, low end of the interval at j | 18 / 27 |
| dup-thirdshift | 8 | partial dup at t ∈ {1/4, 3/4, 1}, with one other entry at 1/3 or 2/3 of its interval | 3 / 12 |
| twin-dup-third | 14 | point at 1/3 or 2/3 of the segment from twin_i to dup_j or antidup_j | 7 / 18 |
| twin-dup-blend | 15 | the same segment at t ∈ {1/4, 1/2, 3/4} | 1 / 22 |
| twin-dup-fifths | 16 | the same segment at t = k/5; brings in the prime 5 (judge: narrow, all D = 15) | 0 / 21 |
| twin-dup-sevenths | 17 | the same segment at t = k/7; brings in the prime 7 (judge: narrow, all D = 21) | 0 / 7 |

All eight put the new node on a low-dimensional face of the one-node fiber, mostly an edge, at a simple rational
position. That is the one kind of shortcut that kept working.

### Base families (vertices only)

| family | round | construction | gained (n = 8 / n = 9) | works at n = 9? |
|---|---|---|---|---|
| gen-bipartite-glue | 10 | one-node glue fiber of (4/(2n−3))·d(K_{2,n−5}) and (5/(2n−3))·d(C_4) | 14 / 11 | no: the n = 9 version yields no vertex (round 11) |
| gen-house-c4-d11 | 11 | two-stage glue of (4/(2n−5))·d(co-P_{n−3}) and (4/(2n−5))·d(C_4) | 6 / 4 | yes, but 293 new n = 9 orbits reach only 4 targets |
| gen-house-p4-d11 | 11 | the same, with (3/(2n−5))·d(P_4) | 2 / 4 | as above |
| gen-dyadic-tower-w1 | 12 | lift tower, keeping D = 8, over a fixed 6-node core (1/8)·d_W | 41 / 14 | n = 9 generation does not finish in 900 s |
| gen-dyadic-tower-w2 | 12 | the same over a second core (judge: narrow) | 6 / 1 | as above |

For the families judged on n ≤ 8 (bipartite-glue, the two towers), every n = 9 gain comes through their n = 8 pieces.

## 4. Where the shortcuts break

### 4.1 Structural claims (ledger, `rules.md`)

| rule | breaks at |
|---|---|
| projects-to-smaller-vertex, lift-fiber-complete, fractal-vertex-blocks | n = 5 |
| finite-middle-vocabulary | n = 6 |
| vertex-moves-cover, all-moves-cover-vertex-only, fractal-const | n = 7 |
| no-simple-vertex, fractal-structured, all-moves-cover (base engine) | n = 8 |
| dominating-set | n = 9 |

The ledger rules that still hold were checked against all of m_7, m_8 and the 1,056,367 m_9 representatives. No
maker claim in rounds 1–15 survived as a new structural rule.

### 4.2 Generative: the restriction barrier

Main-track moves keep their input as a restriction. So a target can become reachable through moves only if some
proper restriction of it is already reached. The **restriction profile**, the largest reached restriction of each
unreached target, therefore splits the unreached targets exactly (`scripts/phase9/shadow_ladder.py`):

| | unreached | nothing reached (needs a base piece at that n) | some restriction reached |
|---|---|---|---|
| m_8 | 22 | 22 | 0 |
| m_9 (after round 17) | 487 | 468 | 19 |

The **denominator lemma** (`docs/denominator_lemma.md`) sharpens this. The moves of rounds 5–15 multiply
denominators only by 2 or 3. If another odd prime p divides a target's denominator, either a restriction carrying p
is a base piece, or some move must introduce p. Rounds 16–17 added the second kind: twin-dup-fifths and
twin-dup-sevenths put the new node at fifths or sevenths of a fiber edge, and reached 28 of the 38 partly reached
targets with D = 15 or 21.

The 19 partly reached m_9 targets left after round 17:
- 10 carry 5 or 7 (D = 15: 7, D = 21: 3). Round 16 found that fifths and sevenths on the twin–twin and twin–antidup
  segments as well reach at least 34 of the original 38 in simulation. At least 4 need 3- or 4-dimensional fiber
  faces.
- 9 have a denominator built from 2 and 3 alone (D = 18: 3, 24: 3, 27: 2, 12: 1). No segment or 2-face blend of
  special columns tried in rounds 14 and 16 reaches them.

So moves, which apply at every n, are close to exhausted on these targets. Everything else needs new base pieces.

### 4.3 Generative: base families do not carry over from n to n + 1

This is the main finding of rounds 10–13.
- Each family found for the n = 8 targets is either:
  - specific to that n: gen-bipartite-glue gives no vertex at n = 9;
  - or makes n = 9 vertices that are mostly not targets: the house families make 305 new n = 9 orbits and reach 8
    targets.
- The odd-denominator m_8 targets are x = (2/D)·d for integer metrics d that are never graph metrics (round 7). Their
  scales go with n (13 = 2n − 3, 11 = 2n − 5 at n = 8), but the shapes behind them do not continue.
- **The dyadic vertices are not built by a short rule** (round 13):
  - Round 12's towers come down to "stars over a fixed 6-node core": each extra node attaches through one of about
    165 columns, and each distance between two extra nodes is an end of its interval. This describes 73 of the 84
    n = 8 outputs.
  - At n = 9 it describes 5 of the 15 D = 8 targets and none of the 59 D = 16 targets.
  - Those targets sit over 585 (D = 8) and 3,819 (D = 16) different 6-node cores. D = 16 does not come from halving.
- Generation cost grows too fast. Round 10's family and round 12's towers both enumerate fibers, and neither finishes
  n = 9 in 900 s.

**In short:** the move shortcuts carry across n, but they only reach targets that already have a reached part. The
base-piece shortcuts reach the "nothing reached" targets at one n and break at the next. Between m_8 and m_9 the
generative picture breaks at the base: about 47% of the m_9 sample (468 targets) would need base pieces that are new
at n = 9.

Round 16 (track A) tested this targets-first on the 214 m_9 targets with D = 11 or 13 and found nothing to build an
open-ended family from:
- D = 13 (116 targets): only 24 have a one-node cover by two scaled graph metrics, and no cover type covers more than 2.
- D = 11 (98): one weak shape, round 11's house glue at scale 2n − 7 instead of 2n − 5. It covers 14 targets spread
  over about 10 variants, and the DSL could not generate it at n = 9 within 10 minutes.
- Almost no 8-node restriction of these targets lies on an extreme ray of MET_8: 4 of 115 at D = 13, 2 of 97 at D = 11.
  So gluing or lifting rescaled smaller vertices cannot reach them.

## 5. What is left

**m_8: 22 unreached.** None has a reached restriction.

| D | 11 | 7 or 14 | 13 | 8 | 10 |
|---|---|---|---|---|---|
| targets | 10 | 7 | 2 | 2 | 1 |

- D = 11: ids 93, 140, 159, 167, 215, 229, 470 and 504 have no cover by two scaled graph metrics.
- D = 8: the 2 targets need cores of their own (round 12).

**m_9: 487 unreached.**
- Nothing reached: 468.

  | D | count |
  |---|---|
  | 13 | 116 |
  | 11 | 98 |
  | 14 | 66 |
  | 16 | 59 |
  | 17 | 27 |
  | 10 | 24 |
  | 19 | 21 |
  | 8 | 15 |
  | other | 42 |
- Partly reached: 19 (D = 15: 7, D = 21: 3, D = 18: 3, D = 24: 3, D = 27: 2, D = 12: 1). The largest reached
  restriction has 3 nodes for 6 of them, 4 for 4, 5 for 5 and 6 for 4. See §4.2.

## 6. Negative results worth keeping

- **Ladder.** The Phase 10 ladder (rung definitions) does not localise breaks. Every unreached m_8 target breaks at
  rung 0 (`docs/ladder_semantics.md`).
- **Scaled-graph-metric constructions for the odd-D and dyadic m_8 targets** (round 7) gave at most 1 target per
  family:
  - a 7-node restriction of the form λ·d_G: D = 13: 1 of 16; D = 11: 0 of 18; D = 8: 0 of 49;
  - sums of two graph metrics: 1 target in all;
  - lift chains whose every step is a vertex: 2 of the 16 D = 13 targets.
- **Dyadic.** The full dyadic lift closure from 3-node seeds has 2,126 orbits at 7 nodes already (round 12). Six
  D = 8 targets have no switching with edge weights in {2, 3}.
- **Moves tried and dropped:**
  - fiber-midpoints, fiber-thirds and twin-fiber-midpoints (round 4) and partial-pendant (round 5): no gain within
    budget;
  - dup-recentre (round 6): 1.37 s per input, dropped at 300 s and at 900 s;
  - other twin/dup blends (round 14): twin–twin 15, twin–antidup 6, dup–dup 1 and dup–antidup 0 targets in
    simulation.
- **Partly reached targets missed by round 14's moves.** About 24 of the 70 that are move-reachable in principle
  were not gained. Their frontier columns sit on 2- or 3-dimensional fiber faces with no common rule found.

## 7. Process notes

- **Generation allowance.** Generative rules get a separate 900 s generation allowance, run one n at a time (user
  decisions 2026-11-23). Rounds 9–10 showed that a single-call generation of n = 3–9 cannot be judged otherwise.
- **Round 8 operator error.** Two of the judge's generation subprocesses were killed by mistake. This is recorded in
  `phase9/round_08/JUDGE_NOTE.md`. Since then, processes are listed and checked before anything is killed.
- **Retries are carried over.** A rule dropped at 300 s while still gaining is retried at 900 s, and if the round
  cap runs out, in the next round. Rounds 8, 10 and 15 existed for that.

## 8. Directions

Directions 1–3 below were tried in rounds 16–17 (three parallel maker tracks, `phase9/round_16/`).

1. **Base pieces at n = 9, built targets-first** for D = 11 and 13 (214 targets). *Tried (round 16, track A): no
   proposal.* No shared structure was found to build an open-ended family from (§4.3).
2. **A move that brings in the prime 5 or 7** for the partly reached m_9 targets with D = 15 or 21. *Tried (rounds
   16–17, track B): twin-dup-fifths and twin-dup-sevenths accepted, 28 targets.* Not yet proposed: the same fifths and
   sevenths on the twin–twin and twin–antidup segments, which reach at least 34 of the original 38 in simulation.
3. **Higher-dimensional fiber faces**, for the 2,3-denominator targets. *Tried (round 16, track C): nothing to
   propose.* Round 14's centroid of three special columns now gains only 2 targets, because twin-dup-third and
   twin-dup-blend took the rest. A cheaper O(n²) triangle family costs about 12k columns per 8-node input. The 9
   remaining 2,3-denominator targets are not reached by any segment or 2-face blend tried.
4. **Accept the barrier as the result.** Document that the generative description of m_n needs new base pieces at
   each n, and measure how that set grows from m_8 to m_9. *Not started.* Rounds 16–17 strengthen the case for it.

## 9. Structure of the vertices (ideas 1–4, 2026-11-24/25)

Four measurements after round 17, to see what a generative description has to cover. Scripts
`scripts/phase9/vertex_structure.py` and `scripts/phase9/sample_reach.py`; results in `results/phase9/vertex_structure_*.json`
and `results/phase9/sample_reach_n*.json`. All exact (rank mod 2^31−1 with an exact fallback when deficient).

**1. Seed size.** Peel nodes one at a time while the restriction stays a vertex of the one-node fiber over the smaller
restriction; the seed is the smallest node set reached. Full m_9 list (1,056,367 orbits, 100 min on 16 workers): seed 3:
583,636; seed 4: 472,722; seed 5: 8 (Deza indices 3562, 3638, 3820 with D = 3; 251870, 263569, 294178 with D = 9;
510482 with D = 11; 575790 with D = 12); seed 2: the cut orbit only. All m_8 orbits have seed ≤ 4. So almost every
vertex is a chain of one-node fiber vertices over a 3- or 4-node seed. The obstacle is not the seed but which fiber
vertex each step picks.

**2. Primitive share** (no restriction on 3 ≤ k < n nodes is a vertex of m_k): n = 7: 4/13; n = 8: 219/533;
n = 9: 673,787/1,056,367 (63.8%; 647/1000 among the Phase 9 targets). The share grows with n, which is the
restriction barrier of §4.2 in numbers. Largest vertex restriction at n = 9: none 673,787; 8 nodes 159,525;
7 nodes 7,316; 6 nodes 500; 5 nodes 215,239.

**3. Cut adjacency.** Every m_8 orbit is adjacent to a cut. At n = 9, 1,221 orbits are not, exactly the count in the
literature (Laurent–Poljak dominating-set conjecture, false at n = 9; `docs/literature.md` S8, C10), which validates
the test; denominators 6–33, mostly 12, 15, 18, 21. Not new: up to switching, cut-adjacent vertices are the scaled
rays of the metric cone (C10), so through n = 8 m_n is "switchings of scaled MET_n rays", and that fails at n = 9.

**4. Reached share away from the target lists.** Random walks on the vertex graph of m_n from twin starts; verdict by
the main engine (reached.json) or the judge's bottom-up search with all accepted moves, 300 s each. n = 8: 27/27
reached; n = 9: 9/14 (two runs); n = 10: 4/7. Every unreached verdict was an exhausted search (4–7 s), none over
budget; unreached denominators 10, 11, 13, 13, 16, 17. Samples are small and biased toward the twin starts (walks at
n ≥ 9 are slow: cdd enumeration explodes at degenerate vertices, so steps are gated by tight-row count), so only the
trend counts: the reached share falls from n = 8 to n = 9 and stays roughly level at n = 10.

## 10. Rules or exceptions? Step types of the peel chains (2026-11-25)

Question (user): either the rules keep growing or the exceptions do. The "exceptions grow" reading of §9 (primitive
share 64%) holds only for moves that must keep a *vertex* restriction. Without that requirement, the seed result says
almost every vertex is a chain of one-node steps, so the question becomes how many kinds of step there are.

**Step types are signed graphs.** Peeling v from S, each tight triangle (v, a, b) gives a row u_a − u_b = c ("diff")
or u_a + u_b = c ("sum") in the unknowns u_a = x_va. The step is determined iff every component of this signed graph on
S − v has an unbalanced cycle (odd number of sum edges); the rest of the component is tree propagation. So a step's
rule is its anchors: the shortest unbalanced cycle length per component (2 = a diff and a sum row on one pair).
Script `scripts/phase9/step_types.py`, results `results/phase9/step_types.json`. Per vertex: the chain reaching the
smallest seed, then the smallest longest anchor.

| n | vertices | longest anchor (count) | distinct step signatures (new) |
|---|---|---|---|
| 7 | 12 | 3: 12 | 3 (1) |
| 8 | 532 | 3: 528, 5: 2, 7: 2 | 5 (2: [5], [7]) |
| 9 | 20,000 sampled | 3: 19,711, 5: 259, 7: 30 | 5 (0) |
| 10 | 7 (walk samples) | 3: 7 | 1 (0) |

**Full m_9 list** (1,056,366 non-cut orbits, `results/phase9/step_types_m9all.json`, 39 min): longest anchor
3: 1,042,960; 5: 11,843; 7: 1,563; no 8. Step signatures [3] 5,760,177, [3, 3] 88,230, [5] 11,967, [2] 3,497,
[7] 1,565, and one new at n = 9: [3, 5] (22 steps), a two-component step combining existing anchors, not a new anchor
kind.

Signatures through n = 8 are [2], [3], [3, 3], [5], [7]. At n = 8 the 7-cycle is the longest possible, so these data alone cannot
bound the anchor length. **Growth test** (`scripts/phase9/anchor_growth.py`, `results/phase9/anchor_growth.json`):
Avis doubling of the path P_d (literature C9), checked exactly as vertices, n = 8, 11, 14 with D = 4, 5, 6: every chain
uses 3-cycle anchors only, also when minimising over all chains. Unbounded denominators do not force longer anchors.

**Reading.** The kinds of step do not grow (5 signatures through n = 9, none new at n = 9; a family with unbounded
denominators needs only 3-anchors). The chain leaves the seed's ≤ 6 coordinates free; they are pinned at the end by the
remaining tight rows (the closing condition), which is where the denominators come from. So neither the rules nor the
exceptions grow: what grows is the number of *choices* (which triangles are tight at each step, which closing). The
Phase 9 barrier is the requirement that intermediates be vertices. Open: the branching of a generator built from these
steps on non-vertex intermediates, i.e. whether the choices can be made by rule rather than by search.

## 11. A generator from the step types, on m_8: complete, but it is a search (2026-11-25)

`scripts/phase9/fiber_generator.py`, results `results/phase9/fiber_generator_n8.json`. For a target denominator D:
all 3- and 4-node points of m_k in (1/D)Z up to symmetry (seeds), then at each level every vertex of the one-node
fiber that lies in (1/D)Z (exactly the determined steps of §10; intermediates need not be vertices), orbits merged;
at level 8 every candidate is tested for being a vertex of m_8.

| D | level 4 | 5 | 6 | 7 | level-8 candidates | of which vertices | Deza orbits with this D found |
|---|---|---|---|---|---|---|---|
| 3 | 8 | 14 | 29 | 64 | 2,958 | 1,274 (43%) | 52 / 52 |
| 4 | 23 | 49 | 155 | 670 | 67,164 | 190 (0.28%) | 12 / 12 |
| 5 | 38 | 115 | 538 | 4,446 | 757,052 | 302 (0.04%) | 15 / 15 |
| 6 | 85 | 311 | 1,871 | 22,788 | 5,215,846 | 3,436 (0.07%) | 95 / 95 |

(Level sizes are orbits; level-8 candidates are counted with repeats. "Vertices" includes vertices whose denominator
divides D.) Fiber vertices per point grow from about 12 at level 4 to about 75–170 at level 7.

**Reading.** The generator is complete (every orbit found, none missed), so the five step types really do generate
m_8. But nothing in it picks the right step: almost all branches die at the final vertex test, and the tree grows like
D^9 to D^11 (level-7 orbits ×356 and candidates ×1,760 from D = 3 to D = 6). Extrapolated to D = 15, the largest m_8
denominator, that is about 10^11 candidates. So the answer to "rules or exceptions" is: the rules are finite, but they
are not a shortcut. Generating m_n with them is a lattice search whose size is set by the denominators, i.e. vertex
enumeration in another form. A shortcut would need a rule that chooses the step (which fiber vertex) from local data;
the vertex share above (0.04–0.3% at D ≥ 4) measures how far a blind choice is from that.

## 12. What a perfect step-choice rule would save (2026-11-25)

`scripts/phase9/useful_share.py`, results `results/phase9/useful_share_n8.json`. A level-k point of the §11 generator
is *useful* if it is x|S for an m_8 vertex x (denominator dividing D) with S on a build chain of x (buildable from
4 nodes by determined steps and extendable to all 8). Choice ratio: for each useful point, its distinct kept
one-node extensions and how many of them are useful.

| D | useful / generator orbits, level 4 | 5 | 6 | 7 | vertex orbits (D' divides D) |
|---|---|---|---|---|---|
| 3 | 3 / 8 | 8 / 14 | 15 / 29 | 31 / 64 | 52 |
| 4 | 12 / 23 | 16 / 49 | 24 / 155 | 22 / 670 | 12 |
| 5 | 15 / 38 | 24 / 115 | 37 / 538 | 37 / 4,446 | 15 |
| 6 | 39 / 85 | 92 / 311 | 200 / 1,871 | 287 / 22,788 | 147 |

| D | useful children per useful point / distinct options, step 4→5 | 5→6 | 6→7 | 7→8 |
|---|---|---|---|---|
| 3 | 3.0 / 3.0 | 3.3 / 4.0 | 4.5 / 5.7 | 5.9 / 14.1 |
| 4 | 2.0 / 3.6 | 3.0 / 8.2 | 2.8 / 13.9 | 1.9 / 21.3 |
| 5 | 2.5 / 5.3 | 4.0 / 11.1 | 4.1 / 17.9 | 1.8 / 33.1 |
| 6 | 3.2 / 5.8 | 4.7 / 13.5 | 4.9 / 29.4 | 2.7 / 65.5 |

**Reading.** The useful tree is small and stays close to the size of the answer (at D = 6: 39, 92, 200, 287 orbits,
ending in 147 vertices), while the blind tree grows to 22,788 orbits at level 7. Only 1–3% of level-7 orbits are useful
at D ≥ 4. Each useful point has about 2–5 useful extensions out of 4–65 options, and the share of good options falls
with the level (to 4–9% at the last step for D ≥ 4). So a perfect local choice rule would turn the search into an
output-sized construction: that is the prize. Whether a *local* rule exists is the open question; the useful and
non-useful extensions recorded here are the data to test candidate rules on.

## 13. Local features do not choose the step (2026-11-25)

`scripts/phase9/choice_features.py`, results `results/phase9/choice_features_n8.json`. Every distinct extension of
every useful point (§12), labelled useful or not, with local features: excess tight rows of the child, tight rows
through the new node (and their excess over the k a determined step needs), whether the child is a vertex of
m_{k+1}, the step's longest anchor, the new coordinates' denominator, and whether the new node is a twin. For each
feature, the strictest threshold that keeps every useful extension, and the share of options it keeps:

| D | step | useful / options | best safe single-feature rule (share kept) |
|---|---|---|---|
| 4 | 4→5 | 24 / 43 | excess ≤ 3 (86%) |
| 4 | 6→7 | 67 / 334 | new-node rows ≤ 20 (96%) |
| 4 | 7→8 | 42 / 469 | excess ≥ 10 (50%) |
| 5 | 5→6 | 95 / 267 | excess ≤ 8 (91%) |
| 5 | 6→7 | 151 / 664 | excess ≤ 14 (90%) |
| 5 | 7→8 | 66 / 1,223 | excess ≥ 5 (68%) |
| 6 | 5→6 | 432 / 1,244 | none below 99.8% |
| 6 | 6→7 | 984 / 5,875 | none below 99.9% |
| 6 | 7→8 | 770 / 18,792 | excess ≥ −1 (82%) |

**Reading.** No single local feature prunes safely at the intermediate steps: the best keeps 86–100% of the options,
while only 17–56% are useful. The degeneracy guess is wrong in direction: at intermediate steps useful children have
*fewer* excess tight rows than the most degenerate non-useful ones, and twins are mostly but not always non-useful
(D = 6, 6→7: 34 useful, 510 not). Being a vertex of m_{k+1} is rare for intermediates (they are mostly not vertices,
which is the §9 primitive share again). At the last step the real filter is the vertex test itself. So within these
features the choice is not local: a useful intermediate looks like a non-useful one until the build is finished.

## 14. Rules or exceptions, tested on both sides (2026-11-25)

A generator that needs the vertex test as a filter (§11) is not a rule set. With rules that must output vertices,
either the rules or the exceptions grow. Two tests, one per side.

**Exceptions under bounded moves** (`scripts/phase9/move_capacity.py`, `results/phase9/move_capacity.json`). All 8
accepted moves applied to all 533 m_8 orbits (reached or not) give 70,047 outputs that are vertices of m_9, counted
without merging orbits, so at most 70,047 orbits: 6.6% of the 1,056,367 known m_9 orbits (mean 131 per input, max
1,456). Ceilings that hold for *any* move keeping its input as a vertex restriction (§9 data): 159,525 m_9 orbits
(15.1%) have an 8-node vertex restriction, 382,580 (36.2%) have any vertex restriction. So at least 63.8% of m_9 is
out of reach of every such move, whatever is proposed; the orbit count grows ×41 then ×1,982 per node while a move
with a bounded choice gives polynomially many outputs. On this side the exceptions grow.

**Rules as graph-indexed families** (`scripts/phase9/graph_types.py`, `results/phase9/graph_types.json`). Each
cut-adjacent vertex is, after a switching, a scaled shortest-path metric of its minimal weighted graph; its type is
the set of edge weights (minimised over valid switchings). Alphabet {1} = unweighted graph metric.

| n | vertices | distinct weight alphabets | unweighted share | typical alphabet size | largest weight |
|---|---|---|---|---|---|
| 5, 6 | 1, 2 | 1 | 100% | 1 | 1 |
| 7 | 12 | 2 | 92% | 1 | 2 |
| 8 | 532 | 9 | 20% | 2–3 | 6 |
| 9 | 20,000 sampled (27 not cut-adjacent) | 270 (99 in a 2,000 sample: not saturated) | 0.6% | 3–4 | 15 |

On this side the rules grow: the unweighted family, which is all of m_5 and m_6, covers 0.6% of m_9, and the number
of weight patterns goes 2, 9, 270+.

**Reading.** Through n = 9 both grow, each in its own framework: bounded moves leave a growing majority of
exceptions, and graph-indexed families need a growing number of weight patterns. Caveat: the weight alphabet is one
way to cut families; a family with parametrised weights could merge many alphabets, so this is evidence, not a proof,
that no finite graph-indexed rule set exists.

## 15. Do parametrised weights collapse the weight patterns? (2026-11-25)

`scripts/phase9/graph_families.py`, results `results/phase9/graph_families.json` (m_5..m_8 complete, 20,000 sampled
m_9 orbits, one switching per orbit: the one with the simplest alphabet).

| n | cut-adjacent vertices | alphabets (intervals {a..b}) | orbits with an interval alphabet | unweighted minimal graphs | most weightings on one graph |
|---|---|---|---|---|---|
| 7 | 12 | 2 (2) | 100% | 11 | 1 |
| 8 | 532 | 9 (8) | 99.4% | 256 | 12 |
| 9 | 19,973 sampled | 270 (36) | 89.5% | 8,006 | 48 (in a 2% sample) |

- **Alphabets collapse partly.** Most orbits use an interval of weights, so "which weights occur" is two numbers
  (a, b) for about 90% of m_9, not 270 separate patterns.
- **The weights are not a function of the graph.** At n = 8, 256 graphs carry 532 orbits: 163 graphs carry one vertex,
  93 carry 2 to 12. At n = 9 the sample already shows graphs with 48 different weightings. A rule "graph ↦ vertex"
  therefore needs the weighting as extra input, and the number of graphs itself grows (11, 256, over 8,000 sampled).
- (At n = 8 there are 516 weighted graphs for 532 orbits: merging distance-0 twins forgets which node was doubled.)

So parametrised weights do not rescue a finite rule set: the pattern count shrinks, but the information a rule must
supply per vertex (a graph on up to n nodes plus a weighting) grows with n.

## 16. Conclusion of Phase 9 (2026-11-25)

**Question.** Is there a generative description of the vertices of m_n that is shorter than the list: a fixed set of
rules valid for all n, plus exceptions?

**Answer through n = 9: no, in every form tried, and each failure is measured.**

1. *Moves from smaller vertices* (rounds 1–17: 8 accepted moves, 5 base families). They reach 511 of 533 m_8 orbits
   and 513 of 1,000 sampled m_9 targets. Applied to all of m_8 they give at most 6.6% of m_9, and no move of this
   kind can exceed 36.2%, because 63.8% of m_9 orbits contain no smaller vertex (4/13, 219/533, 673,787/1,056,367 for
   n = 7, 8, 9). Exceptions grow (§9, §14).
2. *Base families* reach the remaining targets at one n and do not continue to n + 1 (§4.3).
3. *One-node steps without the vertex requirement.* Every one of the 1,056,366 non-cut m_9 orbits is a chain of
   determined one-node steps over a seed of at most 5 nodes (at most 4 for all but 8 orbits), and the steps come in 6
   kinds, anchored by cycles of length 2, 3, 5 or 7 (§9, §10). But the kinds do not say which step to take: a generator
   built from them is complete on m_8 and is a lattice search growing like D^9 to D^11, with 0.04–0.3% of candidates
   being vertices; no local feature tried separates the useful steps (§11–§13).
4. *Graph-indexed families.* The unweighted graph metrics are all of m_5 and m_6, 92% of m_7, 20% of m_8, 0.6% of
   m_9. Weight patterns go 2, 9, 270+; a graph does not determine its weighting (§14, §15).

**What is established.** (a) The structure in item 3: a uniform, exact normal form for every known m_9 vertex.
(b) The primitive share and the move ceiling: a proof-from-data that restriction-keeping rules cannot describe m_9.
(c) Reproduced from the literature as checks: 1,221 m_9 orbits not adjacent to a cut; every m_8 orbit adjacent.
(d) Where a shortcut would have to live: in a non-local choice among fiber vertices. The useful part of the search
tree is output-sized (§12), so the cost of m_n is the cost of that choice.

**Limits.** n ≤ 9 only (n = 10: 7 walk samples). The m_9 list is Deza's, "probably complete", not proved. The
generator results are for m_8 with D ≤ 6. "No local feature" means the six features of §13, not all possible ones.

## 17. Family study, first test: weighted vertices as restrictions of unweighted graph metrics (2026-11-25)

`scripts/phase9/subdivision_test.py`, `scripts/phase9/subdivision_control.py`; results
`results/phase9/subdivision_test.json`, `results/phase9/subdivision_control.json`.

**Claim tested.** Replace every weight-w edge of a vertex's minimal weighted graph (§14) by a path of w unit edges.
The vertex's metric is the restriction of the path metric of this unweighted graph G* on N ≥ n nodes. Is d(G*) an
extreme ray of the metric cone MET_N (exact: tight triangle rows of rank C(N,2) − 1)?

**Result on m_8.** Yes for all 532 non-cut orbits (N from 5 to 67), for a suitable switching. With the
simplest-alphabet switching 531 pass; orbit 165 (D = 7) fails there (corank 2) and passes with 14 of its 15 other
valid switchings. Also yes for all 12 non-cut orbits of m_7 and the 3 of m_5, m_6.

**Control.** 30 non-vertices of m_8 (sibling extensions from the §11 generator, D = 3..6), all 128 switchings tried,
N ≤ 36: 20 also have a switching whose subdivision is an extreme ray; 10 do not (smallest corank 2 to 4).

**Reading.** The property is not a characterisation: two thirds of the sampled non-vertices have it too, so "is a
restriction of an unweighted graph vertex" does not select vertices. It fits the literature's picture that graphic
extreme rays are very abundant (Avis 1980, Theorems 3.3 and 3.5; checked against the source, see §20). It is a true statement about m_8 but not a
rule. What would make it one is a condition on the pair (G*, node subset) that guarantees the restriction is a
vertex; that is the peel problem of §10–§13 in other words.

## 18. Family study, round 18: conditions for the {1,2}-weighted rays (2026-11-25)

Setup `scripts/phase9/family12.py`, judge `scripts/phase9/judge_family.py`, briefs and agent folders
`phase9/round_18/`, verdicts `results/phase9/round_18_family.json` / `.md`.

**The family.** Extreme rays of MET_k whose minimal graph has weights in {1, 2}. Complete lists for k = 5..8:
1, 3, 28, 925 (of 1, 3, 33, 3,751 rays in all). From the full m_9 graph run (below): 5,520 orbits with weights {1}
and 23,645 with {1, 2}, giving 27,963 distinct graphs on 9 nodes, all re-confirmed as rays.

**Full m_9 graph run** (`graph_families.py --all9`, chunks in `checkpoints/phase9/gfam9/`): 1,055,145 cut-adjacent
orbits, 1,221 not. 1,273 weight sets occur (the 20,000 sample showed 270), 48 of them intervals carrying 89.5% of the
orbits; largest weight 21; most common set {2, 3, 4} (217,616 orbits); unweighted 0.52%, {1, 2} 2.2%. The orbits sit
on 31,061 distinct underlying graphs (1,052,364 weighted graphs): 33.9 weightings per graph on average, median 7,
maximum 2,177; 5,910 graphs carry one weighting; 2,463 graphs with 100 or more carry 640,607 of the weightings
(`results/phase9/graph_families_m9all.json`). The first run's grouping step scanned all weightings of a graph per
orbit and was stopped after 100 minutes; indexed by weighted hash it takes 5 minutes.

**Round.** The maker proposed 8 conditions; the breaker built 46,436 new rays (8,011 / 21,487 / 16,938 on 9 / 10 / 11
nodes) and 6,345 non-rays on 9–11 nodes. The judge tested every claim on 28,920 data rays, 3,674 public and 3,670
held-out non-rays, and all 52,781 breaker objects (each checked exactly). No submitted claim was broken.

| claim | kind | data rays accepted | data non-rays rejected | breaker rays accepted | breaker non-rays rejected |
|---|---|---|---|---|---|
| 01 unit rectangle class | sufficient | 3.3% | 100% | 10.4% | 100% |
| 02 rectangle propagation | sufficient | 43.9% | 100% | 72.0% | 100% |
| 03 exchange closure | sufficient | 99.74% | 100% | 99.90% | 100% |
| 04 unweighted closure | necessary (conjecture) | 100% | 18% | 100% | 24% |
| 05 split-prime | necessary | 100% | 67% | 100% | 53% |
| 06 geodesic exchange connected | necessary | 100% | 74% | 100% | 58% |
| 07 exchange quotient connected | necessary | 100% | 57% | 100% | 48% |
| 08 = 2-connected + 05 + 06 + 07 | necessary | 100% | 92% | 100% | 87% |

**The idea.** A solution of the tight system is fixed by its values on the edges, and the constraints are "two
geodesics of the same pair have equal length". A geodesic rectangle forces opposite sides equal; an odd closed chain
of such exchanges forces two pair-classes equal; then a tight triple with one unknown class determines it. Claim 03
says: if these three deductions determine everything, the graph is a ray. It is sound for every k and every weight
set (each step is a consequence of tight equalities).

**No iff.** "Ray iff the closure of 03 succeeds" holds for all 957 rays with k ≤ 8 and fails at k = 9: 76 of the
27,963 data rays, and 46 of the breaker's 46,436 (first found independently by the breaker, 12 submitted). The misses
have weight-2 edges and need three relations combined; the closure combines two. So the same pattern as the rest of
Phase 9 appears inside the simplest weighted family: the rule is complete through n = 8 and exceptions start at n = 9.

**Reservations.** (a) 02, 03, 04, 07 are restricted deduction procedures on the tight relations, not static graph
properties: 03 is an incomplete linear solver, which is why it is sound and why it cannot be an iff. The claims free
of this are 01, 05, 06. (b) 04 is a conjecture with no proof (unweighted rays only: 5,519 in the data). (c) Proofs
are sketches in the file docstrings; 05 quotes Bandelt–Dress from memory. (d) Non-rays are perturbations of rays, a
biased sample. (e) Both agents slightly exceeded a compute rule (maker: one command 5 min 46 s; breaker: 25 min
total).

## 19. Side experiment: elliptope distance (2026-11-25)

`scripts/phase9/elliptope.py`, `results/phase9/elliptope.md`. Y = J − 2X, λ = λ_min(Y) (orbit invariant; λ ≥ 0 iff in
the elliptope), on m_7, m_8 and the 1,000 m_9 targets, split by reached / unreached after round 17. Only the cut has
λ ≥ 0. n = 8: reached median −0.41 (range −1.33..0), unreached −0.39 (−0.58..−0.27). n = 9: reached −0.45
(−0.85..−0.25), unreached −0.44 (−0.75..−0.20). P(unreached below reached) = 0.43 and 0.47; 0.46 within equal
denominators. The most negative orbits are reached ones. **No extra signal**; ledger note added to `rules.md`, no rule
proposed. Denominators do separate the groups (n = 9: D = 13: 116 of 127 unreached; D = 16: 59 of 59; D = 9: 0 of 87).

## 20. A counting theorem: small-choice rules have infinitely many exceptions (2026-11-25)

**Source, read directly** (D. Avis, *On the extreme rays of the metric cone*, Canad. J. Math. 32 (1980) 126–144):
- Theorem 3.3: for 0 < ε < 1/5 and n^(−1/5+ε) ≤ p ≤ 1 − n^(−1/4+ε), Prob(G_{n,p} induces an extreme ray) = 1 − o(1).
  Remark after the proof (p. 138): with p = 1/2 "there are 2^C(n,2) (1 − o(1)) distinct extreme rays".
- Theorem 2.4: if G is 1-ic-colorable (all edges in one class under "opposite edges of an even isometric cycle"),
  d_G is an extreme ray. The converse is false (Fig. 2.3); adding merge steps, "it is beginning to look like we are
  back to solving the original system of tight constraints" (p. 132–133). Round 18's claims 01–03 are this procedure
  and its extensions, and round 18 reached the same end.
- Theorem 3.5: every rational metric on m points is the restriction of an extreme ray on some n ≥ m points. This is
  why the subdivision property of §17 cannot characterise vertices.
- Theorem 3.2: dense m-partite graphs (parts ≥ 3, few missing edges) induce extreme rays; 10^C(n,2) labelled graphs
  on 3n points from this alone.

**From rays to orbits of m_n.** A ray d of MET_n scaled to x = 2d/τ (τ the largest triangle perimeter) is a vertex
of m_n: the tight triangle equalities have rank C(n,2) − 1 and vanish on x, the tight perimeter equality does not.
Distinct labelled graphs give distinct d_G. An orbit of m_n under S_n × switching contains at most n!·2^(n−1) points.
Hence

    (number of orbits of vertices of m_n)  ≥  2^C(n,2) (1 − o(1)) / (n! · 2^(n−1))  =  2^(n²/2 − O(n log n)).

**Theorem (counting).** Let a generator consist of a finite list of exceptions and finitely many rules, each of which
takes an object on n − 1 nodes (a vertex or any intermediate point) and a choice among at most 2^b(n) alternatives and
returns an object on n nodes. If b(n) ≤ (1 − δ)·n for some δ > 0 and all large n, the generator produces at most
2^((1−δ)n²/2 + O(n)) objects on n nodes, so the share of orbits of m_n it reaches tends to 0. In particular it has
infinitely many exceptions at every large n, not finitely many.

*Proof.* If N(n) is the number of objects on n nodes, N(n) ≤ r·2^b(n)·N(n − 1) + e with r rules and e exceptions;
iterate and compare with the lower bound above. ∎

**What it covers.** Every rule type of rounds 1–17 (a bounded or polynomial choice per added node: b(n) = O(log n)),
the fiber generator of §11 for a fixed denominator, and any "family with boundedly many parameters". For these,
"finitely many rules plus finitely many exceptions" is impossible, and the measured growth (13, 533, 1,056,367) is
the beginning of it.

**What it does not cover.** Rules whose choice has about n bits per added node, i.e. rules that take a whole graph
(or weighted graph) as input. There the opposite holds for the unweighted family: the one rule "x = 2 d_G / τ" is
correct for almost all graphs. But (a) deciding *which* graphs is the tight-system rank, with no combinatorial
characterisation known (Avis; round 18); (b) at n = 9 unweighted graphs give 0.52% of the orbits, and whether
weighted rays outnumber graphic ones asymptotically is not known to us (upper bound on all vertices: 2^O(n² log n)).

**Answer to "finite rules or infinite exceptions".** For rules with a small choice per node: infinite exceptions,
proved. For rules that take a graph as input: the rule is the definition (tight rank), and the question becomes
whether a finite *combinatorial* test replaces the rank; §21 measures that.

## 21. Locality: how many nodes a rule must inspect at once (2026-11-25)

`scripts/phase9/locality.py`, `results/phase9/locality.md` / `.json` (116 s, exact arithmetic).

**Measure.** For a ray d on k nodes, the level-s closure solves, for every s-subset W of nodes, the tight triangle
equalities inside W exactly, merges the pairs they force to be proportional, and repeats over all W to a fixpoint.
L(d) is the smallest s at which everything is merged. The closure at s + 1 contains the one at s and s = k is the
definition, so 4 ≤ L ≤ k. Any rule that examines at most s nodes at a time, with unlimited propagation between the
examinations, certifies only rays with L ≤ s. (Level 4 already contains Avis's ic-colouring for 4-cycles and all of
round 18's closure: the 88 rays missed there have L = 4 or 5.)

**All weights (vertices of m_n as rays, simplest switching).**

| n | orbits | L = 4 | 5 | 6 | 7 | 8 | mean L |
|---|---|---|---|---|---|---|---|
| 7 | 12 (all) | 12 | | | | | 4.00 |
| 8 | 532 (all) | 403 | 124 | 4 | 1 | | 4.27 |
| 9 | 30,008 (sample, k = 9 only) | 8,778 | 14,458 | 6,123 | 629 | 20 | 4.96 |

Share certified by 4-node inspection: 100%, 76%, 29%. Largest L: 4, 7, 8, i.e. n − 1 at n = 8 and n = 9.

**Family {1,2}.** k ≤ 7: all L = 4. k = 8 (complete, 925): 916 at 4, 9 at 5. k = 9 (27,963 from m_9): 27,177 at 4,
780 at 5, 5 at 6, 1 at 7. The breaker's constructed rays on 10 and 11 nodes are almost all L = 4 (99.2%, 99.6%),
as expected from local constructions; they say nothing about typical rays.

**Reading.** The number of nodes a rule must see at once grows with n: one more node adds about 0.3 then 0.7 to the
mean, the 4-node rules lose 24% and then 71% of the orbits, and the worst case tracks n − 1. A fixed finite set of
local rules (any fixed s) is therefore complete at n = 7 only, and by §20's Theorem 3.5 of Avis (any rational metric
embeds in a ray) there is no reason for L to stay bounded. This is the "rules keep growing" side, measured: at every
n there are orbits whose proof needs nearly the whole tight system. No ray in the data has L = k.

**Limits.** n = 9 is a 2.9% sample (the largest L on the full list could be 9); one switching per orbit, and L may
depend on the switching; L is defined through this closure, and a cleverer bounded rule could do better on some
rays, though none can beat the full system on s nodes. Unbounded growth of L with n is observed for n = 7, 8, 9 and
is not proved.
