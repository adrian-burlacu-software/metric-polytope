# Denominator lemma (Phase 8a, parked as-is)

Status: proof written out below at the level of a careful sketch; not refereed. The computer checks are listed
separately at the end and are **not** part of the proof.

## Definitions and assumptions

- A point x ∈ ℚ^{pairs(n)}; den(x) = the least D ≥ 1 with D·x integral. odd(D) = D with all factors 2 removed.
- m_n is cut out by the triangle inequalities x_ij − x_ik − x_jk ≤ 0 and perimeter inequalities x_ij + x_ik + x_jk ≤ 2
  (no box or other families).
- The moves are exactly those implemented in `rules/stdlib.mpr` and `scripts/detour_depth2.py`:
  - **S (symmetry):** permutation of nodes; switching x ↦ 1 − x on a cut δ(S).
  - **T (twin):** add v′ with x_{vv′} = 0, x_{v′a} = x_{va} (then optionally switch v′).
  - **Dup (LP92 duplication):** add v′ copying column i, with x_{iv′} = a = min_j min(2x_ij, 2 − 2x_ij).
  - **R (radial Λ^m, m = 1, 2, 3):** add nodes U with x_{ur} = α, x_{uu′} = 2α, α = max(y)/2; then any switching.
  - **F (fiber moves: lift and gluing).** Given partial data, the output is any **vertex** of the fiber
    F = {z ∈ m_n : z agrees with the data off the hole set H}.
    - Lift: data y on n−1 nodes; holes H = all pairs through the new node v.
    - Gluing: data y_A, y_B on A, B with A ∪ B = [n], K = A ∩ B ≠ ∅, agreeing on K; holes H = pairs {a, b} with
      a ∈ A∖K, b ∈ B∖K. Every overlap size is allowed.
  - Inputs to any move may be arbitrary feasible points (vertices or not): detours are allowed.
- The uniform base set U consists of:
  - cuts and anticuts;
  - complete multipartite (1/3)d(G), with or without one edge removed;
  - tree suspensions (1/3)d(∇T);
  - Avis paths x_{G*};
  - all graph metrics x_G = (2/τ(G))·d_G of connected graphs G, where τ(G) is the largest triangle perimeter of d_G.

## Statements

**Lemma 1 (one step).** For every move above, den(output) divides 2·lcm(den(inputs)).

**Corollary 2 (derivations).** If x is derived from base pieces B_1, …, B_k by a derivation of height h, then
den(x) divides 2^h·lcm(den B_i). In particular odd(den x) divides lcm(odd(den B_i)).

**Lemma 3 (graph-metric denominators).** For a connected graph G on k nodes, τ(G) ≤ 2(k − 1), and den(x_G) divides τ(G).
Hence odd(den x_G) ≤ 2k − 3.

**Theorem 4 (prime-power bound).** If x ∈ m_n is derivable from U by the moves above (any intermediate points), then
every odd prime power p^e exactly dividing den(x) satisfies p^e ≤ 2n − 3.

## Proofs

**Lemma 1.**
- S, T and Dup: coordinates are kept, replaced by 1 − x, or set to 0, x_ij, 2x_ij or 2 − 2x_ij. So den(output)
  divides den(input), or 2·den(input) for Dup's 2x terms when den is odd. In both cases it divides 2·den(input).
- R: α = max(y)/2, so den(output) divides 2·den(y).
- F: let d = lcm(den(data)).
  1. *At most two holes per inequality.* For lift, every hole contains v, and a triple contains at most two pairs
     through v. For gluing, a hole joins A∖K to B∖K. A triple with three holes would need all three of its pairs to
     cross that bipartition, which is impossible for a triangle. So every triangle or perimeter row has at most two
     hole coefficients, each ±1. Its constant term (0 or 2, minus the known coordinates) lies in (1/d)ℤ.
  2. *Full rank.* x is a vertex of F, so the tight rows restricted to the hole columns have full column rank |H|.
  3. *The signed graph.* Form a graph on H: a 1-hole row is an anchor on its hole, and a 2-hole row
     ±z_a ± z_b = c is an edge. In a connected component, fix a spanning tree and a root r. Every hole is then
     z_v = σ_v·z_r + c_v with σ_v = ±1 and c_v ∈ (1/d)ℤ.
  4. *The root is pinned with denominator at most 2d.* Any other row of the component reduces to κ·z_r = c′ with
     κ ∈ {0, ±1, ±2} (±1 only for anchors) and c′ ∈ (1/d)ℤ. Full rank forces some row with κ ≠ 0. Hence
     z_r ∈ (1/2d)ℤ, and therefore so is every z_v.
  5. So den(x) divides 2d. ∎

**Corollary 2.** Induction on the derivation tree, using Lemma 1 at each node. ∎

**Lemma 3.**
- *Bound on τ.* For nodes a, b, c, let S be the smallest subtree of a spanning tree of G that contains a, b, c.
  Every edge of S lies on exactly two of the three tree paths between them, so
  d_S(a,b) + d_S(b,c) + d_S(c,a) = 2|E(S)| ≤ 2(k − 1). Since d_G ≤ d_S, τ ≤ 2(k − 1).
- *Denominator.* x_G = (2/τ)·d_G with d_G integral, so den(x_G) divides τ.
- *Odd part.* If τ is odd then τ ≤ 2k − 3. If τ is even, its odd part is at most τ/2 ≤ k − 1. ∎

**Theorem 4.**
- Moves never delete nodes, so every base piece in a derivation of x ∈ m_n has k ≤ n nodes.
- The odd parts of the base denominators are 1 (cuts, anticuts), 3 (multipartite, suspensions), or at most 2k − 3
  for graph metrics by Lemma 3; Avis paths are graph metrics.
- By Corollary 2, p^e divides the lcm of these odd parts, so it divides one of them, and p^e ≤ 2n − 3. ∎

**What it does *not* say.**
- At n = 8 the bound is 13, and every m_8 orbit satisfies it, yet 266 orbits are unreachable. Arithmetic is not the
  obstruction there.
- Base pieces with denominator 11 exist from n = 7 and with denominator 13 from n = 8, both graph metrics. So
  denominators 11 and 13 are not excluded by arithmetic at n ≤ 9.
- What Corollary 2 *does* force is this: in any derivation of an orbit x with p | den(x), some subset T has p | den(x|T)
  and x|T is itself (up to symmetry) a base piece. That is the handle for targeted seeds.

## Computer checks (separate from the proof)

- **Lemma 1:** 0 violations in 3.29M move instances at n ≤ 8: 3,053,630 gluing, 4,387 vertex lifts and 230,386
  non-vertex lifts. See `results/phase4c/denominator_lemma.json`.
- **Ledger:** `denominator-lemma-glue` holds for n = 4…8, and `denominator-lemma-lift` holds for n = 4…9; at n = 9 it
  was checked only on the 1,221 published counterexamples.
- **Lemma 3, exhaustively for k ≤ 9; Theorem 4 on the n = 9 sample; and an exact population count:** see
  `scripts/denominator_bound.py` and `results/phase8/denominator_bound.json`.
