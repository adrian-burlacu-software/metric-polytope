"""Collect the k = 9 rays not reached by the exchange closure (claim 03) and show what is left."""
import importlib.util, json, collections
from pathlib import Path
from multiprocessing import Pool
HERE = Path(__file__).resolve().parent
FAM = HERE.parents[2] / "results/phase9/family12"
_m = None


def mod():
    global _m
    if _m is None:
        sp = importlib.util.spec_from_file_location("c03", HERE / "03_exchange_closure_sufficient.py")
        _m = importlib.util.module_from_spec(sp); sp.loader.exec_module(_m)
    return _m


def work(chunk):
    m = mod()
    return [j for j in chunk if not m.claim(j["k"], [tuple(e) for e in j["edges"]])]


if __name__ == "__main__":
    S = json.loads((FAM / "rays_k9.json").read_text())
    with Pool(4) as pool:
        bad = [j for part in pool.map(work, [S[i:i + 200] for i in range(0, len(S), 200)]) for j in part]
    (HERE / "_k9_closure_misses.json").write_text(json.dumps(bad))
    print(len(bad), "misses")
    m = mod()
    print(collections.Counter(tuple(sorted({w for _, _, w in j["edges"]})) for j in bad))
    for j in bad[:3]:
        k, e = j["k"], [tuple(x) for x in j["edges"]]
        d = m._dist(k, e); T = m._tight(k, d); uf = m._exchange_classes(k, T)
        cl = collections.defaultdict(list)
        for p in m._pairs(k):
            cl[uf.f(p)].append(p)
        name = {c: f"{chr(65 + i)}{d[c[0]][c[1]]}" for i, c in enumerate(cl)}
        print("edges", e)
        for c, v in cl.items():
            print("  ", name[c], v)
        print("  ", sorted(f"{name[S_]}={name[P]}+{name[Q]}" for S_, P, Q in m._class_eqs(T, uf)))
