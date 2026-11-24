# Phase 9 — Rule maker brief (round 16, track A)

You propose new rules for the metric-polytope rule language, the DSL. Your proposals count only when the judge
(`scripts/phase9/judge.py`) confirms them in code. Nothing you claim is accepted on your word.

## Goal
Make as many currently **unreachable** orbits reachable as possible. The targets are:
- all orbits of m_7 (13) and m_8 (533);
- 1,000 seeded orbits of the n = 9 sample.

The current unreached targets are in `results/phase9/unreached_targets.json`, with fields n, id, D, nums and key;
a point is x = nums / D, over the pairs in lexicographic order. That file also covers the 128k unreached sub-orbits
(restrictions of targets) in `results/phase9/unreached_nodes.json`, by canonical key. At the start of this round:
n = 8: 22 of 533 unreached; n = 9: 515 of 1,000 (the file also lists breaker points at n = 9). Accepted so far:
moves partial-dup, dup-midshift, radial-lowend, dup-thirdshift, twin-dup-third, twin-dup-blend; base families
gen-bipartite-glue, gen-house-c4-d11, gen-house-p4-d11, gen-dyadic-tower-w1, gen-dyadic-tower-w2.
**Read `docs/phase9_status.md` first**: it summarises rounds 1–15, what each rule reaches, and where the shortcuts break.

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

## Round 16, track A: base pieces at n = 9, built targets-first (D = 11 and D = 13)
At n = 9, 468 of the 515 unreached targets have no reached restriction (`results/phase9/shadow_ladder_n9.json`), so
only base pieces at n = 9 itself can reach them. The largest groups: **D = 13: 116, D = 11: 98**.

What is known (see `docs/phase9_status.md` §4.3 and the round folders):
- Round 11's house families (`phase9/round_11/maker/`) are defined at every n with scale 2n − 5 (= 13 at n = 9). At
  n = 9 they produce 305 new vertex orbits but reach only 8 targets, so they were built from the n = 8 targets and
  do not aim at the n = 9 ones.
- Round 7 (`phase9/round_07/maker/NOTES.md`): at n = 8 the odd-D targets are x = (2/D)·d for integer metrics d that
  are never graph metrics. At n = 9, no 8-node restriction of a D = 11 or 13 target is a scaled graph metric.
- Every 8-node restriction of these targets is unreached; it is either a non-vertex or one of the few unreached m_8
  vertices.

Task: start from the n = 9 targets themselves. Find structure shared by many of them, such as integer metric d, value
sets, a decomposition into glued scaled graph metrics (round 8's cover.py and round 11's stage.py), or a common core
plus attachments. Then build an open-ended family (scale a function of n) that generates those vertices directly.
Success means **new n = 9 targets** reached. Generation must finish n = 9 in try_rule within about 10 minutes
(`--ns 9`; single commands may run up to 10 minutes for this). A family that reaches only a handful of targets will be
flagged as narrow: say honestly how many targets each family reaches and how it was derived.

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
At most 2 proposals. Each one goes in its own file `phase9/round_16/maker/ANN_name.mpr` (prefix A, e.g. `A01_name.mpr`) and defines **exactly one**
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
- Round 16 has three makers working in parallel (tracks A, B, C) in the same folder. Write only files with your prefix
  `A` (proposals, NOTES_A.md) and put scripts and scratch output in `phase9/round_16/maker/A_work/`. Never touch
  the other tracks' files.
- Write only inside `phase9/round_16/maker/`. Don't edit `rules/`, `results/`, `checkpoints/`, `scripts/` or
  `metricpoly/`.
- Compute: keep any single command under 5 minutes, use at most 3 processes (two other makers run
  at the same time), and use at most about 20 minutes of compute in total. Keep memory under about 8 GB. Don't run the judge yourself.
- For every proposal, add a line to `phase9/round_16/maker/NOTES_A.md` with: the file, a one-line reason, and what
  `try_rule.py` reported (`hits_unreached_nodes` per n). Be honest: a proposal with 0 hits will very likely be
  dropped.
- Finish with a short summary: what you proposed, why, and the try_rule evidence.
