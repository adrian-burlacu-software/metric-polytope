#!/usr/bin/env python3
"""The complete level-s linear closure of C_t for small s (lower bounds for the linear locality), exact arithmetic.

Dual form of the definition in linear_locality.py: a pool of linear relations among the class variables u_C. For a
set W of s points, R_W is the span of the tight equations inside W and of the pool relations supported on the
variables of W; the minimal-support relations (circuits) of every R_W are added to the pool. At the fixed point,
two classes are merged when u_C - u_C' is in the pool; then everything is rebuilt with the coarser partition.
Since R_W n (relations on a subset Y of the variables) is spanned by the circuits of R_W inside Y, this is the
largest consistent family of the definition, for the family of all sets of s points.

C_t is invariant under the rotation; the pool and the merges are closed under it, so only one set per rotation
orbit is treated.

  python scripts/phase9/linear_full.py --t 9 --s 4 5
  python scripts/phase9/linear_full.py --t 10 --s 5 --check --maxsec 420     (fault test: C_10 is not extreme)
Output results/phase9/linear_full.json (appended)
"""
import argparse
import itertools
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
from linear_locality import rref, nullspace  # noqa: E402
from linear_family import Closure  # noqa: E402


def circuits(R, nv):
    """All minimal-support vectors (up to scaling) of the row space of R (rref rows over nv variables), as dicts
    {var_index: coefficient} normalised to first coefficient 1."""
    r = len(R)
    out = {}
    if r == 0:
        return out
    # a circuit has support of size <= nv - r + 1; for each support size, solve
    cols = list(range(nv))
    for size in range(1, nv - r + 2):
        for supp in itertools.combinations(cols, size):
            # skip if it contains a smaller circuit's support
            ss = set(supp)
            if any(set(k) <= ss for k in out):
                continue
            # find a combination of rows vanishing outside supp: solve a * R[:, comp] = 0
            comp = [c for c in cols if c not in ss]
            M = [[R[i][c] for i in range(r)] for c in comp]            # equations on a (r unknowns)
            Rr, piv = rref(M, r) if M else ([], [])
            if len(piv) == r:
                continue
            free = [c for c in range(r) if c not in set(piv)]
            a = [Fraction(0)] * r
            a[free[0]] = Fraction(1)
            for i, pc in enumerate(piv):
                a[pc] = -Rr[i][free[0]]
            v = [sum(a[i] * R[i][c] for i in range(r)) for c in supp]
            if all(x != 0 for x in v):
                out[supp] = [x / v[0] for x in v]
    return out


def solution_basis(C):
    """Basis of the solutions of the full tight system T(d), as vectors u_p = x_p / d_p indexed by pair id."""
    n, d, key = C.n, C.d, C.key
    rows = set()
    for a, b in itertools.combinations(range(n), 2):
        for m in range(n):
            if m != a and m != b and d[a][b] == d[a][m] + d[m][b]:
                r = [0] * len(C.pairs)
                r[key(a, b)] += d[a][b]; r[key(a, m)] -= d[a][m]; r[key(m, b)] -= d[m][b]
                rows.add(tuple(r))
    return nullspace([[Fraction(x) for x in r] for r in rows], len(C.pairs))


