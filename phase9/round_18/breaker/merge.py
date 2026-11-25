#!/usr/bin/env python3
"""Merge pool_rays_*.json / pool_nonrays_*.json, dedupe up to weighted isomorphism, re-verify, print feature ranges."""
import sys, json, glob, warnings, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
import family12 as F
import networkx as nx
warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
DATA = ROOT / "results/phase9/family12"


def feats(k, edges):
    G = nx.Graph(); G.add_nodes_from(range(k))
    for a, b, w in edges: G.add_edge(a, b, w=w)
    d = F.metric(k, edges)
    deg = [G.degree(v) for v in G]
    G2 = nx.Graph([(a, b) for a, b, w in edges if w == 2])
    G1 = nx.Graph(); G1.add_nodes_from(range(k)); G1.add_edges_from([(a, b) for a, b, w in edges if w == 1])
    n2 = G2.number_of_edges()
    tw = sum(1 for a in range(k) for b in range(a + 1, k)
             if all(d[a, c] == d[b, c] for c in range(k) if c not in (a, b)))
    return {"edges": len(edges), "n2": n2, "mindeg": min(deg), "maxdeg": max(deg), "diam": int(d.max()),
            "bip": nx.is_bipartite(G), "tri": sum(nx.triangles(G).values()) // 3, "girth": nx.girth(G),
            "conn": nx.node_connectivity(G), "twinpairs": tw,
            "w1comp": nx.number_connected_components(G1), "w2acyclic": n2 == 0 or nx.is_forest(G2),
            "w2matching": n2 > 0 and max(dict(G2.degree()).values()) == 1,
            "w2maxdeg": max(dict(G2.degree()).values()) if n2 else 0}


def main():
    for kind in ("rays", "nonrays"):
        items, hows = [], {}
        for f in sorted(glob.glob(str(HERE / f"pool_{kind}_*.json"))):
            for j in json.loads(Path(f).read_text()):
                e = sorted(tuple(x) for x in j["edges"])
                items.append((j["k"], e)); hows.setdefault((j["k"], tuple(e)), j["how"])
        uniq = F.dedupe(items)
        out = []
        for k, e in uniq:
            c = F.check(k, e)
            assert c["connected"] and c["minimal"] and set(c["weights"]) <= {1, 2} and c["ray"] == (kind == "rays"), (k, e, c)
            out.append({"k": k, "edges": [list(x) for x in e], "how": hows[(k, tuple(e))]})
        name = "new_rays.json" if kind == "rays" else "pool_nonrays.json"
        (HERE / name).write_text(json.dumps(out))
        print(kind, len(items), "->", len(out), collections.Counter(j["k"] for j in out))
        for k in (9, 10, 11):
            fs = [feats(j["k"], j["edges"]) for j in out if j["k"] == k]
            if not fs: continue
            print(" k", k, {key: (min(f[key] for f in fs), max(f[key] for f in fs)) if not isinstance(fs[0][key], bool)
                            else sum(f[key] for f in fs) for key in fs[0]})
    for k in (8, 9):
        R = json.loads((DATA / f"rays_k{k}.json").read_text())
        fs = [feats(k, [tuple(x) for x in j["edges"]]) for j in R[:6000]]
        print("data k", k, {key: (min(f[key] for f in fs), max(f[key] for f in fs)) if not isinstance(fs[0][key], bool)
                            else sum(f[key] for f in fs) for key in fs[0]})


if __name__ == "__main__":
    main()
