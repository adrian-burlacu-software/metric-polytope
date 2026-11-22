#!/usr/bin/env python3
"""Neighbours of the cut rays δ(S) of Q_n = MET_n ∩ {sum = 1} by recursive adjacency decomposition
(metricpoly.adjdec) under Stab_{S_n}(δ(S)), instead of one monolithic Normaliz call.

For each |S|: orbit representatives of the extreme rays of the tangent cone at δ(S), their total count (sum of orbit
sizes), each followed to its neighbour in Q_n (exact vertex check), S_n-canonicalised (conecut.perm_key) and compared
with the candidate ray orbits results/phase10/met_ray_orbits_n{n}.json.

--validate: also compute the cone directly (cdd) and require identical ray count and identical neighbour orbit set.
Usage: python -u scripts/phase10/rec_cut_rays.py --n 7 --sizes 3 2 1 --validate
Writes results/phase10/rec_cut_rays_n{n}.json (one entry per |S|).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from metricpoly import adjdec  # noqa: E402
from metricpoly.conecut import normalise_sum, perm_key, q_polytope  # noqa: E402
from metricpoly.core import pairs  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def cut_ray(n, s):
    return normalise_sum(n, 1, [1 if (i < s) != (j < s) else 0 for i, j in pairs(n)])


def q_neighbour_keys(n, Q, D, x, rays):
    keys, nonv = set(), 0
    H = adjdec.HPoly(Q.A, Q.b)
    for r in rays:
        y = H.step(D, x, r)
        if not Q.is_vertex(*y):
            nonv += 1
            continue
        keys.add(perm_key(n, *normalise_sum(n, *y)))
    return keys, nonv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--sizes", nargs="+", type=int, default=[4, 3, 2, 1])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--workers", type=int, default=0, help="0 = sequential top level; >0 = parallel (checkpointed)")
    a = ap.parse_args()
    n = a.n
    Q = q_polytope(n)
    cand_path = ROOT / "results" / "phase10" / f"met_ray_orbits_n{n}.json"
    cand = set(json.loads(cand_path.read_text())) if cand_path.exists() else None
    outp = ROOT / "results" / "phase10" / f"rec_cut_rays_n{n}.json"
    out = json.loads(outp.read_text()) if outp.exists() and not a.validate else {}
    for s in a.sizes:
        if str(s) in out:
            continue
        D, x = cut_ray(n, s)
        T = Q.tight(D, x)
        F = [tuple(int(v) for v in x)]
        cone_dim = Q.m - 1                                     # dim Q_n (the sum = 1 hyperplane)
        t0 = time.time()
        info = {}
        if a.workers:
            ck = ROOT / "checkpoints" / "phase10" / f"rec_cut_n{n}" / f"S{s}.jsonl"
            ck.parent.mkdir(parents=True, exist_ok=True)
            orbs, st, info = adjdec.decompose_parallel(n, Q.A[T], F, cone_dim, a.workers, ck,
                                                        log=lambda m: print(f"  [n={n} |S|={s}] {m}", flush=True))
        else:
            ctx = adjdec.Ctx(threads=1, tag=f"n{n}S{s}")
            orbs = adjdec.solve_cone(n, Q.A[T], F, cone_dim, 0, ctx, force_recurse=True)
            st = ctx.stats
        secs = time.time() - t0
        total = sum(sz for _, sz in orbs.values())
        reps = [p[1] for p, _ in orbs.values()]
        keys, nonv = q_neighbour_keys(n, Q, D, x, reps)
        r = {"tight": int(len(T)), "group_order": adjdec.group_order(n, F), "ray_orbits": len(orbs),
             "cone_rays": total, "neighbour_orbits": len(keys), "nonvertex": nonv, "calls": st.calls,
             "max_depth": st.max_depth, **info, "seconds": round(secs, 1)}
        if cand is not None:
            r["outside_candidates"] = sorted(k for k in keys if k not in cand)
        if a.validate:
            direct = adjdec.cone_rays_cdd(Q.A[T])
            dkeys, _ = q_neighbour_keys(n, Q, D, x, direct)
            r["direct_cone_rays"] = len(direct)
            r["same_count"] = len(direct) == total
            r["same_neighbour_orbits"] = dkeys == keys
        out[str(s)] = r
        atomic_write_json(outp, out)
        print(f"[n={n} |S|={s}] " + json.dumps({k: v for k, v in r.items() if k != "outside_candidates"})
              + (f" outside {len(r['outside_candidates'])}" if "outside_candidates" in r else ""), flush=True)


if __name__ == "__main__":
    main()
