#!/usr/bin/env python3
"""Build candidates.json: breaks of the maker's iff claim, odd new rays, near-miss non-rays. All re-verified."""
import sys, json, random, importlib.util, time, warnings
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
HERE = Path(__file__).resolve().parent
MAKER = HERE.parent / "maker"
sys.path.insert(0, str(MAKER)); sys.path.insert(0, str(HERE))
import family12 as F
import networkx as nx
warnings.simplefilter("ignore")


def load(stem):
    spec = importlib.util.spec_from_file_location(stem, MAKER / f"{stem}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def E(j): return [tuple(e) for e in j["edges"]]


def lite(k, edges):
    G = nx.Graph(); G.add_nodes_from(range(k)); G.add_edges_from((a, b) for a, b, _ in edges)
    n2 = sum(1 for e in edges if e[2] == 2)
    return {"m": len(edges), "n2": n2, "bip": nx.is_bipartite(G), "girth": nx.girth(G),
            "mindeg": min(dict(G.degree()).values()), "tri": sum(nx.triangles(G).values()) // 3,
            "diam": int(F.metric(k, edges).max())}


def main():
    rng = random.Random(11)
    rays = json.loads((HERE / "new_rays.json").read_text())
    non = json.loads((HERE / "pool_nonrays.json").read_text())
    iff, suf, comb = load("04_exchange_closure_iff"), load("03_exchange_closure_sufficient"), load("08_combined_necessary")
    cands, log = [], {}
    # 1. breaks of the iff already found, plus a search among k = 9 new rays (smaller examples)
    hits = json.loads((HERE / "attack_report04_.json").read_text())[iff.NAME]["hits_rays"]
    r9 = [j for j in rays if j["k"] == 9]; rng.shuffle(r9)
    t0 = time.time(); tested9 = 0
    for j in r9:
        if time.time() - t0 > 40: break
        tested9 += 1
        if not iff.claim(9, E(j)): hits.append(j)
    log["iff_k9_tested"] = tested9
    hits.sort(key=lambda j: (j["k"], len(j["edges"])))
    for j in hits[:20]:
        assert F.check(j["k"], E(j))["ray"] and not iff.claim(j["k"], E(j))
        cands.append({"k": j["k"], "edges": j["edges"], "claim": iff.NAME,
                      "how": "ray on which the exchange closure fails; built by " + j["how"]})
    log["iff_breaks_total"] = len(hits)
    # 2. sufficient claim 03 on non-rays
    rng.shuffle(non); t0 = time.time(); n3 = 0; b3 = []
    for j in non:
        if time.time() - t0 > 30: break
        n3 += 1
        if suf.claim(j["k"], E(j)): b3.append(j)
    log["suff03_nonrays_tested"] = n3; log["suff03_breaks"] = len(b3)
    for j in b3[:10]:
        assert not F.check(j["k"], E(j))["ray"]
        cands.append({"k": j["k"], "edges": j["edges"], "claim": suf.NAME, "how": "non-ray accepted; " + j["how"]})
    # 3. near misses: non-rays that pass the combined necessary claim
    t0 = time.time(); near = []; nn = 0
    for j in non:
        if time.time() - t0 > 30 or len(near) >= 40: break
        nn += 1
        if comb.claim(j["k"], E(j)): near.append(j)
    log["near_tested"] = nn; log["near_found"] = len(near)
    near.sort(key=lambda j: -j["k"])
    for j in near[:12]:
        c = F.check(j["k"], E(j)); assert c["connected"] and c["minimal"] and not c["ray"]
        cands.append({"k": j["k"], "edges": j["edges"], "claim": "generic",
                      "how": "near miss: non-ray that passes all four necessary claims of the maker; " + j["how"]})
    # 4. odd rays
    samp = rng.sample(rays, 6000)
    fs = [(lite(j["k"], E(j)), j) for j in samp]
    picks = []
    def top(key, n, label, filt=lambda f: True):
        got = sorted([x for x in fs if filt(x[0])], key=lambda x: key(x[0], x[1]))[:n]
        for f, j in got: picks.append((label + f" {f}", j))
    top(lambda f, j: (-j["k"], f["m"]), 4, "bipartite ray", lambda f: f["bip"])
    top(lambda f, j: (-f["girth"], -j["k"], f["tri"]), 4, "girth-5 / triangle-poor ray")
    top(lambda f, j: (f["m"] - j["k"], -j["k"]), 4, "sparsest ray (edges - nodes smallest)")
    top(lambda f, j: (-f["diam"], -j["k"]), 4, "largest-diameter ray")
    top(lambda f, j: (-f["n2"] / f["m"], -j["k"]), 4, "ray with almost all edges of weight 2", lambda f: f["n2"] < f["m"])
    top(lambda f, j: (-f["mindeg"], -j["k"]), 3, "largest minimum degree ray")
    top(lambda f, j: (f["n2"] != 1, -j["k"], f["m"]), 3, "ray with exactly one weight-2 edge", lambda f: f["n2"] == 1)
    seen = set()
    for label, j in picks:
        key = (j["k"], json.dumps(j["edges"]))
        if key in seen: continue
        seen.add(key)
        assert F.check(j["k"], E(j))["ray"]
        cands.append({"k": j["k"], "edges": j["edges"], "claim": "generic", "how": f"odd new ray: {label}; built by {j['how']}"})
    cands = cands[:60]
    for c in cands:
        ch = F.check(c["k"], [tuple(e) for e in c["edges"]])
        assert ch["connected"] and ch["minimal"] and set(ch["weights"]) <= {1, 2}
        c["ray"] = ch["ray"]
    (HERE / "candidates.json").write_text(json.dumps(cands, indent=0))
    print(json.dumps(log)); print(len(cands))
    for c in cands: print(c["k"], len(c["edges"]), c["ray"], c["claim"], "|", c["how"][:150])


if __name__ == "__main__":
    main()
