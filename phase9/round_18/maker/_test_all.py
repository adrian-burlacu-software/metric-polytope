"""Evaluate every claim file on all public data (maker self-test; does not use the judge or the held-out files)."""
import importlib.util, json, sys, time
from pathlib import Path
from multiprocessing import Pool
HERE = Path(__file__).resolve().parent
FAM = HERE.parents[2] / "results/phase9/family12"
FILES = sorted(HERE.glob("[0-9][0-9]_*.py"))
_mods = None


def mods():
    global _mods
    if _mods is None:
        _mods = []
        for p in FILES:
            sp = importlib.util.spec_from_file_location(p.stem, p)
            m = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(m)
            _mods.append(m)
    return _mods


def work(chunk):
    return [[bool(m.claim(k, [tuple(e) for e in edges])) for m in mods()] for k, edges in chunk]


def run(pool, name):
    S = [(j["k"], j["edges"]) for j in json.loads((FAM / name).read_text())]
    ch = [S[i:i + 200] for i in range(0, len(S), 200)]
    res = [r for part in pool.map(work, ch) for r in part]
    return [sum(r[i] for r in res) for i in range(len(FILES))], len(S)


if __name__ == "__main__":
    ks = [int(x) for x in sys.argv[1:]] or [5, 6, 7, 8, 9]
    out = {}
    with Pool(4) as pool:
        for k in ks:
            for kind in ("rays", "nonrays_public"):
                if kind != "rays" and k < 6:
                    continue
                t = time.time()
                acc, n = run(pool, f"{kind}_k{k}.json")
                out[f"{kind}_k{k}"] = {"n": n, "accepted": dict(zip([p.stem for p in FILES], acc))}
                print(kind, k, n, acc, round(time.time() - t, 1), flush=True)
    (HERE / f"_selftest_{'_'.join(map(str, ks))}.json").write_text(json.dumps(out, indent=1))
