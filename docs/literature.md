# Known vertex constructions and structural facts for the metric polytope m_n

Phase 4a. Source keys and access status: `data/literature/SOURCES.md`.
Notation: nodes 1..n; x ∈ ℝ^{C(n,2)}; cut δ(S); switching r_{δ(S)}(x)_{ij} = 1 − x_{ij} if ij ∈ δ(S), else x_{ij};
d_G = shortest-path metric of a connected graph G; Δ_{ijk} perimeter facet, Δ_{ij\bar k} triangle facet x_{ij} ≤ x_{ik}+x_{jk}.

**Status labels.** `PRIMARY` = read in an open copy of the original source. `SECONDARY` = stated in an open
paper citing the (unread) original. `UNREAD` = only in a paywalled source; content not verified. `DERIVED` = my own
reformulation, to be checked in code (Phase 4c). Nothing below has been checked in code yet; Phase 4c does that.

## 0. Corrections to the Phase-4 brief

1. *Graphic vertices of the metric polytope* (Discrete Math. 151, 1996) is by **Monique Laurent alone** [L96].
   It is paywalled (ScienceDirect HTTP 403) and **I could not read it**. Its 1991 Bonn report (91737-OR) is not online.
   The claims the brief attributes to it are handled below as SECONDARY or UNREAD.
2. The Springer link (LNCS 2866, 2003) is *On the Face Lattice of the Metric Polytope* by **Deza, Fukuda, Mizutani, Vo**
   [DFMV03]. Deza–Fukuda–Pasechnik–Sato wrote *On the Skeleton of the Metric Polytope* (LNCS 2098, 2001) [DFPS01].
   Both were read via open preprints.
3. The dominating-set conjecture is Laurent–Poljak, IPCO 1992 (*The metric polytope*), not [L96].
4. Counterexample counts differ by version: arXiv 2005 [DI05]: 910,209 m_9 orbits computed, 477 + 389 = 866
   counterexample orbits; Optim. Lett. 2007 [DI07] and Deza's page: 1,056,368 orbits, **1,221** counterexample orbits
   (483 quasi-simple with incidence 37, 738 with incidence ≥ 38).
5. [DFMV03] preprint abstract prints "1 550 825 000 vertices"; its Proposition 1 and all other sources give
   1 550 825 600 (also reproduced by our Phase 2 orbit–stabilizer sum). Typo in the preprint.

---

## 1. Generative constructions

### C1. Cuts — `PRIMARY` [DFPS01 §2.2, LP92 §1]
- Input: S ⊆ {1..n}. Output: x = δ(S), x_ij = 1 if |{i,j} ∩ S| = 1 else 0.
- Always a vertex of m_n; the cuts are exactly the integral vertices. 2^{n−1} of them, one orbit.

### C2. Anticuts — `PRIMARY` [DFPS01 §2.2, DFMV03 §3.3, LP92 §4.1]
- Input: S. Output: \bar δ(S) = (2/3)·𝟙 − (1/3)·δ(S), i.e. x_ij = 1/3 on δ(S), 2/3 elsewhere.
  Equivalently r_{δ(S)}((2/3)𝟙).
- Vertex of m_n for n ≥ 5 (LP92: m_5 has 2^4 such vertices; m_6 has 2^5). One orbit of size 2^{n−1}.
- LP92 §3 phrases the same object as x(K_{S,T}) (1/3 on K_{S,T}, 2/3 elsewhere), "a vertex of MP_n, n = |S|+|T| ≥ 5 (Avis 1980a)".

### C3. Trivial extensions (0-/1-extension, "lift by a twin node") — `PRIMARY` [LP92 §2.3–2.4 Prop 2.7; DFPS01 §2.2]
- Input: v ∈ ℝ^{C(n−1,2)}. Output η0(v), η1(v) ∈ ℝ^{C(n,2)} (DFPS01 indexing, new node n twins node 1):
  - η0(v)_ij = v_ij (1 ≤ i < j ≤ n−1); η0(v)_{i,n} = v_{1,i} (2 ≤ i ≤ n−1); η0(v)_{1,n} = 0.
  - η1(v) = r_{δ({n})}(η0(v)): η1(v)_{i,n} = 1 − v_{1,i}, η1(v)_{1,n} = 1.
