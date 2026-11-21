"""The symmetry group G_n = switchings x| S_n acting on m_n, canonical forms, stabilizers.

Group elements are pairs (p, s): p indexes a permutation pi in perms(n), s is a bitmask
S over nodes 1..n-1 (node 0 is never in S, so the 2^(n-1) switchings are distinct).
Action:  g.x = switch_S(pi.x).

Two implementations of the canonical form are provided:
- canonical_brute: literal min over all 2^(n-1) n! group elements (reference).
- canonical:       same result, but for each pi the switching is forced by the first n-1
                   coordinates x_{0j} (choose x_{0j} <= 1/2), branching only on ties x_{0j}=1/2,
                   and only for the pis whose forced prefix is lexicographically minimal.
They are cross-checked in tests/.
"""
from __future__ import annotations

import itertools
import math
from functools import lru_cache
from typing import Iterator, List, Optional, Tuple

import numpy as np

from .core import Point, dim, pairs, pidx


# ---------------------------------------------------------------- tables

@lru_cache(maxsize=None)
def perms(n: int) -> Tuple[Tuple[int, ...], ...]:
    return tuple(itertools.permutations(range(n)))


@lru_cache(maxsize=None)
def perm_src(n: int) -> np.ndarray:
    """perm_src[p, e] = index of the coordinate of x that lands on coordinate e of pi_p.x.

    (pi.x)_{pi(i) pi(j)} = x_{ij}, so (pi.x)_{ab} = x_{pi^-1(a) pi^-1(b)}.
    """
    P = perms(n)
    m = dim(n)
    pr = pairs(n)
    out = np.empty((len(P), m), dtype=np.int32)
    for k, pi in enumerate(P):
        inv = [0] * n
        for i, v in enumerate(pi):
            inv[v] = i
        out[k] = [pidx(n, inv[a], inv[b]) for (a, b) in pr]
    out.setflags(write=False)
    return out


@lru_cache(maxsize=None)
def switch_flips(n: int) -> np.ndarray:
    """flips[s, e] = True iff edge e crosses the cut (S, V\\S); S = bitmask over nodes 1..n-1."""
    m = dim(n)
    pr = pairs(n)
    out = np.zeros((1 << (n - 1), m), dtype=bool)
    for s in range(1 << (n - 1)):
        side = [0] + [(s >> (v - 1)) & 1 for v in range(1, n)]
        out[s] = [side[a] != side[b] for (a, b) in pr]
    out.setflags(write=False)
    return out


def group_order(n: int) -> int:
    return (1 << (n - 1)) * math.factorial(n)


def apply(n: int, p: int, s: int, x: Point) -> Point:
    y = x.array()[perm_src(n)[p]]
    y = np.where(switch_flips(n)[s], x.D - y, y)
    return Point.make(n, x.D, y.tolist())


def random_element(n: int, rng: np.random.Generator) -> Tuple[int, int]:
    return int(rng.integers(len(perms(n)))), int(rng.integers(1 << (n - 1)))


# ---------------------------------------------------------------- lexmin helpers

def lexmin_rows(M: np.ndarray) -> np.ndarray:
    """Indices of all rows equal to the lexicographic minimum row."""
    idx = np.arange(M.shape[0])
    for c in range(M.shape[1]):
        v = M[idx, c]
        idx = idx[v == v.min()]
        if idx.size == 1:
            break
    return idx


def _lt(a: np.ndarray, b: Optional[np.ndarray]) -> bool:
    if b is None:
        return True
    d = np.flatnonzero(a != b)
    return bool(d.size) and a[d[0]] < b[d[0]]


def _dtype_for(D: int):
    return np.int16 if D < 2**15 else np.int64


# ---------------------------------------------------------------- canonical forms

