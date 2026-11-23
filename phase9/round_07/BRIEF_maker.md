# Phase 9 — Rule maker brief (round 07)

You propose new rules for the metric-polytope rule language, the DSL. Your proposals count only when the judge
(`scripts/phase9/judge.py`) confirms them in code. Nothing you claim is accepted on your word.

## Goal
Make as many currently **unreachable** orbits reachable as possible. The targets are:
- all orbits of m_7 (13) and m_8 (533);
- 1,000 seeded orbits of the n = 9 sample.

The current unreached targets are in `results/phase9/unreached_targets.json`, with fields n, id, D, nums and key;
a point is x = nums / D, over the pairs in lexicographic order. That file also covers the 128k unreached sub-orbits
(restrictions of targets) in `results/phase9/unreached_nodes.json`, by canonical key. At the start of this round:
n = 8: 120 of 533 unreached; n = 9: 628 of 1,000. Accepted moves so far: partial-dup, dup-midshift.

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

## Round 7 aim (from the restriction profile; read this before proposing)
For every unreached target we computed its largest reached restriction (the largest node subset T, T ≠ all nodes,
with x|T reached). Data: `results/phase9/shadow_ladder_n8.json` and `results/phase9/shadow_ladder_n9.json`; each row
has `orbit` (n = 8: Deza orbit index; n = 9: row of data/deza/orbits9), `D`, `odd_primes`,
`largest_reached_restriction`, `reached_restrictions_by_size`.

Every main-track move keeps its input as a restriction. So a target with **no reached restriction at all** can only be
reached if a new **base piece** appears among its restrictions (or is the target itself). A new move cannot help it.

| group | n = 8 | n = 9 | what is needed |
|---|---|---|---|
| A: nothing reached, no odd prime (dyadic) | 49 (all D = 8) | 89 (D = 8, 16) | base families with denominators 4, 8, 16 |
| B: nothing reached, odd prime p | 42 (p = 11: 18, 13: 16, 7: 7, 5: 1) | 413 (13: 128, 11: 114, 7: 67, 5: 33, 17: 27, 19: 21, 23: 6, 31: 1, other 16) | base families carrying p |
| C: reached up to 3–7 nodes | 29 (21 blocked above 5 nodes; D = 10, 12, 9, 6) | 126 (D mostly 10–18, primes 3, 5) | moves that grow the reached pieces |

Priorities: **group B at n = 8 first**: 34 targets with D = 11 or 13 (note 11 = 2n - 5, 13 = 2n - 3 at n = 8). By the
denominator lemma, p must enter through a base piece; ask what vertex family on k nodes has denominator 2k - 3 or
2k - 5 and occurs as a restriction of those targets. Then group A (dyadic). Then group C.
At n = 9, primes 17, 19, 23, 31 exceed 2n - 3 = 15: by `denominator-prime-bound`, no derivation from the current base
reaches them, so they need a base family that carries those primes at n = 9 itself.
Look at the actual targets: pull a few from `results/phase9/unreached_targets.json` and look at their restrictions with
`check_point.py`.

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
At most 8 proposals. Each one goes in its own file `phase9/round_07/maker/NN_name.mpr` and defines **exactly one**
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
- New base pieces are cheap to judge: they only propagate through cached data. Prefer them.
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
- Write only inside `phase9/round_07/maker/`. Don't edit `rules/`, `results/`, `checkpoints/`, `scripts/` or
  `metricpoly/`.
- Compute: keep any single command under 5 minutes, use at most 4 processes, and use at most about 15 minutes of
  compute in total. Don't run the judge yourself.
- For every proposal, add a line to `phase9/round_07/maker/NOTES.md` with: the file, a one-line reason, and what
  `try_rule.py` reported (`hits_unreached_nodes` per n). Be honest: a proposal with 0 hits will very likely be
  dropped.
- Finish with a short summary: what you proposed, why, and the try_rule evidence.
