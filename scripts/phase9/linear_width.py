#!/usr/bin/env python3
"""Multi-term local deduction on the family C_t ("linear locality").

For a family of point sets W we keep, for each W, a linear space S_W of candidate solutions on the pairs inside W;
initially S_W is the solution space of the tight equations inside W. A step takes two sets W, W' and replaces S_W
and S_W' by their parts that agree on the pairs inside W n W' (i.e. whose restrictions lie in the intersection of
the two projections). Every solution of the whole tight system, restricted to W, stays in S_W, so the procedure is
sound; dually, it derives exactly the linear relations that are supported inside one set of the family and are
obtained by combining relations inside single sets. If every S_W becomes the line through d, extremality has been
derived with relations confined to the sets of the family.

Family used here ("two windows"): W_j = all points A_i, B_i with i in [0, w) or in [j, j + w) (mod t), j in Z_t.
C_t is invariant under rotation, so if all S_{W_j} become lines the same holds for every start window, every pair
of points lies in one of these sets, and the scalars agree on overlaps: d is extreme, proved inside sets of at most
4w points, for every t at once as far as the number of points is concerned.

Arithmetic: modulo p = 2^31 - 1 by default (exploration); --exact repeats the run in rational arithmetic.
  python scripts/phase9/linear_width.py --t 11 13 15 17 19 21 23 25 27 29 31 33 37 41 45 51 --w 4 5
  python scripts/phase9/linear_width.py --t 11 13 15 17 21 25 29 33 37 --w 5 --exact
  python scripts/phase9/linear_width.py --t 10 12 14 20 26 --w 5 6 --tag _even     (fault test: not extreme)
Output results/phase9/linear_width[_exact][tag].json
"""
import argparse
import itertools
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
from family_C import metric  # noqa: E402

P = 2147483647


# ---------------------------------------------------------------- linear algebra (mod p with numpy, or Fractions)
def rref_mod(M):
    """Row-reduced echelon form mod P. Returns (R, pivots) with R the nonzero rows."""
    M = np.array(M, dtype=np.int64) % P
    if M.size == 0:
        return M.reshape(0, M.shape[1] if M.ndim == 2 else 0), []
    r, piv = 0, []
    rows, cols = M.shape
    for c in range(cols):
        if r == rows:
            break
        nz = np.nonzero(M[r:, c])[0]
        if nz.size == 0:
            continue
        k = r + int(nz[0])
        if k != r:
            M[[r, k]] = M[[k, r]]
        inv = pow(int(M[r, c]), P - 2, P)
        M[r] = (M[r] * inv) % P
        f = M[:, c].copy()
        f[r] = 0
        idx = np.nonzero(f)[0]
        if idx.size:
            M[idx] = (M[idx] - (f[idx, None] * M[r][None, :]) % P) % P
        piv.append(c)
        r += 1
    return M[:r], piv


