"""Level-2 extension: fast gluing with the same semantics as the DSL `glue-all-spec` / `glue` moves.

For overlap size k, the DSL spec enumerates t1 ∈ arrangements(|x1|, k), t2 ∈ arrangements(|x2|, k), S2 ∈ switchings(|x2|),
keeps the combinations whose overlap sub-points agree, and extends each glued partial point (all fiber vertices,
or the lexmin one). Here the (t2, S2) side is indexed by the ordered overlap distance pattern, so only agreeing
pairs are visited. Equality with the spec is tested in tests/test_dsl.py.
"""
from __future__ import annotations

import itertools
from fractions import Fraction

from ..prims import (_fiber_vertices, p_entry, p_glue, p_move_first, p_move_last, p_switch, p_switchings)
from ..registry import primitive


def _pattern(x, t):
    return tuple(p_entry(x, t[p], t[q]) for p in range(len(t)) for q in range(p + 1, len(t)))


@primitive("glue-extensions", 5, "Point Point Str Nat Nat -> List<Point>", "glue({0},{1})", r"\mathrm{{glue}}({0},{1})",
           equivariance="G", kernel=False, doc="all (mode 'all') or lexmin (mode 'lexmin') extensions of k-unions, k ≤ cap")
def glue_extensions(x1, x2, mode, maxn, cap):
    a, b = x1.n, x2.n
    out = []
    seen = set()
    klo = max(1, a + b - int(maxn))
    khi = min(int(cap), min(a, b) - 1)
    sw2 = [p_switch(S, x2) for S in p_switchings(b)]
    for k in range(klo, khi + 1):
        index = {}
        for t2 in itertools.permutations(range(b), k):
            for y in sw2:
                index.setdefault(_pattern(y, t2), []).append((t2, y))
        for t1 in itertools.permutations(range(a), k):
            hits = index.get(_pattern(x1, t1))
            if not hits:
                continue
            left = p_move_last(t1, x1)
            for t2, y in hits:
                P = p_glue(left, p_move_first(t2, y), k)
                if P in seen:
                    continue
                seen.add(P)
                vs = _fiber_vertices(P)
                if not vs:
                    continue
                if str(mode) == "lexmin":
                    out.append(min(vs, key=lambda z: z.fractions()))
                else:
                    out.extend(vs)
    return out
