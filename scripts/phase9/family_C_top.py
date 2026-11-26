#!/usr/bin/env python3
"""L(C_t) = 2t for every odd t >= 23: finite exact checks for the proof (docs/paper_draft.md, Theorem 4(c')).

Claim. Let pi be the partition of Theorem 4 and W = V - v with v = A_0 or v = B_0. Then W forces no two classes
of pi to be equal. (By rotation this covers every W with |W| = 2t - 1, so pi is closed at level 2t - 1.)

Method. For each v an explicit solution X of T_W(pi) is built for all odd t >= 23 at once, and its values
D(C) = (X(C) - d(C))/d(C) on the classes are shown to be pairwise different.

  * Parametrisation (proved by hand in the paper, re-checked here on real cycles): every variable is a linear form in
    sigma_j (= x(A_jB_j), one virtual), q_j (= x(A_jB_{j+2})) and a few free symbols at the cut; the tight triples
    reduce to the equations 5a_i: c_i = w_{i+2} + sigma_{i+2} and 5b_i: c_i = m_{i+1} + p_{i+1}, except those lost
    with v.
  * Away from the cut, sigma follows the recurrence, so sigma_j = g (-1)^j + a lam^(j-t) on the stretch
    (lam = real root of z^3 + z^2 - z + 1); the unknowns at the cut are solved exactly. Solvability imposes one
    condition for v = A_0 (it fixes g/a) and none for v = B_0 (g = 0).
  * Every value is then v0 + v1 eps + sum of terms coef * lam^(-k), with v0, v1, coef in Q(lam), eps = lam^(-t), and
    k the distance of a position to the left of the cut. Equality of two classes is an equation
    G0 = sum_i c_i lam^(-k_i) in integer unknowns; a branch-and-bound search with rigorous bounds lists all its
    solutions, and each is shown to be the same class or outside the admissible ranges.
  * Guard: for t in --guard the solution is instantiated in Q(lam) on the real cycle C_t - v, every tight triple is
    checked, and the class values are checked to be pairwise different.

  python scripts/phase9/family_C_top.py [--guard 19 21 23 25 27 31] [--selftest]
Output results/phase9/family_C_top.json.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
from family_C import metric  # noqa: E402

T0 = 23            # the proof covers odd t >= T0
QW = 7             # q_j is an unknown of the cut system for |j| <= QW
RW = 10            # variables at relative positions outside [-RW, RW] are standard

# ---------------------------------------------------------------- the field Q(lam), lam^3 = -lam^2 + lam - 1
Z3 = (Fr(0), Fr(0), Fr(0))
ONE = (Fr(1), Fr(0), Fr(0))


def kadd(x, y): return (x[0] + y[0], x[1] + y[1], x[2] + y[2])
def ksub(x, y): return (x[0] - y[0], x[1] - y[1], x[2] - y[2])
def ksc(x, c): return (x[0] * c, x[1] * c, x[2] * c)
def kzero(x): return x[0] == 0 and x[1] == 0 and x[2] == 0


def kmul(x, y):
    c = [Fr(0)] * 5
    for i in range(3):
        if x[i]:
            for j in range(3):
                c[i + j] += x[i] * y[j]
    # lam^3 = -lam^2 + lam - 1 ; lam^4 = 2 lam^2 - 2 lam + 1
    return (c[0] - c[3] + c[4], c[1] + c[3] - 2 * c[4], c[2] - c[3] + 2 * c[4])


LAM = (Fr(0), Fr(1), Fr(0))
LAMINV = (Fr(1), Fr(-1), Fr(-1))            # 1/lam = 1 - lam - lam^2
assert kmul(LAM, LAMINV) == ONE
_pow = {0: ONE}


def kpow(e):
    if e not in _pow:
        _pow[e] = kmul(kpow(e - 1), LAM) if e > 0 else kmul(kpow(e + 1), LAMINV)
    return _pow[e]


def _enclose(bits=90):
    lo, hi = Fr(-2), Fr(-1)                  # f(-2) = -1 < 0 < f(-1) = 2, f increasing on [-2, -1]
    f = lambda z: z ** 3 + z ** 2 - z + 1
    assert f(lo) < 0 < f(hi)
    for _ in range(bits):
        mid = (lo + hi) / 2
        if f(mid) < 0: lo = mid
        else: hi = mid
    return lo, hi


LLO, LHI = _enclose()                        # LLO < lam < LHI < 0
L2LO, L2HI = LHI * LHI, LLO * LLO            # bounds of lam^2
LINV_HI = 1 / (-LHI)                         # upper bound of 1/|lam|
_linv = {}


def linv_hi(m):
    if m not in _linv: _linv[m] = LINV_HI ** m
    return _linv[m]


def kbounds(x):
    lo = x[0] + min(x[1] * LLO, x[1] * LHI) + min(x[2] * L2LO, x[2] * L2HI)
    hi = x[0] + max(x[1] * LLO, x[1] * LHI) + max(x[2] * L2LO, x[2] * L2HI)
    return lo, hi


def abs_lo(x):
    if kzero(x): return Fr(0)
    lo, hi = kbounds(x)
    if lo > 0: return lo
    if hi < 0: return -hi
    raise ArithmeticError("enclosure of lam too coarse for a nonzero element")


def abs_hi(x):
    lo, hi = kbounds(x)
    return max(abs(lo), abs(hi))


def kfloat(x):
    l = float((LLO + LHI) / 2)
    return float(x[0]) + float(x[1]) * l + float(x[2]) * l * l


# ---------------------------------------------------------------- linear forms and the two cases
class Case:
    """v = 'A' (A_0 removed) or 'B' (B_0 removed). Linear forms are dicts symbol -> Fraction; symbols are
    ('s', j), ('q', j) with j an integer (relative position, or residue mod t on a real cycle) and ('x', name)."""

    def __init__(self, v, t=None):
        self.v, self.t = v, t
        self.j0 = 3 if v == "A" else 2                      # the stretch is j0 <= j <= t - 1
        self.cut_sigma = [0, 1, 2] if v == "A" else [1]

    def r(self, i):                                         # representative of a position
        if self.t is None: return i
        i %= self.t
        return i - self.t if i > self.t // 2 else i

    @staticmethod
    def add(*terms):
        out = {}
        for c, f in terms:
            for k, x in f.items():
                out[k] = out.get(k, 0) + c * x
        return {k: x for k, x in out.items() if x}

    def sig(self, j):
        j = self.r(j)
        if self.v == "B" and j == 0: raise KeyError("sigma_0 does not exist")
        return {("s", j): Fr(1)}

    def q(self, j):
        j = self.r(j)
        if self.v == "B" and j == -2: raise KeyError("q_-2 does not exist")
        return {("q", j): Fr(1)}

    def p(self, i):
        i = self.r(i)
        if self.v == "A" and i in (-1, 0): return {("x", "p%d" % i): Fr(1)}
        if self.v == "B" and i == -1: raise KeyError("p_-1 does not exist")
        return self.add((-1, self.sig(i + 1)))

    def m(self, j): return self.q(j - 3)
    def b(self, j): return self.add((1, self.q(j - 1)), (-1, self.p(j - 1)))

    def w(self, j):
        if self.v == "B" and self.r(j) == -1: return {("x", "w-1"): Fr(1)}
        return self.add((1, self.sig(j - 2)), (1, self.sig(j + 1)), (-1, self.p(j)))

    def c(self, i):
        if self.v == "B" and self.r(i) == -1: return self.add((1, self.w(1)), (1, self.sig(1)))
        return self.add((1, self.b(i)), (1, self.b(i + 1)))

    def e(self, i):
        if self.v == "B" and self.r(i) == -2: return {("x", "e-2"): Fr(1)}
        return self.add((1, self.q(i)), (-1, self.sig(i + 2)))

    def near(self, typ, i):
        return {"s": self.sig, "p": self.p, "q": self.q, "m": self.m, "w": self.w, "b": self.b, "c": self.c,
                "e": self.e}[typ](i)

    # the points of the pair of a near variable, as (kind, position)
    PAIR = {"s": ("A", 0, "B", 0), "p": ("A", 0, "B", 1), "q": ("A", 0, "B", 2), "m": ("A", 0, "B", -1),
            "w": ("A", 0, "B", -2), "b": ("B", 0, "B", 1), "c": ("B", 0, "B", 2), "e": ("A", 0, "A", 2)}

    def exists(self, typ, i):
        k1, o1, k2, o2 = self.PAIR[typ]
        return not ((k1 == self.v and self.r(i + o1) == 0) or (k2 == self.v and self.r(i + o2) == 0))

    def has_5a(self, i):
        i = self.r(i)
        return i != -2 if self.v == "A" else i not in (0, -2, -1)

    def has_5b(self, i):
        i = self.r(i)
        return i != -1 if self.v == "A" else i not in (0, -2)

    def eq5a(self, i): return self.add((1, self.c(i)), (-1, self.w(i + 2)), (-1, self.sig(i + 2)))
    def eq5b(self, i): return self.add((1, self.c(i)), (-1, self.m(i + 1)), (-1, self.p(i + 1)))

    def q_formula(self, j): return self.add((1, self.sig(j + 2)), (2, self.sig(j + 4)), (2, self.sig(j + 5)))


D_NEAR = {"s": 7, "p": 9, "q": 19, "m": 11, "w": 13, "b": 10, "c": 20, "e": 12}
# standard forms on the stretch (alpha = 0): value of the variable at position i = sum of f[o] * sigma_{i+o}
STD = {"s": {0: 1}, "p": {1: -1}, "q": {2: 1, 4: 2, 5: 2}, "m": {-1: 1, 1: 2, 2: 2}, "w": {-2: 1, 1: 2},
       "b": {0: 1, 1: 1, 3: 2, 4: 2}, "c": {0: 1, 1: 2, 2: 1, 3: 2, 4: 4, 5: 2}, "e": {4: 2, 5: 2}}


# ---------------------------------------------------------------- exact elimination with vector right-hand sides
def eliminate(rows, unknowns, width):
    """rows: list of (dict unknown -> Fraction, rhs vector). Returns (solution dict with free unknowns = 0,
    list of free unknowns, list of residual rhs vectors of the rows that reduce to 0 = rhs)."""
    col = {u: i for i, u in enumerate(unknowns)}
    M = [[Fr(0)] * len(unknowns) + list(rhs) for f, rhs in rows]
    for r, (f, rhs) in enumerate(rows):
        for u, x in f.items(): M[r][col[u]] += x
    n = len(unknowns); piv = []; r = 0
    for c in range(n):
        k = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if k is None: continue
        M[r], M[k] = M[k], M[r]
        inv = 1 / M[r][c]; M[r] = [x * inv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f_ = M[i][c]; M[i] = [x - f_ * y for x, y in zip(M[i], M[r])]
        piv.append(c); r += 1
    sol = {u: [Fr(0)] * width for u in unknowns}
    for i, c in enumerate(piv): sol[unknowns[c]] = M[i][n:]
    free = [unknowns[c] for c in range(n) if c not in piv]
    resid = [M[i][n:] for i in range(r, len(M))]
    return sol, free, resid


def vadd(x, y): return [a + b for a, b in zip(x, y)]
def vsc(x, c): return [a * c for a in x]


class Solution:
    """The explicit solution near the cut for one case, valid for every odd t >= T0."""

    def __init__(self, v, log):
        self.v = v
        cs = self.cs = Case(v)
        self.j0 = cs.j0
        unknown = [("s", j) for j in cs.cut_sigma] + [("q", j) for j in range(-QW, QW + 1) if not (v == "B" and j == -2)]
        unknown += [("x", "p-1"), ("x", "p0")] if v == "A" else [("x", "w-1")]
        uset = set(unknown)
        eqs = []
        for i in range(-QW - 1, QW + 4):
            if cs.has_5a(i) and not (v == "B" and i == -1): eqs.append(cs.eq5a(i))
            if cs.has_5b(i): eqs.append(cs.eq5b(i))

        def split(form, sval):
            """unknown part, and the value of the known part (q outside the window by formula, sigma on the stretch)."""
            unk, val = {}, None
            for sym, x in form.items():
                if sym in uset:
                    unk[sym] = unk.get(sym, 0) + x; continue
                if sym[0] == "q":
                    assert abs(sym[1]) > QW
                    for s2, y in cs.q_formula(sym[1]).items():
                        vv = vsc(sval(s2[1]), x * y); val = vv if val is None else vadd(val, vv)
                    continue
                assert sym[0] == "s", sym
                vv = vsc(sval(sym[1]), x); val = vv if val is None else vadd(val, vv)
            return unk, val

        # pass 1: channels [lam-left (3), lam-right (3), (-1)-mode (1)]
        def sval7(j):
            assert j <= -1 or j >= self.j0, j
            if j < 0: return list(kpow(j)) + [Fr(0)] * 3 + [Fr(-((-1) ** (-j)))]     # (-1)^(t+j) = -(-1)^j, t odd
            return [Fr(0)] * 3 + list(kpow(j)) + [Fr((-1) ** j)]
        rows = []
        for f in eqs:
            unk, val = split(f, sval7)
            rows.append((unk, vsc(val, -1) if val is not None else [Fr(0)] * 7))
        sol, free, resid = eliminate(rows, unknown, 7)
        conds = [r_ for r_ in resid if any(r_)]
        log(f"case {v}_0 removed: {len(unknown)} cut unknowns, {len(eqs)} equations, free unknowns {free}, "
            f"{len(conds)} nonzero solvability conditions")
        if conds:
            c0 = conds[0]
            for c1 in conds[1:]:                       # all conditions must be rational multiples of the first
                k = next(i for i in range(7) if c0[i])
                assert all(c1[i] * c0[k] == c0[i] * c1[k] for i in range(7)), "independent conditions"
            # condition: CL + CR*eps (lam-mode, amplitude 1 on lam^(j-t)) and cm ((-1)-mode); take g = CL + CR eps, a = -cm
            self.CL, self.CR, cm = tuple(c0[0:3]), tuple(c0[3:6]), c0[6]
            assert cm != 0
            self.a = -cm
        else:
            self.CL, self.CR, self.a = Z3, Z3, Fr(1)
        self.mixed = bool(conds)
        log(f"   amplitudes: g = {kfloat(self.CL):.6g} + {kfloat(self.CR):.6g} eps on (-1)^j,  a = {self.a} on lam^(j-t)"
            + (f"   (ratio a/g -> {float(self.a) / kfloat(self.CL):.6f})" if self.mixed else ""))
        # pass 2: values as v0 + v1 eps, 6 rationals
        rows = []
        for f in eqs:
            unk, val = split(f, self.sval)
            rows.append((unk, vsc(val, -1) if val is not None else [Fr(0)] * 6))
        sol, free, resid = eliminate(rows, unknown, 6)
        assert not any(any(r_) for r_ in resid), "cut system inconsistent"
        self.free = free
        self.val = sol                                      # symbol -> 6-vector
        for j in (-QW, -QW + 1, QW - 1, QW):                # the window is wide enough
            assert sol[("q", j)] == self.form_val(cs.q_formula(j)), "q window too narrow"
        # the recurrence holds for both modes (so the equations outside the window hold)
        assert kzero(kadd(kadd(ONE, ksc(kpow(3), 2)), kpow(4))) and 1 + 2 * (-1) ** 3 + (-1) ** 4 == 0

    def sval(self, j):
        """sigma at relative position j of the stretch, as v0 + v1 eps."""
        assert j <= -1 or j >= self.j0, j
        if j < 0:
            sg = Fr(-((-1) ** (-j)))
            return list(kadd(ksc(self.CL, sg), ksc(kpow(j), self.a))) + list(ksc(self.CR, sg))
        sg = Fr((-1) ** j)
        return list(ksc(self.CL, sg)) + list(kadd(ksc(self.CR, sg), ksc(kpow(j), self.a)))

    def sym_val(self, sym):
        if sym in self.val: return self.val[sym]
        if sym[0] == "s": return self.sval(sym[1])
        if sym[0] == "q": return self.form_val(self.cs.q_formula(sym[1]))
        raise KeyError(sym)

    def form_val(self, form):
        out = [Fr(0)] * 6
        for sym, x in form.items(): out = vadd(out, vsc(self.sym_val(sym), x))
        return out

    def std_val(self, typ, i):
        """standard value at relative position i, or None if it needs a sigma off the stretch or straddles the cut."""
        pos = [i + o for o in STD[typ]]
        if not (all(p <= -1 for p in pos) or all(p >= self.j0 for p in pos)): return None
        out = [Fr(0)] * 6
        for o, x in STD[typ].items(): out = vadd(out, vsc(self.sval(i + o), Fr(x)))
        return out


# ---------------------------------------------------------------- all solutions of G0 = sum c_i lam^(-k_i)
_gid = [0]


def solve(G0, atoms, grp=0):
    """atoms: list of [id, coef, min exponent, step]. Returns the list of all solutions as dicts id -> (group,
    exponent); exponents in a group other than 0 are relative to a free common shift. Sound: the lower bounds are
    the only constraints used."""
    atoms = [list(a) for a in atoms if not kzero(a[1])]
    if not atoms: return [{}] if kzero(G0) else []
    if kzero(G0): return homogeneous(atoms)
    hi = {a[0]: abs_hi(a[1]) for a in atoms}
    g_lo = abs_lo(G0)
    sols = []
    while True:
        contrib = [hi[a[0]] * linv_hi(a[2]) for a in atoms]
        if g_lo > sum(contrib): return sols
        i = max(range(len(atoms)), key=lambda k: contrib[k])
        a = atoms[i]
        for s in solve(ksub(G0, kmul(a[1], kpow(-a[2]))), atoms[:i] + atoms[i + 1:], grp):
            s = dict(s); s[a[0]] = (grp, a[2]); sols.append(s)
        a[2] += a[3]


def homogeneous(atoms):
    """sum c_i lam^(-k_i) = 0: one atom has the least exponent k; the others are k + d_i, d_i >= 0. (The atom of
    eps may be the least: a pair just left of the break whose sigmas lie right of it has exponent t or t + 1.)"""
    sols = []
    for i0, a0 in enumerate(atoms):
        _gid[0] += 1; g = _gid[0]
        others = []
        for a in atoms[:i0] + atoms[i0 + 1:]:
            if a[3] == 2 and a0[3] == 2: others.append([a[0], a[1], (a[2] - a0[2]) % 2, 2])
            else: others.append([a[0], a[1], 0, 1])
        for s in solve(ksc(a0[1], -1), others, g):
            s = dict(s); s[a0[0]] = (g, 0); sols.append(s)
    return sols


# ---------------------------------------------------------------- classes and their values
def build_classes(S):
    """Returns the list of class instances: dict(name, kind, key, const=(v0, v1), atoms=[(coef, parity)])."""
    v, cs = S.v, S.cs
    pars = [1, 0] if S.mixed else [None]
    sgn = lambda par: Fr(0) if par is None else Fr(1 if par == 1 else -1)          # -(-1)^k
    out = [dict(name="AA", kind="AA", key=("AA",), const=(Z3, Z3), atoms=[])]
    ex = {}
    six = lambda vec, d: (ksc(tuple(vec[:3]), Fr(1, d)), ksc(tuple(vec[3:]), Fr(1, d)))
    # A variable of type typ with index i is a member of the bulk family with exponent k if its value is the
    # standard form in sigma on the stretch: either all positions i + o are <= -1 (then k = -i; "left"), or all are
    # >= j0 (then k = t - i; "right": i may be negative, e.g. x(A_{-1}A_1) uses sigma_3, sigma_4, and k = t + 1).
    # lok = admissible k <= RW on the left, rok = admissible right indices i <= RW; beyond RW everything is standard.
    for typ in STD:
        offs = list(STD[typ])
        lok, rok, cutpos = set(), set(), []
        for i in range(-RW, RW + 1):
            if not cs.exists(typ, i): continue
            if v == "B" and typ == "e" and i == -2: continue   # the free variable x(A_{-2}A_0): in no equation
            actual = S.form_val(cs.near(typ, i))
            if S.std_val(typ, i) == actual:
                if all(i + o <= -1 for o in offs): lok.add(-i)
                else: rok.add(i)
                continue
            cutpos.append(i)
            out.append(dict(name=f"{typ}[{i}]", kind="cut", key=("cut", typ, i), const=six(actual, D_NEAR[typ]), atoms=[]))
        ex[typ] = dict(cut=cutpos, lok=lok, rok=rok)
        km = sum(Fr(x) * (1 if o % 2 == 0 else -1) for o, x in STD[typ].items())   # not (-1) ** o: a float for o < 0
        kl = Z3
        for o, x in STD[typ].items(): kl = kadd(kl, ksc(kpow(o), Fr(x)))
        for par in pars:
            c = sgn(par) * km / D_NEAR[typ]
            out.append(dict(name=f"{typ}[bulk,{par}]", kind="near", key=("near", typ), typ=typ, lok=lok, rok=rok,
                            const=(ksc(S.CL, c), ksc(S.CR, c)), atoms=[(ksc(kl, S.a / D_NEAR[typ]), par)]))
    slok, srok = set(range(1, RW + 1)), set(range(S.j0, RW + 1))        # sigma itself: k >= 1 or i >= j0
    ex["y"] = dict(cut=list(cs.cut_sigma), lok=slok, rok=srok)
    for c_ in cs.cut_sigma:
        out.append(dict(name=f"y[{c_}]", kind="cut", key=("cut", "y", c_), const=six(S.val[("s", c_)], 15), atoms=[]))
    for par in pars:
        out.append(dict(name=f"y[bulk,{par}]", kind="near", key=("near", "y"), typ="y", lok=slok, rok=srok,
                        const=(ksc(S.CL, sgn(par) / 15), ksc(S.CR, sgn(par) / 15)), atoms=[((S.a / 15, Fr(0), Fr(0)), par)]))
    for c_ in cs.cut_sigma:
        base = six(S.val[("s", c_)], 22)
        for par in pars:
            out.append(dict(name=f"BB[{c_};bulk,{par}]", kind="semi", key=("semi", c_), c=c_, lok=slok, rok=srok,
                            const=(kadd(base[0], ksc(S.CL, sgn(par) / 22)), kadd(base[1], ksc(S.CR, sgn(par) / 22))),
                            atoms=[((S.a / 22, Fr(0), Fr(0)), par)]))
    for p1, p2 in itertools.combinations_with_replacement(pars, 2):
        c = (sgn(p1) + sgn(p2)) / 22
        out.append(dict(name=f"BB[bulk,{p1};bulk,{p2}]", kind="bb", key=("bb",), lok=slok, rok=srok,
                        const=(ksc(S.CL, c), ksc(S.CR, c)),
                        atoms=[((S.a / 22, Fr(0), Fr(0)), p1), ((S.a / 22, Fr(0), Fr(0)), p2)]))
    for c in out:                                           # exact arithmetic only
        for el in list(c["const"]) + [coef for coef, _ in c["atoms"]]:
            assert all(type(x) is Fr for x in el), ("non-rational entry", c["name"])
    return out, ex


def member(C, k, i):
    """Is the exponent a member of the bulk family C? k = left distance if known, i = t - k if known (t >= T0 > 2 RW,
    so k <= RW and i <= RW exclude each other)."""
    if k is not None and k <= RW: return k in C["lok"]
    if i is not None and i <= RW: return i in C["rok"]
    return True


def admissible(S, X, Y, sol):
    """Is the solution a coincidence of two different classes inside the admissible ranges? Returns a reason
    string if it is not."""
    ax = [sol[("x", i)] for i in range(len(X["atoms"]))]
    ay = [sol[("y", i)] for i in range(len(Y["atoms"]))]
    if X["key"] == Y["key"] and sorted(ax) == sorted(ay): return "same class"
    teps = sol.get("eps")
    for C, asg in ((X, ax), (Y, ay)):
        if C["kind"] == "bb" and asg[0][0] == asg[1][0] and abs(asg[0][1] - asg[1][1]) < 3: return "B-pair not far"
        for g, k in asg:
            kk = k if g == 0 else None                                              # left distance, if absolute
            ii = (teps[1] - k) if (teps is not None and teps[0] == g) else None     # right index t - k, if known
            if not member(C, kk, ii): return "not a member of the family (position at the break)"
            if C["kind"] == "semi":
                if kk is not None and kk + C["c"] < 3: return "not far from the cut point"
                if ii is not None and ii - C["c"] < 3: return "not far from the cut point"
        if (C["kind"] == "bb" and teps is not None and teps[0] == asg[0][0] == asg[1][0] == 0
                and abs(asg[0][1] - asg[1][1]) > teps[1] - 3):
            return "B-pair not far"
    return None


def compare_all(S, log):
    classes, ex = build_classes(S)
    ncut = sum(1 for c in classes if c["kind"] == "cut")
    log(f"   {len(classes)} class families: {ncut} cut classes, exceptional positions " +
        ", ".join(f"{k}: {sorted(x['cut'])}" for k, x in ex.items()))
    bad, calls, nsol = [], 0, 0
    reasons = {}
    for ia, X in enumerate(classes):
        for Y in classes[ia:]:
            if X is Y and not X["atoms"]: continue
            atoms = []
            for tag, C, s_ in (("x", X, 1), ("y", Y, -1)):
                for i, (coef, par) in enumerate(C["atoms"]):
                    atoms.append([(tag, i), ksc(coef, Fr(s_)), 1 if par in (1, None) else 2, 1 if par is None else 2])
            atoms.append(["eps", ksub(X["const"][1], Y["const"][1]), T0, 2])
            G0 = ksub(Y["const"][0], X["const"][0])
            calls += 1
            for sol in solve(G0, atoms):
                nsol += 1
                why = admissible(S, X, Y, sol)
                if why is None:
                    bad.append((X["name"], Y["name"], {str(k): v for k, v in sol.items()}))
                else:
                    reasons[why] = reasons.get(why, 0) + 1
    log(f"   {calls} equations, {nsol} solutions in the relaxed ranges: " + ", ".join(f"{v} x {k}" for k, v in sorted(reasons.items()))
        + f"; coincidences of different classes: {len(bad)}")
    for b_ in bad[:40]: log(f"      COINCIDENCE {b_}")
    return dict(families=len(classes), cut_classes=ncut, equations=calls, relaxed_solutions=nsol, discarded=reasons,
                coincidences=bad, exceptional={k: sorted(x["cut"]) for k, x in ex.items()})


# ---------------------------------------------------------------- guard on a real cycle
def guard(S, t, log):
    v = S.v
    cs = Case(v, t)
    eps = kpow(-t)
    ev = lambda vec: kadd(tuple(vec[:3]), kmul(tuple(vec[3:]), eps))
    sval, qval = {}, {}

    def sig(j):
        j = cs.r(j)
        if j not in sval:
            if ("s", j) in S.val: sval[j] = ev(S.val[("s", j)])
            else:
                jj = j % t
                assert S.j0 <= jj <= t - 1
                sval[j] = ev(S.sval(jj))
        return sval[j]

    def sym(s_):
        if s_[0] == "s": return sig(s_[1])
        if s_[0] == "x": return ev(S.val[s_]) if s_ in S.val else Z3      # the free variable e-2 := 0
        j = cs.r(s_[1])
        if j not in qval:
            if ("q", j) in S.val: qval[j] = ev(S.val[("q", j)])
            else:
                qval[j] = kadd(kadd(sig(j + 2), ksc(sig(j + 4), 2)), ksc(sig(j + 5), 2))
        return qval[j]

    def form(f):
        out = Z3
        for s_, x in f.items(): out = kadd(out, ksc(sym(s_), x))
        return out

    d = metric(t).tolist(); n = 2 * t
    rem = 0 if v == "A" else t
    W = [x for x in range(n) if x != rem]

    def xval(a, b):
        """deviation x - d (alpha = 0) of a pair, and its class key."""
        if a > b: a, b = b, a
        if b < t:
            k = min((b - a) % t, (a - b) % t)
            if k != 2: return Z3, ("AA",)
            i = a if (b - a) % t == 2 else b
            return form(cs.e(i)), ("e", cs.r(i))
        if a >= t:
            i, j = a - t, b - t
            k = min((j - i) % t, (i - j) % t)
            if k >= 3: return kadd(sig(i), sig(j)), ("BB", i, j)
            lo = i if (j - i) % t == k else j
            return form(cs.b(lo) if k == 1 else cs.c(lo)), ("b" if k == 1 else "c", cs.r(lo))
        i, j = a, b - t
        o = cs.r(j - i)
        if abs(o) >= 3: return sig(j), ("y", j)
        typ = {0: "s", 1: "p", 2: "q", -1: "m", -2: "w"}[o]
        return form(cs.near(typ, i)), (typ, cs.r(i))

    X, keys = {}, {}
    for a, b in itertools.combinations(W, 2):
        X[(a, b)], keys[(a, b)] = xval(a, b)
    g = lambda a, b: X[(a, b) if a < b else (b, a)]
    ntri = 0
    for a, b in itertools.combinations(W, 2):
        for m_ in W:
            if m_ != a and m_ != b and d[a][b] == d[a][m_] + d[m_][b]:
                ntri += 1
                assert kzero(ksub(g(a, b), kadd(g(a, m_), g(m_, b)))), ("tight triple violated", t, a, b, m_)
    # class values pairwise different (x(A_{-2}A_0) is a free variable when B_0 is removed: skip it)
    vals = {}
    for pr, key in keys.items():
        if v == "B" and key == ("e", -2): continue
        D = ksc(X[pr], Fr(1, d[pr[0]][pr[1]]))
        if key in vals: assert vals[key] == D, ("not constant on a class", key)
        vals[key] = D
    seen = {}
    for key, D in vals.items():
        assert D not in seen, ("two classes with equal value", t, key, seen[D])
        seen[D] = key
    # the symbolic representation used in the search (build_classes) reproduces every class value
    classes, ex = build_classes(S)
    fam = {}
    for c in classes: fam.setdefault(c["key"], []).append(c)
    par_of = lambda k: None if not S.mixed else k % 2

    def rep(key, ks):
        """value of the family member with left distances ks (one per atom)."""
        want = sorted((par_of(k) for k in ks), key=str)
        for c in fam[key]:
            if sorted((p_ for _, p_ in c["atoms"]), key=str) == want:
                out = kadd(c["const"][0], kmul(c["const"][1], eps))
                todo = list(ks)
                for coef, p_ in c["atoms"]:
                    k = next(k for k in todo if par_of(k) == p_); todo.remove(k)
                    out = kadd(out, kmul(coef, kpow(-k)))
                return out
        raise KeyError((key, ks))
    for key, D in vals.items():
        if key == ("AA",): D2 = Z3
        elif key[0] == "BB":
            i, j = key[1], key[2]
            cut = [x for x in (i, j) if x in cs.cut_sigma]
            assert len(cut) < 2
            if cut: D2 = rep(("semi", cut[0]), [(-(j if cut[0] == i else i)) % t])
            else: D2 = rep(("bb",), [(-i) % t, (-j) % t])
        else:
            typ, i = key[0], cs.r(key[1])
            if abs(i) > RW: D2 = rep(("near", typ), [(-i) % t])
            elif i in ex[typ]["cut"]: D2 = rep(("cut", typ, i), [])
            elif i < 0 and -i in ex[typ]["lok"]: D2 = rep(("near", typ), [-i])
            else:
                assert i in ex[typ]["rok"], (typ, i)
                D2 = rep(("near", typ), [t - i])
        assert D2 == D, ("symbolic value differs from the value on the cycle", t, key, kfloat(D), kfloat(D2), [str(x) for x in ksub(D, D2)])
    nz = sum(1 for D in vals.values() if not kzero(D))
    log(f"   guard t = {t}: {ntri} tight triples of C_t - {v}_0 hold exactly; {len(vals)} classes, values pairwise different "
        f"({nz} nonzero)")
    return dict(t=t, tight_triples=ntri, classes=len(vals))


def selftest(log):
    """The search finds planted solutions, and reports a class duplicated under another name."""
    import random
    rnd = random.Random(5)

    def rk():
        while True:
            c = tuple(Fr(rnd.randint(-9, 9), rnd.randint(1, 9)) for _ in range(3))
            if not kzero(c): return c
    found = 0
    for _ in range(300):
        atoms, G0, truth = [], Z3, {}
        for i in range(rnd.randint(1, 5)):
            c, par = rk(), rnd.choice([1, 2])
            k = par + 2 * rnd.randint(0, 12)
            atoms.append([("x", i), c, par, 2]); truth[("x", i)] = k
            G0 = kadd(G0, kmul(c, kpow(-k)))
        c, tt = rk(), T0 + 2 * rnd.randint(0, 6)
        atoms.append(["eps", c, T0, 2]); truth["eps"] = tt
        G0 = kadd(G0, kmul(c, kpow(-tt)))
        found += any(all(s.get(k) == (0, v_) for k, v_ in truth.items()) for s in solve(G0, atoms))
    log(f"selftest: {found} of 300 planted solutions found")
    ok = found == 300
    global build_classes
    orig = build_classes
    for v in ("A", "B"):
        S = Solution(v, lambda s: None)
        dups = {}
        for c in orig(S)[0]:
            if c["kind"] != "AA": dups.setdefault(c["kind"], c)

        def mutated(S_, dups=dups):
            cl, ex = orig(S_)
            return cl + [dict(c, name=c["name"] + "_dup", key=c["key"] + ("dup",)) for c in dups.values()], ex
        build_classes = mutated
        r = compare_all(S, lambda s: None)
        build_classes = orig
        hit = {b_[0] for b_ in r["coincidences"]}
        good = all(c["name"] in hit for c in dups.values())
        log(f"selftest {v}_0: duplicated {[c['name'] for c in dups.values()]}; reported as coincidences: {good}")
        ok = ok and good
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guard", type=int, nargs="*", default=[19, 21, 23, 25, 27, 31])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    lines = []

    def log(s):
        print(s, flush=True); lines.append(s)
    if a.selftest:
        log("SELFTEST " + ("passed" if selftest(log) else "FAILED"))
        return
    res = {}
    for v in ("A", "B"):
        S = Solution(v, log)
        res[v] = dict(mixed=S.mixed, a=str(S.a), CL=[str(x) for x in S.CL], CR=[str(x) for x in S.CR],
                      free=[str(f) for f in S.free], guard=[guard(S, t, log) for t in a.guard])
        res[v].update(compare_all(S, log))
        log(f"   ({time.time() - t0:.0f} s)")
    ok = all(not res[v]["coincidences"] for v in res)
    log("RESULT: " + ("no forced merge for W = V - v, v = A_0 and B_0, for every odd t >= %d" % T0 if ok else "coincidences found, see above"))
    res["ok"] = ok; res["T0"] = T0; res["log"] = lines
    from metricpoly.jobs import atomic_write_json
    atomic_write_json(ROOT / "results/phase9/family_C_top.json", res)


if __name__ == "__main__":
    main()
