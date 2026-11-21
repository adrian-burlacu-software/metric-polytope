"""Completion: which catalog inequalities are valid on P = conv(V) + cone(R) [ ∩ [0,1]^m if box ].

Exact rational arithmetic throughout. Replaces legacy/metric_vjson_to_redundancy_lp_gpu_Version4.py.

Without the box (default):  a.x <= b is valid on P  iff  max_{v in V} a.v <= b  and  a.r <= 0 for all r in R.
No LP is needed. With the box on, if every generator already lies in the box and there are no rays,
P ∩ box = P and the same formula applies; otherwise an exact LP (cddlib, GMP) is solved per
inequality, reusing one constraint matrix and only swapping the objective.

Equivariance: for g in G_n, complete(g.V) is complete(V) with inequality f relabelled g.f, and
slacks are preserved: b_{gf} - a_{gf}.(g x) = b_f - a_f.x  (tested in tests/test_completion.py).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Optional, Sequence, Tuple

import numpy as np

from .core import Inequality, Point, dim, metric_inequalities

DEFAULT_FAMILIES = ("triangle", "perimeter")


@dataclass
class IneqResult:
    index: int
    valid: bool
    max_value: Optional[Fraction]            # sup of a.x over P (None = unbounded)
    method: str                              # 'max_over_generators' | 'ray_unbounded' | 'lp_exact'
    tight: List[int] = field(default_factory=list)       # generator indices (0-based) with a.v == b
    argmax: List[int] = field(default_factory=list)      # generator indices attaining max a.v
    violating: List[int] = field(default_factory=list)   # generator indices with a.v > b


@dataclass
class Completion:
    n: int
    families: Tuple[str, ...]
    box: bool
    results: List[IneqResult]

    def valid_set(self) -> List[int]:
        return [r.index for r in self.results if r.valid]

    def tight_on_all(self) -> List[int]:
        """Inequalities valid AND tight on every vertex generator (the face's implied equalities)."""
        return [r.index for r in self.results if r.valid and r.max_value is not None
                and r.max_value == metric_inequalities(self.n, self.families)[r.index].b
                and len(r.tight) == self._nv]

    _nv: int = 0


def _stack(points: Sequence[Point]) -> Tuple[int, np.ndarray]:
    if not points:
        return 1, np.zeros((0, 0), dtype=object)
    L = 1
    for p in points:
        L = L * p.D // math.gcd(L, p.D)
    # object dtype keeps Python ints: exact for any size
    arr = np.array([[v * (L // p.D) for v in p.nums] for p in points], dtype=object)
    return L, arr


def complete(n: int, V: Sequence[Point], R: Sequence[Point] = (), families: Tuple[str, ...] = DEFAULT_FAMILIES,
             box: bool = False) -> Completion:
    if not V:
        raise ValueError("need at least one vertex generator")
    ineqs = metric_inequalities(n, tuple(families))
    A = np.array([q.a for q in ineqs], dtype=object)
    b = [q.b for q in ineqs]
    L, VA = _stack(V)
    S = A.dot(VA.T)                                    # (k, nv) exact ints, = L * a.v
    rays = list(R)
    RS = A.dot(np.array([r.nums for r in rays], dtype=object).T) if rays else None   # sign is what matters

    in_box = all(0 <= v <= p.D for p in V for v in p.nums)
    need_lp = box and (rays or not in_box)
    lp = _LPModel(n, V, rays) if need_lp else None

    out: List[IneqResult] = []
    for i in range(len(ineqs)):
        row = S[i]
        mx = max(row)
        bL = b[i] * L
        res = IneqResult(i, False, None, "max_over_generators",
                         tight=[j for j, v in enumerate(row) if v == bL],
                         argmax=[j for j, v in enumerate(row) if v == mx],
                         violating=[j for j, v in enumerate(row) if v > bL])
        if lp is not None:
            res.method = "lp_exact"
            res.max_value = lp.maximize(ineqs[i].a)
            res.valid = res.max_value is not None and res.max_value <= b[i]
            # with the box on, only in-box generators are witnesses of violation
            res.violating = [j for j in res.violating if all(0 <= v <= V[j].D for v in V[j].nums)]
        elif rays and any(v > 0 for v in RS[i]):
            res.method = "ray_unbounded"
            res.max_value = None
            res.valid = False
        else:
            res.max_value = Fraction(int(mx), L)
            res.valid = mx <= bL
        out.append(res)
    c = Completion(n, tuple(families), box, out)
    c._nv = len(V)
    return c


class _LPModel:
    """max a.x over {x = V lam + R mu, sum lam = 1, lam, mu >= 0, 0 <= x <= 1}, exact (cdd GMP).
    The constraint matrix is built once; each call only sets the objective."""

    def __init__(self, n: int, V: Sequence[Point], R: Sequence[Point]):
        import cdd
        import cdd.gmp
        self.cdd, self.gmp = cdd, cdd.gmp
        self.V = [p.fractions() for p in V]
        self.R = [p.fractions() for p in R]
        nv, nr, m = len(self.V), len(self.R), dim(n)
        z = nv + nr
        rows = []
        rows.append([Fraction(1)] + [Fraction(-1)] * nv + [Fraction(0)] * nr)      # 1 - sum lam = 0
        for i in range(z):                                                           # lam_i, mu_j >= 0
            r = [Fraction(0)] * (z + 1); r[1 + i] = Fraction(1); rows.append(r)
        for t in range(m):
            col = [v[t] for v in self.V] + [r[t] for r in self.R]
            rows.append([Fraction(0)] + col)                                         # x_t >= 0
            rows.append([Fraction(1)] + [-c for c in col])                           # 1 - x_t >= 0
        self.mat = cdd.gmp.matrix_from_array(rows, lin_set={0}, rep_type=cdd.RepType.INEQUALITY)
        self.z = z

    def maximize(self, a: Sequence[int]) -> Optional[Fraction]:
        obj = [Fraction(0)] + [sum(Fraction(ai) * v[t] for t, ai in enumerate(a) if ai) for v in self.V] \
              + [sum(Fraction(ai) * r[t] for t, ai in enumerate(a) if ai) for r in self.R]
        self.mat.obj_type = self.cdd.LPObjType.MAX
        self.mat.obj_func = obj
        lp = self.gmp.linprog_from_matrix(self.mat)
        self.gmp.linprog_solve(lp)
        st = lp.status
        if st == self.cdd.LPStatusType.OPTIMAL:
            return Fraction(lp.obj_value)
        if st in (self.cdd.LPStatusType.UNBOUNDED, self.cdd.LPStatusType.DUAL_INCONSISTENT):
            return None
        raise RuntimeError(f"LP status {st}")


# ---------------------------------------------------------------- V-JSON I/O (project format)

def to_h_json(c: Completion) -> dict:
    ineqs = metric_inequalities(c.n, c.families)
    out = {"n": c.n, "families": list(c.families), "box": c.box,
           "semantics": "redundant = valid on conv(V)+cone(R)" + (" ∩ [0,1]^m" if c.box else ""),
           "redundant": [], "not_redundant": []}
    for r in c.results:
        q = ineqs[r.index]
        obj = {"index": r.index, "kind": q.kind, "meta": [v + 1 for v in q.meta], "b": str(q.b),
               "a": [str(v) for v in q.a], "method": r.method,
               "max_value": None if r.max_value is None else str(r.max_value)}
        (out["redundant"] if r.valid else out["not_redundant"]).append(obj)
    return out


def to_v_json(c: Completion, V: Sequence[Point], R: Sequence[Point]) -> dict:
    ineqs = metric_inequalities(c.n, c.families)
    return {
        "n": c.n, "families": list(c.families), "box": c.box,
        "generators": [{"type": "vertex", "coords": p.strs()} for p in V]
                      + [{"type": "ray", "coords": p.strs()} for p in R],
        "inequality_witnesses": [{
            "index": r.index, "kind": ineqs[r.index].kind, "meta": [v + 1 for v in ineqs[r.index].meta],
            "status": "redundant" if r.valid else "not_redundant",
            "max_value": None if r.max_value is None else str(r.max_value),
            "tight_generator_indices": [j + 1 for j in r.tight],
            "max_generator_indices": [j + 1 for j in r.argmax],
            "violating_vertex_indices": [j + 1 for j in r.violating],
        } for r in c.results],
    }