- Condition (iff): η0(v) is a vertex of m_n ⇔ v is a vertex of m_{n−1} (same for η1) [LP92 Prop 2.7].
- Converse: every non-cut vertex with some coordinate in {0,1} is a trivial extension; "the new vertices of m_n are
  the fully fractional ones" [DFPS01, DFMV03].

### C4. Node duplication with the same denominator — `PRIMARY` [LP92 p. 12]
- Input: fractional vertex x of m_n with denominator d. Output y ∈ ℝ^{C(n+1,2)}:
  y_ij = x_ij (i,j ≤ n); y_{i,n+1} = x_{1i} (2 ≤ i ≤ n); y_{1,n+1} = min_{2≤i≤n} min(2x_{1i}, 2 − 2x_{1i}).
- Claim: y is a vertex of m_{n+1} with the same denominator d. (LP92 refers to a "subsection 2.5" for this; that
  subsection is absent from the report version read.)

### C5. Radial extension Λ^m — `PRIMARY` [DDF96 §3, Thm 3.1, Thm 3.2, (3.6)–(3.9)]
- Definitions: δ(v) = 2 r(v) = max_{i<j} v_ij (diameter, radius). Γ(v) = graph on {1..n} with s~t ⇔ v_st = δ(v).
  A graph G = (N,E) is *good* if it has a spanning subgraph G' = (N,E') with |E'| = |N| admitting no nonzero
  edge-weighting f: E' → ℝ with Σ_{e∋u} f_e = 0 at every node u.
- Map Λ^m_α: ℝ^{C(n,2)} → ℝ^{C(n+m,2)}: old–old pairs keep v_ij; old–new pairs get α; new–new pairs get 2α.
  Radial m-extension Λ^m(v) := Λ^m_{r(v)}(v).
- Membership: Λ^1_α(v) ∈ m_{n+1} ⇔ r(v) ≤ α ≤ 1 − r(v) (3.6); for r < α < 1 − r it is not a vertex (3.7);
  Λ^1_{1−α}(v) = r_{δ({n+1})}(Λ^1_α(v)). Λ^2(v) ∈ m_{n+2} always; for m ≥ 3, Λ^m(v) ∈ m_{n+m} ⇔ δ(v) ≤ 2/3 (3.9).
- Thm 3.1: v vertex of m_n and Γ(v) good ⇒ Λ^1(v) vertex of m_{n+1}.
- Thm 3.2: v vertex of m_n, Γ(v) good, and (m ≥ 3 ⇒ δ(v) ≤ 2/3) ⇒ Λ^m(v) vertex of m_{n+m}.
- Remark 3.3: (1) v need not be a vertex: v = (2/3)d(K_4) is not a vertex of m_4 but Λ^1(v) is, up to switching,
  (2/3)d(K_5) (the paper writes equality; with α = r(v) = 1/3 the new coordinates are 1/3, so equality holds only up
  to switching r_{δ({5})} — to be checked). (2) No known vertex with non-good Γ(v) has Λ^1(v) a vertex.
- `DERIVED`: "good" ⇔ every connected component of G contains an odd cycle (a spanning odd-cycled forest exists;
  its incidence matrix is nonsingular). To verify in code.

### C6. Suspension of a tree — `SECONDARY` [DDF96 Remark 3.3(4), citing L96; search-result abstract of L96]
- DDF96: "For n ≥ 5, v a vertex of m_n and Γ(v) = \bar T for a tree T which is not a star, Laurent [L96] proved that
  Λ^1(v) is a vertex of m_{n+1}."
- DDF96 p. 13: if v = (1/3)d(G) with G of diameter 2, then Γ(v) = \bar G and Λ^1(v) = (1/3)d(∇G), ∇G = suspension
  (G plus one node adjacent to all). So "suspension" = radial extension of a (1/3)·graph-metric vertex.
- The abstract of L96 says graphic vertices arising from the suspension of a tree are *characterized*. The exact
  characterization is in L96 and is `UNREAD`.

