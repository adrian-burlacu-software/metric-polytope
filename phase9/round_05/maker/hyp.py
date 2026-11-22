"""Frontier hypotheses on the new column c relative to twin/antitwin columns t of y."""
import json, sys, pickle, collections, itertools, time
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import numpy as np
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())
def twins(Y, m):
    T = []
    for i in range(m):
        T.append((i, 0, tuple(F(0) if j == i else Y[i][j] for j in range(m))))
        T.append((i, 1, tuple(F(1) if j == i else 1 - Y[i][j] for j in range(m))))
    return T
cnt = collections.Counter(); byn = collections.Counter(); anyc = collections.Counter(); svals = collections.Counter()
for k, vs in front:
    u = point(k); n = u.n; M = d2.matrix(u); D = u.D
    tg = set()
    for v in vs:
        others = [j for j in range(n) if j != v]; m = len(others)
        c = tuple(F(int(M[v, j]), D) for j in others)
        Y = [[F(int(M[a, b]), D) for b in others] for a in others]
        for i, b, t in twins(Y, m):
            dd = [x - y for x, y in zip(c, t)]
            nz = [j for j in range(m) if dd[j]]
            if len(set(dd)) == 1:
                tg.add('H1_shift')
                # relative to smax: pendant from i at distance s (on the switched point)
                s = dd[0] if b == 0 else -dd[0]
                tt = t if b == 0 else tuple(1 - x if j != i else F(0) for j, x in enumerate(t))
                # y switched so node i side; smax = (2 - max perimeter through i)/2 computed on switched Y
                svals[str(abs(dd[0]))] += 1
            if len(set(abs(x) for x in dd)) == 1: tg.add('H2_signedshift')
            if len(nz) == 1: tg.add('H3_one_entry')
            if len(nz) == 2: tg.add('H4_two_entries')
    byn[n] += 1
    for t in tg: cnt[(n, t)] += 1
    if tg: anyc[n] += 1
print('frontier', dict(byn)); print('any', dict(anyc))
for kk in sorted(cnt): print(kk, cnt[kk])
print(svals.most_common(12))
