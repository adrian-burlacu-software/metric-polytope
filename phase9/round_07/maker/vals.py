# per target (n,D): over switchings, minimal value set (by span then size); histogram
import json, sys
from collections import Counter
UT = json.load(open('results/phase9/unreached_targets.json'))
n0, D0 = int(sys.argv[1]), int(sys.argv[2])
C = Counter(); ex = {}
for t in UT:
    if t['n'] != n0 or (D0 and t['D'] != D0): continue
    n, D = t['n'], t['D']
    P = [(i, j) for i in range(n) for j in range(i+1, n)]; v = t['nums']
    best = None
    for S in range(1 << (n-1)):
        vals = frozenset((D - a) if (((S << 1) >> i & 1) != ((S << 1) >> j & 1)) else a for (i, j), a in zip(P, v))
        key = (max(vals) - min(vals), len(vals), sorted(vals))
        if best is None or key < best: best = key
    C[(D, tuple(best[2]))] += 1
for k, c in sorted(C.items()): print(k, c)
