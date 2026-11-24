# summarise covers A u B = V, |A n B| = ov, by (|A|,a,degsA | |B|,b,degsB) over targets
import json, sys
from collections import Counter, defaultdict
f = sys.argv[1]; ov = int(sys.argv[2])
data = json.load(open(f))
summ = Counter(); nocov = []; ntype = Counter()
for rec in data:
    n = 9
    g = {frozenset(T): L for T, L in rec['goods']}
    types = set()
    Ts = list(g)
    for i, A in enumerate(Ts):
        for B in Ts:
            if len(A | B) == n and len(A & B) == ov and (len(A), sorted(A)) >= (len(B), sorted(B)) and A != B:
                for SA, ma, ea, da, EA in g[A]:
                    for SB, mb, eb, db, EB in g[B]:
                        types.add((len(A), ma, tuple(da), len(B), mb, tuple(db)))
    for t in types: summ[t] += 1
    ntype[len(types) > 0] += 1
    if not types: nocov.append(rec['id'])
print('targets with a cover:', dict(ntype))
for k, v in summ.most_common(25): print(v, k)
