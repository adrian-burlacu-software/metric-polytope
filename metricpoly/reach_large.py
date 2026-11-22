"""Reachability for single points at any n (no canonical forms; Phase 9b judge).

Base test (exact, up to switching and permutation), matching the uniform base set:
  - cut orbit       : x is 0/1 and equals some cut δ(S)
  - graph metric    : some switching y of x equals x_G = (2/τ(G)) d_G   (parity-constraint search, not 2^(n-1) loop)
  - third families  : some switching y equals (1/3) d_G with G complete multipartite (>= 2 parts), complete
                      multipartite minus one edge (connected), or the suspension of a tree
Search: top-down over node subsets (memo by bitmask), moves in cost order lift -> radial -> glue, with a budget.
Result for the full point: True (certificate), False (complete search, nothing reaches it), None (undecided:
budget hit or a move skipped because the subset is too large: radial for |T| > RADIAL_MAX, glue for |T| > GLUE_MAX).
"""
from __future__ import annotations

import itertools
import time
from collections import deque
from fractions import Fraction
from typing import Optional

import numpy as np

from .core import Point, pairs
from .graphic import is_graph_metric

RADIAL_MAX = 14
GLUE_MAX = 11


def matrix(x: Point) -> np.ndarray:
    M = np.zeros((x.n, x.n), dtype=np.int64)
    for v, (i, j) in zip(x.nums, pairs(x.n)):
        M[i, j] = M[j, i] = v
    return M


def from_matrix(M, D, T) -> Point:
    T = list(T)
    return Point.make(len(T), D, [int(M[T[a], T[b]]) for a in range(len(T)) for b in range(a + 1, len(T))])


# ------------------------------------------------------------------ parity union-find
class _UF:
    def __init__(self, n):
        self.p = list(range(n))
        self.par = [0] * n          # parity to parent

    def find(self, a):
        if self.p[a] == a:
            return a, 0
        r, q = self.find(self.p[a])
        self.p[a] = r
        self.par[a] ^= q
        return r, self.par[a]

    def union(self, a, b, d):
        """impose s_a xor s_b = d; False on contradiction."""
        ra, pa = self.find(a)
        rb, pb = self.find(b)
        if ra == rb:
            return (pa ^ pb) == d
        self.p[ra] = rb
        self.par[ra] = pa ^ pb ^ d
        return True


def _switchings_by_parity(n, allowed, cap=4096):
    """allowed[(i,j)] subset of {0,1} = permitted values of s_i xor s_j. Yield all side vectors s (s_0 = 0) satisfying
    every forced pair, enumerating free components (None if more than cap)."""
    uf = _UF(n)
    for (i, j), al in allowed.items():
        if not al:
            return []
        if len(al) == 1:
            if not uf.union(i, j, next(iter(al))):
                return []
    roots = sorted({uf.find(v)[0] for v in range(n)})
    r0 = uf.find(0)[0]
    free = [r for r in roots if r != r0]
    if len(free) > 12 or (1 << len(free)) > cap:
        return None
    out = []
    for bits in range(1 << len(free)):
        rootval = {r0: 0}
        for t, r in enumerate(free):
            rootval[r] = (bits >> t) & 1
        s = []
        for v in range(n):
            r, pv = uf.find(v)
            s.append(rootval[r] ^ pv)
        sv = s[0]
        s = [b ^ sv for b in s]
        if all((s[i] ^ s[j]) in al for (i, j), al in allowed.items()):
            out.append(s)
    return out


def graphic_orbit(x: Point) -> Optional[bool]:
    """Exact: some switching of x is a graph metric x_G. None if the free choices exceed the enumeration cap."""
    n, D = x.n, x.D
    pr = pairs(n)
    a = list(x.nums)
    cands = sorted({v for v in a if v > 0} | {D - v for v in a if D - v > 0})
    undecided = False
    for m in cands:
        allowed = {}
        for e, (i, j) in enumerate(pr):
            al = set()
            if a[e] > 0 and a[e] % m == 0:
                al.add(0)
            if D - a[e] > 0 and (D - a[e]) % m == 0:
                al.add(1)
            allowed[(i, j)] = al
        S = _switchings_by_parity(n, allowed)
        if S is None:
            undecided = True
            continue
        for s in S:
            y = [D - a[e] if s[i] ^ s[j] else a[e] for e, (i, j) in enumerate(pr)]
            if min(y) == m and is_graph_metric(y, D, n):
                return True
    return None if undecided else False


def cut_orbit(x: Point) -> bool:
    if x.D != 1:
        return False
    M = matrix(x)
    side = M[0]
    return bool(all(M[i, j] == (side[i] ^ side[j]) for i, j in pairs(x.n)))


