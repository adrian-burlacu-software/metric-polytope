"""Fast engine for the block / fractal decomposition (spec: rules/blocks.mpr; equality tested in tests/test_blocks.py).

A point x (integer matrix over denominator D) splits by a node subset T ∋ node 0 (proper) into A = x|T, B = x|T̄,
middle M = x[T, T̄]. A middle M (r × c) bi-splits by R ⊆ rows (∋ row 0, proper), C ⊆ cols (proper, nonempty) into
M[R,C], M[R,C̄], M[R̄,C], M[R̄,C̄]; the diagonal pair recurses, the off-diagonal pair is the middle's middle.

Class levels (all switching-invariant):
  0 constant up to flips   1 twin (point middles only)   2 two-valued up to complement   3 any
decomposable(x, X, bv): a full tree exists in which every middle node has level <= X (bv: blocks are vertices).
Split preference: most balanced first, then lexicographic (deterministic).
"""
from __future__ import annotations

import itertools
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import numpy as np

from . import core, group
from .core import Point


# ----------------------------------------------------------------- matrices

def matrix(x: Point) -> np.ndarray:
    M = np.zeros((x.n, x.n), dtype=np.int64)
    for v, (i, j) in zip(x.nums, core.pairs(x.n)):
        M[i, j] = M[j, i] = v
    return M


def sub_point(Mx: np.ndarray, D: int, T) -> Point:
    T = list(T)
    return Point.make(len(T), D, [int(Mx[T[a], T[b]]) for a in range(len(T)) for b in range(a + 1, len(T))])


# ----------------------------------------------------------------- class levels

def is_const_up_to_flips(M: np.ndarray, D: int) -> bool:
    r, c = M.shape
    if r == 0 or c == 0:
        return True
    c0 = int(M[0, 0])
    for cv in {c0, D - c0}:
        P = M == cv
        if not (P | (M == D - cv)).all():
            continue
        if cv * 2 == D:
            return True
        if (P == (P[:, :1] ^ P[:1, :] ^ P[0, 0])).all():
            return True
    return False


def is_twin(M: np.ndarray, A: np.ndarray, D: int) -> bool:
    """every column of M equals a column of A, or its complement (A has zero diagonal)."""
    for j in range(M.shape[1]):
        col = M[:, j:j + 1]
        if not ((A == col).all(axis=0) | ((D - A) == col).all(axis=0)).any():
            return False
    return True


def is_two_valued_mod_complement(M: np.ndarray, D: int) -> bool:
    return len(set(np.minimum(M, D - M).ravel().tolist())) <= 2


def mid_level(M: np.ndarray, A: np.ndarray, D: int) -> int:
    if is_const_up_to_flips(M, D):
        return 0
    if is_twin(M, A, D):
        return 1
    if is_two_valued_mod_complement(M, D):
        return 2
    return 3


def rect_level(M: np.ndarray, D: int) -> int:
    if is_const_up_to_flips(M, D):
        return 0
    if is_two_valued_mod_complement(M, D):
        return 2
    return 3


# ----------------------------------------------------------------- split orders

@lru_cache(maxsize=None)
def point_splits(n: int) -> Tuple[Tuple[Tuple[int, ...], Tuple[int, ...]], ...]:
    out = []
    for k in range(1, n):
        for T in itertools.combinations(range(n), k):
            if 0 in T:
                U = tuple(v for v in range(n) if v not in T)
                out.append((T, U))
    out.sort(key=lambda tu: (-min(len(tu[0]), len(tu[1])), tu[0]))
    return tuple(out)


@lru_cache(maxsize=None)
def mid_splits(r: int, c: int):
    Rs = [R for k in range(1, r) for R in itertools.combinations(range(r), k) if 0 in R]
    Cs = [C for k in range(1, c) for C in itertools.combinations(range(c), k)]
    out = []
    for R in Rs:
        Rb = tuple(v for v in range(r) if v not in R)
        for C in Cs:
            Cb = tuple(v for v in range(c) if v not in C)
            out.append((R, Rb, C, Cb))
    out.sort(key=lambda t: (-(min(len(t[0]), len(t[1])) + min(len(t[2]), len(t[3]))), t[0], t[2]))
    return tuple(out)


# ----------------------------------------------------------------- engine

