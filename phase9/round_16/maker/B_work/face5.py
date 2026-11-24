"""Fiber face of the new column for the prime-introducing frontier pairs (fp.json). Face dim, vertices (classified),
and b as a convex combination of affinely independent face vertices (weights)."""
import json, sys, pickle, collections, itertools
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())
exec(open('phase9/round_16/maker/B_work/facelib.py').read())
FP = json.load(open('phase9/round_16/maker/B_work/fp.json'))
ONLY = sys.argv[1] if len(sys.argv) > 1 else 'intro'   # intro: Y has no 5/7
seen = set(); stat = collections.Counter(); ex = collections.defaultdict(list); per = collections.defaultdict(set)
for f in FP:
    if ONLY == 'intro' and int(f['Y'].split('|')[1]) % 5 == 0: continue
    if (f['Y'], f['Z']) in seen: per[seen_key[(f['Y'], f['Z'])]].add(f['tid']); continue
    tg = targets[f['tid']]; n0 = tg.n
    M = d2.matrix(tg); X = [[F(int(M[a, b]), tg.D) for b in range(n0)] for a in range(n0)]
    Ys = [a for a in range(n0) if f['m'] >> a & 1]; v = f['v']
    Y = [[X[a][q] for q in Ys] for a in Ys]; b = tuple(X[v][a] for a in Ys)
    d, vs = facevs(Y, b)
    if vs is None: key = (len(Ys), f['D'], 'dim', d)
    else:
        cl = sorted(classify(Y, list(p)) for p in vs)
        ws = convrep(b, vs)
        key = (len(Ys), f['D'], 'dim', d, 'nv', len(vs), 'w=' + ws)
    stat[key] += 1; seen.add((f['Y'], f['Z']))
    try: seen_key
    except NameError: seen_key = {}
    seen_key[(f['Y'], f['Z'])] = key; per[key].add(f['tid'])
    if len(ex[key]) < 2: ex[key].append((Y, b, vs, [classify(Y, list(p)) for p in (vs or [])]))
for k, v in sorted(stat.items(), key=str): print(k, 'pairs', v, 'targets', len(per[k]))
pickle.dump(dict(ex), open('phase9/round_16/maker/B_work/face5_ex.pkl', 'wb'))
