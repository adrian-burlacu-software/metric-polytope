#!/usr/bin/env python3
"""Do the build rules stay finite as n grows? Step types of the peel chains (2026-11-25).

A peel step S -> S - v (seed_size in vertex_structure.py) fixes the new coordinates u_a = x_va, a in S - v, from the
tight triangles (v, a, b) inside S. Each such row has the form u_a - u_b = c ("diff") or u_a + u_b = c ("sum"), so
the rows form a signed graph on S - v, and the step is determined (full rank) iff every component contains an
unbalanced cycle (odd number of sum edges). Rank of a signed incidence matrix = nodes - balanced components; the
criterion is exact, no arithmetic needed.

A step's rule is therefore its anchors: per component, the length of its shortest unbalanced cycle (length 2 = a
diff and a sum row on the same pair). Everything else in the component is tree propagation. Rules stay finite iff
the anchor length stays bounded as n grows.

Per vertex: among all peel chains, the one reaching the smallest seed, then the smallest bottleneck (longest anchor
along the chain). Reported per n: bottleneck distribution, anchor-length distribution along chosen chains, component
counts, and the seed sizes.

Usage: python -u scripts/phase9/step_types.py [--m9 20000] [--workers 16]
Writes results/phase9/step_types.json.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from collections import Counter, deque
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402
from vertex_structure import tight_rows, load_set  # noqa: E402

INF = 10 ** 9


def step(S: frozenset, v: int, rows_v):
    """Anchors of peeling v from S: None if not determined, else sorted tuple of per-component anchor lengths."""
    nodes = S - {v}
    adj = {a: [] for a in nodes}
    for (a, b, sgn) in rows_v:
        if a in nodes and b in nodes:
            adj[a].append((b, sgn))
            adj[b].append((a, sgn))
    seen, anchors = set(), []
    for s in nodes:
        if s in seen:
            continue
        comp, q = [s], deque([s])
        seen.add(s)
        while q:
            a = q.popleft()
            for b, _ in adj[a]:
                if b not in seen:
                    seen.add(b)
                    comp.append(b)
                    q.append(b)
        # shortest unbalanced closed walk: BFS on (node, parity) from (a, 0) to (a, 1); its minimum over a is the
        # shortest unbalanced cycle length
        best = INF
        for a0 in comp:
            dist = {(a0, 0): 0}
            q = deque([(a0, 0)])
            while q:
                a, p = q.popleft()
                d = dist[(a, p)]
                if d + 1 >= best:
                    break
                for b, sg in adj[a]:
                    st = (b, p ^ sg)
                    if st not in dist:
                        dist[st] = d + 1
                        if st == (a0, 1):
                            best = min(best, d + 1)
                        q.append(st)
        if best == INF:
            return None
        anchors.append(best)
    return tuple(sorted(anchors))


def analyse(args):
    key, x = args
    n = x.n
    T = tight_rows(x)
    rows = {v: [] for v in range(n)}
    for tri, coef, _hom in T:
        for v in tri:
            a, b = [w for w in tri if w != v]
            ca = coef[_pid(n, min(v, a), max(v, a))]
            cb = coef[_pid(n, min(v, b), max(v, b))]
            rows[v].append((a, b, 1 if ca == cb else 0))      # 1 = sum edge (same sign), 0 = diff edge
    memo = {}

    def f(S):
        """(seed size, bottleneck, chain) for the best chain from S."""
        if S in memo:
            return memo[S]
        best = (len(S), 0, ())
        if len(S) > 2:
            for v in S:
                anc = step(S, v, rows[v])
                if anc is None:
                    continue
                sz, bn, ch = f(S - {v})
                cand = (sz, max(bn, max(anc)), (anc,) + ch)
                if cand[:2] < best[:2]:
                    best = cand
        memo[S] = best
        return best

    sz, bn, ch = f(frozenset(range(n)))
    return {"key": key, "n": n, "D": int(x.D), "seed": sz, "bottleneck": bn, "chain": [list(c) for c in ch]}


@lru_cache(maxsize=None)
def _pidx_table(n):
    from metricpoly import core
    return {(i, j): core.pidx(n, i, j) for i in range(n) for j in range(i + 1, n)}


def _pid(n, i, j):
    return _pidx_table(n)[(i, j)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m9", type=int, default=20000)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--seed", type=int, default=20261125)
    a = ap.parse_args()
    t0 = time.time()
    pts = load_set("m8", 0, 0)                                          # n = 5..8, all orbits
    d = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
    c = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
    idx = np.sort(np.random.default_rng(a.seed).choice(len(d), size=min(a.m9, len(d)), replace=False))
    pts += [(f"n9:{i}", Point.make(9, int(d[i]), [int(t) for t in c[i]])) for i in idx]
    s10 = ROOT / "results/phase9/sample_reach_n10.json"
    if s10.exists():
        pts += [(f"n10:{r['key']}", Point.make(10, r["D"], r["nums"])) for r in json.loads(s10.read_text())["rows"]]
    pts = [(k, x) for k, x in pts if x.D > 1]                            # cuts are trivial
    print(f"{len(pts)} vertices ({time.time() - t0:.0f} s)", flush=True)
    with mp.get_context("spawn").Pool(a.workers) as pool:
        res = pool.map(analyse, pts, chunksize=64)
    out = {"m9_sample": int(a.m9), "per_n": {}}
    seen_sigs = set()
    for n in sorted({r["n"] for r in res}):
        R = [r for r in res if r["n"] == n]
        anchors = Counter(L for r in R for st in r["chain"] for L in st)
        comps = Counter(len(st) for r in R for st in r["chain"])
        sigs = {tuple(st) for r in R for st in r["chain"]}
        new = sigs - seen_sigs
        seen_sigs |= sigs
        out["per_n"][str(n)] = {
            "vertices": len(R), "seed": dict(sorted(Counter(r["seed"] for r in R).items())),
            "bottleneck": dict(sorted(Counter(r["bottleneck"] for r in R).items())),
            "anchor_lengths": dict(sorted(anchors.items())), "components_per_step": dict(sorted(comps.items())),
            "distinct_step_signatures": len(sigs), "new_vs_smaller_n": len(new),
            "new_signatures": sorted(list(map(list, new)))[:50],
            "max_bottleneck_examples": [{k: r[k] for k in ("key", "D", "bottleneck", "chain")}
                                        for r in sorted(R, key=lambda r: -r["bottleneck"])[:5]]}
        o = out["per_n"][str(n)]
        print(f"n = {n}: {len(R)} vertices; bottleneck {o['bottleneck']}; anchors {o['anchor_lengths']}; "
              f"components/step {o['components_per_step']}; signatures {len(sigs)} ({len(new)} new)", flush=True)
    out["seconds"] = round(time.time() - t0, 1)
    atomic_write_json(ROOT / "results/phase9/step_types.json", out)


if __name__ == "__main__":
    main()
