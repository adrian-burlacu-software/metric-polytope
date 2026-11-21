#!/usr/bin/env python3
"""Derivation depth with ALL moves: lift (single node), radial Λ^1..Λ^3 (up to switching), and UNCAPPED gluing.

Key fact: every move adds nodes and keeps old coordinates, so every intermediate point of a derivation of x is,
up to symmetry, a restriction x|T. Hence depth is a DP over node subsets T (memoised by canonical form):
  d(T) = 0                                   if orbit(x|T) is a base piece
  lift   : 1 + d(T \\ i)                     if x|T is a vertex of the fiber over x|(T \\ i)
  radial : 1 + d(T \\ U), |U| = 1..3         if some switching of x|T equals Λ^{|U|}(that restriction)
  glue   : 1 + max(d(A), d(B))               A ∪ B = T, A ∩ B ≠ ∅, A, B ≠ T, and x|T is a vertex of the fiber over
                                             the partial point (x|A, x|B)   [every overlap size: uncapped]
VERTEX mode: every point of the chain (x|T, and each predecessor) must be a vertex of its own m_k.
Base set: UNIFORM (cuts, anticuts, complete multipartite ± edge, Avis paths, tree suspensions, all graph metrics).

Usage: python -u scripts/detour_depth2.py [--max-n 8] [--sample K] [--resume] [--force]
"""
from __future__ import annotations

import argparse
import itertools
import math
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import core, deza, group  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.dsl.interp import Interpreter  # noqa: E402
from metricpoly.dsl.prims import certified_rank_is, p_feasible, p_vertex  # noqa: E402
from metricpoly.jobs import Job, Progress, add_job_args, atomic_write_json, atomic_write_text  # noqa: E402

UNIFORM = ["gen-cuts", "gen-anticuts", "gen-multipartite", "gen-avis-paths", "gen-tree-suspension", "gen-graphic"]
INF = math.inf


def matrix(x: Point) -> np.ndarray:
    M = np.zeros((x.n, x.n), dtype=np.int64)
    for v, (i, j) in zip(x.nums, core.pairs(x.n)):
        M[i, j] = M[j, i] = v
    return M


def restrict(M: np.ndarray, D: int, T) -> Point:
    T = list(T)
    return Point.make(len(T), D, [int(M[T[a], T[b]]) for a in range(len(T)) for b in range(a + 1, len(T))])


def fiber_vertex(y: Point, holes) -> bool:
    """y is a vertex of {z in m_k : z agrees with y off the hole pairs}: tight rows on hole columns have full rank."""
    if not holes:
        return True
    A, _ = core.ineq_matrix(y.n)
    T = core.tight_set(y)
    cols = [core.pidx(y.n, i, j) for (i, j) in holes]
    return certified_rank_is(A[np.ix_(T, cols)], len(cols))


def radial_preds(y: Point):
    """Yield (U, v_mask_nodes) such that some switching of y equals Λ^{|U|}(y'|R), |U| in 1..3, |R| >= 3."""
    k, D = y.n, y.D
    M = matrix(y)
    Ys = []
    for s in range(1 << (k - 1)):
        side = np.array([0] + [(s >> (v - 1)) & 1 for v in range(1, k)])
        flip = side[:, None] != side[None, :]
        Ys.append(np.where(flip, D - M, M))
    Ys = np.stack(Ys)                                      # (2^(k-1), k, k)
    for m in (1, 2, 3):
        if k - m < 3:
            break
        for U in itertools.combinations(range(k), m):
            R = [v for v in range(k) if v not in U]
            cross = Ys[:, list(U)][:, :, R]                     # (S, m, |R|)
            a = cross[:, 0, 0]
            ok = (cross == a[:, None, None]).all(axis=(1, 2))
            if m > 1:
                inner = Ys[:, list(U)][:, :, list(U)]
                iu = np.triu_indices(m, 1)
                ok &= (inner[:, iu[0], iu[1]] == 2 * a[:, None]).all(axis=1)
            rest = Ys[:, R][:, :, R]
            ok &= (2 * a == rest.reshape(len(Ys), -1).max(axis=1))   # α = radius of v = max(v)/2
            if ok.any():
                yield U, R


