#!/usr/bin/env python3
"""Side experiment: elliptope distance as a feature for reachable vs unreachable orbits (Phase 9 state after round 17).

For an orbit representative x of m_n, Y = J - 2X (Y_ii = 1, Y_ij = 1 - 2 x_ij). lambda_min(Y) >= 0 iff x is in the
elliptope image; lambda_min is invariant under node permutations and switchings (Y -> D Y D), so it is an orbit feature.
Floats (numpy eigvalsh); whenever |lambda_min| < 1e-9 the sign is decided exactly (integer characteristic polynomial of
D*Y: positive semidefinite iff its coefficients alternate in sign).

Targets: all orbits of m_7 and m_8 and the 1,000 sampled m_9 orbits of the judge; unreached ids from
results/phase9/unreached_targets.json. Output results/phase9/elliptope.json and .md.
"""
from __future__ import annotations

import json
import statistics as st
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

from metricpoly import core  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402
from judge import targets  # noqa: E402


def ymat_int(x):
    """D * Y as an integer matrix."""
    n, D = x.n, x.D
    M = [[D] * n for _ in range(n)]
    for (i, j), v in zip(core.pairs(n), x.nums):
        M[i][j] = M[j][i] = D - 2 * v
    return M


def exact_sign(M):
    """Sign of lambda_min of the integer symmetric matrix M: 0 if PSD and singular, +1 if PD, -1 otherwise."""
    import sympy
    n = len(M)
    co = sympy.Matrix(M).charpoly().all_coeffs()          # t^n + c1 t^(n-1) + ...
    psd = all((-1) ** k * int(c) >= 0 for k, c in enumerate(co))
    if not psd:
        return -1
    return 1 if int(co[-1]) != 0 else 0


def stats(v):
    return {"count": len(v), "mean": round(st.mean(v), 4), "median": round(st.median(v), 4),
            "min": round(min(v), 4), "max": round(max(v), 4)} if v else {"count": 0}


def auc(a, b):
    """P(random a < random b) + half ties: 0.5 = no separation."""
    if not a or not b:
        return None
    b_ = np.sort(np.array(b))
    lo = np.searchsorted(b_, a, side="left")
    hi = np.searchsorted(b_, a, side="right")
    return round(float(((len(b_) - hi) + 0.5 * (hi - lo)).sum() / (len(a) * len(b_))), 4)


def main():
    t0 = time.time()
    un = {(r["n"], r["id"]) for r in json.loads((ROOT / "results/phase9/unreached_targets.json").read_text())}
    rows, exact_used = [], 0
    for n, o, x in targets():
        M = ymat_int(x)
        lam = float(np.linalg.eigvalsh(np.array(M, dtype=float) / x.D)[0])
        if abs(lam) < 1e-9:
            exact_used += 1
            s = exact_sign(M)
            lam = 0.0 if s == 0 else lam
            assert (s > 0) == (lam > 0) and (s < 0) == (lam < 0), (n, o, lam, s)
        rows.append({"n": n, "id": o, "D": x.D, "lam": lam, "lam_over_n": lam / n, "reached": (n, o) not in un})
    out = {"exact_rechecks": exact_used, "per_n": {}}
    md = ["# Elliptope distance vs reachability (Phase 9 state after round 17)", "",
          "Y = J - 2X; lam = lambda_min(Y); lam >= 0 iff the point is in the elliptope. Groups: reached / unreached by "
          "the accepted rules.", ""]
    for n in (7, 8, 9):
        R = [r for r in rows if r["n"] == n]
        re_ = [r["lam"] for r in R if r["reached"]]
        ur = [r["lam"] for r in R if not r["reached"]]
        byD = defaultdict(lambda: ([], []))
        for r in R:
            byD[r["D"]][0 if r["reached"] else 1].append(r["lam"])
        # stratified AUC: pairs (unreached, reached) with the same denominator only
        num = den = 0.0
        for D, (a, b) in byD.items():
            if a and b:
                num += auc(b, a) * len(a) * len(b)
                den += len(a) * len(b)
        o = {"orbits": len(R), "reached": stats(re_), "unreached": stats(ur),
             "reached_over_n": stats([v / n for v in re_]), "unreached_over_n": stats([v / n for v in ur]),
             "in_elliptope": {"reached": sum(1 for v in re_ if v >= 0), "unreached": sum(1 for v in ur if v >= 0)},
             "auc_unreached_below_reached": auc(ur, re_),
             "auc_same_denominator": round(num / den, 4) if den else None, "same_denominator_pairs": int(den),
             "most_negative_reached": sorted((r for r in R if r["reached"]), key=lambda r: r["lam"])[:5],
             "least_negative_unreached": sorted((r for r in R if not r["reached"]), key=lambda r: -r["lam"])[:5],
             "by_denominator": {str(D): {"reached": stats(a), "unreached": stats(b)} for D, (a, b) in sorted(byD.items())}}
        out["per_n"][str(n)] = o
        md += [f"## n = {n}: {len(R)} orbits, {len(re_)} reached, {len(ur)} unreached", "",
               "| group | count | mean | median | min | max | in elliptope |", "|---|---|---|---|---|---|---|"]
        for name, s, k in (("reached", o["reached"], "reached"), ("unreached", o["unreached"], "unreached")):
            if s["count"]:
                md.append(f"| {name} | {s['count']} | {s['mean']} | {s['median']} | {s['min']} | {s['max']} | "
                          f"{o['in_elliptope'][k]} |")
        md += ["", f"P(unreached orbit has smaller lam than reached orbit): overall {o['auc_unreached_below_reached']}, "
                   f"same denominator only {o['auc_same_denominator']} ({o['same_denominator_pairs']} pairs). 0.5 = no "
                   f"separation.", "",
               "| D | reached | median | range | unreached | median | range |", "|---|---|---|---|---|---|---|"]
        for D, (a, b) in sorted(byD.items()):
            sa, sb = stats(a), stats(b)
            fa = f"{sa['count']} | {sa['median']} | {sa['min']} .. {sa['max']}" if a else "0 | | "
            fb = f"{sb['count']} | {sb['median']} | {sb['min']} .. {sb['max']}" if b else "0 | | "
            md.append(f"| {D} | {fa} | {fb} |")
        md.append("")
        print(f"n = {n}: reached {o['reached']} unreached {o['unreached']} AUC {o['auc_unreached_below_reached']} "
              f"same-D {o['auc_same_denominator']}", flush=True)
    out["rows"] = rows
    out["seconds"] = round(time.time() - t0, 1)
    atomic_write_json(ROOT / "results/phase9/elliptope.json", out)
    (ROOT / "results/phase9/elliptope.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"exact rechecks {exact_used}; {out['seconds']} s", flush=True)


if __name__ == "__main__":
    main()
