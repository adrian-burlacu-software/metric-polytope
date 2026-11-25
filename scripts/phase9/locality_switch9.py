#!/usr/bin/env python3
"""Does the locality of an m_9 orbit depend on the switching? Random sample of orbits of the m_9 list; for each,
every switching that gives an extreme ray of MET_9 (all 256 tried), locality of each ray (rays with fewer than 9
distinct points are kept, with their own k). Stops after --budget seconds and reports the orbits finished.
Output results/phase9/locality_switch9.json.
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

import family12 as F  # noqa: E402
from locality import locality  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def job(a):
    i, D, nums = a
    rays = F.dedupe(F._rays_of(Point.make(9, D, nums)))
    return i, D, [(k, locality(k, F.metric(k, e).tolist())) for k, e in rays]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orbits", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--budget", type=float, default=480)
    ap.add_argument("--seed", type=int, default=20261126)
    a = ap.parse_args()
    t0 = time.time()
    d = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
    c = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
    idx = np.random.default_rng(a.seed).choice(len(d), a.orbits, replace=False)       # random order, not sorted
    items = [(int(i), int(d[i]), [int(v) for v in c[i]]) for i in idx if d[i] > 1]
    done, norays = 0, 0
    allL, maxL, minL, spread, full, nrays = Counter(), Counter(), Counter(), Counter(), [], 0
    pool = mp.get_context("spawn").Pool(a.workers)
    for i, D, res in pool.imap(job, items, chunksize=2):                               # in order: a prefix of the sample
        done += 1
        if not res:
            norays += 1
        else:
            Ls = [L for k, L in res if k == 9]
            nrays += len(res)
            for k, L in res:
                allL[f"{k}|{L}"] += 1
                if L == k:
                    full.append({"i": i, "D": D, "k": k})
            if Ls:
                maxL[max(Ls)] += 1
                minL[min(Ls)] += 1
                spread[max(Ls) - min(Ls)] += 1
        if time.time() - t0 > a.budget:
            break
    pool.terminate()
    out = {"orbits_sampled": done, "not_cut_adjacent": norays, "rays": nrays,
           "rays_by_k_and_L": dict(sorted(allL.items())), "max_L_per_orbit": dict(sorted(maxL.items())),
           "min_L_per_orbit": dict(sorted(minL.items())), "max_minus_min": dict(sorted(spread.items())),
           "rays_with_L_equal_k": full, "seconds": round(time.time() - t0, 1)}
    atomic_write_json(ROOT / "results/phase9/locality_switch9.json", out)
    for k, v in out.items():
        print(k, v, flush=True)


if __name__ == "__main__":
    main()
