# For targets (n,D): maximal restrictions that are lam*d_G (up to switching); can two of them cover all nodes?
import json, sys, itertools
from fractions import Fraction as F
from collections import Counter
sys.argv += []
exec(open('phase9/round_07/maker/chain.py').read().split("n0, D0, k0")[0])
n0, D0 = int(sys.argv[1]), int(sys.argv[2])
res = Counter(); lamc = Counter()
for t in UT:
    if t['n'] != n0 or (D0 and t['D'] != D0): continue
    n, D = t['n'], t['D']; it = iter(t['nums']); X = [[F(0)] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n): X[i][j] = X[j][i] = F(next(it), D)
    good = {}
    for k in range(4, n):
        for T in itertools.combinations(range(n), k):
            g = is_scaled_gm(X, list(T))
            if g: good[frozenset(T)] = g
    best = None
    for A, B in itertools.combinations(good, 2):
        if len(A | B) == n and A & B:
            key = (min(len(A), len(B)), len(A) + len(B))
            if best is None or key > best[0]: best = (key, sorted(A), sorted(B), good[A], good[B])
    res[(D, best[0] if best else None)] += 1
    if best: lamc[(str(best[3][0]), str(best[4][0]))] += 1
print(sorted(res.items(), key=str)); print(lamc)
