"""Backward cascade simulation of candidate one-node moves M(y) = {(y, c)} with c built from fiber vertices of y.
mode 'mid'  : c = (a+b)/2 for fiber vertices a, b
mode 'third': c = (2a+b)/3
Propagation uses the engine's cached lift/radial predecessor lists (glue ignored -> lower bound)."""
import json, sys, pickle, collections, time
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import numpy as np
from metricpoly import core
from metricpoly.core import Point
from metricpoly.dsl.prims import _fiber_vertices
from metricpoly.dsl.values import Partial
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())
modes = sys.argv[1].split(',')
LIMIT = float(sys.argv[2]) if len(sys.argv) > 2 else 250
preds = st['preds']
Rs = set(R)
allkeys = list(rep)
t0 = time.time()
cache = {}

def fib_cols(u, v):
    n = u.n
    M = d2.matrix(u)
    known = {(i, j): F(int(M[i, j]), u.D) for i in range(n) for j in range(i + 1, n) if v not in (i, j)}
    P = Partial.make(n, known)
    return [tuple(x.fractions()[core.pidx(n, v, j)] for j in range(n) if j != v) for x in _fiber_vertices(P)]

def test(k, v):
    if (k, v) in cache: return cache[(k, v)]
    u = point(k); n = u.n; M = d2.matrix(u)
    c = tuple(F(int(M[v, j]), u.D) for j in range(n) if j != v)
    V = fib_cols(u, v); Vs = set(V)
    ok = False
    for a in V:
        if 'mid' in modes and tuple(2 * ci - ai for ci, ai in zip(c, a)) in Vs: ok = True; break
        if 'third' in modes and tuple(3 * ci - 2 * ai for ci, ai in zip(c, a)) in Vs: ok = True; break
        if 'quarter' in modes and tuple(4 * ci - 3 * ai for ci, ai in zip(c, a)) in Vs: ok = True; break
    cache[(k, v)] = ok
    return ok

rnd = 0; added_move = 0
while True:
    rnd += 1
    ch = True
    while ch:
        ch = False
        for k in allkeys:
            if k in Rs: continue
            for mv in ('lift', 'radial'):
                if any(p in Rs for p in preds.get((mv, k), ())):
                    Rs.add(k); ch = True; break
    new = set()
    for k in allkeys:
        if k in Rs or time.time() - t0 > LIMIT: continue
        n = int(k.split('|')[0])
        if n < 4: continue
        full = (1 << n) - 1
        for v in range(n):
            if subkey(k, full & ~(1 << v)) in Rs and test(k, v):
                new.add(k); break
    added_move += len(new)
    print('round', rnd, 'move adds', len(new), 'reached', len(Rs), 'time', round(time.time() - t0), flush=True)
    if not new or time.time() - t0 > LIMIT: break
    Rs |= new
gain = Rs - set(R)
print(modes, 'gained nodes', len(gain), collections.Counter(int(k.split('|')[0]) for k in gain),
      'targets', len(gain & TK), 'checks', len(cache), 'time', round(time.time() - t0))
