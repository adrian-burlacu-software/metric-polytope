"""Frontier nodes inside unreached targets of chosen D: compare new column c with the closest twin/antitwin column."""
import json, sys, pickle, collections
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import detour_depth2 as d2
st = pickle.load(open('checkpoints/phase9/engine/engine.pkl', 'rb'))
targets, tkeys, rep = st['targets'], st['tkeys'], st['rep']
R = set(json.load(open('checkpoints/phase9/reached.json')))
UT = json.load(open('results/phase9/unreached_targets.json'))
def bits(m): return [v for v in range(m.bit_length()) if m >> v & 1]
def subkey(k, lm):
    tid, mask = rep[k]; T = bits(mask); return tkeys[tid][sum(1 << T[i] for i in bits(lm))]
def point(k):
    tid, mask = rep[k]; return d2.restrict(d2.matrix(targets[tid]), targets[tid].D, bits(mask))
front = dict((k, vs) for k, vs in json.load(open('phase9/round_06/maker/frontier6.json'))['front'])
tid_of = {tkeys[t][(1 << targets[t].n) - 1]: t for t in range(len(tkeys))}
Ds = [int(x) for x in sys.argv[1].split(',')]
nodeD = collections.defaultdict(set)   # frontier node -> set of (n,D) of targets containing it
for t in UT:
    if t['D'] not in Ds: continue
    tid = tid_of[t['key']]
    for m, k in tkeys[tid].items():
        if k in front: nodeD[k].add((t['n'], t['D']))
print('frontier nodes in these targets', len(nodeD), 'targets with >=1 frontier node',
      sum(1 for t in UT if t['D'] in Ds and any(k in front for k in tkeys[tid_of[t['key']]].values())), 'of', sum(1 for t in UT if t['D'] in Ds))
pat = collections.Counter(); ex = {}
for k in nodeD:
    u = point(k); n = u.n; M = d2.matrix(u); D = u.D
    best = None
    for v in front[k]:
        o = [j for j in range(n) if j != v]; m = len(o)
        c = [F(int(M[v, j]), D) for j in o]; Y = [[F(int(M[a, b]), D) for b in o] for a in o]
        for i in range(m):
            for sw in (0, 1):
                tw = [(F(sw) if j == i else (1 - Y[i][j] if sw else Y[i][j])) for j in range(m)]
                diff = [(j == i, c[j] - tw[j]) for j in range(m) if c[j] != tw[j]]
                sig = (len(diff), tuple(sorted((a, str(abs(b))) for a, b in diff)))
                if best is None or sig[0] < best[0]: best = sig
    s = (best[0], 'i' if any(a for a, _ in best[1]) else '-', len(set(b for _, b in best[1])))
    pat[s] += 1; ex.setdefault(s, (k, best))
for s, c in pat.most_common(25): print(s, c, ex[s][1][1][:6])
print('---- signed small-diff examples')
shown = collections.Counter()
for k in nodeD:
    u = point(k); n = u.n; M = d2.matrix(u); D = u.D
    for v in front[k]:
        o = [j for j in range(n) if j != v]; m = len(o)
        c = [F(int(M[v, j]), D) for j in o]; Y = [[F(int(M[a, b]), D) for b in o] for a in o]
        for i in range(m):
            for sw in (0, 1):
                tw = [(F(sw) if j == i else (1 - Y[i][j] if sw else Y[i][j])) for j in range(m)]
                diff = [j for j in range(m) if c[j] != tw[j]]
                if 2 <= len(diff) <= 3 and shown[len(diff)] < 6:
                    shown[len(diff)] += 1
                    print('i', i, 'sw', sw, 'D', D, 'diffs', [(j, str(tw[j]), str(c[j]), 'Y_ij', str(Y[i][j])) for j in diff])
                    print('   twin', [str(t) for t in tw], ' delta_i', str(min(min(2*Y[i][j], 2-2*Y[i][j]) for j in range(m) if j != i)))
                    print('   Y', [[int(y * D) for y in r] for r in Y])
