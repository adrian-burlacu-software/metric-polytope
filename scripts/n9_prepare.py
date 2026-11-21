#!/usr/bin/env python3
"""Prepare the n = 9 base set (parallel, checkpointed):
 1. all non-isomorphic graphs on 9 nodes (extend each 8-node graph by a node with every neighbour set; exact dedupe
    with degree-sequence + WL-hash buckets and nx.is_isomorphic); checked against OEIS A000088 / A001349
    (274,668 graphs, 261,080 connected); cached in data/generated/graphs9.json
 2. canonical keys of the UNIFORM base pieces for n <= 9 (graph metrics of all connected graphs, cuts, anticuts,
    complete multipartite ± edge, Avis paths, tree suspensions); cached in results/n9/base_keys.json
Usage: python -u scripts/n9_prepare.py [--workers 19]
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

GRAPHS9 = ROOT / "data" / "generated" / "graphs9.json"
BASE = ROOT / "results" / "n9" / "base_keys.json"
EXPECTED9 = (274668, 261080)


def _extend_chunk(edge_lists):
    import networkx as nx
    buckets = {}
    for E in edge_lists:
        g = nx.Graph()
        g.add_nodes_from(range(8))
        g.add_edges_from(E)
        for mask in range(1 << 8):
            h = nx.Graph(g)
            h.add_node(8)
            h.add_edges_from((8, j) for j in range(8) if (mask >> j) & 1)
            key = (tuple(sorted(d for _, d in h.degree())), nx.weisfeiler_lehman_graph_hash(h, iterations=3))
            lst = buckets.setdefault(key, [])
            if not any(nx.is_isomorphic(h, o) for o in lst):
                lst.append(h)
    return {k: [sorted(h.edges()) for h in v] for k, v in buckets.items()}


def _dedupe_bucket(item):
    import networkx as nx
    key, lists = item
    reps = []
    for E in lists:
        h = nx.Graph()
        h.add_nodes_from(range(9))
        h.add_edges_from(E)
        if not any(nx.is_isomorphic(h, o) for o in reps):
            reps.append(h)
    return [(sorted(h.edges()), nx.is_connected(h)) for h in reps]


def _graph_key(E):
    from metricpoly import group
    from metricpoly.dsl.prims import p_gmetric, p_scale, p_triameter
    from metricpoly.dsl.values import Graph
    from fractions import Fraction
    G = Graph.make(9, E)
    x = p_scale(Fraction(2, int(p_triameter(G))), p_gmetric(G))          # x_G = (2/τ) d_G
    return group.canonical(x).key()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=19)
    args = ap.parse_args()
    from metricpoly.dsl.prims import p_graphs
    t0 = time.time()
    if not GRAPHS9.exists():
        g8 = [G.sorted_edges() for G in p_graphs(8)]
        chunks = [g8[i::args.workers * 4] for i in range(args.workers * 4)]
        merged = {}
        with mp.Pool(args.workers) as pool:
            for k, part in enumerate(pool.imap_unordered(_extend_chunk, chunks), 1):
                for key, lists in part.items():
                    merged.setdefault(key, []).extend(lists)
                print(f"[graphs9] extension chunks {k}/{len(chunks)}  buckets {len(merged)}  {time.time() - t0:.0f}s",
                      flush=True)
            reps = []
            for k, part in enumerate(pool.imap_unordered(_dedupe_bucket, merged.items(), chunksize=200), 1):
                reps.extend(part)
                if k % 20000 == 0:
                    print(f"[graphs9] dedupe {k}/{len(merged)}  {time.time() - t0:.0f}s", flush=True)
        conn = sum(1 for _, c in reps if c)
        print(f"[graphs9] {len(reps)} graphs, {conn} connected (expected {EXPECTED9})", flush=True)
        if (len(reps), conn) != EXPECTED9:
            raise SystemExit("graph count mismatch -- not writing graphs9.json")
        from metricpoly.jobs import atomic_write_text
        atomic_write_text(GRAPHS9, json.dumps([E for E, _ in reps]))
    if not BASE.exists():
        from metricpoly import group
        from metricpoly.dsl.interp import Interpreter
        from metricpoly.dsl.prims import p_connected, p_feasible
        from metricpoly.dsl.values import Graph
        sys.path.insert(0, str(ROOT / "scripts"))
        import detour_depth2 as d2
        I = Interpreter()
        for f in ("stdlib.mpr", "literature.mpr"):
            I.load_file(ROOT / "rules" / f)
        I.finalize()
        keys = {n: set(v) for n, v in d2.base_keys(I, d2.UNIFORM, 8).items()}       # n <= 8 as before
        k9 = set()
        for name in ["gen-cuts", "gen-anticuts", "gen-multipartite", "gen-tree-suspension"]:
            for p in I.run_rule(I.rules[name], 9):
                if p.n == 9 and p_feasible(p):
                    k9.add(group.canonical(p).key())
        print(f"[base] non-graphic base pieces at n=9: {len(k9)}  {time.time() - t0:.0f}s", flush=True)
        conn = [E for E in json.loads(GRAPHS9.read_text()) if p_connected(Graph.make(9, E))]
        with mp.Pool(args.workers) as pool:
            for k, key in enumerate(pool.imap_unordered(_graph_key, conn, chunksize=500), 1):
                k9.add(key)
                if k % 20000 == 0:
                    print(f"[base] graph metrics {k}/{len(conn)}  {time.time() - t0:.0f}s", flush=True)
        keys[9] = k9
        from metricpoly.jobs import atomic_write_json
        atomic_write_json(BASE, {str(n): sorted(v) for n, v in keys.items()})
        print(f"[base] n=9 base orbits: {len(k9)}; total {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
