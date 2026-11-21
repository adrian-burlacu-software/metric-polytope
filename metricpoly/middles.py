"""Middle-region types: canonical form of a rectangular block x[T, U] (T, U disjoint) up to row permutations,
column permutations, sign flips (M_ij -> 1 - M_ij iff s_i xor t_j: switching seen on the block) and transpose.

Exact: orient so rows >= cols; for every flip pattern and every column permutation, sorting the rows is the optimal
row permutation for the row-major lexicographic order; the canonical form is the lexmin over all of these (and over
the transpose when r == c). Values are reduced to the block's own denominator.
"""
from __future__ import annotations

import itertools
import math
from functools import lru_cache

import numpy as np

from .blocks import is_const_up_to_flips, is_two_valued_mod_complement, rect_level


def reduce_block(M: np.ndarray, D: int):
    g = math.gcd(D, *[int(v) for v in M.ravel()]) if M.size else D
    return (M // g).astype(np.int64), D // g


@lru_cache(maxsize=None)
def _flip_masks(r: int, c: int) -> np.ndarray:
    out = []
    for s in range(1 << r):
        si = np.array([(s >> i) & 1 for i in range(r)], dtype=bool)
        for t in range(1 << (c - 1)):                          # global (s,t)->(~s,~t) is the same flip
            tj = np.array([0] + [(t >> (j - 1)) & 1 for j in range(1, c)], dtype=bool)
            out.append(si[:, None] ^ tj[None, :])
    return np.stack(out)                                         # (2^(r+c-1), r, c)


@lru_cache(maxsize=None)
def _col_perms(c: int):
    return [list(p) for p in itertools.permutations(range(c))]


def _canon_oriented(M: np.ndarray, D: int):
    r, c = M.shape
    F = _flip_masks(r, c)
    X = np.where(F, D - M[None], M[None])                        # (f, r, c)
    base = D + 1
    best = None
    for p in _col_perms(c):
        Y = X[:, :, p]
        codes = np.zeros(Y.shape[:2], dtype=np.int64)
        for j in range(c):
            codes = codes * base + Y[:, :, j]
        codes.sort(axis=1)                                       # optimal row order per flip
        # lexmin over flips
        idx = np.lexsort(codes.T[::-1])[0]
        cand = tuple(codes[idx].tolist())
        if best is None or cand < best:
            best = cand
    return best


def canonical_type(M: np.ndarray, D: int) -> str:
    M, D = reduce_block(np.asarray(M, dtype=np.int64), D)
    r, c = M.shape
    if r < c:
        M, (r, c) = M.T.copy(), (c, r)
    best = _canon_oriented(M, D)
    if r == c:
        best = min(best, _canon_oriented(M.T.copy(), D))
    return f"{r}x{c}|{D}|" + ",".join(map(str, best))


def decode(key: str):
    shape, D, codes = key.split("|")
    r, c = map(int, shape.split("x"))
    D = int(D)
    base = D + 1
    rows = []
    for code in map(int, codes.split(",")):
        row = []
        for _ in range(c):
            row.append(code % base)
            code //= base
        rows.append(row[::-1])
    return np.array(rows, dtype=np.int64), D


# ----------------------------------------------------------------- expressibility

def one_step_expressible(M: np.ndarray, D: int) -> bool:
    """Some proper bi-split (R ∋ row 0, C) has both off-diagonal blocks constant up to flips."""
    r, c = M.shape
    if r < 2 or c < 2:
        return False
    for kr in range(1, r):
        for R in itertools.combinations(range(r), kr):
            if 0 not in R:
                continue
            Rb = [i for i in range(r) if i not in R]
            for kc in range(1, c):
                for C in itertools.combinations(range(c), kc):
                    Cb = [j for j in range(c) if j not in C]
                    if is_const_up_to_flips(M[np.ix_(R, Cb)], D) and is_const_up_to_flips(M[np.ix_(Rb, C)], D):
                        return True
    return False


@lru_cache(maxsize=200_000)
def _rec(key: str, X: int) -> bool:
    M, D = decode(key)
    if is_const_up_to_flips(M, D):
        return True
    r, c = M.shape
    if r < 2 or c < 2:
        return False                                             # non-constant row/column: not built by the rule
    for kr in range(1, r):
        for R in itertools.combinations(range(r), kr):
            if 0 not in R:
                continue
            Rb = [i for i in range(r) if i not in R]
            for kc in range(1, c):
                for C in itertools.combinations(range(c), kc):
                    Cb = [j for j in range(c) if j not in C]
                    if rect_level(M[np.ix_(R, Cb)], D) > X or rect_level(M[np.ix_(Rb, C)], D) > X:
                        continue
                    if _rec(canonical_type(M[np.ix_(R, C)], D), X) and _rec(canonical_type(M[np.ix_(Rb, Cb)], D), X):
                        return True
    return False


def recursive_expressible(key: str, X: int = 0) -> bool:
    """Built entirely by the block rule: off-diagonal blocks of level <= X, leaves constant up to flips."""
    return _rec(key, X)


def classify(key: str) -> dict:
    M, D = decode(key)
    return {"const": is_const_up_to_flips(M, D), "two_valued": is_two_valued_mod_complement(M, D),
            "one_step": one_step_expressible(M, D), "recursive_const": recursive_expressible(key, 0),
            "recursive_structured": recursive_expressible(key, 2)}