def canonical_brute(x: Point, chunk: int = 512) -> Point:
    """Reference: lexmin of g.x over every group element (chunked over permutations)."""
    n = x.n
    dt = _dtype_for(x.D)
    xs = x.array().astype(dt)
    F = switch_flips(n)
    best = None
    PS = perm_src(n)
    for c0 in range(0, PS.shape[0], chunk):
        X = xs[PS[c0:c0 + chunk]]                                   # (c, m)
        Y = np.where(F[None, :, :], dt(x.D) - X[:, None, :], X[:, None, :]).reshape(-1, X.shape[1])
        r = Y[lexmin_rows(Y)[0]]
        if _lt(r, best):
            best = r.copy()
    return Point(n, x.D, tuple(int(v) for v in best))


def switch_canon(x: Point) -> Point:
    """Lexmin over the 2^(n-1) switchings only (labeling fixed)."""
    n = x.n
    X = x.array()
    F = switch_flips(n)
    Y = np.where(F, x.D - X[None, :], X[None, :])
    return Point(n, x.D, tuple(int(v) for v in Y[lexmin_rows(Y)[0]]))


def _consistent_switchings(Xpre: np.ndarray, target_pre: np.ndarray, D: int, n: int) -> Tuple[np.ndarray, np.ndarray]:
    """For rows of Xpre (= first n-1 coords x_{0j}, j=1..n-1), list (row, s) pairs whose switching
    maps the prefix onto target_pre. Returns arrays (rows, s)."""
    same = Xpre == target_pre[None, :]                 # j not in S works
    flip = (D - Xpre) == target_pre[None, :]           # j in S works
    ok = (same | flip).all(axis=1)
    rows = np.flatnonzero(ok)
    if rows.size == 0:
        return rows, rows
    bits = (1 << np.arange(n - 1)).astype(np.int64)
    forced_in = ((flip[rows] & ~same[rows]) * bits).sum(axis=1)       # must be in S
    free = ((flip[rows] & same[rows]) * bits).sum(axis=1)             # either
    allS = np.arange(1 << (n - 1), dtype=np.int64)
    # s consistent iff (s & ~free) == forced_in
    full = (1 << (n - 1)) - 1
    C = (allS[None, :] & (full & ~free)[:, None]) == forced_in[:, None]
    ri, si = np.nonzero(C)
    return rows[ri], si


def canonical(x: Point, chunk_rows: int = 200_000) -> Point:
    """Lexmin of g.x over G_n (fast, exact; equals canonical_brute)."""
    n = x.n
    D = x.D
    xs = x.array()
    X = xs[perm_src(n)]                                       # (n!, m)
    pre = np.minimum(X[:, :n - 1], D - X[:, :n - 1])
    surv = lexmin_rows(pre)
    target = pre[surv[0]]
    Xs = X[surv]
    rows, ss = _consistent_switchings(Xs[:, :n - 1], target, D, n)
    F = switch_flips(n)
    best = None
    for c0 in range(0, rows.size, chunk_rows):
        r, s = rows[c0:c0 + chunk_rows], ss[c0:c0 + chunk_rows]
        Y = np.where(F[s], D - Xs[r], Xs[r])
        cand = Y[lexmin_rows(Y)[0]]
        if _lt(cand, best):
            best = cand.copy()
    return Point(n, D, tuple(int(v) for v in best))


def canonical_with_element(x: Point) -> Tuple[Point, int, int]:
    """(canonical form c, p, s) with apply(n, p, s, x) == c."""
    n, D = x.n, x.D
    X = x.array()[perm_src(n)]
    pre = np.minimum(X[:, :n - 1], D - X[:, :n - 1])
    surv = lexmin_rows(pre)
    rows, ss = _consistent_switchings(X[surv][:, :n - 1], pre[surv[0]], D, n)
    F = switch_flips(n)
    best, arg = None, None
    for c0 in range(0, rows.size, 200_000):
        r, s = rows[c0:c0 + 200_000], ss[c0:c0 + 200_000]
        Y = np.where(F[s], D - X[surv][r], X[surv][r])
        k = lexmin_rows(Y)[0]
        if _lt(Y[k], best):
            best, arg = Y[k].copy(), (int(surv[r[k]]), int(s[k]))
    return Point(n, D, tuple(int(v) for v in best)), arg[0], arg[1]


