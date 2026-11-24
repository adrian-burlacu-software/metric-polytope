# Phase 9 — Rule maker brief (round 14)

You propose new rules for the metric-polytope rule language, the DSL. Your proposals count only when the judge
(`scripts/phase9/judge.py`) confirms them in code. Nothing you claim is accepted on your word.

## Goal
Make as many currently **unreachable** orbits reachable as possible. The targets are:
- all orbits of m_7 (13) and m_8 (533);
- 1,000 seeded orbits of the n = 9 sample.

The current unreached targets are in `results/phase9/unreached_targets.json`, with fields n, id, D, nums and key;
a point is x = nums / D, over the pairs in lexicographic order. That file also covers the 128k unreached sub-orbits
(restrictions of targets) in `results/phase9/unreached_nodes.json`, by canonical key. At the start of this round:
n = 8: 30 of 533 unreached; n = 9: 555 of 1,000 (the file also lists breaker points at n = 9). Accepted so far:
moves partial-dup, dup-midshift, radial-lowend, dup-thirdshift; base families gen-bipartite-glue (round 10),
gen-house-c4-d11 and gen-house-p4-d11 (round 11), gen-dyadic-tower-w1 and gen-dyadic-tower-w2 (round 12).

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

## Round 14 aim: the partly reached targets (group C), with moves
Profile after round 13 (`results/phase9/shadow_ladder_n9.json`, `_n8.json`; per target: `largest_reached_restriction`,
`reached_restrictions_by_size`, `blockers`):
- n = 9: 555 unreached. **87 have a reached restriction** (largest reached restriction on 3 nodes: 41, 4: 7, 5: 20,
  6: 17, 7: 2). Every one has a denominator divisible by 3: D = 15: 31, 12: 19, 18: 14, 21: 11, 9: 5, 27: 3, 24: 3,
  10: 1. The other 468 have nothing reached and need new base pieces at n = 9 itself; they are not this round's aim.
- n = 8: 30 unreached; 8 have a reached restriction (D = 9: 7, on 3 nodes; D = 12: 1, on 5 nodes).

Rounds 10–13 showed that new base families tend to work at one n only. Moves apply at every n, and these 95 targets are
the only unreached ones a move can still reach (main-track moves keep their input as a restriction, so a move needs
a reached restriction to start from). So this round is about **moves** (generative rules are allowed too).

Round 7 found `radial-lowend` and `dup-thirdshift` exactly this way; read `phase9/round_07/maker/NOTES.md` and reuse
its method and scripts:
- fc.py: for each target, take the unreached restrictions Z one node above a reached restriction Y = Z − v (the
  "frontier pairs"), and find the face of the fiber over Y that contains Z's new column (vertex, edge midpoint, a
  third of an edge, ...);
- sim3.py: a fast exact simulation of the reach cascade with a candidate column generator added, started from
  `checkpoints/phase9/reached.json`, to measure the gain before writing the DSL move;
- timing7.py: the cost per input.

Tasks:
1. Classify the frontier columns of the 87 + 8 targets. The prime 3 is in every denominator, so look for column rules
   involving thirds (a point at 1/3 or 2/3 of a fiber edge, thirds of radial values, shifts by 1/3 of an interval).
   Note which targets are blocked at the 3-node level (41 at n = 9): there the first step out of a reached triangle
   already fails.
2. Turn the best column rules into cheap, G-equivariant moves (`:grow 1` preferred) and measure their gain with the
   simulation before proposing.
3. **Cost matters most.** The judge applies a move forward to every reached sub-orbit, and the reached set is large.
   Round 7's accepted moves cost about 0.26 s per 8-node input; `dup-recentre` at 1.37 s was dropped at both 300 s and
   900 s. Stay at or below about 0.3 s per 8-node input and report the timing.

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
At most 8 proposals. Each one goes in its own file `phase9/round_14/maker/NN_name.mpr` and defines **exactly one**
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
- Write only inside `phase9/round_14/maker/`. Don't edit `rules/`, `results/`, `checkpoints/`, `scripts/` or
  `metricpoly/`.
- Compute: keep any single command under 5 minutes, use at most 4 processes, and use at most about 20 minutes of
  compute in total. Don't run the judge yourself.
- For every proposal, add a line to `phase9/round_14/maker/NOTES.md` with: the file, a one-line reason, and what
  `try_rule.py` reported (`hits_unreached_nodes` per n). Be honest: a proposal with 0 hits will very likely be
  dropped.
- Finish with a short summary: what you proposed, why, and the try_rule evidence.
