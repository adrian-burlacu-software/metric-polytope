#!/usr/bin/env python3
"""Prepare the n = 9 base set (parallel, checkpointed):
 1. all non-isomorphic graphs on 9 nodes (extend each 8-node graph by a node with every neighbour set; exact dedupe
    with degree-sequence + WL-hash buckets and nx.is_isomorphic); checked against OEIS A000088 / A001349
    (274,668 graphs, 261,080 connected); cached in data/generated/graphs9.json
 2. canonical keys of the UNIFORM base pieces (cuts, anticuts, complete multipartite ± edge, Avis paths, tree
    suspensions, and graph metrics for n <= 8), computed in parallel; cached in results/n9/base_keys.json.
    n = 9 graph metrics are NOT tabulated (261,080 keys, ~4 h); they are recognised by the exact test
    metricpoly.graphic.orbit_is_graphic, validated by scripts/validate_graphic_test.py
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
        # canonical keys of the UNIFORM base pieces: n <= 8 all rules (as in the n = 8 DP), n = 9 all rules except
        # gen-graphic -- n = 9 graph metrics are recognised by the exact test metricpoly.graphic.orbit_is_graphic
        from metricpoly.dsl.interp import Interpreter
        from metricpoly.dsl.prims import p_feasible
        sys.path.insert(0, str(ROOT / "scripts"))
        import detour_depth2 as d2
        I = Interpreter()
        for f in ("stdlib.mpr", "literature.mpr"):
            I.load_file(ROOT / "rules" / f)
        I.finalize()
        pts = []
        for name in d2.UNIFORM:
            r = I.rules[name]
            d = tuple(r.meta.get("domain", (3,)))
            hi = 9 if name != "gen-graphic" else 8
            for n in range(max(3, d[0]), min(hi, d[1] if len(d) > 1 else hi) + 1):
                pts.extend(p for p in I.run_rule(r, n) if p.n == n and p_feasible(p))
        uniq = sorted(set(pts), key=lambda p: (p.n, p.D, p.nums))
        print(f"[base] {len(uniq)} distinct base points generated  {time.time() - t0:.0f}s", flush=True)
        keys = {}
        with mp.Pool(args.workers) as pool:
            for k, (n, key) in enumerate(pool.imap_unordered(_canon_key, uniq, chunksize=4), 1):
                keys.setdefault(n, set()).add(key)
                if k % 2000 == 0:
                    print(f"[base] canonical {k}/{len(uniq)}  {time.time() - t0:.0f}s", flush=True)
        from metricpoly.jobs import atomic_write_json
        out = {str(n): sorted(v) for n, v in sorted(keys.items())}
        out["_note"] = "n=9 excludes graph metrics; use metricpoly.graphic.orbit_is_graphic for those"
        atomic_write_json(BASE, out)
        print(f"[base] orbits per n: {{{', '.join(f'{n}: {len(v)}' for n, v in sorted(keys.items()))}}}; "
              f"total {time.time() - t0:.0f}s", flush=True)


def _canon_key(p):
    from metricpoly import group
    return p.n, group.canonical(p).key()


if __name__ == "__main__":
    main()
