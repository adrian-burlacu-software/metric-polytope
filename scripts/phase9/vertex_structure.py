#!/usr/bin/env python3
"""Rule-independent structure of metric-polytope vertices (Phase 9 follow-up, ideas 1-3 of 2026-11-24).

For a vertex x of m_n (x = nums / D over the pairs in lexicographic order), three exact properties:

1. seed size s(x). Peel step S -> S - v (S a node set, v in S): allowed iff x|S is a vertex of the one-node fiber over
   x|(S - v), i.e. the tight inequalities of x|S restricted to the columns (v, u), u in S - v, have rank |S| - 1.
   s(x) = the smallest |S| reachable from the full node set by peel steps (floor 2). Every vertex is a chain of
   discrete fiber-vertex choices on top of a seed point x|S of s(x) nodes.
2. primitive: no restriction x|S with 3 <= |S| < n is a vertex of m_|S|. Also reported: the largest vertex restriction.
3. cut-adjacent: x is adjacent (an edge of m_n) to some cut delta(S); equivalently its switching by S is (2/maxper(d)) d
   for an extreme ray d of the metric cone MET_n. Test: for the switched point x', the homogeneous triangle inequalities
   (tight at the zero cut) that are tight at x' have rank C(n,2) - 1.

Exactness: ranks are computed mod p = 2^31 - 1 (rank mod p <= rank over Q). A full rank mod p is a proof of full rank;
a deficient one is re-checked with metricpoly.core.exact_rank.

Usage:
  python -u scripts/phase9/vertex_structure.py --set m8            # all m_n orbits for n = 5..8 (Deza / p_vertices)
  python -u scripts/phase9/vertex_structure.py --set targets9      # the 1,000 Phase 9 n = 9 targets
  python -u scripts/phase9/vertex_structure.py --set deza9 --start 0 --count 2000   # slice of Deza's m_9 list
  python -u scripts/phase9/vertex_structure.py --set deza9all [--chunk 50000]       # all 1,056,367, resumable
Writes results/phase9/vertex_structure_{set}[_{start}_{count}].json; deza9all writes one compact summary per chunk
(checkpoints/phase9/vstruct9/chunk_NNNNNNN.json: counts plus the exceptional rows) and
results/phase9/vertex_structure_deza9all.json at the end.
"""
from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import sys
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

from metricpoly import core  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402

P = 2147483647


def rank_mod_p(A: np.ndarray) -> int:
    A = np.array(A, dtype=np.int64) % P
    rows, cols = A.shape
    r = 0
    for c in range(cols):
        if r == rows:
            break
        nz = np.flatnonzero(A[r:, c])
        if nz.size == 0:
            continue
        piv = r + nz[0]
        if piv != r:
            A[[r, piv]] = A[[piv, r]]
        inv = pow(int(A[r, c]), P - 2, P)
        A[r] = (A[r] * inv) % P
        below = np.flatnonzero(A[r + 1:, c]) + r + 1
        if below.size:
            f = A[below, c][:, None]
            A[below] = (A[below] - f * A[r]) % P
        r += 1
    return r


def full_rank(A: np.ndarray, need: int) -> bool:
    if A.shape[0] < need:
        return False
    if rank_mod_p(A) >= need:
        return True
    return core.exact_rank(A.tolist()) >= need


@lru_cache(maxsize=None)
def tri_rows(n: int):
    """For every triple (a<b<c): the 4 inequality rows as (coef dict over pair indices, rhs, homogeneous?)."""
    out = []
    for a, b, c in itertools.combinations(range(n), 3):
        ab, ac, bc = core.pidx(n, a, b), core.pidx(n, a, c), core.pidx(n, b, c)
        rows = [({ab: 1, ac: -1, bc: -1}, 0, True), ({ac: 1, ab: -1, bc: -1}, 0, True),
                ({bc: 1, ab: -1, ac: -1}, 0, True), ({ab: 1, ac: 1, bc: 1}, 2, False)]
        out.append(((a, b, c), rows))
    return out


def tight_rows(x: Point):
    """List of (triple, coef dict, homogeneous) for the inequalities tight at x (exact, integer nums over D)."""
    v = x.nums
    T = []
    for tri, rows in tri_rows(x.n):
        for coef, rhs, hom in rows:
            if sum(cf * v[i] for i, cf in coef.items()) == rhs * x.D:
                T.append((tri, coef, hom))
    return T


