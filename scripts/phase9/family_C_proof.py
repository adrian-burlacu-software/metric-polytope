#!/usr/bin/env python3
"""Exact verification of the finite facts used in the proof of Theorem 4 (docs/paper_draft.md) about the family C_t.

C_inf is the metric on the line: points A_i, B_i (i in Z),
    d(A_i, A_j) = 16, 12, 8  for |i - j| = 1, 2, >= 3;   d(B_i, B_j) = 10, 20, 22 for |i - j| = 1, 2, >= 3;
    d(A_i, B_{i+o}) = 13, 11, 7, 9, 19 for o = -2, -1, 0, 1, 2 and 15 for |o| >= 3.
C_t is the same rule with cyclic offsets (t odd, t >= 9).

(V1) Patterns. Distances depend on offsets capped at 3, and every capped configuration of three points occurs
     already in C_9 and in a window of 13 positions of the line. So: C_9 is a metric => C_t and C_inf are metrics;
     and the types of tight triples are the same for all t >= 9 and for the line. Checked: C_9 metric; the tight
     triples of a line window and of C_9, C_11, C_13 have the same 11 types.
(V2) Solutions on the line. For any alpha and any sequence (s_j) with  s_i + 2 s_{i+3} + s_{i+4} = (7/2) alpha  (REC),
     the assignment
        x(A_i A_j) = alpha (|i-j| >= 3), 2 alpha (|i-j| = 1),   x(A_i A_{i+2}) = e_i = q_i - s_{i+2},
        x(A_i B_i) = s_i,  x(A_i B_{i+1}) = p_i = 2 alpha - s_{i+1},
        x(A_i B_{i+2}) = q_i = -2 alpha + s_{i+2} + 2 s_{i+4} + 2 s_{i+5},
        x(A_i B_{i-1}) = m_i = q_{i-3} - alpha,   x(A_i B_{i-2}) = w_i = s_{i-2} + 2 s_{i+1} - alpha,
        x(A_i B_j) = alpha + s_j (|i-j| >= 3),
        x(B_i B_{i+1}) = b_i = q_{i-1} - 2 alpha + s_i,  x(B_i B_{i+2}) = b_i + b_{i+1},
        x(B_i B_j) = s_i + s_j + alpha (|i-j| >= 3)
     satisfies every tight triple of C_inf. Checked symbolically: the residual of each tight equation in a window is
     a rational combination of instances of REC.
(V3) Separation (Lemma S). Let lambda be the real root of z^3 + z^2 - z + 1 (lambda ~ -1.839), a root of
     z^4 + 2 z^3 + 1, so s_j = 7 + lambda^j, alpha = 8 solves REC. For this solution the normalised deviations
     Dn(P) = (x(P) - d(P)) / d(P) of two pairs of the line coincide only if the pairs are in the same class
     (both among the A-A pairs at distance 1 or >= 3, or both of the form A_i B_j, A_i' B_j with |i-j|, |i'-j| >= 3).
     Checked exactly in Q(lambda), with rigorous rational bounds for the infinitely many remaining cases.
Output results/phase9/family_C_proof.json.
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

from family_C import metric as cyc_metric  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402

A1, A2, AF = 16, 12, 8
BV = {1: 10, 2: 20}
GV = {-2: 13, -1: 11, 0: 7, 1: 9, 2: 19}


# ---------------------------------------------------------------- the line metric
def dline(x, y):
    (kx, i), (ky, j) = x, y
    if kx == ky:
        k = abs(i - j)
        if kx == "A":
            return {1: A1, 2: A2}.get(k, AF)
        return BV.get(k, 22)
    if kx == "B":
        (kx, i), (ky, j) = y, x
    return GV.get(j - i, 15)


def ptype(x, y):
    (kx, i), (ky, j) = x, y
    if kx == ky:
        k = abs(i - j)
        return kx + kx + (str(k) if k <= 2 else "F")
    if kx == "B":
        (kx, i), (ky, j) = y, x
    o = j - i
    return "AB" + (("%+d" % o) if abs(o) <= 2 else "F")


def tight_types(points, dist):
    out = set()
    for x, y in itertools.combinations(points, 2):
        for m in points:
            if m != x and m != y and dist(x, y) == dist(x, m) + dist(m, y):
                out.add((ptype(x, y), tuple(sorted((ptype(x, m), ptype(m, y))))))
    return out


# ---------------------------------------------------------------- V2: linear forms in (alpha, s_j)
class LF(dict):
    """Linear form: keys 'a' (alpha) or integer j (s_j)."""
    def __add__(self, o):
        r = LF(self)
        for k, v in o.items():
            r[k] = r.get(k, 0) + v
        return LF({k: v for k, v in r.items() if v})

    def __sub__(self, o):
        return self + o.scale(-1)

    def scale(self, c):
        return LF({k: v * c for k, v in self.items() if v * c})


def S(j):
    return LF({j: Fr(1)})


AL = LF({"a": Fr(1)})


def q_(i):
    return AL.scale(-2) + S(i + 2) + S(i + 4).scale(2) + S(i + 5).scale(2)


def b_(i):
    return q_(i - 1) - AL.scale(2) + S(i)


def xval(x, y):
    (kx, i), (ky, j) = x, y
    if kx == ky == "A":
        if i > j:
            i, j = j, i
        k = j - i
        return AL.scale(2) if k == 1 else (q_(i) - S(i + 2) if k == 2 else AL)
    if kx == ky == "B":
        if i > j:
            i, j = j, i
        k = j - i
        return b_(i) if k == 1 else (b_(i) + b_(i + 1) if k == 2 else S(i) + S(j) + AL)
    if kx == "B":
        (kx, i), (ky, j) = y, x
    o = j - i
    if o == 0:
        return S(i)
    if o == 1:
        return AL.scale(2) - S(i + 1)
    if o == 2:
        return q_(i)
    if o == -1:
        return q_(i - 3) - AL
    if o == -2:
        return S(i - 2) + S(i + 1).scale(2) - AL
    return AL + S(j)


def in_span(target, rows, keys):
    """Is the vector `target` in the row span of `rows`? (exact Gaussian elimination)"""
    M = [[r.get(k, Fr(0)) for k in keys] for r in rows] + [[target.get(k, Fr(0)) for k in keys]]
    piv_rows = []
    r = 0
    ncol = len(keys)
    last = len(M) - 1
    for c in range(ncol):
        p = next((i for i in range(r, last) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        inv = 1 / M[r][c]
        M[r] = [v * inv for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
        if r == last:
            break
    return all(v == 0 for v in M[last])


# ---------------------------------------------------------------- V3: arithmetic in Q(lambda), lambda^3 = -lambda^2 + lambda - 1
def red(p):
    """p: dict exponent(int, may be negative) -> Fraction. Reduce to (c0, c1, c2) in the basis 1, lambda, lambda^2.
    Negative exponents: 1/lambda = -lambda^2 - lambda + 1 (from lambda^3 + lambda^2 - lambda + 1 = 0)."""
    c = [Fr(0), Fr(0), Fr(0)]
    for e, v in p.items():
        vec = power(e)
        for k in range(3):
            c[k] += v * vec[k]
    return tuple(c)


_pw = {0: (Fr(1), Fr(0), Fr(0))}


def mulx(v):          # times lambda
    c0, c1, c2 = v
    return (-c2, c0 + c2, c1 - c2)


def divx(v):          # times 1/lambda = 1 - lambda - lambda^2
    c0, c1, c2 = v
    # (c0 + c1 L + c2 L^2)(1 - L - L^2) reduced:  use inverse of mulx: mulx(w) = v  =>  w2 = -c0, w0 = c1 - w2, w1 = c2 + w2
    w2 = -c0
    return (c1 - w2, c2 + w2, w2)


def power(e):
    if e not in _pw:
        if e > 0:
            _pw[e] = mulx(power(e - 1))
        else:
            _pw[e] = divx(power(e + 1))
    return _pw[e]


def lam_bounds():
    """Rational interval containing the real root of z^3 + z^2 - z + 1."""
    f = lambda z: z ** 3 + z ** 2 - z + 1
    lo, hi = Fr(-2), Fr(-1)
    assert f(lo) < 0 < f(hi)
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return lo, hi


LO, HI = lam_bounds()           # LO < lambda < HI < 0


def ev_bounds(v):
    """Rigorous bounds for c0 + c1*lambda + c2*lambda^2 with lambda in [LO, HI] (both negative)."""
    c0, c1, c2 = v
    t1 = sorted((c1 * LO, c1 * HI))
    t2 = sorted((c2 * LO * LO, c2 * HI * HI))
    return c0 + t1[0] + t2[0], c0 + t1[1] + t2[1]


def abs_bounds(v):
    lo, hi = ev_bounds(v)
    if lo > 0:
        return lo, hi
    if hi < 0:
        return -hi, -lo
    return Fr(0), max(-lo, hi)


def is_zero(v):
    return v == (0, 0, 0)       # 1, lambda, lambda^2 are linearly independent over Q (the cubic is irreducible)


# deviation polynomials of the near types, anchored at i = 0 (deviation of x; divide by d for Dn)
def dev_poly(lf):
    return {k: v for k, v in lf.items() if k != "a"}


NEAR = {
    "s (A_i B_i)": (dev_poly(S(0)), 7),
    "p (A_i B_i+1)": (dev_poly(xval(("A", 0), ("B", 1))), 9),
    "q (A_i B_i+2)": (dev_poly(q_(0)), 19),
    "m (A_i B_i-1)": (dev_poly(xval(("A", 0), ("B", -1))), 11),
    "w (A_i B_i-2)": (dev_poly(xval(("A", 0), ("B", -2))), 13),
    "b (B_i B_i+1)": (dev_poly(b_(0)), 10),
    "c (B_i B_i+2)": (dev_poly(b_(0) + b_(1)), 20),
    "e (A_i A_i+2)": (dev_poly(q_(0) - S(2)), 12),
    "F (A_k B_i, far)": (dev_poly(S(0)), 15),
}


def main():
    out = {}
    # ---------------- V1
    d9 = cyc_metric(9)
    n = 18
    metric9 = all(d9[i][j] <= d9[i][m] + d9[m][j] for i in range(n) for j in range(n) for m in range(n))
    win = [(k, i) for k in "AB" for i in range(13)]
    tl = tight_types(win, dline)
    cyc_types = {}
    for t in (9, 11, 13):
        d = cyc_metric(t)
        pts = [("A", i) for i in range(t)] + [("B", i) for i in range(t)]
        idx = {p: k for k, p in enumerate(pts)}

        def cdist(x, y, d=d, idx=idx):
            return int(d[idx[x]][idx[y]])

        def ctype(x, y, t=t):
            (kx, i), (ky, j) = x, y
            o = (j - i) % t
            if o > t // 2:
                o -= t
            if kx == ky:
                return kx + kx + (str(abs(o)) if abs(o) <= 2 else "F")
            if kx == "B":
                o = -o
            return "AB" + (("%+d" % o) if abs(o) <= 2 else "F")

        s = set()
        for x, y in itertools.combinations(pts, 2):
            for m in pts:
                if m != x and m != y and cdist(x, y) == cdist(x, m) + cdist(m, y):
                    s.add((ctype(x, y), tuple(sorted((ctype(x, m), ctype(m, y))))))
        cyc_types[t] = s
    out["V1"] = {"C_9_is_a_metric": bool(metric9), "tight_types_line": sorted(map(str, tl)),
                 "same_types_on_cycles_9_11_13": all(cyc_types[t] == tl for t in cyc_types)}
    print("V1: C_9 metric:", metric9, "| tight triple types on the line:", len(tl),
          "| same on C_9, C_11, C_13:", out["V1"]["same_types_on_cycles_9_11_13"], flush=True)

    # ---------------- V2
    pts = [(k, i) for k in "AB" for i in range(0, 13)]
    rec = [S(i) + S(i + 3).scale(2) + S(i + 4) - AL.scale(Fr(7, 2)) for i in range(-12, 26)]
    keys = ["a"] + list(range(-14, 34))
    bad, nt = 0, 0
    for x, y in itertools.combinations(pts, 2):
        for m in pts:
            if m != x and m != y and dline(x, y) == dline(x, m) + dline(m, y):
                nt += 1
                resid = xval(x, y) - xval(x, m) - xval(m, y)
                if resid and not in_span(resid, rec, keys):
                    bad += 1
    nominal = all(xval(x, y).get("a", 0) * 8 + sum(v for k, v in xval(x, y).items() if k != "a") * 7 == dline(x, y)
                  for x, y in itertools.combinations(pts, 2))
    out["V2"] = {"tight_triples_in_window": nt, "not_implied_by_REC": bad, "formulas_reproduce_d_at_alpha8_s7": bool(nominal)}
    print(f"V2: {nt} tight triples in a 13-position window of the line; {bad} not implied by REC; "
          f"formulas give d at alpha = 8, s = 7: {nominal}", flush=True)

    # ---------------- V3
    assert is_zero(red({4: Fr(1), 3: Fr(2), 0: Fr(1)}))                 # lambda is a root of z^4 + 2z^3 + 1
    L2 = (LO * LO, HI * HI)                                             # |lambda| in (-HI, -LO)
    lam_lo, lam_hi = -HI, -LO
    info = {}
    vals = {}
    for name, (poly, dd) in NEAR.items():
        v = red({k: val / dd for k, val in poly.items()})
        lo, hi = abs_bounds(v)
        assert lo > 0, name
        vals[name] = v
        info[name] = {"Dn_at_anchor_0": [str(c) for c in v], "abs_lower": float(lo), "abs_upper": float(hi)}
    # (a) two near types (or F), relative shift k: Dn1 = lambda^k Dn2 ?
    coincid = []
    K = 0
    names = list(NEAR)
    import math
    for n1 in names:
        for n2 in names:
            lo1, hi1 = abs_bounds(vals[n1])
            lo2, hi2 = abs_bounds(vals[n2])
            # |lambda|^k = |v1| / |v2| in [lo1/hi2, hi1/lo2]; k range from rigorous bounds
            kmax = 0
            while lam_lo ** (kmax + 1) <= hi1 / lo2:
                kmax += 1
            kmin = 0
            while Fr(1) / (lam_lo ** (-(kmin - 1))) >= lo1 / hi2:
                kmin -= 1
            K = max(K, kmax, -kmin)
            for k in range(kmin - 1, kmax + 2):
                if n1 == n2 and k == 0:
                    continue
                v2 = vals[n2]
                for _ in range(abs(k)):
                    v2 = mulx(v2) if k > 0 else divx(v2)
                if is_zero(tuple(a - b for a, b in zip(vals[n1], v2))):
                    coincid.append((n1, n2, k))
    # (b) far B-B pairs: Dn = (lambda^i + lambda^j)/22, g = j - i >= 3, against a near type at shift r:
    #     (1 + lambda^g)/22 = lambda^r * v_T   <=>   22 lambda^r v_T - 1 = lambda^g
    far_coincid = []
    hmax = 100
    for n2 in names:
        kap = tuple(22 * c for c in vals[n2])                      # kappa = 22 v_T ; equation: lambda^h (1 + lambda^-g) = kappa, h = g - r
        klo, khi = abs_bounds(kap)
        assert klo * lam_lo ** hmax > 3 and khi < lam_lo ** hmax / 3     # outside |h| <= hmax: |kappa lambda^-h - 1| > 1/2 > |lambda|^-3
        for h in range(-hmax, hmax + 1):
            v = kap
            for _ in range(abs(h)):
                v = divx(v) if h > 0 else mulx(v)                  # kappa * lambda^(-h)
            c = (v[0] - 1, v[1], v[2])                             # must equal lambda^(-g) for some g >= 3
            if is_zero(c):
                continue
            lo, hi = abs_bounds(c)
            if lo > Fr(1) / lam_lo ** 3:                           # |c| > |lambda|^-3 >= |lambda|^-g
                continue
            g = 3
            while Fr(1) / lam_lo ** g >= lo and g < 5000:          # |lambda|^-g <= lam_lo^-g ; stop once that is below |c|
                if is_zero(tuple(a - b for a, b in zip(c, power(-g)))):
                    far_coincid.append((n2, h, g))
                g += 1
            assert g < 5000
    # (c) nonvanishing of Dn for every non-alpha class: near types checked above (abs_lower > 0); far B-B: |lambda| != 1
    out["V3"] = {"lambda_interval": [float(LO), float(HI)], "near_types": info,
                 "coincidences_between_near_types": coincid, "shift_range_checked": K,
                 "coincidences_farBB_vs_near": far_coincid}
    print(f"V3: lambda in [{float(LO):.12f}, {float(HI):.12f}]; near-type deviations all nonzero; "
          f"coincidences between near types (shift range up to {K} by rigorous bounds): {coincid}; "
          f"far B-B against near types: {far_coincid}", flush=True)
    atomic_write_json(ROOT / "results/phase9/family_C_proof.json", out)


if __name__ == "__main__":
    main()
