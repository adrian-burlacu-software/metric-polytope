"""Direct check of a DSL move on frontier pairs: reached (s)-node restriction Y of an unreached target, unreached
(s+1)-node restriction Z = Y + v. Counts pairs where the move applied to Y yields Z (canonical keys)."""
import sys, json, time, random, collections
sys.path.insert(0, 'scripts/phase9'); sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
from common import interpreter
import pickle, detour_depth2 as d2
from metricpoly import group
exec(open('phase9/round_04/maker/frontier_load.py').read())
f, name, n0, lim = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
I, _ = interpreter([f]); mv = I.moves[name]
pairs = []
for tid, tg in enumerate(targets):
    if tg.n != n0: continue
    full = (1 << n0) - 1
    if tkeys[tid][full] not in TK: continue
    for m in range(1, full):
        if bin(m).count('1') < 4 or tkeys[tid][m] not in R: continue
        for v in range(n0):
            if m >> v & 1: continue
            Z = tkeys[tid][m | (1 << v)]
            if Z in R: continue
            pairs.append((tkeys[tid][m], Z))
pairs = sorted(set(pairs)); random.seed(2); random.shuffle(pairs)
hit = collections.Counter(); tot = collections.Counter(); cache = {}; t0 = time.time()
for yk, zk in pairs[:lim]:
    if yk not in cache:
        cache[yk] = {group.canonical(o).key() for o in I.apply_move(mv, [point(yk)], as_orbits=True)}
    s = int(zk.split('|')[0]); tot[s] += 1; hit[s] += zk in cache[yk]
print(name, 'n', n0, 'pairs tested', sum(tot.values()), 'of', len(pairs), 'hits by Z size', dict(hit), 'tested by size', dict(tot), round(time.time() - t0), 's')
# sim-style radxm test on the same pairs (column of node v over Y = Z - v), for consistency with sim3.py
from fractions import Fraction as F
def simtest(zk, yk):
    tid, mask = rep[zk]; zp = point(zk); n = zp.n; M = d2.matrix(zp)
    ok = False
    for v in range(n):
        others = [j for j in range(n) if j != v]
        if subkey(zk, ((1 << n) - 1) & ~(1 << v)) != yk: continue
        m = len(others); Y = [[F(int(M[a, b]), zp.D) for b in others] for a in others]
        c = tuple(F(int(M[v, j]), zp.D) for j in others); cc = tuple(1 - x for x in c)
        for S in range(1 << (m - 1)):
            Ss = {a + 1 for a in range(m - 1) if S >> a & 1}
            Zm = [[(1 - Y[a][b]) if ((a in Ss) != (b in Ss)) and a != b else Y[a][b] for b in range(m)] for a in range(m)]
            mx = max(Zm[a][b] for a in range(m) for b in range(m))
            for j in range(m):
                if not any(Zm[j][b] == mx for b in range(m)): continue
                al = max(Zm[a][b] for a in range(m) for b in range(m) if a != j and b != j) / 2
                L = max(abs(al - Zm[j][k]) for k in range(m) if k != j)
                col = [al] * m; col[j] = L
                o = tuple((1 - col[a]) if a in Ss else col[a] for a in range(m))
                if o == c or o == cc: ok = True
    return ok
agree = collections.Counter()
for yk, zk in pairs[:lim]:
    agree[(zk in cache[yk], simtest(zk, yk))] += 1
print('(dsl, sim) agreement', dict(agree))