class Engine:
    def __init__(self):
        self._can: Dict[tuple, bool] = {}
        self._mcan: Dict[tuple, bool] = {}
        self._vtx: Dict[str, bool] = {}

    def block_vertex(self, Mx, D, T) -> bool:
        if len(T) <= 1:
            return True
        p = sub_point(Mx, D, T)
        if len(T) == 2:
            return p.D == 1
        k = p.key()
        if k not in self._vtx:
            self._vtx[k] = core.is_vertex(p)[0]
        return self._vtx[k]

    # -- middles
    def mcan(self, M: np.ndarray, D: int, X: int) -> bool:
        r, c = M.shape
        if r <= 1 or c <= 1:
            return True                              # leaf: always accepted; its level is recorded as a label
        key = (M.tobytes(), M.shape, D, X)
        if key in self._mcan:
            return self._mcan[key]
        ok = X >= 3
        if not ok:
            for R, Rb, C, Cb in mid_splits(r, c):
                M12, M21 = M[np.ix_(R, Cb)], M[np.ix_(Rb, C)]
                if rect_level(M12, D) > X or rect_level(M21, D) > X:
                    continue
                if self.mcan(M[np.ix_(R, C)], D, X) and self.mcan(M[np.ix_(Rb, Cb)], D, X):
                    ok = True
                    break
        self._mcan[key] = ok
        return ok

    def mbuild(self, M: np.ndarray, D: int, X: int) -> dict:
        r, c = M.shape
        if r <= 1 or c <= 1:
            return {"node": "mleaf", "shape": [r, c], "level": rect_level(M, D)}
        for R, Rb, C, Cb in mid_splits(r, c):
            M12, M21 = M[np.ix_(R, Cb)], M[np.ix_(Rb, C)]
            l12, l21 = rect_level(M12, D), rect_level(M21, D)
            if l12 > X or l21 > X:
                continue
            M11, M22 = M[np.ix_(R, C)], M[np.ix_(Rb, Cb)]
            if self.mcan(M11, D, X) and self.mcan(M22, D, X):
                return {"node": "msplit", "R": list(R), "C": list(C), "levels": [l12, l21],
                        "M12": M12.tolist(), "M21": M21.tolist(),
                        "children": [self.mbuild(M11, D, X), self.mbuild(M22, D, X)]}
        raise AssertionError("mbuild called on non-decomposable middle")

    # -- points
    def can(self, Mx: np.ndarray, D: int, X: int, bv: bool) -> bool:
        n = Mx.shape[0]
        if n <= 2:
            return True
        key = (group.canonical(Point.make(n, D, [int(Mx[i, j]) for (i, j) in core.pairs(n)])).key(), X, bv)
        if key in self._can:
            return self._can[key]
        ok = False
        for T, U in point_splits(n):
            if self._split_ok(Mx, D, X, bv, T, U):
                ok = True
                break
        self._can[key] = ok
        return ok

    def _split_ok(self, Mx, D, X, bv, T, U) -> bool:
        A, M, B = Mx[np.ix_(T, T)], Mx[np.ix_(T, U)], Mx[np.ix_(U, U)]
        if mid_level(M, A, D) > X:
            return False
        if bv and not (self.block_vertex(Mx, D, T) and self.block_vertex(Mx, D, U)):
            return False
        return self.can(A, D, X, bv) and self.can(B, D, X, bv) and self.mcan(M, D, X)

    def build(self, Mx: np.ndarray, D: int, X: int, bv: bool, labels=None) -> dict:
        n = Mx.shape[0]
        labels = list(range(n)) if labels is None else labels
        if n <= 2:
            return {"node": "leaf", "nodes": [l + 1 for l in labels]}
        for T, U in point_splits(n):
            if self._split_ok(Mx, D, X, bv, T, U):
                A, M, B = Mx[np.ix_(T, T)], Mx[np.ix_(T, U)], Mx[np.ix_(U, U)]
                return {"node": "split", "T": [labels[t] + 1 for t in T], "Tbar": [labels[u] + 1 for u in U],
                        "level": mid_level(M, A, D), "middle": M.tolist(), "D": D,
                        "A": self.build(A, D, X, bv, [labels[t] for t in T]),
                        "M": self.mbuild(M, D, X),
                        "B": self.build(B, D, X, bv, [labels[u] for u in U])}
        raise AssertionError("build called on non-decomposable point")

    # -- summary for one point
    def analyse(self, x: Point) -> dict:
        Mx, D, n = matrix(x), x.D, x.n
        out = {}
        for bv in (False, True):
            Xstar = next((X for X in range(4) if self.can(Mx, D, X, bv)), None)
            rec = {"Xstar": Xstar}
            if Xstar is not None:
                tree = self.build(Mx, D, Xstar, bv)
                rec["tree"] = tree
                rec["top_split"] = [len(tree["T"]), len(tree["Tbar"])]
                rec["nontrivial_top_split_exists"] = any(
                    min(len(T), len(U)) >= 2 and self._split_ok(Mx, D, Xstar, bv, T, U) for T, U in point_splits(n))
                rec["tree_depth"] = _depth(tree)
            out["vblocks" if bv else "free"] = rec
        out["top_middles"] = [{"T": [t + 1 for t in T], "level": mid_level(Mx[np.ix_(T, U)], Mx[np.ix_(T, T)], D),
                               "M": Mx[np.ix_(T, U)].tolist()} for T, U in point_splits(n)]
        out["D"] = D
        return out


def _depth(t: dict) -> int:
    if t["node"] in ("leaf", "mleaf"):
        return 0
    if t["node"] == "split":
        return 1 + max(_depth(t["A"]), _depth(t["B"]))
    return 0
