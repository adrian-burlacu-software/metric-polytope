"""Fiber-edge cases of the frontier: endpoints ea, eb and position t; classify endpoints."""
import json, sys, pickle, collections, itertools, time
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import numpy as np, sympy
from metricpoly import core
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())
t0 = time.time()
rows = []
for k, vs in front:
    if time.time() - t0 > 200: break
    u = point(k); n, D = u.n, u.D
    A, b = core.ineq_matrix(n)
    sl = b * D - A @ u.array()
    T = np.flatnonzero(sl == 0)
    M = d2.matrix(u)
    for v in vs:
        others = [j for j in range(n) if j != v]
        cols = [core.pidx(n, v, j) for j in others]
        sub = sympy.Matrix(A[np.ix_(T, cols)].tolist())
        ns = sub.nullspace()
        if len(ns) != 1: continue
        d = [F(int(sympy.fraction(t)[0]), int(sympy.fraction(t)[1])) for t in ns[0]]
        Ad = [sum(int(A[r, c]) * dd for c, dd in zip(cols, d)) for r in range(len(A))]
        hi = min((F(int(sl[r]), D) / Ad[r] for r in range(len(A)) if Ad[r] > 0), default=None)
        lo = max((F(int(sl[r]), D) / Ad[r] for r in range(len(A)) if Ad[r] < 0), default=None)
        if hi is None or lo is None: continue
        c = [F(int(M[v, j]), D) for j in others]
        ea = [ci + lo * di for ci, di in zip(c, d)]; eb = [ci + hi * di for ci, di in zip(c, d)]
        Y = [[F(int(M[a, bb]), D) for bb in others] for a in others]
        rows.append(dict(k=k, v=v, t=str((0 - lo) / (hi - lo)), c=[str(x) for x in c], ea=[str(x) for x in ea],
                         eb=[str(x) for x in eb], d=[str(x) for x in d], Y=[[str(x) for x in r] for r in Y]))
json.dump(rows, open('phase9/round_05/maker/edges2.json', 'w'))
print(len(rows), 'edge cases', round(time.time() - t0))
