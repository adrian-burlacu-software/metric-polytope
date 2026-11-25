#!/usr/bin/env python3
"""Locality of random extreme rays of MET_n for n beyond the vertex lists.

Random face descent, in exact rational arithmetic: start from a random metric with all triangle inequalities
strict; repeatedly choose a random direction in the linear span of the current face (the null space of the tight
equalities) and move until the next triangle inequality becomes tight; stop when the null space is a line. The end
point is an extreme ray by construction (re-checked), and typically has few tight triples beyond the minimum
C(n,2) - 1. End points with a zero distance are discarded. The locality of the exact integer ray is computed with
scripts/phase9/locality.py. The distribution is that of the descent, not uniform; the point is the existence of
rays of large locality, each one exact.

  python scripts/phase9/random_ray_locality.py --n 10 11 12 --samples 40
Output results/phase9/random_ray_locality.json (per n; the rays of largest locality are stored).
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import multiprocessing as mp
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

from locality import locality  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def null_space(rows, N):
    """Basis of the null space of integer rows (lists of length N), exact."""
    M = [[Fraction(v) for v in r] for r in rows]
    piv, r = [], 0
    for c in range(N):
        if r == len(M):
            break
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        inv = 1 / M[r][c]
        M[r] = [v * inv for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        piv.append(c)
        r += 1
    free = [c for c in range(N) if c not in piv]
    basis = []
    for fc in free:
        x = [Fraction(0)] * N
        x[fc] = Fraction(1)
        for i, c in enumerate(piv):
            x[c] = -M[i][fc]
        basis.append(x)
    return basis


def primitive(x):
    den = 1
    for v in x:
        den = den * v.denominator // math.gcd(den, v.denominator)
    xi = [int(v * den) for v in x]
    g = 0
    for v in xi:
        g = math.gcd(g, v)
    return [v // g for v in xi]


def job(args):
    try:
        return _job(args)
    except ZeroDivisionError:
        return args[0], args[1], None, None, None


def _job(args):
    n, seed = args
    rng = np.random.default_rng(seed)
    P = list(itertools.combinations(range(n), 2))
    idx = {p: i for i, p in enumerate(P)}
    N = len(P)
    trip = [(idx[(a, b)], idx[(min(a, m), max(a, m))], idx[(min(m, b), max(m, b))])
            for a, b in P for m in range(n) if m != a and m != b]
    x = [Fraction(int(v)) for v in 1000 + rng.integers(0, 1000, size=N)]       # all triangles strict
    tight = set()
    while True:
        rows = []
        for t in sorted(tight):
            r = [0] * N
            r[trip[t][0]] += 1
            r[trip[t][1]] -= 1
            r[trip[t][2]] -= 1
            rows.append(r)
        B = null_space(rows, N) if rows else [[Fraction(int(i == j)) for j in range(N)] for i in range(N)]
        if len(B) == 1:
            break
        co = [int(v) for v in rng.integers(-5, 6, size=len(B))]
        v = [sum(c * b[i] for c, b in zip(co, B)) for i in range(N)]
        # slack_t(x + lam v) = s_t + lam * r_t ; move in the direction of positive lam until the first slack hits 0
        best = None
        for t, (pa, pp, pq) in enumerate(trip):
            if t in tight:
                continue
            rt = v[pp] + v[pq] - v[pa]
            if rt < 0:
                lam = (x[pp] + x[pq] - x[pa]) / (-rt)
                if best is None or lam < best:
                    best = lam
        if best is None:
            continue                                         # direction along the lineality-free cone: try another
        x = [a + best * b for a, b in zip(x, v)]
        x = [Fraction(c) for c in primitive(x)]
        new = {t for t, (pa, pp, pq) in enumerate(trip) if x[pa] == x[pp] + x[pq]}
        assert tight <= new and len(new) > len(tight)
        tight = new
    xi = primitive(B[0])
    if xi[0] < 0:
        xi = [-c for c in xi]
    if min(xi) <= 0:
        return n, seed, None, None, None
    d = [[0] * n for _ in range(n)]
    for (a, b), c in zip(P, xi):
        d[a][b] = d[b][a] = c
    exact_tight = sum(1 for pa, pp, pq in trip if xi[pa] == xi[pp] + xi[pq])
    assert exact_tight == len(tight) and not any(xi[pa] > xi[pp] + xi[pq] for pa, pp, pq in trip)
    return n, seed, d, exact_tight, locality(n, d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, nargs="+", default=[10, 11, 12])
    ap.add_argument("--samples", type=int, default=40)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--budget", type=float, default=500)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    t0 = time.time()
    f = ROOT / "results/phase9/random_ray_locality.json"
    out = json.loads(f.read_text()) if f.exists() else {}
    pool = mp.get_context("spawn").Pool(a.workers)
    for n in a.n:
        c, tc, best, done, bad = Counter(), Counter(), [], 0, 0
        for nn, seed, d, nt, L in pool.imap_unordered(job, [(n, a.seed + 100000 * n + i) for i in range(a.samples)]):
            done += 1
            if d is None:
                bad += 1
            else:
                assert L is not None
                c[L] += 1
                tc[nt - (n * (n - 1) // 2 - 1)] += 1
                best.append((L, nt, seed, d))
            if time.time() - t0 > a.budget:
                break
        best.sort(key=lambda r: -r[0])
        out[str(n)] = {"samples": done, "discarded": bad, "locality": {str(k): v for k, v in sorted(c.items())},
                       "tight_triples_beyond_minimum": {str(k): v for k, v in sorted(tc.items())},
                       "best": [{"L": L, "tight": nt, "seed": seed, "d": d} for L, nt, seed, d in best[:5]]}
        atomic_write_json(f, out)
        print(f"n = {n}: {done} LPs, {bad} discarded, locality {dict(sorted(c.items()))}, "
              f"tight triples beyond C(n,2)-1: {dict(sorted(tc.items()))} ({time.time() - t0:.0f} s)", flush=True)
        if time.time() - t0 > a.budget:
            break
    pool.terminate()


if __name__ == "__main__":
    main()
