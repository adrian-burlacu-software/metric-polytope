#!/usr/bin/env python3
"""Does anchor length grow with n? Avis doubling of the path P_d (docs/literature.md C9): a vertex of m_{3d-1} with
denominator d. For d = 3, 4, 5, ... checks the vertex exactly and reports the best peel chain (step_types.analyse),
plus the smallest bottleneck over all chains regardless of seed size.
Usage: python -u scripts/phase9/anchor_growth.py [--dmax 5]. Writes results/phase9/anchor_growth.json."""
from __future__ import annotations
import argparse, itertools, sys, time
from fractions import Fraction
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
from metricpoly import core  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402
import step_types as stt  # noqa: E402
from vertex_structure import tight_rows  # noqa: E402


def avis_path(d: int) -> Point:
    V = list(range(d)); Vp = [d + i for i in V]; E = [(i, i + 1) for i in range(d - 1)]
    U = [2 * d + k for k in range(len(E))]
    N = 2 * d + len(E)
    adj = {v: set() for v in range(N)}
    def edge(a, b): adj[a].add(b); adj[b].add(a)
    for i, j in E: edge(i, j); edge(Vp[i], Vp[j])
    for i in V: edge(i, Vp[i])
    for k, (i, j) in enumerate(E): edge(i, U[k]); edge(Vp[j], U[k])
    dist = []
    for s in range(N):
        D = {s: 0}; q = [s]
        for a in q:
            for b in adj[a]:
                if b not in D: D[b] = D[a] + 1; q.append(b)
        dist.append(D)
    tau = max(dist[a][b] + dist[a][c] + dist[b][c] for a, b, c in itertools.combinations(range(N), 3))
    x = [Fraction(2 * dist[i][j], tau) for i, j in core.pairs(N)]
    Dn = 1
    for v in x: Dn = Dn * v.denominator // __import__("math").gcd(Dn, v.denominator)
    return Point.make(N, Dn, [int(v * Dn) for v in x])


def min_bottleneck_any(x: Point):
    """Smallest longest-anchor over all peel chains (any end set)."""
    n = x.n; T = tight_rows(x)
    rows = {v: [] for v in range(n)}
    for tri, coef, _ in T:
        for v in tri:
            a, b = [w for w in tri if w != v]
            rows[v].append((a, b, 1 if coef[stt._pid(n, min(v, a), max(v, a))] == coef[stt._pid(n, min(v, b), max(v, b))] else 0))
    memo = {}
    def g(S):
        if S in memo: return memo[S]
        best = None
        for v in S:
            if len(S) <= 2: break
            anc = stt.step(S, v, rows[v])
            if anc is None: continue
            sub = g(S - {v})
            c = max(anc) if sub is None else max(max(anc), sub)
            best = c if best is None else min(best, c)
        memo[S] = best
        return best
    return g(frozenset(range(n)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dmax", type=int, default=5); a = ap.parse_args()
    out = []
    for d in range(3, a.dmax + 1):
        t = time.time(); x = avis_path(d)
        isv = bool(core.is_vertex(x)[0])
        r = stt.analyse((f"avis-P{d}", x)) if isv else {}
        mb = min_bottleneck_any(x) if isv else None
        row = {"d": d, "n": x.n, "D": int(x.D), "vertex": isv, "seed": r.get("seed"), "bottleneck": r.get("bottleneck"),
               "chain": r.get("chain"), "min_bottleneck_any_chain": mb, "s": round(time.time() - t, 1)}
        out.append(row); print(row, flush=True)
        atomic_write_json(ROOT / "results/phase9/anchor_growth.json", out)


if __name__ == "__main__":
    main()
