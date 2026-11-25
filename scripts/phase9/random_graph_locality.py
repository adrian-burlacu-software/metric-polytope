#!/usr/bin/env python3
"""Random graphs G(n, 1/2): share whose shortest-path metric is an extreme ray, and share with locality 4.
Empirical companion to Lemma A / Theorem 3 of docs/paper_draft.md (which are asymptotic)."""
import json, sys, time
from pathlib import Path
import multiprocessing as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
import family12 as F  # noqa: E402
from locality import locality  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def job(a):
    n, seed = a
    rng = np.random.default_rng(seed)
    edges = [(i, j, 1) for i in range(n) for j in range(i + 1, n) if rng.random() < 0.5]
    d = F.metric(n, edges)
    if d.max() >= F.INF:
        return n, False, False
    ray = bool(F.is_ray(d))
    L4 = locality(n, d.tolist(), smax=4) == 4
    assert not (L4 and not ray)
    return n, ray, L4


if __name__ == "__main__":
    t0 = time.time()
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    out = {}
    with mp.get_context("spawn").Pool(6) as pool:
        for n in (6, 8, 10, 12, 14, 16, 20, 24):
            r = list(pool.imap_unordered(job, [(n, 1000 * n + i) for i in range(M)], chunksize=4))
            out[str(n)] = {"graphs": M, "rays": sum(x[1] for x in r), "locality_4": sum(x[2] for x in r)}
            print(n, out[str(n)], f"({time.time() - t0:.0f} s)", flush=True)
    atomic_write_json(ROOT / "results/phase9/random_graph_locality.json", out)
