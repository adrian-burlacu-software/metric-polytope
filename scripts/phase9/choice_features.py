#!/usr/bin/env python3
"""Can a local feature choose the step? (§12 follow-up, 2026-11-25)

For each useful level-k point of the fiber generator (useful_share.py) and each distinct kept one-node extension,
label useful / not and compute local features of the child (k+1 nodes) and of the step:
  excess      : tight triangle rows of the child - C(k+1, 2)
  new_excess  : tight rows through the new node - k (rows a determined step needs at least)
  new_rows    : tight rows through the new node
  is_vertex   : the child is a vertex of m_{k+1}
  anchor      : longest anchor of the step (§10)
  newD        : lcm of the new coordinates' denominators
  twin        : the new node is at distance 0 from an old node
Per step k -> k+1 and feature: the safe threshold (keeps every useful child) and the share of options it keeps;
also the same for the best pair (is_vertex or a threshold on one numeric feature).

Usage: python -u scripts/phase9/choice_features.py --n 8 --D 3 4 5 6 [--workers 16]
Writes results/phase9/choice_features_n{n}.json.
"""
from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import sys
import time
from collections import defaultdict
from fractions import Fraction
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
from useful_share import useful_sets  # noqa: E402

NUM = ["excess", "new_excess", "new_rows", "anchor", "newD"]


def child_features(k, D, parent, child):
    x = Point.make(k + 1, D, child)
    T = tight_rows(x)
    v = k
    new_rows = sum(1 for tri, _c, _h in T if v in tri)
    rows = []
    for tri, coef, _ in T:
        if v in tri:
            a, b = [w for w in tri if w != v]
            rows.append((a, b, 1 if coef[stt._pid(k + 1, min(v, a), max(v, a))] ==
                         coef[stt._pid(k + 1, min(v, b), max(v, b))] else 0))
    anc = stt.step(frozenset(range(k + 1)), v, rows)
    newnums = [child[core.pidx(k + 1, a, v)] for a in range(k)]
    newD = 1
    for t in newnums:
        d = Fraction(t, D).denominator
        newD = newD * d // math.gcd(newD, d)
    return {"excess": len(T) - core.dim(k + 1), "new_excess": new_rows - k, "new_rows": new_rows,
            "is_vertex": bool(core.is_vertex(x)[0]), "anchor": max(anc) if anc else 0, "newD": newD,
            "twin": any(t == 0 for t in newnums)}


def job(args):
    k, D, nums, useful_next = args
    keep, _tot = fiber_vertices((k, D, nums))
    seen, out = set(), []
    for r in keep:
        key = group.canonical(Point.make(k + 1, D, r)).key()
        if key in seen:
            continue
        seen.add(key)
        f = child_features(k, D, nums, r)
        f["useful"] = key in useful_next
        out.append(f)
    return out


def safe_threshold(rows, feat):
    """Both directions: keep f >= t or f <= t, with t the extreme useful value; returns best (keep share, rule)."""
    u = [r[feat] for r in rows if r["useful"]]
    if not u:
        return None
    best = None
    for rule, t, keep in (("ge", min(u), [r for r in rows if r[feat] >= min(u)]),
                          ("le", max(u), [r for r in rows if r[feat] <= max(u)])):
        share = len(keep) / len(rows)
        if best is None or share < best[0]:
            best = (round(share, 4), f"{feat} {'>=' if rule == 'ge' else '<='} {t}")
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--D", type=int, nargs="+", required=True)
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    from metricpoly import deza
    t0 = time.time()
    V = [x for x in deza.load_ext(a.n) if x.D > 1]
    res = {}
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for D in a.D:
            U = defaultdict(dict)
            for part in pool.imap_unordered(useful_sets, [(x, D) for x in V if D % x.D == 0], chunksize=4):
                for k, d in part.items():
                    U[int(k)].update(d)
            info = {}
            for k in range(4, a.n):
                nxt = set(U[k + 1])
                rows = [r for part in pool.imap_unordered(job, [(k, D, r, nxt) for r in U[k].values()], chunksize=8)
                        for r in part]
                nu = sum(r["useful"] for r in rows)
                st = {"options": len(rows), "useful": nu}
                for f in NUM:
                    st[f] = safe_threshold(rows, f)
                    st[f + "_useful_vs_not"] = [sorted(set(r[f] for r in rows if r["useful"])),
                                                sorted(set(r[f] for r in rows if not r["useful"]))]
                for b in ("is_vertex", "twin"):
                    st[b] = {"useful": sum(r[b] for r in rows if r["useful"]),
                             "not_useful": sum(r[b] for r in rows if not r["useful"])}
                info[f"{k}->{k + 1}"] = st
                print(f"D={D} {k}->{k + 1}: {nu}/{len(rows)} useful; " +
                      "; ".join(f"{f}: {st[f]}" for f in NUM) +
                      f"; is_vertex {st['is_vertex']}; twin {st['twin']} ({time.time() - t0:.0f} s)", flush=True)
            res[str(D)] = info
            atomic_write_json(ROOT / "results/phase9" / f"choice_features_n{a.n}.json", res)


if __name__ == "__main__":
    main()
