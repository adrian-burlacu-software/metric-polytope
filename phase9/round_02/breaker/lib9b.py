"""Round 02 breaker helpers: exact fiber vertices (lift / glue / free LP) via cddlib gmp LP."""
from __future__ import annotations

import itertools
import math
import random
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import cdd.gmp as G

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
from metricpoly import core  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from common import verify_vertex  # noqa: E402


def tomat(x: Point):
    M = [[Fraction(0)] * x.n for _ in range(x.n)]
    for v, (i, j) in zip(x.nums, core.pairs(x.n)):
        M[i][j] = M[j][i] = Fraction(v, x.D)
    return M


def frommat(M) -> Point:
    n = len(M)
    return Point.from_fractions(n, [M[i][j] for i, j in core.pairs(n)])


def fiber_lp(M, holes, rng: random.Random, obj=None):
    """M: n x n matrix of Fractions (None on holes). Return a vertex of the fiber (as matrix) maximizing a random
    objective over the hole coordinates, or None if infeasible."""
    n = len(M)
    hidx = {h: t for t, h in enumerate(holes)}
    k = len(holes)

    def var(i, j):
        return hidx.get((min(i, j), max(i, j)))

    rows = []
    for i, j, l in itertools.combinations(range(n), 3):
        es = [(i, j), (i, l), (j, l)]
        vs = [var(*e) for e in es]
        if all(v is None for v in vs):
            continue
        # triangle: e_top - e_o1 - e_o2 <= 0 ; perimeter: sum <= 2
        for c, s in (([1, -1, -1], 0), ([-1, 1, -1], 0), ([-1, -1, 1], 0), ([1, 1, 1], 2)):
            if True:
                b = Fraction(s)
                a = [Fraction(0)] * k
                for cc, e, v in zip(c, es, vs):
                    if v is None:
                        b -= cc * M[e[0]][e[1]]
                    else:
                        a[v] += cc
                rows.append([b] + [-t for t in a])
    if obj is None:
        obj = [rng.randint(-5, 5) for _ in range(k)]
    lp = G.linprog_from_array(rows + [[0] + [Fraction(o) for o in obj]], G.LPObjType.MAX)
    G.linprog_solve(lp)
    if lp.status != G.LPStatusType.OPTIMAL:
        return None
    sol = lp.primal_solution
    N = [r[:] for r in M]
    for (i, j), t in hidx.items():
        N[i][j] = N[j][i] = Fraction(sol[t])
    return N


def lift(x: Point, rng, obj=None):
    M = tomat(x)
    n = x.n
    N = [r + [None] for r in M] + [[None] * (n + 1)]
    for i in range(n):
        N[i][i] = N[i][i] = Fraction(0)
    N[n][n] = Fraction(0)
    holes = [(i, n) for i in range(n)]
    R = fiber_lp(N, holes, rng, obj)
    return None if R is None else frommat(R)


def glue(x: Point, y: Point, k: int, rng, perm_y=None, obj=None):
    """Glue x (nodes 0..a-1) and y over K = last k nodes of x = first k nodes of y (after perm_y on y).
    Requires x|K == y|K."""
    a, b = x.n, y.n
    n = a + b - k
    Mx, My = tomat(x), tomat(y)
    if perm_y is not None:
        My = [[My[perm_y[i]][perm_y[j]] for j in range(b)] for i in range(b)]
    off = a - k
    for i in range(k):
        for j in range(k):
            if Mx[off + i][off + j] != My[i][j]:
                return None
    N = [[None] * n for _ in range(n)]
    for i in range(a):
        for j in range(a):
            N[i][j] = Mx[i][j]
    for i in range(b):
        for j in range(b):
            N[off + i][off + j] = My[i][j]
    holes = [(i, j) for i in range(off) for j in range(a, n)]
    R = fiber_lp(N, holes, rng, obj)
    return None if R is None else frommat(R)


def free_lp(n, rng, obj=None):
    N = [[Fraction(0) if i == j else None for j in range(n)] for i in range(n)]
    R = fiber_lp(N, list(core.pairs(n)), rng, obj)
    return frommat(R)


def odd_pp(D):
    from sympy import factorint
    return sorted(p ** e for p, e in factorint(int(D)).items() if p != 2)


def check(x: Point):
    return verify_vertex(x)
