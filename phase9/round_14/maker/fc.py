"""Group C frontier: for unreached targets whose largest reached restriction has size s, take unreached (s+1)-subsets Z
with a reached s-subset Z-v; face dimension of the new column b in the fiber over x|(Z-v); for dim 1: position t."""
import json, sys, pickle, collections, itertools, time
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())
n0 = int(sys.argv[1])
def rank(rows):
    rows = [list(r) for r in rows]; r = 0
    ncol = len(rows[0]) if rows else 0
    for c in range(ncol):
        p = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if p is None: continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                f = rows[i][c] / rows[r][c]; rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        r += 1
    return r
def tight_rows(Y, b):
    m = len(b); rows = []
    for a in range(m):
        for c in range(a + 1, m):
            y = Y[a][c]; e = [0] * m
            if b[a] - b[c] == y: r = e[:]; r[a] = 1; r[c] = -1; rows.append(r)
            if b[c] - b[a] == y: r = e[:]; r[a] = -1; r[c] = 1; rows.append(r)
            if b[a] + b[c] == y or b[a] + b[c] == 2 - y: r = e[:]; r[a] = 1; r[c] = 1; rows.append(r)
    return rows
stats = collections.Counter(); per_t = collections.Counter(); ex = []
for tid, tg in enumerate(targets):
    if tg.n != n0: continue
    full = (1 << n0) - 1
    if tkeys[tid][full] not in TK: continue
    reached = [m for m in range(1, full) if bin(m).count('1') >= 3 and tkeys[tid][m] in Rs] if False else None
    Rk = [m for m in range(1, full) if bin(m).count('1') >= 3 and tkeys[tid][m] in R]
    s = max((bin(m).count('1') for m in Rk), default=0)
    if s < 3: continue
    M = d2.matrix(tg); D = tg.D; X = [[F(int(M[a, b]), D) for b in range(n0)] for a in range(n0)]
    seen = set(); dims = collections.Counter()
    for m in Rk:
        if bin(m).count('1') != s: continue
        for v in range(n0):
            if m >> v & 1: continue
            Z = m | (1 << v)
            if tkeys[tid][Z] in R: continue
            Ysub = [a for a in range(n0) if m >> a & 1]
            Y = [[X[a][c] for c in Ysub] for a in Ysub]; b = [X[v][a] for a in Ysub]
            rows = tight_rows(Y, b); dim = len(b) - (rank([[F(x) for x in r] for r in rows]) if rows else 0)
            dims[dim] += 1
    stats[(tg.D, s, tuple(sorted(dims.items())))] += 1
for k, c in sorted(stats.items()): print(k, c)

# ---- edge detail for dim-1 cases
def nullvec(rows, m):
    # rows rank m-1: find nullspace vector
    import sympy
    Mx = sympy.Matrix(rows); ns = Mx.nullspace()
    v = ns[0]; return [F(int(sympy.fraction(t)[0]), int(sympy.fraction(t)[1])) for t in v]
def cons(Y, m):
    out = []  # (coef vector, rhs): coef.b <= rhs
    for a in range(m):
        for c in range(a + 1, m):
            y = Y[a][c]; e = [0] * m
            r = e[:]; r[a] = 1; r[c] = -1; out.append((r, y))
            r = e[:]; r[a] = -1; r[c] = 1; out.append((r, y))
            r = e[:]; r[a] = -1; r[c] = -1; out.append((r, -y))
            r = e[:]; r[a] = 1; r[c] = 1; out.append((r, 2 - y))
    return out
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
cnt = collections.Counter(); shown = 0
for tid, tg in enumerate(targets):
    if tg.n != n0: continue
    full = (1 << n0) - 1
    if tkeys[tid][full] not in TK: continue
    Rk = [m for m in range(1, full) if bin(m).count('1') >= 3 and tkeys[tid][m] in R]
    s = max((bin(m).count('1') for m in Rk), default=0)
    if s < 4: continue
    M = d2.matrix(tg); D = tg.D; X = [[F(int(M[a, b]), D) for b in range(n0)] for a in range(n0)]
    for m in Rk:
        if bin(m).count('1') != s: continue
        for v in range(n0):
            if m >> v & 1: continue
            Z = m | (1 << v)
            if tkeys[tid][Z] in R: continue
            Ysub = [a for a in range(n0) if m >> a & 1]
            Y = [[X[a][c] for c in Ysub] for a in Ysub]; b = [X[v][a] for a in Ysub]; mm = len(b)
            rows = tight_rows(Y, b)
            if mm - rank([[F(x) for x in r] for r in rows]) != 1: continue
            dvec = nullvec(rows, mm)
            hi = min((rhs - sum(c * x for c, x in zip(co, b))) / sum(c * x for c, x in zip(co, dvec)) for co, rhs in cons(Y, mm) if sum(c * x for c, x in zip(co, dvec)) > 0)
            lo = max((rhs - sum(c * x for c, x in zip(co, b))) / sum(c * x for c, x in zip(co, dvec)) for co, rhs in cons(Y, mm) if sum(c * x for c, x in zip(co, dvec)) < 0)
            ea = [x + lo * dd for x, dd in zip(b, dvec)]; eb = [x + hi * dd for x, dd in zip(b, dvec)]
            t = (0 - lo) / (hi - lo); ca, cb = classify(Y, ea), classify(Y, eb)
            key = (tg.D, str(min(t, 1 - t)), tuple(sorted([ca.rstrip('0123456789'), cb.rstrip('0123456789')])), tuple(sorted(set(abs(x) for x in dvec))))
            cnt[key] += 1
            if shown < 4 and 'other' in (ca, cb):
                shown += 1
                print('Y', [[str(q) for q in r] for r in Y]); print(' b', [str(q) for q in b], 'ea', [str(q) for q in ea], ca, 'eb', [str(q) for q in eb], cb, 't', t)
for k, c in sorted(cnt.items(), key=str): print(k, c)
