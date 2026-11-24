"""s = 3 group-C targets: which 3-node restrictions are reached, which 4-node frontier restrictions Z exist (canonical keys)."""
import json, sys, pickle, collections
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())
C = json.load(open('phase9/round_14/maker/groupC.json'))
Yc = collections.Counter(); Zc = collections.Counter(); per = collections.Counter()
Z4all = collections.Counter()
for c in C:
    if c['s'] != 3 or c['miss']: continue
    tid = c['tid']; tg = targets[tid]; n0 = tg.n; full = (1 << n0) - 1
    ys = set(); zs = set()
    for m in range(1, full):
        if bin(m).count('1') == 3 and tkeys[tid][m] in R: ys.add(tkeys[tid][m])
        if bin(m).count('1') == 4:
            sub3 = [m & ~(1 << v) for v in range(n0) if m >> v & 1]
            if any(tkeys[tid][q] in R for q in sub3): zs.add(tkeys[tid][m])
    for y in ys: Yc[y] += 1
    for z in zs: Zc[z] += 1
    per[(n0, tg.D, tuple(sorted(ys)))] += 1
print('reached 3-node Y:'); [print(' ', k, v) for k, v in Yc.most_common()]
print('frontier 4-node Z:'); [print(' ', k, v) for k, v in Zc.most_common()]
for k, v in sorted(per.items()): print(k, v)
# all reached 4-node keys with den divisible by 3
print('reached 4-node with 3|D:', sorted(k for k in R if k.startswith('4|') and int(k.split('|')[1]) % 3 == 0))
print('reached 3-node with 3|D:', sorted(k for k in R if k.startswith('3|') and int(k.split('|')[1]) % 3 == 0))
