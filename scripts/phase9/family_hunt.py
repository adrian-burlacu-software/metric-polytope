#!/usr/bin/env python3
"""Hunt for a period-free family: local-pattern families of two-orbit metrics, with or without mirror symmetry and
with or without a fixed centre, whose open windows force no merge beyond the 4-point ones.

Seeds: the rays stored by sym_search.py under --key (any cyclic two-orbit search, e.g. fixed0_orbits2_t6_fast or
fixed1_orbits2_t5_fast). A seed on orbits of size t0 gives profiles fA(k) = d(A_0, A_k), fB(k) = d(B_0, B_k),
h(j) = d(A_0, B_j) (j mod t0, not assumed symmetric) and, with a centre p, zA = d(p, A), zB = d(p, B).
A local pattern is the seed read around a centre offset c: g(j) = h(c + j), |j| <= r = floor((t0 - 1) / 2).
Its extension to a larger t keeps fA, fB, g at offsets up to r and uses one "far" value beyond (for fA, fB the value
at offset r; for g either g(r) or g(-r)). For every pattern:
  1. the extensions to t = --t must be metrics and extreme rays (exact rank test);
  2. window test: the submetric on m consecutive positions (plus the centre) of a large member; classes after the
     4-point closure and after solving the whole window (fast, mod p). No forced period <=> the two numbers agree for
     every m, and the family then is a candidate for locality growing linearly with t.
Output results/phase9/family_hunt.json.

  python scripts/phase9/family_hunt.py --key fixed0_orbits2_t6_fast --t0 6 --t 11 13 --m 10 14
"""
from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

import family12 as F  # noqa: E402
from locality_fast import locality_fast  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def build(t, fA, fB, g, far, z=None):
    """Nodes: A_0..A_{t-1}, B_0..B_{t-1} (B re-indexed so that the pattern centre is offset 0), then the centre."""
    r = len(fA)
    n = 2 * t + (1 if z else 0)
    d = np.zeros((n, n), dtype=np.int64)
    for i in range(t):
        for j in range(t):
            k = min((j - i) % t, (i - j) % t)
            if k:
                d[i, j] = fA[min(k, r) - 1]
                d[t + i, t + j] = fB[min(k, r) - 1]
            o = (j - i) % t
            if o > t // 2:
                o -= t
            d[i, t + j] = d[t + j, i] = g[o + r] if abs(o) <= r else far
    if z:
        for i in range(t):
            d[2 * t, i] = d[i, 2 * t] = z[0]
            d[2 * t, t + i] = d[t + i, 2 * t] = z[1]
    return d


def is_metric(d):
    n = len(d)
    return all(not (d > d[:, x:x + 1] + d[x:x + 1, :]).any() for x in range(n))


