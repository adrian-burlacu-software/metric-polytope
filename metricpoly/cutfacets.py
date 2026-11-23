"""Facet-side adjacency for the cut polytope CUT_n (Track B′ of docs/roadmap_m9.md).

A facet is an integer inequality a·x <= b, valid on all 2^(n-1) cuts δ(S) (as 0/1 vectors in pair order, S ⊆ {0..n-2}),
whose tight cuts ("roots") have affine rank C(n,2) - 1. Everything here is exact (integers / gmp rationals).

  canon(n, a, b)        canonical key of the facet's class under switchings ⋊ S_n: switch the facet to the zero cut by
                        each root (giving a2·x <= 0) and take the minimum S_n-canonical form of a2 (bliss). Two facets
                        are equivalent iff their keys are equal (switching by a root, then permuting, is the general
                        group element that maps one homogeneous representative to another).
  ridges(n, a, b)       the facets of F' = conv(roots) inside aff(F), as (h0, h) with h0 + h·x >= 0 on F', = 0 on the
                        ridge (cdd gmp, V -> H; equations dropped).
  rotate(n, a, b, h0, h) the neighbouring facet G through that ridge (gift wrapping over all cuts):
                        lam = max over cuts c off F of -(h0 + h·c) / (b - a·c);   G: (lam a - h)·x <= h0 + lam b.
  expand(n, a, b)       canonical keys of all neighbours, each checked exactly to be a facet.
"""
from __future__ import annotations

import math
from fractions import Fraction
from functools import lru_cache
from typing import Dict, List, Tuple

import cdd
import cdd.gmp
import numpy as np

from . import adjdec
from .core import pairs


@lru_cache(maxsize=None)
def cut_matrix(n: int) -> Tuple[np.ndarray, Tuple[frozenset, ...]]:
    pr = pairs(n)
    rows, sets = [], []
    for bits in range(1 << (n - 1)):
        S = frozenset(i for i in range(n - 1) if bits >> i & 1)
        sets.append(S)
        rows.append([1 if ((i in S) != (j in S)) else 0 for i, j in pr])
    return np.array(rows, dtype=np.int64), tuple(sets)