### C7. Graphic vertices x_G — `PRIMARY` definition [DFPS01 §2.2, DFMV03 §3.3]; existence claims `SECONDARY`
- Input: connected graph G on n nodes. τ(d_G) = max_{i,j,k} (d_G(ij) + d_G(ik) + d_G(jk)) (triameter).
  Output x_G = (2/τ(d_G))·d_G. "Graphic vertex" := a vertex of m_n of this form.
- x_G ∈ m_n always holds (scaling makes the max perimeter 2), but being a *vertex* is not automatic and must be
  checked (`DERIVED` for the membership remark).
- Claim (SECONDARY, citing L96, LP92-IPCO): every (1/3,2/3)-valued vertex of m_n is, up to switching, graphic:
  v = r_{δ(S)}(x_G).
- Examples with explicit graphs (DDF96 Remark 3.3(3), numbering of DDF96 Table 1, *not* of metric_7.ext):
  v_2 = (2/3)d(K_7); v_7 = (1/3)d(K_7 − C_{2,3,4} − C_{5,6,7}); v_8 = (2/5)d(K_7 − C_7);
  v_9 = (1/3)d(K_7 − C_7 − P_{1,3}); v_10 = (1/3)d(K_7 − C_{2,3,4} − C_{5,6,7} − P_{4,5})
  (C_s, P_s = cycle / path on node subset s; C_7 the 7-cycle).

### C8. (1/3)·metric of complete multipartite graphs — `PRIMARY` result for n = 8 [DDF96 Prop 3.4]; general `SECONDARY` [Avis 1980]
- Input: complete t-partite G on n nodes. Output v = (1/3)d(G) (1/3 across parts, 2/3 inside parts).
- Avis: for G "almost complete t-partite", (1/3)d(G) is a vertex of m_n (definition of "almost" not in sources read: `UNREAD`).
- DDF96 Prop 3.4 (n = 8, computer-checked): (1/3)d(G) is a vertex of m_8 for complete t-partite G only for
  G = K_{4,3,1}, K_{3,3,2}; also for G_e = K_{3,3,1,1} − e, K_{4,2,2} − e, K_{6,1,1} − e, e an edge of the
  subgraph K_{3,3}, K_{4,2}, K_{1,1} respectively.
- Combined with C5: Λ^1((1/3)d(G)), Λ^2((1/3)d(G)) are vertices of m_{n+1}, m_{n+2} (DDF96 Remark 3.3(5)).

### C9. Avis doubling G ↦ G* (arbitrary denominators) — `SECONDARY` [LP92 Prop 4.1, citing Avis 1980a]
- Input: graph G = (V,E), V = {1..n}. Build G* on V ∪ V' ∪ {u_e : e ∈ E}, N = 2n + |E| nodes: edges of G, a copy G'
  on V', twin edges i–i', and for each e = (i,j), i < j, edges i–u_e and j'–u_e.
- Output x_{G*} = (2/τ(G*)) d_{G*}, with τ(G*) = τ(G) + 2. Claim: vertex of m_N; denominator τ(G)+2 or (τ(G)+2)/2.
- Corollary: G = path on d nodes gives a vertex of m_{3d−1} with denominator d; trivial extensions give denominator d
  for all n ≥ 3d − 1. Hence every d ≥ 3 occurs. (m_7 has denominators 3,4,5,6,7.)

### C10. Rays of the metric cone ↦ vertices — `PRIMARY` statement [LP92 §4.1, DFMV03 §3.3]
- Input: extreme ray r of M_n. Output: the point where the ray meets a perimeter facet. LP92: "every extreme ray of
  the metric cone MC_n determines a vertex of the metric polytope MP_n which is the intersection of the ray with some
  triangle facet (2)". Explicit form x = (2/τ(r)) r, τ(r) = max_{ijk}(r_ij + r_ik + r_jk), is `DERIVED`.
- Conjecture (Laurent–Poljak 1992): every vertex of m_n arises this way up to switching ⇔ every fractional vertex is
  adjacent to a cut. Holds n ≤ 8, false n = 9 (see S8).

