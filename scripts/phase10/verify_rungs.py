#!/usr/bin/env python3
"""Phase 10 setup checks (exact). Writes results/phase10/verify_rungs.json.

 (a) Inequality list of each rung = projection of m_n onto E(G_k). P_k ⊇ proj(m_n) holds row by row (every row of
     P_k is a row of m_n or 0 <= x <= 1); P_k ⊆ proj(m_n) iff every vertex of P_k extends to a point of m_n.
     - n = 6 (nK = 5), every k: ALL vertices of P_k (cdd) checked to extend (exact LP). Exact equality.
     - n = 8, 9 (nK = 7, 8), every k: 40 random vertices of P_k (exact LP, random integer objective) each extend to a
       point of m_n (exact LP feasibility in the missing coordinates). (Inclusion P_k ⊇ proj m_n is immediate:
       every row of P_k is a row of m_n, or 0 <= x <= 1, valid on m_n.)
 (b) Canonical form and stabiliser of every rung at n = 6 vs brute force over the whole rung group.
 (c) Full rung (k = nK): canonical partition and orbit sizes vs metricpoly.canon_large / group at n = 8 (533 reps),
     sum of orbit sizes = |V(m_8)|; random group images keep the key at k = 3, 5 (n = 9).
Seed 20261122.
"""
import itertools
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np
import cdd
import cdd.gmp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from metricpoly import deza, group  # noqa: E402
from metricpoly.canon_large import canonical_key as full_key  # noqa: E402
from metricpoly.core import Point, pairs  # noqa: E402
from metricpoly.dsl.prims import p_vertices  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402
from metricpoly.ladder import Rung  # noqa: E402

rng = np.random.default_rng(20261122)


def h_vertices(A, b):
    mat = cdd.gmp.matrix_from_array([[Fraction(int(bi))] + [Fraction(-int(v)) for v in row] for row, bi in zip(A, b)],
                                    rep_type=cdd.RepType.INEQUALITY)
    g = cdd.gmp.copy_generators(cdd.gmp.polyhedron_from_matrix(mat))
    return {tuple(Fraction(v) for v in r[1:]) for r in g.array if r[0] == 1}


def v_hull_vertices(pts):
    mat = cdd.gmp.matrix_from_array([[Fraction(1)] + list(p) for p in pts], rep_type=cdd.RepType.GENERATOR)
    P = cdd.gmp.polyhedron_from_matrix(mat)
    H = cdd.gmp.copy_inequalities(P)
    rows = [(r[1:], r[0]) for r in H.array]                  # r0 + r.x >= 0
    lin = set(H.lin_set)
    # convert to A x <= b and enumerate vertices again (gives the extreme points only)
    A, b = [], []
    for t, (a, r0) in enumerate(rows):
        A.append([-v for v in a]); b.append(r0)
        if t in lin:
            A.append(list(a)); b.append(-r0)
    mat2 = cdd.gmp.matrix_from_array([[Fraction(bi)] + [Fraction(-v) for v in row] for row, bi in zip(A, b)],
                                     rep_type=cdd.RepType.INEQUALITY)
    g = cdd.gmp.copy_generators(cdd.gmp.polyhedron_from_matrix(mat2))
    return {tuple(Fraction(v) for v in r[1:]) for r in g.array if r[0] == 1}


def lp_vertex(R, c):
    """Exact LP: maximise c.x over P_k; returns the optimal vertex (cdd)."""
    arr = [[Fraction(int(bi))] + [Fraction(-int(v)) for v in row] for row, bi in zip(R.A, R.b)]
    arr.append([Fraction(0)] + [Fraction(int(v)) for v in c])
    lp = cdd.gmp.linprog_from_array(arr, obj_type=cdd.LPObjType.MAX)
    cdd.gmp.linprog_solve(lp)
    return [Fraction(v) for v in lp.primal_solution]


def extends(R, x):
    """Exact LP feasibility: exists z on the missing pairs with (x, z) in m_n."""
    n = R.n
    P = pairs(n)
    known = {e: x[t] for t, e in enumerate(R.edges)}
    miss = [e for e in P if e not in known]
    if not miss:
        return True
    midx = {e: t for t, e in enumerate(miss)}
    rows = []
    for i, j, l in itertools.combinations(range(n), 3):
        es = [(i, j), (i, l), (j, l)]
        for coef, rhs in [((1, -1, -1), 0), ((-1, 1, -1), 0), ((-1, -1, 1), 0), ((1, 1, 1), 2)]:
            a = [Fraction(0)] * len(miss)
            r = Fraction(rhs)
            for c_, e in zip(coef, es):
                if e in known:
                    r -= c_ * known[e]
                else:
                    a[midx[e]] += c_
            rows.append([r] + [-v for v in a])               # r - a.z >= 0
    rows.append([Fraction(0)] + [Fraction(0)] * len(miss))
    lp = cdd.gmp.linprog_from_array(rows, obj_type=cdd.LPObjType.MAX)
    cdd.gmp.linprog_solve(lp)
    return lp.status == cdd.LPStatusType.OPTIMAL


