"""Round 14 sim (from round 7 sim3.py): backward cascade lift/radial (preds from engine.pkl) + column generators.
Background generators = accepted moves (partial-dup q<=6, dup-midshift, dup-thirdshift, radial-lowend), so the gain
is the gain of the candidate on top of them (glue ignored -> lower bound).
usage: sim4.py CAND LIMIT [TAG]   CAND = comma list of
   bl:K1-K2[@t@t..][!]  blend (1-t) P + t Q, P of kind K1 (node i), Q of kind K2 (node j), kinds tw an dp ad
                  (twin, anti, dup, antidup); i == j allowed unless '!'; t list '@'-sep (default 1/3, 2/3)
   cen            centroid of 3 specials (all kinds)
   tws[/T]        twin_i with one entry j at t of [L_j, U_j]
   none           background only"""
import json, sys, pickle, collections, time, itertools
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())
CAND = sys.argv[1].split(','); LIMIT = float(sys.argv[2]); TAG = sys.argv[3] if len(sys.argv) > 3 else 'x'
preds = st['preds']; Rs = set(R); allkeys = list(rep); t0 = time.time(); cache = {}; ncols = []
TDB = [F(1, 4), F(1, 3), F(1, 2), F(2, 3), F(3, 4)]
PDF = sorted({F(p, q) for q in range(2, 7) for p in range(1, q)})
def rng(a, Y, j, m):
    L = max(abs(a[k] - Y[j][k]) for k in range(m) if k != j)
    U = min(min(a[k] + Y[j][k], 2 - a[k] - Y[j][k]) for k in range(m) if k != j)
    return L, U
def specials(Y, m):
    S = {'tw': [], 'an': [], 'dp': [], 'ad': []}
    for i in range(m):
        tw = [F(0) if j == i else Y[i][j] for j in range(m)]
        dl = min(min(2 * Y[i][j], 2 - 2 * Y[i][j]) for j in range(m) if j != i)
        dp = list(tw); dp[i] = dl
        S['tw'].append(tw); S['an'].append([1 - t for t in tw]); S['dp'].append(dp); S['ad'].append([1 - t for t in dp])
    return S
def background(Y, m, out):
    for i in range(m):
        tw = [F(0) if j == i else Y[i][j] for j in range(m)]
        dl = min(min(2 * Y[i][j], 2 - 2 * Y[i][j]) for j in range(m) if j != i)
        for t in PDF:
            b = list(tw); b[i] = t * dl; out.add(tuple(b))
        for t, ss in ((F(1), (F(1, 2), F(1, 3), F(2, 3))), (F(1, 4), (F(1, 3), F(2, 3))), (F(3, 4), (F(1, 3), F(2, 3)))):
            b = list(tw); b[i] = t * dl
            for j in range(m):
                if j == i: continue
                L, U = rng(b, Y, j, m)
                for s in ss:
                    bb = list(b); bb[j] = L + s * (U - L); out.add(tuple(bb))
    Sp = specials(Y, m)
    for i in range(m):
        for j in range(m):
            for Q in (Sp['dp'][j], Sp['ad'][j]):
                for t in TDB: out.add(tuple((1 - t) * p + t * q for p, q in zip(Sp['tw'][i], Q)))
    for S in range(1 << (m - 1)):
        Ss = {a + 1 for a in range(m - 1) if S >> a & 1}
        Z = [[(1 - Y[a][c]) if ((a in Ss) != (c in Ss)) and a != c else Y[a][c] for c in range(m)] for a in range(m)]
        mx = max(Z[a][c] for a in range(m) for c in range(m))
        for j in range(m):
            if not any(Z[j][c] == mx for c in range(m)): continue
            al = max([Z[a][c] for a in range(m) for c in range(m) if a != j and c != j]) / 2
            col = [al] * m; L, U = rng(col, Z, j, m)
            if L > U: continue
            col[j] = L; out.add(tuple((1 - col[a]) if a in Ss else col[a] for a in range(m)))