### C11. k-union (gluing) — `PRIMARY` [LP92 Prop 2.9 + Lemma 2.2]
- Input: x_1 vertex of m(V_1), x_2 vertex of m(V_2) agreeing on K(V_1 ∩ V_2). The concatenation x (defined on the
  k-sum of K(V_1) and K(V_2), *not* on all pairs of V_1 ∪ V_2) is a vertex of the projected polytope S(G).
- It extends (Lemma 2.2(ii)) to a vertex y of m(V_1 ∪ V_2), choosing the missing coordinates one at a time at a bound
  of the cycle inequalities. LP92 only asserts existence ("can be extended"); the extension is not unique.
- Remark 3.4 example: 2-sum of two K_5 copies yields a 1/6-integral vertex of S(G).

### C12. Explicit sporadic vertices — `PRIMARY` [LP92 Ex. 2.13, 2.14; DFMV03 §5.2; DI05 Prop 2.1]
- LP92 Ex. 2.14 (n=7): x_ij = 1/3 except 2/3 on (2,3),(2,4),(3,4),(3,6),(5,6),(5,7),(6,7). Claimed vertex of m_7
  **none of whose projections is a vertex of m_6** — a vertex not obtained by any lift.
- LP92 Ex. 2.13 (n=8→9): x ∈ m_8 with 2/3 except 1/3 on (1,2),(1,4),(1,6),(2,3),(4,5),(6,7),(i,8) for 1≤i≤7; extension
  y ∈ m_9: y_{i9} = 1/6 (i=2,3), 3/6 (i=1,4,5,8), 5/6 (i=6,7). Both claimed vertices; y has denominator 6 = 2·3.
- DFMV03: m_8 orbit 451 rep (1/15)(2,4,4,5,5,7,8,6,6,5,5,5,10,8,5,5,5,4,9,9,3,4,10,10,5,10,5,5), the only denominator-15
  orbit, size 2,580,480; orbit 531 rep (1/9)(2,2,3,3,4,4,5,4,3,3,6,6,3,5,5,2,6,3,6,3,3,6,3,3,6,4,5,3), the only orbit
  adjacent to exactly 2 cuts, size 1,290,240.
- DI05 Prop 2.1: the n=9 counterexample (1/9)(2,2,3,3,4,4,5,5,4,3,5,6,6,3,3,5,5,2,4,3,5,6,3,3,6,6,5,3,2,6,6,3,3,5,3,4),
  37 tight facets (listed), 37 neighbours (listed), all fractional.

---

## 2. Structural facts and conjectures

