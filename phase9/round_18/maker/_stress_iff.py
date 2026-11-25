"""Stress test of the conjectural 'only if' of claim 04 beyond the data: build new {1,2}-weighted minimal graphs on
k+1 nodes by adding a node to known rays, decide ray/non-ray exactly with the library (exploration only -- the claim
itself never calls it), and compare with the closure.  Usage: _stress_iff.py K NSAMPLES SEED"""
import importlib.util, json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
import family12 as F

sp = importlib.util.spec_from_file_location("c03", HERE / "03_exchange_closure_sufficient.py")
c03 = importlib.util.module_from_spec(sp); sp.loader.exec_module(c03)
sp = importlib.util.spec_from_file_location("c08", HERE / "08_combined_necessary.py")
c08 = importlib.util.module_from_spec(sp); sp.loader.exec_module(c08)

k, n, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
rng = random.Random(seed)
base = json.loads((ROOT / f"results/phase9/family12/rays_k{k}.json").read_text())
stats = {"tried": 0, "minimal": 0, "ray": 0, "ray_closure_fail": 0, "nonray_closure_accept": 0,
         "ray_nec_fail": 0, "nonray": 0, "nonray_nec_reject": 0}
bad = []
while stats["minimal"] < n and stats["tried"] < 40 * n:
    stats["tried"] += 1
    g = rng.choice(base)
    edges = [tuple(e) for e in g["edges"]]
    mode = rng.random()
    if mode < 0.4:                                   # twin of a node (same neighbours and weights)
        v = rng.randrange(k)
        new = [((a if b == v else b), k, w) for a, b, w in edges if v in (a, b)]
    else:                                            # random neighbourhood
        nb = rng.sample(range(k), rng.randint(2, min(k, 5)))
        new = [(u, k, rng.choice((1, 1, 2))) for u in nb]
    e2 = edges + new
    d = F.metric(k + 1, e2)
    if (d >= F.INF).any() or not F.is_minimal(k + 1, e2, d):
        continue
    stats["minimal"] += 1
    ray = F.is_ray(d)
    cl = c03.claim(k + 1, e2)
    nec = c08.claim(k + 1, e2)
    if ray:
        stats["ray"] += 1
        if not cl:
            stats["ray_closure_fail"] += 1; bad.append({"k": k + 1, "edges": [list(map(int, e)) for e in e2]})
        if not nec:
            stats["ray_nec_fail"] += 1
    else:
        stats["nonray"] += 1
        stats["nonray_closure_accept"] += cl
        stats["nonray_nec_reject"] += (not nec)
print(json.dumps(stats))
(HERE / f"_stress_k{k}_s{seed}.json").write_text(json.dumps({"stats": stats, "ray_closure_fail": bad}))
