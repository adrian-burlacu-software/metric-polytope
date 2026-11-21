"""Exact points, inequalities, and the vertex test for m_n."""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Iterable, List, Sequence, Tuple

import numpy as np


# ---------------------------------------------------------------- indexing

@lru_cache(maxsize=None)
def pairs(n: int) -> Tuple[Tuple[int, int], ...]:
    """All pairs (i,j), 0<=i<j<n, in lexicographic order."""
    return tuple((i, j) for i in range(n) for j in range(i + 1, n))


@lru_cache(maxsize=None)
def pair_index(n: int) -> dict:
    return {p: k for k, p in enumerate(pairs(n))}


def pidx(n: int, i: int, j: int) -> int:
    if i > j:
        i, j = j, i
    return pair_index(n)[(i, j)]


def dim(n: int) -> int:
    return n * (n - 1) // 2


def n_from_dim(m: int) -> int:
    r = math.isqrt(1 + 8 * m)
    if r * r != 1 + 8 * m or (1 + r) % 2:
        raise ValueError(f"{m} is not C(n,2)")
    return (1 + r) // 2


# ---------------------------------------------------------------- points

@dataclass(frozen=True)
class Point:
    """Exact rational point x = nums / D, stored in lowest terms."""
    n: int
    D: int
    nums: Tuple[int, ...]

    @staticmethod
    def make(n: int, D: int, nums: Sequence[int]) -> "Point":
        nums = tuple(int(v) for v in nums)
        if len(nums) != dim(n):
            raise ValueError(f"expected {dim(n)} coordinates for n={n}, got {len(nums)}")
        if D <= 0:
            raise ValueError("denominator must be positive")
        g = math.gcd(D, *nums) if nums else D
        return Point(n, D // g, tuple(v // g for v in nums))

    @staticmethod
    def from_fractions(n: int, xs: Sequence) -> "Point":
        fr = [Fraction(x) for x in xs]
        D = 1
        for f in fr:
            D = D * f.denominator // math.gcd(D, f.denominator)
        return Point.make(n, D, [int(f * D) for f in fr])

    def fractions(self) -> List[Fraction]:
        return [Fraction(v, self.D) for v in self.nums]

    def strs(self) -> List[str]:
        return [str(f) for f in self.fractions()]

    def array(self) -> np.ndarray:
        return np.asarray(self.nums, dtype=np.int64)

    def key(self) -> str:
        return f"{self.n}|{self.D}|" + ",".join(map(str, self.nums))


# ---------------------------------------------------------------- inequalities

@dataclass(frozen=True)
class Inequality:
    """a . x <= b with integer a, b."""
    a: Tuple[int, ...]
    b: int
    kind: str          # 'triangle' | 'perimeter' | 'nonneg' | 'upper'
    meta: Tuple        # triangle: (i,j,k) meaning x_ij <= x_ik + x_jk ; perimeter: (i,j,k)


@lru_cache(maxsize=None)
def metric_inequalities(n: int, families: Tuple[str, ...] = ("triangle", "perimeter")) -> Tuple[Inequality, ...]:
    """Triangle and perimeter inequalities of m_n (and optionally nonneg/upper).

    Order: for each triple i<j<k (lex): tri(ij), tri(ik), tri(jk), perimeter.
    tri(ij) is x_ij - x_ik - x_jk <= 0.
    """
    allowed = {"triangle", "perimeter", "nonneg", "upper"}
    bad = set(families) - allowed
    if bad:
        raise ValueError(f"unknown families {bad}")
    m = dim(n)
    out: List[Inequality] = []
    for i, j, k in itertools.combinations(range(n), 3):
        e_ij, e_ik, e_jk = pidx(n, i, j), pidx(n, i, k), pidx(n, j, k)
        if "triangle" in families:
            for top, o1, o2, lab in ((e_ij, e_ik, e_jk, (i, j, k)),
                                     (e_ik, e_ij, e_jk, (i, k, j)),
                                     (e_jk, e_ij, e_ik, (j, k, i))):
                a = [0] * m
                a[top], a[o1], a[o2] = 1, -1, -1
                out.append(Inequality(tuple(a), 0, "triangle", lab))
        if "perimeter" in families:
            a = [0] * m
            a[e_ij] = a[e_ik] = a[e_jk] = 1
            out.append(Inequality(tuple(a), 2, "perimeter", (i, j, k)))
    for e in range(m):
        if "nonneg" in families:
            a = [0] * m; a[e] = -1
            out.append(Inequality(tuple(a), 0, "nonneg", pairs(n)[e]))
        if "upper" in families:
            a = [0] * m; a[e] = 1
            out.append(Inequality(tuple(a), 1, "upper", pairs(n)[e]))
    return tuple(out)


@lru_cache(maxsize=None)
def ineq_matrix(n: int, families: Tuple[str, ...] = ("triangle", "perimeter")) -> Tuple[np.ndarray, np.ndarray]:
    ineqs = metric_inequalities(n, families)
    A = np.array([q.a for q in ineqs], dtype=np.int64)
    b = np.array([q.b for q in ineqs], dtype=np.int64)
    A.setflags(write=False); b.setflags(write=False)
    return A, b


def slacks(p: Point) -> np.ndarray:
    """D*(b - A x) as exact integers (>=0 iff feasible)."""
    A, b = ineq_matrix(p.n)
    return b * p.D - A @ p.array()


def tight_set(p: Point) -> np.ndarray:
    return np.flatnonzero(slacks(p) == 0)


def is_feasible(p: Point) -> bool:
    return bool((slacks(p) >= 0).all())


# ---------------------------------------------------------------- exact rank

def exact_rank(rows: Iterable[Sequence[int]]) -> int:
    """Rank of an integer matrix, exact (fraction-free Gaussian elimination)."""
    M = [list(map(int, r)) for r in rows]
    if not M:
        return 0
    ncols = len(M[0])
    rank = 0
    r0 = 0
    for c in range(ncols):
        piv = next((r for r in range(r0, len(M)) if M[r][c] != 0), None)
        if piv is None:
            continue
        M[r0], M[piv] = M[piv], M[r0]
        pr = M[r0]
        pv = pr[c]
        for r in range(r0 + 1, len(M)):
            row = M[r]
            f = row[c]
            if f:
                M[r] = [pv * row[t] - f * pr[t] for t in range(ncols)]
                g = math.gcd(*M[r])
                if g > 1:
                    M[r] = [v // g for v in M[r]]
        r0 += 1
        rank += 1
        if r0 == len(M):
            break
    return rank


def is_vertex(p: Point) -> Tuple[bool, str]:
    """Vertex test: feasible AND tight inequalities have full rank C(n,2)."""
    s = slacks(p)
    if (s < 0).any():
        return False, f"infeasible: violates {int((s < 0).sum())} inequalities"
    A, _ = ineq_matrix(p.n)
    T = np.flatnonzero(s == 0)
    r = exact_rank(A[T].tolist())
    if r != dim(p.n):
        return False, f"tight rank {r} < {dim(p.n)}"
    return True, f"tight={len(T)} rank={r}"


def common_denominator_array(points: Sequence[Point]) -> Tuple[int, np.ndarray]:
    """Stack points as integer numerators over one common denominator L."""
    L = 1
    for p in points:
        L = L * p.D // math.gcd(L, p.D)
    arr = np.array([[v * (L // p.D) for v in p.nums] for p in points], dtype=np.int64)
    return L, arr
