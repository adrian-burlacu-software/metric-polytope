"""Frontier test of cheap column families (no fiber vertices): is the new column c of an unreached frontier node u
(with reached deletion y = u - v) a simple combination of twin/antitwin columns of y (and constants)?"""
import json, sys, pickle, collections, itertools, time
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import numpy as np
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())

def twins(Y, m):
    T = []
    for i in range(m):
        T.append(tuple(F(0) if j == i else Y[i][j] for j in range(m)))
        T.append(tuple(F(1) if j == i else 1 - Y[i][j] for j in range(m)))
    return T

def fams(c, Y, m):
    T = twins(Y, m); Ts = set(T); tags = set()
    if c in Ts: tags.add('twin')
    for a, b in itertools.combinations(T, 2):
        if tuple((x + y) / 2 for x, y in zip(a, b)) == c: tags.add('mid2')
    for a in T:
        for b in T:
            if a != b and tuple((2 * x + y) / 3 for x, y in zip(a, b)) == c: tags.add('third2')
            if a != b and tuple((3 * x + y) / 4 for x, y in zip(a, b)) == c: tags.add('quarter2')
    for a, b, d in itertools.combinations(T, 3):
        if tuple((x + y + z) / 3 for x, y, z in zip(a, b, d)) == c: tags.add('cent3')
    # twin & const r : (t + r)/2  -> 2c - t constant
    for a in T:
        s = set(2 * x - y for x, y in zip(c, a))
        if len(s) == 1: tags.add('mid_twin_const')
    return tags

cnt = collections.Counter(); byn = collections.Counter(); anyhit = collections.Counter()
t0 = time.time()
for k, vs in front:
    u = point(k); n = u.n; M = d2.matrix(u); D = u.D
    tg = set()
    for v in vs:
        others = [j for j in range(n) if j != v]
        c = tuple(F(int(M[v, j]), D) for j in others)
        Y = [[F(int(M[a, b]), D) for b in others] for a in others]
        tg |= fams(c, Y, len(others))
    byn[n] += 1
    for t in tg: cnt[(n, t)] += 1
    if tg: anyhit[n] += 1
print('frontier by n', dict(byn)); print('any cheap family', dict(anyhit))
for kk in sorted(cnt): print(kk, cnt[kk])
print('time', round(time.time() - t0))
