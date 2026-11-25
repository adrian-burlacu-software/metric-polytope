#!/usr/bin/env python3
"""How much could a perfect step-choice rule save in the fiber generator (§11)? (2026-11-25)

For target denominator D, a level-k point of the generator is *useful* if it is x|S for some vertex x of m_n with
denominator dividing D, where S lies on a build chain of x: S is buildable (|S| = 4, or S - v buildable and the step
S - v -> S determined) and S extends to all n nodes by determined steps (S is in the peel closure of the full set).
Reports per level: useful orbits vs the generator's level size (results/phase9/fiber_generator_n{n}.json), and per
useful point, how many of its kept fiber vertices are useful (the choice a local rule would have to make).

Usage: python -u scripts/phase9/useful_share.py --n 8 --D 3 4 5 6 [--workers 16]
Writes results/phase9/useful_share_n{n}.json.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

from metricpoly import core, group  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402
import step_types as stt  # noqa: E402
from vertex_structure import tight_rows  # noqa: E402
from fiber_generator import fiber_vertices  # noqa: E402


def restrict(x: Point, S):
    S = sorted(S)
    k = len(S)
    nums = [x.nums[core.pidx(x.n, S[a], S[b])] for a, b in core.pairs(k)]
    return k, nums


def useful_sets(args):
    """For one vertex x (scaled to denominator D): canonical keys of useful restrictions, per size."""
    x, D = args
    n = x.n
    T = tight_rows(x)
    rows = {v: [] for v in range(n)}
    for tri, coef, _ in T:
        for v in tri:
            a, b = [w for w in tri if w != v]
            rows[v].append((a, b, 1 if coef[stt._pid(n, min(v, a), max(v, a))] ==
                            coef[stt._pid(n, min(v, b), max(v, b))] else 0))
    det = {}

    def ok(S, v):
        if (S, v) not in det:
            det[(S, v)] = stt.step(S, v, rows[v]) is not None
        return det[(S, v)]
    full = frozenset(range(n))
    down, stack = {full}, [full]                 # peel closure: S extends to full by determined steps
    while stack:
        S = stack.pop()
        if len(S) <= 4:
            continue
        for v in S:
            S2 = S - {v}
            if S2 not in down and ok(S, v):
                down.add(S2)
                stack.append(S2)
    bmemo = {}

    def buildable(S):
        if len(S) == 4:
            return True
        if S not in bmemo:
            bmemo[S] = any(ok(S, v) and buildable(S - {v}) for v in S)
        return bmemo[S]
    out = defaultdict(dict)
    scale = D // x.D
    xs = Point.make(n, D, [v * scale for v in x.nums]) if scale > 1 else x
    for S in down:
        if len(S) >= 4 and buildable(S):
            k, nums = restrict(xs, S)
            c = group.canonical(Point.make(k, D, nums))
            out[k][c.key()] = [v * (D // c.D) for v in c.nums]     # numerators over D
    return dict(out)


def choice_job(args):
    """For one useful level-k point: kept fiber vertices, and how many of them are useful at level k+1."""
    k, D, nums, useful_next = args
    keep, tot = fiber_vertices((k, D, nums))
    keys = {group.canonical(Point.make(k + 1, D, r)).key() for r in keep}
    return tot, len(keep), len(keys), len(keys & useful_next)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--D", type=int, nargs="+", required=True)
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    from metricpoly import deza
    t0 = time.time()
    gen = json.loads((ROOT / "results/phase9" / f"fiber_generator_n{a.n}.json").read_text())
    V = [x for x in deza.load_ext(a.n) if x.D > 1]
    res = {}
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for D in a.D:
            xs = [x for x in V if D % x.D == 0]
            U = defaultdict(dict)
            for part in pool.imap_unordered(useful_sets, [(x, D) for x in xs], chunksize=4):
                for k, d in part.items():
                    U[int(k)].update(d)
            lv = gen[str(D)]["levels"]
            info = {"D": D, "vertex_orbits_dividing_D": len(xs), "levels": {}}
            for k in range(4, a.n + 1):
                g = lv.get(str(k))
                info["levels"][str(k)] = {"useful": len(U[k]), "generator": g,
                                          "share": round(len(U[k]) / g, 5) if g else None}
            # choice ratio at each step k -> k+1, over useful level-k points (representatives rebuilt from keys)
            info["choices"] = {}
            for k in range(4, a.n):
                reps = list(U[k].values())
                nxt = set(U[k + 1])
                stats = list(pool.imap_unordered(choice_job, [(k, D, r, nxt) for r in reps], chunksize=8))
                tot = sum(s[0] for s in stats); kept = sum(s[1] for s in stats)
                distinct = sum(s[2] for s in stats); good = sum(s[3] for s in stats)
                info["choices"][f"{k}->{k + 1}"] = {
                    "useful_points": len(reps), "fiber_vertices_mean": round(tot / max(1, len(reps)), 1),
                    "kept_distinct_mean": round(distinct / max(1, len(reps)), 1),
                    "useful_children_mean": round(good / max(1, len(reps)), 2),
                    "useful_child_share": round(good / max(1, distinct), 4)}
            res[str(D)] = info
            print(json.dumps(info), f"({time.time() - t0:.0f} s)", flush=True)
            atomic_write_json(ROOT / "results/phase9" / f"useful_share_n{a.n}.json", res)


if __name__ == "__main__":
    main()
