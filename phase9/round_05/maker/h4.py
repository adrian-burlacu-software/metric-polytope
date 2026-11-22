import json, sys, pickle, collections, itertools, time
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import numpy as np
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())
cnt = collections.Counter(); ex = []
for k, vs in front:
    u = point(k); n = u.n; M = d2.matrix(u); D = u.D
    for v in vs:
        others = [j for j in range(n) if j != v]; m = len(others)
        c = tuple(F(int(M[v, j]), D) for j in others)
        Y = [[F(int(M[a, b]), D) for b in others] for a in others]
        for i in range(m):
          for b in (0, 1):
            Ys = [[Y[p][q] if ((p == i) == (q == i)) or b == 0 else 1 - Y[p][q] for q in range(m)] for p in range(m)]
            cc = c if b == 0 else tuple(1 - x if j != i else x for j, x in enumerate(c))  # switch at node i (v joins side of i)
            # after switching y at {i}... simpler: compare to twin in switched frame
            t = tuple(F(0) if j == i else Y[i][j] for j in range(m)) if b == 0 else tuple(F(1) if j == i else 1 - Y[i][j] for j in range(m))
            dd = [x - y for x, y in zip(c, t)]
            nz = [j for j in range(m) if dd[j]]
            if len(nz) != 2: continue
            if i in nz:
                j = [q for q in nz if q != i][0]
                a = abs(dd[i]); bb = dd[j] if b == 0 else -dd[j]
                rel = 'cj=+ci' if bb == a else 'cj=-ci' if bb == -a else 'other'
                cnt[('i_in', rel)] += 1
                if len(ex) < 5 and rel == 'other': ex.append((k, v, i, b, [str(x) for x in c], [str(x) for x in t]))
            else:
                cnt[('i_out', 'eq' if abs(dd[nz[0]]) == abs(dd[nz[1]]) else 'neq')] += 1
print(cnt)
for e in ex: print(e)
