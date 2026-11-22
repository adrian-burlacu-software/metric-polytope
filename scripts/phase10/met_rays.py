#!/usr/bin/env python3
"""The cut orbit's neighbourhood = extreme rays of the metric cone MET_n (metricpoly/conecut.py).

  validate : n = 5, 6. Rays extracted from ALL vertices of m_n (vertices y with [0, y] an edge, i.e. y on an extreme
             ray) == all extreme rays of MET_n from cdd, as S_n-orbits; orbit sizes sum to the cdd ray count.
  candidates --n 8 : for each of Deza's 533 representatives x and each of its 128 switchings y, keep y if it lies on an
             extreme ray of MET_8 (exact rank test); canonicalise the ray under S_8; sum the orbit sizes
             (literature: 119,269,588 extreme rays [DFMV03, derived from their completeness proof]).
  time --n 8 : neighbour enumeration on Q_8 = MET_8 ∩ {sum = 1} for 100 random candidate ray orbits and all cut-ray
             orbits δ(S), |S| = 1..4 (per-orbit timeout); every neighbour completed and canonicalised; reports
             rays per orbit, seconds, and whether all neighbour orbits are candidates (closure so far).
Writes results/phase10/met_rays_<cmd>_n<n>.json. Seed 20261122.
"""
import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from metricpoly.core import pairs  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def _rays_of_vertex(args):
    n, D, nums = args
    from metricpoly.conecut import is_extreme_ray, normalise_sum, perm_key, perm_orbit_size
    pr = pairs(n)
    out = {}
    for s in range(1 << (n - 1)):
        side = [0] + [(s >> (v - 1)) & 1 for v in range(1, n)]
        y = [D - v if side[i] != side[j] else v for v, (i, j) in zip(nums, pr)]
        if not any(y):
            continue
        if is_extreme_ray(n, D, y):
            Dq, q = normalise_sum(n, D, y)
            k = perm_key(n, Dq, q)
            if k not in out:
                out[k] = (Dq, list(q), perm_orbit_size(n, Dq, q))
    return out


def extract(n, reps, workers):
    allr = {}
    with mp.Pool(workers) as pool:
        for part in pool.imap_unordered(_rays_of_vertex, [(n, D, list(nums)) for D, nums in reps], chunksize=4):
            allr.update(part)
    return allr


def cmd_validate(workers):
    from metricpoly.conecut import normalise_sum, perm_key, perm_orbit_size
    from metricpoly.dsl.prims import p_vertices
    from metricpoly.polyhedra import enumerate_cone_rays
    out = {}
    for n in (5, 6):
        cdd_rays = enumerate_cone_rays(n)
        cdd_keys = {}
        for r in cdd_rays:
            Dq, q = normalise_sum(n, 1, r.nums)
            cdd_keys.setdefault(perm_key(n, Dq, q), 0)
            cdd_keys[perm_key(n, Dq, q)] += 1
        sizes_ok = all(perm_orbit_size(n, *normalise_sum(n, 1, r.nums)) == cdd_keys[perm_key(n, *normalise_sum(n, 1, r.nums))]
                       for r in cdd_rays)
        ext = extract(n, [(x.D, x.nums) for x in p_vertices(n)], workers)
        out[f"n{n}"] = {"cdd_rays": len(cdd_rays), "cdd_ray_orbits": len(cdd_keys),
                        "extracted_ray_orbits": len(ext), "same_orbit_set": set(ext) == set(cdd_keys),
                        "orbit_sizes_match_cdd": sizes_ok,
                        "extracted_size_sum": int(sum(v[2] for v in ext.values()))}
    return out


def cmd_candidates(n, workers):
    from metricpoly import deza
    t = time.time()
    ext = extract(n, [(x.D, x.nums) for x in deza.load_ext(n)], workers)
    path = ROOT / "results" / "phase10" / f"met_ray_orbits_n{n}.json"
    atomic_write_json(path, {k: v for k, v in ext.items()})
    return {"ray_orbits": len(ext), "rays_total": int(sum(v[2] for v in ext.values())),
            "literature_rays": 119269588 if n == 8 else None, "seconds": round(time.time() - t, 1),
            "saved": str(path.relative_to(ROOT))}


def _walk_ray(args):
    n, key, D, nums = args
    from metricpoly.conecut import normalise_sum, perm_key, q_polytope
    Q = q_polytope(n)
    t = time.time()
    nb, nrays = Q.neighbours(D, tuple(nums))
    keys = set()
    nonv = 0
    for Dy, y in nb:
        if not Q.is_vertex(Dy, y):
            nonv += 1
            continue
        keys.add(perm_key(n, *normalise_sum(n, Dy, y)))
    return {"key": key, "tight": int(len(Q.tight(D, tuple(nums)))), "rays": nrays, "nbr_keys": sorted(keys),
            "nonvertex": nonv, "s": round(time.time() - t, 2)}


