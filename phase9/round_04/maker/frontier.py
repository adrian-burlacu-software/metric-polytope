"""Frontier analysis: unreached nodes u with a REACHED one-node deletion y = u - v.
Classifies the new column c (distances from v) relative to y.  Exact (Fractions + certified rank)."""
import json, sys, pickle, collections, itertools, time
from fractions import Fraction as F
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
import numpy as np
from metricpoly import core, group
from metricpoly.core import Point
import detour_depth2 as d2
from metricpoly.dsl.prims import certified_rank_is

st = pickle.load(open('checkpoints/phase9/engine/engine.pkl', 'rb'))
targets, tkeys, rep = st['targets'], st['tkeys'], st['rep']
R = set(json.load(open('checkpoints/phase9/reached.json')))
U = json.load(open('results/phase9/unreached_nodes.json')); UK = set(U['keys']); TK = set(U['target_keys'])

def bits(m): return [v for v in range(m.bit_length()) if m >> v & 1]
def subkey(k, lm):
    tid, mask = rep[k]; T = bits(mask)
    return tkeys[tid][sum(1 << T[i] for i in bits(lm))]
def point(k):
    tid, mask = rep[k]; return d2.restrict(d2.matrix(targets[tid]), targets[tid].D, bits(mask))

front = []
for k in UK:
    if k not in rep: continue
    n = int(k.split('|')[0])
    if n < 4: continue
    full = (1 << n) - 1
    vs = [v for v in range(n) if subkey(k, full & ~(1 << v)) in R]
    if vs: front.append((k, vs))
print('frontier nodes', len(front), collections.Counter(int(k.split('|')[0]) for k, _ in front))
print('frontier targets', sum(k in TK for k, _ in front))

A_cache = {}
def classify(u, v):
    n, D = u.n, u.D
    M = d2.matrix(u)
    others = [j for j in range(n) if j != v]
    c = [F(int(M[v, j]), D) for j in others]
    y = d2.restrict(M, D, others)
    Y = [[F(int(M[a, b]), D) for b in others] for a in others]
    m = len(others)
    tags = set()
    for sw in (0, 1):
        cc = [1 - t for t in c] if sw else c
        if len(set(cc)) == 1:
            mc = max(Y[a][b] for a in range(m) for b in range(m))
            tags.add('const' + ('=mc/2' if cc[0] == mc / 2 else '=1/2' if cc[0] == F(1, 2) else '_other'))
        for i in range(m):
            diff = [j for j in range(m) if j != i and cc[j] != Y[i][j]]
            if not diff:
                dupv = min(min(2 * Y[i][j], 2 - 2 * Y[i][j]) for j in range(m) if j != i)
                tags.add('copy_i' + ('=0' if cc[i] == 0 else '=dup' if cc[i] == dupv else '=dup/2' if cc[i] == dupv / 2 else '_other'))
            elif len(diff) == 1:
                tags.add('copy_i_1diff')
    # face dimension of c in the fiber
    holes = [(min(v, b), max(v, b)) for b in range(n) if b != v]
    A, _ = core.ineq_matrix(n)
    T = core.tight_set(u)
    cols = [core.pidx(n, i, j) for (i, j) in holes]
    sub = A[np.ix_(T, cols)].astype(float)
    rk = np.linalg.matrix_rank(sub) if len(T) else 0
    tags.add('fiberdim%d' % (len(cols) - rk))
    return tags

t0 = time.time()
cnt = collections.Counter(); ex = collections.defaultdict(list)
for k, vs in front:
    u = point(k)
    tg = set()
    for v in vs:
        tg |= classify(u, v)
    for t in tg:
        cnt[(int(k.split('|')[0]), t)] += 1
        if len(ex[t]) < 3: ex[t].append(k)
    if time.time() - t0 > 200: print('TIMEOUT partial'); break
for kk in sorted(cnt): print(kk, cnt[kk])
json.dump({'front': front, 'ex': ex}, open('phase9/round_04/maker/frontier.json', 'w'))
print('time', time.time() - t0)
