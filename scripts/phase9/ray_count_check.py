#!/usr/bin/env python3
"""Cross-check of the ray lists behind locality_checks.py against the published numbers of extreme rays of MET_n.

Every extreme ray of MET_n is a blow-up (points at distance 0 merged, Avis 1980 Thm 4.2) of an extreme ray with
positive distances on k <= n points: the 2-point metric (cuts) or one of our rays on k = 5..8 points. A ray r on k
points gives k! * S(n, k) / |Aut(r)| labelled rays on n points (S = Stirling number of the second kind).
Published totals (A. Deza's metric polytope page): 25, 296, 55,226, 119,269,588 for n = 5, 6, 7, 8.
Also the number of orbits under S_n (orbits of Aut(r) on the compositions of n into k positive parts).
"""
import itertools, json, math, sys, time
from pathlib import Path
import multiprocessing as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
import family12 as F  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402

PUBLISHED = {5: 25, 6: 296, 7: 55226, 8: 119269588}
_P = {}


def auts(item):
    k, e = item
    if k not in _P:
        _P[k] = np.array(list(itertools.permutations(range(k))), dtype=np.int64)
    P = _P[k]
    d = F.metric(k, e)
    ok = np.ones(len(P), dtype=bool)
    for i in range(k):
        for j in range(i + 1, k):
            ok &= d[P[:, i], P[:, j]] == d[i, j]
    return k, [tuple(int(v) for v in p) for p in P[ok]]


def stirling2(n, k):
    return sum((-1) ** (k - j) * math.comb(k, j) * j ** n for j in range(k + 1)) // math.factorial(k)


def comp_orbits(n, k, A):
    comps = [c for c in itertools.product(range(1, n - k + 2), repeat=k) if sum(c) == n]
    seen, orbits = set(), 0
    for c in comps:
        if c in seen:
            continue
        orbits += 1
        for p in A:
            seen.add(tuple(c[p[i]] for i in range(k)))
    return orbits


def main():
    t0 = time.time()
    from vertex_structure import load_set
    pts = [x for _k, x in load_set("m8", 0, 0) if x.D > 1]
    with mp.get_context("spawn").Pool(6) as pool:
        uniq = F.dedupe([r for part in pool.imap_unordered(F._rays_of, pts, chunksize=4) for r in part])
        res = list(pool.imap(auts, uniq, chunksize=8))
    out = {}
    for n in (5, 6, 7, 8):
        total, orbits = stirling2(n, 2), n // 2            # cuts: S(n,2) labelled, floor(n/2) orbits
        for k, A in res:
            if k <= n:
                lab = math.factorial(k) * stirling2(n, k)
                assert lab % len(A) == 0
                total += lab // len(A)
                orbits += comp_orbits(n, k, A)
        out[str(n)] = {"extreme_rays": total, "published": PUBLISHED[n], "match": total == PUBLISHED[n], "orbits_under_S_n": orbits}
        print(f"MET_{n}: {total} extreme rays (published {PUBLISHED[n]}), {orbits} orbits under S_{n}", flush=True)
    out["positive_rays_per_k"] = {str(k): sum(1 for kk, _ in res if kk == k) for k in (5, 6, 7, 8)}
    out["seconds"] = round(time.time() - t0, 1)
    atomic_write_json(ROOT / "results/phase9/ray_count_check.json", out)


if __name__ == "__main__":
    main()
