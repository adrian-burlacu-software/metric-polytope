#!/usr/bin/env python3
"""Cap-lemma LPs for m_9 against the SMAPO CUT_9 facet classes (164,506 classes, "description possibly complete").

Per class, in parallel and checkpointed (one JSONL line per class), with exact arithmetic throughout:
  1. Facet check: the inequality is valid on all 256 cuts, and its tight cuts have affine rank 35.
  2. Class size: (number of switchings ⋊ S_9 images) = 2^8 * (facets through the zero cut) / roots. The facets through
     the zero cut are the switchings by the roots, counted by S_9-orbit sizes (bliss). The sum over all classes is
     compared with the stated total 12,246,651,158,320. SMAPO's statistics file is corrupt on the server (gzip CRC
     error, same bytes on 3 downloads), so per-class sizes are not compared.
  3. LP: maximise a·x over m_9 (cdd gmp), with an exact dual certificate. If the max is <= rhs the cap is empty.
     Otherwise the optimum is checked exactly to be a vertex of m_9, canonicalised (canon_large, bliss), and compared
     with Deza's list keys (checkpoints/verify_n9_list).
An optimum that is NOT in Deza's list disproves the list's completeness unconditionally (it is a vertex of m_9).
If every optimum is listed, then together with the closure walk of all non-cut orbits (not yet run at n = 9) the cap
lemma gives: Deza's m_9 list is complete IF the CUT_9 facet list is complete.

Usage: python -u scripts/phase10/cap_lemma_lp9.py --workers 18 [--limit N]
Checkpoint: checkpoints/phase10/cap_lemma_n9.jsonl. Summary: results/phase10/cap_lemma_n9.json.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import sys
import time
from fractions import Fraction
from multiprocessing import get_context
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase10"))

from metricpoly.jobs import atomic_write_json  # noqa: E402

N = 9
TOTAL = 12246651158320
CK = ROOT / "checkpoints" / "phase10" / "cap_lemma_n9.jsonl"


def read_classes():
    with gzip.open(ROOT / "data" / "smapo" / "raw" / "cut9.gz", "rt") as fh:
        head = fh.readline().split()
        k = int(head[0])
        cols = fh.readline().split()
        out = []
        for ln in fh:
            p = ln.split()
            if len(p) == 37:
                out.append((tuple(int(v) for v in p[:36]), int(p[36])))
    if len(out) != k:
        raise RuntimeError(f"{len(out)} rows vs header {k}")
    letters = "ABCDEFGHI"
    from metricpoly.core import pairs
    if cols[:36] != [letters[i] + letters[j] for i, j in pairs(N)]:
        raise RuntimeError("coordinate order differs from pairs(9)")
    return out


_W = {}


def _init():
    from metricpoly.core import ineq_matrix, pairs
    import cap_lemma_lp as cl
    A, b = ineq_matrix(N)
    _W.update(A=A, b=b, cl=cl, pr=pairs(N), cuts=list(cl.cuts(N)))


def _job(item):
    idx, (a, rhs) = item
    from metricpoly.canon_large import canonical_key
    from metricpoly.core import Point
    from metricpoly.dsl.prims import certified_rank_is
    cl, A, b, pr = _W["cl"], _W["A"], _W["b"], _W["pr"]
    t = time.time()
    av = np.array(a, dtype=np.int64)
    tight, valid = [], True
    for S, c in _W["cuts"]:
        v = int(av @ c)
        if v > rhs:
            valid = False
        elif v == rhs:
            tight.append((S, c))
    base = tight[0][1] if tight else None
    is_facet = bool(valid and len(tight) >= len(pr) and
                    certified_rank_is(np.array([c - base for _, c in tight[1:]], dtype=np.int64), len(pr) - 1))
    at0 = {}
    for S, c in tight:
        a2, b2 = cl.switch(a, rhs, S, pr)
        k, sz = cl.sn_orbit(N, a2)
        at0[k] = sz
    n_at0 = sum(at0.values())
    size = (256 * n_at0) // len(tight) if tight and (256 * n_at0) % len(tight) == 0 else None
    x, val, cert = cl.lp_max(A, b, a)
    r = {"i": idx, "valid": valid, "facet": is_facet, "roots": len(tight), "size": size, "dual_certified": cert,
         "max_minus_rhs": str(val - rhs)}
    if val > rhs:
        D = 1
        for f in x:
            D = D * f.denominator // math.gcd(D, f.denominator)
        p = Point.make(N, D, tuple(int(f * D) for f in x))
        sl = b * p.D - A @ np.array(p.nums, dtype=np.int64)
        T = np.nonzero(sl == 0)[0]
        r["vertex"] = bool((sl >= 0).all()) and bool(certified_rank_is(A[T], len(pr)))
        r["key"] = canonical_key(p)
        r["point"] = [p.D, list(p.nums)]
    r["s"] = round(time.time() - t, 3)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=18)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    t0 = time.time()
    classes = read_classes()
    done = {}
    if CK.exists():
        for ln in CK.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(ln)
                done[r["i"]] = r
            except json.JSONDecodeError:
                pass
    todo = [(i, c) for i, c in enumerate(classes) if i not in done]
    if a.limit is not None:
        todo = todo[:a.limit]
    print(f"{len(classes)} classes, {len(done)} done, {len(todo)} to do", flush=True)
    CK.parent.mkdir(parents=True, exist_ok=True)
    with get_context("spawn").Pool(a.workers, initializer=_init) as pool, open(CK, "a", encoding="utf-8") as fh:
        for k, r in enumerate(pool.imap_unordered(_job, todo, chunksize=16)):
            fh.write(json.dumps(r) + "\n")
            done[r["i"]] = r
            if k % 2000 == 0:
                fh.flush()
                print(f"  {k + 1}/{len(todo)} in {time.time() - t0:.0f} s", flush=True)
    if len(done) < len(classes):
        print(f"partial: {len(done)}/{len(classes)}", flush=True)
        return
    # ---------------------------------------------------------------- summary
    keys = set()
    for f in sorted((ROOT / "checkpoints" / "verify_n9_list").glob("chunk_*.json")):
        keys.update(json.loads(f.read_text())["keys"])
    R = [done[i] for i in range(len(classes))]
    pos = [r for r in R if "key" in r]
    unlisted = [r for r in pos if r["key"] not in keys]
    out = {"classes": len(R), "list_orbits": len(keys),
           "all_valid": all(r["valid"] for r in R), "all_facets": all(r["facet"] for r in R),
           "all_dual_certified": all(r["dual_certified"] for r in R),
           "sum_class_sizes": sum(r["size"] or 0 for r in R), "stated_total": TOTAL,
           "sizes_integral": all(r["size"] is not None for r in R),
           "empty_caps": len(R) - len(pos), "positive_caps": len(pos),
           "all_optima_vertices": all(r["vertex"] for r in pos),
           "distinct_optimum_orbits": len({r["key"] for r in pos}),
           "unlisted_optima": [{"class": r["i"] + 1, "key": r["key"], "point": r["point"]} for r in unlisted],
           "seconds_total_cpu": round(sum(r["s"] for r in R), 1)}
    out["PASS_all_optima_listed"] = (out["all_valid"] and out["all_facets"] and out["all_dual_certified"]
                                     and out["all_optima_vertices"] and not unlisted)
    atomic_write_json(ROOT / "results" / "phase10" / "cap_lemma_n9.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "unlisted_optima"}), flush=True)
    print(f"unlisted optima: {len(unlisted)}", flush=True)


if __name__ == "__main__":
    main()