def seed_size(x: Point, T) -> int:
    n = x.n
    pid = {(i, j): core.pidx(n, i, j) for i in range(n) for j in range(i + 1, n)}
    by_node = {v: [(set(tri), coef) for tri, coef, _ in T if v in tri] for v in range(n)}

    def peel_ok(S: frozenset, v: int) -> bool:
        rest = sorted(S - {v})
        cols = [pid[(min(v, u), max(v, u))] for u in rest]
        rows = [[coef.get(c, 0) for c in cols] for tri, coef in by_node[v] if tri <= S]
        return bool(rows) and full_rank(np.array(rows, dtype=np.int64), len(cols))

    full = frozenset(range(n))
    seen = {full}
    frontier = [full]
    best = n
    while frontier:
        nxt = []
        for S in frontier:
            for v in S:
                S2 = S - {v}
                if S2 in seen:
                    continue
                if peel_ok(S, v):
                    seen.add(S2)
                    best = min(best, len(S2))
                    if len(S2) > 2:
                        nxt.append(S2)
        if best == 2:
            break
        frontier = nxt
    return best


def vertex_restrictions(x: Point, T):
    """Sizes k (3 <= k < n) for which some restriction x|S is a vertex of m_k; returns (primitive, largest k or 0)."""
    n = x.n
    largest = 0
    rows_all = [(set(tri), coef) for tri, coef, _ in T]
    for k in range(n - 1, 2, -1):
        for S in itertools.combinations(range(n), k):
            Ss = set(S)
            cols = [core.pidx(n, a, b) for a, b in itertools.combinations(S, 2)]
            rows = [[coef.get(c, 0) for c in cols] for tri, coef in rows_all if tri <= Ss]
            if len(rows) >= len(cols) and full_rank(np.array(rows, dtype=np.int64), len(cols)):
                largest = k
                break
        if largest:
            break
    return largest == 0, largest


def cut_adjacent(x: Point) -> bool:
    """Some switching x' of x has tight homogeneous triangle rows of rank C(n,2) - 1."""
    n, D = x.n, x.D
    m = core.dim(n)
    A, b = core.ineq_matrix(n, ("triangle",))
    v = np.array(x.nums, dtype=np.int64)
    prs = core.pairs(n)
    for mask in range(1 << (n - 1)):                       # S ranges over subsets not containing node n-1
        sep = np.array([((mask >> i) & 1) != ((mask >> j) & 1) if j < n - 1 else ((mask >> i) & 1) == 1
                        for i, j in prs])
        w = np.where(sep, D - v, v)
        T = np.flatnonzero(A @ w == 0)                     # homogeneous rows tight at x' (b = 0 for triangle rows)
        if T.size >= m - 1 and full_rank(A[T], m - 1):
            return True
    return False


def analyse(args):
    key, x = args
    t = time.time()
    T = tight_rows(x)
    s = seed_size(x, T)
    prim, largest = vertex_restrictions(x, T)
    ca = cut_adjacent(x)
    return {"key": key, "n": x.n, "D": x.D, "seed": s, "primitive": prim, "largest_vertex_restriction": largest,
            "cut_adjacent": ca, "s": round(time.time() - t, 3)}


def load_set(name, start, count):
    if name == "m8":
        from metricpoly import deza
        from metricpoly.dsl.prims import p_vertices
        from metricpoly import group
        out = []
        for n in (5, 6):
            keys = {}
            for p in p_vertices(n):
                k = group.canonical(p).key()
                keys.setdefault(k, p)
            out += [(f"n{n}:{i}", p) for i, p in enumerate(keys.values())]
        for n in (7, 8):
            out += [(f"n{n}:{i}", p) for i, p in enumerate(deza.load_ext(n))]
        return out
    if name == "targets9":
        from judge import targets
        return [(f"n9:{o}", x) for m, o, x in targets() if m == 9]
    if name == "deza9":
        c = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
        d = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
        hi = min(len(d), start + count)
        return [(f"n9:{i}", Point.make(9, int(d[i]), [int(t) for t in c[i]])) for i in range(start, hi)]
    raise SystemExit(f"unknown set {name}")


