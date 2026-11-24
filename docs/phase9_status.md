# Phase 9 status after round 15 (2026-11-24)

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
| 15 | **22 (4.1%)** | **515 (51.5%)** | move twin-dup-blend (retry) |

Rounds 1–4, 9 and 13 accepted nothing on the main track. Round 1's scaled graph metrics and round 3's
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

All six put the new node on a low-dimensional face of the one-node fiber, mostly an edge, at a simple rational
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
| m_9 | 515 | 468 | 47 |

The **denominator lemma** (`docs/denominator_lemma.md`) sharpens this. Moves multiply denominators by at most 2. If
an odd prime p divides a target's denominator, some restriction carrying p must be a base piece. Of the 47 partly
reached m_9 targets:
- 38 carry the prime 5 or 7, and per round 14's analysis most of those have no reached restriction carrying that
  prime;
- only 9 have a denominator built from 2 and 3 alone (12, 18, 24, 27).

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
generative picture breaks at the base: about 47% of the m_9 sample would need base pieces that are new at n = 9.

## 5. What is left

**m_8: 22 unreached.** None has a reached restriction.

| D | 11 | 7 or 14 | 13 | 8 | 10 |
|---|---|---|---|---|---|
| targets | 10 | 7 | 2 | 2 | 1 |

- D = 11: ids 93, 140, 159, 167, 215, 229, 470 and 504 have no cover by two scaled graph metrics.
- D = 8: the 2 targets need cores of their own (round 12).

**m_9: 515 unreached.**
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
- Partly reached: 47. The largest reached restriction has 3 nodes for 29 of them, 4 for 2, 5 for 7, 6 for 8 and 7
  for 1.

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

## 8. Directions not yet tried

1. **Base pieces at n = 9, built targets-first** for D = 11 and 13 (214 targets). The risk is narrow, n-specific
   families, as in rounds 10–12.
2. **A move that brings in the prime 5 or 7** for the 38 partly reached m_9 targets with D = 15 or 21. It would have
   to introduce the prime without breaking the restriction rule, for example a radial value with a fifth.
3. **Higher-dimensional fiber faces**, for the 9 remaining 2,3-denominator targets: centroids of 2-faces. Round 14
   found 19 targets in simulation but at O(n³) columns per input.
4. **Accept the barrier as the result.** Document that the generative description of m_n needs new base pieces at
   each n, and measure how that set grows from m_8 to m_9.
