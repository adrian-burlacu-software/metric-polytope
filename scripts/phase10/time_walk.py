#!/usr/bin/env python3
"""Phase 10 step 4: time the adjacency walk at the top rung (k = 8, i.e. m_9) on 100 random Deza orbits (seed 20261122).
Per orbit: tangent-cone extreme rays (exact cdd), each followed to the neighbouring vertex, every neighbour completed
(tight set) and checked to be a vertex, then canonicalised (bliss, full group). Hard-orbit flag: > 100,000 rays or
> 600 s (hard per-orbit timeout). 19 workers. Writes results/phase10/time_walk.json.
"""
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from metricpoly.jobs import atomic_write_json  # noqa: E402

RAY_CAP = 100_000
ORBIT_TIMEOUT = 600


def _one(args):
    r, D, nums = args
    from metricpoly.ladder import rung
    from metricpoly.core import pairs
    R = rung(8, 8)
    order = {e: t for t, e in enumerate(pairs(9))}
    x = tuple(nums[order[e]] for e in R.edges)
    t0 = time.time()
    nb, nrays = R.neighbours(D, x, max_rays=RAY_CAP)
    t_rays = time.time() - t0
    if nb is None:
        return {"row": r, "D": D, "rays": nrays, "flag": "ray cap", "s": round(time.time() - t0, 2)}
    t1 = time.time()
    keys = set()
    nonvert = 0
    for Dy, y in nb:
        if not R.is_vertex(Dy, y):               # completion: full tight set + rank check
            nonvert += 1
        keys.add(R.canonical_key(Dy, y))
    return {"row": r, "D": D, "tight": int(len(R.tight(D, x))), "rays": nrays, "neighbour_orbits": len(keys),
            "non_vertex_neighbours": nonvert, "s_rays": round(t_rays, 3), "s_complete_canon": round(time.time() - t1, 3),
            "s": round(time.time() - t0, 3)}


def main():
    rng = np.random.default_rng(20261122)
    co = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
    de = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
    rows = sorted(int(r) for r in rng.choice(len(co), 100, replace=False))
    jobs = [(r, int(de[r]), [int(v) for v in co[r]]) for r in rows]
    t0 = time.time()
    res = []
    with mp.Pool(19) as pool:
        asy = [pool.apply_async(_one, (j,)) for j in jobs]
        for j, a in zip(jobs, asy):
            try:
                res.append(a.get(timeout=max(1, ORBIT_TIMEOUT - (time.time() - t0)) + ORBIT_TIMEOUT))
            except mp.TimeoutError:
                res.append({"row": j[0], "D": j[1], "flag": "timeout > 600 s"})
        pool.terminate()
    ok = [r for r in res if "flag" not in r]
    out = {"orbits": len(res), "completed": len(ok), "flagged": [r for r in res if "flag" in r],
           "mean_rays": float(np.mean([r["rays"] for r in ok])), "median_rays": float(np.median([r["rays"] for r in ok])),
           "max_rays": int(max(r["rays"] for r in ok)),
           "mean_s_per_orbit": float(np.mean([r["s"] for r in ok])), "median_s": float(np.median([r["s"] for r in ok])),
           "max_s": float(max(r["s"] for r in ok)),
           "mean_s_rays": float(np.mean([r["s_rays"] for r in ok])),
           "mean_s_complete_canon": float(np.mean([r["s_complete_canon"] for r in ok])),
           "non_vertex_neighbours_total": int(sum(r["non_vertex_neighbours"] for r in ok)),
           "wall_seconds": round(time.time() - t0, 1), "rows": res}
    atomic_write_json(ROOT / "results/phase10/time_walk.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