def _third_family(G_adj, n) -> bool:
    """G (as adjacency sets) is complete multipartite (>=2 parts), complete multipartite minus one edge (connected),
    or a tree suspension (apex adjacent to all others, others induce a tree)."""
    non = [(i, j) for i, j in pairs(n) if j not in G_adj[i]]

    def multipartite(nonedges):
        # complement graph is a disjoint union of cliques, with >= 2 classes
        par = list(range(n))

        def f(a):
            while par[a] != a:
                par[a] = par[par[a]]
                a = par[a]
            return a
        for i, j in nonedges:
            par[f(i)] = f(j)
        cls = {}
        for v in range(n):
            cls.setdefault(f(v), []).append(v)
        S = set(nonedges)
        for c in cls.values():
            for i, j in itertools.combinations(sorted(c), 2):
                if (i, j) not in S:
                    return False
        return len(cls) >= 2
    if multipartite(non):
        return True
    for e in non:                                   # minus one edge: removing e from the non-edges restores it
        rest = [f for f in non if f != e]
        if multipartite(rest):
            return True
    for apex in range(n):                           # tree suspension
        if len(G_adj[apex]) == n - 1:
            others = [v for v in range(n) if v != apex]
            E = [(i, j) for i, j in pairs(n) if i != apex and j != apex and j in G_adj[i]]
            if len(E) == n - 2:
                par = {v: v for v in others}

                def g(a):
                    while par[a] != a:
                        a = par[a]
                    return a
                ok = True
                for i, j in E:
                    ri, rj = g(i), g(j)
                    if ri == rj:
                        ok = False
                        break
                    par[ri] = rj
                if ok:
                    return True
    return False


def third_orbit(x: Point) -> Optional[bool]:
    """Exact: some switching y of x equals (1/3) d_G with G in the third families (values 1/3, 2/3 only)."""
    if x.D != 3 or any(v not in (1, 2) for v in x.nums):
        return False
    n = x.n
    if n > 16:
        return None
    M = matrix(x)
    for s in range(1 << (n - 1)):
        side = [0] + [(s >> (v - 1)) & 1 for v in range(1, n)]
        adj = [set() for _ in range(n)]
        for i, j in pairs(n):
            val = M[i, j] if side[i] == side[j] else 3 - M[i, j]
            if val == 1:
                adj[i].add(j)
                adj[j].add(i)
        if _third_family(adj, n):
            return True
    return False


def is_base(x: Point) -> Optional[bool]:
    if cut_orbit(x):
        return True
    g = graphic_orbit(x)
    if g:
        return True
    t = third_orbit(x)
    if t:
        return True
    return None if (g is None or t is None) else False


# ------------------------------------------------------------------ moves (exact; same checks as the judge's engine)
def _d2():
    import sys
    from pathlib import Path
    sp = str(Path(__file__).resolve().parent.parent / "scripts")
    if sp not in sys.path:
        sys.path.insert(0, sp)
    import detour_depth2 as d2
    return d2


def _fiber_vertex(y: Point, holes) -> bool:
    return _d2().fiber_vertex(y, holes)


def _radial_preds(y: Point):
    return [R for _, R in _d2().radial_preds(y)]


def reachable(x: Point, budget: float = 120.0, small_oracle=None):
    """Top-down search. small_oracle(point) -> True/False for |T| <= 9 if supplied (e.g. the judge's engine)."""
    t_end = time.time() + budget
    M, D, n = matrix(x), x.D, x.n
    memo, incomplete = {}, [False]

    def pt(T):
        return from_matrix(M, D, T)

    def rec(mask):
        if mask in memo:
            return memo[mask]
        if time.time() > t_end:
            incomplete[0] = True
            return False
        T = [v for v in range(n) if (mask >> v) & 1]
        y = pt(T)
        memo[mask] = False                           # cycle guard (moves only add nodes, so no real cycles)
        if small_oracle is not None and len(T) <= 9:
            r = small_oracle(y)
            memo[mask] = bool(r)
            return memo[mask]
        b = is_base(y)
        if b:
            memo[mask] = True
            return True
        if b is None:
            incomplete[0] = True
        k = len(T)
        if k <= 3:
            return False
        for a, v in enumerate(T):                   # lift
            holes = [(min(a, b2), max(a, b2)) for b2 in range(k) if b2 != a]
            if _fiber_vertex(y, holes) and rec(mask & ~(1 << v)):
                memo[mask] = True
                return True
        if k <= RADIAL_MAX:                         # radial
            for R in _radial_preds(y):
                if rec(sum(1 << T[r] for r in R)):
                    memo[mask] = True
                    return True
        else:
            incomplete[0] = True
        if k <= GLUE_MAX:                           # glue (uncapped overlap)
            full = (1 << k) - 1
            for am in range(1, full):
                if bin(am).count("1") < 3:
                    continue
                Ab = [i for i in range(k) if (am >> i) & 1]
                if not rec(sum(1 << T[i] for i in Ab)):         # both parts must be reachable: test that first
                    continue
                for kk in range(1, len(Ab)):
                    for K in itertools.combinations(Ab, kk):
                        bm = (full & ~am) | sum(1 << i for i in K)
                        if bin(bm).count("1") < 3:
                            continue
                        Bm = sum(1 << T[i] for i in range(k) if (bm >> i) & 1)
                        if not rec(Bm):
                            continue
                        onlyA = [i for i in Ab if i not in K]
                        onlyB = [i for i in range(k) if (bm >> i) & 1 and i not in K]
                        holes = [(min(i, j), max(i, j)) for i in onlyA for j in onlyB]
                        if _fiber_vertex(y, holes):
                            memo[mask] = True
                            return True
        else:
            incomplete[0] = True
        return False

    r = rec((1 << n) - 1)
    if r:
        return True, len(memo)
    return (None if incomplete[0] else False), len(memo)
