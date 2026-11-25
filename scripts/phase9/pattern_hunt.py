#!/usr/bin/env python3
"""Complete enumeration of local-pattern two-orbit families of radius r, and the hunt for a period-free one.

A local pattern of radius r assigns distances by offset only:
    d(A_i, A_{i+k}) = fA(min(k, r + 1)),  d(B_i, B_{i+k}) = fB(min(k, r + 1))   (k >= 1, cyclic distance),
    d(A_i, B_{i+o}) = g(o) for |o| <= r,  = gfar otherwise
(optionally a centre p with d(p, A) = zA, d(p, B) = zB). For t >= 4r + 6 the set of patterns that are metrics on the
cycle of length t is one polyhedral cone, independent of t; a family of extreme rays of MET_2t of this form must be
an extreme ray of that cone. The cone is enumerated exactly (cdd), and every extreme ray with positive distances is
tested:
  1. extreme ray of MET_2t for at least two t in --t (exact rank test);
  2. on the largest such cycle: classes left after levels 4 and 7 (fast, mod p); dropped if everything merges;
  3. window test for m in --m: classes after level 4 and after solving the whole window of m positions. A family
     with equal numbers for every m has no forced period: candidate for locality growing linearly in t.

  python scripts/phase9/pattern_hunt.py --r 2 [--centre] [--mirror]
Output results/phase9/pattern_hunt.json.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import multiprocessing as mp
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

import family12 as F  # noqa: E402
from locality_fast import locality_fast  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def var_of(t, r, mirror):
    """Map node pairs of the two-orbit cycle (plus optional centre index 2t) to pattern variables."""
    def v(x, y):
        if x > y:
            x, y = y, x
        if y == 2 * t:
            return ("zA",) if x < t else ("zB",)
        if y < t:
            k = min((y - x) % t, (x - y) % t)
            return ("A", min(k, r + 1))
        if x >= t:
            k = min((y - x) % t, (x - y) % t)
            return ("B", min(k, r + 1))
        o = (y - t - x) % t
        if o > t // 2:
            o -= t
        if abs(o) > r:
            return ("gfar",)
        return ("g", abs(o) if mirror else o)
    return v


def build(t, pat, r, mirror, centre):
    v = var_of(t, r, mirror)
    n = 2 * t + (1 if centre else 0)
    d = np.zeros((n, n), dtype=np.int64)
    for x in range(n):
        for y in range(x + 1, n):
            d[x, y] = d[y, x] = pat[v(x, y)]
    return d


def is_metric(d):
    return all(not (d > d[:, x:x + 1] + d[x:x + 1, :]).any() for x in range(len(d)))


def job(args):
    pat, r, mirror, centre, ts, ms = args
    good = []
    for t in ts:
        d = build(t, pat, r, mirror, centre)
        if is_metric(d) and F.is_ray(d):
            good.append(t)
    if len(good) < 2:
        return pat, good, None
    out = {}
    t = good[-1]
    n = 2 * t + (1 if centre else 0)
    G = [[(i + s_) % t for i in range(t)] + [t + (i + s_) % t for i in range(t)] + list(range(2 * t, n)) for s_ in range(t)]
    L, prof = locality_fast(n, build(t, pat, r, mirror, centre).tolist(), G, levels=[4, 7])
    out["cycle"] = (t, prof.get(4), prof.get(7) or 1)
    if out["cycle"][2] == 1:
        return pat, good, out
    for m in ms:
        t = 2 * m + 2 * r + 7
        d = build(t, pat, r, mirror, centre)
        W = list(range(m)) + [t + i for i in range(m)] + ([2 * t] if centre else [])
        dw = d[np.ix_(W, W)]
        L, prof = locality_fast(len(W), dw.tolist(), None, levels=[4, len(W)])
        out[m] = (prof.get(4), prof.get(len(W)) or 1)
    return pat, good, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, default=2)
    ap.add_argument("--centre", action="store_true")
    ap.add_argument("--mirror", action="store_true")
    ap.add_argument("--t", type=int, nargs="+", default=[9, 10, 11, 12, 13, 14])
    ap.add_argument("--m", type=int, nargs="+", default=[10, 14])
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    import cdd
    import cdd.gmp
    t0 = time.time()
    r = a.r
    t = 4 * r + 7
    n = 2 * t + (1 if a.centre else 0)
    v = var_of(t, r, a.mirror)
    names = sorted({v(x, y) for x, y in itertools.combinations(range(n), 2)}, key=str)
    col = {nm: i for i, nm in enumerate(names)}
    rows = set()
    for x, y, z in itertools.combinations(range(n), 3):
        pa, pb, pc = col[v(x, y)], col[v(x, z)], col[v(y, z)]
        for big, s1, s2 in ((pa, pb, pc), (pb, pa, pc), (pc, pa, pb)):
            row = [0] * len(names)
            row[s1] += 1
            row[s2] += 1
            row[big] -= 1
            if any(row):
                rows.add(tuple(row))
    print(f"radius {r}, centre {a.centre}, mirror {a.mirror}: {len(names)} pattern variables, {len(rows)} inequalities", flush=True)
    mat = cdd.gmp.matrix_from_array([[0] + list(row) for row in sorted(rows)], rep_type=cdd.RepType.INEQUALITY)
    gens = cdd.gmp.copy_generators(cdd.gmp.polyhedron_from_matrix(mat))
    rays = [[Fraction(c) for c in g_[1:]] for g_ in gens.array if g_[0] == 0]
    items = []
    for ray in rays:
        if min(ray) <= 0:
            continue
        den = 1
        for c in ray:
            den = den * c.denominator // math.gcd(den, c.denominator)
        vals = [int(c * den) for c in ray]
        g0 = 0
        for c in vals:
            g0 = math.gcd(g0, c)
        items.append(({nm: vals[i] // g0 for nm, i in col.items()}, r, a.mirror, a.centre, a.t, a.m))
    print(f"{len(rays)} extreme rays of the pattern cone, {len(items)} with positive distances ({time.time() - t0:.0f} s)", flush=True)
    fams, stalled = 0, []
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for k, (pat, good, out) in enumerate(pool.imap_unordered(job, items, chunksize=8), 1):
            if out is not None:
                fams += 1
                if out["cycle"][2] > 1:
                    stalled.append((pat, good, out))
            if k % 5000 == 0:
                print(f"  {k} of {len(items)}: {fams} families, {len(stalled)} unmerged on the cycle ({time.time() - t0:.0f} s)", flush=True)
    m1, m2 = a.m[0], a.m[-1]
    free = [x for x in stalled if all(x[2][m][0] == x[2][m][1] for m in a.m) and x[2][m2][0] > x[2][m1][0]]
    rest = sorted([x for x in stalled if x not in free], key=lambda x: (x[2][m2][0] - x[2][m2][1], -x[2][m2][1]))
    print(f"{fams} patterns are extreme rays for at least two t in {a.t}; {len(stalled)} stay unmerged after level 7 on the "
          f"cycle; {len(free)} have windows forcing no merge ({time.time() - t0:.0f} s)", flush=True)

    def show(x):
        pat, good, out = x
        return (" ".join(f"{'' .join(map(str, k))}={val}" for k, val in sorted(pat.items(), key=lambda kv: str(kv[0]))) +
                f" | rays at t = {good} | cycle (t, level 4, level 7) {out['cycle']} | windows " +
                ", ".join(f"m={m}: {out[m]}" for m in a.m))
    for x in free[:40]:
        print("  PERIOD-FREE CANDIDATE", show(x), flush=True)
    print("closest others:", flush=True)
    for x in rest[:15]:
        print("  ", show(x), flush=True)
    f = ROOT / "results/phase9/pattern_hunt.json"
    old = json.loads(f.read_text()) if f.exists() else {}
    ser = lambda x: {"pattern": {"".join(map(str, k)): val for k, val in x[0].items()}, "rays_at": x[1],
                     "classes": {str(k): val for k, val in x[2].items()}}
    old[f"r{r}" + ("_centre" if a.centre else "") + ("_mirror" if a.mirror else "")] = {
        "cone_rays": len(rays), "positive": len(items), "ray_families": fams, "unmerged_on_cycle": len(stalled),
        "period_free": [ser(x) for x in free], "closest": [ser(x) for x in rest[:100]], "seconds": round(time.time() - t0, 1)}
    atomic_write_json(f, old)


if __name__ == "__main__":
    main()