def exceptional(r) -> bool:
    return (not r["cut_adjacent"]) or r["seed"] not in (3, 4)


def run_all9(a, t0):
    ck = ROOT / "checkpoints" / "phase9" / "vstruct9"
    ck.mkdir(parents=True, exist_ok=True)
    total = len(np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r"))
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for start in range(0, total, a.chunk):
            f = ck / f"chunk_{start:07d}.json"
            if f.exists():
                continue
            if (ck / ".halt").exists():
                print("halt file: stopping", flush=True)
                return
            items = load_set("deza9", start, a.chunk)
            seed, lvr, prim, ca, exc, ss = Counter(), Counter(), 0, 0, [], 0.0
            for r in pool.imap_unordered(analyse, items, chunksize=16):
                seed[r["seed"]] += 1
                lvr[r["largest_vertex_restriction"]] += 1
                prim += r["primitive"]
                ca += r["cut_adjacent"]
                ss += r["s"]
                if exceptional(r):
                    exc.append(r)
            atomic_write_json(f, {"start": start, "count": len(items), "seed_size": dict(seed),
                                  "largest_vertex_restriction": dict(lvr), "primitive": prim, "cut_adjacent": ca,
                                  "cpu_s": round(ss, 1), "exceptional": exc})
            print(f"  chunk {start}: {len(items)} done, not cut-adjacent {len(items) - ca}, primitive {prim} "
                  f"({time.time() - t0:.0f} s)", flush=True)
    seed, lvr, prim, ca, n, exc = Counter(), Counter(), 0, 0, 0, []
    for f in sorted(ck.glob("chunk_*.json")):
        c = json.loads(f.read_text())
        seed.update({int(k): v for k, v in c["seed_size"].items()})
        lvr.update({int(k): v for k, v in c["largest_vertex_restriction"].items()})
        prim += c["primitive"]; ca += c["cut_adjacent"]; n += c["count"]; exc += c["exceptional"]
    out = {"set": "deza9all", "orbits": n, "seed_size": dict(sorted(seed.items())), "primitive": prim,
           "largest_vertex_restriction": dict(sorted(lvr.items())), "cut_adjacent": ca,
           "not_cut_adjacent": [r for r in exc if not r["cut_adjacent"]],
           "seed_not_3_or_4": [r for r in exc if r["seed"] not in (3, 4)], "seconds": round(time.time() - t0, 1)}
    atomic_write_json(ROOT / "results" / "phase9" / "vertex_structure_deza9all.json", out)
    print(json.dumps({k: v for k, v in out.items() if not isinstance(v, list)}), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True, choices=["m8", "targets9", "deza9", "deza9all"])
    ap.add_argument("--chunk", type=int, default=50000)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--count", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    t0 = time.time()
    if a.set == "deza9all":
        return run_all9(a, t0)
    items = load_set(a.set, a.start, a.count)
    print(f"{len(items)} vertices ({time.time() - t0:.0f} s)", flush=True)
    with mp.get_context("spawn").Pool(a.workers) as pool:
        rows = []
        for j, r in enumerate(pool.imap(analyse, items, chunksize=4)):
            rows.append(r)
            if (j + 1) % 200 == 0:
                print(f"  {j + 1}/{len(items)} ({time.time() - t0:.0f} s)", flush=True)
    summ = {}
    for n in sorted({r["n"] for r in rows}):
        R = [r for r in rows if r["n"] == n]
        summ[n] = {"orbits": len(R), "seed_size": dict(sorted(Counter(r["seed"] for r in R).items())),
                   "primitive": sum(r["primitive"] for r in R),
                   "largest_vertex_restriction": dict(sorted(Counter(r["largest_vertex_restriction"] for r in R).items())),
                   "cut_adjacent": sum(r["cut_adjacent"] for r in R),
                   "mean_s": round(sum(r["s"] for r in R) / len(R), 3), "max_s": max(r["s"] for r in R)}
    suffix = f"_{a.start}_{a.count}" if a.set == "deza9" else ""
    out = {"set": a.set, "summary": summ, "rows": rows, "seconds": round(time.time() - t0, 1)}
    atomic_write_json(ROOT / "results" / "phase9" / f"vertex_structure_{a.set}{suffix}.json", out)
    print(json.dumps(summ, indent=1))
    print(f"done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
