# For unreached targets (n, D filter): does some k-node restriction equal, up to switching, c * d_G (G graph on k nodes)?
import json, sys, itertools
from fractions import Fraction as F
UT = json.load(open('results/phase9/unreached_targets.json'))
def mat(n, nums):
    M = [[0]*n for _ in range(n)]; it = iter(nums)
    for i in range(n):
        for j in range(i+1, n): M[i][j] = M[j][i] = next(it)
    return M
def is_scaled_gm(N, k):
    # N integer matrix (units 1/D). Check N = c * shortest path metric of graph with edges = pairs at min value
    vals = [N[i][j] for i in range(k) for j in range(i+1,k)]
    m = min(vals)
    if m == 0: return None
    if any(v % m for v in vals): return None
    A = [[N[i][j]//m for j in range(k)] for i in range(k)]
    # A must be the shortest-path metric of graph with edges where A==1
    INF = 99
    d = [[0 if i==j else (1 if A[i][j]==1 else INF) for j in range(k)] for i in range(k)]
    for w in range(k):
        for i in range(k):
            for j in range(k):
                if d[i][w]+d[w][j] < d[i][j]: d[i][j] = d[i][w]+d[w][j]
    return (m, max(max(r) for r in A)) if d == A else None
n0, D0, k = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
hit = 0; tot = 0
from collections import Counter
C = Counter()
for t in UT:
    if t['n'] != n0 or (D0 and t['D'] != D0): continue
    tot += 1; n, D = t['n'], t['D']; M = mat(n, t['nums']); found = None
    for T in itertools.combinations(range(n), k):
        for S in range(1 << (k-1)):
            Ss = {T[i+1] for i in range(k-1) if S >> i & 1}
            N = [[(D - M[a][b]) if ((a in Ss) != (b in Ss)) else M[a][b] for b in T] for a in T]
            r = is_scaled_gm(N, k)
            if r: found = (T, r); break
        if found: break
    if found: hit += 1; C[(D, found[1])] += 1
print('n', n0, 'D', D0, 'k', k, 'hits', hit, '/', tot, dict(C))
