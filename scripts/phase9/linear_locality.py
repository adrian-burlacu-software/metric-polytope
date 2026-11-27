#!/usr/bin/env python3
"""Linear locality L_lin(d) of an extreme ray, in exact rational arithmetic.

Level-s linear closure. Start from the discrete partition pi of the pairs. For a set W of s points, T_W(pi) is the
system of the tight equations inside W in one variable u_C per class C that contains a pair inside W. Keep, for
every W, a subspace S_W of the solution space of T_W(pi); make the family consistent (for all W, W' the projections
of S_W and S_W' to their common variables are equal) by repeated mutual restriction; merge C and C' whenever
u_C = u_C' on some S_W; repeat with the coarser partition until nothing changes. L_lin(d) is the least s >= 4 for
which a single class remains. Without the exchange of relations between sets this is the level-s closure of
locality.py, so L_lin <= L.

  linear_closure(k, d, s) -> number of classes of the level-s linear closure
  linear_locality(k, d, smax) -> least s in [4, smax] with one class, or None

Runs on every ray of MET_5..8 with L >= 5 (L_lin = 4 when L = 4) and on the two rays of the m_9 list with L = 9.
  python scripts/phase9/linear_locality.py [--workers 12] [--limit N]
  python scripts/phase9/linear_locality.py --m9hard          (needs the local gfam9 checkpoints of locality.py --all9)
Output results/phase9/linear_locality.json, linear_locality_m9hard.json
"""
import argparse
import itertools
import json
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))


