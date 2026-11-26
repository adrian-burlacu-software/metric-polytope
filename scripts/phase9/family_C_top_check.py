#!/usr/bin/env python3
"""Independent re-implementation of the checks W1-W3 of Theorem 4(c) (docs/paper_draft.md): L(C_t) = 2t, t >= 23 odd.

Written from the statement of the proof in the paper, not from family_C_top.py; it shares no code with it (the
metric is redefined here and only compared with family_C.metric). What is different:

  * arithmetic in the basis 1, u, u^2 with u = 1/lam (u^3 = u^2 - u - 1) instead of 1, lam, lam^2;
  * the classes are catalogued differently. Fix R = 10. Every pair whose index lies within R of the removed point
    is a *window class* with an explicit value r0 + r1 eps (eps = u^t; no unknown exponent), computed pair by pair
    from the formulas of Step 1. Every other pair is in the *bulk*: its formula involves only sigma on the stretch,
    and its value is const + coef * u^k with R < k < t - R (k = distance to the left of the removed point). So there
    is no bookkeeping of "exceptional positions": the ranges are the same for all types;
  * the equation G = sum c_i u^(k_i) is solved by a different algorithm: in a solution, some term is at least
    |G| / (number of terms); enumerate that term and its exponent, subtract, recurse. If G = 0, divide by the
    term with the least exponent;
  * a solution is discarded only for one of three reasons that hold for every shift: it is the same class, an
    exponent k violates t - k >= its margin, or two B's of a far B-pair are closer than 3. Everything else is
    reported as a coincidence (so the test errs on the side of reporting);
  * ground truth: for each t in --guard the solution is built on the real cycle with arrays indexed mod t, every
    tight triple of C_t - v is checked, and the set of (catalogue entry, exponents) valid at t is compared with
    the set of classes of pi inside W, with their values. This checks ranges and values of the catalogue.

  python scripts/phase9/family_C_top_check.py [--guard 23 25 27 29 31 37 45] [--selftest]
Output results/phase9/family_C_top_check.json.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import random
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T0 = 23         # odd t >= T0
R = 10          # window radius
QWIN = 7        # q_j is an unknown for |j| <= QWIN (Step 2 of the proof)
assert T0 >= 2 * R + 3

# ------------------------------------------------------------------ Q(u), u = 1/lam, u^3 = u^2 - u - 1
O = (Fr(0), Fr(0), Fr(0))
I = (Fr(1), Fr(0), Fr(0))
U = (Fr(0), Fr(1), Fr(0))
LAM = (Fr(-1), Fr(1), Fr(-1))


def fadd(x, y): return (x[0] + y[0], x[1] + y[1], x[2] + y[2])
def fsub(x, y): return (x[0] - y[0], x[1] - y[1], x[2] - y[2])
def fsc(x, c): return (x[0] * c, x[1] * c, x[2] * c)
def fnz(x): return bool(x[0] or x[1] or x[2])       # 1, u, u^2 are independent over Q


def fmul(x, y):
    c = [Fr(0)] * 5
    for i in range(3):
        for j in range(3):
            c[i + j] += x[i] * y[j]
    # u^3 = u^2 - u - 1,  u^4 = -2u - 1
    return (c[0] - c[3] - c[4], c[1] - c[3] - 2 * c[4], c[2] + c[3])


assert fmul(U, LAM) == I
assert fadd(fadd(fmul(LAM, fmul(LAM, LAM)), fmul(LAM, LAM)), fsub(I, LAM)) == O      # lam^3 + lam^2 - lam + 1 = 0
_up = {0: I}


def upow(k):
    if k not in _up:
        _up[k] = fmul(upow(k - 1), U) if k > 0 else fmul(upow(k + 1), LAM)
    return _up[k]


def _f(x): return x ** 3 - x ** 2 + x + 1            # increasing on R (derivative 3x^2 - 2x + 1 > 0); root u


def _enclosure(bits):
    lo, hi = Fr(-1), Fr(0)
    assert _f(lo) < 0 < _f(hi)
    for _ in range(bits):
        mid = (lo + hi) / 2
        if _f(mid) < 0: lo = mid
        else: hi = mid
    return lo, hi


ENCL = [_enclosure(b) for b in (72, 400)]
UH = Fr(544, 1000)                                   # |u| < UH
assert _f(-UH) < 0
_uh = {}


def uh_pow(k):
    if k not in _uh: _uh[k] = UH ** k
    return _uh[k]


def interval(x, enc):
    lo, hi = enc                                     # lo < u < hi <= 0, so hi^2 <= u^2 <= lo^2
    a = x[0] + min(x[1] * lo, x[1] * hi) + min(x[2] * hi * hi, x[2] * lo * lo)
    b = x[0] + max(x[1] * lo, x[1] * hi) + max(x[2] * hi * hi, x[2] * lo * lo)
    return a, b


def abs_bounds(x):
    """(lower, upper) bound of |x|; the lower bound is positive if x != 0."""
    if not fnz(x): return Fr(0), Fr(0)
    for enc in ENCL:
        a, b = interval(x, enc)
        if a > 0: return a, b
        if b < 0: return -b, -a
    raise ArithmeticError("cannot separate a nonzero element from 0")


def fl(x):
    u = float(sum(ENCL[0]) / 2)
    return float(x[0]) + float(x[1]) * u + float(x[2]) * u * u


# ------------------------------------------------------------------ values r0 + r1 eps
EZ = (O, O)
def eadd(x, y): return (fadd(x[0], y[0]), fadd(x[1], y[1]))
def esc(x, c): return (fsc(x[0], c), fsc(x[1], c))


class Missing(Exception):
    pass


class Model:
    """Steps 1 and 2 of the proof for v = 'A' (A_0 removed) or 'B' (B_0 removed), for all odd t >= T0 at once.
    A linear form is a pair (dict unknown -> Fraction, known value r0 + r1 eps)."""

    def __init__(self, v, log):
        self.v = v
        A = v == "A"
        self.j0 = 3 if A else 2
        self.cut = (0, 1, 2) if A else (1,)
        self.g = (I, fsc(I, Fr(-1))) if A else EZ          # g = 1 - eps, resp. 0
        self.a = Fr(2) if A else Fr(1)
        self.unknowns = [("s", j) for j in self.cut]
        self.unknowns += [("q", j) for j in range(-QWIN, QWIN + 1) if A or j != -2]
        self.unknowns += [("p", -1), ("p", 0)] if A else [("w", -1)]
        self.sol = None
        eqs = []
        for i in range(-8, 11):
            if (i != -2) if A else (i not in (0, -1, -2)): eqs.append(self.eq5a(i))
            if (i != -1) if A else (i not in (0, -2)): eqs.append(self.eq5b(i))
        self.n_eq = len(eqs)
        self.sol, self.rank, self.free, consistent = self._solve(eqs)
        log(f"case {v}_0: {len(self.unknowns)} unknowns, {len(eqs)} equations, rank {self.rank}, free {self.free}, "
            f"consistent {consistent}")
        assert consistent, "cut system has no solution with the stated (g, a)"
        assert (len(self.unknowns), len(eqs)) == ((20, 36) if A else (16, 33)), "counts differ from the paper"
        # equations beyond the window hold identically (they involve no unknown)
        for i in list(range(-16, -8)) + list(range(11, 19)):
            for f in (self.eq5a(i), self.eq5b(i)):
                assert not f[0] and f[1] == EZ, ("equation outside the window fails", i)

    # --- sigma on the stretch: sigma_j = g (-1)^j + a lam^(j - t), j0 <= j <= t - 1; left positions are j - t
    def sigma(self, j):
        sg = Fr(1 if j % 2 == 0 else -1)
        if j >= self.j0:                 # g sg + a eps u^(-j)
            return (fsc(self.g[0], sg), fadd(fsc(self.g[1], sg), fsc(upow(-j), self.a)))
        if j <= -1:                      # position t + j: (-1)^(t+j) = -sg ; lam^j = u^(-j)
            return (fadd(fsc(self.g[0], -sg), fsc(upow(-j), self.a)), fsc(self.g[1], -sg))
        raise Missing(("sigma", j))

    @staticmethod
    def lin(*terms):
        d, k = {}, EZ
        for c, (fd, fk) in terms:
            c = Fr(c)
            for s, x in fd.items(): d[s] = d.get(s, Fr(0)) + c * x
            k = eadd(k, esc(fk, c))
        return ({s: x for s, x in d.items() if x}, k)

    def unk(self, s): return ({s: Fr(1)}, EZ)

    def S(self, j):
        if j in self.cut: return self.unk(("s", j))
        if self.v == "B" and j == 0: raise Missing("sigma_0")
        return ({}, self.sigma(j))

    def Q(self, j):
        if self.v == "B" and j == -2: raise Missing("q_-2")
        if abs(j) <= QWIN: return self.unk(("q", j))
        return self.lin((1, self.S(j + 2)), (2, self.S(j + 4)), (2, self.S(j + 5)))

    def P(self, i):
        if self.v == "A" and i in (-1, 0): return self.unk(("p", i))
        if self.v == "B" and i == -1: raise Missing("p_-1")
        return self.lin((-1, self.S(i + 1)))

    def M(self, i): return self.Q(i - 3)
    def Bb(self, i): return self.lin((1, self.Q(i - 1)), (-1, self.P(i - 1)))

    def W(self, i):
        if self.v == "B" and i == -1: return self.unk(("w", -1))
        return self.lin((1, self.S(i - 2)), (1, self.S(i + 1)), (-1, self.P(i)))

    def C(self, i):
        if self.v == "B" and i == -1: return self.lin((1, self.W(1)), (1, self.S(1)))
        return self.lin((1, self.Bb(i)), (1, self.Bb(i + 1)))

    def E(self, i): return self.lin((1, self.Q(i)), (-1, self.S(i + 2)))

    def eq5a(self, i): return self.lin((1, self.C(i)), (-1, self.W(i + 2)), (-1, self.S(i + 2)))
    def eq5b(self, i): return self.lin((1, self.C(i)), (-1, self.M(i + 1)), (-1, self.P(i + 1)))

    def form(self, typ, i):
        return {"s": self.S, "p": self.P, "q": self.Q, "m": self.M, "w": self.W, "b": self.Bb, "c": self.C,
                "e": self.E}[typ](i)

    def _solve(self, eqs):
        """Gauss-Jordan over Q; right-hand sides are 6 rationals (r0, r1 in Q(u)). Free unknowns are set to 0."""
        col = {s: n for n, s in enumerate(self.unknowns)}
        n = len(self.unknowns)
        rows = []
        for fd, fk in eqs:
            row = [Fr(0)] * n + [-x for x in fk[0]] + [-x for x in fk[1]]
            for s, x in fd.items(): row[col[s]] = x
            rows.append(row)
        piv, r = [], 0
        for c in range(n):
            k = next((i for i in range(r, len(rows)) if rows[i][c]), None)
            if k is None: continue
            rows[r], rows[k] = rows[k], rows[r]
            inv = 1 / rows[r][c]
            rows[r] = [x * inv for x in rows[r]]
            for i in range(len(rows)):
                if i != r and rows[i][c]:
                    f = rows[i][c]
                    rows[i] = [x - f * y for x, y in zip(rows[i], rows[r])]
            piv.append(c); r += 1
        consistent = all(not any(row[n:]) for row in rows[r:])
        sol = {s: EZ for s in self.unknowns}
        for i, c in enumerate(piv):
            sol[self.unknowns[c]] = (tuple(rows[i][n:n + 3]), tuple(rows[i][n + 3:n + 6]))
        return sol, r, [self.unknowns[c] for c in range(n) if c not in piv], consistent

    def value(self, f):
        out = f[1]
        for s, x in f[0].items(): out = eadd(out, esc(self.sol[s], x))
        return out

    # the two points of a pair of each type: (kind, offset)
    POINTS = {"s": (("A", 0), ("B", 0)), "p": (("A", 0), ("B", 1)), "q": (("A", 0), ("B", 2)),
              "m": (("A", 0), ("B", -1)), "w": (("A", 0), ("B", -2)), "b": (("B", 0), ("B", 1)),
              "c": (("B", 0), ("B", 2)), "e": (("A", 0), ("A", 2))}

    def exists(self, typ, i):
        return all(not (kind == self.v and i + o == 0) for kind, o in self.POINTS[typ])


D_TYPE = {"s": 7, "p": 9, "q": 19, "m": 11, "w": 13, "b": 10, "c": 20, "e": 12}      # distances, from the definition


def _generic_forms():
    """type -> {offset o: coefficient of sigma_{i+o}} away from the cut, from the formulas of Step 1."""
    def sh(f, s): return {o + s: c for o, c in f.items()}

    def comb(*terms):
        out = {}
        for c, f in terms:
            for o, x in f.items(): out[o] = out.get(o, 0) + c * x
        return {o: Fr(x) for o, x in sorted(out.items()) if x}
    s = {0: 1}
    p = {1: -1}
    q = {2: 1, 4: 2, 5: 2}
    b = comb((1, sh(q, -1)), (-1, sh(p, -1)))
    return {"s": comb((1, s)), "p": comb((1, p)), "q": comb((1, q)), "m": comb((1, sh(q, -3))),
            "w": comb((1, sh(s, -2)), (1, sh(s, 1)), (-1, p)), "b": b, "c": comb((1, b), (1, sh(b, 1))),
            "e": comb((1, q), (-1, sh(s, 2)))}


GEN = _generic_forms()


# ------------------------------------------------------------------ the catalogue of classes
def catalogue(Mo):
    """Returns (consts, fams): consts: key -> entry; fams: (family, parities) -> entry. An entry is a dict with
    name, fam (None for a window class), v = (r0, r1), atoms = [dict(coef, par, lo, hm)]: the value is
    r0 + r1 eps + sum coef u^k over the atoms, with k = par (mod 2), k >= lo, t - k >= hm."""
    pars = (0, 1) if fnz(Mo.g[0]) or fnz(Mo.g[1]) else (None,)

    def gpart(par):                      # -g (-1)^k
        if par is None: return EZ
        return esc(Mo.g, Fr(-1 if par == 0 else 1))
    consts, fams = {}, {}
    consts[("AA",)] = dict(name="AA", fam=None, v=EZ, atoms=[])
    for typ in GEN:
        d = D_TYPE[typ]
        for i in range(-R, R + 1):
            if not Mo.exists(typ, i): continue
            if Mo.v == "B" and typ == "e" and i == -2: continue           # x(A_-2 A_0): in no tight triple
            consts[("n", typ, i)] = dict(name=f"{typ}[{i}]", fam=None, v=esc(Mo.value(Mo.form(typ, i)), Fr(1, d)), atoms=[])
        km = sum(c * (1 if o % 2 == 0 else -1) for o, c in GEN[typ].items())
        kl = O
        for o, c in GEN[typ].items(): kl = fadd(kl, fsc(upow(-o), c))
        for par in pars:
            fams[(("n", typ), (par,))] = dict(name=f"{typ}[bulk {par}]", fam=("n", typ), v=esc(gpart(par), km / d),
                                              atoms=[dict(coef=fsc(kl, Mo.a / d), par=par, lo=R + 1, hm=R + 1)])
    sw = {}
    for j in range(-R, R + 1):
        if Mo.v == "B" and j == 0: continue
        sw[j] = Mo.value(Mo.S(j))
        consts[("y", j)] = dict(name=f"y[{j}]", fam=None, v=esc(sw[j], Fr(1, 15)), atoms=[])
    one = fsc(I, Mo.a)
    for par in pars:
        fams[(("y",), (par,))] = dict(name=f"y[bulk {par}]", fam=("y",), v=esc(gpart(par), Fr(1, 15)),
                                      atoms=[dict(coef=fsc(one, Fr(1, 15)), par=par, lo=R + 1, hm=R + 1)])
    for i, j in itertools.combinations(sorted(sw), 2):
        if j - i >= 3:
            consts[("ww", i, j)] = dict(name=f"BB[{i},{j}]", fam=None, v=esc(eadd(sw[i], sw[j]), Fr(1, 22)), atoms=[])
    for j in sorted(sw):
        for par in pars:                 # B_j with a B in the bulk at left distance k; far: k + j >= 3, resp. t - k - j >= 3
            fams[(("semi", j), (par,))] = dict(
                name=f"BB[{j}; bulk {par}]", fam=("semi", j), v=esc(eadd(sw[j], gpart(par)), Fr(1, 22)),
                atoms=[dict(coef=fsc(one, Fr(1, 22)), par=par, lo=max(R + 1, 3 - j), hm=max(R + 1, j + 3))])
    for p1, p2 in itertools.combinations_with_replacement(pars, 2):
        fams[(("bb",), (p1, p2))] = dict(
            name=f"BB[bulk {p1}; bulk {p2}]", fam=("bb",), v=esc(eadd(gpart(p1), gpart(p2)), Fr(1, 22)),
            atoms=[dict(coef=fsc(one, Fr(1, 22)), par=p, lo=R + 1, hm=R + 1) for p in (p1, p2)])
    # bulk formula = pair-by-pair formula where both apply (indices 11..16 on either side)
    for typ in GEN:
        for i in range(R + 1, R + 7):
            for par in pars:
                if par is not None and par != i % 2: continue
                e = fams[(("n", typ), (par,))]
                left = eadd(e["v"], (fmul(e["atoms"][0]["coef"], upow(i)), O))                 # k = i, index -i
                assert left == esc(Mo.value(Mo.form(typ, -i)), Fr(1, D_TYPE[typ])), ("bulk formula, left", typ, i)
            for par in pars:
                if par is not None and par == i % 2: continue                                  # k = t - i, t odd
                e = fams[(("n", typ), (par,))]
                right = eadd(e["v"], (O, fmul(e["atoms"][0]["coef"], upow(-i))))               # u^(t-i) = eps u^(-i)
                assert right == esc(Mo.value(Mo.form(typ, i)), Fr(1, D_TYPE[typ])), ("bulk formula, right", typ, i)
    return consts, fams


def entry_value(e, exps, t):
    out = fadd(e["v"][0], fmul(e["v"][1], upow(t)))
    for a, k in zip(e["atoms"], exps): out = fadd(out, fmul(a["coef"], upow(k)))
    return out


def valid(e, exps, t):
    for a, k in zip(e["atoms"], exps):
        if k < a["lo"] or t - k < a["hm"] or (a["par"] is not None and k % 2 != a["par"]): return False
    if e["fam"] == ("bb",):
        if abs(exps[0] - exps[1]) < 3: return False
        if e["atoms"][0]["par"] == e["atoms"][1]["par"] and exps[0] > exps[1]: return False   # canonical order
    return True


def instances(consts, fams, t):
    """All (entry name, exponents) valid at t. The exponents run over 1..t+R, wider than any range, so that the
    ranges lo, hm of the entries alone decide (a range that is too wide shows up as an extra instance)."""
    out = {(e["name"], ()) for e in consts.values()}
    for e in fams.values():
        rng = range(1, t + R + 1)
        for exps in itertools.product(rng, repeat=len(e["atoms"])):
            if valid(e, exps, t): out.add((e["name"], exps))
    return out


# ------------------------------------------------------------------ all solutions of sum c_i u^(k_i) = G
def _canon(ab, rels): return (frozenset(ab.items()), frozenset(frozenset(r.items()) for r in rels))


def solve(G, atoms):
    """atoms: list of (id, coef, lo, step); unknowns k_id >= lo, k_id = lo (mod step). Returns the list of all
    solutions as (abs, rels): abs = dict id -> exponent; rels = list of dicts id -> offset >= 0, each a group of
    terms that sums to 0 and may be shifted as a whole (for these only the offsets are constrained, and of the
    lower bounds only the congruences between terms of step 2 are kept: a superset of the true solutions)."""
    atoms = [a for a in atoms if fnz(a[1])]
    if not atoms: return [({}, [])] if not fnz(G) else []
    if not fnz(G): return [({}, rels) for rels in homog(atoms)]
    thr = abs_bounds(G)[0] / len(atoms)              # some term has absolute value >= |G| / n
    found = {}
    for n, (aid, c, lo, st) in enumerate(atoms):
        ch = abs_bounds(c)[1]
        rest = atoms[:n] + atoms[n + 1:]
        k = lo
        while ch * uh_pow(k) >= thr:
            for ab, rels in solve(fsub(G, fmul(c, upow(k))), rest):
                ab = dict(ab); ab[aid] = k
                found[_canon(ab, rels)] = (ab, rels)
            k += st
    return list(found.values())


def homog(atoms):
    """sum c_i u^(k_i) = 0: divide by the term with the least exponent."""
    found = {}
    for n, (aid, c, lo, st) in enumerate(atoms):
        rest = [(b, cb, (lb - lo) % 2 if (sb == 2 and st == 2) else 0, 2 if (sb == 2 and st == 2) else 1)
                for b, cb, lb, sb in atoms[:n] + atoms[n + 1:]]
        for ab, rels in solve(fsc(c, Fr(-1)), rest):
            grp = dict(ab); grp[aid] = 0
            rels = [grp] + rels
            found[frozenset(frozenset(r.items()) for r in rels)] = rels
    return list(found.values())


def check_solution(G, atoms, sol):
    """every reported solution is one (soundness of the output)."""
    ab, rels = sol
    coef = {a[0]: a[1] for a in atoms if fnz(a[1])}
    assert set(coef) == set(ab) | {i for r in rels for i in r}
    tot = O
    for i, k in ab.items(): tot = fadd(tot, fmul(coef[i], upow(k)))
    assert tot == G
    for r in rels:
        tot = O
        for i, k in r.items(): tot = fadd(tot, fmul(coef[i], upow(k)))
        assert tot == O


# ------------------------------------------------------------------ comparison of all pairs of classes
def judge(X, Y, sol):
    """None if the solution may be a coincidence of two different classes; otherwise the reason why it is not."""
    ab, rels = sol
    loc = {i: (0, k) for i, k in ab.items()}
    for n, r in enumerate(rels):
        for i, k in r.items(): loc[i] = (n + 1, k)
    xs = [loc[("x", n)] for n in range(len(X["atoms"]))]
    ys = [loc[("y", n)] for n in range(len(Y["atoms"]))]
    if X["fam"] is not None and X["fam"] == Y["fam"] and sorted(xs) == sorted(ys): return "same class"
    te = loc.get("eps")
    for C, asg in ((X, xs), (Y, ys)):
        for a, (g, k) in zip(C["atoms"], asg):
            if te is not None and te[0] == g and te[1] - k < a["hm"]: return "exponent beyond its range (t - k too small)"
        if C["fam"] == ("bb",) and asg[0][0] == asg[1][0] and abs(asg[0][1] - asg[1][1]) < 3: return "B-pair not far"
    return None


def equation(X, Y, step):
    atoms = []
    for tag, C, sg in (("x", X, 1), ("y", Y, -1)):
        for n, a in enumerate(C["atoms"]):
            lo = a["lo"] + (0 if a["par"] is None or a["lo"] % 2 == a["par"] else 1)
            atoms.append(((tag, n), fsc(a["coef"], Fr(sg)), lo, step))
    atoms.append(("eps", fsub(X["v"][1], Y["v"][1]), T0, 2))
    return fsub(Y["v"][0], X["v"][0]), atoms


def compare(consts, fams, log, quiet=False):
    entries = list(consts.values()) + list(fams.values())
    step = 1 if all(a["par"] is None for e in fams.values() for a in e["atoms"]) else 2
    neq = nsol = 0
    reasons, bad = {}, []
    for n, X in enumerate(entries):
        for Y in entries[n:]:
            if X is Y and not X["atoms"]: continue
            G, atoms = equation(X, Y, step)
            neq += 1
            for sol in solve(G, atoms):
                check_solution(G, atoms, sol)
                nsol += 1
                why = judge(X, Y, sol)
                if why is None: bad.append((X["name"], Y["name"], str(sol)))
                else: reasons[why] = reasons.get(why, 0) + 1
    if not quiet:
        log(f"   {len(consts)} window classes, {len(fams)} bulk families, {neq} equations, {nsol} solutions: "
            + ", ".join(f"{c} x {w}" for w, c in sorted(reasons.items())) + f"; possible coincidences: {len(bad)}")
        for b in bad[:30]: log(f"      COINCIDENCE {b}")
    return dict(window_classes=len(consts), bulk_families=len(fams), equations=neq, solutions=nsol, discarded=reasons,
                coincidences=bad)


# ------------------------------------------------------------------ ground truth on a real cycle
def my_metric(t):
    n = 2 * t
    d = [[0] * n for _ in range(n)]
    for i in range(t):
        for j in range(t):
            k = min((i - j) % t, (j - i) % t)
            if k:
                d[i][j] = {1: 16, 2: 12}.get(k, 8)
                d[t + i][t + j] = {1: 10, 2: 20}.get(k, 22)
            o = (j - i) % t
            if o > t // 2: o -= t
            d[i][t + j] = d[t + j][i] = {-2: 13, -1: 11, 0: 7, 1: 9, 2: 19}.get(o, 15)
    return d


def guard(Mo, consts, fams, t, log):
    assert t % 2 == 1 and t >= T0
    v = Mo.v
    d = my_metric(t)
    try:
        sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
        from family_C import metric
        assert metric(t).tolist() == d, "metric differs from family_C.metric"
    except ImportError:
        pass
    eps = upow(t)
    ev = lambda x: fadd(x[0], fmul(x[1], eps))
    rep = lambda i: (i % t) - t if (i % t) > t // 2 else (i % t)
    g = ev(Mo.g)
    # arrays indexed by residues mod t; None = no such pair / not defined
    sig = [None] * t
    for j in range(t):
        if j < Mo.j0: sig[j] = ev(Mo.sol[("s", j)]) if j in Mo.cut else None
        else: sig[j] = fadd(fsc(g, Fr(1 if j % 2 == 0 else -1)), fsc(upow(t - j), Mo.a))

    def plus(*terms):
        out = O
        for c, x in terms:
            if x is None: return None
            out = fadd(out, fsc(x, Fr(c)))
        return out
    q = [None] * t
    for j in range(t):
        r = rep(j)
        if abs(r) <= QWIN: q[j] = ev(Mo.sol[("q", r)]) if ("q", r) in Mo.sol else None
        else:
            assert 8 <= j <= t - 8
            q[j] = plus((1, sig[j + 2]), (2, sig[j + 4]), (2, sig[j + 5]))
    p = [None] * t
    for i in range(t):
        if v == "A" and rep(i) in (-1, 0): p[i] = ev(Mo.sol[("p", rep(i))])
        elif v == "B" and rep(i) == -1: p[i] = None
        else: p[i] = plus((-1, sig[(i + 1) % t]))
    m = [q[(i - 3) % t] for i in range(t)]
    b = [plus((1, q[(i - 1) % t]), (-1, p[(i - 1) % t])) for i in range(t)]
    w = [plus((1, sig[(i - 2) % t]), (1, sig[(i + 1) % t]), (-1, p[i])) for i in range(t)]
    if v == "B": w[t - 1] = ev(Mo.sol[("w", -1)])
    c = [plus((1, b[i]), (1, b[(i + 1) % t])) for i in range(t)]
    if v == "B": c[t - 1] = plus((1, w[1]), (1, sig[1]))
    e = [plus((1, q[i]), (-1, sig[(i + 2) % t])) for i in range(t)]
    near = {"s": sig, "p": p, "q": q, "m": m, "w": w, "b": b, "c": c, "e": e}

    def xval(x, y):
        """value and class key of the pair {x, y}; points: A_i = i, B_i = t + i."""
        if x > y: x, y = y, x
        if y < t:
            k = min((y - x) % t, (x - y) % t)
            if k != 2: return O, ("AA",)
            i = x if (y - x) % t == 2 else y
            return e[i], ("e", i)
        if x >= t:
            i, j = x - t, y - t
            k = min((j - i) % t, (i - j) % t)
            if k >= 3: return plus((1, sig[i]), (1, sig[j])), ("BB", i, j)
            i0 = i if (j - i) % t == k else j
            return (b[i0], ("b", i0)) if k == 1 else (c[i0], ("c", i0))
        i, j = x, y - t
        o = rep(j - i)
        if abs(o) >= 3: return sig[j], ("y", j)
        typ = {0: "s", 1: "p", 2: "q", -1: "m", -2: "w"}[o]
        return near[typ][i], (typ, i)

    gone = 0 if v == "A" else t
    pts = [x for x in range(2 * t) if x != gone]
    X, key = {}, {}
    for x, y in itertools.combinations(pts, 2): X[(x, y)], key[(x, y)] = xval(x, y)
    undefined = {pr for pr, val in X.items() if val is None}
    assert {key[pr] for pr in undefined} == ({("e", t - 2)} if v == "B" else set()), "an existing pair has no value"
    get = lambda x, y: X[(x, y) if x < y else (y, x)]
    ntri = 0
    for x, y in itertools.combinations(pts, 2):
        dxy, dx, dy = d[x][y], d[x], d[y]
        for z in pts:
            if z != x and z != y and dxy == dx[z] + dy[z]:
                ntri += 1
                vals = (get(x, y), get(x, z), get(z, y))
                assert None not in vals, ("tight triple through the free pair", x, y, z)
                assert vals[0] == fadd(vals[1], vals[2]), ("tight triple violated", t, x, y, z)
    # class values
    val = {}
    for pr, k in key.items():
        if pr in undefined: continue
        D = fsc(X[pr], Fr(1, d[pr[0]][pr[1]]))
        assert val.setdefault(k, D) == D, ("not constant on a class of pi", k)
    seen = {}
    for k, D in val.items():
        assert D not in seen, ("two classes with the same value", t, k, seen[D])
        seen[D] = k
    # the catalogue: every class is exactly one valid instance, with the same value, and conversely
    pars = (0, 1) if any(a["par"] is not None for f in fams.values() for a in f["atoms"]) else (None,)
    par = lambda k: None if pars == (None,) else k % 2
    used = set()
    for k, D in val.items():
        if k == ("AA",): ent, exps = consts[("AA",)], ()
        elif k[0] == "BB":
            ri, rj = rep(k[1]), rep(k[2])
            win = sorted(r for r in (ri, rj) if abs(r) <= R)
            blk = [(-r) % t for r in (ri, rj) if abs(r) > R]
            if len(win) == 2: ent, exps = consts[("ww", win[0], win[1])], ()
            elif len(win) == 1: ent, exps = fams[(("semi", win[0]), (par(blk[0]),))], (blk[0],)
            else:
                blk.sort(key=lambda kk: (str(par(kk)), kk))
                blk.sort(key=lambda kk: (0 if par(kk) in (0, None) else 1))
                ent, exps = fams[(("bb",), (par(blk[0]), par(blk[1])))], tuple(blk)
        else:
            typ, r = k[0], rep(k[1])
            if abs(r) <= R: ent, exps = consts[("y", r) if typ == "y" else ("n", typ, r)], ()
            else:
                kk = (-r) % t
                ent, exps = fams[((("y",) if typ == "y" else ("n", typ)), (par(kk),))], (kk,)
        assert valid(ent, exps, t), ("class outside the ranges of the catalogue", k, ent["name"], exps)
        assert entry_value(ent, exps, t) == D, ("catalogue value differs from the value on the cycle", t, k, ent["name"], exps)
        assert (ent["name"], exps) not in used
        used.add((ent["name"], exps))
    inst = instances(consts, fams, t)
    assert used == inst, ("catalogue instances and classes differ", t, sorted(inst - used)[:5], sorted(used - inst)[:5])
    log(f"   guard t = {t}: {ntri} tight triples hold; {len(val)} classes = catalogue instances, values equal and pairwise different")
    return dict(t=t, tight_triples=ntri, classes=len(val))


# ------------------------------------------------------------------ self-test
def selftest(log):
    rnd = random.Random(11)
    base = [I, U, LAM, fadd(I, U), fsub(U, I)]

    def rc():
        return fsc(rnd.choice(base), Fr(rnd.choice([1, -1, 2, -2, 3, -3]), rnd.choice([1, 1, 2])))
    ok = True
    # (1) completeness against brute force in a box, with many planted and homogeneous instances
    width, missed, trials, nb = 7, 0, 150, 0
    for _ in range(trials):
        atoms = []
        for n in range(rnd.randint(1, 3)):
            atoms.append((("x", n), rc(), rnd.randint(1, 3), rnd.choice([1, 2])))
        atoms.append(("eps", rc() if rnd.random() < 0.8 else O, 5, 2))
        plant = {a[0]: a[2] + a[3] * rnd.randint(0, width - 1) for a in atoms}
        mode = rnd.random()
        if mode < 0.35 and len(atoms) >= 2:          # make the last x-atom cancel everything: G = 0
            tot = O
            for a in atoms:
                if a[0] != ("x", 0): tot = fadd(tot, fmul(a[1], upow(plant[a[0]])))
            a0 = atoms[0]
            atoms[0] = (a0[0], fsc(fmul(tot, upow(-plant[a0[0]])), Fr(-1)), a0[2], a0[3])
        G = O
        for a in atoms: G = fadd(G, fmul(a[1], upow(plant[a[0]])))
        if mode > 0.9: G = fadd(G, rc())             # usually no solution
        sols = solve(G, atoms)
        for s in sols: check_solution(G, atoms, s)
        live = [a for a in atoms if fnz(a[1])]
        for ks in itertools.product(*[[a[2] + a[3] * n for n in range(width)] for a in live]):
            tot = O
            for a, k in zip(live, ks): tot = fadd(tot, fmul(a[1], upow(k)))
            if tot != G: continue
            nb += 1
            asg = {a[0]: k for a, k in zip(live, ks)}
            cov = any(all(asg[i] == k for i, k in ab.items()) and
                      all(len({asg[i] - k for i, k in r.items()}) == 1 for r in rels) for ab, rels in sols)
            missed += not cov
    log(f"selftest 1: {trials} random equations, {nb} solutions found by brute force in a box, missed by the search: {missed}")
    ok = ok and missed == 0 and nb >= trials * 0.8
    # (2) duplicated and planted classes are reported
    for v in ("A", "B"):
        Mo = Model(v, lambda s: None)
        consts, fams = catalogue(Mo)
        extra_c, extra_f, want = {}, {}, []
        c0 = consts[("n", "q", -4)]
        extra_c["dup1"] = dict(c0, name="DUP-window"); want.append(("DUP-window", c0["name"]))
        for fam in (("n", "c"), ("y",), ("semi", 5), ("bb",)):
            key = next(k for k in fams if k[0] == fam)
            extra_f[("dup",) + key] = dict(fams[key], name="DUP-" + fams[key]["name"], fam=("dup", fam))
            want.append(("DUP-" + fams[key]["name"], fams[key]["name"]))
        # a window class moved so that it equals another one at t = 29 only
        ca, cb = consts[("n", "m", 3)], consts[("n", "w", -6)]
        dv = fsub(ca["v"][1], cb["v"][1])
        extra_c["pl1"] = dict(name="PLANT-t29", fam=None, atoms=[], v=(fadd(cb["v"][0], fmul(dv, upow(29))), fsub(cb["v"][1], dv)))
        want.append(("PLANT-t29", cb["name"]))
        # a window class equal to a bulk class at k = 14 or 15, t = 37
        key = next(k for k in fams if k[0] == ("n", "b"))
        fb = fams[key]
        kk = 14 if fb["atoms"][0]["par"] in (0, None) else 15
        extra_c["pl2"] = dict(name="PLANT-bulk", fam=None, atoms=[],
                              v=(fadd(fb["v"][0], fmul(fb["atoms"][0]["coef"], upow(kk))), fb["v"][1]))
        want.append(("PLANT-bulk", fb["name"]))
        c2 = dict(consts); c2.update(extra_c)
        f2 = dict(fams); f2.update(extra_f)
        r = compare(c2, f2, log, quiet=True)
        got = {frozenset((x, y)) for x, y, _ in r["coincidences"]}
        miss = [w for w in want if frozenset(w) not in got]
        log(f"selftest 2, {v}_0: {len(want)} duplicated or planted classes, not reported: {miss}; "
            f"reported in all: {len(r['coincidences'])}")
        ok = ok and not miss
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guard", type=int, nargs="*", default=[23, 25, 27, 29, 31, 37, 45])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    lines = []

    def log(s):
        print(s, flush=True); lines.append(s)
    if a.selftest:
        log("SELFTEST " + ("passed" if selftest(log) else "FAILED") + f" ({time.time() - t0:.0f} s)")
        return
    res = {}
    for v in ("A", "B"):
        Mo = Model(v, log)
        consts, fams = catalogue(Mo)
        res[v] = dict(rank=Mo.rank, free=[str(f) for f in Mo.free], guard=[guard(Mo, consts, fams, t, log) for t in a.guard])
        res[v].update(compare(consts, fams, log))
        log(f"   ({time.time() - t0:.0f} s)")
    ok = all(not res[v]["coincidences"] for v in res)
    log("RESULT: " + (f"no two classes of pi inside V - v have equal values, for v = A_0 and B_0 and every odd t >= {T0}"
                      if ok else "possible coincidences, see above"))
    res.update(ok=ok, T0=T0, R=R, log=lines)
    out = ROOT / "results/phase9/family_C_top_check.json"
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(res, indent=1))
    os.replace(tmp, out)


if __name__ == "__main__":
    main()
