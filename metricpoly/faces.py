"""Orbitwise enumeration of the upper face lattice of m_n (faces of small codimension).

A face F is represented by its vertex set (boolean mask over a full vertex list) and its
tight facet set T(F) = {facets containing F}; codim F = rank of the normals in T(F).
Orbit key of F = canonical form of the barycenter of its vertices: the barycenter lies in
the relative interior of F (so it determines F), and g.bary(F) = bary(g.F) because every
group element is affine. So face orbits <-> point orbits of barycenters.

Codim-(k+1) faces are generated from codim-k orbit representatives F as F ∩ f for facets
f not in T(F); every facet of F arises this way and G acts on the lattice, so expanding
representatives only is complete.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .core import Point, dim, exact_rank, ineq_matrix
from .group import canonical


@dataclass
class FaceLattice:
    n: int
    L: int                      # common denominator of vertex array
    V: np.ndarray               # (Nv, m) int numerators over L
    inc: np.ndarray = field(init=False)   # (F, Nv) bool: facet f tight at vertex v

    def __post_init__(self):
        A, b = ineq_matrix(self.n)
        self.A = A
        self.inc = (self.V @ A.T == (b * self.L)[None, :]).T

    def closure(self, mask: np.ndarray) -> np.ndarray:
        """Facets containing every vertex in mask."""
        return np.flatnonzero(self.inc[:, mask].all(axis=1))

    def face_from_facets(self, T: Sequence[int]) -> np.ndarray:
        return self.inc[list(T)].all(axis=0)

    def codim(self, T: Sequence[int]) -> int:
        return exact_rank(self.A[list(T)].tolist())

    def barycenter_key(self, mask: np.ndarray) -> Point:
        idx = np.flatnonzero(mask)
        s = self.V[idx].sum(axis=0)
        return canonical(Point.make(self.n, self.L * len(idx), s.tolist()))

    def facet_defining_all(self) -> bool:
        """Every inequality is facet-defining: affine rank of its tight vertices = m-1."""
        m = dim(self.n)
        for f in range(self.inc.shape[0]):
            W = self.V[self.inc[f]]
            H = np.hstack([W, np.full((W.shape[0], 1), self.L, dtype=np.int64)])
            if exact_rank(H.tolist()) != m:
                return False
        return True


def upper_lattice(fl: FaceLattice, max_codim: int,
                  on_level: Optional[Callable[[int, List[dict]], None]] = None,
                  start: Optional[Dict[int, List[dict]]] = None) -> Dict[int, List[dict]]:
    """Return {codim: [face rep records]} for codim 1..max_codim.

    A record: {'facets': sorted tight facet indices, 'nverts': int, 'key': canonical barycenter key}.
    `start` lets a caller resume from already-computed levels (checkpointing).
    """
    levels: Dict[int, List[dict]] = dict(start or {})
    if 1 not in levels:
        reps: Dict[str, dict] = {}
        for f in range(fl.inc.shape[0]):
            mask = fl.inc[f]
            T = fl.closure(mask)
            if fl.codim(T) != 1:
                continue
            key = fl.barycenter_key(mask).key()
            reps.setdefault(key, {"facets": T.tolist(), "nverts": int(mask.sum()), "key": key})
        levels[1] = list(reps.values())
        if on_level:
            on_level(1, levels[1])
    for k in range(2, max_codim + 1):
        if k in levels:
            continue
        reps = {}
        seen_T = set()
        for F in levels[k - 1]:
            Fmask = fl.face_from_facets(F["facets"])
            Tset = set(F["facets"])
            for f in range(fl.inc.shape[0]):
                if f in Tset:
                    continue
                mask = Fmask & fl.inc[f]
                if not mask.any():
                    continue
                T = fl.closure(mask)
                tk = tuple(T.tolist())
                if tk in seen_T:
                    continue
                seen_T.add(tk)
                if fl.codim(T) != k:
                    continue
                key = fl.barycenter_key(mask).key()
                reps.setdefault(key, {"facets": list(tk), "nverts": int(mask.sum()), "key": key})
        levels[k] = list(reps.values())
        if on_level:
            on_level(k, levels[k])
    return levels
