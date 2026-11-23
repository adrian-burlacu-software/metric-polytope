# extract integer metric d (unique even switching for odd D) of unreached targets; print with perimeter info
import json, sys, itertools
from collections import Counter
UT = json.load(open('results/phase9/unreached_targets.json'))
def dmetric(t):
    n, D = t['n'], t['D']; P = [(i, j) for i in range(n) for j in range(i+1, n)]
    for S in range(1 << (n-1)):
        s = S << 1
        v = [(D - a) if ((s >> i & 1) != (s >> j & 1)) else a for (i, j), a in zip(P, t['nums'])]
        if all(a % 2 == 0 for a in v):
            d = [[0]*n for _ in range(n)]
            for (i, j), a in zip(P, v): d[i][j] = d[j][i] = a // 2
            return d, s
    return None, None
if __name__ == '__main__':
    n0 = int(sys.argv[1]); Ds = [int(a) for a in sys.argv[2].split(',')]
    out = []
    for t in UT:
        if t['n'] != n0 or t['D'] not in Ds: continue
        d, s = dmetric(t)
        n = t['n']
        if d is None: print(t['id'], t['D'], 'no even frame'); continue
        tau = max(d[a][b]+d[a][c]+d[b][c] for a,b,c in itertools.combinations(range(n),3))
        vals = Counter(d[i][j] for i in range(n) for j in range(i+1,n))
        out.append({'id': t['id'], 'D': t['D'], 'n': n, 'd': d, 'S': s, 'tau': tau})
        print(t['id'], 'D', t['D'], 'tau', tau, 'vals', dict(sorted(vals.items())))
    json.dump(out, open(f'phase9/round_08/maker/dmet_n{n0}.json', 'w'))
