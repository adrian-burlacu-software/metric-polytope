#!/usr/bin/env python3
"""Family study (round 18): extreme rays of the metric cone MET_k whose minimal graph has weights in {1, 2}.

Objects: a weighted graph on nodes 0..k-1, edges [[a, b, w], ...] with integer w >= 1. Its metric d is the weighted
shortest-path metric. The graph is *minimal* if every edge is a geodesic with no node strictly between its ends and
every non-edge has a node strictly between (so the graph is the minimal graph of d, see docs/phase9_status.md §14).
It is a *ray* if in addition d spans an extreme ray of MET_k: the tight triangle equalities d_ij = d_ik + d_kj have
rank C(k,2) - 1 (exact: rank mod 2^31-1 can only undercount, and C(k,2) - 1 is the maximum).

Library functions: metric(k, edges), is_minimal(k, edges, d), is_ray(d), check(k, edges), iso_key helpers.
CLI:  python scripts/phase9/family12.py build            -> results/phase9/family12/rays_k{5..8}.json (complete)
      python scripts/phase9/family12.py check FILE.json  -> exact verdict for {"k": .., "edges": [[a,b,w],...]}
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
OUT = ROOT / "results/phase9/family12"
INF = 10 ** 6


def metric(k, edges):
    d = np.full((k, k), INF, dtype=np.int64)
    np.fill_diagonal(d, 0)
    for a, b, w in edges:
        d[a, b] = d[b, a] = min(d[a, b], w)
    for m in range(k):
        d = np.minimum(d, d[:, m:m + 1] + d[m:m + 1, :])
    return d


def minimal_edges(k, d):
    return sorted((a, b, int(d[a, b])) for a, b in itertools.combinations(range(k), 2)
                  if not any(d[a, b] == d[a, m] + d[m, b] for m in range(k) if m != a and m != b))


def is_minimal(k, edges, d=None):
    d = metric(k, edges) if d is None else d
    if (d >= INF).any():
        return False
    return sorted((min(a, b), max(a, b), int(w)) for a, b, w in edges) == minimal_edges(k, d)


def is_ray(d):
    from vertex_structure import rank_mod_p
    k = len(d)
    idx = {}
    for i, j in itertools.combinations(range(k), 2):
        idx[(i, j)] = idx[(j, i)] = len(idx) // 2
    rows = []
    for a, b, c in itertools.combinations(range(k), 3):
        for (i, j, m) in ((a, b, c), (a, c, b), (b, c, a)):
            if d[i, j] == d[i, m] + d[j, m]:
                r = np.zeros(k * (k - 1) // 2, dtype=np.int64)
                r[idx[(i, j)]] = 1; r[idx[(i, m)]] = -1; r[idx[(j, m)]] = -1
                rows.append(r)
    return bool(rows) and rank_mod_p(np.array(rows)) == k * (k - 1) // 2 - 1


def check(k, edges):
    d = metric(k, edges)
    conn = not (d >= INF).any()
    mn = conn and is_minimal(k, edges, d)
    return {"k": k, "connected": conn, "minimal": mn, "weights": sorted({int(w) for _, _, w in edges}),
            "ray": bool(mn and is_ray(d))}


def nxgraph(edges):
    import networkx as nx
    G = nx.Graph()
    for a, b, w in edges:
        G.add_edge(a, b, w=int(w))
    return G


def dedupe(items):
    """items: list of (k, edges). Unique up to weighted isomorphism."""
    import warnings
    import networkx as nx
    from networkx.algorithms.isomorphism import numerical_edge_match
    warnings.simplefilter("ignore")
    em = numerical_edge_match("w", 0)
    buckets, out = {}, []
    for k, edges in items:
        G = nxgraph(edges)
        h = (k, len(edges), nx.weisfeiler_lehman_graph_hash(G, edge_attr="w", iterations=4))
        for G2 in buckets.setdefault(h, []):
            if nx.is_isomorphic(G, G2, edge_match=em):
                break
        else:
            buckets[h].append(G)
            out.append((k, edges))
    return out


def relabel(edges):
    nodes = sorted({a for a, b, _ in edges} | {b for a, b, _ in edges})
    lab = {v: i for i, v in enumerate(nodes)}
    return len(nodes), sorted([min(lab[a], lab[b]), max(lab[a], lab[b]), int(w)] for a, b, w in edges)


def _rays_of(x):
    """All rays (weighted minimal graphs, zero-distance nodes merged) from the valid switchings of the vertex x."""
    from metricpoly import core
    from vertex_structure import full_rank
    from graph_types import tables
    import graph_families as gf
    n, D = x.n, x.D
    m = core.dim(n)
    A, sep = tables(n)
    v = np.array(x.nums, dtype=np.int64)
    out = []
    for mask in range(1 << (n - 1)):
        w = np.where(sep[mask], D - v, v)
        T = np.flatnonzero(A @ w == 0)
        if T.size >= m - 1 and full_rank(A[T], m - 1):
            _nn, edges = gf.weighted_graph(n, w)
            out.append(relabel(edges))
    return out


def build():
    import multiprocessing as mp
    from collections import Counter
    from vertex_structure import load_set
    from metricpoly.jobs import atomic_write_json
    OUT.mkdir(parents=True, exist_ok=True)
    pts = [x for _k, x in load_set("m8", 0, 0) if x.D > 1]
    with mp.get_context("spawn").Pool(8) as pool:
        allr = [r for part in pool.imap_unordered(_rays_of, pts, chunksize=4) for r in part]
    uniq = dedupe(allr)
    summary = {}
    for k in sorted({k for k, _ in uniq}):
        R = [e for kk, e in uniq if kk == k]
        al = Counter(tuple(sorted({w for _, _, w in e})) for e in R)
        f12 = [e for e in R if {w for _, _, w in e} <= {1, 2}]
        for e in f12:                                   # self-check with the library's own test
            assert check(k, e)["ray"], (k, e)
        atomic_write_json(OUT / f"rays_k{k}.json", [{"k": k, "edges": e} for e in f12])
        summary[str(k)] = {"rays_all_alphabets": len(R), "family12": len(f12),
                           "unweighted": sum(1 for e in f12 if {w for _, _, w in e} == {1}),
                           "by_alphabet": {str(list(a)): c for a, c in sorted(al.items())}}
        print(f"k = {k}: {len(R)} rays of MET_{k} up to permutation; family {{1,2}}: {len(f12)} "
              f"({summary[str(k)]['unweighted']} unweighted)", flush=True)
    atomic_write_json(OUT / "summary.json", summary)


if __name__ == "__main__":
    if sys.argv[1] == "build":
        build()
    else:
        j = json.loads(Path(sys.argv[2]).read_text())
        print(json.dumps(check(int(j["k"]), [tuple(e) for e in j["edges"]])))
