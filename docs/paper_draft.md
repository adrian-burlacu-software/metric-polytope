# No bounded-scope characterisation of the extreme rays of the metric cone

*Draft of 2026-11-26. Every statement is marked **Theorem** / **Proposition** / **Lemma** (proved here),
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
arithmetic). Hence no criterion of bounded scope characterises the extreme rays of the metric cone,
or the vertices of the metric polytope m_n adjacent to a cut. We compute L exactly for all extreme rays of MET_n,
n ≤ 8, and for the 1,055,145 cut-adjacent orbits of the known vertex list of m_9: the largest values are 4, 4, 5, 7
for n = 5, ..., 8 and 9 on the m_9 list, and the share of rays with L = 4 falls from 97% (n = 7) to 30% (n = 9).
We also show, by a counting argument resting on a theorem of Avis, that a generator of vertices of m_n which makes
fewer than (1 − δ)n bits of choice when it adds the n-th node produces a vanishing share of the orbits, so that no
finite set of such rules with a finite list of exceptions describes the vertices.

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
a large class of graphs. We measure the scope a test needs by the locality L (Section 3).

*Small-choice rules.* A rule receives an object on n − 1 nodes and a bounded or slowly growing amount of choice and
returns an object on n nodes. All classical constructions are of this kind.

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
   density theorem), and a generator with at most (1 − δ)n bits of choice per node produces a vanishing share of
   them (Theorem 6).
4. *Exact computations.* L for all extreme rays of MET_n, n ≤ 8, and for the m_9 list (C1–C3); searches for large
   locality beyond the lists (C4–C6); and negative results for four other candidate descriptions of the m_9 list
   (C7–C12).

Together, 1 and 2 say that the scope of the rank condition is the smallest possible for a typical graph and
unbounded in the worst case; the computations show that on the actual vertex lists the typical case is already
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
[DI07] (re-derived in C7 below).

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
subset to another is not covered and would need a wider definition.

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

Part (b) is the case p = 1/2 of Avis's density theorem [A80, Thm 3.3], with the stronger conclusion L = 4; the
argument follows Avis's and treats explicitly the pairs of edges with a common endpoint.

**Remark (finite n).** The union bound in (b) is effective only for n in the thousands, but the conclusion sets in
much earlier (C4 below): of 300 samples of G(n, 1/2) each, the shares with d_G extreme are 0.7%, 6%, 23%, 61%,
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
the versions with A and B exchanged. (5) Chirality matters: the mirror-symmetric family K_t of C6 reduces in the
same way to a recurrence, but all its characteristic roots are roots of unity, every solution on an open stretch is
periodic, and its locality stays bounded.

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

**Definition (generator).** A *generator* consists of sets O_n of *objects on n nodes* (n ≥ n_0), a finite set E of
exceptional objects, and r *rules*. Each rule maps a pair (object on n − 1 nodes, choice c ∈ {1, ..., C(n)}) to an
object on n nodes or to nothing. The generated objects are the exceptional ones and the outputs of rules applied to
generated objects. A map from generated objects on n nodes to orbits of m_n (possibly partial) says which orbit, if
any, an object *produces*. The *choice* of the generator is b(n) = log₂ C(n) bits.

Nothing is assumed about the objects: they may be vertices, points of m_n that are not vertices, graphs, or partial
structures. Restriction-keeping moves, families with boundedly many integer parameters of size polynomial in n, and
the generator of C9 for a fixed denominator are generators with b(n) = O(log n).

**Theorem 6.** Let a generator have b(n) ≤ (1 − δ)n for some δ > 0 and all large n. Then it produces at most
2^((1−δ)n²/2 + O(n)) orbits of m_n, and the share of the orbits of m_n it produces tends to 0. In particular the
number of orbits it misses is unbounded, so no finite list of exceptions completes it.

