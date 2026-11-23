#!/usr/bin/env python3
"""Table of the most degenerate orbits of Deza's m_9 list (candidates for the 20 orbits whose adjacency Deza et al.
did not compute; the page does not say which 20, so "hard" here means highest incidence).

For every listed orbit (data/deza/orbits9/orbits9.npz, from Orbits.zip): the incidence (number of tight triangle and
perimeter inequalities) is recomputed exactly and compared with the file's column. For the top --top orbits:
  excess        = incidence - 36 (rows of the tangent cone minus its dimension; the cone is full-dimensional)
  stab_Sn       = |Aut_{S_9}(x)| (bliss)
  switch_fix    = number of switchings S (out of 256) whose image of x is S_9-equivalent to x
  stabiliser    = switch_fix * stab_Sn  (stabiliser of x in switchings ⋊ S_9)
  orbit_size    = 256 * 9! / stabiliser
Calibration, for a rough size estimate of each tangent cone: (incidence, ray count) pairs measured exactly at m_8
(results/phase10/closure_n8 batches; MET_8 for the cut) and from the m_9 timing sample (results/phase10/time_walk.json).

Usage: python -u scripts/phase10/hard_orbits9.py --top 40
Writes results/phase10/hard_orbits_n9.json.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase10"))

from metricpoly import adjdec  # noqa: E402
from metricpoly.core import ineq_matrix, pairs  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402

N = 9


def switched(D, nums, S, pr):
    return tuple((D - v) if ((i in S) != (j in S)) else v for v, (i, j) in zip(nums, pr))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=40)
    a = ap.parse_args()
    t0 = time.time()
    z = np.load(ROOT / "data/deza/orbits9/orbits9.npz")
    co, de, inc = z["coords"].astype(np.int64), z["den"].astype(np.int64), z["incidence"].astype(np.int64)
    A, b = ineq_matrix(N)
    pr = pairs(N)
    # exact incidence for every orbit, in chunks
    tight = np.empty(len(de), dtype=np.int64)
    for s in range(0, len(de), 50000):
        sl = b[None, :] * de[s:s + 50000, None] - co[s:s + 50000] @ A.T
        if (sl < 0).any():
            raise RuntimeError(f"infeasible row near {s}")
        tight[s:s + 50000] = (sl == 0).sum(axis=1)
    mism = int((tight != inc).sum())
    print(f"incidence recomputed for {len(de)} orbits, {mism} mismatches with the file ({time.time() - t0:.0f} s)",
          flush=True)
    hist = {int(k): int(v) for k, v in zip(*np.unique(tight, return_counts=True))}
    order = np.argsort(-tight, kind="stable")[:a.top]
    rows = []
    for r in order:
        D, nums = int(de[r]), tuple(int(v) for v in co[r])
        F = []
        stab_sn = adjdec.group_order(N, [nums])
        key0 = adjdec.fix_key(N, F, (D, nums))
        fix = 0
        for bits in range(256):
            S = {i for i in range(8) if bits >> i & 1}
            if adjdec.fix_key(N, F, (D, switched(D, nums, S, pr))) == key0:
                fix += 1
        stab = fix * stab_sn
        rows.append({"row": int(r), "D": D, "incidence": int(tight[r]), "excess": int(tight[r]) - 36,
                     "stab_Sn": stab_sn, "switch_fix": fix, "stabiliser": stab,
                     "orbit_size": 256 * math.factorial(N) // stab, "point": list(nums)})
    # calibration
    cal8 = []
    from metricpoly import deza
    reps = list(deza.load_ext(8))
    A8, b8 = ineq_matrix(8)
    for f in sorted((ROOT / "checkpoints/phase10/closure_n8").glob("batch_*.json")):
        rec = json.loads(f.read_text())
        for rr, k in rec["rays"].items():
            p = reps[int(rr)]
            t = int(((b8 * p.D - A8 @ np.array(p.nums, dtype=np.int64)) == 0).sum())
            cal8.append((t, int(k)))
    cal8.append((168, 119269588))                                  # cut vertex of m_8: tangent cone MET_8
    tw = json.loads((ROOT / "results/phase10/time_walk.json").read_text())
    cal9 = [(x["tight"], x["rays"]) for x in tw["rows"]]
    out = {"orbits": len(de), "incidence_mismatches": mism, "incidence_histogram_top": dict(sorted(hist.items())[-25:]),
           "top": rows, "calibration_m8_incidence_rays": sorted(cal8), "calibration_m9_sample_incidence_rays": sorted(cal9),
           "seconds": round(time.time() - t0, 1)}
    atomic_write_json(ROOT / "results/phase10/hard_orbits_n9.json", out)
    print(f"{'row':>8} {'D':>3} {'inc':>4} {'exc':>4} {'|Aut S9|':>9} {'sw':>4} {'stab':>9} {'orbit size':>12}")
    for x in rows:
        print(f"{x['row']:>8} {x['D']:>3} {x['incidence']:>4} {x['excess']:>4} {x['stab_Sn']:>9} {x['switch_fix']:>4} "
              f"{x['stabiliser']:>9} {x['orbit_size']:>12}")
    print("histogram (incidence: orbits), top:", out["incidence_histogram_top"])
    print("m8 calibration, top 12 by incidence:", sorted(cal8)[-12:])
    print("m9 sample, top 8:", sorted(cal9)[-8:])
    print(f"done in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
