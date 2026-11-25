#!/usr/bin/env python3
"""Locality of the period-free candidates of pattern_hunt.py on cycles of growing size (fast, mod p).

For each candidate and each t: extreme ray? Then the deficit n - L is bracketed by single-level closures:
level n - 1, n - 2, ... down to n - gmax - 1 (a level-s closure that is not total means L > s).
  python scripts/phase9/cand_pattern.py --key r2 --t 9 11 13 15 17 --gmax 3
Output results/phase9/cand_pattern.json.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

import family12 as F  # noqa: E402
from locality_fast import locality_fast  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402
from pattern_hunt import build, is_metric  # noqa: E402


def parse(pd):
    pat = {}
    for k, v in pd.items():
        if k in ("gfar", "zA", "zB"):
            pat[(k,)] = v
        else:
            pat[(k[0], int(k[1:]))] = v
    return pat


def job(args):
    ci, pd, r, mirror, centre, t, gmax = args
    t0 = time.time()
    pat = parse(pd)
    d = build(t, pat, r, mirror, centre)
    if not is_metric(d):
        return ci, t, "not a metric", None, 0
    if not F.is_ray(d):
        return ci, t, "not a ray", None, 0
    n = len(d)
    G = [[(i + s_) % t for i in range(t)] + [t + (i + s_) % t for i in range(t)] + list(range(2 * t, n)) for s_ in range(t)]
    dl = d.tolist()
    g = 0
    while g <= gmax:
        s = n - g - 1
        L, prof = locality_fast(n, dl, G, levels=[4, s])
        if L is None:
            return ci, t, "ray", g, round(time.time() - t0)          # cl_s not total: L = n - g
        g += 1
    return ci, t, "ray", gmax + 1, round(time.time() - t0)           # L <= n - gmax - 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default="r2")
    ap.add_argument("--t", type=int, nargs="+", default=[9, 11, 13])
    ap.add_argument("--gmax", type=int, default=3)
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--count", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    t0 = time.time()
    j = json.loads((ROOT / "results/phase9/pattern_hunt.json").read_text())[a.key]
    r = int(a.key[1])
    centre, mirror = "centre" in a.key, "mirror" in a.key
    cands = j["period_free"][a.first:a.first + a.count]
    items = [(ci, c["pattern"], r, mirror, centre, t, a.gmax) for ci, c in enumerate(cands) for t in a.t]
    items.sort(key=lambda x: x[5])
    res = {}
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for ci, t, st, g, sec in pool.imap_unordered(job, items):
            res.setdefault(ci, {})[t] = (st, g)
    out = []
    for ci, c in enumerate(cands):
        row = res.get(ci, {})
        txt = ", ".join(f"t={t}: " + ("n" + (f" - {row[t][1]}" if row[t][1] else "") if row[t][0] == "ray" and row[t][1] <= a.gmax
                                      else (f"<= n - {row[t][1]}" if row[t][0] == "ray" else row[t][0])) for t in a.t if t in row)
        print(f"{a.first + ci:3d} " + " ".join(f"{k}={v}" for k, v in sorted(c["pattern"].items())) + "  ->  L: " + txt, flush=True)
        out.append({"pattern": c["pattern"], "result": {str(t): row[t] for t in row}})
    f = ROOT / "results/phase9/cand_pattern.json"
    old = json.loads(f.read_text()) if f.exists() else {}
    old[a.key + "_t" + "_".join(map(str, a.t))] = out
    atomic_write_json(f, old)
    print(f"done ({time.time() - t0:.0f} s)", flush=True)


if __name__ == "__main__":
    main()