def rref_frac(M):
    M = [[Fraction(x) for x in row] for row in M]
    r, piv = 0, []
    cols = len(M[0]) if M else 0
    for c in range(cols):
        if r == len(M):
            break
        k = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if k is None:
            continue
        M[r], M[k] = M[k], M[r]
        inv = 1 / M[r][c]
        M[r] = [x * inv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv.append(c)
        r += 1
    return M[:r], piv


class Field:
    def __init__(self, exact):
        self.exact = exact

    def rref(self, M, ncols):
        if len(M) == 0:
            return [], []
        if self.exact:
            return rref_frac(M)
        R, piv = rref_mod(M)
        return R, piv

    def nullspace(self, M, ncols):
        """Basis (list of rows) of {x : M x = 0}."""
        R, piv = self.rref(M, ncols)
        free = [c for c in range(ncols) if c not in set(piv)]
        out = []
        for f in free:
            v = [0] * ncols
            v[f] = 1
            for i, pc in enumerate(piv):
                x = R[i][f]
                v[pc] = (-x) if self.exact else int((-int(x)) % P)
            out.append(v)
        return out

    def matmul(self, U, B):
        if self.exact:
            return [[sum(u * b for u, b in zip(row, col)) for col in zip(*B)] for row in U]
        U = np.array(U, dtype=object)
        B = np.array(B, dtype=object)
        return (U.dot(B) % P).astype(np.int64)

    def basis(self, M, ncols):
        R, _ = self.rref(M, ncols)
        return [list(r) for r in R] if self.exact else np.array(R, dtype=np.int64)


# ---------------------------------------------------------------- the procedure
def window_sets(t, w):
    sets = []
    for j in range(t):
        pos = sorted(set(range(w)) | {(j + k) % t for k in range(w)})
        sets.append([i for i in pos] + [t + i for i in pos])  # A_i -> i, B_i -> t + i
    return sets


def local_space(F, d, W):
    pairs = list(itertools.combinations(W, 2))
    idx = {p: i for i, p in enumerate(pairs)}
    key = lambda a, b: idx[(a, b) if a < b else (b, a)]
    rows = []
    for a, b in pairs:
        for m in W:
            if m != a and m != b and d[a][b] == d[a][m] + d[m][b]:
                r = [0] * len(pairs)
                r[key(a, b)] += 1; r[key(a, m)] -= 1; r[key(m, b)] -= 1
                rows.append(r)
    B = F.nullspace(rows, len(pairs)) if rows else [[int(i == j) for j in range(len(pairs))] for i in range(len(pairs))]
    return pairs, idx, B


def restrict(F, S1, S2):
    """Mutual restriction of two (pairs, idx, basis) spaces on their common pairs. Returns True if something shrank."""
    p1, i1, B1 = S1
    p2, i2, B2 = S2
    common = [p for p in p1 if p in i2]
    if not common:
        return False
    k1, k2 = len(B1), len(B2)
    if k1 == 0 or k2 == 0:
        return False
    c1 = [i1[p] for p in common]
    c2 = [i2[p] for p in common]
    if F.exact:
        M = [[B1[r][a] for r in range(k1)] + [-B2[r][b] for r in range(k2)] for a, b in zip(c1, c2)]
    else:
        A1 = np.array(B1, dtype=np.int64)[:, c1].T
        A2 = (-np.array(B2, dtype=np.int64)[:, c2].T) % P
        M = np.concatenate([A1, A2], axis=1)
    N = F.nullspace(M, k1 + k2)          # (u, v) with u B1|C = v B2|C
    U = [row[:k1] for row in N]
    V = [row[k1:] for row in N]
    n1 = F.basis(F.matmul(U, B1), len(p1)) if U else []
    n2 = F.basis(F.matmul(V, B2), len(p2)) if V else []
    changed = len(n1) < k1 or len(n2) < k2
    S1[2] = n1
    S2[2] = n2
    return changed


def run(t, w, exact=False, log=None):
    F = Field(exact)
    d = np.array(metric(t)[0] if isinstance(metric(t), tuple) else metric(t)).tolist()
    sets = window_sets(t, w)
    S = [list(local_space(F, d, W)) for W in sets]
    dims0 = [len(s[2]) for s in S]
    sweeps = 0
    while True:
        changed = False
        for j in list(range(t)) + list(range(t - 1, -1, -1)):
            changed |= restrict(F, S[j], S[(j + 1) % t])
        sweeps += 1
        if not changed or sweeps > 6 * t:
            break
    dims = [len(s[2]) for s in S]
    return {"t": t, "w": w, "points_per_set": max(len(W) for W in sets), "exact": exact, "sweeps": sweeps,
            "initial_dims": [min(dims0), max(dims0)], "final_dims": [min(dims), max(dims)],
            "proved": max(dims) == 1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t", type=int, nargs="+", default=[9, 11, 13])
    ap.add_argument("--w", type=int, nargs="+", default=[3, 4, 5, 6])
    ap.add_argument("--exact", action="store_true")
    ap.add_argument("--tag", default="", help="suffix of the output file, e.g. _even for the fault test")
    a = ap.parse_args()
    out = []
    for w in a.w:
        for t in a.t:
            if 2 * w > t:
                continue
            t0 = time.time()
            r = run(t, w, a.exact)
            r["seconds"] = round(time.time() - t0, 1)
            out.append(r)
            print(f"t = {t:3d}  w = {w}  sets of <= {r['points_per_set']:2d} points  dims {r['initial_dims']} -> "
                  f"{r['final_dims']}  sweeps {r['sweeps']:3d}  proved = {r['proved']}  ({r['seconds']} s)", flush=True)
    path = ROOT / "results" / "phase9" / f"linear_width{'_exact' if a.exact else ''}{a.tag}.json"
    json.dump(out, open(path, "w"), indent=1)


if __name__ == "__main__":
    main()
