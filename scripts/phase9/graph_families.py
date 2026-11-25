#!/usr/bin/env python3
"""Do parametrised weights collapse the weight patterns of §14 into few families? (2026-11-25)

For each cut-adjacent vertex, the minimal weighted graph of the switching chosen as in graph_types.py. Two checks:
 (a) alphabet shape: share of alphabets (and of orbits) that are integer intervals {a..b}, and that start at 1;
 (b) does the unweighted graph determine the weights: isomorphism classes of the unweighted minimal graphs
     (networkx, WL hash buckets then exact isomorphism), orbits per class, and for classes carrying several orbits
     how many different weightings (weighted isomorphism classes) and alphabets they carry.
Caveat: one switching per orbit is used (the one with the simplest alphabet), so multiplicities are for that choice.

Usage: python -u scripts/phase9/graph_families.py [--m9 20000] [--workers 16]
Writes results/phase9/graph_families.json.
"""
from __future__ import annotations
import argparse, itertools, math, multiprocessing as mp, sys, time
from collections import Counter, defaultdict
from functools import reduce
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
from metricpoly import core  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402
from vertex_structure import full_rank, load_set  # noqa: E402
from graph_types import tables  # noqa: E402


def weighted_graph(n, w):
    g = reduce(math.gcd, [int(t) for t in w])
    d = {}
    for (i, j), t in zip(core.pairs(n), w):
        d[(i, j)] = d[(j, i)] = int(t) // g
    rep = list(range(n))
    for i in range(n):
        for j in range(i):
            if d[(i, j)] == 0:
                rep[i] = rep[j]
                break
    nodes = sorted(set(rep))
    edges = [(a, b, d[(a, b)]) for a, b in itertools.combinations(nodes, 2)
             if not any(d[(a, b)] == d[(a, k)] + d[(k, b)] for k in nodes if k != a and k != b)]
    return len(nodes), edges


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
            nn, edges = weighted_graph(n, w)
            alpha = tuple(sorted({e[2] for e in edges}))
            cand = ((len(alpha), alpha[-1] if alpha else 0, alpha, len(edges), tuple(sorted(e[2] for e in edges))), nn, edges)
            if best is None or cand[0] < best[0]:
                best = cand
    if best is None:
        return None
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from({a for a, b, _ in best[2]} | {b for a, b, _ in best[2]})
    for a, b, wt in best[2]:
        G.add_edge(a, b, w=wt)
    return {"n": n, "D": int(D), "alphabet": best[0][2], "nodes": best[1], "edges": best[2],
            "h": nx.weisfeiler_lehman_graph_hash(G, iterations=4), "hw": nx.weisfeiler_lehman_graph_hash(G, edge_attr="w", iterations=4)}


def classes(rows):
    """Exact isomorphism classes of the unweighted graphs; per class the weighted classes."""
    import networkx as nx
    from networkx.algorithms.isomorphism import numerical_edge_match
    def build(r):
        G = nx.Graph()
        for a, b, wt in r["edges"]:
            G.add_edge(a, b, w=wt)
        return G
    buckets = defaultdict(list)
    for r in rows:
        buckets[(r["nodes"], len(r["edges"]), r["h"])].append(r)
    out = []                                   # list of classes; class = list of weighted classes; each = list of rows
    em = numerical_edge_match("w", 0)
    done, t0 = 0, time.time()
    for rs in buckets.values():
        cls = []                               # [(G0, {hw: [(Gw, [rows])]})]; weighted classes indexed by their hash
        for r in rs:
            G = build(r)
            hit = False
            for _G0, wcls in cls:              # a weighted isomorphism settles both questions at once
                for Gw, lst in wcls.get(r["hw"], ()):
                    if nx.is_isomorphic(Gw, G, edge_match=em):
                        lst.append(r)
                        hit = True
                        break
                if hit:
                    break
            if not hit:
                for G0, wcls in cls:
                    if nx.is_isomorphic(G0, G):
                        wcls.setdefault(r["hw"], []).append((G, [r]))
                        break
                else:
                    cls.append((G, {r["hw"]: [(G, [r])]}))
            done += 1
            if done % 100000 == 0:
                print(f"    classes: {done} of {len(rows)} rows ({time.time() - t0:.0f} s)", flush=True)
        out += [[lst for ws in wcls.values() for _, lst in ws] for _, wcls in cls]
    return out


