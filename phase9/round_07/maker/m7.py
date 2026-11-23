import sys, itertools
sys.path.insert(0, '.')
from metricpoly import deza
from collections import Counter
n = int(sys.argv[1]); Dw = int(sys.argv[2])
for idx, p in enumerate(deza.load_ext(n)):
    if p.D != Dw: continue
    P = [(i, j) for i in range(n) for j in range(i+1, n)]
    best = None
    for S in range(1 << (n-1)):
        s = S << 1
        v = [(p.D - a) if ((s >> i & 1) != (s >> j & 1)) else a for (i, j), a in zip(P, p.nums)]
        key = (max(v) - min(v), len(set(v)), sorted(v), v)
        if best is None or key[:3] < best[:3]: best = key
    v = best[3]; d = [[0]*n for _ in range(n)]
    for (i, j), a in zip(P, v): d[i][j] = d[j][i] = a
    E = [(i, j, d[i][j]) for i, j in P if not any(q not in (i, j) and d[i][q] + d[q][j] == d[i][j] for q in range(n))]
    print(idx + 1, 'D', p.D, 'vals', sorted(set(v)), 'W', dict(Counter(w for *_, w in E)), 'E', E)
