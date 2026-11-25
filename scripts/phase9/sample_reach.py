#!/usr/bin/env python3
"""Do the Phase 9 moves carry across n? Reached share of random LP vertices of m_n, n = 8, 9, 10 (idea 4, 2026-11-24).

Sampling: random walks on the vertex graph of m_n (exact neighbours, metricpoly.ladder), started at the twin extension
of a random non-cut vertex of m_{n-1} (Deza list), --steps steps each; the last non-cut vertex of each walk, deduped by
orbit. (Random LP objectives were tried first and land on cuts almost always: 2 non-cut orbits from 1,200 LPs at n = 8.)
The walk is biased (toward vertex degree, and by its start), the same way at every n, so the trend across n is the
measurement, not the absolute share.

Verdict, exact:
  n <= 9 : the orbit key is in checkpoints/phase9/reached.json -> reached; an unreached Phase 9 target -> unreached;
           otherwise as for n = 10.
  n = 10 : metricpoly.reach_large.reachable_bu (the judge's bottom-up search for n <= 12) with all accepted moves of
           checkpoints/phase9/state.json, its base test extended by: every restriction on <= 9 nodes whose orbit is
           already reached by the main engine (reached.json) or is an extra base orbit of an accepted family counts as
           base (sound: those points are derivable). True / False / None (budget exhausted).

Usage: python -u scripts/phase9/sample_reach.py --n 10 [--walks 30] [--steps 15] [--budget 300] [--workers 12]
Writes results/phase9/sample_reach_n{n}.json.
"""
from __future__ import annotations

import argparse
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
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

from metricpoly import core  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402

_W = {}


def lp_vertex(n: int, c) -> Point:
    import cdd
    import cdd.gmp
    A, b = core.ineq_matrix(n)
    arr = [[Fraction(int(bi))] + [Fraction(-int(v)) for v in row] for row, bi in zip(A, b)]
    arr.append([Fraction(0)] + [Fraction(int(v)) for v in c])
    lp = cdd.gmp.linprog_from_array(arr, obj_type=cdd.LPObjType.MAX)
    cdd.gmp.linprog_solve(lp)
    x = [Fraction(v) for v in lp.primal_solution]
    D = 1
    for v in x:
        D = D * v.denominator // np.gcd(D, v.denominator)
    return Point.make(n, int(D), [int(v * D) for v in x])


def twin(y: Point) -> Point:
    """y on n-1 nodes plus a copy of node 0 (distance 0 to node 0): an exact vertex of m_n (round 8)."""
    n1 = y.n
    M = {}
    for v, (i, j) in zip(y.nums, core.pairs(n1)):
        M[(i, j)] = M[(j, i)] = v
    M.update({(i, i): 0 for i in range(n1)})
    nums = [M[(i, j)] if j < n1 else M[(i, 0)] for i, j in core.pairs(n1 + 1)]
    return Point.make(n1 + 1, y.D, nums)


def _walk(args):
    """Random walk on the vertex graph of m_n (metricpoly.ladder rung(n-1, n-1) = m_n, exact neighbours).
    A step picks a uniformly random neighbour; vertices whose tangent cone has more than ray_cap rays are not
    entered (the walk stays and redraws). Returns the last non-cut vertex visited and step statistics."""
    n, x, steps, seed, cap, tcap, tcap0 = args
    from metricpoly.ladder import rung
    R = rung(n - 1, n - 1)

    def nbrs(D, y, tcap=tcap):
        # cdd's enumeration time explodes with degeneracy and max_rays is only checked afterwards, so refuse
        # vertices with more than dim + tcap tight rows before calling cdd (n = 8 probe: <= 56 tight rows take < 7 s,
        # 79 tight rows did not finish in 25 s; an 8 h hang at a near-cut vertex on 2026-11-24).
        if len(R.tight(D, y)) > R.m + tcap:
            return None
        return R.neighbours(D, y, max_rays=cap)[0]
    rng = np.random.default_rng(seed)
    pos = {e: t for t, e in enumerate(core.pairs(n))}
    to_r = lambda p: tuple(p.nums[pos[e]] for e in R.edges)                       # noqa: E731
    from_r = lambda D, y: Point.make(n, int(D), [int(y[R.edges.index(e)]) for e in core.pairs(n)])  # noqa: E731
    st = Counter()
    cur, last_noncut = x, None
    nb_cur = None
    for _ in range(steps):
        if nb_cur is None:
            nb_cur = nbrs(cur.D, to_r(cur), tcap0 if cur is x else tcap)
            if nb_cur is None:
                st["start over ray cap"] += 1
                return last_noncut, dict(st)
        moved = False
        for _try in range(5):
            Dy, y = nb_cur[int(rng.integers(0, len(nb_cur)))]
            cand = from_r(Dy, y)
            nb = nbrs(cand.D, to_r(cand))
            if nb is None:
                st["refused (degenerate / ray cap)"] += 1
                continue
            cur, nb_cur, moved = cand, nb, True
            st["steps"] += 1
            break
        if not moved:
            st["stuck"] += 1
        if cur.D > 1:
            last_noncut = cur
    return last_noncut, dict(st)


def _init():
    from common import interpreter
    from metricpoly import reach_large, group
    I, _ = interpreter([])
    st = json.loads((ROOT / "checkpoints/phase9/state.json").read_text())
    reached = set(json.loads((ROOT / "checkpoints/phase9/reached.json").read_text()))
    extra = set(st["extra_base"])
    _W.update(I=I, moves=[(nm, int(mv.grow)) for nm, mv in I.moves.items() if nm in st["moves"]])
    orig = reach_large.is_base

    def is_base(x):
        if 3 <= x.n <= 9:
            k = group.canonical(x).key()
            if k in reached or k in extra:
                return True
        return orig(x)
    reach_large.is_base = is_base


