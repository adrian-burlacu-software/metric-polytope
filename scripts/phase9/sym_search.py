#!/usr/bin/env python3
"""Search for extreme rays of large locality among metrics with a cyclic symmetry.

Nodes: `fixed` fixed points and `orbits` orbits of size t under Z_t (rotation of the index). A Z_t-invariant metric
is a point of the invariant subcone of MET_n, whose coordinates are the orbits of pairs. An extreme ray of MET_n that
is invariant is an extreme ray of the invariant subcone, so: enumerate the extreme rays of the subcone exactly (cdd),
keep those with positive distances that are extreme in MET_n (exact rank test), and compute their locality.
Unlike circulants (one orbit, automatically reflection-symmetric), two or more orbits allow chiral metrics.

  python scripts/phase9/sym_search.py --fixed 1 --orbits 2 --t 5 [--smax 9]
Appends to results/phase9/sym_search.json.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import multiprocessing as mp
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

import numpy as np  # noqa: E402

import family12 as F  # noqa: E402
from locality import locality  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def setup(fixed, orbits, t):
    nodes = [("f", i, 0) for i in range(fixed)] + [("o", o, i) for o in range(orbits) for i in range(t)]
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)

    def rot(i, s):
        k, o, j = nodes[i]
        return i if k == "f" else idx[(k, o, (j + s) % t)]

    var = {}
    for a, b in itertools.combinations(range(n), 2):
        if (a, b) in var:
            continue
        v = len(set(var.values()))
        for s in range(t):
            x, y = rot(a, s), rot(b, s)
            var[(min(x, y), max(x, y))] = v
    nv = len(set(var.values()))
    rows = set()
    for a, b, c in itertools.combinations(range(n), 3):
        pa, pb, pc = var[(a, b)], var[(a, c)], var[(b, c)]
        for big, s1, s2 in ((pa, pb, pc), (pb, pa, pc), (pc, pa, pb)):       # s1 + s2 - big >= 0
            r = [0] * nv
            r[s1] += 1
            r[s2] += 1
            r[big] -= 1
            if any(r):
                rows.add(tuple(r))
    return n, var, nv, sorted(rows)


def job(args):
    n, M, smax = args
    d = np.array(M, dtype=np.int64)
    if not F.is_ray(d):
        return M, False, None
    return M, True, locality(n, [list(r) for r in M], smax=smax)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixed", type=int, default=1)
    ap.add_argument("--orbits", type=int, default=2)
    ap.add_argument("--t", type=int, default=5)
    ap.add_argument("--smax", type=int, default=0, help="stop the closure at this level (0 = n); L = None means > smax")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--budget", type=float, default=500)
    a = ap.parse_args()
    import cdd
    import cdd.gmp
    t0 = time.time()
    n, var, nv, rows = setup(a.fixed, a.orbits, a.t)
    print(f"n = {n}, {nv} pair orbits, {len(rows)} inequalities", flush=True)
    mat = cdd.gmp.matrix_from_array([[0] + list(r) for r in rows], rep_type=cdd.RepType.INEQUALITY)
    gens = cdd.gmp.copy_generators(cdd.gmp.polyhedron_from_matrix(mat))
    rays = [[Fraction(c) for c in g[1:]] for g in gens.array if g[0] == 0]
    print(f"{len(rays)} extreme rays of the invariant cone ({time.time() - t0:.0f} s)", flush=True)
    items = []
    for r in rays:
        if min(r) <= 0:
            continue
        den = 1
        for c in r:
            den = den * c.denominator // math.gcd(den, c.denominator)
        v = [int(c * den) for c in r]
        g = 0
        for c in v:
            g = math.gcd(g, c)
        v = [c // g for c in v]
        M = [[0] * n for _ in range(n)]
        for (x, y), k in var.items():
            M[x][y] = M[y][x] = v[k]
        items.append((n, tuple(tuple(row) for row in M), a.smax or n))
    print(f"{len(items)} with positive distances", flush=True)
    res, c = [], Counter()
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for M, ray, L in pool.imap_unordered(job, items, chunksize=2):
            if ray:
                c[L if L is not None else f">{a.smax}"] += 1
                res.append((L if L is not None else 10 ** 6, M))
            if time.time() - t0 > a.budget:
                print("budget reached, partial", flush=True)
                break
    res.sort(key=lambda r: -r[0])
    print(f"extreme in MET_{n}: {sum(c.values())}; locality {dict(sorted(c.items(), key=lambda kv: str(kv[0])))} ({time.time() - t0:.0f} s)", flush=True)
    for L, M in res[:3]:
        print("  L", L if L < 10 ** 6 else f">{a.smax}", "row 0:", M[0], "row", a.fixed, ":", M[a.fixed], flush=True)
    f = ROOT / "results/phase9/sym_search.json"
    old = json.loads(f.read_text()) if f.exists() else {}
    old[f"fixed{a.fixed}_orbits{a.orbits}_t{a.t}"] = {
        "n": n, "invariant_cone_rays": len(rays), "positive": len(items), "extreme_in_MET": sum(c.values()),
        "locality": {str(k): v for k, v in c.items()}, "smax": a.smax or n,
        "best": [{"L": (L if L < 10 ** 6 else None), "d": [list(r) for r in M]} for L, M in res[:5]],
        "seconds": round(time.time() - t0, 1)}
    atomic_write_json(f, old)


if __name__ == "__main__":
    main()
