"""Backward cascade simulation (as round_04 simulate.py) for cheap column generators.
modes: rc_twin  : twin/antitwin column of node i, with one entry j re-centred to t in its feasible range
       rc_fiber : fiber vertex with one entry re-centred (t = 1/2)
       pendant  : twin/antitwin of i shifted by s*1, s = t*smax (pendant node hanging off i)
Glue ignored -> lower bound."""
import json, sys, pickle, collections, time
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import numpy as np
from metricpoly import core
from metricpoly.dsl.prims import _fiber_vertices
from metricpoly.dsl.values import Partial
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())
modes = sys.argv[1].split(','); LIMIT = float(sys.argv[2]); TS = [F(x) for x in sys.argv[3].split(',')]
preds = st['preds']; Rs = set(R); allkeys = list(rep); t0 = time.time(); cache = {}; ncols = []

def twins(Y, m):
    for i in range(m):
        yield i, tuple(F(0) if j == i else Y[i][j] for j in range(m))
        yield i, tuple(F(1) if j == i else 1 - Y[i][j] for j in range(m))
def rng(a, Y, j, m):
    L = max(abs(a[k] - Y[j][k]) for k in range(m) if k != j)
    U = min(min(a[k] + Y[j][k], 2 - a[k] - Y[j][k]) for k in range(m) if k != j)
    return L, U
def recenters(a, Y, m, out):
    for j in range(m):
        L, U = rng(a, Y, j, m)
        for t in TS:
            b = list(a); b[j] = L + t * (U - L); out.add(tuple(b))
def gen(u, v):
    n = u.n; M = d2.matrix(u); others = [j for j in range(n) if j != v]; m = len(others)
    Y = [[F(int(M[a, b]), u.D) for b in others] for a in others]
    out = set()
    if 'rc_twin' in modes:
        for i, t in twins(Y, m): recenters(t, Y, m, out)
    if 'pendant' in modes:
        for i, t in twins(Y, m):
            # t + s*1 feasible iff for all j,k: t_j + t_k + Y_jk + 2s <= 2 and t_j - t_k <= Y_jk (unchanged)
            # and t_j + s... triangle c_j <= c_k + Y_jk unchanged; Y_jk <= c_j + c_k ok. so smax from perimeter
            smax = min((2 - t[j] - t[k] - Y[j][k]) / 2 for j in range(m) for k in range(m) if j != k)
            for s in TS: out.add(tuple(x + s * smax for x in t))
    if 'rc_fiber' in modes:
        known = {(i, j): F(int(M[i, j]), u.D) for i in range(n) for j in range(i + 1, n) if v not in (i, j)}
        P = Partial.make(n, known)
        for x in _fiber_vertices(P):
            a = tuple(x.fractions()[core.pidx(n, v, j)] for j in range(n) if j != v)
            recenters(a, Y, m, out)
    return out, tuple(F(int(M[v, j]), u.D) for j in others)
def test(k, v):
    if (k, v) not in cache:
        u = point(k); out, c = gen(u, v); cache[(k, v)] = c in out; ncols.append((u.n - 1, len(out)))
    return cache[(k, v)]
rnd = 0
while True:
    rnd += 1; ch = True
    while ch:
        ch = False
        for k in allkeys:
            if k in Rs: continue
            for mv in ('lift', 'radial'):
                if any(p in Rs for p in preds.get((mv, k), ())): Rs.add(k); ch = True; break
    new = set()
    for k in allkeys:
        if k in Rs or time.time() - t0 > LIMIT: continue
        n = int(k.split('|')[0])
        if n < 4: continue
        full = (1 << n) - 1
        for v in range(n):
            if subkey(k, full & ~(1 << v)) in Rs and test(k, v): new.add(k); break
    print('round', rnd, 'adds', len(new), 'reached', len(Rs), 'time', round(time.time() - t0), flush=True)
    if not new or time.time() - t0 > LIMIT: break
    Rs |= new
gain = Rs - set(R)
tg = gain & TK
print(modes, [str(t) for t in TS], 'gained', len(gain), sorted(collections.Counter(int(k.split('|')[0]) for k in gain).items()),
      'targets', len(tg), sorted(collections.Counter(int(k.split('|')[0]) for k in tg).items()), 'time', round(time.time() - t0))
print('target D', sorted(collections.Counter(int(k.split('|')[1]) for k in tg).items()))
cs = collections.defaultdict(list)
for m, c in ncols: cs[m].append(c)
print('cols per input by input size', {m: (min(v), max(v), round(sum(v) / len(v))) for m, v in sorted(cs.items())})