def brute_orbits(R, verts):
    """Orbits of the rung group on a vertex list by brute force (all group elements)."""
    elems = []
    for perm in R.group_perms():
        for s in range(1 << (R.n - 1)):
            side = [0] + [(s >> (v - 1)) & 1 for v in range(1, R.n)]
            elems.append((perm, side))
    seen, orbits = {}, []
    for D, nums in verts:
        if (D, nums) in seen:
            continue
        orb = set()
        for perm, side in elems:
            orb.add(R.apply(D, nums, perm, side))
        oid = len(orbits)
        orbits.append(orb)
        for y in orb:
            seen[(D, y)] = oid
    return orbits, seen


def as_int(R, x):
    D = 1
    for f in x:
        D = D * f.denominator // np.gcd(D, f.denominator)
    return int(D), tuple(int(f * D) for f in x)


def main():
    out = {}
    t0 = time.time()
    # (a) exact at n = 6: P_k ⊇ proj(m_6) holds row by row; P_k ⊆ proj(m_6) iff EVERY vertex of P_k extends to m_6
    for k in range(0, 6):
        R = Rung(5, k)
        mine = h_vertices(R.A, R.b)
        ext = sum(1 for v in mine if extends(R, list(v)))
        out[f"a_n6_k{k}"] = {"P_k_vertices": len(mine), "vertices_extending_to_m6": ext, "equal": ext == len(mine)}
        print(f"a_n6_k{k}", out[f"a_n6_k{k}"], round(time.time() - t0, 1), flush=True)
    # (a) sampled at n = 8, 9
    for nK in (7, 8):
        for k in range(0, nK + 1):
            R = Rung(nK, k)
            ok = 0
            for _ in range(40):
                c = rng.integers(-5, 6, R.m)
                x = lp_vertex(R, c)
                ok += extends(R, x)
            out[f"a_n{nK + 1}_k{k}_random_vertices_extend"] = f"{ok}/40"
            print(f"a_n{nK + 1}_k{k}", f"{ok}/40", round(time.time() - t0, 1), flush=True)
    print({k: v for k, v in out.items() if k.startswith("a_n8") or k.startswith("a_n9")}, round(time.time() - t0, 1), flush=True)
    # (b) brute force at n = 6
    for k in range(0, 6):
        R = Rung(5, k)
        verts = [as_int(R, v) for v in h_vertices(R.A, R.b)]
        orbits, seen = brute_orbits(R, verts)
        keys = {}
        for D, nums in verts:
            keys.setdefault(R.canonical_key(D, nums), set()).add(seen[(D, nums)])
        size_ok = all(R.orbit_size(D, nums) == len(orbits[seen[(D, nums)]]) for D, nums in verts)
        out[f"b_n6_k{k}"] = {"vertices": len(verts), "brute_orbits": len(orbits), "key_orbits": len(keys),
                             "partition_equal": len(keys) == len(orbits) and all(len(v) == 1 for v in keys.values()),
                             "orbit_sizes_equal": size_ok}
    print({k: v for k, v in out.items() if k.startswith("b_")}, round(time.time() - t0, 1), flush=True)
    # (c) full rung at n = 8
    R = Rung(7, 7)
    reps = list(deza.load_ext(8))
    ks = set()
    tot = 0
    size_bad = 0
    for x in reps:
        nums = tuple(x.nums[[*pairs(8)].index(e)] for e in R.edges)
        ks.add(R.canonical_key(x.D, nums))
        o = R.orbit_size(x.D, nums)
        tot += o
        size_bad += o != group.group_order(8) // group.stabilizer_size(x)
    out["c_n8_full_rung"] = {"reps": len(reps), "distinct_keys": len(ks), "orbit_size_mismatch": size_bad,
                             "vertex_total": tot, "expected_total": 1550825600}
    bad = 0
    for k in (3, 5, 7, 8):
        R = Rung(8, k)
        for _ in range(30):
            x = lp_vertex(R, rng.integers(-5, 6, R.m))
            D, nums = as_int(R, x)
            key = R.canonical_key(D, nums)
            for _ in range(3):
                perm, side = R.random_element(rng)
                bad += R.canonical_key(D, R.apply(D, nums, perm, side)) != key
    out["c_n9_k3_k5_k7_k8_image_mismatch"] = bad
    out["seconds"] = round(time.time() - t0, 1)
    (ROOT / "results/phase10").mkdir(parents=True, exist_ok=True)
    atomic_write_json(ROOT / "results/phase10/verify_rungs.json", out)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
