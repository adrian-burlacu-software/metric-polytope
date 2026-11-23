# For targets (n, D): over all switchings, compute non-redundant edges + weights; report switchings minimizing #distinct weights then #edges
import json, sys, itertools
from collections import Counter
UT = json.load(open('results/phase9/unreached_targets.json'))
def mat(n, nums):
    M = [[0]*n for _ in range(n)]; it = iter(nums)
    for i in range(n):
        for j in range(i+1, n): M[i][j] = M[j][i] = next(it)
    return M
n0, D0, cnt = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
k = 0; summ = Counter()
for t in UT:
    if t['n'] != n0 or t['D'] != D0: continue
    n, D = n0, D0; M = mat(n, t['nums']); best = None
    for S in range(1 << (n-1)):
        Ss = {i+1 for i in range(n-1) if S >> i & 1}
        N = [[(D - M[a][b]) if ((a in Ss) != (b in Ss)) else M[a][b] for b in range(n)] for a in range(n)]
        E = [(i, j, N[i][j]) for i, j in itertools.combinations(range(n), 2)
             if not any(q not in (i, j) and N[i][q] + N[q][j] == N[i][j] for q in range(n))]
        W = sorted(set(w for _, _, w in E))
        key = (max(W), len(E))
        if best is None or key < best[0]: best = (key, E, W, N)
    _, E, W, N = best
    deg = Counter(); [deg.update([i, j]) for i, j, _ in E]
    summ[(tuple(W), len(E))] += 1
    if k < cnt:
        print('id', t['id'], 'W', W, '#E', len(E), 'degs', sorted(deg.values()), 'wcount', Counter(w for *_, w in E))
        print('   E', [(i, j, w) for i, j, w in E])
    k += 1
print(dict(summ))
