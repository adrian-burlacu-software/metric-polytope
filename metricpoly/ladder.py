"""Phase 10: the edge-by-edge ladder from m_{n-1} to m_n.

Rung (nK, k): graph G_k = K_nK on nodes 0..nK-1 plus a new node w = nK joined to N = {0, .., k-1}. G_{nK} = K_{nK+1}.
Polytope P_k = projection of m_{nK+1} onto the edges of G_k. G_k is chordal (N is a clique), so by Barahona's
description of the projection of the metric polytope (cycle inequalities; chordless cycles of a chordal graph are
triangles) P_k is cut out by the triangle and perimeter inequalities of the triangles of G_k, plus 0 <= x_e <= 1 for
edges in no triangle (only the edge w-0 when k = 1). This list is VERIFIED in code (scripts/phase10/verify_rungs.py),
not assumed.

Points are integer numerators over a common denominator D, in the order of `Rung.edges` (lexicographic pairs of G_k).

Symmetry group of a rung: permutations of N among themselves and of K \\ N among themselves (w fixed), and switchings
x -> 1 - x on the edges of a cut δ(S) of G_k. Canonical form: switching normalised at a root r (row r <= 1/2; ties at 1/2
branch); roots = N (k >= 1) or K (k = 0), restricted to those with the fewest ties (an invariant set); then bliss on a
vertex-coloured incidence graph whose colours encode N / K\\N / w and the edge values. Stabiliser by counting the
root normalisations isomorphic to the chosen one times the rooted automorphism count (bliss).
Neighbours of a vertex: extreme rays of its tangent cone (exact cdd), each followed to the next facet.
"""
from __future__ import annotations

import itertools
import math
from fractions import Fraction
from functools import lru_cache
from typing import List, Optional, Tuple

import cdd
import cdd.gmp
import igraph as ig
import numpy as np

TIE_CAP = 1 << 12


