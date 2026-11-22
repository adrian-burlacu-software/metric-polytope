import json, collections
from fractions import Fraction as F
R = json.load(open('phase9/round_05/maker/edges2.json'))
cnt = collections.Counter()
for r in R:
    d = [F(x) for x in r['d']]; nz = [x for x in d if x]
    mx = max(abs(x) for x in nz); dn = tuple(sorted(x / mx for x in nz))
    t = F(r['t']); t = min(t, 1 - t)
    cnt[(len(d), len(nz), str(t), tuple(sorted(set(abs(x / mx) for x in nz))) )] += 1
for k, v in sorted(cnt.items(), key=lambda z: -z[1])[:30]: print(k, v)
for r in R[:6]:
    print(r['k'], r['v'], r['t']); print(' c ', r['c']); print(' ea', r['ea']); print(' eb', r['eb']); print(' Y', r['Y'])