def full_closure(t, s, log=print, check=False, maxsec=0):
    """check: assert that every relation put in the pool holds on every solution of T(d) (soundness, relation by
    relation). maxsec: stop after the first pass that ends later than this; returns the state reached."""
    C = Closure(t)
    n = C.n
    t0 = time.time()
    sol = solution_basis(C) if check else []
    if check:
        log(f"  t = {t}: solution space of T(d) has dimension {len(sol)} ({time.time() - t0:.0f} s)")
    rot = lambda x, k: (x + k) % t if x < t else t + (x - t + k) % t
    reps = sorted({min(tuple(sorted(rot(x, k) for x in W)) for k in range(t)) for W in itertools.combinations(range(n), s)})
    tight = {W: [(a, m, b) for a, b in itertools.combinations(W, 2) for m in W
                 if m != a and m != b and C.d[a][b] == C.d[a][m] + C.d[m][b]] for W in reps}
    rounds = 0
    while True:
        rounds += 1
        find, key, d = C.find, C.key, C.d
        vars_of = {W: sorted({find(key(a, b)) for a, b in itertools.combinations(W, 2)}) for W in reps}
        pool = {}                      # frozenset of (var, coef) items -> True ; stored as tuple(sorted(items))
        by_var = {}

        def add(rel):                   # rel: dict var -> coef (normalised), added with all rotations
            new = False
            for k in range(t):
                rr = {}
                for v, c in rel.items():
                    w = find(C.rot[k][v])
                    rr[w] = rr.get(w, 0) + c
                rr = {v: c for v, c in rr.items() if c != 0}
                if not rr:
                    continue
                v0 = min(rr)
                kk = tuple(sorted((v, c / rr[v0]) for v, c in rr.items()))
                if kk not in pool:
                    for u in sol:
                        assert sum(c * u[v] for v, c in kk) == 0, ("unsound relation", kk)
                    pool[kk] = True
                    by_var.setdefault(kk[0][0], []).append(kk)
                    new = True
            return new

        passes = 0
        while True:
            passes += 1
            grew = False
            for W in reps:
                vs = vars_of[W]
                ix = {v: i for i, v in enumerate(vs)}
                rows = []
                for a, m, b in tight[W]:
                    r = [Fraction(0)] * len(vs)
                    r[ix[find(key(a, b))]] += d[a][b]
                    r[ix[find(key(a, m))]] -= d[a][m]
                    r[ix[find(key(m, b))]] -= d[m][b]
                    rows.append(r)
                for v in vs:
                    for kk in by_var.get(v, ()):
                        if all(x in ix for x, _ in kk):
                            r = [Fraction(0)] * len(vs)
                            for x, c in kk:
                                r[ix[x]] = c
                            rows.append(r)
                R, _ = rref(rows, len(vs)) if rows else ([], [])
                for supp, coef in circuits(R, len(vs)).items():
                    grew |= add({vs[c]: x for c, x in zip(supp, coef)})
            log(f"    pass {passes}: pool {len(pool)} ({time.time() - t0:.0f} s)")
            if not grew:
                break
            if maxsec and time.time() - t0 > maxsec:
                log(f"  t = {t}, s = {s}: stopped after {time.time() - t0:.0f} s, pool {len(pool)}, classes {C.classes()}")
                return C.classes(), len(pool), False
        merged = False
        for kk in list(pool):
            if len(kk) == 2 and kk[0][1] == 1 and kk[1][1] == -1:
                merged |= C.merge(kk[0][0], kk[1][0])
        log(f"  t = {t}, s = {s}: round {rounds}: {len(reps)} set orbits, pool {len(pool)}, passes {passes}, classes {C.classes()}")
        if not merged or C.classes() == 1:
            return C.classes(), len(pool), True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t", type=int, nargs="+", default=[9])
    ap.add_argument("--s", type=int, nargs="+", default=[4])
    ap.add_argument("--check", action="store_true", help="assert the soundness of every relation derived")
    ap.add_argument("--maxsec", type=int, default=0)
    a = ap.parse_args()
    path = ROOT / "results/phase9/linear_full.json"
    out = json.loads(path.read_text()) if path.exists() else []
    for t in a.t:
        for s in a.s:
            t0 = time.time()
            cls, pool, done = full_closure(t, s, log=lambda m: print(m, flush=True), check=a.check, maxsec=a.maxsec)
            r = {"t": t, "s": s, "classes": cls, "total": cls == 1, "pool": pool, "finished": done,
                 "relations_checked_sound": a.check, "seconds": round(time.time() - t0, 1)}
            out.append(r)
            print(r, flush=True)
            path.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
