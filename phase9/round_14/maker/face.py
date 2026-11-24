"""Group C frontier pairs (reached Y = Z - v, unreached Z), for targets with no missing odd prime: minimal fiber face of
the new column b (dim d <= 2), its vertices (classified), and b as a combination of 2 or 3 face vertices."""
import json, sys, pickle, collections, itertools
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())
import sympy
C = json.load(open('phase9/round_14/maker/groupC.json'))
NS = set(int(a) for a in sys.argv[1].split(','))
def cons(Y, m):
    out = []
    for a in range(m):
        for c in range(a + 1, m):
            y = Y[a][c]; e = [0] * m
            r = e[:]; r[a] = 1; r[c] = -1; out.append((r, y))
            r = e[:]; r[a] = -1; r[c] = 1; out.append((r, y))
            r = e[:]; r[a] = -1; r[c] = -1; out.append((r, -y))
            r = e[:]; r[a] = 1; r[c] = 1; out.append((r, 2 - y))
    return out
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def classify(Y, e):
    m = len(e)
    for i in range(m):
        tw = [F(0) if j == i else Y[i][j] for j in range(m)]
        if e == tw: return f'twin{i}'
        if e == [1 - t for t in tw]: return f'anti{i}'
        dl = min(min(2 * Y[i][j], 2 - 2 * Y[i][j]) for j in range(m) if j != i)
        dp = list(tw); dp[i] = dl
        if e == dp: return f'dup{i}'
        if e == [1 - t for t in dp]: return f'antidup{i}'
    if all(t == e[0] for t in e): return 'const'
    return 'other'
def facevs(Y, b):
    m = len(b); cs = cons(Y, m)
    tight = [co for co, r in cs if dot(co, b) == r]
    if tight:
        N = sympy.Matrix(tight).nullspace()
    else:
        N = sympy.eye(m).columnspace()
    N = [[F(int(sympy.fraction(t)[0]), int(sympy.fraction(t)[1])) for t in v] for v in N]
    d = len(N)
    if d == 0: return 0, [b]
    if d > 2: return d, None
    # constraints in lambda: co.(b + sum l_k N_k) <= r
    L = [([dot(co, Nk) for Nk in N], r - dot(co, b)) for co, r in cs if dot(co, b) != r]
    L = [(a, r) for a, r in L if any(a)]
    vs = set()
    for comb in itertools.combinations(range(len(L)), d):
        A = sympy.Matrix([L[i][0] for i in comb]); rhs = sympy.Matrix([L[i][1] for i in comb])
        if A.det() == 0: continue
        lam = A.LUsolve(rhs); lam = [F(int(sympy.fraction(t)[0]), int(sympy.fraction(t)[1])) for t in lam]
        if all(dot(a, lam) <= r for a, r in L):
            vs.add(tuple(bi + sum(l * Nk[i] for l, Nk in zip(lam, N)) for i, bi in enumerate(b)))
    return d, sorted(vs)
def comb2(b, vs):
    out = []
    for p, q in itertools.combinations(vs, 2):
        # b = p + t (q - p)
        dif = [qi - pi for pi, qi in zip(p, q)]; idx = [i for i, x in enumerate(dif) if x != 0]
        t = (b[idx[0]] - p[idx[0]]) / dif[idx[0]]
        if 0 < t < 1 and all(p[i] + t * dif[i] == b[i] for i in range(len(b))): out.append((p, q, t))
    return out
stat = collections.Counter(); ex = collections.defaultdict(list)
for c in C:
    if c['n'] not in NS or c['miss']: continue
    tid = c['tid']; tg = targets[tid]; n0 = tg.n; full = (1 << n0) - 1; s = c['s']
    M = d2.matrix(tg); X = [[F(int(M[a, b]), tg.D) for b in range(n0)] for a in range(n0)]
    seen = set()
    for m in range(1, full):
        if bin(m).count('1') != s or tkeys[tid][m] not in R: continue
        for v in range(n0):
            if m >> v & 1: continue
            Zk = tkeys[tid][m | (1 << v)]
            if Zk in R or (tkeys[tid][m], Zk) in seen: continue
            seen.add((tkeys[tid][m], Zk))
            Ys = [a for a in range(n0) if m >> a & 1]
            Y = [[X[a][q] for q in Ys] for a in Ys]; b = tuple(X[v][a] for a in Ys)
            d, vs = facevs(Y, b)
            if vs is None: stat[(c['n'], tg.D, s, 'dim', d)] += 1; continue
            if d == 1:
                p, q = vs; t = comb2(b, vs)[0][2]
                key = (c['n'], tg.D, s, 'edge', str(min(t, 1 - t)), tuple(sorted([classify(Y, list(p)).rstrip('0123456789'), classify(Y, list(q)).rstrip('0123456789')])))
            else:
                cs2 = comb2(b, vs)
                ts = sorted(set(str(min(t, 1 - t)) for _, _, t in cs2))
                # centroid test
                cen = any(all(3 * b[i] == p[i] + q[i] + r[i] for i in range(len(b))) for p, q, r in itertools.combinations(vs, 3))
                key = (c['n'], tg.D, s, 'face2', len(vs), 'diag_t=' + ','.join(ts), 'centroid' if cen else '')
            stat[key] += 1
            if len(ex[key]) < 2: ex[key].append((Y, b, vs))
for k, v in sorted(stat.items(), key=str): print(k, v)
import pickle as pk; pk.dump(dict(ex), open('phase9/round_14/maker/face_ex_%s.pkl' % sys.argv[1].replace(',', '_'), 'wb'))
