# For targets (n, D): does a lift chain exist from a k0-node restriction equal (up to switching) to lam*d_G
# (G graph, any lam) up to the full target, each step's new column a vertex of the fiber over the previous restriction?
import json, sys, itertools
from fractions import Fraction as F
from collections import Counter
UT = json.load(open('results/phase9/unreached_targets.json'))
def rank(rows):
    rows = [list(r) for r in rows]; r = 0; ncol = len(rows[0]) if rows else 0
    for c in range(ncol):
        p = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if p is None: continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                f = rows[i][c] / rows[r][c]; rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        r += 1
    return r
def fiber_vertex(X, T, v):
    m = len(T); rows = []
    for a in range(m):
        for b in range(a + 1, m):
            i, j = T[a], T[b]; y = X[i][j]; bi, bj = X[v][i], X[v][j]
            e = [F(0)] * m
            if bi - bj == y: e2 = e[:]; e2[a] = F(1); e2[b] = F(-1); rows.append(e2)
            if bj - bi == y: e2 = e[:]; e2[a] = F(-1); e2[b] = F(1); rows.append(e2)
            if bi + bj == y or bi + bj == 2 - y: e2 = e[:]; e2[a] = F(1); e2[b] = F(1); rows.append(e2)
    return len(rows) >= m and rank(rows) == m
def is_scaled_gm(X, T):
    k = len(T); vals = [X[a][b] for a, b in itertools.combinations(T, 2)]
    # try all switchings within T
    for S in range(1 << (k - 1)):
        Ss = {T[i + 1] for i in range(k - 1) if S >> i & 1}
        N = {(a, b): (1 - X[a][b]) if ((a in Ss) != (b in Ss)) else X[a][b] for a, b in itertools.combinations(T, 2)}
        m = min(N.values())
        if m == 0: continue
        A = {e: N[e] / m for e in N}
        if any(v.denominator != 1 for v in A.values()): continue
        INF = 99; d = {(a, b): (0 if a == b else INF) for a in T for b in T}
        for (a, b), v in A.items():
            if v == 1: d[(a, b)] = d[(b, a)] = 1
        for w in T:
            for a in T:
                for b in T:
                    if d[(a, w)] + d[(w, b)] < d[(a, b)]: d[(a, b)] = d[(a, w)] + d[(w, b)]
        if all(d[e] == A[e] for e in A): return (m, max(A.values()))
    return None
n0, D0, k0 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
res = Counter()
for t in UT:
    if t['n'] != n0 or (D0 and t['D'] != D0): continue
    n, D = t['n'], t['D']; it = iter(t['nums']); X = [[F(0)] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n): X[i][j] = X[j][i] = F(next(it), D)
    ok = None
    def ext(T):
        if len(T) == n: return True
        for v in range(n):
            if v in T: continue
            if fiber_vertex(X, T, v) and ext(T + [v]): return True
        return False
    for T in itertools.combinations(range(n), k0):
        g = is_scaled_gm(X, list(T))
        if g and ext(list(T)): ok = g; break
    res[(D, ok is not None)] += 1
    if ok: print(t['id'], D, 'seed', ok)
print(sorted(res.items()))
