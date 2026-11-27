# Extremality in the metric cone has unbounded locality

*Draft of 2026-11-27. Every statement is marked **Theorem** / **Proposition** / **Lemma** (proved here),
**Computation** (exact computer result on a stated data set) or **Question** (open). Section 10 lists what still has
to be done before submission and is not part of the paper.*

## Abstract

A metric on n points spans an extreme ray of the metric cone MET_n exactly when its tight triangle equalities have
rank C(n,2) − 1. We ask whether this rank condition can be replaced by a test that looks at a bounded number of
points at a time. To measure this we introduce the *locality* L(d) of an extreme ray d: the least s such that
extremality of d can be derived by solving the tight equalities inside sets of s points and propagating the
proportionalities obtained. We prove that L = 4, the smallest possible value, for every graph covered by Avis's
isometric-cycle criterion, hence for almost all graphs, and that L is nevertheless unbounded: an explicit chiral
family C_t of extreme rays on 2t points (t odd, t ≥ 9) has L(C_t) = 2t, that is, no proper subset of the points
proves extremality (the bound L(C_t) > t/6 has a short proof; the equality is computer-assisted, with exact
arithmetic). Hence no test that proceeds by such deductions on a bounded number of points characterises the extreme
rays of the metric cone, or the vertices of the metric polytope m_n adjacent to a cut; tests that only forbid
restrictions to a bounded number of points are excluded by Avis's embedding theorem. The obstruction is specific
to two-term deduction: with longer linear relations, five points suffice for every ray tested on the lists up to nine
points, and ten points for every C_t (five for C_9, C_11 and C_13), and
with counting and recursion a bounded number of variables suffices for all metrics, by a theorem of Dawar, Grohe,
Holm and Laubner; whether deduction with longer relations has bounded scope on all extreme rays is left open. We
compute L exactly for all extreme rays of MET_n,
n ≤ 8, and for the 1,055,145 cut-adjacent orbits of the known vertex list of m_9: the largest values are 4, 4, 5, 7
for n = 5, ..., 8 and 9 on the m_9 list, and the share of rays with L = 4 falls from 97% (n = 7) to 30% (n = 9).
We also show, by a counting argument resting on a theorem of Avis, that a generator of vertices of m_n whose rules
build an object on n nodes from smaller ones that overlap in a bounded number of nodes, with fewer than (1 − δ)n
bits of choice, produces a vanishing share of the orbits, so that no finite set of such rules with a finite list of
exceptions describes the vertices.

## 1. Introduction

