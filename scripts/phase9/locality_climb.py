#!/usr/bin/env python3
"""Search for extreme rays of large locality on more than 9 points by one-point extensions.

If d is an extreme ray of MET_k and u is a vertex of the fiber polyhedron
    F(d) = { u in R^k : |u_a - u_b| <= d_ab <= u_a + u_b for all a < b },
then (d, u) is an extreme ray of MET_{k+1}: the tight equalities of d have rank C(k,2) - 1 and the k independent
tight constraints at u involve the new coordinates with rank k. So every fiber vertex is a ray; no rank test needed
(one is done anyway as a check). Beam search: from the rays of largest locality on k points, enumerate fiber
vertices (cdd, exact), compute the locality of each extension, keep the best --beam, repeat.
Start: all rays of MET_8 with L >= 6 (from the complete list), or a JSON list given with --start.
Output results/phase9/locality_climb.json (best rays per k, with locality).
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

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

import family12 as F  # noqa: E402
from locality import locality  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def extensions(args):
    """All fiber vertices over the integer metric d (list of lists) with positive entries, as integer metrics."""
    import cdd
    import cdd.gmp
    d, cap, seed = args
    k = len(d)
    rows = []
    for a, b in itertools.combinations(range(k), 2):
        y = d[a][b]
        for ca, cb, rhs in ((1, -1, y), (-1, 1, y), (-1, -1, -y)):       # rhs + (-ca) u_a + (-cb) u_b >= 0
            v = [0] * k
            v[a], v[b] = -ca, -cb
            rows.append([rhs] + v)
    mat = cdd.gmp.matrix_from_array(rows, rep_type=cdd.RepType.INEQUALITY)
    gens = cdd.gmp.copy_generators(cdd.gmp.polyhedron_from_matrix(mat))
    verts = [[Fraction(c) for c in g[1:]] for g in gens.array if g[0] == 1]
    verts = [u for u in verts if all(c > 0 for c in u)]                  # new point distinct from the old ones
    if len(verts) > cap:
        rng = np.random.default_rng(seed)
        verts = [verts[i] for i in sorted(rng.choice(len(verts), cap, replace=False))]
    out = []
    for u in verts:
        den = 1
        for c in u:
            den = den * c.denominator // math.gcd(den, c.denominator)
        M = [[d[i][j] * den for j in range(k)] + [int(u[i] * den)] for i in range(k)]
        M.append([int(c * den) for c in u] + [0])
        g = 0
        for row in M:
            for c in row:
                g = math.gcd(g, c)
        out.append(tuple(tuple(c // g for c in row) for row in M))
    return out


def loc_job(M):
    k = len(M)
    return M, locality(k, [list(r) for r in M])


def canon_key(M):
    """Cheap invariant for de-duplication (not a canonical form): sorted row multisets."""
    return tuple(sorted(tuple(sorted(r)) for r in M))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="")
    ap.add_argument("--kmax", type=int, default=11)
    ap.add_argument("--beam", type=int, default=8)
    ap.add_argument("--cap", type=int, default=400, help="at most this many fiber vertices per base ray")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--budget", type=float, default=540)
    a = ap.parse_args()
    t0 = time.time()
    pool = mp.get_context("spawn").Pool(a.workers)
    if a.start:
        base = [tuple(tuple(r) for r in M) for M in json.loads(Path(a.start).read_text())]
        cur = pool.map(loc_job, base)
    else:
        from vertex_structure import load_set
        pts = [x for _k, x in load_set("m8", 0, 0) if x.D > 1 and x.n == 8]
        uniq = F.dedupe([r for part in pool.imap_unordered(F._rays_of, pts, chunksize=4) for r in part])
        base = [tuple(tuple(int(v) for v in row) for row in F.metric(k, e)) for k, e in uniq if k == 8]
        cur = [r for r in pool.imap_unordered(loc_job, base, chunksize=16) if r[1] >= 6]
    out = {"levels": {}}
    while True:
        k = len(cur[0][0])
        cur.sort(key=lambda r: -r[1])
        c = Counter(L for _, L in cur)
        print(f"k = {k}: {len(cur)} rays, locality {dict(sorted(c.items()))} ({time.time() - t0:.0f} s)", flush=True)
        out["levels"][str(k)] = {"rays": len(cur), "locality": {str(L): v for L, v in sorted(c.items())},
                                 "best": [{"L": L, "d": [list(r) for r in M]} for M, L in cur[:a.beam]]}
        atomic_write_json(ROOT / "results/phase9/locality_climb.json", out)
        if k >= a.kmax or time.time() - t0 > a.budget:
            break
        beam = cur[:a.beam]
        ext, seen = [], set()
        for part in pool.imap_unordered(extensions, [([list(r) for r in M], a.cap, 7 + i) for i, (M, _) in enumerate(beam)]):
            for M in part:
                key = canon_key(M)
                if key not in seen:
                    seen.add(key)
                    ext.append(M)
        print(f"  {len(ext)} distinct extensions on {k + 1} points ({time.time() - t0:.0f} s)", flush=True)
        nxt = []
        for r in pool.imap_unordered(loc_job, ext, chunksize=4):
            nxt.append(r)
            if time.time() - t0 > a.budget:
                break
        assert all(L is not None for _, L in nxt)          # every extension is a ray
        cur = nxt
    pool.terminate()
    print(f"done ({time.time() - t0:.0f} s)", flush=True)


if __name__ == "__main__":
    main()