class DP:
    def __init__(self, base, vertex_mode):
        self.base, self.vmode = base, vertex_mode
        self.memo = {}          # canonical key -> (depth, how)

    def point_depth(self, x: Point):
        M = matrix(x)
        n = x.n
        d_of = {}               # bitmask -> depth for this x
        key_of = {}
        for size in range(3, n + 1):
            for T in itertools.combinations(range(n), size):
                mask = sum(1 << v for v in T)
                y = restrict(M, x.D, T)
                k = group.canonical(y).key()
                key_of[mask] = k
                if k not in self.memo:
                    self.memo[k] = self._solve(y, T, mask, d_of, M, x.D)
                d_of[mask] = self.memo[k][0]
        return d_of[(1 << n) - 1], key_of[(1 << n) - 1]

    def _solve(self, y, T, mask, d_of, M, D):
        if group.canonical(y).key() in self.base.get(y.n, ()):
            return (0, "base")
        if self.vmode and not p_vertex(y):
            return (INF, None)
        best, how = INF, None
        Tl = list(T)
        # lift
        for a, v in enumerate(Tl):
            sub = mask & ~(1 << v)
            if len(Tl) - 1 < 3 or d_of.get(sub, INF) + 1 >= best:
                continue
            if self.vmode and not p_vertex(restrict(M, D, [w for w in Tl if w != v])):
                continue
            holes = [(min(a, b), max(a, b)) for b in range(len(Tl)) if b != a]
            if fiber_vertex(y, holes):
                best, how = d_of[sub] + 1, ("lift", v)
        if best <= 1:
            return (best, how)
        # radial (local labels of y)
        for U, R in radial_preds(y):
            sub = sum(1 << Tl[r] for r in R)
            if d_of.get(sub, INF) + 1 < best:
                if self.vmode and not p_vertex(restrict(M, D, [Tl[r] for r in R])):
                    continue
                best, how = d_of[sub] + 1, ("radial", tuple(Tl[u] for u in U))
        if best <= 1:
            return (best, how)
        # glue, uncapped: A ∪ B = T, A ∩ B ≠ ∅, both proper; enumerate A ⊂ T, K = A ∩ B ⊂ A (nonempty, ≠ A)
        t = len(Tl)
        for amask_local in range(1, (1 << t) - 1):
            A = [Tl[i] for i in range(t) if (amask_local >> i) & 1]
            if len(A) < 3:
                continue
            Amask = sum(1 << v for v in A)
            dA = d_of.get(Amask, INF)
            if dA + 1 >= best:
                continue
            rest = [v for v in Tl if v not in A]
            for kk in range(1, len(A)):
                for K in itertools.combinations(A, kk):
                    B = sorted(rest + list(K))
                    if len(B) < 3:
                        continue
                    Bmask = sum(1 << v for v in B)
                    dB = d_of.get(Bmask, INF)
                    if max(dA, dB) + 1 >= best:
                        continue
                    if self.vmode and not (p_vertex(restrict(M, D, A)) and p_vertex(restrict(M, D, B))):
                        continue
                    onlyA = [Tl.index(v) for v in A if v not in K]
                    onlyB = [Tl.index(v) for v in rest]
                    holes = [(min(i, j), max(i, j)) for i in onlyA for j in onlyB]
                    if fiber_vertex(y, holes):
                        best, how = max(dA, dB) + 1, ("glue", tuple(A), tuple(B))
        return (best, how)


