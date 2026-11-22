"""For frontier pairs (u, v) whose new column lies on a fiber EDGE: exact endpoints and the position t on the edge."""
import json, sys, pickle, collections
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import numpy as np, sympy
from metricpoly import core
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())

out = collections.Counter(); ends = collections.Counter(); exs = []
for k, vs in front:
    u = point(k); n, D = u.n, u.D
    A, b = core.ineq_matrix(n)
    sl = b * D - A @ u.array()
    T = np.flatnonzero(sl == 0)
    for v in vs:
        cols = [core.pidx(n, v, j) for j in range(n) if j != v]
        sub = sympy.Matrix(A[np.ix_(T, cols)].tolist())
        ns = sub.nullspace()
        if len(ns) != 1: continue
        d = [F(int(sympy.fraction(t)[0]), int(sympy.fraction(t)[1])) for t in ns[0]]
        Ad = [sum(int(A[r, c]) * dd for c, dd in zip(cols, d)) for r in range(len(A))]
        # u + s d feasible: Ad_r * s <= sl_r / D
        hi = min((F(int(sl[r]), D) / Ad[r] for r in range(len(A)) if Ad[r] > 0), default=None)
        lo = max((F(int(sl[r]), D) / Ad[r] for r in range(len(A)) if Ad[r] < 0), default=None)
        if hi is None or lo is None: out['unbounded'] += 1; continue
        t = (0 - lo) / (hi - lo)
        t = min(t, 1 - t)
        out[(n, str(t))] += 1
        c = [F(int(x), D) for x in [d2.matrix(u)[v, j] for j in range(n) if j != v]]
        ea = [ci + lo * di for ci, di in zip(c, d)]; eb = [ci + hi * di for ci, di in zip(c, d)]
        if len(exs) < 6: exs.append((k, v, [str(x) for x in c], [str(x) for x in ea], [str(x) for x in eb]))
for kk, vv in sorted(out.items(), key=lambda z: -z[1])[:30]: print(kk, vv)
for e in exs: print(e)
