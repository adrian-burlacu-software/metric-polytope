# Is some switching of x equal to lam*(d_G + d_H) for graphs G, H on the same nodes?
import json, sys, itertools
from fractions import Fraction as F
from collections import Counter
UT = json.load(open('results/phase9/unreached_targets.json'))
def apsp(n, E):
    INF = 99; d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for i, j in E: d[i][j] = d[j][i] = 1
    for w in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][w] + d[w][j] < d[i][j]: d[i][j] = d[i][w] + d[w][j]
    return d
def try_split(n, d):
    P = [(i, j) for i in range(n) for j in range(i+1, n)]
    both = [p for p in P if d[p[0]][p[1]] == 2]
    three = [p for p in P if d[p[0]][p[1]] == 3]
    if len(three) > 16: return None
    for mask in range(1 << len(three)):
        if three and mask >> (len(three) - 1) & 1: continue  # symmetry G<->H
        G = both + [three[i] for i in range(len(three)) if mask >> i & 1]
        H = both + [three[i] for i in range(len(three)) if not mask >> i & 1]
        dg, dh = apsp(n, G), apsp(n, H)
        if all(dg[i][j] + dh[i][j] == d[i][j] for i, j in P): return (len(G), len(H))
    return None
n0, D0 = int(sys.argv[1]), int(sys.argv[2]); res = Counter()
for t in UT:
    if t['n'] != n0 or (D0 and t['D'] != D0): continue
    n, D = t['n'], t['D']; P = [(i, j) for i in range(n) for j in range(i+1, n)]; found = None
    for S in range(1 << (n-1)):
        s = S << 1
        v = [F((D - a) if ((s >> i & 1) != (s >> j & 1)) else a, D) for (i, j), a in zip(P, t['nums'])]
        m = min(v)
        if m == 0: continue
        lam = m / 2
        dd = [x / lam for x in v]
        if any(x.denominator != 1 for x in dd): continue
        d = [[0]*n for _ in range(n)]
        for (i, j), a in zip(P, dd): d[i][j] = d[j][i] = int(a)
        r = try_split(n, d)
        if r: found = (str(lam), r); break
    res[(D, found is not None)] += 1
print(sorted(res.items()))
