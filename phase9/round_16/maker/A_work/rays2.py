# per target: subsets T (5..8 nodes) with d|T an extreme ray of MET_|T| (even frame); covers A u B = V, |A n B| = 1 by such
import json, sys, itertools
from collections import Counter
sys.path.insert(0, 'phase9/round_16/maker/A_work')
from rk import rank_tight
data = json.load(open(sys.argv[1]))
cc = Counter(); cov = Counter(); sz = Counter()
for rec in data:
    d = rec['d']; good = []
    for k in range(4, 9):
        for T in itertools.combinations(range(9), k):
            r, m = rank_tight(d, T)
            if r == m - 1: good.append(frozenset(T))
    c1 = sum(1 for A in good for B in good if len(A | B) == 9 and len(A & B) == 1 and len(A) >= len(B))
    c2 = sum(1 for A in good for B in good if len(A | B) == 9 and len(A & B) == 2 and len(A) >= len(B))
    cov[(c1 > 0, c2 > 0)] += 1
    sz[max((len(T) for T in good), default=0)] += 1
    print(rec['id'], Counter(len(T) for T in good), 'ov1', c1, 'ov2', c2, flush=True)
print('covers (ov1, ov2):', dict(cov), 'max size', dict(sz))