def job(args):
    pat, ts, ms = args
    fA, fB, g, far, z = pat
    r = len(fA)
    for t in ts:
        d = build(t, fA, fB, g, far, z)
        if not is_metric(d) or not F.is_ray(d):
            return pat, None
    out = {}
    t = ts[-1]                                           # on the cycle: classes left after levels 4 and 7
    n = 2 * t + (1 if z else 0)
    G = [[(i + s_) % t for i in range(t)] + [t + (i + s_) % t for i in range(t)] + list(range(2 * t, n)) for s_ in range(t)]
    L, prof = locality_fast(n, build(t, fA, fB, g, far, z).tolist(), G, levels=[4, 7])
    out["cycle"] = (prof.get(4), prof.get(7) or 1)
    if out["cycle"][1] == 1:
        return pat, out                                  # local on the cycle: not interesting, skip the window test
    for m in ms:
        t = 2 * m + 2 * r + 5
        d = build(t, fA, fB, g, far, z)
        W = list(range(m)) + [t + i for i in range(m)] + ([2 * t] if z else [])
        dw = d[np.ix_(W, W)]
        if not is_metric(dw):
            return pat, None
        L, prof = locality_fast(len(W), dw.tolist(), None, levels=[4, len(W)])
        out[m] = (prof.get(4), prof.get(len(W)) or 1)
    return pat, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--t0", type=int, required=True)
    ap.add_argument("--t", type=int, nargs="+", default=[11, 13])
    ap.add_argument("--m", type=int, nargs="+", default=[10, 14])
    ap.add_argument("--workers", type=int, default=14)
    ap.add_argument("--max-seeds", type=int, default=0)
    a = ap.parse_args()
    t0 = time.time()
    j = json.loads((ROOT / "results/phase9/sym_search.json").read_text())
    seeds = j[a.key]["best"]
    if a.max_seeds:
        seeds = seeds[:a.max_seeds]
    centre = a.key.startswith("fixed1")
    f = 1 if centre else 0
    t = a.t0
    r = (t - 1) // 2
    pats = set()
    for b in seeds:
        d = b["d"]
        fA = tuple(d[f][f + k] for k in range(1, r + 1))
        fB = tuple(d[f + t][f + t + k] for k in range(1, r + 1))
        h = [d[f][f + t + jj] for jj in range(t)]
        z = (d[0][f], d[0][f + t]) if centre else None
        for c in range(t):
            g = tuple(h[(c + jj) % t] for jj in range(-r, r + 1))
            for far in {g[0], g[-1]}:
                pats.add((fA, fB, g, far, z))
                pats.add((fB, fA, tuple(reversed(g)), far, (z[1], z[0]) if z else None))      # roles of A and B swapped
    # the swapped pattern is the same family; keep one representative
    uniq = set()
    for p_ in pats:
        q = (p_[1], p_[0], tuple(reversed(p_[2])), p_[3], (p_[4][1], p_[4][0]) if p_[4] else None)
        if q not in uniq:
            uniq.add(p_)
    items = [(p_, a.t, a.m) for p_ in sorted(uniq, key=str)]
    print(f"{len(seeds)} seeds ({a.key}), {len(items)} local patterns", flush=True)
    rays, res = 0, []
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for k, (pat, out) in enumerate(pool.imap_unordered(job, items, chunksize=8), 1):
            if out is not None:
                rays += 1
                res.append((pat, out))
            if k % 5000 == 0:
                print(f"  {k} of {len(items)}, {rays} families ({time.time() - t0:.0f} s)", flush=True)
    m1, m2 = a.m[0], a.m[-1]
    stalled = [(p_, o) for p_, o in res if o["cycle"][1] > 1]
    print(f"{len(stalled)} of the {rays} ray families are still unmerged after level 7 on the cycle", flush=True)
    res = stalled
    free = [(p_, o) for p_, o in res if all(o[m][0] == o[m][1] for m in a.m) and o[m2][0] > o[m1][0]]
    near = sorted([(p_, o) for p_, o in res if (p_, o) not in free],
                  key=lambda x: (x[1][m2][0] - x[1][m2][1], -x[1][m2][1]))
    print(f"{rays} local-pattern families are rays at t = {a.t}; {len(free)} have windows that force no merge "
          f"(classes growing with m); ({time.time() - t0:.0f} s)", flush=True)
    for p_, o in free[:30]:
        print("  PERIOD-FREE CANDIDATE fA", p_[0], "fB", p_[1], "g", p_[2], "far", p_[3], "centre", p_[4], "classes", o, flush=True)
    print("closest others (classes after level 4, after the whole window):", flush=True)
    for p_, o in near[:12]:
        print("  fA", p_[0], "fB", p_[1], "g", p_[2], "far", p_[3], "centre", p_[4], o, flush=True)
    fpath = ROOT / "results/phase9/family_hunt.json"
    old = json.loads(fpath.read_text()) if fpath.exists() else {}
    old[a.key] = {"t": a.t, "m": a.m, "patterns": len(items), "ray_families": rays,
                  "period_free": [{"fA": p_[0], "fB": p_[1], "g": p_[2], "far": p_[3], "centre": p_[4],
                                   "classes": {str(m): o[m] for m in o}} for p_, o in free],
                  "closest": [{"fA": p_[0], "fB": p_[1], "g": p_[2], "far": p_[3], "centre": p_[4],
                               "classes": {str(m): o[m] for m in o}} for p_, o in near[:50]]}
    atomic_write_json(fpath, old)


if __name__ == "__main__":
    main()