def cand(Y, m, out):
    Sp = None
    for c in CAND:
        if c == 'none': continue
        if c.startswith('bl:'):
            body = c[3:]; ts = [F(1, 3), F(2, 3)]
            ne = body.endswith('!'); body = body.rstrip('!')
            if '@' in body: body, tt = body.split('@', 1); ts = [F(x) for x in tt.split('@')]
            k1, k2 = body.split('-')
            Sp = Sp or specials(Y, m)
            for i in range(m):
                for j in range(m):
                    if ne and i == j: continue
                    P, Q = Sp[k1][i], Sp[k2][j]
                    for t in ts: out.add(tuple((1 - t) * p + t * q for p, q in zip(P, Q)))
        elif c.startswith('tri:'):
            # tri:K1.K2.K3:PAT@w1/w2/w3@...  K = kinds joined by '+', PAT over {i,j} e.g. iij; weights in all permutations
            _, kk, rest = c.split(':'); pt, *ws = rest.split('@'); ks = kk.split('.')
            W = set()
            for w in ws:
                for pm in itertools.permutations([F(x) for x in w.split(';')]): W.add(pm)
            Sp = Sp or specials(Y, m)
            for i in range(m):
                for j in range(m):
                    if 'j' in pt and i == j: continue
                    idx = [i if ch == 'i' else j for ch in pt]
                    for k1 in ks[0].split('+'):
                      for k2 in ks[1].split('+'):
                        for k3 in ks[2].split('+'):
                          A, B, Cc = Sp[k1][idx[0]], Sp[k2][idx[1]], Sp[k3][idx[2]]
                          for a, b, d in W: out.add(tuple(a * x + b * y + d * z for x, y, z in zip(A, B, Cc)))
                    if 'j' not in pt: break
        elif c == 'cen':
            Sp = Sp or specials(Y, m); allv = [tuple(v) for k in Sp for v in Sp[k]]
            for a, b, d in itertools.combinations(sorted(set(allv)), 3): out.add(tuple((x + y + z) / 3 for x, y, z in zip(a, b, d)))
        elif c.startswith('tws'):
            ts = [F(x) for x in c.split('/')[1:]] or [F(1, 3), F(2, 3)]
            for i in range(m):
                tw = [F(0) if j == i else Y[i][j] for j in range(m)]
                for j in range(m):
                    if j == i: continue
                    L, U = rng(tw, Y, j, m)
                    for s in ts: bb = list(tw); bb[j] = L + s * (U - L); out.add(tuple(bb))
        else: raise SystemExit('bad cand ' + c)
def gen(u, v, withcand):
    n = u.n; M = d2.matrix(u); others = [j for j in range(n) if j != v]; m = len(others)
    Y = [[F(int(M[a, b]), u.D) for b in others] for a in others]
    out = set(); background(Y, m, out)
    if withcand: cand(Y, m, out)
    return out, tuple(F(int(M[v, j]), u.D) for j in others)
def test(k, v):
    if (k, v) not in cache:
        u = point(k); out, c = gen(u, v, True)
        cc = tuple(1 - x for x in c)
        cache[(k, v)] = c in out or cc in out; ncols.append((u.n - 1, len(out)))
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
print(CAND, 'gained', len(gain), sorted(collections.Counter(int(k.split('|')[0]) for k in gain).items()),
      'targets', len(tg), sorted(collections.Counter(int(k.split('|')[0]) for k in tg).items()), 'time', round(time.time() - t0), 'timeout' if time.time() - t0 > LIMIT else '')
for n in (8, 9):
    print(' n', n, 'target D', sorted(collections.Counter(int(k.split('|')[1]) for k in tg if k.startswith(f'{n}|')).items()))
json.dump(sorted(gain), open(f'phase9/round_16/maker/C_work/gain_{TAG}.json', 'w'))
