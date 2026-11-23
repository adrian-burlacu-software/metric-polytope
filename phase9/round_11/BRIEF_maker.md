# Phase 9 — Rule maker brief (round 11)

You propose new rules for the metric-polytope rule language, the DSL. Your proposals count only when the judge
(`scripts/phase9/judge.py`) confirms them in code. Nothing you claim is accepted on your word.

## Goal
Make as many currently **unreachable** orbits reachable as possible. The targets are:
- all orbits of m_7 (13) and m_8 (533);
- 1,000 seeded orbits of the n = 9 sample.

The current unreached targets are in `results/phase9/unreached_targets.json`, with fields n, id, D, nums and key;
a point is x = nums / D, over the pairs in lexicographic order. That file also covers the 128k unreached sub-orbits
(restrictions of targets) in `results/phase9/unreached_nodes.json`, by canonical key. At the start of this round:
n = 8: 85 of 533 unreached; n = 9: 578 of 1,000. Accepted so far: moves partial-dup, dup-midshift, radial-lowend, dup-thirdshift; base family gen-bipartite-glue (round 10).

## How reachability works (the judge's engine, `metricpoly/reach.py`)
- **Base pieces:** cuts; anticuts; complete multipartite (1/3)d(G), with or without one edge removed; tree
  suspensions; Avis paths; and **all graph metrics** x_G = (2/τ)·d_G. A new base piece must therefore be something
  that is not a graph metric.
- **Moves:** lift (vertex of the fiber when one node is added), radial Λ^1–Λ^3, and gluing with any overlap.
  Intermediate points may be non-vertices.
- An orbit is reached if some chain of moves from base pieces produces it. Every intermediate point is a
  restriction of the target, so your rule helps only if it hits unreached sub-orbits.
- **Useful theory:** `docs/denominator_lemma.md`. Moves multiply denominators by at most 2. So if an odd prime p
  divides den(x), some restriction x|T with p | den(x|T) must itself be a base piece. Targeted seeds therefore need
  that prime in their denominator.

## Round 11 aim: base families, following the pattern that worked in round 10
Round 10 accepted `gen-bipartite-glue` (`rules/phase9_accepted.mpr`; source and analysis in `phase9/round_08/maker/`,
see its NOTES.md). It is the vertices of the one-node glue fiber of (4/(2n-3))·d(K_{2,n-5}) and (5/(2n-3))·d(C_4).
At n = 8 it gave 14 new base orbits, exactly 14 of the 16 D = 13 targets, and 11 D = 13 targets at n = 9 through
those pieces. Its weakness is cost: it enumerates the whole fiber (35,718 points, 267 s at n = 8, of which only 168
are vertices), and n = 9 did not finish within the judge's 900 s generation allowance. The judge generates families
one n at a time and judges them on the sizes that finish.

Current profile (`results/phase9/shadow_ladder_n8.json`, `_n9.json`): n = 8 has 85 unreached targets, 77 with no
reached restriction at all: D = 8: 49 (dyadic), D = 11: 18, D = 7 or 14: 7, D = 13: 2, D = 10: 1. n = 9 has 578, 491
with nothing reached.

Tasks, in priority order (proposals must be generative rules; no moves):
1. **D = 11 (18 targets at n = 8, 114 at n = 9).** Round 8's maker found one-node covers by scaled graph metrics for
   10 of 18: K_{2,3} at 4/11 + C_4 at 4/11 (6 targets), K_{2,3} at 4/11 + P_4 at 3/11 (6), a 6-node piece at 4/11 + a
   3-node path (5); ids 93, 140, 159, 167, 215, 229, 470, 504 have no such cover. Build sister families of
   gen-bipartite-glue. Aim for scales that are a function of n (11 = 2n - 5 at n = 8).
2. **A cheap version of the D = 13 family**, so n = 9 can be generated. Build the vertex orbits directly instead of
   enumerating the fiber: for example, characterise which fiber points are m_n vertices (the 168 of 35,718) and
   construct only those, or enumerate fiber vertices with a cheaper primitive. Submit it as a new generative rule.
   Duplicate base orbits are harmless.
3. **Stretch: the dyadic D = 8 group (49 targets).** 40 of 49 take values {2, …, 6}/8 with edge weights {2, 3}
   (round 7 maker notes).
