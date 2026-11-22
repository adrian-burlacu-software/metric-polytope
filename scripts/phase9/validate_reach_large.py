#!/usr/bin/env python3
"""Validate metricpoly.reach_large against the n <= 9 machinery (seeded 20261122). Runs in parallel, < 10 min.
 (1) base test vs base-key table: every base orbit n <= 9 must be recognised; every Deza vertex rep n <= 8 must get
     the same verdict as table membership
 (2) reachable() vs the engine's verdict on 60 n = 8 targets (30 reached, 30 unreached) and 10 n = 9 targets,
     30 s budget each (None = undecided is reported, not counted as agreement)
Writes results/phase9/reach_large_validation.json
"""
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

from metricpoly import deza, group  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402
from metricpoly.reach_large import is_base, reachable  # noqa: E402


def _base_check(k):
    n, D = int(k.split("|")[0]), int(k.split("|")[1])
    return bool(is_base(Point.make(n, D, [int(v) for v in k.split("|")[2].split(",")])))


def _deza_check(args):
    x, in_table = args
    return bool(is_base(x)) == in_table


def _reach(args):
    meta, x = args
    t0 = time.time()
    v, nodes = reachable(x, budget=30)
    return {**meta, "large": v, "nodes": nodes, "s": round(time.time() - t0, 2)}


def main():
    from judge import CK, targets
    from phase9_round import load_state
    from metricpoly.reach import Engine
    rng = np.random.default_rng(20261122)
    b = json.loads((ROOT / "results/n9/base_keys.json").read_text())
    out = {}
    t = time.time()
    with mp.Pool(16) as pool:
        keys = [k for n in range(3, 10) for k in b[str(n)]]
        ok = pool.map(_base_check, keys, chunksize=50)
        out["base_table_orbits"] = len(keys)
        out["base_table_orbits_not_recognised"] = sum(1 for v in ok if not v)
        dz = []
        for n in range(3, 9):
            ks = set(b[str(n)])
            dz += [(x, group.canonical(x).key() in ks) for x in deza.load_ext(n)]
        agree = pool.map(_deza_check, dz, chunksize=20)
        out["deza_reps_checked"] = len(dz)
        out["deza_base_mismatch"] = sum(1 for v in agree if not v)
        print(out, round(time.time() - t, 1), flush=True)
        eng = Engine(CK / "engine")
        reached, _ = load_state()
        T = targets()
        ids8 = [i for i, (n, o, _) in enumerate(T) if n == 8]
        r8 = [i for i in ids8 if eng.target_key(i) in reached]
        u8 = [i for i in ids8 if eng.target_key(i) not in reached]
        ids9 = [i for i, (n, o, _) in enumerate(T) if n == 9 and isinstance(o, int)]
        pick = [int(i) for i in rng.choice(r8, 30, replace=False)] + [int(i) for i in rng.choice(u8, 30, replace=False)] \
            + [int(i) for i in rng.choice(ids9, 10, replace=False)]
        jobs = [({"n": T[i][0], "id": int(T[i][1]), "engine": eng.target_key(i) in reached}, T[i][2]) for i in pick]
        res = pool.map(_reach, jobs, chunksize=1)
    out["checked"] = len(res)
    out["agree"] = sum(1 for r in res if r["large"] == r["engine"])
    out["undecided"] = sum(1 for r in res if r["large"] is None)
    out["disagree"] = [r for r in res if r["large"] is not None and r["large"] != r["engine"]]
    out["rows"] = res
    out["seconds"] = round(time.time() - t, 1)
    atomic_write_json(ROOT / "results/phase9/reach_large_validation.json", out)
    print({k: v for k, v in out.items() if k != "rows"}, flush=True)


if __name__ == "__main__":
    main()