def _apply(name, p):
    I = _W["I"]
    try:
        return [o for o in I.apply_move(I.moves[name], [p], as_orbits=True) if core.is_feasible(o)]
    except Exception:
        return []


def _verdict(args):
    x, budget = args
    from metricpoly.reach_large import reachable_bu
    t = time.time()
    v, stats = reachable_bu(x, _W["moves"], _apply, budget=budget)
    return {"verdict": v, "s": round(time.time() - t, 1), "stats": {k: stats[k] for k in list(stats)[:6]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--walks", type=int, default=30)
    ap.add_argument("--steps", type=int, default=15)
    ap.add_argument("--ray-cap", type=int, default=20000)
    ap.add_argument("--tight-cap", type=int, default=30, help="refuse vertices with more than dim + this tight rows")
    ap.add_argument("--start-tight-cap", type=int, default=None, help="tight cap for the start vertex (default: --tight-cap)")
    ap.add_argument("--walk-deadline", type=float, default=900, help="wall-clock limit for all walks (s)")
    ap.add_argument("--budget", type=float, default=300)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--seed", type=int, default=20261124)
    a = ap.parse_args()
    from metricpoly import group
    from metricpoly.canon_large import canonical_key
    t0 = time.time()
    rng = np.random.default_rng(a.seed + a.n)
    starts = []
    if a.n - 1 <= 8:
        from metricpoly import deza
        base = [y for y in deza.load_ext(a.n - 1) if y.D > 1]
        for i in rng.integers(0, len(base), size=a.walks):
            starts.append(base[int(i)])
    else:
        C = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
        Dn = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
        while len(starts) < a.walks:
            i = int(rng.integers(0, len(Dn)))
            if Dn[i] > 1:
                starts.append(Point.make(9, int(Dn[i]), [int(v) for v in C[i]]))
    jobs = [(a.n, twin(y), a.steps, a.seed + 1000 * a.n + j, a.ray_cap, a.tight_cap,
             a.tight_cap if a.start_tight_cap is None else a.start_tight_cap) for j, y in enumerate(starts)]
    pool = mp.get_context("spawn").Pool(a.workers)
    res = [pool.apply_async(_walk, (j,)) for j in jobs]
    walked, dl = [], time.time() + a.walk_deadline
    for r in res:
        try:
            walked.append(r.get(timeout=max(1.0, dl - time.time())))
        except mp.TimeoutError:
            walked.append((None, {"walk over deadline": 1}))
    pool.terminate()
    pool.join()
    pts, keys, wstats = [], set(), Counter()
    for x, st in walked:
        wstats.update(st)
        if x is None:
            continue
        k = group.canonical(x).key() if a.n <= 9 else canonical_key(x)
        if k in keys:
            wstats["duplicate orbit"] += 1
            continue
        assert core.is_vertex(x)[0]
        keys.add(k)
        pts.append((k, x))
    tries = a.walks
    print(f"n = {a.n}: {len(pts)} distinct non-cut vertex orbits from {a.walks} walks of {a.steps} steps "
          f"({time.time() - t0:.0f} s); walk stats {dict(wstats)}; D {dict(Counter(x.D for _, x in pts))}", flush=True)
    rows, todo = [], []
    if a.n <= 9:
        reached = set(json.loads((ROOT / "checkpoints/phase9/reached.json").read_text()))
        unr = {t["key"] for t in json.loads((ROOT / "results/phase9/unreached_targets.json").read_text())}
    for k, x in pts:
        r = {"key": k, "D": int(x.D), "nums": [int(v) for v in x.nums]}
        if a.n <= 9 and k in reached:
            r.update(verdict=True, how="reached.json")
        elif a.n <= 9 and k in unr:
            r.update(verdict=False, how="unreached Phase 9 target")
        else:
            todo.append(len(rows))
        rows.append(r)
    if todo:
        with mp.get_context("spawn").Pool(min(a.workers, len(todo)), initializer=_init) as pool:
            for i, res in zip(todo, pool.imap(_verdict, [(Point.make(a.n, rows[i]["D"], rows[i]["nums"]), a.budget)
                                                         for i in todo])):
                rows[i].update(res, how="reachable_bu")
                print(f"  D={rows[i]['D']}: {res['verdict']} ({res['s']} s; {time.time() - t0:.0f} s)", flush=True)
    c = Counter(str(r["verdict"]) for r in rows)
    out = {"n": a.n, "samples": len(rows), "walks": a.walks, "steps": a.steps, "walk_stats": dict(wstats), "budget_s": a.budget,
           "reached": c.get("True", 0), "unreached": c.get("False", 0), "undecided": c.get("None", 0),
           "by_D": {str(D): dict(Counter(str(r["verdict"]) for r in rows if r["D"] == D))
                    for D in sorted({r["D"] for r in rows})},
           "rows": rows, "seconds": round(time.time() - t0, 1)}
    atomic_write_json(ROOT / "results" / "phase9" / f"sample_reach_n{a.n}.json", out)
    print(json.dumps({k: out[k] for k in ("n", "samples", "reached", "unreached", "undecided", "by_D")}), flush=True)


if __name__ == "__main__":
    main()
