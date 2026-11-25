#!/usr/bin/env python3
"""Locality of an extreme ray: how many nodes must be looked at simultaneously to prove it is a ray.

For a metric d on k nodes write x_p = d_p * u_p for a solution x of the tight system (u = all-ones is d itself).
d is an extreme ray iff the tight triangle equalities force all u_p equal. Level-s closure: for every s-subset W of
the nodes, take the tight triples inside W (in the current classes of pairs), solve that small system exactly, and
merge the classes it forces to be equal; repeat over all W until nothing changes. The locality L(d) is the smallest
s at which one class remains. The closure at s + 1 contains the closure at s, and s = k is the definition, so
4 <= L <= k for every ray. A combinatorial rule that inspects at most s nodes at a time (with any amount of
propagation between the inspections) can certify only rays with L <= s.

Sets: the {1,2} family (complete for k <= 8; samples at 9, 10, 11 plus the rays missed by round 18's closure), and
all weights: every cut-adjacent orbit of m_7 and m_8 and a random sample of m_9 (as rays, simplest switching).
Exact arithmetic (Fractions). Output results/phase9/locality.json and .md.
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
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

import family12 as F  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def _forced_equal(rows, nv):
    """rows: list of dicts var -> int over variables 0..nv-1. Groups of variables equal on the whole solution space
    (the all-ones vector is a solution, so proportional means equal)."""
    M = [[Fraction(r.get(j, 0)) for j in range(nv)] for r in rows]
    piv, r = [], 0
    for c in range(nv):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        inv = 1 / M[r][c]
        M[r] = [v * inv for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv.append(c)
        r += 1
        if r == len(M):
            break
    free = [c for c in range(nv) if c not in piv]
    expr = {}
    for c in free:
        expr[c] = tuple(1 if f == c else 0 for f in free)
    for i, c in enumerate(piv):
        expr[c] = tuple(-M[i][f] for f in free)
    groups = {}
    for c, e in expr.items():
        groups.setdefault(e, []).append(c)
    return [g for g in groups.values() if len(g) > 1]


def locality(k, d, smax=None):
    """Smallest s such that the level-s closure proves d is a ray; None if not reached by smax (default k)."""
    P = list(itertools.combinations(range(k), 2))
    idx = {p: i for i, p in enumerate(P)}
    par = list(range(len(P)))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    T = [(a, b, m) for a, b in P for m in range(k) if m != a and m != b and d[a][b] == d[a][m] + d[m][b]]
    ncls = len(P)
    for s in range(4, (smax or k) + 1):
        subs = []
        for W in itertools.combinations(range(k), s):
            Ws = set(W)
            tw = [(idx[(a, b)], idx[(min(a, m), max(a, m))], idx[(min(m, b), max(m, b))], d[a][b], d[a][m], d[m][b])
                  for a, b, m in T if a in Ws and b in Ws and m in Ws]
            if tw:
                subs.append(tw)
        changed = True
        while changed and ncls > 1:
            changed = False
            for tw in subs:
                rows, seen, var = [], set(), {}
                for pa, pp, pq, da, dp, dq in tw:
                    r = {}
                    for cl, c in ((find(pa), da), (find(pp), -dp), (find(pq), -dq)):
                        r[cl] = r.get(cl, 0) + c
                    r = {c_: v for c_, v in r.items() if v}
                    key = tuple(sorted(r.items()))
                    if r and key not in seen:
                        seen.add(key)
                        rows.append(r)
                for r in rows:
                    for c_ in r:
                        var.setdefault(c_, len(var))
                if len(var) < 2:
                    continue
                names = list(var)
                for g in _forced_equal([{var[c_]: v for c_, v in r.items()} for r in rows], len(var)):
                    for j in g[1:]:
                        ra, rb = find(names[g[0]]), find(names[j])
                        if ra != rb:
                            par[ra] = rb
                            ncls -= 1
                            changed = True
        if ncls == 1:
            return s
    return None


def _job(args):
    tag, k, edges = args
    d = F.metric(k, edges).tolist()
    return tag, k, locality(k, d)


def load_sets(a):
    rng = np.random.default_rng(a.seed)
    fam = ROOT / "results/phase9/family12"
    items = []

    def pick(lst, m):
        if len(lst) <= m:
            return lst
        return [lst[i] for i in sorted(rng.choice(len(lst), m, replace=False))]

    for k in (5, 6, 7, 8):
        items += [("family12 (complete)", r["k"], r["edges"]) for r in json.loads((fam / f"rays_k{k}.json").read_text())]
    items += [("family12 (m_9 data sample)", r["k"], r["edges"])
              for r in pick(json.loads((fam / "rays_k9.json").read_text()), a.fam9)]
    items += [("round 18 closure misses", r["k"], r["edges"])
              for r in json.loads((ROOT / "phase9/round_18/maker/_k9_closure_misses.json").read_text())]
    br = ROOT / "phase9/round_18/breaker"
    items += [("round 18 closure misses", r["k"], r["edges"]) for r in json.loads((br / "candidates.json").read_text())
              if r.get("claim") not in (None, "generic") and "iff" in str(r.get("claim"))]
    new = json.loads((br / "new_rays.json").read_text())
    for k in (10, 11):
        items += [("family12 (breaker's constructions)", r["k"], r["edges"]) for r in pick([r for r in new if r["k"] == k], a.brk)]
    # all weights: m_7, m_8 (every cut-adjacent orbit) and a sample of m_9
    from graph_families import analyse
    from vertex_structure import load_set
    for key, x in load_set("m8", 0, 0):
        if x.D > 1 and x.n in (7, 8):
            r = analyse((key, x))
            if r is not None:
                k, e = F.relabel([tuple(t) for t in r["edges"]])
                items.append((f"all weights, m_{x.n} (every orbit)", k, e))
    ck = sorted((ROOT / "checkpoints/phase9/gfam9").glob("chunk_*.json"))
    per = a.m9 // len(ck) + 1
    for f in ck:
        rows = [r for r in json.loads(f.read_text())["rows"] if r["nodes"] == 9]
        for r in pick(rows, per):
            k, e = F.relabel([tuple(t) for t in r["edges"]])
            items.append(("all weights, m_9 (sample)", k, e))
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fam9", type=int, default=2000)
    ap.add_argument("--brk", type=int, default=600)
    ap.add_argument("--m9", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--seed", type=int, default=20261125)
    ap.add_argument("--limit", type=int, default=0, help="timing test: only the first N items of a shuffled list")
    a = ap.parse_args()
    t0 = time.time()
    items = load_sets(a)
    if a.limit:
        order = np.random.default_rng(1).permutation(len(items))[:a.limit]
        items = [items[i] for i in order]
    print(f"{len(items)} rays loaded ({time.time() - t0:.0f} s)", flush=True)
    tab = {}
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for n, (tag, k, L) in enumerate(pool.imap_unordered(_job, items, chunksize=4), 1):
            tab.setdefault(tag, {}).setdefault(k, Counter())[L] += 1
            if n % 1000 == 0:
                print(f"  {n} of {len(items)} ({time.time() - t0:.0f} s)", flush=True)
    out = {"seconds": round(time.time() - t0, 1), "sets": {}}
    md = ["# Locality of extreme rays", "",
          "L = smallest number of nodes that must be examined together (level-s closure, see `scripts/phase9/locality.py`). "
          "4 <= L <= k; L = k means only the full tight system proves the ray.", ""]
    for tag in sorted(tab):
        md += [f"## {tag}", "", "| k | rays | " + " | ".join(f"L = {s}" for s in range(4, 12)) + " | max L | share with L >= 6 |",
               "|---|---|" + "---|" * 10]
        out["sets"][tag] = {}
        for k in sorted(tab[tag]):
            c = tab[tag][k]
            n = sum(c.values())
            assert None not in c, (tag, k)                       # every input is a ray, so the closure must end by s = k
            out["sets"][tag][str(k)] = {str(s): v for s, v in sorted(c.items())}
            md.append(f"| {k} | {n} | " + " | ".join(str(c.get(s, "")) for s in range(4, 12)) +
                      f" | {max(c)} | {sum(v for s, v in c.items() if s >= 6) / n:.2%} |")
            print(f"{tag} k = {k}: {dict(sorted(c.items()))}", flush=True)
        md.append("")
    if not a.limit:
        atomic_write_json(ROOT / "results/phase9/locality.json", out)
        (ROOT / "results/phase9/locality.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"done ({out['seconds']} s)", flush=True)


if __name__ == "__main__":
    main()
