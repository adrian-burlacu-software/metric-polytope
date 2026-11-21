#!/usr/bin/env python3
"""Shortest derivation depth of every vertex orbit of m_n (n = 4..8), with and without non-vertex detours.

Backward recursion over single-node deletions (each step = one lift-fiber move, read backwards):
  depth(x) = 0                              if orbit(x) is a base piece of size |x|
           = 1 + min_i depth(x \\ i)         over nodes i such that x is a vertex of the fiber over x \\ i
                                            (VERTEX mode: additionally x \\ i must be a vertex of m_{|x|-1})
           = inf                            otherwise.
Memoised by canonical form (depth is G-invariant). Vertices of m_n are always fiber vertices over any deletion.

Base set UNIFORM (rules defined for every n <= 8: cuts, anticuts, complete multipartite (1/3)-metrics with and without
one edge, Avis doubling of paths, tree suspensions, graph metrics x_G of every connected graph).
Base pieces include NON-vertex outputs (they are constructions, not data).
Moves not represented: binary gluing, 2- and 3-node radial extensions.

Usage: python -u scripts/detour_depth.py [--max-n 8] [--resume] [--force]
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import core, deza, group  # noqa: E402
from metricpoly.dsl.interp import Interpreter  # noqa: E402
from metricpoly.dsl.prims import certified_rank_is, p_feasible, p_restrict, p_vertex  # noqa: E402
from metricpoly.jobs import Job, Progress, add_job_args, atomic_write_json, atomic_write_text  # noqa: E402

UNIFORM = ["gen-cuts", "gen-anticuts", "gen-multipartite", "gen-avis-paths", "gen-tree-suspension", "gen-graphic"]
RICH_EXTRA = []   # graph metrics now available for all n <= 8; cone rays (n <= 6) add nothing there
INF = math.inf


def fiber_vertex(x, i) -> bool:
    """Is x a vertex of the fiber {z in m_n : z \\ i = x \\ i}?  <=> tight rows restricted to the n-1 hole columns
    (pairs containing i) have rank n-1."""
    n = x.n
    A, _ = core.ineq_matrix(n)
    T = core.tight_set(x)
    cols = [core.pidx(n, i, j) for j in range(n) if j != i]
    return certified_rank_is(A[np.ix_(T, cols)], n - 1)


class Depth:
    def __init__(self, base_keys, vertex_mode):
        self.base = base_keys            # n -> set of canonical keys
        self.vmode = vertex_mode
        self.memo = {}                   # key -> (depth, next_key or None)

    def __call__(self, x):
        k = group.canonical(x).key()
        if k in self.memo:
            return self.memo[k][0]
        if k in self.base.get(x.n, ()):
            self.memo[k] = (0, None)
            return 0
        if x.n <= 3:
            self.memo[k] = (INF, None)
            return INF
        self.memo[k] = (INF, None)       # provisional (no cycles: sizes strictly decrease)
        best, arg = INF, None
        cand = []
        for i in range(x.n):
            y = p_restrict(frozenset(set(range(x.n)) - {i}), x)
            ky = group.canonical(y).key()
            cand.append((ky, i, y))
        seen = set()
        for ky, i, y in sorted(cand, key=lambda t: t[0]):
            if ky in seen:
                continue
            seen.add(ky)
            if self.vmode and not p_vertex(y):
                continue
            if not fiber_vertex(x, i):
                continue
            d = self(y)
            if d + 1 < best:
                best, arg = d + 1, ky
        self.memo[k] = (best, arg)
        return best

    def chain(self, x):
        k = group.canonical(x).key()
        out = [k]
        while self.memo.get(k, (INF, None))[1] is not None:
            k = self.memo[k][1]
            out.append(k)
        return out


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
    args = ap.parse_args()
    job = Job("detour_depth", {"max_n": args.max_n, "uniform": UNIFORM, "rich_extra": RICH_EXTRA}, args.seed,
              resume=args.resume, force=args.force)
    I = Interpreter(seed=args.seed)
    for f in ("stdlib.mpr", "literature.mpr"):
        I.load_file(ROOT / "rules" / f)
    I.finalize()
    bases = {"uniform": base_keys(I, UNIFORM, args.max_n)}
    for bname, B in bases.items():
        print(f"base {bname}: " + ", ".join(f"n={n}: {len(v)}" for n, v in sorted(B.items())), flush=True)
    for bname, B in bases.items():
        DV, DF = Depth(B, True), Depth(B, False)
        for n in range(4, args.max_n + 1):
            task = f"{bname}@{n}"
            if job.is_done(task):
                continue
            reps = deza.load_ext(n)
            prog = Progress(task, len(reps), every=20)
            rows = []
            t = time.time()
            for i, x in enumerate(reps, 1):
                dv, df = DV(x), DF(x)
                rows.append({"orbit": i, "dV": None if dv == INF else dv, "dF": None if df == INF else df,
                             "den": x.D, "chainF": DF.chain(x)})
                prog.step()
            job.record(task, {"rows": rows, "seconds": round(time.time() - t, 1),
                              "memo_V": len(DV.memo), "memo_F": len(DF.memo)})
    report(job, args)


def report(job, args):
    R = job.results()
    md = ["# Derivation depth with and without non-vertex detours", "",
          f"code_version `{job.state['code_version']}`, git `{job.state['git_head']}`", "",
          "d_V: shortest chain of single-node deletions to a base piece through **vertices** only; "
          "d_F: intermediates may be any feasible point that is a vertex of the fiber over the next one. "
          "∞ = no such chain. Moves not represented: binary gluing, 2-/3-node radial.", ""]
    summary = {}
    for bname in ("uniform",):
        md += [f"## Base set: {bname}", "",
               "| n | orbits | d_V = ∞ | d_V histogram | d_F = ∞ | d_F histogram | max d_F | mean d_F | mean (d_V − d_F) where both finite |",
               "|---|---|---|---|---|---|---|---|---|"]
        for n in range(4, args.max_n + 1):
            rec = R.get(f"{bname}@{n}")
            if not rec:
                continue
            rows = rec["rows"]
            hv = Counter(r["dV"] for r in rows)
            hf = Counter(r["dF"] for r in rows)
            fin = [r["dF"] for r in rows if r["dF"] is not None]
            both = [r["dV"] - r["dF"] for r in rows if r["dV"] is not None and r["dF"] is not None]
            fmt = lambda h: ", ".join(f"{k}:{v}" for k, v in sorted(((k, v) for k, v in h.items() if k is not None)))
            md.append(f"| {n} | {len(rows)} | {hv.get(None, 0)} | {fmt(hv)} | {hf.get(None, 0)} | {fmt(hf)} | "
                      f"{max(fin) if fin else '—'} | {sum(fin) / len(fin) if fin else float('nan'):.2f} | "
                      f"{sum(both) / len(both) if both else float('nan'):.2f} |")
            summary[f"{bname}@{n}"] = {"dV_inf": hv.get(None, 0), "dF_inf": hf.get(None, 0),
                                       "hist_dV": {str(k): v for k, v in hv.items()},
                                       "hist_dF": {str(k): v for k, v in hf.items()}}
        md.append("")
    atomic_write_json(ROOT / "results" / "phase4c" / "detour_depth.json", {"summary": summary, "raw": R})
    atomic_write_text(ROOT / "results" / "phase4c" / "detour_depth.md", "\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