# ---------------------------------------------------------------- exact linear algebra on small matrices
def rref(M, ncols):
    M = [row[:] for row in M]
    r, piv = 0, []
    for c in range(ncols):
        if r == len(M):
            break
        k = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if k is None:
            continue
        M[r], M[k] = M[k], M[r]
        inv = 1 / Fraction(M[r][c])
        M[r] = [x * inv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv.append(c)
        r += 1
    return M[:r], piv


def nullspace(M, ncols):
    R, piv = rref(M, ncols)
    ps = set(piv)
    out = []
    for f in range(ncols):
        if f in ps:
            continue
        v = [Fraction(0)] * ncols
        v[f] = Fraction(1)
        for i, pc in enumerate(piv):
            v[pc] = -R[i][f]
        out.append(v)
    return out


def restrict(S1, S2):
    """S = [vars(list), index(dict), basis(list of rows)]. Mutual restriction on common variables; returns
    (changed1, changed2)."""
    v1, i1, B1 = S1
    v2, i2, B2 = S2
    common = [v for v in v1 if v in i2]
    if len(common) < 2 or not B1 or not B2:
        return False, False
    k1, k2 = len(B1), len(B2)
    c1 = [i1[v] for v in common]
    c2 = [i2[v] for v in common]
    M = [[B1[r][a] for r in range(k1)] + [-B2[r][b] for r in range(k2)] for a, b in zip(c1, c2)]
    N = nullspace(M, k1 + k2)
    if len(N) == k1 + k2:
        return False, False
    U = [[sum(row[r] * B1[r][c] for r in range(k1)) for c in range(len(v1))] for row in N]
    V = [[sum(row[k1 + r] * B2[r][c] for r in range(k2)) for c in range(len(v2))] for row in N]
    n1, _ = rref(U, len(v1))
    n2, _ = rref(V, len(v2))
    ch = (len(n1) < k1, len(n2) < k2)
    S1[2], S2[2] = n1, n2
    return ch


# ---------------------------------------------------------------- the closure
def linear_closure(k, d, s, exchange=True):
    pairs = list(itertools.combinations(range(k), 2))
    pid = {p: i for i, p in enumerate(pairs)}
    key = lambda a, b: pid[(a, b) if a < b else (b, a)]
    parent = list(range(len(pairs)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    sets = list(itertools.combinations(range(k), min(s, k)))
    tight = {W: [(a, m, b) for a, b in itertools.combinations(W, 2) for m in W
                 if m != a and m != b and d[a][b] == d[a][m] + d[m][b]] for W in sets}

    def build():
        fam = []
        for W in sets:
            vs = sorted({find(key(a, b)) for a, b in itertools.combinations(W, 2)})
            ix = {v: i for i, v in enumerate(vs)}
            rows = []
            for a, m, b in tight[W]:
                r = [Fraction(0)] * len(vs)
                r[ix[find(key(a, b))]] += d[a][b]
                r[ix[find(key(a, m))]] -= d[a][m]
                r[ix[find(key(m, b))]] -= d[m][b]
                rows.append(r)
            fam.append([vs, ix, nullspace(rows, len(vs))])
        return fam

    def merges(fam):
        done = False
        for vs, ix, B in fam:
            if not B:
                continue
            cols = {}
            for j, v in enumerate(vs):
                cols.setdefault(tuple(row[j] for row in B), []).append(v)
            for grp in cols.values():
                for v in grp[1:]:
                    a, b = find(grp[0]), find(v)
                    if a != b:
                        parent[b] = a
                        done = True
        return done

    while True:
        fam = build()
        if merges(fam):                    # two-term forcing first: cheap
            continue
        if not exchange:
            break
        # make the family consistent
        nbrs = [[j for j in range(len(fam)) if j != i and len(set(fam[i][0]) & set(fam[j][0])) >= 2] for i in range(len(fam))]
        queue = list(range(len(fam)))
        inq = [True] * len(fam)
        while queue:
            i = queue.pop()
            inq[i] = False
            for j in nbrs[i]:
                ci, cj = restrict(fam[i], fam[j])
                if cj and not inq[j]:
                    queue.append(j); inq[j] = True
                if ci and not inq[i]:
                    queue.append(i); inq[i] = True
        if not merges(fam):
            break
    return len({find(i) for i in range(len(pairs))})


def linear_locality(k, d, smax=None, exchange=True):
    for s in range(4, (smax or k) + 1):
        if linear_closure(k, d, s, exchange) == 1:
            return s
    return None


# ---------------------------------------------------------------- driver
def _job(a):
    import family12 as F
    from locality import locality
    tag, k, e = a
    d = F.metric(k, e).tolist()
    t0 = time.time()
    L = locality(k, d)
    if L == 4:
        return tag, k, L, 4, 0.0
    Ll = linear_locality(k, d, L)
    L0 = linear_locality(k, d, L, exchange=False)      # must reproduce L: check of this implementation
    assert L0 == L, (k, e, L, L0)
    return tag, k, L, Ll, time.time() - t0


def _job9(a):
    import family12 as F
    i, L, edges = a
    k, e = F.relabel([tuple(t) for t in edges])
    d = F.metric(k, e).tolist()
    t0 = time.time()
    return i, k, L, linear_locality(k, d, L), round(time.time() - t0, 1)


def run_m9hard(a):
    """The rays of the m_9 list with L >= 8 (ids from locality_m9all.json, metrics from the gfam9 checkpoints)."""
    import multiprocessing as mp
    want = {r["i"]: r["L"] for r in json.loads((ROOT / "results/phase9/locality_m9all.json").read_text())["L_ge_8"]}
    items = []
    for f in sorted((ROOT / "checkpoints/phase9/gfam9").glob("chunk_*.json")):
        for r in json.loads(f.read_text())["rows"]:
            if r["i"] in want:
                items.append((r["i"], want[r["i"]], r["edges"]))
    assert len(items) == len(want), (len(items), len(want))
    items.sort(key=lambda x: -x[1])
    if a.limit:
        items = items[:a.limit]
    t0 = time.time()
    rows = []
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for i, k, L, Ll, sec in pool.imap_unordered(_job9, items, chunksize=1):
            rows.append({"i": i, "k": k, "L": L, "L_lin": Ll, "seconds": sec})
            if len(rows) % 50 == 0 or a.limit:
                print(f"  {len(rows)} of {len(items)} ({time.time() - t0:.0f} s)  last: {rows[-1]}", flush=True)
    tab = Counter((r["L"], r["L_lin"]) for r in rows)
    print({f"L={L},Llin={Ll}": v for (L, Ll), v in sorted(tab.items())}, f"wall {time.time() - t0:.0f} s", flush=True)
    if not a.limit:
        json.dump({"seconds": round(time.time() - t0, 1), "table": {f"L={L},Llin={Ll}": v for (L, Ll), v in sorted(tab.items())},
                   "rows": sorted(rows, key=lambda r: r["i"])}, open(ROOT / "results/phase9/linear_locality_m9hard.json", "w"), indent=1)


def main():
    import multiprocessing as mp
    import numpy as np
    import family12 as F
    from vertex_structure import load_set
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--m9hard", action="store_true", help="the 428 rays of the m_9 list with L >= 8")
    a = ap.parse_args()
    if a.m9hard:
        return run_m9hard(a)
    t0 = time.time()
    with mp.get_context("spawn").Pool(a.workers) as pool:
        pts = [x for _k, x in load_set("m8", 0, 0) if x.D > 1]
        allr = [r for part in pool.imap_unordered(F._rays_of, pts, chunksize=4) for r in part]
        items = [("MET_5..8 (complete)", k, e) for k, e in F.dedupe(allr)]
        print(f"{len(items)} rays of MET_5..8 ({time.time() - t0:.0f} s)", flush=True)
        if a.limit:
            order = np.random.default_rng(1).permutation(len(items))[:a.limit]
            items = [items[i] for i in order]
        tab, secs, n = {}, [], 0
        for tag, k, L, Ll, sec in pool.imap_unordered(_job, items, chunksize=2):
            tab.setdefault(k, Counter())[(L, Ll)] += 1
            n += 1
            if L > 4:
                secs.append(sec)
            if n % 500 == 0:
                print(f"  {n} of {len(items)} ({time.time() - t0:.0f} s)", flush=True)
    out = {"seconds": round(time.time() - t0, 1), "rays_computed": len(secs),
           "cpu_seconds_per_ray": {"mean": round(sum(secs) / max(1, len(secs)), 2), "max": round(max(secs or [0]), 2)},
           "table": {str(k): {f"L={L},Llin={Ll}": v for (L, Ll), v in sorted(c.items())} for k, c in sorted(tab.items())}}
    for k, c in sorted(tab.items()):
        print(f"k = {k}:", {f"L={L},Llin={Ll}": v for (L, Ll), v in sorted(c.items())}, flush=True)
    print(f"{len(secs)} rays with L > 4 computed, mean {out['cpu_seconds_per_ray']['mean']} s, max "
          f"{out['cpu_seconds_per_ray']['max']} s per ray; wall {out['seconds']} s", flush=True)
    if not a.limit:
        json.dump(out, open(ROOT / "results/phase9/linear_locality.json", "w"), indent=1)


if __name__ == "__main__":
    main()
