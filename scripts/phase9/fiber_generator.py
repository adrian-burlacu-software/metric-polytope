#!/usr/bin/env python3
"""Generator built from the peel-step types (docs/phase9_status.md §10), run on m_8 to measure its branching.

For a target denominator D (every restriction of a vertex with denominator D lies in (1/D)Z):
  level 3 : all 3-node points of m_3 in (1/D)Z, up to symmetry;
  level 4 : all 4-node points of m_4 in (1/D)Z (seeds of size 4), up to symmetry -- this contains every fiber vertex
            over level 3 as well;
  level k+1 (k >= 4): every vertex of the one-node fiber over each level-k point (= a determined step, §10), kept
            if in (1/D)Z; deduped by group.canonical.
  final   : level-n points that are vertices of m_n, compared to Deza's list (orbits with this D).
Branching = level sizes, fiber vertices per point, and the vertex share of the last level. Intermediates are not
required to be vertices. Sound and complete for orbits with seed <= 4 (all of m_8): a chain seed -> ... -> x with
determined steps is exactly a sequence of fiber vertices.

Usage: python -u scripts/phase9/fiber_generator.py --n 8 --D 3 4 5 [--workers 16] [--level-cap 400000]
Writes results/phase9/fiber_generator_n{n}.json (one entry per D, rewritten after each D).
"""
from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from metricpoly import core, group  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def lattice_points(k: int, D: int):
    """All points of m_k with coordinates in (1/D)Z, as integer arrays (numerators), vectorised by node extension."""
    P = [np.zeros((1, 0), dtype=np.int64)]   # k = 1: no coordinates
    cur = np.zeros((1, 0), dtype=np.int64)
    for m in range(1, k):                    # add node m to nodes 0..m-1
        grid = np.array(list(itertools.product(range(D + 1), repeat=m)), dtype=np.int64)   # x_{a m}, a < m
        out = []
        for row in cur:
            ok = np.ones(len(grid), dtype=bool)
            for a, b in itertools.combinations(range(m), 2):
                y = row[core.pidx(m, a, b)] if m > 1 else 0
                ua, ub = grid[:, a], grid[:, b]
                ok &= (ua - ub <= y) & (ub - ua <= y) & (y <= ua + ub) & (ua + ub + y <= 2 * D)
            for g in grid[ok]:
                # coordinates on m+1 nodes in core.pairs order
                M = {}
                for (a, b) in core.pairs(m):
                    M[(a, b)] = row[core.pidx(m, a, b)]
                for a in range(m):
                    M[(a, m)] = g[a]
                out.append([M[e] for e in core.pairs(m + 1)])
        cur = np.array(out, dtype=np.int64).reshape(len(out), core.dim(m + 1))
    return cur


def canon(k: int, D: int, nums) -> str:
    return group.canonical(Point.make(k, D, [int(v) for v in nums])).key()


def _canon_job(args):
    k, D, rows = args
    out = {}
    for r in rows:
        key = canon(k, D, r)
        if key not in out:
            out[key] = r
    return out


def fiber_vertices(args):
    """Vertices of the one-node fiber over the k-node point (D, nums), kept if in (1/D)Z. Returns list of nums on
    k+1 nodes and the total fiber vertex count."""
    import cdd
    import cdd.gmp
    k, D, nums = args
    rows = []
    for a, b in itertools.combinations(range(k), 2):
        y = Fraction(int(nums[core.pidx(k, a, b)]), D)
        e = [0] * k
        def r(ca, cb, rhs):
            v = [Fraction(0)] * k
            v[a], v[b] = Fraction(-ca), Fraction(-cb)
            rows.append([rhs] + v)
        r(1, -1, y); r(-1, 1, y); r(-1, -1, -y); r(1, 1, 2 - y)
    mat = cdd.gmp.matrix_from_array(rows, rep_type=cdd.RepType.INEQUALITY)
    gens = cdd.gmp.copy_generators(cdd.gmp.polyhedron_from_matrix(mat))
    verts = [g[1:] for g in gens.array if g[0] == 1]
    keep = []
    for u in verts:
        if all((Fraction(c) * D).denominator == 1 for c in u):
            M = {e: int(nums[core.pidx(k, *e)]) for e in core.pairs(k)}
            for a in range(k):
                M[(a, k)] = int(Fraction(u[a]) * D)
            keep.append([M[e] for e in core.pairs(k + 1)])
    return keep, len(verts)


def _last_step(args):
    k, n, D, r = args
    keep, tot = fiber_vertices((k, D, r))
    o, nv, nc = _final_job((n, D, keep))
    return o, nv, nc, tot


