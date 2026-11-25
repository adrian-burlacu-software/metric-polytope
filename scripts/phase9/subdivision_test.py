#!/usr/bin/env python3
"""Family study, first test (2026-11-25): is every weighted-graph vertex the restriction of an unweighted-graph
vertex on more nodes?

For each cut-adjacent vertex with integer weights (graph_families.analyse: minimal weighted graph of the simplest
switching), subdivide every edge of weight w into w unit edges (w - 1 new nodes): an unweighted graph G* on N nodes
whose path metric restricts to the vertex's metric on the old nodes. Test exactly whether d(G*) is an extreme ray of
the metric cone MET_N (tight triangle rows of rank C(N,2) - 1), i.e. whether (2/tau) d(G*) is a vertex of m_N adjacent
to the cut 0 (literature C10).

Usage: python -u scripts/phase9/subdivision_test.py [--alphabet 1 2] [--nmax 30] [--workers 8]
Writes results/phase9/subdivision_test.json.
"""
from __future__ import annotations
import argparse, itertools, multiprocessing as mp, sys, time
from collections import Counter
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
from metricpoly.jobs import atomic_write_json  # noqa: E402
from vertex_structure import rank_mod_p, load_set  # noqa: E402
import graph_families as gf  # noqa: E402


def path_metric(N, edges):
    INF = 10 ** 6
    d = np.full((N, N), INF, dtype=np.int64)
    np.fill_diagonal(d, 0)
    for a, b in edges:
        d[a, b] = d[b, a] = 1
    for k in range(N):
        d = np.minimum(d, d[:, k:k + 1] + d[k:k + 1, :])
    return d


def ray_rank(d):
    """Rank (mod p; a lower bound on the exact rank, equal in practice) of the tight triangle rows of the metric d."""
    N = len(d)
    idx = {}
    for i, j in itertools.combinations(range(N), 2):
        idx[(i, j)] = idx[(j, i)] = len(idx) // 2
    rows = []
    for a, b, c in itertools.combinations(range(N), 3):
        for (i, j, k) in ((a, b, c), (a, c, b), (b, c, a)):       # d_ij = d_ik + d_jk
            if d[i, j] == d[i, k] + d[j, k]:
                r = np.zeros(N * (N - 1) // 2, dtype=np.int64)
                r[idx[(i, j)]] = 1; r[idx[(i, k)]] = -1; r[idx[(j, k)]] = -1
                rows.append(r)
    if not rows:
        return 0
    return rank_mod_p(np.array(rows))


def job(args):
    key, x, nmax = args
    r = gf.analyse((key, x))
    if r is None:
        return None
    nodes = sorted({a for a, b, _ in r["edges"]} | {b for a, b, _ in r["edges"]})
    lab = {v: i for i, v in enumerate(nodes)}
    N, edges = len(nodes), []
    for a, b, w in r["edges"]:
        prev = lab[a]
        for _ in range(w - 1):
            edges.append((prev, N)); prev = N; N += 1
        edges.append((prev, lab[b]))
    out = {"key": key, "n": x.n, "D": int(x.D), "alphabet": list(r["alphabet"]), "nodes": len(nodes), "N": N}
    if N > nmax:
        out["ray"] = None
        return out
    d = path_metric(N, edges)
    # sanity: restriction to the old nodes reproduces the weighted metric (edges are geodesics)
    out["restriction_ok"] = all(int(d[lab[a], lab[b]]) == w for a, b, w in r["edges"])
    m = N * (N - 1) // 2
    rk = ray_rank(d)
    out["ray"] = bool(rk == m - 1)
    out["corank"] = int(m - rk)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alphabet", type=int, nargs="*", default=None, help="only this alphabet (default: all)")
    ap.add_argument("--nmax", type=int, default=30)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    t0 = time.time()
    pts = [(k, x, a.nmax) for k, x in load_set("m8", 0, 0) if x.D > 1]
    with mp.get_context("spawn").Pool(a.workers) as pool:
        res = [r for r in pool.imap_unordered(job, pts, chunksize=4) if r is not None]
    if a.alphabet:
        res = [r for r in res if r["alphabet"] == a.alphabet]
    summ = {}
    for n in sorted({r["n"] for r in res}):
        for al in sorted({tuple(r["alphabet"]) for r in res if r["n"] == n}):
            R = [r for r in res if r["n"] == n and tuple(r["alphabet"]) == al]
            c = Counter("too large" if r["ray"] is None else ("ray" if r["ray"] else "not a ray") for r in R)
            summ[f"n{n} {list(al)}"] = {"orbits": len(R), **c, "N": dict(sorted(Counter(r["N"] for r in R).items())),
                                         "corank_not_ray": dict(sorted(Counter(r["corank"] for r in R if r["ray"] is False).items()))}
            print(f"n = {n} alphabet {list(al)}: {len(R)} orbits; {dict(c)}; corank of failures "
                  f"{summ[f'n{n} {list(al)}']['corank_not_ray']} ({time.time() - t0:.0f} s)", flush=True)
    atomic_write_json(ROOT / "results/phase9/subdivision_test.json", {"nmax": a.nmax, "summary": summ, "rows": res})


if __name__ == "__main__":
    main()
