"""Exact vertex / ray enumeration with cddlib (GMP rationals). Intended for n <= 6 only."""
from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

import cdd
import cdd.gmp

from .core import Point, dim, metric_inequalities


def _h_matrix(rows_ab: List[Tuple[Tuple[int, ...], int]]):
    # cdd inequality row [b, -a] means b - a.x >= 0
    arr = [[Fraction(b)] + [Fraction(-v) for v in a] for a, b in rows_ab]
    return cdd.gmp.matrix_from_array(arr, rep_type=cdd.RepType.INEQUALITY)


def enumerate_vertices(n: int) -> List[Point]:
    """All vertices of m_n, exact."""
    rows = [(q.a, q.b) for q in metric_inequalities(n)]
    P = cdd.gmp.polyhedron_from_matrix(_h_matrix(rows))
    g = cdd.gmp.copy_generators(P)
    if g.lin_set:
        raise RuntimeError("m_n should have no lineality")
    pts = []
    for r in g.array:
        if r[0] != 1:
            raise RuntimeError(f"unexpected ray in m_{n}: {r}")
        pts.append(Point.from_fractions(n, r[1:]))
    return pts


def enumerate_cone_rays(n: int) -> List[Point]:
    """Extreme rays of the metric cone M_n (triangle inequalities only), scaled to primitive integers."""
    rows = [(q.a, 0) for q in metric_inequalities(n, ("triangle",))]
    P = cdd.gmp.polyhedron_from_matrix(_h_matrix(rows))
    g = cdd.gmp.copy_generators(P)
    if g.lin_set:
        raise RuntimeError("M_n should be pointed")
    rays = []
    for r in g.array:
        if r[0] == 0:
            p = Point.from_fractions(n, r[1:])
            rays.append(Point.make(n, 1, p.nums))      # direction only
        elif any(v != 0 for v in r[1:]):
            raise RuntimeError(f"unexpected nonzero vertex in cone: {r}")
    return rays
