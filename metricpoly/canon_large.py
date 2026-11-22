"""Canonical form of a point under switchings ⋊ S_n for any n (bliss via python-igraph). Validated against the
lexmin canonical form of metricpoly.group for n <= 9 (scripts/phase9/validate_canon_large.py).

Method
  1. Switching: for a root r, the switching class contains exactly one point y with y_rj <= 1/2 for all j, except that
     entries y_rj = 1/2 leave a free choice (branch). Only roots with the fewest 1/2-entries in their row are used;
     that set is invariant, so the result is canonical.
  2. Permutation: y is encoded as a vertex-coloured graph (n point vertices of colour 0; one vertex per pair, coloured
     1 + numerator, adjacent to its two endpoints). bliss gives a canonical labelling; the point vertices sorted by
     their canonical labels give the canonical node order.
  3. Key = min over (root, tie choices) of the relabelled upper triangle: "n|D|v,v,...". Note: these keys differ from
     metricpoly.group's lexmin keys (different representative); only equality of keys is meaningful.
"""
from __future__ import annotations

import itertools

import igraph as ig
import numpy as np

from .core import Point, pairs

TIE_CAP = 1 << 12


def _matrix(x: Point) -> np.ndarray:
    M = np.zeros((x.n, x.n), dtype=np.int64)
    for v, (i, j) in zip(x.nums, pairs(x.n)):
        M[i, j] = M[j, i] = v
    return M


def _perm_canon(Y: np.ndarray, D: int) -> tuple:
    n = Y.shape[0]
    pr = pairs(n)
    edges, colors = [], [0] * n
    for e, (i, j) in enumerate(pr):
        v = n + e
        colors.append(1 + int(Y[i, j]))
        edges.append((i, v))
        edges.append((j, v))
    g = ig.Graph(n=n + len(pr), edges=edges)
    lab = g.canonical_permutation(color=colors)
    # igraph returns lab[i] = the original vertex placed at canonical position i (tested in
    # scripts/phase9/validate_canon_large.py; the docstring suggests the inverse reading, which is NOT colour-invariant)
    order = [v for v in lab if v < n]
    return tuple(int(Y[order[a], order[b]]) for a, b in pr)


def canonical_key(x: Point) -> str:
    n, D = x.n, x.D
    M = _matrix(x)
    ties = [sum(1 for j in range(n) if j != r and 2 * M[r, j] == D) for r in range(n)]
    tmin = min(ties)
    if (1 << tmin) > TIE_CAP:
        raise ValueError(f"canonical_key: {tmin} ties at 1/2 exceed the branching cap")
    best = None
    for r in range(n):
        if ties[r] != tmin:
            continue
        base_side = [0] * n
        free = []
        for j in range(n):
            if j == r:
                continue
            if 2 * M[r, j] > D:
                base_side[j] = 1
            elif 2 * M[r, j] == D:
                free.append(j)
        for bits in range(1 << len(free)):
            side = list(base_side)
            for t, j in enumerate(free):
                side[j] = (bits >> t) & 1
            s = np.array(side)
            flip = s[:, None] != s[None, :]
            Y = np.where(flip, D - M, M)
            c = _perm_canon(Y, D)
            if best is None or c < best:
                best = c
    return f"{n}|{D}|" + ",".join(map(str, best))


def random_image(x: Point, rng) -> Point:
    """A uniformly random element of switchings ⋊ S_n applied to x (any n)."""
    n, D = x.n, x.D
    M = _matrix(x)
    p = rng.permutation(n)
    P = M[np.ix_(p, p)]
    side = np.concatenate([[0], rng.integers(0, 2, n - 1)])
    flip = side[:, None] != side[None, :]
    Y = np.where(flip, D - P, P)
    return Point.make(n, D, [int(Y[i, j]) for i, j in pairs(n)])