def _final_job(args):
    """Last level: no orbit merge; vertex test per candidate, canonical key only for vertices."""
    n, D, rows = args
    out, nv = {}, 0
    for r in rows:
        x = Point.make(n, D, [int(v) for v in r])
        if core.is_vertex(x)[0]:
            nv += 1
            out.setdefault(group.canonical(x).key(), x.D)
    return out, nv, len(rows)


def dedup(pool, k, D, rows, workers):
    chunks = [(k, D, rows[i::workers * 4]) for i in range(workers * 4)]
    out = {}
    for part in pool.imap_unordered(_canon_job, chunks):
        for key, r in part.items():
            out.setdefault(key, r)
    return out


def run_D(pool, n, D, workers, cap, t0):
    from metricpoly import deza
    info = {"D": D, "levels": {}}
    L3 = dedup(pool, 3, D, [list(r) for r in lattice_points(3, D)], workers)
    L4 = dedup(pool, 4, D, [list(r) for r in lattice_points(4, D)], workers)
    info["levels"]["3"] = len(L3)
    info["levels"]["4"] = len(L4)
    print(f"  D={D}: level 3 {len(L3)}, level 4 {len(L4)} ({time.time() - t0:.0f} s)", flush=True)
    cur = L4
    for k in range(4, n):
        if len(cur) > cap:
            info["stopped"] = f"level {k} has {len(cur)} > cap {cap}"
            print(f"  D={D}: {info['stopped']}", flush=True)
            return info
        if k + 1 == n:
            break
        nxt_rows, fv = [], Counter()
        for keep, tot in pool.imap_unordered(fiber_vertices, [(k, D, r) for r in cur.values()], chunksize=32):
            nxt_rows += keep
            fv["fiber vertices"] += tot
            fv["kept (1/D)"] += len(keep)
        nxt = dedup(pool, k + 1, D, nxt_rows, workers)
        info["levels"][str(k + 1)] = len(nxt)
        info.setdefault("per_point", {})[str(k)] = {"fiber_vertices_mean": round(fv["fiber vertices"] / max(1, len(cur)), 1),
                                                    "kept_mean": round(fv["kept (1/D)"] / max(1, len(cur)), 1)}
        print(f"  D={D}: level {k + 1} {len(nxt)} (fiber vertices/point {info['per_point'][str(k)]}) "
              f"({time.time() - t0:.0f} s)", flush=True)
        cur = nxt
    # last level: candidates = all kept fiber vertices over level n-1 (with repeats across orbits of level n-1)
    verts, cand, nvr, fvt = {}, 0, 0, 0
    for res in pool.imap_unordered(_last_step, [(k, n, D, r) for r in cur.values()], chunksize=16):
        o, nv, nc, ft = res
        verts.update(o); nvr += nv; cand += nc; fvt += ft
    info["per_point"][str(n - 1)] = {"fiber_vertices_mean": round(fvt / max(1, len(cur)), 1),
                                     "kept_mean": round(cand / max(1, len(cur)), 1)}
    info["levels"][f"{n} (candidates, not merged)"] = cand
    vD = {key for key, d in verts.items() if d == D}
    target = {group.canonical(x).key() for x in deza.load_ext(n) if x.D == D}
    info.update(final_candidates=cand, vertex_candidates=nvr, vertices=len(verts), vertices_with_D=len(vD), deza_orbits_D=len(target),
                found=len(vD & target), missed=len(target - vD), extra_not_in_deza=len(vD - target),
                vertex_share_last_level=round(nvr / max(1, cand), 5))
    print(f"  D={D}: {cand} candidates at level {n} (from {len(cur)} level-{n - 1} orbits), {nvr} are vertices, "
          f"{len(verts)} vertex orbits ({len(vD)} with D = {D}); "
          f"Deza orbits with D = {D}: {len(target)}, found {len(vD & target)}, missed {len(target - vD)}", flush=True)
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--D", type=int, nargs="+", required=True)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--level-cap", type=int, default=400000)
    a = ap.parse_args()
    t0 = time.time()
    path = ROOT / "results/phase9" / f"fiber_generator_n{a.n}.json"
    res = json.loads(path.read_text()) if path.exists() else {}
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for D in a.D:
            res[str(D)] = run_D(pool, a.n, D, a.workers, a.level_cap, t0)
            res[str(D)]["seconds_cumulative"] = round(time.time() - t0, 1)
            atomic_write_json(path, res)


if __name__ == "__main__":
    main()
