import json, sys, itertools
from collections import Counter
UT = json.load(open('results/phase9/unreached_targets.json'))
n0, D0, show = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
k = 0; summ = Counter()
for t in UT:
    if t['n'] != n0 or t['D'] != D0: continue
    n, D = n0, D0; P = [(i, j) for i in range(n) for j in range(i+1, n)]
    for S in range(1 << (n-1)):
        s = S << 1
        v = [(D - a) if ((s >> i & 1) != (s >> j & 1)) else a for (i, j), a in zip(P, t['nums'])]
        if all(a % 2 == 0 for a in v):
            d = [[0]*n for _ in range(n)]
            for (i, j), a in zip(P, v): d[i][j] = d[j][i] = a // 2
            E = [(i, j, d[i][j]) for i, j in P if not any(q not in (i, j) and d[i][q] + d[q][j] == d[i][j] for q in range(n))]
            W = Counter(w for *_, w in E)
            deg = Counter(); [deg.update([i, j]) for i, j, _ in E]
            summ[tuple(sorted(W.items()))] += 1
            if k < show:
                print(t['id'], 'W', dict(W), 'degs', sorted(deg.values()))
                for r in d: print('   ', r)
            k += 1
            break
print(summ)
