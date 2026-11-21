#!/usr/bin/env python3
"""Test the denominator lemma: for every move, den(output) divides 2 * lcm(den(inputs)).

(1) lift  : every vertex x of m_n (Deza reps n <= 8) and every node i:      den(x) | 2 den(x \\ i)
(2) glue  : every vertex x and every split T = A ∪ B (A ∩ B ≠ ∅, both proper): den(x) | 2 lcm(den x|A, den x|B)
    (a vertex of m_n is a vertex of every fiber through it, so these are genuine move instances)
(3) lift over non-vertices (detour steps): every fiber vertex over every base piece of size 5..7
(4) radial: Λ^m(v) has coordinates v_ij, α = max(v)/2, 2α  ->  den | 2 den(v) by construction (not tested)
Then: the arithmetic closure of base denominators under {·2, lcm} vs the denominators actually reached.
"""
from __future__ import annotations

import itertools
import math
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import deza  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.dsl.interp import Interpreter  # noqa: E402
from metricpoly.dsl.prims import _fiber_vertices, p_feasible, p_lift_partial  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from detour_depth2 import UNIFORM, matrix, restrict  # noqa: E402


def divides(a, b):
    return b % a == 0


def main():
    t0 = time.time()
    res = {"lift": Counter(), "glue": Counter(), "lift_nonvertex": Counter()}
    viol = {"lift": [], "glue": [], "lift_nonvertex": []}
    for n in range(4, 9):
        for idx, x in enumerate(deza.load_ext(n), 1):
            M = matrix(x)
            for i in range(n):
                y = restrict(M, x.D, [v for v in range(n) if v != i])
                ok = divides(x.D, 2 * y.D)
                res["lift"][ok] += 1
                if not ok:
                    viol["lift"].append((n, idx, i, x.D, y.D))
            for asz in range(3, n):
                for A in itertools.combinations(range(n), asz):
                    rest = [v for v in range(n) if v not in A]
                    for kk in range(1, asz):
                        for K in itertools.combinations(A, kk):
                            B = sorted(rest + list(K))
                            if len(B) < 3:
                                continue
                            dA = restrict(M, x.D, A).D
                            dB = restrict(M, x.D, B).D
                            ok = divides(x.D, 2 * math.lcm(dA, dB))
                            res["glue"][ok] += 1
                            if not ok and len(viol["glue"]) < 20:
                                viol["glue"].append((n, idx, A, B, x.D, dA, dB))
        print(f"n={n} done ({time.time() - t0:.0f}s)", flush=True)

    I = Interpreter()
    for f in ("stdlib.mpr", "literature.mpr"):
        I.load_file(ROOT / "rules" / f)
    I.finalize()
    base_dens = Counter()
    base_pts = []
    for name in UNIFORM:
        r = I.rules[name]
        d = tuple(r.meta.get("domain", (3,)))
        for n in range(max(3, d[0]), min(8, d[1] if len(d) > 1 else 8) + 1):
            for p in I.run_rule(r, n):
                if p.n == n and p_feasible(p):
                    base_dens[p.D] += 1
                    if 5 <= n <= 7:
                        base_pts.append(p)
    seen = set()
    for v in base_pts:
        if v in seen:
            continue
        seen.add(v)
        for z in _fiber_vertices(p_lift_partial(v)):
            ok = divides(z.D, 2 * v.D)
            res["lift_nonvertex"][ok] += 1
            if not ok and len(viol["lift_nonvertex"]) < 20:
                viol["lift_nonvertex"].append((v.n, v.D, z.D, v.strs(), z.strs()))
    print("non-vertex lifts done", flush=True)

    # arithmetic closure of base denominators under doubling and lcm (bounded by the largest m_8 denominator 15·2)
    closure = set(base_dens)
    changed = True
    while changed:
        changed = False
        for a in list(closure):
            for c in [2 * a] + [math.lcm(a, b) for b in list(closure)]:
                if c <= 60 and c not in closure:
                    closure.add(c)
                    changed = True
    # a denominator d is arithmetically reachable iff d divides some element of the closure
    arith_ok = lambda d: any(c % d == 0 for c in closure)
    import json
    S = json.load(open(ROOT / "results" / "phase4c" / "detour_depth2.json", encoding="utf-8"))
    rows = S["raw"]["detour@8"]["rows"]
    explained = Counter()
    for r in rows:
        if r["depth"] is None:
            explained["unreached, arithmetic forbids" if not arith_ok(r["den"]) else "unreached, arithmetic allows"] += 1
        else:
            explained["reached (arith ok)" if arith_ok(r["den"]) else "reached BUT arithmetic forbids (lemma false!)"] += 1
    out = {"counts": {k: {str(b): c for b, c in v.items()} for k, v in res.items()},
           "violations": viol, "base_denominators": dict(sorted(base_dens.items())),
           "arith_closure": sorted(closure), "n8_explained": dict(explained), "seconds": round(time.time() - t0, 1)}
    atomic_write_json(ROOT / "results" / "phase4c" / "denominator_lemma.json", out)
    print(json.dumps({k: out[k] for k in ("counts", "base_denominators", "arith_closure", "n8_explained", "seconds")},
                     indent=1))
    print("violations:", {k: v[:5] for k, v in viol.items()})


if __name__ == "__main__":
    main()
