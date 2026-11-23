# Test: some switching of x equals (2/tau)(d_G + c) or (1/tau')(d_G + c) generally x = lam*(d_G + c J), G graph, c>=0 integer
import json, sys, itertools
from fractions import Fraction as F
from collections import Counter
UT = json.load(open('results/phase9/unreached_targets.json'))
def apsp(n, adj):
    INF = 99; d = [[0 if i == j else (1 if adj[i][j] else INF) for j in range(n)] for i in range(n)]
    for w in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][w] + d[w][j] < d[i][j]: d[i][j] = d[i][w] + d[w][j]
    return d
def test(n, M):
    # M matrix of Fractions; find c, lam: M = lam*(d_G + c) off-diagonal. Let m = min, then lam*(1+c) = m.
    vals = sorted(set(M[i][j] for i in range(n) for j in range(i+1, n)))
    m = vals[0]
    if m == 0: return None
    for c in range(0, 6):
        lam = m / (1 + c)
        d = [[(M[i][j] / lam - c) if i != j else 0 for j in range(n)] for i in range(n)]
        if any(d[i][j].denominator != 1 for i in range(n) for j in range(n)): continue
        adj = [[d[i][j] == 1 for j in range(n)] for i in range(n)]
        g = apsp(n, adj)
        if all(g[i][j] == d[i][j] for i in range(n) for j in range(n)): return (c, lam, max(max(r) for r in g))
    return None
n0 = int(sys.argv[1]); C = Counter(); NC = Counter(); EX = {}
for t in UT:
    if t['n'] != n0: continue
    n, D = t['n'], t['D']; it = iter(t['nums']); X = [[F(0)]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n): X[i][j] = X[j][i] = F(next(it), D)
    found = None
    for S in range(1 << (n-1)):
        Ss = {i+1 for i in range(n-1) if S >> i & 1}
        M = [[(1 - X[i][j]) if ((i in Ss) != (j in Ss)) else X[i][j] for j in range(n)] for i in range(n)]
        r = test(n, M)
        if r and (found is None or r[0] < found[0]): found = r
    if found: C[(D, found[0], found[2])] += 1; EX.setdefault((D, found[0], found[2]), t['id'])
    else: NC[D] += 1
print('found', sorted(C.items())); print('none', sorted(NC.items()))
print(EX)