*Proof.* Let N(n) be the number of generated objects on n nodes. A generated object on n nodes is exceptional or
the output of one of r rules on one of N(n − 1) objects with one of 2^b(n) choices, so
N(n) ≤ r·2^b(n)·N(n − 1) + |E|, and by induction N(n) ≤ (|E| + 1)·∏_{k ≤ n} (r·2^b(k) + 1) = 2^(Σ_{k≤n} b(k) + O(n)).
Since b(k) ≤ (1 − δ)k for all large k, Σ_{k≤n} b(k) ≤ (1 − δ)n²/2 + O(n). The number of orbits produced is at most
N(n). By Proposition 5, v(n) ≥ 2^(n²/2 − O(n log n)), so N(n)/v(n) ≤ 2^(−δn²/2 + O(n log n)) → 0 and
v(n) − N(n) → ∞. The exceptions are included in N(n). ∎

**Remarks.** (a) The bound is sharp in the choice up to a constant factor: with b(n) = n − 1 a rule can choose the
neighbourhood of the new node, hence an arbitrary graph, and then the single rule G ↦ x_G produces
2^(n²/2 − O(n log n)) orbits; and by [CL25] a choice of 4.76·n bits per node is enough to index all cut-adjacent
orbits. (b) The theorem does not need the m_9 list or any computation. (c) It is a statement about growth, and the
lists show the growth has begun: v(7), v(8), v(9) = 13, 533, ≥ 1,056,367, successive factors 41 and 1,982.

**Question 1.** Let r(n) be the number of extreme rays of MET_n. Is log₂ r(n) ~ n²/2, i.e. are almost all extreme
rays graphic on the logarithmic scale, or is lim log₂ r(n)/n² > 1/2? By [CL25] the limit, if it exists, is at most
2.38. On the lists the graphic share of the cut-adjacent orbits is 92%, 20%, 0.52% for n = 7, 8, 9 (C10), which
suggests that non-graphic rays dominate at least in number. (For vertices of m_n not adjacent to a cut we know only
the trivial bound 2^O(n² log n).)

## 6. Computations: locality on the vertex lists and beyond

All computations use exact rational arithmetic unless marked *. Lists: the vertices of m_n for n ≤ 8 (complete:
[DFPS01, DFMV03]; completeness for n = 8 was re-proved independently in this project) and the list of [DI07] for
n = 9 as distributed by its authors. The distributed file has 1,056,367 orbits including the cut orbit; [DI07] and
the authors' web page state 1,056,368. The file has 1,056,369 lines of which two are header lines, so the published
number equals the number of lines minus one, which suggests a counting slip, but we cannot exclude that one orbit is
missing from the file. We verified that the 1,056,367 rows are vertices, pairwise inequivalent, and include the
1,221 orbits of [DI07] that are not adjacent to a cut. The m_9 list is not known to be complete, so C2, C3 and
C7–C12 are statements about the list.

**C1 (all extreme rays of MET_k, k ≤ 8).** Every extreme ray of MET_k with positive distances is obtained from a
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

