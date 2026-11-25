#!/usr/bin/env python3
"""Find families of extreme rays, uniform in the orbit size t, with growing locality.

Input: the dihedral two-orbit rays on 2t0 points found by sym_search.py (results/phase9/sym_search.json, key
fixed0_orbits2_t{t0}_mirror0_1_fast). Such a metric is given by three profiles in the offset k:
    fA(k) = d(A_i, A_{i+k}),  fB(k) = d(B_i, B_{i+k})  (k = 1..r),   h(k) = d(A_i, B_{i+k})  (k = -r..r, h(k) = h(-k)),
with r = (t0 - 1) / 2 and the B orbit re-indexed so that the reflection fixes offset 0.
Each profile is extended to a larger odd t in one of two ways: "near" (offsets beyond r keep the last value) or
"far" (the values are anchored at the antipode: offset r' - j gets the value of offset r - j, smaller offsets keep
their value while they exist, the gap takes the value at offset `gap`). All combinations are tried; an extension is
kept if it is a metric, an extreme ray (exact rank test) and its locality (fast, mod p) is computed. A family is
reported when the same rule gives rays at several t.

  python scripts/phase9/family_extend.py --t0 7 --t 9 11 --minL 9
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


def dihedral(t):
    n = 2 * t
    rot = [(i + 1) % t for i in range(t)] + [t + (i + 1) % t for i in range(t)]
    ref = [(-i) % t for i in range(t)] + [t + (-i) % t for i in range(t)]
    G, fr = {tuple(range(n))}, [tuple(range(n))]
    while fr:
        nx = []
        for h in fr:
            for g in (rot, ref):
                c = tuple(g[h[i]] for i in range(n))
                if c not in G:
                    G.add(c)
                    nx.append(c)
        fr = nx
    return [list(g) for g in G]


def profiles(d, t):
    """(fA, fB, h) of a metric from sym_search with mirror offsets (0, 1): the reflection maps B_j to B_{1-j}, so the
    fixed B offset is (t + 1) / 2; re-index B by that shift."""
    r = (t - 1) // 2
    s = (t + 1) // 2
    fA = [d[0][k] for k in range(1, r + 1)]
    fB = [d[t][t + k] for k in range(1, r + 1)]
    h = [d[0][t + (s + k) % t] for k in range(0, r + 1)]
    assert all(d[0][t + (s + k) % t] == d[0][t + (s - k) % t] for k in range(r + 1))
    return fA, fB, h


def extend(f, r, r2, mode, first):
    """f: values for offsets first..r. Returns values for offsets first..r2.
    near: offsets beyond r keep the last value. far: the first half of the offsets (up to m) keeps its values, the
    second half stays attached to the antipode (offset r2 - j gets the value of offset r - j), and the gap takes
    the value at offset m."""
    if mode == "near":
        return f + [f[-1]] * (r2 - r)
    m = (first + r) // 2
    out = []
    for k in range(first, r2 + 1):
        jj = r2 - k
        if k <= m:
            out.append(f[k - first])
        elif jj <= r - m - 1:
            out.append(f[r - jj - first])
        else:
            out.append(f[m - first])
    return out


def build(t, fA, fB, h):
    n = 2 * t
    d = np.zeros((n, n), dtype=np.int64)
    for i in range(t):
        for j in range(t):
            k = min((j - i) % t, (i - j) % t)
            if k:
                d[i, j] = fA[k - 1]
                d[t + i, t + j] = fB[k - 1]
            d[i, t + j] = d[t + j, i] = h[k]
    return d


def job(args):
    t, fA, fB, h, tag, smax = args
    d = build(t, fA, fB, h)
    n = 2 * t
    for m in range(n):                                   # metric? (cheap vectorised check)
        if (d > d[:, m:m + 1] + d[m:m + 1, :]).any():
            return tag, t, None, None
    if not F.is_ray(d):
        return tag, t, None, None
    L, prof = locality_fast(n, d.tolist(), dihedral(t), smax)
    return tag, t, (L if L is not None else 10 ** 6), prof


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t0", type=int, default=7)
    ap.add_argument("--t", type=int, nargs="+", default=[9, 11])
    ap.add_argument("--minL", type=int, default=8, help="only seeds with at least this locality at t0")
    ap.add_argument("--smax", type=int, default=0)
    ap.add_argument("--workers", type=int, default=14)
    a = ap.parse_args()
    t0 = time.time()
    j = json.loads((ROOT / "results/phase9/sym_search.json").read_text())
    seeds = [b for b in j[f"fixed0_orbits2_t{a.t0}_mirror0_1_fast"]["best"] if b["L"] and b["L"] >= a.minL]
    r = (a.t0 - 1) // 2
    items, seen = [], set()
    for si, b in enumerate(seeds):
        fA, fB, h = profiles(b["d"], a.t0)
        for mA, mB, mh in itertools.product(("near", "far"), repeat=3):
            for t in a.t:
                r2 = (t - 1) // 2
                e = (tuple(extend(fA, r, r2, mA, 1)), tuple(extend(fB, r, r2, mB, 1)), tuple(extend(h, r, r2, mh, 0)))
                if (t, e) in seen:
                    continue
                seen.add((t, e))
                items.append((t, list(e[0]), list(e[1]), list(e[2]), (si, b["L"], mA, mB, mh, tuple(fA), tuple(fB), tuple(h)), a.smax or None))
    print(f"{len(seeds)} seeds at t0 = {a.t0}, {len(items)} candidate extensions", flush=True)
    res = {}
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for tag, t, L, prof in pool.imap_unordered(job, items, chunksize=2):
            if L is not None:
                res.setdefault(tag, {})[t] = L
    fam = sorted(res.items(), key=lambda kv: (-len(kv[1]), -max(kv[1].values())))
    out = []
    for tag, byt in fam:
        si, L0, mA, mB, mh, fA, fB, h = tag
        print(f"seed L = {L0} at t = {a.t0}; fA {fA} [{mA}], fB {fB} [{mB}], h {h} [{mh}]  ->  " +
              ", ".join(f"t = {t}: L = {L if L < 10 ** 6 else '>smax'}" for t, L in sorted(byt.items())), flush=True)
        out.append({"t0": a.t0, "L0": L0, "fA": fA, "fB": fB, "h": h, "modes": [mA, mB, mh],
                    "L": {str(t): (L if L < 10 ** 6 else None) for t, L in sorted(byt.items())}})
    f = ROOT / "results/phase9/family_extend.json"
    old = json.loads(f.read_text()) if f.exists() else {}
    old[f"t0_{a.t0}"] = out
    atomic_write_json(f, old)
    print(f"done ({time.time() - t0:.0f} s)", flush=True)


if __name__ == "__main__":
    main()