def primitive(a, b) -> Tuple[Tuple[int, ...], int]:
    g = math.gcd(*[int(v) for v in a], int(b))
    return tuple(int(v) // g for v in a), int(b) // g


def roots(n: int, a, b) -> np.ndarray:
    C, _ = cut_matrix(n)
    v = C @ np.asarray(a, dtype=np.int64)
    if (v > b).any():
        raise ValueError("inequality not valid on all cuts")
    return np.nonzero(v == b)[0]


def exact_rank(M: np.ndarray) -> int:
    if len(M) == 0:
        return 0
    from .dsl.prims import certified_rank_is
    m = M.shape[1]
    for r in range(min(len(M), m), -1, -1):        # certified_rank_is is exact; scan from the top (usually 1 step)
        if certified_rank_is(M, r):
            return r
    return 0


def is_facet(n: int, a, b) -> bool:
    C, _ = cut_matrix(n)
    v = C @ np.asarray(a, dtype=np.int64)
    if (v > b).any():
        return False
    R = C[v == b]
    m = C.shape[1]
    if len(R) < m:
        return False
    from .dsl.prims import certified_rank_is
    return bool(certified_rank_is(R[1:] - R[0], m - 1))


def switch(n: int, a, b, S) -> Tuple[Tuple[int, ...], int]:
    """a·x <= b under x_e -> 1 - x_e for e in δ(S)."""
    pr = pairs(n)
    a2 = tuple((-v if ((i in S) != (j in S)) else v) for v, (i, j) in zip(a, pr))
    b2 = b - sum(v for v, (i, j) in zip(a, pr) if (i in S) != (j in S))
    return a2, b2


def sn_key(n: int, a) -> str:
    return adjdec.fix_key(n, [], (0, tuple(int(v) for v in a)))


def canon(n: int, a, b, R=None) -> str:
    _, sets = cut_matrix(n)
    if R is None:
        R = roots(n, a, b)
    best = None
    for r in R:
        a2, b2 = switch(n, a, b, sets[r])
        assert b2 == 0
        k = sn_key(n, a2)
        if best is None or k < best:
            best = k
    return best


def ridges(n: int, a, b, R=None) -> List[Tuple[int, Tuple[int, ...]]]:
    C, _ = cut_matrix(n)
    if R is None:
        R = roots(n, a, b)
    pts = C[R]
    mat = cdd.gmp.matrix_from_array([[Fraction(1)] + [Fraction(int(v)) for v in p] for p in pts],
                                    rep_type=cdd.RepType.GENERATOR)
    H = cdd.gmp.copy_inequalities(cdd.gmp.polyhedron_from_matrix(mat))
    lin = set(H.lin_set)
    out = []
    for i, row in enumerate(H.array):
        if i in lin:
            continue
        fr = [Fraction(v) for v in row]
        L = 1
        for f in fr:
            L = L * f.denominator // math.gcd(L, f.denominator)
        iv = [int(f * L) for f in fr]
        g = math.gcd(*iv)
        iv = [v // g for v in iv]
        out.append((iv[0], tuple(iv[1:])))
    return out


def rotate(n: int, a, b, h0: int, h) -> Tuple[Tuple[int, ...], int]:
    C, _ = cut_matrix(n)
    av, hv = np.asarray(a, dtype=object), np.asarray(h, dtype=object)
    sF = b - C.astype(object) @ av
    sH = h0 + C.astype(object) @ hv
    off = [i for i in range(len(C)) if sF[i] > 0]
    lam = max(Fraction(-int(sH[i]), int(sF[i])) for i in off)
    # G slack = sH + lam sF >= 0 everywhere;  G: (lam a - h)·x <= h0 + lam b
    D = lam.denominator
    aG = [lam.numerator * int(x) - D * int(y) for x, y in zip(a, h)]
    bG = D * h0 + lam.numerator * b
    return primitive(aG, bG)


def expand(n: int, a, b) -> Dict[str, Tuple[Tuple[int, ...], int]]:
    """{canonical key: representative} of all facets adjacent to a·x <= b. Raises if a rotation is not a facet."""
    R = roots(n, a, b)
    out = {}
    for h0, h in ridges(n, a, b, R):
        aG, bG = rotate(n, a, b, h0, h)
        if not is_facet(n, aG, bG):
            raise RuntimeError("rotation did not give a facet")
        out.setdefault(canon(n, aG, bG), (aG, bG))
    return out


# ------------------------------------------------------------------ symmetry-reduced expansion (degenerate facets)

def ridges_nmz(n: int, a0, threads: int = 18, budget=None, tag: str = "rid") -> List[Tuple[int, Tuple[int, ...]]]:
    """Ridges of a facet a0·x <= 0 through the zero cut, by Normaliz (support hyperplanes of the cone generated by
    the homogenised roots (c, 1)); memory-capped via adjdec._nmz_run. Returned as (h0, h): h0 + h·x >= 0."""
    C, _ = cut_matrix(n)
    R = roots(n, a0, 0)
    P = np.hstack([C[R], np.ones((len(R), 1), dtype=np.int64)])
    ctx = adjdec.Ctx(threads=threads, tag=tag)
    hyp = adjdec._nmz_run(-P, tag, threads, budget, ctx)          # support hyperplanes of cone(P)
    return [(int(r[-1]), tuple(int(v) for v in r[:-1])) for r in hyp]


def ridge_key(n: int, a0, h0: int, h) -> str:
    """Canonical key of a ridge of the facet a0·x <= 0 under G = Stab_{S_n}(a0). The ridge functional is defined
    modulo a0 (and a positive scalar); the orthogonal projection away from a0 is G-equivariant and fixes the choice."""
    av = np.asarray(a0, dtype=object)
    hv = np.asarray(h, dtype=object)
    aa, ha = int(av @ av), int(hv @ av)
    hp = [aa * int(x) - ha * int(y) for x, y in zip(h, a0)]
    g = math.gcd(aa * int(h0), *hp)
    return adjdec.fix_key(n, [tuple(int(v) for v in a0)], (aa * int(h0) // g, tuple(v // g for v in hp)))


def expand_sym(n: int, a, b, threads: int = 18, budget=None, log=None) -> Dict:
    """Expand a facet using Normaliz ridges and one rotation per Stab_{S_n}-orbit of ridges (after switching the
    facet to the zero cut). Returns {"ridges", "ridge_orbits", "nbr": {key: rep}, "s"}."""
    import time
    t = time.time()
    _, sets = cut_matrix(n)
    R = roots(n, a, b)
    a0, b0 = switch(n, a, b, sets[R[0]])
    assert b0 == 0
    rid = ridges_nmz(n, a0, threads, budget, tag=f"rid{n}_{len(R)}")
    if log:
        log(f"    {len(rid)} ridges from Normaliz ({time.time() - t:.0f} s)")
    reps = {}
    for h0, h in rid:
        reps.setdefault(ridge_key(n, a0, h0, h), (h0, h))
    if log:
        log(f"    {len(reps)} ridge orbits under Stab_Sn ({time.time() - t:.0f} s)")
    nbr = {}
    for h0, h in reps.values():
        aG, bG = rotate(n, a0, 0, h0, h)
        if not is_facet(n, aG, bG):
            raise RuntimeError("rotation did not give a facet")
        nbr.setdefault(canon(n, aG, bG), (aG, bG))
    return {"roots": len(R), "ridges": len(rid), "ridge_orbits": len(reps), "nbr": nbr, "s": round(time.time() - t, 1)}


# ------------------------------------------------------------------ recursive ridge enumeration (very degenerate facets)
#
# Dual formulation. For a facet a0·x <= 0 through the zero cut with roots R, the ridge functionals y = (h, h0) in
# R^(m+1) (h0 + h·c >= 0 on the roots) form the cone {y : -(c, 1)·y <= 0 for c in R}, whose lineality is spanned by
# (a0, 0). Adding the rows ±(a0, 0) cuts that line out:
#     K = {y : -(c,1)·y <= 0 (c in R),  ±(a0,0)·y <= 0}        pointed, dimension m, extreme rays = ridges of the facet
# (each ridge functional, projected orthogonally away from a0). K is invariant under G = Stab_{S_n}(a0), which permutes
# the roots and fixes the homogenising coordinate, so adjdec's recursive adjacency decomposition applies unchanged:
# vertices of K's section are enumerated orbit by orbit under G (exact LP start, exact steps = rotations inside the
# facet, neighbours from the tangent cones by cdd / Normaliz / recursion, Balinski stop).

def ridge_cone(n: int, a0) -> np.ndarray:
    C, _ = cut_matrix(n)
    R = roots(n, a0, 0)
    P = np.hstack([C[R], np.ones((len(R), 1), dtype=np.int64)])
    l = np.array(list(a0) + [0], dtype=np.int64)
    return np.vstack([-P, l[None, :], -l[None, :]])


def ridges_adm(n: int, a0, workers: int = 0, ckpt=None, log=print, threads: int = 1, deadline=None, star=True):
    """Orbit representatives (under Stab_{S_n}(a0)) of the ridges of a0·x <= 0, by recursive adjacency
    decomposition. Returns ([(h0, h, orbit size)], info)."""
    m = len(pairs(n))
    AT = ridge_cone(n, a0)
    F = [tuple(int(v) for v in a0)]
    if workers:
        # The zero cut is a root fixed by Stab_Sn(a0); ridges through it are those with h0 = y[m] = 0, i.e. the
        # vertices of the section on the face dual to the zero cut, so the star criterion applies with that face.
        orb, stats, info = adjdec.decompose_parallel(n, AT, F, m, workers, ckpt, log=log, deadline=deadline,
                                                     star=(lambda p: int(p[1][m]) == 0) if star else None)
    else:
        ctx = adjdec.Ctx(threads=threads, tag=f"radm{n}")
        orb = adjdec.decompose(n, AT, F, m, 0, ctx)
        stats, info = ctx.stats, {}
    out = []
    for (D, y), sz in orb.values():
        out.append((int(y[m]), tuple(int(v) for v in y[:m]), sz))
    info = dict(info, stats=stats.as_dict(), orbits=len(out), ridges=sum(s for *_, s in out))
    return out, info


def expand_adm(n: int, a, b, workers: int = 0, ckpt=None, log=None, threads: int = 1, deadline=None,
               star=True) -> Dict:
    """expand_sym with the ridges from ridges_adm instead of one Normaliz call."""
    import time
    t = time.time()
    _, sets = cut_matrix(n)
    R = roots(n, a, b)
    a0, b0 = switch(n, a, b, sets[R[0]])
    assert b0 == 0
    reps, info = ridges_adm(n, a0, workers, ckpt, log or (lambda *_: None), threads, deadline, star)
    if log:
        log(f"    {info['orbits']} ridge orbits ({info['ridges']} ridges) by adjacency decomposition "
            f"({time.time() - t:.0f} s) {info['stats']}")
    nbr = {}
    if workers:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(workers) as pool:
            for k, rep in pool.imap_unordered(_rot, [(n, tuple(a0), h0, h) for h0, h, _ in reps], chunksize=256):
                nbr.setdefault(k, rep)
    else:
        for h0, h, _ in reps:
            k, rep = _rot((n, tuple(a0), h0, h))
            nbr.setdefault(k, rep)
    if log:
        log(f"    {len(nbr)} neighbour classes ({time.time() - t:.0f} s)")
    return {"roots": len(R), "ridges": info["ridges"], "ridge_orbits": info["orbits"], "adm": info, "nbr": nbr,
            "s": round(time.time() - t, 1)}


def _rot(args):
    """Rotate facet a0·x <= 0 about ridge (h0, h); returns (canonical key, representative). Raises if not a facet."""
    n, a0, h0, h = args
    aG, bG = rotate(n, a0, 0, h0, h)
    if not is_facet(n, aG, bG):
        raise RuntimeError("rotation did not give a facet")
    return canon(n, aG, bG), (aG, bG)