def switch_canon_fast(x: Point) -> Point:
    """= switch_canon(x), but the switching is forced by x_{0j} (branch only on x_{0j} = 1/2)."""
    n, D = x.n, x.D
    X = x.array()[None, :]
    target = np.minimum(X[:, :n - 1], D - X[:, :n - 1])[0]
    rows, ss = _consistent_switchings(X[:, :n - 1], target, D, n)
    Y = np.where(switch_flips(n)[ss], D - X[0][None, :], X[0][None, :])
    return Point(n, D, tuple(int(v) for v in Y[lexmin_rows(Y)[0]]))


@lru_cache(maxsize=None)
def ineq_action(n: int, p: int, s: int) -> np.ndarray:
    """out[f] = index of the facet g.f for g = (p, s); slack is preserved: slack(g.x, g.f) = slack(x, f)."""
    from .patterns import catalog_clauses, clause_index, permute_clause, switch_clause
    C = catalog_clauses(n)
    ci = clause_index(n)
    pi = perms(n)[p]
    S = [v for v in range(1, n) if (s >> (v - 1)) & 1]
    return np.array([ci[switch_clause(permute_clause(c, pi), S)] for c in C], dtype=np.int64)


def canonical_via_switch_canon(x: Point) -> Point:
    """min over pi of switch_canon(pi.x) -- the literal user definition, O(n! 2^(n-1))."""
    n = x.n
    best = None
    for p in range(len(perms(n))):
        c = np.asarray(switch_canon(apply(n, p, 0, x)).nums)
        if _lt(c, best):
            best = c
    return Point(n, x.D, tuple(int(v) for v in best))


# ---------------------------------------------------------------- stabilizer / orbit

def stabilizer_size(x: Point) -> int:
    """|Stab_G(x)| = #{(pi,S): switch_S(pi.x) == x}."""
    n = x.n
    xs = x.array()
    X = xs[perm_src(n)]
    rows, ss = _consistent_switchings(X[:, :n - 1], xs[:n - 1], x.D, n)
    if rows.size == 0:
        return 0
    F = switch_flips(n)
    cnt = 0
    for c0 in range(0, rows.size, 200_000):
        r, s = rows[c0:c0 + 200_000], ss[c0:c0 + 200_000]
        Y = np.where(F[s], x.D - X[r], X[r])
        cnt += int((Y == xs[None, :]).all(axis=1).sum())
    return cnt


def stabilizer_size_brute(x: Point) -> int:
    n = x.n
    xs = x.array()
    F = switch_flips(n)
    cnt = 0
    for X in xs[perm_src(n)]:
        Y = np.where(F, x.D - X[None, :], X[None, :])
        cnt += int((Y == xs[None, :]).all(axis=1).sum())
    return cnt


def orbit_array(x: Point, L: Optional[int] = None, chunk: int = 256) -> np.ndarray:
    """All distinct images g.x as integer rows over denominator L (default x.D). Sorted, unique."""
    n = x.n
    L = x.D if L is None else L
    if L % x.D:
        raise ValueError("L must be a multiple of x.D")
    dt = _dtype_for(L)
    xs = (x.array() * (L // x.D)).astype(dt)
    F = switch_flips(n)
    PS = perm_src(n)
    parts = []
    for c0 in range(0, PS.shape[0], chunk):
        X = xs[PS[c0:c0 + chunk]]
        Y = np.where(F[None, :, :], dt(L) - X[:, None, :], X[:, None, :]).reshape(-1, X.shape[1])
        parts.append(np.unique(Y, axis=0))
    return np.unique(np.concatenate(parts), axis=0)