class Rung:
    def __init__(self, nK: int, k: int):
        assert 0 <= k <= nK
        self.nK, self.k = nK, k
        self.n = nK + 1                                   # nodes 0..nK, w = nK
        self.w = nK
        self.N = list(range(k))
        E = [(i, j) for i in range(nK) for j in range(i + 1, nK)] + [(a, nK) for a in range(k)]
        self.edges = sorted(E)
        self.eidx = {e: t for t, e in enumerate(self.edges)}
        self.m = len(self.edges)
        adj = [set() for _ in range(self.n)]
        for i, j in self.edges:
            adj[i].add(j)
            adj[j].add(i)
        self.adj = adj
        rows, rhs, self.row_desc = [], [], []
        tris = [t for t in itertools.combinations(range(self.n), 3)
                if t[1] in adj[t[0]] and t[2] in adj[t[0]] and t[2] in adj[t[1]]]
        in_tri = set()
        for i, j, l in tris:
            e = [self.eidx[(i, j)], self.eidx[(i, l)], self.eidx[(j, l)]]
            in_tri.update(e)
            for s in range(3):                             # x_e_s - x_others <= 0
                a = [0] * self.m
                for t in range(3):
                    a[e[t]] = 1 if t == s else -1
                rows.append(a)
                rhs.append(0)
                self.row_desc.append(("tri", (i, j, l), s))
            a = [0] * self.m
            for t in range(3):
                a[e[t]] = 1
            rows.append(a)
            rhs.append(2)
            self.row_desc.append(("per", (i, j, l)))
        for t in range(self.m):                            # edges in no triangle: 0 <= x <= 1
            if t not in in_tri:
                a = [0] * self.m
                a[t] = -1
                rows.append(a)
                rhs.append(0)
                self.row_desc.append(("lo", self.edges[t]))
                a = [0] * self.m
                a[t] = 1
                rows.append(a)
                rhs.append(1)
                self.row_desc.append(("hi", self.edges[t]))
        self.A = np.array(rows, dtype=np.int64)
        self.b = np.array(rhs, dtype=np.int64)
        # symmetry group = Aut(G_k) with switchings ("relabelings preserving G_k"). Generic k: N and the rest of K
        # permuted separately, w fixed. k = nK: G = K_n and Aut = S_n (w is not special). k = nK - 1: w and the single
        # non-neighbour u of w have the same neighbourhood N, so the swap u <-> w is an automorphism as well.
        ncomp = 1 if k >= 1 else 2
        if k == nK:
            self.color_node = [0] * self.n
            perm_order = math.factorial(self.n)
            self.roots = list(range(self.n))
        elif k == nK - 1 and nK >= 2:
            self.u = nK - 1
            self.color_node = [0 if v in self.N else 2 for v in range(nK)] + [2]
            perm_order = math.factorial(k) * 2
            self.roots = self.N
        else:
            self.color_node = [0 if v in self.N else 1 for v in range(nK)] + [2]
            perm_order = math.factorial(k) * math.factorial(nK - k)
            self.roots = self.N if k >= 1 else list(range(nK))
        self.group_order = perm_order * (1 << (self.n - ncomp))

    # ---------------------------------------------------------------- exact basics
    def slacks(self, D: int, nums) -> np.ndarray:
        return D * self.b - self.A @ np.asarray(nums, dtype=np.int64)

    def tight(self, D: int, nums) -> np.ndarray:
        return np.nonzero(self.slacks(D, nums) == 0)[0]

    def feasible(self, D: int, nums) -> bool:
        return bool((self.slacks(D, nums) >= 0).all())

    def is_vertex(self, D: int, nums) -> bool:
        """Exact: feasible and the tight rows have rank m (= number of edges)."""
        if not self.feasible(D, nums):
            return False
        T = self.tight(D, nums)
        if len(T) < self.m:
            return False
        from .dsl.prims import certified_rank_is
        return bool(certified_rank_is(self.A[T], self.m))

    # ---------------------------------------------------------------- symmetry
    def _matrix(self, D, nums):
        M = np.full((self.n, self.n), -1, dtype=np.int64)
        for (i, j), v in zip(self.edges, nums):
            M[i, j] = M[j, i] = v
        return M

    def _normalisations(self, D, nums):
        """All (root, switched matrix) with the root row <= 1/2, over the roots with the fewest ties."""
        M = self._matrix(D, nums)
        ties = {}
        for r in self.roots:
            ties[r] = [j for j in self.adj[r] if 2 * M[r, j] == D]
        tmin = min(len(v) for v in ties.values())
        if (1 << tmin) > TIE_CAP:
            raise ValueError(f"rung canonical form: {tmin} ties exceed the cap")
        out = []
        for r in self.roots:
            if len(ties[r]) != tmin:
                continue
            base = [0] * self.n
            for j in self.adj[r]:
                if 2 * M[r, j] > D:
                    base[j] = 1
            # nodes not adjacent to r (only possible for k = 0: w; or r not in N): side fixed at 0
            for bits in range(1 << tmin):
                side = list(base)
                for t, j in enumerate(ties[r]):
                    side[j] = (bits >> t) & 1
                Y = M.copy()
                for i, j in self.edges:
                    if side[i] != side[j]:
                        Y[i, j] = Y[j, i] = D - M[i, j]
                out.append((r, Y))
        return out

    def _graph(self, Y, root=None):
        n = self.n
        colors = [c if (root is None or v != root) else 3 for v, c in enumerate(self.color_node)]
        edges = []
        for t, (i, j) in enumerate(self.edges):
            v = n + t
            colors.append(4 + int(Y[i, j]))
            edges.append((i, v))
            edges.append((j, v))
        return ig.Graph(n=n + self.m, edges=edges), colors

    def _canon_of(self, Y):
        g, colors = self._graph(Y)
        lab = g.canonical_permutation(color=colors)            # lab[i] = original vertex at canonical position i
        pos = {v: p for p, v in enumerate(v for v in lab if v < self.n)}
        trip = sorted((min(pos[i], pos[j]), max(pos[i], pos[j]), int(Y[i, j]),
                       self.color_node[i] + self.color_node[j]) for i, j in self.edges)
        node_cols = tuple(self.color_node[v] for v in sorted(range(self.n), key=lambda v: pos[v]))
        return (node_cols, tuple(trip))

    def canonical_key(self, D, nums) -> str:
        best = min(self._canon_of(Y) for _, Y in self._normalisations(D, nums))
        return f"R{self.nK}.{self.k}|{D}|" + ";".join(f"{a},{b},{v}" for a, b, v, _ in best[1])

    def stabilizer_size(self, D, nums) -> int:
        norms = self._normalisations(D, nums)
        r0, Y0 = norms[0]
        g0, c0 = self._graph(Y0, root=r0)
        same = 0
        for r, Y in norms:
            g, c = self._graph(Y, root=r)
            if g.isomorphic_bliss(g0, color1=c, color2=c0):
                same += 1
        return same * g0.count_automorphisms(color=c0)

    def orbit_size(self, D, nums) -> int:
        st = self.stabilizer_size(D, nums)
        assert self.group_order % st == 0
        return self.group_order // st

    def apply(self, D, nums, perm, side) -> Tuple[int, ...]:
        """Image under node permutation perm (perm[v] = image of v; must preserve N, K\\N, w) then switching side."""
        M = self._matrix(D, nums)
        out = []
        inv = {perm[v]: v for v in range(self.n)}
        for i, j in self.edges:
            a, b = inv[i], inv[j]
            v = int(M[a, b])
            out.append(D - v if side[i] != side[j] else v)
        return tuple(out)

    def _blocks(self):
        cls = {}
        for v, c in enumerate(self.color_node):
            cls.setdefault(c, []).append(v)
        return list(cls.values())

    def group_perms(self):
        """All node permutations in Aut(G_k) (as image lists), for brute-force checks on small rungs."""
        blocks = self._blocks()
        for combo in itertools.product(*[itertools.permutations(b) for b in blocks]):
            perm = [0] * self.n
            for b, img in zip(blocks, combo):
                for v, t in zip(b, img):
                    perm[v] = t
            yield perm

    def random_element(self, rng):
        perm = list(range(self.n))
        for b in self._blocks():
            for v, t in zip(b, rng.permutation(b)):
                perm[v] = int(t)
        side = [0] + [int(rng.integers(0, 2)) for _ in range(self.n - 1)]
        return perm, side

    # ---------------------------------------------------------------- neighbours
    def neighbours(self, D, nums, max_rays: Optional[int] = None):
        """Adjacent vertices of the vertex (D, nums): extreme rays of the tangent cone {d : A_T d <= 0} (exact cdd),
        each followed to the first leaving facet. Returns list of (D', nums') (each completed and checked) and the
        ray count."""
        T = self.tight(D, nums)
        AT = self.A[T]
        mat = cdd.gmp.matrix_from_array([[Fraction(0)] + [Fraction(-int(v)) for v in row] for row in AT],
                                        rep_type=cdd.RepType.INEQUALITY)
        P = cdd.gmp.polyhedron_from_matrix(mat)
        gens = cdd.gmp.copy_generators(P)
        if gens.lin_set:
            raise RuntimeError("tangent cone not pointed: point is not a vertex")
        rays = [r[1:] for r in gens.array if r[0] == 0]
        if max_rays is not None and len(rays) > max_rays:
            return None, len(rays)
        x = [Fraction(v, D) for v in nums]
        s = self.slacks(D, nums)
        out = []
        nonT = np.nonzero(s != 0)[0]
        for d in rays:
            dd = [Fraction(v) for v in d]
            best = None
            for i in nonT:
                ad = sum(int(self.A[i, t]) * dd[t] for t in range(self.m) if self.A[i, t])
                if ad > 0:
                    t_i = Fraction(int(s[i]), D) / ad
                    if best is None or t_i < best:
                        best = t_i
            if best is None:
                raise RuntimeError("unbounded edge in a polytope")
            y = [x[t] + best * dd[t] for t in range(self.m)]
            Dy = 1
            for f in y:
                Dy = Dy * f.denominator // math.gcd(Dy, f.denominator)
            ny = tuple(int(f * Dy) for f in y)
            out.append((Dy, ny))
        return out, len(rays)


@lru_cache(maxsize=None)
def rung(nK: int, k: int) -> Rung:
    return Rung(nK, k)
