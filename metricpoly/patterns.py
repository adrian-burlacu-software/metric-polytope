"""Tight-constraint ("clause") patterns: the +-1 matrix view of a point.

Every facet of m_n is encoded (as in Deza's up_lattice files) by a node vector
V in {-1,0,+1}^n with exactly 3 nonzeros on a triple {a,b,c}, up to global sign:
    sum_{pairs uv in abc} V_u V_v x_uv <= 2 if all three signs agree (perimeter), else 0 (triangle).
In +-1 coordinates y = 1 - 2x this is uniformly   sum V_u V_v y_uv >= -1.

Symmetries in this view:
  permutation pi  -> permute columns (nodes);
  switching by S  -> negate columns in S;
  rows are an unordered set; each row is defined up to global sign
  (normalised here so the first nonzero entry is +1).

A cut sigma in {+-1}^n (y = sigma sigma^T) is tight on V iff (V_a s_a, V_b s_b, V_c s_c)
are Not-All-Equal: the tight pattern of a face is an NAE-3SAT formula whose solutions
are the cuts on that face.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List, Sequence, Tuple

import numpy as np

from .core import Inequality, Point, dim, metric_inequalities, pidx, tight_set

Clause = Tuple[int, ...]   # length n, entries in {-1,0,1}, 3 nonzeros, first nonzero = +1


def normalize_clause(V: Sequence[int]) -> Clause:
    V = tuple(int(v) for v in V)
    nz = [v for v in V if v]
    if len(nz) != 3 or any(abs(v) != 1 for v in nz):
        raise ValueError(f"bad clause {V}")
    return V if nz[0] > 0 else tuple(-v for v in V)


def clause_to_inequality(V: Sequence[int]) -> Tuple[Tuple[int, ...], int]:
    """(a, b) with a.x <= b, for clause V on n = len(V) nodes."""
    n = len(V)
    sup = [i for i, v in enumerate(V) if v]
    if len(sup) != 3:
        raise ValueError(f"clause needs 3 nonzeros: {V}")
    a = [0] * dim(n)
    for u in range(3):
        for w in range(u + 1, 3):
            i, j = sup[u], sup[w]
            a[pidx(n, i, j)] = V[i] * V[j]
    signs = {V[i] for i in sup}
    b = 2 if len(signs) == 1 else 0
    return tuple(a), b


def inequality_to_clause(n: int, q: Inequality) -> Clause:
    i, j, k = q.meta
    V = [0] * n
    if q.kind == "perimeter":
        V[i] = V[j] = V[k] = 1
    elif q.kind == "triangle":          # meta (i,j,k): x_ij <= x_ik + x_jk  -> V_i=V_j=+1, V_k=-1
        V[i] = V[j] = 1
        V[k] = -1
    else:
        raise ValueError(q.kind)
    return normalize_clause(V)


@lru_cache(maxsize=None)
def catalog_clauses(n: int) -> Tuple[Clause, ...]:
    return tuple(inequality_to_clause(n, q) for q in metric_inequalities(n))


@lru_cache(maxsize=None)
def clause_index(n: int) -> dict:
    return {c: k for k, c in enumerate(catalog_clauses(n))}


def pattern(p: Point) -> np.ndarray:
    """The +-1 matrix of p: one row (clause) per tight facet, columns = nodes. Rows sorted."""
    C = catalog_clauses(p.n)
    rows = sorted(C[t] for t in tight_set(p))
    return np.array(rows, dtype=np.int8).reshape(-1, p.n)


def switch_clause(V: Clause, S_nodes: Sequence[int]) -> Clause:
    W = list(V)
    for v in S_nodes:
        W[v] = -W[v]
    return normalize_clause(W)


def permute_clause(V: Clause, pi: Sequence[int]) -> Clause:
    """Node i -> pi[i]."""
    W = [0] * len(V)
    for i, v in enumerate(V):
        W[pi[i]] = v
    return normalize_clause(W)


def nae_tight(V: Clause, sigma: Sequence[int]) -> bool:
    lits = [V[i] * sigma[i] for i in range(len(V)) if V[i]]
    return not (lits[0] == lits[1] == lits[2])