def run_all9(a, t0):
    """Full m_9 list in resumable chunks (checkpoints/phase9/gfam9/chunk_NNNNNNN.json); stop with a .halt file there."""
    import json
    ck = ROOT / "checkpoints/phase9/gfam9"
    ck.mkdir(parents=True, exist_ok=True)
    d = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
    c = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
    N = len(d)
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for lo in range(0, N, a.chunk):
            f = ck / f"chunk_{lo:07d}.json"
            if f.exists():
                continue
            if (ck / ".halt").exists():
                print("halt file found, stopping", flush=True)
                return None
            pts = [(i, Point.make(9, int(d[i]), [int(t) for t in c[i]])) for i in range(lo, min(N, lo + a.chunk))
                   if d[i] > 1]
            rows, notray = [], []
            for (i, _x), r in zip(pts, pool.imap(analyse, pts, chunksize=32)):
                if r is None:
                    notray.append(i)
                else:
                    r["i"] = i
                    r["alphabet"] = list(r["alphabet"])
                    rows.append(r)
            atomic_write_json(f, {"lo": lo, "rows": rows, "not_cut_adjacent": notray})
            print(f"  chunk {lo}: {len(rows)} rows, {len(notray)} not cut-adjacent ({time.time() - t0:.0f} s)", flush=True)
    res, notray = [], 0
    for f in sorted(ck.glob("chunk_*.json")):
        j = json.loads(f.read_text())
        notray += len(j["not_cut_adjacent"])
        for r in j["rows"]:
            r["alphabet"] = tuple(r["alphabet"])
            r["edges"] = [tuple(e) for e in r["edges"]]
            res.append(r)
    return res, notray


def is_interval(al):
    return list(al) == list(range(al[0], al[-1] + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m9", type=int, default=20000)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--seed", type=int, default=20261125)
    ap.add_argument("--all9", action="store_true", help="full m_9 list, resumable chunks")
    ap.add_argument("--chunk", type=int, default=50000)
    a = ap.parse_args()
    t0 = time.time()
    if a.all9:
        got = run_all9(a, t0)
        if got is None:
            return
        res9, notray = got
        print(f"{len(res9)} cut-adjacent m_9 orbits loaded, {notray} not cut-adjacent ({time.time() - t0:.0f} s)", flush=True)
        report(res9, {"set": "deza9all", "not_cut_adjacent": notray}, "graph_families_m9all.json", t0)
        # the two simplest families, for the family study (alphabet {1} and {1, 2})
        fam = [{"i": r["i"], "D": r["D"], "alphabet": list(r["alphabet"]), "nodes": r["nodes"], "edges": r["edges"]}
               for r in res9 if r["alphabet"] in ((1,), (1, 2))]
        atomic_write_json(ROOT / "results/phase9/graph_family_12_m9.json", fam)
        print(f"{len(fam)} orbits with alphabet [1] or [1, 2] saved", flush=True)
        return
    pts = load_set("m8", 0, 0)
    d = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
    c = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
    idx = np.sort(np.random.default_rng(a.seed).choice(len(d), size=min(a.m9, len(d)), replace=False))
    pts += [(f"n9:{i}", Point.make(9, int(d[i]), [int(t) for t in c[i]])) for i in idx]
    pts = [(k, x) for k, x in pts if x.D > 1]
    with mp.get_context("spawn").Pool(a.workers) as pool:
        res = [r for r in pool.imap_unordered(analyse, pts, chunksize=16) if r is not None]
    print(f"{len(res)} cut-adjacent vertices analysed ({time.time() - t0:.0f} s)", flush=True)
    report(res, {"m9_sample": a.m9}, "graph_families.json", t0)


def report(res, head, name, t0):
    out = dict(head, per_n={})
    for n in sorted({r["n"] for r in res}):
        R = [r for r in res if r["n"] == n]
        al = Counter(r["alphabet"] for r in R)
        iv = [k for k in al if is_interval(k)]
        cl = classes(R)
        sizes = Counter(sum(len(l) for l in c_) for c_ in cl)          # orbits per unweighted graph
        wper = Counter(len(c_) for c_ in cl)                           # weightings per unweighted graph
        multi = [c_ for c_ in cl if len(c_) > 1]
        o = {"vertices": len(R), "alphabets": len(al), "interval_alphabets": len(iv),
             "orbits_with_interval_alphabet": round(sum(al[k] for k in iv) / len(R), 4),
             "orbits_with_alphabet_from_1": round(sum(v for k, v in al.items() if k[0] == 1) / len(R), 4),
             "interval_ranges": sorted({(k[0], k[-1]) for k in iv}),
             "unweighted_graphs": len(cl), "weighted_graphs": sum(len(c_) for c_ in cl),
             "orbits_per_unweighted_graph": dict(sorted(sizes.items())),
             "weightings_per_unweighted_graph": dict(sorted(wper.items())),
             "orbits_in_graphs_with_several_weightings": sum(sum(len(l) for l in c_) for c_ in multi),
             "example_multi": [{"edges": len(c_[0][0]["edges"]), "nodes": c_[0][0]["nodes"],
                                "alphabets": sorted({tuple(l[0]["alphabet"]) for l in c_})} for c_ in
                               sorted(multi, key=len, reverse=True)[:5]]}
        out["per_n"][str(n)] = o
        print(f"n = {n}: {len(R)} vertices; alphabets {len(al)} ({len(iv)} intervals, {o['orbits_with_interval_alphabet']} of orbits); "
              f"unweighted graphs {len(cl)}, weighted {o['weighted_graphs']}; weightings per graph {o['weightings_per_unweighted_graph']} "
              f"({time.time() - t0:.0f} s)", flush=True)
    out["seconds"] = round(time.time() - t0, 1)
    atomic_write_json(ROOT / "results/phase9" / name, out)


if __name__ == "__main__":
    main()
