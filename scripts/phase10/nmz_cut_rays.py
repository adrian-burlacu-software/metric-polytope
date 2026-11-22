#!/usr/bin/env python3
"""Neighbours of the cut rays δ(S) of MET_n in Q_n = MET_n ∩ {sum = 1}, using Normaliz (exact, multi-threaded) for the
extreme rays of the tangent cone at δ(S); each ray followed to the neighbouring vertex in exact arithmetic, completed,
canonicalised under S_n (metricpoly.conecut.perm_key) and compared with the candidate ray orbits
(results/phase10/met_ray_orbits_n{n}.json). Normaliz binary: tools/normaliz-3.11.1 (official Windows64 release,
sha256 22bf4417...b02a3 verified against the GitHub asset digest).
Validated against cdd on the cut rays of MET_6 and MET_7 (same neighbour orbit sets).
Usage: python -u scripts/phase10/nmz_cut_rays.py --n 8 --sizes 4 3 2 1 [--threads 8] [--validate]
Writes results/phase10/nmz_cut_rays_n{n}.json (one entry per |S|, written as soon as it finishes).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from metricpoly.conecut import normalise_sum, perm_key, q_polytope  # noqa: E402
from metricpoly.core import pairs  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402

NMZ = ROOT / "tools" / "normaliz-3.11.1" / "normaliz-3.11.1" / "normaliz.exe"
WORK = ROOT / "checkpoints" / "phase10" / "nmz"


def cut_ray(n, s):
    v = [1 if (i < s) != (j < s) else 0 for i, j in pairs(n)]
    return normalise_sum(n, 1, v)


def nmz_extreme_rays(A_T, tag, threads):
    """Extreme rays of the cone {d : A_T d <= 0} via Normaliz (input as inequalities -A_T d >= 0)."""
    WORK.mkdir(parents=True, exist_ok=True)
    m = A_T.shape[1]
    inp = WORK / f"{tag}.in"
    rows = "\n".join(" ".join(str(-int(v)) for v in r) for r in A_T)
    inp.write_text(f"amb_space {m}\ninequalities {len(A_T)}\n{rows}\nExtremeRays\n", encoding="ascii")
    t = time.time()
    cp = subprocess.run([str(NMZ), "-c", f"-x={threads}", str(inp)], capture_output=True, text=True, cwd=WORK)
    if cp.returncode != 0:
        raise RuntimeError(f"normaliz failed: {cp.stderr[-500:]}")
    lines = (WORK / f"{tag}.out").read_text().splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().endswith("extreme rays:"):
            k = int(ln.split()[0])
            rays = [[int(v) for v in lines[i + 1 + t_].split()] for t_ in range(k)]
            return rays, time.time() - t
    raise RuntimeError("no extreme rays section in normaliz output")


def neighbours_via_nmz(n, D, x, threads, tag):
    Q = q_polytope(n)
    T = Q.tight(D, x)
    rays, secs = nmz_extreme_rays(Q.A[T], tag, threads)
    s = Q.slacks(D, x)
    nonT = np.nonzero(s != 0)[0]
    xs = [Fraction(int(v), D) for v in x]
    keys, nonv = set(), 0
    for d in rays:
        best = None
        for i in nonT:
            ad = sum(int(Q.A[i, t]) * d[t] for t in range(Q.m) if Q.A[i, t])
            if ad > 0:
                ti = Fraction(int(s[i]), D * ad)
                if best is None or ti < best:
                    best = ti
        y = [xs[t] + best * d[t] for t in range(Q.m)]
        Dy = 1
        for f in y:
            Dy = Dy * f.denominator // np.gcd(Dy, f.denominator)
        ny = tuple(int(f * Dy) for f in y)
        if not Q.is_vertex(int(Dy), ny):
            nonv += 1
            continue
        keys.add(perm_key(n, *normalise_sum(n, int(Dy), ny)))
    return {"tight": int(len(T)), "cone_rays": len(rays), "normaliz_s": round(secs, 1), "nbr_orbits": sorted(keys),
            "nonvertex": nonv}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--sizes", nargs="+", type=int, default=[4, 3, 2, 1])
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--validate", action="store_true", help="compare with cdd neighbours (small n)")
    ap.add_argument("--flagged", action="store_true",
                    help="also walk the ray orbits flagged in the cdd phase-A run (checkpoints/phase10/met_closure_n*/phaseA.jsonl)")
    a = ap.parse_args()
    n = a.n
    cand = set(json.loads((ROOT / "results" / "phase10" / f"met_ray_orbits_n{n}.json").read_text()))
    outp = ROOT / "results" / "phase10" / f"nmz_cut_rays_n{n}.json"
    out = json.loads(outp.read_text()) if outp.exists() else {}
    for s in a.sizes:
        if str(s) in out and not a.validate:
            continue
        D, x = cut_ray(n, s)
        t0 = time.time()
        r = neighbours_via_nmz(n, D, x, a.threads, f"n{n}_S{s}")
        r["outside_candidates"] = [k for k in r["nbr_orbits"] if k not in cand]
        r["seconds"] = round(time.time() - t0, 1)
        if a.validate:
            Q = q_polytope(n)
            nb, _ = Q.neighbours(D, x)
            ck = {perm_key(n, *normalise_sum(n, Dy, y)) for Dy, y in nb}
            r["cdd_same_neighbour_orbits"] = ck == set(r["nbr_orbits"])
        out[str(s)] = {k: v for k, v in r.items() if k != "nbr_orbits"} | {"neighbour_orbits": len(r["nbr_orbits"])}
        atomic_write_json(outp, out)
        print(f"[n={n} |S|={s}] tight {r['tight']}, cone rays {r['cone_rays']}, normaliz {r['normaliz_s']} s, "
              f"neighbour orbits {len(r['nbr_orbits'])}, outside candidates {len(r['outside_candidates'])}"
              + (f", cdd agrees {r['cdd_same_neighbour_orbits']}" if a.validate else ""), flush=True)
    if a.flagged:
        cand_full = json.loads((ROOT / "results" / "phase10" / f"met_ray_orbits_n{n}.json").read_text())
        part = ROOT / "checkpoints" / "phase10" / f"met_closure_n{n}" / "phaseA.jsonl"
        flagged = [json.loads(l)["key"] for l in part.read_text(encoding="utf-8").splitlines()
                   if l.strip() and "flag" in json.loads(l)]
        for i, key in enumerate(flagged):
            tag = f"flag:{key}"
            if tag in out:
                continue
            D, x = cand_full[key][0], tuple(cand_full[key][1])
            t0 = time.time()
            r = neighbours_via_nmz(n, D, x, a.threads, f"n{n}_F{i}")
            r["outside_candidates"] = [k for k in r["nbr_orbits"] if k not in cand]
            r["seconds"] = round(time.time() - t0, 1)
            out[tag] = {k: v for k, v in r.items() if k != "nbr_orbits"} | {"neighbour_orbits": len(r["nbr_orbits"])}
            atomic_write_json(outp, out)
            print(f"[n={n} flagged {i + 1}/{len(flagged)}] tight {r['tight']}, cone rays {r['cone_rays']}, "
                  f"normaliz {r['normaliz_s']} s, outside candidates {len(r['outside_candidates'])}", flush=True)


if __name__ == "__main__":
    main()