| id | statement | n where stated to hold | source / status |
|---|---|---|---|
| S1 | Cuts are exactly the integral vertices. | all n | PRIMARY [DFPS01, LP92] |
| S2 | No fractional ½-integral vertex (no vertex with denominator 2). | all n | PRIMARY [LP92 Cor 2.8] |
| S3 | A non-cut vertex with a 0/1 coordinate is a trivial extension of a vertex of m_{n−1}. | all n | PRIMARY [LP92 Prop 2.7; DFPS01] |
| S4 | If a vertex has denominator d, any vertex extending it (to n+1) has denominator d or 2d. | all n | PRIMARY [LP92 Prop 2.12] |
| S5 | A vertex x of m_n projects to a vertex of m_{n−1} ⇔ ∃ base B of tight triangle equalities and a node i with \|B(i)\| = n−1 (and Thm 2.11's odd-signed-cycle characterization). | all n | PRIMARY [LP92 Lemma 2.10, Thm 2.11] |
| S6 | If projections of x ∈ m_n deleting three distinct nodes are all vertices of m_{n−1}, then x is a vertex. | all n | PRIMARY [LP92 Lemma 2.15] |
| S7 | Incidence: Icd(v) ≤ 3C(n,3), equality iff cut; trivial extension ⇒ Icd ≤ 2C(n,3); fully fractional ⇒ Icd ≤ C(n,3), equality iff anticut. | all n | SECONDARY [DFPS01 Property 1, citing LP-IPCO92] |
| S8 | Dominating set: every vertex is adjacent to a cut. | true n ≤ 8; **false n = 9** (1,221 known orbits) | PRIMARY [DI05, DI07, DFMV03] |
| S9 | No cut-set: for n ≥ 6 the non-cut vertices induce a connected subgraph of the skeleton. | true n ≤ 8; checked for 253,210 m_9 orbits (2003) | PRIMARY [DFPS01, DFMV03] |
| S10 | Every (1/3,2/3)-valued vertex is graphic up to switching. | all n | SECONDARY [DFMV03, DFPS01 citing L96] |
| S11 | Every d ≥ 3 is a denominator for n ≥ 3d − 1; m_7 denominators {3,4,5,6,7}; max denominator of m_8 is 15 (orbit 451 only); largest known for m_9 is 39. | — | PRIMARY [LP92 Prop 4.1; DFMV03] |
| S12 | Simple vertices: none in m_6, m_7; in m_8 only orbits 532, 533 (both graphic, (1/3,2/3)-valued); none known in m_9. | — | PRIMARY [DFMV03] |
| S13 | Orbit composition: m_7 = cuts, anticuts, 3 trivial-extension orbits, 3 (1/3,2/3) orbits, 5 other fully fractional; m_8 = cuts, anticuts, 28 trivial ext., 37 (1/3,2/3), 466 other fully fractional (533 total). | n = 7, 8 | PRIMARY [DFPS01, DFMV03] |
| S14 | Codim-3 faces form 15 orbits for all n ≥ 9; the codim-k orbit count is "probably constant for n ≥ 3k". | Thm for k=3; conjecture for k>3 | PRIMARY [DFMV03 Thm 1, Remark 2] |
| S15 | The face Δ_{123} ∩ Δ_{12\bar3} (codim n−1) is combinatorially equivalent to m_{n−1}. | all n | PRIMARY [DFMV03 §5.2] |
| S16 | Every vertex of m_8 is adjacent to ≥ 2 cuts. | n = 8 | PRIMARY [DFMV03] |
| S17 | Diameters δ(m_3)=δ(m_4)=1, δ(m_5)=δ(m_6)=2, δ(m_7)=δ(m_8)=3. | n ≤ 8 | PRIMARY [DI05 §3.1] |
| S18 | Vertices split into switching classes; **apart from cuts, no two vertices in the same switching class are adjacent.** | — | **UNREAD** (brief, attributed to L96). Not found in any open source read. Test in code. |
| S19 | Symmetry group: for n ≥ 5, Is(m_n) = switchings ⋊ S_n, order 2^{n−1} n!; \|Is(m_4)\| = 2(4!)^2 = 1152. | — | PRIMARY [DFMV03 §2.1, §3.2] |

Note on S19: our Phase 2 uses the 2^{n−1} n! group for all n, including n = 4 (order 192 < 1152). Deza's orbit
counts are stated "under permutations and switchings", so this is consistent with his tables; it matters only if we
ever claim orbits under the full isometry group at n = 4.

---

## 3. How completeness of the orbit lists was established

- **n ≤ 7** — m_5, m_6 described in LP92 §4.1; m_7's 275,840 vertices computed by cdd (double description) with a
  facet insertion order built from maximal cocliques of the dual skeleton [DDF96 §4]. A full vertex enumeration,
  hence complete.
- **n = 8** — [DFPS01] found 533 orbits with the *orbitwise (adjacency-decomposition) vertex enumeration*:
  start from a vertex, enumerate its neighbours, canonicalize, repeat on new orbits. That relied on Conjecture 2
  (no cut-set) to skip the intractable cut neighbourhood (incidence 168), so it was not a proof.
  [DFMV03 §5.1–5.2] proved completeness by *orbitwise face enumeration*: compute canonical representatives of all
  face orbits down to codimension 7 (21-dimensional faces of the 28-dimensional m_8); every vertex lies on some face of
  every layer, so enumerating the vertices of each representative 21-face with cddlib (lexicographic facet order) and
  canonicalizing them yields all orbits. The one representative face Δ_{123} ∩ Δ_{12\bar3} ≅ m_7 is skipped because its
  vertices are known (trivial extensions). Result: exactly the 533 orbits. Consequences: 1,550,825,600 vertices,
  δ(m_8) = 3, M_8 has 119,269,588 extreme rays, Conjectures 1 and 2 hold for n = 8.
- **n = 9** — not proven complete. Orbitwise vertex enumeration with an incidence cutoff Icd_max (44 in 2003, giving
  253,210 orbits; later 1,056,368 orbits [DI07]). The list is "conjectured to be complete" (Deza's page) but the
  method cannot reach vertices of high incidence, and the authors expect undiscovered simple vertices [DFMV03 Remark 3].

## 4. What this means for the DSL (input to Phase 4b)

Primitive operations the grammar must express, by construction:
`cut(S)`, `anticut(S)`, `switch(S, ·)`, `perm(π, ·)`, `twin0/twin1` (C3), `dup` (C4, a node copy with a computed
diagonal value), `radial(m, α, ·)` (C5), `graph_metric(G, scale)` and `triameter` (C7–C9), graph builders
(K_n, complete multipartite, cycles/paths on subsets, edge deletion, suspension ∇, Avis doubling G*), `ray_to_vertex` (C10),
`glue_k(x1, x2)` + a completion choice (C11), literal points (C12), and predicates for S1–S18
(vertex test, denominators, incidence, projection-to-vertex, adjacency to cuts, switching-class adjacency).
Two constructions need a *selection* among valid outputs (C4's min, C11's extension), so the DSL needs a
deterministic "choose" combinator with an explicit rule.

### Avis 1980, read directly (2026-11-25) — `PRIMARY`
D. Avis, *On the extreme rays of the metric cone*, Canad. J. Math. 32 (1980) 126–144, doi 10.4153/CJM-1980-010-0.
- Thm 2.4 (1-ic-colorable ⇒ extreme ray; converse false). Thm 3.2: dense m-partite graphs: parts V_1..V_m with
  |V_i| ≥ 3 and ||V_i ∪ V_j|| ≥ |V_i||V_j| − max(|V_i|, |V_j|) + 2 ("almost complete" = this). Thm 3.3: G_{n,p} induces
  an extreme ray with probability 1 − o(1) for n^(−1/5+ε) ≤ p ≤ 1 − n^(−1/4+ε); hence 2^C(n,2)(1 − o(1)) labelled
  graphic extreme rays. Lemma 3.4 / Thm 3.5: F(G) (two copies of G joined by a matching, plus a new vertex per edge
  u1v1 joined to u1 and v2) is an extreme ray containing G isometrically; every rational metric is a restriction of
  an extreme ray. Thm 4.2 (zero distances), Thm 4.4 (union of two overlapping extreme rays is an extreme ray).
- This resolves the `UNREAD` in C8 and gives the construction behind C9 from the primary source.

## Forward-citation check, 2026-11-26 (OpenAlex only)

Works citing Avis 1980 (68), Laurent 1996 (26) and Deza–Indik 2007 (6) were listed from OpenAlex; zbMATH Open
returned HTTP 403 to automated access. Titles concerning extreme rays, vertices of the metric polytope or
extremality criteria were followed up. Nothing found that states a bounded-scope impossibility, a locality
measure, a 2^(cn²) count beyond Avis / Cizma–Linial, or a limit on generators.

- Melleray, Petrov, Vershik 2008 (arXiv math/0611049): extremal = on an extreme ray of the semimetric cone; open
  Question 6 asks to describe extremal n-point spaces and estimate their number. Now cited.
- Casabella, Joswig, Kastner 2024 (arXiv 2402.17665): seven-point classification via hypersimplex subdivisions; new
  families of rays. Read to about 40%. Now cited.
- Feldman, Kehoe 2026 (Zenodo): bowtie metrics as extreme rays, metric body. Record description only.
- Bondarenko–Nikolaev 2014/2015, Nikolaev 2015: integrality of relaxations, vertex denominators growing
  exponentially. Not about extremality criteria.
- Not read (no accessible text): Karzanov 1998 (primitive extensions), Grishukhin 1992 (rays for seven points),
  Avis 1980 (Ann. Discrete Math. 8), the "metric body" thesis (core.ac.uk, 403).
