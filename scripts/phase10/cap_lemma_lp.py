#!/usr/bin/env python3
"""Cap-lemma completeness test for Deza's m_n vertex list, using the SMAPO facet classes of CUT_n.

Cap lemma. P a polytope with connected vertex graph, K the listed vertices, H ⊆ K the unexpanded ("hard") vertices,
every vertex of K \\ H expanded (all its neighbours in K). For a linear F with F <= 0 on H, the vertices with F > 0
form a connected subgraph avoiding H (strictly F-increasing paths to the connected optimal face); hence if that
cap contains a vertex of K, all its vertices are in K. With H = the cut orbit, conv(H) = CUT_n is full-dimensional,
every vertex of m_n outside H lies in the cap of some facet of CUT_n, and one LP per facet class decides each cap:
max F over m_n <= 0 (empty cap, certified by exact dual multipliers) or attained at a vertex w (exact vertex check);
if w is listed, the cap is listed. Symmetry: for g in the group, the cap of gF has optimum gw, also listed.
Inputs needed besides this script: the closure result that all non-cut orbits of the list were expanded with no
outside neighbour (n = 8: results/phase10/closure_n8.json), and completeness of the CUT_n facet list (literature).

Checks on the SMAPO data (data/smapo/raw, sha256 in data/smapo/SHA256SUMS.txt), all exact:
  each class representative a·x <= 0 is valid on all 2^(n-1) cuts; its tight cuts number = ROOTS (stt) and have rank
  C(n,2) - 1 (a facet); class size recomputed as 2^(n-1) * (facets at the zero cut) / roots, where the facets at the
  zero cut are the switchings of the representative by its roots, counted by S_n-orbit sizes (bliss), = stt column;
  sum of class sizes = stated total.
Negative control: drop from the list the orbit hit by one LP and confirm the test fails.

Usage: python -u scripts/phase10/cap_lemma_lp.py --n 8
Writes results/phase10/cap_lemma_n{n}.json.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import sys
import time
from fractions import Fraction
from pathlib import Path

import cdd
import cdd.gmp
import igraph as ig
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from metricpoly import deza  # noqa: E402
from metricpoly.canon_large import canonical_key  # noqa: E402
from metricpoly.core import Point, ineq_matrix, pairs  # noqa: E402
from metricpoly.dsl.prims import certified_rank_is  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402

RAW = ROOT / "data" / "smapo" / "raw"


def parse_classes(n):
    txt = (RAW / f"swcut_{n}").read_text()
    m = C2 = n * (n - 1) // 2
    out = []
    for ln in txt.splitlines():
        mm = re.match(r"\s*\(\s*\d+\)\s*(.*)<=\s*(-?\d+)\s*$", ln)
        if mm:
            a = [int(v) for v in mm.group(1).split()]
            if len(a) != m:
                raise RuntimeError(f"bad row length {len(a)}")
            out.append((tuple(a), int(mm.group(2))))
    hdr = re.search(r"INDEX\s*\n(.*)\n", txt).group(1).split()
    letters = "ABCDEFGHIJ"
    if hdr != [letters[i] + letters[j] for i, j in pairs(n)]:
        raise RuntimeError("coordinate order differs from pairs(n)")
    return out


def parse_stt(n):
    txt = (RAW / f"swcut_{n}.stt").read_text()
    total = int(re.search(r"Total number of facets:\s*(\d+)", txt).group(1))
    rows = []
    for ln in txt.splitlines():
        p = ln.split()
        if len(p) == 4 and all(t.isdigit() for t in p):
            rows.append(tuple(int(t) for t in p))        # number, roots, facets at the zero cut, facets in class
    return total, rows


def cuts(n):
    pr = pairs(n)
    for bits in range(1 << (n - 1)):
        S = {i for i in range(n - 1) if bits >> i & 1}
        yield S, np.array([1 if ((i in S) != (j in S)) else 0 for i, j in pr], dtype=np.int64)


def switch(a, b, S, pr):
    """a·x <= b switched by S: x_e -> 1 - x_e on δ(S)."""
    a2 = [(-v if ((i in S) != (j in S)) else v) for v, (i, j) in zip(a, pr)]
    b2 = b - sum(v for v, (i, j) in zip(a, pr) if (i in S) != (j in S))
    return tuple(a2), b2


def sn_orbit(n, a):
    pr = pairs(n)
    vals = sorted(set(a))
    col = {v: k + 1 for k, v in enumerate(vals)}
    edges = []
    for e, (i, j) in enumerate(pr):
        edges += [(i, n + e), (j, n + e)]
    g = ig.Graph(n=n + len(pr), edges=edges)
    colors = [0] * n + [col[v] for v in a]
    lab = g.canonical_permutation(color=colors)
    order = [v for v in lab if v < n]
    idx = {e: t for t, e in enumerate(pr)}
    key = tuple(a[idx[(min(order[x], order[y]), max(order[x], order[y]))]] for x, y in pr)
    return key, math.factorial(n) // g.count_automorphisms(color=colors)


def check_facet(n, a, b):
    pr = pairs(n)
    av = np.array(a, dtype=np.int64)
    tight, ok = [], True
    for S, c in cuts(n):
        v = int(av @ c)
        if v > b:
            ok = False
        if v == b:
            tight.append((S, c))
    # facet of the full-dimensional CUT_n: tight cuts affinely span a hyperplane (affine rank C(n,2) - 1)
    base = tight[0][1]
    M = np.array([c - base for _, c in tight[1:]], dtype=np.int64)
    is_facet = ok and len(M) >= len(pr) - 1 and bool(certified_rank_is(M, len(pr) - 1))
    at0 = {}
    for S, c in tight:
        a2, b2 = switch(a, b, S, pr)
        assert b2 == 0
        k, sz = sn_orbit(n, a2)
        at0[k] = sz
    return ok, is_facet, len(tight), sum(at0.values())


def lp_max(A, b, c):
    rows = [[Fraction(int(bi))] + [Fraction(-int(v)) for v in row] for bi, row in zip(b, A)]
    rows.append([Fraction(0)] + [Fraction(int(v)) for v in c])
    lp = cdd.gmp.linprog_from_array(rows, cdd.LPObjType.MAX)
    cdd.gmp.linprog_solve(lp)
    if lp.status != cdd.LPStatusType.OPTIMAL:
        raise RuntimeError(f"LP status {lp.status}")
    x = [Fraction(v) for v in lp.primal_solution]
    val = Fraction(lp.obj_value)
    # exact dual certificate: y >= 0, y^T A = c, y^T b = val  (proves val is the maximum)
    y = [Fraction(0)] * len(A)
    for i, v in lp.dual_solution:
        y[i] = Fraction(v)
    cert = all(v >= 0 for v in y) and \
        all(sum(y[i] * int(A[i, t]) for i in range(len(A)) if y[i]) == int(c[t]) for t in range(A.shape[1])) and \
        sum(y[i] * int(b[i]) for i in range(len(A)) if y[i]) == val and \
        sum(Fraction(int(c[t])) * x[t] for t in range(A.shape[1])) == val
    return x, val, cert


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    a_ = ap.parse_args()
    n = a_.n
    t0 = time.time()
    pr = pairs(n)
    classes = parse_classes(n)
    total, stt = parse_stt(n)
    if len(classes) != len(stt):
        raise RuntimeError(f"{len(classes)} classes vs {len(stt)} stt rows")
    # --- verify the facet data
    fac_ok, sizes = True, []
    for (a, b), (num, roots, atv, facets) in zip(classes, stt):
        valid, is_facet, ntight, at0 = check_facet(n, a, b)
        size = (1 << (n - 1)) * at0 // roots if roots else None
        good = valid and is_facet and ntight == roots and at0 == atv and size == facets
        fac_ok &= good
        sizes.append(size)
        if not good:
            print(f"class {num}: valid {valid} facet {is_facet} tight {ntight}/{roots} at0 {at0}/{atv} "
                  f"size {size}/{facets}", flush=True)
    print(f"facet data: {len(classes)} classes, all checks {'pass' if fac_ok else 'FAIL'}, "
          f"sum of sizes {sum(s for s in sizes if s)} vs stated {total}, {time.time() - t0:.0f} s", flush=True)
    # --- the listed orbits
    reps = list(deza.load_ext(n))
    listed = {canonical_key(p) for p in reps}
    cut_key = canonical_key(Point.make(n, 1, tuple([0] * len(pr))))
    if cut_key not in listed or len(listed) != len(reps):
        raise RuntimeError("list problem")
    # --- one LP per class
    A, b = ineq_matrix(n)
    res, hits = [], {}
    for k, (a, rhs) in enumerate(classes):
        x, val, cert = lp_max(A, b, a)
        r = {"class": k + 1, "max": str(val - rhs), "dual_certified": cert}
        if val > rhs:
            D = 1
            for f in x:
                D = D * f.denominator // math.gcd(D, f.denominator)
            p = Point.make(n, D, tuple(int(f * D) for f in x))
            sl = b * p.D - A @ np.array(p.nums, dtype=np.int64)
            T = np.nonzero(sl == 0)[0]
            is_v = bool((sl >= 0).all()) and certified_rank_is(A[T], len(pr))
            key = canonical_key(p)
            r.update(vertex=bool(is_v), listed=key in listed, is_cut=key == cut_key, D=p.D, key=key)
            hits.setdefault(key, []).append(k + 1)
        else:
            r.update(empty_cap=True)
        res.append(r)
    passed = fac_ok and all(r["dual_certified"] for r in res) and \
        all(r.get("empty_cap") or (r["vertex"] and r["listed"]) for r in res)
    # --- negative control: drop one optimum orbit (not the cut) from the list and re-evaluate the pass condition
    ctrl = None
    for key, cls in hits.items():
        if key != cut_key:
            listed2 = listed - {key}
            failing = [r["class"] for r in res if not r.get("empty_cap") and r["key"] not in listed2]
            ctrl = {"dropped_orbit": key, "classes_now_failing": failing, "test_fails": bool(failing)}
            break
    out = {"n": n, "classes": len(classes), "facet_data_verified": fac_ok, "stated_total": total,
           "sum_class_sizes": sum(s for s in sizes if s), "lp": res,
           "positive_caps": sum(1 for r in res if not r.get("empty_cap")),
           "empty_caps": sum(1 for r in res if r.get("empty_cap")),
           "distinct_optimum_orbits": len(hits), "all_optima_listed": all(r.get("listed", True) for r in res),
           "negative_control": ctrl, "PASS": passed, "seconds": round(time.time() - t0, 1)}
    atomic_write_json(ROOT / "results" / "phase10" / f"cap_lemma_n{n}.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "lp"}), flush=True)


if __name__ == "__main__":
    main()
