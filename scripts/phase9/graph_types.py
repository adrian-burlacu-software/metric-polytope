#!/usr/bin/env python3
"""Graph types of the vertices (2026-11-25): is a bounded set of graph-indexed families enough?

A cut-adjacent vertex x has a switching x' that is a scaled extreme ray of the metric cone (literature C10). Scale x'
to coprime integers d, merge nodes at distance 0, and keep the edges ij with no node k strictly between
(d_ij = d_ik + d_kj): d is the shortest-path metric of this minimal weighted graph. The vertex's type is the weight
alphabet (sorted distinct edge weights), minimised over the valid switchings by (size, largest weight, alphabet).
Alphabet (1,) = an unweighted graph metric (the "graphic" vertices). If the alphabets stay few as n grows, a few
graph-indexed families cover everything; if they multiply, so do the rules.

Usage: python -u scripts/phase9/graph_types.py [--m9 20000] [--workers 16]
Writes results/phase9/graph_types.json.
"""
from __future__ import annotations
import argparse, itertools, json, math, multiprocessing as mp, sys, time
from collections import Counter
from functools import lru_cache, reduce
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
from metricpoly import core  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402
from vertex_structure import full_rank, load_set  # noqa: E402


@lru_cache(maxsize=None)
def tables(n):
    A, _b = core.ineq_matrix(n, ("triangle",))
    prs = core.pairs(n)
    sep = np.array([[((mask >> i) & 1) != ((mask >> j) & 1) if j < n - 1 else ((mask >> i) & 1) == 1 for i, j in prs]
                    for mask in range(1 << (n - 1))])
    return np.asarray(A, dtype=np.int64), sep


def graph_type(n, w):
    g = reduce(math.gcd, [int(t) for t in w])
    d = {}
    for (i, j), t in zip(core.pairs(n), w):
        d[(i, j)] = d[(j, i)] = int(t) // g
    rep = list(range(n))                                  # merge distance-0 classes
    for i in range(n):
        for j in range(i):
            if d[(i, j)] == 0:
                rep[i] = rep[j]
                break
    nodes = sorted(set(rep))
    edges = []
    for a, b in itertools.combinations(nodes, 2):
        if not any(d[(a, b)] == d[(a, k)] + d[(k, b)] for k in nodes if k != a and k != b):
            edges.append(d[(a, b)])
    alpha = tuple(sorted(set(edges)))
    return alpha, len(nodes), len(edges)


def analyse(args):
    key, x = args
    n, D = x.n, x.D
    m = core.dim(n)
    A, sep = tables(n)
    v = np.array(x.nums, dtype=np.int64)
    best = None
    for mask in range(1 << (n - 1)):
        w = np.where(sep[mask], D - v, v)
        T = np.flatnonzero(A @ w == 0)
        if T.size >= m - 1 and full_rank(A[T], m - 1):
            alpha, nn, ne = graph_type(n, w)
            cand = ((len(alpha), alpha[-1] if alpha else 0, alpha), nn, ne)
            if best is None or cand[0] < best[0]:
                best = cand
    if best is None:
        return {"n": n, "D": int(D), "ray": False}
    return {"n": n, "D": int(D), "ray": True, "alphabet": list(best[0][2]), "nodes": best[1], "edges": best[2]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m9", type=int, default=20000)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--seed", type=int, default=20261125)
    a = ap.parse_args()
    t0 = time.time()
    pts = load_set("m8", 0, 0)
    d = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
    c = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
    idx = np.sort(np.random.default_rng(a.seed).choice(len(d), size=min(a.m9, len(d)), replace=False))
    pts += [(f"n9:{i}", Point.make(9, int(d[i]), [int(t) for t in c[i]])) for i in idx]
    pts = [(k, x) for k, x in pts if x.D > 1]
    agg = {}
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for r in pool.imap_unordered(analyse, pts, chunksize=16):
            g = agg.setdefault(r["n"], {"R": 0, "not_ray": 0, "alpha": Counter(), "size": Counter(), "maxw": Counter(),
                                        "byD": {}})
            g["R"] += 1
            if not r["ray"]:
                g["not_ray"] += 1
                continue
            al = tuple(r["alphabet"])
            g["alpha"][al] += 1
            g["size"][len(al)] += 1
            g["maxw"][al[-1]] += 1
            g["byD"].setdefault(r["D"], Counter())[al] += 1
    out, seen = {"m9_sample": a.m9, "per_n": {}}, set()
    for n in sorted(agg):
        g = agg[n]
        new = set(g["alpha"]) - seen
        seen |= set(g["alpha"])
        rays = g["R"] - g["not_ray"]
        out["per_n"][str(n)] = {
            "vertices": g["R"], "not_cut_adjacent": g["not_ray"], "distinct_alphabets": len(g["alpha"]),
            "new_alphabets": len(new), "unweighted_share": round(g["alpha"].get((1,), 0) / max(1, rays), 4),
            "alphabet_size": dict(sorted(g["size"].items())), "largest_weight": dict(sorted(g["maxw"].items())),
            "alphabets": {str(list(k)): v for k, v in g["alpha"].most_common()},
            "alphabets_per_D": {str(D): len(cn) for D, cn in sorted(g["byD"].items())}}
        o = out["per_n"][str(n)]
        print(f"n = {n}: {g['R']} vertices ({g['not_ray']} not cut-adjacent); {len(g['alpha'])} alphabets ({len(new)} new); "
              f"unweighted {o['unweighted_share']}; alphabet size {o['alphabet_size']}; largest weight {o['largest_weight']}", flush=True)
    out["seconds"] = round(time.time() - t0, 1)
    atomic_write_json(ROOT / "results/phase9/graph_types.json", out)


if __name__ == "__main__":
    main()
