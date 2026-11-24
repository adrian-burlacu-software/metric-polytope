import sympy
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
def fr(t): p, q = sympy.fraction(t); return F(int(p), int(q))
def classify(Y, e):
    m = len(e); e = list(e)
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
def facevs(Y, b, maxd=3):
    m = len(b); cs = cons(Y, m)
    tight = [co for co, r in cs if dot(co, b) == r]
    N = sympy.Matrix(tight).nullspace() if tight else sympy.eye(m).columnspace()
    N = [[fr(t) for t in v] for v in N]
    d = len(N)
    if d == 0: return 0, [tuple(b)]
    if d > maxd: return d, None
    L = [([dot(co, Nk) for Nk in N], r - dot(co, b)) for co, r in cs if dot(co, b) != r]
    L = [(a, r) for a, r in L if any(a)]
    vs = set()
    for comb in itertools.combinations(range(len(L)), d):
        A = sympy.Matrix([L[i][0] for i in comb])
        if A.det() == 0: continue
        lam = [fr(t) for t in A.LUsolve(sympy.Matrix([L[i][1] for i in comb]))]
        if all(dot(a, lam) <= r for a, r in L):
            vs.add(tuple(bi + sum(l * Nk[i] for l, Nk in zip(lam, N)) for i, bi in enumerate(b)))
    return d, sorted(vs)
def convrep(b, vs):
    """all minimal-support convex reps of b by affinely independent vertex subsets; return sorted weight multisets"""
    out = set()
    for k in range(1, len(vs) + 1):
        for S in itertools.combinations(vs, k):
            # solve sum w_s S_s = b, sum w = 1
            A = sympy.Matrix([[s[i] for s in S] for i in range(len(b))] + [[1] * k])
            rhs = sympy.Matrix(list(b) + [1])
            if A.rank() < k: continue
            try: sol = A.gauss_jordan_solve(rhs)[0]
            except ValueError: continue
            w = [fr(t) for t in sol]
            if all(x > 0 for x in w): out.add(','.join(str(x) for x in sorted(w)))
        if out: return '|'.join(sorted(out))
    return '?'