def base_keys(I, rules, max_n):
    out = {}
    for name in rules:
        r = I.rules[name]
        d = tuple(r.meta.get("domain", (3,)))
        for n in range(max(3, d[0]), min(max_n, d[1] if len(d) > 1 else max_n) + 1):
            for p in I.run_rule(r, n):
                if p.n == n and p_feasible(p):
                    out.setdefault(n, set()).add(group.canonical(p).key())
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_job_args(ap)
    ap.add_argument("--max-n", type=int, default=8)
    ap.add_argument("--sample", type=int, default=0, help="time only K random n=max-n reps (no report)")
    args = ap.parse_args()
    I = Interpreter(seed=args.seed)
    for f in ("stdlib.mpr", "literature.mpr"):
        I.load_file(ROOT / "rules" / f)
    I.finalize()
    B = base_keys(I, UNIFORM, args.max_n)
    if args.sample:
        rng = np.random.default_rng(args.seed)
        reps = deza.load_ext(args.max_n)
        pick = sorted(rng.choice(len(reps), args.sample, replace=False))
        for mode in (False, True):
            dp = DP(B, mode)
            t = time.time()
            ds = [dp.point_depth(reps[i])[0] for i in pick]
            dt = time.time() - t
            print(f"{'vertex' if mode else 'detour'} mode: {args.sample} reps in {dt:.1f}s "
                  f"({dt / args.sample:.2f}s/rep, memo {len(dp.memo)}); depths {ds}", flush=True)
        return
    job = Job(f"detour_depth2_n{args.max_n}", {"max_n": args.max_n, "base": UNIFORM}, args.seed,
              resume=args.resume, force=args.force)
    for mname, vmode in (("detour", False), ("vertex", True)):
        dp = DP(B, vmode)
        for n in range(4, args.max_n + 1):
            task = f"{mname}@{n}"
            if job.is_done(task):
                continue
            reps = deza.load_ext(n)
            prog = Progress(task, len(reps), every=30)
            rows, t = [], time.time()
            for i, x in enumerate(reps, 1):
                d, k = dp.point_depth(x)
                rows.append({"orbit": i, "depth": None if d == INF else d, "den": x.D,
                             "how": str(dp.memo[k][1])})
                prog.step()
            job.record(task, {"rows": rows, "seconds": round(time.time() - t, 1), "memo": len(dp.memo)})
    report(job, args)


def report(job, args):
    R = job.results()
    md = ["# Derivation depth with all moves (lift, radial 1–3, uncapped gluing)", "",
          f"code_version `{job.state['code_version']}`, git `{job.state['git_head']}`", "",
          "| n | orbits | vertex-only: ∞ | vertex-only histogram | detours: ∞ | detour histogram | max detour depth | last move used (detour, finite) |",
          "|---|---|---|---|---|---|---|---|"]
    out = {}
    for n in range(4, args.max_n + 1):
        v, f = R[f"vertex@{n}"]["rows"], R[f"detour@{n}"]["rows"]
        hv, hf = Counter(r["depth"] for r in v), Counter(r["depth"] for r in f)
        fin = [r["depth"] for r in f if r["depth"] is not None]
        moves = Counter(r["how"].split("'")[1] if "'" in r["how"] else r["how"] for r in f if r["depth"])
        fmt = lambda h: ", ".join(f"{k}:{c}" for k, c in sorted((k, c) for k, c in h.items() if k is not None))
        md.append(f"| {n} | {len(f)} | {hv.get(None, 0)} | {fmt(hv)} | {hf.get(None, 0)} | {fmt(hf)} | "
                  f"{max(fin) if fin else '—'} | {dict(moves)} |")
        out[str(n)] = {"vertex_inf": hv.get(None, 0), "detour_inf": hf.get(None, 0),
                       "detour_inf_orbits": [r["orbit"] for r in f if r["depth"] is None],
                       "detour_inf_denominators": dict(Counter(r["den"] for r in f if r["depth"] is None))}
    atomic_write_json(ROOT / "results" / "phase4c" / "detour_depth2.json", {"summary": out, "raw": R})
    atomic_write_text(ROOT / "results" / "phase4c" / "detour_depth2.md", "\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
