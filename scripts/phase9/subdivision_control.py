#!/usr/bin/env python3
"""Control for subdivision_test.py (2026-11-25): do NON-vertices of m_8 also subdivide into extreme rays?

Non-vertices: for sampled m_8 vertices x, the kept fiber vertices over x restricted to nodes 0..6 (same denominator)
that are not vertices of m_8 (siblings of x in the generator of §11). For each, every switching is tried: minimal
weighted graph, full subdivision, exact extreme-ray test of the unweighted graph metric (N <= nmax). Reported:
how many non-vertices have a switching whose subdivision is an extreme ray.
Usage: python -u scripts/phase9/subdivision_control.py [--points 30] [--nmax 36] [--workers 12]
Writes results/phase9/subdivision_control.json."""
from __future__ import annotations
import argparse, multiprocessing as mp, sys, time
from collections import Counter
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
from metricpoly import core  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402
import graph_families as gf  # noqa: E402
import subdivision_test as sd  # noqa: E402
from graph_types import tables  # noqa: E402


def job(args):
    D, nums, nmax = args
    n = 8
    _A, sep = tables(n)
    v = np.array(nums, dtype=np.int64)
    tried, seen, best = 0, set(), None
    for mask in range(1 << (n - 1)):
        w = np.where(sep[mask], D - v, v)
        if not w.any():
            continue
        nn, edges = gf.weighted_graph(n, w)
        if nn < 3 or not edges:
            continue
        nodes = sorted({a for a, b, _ in edges} | {b for a, b, _ in edges})
        lab = {u: i for i, u in enumerate(nodes)}
        N, E = len(nodes), []
        for a, b, wt in edges:
            prev = lab[a]
            for _ in range(wt - 1):
                E.append((prev, N)); prev = N; N += 1
            E.append((prev, lab[b]))
        sig = (N, tuple(sorted(E)))
        if N > nmax or sig in seen:
            continue
        seen.add(sig)
        tried += 1
        d = sd.path_metric(N, E)
        cor = N * (N - 1) // 2 - sd.ray_rank(d)
        best = cor if best is None else min(best, cor)
        if cor == 1:
            break
    return {"D": D, "nums": nums, "switchings_tested": tried, "min_corank": best}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--points", type=int, default=30)
    ap.add_argument("--nmax", type=int, default=36)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    from metricpoly import deza
    from fiber_generator import fiber_vertices
    t0 = time.time()
    rng = np.random.default_rng(20261125)
    V = [x for x in deza.load_ext(8) if 3 <= x.D <= 6]
    cands = []
    for i in rng.permutation(len(V))[:60]:
        x = V[int(i)]
        sub = [x.nums[core.pidx(8, p, q)] for p, q in core.pairs(7)]
        keep, _ = fiber_vertices((7, x.D, sub))
        non = [r for r in keep if not core.is_vertex(Point.make(8, x.D, r))[0]]
        for j in rng.permutation(len(non))[:2]:
            cands.append((int(x.D), [int(t) for t in non[int(j)]], a.nmax))
    cands = cands[:a.points]
    print(f"{len(cands)} non-vertices of m_8 ({time.time() - t0:.0f} s)", flush=True)
    with mp.get_context("spawn").Pool(a.workers) as pool:
        res = list(pool.imap_unordered(job, cands, chunksize=1))
    c = Counter("ray for some switching" if r["min_corank"] == 1 else
                ("no switching tested" if r["min_corank"] is None else "never a ray") for r in res)
    print(dict(c), "min corank", dict(sorted(Counter(r["min_corank"] for r in res if r["min_corank"]).items())),
          f"({time.time() - t0:.0f} s)", flush=True)
    atomic_write_json(ROOT / "results/phase9/subdivision_control.json", {"summary": dict(c), "rows": res})


if __name__ == "__main__":
    main()
