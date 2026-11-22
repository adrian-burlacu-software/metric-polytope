"""Backward cascade (round_05 sim2.py) with per-(n, D) target breakdown and new cheap column generators.
modes: pd    : partial-dup columns (copy of i, d(v,i) = t*delta_i)            [entry i only]
       pd2   : partial-dup column (t in TS, incl. t=1 dup), then ONE other entry j re-centred at t2 in TS2 within
               its feasible range [L, U]
       pend  : pendant (twin of i shifted by s*1, s = t*smax)
args: modes LIMIT TS [TS2]. Glue ignored -> lower bound. Start set = current reached (includes partial-dup q<=6)."""
import json, sys, pickle, collections, time
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())
modes = sys.argv[1].split(','); LIMIT = float(sys.argv[2]); TS = [F(x) for x in sys.argv[3].split(',')]
TS2 = [F(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else TS
preds = st['preds']; Rs = set(R); allkeys = list(rep); t0 = time.time(); cache = {}; ncols = []
def twins(Y, m):
    for i in range(m):
        yield i, tuple(F(0) if j == i else Y[i][j] for j in range(m))
def rng(a, Y, j, m):
    L = max(abs(a[k] - Y[j][k]) for k in range(m) if k != j)
    U = min(min(a[k] + Y[j][k], 2 - a[k] - Y[j][k]) for k in range(m) if k != j)
    return L, U
def gen(u, v):
    n = u.n; M = d2.matrix(u); others = [j for j in range(n) if j != v]; m = len(others)
    Y = [[F(int(M[a, b]), u.D) for b in others] for a in others]
    # switching class: test c and its antitwin version are handled by testing both c and switched target column
    out = set()
    for i, tw in twins(Y, m):
        dl = min(min(2 * Y[i][j], 2 - 2 * Y[i][j]) for j in range(m) if j != i)
        if 'pd' in modes:
            for t in TS:
                b = list(tw); b[i] = t * dl; out.add(tuple(b))
        if 'pd2' in modes:
            for t in TS + ([F(1)] if F(1) not in TS else []):
                b = list(tw); b[i] = t * dl
                for j in range(m):
                    if j == i: continue
                    L, U = rng(b, Y, j, m)
                    for t2 in TS2:
                        bb = list(b); bb[j] = L + t2 * (U - L); out.add(tuple(bb))
        if 'pd3' in modes:
            b = list(tw); b[i] = dl
            for j in range(m):
                if j == i: continue
                L, U = rng(b, Y, j, m); b1 = list(b); b1[j] = (L + U) / 2
                for k2 in range(m):
                    if k2 in (i, j): continue
                    L2, U2 = rng(b1, Y, k2, m); b2 = list(b1); b2[k2] = (L2 + U2) / 2; out.add(tuple(b2))
        if 'pend' in modes:
            smax = min((2 - tw[j] - tw[k] - Y[j][k]) / 2 for j in range(m) for k in range(m) if j != k)
            for s in TS: out.add(tuple(x + s * smax for x in tw))
    return out, tuple(F(int(M[v, j]), u.D) for j in others)
def test(k, v):
    if (k, v) not in cache:
        u = point(k); out, c = gen(u, v)
        # equivariant moves: the move applied to a switched input gives the switched output, so compare up to
        # switching of the new node v alone (complement column) -- pd/pd2 are switching-equivariant
        cc = tuple(1 - x for x in c)
        cache[(k, v)] = c in out or ('pend' not in modes and cc in out); ncols.append((u.n - 1, len(out)))
    return cache[(k, v)]
rnd = 0
while True:
    rnd += 1; ch = True
    while ch:
        ch = False
        for k in allkeys:
            if k in Rs: continue
            for mv in ('lift', 'radial'):
                if any(p in Rs for p in preds.get((mv, k), ())): Rs.add(k); ch = True; break
    new = set()
    for k in allkeys:
        if k in Rs or time.time() - t0 > LIMIT: continue
        n = int(k.split('|')[0])
        if n < 4: continue
        full = (1 << n) - 1
        for v in range(n):
            if subkey(k, full & ~(1 << v)) in Rs and test(k, v): new.add(k); break
    print('round', rnd, 'adds', len(new), 'reached', len(Rs), 'time', round(time.time() - t0), flush=True)
    if not new or time.time() - t0 > LIMIT: break
    Rs |= new
gain = Rs - set(R); tg = gain & TK
print(modes, [str(t) for t in TS], [str(t) for t in TS2], 'gained', len(gain), sorted(collections.Counter(int(k.split('|')[0]) for k in gain).items()),
      'targets', len(tg), sorted(collections.Counter(int(k.split('|')[0]) for k in tg).items()), 'time', round(time.time() - t0))
for n in (8, 9):
    print(' n', n, 'target D', sorted(collections.Counter(int(k.split('|')[1]) for k in tg if k.startswith(f'{n}|')).items()))
cs = collections.defaultdict(list)
for m, c in ncols: cs[m].append(c)
print('cols per input by input size', {m: (min(v), max(v), round(sum(v) / len(v))) for m, v in sorted(cs.items())})
json.dump(sorted(tg), open(f'phase9/round_06/maker/gain_{"_".join(modes)}_{len(TS)}_{len(TS2)}.json', 'w'))
