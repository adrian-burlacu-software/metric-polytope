# Ladder semantics for Phase 9 rules (proposal, 2026-11-23)

Purpose: say exactly what "rule R breaks at rung k between m_n and m_{n+1}" means, so that the Phase 10 ladder can
locate breaks more finely than "between n and n+1". Status: approved 2026-11-23; **outcome below: Definition 1 does not localise breaks; replaced by the restriction profile.**

## The rungs (from `metricpoly/ladder.py`)

Nodes K = {0..n-1} plus a new node w. Rung k (0 ≤ k ≤ n) has the graph G_k = complete graph on K, plus w joined to
N = {0..k-1}. P_k = projection of m_{n+1} onto the edges of G_k. P_0 = m_n (w isolated), P_n = m_{n+1}.

## Three facts the definitions rest on

- **F1 (gluing).** G_k is the clique sum of K_K and K_{N+w} over the clique N. So P_k is cut out by the triangle
  inequalities inside K and inside N ∪ {w} (verified in code, `scripts/phase10/verify_rungs.py`). Equivalently:
  y ∈ P_k ⇔ y|K ∈ m_n and y|(N∪w) ∈ m_{k+1}. A rung point is exactly a gluing of a point of m_n and a point of
  m_{k+1} along N.
- **F2 (shadows).** P_k is a linear image of m_{n+1}, so every vertex of P_k is the shadow x|G_k of at least one
  vertex x of m_{n+1}.
- **F3 (edge steps).** The fiber of P_k over a point of P_{k-1} is an interval (one new edge). A vertex of P_k is
  an endpoint of the interval over its own shadow in P_{k-1}.

## Definition 1: generative rules (reachability; the main Phase 9 game)

Fix a rule set R (base pieces + moves) and the Phase 9 engine (`metricpoly/reach.py`). For a vertex y of P_k:

- k < n: y is **R-reached** iff both pieces are R-reached nodes:
  - y|K, a point of m_n;
  - y|(N ∪ w), a point of m_{k+1}. Pieces on ≤ 2 nodes count as reached.

  Either piece may be a non-vertex. That is allowed exactly as Phase 9 allows detours, and the vertex-only variants
  require vertex pieces.
- k = n: P_n = m_{n+1}, so this is Phase 9 itself.

**Rung k is covered** iff every vertex orbit of P_k is R-reached. **R breaks at rung k** = the smallest uncovered k.

How to read it:
- A break at k < n means the new node's partial attachment already produces a piece that R cannot build. The
  failure is on smaller polytopes: m_{k+1}, or a non-vertex point of m_n.
- A break only at k = n means every partial attachment is fine and the failure is the last gluing step.

This adds no move to R, and Phase 9 verdicts at n and n+1 are unchanged. It only localises them.

## Definition 2: structural rules

A rule gets a rung version only if its statement makes sense for a vertex of a projected polytope. The rung
version uses the same quantities, with G_k in place of K_n:
- C(n,2) → |E(G_k)|;
- triangles → triangles of G_k;
- cuts → restrictions of cuts to G_k;
- skeleton → skeleton of P_k (neighbours: `ladder.py`).

| rule | rung version | note |
|---|---|---|
| cuts-are-the-integral-vertices, no-half-integral | on y | coordinates only |
| no-simple-vertex | tight count = \|E(G_k)\| on y | breaks between 7 and 8 |
| incidence-bounds | bounds in G_k's triangles | the bound constants need rederiving per rung |
| third-valued-is-graphic | on y | "graphic" for partial points: y = (2/τ) d_H restricted to G_k |
| dominating-set, at-least-two-cuts, no-cut-set, switch-class-nonadjacent | skeleton of P_k | adjacency rules |
| extension-denominator, denominator-lemma-lift/-glue | on y with node deletions inside G_k | |
| fractal-*, finite-middle-vocabulary, projects-to-smaller-vertex, lift-fiber-complete, three-projections-imply-vertex | **no rung version** | about block structure or projections of complete metrics; evaluated only at n and n+1 |
| vertex-moves-cover(-M1), all-moves-cover(-vertex-only), denominator-prime-bound | Definition 1 | generative |

## What exists and what would be computed

- Ladders, complete: n = 5→6 (`checkpoints/phase10/ladder_n6`, rung orbits 2,2,2,3,3,3) and n = 6→7
  (`ladder_n7`: 3,4,6,10,20,17,13).
- n = 7→8 (`ladder_n8`): only rungs 0–1. This is where all-moves-cover, no-simple-vertex and fractal-structured
  break, so rungs 2–7 are needed. The cost must be estimated first.
- Engine work: add the rung pieces as Phase 9 targets and evaluate them with the current accepted rule set. Every
  verdict is exact.

## Outcome (2026-11-23)

**Definition 1 on all rung vertices, 6→7 ladder** (`scripts/phase9/ladder_eval.py`, `results/phase9/ladder_eval_n7.json`).
The bottom-up search used for the main track agreed with the engine on 40/40 validation nodes.

| rung k | 0 | 1 | 2 | 3 | 4 | 5 | 6 (= m_7) |
|---|---|---|---|---|---|---|---|
| unreached orbits (main and detour) | 0/3 | 0/4 | 4/6 | 2/10 | 3/20 | 3/17 | 0/13 |
| unreached orbits (vertex-only) | 0/3 | 0/4 | 4/6 | 2/10 | 7/20 | 5/17 | 1/13 |

The "break" at rung 2 is an artifact. Every failing piece is a non-vertex point, either with a zero coordinate (two
coinciding nodes) or with denominator 4, 6 or 7, and no derivation of an m_7 vertex needs it: all 13 m_7 orbits are
reached at rung 6.

**Definition 1 along each unreached target's own ladder** (`scripts/phase9/shadow_ladder.py`,
`results/phase9/shadow_ladder_n8.json`). For each new node w the pieces are restrictions of the target, which have
exact engine verdicts. All 120 unreached m_8 targets break at rung 0: for every w, x minus w is unreached and is not
a vertex. So the ladder does not localise anything for these targets.

**What does localise: the restriction profile** (largest reached restriction of each unreached m_8 target).

| largest reached restriction | targets | denominators | odd primes |
|---|---|---|---|
| none (not even 3 nodes) | 91 | 8: 49, 11: 18, 13: 16, 14: 4, 7: 3, 10: 1 | none (dyadic): 49; 11: 18; 13: 16; 7: 7; 5: 1 |
| 3 nodes | 7 | 9: 7 | 3 |
| 4 nodes | 1 | 10 | 5 |
| 5 nodes | 21 | 10: 15, 12: 4, 6: 2 | 5: 15; 3: 6 |

Main-track moves keep their input as a restriction, so a target with no reached restriction can only become reachable
through a new base piece at some restriction of it.

Decision: round 7 is aimed by this profile, not by rungs. The ladder stays available, but it is not a localisation
tool for the generative rules.
