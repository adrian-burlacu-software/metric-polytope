# even-frame integer metric d (x = 2d/D) for odd-D n=9 targets; value sets, essential-edge weights, aut
import json, sys, itertools
from collections import Counter
sys.path.insert(0, 'phase9/round_16/maker/A_work')
from cov9 import load
n = 9; Ds = {int(a) for a in sys.argv[1].split(',')}
out = []
vc = Counter(); ec = Counter(); essn = Counter(); perim = Counter()
for tid, D, X in load(n, Ds):
    # parity pattern must be a cut: S = nodes j with X[0][j] odd
    S = {j for j in range(1, n) if X[0][j] % 2}
    Y = [[(D - X[i][j]) if ((i in S) != (j in S)) else X[i][j] for j in range(n)] for i in range(n)]
    if not all(Y[i][j] % 2 == 0 for i in range(n) for j in range(n)):
        print(tid, D, "NOT-EVEN"); continue
    d = [[Y[i][j] // 2 for j in range(n)] for i in range(n)]
    vals = sorted(Counter(d[i][j] for i, j in itertools.combinations(range(n), 2)).items())
    ess = [(i, j) for i, j in itertools.combinations(range(n), 2)
           if not any(d[i][k] + d[k][j] == d[i][j] for k in range(n) if k not in (i, j))]
    ew = Counter(d[i][j] for i, j in ess)
    mp = max(d[i][j] + d[i][k] + d[j][k] for i, j, k in itertools.combinations(range(n), 3))
    out.append({'id': tid, 'D': D, 'd': d, 'S': sorted(S), 'ess': ess})
    vc[tuple(v for v, c in vals)] += 1; ec[tuple(sorted(ew))] += 1; essn[len(ess)] += 1; perim[mp == D] += 1
    print(tid, D, 'vals', vals, 'ess', len(ess), dict(sorted(ew.items())), 'maxper==D', mp == D)
print('value sets', vc.most_common(10)); print('ess weights', ec.most_common(10)); print('ness', sorted(essn.items())); print(perim)
json.dump(out, open('phase9/round_16/maker/A_work/dmet_%s.json' % sys.argv[1].replace(',', '_'), 'w'))