**C2 (the m_9 list).** For each of the 1,055,145 cut-adjacent orbits, one switching to a ray (the one with the
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

**C3 (dependence on the switching).** L is an invariant of the ray, not of the orbit of m_n: different switchings
of a vertex give different rays. For n ≤ 8 all switchings are covered by C1. For 4,000 random orbits of the m_9 list
and all 256 switchings (27,826 rays, 27,737 of them on 9 distinct points) the distribution over the latter is
L = 4: 30.4%, 5: 48.4%, 6: 19.7%, 7: 1.5%, 8: 0.03%, close to the distribution of C2. Per orbit, the smallest L over
the switchings is 4 for 49% of the orbits, 5 for 42%, 6 for 9%, 7 for 0.2%; the largest is 4 for 5%, 5 for 43%,
6 for 46%, 7 for 7%, 8 for 0.2%; the two differ by at most 4. So 9% of the sampled orbits have no switching with
L ≤ 5.

**Reading of C1–C3.** The largest locality is 4, 4, 5, 7, 9 for k = 5, ..., 9, and the share of rays with L = 4
decreases (97%, 72%, 30% for k = 7, 8, 9). Fixed-scope deduction characterises the extreme rays for k ≤ 6
(scope 4) and k ≤ 7 (scope 5) only, and at k = 9 there are rays whose extremality has no proof from any proper
subset of the points. Large locality is rare on the lists: two orbits in a million at k = 9.

**C4 (random and circulant graphs).** Random graphs G(n, 1/2), 300 samples for each n: see the remark after
Theorem 3. Every extreme ray found among the weighted circulant graphs on 7 to 13 nodes with weights at most 3 has
L = 4. High locality is not typical, and it is not a consequence of symmetry alone.

**C5 (searches for large locality beyond the lists).** Values marked * were computed with a symmetry-reduced
closure modulo 2^31 − 1 and not re-run in rational arithmetic.
(a) *Two-orbit metrics.* The metrics on points A_i, B_i (i ∈ Z_t) invariant under the rotation form a cone whose
extreme rays can be enumerated and tested. Cyclic symmetry: t = 5 (294 rays of MET_10), largest L = 8; t = 6 (3,019
rays of MET_12), largest L = 9; t = 5 with a fixed centre (1,332 rays of MET_11), largest L = 8. Dihedral symmetry:
t = 7 (3,497 rays of MET_14), largest L = 12; t = 7 with a fixed centre (n = 15), largest L = 13; t = 9 (55,300
rays of MET_18 tested, of 132,051 candidates), largest L = 17*.
(b) *Generic procedures do not find large locality.* Seven vertices of m_10 found by random walks on the skeleton
(49 rays over all switchings): L from 4 to 7. Adding a point to the rays of MET_8 with L ≥ 6 (beam search to 11
points, 6,794 rays): L never above 7. Random face descent in MET_n, n = 7, ..., 11 (54 extreme rays from 280
descents, the others ended with a zero distance): L ≤ 5. The graphs K_1 ∨ C_m² (a centre joined to the square of
the m-cycle) are graphic extreme rays with L = 7 for every m from 8 to 13.

**C6 (a symmetric family whose locality saturates).** The family K_t on A_i, B_i (i ∈ Z_t): d(A_i, A_{i±1}) = 10,
d(A_i, A_{i±2}) = 20, d(A_i, A_j) = 26 otherwise; d(B_i, B_{i±1}) = 24, d(B_i, B_j) = 12 otherwise; d(A_i, B_i) = 7,
d(A_i, B_{i±1}) = 17, d(A_i, B_{i±2}) = 13, d(A_i, B_j) = 19 otherwise. It is invariant under the dihedral group.
By computation K_t is an extreme ray for t = 7, 11, 13, 17, 19 and for no other t from 7 to 20, with L = 12 for
t = 7, L = 16* for t = 11 and 14 < L ≤ 16* for t = 13. After the 4-point merges the classes are one class K for
all pairs of B's and singletons, and eliminating all but s_i = [A_iB_i] leaves the recurrence
s_i + s_{i+1} + 2s_{i+2} + s_{i+3} + s_{i+4} = 6K for all i mod t. Its symbol (1 + ω²)(1 + ω + ω²) vanishes exactly
at the primitive 3rd and 4th roots of unity. So K_t cannot be an extreme ray when 3 or 4 divides t, and every
solution along an open stretch of the cycle has period 12, so 13 consecutive positions force s_j = s_{j+12}; this
caps the locality of the family. (The failure for t = 10, 14 is not explained by this recurrence alone.) Of 1,094
mirror-symmetric local-pattern families obtained by extending the dihedral rays of C5(a) for t = 7, every one has a
window of 14 positions that forces merges beyond the 4-point ones. This is what led to the chiral families of
Section 4.

**Largest locality known per n.** 4, 4, 5, 7 for n = 5, ..., 8 (complete lists); 9 for n = 9 (the m_9 list); at least
8, 8, 9, 12, 13 for n = 10, 11, 12, 14, 15 (C5); n for every n ≡ 2 (mod 4), n ≥ 18 (Theorem 4(c)).

**Fact (from C1, C2).** L(d) ≤ n − 1 for every extreme ray of MET_n, n ≤ 8, but max L = n for n = 9.

**Question 2.** Is max { L(d) : d extreme in MET_n } = n for every n ≥ 9? By Theorem 4(c) this holds for
n ≡ 2 (mod 4), n ≥ 18, and for n = 9 by C2 (the two rays exist whether or not the m_9 list is complete).

**Question 3.** Does the share of orbits of m_n with L = 4 tend to 0? By Theorem 3 and Proposition 5 at least
2^(n²/2 − O(n log n)) orbits have L = 4, so this is Question 1 in another form.

## 7. Other descriptions of the m_9 list

**C7 (primitive vertices; cut adjacency).** Call a vertex of m_n *primitive* if none of its restrictions to k nodes,
3 ≤ k < n, is a vertex of m_k. A rule that keeps its input as a restriction of its output cannot produce a
primitive vertex.

| n | orbits | primitive | share |
|---|---|---|---|
| 7 | 13 | 4 | 31% |
| 8 | 533 | 219 | 41% |
| 9 | 1,056,367 | 673,787 | 63.8% |

On the m_9 list 1,221 orbits are not adjacent to a cut, in agreement with [DI07].

**C8 (a normal form).** Say node v can be *peeled* from the node set S of a vertex x if x|S is a vertex of the fiber
of m_S over x|(S − v), i.e. the coordinates x_va are determined by the tight inequalities inside S that contain v.
Peel until no node can be peeled; the remaining set is a *seed*. On the m_9 list the seed has 3 nodes for 583,636
orbits, 4 nodes for 472,722 and 5 nodes for 8. A tight triangle through v gives an equation x_va ± x_vb = c; these
form a signed graph on S − v, and v can be peeled iff every component has an unbalanced cycle. Describing a step by
the lengths of the shortest unbalanced cycles of its components, the 1,056,366 non-cut orbits use six kinds of
steps: one 3-cycle (5,760,177 steps), two components with 3-cycles (88,230), one 5-cycle (11,967), one 2-cycle
(3,497), one 7-cycle (1,565), a 3-cycle and a 5-cycle (22).

**C9 (the normal form is not a construction).** The generator "start from all points of m_3 and m_4 with
denominator D, extend by all determined steps with denominator D, test for vertices" finds every orbit of m_8 with
D = 3, 4, 5, 6 (52, 12, 15, 95 orbits) and nothing else, from 2,958, 67,164, 757,052 and 5,215,846 candidates on 8
nodes, of which 43%, 0.28%, 0.04%, 0.07% are vertices. The partial points that lie on a path to a vertex number 39,
92, 200, 287 on 4 to 7 nodes for D = 6 (against 85, 311, 1,871, 22,788 generated). Six local features of an
extension were tested as filters that never discard a useful extension; the best keeps 86–100% of the extensions
where 17–56% are useful.

**C10 (graph-indexed families).** Alphabets and underlying graphs of the cut-adjacent orbits:

| n | orbits | alphabets | graphic | underlying graphs | most orbits on one graph |
|---|---|---|---|---|---|
| 7 | 12 | 2 | 92% | 11 | 1 |
| 8 | 532 | 9 | 20% | 256 | 12 |
| 9 | 1,055,145 | 1,273 | 0.52% | 31,061 | 2,177 |

A graph does not determine its weights, so "graph ↦ vertex" needs the weights as input.

**C11 (the simplest weighted family).** For rays with alphabet ⊆ {1, 2} (1, 3, 28, 925 for k = 5, ..., 8; 27,963
from the m_9 list) a deduction rule in the spirit of [A80, §2] (opposite sides of geodesic rectangles; odd closed
chains of exchanges; propagation through triples with one unknown) is sufficient for extremality and is necessary
for all 957 rays with k ≤ 8; it fails for 76 of the 27,963 rays on 9 nodes. The best necessary condition found
rejects 92% of 7,344 near-miss non-rays. This repeats, for weights {1, 2}, the experience of [A80, p. 132–133].

**C12 (elliptope).** For x in an orbit let λ(x) be the smallest eigenvalue of J − 2X, an orbit invariant. On m_7,
m_8 and 1,000 sampled orbits of m_9, λ does not separate the orbits reached by 8 restriction-keeping rules from the
others (probability that an unreached orbit has smaller λ than a reached one: 0.43, 0.47; 0.46 at equal
denominators).

## 8. Related work

Avis [A80] introduced graphic extreme rays, the isometric-cycle criterion, the density theorem used here and the
embedding theorem (every rational metric is a restriction of an extreme ray, [A80, Thm 3.5]); the last explains why
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
extreme metrics for general n is open. Bodwin [Bo18] characterises the path systems that are unique shortest paths
of a weighted graph by forbidden subsystems coming from two-coloured polyhedra; his examples have 4 to 10 nodes and
the family is not bounded in size. That result concerns faces of the metric cone of a different kind (strict
metrizability), but it is the closest analogue we know of Theorem 4: obstructions that cannot be confined to a
bounded number of points. Melleray, Petrov and Vershik [MPV08] study extreme rays under the name of linearly rigid
metric spaces; they pose as an open question to describe the extremal metric spaces on n points and to estimate
their number. Casabella, Joswig and Kastner [CJK24] classify the metric spaces on seven points through subdivisions
of hypersimplices and give new infinite families of rays. Feldman and Kehoe [FK26] give further families of
extreme rays (bowtie metrics). In none of these did we find the locality invariant, a bound on generators, or a
statement that extreme rays admit no bounded-scope characterisation.

*Forward citations.* We went through the works citing [A80] (68), [L96] (26) and [DI07] (6) in the OpenAlex index
(November 2026) and read those whose titles concern extreme rays, vertices of the metric polytope or criteria for
extremality; none contains a result of the kind of Theorems 4 or 6.

## 9. Reproduction

Scripts in `scripts/phase9/`, outputs in `results/phase9/`.

| item | script | output |
|---|---|---|
| Theorem 4 (a), (b): checks V1–V3; remark 4 | `family_C_proof.py`, `family_C_structure.py`, `pattern_hunt.py`, `cand_pattern.py` | `family_C_proof.json`, `pattern_hunt.json`, `cand_pattern.json` |
| Theorem 4 (c): t ≤ 21; checks W1–W3 for t ≥ 23 | `family_C.py`; `family_C_top.py` | `family_C.json`; `family_C_top.json` |
| Theorem 4 (c): second implementation of W1–W3 | `family_C_top_check.py` | `family_C_top_check.json` |
| C1, validation | `locality_checks.py`, `ray_count_check.py` | `locality_checks.json`, `ray_count_check.json` |
| C2 | `locality.py --all9` | `locality_m9all.json` |
| C3 | `locality_switch9.py` | `locality_switch9.json` |
| C4 | `random_graph_locality.py`, `locality_checks.py` | `random_graph_locality.json`, `locality_checks.json` |
| C5 | `sym_search.py` (`--mirror 0 1 --fast` for the dihedral runs), `locality_checks.py`, `locality_climb.py`, `random_ray_locality.py` | `sym_search.json`, `locality_checks.json`, `locality_climb.json`, `random_ray_locality.json` |
| C6 | `famK.py`, `famK_level.py`, `family_scan.py`, `window_test.py`, `exact_check.py` | `family_scan.json`, `window_test.json`, `exact_check.json` |
| C7, C8 | `vertex_structure.py`, `step_types.py` | `vertex_structure_deza9all.json`, `step_types_m9all.json` |
| C9 | `fiber_generator.py`, `useful_share.py`, `choice_features.py` | `fiber_generator_n8.json`, `useful_share_n8.json`, `choice_features_n8.json` |
| C10 | `graph_families.py --all9` | `graph_families_m9all.json` |
| C11 | `family12.py`, `judge_family.py` | `round_18_family.json` |
| C12 | `elliptope.py` | `elliptope.json` |

Ranks are computed modulo 2^31 − 1 with an exact fallback whenever the modular rank is deficient, so every "is a
vertex" and "is a ray" verdict is exact; the locality closure uses rational arithmetic throughout, except for the
values marked * in C5 and C6 and the parenthesis of Theorem 4(c).

## 10. Before submission (not part of the paper)

1. **Second reader.** The proofs of Theorem 4 and Theorem 3(b) have been checked only by their author and, for the
   finite checks V1–V3 and W1–W3, by `family_C_proof.py` and `family_C_top.py`. Both should be read by a second
   person. The search of Theorem 4(c) now exists in two implementations that agree (`family_C_top.py`,
   `family_C_top_check.py`, 2026-11-26), but both were written by the same author and both rest on Lemma P and on
   Steps 1–2 as stated; the real-cycle checks cover these only for the values of t that were run (19 to 45).
2. **Theorem 4(c) for 9 ≤ t ≤ 21** rests on the closure computation, not on the proof; the construction of the
   proof also passes its guard for t = 19, 21, so the two methods agree where both were run.
3. **Citations.** Forward citations of [A80], [L96], [DI07] were checked in OpenAlex only (2026-11-26); zbMATH
   refused automated access and MathSciNet needs a subscription, so one of the two should still be consulted by
   hand. Citing relations and titles were taken from the index, partly through machine summaries. Not read in
   full text: Karzanov, *Metrics with finite sets of primitive extensions* (Ann. Comb. 2, 1998); Grishukhin,
   *Computing extreme rays of the metric cone for seven points* (European J. Combin. 13, 1992); Avis, *Extremal
   metrics induced by graphs* (Ann. Discrete Math. 8, 1980); the thesis on the "metric body" behind [FK26]; [FK26]
   itself (record description only); the second half of [CJK24]. [CL25] §7, [La25] §4.2 onwards and [Bo18] §2.2
   onwards were read in summary only. The page numbers of [KMT00] and [SY04] are from memory; the bibliographic
   data of [MPV08], [CJK24], [FK26] come from index records and should be checked against the papers.
4. **The m_9 count.** The file has one orbit fewer than published (Section 6); the authors of the list could
   confirm which number is right.
5. **Values marked *** (C5, C6) should be re-run in rational arithmetic or dropped.
6. **Earlier numbering.** In the project notes (`docs/phase9_status.md`) Theorem 6 is "Theorem 1", Proposition 5 is
   "Corollary 1", and C3–C12 appear as C2′, C3–C3⁗, C4–C9.

## References

- [A80] D. Avis, On the extreme rays of the metric cone, Canad. J. Math. 32 (1980) 126–144.
- [BD92] H.-J. Bandelt, A. W. M. Dress, A canonical decomposition theory for metrics on a finite set, Adv. Math. 92
  (1992) 47–105.
- [Bo18] G. Bodwin, On the structure of unique shortest paths in graphs, arXiv:1804.09745.
- [CJK24] L. Casabella, M. Joswig, L. Kastner, Subdivisions of hypersimplices: with a view toward finite metric
  spaces, Exp. Math. (2024), arXiv:2402.17665.
- [CL25] D. Cizma, N. Linial, On the number of path systems, arXiv:2508.21379v3 (2025).
- [FK26] D. V. Feldman, E. R. Kehoe, Extreme rays of the metric cone and the metric body: bowtie metrics and
  half-one extremality, preprint, Zenodo, doi:10.5281/zenodo.21898516 (2026).
- [MPV08] J. Melleray, F. V. Petrov, A. M. Vershik, Linearly rigid metric spaces and the embedding problem, Fund.
  Math. 199 (2008) 177–194, arXiv:math/0611049.
- [DD-web] A. Deza, metric polytope data page, www.cas.mcmaster.ca/~deza/metric.html.
- [DDF96] A. Deza, M. Deza, K. Fukuda, On skeletons, diameters and volumes of metric polyhedra, LNCS 1120 (1996)
  112–128.
- [DFPS01] A. Deza, K. Fukuda, D. Pasechnik, M. Sato, On the skeleton of the metric polytope, LNCS 2098 (2001)
  125–136.
- [DFMV03] A. Deza, K. Fukuda, T. Mizutani, C. Vo, On the face lattice of the metric polytope, LNCS 2866 (2003)
  118–128.
- [DI07] A. Deza, G. Indik, A counterexample to the dominating set conjecture, Optim. Lett. 1 (2007) 163–169.
- [DL97] M. Deza, M. Laurent, Geometry of Cuts and Metrics, Springer, 1997.
- [KMT00] J. Koolen, V. Moulton, U. Tönges, A classification of the six-point prime metrics, European J. Combin. 21
  (2000) 815–829.
- [La25] A. Lavrov, Ternary relations and their polytopes, arXiv:2509.06811 (2025).
- [L96] M. Laurent, Graphic vertices of the metric polytope, Discrete Math. 151 (1996) 131–153.
- [LP92] M. Laurent, S. Poljak, One-third-integrality in the max-cut problem, Math. Programming 71 (1995) 29–50
  (CWI Report BS-R9209, 1992).
- [SY04] B. Sturmfels, J. Yu, Classification of six-point metrics, Electron. J. Combin. 11 (2004) R44.