Keep each family's generation under about 5 minutes at n = 8 in try_rule (`--ns 3-8`, and n = 9 if feasible).

## Hard rules (decided by the user after round 1)
- **Base pieces must be true vertices of m_k.** The judge discards every generated point that isn't an exact vertex.
  The existing graph-metric base is the only non-vertex exception. Intermediate points of a derivation may still be
  non-vertices (detours).
- **Non-vertex seeds** are allowed only as a separate variant. Put `:variant "nonvertex"` in the rule's header. The
  judge evaluates such a rule on a separate state and logs it in `results/phase9/variant_nonvertex.json`; it never
  enters the main numbers.
- **Every n:** the `:domain` must have no upper bound, so write `(lo)`, not `(lo hi)`. A family that only works for
  small n is rejected.
- **Moves must keep their input as a restriction.** Every output of a main-track move must contain its input, up to
  symmetry, on some subset of its nodes; lift, gluing, radial, twin and dup all do. Moves that rescale or otherwise
  change the input's coordinates are rejected on the main track. Without this rule, "unreachable" stops being an
  exact verdict. The judge tests it on probe points, including non-vertices; you may submit such moves only with
  `:variant "nonvertex"`.
- Round 1's `scaled-graph-metrics` (d_G/k, non-vertex) and round 3's `radial-normalized` (which rescales its input)
  now live in the variant. Don't resubmit them to the main track.

## What to propose
At most 8 proposals. Each one goes in its own file `phase9/round_11/maker/NN_name.mpr` and defines **exactly one**
top-level form:
- `(generative NAME (n) :domain (3) :doc "one-line reason" BODY)`: new base pieces, which must be vertices. It must be a
  family defined for every n (open-ended domain), not a single hard-coded point.
- `(move NAME (x) :grow k :doc "one-line reason" BODY)`: a new **unary** move that adds k ≥ 1 nodes.
- `(structural NAME (n) :domain (lo hi) :doc "one-line reason" BODY)`: a claim. It's accepted only if it holds on
  all of the judge's data for n ≤ 8, and the breaker will then attack it.

Keep each rule small. Helper `(define ...)` forms are allowed in the same file. For the language, read
`docs/dsl_grammar.md`, and for idioms `rules/stdlib.mpr`, `rules/literature.mpr`, `rules/mutations.mpr` and
`rules/phase7.mpr`. `gen-lift-multipartite` in mutations.mpr is a worked example of a rule that fixed a break.
Only use primitives that exist; the registry is in `metricpoly/dsl/prims.py` and `metricpoly/dsl/ext/*.py`. You may
NOT add Python primitives.

## Cost (budget: 300 s per proposal; one retry at 900 s if it was still gaining sub-orbits when the budget ran out)
- New base pieces are cheap to judge: they only propagate through cached data. Prefer them. Generating a family
  gets its own one-off allowance of 900 s for n = 3–9 (user decision 2026-11-23); the 300 s budget then applies
  to propagation only.
- New moves are applied forward by the interpreted DSL to every reached sub-orbit, on whole orbits (switching
  classes). That can take seconds per input, so a move that is slow to evaluate will hit the budget and be dropped.
  Keep moves cheap, and G-equivariant if you can.

## Tools (use them; they are exact)
- `.venv/Scripts/python scripts/phase9/try_rule.py FILE.mpr --ns 3-9` loads your file on top of the current rule set
  and reports, for each n: points, exact feasibility, vertices, orbits, and how many hit unreached sub-orbits
  (`hits_unreached_nodes`) and unreached targets.
- `.venv/Scripts/python scripts/phase9/check_point.py FILE.json` gives exact vertex and orbit checks for points you
  build by hand.

## Rules of conduct
- Write only inside `phase9/round_11/maker/`. Don't edit `rules/`, `results/`, `checkpoints/`, `scripts/` or
  `metricpoly/`.
- Compute: keep any single command under 5 minutes, use at most 4 processes, and use at most about 15 minutes of
  compute in total. Don't run the judge yourself.
- For every proposal, add a line to `phase9/round_11/maker/NOTES.md` with: the file, a one-line reason, and what
  `try_rule.py` reported (`hits_unreached_nodes` per n). Be honest: a proposal with 0 hits will very likely be
  dropped.
- Finish with a short summary: what you proposed, why, and the try_rule evidence.