def cmd_time(n, workers, timeout):
    from metricpoly.conecut import normalise_sum, perm_key
    cand = json.loads((ROOT / "results" / "phase10" / f"met_ray_orbits_n{n}.json").read_text())
    rng = np.random.default_rng(20261122)
    keys = sorted(cand)
    pick = [keys[i] for i in rng.choice(len(keys), min(100, len(keys)), replace=False)]
    pr = pairs(n)
    cuts = []
    for s in range(1, n // 2 + 1):                     # cut rays δ(S), |S| = s
        v = [1 if (i < s) != (j < s) else 0 for i, j in pr]
        Dq, q = normalise_sum(n, 1, v)
        k = perm_key(n, Dq, q)
        cuts.append(k)
        cand.setdefault(k, (Dq, list(q), None))
    jobs = [(n, k, cand[k][0], cand[k][1]) for k in list(dict.fromkeys(cuts + pick))]
    res = {}
    t0 = time.time()
    with mp.Pool(workers) as pool:
        asy = {j[1]: pool.apply_async(_walk_ray, (j,)) for j in jobs}
        last = time.time()
        while asy:
            done = [k for k, a in asy.items() if a.ready()]
            for k in done:
                res[k] = asy.pop(k).get()
                last = time.time()
            if asy and len(asy) <= workers and time.time() - last > timeout:
                for k in asy:
                    res[k] = {"key": k, "flag": f"no result within {timeout:.0f} s"}
                asy.clear()
            if not done:
                time.sleep(0.5)
        pool.terminate()
    ok = [r for r in res.values() if "flag" not in r]
    outside = sorted({k for r in ok for k in r["nbr_keys"] if k not in cand})
    return {"walked": len(ok), "flagged": [r for r in res.values() if "flag" in r],
            "cut_rays": {k: res[k] for k in cuts},
            "rays_mean": float(np.mean([r["rays"] for r in ok])), "rays_max": int(max(r["rays"] for r in ok)),
            "s_mean": float(np.mean([r["s"] for r in ok])), "s_max": float(max(r["s"] for r in ok)),
            "neighbour_orbits_outside_candidates": len(outside), "outside_examples": outside[:5],
            "nonvertex_neighbours": int(sum(r["nonvertex"] for r in ok)), "wall_s": round(time.time() - t0, 1)}


def _run_jobs(jobs, workers, stuck_timeout, part, hard_cap=None):
    """Run _walk_ray jobs, appending each result to `part` (JSONL, resumable). A job is flagged when only stuck jobs
    remain and nothing finished for stuck_timeout s, or (hard_cap) when it ran longer than hard_cap s in total."""
    done = {}
    if part.exists():
        for line in part.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done[r["key"]] = r
    todo = [j for j in jobs if j[1] not in done]
    if not todo:
        return done
    t0 = time.time()
    with mp.Pool(min(workers, len(todo))) as pool, open(part, "a", encoding="utf-8", newline="\n") as f:
        asy = {j[1]: pool.apply_async(_walk_ray, (j,)) for j in todo}
        last = time.time()
        while asy:
            fin = [k for k, a in asy.items() if a.ready()]
            for k in fin:
                r = asy.pop(k).get()
                done[k] = r
                f.write(json.dumps(r) + "\n")
                f.flush()
                last = time.time()
            over = hard_cap is not None and time.time() - t0 > hard_cap
            stuck = hard_cap is None and asy and len(asy) <= workers and time.time() - last > stuck_timeout
            if asy and (over or stuck):
                for k in asy:
                    done[k] = {"key": k, "flag": f"no result within {hard_cap or stuck_timeout:.0f} s"}
                    f.write(json.dumps(done[k]) + "\n")
                asy.clear()
            if not fin:
                time.sleep(1.0)
            if time.time() - t0 > 60 and int(time.time() - t0) % 300 < 1:
                print(f"  ... {len(done)} done, {len(asy)} running, {time.time() - t0:.0f}s", flush=True)
        pool.terminate()
    return done


PHASE_A_ONLY = {"on": False}


def cmd_closure(n, workers, timeout, cut_cap):
    """Closure check of the candidate ray orbits of MET_n (Q_n's vertex graph) with the Balinski skip.
    Phase A: every non-cut ray orbit (stuck timeout). Phase B: the cut-ray orbits δ(S), |S| >= 2 (hard cap each,
    in parallel). The star-cut orbit δ({v}) is NOT walked: it is skipped by Balinski's theorem if every other orbit
    closes (Q_n has dimension C(n,2) - 1; the skipped set has n vertices < C(n,2) - 1)."""
    from math import comb
    from metricpoly.conecut import normalise_sum, perm_key
    cand = json.loads((ROOT / "results" / "phase10" / f"met_ray_orbits_n{n}.json").read_text())
    pr = pairs(n)
    cutkeys = {}
    for s in range(1, n // 2 + 1):
        v = [1 if (i < s) != (j < s) else 0 for i, j in pr]
        Dq, q = normalise_sum(n, 1, v)
        k = perm_key(n, Dq, q)
        cutkeys[s] = k
        assert k in cand, f"cut ray |S|={s} missing from the candidates"
    ck = ROOT / "checkpoints" / "phase10" / f"met_closure_n{n}"
    ck.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    others = [(n, k, v[0], v[1]) for k, v in cand.items() if k not in cutkeys.values()]
    print(f"[MET_{n} closure] {len(cand)} candidate ray orbits; phase A: {len(others)} non-cut orbits", flush=True)
    A = _run_jobs(others, workers, timeout, ck / "phaseA.jsonl")
    print(f"[MET_{n} closure] phase A done: {sum(1 for r in A.values() if 'flag' not in r)} walked, "
          f"{sum(1 for r in A.values() if 'flag' in r)} flagged, {time.time() - t0:.0f}s", flush=True)
    if PHASE_A_ONLY["on"]:
        return {"phase": "A only", "walked": sum(1 for r in A.values() if "flag" not in r),
                "flagged": [k for k, r in A.items() if "flag" in r],
                "outside_candidates": sorted({k for r in A.values() if "flag" not in r for k in r["nbr_keys"] if k not in cand}),
                "seconds": round(time.time() - t0, 1)}
    cut_jobs = [(n, cutkeys[s], cand[cutkeys[s]][0], cand[cutkeys[s]][1]) for s in cutkeys if s >= 2]
    print(f"[MET_{n} closure] phase B: cut rays |S| = 2..{n // 2} (cap {cut_cap:.0f} s each, in parallel)", flush=True)
    B = _run_jobs(cut_jobs, len(cut_jobs), timeout, ck / "phaseB.jsonl", hard_cap=cut_cap)
    allr = {**A, **B}
    walked = {k: r for k, r in allr.items() if "flag" not in r}
    flagged = [k for k, r in allr.items() if "flag" in r]
    outside = sorted({k for r in walked.values() for k in r["nbr_keys"] if k not in cand})
    sizes = {k: v[2] for k, v in cand.items()}
    skipped = [cutkeys[1]] + flagged
    skipped_vertices = sum(sizes[k] for k in skipped)
    dimQ = comb(n, 2) - 1
    proof = (not outside) and skipped_vertices < dimQ
    out = {"n": n, "candidate_ray_orbits": len(cand), "rays_total": int(sum(sizes.values())),
           "walked_orbits": len(walked), "flagged_orbits": flagged, "skipped_orbits": skipped,
           "skipped_vertices": int(skipped_vertices), "dim_Q": dimQ,
           "balinski_skip_valid": skipped_vertices < dimQ,
           "neighbour_orbits_outside_candidates": len(outside), "outside_examples": outside[:10],
           "nonvertex_neighbours": int(sum(r["nonvertex"] for r in walked.values())),
           "cut_rays": {s: {kk: vv for kk, vv in allr[k].items() if kk != "nbr_keys"} for s, k in cutkeys.items() if k in allr},
           "candidate_set_is_all_rays_of_MET": proof, "seconds": round(time.time() - t0, 1)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["validate", "candidates", "time", "closure"])
    ap.add_argument("--cut-cap", type=float, default=7200)
    ap.add_argument("--phase-a-only", action="store_true")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--workers", type=int, default=19)
    ap.add_argument("--timeout", type=float, default=600)
    a = ap.parse_args()
    PHASE_A_ONLY["on"] = a.phase_a_only
    out = {"validate": lambda: cmd_validate(a.workers), "candidates": lambda: cmd_candidates(a.n, a.workers),
           "time": lambda: cmd_time(a.n, a.workers, a.timeout),
           "closure": lambda: cmd_closure(a.n, a.workers, a.timeout, a.cut_cap)}[a.cmd]()
    atomic_write_json(ROOT / "results" / "phase10" / f"met_rays_{a.cmd}{'_phaseA' if a.phase_a_only else ''}_n{a.n}.json", out)
    print(json.dumps(out, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