The metric cone MET_n is the set of x ∈ R^C(n,2) with x_ij ≤ x_ik + x_jk for all triples, and the metric polytope
m_n is its intersection with the half-spaces x_ij + x_ik + x_jk ≤ 2. The cut polytope is contained in m_n and has
the same integral vertices, and m_n is the standard linear relaxation of max-cut; its fractional vertices are what
separates the relaxation from the problem. Complete vertex lists are known for n ≤ 8 [DFPS01, DFMV03], and for
n = 9 there is a list of 1,056,368 orbits conjectured to be complete [DI07]. Constructions of infinite families are
known (cuts and anticuts, trivial extensions, graphic vertices, Avis's doubling, gluing; see [LP92, L96, DL97]), but
they account for a small and shrinking part of the lists, and no description of the vertices other than enumeration
is known.

> **Question.** Is there a finite set of rules, valid for every n, and a finite list of exceptions, which together
> produce exactly the vertices of m_n?

The answer depends on what a rule may do, and we separate two regimes.

*Graph-input rules.* A rule receives a weighted graph on n nodes and returns its shortest-path metric, scaled. Every
vertex adjacent to a cut arises this way, and the rule is correct exactly when the metric is an extreme ray of MET_n,
that is, when its tight triangle equalities have rank C(n,2) − 1. The question becomes whether this rank condition
can be replaced by a combinatorial test of bounded scope, in the way Avis's isometric-cycle criterion [A80] does for
a large class of graphs. We treat the two simplest kinds of such tests: those that propagate proportionalities
between distances from one bounded set of points to another, whose scope is measured by the locality L (Section 3),
and those that only inspect the restrictions to bounded sets of points (Section 5b).

*Small-choice rules.* A rule receives one or several objects on fewer than n nodes and a bounded or slowly growing
amount of choice and returns an object on n nodes. Trivial extensions, Avis's doubling and gluing along a bounded
number of common points are of this kind; gluing along an unbounded number of common points is not, and our result
does not cover it (Remark (d) after Theorem 6).

**Results.**
1. *Locality.* The invariant L is well defined, sound and complete (Proposition 2). It equals 4 for every graph
   covered by the isometric-cycle criterion, and for almost all graphs (Theorem 3).
2. *Locality is unbounded* (Theorem 4, the main result). An explicit family C_t of extreme rays on n = 2t points has
   L = n. The proof reduces the tight system of C_t to a linear recurrence around the cycle whose characteristic
   polynomial has a root λ that is not a root of unity. On any set of points that misses five consecutive positions
   this root yields a second solution of the local equations, which no local deduction can exclude; this gives
   L > n/12 by hand. When a single point is removed, the recurrence is broken at that point only, and a solution
   that decays like λ^(−k) away from the break still exists; showing that it separates all classes is a finite
   exact computation, uniform in t.
3. *Counting.* The number of orbits of vertices of m_n is at least 2^(n²/2 − O(n log n)) (Proposition 5, from Avis's
   density theorem), and a generator with at most (1 − δ)n bits of choice per node, whose rules may combine several
   inputs with bounded overlap, produces a vanishing share of them (Theorem 6).
3b. *Hereditary tests.* A test that accepts a metric when all its restrictions to at most s points belong to an
   allowed set, and that accepts every extreme ray, accepts every rational metric with positive distances (Proposition 7, a consequence of
   Avis's embedding theorem).
3c. *Stronger local tests* (Section 5c). Deduction with linear relations of more than two terms, confined to sets
   of s points, is sound and at least as strong as two-term deduction (Proposition 8); it proves the
   extremality of every ray tested on the lists up to nine points with s ≤ 5, and that of C_t with s = 20 for every
   t tried. With counting and recursion, a bounded number of variables
   suffices for all metrics (Proposition 10).
4. *Exact computations.* L for all extreme rays of MET_n, n ≤ 8, and for the m_9 list (Comp. 1–3); searches for large
   locality beyond the lists (Comp. 4–6); and negative results for four other candidate descriptions of the m_9 list
   (Comp. 7–12).

Together, 1 and 2 say that the scope of the rank condition is the smallest possible for a typical graph and
unbounded in the worst case. What is excluded is stated precisely in the paragraph "What L bounds" of Section 3 and
in Section 5b: tests by local deduction of proportionalities, and tests by forbidden restrictions. We do not claim
that every conceivable test of bounded scope fails, and Section 5c shows that this would be false: deductions with
relations of more than two terms prove the extremality of every C_t inside sets of ten points (Theorem 9; five points for C_9, C_11 and C_13), and with counting and
recursion a bounded number of variables suffices for all metrics, by a theorem of Dawar, Grohe, Holm and Laubner on
the rank of rational matrices. Whether deduction with longer relations has bounded scope on all extreme rays is open
(Question 2). The computations show that on the actual vertex lists the typical case is already
leaving the minimum at n = 9.

## 2. Preliminaries

**Symmetries.** The symmetry group of m_n is generated by the permutations of the nodes and the switchings
r_S(x)_ij = 1 − x_ij for ij in the cut δ(S), x_ij otherwise. It has order n!·2^(n−1) for n ≥ 5. "Orbit" means an
orbit of this group. The cuts are the integral vertices and form one orbit.

**Tight systems.** For a metric d on n points, a triple (a, m, b) is *tight* if d_ab = d_am + d_mb (m is between a
and b). The *tight system* T(d) is the set of linear equations x_ab = x_am + x_mb over the tight triples. d spans an
extreme ray of MET_n iff the solution space of T(d) is the line through d, i.e. rank T(d) = C(n,2) − 1.

**Lemma 1 (rays give vertices).** Let d span an extreme ray of MET_n, n ≥ 3, and let τ be the largest perimeter
d_ij + d_ik + d_jk. Then x = (2/τ)·d is a vertex of m_n, and it is adjacent to the cut vertex 0.

*Proof.* x ∈ m_n by the choice of τ. The equations of T(d) are tight at x and have rank C(n,2) − 1; each of them
vanishes at x. A triple attaining τ gives a tight perimeter inequality x_ij + x_ik + x_jk = 2, which does not vanish
at x and is therefore independent of them. So the tight inequalities at x have rank C(n,2). The segment from 0 to x
lies on the C(n,2) − 1 independent facets of T(d), so it is an edge. ∎

Conversely, a vertex of m_n adjacent to a cut is, after the switching that moves this cut to 0, of the form (2/τ)d
for an extreme ray d [LP92]. Every vertex of m_n, n ≤ 8, is adjacent to a cut; on the m_9 list 1,221 orbits are not
[DI07] (re-derived in Comp. 7 below).

**Weighted graphs.** For a metric d with positive distances, the *minimal graph* has an edge ab of weight d_ab
whenever no third point is between a and b; d is its shortest-path metric. We scale d to coprime integers and call
the set of weights the *alphabet*. *Graphic* means alphabet {1}; d_G denotes the shortest-path metric of a
connected graph G.

## 3. Locality of an extreme ray

Let d be a metric on a node set V, |V| = k ≥ 4, with positive distances. Write a solution x of T(d) as
x_p = d_p·u_p over the pairs p; then u ≡ 1 is a solution, and d is extreme iff every solution has u constant.

**Definition (level-s closure, locality).** Let π be a partition of the pairs, and W ⊆ V. The system T_W(π) consists
of the equations d_ab·u_[ab] = d_am·u_[am] + d_mb·u_[mb] for the tight triples with a, m, b ∈ W, in one variable u_C
per class C of π that contains a pair inside W. W *forces* C = C′ under π if u_C = u_C′ in every solution of T_W(π).
The *level-s closure* cl_s(d) is the finest partition π that is closed under merging C and C′ whenever some W with
|W| = s forces C = C′ under π. The *locality* L(d) is the least s ≥ 4 such that cl_s(d) has a single class; L(d) = ∞
if there is none.

**Proposition 2.**
(i) cl_s(d) is well defined, and is the result of applying the merges in any order until none applies.
(ii) (Soundness) If two pairs p, q are in the same class of cl_s(d), then x_p/d_p = x_q/d_q for every solution x of
T(d). Hence L(d) < ∞ implies that d is extreme.
(iii) cl_s(d) refines cl_{s+1}(d), and cl_k(d) has a single class iff d is extreme. Hence d is extreme iff
L(d) ≤ k, and then 4 ≤ L(d) ≤ k.
(iv) L is invariant under relabelling and scaling.

*Proof.* (i) If π refines π′, every solution of T_W(π′) is a solution of T_W(π) that is constant on the classes of
π′; so a merge forced under π is forced, or already made, under π′. The merge operator is therefore monotone on
the lattice of partitions and has a least closed partition above the discrete one, reached by any maximal sequence
of merges. (ii) By induction on the sequence of merges: if u is constant on the classes of π for every solution of
T(d), then the restriction of u to the pairs inside W solves T_W(π), so a forced merge preserves the property.
(iii) A set W of size s is contained in a set W′ of size s + 1 and T_W(π) ⊆ T_W′(π), which gives the refinement.
For W = V and π discrete, T_V(π) is T(d) in the variables u, and it forces all classes equal iff its solution space
is spanned by u ≡ 1. (iv) is clear. ∎

**What L bounds.** Call a deduction *s-local* if it derives a proportionality x_p = c·x_q from the tight equations
among at most s nodes, used together with proportionalities derived earlier. By (i), the proportionalities
derivable by s-local deductions are exactly those of cl_s(d). So a test for extremality that proceeds by s-local
deductions succeeds on d iff L(d) ≤ s, and a characterisation of extreme rays by forbidden or required
configurations on at most s nodes, closed under such propagation, cannot be complete unless L ≤ s on all rays. The
notion covers deductions of two-term proportionalities; a local rule that carries longer linear relations from one
subset to another is not covered; such deductions are defined and discussed in Section 5c, where it is shown that
they prove the extremality of every C_t inside sets of ten points. Tests that do not propagate anything, and only
require every restriction to s points to be of an allowed kind, are treated in Section 5b.

**Theorem 3.** Let G be a connected graph on k ≥ 4 nodes.
(a) If all edges of G fall into one class under the relation generated by "opposite edges of an even isometric
cycle" (G is 1-ic-colorable in the sense of Avis [A80, §2]), then L(d_G) = 4; in particular d_G is extreme.
(b) For G = G(n, 1/2), with probability 1 − o(1): G is connected and any two edges of G are linked by a chain of
induced 4-cycles in which consecutive edges are opposite. Hence L(d_G) = 4 for 2^C(n,2)·(1 − o(1)) labelled graphs
on n nodes.

*Proof.* (a) Let 1, 2, ..., 2t be an isometric cycle of G, t ≥ 2, and W = {1, 2, t + 1, t + 2}. The triples
(1, t + 2, t + 1), (1, 2, t + 1), (2, 1, t + 2), (2, t + 1, t + 2) (middle node between the outer two) are tight and
lie in W. They give x_{1,t+1} = x_{1,t+2} + x_{t+1,t+2} = x_{1,2} + x_{2,t+1} and
x_{2,t+2} = x_{1,2} + x_{1,t+2} = x_{2,t+1} + x_{t+1,t+2}; subtracting the two resulting equalities gives
x_{1,2} = x_{t+1,t+2} (this is [A80, Lemma 2.3]). Both pairs have d = 1, so W forces their classes equal under any
partition. Hence all edges lie in one class E of cl_4(d_G). Let ab be a pair at distance j ≥ 2 and m a neighbour of
a on a geodesic from a to b. If [mb] = E (induction on j), the equation j·u_ab = u_E + (j − 1)·u_E inside any
4-set W ⊇ {a, m, b} forces [ab] = E. So cl_4 has one class, L ≤ 4, and L ≥ 4 by definition; extremality follows
from Proposition 2(ii), without using [A80, Thm 2.4].

(b) Fix distinct nodes s, t, u, v and split the other n − 4 nodes into ⌊(n − 4)/2⌋ pairs {x, y}. For a pair, let
A_{x,y} be the event that xs, xy, xv, yt, yu are edges and xt, xu, ys, yv are not; it has probability 2^(−9), and
the events for different pairs are independent of each other and of the presence of st and uv, since they concern
disjoint sets of pairs of nodes. If st and uv are edges and A_{x,y} holds, then s, t, y, x and u, v, x, y are
induced 4-cycles, in which st and uv are both opposite to xy [A80, Fig. 3.5]. There are at most 3·C(n,4) choices of
two disjoint pairs st, uv, so the probability that some two disjoint edges are not linked in this way is at most
3·C(n,4)·(1 − 2^(−9))^⌊(n−4)/2⌋ → 0. Two edges with a common endpoint are linked through a third edge disjoint from
both, which exists unless some n − 3 nodes span no edge, an event of probability at most C(n,3)·2^(−C(n−3,2)) → 0.
The probability of an isolated node is at most n·2^(−(n−1)) → 0, and a graph without isolated nodes in which all
edges are linked by chains of 4-cycles is connected. An induced 4-cycle is isometric, so (a) applies. ∎

**Corollary (bipartite graphs).** Let G be a connected bipartite graph on k ≥ 4 nodes. Call two edges ab, cd
*opposite* if d_G(a, c) = d_G(b, d), d_G(a, d) = d_G(b, c) and these two numbers are different [LS93, Prop. 4]. The
following are equivalent: (i) d_G is extreme; (ii) all edges of G lie in one class of the transitive closure of
oppositeness; (iii) L(d_G) = 4.

*Proof.* (i) ⇒ (ii) is a theorem of Lomonosov and Sebő [LS93, Corollary 1(c) of Theorem 5]. (ii) ⇒ (iii): let ab,
cd be opposite. The two numbers differ by one because cd is an edge; name the ends so that d_G(a, d) = d_G(b, c) = j
and d_G(a, c) = d_G(b, d) = j + 1. If j = 0 the two edges coincide, so a, b, c, d are distinct, and the triples
(a, d, c), (a, b, c), (b, a, d), (b, c, d) are tight and lie in W = {a, b, c, d}. As in the proof of Theorem 3(a)
they give x_ab = x_cd, so W forces the classes of ab and cd equal, and the rest of that proof applies without
change. (iii) ⇒ (i) is Proposition 2(ii). ∎

Oppositeness is weaker than "opposite on an even isometric cycle": it asks only that four paths of the cycle be
geodesics [LS93, p. 223]. So for bipartite graphs extremality is decided by deductions on four points, and graphic
extreme rays of locality above 4 (such as K_1 ∨ C_m² in Comp. 5) are not bipartite. For non-bipartite graphs [LS93]
gives no such description. The corollary was also tested on 600 random connected bipartite graphs with 5 to 10
nodes (215 of them extreme): the three conditions agree on all of them (`bipartite_check.py`).

Part (b) of Theorem 3 is the case p = 1/2 of Avis's density theorem [A80, Thm 3.3], with the stronger conclusion L = 4; the
argument follows Avis's and treats explicitly the pairs of edges with a common endpoint.

**Remark (finite n).** The union bound in (b) is effective only for n in the thousands, but the conclusion sets in
much earlier (Comp. 4 below): of 300 samples of G(n, 1/2) each, the shares with d_G extreme are 0.7%, 6%, 23%, 61%,
81%, 91%, 99.3%, 100% for n = 6, 8, 10, 12, 14, 16, 20, 24, and all but one of these 1,383 rays have L = 4.

## 4. Locality is unbounded

**The family C_t.** For odd t ≥ 9 let C_t be the following function on the 2t points A_i, B_i (i ∈ Z_t), where
|i − j| denotes the cyclic distance and offsets o are taken in (−t/2, t/2):

| pair | distance |
|---|---|
| A_i, A_j | 16 if \|i − j\| = 1; 12 if \|i − j\| = 2; 8 if \|i − j\| ≥ 3 |
| B_i, B_j | 10 if \|i − j\| = 1; 20 if \|i − j\| = 2; 22 if \|i − j\| ≥ 3 |
| A_i, B_{i+o} | 13, 11, 7, 9, 19 for o = −2, −1, 0, 1, 2; 15 if \|o\| ≥ 3 |

C_t is invariant under the rotation i ↦ i + 1 and has no reflection symmetry. C_∞ denotes the same rule on the
line (i ∈ Z, ordinary offsets).

**Theorem 4.** (a) For every odd t ≥ 9, C_t is a metric and spans an extreme ray of MET_2t.
(b) For every odd t ≥ 9 and every s ≤ t/6, the level-s closure of C_t is not total. Hence L(C_t) > t/6 and

    sup { L(d) : d an extreme ray of MET_n } > n/12   for every n = 2t, t odd, t ≥ 9;  in particular it is unbounded.

(c) L(C_t) = 2t for every odd t ≥ 9: no proper subset of the points proves extremality. (Computer-assisted: for
t ≤ 21 by exact computation of the level-(2t − 1) closure; for t ≥ 23 by the proof below, which uses exact finite
checks in Q(λ).)

**Corollary.** No test that proceeds by s-local deductions, for any fixed s, characterises the extreme rays of the
metric cone; by Lemma 1 the same holds for the vertices of m_n adjacent to a cut. Moreover
max { L(d) : d extreme in MET_n } = n for every n ≡ 2 (mod 4), n ≥ 18.

*Proof of (a).* *Patterns.* A distance of C_t depends on the kinds of the two points and on their offset capped at
±3. For t ≥ 9 every configuration of three points, described by kinds and capped offsets, occurs already in C_9
(two of the three cyclic gaps determine the capped configuration, and all combinations with gaps 0, 1, 2 or "at
least 3" are realised when t = 9), and the same configurations occur in C_∞. Therefore the triangle inequalities,
and the list of types of tight triples, need to be checked only for t = 9; the check (V1 in `family_C_proof.py`)
shows that C_9 is a metric and that there are 11 types of tight triples, written long = short + short:

    A_iA_{i+1} = A_iA_k + A_kA_{i+1} (k far from both);            A_iA_{i+1} = A_iB_{i+1} + B_{i+1}A_{i+1};
    A_iB_{i+2} = A_iA_{i+2} + A_{i+2}B_{i+2} = A_iA_{i+3} + A_{i+3}B_{i+2} = A_iB_{i+1} + B_{i+1}B_{i+2};
    A_iB_j = A_iA_j + A_jB_j (|i − j| ≥ 3);
    B_iB_{i+2} = B_iA_{i+2} + A_{i+2}B_{i+2} = B_iA_{i+1} + A_{i+1}B_{i+2} = B_iB_{i+1} + B_{i+1}B_{i+2};
    B_iB_j = B_iA_i + A_iB_j (|i − j| ≥ 3; also with i and j exchanged);    B_iB_{i+3} = B_iA_{i+2} + A_{i+2}B_{i+3}.

*The A-pairs.* Let x be a solution of the tight system. Write f(i, k) = x(A_iA_k) for |i − k| ≥ 3 and
ρ_i = x(A_iA_{i+1}). By the first type, ρ_i = f(i, k) + f(k, i + 1) whenever k − i ∈ [4, t − 3]. For
k − i ∈ [4, t − 4] this gives four equations for the two pairs {i, i+1} and {k, k+1}:
ρ_i = f(i,k) + f(i+1,k) = f(i,k+1) + f(i+1,k+1) and ρ_k = f(i,k) + f(i,k+1) = f(i+1,k) + f(i+1,k+1), hence
f(i+1, k) = f(i, k+1) and f(i, k) = f(i+1, k+1). The second identity shows that f(i, i + δ) does not depend on i
for δ ∈ [4, t − 4], and the first, with δ = 4 and δ = t − 4, extends this to δ = 3 and δ = t − 3 (here t ≥ 9 is
used). So f(i, i + δ) = f(δ) with f(δ − 1) = f(δ + 1) for δ ∈ [4, t − 4], and f(δ) = f(t − δ) because the two
offsets describe the same pair. As t is odd, δ and t − δ have different parity, so f is constant, say α, and
ρ_i = 2α.

*The recurrence.* Put s_i = x(A_iB_i), p_i = x(A_iB_{i+1}), q_i = x(A_iB_{i+2}), m_i = x(A_iB_{i−1}),
w_i = x(A_iB_{i−2}), b_i = x(B_iB_{i+1}), c_i = x(B_iB_{i+2}), e_i = x(A_iA_{i+2}). The tight triples give
p_i = 2α − s_{i+1}; q_i = e_i + s_{i+2} = α + m_{i+3} = p_i + b_{i+1}; x(A_iB_j) = α + s_j and
x(B_iB_j) = s_i + s_j + α for |i − j| ≥ 3; c_i = w_{i+2} + s_{i+2} = m_{i+1} + p_{i+1} = b_i + b_{i+1};
s_i + s_{i+3} + α = w_{i+2} + p_{i+2}. Hence m_{i+3} = q_i − α, b_{i+1} = q_i − 2α + s_{i+1} and
w_{i+2} = s_i + 2s_{i+3} − α, and the two expressions of c_i = b_i + b_{i+1} through m, p and through w, s become

    q_{i−1} + q_i − q_{i−2} = 5α − s_i − s_{i+1} − s_{i+2},      q_{i−1} + q_i = 3α − s_{i+1} + s_{i+2} + 2s_{i+3},

whence q_i = −2α + s_{i+2} + 2s_{i+4} + 2s_{i+5} and then

    s_i + 2 s_{i+3} + s_{i+4} = (7/2) α      for all i ∈ Z_t.                                            (REC)

*Rigidity.* The characteristic polynomial of (REC) is z⁴ + 2z³ + 1 = (z + 1)(z³ + z² − z + 1). The cubic has no
rational root, so it is irreducible, and no cyclotomic polynomial has degree 3; hence its roots are not roots of
unity. For odd t, −1 is not a t-th root of unity either. So the circulant system (REC) on Z_t has only the constant
solution s_i = (7/8)α, and then p, q, m, w, b, c, e and all far pairs are determined by α. The solution space of the
tight system is a line, i.e. C_t is extreme. ∎

*Proof of (b).* *Solutions on the line.* Let α ∈ R and let (s_j), j ∈ Z, satisfy (REC) for all i ∈ Z. Define x on the
pairs of C_∞ by the formulas above (x = α on A-pairs at distance ≥ 3, 2α at distance 1, and so on; the full list is
in `family_C_proof.py`). Then x satisfies every tight triple of C_∞: by the pattern argument it suffices to check the
triples inside a window of 13 positions, and for each of these 397 triples the equation is a rational combination of
instances of (REC) (check V2, exact). Let λ ≈ −1.8393 be the real root of z³ + z² − z + 1. Then α = 8,
s_j = 7 + λ^j is such a sequence; write D(P) = (x(P) − d(P))/d(P) for the resulting relative deviation of a pair P
of C_∞. Call two pairs of C_∞ *related* if both are A-pairs at distance 1 or ≥ 3, or if they are A_iB_j and
A_{i′}B_j with |i − j|, |i′ − j| ≥ 3.

*Lemma S.* D(P) = D(Q) only if P = Q or P and Q are related.
*Proof.* D vanishes on the A-pairs at distance 1 or ≥ 3, and D(A_iB_j) = λ^j/15 for |i − j| ≥ 3. For each of the
other eight types of pairs, D of the pair at position i is λ^i·κ with an explicit κ ∈ Q(λ), and all nine values of
κ (including 1/15) are nonzero. An equality between two such pairs reads κ = λ^k κ′; since |λ| > 1 this determines k
up to finitely many candidates, bounded rigorously by rational enclosures of λ, and none of them gives equality in
Q(λ) (check V3, exact). For a B-pair at distance g ≥ 3, D = λ^i(1 + λ^g)/22; an equality with a pair of another type
reads λ^h(1 + λ^{−g}) = 22κ′ for an integer h, where |1 + λ^{−g}| ∈ [1 − |λ|^{−3}, 1 + |λ|^{−3}] bounds h and each h
leaves at most one g; again no equality occurs (V3). For two different B-pairs at distances ≥ 3, λ^i + λ^j =
λ^{i′} + λ^{j′}: if the largest exponent occurs on both sides the pairs coincide, and otherwise the largest term
exceeds the sum of the absolute values of the other three, because |λ|^{−1} + |λ|^{−3} + |λ|^{−4} < 0.8. Finally
D ≠ 0 for every pair that is not an A-pair at distance 1 or ≥ 3. ∎

*The partition.* Let π be the partition of the pairs of C_t whose classes are: the set of all A-pairs at cyclic
distance 1 or ≥ 3; for each j the set of pairs A_iB_j with |i − j| ≥ 3; and all other pairs as singletons. π is not
total. We show that π is closed under the merges of level s when t ≥ 6s; since cl_s is the finest partition closed
under these merges (Proposition 2(i)), cl_s refines π and is not total.

Let W be a set of at most s points of C_t. Its points occupy at most s positions of Z_t, which cut the cycle into
at most s runs of free positions with t − s ≥ 5s positions in total, so some run of 5 consecutive positions is
free. Cutting the cycle inside this run identifies the positions of W with integers in an
interval of t − 5 consecutive integers, and this identification ψ: W → C_∞ preserves distances: two points at line
offset o, 1 ≤ o ≤ t − 6, have cyclic offset o if o < t/2, and o − t otherwise; in the second case o ≥ 5 and
t − o ≥ 6, so the pair is far (offset of absolute value at least 3) both on the line and on the cycle, where the
distance does not depend on the offset. Hence the tight triples inside W are tight triples of C_∞, and for every
real c the function u_c(P) = 1 + c·D(ψP) on the pairs inside W is a solution of T_W in the normalised variables (a
combination of the solutions d and x). It is constant on the classes of π: D = 0 on the first class, and
D(ψ(A_iB_j)) = λ^{ψ(j)}/15 on the classes of the second kind. So u_c solves T_W(π). If W forced two different
classes C ∋ P, C′ ∋ Q of π to be equal, we would have u_c(P) = u_c(Q) for all c, i.e. D(ψP) = D(ψQ), and by Lemma S
the pairs ψP, ψQ would be equal or related, i.e. P and Q would lie in the same class of π. So no merge is forced, π
is closed at level s, and L(C_t) > s for every s ≤ t/6. ∎

*Proof of (c).* For t ≤ 21 the level-(2t − 1) closure was computed in rational arithmetic and is not total
(`family_C.py`). Let t ≥ 23. As in (b) it suffices to show that π is closed under the merges of level 2t − 1, i.e.
that W = V − v forces no two classes of π to be equal, and by the rotation we may take v = A_0 or v = B_0. For each
of the two we construct a solution x of T_W(π) with x = 0 on the first class of π (a deviation from d, as D in (b))
whose relative values D(C) = x(C)/d(C) on the classes C of π inside W are pairwise different; then u = 1 + cD
separates any two classes. Indices are taken modulo t and written with representatives near 0.

*Step 1: parametrisation.* Let numbers σ_j, q_j (j ∈ Z_t) be given, and in addition p_{−1}, p_0 if v = A_0, and
w_{−1} if v = B_0. Put p_i = −σ_{i+1} for the other i, and

    m_i = q_{i−3},   b_i = q_{i−1} − p_{i−1},   w_i = σ_{i−2} + σ_{i+1} − p_i,   c_i = b_i + b_{i+1}

(for v = B_0: w_{−1} as given, and c_{−1} = w_1 + σ_1). Define x on the pairs inside W by x = 0 on the A-pairs at
distance 1 or ≥ 3, x(A_iB_i) = σ_i, x(A_iB_{i+1}) = p_i, x(A_iB_{i+2}) = q_i, x(A_iB_{i−1}) = m_i,
x(A_iB_{i−2}) = w_i, x(B_iB_{i+1}) = b_i, x(B_iB_{i+2}) = c_i, x(A_iA_{i+2}) = q_i − σ_{i+2}, and x(A_iB_j) = σ_j,
x(B_iB_j) = σ_i + σ_j for |i − j| ≥ 3. (For v = A_0 the numbers σ_0, q_0, p_0 belong to pairs through A_0; they
enter as σ_0 = x(A_iB_0) for i far from 0, q_0 = x(A_3B_2) and q_0 − p_0 = x(B_1B_2). For v = B_0 quantities with an
index that would give a pair through B_0 are not used, and x(A_{−2}A_0) is arbitrary.) Consider the equations

    (5a_i)  c_i = w_{i+2} + σ_{i+2},        (5b_i)  c_i = m_{i+1} + p_{i+1}.

*Lemma P.* x is constant on the classes of π, and it satisfies all tight triples inside W if 5a_i and 5b_i hold for
all i except 5a_{−2}, 5b_{−1} when v = A_0, and except 5a_0, 5a_{−1}, 5a_{−2}, 5b_0, 5b_{−2} when v = B_0.
*Proof.* Go through the 11 types of tight triples in the proof of (a). The triples A_iA_{i+1} through A_k read
0 = 0; those through B_{i+1} read p_i + σ_{i+1} = 0, and the two with i ∈ {−1, 0} (for v = A_0), resp. the one with
i = −1 (for v = B_0), contain v. The three triples for A_iB_{i+2} are the definitions of x(A_iA_{i+2}), of m_{i+3}
and of b_{i+1}. A_iB_j through A_j reads σ_j = σ_j. The triples for B_iB_{i+2} are the definition of c_i (through
B_{i+1}), 5a_i (through A_{i+2}) and 5b_i (through A_{i+1}). B_iB_j through A_i reads σ_i + σ_j = σ_i + σ_j, and
B_iB_{i+3} through A_{i+2} is the definition of w_{i+2}. The triples that contain v are exactly those in which the
statement uses a free number or omits an equation: for v = A_0, the triples (A_{−1}, B_0, A_0), (A_0, B_1, A_1),
(A_0, A_3, B_2), (A_0, B_1, B_2), (A_i, A_0, B_0) free p_{−1}, p_0, q_0 and σ_0, and (B_{−2}, A_0, B_0),
(B_{−1}, A_0, B_1) are 5a_{−2}, 5b_{−1}; for v = B_0, the triple (B_{−1}, B_0, B_1) frees c_{−1}, which is then
defined by 5a_{−1}; (B_{−3}, A_{−1}, B_0) frees w_{−1}; (A_{−2}, A_0, B_0) is the only triple with the pair
A_{−2}A_0; and 5a_0, 5a_{−2}, 5b_0, 5b_{−2} concern pairs through B_0. ∎

*Step 2: the solution.* If q_{i−2}, q_{i−1}, q_i are given by q_j = σ_{j+2} + 2σ_{j+4} + 2σ_{j+5}, the p's by
p_i = −σ_{i+1}, and σ_{i+1} + 2σ_{i+4} + σ_{i+5} = 0, then 5a_i and 5b_i hold (the computation in the proof of
(a)). Let j_0 = 3 for v = A_0 and j_0 = 2 for v = B_0, ε = λ^(−t), and put

    σ_j = g·(−1)^j + a·λ^(j−t)   for j_0 ≤ j ≤ t − 1,        q_j = σ_{j+2} + 2σ_{j+4} + 2σ_{j+5}   for 8 ≤ j ≤ t − 8,

with (g, a) = (1 − ε, 2) for v = A_0 and (g, a) = (0, 1) for v = B_0. Both (−1)^j and λ^j satisfy the recurrence,
so 5a_i and 5b_i hold for 11 ≤ i ≤ t − 9. The remaining unknowns are σ_j for 0 ≤ j < j_0 (j = 1 only, for
v = B_0), q_j for |j| ≤ 7, and p_{−1}, p_0 resp. w_{−1}: 20 resp. 16 unknowns. The remaining equations are those
5a_i, 5b_i with −8 ≤ i ≤ 10 that are required by Lemma P: 36 resp. 33 linear equations with rational coefficients,
whose right-hand sides are of the form r_0 + r_1ε with r_0, r_1 ∈ Q(λ) that do not depend on t. They are solvable
with solutions of the same form (check W1 in `family_C_top.py`; for v = A_0 the system has rank 19 and one
solvability condition, which is (1 − ε)a = 2g and explains the choice of g; for v = B_0 the solution is unique).
By Lemma P this gives a solution x of T_W(π) for every odd t ≥ 23. As a guard against slips in Lemma P, the solution
was instantiated on the real cycle for t = 19, 21, 23, 25, 27, 31 and every tight triple of C_t − v was verified
exactly (W2). The same check confirms, class by class, that the symbolic values used in Step 3 are the values on
the cycle.

*Step 3: the values are pairwise different.* Away from the break the values of x follow the formulas of (a) with
s = σ, so for a pair P whose formula involves only σ_j on the stretch, at position t − k (k ≥ 1),

    D(P) = ± g·κ′ + a·κ·λ^(−k),

where κ ∈ Q(λ) and κ′ ∈ Q depend only on the type of the pair (κ is the constant of Lemma S, κ′ the corresponding
constant for the root −1) and the sign on the parity of k. The pairs for which this fails are 40 (v = A_0) resp. 27
(v = B_0) pairs near the break, with D = r_0 + r_1ε, and the far B-pairs, whose value is the sum of the values of
σ at their two positions divided by 22. So an equality D(P) = D(Q) between two classes is an equation

    G_0 = Σ_i c_i·λ^(−k_i)

in at most five integer unknowns k_i (the positions involved, and t itself for the terms in ε), with
G_0, c_i ∈ Q(λ) taken from a finite list: 2,305 equations for v = A_0 and 752 for v = B_0. Since |λ| > 1 the
solutions of such an equation can be listed completely: if |G_0| exceeds the sum of the largest possible values of
the terms there is none; otherwise one branches on the largest term, fixing its exponent at its least admissible
value or raising that value; if G_0 = 0, one divides by the largest term. All bounds use rational enclosures of λ,
and equalities are decided exactly in Q(λ). The search (check W3) finds 109 resp. 53 solutions when the ranges of
the k_i are relaxed to k_i ≥ 1, t ≥ 23; in 92 resp. 38 of them P and Q are the same class, and in the other 17
resp. 15 one of the pairs sits at one of the positions near the break where the formula does not apply (these
pairs are among the 40 resp. 27, with their true values). A pair just left of the break whose formula involves
only σ's to the right of it (for example A_{−1}A_1, with σ_3 and σ_4) belongs to the first kind with k = t + 1; the
ranges of k are set accordingly. So D takes different values on different classes, for
every odd t ≥ 23. (For v = B_0 the pair A_{−2}A_0 is excluded; it occurs in no tight triple inside W, so nothing
forces its class to equal another.) Hence W forces no merge, π is closed at level 2t − 1, cl_{2t−1} refines π,
and L(C_t) = 2t. ∎

The search procedure was tested on 300 equations with planted solutions (all recovered), and by duplicating one
class of each kind under a different name (every duplicate is reported as a coincidence); see `--selftest`.

*Second implementation.* Checks W1–W3 were repeated by a second program written from the text of this proof
(`family_C_top_check.py`; it shares no code with the first). It differs in three ways. (i) It fixes R = 10 and
treats every pair with an index within R of the removed point as a class of its own with an explicit value
r_0 + r_1ε, computed pair by pair from the formulas of Step 1 (354 resp. 334 such classes); all other pairs have
R < k < t − R, where the formula D = ±gκ′ + aκλ^(−k) applies for every type, so no list of exceptional positions is
needed. (ii) The equation G_0 = Σ c_i λ^(−k_i) is solved by another method: some term of a solution has absolute
value at least |G_0|/(number of terms); this term and its exponent are enumerated, and one recurses. (iii) A
solution is discarded only if P and Q are the same class, if an exponent violates t − k > R (or the corresponding
bound for a far B-pair), or if the two points of a far B-pair are closer than 3; every other solution would be
reported. Of 86,799 resp. 66,096 equations, 373 resp. 400 have solutions (69 resp. 36 the same class, 304 resp. 364
out of range), and none is reported. The cut solutions of the two programs are equal. The second program builds
the solution on the real cycles t = 23, 25, 27, 29, 31, 37, 45 with arrays indexed modulo t, verifies every tight
triple, and checks that the classes of π inside W correspond one to one, with equal values, to the instances of its
list of classes that are in range at t. Its search was compared with exhaustive enumeration in a box on 150 random
equations (261 solutions, none missed), and it reports duplicated classes and classes planted to coincide at one
value of t.

**Remarks.** (1) Part (b) is implied by (c); we keep it because its proof needs only Lemma S, while (c) relies on a
larger computation. (2) The level-(2t − 1) closure of C_t has exactly (t² + 13t + 2)/2 classes for every odd t from
9 to 21, the number of classes of π: in these cases cl_{2t−1} = π.
(3) Replacing d(A_i, A_{i+2}) = 12 by 16 gives a second family, an extreme ray with L = 2t for every odd t from 9
to 21 by the same computation. (4) How the family was found: the two-orbit metrics whose distances depend only on
offsets capped at ±3 are, for all large t, the points of a fixed 12-dimensional cone of "patterns of radius 2"
(`pattern_hunt.py`); of its 26,319 extreme rays with positive distances, 9,464 give extreme rays of MET_2t for at
least two t between 9 and 14, and 96 pass two filters (classes left unmerged on the cycle, and no merge forced on an
open stretch); 8 of the 96 have L = 2t at t = 9, 11, 13, and they are C_t, its variant (3), their mirror images and
the versions with A and B exchanged. (5) Chirality matters: the mirror-symmetric family K_t of Comp. 6 reduces in the
same way to a recurrence, but all its characteristic roots are roots of unity, every solution on an open stretch is
periodic, and its locality stays bounded. (6) Locality is not monotone under restriction. By Avis's embedding
(Section 5b), C_t is the restriction of the metric of a graph F(G) on more points, and the proof of [A80, Lemma 3.4]
shows that F(G) is 1-ic-colorable, so L(d_F(G)) = 4 by Theorem 3(a). Thus a ray whose extremality has no proof on
fewer than all of its points is a restriction of a ray whose extremality is proved four points at a time. The
additional points serve as auxiliary variables; L measures deductions among the given points only, and Theorem 4
says nothing about tests that are allowed to add points. Such tests are discussed in Remark (3) of Section 5c: they
are either unsound or a form of deduction with longer relations.

## 5. A counting bound for small-choice generators

**Theorem (Avis [A80, Thm 3.3]).** Let 0 < γ < 1/5 and n^(−1/5+γ) ≤ p ≤ 1 − n^(−1/4+γ). Then the shortest-path
metric of the random graph G_{n,p} spans an extreme ray of MET_n with probability 1 − o(1).

With p = 1/2 all labelled graphs are equally likely, so 2^C(n,2)·(1 − o(1)) labelled graphs G have d_G extreme
[A80, p. 138]; this lower bound on the number of extreme rays of MET_n is quoted in this form in [CL25, §5.1]. The
case p = 1/2 is also proved by Theorem 3(b), so what follows does not depend on [A80, Thm 3.3].

**Proposition 5.** The number v(n) of orbits of vertices of m_n satisfies
v(n) ≥ 2^C(n,2)·(1 − o(1)) / (n!·2^(n−1)) = 2^(n²/2 − O(n log n)).

*Proof.* Distinct labelled graphs have distinct metrics d_G, and G is recovered from x_G = (2/τ)d_G as the set of
pairs of smallest value, so the vertices x_G of Lemma 1 are distinct. An orbit has at most n!·2^(n−1) elements. ∎

**Upper bound.** Cizma and Linial [CL25, Thm 5.5] prove that MET_n has at most 2^(2.38 n²(1+o(1))) faces. Hence the
number of extreme rays of MET_n, and the number of orbits of vertices of m_n adjacent to a cut, is 2^Θ(n²), with
the constant in the exponent between 1/2 and 2.38.

**Definition (generator).** A *generator* consists of sets O_n of *objects on n nodes* (n ≥ 1), a finite set E of
exceptional objects, r *rules*, and two constants: the largest number a_0 ≥ 1 of inputs of a rule and the *overlap*
q ≥ 0. Each rule maps a tuple (objects on n_1, ..., n_a nodes, choice c ∈ {1, ..., C(n)}) with a ≤ a_0,
1 ≤ n_i ≤ n − 1 and n_1 + ... + n_a ≤ n + q to an object on n nodes or to nothing. The generated objects are the
exceptional ones and the outputs of rules applied to generated objects. A map from generated objects on n nodes to
orbits of m_n (possibly partial) says which orbit, if any, an object *produces*. The *choice* of the generator is
b(n) = log₂ C(n) bits.

Nothing is assumed about the objects: they may be vertices, points of m_n that are not vertices, graphs, or partial
structures. A rule with one input adds one or more nodes to an object. A rule with two inputs on n_1 and n_2 nodes
that identifies k nodes of the first with k nodes of the second has n = n_1 + n_2 − k, so the condition says k ≤ q:
gluing along at most q common points is allowed, gluing along more is not. Restriction-keeping moves, families with
boundedly many integer parameters of size polynomial in n, and the generator of Comp. 9 for a fixed denominator are
generators with one input per rule and b(n) = O(log n).

**Theorem 6.** Let a generator have b(n) ≤ (1 − δ)n for some δ > 0 and all large n. Then it produces at most
2^((1−δ)n²/2 + O(n log n)) orbits of m_n, and the share of the orbits of m_n it produces tends to 0. In particular
the number of orbits it misses is unbounded, so no finite list of exceptions completes it.

*Proof.* Let N(n) be the number of generated objects on n nodes; it is finite, by induction on n. Put c = 1 − δ and,
for a constant K chosen below, g(x) = (c/2)x² + K·x·log₂(x + 1) for x ≥ 0. g is convex and increasing, g(0) = 0, and
for n ≥ 1, g(n) − g(n − 1) ≥ cn − c/2 + K·log₂ n, because n·log₂(n + 1) − (n − 1)·log₂ n ≥ log₂ n. We show
N(n) ≤ 2^g(n) for all n ≥ 1.

Let n_2 be such that for n ≥ n_2: b(n) ≤ cn, no exceptional object has n nodes, n > q + 2, and
log₂ n ≥ max(1, 2(q + 1)·log₂(q + 2)). Put C_0 = log₂(r·a_0) + c/2 + c(q + 1)²/2 and choose K ≥ 2a_0 + 2C_0 so large
that N(n) ≤ 2^g(n) for all n < n_2; this is possible because g(n) ≥ K for n ≥ 1, and neither n_2 nor C_0 depends on
K.

Let n ≥ n_2 and suppose N(k) ≤ 2^g(k) for k < n. For fixed sizes (n_1, ..., n_a) the number of input tuples is at
most ∏ N(n_i) ≤ 2^(Σ g(n_i)). The sizes lie in the polytope {x ∈ [0, n − 1]^a : Σ x_i ≤ n + q}, and the convex
function Σ g(x_i) attains its maximum over this polytope at a vertex. At a vertex all coordinates except at most one
are 0 or n − 1; since 2(n − 1) > n + q, at most one coordinate equals n − 1, and then the remaining ones sum to at
most q + 1. As g is increasing, Σ g(n_i) ≤ g(n − 1) + g(q + 1). There are at most a_0·n^(a_0) choices of the sizes,
r rules and 2^b(n) choices, so

  log₂ N(n) ≤ log₂(r·a_0) + a_0·log₂ n + cn + g(n − 1) + g(q + 1).

By the choice of n_2, g(q + 1) = c(q + 1)²/2 + K(q + 1)·log₂(q + 2) ≤ c(q + 1)²/2 + (K/2)·log₂ n. Hence
log₂ N(n) − g(n) ≤ a_0·log₂ n + C_0 − (K/2)·log₂ n ≤ 0, because K/2 ≥ a_0 + C_0 and log₂ n ≥ 1. This proves
N(n) ≤ 2^g(n) = 2^((1−δ)n²/2 + O(n log n)).

The number of orbits produced is at most N(n). By Proposition 5, v(n) ≥ 2^(n²/2 − O(n log n)), so
N(n)/v(n) ≤ 2^(−δn²/2 + O(n log n)) → 0 and v(n) − N(n) → ∞. The exceptions are included in N(n). ∎

**Remarks.** (a) The bound is sharp in the choice up to a constant factor: with b(n) = n − 1 a rule can choose the
neighbourhood of the new node, hence an arbitrary graph, and then the single rule G ↦ x_G produces
2^(n²/2 − O(n log n)) orbits; and by [CL25] a choice of 4.76·n bits per node is enough to index all cut-adjacent
orbits. (b) The theorem does not need the m_9 list or any computation. (c) It is a statement about growth, and the
lists show the growth has begun: v(7), v(8), v(9) = 13, 533, ≥ 1,056,367, successive factors 41 and 1,982. (d) The
bound on the overlap is used, and the theorem says nothing about rules that glue along an unbounded number of common
points. In the proof, bounded overlap is what makes the product of the numbers of inputs small: the sum of the
squares of the input sizes is at most (n − 1)² + (q + 1)². Without it, the pairs of objects on n − 1 nodes alone
number N(n − 1)², and the induction fails. This is not only a defect of the proof. A vertex x of m_n is determined,
up to two possibilities, by its restrictions to V ∖ {a} and V ∖ {b}: the points of m_n with these two restrictions
differ only in the coordinate x_ab and form a segment, and a vertex of m_n on a segment contained in m_n is an
endpoint of it. So a single rule with two inputs, overlap n − 2 and one bit of choice returns every vertex from two
of its restrictions. Such a rule only moves the difficulty to the restrictions, which are not vertices in general
and would have to be generated as well; whether a generator with unbounded overlap and small choice can produce a
positive share of the orbits is not settled by our argument.

**Question 1.** Let r(n) be the number of extreme rays of MET_n. Is log₂ r(n) ~ n²/2, i.e. are almost all extreme
rays graphic on the logarithmic scale, or is lim log₂ r(n)/n² > 1/2? By [CL25] the limit, if it exists, is at most
2.38. On the lists the graphic share of the cut-adjacent orbits is 92%, 20%, 0.52% for n = 7, 8, 9 (Comp. 10), which
suggests that non-graphic rays dominate at least in number. (For vertices of m_n not adjacent to a cut we know only
the trivial bound 2^O(n² log n).)

## 5b. Tests by forbidden restrictions

Locality measures tests that propagate proportionalities. The other simple kind of test of bounded scope does not
propagate anything: it looks at every set of at most s points separately. Such tests are excluded, for every s, by a
theorem of Avis.

**Definition (hereditary test).** Let s ≥ 1 and let 𝒜 be a set of metrics on at most s points, closed under
relabelling. The *hereditary test* with allowed set 𝒜 accepts a metric d, on any number of points, if the
restriction of d to every set of at most s points belongs to 𝒜.

Equivalently, the test forbids the restrictions outside 𝒜; the set 𝒜 is arbitrary and may be infinite, but it is the
same for all n.

**Proposition 7.** A hereditary test that accepts every metric with positive distances spanning an extreme ray of
some MET_n accepts every rational metric with positive distances. In particular, for no s is there a hereditary test
that accepts exactly the extreme rays: on every n ≥ 3 points it accepts metrics that are not extreme, for instance
the metric with all distances equal to 1.

*Proof.* Let d be a rational metric with positive distances on m points. Avis's embedding theorem [A80, Thm 3.5]
states that there are an integer n and a metric D on n ≥ m points, spanning an extreme ray of MET_n, whose
restriction to the first m points is equal to d; the restriction is d itself, not a multiple of it. In Avis's proof,
k is the least positive integer with k·d integral, G is the graph in which every two of the m points are joined by a
path of length k·d_ij, and D = d_F(G)/k for a graph F(G) that contains G isometrically [A80, Lemma 3.4]; so D has
positive distances, and the construction uses that d has. Every restriction of d to at most s points is a
restriction of D to the same points, and belongs to 𝒜 because the test accepts D. So the test accepts d. The metric
with all distances 1 on n ≥ 3 points has no tight triple, so it is not extreme. ∎

**Remarks.** (1) The proposition and Theorem 4 exclude two different kinds of test, and neither implies the other. A
hereditary test that accepts all extreme rays is not sound, for any s: it also accepts metrics that are not extreme.
A test by s-local deduction is always sound (Proposition 2(ii)) and fails to be complete. (2) Zero distances are excluded in the
proposition because the construction in [A80] needs paths of positive length. They can be admitted: a metric with
zero distances is extreme iff its restriction to one point from each class of points at distance zero is extreme
[A80, Thm 4.2], so the embedding extends by repeating points. We do not need this. (3) The proposition uses
that the allowed set does not depend on n. It does not cover tests that require some configuration to be present,
Boolean combinations of forbidden and required configurations, or tests that count configurations; and Theorem 4
does not cover deductions of relations with more than two terms. A statement that no test of bounded scope of any
kind characterises the extreme rays would need a definition of "test of bounded scope" that includes all of these,
and we do not have one; with the definition of finite model theory (a bounded number of variables, with counting
and recursion) the statement is false (Proposition 10).

## 5c. Stronger local tests

Theorem 4 concerns deductions of two-term proportionalities. This section places it among stronger kinds of test of
bounded scope. In short: the obstruction is specific to two-term deduction. If the sets of s points may exchange
linear relations with more than two terms, four or five points suffice for every extreme ray of the lists up to nine
points that we tested, including those of largest locality, and ten points suffice for every C_t (Theorem 9; five for C_9, C_11 and C_13); and if counting and
recursion are allowed, a bounded number of variables suffices for every metric, by a known theorem on the
definability of rank. Whether deduction with longer relations has bounded scope on all extreme rays is open.

**Definition (linear closure, linear locality).** Let d be a metric with positive distances on V, |V| = n ≥ 4, let
s ≥ 4 and let π be a partition of the pairs. For a set W of at most s points, T_W(π) is the system of Section 3, in
the variables u_C of the classes C that contain a pair inside W. A family (S_W) of subspaces of the solution spaces
of the systems T_W(π) is *consistent* if for all W, W′ the projections of S_W and of S_W′ to the variables they have
in common are equal. Sums of consistent families are consistent, so there is a largest one, (S*_W(π)); it is reached
from the full solution spaces by repeatedly replacing S_W by the set of its elements whose projection to the common
variables lies in the projection of S_W′, in any order. W *linearly forces* C = C′ under π if u_C = u_C′ on S*_W(π).
The *level-s linear closure* is the finest partition that is closed under merging C and C′ whenever some W linearly
forces C = C′, and the *linear locality* L_lin(d) is the least s ≥ 4 for which it has a single class; L_lin(d) = ∞
if there is none.

This is the level-s closure of Section 3 with one addition: two sets W, W′ may exchange any linear relation among
the variables they share, not only equalities of two variables. Dually, the procedure derives linear relations
among the u_C, each supported on the classes that meet one set of at most s points.

**Proposition 8.** (i) The level-s linear closure is well defined, and it is coarser than cl_s(d). (ii) (Soundness)
If two pairs p, q are in one class of it, then x_p/d_p = x_q/d_q for every solution x of T(d). Hence L_lin(d) < ∞
implies that d is extreme. (iii) d is extreme iff L_lin(d) ≤ n, and then 4 ≤ L_lin(d) ≤ L(d).

*Proof.* (i) Let π refine π′. A solution of T_W(π′) is a solution of T_W(π) that is constant on the classes of π′,
and a class of π that meets both W and W′ lies in a class of π′ that meets both; so a consistent family for π′ is
one for π, and S*_W(π′) is contained in S*_W(π) under this identification. Hence a merge that is linearly forced
under π is forced, or already made, under π′, and the argument of Proposition 2(i) applies. Since S*_W(π) is
contained in the solution space of T_W(π), a merge forced in the sense of Section 3 is linearly forced, which gives
the comparison with cl_s. (ii) By induction on the merges: if u is constant on the classes of π for every solution
of T(d), the restrictions of these solutions form a consistent family, so they lie in S*_W(π), and a linearly
forced merge preserves the property. (iii) For s = n the set V belongs to the family and T_V(π) is T(d) on the
classes of π, so the closure is total iff d is extreme; the bounds follow from (i) and the definition. ∎

**Computation (linear locality on the lists).** L_lin was computed in rational arithmetic for every extreme ray of
MET_k, k ≤ 8 (Comp. 1; L_lin = 4 when L = 4), and for the 428 rays of Comp. 2 on nine points with L ≥ 8, which
include the two with L = 9.

| rays | L | number | L_lin = 4 | L_lin = 5 |
|---|---|---|---|---|
| MET_5, MET_6, MET_7 (all) | 4, 5 | 37 | 37 | |
| MET_8 (all) | 4 | 2,691 | 2,691 | |
| | 5 | 992 | 968 | 24 |
| | 6 | 67 | 67 | |
| | 7 | 1 | 1 | |
| m_9 list, 9 points | 8 | 426 | 358 | 68 |
| | 9 | 2 | 2 | |

So every ray tested has L_lin ≤ 5, and the two rays whose extremality has no two-term proof on fewer than all nine
points are proved four points at a time once longer relations may be exchanged. Checks of the program: without the
exchange step it reproduces L for each of the 1,061 rays with L ≥ 5 on at most 8 points; on 400 metrics that are
not extreme it ends with more than one class at every level; and on 150 rays it ends with one class at level k
(`linear_locality.py`).

**Computation (linear locality of C_t).** (a) *Exact values.* The complete level-s linear closure of C_t, over
all sets of s points, was computed in rational arithmetic in the dual form: a pool of linear relations among the
u_C is closed under passing to the minimal-support relations of each set, and under the rotation. At level 4 it is
the partition π of the proof of Theorem 4, with (t² + 13t + 2)/2 classes, for t = 9, 11, 13, 15, 17; so relations
with more than two terms add nothing on four points. At level 5 a single class remains for t = 9 (128,088
relations) , t = 11 (395,945 relations) and t = 13 (1,188,876 relations). Hence

  L_lin(C_9) = L_lin(C_11) = L_lin(C_13) = 5,   L_lin(C_t) ≥ 5 (t = 15, 17),

while L(C_t) = 18, 22, 26. Checks of the program: every relation derived was tested against a basis of
the solutions of the full system T(d); and for t = 10, where C_t is a metric but not extreme (the solution space
has dimension 3), a run at level 5 stopped after about 190,000 relations, all of them valid on that space, with 128
classes (`linear_full.py`). The level-5 computation for t ≥ 15 was not done.

(b) *Upper bounds from small families of sets.* With the sets of the proof of Theorem 4 on at most four points, the
t sets {B_0, …, B_4} ∪ {B_j, …, B_{j+4}} and the t sets of the points at five consecutive positions, a single class
remains for t = 9, 11, 13, 15, 17; so L_lin(C_t) ≤ 10 for these t (`linear_family.py`).

(c) For larger t we have a cruder scheme. For windows of five consecutive positions, let W_{a,j} be the set of the
points A_i, B_i with i ∈ [a, a + 5) or i ∈ [j, j + 5), at most 20 points. Starting from the discrete partition and
using only the t sets W_{0,j}, with exchanges between W_{0,j} and W_{0,j+1}, every S_{W_{0,j}} becomes the line
through d: in rational arithmetic for t = 11, 13, 15, 17, 21, 25, 29, 33, 37, and modulo 2³¹ − 1 for t = 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 37, 41, 45, 51. Then all pairs inside W_{0,j} are
merged; by the rotation the same holds for every W_{a,j}, every pair lies in one of these sets, and consecutive sets
share pairs, so a single class remains. Hence L_lin(C_t) ≤ 20 for these t. For even t the same run ends with spaces
of dimension 3 and proves nothing (`linear_width.py`).

**Theorem 9.** L_lin(C_t) ≤ 10 for every odd t ≥ 9, while L(C_t) = 2t. (Computer-assisted: for t ≤ 17 by the
computation (b) above; for t ≥ 19 by the proof below, which uses one exact finite check.)

*Proof.* Let t ≥ 19 be odd and s = 10. Two facts about the largest consistent families. (F1) If a linear relation
among class variables holds on S*_W(π) and each of its variables belongs to a class that meets W′, then it holds on
S*_{W′}(π), because the two spaces have the same projection to their common variables. (F2) If π′ is coarser than
π, a relation that holds on S*_W(π) holds on S*_W(π′), with the variables of merged classes identified (proof of
Proposition 8(i)). Consequently, if the level-10 linear closure is coarser than a partition π′ and a merge is
linearly forced under π′, the merge is made in the closure.

*Step 0: the partition π.* The level-4 closure is coarser than the partition π of the proof of Theorem 4, and so is
the level-10 linear closure (Proposition 8(i)). Indeed, the step "The A-pairs" of the proof of Theorem 4(a) uses,
for each conclusion, the equations inside one set {A_i, A_{i+1}, A_k, A_{k+1}}, and its conclusions are equalities
of two normalised variables; and for i, i′ far from j the two equations 15 u(A_iB_j) = 8u_α + 7u(A_jB_j) and
15 u(A_{i′}B_j) = 8u_α + 7u(A_jB_j) inside {A_i, A_{i′}, A_j, B_j} force u(A_iB_j) = u(A_{i′}B_j). Write u_α for
the variable of the class of the A-pairs at distance 1 or ≥ 3 and u_(j) for that of the class of the pairs A_iB_j,
|i − j| ≥ 3. Since x(A_iB_j) = α + s_j on these pairs, (REC) reads, in these variables,

  u_(i) + 2u_(i+3) + u_(i+4) = 4u_α.   (REC_i)

*Step 1: the recurrence is derived locally.* Let I_a be the set of the ten points A_j, B_j, j ∈ [a, a + 5). All four
variables of (REC_i) belong to classes that meet I_i. Claim: (REC_i) holds on S*_{I_i}(π). By the rotation let
i = 0. Start from the solution spaces of T_{I_a}(π) for the five sets I_a, −2 ≤ a ≤ 2, and make this family of five
spaces consistent by mutual restriction; the result contains S*_{I_a}(π), since the spaces S*_{I_a}(π) form a
consistent family. The five sets lie in 9 consecutive positions; for t ≥ 11 the distances between their points, the
tight triples and the classes of π shared by them are those of the corresponding points of C_∞, so this computation
does not depend on t. It was done in rational arithmetic (for t = 31 and t = 41): the space of I_0 ends with
dimension 5 and (REC_0) holds on it (check U1 in `linear_uniform.py`; with three sets, −1 ≤ a ≤ 1, it does not).

*Step 2: propagation.* Put y_j = u_(j) − u_α, so that (REC_i) is y_i + 2y_{i+3} + y_{i+4} = 0. Define vectors
c_k ∈ Q⁴, k ≥ 0, by c_k = e_k (unit vectors) for k ≤ 3 and c_{k+4} = −c_k − 2c_{k+3}. Claim: for 0 ≤ k ≤ t + 3 the
relation

  y_{k mod t} = c_{k,0} y_0 + c_{k,1} y_1 + c_{k,2} y_2 + c_{k,3} y_3   (R_k)

holds on S*_W(π) for every set W of at most 10 points that meets the classes α, (0), (1), (2), (3) and (k mod t).
For k ≤ 3 it is trivial. Let 0 ≤ k ≤ t − 1 and suppose (R_k) and (R_{k+3}) hold. Let P be the set of the positions
0, 1, 2, 3, k, k + 3, k + 4 modulo t. The positions at cyclic distance at most 2 from P lie in the two intervals
[−2, 5] and [k − 2, k + 6], of 17 positions together, so at least two positions y, y′ are at distance ≥ 3 from P;
two such positions are not at distance 2 from each other, because the position between them would belong to an
interval of at least 8 positions that are not free. So A_yA_{y′} is in the class α, and the set
W′ = {B_p : p ∈ P} ∪ {A_y, A_{y′}} of at most 9 points meets α and (p) for every p ∈ P. By the induction hypothesis
(R_k) and (R_{k+3}) hold on S*_{W′}(π), and by Step 1 and (F1) so does (REC_k). Their combination (R_{k+4}) holds on
S*_{W′}(π), and by (F1) on every W as in the claim.

*Step 3: closing the cycle.* Let M be the matrix with rows c_1, c_2, c_3, c_4; then the matrix with rows
c_k, …, c_{k+3} is M^k, and the characteristic polynomial of M is z⁴ + 2z³ + 1. Take W = {B_0, B_1, B_2, B_3, A_y,
A_{y′}} with y, y′ as in Step 2. On S*_W(π) the relations (R_t), …, (R_{t+3}) say that (M^t − I)(y_0, y_1, y_2,
y_3)ᵀ = 0. By the step "Rigidity" of the proof of Theorem 4(a), no eigenvalue of M is a t-th root of unity, so
M^t − I is invertible and y_0 = … = y_3 = 0 on S*_W(π): the set W linearly forces (j) = α for j = 0, 1, 2, 3, and by
the rotation for every j.

*Step 4: the end.* After these merges, three-point sets force the remaining merges, one type of pair at a time, each
by a tight triple in which the two other pairs are already in the class α: A_jB_j from {A_i, A_j, B_j} with i far
from j (15 = 8 + 7); A_iB_{i+1} from {A_i, A_{i+1}, B_{i+1}} (16 = 9 + 7); B_iB_j, |i − j| ≥ 3, from
{B_i, A_i, B_j} (22 = 7 + 15); A_{i+2}B_i from {B_i, A_{i+2}, B_{i+3}} (22 = 13 + 9); B_iB_{i+2} from
{B_i, A_{i+2}, B_{i+2}} (20 = 13 + 7); A_{i+1}B_i from {B_i, A_{i+1}, B_{i+2}} (20 = 11 + 9); A_iB_{i+2} from
{A_i, A_{i+3}, B_{i+2}} (19 = 8 + 11); B_{i+1}B_{i+2} from {A_i, B_{i+1}, B_{i+2}} (19 = 9 + 10); A_iA_{i+2} from
{A_i, A_{i+2}, B_{i+2}} (19 = 12 + 7). These are all the types of pairs, so a single class remains. ∎

**Checks of the proof.** The scheme of the proof was also run as a program, with the sets I_a, the sets W′ of Step 2
and the sets on at most four points: a single class remains for t = 17, 19, 21, 23, 25, 27 (for t ≤ 15 some of the
sets W′ do not exist), and for t = 20, where C_t is not extreme, 130 classes remain (`linear_family.py`, scheme
`state`). Step 4 was checked by computing the two-term merges on all three-point sets for t = 19, 21, 31 (check U2).
The bound 10 comes from the sets I_a of Step 1; Steps 2 to 4 use at most 9 points. We did not try to lower it, and
the exact values in (a) suggest that L_lin(C_t) = 5 for every odd t ≥ 9; we have no proof of this.

The reason is the one that makes C_t hard for two-term deduction. Its tight system reduces to the recurrence (REC)
around the cycle. A two-term relation cannot carry the state of a recurrence of order 4 from one position to the
next, but a relation with a few more terms can: it expresses the values in the current window through those in the
starting window, and going once around the cycle closes the system.

**Proposition 10.** Extremality is definable in fixed-point logic with counting. Consequently there is an integer k
such that, for metrics d with positive distances on any number of points, whether d is extreme is determined by the
equivalence class of the structure (V, Tight_d) in the k-variable logic with counting quantifiers, where Tight_d is
the ternary relation of tight triples.

*Proof.* d is extreme iff the matrix of T(d) has rank C(n,2) − 1 over Q. Index its rows by the tight triples and its
columns by the ordered pairs of distinct points (each column of an unordered pair occurs twice, which does not
change the rank); its entries 0, ±1 are then defined by first-order formulas in Tight_d. The rank over Q of a matrix
defined in this way is definable in fixed-point logic with counting [DGHL09, Corollary VI.6], and so is the number
C(n,2) − 1. Every formula of this logic is equivalent, on finite structures, to a formula of the infinitary logic
with counting quantifiers and a bounded number of variables [O97]. ∎

**Remarks.** (1) Proposition 10 shows that the statement "no test of bounded scope characterises the extreme rays"
is false if bounded scope is understood as a bounded number of variables and the test may count and recurse. Such a
test is not a local deduction in any practical sense: it evaluates traces of powers of the matrix [DGHL09]. The
positive results of this kind hold over Q; the rank over a finite field is not definable in this logic [DGHL09],
and extremality is a property over Q. (2) So there are three levels. Two-term deduction on s points: unbounded
scope (Theorem 4). Linear deduction on s points: at most 5 on every ray of the lists that we tested, at most 10 on every C_t (Theorem 9) and exactly 5 on C_9, C_11 and C_13, by the
computations above; unknown in general.
Counting logic with k variables: bounded. (3) *Tests that add points.* A test that adds points to d and proves that
the larger metric is extreme proves nothing about d: by Avis's embedding theorem every rational metric with
positive distances, extreme or not, is a restriction of an extreme ray with L = 4 (Proposition 7 and Remark (6)
after Theorem 4). Adding points is sound when every solution of T(d) extends to a solution of the tight system of
the larger metric; the new distances are then auxiliary variables defined by linear equations, and eliminating them
gives relations with more than two terms among the old ones. So this is linear deduction in another form, and
belongs to the middle level.

**Question 2.** Is L_lin bounded on the extreme rays of the metric cones? On the lists it is at most 5, and no ray with L_lin ≥ 6 is known to us. A family that answers
this in the negative cannot be organised along a cycle as C_t is, since the state of a recurrence along a cycle passes through a bounded
window; one would look for tight systems with the structure of a grid or of an expander.

## 6. Computations: locality on the vertex lists and beyond

All computations use exact rational arithmetic unless marked *. Lists: the vertices of m_n for n ≤ 8 (complete:
[DFPS01, DFMV03]; completeness for n = 8 was re-proved independently in this project) and the list of [DI07] for
n = 9 as distributed by its authors. The distributed file has 1,056,367 orbits including the cut orbit; [DI07] and
the authors' web page state 1,056,368. The file has 1,056,369 lines of which two are header lines, so the published
number equals the number of lines minus one, which suggests a counting slip, but we cannot exclude that one orbit is
missing from the file. We verified that the 1,056,367 rows are vertices, pairwise inequivalent, and include the
1,221 orbits of [DI07] that are not adjacent to a cut. The m_9 list is not known to be complete, so Comp. 2, Comp. 3 and
Comp. 7–12 are statements about the list.

**Comp. 1 (all extreme rays of MET_k, k ≤ 8).** Every extreme ray of MET_k with positive distances is obtained from a
vertex of m_k by a switching (Lemma 1 and its converse). Running through all 2^(k−1) switchings of every orbit
representative gives 1, 3, 33, 3,751 rays up to permutation for k = 5, 6, 7, 8. As a check of completeness we
counted all extreme rays of MET_n from these lists (a ray on k points with automorphism group A gives
k!·S(n,k)/|A| rays on n points by merging points, [A80, Thm 4.2]; the cuts are the case k = 2): the totals 25, 296,
55,226, 119,269,588 for n = 5, 6, 7, 8 agree with the published values [DD-web], and the numbers of orbits under S_n
are 3, 8, 46, 3,918.

| k | rays | L = 4 | 5 | 6 | 7 | max L |
|---|---|---|---|---|---|---|
| 5 | 1 | 1 | | | | 4 |
| 6 | 3 | 3 | | | | 4 |
| 7 | 33 | 32 | 1 | | | 5 |
| 8 | 3,751 | 2,691 | 992 | 67 | 1 | 7 |

*Validation of the implementation.* On 14,646 weighted graphs with 5 to 11 nodes (957 rays, 13,689 non-rays by the
rank test) the closure at s = k ends with one class exactly for the rays, as Proposition 2(iii) requires.

**Comp. 2 (the m_9 list).** For each of the 1,055,145 cut-adjacent orbits, one switching to a ray (the one with the
smallest alphabet); 3,394 of these rays have fewer than 9 distinct points and are counted with their own k.

| k | rays | L = 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|
| 5–7 | 81 | 81 | | | | | |
| 8 | 3,313 | 2,411 | 870 | 27 | 5 | | |
| 9 | 1,051,751 | 315,636 | 515,637 | 201,727 | 18,323 | 426 | 2 |

For k = 9 the shares are 30.0%, 49.0%, 19.2%, 1.7%, 0.04% and two orbits with L = 9 (rows 1,048,423 and 1,048,435
of the list, both of denominator 27, weights 5 to 10, with 37 tight triples where 35 are needed). For these two the
closure stops changing at level 6 with 13 and 12 classes joined by 14 and 13 relations, one more than the number of
classes: the quotient system is a single circuit, and it has no two-term consequence on fewer than all 9 points.

**Comp. 3 (dependence on the switching).** L is an invariant of the ray, not of the orbit of m_n: different switchings
of a vertex give different rays. For n ≤ 8 all switchings are covered by Comp. 1. For 4,000 random orbits of the m_9 list
and all 256 switchings (27,826 rays, 27,737 of them on 9 distinct points) the distribution over the latter is
L = 4: 30.4%, 5: 48.4%, 6: 19.7%, 7: 1.5%, 8: 0.03%, close to the distribution of Comp. 2. Per orbit, the smallest L over
the switchings is 4 for 49% of the orbits, 5 for 42%, 6 for 9%, 7 for 0.2%; the largest is 4 for 5%, 5 for 43%,
6 for 46%, 7 for 7%, 8 for 0.2%; the two differ by at most 4. So 9% of the sampled orbits have no switching with
L ≤ 5.

**Reading of Comp. 1–3.** The largest locality is 4, 4, 5, 7, 9 for k = 5, ..., 9, and the share of rays with L = 4
decreases (97%, 72%, 30% for k = 7, 8, 9). Fixed-scope deduction characterises the extreme rays for k ≤ 6
(scope 4) and k ≤ 7 (scope 5) only, and at k = 9 there are rays whose extremality has no proof from any proper
subset of the points. Large locality is rare on the lists: two orbits in a million at k = 9.

**Comp. 4 (random and circulant graphs).** Random graphs G(n, 1/2), 300 samples for each n: see the remark after
Theorem 3. Every extreme ray found among the weighted circulant graphs on 7 to 13 nodes with weights at most 3 has
L = 4. High locality is not typical, and it is not a consequence of symmetry alone.

**Comp. 5 (searches for large locality beyond the lists).** Values marked * were computed with a symmetry-reduced
closure modulo 2^31 − 1 and not re-run in rational arithmetic.
(a) *Two-orbit metrics.* The metrics on points A_i, B_i (i ∈ Z_t) invariant under the rotation form a cone whose
extreme rays can be enumerated and tested. Cyclic symmetry: t = 5 (294 rays of MET_10), largest L = 8; t = 6 (3,019
rays of MET_12), largest L = 9; t = 5 with a fixed centre (1,332 rays of MET_11), largest L = 8. Dihedral symmetry:
t = 7 (3,497 rays of MET_14), largest L = 12; t = 7 with a fixed centre (n = 15), largest L = 13; t = 9 (55,300
rays of MET_18 tested, of 132,051 candidates), largest L = 17*; for the ray that attains it, L = 17 was
confirmed in rational arithmetic (`exact_check.py`), as were the values 12 and 13 above, so the star concerns only
the statement that no tested ray has a larger value.
(b) *Generic procedures do not find large locality.* Seven vertices of m_10 found by random walks on the skeleton
(49 rays over all switchings): L from 4 to 7. Adding a point to the rays of MET_8 with L ≥ 6 (beam search to 11
points, 6,794 rays): L never above 7. Random face descent in MET_n, n = 7, ..., 11 (54 extreme rays from 280
descents, the others ended with a zero distance): L ≤ 5. The graphs K_1 ∨ C_m² (a centre joined to the square of
the m-cycle) are graphic extreme rays with L = 7 for every m from 8 to 13.

**Comp. 6 (a symmetric family whose locality saturates).** The family K_t on A_i, B_i (i ∈ Z_t): d(A_i, A_{i±1}) = 10,
d(A_i, A_{i±2}) = 20, d(A_i, A_j) = 26 otherwise; d(B_i, B_{i±1}) = 24, d(B_i, B_j) = 12 otherwise; d(A_i, B_i) = 7,
d(A_i, B_{i±1}) = 17, d(A_i, B_{i±2}) = 13, d(A_i, B_j) = 19 otherwise. It is invariant under the dihedral group.
By computation K_t is an extreme ray for t = 7, 11, 13, 17, 19 and for no other t from 7 to 20, with L = 12 for
t = 7, L = 16* for t = 11 and 14 < L ≤ 16* for t = 13. After the 4-point merges the classes are one class K for
all pairs of B's and singletons, and eliminating all but s_i = [A_iB_i] leaves the recurrence
s_i + s_{i+1} + 2s_{i+2} + s_{i+3} + s_{i+4} = 6K for all i mod t. Its symbol (1 + ω²)(1 + ω + ω²) vanishes exactly
at the primitive 3rd and 4th roots of unity. So K_t cannot be an extreme ray when 3 or 4 divides t, and every
solution along an open stretch of the cycle has period 12, so 13 consecutive positions force s_j = s_{j+12}; this
caps the locality of the family. (The failure for t = 10, 14 is not explained by this recurrence alone.) Of 1,094
mirror-symmetric local-pattern families obtained by extending the dihedral rays of Comp. 5(a) for t = 7, every one has a
window of 14 positions that forces merges beyond the 4-point ones. This is what led to the chiral families of
Section 4.

**Largest locality known per n.** 4, 4, 5, 7 for n = 5, ..., 8 (complete lists); 9 for n = 9 (the m_9 list); at least
8, 8, 9, 12, 13 for n = 10, 11, 12, 14, 15 (Comp. 5); n for every n ≡ 2 (mod 4), n ≥ 18 (Theorem 4(c)).

**Fact (from Comp. 1, Comp. 2).** L(d) ≤ n − 1 for every extreme ray of MET_n, n ≤ 8, but max L = n for n = 9.

**Question 3.** Is max { L(d) : d extreme in MET_n } = n for every n ≥ 9? By Theorem 4(c) this holds for
n ≡ 2 (mod 4), n ≥ 18, and for n = 9 by Comp. 2 (the two rays exist whether or not the m_9 list is complete).

**Question 4.** Does the share of orbits of m_n with L = 4 tend to 0? By Theorem 3 and Proposition 5 at least
2^(n²/2 − O(n log n)) orbits have L = 4, so this is Question 1 in another form.

## 7. Other descriptions of the m_9 list

**Comp. 7 (primitive vertices; cut adjacency).** Call a vertex of m_n *primitive* if none of its restrictions to k nodes,
3 ≤ k < n, is a vertex of m_k. A rule that keeps its input as a restriction of its output cannot produce a
primitive vertex.

| n | orbits | primitive | share |
|---|---|---|---|
| 7 | 13 | 4 | 31% |
| 8 | 533 | 219 | 41% |
| 9 | 1,056,367 | 673,787 | 63.8% |

On the m_9 list 1,221 orbits are not adjacent to a cut, in agreement with [DI07].

**Comp. 8 (a normal form).** Say node v can be *peeled* from the node set S of a vertex x if x|S is a vertex of the fiber
of m_S over x|(S − v), i.e. the coordinates x_va are determined by the tight inequalities inside S that contain v.
Peel until no node can be peeled; the remaining set is a *seed*. On the m_9 list the seed has 3 nodes for 583,636
orbits, 4 nodes for 472,722 and 5 nodes for 8. A tight triangle through v gives an equation x_va ± x_vb = c; these
form a signed graph on S − v, and v can be peeled iff every component has an unbalanced cycle. Describing a step by
the lengths of the shortest unbalanced cycles of its components, the 1,056,366 non-cut orbits use six kinds of
steps: one 3-cycle (5,760,177 steps), two components with 3-cycles (88,230), one 5-cycle (11,967), one 2-cycle
(3,497), one 7-cycle (1,565), a 3-cycle and a 5-cycle (22).

**Comp. 9 (the normal form is not a construction).** The generator "start from all points of m_3 and m_4 with
denominator D, extend by all determined steps with denominator D, test for vertices" finds every orbit of m_8 with
D = 3, 4, 5, 6 (52, 12, 15, 95 orbits) and nothing else, from 2,958, 67,164, 757,052 and 5,215,846 candidates on 8
nodes, of which 43%, 0.28%, 0.04%, 0.07% are vertices. The partial points that lie on a path to a vertex number 39,
92, 200, 287 on 4 to 7 nodes for D = 6 (against 85, 311, 1,871, 22,788 generated). Six local features of an
extension were tested as filters that never discard a useful extension; the best keeps 86–100% of the extensions
where 17–56% are useful.

**Comp. 10 (graph-indexed families).** Alphabets and underlying graphs of the cut-adjacent orbits:

| n | orbits | alphabets | graphic | underlying graphs | most orbits on one graph |
|---|---|---|---|---|---|
| 7 | 12 | 2 | 92% | 11 | 1 |
| 8 | 532 | 9 | 20% | 256 | 12 |
| 9 | 1,055,145 | 1,273 | 0.52% | 31,061 | 2,177 |

A graph does not determine its weights, so "graph ↦ vertex" needs the weights as input.

**Comp. 11 (the simplest weighted family).** For rays with alphabet ⊆ {1, 2} (1, 3, 28, 925 for k = 5, ..., 8; 27,963
from the m_9 list) a deduction rule in the spirit of [A80, §2] (opposite sides of geodesic rectangles; odd closed
chains of exchanges; propagation through triples with one unknown) is sufficient for extremality and is necessary
for all 957 rays with k ≤ 8; it fails for 76 of the 27,963 rays on 9 nodes. The best necessary condition found
rejects 92% of 7,344 near-miss non-rays. This repeats, for weights {1, 2}, the experience of [A80, p. 132–133].

**Comp. 12 (elliptope).** For x in an orbit let λ(x) be the smallest eigenvalue of J − 2X, an orbit invariant. On m_7,
m_8 and 1,000 sampled orbits of m_9, λ does not separate the orbits reached by 8 restriction-keeping rules from the
others (probability that an unreached orbit has smaller λ than a reached one: 0.43, 0.47; 0.46 at equal
denominators).

## 8. Related work

Avis [A80] introduced graphic extreme rays, the isometric-cycle criterion, the density theorem used here and the
embedding theorem (every rational metric with positive distances is a restriction of an extreme ray, [A80, Thm 3.5]); the last explains why
"is a restriction of a graphic vertex" cannot characterise vertices. Laurent and Poljak [LP92] and Laurent [L96]
study graphic and one-third-integral vertices and the operations that preserve vertices. The lists are due to Deza,
Deza, Fukuda, Pasechnik, Sato, Mizutani, Vo and Indik [DDF96, DFPS01, DFMV03, DI07]. Cizma and Linial [CL25]
count path systems and faces of MET_n: they quote Avis's lower bound 2^(C(n,2)(1+o(1))) for the extreme rays, prove
the upper bound 2^(2.38n²(1+o(1))) for all faces, and show that metrizability of a path system is decided by a
linear program; as far as we could see they do not consider generators or bounded-scope criteria. Proposition 5 is
thus Avis's bound transferred to orbits of m_n, and Theorem 6 is an elementary consequence of it. What is new here,
to our knowledge, is the locality invariant with Theorems 3 and 4, the formulation of the counting bound as a limit
on generators, and the computations.

Bandelt and Dress [BD92] decompose a metric into split metrics and a split-prime residue; extreme rays other than
cuts are split-prime, but split-prime metrics need not be extreme, so this gives a necessary condition only.
Koolen, Moulton and Tönges [KMT00] and Sturmfels and Yu [SY04] classify the six-point metrics. Lavrov [La25]
generalises Avis's isometric-cycle criterion to metrics on simplicial posets and states that the classification of
extreme metrics for general n is open; he also considers a condition on the set of tight triangle inequalities that
involves only the triangles through one edge ("locally feasible markings") and notes that it is necessary but not
sufficient, already on five points. This is a consistency condition on one pattern of tight inequalities and is not
related to the closure of Section 3. Bodwin [Bo18] characterises the path systems that are unique shortest paths
of a weighted graph by forbidden subsystems coming from two-coloured polyhedra; his examples have 4 to 10 nodes and
the family is not bounded in size. That result concerns faces of the metric cone of a different kind (strict
metrizability), but it is the closest analogue we know of Theorem 4: obstructions that cannot be confined to a
bounded number of points. Melleray, Petrov and Vershik [MPV08] study extreme rays under the name of linearly rigid
metric spaces; they pose as an open question to describe the extremal metric spaces on n points and to estimate
their number. Casabella, Joswig and Kastner [CJK24] classify the metric spaces on seven points through subdivisions
of hypersimplices and give new infinite families of rays. Feldman and Kehoe [FK26] give further families of
extreme rays (bowtie metrics). Howe, Johnson and Lawrence [HJL86] study which graphs produce extreme rays of the
cone of distance matrices. Lomonosov and Sebő [LS93] ask which graphs are *primitive*, that is, have d_G extreme, and
more generally describe the minimal face of the metric cone that contains d_G. For bipartite G they give a complete
combinatorial answer: the extreme rays of that face are the characteristic vectors of the classes of an
"oppositeness" relation on the edges, and G is primitive iff there is one class. The relation is a condition on
four points, so in our terms their theorem says that bipartite graphic extreme rays have locality 4 (the corollary
after Theorem 3). For arbitrary graphs they state that this does not characterise primitivity [LS93, p. 229].
Theorem 4 shows that for weighted metrics no relation on a bounded number of points can play this role. In none of these
did we find the locality invariant, a bound on generators, or a
statement that extreme rays cannot be recognised by local deduction on a bounded number of points.

*Forward citations.* We went through the works citing [A80] (68), [L96] (26) and [DI07] (6) in the OpenAlex index,
and those citing [A80] (33), [L96] (14), [DI07] (2), [LP92] (4) and Grishukhin's enumeration for seven points (16)
in zbMATH Open (both in November 2026), together with keyword searches in zbMATH Open for extreme rays of the
metric cone and vertices of the metric polytope. We read those whose titles or reviews concern extreme rays,
vertices of the metric polytope or criteria for extremality; none contains a result of the kind of Theorems 4 or 6.

## 9. Reproduction

All scripts and their outputs are in the repository https://github.com/adrian-burlacu-software/metric-polytope (scripts in `scripts/phase9/`,
outputs in `results/phase9/`; the Python packages needed are listed in `requirements.txt`). The vertex lists of m_n
for n ≤ 8 are included in `data/deza/raw/`. The m_9 list is not included: it has to be downloaded from its authors'
page [DD-web], and the checksums of the file we used are in `data/deza/orbits9/SHA256SUMS.txt`. Permanent copies of the
repository are archived at Zenodo, one for each release, under the DOI 10.5281/zenodo.24564343, which resolves to the latest archived
version and lists the earlier ones.

| item | script | output |
|---|---|---|
| Theorem 4 (a), (b): checks V1–V3; remark 4 | `family_C_proof.py`, `family_C_structure.py`, `pattern_hunt.py`, `cand_pattern.py` | `family_C_proof.json`, `pattern_hunt.json`, `cand_pattern.json` |
| Theorem 4 (c): t ≤ 21; checks W1–W3 for t ≥ 23 | `family_C.py`; `family_C_top.py` | `family_C.json`; `family_C_top.json` |
| Theorem 4 (c): second implementation of W1–W3 | `family_C_top_check.py` | `family_C_top_check.json` |
| Corollary on bipartite graphs | `bipartite_check.py` | `bipartite_check.json` |
| Linear locality on the lists (Section 5c) | `linear_locality.py` (`--m9hard` for the nine-point rays) | `linear_locality.json`, `linear_locality_m9hard.json` |
| Linear locality of C_t (Section 5c) | `linear_uniform.py` (checks U1, U2 of Theorem 9), `linear_full.py` (exact values; `--check`), `linear_family.py` (`--scheme bblocks --par 5 --local 5`; `--scheme state --local 5`), `linear_width.py` (`--exact` for rational arithmetic) | `linear_uniform.json`, `linear_full.json`, `linear_family.json`, `linear_width.json`, `linear_width_exact.json`, `linear_width_even.json` |
| Comp. 1, validation | `locality_checks.py`, `ray_count_check.py` | `locality_checks.json`, `ray_count_check.json` |
| Comp. 2 | `locality.py --all9` | `locality_m9all.json` |
| Comp. 3 | `locality_switch9.py` | `locality_switch9.json` |
| Comp. 4 | `random_graph_locality.py`, `locality_checks.py` | `random_graph_locality.json`, `locality_checks.json` |
| Comp. 5 | `sym_search.py` (`--mirror 0 1 --fast` for the dihedral runs), `locality_checks.py`, `locality_climb.py`, `random_ray_locality.py` | `sym_search.json`, `locality_checks.json`, `locality_climb.json`, `random_ray_locality.json` |
| Comp. 6 | `famK.py`, `famK_level.py`, `family_scan.py`, `window_test.py`, `exact_check.py` | `family_scan.json`, `window_test.json`, `exact_check.json` |
| Comp. 7, Comp. 8 | `vertex_structure.py`, `step_types.py` | `vertex_structure_deza9all.json`, `step_types_m9all.json` |
| Comp. 9 | `fiber_generator.py`, `useful_share.py`, `choice_features.py` | `fiber_generator_n8.json`, `useful_share_n8.json`, `choice_features_n8.json` |
| Comp. 10 | `graph_families.py --all9` | `graph_families_m9all.json` |
| Comp. 11 | `family12.py`, `judge_family.py` | `round_18_family.json` |
| Comp. 12 | `elliptope.py` | `elliptope.json` |

Ranks are computed modulo 2^31 − 1 with an exact fallback whenever the modular rank is deficient, so every "is a
vertex" and "is a ray" verdict is exact; the locality closure uses rational arithmetic throughout, except for the
values marked * in Comp. 5 and Comp. 6 and the parenthesis of Theorem 4(c).

## Acknowledgements and use of AI tools

This work was carried out with an AI assistant, Claude (Anthropic; models Claude Opus 5.5 and Claude Fable 5.2, used
through the tool Claude Code). Under the direction of the author, the assistant wrote the scripts, ran the
computations and the searches that led to the family C_t, searched the literature, and drafted the proofs and the
text of this paper. The author set the questions, decided what was pursued and what was claimed, and is responsible
for the content. The computer-assisted part of Theorem 4(c) exists in two implementations, both written with the
assistant; neither they nor the proofs have yet been checked by a second person.

## 10. Before submission (not part of the paper)

1. **Second reader.** The proofs of Theorem 4 and Theorem 3(b) have been checked only by their author and, for the
   finite checks V1–V3 and W1–W3, by `family_C_proof.py` and `family_C_top.py`. Both should be read by a second
   person. The search of Theorem 4(c) now exists in two implementations that agree (`family_C_top.py`,
   `family_C_top_check.py`, 2026-11-26), but both were written by the same author and both rest on Lemma P and on
   Steps 1–2 as stated; the real-cycle checks cover these only for the values of t that were run (19 to 45).
2. **Theorem 4(c) for 9 ≤ t ≤ 21** rests on the closure computation, not on the proof; the construction of the
   proof also passes its guard for t = 19, 21, so the two methods agree where both were run.
3. **Citations.** Forward citations of [A80], [L96], [DI07] were checked in OpenAlex and, through its public API,
   in zbMATH Open (2026-11-26; also [LP92], Grishukhin 1992 and seven keyword searches). The zbMATH search found
   two works not cited before, [HJL86] and [LS93], now in Section 8. [LS93] was then read in full (scan supplied by the author, 2026-11-26): it is the closest
   prior work, gives the bipartite case completely, and led to the corollary after Theorem 3 and to Remark (6)
   after Theorem 4; it does not anticipate Theorem 4. The corollary's proof and Remark (6) are new and unread by
   anyone else. One zbMATH record citing [A80] and [DI07] (Zbl 1578.52017, 2025) is
   hidden for licence reasons and could not be identified. MathSciNet was not consulted. Citing relations and titles were taken from the index, partly through machine summaries. Not read in
   full text: Karzanov, *Metrics with finite sets of primitive extensions* (Ann. Comb. 2, 1998); Grishukhin,
   *Computing extreme rays of the metric cone for seven points* (European J. Combin. 13, 1992); Avis, *Extremal
   metrics induced by graphs* (Ann. Discrete Math. 8, 1980); the thesis on the "metric body" behind [FK26]; [FK26]
   itself (record description only); the second half of [CJK24]. [CL25] §7, [La25] §4.2 onwards and [Bo18] §2.2
   onwards were read in summary only. The page numbers of [KMT00] and [SY04] are from memory; the bibliographic
   data of [MPV08], [CJK24], [FK26] come from index records and should be checked against the papers.
4. **The m_9 count.** The file has one orbit fewer than published (Section 6); the authors of the list could
   confirm which number is right.
5. **Values marked *** (Comp. 5, Comp. 6). The record values 12, 13, 17 of Comp. 5(a) are exact
   (`exact_check.json`; the 18-point run took 51 minutes). Still modular: the statement that no other tested
   18-point ray exceeds 17, and L = 16 (t = 11, 22 points) and 14 < L ≤ 16 (t = 13, 26 points) for the family K_t
   of Comp. 6. An exact run on 22 points is estimated at several days (extrapolating 45 s, 140 s, 3,072 s for 14,
   15, 18 points) and was not started; either keep the stars or drop the two K_t values.
8. **Bibliography check (2026-11-26).** All entries were compared with Crossref, arXiv and Zenodo records: volume,
   year and pages agree for [A80], [BD92], [DDF96], [DFMV03], [DFPS01], [DI07], [KMT00], [L96], [LP92], [MPV08],
   [SY04]; [Bo18] and [CJK24] were updated to the published versions; the DOI of [FK26] is the all-versions DOI of
   the record. The year of volume 34 of Exp. Math. (2025) is inferred, not read from the journal page.
9. **Sources re-read (2026-11-26), by keyword search and reading of the passages found, not cover to cover.**
   [Bo18] whole text, [CL25] §7, [La25] §3, [FK26] abstract, section list and keyword hits: no statement about
   bounded-scope tests for extreme rays, locality, or generators. [La25] §3 has "locally feasible markings" (now
   mentioned in Section 8). [FK26]'s "metric body" is the set of pseudometrics with values at most 1, not m_n.
   Still not obtained: Karzanov 1998, Grishukhin 1992 (publisher refused automated download), Avis, *Extremal
   metrics induced by graphs* (Ann. Discrete Math. 8 (1980) 217–220); second half of [CJK24] only searched.
7. **Permanent archive.** The repository is public on GitHub since 2026-11-26, with licences (MIT for the code,
   CC BY 4.0 for `docs/`); the third-party data in `data/deza/raw/` and `data/smapo/raw/` are kept (author's
   decision; their terms of redistribution were not checked). Release `v0.1-draft` is archived at Zenodo
   (doi:10.5281/zenodo.24564344; all versions: doi:10.5281/zenodo.24564343), 2026-11-26. Before submission: make a new release from the submitted
   version and update the version DOI in Section 9.
10. **Section 5c (added 2026-11-27).** Proposition 8 and its proof, the computations of L_lin(C_t) (exact value 5 for t = 9, 11, 13), Theorem 9 (L_lin(C_t) ≤ 10 for all odd t ≥ 9; proof new, needs a reader, especially facts (F1), (F2) and Step 2) and Proposition 10
   are new and unread by anyone else. [DGHL09] was read (Section VI, Corollary VI.6). [O97] is cited from memory for
   the standard fact that fixed-point logic with counting embeds in bounded-variable infinitary counting logic; the
   reference and the statement should be checked. The computation is exact for the listed t only; a proof uniform
   in t (transfer matrices of (REC)) is not written. Question 2 is open and is the natural next project: an
   extreme ray with unbounded linear locality would need a two-dimensional structure.
6. **Earlier numbering.** In the project notes (`docs/phase9_status.md`) Theorem 6 is "Theorem 1", Proposition 5 is
   "Corollary 1", and Comp. 3–12 appear as Comp. 2′, Comp. 3–3⁗, Comp. 4–9.

## References

- [A80] D. Avis, On the extreme rays of the metric cone, Canad. J. Math. 32 (1980) 126–144.
- [BD92] H.-J. Bandelt, A. W. M. Dress, A canonical decomposition theory for metrics on a finite set, Adv. Math. 92
  (1992) 47–105.
- [Bo18] G. Bodwin, On the structure of unique shortest paths in graphs, in Proc. 30th ACM-SIAM Symposium on
  Discrete Algorithms (SODA 2019), 2071–2089; arXiv:1804.09745v3 (2026).
- [CJK24] L. Casabella, M. Joswig, L. Kastner, Subdivisions of hypersimplices: with a view toward finite metric
  spaces, Exp. Math. 34 (2025) 808–823 (online 2024), arXiv:2402.17665.
- [CL25] D. Cizma, N. Linial, On the number of path systems, arXiv:2508.21379v3 (2025).
- [FK26] D. V. Feldman, E. R. Kehoe, Extreme rays of the metric cone and the metric body: bowtie metrics and
  half-one extremality, preprint, Zenodo, doi:10.5281/zenodo.21898516 (2026).
- [LS93] M. Lomonosov, A. Sebő, On the geodesic-structure of graphs: a polyhedral approach to metric decomposition,
  in Third IPCO Conference (Erice, 1993), G. Rinaldi and L. Wolsey (eds.), CORE, Louvain-la-Neuve, 1993, 221–234.
- [MPV08] J. Melleray, F. V. Petrov, A. M. Vershik, Linearly rigid metric spaces and the embedding problem, Fund.
  Math. 199 (2008) 177–194, arXiv:math/0611049.
- [DD-web] A. Deza, metric polytope data page, www.cas.mcmaster.ca/~deza/metric.html.
- [DDF96] A. Deza, M. Deza, K. Fukuda, On skeletons, diameters and volumes of metric polyhedra, LNCS 1120 (1996)
  112–128.
- [DFPS01] A. Deza, K. Fukuda, D. Pasechnik, M. Sato, On the skeleton of the metric polytope, LNCS 2098 (2001)
  125–136.
- [DFMV03] A. Deza, K. Fukuda, T. Mizutani, C. Vo, On the face lattice of the metric polytope, LNCS 2866 (2003)
  118–128.
- [DGHL09] A. Dawar, M. Grohe, B. Holm, B. Laubner, Logics with rank operators, in Proc. 24th IEEE Symposium on
  Logic in Computer Science (LICS 2009), 113–122.
- [DI07] A. Deza, G. Indik, A counterexample to the dominating set conjecture, Optim. Lett. 1 (2007) 163–169.
- [DL97] M. Deza, M. Laurent, Geometry of Cuts and Metrics, Springer, 1997.
- [HJL86] E. Howe, C. R. Johnson, J. Lawrence, The structure of distances in networks, Networks 16 (1986) 87–106.
- [KMT00] J. Koolen, V. Moulton, U. Tönges, A classification of the six-point prime metrics, European J. Combin. 21
  (2000) 815–829.
- [La25] A. Lavrov, Ternary relations and their polytopes, arXiv:2509.06811 (2025).
- [L96] M. Laurent, Graphic vertices of the metric polytope, Discrete Math. 151 (1996) 131–153.
- [LP92] M. Laurent, S. Poljak, One-third-integrality in the max-cut problem, Math. Programming 71 (1995) 29–50
  (CWI Report BS-R9209, 1992).
- [O97] M. Otto, Bounded Variable Logics and Counting, Lecture Notes in Logic 9, Springer, 1997.
- [SY04] B. Sturmfels, J. Yu, Classification of six-point metrics, Electron. J. Combin. 11 (2004) R44.
