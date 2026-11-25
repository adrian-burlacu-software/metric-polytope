#!/usr/bin/env python3
"""Checks and complete small cases for the locality invariant (scripts/phase9/locality.py).

1. Validation against the exact rank test: on every stored non-ray (round 18 pools, k = 6..11) the closure at s = k
   must NOT end with one class; on every ray it must. (At s = k the closure is the full tight system.)
2. Complete lists: every extreme ray of MET_k with all distances positive, k = 5..8, up to permutation (all valid
   switchings of every vertex of m_5..m_8; the lists of m_n, n <= 8, are complete). Locality distribution.
3. The 7 sampled vertices of m_10 (random walks), every valid switching.
Output results/phase9/locality_checks.json and .md.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

import family12 as F  # noqa: E402
from locality import locality  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def _loc(args):
    k, e = args
    return k, locality(k, F.metric(k, e).tolist())


def _val(args):
    k, e = args
    return k, F.check(k, e)["ray"], locality(k, F.metric(k, e).tolist())


def main():
    t0 = time.time()
    W = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    out, md = {}, ["# Locality: validation and complete small cases", ""]
    fam = ROOT / "results/phase9/family12"
    with mp.get_context("spawn").Pool(W) as pool:
        # 1. validation
        items = []
        for k in (6, 7, 8, 9):
            for name in ("public", "heldout"):
                items += [(r["k"], [tuple(t) for t in r["edges"]]) for r in json.loads((fam / f"nonrays_{name}_k{k}.json").read_text())]
        items += [(r["k"], [tuple(t) for t in r["edges"]])
                  for r in json.loads((ROOT / "phase9/round_18/breaker/pool_nonrays.json").read_text())]
        for k in (5, 6, 7, 8):
            items += [(r["k"], [tuple(t) for t in r["edges"]]) for r in json.loads((fam / f"rays_k{k}.json").read_text())]
        agree, tab = 0, Counter()
        for k, ray, L in pool.imap_unordered(_val, items, chunksize=32):
            ok = (L is not None) == bool(ray)
            agree += ok
            tab[(k, bool(ray), L is not None)] += 1
            assert ok, (k, ray, L)
        out["validation"] = {"graphs": len(items), "agree": agree,
                             "non_rays": sum(v for (k, r, c), v in tab.items() if not r),
                             "rays": sum(v for (k, r, c), v in tab.items() if r)}
        print(f"validation: {agree} of {len(items)} agree with the rank test ({time.time() - t0:.0f} s)", flush=True)
        md += ["## 1. Validation", "",
               f"{len(items)} weighted graphs on 5 to 11 nodes ({out['validation']['rays']} rays, "
               f"{out['validation']['non_rays']} non-rays by the exact rank test): the closure at s = k ends with one class "
               f"exactly for the rays, in all {agree} cases.", ""]
        # 2. complete lists for MET_5..MET_8
        from vertex_structure import load_set
        pts = [x for _k, x in load_set("m8", 0, 0) if x.D > 1]
        allr = [r for part in pool.imap_unordered(F._rays_of, pts, chunksize=4) for r in part]
        uniq = F.dedupe(allr)
        print(f"{len(uniq)} rays of MET_5..8 up to permutation ({time.time() - t0:.0f} s)", flush=True)
        dist = {}
        for k, L in pool.imap_unordered(_loc, uniq, chunksize=16):
            dist.setdefault(k, Counter())[L] += 1
        out["complete"] = {str(k): {str(L): v for L, v in sorted(c.items())} for k, c in sorted(dist.items())}
        md += ["## 2. All extreme rays of MET_k with positive distances, up to permutation", "",
               "| k | rays | L = 4 | 5 | 6 | 7 | 8 | max L |", "|---|---|---|---|---|---|---|---|"]
        for k, c in sorted(dist.items()):
            assert None not in c
            md.append(f"| {k} | {sum(c.values())} | " + " | ".join(str(c.get(s, "")) for s in range(4, 9)) + f" | {max(c)} |")
            print(f"MET_{k}: {dict(sorted(c.items()))}", flush=True)
        md.append("")
        # 3. m_10 samples
        rows = json.loads((ROOT / "results/phase9/sample_reach_n10.json").read_text())["rows"]
        pts10 = []
        for r in rows:
            n, D, nums = r["key"].split("|")
            pts10.append(Point.make(int(n), int(D), [int(v) for v in nums.split(",")]))
        res10 = []
        for x, part in zip(pts10, pool.imap(F._rays_of, pts10)):
            u = F.dedupe(part)
            Ls = Counter(L for _k, L in pool.imap_unordered(_loc, u, chunksize=4))
            res10.append({"D": x.D, "rays": len(u), "L": {str(L): v for L, v in sorted(Ls.items())}})
            print(f"m_10 sample D = {x.D}: {len(u)} rays, L {dict(sorted(Ls.items()))} ({time.time() - t0:.0f} s)", flush=True)
        out["m10_samples"] = res10
        md += ["## 3. Seven sampled vertices of m_10 (all switchings that give rays)", "", "| D | rays | L values (count) |", "|---|---|---|"]
        md += [f"| {r['D']} | {r['rays']} | {r['L']} |" for r in res10]
    out["seconds"] = round(time.time() - t0, 1)
    atomic_write_json(ROOT / "results/phase9/locality_checks.json", out)
    (ROOT / "results/phase9/locality_checks.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"done ({out['seconds']} s)", flush=True)


if __name__ == "__main__":
    main()
