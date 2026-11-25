#!/usr/bin/env python3
"""The family C_t (t odd, t >= 9): 2t points A_i, B_i (i mod t) with

    d(A_i, A_j) = 16, 12, 8   for cyclic distance |i - j| = 1, 2, >= 3
    d(B_i, B_j) = 10, 20, 22  for cyclic distance |i - j| = 1, 2, >= 3
    d(A_i, B_{i+o}) = 13, 11, 7, 9, 19 for o = -2, -1, 0, 1, 2, and 15 otherwise.

Checks, in exact arithmetic, for each t given:
  1. d is a metric;
  2. d spans an extreme ray of MET_2t (rank of the tight system = C(2t,2) - 1; the modular rank is a lower bound
     for the rank and C(2t,2) - 1 is an upper bound, so equality is exact);
  3. the level-(2t - 1) closure is not total (rational arithmetic), i.e. the locality is exactly 2t: no proper
     subset of the points proves extremality.
  python scripts/phase9/family_C.py 9 11 13 ...
Output results/phase9/family_C.json.
"""
import json, sys, time
from pathlib import Path
import multiprocessing as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
import family12 as F  # noqa: E402
from locality import closure_classes  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402

A = {1: 16, 2: 12}
B = {1: 10, 2: 20}
G = {-2: 13, -1: 11, 0: 7, 1: 9, 2: 19}


def metric(t, a2=12):
    d = np.zeros((2 * t, 2 * t), dtype=np.int64)
    for i in range(t):
        for j in range(t):
            k = min((j - i) % t, (i - j) % t)
            if k:
                d[i, j] = {1: 16, 2: a2}.get(k, 8)
                d[t + i, t + j] = B.get(k, 22)
            o = (j - i) % t
            if o > t // 2:
                o -= t
            d[i, t + j] = d[t + j, i] = G.get(o, 15)
    return d


def job(a):
    t, a2 = a
    t0 = time.time()
    d = metric(t, a2)
    n = 2 * t
    met = all(not (d > d[:, x:x + 1] + d[x:x + 1, :]).any() for x in range(n))
    ray = bool(met and F.is_ray(d))
    tight = int(sum((d[i, j] == d[i, m] + d[m, j]) for i in range(n) for j in range(i + 1, n) for m in range(n) if m != i and m != j))
    cls = closure_classes(n, d.tolist(), n - 1) if ray else None
    return t, a2, met, ray, tight, cls, round(time.time() - t0)


if __name__ == "__main__":
    ts = [int(v) for v in sys.argv[1:]] or [9, 11, 13]
    f = ROOT / "results/phase9/family_C.json"
    out = json.loads(f.read_text()) if f.exists() else {}
    with mp.get_context("spawn").Pool(min(16, 2 * len(ts))) as pool:
        for t, a2, met, ray, tight, cls, sec in pool.imap_unordered(job, [(t, a2) for t in ts for a2 in (12, 16)]):
            n = 2 * t
            print(f"t = {t} (n = {n}), d(A_i, A_i+2) = {a2}: metric {met}, extreme ray {ray}, tight triples {tight} "
                  f"(minimum {n*(n-1)//2 - 1}), classes of cl_{n-1}: {cls} -> " +
                  ("L = n" if ray and cls and cls > 1 else "L < n" if ray else "-") + f" ({sec} s)", flush=True)
            out[f"t{t}_a{a2}"] = {"n": n, "metric": met, "extreme_ray": ray, "tight_triples": tight, "classes_level_n_minus_1": cls,
                                  "L_equals_n": bool(ray and cls and cls > 1), "seconds": sec}
            atomic_write_json(f, out)
