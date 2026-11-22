"""The cut orbit's neighbourhood: extreme rays of the metric cone MET_n (the tangent cone of m_n at the zero cut).

Q_n = MET_n ∩ {sum x = 1}: a polytope whose vertices are the extreme rays of MET_n (normalised), and whose edges are the
2-faces of MET_n (adjacent rays). The neighbours of the zero cut in m_n are exactly the points (2/τ(r)) r for the extreme
rays r (Laurent–Poljak; τ(r) = largest triangle perimeter). Symmetry of the cone at the zero cut: S_n only (a switching
moves the zero cut). Canonical form: bliss on the coloured incidence graph (permutations only), validated in
scripts/phase10/met_rays.py against brute force at small n.
"""
from __future__ import annotations

import itertools
import math

import igraph as ig
import numpy as np

from .core import pairs
from .ladder import Rung


def q_polytope(n: int) -> Rung:
    """Q_n as a Rung-like H-polytope over the pairs of K_n: triangle rows x_ij - x_ik - x_jk <= 0, and sum x = 1
    as two inequalities. Reuses Rung's exact slack / vertex / neighbour code."""
    R = Rung(n - 1, n - 1)
    keep = [i for i, d in enumerate(R.row_desc) if d[0] == "tri"]
    A = R.A[keep]
    b = R.b[keep]
    ones = np.ones((1, R.m), dtype=np.int64)
    R.A = np.vstack([A, ones, -ones])
    R.b = np.concatenate([b, [1, -1]])
    R.row_desc = [R.row_desc[i] for i in keep] + [("sum", "<="), ("sum", ">=")]
    return R


def _graph(n, D, nums):
    pr = pairs(n)
    edges, colors = [], [0] * n
    for e, (i, j) in enumerate(pr):
        v = n + e
        colors.append(1 + int(nums[e]))
        edges.append((i, v))
        edges.append((j, v))
    return ig.Graph(n=n + len(pr), edges=edges), colors


def perm_key(n, D, nums) -> str:
    """Canonical form under S_n only (no switching)."""
    g, colors = _graph(n, D, nums)
    lab = g.canonical_permutation(color=colors)           # lab[i] = original vertex at canonical position i
    order = [v for v in lab if v < n]
    pos = {v: p for p, v in enumerate(order)}
    pr = pairs(n)
    idx = {e: t for t, e in enumerate(pr)}
    vals = tuple(int(nums[idx[(min(order[a], order[b]), max(order[a], order[b]))]]) for a, b in pr)
    return f"Q{n}|{D}|" + ",".join(map(str, vals))


def perm_orbit_size(n, D, nums) -> int:
    g, colors = _graph(n, D, nums)
    return math.factorial(n) // g.count_automorphisms(color=colors)


def normalise_sum(n, D, nums):
    """Scale a nonzero nonnegative point to sum = 1; returns (D', nums')."""
    s = sum(int(v) for v in nums)
    g = math.gcd(s, *[int(v) for v in nums])
    return s // g, tuple(int(v) // g for v in nums)


def is_extreme_ray(n, D, nums) -> bool:
    """Exact: nums/D (nonzero) spans an extreme ray of MET_n: feasible for all triangle rows and the tight triangle rows
    have rank C(n,2) - 1."""
    from .dsl.prims import certified_rank_is
    Q = q_polytope(n)
    A = Q.A[:-2]
    v = np.asarray(nums, dtype=np.int64)
    s = A @ v
    if (s > 0).any() or not v.any():
        return False
    T = np.nonzero(s == 0)[0]
    return len(T) >= Q.m - 1 and bool(certified_rank_is(A[T], Q.m - 1))
