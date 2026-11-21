"""Exact test: is the orbit of x (under switchings ⋊ S_n) the orbit of a graph metric x_G = (2/τ(G)) d_G?

Every group element is a permutation composed with a switching, and the property "y = x_G for some
connected G" is permutation-invariant. Hence the orbit of x contains some x_G iff some switching y of x
(S over nodes 1..n-1, 2^(n-1) choices) is itself a graph metric. For a candidate y: m = min(y); G = pairs
where y = m; require G connected, y = m·d_G, and m = 2/τ(G) with τ(G) = max triangle perimeter of d_G.
This replaces the table of canonical keys of all graph metrics at n = 9 (261,080 graphs), which would take ~4 h.
"""
from __future__ import annotations

import itertools
from collections import deque
from fractions import Fraction

import numpy as np

from .core import Point, pairs
from .group import switch_flips


def _bfs_all(n, adj):
    D = []
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    q.append(v)
        if min(dist) < 0:
            return None
        D.append(dist)
    return D


def is_graph_metric(y_nums, D, n) -> bool:
    """y = y_nums / D (integer numerators) is exactly x_G for a connected graph G."""
    pr = pairs(n)
    m = min(y_nums)
    if m <= 0:
        return False
    adj = [[] for _ in range(n)]
    for e, (i, j) in enumerate(pr):
        if y_nums[e] == m:
            adj[i].append(j)
            adj[j].append(i)
    dist = _bfs_all(n, adj)
    if dist is None:
        return False
    if any(y_nums[e] != m * dist[i][j] for e, (i, j) in enumerate(pr)):
        return False
    tau = max(dist[i][j] + dist[i][k] + dist[j][k] for i, j, k in itertools.combinations(range(n), 3))
    return Fraction(m, D) == Fraction(2, tau)


def orbit_is_graphic(x: Point) -> bool:
    a = np.asarray(x.nums, dtype=np.int64)
    F = switch_flips(x.n)
    for s in range(F.shape[0]):
        y = np.where(F[s], x.D - a, a)
        if is_graph_metric(y.tolist(), x.D, x.n):
            return True
    return False
