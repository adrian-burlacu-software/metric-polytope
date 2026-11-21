"""Level-2 extensions used by the Phase 7 ledger rules (all tested against the Phase 4c/6 scripts' results).

middle-types x      : canonical types of every cross block x[T, U] (T, U disjoint, nonempty)   (metricpoly/middles.py)
type-set L          : union of middle-types over a list of points (a frozenset of type keys)
type-constant? k    : type k is constant up to sign flips
type-one-step? k    : type k is one bi-split from smaller types with constant-up-to-flips off-diagonal blocks
derivable? x detour : x has finite derivation depth from the uniform base pieces with all moves (lift, radial 1–3,
                      uncapped gluing) — the scripts/detour_depth2.py DP; detour = non-vertex intermediates allowed
"""
from __future__ import annotations

import itertools
import math
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

from ... import blocks, middles
from ..registry import primitive


def _pairs(n):
    for kt in range(1, n):
        for T in itertools.combinations(range(n), kt):
            rest = [v for v in range(n) if v not in T]
            for ku in range(1, len(rest) + 1):
                for U in itertools.combinations(rest, ku):
                    if T[0] < U[0]:
                        yield T, U


@lru_cache(maxsize=50_000)
def _types(x):
    Mx = blocks.matrix(x)
    return frozenset(middles.canonical_type(Mx[np.ix_(T, U)], x.D) for T, U in _pairs(x.n))


@primitive("middle-types", 1, "Point -> List<Str>", "types({0})", r"\mathrm{{types}}({0})", equivariance="G", kernel=False)
def p_middle_types(x):
    return sorted(_types(x))


_SETS = {}


@primitive("type-set", 1, "List<Point> -> Set<Str>", "types({0})", r"\mathrm{{types}}({0})", kernel=False)
def p_type_set(L):
    k = id(L)
    if k not in _SETS:
        _SETS[k] = (frozenset().union(*[_types(x) for x in L]) if L else frozenset(), L)
    return _SETS[k][0]


@lru_cache(maxsize=None)
def _cls(k):
    M, D = middles.decode(k)
    return blocks.is_const_up_to_flips(M, D), middles.one_step_expressible(M, D)


@primitive("type-constant?", 1, "Str -> Bool", "const({0})", r"\mathrm{{const}}({0})", kernel=False)
def p_type_constant(k):
    return _cls(k)[0]


@primitive("type-one-step?", 1, "Str -> Bool", "step({0})", r"\mathrm{{step}}({0})", kernel=False)
def p_type_one_step(k):
    return _cls(k)[1]


_DP = {}


@primitive("derivable?", 2, "Point Bool -> Bool", "der_{1}({0})", r"\mathrm{{der}}_{{{1}}}({0})",
           equivariance="G", kernel=False, needs_interp=True)
def p_derivable(interp, x, detour):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
    import detour_depth2 as d2
    key = bool(detour)
    if key not in _DP:
        if "base" not in _DP:
            _DP["base"] = d2.base_keys(interp, d2.UNIFORM, 8)
        _DP[key] = d2.DP(_DP["base"], vertex_mode=not key)
    d, _ = _DP[key].point_depth(x)
    return d != math.inf


@primitive("subsets-of", 1, "Nodes -> List<Nodes>", "2^{0}", r"2^{{{0}}}", kernel=False)
def p_subsets_of(S):
    S = sorted(S)
    return [frozenset(c) for r in range(len(S) + 1) for c in itertools.combinations(S, r)]


@primitive("lcm", (1, None), "Nat... -> Nat", "lcm({0})", r"\mathrm{{lcm}}({0})", kernel=False)
def p_lcm(*xs):
    return math.lcm(*[int(v) for v in xs])
