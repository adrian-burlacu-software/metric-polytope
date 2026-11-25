#!/usr/bin/env python3
"""Scan for families of extreme rays whose locality stays within a constant of the number of points.

Testing "L >= n - g" is cheap for small g: only the subsets missing g + 1 points matter (the closure at level s
contains the closure at every lower level, so L > s iff the level-s closure, run on its own, is not total).
For every dihedral two-orbit ray on 2*t0 points (seeds from sym_search.py) and every extension rule of
family_extend.py, the extension to each t in --t is tested: extreme ray (exact rank)? and the largest g <= --gmax
with cl_{n-g} total (fast, mod p), i.e. L = n - g, or L <= n - gmax - ... if still total at n - gmax.
A rule is reported when it gives rays for at least two of the t's.

  python scripts/phase9/family_scan.py --t0 7 --t 11 13 17 --gmax 4
"""
from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

import family12 as F  # noqa: E402
from family_extend import build, dihedral, extend, profiles  # noqa: E402
from locality_fast import locality_fast  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402

_G = {}


def deficit(t, d, gmax):
    """Smallest g in 0..gmax with cl_{n-g-1} not total (then L = n - g); gmax + 1 if cl_{n-gmax-1} is total."""
    n = 2 * t
    if t not in _G:
        _G[t] = dihedral(t)
    for g in range(gmax + 1):
        s = n - g - 1
        L, prof = locality_fast(n, d, _G[t], smax=s, smin=s)
        if L is None:
            return g
    return gmax + 1


def job(args):
    t, fA, fB, h, tag, gmax = args
    d = build(t, fA, fB, h)
    n = 2 * t
    for m in range(n):
        if (d > d[:, m:m + 1] + d[m:m + 1, :]).any():
            return tag, t, None
    if not F.is_ray(d):
        return tag, t, None
    return tag, t, deficit(t, d.tolist(), gmax)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t0", type=int, default=7)
    ap.add_argument("--t", type=int, nargs="+", default=[11, 13])
    ap.add_argument("--gmax", type=int, default=3)
    ap.add_argument("--minL", type=int, default=4)
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
                items.append((t, list(e[0]), list(e[1]), list(e[2]), (b["L"], mA, mB, mh, tuple(fA), tuple(fB), tuple(h)), a.gmax))
    print(f"{len(seeds)} seeds at t0 = {a.t0}, {len(items)} candidate extensions", flush=True)
    res = {}
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for k, (tag, t, g) in enumerate(pool.imap_unordered(job, items, chunksize=8), 1):
            if g is not None:
                res.setdefault(tag, {})[t] = g
            if k % 5000 == 0:
                print(f"  {k} of {len(items)} ({time.time() - t0:.0f} s)", flush=True)
    fam = [(tag, byt) for tag, byt in res.items() if len(byt) >= min(2, len(a.t))]
    fam.sort(key=lambda kv: (max(kv[1].values()), -len(kv[1])))
    out = []
    for tag, byt in fam:
        L0, mA, mB, mh, fA, fB, h = tag
        txt = ", ".join(f"t = {t}: L = " + (f"n - {g}" if g <= a.gmax else f"<= n - {g}") for t, g in sorted(byt.items()))
        out.append({"t0": a.t0, "L0": L0, "fA": fA, "fB": fB, "h": h, "modes": [mA, mB, mh], "deficit": {str(t): g for t, g in byt.items()}})
        if max(byt.values()) <= a.gmax:
            print(f"seed L = {L0}; fA {fA} [{mA}], fB {fB} [{mB}], h {h} [{mh}]  ->  {txt}", flush=True)
    print(f"{len(fam)} rules give rays at two or more t; {sum(1 for _, b in fam if max(b.values()) <= a.gmax)} keep L >= n - {a.gmax} ({time.time() - t0:.0f} s)", flush=True)
    f = ROOT / "results/phase9/family_scan.json"
    old = json.loads(f.read_text()) if f.exists() else {}
    old[f"t0_{a.t0}_t_{'_'.join(map(str, a.t))}"] = out
    atomic_write_json(f, old)


if __name__ == "__main__":
    main()
